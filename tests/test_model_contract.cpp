#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/model/model_contract.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

static_assert(__cplusplus == 201703L, "The project must compile as C++17");

namespace {

namespace core = edge_ai_defect::core;
namespace model = edge_ai_defect::model;

constexpr std::size_t kExpectedCaseCount = 43;

class TestContext {
public:
    void begin_case(const std::string& case_name) {
        ++case_count_;
        current_case_ = case_name;
    }

    void expect(bool condition, const std::string& detail) {
        if (!condition) {
            ++failure_count_;
            std::cerr << "FAILED: " << current_case_ << ": " << detail
                      << '\n';
        }
    }

    [[nodiscard]] std::size_t case_count() const noexcept {
        return case_count_;
    }

    [[nodiscard]] int failure_count() const noexcept {
        return failure_count_;
    }

private:
    std::string current_case_;
    std::size_t case_count_ = 0;
    int failure_count_ = 0;
};

struct Options {
    std::filesystem::path contract_path;
    std::filesystem::path temp_dir;
};

bool parse_options(int argc, char* argv[], Options& options) {
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        if (argument == "--contract" && index + 1 < argc) {
            options.contract_path = argv[++index];
        } else if (argument == "--temp-dir" && index + 1 < argc) {
            options.temp_dir = argv[++index];
        } else {
            std::cerr << "Unknown or incomplete argument: " << argument
                      << '\n';
            return false;
        }
    }

    if (options.contract_path.empty() || options.temp_dir.empty()) {
        std::cerr << "Usage: test_model_contract --contract <path> "
                     "--temp-dir <path>\n";
        return false;
    }
    return true;
}

std::string valid_contract_yaml() {
    return R"yaml(schema_version: 1

model:
  id: yolov8n_neudet_frozen
  format: onnx
  sha256: c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
  size_bytes: 12242487

input:
  name: images
  dtype: float32
  layout: NCHW
  shape: [1, 3, 640, 640]

output:
  name: output0
  dtype: float32
  layout: BCN
  shape: [1, 10, 8400]

classes:
  count: 6
  names:
    - crazing
    - inclusion
    - patches
    - pitted_surface
    - rolled-in_scale
    - scratches
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

bool equal_tensor_contract(const model::TensorContract& left,
                           const model::TensorContract& right) {
    return left.name == right.name &&
        left.tensor_info.dtype == right.tensor_info.dtype &&
        left.tensor_info.layout == right.tensor_info.layout &&
        left.tensor_info.shape == right.tensor_info.shape;
}

bool equal_model_contract(const model::ModelContract& left,
                          const model::ModelContract& right) {
    return left.schema_version == right.schema_version &&
        left.model_id == right.model_id && left.format == right.format &&
        left.expected_onnx_sha256 == right.expected_onnx_sha256 &&
        left.expected_onnx_size_bytes == right.expected_onnx_size_bytes &&
        equal_tensor_contract(left.input, right.input) &&
        equal_tensor_contract(left.output, right.output) &&
        left.class_names == right.class_names;
}

model::ModelContract load_formal_contract(TestContext& context,
                                          const Options& options) {
    model::ModelContract contract;
    const core::Status status =
        model::ModelContractLoader::load(options.contract_path, &contract);
    context.expect(status.ok(),
                   "formal contract load failed: " + status.message());
    return contract;
}

void expect_yaml_failure(TestContext& context,
                         const Options& options,
                         const std::string& case_name,
                         const std::string& yaml,
                         core::ErrorCode expected_code,
                         const std::string& expected_path) {
    context.begin_case(case_name);
    const std::filesystem::path path =
        options.temp_dir /
        ("invalid_" + std::to_string(context.case_count()) + ".yaml");
    context.expect(write_text_file(path, yaml),
                   "could not write temporary YAML");

    model::ModelContract contract;
    bool exception_escaped = false;
    core::Status status = core::Status::success();
    try {
        status = model::ModelContractLoader::load(path, &contract);
    } catch (...) {
        exception_escaped = true;
    }

    context.expect(!exception_escaped,
                   "loader allowed an exception to cross its boundary");
    context.expect(!status.ok(), "load must fail");
    context.expect(status.code() == expected_code, "unexpected ErrorCode");
    context.expect(status.message().find(expected_path) != std::string::npos,
                   "message must contain field path '" + expected_path +
                       "', got '" + status.message() + "'");
}

void test_formal_contract(TestContext& context, const Options& options) {
    context.begin_case("formal YAML loads");
    const model::ModelContract loaded = load_formal_contract(context, options);

    context.begin_case("schema version");
    const model::ModelContract schema = load_formal_contract(context, options);
    context.expect(schema.schema_version == 1,
                   "schema_version must equal 1");

    context.begin_case("model identity and provenance");
    const model::ModelContract model_fields =
        load_formal_contract(context, options);
    context.expect(model_fields.model_id == "yolov8n_neudet_frozen",
                   "unexpected model id");
    context.expect(model_fields.format == "onnx", "unexpected model format");
    context.expect(
        model_fields.expected_onnx_sha256 ==
            "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944",
        "unexpected model SHA256");
    context.expect(model_fields.expected_onnx_size_bytes == 12242487,
                   "unexpected model size");

    context.begin_case("input tensor contract");
    const model::ModelContract input = load_formal_contract(context, options);
    context.expect(input.input.name == "images", "unexpected input name");
    context.expect(input.input.tensor_info.dtype ==
                       core::TensorDataType::kFloat32,
                   "unexpected input dtype");
    context.expect(input.input.tensor_info.layout ==
                       core::TensorLayout::kNchw,
                   "unexpected input layout");
    context.expect(input.input.tensor_info.shape ==
                       std::vector<std::int64_t>({1, 3, 640, 640}),
                   "unexpected input shape");

    context.begin_case("output tensor contract");
    const model::ModelContract output = load_formal_contract(context, options);
    context.expect(output.output.name == "output0", "unexpected output name");
    context.expect(output.output.tensor_info.dtype ==
                       core::TensorDataType::kFloat32,
                   "unexpected output dtype");
    context.expect(output.output.tensor_info.layout ==
                       core::TensorLayout::kBcn,
                   "unexpected output layout");
    context.expect(output.output.tensor_info.shape ==
                       std::vector<std::int64_t>({1, 10, 8400}),
                   "unexpected output shape");

    context.begin_case("ordered class names");
    const model::ModelContract classes = load_formal_contract(context, options);
    const std::vector<std::string> expected_classes = {
        "crazing",
        "inclusion",
        "patches",
        "pitted_surface",
        "rolled-in_scale",
        "scratches",
    };
    context.expect(classes.class_names == expected_classes,
                   "class count or order differs from frozen contract");

    context.begin_case("frozen tensor element counts");
    const model::ModelContract tensors = load_formal_contract(context, options);
    std::size_t input_elements = 0;
    std::size_t output_elements = 0;
    const core::Status input_status = core::checked_element_count(
        tensors.input.tensor_info.shape, input_elements);
    const core::Status output_status = core::checked_element_count(
        tensors.output.tensor_info.shape, output_elements);
    context.expect(input_status.ok() && input_elements == 1228800,
                   "input element count must equal 1228800");
    context.expect(output_status.ok() && output_elements == 84000,
                   "output element count must equal 84000");

    (void)loaded;
}

void test_public_api(TestContext& context, const Options& options) {
    context.begin_case("null output pointer");
    const core::Status null_status =
        model::ModelContractLoader::load(options.contract_path, nullptr);
    context.expect(!null_status.ok(), "load must fail");
    context.expect(null_status.code() == core::ErrorCode::kInvalidArgument,
                   "expected kInvalidArgument");
    context.expect(null_status.message().find("output") != std::string::npos,
                   "message must contain output field path");

    context.begin_case("failed load preserves output");
    const model::ModelContract sentinel{
        99,
        "sentinel-model",
        "sentinel-format",
        "sentinel-sha",
        42,
        {"sentinel-input",
         {core::TensorDataType::kFloat32,
          core::TensorLayout::kNchw,
          {1, 1, 1, 1}}},
        {"sentinel-output",
         {core::TensorDataType::kFloat32,
          core::TensorLayout::kBcn,
          {1, 1, 1}}},
        {"sentinel-class"},
    };
    model::ModelContract actual = sentinel;
    const std::filesystem::path invalid_path =
        options.temp_dir / "atomic_update.yaml";
    context.expect(write_text_file(
                       invalid_path,
                       replace_once(valid_contract_yaml(),
                                    "  format: onnx\n",
                                    "  format: invalid\n")),
                   "could not write temporary YAML");
    const core::Status status =
        model::ModelContractLoader::load(invalid_path, &actual);
    context.expect(!status.ok(), "load must fail");
    context.expect(equal_model_contract(actual, sentinel),
                   "output changed despite failed validation");
}

void test_negative_cases(TestContext& context, const Options& options) {
    context.begin_case("nonexistent contract file");
    const std::filesystem::path missing = options.temp_dir / "missing.yaml";
    std::error_code remove_error;
    std::filesystem::remove(missing, remove_error);
    model::ModelContract contract;
    const core::Status missing_status =
        model::ModelContractLoader::load(missing, &contract);
    context.expect(!missing_status.ok(), "load must fail");
    context.expect(missing_status.code() == core::ErrorCode::kIoError,
                   "expected kIoError");
    context.expect(missing_status.message().find(missing.string()) !=
                       std::string::npos,
                   "message must contain the missing file path");

    expect_yaml_failure(context,
                        options,
                        "YAML syntax error",
                        "schema_version: [1\n",
                        core::ErrorCode::kParseError,
                        "$");
    expect_yaml_failure(context,
                        options,
                        "root is not mapping",
                        "- schema_version\n",
                        core::ErrorCode::kSchemaViolation,
                        "$");
    expect_yaml_failure(
        context,
        options,
        "missing required field",
        replace_once(valid_contract_yaml(),
                     "  id: yolov8n_neudet_frozen\n",
                     ""),
        core::ErrorCode::kSchemaViolation,
        "model.id");
    expect_yaml_failure(context,
                        options,
                        "unknown top-level field",
                        valid_contract_yaml() + "unexpected: true\n",
                        core::ErrorCode::kSchemaViolation,
                        "$.unexpected");
    expect_yaml_failure(
        context,
        options,
        "unknown nested field",
        replace_once(valid_contract_yaml(),
                     "model:\n",
                     "model:\n  unexpected: true\n"),
        core::ErrorCode::kSchemaViolation,
        "model.unexpected");
    expect_yaml_failure(context,
                        options,
                        "duplicate key",
                        "schema_version: 1\n" + valid_contract_yaml(),
                        core::ErrorCode::kSchemaViolation,
                        "$.schema_version");
    expect_yaml_failure(
        context,
        options,
        "unsupported schema version",
        replace_once(valid_contract_yaml(),
                     "schema_version: 1\n",
                     "schema_version: 2\n"),
        core::ErrorCode::kSchemaViolation,
        "schema_version");
    expect_yaml_failure(context,
                        options,
                        "invalid model format",
                        replace_once(valid_contract_yaml(),
                                     "  format: onnx\n",
                                     "  format: plan\n"),
                        core::ErrorCode::kSchemaViolation,
                        "model.format");
    expect_yaml_failure(
        context,
        options,
        "SHA256 wrong length",
        replace_once(
            valid_contract_yaml(),
            "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944",
            "c88ac014"),
        core::ErrorCode::kSchemaViolation,
        "model.sha256");
    expect_yaml_failure(
        context,
        options,
        "SHA256 non-lowercase-hex character",
        replace_once(
            valid_contract_yaml(),
            "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944",
            "C88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944"),
        core::ErrorCode::kSchemaViolation,
        "model.sha256");
    expect_yaml_failure(context,
                        options,
                        "zero model size",
                        replace_once(valid_contract_yaml(),
                                     "  size_bytes: 12242487\n",
                                     "  size_bytes: 0\n"),
                        core::ErrorCode::kSchemaViolation,
                        "model.size_bytes");
    expect_yaml_failure(context,
                        options,
                        "negative model size",
                        replace_once(valid_contract_yaml(),
                                     "  size_bytes: 12242487\n",
                                     "  size_bytes: -1\n"),
                        core::ErrorCode::kSchemaViolation,
                        "model.size_bytes");
    expect_yaml_failure(context,
                        options,
                        "unsupported dtype",
                        replace_once(valid_contract_yaml(),
                                     "  dtype: float32\n",
                                     "  dtype: float16\n"),
                        core::ErrorCode::kUnsupportedDataType,
                        "input.dtype");
    expect_yaml_failure(context,
                        options,
                        "unsupported layout",
                        replace_once(valid_contract_yaml(),
                                     "  layout: NCHW\n",
                                     "  layout: nchw\n"),
                        core::ErrorCode::kUnsupportedLayout,
                        "input.layout");
    expect_yaml_failure(context,
                        options,
                        "shape is not sequence",
                        replace_once(valid_contract_yaml(),
                                     "  shape: [1, 3, 640, 640]\n",
                                     "  shape: invalid\n"),
                        core::ErrorCode::kInvalidShape,
                        "input.shape");
    expect_yaml_failure(context,
                        options,
                        "shape is empty",
                        replace_once(valid_contract_yaml(),
                                     "  shape: [1, 3, 640, 640]\n",
                                     "  shape: []\n"),
                        core::ErrorCode::kInvalidShape,
                        "input.shape");
    expect_yaml_failure(context,
                        options,
                        "shape has non-integer",
                        replace_once(valid_contract_yaml(),
                                     "  shape: [1, 3, 640, 640]\n",
                                     "  shape: [1, nope, 640, 640]\n"),
                        core::ErrorCode::kParseError,
                        "input.shape[1]");
    expect_yaml_failure(context,
                        options,
                        "shape has zero dimension",
                        replace_once(valid_contract_yaml(),
                                     "  shape: [1, 3, 640, 640]\n",
                                     "  shape: [1, 0, 640, 640]\n"),
                        core::ErrorCode::kInvalidShape,
                        "input.shape[1]");
    expect_yaml_failure(context,
                        options,
                        "shape has negative dimension",
                        replace_once(valid_contract_yaml(),
                                     "  shape: [1, 3, 640, 640]\n",
                                     "  shape: [1, -1, 640, 640]\n"),
                        core::ErrorCode::kInvalidShape,
                        "input.shape[1]");
    expect_yaml_failure(
        context,
        options,
        "shape element count overflows",
        replace_once(valid_contract_yaml(),
                     "  shape: [1, 3, 640, 640]\n",
                     "  shape: [9223372036854775807, 3]\n"),
        core::ErrorCode::kOverflow,
        "input.shape");
    expect_yaml_failure(context,
                        options,
                        "class count mismatch",
                        replace_once(valid_contract_yaml(),
                                     "  count: 6\n",
                                     "  count: 5\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.count");
    expect_yaml_failure(context,
                        options,
                        "empty class name",
                        replace_once(valid_contract_yaml(),
                                     "    - crazing\n",
                                     "    - \"\"\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.names[0]");
    expect_yaml_failure(context,
                        options,
                        "duplicate class name",
                        replace_once(valid_contract_yaml(),
                                     "    - scratches\n",
                                     "    - crazing\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.names[5]");
    expect_yaml_failure(context,
                        options,
                        "class names is not sequence",
                        replace_to_end(valid_contract_yaml(),
                                       "  names:\n",
                                       "  names: crazing\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.names");

    const std::string model_not_mapping = replace_once(
        valid_contract_yaml(),
        valid_contract_yaml().substr(
            valid_contract_yaml().find("model:\n"),
            valid_contract_yaml().find("input:\n") -
                valid_contract_yaml().find("model:\n")),
        "model: onnx\n\n");
    expect_yaml_failure(context,
                        options,
                        "model is not mapping",
                        model_not_mapping,
                        core::ErrorCode::kSchemaViolation,
                        "model");
    expect_yaml_failure(context,
                        options,
                        "tensor name is not scalar",
                        replace_once(valid_contract_yaml(),
                                     "  name: images\n",
                                     "  name: [images]\n"),
                        core::ErrorCode::kSchemaViolation,
                        "input.name");
    expect_yaml_failure(context,
                        options,
                        "class count scalar conversion",
                        replace_once(valid_contract_yaml(),
                                     "  count: 6\n",
                                     "  count: many\n"),
                        core::ErrorCode::kParseError,
                        "classes.count");
    expect_yaml_failure(context,
                        options,
                        "class name is not scalar",
                        replace_once(valid_contract_yaml(),
                                     "    - crazing\n",
                                     "    - [crazing]\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.names[0]");
    expect_yaml_failure(context,
                        options,
                        "empty model id",
                        replace_once(valid_contract_yaml(),
                                     "  id: yolov8n_neudet_frozen\n",
                                     "  id: \"\"\n"),
                        core::ErrorCode::kSchemaViolation,
                        "model.id");
    expect_yaml_failure(context,
                        options,
                        "empty input name",
                        replace_once(valid_contract_yaml(),
                                     "  name: images\n",
                                     "  name: \"\"\n"),
                        core::ErrorCode::kSchemaViolation,
                        "input.name");
    expect_yaml_failure(context,
                        options,
                        "empty output name",
                        replace_once(valid_contract_yaml(),
                                     "  name: output0\n",
                                     "  name: \"\"\n"),
                        core::ErrorCode::kSchemaViolation,
                        "output.name");
    expect_yaml_failure(context,
                        options,
                        "zero class count",
                        replace_once(valid_contract_yaml(),
                                     "  count: 6\n",
                                     "  count: 0\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.count");
    expect_yaml_failure(context,
                        options,
                        "negative class count",
                        replace_once(valid_contract_yaml(),
                                     "  count: 6\n",
                                     "  count: -1\n"),
                        core::ErrorCode::kSchemaViolation,
                        "classes.count");
}

}  // namespace

int main(int argc, char* argv[]) {
    Options options;
    if (!parse_options(argc, argv, options)) {
        return 2;
    }

    std::error_code filesystem_error;
    std::filesystem::remove_all(options.temp_dir, filesystem_error);
    filesystem_error.clear();
    std::filesystem::create_directories(options.temp_dir, filesystem_error);
    if (filesystem_error) {
        std::cerr << "Could not create temporary directory: "
                  << filesystem_error.message() << '\n';
        return 2;
    }

    TestContext context;
    test_formal_contract(context, options);
    test_public_api(context, options);
    test_negative_cases(context, options);
    context.expect(context.case_count() == kExpectedCaseCount,
                   "unexpected model contract case count");

    std::filesystem::remove_all(options.temp_dir, filesystem_error);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " assertion(s) failed across "
                  << context.case_count() << " model contract cases\n";
        return 1;
    }

    std::cout << "All " << context.case_count()
              << " model contract cases passed\n";
    return 0;
}
