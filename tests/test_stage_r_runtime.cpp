#include "edge_ai_defect/runtime/diagnostic_sampling.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>

namespace {
namespace runtime = edge_ai_defect::runtime;
void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }

std::string v6(const std::string& variant, const std::string& mode) {
    return "schema_version: 6\nbackend:\n  type: tensorrt_int8\n"
           "tensorrt:\n  engine_path: engine.plan\n  engine_manifest_path: engine.json\n  device_id: 0\n"
           "model:\n  contract_path: contract.yaml\nruntime:\n  mode: pipeline\n  opencv_num_threads: 1\n"
           "  pipeline:\n    queue_capacity: 1\n    drop_policy: block\n"
           "input:\n  type: directory\n  directory: images\n"
           "output:\n  json_path: result.json\n  console: false\n  overwrite: false\n"
           "postprocess:\n  conf_threshold: 0.25\n  iou_threshold: 0.45\n  max_nms: 30000\n  max_det: 300\n  max_wh: 7680\n  agnostic: false\n"
           "timing:\n  enabled: true\ndata_path:\n  variant: " + variant +
           "\nprofiling:\n  mode: " + mode + "\n";
}

std::string v5() {
    std::string text = v6("V0", "off");
    text.replace(text.find("schema_version: 6"), 18, "schema_version: 5\n");
    const auto data = text.find("data_path:\n");
    text.erase(data);
    return text;
}

void test_config() {
    const auto root = std::filesystem::temp_directory_path() / "stage_r_runtime_test";
    std::filesystem::remove_all(root);
    std::filesystem::create_directories(root);
    for (const auto& [name, text, variant, mode] : {
        std::tuple<std::string, std::string, runtime::DataPathVariant, runtime::ProfilingMode>{
            "v5", v5(), runtime::DataPathVariant::kV0, runtime::ProfilingMode::kOff},
        {"v6off", v6("V0", "off"), runtime::DataPathVariant::kV0, runtime::ProfilingMode::kOff},
        {"v6diag", v6("V0", "diagnostic"), runtime::DataPathVariant::kV0, runtime::ProfilingMode::kDiagnostic},
        {"v6formal", v6("V0", "formal"), runtime::DataPathVariant::kV0, runtime::ProfilingMode::kFormal},
        {"v6v2", v6("V2", "off"), runtime::DataPathVariant::kV2, runtime::ProfilingMode::kOff}}) {
        const auto path = root / (name + ".yaml");
        std::ofstream(path) << text;
        runtime::RuntimeConfig config;
        const auto status = runtime::RuntimeConfigLoader::load(path, &config);
        if (!status.ok()) throw std::runtime_error(name + ": " + status.message());
        require(config.data_path_variant == variant, "variant mismatch");
        require(config.profiling_mode == mode, "profiling mode mismatch");
    }
    const auto bad = root / "bad.yaml";
    std::ofstream(bad) << v6("V9", "off");
    runtime::RuntimeConfig ignored;
    require(!runtime::RuntimeConfigLoader::load(bad, &ignored).ok(), "invalid variant accepted");
    std::ofstream(bad) << v6("V0", "trace");
    require(!runtime::RuntimeConfigLoader::load(bad, &ignored).ok(), "invalid mode accepted");
    std::ofstream(bad) << v6("V0", "off") + "profiling:\n  mode: off\n";
    require(!runtime::RuntimeConfigLoader::load(bad, &ignored).ok(), "duplicate field accepted");
    std::filesystem::remove_all(root);
}

void test_sampling() {
    bool seen[180] = {};
    std::size_t count = 0;
    for (std::size_t cycle = 0; cycle < 10; ++cycle) {
        for (std::size_t position = 0; position < 180; ++position) {
            if (runtime::should_sample_diagnostic(position, cycle)) {
                require(!seen[position], "duplicate sample position");
                seen[position] = true; ++count;
            }
        }
    }
    require(count == 180, "sample count mismatch");
    for (bool value : seen) require(value, "missing sample position");
}
}

int main() {
    try { test_config(); test_sampling(); std::cout << "Stage R runtime tests passed\n"; return 0; }
    catch (const std::exception& error) { std::cerr << "Stage R runtime test failed: " << error.what() << '\n'; return 1; }
}
