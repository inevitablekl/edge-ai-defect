#include "ort_smoke_test_support.hpp"

#include <onnxruntime_cxx_api.h>

#include <exception>
#include <filesystem>
#include <iostream>
#include <string>

namespace {

namespace smoke_support = edge_ai_defect::test::ort_smoke;

struct Arguments {
    std::string mode;
    std::string model_path;
};

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

void print_validation_failure(
    const smoke_support::ContractValidationResult& result) {
    if (!result.ok) {
        std::cerr << result.message << '\n';
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
        const OrtErrorCode error_code = exception.GetOrtErrorCode();
        std::cout << "ORT error code: " << static_cast<int>(error_code) << '\n'
                  << "ORT message: " << exception.what() << '\n';
        if (error_code == ORT_NO_SUCHFILE) {
            std::cout << "Expected ORT_NO_SUCHFILE detected: PASS\n"
                      << "M0.4 missing-model smoke: PASS\n";
            return 0;
        }

        std::cerr << "Unexpected ORT error for missing model; expected code: "
                  << static_cast<int>(ORT_NO_SUCHFILE)
                  << "; actual code: " << static_cast<int>(error_code) << '\n';
        return 5;
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
        bool counts_match = true;
        if (input_count != 1) {
            std::cerr << "Expected input count: 1\nActual input count: "
                      << input_count << '\n';
            counts_match = false;
        }
        if (output_count != 1) {
            std::cerr << "Expected output count: 1\nActual output count: "
                      << output_count << '\n';
            counts_match = false;
        }
        if (!counts_match) {
            return 4;
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

        if (arguments.mode == "contract-mismatch") {
            if (!input_result.ok || !output_result.ok) {
                std::cerr << "Actual model contract must be valid before the "
                             "intentional mismatch check\n";
                print_validation_failure(input_result);
                print_validation_failure(output_result);
                return 4;
            }

            smoke_support::ExpectedTensorContract wrong_input = expected_input;
            wrong_input.name = "wrong_images";
            const smoke_support::ContractValidationResult mismatch_result =
                smoke_support::validate_tensor("input", wrong_input,
                                               input_metadata);
            if (!mismatch_result.ok &&
                mismatch_result.field == smoke_support::ContractField::kName &&
                mismatch_result.expected == "wrong_images" &&
                mismatch_result.actual == "images") {
                print_validation_failure(mismatch_result);
                std::cout << "Expected structured name mismatch detected: PASS\n"
                          << "M0.4 contract-mismatch smoke: PASS\n";
                return 0;
            }

            std::cerr << "Contract mismatch mode did not detect exactly the "
                         "intended structured input-name difference\n";
            print_validation_failure(mismatch_result);
            return 4;
        }

        if (!input_result.ok || !output_result.ok) {
            print_validation_failure(input_result);
            print_validation_failure(output_result);
            return 4;
        }

        std::cout << "Input count: " << input_count << '\n'
                  << "Input name: " << input_metadata.name << '\n'
                  << "Input dtype: "
                  << smoke_support::format_element_type(
                         input_metadata.element_type)
                  << '\n'
                  << "Input shape: "
                  << smoke_support::format_shape(input_metadata.shape) << '\n'
                  << "Output count: " << output_count << '\n'
                  << "Output name: " << output_metadata.name << '\n'
                  << "Output dtype: "
                  << smoke_support::format_element_type(
                         output_metadata.element_type)
                  << '\n'
                  << "Output shape: "
                  << smoke_support::format_shape(output_metadata.shape) << '\n'
                  << "Static dimensions: PASS\n"
                  << "Model contract: PASS\n"
                  << "M0.4 model contract smoke: PASS\n";
        return 0;
    } catch (const Ort::Exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; Ort::Exception code: "
                  << static_cast<int>(exception.GetOrtErrorCode())
                  << "; message: " << exception.what() << '\n';
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
