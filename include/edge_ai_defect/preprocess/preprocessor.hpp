#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/preprocess/letterbox.hpp"

namespace edge_ai_defect::preprocess {

struct PreprocessedFrame {
    core::HostTensor tensor;
    ImageTransformMetadata transform;
};

class Preprocessor final {
public:
    [[nodiscard]] core::Status preprocess(
        const cv::Mat& input_bgr,
        const core::TensorInfo& model_input_info,
        PreprocessedFrame* output) const;
};

}  // namespace edge_ai_defect::preprocess
