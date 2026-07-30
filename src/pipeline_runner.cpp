#include "edge_ai_defect/runtime/pipeline_runner.hpp"

#include <chrono>
#include <cmath>
#include <limits>
#include <mutex>
#include <optional>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

using Clock = std::chrono::steady_clock;
using core::ErrorCode;
using core::Status;

std::uint64_t ns(Clock::time_point value) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(value.time_since_epoch()).count());
}

double ms(Clock::time_point begin, Clock::time_point end) {
    return std::chrono::duration<double, std::milli>(end - begin).count();
}

struct SourcePacket {
    ImageItem item;
    std::uint64_t source_begin_ns = 0;
    std::uint64_t source_end_ns = 0;
};

struct PreprocessPacket {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    cv::Mat image_bgr;
    preprocess::PreprocessedFrame value;
    FrameTimings timings;
};

struct InferencePacket {
    std::size_t sequence_index = 0;
    std::filesystem::path relative_path;
    cv::Mat image_bgr;
    preprocess::PreprocessedFrame preprocessed;
    core::HostTensor raw_output;
    FrameTimings timings;
};

struct FailureState {
    mutable std::mutex mutex;
    bool failed = false;
    Status status = Status::success();

    void record(const std::string& stage, const Status& value, std::size_t sequence = 0,
                const std::filesystem::path* path = nullptr) {
        std::lock_guard<std::mutex> lock(mutex);
        if (failed) return;
        failed = true;
        std::string message = stage;
        if (path != nullptr) {
            message += " sequence_index=" + std::to_string(sequence) +
                       " relative_path=" + path->generic_string();
        }
        message += ": " + value.message();
        status = Status::failure(value.code(), std::move(message));
    }

    [[nodiscard]] bool is_failed() const {
        std::lock_guard<std::mutex> lock(mutex);
        return failed;
    }

    [[nodiscard]] Status result() const {
        std::lock_guard<std::mutex> lock(mutex);
        return status;
    }
};

struct SharedQueues {
    explicit SharedQueues(std::size_t capacity) : q1(capacity), q2(capacity), q3(capacity) {}
    BoundedQueue<SourcePacket> q1;
    BoundedQueue<PreprocessPacket> q2;
    BoundedQueue<InferencePacket> q3;
};

void cancel_all(SharedQueues& queues) {
    queues.q1.cancel();
    queues.q2.cancel();
    queues.q3.cancel();
}

struct WorkerContext {
    SharedQueues& queues;
    FailureState& failure;
    IFrameTraceObserver* trace;

    void fail(const std::string& stage, const Status& status, std::size_t sequence = 0,
              const std::filesystem::path* path = nullptr) {
        failure.record(stage, status, sequence, path);
        cancel_all(queues);
    }
};

Status trace_begin(IFrameTraceObserver* observer, std::size_t cycle, FrameTraceStage stage) {
    return observer == nullptr
               ? Status::success()
               : observer->on_stage_begin(cycle, stage, ns(Clock::now()));
}

Status trace_end(IFrameTraceObserver* observer, std::size_t cycle, FrameTraceStage stage) {
    return observer == nullptr
               ? Status::success()
               : observer->on_stage_end(cycle, stage, ns(Clock::now()));
}

bool valid_timing(const FrameTimings& timing) {
    return std::isfinite(timing.source_ms) && timing.source_ms >= 0.0 &&
           std::isfinite(timing.preprocess_ms) && timing.preprocess_ms >= 0.0 &&
           std::isfinite(timing.inference_ms) && timing.inference_ms >= 0.0 &&
           std::isfinite(timing.postprocess_ms) && timing.postprocess_ms >= 0.0 &&
           std::isfinite(timing.pre_sink_total_ms) && timing.pre_sink_total_ms >= 0.0;
}

}  // namespace

PipelineRunner::PipelineRunner(ImageSource& source,
                               preprocess::Preprocessor& preprocessor,
                               const core::TensorInfo& model_input_info,
                               inference::IInferenceEngine& engine,
                               postprocess::PostProcessor& postprocessor,
                               IResultSink& sink,
                               std::uint32_t queue_capacity,
                               IFrameTraceObserver* trace_observer)
    : source_(source),
      preprocessor_(preprocessor),
      model_input_info_(model_input_info),
      engine_(engine),
      postprocessor_(postprocessor),
      sink_(sink),
      queue_capacity_(queue_capacity),
      trace_observer_(trace_observer) {}

core::Status PipelineRunner::run(const RunMetadata& metadata, RunSummary* summary) {
    if (summary == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument, "PipelineRunner summary must not be null");
    }
    if (queue_capacity_ == 0) {
        return Status::failure(ErrorCode::kInvalidArgument, "PipelineRunner queue capacity must be positive");
    }

    const Status begin_status = sink_.begin_run(metadata);
    if (!begin_status.ok()) return Status::failure(begin_status.code(), "sink.begin_run: " + begin_status.message());

    SharedQueues queues(queue_capacity_);
    FailureState failure;
    WorkerContext context{queues, failure, trace_observer_};
    std::size_t source_frames = 0;
    std::size_t processed_images = 0;
    std::size_t total_detections = 0;
    const auto run_begin = Clock::now();

    auto source_worker = [&] {
        try {
            std::size_t cycle = 0;
            while (!failure.is_failed()) {
                const auto source_begin = Clock::now();
                if (!trace_begin(context.trace, cycle, FrameTraceStage::kSource).ok()) {
                    context.fail("trace.source.begin", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"));
                    break;
                }
                std::optional<ImageItem> item;
                const Status status = source_.next(&item);
                const auto source_end = Clock::now();
                if (!trace_end(context.trace, cycle, FrameTraceStage::kSource).ok()) {
                    context.fail("trace.source.end", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"));
                    break;
                }
                if (!status.ok()) { context.fail("source", status); break; }
                if (!item.has_value()) { queues.q1.close(); break; }
                ++source_frames;
                SourcePacket packet{std::move(*item), ns(source_begin), ns(source_end)};
                if (queues.q1.push(std::move(packet)) != QueuePushResult::PUSHED) break;
                ++cycle;
            }
        } catch (const std::exception& error) {
            context.fail("source worker", Status::failure(ErrorCode::kBackendRuntimeError, error.what()));
        }
        if (failure.is_failed()) queues.q1.cancel();
    };

    auto preprocess_worker = [&] {
        try {
            while (true) {
                auto received = queues.q1.pop();
                if (received.status == QueuePopStatus::CANCELLED) break;
                if (received.status == QueuePopStatus::EOS) { queues.q2.close(); break; }
                SourcePacket packet = std::move(received.item->value);
                const std::size_t cycle = packet.item.sequence_index;
                const auto begin = Clock::now();
                if (!trace_begin(context.trace, cycle, FrameTraceStage::kPreprocess).ok()) {
                    context.fail("trace.preprocess.begin", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.item.relative_path); break;
                }
                preprocess::PreprocessedFrame value;
                const Status status = preprocessor_.preprocess(packet.item.image_bgr, model_input_info_, &value);
                const auto end = Clock::now();
                if (!trace_end(context.trace, cycle, FrameTraceStage::kPreprocess).ok()) {
                    context.fail("trace.preprocess.end", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.item.relative_path); break;
                }
                if (!status.ok()) { context.fail("preprocess", status, cycle, &packet.item.relative_path); break; }
                PreprocessPacket output;
                output.sequence_index = packet.item.sequence_index;
                output.relative_path = packet.item.relative_path;
                output.image_bgr = std::move(packet.item.image_bgr);
                output.value = std::move(value);
                output.timings.source_ms = ms(Clock::time_point(std::chrono::nanoseconds(packet.source_begin_ns)),
                                              Clock::time_point(std::chrono::nanoseconds(packet.source_end_ns)));
                output.timings.preprocess_ms = ms(begin, end);
                output.timings.pipeline_queue = PipelineQueueTimings{};
                output.timings.pipeline_queue->source_to_preprocess_wait_ms =
                    static_cast<double>(std::max<std::uint64_t>(0, ns(begin) - received.item->enqueued_ns)) / 1.0e6;
                if (queues.q2.push(std::move(output)) != QueuePushResult::PUSHED) break;
            }
        } catch (const std::exception& error) {
            context.fail("preprocess worker", Status::failure(ErrorCode::kBackendRuntimeError, error.what()));
        }
        if (failure.is_failed()) queues.q2.cancel();
    };

    auto inference_worker = [&] {
        try {
            while (true) {
                auto received = queues.q2.pop();
                if (received.status == QueuePopStatus::CANCELLED) break;
                if (received.status == QueuePopStatus::EOS) { queues.q3.close(); break; }
                PreprocessPacket packet = std::move(received.item->value);
                const auto begin = Clock::now();
                const std::size_t cycle = packet.sequence_index;
                if (!trace_begin(context.trace, cycle, FrameTraceStage::kInference).ok()) {
                    context.fail("trace.inference.begin", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                core::HostTensor raw_output;
                const Status status = engine_.run(packet.value.tensor, &raw_output);
                const auto end = Clock::now();
                if (!trace_end(context.trace, cycle, FrameTraceStage::kInference).ok()) {
                    context.fail("trace.inference.end", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                if (!status.ok()) { context.fail("inference", status, cycle, &packet.relative_path); break; }
                InferencePacket output;
                output.sequence_index = packet.sequence_index;
                output.relative_path = packet.relative_path;
                output.image_bgr = std::move(packet.image_bgr);
                output.preprocessed = std::move(packet.value);
                output.raw_output = std::move(raw_output);
                output.timings = packet.timings;
                output.timings.inference_ms = ms(begin, end);
                output.timings.pipeline_queue->preprocess_to_inference_wait_ms =
                    static_cast<double>(std::max<std::uint64_t>(0, ns(begin) - received.item->enqueued_ns)) / 1.0e6;
                if (queues.q3.push(std::move(output)) != QueuePushResult::PUSHED) break;
            }
        } catch (const std::exception& error) {
            context.fail("inference worker", Status::failure(ErrorCode::kBackendRuntimeError, error.what()));
        }
        if (failure.is_failed()) queues.q3.cancel();
    };

    auto postprocess_worker = [&] {
        try {
            while (true) {
                auto received = queues.q3.pop();
                if (received.status == QueuePopStatus::CANCELLED) break;
                if (received.status == QueuePopStatus::EOS) break;
                InferencePacket packet = std::move(received.item->value);
                const auto begin = Clock::now();
                const std::size_t cycle = packet.sequence_index;
                if (!trace_begin(context.trace, cycle, FrameTraceStage::kPostprocess).ok()) {
                    context.fail("trace.postprocess.begin", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                std::vector<postprocess::Detection> detections;
                const Status status = postprocessor_.process(packet.raw_output, packet.preprocessed.transform, &detections);
                const auto end = Clock::now();
                if (!trace_end(context.trace, cycle, FrameTraceStage::kPostprocess).ok()) {
                    context.fail("trace.postprocess.end", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                if (!status.ok()) { context.fail("postprocess", status, cycle, &packet.relative_path); break; }
                FrameResult frame;
                frame.sequence_index = packet.sequence_index;
                frame.relative_path = packet.relative_path;
                frame.image_width = packet.image_bgr.cols;
                frame.image_height = packet.image_bgr.rows;
                frame.detections = std::move(detections);
                packet.timings.postprocess_ms = ms(begin, end);
                packet.timings.pre_sink_total_ms = packet.timings.source_ms + packet.timings.preprocess_ms + packet.timings.inference_ms + packet.timings.postprocess_ms;
                if (metadata.timing_enabled) {
                    if (!valid_timing(packet.timings)) { context.fail("timing", Status::failure(ErrorCode::kInvalidArgument, "measured duration is invalid"), cycle, &packet.relative_path); break; }
                    frame.timings = packet.timings;
                }
                const auto sink_begin = Clock::now();
                if (!trace_begin(context.trace, cycle, FrameTraceStage::kSink).ok()) {
                    context.fail("trace.sink.begin", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                const Status sink_status = sink_.write_frame(frame);
                if (!trace_end(context.trace, cycle, FrameTraceStage::kSink).ok()) {
                    context.fail("trace.sink.end", Status::failure(ErrorCode::kBackendRuntimeError, "trace callback failed"), cycle, &packet.relative_path); break;
                }
                if (!sink_status.ok()) { context.fail("sink.write_frame", sink_status, cycle, &packet.relative_path); break; }
                ++processed_images;
                total_detections += frame.detections.size();
                (void)sink_begin;
            }
        } catch (const std::exception& error) {
            context.fail("postprocess worker", Status::failure(ErrorCode::kBackendRuntimeError, error.what()));
        }
    };

    std::vector<std::thread> workers;
    try {
        workers.emplace_back(source_worker);
        workers.emplace_back(preprocess_worker);
        workers.emplace_back(inference_worker);
        workers.emplace_back(postprocess_worker);
    } catch (const std::system_error& error) {
        context.fail("thread creation", Status::failure(ErrorCode::kBackendRuntimeError, error.what()));
    }
    for (std::thread& worker : workers) if (worker.joinable()) worker.join();

    if (failure.is_failed()) return failure.result();
    if (processed_images == 0) {
        return Status::failure(ErrorCode::kInvalidArgument, "source: end of stream before any image");
    }
    RunSummary staged;
    staged.processed_images = processed_images;
    staged.total_detections = total_detections;
    if (metadata.runtime_v3.has_value()) {
        staged.runtime_v3 = RunSummaryV3{};
        staged.runtime_v3->source_frames = source_frames;
        staged.runtime_v3->run_processing_wall_ms = ms(run_begin, Clock::now());
        staged.runtime_v3->pipeline = PipelineSummaryV3{{queues.q1.statistics().high_water_mark,
                                                         queues.q2.statistics().high_water_mark,
                                                         queues.q3.statistics().high_water_mark}};
    }
    const Status end_status = sink_.end_run(staged);
    if (!end_status.ok()) return Status::failure(end_status.code(), "sink.end_run: " + end_status.message());
    *summary = staged;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
