#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <opencv2/core.hpp>

#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>

namespace {

namespace core = edge_ai_defect::core;
namespace preprocess = edge_ai_defect::preprocess;

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

core::TensorInfo make_model_input_info(std::int64_t height = 640,
                                       std::int64_t width = 640) {
    return {
        core::TensorDataType::kFloat32,
        core::TensorLayout::kNchw,
        {1, 3, height, width},
    };
}

bool metadata_equal(const preprocess::ImageTransformMetadata& left,
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

void expect_failure(TestContext& context,
                    const std::string& case_name,
                    const core::Status& status,
                    core::ErrorCode expected_code) {
    context.expect(!status.ok(), case_name, "operation must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(!status.message().empty(),
                   case_name,
                   "failure must contain a diagnostic message");
}

void expect_geometry(TestContext& context,
                     const std::string& case_name,
                     int original_width,
                     int original_height,
                     const core::TensorInfo& model_input_info,
                     const preprocess::ImageTransformMetadata& expected) {
    preprocess::ImageTransformMetadata actual;
    const core::Status status = preprocess::compute_letterbox_geometry(
        original_width, original_height, model_input_info, &actual);
    context.expect(status.ok(), case_name, status.message());
    if (!status.ok()) {
        return;
    }

    context.expect(actual.original_width == expected.original_width,
                   case_name,
                   "unexpected original width");
    context.expect(actual.original_height == expected.original_height,
                   case_name,
                   "unexpected original height");
    context.expect(actual.target_width == expected.target_width,
                   case_name,
                   "unexpected target width");
    context.expect(actual.target_height == expected.target_height,
                   case_name,
                   "unexpected target height");
    context.expect(actual.resized_width == expected.resized_width,
                   case_name,
                   "unexpected resized width");
    context.expect(actual.resized_height == expected.resized_height,
                   case_name,
                   "unexpected resized height");
    context.expect(std::abs(actual.gain - expected.gain) <= 1.0e-12,
                   case_name,
                   "unexpected gain");
    context.expect(actual.pad_left == expected.pad_left,
                   case_name,
                   "unexpected left padding");
    context.expect(actual.pad_right == expected.pad_right,
                   case_name,
                   "unexpected right padding");
    context.expect(actual.pad_top == expected.pad_top,
                   case_name,
                   "unexpected top padding");
    context.expect(actual.pad_bottom == expected.pad_bottom,
                   case_name,
                   "unexpected bottom padding");
    context.expect(actual.resized_width + actual.pad_left + actual.pad_right ==
                       actual.target_width,
                   case_name,
                   "horizontal dimensions must sum to the target width");
    context.expect(actual.resized_height + actual.pad_top +
                           actual.pad_bottom ==
                       actual.target_height,
                   case_name,
                   "vertical dimensions must sum to the target height");
}

void test_geometry(TestContext& context) {
    const core::TensorInfo square = make_model_input_info();
    expect_geometry(context,
                    "square resize",
                    200,
                    200,
                    square,
                    {200, 200, 640, 640, 640, 640, 3.2, 0, 0, 0, 0});
    expect_geometry(context,
                    "landscape vertical padding",
                    640,
                    360,
                    square,
                    {640, 360, 640, 640, 640, 360, 1.0, 0, 0, 140, 140});
    expect_geometry(context,
                    "portrait horizontal padding",
                    360,
                    640,
                    square,
                    {360, 640, 640, 640, 360, 640, 1.0, 140, 140, 0, 0});
    expect_geometry(context,
                    "odd vertical padding",
                    641,
                    480,
                    square,
                    {641,
                     480,
                     640,
                     640,
                     640,
                     479,
                     640.0 / 641.0,
                     0,
                     0,
                     80,
                     81});
    expect_geometry(context,
                    "odd horizontal padding",
                    480,
                    641,
                    square,
                    {480,
                     641,
                     640,
                     640,
                     479,
                     640,
                     640.0 / 641.0,
                     80,
                     81,
                     0,
                     0});
    expect_geometry(context,
                    "small portrait input",
                    37,
                    53,
                    square,
                    {37,
                     53,
                     640,
                     640,
                     447,
                     640,
                     640.0 / 53.0,
                     96,
                     97,
                     0,
                     0});
    expect_geometry(context,
                    "ties-to-even 1.5",
                    2,
                    4,
                    make_model_input_info(3, 3),
                    {2, 4, 3, 3, 2, 3, 0.75, 0, 1, 0, 0});
    expect_geometry(context,
                    "ties-to-even 2.5",
                    2,
                    4,
                    make_model_input_info(5, 5),
                    {2, 4, 5, 5, 2, 5, 1.25, 1, 2, 0, 0});
    expect_geometry(context,
                    "round_half_even_3_5",
                    2,
                    4,
                    make_model_input_info(7, 7),
                    {2, 4, 7, 7, 4, 7, 1.75, 1, 2, 0, 0});
    expect_geometry(context,
                    "round_half_even_4_5",
                    2,
                    4,
                    make_model_input_info(9, 9),
                    {2, 4, 9, 9, 4, 9, 2.25, 2, 3, 0, 0});
    expect_geometry(context,
                    "round_below_half",
                    3,
                    2000000000,
                    make_model_input_info(1666666666, 4),
                    {3,
                     2000000000,
                     4,
                     1666666666,
                     2,
                     1666666666,
                     0.833333333,
                     1,
                     1,
                     0,
                     0});
    expect_geometry(context,
                    "round_above_half",
                    3,
                    2000000000,
                    make_model_input_info(1666666667, 4),
                    {3,
                     2000000000,
                     4,
                     1666666667,
                     3,
                     1666666667,
                     0.8333333335,
                     0,
                     1,
                     0,
                     0});
}

void test_geometry_failures(TestContext& context) {
    const core::TensorInfo valid = make_model_input_info();
    expect_failure(context,
                   "null geometry metadata",
                   preprocess::compute_letterbox_geometry(
                       640, 480, valid, nullptr),
                   core::ErrorCode::kInvalidArgument);

    preprocess::ImageTransformMetadata metadata;
    expect_failure(context,
                   "zero original width",
                   preprocess::compute_letterbox_geometry(
                       0, 480, valid, &metadata),
                   core::ErrorCode::kInvalidArgument);
    expect_failure(context,
                   "zero original height",
                   preprocess::compute_letterbox_geometry(
                       640, 0, valid, &metadata),
                   core::ErrorCode::kInvalidArgument);
    expect_failure(context,
                   "negative original width",
                   preprocess::compute_letterbox_geometry(
                       -1, 480, valid, &metadata),
                   core::ErrorCode::kInvalidArgument);

    core::TensorInfo invalid = valid;
    invalid.shape.clear();
    expect_failure(context,
                   "empty model shape",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape = {1, 3, 640};
    expect_failure(context,
                   "model rank is not four",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.dtype = static_cast<core::TensorDataType>(99);
    expect_failure(context,
                   "unsupported input dtype",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kUnsupportedDataType);
    invalid = valid;
    invalid.layout = core::TensorLayout::kBcn;
    expect_failure(context,
                   "input layout is not NCHW",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kUnsupportedLayout);
    invalid = valid;
    invalid.shape[0] = 2;
    expect_failure(context,
                   "input batch is not one",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape[1] = 1;
    expect_failure(context,
                   "input channels are not three",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape[2] = 0;
    expect_failure(context,
                   "zero target height",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape[3] = -1;
    expect_failure(context,
                   "negative target width",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape[2] =
        static_cast<std::int64_t>(std::numeric_limits<int>::max()) + 1;
    invalid.shape[3] = 1;
    expect_failure(context,
                   "target height exceeds int",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
    invalid = valid;
    invalid.shape[2] = 1;
    invalid.shape[3] =
        static_cast<std::int64_t>(std::numeric_limits<int>::max()) + 1;
    expect_failure(context,
                   "target width exceeds int",
                   preprocess::compute_letterbox_geometry(
                       640, 480, invalid, &metadata),
                   core::ErrorCode::kInvalidShape);
}

bool all_pixels_equal(const cv::Mat& image, const cv::Vec3b& expected) {
    for (int row = 0; row < image.rows; ++row) {
        for (int column = 0; column < image.cols; ++column) {
            if (image.at<cv::Vec3b>(row, column) != expected) {
                return false;
            }
        }
    }
    return true;
}

void test_uniform_resize(TestContext& context) {
    const cv::Vec3b color(17, 83, 201);
    cv::Mat input(200, 200, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    const cv::Mat original = input.clone();
    const unsigned char* const input_data = input.data;
    cv::Mat output;
    preprocess::ImageTransformMetadata metadata;

    const core::Status status = preprocess::letterbox_bgr(
        input, make_model_input_info(), &output, &metadata);
    context.expect(status.ok(), "uniform resize", status.message());
    context.expect(output.rows == 640 && output.cols == 640,
                   "uniform resize",
                   "output size must be 640x640");
    context.expect(output.type() == CV_8UC3,
                   "uniform resize",
                   "output type must remain CV_8UC3");
    context.expect(all_pixels_equal(output, color),
                   "uniform resize",
                   "uniform BGR color must be preserved exactly");
    context.expect(input.data == input_data && cv::norm(input, original) == 0.0,
                   "uniform resize",
                   "input image must remain unchanged");
    context.expect(output.data != input.data,
                   "uniform resize",
                   "output must own independent image data");
}

void test_vertical_padding(TestContext& context) {
    const cv::Vec3b color(3, 40, 250);
    const cv::Vec3b padding(114, 114, 114);
    cv::Mat input(360, 640, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    cv::Mat output;
    preprocess::ImageTransformMetadata metadata;
    const core::Status status = preprocess::letterbox_bgr(
        input, make_model_input_info(), &output, &metadata);

    context.expect(status.ok(), "vertical padding image", status.message());
    context.expect(metadata.pad_top == 140 && metadata.pad_bottom == 140,
                   "vertical padding image",
                   "vertical padding must be 140 pixels per side");
    context.expect(output.at<cv::Vec3b>(0, 0) == padding &&
                       output.at<cv::Vec3b>(139, 639) == padding &&
                       output.at<cv::Vec3b>(500, 0) == padding &&
                       output.at<cv::Vec3b>(639, 639) == padding,
                   "vertical padding image",
                   "padding pixels must be BGR 114");
    context.expect(output.at<cv::Vec3b>(140, 0) == color &&
                       output.at<cv::Vec3b>(499, 639) == color,
                   "vertical padding image",
                   "content pixels must remain unchanged");
}

void test_odd_horizontal_padding(TestContext& context) {
    const cv::Vec3b color(220, 31, 9);
    const cv::Vec3b padding(114, 114, 114);
    cv::Mat input(641, 480, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    cv::Mat output;
    preprocess::ImageTransformMetadata metadata;
    const core::Status status = preprocess::letterbox_bgr(
        input, make_model_input_info(), &output, &metadata);

    context.expect(status.ok(), "odd horizontal padding image", status.message());
    context.expect(metadata.resized_width == 479 && metadata.pad_left == 80 &&
                       metadata.pad_right == 81,
                   "odd horizontal padding image",
                   "horizontal split must preserve the odd padding pixel");
    context.expect(output.at<cv::Vec3b>(0, 0) == padding &&
                       output.at<cv::Vec3b>(639, 79) == padding &&
                       output.at<cv::Vec3b>(0, 559) == padding &&
                       output.at<cv::Vec3b>(639, 639) == padding,
                   "odd horizontal padding image",
                   "left and right padding must be BGR 114");
    context.expect(output.at<cv::Vec3b>(0, 80) == color &&
                       output.at<cv::Vec3b>(639, 558) == color,
                   "odd horizontal padding image",
                   "resized content must occupy the expected interval");
}

void test_independent_copy_without_transform(TestContext& context) {
    const cv::Vec3b color(7, 19, 73);
    cv::Mat input(4, 5, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    const unsigned char* const input_data = input.data;
    cv::Mat output;
    preprocess::ImageTransformMetadata metadata;
    const core::Status status = preprocess::letterbox_bgr(
        input, make_model_input_info(4, 5), &output, &metadata);

    context.expect(status.ok(), "independent no-op copy", status.message());
    context.expect(output.rows == input.rows && output.cols == input.cols,
                   "independent no-op copy",
                   "output dimensions must match the input");
    context.expect(output.data != input_data,
                   "independent no-op copy",
                   "no-op transform must still clone input data");
    context.expect(cv::norm(output, input) == 0.0,
                   "independent no-op copy",
                   "no-op transform must preserve every pixel");
}

void test_alias_safety(TestContext& context) {
    const cv::Vec3b color(90, 45, 12);
    const cv::Vec3b padding(114, 114, 114);
    cv::Mat image(360, 640, CV_8UC3, cv::Scalar(color[0], color[1], color[2]));
    preprocess::ImageTransformMetadata metadata;
    const core::Status status = preprocess::letterbox_bgr(
        image, make_model_input_info(), &image, &metadata);

    context.expect(status.ok(), "input output alias", status.message());
    context.expect(image.rows == 640 && image.cols == 640,
                   "input output alias",
                   "aliased output must have the target dimensions");
    context.expect(image.at<cv::Vec3b>(0, 0) == padding &&
                       image.at<cv::Vec3b>(140, 0) == color &&
                       image.at<cv::Vec3b>(499, 639) == color,
                   "input output alias",
                   "aliased transform must preserve content and padding");
}

void test_image_failures_and_atomicity(TestContext& context) {
    const core::TensorInfo valid = make_model_input_info();
    const cv::Mat valid_input(8, 8, CV_8UC3, cv::Scalar(1, 2, 3));
    cv::Mat output;
    preprocess::ImageTransformMetadata metadata;

    expect_failure(context,
                   "null image output",
                   preprocess::letterbox_bgr(
                       valid_input, valid, nullptr, &metadata),
                   core::ErrorCode::kInvalidArgument);
    expect_failure(context,
                   "null image metadata",
                   preprocess::letterbox_bgr(
                       valid_input, valid, &output, nullptr),
                   core::ErrorCode::kInvalidArgument);
    expect_failure(context,
                   "empty input image",
                   preprocess::letterbox_bgr(
                       cv::Mat(), valid, &output, &metadata),
                   core::ErrorCode::kInvalidArgument);

    const cv::Mat one_channel(8, 8, CV_8UC1, cv::Scalar(1));
    expect_failure(context,
                   "one-channel input image",
                   preprocess::letterbox_bgr(
                       one_channel, valid, &output, &metadata),
                   core::ErrorCode::kInvalidArgument);
    const cv::Mat four_channels(8, 8, CV_8UC4, cv::Scalar(1, 2, 3, 4));
    expect_failure(context,
                   "four-channel input image",
                   preprocess::letterbox_bgr(
                       four_channels, valid, &output, &metadata),
                   core::ErrorCode::kInvalidArgument);
    const cv::Mat float_image(8, 8, CV_32FC3, cv::Scalar(1.0, 2.0, 3.0));
    expect_failure(context,
                   "float input image",
                   preprocess::letterbox_bgr(
                       float_image, valid, &output, &metadata),
                   core::ErrorCode::kInvalidArgument);

    const preprocess::ImageTransformMetadata sentinel_metadata{
        11, 12, 13, 14, 15, 16, 17.0, 18, 19, 20, 21};
    const cv::Vec3b sentinel_color(31, 41, 59);
    cv::Mat sentinel_output(
        2,
        3,
        CV_8UC3,
        cv::Scalar(sentinel_color[0], sentinel_color[1], sentinel_color[2]));
    const cv::Mat sentinel_copy = sentinel_output.clone();
    const unsigned char* const sentinel_data = sentinel_output.data;
    metadata = sentinel_metadata;
    const core::Status invalid_image_status = preprocess::letterbox_bgr(
        one_channel, valid, &sentinel_output, &metadata);
    expect_failure(context,
                   "invalid image preserves outputs",
                   invalid_image_status,
                   core::ErrorCode::kInvalidArgument);
    context.expect(sentinel_output.data == sentinel_data &&
                       cv::norm(sentinel_output, sentinel_copy) == 0.0,
                   "invalid image preserves outputs",
                   "output image must remain unchanged on failure");
    context.expect(metadata_equal(metadata, sentinel_metadata),
                   "invalid image preserves outputs",
                   "metadata must remain unchanged on failure");

    core::TensorInfo invalid_info = valid;
    invalid_info.layout = core::TensorLayout::kBcn;
    const core::Status invalid_tensor_status = preprocess::letterbox_bgr(
        valid_input, invalid_info, &sentinel_output, &metadata);
    expect_failure(context,
                   "invalid TensorInfo preserves outputs",
                   invalid_tensor_status,
                   core::ErrorCode::kUnsupportedLayout);
    context.expect(sentinel_output.data == sentinel_data &&
                       cv::norm(sentinel_output, sentinel_copy) == 0.0,
                   "invalid TensorInfo preserves outputs",
                   "output image must remain unchanged on failure");
    context.expect(metadata_equal(metadata, sentinel_metadata),
                   "invalid TensorInfo preserves outputs",
                   "metadata must remain unchanged on failure");

    preprocess::ImageTransformMetadata geometry_metadata = sentinel_metadata;
    const core::Status invalid_geometry_status =
        preprocess::compute_letterbox_geometry(
            0, 8, valid, &geometry_metadata);
    expect_failure(context,
                   "geometry failure preserves metadata",
                   invalid_geometry_status,
                   core::ErrorCode::kInvalidArgument);
    context.expect(metadata_equal(geometry_metadata, sentinel_metadata),
                   "geometry failure preserves metadata",
                   "geometry metadata must remain unchanged on failure");
}

}  // namespace

int main() {
    TestContext context;
    test_geometry(context);
    test_geometry_failures(context);
    test_uniform_resize(context);
    test_vertical_padding(context);
    test_odd_horizontal_padding(context);
    test_independent_copy_without_transform(context);
    test_alias_safety(context);
    test_image_failures_and_atomicity(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " LetterBox test(s) failed\n";
        return 1;
    }

    std::cout << "All LetterBox geometry and BGR image tests passed\n";
    return 0;
}
