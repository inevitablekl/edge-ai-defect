#pragma once

#include "edge_ai_defect/runtime/canonical_detection_hash.hpp"
#include "edge_ai_defect/runtime/result_sink.hpp"

#include <map>

namespace edge_ai_defect::runtime {

enum class CanonicalHashScope { RUN_AND_CYCLE };

class CanonicalHashSink final : public IResultSink {
public:
    explicit CanonicalHashSink(CanonicalHashScope scope = CanonicalHashScope::RUN_AND_CYCLE,
                               std::size_t cycle_length = 180);
    [[nodiscard]] core::Status begin_run(const RunMetadata& metadata) override;
    [[nodiscard]] core::Status write_frame(const FrameResult& frame) override;
    [[nodiscard]] core::Status end_run(const RunSummary& summary) override;
    [[nodiscard]] const std::string& run_hash() const noexcept { return run_hash_; }
    [[nodiscard]] const std::map<std::size_t, std::string>& cycle_hashes() const noexcept { return cycle_hashes_; }
    [[nodiscard]] const std::vector<FrameResult>& frames() const noexcept { return frames_; }

private:
    CanonicalHashScope scope_;
    std::size_t cycle_length_;
    std::vector<FrameResult> frames_;
    std::string run_hash_;
    std::map<std::size_t, std::string> cycle_hashes_;
    bool active_ = false;
};

}  // namespace edge_ai_defect::runtime
