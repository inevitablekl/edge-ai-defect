#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"

#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

static_assert(__cplusplus == 201703L, "The project must compile as C++17");

namespace {

namespace core = edge_ai_defect::core;

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

void test_status(TestContext& context) {
    const core::Status success = core::Status::success();
    context.expect(success.ok(), "status success", "ok() must be true");
    context.expect(success.code() == core::ErrorCode::kOk,
                   "status success",
                   "code must be kOk");
    context.expect(success.message().empty(),
                   "status success",
                   "message must be empty");

    const core::Status failure = core::Status::failure(
        core::ErrorCode::kInvalidArgument, "invalid core argument");
    context.expect(!failure.ok(), "status failure", "ok() must be false");
    context.expect(failure.code() == core::ErrorCode::kInvalidArgument,
                   "status failure",
                   "error code must be preserved");
    context.expect(failure.message() == "invalid core argument",
                   "status failure",
                   "diagnostic message must be preserved");
}

void expect_element_count(TestContext& context,
                          const std::string& case_name,
                          const std::vector<std::int64_t>& shape,
                          std::size_t expected_count) {
    std::size_t actual_count = 0;
    const core::Status status =
        core::checked_element_count(shape, actual_count);
    context.expect(status.ok(), case_name, "element count must succeed");
    context.expect(actual_count == expected_count,
                   case_name,
                   "unexpected element count");
}

void expect_element_count_failure(TestContext& context,
                                  const std::string& case_name,
                                  const std::vector<std::int64_t>& shape,
                                  core::ErrorCode expected_code) {
    std::size_t element_count = 123;
    const core::Status status =
        core::checked_element_count(shape, element_count);
    context.expect(!status.ok(), case_name, "element count must fail");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected error code");
    context.expect(element_count == 0,
                   case_name,
                   "failed calculation must reset output count");
    context.expect(!status.message().empty(),
                   case_name,
                   "failure must include a diagnostic message");
}

void test_checked_element_count(TestContext& context) {
    expect_element_count(context,
                         "NCHW model input element count",
                         {1, 3, 640, 640},
                         1228800);
    expect_element_count(context,
                         "BCN model output element count",
                         {1, 10, 8400},
                         84000);
    expect_element_count_failure(
        context, "empty shape", {}, core::ErrorCode::kInvalidShape);
    expect_element_count_failure(
        context, "zero dimension", {1, 0, 4}, core::ErrorCode::kInvalidShape);
    expect_element_count_failure(context,
                                 "dynamic dimension",
                                 {1, -1, 4},
                                 core::ErrorCode::kInvalidShape);
    expect_element_count_failure(context,
                                 "negative dimension",
                                 {1, -2, 4},
                                 core::ErrorCode::kInvalidShape);
    expect_element_count_failure(
        context,
        "element count overflow",
        {std::numeric_limits<std::int64_t>::max(), 3},
        core::ErrorCode::kOverflow);
}

void expect_host_tensor_status(TestContext& context,
                               const std::string& case_name,
                               const core::HostTensor& tensor,
                               bool expected_ok,
                               core::ErrorCode expected_code) {
    const core::Status status = core::validate_host_tensor(tensor);
    context.expect(status.ok() == expected_ok,
                   case_name,
                   "unexpected validation result");
    context.expect(status.code() == expected_code,
                   case_name,
                   "unexpected validation error code");
    if (!expected_ok) {
        context.expect(!status.message().empty(),
                       case_name,
                       "failure must include a diagnostic message");
    }
}

void test_host_tensor(TestContext& context) {
    const core::HostTensor valid_nchw{
        {core::TensorDataType::kFloat32,
         core::TensorLayout::kNchw,
         {1, 3, 2, 2}},
        std::vector<float>(12, 0.5F),
    };
    expect_host_tensor_status(context,
                              "valid float32 NCHW HostTensor",
                              valid_nchw,
                              true,
                              core::ErrorCode::kOk);

    const core::HostTensor valid_bcn{
        {core::TensorDataType::kFloat32,
         core::TensorLayout::kBcn,
         {1, 10, 4}},
        std::vector<float>(40, 0.0F),
    };
    expect_host_tensor_status(context,
                              "valid float32 BCN HostTensor",
                              valid_bcn,
                              true,
                              core::ErrorCode::kOk);

    core::HostTensor insufficient_data = valid_nchw;
    insufficient_data.data.pop_back();
    expect_host_tensor_status(context,
                              "HostTensor insufficient data",
                              insufficient_data,
                              false,
                              core::ErrorCode::kDataSizeMismatch);

    core::HostTensor excess_data = valid_nchw;
    excess_data.data.push_back(0.0F);
    expect_host_tensor_status(context,
                              "HostTensor excess data",
                              excess_data,
                              false,
                              core::ErrorCode::kDataSizeMismatch);

    core::HostTensor invalid_shape = valid_nchw;
    invalid_shape.info.shape = {1, 3, 0, 2};
    expect_host_tensor_status(context,
                              "HostTensor invalid shape",
                              invalid_shape,
                              false,
                              core::ErrorCode::kInvalidShape);

    core::HostTensor invalid_dtype = valid_nchw;
    invalid_dtype.info.dtype = static_cast<core::TensorDataType>(99);
    expect_host_tensor_status(context,
                              "HostTensor invalid dtype",
                              invalid_dtype,
                              false,
                              core::ErrorCode::kUnsupportedDataType);

    core::HostTensor invalid_layout = valid_nchw;
    invalid_layout.info.layout = static_cast<core::TensorLayout>(99);
    expect_host_tensor_status(context,
                              "HostTensor invalid layout",
                              invalid_layout,
                              false,
                              core::ErrorCode::kUnsupportedLayout);
}

}  // namespace

int main() {
    TestContext context;
    test_status(context);
    test_checked_element_count(context);
    test_host_tensor(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " core contract test(s) failed\n";
        return 1;
    }

    std::cout << "All core contract tests passed\n";
    return 0;
}
