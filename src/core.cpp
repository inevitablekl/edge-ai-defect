#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"

#include <cstdint>
#include <limits>
#include <string>
#include <utility>

namespace edge_ai_defect::core {

Status::Status(ErrorCode code, std::string message)
    : code_(code), message_(std::move(message)) {}

Status Status::success() noexcept {
    return Status();
}

Status Status::failure(ErrorCode code, std::string message) {
    if (code == ErrorCode::kOk) {
        return Status(ErrorCode::kInvalidArgument,
                      "Failure status requires a non-kOk error code");
    }
    return Status(code, std::move(message));
}

bool Status::ok() const noexcept {
    return code_ == ErrorCode::kOk;
}

ErrorCode Status::code() const noexcept {
    return code_;
}

const std::string& Status::message() const noexcept {
    return message_;
}

Status checked_element_count(const std::vector<std::int64_t>& shape,
                             std::size_t& element_count) {
    element_count = 0;
    if (shape.empty()) {
        return Status::failure(ErrorCode::kInvalidShape,
                               "Tensor shape must not be empty");
    }

    std::size_t count = 1;
    constexpr std::size_t kMaximumSize =
        std::numeric_limits<std::size_t>::max();
    for (std::size_t index = 0; index < shape.size(); ++index) {
        const std::int64_t dimension = shape[index];
        if (dimension <= 0) {
            return Status::failure(
                ErrorCode::kInvalidShape,
                "Tensor dimension at index " + std::to_string(index) +
                    " must be positive, got " + std::to_string(dimension));
        }

        const std::uint64_t unsigned_dimension =
            static_cast<std::uint64_t>(dimension);
        if constexpr (sizeof(std::size_t) < sizeof(std::uint64_t)) {
            if (unsigned_dimension > kMaximumSize) {
                return Status::failure(
                    ErrorCode::kOverflow,
                    "Tensor dimension at index " + std::to_string(index) +
                        " exceeds size_t range");
            }
        }

        const std::size_t dimension_size =
            static_cast<std::size_t>(unsigned_dimension);
        if (count > kMaximumSize / dimension_size) {
            return Status::failure(
                ErrorCode::kOverflow,
                "Tensor element count overflows size_t at dimension index " +
                    std::to_string(index));
        }
        count *= dimension_size;
    }

    element_count = count;
    return Status::success();
}

namespace {

Status validate_tensor_info_and_count(const TensorInfo& info,
                                      std::size_t& element_count) {
    switch (info.dtype) {
        case TensorDataType::kFloat32:
            break;
        default:
            return Status::failure(ErrorCode::kUnsupportedDataType,
                                   "Unsupported tensor data type");
    }

    switch (info.layout) {
        case TensorLayout::kNchw:
        case TensorLayout::kBcn:
            break;
        default:
            return Status::failure(ErrorCode::kUnsupportedLayout,
                                   "Unsupported tensor layout");
    }

    return checked_element_count(info.shape, element_count);
}

}  // namespace

Status validate_tensor_info(const TensorInfo& info) {
    std::size_t element_count = 0;
    return validate_tensor_info_and_count(info, element_count);
}

Status validate_host_tensor(const HostTensor& tensor) {
    std::size_t expected_element_count = 0;
    const Status info_status =
        validate_tensor_info_and_count(tensor.info, expected_element_count);
    if (!info_status.ok()) {
        return info_status;
    }

    if (tensor.data.size() != expected_element_count) {
        return Status::failure(
            ErrorCode::kDataSizeMismatch,
            "HostTensor data size mismatch: expected " +
                std::to_string(expected_element_count) + ", got " +
                std::to_string(tensor.data.size()));
    }

    return Status::success();
}

}  // namespace edge_ai_defect::core
