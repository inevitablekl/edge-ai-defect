#include "preprocess_level_a_manifest.hpp"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <fstream>
#include <initializer_list>
#include <limits>
#include <set>
#include <sstream>
#include <string_view>
#include <utility>

namespace edge_ai_defect::test::preprocess_level_a {
namespace {

namespace fs = std::filesystem;

constexpr double kGainTolerance = 1.0e-12;

const std::array<FrozenCaseSpec, 8> kFrozenCaseSpecs{{
    {"no_transform_gradient",
     "inputs/no_transform_gradient.bgr",
     "golden/no_transform_gradient.f32le",
     4,
     4,
     3,
     {1, 3, 4, 4},
     "exact",
     {4, 4, 4, 4, 4, 4, 1.0, 0, 0, 0, 0}},
    {"vertical_padding",
     "inputs/vertical_padding.bgr",
     "golden/vertical_padding.f32le",
     8,
     4,
     3,
     {1, 3, 8, 8},
     "exact",
     {8, 4, 8, 8, 8, 4, 1.0, 0, 0, 2, 2}},
    {"horizontal_padding",
     "inputs/horizontal_padding.bgr",
     "golden/horizontal_padding.f32le",
     4,
     8,
     3,
     {1, 3, 8, 8},
     "exact",
     {4, 8, 8, 8, 4, 8, 1.0, 2, 2, 0, 0}},
    {"odd_horizontal_padding",
     "inputs/odd_horizontal_padding.bgr",
     "golden/odd_horizontal_padding.f32le",
     5,
     8,
     3,
     {1, 3, 8, 8},
     "exact",
     {5, 8, 8, 8, 5, 8, 1.0, 1, 2, 0, 0}},
    {"non_integer_resize",
     "inputs/non_integer_resize.bgr",
     "golden/non_integer_resize.f32le",
     7,
     5,
     3,
     {1, 3, 11, 11},
     "resize",
     {7, 5, 11, 11, 11, 8, 11.0 / 7.0, 0, 0, 1, 2}},
    {"small_upscale",
     "inputs/small_upscale.bgr",
     "golden/small_upscale.f32le",
     3,
     2,
     3,
     {1, 3, 16, 16},
     "resize",
     {3, 2, 16, 16, 16, 11, 16.0 / 3.0, 0, 0, 2, 3}},
    {"rgb_color_blocks",
     "inputs/rgb_color_blocks.bgr",
     "golden/rgb_color_blocks.f32le",
     2,
     2,
     3,
     {1, 3, 2, 2},
     "exact",
     {2, 2, 2, 2, 2, 2, 1.0, 0, 0, 0, 0}},
    {"frozen_640_checkerboard",
     "inputs/frozen_640_checkerboard.bgr",
     "golden/frozen_640_checkerboard.f32le",
     37,
     53,
     3,
     {1, 3, 640, 640},
     "resize",
     {37, 53, 640, 640, 447, 640, 640.0 / 53.0, 96, 97, 0, 0}},
}};

template <typename T>
T require_scalar(const YAML::Node& parent,
                 const std::string& key,
                 const std::string& context) {
    const YAML::Node node = parent[key];
    if (!node || !node.IsScalar()) {
        throw ManifestError(context + "." + key + ": missing scalar field");
    }
    try {
        return node.as<T>();
    } catch (const YAML::Exception& exception) {
        throw ManifestError(context + "." + key + ": invalid scalar: " +
                            exception.what());
    }
}

void require_strict_mapping(const YAML::Node& node,
                            const std::string& context,
                            std::initializer_list<std::string_view> allowed_fields) {
    if (!node || !node.IsMap()) {
        throw ManifestError(context + ": expected mapping");
    }
    std::set<std::string> seen;
    for (const auto& entry : node) {
        if (!entry.first.IsScalar()) {
            throw ManifestError(context + ": mapping key must be scalar");
        }
        const std::string key = entry.first.Scalar();
        if (!seen.insert(key).second) {
            throw ManifestError(context + "." + key + ": duplicate key");
        }
        const bool allowed = std::any_of(
            allowed_fields.begin(), allowed_fields.end(), [&key](std::string_view field) {
                return field == key;
            });
        if (!allowed) {
            throw ManifestError(context + "." + key + ": unknown field");
        }
    }
}

void require_value(const YAML::Node& parent,
                   const std::string& key,
                   const std::string& expected,
                   const std::string& context) {
    const std::string actual = require_scalar<std::string>(parent, key, context);
    if (actual != expected) {
        throw ManifestError(context + "." + key + ": expected='" + expected +
                            "' actual='" + actual + "'");
    }
}

fs::path require_relative_path(const YAML::Node& parent,
                               const std::string& key,
                               const std::string& context) {
    const fs::path path = require_scalar<std::string>(parent, key, context);
    if (path.empty() || path.is_absolute()) {
        throw ManifestError(context + "." + key +
                            ": must be a nonempty relative path");
    }
    for (const fs::path& component : path) {
        if (component == "..") {
            throw ManifestError(context + "." + key +
                                ": path must not escape data root");
        }
    }
    return path;
}

std::string require_sha256_field(const YAML::Node& parent,
                                 const std::string& key,
                                 const std::string& context) {
    const std::string value = require_scalar<std::string>(parent, key, context);
    const bool is_hex = std::all_of(
        value.begin(), value.end(), [](char character) {
            return (character >= '0' && character <= '9') ||
                   (character >= 'a' && character <= 'f');
        });
    if (value.size() != 64U || !is_hex) {
        throw ManifestError(context + "." + key +
                            ": must be a lowercase SHA256 digest");
    }
    return value;
}

bool path_is_contained(const fs::path& root, const fs::path& candidate) {
    auto root_component = root.begin();
    auto candidate_component = candidate.begin();
    for (; root_component != root.end();
         ++root_component, ++candidate_component) {
        if (candidate_component == candidate.end() ||
            *candidate_component != *root_component) {
            return false;
        }
    }
    return true;
}

std::map<std::string, std::string> load_sha256sums(
    const fs::path& sha256sums_path) {
    std::ifstream input(sha256sums_path);
    if (!input) {
        throw ManifestError("SHA256SUMS: cannot read file: " +
                            sha256sums_path.string());
    }
    std::map<std::string, std::string> entries;
    std::string line;
    std::size_t line_number = 0U;
    while (std::getline(input, line)) {
        ++line_number;
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        const std::string context =
            "SHA256SUMS line " + std::to_string(line_number);
        if (line.size() <= 66U || line[64] != ' ' || line[65] != ' ') {
            throw ManifestError(context + ": expected '<sha256>  <path>'");
        }
        const std::string digest = line.substr(0U, 64U);
        const bool is_hex = std::all_of(
            digest.begin(), digest.end(), [](char character) {
                return (character >= '0' && character <= '9') ||
                       (character >= 'a' && character <= 'f');
            });
        if (!is_hex) {
            throw ManifestError(context + ": invalid lowercase SHA256 digest");
        }
        const fs::path path = line.substr(66U);
        if (path.empty() || path.is_absolute()) {
            throw ManifestError(context + ": path must be nonempty and relative");
        }
        for (const fs::path& component : path) {
            if (component == "..") {
                throw ManifestError(context + ": path must not contain '..'");
            }
        }
        const std::string normalized = path.generic_string();
        if (normalized == "SHA256SUMS") {
            throw ManifestError(context + ": SHA256SUMS must not hash itself");
        }
        if (!entries.emplace(normalized, digest).second) {
            throw ManifestError(context + ": duplicate path='" + normalized + "'");
        }
    }
    if (input.bad()) {
        throw ManifestError("SHA256SUMS: failed while reading file");
    }
    if (entries.size() != 18U) {
        throw ManifestError("SHA256SUMS: expected exactly 18 entries actual=" +
                            std::to_string(entries.size()));
    }
    return entries;
}

void validate_manifest_sha_chain(
    const std::vector<CaseDefinition>& cases,
    const std::map<std::string, std::string>& entries) {
    for (const CaseDefinition& definition : cases) {
        for (const auto& asset : {
                 std::pair<fs::path, std::string>{definition.input_path,
                                                  definition.input_sha256},
                 std::pair<fs::path, std::string>{definition.golden_path,
                                                  definition.golden_sha256}}) {
            const std::string path = asset.first.generic_string();
            const auto entry = entries.find(path);
            if (entry == entries.end()) {
                throw ManifestError("SHA256SUMS: missing manifest asset path='" +
                                    path + "'");
            }
            if (entry->second != asset.second) {
                throw ManifestError("SHA256 mismatch for path='" + path +
                                    "' manifest='" + asset.second +
                                    "' SHA256SUMS='" + entry->second + "'");
            }
        }
    }
}

TransformMetadata parse_metadata(const YAML::Node& node,
                                 const std::string& context) {
    require_strict_mapping(node,
                           context,
                           {"original_width",
                            "original_height",
                            "target_width",
                            "target_height",
                            "resized_width",
                            "resized_height",
                            "gain",
                            "pad_left",
                            "pad_right",
                            "pad_top",
                            "pad_bottom"});
    return {
        require_scalar<int>(node, "original_width", context),
        require_scalar<int>(node, "original_height", context),
        require_scalar<int>(node, "target_width", context),
        require_scalar<int>(node, "target_height", context),
        require_scalar<int>(node, "resized_width", context),
        require_scalar<int>(node, "resized_height", context),
        require_scalar<double>(node, "gain", context),
        require_scalar<int>(node, "pad_left", context),
        require_scalar<int>(node, "pad_right", context),
        require_scalar<int>(node, "pad_top", context),
        require_scalar<int>(node, "pad_bottom", context),
    };
}

std::vector<std::int64_t> parse_target_shape(const YAML::Node& node,
                                             const std::string& context) {
    if (!node || !node.IsSequence() || node.size() != 4U) {
        throw ManifestError(context + ".target_shape: expected four dimensions");
    }
    std::vector<std::int64_t> shape;
    shape.reserve(4U);
    for (std::size_t index = 0; index < node.size(); ++index) {
        try {
            shape.push_back(node[index].as<std::int64_t>());
        } catch (const YAML::Exception& exception) {
            throw ManifestError(context + ".target_shape[" + std::to_string(index) +
                                "]: invalid dimension: " + exception.what());
        }
    }
    if (shape[0] != 1 || shape[1] != 3 || shape[2] <= 0 || shape[3] <= 0) {
        throw ManifestError(context +
                            ".target_shape: expected positive [1,3,H,W]");
    }
    return shape;
}

std::size_t checked_element_count(const std::vector<std::int64_t>& shape,
                                  const std::string& context) {
    std::size_t count = 1U;
    for (std::size_t index = 0; index < shape.size(); ++index) {
        const std::int64_t dimension = shape[index];
        if (dimension <= 0 || static_cast<std::uint64_t>(dimension) >
                                  std::numeric_limits<std::size_t>::max()) {
            throw ManifestError(context + ".target_shape[" + std::to_string(index) +
                                "]: dimension does not fit size_t");
        }
        const std::size_t size = static_cast<std::size_t>(dimension);
        if (count > std::numeric_limits<std::size_t>::max() / size) {
            throw ManifestError(context + ".target_shape: element count overflow");
        }
        count *= size;
    }
    return count;
}

std::string render_shape(const std::vector<std::int64_t>& shape) {
    std::ostringstream output;
    output << '[';
    for (std::size_t index = 0; index < shape.size(); ++index) {
        output << (index == 0U ? "" : ",") << shape[index];
    }
    return output.str() + ']';
}

std::string render_shape(const std::array<std::int64_t, 4>& shape) {
    return render_shape(std::vector<std::int64_t>(shape.begin(), shape.end()));
}

template <typename T>
void require_frozen_equal(const std::string& case_id,
                          const std::string& field,
                          const T& expected,
                          const T& actual) {
    if (actual == expected) {
        return;
    }
    std::ostringstream message;
    message << "case '" << case_id << "'." << field << ": expected=" << expected
            << " actual=" << actual;
    throw ManifestError(message.str());
}

void validate_frozen_metadata(const CaseDefinition& actual,
                              const FrozenCaseSpec& expected) {
    const std::string& id = actual.id;
    const TransformMetadata& value = actual.metadata;
    const TransformMetadata& frozen = expected.metadata;
    require_frozen_equal(id, "expected_metadata.original_width", frozen.original_width,
                         value.original_width);
    require_frozen_equal(id, "expected_metadata.original_height", frozen.original_height,
                         value.original_height);
    require_frozen_equal(id, "expected_metadata.target_width", frozen.target_width,
                         value.target_width);
    require_frozen_equal(id, "expected_metadata.target_height", frozen.target_height,
                         value.target_height);
    require_frozen_equal(id, "expected_metadata.resized_width", frozen.resized_width,
                         value.resized_width);
    require_frozen_equal(id, "expected_metadata.resized_height", frozen.resized_height,
                         value.resized_height);
    if (!std::isfinite(value.gain) ||
        std::abs(value.gain - frozen.gain) > kGainTolerance) {
        std::ostringstream message;
        message << std::setprecision(17) << "case '" << id
                << "'.expected_metadata.gain: expected=" << frozen.gain
                << " actual=" << value.gain << " tolerance=" << kGainTolerance;
        throw ManifestError(message.str());
    }
    require_frozen_equal(id, "expected_metadata.pad_left", frozen.pad_left,
                         value.pad_left);
    require_frozen_equal(id, "expected_metadata.pad_right", frozen.pad_right,
                         value.pad_right);
    require_frozen_equal(id, "expected_metadata.pad_top", frozen.pad_top, value.pad_top);
    require_frozen_equal(id, "expected_metadata.pad_bottom", frozen.pad_bottom,
                         value.pad_bottom);
}

void validate_unique_paths(const std::vector<CaseDefinition>& cases) {
    struct PathOwner {
        std::string case_id;
        std::string field;
    };
    std::map<std::string, PathOwner> owners;
    for (const CaseDefinition& definition : cases) {
        for (const auto& candidate :
             {std::pair<std::string, fs::path>{"input", definition.input_path},
              std::pair<std::string, fs::path>{"golden_tensor",
                                               definition.golden_path}}) {
            const std::string path = candidate.second.generic_string();
            const auto [iterator, inserted] =
                owners.emplace(path, PathOwner{definition.id, candidate.first});
            if (!inserted) {
                throw ManifestError(
                    "manifest path uniqueness: duplicate path='" + path +
                    "' first_case='" + iterator->second.case_id + "' first_field='" +
                    iterator->second.field + "' second_case='" + definition.id +
                    "' second_field='" + candidate.first + "'");
            }
        }
    }
}

void validate_frozen_cases(const std::vector<CaseDefinition>& cases) {
    for (std::size_t index = 0; index < kFrozenCaseSpecs.size(); ++index) {
        const CaseDefinition& actual = cases[index];
        const FrozenCaseSpec& expected = kFrozenCaseSpecs[index];
        require_frozen_equal(std::string(expected.id),
                             "id/order",
                             std::string(expected.id),
                             actual.id);
        require_frozen_equal(actual.id,
                             "input",
                             std::string(expected.input_path),
                             actual.input_path.generic_string());
        require_frozen_equal(actual.id,
                             "golden_tensor",
                             std::string(expected.golden_path),
                             actual.golden_path.generic_string());
        require_frozen_equal(actual.id, "width", expected.width, actual.width);
        require_frozen_equal(actual.id, "height", expected.height, actual.height);
        require_frozen_equal(actual.id, "channels", expected.channels, actual.channels);
        const std::vector<std::int64_t> expected_shape(expected.target_shape.begin(),
                                                       expected.target_shape.end());
        if (actual.target_shape != expected_shape) {
            throw ManifestError("case '" + actual.id +
                                "'.target_shape: expected=" +
                                render_shape(expected.target_shape) + " actual=" +
                                render_shape(actual.target_shape));
        }
        require_frozen_equal(actual.id,
                             "tolerance_profile",
                             std::string(expected.tolerance_profile),
                             actual.tolerance_profile);
        validate_frozen_metadata(actual, expected);
        const std::size_t expected_count =
            checked_element_count(expected_shape, "case '" + actual.id + "'");
        require_frozen_equal(actual.id,
                             "golden_element_count",
                             expected_count,
                             actual.golden_element_count);
    }
}

}  // namespace

const std::array<FrozenCaseSpec, 8>& frozen_case_specs() noexcept {
    return kFrozenCaseSpecs;
}

void resolve_asset_path_under_root(const fs::path& data_root,
                                   const fs::path& relative_path,
                                   fs::path* resolved_path) {
    if (resolved_path == nullptr) {
        throw ManifestError("asset path: output pointer is null");
    }
    if (relative_path.empty() || relative_path.is_absolute()) {
        throw ManifestError("asset path: must be a nonempty relative path");
    }
    for (const fs::path& component : relative_path) {
        if (component == "..") {
            throw ManifestError("asset path: '..' is not allowed: " +
                                relative_path.generic_string());
        }
    }
    std::error_code error;
    const fs::path canonical_root = fs::canonical(data_root, error);
    if (error) {
        throw ManifestError("asset path: cannot resolve data root: " +
                            error.message());
    }
    const fs::path candidate = fs::canonical(canonical_root / relative_path, error);
    if (error) {
        throw ManifestError("asset path: cannot resolve existing asset '" +
                            relative_path.generic_string() + "': " +
                            error.message());
    }
    if (!path_is_contained(canonical_root, candidate) || candidate == canonical_root) {
        throw ManifestError("asset path: resolved path escapes data root: " +
                            relative_path.generic_string());
    }
    *resolved_path = candidate;
}

Manifest load_manifest(const fs::path& manifest_path,
                       const fs::path& sha256sums_path) {
    YAML::Node root;
    try {
        root = YAML::LoadFile(manifest_path.string());
    } catch (const YAML::Exception& exception) {
        throw ManifestError("manifest: " + std::string(exception.what()));
    }
    require_strict_mapping(
        root, "manifest", {"schema_version", "reference", "tensor_format",
                            "tolerance_profiles", "cases"});
    if (require_scalar<int>(root, "schema_version", "manifest") != 1) {
        throw ManifestError("manifest.schema_version: expected=1");
    }

    const YAML::Node reference = root["reference"];
    require_strict_mapping(reference,
                           "manifest.reference",
                           {"implementation",
                            "python_version",
                            "numpy_version",
                            "opencv_version",
                            "input_color_order",
                            "output_color_order",
                            "interpolation",
                            "padding_value",
                            "rounding",
                            "center",
                            "auto",
                            "scale_fill",
                            "scaleup",
                            "stride"});
    require_value(reference, "input_color_order", "BGR", "manifest.reference");
    require_value(reference, "output_color_order", "RGB", "manifest.reference");
    require_value(reference, "interpolation", "INTER_LINEAR", "manifest.reference");
    require_value(reference, "rounding", "python_ties_to_even", "manifest.reference");
    if (require_scalar<int>(reference, "padding_value", "manifest.reference") != 114 ||
        !require_scalar<bool>(reference, "center", "manifest.reference") ||
        require_scalar<bool>(reference, "auto", "manifest.reference") ||
        require_scalar<bool>(reference, "scale_fill", "manifest.reference") ||
        !require_scalar<bool>(reference, "scaleup", "manifest.reference") ||
        require_scalar<int>(reference, "stride", "manifest.reference") != 32) {
        throw ManifestError(
            "manifest.reference: frozen LetterBox semantics do not match Level A");
    }

    const YAML::Node tensor_format = root["tensor_format"];
    require_strict_mapping(
        tensor_format, "manifest.tensor_format", {"dtype", "byte_order", "layout"});
    require_value(tensor_format, "dtype", "float32", "manifest.tensor_format");
    require_value(
        tensor_format, "byte_order", "little_endian", "manifest.tensor_format");
    require_value(tensor_format, "layout", "NCHW", "manifest.tensor_format");

    Manifest manifest;
    manifest.reference = {
        require_scalar<std::string>(reference, "implementation", "manifest.reference"),
        require_scalar<std::string>(reference, "python_version", "manifest.reference"),
        require_scalar<std::string>(reference, "numpy_version", "manifest.reference"),
        require_scalar<std::string>(reference, "opencv_version", "manifest.reference"),
    };
    if (manifest.reference.opencv_version != "4.10.0") {
        throw ManifestError(
            "manifest.reference.opencv_version: expected='4.10.0' actual='" +
            manifest.reference.opencv_version + "'");
    }

    const YAML::Node profiles = root["tolerance_profiles"];
    require_strict_mapping(
        profiles, "manifest.tolerance_profiles", {"exact", "resize"});
    for (const std::string& name : {std::string("exact"), std::string("resize")}) {
        const YAML::Node profile = profiles[name];
        const std::string context = "manifest.tolerance_profiles." + name;
        require_strict_mapping(profile, context, {"mae_limit", "max_abs_limit"});
        const ToleranceProfile tolerance{
            require_scalar<double>(profile, "mae_limit", context),
            require_scalar<double>(profile, "max_abs_limit", context),
        };
        if (!std::isfinite(tolerance.mae_limit) || tolerance.mae_limit < 0.0 ||
            !std::isfinite(tolerance.max_abs_limit) ||
            tolerance.max_abs_limit < 0.0) {
            throw ManifestError(context + ": limits must be finite and nonnegative");
        }
        manifest.tolerances.emplace(name, tolerance);
    }

    const YAML::Node cases = root["cases"];
    if (!cases || !cases.IsSequence() || cases.size() != kFrozenCaseSpecs.size()) {
        throw ManifestError("manifest.cases: expected exactly eight entries");
    }
    for (std::size_t index = 0; index < cases.size(); ++index) {
        const YAML::Node node = cases[index];
        const std::string context = "manifest.cases[" + std::to_string(index) + "]";
        require_strict_mapping(node,
                               context,
                               {"id",
                                "input",
                                "input_sha256",
                                "width",
                                "height",
                                "channels",
                                "target_shape",
                                "golden_tensor",
                                "golden_sha256",
                                "golden_element_count",
                                "expected_metadata",
                                "tolerance_profile"});
        CaseDefinition definition;
        definition.id = require_scalar<std::string>(node, "id", context);
        const std::string case_context = "case '" + definition.id + "'";
        definition.input_path = require_relative_path(node, "input", case_context);
        definition.input_sha256 =
            require_sha256_field(node, "input_sha256", case_context);
        definition.width = require_scalar<int>(node, "width", case_context);
        definition.height = require_scalar<int>(node, "height", case_context);
        definition.channels = require_scalar<int>(node, "channels", case_context);
        if (definition.width <= 0 || definition.height <= 0 ||
            definition.channels != 3) {
            throw ManifestError(case_context +
                                ": input dimensions/channels are invalid");
        }
        definition.target_shape = parse_target_shape(node["target_shape"], case_context);
        definition.golden_path =
            require_relative_path(node, "golden_tensor", case_context);
        definition.golden_sha256 =
            require_sha256_field(node, "golden_sha256", case_context);
        definition.golden_element_count =
            require_scalar<std::size_t>(node, "golden_element_count", case_context);
        definition.metadata = parse_metadata(
            node["expected_metadata"], case_context + ".expected_metadata");
        definition.tolerance_profile =
            require_scalar<std::string>(node, "tolerance_profile", case_context);
        if (manifest.tolerances.count(definition.tolerance_profile) == 0U) {
            throw ManifestError(case_context + ".tolerance_profile: unknown profile '" +
                                definition.tolerance_profile + "'");
        }
        const std::size_t shape_count =
            checked_element_count(definition.target_shape, case_context);
        if (shape_count != definition.golden_element_count) {
            throw ManifestError(case_context +
                                ".golden_element_count: expected=" +
                                std::to_string(shape_count) + " actual=" +
                                std::to_string(definition.golden_element_count));
        }
        manifest.cases.push_back(std::move(definition));
    }

    validate_unique_paths(manifest.cases);
    validate_frozen_cases(manifest.cases);
    validate_manifest_sha_chain(manifest.cases, load_sha256sums(sha256sums_path));
    return manifest;
}

}  // namespace edge_ai_defect::test::preprocess_level_a
