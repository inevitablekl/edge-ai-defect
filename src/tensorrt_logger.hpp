#pragma once

#include <NvInferRuntime.h>

namespace edge_ai_defect::backend_tensorrt {

class TensorRtLogger final : public nvinfer1::ILogger {
public:
    void log(Severity severity, const char* message) noexcept override;
};

}  // namespace edge_ai_defect::backend_tensorrt
