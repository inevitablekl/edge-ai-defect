#pragma once

#include <cstddef>

namespace edge_ai_defect::postprocess {

// Bounding boxes use continuous original-image xyxy coordinates. Width and
// height are max(0, x2 - x1) and max(0, y2 - y1); no inclusive-pixel +1 term
// is used. Valid postprocessed coordinates are clipped to [0, image_width]
// and [0, image_height].
struct Detection {
    float x1 = 0.0F;
    float y1 = 0.0F;
    float x2 = 0.0F;
    float y2 = 0.0F;
    float confidence = 0.0F;
    int class_id = 0;

    // Zero-based position in the raw BCN candidate dimension, in [0, N).
    std::size_t candidate_index = 0;
};

}  // namespace edge_ai_defect::postprocess
