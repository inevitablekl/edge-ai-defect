#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/postprocess/detection.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"
#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <vector>

namespace edge_ai_defect::postprocess {

class PostProcessor final {
public:
    explicit PostProcessor(PostprocessConfig config = {});

    // output must not be null; a null pointer returns kInvalidArgument. On any
    // failure, output must retain its original value. The M3.1 contract
    // declares this operation; candidate decoding begins in M3.2.
    [[nodiscard]] core::Status process(
        const core::HostTensor& raw_output,
        const preprocess::ImageTransformMetadata& transform,
        std::vector<Detection>* output) const;

private:
    PostprocessConfig config_;
};

}  // namespace edge_ai_defect::postprocess
