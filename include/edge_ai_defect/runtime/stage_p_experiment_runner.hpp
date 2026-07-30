#pragma once

#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/timed_json_sink.hpp"

namespace edge_ai_defect::runtime {

class StagePExperimentRunner final {
public:
    [[nodiscard]] static core::Status run(
        CorpusReplaySource& source,
        preprocess::Preprocessor& preprocessor,
        const core::TensorInfo& model_input_info,
        inference::IInferenceEngine& engine,
        postprocess::PostProcessor& postprocessor,
        CanonicalHashSink& hash_sink,
        TimedJsonSink& timed_json_sink,
        const RunMetadata& metadata,
        std::uint32_t queue_capacity,
        RunSummary* summary,
        IFrameTraceObserver* trace_observer = nullptr);
};

}  // namespace edge_ai_defect::runtime
