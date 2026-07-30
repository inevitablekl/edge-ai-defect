#pragma once

#include "edge_ai_defect/postprocess/detection.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cstddef>
#include <cstdint>
#include <array>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

namespace edge_ai_defect::runtime {

struct PipelineQueueTimings {
    double source_to_preprocess_wait_ms = 0.0;
    double preprocess_to_inference_wait_ms = 0.0;
    double inference_to_postprocess_wait_ms = 0.0;
};

struct FrameTimings {
    double source_ms = 0.0;
    double preprocess_ms = 0.0;
    double inference_ms = 0.0;
    double postprocess_ms = 0.0;
    double pre_sink_total_ms = 0.0;
    std::optional<PipelineQueueTimings> pipeline_queue;
};

struct PipelineMetadataV3 {
    std::uint32_t queue_capacity = 0;
    std::string drop_policy;
};

struct RuntimeMetadataV3 {
    std::string runtime_mode;
    std::string input_type;
    std::optional<PipelineMetadataV3> pipeline;
};

struct RunMetadata {
    std::uint32_t schema_version = 0;
    std::string backend_type;

    std::string model_filename;
    std::string model_sha256;
    std::string contract_filename;
    std::string artifact_kind;
    std::string source_onnx_sha256;
    std::string engine_manifest_filename;

    std::vector<std::string> class_names;
    postprocess::PostprocessConfig postprocess_config;

    bool timing_enabled = false;
    std::optional<RuntimeMetadataV3> runtime_v3;
};

struct FrameResult {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;

    int image_width = 0;
    int image_height = 0;

    std::vector<postprocess::Detection> detections;
    std::optional<FrameTimings> timings;
};

struct PipelineSummaryV3 {
    std::array<std::size_t, 3> queue_high_water_marks{0, 0, 0};
};

struct RunSummaryV3 {
    std::size_t source_frames = 0;
    double run_processing_wall_ms = 0.0;
    std::optional<PipelineSummaryV3> pipeline;
};

struct RunSummary {
    std::size_t processed_images = 0;
    std::size_t total_detections = 0;
    std::optional<RunSummaryV3> runtime_v3;
};

}  // namespace edge_ai_defect::runtime
