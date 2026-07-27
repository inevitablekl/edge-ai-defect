#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cuda_runtime_api.h>

namespace edge_ai_defect::backend_tensorrt {

[[nodiscard]] core::Status cuda_status(cudaError_t error, const char* operation);

}  // namespace edge_ai_defect::backend_tensorrt
