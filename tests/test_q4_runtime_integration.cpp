#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

namespace {
namespace fs = std::filesystem;
using namespace edge_ai_defect;

bool write_file(const fs::path& path, const std::string& text) {
    std::ofstream output(path);
    output << text;
    return output.good();
}

std::string config_yaml(const fs::path& output, const std::string& backend,
                        const fs::path& manifest) {
    return "schema_version: 5\nbackend:\n  type: " + backend +
           "\ntensorrt:\n  engine_path: /home/orin/edge-ai-local-models/stage_q/formal/yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine\n  engine_manifest_path: " + manifest.string() +
           "\n  device_id: 0\nmodel:\n  contract_path: configs/model_contracts/yolov8n_neudet_frozen.yaml\nruntime:\n  mode: serial\n  opencv_num_threads: 1\ninput:\n  type: directory\n  directory: data/raw/NEU-DET/IMAGES\noutput:\n  json_path: " + output.string() +
           "\n  console: false\n  overwrite: true\npostprocess:\n  conf_threshold: 0.25\n  iou_threshold: 0.45\n  max_nms: 30000\n  max_det: 300\n  max_wh: 7680\n  agnostic: false\ntiming:\n  enabled: false\n";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const fs::path temp = argv[1];
    fs::create_directories(temp);
    const fs::path manifest = "/home/orin/edge-ai-local-models/stage_q/formal/engine_manifest_v2.json";
    const fs::path contract_path = "configs/model_contracts/yolov8n_neudet_frozen.yaml";

    runtime::RuntimeConfig config;
    const fs::path config_path = temp / "runtime_v5.yaml";
    if (!write_file(config_path, config_yaml(temp / "result.json", "tensorrt_int8", manifest)) ||
        !runtime::RuntimeConfigLoader::load(config_path, &config).ok() ||
        config.schema_version != 5U || config.backend_type != "tensorrt_int8") {
        std::cerr << "RuntimeConfig v5 parse failed\n";
        return 1;
    }

    model::ModelContract contract;
    if (!model::ModelContractLoader::load(contract_path, &contract).ok()) return 1;
    model::TensorRtEngineManifest v2;
    auto status = model::TensorRtEngineManifestLoader::load(manifest, &contract, &v2);
    if (!status.ok() || v2.schema_version != 2U || v2.backend_type != "tensorrt_int8" ||
        !v2.int8_enabled || v2.confirmed_int8_compute == 0U ||
        v2.host_io_dtype != "FP32" || v2.cache_metadata_sha256.size() != 64U) {
        std::cerr << "Manifest v2 validation failed: " << status.message() << '\n';
        return 1;
    }
    model::TensorRtEngineManifest v1;
    status = model::TensorRtEngineManifestLoader::load(
        "models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json",
        &contract, &v1);
    if (!status.ok() || v1.schema_version != 1U || v1.int8_enabled ||
        v1.backend_type != "") {
        std::cerr << "Manifest v1 compatibility failed: " << status.message() << '\n';
        return 1;
    }

    runtime::RunMetadata metadata;
    metadata.schema_version = 4;
    metadata.backend_type = "tensorrt_int8";
    metadata.model_filename = "yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine";
    metadata.model_sha256 = v2.engine_sha256;
    metadata.contract_filename = "yolov8n_neudet_frozen.yaml";
    metadata.artifact_kind = "tensorrt_engine";
    metadata.source_onnx_sha256 = v2.source_onnx_sha256;
    metadata.engine_manifest_filename = "engine_manifest_v2.json";
    metadata.class_names = contract.class_names;
    metadata.postprocess_config.confidence_threshold = 0.25F;
    metadata.postprocess_config.iou_threshold = 0.45F;
    metadata.postprocess_config.max_nms = 30000;
    metadata.postprocess_config.max_det = 300;
    metadata.postprocess_config.max_wh = 7680.0F;
    metadata.precision_v4 = runtime::PrecisionMetadataV4{
        v2.precision_mode, true, true, "FP32",
        runtime::CalibrationMetadataV4{
            "IInt8EntropyCalibrator2", "train", 1260U,
            v2.calibration_manifest_sha256, v2.calibration_cache_sha256,
            v2.cache_metadata_sha256}};
    metadata.runtime_v3 = runtime::RuntimeMetadataV3{"serial", "directory", std::nullopt};

    std::unique_ptr<runtime::JsonSink> sink;
    status = runtime::JsonSink::create(temp / "result.json", true, &sink);
    if (!status.ok() || !sink->begin_run(metadata).ok()) return 1;
    runtime::FrameResult frame;
    frame.relative_path = "sample.jpg";
    frame.image_width = 640;
    frame.image_height = 640;
    if (!sink->write_frame(frame).ok()) return 1;
    runtime::RunSummary summary;
    summary.processed_images = 1;
    summary.runtime_v3 = runtime::RunSummaryV3{};
    summary.runtime_v3->source_frames = 1;
    summary.runtime_v3->run_processing_wall_ms = 1.0;
    status = sink->end_run(summary);
    if (!status.ok()) return 1;
    std::ifstream input(temp / "result.json");
    const std::string result((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
    if (result.find("\"schema_version\": 4") == std::string::npos ||
        result.find("\"engine_compute_mode\"") == std::string::npos ||
        result.find("\"calibration\"") == std::string::npos ||
        result.find("\"cache_metadata_sha256\"") == std::string::npos) return 1;
    std::cout << "Q4_RUNTIME_INTEGRATION_FOCUSED_PASS\n";
    return 0;
}
