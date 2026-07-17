#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"

#include <opencv2/core/mat.hpp>

namespace edge_ai_defect::preprocess {

struct ImageTransformMetadata {
    int original_width = 0;
    int original_height = 0;
    int target_width = 0;
    int target_height = 0;
    int resized_width = 0;
    int resized_height = 0;
    double gain = 0.0;
    int pad_left = 0;
    int pad_right = 0;
    int pad_top = 0;
    int pad_bottom = 0;
};

[[nodiscard]] core::Status compute_letterbox_geometry(
    int original_width,
    int original_height,
    const core::TensorInfo& model_input_info,
    ImageTransformMetadata* metadata);

[[nodiscard]] core::Status letterbox_bgr(
    const cv::Mat& input_bgr,
    const core::TensorInfo& model_input_info,
    cv::Mat* output_bgr,
    ImageTransformMetadata* metadata);

}  // namespace edge_ai_defect::preprocess
