#include "backend_tensorrt/pinned_raw_staging.hpp"

#include <cstring>
#include <limits>
#include <string>

namespace edge_ai_defect::stage_r {

PinnedRawStaging::~PinnedRawStaging() {
    if (pinned_ != nullptr) {
        cudaFreeHost(pinned_);
        pinned_ = nullptr;
    }
    capacity_ = 0;
    size_ = 0;
}

core::Status PinnedRawStaging::allocate(std::size_t capacity) {
    if (pinned_ != nullptr && capacity_ >= capacity) {
        return core::Status::success();
    }
    if (pinned_ != nullptr) {
        cudaFreeHost(pinned_);
        pinned_ = nullptr;
        capacity_ = 0;
    }
    void* memory = nullptr;
    const cudaError_t error = cudaHostAlloc(&memory, capacity, cudaHostAllocDefault);
    if (error != cudaSuccess || memory == nullptr) {
        return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                     std::string("pinned staging allocation failed: ") +
                                         cudaGetErrorString(error));
    }
    pinned_ = static_cast<std::uint8_t*>(memory);
    capacity_ = capacity;
    return core::Status::success();
}

core::Status PinnedRawStaging::prepare(const cv::Mat& image) {
    if (image.empty() || image.dims != 2 || image.depth() != CV_8U ||
        image.channels() != 3 || image.cols <= 0 || image.rows <= 0) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "pinned staging requires a non-empty CV_8UC3 image");
    }
    const std::size_t packed_row_bytes = static_cast<std::size_t>(image.cols) * 3U;
    if (image.cols > 0 && packed_row_bytes / 3U != static_cast<std::size_t>(image.cols)) {
        return core::Status::failure(core::ErrorCode::kOverflow,
                                     "pinned staging row byte count overflows");
    }
    const std::size_t height = static_cast<std::size_t>(image.rows);
    if (height > std::numeric_limits<std::size_t>::max() / packed_row_bytes) {
        return core::Status::failure(core::ErrorCode::kOverflow,
                                     "pinned staging byte count overflows");
    }
    const std::size_t total = height * packed_row_bytes;
    if (pinned_ == nullptr || total > capacity_) {
        return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                     "pinned staging buffer not allocated or too small; "
                                     "allocate() must be called with sufficient capacity");
    }
    for (int row = 0; row < image.rows; ++row) {
        std::memcpy(pinned_ + static_cast<std::size_t>(row) * packed_row_bytes,
                    image.ptr(row), packed_row_bytes);
    }
    size_ = total;
    width_ = image.cols;
    height_ = image.rows;
    channels_ = 3;
    source_row_stride_ = image.step;
    packed_row_bytes_ = packed_row_bytes;
    return core::Status::success();
}

}  // namespace edge_ai_defect::stage_r
