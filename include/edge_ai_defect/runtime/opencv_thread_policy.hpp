#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <cstdint>
#include <memory>
#include <string>

namespace edge_ai_defect::runtime {

class OpenCvThreadPolicyRecord final {
public:
    OpenCvThreadPolicyRecord(const OpenCvThreadPolicyRecord&) = delete;
    OpenCvThreadPolicyRecord& operator=(const OpenCvThreadPolicyRecord&) = delete;
    OpenCvThreadPolicyRecord(OpenCvThreadPolicyRecord&&) = delete;
    OpenCvThreadPolicyRecord& operator=(OpenCvThreadPolicyRecord&&) = delete;
    ~OpenCvThreadPolicyRecord() = default;

    [[nodiscard]] static core::Status apply(
        const RuntimeConfig& config,
        std::unique_ptr<const OpenCvThreadPolicyRecord>* output);

    [[nodiscard]] std::uint32_t requested_threads() const noexcept;
    [[nodiscard]] std::uint32_t applied_threads() const noexcept;
    [[nodiscard]] const std::string& opencv_version() const noexcept;
    [[nodiscard]] bool policy_active() const noexcept;
    [[nodiscard]] std::string canonical_json() const;

private:
    OpenCvThreadPolicyRecord(std::uint32_t requested_threads,
                             std::uint32_t applied_threads,
                             std::string opencv_version,
                             bool policy_active);

    const std::uint32_t requested_threads_;
    const std::uint32_t applied_threads_;
    const std::string opencv_version_;
    const bool policy_active_;
};

}  // namespace edge_ai_defect::runtime
