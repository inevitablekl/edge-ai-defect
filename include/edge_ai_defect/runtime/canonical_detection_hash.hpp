#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <cstdint>
#include <string>
#include <vector>

namespace edge_ai_defect::runtime {

enum class CanonicalScope : std::uint32_t { kRun = 1, kCycle = 2 };

[[nodiscard]] core::Status serialize_canonical_detections(
    CanonicalScope scope,
    const std::vector<FrameResult>& frames,
    std::vector<std::uint8_t>* output);

[[nodiscard]] core::Status canonical_detection_sha256(
    CanonicalScope scope,
    const std::vector<FrameResult>& frames,
    std::string* output_hex);

}  // namespace edge_ai_defect::runtime
