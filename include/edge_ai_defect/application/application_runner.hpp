#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <optional>

namespace edge_ai_defect::runtime {
class ImageSource;
class IResultSink;
}

namespace edge_ai_defect::application {

struct RunOptions {
    std::optional<bool> timing_enabled_override;
    runtime::IFrameTraceObserver* trace_observer = nullptr;
};

struct RunResult {
    core::Status status;
    bool runtime_failure = false;
};

[[nodiscard]] RunResult run(
    const runtime::RuntimeConfig& config,
    const RunOptions& options = {});

// Minimal internal composition seam shared by future serial and pipeline
// runners. It deliberately owns no registry, thread pool, or worker threads.
[[nodiscard]] RunResult run_with_components(
    const runtime::RuntimeConfig& config,
    runtime::ImageSource& source,
    runtime::IResultSink& sink,
    const RunOptions& options = {});

// Explicit experiment composition seam. The caller owns the source, sink, and
// backend-specific components; this function only dispatches the configured
// serial or pipeline runner with the supplied v3 metadata.
[[nodiscard]] RunResult run_with_components(
    const runtime::RuntimeConfig& config,
    runtime::ImageSource& source,
    runtime::IResultSink& sink,
    const runtime::RunMetadata& metadata,
    preprocess::Preprocessor& preprocessor,
    const core::TensorInfo& model_input_info,
    inference::IInferenceEngine& engine,
    postprocess::PostProcessor& postprocessor,
    runtime::RunSummary* summary,
    const RunOptions& options = {});

}  // namespace edge_ai_defect::application
