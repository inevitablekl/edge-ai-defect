#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"

namespace edge_ai_defect::runtime {

CanonicalHashSink::CanonicalHashSink(CanonicalHashScope scope, std::size_t cycle_length)
    : scope_(scope), cycle_length_(cycle_length) {}

core::Status CanonicalHashSink::begin_run(const RunMetadata&) {
    if (active_) return core::Status::failure(core::ErrorCode::kInvalidArgument, "CanonicalHashSink already active");
    frames_.clear(); run_hash_.clear(); cycle_hashes_.clear(); active_ = true; return core::Status::success();
}

core::Status CanonicalHashSink::write_frame(const FrameResult& frame) {
    if (!active_) return core::Status::failure(core::ErrorCode::kInvalidArgument, "CanonicalHashSink is not active");
    frames_.push_back(frame); return core::Status::success();
}

core::Status CanonicalHashSink::end_run(const RunSummary&) {
    if (!active_) return core::Status::failure(core::ErrorCode::kInvalidArgument, "CanonicalHashSink is not active");
    if (scope_ == CanonicalHashScope::RUN_AND_CYCLE) {
        auto status = canonical_detection_sha256(CanonicalScope::kRun, frames_, &run_hash_);
        if (!status.ok()) { active_ = false; return status; }
        if (cycle_length_ == 0) { active_ = false; return core::Status::failure(core::ErrorCode::kInvalidArgument, "cycle length is zero"); }
        for (std::size_t begin = 0; begin < frames_.size(); begin += cycle_length_) {
            const std::size_t end = std::min(begin + cycle_length_, frames_.size());
            std::vector<FrameResult> cycle(frames_.begin() + begin, frames_.begin() + end);
            std::string hash;
            status = canonical_detection_sha256(CanonicalScope::kCycle, cycle, &hash);
            if (!status.ok()) { active_ = false; return status; }
            cycle_hashes_[begin / cycle_length_] = std::move(hash);
        }
    }
    active_ = false; return core::Status::success();
}

}  // namespace edge_ai_defect::runtime
