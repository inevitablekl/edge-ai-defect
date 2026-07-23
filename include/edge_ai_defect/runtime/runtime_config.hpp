#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace edge_ai_defect::runtime {

struct OnnxRuntimeConfig {
    std::string execution_mode;
    std::string graph_optimization_level;
    std::uint32_t intra_op_threads = 0;
    std::uint32_t inter_op_threads = 0;
    bool intra_op_allow_spinning = false;
    bool inter_op_allow_spinning = false;
    bool cpu_arena_enabled = false;
    bool memory_pattern_enabled = false;
};

struct RuntimeConfig {
    std::uint32_t schema_version = 0;

    std::string backend_type;

    std::filesystem::path model_contract_path;
    std::filesystem::path model_path;

    std::string input_type;
    std::filesystem::path input_directory;

    std::filesystem::path output_json_path;
    bool output_console = false;
    bool output_overwrite = false;

    postprocess::PostprocessConfig postprocess_config;

    bool timing_enabled = false;

    OnnxRuntimeConfig onnxruntime;
    std::uint32_t opencv_num_threads = 0;
};

class RuntimeConfigLoader {
public:
    [[nodiscard]] static core::Status load(
        const std::filesystem::path& config_path,
        RuntimeConfig* output);
};

}  // namespace edge_ai_defect::runtime
