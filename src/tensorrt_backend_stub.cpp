#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"

namespace edge_ai_defect::backend_tensorrt {

class TensorRtEngine::Impl {};
TensorRtEngine::TensorRtEngine() = default;
TensorRtEngine::~TensorRtEngine() = default;
core::Status TensorRtEngine::initialize(const model::ModelContract&, const std::filesystem::path&) {
    return core::Status::failure(core::ErrorCode::kBackendInitializationError,
                                 "TensorRT backend is disabled at CMake configure time");
}
core::Status TensorRtEngine::initialize(const runtime::RuntimeConfig&, const model::ModelContract&) {
    return core::Status::failure(core::ErrorCode::kBackendInitializationError,
                                 "TensorRT backend is disabled at CMake configure time");
}
core::Status TensorRtEngine::run(const core::HostTensor&, core::HostTensor*) {
    return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                 "TensorRT backend is disabled at CMake configure time");
}

}  // namespace edge_ai_defect::backend_tensorrt
