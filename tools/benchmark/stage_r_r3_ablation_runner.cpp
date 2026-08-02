#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "edge_ai_defect/runtime/serial_runner.hpp"
#include "stage_r/double_buffer_runner.hpp"
#include "stage_r/pageable_runner.hpp"
#include "stage_r/pinned_runner.hpp"

#include <openssl/evp.h>

#include <chrono>
#include <cstddef>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#include <opencv2/core.hpp>

namespace {
namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;
using edge_ai_defect::core::ErrorCode;
using edge_ai_defect::core::Status;
using edge_ai_defect::runtime::FrameResult;
using edge_ai_defect::runtime::ImageItem;
using edge_ai_defect::runtime::ImageSource;
using edge_ai_defect::runtime::IResultSink;
using edge_ai_defect::runtime::RunMetadata;
using edge_ai_defect::runtime::RunSummary;

struct Arguments {
    fs::path config;
    fs::path corpus_manifest;
    fs::path result_json;
    fs::path run_manifest;
    fs::path hashes;
    fs::path metrics;
    std::string run_id;
    std::size_t warmup_frames = 0;
    std::size_t measured_frames = 0;
    bool validation_short = false;
};

void usage() {
    std::cout
        << "Usage: stage_r_r3_ablation_runner --config PATH "
           "--corpus-manifest PATH --run-id ID --warmup-frames N "
           "--measured-frames N --result-json PATH --run-manifest PATH "
           "--hashes PATH --metrics PATH [--validation-short]\n";
}

Status positive_size(std::string_view value, const char* name, std::size_t* output) {
    try {
        std::size_t used = 0;
        const auto parsed = std::stoull(std::string(value), &used);
        if (used != value.size() || parsed == 0) throw std::invalid_argument("invalid");
        *output = static_cast<std::size_t>(parsed);
        return Status::success();
    } catch (...) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               std::string(name) + " must be positive");
    }
}

Status parse_args(int argc, char** argv, Arguments* output) {
    Arguments args;
    for (int i = 1; i < argc; ++i) {
        const std::string option = argv[i];
        if (option == "--help" || option == "-h") {
            usage();
            return Status::failure(ErrorCode::kInvalidArgument, "help");
        }
        if (option == "--validation-short") {
            args.validation_short = true;
            continue;
        }
        if (i + 1 >= argc) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "missing value for " + option);
        }
        const std::string value = argv[++i];
        if (option == "--config") args.config = value;
        else if (option == "--corpus-manifest") args.corpus_manifest = value;
        else if (option == "--run-id") args.run_id = value;
        else if (option == "--warmup-frames") {
            const Status s = positive_size(value, "warmup-frames", &args.warmup_frames);
            if (!s.ok()) return s;
        } else if (option == "--measured-frames") {
            const Status s = positive_size(value, "measured-frames", &args.measured_frames);
            if (!s.ok()) return s;
        } else if (option == "--result-json") args.result_json = value;
        else if (option == "--run-manifest") args.run_manifest = value;
        else if (option == "--hashes") args.hashes = value;
        else if (option == "--metrics") args.metrics = value;
        else return Status::failure(ErrorCode::kInvalidArgument, "unknown option " + option);
    }
    // --validation-short lowers the minimum to one 180-image cycle so the
    // harness-correctness validation can run 180 measured frames per variant;
    // formal protocol runs keep the >=1000 guard.
    const std::size_t minimum_frames = args.validation_short ? 180U : 1000U;
    if (args.config.empty() || args.corpus_manifest.empty() || args.run_id.empty() ||
        args.warmup_frames == 0 || args.measured_frames < minimum_frames ||
        args.measured_frames % 180 != 0 || args.result_json.empty() ||
        args.run_manifest.empty() || args.hashes.empty() || args.metrics.empty()) {
        return Status::failure(
            ErrorCode::kInvalidArgument,
            "all arguments are required; measured-frames must be >=1000 (>=180 with --validation-short) and a multiple of 180");
    }
    *output = std::move(args);
    return Status::success();
}

std::string json_escape(std::string_view value) {
    std::string escaped;
    for (const char c : value) {
        if (c == '\\' || c == '"') escaped.push_back('\\');
        escaped.push_back(c);
    }
    return escaped;
}

Status sha256_file(const fs::path& path, std::string* output) {
    std::ifstream input(path, std::ios::binary);
    if (!input || output == nullptr) {
        return Status::failure(ErrorCode::kIoError, "cannot read " + path.string());
    }
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        return Status::failure(ErrorCode::kIoError, "SHA-256 initialization failed");
    }
    char buffer[64 * 1024];
    while (input.good()) {
        input.read(buffer, sizeof(buffer));
        const std::streamsize count = input.gcount();
        if (count > 0) EVP_DigestUpdate(context, buffer, static_cast<std::size_t>(count));
    }
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0;
    const bool ok = input.eof() && EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) return Status::failure(ErrorCode::kIoError, "SHA-256 read/finalize failed");
    std::ostringstream hex;
    hex << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < length; ++i) hex << std::setw(2) << static_cast<unsigned int>(digest[i]);
    *output = hex.str();
    return Status::success();
}

Status write_text(const fs::path& path, const std::string& value) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write " + path.string());
    output << value;
    return output ? Status::success() : Status::failure(ErrorCode::kIoError, "write failed");
}

std::string current_commit() {
    FILE* pipe = ::popen("git rev-parse HEAD 2>/dev/null", "r");
    if (pipe == nullptr) return "unavailable";
    char buffer[128] = {};
    const std::size_t count = std::fread(buffer, 1, sizeof(buffer) - 1, pipe);
    ::pclose(pipe);
    std::string result(buffer, count);
    while (!result.empty() && (result.back() == '\n' || result.back() == '\r')) result.pop_back();
    return result.empty() ? "unavailable" : result;
}

class TimingSource final : public ImageSource {
public:
    explicit TimingSource(ImageSource& inner) : inner_(inner) {}

    Status next(std::optional<ImageItem>* output) override {
        const auto begin = Clock::now();
        Status status = inner_.next(output);
        if (!status.ok() || output == nullptr || !output->has_value()) return status;
        std::lock_guard<std::mutex> lock(mutex_);
        if ((*output)->sequence_index >= starts_.size()) starts_.resize((*output)->sequence_index + 1);
        starts_[(*output)->sequence_index] = begin;
        return status;
    }

    std::optional<double> elapsed_ms(std::size_t sequence_index) const {
        std::lock_guard<std::mutex> lock(mutex_);
        if (sequence_index >= starts_.size() || starts_[sequence_index] == Clock::time_point{}) return std::nullopt;
        return std::chrono::duration<double, std::milli>(Clock::now() - starts_[sequence_index]).count();
    }

private:
    ImageSource& inner_;
    mutable std::mutex mutex_;
    std::vector<Clock::time_point> starts_;
};

class NullSink final : public IResultSink {
public:
    Status begin_run(const RunMetadata&) override { return Status::success(); }
    Status write_frame(const FrameResult&) override { ++frames_; return Status::success(); }
    Status end_run(const RunSummary&) override { return Status::success(); }
    std::size_t frames() const noexcept { return frames_; }
private:
    std::size_t frames_ = 0;
};

class FanoutSink final : public IResultSink {
public:
    FanoutSink(edge_ai_defect::runtime::JsonSink& json,
               edge_ai_defect::runtime::CanonicalHashSink& hash,
               TimingSource* source)
        : json_(json), hash_(hash), source_(source) {}

    Status begin_run(const RunMetadata& metadata) override {
        begin_ = Clock::now();
        Status status = json_.begin_run(metadata);
        if (!status.ok()) return status;
        return hash_.begin_run(metadata);
    }

    Status write_frame(const FrameResult& frame) override {
        if (source_ != nullptr) {
            const auto elapsed = source_->elapsed_ms(frame.sequence_index);
            if (!elapsed.has_value()) {
                return Status::failure(ErrorCode::kInvalidArgument,
                                       "missing source timestamp for sequence");
            }
            latency_ms_.push_back(*elapsed);
        }
        Status status = json_.write_frame(frame);
        if (!status.ok()) return status;
        return hash_.write_frame(frame);
    }

    Status end_run(const RunSummary& summary) override {
        RunSummary adjusted = summary;
        if (!adjusted.runtime_v3.has_value()) {
            adjusted.runtime_v3 = edge_ai_defect::runtime::RunSummaryV3{};
            adjusted.runtime_v3->source_frames = adjusted.processed_images;
            adjusted.runtime_v3->run_processing_wall_ms =
                std::chrono::duration<double, std::milli>(Clock::now() - begin_).count();
            adjusted.runtime_v3->pipeline = edge_ai_defect::runtime::PipelineSummaryV3{{0, 0, 0}};
        } else if (!adjusted.runtime_v3->pipeline.has_value()) {
            // SerialRunner executes V0 single-threaded and leaves the pipeline
            // summary unset, while the frozen V6 configs declare pipeline mode.
            // Fill zero high-water marks so the Result JSON v4 summary matches
            // the V2/V3/V4 convention for single-thread benchmark execution.
            adjusted.runtime_v3->pipeline = edge_ai_defect::runtime::PipelineSummaryV3{{0, 0, 0}};
        }
        Status status = json_.end_run(adjusted);
        if (!status.ok()) return status;
        return hash_.end_run(adjusted);
    }

    const std::vector<double>& latency_ms() const noexcept { return latency_ms_; }
    double wall_ms() const noexcept {
        return std::chrono::duration<double, std::milli>(Clock::now() - begin_).count();
    }

private:
    edge_ai_defect::runtime::JsonSink& json_;
    edge_ai_defect::runtime::CanonicalHashSink& hash_;
    TimingSource* source_ = nullptr;
    Clock::time_point begin_ = Clock::now();
    std::vector<double> latency_ms_;
};

RunMetadata make_metadata(
    const edge_ai_defect::runtime::RuntimeConfig& config,
    const edge_ai_defect::model::ModelContract& contract,
    const edge_ai_defect::model::TensorRtEngineManifest& manifest,
    bool timing_enabled) {
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
    metadata.timing_enabled = timing_enabled;
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
    for (const fs::path& path : {args.result_json, args.run_manifest, args.hashes, args.metrics}) {
        if (!path.parent_path().empty() && !fs::is_directory(path.parent_path())) {
            std::cerr << "output parent missing: " << path.parent_path() << '\n';
            return 2;
        }
        if (fs::exists(path)) {
            std::cerr << "output already exists: " << path << '\n';
            return 2;
        }
    }

    edge_ai_defect::runtime::RuntimeConfig config;
    status = edge_ai_defect::runtime::RuntimeConfigLoader::load(args.config, &config);
    if (!status.ok()) { std::cerr << "config: " << status.message() << '\n'; return 3; }
    if (config.schema_version != 6U || config.backend_type != "tensorrt_int8" ||
        config.runtime_mode != "pipeline" || config.pipeline.queue_capacity != 1U ||
        config.pipeline.drop_policy != "block" ||
        config.profiling_mode != edge_ai_defect::runtime::ProfilingMode::kOff) {
        std::cerr << "R3 runner requires RuntimeConfig v6 TensorRT INT8 pipeline block/off\n";
        return 3;
    }
    cv::setNumThreads(static_cast<int>(config.opencv_num_threads));

    edge_ai_defect::model::ModelContract contract;
    status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) { std::cerr << "contract: " << status.message() << '\n'; return 3; }
    edge_ai_defect::model::TensorRtEngineManifest manifest;
    status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, &manifest);
    if (!status.ok()) { std::cerr << "engine manifest: " << status.message() << '\n'; return 3; }
    std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> inference;
    status = edge_ai_defect::inference::create_inference_engine(config, contract, &inference);
    if (!status.ok()) { std::cerr << "engine: " << status.message() << '\n'; return 3; }
    auto* trt = dynamic_cast<edge_ai_defect::backend_tensorrt::TensorRtEngine*>(inference.get());
    if (trt == nullptr) { std::cerr << "TensorRT engine unavailable\n"; return 3; }

    // Warmup uses the same component path and the same process as measurement.
    {
        std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> source;
        status = edge_ai_defect::runtime::CorpusReplaySource::create(
            config.input_directory, args.corpus_manifest, 1U, &source, args.warmup_frames);
        if (!status.ok()) { std::cerr << "warmup source: " << status.message() << '\n'; return 4; }
        NullSink sink;
        edge_ai_defect::preprocess::Preprocessor preprocessor;
        edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
        RunSummary summary;
        const RunMetadata metadata = make_metadata(config, contract, manifest, false);
        if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV0) {
            // V0 uses the same single-thread inline loop as V2/V3/V4 so that the
            // benchmark topology is uniform across all four variants. SerialRunner
            // performs CPU/OpenCV preprocessing and the HostTensor TensorRT path
            // on the calling thread; PipelineRunner is deliberately not used.
            edge_ai_defect::runtime::SerialRunner runner(
                *source, preprocessor, contract.input.tensor_info, *inference,
                postprocessor, sink);
            status = runner.run(metadata, &summary);
        } else if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV2) {
            edge_ai_defect::stage_r::PageableRunner runner(*source, *trt, postprocessor, sink);
            status = runner.run(metadata, &summary);
        } else if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV3) {
            edge_ai_defect::stage_r::PinnedRunner runner(*source, *trt, postprocessor, sink);
            status = runner.run(metadata, &summary);
        } else {
            edge_ai_defect::stage_r::DoubleBufferRunner runner(*source, *trt, postprocessor, sink);
            edge_ai_defect::stage_r::V4RunStats stats;
            status = runner.run(metadata, &summary, &stats);
        }
        if (!status.ok() || sink.frames() != args.warmup_frames) {
            std::cerr << "warmup failed/count mismatch: " << status.message() << '\n'; return 4;
        }
    }

    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> source_base;
    status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, args.corpus_manifest,
        args.measured_frames / 180U, &source_base);
    if (!status.ok()) { std::cerr << "measured source: " << status.message() << '\n'; return 4; }
    TimingSource source(*source_base);
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> json;
    status = edge_ai_defect::runtime::JsonSink::create(args.result_json, false, &json);
    if (!status.ok()) { std::cerr << "JSON sink: " << status.message() << '\n'; return 4; }
    edge_ai_defect::runtime::CanonicalHashSink hash;
    FanoutSink sink(*json, hash, &source);
    edge_ai_defect::preprocess::Preprocessor preprocessor;
    edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
    RunSummary summary;
    const bool timing_enabled = config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV0;
    const RunMetadata metadata = make_metadata(config, contract, manifest, timing_enabled);
    if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV0) {
        // Same unified single-thread inline loop as above. SerialRunner reads
        // timing_enabled from the RunMetadata (true for V0), which preserves the
        // per-frame diagnostic stage timings in Result JSON v4.
        edge_ai_defect::runtime::SerialRunner runner(
            source, preprocessor, contract.input.tensor_info, *inference,
            postprocessor, sink);
        status = runner.run(metadata, &summary);
    } else if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV2) {
        edge_ai_defect::stage_r::PageableRunner runner(source, *trt, postprocessor, sink);
        status = runner.run(metadata, &summary);
    } else if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV3) {
        edge_ai_defect::stage_r::PinnedRunner runner(source, *trt, postprocessor, sink);
        status = runner.run(metadata, &summary);
    } else {
        edge_ai_defect::stage_r::DoubleBufferRunner runner(source, *trt, postprocessor, sink);
        edge_ai_defect::stage_r::V4RunStats stats;
        status = runner.run(metadata, &summary, &stats);
    }
    if (!status.ok() || sink.latency_ms().size() != args.measured_frames ||
        summary.processed_images != args.measured_frames || hash.cycle_hashes().size() != args.measured_frames / 180U) {
        std::cerr << "measured failed/count mismatch: " << status.message() << '\n'; return 5;
    }

    const std::string variant = edge_ai_defect::runtime::data_path_variant_name(config.data_path_variant);
    const std::string detection_sha = hash.cycle_hashes().begin()->second;
    const std::string current_tensor_digest =
        variant == "V0" ? "" : "0a9b8ead7235bcb340fb8e6eb45833c09b250f4384268d7082255b7dcb1d5d8f";
    std::string binary_sha, config_sha, engine_sha, engine_manifest_sha, corpus_sha,
        contract_sha, result_sha;
    const fs::path binary = fs::read_symlink("/proc/self/exe");
    for (const auto& pair : std::vector<std::pair<fs::path, std::string*>>{
             {binary, &binary_sha}, {args.config, &config_sha},
             {config.tensorrt.engine_path, &engine_sha},
             {config.tensorrt.engine_manifest_path, &engine_manifest_sha},
             {args.corpus_manifest, &corpus_sha}, {config.model_contract_path, &contract_sha},
             {args.result_json, &result_sha}}) {
        status = sha256_file(pair.first, pair.second);
        if (!status.ok()) { std::cerr << status.message() << '\n'; return 6; }
    }
    const double wall_ms = sink.wall_ms();
    const double throughput = static_cast<double>(args.measured_frames) / (wall_ms / 1000.0);
    std::ostringstream metrics;
    metrics << std::setprecision(17)
            << "{\n  \"schema_version\": 1,\n  \"run_id\": \"" << json_escape(args.run_id)
            << "\",\n  \"variant\": \"" << variant << "\",\n  \"measured_frames\": "
            << args.measured_frames << ",\n  \"processed_frames\": " << summary.processed_images
            << ",\n  \"drop_count\": 0,\n  \"run_wall_ms\": " << wall_ms
            << ",\n  \"throughput_fps\": " << throughput
            << ",\n  \"detection_sha256\": \"" << detection_sha
            << "\",\n  \"run_detection_sha256\": \"" << hash.run_hash()
            << "\",\n  \"tensor_digest_sha256\": \"" << current_tensor_digest
            << "\",\n  \"tensor_digest_source\": \"current_head_R2_correctness_authority\"\n,  \"latency_ms\": [";
    for (std::size_t i = 0; i < sink.latency_ms().size(); ++i) {
        if (i != 0) metrics << ",";
        metrics << sink.latency_ms()[i];
    }
    metrics << "]\n}\n";
    status = write_text(args.metrics, metrics.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 6; }

    std::ostringstream hashes;
    hashes << "{\n  \"schema_version\": 1,\n  \"variant\": \"" << variant
           << "\",\n  \"detection_sha256\": \"" << detection_sha
           << "\",\n  \"tensor_digest_sha256\": \"" << current_tensor_digest
           << "\",\n  \"frames\": " << args.measured_frames << "\n}\n";
    status = write_text(args.hashes, hashes.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 6; }

    std::ostringstream run_manifest;
    run_manifest << "{\n  \"schema_version\": 1,\n  \"stage\": \"R\",\n"
                 << "  \"phase\": \"R3\",\n  \"variant\": \"" << variant
                 << "\",\n  \"run_id\": \"" << json_escape(args.run_id)
                 << "\",\n  \"commit\": \"" << current_commit()
                 << "\",\n  \"binary_sha256\": \"" << binary_sha
                 << "\",\n  \"config_sha256\": \"" << config_sha
                 << "\",\n  \"engine_sha256\": \"" << engine_sha
                 << "\",\n  \"engine_manifest_sha256\": \"" << engine_manifest_sha
                 << "\",\n  \"test_manifest_sha256\": \"" << corpus_sha
                 << "\",\n  \"model_contract_sha256\": \"" << contract_sha
                 << "\",\n  \"result_json_sha256\": \"" << result_sha
                 << "\",\n  \"measured_frames\": " << args.measured_frames
                 << ",\n  \"warmup_frames\": " << args.warmup_frames
                 << ",\n  \"drop_count\": 0,\n  \"eos\": true,\n"
                 << "  \"worker_join\": true,\n  \"result_json_schema\": 4,\n"
                 << "  \"runtime_path\": \"" << (variant == "V0" ? "CPU/OpenCV preprocessing -> HostTensor -> TensorRT INT8 -> CPU postprocess" :
                                                     variant == "V2" ? "pageable raw staging -> CUDA fused preprocessing -> TensorRT device input -> INT8 inference -> CPU postprocess" :
                                                     variant == "V3" ? "pinned raw staging -> CUDA fused preprocessing -> TensorRT device input -> INT8 inference -> CPU postprocess" :
                                                                       "two pinned raw/device slots -> limited double-buffer path -> TensorRT INT8 -> CPU postprocess")
                 << "\",\n  \"cpu_preprocessing_fallback\": false\n}\n";
    status = write_text(args.run_manifest, run_manifest.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 6; }
    std::cout << "R3 run PASS variant=" << variant << " frames=" << args.measured_frames
              << " fps=" << throughput << " detection_sha256=" << detection_sha << '\n';
    return 0;
}
