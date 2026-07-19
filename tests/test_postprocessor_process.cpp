#include "edge_ai_defect/postprocess/postprocessor.hpp"

#include <array>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace postprocess = edge_ai_defect::postprocess;
namespace preprocess = edge_ai_defect::preprocess;

constexpr std::size_t kChannelCount = 10U;
constexpr std::size_t kCandidateCount = 8400U;
constexpr std::size_t kElementCount = kChannelCount * kCandidateCount;

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

core::HostTensor make_raw_output() {
    return {
        {core::TensorDataType::kFloat32,
         core::TensorLayout::kBcn,
         {1, 10, 8400}},
        std::vector<float>(kElementCount, 0.0F),
    };
}

void set_value(core::HostTensor& raw_output,
               std::size_t channel,
               std::size_t candidate_index,
               float value) {
    raw_output.data[channel * kCandidateCount + candidate_index] = value;
}

void set_candidate(core::HostTensor& raw_output,
                   std::size_t candidate_index,
                   float cx,
                   float cy,
                   float width,
                   float height,
                   int class_id,
                   float confidence) {
    set_value(raw_output, 0U, candidate_index, cx);
    set_value(raw_output, 1U, candidate_index, cy);
    set_value(raw_output, 2U, candidate_index, width);
    set_value(raw_output, 3U, candidate_index, height);
    set_value(raw_output,
              4U + static_cast<std::size_t>(class_id),
              candidate_index,
              confidence);
}

preprocess::ImageTransformMetadata make_transform(
    int original_width = 640,
    int original_height = 640,
    int resized_width = 640,
    int resized_height = 640,
    double gain = 1.0,
    int pad_left = 0,
    int pad_right = 0,
    int pad_top = 0,
    int pad_bottom = 0) {
    return {original_width,
            original_height,
            640,
            640,
            resized_width,
            resized_height,
            gain,
            pad_left,
            pad_right,
            pad_top,
            pad_bottom};
}

bool detections_equal(const std::vector<postprocess::Detection>& left,
                      const std::vector<postprocess::Detection>& right) {
    if (left.size() != right.size()) {
        return false;
    }
    for (std::size_t index = 0U; index < left.size(); ++index) {
        const postprocess::Detection& lhs = left[index];
        const postprocess::Detection& rhs = right[index];
        if (lhs.x1 != rhs.x1 || lhs.y1 != rhs.y1 || lhs.x2 != rhs.x2 ||
            lhs.y2 != rhs.y2 || lhs.confidence != rhs.confidence ||
            lhs.class_id != rhs.class_id ||
            lhs.candidate_index != rhs.candidate_index) {
            return false;
        }
    }
    return true;
}

void expect_near(TestContext& context,
                 const std::string& case_name,
                 float actual,
                 float expected) {
    context.expect(std::abs(actual - expected) <= 1.0e-5F,
                   case_name,
                   "unexpected coordinate");
}

void expect_success(TestContext& context,
                    const std::string& case_name,
                    const postprocess::PostProcessor& processor,
                    const core::HostTensor& raw_output,
                    const preprocess::ImageTransformMetadata& transform,
                    std::vector<postprocess::Detection>& output) {
    const core::Status status = processor.process(raw_output, transform, &output);
    context.expect(status.ok(), case_name, "process must succeed");
    context.expect(status.code() == core::ErrorCode::kOk,
                   case_name,
                   "success must return kOk");
}

void expect_failure_atomic(
    TestContext& context,
    const std::string& case_name,
    const postprocess::PostProcessor& processor,
    const core::HostTensor& raw_output,
    const preprocess::ImageTransformMetadata& transform,
    core::ErrorCode expected_code) {
    const std::vector<postprocess::Detection> expected_output{
        {1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 5, 73U}};
    std::vector<postprocess::Detection> output = expected_output;
    const core::Status status = processor.process(raw_output, transform, &output);
    context.expect(!status.ok(), case_name, "process must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(detections_equal(output, expected_output),
                   case_name,
                   "failure must preserve caller output");
}

void test_inverse_transform(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate(raw_output, 3U, 100.0F, 200.0F, 20.0F, 40.0F, 2, 0.9F);
    postprocess::PostProcessor processor;
    std::vector<postprocess::Detection> output;
    expect_success(context,
                   "identity inverse transform",
                   processor,
                   raw_output,
                   make_transform(),
                   output);
    context.expect(output.size() == 1U,
                   "identity inverse transform",
                   "one detection expected");
    if (output.size() == 1U) {
        expect_near(context, "identity inverse transform", output[0].x1, 90.0F);
        expect_near(context, "identity inverse transform", output[0].y1, 180.0F);
        expect_near(context, "identity inverse transform", output[0].x2, 110.0F);
        expect_near(context, "identity inverse transform", output[0].y2, 220.0F);
    }

    raw_output = make_raw_output();
    set_candidate(raw_output, 4U, 220.0F, 240.0F, 200.0F, 200.0F, 1, 0.9F);
    output.clear();
    const preprocess::ImageTransformMetadata padded =
        make_transform(320, 300, 640, 600, 2.0, 0, 0, 20, 20);
    expect_success(context,
                   "padded inverse transform",
                   processor,
                   raw_output,
                   padded,
                   output);
    context.expect(output.size() == 1U,
                   "padded inverse transform",
                   "one detection expected");
    if (output.size() == 1U) {
        expect_near(context, "padded inverse transform", output[0].x1, 60.0F);
        expect_near(context, "padded inverse transform", output[0].y1, 60.0F);
        expect_near(context, "padded inverse transform", output[0].x2, 160.0F);
        expect_near(context, "padded inverse transform", output[0].y2, 160.0F);
    }
}

void test_actual_odd_padding_metadata(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate(raw_output, 6U, 100.0F, 100.0F, 20.0F, 20.0F, 0, 0.9F);
    const preprocess::ImageTransformMetadata odd_padding = make_transform(
        480, 641, 479, 640, 640.0 / 641.0, 80, 81, 0, 0);
    postprocess::PostProcessor processor;
    std::vector<postprocess::Detection> output;
    expect_success(context,
                   "actual odd left padding",
                   processor,
                   raw_output,
                   odd_padding,
                   output);
    context.expect(output.size() == 1U,
                   "actual odd left padding",
                   "one detection expected");
    if (output.size() == 1U) {
        expect_near(context,
                    "actual odd left padding",
                    output[0].x1,
                    10.0F * 641.0F / 640.0F);
        expect_near(context,
                    "actual odd left padding",
                    output[0].x2,
                    30.0F * 641.0F / 640.0F);
    }
}

void test_clipping_and_degenerate_retention(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate(raw_output, 0U, -30.0F, 100.0F, 20.0F, 20.0F, 0, 0.95F);
    set_candidate(raw_output, 1U, 100.0F, -30.0F, 20.0F, 20.0F, 1, 0.90F);
    set_candidate(raw_output, 2U, 730.0F, 100.0F, 20.0F, 20.0F, 2, 0.85F);
    set_candidate(raw_output, 3U, 100.0F, 730.0F, 20.0F, 20.0F, 3, 0.80F);
    set_candidate(raw_output, 4U, 50.0F, 50.0F, 100.0F, 100.0F, 4, 0.75F);
    set_candidate(raw_output, 5U, 20.0F, 50.0F, 60.0F, 40.0F, 5, 0.70F);

    const preprocess::ImageTransformMetadata transform =
        make_transform(640, 640, 640, 640, 1.0);
    postprocess::PostProcessor processor;
    std::vector<postprocess::Detection> output;
    expect_success(context,
                   "continuous clipping and degeneracy retention",
                   processor,
                   raw_output,
                   transform,
                   output);
    context.expect(output.size() == 6U,
                   "continuous clipping and degeneracy retention",
                   "all cross-class candidates must remain");
    if (output.size() != 6U) {
        return;
    }
    context.expect(output[0].x1 == 0.0F && output[0].x2 == 0.0F,
                   "left degenerate retention",
                   "fully left box must remain at x equals zero");
    context.expect(output[1].y1 == 0.0F && output[1].y2 == 0.0F,
                   "top degenerate retention",
                   "fully top box must remain at y equals zero");
    context.expect(output[2].x1 == 640.0F && output[2].x2 == 640.0F,
                   "right degenerate retention",
                   "fully right box must remain at x equals width");
    context.expect(output[3].y1 == 640.0F && output[3].y2 == 640.0F,
                   "bottom degenerate retention",
                   "fully bottom box must remain at y equals height");
    expect_near(context, "partial clipping", output[4].x1, 0.0F);
    expect_near(context, "partial clipping", output[4].y1, 0.0F);
    expect_near(context, "partial clipping", output[4].x2, 100.0F);
    expect_near(context, "partial clipping", output[4].y2, 100.0F);
    expect_near(context, "inside clipping", output[5].x1, 0.0F);
    expect_near(context, "inside clipping", output[5].y1, 30.0F);
    expect_near(context, "inside clipping", output[5].x2, 50.0F);
    expect_near(context, "inside clipping", output[5].y2, 70.0F);
    constexpr std::array<float, 6U> kExpectedConfidences{
        0.95F, 0.90F, 0.85F, 0.80F, 0.75F, 0.70F};
    for (std::size_t index = 0U; index < output.size(); ++index) {
        context.expect(output[index].confidence == kExpectedConfidences[index] &&
                           output[index].class_id == static_cast<int>(index) &&
                           output[index].candidate_index == index,
                       "degenerate provenance and order",
                       "confidence, class, index, and NMS order must remain intact");
    }
}

void test_nms_before_transform_and_class_aware(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate(raw_output, 0U, 150.0F, 50.0F, 100.0F, 100.0F, 0, 0.9F);
    set_candidate(raw_output, 1U, 150.0F, 70.0F, 100.0F, 100.0F, 0, 0.8F);
    const preprocess::ImageTransformMetadata padded =
        make_transform(640, 360, 640, 360, 1.0, 0, 0, 140, 140);
    postprocess::PostProcessor processor;
    std::vector<postprocess::Detection> output;
    expect_success(context,
                   "NMS before transform",
                   processor,
                   raw_output,
                   padded,
                   output);
    context.expect(output.size() == 1U && output.front().candidate_index == 0U,
                   "NMS before transform",
                   "model-space overlap must suppress before clipping");

    raw_output = make_raw_output();
    set_candidate(raw_output, 2U, 200.0F, 200.0F, 40.0F, 40.0F, 0, 0.9F);
    set_candidate(raw_output, 3U, 200.0F, 200.0F, 40.0F, 40.0F, 1, 0.8F);
    output.clear();
    expect_success(context,
                   "class-aware public process",
                   processor,
                   raw_output,
                   make_transform(),
                   output);
    context.expect(output.size() == 2U && output[0].class_id == 0 &&
                       output[1].class_id == 1 && output[0].x1 == 180.0F &&
                       output[1].x1 == 180.0F,
                   "class-aware public process",
                   "class offset must not suppress or leak into detections");
}

void test_decode_and_nms_integration(TestContext& context) {
    postprocess::PostProcessor processor;
    core::HostTensor raw_output = make_raw_output();
    set_candidate(raw_output, 0U, 100.0F, 100.0F, 20.0F, 20.0F, 0, 0.25F);
    set_candidate(raw_output,
                  1U,
                  200.0F,
                  100.0F,
                  20.0F,
                  20.0F,
                  0,
                  std::nextafter(0.25F, std::numeric_limits<float>::infinity()));
    std::vector<postprocess::Detection> output;
    expect_success(context,
                   "strict public confidence threshold",
                   processor,
                   raw_output,
                   make_transform(),
                   output);
    context.expect(output.size() == 1U && output.front().candidate_index == 1U,
                   "strict public confidence threshold",
                   "only confidence strictly above 0.25 must remain");

    raw_output = make_raw_output();
    set_candidate(raw_output, 0U, 100.0F, 100.0F, 20.0F, 20.0F, 0, 0.9F);
    set_candidate(raw_output, 1U, 200.0F, 100.0F, 20.0F, 20.0F, 0, 0.8F);
    set_candidate(raw_output, 2U, 300.0F, 100.0F, 20.0F, 20.0F, 0, 0.7F);
    postprocess::PostprocessConfig max_nms_config;
    max_nms_config.max_nms = 2U;
    max_nms_config.max_det = 2U;
    output.clear();
    expect_success(context,
                   "max_nms public integration",
                   postprocess::PostProcessor(max_nms_config),
                   raw_output,
                   make_transform(),
                   output);
    context.expect(output.size() == 2U && output[0].candidate_index == 0U &&
                       output[1].candidate_index == 1U,
                   "max_nms public integration",
                   "decode max_nms must exclude later candidates");

    postprocess::PostprocessConfig max_det_config;
    max_det_config.max_nms = 3U;
    max_det_config.max_det = 1U;
    output.clear();
    expect_success(context,
                   "max_det public integration",
                   postprocess::PostProcessor(max_det_config),
                   raw_output,
                   make_transform(),
                   output);
    context.expect(output.size() == 1U && output.front().candidate_index == 0U,
                   "max_det public integration",
                   "NMS max_det must truncate accepted candidates");
}

void test_failures_and_empty_result(TestContext& context) {
    const postprocess::PostProcessor processor;
    const core::HostTensor valid_raw = make_raw_output();
    const preprocess::ImageTransformMetadata valid_transform = make_transform();

    const core::Status null_status = processor.process(valid_raw, valid_transform, nullptr);
    context.expect(!null_status.ok() &&
                       null_status.code() == core::ErrorCode::kInvalidArgument,
                   "null output",
                   "null output must return kInvalidArgument");

    core::HostTensor invalid_raw = valid_raw;
    invalid_raw.info.dtype = static_cast<core::TensorDataType>(99);
    expect_failure_atomic(context,
                          "invalid raw dtype",
                          processor,
                          invalid_raw,
                          valid_transform,
                          core::ErrorCode::kUnsupportedDataType);
    invalid_raw = valid_raw;
    invalid_raw.info.layout = core::TensorLayout::kNchw;
    expect_failure_atomic(context,
                          "invalid raw layout",
                          processor,
                          invalid_raw,
                          valid_transform,
                          core::ErrorCode::kUnsupportedLayout);
    invalid_raw = valid_raw;
    invalid_raw.info.shape = {1, 10, 8399};
    invalid_raw.data.resize(10U * 8399U);
    expect_failure_atomic(context,
                          "invalid raw shape",
                          processor,
                          invalid_raw,
                          valid_transform,
                          core::ErrorCode::kInvalidShape);
    invalid_raw = valid_raw;
    invalid_raw.data.pop_back();
    expect_failure_atomic(context,
                          "invalid raw data size",
                          processor,
                          invalid_raw,
                          valid_transform,
                          core::ErrorCode::kDataSizeMismatch);
    invalid_raw = valid_raw;
    invalid_raw.data[0] = std::numeric_limits<float>::infinity();
    expect_failure_atomic(context,
                          "non-finite raw value",
                          processor,
                          invalid_raw,
                          valid_transform,
                          core::ErrorCode::kInvalidArgument);

    preprocess::ImageTransformMetadata invalid_transform = valid_transform;
    invalid_transform.original_width = 0;
    expect_failure_atomic(context,
                          "zero original width",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);
    invalid_transform = valid_transform;
    invalid_transform.original_height = 0;
    expect_failure_atomic(context,
                          "zero original height",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);
    invalid_transform = valid_transform;
    invalid_transform.gain = 0.0;
    expect_failure_atomic(context,
                          "zero gain",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);
    invalid_transform = valid_transform;
    invalid_transform.gain = -1.0;
    expect_failure_atomic(context,
                          "negative gain",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);
    invalid_transform = valid_transform;
    invalid_transform.gain = std::numeric_limits<double>::quiet_NaN();
    expect_failure_atomic(context,
                          "non-finite gain",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);
    invalid_transform = valid_transform;
    invalid_transform.target_width = 320;
    expect_failure_atomic(context,
                          "incorrect target width",
                          processor,
                          valid_raw,
                          invalid_transform,
                          core::ErrorCode::kInvalidArgument);

    postprocess::PostprocessConfig invalid_config;
    invalid_config.agnostic = true;
    expect_failure_atomic(context,
                          "invalid config",
                          postprocess::PostProcessor(invalid_config),
                          valid_raw,
                          valid_transform,
                          core::ErrorCode::kInvalidArgument);

    std::vector<postprocess::Detection> output{
        {1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 1, 99U}};
    expect_success(context,
                   "empty valid result",
                   processor,
                   valid_raw,
                   valid_transform,
                   output);
    context.expect(output.empty(),
                   "empty valid result",
                   "no confidence above threshold must succeed with empty output");
}

}  // namespace

int main() {
    TestContext context;
    test_inverse_transform(context);
    test_actual_odd_padding_metadata(context);
    test_clipping_and_degenerate_retention(context);
    test_nms_before_transform_and_class_aware(context);
    test_decode_and_nms_integration(context);
    test_failures_and_empty_result(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count()
                  << " postprocessor process test(s) failed\n";
        return 1;
    }

    std::cout << "Postprocessor process tests passed\n";
    return 0;
}
