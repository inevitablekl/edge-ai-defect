#include "postprocess_detail.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace edge_ai_defect::postprocess::detail {
namespace {

constexpr std::size_t kBatchSize = 1U;
constexpr std::size_t kChannelCount = 10U;
constexpr std::size_t kCandidateCount = 8400U;
constexpr std::size_t kClassCount = 6U;
constexpr std::array<std::int64_t, 3U> kExpectedShape{
    1,
    static_cast<std::int64_t>(kChannelCount),
    static_cast<std::int64_t>(kCandidateCount),
};
constexpr std::size_t kExpectedElementCount =
    kBatchSize * kChannelCount * kCandidateCount;

core::Status validate_raw_output_contract(const core::HostTensor& raw_output) {
    const core::Status host_status = core::validate_host_tensor(raw_output);
    if (!host_status.ok()) {
        return host_status;
    }
    if (raw_output.info.dtype != core::TensorDataType::kFloat32) {
        return core::Status::failure(core::ErrorCode::kUnsupportedDataType,
                                     "raw_output dtype must be float32");
    }
    if (raw_output.info.layout != core::TensorLayout::kBcn) {
        return core::Status::failure(core::ErrorCode::kUnsupportedLayout,
                                     "raw_output layout must be BCN");
    }
    if (raw_output.info.shape.size() != kExpectedShape.size()) {
        return core::Status::failure(core::ErrorCode::kInvalidShape,
                                     "raw_output shape must have rank 3");
    }
    for (std::size_t index = 0; index < kExpectedShape.size(); ++index) {
        if (raw_output.info.shape[index] != kExpectedShape[index]) {
            return core::Status::failure(
                core::ErrorCode::kInvalidShape,
                "raw_output shape must be [1, 10, 8400]");
        }
    }

    std::size_t element_count = 0U;
    const core::Status count_status =
        core::checked_element_count(raw_output.info.shape, element_count);
    if (!count_status.ok()) {
        return count_status;
    }
    if (element_count != kExpectedElementCount ||
        raw_output.data.size() != kExpectedElementCount) {
        return core::Status::failure(
            core::ErrorCode::kDataSizeMismatch,
            "raw_output must contain exactly 84000 float32 elements");
    }

    for (const float value : raw_output.data) {
        if (!std::isfinite(value)) {
            return core::Status::failure(
                core::ErrorCode::kInvalidArgument,
                "raw_output must not contain NaN or infinity");
        }
    }
    return core::Status::success();
}

[[nodiscard]] bool is_pre_nms_before(const DecodedCandidate& left,
                                      const DecodedCandidate& right) {
    if (left.confidence != right.confidence) {
        return left.confidence > right.confidence;
    }
    if (left.class_id != right.class_id) {
        return left.class_id < right.class_id;
    }
    return left.candidate_index < right.candidate_index;
}

}  // namespace

core::Status decode_candidates(const core::HostTensor& raw_output,
                               const PostprocessConfig& config,
                               std::vector<DecodedCandidate>* output) {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output must not be null");
    }

    const core::Status config_status = validate_postprocess_config(config);
    if (!config_status.ok()) {
        return config_status;
    }
    const core::Status raw_status = validate_raw_output_contract(raw_output);
    if (!raw_status.ok()) {
        return raw_status;
    }

    std::vector<DecodedCandidate> decoded;
    decoded.reserve(kCandidateCount);
    for (std::size_t candidate_index = 0U;
         candidate_index < kCandidateCount;
         ++candidate_index) {
        const float cx = raw_output.data[candidate_index];
        const float cy = raw_output.data[kCandidateCount + candidate_index];
        const float width = raw_output.data[2U * kCandidateCount + candidate_index];
        const float height = raw_output.data[3U * kCandidateCount + candidate_index];
        if (width <= 0.0F || height <= 0.0F) {
            continue;
        }

        int class_id = 0;
        float confidence = raw_output.data[4U * kCandidateCount + candidate_index];
        for (std::size_t class_index = 1U;
             class_index < kClassCount;
             ++class_index) {
            const float score = raw_output.data[
                (4U + class_index) * kCandidateCount + candidate_index];
            if (score > confidence) {
                confidence = score;
                class_id = static_cast<int>(class_index);
            }
        }
        if (confidence <= config.confidence_threshold) {
            continue;
        }

        const float half_width = width / 2.0F;
        const float half_height = height / 2.0F;
        const DecodedCandidate candidate{
            cx - half_width,
            cy - half_height,
            cx + half_width,
            cy + half_height,
            confidence,
            class_id,
            candidate_index,
        };
        if (!std::isfinite(candidate.x1) || !std::isfinite(candidate.y1) ||
            !std::isfinite(candidate.x2) || !std::isfinite(candidate.y2)) {
            continue;
        }
        decoded.push_back(candidate);
    }

    std::sort(decoded.begin(), decoded.end(), is_pre_nms_before);
    if (decoded.size() > config.max_nms) {
        decoded.resize(config.max_nms);
    }
    *output = std::move(decoded);
    return core::Status::success();
}

}  // namespace edge_ai_defect::postprocess::detail
