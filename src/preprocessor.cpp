#include "edge_ai_defect/preprocess/preprocessor.hpp"

#include <opencv2/core.hpp>

#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace edge_ai_defect::preprocess {
namespace {

core::Status validate_preprocess_input(
    const cv::Mat& input_bgr,
    const core::TensorInfo& model_input_info,
    std::size_t& element_count,
    int& target_height,
    int& target_width) {
    if (input_bgr.empty()) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "input_bgr must not be empty");
    }
    if (input_bgr.type() != CV_8UC3) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "input_bgr must have type CV_8UC3");
    }
    if (model_input_info.dtype != core::TensorDataType::kFloat32) {
        return core::Status::failure(
            core::ErrorCode::kUnsupportedDataType,
            "model_input_info.dtype must be float32");
    }
    if (model_input_info.layout != core::TensorLayout::kNchw) {
        return core::Status::failure(
            core::ErrorCode::kUnsupportedLayout,
            "model_input_info.layout must be NCHW");
    }
    if (model_input_info.shape.size() != 4U) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape must have rank 4");
    }
    if (model_input_info.shape[0] != 1) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape batch dimension must be 1");
    }
    if (model_input_info.shape[1] != 3) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape channel dimension must be 3");
    }

    const std::int64_t target_height_value = model_input_info.shape[2];
    const std::int64_t target_width_value = model_input_info.shape[3];
    if (target_height_value <= 0 || target_width_value <= 0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape height and width must be positive");
    }

    const core::Status count_status =
        core::checked_element_count(model_input_info.shape, element_count);
    if (!count_status.ok()) {
        return core::Status::failure(
            count_status.code(),
            "model_input_info.shape is invalid: " + count_status.message());
    }

    constexpr std::int64_t kMaximumInt =
        static_cast<std::int64_t>(std::numeric_limits<int>::max());
    if (target_height_value > kMaximumInt || target_width_value > kMaximumInt) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape height and width must fit in int");
    }

    target_height = static_cast<int>(target_height_value);
    target_width = static_cast<int>(target_width_value);
    return core::Status::success();
}

}  // namespace

core::Status Preprocessor::preprocess(
    const cv::Mat& input_bgr,
    const core::TensorInfo& model_input_info,
    PreprocessedFrame* output) const {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output must not be null");
    }

    std::size_t element_count = 0;
    int target_height = 0;
    int target_width = 0;
    const core::Status input_status = validate_preprocess_input(
        input_bgr,
        model_input_info,
        element_count,
        target_height,
        target_width);
    if (!input_status.ok()) {
        return input_status;
    }

    cv::Mat letterboxed_bgr;
    ImageTransformMetadata transform;
    const core::Status letterbox_status = letterbox_bgr(
        input_bgr, model_input_info, &letterboxed_bgr, &transform);
    if (!letterbox_status.ok()) {
        return letterbox_status;
    }
    if (letterboxed_bgr.type() != CV_8UC3 ||
        letterboxed_bgr.rows != target_height ||
        letterboxed_bgr.cols != target_width) {
        return core::Status::failure(
            core::ErrorCode::kImageProcessingError,
            "LetterBox output does not match the preprocessor target");
    }

    const std::size_t height = static_cast<std::size_t>(target_height);
    const std::size_t width = static_cast<std::size_t>(target_width);
    const std::size_t plane_size = height * width;
    if (plane_size > std::numeric_limits<std::size_t>::max() / 3U ||
        plane_size * 3U != element_count) {
        return core::Status::failure(
            core::ErrorCode::kDataSizeMismatch,
            "Preprocessor tensor element count does not match NCHW dimensions");
    }

    std::vector<float>& tensor_data = output->tensor.data;
    tensor_data.resize(element_count);
    for (int row = 0; row < target_height; ++row) {
        const cv::Vec3b* const pixels = letterboxed_bgr.ptr<cv::Vec3b>(row);
        const std::size_t row_offset =
            static_cast<std::size_t>(row) * width;
        for (int column = 0; column < target_width; ++column) {
            const cv::Vec3b& pixel = pixels[column];
            const std::size_t spatial_offset =
                row_offset + static_cast<std::size_t>(column);
            tensor_data[spatial_offset] =
                static_cast<float>(pixel[2]) / 255.0F;
            tensor_data[plane_size + spatial_offset] =
                static_cast<float>(pixel[1]) / 255.0F;
            tensor_data[2U * plane_size + spatial_offset] =
                static_cast<float>(pixel[0]) / 255.0F;
        }
    }

    output->tensor.info = model_input_info;
    output->transform = transform;
    return core::Status::success();
}

}  // namespace edge_ai_defect::preprocess
