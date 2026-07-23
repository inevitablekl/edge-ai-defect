#pragma once

#include "edge_ai_defect/backend_ort/onnx_runtime_options.hpp"
#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/opencv_thread_policy.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <filesystem>
#include <memory>
#include <string>

namespace edge_ai_defect::runtime {

struct PortableControlOptions {
    std::filesystem::path executable_path;
    std::filesystem::path config_path;
    std::filesystem::path evidence_directory;
    std::filesystem::path trace_output_path;
    bool overwrite_evidence = false;
};

class PortableEnvironmentInfo final {
public:
    [[nodiscard]] static PortableEnvironmentInfo capture();

    [[nodiscard]] const std::string& architecture() const noexcept;
    [[nodiscard]] const std::string& compiler() const noexcept;
    [[nodiscard]] std::string canonical_json() const;

private:
    PortableEnvironmentInfo(std::string architecture, std::string compiler);

    std::string architecture_;
    std::string compiler_;
};

class PortableControlSession final {
public:
    PortableControlSession(const PortableControlSession&) = delete;
    PortableControlSession& operator=(const PortableControlSession&) = delete;
    PortableControlSession(PortableControlSession&&) = delete;
    PortableControlSession& operator=(PortableControlSession&&) = delete;
    ~PortableControlSession() = default;

    [[nodiscard]] static core::Status start(
        const PortableControlOptions& options,
        std::unique_ptr<const PortableControlSession>* output);

    [[nodiscard]] const RuntimeConfig& config() const noexcept;
    [[nodiscard]] const std::filesystem::path& executable_path() const noexcept;
    [[nodiscard]] const std::filesystem::path& config_path() const noexcept;
    [[nodiscard]] const std::filesystem::path& evidence_directory() const noexcept;
    [[nodiscard]] const std::filesystem::path& evidence_record_path() const noexcept;
    [[nodiscard]] const std::filesystem::path& trace_output_path() const noexcept;
    [[nodiscard]] const backend_ort::OrtOptionsRecord& ort_options() const noexcept;
    [[nodiscard]] const OpenCvThreadPolicyRecord& opencv_thread_policy() const noexcept;
    [[nodiscard]] const PortableEnvironmentInfo& environment_info() const noexcept;
    [[nodiscard]] std::string canonical_json() const;

    [[nodiscard]] core::Status write_evidence_record() const;

private:
    PortableControlSession(
        PortableControlOptions options,
        RuntimeConfig config,
        std::unique_ptr<const backend_ort::OrtOptionsRecord> ort_options,
        std::unique_ptr<const OpenCvThreadPolicyRecord> opencv_thread_policy,
        PortableEnvironmentInfo environment_info,
        std::filesystem::path evidence_record_path,
        std::filesystem::path trace_output_path);

    const PortableControlOptions options_;
    const RuntimeConfig config_;
    const std::unique_ptr<const backend_ort::OrtOptionsRecord> ort_options_;
    const std::unique_ptr<const OpenCvThreadPolicyRecord> opencv_thread_policy_;
    const PortableEnvironmentInfo environment_info_;
    const std::filesystem::path evidence_record_path_;
    const std::filesystem::path trace_output_path_;
};

}  // namespace edge_ai_defect::runtime
