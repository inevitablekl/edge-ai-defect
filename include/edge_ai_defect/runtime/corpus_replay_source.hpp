#pragma once

#include "edge_ai_defect/runtime/image_source.hpp"

#include <cstddef>
#include <filesystem>
#include <memory>
#include <vector>

namespace edge_ai_defect::runtime {

class CorpusReplaySource final : public ImageSource {
public:
    [[nodiscard]] static core::Status create(
        const std::filesystem::path& image_root,
        const std::filesystem::path& manifest_path,
        std::size_t cycles,
        std::unique_ptr<CorpusReplaySource>* output);

    [[nodiscard]] core::Status next(std::optional<ImageItem>* output) override;
    [[nodiscard]] std::size_t cycle_id() const noexcept { return last_cycle_id_; }
    [[nodiscard]] std::size_t frame_index() const noexcept { return last_frame_index_; }
    [[nodiscard]] std::size_t frame_count() const noexcept { return entries_.size(); }

private:
    struct Entry { std::filesystem::path filename; };
    CorpusReplaySource(std::filesystem::path root, std::vector<Entry> entries,
                       std::size_t cycles);
    std::filesystem::path root_;
    std::vector<Entry> entries_;
    std::size_t cycles_ = 0;
    std::size_t cursor_ = 0;
    std::size_t last_cycle_id_ = 0;
    std::size_t last_frame_index_ = 0;
};

}  // namespace edge_ai_defect::runtime
