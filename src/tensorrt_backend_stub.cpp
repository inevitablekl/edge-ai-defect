#include "edge_ai_defect/core/status.hpp"

namespace edge_ai_defect::backend_tensorrt {

core::Status status_not_implemented() {
    return core::Status::failure(
        core::ErrorCode::kBackendInitializationError,
        "TensorRT inference is reserved for K4");
}

}  // namespace edge_ai_defect::backend_tensorrt
