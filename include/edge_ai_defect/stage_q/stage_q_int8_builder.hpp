#pragma once

#include <filesystem>
#include <cstdint>
#include <string>
#include <vector>

namespace edge_ai_defect::stage_q {

struct CalibrationImage {
    std::filesystem::path path;
    std::string sha256;
};

struct CalibrationManifest {
    std::string split;
    std::string source_sha256;
    std::string manifest_sha256;
    std::string purpose;
    std::string ordering_algorithm;
    std::uint32_t seed = 0;
    std::vector<CalibrationImage> images;
};

// Reads the frozen split_v2 JSON manifest, checks content identities, and
// returns exactly the requested prefix.  Q2 callers are required to request 4.
CalibrationManifest read_smoke_manifest(const std::filesystem::path& manifest,
                                        const std::filesystem::path& dataset_root,
                                        std::size_t image_count);

int run_builder(int argc, char** argv);

}  // namespace edge_ai_defect::stage_q
