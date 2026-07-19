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
               timing.pre_sink_total_ms >= 0.0;
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
    output << indent << "  \"pre_sink_total\": "; write_double(output, timing.pre_sink_total_ms); output << "\n";
    output << indent << "}";
}

}  // namespace

core::Status validate_metadata(const RunMetadata& metadata) {
    if (metadata.schema_version != 1U) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "RunMetadata schema_version must be 1");
    }
    if (metadata.backend_type != "onnxruntime_cpu") {
        return Status::failure(ErrorCode::kSchemaViolation,
                               "RunMetadata backend_type must be onnxruntime_cpu");
    }
    if (!is_filename(metadata.model_filename) || !is_filename(metadata.contract_filename)) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunMetadata model and contract must be filenames");
    }
    if (!is_lowercase_sha256(metadata.model_sha256)) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunMetadata model_sha256 must be lowercase SHA256");
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
    return Status::success();
}

core::Status validate_summary(const RunSummary& summary,
                              std::size_t received_frames,
                              std::size_t received_detections) {
    if (summary.processed_images != received_frames ||
        summary.total_detections != received_detections) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "RunSummary counts do not match received frames");
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
    output << "{\n"
           << "  \"schema_version\": 1,\n"
           << "  \"backend\": {\n"
           << "    \"type\": \"" << json_escape(metadata.backend_type) << "\"\n"
           << "  },\n"
           << "  \"model\": {\n"
           << "    \"filename\": \"" << json_escape(metadata.model_filename) << "\",\n"
           << "    \"sha256\": \"" << json_escape(metadata.model_sha256) << "\",\n"
           << "    \"contract_filename\": \"" << json_escape(metadata.contract_filename) << "\",\n"
           << "    \"classes\": [\n";
    for (std::size_t index = 0; index < metadata.class_names.size(); ++index) {
        output << "      \"" << json_escape(metadata.class_names[index]) << "\""
               << (index + 1U == metadata.class_names.size() ? "\n" : ",\n");
    }
    output << "    ]\n"
           << "  },\n"
           << "  \"postprocess\": {\n"
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
           << "  \"summary\": {\n"
           << "    \"processed_images\": " << summary.processed_images << ",\n"
           << "    \"total_detections\": " << summary.total_detections << "\n"
           << "  }\n"
           << "}\n";
    return output.str();
}

}  // namespace edge_ai_defect::runtime::detail
