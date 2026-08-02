#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "backend_tensorrt/pinned_raw_staging.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "stage_r/pinned_runner.hpp"

#include <openssl/evp.h>

#include <cuda_runtime_api.h>
#include <opencv2/core.hpp>
#include <yaml-cpp/yaml.h>

#include <filesystem>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

namespace {
namespace fs = std::filesystem;
using edge_ai_defect::core::ErrorCode;
using edge_ai_defect::core::Status;
using edge_ai_defect::runtime::FrameResult;
using edge_ai_defect::runtime::RunMetadata;
using edge_ai_defect::runtime::RunSummary;

struct Arguments {
    fs::path config;
    fs::path manifest;
    fs::path result;
    fs::path hashes;
    fs::path run_manifest;
};

void usage() {
    std::cout << "Usage: stage_r_v3_task_harness --config PATH --manifest PATH "
                 "--result-json PATH --hashes PATH --run-manifest PATH\n";
}

Status parse_args(int argc, char** argv, Arguments* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "output is null");
    Arguments args;
    for (int i = 1; i < argc; ++i) {
        const std::string option = argv[i];
        if (option == "--help" || option == "-h") {
            usage();
            return Status::failure(ErrorCode::kInvalidArgument, "help");
        }
        if (i + 1 >= argc) return Status::failure(ErrorCode::kInvalidArgument, "missing value for " + option);
        const fs::path value = argv[++i];
        if (option == "--config") args.config = value;
        else if (option == "--manifest") args.manifest = value;
        else if (option == "--result-json") args.result = value;
        else if (option == "--hashes") args.hashes = value;
        else if (option == "--run-manifest") args.run_manifest = value;
        else return Status::failure(ErrorCode::kInvalidArgument, "unknown option " + option);
    }
    if (args.config.empty() || args.manifest.empty() || args.result.empty() ||
        args.hashes.empty() || args.run_manifest.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument, "all arguments are required");
    }
    *output = std::move(args);
    return Status::success();
}

std::string sha256_bytes(const void* data, std::size_t size) {
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        return {};
    }
    EVP_DigestUpdate(context, data, size);
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0;
    const bool ok = EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) return {};
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < length; ++i) output << std::setw(2) << static_cast<unsigned int>(digest[i]);
    return output.str();
}

class Sha256Accumulator final {
public:
    Sha256Accumulator() : context_(EVP_MD_CTX_new()) {
        if (context_ != nullptr) EVP_DigestInit_ex(context_, EVP_sha256(), nullptr);
    }
    ~Sha256Accumulator() { if (context_ != nullptr) EVP_MD_CTX_free(context_); }
    bool update(const void* data, std::size_t size) {
        return context_ != nullptr && EVP_DigestUpdate(context_, data, size) == 1;
    }
    std::string finish() {
        if (context_ == nullptr) return {};
        unsigned char digest[EVP_MAX_MD_SIZE] = {};
        unsigned int length = 0;
        if (EVP_DigestFinal_ex(context_, digest, &length) != 1) return {};
        std::ostringstream output;
        output << std::hex << std::setfill('0');
        for (unsigned int i = 0; i < length; ++i) output << std::setw(2) << static_cast<unsigned int>(digest[i]);
        context_ = nullptr;
        return output.str();
    }
private:
    EVP_MD_CTX* context_ = nullptr;
};

Status write_text(const fs::path& path, const std::string& value) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write " + path.string());
    output << value;
    return output ? Status::success() : Status::failure(ErrorCode::kIoError, "write failed " + path.string());
}

std::string current_commit() {
    FILE* pipe = ::popen("git rev-parse HEAD 2>/dev/null", "r");
    if (pipe == nullptr) return "unavailable";
    char buffer[128] = {};
    const std::size_t count = std::fread(buffer, 1, sizeof(buffer) - 1, pipe);
    ::pclose(pipe);
    std::string result(buffer, count);
    while (!result.empty() && (result.back() == '\n' || result.back() == '\r')) result.pop_back();
    return result;
}

RunMetadata make_metadata(const edge_ai_defect::runtime::RuntimeConfig& config,
                          const edge_ai_defect::model::ModelContract& contract,
                          const edge_ai_defect::model::TensorRtEngineManifest& manifest) {
    RunMetadata metadata;
    metadata.schema_version = 4;
    metadata.backend_type = config.backend_type;
    metadata.model_filename = config.tensorrt.engine_path.filename().string();
    metadata.model_sha256 = manifest.engine_sha256;
    metadata.contract_filename = config.model_contract_path.filename().string();
    metadata.artifact_kind = "tensorrt_engine";
    metadata.source_onnx_sha256 = manifest.source_onnx_sha256;
    metadata.engine_manifest_filename = config.tensorrt.engine_manifest_path.filename().string();
    metadata.class_names = contract.class_names;
    metadata.postprocess_config = config.postprocess_config;
    metadata.timing_enabled = false;
    metadata.runtime_v3 = edge_ai_defect::runtime::RuntimeMetadataV3{
        config.runtime_mode, config.input_type,
        edge_ai_defect::runtime::PipelineMetadataV3{
            config.pipeline.queue_capacity, config.pipeline.drop_policy}};
    metadata.precision_v4 = edge_ai_defect::runtime::PrecisionMetadataV4{
        manifest.precision_mode, manifest.int8_enabled, manifest.fp16_fallback_enabled,
        manifest.host_io_dtype, edge_ai_defect::runtime::CalibrationMetadataV4{
            "IInt8EntropyCalibrator2", "train", 1260U,
            manifest.calibration_manifest_sha256, manifest.calibration_cache_sha256,
            manifest.cache_metadata_sha256}};
    return metadata;
}

Status sha256_file(const fs::path& path, std::string* output) {
    std::ifstream input(path, std::ios::binary);
    if (!input || output == nullptr) return Status::failure(ErrorCode::kIoError, "cannot read " + path.string());
    Sha256Accumulator accumulator;
    char buffer[64 * 1024];
    while (input.good()) {
        input.read(buffer, sizeof(buffer));
        const std::streamsize count = input.gcount();
        if (count > 0 && !accumulator.update(buffer, static_cast<std::size_t>(count)))
            return Status::failure(ErrorCode::kIoError, "SHA update failed");
    }
    if (!input.eof()) return Status::failure(ErrorCode::kIoError, "SHA read failed");
    *output = accumulator.finish();
    return output->empty() ? Status::failure(ErrorCode::kIoError, "SHA finalize failed") : Status::success();
}

}  // namespace

int main(int argc, char** argv) {
    Arguments args;
    Status status = parse_args(argc, argv, &args);
    if (!status.ok()) {
        if (status.message() == "help") return 0;
        std::cerr << status.message() << '\n';
        usage();
        return 2;
    }

    edge_ai_defect::runtime::RuntimeConfig config;
    status = edge_ai_defect::runtime::RuntimeConfigLoader::load(args.config, &config);
    if (!status.ok()) { std::cerr << "config: " << status.message() << '\n'; return 3; }
    if (config.data_path_variant != edge_ai_defect::runtime::DataPathVariant::kV3 ||
        config.backend_type != "tensorrt_int8" || config.schema_version != 6U ||
        config.profiling_mode != edge_ai_defect::runtime::ProfilingMode::kOff) {
        std::cerr << "harness requires RuntimeConfig v6 V3 TensorRT INT8 profiling off\n";
        return 3;
    }
    for (const fs::path& path : {args.result, args.hashes, args.run_manifest}) {
        if (!path.parent_path().empty() && !fs::is_directory(path.parent_path())) {
            std::cerr << "output parent missing: " << path.parent_path() << '\n'; return 3;
        }
        if (fs::exists(path)) { std::cerr << "output already exists: " << path << '\n'; return 3; }
    }
    cv::setNumThreads(static_cast<int>(config.opencv_num_threads));

    edge_ai_defect::model::ModelContract contract;
    status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) { std::cerr << "contract: " << status.message() << '\n'; return 3; }
    edge_ai_defect::model::TensorRtEngineManifest engine_manifest;
    status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, &engine_manifest);
    if (!status.ok()) { std::cerr << "engine manifest: " << status.message() << '\n'; return 3; }
    std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> inference;
    status = edge_ai_defect::inference::create_inference_engine(config, contract, &inference);
    if (!status.ok()) { std::cerr << "engine: " << status.message() << '\n'; return 3; }
    auto* engine = dynamic_cast<edge_ai_defect::backend_tensorrt::TensorRtEngine*>(inference.get());
    if (engine == nullptr) { std::cerr << "TensorRT capability unavailable\n"; return 3; }

    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> source;
    status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, args.manifest, 1U, &source);
    if (!status.ok()) { std::cerr << "manifest source: " << status.message() << '\n'; return 3; }
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> json_sink;
    status = edge_ai_defect::runtime::JsonSink::create(args.result, false, &json_sink);
    if (!status.ok()) { std::cerr << "JSON sink: " << status.message() << '\n'; return 3; }
    edge_ai_defect::runtime::CanonicalHashSink detection_hash;
    class Sink final : public edge_ai_defect::runtime::IResultSink {
    public:
        Sink(edge_ai_defect::runtime::JsonSink& json, edge_ai_defect::runtime::CanonicalHashSink& hash)
            : json_(json), hash_(hash) {}
        Status begin_run(const RunMetadata& m) override { auto s = json_.begin_run(m); if (!s.ok()) return s; return hash_.begin_run(m); }
        Status write_frame(const FrameResult& f) override { auto s = json_.write_frame(f); if (!s.ok()) return s; return hash_.write_frame(f); }
        Status end_run(const RunSummary& s) override { auto first = json_.end_run(s); if (!first.ok()) return first; return hash_.end_run(s); }
    private:
        edge_ai_defect::runtime::JsonSink& json_;
        edge_ai_defect::runtime::CanonicalHashSink& hash_;
    } sink(*json_sink, detection_hash);

    const RunMetadata metadata = make_metadata(config, contract, engine_manifest);
    status = sink.begin_run(metadata);
    if (!status.ok()) { std::cerr << "sink begin: " << status.message() << '\n'; return 4; }
    std::unique_ptr<edge_ai_defect::stage_r::CudaPreprocessor> preprocessor;
    status = edge_ai_defect::stage_r::CudaPreprocessor::create_for_external_tensor(
        4096, 4096, static_cast<std::size_t>(4096) * 3U,
        reinterpret_cast<cudaStream_t>(engine->cuda_stream_handle()),
        static_cast<float*>(engine->device_input_buffer()), &preprocessor);
    if (!status.ok()) { std::cerr << "V3 preprocessor: " << status.message() << '\n'; return 4; }
    // The pinned buffer is allocated once before the frame loop and released
    // at shutdown; no per-frame cudaHostAlloc/cudaFreeHost occurs.
    edge_ai_defect::stage_r::PinnedRawStaging staging;
    status = staging.allocate(4096U * 4096U * 3U);
    if (!status.ok()) { std::cerr << "pinned staging: " << status.message() << '\n'; return 4; }
    edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
    std::vector<float> tensor(edge_ai_defect::stage_r::CudaPreprocessor::kTargetElementCount);
    Sha256Accumulator tensor_digest;
    std::size_t frames = 0;
    std::vector<std::string> paths;
    std::vector<std::pair<int, int>> dimensions;
    const auto run_start = std::chrono::steady_clock::now();
    for (;;) {
        std::optional<edge_ai_defect::runtime::ImageItem> item;
        status = source->next(&item);
        if (!status.ok()) { std::cerr << "source: " << status.message() << '\n'; return 4; }
        if (!item.has_value()) break;
        const cv::Mat& image = item->image_bgr;
        status = staging.prepare(image);
        if (!status.ok()) { std::cerr << "staging: " << status.message() << '\n'; return 4; }
        edge_ai_defect::preprocess::ImageTransformMetadata geometry;
        status = edge_ai_defect::stage_r::CudaPreprocessor::compute_geometry(
            staging.width(), staging.height(), &geometry);
        if (!status.ok()) { std::cerr << "geometry: " << status.message() << '\n'; return 4; }
        status = preprocessor->preprocess(staging.data(), staging.width(), staging.height(),
                                          staging.packed_row_bytes(), geometry);
        if (!status.ok()) { std::cerr << "CUDA preprocess: " << status.message() << '\n'; return 4; }
        status = preprocessor->copy_output_to_host(tensor.data(), tensor.size());
        if (!status.ok() || !tensor_digest.update(tensor.data(), tensor.size() * sizeof(float))) {
            std::cerr << "tensor digest copy failed\n"; return 4;
        }
        edge_ai_defect::core::HostTensor output;
        status = engine->run_device_input(engine->device_input_buffer(), engine->device_input_bytes(), &output);
        if (!status.ok()) { std::cerr << "TensorRT V3 input: " << status.message() << '\n'; return 4; }
        std::vector<edge_ai_defect::postprocess::Detection> detections;
        status = postprocessor.process(output, geometry, &detections);
        if (!status.ok()) { std::cerr << "postprocess: " << status.message() << '\n'; return 4; }
        FrameResult frame;
        frame.sequence_index = item->sequence_index;
        frame.relative_path = item->relative_path;
        frame.image_width = image.cols;
        frame.image_height = image.rows;
        frame.detections = std::move(detections);
        status = sink.write_frame(frame);
        if (!status.ok()) { std::cerr << "sink frame: " << status.message() << '\n'; return 4; }
        paths.push_back(frame.relative_path.generic_string());
        dimensions.emplace_back(frame.image_width, frame.image_height);
        ++frames;
    }
    RunSummary summary;
    summary.processed_images = frames;
    for (const FrameResult& frame : detection_hash.frames()) summary.total_detections += frame.detections.size();
    summary.runtime_v3 = edge_ai_defect::runtime::RunSummaryV3{};
    summary.runtime_v3->source_frames = frames;
    summary.runtime_v3->run_processing_wall_ms =
        std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - run_start).count();
    summary.runtime_v3->pipeline = edge_ai_defect::runtime::PipelineSummaryV3{{0, 0, 0}};
    status = sink.end_run(summary);
    if (!status.ok()) { std::cerr << "sink end: " << status.message() << '\n'; return 4; }
    if (frames != 180U || detection_hash.cycle_hashes().size() != 1U || paths.size() != 180U) {
        std::cerr << "frame contract failed\n"; return 5;
    }
    const std::string tensor_sha = tensor_digest.finish();
    const std::string binary = fs::read_symlink("/proc/self/exe").string();
    std::string binary_sha, config_sha, engine_sha, manifest_sha, result_sha;
    for (const auto& pair : std::vector<std::pair<fs::path, std::string*>>{{binary, &binary_sha}, {args.config, &config_sha}, {config.tensorrt.engine_path, &engine_sha}, {args.manifest, &manifest_sha}, {args.result, &result_sha}}) {
        status = sha256_file(pair.first, pair.second);
        if (!status.ok()) { std::cerr << status.message() << '\n'; return 5; }
    }
    std::ostringstream hashes;
    hashes << "{\n  \"schema_version\": 1,\n  \"variant\": \"V3\",\n  \"detection_sha256\": \"" << detection_hash.cycle_hashes().begin()->second
           << "\",\n  \"tensor_digest_sha256\": \"" << tensor_sha << "\",\n  \"frames\": " << frames << "\n}\n";
    status = write_text(args.hashes, hashes.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 5; }
    std::ostringstream manifest;
    manifest << "{\n  \"schema_version\": 1,\n  \"stage\": \"R\",\n  \"phase\": \"R2.3\",\n  \"variant\": \"V3\",\n  \"commit\": \"" << current_commit()
             << "\",\n  \"binary_sha256\": \"" << binary_sha << "\",\n  \"config_sha256\": \"" << config_sha
             << "\",\n  \"engine_sha256\": \"" << engine_sha << "\",\n  \"test_manifest_sha256\": \"" << manifest_sha
             << "\",\n  \"result_json_sha256\": \"" << result_sha << "\",\n  \"processed_frames\": 180,\n  \"drop_count\": 0,\n  \"eos\": true,\n  \"worker_join\": true,\n  \"worker_model\": \"single-threaded validation harness; join is vacuous\",\n  \"runtime_path\": \"pinned raw staging -> CUDA preprocessing -> TensorRtDeviceInputCapability -> TensorRT INT8 -> existing postprocess\",\n  \"cpu_preprocessing_fallback\": false\n}\n";
    status = write_text(args.run_manifest, manifest.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 5; }
    std::cout << "V3 task harness PASS\nframes=180\ndetection_sha256=" << detection_hash.cycle_hashes().begin()->second
              << "\ntensor_digest_sha256=" << tensor_sha << '\n';
    return 0;
}
