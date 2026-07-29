#include "edge_ai_defect/runtime/frame_trace.hpp"

#include <limits>
#include <algorithm>
#include <map>
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

ConcurrentFrameTraceRecorder::ConcurrentFrameTraceRecorder(ConcurrentTraceMode mode)
    : mode_(mode) {}

core::Status ConcurrentFrameTraceRecorder::on_stage_begin(
    std::size_t cycle_id, FrameTraceStage stage, std::uint64_t timestamp_ns) {
    std::lock_guard<std::mutex> lock(mutex_);
    const Key key{cycle_id, stage};
    if (active_.find(key) != active_.end()) return trace_error("duplicate active interval");
    active_.emplace(key, timestamp_ns);
    return Status::success();
}

core::Status ConcurrentFrameTraceRecorder::on_stage_end(
    std::size_t cycle_id, FrameTraceStage stage, std::uint64_t timestamp_ns) {
    std::lock_guard<std::mutex> lock(mutex_);
    const Key key{cycle_id, stage};
    const auto it = active_.find(key);
    if (it == active_.end()) return trace_error("stage end without matching interval");
    if (timestamp_ns < it->second) return trace_error("interval end precedes begin");
    const FrameTraceRecord record{cycle_id, stage, it->second, timestamp_ns,
                                  timestamp_ns - it->second};
    active_.erase(it);
    if (mode_ == ConcurrentTraceMode::kBufferedRecords) records_.push_back(record);
    FrameTraceAggregate& aggregate = aggregates_[stage];
    if (aggregate.count == 0) aggregate.min_ns = record.duration_ns;
    aggregate.count++;
    aggregate.total_ns += record.duration_ns;
    aggregate.min_ns = std::min(aggregate.min_ns, record.duration_ns);
    aggregate.max_ns = std::max(aggregate.max_ns, record.duration_ns);
    return Status::success();
}

core::Status ConcurrentFrameTraceRecorder::flush(std::ostream& output, bool flush_output) const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!active_.empty()) return trace_error("cannot flush with active intervals");
    if (mode_ == ConcurrentTraceMode::kBufferedRecords) {
        for (const FrameTraceRecord& record : records_) {
            output << "{\"cycle_id\":" << record.cycle_id
                   << ",\"stage\":\"" << frame_trace_stage_name(record.stage)
                   << "\",\"start_ns\":" << record.start_ns
                   << ",\"end_ns\":" << record.end_ns
                   << ",\"duration_ns\":" << record.duration_ns << "}\n";
        }
    }
    if (!output) return Status::failure(ErrorCode::kIoError, "frame trace: output write failed");
    if (flush_output) { output.flush(); if (!output) return Status::failure(ErrorCode::kIoError, "frame trace: output flush failed"); }
    return Status::success();
}

std::vector<FrameTraceRecord> ConcurrentFrameTraceRecorder::records() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return records_;
}

std::map<FrameTraceStage, FrameTraceAggregate> ConcurrentFrameTraceRecorder::aggregates() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return aggregates_;
}

bool ConcurrentFrameTraceRecorder::has_complete_frame(std::size_t cycle_id) const {
    std::lock_guard<std::mutex> lock(mutex_);
    constexpr FrameTraceStage stages[] = {FrameTraceStage::kSource, FrameTraceStage::kPreprocess,
                                          FrameTraceStage::kInference, FrameTraceStage::kPostprocess,
                                          FrameTraceStage::kSink};
    for (FrameTraceStage stage : stages) {
        const Key key{cycle_id, stage};
        if (active_.find(key) != active_.end()) return false;
        const bool found = std::any_of(records_.begin(), records_.end(),
            [cycle_id, stage](const FrameTraceRecord& record) {
                return record.cycle_id == cycle_id && record.stage == stage;
            });
        if (!found) return false;
    }
    return true;
}

}  // namespace edge_ai_defect::runtime
