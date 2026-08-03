#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/preprocess/letterbox.hpp"

#include <cuda_runtime_api.h>

#include <cstddef>
#include <cstdint>
#include <memory>

namespace edge_ai_defect::stage_r {

enum class ResizeSemantic {
    kHistoricalV2V3,
    kOpenCv454AlignedFixedContract,
};

[[nodiscard]] const char* resize_semantic_name(ResizeSemantic value) noexcept;

struct DeviceTensorView {
    const float* data = nullptr;
    std::size_t element_count = 0U;
    int batch = 1;
    int channels = 3;
    int height = 640;
    int width = 640;
};

// Stage R R2.1-only CUDA preprocessing foundation.  This class owns the
// persistent raw and output device buffers and exactly one CUDA stream.  It
// intentionally has no TensorRT, inference, postprocess, or result-sink API.
class CudaPreprocessor final {
public:
    static constexpr int kTargetWidth = 640;
    static constexpr int kTargetHeight = 640;
    static constexpr int kTargetChannels = 3;
    static constexpr std::size_t kTargetElementCount =
        static_cast<std::size_t>(kTargetChannels) *
        static_cast<std::size_t>(kTargetHeight) *
        static_cast<std::size_t>(kTargetWidth);

    // max_row_stride is the largest host row stride accepted by preprocess.
    // All device allocations and the stream are made here, never per frame.
    [[nodiscard]] static core::Status create(
        int max_width,
        int max_height,
        std::size_t max_row_stride,
        std::unique_ptr<CudaPreprocessor>* output,
        ResizeSemantic semantic = ResizeSemantic::kHistoricalV2V3);

    [[nodiscard]] static core::Status create_for_external_tensor(
        int max_width,
        int max_height,
        std::size_t max_row_stride,
        cudaStream_t stream,
        float* device_tensor,
        std::unique_ptr<CudaPreprocessor>* output,
        ResizeSemantic semantic = ResizeSemantic::kHistoricalV2V3);

    ~CudaPreprocessor() noexcept;

    CudaPreprocessor(const CudaPreprocessor&) = delete;
    CudaPreprocessor& operator=(const CudaPreprocessor&) = delete;
    CudaPreprocessor(CudaPreprocessor&&) = delete;
    CudaPreprocessor& operator=(CudaPreprocessor&&) = delete;

    // Reuses the existing CPU geometry helper.  This function only computes
    // metadata; it does not allocate or launch CUDA work.
    [[nodiscard]] static core::Status compute_geometry(
        int width,
        int height,
        preprocess::ImageTransformMetadata* output);

    // bgr_host is a host uint8 BGR image with row_stride bytes per row.
    // Geometry must have been produced by compute_geometry (or the equivalent
    // existing CPU helper) for the same width and height.
    [[nodiscard]] core::Status preprocess(
        const std::uint8_t* bgr_host,
        int width,
        int height,
        std::size_t row_stride,
        const preprocess::ImageTransformMetadata& geometry);

    [[nodiscard]] core::Status synchronize() const;

    // Copies the most recently produced output to caller-owned host storage.
    // The caller supplies storage for exactly kTargetElementCount floats.
    [[nodiscard]] core::Status copy_output_to_host(
        float* host_output,
        std::size_t element_count) const;

    [[nodiscard]] DeviceTensorView device_tensor() const noexcept;
    [[nodiscard]] cudaStream_t stream() const noexcept { return stream_; }
    [[nodiscard]] std::size_t max_row_stride() const noexcept {
        return max_row_stride_;
    }

private:
    CudaPreprocessor(int max_width,
                     int max_height,
                     std::size_t max_row_stride,
                     bool owns_stream,
                     bool owns_tensor,
                     cudaStream_t stream,
                     float* device_tensor,
                     ResizeSemantic semantic) noexcept
        : max_width_(max_width),
          max_height_(max_height),
          max_row_stride_(max_row_stride),
          owns_stream_(owns_stream),
          owns_tensor_(owns_tensor),
          stream_(stream),
          device_tensor_(device_tensor),
          semantic_(semantic) {}

    int max_width_ = 0;
    int max_height_ = 0;
    std::size_t max_row_stride_ = 0U;
    bool owns_stream_ = true;
    bool owns_tensor_ = true;
    std::uint8_t* device_raw_ = nullptr;
    float* device_tensor_ = nullptr;
    cudaStream_t stream_ = nullptr;
    ResizeSemantic semantic_ = ResizeSemantic::kHistoricalV2V3;
};

}  // namespace edge_ai_defect::stage_r
