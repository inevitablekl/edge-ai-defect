#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <openssl/evp.h>
#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>
#include <unistd.h>

namespace {

namespace core = edge_ai_defect::core;
namespace inference = edge_ai_defect::inference;
namespace model = edge_ai_defect::model;
namespace runtime = edge_ai_defect::runtime;
namespace fs = std::filesystem;

constexpr std::array<std::int64_t, 4> kInputShape{1, 3, 640, 640};
constexpr std::array<std::int64_t, 3> kOutputShape{1, 10, 8400};
constexpr std::size_t kInputElements = 1228800U;
constexpr std::size_t kOutputElements = 84000U;
constexpr std::size_t kInputBytes = kInputElements * sizeof(float);
constexpr std::size_t kOutputBytes = kOutputElements * sizeof(float);

struct InputEntry {
    std::string image_id;
    fs::path tensor_path;
    std::string tensor_path_text;
    std::string sha256;
    std::vector<std::int64_t> shape;
    std::string dtype;
    std::string byte_order;
    std::string layout;
    std::size_t element_count = 0;
    std::size_t byte_size = 0;
};

struct Options {
    fs::path config_path;
    fs::path input_manifest_path;
    fs::path output_dir;
    std::string run_id;
    std::string source_commit = "unknown";
    std::string executable_sha256;
    bool help = false;
};

core::Status failure(core::ErrorCode code, const std::string& message) {
    return core::Status::failure(code, message);
}

bool is_lowercase_sha256(const std::string& value) {
    if (value.size() != 64U) return false;
    return std::all_of(value.begin(), value.end(), [](unsigned char character) {
        return (character >= '0' && character <= '9') ||
               (character >= 'a' && character <= 'f');
    });
}

core::Status sha256_file(const fs::path& path, std::string* digest) {
    if (digest == nullptr) return failure(core::ErrorCode::kInvalidArgument, "digest is null");
    std::ifstream input(path, std::ios::binary);
    if (!input.is_open()) return failure(core::ErrorCode::kIoError, "cannot open file for SHA256: " + path.string());
    using Context = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    Context context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context || EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) != 1) {
        return failure(core::ErrorCode::kIoError, "cannot initialize SHA256 for: " + path.string());
    }
    std::array<char, 65536> buffer{};
    while (input.good()) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context.get(), buffer.data(), static_cast<std::size_t>(count)) != 1) {
            return failure(core::ErrorCode::kIoError, "cannot update SHA256 for: " + path.string());
        }
    }
    if (!input.eof()) return failure(core::ErrorCode::kIoError, "cannot read file for SHA256: " + path.string());
    std::array<unsigned char, EVP_MAX_MD_SIZE> raw{};
    unsigned int size = 0;
    if (EVP_DigestFinal_ex(context.get(), raw.data(), &size) != 1 || size != 32U) {
        return failure(core::ErrorCode::kIoError, "cannot finalize SHA256 for: " + path.string());
    }
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (unsigned int index = 0; index < size; ++index) output << std::setw(2) << static_cast<unsigned int>(raw[index]);
    *digest = output.str();
    return core::Status::success();
}

core::Status require_regular_file(const fs::path& path, const std::string& label) {
    std::error_code error;
    if (fs::is_symlink(path, error) || error || !fs::is_regular_file(path, error) || error) {
        return failure(core::ErrorCode::kIoError, label + " is not a regular file: " + path.string());
    }
    return core::Status::success();
}

core::Status require_new_directory(const fs::path& path) {
    std::error_code error;
    if (fs::exists(path, error) || error) {
        return failure(core::ErrorCode::kIoError, "output directory already exists or cannot be inspected: " + path.string());
    }
    if (!fs::create_directories(path, error) || error) {
        return failure(core::ErrorCode::kIoError, "cannot create output directory: " + path.string());
    }
    return core::Status::success();
}

std::string json_escape(const std::string& value) {
    std::ostringstream output;
    for (const unsigned char character : value) {
        switch (character) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (character < 0x20U) {
                    output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                           << static_cast<unsigned int>(character) << std::dec;
                } else {
                    output << static_cast<char>(character);
                }
        }
    }
    return output.str();
}

std::string json_string(const std::string& value) {
    return "\"" + json_escape(value) + "\"";
}

std::string shape_json(const std::vector<std::int64_t>& shape) {
    std::ostringstream output;
    output << '[';
    for (std::size_t index = 0; index < shape.size(); ++index) {
        if (index != 0U) output << ',';
        output << shape[index];
    }
    output << ']';
    return output.str();
}

bool little_endian_host() {
    const std::uint16_t value = 0x0001U;
    return *reinterpret_cast<const unsigned char*>(&value) == 0x01U;
}

template <typename T>
core::Status scalar(const YAML::Node& node, const std::string& path, T* output) {
    if (!node.IsScalar()) return failure(core::ErrorCode::kSchemaViolation, path + ": expected scalar");
    try {
        *output = node.as<T>();
    } catch (const YAML::Exception& exception) {
        return failure(core::ErrorCode::kParseError, path + ": " + exception.what());
    }
    return core::Status::success();
}

core::Status exact_string(const YAML::Node& node, const std::string& path,
                          const std::string& expected) {
    std::string value;
    const core::Status status = scalar(node, path, &value);
    if (!status.ok()) return status;
    if (value != expected) return failure(core::ErrorCode::kSchemaViolation, path + ": expected '" + expected + "'");
    return core::Status::success();
}

core::Status parse_shape(const YAML::Node& node, const std::string& path,
                         std::vector<std::int64_t>* output) {
    if (!node.IsSequence()) return failure(core::ErrorCode::kInvalidShape, path + ": expected sequence");
    std::vector<std::int64_t> value;
    for (std::size_t index = 0; index < node.size(); ++index) {
        std::int64_t dimension = 0;
        const core::Status status = scalar(node[index], path + "[" + std::to_string(index) + "]", &dimension);
        if (!status.ok()) return status;
        if (dimension <= 0) return failure(core::ErrorCode::kInvalidShape, path + ": dimensions must be positive");
        value.push_back(dimension);
    }
    *output = std::move(value);
    return core::Status::success();
}

bool same_shape(const std::vector<std::int64_t>& actual, const std::vector<std::int64_t>& expected) {
    return actual == expected;
}

core::Status parse_input_manifest(const fs::path& path, std::vector<InputEntry>* output) {
    if (output == nullptr) return failure(core::ErrorCode::kInvalidArgument, "input manifest output is null");
    std::ifstream input(path);
    if (!input.is_open()) return failure(core::ErrorCode::kIoError, "input manifest is not readable: " + path.string());
    try {
        const YAML::Node root = YAML::Load(input);
        if (!root.IsMap()) return failure(core::ErrorCode::kSchemaViolation, "input manifest root must be an object");
        std::int64_t version = 0;
        core::Status status = scalar(root["schema_version"], "schema_version", &version);
        if (!status.ok() || version != 1) return failure(core::ErrorCode::kSchemaViolation, "schema_version must be 1");
        status = exact_string(root["artifact_kind"], "artifact_kind", "stage_k_raw_tensor_input_manifest");
        if (!status.ok()) return status;
        status = exact_string(root["dtype"], "dtype", "float32");
        if (!status.ok()) return status;
        status = exact_string(root["byte_order"], "byte_order", "little_endian");
        if (!status.ok()) return status;
        status = exact_string(root["layout"], "layout", "NCHW");
        if (!status.ok()) return status;
        std::vector<std::int64_t> manifest_shape;
        status = parse_shape(root["shape"], "shape", &manifest_shape);
        const std::vector<std::int64_t> expected_shape(kInputShape.begin(), kInputShape.end());
        if (!status.ok() || !same_shape(manifest_shape, expected_shape)) {
            return failure(core::ErrorCode::kSchemaViolation, "input manifest shape must be [1,3,640,640]");
        }
        std::int64_t element_count = 0;
        status = scalar(root["element_count"], "element_count", &element_count);
        if (!status.ok() || element_count != static_cast<std::int64_t>(kInputElements)) return failure(core::ErrorCode::kDataSizeMismatch, "input manifest element_count must be 1228800");
        std::int64_t byte_size = 0;
        status = scalar(root["byte_size"], "byte_size", &byte_size);
        if (!status.ok() || byte_size != static_cast<std::int64_t>(kInputBytes)) return failure(core::ErrorCode::kDataSizeMismatch, "input manifest byte_size must be 4915200");
        const YAML::Node entries = root["entries"];
        if (!entries.IsSequence() || entries.size() == 0U) return failure(core::ErrorCode::kSchemaViolation, "entries must be a non-empty array");
        std::vector<InputEntry> parsed;
        parsed.reserve(entries.size());
        for (std::size_t index = 0; index < entries.size(); ++index) {
            const YAML::Node node = entries[index];
            if (!node.IsMap()) return failure(core::ErrorCode::kSchemaViolation, "entries[" + std::to_string(index) + "] must be an object");
            InputEntry entry;
            status = scalar(node["image_id"], "entries[" + std::to_string(index) + "].image_id", &entry.image_id);
            if (!status.ok() || entry.image_id.empty()) return failure(core::ErrorCode::kSchemaViolation, "entry image_id must not be empty");
            status = scalar(node["input_tensor_path"], "entries[" + std::to_string(index) + "].input_tensor_path", &entry.tensor_path_text);
            if (!status.ok() || entry.tensor_path_text.empty()) return failure(core::ErrorCode::kSchemaViolation, "entry input_tensor_path must not be empty");
            const fs::path raw_path(entry.tensor_path_text);
            entry.tensor_path = (raw_path.is_absolute() ? raw_path : path.parent_path() / raw_path).lexically_normal();
            status = scalar(node["input_sha256"], "entries[" + std::to_string(index) + "].input_sha256", &entry.sha256);
            if (!status.ok() || !is_lowercase_sha256(entry.sha256)) return failure(core::ErrorCode::kSchemaViolation, "entry input_sha256 must be lowercase SHA256");
            status = exact_string(node["dtype"], "entries[" + std::to_string(index) + "].dtype", "float32");
            if (!status.ok()) return status;
            status = exact_string(node["byte_order"], "entries[" + std::to_string(index) + "].byte_order", "little_endian");
            if (!status.ok()) return status;
            status = exact_string(node["layout"], "entries[" + std::to_string(index) + "].layout", "NCHW");
            if (!status.ok()) return status;
            status = parse_shape(node["shape"], "entries[" + std::to_string(index) + "].shape", &entry.shape);
            const std::vector<std::int64_t> expected_shape(kInputShape.begin(), kInputShape.end());
            if (!status.ok() || !same_shape(entry.shape, expected_shape)) return failure(core::ErrorCode::kInvalidShape, "entry shape must be [1,3,640,640]");
            std::int64_t entry_count = 0;
            status = scalar(node["element_count"], "entry element_count", &entry_count);
            if (!status.ok() || entry_count != static_cast<std::int64_t>(kInputElements)) return failure(core::ErrorCode::kDataSizeMismatch, "entry element_count must be 1228800");
            entry.element_count = kInputElements;
            std::int64_t entry_size = 0;
            status = scalar(node["byte_size"], "entry byte_size", &entry_size);
            if (!status.ok() || entry_size != static_cast<std::int64_t>(kInputBytes)) return failure(core::ErrorCode::kDataSizeMismatch, "entry byte_size must be 4915200");
            entry.byte_size = kInputBytes;
            parsed.push_back(std::move(entry));
        }
        std::sort(parsed.begin(), parsed.end(), [](const InputEntry& left, const InputEntry& right) { return left.image_id < right.image_id; });
        for (std::size_t index = 1; index < parsed.size(); ++index) {
            if (parsed[index - 1].image_id == parsed[index].image_id) return failure(core::ErrorCode::kSchemaViolation, "duplicate image_id: " + parsed[index].image_id);
        }
        *output = std::move(parsed);
        return core::Status::success();
    } catch (const YAML::Exception& exception) {
        return failure(core::ErrorCode::kParseError, "input manifest JSON/YAML parse error: " + std::string(exception.what()));
    }
}

core::Status read_input_tensor(const InputEntry& entry, core::HostTensor* output) {
    if (output == nullptr) return failure(core::ErrorCode::kInvalidArgument, "input tensor output is null");
    core::Status status = require_regular_file(entry.tensor_path, "input tensor");
    if (!status.ok()) return status;
    std::error_code error;
    const std::uintmax_t actual_size = fs::file_size(entry.tensor_path, error);
    if (error || actual_size != entry.byte_size) return failure(core::ErrorCode::kDataSizeMismatch, "input tensor exact byte-size mismatch: " + entry.tensor_path.string());
    std::string actual_sha;
    status = sha256_file(entry.tensor_path, &actual_sha);
    if (!status.ok() || actual_sha != entry.sha256) return failure(core::ErrorCode::kModelContractMismatch, "input tensor SHA256 mismatch: " + entry.tensor_path.string());
    std::ifstream input(entry.tensor_path, std::ios::binary);
    std::vector<unsigned char> bytes(entry.byte_size);
    input.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    if (!input || static_cast<std::size_t>(input.gcount()) != bytes.size()) return failure(core::ErrorCode::kIoError, "input tensor read was truncated: " + entry.tensor_path.string());
    std::vector<float> values(entry.element_count);
    std::memcpy(values.data(), bytes.data(), bytes.size());
    for (const float value : values) if (!std::isfinite(value)) return failure(core::ErrorCode::kInvalidArgument, "input tensor contains non-finite value: " + entry.image_id);
    core::HostTensor tensor;
    tensor.info.dtype = core::TensorDataType::kFloat32;
    tensor.info.layout = core::TensorLayout::kNchw;
    tensor.info.shape = entry.shape;
    tensor.data = std::move(values);
    *output = std::move(tensor);
    return core::Status::success();
}

core::Status write_atomic(const fs::path& path, const std::vector<float>& values) {
    if (values.size() != kOutputElements) return failure(core::ErrorCode::kDataSizeMismatch, "raw output size is not 84000 float32 values");
    const fs::path temporary = path.string() + ".tmp." + std::to_string(static_cast<long long>(::getpid()));
    {
        std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
        if (!output.is_open()) return failure(core::ErrorCode::kIoError, "cannot open temporary output: " + temporary.string());
        output.write(reinterpret_cast<const char*>(values.data()), static_cast<std::streamsize>(values.size() * sizeof(float)));
        output.flush();
        if (!output) return failure(core::ErrorCode::kIoError, "cannot write raw output: " + path.string());
    }
    std::error_code error;
    fs::rename(temporary, path, error);
    if (error) {
        fs::remove(temporary);
        return failure(core::ErrorCode::kIoError, "cannot atomically publish raw output: " + error.message());
    }
    return core::Status::success();
}

std::string timestamp_utc() {
    const auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::tm utc{};
    gmtime_r(&now, &utc);
    std::ostringstream output;
    output << std::put_time(&utc, "%Y-%m-%dT%H:%M:%SZ");
    return output.str();
}

struct OutputRecord {
    std::string image_id;
    std::string input_filename;
    std::string input_sha256;
    std::string output_filename;
    std::string output_sha256;
};

std::string output_manifest_json(const Options& options, const runtime::RuntimeConfig& config,
                                 const model::ModelContract& contract, const std::string& runtime_sha,
                                 const std::string& contract_sha, const std::string& model_sha,
                                 const std::string& engine_sha, const std::string& engine_manifest_sha,
                                 const std::string& input_manifest_sha,
                                 const std::vector<OutputRecord>& records) {
    std::ostringstream output;
    output << "{\n"
           << "  \"schema_version\": 1,\n"
           << "  \"artifact_kind\": \"stage_k_raw_tensor_output_manifest\",\n"
           << "  \"run_id\": " << json_string(options.run_id) << ",\n"
           << "  \"backend_type\": " << json_string(config.backend_type) << ",\n"
           << "  \"source_git_commit\": " << json_string(options.source_commit) << ",\n"
           << "  \"executable_sha256\": " << json_string(options.executable_sha256) << ",\n"
           << "  \"runtime_config_sha256\": " << json_string(runtime_sha) << ",\n"
           << "  \"model_contract_sha256\": " << json_string(contract_sha) << ",\n"
           << "  \"onnx_sha256\": " << (model_sha.empty() ? "null" : json_string(model_sha)) << ",\n"
           << "  \"engine_sha256\": " << (engine_sha.empty() ? "null" : json_string(engine_sha)) << ",\n"
           << "  \"engine_manifest_sha256\": " << (engine_manifest_sha.empty() ? "null" : json_string(engine_manifest_sha)) << ",\n"
           << "  \"input_manifest_sha256\": " << json_string(input_manifest_sha) << ",\n"
           << "  \"entry_count\": " << records.size() << ",\n"
           << "  \"success_count\": " << records.size() << ",\n"
           << "  \"failure_count\": 0,\n"
           << "  \"overall_status\": \"SUCCESS\",\n"
           << "  \"creation_timestamp\": " << json_string(timestamp_utc()) << ",\n"
           << "  \"tensor_contract\": {\"dtype\": \"float32\", \"byte_order\": \"little_endian\", \"layout\": \"BCN\", \"shape\": [1, 10, 8400], \"element_count\": 84000, \"byte_size\": 336000},\n"
           << "  \"limitations\": [\"non-formal tooling smoke only\", \"no preprocessing\", \"no postprocessing\"],\n"
           << "  \"entries\": [\n";
    for (std::size_t index = 0; index < records.size(); ++index) {
        const auto& record = records[index];
        output << "    {\n"
               << "      \"image_id\": " << json_string(record.image_id) << ",\n"
               << "      \"input_filename\": " << json_string(record.input_filename) << ",\n"
               << "      \"input_sha256\": " << json_string(record.input_sha256) << ",\n"
               << "      \"output_filename\": " << json_string(record.output_filename) << ",\n"
               << "      \"output_sha256\": " << json_string(record.output_sha256) << ",\n"
               << "      \"output_byte_size\": 336000,\n"
               << "      \"dtype\": \"float32\",\n"
               << "      \"byte_order\": \"little_endian\",\n"
               << "      \"layout\": \"BCN\",\n"
               << "      \"shape\": [1, 10, 8400],\n"
               << "      \"element_count\": 84000,\n"
               << "      \"finite_count\": 84000,\n"
               << "      \"backend_type\": " << json_string(config.backend_type) << ",\n"
               << "      \"status\": \"success\"\n"
               << "    }" << (index + 1U == records.size() ? "\n" : ",\n");
    }
    output << "  ]\n}\n";
    (void)contract;
    return output.str();
}

core::Status publish_manifest(const fs::path& path, const std::string& content) {
    const fs::path temporary = path.string() + ".tmp." + std::to_string(static_cast<long long>(::getpid()));
    {
        std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
        if (!output.is_open()) return failure(core::ErrorCode::kIoError, "cannot open temporary output manifest");
        output << content;
        output.flush();
        if (!output) return failure(core::ErrorCode::kIoError, "cannot write output manifest");
    }
    std::error_code error;
    fs::rename(temporary, path, error);
    if (error) {
        fs::remove(temporary);
        return failure(core::ErrorCode::kIoError, "cannot atomically publish output manifest: " + error.message());
    }
    return core::Status::success();
}

core::Status parse_options(int argc, char** argv, Options* output) {
    if (output == nullptr) return failure(core::ErrorCode::kInvalidArgument, "options output is null");
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string flag(argv[index]);
        if (flag == "--help") {
            std::cout << "Usage: stage_k_raw_tensor_runner --config <runtime-config-v2-or-v3> --input-manifest <input-manifest.json> --output-dir <new-directory> --run-id <identifier> [--source-commit <sha>] [--executable-sha <sha>]\n";
            options.help = true;
            *output = std::move(options);
            return core::Status::success();
        }
        if (index + 1 >= argc) return failure(core::ErrorCode::kInvalidArgument, "missing value for " + flag);
        const std::string value(argv[++index]);
        if (flag == "--config") options.config_path = value;
        else if (flag == "--input-manifest") options.input_manifest_path = value;
        else if (flag == "--output-dir") options.output_dir = value;
        else if (flag == "--run-id") options.run_id = value;
        else if (flag == "--source-commit") options.source_commit = value;
        else if (flag == "--executable-sha") options.executable_sha256 = value;
        else return failure(core::ErrorCode::kInvalidArgument, "unknown option: " + flag);
    }
    if (options.config_path.empty() || options.input_manifest_path.empty() || options.output_dir.empty() || options.run_id.empty()) {
        return failure(core::ErrorCode::kInvalidArgument, "--config, --input-manifest, --output-dir and --run-id are required");
    }
    *output = std::move(options);
    return core::Status::success();
}

core::Status exact_contract(const model::ModelContract& contract) {
    const std::vector<std::int64_t> input_shape(kInputShape.begin(), kInputShape.end());
    const std::vector<std::int64_t> output_shape(kOutputShape.begin(), kOutputShape.end());
    if (contract.input.tensor_info.dtype != core::TensorDataType::kFloat32 ||
        contract.input.tensor_info.layout != core::TensorLayout::kNchw || contract.input.tensor_info.shape != input_shape ||
        contract.output.tensor_info.dtype != core::TensorDataType::kFloat32 ||
        contract.output.tensor_info.layout != core::TensorLayout::kBcn || contract.output.tensor_info.shape != output_shape) {
        return failure(core::ErrorCode::kModelContractMismatch, "ModelContract does not match frozen raw tensor contract");
    }
    return core::Status::success();
}

}  // namespace

int main(int argc, char** argv) {
    if (!little_endian_host()) {
        std::cerr << "stage_k_raw_tensor_runner: big-endian host is unsupported\n";
        return 2;
    }
    Options options;
    core::Status status = parse_options(argc, argv, &options);
    if (!status.ok()) {
        std::cerr << "stage_k_raw_tensor_runner: " << status.message() << '\n';
        return 2;
    }
    if (options.help) return 0;
    runtime::RuntimeConfig config;
    status = runtime::RuntimeConfigLoader::load(options.config_path, &config);
    if (!status.ok()) { std::cerr << "runtime config: " << status.message() << '\n'; return 3; }
    if (config.schema_version != 2U && config.schema_version != 3U) { std::cerr << "runtime config: only schema v2/v3 is allowed\n"; return 3; }
    model::ModelContract contract;
    status = model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) { std::cerr << "model contract: " << status.message() << '\n'; return 3; }
    status = exact_contract(contract);
    if (!status.ok()) { std::cerr << "model contract: " << status.message() << '\n'; return 3; }
    std::vector<InputEntry> entries;
    status = parse_input_manifest(options.input_manifest_path, &entries);
    if (!status.ok()) { std::cerr << "input manifest: " << status.message() << '\n'; return 3; }
    std::unique_ptr<inference::IInferenceEngine> engine;
    status = inference::create_inference_engine(config, contract, &engine);
    if (!status.ok() || !engine) { std::cerr << "backend initialization: " << status.message() << '\n'; return 4; }
    status = require_new_directory(options.output_dir);
    if (!status.ok()) { std::cerr << "output directory: " << status.message() << '\n'; return 5; }

    std::string runtime_sha, contract_sha, input_manifest_sha;
    if (!(sha256_file(options.config_path, &runtime_sha).ok() && sha256_file(config.model_contract_path, &contract_sha).ok() && sha256_file(options.input_manifest_path, &input_manifest_sha).ok())) {
        std::cerr << "provenance: cannot hash runtime config or model contract\n"; return 6;
    }
    if (options.executable_sha256.empty()) {
        std::string executable_path;
        std::array<char, 4096> path_buffer{};
        const ssize_t length = readlink("/proc/self/exe", path_buffer.data(), path_buffer.size() - 1U);
        if (length > 0) {
            executable_path.assign(path_buffer.data(), static_cast<std::size_t>(length));
            if (!sha256_file(executable_path, &options.executable_sha256).ok()) options.executable_sha256 = "unknown";
        } else options.executable_sha256 = "unknown";
    }
    std::string model_sha, engine_sha, engine_manifest_sha;
    if (config.backend_type == "onnxruntime_cpu") {
        status = sha256_file(config.model_path, &model_sha);
    } else if (config.backend_type == "tensorrt_fp16") {
        status = sha256_file(config.tensorrt.engine_path, &engine_sha);
        if (status.ok()) status = sha256_file(config.tensorrt.engine_manifest_path, &engine_manifest_sha);
    }
    if (!status.ok()) { std::cerr << "provenance: " << status.message() << '\n'; return 6; }

    std::vector<OutputRecord> records;
    records.reserve(entries.size());
    for (std::size_t index = 0; index < entries.size(); ++index) {
        core::HostTensor input;
        status = read_input_tensor(entries[index], &input);
        if (!status.ok()) { std::cerr << "entry " << entries[index].image_id << ": " << status.message() << '\n'; return 7; }
        core::HostTensor output;
        status = engine->run(input, &output);
        if (!status.ok()) { std::cerr << "entry " << entries[index].image_id << " inference: " << status.message() << '\n'; return 7; }
        status = core::validate_host_tensor(output);
        if (!status.ok() || output.info.dtype != core::TensorDataType::kFloat32 || output.info.layout != core::TensorLayout::kBcn || output.info.shape != std::vector<std::int64_t>(kOutputShape.begin(), kOutputShape.end())) {
            std::cerr << "entry " << entries[index].image_id << ": output contract mismatch\n"; return 7;
        }
        if (!std::all_of(output.data.begin(), output.data.end(), [](float value) { return std::isfinite(value); })) {
            std::cerr << "entry " << entries[index].image_id << ": output contains non-finite value\n"; return 7;
        }
        const std::string output_filename = "output_" + std::to_string(index) + ".f32le";
        status = write_atomic(options.output_dir / output_filename, output.data);
        if (!status.ok()) { std::cerr << "entry " << entries[index].image_id << ": " << status.message() << '\n'; return 7; }
        std::string output_sha;
        status = sha256_file(options.output_dir / output_filename, &output_sha);
        if (!status.ok()) { std::cerr << "entry " << entries[index].image_id << ": cannot hash output\n"; return 7; }
        records.push_back({entries[index].image_id, entries[index].tensor_path.filename().string(), entries[index].sha256, output_filename, output_sha});
    }
    const std::string manifest = output_manifest_json(options, config, contract, runtime_sha, contract_sha, model_sha, engine_sha, engine_manifest_sha, input_manifest_sha, records);
    status = publish_manifest(options.output_dir / "output_manifest.json", manifest);
    if (!status.ok()) { std::cerr << "output manifest: " << status.message() << '\n'; return 8; }
    std::cout << "stage_k_raw_tensor_runner: SUCCESS entries=" << records.size() << " output_manifest=" << (options.output_dir / "output_manifest.json").string() << '\n';
    return 0;
}
