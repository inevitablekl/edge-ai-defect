#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace edge_ai_defect::core {

enum class TensorDataType {
    kFloat32,
};

enum class TensorLayout {
    kNchw,
    kBcn,
};

struct TensorInfo {
    TensorDataType dtype = TensorDataType::kFloat32;
    TensorLayout layout = TensorLayout::kNchw;
    std::vector<std::int64_t> shape;
};

struct HostTensor {
    TensorInfo info;
    std::vector<float> data;
};

[[nodiscard]] Status checked_element_count(
    const std::vector<std::int64_t>& shape,
    std::size_t& element_count);

[[nodiscard]] Status validate_tensor_info(const TensorInfo& info);

[[nodiscard]] Status validate_host_tensor(const HostTensor& tensor);

}  // namespace edge_ai_defect::core
