#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "backend_tensorrt/pageable_raw_staging.hpp"
#include "backend_tensorrt/pinned_raw_staging.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_detection_hash.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <cuda_runtime_api.h>
#include <openssl/sha.h>
#include <opencv2/imgcodecs.hpp>
#include <yaml-cpp/yaml.h>

#include <cmath>
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <iterator>
#include <vector>

namespace {
namespace fs = std::filesystem;
namespace e = edge_ai_defect;

struct CaseInput {
    std::string id;
    fs::path path;
    std::string sha;
    bool raw_bgr = false;
    int width = 0;
    int height = 0;
    std::size_t row_stride = 0U;
};
struct VariantResult {
    std::string variant;
    std::size_t frames = 0;
    std::size_t total_detections = 0;
    std::size_t nonfinite_outputs = 0;
    bool geometry_pass = true;
    bool shape_pass = true;
    bool cuda_pass = true;
    std::string tensor_digest;
    std::string detection_digest;
};

class ValidationError final : public std::runtime_error {
public: using std::runtime_error::runtime_error;
};

std::string sha256_bytes(const std::vector<std::uint8_t>& bytes) {
    unsigned char digest[SHA256_DIGEST_LENGTH] = {};
    SHA256(bytes.data(), bytes.size(), digest);
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (unsigned char value : digest) out << std::setw(2) << static_cast<unsigned>(value);
    return out.str();
}

std::string sha256_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw ValidationError("cannot read " + path.string());
    std::vector<std::uint8_t> bytes((std::istreambuf_iterator<char>(input)), {});
    return sha256_bytes(bytes);
}

std::vector<CaseInput> load_cases(const fs::path& manifest) {
    const YAML::Node root = YAML::LoadFile(manifest.string());
    if (root["schema_version"].as<int>() != 1 || root["entry_count"].as<int>() != 16 ||
        !root["cases"].IsSequence() || root["cases"].size() != 16U)
        throw ValidationError("integration pretest requires the frozen 16-case corpus");
    std::vector<CaseInput> cases;
    for (const auto& node : root["cases"]) {
        const bool raw_bgr = node["format"].as<std::string>() == "raw_bgr";
        cases.push_back({node["id"].as<std::string>(), node["path"].as<std::string>(),
                         node["source_sha256"].as<std::string>(), raw_bgr,
                         raw_bgr ? node["width"].as<int>() : 0,
                         raw_bgr ? node["height"].as<int>() : 0,
                         raw_bgr ? node["row_stride"].as<std::size_t>() : 0U});
    }
    return cases;
}

VariantResult run_variant(const fs::path& config_path, const fs::path& manifest,
                          const fs::path& image_root, bool pinned) {
    e::runtime::RuntimeConfig config;
    auto status = e::runtime::RuntimeConfigLoader::load(config_path, &config);
    if (!status.ok()) throw ValidationError(status.message());
    const bool expected_v2r = config.data_path_variant == e::runtime::DataPathVariant::kV2R;
    const bool expected_v3r = config.data_path_variant == e::runtime::DataPathVariant::kV3R;
    if ((!pinned && !expected_v2r) || (pinned && !expected_v3r) ||
        config.backend_type != "tensorrt_int8")
        throw ValidationError("integration config has the wrong V2R/V3R identity");

    e::model::ModelContract contract;
    status = e::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) throw ValidationError(status.message());
    std::unique_ptr<e::inference::IInferenceEngine> generic_engine;
    status = e::inference::create_inference_engine(config, contract, &generic_engine);
    if (!status.ok()) throw ValidationError(status.message());
    auto* engine = dynamic_cast<e::backend_tensorrt::TensorRtEngine*>(generic_engine.get());
    if (engine == nullptr) throw ValidationError("TensorRT capability unavailable");

    const auto cases = load_cases(manifest);
    std::vector<cv::Mat> images;
    images.reserve(cases.size());
    std::vector<std::vector<std::uint8_t>> raw(cases.size());
    int max_width = 0;
    int max_height = 0;
    for (const auto& item : cases) {
        const fs::path path = image_root / item.path;
        if (!fs::is_regular_file(path) || fs::is_symlink(path) || sha256_file(path) != item.sha)
            throw ValidationError("corpus identity mismatch: " + path.string());
        cv::Mat image;
        if (cases[images.size()].raw_bgr) {
            const std::size_t expected = cases[images.size()].row_stride *
                                         static_cast<std::size_t>(cases[images.size()].height);
            std::ifstream input(path, std::ios::binary);
            raw[images.size()] = std::vector<std::uint8_t>(
                (std::istreambuf_iterator<char>(input)), {});
            if (raw[images.size()].size() != expected) throw ValidationError("raw BGR size mismatch");
            image = cv::Mat(cases[images.size()].height, cases[images.size()].width,
                            CV_8UC3, raw[images.size()].data(), cases[images.size()].row_stride);
        } else {
            image = cv::imread(path.string(), cv::IMREAD_COLOR);
        }
        if (image.empty() || image.type() != CV_8UC3) throw ValidationError("decode failed");
        max_width = std::max(max_width, image.cols);
        max_height = std::max(max_height, image.rows);
        images.push_back(std::move(image));
    }

    std::unique_ptr<e::stage_r::CudaPreprocessor> preprocessor;
    status = e::stage_r::CudaPreprocessor::create_for_external_tensor(
        max_width, max_height, static_cast<std::size_t>(max_width) * 3U,
        reinterpret_cast<cudaStream_t>(engine->cuda_stream_handle()),
        static_cast<float*>(engine->device_input_buffer()), &preprocessor,
        e::stage_r::ResizeSemantic::kOpenCv454AlignedFixedContract);
    if (!status.ok()) throw ValidationError(status.message());

    e::stage_r::PageableRawStaging pageable;
    e::stage_r::PinnedRawStaging pinned_staging;
    if (pinned) {
        status = pinned_staging.allocate(static_cast<std::size_t>(max_width) *
                                         static_cast<std::size_t>(max_height) * 3U);
        if (!status.ok()) throw ValidationError(status.message());
    }
    e::postprocess::PostProcessor postprocessor(config.postprocess_config);
    std::vector<e::runtime::FrameResult> frames;
    frames.reserve(images.size());
    std::vector<std::uint8_t> tensor_bytes;
    VariantResult result;
    result.variant = pinned ? "V3R" : "V2R";
    for (std::size_t index = 0; index < images.size(); ++index) {
        const cv::Mat& image = images[index];
        const std::uint8_t* data = nullptr;
        std::size_t stride = 0U;
        int width = 0;
        int height = 0;
        if (pinned) {
            status = pinned_staging.prepare(image);
            data = pinned_staging.data(); width = pinned_staging.width();
            height = pinned_staging.height(); stride = pinned_staging.packed_row_bytes();
        } else {
            status = pageable.prepare(image);
            data = pageable.data(); width = pageable.width();
            height = pageable.height(); stride = pageable.packed_row_bytes();
        }
        if (!status.ok()) throw ValidationError(status.message());
        e::preprocess::ImageTransformMetadata geometry;
        status = e::stage_r::CudaPreprocessor::compute_geometry(width, height, &geometry);
        if (!status.ok()) throw ValidationError(status.message());
        status = preprocessor->preprocess(data, width, height, stride, geometry);
        if (!status.ok()) throw ValidationError(status.message());
        std::vector<float> tensor(e::stage_r::CudaPreprocessor::kTargetElementCount);
        status = preprocessor->copy_output_to_host(tensor.data(), tensor.size());
        if (!status.ok()) throw ValidationError(status.message());
        for (float value : tensor) if (!std::isfinite(value)) ++result.nonfinite_outputs;
        tensor_bytes.insert(tensor_bytes.end(),
                            reinterpret_cast<const std::uint8_t*>(tensor.data()),
                            reinterpret_cast<const std::uint8_t*>(tensor.data()) +
                                tensor.size() * sizeof(float));
        e::core::HostTensor output;
        status = engine->run_device_input(engine->device_input_buffer(),
                                          engine->device_input_bytes(), &output);
        if (!status.ok()) throw ValidationError(status.message());
        for (float value : output.data) if (!std::isfinite(value)) ++result.nonfinite_outputs;
        result.shape_pass = result.shape_pass && output.info.shape.size() == 3U &&
            output.info.shape[0] == 1 && output.info.shape[1] == 10 && output.info.shape[2] == 8400;
        std::vector<e::postprocess::Detection> detections;
        status = postprocessor.process(output, geometry, &detections);
        if (!status.ok()) throw ValidationError(status.message());
        result.total_detections += detections.size();
        frames.push_back({index, cases[index].path, image.cols, image.rows, std::move(detections), std::nullopt});
        ++result.frames;
    }
    result.tensor_digest = sha256_bytes(tensor_bytes);
    status = e::runtime::canonical_detection_sha256(e::runtime::CanonicalScope::kRun,
                                                     frames, &result.detection_digest);
    if (!status.ok()) throw ValidationError(status.message());
    result.geometry_pass = true;
    result.cuda_pass = result.nonfinite_outputs == 0U;
    return result;
}

void write_report(const fs::path& path, const VariantResult& v2r, const VariantResult& v3r,
                  const std::string& engine_sha, const std::string& manifest_sha) {
    std::ofstream out(path);
    if (!out) throw ValidationError("cannot write integration report");
    const bool identity = v2r.tensor_digest == v3r.tensor_digest &&
                          v2r.detection_digest == v3r.detection_digest;
    out << "{\n  \"schema_version\": 1,\n"
        << "  \"validation\": \"paper_phase0_5c_i1_gate_c2_integration_pretest\",\n"
        << "  \"remediation_id\": \"opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1\",\n"
        << "  \"engine_sha256\": \"" << engine_sha << "\",\n"
        << "  \"test_manifest_sha256\": \"" << manifest_sha << "\",\n"
        << "  \"formal_gate_d\": \"NOT RUN\",\n  \"task_metrics\": \"NOT GENERATED\",\n"
        << "  \"v2r_v3r_identity_pass\": " << (identity ? "true" : "false") << ",\n"
        << "  \"variants\": {\n";
    for (const auto* value : {&v2r, &v3r}) {
        out << "    \"" << value->variant << "\": {\"frames\": " << value->frames
            << ", \"total_detections\": " << value->total_detections
            << ", \"nonfinite_outputs\": " << value->nonfinite_outputs
            << ", \"shape_pass\": " << (value->shape_pass ? "true" : "false")
            << ", \"cuda_pass\": " << (value->cuda_pass ? "true" : "false")
            << ", \"tensor_digest_sha256\": \"" << value->tensor_digest
            << "\", \"detection_sha256\": \"" << value->detection_digest << "\"}"
            << (value == &v3r ? "\n" : ",\n");
    }
    out << "  },\n  \"status\": \""
        << (identity && v2r.cuda_pass && v3r.cuda_pass && v2r.shape_pass && v3r.shape_pass
                ? "PASS" : "FAIL") << "\"\n}\n";
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 11) {
        std::cerr << "usage: stage_r_v2r_integration_pretest --v2r-config PATH --v3r-config PATH "
                     "--manifest PATH --image-root PATH --report PATH\n";
        return 2;
    }
    try {
        fs::path v2r, v3r, manifest, image_root, report;
        for (int i = 1; i < argc; i += 2) {
            const std::string key = argv[i];
            const fs::path value = argv[i + 1];
            if (key == "--v2r-config") v2r = value;
            else if (key == "--v3r-config") v3r = value;
            else if (key == "--manifest") manifest = value;
            else if (key == "--image-root") image_root = value;
            else if (key == "--report") report = value;
            else throw ValidationError("unknown option: " + key);
        }
        const VariantResult v2r_result = run_variant(v2r, manifest, image_root, false);
        const VariantResult v3r_result = run_variant(v3r, manifest, image_root, true);
        if (!report.parent_path().empty()) fs::create_directories(report.parent_path());
        write_report(report, v2r_result, v3r_result,
                     sha256_file(YAML::LoadFile(v2r.string())["tensorrt"]["engine_path"].as<std::string>()),
                     sha256_file(manifest));
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "stage_r_v2r_integration_pretest: " << error.what() << '\n';
        return 1;
    }
}
