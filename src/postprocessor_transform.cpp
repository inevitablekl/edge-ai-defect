#include "postprocess_detail.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace edge_ai_defect::postprocess::detail {
namespace {

constexpr int kFrozenTargetWidth = 640;
constexpr int kFrozenTargetHeight = 640;

[[nodiscard]] bool valid_padding_sums(
    const preprocess::ImageTransformMetadata& transform) noexcept {
    const std::int64_t padded_width =
        static_cast<std::int64_t>(transform.resized_width) +
        static_cast<std::int64_t>(transform.pad_left) +
        static_cast<std::int64_t>(transform.pad_right);
    const std::int64_t padded_height =
        static_cast<std::int64_t>(transform.resized_height) +
        static_cast<std::int64_t>(transform.pad_top) +
        static_cast<std::int64_t>(transform.pad_bottom);
    return padded_width == transform.target_width &&
           padded_height == transform.target_height;
}

[[nodiscard]] core::Status transform_coordinate(
    float model_coordinate,
    int leading_padding,
    double gain,
    int original_extent,
    float& output_coordinate) {
    const double restored_coordinate =
        (static_cast<double>(model_coordinate) -
         static_cast<double>(leading_padding)) /
        gain;
    if (!std::isfinite(restored_coordinate)) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "inverse LetterBox coordinate must be finite");
    }

    const double clipped_coordinate = std::clamp(
        restored_coordinate, 0.0, static_cast<double>(original_extent));
    const float clipped_float = static_cast<float>(clipped_coordinate);
    if (!std::isfinite(clipped_float)) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "clipped detection coordinate must be finite");
    }

    output_coordinate = clipped_float;
    return core::Status::success();
}

}  // namespace

core::Status validate_transform_metadata(
    const preprocess::ImageTransformMetadata& transform) {
    if (transform.original_width <= 0 || transform.original_height <= 0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "transform original dimensions must be positive");
    }
    if (transform.target_width != kFrozenTargetWidth ||
        transform.target_height != kFrozenTargetHeight) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "transform target dimensions must be the frozen 640 by 640 input");
    }
    if (transform.resized_width <= 0 || transform.resized_height <= 0 ||
        transform.resized_width > transform.target_width ||
        transform.resized_height > transform.target_height) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "transform resized dimensions must be within the target bounds");
    }
    if (!std::isfinite(transform.gain) || transform.gain <= 0.0) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "transform gain must be finite and positive");
    }
    if (transform.pad_left < 0 || transform.pad_right < 0 ||
        transform.pad_top < 0 || transform.pad_bottom < 0) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "transform padding must be nonnegative");
    }
    if (!valid_padding_sums(transform)) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "transform resized dimensions and padding must match the target");
    }
    return core::Status::success();
}

core::Status transform_and_clip_detections(
    const std::vector<DecodedCandidate>& candidates,
    const preprocess::ImageTransformMetadata& transform,
    std::vector<Detection>* output) {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output must not be null");
    }
    const core::Status transform_status = validate_transform_metadata(transform);
    if (!transform_status.ok()) {
        return transform_status;
    }

    std::vector<Detection> detections;
    detections.reserve(candidates.size());
    for (const DecodedCandidate& candidate : candidates) {
        if (!std::isfinite(candidate.x1) || !std::isfinite(candidate.y1) ||
            !std::isfinite(candidate.x2) || !std::isfinite(candidate.y2) ||
            !std::isfinite(candidate.confidence)) {
            return core::Status::failure(
                core::ErrorCode::kInvalidArgument,
                "candidate coordinates and confidence must be finite");
        }

        Detection detection;
        core::Status coordinate_status = transform_coordinate(
            candidate.x1,
            transform.pad_left,
            transform.gain,
            transform.original_width,
            detection.x1);
        if (!coordinate_status.ok()) {
            return coordinate_status;
        }
        coordinate_status = transform_coordinate(candidate.y1,
                                                 transform.pad_top,
                                                 transform.gain,
                                                 transform.original_height,
                                                 detection.y1);
        if (!coordinate_status.ok()) {
            return coordinate_status;
        }
        coordinate_status = transform_coordinate(candidate.x2,
                                                 transform.pad_left,
                                                 transform.gain,
                                                 transform.original_width,
                                                 detection.x2);
        if (!coordinate_status.ok()) {
            return coordinate_status;
        }
        coordinate_status = transform_coordinate(candidate.y2,
                                                 transform.pad_top,
                                                 transform.gain,
                                                 transform.original_height,
                                                 detection.y2);
        if (!coordinate_status.ok()) {
            return coordinate_status;
        }

        detection.confidence = candidate.confidence;
        detection.class_id = candidate.class_id;
        detection.candidate_index = candidate.candidate_index;
        detections.push_back(detection);
    }

    *output = std::move(detections);
    return core::Status::success();
}

}  // namespace edge_ai_defect::postprocess::detail
