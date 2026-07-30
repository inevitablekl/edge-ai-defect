#include "edge_ai_defect/runtime/video_file_source.hpp"

#include <opencv2/videoio.hpp>

#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>
#include <utility>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status decode_failure(const std::filesystem::path& video_path,
                      std::size_t sequence_index,
                      const std::string& detail) {
    return Status::failure(
        ErrorCode::kImageProcessingError,
        "decode video '" + video_path.generic_string() + "' at frame " +
            std::to_string(sequence_index) + ": " + detail);
}

std::filesystem::path frame_path(const std::filesystem::path& video_path,
                                 std::size_t sequence_index) {
    std::ostringstream name;
    name << "frame_" << std::setfill('0') << std::setw(6) << sequence_index;
    return std::filesystem::path(video_path.filename().generic_u8string()) /
           name.str();
}

bool finite_positive(double value) {
    return std::isfinite(value) && value > 0.0;
}

}  // namespace

VideoFileSource::VideoFileSource(std::filesystem::path video_path,
                                 std::optional<std::size_t> max_frames)
    : video_path_(std::move(video_path)), max_frames_(max_frames) {}

core::Status VideoFileSource::create(
    const std::filesystem::path& video_path,
    std::unique_ptr<VideoFileSource>* output,
    std::optional<std::size_t> max_frames) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "VideoFileSource create output must not be null");
    }
    if (video_path.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "VideoFileSource video path must not be empty");
    }
    if (max_frames.has_value() && *max_frames == 0) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "VideoFileSource max_frames must be positive");
    }

    std::unique_ptr<VideoFileSource> candidate(
        new VideoFileSource(video_path, max_frames));
    try {
        if (!candidate->capture_.open(video_path.string(), cv::CAP_ANY) ||
            !candidate->capture_.isOpened()) {
            return Status::failure(
                ErrorCode::kIoError,
                "open video file failed: '" + video_path.generic_string() + "'");
        }
    } catch (const cv::Exception& exception) {
        return Status::failure(
            ErrorCode::kIoError,
            "open video file '" + video_path.generic_string() + "': " +
                exception.what());
    }

    const double width = candidate->capture_.get(cv::CAP_PROP_FRAME_WIDTH);
    const double height = candidate->capture_.get(cv::CAP_PROP_FRAME_HEIGHT);
    if (!finite_positive(width) || !finite_positive(height) ||
        width > static_cast<double>(std::numeric_limits<int>::max()) ||
        height > static_cast<double>(std::numeric_limits<int>::max())) {
        return Status::failure(
            ErrorCode::kImageProcessingError,
            "video metadata has invalid resolution for '" +
                video_path.generic_string() + "'");
    }
    candidate->metadata_.width = static_cast<int>(std::lround(width));
    candidate->metadata_.height = static_cast<int>(std::lround(height));
    candidate->metadata_.nominal_fps = candidate->capture_.get(cv::CAP_PROP_FPS);

    const double reported_count =
        candidate->capture_.get(cv::CAP_PROP_FRAME_COUNT);
    if (std::isfinite(reported_count) && reported_count > 0.0 &&
        reported_count <= static_cast<double>(std::numeric_limits<std::size_t>::max())) {
        candidate->expected_frame_count_ =
            static_cast<std::size_t>(std::llround(reported_count));
        candidate->has_expected_frame_count_ =
            candidate->expected_frame_count_ > 0;
    }

    *output = std::move(candidate);
    return Status::success();
}

core::Status VideoFileSource::next(std::optional<ImageItem>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "VideoFileSource next output must not be null");
    }
    if (eof_ || (max_frames_.has_value() &&
                 metadata_.decoded_frame_count >= *max_frames_)) {
        *output = std::nullopt;
        return Status::success();
    }

    const std::size_t sequence_index = metadata_.decoded_frame_count;
    cv::Mat image_bgr;
    bool read_succeeded = false;
    try {
        read_succeeded = capture_.read(image_bgr);
    } catch (const cv::Exception& exception) {
        return decode_failure(video_path_, sequence_index, exception.what());
    }

    if (!read_succeeded || image_bgr.empty()) {
        if (has_expected_frame_count_ &&
            metadata_.decoded_frame_count < expected_frame_count_) {
            return decode_failure(
                video_path_, sequence_index,
                "VideoCapture ended before CAP_PROP_FRAME_COUNT was decoded");
        }
        eof_ = true;
        *output = std::nullopt;
        return Status::success();
    }
    if (image_bgr.type() != CV_8UC3) {
        return decode_failure(video_path_, sequence_index,
                              "decoded frame is not CV_8UC3");
    }
    if (image_bgr.cols != metadata_.width || image_bgr.rows != metadata_.height) {
        return decode_failure(video_path_, sequence_index,
                              "decoded frame dimensions differ from video metadata");
    }

    ImageItem item;
    item.sequence_index = sequence_index;
    item.relative_path = frame_path(video_path_, sequence_index);
    item.image_bgr = std::move(image_bgr);
    *output = std::move(item);
    ++metadata_.decoded_frame_count;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
