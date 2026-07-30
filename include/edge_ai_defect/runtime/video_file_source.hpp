#pragma once

#include "edge_ai_defect/runtime/image_source.hpp"

#include <opencv2/videoio.hpp>

#include <cstddef>
#include <filesystem>
#include <memory>
#include <optional>

namespace edge_ai_defect::runtime {

struct VideoFileMetadata {
    int width = 0;
    int height = 0;
    double nominal_fps = 0.0;
    std::size_t decoded_frame_count = 0;
};

class VideoFileSource final : public ImageSource {
public:
    [[nodiscard]] static core::Status create(
        const std::filesystem::path& video_path,
        std::unique_ptr<VideoFileSource>* output,
        std::optional<std::size_t> max_frames = std::nullopt);

    // A successful end of stream assigns std::nullopt to output. A failure
    // leaves output unchanged. max_frames, when set, is a source-local
    // constructor control and is not part of RuntimeConfig.
    [[nodiscard]] core::Status next(
        std::optional<ImageItem>* output) override;

    [[nodiscard]] const std::filesystem::path& video_path() const noexcept {
        return video_path_;
    }

    [[nodiscard]] const VideoFileMetadata& metadata() const noexcept {
        return metadata_;
    }

private:
    VideoFileSource(std::filesystem::path video_path,
                    std::optional<std::size_t> max_frames);

    std::filesystem::path video_path_;
    std::optional<std::size_t> max_frames_;
    cv::VideoCapture capture_;
    VideoFileMetadata metadata_;
    std::size_t expected_frame_count_ = 0;
    bool has_expected_frame_count_ = false;
    bool eof_ = false;
};

}  // namespace edge_ai_defect::runtime
