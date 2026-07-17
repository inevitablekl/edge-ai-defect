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
                    const std::vector<std::string>& expected_tokens) {
    const fs::path manifest_path = temp_dir / (name + ".yaml");
    write_text(manifest_path, contents);
    try {
        static_cast<void>(level_a::load_manifest(manifest_path));
        std::cerr << name << ": expected schema failure but manifest passed\n";
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
    const YAML::Node tracked = YAML::Load(tracked_contents);
    bool pass = true;

    try {
        const level_a::Manifest manifest = level_a::load_manifest(options.manifest);
        if (manifest.cases.size() != level_a::frozen_case_specs().size()) {
            std::cerr << "positive_tracked_manifest: unexpected case count\n";
            pass = false;
        } else {
            std::cout << "positive_tracked_manifest: PASS\n";
        }
    } catch (const std::exception& exception) {
        std::cerr << "positive_tracked_manifest: FAIL " << exception.what() << '\n';
        pass = false;
    }

    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["input"] = root["cases"][1]["input"].as<std::string>();
        pass = expect_failure("duplicate_input_path",
                              options.temp_dir,
                              emit_yaml(root),
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
                              {"duplicate path", "horizontal_padding", "input"}) &&
               pass;
    }
    {
        YAML::Node root = YAML::Clone(tracked);
        root["unexpected_root_field"] = true;
        pass = expect_failure("unknown_root_field",
                              options.temp_dir,
                              emit_yaml(root),
                              {"manifest.unexpected_root_field", "unknown field"}) &&
               pass;
    }
    pass = expect_failure("duplicate_root_key",
                          options.temp_dir,
                          "schema_version: 1\n" + tracked_contents,
                          {"manifest.schema_version", "duplicate key"}) &&
           pass;
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][0]["unexpected_case_field"] = true;
        pass = expect_failure("nested_unknown_field",
                              options.temp_dir,
                              emit_yaml(root),
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
               {"manifest.cases[0].width", "duplicate key"}) &&
           pass;
    {
        YAML::Node root = YAML::Clone(tracked);
        root["cases"][2]["width"] = 8;
        pass = expect_failure("frozen_case_field",
                              options.temp_dir,
                              emit_yaml(root),
                              {"horizontal_padding", "width", "expected=4",
                               "actual=8"}) &&
               pass;
    }

    std::cout << "manifest_guard: " << (pass ? "11/11 PASS" : "FAIL") << '\n';
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
