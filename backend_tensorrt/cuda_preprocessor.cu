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

const char* resize_semantic_name(ResizeSemantic value) noexcept {
    switch (value) {
        case ResizeSemantic::kHistoricalV2V3:
            return "historical_v2_v3_resize";
        case ResizeSemantic::kOpenCv454AlignedFixedContract:
            return "opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1";
    }
    return "unknown";
}

namespace {

constexpr float kNormalization = 1.0F / 255.0F;
constexpr float kPaddingNormalized = 114.0F / 255.0F;
constexpr int kResizeCoefficientBits = 11;
constexpr int kResizeCoefficientScale = 1 << kResizeCoefficientBits;

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
    // OpenCV's 8-bit INTER_LINEAR path quantizes resize coefficients to
    // 11-bit fixed point.  Keep the first remediation deliberately local to
    // coefficient precision; separable horizontal/vertical execution is not
    // attempted here.
    const int x_alpha = __float2int_rn(
        static_cast<float>(source_x - x0_unclamped) *
        static_cast<float>(kResizeCoefficientScale));
    const int y_alpha = __float2int_rn(
        static_cast<float>(source_y - y0_unclamped) *
        static_cast<float>(kResizeCoefficientScale));
    const int x_weight_0 = kResizeCoefficientScale - x_alpha;
    const int y_weight_0 = kResizeCoefficientScale - y_alpha;

    const int x0 = max(0, min(x0_unclamped, original_width - 1));
    const int x1 = max(0, min(x0_unclamped + 1, original_width - 1));
    const int y0 = max(0, min(y0_unclamped, original_height - 1));
    const int y1 = max(0, min(y0_unclamped + 1, original_height - 1));

    const std::int64_t top =
        static_cast<std::int64_t>(raw_pixel(raw, row_stride, y0, x0, channel)) *
            x_weight_0 +
        static_cast<std::int64_t>(raw_pixel(raw, row_stride, y0, x1, channel)) *
            x_alpha;
    const std::int64_t bottom =
        static_cast<std::int64_t>(raw_pixel(raw, row_stride, y1, x0, channel)) *
            x_weight_0 +
        static_cast<std::int64_t>(raw_pixel(raw, row_stride, y1, x1, channel)) *
            x_alpha;
    const std::int64_t weighted = top * y_weight_0 + bottom * y_alpha;
    constexpr std::int64_t kRounding =
        static_cast<std::int64_t>(1) << (kResizeCoefficientBits * 2 - 1);
    return static_cast<float>((weighted + kRounding) >>
                              (kResizeCoefficientBits * 2));
}

__device__ int opencv_resize_coefficient(float value) {
    // OpenCV 4.5.4 stores each CV_8U INTER_LINEAR coefficient independently
    // at INTER_RESIZE_COEF_BITS precision.  This is a fixed implementation
    // detail of the bounded contract, not a runtime-selectable mode.
    return __float2int_rn(value * static_cast<float>(kResizeCoefficientScale));
}

__device__ float read_opencv_454_aligned_channel(const std::uint8_t* raw,
                                                std::size_t row_stride,
                                                int original_width,
                                                int original_height,
                                                int resized_width,
                                                int resized_height,
                                                int x,
                                                int y,
                                                int channel) {
    // Fixed contract: CV_8UC3 BGR, current letterbox dimensions, and the
    // OpenCV C++ 4.5.4 uint8 INTER_LINEAR mapping.  This is intentionally a
    // narrow GPU implementation and does not copy a general OpenCV resize.
    const float source_x = static_cast<float>(
        (static_cast<double>(x) + 0.5) *
            static_cast<double>(original_width) /
            static_cast<double>(resized_width) -
        0.5);
    const float source_y = static_cast<float>(
        (static_cast<double>(y) + 0.5) *
            static_cast<double>(original_height) /
            static_cast<double>(resized_height) -
        0.5);
    const int x_unclamped = static_cast<int>(floorf(source_x));
    const int y_unclamped = static_cast<int>(floorf(source_y));
    float x_fraction = source_x - static_cast<float>(x_unclamped);
    const float y_fraction = source_y - static_cast<float>(y_unclamped);
    int x0 = x_unclamped;
    const bool y_is_edge = y_unclamped < 0 || y_unclamped >= original_height - 1;
    const int y0 = max(0, min(y_unclamped, original_height - 1));
    if (x0 < 0) {
        x0 = 0;
        x_fraction = 0.0F;
    } else if (x0 >= original_width - 1) {
        x0 = original_width - 1;
        x_fraction = 0.0F;
    }
    const int x1 = min(x0 + 1, original_width - 1);
    const int y1 = y_is_edge ? y0 : min(y0 + 1, original_height - 1);
    const int x_weight_0 = opencv_resize_coefficient(1.0F - x_fraction);
    const int x_weight_1 = opencv_resize_coefficient(x_fraction);
    const int y_weight_0 = opencv_resize_coefficient(1.0F - y_fraction);
    const int y_weight_1 = opencv_resize_coefficient(y_fraction);
    const bool x_is_edge = x_unclamped < 0 || x_unclamped >= original_width - 1;

    const std::int64_t top = x_is_edge
        ? static_cast<std::int64_t>(raw_pixel(raw, row_stride, y0, x0, channel)) *
              kResizeCoefficientScale
        : static_cast<std::int64_t>(raw_pixel(raw, row_stride, y0, x0, channel)) *
                  x_weight_0 +
              static_cast<std::int64_t>(raw_pixel(raw, row_stride, y0, x1, channel)) *
                  x_weight_1;
    const std::int64_t bottom = x_is_edge
        ? static_cast<std::int64_t>(raw_pixel(raw, row_stride, y1, x0, channel)) *
              kResizeCoefficientScale
        : static_cast<std::int64_t>(raw_pixel(raw, row_stride, y1, x0, channel)) *
                  x_weight_0 +
              static_cast<std::int64_t>(raw_pixel(raw, row_stride, y1, x1, channel)) *
                  x_weight_1;
    // OpenCV 4.5.4's aarch64 CV_8U vector path keeps the horizontal fixed
    // point product at 11 bits, discards its low four bits, then performs the
    // two vertical products and the final two-bit rounding.  Keeping this
    // order is the bounded platform contract used by the Jetson reference.
    const std::int64_t horizontal_top = top >> 4;
    const std::int64_t horizontal_bottom = bottom >> 4;
    const std::int64_t value =
        (((static_cast<std::int64_t>(y_weight_0) * horizontal_top) >> 16) +
         ((static_cast<std::int64_t>(y_weight_1) * horizontal_bottom) >> 16) +
         2) >> 2;
    const std::int64_t clamped = value < 0 ? 0 : (value > 255 ? 255 : value);
    return static_cast<float>(clamped);
}

__device__ float read_resize_channel(const std::uint8_t* raw,
                                     std::size_t row_stride,
                                     int original_width,
                                     int original_height,
                                     int resized_width,
                                     int resized_height,
                                     int x,
                                     int y,
                                     int channel,
                                     ResizeSemantic semantic) {
    if (semantic == ResizeSemantic::kOpenCv454AlignedFixedContract) {
        return read_opencv_454_aligned_channel(raw, row_stride, original_width,
                                               original_height, resized_width,
                                               resized_height, x, y, channel);
    }
    return read_bilinear_channel(raw, row_stride, original_width, original_height,
                                 resized_width, resized_height, x, y, channel);
}

__global__ void preprocess_kernel(const std::uint8_t* raw,
                                  std::size_t row_stride,
                                  DeviceGeometry geometry,
                                  ResizeSemantic semantic,
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
            bgr[channel] = read_resize_channel(
                raw,
                row_stride,
                geometry.original_width,
                geometry.original_height,
                geometry.resized_width,
                geometry.resized_height,
                resized_x,
                resized_y,
                channel,
                semantic);
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
    std::unique_ptr<CudaPreprocessor>* output,
    ResizeSemantic semantic) {
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
                             true, true, nullptr, nullptr, semantic));
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
    std::unique_ptr<CudaPreprocessor>* output,
    ResizeSemantic semantic) {
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
                             false, false, stream, device_tensor, semantic));
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
        device_raw_, max_row_stride_, device_geometry, semantic_, device_tensor_);
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
