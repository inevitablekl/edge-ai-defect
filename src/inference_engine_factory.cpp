#include "edge_ai_defect/inference/inference_engine_factory.hpp"

#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"

namespace edge_ai_defect::inference {

core::Status create_inference_engine(
    const runtime::RuntimeConfig& config,
    const model::ModelContract& contract,
    std::unique_ptr<IInferenceEngine>* output) {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "inference engine output must not be null");
    }
    output->reset();
    if (config.backend_type == "onnxruntime_cpu") {
        auto engine = std::make_unique<backend_ort::OnnxRuntimeEngine>();
        core::Status status = config.schema_version == 2U
                                  ? engine->initialize(config, contract, config.model_path)
                                  : engine->initialize(contract, config.model_path);
        if (!status.ok()) return status;
        *output = std::move(engine);
        return core::Status::success();
    }
    if (config.backend_type == "tensorrt_fp16") {
        return core::Status::failure(
            core::ErrorCode::kBackendInitializationError,
            "TensorRT backend factory dispatch is not implemented until K4");
    }
    return core::Status::failure(core::ErrorCode::kSchemaViolation,
                                 "unsupported backend.type: " + config.backend_type);
}

}  // namespace edge_ai_defect::inference
