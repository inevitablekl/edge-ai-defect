#pragma once

#include "edge_ai_defect/runtime/image_source.hpp"

#include <cstddef>
#include <filesystem>
#include <memory>
#include <optional>
#include <vector>

namespace edge_ai_defect::runtime {

class DirectorySource final : public ImageSource {
public:
    [[nodiscard]] static core::Status create(
        const std::filesystem::path& root,
        std::unique_ptr<DirectorySource>* output);

    // On decode failure the cursor remains on the failing entry, so a later
    // call retries that same entry. EOS remains success plus std::nullopt.
    [[nodiscard]] core::Status next(
        std::optional<ImageItem>* output) override;

private:
    DirectorySource(std::filesystem::path root,
                    std::vector<std::filesystem::path> relative_paths);

    std::filesystem::path root_;
    std::vector<std::filesystem::path> relative_paths_;
    std::size_t cursor_ = 0;
};

}  // namespace edge_ai_defect::runtime
