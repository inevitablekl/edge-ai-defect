#pragma once

#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <cstdint>
#include <filesystem>

namespace edge_ai_defect::runtime {

struct PacketDimensions {
    int width = 0;
    int height = 0;
};

struct PacketTimestamps {
    std::uint64_t source_begin_ns = 0;
    std::uint64_t source_end_ns = 0;
    std::uint64_t preprocess_begin_ns = 0;
    std::uint64_t preprocess_end_ns = 0;
    std::uint64_t inference_begin_ns = 0;
    std::uint64_t inference_end_ns = 0;
    std::uint64_t postprocess_begin_ns = 0;
    std::uint64_t postprocess_end_ns = 0;
};

struct PacketQueueResidence {
    double source_to_preprocess_wait_ms = 0.0;
    double preprocess_to_inference_wait_ms = 0.0;
    double inference_to_postprocess_wait_ms = 0.0;
};

struct SourcePacket {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    PacketDimensions dimensions;
    PacketTimestamps timestamps;
    cv::Mat image_bgr;
};

struct PreprocessedPacket {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    PacketDimensions dimensions;
    PacketTimestamps timestamps;
    preprocess::ImageTransformMetadata transform;
    core::HostTensor input;
    PacketQueueResidence queue_residence;
};

struct InferencePacket {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    PacketDimensions dimensions;
    PacketTimestamps timestamps;
    preprocess::ImageTransformMetadata transform;
    core::HostTensor raw_output;
    PacketQueueResidence queue_residence;
};

}  // namespace edge_ai_defect::runtime
