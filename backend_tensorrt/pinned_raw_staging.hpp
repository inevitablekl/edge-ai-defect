#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <cuda_runtime_api.h>
#include <opencv2/core.hpp>

#include <cstddef>
#include <cstdint>

namespace edge_ai_defect::stage_r {

// V3-only pinned (page-locked) host staging. The buffer is allocated once at
// initialization, reused for every frame, and released at shutdown. It owns
// packed BGR rows; it never retains cv::Mat padding bytes. Allocation failure
// is an explicit error; there is no silent fallback to pageable staging.
class PinnedRawStaging final {
public:
    PinnedRawStaging() = default;
    ~PinnedRawStaging();

    PinnedRawStaging(const PinnedRawStaging&) = delete;
    PinnedRawStaging& operator=(const PinnedRawStaging&) = delete;

    // Allocate the pinned buffer with the requested capacity in bytes.
    // Idempotent when the current buffer already satisfies the capacity.
    // Allocates with cudaHostAlloc; never allocates per frame.
    [[nodiscard]] core::Status allocate(std::size_t capacity);

    // Copy one CV_8UC3 image into the pinned buffer using row-aware copies.
    // Fails explicitly if the packed image does not fit the allocated
    // capacity; it does not fall back to pageable staging.
    [[nodiscard]] core::Status prepare(const cv::Mat& image);

    [[nodiscard]] const std::uint8_t* data() const noexcept { return pinned_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] int channels() const noexcept { return channels_; }
    [[nodiscard]] std::size_t source_row_stride() const noexcept { return source_row_stride_; }
    [[nodiscard]] std::size_t packed_row_bytes() const noexcept { return packed_row_bytes_; }
    [[nodiscard]] std::size_t total_packed_bytes() const noexcept { return size_; }

private:
    std::uint8_t* pinned_ = nullptr;
    std::size_t capacity_ = 0;
    std::size_t size_ = 0;
    int width_ = 0;
    int height_ = 0;
    int channels_ = 0;
    std::size_t source_row_stride_ = 0;
    std::size_t packed_row_bytes_ = 0;
};

}  // namespace edge_ai_defect::stage_r
