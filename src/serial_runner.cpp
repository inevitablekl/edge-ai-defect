#include "edge_ai_defect/runtime/serial_runner.hpp"

#include <chrono>
#include <cmath>
#include <limits>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

using Clock = std::chrono::steady_clock;
using core::ErrorCode;
using core::Status;

double elapsed_ms(const Clock::time_point& start, const Clock::time_point& end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

Status stage_failure(const char* stage,
                     const Status& status,
                     const ImageItem* item = nullptr) {
    std::string message(stage);
    if (item != nullptr) {
        message += " sequence_index=" + std::to_string(item->sequence_index) +
                   " relative_path=" + item->relative_path.generic_string();
    }
    message += ": " + status.message();
    return Status::failure(status.code(), std::move(message));
}

Status invalid_timing(const ImageItem& item) {
    return Status::failure(ErrorCode::kInvalidArgument,
                           "timing sequence_index=" +
                               std::to_string(item.sequence_index) +
                               " relative_path=" + item.relative_path.generic_string() +
                               ": measured duration must be finite and non-negative");
}

bool timing_is_valid(const FrameTimings& timing) {
    return std::isfinite(timing.source_ms) && timing.source_ms >= 0.0 &&
           std::isfinite(timing.preprocess_ms) && timing.preprocess_ms >= 0.0 &&
           std::isfinite(timing.inference_ms) && timing.inference_ms >= 0.0 &&
           std::isfinite(timing.postprocess_ms) && timing.postprocess_ms >= 0.0 &&
           std::isfinite(timing.pre_sink_total_ms) &&
               timing.pre_sink_total_ms >= 0.0;
}

}  // namespace

SerialRunner::SerialRunner(ImageSource& source,
                           preprocess::Preprocessor& preprocessor,
                           const core::TensorInfo& model_input_info,
                           inference::IInferenceEngine& engine,
                           postprocess::PostProcessor& postprocessor,
                           IResultSink& sink)
    : source_(source),
      preprocessor_(preprocessor),
      model_input_info_(model_input_info),
      engine_(engine),
      postprocessor_(postprocessor),
      sink_(sink) {}

core::Status SerialRunner::run(const RunMetadata& metadata,
                               RunSummary* summary) {
    if (summary == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "SerialRunner summary must not be null");
    }

    RunSummary staged_summary;
    const Status begin_status = sink_.begin_run(metadata);
    if (!begin_status.ok()) {
        return stage_failure("sink.begin_run", begin_status);
    }

    while (true) {
        const Clock::time_point pre_sink_start = Clock::now();
        std::optional<ImageItem> item;
        const Status source_status = source_.next(&item);
        const Clock::time_point source_end = Clock::now();
        if (!source_status.ok()) {
            return stage_failure("source", source_status);
        }
        if (!item.has_value()) {
            break;
        }

        preprocess::PreprocessedFrame preprocessed;
        const Clock::time_point preprocess_start = Clock::now();
        const Status preprocess_status = preprocessor_.preprocess(
            item->image_bgr, model_input_info_, &preprocessed);
        const Clock::time_point preprocess_end = Clock::now();
        if (!preprocess_status.ok()) {
            return stage_failure("preprocess", preprocess_status, &*item);
        }

        core::HostTensor raw_output;
        const Clock::time_point inference_start = Clock::now();
        const Status inference_status = engine_.run(preprocessed.tensor, &raw_output);
        const Clock::time_point inference_end = Clock::now();
        if (!inference_status.ok()) {
            return stage_failure("inference", inference_status, &*item);
        }

        std::vector<postprocess::Detection> detections;
        const Clock::time_point postprocess_start = Clock::now();
        const Status postprocess_status = postprocessor_.process(
            raw_output, preprocessed.transform, &detections);
        const Clock::time_point postprocess_end = Clock::now();
        if (!postprocess_status.ok()) {
            return stage_failure("postprocess", postprocess_status, &*item);
        }

        if (staged_summary.processed_images ==
                std::numeric_limits<std::size_t>::max() ||
            detections.size() >
                std::numeric_limits<std::size_t>::max() -
                    staged_summary.total_detections) {
            return Status::failure(
                ErrorCode::kOverflow,
                "sink.write_frame sequence_index=" +
                    std::to_string(item->sequence_index) + " relative_path=" +
                    item->relative_path.generic_string() +
                    ": RunSummary count would overflow");
        }

        FrameResult frame;
        frame.sequence_index = item->sequence_index;
        frame.relative_path = item->relative_path;
        frame.image_width = item->image_bgr.cols;
        frame.image_height = item->image_bgr.rows;
        frame.detections = std::move(detections);
        if (metadata.timing_enabled) {
            FrameTimings timing;
            timing.source_ms = elapsed_ms(pre_sink_start, source_end);
            timing.preprocess_ms = elapsed_ms(preprocess_start, preprocess_end);
            timing.inference_ms = elapsed_ms(inference_start, inference_end);
            timing.postprocess_ms = elapsed_ms(postprocess_start, postprocess_end);
            timing.pre_sink_total_ms = elapsed_ms(pre_sink_start, postprocess_end);
            if (!timing_is_valid(timing)) {
                return invalid_timing(*item);
            }
            frame.timings = timing;
        }

        const Status write_status = sink_.write_frame(frame);
        if (!write_status.ok()) {
            return stage_failure("sink.write_frame", write_status, &*item);
        }
        ++staged_summary.processed_images;
        staged_summary.total_detections += frame.detections.size();
    }

    if (staged_summary.processed_images == 0U) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "source: end of stream before any image");
    }

    const Status end_status = sink_.end_run(staged_summary);
    if (!end_status.ok()) {
        return stage_failure("sink.end_run", end_status);
    }
    *summary = staged_summary;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
