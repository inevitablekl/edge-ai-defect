#include "backend_tensorrt/cuda_preprocessor.hpp"

#include "edge_ai_defect/preprocess/preprocessor.hpp"

#include <cuda_runtime_api.h>
#include <opencv2/imgcodecs.hpp>
#include <yaml-cpp/yaml.h>
#include <openssl/evp.h>

#include <algorithm>
#include <cmath>
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
namespace stage_r = edge_ai_defect::stage_r;
namespace preprocess = edge_ai_defect::preprocess;

constexpr double kMaeLimit = 5.0e-4;
constexpr double kP99Limit = 2.0 / 255.0 + 1.0e-6;
constexpr double kMaxLimit = 4.0 / 255.0 + 1.0e-6;

struct Options {
    fs::path manifest;
    fs::path image_root;
    fs::path report;
};

struct CaseInput {
    std::string id;
    fs::path path;
    bool raw_bgr = false;
    int width = 0;
    int height = 0;
    std::size_t row_stride = 0U;
    std::string source_sha256;
};

struct CaseResult {
    std::string id;
    double mae = 0.0;
    double max_abs = 0.0;
    std::size_t nonfinite = 0U;
    bool geometry_pass = false;
};

struct Aggregate {
    std::vector<double> errors;
    double sum = 0.0;
    double max_abs = 0.0;
    std::size_t nonfinite = 0U;
};

class GateError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

Options parse_options(int argc, char** argv) {
    if (argc != 7) {
        throw GateError(
            "usage: stage_r_cuda_preprocess_gate --manifest PATH "
            "--image-root PATH --report PATH");
    }
    Options options;
    for (int i = 1; i < argc; i += 2) {
        const std::string option = argv[i];
        const fs::path value = argv[i + 1];
        if (option == "--manifest") options.manifest = value;
        else if (option == "--image-root") options.image_root = value;
        else if (option == "--report") options.report = value;
        else throw GateError("unknown option: " + option);
    }
    if (options.manifest.empty() || options.image_root.empty() || options.report.empty()) {
        throw GateError("manifest, image-root, and report are required");
    }
    return options;
}

std::string sha256_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw GateError("cannot read corpus file: " + path.string());
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        throw GateError("SHA-256 initialization failed");
    }
    char buffer[64 * 1024];
    while (input.good()) {
        input.read(buffer, sizeof(buffer));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context, buffer,
                                           static_cast<std::size_t>(count)) != 1) {
            EVP_MD_CTX_free(context);
            throw GateError("SHA-256 update failed");
        }
    }
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0U;
    const bool ok = input.eof() && EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) throw GateError("SHA-256 read/finalize failed: " + path.string());
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < length; ++i) {
        output << std::setw(2) << static_cast<unsigned int>(digest[i]);
    }
    return output.str();
}

int required_int(const YAML::Node& node, const char* key, int minimum) {
    if (!node[key] || !node[key].IsScalar()) {
        throw GateError(std::string("manifest field is missing: ") + key);
    }
    const int value = node[key].as<int>();
    if (value < minimum) throw GateError(std::string("manifest field is invalid: ") + key);
    return value;
}

std::vector<CaseInput> load_manifest(const fs::path& path) {
    const YAML::Node root = YAML::LoadFile(path.string());
    if (root["schema_version"].as<int>() != 1 ||
        root["entry_count"].as<int>() != 16 || !root["cases"].IsSequence() ||
        root["cases"].size() != 16U) {
        throw GateError("Stage R CUDA corpus must contain exactly 16 cases");
    }
    const auto shape = root["target_shape"];
    if (!shape.IsSequence() || shape.size() != 4U || shape[0].as<int>() != 1 ||
        shape[1].as<int>() != 3 || shape[2].as<int>() != 640 || shape[3].as<int>() != 640) {
        throw GateError("Stage R CUDA corpus target shape must be [1,3,640,640]");
    }
    std::vector<CaseInput> cases;
    cases.reserve(16U);
    for (const auto& node : root["cases"]) {
        CaseInput item;
        item.id = node["id"].as<std::string>();
        item.path = node["path"].as<std::string>();
        item.raw_bgr = node["format"].as<std::string>() == "raw_bgr";
        if (!item.raw_bgr && node["format"].as<std::string>() != "image") {
            throw GateError("unsupported corpus format for " + item.id);
        }
        item.source_sha256 = node["source_sha256"].as<std::string>();
        if (item.raw_bgr) {
            item.width = required_int(node, "width", 1);
            item.height = required_int(node, "height", 1);
            item.row_stride = static_cast<std::size_t>(
                required_int(node, "row_stride", item.width * 3));
        }
        cases.push_back(std::move(item));
    }
    return cases;
}

std::vector<std::uint8_t> read_raw(const fs::path& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw GateError("cannot read raw BGR file: " + path.string());
    const std::streampos end = input.tellg();
    if (end < 0) throw GateError("cannot determine raw BGR file size: " + path.string());
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(end));
    input.seekg(0, std::ios::beg);
    if (!bytes.empty()) {
        input.read(reinterpret_cast<char*>(bytes.data()),
                   static_cast<std::streamsize>(bytes.size()));
        if (!input) throw GateError("cannot read complete raw BGR file: " + path.string());
    }
    return bytes;
}

double type7_p99(std::vector<double> values) {
    if (values.empty()) return std::numeric_limits<double>::infinity();
    std::sort(values.begin(), values.end());
    const double rank = 0.99 * static_cast<double>(values.size() - 1U);
    const std::size_t lower = static_cast<std::size_t>(std::floor(rank));
    const std::size_t upper = static_cast<std::size_t>(std::ceil(rank));
    return values[lower] + (rank - static_cast<double>(lower)) *
                               (values[upper] - values[lower]);
}

void write_report(const fs::path& path,
                  const std::string& corpus_id,
                  const std::vector<CaseResult>& results,
                  const Aggregate& aggregate,
                  double p99,
                  bool pass) {
    if (!path.parent_path().empty()) fs::create_directories(path.parent_path());
    std::ofstream output(path);
    if (!output) throw GateError("cannot open gate report: " + path.string());
    output << std::setprecision(17)
           << "{\n  \"schema_version\": 1,\n"
           << "  \"validation\": \"stage_r_cuda_preprocess_tensor_gate\",\n"
           << "  \"corpus_id\": \"" << corpus_id << "\",\n"
           << "  \"image_count\": " << results.size() << ",\n"
           << "  \"measured_fps\": null,\n  \"measured_latency_ms\": null,\n"
           << "  \"gate\": {\n"
           << "    \"mae\": " << aggregate.sum /
               static_cast<double>(aggregate.errors.size()) << ",\n"
           << "    \"mae_limit\": " << kMaeLimit << ",\n"
           << "    \"p99\": " << p99 << ",\n"
           << "    \"p99_limit\": " << kP99Limit << ",\n"
           << "    \"max_abs\": " << aggregate.max_abs << ",\n"
           << "    \"max_abs_limit\": " << kMaxLimit << ",\n"
           << "    \"nonfinite\": " << aggregate.nonfinite << ",\n"
           << "    \"status\": \"" << (pass ? "PASS" : "FAIL") << "\"\n"
           << "  },\n  \"cases\": [\n";
    for (std::size_t i = 0; i < results.size(); ++i) {
        const auto& result = results[i];
        output << "    {\"id\": \"" << result.id << "\", \"mae\": "
               << result.mae << ", \"max_abs\": " << result.max_abs
               << ", \"nonfinite\": " << result.nonfinite
               << ", \"geometry\": \""
               << (result.geometry_pass ? "PASS" : "FAIL") << "\"}"
               << (i + 1U == results.size() ? "\n" : ",\n");
    }
    output << "  ]\n}\n";
}

int run(const Options& options) {
    int device_count = 0;
    const cudaError_t device_error = cudaGetDeviceCount(&device_count);
    if (device_error != cudaSuccess || device_count == 0) {
        std::cerr << "CUDA tensor gate unavailable: "
                  << cudaGetErrorString(device_error) << '\n';
        return 77;
    }

    const YAML::Node manifest_root = YAML::LoadFile(options.manifest.string());
    const std::string corpus_id = manifest_root["corpus_id"].as<std::string>();
    const std::vector<CaseInput> cases = load_manifest(options.manifest);
    std::vector<fs::path> paths;
    paths.reserve(cases.size());
    int max_width = 0;
    int max_height = 0;
    std::size_t max_stride = 0U;
    for (const CaseInput& item : cases) {
        const fs::path path = options.image_root / item.path;
        if (!fs::is_regular_file(path) || fs::is_symlink(path)) {
            throw GateError("corpus source is not a regular file: " + path.string());
        }
        if (sha256_file(path) != item.source_sha256) {
            throw GateError("corpus source SHA-256 mismatch: " + path.string());
        }
        paths.push_back(path);
        if (item.raw_bgr) {
            max_width = std::max(max_width, item.width);
            max_height = std::max(max_height, item.height);
            max_stride = std::max(max_stride, item.row_stride);
        }
    }

    std::vector<cv::Mat> decoded(cases.size());
    std::vector<std::vector<std::uint8_t>> raw(cases.size());
    for (std::size_t i = 0; i < cases.size(); ++i) {
        if (cases[i].raw_bgr) {
            raw[i] = read_raw(paths[i]);
            const std::size_t expected = cases[i].row_stride *
                                          static_cast<std::size_t>(cases[i].height);
            if (raw[i].size() != expected) throw GateError("raw BGR size mismatch: " + cases[i].id);
            decoded[i] = cv::Mat(cases[i].height,
                                 cases[i].width,
                                 CV_8UC3,
                                 raw[i].data(),
                                 cases[i].row_stride);
        } else {
            decoded[i] = cv::imread(paths[i].string(), cv::IMREAD_COLOR);
            if (decoded[i].empty() || decoded[i].type() != CV_8UC3) {
                throw GateError("image decode failed: " + paths[i].string());
            }
        }
        max_width = std::max(max_width, decoded[i].cols);
        max_height = std::max(max_height, decoded[i].rows);
        max_stride = std::max(max_stride, static_cast<std::size_t>(decoded[i].step));
    }

    std::unique_ptr<stage_r::CudaPreprocessor> cuda_preprocessor;
    auto status = stage_r::CudaPreprocessor::create(
        max_width, max_height, max_stride, &cuda_preprocessor);
    if (!status.ok()) throw GateError(status.message());

    const edge_ai_defect::core::TensorInfo input_info{
        edge_ai_defect::core::TensorDataType::kFloat32,
        edge_ai_defect::core::TensorLayout::kNchw,
        {1, 3, 640, 640}};
    std::vector<float> cuda_tensor(stage_r::CudaPreprocessor::kTargetElementCount);
    std::vector<CaseResult> results;
    Aggregate aggregate;
    aggregate.errors.reserve(cases.size() * stage_r::CudaPreprocessor::kTargetElementCount);
    bool pass = true;
    for (std::size_t i = 0; i < cases.size(); ++i) {
        preprocess::PreprocessedFrame cpu_output;
        status = preprocess::Preprocessor().preprocess(decoded[i], input_info, &cpu_output);
        if (!status.ok()) throw GateError("CPU preprocessing failed for " + cases[i].id +
                                         ": " + status.message());
        preprocess::ImageTransformMetadata geometry;
        status = stage_r::CudaPreprocessor::compute_geometry(
            decoded[i].cols, decoded[i].rows, &geometry);
        if (!status.ok()) throw GateError("geometry failed for " + cases[i].id);
        const auto& cpu_geometry = cpu_output.transform;
        const bool geometry_pass = geometry.original_width == cpu_geometry.original_width &&
            geometry.original_height == cpu_geometry.original_height &&
            geometry.resized_width == cpu_geometry.resized_width &&
            geometry.resized_height == cpu_geometry.resized_height &&
            geometry.pad_left == cpu_geometry.pad_left &&
            geometry.pad_right == cpu_geometry.pad_right &&
            geometry.pad_top == cpu_geometry.pad_top &&
            geometry.pad_bottom == cpu_geometry.pad_bottom;
        status = cuda_preprocessor->preprocess(decoded[i].data,
                                               decoded[i].cols,
                                               decoded[i].rows,
                                               decoded[i].step,
                                               geometry);
        if (!status.ok()) throw GateError("CUDA preprocessing submission failed for " + cases[i].id +
                                         ": " + status.message());
        status = cuda_preprocessor->copy_output_to_host(cuda_tensor.data(), cuda_tensor.size());
        if (!status.ok()) throw GateError("CUDA output copy failed for " + cases[i].id +
                                         ": " + status.message());

        CaseResult result;
        result.id = cases[i].id;
        result.geometry_pass = geometry_pass;
        double case_sum = 0.0;
        for (std::size_t index = 0; index < cuda_tensor.size(); ++index) {
            if (!std::isfinite(cuda_tensor[index]) ||
                !std::isfinite(cpu_output.tensor.data[index])) {
                ++result.nonfinite;
                ++aggregate.nonfinite;
                continue;
            }
            const double error = std::abs(static_cast<double>(cuda_tensor[index]) -
                                          static_cast<double>(cpu_output.tensor.data[index]));
            case_sum += error;
            aggregate.sum += error;
            aggregate.max_abs = std::max(aggregate.max_abs, error);
            result.max_abs = std::max(result.max_abs, error);
            aggregate.errors.push_back(error);
        }
        result.mae = case_sum / static_cast<double>(cuda_tensor.size());
        pass = pass && result.geometry_pass && result.nonfinite == 0U &&
               result.mae <= kMaeLimit && result.max_abs <= kMaxLimit;
        results.push_back(result);
        std::cout << result.id << ": mae=" << result.mae
                  << " max=" << result.max_abs
                  << " nonfinite=" << result.nonfinite
                  << " geometry=" << (result.geometry_pass ? "PASS" : "FAIL") << '\n';
    }
    const double p99 = type7_p99(aggregate.errors);
    pass = pass && aggregate.nonfinite == 0U && p99 <= kP99Limit;
    write_report(options.report, corpus_id, results, aggregate, p99, pass);
    std::cout << "tensor gate: " << (pass ? "PASS" : "FAIL")
              << " mae=" << aggregate.sum / static_cast<double>(aggregate.errors.size())
              << " p99=" << p99 << " max=" << aggregate.max_abs
              << " nonfinite=" << aggregate.nonfinite << '\n';
    return pass ? 0 : 1;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        return run(parse_options(argc, argv));
    } catch (const std::exception& exception) {
        std::cerr << "stage_r_cuda_preprocess_gate: " << exception.what() << '\n';
        return 2;
    }
}
