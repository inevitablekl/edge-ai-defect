#include "preprocess_level_a_manifest.hpp"

#include <yaml-cpp/yaml.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace fs = std::filesystem;
namespace level_a = edge_ai_defect::test::preprocess_level_a;

struct Options {
    fs::path manifest;
    fs::path temp_dir;
};

Options parse_options(int argc, char** argv) {
    if (argc != 5 || std::string(argv[1]) != "--manifest" ||
        std::string(argv[3]) != "--temp-dir") {
        throw std::runtime_error(
            "expected --manifest <tracked-manifest> --temp-dir <build-tree-dir>");
    }
    return {argv[2], argv[4]};
}

std::string read_text(const fs::path& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("cannot read manifest: " + path.string());
    }
    std::ostringstream contents;
    contents << input.rdbuf();
    if (input.bad()) {
        throw std::runtime_error("failed while reading manifest: " + path.string());
    }
    return contents.str();
}

void write_text(const fs::path& path, const std::string& contents) {
    std::ofstream output(path);
    if (!output) {
        throw std::runtime_error("cannot write temporary manifest: " + path.string());
    }
    output << contents;
    if (!output) {
        throw std::runtime_error("failed while writing temporary manifest: " +
                                 path.string());
    }
}

std::string emit_yaml(const YAML::Node& root) {
    YAML::Emitter output;
    output << root;
    if (!output.good()) {
        throw std::runtime_error("failed to emit temporary YAML manifest");
    }
    return output.c_str();
}

std::string replace_once(std::string contents,
                         const std::string& needle,
                         const std::string& replacement) {
    const std::size_t position = contents.find(needle);
    if (position == std::string::npos) {
        throw std::runtime_error("mutation anchor not found: " + needle);
    }
    contents.replace(position, needle.size(), replacement);
    return contents;
}

bool contains_all(const std::string& message,
                  const std::vector<std::string>& expected_tokens) {
    for (const std::string& token : expected_tokens) {
        if (message.find(token) == std::string::npos) {
            std::cerr << "missing diagnostic token '" << token << "' in: " << message
                      << '\n';
            return false;
        }
    }
    return true;
}

bool expect_failure(const std::string& name,
                    const fs::path& temp_dir,
                    const std::string& contents,
                    const std::string& sha256sums,
                    const std::vector<std::string>& expected_tokens) {
    const fs::path manifest_path = temp_dir / (name + ".yaml");
    const fs::path sha256sums_path = temp_dir / (name + ".SHA256SUMS");
    write_text(manifest_path, contents);
    write_text(sha256sums_path, sha256sums);
    try {
        static_cast<void>(level_a::load_manifest(manifest_path, sha256sums_path));
        std::cerr << name << ": expected schema failure but manifest passed\n";
        return false;
    } catch (const level_a::ManifestError& exception) {
        const bool pass = contains_all(exception.what(), expected_tokens);
        std::cout << name << ": " << (pass ? "PASS" : "FAIL")
                  << " diagnostic=" << exception.what() << '\n';
        return pass;
    }
}

bool expect_resolve_success(const std::string& name,
                            const fs::path& root,
                            const fs::path& relative,
                            const fs::path& expected) {
    try {
        fs::path resolved;
        level_a::resolve_asset_path_under_root(root, relative, &resolved);
        const bool pass = resolved == fs::canonical(expected);
        std::cout << name << ": " << (pass ? "PASS" : "FAIL") << '\n';
        return pass;
    } catch (const std::exception& exception) {
        std::cerr << name << ": unexpected failure: " << exception.what() << '\n';
        return false;
    }
}

bool expect_resolve_failure(const std::string& name,
                            const fs::path& root,
                            const fs::path& relative,
                            const std::vector<std::string>& expected_tokens) {
    try {
        fs::path resolved;
        level_a::resolve_asset_path_under_root(root, relative, &resolved);
        std::cerr << name << ": expected path rejection but resolved to " << resolved
                  << '\n';
        return false;
    } catch (const level_a::ManifestError& exception) {
        const bool pass = contains_all(exception.what(), expected_tokens);
        std::cout << name << ": " << (pass ? "PASS" : "FAIL")
                  << " diagnostic=" << exception.what() << '\n';
        return pass;
    }
}

int run(const Options& options) {
    std::error_code remove_error;
    fs::remove_all(options.temp_dir, remove_error);
    if (remove_error) {
        throw std::runtime_error("cannot clear temp directory: " +
                                 remove_error.message());
    }
    fs::create_directories(options.temp_dir);

    const std::string tracked_contents = read_text(options.manifest);
    const fs::path tracked_sha256sums_path = options.manifest.parent_path() / "SHA256SUMS";
    const std::string tracked_sha256sums = read_text(tracked_sha256sums_path);
    const YAML::Node tracked = YAML::Load(tracked_contents);
    bool pass = true;

    try {
        const level_a::Manifest manifest =
            level_a::load_manifest(options.manifest, tracked_sha256sums_path);
        if (manifest.cases.size() != level_a::frozen_case_specs().size()) {
            std::cerr << "positive_sha_chain: unexpected case count\n";
            pass = false;
        } else {
            std::cout << "positive_sha_chain: PASS\n";
        }
    } catch (const std::exception& exception) {
        std::cerr << "positive_sha_chain: FAIL " << exception.what() << '\n';
        pass = false;
    }

    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["input"] = root["cases"][1]["input"].as<std::string>();
        pass = expect_failure("duplicate_input_path",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"duplicate path", "vertical_padding",
                               "horizontal_padding", "input"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["golden_tensor"] =
            root["cases"][1]["golden_tensor"].as<std::string>();
        pass = expect_failure("duplicate_golden_path",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"duplicate path", "vertical_padding",
                               "horizontal_padding", "golden_tensor"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["input"] =
            root["cases"][1]["golden_tensor"].as<std::string>();
        pass = expect_failure("input_golden_path_collision",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"duplicate path", "vertical_padding",
                               "horizontal_padding", "input", "golden_tensor"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        const std::string vertical_input = root["cases"][1]["input"].as<std::string>();
        const std::string vertical_golden =
            root["cases"][1]["golden_tensor"].as<std::string>();
        root["cases"][1]["input"] = root["cases"][2]["input"].as<std::string>();
        root["cases"][1]["golden_tensor"] =
            root["cases"][2]["golden_tensor"].as<std::string>();
        root["cases"][2]["input"] = vertical_input;
        root["cases"][2]["golden_tensor"] = vertical_golden;
        pass = expect_failure("swapped_case_asset_paths",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"vertical_padding", "input", "expected=",
                               "actual="}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        YAML::Node replacement = YAML::Clone(root["cases"][1]);
        replacement["id"] = "horizontal_padding";
        root["cases"][2] = replacement;
        pass = expect_failure("substituted_case_semantics",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"duplicate path", "horizontal_padding", "input"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        root["unexpected_root_field"] = true;
        pass = expect_failure("unknown_root_field",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"manifest.unexpected_root_field", "unknown field"}) &&
               pass;
    }
    pass = expect_failure("duplicate_root_key",
                          options.temp_dir,
                          "schema_version: 1\n" + tracked_contents,
                          tracked_sha256sums,
                          {"manifest.schema_version", "duplicate key"}) &&
           pass;
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][0]["unexpected_case_field"] = true;
        pass = expect_failure("nested_unknown_field",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"manifest.cases[0].unexpected_case_field",
                               "unknown field"}) &&
               pass;
    }
    pass = expect_failure(
               "nested_duplicate_key",
               options.temp_dir,
               replace_once(tracked_contents,
                            "    width: 4\n",
                            "    width: 4\n    width: 4\n"),
               tracked_sha256sums,
               {"manifest.cases[0].width", "duplicate key"}) &&
           pass;
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["width"] = 8;
        pass = expect_failure("frozen_case_field",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"horizontal_padding", "width", "expected=4",
                               "actual=8"}) &&
               pass;
    }

    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][0]["input_sha256"] = std::string(64U, '0');
        pass = expect_failure("forged_input_sha",
                              options.temp_dir,
                              emit_yaml(root),
                              tracked_sha256sums,
                              {"SHA256 mismatch", "inputs/no_transform_gradient.bgr"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][0]["golden_sha256"] = std::string(64U, '0');
        pass = expect_failure(
                   "forged_golden_sha",
                   options.temp_dir,
                   emit_yaml(root),
                   tracked_sha256sums,
                   {"SHA256 mismatch", "golden/no_transform_gradient.f32le"}) &&
               pass;
    }
    {
        const std::string first_input_line =
            "6b687705511589a45cd148c49a34f4bbb85d6b0f496abcaae9c917b544f21bdc  "
            "inputs/no_transform_gradient.bgr\n";
        pass = expect_failure("missing_sha_entry",
                              options.temp_dir,
                              tracked_contents,
                              replace_once(tracked_sha256sums, first_input_line, ""),
                              {"expected exactly 18 entries", "17"}) &&
               pass;
        pass = expect_failure("duplicate_sha_entry",
                              options.temp_dir,
                              tracked_contents,
                              tracked_sha256sums + first_input_line,
                              {"duplicate path", "inputs/no_transform_gradient.bgr"}) &&
               pass;
        pass = expect_failure(
                   "sha_path_mismatch",
                   options.temp_dir,
                   tracked_contents,
                   replace_once(tracked_sha256sums,
                                "inputs/no_transform_gradient.bgr",
                                "inputs/no_transform_gradient_mismatch.bgr"),
                   {"missing manifest asset path", "inputs/no_transform_gradient.bgr"}) &&
               pass;
    }

    const fs::path path_root = options.temp_dir / "path_root";
    const fs::path outside = options.temp_dir / "outside";
    const fs::path prefix_collision = options.temp_dir / "path_root_escape";
    fs::create_directories(path_root / "regular");
    fs::create_directories(path_root / "inside");
    fs::create_directories(path_root / "nested");
    fs::create_directories(outside / "nested_target");
    fs::create_directories(prefix_collision);
    write_text(path_root / "regular/file.bin", "regular");
    write_text(path_root / "inside/file.bin", "inside");
    write_text(outside / "file.bin", "outside");
    write_text(outside / "nested_target/file.bin", "nested-outside");
    write_text(prefix_collision / "file.bin", "prefix");
    fs::create_symlink(path_root / "inside/file.bin", path_root / "inside_link.bin");
    fs::create_symlink(outside / "file.bin", path_root / "outside_link.bin");
    fs::create_directory_symlink(outside / "nested_target", path_root / "nested/out");
    fs::create_symlink(prefix_collision / "file.bin", path_root / "prefix_link.bin");

    pass = expect_resolve_success("regular_asset_path",
                                  path_root,
                                  "regular/file.bin",
                                  path_root / "regular/file.bin") &&
           pass;
    pass = expect_resolve_success("inside_symlink_path",
                                  path_root,
                                  "inside_link.bin",
                                  path_root / "inside/file.bin") &&
           pass;
    pass = expect_resolve_failure("outside_symlink_path",
                                  path_root,
                                  "outside_link.bin",
                                  {"escapes data root"}) &&
           pass;
    pass = expect_resolve_failure("nested_outside_symlink_path",
                                  path_root,
                                  "nested/out/file.bin",
                                  {"escapes data root"}) &&
           pass;
    pass = expect_resolve_failure("prefix_collision_symlink_path",
                                  path_root,
                                  "prefix_link.bin",
                                  {"escapes data root"}) &&
           pass;
    pass = expect_resolve_failure("nonexistent_asset_path",
                                  path_root,
                                  "missing.bin",
                                  {"cannot resolve existing asset"}) &&
           pass;
    pass = expect_resolve_failure("absolute_asset_path",
                                  path_root,
                                  outside / "file.bin",
                                  {"nonempty relative path"}) &&
           pass;
    pass = expect_resolve_failure("dotdot_asset_path",
                                  path_root,
                                  "../outside/file.bin",
                                  {"'..' is not allowed"}) &&
           pass;
    try {
        level_a::resolve_asset_path_under_root(
            path_root, "regular/file.bin", nullptr);
        std::cerr << "null_output_path: expected rejection\n";
        pass = false;
    } catch (const level_a::ManifestError& exception) {
        const bool null_pass = contains_all(exception.what(), {"output pointer is null"});
        std::cout << "null_output_path: " << (null_pass ? "PASS" : "FAIL") << '\n';
        pass = null_pass && pass;
    }

    std::cout << "manifest_guard: " << (pass ? "25/25 PASS" : "FAIL") << '\n';
    return pass ? 0 : 1;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        return run(parse_options(argc, argv));
    } catch (const std::exception& exception) {
        std::cerr << "manifest_guard: " << exception.what() << '\n';
        return 1;
    }
}
