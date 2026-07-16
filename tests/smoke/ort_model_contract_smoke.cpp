#include <onnxruntime_cxx_api.h>

#include <cstddef>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

struct ExpectedTensorContract {
    std::string name;
    ONNXTensorElementDataType element_type;
    std::vector<std::int64_t> shape;
};

struct ActualTensorMetadata {
    std::string name;
    ONNXTensorElementDataType element_type;
    std::vector<std::int64_t> shape;
};

struct Arguments {
    std::string mode;
    std::string model_path;
};

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

bool parse_arguments(int argc, char* argv[], Arguments& arguments) {
    if (argc != 5 || std::string(argv[1]) != "--mode" ||
        std::string(argv[3]) != "--model") {
        std::cerr << "Argument error: expected --mode <positive|missing-model|"
                     "contract-mismatch> --model <onnx-path>\n";
        return false;
    }

    arguments.mode = argv[2];
    arguments.model_path = argv[4];
    if (arguments.mode != "positive" &&
        arguments.mode != "missing-model" &&
        arguments.mode != "contract-mismatch") {
        std::cerr << "Argument error: unknown mode: " << arguments.mode << '\n';
        return false;
    }
    if (arguments.model_path.empty()) {
        std::cerr << "Argument error: model path is empty\n";
        return false;
    }
    return true;
}

ActualTensorMetadata read_tensor_metadata(Ort::Session& session,
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
    const auto tensor_info = type_info.GetTensorTypeAndShapeInfo();

    return ActualTensorMetadata{
        name,
        tensor_info.GetElementType(),
        tensor_info.GetShape(),
    };
}

void validate_tensor(const std::string& label,
                     const ExpectedTensorContract& expected,
                     const ActualTensorMetadata& actual,
                     std::vector<std::string>& errors) {
    if (actual.name != expected.name) {
        errors.push_back("Expected " + label + " name: " + expected.name +
                         "\nActual " + label + " name: " + actual.name);
    }

    if (actual.element_type != expected.element_type) {
        errors.push_back(
            "Expected " + label + " dtype: " +
            format_element_type(expected.element_type) + "\nActual " + label +
            " dtype: " + format_element_type(actual.element_type));
    }

    if (actual.shape.size() != expected.shape.size()) {
        errors.push_back("Expected " + label + " rank: " +
                         std::to_string(expected.shape.size()) + "\nActual " +
                         label + " rank: " +
                         std::to_string(actual.shape.size()));
    }

    for (std::size_t index = 0; index < actual.shape.size(); ++index) {
        if (actual.shape[index] <= 0) {
            errors.push_back("Expected " + label + " dimension " +
                             std::to_string(index) +
                             " to be a positive static value\nActual " + label +
                             " dimension " + std::to_string(index) + ": " +
                             std::to_string(actual.shape[index]));
        }
    }

    if (actual.shape != expected.shape) {
        errors.push_back("Expected " + label + " shape: " +
                         format_shape(expected.shape) + "\nActual " + label +
                         " shape: " + format_shape(actual.shape));
    }
}

void print_errors(const std::vector<std::string>& errors) {
    for (const std::string& error : errors) {
        std::cerr << error << '\n';
    }
}

int run_missing_model(const Arguments& arguments,
                      Ort::Env& environment,
                      Ort::SessionOptions& session_options) {
    if (std::filesystem::exists(arguments.model_path)) {
        std::cerr << "Model load error: missing-model path unexpectedly exists: "
                  << arguments.model_path << '\n';
        return 3;
    }

    try {
        Ort::Session session(environment, arguments.model_path.c_str(),
                             session_options);
    } catch (const Ort::Exception& exception) {
        std::cout << "Expected model load failure detected: PASS\n"
                  << "ORT message: " << exception.what() << '\n'
                  << "M0.4 missing-model smoke: PASS\n";
        return 0;
    }

    std::cerr << "Model load error: nonexistent model unexpectedly loaded\n";
    return 3;
}

}  // namespace

int main(int argc, char* argv[]) {
    Arguments arguments;
    if (!parse_arguments(argc, argv, arguments)) {
        return 2;
    }

    std::string stage = "Ort::Env creation";
    try {
        Ort::Env environment(ORT_LOGGING_LEVEL_WARNING,
                             "edge_ai_m0_model_contract_smoke");
        stage = "Ort::SessionOptions creation";
        Ort::SessionOptions session_options;

        if (arguments.mode == "missing-model") {
            return run_missing_model(arguments, environment, session_options);
        }

        stage = "model loading";
        Ort::Session session(environment, arguments.model_path.c_str(),
                             session_options);
        std::cout << "Model load: PASS\n";

        stage = "model metadata query";
        const std::size_t input_count = session.GetInputCount();
        const std::size_t output_count = session.GetOutputCount();
        std::vector<std::string> errors;
        if (input_count != 1) {
            errors.push_back("Expected input count: 1\nActual input count: " +
                             std::to_string(input_count));
        }
        if (output_count != 1) {
            errors.push_back("Expected output count: 1\nActual output count: " +
                             std::to_string(output_count));
        }

        Ort::AllocatorWithDefaultOptions allocator;
        ActualTensorMetadata input_metadata;
        ActualTensorMetadata output_metadata;
        if (input_count > 0) {
            input_metadata =
                read_tensor_metadata(session, allocator, true, 0);
        }
        if (output_count > 0) {
            output_metadata =
                read_tensor_metadata(session, allocator, false, 0);
        }

        ExpectedTensorContract expected_input{
            arguments.mode == "contract-mismatch" ? "wrong_images" : "images",
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT,
            {1, 3, 640, 640},
        };
        const ExpectedTensorContract expected_output{
            "output0",
            ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT,
            {1, 10, 8400},
        };

        if (input_count > 0) {
            validate_tensor("input", expected_input, input_metadata, errors);
        }
        if (output_count > 0) {
            validate_tensor("output", expected_output, output_metadata, errors);
        }

        if (arguments.mode == "contract-mismatch") {
            if (errors.size() == 1 &&
                errors.front().find("Expected input name: wrong_images") !=
                    std::string::npos &&
                errors.front().find("Actual input name: images") !=
                    std::string::npos) {
                print_errors(errors);
                std::cout << "Expected contract mismatch detected: PASS\n"
                          << "M0.4 contract-mismatch smoke: PASS\n";
                return 0;
            }

            std::cerr << "Contract mismatch mode did not detect exactly the "
                         "intended input-name difference\n";
            print_errors(errors);
            return 4;
        }

        if (!errors.empty()) {
            print_errors(errors);
            return 4;
        }

        std::cout << "Input count: " << input_count << '\n'
                  << "Input name: " << input_metadata.name << '\n'
                  << "Input dtype: "
                  << format_element_type(input_metadata.element_type) << '\n'
                  << "Input shape: " << format_shape(input_metadata.shape)
                  << '\n'
                  << "Output count: " << output_count << '\n'
                  << "Output name: " << output_metadata.name << '\n'
                  << "Output dtype: "
                  << format_element_type(output_metadata.element_type) << '\n'
                  << "Output shape: " << format_shape(output_metadata.shape)
                  << '\n'
                  << "Static dimensions: PASS\n"
                  << "Model contract: PASS\n"
                  << "M0.4 model contract smoke: PASS\n";
        return 0;
    } catch (const Ort::Exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; Ort::Exception message: " << exception.what() << '\n';
        return stage == "model loading" ? 3 : 5;
    } catch (const std::exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; std::exception message: " << exception.what() << '\n';
    } catch (...) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; exception message: unknown exception\n";
    }

    return 6;
}
