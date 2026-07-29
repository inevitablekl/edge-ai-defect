#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <fstream>
#include <filesystem>
#include <iostream>
#include <string>

namespace {
namespace model = edge_ai_defect::model;
namespace runtime = edge_ai_defect::runtime;
namespace inference = edge_ai_defect::inference;

bool write_file(const std::filesystem::path& path, const std::string& text) {
    std::ofstream output(path);
    output << text;
    return output.good();
}

int config_test(const std::filesystem::path& temp) {
    const auto path = temp / "runtime_v3.yaml";
    const std::string yaml = R"yaml(schema_version: 3
backend:
  type: tensorrt_fp16
tensorrt:
  engine_path: /tmp/frozen.engine
  engine_manifest_path: /tmp/frozen.manifest.json
  device_id: 0
runtime:
  opencv_num_threads: 1
model:
  contract_path: /tmp/frozen.yaml
input:
  type: directory
  directory: /tmp/images
output:
  json_path: /tmp/results.json
  console: false
  overwrite: false
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false
)yaml";
    if (!write_file(path, yaml)) return 1;
    runtime::RuntimeConfig config;
    auto status = runtime::RuntimeConfigLoader::load(path, &config);
    if (!status.ok() || config.schema_version != 3U ||
        config.backend_type != "tensorrt_fp16" || config.tensorrt.device_id != 0U ||
        !config.tensorrt.engine_path.is_absolute()) {
        std::cerr << "RuntimeConfig v3 test failed: " << status.message() << '\n';
        return 1;
    }
    const auto unknown = temp / "runtime_v3_unknown.yaml";
    if (!write_file(unknown, yaml + "\nunknown: true\n") ||
        runtime::RuntimeConfigLoader::load(unknown, &config).ok()) return 1;
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: test_k3_foundation <temp-dir> <manifest>\n";
        return 2;
    }
    const std::filesystem::path temp = argv[1];
    std::filesystem::create_directories(temp);
    if (config_test(temp) != 0) return 1;

    model::ModelContract contract;
    auto status = model::ModelContractLoader::load(
        "configs/model_contracts/yolov8n_neudet_frozen.yaml", &contract);
    if (!status.ok()) return 1;
    model::TensorRtEngineManifest manifest;
    status = model::TensorRtEngineManifestLoader::load(argv[2], &contract, &manifest);
    if (!status.ok()) {
        std::cerr << "Manifest test failed: " << status.message() << '\n';
        return 1;
    }
    runtime::RuntimeConfig trt;
    trt.schema_version = 3;
    trt.backend_type = "tensorrt_fp16";
    std::unique_ptr<inference::IInferenceEngine> engine;
    status = inference::create_inference_engine(trt, contract, &engine);
    if (status.ok() || engine) {
        std::cerr << "TensorRT factory must remain unimplemented in K3\n";
        return 1;
    }
    trt.backend_type = "unknown";
    status = inference::create_inference_engine(trt, contract, &engine);
    if (status.ok()) return 1;
    std::cout << "K3 foundation tests passed\n";
    return 0;
}
