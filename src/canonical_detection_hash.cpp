#include "edge_ai_defect/runtime/canonical_detection_hash.hpp"

#include <openssl/sha.h>

#include <cmath>
#include <cstring>
#include <limits>
#include <type_traits>

static_assert(sizeof(float) == 4, "canonical serializer requires IEEE 754 binary32 float");
static_assert(std::numeric_limits<float>::is_iec559, "canonical serializer requires IEC 559 / IEEE 754 float");

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

void u32(std::vector<std::uint8_t>& b, std::uint32_t v) {
    for (int i = 0; i < 4; ++i) b.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
}
void u64(std::vector<std::uint8_t>& b, std::uint64_t v) {
    for (int i = 0; i < 8; ++i) b.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
}
void i32(std::vector<std::uint8_t>& b, std::int32_t v) { u32(b, static_cast<std::uint32_t>(v)); }
void bits(std::vector<std::uint8_t>& b, float value) {
    std::uint32_t raw = 0;
    std::memcpy(&raw, &value, sizeof(raw));
    u32(b, raw);
}

Status checked_i32(int value, const char* field) {
    if (static_cast<long long>(value) < std::numeric_limits<std::int32_t>::min() ||
        static_cast<long long>(value) > std::numeric_limits<std::int32_t>::max())
        return Status::failure(ErrorCode::kOverflow, std::string(field) + " does not fit int32");
    return Status::success();
}

Status checked_u64(std::size_t value, const char* field) {
    if (value > static_cast<std::size_t>(std::numeric_limits<std::uint64_t>::max()))
        return Status::failure(ErrorCode::kOverflow, std::string(field) + " does not fit uint64");
    return Status::success();
}

Status checked_u32(std::size_t value, const char* field) {
    if (value > static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max()))
        return Status::failure(ErrorCode::kOverflow, std::string(field) + " does not fit uint32");
    return Status::success();
}

}  // namespace

core::Status serialize_canonical_detections(CanonicalScope scope,
                                             const std::vector<FrameResult>& frames,
                                             std::vector<std::uint8_t>* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "canonical output is null");
    if (scope != CanonicalScope::kRun && scope != CanonicalScope::kCycle)
        return Status::failure(ErrorCode::kInvalidArgument, "canonical scope is invalid");
    Status count_status = checked_u64(frames.size(), "frame count");
    if (!count_status.ok()) return count_status;
    std::vector<std::uint8_t> bytes;
    const char magic[] = "EAICANON";
    bytes.insert(bytes.end(), magic, magic + 8);
    u32(bytes, 1);
    u32(bytes, static_cast<std::uint32_t>(scope));
    std::uint64_t total = 0;
    for (std::size_t frame_index = 0; frame_index < frames.size(); ++frame_index) {
        const FrameResult& frame = frames[frame_index];
        const std::string path = frame.relative_path.generic_u8string();
        Status len_status = checked_u32(path.size(), "path length");
        if (!len_status.ok()) return len_status;
        len_status = checked_u32(frame.detections.size(), "detection count per frame");
        if (!len_status.ok()) return len_status;
        Status status = checked_i32(frame.image_width, "image_width");
        if (!status.ok()) return status;
        status = checked_i32(frame.image_height, "image_height");
        if (!status.ok()) return status;
        // RUN scope: use global sequence_index.
        // CYCLE scope: use zero-based position within the cycle vector.
        const std::uint64_t sequence_or_frame_index =
            (scope == CanonicalScope::kRun)
                ? static_cast<std::uint64_t>(frame.sequence_index)
                : static_cast<std::uint64_t>(frame_index);
        u64(bytes, sequence_or_frame_index);
        u32(bytes, static_cast<std::uint32_t>(path.size()));
        bytes.insert(bytes.end(), path.begin(), path.end());
        i32(bytes, frame.image_width); i32(bytes, frame.image_height);
        u32(bytes, static_cast<std::uint32_t>(frame.detections.size()));
        if (total > std::numeric_limits<std::uint64_t>::max() - frame.detections.size())
            return Status::failure(ErrorCode::kOverflow, "detection count overflows uint64");
        total += frame.detections.size();
        for (const auto& detection : frame.detections) {
            if (!std::isfinite(detection.x1) || !std::isfinite(detection.y1) ||
                !std::isfinite(detection.x2) || !std::isfinite(detection.y2) ||
                !std::isfinite(detection.confidence))
                return Status::failure(ErrorCode::kInvalidArgument, "canonical float must be finite");
            Status idx_status = checked_u64(detection.candidate_index, "candidate_index");
            if (!idx_status.ok()) return idx_status;
            u64(bytes, static_cast<std::uint64_t>(detection.candidate_index));
            i32(bytes, detection.class_id); bits(bytes, detection.confidence);
            bits(bytes, detection.x1); bits(bytes, detection.y1);
            bits(bytes, detection.x2); bits(bytes, detection.y2);
        }
    }
    u64(bytes, static_cast<std::uint64_t>(frames.size()));
    u64(bytes, total);
    *output = std::move(bytes);
    return Status::success();
}

core::Status canonical_detection_sha256(CanonicalScope scope,
                                        const std::vector<FrameResult>& frames,
                                        std::string* output_hex) {
    if (output_hex == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "canonical hash output is null");
    std::vector<std::uint8_t> bytes;
    Status status = serialize_canonical_detections(scope, frames, &bytes);
    if (!status.ok()) return status;
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(bytes.data(), bytes.size(), digest);
    static constexpr char hex[] = "0123456789abcdef";
    std::string result;
    result.reserve(64);
    for (unsigned char value : digest) { result.push_back(hex[value >> 4]); result.push_back(hex[value & 0x0f]); }
    *output_hex = std::move(result);
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
