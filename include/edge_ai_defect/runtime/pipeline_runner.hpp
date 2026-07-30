#pragma once

#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/bounded_queue.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/image_source.hpp"
#include "edge_ai_defect/runtime/result_sink.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

namespace edge_ai_defect::runtime {

class PipelineRunner final {
public:
    PipelineRunner(ImageSource& source,
                   preprocess::Preprocessor& preprocessor,
                   const core::TensorInfo& model_input_info,
                   inference::IInferenceEngine& engine,
                   postprocess::PostProcessor& postprocessor,
                   IResultSink& sink,
                   std::uint32_t queue_capacity,
                   IFrameTraceObserver* trace_observer = nullptr);

    [[nodiscard]] core::Status run(const RunMetadata& metadata,
                                   RunSummary* summary);

private:
    ImageSource& source_;
    preprocess::Preprocessor& preprocessor_;
    core::TensorInfo model_input_info_;
    inference::IInferenceEngine& engine_;
    postprocess::PostProcessor& postprocessor_;
    IResultSink& sink_;
    std::uint32_t queue_capacity_;
    IFrameTraceObserver* trace_observer_ = nullptr;
};

}  // namespace edge_ai_defect::runtime
