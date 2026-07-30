#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/timed_json_sink.hpp"

#include <opencv2/imgcodecs.hpp>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
namespace runtime = edge_ai_defect::runtime;

void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }

void write_manifest(const fs::path& path, const std::vector<std::string>& image_paths) {
    std::ofstream output(path);
    require(static_cast<bool>(output), "manifest open");
    output << "{\"entries\":[";
    for (std::size_t i = 0; i < image_paths.size(); ++i) {
        if (i != 0) output << ',';
        output << "{\"image_path\":\"" << image_paths[i] << "\"}";
    }
    output << "]}";
    require(static_cast<bool>(output), "manifest write");
}

class Sink final : public runtime::IResultSink {
public:
    edge_ai_defect::core::Status begin_run(const runtime::RunMetadata&) override { return edge_ai_defect::core::Status::success(); }
    edge_ai_defect::core::Status write_frame(const runtime::FrameResult&) override { return edge_ai_defect::core::Status::success(); }
    edge_ai_defect::core::Status end_run(const runtime::RunSummary&) override { return edge_ai_defect::core::Status::success(); }
};

void components() {
    const fs::path root = fs::temp_directory_path() / "stage_p_components_test";
    fs::create_directories(root / "IMAGES");
    cv::imwrite((root / "IMAGES/frame_a.jpg").string(), cv::Mat(4, 4, CV_8UC3, cv::Scalar(1, 2, 3)));
    cv::imwrite((root / "IMAGES/frame_b.jpg").string(), cv::Mat(4, 4, CV_8UC3, cv::Scalar(4, 5, 6)));
    cv::imwrite((root / "IMAGES/frame_c.jpg").string(), cv::Mat(4, 4, CV_8UC3, cv::Scalar(7, 8, 9)));

    std::vector<std::string> image_paths;
    image_paths.reserve(180);
    for (std::size_t i = 0; i < 180; ++i) {
        image_paths.push_back("IMAGES/frame_" + std::string(1, static_cast<char>('a' + (i % 3))) + ".jpg");
    }
    const fs::path manifest = root / "manifest.json";
    write_manifest(manifest, image_paths);

    std::unique_ptr<runtime::CorpusReplaySource> source;
    require(runtime::CorpusReplaySource::create(root, manifest, 2, &source).ok(), "replay create");
    std::optional<runtime::ImageItem> item;
    require(source->frame_count() == 180, "replay frame count");
    std::vector<std::string> observed_paths;
    std::vector<int> observed_pixels;
    observed_paths.reserve(360);
    observed_pixels.reserve(360);
    for (std::size_t i = 0; i < 360; ++i) {
        require(source->next(&item).ok() && item->sequence_index == i, "replay sequence");
        require(source->cycle_id() == i / 180 && source->frame_index() == i % 180, "replay position");
        require(item->relative_path.generic_string() == image_paths[i % 180], "replay relative path");
        observed_paths.push_back(item->relative_path.generic_string());
        observed_pixels.push_back(static_cast<int>(item->image_bgr.at<cv::Vec3b>(0, 0)[0]));
    }
    require(source->next(&item).ok() && !item.has_value(), "replay EOS");

    std::unique_ptr<runtime::CorpusReplaySource> smoke_source;
    require(runtime::CorpusReplaySource::create(root, manifest, 1, &smoke_source).ok(),
            "replay repeat create");
    for (std::size_t i = 0; i < 180; ++i) {
        require(smoke_source->next(&item).ok() && item->sequence_index == i,
                "replay repeat sequence");
        require(item->relative_path.generic_string() == observed_paths[i],
                "replay deterministic relative path");
        require(static_cast<int>(item->image_bgr.at<cv::Vec3b>(0, 0)[0]) == observed_pixels[i],
                "replay deterministic image");
    }
    require(smoke_source->next(&item).ok() && !item.has_value(), "replay repeat EOS");

    const fs::path missing_manifest = root / "missing_image_path.json";
    std::vector<std::string> missing_entries(180, "IMAGES/frame_a.jpg");
    write_manifest(missing_manifest, missing_entries);
    {
        std::ofstream output(missing_manifest);
        require(static_cast<bool>(output), "missing manifest open");
        output << "{\"entries\":[{}";
        for (std::size_t i = 1; i < 180; ++i) {
            output << ",{\"image_path\":\"IMAGES/frame_a.jpg\"}";
        }
        output << "]}";
    }
    std::unique_ptr<runtime::CorpusReplaySource> missing_source;
    require(!runtime::CorpusReplaySource::create(root, missing_manifest, 1, &missing_source).ok(),
            "missing image_path must fail");

    const fs::path absolute_manifest = root / "absolute_image_path.json";
    std::vector<std::string> absolute_entries(180, "IMAGES/frame_a.jpg");
    write_manifest(absolute_manifest, absolute_entries);
    {
        std::ofstream output(absolute_manifest);
        require(static_cast<bool>(output), "absolute manifest open");
        output << "{\"entries\":[{\"image_path\":\"/tmp/frame_a.jpg\"}";
        for (std::size_t i = 1; i < 180; ++i) {
            output << ",{\"image_path\":\"IMAGES/frame_a.jpg\"}";
        }
        output << "]}";
    }
    std::unique_ptr<runtime::CorpusReplaySource> absolute_source;
    require(!runtime::CorpusReplaySource::create(root, absolute_manifest, 1, &absolute_source).ok(),
            "absolute image_path must fail");

    runtime::CanonicalHashSink hash;
    runtime::RunMetadata metadata;
    runtime::RunSummary summary;
    require(hash.begin_run(metadata).ok(), "hash begin");
    runtime::FrameResult frame;
    frame.relative_path = "frame.jpg"; frame.image_width = 4; frame.image_height = 4;
    require(hash.write_frame(frame).ok() && hash.write_frame(frame).ok(), "hash write");
    require(hash.end_run(summary).ok() && !hash.run_hash().empty() && hash.cycle_hashes().size() == 1, "hash output");

    Sink inner;
    runtime::TimedJsonSink timed(inner);
    require(timed.begin_run(metadata).ok() && timed.end_run(summary).ok(), "timed sink");
    require(timed.end_run_duration_ns() >= 0, "timing output");
    std::error_code error; fs::remove_all(root, error);
}
}

int main() {
    try { components(); std::cout << "Stage P component tests passed\n"; return 0; }
    catch (const std::exception& error) { std::cerr << "Stage P component test failed: " << error.what() << '\n'; return 1; }
}
