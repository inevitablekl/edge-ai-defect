#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <optional>

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

}  // namespace edge_ai_defect::application
