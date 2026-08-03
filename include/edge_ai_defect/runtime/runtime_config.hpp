#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace edge_ai_defect::runtime {

enum class DataPathVariant { kV0, kV2, kV3, kV4, kV2R, kV3R };
enum class ProfilingMode { kOff, kDiagnostic, kFormal };

[[nodiscard]] const char* data_path_variant_name(DataPathVariant value) noexcept;
[[nodiscard]] const char* profiling_mode_name(ProfilingMode value) noexcept;

struct OnnxRuntimeConfig {
    std::string execution_mode = "sequential";
    std::string graph_optimization_level = "all";
    std::uint32_t intra_op_threads = 1;
    std::uint32_t inter_op_threads = 1;
    bool intra_op_allow_spinning = true;
    bool inter_op_allow_spinning = true;
    bool cpu_arena_enabled = true;
    bool memory_pattern_enabled = true;
};

struct TensorRtConfig {
    std::filesystem::path engine_path;
    std::filesystem::path engine_manifest_path;
    std::uint32_t device_id = 0;
};

struct RuntimeConfig {
    std::uint32_t schema_version = 0;

    // v5 derives these values as V0/off. v6 accepts the explicit closed enums.
    DataPathVariant data_path_variant = DataPathVariant::kV0;
    ProfilingMode profiling_mode = ProfilingMode::kOff;

    std::string backend_type;

    std::filesystem::path model_contract_path;
    std::filesystem::path model_path;

    std::string input_type;
    std::filesystem::path input_directory;
    std::filesystem::path input_video_path;

    std::string runtime_mode;
    struct PipelineConfig {
        std::uint32_t queue_capacity = 0;
        std::string drop_policy;
    } pipeline;

    std::filesystem::path output_json_path;
    bool output_console = false;
    bool output_overwrite = false;

    postprocess::PostprocessConfig postprocess_config;

    bool timing_enabled = false;

    OnnxRuntimeConfig onnxruntime;
    TensorRtConfig tensorrt;
    std::uint32_t opencv_num_threads = 1;

    // Phase 0.5D protocol metadata is parsed here so the dedicated harness
    // and the normal YAML loader share one configuration identity. These
    // values do not alter runner or backend execution semantics.
    struct Phase0_5DConfig {
        std::string execution_mode;
        std::uint32_t warmup_frames = 0;
        std::uint32_t measured_frames = 0;
        std::uint32_t input_size = 0;
        std::uint32_t batch = 0;
        std::uint32_t repetitions = 0;
        std::string schedule_id;
        std::string result_root;
        std::string cpu_affinity;
        std::uint32_t opencv_threads = 0;
        std::string timing_boundary_id;
        std::string sink_id;
        std::string serialization_id;
        std::string digest_id;
    } phase0_5d;
};

class RuntimeConfigLoader {
public:
    [[nodiscard]] static core::Status load(
        const std::filesystem::path& config_path,
        RuntimeConfig* output);
};

}  // namespace edge_ai_defect::runtime
