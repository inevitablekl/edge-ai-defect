#include "edge_ai_defect/runtime/timed_json_sink.hpp"

#include <chrono>

namespace edge_ai_defect::runtime {

core::Status TimedJsonSink::end_run(const RunSummary& summary) {
    const auto begin = std::chrono::steady_clock::now();
    const core::Status status = inner_.end_run(summary);
    end_run_duration_ns_ = static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - begin).count());
    return status;
}

}  // namespace edge_ai_defect::runtime
