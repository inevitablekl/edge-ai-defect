#pragma once

#include "edge_ai_defect/runtime/result_sink.hpp"

#include <cstdint>

namespace edge_ai_defect::runtime {

class TimedJsonSink final : public IResultSink {
public:
    explicit TimedJsonSink(IResultSink& inner) : inner_(inner) {}
    [[nodiscard]] core::Status begin_run(const RunMetadata& metadata) override { return inner_.begin_run(metadata); }
    [[nodiscard]] core::Status write_frame(const FrameResult& frame) override { return inner_.write_frame(frame); }
    [[nodiscard]] core::Status end_run(const RunSummary& summary) override;
    [[nodiscard]] std::uint64_t end_run_duration_ns() const noexcept { return end_run_duration_ns_; }
private:
    IResultSink& inner_;
    std::uint64_t end_run_duration_ns_ = 0;
};

}  // namespace edge_ai_defect::runtime
