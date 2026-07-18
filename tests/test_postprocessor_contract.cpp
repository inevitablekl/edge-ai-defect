#include "edge_ai_defect/postprocess/detection.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"

#include <iostream>
#include <limits>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace postprocess = edge_ai_defect::postprocess;
namespace preprocess = edge_ai_defect::preprocess;

using ProcessSignature = core::Status (postprocess::PostProcessor::*)(
    const core::HostTensor&,
    const preprocess::ImageTransformMetadata&,
    std::vector<postprocess::Detection>*) const;

static_assert(std::is_same_v<decltype(&postprocess::PostProcessor::process),
                             ProcessSignature>);
static_assert(std::is_copy_constructible_v<postprocess::PostProcessor>);
static_assert(std::is_copy_assignable_v<postprocess::PostProcessor>);
static_assert(std::is_move_constructible_v<postprocess::PostProcessor>);
static_assert(std::is_move_assignable_v<postprocess::PostProcessor>);

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

void expect_invalid_config(TestContext& context,
                           const std::string& case_name,
                           const postprocess::PostprocessConfig& config) {
    const core::Status status = postprocess::validate_postprocess_config(config);
    context.expect(!status.ok(), case_name, "validation must fail");
    context.expect(status.code() == core::ErrorCode::kInvalidArgument,
                   case_name,
                   "error code must be kInvalidArgument");
    context.expect(!status.message().empty(),
                   case_name,
                   "failure must include a diagnostic message");
}

void test_detection_contract(TestContext& context) {
    const postprocess::Detection detection{
        1.25F, 2.5F, 101.75F, 202.0F, 0.9F, 4, 8399U};
    context.expect(detection.x1 == 1.25F && detection.y1 == 2.5F &&
                       detection.x2 == 101.75F && detection.y2 == 202.0F,
                   "Detection coordinates",
                   "continuous original-image xyxy values must be expressible");
    context.expect(detection.confidence == 0.9F,
                   "Detection confidence",
                   "confidence field must preserve float values");
    context.expect(detection.class_id == 4,
                   "Detection class id",
                   "class id field must preserve integer values");
    context.expect(detection.candidate_index == 8399U,
                   "Detection candidate index",
                   "candidate index must preserve the raw BCN position");
}

void test_default_config(TestContext& context) {
    const postprocess::PostprocessConfig config;
    context.expect(config.confidence_threshold == 0.25F,
                   "default config",
                   "unexpected confidence threshold");
    context.expect(config.iou_threshold == 0.45F,
                   "default config",
                   "unexpected IoU threshold");
    context.expect(config.max_nms == 30000U,
                   "default config",
                   "unexpected max_nms");
    context.expect(config.max_det == 300U,
                   "default config",
                   "unexpected max_det");
    context.expect(config.max_wh == 7680.0F,
                   "default config",
                   "unexpected max_wh");
    context.expect(!config.multi_label && !config.agnostic,
                   "default config",
                   "M3 must use single-label class-aware NMS");

    const core::Status status = postprocess::validate_postprocess_config(config);
    context.expect(status.ok(), "default config", "validation must succeed");
    context.expect(status.code() == core::ErrorCode::kOk,
                   "default config",
                   "success code must be kOk");
}

void test_config_validation(TestContext& context) {
    postprocess::PostprocessConfig config;

    config.confidence_threshold =
        std::numeric_limits<float>::quiet_NaN();
    expect_invalid_config(context, "non-finite confidence threshold", config);
    config = {};
    config.confidence_threshold = -0.01F;
    expect_invalid_config(context, "negative confidence threshold", config);
    config = {};
    config.confidence_threshold = 1.01F;
    expect_invalid_config(context, "confidence threshold above one", config);

    config = {};
    config.iou_threshold = std::numeric_limits<float>::infinity();
    expect_invalid_config(context, "non-finite IoU threshold", config);
    config = {};
    config.iou_threshold = -0.01F;
    expect_invalid_config(context, "negative IoU threshold", config);
    config = {};
    config.iou_threshold = 1.01F;
    expect_invalid_config(context, "IoU threshold above one", config);

    config = {};
    config.max_det = 0U;
    expect_invalid_config(context, "zero max_det", config);
    config = {};
    config.max_nms = 0U;
    expect_invalid_config(context, "zero max_nms", config);
    config = {};
    config.max_nms = config.max_det - 1U;
    expect_invalid_config(context, "max_nms below max_det", config);

    config = {};
    config.max_wh = std::numeric_limits<float>::quiet_NaN();
    expect_invalid_config(context, "non-finite max_wh", config);
    config = {};
    config.max_wh = 0.0F;
    expect_invalid_config(context, "non-positive max_wh", config);

    config = {};
    config.multi_label = true;
    expect_invalid_config(context, "multi-label mode", config);
    config = {};
    config.agnostic = true;
    expect_invalid_config(context, "class-agnostic mode", config);
}

void test_postprocessor_value_semantics(TestContext& context) {
    postprocess::PostProcessor original;
    postprocess::PostProcessor copied(original);
    postprocess::PostProcessor copy_assigned;
    copy_assigned = copied;
    postprocess::PostProcessor moved(std::move(copied));
    postprocess::PostProcessor move_assigned;
    move_assigned = std::move(moved);
    (void)move_assigned;
    context.expect(true,
                   "PostProcessor value semantics",
                   "copy and move operations must compile");
}

}  // namespace

int main() {
    TestContext context;
    test_detection_contract(context);
    test_default_config(context);
    test_config_validation(context);
    test_postprocessor_value_semantics(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count()
                  << " postprocessor contract test(s) failed\n";
        return 1;
    }

    std::cout << "Postprocessor contract tests passed\n";
    return 0;
}
