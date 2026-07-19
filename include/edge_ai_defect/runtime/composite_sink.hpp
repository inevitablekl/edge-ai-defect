#pragma once

#include "edge_ai_defect/runtime/result_sink.hpp"

#include <memory>
#include <vector>

namespace edge_ai_defect::runtime {

class CompositeSink final : public IResultSink {
public:
    [[nodiscard]] static core::Status create(
        std::vector<std::unique_ptr<IResultSink>> sinks,
        std::unique_ptr<CompositeSink>* output);

    [[nodiscard]] core::Status begin_run(const RunMetadata& metadata) override;
    [[nodiscard]] core::Status write_frame(const FrameResult& frame) override;
    [[nodiscard]] core::Status end_run(const RunSummary& summary) override;

private:
    enum class State { kReady, kActive, kCompleted, kFailed };

    explicit CompositeSink(std::vector<std::unique_ptr<IResultSink>> sinks);
    [[nodiscard]] core::Status lifecycle_failure(const char* operation) const;

    std::vector<std::unique_ptr<IResultSink>> sinks_;
    State state_ = State::kReady;
};

}  // namespace edge_ai_defect::runtime
