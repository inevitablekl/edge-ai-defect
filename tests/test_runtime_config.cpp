#include "edge_ai_defect/backend_ort/onnx_runtime_options.hpp"
#include "edge_ai_defect/runtime/opencv_thread_policy.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <opencv2/core.hpp>
#include <onnxruntime_cxx_api.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>

namespace {

namespace core = edge_ai_defect::core;
namespace backend_ort = edge_ai_defect::backend_ort;
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

std::string valid_yaml_v2() {
    return R"yaml(schema_version: 2

backend:
  type: onnxruntime_cpu

onnxruntime:
  execution_mode: sequential
  graph_optimization_level: all
  intra_op_threads: 1
  inter_op_threads: 1
  intra_op_allow_spinning: true
  inter_op_allow_spinning: true
  cpu_arena_enabled: true
  memory_pattern_enabled: true

runtime:
  opencv_num_threads: 1

model:
  path: ../models/frozen.onnx
  contract_path: ../contracts/frozen.yaml

input:
  type: directory
  directory: ../images

output:
  json_path: ../results/serial.json
  console: true
  overwrite: false

postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_det: 300
  max_nms: 30000
  max_wh: 7680.0
  agnostic: false
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

void test_v2_config_and_isolation(TestContext& context, const Options& options) {
    const std::filesystem::path config_dir = options.temp_dir / "configs_v2";
    std::error_code error;
    std::filesystem::create_directories(config_dir, error);
    context.expect(!error,
                   "v2 valid config setup",
                   "could not create config directory");
    const std::filesystem::path config_path = config_dir / "runtime_v2.yaml";
    context.expect(write_text_file(config_path, valid_yaml_v2()),
                   "v2 valid config setup",
                   "could not write YAML");

    runtime::RuntimeConfig config;
    const core::Status status = runtime::RuntimeConfigLoader::load(config_path, &config);
    context.expect(status.ok(), "v2 valid config", status.message());
    if (status.ok()) {
        context.expect(config.schema_version == 2,
                       "v2 valid config",
                       "schema version mismatch");
        context.expect(config.model_path == options.temp_dir / "models/frozen.onnx",
                       "v2 model path",
                       "model.path must resolve relative to config directory");
        context.expect(config.onnxruntime.execution_mode == "sequential" &&
                           config.onnxruntime.graph_optimization_level == "all" &&
                           config.onnxruntime.intra_op_threads == 1U &&
                           config.onnxruntime.inter_op_threads == 1U &&
                           config.onnxruntime.intra_op_allow_spinning &&
                           config.onnxruntime.inter_op_allow_spinning &&
                           config.onnxruntime.cpu_arena_enabled &&
                           config.onnxruntime.memory_pattern_enabled,
                       "v2 onnxruntime options",
                       "ORT options mismatch");
        context.expect(config.opencv_num_threads == 1U,
                       "v2 runtime options",
                       "OpenCV thread count mismatch");
        context.expect(config.postprocess_config.confidence_threshold == 0.25F &&
                           config.postprocess_config.max_det == 300U &&
                           config.postprocess_config.max_nms == 30000U,
                       "v2 postprocess options",
                       "postprocess fields mismatch");
    }

    expect_failure(context,
                   options,
                   "v2_rejects_v1_timing",
                   valid_yaml_v2() + "\ntiming:\n  enabled: true\n",
                   "$.timing");
    expect_failure(context,
                   options,
                   "v2_rejects_v1_postprocess_name",
                   replace_once(valid_yaml_v2(),
                                "  conf_threshold: 0.25",
                                "  confidence_threshold: 0.25"),
                   "postprocess.confidence_threshold");
    expect_failure(context,
                   options,
                   "v1_rejects_v2_onnxruntime",
                   replace_once(valid_yaml(),
                                "model:\n",
                                "onnxruntime:\n  execution_mode: sequential\nmodel:\n"),
                   "$.onnxruntime");
    expect_failure(context,
                   options,
                   "v1_rejects_schema_v2_without_v2_fields",
                   replace_once(valid_yaml(), "schema_version: 1", "schema_version: 2"),
                   "$.timing");
    expect_failure(context,
                   options,
                   "v2_missing_required_field",
                   replace_once(valid_yaml_v2(),
                                "  memory_pattern_enabled: true\n",
                                ""),
                   "onnxruntime.memory_pattern_enabled");
}

void test_ort_options_record(TestContext& context) {
    runtime::RuntimeConfig config;
    config.schema_version = 2;
    config.backend_type = "onnxruntime_cpu";

    std::unique_ptr<const backend_ort::OrtOptionsRecord> record;
    const core::Status record_status =
        backend_ort::OrtOptionsRecord::create(config, &record);
    context.expect(record_status.ok(),
                   "ORT options default record",
                   record_status.message());
    if (!record_status.ok()) {
        return;
    }

    context.expect(record->schema_version() == 2U &&
                       record->backend_type() == "onnxruntime_cpu" &&
                       record->execution_mode() == "sequential" &&
                       record->graph_optimization_level() == "all" &&
                       record->intra_op_threads() == 1U &&
                       record->inter_op_threads() == 1U &&
                       record->intra_op_allow_spinning() &&
                       record->inter_op_allow_spinning() &&
                       record->cpu_arena_enabled() &&
                       record->memory_pattern_enabled(),
                   "ORT options default values",
                   "default option values mismatch");

    const std::string expected_record =
        "{\"schema_version\":2,\"backend_type\":\"onnxruntime_cpu\","
        "\"execution_mode\":\"sequential\",\"graph_optimization_level\":\"all\","
        "\"intra_op_threads\":1,\"inter_op_threads\":1,"
        "\"intra_op_allow_spinning\":true,\"inter_op_allow_spinning\":true,"
        "\"cpu_arena_enabled\":true,\"memory_pattern_enabled\":true}";
    context.expect(record->canonical_json() == expected_record,
                   "ORT options stable record",
                   "canonical record output changed");

    Ort::SessionOptions session_options;
    std::unique_ptr<const backend_ort::OrtOptionsRecord> applied_record;
    const core::Status apply_status = backend_ort::apply_ort_options(
        config, &session_options, &applied_record);
    context.expect(apply_status.ok(),
                   "ORT options application",
                   apply_status.message());
    context.expect(applied_record != nullptr &&
                       applied_record->canonical_json() == expected_record,
                   "ORT options applied record",
                   "applied record mismatch");

    runtime::RuntimeConfig invalid = config;
    invalid.schema_version = 1;
    std::unique_ptr<const backend_ort::OrtOptionsRecord> rejected;
    context.expect(!backend_ort::OrtOptionsRecord::create(invalid, &rejected).ok(),
                   "ORT options invalid schema",
                   "schema v1 must be rejected");
    invalid = config;
    invalid.onnxruntime.execution_mode = "parallel";
    context.expect(!backend_ort::OrtOptionsRecord::create(invalid, &rejected).ok(),
                   "ORT options invalid execution mode",
                   "unsupported execution mode must be rejected");
    invalid = config;
    invalid.onnxruntime.intra_op_threads = 0;
    context.expect(!backend_ort::OrtOptionsRecord::create(invalid, &rejected).ok(),
                   "ORT options invalid thread count",
                   "zero thread count must be rejected");
}

void test_opencv_thread_policy(TestContext& context) {
    const int previous_threads = cv::getNumThreads();
    runtime::RuntimeConfig config;
    config.schema_version = 2;
    config.opencv_num_threads = 1;

    std::unique_ptr<const runtime::OpenCvThreadPolicyRecord> record;
    const core::Status status =
        runtime::OpenCvThreadPolicyRecord::apply(config, &record);
    context.expect(status.ok(), "OpenCV policy mapping", status.message());
    if (status.ok()) {
        context.expect(record->requested_threads() == 1U &&
                           record->applied_threads() == 1U &&
                           record->opencv_version() == CV_VERSION &&
                           record->policy_active(),
                       "OpenCV policy record",
                       "requested/applied/version/active mismatch");
        const std::string expected =
            "{\"requested_threads\":1,\"applied_threads\":1,\"opencv_version\":\"" +
            std::string(CV_VERSION) + "\",\"policy_active\":true}";
        context.expect(record->canonical_json() == expected,
                       "OpenCV policy stable output",
                       "canonical policy record changed");
        context.expect(cv::getNumThreads() == 1,
                       "OpenCV policy application",
                       "cv::getNumThreads did not report requested value");
    }

    runtime::RuntimeConfig invalid = config;
    invalid.schema_version = 1;
    std::unique_ptr<const runtime::OpenCvThreadPolicyRecord> rejected;
    context.expect(!runtime::OpenCvThreadPolicyRecord::apply(invalid, &rejected).ok(),
                   "OpenCV policy invalid schema",
                   "schema v1 must be rejected");
    invalid = config;
    invalid.opencv_num_threads = 0;
    context.expect(!runtime::OpenCvThreadPolicyRecord::apply(invalid, &rejected).ok(),
                   "OpenCV policy invalid thread count",
                   "zero thread count must be rejected");

    cv::setNumThreads(previous_threads);
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
                   replace_once(valid_yaml(), "schema_version: 1", "schema_version: 3"),
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
    test_v2_config_and_isolation(context, options);
    test_ort_options_record(context);
    test_opencv_thread_policy(context);
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
