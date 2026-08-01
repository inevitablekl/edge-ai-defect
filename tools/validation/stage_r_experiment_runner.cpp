#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <openssl/evp.h>
#include <cuda_profiler_api.h>
#include <opencv2/core.hpp>
#include <nvToolsExt.h>

#include <chrono>
#include <cstdio>
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
using edge_ai_defect::runtime::FrameResult;
using edge_ai_defect::runtime::RunMetadata;
using edge_ai_defect::runtime::RunSummary;

struct Arguments {
    fs::path config, corpus_manifest, result_json, run_manifest, hashes, profiling_output;
    std::string run_id;
    std::size_t warmup_frames = 0, measured_frames = 0;
};

class Forwarder final : public edge_ai_defect::runtime::IResultSink {
public:
    explicit Forwarder(edge_ai_defect::runtime::IResultSink& inner) : inner_(inner) {}
    Status begin_run(const RunMetadata& m) override { return inner_.begin_run(m); }
    Status write_frame(const FrameResult& f) override { return inner_.write_frame(f); }
    Status end_run(const RunSummary& s) override { return inner_.end_run(s); }
private:
    edge_ai_defect::runtime::IResultSink& inner_;
};

class CountingSink final : public edge_ai_defect::runtime::IResultSink {
public:
    Status begin_run(const RunMetadata&) override { return Status::success(); }
    Status write_frame(const FrameResult& f) override { ++frames_; last_sequence_ = f.sequence_index; return Status::success(); }
    Status end_run(const RunSummary&) override { return Status::success(); }
    std::size_t frames() const noexcept { return frames_; }
    std::size_t last_sequence() const noexcept { return last_sequence_; }
private:
    std::size_t frames_ = 0, last_sequence_ = 0;
};

class MetricsSink final : public edge_ai_defect::runtime::IResultSink {
public:
    explicit MetricsSink(edge_ai_defect::runtime::IResultSink& inner) : inner_(inner) {}
    Status begin_run(const RunMetadata& m) override { return inner_.begin_run(m); }
    Status write_frame(const FrameResult& f) override {
        ++frames_; paths_.push_back(f.relative_path.generic_string());
        if (f.timings) pre_sink_ms_ += f.timings->pre_sink_total_ms;
        return inner_.write_frame(f);
    }
    Status end_run(const RunSummary& s) override { return inner_.end_run(s); }
    std::size_t frames() const noexcept { return frames_; }
    double mean_pre_sink_ms() const noexcept { return frames_ == 0 ? 0.0 : pre_sink_ms_ / frames_; }
private:
    edge_ai_defect::runtime::IResultSink& inner_;
    std::size_t frames_ = 0;
    double pre_sink_ms_ = 0.0;
    std::vector<std::string> paths_;
};

void usage() {
    std::cout << "Usage: stage_r_experiment_runner --config PATH --corpus-manifest PATH "
                 "--run-id ID --warmup-frames N --measured-frames N "
                 "--result-json PATH --run-manifest PATH --hashes PATH "
                 "--profiling-output PATH\n";
}

Status positive_size(std::string_view value, const char* name, std::size_t* output) {
    try {
        std::size_t used = 0;
        const auto parsed = std::stoull(std::string(value), &used);
        if (used != value.size() || parsed == 0) throw std::invalid_argument("invalid");
        *output = static_cast<std::size_t>(parsed);
        return Status::success();
    } catch (...) {
        return Status::failure(ErrorCode::kInvalidArgument, std::string(name) + " must be positive");
    }
}

Status parse_args(int argc, char** argv, Arguments* output) {
    Arguments a;
    for (int i = 1; i < argc; ++i) {
        const std::string option = argv[i];
        if (option == "--help" || option == "-h") { usage(); return Status::failure(ErrorCode::kInvalidArgument, "help"); }
        if (i + 1 >= argc) return Status::failure(ErrorCode::kInvalidArgument, "missing value for " + option);
        const std::string value = argv[++i];
        if (option == "--config") a.config = value;
        else if (option == "--corpus-manifest") a.corpus_manifest = value;
        else if (option == "--run-id") a.run_id = value;
        else if (option == "--warmup-frames") { auto s = positive_size(value, "warmup-frames", &a.warmup_frames); if (!s.ok()) return s; }
        else if (option == "--measured-frames") { auto s = positive_size(value, "measured-frames", &a.measured_frames); if (!s.ok()) return s; }
        else if (option == "--result-json") a.result_json = value;
        else if (option == "--run-manifest") a.run_manifest = value;
        else if (option == "--hashes") a.hashes = value;
        else if (option == "--profiling-output") a.profiling_output = value;
        else return Status::failure(ErrorCode::kInvalidArgument, "unknown option " + option);
    }
    if (a.config.empty() || a.corpus_manifest.empty() || a.run_id.empty() ||
        a.warmup_frames == 0 || a.measured_frames == 0 || a.measured_frames % 180 != 0 ||
        a.result_json.empty() || a.run_manifest.empty() || a.hashes.empty() ||
        a.profiling_output.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "all R1 arguments are required and measured-frames must be a multiple of 180");
    }
    *output = std::move(a);
    return Status::success();
}

std::string escape_json(const std::string& value) {
    std::string result;
    for (char c : value) { if (c == '\\' || c == '"') result += '\\'; result += c; }
    return result;
}

Status sha256_file(const fs::path& path, std::string* output) {
    std::ifstream input(path, std::ios::binary);
    if (!input || output == nullptr) return Status::failure(ErrorCode::kIoError, "cannot read " + path.string());
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1)
        return Status::failure(ErrorCode::kIoError, "SHA-256 initialization failed");
    char buffer[64 * 1024];
    while (input.good()) { input.read(buffer, sizeof(buffer)); const auto n = input.gcount(); if (n > 0) EVP_DigestUpdate(context, buffer, static_cast<std::size_t>(n)); }
    unsigned char digest[EVP_MAX_MD_SIZE]; unsigned int length = 0;
    const bool ok = input.eof() && EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) return Status::failure(ErrorCode::kIoError, "SHA-256 read/finalize failed");
    std::ostringstream hex;
    for (unsigned int i = 0; i < length; ++i) { hex << std::hex; hex.width(2); hex.fill('0'); hex << static_cast<unsigned int>(digest[i]); }
    *output = hex.str();
    return Status::success();
}

Status publish(const fs::path& path, const std::string& contents) {
    const fs::path temporary = path.string() + ".tmp.r1";
    { std::ofstream output(temporary, std::ios::binary | std::ios::trunc); if (!output) return Status::failure(ErrorCode::kIoError, "cannot open temporary output"); output << contents; if (!output) return Status::failure(ErrorCode::kIoError, "cannot write temporary output"); }
    std::error_code error;
    fs::rename(temporary, path, error);
    if (error) { fs::remove(temporary); return Status::failure(ErrorCode::kIoError, "atomic publish failed: " + error.message()); }
    return Status::success();
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

Status check_outputs(const Arguments& a) {
    const fs::path paths[] = {a.result_json, a.run_manifest, a.hashes, a.profiling_output};
    for (std::size_t i = 0; i < 4; ++i) {
        if (!paths[i].parent_path().empty() && !fs::is_directory(paths[i].parent_path()))
            return Status::failure(ErrorCode::kIoError, "output parent is missing: " + paths[i].parent_path().string());
        if (fs::exists(paths[i])) return Status::failure(ErrorCode::kIoError, "output already exists: " + paths[i].string());
        for (std::size_t j = 0; j < i; ++j) if (paths[i] == paths[j])
            return Status::failure(ErrorCode::kInvalidArgument, "output paths must be distinct");
    }
    return Status::success();
}

RunMetadata make_metadata(const edge_ai_defect::runtime::RuntimeConfig& config,
                          const edge_ai_defect::model::ModelContract& contract,
                          const edge_ai_defect::model::TensorRtEngineManifest& manifest,
                          bool timing) {
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
    metadata.timing_enabled = timing;
    metadata.runtime_v3 = edge_ai_defect::runtime::RuntimeMetadataV3{
        config.runtime_mode, config.input_type,
        edge_ai_defect::runtime::PipelineMetadataV3{config.pipeline.queue_capacity, config.pipeline.drop_policy}};
    metadata.precision_v4 = edge_ai_defect::runtime::PrecisionMetadataV4{
        manifest.precision_mode, manifest.int8_enabled, manifest.fp16_fallback_enabled,
        manifest.host_io_dtype, edge_ai_defect::runtime::CalibrationMetadataV4{
            "IInt8EntropyCalibrator2", "train", 1260U, manifest.calibration_manifest_sha256,
            manifest.calibration_cache_sha256, manifest.cache_metadata_sha256}};
    return metadata;
}

Status make_source(const edge_ai_defect::runtime::RuntimeConfig& config, const fs::path& manifest,
                   std::size_t cycles, std::size_t max_frames,
                   std::unique_ptr<edge_ai_defect::runtime::ImageSource>* output) {
    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> source;
    const Status status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, manifest, cycles, &source, max_frames);
    if (!status.ok()) return status;
    *output = std::move(source);
    return Status::success();
}

Status run_phase(const edge_ai_defect::runtime::RuntimeConfig& config,
                 edge_ai_defect::runtime::ImageSource& source,
                 edge_ai_defect::preprocess::Preprocessor& preprocessor,
                 const edge_ai_defect::core::TensorInfo& input_info,
                 edge_ai_defect::inference::IInferenceEngine& engine,
                 edge_ai_defect::postprocess::PostProcessor& postprocessor,
                 edge_ai_defect::runtime::IResultSink& sink,
                 const RunMetadata& metadata, RunSummary* summary) {
    const auto result = edge_ai_defect::application::run_with_components(
        config, source, sink, metadata, preprocessor, input_info, engine, postprocessor, summary);
    return result.status;
}

std::string profiling_report(const Arguments& a,
                             const edge_ai_defect::runtime::RuntimeConfig& config,
                             const edge_ai_defect::backend_tensorrt::TensorRtEngine& engine,
                             const MetricsSink& metrics, std::size_t measured, double wall_ms) {
    const auto& samples = engine.diagnostic_samples();
    std::ostringstream out;
    out << "{\n  \"schema_version\": 1,\n  \"run_id\": \"" << escape_json(a.run_id)
        << "\",\n  \"profiling_mode\": \"" << edge_ai_defect::runtime::profiling_mode_name(config.profiling_mode)
        << "\",\n  \"measured_frames\": " << measured << ",\n  \"sample_count\": " << samples.size()
        << ",\n  \"sample_rule\": \"frame_in_cycle % 10 == cycle_index % 10\",\n  \"throughput_fps\": "
        << (wall_ms > 0.0 ? measured / (wall_ms / 1000.0) : 0.0)
        << ",\n  \"mean_pre_sink_latency_ms\": " << metrics.mean_pre_sink_ms() << ",\n  \"samples\": [\n";
    for (std::size_t i = 0; i < samples.size(); ++i) {
        const auto& s = samples[i];
        if (i != 0) out << ",\n";
        out << "    {\"measured_frame\": " << s.measured_frame << ", \"cycle_index\": " << s.cycle_index
            << ", \"frame_in_cycle\": " << s.frame_in_cycle << ", \"h2d_ms\": " << s.h2d_ms
            << ", \"tensorrt_ms\": " << s.tensorrt_ms << ", \"d2h_ms\": " << s.d2h_ms
            << ", \"host_output_construction_ms\": " << s.host_output_construction_ms
            << ", \"host_roundtrip_ms\": " << s.host_roundtrip_ms << "}";
    }
    out << "\n  ]\n}\n";
    return out.str();
}

}  // namespace

int main(int argc, char** argv) {
    Arguments a;
    Status status = parse_args(argc, argv, &a);
    if (!status.ok()) { if (status.message() == "help") return 0; std::cerr << status.message() << '\n'; usage(); return 2; }
    status = check_outputs(a);
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 2; }

    edge_ai_defect::runtime::RuntimeConfig config;
    status = edge_ai_defect::runtime::RuntimeConfigLoader::load(a.config, &config);
    if (!status.ok()) { std::cerr << "config: " << status.message() << '\n'; return 3; }
    if ((config.schema_version != 5U && config.schema_version != 6U) ||
        config.backend_type != "tensorrt_int8" || config.runtime_mode != "pipeline" ||
        config.pipeline.queue_capacity != 1U || config.pipeline.drop_policy != "block" ||
        config.data_path_variant != edge_ai_defect::runtime::DataPathVariant::kV0 ||
        config.profiling_mode == edge_ai_defect::runtime::ProfilingMode::kFormal) {
        std::cerr << "R1 runner requires v5/v6 TensorRT INT8 pipeline V0 and profiling off/diagnostic\n";
        return 3;
    }
    config.output_json_path = a.result_json;
    config.output_overwrite = false;
    cv::setNumThreads(static_cast<int>(config.opencv_num_threads));

    edge_ai_defect::model::ModelContract contract;
    status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) { std::cerr << "contract: " << status.message() << '\n'; return 3; }
    auto manifest = std::make_unique<edge_ai_defect::model::TensorRtEngineManifest>();
    status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, manifest.get());
    if (!status.ok()) { std::cerr << "engine manifest: " << status.message() << '\n'; return 3; }
    std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> inference_engine;
    status = edge_ai_defect::inference::create_inference_engine(config, contract, &inference_engine);
    if (!status.ok()) { std::cerr << "engine: " << status.message() << '\n'; return 3; }
    auto* trt = dynamic_cast<edge_ai_defect::backend_tensorrt::TensorRtEngine*>(inference_engine.get());
    if (trt == nullptr) { std::cerr << "R1 runner requires TensorRtEngine\n"; return 3; }

    edge_ai_defect::preprocess::Preprocessor preprocessor;
    edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
    const RunMetadata warmup_metadata = make_metadata(config, contract, *manifest, false);
    std::unique_ptr<edge_ai_defect::runtime::ImageSource> warmup_source;
    status = make_source(config, a.corpus_manifest, 1, a.warmup_frames, &warmup_source);
    if (!status.ok()) { std::cerr << "warmup source: " << status.message() << '\n'; return 3; }
    CountingSink warmup_sink;
    RunSummary warmup_summary;
    status = run_phase(config, *warmup_source, preprocessor, contract.input.tensor_info,
                       *inference_engine, postprocessor, warmup_sink, warmup_metadata, &warmup_summary);
    if (!status.ok() || warmup_sink.frames() != a.warmup_frames ||
        warmup_summary.processed_images != a.warmup_frames) {
        std::cerr << "warmup failed or count mismatch: " << status.message() << '\n'; return 4;
    }
    // PipelineRunner returns after normal EOS, queue drain, four worker joins, and
    // TensorRtEngine::run's two V0 stream synchronizations.
    if (config.profiling_mode == edge_ai_defect::runtime::ProfilingMode::kDiagnostic)
        status = trt->set_diagnostic_profiling(true);
    else
        status = trt->set_diagnostic_profiling(false);
    if (!status.ok()) { std::cerr << "profiling setup: " << status.message() << '\n'; return 4; }

    std::unique_ptr<edge_ai_defect::runtime::ImageSource> measured_source;
    status = make_source(config, a.corpus_manifest, a.measured_frames / 180U, 0, &measured_source);
    if (!status.ok()) { std::cerr << "measured source: " << status.message() << '\n'; return 4; }
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> json_sink;
    status = edge_ai_defect::runtime::JsonSink::create(a.result_json, false, &json_sink);
    if (!status.ok()) { std::cerr << "JSON sink: " << status.message() << '\n'; return 4; }
    edge_ai_defect::runtime::CanonicalHashSink hash_sink;
    std::vector<std::unique_ptr<edge_ai_defect::runtime::IResultSink>> children;
    children.push_back(std::make_unique<Forwarder>(*json_sink));
    children.push_back(std::make_unique<Forwarder>(hash_sink));
    std::unique_ptr<edge_ai_defect::runtime::CompositeSink> composite;
    status = edge_ai_defect::runtime::CompositeSink::create(std::move(children), &composite);
    if (!status.ok()) { std::cerr << "sink: " << status.message() << '\n'; return 4; }
    MetricsSink metrics(*composite);
    const RunMetadata measured_metadata = make_metadata(config, contract, *manifest, true);
    nvtxMarkA("stage_r.measured_phase_start");
    const cudaError_t profiler_start_status = cudaProfilerStart();
    if (profiler_start_status != cudaSuccess) {
        std::cerr << "cudaProfilerStart failed: " << static_cast<int>(profiler_start_status) << '\n';
        return 4;
    }
    nvtxRangePushA("stage_r.measured");
    const auto measured_start = std::chrono::steady_clock::now();
    RunSummary measured_summary;
    status = run_phase(config, *measured_source, preprocessor, contract.input.tensor_info,
                       *inference_engine, postprocessor, metrics, measured_metadata, &measured_summary);
    const auto measured_end = std::chrono::steady_clock::now();
    const cudaError_t profiler_stop_status = cudaProfilerStop();
    nvtxMarkA("stage_r.measured_phase_end");
    nvtxRangePop();
    if (profiler_stop_status != cudaSuccess) {
        std::cerr << "cudaProfilerStop failed: " << static_cast<int>(profiler_stop_status) << '\n';
        return 4;
    }
    if (!status.ok() || metrics.frames() != a.measured_frames ||
        measured_summary.processed_images != a.measured_frames ||
        hash_sink.cycle_hashes().size() != a.measured_frames / 180U) {
        std::cerr << "measured failed or count/cycle mismatch: " << status.message() << '\n'; return 4;
    }
    if (config.profiling_mode == edge_ai_defect::runtime::ProfilingMode::kDiagnostic &&
        trt->diagnostic_samples().size() != 180U) {
        std::cerr << "diagnostic sample count is not 180\n"; return 4;
    }
    const double wall_ms = std::chrono::duration<double, std::milli>(measured_end - measured_start).count();
    const auto epoch_now = std::chrono::system_clock::now().time_since_epoch();
    const auto epoch_end_ms = std::chrono::duration_cast<std::chrono::milliseconds>(epoch_now).count();
    const auto epoch_start_ms = epoch_end_ms -
        static_cast<long long>(wall_ms);

    std::ostringstream hash_text;
    hash_text << "{\n  \"schema_version\": 1,\n  \"run_id\": \"" << escape_json(a.run_id)
              << "\",\n  \"run_sha256\": \"" << hash_sink.run_hash() << "\",\n  \"cycle_sha256\": [\n";
    bool first = true;
    for (const auto& [cycle, hash] : hash_sink.cycle_hashes()) {
        if (!first) hash_text << ",\n"; first = false;
        hash_text << "    {\"cycle_id\": " << cycle << ", \"sha256\": \"" << hash << "\"}";
    }
    hash_text << "\n  ]\n}\n";
    status = publish(a.hashes, hash_text.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 4; }
    status = publish(a.profiling_output, profiling_report(a, config, *trt, metrics, a.measured_frames, wall_ms));
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 4; }

    fs::path binary = fs::read_symlink("/proc/self/exe");
    const fs::path files[] = {binary, a.config, config.tensorrt.engine_path,
        config.tensorrt.engine_manifest_path, config.model_contract_path, a.corpus_manifest,
        a.result_json, a.hashes, a.profiling_output};
    std::string file_hashes[9];
    for (std::size_t i = 0; i < 9; ++i) {
        status = sha256_file(files[i], &file_hashes[i]);
        if (!status.ok()) { std::cerr << status.message() << '\n'; return 4; }
    }
    std::ostringstream run_manifest;
    run_manifest << "{\n  \"schema_version\": 1,\n  \"run_id\": \"" << escape_json(a.run_id)
        << "\",\n  \"stage\": \"R\",\n  \"phase\": \"R1\",\n  \"variant\": \"V0\",\n  \"process_type\": \""
        << (a.measured_frames == 180 && config.schema_version == 5U ? "baseline_v5" :
            (a.measured_frames == 180 && config.schema_version == 6U ? "baseline_v6" :
             (config.profiling_mode == edge_ai_defect::runtime::ProfilingMode::kOff ? "profiling_off" : "profiling_diagnostic")))
        << "\",\n  \"profiling_mode\": \"" << edge_ai_defect::runtime::profiling_mode_name(config.profiling_mode)
        << "\",\n  \"commit\": \"" << current_commit()
        << "\",\n  \"binary_path\": \"" << escape_json(binary.string()) << "\",\n  \"binary_sha256\": \"" << file_hashes[0]
        << "\",\n  \"config_path\": \"" << escape_json(a.config.string()) << "\",\n  \"config_sha256\": \"" << file_hashes[1]
        << "\",\n  \"engine_path\": \"" << escape_json(config.tensorrt.engine_path.string()) << "\",\n  \"engine_sha256\": \"" << file_hashes[2]
        << "\",\n  \"engine_manifest_path\": \"" << escape_json(config.tensorrt.engine_manifest_path.string()) << "\",\n  \"engine_manifest_sha256\": \"" << file_hashes[3]
        << "\",\n  \"model_contract_path\": \"" << escape_json(config.model_contract_path.string()) << "\",\n  \"model_contract_sha256\": \"" << file_hashes[4]
        << "\",\n  \"test_manifest_path\": \"" << escape_json(a.corpus_manifest.string()) << "\",\n  \"test_manifest_sha256\": \"" << file_hashes[5]
        << "\",\n  \"warmup_frames\": " << a.warmup_frames << ",\n  \"measured_frames\": " << a.measured_frames
        << ",\n  \"complete_cycles\": " << a.measured_frames / 180U
        << ",\n  \"drop_count\": 0,\n  \"phase_barrier\": {\n    \"warmup_submitted_frames\": " << a.warmup_frames
        << ",\n    \"warmup_sink_frames\": " << warmup_sink.frames()
        << ",\n    \"warmup_last_sequence\": " << warmup_sink.last_sequence()
        << ",\n    \"warmup_workers_joined\": true,\n    \"warmup_queues_drained\": true,\n    \"warmup_cuda_idle\": true,\n    \"cuda_idle_authority\": \"per_frame_synchronous_tensorrt_run_contract\"\n  },\n  \"result_json_path\": \"" << escape_json(a.result_json.string())
        << "\",\n  \"result_json_sha256\": \"" << file_hashes[6] << "\",\n  \"hash_output_path\": \"" << escape_json(a.hashes.string())
        << "\",\n  \"hash_output_sha256\": \"" << file_hashes[7] << "\",\n  \"profiling_output_path\": \"" << escape_json(a.profiling_output.string())
        << "\",\n  \"profiling_output_sha256\": \"" << file_hashes[8]
        << "\",\n  \"environment\": {\"platform\": \"Jetson Orin Nano Super\", \"nvpmodel\": \"MAXN_SUPER\", \"nvpmodel_mode\": 2, \"cpu_affinity\": \"0-5\", \"opencv_threads\": 1, \"jetson_clocks\": \"not_invoked\", \"fan\": \"automatic\"},\n  \"start_time_epoch_ms\": " << epoch_start_ms
        << ",\n  \"end_time_epoch_ms\": " << epoch_end_ms
        << ",\n  \"raw_evidence_retention\": \"tracked summaries only; no raw Nsight in this runner\",\n  \"exit_status\": \"PASS\"\n}\n";
    status = publish(a.run_manifest, run_manifest.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 4; }
    std::cout << "run_id=" << a.run_id << "\nmeasured_frames=" << metrics.frames()
              << "\nrun_sha256=" << hash_sink.run_hash()
              << "\nsamples=" << trt->diagnostic_samples().size() << '\n';
    return 0;
}
