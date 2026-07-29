#include "cuda_status.hpp"

#include <string>

namespace edge_ai_defect::backend_tensorrt {

core::Status cuda_status(cudaError_t error, const char* operation) {
    if (error == cudaSuccess) return core::Status::success();
    return core::Status::failure(
        core::ErrorCode::kBackendRuntimeError,
        std::string(operation == nullptr ? "CUDA operation" : operation) +
            " failed: " + cudaGetErrorString(error));
}

}  // namespace edge_ai_defect::backend_tensorrt
