#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cstddef>

namespace edge_ai_defect::postprocess {

struct PostprocessConfig {
    float confidence_threshold = 0.25F;
    float iou_threshold = 0.45F;
    std::size_t max_nms = 30000U;
    std::size_t max_det = 300U;
    float max_wh = 7680.0F;
    bool agnostic = false;
    bool multi_label = false;
};

[[nodiscard]] core::Status validate_postprocess_config(
    const PostprocessConfig& config);

}  // namespace edge_ai_defect::postprocess
