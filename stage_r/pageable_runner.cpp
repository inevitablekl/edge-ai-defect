#include "stage_r/pageable_runner.hpp"

#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "backend_tensorrt/pageable_raw_staging.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"

#include <chrono>
#include <memory>
#include <optional>
#include <vector>

namespace edge_ai_defect::stage_r {

PageableRunner::PageableRunner(runtime::ImageSource& source,
                               backend_tensorrt::TensorRtEngine& engine,
                               postprocess::PostProcessor& postprocessor,
                               runtime::IResultSink& sink,
                               ResizeSemantic semantic)
    : source_(source), engine_(engine), postprocessor_(postprocessor), sink_(sink),
      semantic_(semantic) {}

core::Status PageableRunner::run(const runtime::RunMetadata& metadata,
                                 runtime::RunSummary* summary) {
    if (summary == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "summary must not be null");
    }
    *summary = {};
    core::Status status = sink_.begin_run(metadata);
    if (!status.ok()) return status;

    // The source is decoded by the existing ImageSource. The largest accepted
    // raw shape is established once; no per-frame CUDA resource is created.
    std::unique_ptr<CudaPreprocessor> cuda_preprocessor;
    status = CudaPreprocessor::create_for_external_tensor(
        4096, 4096, static_cast<std::size_t>(4096) * 3U,
        reinterpret_cast<cudaStream_t>(engine_.cuda_stream_handle()),
        static_cast<float*>(engine_.device_input_buffer()), &cuda_preprocessor,
        semantic_);
    if (!status.ok()) return status;
    PageableRawStaging staging;

    for (;;) {
        std::optional<runtime::ImageItem> item;
        status = source_.next(&item);
        if (!status.ok()) return status;
        if (!item.has_value()) break;
        const cv::Mat& image = item->image_bgr;
        status = staging.prepare(image);
        if (!status.ok()) return status;
        preprocess::ImageTransformMetadata geometry;
        status = CudaPreprocessor::compute_geometry(
            staging.width(), staging.height(), &geometry);
        if (!status.ok()) return status;
        status = cuda_preprocessor->preprocess(
            staging.data(), staging.width(), staging.height(),
            staging.packed_row_bytes(), geometry);
        if (!status.ok()) return status;

        core::HostTensor output;
        status = engine_.run_device_input(engine_.device_input_buffer(),
                                          engine_.device_input_bytes(), &output);
        if (!status.ok()) return status;
        std::vector<postprocess::Detection> detections;
        status = postprocessor_.process(output, geometry, &detections);
        if (!status.ok()) return status;
        runtime::FrameResult frame;
        frame.sequence_index = item->sequence_index;
        frame.relative_path = item->relative_path;
        frame.image_width = image.cols;
        frame.image_height = image.rows;
        frame.detections = std::move(detections);
        status = sink_.write_frame(frame);
        if (!status.ok()) return status;
        ++summary->processed_images;
        summary->total_detections += frame.detections.size();
    }
    return sink_.end_run(*summary);
}

}  // namespace edge_ai_defect::stage_r
