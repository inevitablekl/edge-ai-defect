#include "edge_ai_defect/runtime/portable_control.hpp"

#include <fstream>
#include <sstream>
#include <system_error>
#include <utility>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status invalid(const std::string& detail) {
    return Status::failure(ErrorCode::kInvalidArgument,
                           "portable control: " + detail);
}

Status io_error(const std::string& detail) {
    return Status::failure(ErrorCode::kIoError,
                           "portable control: " + detail);
}

std::filesystem::path normalized_path(const std::filesystem::path& path) {
    return std::filesystem::absolute(path).lexically_normal();
}

bool is_existing_file(const std::filesystem::path& path) {
    std::error_code error;
    return std::filesystem::is_regular_file(path, error) && !error;
}

bool is_existing_directory(const std::filesystem::path& path) {
    std::error_code error;
    return std::filesystem::is_directory(path, error) && !error;
}

std::string json_escape(const std::string& value) {
    std::string escaped;
    escaped.reserve(value.size());
    for (const char character : value) {
        switch (character) {
            case '"': escaped += "\\\""; break;
            case '\\': escaped += "\\\\"; break;
            case '\n': escaped += "\\n"; break;
            case '\r': escaped += "\\r"; break;
            case '\t': escaped += "\\t"; break;
            default: escaped += character; break;
        }
    }
    return escaped;
}

std::string json_path(const std::filesystem::path& path) {
    return json_escape(path.generic_string());
}

std::string compiler_name() {
#if defined(__GNUC__)
    return std::string("gcc ") + __VERSION__;
#elif defined(__clang__)
    return std::string("clang ") + __clang_version__;
#else
    return "unknown";
#endif
}

std::string architecture_name() {
#if defined(__aarch64__)
    return "aarch64";
#elif defined(__x86_64__)
    return "x86_64";
#elif defined(__arm__)
    return "arm";
#else
    return "unknown";
#endif
}

}  // namespace

PortableEnvironmentInfo::PortableEnvironmentInfo(std::string architecture,
                                                 std::string compiler)
    : architecture_(std::move(architecture)), compiler_(std::move(compiler)) {}

PortableEnvironmentInfo PortableEnvironmentInfo::capture() {
    return PortableEnvironmentInfo(architecture_name(), compiler_name());
}

const std::string& PortableEnvironmentInfo::architecture() const noexcept {
    return architecture_;
}

const std::string& PortableEnvironmentInfo::compiler() const noexcept {
    return compiler_;
}

std::string PortableEnvironmentInfo::canonical_json() const {
    return "{\"architecture\":\"" + json_escape(architecture_) +
           "\",\"compiler\":\"" + json_escape(compiler_) + "\"}";
}

PortableControlSession::PortableControlSession(
    PortableControlOptions options,
    RuntimeConfig config,
    std::unique_ptr<const backend_ort::OrtOptionsRecord> ort_options,
    std::unique_ptr<const OpenCvThreadPolicyRecord> opencv_thread_policy,
    PortableEnvironmentInfo environment_info,
    std::filesystem::path evidence_record_path,
    std::filesystem::path trace_output_path)
    : options_(std::move(options)),
      config_(std::move(config)),
      ort_options_(std::move(ort_options)),
      opencv_thread_policy_(std::move(opencv_thread_policy)),
      environment_info_(std::move(environment_info)),
      evidence_record_path_(std::move(evidence_record_path)),
      trace_output_path_(std::move(trace_output_path)) {}

core::Status PortableControlSession::start(
    const PortableControlOptions& options,
    std::unique_ptr<const PortableControlSession>* output) {
    if (output == nullptr) {
        return invalid("output session pointer must not be null");
    }
    if (options.executable_path.empty() || options.config_path.empty() ||
        options.evidence_directory.empty()) {
        return invalid("executable_path, config_path and evidence_directory "
                       "must be non-empty");
    }

    const std::filesystem::path executable_path =
        normalized_path(options.executable_path);
    const std::filesystem::path config_path = normalized_path(options.config_path);
    const std::filesystem::path evidence_directory =
        normalized_path(options.evidence_directory);

    if (!is_existing_file(executable_path)) {
        return invalid("executable_path must identify a regular file: " +
                       executable_path.string());
    }
    if (!is_existing_file(config_path)) {
        return invalid("config_path must identify a regular file: " +
                       config_path.string());
    }
    if (is_existing_file(evidence_directory)) {
        return invalid("evidence_directory must be a directory path");
    }

    RuntimeConfig config;
    const Status config_status = RuntimeConfigLoader::load(config_path, &config);
    if (!config_status.ok()) {
        return Status::failure(config_status.code(),
                               "portable control config: " +
                                   config_status.message());
    }
    if (config.schema_version != 2U) {
        return invalid("portable control requires RuntimeConfig schema_version 2");
    }

    std::unique_ptr<const backend_ort::OrtOptionsRecord> ort_options;
    const Status ort_status =
        backend_ort::OrtOptionsRecord::create(config, &ort_options);
    if (!ort_status.ok()) {
        return ort_status;
    }

    std::filesystem::path trace_output_path = options.trace_output_path;
    if (trace_output_path.empty()) {
        trace_output_path = evidence_directory / "trace.jsonl";
    } else if (!trace_output_path.is_absolute()) {
        trace_output_path = evidence_directory / trace_output_path;
    }
    trace_output_path = normalized_path(trace_output_path);
    if (is_existing_directory(trace_output_path)) {
        return invalid("trace_output_path must identify a file path");
    }

    const std::filesystem::path evidence_record_path =
        evidence_directory / "run_control.json";
    if (is_existing_directory(evidence_record_path)) {
        return invalid("evidence record path must identify a file path");
    }

    std::unique_ptr<const OpenCvThreadPolicyRecord> opencv_thread_policy;
    const Status opencv_status =
        OpenCvThreadPolicyRecord::apply(config, &opencv_thread_policy);
    if (!opencv_status.ok()) {
        return opencv_status;
    }

    std::error_code error;
    if (!std::filesystem::create_directories(evidence_directory, error) &&
        error) {
        return io_error("could not create evidence_directory: " +
                        evidence_directory.string() + ": " + error.message());
    }
    if (!is_existing_directory(evidence_directory)) {
        return io_error("evidence_directory is not a directory: " +
                        evidence_directory.string());
    }
    const std::filesystem::path trace_parent = trace_output_path.parent_path();
    if (is_existing_file(trace_parent)) {
        return invalid("trace output parent must be a directory path");
    }
    if (!std::filesystem::create_directories(trace_parent, error) && error) {
        return io_error("could not create trace output parent: " +
                        trace_parent.string() + ": " + error.message());
    }
    if (!is_existing_directory(trace_parent)) {
        return io_error("trace output parent is not a directory: " +
                        trace_parent.string());
    }

    *output = std::unique_ptr<const PortableControlSession>(
        new PortableControlSession(
            PortableControlOptions{executable_path,
                                    config_path,
                                    evidence_directory,
                                    trace_output_path,
                                    options.overwrite_evidence},
            std::move(config),
            std::move(ort_options),
            std::move(opencv_thread_policy),
            PortableEnvironmentInfo::capture(),
            evidence_record_path,
            trace_output_path));
    return Status::success();
}

const RuntimeConfig& PortableControlSession::config() const noexcept {
    return config_;
}

const std::filesystem::path& PortableControlSession::executable_path() const noexcept {
    return options_.executable_path;
}

const std::filesystem::path& PortableControlSession::config_path() const noexcept {
    return options_.config_path;
}

const std::filesystem::path& PortableControlSession::evidence_directory() const noexcept {
    return options_.evidence_directory;
}

const std::filesystem::path& PortableControlSession::evidence_record_path() const noexcept {
    return evidence_record_path_;
}

const std::filesystem::path& PortableControlSession::trace_output_path() const noexcept {
    return trace_output_path_;
}

const backend_ort::OrtOptionsRecord& PortableControlSession::ort_options() const noexcept {
    return *ort_options_;
}

const OpenCvThreadPolicyRecord& PortableControlSession::opencv_thread_policy() const noexcept {
    return *opencv_thread_policy_;
}

const PortableEnvironmentInfo& PortableControlSession::environment_info() const noexcept {
    return environment_info_;
}

std::string PortableControlSession::canonical_json() const {
    return "{\"schema_version\":1,\"executable_path\":\"" +
           json_path(executable_path()) +
           "\",\"config_path\":\"" + json_path(config_path()) +
           "\",\"model_path\":\"" + json_path(config_.model_path) +
           "\",\"evidence_directory\":\"" +
           json_path(evidence_directory()) +
           "\",\"evidence_record_path\":\"" +
           json_path(evidence_record_path()) +
           "\",\"ort_options\":" + ort_options().canonical_json() +
           ",\"opencv_thread_policy\":" +
           opencv_thread_policy().canonical_json() +
           ",\"trace_output_path\":\"" +
           json_path(trace_output_path()) +
           "\",\"environment\":" + environment_info().canonical_json() +
           "}";
}

core::Status PortableControlSession::write_evidence_record() const {
    if (!options_.overwrite_evidence && is_existing_file(evidence_record_path_)) {
        return io_error("evidence record already exists and overwrite is disabled: " +
                        evidence_record_path_.string());
    }

    std::ofstream output(evidence_record_path_, std::ios::trunc);
    if (!output) {
        return io_error("could not open evidence record: " +
                        evidence_record_path_.string());
    }
    output << canonical_json() << '\n';
    output.flush();
    if (!output) {
        return io_error("could not write evidence record: " +
                        evidence_record_path_.string());
    }
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
