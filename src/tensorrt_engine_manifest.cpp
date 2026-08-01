#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"

#include <openssl/evp.h>
#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <array>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <unordered_set>

namespace edge_ai_defect::model {
namespace {
using core::ErrorCode;
using core::Status;

Status error(ErrorCode code, const std::string& path, const std::string& detail) {
    return Status::failure(code, path + ": " + detail);
}

Status mapping(const YAML::Node& node, const std::string& path,
               const std::vector<std::string>& keys) {
    if (!node.IsMap()) return error(ErrorCode::kSchemaViolation, path, "expected mapping");
    std::unordered_set<std::string> seen;
    for (const auto& entry : node) {
        if (!entry.first.IsScalar()) return error(ErrorCode::kSchemaViolation, path, "key must be scalar");
        const std::string key = entry.first.Scalar();
        if (!seen.insert(key).second) return error(ErrorCode::kSchemaViolation, path + "." + key, "duplicate key");
        if (std::find(keys.begin(), keys.end(), key) == keys.end()) {
            return error(ErrorCode::kSchemaViolation, path + "." + key, "unknown field");
        }
    }
    for (const auto& key : keys) {
        if (!node[key].IsDefined()) return error(ErrorCode::kSchemaViolation, path + "." + key, "missing required field");
    }
    return Status::success();
}

template <typename T>
Status scalar(const YAML::Node& node, const std::string& path, T* value) {
    if (!node.IsScalar()) return error(ErrorCode::kSchemaViolation, path, "expected scalar");
    try { *value = node.as<T>(); }
    catch (const YAML::Exception& exception) { return error(ErrorCode::kParseError, path, exception.what()); }
    return Status::success();
}

bool sha256_text(const std::filesystem::path& path, std::string* output) {
    std::ifstream input(path, std::ios::binary);
    if (!input.is_open()) return false;
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        EVP_MD_CTX_free(context); return false;
    }
    std::array<char, 65536> buffer{};
    while (input.good()) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context, buffer.data(), static_cast<std::size_t>(count)) != 1) {
            EVP_MD_CTX_free(context); return false;
        }
    }
    unsigned char digest[EVP_MAX_MD_SIZE]{};
    unsigned int length = 0;
    const bool ok = !input.bad() && EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) return false;
    std::ostringstream text;
    text << std::hex << std::setfill('0');
    for (unsigned int index = 0; index < length; ++index) text << std::setw(2) << static_cast<unsigned int>(digest[index]);
    *output = text.str();
    return true;
}

Status tensor(const YAML::Node& node, const std::string& path, TensorContract* output) {
    const Status status = mapping(node, path, {"name", "shape", "dtype", "format"});
    if (!status.ok()) return status;
    TensorContract value;
    if (!scalar(node["name"], path + ".name", &value.name).ok() || value.name.empty()) return error(ErrorCode::kSchemaViolation, path + ".name", "must not be empty");
    std::string dtype;
    if (!scalar(node["dtype"], path + ".dtype", &dtype).ok() || dtype != "FP32") return error(ErrorCode::kSchemaViolation, path + ".dtype", "must be FP32");
    std::string format;
    if (!scalar(node["format"], path + ".format", &format).ok() || format != "CHW") return error(ErrorCode::kSchemaViolation, path + ".format", "must be CHW");
    value.tensor_info.dtype = core::TensorDataType::kFloat32;
    value.tensor_info.layout = core::TensorLayout::kNchw;
    if (!node["shape"].IsSequence() || node["shape"].size() == 0) return error(ErrorCode::kInvalidShape, path + ".shape", "must be a non-empty sequence");
    for (std::size_t index = 0; index < node["shape"].size(); ++index) {
        std::int64_t dimension = 0;
        const Status shape_status = scalar(node["shape"][index], path + ".shape[" + std::to_string(index) + "]", &dimension);
        if (!shape_status.ok()) return shape_status;
        if (dimension <= 0) return error(ErrorCode::kInvalidShape, path + ".shape", "dimensions must be positive");
        value.tensor_info.shape.push_back(dimension);
    }
    *output = std::move(value);
    return Status::success();
}

Status sha_field(const YAML::Node& node, const std::string& path, std::string* output) {
    Status status = scalar(node, path, output);
    if (!status.ok()) return status;
    if (output->size() != 64U || output->find_first_not_of("0123456789abcdef") != std::string::npos)
        return error(ErrorCode::kSchemaViolation, path, "must be lowercase SHA256");
    return Status::success();
}

std::filesystem::path resolve(const std::filesystem::path& manifest, const std::string& raw);

Status load_v2(const YAML::Node& root,
               const std::filesystem::path& manifest_path,
               const ModelContract* expected_contract,
               TensorRtEngineManifest* output) {
    const Status root_status = mapping(root, "$", {
        "schema_version", "artifact_kind", "backend_type", "artifact_purpose",
        "engine_path", "engine_sha256", "model_contract_path", "onnx_sha256",
        "precision_mode", "int8_enabled", "fp16_fallback_enabled", "host_io_dtype",
        "calibration_manifest_sha256", "calibration_cache_sha256",
        "precision_audit_sha256"});
    if (!root_status.ok()) return root_status;
    std::int64_t version = 0;
    Status status = scalar(root["schema_version"], "schema_version", &version);
    if (!status.ok() || version != 2) return error(ErrorCode::kSchemaViolation, "schema_version", "must be exactly 2");
    TensorRtEngineManifest value;
    value.schema_version = 2;
    status = scalar(root["artifact_kind"], "artifact_kind", &value.artifact_kind);
    if (!status.ok() || value.artifact_kind != "tensorrt_engine") return error(ErrorCode::kSchemaViolation, "artifact_kind", "must be tensorrt_engine");
    status = scalar(root["backend_type"], "backend_type", &value.backend_type);
    if (!status.ok() || value.backend_type != "tensorrt_int8") return error(ErrorCode::kSchemaViolation, "backend_type", "must be tensorrt_int8");
    std::string purpose;
    status = scalar(root["artifact_purpose"], "artifact_purpose", &purpose);
    if (!status.ok() || purpose != "formal") return error(ErrorCode::kSchemaViolation, "artifact_purpose", "must be formal");
    std::string raw_path;
    status = scalar(root["engine_path"], "engine_path", &raw_path); if (!status.ok()) return status;
    value.engine_path = resolve(manifest_path, raw_path);
    status = sha_field(root["engine_sha256"], "engine_sha256", &value.engine_sha256); if (!status.ok()) return status;
    status = scalar(root["model_contract_path"], "model_contract_path", &raw_path); if (!status.ok()) return status;
    value.model_contract_path = resolve(manifest_path, raw_path);
    status = sha_field(root["onnx_sha256"], "onnx_sha256", &value.source_onnx_sha256); if (!status.ok()) return status;
    value.source_onnx_path = resolve(manifest_path, "models/onnx/yolov8n_neudet_frozen.onnx");
    status = scalar(root["precision_mode"], "precision_mode", &value.precision_mode); if (!status.ok()) return status;
    status = scalar(root["int8_enabled"], "int8_enabled", &value.int8_enabled); if (!status.ok() || !value.int8_enabled) return error(ErrorCode::kSchemaViolation, "int8_enabled", "must be true");
    status = scalar(root["fp16_fallback_enabled"], "fp16_fallback_enabled", &value.fp16_fallback_enabled); if (!status.ok() || !value.fp16_fallback_enabled) return error(ErrorCode::kSchemaViolation, "fp16_fallback_enabled", "must be true");
    status = scalar(root["host_io_dtype"], "host_io_dtype", &value.host_io_dtype); if (!status.ok() || value.host_io_dtype != "FP32") return error(ErrorCode::kSchemaViolation, "host_io_dtype", "must be FP32");
    status = sha_field(root["calibration_manifest_sha256"], "calibration_manifest_sha256", &value.calibration_manifest_sha256); if (!status.ok()) return status;
    status = sha_field(root["calibration_cache_sha256"], "calibration_cache_sha256", &value.calibration_cache_sha256); if (!status.ok()) return status;
    status = sha_field(root["precision_audit_sha256"], "precision_audit_sha256", &value.precision_audit_sha256); if (!status.ok()) return status;
    value.input.name = expected_contract != nullptr ? expected_contract->input.name : "images";
    value.output.name = expected_contract != nullptr ? expected_contract->output.name : "output0";
    if (expected_contract != nullptr) { value.input = expected_contract->input; value.output = expected_contract->output; }
    std::string actual;
    if (!sha256_text(value.engine_path, &actual) || actual != value.engine_sha256) return error(ErrorCode::kModelContractMismatch, "engine_sha256", "engine hash mismatch");
    if (!sha256_text(value.source_onnx_path, &actual) || actual != value.source_onnx_sha256) return error(ErrorCode::kModelContractMismatch, "onnx_sha256", "ONNX hash mismatch");
    if (!sha256_text(value.model_contract_path, &actual)) return error(ErrorCode::kModelContractMismatch, "model_contract_path", "contract unreadable");
    const auto audit_path = std::filesystem::current_path() / "results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json";
    if (!sha256_text(audit_path, &actual) || actual != value.precision_audit_sha256) return error(ErrorCode::kModelContractMismatch, "precision_audit_sha256", "precision audit hash mismatch");
    YAML::Node audit;
    try { audit = YAML::LoadFile(audit_path.string()); } catch (const YAML::Exception& exception) { return error(ErrorCode::kParseError, "precision_audit", exception.what()); }
    std::int64_t int8_compute = 0;
    status = scalar(audit["confirmed_int8_compute"], "precision_audit.confirmed_int8_compute", &int8_compute);
    if (!status.ok() || int8_compute <= 0) return error(ErrorCode::kSchemaViolation, "precision_audit.confirmed_int8_compute", "must be positive");
    value.confirmed_int8_compute = static_cast<std::uint64_t>(int8_compute);
    const auto cache_path = manifest_path.parent_path() / "calibration.cache";
    if (!sha256_text(cache_path, &actual) || actual != value.calibration_cache_sha256) return error(ErrorCode::kModelContractMismatch, "calibration_cache_sha256", "calibration cache hash mismatch");
    const auto metadata_path = cache_path.parent_path() / "calibration_cache.meta.json";
    if (!sha256_text(metadata_path, &value.cache_metadata_sha256)) return error(ErrorCode::kModelContractMismatch, "calibration_cache.meta.json", "cache metadata unreadable");
    try {
        const YAML::Node metadata = YAML::LoadFile(metadata_path.string());
        std::string metadata_purpose, metadata_manifest, metadata_cache, metadata_contract;
        std::int64_t batches = 0, failed = 0;
        if (!scalar(metadata["artifact_purpose"], "cache_metadata.artifact_purpose", &metadata_purpose).ok() || metadata_purpose != "formal" ||
            !scalar(metadata["calibration_manifest_sha256"], "cache_metadata.calibration_manifest_sha256", &metadata_manifest).ok() || metadata_manifest != value.calibration_manifest_sha256 ||
            !scalar(metadata["cache_sha256"], "cache_metadata.cache_sha256", &metadata_cache).ok() || metadata_cache != value.calibration_cache_sha256 ||
            !scalar(metadata["model_contract_sha256"], "cache_metadata.model_contract_sha256", &metadata_contract).ok() ||
            !scalar(metadata["successful_calibration_batches"], "cache_metadata.successful_calibration_batches", &batches).ok() || batches != 1260 ||
            !scalar(metadata["failed_images"], "cache_metadata.failed_images", &failed).ok() || failed != 0)
            return error(ErrorCode::kSchemaViolation, "cache_metadata", "formal calibration provenance is incomplete");
        if (!sha256_text(value.model_contract_path, &actual) || actual != metadata_contract)
            return error(ErrorCode::kModelContractMismatch, "model_contract_sha256", "ModelContract hash mismatch");
        value.model_contract_sha256 = metadata_contract;
    } catch (const YAML::Exception& exception) { return error(ErrorCode::kParseError, "cache_metadata", exception.what()); }
    try {
        const YAML::Node formal_manifest = YAML::LoadFile((std::filesystem::current_path() / "results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json").string());
        std::string purpose, split, ordering; std::int64_t count = 0;
        if (!scalar(formal_manifest["purpose"], "calibration_manifest.purpose", &purpose).ok() || purpose != "formal_int8_calibration" ||
            !scalar(formal_manifest["source_split"], "calibration_manifest.source_split", &split).ok() || split != "train" ||
            !scalar(formal_manifest["ordering_algorithm"], "calibration_manifest.ordering_algorithm", &ordering).ok() || ordering != "sha256_key_permutation_v1" ||
            !scalar(formal_manifest["image_count"], "calibration_manifest.image_count", &count).ok() || count != 1260)
            return error(ErrorCode::kSchemaViolation, "calibration_manifest", "formal calibration provenance is incomplete");
    } catch (const YAML::Exception& exception) { return error(ErrorCode::kParseError, "calibration_manifest", exception.what()); }
    *output = std::move(value);
    return Status::success();
}

bool same_tensor(const TensorContract& left, const TensorContract& right) {
    return left.name == right.name && left.tensor_info.dtype == right.tensor_info.dtype &&
           left.tensor_info.shape == right.tensor_info.shape;
}

std::filesystem::path resolve(const std::filesystem::path& manifest, const std::string& raw) {
    const std::filesystem::path path(raw);
    if (path.is_absolute()) return path;
    const std::filesystem::path cwd = std::filesystem::current_path() / path;
    std::error_code error;
    if (std::filesystem::is_regular_file(cwd, error) && !error) return cwd;
    return manifest.parent_path() / path;
}
}  // namespace

core::Status TensorRtEngineManifestLoader::load(
    const std::filesystem::path& manifest_path,
    const ModelContract* expected_contract,
    TensorRtEngineManifest* output) {
    if (output == nullptr) return error(ErrorCode::kInvalidArgument, "output", "must not be null");
    std::ifstream input(manifest_path);
    if (!input.is_open()) return error(ErrorCode::kIoError, manifest_path.string(), "manifest is not readable");
    try {
        const YAML::Node root = YAML::Load(input);
        if (root["schema_version"].IsDefined() && root["schema_version"].IsScalar() &&
            root["schema_version"].as<int>() == 2) {
            return load_v2(root, manifest_path, expected_contract, output);
        }
        const Status root_status = mapping(root, "$", {"schema_version", "artifact_kind", "engine_id", "engine_filename", "engine_local_path", "engine_sha256", "engine_size_bytes", "source_onnx", "source_onnx_sha256", "model_contract", "model_contract_sha256", "tensorrt_version", "tensorrt_runtime_version", "cuda_version", "l4t_version", "jetson_model", "architecture", "compute_capability", "fp16_builder_mode", "precision_mode", "memory_pool", "input", "output", "batch", "dynamic_shapes", "int8_enabled", "dla_enabled", "custom_plugin_dependency", "standard_plugins_loaded", "profiling_verbosity", "build_command", "build_log", "build_log_sha256", "inspection_command", "inspection_exit_code", "load_smoke_command", "load_smoke_exit_code", "source_git_commit", "limitations"});
        if (!root_status.ok()) return root_status;
        TensorRtEngineManifest value;
        std::int64_t version = 0;
        Status status = scalar(root["schema_version"], "schema_version", &version);
        if (!status.ok() || version != 1) return error(ErrorCode::kSchemaViolation, "schema_version", "must be exactly 1");
        value.schema_version = 1;
        status = scalar(root["artifact_kind"], "artifact_kind", &value.artifact_kind);
        if (!status.ok() || value.artifact_kind != "tensorrt_engine") return error(ErrorCode::kSchemaViolation, "artifact_kind", "must be tensorrt_engine");
        status = scalar(root["engine_id"], "engine_id", &value.engine_id); if (!status.ok()) return status;
        std::string engine_local_path; status = scalar(root["engine_local_path"], "engine_local_path", &engine_local_path); if (!status.ok()) return status;
        value.engine_path = resolve(manifest_path, engine_local_path);
        status = scalar(root["engine_sha256"], "engine_sha256", &value.engine_sha256); if (!status.ok()) return status;
        status = scalar(root["source_onnx_sha256"], "source_onnx_sha256", &value.source_onnx_sha256); if (!status.ok()) return status;
        status = scalar(root["model_contract_sha256"], "model_contract_sha256", &value.model_contract_sha256); if (!status.ok()) return status;
        status = tensor(root["input"], "input", &value.input); if (!status.ok()) return status;
        status = tensor(root["output"], "output", &value.output); if (!status.ok()) return status;
        std::string source_onnx, contract_path; status = scalar(root["source_onnx"], "source_onnx", &source_onnx); if (!status.ok()) return status;
        status = scalar(root["model_contract"], "model_contract", &contract_path); if (!status.ok()) return status;
        value.source_onnx_path = resolve(manifest_path, source_onnx);
        value.model_contract_path = resolve(manifest_path, contract_path);
        std::string actual;
        if (!sha256_text(value.engine_path, &actual) || actual != value.engine_sha256) return error(ErrorCode::kModelContractMismatch, "engine_sha256", "engine artifact hash mismatch or unreadable");
        if (!sha256_text(value.source_onnx_path, &actual) || actual != value.source_onnx_sha256) return error(ErrorCode::kModelContractMismatch, "source_onnx_sha256", "source ONNX hash mismatch or unreadable");
        if (!sha256_text(value.model_contract_path, &actual) || actual != value.model_contract_sha256) return error(ErrorCode::kModelContractMismatch, "model_contract_sha256", "model contract hash mismatch or unreadable");
        if (expected_contract != nullptr && (!same_tensor(value.input, expected_contract->input) || !same_tensor(value.output, expected_contract->output))) return error(ErrorCode::kModelContractMismatch, "tensor_contract", "manifest tensors do not match ModelContract");
        *output = std::move(value);
        return Status::success();
    } catch (const YAML::Exception& exception) {
        return error(ErrorCode::kParseError, "$", exception.what());
    }
}
}  // namespace edge_ai_defect::model
