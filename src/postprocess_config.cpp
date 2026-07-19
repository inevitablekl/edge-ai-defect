#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cmath>

namespace edge_ai_defect::postprocess {

core::Status validate_postprocess_config(const PostprocessConfig& config) {
    if (!std::isfinite(config.confidence_threshold) ||
        config.confidence_threshold < 0.0F ||
        config.confidence_threshold > 1.0F) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "confidence_threshold must be finite and within [0, 1]");
    }
    if (!std::isfinite(config.iou_threshold) ||
        config.iou_threshold < 0.0F || config.iou_threshold > 1.0F) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "iou_threshold must be finite and within [0, 1]");
    }
    if (config.max_det == 0U) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "max_det must be positive");
    }
    if (config.max_nms == 0U) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "max_nms must be positive");
    }
    if (config.max_nms < config.max_det) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "max_nms must be greater than or equal to max_det");
    }
    if (!std::isfinite(config.max_wh) || config.max_wh <= 0.0F) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "max_wh must be finite and positive");
    }
    if (config.multi_label) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "multi_label must remain false in M3");
    }
    if (config.agnostic) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "agnostic must remain false in M3");
    }
    return core::Status::success();
}

}  // namespace edge_ai_defect::postprocess
