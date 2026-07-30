#include "edge_ai_defect/runtime/corpus_replay_source.hpp"

#include <opencv2/imgcodecs.hpp>
#include <yaml-cpp/yaml.h>

#include <system_error>

namespace edge_ai_defect::runtime {
namespace {
using core::ErrorCode;
using core::Status;
}

CorpusReplaySource::CorpusReplaySource(std::filesystem::path root,
                                       std::vector<Entry> entries,
                                       std::size_t cycles)
    : root_(std::move(root)), entries_(std::move(entries)), cycles_(cycles) {}

core::Status CorpusReplaySource::create(const std::filesystem::path& image_root,
                                        const std::filesystem::path& manifest_path,
                                        std::size_t cycles,
                                        std::unique_ptr<CorpusReplaySource>* output) {
    if (output == nullptr || image_root.empty() || manifest_path.empty() || cycles == 0) {
        return Status::failure(ErrorCode::kInvalidArgument, "CorpusReplaySource arguments are invalid");
    }
    try {
        const YAML::Node manifest = YAML::LoadFile(manifest_path.string());
        const YAML::Node entries_node = manifest["entries"];
        if (!entries_node || !entries_node.IsSequence() || entries_node.size() != 180U) {
            return Status::failure(ErrorCode::kSchemaViolation, "CorpusReplaySource requires exactly 180 manifest entries");
        }
        std::vector<Entry> entries;
        entries.reserve(entries_node.size());
        for (std::size_t index = 0; index < entries_node.size(); ++index) {
            const YAML::Node filename = entries_node[index]["prepared_filename"];
            if (!filename || !filename.IsScalar()) {
                return Status::failure(ErrorCode::kSchemaViolation, "CorpusReplaySource entry lacks prepared_filename");
            }
            entries.push_back({filename.as<std::string>()});
        }
        std::error_code error;
        if (!std::filesystem::is_directory(image_root, error) || error) {
            return Status::failure(ErrorCode::kIoError, "CorpusReplaySource image root is not a directory");
        }
        std::unique_ptr<CorpusReplaySource> candidate(new CorpusReplaySource(
            std::filesystem::absolute(image_root), std::move(entries), cycles));
        *output = std::move(candidate);
        return Status::success();
    } catch (const YAML::Exception& exception) {
        return Status::failure(ErrorCode::kParseError, std::string("CorpusReplaySource manifest: ") + exception.what());
    }
}

core::Status CorpusReplaySource::next(std::optional<ImageItem>* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "CorpusReplaySource output is null");
    if (cursor_ == entries_.size() * cycles_) { *output = std::nullopt; return Status::success(); }
    const std::size_t frame = cursor_ % entries_.size();
    const std::size_t cycle = cursor_ / entries_.size();
    const std::filesystem::path relative = entries_[frame].filename;
    cv::Mat image;
    try { image = cv::imread((root_ / relative).string(), cv::IMREAD_COLOR); }
    catch (const cv::Exception& exception) {
        return Status::failure(ErrorCode::kImageProcessingError, exception.what());
    }
    if (image.empty() || image.type() != CV_8UC3) {
        return Status::failure(ErrorCode::kImageProcessingError, "CorpusReplaySource decode failed: " + relative.generic_string());
    }
    ImageItem item;
    item.sequence_index = cursor_;
    item.relative_path = relative;
    item.image_bgr = std::move(image);
    *output = std::move(item);
    last_cycle_id_ = cycle;
    last_frame_index_ = frame;
    ++cursor_;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
