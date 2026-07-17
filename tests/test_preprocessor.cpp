#include "edge_ai_defect/preprocess/preprocessor.hpp"

#include <opencv2/core.hpp>

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace preprocess = edge_ai_defect::preprocess;

constexpr float kFloatTolerance = 1.0e-7F;

class TestContext {
public:
    void expect(bool condition,
                const std::string& case_name,
                const std::string& detail) {
        if (!condition) {
            ++failure_count_;
            std::cerr << "FAILED: " << case_name << ": " << detail << '\n';
        }
    }

    [[nodiscard]] int failure_count() const noexcept {
        return failure_count_;
    }

private:
    int failure_count_ = 0;
};

core::TensorInfo make_model_input_info(std::int64_t height,
                                       std::int64_t width) {
    return {
        core::TensorDataType::kFloat32,
        core::TensorLayout::kNchw,
        {1, 3, height, width},
    };
}

bool tensor_info_equal(const core::TensorInfo& left,
                       const core::TensorInfo& right) {
    return left.dtype == right.dtype && left.layout == right.layout &&
           left.shape == right.shape;
}

bool transform_equal(const preprocess::ImageTransformMetadata& left,
                     const preprocess::ImageTransformMetadata& right) {
    return left.original_width == right.original_width &&
           left.original_height == right.original_height &&
           left.target_width == right.target_width &&
           left.target_height == right.target_height &&
           left.resized_width == right.resized_width &&
           left.resized_height == right.resized_height &&
           left.gain == right.gain && left.pad_left == right.pad_left &&
           left.pad_right == right.pad_right &&
           left.pad_top == right.pad_top &&
           left.pad_bottom == right.pad_bottom;
}

bool frame_equal(const preprocess::PreprocessedFrame& left,
                 const preprocess::PreprocessedFrame& right) {
    return tensor_info_equal(left.tensor.info, right.tensor.info) &&
           left.tensor.data == right.tensor.data &&
           transform_equal(left.transform, right.transform);
}

void expect_float(TestContext& context,
                  const std::string& case_name,
                  float actual,
                  float expected) {
    context.expect(std::abs(actual - expected) <= kFloatTolerance,
                   case_name,
                   "unexpected float value");
}

void expect_vector(TestContext& context,
                   const std::string& case_name,
                   const std::vector<float>& actual,
                   const std::vector<float>& expected) {
    context.expect(actual.size() == expected.size(),
                   case_name,
                   "unexpected tensor data size");
    if (actual.size() != expected.size()) {
        return;
    }
    for (std::size_t index = 0; index < expected.size(); ++index) {
        expect_float(context, case_name, actual[index], expected[index]);
    }
}

void expect_valid_frame(TestContext& context,
                        const std::string& case_name,
                        const preprocess::PreprocessedFrame& frame,
                        const core::TensorInfo& expected_info) {
    const core::Status validation_status =
        core::validate_host_tensor(frame.tensor);
    context.expect(validation_status.ok(),
                   case_name,
                   validation_status.message());
    context.expect(tensor_info_equal(frame.tensor.info, expected_info),
                   case_name,
                   "output TensorInfo does not match the model input");

    std::size_t expected_count = 0;
    const core::Status count_status =
        core::checked_element_count(expected_info.shape, expected_count);
    context.expect(count_status.ok(), case_name, count_status.message());
    context.expect(frame.tensor.data.size() == expected_count,
                   case_name,
                   "output data size does not match the shape");
    for (float value : frame.tensor.data) {
        context.expect(std::isfinite(value),
                       case_name,
                       "tensor value must be finite");
        context.expect(value >= 0.0F && value <= 1.0F,
                       case_name,
                       "tensor value must be normalized to [0,1]");
    }
}

float tensor_value(const preprocess::PreprocessedFrame& frame,
                   int channel,
                   int row,
                   int column) {
    const std::size_t height =
        static_cast<std::size_t>(frame.tensor.info.shape[2]);
    const std::size_t width =
        static_cast<std::size_t>(frame.tensor.info.shape[3]);
    const std::size_t index = static_cast<std::size_t>(channel) * height * width +
                              static_cast<std::size_t>(row) * width +
                              static_cast<std::size_t>(column);
    return frame.tensor.data[index];
}

void expect_preprocess_failure(TestContext& context,
                               const std::string& case_name,
                               const core::Status& status,
                               core::ErrorCode expected_code,
                               const std::string& message_fragment) {
    context.expect(!status.ok(), case_name, "preprocess must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(status.message().find(message_fragment) != std::string::npos,
                   case_name,
                   "diagnostic message does not identify the failure");
}

preprocess::PreprocessedFrame make_sentinel_frame() {
    return {
        {{core::TensorDataType::kFloat32,
          core::TensorLayout::kBcn,
          {1, 2, 2}},
         {0.25F, 0.5F, 0.75F, 1.0F}},
        {11, 12, 13, 14, 15, 16, 17.0, 18, 19, 20, 21},
    };
}

void expect_atomic_failure(TestContext& context,
                           const std::string& case_name,
                           const preprocess::Preprocessor& preprocessor,
                           const cv::Mat& input,
                           const core::TensorInfo& input_info,
                           core::ErrorCode expected_code,
                           const std::string& message_fragment) {
    preprocess::PreprocessedFrame output = make_sentinel_frame();
    const preprocess::PreprocessedFrame expected = output;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    expect_preprocess_failure(
        context, case_name, status, expected_code, message_fragment);
    context.expect(frame_equal(output, expected),
                   case_name,
                   "failed preprocess must preserve the complete output");
}

void test_single_pixel_colors(TestContext& context) {
    struct ColorCase {
        const char* name;
        cv::Vec3b bgr;
        std::vector<float> expected;
    };
    const std::vector<ColorCase> cases{
        {"single red", cv::Vec3b(0, 0, 255), {1.0F, 0.0F, 0.0F}},
        {"single green", cv::Vec3b(0, 255, 0), {0.0F, 1.0F, 0.0F}},
        {"single blue", cv::Vec3b(255, 0, 0), {0.0F, 0.0F, 1.0F}},
        {"single gray 114",
         cv::Vec3b(114, 114, 114),
         {114.0F / 255.0F, 114.0F / 255.0F, 114.0F / 255.0F}},
    };

    const preprocess::Preprocessor preprocessor;
    const core::TensorInfo input_info = make_model_input_info(1, 1);
    for (const ColorCase& color_case : cases) {
        cv::Mat input(1,
                      1,
                      CV_8UC3,
                      cv::Scalar(color_case.bgr[0],
                                 color_case.bgr[1],
                                 color_case.bgr[2]));
        preprocess::PreprocessedFrame output;
        const core::Status status =
            preprocessor.preprocess(input, input_info, &output);
        context.expect(status.ok(), color_case.name, status.message());
        if (!status.ok()) {
            continue;
        }
        expect_valid_frame(context, color_case.name, output, input_info);
        expect_vector(
            context, color_case.name, output.tensor.data, color_case.expected);
        context.expect(output.transform.pad_left == 0 &&
                           output.transform.pad_right == 0 &&
                           output.transform.pad_top == 0 &&
                           output.transform.pad_bottom == 0,
                       color_case.name,
                       "single-pixel transform must not add padding");
    }
}

void test_chw_indexing(TestContext& context) {
    cv::Mat input(2, 2, CV_8UC3);
    input.at<cv::Vec3b>(0, 0) = cv::Vec3b(0, 0, 255);
    input.at<cv::Vec3b>(0, 1) = cv::Vec3b(0, 255, 0);
    input.at<cv::Vec3b>(1, 0) = cv::Vec3b(255, 0, 0);
    input.at<cv::Vec3b>(1, 1) = cv::Vec3b(255, 255, 255);
    const std::vector<float> expected{
        1.0F, 0.0F, 0.0F, 1.0F,
        0.0F, 1.0F, 0.0F, 1.0F,
        0.0F, 0.0F, 1.0F, 1.0F,
    };

    const preprocess::Preprocessor preprocessor;
    const core::TensorInfo input_info = make_model_input_info(2, 2);
    preprocess::PreprocessedFrame output;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "2x2 CHW indexing", status.message());
    if (!status.ok()) {
        return;
    }
    expect_valid_frame(context, "2x2 CHW indexing", output, input_info);
    expect_vector(context, "2x2 CHW indexing", output.tensor.data, expected);
    context.expect(output.transform.resized_width == 2 &&
                       output.transform.resized_height == 2,
                   "2x2 CHW indexing",
                   "no-transform geometry must preserve dimensions");
}

void test_normalization_inner_values(TestContext& context) {
    cv::Mat input(1, 1, CV_8UC3, cv::Scalar(1, 254, 0));
    const core::TensorInfo input_info = make_model_input_info(1, 1);
    preprocess::PreprocessedFrame output;
    const preprocess::Preprocessor preprocessor;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "normalization inner values", status.message());
    if (!status.ok()) {
        return;
    }
    expect_valid_frame(context, "normalization inner values", output, input_info);
    expect_vector(context,
                  "normalization inner values",
                  output.tensor.data,
                  {0.0F, 254.0F / 255.0F, 1.0F / 255.0F});
}

void test_vertical_padding(TestContext& context) {
    const cv::Vec3b color(10, 20, 30);
    cv::Mat input(2, 4, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    const cv::Mat original = input.clone();
    const unsigned char* const input_data = input.data;
    const core::TensorInfo input_info = make_model_input_info(4, 4);
    preprocess::PreprocessedFrame output;
    const preprocess::Preprocessor preprocessor;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "vertical padding", status.message());
    if (!status.ok()) {
        return;
    }

    expect_valid_frame(context, "vertical padding", output, input_info);
    context.expect(output.transform.pad_top == 1 &&
                       output.transform.pad_bottom == 1 &&
                       output.transform.pad_left == 0 &&
                       output.transform.pad_right == 0,
                   "vertical padding",
                   "unexpected vertical padding geometry");
    for (int channel = 0; channel < 3; ++channel) {
        expect_float(context,
                     "vertical padding",
                     tensor_value(output, channel, 0, 0),
                     114.0F / 255.0F);
        expect_float(context,
                     "vertical padding",
                     tensor_value(output, channel, 3, 3),
                     114.0F / 255.0F);
    }
    expect_float(context,
                 "vertical padding",
                 tensor_value(output, 0, 1, 0),
                 30.0F / 255.0F);
    expect_float(context,
                 "vertical padding",
                 tensor_value(output, 1, 2, 3),
                 20.0F / 255.0F);
    expect_float(context,
                 "vertical padding",
                 tensor_value(output, 2, 1, 3),
                 10.0F / 255.0F);
    context.expect(input.data == input_data && input.rows == original.rows &&
                       input.cols == original.cols &&
                       input.type() == original.type() &&
                       cv::norm(input, original, cv::NORM_INF) == 0.0,
                   "vertical padding",
                   "preprocess must not modify its input image");
}

void test_odd_horizontal_padding(TestContext& context) {
    const cv::Vec3b color(12, 34, 56);
    cv::Mat input(4, 2, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    const core::TensorInfo input_info = make_model_input_info(5, 5);
    preprocess::PreprocessedFrame output;
    const preprocess::Preprocessor preprocessor;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "odd horizontal padding", status.message());
    if (!status.ok()) {
        return;
    }

    expect_valid_frame(context, "odd horizontal padding", output, input_info);
    context.expect(output.transform.resized_width == 2 &&
                       output.transform.resized_height == 5 &&
                       output.transform.pad_left == 1 &&
                       output.transform.pad_right == 2,
                   "odd horizontal padding",
                   "unexpected odd horizontal padding geometry");
    expect_float(context,
                 "odd horizontal padding",
                 tensor_value(output, 0, 2, 0),
                 114.0F / 255.0F);
    expect_float(context,
                 "odd horizontal padding",
                 tensor_value(output, 0, 2, 1),
                 56.0F / 255.0F);
    expect_float(context,
                 "odd horizontal padding",
                 tensor_value(output, 1, 2, 2),
                 34.0F / 255.0F);
    expect_float(context,
                 "odd horizontal padding",
                 tensor_value(output, 2, 2, 3),
                 114.0F / 255.0F);
    expect_float(context,
                 "odd horizontal padding",
                 tensor_value(output, 2, 2, 4),
                 114.0F / 255.0F);
}

void test_uniform_resize(TestContext& context) {
    const cv::Vec3b color(13, 79, 211);
    cv::Mat input(2, 2, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    const core::TensorInfo input_info = make_model_input_info(4, 4);
    preprocess::PreprocessedFrame output;
    const preprocess::Preprocessor preprocessor;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "uniform resize", status.message());
    if (!status.ok()) {
        return;
    }

    expect_valid_frame(context, "uniform resize", output, input_info);
    context.expect(output.transform.resized_width == 4 &&
                       output.transform.resized_height == 4 &&
                       output.transform.pad_left == 0 &&
                       output.transform.pad_right == 0 &&
                       output.transform.pad_top == 0 &&
                       output.transform.pad_bottom == 0,
                   "uniform resize",
                   "uniform resize must fill the target without padding");
    for (int row = 0; row < 4; ++row) {
        for (int column = 0; column < 4; ++column) {
            expect_float(context,
                         "uniform resize",
                         tensor_value(output, 0, row, column),
                         211.0F / 255.0F);
            expect_float(context,
                         "uniform resize",
                         tensor_value(output, 1, row, column),
                         79.0F / 255.0F);
            expect_float(context,
                         "uniform resize",
                         tensor_value(output, 2, row, column),
                         13.0F / 255.0F);
        }
    }
}

void test_non_contiguous_input(TestContext& context) {
    cv::Mat storage(3, 5, CV_8UC3, cv::Scalar(91, 92, 93));
    cv::Mat input = storage(cv::Rect(1, 0, 2, 2));
    context.expect(!input.isContinuous(),
                   "non-contiguous input",
                   "ROI must exercise a non-contiguous Mat");
    input.at<cv::Vec3b>(0, 0) = cv::Vec3b(0, 0, 255);
    input.at<cv::Vec3b>(0, 1) = cv::Vec3b(0, 255, 0);
    input.at<cv::Vec3b>(1, 0) = cv::Vec3b(255, 0, 0);
    input.at<cv::Vec3b>(1, 1) = cv::Vec3b(1, 254, 255);

    const core::TensorInfo input_info = make_model_input_info(2, 2);
    preprocess::PreprocessedFrame output;
    const preprocess::Preprocessor preprocessor;
    const core::Status status =
        preprocessor.preprocess(input, input_info, &output);
    context.expect(status.ok(), "non-contiguous input", status.message());
    if (!status.ok()) {
        return;
    }
    expect_valid_frame(context, "non-contiguous input", output, input_info);
    expect_vector(context,
                  "non-contiguous input",
                  output.tensor.data,
                  {1.0F, 0.0F, 0.0F, 1.0F,
                   0.0F, 1.0F, 0.0F, 254.0F / 255.0F,
                   0.0F, 0.0F, 1.0F, 1.0F / 255.0F});
}

void test_buffer_reuse(TestContext& context) {
    const preprocess::Preprocessor preprocessor;
    const core::TensorInfo input_info = make_model_input_info(2, 2);
    preprocess::PreprocessedFrame output;
    cv::Mat first_input(2, 2, CV_8UC3, cv::Scalar(0, 0, 255));
    const core::Status first_status =
        preprocessor.preprocess(first_input, input_info, &output);
    context.expect(first_status.ok(), "buffer reuse first call", first_status.message());
    if (!first_status.ok()) {
        return;
    }
    const std::size_t first_size = output.tensor.data.size();
    const std::size_t first_capacity = output.tensor.data.capacity();
    const float* const first_pointer = output.tensor.data.data();

    cv::Mat second_input(1, 2, CV_8UC3, cv::Scalar(255, 0, 0));
    const core::Status second_status =
        preprocessor.preprocess(second_input, input_info, &output);
    context.expect(second_status.ok(),
                   "buffer reuse second call",
                   second_status.message());
    if (!second_status.ok()) {
        return;
    }

    expect_valid_frame(context, "buffer reuse second call", output, input_info);
    context.expect(output.tensor.data.size() == first_size,
                   "buffer reuse",
                   "same target must keep the same data size");
    context.expect(output.tensor.data.capacity() >= first_capacity,
                   "buffer reuse",
                   "buffer capacity must not decrease");
    context.expect(output.tensor.data.data() == first_pointer,
                   "buffer reuse",
                   "same target must reuse the existing allocation");
    context.expect(output.transform.original_width == 2 &&
                       output.transform.original_height == 1 &&
                       output.transform.pad_top == 0 &&
                       output.transform.pad_bottom == 1,
                   "buffer reuse",
                   "second call must update transform metadata");
    expect_float(context,
                 "buffer reuse",
                 tensor_value(output, 2, 0, 0),
                 1.0F);
    expect_float(context,
                 "buffer reuse",
                 tensor_value(output, 0, 0, 0),
                 0.0F);
    expect_float(context,
                 "buffer reuse",
                 tensor_value(output, 0, 1, 0),
                 114.0F / 255.0F);
}

void test_failures_and_atomicity(TestContext& context) {
    const preprocess::Preprocessor preprocessor;
    const core::TensorInfo valid_info = make_model_input_info(2, 2);
    const cv::Mat valid_input(2, 2, CV_8UC3, cv::Scalar(1, 2, 3));

    const core::Status null_output_status =
        preprocessor.preprocess(valid_input, valid_info, nullptr);
    expect_preprocess_failure(context,
                              "null output",
                              null_output_status,
                              core::ErrorCode::kInvalidArgument,
                              "output");

    expect_atomic_failure(context,
                          "empty input",
                          preprocessor,
                          cv::Mat(),
                          valid_info,
                          core::ErrorCode::kInvalidArgument,
                          "input_bgr");
    expect_atomic_failure(context,
                          "CV_8UC1 input",
                          preprocessor,
                          cv::Mat(2, 2, CV_8UC1, cv::Scalar(1)),
                          valid_info,
                          core::ErrorCode::kInvalidArgument,
                          "CV_8UC3");
    expect_atomic_failure(context,
                          "CV_8UC4 input",
                          preprocessor,
                          cv::Mat(2, 2, CV_8UC4, cv::Scalar(1, 2, 3, 4)),
                          valid_info,
                          core::ErrorCode::kInvalidArgument,
                          "CV_8UC3");
    expect_atomic_failure(context,
                          "CV_32FC3 input",
                          preprocessor,
                          cv::Mat(2, 2, CV_32FC3, cv::Scalar(1.0, 2.0, 3.0)),
                          valid_info,
                          core::ErrorCode::kInvalidArgument,
                          "CV_8UC3");

    core::TensorInfo invalid_info = valid_info;
    invalid_info.dtype = static_cast<core::TensorDataType>(99);
    expect_atomic_failure(context,
                          "invalid dtype enum",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kUnsupportedDataType,
                          "dtype");
    invalid_info = valid_info;
    invalid_info.dtype = static_cast<core::TensorDataType>(1);
    expect_atomic_failure(context,
                          "non-float32 dtype",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kUnsupportedDataType,
                          "dtype");
    invalid_info = valid_info;
    invalid_info.layout = core::TensorLayout::kBcn;
    expect_atomic_failure(context,
                          "BCN layout",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kUnsupportedLayout,
                          "layout");
    invalid_info = valid_info;
    invalid_info.layout = static_cast<core::TensorLayout>(99);
    expect_atomic_failure(context,
                          "invalid layout enum",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kUnsupportedLayout,
                          "layout");
    invalid_info = valid_info;
    invalid_info.shape = {1, 3, 2};
    expect_atomic_failure(context,
                          "invalid rank",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "rank 4");
    invalid_info = valid_info;
    invalid_info.shape[0] = 2;
    expect_atomic_failure(context,
                          "invalid batch",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "batch");
    invalid_info = valid_info;
    invalid_info.shape[1] = 1;
    expect_atomic_failure(context,
                          "invalid channel",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "channel");
    invalid_info = valid_info;
    invalid_info.shape[2] = 0;
    expect_atomic_failure(context,
                          "zero target height",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "positive");
    invalid_info = valid_info;
    invalid_info.shape[3] = -1;
    expect_atomic_failure(context,
                          "negative target width",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "positive");
    invalid_info = valid_info;
    invalid_info.shape[2] = std::numeric_limits<std::int64_t>::max();
    invalid_info.shape[3] = std::numeric_limits<std::int64_t>::max();
    expect_atomic_failure(context,
                          "element count overflow",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kOverflow,
                          "overflows");
    invalid_info = valid_info;
    invalid_info.shape[2] =
        static_cast<std::int64_t>(std::numeric_limits<int>::max()) + 1;
    invalid_info.shape[3] = 1;
    expect_atomic_failure(context,
                          "target exceeds int range",
                          preprocessor,
                          valid_input,
                          invalid_info,
                          core::ErrorCode::kInvalidShape,
                          "fit in int");
}

}  // namespace

int main() {
    TestContext context;
    test_single_pixel_colors(context);
    test_chw_indexing(context);
    test_normalization_inner_values(context);
    test_vertical_padding(context);
    test_odd_horizontal_padding(context);
    test_uniform_resize(context);
    test_non_contiguous_input(context);
    test_buffer_reuse(context);
    test_failures_and_atomicity(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " CPU preprocessor test(s) failed\n";
        return 1;
    }

    std::cout << "All CPU preprocessor tests passed\n";
    return 0;
}
