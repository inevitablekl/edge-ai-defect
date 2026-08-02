#include "stage_r/double_buffer_runner.hpp"

#include "backend_tensorrt/cuda_preprocessor.hpp"
#include "backend_tensorrt/pinned_raw_staging.hpp"
#include "edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp"

#include <cuda_runtime_api.h>
#include <openssl/evp.h>

#include <array>
#include <chrono>
#include <cstring>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

namespace edge_ai_defect::stage_r {
namespace {
constexpr std::size_t kMaxStagingBytes = 4096U * 4096U * 3U;

std::string sha256(const std::vector<float>& values) {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (ctx == nullptr || EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) != 1) {
        if (ctx != nullptr) EVP_MD_CTX_free(ctx);
        return {};
    }
    EVP_DigestUpdate(ctx, values.data(), values.size() * sizeof(float));
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0U;
    const bool ok = EVP_DigestFinal_ex(ctx, digest, &length) == 1;
    EVP_MD_CTX_free(ctx);
    if (!ok) return {};
    std::ostringstream out;
    out << std::hex;
    for (unsigned int i = 0; i < length; ++i) {
        out.width(2);
        out.fill('0');
        out << static_cast<unsigned int>(digest[i]);
    }
    return out.str();
}
}  // namespace

DoubleBufferRunner::DoubleBufferRunner(runtime::ImageSource& source,
                                       backend_tensorrt::TensorRtEngine& engine,
                                       postprocess::PostProcessor& postprocessor,
                                       runtime::IResultSink& sink)
    : source_(source), engine_(engine), postprocessor_(postprocessor), sink_(sink) {}

core::Status DoubleBufferRunner::run(const runtime::RunMetadata& metadata,
                                     runtime::RunSummary* summary,
                                     V4RunStats* stats) {
    if (summary == nullptr || stats == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "V4 summary and stats must not be null");
    }
    *summary = {};
    *stats = {};
    core::Status status = sink_.begin_run(metadata);
    if (!status.ok()) return status;

    std::array<PinnedRawStaging, 2> raw;
    for (auto& slot : raw) {
        status = slot.allocate(kMaxStagingBytes);
        if (!status.ok()) return status;
        ++stats->allocation_count;
    }
    std::array<void*, 2> input_slots{engine_.device_input_buffer(), nullptr};
    status = core::Status::success();
    if (cudaMalloc(&input_slots[1], engine_.device_input_bytes()) != cudaSuccess) {
        return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                     "V4 second TensorRT input slot allocation failed");
    }
    ++stats->allocation_count;
    struct DeviceGuard {
        void* pointer = nullptr;
        ~DeviceGuard() { if (pointer != nullptr) cudaFree(pointer); }
    } second_input{input_slots[1]};

    std::array<std::unique_ptr<CudaPreprocessor>, 2> preprocessors;
    for (std::size_t i = 0; i < preprocessors.size(); ++i) {
        status = CudaPreprocessor::create_for_external_tensor(
            4096, 4096, static_cast<std::size_t>(4096) * 3U,
            reinterpret_cast<cudaStream_t>(engine_.cuda_stream_handle()),
            static_cast<float*>(input_slots[i]), &preprocessors[i]);
        if (!status.ok()) return status;
        ++stats->allocation_count;
    }

    std::vector<float> tensor(CudaPreprocessor::kTargetElementCount);
    std::vector<std::byte> digest_bytes;
    digest_bytes.reserve(180U * tensor.size() * sizeof(float));
    std::size_t frame_index = 0U;
    const auto run_begin = std::chrono::steady_clock::now();
    for (;;) {
        std::optional<runtime::ImageItem> item;
        status = source_.next(&item);
        if (!status.ok()) return status;
        if (!item.has_value()) break;
        const std::size_t slot_index = frame_index % 2U;
        if (frame_index >= 2U) ++stats->reuse_count;
        auto& staging = raw[slot_index];
        status = staging.prepare(item->image_bgr);
        if (!status.ok()) return status;
        preprocess::ImageTransformMetadata geometry;
        status = CudaPreprocessor::compute_geometry(staging.width(), staging.height(), &geometry);
        if (!status.ok()) return status;
        status = preprocessors[slot_index]->preprocess(
            staging.data(), staging.width(), staging.height(),
            staging.packed_row_bytes(), geometry);
        if (!status.ok()) return status;
        status = preprocessors[slot_index]->copy_output_to_host(tensor.data(), tensor.size());
        if (!status.ok()) return status;
        const auto* bytes = reinterpret_cast<const std::byte*>(tensor.data());
        digest_bytes.insert(digest_bytes.end(), bytes, bytes + tensor.size() * sizeof(float));
        ++stats->synchronization_count;

        core::HostTensor output;
        status = engine_.run_device_input_slot(input_slots[slot_index],
                                               engine_.device_input_bytes(), &output);
        if (!status.ok()) return status;
        ++stats->synchronization_count;
        std::vector<postprocess::Detection> detections;
        status = postprocessor_.process(output, geometry, &detections);
        if (!status.ok()) return status;
        runtime::FrameResult frame;
        frame.sequence_index = item->sequence_index;
        frame.relative_path = item->relative_path;
        frame.image_width = item->image_bgr.cols;
        frame.image_height = item->image_bgr.rows;
        frame.detections = std::move(detections);
        status = sink_.write_frame(frame);
        if (!status.ok()) return status;
        ++summary->processed_images;
        summary->total_detections += frame.detections.size();
        ++frame_index;
    }
    if (metadata.runtime_v3.has_value()) {
        summary->runtime_v3 = runtime::RunSummaryV3{};
        summary->runtime_v3->source_frames = frame_index;
        summary->runtime_v3->run_processing_wall_ms =
            std::chrono::duration<double, std::milli>(
                std::chrono::steady_clock::now() - run_begin).count();
        if (metadata.runtime_v3->pipeline.has_value()) {
            summary->runtime_v3->pipeline = runtime::PipelineSummaryV3{{0, 0, 0}};
        }
    }
    status = sink_.end_run(*summary);
    if (!status.ok()) return status;
    stats->processed_frames = frame_index;
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (ctx == nullptr || EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) != 1) {
        if (ctx != nullptr) EVP_MD_CTX_free(ctx);
        return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                     "V4 tensor digest initialization failed");
    }
    EVP_DigestUpdate(ctx, digest_bytes.data(), digest_bytes.size());
    unsigned char digest[EVP_MAX_MD_SIZE] = {};
    unsigned int length = 0U;
    const bool ok = EVP_DigestFinal_ex(ctx, digest, &length) == 1;
    EVP_MD_CTX_free(ctx);
    if (!ok) return core::Status::failure(core::ErrorCode::kBackendRuntimeError,
                                          "V4 tensor digest finalization failed");
    std::ostringstream out;
    out << std::hex;
    for (unsigned int i = 0; i < length; ++i) { out.width(2); out.fill('0'); out << static_cast<unsigned int>(digest[i]); }
    stats->tensor_digest_sha256 = out.str();
    return core::Status::success();
}

}  // namespace edge_ai_defect::stage_r
