#include "backend_tensorrt/pageable_raw_staging.hpp"

#include <cstring>
#include <limits>

namespace edge_ai_defect::stage_r {

core::Status PageableRawStaging::prepare(const cv::Mat& image) {
    if (image.empty() || image.dims != 2 || image.depth() != CV_8U ||
        image.channels() != 3 || image.cols <= 0 || image.rows <= 0) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "pageable staging requires a non-empty CV_8UC3 image");
    }
    const std::size_t packed_row_bytes = static_cast<std::size_t>(image.cols) * 3U;
    if (image.cols > 0 && packed_row_bytes / 3U != static_cast<std::size_t>(image.cols)) {
        return core::Status::failure(core::ErrorCode::kOverflow,
                                     "pageable staging row byte count overflows");
    }
    const std::size_t height = static_cast<std::size_t>(image.rows);
    if (height > std::numeric_limits<std::size_t>::max() / packed_row_bytes) {
        return core::Status::failure(core::ErrorCode::kOverflow,
                                     "pageable staging byte count overflows");
    }
    const std::size_t total = height * packed_row_bytes;
    bytes_.resize(total);
    for (int row = 0; row < image.rows; ++row) {
        std::memcpy(bytes_.data() + static_cast<std::size_t>(row) * packed_row_bytes,
                    image.ptr(row), packed_row_bytes);
    }
    width_ = image.cols;
    height_ = image.rows;
    channels_ = 3;
    source_row_stride_ = image.step;
    packed_row_bytes_ = packed_row_bytes;
    return core::Status::success();
}

}  // namespace edge_ai_defect::stage_r
