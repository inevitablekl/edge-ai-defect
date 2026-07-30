#include "edge_ai_defect/runtime/pipeline_runner.hpp"

#include <opencv2/core.hpp>

#include <atomic>
#include <chrono>
#include <filesystem>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <thread>
#include <vector>

namespace {
namespace core = edge_ai_defect::core;
namespace inference = edge_ai_defect::inference;
namespace model = edge_ai_defect::model;
namespace postprocess = edge_ai_defect::postprocess;
namespace preprocess = edge_ai_defect::preprocess;
namespace runtime = edge_ai_defect::runtime;

void require(bool value, const char* message) {
    if (!value) throw std::runtime_error(message);
}

core::TensorInfo input_info() {
    return {core::TensorDataType::kFloat32, core::TensorLayout::kNchw, {1, 3, 640, 640}};
}

core::HostTensor output_tensor(bool valid = true) {
    if (!valid) return {{core::TensorDataType::kFloat32, core::TensorLayout::kNchw, {1, 2}}, {1.0F}};
    core::HostTensor output{{core::TensorDataType::kFloat32, core::TensorLayout::kBcn, {1, 10, 8400}},
                            std::vector<float>(10U * 8400U, 0.0F)};
    output.data[0 * 8400 + 2] = 100.0F; output.data[1 * 8400 + 2] = 100.0F;
    output.data[2 * 8400 + 2] = 20.0F; output.data[3 * 8400 + 2] = 20.0F;
    output.data[4 * 8400 + 2] = 0.9F;
    return output;
}

runtime::RunMetadata metadata(bool timing = true) {
    runtime::RunMetadata value;
    value.schema_version = 3;
    value.backend_type = "test";
    value.timing_enabled = timing;
    value.runtime_v3 = runtime::RuntimeMetadataV3{"pipeline", "directory",
        runtime::PipelineMetadataV3{2, "block"}};
    return value;
}

class Source final : public runtime::ImageSource {
public:
    explicit Source(std::size_t count, bool fail = false) : count_(count), fail_(fail) {}
    core::Status next(std::optional<runtime::ImageItem>* output) override {
        if (fail_ && cursor_ == 1) return core::Status::failure(core::ErrorCode::kIoError, "source failure");
        if (cursor_ == count_) { *output = std::nullopt; return core::Status::success(); }
        runtime::ImageItem item;
        item.sequence_index = cursor_;
        item.relative_path = "frame_" + std::to_string(cursor_) + ".png";
        item.image_bgr = cv::Mat(8, 6, CV_8UC3, cv::Scalar(3, 5, 7)).clone();
        *output = std::move(item); ++cursor_; return core::Status::success();
    }
private:
    std::size_t count_;
    bool fail_;
    std::size_t cursor_ = 0;
};

class Engine final : public inference::IInferenceEngine {
public:
    explicit Engine(bool fail = false, bool invalid_output = false, int delay_ms = 0)
        : fail_(fail), invalid_output_(invalid_output), delay_ms_(delay_ms) {}
    core::Status initialize(const model::ModelContract&, const std::filesystem::path&) override {
        return core::Status::success();
    }
    core::Status run(const core::HostTensor&, core::HostTensor* output) override {
        const int active_now = ++active;
        int observed = maximum.load();
        while (active_now > observed && !maximum.compare_exchange_weak(observed, active_now)) {}
        if (delay_ms_ != 0) std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms_));
        --active;
        if (fail_) return core::Status::failure(core::ErrorCode::kBackendRuntimeError, "engine failure");
        *output = output_tensor(!invalid_output_); return core::Status::success();
    }
    std::atomic<int> active{0};
    std::atomic<int> maximum{0};
private:
    bool fail_; bool invalid_output_; int delay_ms_;
};

class Sink final : public runtime::IResultSink {
public:
    explicit Sink(bool fail_write = false, bool fail_begin = false, bool fail_end = false)
        : fail_write_(fail_write), fail_begin_(fail_begin), fail_end_(fail_end) {}
    core::Status begin_run(const runtime::RunMetadata&) override {
        ++begin_calls; if (fail_begin_) return failure("begin"); return core::Status::success();
    }
    core::Status write_frame(const runtime::FrameResult&) override {
        ++write_calls; if (fail_write_) return failure("write"); return core::Status::success();
    }
    core::Status end_run(const runtime::RunSummary&) override {
        ++end_calls; if (fail_end_) return failure("end"); return core::Status::success();
    }
    int begin_calls = 0; int write_calls = 0; int end_calls = 0;
private:
    static core::Status failure(const char* detail) {
        return core::Status::failure(core::ErrorCode::kIoError, detail);
    }
    bool fail_write_; bool fail_begin_; bool fail_end_;
};

runtime::RunSummary run(Source& source, Engine& engine, Sink& sink, runtime::RunMetadata meta = metadata()) {
    preprocess::Preprocessor preprocessor;
    postprocess::PostProcessor postprocessor;
    runtime::PipelineRunner runner(source, preprocessor, input_info(), engine, postprocessor, sink, 2);
    runtime::RunSummary summary;
    require(runner.run(meta, &summary).ok(), "pipeline run failed");
    return summary;
}

void success_and_lifecycle() {
    Source source(12); Engine engine(false, false, 1); Sink sink;
    const auto summary = run(source, engine, sink);
    require(summary.processed_images == 12 && summary.runtime_v3.has_value(), "summary mismatch");
    require(summary.runtime_v3->source_frames == 12, "source frame count");
    require(engine.maximum == 1, "engine concurrency exceeded one");
    require(sink.begin_calls == 1 && sink.write_calls == 12 && sink.end_calls == 1, "sink lifecycle");
}

void failures_do_not_end_run() {
    { Source source(0); Engine engine; Sink sink; preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "empty source"); }
    { Source source(2, true); Engine engine; Sink sink; preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "source failure"); }
    { Source source(1); Engine engine(true); Sink sink; preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "inference failure"); }
    { Source source(1); Engine engine(false, true); Sink sink; preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "postprocess failure"); }
    { Source source(1); Engine engine; Sink sink(true); preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "sink write failure"); }
    { Source source(1); Engine engine; Sink sink(false, true); preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 0, "begin failure"); }
    { Source source(1); Engine engine; Sink sink(false, false, true); preprocess::Preprocessor p; postprocess::PostProcessor pp; runtime::PipelineRunner r(source,p,input_info(),engine,pp,sink,2); runtime::RunSummary s; require(!r.run(metadata(), &s).ok() && sink.end_calls == 1, "end failure"); }
}

}  // namespace

int main() {
    try { success_and_lifecycle(); failures_do_not_end_run(); std::cout << "PipelineRunner tests passed\n"; return 0; }
    catch (const std::exception& error) { std::cerr << "PipelineRunner test failed: " << error.what() << '\n'; return 1; }
}
