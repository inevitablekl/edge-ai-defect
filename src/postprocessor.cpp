#include "edge_ai_defect/postprocess/postprocessor.hpp"

#include "postprocess_detail.hpp"

#include <utility>
#include <vector>

namespace edge_ai_defect::postprocess {

PostProcessor::PostProcessor(PostprocessConfig config)
    : config_(std::move(config)) {}

core::Status PostProcessor::process(
    const core::HostTensor& raw_output,
    const preprocess::ImageTransformMetadata& transform,
    std::vector<Detection>* output) const {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output must not be null");
    }
    const core::Status config_status = validate_postprocess_config(config_);
    if (!config_status.ok()) {
        return config_status;
    }
    const core::Status transform_status =
        detail::validate_transform_metadata(transform);
    if (!transform_status.ok()) {
        return transform_status;
    }

    std::vector<detail::DecodedCandidate> decoded;
    const core::Status decode_status =
        detail::decode_candidates(raw_output, config_, &decoded);
    if (!decode_status.ok()) {
        return decode_status;
    }

    std::vector<detail::DecodedCandidate> retained;
    const core::Status nms_status =
        detail::apply_class_aware_nms(decoded, config_, &retained);
    if (!nms_status.ok()) {
        return nms_status;
    }

    std::vector<Detection> detections;
    const core::Status detection_status = detail::transform_and_clip_detections(
        retained, transform, &detections);
    if (!detection_status.ok()) {
        return detection_status;
    }

    *output = std::move(detections);
    return core::Status::success();
}

}  // namespace edge_ai_defect::postprocess
