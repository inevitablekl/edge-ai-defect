#include "edge_ai_defect/runtime/opencv_thread_policy.hpp"

#include <opencv2/core.hpp>

#include <climits>
#include <cstdint>
#include <string>
#include <utility>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status invalid(const std::string& detail) {
    return Status::failure(ErrorCode::kSchemaViolation,
                           "OpenCV thread policy: " + detail);
}

}  // namespace

OpenCvThreadPolicyRecord::OpenCvThreadPolicyRecord(
    std::uint32_t requested_threads,
    std::uint32_t applied_threads,
    std::string opencv_version,
    bool policy_active)
    : requested_threads_(requested_threads),
      applied_threads_(applied_threads),
      opencv_version_(std::move(opencv_version)),
      policy_active_(policy_active) {}

core::Status OpenCvThreadPolicyRecord::apply(
    const RuntimeConfig& config,
    std::unique_ptr<const OpenCvThreadPolicyRecord>* output) {
    if (output == nullptr) {
        return Status::failure(
            ErrorCode::kInvalidArgument,
            "output: OpenCV thread policy record pointer must not be null");
    }
    if (config.schema_version != 2U) {
        return invalid("schema_version must be exactly 2");
    }
    if (config.opencv_num_threads == 0U ||
        config.opencv_num_threads > static_cast<std::uint32_t>(INT_MAX)) {
        return invalid("opencv_num_threads must be positive and fit int");
    }

    const std::uint32_t requested_threads = config.opencv_num_threads;
    cv::setNumThreads(static_cast<int>(requested_threads));
    const int applied_value = cv::getNumThreads();
    if (applied_value <= 0 ||
        static_cast<std::uint32_t>(applied_value) != requested_threads) {
        return Status::failure(
            ErrorCode::kBackendInitializationError,
            "OpenCV thread policy was not applied exactly: requested " +
                std::to_string(requested_threads) + ", applied " +
                std::to_string(applied_value));
    }

    *output = std::unique_ptr<const OpenCvThreadPolicyRecord>(
        new OpenCvThreadPolicyRecord(requested_threads,
                                     static_cast<std::uint32_t>(applied_value),
                                     CV_VERSION,
                                     true));
    return Status::success();
}

std::uint32_t OpenCvThreadPolicyRecord::requested_threads() const noexcept {
    return requested_threads_;
}

std::uint32_t OpenCvThreadPolicyRecord::applied_threads() const noexcept {
    return applied_threads_;
}

const std::string& OpenCvThreadPolicyRecord::opencv_version() const noexcept {
    return opencv_version_;
}

bool OpenCvThreadPolicyRecord::policy_active() const noexcept {
    return policy_active_;
}

std::string OpenCvThreadPolicyRecord::canonical_json() const {
    return "{\"requested_threads\":" +
           std::to_string(requested_threads_) +
           ",\"applied_threads\":" + std::to_string(applied_threads_) +
           ",\"opencv_version\":\"" + opencv_version_ +
           "\",\"policy_active\":" +
           (policy_active_ ? "true" : "false") + "}";
}

}  // namespace edge_ai_defect::runtime
