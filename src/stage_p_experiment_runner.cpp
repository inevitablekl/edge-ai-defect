#include "edge_ai_defect/runtime/stage_p_experiment_runner.hpp"

#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/pipeline_runner.hpp"
#include "edge_ai_defect/runtime/serial_runner.hpp"

#include <memory>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

class SinkForwarder final : public IResultSink {
public:
    explicit SinkForwarder(IResultSink& sink) : sink_(sink) {}
    core::Status begin_run(const RunMetadata& metadata) override { return sink_.begin_run(metadata); }
    core::Status write_frame(const FrameResult& frame) override { return sink_.write_frame(frame); }
    core::Status end_run(const RunSummary& summary) override { return sink_.end_run(summary); }
private:
    IResultSink& sink_;
};

}  // namespace

core::Status StagePExperimentRunner::run(
    ImageSource& source, preprocess::Preprocessor& preprocessor,
    const core::TensorInfo& model_input_info, inference::IInferenceEngine& engine,
    postprocess::PostProcessor& postprocessor, CanonicalHashSink& hash_sink,
    TimedJsonSink& timed_json_sink, const RunMetadata& metadata,
    std::uint32_t queue_capacity, RunSummary* summary,
    IFrameTraceObserver* trace_observer) {
    std::vector<std::unique_ptr<IResultSink>> sinks;
    sinks.push_back(std::make_unique<SinkForwarder>(timed_json_sink));
    sinks.push_back(std::make_unique<SinkForwarder>(hash_sink));
    std::unique_ptr<CompositeSink> composite;
    core::Status status = CompositeSink::create(std::move(sinks), &composite);
    if (!status.ok()) return status;
    if (metadata.runtime_v3.has_value() &&
        metadata.runtime_v3->runtime_mode == "serial") {
        SerialRunner runner(source, preprocessor, model_input_info, engine,
                            postprocessor, *composite, trace_observer);
        return runner.run(metadata, summary);
    }
    PipelineRunner runner(source, preprocessor, model_input_info, engine,
                          postprocessor, *composite, queue_capacity, trace_observer);
    return runner.run(metadata, summary);
}

}  // namespace edge_ai_defect::runtime
