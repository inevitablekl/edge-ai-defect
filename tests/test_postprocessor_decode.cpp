#include "postprocess_detail.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace detail = edge_ai_defect::postprocess::detail;
namespace postprocess = edge_ai_defect::postprocess;

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

void set_candidate_geometry(core::HostTensor& raw_output,
                            std::size_t candidate_index,
                            float cx,
                            float cy,
                            float width,
                            float height) {
    set_value(raw_output, 0U, candidate_index, cx);
    set_value(raw_output, 1U, candidate_index, cy);
    set_value(raw_output, 2U, candidate_index, width);
    set_value(raw_output, 3U, candidate_index, height);
}

void set_class_score(core::HostTensor& raw_output,
                     std::size_t candidate_index,
                     std::size_t class_id,
                     float score) {
    set_value(raw_output, 4U + class_id, candidate_index, score);
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

void expect_decode_success(TestContext& context,
                           const std::string& case_name,
                           const core::HostTensor& raw_output,
                           const postprocess::PostprocessConfig& config,
                           std::vector<detail::DecodedCandidate>& output) {
    const core::Status status =
        detail::decode_candidates(raw_output, config, &output);
    context.expect(status.ok(), case_name, "decode must succeed");
    context.expect(status.code() == core::ErrorCode::kOk,
                   case_name,
                   "success code must be kOk");
}

void expect_decode_failure(TestContext& context,
                           const std::string& case_name,
                           const core::HostTensor& raw_output,
                           const postprocess::PostprocessConfig& config,
                           core::ErrorCode expected_code) {
    const std::vector<detail::DecodedCandidate> expected_output{
        {1.0F, 2.0F, 3.0F, 4.0F, 0.9F, 5, 17U}};
    std::vector<detail::DecodedCandidate> output = expected_output;
    const core::Status status =
        detail::decode_candidates(raw_output, config, &output);
    context.expect(!status.ok(), case_name, "decode must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(candidate_vectors_equal(output, expected_output),
                   case_name,
                   "failure must preserve output");
}

void test_bcn_indexing_and_xyxy(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate_geometry(raw_output, 7U, 100.25F, 200.5F, 20.5F, 40.25F);
    set_class_score(raw_output, 7U, 3U, 0.9F);

    std::vector<detail::DecodedCandidate> output;
    expect_decode_success(context,
                          "BCN indexing and xyxy conversion",
                          raw_output,
                          {},
                          output);
    context.expect(output.size() == 1U,
                   "BCN indexing and xyxy conversion",
                   "expected exactly one decoded candidate");
    if (output.size() != 1U) {
        return;
    }
    const detail::DecodedCandidate& candidate = output.front();
    context.expect(candidate.candidate_index == 7U,
                   "BCN indexing and xyxy conversion",
                   "must retain the BCN candidate index");
    context.expect(candidate.class_id == 3 && candidate.confidence == 0.9F,
                   "BCN indexing and xyxy conversion",
                   "must read class scores using BCN indexing");
    context.expect(candidate.x1 == 90.0F && candidate.y1 == 180.375F &&
                       candidate.x2 == 110.5F && candidate.y2 == 220.625F,
                   "BCN indexing and xyxy conversion",
                   "must convert continuous cxcywh without rounding");
}

void test_confidence_boundary(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    for (const std::size_t candidate_index : {1U, 2U, 3U}) {
        set_candidate_geometry(raw_output, candidate_index, 10.0F, 10.0F, 2.0F, 2.0F);
    }
    set_class_score(raw_output, 1U, 0U, 0.2499F);
    set_class_score(raw_output, 2U, 0U, 0.25F);
    set_class_score(raw_output,
                    3U,
                    0U,
                    std::nextafter(0.25F, std::numeric_limits<float>::infinity()));

    std::vector<detail::DecodedCandidate> output;
    expect_decode_success(context, "strict confidence boundary", raw_output, {}, output);
    context.expect(output.size() == 1U,
                   "strict confidence boundary",
                   "only confidence strictly above threshold may remain");
    if (output.size() == 1U) {
        context.expect(output.front().candidate_index == 3U,
                       "strict confidence boundary",
                       "nextafter threshold candidate must remain");
    }
}

void test_class_argmax_ties(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    for (const std::size_t candidate_index : {10U, 11U, 12U}) {
        set_candidate_geometry(raw_output, candidate_index, 10.0F, 10.0F, 2.0F, 2.0F);
    }
    set_class_score(raw_output, 10U, 4U, 0.8F);
    set_class_score(raw_output, 11U, 1U, 0.9F);
    set_class_score(raw_output, 11U, 5U, 0.9F);
    for (std::size_t class_id = 0U; class_id < 6U; ++class_id) {
        set_class_score(raw_output, 12U, class_id, 0.7F);
    }

    std::vector<detail::DecodedCandidate> output;
    expect_decode_success(context, "class argmax ties", raw_output, {}, output);
    context.expect(output.size() == 3U,
                   "class argmax ties",
                   "all three candidates must pass confidence filtering");
    if (output.size() != 3U) {
        return;
    }
    context.expect(output[0].candidate_index == 11U && output[0].class_id == 1,
                   "class argmax ties",
                   "two-way score tie must choose the smaller class id");
    context.expect(output[1].candidate_index == 10U && output[1].class_id == 4,
                   "class argmax ties",
                   "single maximum must select its class id");
    context.expect(output[2].candidate_index == 12U && output[2].class_id == 0,
                   "class argmax ties",
                   "six-way score tie must choose class zero");
}

void test_deterministic_order_and_max_nms(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    const std::size_t indices[] = {20U, 5U, 10U, 9U};
    for (const std::size_t candidate_index : indices) {
        set_candidate_geometry(raw_output, candidate_index, 10.0F, 10.0F, 2.0F, 2.0F);
    }
    set_class_score(raw_output, 20U, 4U, 0.95F);
    set_class_score(raw_output, 5U, 1U, 0.8F);
    set_class_score(raw_output, 10U, 2U, 0.8F);
    set_class_score(raw_output, 9U, 1U, 0.8F);

    std::vector<detail::DecodedCandidate> output;
    expect_decode_success(context, "deterministic order", raw_output, {}, output);
    context.expect(output.size() == 4U,
                   "deterministic order",
                   "all candidates must remain before max_nms truncation");
    if (output.size() == 4U) {
        context.expect(output[0].candidate_index == 20U &&
                           output[1].candidate_index == 5U &&
                           output[2].candidate_index == 9U &&
                           output[3].candidate_index == 10U,
                       "deterministic order",
                       "must sort by confidence, class id, then candidate index");
    }

    postprocess::PostprocessConfig config;
    config.max_nms = 2U;
    config.max_det = 2U;
    output.clear();
    expect_decode_success(context, "max_nms truncation", raw_output, config, output);
    context.expect(output.size() == 2U && output[0].candidate_index == 20U &&
                       output[1].candidate_index == 5U,
                   "max_nms truncation",
                   "must keep the first sorted max_nms candidates");
}

void test_invalid_geometry_and_empty_result(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate_geometry(raw_output, 1U, 10.0F, 10.0F, 0.0F, 2.0F);
    set_candidate_geometry(raw_output, 2U, 10.0F, 10.0F, -1.0F, 2.0F);
    set_candidate_geometry(raw_output, 3U, 10.0F, 10.0F, 2.0F, 0.0F);
    set_candidate_geometry(raw_output, 4U, 10.0F, 10.0F, 2.0F, -1.0F);
    set_candidate_geometry(raw_output,
                           5U,
                           std::numeric_limits<float>::max(),
                           10.0F,
                           std::numeric_limits<float>::max(),
                           2.0F);
    for (const std::size_t candidate_index : {1U, 2U, 3U, 4U, 5U}) {
        set_class_score(raw_output, candidate_index, 0U, 0.9F);
    }

    std::vector<detail::DecodedCandidate> output;
    expect_decode_success(context, "invalid geometry", raw_output, {}, output);
    context.expect(output.empty(),
                   "invalid geometry",
                   "non-positive or non-finite decoded geometry must be skipped");

    raw_output = make_raw_output();
    set_candidate_geometry(raw_output, 5U, 10.0F, 10.0F, 2.0F, 2.0F);
    set_class_score(raw_output, 5U, 0U, 0.25F);
    expect_decode_success(context, "empty valid result", raw_output, {}, output);
    context.expect(output.empty(),
                   "empty valid result",
                   "no candidate above threshold is a successful empty result");
}

void test_contract_failures_and_atomicity(TestContext& context) {
    core::HostTensor raw_output = make_raw_output();
    set_candidate_geometry(raw_output, 0U, 10.0F, 10.0F, 2.0F, 2.0F);
    set_class_score(raw_output, 0U, 0U, 0.9F);

    const core::Status null_status =
        detail::decode_candidates(raw_output, {}, nullptr);
    context.expect(!null_status.ok() &&
                       null_status.code() == core::ErrorCode::kInvalidArgument,
                   "null output",
                   "null output must fail with kInvalidArgument");

    core::HostTensor invalid_dtype = raw_output;
    invalid_dtype.info.dtype = static_cast<core::TensorDataType>(99);
    expect_decode_failure(context,
                          "invalid dtype",
                          invalid_dtype,
                          {},
                          core::ErrorCode::kUnsupportedDataType);

    core::HostTensor invalid_layout = raw_output;
    invalid_layout.info.layout = core::TensorLayout::kNchw;
    expect_decode_failure(context,
                          "invalid layout",
                          invalid_layout,
                          {},
                          core::ErrorCode::kUnsupportedLayout);

    core::HostTensor invalid_shape = raw_output;
    invalid_shape.info.shape = {1, 10, 8399};
    invalid_shape.data.resize(83990U);
    expect_decode_failure(context,
                          "invalid shape",
                          invalid_shape,
                          {},
                          core::ErrorCode::kInvalidShape);

    core::HostTensor invalid_data_size = raw_output;
    invalid_data_size.data.pop_back();
    expect_decode_failure(context,
                          "invalid data size",
                          invalid_data_size,
                          {},
                          core::ErrorCode::kDataSizeMismatch);

    core::HostTensor nan_value = raw_output;
    nan_value.data[6U * kCandidateCount] =
        std::numeric_limits<float>::quiet_NaN();
    expect_decode_failure(context,
                          "NaN raw value",
                          nan_value,
                          {},
                          core::ErrorCode::kInvalidArgument);

    core::HostTensor infinity_value = raw_output;
    infinity_value.data[7U * kCandidateCount] =
        std::numeric_limits<float>::infinity();
    expect_decode_failure(context,
                          "infinite raw value",
                          infinity_value,
                          {},
                          core::ErrorCode::kInvalidArgument);

    core::HostTensor negative_infinity_value = raw_output;
    negative_infinity_value.data[8U * kCandidateCount] =
        -std::numeric_limits<float>::infinity();
    expect_decode_failure(context,
                          "negative infinite raw value",
                          negative_infinity_value,
                          {},
                          core::ErrorCode::kInvalidArgument);

    postprocess::PostprocessConfig invalid_config;
    invalid_config.multi_label = true;
    expect_decode_failure(context,
                          "invalid config",
                          raw_output,
                          invalid_config,
                          core::ErrorCode::kInvalidArgument);
}

}  // namespace

int main() {
    TestContext context;
    test_bcn_indexing_and_xyxy(context);
    test_confidence_boundary(context);
    test_class_argmax_ties(context);
    test_deterministic_order_and_max_nms(context);
    test_invalid_geometry_and_empty_result(context);
    test_contract_failures_and_atomicity(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count()
                  << " postprocessor decode test(s) failed\n";
        return 1;
    }

    std::cout << "Postprocessor decode tests passed\n";
    return 0;
}
