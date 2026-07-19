#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>

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

struct Options {
    std::filesystem::path temp_dir;
};

bool parse_options(int argc, char* argv[], Options* options) {
    if (options == nullptr) {
        return false;
    }
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        if (argument == "--temp-dir" && index + 1 < argc) {
            options->temp_dir = argv[++index];
        } else {
            std::cerr << "Unknown or incomplete argument: " << argument << '\n';
            return false;
        }
    }
    if (options->temp_dir.empty()) {
        std::cerr << "Usage: test_runtime_config --temp-dir <path>\n";
        return false;
    }
    return true;
}

std::string valid_yaml() {
    return R"yaml(schema_version: 1

backend:
  type: onnxruntime_cpu

model:
  contract_path: ../contracts/frozen.yaml
  model_path: ../models/frozen.onnx

input:
  type: directory
  directory: ../images

output:
  json_path: ../results/serial.json
  console: true
  overwrite: false

postprocess:
  confidence_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680.0
  agnostic: false
  multi_label: false

timing:
  enabled: true
)yaml";
}

std::string replace_once(std::string source,
                         const std::string& original,
                         const std::string& replacement) {
    const std::size_t position = source.find(original);
    if (position == std::string::npos) {
        return {};
    }
    source.replace(position, original.size(), replacement);
    return source;
}

std::string replace_to_end(std::string source,
                           const std::string& marker,
                           const std::string& replacement) {
    const std::size_t position = source.find(marker);
    if (position == std::string::npos) {
        return {};
    }
    source.replace(position, std::string::npos, replacement);
    return source;
}

bool write_text_file(const std::filesystem::path& path,
                     const std::string& content) {
    std::ofstream output(path);
    output << content;
    output.close();
    return output.good();
}

runtime::RuntimeConfig sentinel_config() {
    runtime::RuntimeConfig config;
    config.schema_version = 99;
    config.backend_type = "sentinel";
    config.model_contract_path = "sentinel_contract";
    config.model_path = "sentinel_model";
    config.input_type = "sentinel_input";
    config.input_directory = "sentinel_directory";
    config.output_json_path = "sentinel_output";
    config.output_console = true;
    config.output_overwrite = true;
    config.timing_enabled = true;
    return config;
}

bool config_equal(const runtime::RuntimeConfig& left,
                  const runtime::RuntimeConfig& right) {
    return left.schema_version == right.schema_version &&
        left.backend_type == right.backend_type &&
        left.model_contract_path == right.model_contract_path &&
        left.model_path == right.model_path &&
        left.input_type == right.input_type &&
        left.input_directory == right.input_directory &&
        left.output_json_path == right.output_json_path &&
        left.output_console == right.output_console &&
        left.output_overwrite == right.output_overwrite &&
        left.postprocess_config.confidence_threshold ==
            right.postprocess_config.confidence_threshold &&
        left.postprocess_config.iou_threshold ==
            right.postprocess_config.iou_threshold &&
        left.postprocess_config.max_nms == right.postprocess_config.max_nms &&
        left.postprocess_config.max_det == right.postprocess_config.max_det &&
        left.postprocess_config.max_wh == right.postprocess_config.max_wh &&
        left.postprocess_config.agnostic == right.postprocess_config.agnostic &&
        left.postprocess_config.multi_label == right.postprocess_config.multi_label &&
        left.timing_enabled == right.timing_enabled;
}

void expect_failure(TestContext& context,
                    const Options& options,
                    const std::string& case_name,
                    const std::string& yaml,
                    const std::string& expected_message_fragment) {
    const std::filesystem::path path =
        options.temp_dir / ("invalid_" + case_name + ".yaml");
    context.expect(write_text_file(path, yaml), case_name, "could not write YAML");

    const runtime::RuntimeConfig sentinel = sentinel_config();
    runtime::RuntimeConfig output = sentinel;
    bool exception_escaped = false;
    core::Status status = core::Status::success();
    try {
        status = runtime::RuntimeConfigLoader::load(path, &output);
    } catch (...) {
        exception_escaped = true;
    }

    context.expect(!exception_escaped,
                   case_name,
                   "loader must not allow an exception to cross its boundary");
    context.expect(!status.ok(), case_name, "load must fail");
    context.expect(!status.message().empty(), case_name, "message must be present");
    context.expect(status.message().find(expected_message_fragment) != std::string::npos,
                   case_name,
                   "message must identify '" + expected_message_fragment + "'");
    context.expect(config_equal(output, sentinel),
                   case_name,
                   "failure must preserve caller output");
}

void test_valid_config_and_paths(TestContext& context, const Options& options) {
    const std::filesystem::path config_dir = options.temp_dir / "configs";
    std::error_code error;
    std::filesystem::create_directories(config_dir, error);
    context.expect(!error, "valid config setup", "could not create config directory");

    const std::filesystem::path config_path = config_dir / "runtime.yaml";
    context.expect(write_text_file(config_path, valid_yaml()),
                   "valid config setup",
                   "could not write YAML");

    const std::filesystem::path relative_config_path =
        std::filesystem::relative(config_path, std::filesystem::current_path(), error);
    context.expect(!error && !relative_config_path.empty(),
                   "relative config path setup",
                   "could not derive CWD-relative config path");

    runtime::RuntimeConfig config;
    const core::Status status =
        runtime::RuntimeConfigLoader::load(relative_config_path, &config);
    context.expect(status.ok(), "valid config", status.message());
    if (!status.ok()) {
        return;
    }

    const std::filesystem::path expected_root = options.temp_dir;
    context.expect(config.schema_version == 1, "valid config", "schema version mismatch");
    context.expect(config.backend_type == "onnxruntime_cpu",
                   "valid config",
                   "backend mismatch");
    context.expect(config.input_type == "directory", "valid config", "input type mismatch");
    context.expect(config.model_contract_path == expected_root / "contracts/frozen.yaml",
                   "relative path resolution",
                   "contract path must resolve relative to config directory");
    context.expect(config.model_path == expected_root / "models/frozen.onnx",
                   "relative path resolution",
                   "model path must resolve relative to config directory");
    context.expect(config.input_directory == expected_root / "images",
                   "relative path resolution",
                   "input path must resolve relative to config directory");
    context.expect(config.output_json_path == expected_root / "results/serial.json",
                   "relative path resolution",
                   "output path must resolve relative to config directory");
    context.expect(config.output_console && !config.output_overwrite && config.timing_enabled,
                   "valid config",
                   "boolean fields mismatch");
    context.expect(config.postprocess_config.confidence_threshold == 0.25F &&
                       config.postprocess_config.iou_threshold == 0.45F &&
                       config.postprocess_config.max_nms == 30000U &&
                       config.postprocess_config.max_det == 300U &&
                       config.postprocess_config.max_wh == 7680.0F &&
                       !config.postprocess_config.agnostic &&
                       !config.postprocess_config.multi_label,
                   "valid config",
                   "postprocess fields mismatch");
}

void test_schema_failures(TestContext& context, const Options& options) {
    expect_failure(context,
                   options,
                   "missing_section",
                   replace_to_end(valid_yaml(), "timing:\n", ""),
                   "timing");
    expect_failure(context,
                   options,
                   "missing_key",
                   replace_once(valid_yaml(), "  overwrite: false\n", ""),
                   "output.overwrite");
    expect_failure(context,
                   options,
                   "unknown_key",
                   replace_once(valid_yaml(),
                                "timing:\n",
                                "unexpected: true\ntiming:\n"),
                   "$.unexpected");
    expect_failure(context,
                   options,
                   "duplicate_key",
                   replace_once(valid_yaml(),
                                "schema_version: 1\n",
                                "schema_version: 1\nschema_version: 1\n"),
                   "$.schema_version");
    expect_failure(context,
                   options,
                   "wrong_type",
                   replace_once(valid_yaml(),
                                "output:\n"
                                "  json_path: ../results/serial.json\n"
                                "  console: true\n"
                                "  overwrite: false\n",
                                "output: false\n"),
                   "output");
    expect_failure(context,
                   options,
                   "invalid_schema_version",
                   replace_once(valid_yaml(), "schema_version: 1", "schema_version: 2"),
                   "schema_version");
    expect_failure(context,
                   options,
                   "invalid_backend_type",
                   replace_once(valid_yaml(), "type: onnxruntime_cpu", "type: tensorrt"),
                   "backend.type");
    expect_failure(context,
                   options,
                   "invalid_input_type",
                   replace_once(valid_yaml(), "  type: directory", "  type: video"),
                   "input.type");
    expect_failure(context,
                   options,
                   "empty_path",
                   replace_once(valid_yaml(),
                                "  model_path: ../models/frozen.onnx",
                                "  model_path: \"\""),
                   "model.model_path");
    expect_failure(context,
                   options,
                   "invalid_postprocess",
                   replace_once(valid_yaml(),
                                "  confidence_threshold: 0.25",
                                "  confidence_threshold: 1.5"),
                   "postprocess");
    expect_failure(context,
                   options,
                   "negative_postprocess_limit",
                   replace_once(valid_yaml(), "  max_nms: 30000", "  max_nms: -1"),
                   "postprocess");
    expect_failure(context,
                   options,
                   "timing_wrong_type",
                   replace_once(valid_yaml(), "  enabled: true", "  enabled: []"),
                   "timing.enabled");
}

void test_loader_argument_failures(TestContext& context, const Options& options) {
    runtime::RuntimeConfig output = sentinel_config();
    const runtime::RuntimeConfig sentinel = output;
    const core::Status empty_path = runtime::RuntimeConfigLoader::load({}, &output);
    context.expect(!empty_path.ok(), "empty config path", "load must fail");
    context.expect(empty_path.code() == core::ErrorCode::kInvalidArgument,
                   "empty config path",
                   "unexpected ErrorCode");
    context.expect(config_equal(output, sentinel),
                   "empty config path",
                   "failure must preserve output");

    const core::Status null_output = runtime::RuntimeConfigLoader::load(
        options.temp_dir / "missing.yaml", nullptr);
    context.expect(!null_output.ok(), "null output", "load must fail");
    context.expect(null_output.code() == core::ErrorCode::kInvalidArgument,
                   "null output",
                   "unexpected ErrorCode");

    const core::Status unreadable = runtime::RuntimeConfigLoader::load(
        options.temp_dir / "missing.yaml", &output);
    context.expect(!unreadable.ok(), "missing file", "load must fail");
    context.expect(unreadable.code() == core::ErrorCode::kIoError,
                   "missing file",
                   "unexpected ErrorCode");
    context.expect(config_equal(output, sentinel),
                   "missing file",
                   "failure must preserve output");
}

}  // namespace

int main(int argc, char* argv[]) {
    Options options;
    if (!parse_options(argc, argv, &options)) {
        return 2;
    }

    std::error_code error;
    std::filesystem::remove_all(options.temp_dir, error);
    if (error) {
        std::cerr << "Could not clear test directory: " << error.message() << '\n';
        return 2;
    }
    std::filesystem::create_directories(options.temp_dir, error);
    if (error) {
        std::cerr << "Could not create test directory: " << error.message() << '\n';
        return 2;
    }

    TestContext context;
    test_valid_config_and_paths(context, options);
    test_schema_failures(context, options);
    test_loader_argument_failures(context, options);

    std::filesystem::remove_all(options.temp_dir, error);
    if (error) {
        std::cerr << "Could not clean test directory: " << error.message() << '\n';
        return 2;
    }

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " runtime config test(s) failed\n";
        return 1;
    }

    std::cout << "All runtime config tests passed\n";
    return 0;
}
