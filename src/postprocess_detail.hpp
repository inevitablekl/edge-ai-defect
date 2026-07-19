#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/postprocess/detection.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"
#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <cstddef>
#include <vector>

namespace edge_ai_defect::postprocess::detail {

// Internal pre-NMS representation in continuous model-input xyxy coordinates.
// This is not a public Detection and has not been restored to original-image
// coordinates.
struct DecodedCandidate {
    float x1 = 0.0F;
    float y1 = 0.0F;
    float x2 = 0.0F;
    float y2 = 0.0F;
    float confidence = 0.0F;
    int class_id = 0;
    std::size_t candidate_index = 0;
};

[[nodiscard]] core::Status decode_candidates(
    const core::HostTensor& raw_output,
    const PostprocessConfig& config,
    std::vector<DecodedCandidate>* output);

[[nodiscard]] float continuous_iou(
    const DecodedCandidate& lhs,
    const DecodedCandidate& rhs,
    float lhs_offset = 0.0F,
    float rhs_offset = 0.0F) noexcept;

[[nodiscard]] core::Status apply_class_aware_nms(
    const std::vector<DecodedCandidate>& sorted_candidates,
    const PostprocessConfig& config,
    std::vector<DecodedCandidate>* output);

[[nodiscard]] core::Status validate_transform_metadata(
    const preprocess::ImageTransformMetadata& transform);

[[nodiscard]] core::Status transform_and_clip_detections(
    const std::vector<DecodedCandidate>& candidates,
    const preprocess::ImageTransformMetadata& transform,
    std::vector<Detection>* output);

}  // namespace edge_ai_defect::postprocess::detail
