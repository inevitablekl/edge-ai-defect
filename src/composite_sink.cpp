#include "edge_ai_defect/runtime/composite_sink.hpp"

#include <string>
#include <utility>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

}  // namespace

CompositeSink::CompositeSink(std::vector<std::unique_ptr<IResultSink>> sinks)
    : sinks_(std::move(sinks)) {}

core::Status CompositeSink::create(std::vector<std::unique_ptr<IResultSink>> sinks,
                                   std::unique_ptr<CompositeSink>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "CompositeSink create output must not be null");
    }
    if (sinks.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "CompositeSink requires at least one child sink");
    }
    for (const std::unique_ptr<IResultSink>& sink : sinks) {
        if (!sink) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "CompositeSink child sink must not be null");
        }
    }
    std::unique_ptr<CompositeSink> candidate(new CompositeSink(std::move(sinks)));
    *output = std::move(candidate);
    return Status::success();
}

core::Status CompositeSink::lifecycle_failure(const char* operation) const {
    return Status::failure(ErrorCode::kInvalidArgument,
                           std::string("CompositeSink cannot ") + operation +
                               " in its current lifecycle state");
}

core::Status CompositeSink::begin_run(const RunMetadata& metadata) {
    if (state_ != State::kReady) {
        return lifecycle_failure("begin_run");
    }
    for (const std::unique_ptr<IResultSink>& sink : sinks_) {
        const Status status = sink->begin_run(metadata);
        if (!status.ok()) {
            state_ = State::kFailed;
            return status;
        }
    }
    state_ = State::kActive;
    return Status::success();
}

core::Status CompositeSink::write_frame(const FrameResult& frame) {
    if (state_ != State::kActive) {
        return lifecycle_failure("write_frame");
    }
    for (const std::unique_ptr<IResultSink>& sink : sinks_) {
        const Status status = sink->write_frame(frame);
        if (!status.ok()) {
            state_ = State::kFailed;
            return status;
        }
    }
    return Status::success();
}

core::Status CompositeSink::end_run(const RunSummary& summary) {
    if (state_ != State::kActive) {
        return lifecycle_failure("end_run");
    }
    for (auto iterator = sinks_.rbegin(); iterator != sinks_.rend(); ++iterator) {
        const Status status = (*iterator)->end_run(summary);
        if (!status.ok()) {
            state_ = State::kFailed;
            return status;
        }
    }
    state_ = State::kCompleted;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
