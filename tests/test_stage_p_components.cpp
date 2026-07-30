#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/timed_json_sink.hpp"

#include <opencv2/imgcodecs.hpp>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
namespace fs = std::filesystem;
namespace runtime = edge_ai_defect::runtime;

void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }

class Sink final : public runtime::IResultSink {
public:
    edge_ai_defect::core::Status begin_run(const runtime::RunMetadata&) override { return edge_ai_defect::core::Status::success(); }
    edge_ai_defect::core::Status write_frame(const runtime::FrameResult&) override { return edge_ai_defect::core::Status::success(); }
    edge_ai_defect::core::Status end_run(const runtime::RunSummary&) override { return edge_ai_defect::core::Status::success(); }
};

void components() {
    const fs::path root = fs::temp_directory_path() / "stage_p_components_test";
    fs::create_directories(root);
    cv::imwrite((root / "frame.jpg").string(), cv::Mat(4, 4, CV_8UC3, cv::Scalar(1, 2, 3)));
    const fs::path manifest = root / "manifest.json";
    std::ofstream output(manifest);
    output << "{\"entries\":[";
    for (int i = 0; i < 180; ++i) output << (i == 0 ? "" : ",") << "{\"prepared_filename\":\"frame.jpg\"}";
    output << "]}";
    output.close();

    std::unique_ptr<runtime::CorpusReplaySource> source;
    require(runtime::CorpusReplaySource::create(root, manifest, 2, &source).ok(), "replay create");
    std::optional<runtime::ImageItem> item;
    for (std::size_t i = 0; i < 360; ++i) {
        require(source->next(&item).ok() && item->sequence_index == i, "replay sequence");
        require(source->cycle_id() == i / 180 && source->frame_index() == i % 180, "replay position");
    }
    require(source->next(&item).ok() && !item.has_value(), "replay EOS");

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
