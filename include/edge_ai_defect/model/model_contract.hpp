#pragma once

#include "edge_ai_defect/core/tensor.hpp"

#include <cstdint>
#include <string>
#include <vector>

namespace edge_ai_defect::model {

struct TensorContract {
    std::string name;
    core::TensorInfo tensor_info;
};

struct ModelContract {
    std::uint32_t schema_version = 0;
    std::string model_id;
    std::string format;
    std::string expected_onnx_sha256;
    std::uint64_t expected_onnx_size_bytes = 0;
    TensorContract input;
    TensorContract output;
    std::vector<std::string> class_names;
};

}  // namespace edge_ai_defect::model
