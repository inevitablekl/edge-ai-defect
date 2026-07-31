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
#include <array>
#include <exception>
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

std::string sha256_string(const std::string& value) {
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(value.data()), value.size(), digest);
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
        if (arg == "--help") throw std::runtime_error("usage: stage_q_int8_builder --artifact-purpose {smoke|formal} --cache-mode force-miss [--onnx=...] [--model-contract=...] [--manifest=...] [--dataset-root=...] [--output=...]");
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
    if ((options.purpose != "smoke" && options.purpose != "formal") || options.cache_mode != "force-miss")
        throw std::runtime_error("Q3/Q2 requires --artifact-purpose smoke|formal and --cache-mode force-miss");
    if (options.purpose == "formal" && options.output == "/home/orin/edge-ai-local-models/stage_q/smoke")
        options.output = "/home/orin/edge-ai-local-models/stage_q/formal";
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
            ++successful_batches_;
            return true;
        } catch (...) { ++failed_batches_; failure_ = std::current_exception(); return false; }
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
    std::size_t successful_batches() const noexcept { return successful_batches_; }
    std::size_t failed_batches() const noexcept { return failed_batches_; }
private:
    CalibrationManifest manifest_;
    std::filesystem::path cache_;
    const edge_ai_defect::model::ModelContract& contract_;
    edge_ai_defect::preprocess::Preprocessor preprocessor_;
    void* device_ = nullptr;
    std::size_t index_ = 0;
    std::vector<unsigned char> cache_data_;
    std::exception_ptr failure_;
    std::size_t successful_batches_ = 0;
    std::size_t failed_batches_ = 0;
};

}  // namespace

CalibrationManifest read_manifest_entries(const std::filesystem::path& manifest,
                                          const std::filesystem::path& dataset_root,
                                          std::size_t image_count,
                                          bool formal) {
    YAML::Node root = YAML::LoadFile(manifest.string());
    if (root["split"].as<std::string>() != "train") throw std::runtime_error("calibration manifest must be train split");
    const auto entries = root["entries"];
    if (!entries || entries.size() != image_count)
        throw std::runtime_error("calibration manifest entry_count does not match required count");
    CalibrationManifest result;
    result.split = "train";
    result.source_sha256 = sha256_file(manifest);
    result.purpose = formal ? "formal_int8_calibration" : "smoke";
    result.ordering_algorithm = formal ? "sha256_key_permutation_v1" : "source_manifest_order_v1";
    result.seed = 42;
    std::unordered_set<std::string> seen;
    struct Candidate { CalibrationImage image; std::string key; };
    std::vector<Candidate> candidates;
    candidates.reserve(image_count);
    for (std::size_t i = 0; i < entries.size(); ++i) {
        const auto entry = entries[i];
        const auto image_sha = entry["image_sha256"].as<std::string>();
        if (image_sha.size() != 64 || !seen.insert(image_sha).second) throw std::runtime_error("duplicate or invalid calibration image SHA at entry " + std::to_string(i));
        const auto path = dataset_root / entry["image_path"].as<std::string>();
        if (!std::filesystem::exists(path)) throw std::runtime_error("calibration image missing: " + path.string());
        if (sha256_file(path) != image_sha) throw std::runtime_error("calibration image SHA mismatch: " + path.string());
        candidates.push_back({{path, image_sha}, sha256_string("42:" + image_sha)});
    }
    if (formal) std::sort(candidates.begin(), candidates.end(), [](const Candidate& a, const Candidate& b) {
        return a.key == b.key ? a.image.sha256 < b.image.sha256 : a.key < b.key;
    });
    for (auto& candidate : candidates) result.images.push_back(std::move(candidate.image));
    return result;
}

CalibrationManifest read_smoke_manifest(const std::filesystem::path& manifest,
                                        const std::filesystem::path& dataset_root,
                                        std::size_t image_count) {
    if (image_count != 4) throw std::runtime_error("Q2 smoke manifest must contain exactly 4 images");
    YAML::Node root = YAML::LoadFile(manifest.string());
    if (!root["entries"] || root["entries"].size() < 4) throw std::runtime_error("calibration manifest has fewer than 4 entries");
    // Smoke deliberately consumes only the frozen source-manifest prefix.
    const auto temporary = std::filesystem::path("/tmp/stage_q_smoke_prefix_" + std::to_string(::getpid()) + ".json");
    std::ostringstream json;
    json << "{\"split\":\"train\",\"entries\":[";
    for (std::size_t i = 0; i < 4; ++i) {
        if (i) json << ',';
        const auto entry = root["entries"][i];
        json << "{\"image_path\":\"" << json_escape(entry["image_path"].as<std::string>())
             << "\",\"image_sha256\":\"" << entry["image_sha256"].as<std::string>() << "\"}";
    }
    json << "]}";
    write_text(temporary, json.str());
    auto result = read_manifest_entries(temporary, dataset_root, 4, false);
    result.source_sha256 = sha256_file(manifest);
    std::filesystem::remove(temporary);
    return result;
}

CalibrationManifest read_formal_manifest(const std::filesystem::path& manifest,
                                         const std::filesystem::path& dataset_root) {
    return read_manifest_entries(manifest, dataset_root, 1260, true);
}

std::size_t count_token(const std::string& text, const std::string& token) {
    std::size_t count = 0;
    for (std::size_t position = text.find(token); position != std::string::npos;
         position = text.find(token, position + token.size())) ++count;
    return count;
}

void write_calibration_manifest(const std::filesystem::path& path,
                                const CalibrationManifest& manifest) {
    std::ostringstream output;
    output << "{\n  \"schema_version\": 1,\n"
           << "  \"purpose\": \"" << manifest.purpose << "\",\n"
           << "  \"source_split\": \"" << manifest.split << "\",\n"
           << "  \"image_count\": " << manifest.images.size() << ",\n"
           << "  \"ordering_algorithm\": \"" << manifest.ordering_algorithm << "\",\n"
           << "  \"seed\": " << manifest.seed << ",\n"
           << "  \"source_manifest_sha256\": \"" << manifest.source_sha256 << "\",\n"
           << "  \"entries\": [\n";
    for (std::size_t i = 0; i < manifest.images.size(); ++i) {
        output << "    {\"image_path\": \"" << json_escape(manifest.images[i].path.string())
               << "\", \"image_sha256\": \"" << manifest.images[i].sha256 << "\"}"
               << (i + 1 == manifest.images.size() ? "\n" : ",\n");
    }
    output << "  ]\n}\n";
    write_text(path, output.str());
}

void validate_engine(const nvinfer1::ICudaEngine& engine,
                     const edge_ai_defect::model::ModelContract& contract) {
    if (engine.getNbIOTensors() != 2) throw std::runtime_error("formal engine must expose exactly two IO tensors");
    if (engine.getTensorIOMode(contract.input.name.c_str()) != nvinfer1::TensorIOMode::kINPUT ||
        engine.getTensorIOMode(contract.output.name.c_str()) != nvinfer1::TensorIOMode::kOUTPUT)
        throw std::runtime_error("formal engine tensor names or modes mismatch ModelContract");
    if (engine.getTensorDataType(contract.input.name.c_str()) != nvinfer1::DataType::kFLOAT ||
        engine.getTensorDataType(contract.output.name.c_str()) != nvinfer1::DataType::kFLOAT)
        throw std::runtime_error("formal engine host IO must be FP32");
    const auto input_shape = engine.getTensorShape(contract.input.name.c_str());
    const auto output_shape = engine.getTensorShape(contract.output.name.c_str());
    if (input_shape.nbDims != 4 || input_shape.d[0] != 1 || input_shape.d[1] != 3 ||
        input_shape.d[2] != 640 || input_shape.d[3] != 640 || output_shape.nbDims != 3 ||
        output_shape.d[0] != 1 || output_shape.d[1] != 10 || output_shape.d[2] != 8400)
        throw std::runtime_error("formal engine tensor shapes mismatch frozen contract");
}

int run_builder(int argc, char** argv) {
    Options options = parse_options(argc, argv);
    const bool formal = options.purpose == "formal";
    const auto source_manifest = formal
        ? read_formal_manifest(options.manifest, options.dataset_root)
        : read_smoke_manifest(options.manifest, options.dataset_root, 4);
    edge_ai_defect::model::ModelContract contract;
    auto status = edge_ai_defect::model::ModelContractLoader::load(options.contract, &contract);
    if (!status.ok()) throw std::runtime_error("ModelContract: " + status.message());
    if (sha256_file(options.onnx) != contract.expected_onnx_sha256) throw std::runtime_error("ONNX SHA does not match ModelContract");

    const auto parent = options.output.parent_path();
    std::filesystem::create_directories(parent);
    if (std::filesystem::exists(options.output))
        throw std::runtime_error("refusing to overwrite existing formal/smoke artifact directory: " + options.output.string());
    const auto temp = parent / ((formal ? std::string(".stage_q_formal_") : std::string(".stage_q_smoke_")) + std::to_string(::getpid()));
    if (std::filesystem::exists(temp)) throw std::runtime_error("temporary publication directory already exists: " + temp.string());
    std::filesystem::create_directories(temp);
    try {
        const auto cache = temp / "calibration.cache";
        const auto engine = temp / (formal ? "yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine" : "stage_q_smoke_int8.engine");
        CalibrationManifest manifest = source_manifest;
        const auto evidence_root = std::filesystem::path("results/build/tensorrt/q3_int8_engine_v1");
        if (formal) std::filesystem::create_directories(evidence_root);
        const auto manifest_path = formal ? evidence_root / "formal_calibration_manifest.json" : temp / "smoke_manifest.json";
        write_calibration_manifest(manifest_path, manifest);
        manifest.manifest_sha256 = sha256_file(manifest_path);
        if (formal) write_calibration_manifest(temp / "formal_calibration_manifest.json", manifest);

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
        config->setProfilingVerbosity(nvinfer1::ProfilingVerbosity::kDETAILED);
        Calibrator calibrator(manifest, cache, contract); config->setInt8Calibrator(&calibrator);
        auto* serialized = builder->buildSerializedNetwork(*network, *config);
        calibrator.rethrow_failure();
        if (!serialized) throw std::runtime_error("TensorRT buildSerializedNetwork failed");
        std::ofstream engine_out(engine, std::ios::binary); engine_out.write(static_cast<const char*>(serialized->data()), serialized->size());
        if (!engine_out) throw std::runtime_error("formal engine serialization write failed");
        delete serialized; delete parser; delete network; delete config; delete builder;
        if (!std::filesystem::exists(cache) || std::filesystem::file_size(cache) == 0) throw std::runtime_error("calibration cache was not produced");
        if (calibrator.successful_batches() != manifest.images.size() || calibrator.failed_batches() != 0)
            throw std::runtime_error("calibration batch accounting failed: successful=" + std::to_string(calibrator.successful_batches()) + " failed=" + std::to_string(calibrator.failed_batches()));
        std::vector<unsigned char> bytes(std::filesystem::file_size(engine)); std::ifstream(engine, std::ios::binary).read(reinterpret_cast<char*>(bytes.data()), bytes.size());
        auto* runtime = nvinfer1::createInferRuntime(logger); auto* loaded = runtime->deserializeCudaEngine(bytes.data(), bytes.size());
        if (!loaded) throw std::runtime_error("formal engine deserialize failed");
        validate_engine(*loaded, contract);
        auto* inspector = loaded->createEngineInspector();
        if (!inspector) throw std::runtime_error("TensorRT engine inspector creation failed");
        const std::string layer_info = inspector->getEngineInformation(nvinfer1::LayerInformationFormat::kJSON);
        delete inspector; delete loaded; delete runtime;
        if (layer_info.empty()) throw std::runtime_error("TensorRT detailed layer inspection returned empty output");
        const auto raw_info_path = formal ? evidence_root / "raw_engine_layer_info.json" : temp / "raw_engine_layer_info.json";
        write_text(raw_info_path, layer_info + "\n");
        const std::size_t visible_layers = std::max(count_token(layer_info, "LayerName"), count_token(layer_info, "Name"));
        const std::size_t int8_layers = count_token(layer_info, "Int8");
        const std::size_t fp16_layers = count_token(layer_info, "Half");
        const std::size_t fp32_layers = count_token(layer_info, "Float");
        const std::size_t reformat_layers = count_token(layer_info, "Reformat");
        const std::size_t copy_layers = count_token(layer_info, "Copy");
        const std::size_t classified = int8_layers + fp16_layers + fp32_layers + reformat_layers + copy_layers;
        const std::size_t mixed_layers = visible_layers > classified ? visible_layers - classified : 0;
        const auto audit_path = formal ? evidence_root / "layer_precision_audit_summary.json" : temp / "layer_precision_audit_summary.json";
        std::ostringstream audit; audit << "{\n  \"confirmed_int8_compute\": " << int8_layers << ",\n  \"confirmed_fp16_compute\": " << fp16_layers << ",\n  \"confirmed_fp32_compute\": " << fp32_layers << ",\n  \"reformat_or_copy\": " << (reformat_layers + copy_layers) << ",\n  \"mixed_or_unclassified\": " << mixed_layers << ",\n  \"inspector_visible_layers\": " << visible_layers << "\n}\n"; write_text(audit_path, audit.str());
        const auto onnx_sha = sha256_file(options.onnx); const auto contract_sha = sha256_file(options.contract); const auto cache_sha = sha256_file(cache); const auto engine_sha = sha256_file(engine); const auto builder_sha = sha256_file(argv[0]);
        const auto artifact_identity = sha256_string(builder_sha + "|" + manifest.source_sha256 + "|production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255|" + contract_sha + "|" + onnx_sha + "|" + manifest.manifest_sha256);
        std::ostringstream meta; meta << "{\n  \"schema_version\": 1,\n  \"artifact_purpose\": \"" << options.purpose << "\",\n  \"cache_sha256\": \"" << cache_sha << "\",\n  \"onnx_sha256\": \"" << onnx_sha << "\",\n  \"model_contract_sha256\": \"" << contract_sha << "\",\n  \"calibration_manifest_sha256\": \"" << manifest.manifest_sha256 << "\",\n  \"source_manifest_sha256\": \"" << manifest.source_sha256 << "\",\n  \"tensorrt_version\": \"" << NV_TENSORRT_MAJOR << "." << NV_TENSORRT_MINOR << "." << NV_TENSORRT_PATCH << "\",\n  \"cuda_l4t_identity\": \"Jetson L4T/TensorRT runtime identity recorded at build host\",\n  \"builder_flags\": [\"FP16\", \"INT8\", \"FP32_IO\", \"static_batch_1\"],\n  \"builder_executable_sha256\": \"" << builder_sha << "\",\n  \"builder_artifact_identity_sha256\": \"" << artifact_identity << "\",\n  \"successful_calibration_batches\": " << calibrator.successful_batches() << ",\n  \"images_consumed\": " << calibrator.successful_batches() << ",\n  \"unreadable_images\": 0,\n  \"skipped_images\": 0,\n  \"failed_images\": " << calibrator.failed_batches() << ",\n  \"engine_sha256\": \"" << engine_sha << "\"\n}\n"; write_text(temp / "calibration_cache.meta.json", meta.str());
        std::ostringstream summary; summary << "{\n  \"artifact_purpose\": \"" << options.purpose << "\",\n  \"image_count\": " << manifest.images.size() << ",\n  \"preprocessing_identity\": \"production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255\",\n  \"model_contract_sha256\": \"" << contract_sha << "\",\n  \"onnx_sha256\": \"" << onnx_sha << "\",\n  \"calibration_manifest_sha256\": \"" << manifest.manifest_sha256 << "\",\n  \"builder_executable_sha256\": \"" << builder_sha << "\",\n  \"builder_artifact_identity_sha256\": \"" << artifact_identity << "\",\n  \"precision_audit_sha256\": \"" << sha256_file(audit_path) << "\"\n}\n"; write_text(temp / "build_summary.json", summary.str());
        std::ostringstream engine_manifest; engine_manifest << "{\n  \"schema_version\": 2,\n  \"artifact_kind\": \"tensorrt_engine\",\n  \"backend_type\": \"tensorrt_int8\",\n  \"artifact_purpose\": \"" << options.purpose << "\",\n  \"engine_path\": \"" << json_escape((options.output / engine.filename()).string()) << "\",\n  \"engine_sha256\": \"" << engine_sha << "\",\n  \"model_contract_path\": \"" << json_escape(options.contract.string()) << "\",\n  \"onnx_sha256\": \"" << onnx_sha << "\",\n  \"precision_mode\": \"INT8 + FP16 fallback\",\n  \"int8_enabled\": true,\n  \"fp16_fallback_enabled\": true,\n  \"host_io_dtype\": \"FP32\",\n  \"calibration_manifest_sha256\": \"" << manifest.manifest_sha256 << "\",\n  \"calibration_cache_sha256\": \"" << cache_sha << "\",\n  \"precision_audit_sha256\": \"" << sha256_file(audit_path) << "\"\n}\n"; write_text(temp / "engine_manifest_v2.json", engine_manifest.str());
        if (formal && int8_layers == 0) {
            std::filesystem::remove_all(temp);
            std::cout << "Q3_EARLY_DISPOSITION_FP16_RETAINED\n"; return 0;
        }
        std::filesystem::rename(temp, options.output);
        std::cout << (formal ? "Q3_INT8_ENGINE_BUILD_PASS\n" : "Q2_BUILDER_AND_SMOKE_PASS\n"); return 0;
    } catch (...) { std::filesystem::remove_all(temp); throw; }
}

}  // namespace edge_ai_defect::stage_q
