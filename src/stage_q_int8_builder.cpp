#include "edge_ai_defect/stage_q/stage_q_int8_builder.hpp"

#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/core/tensor.hpp"

#include <NvInfer.h>
#include <NvOnnxParser.h>
#include <cuda_runtime_api.h>
#include <yaml-cpp/yaml.h>
#include <opencv2/imgcodecs.hpp>
#include <openssl/sha.h>

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <unistd.h>
#include <unordered_set>

namespace edge_ai_defect::stage_q {
namespace {

std::string hex_digest(const unsigned char* digest) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (std::size_t i = 0; i < SHA256_DIGEST_LENGTH; ++i)
        out << std::setw(2) << static_cast<int>(digest[i]);
    return out.str();
}

std::string sha256_file(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open file for SHA256: " + path.string());
    SHA256_CTX context;
    SHA256_Init(&context);
    std::array<unsigned char, 1U << 16U> buffer{};
    while (input) {
        input.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        const auto count = input.gcount();
        if (count > 0) SHA256_Update(&context, buffer.data(), static_cast<std::size_t>(count));
    }
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256_Final(digest, &context);
    return hex_digest(digest);
}

std::string json_escape(const std::string& value) {
    std::string result;
    for (char c : value) {
        if (c == '\\' || c == '"') result += '\\';
        result += c;
    }
    return result;
}

void write_text(const std::filesystem::path& path, const std::string& text) {
    std::ofstream output(path);
    if (!output) throw std::runtime_error("cannot write " + path.string());
    output << text;
    if (!output) throw std::runtime_error("write failed: " + path.string());
}

struct Options {
    std::filesystem::path onnx = "models/onnx/yolov8n_neudet_frozen.onnx";
    std::filesystem::path contract = "configs/model_contracts/yolov8n_neudet_frozen.yaml";
    std::filesystem::path manifest = "results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json";
    std::filesystem::path dataset_root = "data/raw/NEU-DET";
    std::filesystem::path output = "/home/orin/edge-ai-local-models/stage_q/smoke";
    std::string purpose;
    std::string cache_mode;
};

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string arg(argv[i]);
        const auto take = [&](const std::string& name) -> std::filesystem::path {
            if (arg.rfind(name + "=", 0) != 0) throw std::runtime_error("expected " + name + "=<value>");
            return arg.substr(name.size() + 1);
        };
        if (arg == "--help") throw std::runtime_error("usage: stage_q_int8_builder --artifact-purpose smoke --cache-mode force-miss [--onnx=...] [--model-contract=...] [--manifest=...] [--dataset-root=...] [--output=...]");
        if (arg.rfind("--onnx=", 0) == 0) options.onnx = take("--onnx");
        else if (arg.rfind("--model-contract=", 0) == 0) options.contract = take("--model-contract");
        else if (arg.rfind("--manifest=", 0) == 0) options.manifest = take("--manifest");
        else if (arg.rfind("--dataset-root=", 0) == 0) options.dataset_root = take("--dataset-root");
        else if (arg.rfind("--output=", 0) == 0) options.output = take("--output");
        else if (arg == "--artifact-purpose" && i + 1 < argc) options.purpose = argv[++i];
        else if (arg.rfind("--artifact-purpose=", 0) == 0) options.purpose = arg.substr(19);
        else if (arg == "--cache-mode" && i + 1 < argc) options.cache_mode = argv[++i];
        else if (arg.rfind("--cache-mode=", 0) == 0) options.cache_mode = arg.substr(13);
        else throw std::runtime_error("unknown argument: " + arg);
    }
    if (options.purpose != "smoke" || options.cache_mode != "force-miss")
        throw std::runtime_error("Q2 requires --artifact-purpose smoke and --cache-mode force-miss");
    return options;
}

class Logger final : public nvinfer1::ILogger {
    void log(Severity severity, const char* message) noexcept override {
        if (severity <= Severity::kWARNING) std::cerr << "[TensorRT] " << message << '\n';
    }
};

class Calibrator final : public nvinfer1::IInt8EntropyCalibrator2 {
public:
    Calibrator(const CalibrationManifest& manifest, const std::filesystem::path& cache,
               const edge_ai_defect::model::ModelContract& contract)
        : manifest_(manifest), cache_(cache), contract_(contract) {
        if (cudaMalloc(&device_, 3U * 640U * 640U * sizeof(float)) != cudaSuccess)
            throw std::runtime_error("cudaMalloc calibration buffer failed");
    }
    ~Calibrator() override { if (device_) cudaFree(device_); }
    int getBatchSize() const noexcept override { return 1; }
    bool getBatch(void* bindings[], const char*[], int) noexcept override {
        try {
            if (index_ == manifest_.images.size()) return false;
            const auto& item = manifest_.images[index_++];
            cv::Mat image = cv::imread(item.path.string(), cv::IMREAD_COLOR);
            if (image.empty()) throw std::runtime_error("calibration image cannot be decoded: " + item.path.string());
            edge_ai_defect::preprocess::PreprocessedFrame frame;
            auto status = preprocessor_.preprocess(image, contract_.input.tensor_info, &frame);
            if (!status.ok()) throw std::runtime_error("preprocess failed: " + status.message());
            if (cudaMemcpy(device_, frame.tensor.data.data(), frame.tensor.data.size() * sizeof(float), cudaMemcpyHostToDevice) != cudaSuccess)
                throw std::runtime_error("cudaMemcpy calibration batch failed");
            bindings[0] = device_;
            return true;
        } catch (...) { failure_ = std::current_exception(); return false; }
    }
    const void* readCalibrationCache(std::size_t& length) noexcept override {
        if (!std::filesystem::exists(cache_)) { length = 0; return nullptr; }
        std::ifstream input(cache_, std::ios::binary | std::ios::ate);
        if (!input) { length = 0; return nullptr; }
        const auto size = input.tellg(); input.seekg(0);
        cache_data_.resize(static_cast<std::size_t>(size));
        input.read(reinterpret_cast<char*>(cache_data_.data()), size);
        length = cache_data_.size(); return cache_data_.data();
    }
    void writeCalibrationCache(const void* cache, std::size_t length) noexcept override {
        try { std::ofstream output(cache_, std::ios::binary); output.write(static_cast<const char*>(cache), length); }
        catch (...) { failure_ = std::current_exception(); }
    }
    void rethrow_failure() { if (failure_) std::rethrow_exception(failure_); }
private:
    CalibrationManifest manifest_;
    std::filesystem::path cache_;
    const edge_ai_defect::model::ModelContract& contract_;
    edge_ai_defect::preprocess::Preprocessor preprocessor_;
    void* device_ = nullptr;
    std::size_t index_ = 0;
    std::vector<unsigned char> cache_data_;
    std::exception_ptr failure_;
};

}  // namespace

CalibrationManifest read_smoke_manifest(const std::filesystem::path& manifest,
                                        const std::filesystem::path& dataset_root,
                                        std::size_t image_count) {
    if (image_count != 4) throw std::runtime_error("Q2 smoke manifest must contain exactly 4 images");
    YAML::Node root = YAML::LoadFile(manifest.string());
    if (root["split"].as<std::string>() != "train") throw std::runtime_error("calibration manifest must be train split");
    const auto entries = root["entries"];
    if (!entries || entries.size() < image_count) throw std::runtime_error("calibration manifest has fewer than 4 entries");
    CalibrationManifest result{"train", sha256_file(manifest), {}};
    std::unordered_set<std::string> seen;
    for (std::size_t i = 0; i < image_count; ++i) {
        const auto entry = entries[i];
        const auto image_sha = entry["image_sha256"].as<std::string>();
        if (image_sha.size() != 64 || !seen.insert(image_sha).second) throw std::runtime_error("duplicate or invalid calibration image SHA at entry " + std::to_string(i));
        const auto path = dataset_root / entry["image_path"].as<std::string>();
        if (!std::filesystem::exists(path)) throw std::runtime_error("calibration image missing: " + path.string());
        if (sha256_file(path) != image_sha) throw std::runtime_error("calibration image SHA mismatch: " + path.string());
        result.images.push_back({path, image_sha});
    }
    return result;
}

int run_builder(int argc, char** argv) {
    Options options = parse_options(argc, argv);
    const auto manifest = read_smoke_manifest(options.manifest, options.dataset_root, 4);
    edge_ai_defect::model::ModelContract contract;
    auto status = edge_ai_defect::model::ModelContractLoader::load(options.contract, &contract);
    if (!status.ok()) throw std::runtime_error("ModelContract: " + status.message());
    if (sha256_file(options.onnx) != contract.expected_onnx_sha256) throw std::runtime_error("ONNX SHA does not match ModelContract");

    const auto parent = options.output.parent_path();
    std::filesystem::create_directories(parent);
    const auto temp = parent / (".stage_q_smoke_" + std::to_string(::getpid()));
    std::filesystem::remove_all(temp);
    std::filesystem::create_directories(temp);
    try {
        const auto cache = temp / "calibration.cache";
        const auto engine = temp / "stage_q_smoke_int8.engine";
        const auto smoke_manifest = temp / "smoke_manifest.json";
        std::ostringstream sm; sm << "{\n  \"artifact_purpose\": \"smoke\",\n  \"split\": \"train\",\n  \"image_count\": 4,\n  \"source_manifest_sha256\": \"" << manifest.source_sha256 << "\",\n  \"images\": [\n";
        for (std::size_t i = 0; i < manifest.images.size(); ++i) sm << "    {\"path\": \"" << json_escape(manifest.images[i].path.string()) << "\", \"sha256\": \"" << manifest.images[i].sha256 << "\"}" << (i + 1 == manifest.images.size() ? "\n" : ",\n");
        sm << "  ]\n}\n"; write_text(smoke_manifest, sm.str());

        Logger logger;
        auto* builder = nvinfer1::createInferBuilder(logger);
        if (!builder) throw std::runtime_error("createInferBuilder failed");
        const auto flags = 1U << static_cast<unsigned int>(nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);
        auto* network = builder->createNetworkV2(flags);
        auto* parser = nvonnxparser::createParser(*network, logger);
        if (!network || !parser || !parser->parseFromFile(options.onnx.c_str(), static_cast<int>(nvinfer1::ILogger::Severity::kWARNING))) throw std::runtime_error("ONNX parser failed");
        auto* config = builder->createBuilderConfig();
        config->setMemoryPoolLimit(nvinfer1::MemoryPoolType::kWORKSPACE, 1ULL << 30U);
        config->setFlag(nvinfer1::BuilderFlag::kFP16); config->setFlag(nvinfer1::BuilderFlag::kINT8);
        Calibrator calibrator(manifest, cache, contract); config->setInt8Calibrator(&calibrator);
        auto* serialized = builder->buildSerializedNetwork(*network, *config);
        calibrator.rethrow_failure();
        if (!serialized) throw std::runtime_error("TensorRT buildSerializedNetwork failed");
        std::ofstream engine_out(engine, std::ios::binary); engine_out.write(static_cast<const char*>(serialized->data()), serialized->size());
        delete serialized; delete parser; delete network; delete config; delete builder;
        if (!std::filesystem::exists(cache) || std::filesystem::file_size(cache) == 0) throw std::runtime_error("calibration cache was not produced");
        std::vector<unsigned char> bytes(std::filesystem::file_size(engine)); std::ifstream(engine, std::ios::binary).read(reinterpret_cast<char*>(bytes.data()), bytes.size());
        auto* runtime = nvinfer1::createInferRuntime(logger); auto* loaded = runtime->deserializeCudaEngine(bytes.data(), bytes.size());
        if (!loaded) throw std::runtime_error("smoke engine deserialize failed"); delete loaded; delete runtime;
        const auto onnx_sha = sha256_file(options.onnx); const auto contract_sha = sha256_file(options.contract); const auto cache_sha = sha256_file(cache); const auto engine_sha = sha256_file(engine);
        std::ostringstream meta; meta << "{\n  \"schema_version\": 1,\n  \"artifact_purpose\": \"smoke\",\n  \"cache_sha256\": \"" << cache_sha << "\",\n  \"onnx_sha256\": \"" << onnx_sha << "\",\n  \"model_contract_sha256\": \"" << contract_sha << "\",\n  \"calibration_manifest_sha256\": \"" << manifest.source_sha256 << "\",\n  \"tensorrt_version\": " << NV_TENSORRT_MAJOR << "" << NV_TENSORRT_MINOR << "" << NV_TENSORRT_PATCH << ",\n  \"cuda_l4t_identity\": \"Jetson L4T/TensorRT runtime identity recorded at build host\",\n  \"builder_flags\": [\"FP16\", \"INT8\", \"FP32_IO\", \"static_batch_1\"],\n  \"builder_executable_sha256\": \"" << sha256_file(argv[0]) << "\",\n  \"engine_sha256\": \"" << engine_sha << "\"\n}\n"; write_text(temp / "calibration_cache.meta.json", meta.str());
        write_text(temp / "build_summary.json", "{\n  \"artifact_purpose\": \"smoke\",\n  \"image_count\": 4,\n  \"preprocessing_identity\": \"production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255\",\n  \"model_contract_sha256\": \"" + contract_sha + "\",\n  \"onnx_sha256\": \"" + onnx_sha + "\",\n  \"calibration_manifest_sha256\": \"" + manifest.source_sha256 + "\",\n  \"builder_executable_sha256\": \"" + sha256_file(argv[0]) + "\"\n}\n");
        std::filesystem::remove_all(options.output); std::filesystem::rename(temp, options.output);
        std::cout << "Q2_BUILDER_AND_SMOKE_PASS\n"; return 0;
    } catch (...) { std::filesystem::remove_all(temp); throw; }
}

}  // namespace edge_ai_defect::stage_q
