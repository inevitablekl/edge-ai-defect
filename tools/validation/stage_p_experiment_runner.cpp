#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "edge_ai_defect/runtime/stage_p_experiment_runner.hpp"
#include "edge_ai_defect/runtime/timed_json_sink.hpp"

#include <openssl/evp.h>

#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

namespace fs = std::filesystem;
using edge_ai_defect::core::ErrorCode;
using edge_ai_defect::core::Status;
using edge_ai_defect::model::ModelContract;
using edge_ai_defect::runtime::RuntimeConfig;

struct Arguments {
    bool help_requested = false;
    fs::path config;
    fs::path corpus_manifest;
    fs::path trace;
    fs::path sidecar;
    fs::path hashes;
    std::string run_id;
    std::size_t cycles = 1;
    std::size_t max_frames = 0;
};

class SinkForwarder final : public edge_ai_defect::runtime::IResultSink {
public:
    explicit SinkForwarder(edge_ai_defect::runtime::IResultSink& sink) : sink_(sink) {}
    Status begin_run(const edge_ai_defect::runtime::RunMetadata& metadata) override {
        return sink_.begin_run(metadata);
    }
    Status write_frame(const edge_ai_defect::runtime::FrameResult& frame) override {
        return sink_.write_frame(frame);
    }
    Status end_run(const edge_ai_defect::runtime::RunSummary& summary) override {
        return sink_.end_run(summary);
    }
private:
    edge_ai_defect::runtime::IResultSink& sink_;
};

void print_usage(std::ostream& output) {
    output << "Usage: stage_p_experiment_runner --config PATH"
              " --corpus-manifest PATH --run-id ID --trace PATH"
              " --sidecar PATH --hashes PATH [--cycles N] [--max-frames N]\n"
              "Stage P experiment-only RuntimeConfig v4 runner.\n";
}

Status parse_size(std::string_view value, const char* name, std::size_t* output) {
    if (value.empty() || output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               std::string(name) + " must be a positive integer");
    }
    std::size_t parsed = 0;
    try {
        std::size_t consumed = 0;
        parsed = std::stoull(std::string(value), &consumed);
        if (consumed != value.size() || parsed == 0) throw std::invalid_argument("invalid");
    } catch (const std::exception&) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               std::string(name) + " must be a positive integer");
    }
    *output = parsed;
    return Status::success();
}

Status parse_arguments(int argc, char** argv, Arguments* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument, "argument output is null");
    }
    Arguments arguments;
    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];
        if (option == "--help" || option == "-h") {
            print_usage(std::cout);
            arguments.help_requested = true;
            *output = std::move(arguments);
            return Status::success();
        }
        if (index + 1 >= argc) {
            return Status::failure(ErrorCode::kInvalidArgument, "missing value for " + option);
        }
        const std::string value = argv[++index];
        if (option == "--config") arguments.config = value;
        else if (option == "--corpus-manifest") arguments.corpus_manifest = value;
        else if (option == "--run-id") arguments.run_id = value;
        else if (option == "--trace") arguments.trace = value;
        else if (option == "--sidecar") arguments.sidecar = value;
        else if (option == "--hashes") arguments.hashes = value;
        else if (option == "--cycles") {
            Status status = parse_size(value, "--cycles", &arguments.cycles);
            if (!status.ok()) return status;
        } else if (option == "--max-frames") {
            Status status = parse_size(value, "--max-frames", &arguments.max_frames);
            if (!status.ok()) return status;
        } else {
            return Status::failure(ErrorCode::kInvalidArgument, "unknown option: " + option);
        }
    }
    if (arguments.config.empty() || arguments.corpus_manifest.empty() ||
        arguments.run_id.empty() || arguments.trace.empty() ||
        arguments.sidecar.empty() || arguments.hashes.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "config, corpus manifest, run id, trace, sidecar, and hashes are required");
    }
    *output = std::move(arguments);
    return Status::success();
}

Status sha256_file(const fs::path& path, std::string* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument, "SHA output is null");
    }
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        return Status::failure(ErrorCode::kIoError, "cannot open file for SHA-256: " + path.string());
    }
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        return Status::failure(ErrorCode::kIoError, "cannot initialize SHA-256");
    }
    std::array<char, 64 * 1024> buffer{};
    while (input.good()) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context, buffer.data(), static_cast<std::size_t>(count)) != 1) {
            EVP_MD_CTX_free(context);
            return Status::failure(ErrorCode::kIoError, "cannot update SHA-256");
        }
    }
    if (!input.eof()) {
        EVP_MD_CTX_free(context);
        return Status::failure(ErrorCode::kIoError, "cannot read file for SHA-256: " + path.string());
    }
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int digest_length = 0;
    const bool finalized = EVP_DigestFinal_ex(context, digest.data(), &digest_length) == 1;
    EVP_MD_CTX_free(context);
    if (!finalized) return Status::failure(ErrorCode::kIoError, "cannot finalize SHA-256");
    std::ostringstream hex;
    hex << std::hex;
    for (unsigned int index = 0; index < digest_length; ++index) {
        hex.width(2);
        hex.fill('0');
        hex << static_cast<unsigned int>(digest[index]);
    }
    *output = hex.str();
    return Status::success();
}

Status executable_path(fs::path* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "executable output is null");
    std::error_code error;
    const fs::path path = fs::read_symlink("/proc/self/exe", error);
    if (error || path.empty()) {
        return Status::failure(ErrorCode::kIoError, "cannot resolve /proc/self/exe");
    }
    *output = path;
    return Status::success();
}

Status write_hashes(const fs::path& path, const std::string& run_id,
                    const edge_ai_defect::runtime::CanonicalHashSink& hash_sink) {
    std::ofstream output(path);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write hash output: " + path.string());
    output << "{\n  \"run_id\": \"" << run_id << "\",\n"
           << "  \"run_sha256\": \"" << hash_sink.run_hash() << "\",\n"
           << "  \"cycle_sha256\": [\n";
    bool first = true;
    for (const auto& [cycle, hash] : hash_sink.cycle_hashes()) {
        if (!first) output << ",\n";
        first = false;
        output << "    {\"cycle_id\": " << cycle << ", \"sha256\": \"" << hash << "\"}";
    }
    output << "\n  ]\n}\n";
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot finalize hash output: " + path.string());
    return Status::success();
}

Status write_sidecar(const fs::path& path, const Arguments& arguments,
                     const std::string& config_sha256,
                     const std::string& executable_sha256,
                     const std::string& engine_sha256,
                     const std::string& manifest_sha256,
                     const std::string& contract_sha256,
                     const std::string& corpus_manifest_sha256,
                     const RuntimeConfig& config) {
    std::ofstream output(path);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write sidecar: " + path.string());
    output << "{\n"
           << "  \"run_id\": \"" << arguments.run_id << "\",\n"
           << "  \"runtime_mode\": \"" << config.runtime_mode << "\",\n"
           << "  \"config_sha256\": \"" << config_sha256 << "\",\n"
           << "  \"executable_sha256\": \"" << executable_sha256 << "\",\n"
           << "  \"engine_sha256\": \"" << engine_sha256 << "\",\n"
           << "  \"manifest_sha256\": \"" << manifest_sha256 << "\",\n"
           << "  \"contract_sha256\": \"" << contract_sha256 << "\",\n"
           << "  \"corpus_manifest_sha256\": \"" << corpus_manifest_sha256 << "\"\n"
           << "}\n";
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot finalize sidecar: " + path.string());
    return Status::success();
}

Status hash_named_file(const fs::path& path, const char* label, std::string* output) {
    Status status = sha256_file(path, output);
    if (!status.ok()) {
        return Status::failure(status.code(), std::string(label) + ": " + status.message());
    }
    return status;
}

}  // namespace

int main(int argc, char** argv) {
    Arguments arguments;
    Status status = parse_arguments(argc, argv, &arguments);
    if (!status.ok()) {
        std::cerr << "stage_p_experiment_runner: " << status.message() << '\n';
        print_usage(std::cerr);
        return 2;
    }
    if (arguments.help_requested) return 0;

    RuntimeConfig config;
    status = edge_ai_defect::runtime::RuntimeConfigLoader::load(arguments.config, &config);
    if (!status.ok()) {
        std::cerr << "runtime config: " << status.message() << '\n';
        return 3;
    }
    if (config.schema_version != 4U || config.backend_type != "tensorrt_fp16" ||
        (config.runtime_mode != "serial" && config.runtime_mode != "pipeline")) {
        std::cerr << "stage_p_experiment_runner requires RuntimeConfig v4 with"
                     " backend.type tensorrt_fp16 and runtime.mode serial or pipeline\n";
        return 3;
    }

    ModelContract contract;
    status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) {
        std::cerr << "model contract: " << status.message() << '\n';
        return 3;
    }
    auto manifest = std::make_unique<edge_ai_defect::model::TensorRtEngineManifest>();
    status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, manifest.get());
    if (!status.ok()) {
        std::cerr << "TensorRT manifest: " << status.message() << '\n';
        return 3;
    }
    std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> engine;
    status = edge_ai_defect::inference::create_inference_engine(config, contract, &engine);
    if (!status.ok()) {
        std::cerr << "engine factory: " << status.message() << '\n';
        return 3;
    }

    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> source;
    status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, arguments.corpus_manifest, arguments.cycles, &source,
        arguments.max_frames);
    if (!status.ok()) {
        std::cerr << "corpus replay: " << status.message() << '\n';
        return 3;
    }
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> json_sink;
    status = edge_ai_defect::runtime::JsonSink::create(
        config.output_json_path, config.output_overwrite, &json_sink);
    if (!status.ok()) {
        std::cerr << "JSON sink: " << status.message() << '\n';
        return 3;
    }

    edge_ai_defect::preprocess::Preprocessor preprocessor;
    edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
    edge_ai_defect::runtime::TimedJsonSink timed_json_sink(*json_sink);
    edge_ai_defect::runtime::CanonicalHashSink hash_sink;
    edge_ai_defect::runtime::ConcurrentFrameTraceRecorder trace_recorder;

    edge_ai_defect::runtime::RunMetadata metadata;
    metadata.schema_version = 3;
    metadata.backend_type = config.backend_type;
    metadata.model_filename = config.tensorrt.engine_path.filename().string();
    metadata.model_sha256 = manifest->engine_sha256;
    metadata.contract_filename = config.model_contract_path.filename().string();
    metadata.artifact_kind = "tensorrt_engine";
    metadata.source_onnx_sha256 = manifest->source_onnx_sha256;
    metadata.engine_manifest_filename = config.tensorrt.engine_manifest_path.filename().string();
    metadata.class_names = contract.class_names;
    metadata.postprocess_config = config.postprocess_config;
    metadata.timing_enabled = config.timing_enabled;
    metadata.runtime_v3 = edge_ai_defect::runtime::RuntimeMetadataV3{
        config.runtime_mode, config.input_type,
        config.runtime_mode == "pipeline"
            ? std::optional<edge_ai_defect::runtime::PipelineMetadataV3>(
                  edge_ai_defect::runtime::PipelineMetadataV3{
                      config.pipeline.queue_capacity, config.pipeline.drop_policy})
            : std::nullopt};

    std::vector<std::unique_ptr<edge_ai_defect::runtime::IResultSink>> sinks;
    sinks.push_back(std::make_unique<SinkForwarder>(timed_json_sink));
    sinks.push_back(std::make_unique<SinkForwarder>(hash_sink));
    std::unique_ptr<edge_ai_defect::runtime::CompositeSink> composite_sink;
    status = edge_ai_defect::runtime::CompositeSink::create(
        std::move(sinks), &composite_sink);
    if (!status.ok()) {
        std::cerr << "sink composition: " << status.message() << '\n';
        return 3;
    }
    edge_ai_defect::runtime::RunSummary summary;
    const edge_ai_defect::application::RunResult run_result =
        edge_ai_defect::application::run_with_components(
            config, *source, *composite_sink, metadata, preprocessor,
            contract.input.tensor_info, *engine, postprocessor, &summary,
            edge_ai_defect::application::RunOptions{std::nullopt, &trace_recorder});
    status = run_result.status;
    std::ofstream trace_output(arguments.trace);
    if (!trace_output) {
        std::cerr << "trace: cannot open output " << arguments.trace << '\n';
        return 4;
    }
    const Status trace_status = trace_recorder.flush(trace_output);
    if (!status.ok()) {
        std::cerr << "experiment run: " << status.message() << '\n';
        return 4;
    }
    if (!trace_status.ok()) {
        std::cerr << "trace: " << trace_status.message() << '\n';
        return 4;
    }

    status = write_hashes(arguments.hashes, arguments.run_id, hash_sink);
    if (!status.ok()) {
        std::cerr << status.message() << '\n';
        return 4;
    }
    fs::path executable;
    status = executable_path(&executable);
    if (!status.ok()) {
        std::cerr << status.message() << '\n';
        return 4;
    }
    std::string config_sha256, executable_sha256, engine_sha256, manifest_sha256;
    std::string contract_sha256, corpus_manifest_sha256;
    const std::array<std::pair<const fs::path*, const char*>, 6> files = {{
        {&arguments.config, "config"}, {&executable, "executable"},
        {&config.tensorrt.engine_path, "engine"},
        {&config.tensorrt.engine_manifest_path, "manifest"},
        {&config.model_contract_path, "contract"},
        {&arguments.corpus_manifest, "corpus manifest"}}};
    std::array<std::string*, 6> hashes = {{
        &config_sha256, &executable_sha256, &engine_sha256,
        &manifest_sha256, &contract_sha256, &corpus_manifest_sha256}};
    for (std::size_t index = 0; index < files.size(); ++index) {
        status = hash_named_file(*files[index].first, files[index].second, hashes[index]);
        if (!status.ok()) {
            std::cerr << status.message() << '\n';
            return 4;
        }
    }
    status = write_sidecar(arguments.sidecar, arguments, config_sha256, executable_sha256,
                           engine_sha256, manifest_sha256, contract_sha256,
                           corpus_manifest_sha256, config);
    if (!status.ok()) {
        std::cerr << status.message() << '\n';
        return 4;
    }
    std::cout << "run_id=" << arguments.run_id << '\n'
              << "runtime_mode=" << config.runtime_mode << '\n'
              << "processed_images=" << summary.processed_images << '\n'
              << "run_sha256=" << hash_sink.run_hash() << '\n';
    for (const auto& [cycle, hash] : hash_sink.cycle_hashes()) {
        std::cout << "cycle[" << cycle << "]_sha256=" << hash << '\n';
    }
    return 0;
}
