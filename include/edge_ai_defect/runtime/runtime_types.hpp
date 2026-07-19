#pragma once

#include "edge_ai_defect/postprocess/detection.hpp"
#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

namespace edge_ai_defect::runtime {

struct FrameTimings {
    double source_ms = 0.0;
    double preprocess_ms = 0.0;
    double inference_ms = 0.0;
    double postprocess_ms = 0.0;
    double pre_sink_total_ms = 0.0;
};

struct RunMetadata {
    std::uint32_t schema_version = 0;
    std::string backend_type;

    std::string model_filename;
    std::string model_sha256;
    std::string contract_filename;

    std::vector<std::string> class_names;
    postprocess::PostprocessConfig postprocess_config;

    bool timing_enabled = false;
};

struct FrameResult {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;

    int image_width = 0;
    int image_height = 0;

    std::vector<postprocess::Detection> detections;
    std::optional<FrameTimings> timings;
};

struct RunSummary {
    std::size_t processed_images = 0;
    std::size_t total_detections = 0;
};

}  // namespace edge_ai_defect::runtime
