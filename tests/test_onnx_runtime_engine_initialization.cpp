#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"

#include <filesystem>
#include <iostream>
#include <string>

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

bool expect_code(const core::Status& status,
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

    {
        backend_ort::OnnxRuntimeEngine engine;
        const core::Status status = engine.initialize(
            contract, "missing_model_for_m2_2_initialization_test.onnx");
        if (!expect_code(status, core::ErrorCode::kIoError, "missing model")) {
            return 4;
        }
    }

    {
        backend_ort::OnnxRuntimeEngine engine;
        model::ModelContract wrong_contract = contract;
        wrong_contract.format = "not-onnx";
        const core::Status status =
            engine.initialize(wrong_contract, arguments.model_path);
        if (!expect_code(status,
                         core::ErrorCode::kModelContractMismatch,
                         "invalid contract")) {
            return 5;
        }
    }

    {
        backend_ort::OnnxRuntimeEngine engine;
        model::ModelContract wrong_contract = contract;
        wrong_contract.input.name = "wrong_input_name";
        const core::Status status =
            engine.initialize(wrong_contract, arguments.model_path);
        if (!expect_code(status,
                         core::ErrorCode::kModelContractMismatch,
                         "input metadata mismatch")) {
            return 6;
        }
    }

    {
        backend_ort::OnnxRuntimeEngine engine;
        model::ModelContract wrong_contract = contract;
        wrong_contract.output.name = "wrong_output_name";
        const core::Status status =
            engine.initialize(wrong_contract, arguments.model_path);
        if (!expect_code(status,
                         core::ErrorCode::kModelContractMismatch,
                         "output metadata mismatch")) {
            return 7;
        }
    }

    backend_ort::OnnxRuntimeEngine engine;
    const core::Status initialize_status = engine.initialize(contract, arguments.model_path);
    if (!initialize_status.ok()) {
        std::cerr << "positive initialization failed: "
                  << initialize_status.message() << '\n';
        return 8;
    }

    std::cout << "OnnxRuntimeEngine initialization tests passed\n";
    return 0;
}
