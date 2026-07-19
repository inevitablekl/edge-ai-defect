#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <opencv2/core.hpp>

#include <cstddef>
#include <filesystem>
#include <optional>

namespace edge_ai_defect::runtime {

struct ImageItem {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    cv::Mat image_bgr;
};

class ImageSource {
public:
    virtual ~ImageSource() = default;

    // A successful end of stream assigns std::nullopt to output. A failure
    // leaves output unchanged.
    [[nodiscard]] virtual core::Status next(
        std::optional<ImageItem>* output) = 0;
};

}  // namespace edge_ai_defect::runtime
