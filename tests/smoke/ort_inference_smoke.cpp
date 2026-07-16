#include "ort_smoke_test_support.hpp"

#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

namespace smoke_support = edge_ai_defect::test::ort_smoke;

constexpr std::size_t kExpectedInputElementCount = 1228800;
constexpr std::size_t kExpectedOutputElementCount = 84000;
constexpr float kSyntheticInputValue = 0.5F;

bool parse_model_argument(int argc, char* argv[], std::string& model_path) {
    if (argc != 3 || std::string(argv[1]) != "--model") {
        std::cerr << "Argument error: expected --model <onnx-path>\n";
        return false;
    }
    model_path = argv[2];
    if (model_path.empty()) {
        std::cerr << "Argument error: model path is empty\n";
        return false;
    }
    return true;
}

std::size_t element_count(const std::vector<std::int64_t>& shape) {
    std::size_t count = 1;
    for (const std::int64_t dimension : shape) {
        if (dimension <= 0) {
            throw std::runtime_error(
                "Cannot count elements for a non-positive dimension");
        }
        count *= static_cast<std::size_t>(dimension);
    }
    return count;
}

void print_validation_failure(
    const smoke_support::ContractValidationResult& result) {
    if (!result.ok) {
        std::cerr << result.message << '\n';
    }
}

}  // namespace

int main(int argc, char* argv[]) {
    std::string model_path;
    if (!parse_model_argument(argc, argv, model_path)) {
        return 2;
    }

    std::string stage = "Ort::Env creation";
    try {
        Ort::Env environment(ORT_LOGGING_LEVEL_WARNING,
                             "edge_ai_m0_inference_smoke");
        stage = "Ort::SessionOptions creation";
        Ort::SessionOptions session_options;
        stage = "model load";
        Ort::Session session(environment, model_path.c_str(), session_options);

        stage = "metadata validation";
        const std::size_t input_count = session.GetInputCount();
        const std::size_t output_count = session.GetOutputCount();
        if (input_count != 1 || output_count != 1) {
            std::cerr << "Expected input/output counts: 1/1\nActual input/output "
                         "counts: "
                      << input_count << '/' << output_count << '\n';
            return 3;
        }

        Ort::AllocatorWithDefaultOptions allocator;
        const smoke_support::ActualTensorMetadata input_metadata =
            smoke_support::read_tensor_metadata(session, allocator, true, 0);
        const smoke_support::ActualTensorMetadata output_metadata =
            smoke_support::read_tensor_metadata(session, allocator, false, 0);
        const smoke_support::ExpectedTensorContract expected_input{
            "images",
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT,
            {1, 3, 640, 640},
        };
        const smoke_support::ExpectedTensorContract expected_output{
            "output0",
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT,
            {1, 10, 8400},
        };
        const smoke_support::ContractValidationResult input_result =
            smoke_support::validate_tensor("input", expected_input,
                                           input_metadata);
        const smoke_support::ContractValidationResult output_result =
            smoke_support::validate_tensor("output", expected_output,
                                           output_metadata);
        if (!input_result.ok || !output_result.ok) {
            print_validation_failure(input_result);
            print_validation_failure(output_result);
            return 3;
        }
        std::cout << "Model contract: PASS\n";

        const std::size_t input_element_count =
            element_count(expected_input.shape);
        if (input_element_count != kExpectedInputElementCount) {
            std::cerr << "Synthetic input element count mismatch: expected "
                      << kExpectedInputElementCount << ", actual "
                      << input_element_count << '\n';
            return 4;
        }

        std::vector<float> input_data(input_element_count,
                                      kSyntheticInputValue);
        if (input_data.size() != kExpectedInputElementCount ||
            !std::all_of(input_data.begin(), input_data.end(), [](float value) {
                return value == kSyntheticInputValue;
            })) {
            std::cerr << "Synthetic input buffer validation failed\n";
            return 4;
        }

        stage = "input tensor creation";
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault);
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info,
            input_data.data(),
            input_data.size(),
            expected_input.shape.data(),
            expected_input.shape.size());
        if (!input_tensor.IsTensor()) {
            std::cerr << "Input tensor creation failed: value is not a tensor\n";
            return 4;
        }

        const Ort::TensorTypeAndShapeInfo input_tensor_info =
            input_tensor.GetTensorTypeAndShapeInfo();
        if (input_tensor_info.GetElementType() !=
                ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT ||
            input_tensor_info.GetShape() != expected_input.shape ||
            input_tensor_info.GetElementCount() != input_data.size()) {
            std::cerr << "Input tensor metadata validation failed\n";
            return 4;
        }
        std::cout << "Synthetic input shape: "
                  << smoke_support::format_shape(expected_input.shape) << '\n'
                  << "Synthetic input elements: " << input_data.size() << '\n'
                  << "Synthetic input value: " << kSyntheticInputValue << '\n'
                  << "Input tensor creation: PASS\n";

        const std::string input_name = input_metadata.name;
        const std::string output_name = output_metadata.name;
        const char* input_names[] = {input_name.c_str()};
        const char* output_names[] = {output_name.c_str()};

        stage = "session run";
        Ort::RunOptions run_options;
        std::vector<Ort::Value> output_tensors = session.Run(
            run_options,
            input_names,
            &input_tensor,
            1,
            output_names,
            1);
        std::cout << "Session::Run: PASS\n";

        stage = "output validation";
        if (output_tensors.size() != 1) {
            std::cerr << "Expected output tensor count: 1\nActual output tensor "
                         "count: "
                      << output_tensors.size() << '\n';
            return 5;
        }

        const Ort::Value& output_tensor = output_tensors.front();
        if (!output_tensor.IsTensor()) {
            std::cerr << "Output validation failed: output is not a tensor\n";
            return 5;
        }
        const Ort::TensorTypeAndShapeInfo output_tensor_info =
            output_tensor.GetTensorTypeAndShapeInfo();
        const std::vector<std::int64_t> output_shape =
            output_tensor_info.GetShape();
        const std::size_t output_element_count =
            output_tensor_info.GetElementCount();
        if (output_tensor_info.GetElementType() !=
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT) {
            std::cerr << "Expected output dtype: float32\nActual output dtype: "
                      << smoke_support::format_element_type(
                             output_tensor_info.GetElementType())
                      << '\n';
            return 5;
        }
        if (output_shape != expected_output.shape) {
            std::cerr << "Expected output shape: "
                      << smoke_support::format_shape(expected_output.shape)
                      << "\nActual output shape: "
                      << smoke_support::format_shape(output_shape) << '\n';
            return 5;
        }
        if (output_element_count != kExpectedOutputElementCount) {
            std::cerr << "Expected output elements: "
                      << kExpectedOutputElementCount
                      << "\nActual output elements: " << output_element_count
                      << '\n';
            return 5;
        }

        const float* output_data = output_tensor.GetTensorData<float>();
        if (output_data == nullptr) {
            std::cerr << "Output validation failed: tensor data is null\n";
            return 5;
        }
        std::size_t finite_count = 0;
        std::size_t nan_count = 0;
        std::size_t positive_infinity_count = 0;
        std::size_t negative_infinity_count = 0;
        float minimum = std::numeric_limits<float>::infinity();
        float maximum = -std::numeric_limits<float>::infinity();
        for (std::size_t index = 0; index < output_element_count; ++index) {
            const float value = output_data[index];
            if (std::isnan(value)) {
                ++nan_count;
            } else if (std::isinf(value)) {
                if (std::signbit(value)) {
                    ++negative_infinity_count;
                } else {
                    ++positive_infinity_count;
                }
            } else {
                ++finite_count;
                minimum = std::min(minimum, value);
                maximum = std::max(maximum, value);
            }
        }

        std::cout << "Output tensor count: " << output_tensors.size() << '\n'
                  << "Output shape: "
                  << smoke_support::format_shape(output_shape) << '\n'
                  << "Output elements: " << output_element_count << '\n'
                  << "Finite count: " << finite_count << '\n'
                  << "NaN count: " << nan_count << '\n'
                  << "Positive infinity count: "
                  << positive_infinity_count << '\n'
                  << "Negative infinity count: "
                  << negative_infinity_count << '\n';
        if (finite_count > 0) {
            std::cout << "Output min: " << minimum << '\n'
                      << "Output max: " << maximum << '\n';
        }

        if (finite_count != kExpectedOutputElementCount || nan_count != 0 ||
            positive_infinity_count != 0 || negative_infinity_count != 0) {
            std::cerr << "Output finite-value validation failed\n";
            return 5;
        }

        std::cout << "M0.5 synthetic inference smoke: PASS\n";
        return 0;
    } catch (const Ort::Exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; Ort::Exception code: "
                  << static_cast<int>(exception.GetOrtErrorCode())
                  << "; message: " << exception.what() << '\n';
    } catch (const std::exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; std::exception message: " << exception.what() << '\n';
    } catch (...) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; exception message: unknown exception\n";
    }

    return 6;
}
