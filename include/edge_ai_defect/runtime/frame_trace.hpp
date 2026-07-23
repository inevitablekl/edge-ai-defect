#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cstddef>
#include <cstdint>
#include <ostream>
#include <string>

namespace edge_ai_defect::runtime {

enum class FrameTraceStage {
    kSource,
    kPreprocess,
    kInference,
    kPostprocess,
    kSink,
};

[[nodiscard]] const char* frame_trace_stage_name(FrameTraceStage stage) noexcept;

class IFrameTraceObserver {
public:
    virtual ~IFrameTraceObserver() = default;

    [[nodiscard]] virtual core::Status on_stage_begin(
        std::size_t cycle_id,
        FrameTraceStage stage,
        std::uint64_t monotonic_timestamp_ns) = 0;

    [[nodiscard]] virtual core::Status on_stage_end(
        std::size_t cycle_id,
        FrameTraceStage stage,
        std::uint64_t monotonic_timestamp_ns) = 0;
};

class TraceRecorder final : public IFrameTraceObserver {
public:
    explicit TraceRecorder(std::ostream& output, bool flush_each_record = true);

    [[nodiscard]] core::Status on_stage_begin(
        std::size_t cycle_id,
        FrameTraceStage stage,
        std::uint64_t monotonic_timestamp_ns) override;

    [[nodiscard]] core::Status on_stage_end(
        std::size_t cycle_id,
        FrameTraceStage stage,
        std::uint64_t monotonic_timestamp_ns) override;

    [[nodiscard]] core::Status flush();

private:
    std::ostream& output_;
    bool flush_each_record_;
    bool active_stage_ = false;
    std::size_t active_cycle_id_ = 0;
    FrameTraceStage active_stage_kind_ = FrameTraceStage::kSource;
    std::uint64_t active_start_ns_ = 0;
    std::uint64_t last_timestamp_ns_ = 0;
};

}  // namespace edge_ai_defect::runtime
