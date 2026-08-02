#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"

#include "cuda_status.hpp"
#include "tensorrt_logger.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/runtime/diagnostic_sampling.hpp"

#include <NvInfer.h>
#include <cuda_runtime_api.h>

#include <cmath>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <limits>
#include <memory>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace edge_ai_defect::backend_tensorrt {
namespace {

using core::ErrorCode;
using core::Status;

Status failure(ErrorCode code, std::string message) {
    return Status::failure(code, std::move(message));
}

Status validate_config(const runtime::RuntimeConfig& config) {
    const bool supported_runtime_schema = config.schema_version == 3U ||
                                          config.schema_version == 4U ||
                                          config.schema_version == 5U ||
                                          config.schema_version == 6U;
    const bool supported_backend = config.backend_type == "tensorrt_fp16" ||
                                   ((config.schema_version == 5U || config.schema_version == 6U) &&
                                    config.backend_type == "tensorrt_int8");
    if (!supported_runtime_schema || !supported_backend) {
        return failure(ErrorCode::kSchemaViolation,
                       "TensorRtEngine requires RuntimeConfig schema_version 3, 4, 5, or 6 "
                       "and a supported TensorRT backend");
    }
    if (config.data_path_variant == runtime::DataPathVariant::kV3 ||
        config.data_path_variant == runtime::DataPathVariant::kV4) {
        return failure(ErrorCode::kSchemaViolation,
                       "TensorRtEngine only implements Stage R V0 and V2");
    }
    if (config.tensorrt.engine_path.empty() ||
        config.tensorrt.engine_manifest_path.empty()) {
        return failure(ErrorCode::kInvalidArgument,
                       "TensorRtEngine engine and manifest paths must not be empty");
    }
    if (config.model_contract_path.empty()) {
        return failure(ErrorCode::kInvalidArgument,
                       "TensorRtEngine model contract path must not be empty");
    }
    return Status::success();
}

Status validate_contract(const model::ModelContract& contract) {
    if (contract.format != "onnx" || contract.model_id.empty()) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRtEngine ModelContract format or id is invalid");
    }
    if (contract.input.name.empty() || contract.output.name.empty()) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRtEngine ModelContract tensor names must not be empty");
    }
    const Status input_status = core::validate_tensor_info(contract.input.tensor_info);
    if (!input_status.ok()) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRtEngine input contract is invalid: " + input_status.message());
    }
    const Status output_status = core::validate_tensor_info(contract.output.tensor_info);
    if (!output_status.ok()) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRtEngine output contract is invalid: " + output_status.message());
    }
    if (contract.input.tensor_info.layout != core::TensorLayout::kNchw ||
        contract.output.tensor_info.layout != core::TensorLayout::kBcn) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRtEngine requires NCHW input and BCN output contracts");
    }
    return Status::success();
}

Status read_file(const std::filesystem::path& path, std::vector<std::uint8_t>* output) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input.is_open()) {
        return failure(ErrorCode::kIoError, "Cannot open TensorRT engine: " + path.string());
    }
    const std::streampos end = input.tellg();
    if (end < 0 || static_cast<std::uintmax_t>(end) >
                       static_cast<std::uintmax_t>(std::numeric_limits<std::size_t>::max())) {
        return failure(ErrorCode::kIoError, "Cannot determine TensorRT engine size");
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(end));
    input.seekg(0, std::ios::beg);
    if (!bytes.empty() && !input.read(reinterpret_cast<char*>(bytes.data()),
                                      static_cast<std::streamsize>(bytes.size()))) {
        return failure(ErrorCode::kIoError, "Cannot read TensorRT engine: " + path.string());
    }
    *output = std::move(bytes);
    return Status::success();
}

bool dims_match(const nvinfer1::Dims& actual,
                const std::vector<std::int64_t>& expected) {
    if (actual.nbDims != static_cast<int>(expected.size())) return false;
    for (int index = 0; index < actual.nbDims; ++index) {
        if (actual.d[index] != expected[static_cast<std::size_t>(index)]) return false;
    }
    return true;
}

Status tensor_metadata(const nvinfer1::ICudaEngine& engine,
                       const std::string& name,
                       const model::TensorContract& expected,
                       nvinfer1::TensorIOMode expected_mode) {
    if (engine.getTensorIOMode(name.c_str()) != expected_mode) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRT tensor mode mismatch for '" + name + "'");
    }
    if (engine.getTensorDataType(name.c_str()) != nvinfer1::DataType::kFLOAT) {
        return failure(ErrorCode::kUnsupportedDataType,
                       "TensorRT tensor dtype must be FP32 for '" + name + "'");
    }
    if (!dims_match(engine.getTensorShape(name.c_str()), expected.tensor_info.shape)) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRT tensor shape mismatch for '" + name + "'");
    }
    if (engine.getTensorLocation(name.c_str()) != nvinfer1::TensorLocation::kDEVICE) {
        return failure(ErrorCode::kBackendInitializationError,
                       "TensorRT tensor must use device memory for '" + name + "'");
    }
    return Status::success();
}

}  // namespace

class TensorRtEngine::Impl {
public:
    TensorRtLogger logger;
    std::unique_ptr<nvinfer1::IRuntime> runtime;
    std::unique_ptr<nvinfer1::ICudaEngine> engine;
    std::unique_ptr<nvinfer1::IExecutionContext> context;
    cudaStream_t stream = nullptr;
    void* input_device = nullptr;
    void* output_device = nullptr;
    std::size_t input_bytes = 0;
    std::size_t output_bytes = 0;
    std::string input_name;
    std::string output_name;
    core::TensorInfo input_info;
    core::TensorInfo output_info;
    std::uint32_t device_id = 0;
    bool diagnostic_enabled = false;
    std::size_t diagnostic_frame = 0;
    std::vector<TensorRtDiagnosticSample> diagnostic_samples;
    cudaEvent_t h2d_begin = nullptr;
    cudaEvent_t h2d_end = nullptr;
    cudaEvent_t trt_begin = nullptr;
    cudaEvent_t trt_end = nullptr;
    cudaEvent_t d2h_begin = nullptr;
    cudaEvent_t d2h_end = nullptr;

    void destroy_diagnostic_events() noexcept {
        if (h2d_begin != nullptr) cudaEventDestroy(h2d_begin);
        if (h2d_end != nullptr) cudaEventDestroy(h2d_end);
        if (trt_begin != nullptr) cudaEventDestroy(trt_begin);
        if (trt_end != nullptr) cudaEventDestroy(trt_end);
        if (d2h_begin != nullptr) cudaEventDestroy(d2h_begin);
        if (d2h_end != nullptr) cudaEventDestroy(d2h_end);
        h2d_begin = h2d_end = trt_begin = trt_end = d2h_begin = d2h_end = nullptr;
    }

    ~Impl() {
        destroy_diagnostic_events();
        if (input_device != nullptr) cudaFree(input_device);
        if (output_device != nullptr) cudaFree(output_device);
        if (stream != nullptr) cudaStreamDestroy(stream);
    }
};

TensorRtEngine::TensorRtEngine() = default;
TensorRtEngine::~TensorRtEngine() = default;

core::Status TensorRtEngine::initialize(
    const model::ModelContract&,
    const std::filesystem::path&) {
    return failure(ErrorCode::kInvalidArgument,
                   "TensorRtEngine initialization requires RuntimeConfig schema_version 3");
}

core::Status TensorRtEngine::initialize(
    const runtime::RuntimeConfig& config,
    const model::ModelContract& contract) {
    Status status = validate_config(config);
    if (!status.ok()) return status;
    status = validate_contract(contract);
    if (!status.ok()) return status;

    model::TensorRtEngineManifest manifest;
    status = model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, &manifest);
    if (!status.ok()) return status;

    const auto normalized_config_engine =
        std::filesystem::absolute(config.tensorrt.engine_path).lexically_normal();
    const auto normalized_manifest_engine =
        std::filesystem::absolute(manifest.engine_path).lexically_normal();
    if (normalized_config_engine != normalized_manifest_engine) {
        return failure(ErrorCode::kModelContractMismatch,
                       "RuntimeConfig engine_path does not match Engine Manifest");
    }
    const auto normalized_config_contract =
        std::filesystem::absolute(config.model_contract_path).lexically_normal();
    const auto normalized_manifest_contract =
        std::filesystem::absolute(manifest.model_contract_path).lexically_normal();
    if (normalized_config_contract != normalized_manifest_contract) {
        return failure(ErrorCode::kModelContractMismatch,
                       "RuntimeConfig model contract path does not match Engine Manifest");
    }

    std::vector<std::uint8_t> engine_bytes;
    status = read_file(normalized_config_engine, &engine_bytes);
    if (!status.ok()) return status;

    status = cuda_status(cudaSetDevice(config.tensorrt.device_id), "cudaSetDevice");
    if (!status.ok()) return status;

    auto candidate = std::make_unique<Impl>();
    candidate->device_id = config.tensorrt.device_id;
    candidate->runtime.reset(nvinfer1::createInferRuntime(candidate->logger));
    if (!candidate->runtime) {
        return failure(ErrorCode::kBackendInitializationError,
                       "TensorRT createInferRuntime failed");
    }
    candidate->engine.reset(candidate->runtime->deserializeCudaEngine(
        engine_bytes.data(), engine_bytes.size()));
    if (!candidate->engine) {
        return failure(ErrorCode::kBackendInitializationError,
                       "TensorRT engine deserialization failed");
    }
    candidate->context.reset(candidate->engine->createExecutionContext());
    if (!candidate->context) {
        return failure(ErrorCode::kBackendInitializationError,
                       "TensorRT createExecutionContext failed");
    }
    status = cuda_status(cudaStreamCreate(&candidate->stream), "cudaStreamCreate");
    if (!status.ok()) return status;

    if (candidate->engine->getNbIOTensors() != 2) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRT engine must expose exactly two IO tensors");
    }
    for (int index = 0; index < candidate->engine->getNbIOTensors(); ++index) {
        const char* name = candidate->engine->getIOTensorName(index);
        if (name == nullptr) {
            return failure(ErrorCode::kModelContractMismatch,
                           "TensorRT returned a null IO tensor name");
        }
        const std::string tensor_name(name);
        if (candidate->engine->getTensorIOMode(name) == nvinfer1::TensorIOMode::kINPUT) {
            if (tensor_name != contract.input.name || !candidate->input_name.empty()) {
                return failure(ErrorCode::kModelContractMismatch,
                               "TensorRT input tensor name mismatch");
            }
            candidate->input_name = tensor_name;
        } else if (candidate->engine->getTensorIOMode(name) == nvinfer1::TensorIOMode::kOUTPUT) {
            if (tensor_name != contract.output.name || !candidate->output_name.empty()) {
                return failure(ErrorCode::kModelContractMismatch,
                               "TensorRT output tensor name mismatch");
            }
            candidate->output_name = tensor_name;
        } else {
            return failure(ErrorCode::kModelContractMismatch,
                           "TensorRT IO tensor has invalid mode");
        }
    }
    if (candidate->input_name.empty() || candidate->output_name.empty()) {
        return failure(ErrorCode::kModelContractMismatch,
                       "TensorRT input/output tensor names are incomplete");
    }
    status = tensor_metadata(*candidate->engine, candidate->input_name,
                             contract.input, nvinfer1::TensorIOMode::kINPUT);
    if (!status.ok()) return status;
    status = tensor_metadata(*candidate->engine, candidate->output_name,
                             contract.output, nvinfer1::TensorIOMode::kOUTPUT);
    if (!status.ok()) return status;

    std::size_t input_elements = 0;
    std::size_t output_elements = 0;
    status = core::checked_element_count(contract.input.tensor_info.shape, input_elements);
    if (!status.ok()) return status;
    status = core::checked_element_count(contract.output.tensor_info.shape, output_elements);
    if (!status.ok()) return status;
    candidate->input_bytes = input_elements * sizeof(float);
    candidate->output_bytes = output_elements * sizeof(float);
    status = cuda_status(cudaMalloc(&candidate->input_device, candidate->input_bytes),
                         "cudaMalloc input buffer");
    if (!status.ok()) return status;
    status = cuda_status(cudaMalloc(&candidate->output_device, candidate->output_bytes),
                         "cudaMalloc output buffer");
    if (!status.ok()) return status;
    candidate->input_info = contract.input.tensor_info;
    candidate->output_info = contract.output.tensor_info;
    impl_ = std::move(candidate);
    return Status::success();
}

core::Status TensorRtEngine::run(const core::HostTensor& input,
                                 core::HostTensor* output) {
    if (!impl_ || !impl_->context) {
        return failure(ErrorCode::kBackendRuntimeError,
                       "TensorRtEngine is not initialized");
    }
    if (output == nullptr) {
        return failure(ErrorCode::kInvalidArgument,
                       "Inference output must not be null");
    }
    const Status input_status = core::validate_host_tensor(input);
    if (!input_status.ok()) return input_status;
    if (input.info.dtype != impl_->input_info.dtype ||
        input.info.layout != impl_->input_info.layout ||
        input.info.shape != impl_->input_info.shape || input.data.empty()) {
        return failure(ErrorCode::kInvalidShape,
                       "TensorRtEngine input does not match the frozen contract");
    }

    const std::size_t measured_frame = impl_->diagnostic_frame;
    const std::size_t cycle_index = measured_frame / 180U;
    const std::size_t frame_in_cycle = measured_frame % 180U;
    const bool sample = impl_->diagnostic_enabled &&
        runtime::should_sample_diagnostic(frame_in_cycle, cycle_index);
    if (sample) {
        cudaEventRecord(impl_->h2d_begin, impl_->stream);
    }
    Status status = cuda_status(cudaMemcpyAsync(
        impl_->input_device, input.data.data(), impl_->input_bytes,
        cudaMemcpyHostToDevice, impl_->stream), "cudaMemcpyAsync host-to-device");
    if (!status.ok()) return status;
    if (sample) cudaEventRecord(impl_->h2d_end, impl_->stream);
    return run_device_input(impl_->input_device, impl_->input_bytes, output);
}

void* TensorRtEngine::device_input_buffer() const noexcept {
    return impl_ ? impl_->input_device : nullptr;
}

std::size_t TensorRtEngine::device_input_bytes() const noexcept {
    return impl_ ? impl_->input_bytes : 0U;
}

void* TensorRtEngine::cuda_stream_handle() const noexcept {
    return impl_ ? reinterpret_cast<void*>(impl_->stream) : nullptr;
}

core::Status TensorRtEngine::run_device_input(const void* device_input,
                                              std::size_t input_bytes,
                                              core::HostTensor* output) {
    if (!impl_ || !impl_->context) {
        return failure(ErrorCode::kBackendRuntimeError,
                       "TensorRtEngine is not initialized");
    }
    if (output == nullptr || device_input != impl_->input_device ||
        input_bytes != impl_->input_bytes) {
        return failure(ErrorCode::kInvalidArgument,
                       "device input must be the TensorRT-owned fixed-size buffer");
    }
    const std::size_t measured_frame = impl_->diagnostic_frame++;
    const std::size_t cycle_index = measured_frame / 180U;
    const std::size_t frame_in_cycle = measured_frame % 180U;
    const bool sample = impl_->diagnostic_enabled &&
        runtime::should_sample_diagnostic(frame_in_cycle, cycle_index);
    const auto host_roundtrip_begin = std::chrono::steady_clock::now();
    Status status = Status::success();
    if (sample) cudaEventRecord(impl_->trt_begin, impl_->stream);
    if (!impl_->context->setTensorAddress(impl_->input_name.c_str(), impl_->input_device) ||
        !impl_->context->setTensorAddress(impl_->output_name.c_str(), impl_->output_device)) {
        return failure(ErrorCode::kBackendRuntimeError,
                       "TensorRT setTensorAddress failed");
    }
    if (!impl_->context->enqueueV3(impl_->stream)) {
        return failure(ErrorCode::kBackendRuntimeError,
                       "TensorRT enqueueV3 failed");
    }
    if (sample) cudaEventRecord(impl_->trt_end, impl_->stream);
    status = cuda_status(cudaStreamSynchronize(impl_->stream),
                         "cudaStreamSynchronize");
    if (!status.ok()) return status;

    std::size_t output_elements = 0;
    status = core::checked_element_count(impl_->output_info.shape, output_elements);
    if (!status.ok()) return status;
    const auto host_output_begin = std::chrono::steady_clock::now();
    std::vector<float> host_output(output_elements);
    const auto host_output_end = std::chrono::steady_clock::now();
    if (sample) cudaEventRecord(impl_->d2h_begin, impl_->stream);
    status = cuda_status(cudaMemcpyAsync(
        host_output.data(), impl_->output_device, impl_->output_bytes,
        cudaMemcpyDeviceToHost, impl_->stream), "cudaMemcpyAsync device-to-host");
    if (!status.ok()) return status;
    if (sample) cudaEventRecord(impl_->d2h_end, impl_->stream);
    status = cuda_status(cudaStreamSynchronize(impl_->stream),
                         "cudaStreamSynchronize output");
    if (!status.ok()) return status;
    if (sample) {
        float h2d_ms = 0.0F;
        float trt_ms = 0.0F;
        float d2h_ms = 0.0F;
        if (cudaEventElapsedTime(&h2d_ms, impl_->h2d_begin, impl_->h2d_end) != cudaSuccess ||
            cudaEventElapsedTime(&trt_ms, impl_->trt_begin, impl_->trt_end) != cudaSuccess ||
            cudaEventElapsedTime(&d2h_ms, impl_->d2h_begin, impl_->d2h_end) != cudaSuccess) {
            return failure(ErrorCode::kBackendRuntimeError, "TensorRT diagnostic event elapsed time failed");
        }
        impl_->diagnostic_samples.push_back(TensorRtDiagnosticSample{
            measured_frame, cycle_index, frame_in_cycle,
            h2d_ms, trt_ms, d2h_ms,
            std::chrono::duration<double, std::milli>(host_output_end - host_output_begin).count(),
            std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - host_roundtrip_begin).count()});
    }
    for (const float value : host_output) {
        if (!std::isfinite(value)) {
            return failure(ErrorCode::kBackendRuntimeError,
                           "TensorRT output contains a non-finite value");
        }
    }
    core::HostTensor candidate{impl_->output_info, std::move(host_output)};
    status = core::validate_host_tensor(candidate);
    if (!status.ok()) return status;
    *output = std::move(candidate);
    return Status::success();
}

core::Status TensorRtEngine::set_diagnostic_profiling(bool enabled) {
    if (!impl_) return failure(ErrorCode::kBackendRuntimeError, "TensorRtEngine is not initialized");
    if (!enabled) {
        impl_->diagnostic_enabled = false;
        impl_->diagnostic_frame = 0;
        impl_->diagnostic_samples.clear();
        impl_->destroy_diagnostic_events();
        return Status::success();
    }
    if (!impl_->diagnostic_enabled) {
        cudaEvent_t* events[] = {&impl_->h2d_begin, &impl_->h2d_end, &impl_->trt_begin,
                                 &impl_->trt_end, &impl_->d2h_begin, &impl_->d2h_end};
        for (cudaEvent_t* event : events) {
            const cudaError_t error = cudaEventCreate(event);
            if (error != cudaSuccess) {
                impl_->destroy_diagnostic_events();
                return failure(ErrorCode::kBackendInitializationError, "TensorRT diagnostic event creation failed");
            }
        }
        impl_->diagnostic_enabled = true;
    }
    return reset_diagnostic_profiling();
}

core::Status TensorRtEngine::reset_diagnostic_profiling() {
    if (!impl_) return failure(ErrorCode::kBackendRuntimeError, "TensorRtEngine is not initialized");
    impl_->diagnostic_frame = 0;
    impl_->diagnostic_samples.clear();
    return Status::success();
}

const std::vector<TensorRtDiagnosticSample>& TensorRtEngine::diagnostic_samples() const noexcept {
    static const std::vector<TensorRtDiagnosticSample> empty;
    return impl_ ? impl_->diagnostic_samples : empty;
}

}  // namespace edge_ai_defect::backend_tensorrt
