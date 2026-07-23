#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/backend_ort/onnx_runtime_options.hpp"

#include "edge_ai_defect/core/tensor.hpp"

#include <cpu_provider_factory.h>
#include <onnxruntime_cxx_api.h>
#include <openssl/evp.h>

#include <array>
#include <cctype>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <fstream>
#include <iomanip>
#include <limits>
#include <memory>
#include <sstream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace edge_ai_defect::backend_ort {
namespace {

using core::ErrorCode;
using core::Status;

Status model_contract_failure(std::string message) {
    return Status::failure(ErrorCode::kModelContractMismatch,
                           std::move(message));
}

bool is_lowercase_sha256(const std::string& digest) {
    if (digest.size() != 64U) {
        return false;
    }
    for (const unsigned char character : digest) {
        if (!std::isdigit(character) &&
            (character < static_cast<unsigned char>('a') ||
             character > static_cast<unsigned char>('f'))) {
            return false;
        }
    }
    return true;
}

Status validate_contract(const model::ModelContract& contract) {
    if (contract.format != "onnx") {
        return model_contract_failure("ModelContract format must be 'onnx'");
    }
    if (contract.model_id.empty()) {
        return model_contract_failure("ModelContract model_id must not be empty");
    }
    if (!is_lowercase_sha256(contract.expected_onnx_sha256)) {
        return model_contract_failure(
            "ModelContract expected_onnx_sha256 must be lowercase SHA256");
    }
    if (contract.expected_onnx_size_bytes == 0U) {
        return model_contract_failure(
            "ModelContract expected_onnx_size_bytes must be positive");
    }
    if (contract.input.name.empty() || contract.output.name.empty()) {
        return model_contract_failure(
            "ModelContract input/output names must not be empty");
    }
    if (contract.input.tensor_info.layout != core::TensorLayout::kNchw) {
        return model_contract_failure(
            "ModelContract input layout must be NCHW");
    }
    if (contract.output.tensor_info.layout != core::TensorLayout::kBcn) {
        return model_contract_failure(
            "ModelContract output layout must be BCN");
    }

    const Status input_status = core::validate_tensor_info(contract.input.tensor_info);
    if (!input_status.ok()) {
        return model_contract_failure("ModelContract input is invalid: " +
                                      input_status.message());
    }
    const Status output_status =
        core::validate_tensor_info(contract.output.tensor_info);
    if (!output_status.ok()) {
        return model_contract_failure("ModelContract output is invalid: " +
                                      output_status.message());
    }
    return Status::success();
}

Status read_model_size(const std::filesystem::path& model_path,
                       std::uint64_t& size_bytes) {
    std::error_code error;
    if (!std::filesystem::exists(model_path, error)) {
        if (error) {
            return Status::failure(ErrorCode::kIoError,
                                   "Cannot inspect model path '" +
                                       model_path.string() + "': " +
                                       error.message());
        }
        return Status::failure(ErrorCode::kIoError,
                               "Model file does not exist: " +
                                   model_path.string());
    }
    if (!std::filesystem::is_regular_file(model_path, error)) {
        return Status::failure(ErrorCode::kIoError,
                               "Model path is not a regular file: " +
                                   model_path.string());
    }

    const std::uintmax_t file_size = std::filesystem::file_size(model_path, error);
    if (error) {
        return Status::failure(ErrorCode::kIoError,
                               "Cannot read model file size for '" +
                                   model_path.string() + "': " + error.message());
    }
    if (file_size > std::numeric_limits<std::uint64_t>::max()) {
        return Status::failure(ErrorCode::kIoError,
                               "Model file size exceeds uint64 range: " +
                                   model_path.string());
    }
    size_bytes = static_cast<std::uint64_t>(file_size);
    return Status::success();
}

Status sha256_file(const std::filesystem::path& model_path, std::string& digest) {
    std::ifstream input(model_path, std::ios::binary);
    if (!input) {
        return Status::failure(ErrorCode::kIoError,
                               "Cannot open model file for SHA256: " +
                                   model_path.string());
    }

    using DigestContext = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    DigestContext context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context || EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) != 1) {
        return Status::failure(ErrorCode::kBackendInitializationError,
                               "Cannot initialize OpenSSL SHA256 context");
    }

    std::array<char, 16384> buffer{};
    while (input.good()) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize bytes_read = input.gcount();
        if (bytes_read > 0 &&
            EVP_DigestUpdate(context.get(), buffer.data(),
                             static_cast<std::size_t>(bytes_read)) != 1) {
            return Status::failure(ErrorCode::kBackendInitializationError,
                                   "Cannot update OpenSSL SHA256 digest");
        }
    }
    if (!input.eof()) {
        return Status::failure(ErrorCode::kIoError,
                               "Cannot read model file for SHA256: " +
                                   model_path.string());
    }

    std::array<unsigned char, EVP_MAX_MD_SIZE> raw_digest{};
    unsigned int raw_digest_size = 0;
    if (EVP_DigestFinal_ex(context.get(), raw_digest.data(), &raw_digest_size) != 1 ||
        raw_digest_size != 32U) {
        return Status::failure(ErrorCode::kBackendInitializationError,
                               "Cannot finalize OpenSSL SHA256 digest");
    }

    std::ostringstream stream;
    stream << std::hex << std::setfill('0');
    for (unsigned int index = 0; index < raw_digest_size; ++index) {
        stream << std::setw(2) << static_cast<unsigned int>(raw_digest[index]);
    }
    digest = stream.str();
    return Status::success();
}

Status validate_ort_tensor(const char* label,
                           const model::TensorContract& expected,
                           const Ort::TypeInfo& type_info,
                           const std::string& actual_name) {
    if (actual_name != expected.name) {
        return model_contract_failure(std::string("ORT ") + label +
                                      " name mismatch: expected '" +
                                      expected.name + "', actual '" + actual_name +
                                      "'");
    }
    if (type_info.GetONNXType() != ONNX_TYPE_TENSOR) {
        return model_contract_failure(std::string("ORT ") + label +
                                      " must be an ONNX tensor");
    }

    const auto tensor_info =
        type_info.GetTensorTypeAndShapeInfo();
    if (tensor_info.GetElementType() != ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT) {
        return model_contract_failure(std::string("ORT ") + label +
                                      " dtype mismatch: expected float32");
    }
    const std::vector<std::int64_t> actual_shape = tensor_info.GetShape();
    for (std::size_t index = 0; index < actual_shape.size(); ++index) {
        if (actual_shape[index] <= 0) {
            return model_contract_failure(std::string("ORT ") + label +
                                          " has non-positive static dimension at " +
                                          std::to_string(index));
        }
    }
    if (actual_shape != expected.tensor_info.shape) {
        return model_contract_failure(std::string("ORT ") + label +
                                      " shape does not match ModelContract");
    }
    return Status::success();
}

bool tensor_info_matches(const core::TensorInfo& actual,
                         const core::TensorInfo& expected) {
    return actual.dtype == expected.dtype && actual.layout == expected.layout &&
           actual.shape == expected.shape;
}

Status validate_run_input(const core::HostTensor& input,
                          const core::TensorInfo& expected_info) {
    const Status tensor_status = core::validate_host_tensor(input);
    if (!tensor_status.ok()) {
        return tensor_status;
    }
    if (input.data.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "Inference input data must not be empty");
    }
    if (input.info.dtype != expected_info.dtype) {
        return Status::failure(ErrorCode::kUnsupportedDataType,
                               "Inference input dtype does not match ModelContract");
    }
    if (input.info.layout != expected_info.layout) {
        return Status::failure(ErrorCode::kUnsupportedLayout,
                               "Inference input layout does not match ModelContract");
    }
    if (input.info.shape != expected_info.shape) {
        return Status::failure(ErrorCode::kInvalidShape,
                               "Inference input shape does not match ModelContract");
    }
    return Status::success();
}

}  // namespace

class OnnxRuntimeEngine::Impl {
public:
    std::unique_ptr<Ort::Env> environment;
    std::unique_ptr<Ort::SessionOptions> session_options;
    std::unique_ptr<Ort::Session> session;
    std::unique_ptr<const OrtOptionsRecord> options_record;
    model::ModelContract contract;
    core::TensorInfo input_info;
    core::TensorInfo output_info;
    std::string input_name;
    std::string output_name;
};

OnnxRuntimeEngine::OnnxRuntimeEngine() = default;

OnnxRuntimeEngine::~OnnxRuntimeEngine() = default;

core::Status OnnxRuntimeEngine::initialize(
    const model::ModelContract& contract,
    const std::filesystem::path& model_path) {
    runtime::RuntimeConfig default_config;
    default_config.schema_version = 2;
    default_config.backend_type = "onnxruntime_cpu";
    return initialize(default_config, contract, model_path);
}

core::Status OnnxRuntimeEngine::initialize(
    const runtime::RuntimeConfig& config,
    const model::ModelContract& contract,
    const std::filesystem::path& model_path) {
    if (model_path.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "Model path must not be empty");
    }

    const Status contract_status = validate_contract(contract);
    if (!contract_status.ok()) {
        return contract_status;
    }

    std::uint64_t actual_size_bytes = 0;
    const Status size_status = read_model_size(model_path, actual_size_bytes);
    if (!size_status.ok()) {
        return size_status;
    }
    if (actual_size_bytes != contract.expected_onnx_size_bytes) {
        return model_contract_failure(
            "Model file size does not match ModelContract: expected " +
            std::to_string(contract.expected_onnx_size_bytes) + ", actual " +
            std::to_string(actual_size_bytes));
    }

    std::string actual_sha256;
    const Status hash_status = sha256_file(model_path, actual_sha256);
    if (!hash_status.ok()) {
        return hash_status;
    }
    if (actual_sha256 != contract.expected_onnx_sha256) {
        return model_contract_failure(
            "Model SHA256 does not match ModelContract");
    }

    try {
        auto candidate = std::make_unique<Impl>();
        candidate->environment = std::make_unique<Ort::Env>(
            ORT_LOGGING_LEVEL_WARNING, "edge_ai_defect_onnx_runtime_engine");
        candidate->session_options = std::make_unique<Ort::SessionOptions>();
        const Status options_status = apply_ort_options(
            config, candidate->session_options.get(), &candidate->options_record);
        if (!options_status.ok()) {
            return options_status;
        }
        candidate->session = std::make_unique<Ort::Session>(
            *candidate->environment, model_path.c_str(), *candidate->session_options);

        const std::size_t input_count = candidate->session->GetInputCount();
        const std::size_t output_count = candidate->session->GetOutputCount();
        if (input_count != 1U || output_count != 1U) {
            return model_contract_failure(
                "ORT input/output count mismatch: expected 1/1, actual " +
                std::to_string(input_count) + "/" + std::to_string(output_count));
        }

        Ort::AllocatorWithDefaultOptions allocator;
        auto input_name = candidate->session->GetInputNameAllocated(0, allocator);
        auto output_name = candidate->session->GetOutputNameAllocated(0, allocator);
        if (!input_name || !output_name) {
            return model_contract_failure("ORT returned a null input or output name");
        }
        candidate->input_name = input_name.get();
        candidate->output_name = output_name.get();

        const Status input_metadata_status = validate_ort_tensor(
            "input", contract.input, candidate->session->GetInputTypeInfo(0),
            candidate->input_name);
        if (!input_metadata_status.ok()) {
            return input_metadata_status;
        }
        const Status output_metadata_status = validate_ort_tensor(
            "output", contract.output, candidate->session->GetOutputTypeInfo(0),
            candidate->output_name);
        if (!output_metadata_status.ok()) {
            return output_metadata_status;
        }

        candidate->contract = contract;
        candidate->input_info = contract.input.tensor_info;
        candidate->output_info = contract.output.tensor_info;
        impl_ = std::move(candidate);
        return Status::success();
    } catch (const Ort::Exception& exception) {
        return Status::failure(
            ErrorCode::kBackendInitializationError,
            "ONNX Runtime initialization failed: " + std::string(exception.what()));
    } catch (const std::exception& exception) {
        return Status::failure(
            ErrorCode::kBackendInitializationError,
            "ONNX Runtime initialization failed: " + std::string(exception.what()));
    }
}

core::Status OnnxRuntimeEngine::run(const core::HostTensor& input,
                                    core::HostTensor* output) {
    if (!impl_ || !impl_->session) {
        return Status::failure(ErrorCode::kBackendRuntimeError,
                               "OnnxRuntimeEngine is not initialized");
    }
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "Inference output must not be null");
    }

    const Status input_status = validate_run_input(input, impl_->input_info);
    if (!input_status.ok()) {
        return input_status;
    }

    try {
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault);
        // ORT consumes this caller-owned input buffer synchronously without copying it.
        Ort::Value input_value = Ort::Value::CreateTensor<float>(
            memory_info,
            const_cast<float*>(input.data.data()),
            input.data.size(),
            input.info.shape.data(),
            input.info.shape.size());
        if (!input_value.IsTensor()) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime did not create a tensor input value");
        }

        const char* input_names[] = {impl_->input_name.c_str()};
        const char* output_names[] = {impl_->output_name.c_str()};
        Ort::RunOptions run_options;
        std::vector<Ort::Value> output_values = impl_->session->Run(
            run_options,
            input_names,
            &input_value,
            1,
            output_names,
            1);

        if (output_values.size() != 1U || !output_values.front().IsTensor()) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output must contain exactly one tensor");
        }

        const Ort::Value& output_value = output_values.front();
        const auto output_tensor_info = output_value.GetTensorTypeAndShapeInfo();
        if (output_tensor_info.GetElementType() !=
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output dtype must be float32");
        }
        const std::vector<std::int64_t> output_shape =
            output_tensor_info.GetShape();
        if (output_shape != impl_->output_info.shape) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output shape does not match ModelContract");
        }

        std::size_t expected_element_count = 0;
        const Status count_status = core::checked_element_count(
            impl_->output_info.shape, expected_element_count);
        if (!count_status.ok() ||
            output_tensor_info.GetElementCount() != expected_element_count) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output element count does not match ModelContract");
        }

        const float* output_data = output_value.GetTensorData<float>();
        if (output_data == nullptr) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output tensor data is null");
        }
        for (std::size_t index = 0; index < expected_element_count; ++index) {
            if (!std::isfinite(output_data[index])) {
                return Status::failure(ErrorCode::kBackendRuntimeError,
                                       "ONNX Runtime output contains a non-finite value");
            }
        }

        core::HostTensor candidate{
            impl_->output_info,
            std::vector<float>(output_data, output_data + expected_element_count),
        };
        const Status output_status = core::validate_host_tensor(candidate);
        if (!output_status.ok() ||
            !tensor_info_matches(candidate.info, impl_->output_info)) {
            return Status::failure(ErrorCode::kBackendRuntimeError,
                                   "ONNX Runtime output HostTensor validation failed");
        }
        *output = std::move(candidate);
        return Status::success();
    } catch (const Ort::Exception& exception) {
        return Status::failure(
            ErrorCode::kBackendRuntimeError,
            "ONNX Runtime run failed: " + std::string(exception.what()));
    } catch (const std::exception& exception) {
        return Status::failure(
            ErrorCode::kBackendRuntimeError,
            "ONNX Runtime run failed: " + std::string(exception.what()));
    }
}

}  // namespace edge_ai_defect::backend_ort
