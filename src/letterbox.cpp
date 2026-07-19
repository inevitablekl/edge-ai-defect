#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <utility>

namespace edge_ai_defect::preprocess {
namespace {

core::Status validate_model_input_info(
    const core::TensorInfo& model_input_info,
    int& target_width,
    int& target_height) {
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

    constexpr std::int64_t kMaximumInt =
        static_cast<std::int64_t>(std::numeric_limits<int>::max());
    const std::int64_t target_height_value = model_input_info.shape[2];
    const std::int64_t target_width_value = model_input_info.shape[3];
    if (target_height_value <= 0 || target_width_value <= 0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape height and width must be positive");
    }
    if (target_height_value > kMaximumInt || target_width_value > kMaximumInt) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "model_input_info.shape height and width must fit in int");
    }

    std::size_t element_count = 0;
    const core::Status count_status =
        core::checked_element_count(model_input_info.shape, element_count);
    if (!count_status.ok()) {
        return core::Status::failure(
            count_status.code(),
            "model_input_info.shape is invalid: " + count_status.message());
    }

    target_height = static_cast<int>(target_height_value);
    target_width = static_cast<int>(target_width_value);
    return core::Status::success();
}

core::Status python_round_nonnegative(double value, int& rounded_value) {
    if (!std::isfinite(value) || value < 0.0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "Python-compatible rounding requires a finite nonnegative value");
    }

    const double lower = std::floor(value);
    const double fraction = value - lower;
    double rounded = lower;
    if (fraction > 0.5 ||
        (fraction == 0.5 && std::fmod(lower, 2.0) != 0.0)) {
        rounded = lower + 1.0;
    }

    if (rounded > static_cast<double>(std::numeric_limits<int>::max())) {
        return core::Status::failure(
            core::ErrorCode::kOverflow,
            "Rounded image dimension exceeds int range");
    }

    rounded_value = static_cast<int>(rounded);
    return core::Status::success();
}

core::Status split_padding(int total_padding,
                           int& leading_padding,
                           int& trailing_padding) {
    if (total_padding == 0) {
        leading_padding = 0;
        trailing_padding = 0;
        return core::Status::success();
    }

    const double half_padding = static_cast<double>(total_padding) / 2.0;
    const core::Status leading_status =
        python_round_nonnegative(half_padding - 0.1, leading_padding);
    if (!leading_status.ok()) {
        return leading_status;
    }
    const core::Status trailing_status =
        python_round_nonnegative(half_padding + 0.1, trailing_padding);
    if (!trailing_status.ok()) {
        return trailing_status;
    }
    if (leading_padding + trailing_padding != total_padding) {
        return core::Status::failure(
            core::ErrorCode::kImageProcessingError,
            "LetterBox padding split does not preserve the target dimension");
    }
    return core::Status::success();
}

}  // namespace

core::Status compute_letterbox_geometry(
    int original_width,
    int original_height,
    const core::TensorInfo& model_input_info,
    ImageTransformMetadata* metadata) {
    if (metadata == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "metadata must not be null");
    }
    if (original_width <= 0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "original_width must be positive");
    }
    if (original_height <= 0) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "original_height must be positive");
    }

    int target_width = 0;
    int target_height = 0;
    const core::Status input_info_status = validate_model_input_info(
        model_input_info, target_width, target_height);
    if (!input_info_status.ok()) {
        return input_info_status;
    }

    const double height_gain = static_cast<double>(target_height) /
                               static_cast<double>(original_height);
    const double width_gain = static_cast<double>(target_width) /
                              static_cast<double>(original_width);
    const double gain = std::min(height_gain, width_gain);
    if (!std::isfinite(gain) || gain <= 0.0) {
        return core::Status::failure(core::ErrorCode::kInvalidShape,
                                     "LetterBox gain must be finite and positive");
    }

    int resized_width = 0;
    int resized_height = 0;
    const core::Status width_status = python_round_nonnegative(
        static_cast<double>(original_width) * gain, resized_width);
    if (!width_status.ok()) {
        return width_status;
    }
    const core::Status height_status = python_round_nonnegative(
        static_cast<double>(original_height) * gain, resized_height);
    if (!height_status.ok()) {
        return height_status;
    }
    if (resized_width <= 0 || resized_height <= 0 ||
        resized_width > target_width || resized_height > target_height) {
        return core::Status::failure(
            core::ErrorCode::kImageProcessingError,
            "LetterBox resized dimensions are outside the target bounds");
    }

    const int horizontal_padding = target_width - resized_width;
    const int vertical_padding = target_height - resized_height;
    int pad_left = 0;
    int pad_right = 0;
    int pad_top = 0;
    int pad_bottom = 0;
    const core::Status horizontal_status =
        split_padding(horizontal_padding, pad_left, pad_right);
    if (!horizontal_status.ok()) {
        return horizontal_status;
    }
    const core::Status vertical_status =
        split_padding(vertical_padding, pad_top, pad_bottom);
    if (!vertical_status.ok()) {
        return vertical_status;
    }

    const ImageTransformMetadata computed_metadata{
        original_width,
        original_height,
        target_width,
        target_height,
        resized_width,
        resized_height,
        gain,
        pad_left,
        pad_right,
        pad_top,
        pad_bottom,
    };
    *metadata = computed_metadata;
    return core::Status::success();
}

core::Status letterbox_bgr(const cv::Mat& input_bgr,
                           const core::TensorInfo& model_input_info,
                           cv::Mat* output_bgr,
                           ImageTransformMetadata* metadata) {
    if (output_bgr == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output_bgr must not be null");
    }
    if (metadata == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "metadata must not be null");
    }
    if (input_bgr.empty()) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "input_bgr must not be empty");
    }
    if (input_bgr.type() != CV_8UC3) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "input_bgr must have type CV_8UC3");
    }

    ImageTransformMetadata computed_metadata;
    const core::Status geometry_status = compute_letterbox_geometry(
        input_bgr.cols, input_bgr.rows, model_input_info, &computed_metadata);
    if (!geometry_status.ok()) {
        return geometry_status;
    }

    cv::Mat resized_bgr;
    cv::Mat transformed_bgr;
    try {
        if (computed_metadata.resized_width == input_bgr.cols &&
            computed_metadata.resized_height == input_bgr.rows) {
            resized_bgr = input_bgr.clone();
        } else {
            cv::resize(input_bgr,
                       resized_bgr,
                       cv::Size(computed_metadata.resized_width,
                                computed_metadata.resized_height),
                       0.0,
                       0.0,
                       cv::INTER_LINEAR);
        }

        if (computed_metadata.pad_left == 0 &&
            computed_metadata.pad_right == 0 &&
            computed_metadata.pad_top == 0 &&
            computed_metadata.pad_bottom == 0) {
            transformed_bgr = std::move(resized_bgr);
        } else {
            cv::copyMakeBorder(resized_bgr,
                               transformed_bgr,
                               computed_metadata.pad_top,
                               computed_metadata.pad_bottom,
                               computed_metadata.pad_left,
                               computed_metadata.pad_right,
                               cv::BORDER_CONSTANT,
                               cv::Scalar(114, 114, 114));
        }
    } catch (const cv::Exception& exception) {
        return core::Status::failure(
            core::ErrorCode::kImageProcessingError,
            "OpenCV LetterBox processing failed: " +
                std::string(exception.what()));
    }

    if (transformed_bgr.empty() || transformed_bgr.type() != CV_8UC3 ||
        transformed_bgr.cols != computed_metadata.target_width ||
        transformed_bgr.rows != computed_metadata.target_height) {
        return core::Status::failure(
            core::ErrorCode::kImageProcessingError,
            "OpenCV LetterBox output does not match the target image contract");
    }

    *metadata = computed_metadata;
    *output_bgr = std::move(transformed_bgr);
    return core::Status::success();
}

}  // namespace edge_ai_defect::preprocess
