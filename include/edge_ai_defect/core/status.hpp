#pragma once

#include <string>

namespace edge_ai_defect::core {

enum class ErrorCode {
    kOk,
    kInvalidArgument,
    kInvalidShape,
    kUnsupportedDataType,
    kUnsupportedLayout,
    kOverflow,
    kDataSizeMismatch,
    kIoError,
    kParseError,
    kSchemaViolation,
    kImageProcessingError,
    kModelContractMismatch,
    kBackendInitializationError,
    kBackendRuntimeError,
};

class Status {
public:
    [[nodiscard]] static Status success() noexcept;
    [[nodiscard]] static Status failure(ErrorCode code, std::string message);

    [[nodiscard]] bool ok() const noexcept;
    [[nodiscard]] ErrorCode code() const noexcept;
    [[nodiscard]] const std::string& message() const noexcept;

private:
    Status() noexcept = default;
    Status(ErrorCode code, std::string message);

    ErrorCode code_ = ErrorCode::kOk;
    std::string message_;
};

}  // namespace edge_ai_defect::core
