#pragma once

#include <onnxruntime_cxx_api.h>

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace edge_ai_defect::test::ort_smoke {

enum class ContractField {
    kNone,
    kOnnxType,
    kName,
    kElementType,
    kRank,
    kShape,
    kStaticDimension,
};

struct ExpectedTensorContract {
    std::string name;
    ONNXTensorElementDataType element_type;
    std::vector<std::int64_t> shape;
};

struct ActualTensorMetadata {
    std::string name;
    ONNXType onnx_type;
    ONNXTensorElementDataType element_type;
    std::vector<std::int64_t> shape;
};

struct ContractValidationResult {
    bool ok;
    ContractField field;
    std::string expected;
    std::string actual;
    std::string message;
};

std::string format_shape(const std::vector<std::int64_t>& shape);

std::string format_element_type(ONNXTensorElementDataType element_type);

ActualTensorMetadata read_tensor_metadata(
    Ort::Session& session,
    Ort::AllocatorWithDefaultOptions& allocator,
    bool is_input,
    std::size_t index);

ContractValidationResult validate_tensor(
    const std::string& label,
    const ExpectedTensorContract& expected,
    const ActualTensorMetadata& actual);

}  // namespace edge_ai_defect::test::ort_smoke
