#include "backend_tensorrt/cuda_preprocessor.hpp"

#include "edge_ai_defect/core/tensor.hpp"

#include <cuda_runtime.h>

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <string>

namespace edge_ai_defect::stage_r {
namespace {

constexpr float kNormalization = 1.0F / 255.0F;
constexpr float kPaddingNormalized = 114.0F / 255.0F;

__device__ float raw_pixel(const std::uint8_t* raw,
                           std::size_t row_stride,
                           int sample_y,
                           int sample_x,
                           int channel) {
    return static_cast<float>(raw[static_cast<std::size_t>(sample_y) * row_stride +
                                  static_cast<std::size_t>(sample_x) * 3U +
                                  static_cast<std::size_t>(channel)]);
}

struct DeviceGeometry {
    int original_width;
    int original_height;
    int resized_width;
    int resized_height;
    int pad_left;
    int pad_top;
};

__device__ float read_bilinear_channel(const std::uint8_t* raw,
                                       std::size_t row_stride,
                                       int original_width,
                                       int original_height,
                                       int resized_width,
                                       int resized_height,
                                       int x,
                                       int y,
                                       int channel) {
    // This is the half-pixel mapping used by the existing CPU INTER_LINEAR
    // path.  Dimensions and padding are supplied by CPU geometry; no scale,
    // padding, or rounding decision is recomputed here.
    const double source_x =
        (static_cast<double>(x) + 0.5) *
            static_cast<double>(original_width) /
            static_cast<double>(resized_width) -
        0.5;
    const double source_y =
        (static_cast<double>(y) + 0.5) *
            static_cast<double>(original_height) /
            static_cast<double>(resized_height) -
        0.5;

    const int x0_unclamped = static_cast<int>(floor(source_x));
    const int y0_unclamped = static_cast<int>(floor(source_y));
    const float x_alpha = static_cast<float>(source_x - x0_unclamped);
    const float y_alpha = static_cast<float>(source_y - y0_unclamped);

    const int x0 = max(0, min(x0_unclamped, original_width - 1));
    const int x1 = max(0, min(x0_unclamped + 1, original_width - 1));
    const int y0 = max(0, min(y0_unclamped, original_height - 1));
    const int y1 = max(0, min(y0_unclamped + 1, original_height - 1));

    const float top = raw_pixel(raw, row_stride, y0, x0, channel) *
                          (1.0F - x_alpha) +
                      raw_pixel(raw, row_stride, y0, x1, channel) * x_alpha;
    const float bottom = raw_pixel(raw, row_stride, y1, x0, channel) *
                             (1.0F - x_alpha) +
                         raw_pixel(raw, row_stride, y1, x1, channel) * x_alpha;
    const float interpolated = top * (1.0F - y_alpha) + bottom * y_alpha;
    return static_cast<float>(__float2int_rn(interpolated));
}

__global__ void preprocess_kernel(const std::uint8_t* raw,
                                  std::size_t row_stride,
                                  DeviceGeometry geometry,
                                  float* output) {
    const std::size_t spatial_index =
        static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    constexpr std::size_t kSpatial =
        static_cast<std::size_t>(CudaPreprocessor::kTargetHeight) *
        static_cast<std::size_t>(CudaPreprocessor::kTargetWidth);
    if (spatial_index >= kSpatial) return;

    const int output_y = static_cast<int>(
        spatial_index / static_cast<std::size_t>(CudaPreprocessor::kTargetWidth));
    const int output_x = static_cast<int>(
        spatial_index % static_cast<std::size_t>(CudaPreprocessor::kTargetWidth));
    const bool is_padding =
        output_x < geometry.pad_left ||
        output_x >= geometry.pad_left + geometry.resized_width ||
        output_y < geometry.pad_top ||
        output_y >= geometry.pad_top + geometry.resized_height;

    float bgr[3];
    if (is_padding) {
        output[spatial_index] = kPaddingNormalized;
        output[kSpatial + spatial_index] = kPaddingNormalized;
        output[2U * kSpatial + spatial_index] = kPaddingNormalized;
        return;
    } else {
        const int resized_x = output_x - geometry.pad_left;
        const int resized_y = output_y - geometry.pad_top;
        for (int channel = 0; channel < 3; ++channel) {
            bgr[channel] = read_bilinear_channel(
                raw,
                row_stride,
                geometry.original_width,
                geometry.original_height,
                geometry.resized_width,
                geometry.resized_height,
                resized_x,
                resized_y,
                channel);
        }
    }

    // RGB NCHW from the input BGR order.
    output[spatial_index] = bgr[2] * kNormalization;
    output[kSpatial + spatial_index] = bgr[1] * kNormalization;
    output[2U * kSpatial + spatial_index] = bgr[0] * kNormalization;
}

core::Status cuda_failure(cudaError_t error, const char* operation) {
    if (error == cudaSuccess) return core::Status::success();
    return core::Status::failure(
        core::ErrorCode::kBackendRuntimeError,
        std::string(operation) + ": " + cudaGetErrorString(error));
}

core::Status validate_geometry(
    const preprocess::ImageTransformMetadata& geometry,
    int width,
    int height) {
    if (geometry.original_width != width || geometry.original_height != height) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "CUDA geometry original dimensions do not match the image");
    }
    if (geometry.target_width != CudaPreprocessor::kTargetWidth ||
        geometry.target_height != CudaPreprocessor::kTargetHeight) {
        return core::Status::failure(
            core::ErrorCode::kInvalidShape,
            "CUDA preprocessing requires target geometry 640x640");
    }
    if (!std::isfinite(geometry.gain) || geometry.gain <= 0.0 ||
        geometry.resized_width <= 0 || geometry.resized_height <= 0 ||
        geometry.pad_left < 0 || geometry.pad_right < 0 ||
        geometry.pad_top < 0 || geometry.pad_bottom < 0 ||
        geometry.resized_width + geometry.pad_left + geometry.pad_right !=
            CudaPreprocessor::kTargetWidth ||
        geometry.resized_height + geometry.pad_top + geometry.pad_bottom !=
            CudaPreprocessor::kTargetHeight) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "CUDA geometry metadata is inconsistent");
    }
    return core::Status::success();
}

}  // namespace

core::Status CudaPreprocessor::create(
    int max_width,
    int max_height,
    std::size_t max_row_stride,
    std::unique_ptr<CudaPreprocessor>* output) {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output must not be null");
    }
    if (max_width <= 0 || max_height <= 0 || max_row_stride == 0U ||
        max_row_stride < static_cast<std::size_t>(max_width) * 3U) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "CUDA buffer limits must be positive and row stride must fit width");
    }
    if (static_cast<std::size_t>(max_height) >
        std::numeric_limits<std::size_t>::max() / max_row_stride) {
        return core::Status::failure(core::ErrorCode::kOverflow,
                                     "CUDA raw buffer size overflows size_t");
    }

    auto candidate = std::unique_ptr<CudaPreprocessor>(
        new CudaPreprocessor(max_width, max_height, max_row_stride,
                             true, true, nullptr, nullptr));
    const std::size_t raw_bytes =
        static_cast<std::size_t>(max_height) * max_row_stride;
    cudaError_t error = cudaStreamCreate(&candidate->stream_);
    if (error != cudaSuccess) return cuda_failure(error, "cudaStreamCreate");
    error = cudaMalloc(reinterpret_cast<void**>(&candidate->device_raw_), raw_bytes);
    if (error != cudaSuccess) return cuda_failure(error, "cudaMalloc raw buffer");
    error = cudaMalloc(reinterpret_cast<void**>(&candidate->device_tensor_),
                       kTargetElementCount * sizeof(float));
    if (error != cudaSuccess) return cuda_failure(error, "cudaMalloc tensor buffer");

    *output = std::move(candidate);
    return core::Status::success();
}

core::Status CudaPreprocessor::create_for_external_tensor(
    int max_width, int max_height, std::size_t max_row_stride,
    cudaStream_t stream, float* device_tensor,
    std::unique_ptr<CudaPreprocessor>* output) {
    if (output == nullptr || stream == nullptr || device_tensor == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "external CUDA resources must not be null");
    }
    if (max_width <= 0 || max_height <= 0 || max_row_stride == 0U ||
        max_row_stride < static_cast<std::size_t>(max_width) * 3U ||
        static_cast<std::size_t>(max_height) >
            std::numeric_limits<std::size_t>::max() / max_row_stride) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "invalid external CUDA buffer limits");
    }
    auto candidate = std::unique_ptr<CudaPreprocessor>(
        new CudaPreprocessor(max_width, max_height, max_row_stride,
                             false, false, stream, device_tensor));
    const std::size_t raw_bytes = static_cast<std::size_t>(max_height) * max_row_stride;
    const cudaError_t error = cudaMalloc(reinterpret_cast<void**>(&candidate->device_raw_), raw_bytes);
    if (error != cudaSuccess) return cuda_failure(error, "cudaMalloc raw buffer");
    *output = std::move(candidate);
    return core::Status::success();
}

CudaPreprocessor::~CudaPreprocessor() noexcept {
    if (stream_ != nullptr) (void)cudaStreamSynchronize(stream_);
    if (device_tensor_ != nullptr && owns_tensor_) (void)cudaFree(device_tensor_);
    if (device_raw_ != nullptr) (void)cudaFree(device_raw_);
    if (stream_ != nullptr && owns_stream_) (void)cudaStreamDestroy(stream_);
}

core::Status CudaPreprocessor::compute_geometry(
    int width,
    int height,
    preprocess::ImageTransformMetadata* output) {
    const core::TensorInfo input_info{
        core::TensorDataType::kFloat32,
        core::TensorLayout::kNchw,
        {1, 3, kTargetHeight, kTargetWidth}};
    return preprocess::compute_letterbox_geometry(width, height, input_info, output);
}

core::Status CudaPreprocessor::preprocess(
    const std::uint8_t* bgr_host,
    int width,
    int height,
    std::size_t row_stride,
    const preprocess::ImageTransformMetadata& geometry) {
    if (bgr_host == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "bgr_host must not be null");
    }
    if (width <= 0 || height <= 0 || width > max_width_ || height > max_height_ ||
        row_stride < static_cast<std::size_t>(width) * 3U ||
        row_stride > max_row_stride_) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "image dimensions or row stride exceed CUDA buffer limits");
    }
    const core::Status geometry_status = validate_geometry(geometry, width, height);
    if (!geometry_status.ok()) return geometry_status;

    const std::size_t row_bytes = static_cast<std::size_t>(width) * 3U;
    cudaError_t error = cudaMemcpy2DAsync(device_raw_,
                                          max_row_stride_,
                                          bgr_host,
                                          row_stride,
                                          row_bytes,
                                          static_cast<std::size_t>(height),
                                          cudaMemcpyHostToDevice,
                                          stream_);
    if (error != cudaSuccess) return cuda_failure(error, "cudaMemcpy2DAsync H2D");

    const DeviceGeometry device_geometry{
        geometry.original_width,
        geometry.original_height,
        geometry.resized_width,
        geometry.resized_height,
        geometry.pad_left,
        geometry.pad_top,
    };
    constexpr int kThreads = 256;
    constexpr std::size_t kBlocks =
        (kTargetElementCount / kTargetChannels + kThreads - 1U) / kThreads;
    preprocess_kernel<<<static_cast<unsigned int>(kBlocks), kThreads, 0, stream_>>>(
        device_raw_, max_row_stride_, device_geometry, device_tensor_);
    error = cudaGetLastError();
    return cuda_failure(error, "CUDA preprocessing kernel launch");
}

core::Status CudaPreprocessor::synchronize() const {
    return cuda_failure(cudaStreamSynchronize(stream_), "cudaStreamSynchronize");
}

core::Status CudaPreprocessor::copy_output_to_host(
    float* host_output,
    std::size_t element_count) const {
    if (host_output == nullptr || element_count != kTargetElementCount) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "host output must provide exactly [1,3,640,640] elements");
    }
    const cudaError_t error = cudaMemcpyAsync(host_output,
                                              device_tensor_,
                                              kTargetElementCount * sizeof(float),
                                              cudaMemcpyDeviceToHost,
                                              stream_);
    if (error != cudaSuccess) return cuda_failure(error, "cudaMemcpyAsync D2H");
    return synchronize();
}

DeviceTensorView CudaPreprocessor::device_tensor() const noexcept {
    return {device_tensor_, kTargetElementCount, 1, kTargetChannels,
            kTargetHeight, kTargetWidth};
}

}  // namespace edge_ai_defect::stage_r
