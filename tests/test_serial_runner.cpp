#include "edge_ai_defect/runtime/serial_runner.hpp"

#include <opencv2/core.hpp>

#include <cmath>
#include <filesystem>
#include <iostream>
#include <limits>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace inference = edge_ai_defect::inference;
namespace model = edge_ai_defect::model;
namespace postprocess = edge_ai_defect::postprocess;
namespace preprocess = edge_ai_defect::preprocess;
namespace runtime = edge_ai_defect::runtime;

class TestContext {
public:
    void expect(bool condition, const std::string& name, const std::string& detail) {
        if (!condition) {
            ++failures_;
            std::cerr << "FAILED: " << name << ": " << detail << '\n';
        }
    }
    [[nodiscard]] int failures() const noexcept { return failures_; }
private:
    int failures_ = 0;
};

core::TensorInfo valid_input_info() {
    return {core::TensorDataType::kFloat32, core::TensorLayout::kNchw,
            {1, 3, 640, 640}};
}

runtime::ImageItem image(std::size_t index, const std::string& path, int width = 8,
                         int height = 6) {
    runtime::ImageItem item;
    item.sequence_index = index;
    item.relative_path = path;
    item.image_bgr = cv::Mat(height, width, CV_8UC3, cv::Scalar(3, 5, 7)).clone();
    return item;
}

runtime::RunMetadata metadata(bool timing_enabled = false) {
    runtime::RunMetadata value;
    value.schema_version = 1;
    value.backend_type = "onnxruntime_cpu";
    value.model_filename = "frozen.onnx";
    value.model_sha256 = std::string(64, 'a');
    value.contract_filename = "frozen.yaml";
    value.class_names = {"c0", "c1", "c2", "c3", "c4", "c5"};
    value.timing_enabled = timing_enabled;
    return value;
}

core::HostTensor raw_output(bool valid = true) {
    if (!valid) {
        return {{core::TensorDataType::kFloat32, core::TensorLayout::kNchw, {1, 2, 2}},
                {1.0F, 2.0F, 3.0F, 4.0F}};
    }
    core::HostTensor output{
        {core::TensorDataType::kFloat32, core::TensorLayout::kBcn, {1, 10, 8400}},
        std::vector<float>(10U * 8400U, 0.0F)};
    const auto set = [&output](std::size_t channel, std::size_t candidate, float value) {
        output.data[channel * 8400U + candidate] = value;
    };
    set(0, 2, 100.0F); set(1, 2, 100.0F); set(2, 2, 20.0F); set(3, 2, 20.0F); set(4, 2, 0.9F);
    set(0, 5, 200.0F); set(1, 5, 200.0F); set(2, 5, 30.0F); set(3, 5, 30.0F); set(5, 5, 0.8F);
    return output;
}

class FakeSource final : public runtime::ImageSource {
public:
    struct Step {
        core::Status status = core::Status::success();
        std::optional<runtime::ImageItem> item;
    };
    explicit FakeSource(std::vector<Step> steps) : steps_(std::move(steps)) {}
    core::Status next(std::optional<runtime::ImageItem>* output) override {
        ++calls;
        if (output == nullptr) return core::Status::failure(core::ErrorCode::kInvalidArgument, "null output");
        if (cursor_ == steps_.size()) { *output = std::nullopt; return core::Status::success(); }
        const Step& step = steps_[cursor_++];
        if (!step.status.ok()) return step.status;
        *output = step.item;
        return core::Status::success();
    }
    int calls = 0;
private:
    std::vector<Step> steps_;
    std::size_t cursor_ = 0;
};

FakeSource::Step success_step(runtime::ImageItem item) {
    return {core::Status::success(), std::move(item)};
}

class FakeEngine final : public inference::IInferenceEngine {
public:
    core::Status initialize(const model::ModelContract&, const std::filesystem::path&) override {
        return core::Status::success();
    }
    core::Status run(const core::HostTensor& input, core::HostTensor* output) override {
        ++calls;
        received_inputs.push_back(input.info);
        if (!status.ok()) return status;
        *output = output_tensor;
        return core::Status::success();
    }
    core::Status status = core::Status::success();
    core::HostTensor output_tensor = raw_output();
    int calls = 0;
    std::vector<core::TensorInfo> received_inputs;
};

class RecordingSink final : public runtime::IResultSink {
public:
    core::Status begin_run(const runtime::RunMetadata&) override {
        calls.push_back("begin"); ++begin_calls; return begin_status;
    }
    core::Status write_frame(const runtime::FrameResult& frame) override {
        calls.push_back("write"); ++write_calls;
        if (!write_status.ok()) return write_status;
        frames.push_back(frame); return core::Status::success();
    }
    core::Status end_run(const runtime::RunSummary& value) override {
        calls.push_back("end"); ++end_calls; received_summary = value; return end_status;
    }
    core::Status begin_status = core::Status::success();
    core::Status write_status = core::Status::success();
    core::Status end_status = core::Status::success();
    int begin_calls = 0;
    int write_calls = 0;
    int end_calls = 0;
    std::vector<std::string> calls;
    std::vector<runtime::FrameResult> frames;
    runtime::RunSummary received_summary;
};

bool tensor_info_equal(const core::TensorInfo& left, const core::TensorInfo& right) {
    return left.dtype == right.dtype && left.layout == right.layout && left.shape == right.shape;
}

runtime::RunSummary sentinel_summary() { return {99, 77}; }
bool summary_equal(const runtime::RunSummary& left, const runtime::RunSummary& right) {
    return left.processed_images == right.processed_images && left.total_detections == right.total_detections;
}

void expect_failure_context(TestContext& context, const std::string& name,
                            const core::Status& status, const std::string& stage,
                            bool expect_item_context = false,
                            bool expect_injected_detail = true) {
    context.expect(!status.ok(), name, "run must fail");
    context.expect(status.message().find(stage) != std::string::npos, name, "stage context missing");
    if (expect_injected_detail) {
        context.expect(status.message().find("injected") != std::string::npos,
                       name, "bottom-level message missing");
    }
    if (expect_item_context) {
        context.expect(status.message().find("sequence_index=0") != std::string::npos &&
                           status.message().find("relative_path=frame.jpg") != std::string::npos,
                       name, "ImageItem context missing");
    }
}

void test_success_and_timing(TestContext& context) {
    FakeSource source({success_step(image(0, "frame.jpg", 8, 6)), success_step(image(1, "next.png", 5, 4))});
    preprocess::Preprocessor preprocessor;
    core::TensorInfo input_info = valid_input_info();
    FakeEngine engine;
    postprocess::PostProcessor postprocessor;
    RecordingSink sink;
    runtime::SerialRunner runner(source, preprocessor, input_info, engine, postprocessor, sink);
    input_info.layout = core::TensorLayout::kBcn;
    runtime::RunSummary summary = sentinel_summary();
    const core::Status status = runner.run(metadata(true), &summary);
    context.expect(status.ok(), "multi-frame success", status.message());
    context.expect(summary_equal(summary, {2, 4}), "success summary", "wrong counts");
    context.expect(sink.received_summary.processed_images == 2 && sink.received_summary.total_detections == 4,
                   "staged summary", "sink received wrong counts");
    context.expect(sink.calls == std::vector<std::string>{"begin", "write", "write", "end"},
                   "stage order", "sink ordering wrong");
    context.expect(source.calls == 3 && engine.calls == 2 && sink.frames.size() == 2,
                   "multi-frame calls", "unexpected call count");
    context.expect(engine.received_inputs.size() == 2 &&
                       tensor_info_equal(engine.received_inputs[0], valid_input_info()),
                   "injected TensorInfo value copy",
                   "Preprocessor did not receive the construction-time contract");
    if (sink.frames.size() == 2) {
        context.expect(sink.frames[0].sequence_index == 0 && sink.frames[0].relative_path == "frame.jpg" &&
                           sink.frames[0].image_width == 8 && sink.frames[0].image_height == 6,
                       "FrameResult passthrough", "first frame fields wrong");
        context.expect(sink.frames[0].detections.size() == 2 && sink.frames[0].detections[0].candidate_index == 2 &&
                           sink.frames[0].detections[1].candidate_index == 5,
                       "Detection order", "PostProcessor order changed");
        context.expect(sink.frames[0].timings.has_value(), "timing enabled", "timings missing");
        if (sink.frames[0].timings.has_value()) {
            const runtime::FrameTimings& timing = *sink.frames[0].timings;
            context.expect(std::isfinite(timing.source_ms) && timing.source_ms >= 0.0 &&
                               std::isfinite(timing.preprocess_ms) && timing.preprocess_ms >= 0.0 &&
                               std::isfinite(timing.inference_ms) && timing.inference_ms >= 0.0 &&
                               std::isfinite(timing.postprocess_ms) && timing.postprocess_ms >= 0.0 &&
                               std::isfinite(timing.pre_sink_total_ms) && timing.pre_sink_total_ms >= 0.0,
                           "timing finite", "invalid timing value");
            context.expect(timing.pre_sink_total_ms >= timing.source_ms,
                           "pre-sink timing boundary", "total must include source stage");
        }
    }

    input_info = valid_input_info();
    FakeSource disabled_source({success_step(image(0, "frame.jpg"))});
    FakeEngine disabled_engine;
    RecordingSink disabled_sink;
    runtime::SerialRunner disabled_runner(disabled_source, preprocessor, input_info, disabled_engine, postprocessor, disabled_sink);
    runtime::RunSummary disabled_summary;
    context.expect(disabled_runner.run(metadata(false), &disabled_summary).ok(), "timing disabled run", "must succeed");
    context.expect(disabled_sink.frames.size() == 1 && !disabled_sink.frames[0].timings.has_value(),
                   "timing disabled", "must not create zero timing placeholder");
}

void test_fail_fast(TestContext& context) {
    const core::TensorInfo input_info = valid_input_info();
    preprocess::Preprocessor preprocessor;
    postprocess::PostProcessor postprocessor;
    const auto run_case = [&](const std::string& name, FakeSource& source, FakeEngine& engine,
                              RecordingSink& sink, const std::string& stage, bool item_context,
                              int expected_engine, int expected_writes, int expected_end,
                              bool expect_injected_detail = true) {
        runtime::SerialRunner runner(source, preprocessor, input_info, engine, postprocessor, sink);
        runtime::RunSummary summary = sentinel_summary();
        const core::Status status = runner.run(metadata(), &summary);
        expect_failure_context(context, name, status, stage, item_context,
                               expect_injected_detail);
        context.expect(summary_equal(summary, sentinel_summary()), name, "caller summary changed");
        context.expect(engine.calls == expected_engine && sink.write_calls == expected_writes && sink.end_calls == expected_end,
                       name, "fail-fast call counts wrong");
    };

    FakeSource begin_source({success_step(image(0, "frame.jpg"))}); FakeEngine begin_engine; RecordingSink begin_sink;
    begin_sink.begin_status = core::Status::failure(core::ErrorCode::kIoError, "injected begin");
    run_case("begin failure", begin_source, begin_engine, begin_sink, "sink.begin_run", false, 0, 0, 0);
    context.expect(begin_source.calls == 0, "begin failure", "source must not be read");

    FakeSource source_failure({{core::Status::failure(core::ErrorCode::kIoError, "injected source"), std::nullopt}}); FakeEngine source_engine; RecordingSink source_sink;
    run_case("source failure", source_failure, source_engine, source_sink, "source", false, 0, 0, 0);

    runtime::ImageItem bad_item = image(0, "frame.jpg"); bad_item.image_bgr = cv::Mat();
    FakeSource preprocess_failure({success_step(bad_item)}); FakeEngine preprocess_engine; RecordingSink preprocess_sink;
    run_case("preprocess failure", preprocess_failure, preprocess_engine, preprocess_sink, "preprocess", true, 0, 0, 0, false);

    FakeSource inference_failure({success_step(image(0, "frame.jpg"))}); FakeEngine inference_engine; RecordingSink inference_sink;
    inference_engine.status = core::Status::failure(core::ErrorCode::kBackendRuntimeError, "injected inference");
    run_case("inference failure", inference_failure, inference_engine, inference_sink, "inference", true, 1, 0, 0);

    FakeSource postprocess_failure({success_step(image(0, "frame.jpg"))}); FakeEngine postprocess_engine; RecordingSink postprocess_sink;
    postprocess_engine.output_tensor = raw_output(false);
    run_case("postprocess failure", postprocess_failure, postprocess_engine, postprocess_sink, "postprocess", true, 1, 0, 0, false);

    FakeSource write_failure({success_step(image(0, "frame.jpg")), success_step(image(1, "second.jpg"))}); FakeEngine write_engine; RecordingSink write_sink;
    write_sink.write_status = core::Status::failure(core::ErrorCode::kIoError, "injected write");
    run_case("write failure", write_failure, write_engine, write_sink, "sink.write_frame", true, 1, 1, 0);
    context.expect(write_failure.calls == 1, "write failure", "must not read next image");

    FakeSource end_failure({success_step(image(0, "frame.jpg"))}); FakeEngine end_engine; RecordingSink end_sink;
    end_sink.end_status = core::Status::failure(core::ErrorCode::kIoError, "injected end");
    run_case("end failure", end_failure, end_engine, end_sink, "sink.end_run", false, 1, 1, 1);

    FakeSource eos_source({}); FakeEngine eos_engine; RecordingSink eos_sink;
    run_case("immediate eos", eos_source, eos_engine, eos_sink, "source", false, 0, 0, 0, false);
    context.expect(eos_source.calls == 1, "immediate eos", "must read EOS once");
}

void test_injected_tensor_failure(TestContext& context) {
    FakeSource source({success_step(image(0, "frame.jpg"))});
    preprocess::Preprocessor preprocessor;
    core::TensorInfo invalid_info = valid_input_info();
    invalid_info.layout = core::TensorLayout::kBcn;
    FakeEngine engine;
    postprocess::PostProcessor postprocessor;
    RecordingSink sink;
    runtime::SerialRunner runner(source, preprocessor, invalid_info, engine, postprocessor, sink);
    runtime::RunSummary summary = sentinel_summary();
    const core::Status status = runner.run(metadata(), &summary);
    context.expect(!status.ok() && status.message().find("preprocess") != std::string::npos &&
                       status.message().find("sequence_index=0") != std::string::npos &&
                       status.message().find("frame.jpg") != std::string::npos,
                   "injected invalid TensorInfo", "preprocess context missing");
    context.expect(engine.calls == 0 && sink.write_calls == 0 && sink.end_calls == 0 &&
                       summary_equal(summary, sentinel_summary()),
                   "injected invalid TensorInfo", "failure must stop before engine and preserve summary");
}

}  // namespace

int main() {
    TestContext context;
    test_success_and_timing(context);
    test_fail_fast(context);
    test_injected_tensor_failure(context);
    if (context.failures() != 0) {
        std::cerr << context.failures() << " SerialRunner test(s) failed\n";
        return 1;
    }
    std::cout << "All SerialRunner tests passed\n";
    return 0;
}
