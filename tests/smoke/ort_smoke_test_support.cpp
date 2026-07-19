#include "ort_smoke_test_support.hpp"

#include <sstream>
#include <stdexcept>
#include <utility>

namespace edge_ai_defect::test::ort_smoke {
namespace {

ContractValidationResult make_failure(ContractField field,
                                      std::string expected,
                                      std::string actual,
                                      std::string message) {
    return ContractValidationResult{
        false,
        field,
        std::move(expected),
        std::move(actual),
        std::move(message),
    };
}

std::string format_onnx_type(ONNXType onnx_type) {
    if (onnx_type == ONNX_TYPE_TENSOR) {
        return "ONNX_TYPE_TENSOR";
    }
    return "ONNX type " + std::to_string(static_cast<int>(onnx_type));
}

}  // namespace

std::string format_shape(const std::vector<std::int64_t>& shape) {
    std::ostringstream stream;
    stream << '[';
    for (std::size_t index = 0; index < shape.size(); ++index) {
        if (index != 0) {
            stream << ',';
        }
        stream << shape[index];
    }
    stream << ']';
    return stream.str();
}

std::string format_element_type(ONNXTensorElementDataType element_type) {
    if (element_type == ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT) {
        return "float32";
    }
    return "ONNX element type " +
           std::to_string(static_cast<int>(element_type));
}

ActualTensorMetadata read_tensor_metadata(
    Ort::Session& session,
    Ort::AllocatorWithDefaultOptions& allocator,
    bool is_input,
    std::size_t index) {
    auto allocated_name =
        is_input ? session.GetInputNameAllocated(index, allocator)
                 : session.GetOutputNameAllocated(index, allocator);
    if (!allocated_name) {
        throw std::runtime_error("ORT returned a null node name");
    }
    const std::string name(allocated_name.get());

    const Ort::TypeInfo type_info =
        is_input ? session.GetInputTypeInfo(index)
                 : session.GetOutputTypeInfo(index);
    const ONNXType onnx_type = type_info.GetONNXType();
    if (onnx_type != ONNX_TYPE_TENSOR) {
        return ActualTensorMetadata{
            name,
            onnx_type,
            ONNX_TENSOR_ELEMENT_DATA_TYPE_UNDEFINED,
            {},
        };
    }

    const auto tensor_info = type_info.GetTensorTypeAndShapeInfo();
    return ActualTensorMetadata{
        name,
        onnx_type,
        tensor_info.GetElementType(),
        tensor_info.GetShape(),
    };
}

ContractValidationResult validate_tensor(
    const std::string& label,
    const ExpectedTensorContract& expected,
    const ActualTensorMetadata& actual) {
    if (actual.onnx_type != ONNX_TYPE_TENSOR) {
        const std::string expected_type = "ONNX_TYPE_TENSOR";
        const std::string actual_type = format_onnx_type(actual.onnx_type);
        return make_failure(
            ContractField::kOnnxType,
            expected_type,
            actual_type,
            "Expected " + label + " ONNX type: " + expected_type +
                "\nActual " + label + " ONNX type: " + actual_type);
    }

    if (actual.name != expected.name) {
        return make_failure(
            ContractField::kName,
            expected.name,
            actual.name,
            "Expected " + label + " name: " + expected.name +
                "\nActual " + label + " name: " + actual.name);
    }

    if (actual.element_type != expected.element_type) {
        const std::string expected_type =
            format_element_type(expected.element_type);
        const std::string actual_type =
            format_element_type(actual.element_type);
        return make_failure(
            ContractField::kElementType,
            expected_type,
            actual_type,
            "Expected " + label + " dtype: " + expected_type +
                "\nActual " + label + " dtype: " + actual_type);
    }

    if (actual.shape.size() != expected.shape.size()) {
        const std::string expected_rank =
            std::to_string(expected.shape.size());
        const std::string actual_rank = std::to_string(actual.shape.size());
        return make_failure(
            ContractField::kRank,
            expected_rank,
            actual_rank,
            "Expected " + label + " rank: " + expected_rank +
                "\nActual " + label + " rank: " + actual_rank);
    }

    for (std::size_t index = 0; index < actual.shape.size(); ++index) {
        if (actual.shape[index] <= 0) {
            const std::string expected_dimension =
                "positive static dimension at index " +
                std::to_string(index);
            const std::string actual_dimension =
                std::to_string(actual.shape[index]);
            return make_failure(
                ContractField::kStaticDimension,
                expected_dimension,
                actual_dimension,
                "Expected " + label + " " + expected_dimension +
                    "\nActual " + label + " dimension " +
                    std::to_string(index) + ": " + actual_dimension);
        }
    }

    if (actual.shape != expected.shape) {
        const std::string expected_shape = format_shape(expected.shape);
        const std::string actual_shape = format_shape(actual.shape);
        return make_failure(
            ContractField::kShape,
            expected_shape,
            actual_shape,
            "Expected " + label + " shape: " + expected_shape +
                "\nActual " + label + " shape: " + actual_shape);
    }

    return ContractValidationResult{true, ContractField::kNone, "", "", ""};
}

}  // namespace edge_ai_defect::test::ort_smoke
