#include "result_sink_detail.hpp"

#include "edge_ai_defect/postprocess/postprocess_config.hpp"

#include <cmath>
#include <iomanip>
#include <limits>
#include <locale>
#include <sstream>

namespace edge_ai_defect::runtime::detail {
namespace {

using core::ErrorCode;
using core::Status;

bool is_lowercase_sha256(const std::string& value) {
    if (value.size() != 64U) {
        return false;
    }
    for (const char character : value) {
        if (!((character >= '0' && character <= '9') ||
              (character >= 'a' && character <= 'f'))) {
            return false;
        }
    }
    return true;
}

bool is_filename(const std::string& value) {
    return !value.empty() && value.find('/') == std::string::npos &&
           value.find('\\') == std::string::npos;
}

bool finite_detection(const postprocess::Detection& detection) {
    return std::isfinite(detection.x1) && std::isfinite(detection.y1) &&
           std::isfinite(detection.x2) && std::isfinite(detection.y2) &&
           std::isfinite(detection.confidence);
}

bool finite_timing(const FrameTimings& timing) {
    return std::isfinite(timing.source_ms) && timing.source_ms >= 0.0 &&
           std::isfinite(timing.preprocess_ms) && timing.preprocess_ms >= 0.0 &&
           std::isfinite(timing.inference_ms) && timing.inference_ms >= 0.0 &&
           std::isfinite(timing.postprocess_ms) && timing.postprocess_ms >= 0.0 &&
           std::isfinite(timing.pre_sink_total_ms) &&
               timing.pre_sink_total_ms >= 0.0 &&
           (!timing.pipeline_queue.has_value() ||
            (std::isfinite(timing.pipeline_queue->source_to_preprocess_wait_ms) &&
             timing.pipeline_queue->source_to_preprocess_wait_ms >= 0.0 &&
             std::isfinite(timing.pipeline_queue->preprocess_to_inference_wait_ms) &&
             timing.pipeline_queue->preprocess_to_inference_wait_ms >= 0.0 &&
             std::isfinite(timing.pipeline_queue->inference_to_postprocess_wait_ms) &&
             timing.pipeline_queue->inference_to_postprocess_wait_ms >= 0.0));
}

void write_float(std::ostream& output, float value) {
    output << std::setprecision(std::numeric_limits<float>::max_digits10) << value;
}

void write_double(std::ostream& output, double value) {
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << value;
}

void write_detection(std::ostream& output, const postprocess::Detection& detection,
                     const std::string& indent) {
    output << indent << "{\n";
    output << indent << "  \"x1\": "; write_float(output, detection.x1); output << ",\n";
    output << indent << "  \"y1\": "; write_float(output, detection.y1); output << ",\n";
    output << indent << "  \"x2\": "; write_float(output, detection.x2); output << ",\n";
    output << indent << "  \"y2\": "; write_float(output, detection.y2); output << ",\n";
    output << indent << "  \"confidence\": "; write_float(output, detection.confidence); output << ",\n";
    output << indent << "  \"class_id\": " << detection.class_id << ",\n";
    output << indent << "  \"candidate_index\": " << detection.candidate_index << "\n";
    output << indent << "}";
}

void write_timing(std::ostream& output, const FrameTimings& timing,
                  const std::string& indent) {
    output << indent << "\"timing_ms\": {\n";
    output << indent << "  \"source\": "; write_double(output, timing.source_ms); output << ",\n";
    output << indent << "  \"preprocess\": "; write_double(output, timing.preprocess_ms); output << ",\n";
    output << indent << "  \"inference\": "; write_double(output, timing.inference_ms); output << ",\n";
    output << indent << "  \"postprocess\": "; write_double(output, timing.postprocess_ms); output << ",\n";
    output << indent << "  \"pre_sink_total\": "; write_double(output, timing.pre_sink_total_ms);
    if (timing.pipeline_queue.has_value()) {
        output << ",\n" << indent << "  \"queue_residence\": {\n"
               << indent << "    \"source_to_preprocess\": ";
        write_double(output, timing.pipeline_queue->source_to_preprocess_wait_ms);
        output << ",\n" << indent << "    \"preprocess_to_inference\": ";
        write_double(output, timing.pipeline_queue->preprocess_to_inference_wait_ms);
        output << ",\n" << indent << "    \"inference_to_postprocess\": ";
        write_double(output, timing.pipeline_queue->inference_to_postprocess_wait_ms);
        output << "\n" << indent << "  }\n";
    } else {
        output << "\n";
    }
    output << indent << "}";
}

}  // namespace

core::Status validate_metadata(const RunMetadata& metadata) {
    const bool trt_v2 = metadata.schema_version == 2U &&
                        metadata.backend_type == "tensorrt_fp16";
    const bool trt_v3 = metadata.schema_version == 3U &&
                        metadata.backend_type == "tensorrt_fp16";
    if (metadata.schema_version != 1U && !trt_v2 && !trt_v3) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "RunMetadata schema_version must be 1, TensorRT v2, or Result v3");
    }
    if (metadata.backend_type != "onnxruntime_cpu" && !trt_v2 && !trt_v3) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "RunMetadata backend_type is unsupported");
    }
    if (!is_filename(metadata.model_filename) || !is_filename(metadata.contract_filename)) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunMetadata model and contract must be filenames");
    }
    if (!is_lowercase_sha256(metadata.model_sha256)) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunMetadata model_sha256 must be lowercase SHA256");
    }
    if ((trt_v2 || trt_v3) && (metadata.artifact_kind != "tensorrt_engine" ||
                   !is_lowercase_sha256(metadata.source_onnx_sha256) ||
                   !is_filename(metadata.engine_manifest_filename))) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "TensorRT metadata is incomplete or invalid");
    }
    if (metadata.schema_version == 3U) {
        if (!metadata.runtime_v3.has_value())
            return Status::failure(ErrorCode::kSchemaViolation, "Result v3 requires runtime metadata");
        const auto& runtime = *metadata.runtime_v3;
        if ((runtime.runtime_mode != "serial" && runtime.runtime_mode != "pipeline") ||
            (runtime.input_type != "directory" && runtime.input_type != "video_file"))
            return Status::failure(ErrorCode::kSchemaViolation, "Result v3 runtime metadata is invalid");
        if ((runtime.runtime_mode == "pipeline") != runtime.pipeline.has_value())
            return Status::failure(ErrorCode::kSchemaViolation, "Result v3 pipeline metadata mismatch");
        if (runtime.pipeline.has_value() &&
            (runtime.pipeline->queue_capacity == 0U || runtime.pipeline->queue_capacity > 16U ||
             runtime.pipeline->drop_policy != "block"))
            return Status::failure(ErrorCode::kSchemaViolation, "Result v3 pipeline metadata is invalid");
    }
    if (metadata.class_names.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunMetadata class_names must not be empty");
    }
    for (const std::string& class_name : metadata.class_names) {
        if (class_name.empty()) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "RunMetadata class names must not be empty");
        }
    }
    const Status config_status = postprocess::validate_postprocess_config(
        metadata.postprocess_config);
    if (!config_status.ok()) {
        return Status::failure(config_status.code(),
                               "RunMetadata postprocess: " + config_status.message());
    }
    return Status::success();
}

core::Status validate_frame(const FrameResult& frame,
                            const RunMetadata& metadata,
                            std::size_t expected_sequence_index) {
    if (frame.sequence_index != expected_sequence_index) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "FrameResult sequence_index must be contiguous from 0");
    }
    if (frame.relative_path.empty() || frame.relative_path.is_absolute()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "FrameResult relative_path must be non-empty and relative");
    }
    for (const auto& component : frame.relative_path) {
        if (component == "..") {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "FrameResult relative_path must not traverse parent");
        }
    }
    if (frame.image_width <= 0 || frame.image_height <= 0) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "FrameResult image dimensions must be positive");
    }
    for (const postprocess::Detection& detection : frame.detections) {
        if (!finite_detection(detection)) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "FrameResult Detection values must be finite");
        }
        if (detection.class_id < 0 ||
            static_cast<std::size_t>(detection.class_id) >= metadata.class_names.size()) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "FrameResult Detection class_id is outside class_names");
        }
    }
    if (metadata.timing_enabled != frame.timings.has_value()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "FrameResult timings must match RunMetadata timing_enabled");
    }
    if (frame.timings.has_value() && !finite_timing(*frame.timings)) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "FrameResult timing values must be finite and non-negative");
    }
    if (metadata.schema_version < 3U && frame.timings.has_value() &&
        frame.timings->pipeline_queue.has_value())
        return Status::failure(ErrorCode::kSchemaViolation, "pipeline queue timing requires Result v3");
    if (metadata.schema_version == 3U && metadata.runtime_v3.has_value() &&
        metadata.runtime_v3->runtime_mode == "pipeline" && metadata.timing_enabled &&
        (!frame.timings.has_value() || !frame.timings->pipeline_queue.has_value()))
        return Status::failure(ErrorCode::kSchemaViolation,
                               "Result v3 pipeline timing requires queue residence");
    if (metadata.schema_version == 3U && metadata.runtime_v3.has_value() &&
        metadata.runtime_v3->runtime_mode == "serial" && frame.timings.has_value() &&
        frame.timings->pipeline_queue.has_value())
        return Status::failure(ErrorCode::kSchemaViolation,
                               "Result v3 serial timing forbids queue residence");
    return Status::success();
}

core::Status validate_summary(const RunSummary& summary,
                              const RunMetadata& metadata,
                              std::size_t received_frames,
                              std::size_t received_detections) {
    if (summary.processed_images != received_frames ||
        summary.total_detections != received_detections) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunSummary counts do not match received frames");
    }
    // Schema v1/v2: runtime_v3 must be absent
    if (metadata.schema_version < 3U && summary.runtime_v3.has_value()) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "Result v1/v2 forbid runtime summary metadata");
    }
    // Schema v3: runtime_v3 is required
    if (metadata.schema_version == 3U) {
        if (!summary.runtime_v3.has_value()) {
            return Status::failure(ErrorCode::kSchemaViolation,
                                   "Result v3 requires runtime summary metadata");
        }
        const auto& value = *summary.runtime_v3;
        // Block-only: source_frames == processed_images, dropped == 0
        if (value.source_frames != summary.processed_images) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "Result v3 block-only: source_frames must equal processed_images");
        }
        if (value.source_frames < summary.processed_images) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "source_frames must not be less than processed_images");
        }
        if (!std::isfinite(value.run_processing_wall_ms) || value.run_processing_wall_ms <= 0.0) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "run processing wall time must be finite and positive");
        }
        // Throughput must be finite
        const double throughput = static_cast<double>(summary.processed_images) /
                                  (value.run_processing_wall_ms / 1000.0);
        if (!std::isfinite(throughput)) {
            return Status::failure(ErrorCode::kInvalidArgument,
                                   "derived throughput must be finite");
        }
        // Mode matching
        if (!metadata.runtime_v3.has_value()) {
            return Status::failure(ErrorCode::kSchemaViolation,
                                   "Result v3 summary validation requires metadata runtime_v3");
        }
        const auto& rt_meta = *metadata.runtime_v3;
        if ((rt_meta.runtime_mode == "pipeline") != value.pipeline.has_value()) {
            return Status::failure(ErrorCode::kSchemaViolation,
                                   "Result v3 runtime mode and summary pipeline mismatch");
        }
        if (value.pipeline.has_value() && rt_meta.pipeline.has_value()) {
            // queue_high_water_mark <= queue_capacity
            for (std::size_t i = 0; i < 3; ++i) {
                if (value.pipeline->queue_high_water_marks[i] > rt_meta.pipeline->queue_capacity) {
                    return Status::failure(ErrorCode::kSchemaViolation,
                                           "queue high water mark exceeds capacity");
                }
            }
        }
        if (rt_meta.runtime_mode == "serial" && value.pipeline.has_value()) {
            return Status::failure(ErrorCode::kSchemaViolation,
                                   "serial summary must not carry pipeline metadata");
        }
    }
    return Status::success();
}

std::string json_escape(const std::string& value) {
    std::ostringstream output;
    output.imbue(std::locale::classic());
    for (const unsigned char character : value) {
        switch (character) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (character < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2) << std::setfill('0')
                           << static_cast<unsigned int>(character) << std::dec
                           << std::setfill(' ');
                } else {
                    output << static_cast<char>(character);
                }
                break;
        }
    }
    return output.str();
}

std::string serialize_run(const RunMetadata& metadata,
                          const std::vector<FrameResult>& frames,
                          const RunSummary& summary) {
    std::ostringstream output;
    output.imbue(std::locale::classic());
    const bool tensorrt_result =
        metadata.schema_version == 2U || metadata.schema_version == 3U;
    const bool result_v3 = metadata.schema_version == 3U;
    output << "{\n"
           << "  \"schema_version\": " << metadata.schema_version << ",\n"
           << "  \"backend\": {\n"
           << "    \"type\": \"" << json_escape(metadata.backend_type) << "\"\n"
           << "  },\n"
           << "  \"model\": {\n";
    if (tensorrt_result) {
        output << "    \"artifact_kind\": \"" << json_escape(metadata.artifact_kind) << "\",\n";
    }
    output << "    \"filename\": \"" << json_escape(metadata.model_filename) << "\",\n"
           << "    \"sha256\": \"" << json_escape(metadata.model_sha256) << "\",\n";
    if (tensorrt_result) {
        output << "    \"source_onnx_sha256\": \"" << json_escape(metadata.source_onnx_sha256) << "\",\n"
               << "    \"engine_manifest_filename\": \"" << json_escape(metadata.engine_manifest_filename) << "\",\n";
    }
    output << "    \"contract_filename\": \"" << json_escape(metadata.contract_filename) << "\",\n"
           << "    \"classes\": [\n";
    for (std::size_t index = 0; index < metadata.class_names.size(); ++index) {
        output << "      \"" << json_escape(metadata.class_names[index]) << "\""
               << (index + 1U == metadata.class_names.size() ? "\n" : ",\n");
    }
    output << "    ]\n"
           << "  },\n";
    if (result_v3) {
        output << "  \"runtime\": {\n"
               << "    \"mode\": \"" << json_escape(metadata.runtime_v3->runtime_mode) << "\",\n"
               << "    \"input_type\": \"" << json_escape(metadata.runtime_v3->input_type) << "\"";
        if (metadata.runtime_v3->pipeline.has_value()) {
            output << ",\n    \"pipeline\": {\n"
                   << "      \"queue_capacity\": " << metadata.runtime_v3->pipeline->queue_capacity << ",\n"
                   << "      \"drop_policy\": \"" << json_escape(metadata.runtime_v3->pipeline->drop_policy) << "\"\n"
                   << "    }";
        }
        output << "\n  },\n";
    }
    output << "  \"postprocess\": {\n"
           << "    \"confidence_threshold\": "; write_float(output, metadata.postprocess_config.confidence_threshold); output << ",\n";
    output << "    \"iou_threshold\": "; write_float(output, metadata.postprocess_config.iou_threshold); output << ",\n";
    output << "    \"max_nms\": " << metadata.postprocess_config.max_nms << ",\n"
           << "    \"max_det\": " << metadata.postprocess_config.max_det << ",\n"
           << "    \"max_wh\": "; write_float(output, metadata.postprocess_config.max_wh); output << ",\n";
    output << "    \"agnostic\": " << (metadata.postprocess_config.agnostic ? "true" : "false") << ",\n"
           << "    \"multi_label\": " << (metadata.postprocess_config.multi_label ? "true" : "false") << "\n"
           << "  },\n"
           << "  \"images\": [\n";
    for (std::size_t index = 0; index < frames.size(); ++index) {
        const FrameResult& frame = frames[index];
        output << "    {\n"
               << "      \"sequence_index\": " << frame.sequence_index << ",\n"
               << "      \"relative_path\": \"" << json_escape(frame.relative_path.generic_string()) << "\",\n"
               << "      \"width\": " << frame.image_width << ",\n"
               << "      \"height\": " << frame.image_height << ",\n"
               << "      \"detections\": [\n";
        for (std::size_t detection_index = 0; detection_index < frame.detections.size(); ++detection_index) {
            write_detection(output, frame.detections[detection_index], "        ");
            output << (detection_index + 1U == frame.detections.size() ? "\n" : ",\n");
        }
        output << "      ]";
        if (frame.timings.has_value()) {
            output << ",\n";
            write_timing(output, *frame.timings, "      ");
            output << "\n";
        } else {
            output << "\n";
        }
        output << "    }" << (index + 1U == frames.size() ? "\n" : ",\n");
    }
    output << "  ],\n"
           << "  \"summary\": {\n";
    if (result_v3) {
        const auto& value = *summary.runtime_v3;
        const double throughput = static_cast<double>(summary.processed_images) /
                                  (value.run_processing_wall_ms / 1000.0);
        output << "    \"processed_frames\": " << summary.processed_images << ",\n"
               << "    \"total_detections\": " << summary.total_detections << ",\n"
               << "    \"source_frames\": " << value.source_frames << ",\n"
               << "    \"dropped_frames\": " << (value.source_frames - summary.processed_images) << ",\n"
               << "    \"run_processing_wall_ms\": ";
        write_double(output, value.run_processing_wall_ms);
        output << ",\n    \"run_processing_throughput_fps\": ";
        write_double(output, throughput);
        if (value.pipeline.has_value()) {
            output << ",\n    \"queue_high_water_marks\": {\n"
                   << "      \"source_to_preprocess\": " << value.pipeline->queue_high_water_marks[0] << ",\n"
                   << "      \"preprocess_to_inference\": " << value.pipeline->queue_high_water_marks[1] << ",\n"
                   << "      \"inference_to_postprocess\": " << value.pipeline->queue_high_water_marks[2] << "\n"
                   << "    }\n";
        } else {
            output << "\n";
        }
    } else {
        output << "    \"processed_images\": " << summary.processed_images << ",\n"
               << "    \"total_detections\": " << summary.total_detections << "\n";
    }
    output << "  }\n"
           << "}\n";
    return output.str();
}

}  // namespace edge_ai_defect::runtime::detail
