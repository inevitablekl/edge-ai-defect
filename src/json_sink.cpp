#include "edge_ai_defect/runtime/json_sink.hpp"

#include "result_sink_detail.hpp"

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <system_error>
#include <unistd.h>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;
namespace fs = std::filesystem;

Status state_error(const char* operation) {
    return Status::failure(ErrorCode::kInvalidArgument,
                           std::string("JsonSink cannot ") + operation +
                               " in its current lifecycle state");
}

Status filesystem_failure(const std::string& stage, const std::error_code& error) {
    return Status::failure(ErrorCode::kIoError, stage + ": " + error.message());
}

}  // namespace

JsonSink::JsonSink(std::filesystem::path target_path, bool overwrite)
    : target_path_(std::move(target_path)), overwrite_(overwrite) {}

JsonSink::~JsonSink() {
    remove_temporary_file();
}

void JsonSink::remove_temporary_file() noexcept {
    if (temporary_path_.empty()) {
        return;
    }
    std::error_code error;
    fs::remove(temporary_path_, error);
    temporary_path_.clear();
}

core::Status JsonSink::create(const fs::path& target_path,
                              bool overwrite,
                              std::unique_ptr<JsonSink>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "JsonSink create output must not be null");
    }
    if (target_path.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "JsonSink target path must not be empty");
    }
    const fs::path parent = target_path.has_parent_path() ? target_path.parent_path()
                                                           : fs::path{"."};
    std::error_code error;
    const fs::file_status parent_status = fs::status(parent, error);
    if (error) {
        return filesystem_failure("inspect JsonSink output parent", error);
    }
    if (!fs::exists(parent_status) || !fs::is_directory(parent_status)) {
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink output parent must exist and be a directory");
    }
    const bool target_exists = fs::exists(target_path, error);
    if (error) {
        return filesystem_failure("inspect JsonSink target", error);
    }
    if (target_exists && fs::is_directory(target_path, error)) {
        if (error) {
            return filesystem_failure("inspect JsonSink target", error);
        }
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink target must not be a directory");
    }
    if (!overwrite && target_exists) {
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink target exists while overwrite is false");
    }

    std::unique_ptr<JsonSink> candidate(new JsonSink(target_path, overwrite));
    *output = std::move(candidate);
    return Status::success();
}

core::Status JsonSink::begin_run(const RunMetadata& metadata) {
    if (state_ != State::kReady) {
        return state_error("begin_run");
    }
    const Status validation_status = detail::validate_metadata(metadata);
    if (!validation_status.ok()) {
        return validation_status;
    }
    std::error_code error;
    const bool target_exists = fs::exists(target_path_, error);
    if (error) {
        return filesystem_failure("inspect JsonSink target", error);
    }
    if (!overwrite_ && target_exists) {
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink target exists while overwrite is false");
    }
    metadata_ = metadata;
    state_ = State::kActive;
    return Status::success();
}

core::Status JsonSink::write_frame(const FrameResult& frame) {
    if (state_ != State::kActive) {
        return state_error("write_frame");
    }
    const Status validation_status =
        detail::validate_frame(frame, metadata_, frames_.size());
    if (!validation_status.ok()) {
        return validation_status;
    }
    frames_.push_back(frame);
    received_detections_ += frame.detections.size();
    return Status::success();
}

core::Status JsonSink::end_run(const RunSummary& summary) {
    if (state_ != State::kActive) {
        return state_error("end_run");
    }
    const Status summary_status =
        detail::validate_summary(summary, frames_.size(), received_detections_);
    if (!summary_status.ok()) {
        return summary_status;
    }

    std::string serialized;
    try {
        serialized = detail::serialize_run(metadata_, frames_, summary);
    } catch (const std::exception& exception) {
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink serialize failed: " + std::string(exception.what()));
    }

    const fs::path parent = target_path_.has_parent_path() ? target_path_.parent_path()
                                                            : fs::path{"."};
    std::string pattern = (parent / (target_path_.filename().string() + ".tmp.XXXXXX")).string();
    std::vector<char> writable_pattern(pattern.begin(), pattern.end());
    writable_pattern.push_back('\0');
    const int descriptor = ::mkstemp(writable_pattern.data());
    if (descriptor < 0) {
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink create temporary file failed: " +
                                   std::string(std::strerror(errno)));
    }
    temporary_path_ = writable_pattern.data();
    std::FILE* file = ::fdopen(descriptor, "wb");
    if (file == nullptr) {
        const int saved_errno = errno;
        ::close(descriptor);
        remove_temporary_file();
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink open temporary file failed: " +
                                   std::string(std::strerror(saved_errno)));
    }
    bool write_failed = std::fwrite(serialized.data(), 1, serialized.size(), file) !=
                        serialized.size();
    if (!write_failed && std::fflush(file) != 0) {
        write_failed = true;
    }
    if (std::fclose(file) != 0) {
        write_failed = true;
    }
    if (write_failed) {
        const int saved_errno = errno;
        remove_temporary_file();
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink write temporary file failed: " +
                                   std::string(std::strerror(saved_errno)));
    }

    if (!overwrite_) {
        std::error_code error;
        if (fs::exists(target_path_, error)) {
            remove_temporary_file();
            if (error) {
                return filesystem_failure("inspect JsonSink target before commit", error);
            }
            return Status::failure(ErrorCode::kIoError,
                                   "JsonSink target exists while overwrite is false");
        }
        if (error) {
            remove_temporary_file();
            return filesystem_failure("inspect JsonSink target before commit", error);
        }
    }
    if (std::rename(temporary_path_.c_str(), target_path_.c_str()) != 0) {
        const int saved_errno = errno;
        remove_temporary_file();
        return Status::failure(ErrorCode::kIoError,
                               "JsonSink atomic rename failed: " +
                                   std::string(std::strerror(saved_errno)));
    }
    temporary_path_.clear();
    state_ = State::kCompleted;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
