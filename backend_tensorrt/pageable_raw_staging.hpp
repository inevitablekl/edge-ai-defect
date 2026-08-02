#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <opencv2/core.hpp>

#include <cstddef>
#include <cstdint>
#include <vector>

namespace edge_ai_defect::stage_r {

// V2-only ordinary pageable host staging. The buffer owns packed BGR rows;
// it never retains cv::Mat padding bytes and never uses CUDA host allocation.
class PageableRawStaging final {
public:
    [[nodiscard]] core::Status prepare(const cv::Mat& image);

    [[nodiscard]] const std::uint8_t* data() const noexcept { return bytes_.data(); }
    [[nodiscard]] std::size_t size() const noexcept { return bytes_.size(); }
    [[nodiscard]] std::size_t capacity() const noexcept { return bytes_.capacity(); }
    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] int channels() const noexcept { return channels_; }
    [[nodiscard]] std::size_t source_row_stride() const noexcept { return source_row_stride_; }
    [[nodiscard]] std::size_t packed_row_bytes() const noexcept { return packed_row_bytes_; }
    [[nodiscard]] std::size_t total_packed_bytes() const noexcept { return bytes_.size(); }

private:
    std::vector<std::uint8_t> bytes_;
    int width_ = 0;
    int height_ = 0;
    int channels_ = 0;
    std::size_t source_row_stride_ = 0;
    std::size_t packed_row_bytes_ = 0;
};

}  // namespace edge_ai_defect::stage_r
