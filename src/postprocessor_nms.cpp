#include "postprocess_detail.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

namespace edge_ai_defect::postprocess::detail {
namespace {

constexpr int kFrozenClassCount = 6;

[[nodiscard]] bool is_finite(float value) noexcept {
    return std::isfinite(value);
}

[[nodiscard]] core::Status validate_internal_candidate(
    const DecodedCandidate& candidate) {
    if (candidate.class_id < 0 || candidate.class_id >= kFrozenClassCount) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "candidate class_id is outside [0, 6)");
    }
    if (!is_finite(candidate.x1) || !is_finite(candidate.y1) ||
        !is_finite(candidate.x2) || !is_finite(candidate.y2) ||
        !is_finite(candidate.confidence)) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "candidate coordinates and confidence must be finite");
    }
    if (candidate.x2 <= candidate.x1 || candidate.y2 <= candidate.y1) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "candidate must have positive continuous xyxy area");
    }
    return core::Status::success();
}

[[nodiscard]] float class_offset(const DecodedCandidate& candidate,
                                 const PostprocessConfig& config) noexcept {
    return static_cast<float>(candidate.class_id) * config.max_wh;
}

}  // namespace

float continuous_iou(const DecodedCandidate& lhs,
                     const DecodedCandidate& rhs,
                     float lhs_offset,
                     float rhs_offset) noexcept {
    const float lhs_x1 = lhs.x1 + lhs_offset;
    const float lhs_y1 = lhs.y1 + lhs_offset;
    const float lhs_x2 = lhs.x2 + lhs_offset;
    const float lhs_y2 = lhs.y2 + lhs_offset;
    const float rhs_x1 = rhs.x1 + rhs_offset;
    const float rhs_y1 = rhs.y1 + rhs_offset;
    const float rhs_x2 = rhs.x2 + rhs_offset;
    const float rhs_y2 = rhs.y2 + rhs_offset;
    if (!is_finite(lhs_x1) || !is_finite(lhs_y1) || !is_finite(lhs_x2) ||
        !is_finite(lhs_y2) || !is_finite(rhs_x1) || !is_finite(rhs_y1) ||
        !is_finite(rhs_x2) || !is_finite(rhs_y2)) {
        return 0.0F;
    }

    const float intersection_width = std::max(
        0.0F, std::min(lhs_x2, rhs_x2) - std::max(lhs_x1, rhs_x1));
    const float intersection_height = std::max(
        0.0F, std::min(lhs_y2, rhs_y2) - std::max(lhs_y1, rhs_y1));
    const float lhs_width = std::max(0.0F, lhs_x2 - lhs_x1);
    const float lhs_height = std::max(0.0F, lhs_y2 - lhs_y1);
    const float rhs_width = std::max(0.0F, rhs_x2 - rhs_x1);
    const float rhs_height = std::max(0.0F, rhs_y2 - rhs_y1);
    const float intersection_area = intersection_width * intersection_height;
    const float lhs_area = lhs_width * lhs_height;
    const float rhs_area = rhs_width * rhs_height;
    const float union_area = lhs_area + rhs_area - intersection_area;
    if (!is_finite(intersection_area) || !is_finite(lhs_area) ||
        !is_finite(rhs_area) || !is_finite(union_area) || union_area <= 0.0F) {
        return 0.0F;
    }

    const float iou = intersection_area / union_area;
    return is_finite(iou) ? iou : 0.0F;
}

core::Status apply_class_aware_nms(
    const std::vector<DecodedCandidate>& sorted_candidates,
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

    const std::size_t candidate_count =
        std::min(sorted_candidates.size(), config.max_nms);
    for (std::size_t index = 0U; index < candidate_count; ++index) {
        const core::Status candidate_status =
            validate_internal_candidate(sorted_candidates[index]);
        if (!candidate_status.ok()) {
            return candidate_status;
        }
    }

    std::vector<bool> suppressed(candidate_count, false);
    std::vector<DecodedCandidate> retained;
    retained.reserve(std::min(candidate_count, config.max_det));
    for (std::size_t current_index = 0U;
         current_index < candidate_count;
         ++current_index) {
        if (suppressed[current_index]) {
            continue;
        }

        const DecodedCandidate& current = sorted_candidates[current_index];
        retained.push_back(current);
        if (retained.size() == config.max_det) {
            break;
        }

        const float current_offset = class_offset(current, config);
        for (std::size_t later_index = current_index + 1U;
             later_index < candidate_count;
             ++later_index) {
            if (suppressed[later_index]) {
                continue;
            }
            const DecodedCandidate& later = sorted_candidates[later_index];
            const float later_offset = class_offset(later, config);
            if (continuous_iou(current, later, current_offset, later_offset) >
                config.iou_threshold) {
                suppressed[later_index] = true;
            }
        }
    }

    *output = std::move(retained);
    return core::Status::success();
}

}  // namespace edge_ai_defect::postprocess::detail
