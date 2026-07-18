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

bool expect_initialize_failure(const model::ModelContract& contract,
                               const std::filesystem::path& model_path,
                               core::ErrorCode expected_code,
                               const std::string& case_name) {
    backend_ort::OnnxRuntimeEngine engine;
    return expect_code(engine.initialize(contract, model_path), expected_code,
                       case_name);
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

    const std::filesystem::path missing_model =
        arguments.model_path.parent_path() / "m2_4_missing_model.onnx";
    if (!expect_initialize_failure(contract,
                                   missing_model,
                                   core::ErrorCode::kIoError,
                                   "missing model")) {
        return 4;
    }
    if (!expect_initialize_failure(contract,
                                   arguments.model_path.parent_path(),
                                   core::ErrorCode::kIoError,
                                   "non-regular model path")) {
        return 5;
    }

    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.expected_onnx_sha256[0] =
            wrong_contract.expected_onnx_sha256[0] == '0' ? '1' : '0';
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "SHA256 mismatch")) {
            return 6;
        }
    }
    {
        model::ModelContract wrong_contract = contract;
        ++wrong_contract.expected_onnx_size_bytes;
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "size mismatch")) {
            return 7;
        }
    }

    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.input.name = "wrong_input_name";
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "input name mismatch")) {
            return 8;
        }
    }
    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.input.tensor_info.dtype =
            static_cast<core::TensorDataType>(99);
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "input dtype mismatch")) {
            return 9;
        }
    }
    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.input.tensor_info.shape = {1, 3, 320, 1280};
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "input shape mismatch")) {
            return 10;
        }
    }

    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.output.name = "wrong_output_name";
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "output name mismatch")) {
            return 11;
        }
    }
    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.output.tensor_info.dtype =
            static_cast<core::TensorDataType>(99);
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "output dtype mismatch")) {
            return 12;
        }
    }
    {
        model::ModelContract wrong_contract = contract;
        wrong_contract.output.tensor_info.shape = {1, 10, 4200};
        if (!expect_initialize_failure(wrong_contract,
                                       arguments.model_path,
                                       core::ErrorCode::kModelContractMismatch,
                                       "output shape mismatch")) {
            return 13;
        }
    }

    backend_ort::OnnxRuntimeEngine engine;
    const core::Status initialize_status = engine.initialize(contract, arguments.model_path);
    if (!initialize_status.ok()) {
        std::cerr << "positive initialization failed: "
                  << initialize_status.message() << '\n';
        return 14;
    }

    std::cout << "OnnxRuntimeEngine initialization tests passed\n";
    return 0;
}
