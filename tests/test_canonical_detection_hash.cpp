#include "edge_ai_defect/runtime/canonical_detection_hash.hpp"

#include <cmath>
#include <iostream>
#include <limits>
#include <iomanip>
#include <sstream>

using namespace edge_ai_defect;

int main() {
    runtime::FrameResult frame;
    frame.sequence_index = 0;
    frame.relative_path = "a.jpg";
    frame.image_width = 10;
    frame.image_height = 20;
    frame.detections.push_back({-0.0F, 1.0F, 2.0F, 3.0F, 0.5F, 0, 4});
    std::vector<runtime::FrameResult> frames{frame};
    std::string run_hash;
    std::string cycle_hash;
    if (!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, frames, &run_hash).ok() ||
        !runtime::canonical_detection_sha256(runtime::CanonicalScope::kCycle, frames, &cycle_hash).ok() ||
        run_hash == cycle_hash || run_hash.size() != 64U) return 1;
    frame.detections[0].x1 = 0.0F;
    std::string positive_hash;
    if (!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {frame}, &positive_hash).ok() ||
        positive_hash == run_hash) return 1;
    frame.detections[0].x1 = std::numeric_limits<float>::quiet_NaN();
    if (runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {frame}, &run_hash).ok()) return 1;
    frame.detections[0].x1 = std::numeric_limits<float>::infinity();
    if (runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {frame}, &run_hash).ok()) return 1;
    std::vector<std::uint8_t> bytes;
    if (!runtime::serialize_canonical_detections(runtime::CanonicalScope::kRun, {}, &bytes).ok() ||
        bytes.size() != 8U + 4U + 4U + 8U + 8U) return 1;
    std::ostringstream vector_hex;
    vector_hex << std::hex << std::setfill('0');
    for (std::uint8_t value : bytes) vector_hex << std::setw(2) << static_cast<unsigned>(value);
    if (vector_hex.str() != "45414943414e4f4e010000000100000000000000000000000000000000000000") return 1;
    std::string empty_hash;
    if (!runtime::canonical_detection_sha256(runtime::CanonicalScope::kRun, {}, &empty_hash).ok() ||
        empty_hash != "f48f8ba534f74ee56cdb1b884c182afe0af7dbf7667219e8eb32dc769649d39d") return 1;
    std::cout << "Canonical detection hash tests passed\n";
    return 0;
}
