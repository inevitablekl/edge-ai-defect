#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace edge_ai_defect::test::preprocess_level_a {

class ManifestError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

struct ReferenceInfo {
    std::string implementation;
    std::string python_version;
    std::string numpy_version;
    std::string opencv_version;
};

struct ToleranceProfile {
    double mae_limit = 0.0;
    double max_abs_limit = 0.0;
};

struct TransformMetadata {
    int original_width = 0;
    int original_height = 0;
    int target_width = 0;
    int target_height = 0;
    int resized_width = 0;
    int resized_height = 0;
    double gain = 0.0;
    int pad_left = 0;
    int pad_right = 0;
    int pad_top = 0;
    int pad_bottom = 0;
};

struct CaseDefinition {
    std::string id;
    std::filesystem::path input_path;
    std::string input_sha256;
    int width = 0;
    int height = 0;
    int channels = 0;
    std::vector<std::int64_t> target_shape;
    std::filesystem::path golden_path;
    std::string golden_sha256;
    std::size_t golden_element_count = 0;
    TransformMetadata metadata;
    std::string tolerance_profile;
};

struct Manifest {
    ReferenceInfo reference;
    std::map<std::string, ToleranceProfile> tolerances;
    std::vector<CaseDefinition> cases;
};

struct FrozenCaseSpec {
    const char* id;
    const char* input_path;
    const char* golden_path;
    int width;
    int height;
    int channels;
    std::array<std::int64_t, 4> target_shape;
    const char* tolerance_profile;
    TransformMetadata metadata;
};

const std::array<FrozenCaseSpec, 8>& frozen_case_specs() noexcept;

void resolve_asset_path_under_root(
    const std::filesystem::path& data_root,
    const std::filesystem::path& relative_path,
    std::filesystem::path* resolved_path);

Manifest load_manifest(const std::filesystem::path& manifest_path,
                       const std::filesystem::path& sha256sums_path);

}  // namespace edge_ai_defect::test::preprocess_level_a
