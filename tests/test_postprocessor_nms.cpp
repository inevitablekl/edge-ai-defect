#include "postprocess_detail.hpp"

#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace detail = edge_ai_defect::postprocess::detail;
namespace postprocess = edge_ai_defect::postprocess;

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

detail::DecodedCandidate make_candidate(float x1,
                                        float y1,
                                        float x2,
                                        float y2,
                                        float confidence,
                                        int class_id,
                                        std::size_t candidate_index) {
    return {x1, y1, x2, y2, confidence, class_id, candidate_index};
}

bool candidates_equal(const detail::DecodedCandidate& left,
                      const detail::DecodedCandidate& right) {
    return left.x1 == right.x1 && left.y1 == right.y1 &&
           left.x2 == right.x2 && left.y2 == right.y2 &&
           left.confidence == right.confidence && left.class_id == right.class_id &&
           left.candidate_index == right.candidate_index;
}

bool candidate_vectors_equal(const std::vector<detail::DecodedCandidate>& left,
                             const std::vector<detail::DecodedCandidate>& right) {
    if (left.size() != right.size()) {
        return false;
    }
    for (std::size_t index = 0U; index < left.size(); ++index) {
        if (!candidates_equal(left[index], right[index])) {
            return false;
        }
    }
    return true;
}

void expect_near(TestContext& context,
                 const std::string& case_name,
                 float actual,
                 float expected) {
    context.expect(std::abs(actual - expected) <= 1.0e-6F,
                   case_name,
                   "unexpected float value");
}

void expect_nms_success(TestContext& context,
                        const std::string& case_name,
                        const std::vector<detail::DecodedCandidate>& input,
                        const postprocess::PostprocessConfig& config,
                        std::vector<detail::DecodedCandidate>& output) {
    const core::Status status =
        detail::apply_class_aware_nms(input, config, &output);
    context.expect(status.ok(), case_name, "NMS must succeed");
    context.expect(status.code() == core::ErrorCode::kOk,
                   case_name,
                   "success code must be kOk");
}

void expect_nms_failure(TestContext& context,
                        const std::string& case_name,
                        const std::vector<detail::DecodedCandidate>& input,
                        const postprocess::PostprocessConfig& config,
                        core::ErrorCode expected_code) {
    const std::vector<detail::DecodedCandidate> expected_output{
        make_candidate(1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 5, 42U)};
    std::vector<detail::DecodedCandidate> output = expected_output;
    const core::Status status =
        detail::apply_class_aware_nms(input, config, &output);
    context.expect(!status.ok(), case_name, "NMS must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(candidate_vectors_equal(output, expected_output),
                   case_name,
                   "failure must preserve output");
}

void test_continuous_iou(TestContext& context) {
    const detail::DecodedCandidate first =
        make_candidate(0.0F, 0.0F, 2.0F, 2.0F, 0.9F, 0, 1U);
    const detail::DecodedCandidate disjoint =
        make_candidate(3.0F, 0.0F, 5.0F, 2.0F, 0.8F, 0, 2U);
    const detail::DecodedCandidate partial =
        make_candidate(1.0F, 0.0F, 3.0F, 2.0F, 0.8F, 0, 3U);
    const detail::DecodedCandidate touching =
        make_candidate(2.0F, 0.0F, 4.0F, 2.0F, 0.8F, 0, 4U);
    const detail::DecodedCandidate zero_area =
        make_candidate(0.0F, 0.0F, 0.0F, 2.0F, 0.8F, 0, 5U);
    const detail::DecodedCandidate larger =
        make_candidate(0.0F, 0.0F, 1.0F, 1.0F, 0.8F, 0, 6U);
    const detail::DecodedCandidate largest =
        make_candidate(0.0F, 0.0F, 2.0F, 2.0F, 0.8F, 0, 7U);

    expect_near(context,
                "disjoint IoU",
                detail::continuous_iou(first, disjoint),
                0.0F);
    expect_near(context,
                "identical IoU",
                detail::continuous_iou(first, first),
                1.0F);
    expect_near(context,
                "partial overlap IoU",
                detail::continuous_iou(first, partial),
                1.0F / 3.0F);
    expect_near(context,
                "edge touching IoU",
                detail::continuous_iou(first, touching),
                0.0F);
    expect_near(context,
                "zero-area IoU",
                detail::continuous_iou(first, zero_area),
                0.0F);
    expect_near(context,
                "continuous no-plus-one IoU",
                detail::continuous_iou(larger, largest),
                0.25F);
    expect_near(context,
                "non-finite offset IoU",
                detail::continuous_iou(first,
                                       partial,
                                       std::numeric_limits<float>::infinity()),
                0.0F);
}

void test_threshold_strictness(TestContext& context) {
    const detail::DecodedCandidate first =
        make_candidate(0.0F, 0.0F, 2.0F, 2.0F, 0.9F, 0, 1U);
    const detail::DecodedCandidate second =
        make_candidate(1.0F, 0.0F, 3.0F, 2.0F, 0.8F, 0, 2U);
    const std::vector<detail::DecodedCandidate> input{first, second};
    const float actual_iou = detail::continuous_iou(first, second);

    postprocess::PostprocessConfig equal_threshold;
    equal_threshold.iou_threshold = actual_iou;
    std::vector<detail::DecodedCandidate> output;
    expect_nms_success(context,
                       "IoU equal threshold",
                       input,
                       equal_threshold,
                       output);
    context.expect(output.size() == 2U,
                   "IoU equal threshold",
                   "IoU equal to threshold must not suppress");

    postprocess::PostprocessConfig lower_threshold = equal_threshold;
    lower_threshold.iou_threshold = std::nextafter(
        actual_iou, -std::numeric_limits<float>::infinity());
    output.clear();
    expect_nms_success(context,
                       "IoU above threshold",
                       input,
                       lower_threshold,
                       output);
    context.expect(output.size() == 1U && output.front().candidate_index == 1U,
                   "IoU above threshold",
                   "IoU strictly above threshold must suppress later candidate");
}

void test_same_and_cross_class_behavior(TestContext& context) {
    const detail::DecodedCandidate first =
        make_candidate(0.0F, 0.0F, 10.0F, 10.0F, 0.9F, 0, 1U);
    const detail::DecodedCandidate same_class =
        make_candidate(1.0F, 1.0F, 9.0F, 9.0F, 0.8F, 0, 2U);
    const detail::DecodedCandidate other_class =
        make_candidate(0.0F, 0.0F, 10.0F, 10.0F, 0.8F, 1, 3U);
    const detail::DecodedCandidate equal_confidence_later =
        make_candidate(1.0F, 1.0F, 9.0F, 9.0F, 0.9F, 0, 2U);

    std::vector<detail::DecodedCandidate> output;
    expect_nms_success(context,
                       "same-class default threshold",
                       {first, same_class},
                       {},
                       output);
    context.expect(output.size() == 1U && output.front().candidate_index == 1U,
                   "same-class default threshold",
                   "higher-confidence same-class candidate must remain");

    output.clear();
    expect_nms_success(context,
                       "same-class equal-confidence order",
                       {first, equal_confidence_later},
                       {},
                       output);
    context.expect(output.size() == 1U && output.front().candidate_index == 1U,
                   "same-class equal-confidence order",
                   "same-confidence candidates must retain the first sorted input");

    output.clear();
    expect_nms_success(context,
                       "cross-class retention",
                       {first, other_class},
                       {},
                       output);
    context.expect(output.size() == 2U,
                   "cross-class retention",
                   "identical cross-class boxes must both remain");
    if (output.size() == 2U) {
        context.expect(candidates_equal(output[0], first) &&
                           candidates_equal(output[1], other_class),
                       "cross-class retention",
                       "class offset must not alter output coordinates");
    }
}

void test_order_and_limits(TestContext& context) {
    const std::vector<detail::DecodedCandidate> sorted_input{
        make_candidate(0.0F, 0.0F, 2.0F, 2.0F, 0.9F, 0, 1U),
        make_candidate(0.25F, 0.25F, 1.75F, 1.75F, 0.8F, 0, 2U),
        make_candidate(4.0F, 0.0F, 6.0F, 2.0F, 0.7F, 1, 3U),
        make_candidate(8.0F, 0.0F, 10.0F, 2.0F, 0.6F, 1, 4U),
    };
    std::vector<detail::DecodedCandidate> output;
    expect_nms_success(context, "greedy accepted order", sorted_input, {}, output);
    context.expect(output.size() == 3U && output[0].candidate_index == 1U &&
                       output[1].candidate_index == 3U &&
                       output[2].candidate_index == 4U,
                   "greedy accepted order",
                   "NMS must not reorder unsuppressed candidates");

    postprocess::PostprocessConfig max_det_config;
    max_det_config.max_det = 2U;
    max_det_config.max_nms = 4U;
    output.clear();
    expect_nms_success(context, "max_det", sorted_input, max_det_config, output);
    context.expect(output.size() == 2U && output[0].candidate_index == 1U &&
                       output[1].candidate_index == 3U,
                   "max_det",
                   "must stop after the first max_det accepted candidates");

    postprocess::PostprocessConfig max_nms_config;
    max_nms_config.max_det = 2U;
    max_nms_config.max_nms = 2U;
    output.clear();
    expect_nms_success(context,
                       "max_nms defensive bound",
                       sorted_input,
                       max_nms_config,
                       output);
    context.expect(output.size() == 1U && output.front().candidate_index == 1U,
                   "max_nms defensive bound",
                   "candidates after max_nms must not be processed");
}

void test_failures_and_empty_input(TestContext& context) {
    const std::vector<detail::DecodedCandidate> valid_input{
        make_candidate(0.0F, 0.0F, 2.0F, 2.0F, 0.9F, 0, 1U)};
    const core::Status null_status =
        detail::apply_class_aware_nms(valid_input, {}, nullptr);
    context.expect(!null_status.ok() &&
                       null_status.code() == core::ErrorCode::kInvalidArgument,
                   "null output",
                   "null output must fail with kInvalidArgument");

    postprocess::PostprocessConfig config;
    config.iou_threshold = std::numeric_limits<float>::quiet_NaN();
    expect_nms_failure(context,
                       "invalid IoU threshold",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.max_det = 0U;
    expect_nms_failure(context,
                       "zero max_det",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.max_nms = 0U;
    expect_nms_failure(context,
                       "zero max_nms",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.max_nms = config.max_det - 1U;
    expect_nms_failure(context,
                       "max_nms below max_det",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.max_wh = std::numeric_limits<float>::infinity();
    expect_nms_failure(context,
                       "non-finite max_wh",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.max_wh = 0.0F;
    expect_nms_failure(context,
                       "non-positive max_wh",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.agnostic = true;
    expect_nms_failure(context,
                       "agnostic mode",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);
    config = {};
    config.multi_label = true;
    expect_nms_failure(context,
                       "multi-label mode",
                       valid_input,
                       config,
                       core::ErrorCode::kInvalidArgument);

    std::vector<detail::DecodedCandidate> invalid_class = valid_input;
    invalid_class.front().class_id = 6;
    expect_nms_failure(context,
                       "invalid class id",
                       invalid_class,
                       {},
                       core::ErrorCode::kInvalidArgument);
    std::vector<detail::DecodedCandidate> non_finite_coordinate = valid_input;
    non_finite_coordinate.front().x1 = std::numeric_limits<float>::quiet_NaN();
    expect_nms_failure(context,
                       "non-finite coordinate",
                       non_finite_coordinate,
                       {},
                       core::ErrorCode::kInvalidArgument);
    std::vector<detail::DecodedCandidate> non_finite_confidence = valid_input;
    non_finite_confidence.front().confidence = std::numeric_limits<float>::infinity();
    expect_nms_failure(context,
                       "non-finite confidence",
                       non_finite_confidence,
                       {},
                       core::ErrorCode::kInvalidArgument);
    std::vector<detail::DecodedCandidate> zero_width = valid_input;
    zero_width.front().x2 = zero_width.front().x1;
    expect_nms_failure(context,
                       "zero-width candidate",
                       zero_width,
                       {},
                       core::ErrorCode::kInvalidArgument);
    std::vector<detail::DecodedCandidate> negative_height = valid_input;
    negative_height.front().y2 = negative_height.front().y1 - 1.0F;
    expect_nms_failure(context,
                       "negative-height candidate",
                       negative_height,
                       {},
                       core::ErrorCode::kInvalidArgument);

    std::vector<detail::DecodedCandidate> output{
        make_candidate(1.0F, 1.0F, 2.0F, 2.0F, 0.9F, 0, 8U)};
    expect_nms_success(context, "empty input", {}, {}, output);
    context.expect(output.empty(),
                   "empty input",
                   "empty input must succeed with empty output");
}

}  // namespace

int main() {
    TestContext context;
    test_continuous_iou(context);
    test_threshold_strictness(context);
    test_same_and_cross_class_behavior(context);
    test_order_and_limits(context);
    test_failures_and_empty_input(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count()
                  << " postprocessor NMS test(s) failed\n";
        return 1;
    }

    std::cout << "Postprocessor NMS tests passed\n";
    return 0;
}
