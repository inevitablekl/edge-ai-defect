#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

namespace {
namespace backend = edge_ai_defect::backend_tensorrt;
namespace core = edge_ai_defect::core;
namespace model = edge_ai_defect::model;
namespace runtime = edge_ai_defect::runtime;

bool write_text(const std::filesystem::path& path, const std::string& text) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output << text;
    return output.good();
}

std::string read_text(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

std::string replace_once(std::string source, const std::string& from,
                         const std::string& to) {
    const std::size_t position = source.find(from);
    if (position == std::string::npos) return {};
    source.replace(position, from.size(), to);
    return source;
}

runtime::RuntimeConfig config_for(const std::filesystem::path& engine,
                                  const std::filesystem::path& manifest,
                                  const std::filesystem::path& contract) {
    runtime::RuntimeConfig config;
    config.schema_version = 3;
    config.backend_type = "tensorrt_fp16";
    config.tensorrt.engine_path = engine;
    config.tensorrt.engine_manifest_path = manifest;
    config.model_contract_path = contract;
    config.tensorrt.device_id = 0;
    return config;
}

core::HostTensor valid_input(const model::ModelContract& contract) {
    std::size_t count = 0;
    if (!core::checked_element_count(contract.input.tensor_info.shape, count).ok()) return {};
    return {contract.input.tensor_info, std::vector<float>(count, 0.0F)};
}

bool same_output(const core::HostTensor& left, const core::HostTensor& right) {
    return left.info.dtype == right.info.dtype && left.info.layout == right.info.layout &&
           left.info.shape == right.info.shape && left.data == right.data;
}

bool expect_failure_without_output(backend::TensorRtEngine& engine,
                                   const core::HostTensor& input,
                                   const core::HostTensor& sentinel) {
    core::HostTensor output = sentinel;
    const core::Status status = engine.run(input, &output);
    return !status.ok() && same_output(output, sentinel);
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc != 5) {
        std::cerr << "Usage: test_tensorrt_engine <engine> <manifest> <contract> <temp-dir>\n";
        return 2;
    }
    const std::filesystem::path engine_path = argv[1];
    const std::filesystem::path manifest_path = argv[2];
    const std::filesystem::path contract_path = argv[3];
    const std::filesystem::path temp_dir = argv[4];
    std::filesystem::create_directories(temp_dir);

    model::ModelContract contract;
    core::Status status = model::ModelContractLoader::load(contract_path, &contract);
    if (!status.ok()) return 1;
    const core::HostTensor input = valid_input(contract);
    const core::HostTensor sentinel{contract.output.tensor_info, {7.0F, 8.0F, 9.0F}};

    backend::TensorRtEngine engine;
    status = engine.initialize(config_for(engine_path, manifest_path, contract_path), contract);
    if (!status.ok()) {
        std::cerr << "valid initialization failed: " << status.message() << '\n';
        return 1;
    }
    if (engine.run(input, nullptr).ok()) {
        std::cerr << "null output must fail\n";
        return 1;
    }
    core::HostTensor invalid_shape = input;
    invalid_shape.info.shape[3] = 320;
    if (!expect_failure_without_output(engine, invalid_shape, sentinel)) {
        std::cerr << "invalid shape must fail without mutation\n";
        return 1;
    }
    core::HostTensor empty_input = input;
    empty_input.data.clear();
    if (!expect_failure_without_output(engine, empty_input, sentinel)) {
        std::cerr << "empty input must fail without mutation\n";
        return 1;
    }
    core::HostTensor output = sentinel;
    status = engine.run(input, &output);
    if (!status.ok() || output.info.shape != contract.output.tensor_info.shape ||
        output.data.empty()) {
        std::cerr << "inference failed: " << status.message() << '\n';
        return 1;
    }
    for (const float value : output.data) {
        if (!std::isfinite(value)) {
            std::cerr << "output contains non-finite value\n";
            return 1;
        }
    }
    const std::size_t first_size = output.data.size();
    status = engine.run(input, &output);
    if (!status.ok() || output.data.size() != first_size) {
        std::cerr << "second persistent-buffer inference failed\n";
        return 1;
    }

    const std::string manifest_text = read_text(manifest_path);
    const std::string bad_hash = replace_once(
        manifest_text,
        "6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc",
        std::string(64, '0'));
    const auto bad_hash_manifest = temp_dir / "bad_engine_hash.manifest.json";
    if (bad_hash.empty() || !write_text(bad_hash_manifest, bad_hash)) return 1;
    backend::TensorRtEngine bad_hash_engine;
    if (bad_hash_engine.initialize(config_for(engine_path, bad_hash_manifest, contract_path), contract).ok()) return 1;

    const std::string bad_contract_hash = replace_once(
        manifest_text,
        "9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190",
        std::string(64, '0'));
    const auto bad_contract_manifest = temp_dir / "bad_contract_hash.manifest.json";
    if (bad_contract_hash.empty() || !write_text(bad_contract_manifest, bad_contract_hash)) return 1;
    backend::TensorRtEngine bad_contract_engine;
    if (bad_contract_engine.initialize(config_for(engine_path, bad_contract_manifest, contract_path), contract).ok()) return 1;

    model::ModelContract bad_model_contract = contract;
    bad_model_contract.format = "not_onnx";
    backend::TensorRtEngine bad_model_engine;
    if (bad_model_engine.initialize(config_for(engine_path, manifest_path, contract_path), bad_model_contract).ok()) return 1;

    model::ModelContract mismatched_contract = contract;
    mismatched_contract.output.name = "wrong_output";
    backend::TensorRtEngine mismatched_engine;
    if (mismatched_engine.initialize(config_for(engine_path, manifest_path, contract_path), mismatched_contract).ok()) return 1;

    std::cout << "TensorRtEngine tests passed\n";
    return 0;
}
