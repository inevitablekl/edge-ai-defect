#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "backend_tensorrt/pageable_raw_staging.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <NvInfer.h>
#include <cuda_runtime_api.h>
#include <openssl/evp.h>
#include <opencv2/imgcodecs.hpp>
#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
namespace e = edge_ai_defect;

constexpr double kMaeLimit = 5.0e-4;
constexpr double kP99Limit = 2.0 / 255.0 + 1.0e-6;
constexpr double kMaxLimit = 4.0 / 255.0 + 1.0e-6;
constexpr std::size_t kTensorElements = 3U * 640U * 640U;

struct Options { fs::path config, manifest, image_root, report; };
struct CaseInput {
    std::string id;
    fs::path path;
    std::string source_sha256;
    bool raw_bgr = false;
    int width = 0;
    int height = 0;
    std::size_t row_stride = 0U;
};
struct Metrics {
    double sum = 0.0;
    double max_abs = 0.0;
    std::size_t nonfinite = 0U;
    std::vector<double> errors;
};
struct CaseResult {
    std::string id;
    bool geometry = false;
    double mae = 0.0;
    double max_abs = 0.0;
    std::size_t nonfinite = 0U;
};

class GateError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

Options parse_options(int argc, char** argv) {
    if (argc != 9) {
        throw GateError("usage: stage_r_v2_tensor_gate --config PATH --manifest PATH "
                        "--image-root PATH --report PATH");
    }
    Options options;
    for (int i = 1; i < argc; i += 2) {
        const std::string key = argv[i];
        const fs::path value = argv[i + 1];
        if (key == "--config") options.config = value;
        else if (key == "--manifest") options.manifest = value;
        else if (key == "--image-root") options.image_root = value;
        else if (key == "--report") options.report = value;
        else throw GateError("unknown option: " + key);
    }
    if (options.config.empty() || options.manifest.empty() ||
        options.image_root.empty() || options.report.empty()) {
        throw GateError("all options are required");
    }
    return options;
}

std::string sha256_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw GateError("cannot open file for SHA-256: " + path.string());
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        throw GateError("SHA-256 initialization failed");
    }
    char buffer[64 * 1024];
    while (input.good()) {
        input.read(buffer, sizeof(buffer));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context, buffer, static_cast<std::size_t>(count)) != 1) {
            EVP_MD_CTX_free(context);
            throw GateError("SHA-256 update failed");
        }
    }
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0U;
    if (!input.eof() || EVP_DigestFinal_ex(context, digest, &length) != 1) {
        EVP_MD_CTX_free(context);
        throw GateError("SHA-256 finalization failed");
    }
    EVP_MD_CTX_free(context);
    std::ostringstream result;
    result << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < length; ++i) result << std::setw(2) << static_cast<unsigned>(digest[i]);
    return result.str();
}

std::string current_commit() {
    FILE* pipe = popen("git rev-parse HEAD 2>/dev/null", "r");
    if (pipe == nullptr) return "unavailable";
    char buffer[128] = {};
    const std::size_t count = std::fread(buffer, 1, sizeof(buffer) - 1U, pipe);
    pclose(pipe);
    std::string result(buffer, count);
    while (!result.empty() && (result.back() == '\n' || result.back() == '\r')) result.pop_back();
    return result.empty() ? "unavailable" : result;
}

int required_int(const YAML::Node& node, const char* key) {
    if (!node[key] || !node[key].IsScalar()) throw GateError(std::string("missing manifest field: ") + key);
    const int value = node[key].as<int>();
    if (value <= 0) throw GateError(std::string("invalid manifest field: ") + key);
    return value;
}

std::vector<CaseInput> load_cases(const fs::path& path) {
    const YAML::Node root = YAML::LoadFile(path.string());
    if (!root["cases"] || !root["cases"].IsSequence() || root["cases"].size() != 16U ||
        root["entry_count"].as<int>() != 16) {
        throw GateError("V2 tensor gate requires the frozen 16-case corpus");
    }
    const YAML::Node shape = root["target_shape"];
    if (!shape || shape.size() != 4U || shape[0].as<int>() != 1 ||
        shape[1].as<int>() != 3 || shape[2].as<int>() != 640 || shape[3].as<int>() != 640) {
        throw GateError("V2 tensor gate requires target shape [1,3,640,640]");
    }
    std::vector<CaseInput> cases;
    for (const auto& node : root["cases"]) {
        CaseInput item;
        item.id = node["id"].as<std::string>();
        item.path = node["path"].as<std::string>();
        item.source_sha256 = node["source_sha256"].as<std::string>();
        item.raw_bgr = node["format"].as<std::string>() == "raw_bgr";
        if (item.raw_bgr) {
            item.width = required_int(node, "width");
            item.height = required_int(node, "height");
            item.row_stride = static_cast<std::size_t>(required_int(node, "row_stride"));
            if (item.row_stride < static_cast<std::size_t>(item.width) * 3U) {
                throw GateError("raw BGR row stride is smaller than packed row bytes");
            }
        }
        cases.push_back(std::move(item));
    }
    return cases;
}

std::vector<std::uint8_t> read_bytes(const fs::path& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw GateError("cannot read raw BGR file: " + path.string());
    const std::streampos end = input.tellg();
    if (end < 0) throw GateError("cannot determine raw BGR file size");
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(end));
    input.seekg(0, std::ios::beg);
    if (!bytes.empty() && !input.read(reinterpret_cast<char*>(bytes.data()),
                                      static_cast<std::streamsize>(bytes.size()))) {
        throw GateError("cannot read complete raw BGR file");
    }
    return bytes;
}

double p99(std::vector<double> values) {
    if (values.empty()) return std::numeric_limits<double>::infinity();
    std::sort(values.begin(), values.end());
    const double rank = 0.99 * static_cast<double>(values.size() - 1U);
    const std::size_t low = static_cast<std::size_t>(std::floor(rank));
    const std::size_t high = static_cast<std::size_t>(std::ceil(rank));
    return values[low] + (rank - static_cast<double>(low)) * (values[high] - values[low]);
}

void write_report(const Options& options,
                  const e::runtime::RuntimeConfig& config,
                  const std::vector<CaseResult>& cases,
                  const Metrics& metrics,
                  double p99_value,
                  bool pass) {
    if (!options.report.parent_path().empty()) fs::create_directories(options.report.parent_path());
    std::ofstream output(options.report);
    if (!output) throw GateError("cannot write report: " + options.report.string());
    const double mae = metrics.errors.empty() ? std::numeric_limits<double>::infinity() :
        metrics.sum / static_cast<double>(metrics.errors.size());
    output << std::setprecision(17)
           << "{\n  \"schema_version\": 1,\n"
           << "  \"validation\": \"stage_r_r2_v2_tensor_gate\",\n"
           << "  \"status\": \"" << (pass ? "PASS" : "FAIL") << "\",\n"
           << "  \"commit\": \"" << current_commit() << "\",\n"
           << "  \"binary_sha256\": \"" << sha256_file("/proc/self/exe") << "\",\n"
           << "  \"engine_sha256\": \"" << sha256_file(config.tensorrt.engine_path) << "\",\n"
           << "  \"config_sha256\": \"" << sha256_file(options.config) << "\",\n"
           << "  \"test_manifest_sha256\": \"" << sha256_file(options.manifest) << "\",\n"
           << "  \"validator_mode\": \"V2 pageable raw staging to actual TensorRT input_device copy-back; no enqueue\",\n"
           << "  \"tensor_source\": \"TensorRtEngine::device_input_buffer() passed to CudaPreprocessor::create_for_external_tensor()\",\n"
           << "  \"tensor_shape\": [1, 3, 640, 640],\n"
           << "  \"image_count\": " << cases.size() << ",\n"
           << "  \"mae\": " << mae << ",\n"
           << "  \"p99\": " << p99_value << ",\n"
           << "  \"max_abs\": " << metrics.max_abs << ",\n"
           << "  \"nonfinite\": " << metrics.nonfinite << ",\n"
           << "  \"thresholds\": {\"mae\": " << kMaeLimit
           << ", \"p99\": " << kP99Limit << ", \"max_abs\": " << kMaxLimit << "},\n"
           << "  \"cases\": [\n";
    for (std::size_t i = 0; i < cases.size(); ++i) {
        const auto& item = cases[i];
        output << "    {\"id\": \"" << item.id << "\", \"geometry\": \""
               << (item.geometry ? "PASS" : "FAIL") << "\", \"mae\": " << item.mae
               << ", \"max_abs\": " << item.max_abs << ", \"nonfinite\": " << item.nonfinite << "}"
               << (i + 1U == cases.size() ? "\n" : ",\n");
    }
    output << "  ]\n}\n";
}

int run(const Options& options) {
    e::runtime::RuntimeConfig config;
    auto status = e::runtime::RuntimeConfigLoader::load(options.config, &config);
    if (!status.ok()) throw GateError("config: " + status.message());
    if (config.data_path_variant != e::runtime::DataPathVariant::kV2 ||
        config.backend_type != "tensorrt_int8") {
        throw GateError("validator requires RuntimeConfig V2 and tensorrt_int8");
    }
    e::model::ModelContract contract;
    status = e::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) throw GateError("contract: " + status.message());
    std::unique_ptr<e::inference::IInferenceEngine> generic_engine;
    status = e::inference::create_inference_engine(config, contract, &generic_engine);
    if (!status.ok()) throw GateError("engine: " + status.message());
    auto* engine = dynamic_cast<e::backend_tensorrt::TensorRtEngine*>(generic_engine.get());
    if (engine == nullptr) throw GateError("V2 TensorRT capability is unavailable");

    const auto cases = load_cases(options.manifest);
    int max_width = 0;
    int max_height = 0;
    std::size_t max_stride = 0U;
    for (const auto& item : cases) {
        const fs::path path = options.image_root / item.path;
        if (!fs::is_regular_file(path) || fs::is_symlink(path) || sha256_file(path) != item.source_sha256) {
            throw GateError("corpus identity mismatch: " + path.string());
        }
        if (item.raw_bgr) {
            max_width = std::max(max_width, item.width);
            max_height = std::max(max_height, item.height);
            max_stride = std::max(max_stride, item.row_stride);
        }
    }
    std::vector<cv::Mat> images;
    std::vector<std::vector<std::uint8_t>> raw;
    images.reserve(cases.size());
    raw.resize(cases.size());
    for (std::size_t i = 0; i < cases.size(); ++i) {
        const fs::path path = options.image_root / cases[i].path;
        if (cases[i].raw_bgr) {
            raw[i] = read_bytes(path);
            const std::size_t expected = cases[i].row_stride * static_cast<std::size_t>(cases[i].height);
            if (raw[i].size() != expected) throw GateError("raw BGR size mismatch: " + cases[i].id);
            images.emplace_back(cases[i].height, cases[i].width, CV_8UC3,
                                raw[i].data(), cases[i].row_stride);
        } else {
            images.push_back(cv::imread(path.string(), cv::IMREAD_COLOR));
            if (images.back().empty() || images.back().type() != CV_8UC3) {
                throw GateError("decode failed: " + path.string());
            }
        }
        max_width = std::max(max_width, images.back().cols);
        max_height = std::max(max_height, images.back().rows);
        max_stride = std::max(max_stride, static_cast<std::size_t>(images.back().step));
    }

    std::unique_ptr<e::stage_r::CudaPreprocessor> preprocessor;
    status = e::stage_r::CudaPreprocessor::create_for_external_tensor(
        max_width, max_height, max_stride,
        reinterpret_cast<cudaStream_t>(engine->cuda_stream_handle()),
        static_cast<float*>(engine->device_input_buffer()), &preprocessor);
    if (!status.ok()) throw GateError("V2 external preprocessor: " + status.message());
    e::stage_r::PageableRawStaging staging;
    e::preprocess::Preprocessor cpu_preprocessor;
    const auto& input_info = contract.input.tensor_info;
    std::vector<float> copy_back(kTensorElements);
    Metrics metrics;
    metrics.errors.reserve(cases.size() * kTensorElements);
    std::vector<CaseResult> results;
    results.reserve(cases.size());
    bool pass = true;
    for (std::size_t i = 0; i < cases.size(); ++i) {
        e::preprocess::PreprocessedFrame cpu;
        status = cpu_preprocessor.preprocess(images[i], input_info, &cpu);
        if (!status.ok()) throw GateError("CPU preprocessing: " + status.message());
        e::preprocess::ImageTransformMetadata geometry;
        status = e::stage_r::CudaPreprocessor::compute_geometry(images[i].cols, images[i].rows, &geometry);
        if (!status.ok()) throw GateError("geometry: " + status.message());
        const auto& expected = cpu.transform;
        const bool geometry_pass = geometry.original_width == expected.original_width &&
            geometry.original_height == expected.original_height &&
            geometry.resized_width == expected.resized_width &&
            geometry.resized_height == expected.resized_height &&
            geometry.pad_left == expected.pad_left && geometry.pad_right == expected.pad_right &&
            geometry.pad_top == expected.pad_top && geometry.pad_bottom == expected.pad_bottom;
        status = staging.prepare(images[i]);
        if (!status.ok()) throw GateError("pageable staging: " + status.message());
        status = preprocessor->preprocess(staging.data(), staging.width(), staging.height(),
                                          staging.packed_row_bytes(), geometry);
        if (!status.ok()) throw GateError("V2 preprocessing: " + status.message());
        // This is the actual TensorRT input allocation obtained through the
        // backend-only capability, not a second CUDA preprocessing output.
        status = preprocessor->copy_output_to_host(copy_back.data(), copy_back.size());
        if (!status.ok()) throw GateError("TensorRT input copy-back: " + status.message());

        CaseResult result{cases[i].id, geometry_pass, 0.0, 0.0, 0U};
        double case_sum = 0.0;
        for (std::size_t index = 0; index < kTensorElements; ++index) {
            const float actual = copy_back[index];
            const float reference = cpu.tensor.data[index];
            if (!std::isfinite(actual) || !std::isfinite(reference)) {
                ++result.nonfinite;
                ++metrics.nonfinite;
                continue;
            }
            const double error = std::abs(static_cast<double>(actual) - static_cast<double>(reference));
            case_sum += error;
            metrics.sum += error;
            metrics.max_abs = std::max(metrics.max_abs, error);
            metrics.errors.push_back(error);
            result.max_abs = std::max(result.max_abs, error);
        }
        result.mae = case_sum / static_cast<double>(kTensorElements);
        pass = pass && result.geometry && result.nonfinite == 0U &&
               result.mae <= kMaeLimit && result.max_abs <= kMaxLimit;
        results.push_back(result);
        std::cout << result.id << ": mae=" << result.mae << " max=" << result.max_abs
                  << " nonfinite=" << result.nonfinite
                  << " geometry=" << (result.geometry ? "PASS" : "FAIL") << '\n';
    }
    const double p99_value = p99(metrics.errors);
    const double mae = metrics.sum / static_cast<double>(metrics.errors.size());
    pass = pass && metrics.nonfinite == 0U && mae <= kMaeLimit &&
           p99_value <= kP99Limit && metrics.max_abs <= kMaxLimit;
    write_report(options, config, results, metrics, p99_value, pass);
    std::cout << "V2 tensor gate: " << (pass ? "PASS" : "FAIL")
              << " mae=" << mae << " p99=" << p99_value
              << " max=" << metrics.max_abs << " nonfinite=" << metrics.nonfinite << '\n';
    return pass ? 0 : 1;
}
}  // namespace

int main(int argc, char** argv) {
    try { return run(parse_options(argc, argv)); }
    catch (const std::exception& error) {
        std::cerr << "stage_r_v2_tensor_gate: " << error.what() << '\n';
        return 2;
    }
}
