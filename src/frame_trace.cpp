#include "edge_ai_defect/runtime/frame_trace.hpp"

#include <limits>
#include <string>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status trace_error(const std::string& detail) {
    return Status::failure(ErrorCode::kInvalidArgument, "frame trace: " + detail);
}

}  // namespace

const char* frame_trace_stage_name(FrameTraceStage stage) noexcept {
    switch (stage) {
        case FrameTraceStage::kSource:
            return "source";
        case FrameTraceStage::kPreprocess:
            return "preprocess";
        case FrameTraceStage::kInference:
            return "inference";
        case FrameTraceStage::kPostprocess:
            return "postprocess";
        case FrameTraceStage::kSink:
            return "sink";
    }
    return "unknown";
}

TraceRecorder::TraceRecorder(std::ostream& output, bool flush_each_record)
    : output_(output), flush_each_record_(flush_each_record) {}

core::Status TraceRecorder::on_stage_begin(
    std::size_t cycle_id,
    FrameTraceStage stage,
    std::uint64_t monotonic_timestamp_ns) {
    if (active_stage_) {
        return trace_error("stage begin while another stage is active");
    }
    if (monotonic_timestamp_ns < last_timestamp_ns_) {
        return trace_error("timestamp is not monotonic");
    }
    active_stage_ = true;
    active_cycle_id_ = cycle_id;
    active_stage_kind_ = stage;
    active_start_ns_ = monotonic_timestamp_ns;
    last_timestamp_ns_ = monotonic_timestamp_ns;
    return Status::success();
}

core::Status TraceRecorder::on_stage_end(
    std::size_t cycle_id,
    FrameTraceStage stage,
    std::uint64_t monotonic_timestamp_ns) {
    if (!active_stage_) {
        return trace_error("stage end without an active stage");
    }
    if (cycle_id != active_cycle_id_ || stage != active_stage_kind_) {
        return trace_error("stage end does not match active stage");
    }
    if (monotonic_timestamp_ns < active_start_ns_ ||
        monotonic_timestamp_ns < last_timestamp_ns_) {
        return trace_error("timestamp is not monotonic");
    }

    const std::uint64_t duration_ns = monotonic_timestamp_ns - active_start_ns_;
    output_ << "{\"cycle_id\":" << active_cycle_id_
            << ",\"stage\":\"" << frame_trace_stage_name(active_stage_kind_)
            << "\",\"start_ns\":" << active_start_ns_
            << ",\"end_ns\":" << monotonic_timestamp_ns
            << ",\"duration_ns\":" << duration_ns << "}\n";
    if (!output_) {
        return Status::failure(ErrorCode::kIoError,
                               "frame trace: output write failed");
    }
    if (flush_each_record_) {
        output_.flush();
        if (!output_) {
            return Status::failure(ErrorCode::kIoError,
                                   "frame trace: output flush failed");
        }
    }
    active_stage_ = false;
    last_timestamp_ns_ = monotonic_timestamp_ns;
    return Status::success();
}

core::Status TraceRecorder::flush() {
    output_.flush();
    if (!output_) {
        return Status::failure(ErrorCode::kIoError,
                               "frame trace: output flush failed");
    }
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
