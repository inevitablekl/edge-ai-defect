#pragma once

#include <cstddef>

namespace edge_ai_defect::runtime {

// R1's fixed ten-cycle schedule: each manifest position is sampled once.
[[nodiscard]] constexpr bool should_sample_diagnostic(
    std::size_t frame_in_cycle, std::size_t cycle_index) noexcept {
    return frame_in_cycle % 10U == cycle_index % 10U;
}

}  // namespace edge_ai_defect::runtime
