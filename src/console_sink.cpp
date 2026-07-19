#include "edge_ai_defect/runtime/console_sink.hpp"

#include "result_sink_detail.hpp"

#include <iomanip>
#include <limits>
#include <locale>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status state_error(const char* operation) {
    return Status::failure(ErrorCode::kInvalidArgument,
                           std::string("ConsoleSink cannot ") + operation +
                               " in its current lifecycle state");
}

void write_float(std::ostream& output, float value) {
    output << std::setprecision(std::numeric_limits<float>::max_digits10) << value;
}

void write_double(std::ostream& output, double value) {
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << value;
}

}  // namespace

ConsoleSink::ConsoleSink(std::ostream& output) : output_(output) {
    output_.imbue(std::locale::classic());
}

core::Status ConsoleSink::begin_run(const RunMetadata& metadata) {
    if (state_ != State::kReady) {
        return state_error("begin_run");
    }
    const Status validation_status = detail::validate_metadata(metadata);
    if (!validation_status.ok()) {
        return validation_status;
    }
    try {
        output_ << "RUN backend=" << metadata.backend_type
                << " model=" << metadata.model_filename << '\n';
    } catch (const std::exception& exception) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink begin_run write failed: " +
                                   std::string(exception.what()));
    }
    if (!output_) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink begin_run write failed");
    }
    metadata_ = metadata;
    state_ = State::kActive;
    return Status::success();
}

core::Status ConsoleSink::write_frame(const FrameResult& frame) {
    if (state_ != State::kActive) {
        return state_error("write_frame");
    }
    const Status validation_status =
        detail::validate_frame(frame, metadata_, received_frames_);
    if (!validation_status.ok()) {
        return validation_status;
    }
    try {
        output_ << "IMAGE index=" << frame.sequence_index
                << " path=" << frame.relative_path.generic_string()
                << " width=" << frame.image_width
                << " height=" << frame.image_height
                << " detections=" << frame.detections.size();
        if (frame.timings.has_value()) {
            output_ << " source_ms="; write_double(output_, frame.timings->source_ms);
            output_ << " preprocess_ms="; write_double(output_, frame.timings->preprocess_ms);
            output_ << " inference_ms="; write_double(output_, frame.timings->inference_ms);
            output_ << " postprocess_ms="; write_double(output_, frame.timings->postprocess_ms);
            output_ << " pre_sink_total_ms="; write_double(output_, frame.timings->pre_sink_total_ms);
        }
        output_ << '\n';
        for (const postprocess::Detection& detection : frame.detections) {
            output_ << "DETECTION class_id=" << detection.class_id << " confidence=";
            write_float(output_, detection.confidence);
            output_ << " x1="; write_float(output_, detection.x1);
            output_ << " y1="; write_float(output_, detection.y1);
            output_ << " x2="; write_float(output_, detection.x2);
            output_ << " y2="; write_float(output_, detection.y2);
            output_ << " candidate_index=" << detection.candidate_index << '\n';
        }
    } catch (const std::exception& exception) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink write_frame write failed: " +
                                   std::string(exception.what()));
    }
    if (!output_) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink write_frame write failed");
    }
    ++received_frames_;
    received_detections_ += frame.detections.size();
    return Status::success();
}

core::Status ConsoleSink::end_run(const RunSummary& summary) {
    if (state_ != State::kActive) {
        return state_error("end_run");
    }
    const Status validation_status =
        detail::validate_summary(summary, received_frames_, received_detections_);
    if (!validation_status.ok()) {
        return validation_status;
    }
    try {
        output_ << "SUMMARY processed_images=" << summary.processed_images
                << " total_detections=" << summary.total_detections << '\n';
    } catch (const std::exception& exception) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink end_run write failed: " +
                                   std::string(exception.what()));
    }
    if (!output_) {
        return Status::failure(ErrorCode::kIoError,
                               "ConsoleSink end_run write failed");
    }
    state_ = State::kCompleted;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
