#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"

#include <cmath>
#include <cstddef>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

namespace backend_ort = edge_ai_defect::backend_ort;
namespace core = edge_ai_defect::core;
namespace model = edge_ai_defect::model;

struct Arguments {
    std::filesystem::path contract_path;
    std::filesystem::path model_path;
};

bool parse_arguments(int argc, char* argv[], Arguments& arguments) {
    if (argc != 5 || std::string(argv[1]) != "--contract" ||
        std::string(argv[3]) != "--model") {
        std::cerr << "Expected --contract <path> --model <path>\n";
        return false;
    }
    arguments.contract_path = argv[2];
    arguments.model_path = argv[4];
    return !arguments.contract_path.empty() && !arguments.model_path.empty();
}

bool expect_failure(const core::Status& status,
                    core::ErrorCode expected_code,
                    const std::string& case_name) {
    if (!status.ok() && status.code() == expected_code) {
        return true;
    }
    std::cerr << case_name << " failed: expected error code "
              << static_cast<int>(expected_code) << ", actual "
              << static_cast<int>(status.code()) << "; message: "
              << status.message() << '\n';
    return false;
}

core::HostTensor make_constant_input(const core::TensorInfo& info) {
    std::size_t element_count = 0;
    const core::Status count_status =
        core::checked_element_count(info.shape, element_count);
    if (!count_status.ok()) {
        throw std::runtime_error("Test input shape must be valid");
    }
    return core::HostTensor{info, std::vector<float>(element_count, 0.5F)};
}

bool output_is_unchanged(const core::HostTensor& output,
                         const core::HostTensor& expected) {
    return output.info.dtype == expected.info.dtype &&
           output.info.layout == expected.info.layout &&
           output.info.shape == expected.info.shape && output.data == expected.data;
}

}  // namespace

int main(int argc, char* argv[]) {
    Arguments arguments;
    if (!parse_arguments(argc, argv, arguments)) {
        return 2;
    }

    model::ModelContract contract;
    const core::Status load_status =
        model::ModelContractLoader::load(arguments.contract_path, &contract);
    if (!load_status.ok()) {
        std::cerr << "Cannot load test contract: " << load_status.message() << '\n';
        return 3;
    }
    const core::HostTensor input = make_constant_input(contract.input.tensor_info);
    const core::HostTensor sentinel{
        {core::TensorDataType::kFloat32, core::TensorLayout::kBcn, {1, 1, 1}},
        {42.0F},
    };

    {
        backend_ort::OnnxRuntimeEngine uninitialized_engine;
        core::HostTensor output = sentinel;
        const core::Status status = uninitialized_engine.run(input, &output);
        if (!expect_failure(status,
                            core::ErrorCode::kBackendRuntimeError,
                            "uninitialized engine") ||
            !output_is_unchanged(output, sentinel)) {
            return 4;
        }
    }

    backend_ort::OnnxRuntimeEngine engine;
    const core::Status initialize_status = engine.initialize(contract, arguments.model_path);
    if (!initialize_status.ok()) {
        std::cerr << "Engine initialization failed: " << initialize_status.message()
                  << '\n';
        return 5;
    }

    {
        core::HostTensor invalid_shape = input;
        invalid_shape.info.shape = {1, 3, 320, 1280};
        core::HostTensor output = sentinel;
        const core::Status status = engine.run(invalid_shape, &output);
        if (!expect_failure(status, core::ErrorCode::kInvalidShape, "invalid shape") ||
            !output_is_unchanged(output, sentinel)) {
            return 6;
        }
    }

    {
        core::HostTensor invalid_dtype = input;
        invalid_dtype.info.dtype = static_cast<core::TensorDataType>(99);
        core::HostTensor output = sentinel;
        const core::Status status = engine.run(invalid_dtype, &output);
        if (!expect_failure(status,
                            core::ErrorCode::kUnsupportedDataType,
                            "invalid dtype") ||
            !output_is_unchanged(output, sentinel)) {
            return 7;
        }
    }

    {
        core::HostTensor invalid_layout = input;
        invalid_layout.info.layout = core::TensorLayout::kBcn;
        core::HostTensor output = sentinel;
        const core::Status status = engine.run(invalid_layout, &output);
        if (!expect_failure(status,
                            core::ErrorCode::kUnsupportedLayout,
                            "invalid layout") ||
            !output_is_unchanged(output, sentinel)) {
            return 8;
        }
    }

    core::HostTensor first_output = sentinel;
    const core::Status first_run_status = engine.run(input, &first_output);
    if (!first_run_status.ok()) {
        std::cerr << "First run failed: " << first_run_status.message() << '\n';
        return 9;
    }
    if (first_output.info.dtype != core::TensorDataType::kFloat32 ||
        first_output.info.layout != core::TensorLayout::kBcn ||
        first_output.info.shape != contract.output.tensor_info.shape ||
        first_output.data.size() != 84000U) {
        std::cerr << "First run output contract mismatch\n";
        return 10;
    }
    for (const float value : first_output.data) {
        if (!std::isfinite(value)) {
            std::cerr << "First run output contains a non-finite value\n";
            return 11;
        }
    }

    core::HostTensor second_output;
    const core::Status second_run_status = engine.run(input, &second_output);
    if (!second_run_status.ok()) {
        std::cerr << "Second run failed: " << second_run_status.message() << '\n';
        return 12;
    }
    if (second_output.info.shape != first_output.info.shape ||
        second_output.data != first_output.data) {
        std::cerr << "Consecutive run outputs differ\n";
        return 13;
    }

    std::cout << "OnnxRuntimeEngine run tests passed\n";
    return 0;
}
