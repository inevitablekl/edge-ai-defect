#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cstddef>
#include <cstdint>
#include <map>
#include <mutex>
#include <ostream>
#include <string>
#include <vector>

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

enum class ConcurrentTraceMode { kBufferedRecords, kAggregateOnly };

struct FrameTraceRecord {
    std::size_t cycle_id = 0;
    FrameTraceStage stage = FrameTraceStage::kSource;
    std::uint64_t start_ns = 0;
    std::uint64_t end_ns = 0;
    std::uint64_t duration_ns = 0;
};

struct FrameTraceAggregate {
    std::size_t count = 0;
    std::uint64_t total_ns = 0;
    std::uint64_t min_ns = 0;
    std::uint64_t max_ns = 0;
};

class ConcurrentFrameTraceRecorder final : public IFrameTraceObserver {
public:
    explicit ConcurrentFrameTraceRecorder(ConcurrentTraceMode mode = ConcurrentTraceMode::kBufferedRecords);

    [[nodiscard]] core::Status on_stage_begin(std::size_t cycle_id, FrameTraceStage stage,
                                               std::uint64_t monotonic_timestamp_ns) override;
    [[nodiscard]] core::Status on_stage_end(std::size_t cycle_id, FrameTraceStage stage,
                                             std::uint64_t monotonic_timestamp_ns) override;
    [[nodiscard]] core::Status flush(std::ostream& output, bool flush_output = true) const;
    [[nodiscard]] std::vector<FrameTraceRecord> records() const;
    [[nodiscard]] std::map<FrameTraceStage, FrameTraceAggregate> aggregates() const;
    [[nodiscard]] bool has_complete_frame(std::size_t cycle_id) const;

private:
    struct Key {
        std::size_t cycle_id;
        FrameTraceStage stage;
        bool operator<(const Key& other) const {
            return cycle_id < other.cycle_id ||
                   (cycle_id == other.cycle_id && stage < other.stage);
        }
    };
    mutable std::mutex mutex_;
    ConcurrentTraceMode mode_;
    std::map<Key, std::uint64_t> active_;
    std::vector<FrameTraceRecord> records_;
    std::map<FrameTraceStage, FrameTraceAggregate> aggregates_;
};

}  // namespace edge_ai_defect::runtime
