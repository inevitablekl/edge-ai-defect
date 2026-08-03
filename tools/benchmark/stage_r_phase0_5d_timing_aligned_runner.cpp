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
#include "stage_r/pageable_runner.hpp"
#include "stage_r/pinned_runner.hpp"

#include <openssl/evp.h>

#include <chrono>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#include <opencv2/core.hpp>

#include <time.h>

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

constexpr std::string_view kPreflightEvidenceClass = "NOT_FORMAL_PERFORMANCE_EVIDENCE";
constexpr std::string_view kFormalEvidenceClass = "FORMAL_PERFORMANCE_EVIDENCE";
constexpr std::string_view kRemediationId =
    "opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1";

struct Arguments {
    fs::path config;
    fs::path manifest;
    fs::path output_dir;
    std::size_t warmup_frames = 0;
    std::size_t measured_frames = 0;
    std::string execution_mode;
};

void usage() {
    std::cout << "Usage: stage_r_phase0_5d_timing_aligned_runner"
                 " --config PATH --manifest PATH --output-dir PATH"
                 " --warmup-frames N --measured-frames N"
                 " --execution-mode PREFLIGHT_ONLY|FORMAL_AUTHORITY\n";
}

Status parse_size(std::string_view value, const char* name, std::size_t* output) {
    try {
        std::size_t used = 0;
        const auto parsed = std::stoull(std::string(value), &used);
        if (used != value.size() || parsed == 0U) throw std::invalid_argument("invalid");
        *output = static_cast<std::size_t>(parsed);
        return Status::success();
    } catch (...) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               std::string(name) + " must be positive");
    }
}

Status parse_args(int argc, char** argv, Arguments* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "null arguments");
    Arguments args;
    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];
        if (option == "--help" || option == "-h") {
            usage();
            return Status::failure(ErrorCode::kInvalidArgument, "help");
        }
        if (index + 1 >= argc) {
            return Status::failure(ErrorCode::kInvalidArgument, "missing value for " + option);
        }
        const std::string value = argv[++index];
        if (option == "--config") args.config = value;
        else if (option == "--manifest") args.manifest = value;
        else if (option == "--output-dir") args.output_dir = value;
        else if (option == "--execution-mode") args.execution_mode = value;
        else if (option == "--warmup-frames") {
            const Status status = parse_size(value, "warmup-frames", &args.warmup_frames);
            if (!status.ok()) return status;
        } else if (option == "--measured-frames") {
            const Status status = parse_size(value, "measured-frames", &args.measured_frames);
            if (!status.ok()) return status;
        } else {
            return Status::failure(ErrorCode::kInvalidArgument, "unknown option " + option);
        }
    }
    const bool valid_mode = args.execution_mode == "PREFLIGHT_ONLY" ||
                            args.execution_mode == "FORMAL_AUTHORITY";
    const bool preflight_limits_ok = args.execution_mode != "PREFLIGHT_ONLY" ||
                                     (args.warmup_frames <= 3U && args.measured_frames <= 16U);
    if (args.config.empty() || args.manifest.empty() || args.output_dir.empty() ||
        !valid_mode || !preflight_limits_ok) {
        return Status::failure(
            ErrorCode::kInvalidArgument,
            "requires config, manifest, output-dir, execution-mode PREFLIGHT_ONLY or "
            "FORMAL_AUTHORITY; PREFLIGHT_ONLY requires warmup <= 3 and measured <= 16");
    }
    *output = std::move(args);
    return Status::success();
}

std::string json_escape(std::string_view value) {
    std::ostringstream output;
    for (const unsigned char character : value) {
        switch (character) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default: output << static_cast<char>(character); break;
        }
    }
    return output.str();
}

Status sha256_file(const fs::path& path, std::string* output) {
    if (output == nullptr) return Status::failure(ErrorCode::kInvalidArgument, "null digest output");
    std::ifstream input(path, std::ios::binary);
    if (!input) return Status::failure(ErrorCode::kIoError, "cannot read " + path.string());
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    if (context == nullptr || EVP_DigestInit_ex(context, EVP_sha256(), nullptr) != 1) {
        if (context != nullptr) EVP_MD_CTX_free(context);
        return Status::failure(ErrorCode::kIoError, "SHA-256 initialization failed");
    }
    char buffer[64 * 1024];
    while (input.good()) {
        input.read(buffer, sizeof(buffer));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context, buffer, static_cast<std::size_t>(count)) != 1) {
            EVP_MD_CTX_free(context);
            return Status::failure(ErrorCode::kIoError, "SHA-256 update failed");
        }
    }
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0;
    const bool ok = input.eof() && EVP_DigestFinal_ex(context, digest, &length) == 1;
    EVP_MD_CTX_free(context);
    if (!ok) return Status::failure(ErrorCode::kIoError, "SHA-256 read/finalize failed");
    std::ostringstream hex;
    hex << std::hex << std::setfill('0');
    for (unsigned int index = 0; index < length; ++index) hex << std::setw(2) << static_cast<unsigned int>(digest[index]);
    *output = hex.str();
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

std::string binary_path(char* argv0) {
    std::error_code error;
    const fs::path resolved = fs::read_symlink("/proc/self/exe", error);
    if (!error && !resolved.empty()) return resolved;
    return fs::absolute(argv0, error).lexically_normal();
}

std::uint64_t process_cpu_ns() {
    timespec value{};
    if (::clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &value) != 0) return 0U;
    return static_cast<std::uint64_t>(value.tv_sec) * 1000000000ULL +
           static_cast<std::uint64_t>(value.tv_nsec);
}

std::uint64_t steady_ns(const Clock::time_point& value) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(value.time_since_epoch()).count());
}

std::string utc_now() {
    const auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::tm tm{};
    gmtime_r(&now, &tm);
    std::ostringstream output;
    output << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return output.str();
}

Status write_text(const fs::path& path, const std::string& text) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write " + path.string());
    output << text;
    return output ? Status::success() : Status::failure(ErrorCode::kIoError, "write failed: " + path.string());
}

class TimingSource final : public ImageSource {
public:
    explicit TimingSource(ImageSource& inner) : inner_(inner) {}

    Status next(std::optional<ImageItem>* output) override {
        const Clock::time_point start = Clock::now();
        const Status status = inner_.next(output);
        if (!status.ok() || output == nullptr || !output->has_value()) return status;
        const std::size_t sequence = (*output)->sequence_index;
        if (sequence >= starts_.size()) starts_.resize(sequence + 1U);
        starts_[sequence] = start;
        return status;
    }

    std::optional<double> elapsed_ms(std::size_t sequence) const {
        if (sequence >= starts_.size() || starts_[sequence] == Clock::time_point{}) return std::nullopt;
        return std::chrono::duration<double, std::milli>(Clock::now() - starts_[sequence]).count();
    }

private:
    ImageSource& inner_;
    std::vector<Clock::time_point> starts_;
};

class FanoutSink final : public IResultSink {
public:
    FanoutSink(edge_ai_defect::runtime::JsonSink& json,
               edge_ai_defect::runtime::CanonicalHashSink& hash,
               TimingSource* source)
        : json_(json), hash_(hash), source_(source) {}

    Status begin_run(const RunMetadata& metadata) override {
        begin_ = Clock::now();
        const Status json_status = json_.begin_run(metadata);
        if (!json_status.ok()) return json_status;
        return hash_.begin_run(metadata);
    }

    Status write_frame(const FrameResult& frame) override {
        if (frame.timings.has_value()) {
            internal_timing_seen_ = true;
            return Status::failure(ErrorCode::kSchemaViolation,
                                   "timing-aligned harness received an internal timing object");
        }
        if (source_ != nullptr) {
            const auto elapsed = source_->elapsed_ms(frame.sequence_index);
            if (!elapsed.has_value() || !std::isfinite(*elapsed) || *elapsed < 0.0) {
                return Status::failure(ErrorCode::kInvalidArgument,
                                       "external latency boundary sample is invalid");
            }
            latency_ms_.push_back(*elapsed);
        }
        const Status json_status = json_.write_frame(frame);
        if (!json_status.ok()) return json_status;
        return hash_.write_frame(frame);
    }

    Status end_run(const RunSummary& summary) override {
        RunSummary adjusted = summary;
        if (!adjusted.runtime_v3.has_value()) {
            adjusted.runtime_v3 = edge_ai_defect::runtime::RunSummaryV3{};
            adjusted.runtime_v3->source_frames = adjusted.processed_images;
            adjusted.runtime_v3->run_processing_wall_ms =
                std::chrono::duration<double, std::milli>(Clock::now() - begin_).count();
        }
        return end_run_with_summary(adjusted);
    }

    Status end_run_with_wall(const RunSummary& summary, double wall_ms) {
        RunSummary adjusted = summary;
        if (!adjusted.runtime_v3.has_value()) {
            adjusted.runtime_v3 = edge_ai_defect::runtime::RunSummaryV3{};
            adjusted.runtime_v3->source_frames = adjusted.processed_images;
            adjusted.runtime_v3->run_processing_wall_ms = wall_ms;
        } else {
            adjusted.runtime_v3->run_processing_wall_ms = wall_ms;
        }
        return end_run_with_summary(adjusted);
    }

    const std::vector<double>& latency_ms() const noexcept { return latency_ms_; }
    bool internal_timing_seen() const noexcept { return internal_timing_seen_; }
    const std::string& detection_sha() const noexcept { return hash_.run_hash(); }

private:
    Status end_run_with_summary(const RunSummary& summary) {
        const Status json_status = json_.end_run(summary);
        if (!json_status.ok()) return json_status;
        return hash_.end_run(summary);
    }

    edge_ai_defect::runtime::JsonSink& json_;
    edge_ai_defect::runtime::CanonicalHashSink& hash_;
    TimingSource* source_ = nullptr;
    std::vector<double> latency_ms_;
    bool internal_timing_seen_ = false;
    Clock::time_point begin_ = Clock::now();
};

RunMetadata make_metadata(const edge_ai_defect::runtime::RuntimeConfig& config,
                          const edge_ai_defect::model::ModelContract& contract,
                          const edge_ai_defect::model::TensorRtEngineManifest& manifest) {
    RunMetadata metadata;
    metadata.schema_version = 4U;
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
        "serial", config.input_type, std::nullopt};
    metadata.precision_v4 = edge_ai_defect::runtime::PrecisionMetadataV4{
        manifest.precision_mode, manifest.int8_enabled, manifest.fp16_fallback_enabled,
        manifest.host_io_dtype, edge_ai_defect::runtime::CalibrationMetadataV4{
            "IInt8EntropyCalibrator2", "train", 1260U,
            manifest.calibration_manifest_sha256, manifest.calibration_cache_sha256,
            manifest.cache_metadata_sha256}};
    return metadata;
}

Status run_selected(const edge_ai_defect::runtime::RuntimeConfig& config,
                    ImageSource& source,
                    edge_ai_defect::preprocess::Preprocessor& preprocessor,
                    const edge_ai_defect::model::ModelContract& contract,
                    edge_ai_defect::inference::IInferenceEngine& inference,
                    edge_ai_defect::postprocess::PostProcessor& postprocessor,
                    IResultSink& sink,
                    const RunMetadata& metadata,
                    RunSummary* summary) {
    if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV0) {
        edge_ai_defect::runtime::SerialRunner runner(
            source, preprocessor, contract.input.tensor_info, inference, postprocessor, sink);
        return runner.run(metadata, summary);
    }
    auto* tensorrt = dynamic_cast<edge_ai_defect::backend_tensorrt::TensorRtEngine*>(&inference);
    if (tensorrt == nullptr) {
        return Status::failure(ErrorCode::kBackendRuntimeError, "TensorRT capability unavailable");
    }
    if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV2R) {
        edge_ai_defect::stage_r::PageableRunner runner(
            source, *tensorrt, postprocessor, sink,
            edge_ai_defect::stage_r::ResizeSemantic::kOpenCv454AlignedFixedContract);
        return runner.run(metadata, summary);
    }
    if (config.data_path_variant == edge_ai_defect::runtime::DataPathVariant::kV3R) {
        edge_ai_defect::stage_r::PinnedRunner runner(
            source, *tensorrt, postprocessor, sink,
            edge_ai_defect::stage_r::ResizeSemantic::kOpenCv454AlignedFixedContract);
        return runner.run(metadata, summary);
    }
    return Status::failure(ErrorCode::kSchemaViolation,
                           "only V0, V2R, and V3R are accepted by this harness");
}

Status write_failure(const fs::path& output_dir, std::string_view phase,
                     std::string_view evidence_class, const Status& status) {
    std::ostringstream text;
    text << "{\n  \"evidence_class\": \"" << evidence_class << "\",\n"
         << "  \"status\": \"IMPLEMENTATION_FAILURE\",\n"
         << "  \"phase\": \"" << json_escape(phase) << "\",\n"
         << "  \"message\": \"" << json_escape(status.message()) << "\"\n}\n";
    return write_text(output_dir / "failure.json", text.str());
}

}  // namespace

int main(int argc, char** argv) {
    Arguments args;
    const Status arg_status = parse_args(argc, argv, &args);
    if (!arg_status.ok()) {
        if (arg_status.message() == "help") return 0;
        std::cerr << arg_status.message() << '\n';
        usage();
        return 2;
    }

    const std::string_view evidence_class = args.execution_mode == "FORMAL_AUTHORITY"
        ? kFormalEvidenceClass : kPreflightEvidenceClass;

    std::error_code error;
    const fs::path output_dir = fs::absolute(args.output_dir, error).lexically_normal();
    if (error || output_dir.empty() || fs::exists(output_dir)) {
        std::cerr << "output directory must be new and resolvable: " << output_dir << '\n';
        return 2;
    }
    if (!fs::is_directory(output_dir.parent_path())) {
        std::cerr << "output parent directory is missing: " << output_dir.parent_path() << '\n';
        return 2;
    }
    fs::create_directory(output_dir, error);
    if (error) {
        std::cerr << "cannot create output directory: " << error.message() << '\n';
        return 2;
    }
    auto fail = [&](std::string_view phase, const Status& status, int code) {
        std::cerr << phase << ": " << status.message() << '\n';
        (void)write_failure(output_dir, phase, evidence_class, status);
        return code;
    };

    edge_ai_defect::runtime::RuntimeConfig config;
    Status status = edge_ai_defect::runtime::RuntimeConfigLoader::load(args.config, &config);
    if (!status.ok()) return fail("config", status, 3);
    if (config.schema_version != 6U || config.backend_type != "tensorrt_int8" ||
        config.runtime_mode != "serial" || config.timing_enabled ||
        config.profiling_mode != edge_ai_defect::runtime::ProfilingMode::kOff ||
        config.phase0_5d.warmup_frames != 60U || config.phase0_5d.measured_frames != 1080U ||
        config.phase0_5d.input_size != 640U || config.phase0_5d.batch != 1U ||
        config.phase0_5d.opencv_threads != config.opencv_num_threads ||
        config.phase0_5d.execution_mode != "FORMAL_AUTHORITY") {
        return fail("config", Status::failure(ErrorCode::kSchemaViolation,
            "timing-aligned config contract is not frozen v1"), 3);
    }
    if (args.execution_mode == "FORMAL_AUTHORITY" &&
        (args.warmup_frames != config.phase0_5d.warmup_frames ||
         args.measured_frames != config.phase0_5d.measured_frames)) {
        return fail("config", Status::failure(ErrorCode::kSchemaViolation,
            "formal execution counts must match phase0_5d warmup/measured config"), 3);
    }
    const auto variant = config.data_path_variant;
    if (variant != edge_ai_defect::runtime::DataPathVariant::kV0 &&
        variant != edge_ai_defect::runtime::DataPathVariant::kV2R &&
        variant != edge_ai_defect::runtime::DataPathVariant::kV3R) {
        return fail("dispatch", Status::failure(ErrorCode::kSchemaViolation,
            "only V0, V2R, and V3R are accepted"), 3);
    }
    cv::setNumThreads(static_cast<int>(config.opencv_num_threads));

    edge_ai_defect::model::ModelContract contract;
    status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
    if (!status.ok()) return fail("model_contract", status, 3);
    edge_ai_defect::model::TensorRtEngineManifest manifest;
    status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
        config.tensorrt.engine_manifest_path, &contract, &manifest);
    if (!status.ok()) return fail("engine_manifest", status, 3);
    std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> inference;
    status = edge_ai_defect::inference::create_inference_engine(config, contract, &inference);
    if (!status.ok()) return fail("engine", status, 4);

    std::string config_sha, manifest_sha, contract_sha, corpus_sha, engine_sha, binary_sha;
    for (const auto& item : {std::pair<const fs::path*, std::string*>(&args.config, &config_sha),
                             std::pair<const fs::path*, std::string*>(&config.tensorrt.engine_manifest_path, &manifest_sha),
                             std::pair<const fs::path*, std::string*>(&config.model_contract_path, &contract_sha),
                             std::pair<const fs::path*, std::string*>(&args.manifest, &corpus_sha),
                             std::pair<const fs::path*, std::string*>(&config.tensorrt.engine_path, &engine_sha)}) {
        status = sha256_file(*item.first, item.second);
        if (!status.ok()) return fail("identity", status, 3);
    }
    const fs::path executable = binary_path(argv[0]);
    status = sha256_file(executable, &binary_sha);
    if (!status.ok()) return fail("identity", status, 3);

    const RunMetadata metadata = make_metadata(config, contract, manifest);
    edge_ai_defect::preprocess::Preprocessor preprocessor;
    edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);

    // Warmup deliberately uses the same source/runner/result serialization and
    // canonical digest path. Its result is retained but never aggregated.
    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> warmup_source;
    status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, args.manifest, 1U, &warmup_source, args.warmup_frames);
    if (!status.ok()) return fail("warmup_source", status, 4);
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> warmup_json;
    status = edge_ai_defect::runtime::JsonSink::create(
        output_dir / "warmup_result.json", false, &warmup_json);
    if (!status.ok()) return fail("warmup_sink", status, 4);
    edge_ai_defect::runtime::CanonicalHashSink warmup_hash;
    FanoutSink warmup_sink(*warmup_json, warmup_hash, nullptr);
    RunSummary warmup_summary;
    status = run_selected(config, *warmup_source, preprocessor, contract, *inference,
                          postprocessor, warmup_sink, metadata, &warmup_summary);
    if (!status.ok() || warmup_summary.processed_images != args.warmup_frames ||
        warmup_sink.internal_timing_seen()) {
        if (status.ok()) status = Status::failure(ErrorCode::kInvalidArgument, "warmup count or timing mismatch");
        return fail("warmup", status, 4);
    }

    std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource> measured_base;
    status = edge_ai_defect::runtime::CorpusReplaySource::create(
        config.input_directory, args.manifest, 1U, &measured_base, args.measured_frames);
    if (!status.ok()) return fail("measured_source", status, 4);
    TimingSource measured_source(*measured_base);
    std::unique_ptr<edge_ai_defect::runtime::JsonSink> result_json;
    status = edge_ai_defect::runtime::JsonSink::create(
        output_dir / "result.json", false, &result_json);
    if (!status.ok()) return fail("result_sink", status, 4);
    edge_ai_defect::runtime::CanonicalHashSink result_hash;
    FanoutSink sink(*result_json, result_hash, &measured_source);
    RunSummary summary;
    const Clock::time_point wall_start = Clock::now();
    const std::uint64_t cpu_start = process_cpu_ns();
    const std::string wall_start_utc = utc_now();
    status = run_selected(config, measured_source, preprocessor, contract, *inference,
                          postprocessor, sink, metadata, &summary);
    const Clock::time_point wall_end = Clock::now();
    const std::uint64_t cpu_end = process_cpu_ns();
    const std::string wall_end_utc = utc_now();
    const double wall_ms = std::chrono::duration<double, std::milli>(wall_end - wall_start).count();
    if (!status.ok()) return fail("measured", status, 5);
    if (summary.processed_images != args.measured_frames || sink.latency_ms().size() != args.measured_frames ||
        sink.internal_timing_seen() || !std::isfinite(wall_ms) || wall_ms <= 0.0) {
        return fail("measured", Status::failure(ErrorCode::kInvalidArgument,
            "processed count, external latency samples, timing policy, or wall interval invalid"), 5);
    }
    // The JSON summary is finalized by FanoutSink through the shared sink. The
    // explicit process-wall markers below are the harness timing authority.
    const fs::path result_path = output_dir / "result.json";
    const fs::path warmup_path = output_dir / "warmup_result.json";
    std::string result_sha, warmup_sha;
    status = sha256_file(result_path, &result_sha);
    if (!status.ok()) return fail("result_identity", status, 6);
    status = sha256_file(warmup_path, &warmup_sha);
    if (!status.ok()) return fail("warmup_identity", status, 6);

    std::ostringstream metrics;
    metrics << std::setprecision(17)
            << "{\n  \"schema_version\": 1,\n  \"evidence_class\": \"" << evidence_class
            << "\",\n  \"execution_mode\": \"" << args.execution_mode
            << "\",\n  \"variant\": \""
            << edge_ai_defect::runtime::data_path_variant_name(variant)
            << "\",\n  \"measured_frames\": " << args.measured_frames
            << ",\n  \"processed_frames\": " << summary.processed_images
            << ",\n  \"drop_count\": 0,\n  \"eos\": true,\n  \"latency_ms\": [";
    for (std::size_t index = 0; index < sink.latency_ms().size(); ++index) {
        if (index != 0) metrics << ", ";
        metrics << sink.latency_ms()[index];
    }
    const double cpu_ms = cpu_end >= cpu_start
        ? static_cast<double>(cpu_end - cpu_start) / 1.0e6 : -1.0;
    const double cpu_cores = cpu_ms >= 0.0 && wall_ms > 0.0 ? cpu_ms / wall_ms : -1.0;
    metrics << "],\n  \"process_wall_start_steady_ns\": " << steady_ns(wall_start)
            << ",\n  \"process_wall_end_steady_ns\": " << steady_ns(wall_end)
            << ",\n  \"process_wall_ms\": " << wall_ms
            << ",\n  \"process_cpu_ms\": " << cpu_ms
            << ",\n  \"cpu_equivalent_cores\": " << cpu_cores << "\n}\n";
    status = write_text(output_dir / "metrics.json", metrics.str());
    if (!status.ok()) return fail("metrics", status, 6);

    std::ostringstream hashes;
    hashes << "{\n  \"schema_version\": 1,\n  \"evidence_class\": \"" << evidence_class
           << "\",\n  \"execution_mode\": \"" << args.execution_mode
           << "\",\n  \"variant\": \""
           << edge_ai_defect::runtime::data_path_variant_name(variant)
           << "\",\n  \"detection_sha256\": \"" << sink.detection_sha()
           << "\",\n  \"tensor_digest_sha256\": null,\n  \"frames\": "
           << args.measured_frames << "\n}\n";
    status = write_text(output_dir / "hashes.json", hashes.str());
    if (!status.ok()) return fail("hashes", status, 6);

    std::ostringstream run_manifest;
    run_manifest << "{\n  \"schema_version\": 1,\n  \"evidence_class\": \"" << evidence_class
                 << "\",\n  \"execution_mode\": \"" << args.execution_mode
                 << "\",\n  \"variant\": \""
                 << edge_ai_defect::runtime::data_path_variant_name(variant)
                 << "\",\n  \"commit\": \"" << current_commit()
                 << "\",\n  \"binary_sha256\": \"" << binary_sha
                 << "\",\n  \"harness_source\": \"tools/benchmark/stage_r_phase0_5d_timing_aligned_runner.cpp\",\n"
                 << "  \"config_sha256\": \"" << config_sha
                 << "\",\n  \"engine_sha256\": \"" << engine_sha
                 << "\",\n  \"engine_manifest_sha256\": \"" << manifest_sha
                 << "\",\n  \"model_contract_sha256\": \"" << contract_sha
                 << "\",\n  \"test_manifest_sha256\": \"" << corpus_sha
                 << "\",\n  \"result_json_sha256\": \"" << result_sha
                 << "\",\n  \"warmup_result_sha256\": \"" << warmup_sha
                 << "\",\n  \"timing_enabled_config\": false,\n  \"timing_enabled_metadata\": false,\n"
                 << "  \"profiling_mode\": \"off\",\n  \"internal_timing_fields\": false,\n"
                 << "  \"timing_boundary_id\": \"" << config.phase0_5d.timing_boundary_id
                 << "\",\n  \"timing_boundary_start\": \"before TimingSource::inner.next\",\n"
                 << "  \"timing_boundary_end\": \"FanoutSink::write_frame before JsonSink::write_frame\",\n"
                 << "  \"timing_boundary_excludes\": [\"JSON serialization\", \"file write\", \"digest finalization\", \"summary persistence\"],\n"
                 << "  \"sink_id\": \"" << config.phase0_5d.sink_id
                 << "\",\n  \"serialization_id\": \"" << config.phase0_5d.serialization_id
                 << "\",\n  \"digest_id\": \"" << config.phase0_5d.digest_id
                 << "\",\n  \"remediation_id\": \""
                 << (variant == edge_ai_defect::runtime::DataPathVariant::kV0
                         ? "not_applicable_v0_cpu_opencv_host_tensor"
                         : std::string(kRemediationId))
                 << "\",\n  \"warmup_frames\": " << args.warmup_frames
                 << ",\n  \"measured_frames\": " << args.measured_frames
                 << ",\n  \"processed_frames\": " << summary.processed_images
                 << ",\n  \"drop_count\": 0,\n  \"eos\": true,\n  \"worker_join\": true,\n"
                 << "  \"schema_version_result\": 4,\n  \"per_frame_timing_field\": false,\n"
                 << "  \"result_field_contract\": \"shared_result_json_v4_no_internal_timing_v1\",\n"
                 << "  \"process_wall_start_utc\": \"" << wall_start_utc
                 << "\",\n  \"process_wall_end_utc\": \"" << wall_end_utc
                 << "\",\n  \"process_wall_start_steady_ns\": " << steady_ns(wall_start)
                 << ",\n  \"process_wall_end_steady_ns\": " << steady_ns(wall_end)
                 << ",\n  \"cpu_measurement\": \"CLOCK_PROCESS_CPUTIME_ID over measured process window\"\n}\n";
    status = write_text(output_dir / "run_manifest.json", run_manifest.str());
    if (!status.ok()) return fail("run_manifest", status, 6);

    std::cout << args.execution_mode << " PASS variant="
              << edge_ai_defect::runtime::data_path_variant_name(variant)
              << " frames=" << args.measured_frames
              << " detection_sha256=" << sink.detection_sha() << '\n';
    return 0;
}
