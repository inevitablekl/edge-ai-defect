#pragma once

#include "edge_ai_defect/runtime/result_sink.hpp"

#include <cstddef>
#include <ostream>

namespace edge_ai_defect::runtime {

class ConsoleSink final : public IResultSink {
public:
    explicit ConsoleSink(std::ostream& output);

    [[nodiscard]] core::Status begin_run(const RunMetadata& metadata) override;
    [[nodiscard]] core::Status write_frame(const FrameResult& frame) override;
    [[nodiscard]] core::Status end_run(const RunSummary& summary) override;

private:
    enum class State { kReady, kActive, kCompleted, kFailed };

    std::ostream& output_;
    State state_ = State::kReady;
    RunMetadata metadata_;
    std::size_t received_frames_ = 0;
    std::size_t received_detections_ = 0;
};

}  // namespace edge_ai_defect::runtime
