#include "edge_ai_defect/runtime/cli.hpp"

#include <iostream>
#include <string>

namespace {

namespace core = edge_ai_defect::core;
namespace runtime = edge_ai_defect::runtime;

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

bool options_equal(const runtime::CliOptions& left,
                   const runtime::CliOptions& right) {
    return left.action == right.action && left.config_path == right.config_path;
}

void expect_failure_preserves_output(TestContext& context,
                                     const std::string& case_name,
                                     int argc,
                                     const char* const argv[]) {
    const runtime::CliOptions sentinel{runtime::CliAction::kRun, "sentinel.yaml"};
    runtime::CliOptions output = sentinel;
    const core::Status status = runtime::parse_cli(argc, argv, &output);
    context.expect(!status.ok(), case_name, "parse must fail");
    context.expect(status.code() == core::ErrorCode::kInvalidArgument,
                   case_name,
                   "unexpected ErrorCode");
    context.expect(!status.message().empty(), case_name, "message must be present");
    context.expect(options_equal(output, sentinel),
                   case_name,
                   "failure must preserve caller output");
}

void test_valid_config(TestContext& context) {
    const char* const argv[] = {"edge_ai_defect", "--config", "configs/runtime.yaml"};
    runtime::CliOptions options;
    const core::Status status = runtime::parse_cli(3, argv, &options);
    context.expect(status.ok(), "valid --config", status.message());
    context.expect(options.action == runtime::CliAction::kRun,
                   "valid --config",
                   "action must be run");
    context.expect(options.config_path == "configs/runtime.yaml",
                   "valid --config",
                   "config path must be preserved for the loader");
}

void test_help(TestContext& context) {
    const char* const argv[] = {"edge_ai_defect", "--help"};
    runtime::CliOptions options;
    const core::Status status = runtime::parse_cli(2, argv, &options);
    context.expect(status.ok(), "standalone --help", status.message());
    context.expect(options.action == runtime::CliAction::kHelp,
                   "standalone --help",
                   "action must be help");
    context.expect(options.config_path.empty(),
                   "standalone --help",
                   "help must not carry a config path");
}

void test_failures(TestContext& context) {
    const char* const missing_value[] = {"edge_ai_defect", "--config"};
    expect_failure_preserves_output(context, "missing --config value", 2, missing_value);

    const char* const duplicate_config[] = {
        "edge_ai_defect", "--config", "a.yaml", "--config", "b.yaml"};
    expect_failure_preserves_output(context, "duplicate --config", 5, duplicate_config);

    const char* const extra_argument[] = {
        "edge_ai_defect", "--config", "a.yaml", "extra"};
    expect_failure_preserves_output(context, "extra argument", 4, extra_argument);

    const char* const positional_argument[] = {"edge_ai_defect", "a.yaml"};
    expect_failure_preserves_output(context, "positional argument", 2, positional_argument);

    const char* const unsupported_flag[] = {"edge_ai_defect", "--model", "x.onnx"};
    expect_failure_preserves_output(context, "unsupported --model", 3, unsupported_flag);

    const char* const help_with_config[] = {
        "edge_ai_defect", "--help", "--config", "a.yaml"};
    expect_failure_preserves_output(context, "--help with other arguments", 4, help_with_config);

    const char* const empty_config[] = {"edge_ai_defect", "--config", ""};
    expect_failure_preserves_output(context, "empty --config value", 3, empty_config);
}

void test_invalid_invocation(TestContext& context) {
    runtime::CliOptions options;
    const core::Status null_output = runtime::parse_cli(1, nullptr, nullptr);
    context.expect(!null_output.ok(), "null output", "parse must fail");
    context.expect(null_output.code() == core::ErrorCode::kInvalidArgument,
                   "null output",
                   "unexpected ErrorCode");

    const core::Status invalid_argv = runtime::parse_cli(1, nullptr, &options);
    context.expect(!invalid_argv.ok(), "null argv", "parse must fail");
    context.expect(invalid_argv.code() == core::ErrorCode::kInvalidArgument,
                   "null argv",
                   "unexpected ErrorCode");
}

}  // namespace

int main() {
    TestContext context;
    test_valid_config(context);
    test_help(context);
    test_failures(context);
    test_invalid_invocation(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " CLI parser test(s) failed\n";
        return 1;
    }

    std::cout << "All CLI parser tests passed\n";
    return 0;
}
