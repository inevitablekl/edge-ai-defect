#include "tensorrt_logger.hpp"

#include <iostream>

namespace edge_ai_defect::backend_tensorrt {

void TensorRtLogger::log(Severity severity, const char* message) noexcept {
    if (message == nullptr || severity > Severity::kWARNING) return;
    std::cerr << "[TensorRT] " << message << '\n';
}

}  // namespace edge_ai_defect::backend_tensorrt
