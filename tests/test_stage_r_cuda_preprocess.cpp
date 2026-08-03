#include "backend_tensorrt/cuda_preprocessor.hpp"

#include "edge_ai_defect/preprocess/preprocessor.hpp"

#include <cuda_runtime_api.h>
#include <opencv2/core.hpp>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace stage_r = edge_ai_defect::stage_r;
namespace preprocess = edge_ai_defect::preprocess;

constexpr double kMaeLimit = 5.0e-4;
constexpr double kP99Limit = 2.0 / 255.0 + 1.0e-6;
constexpr double kMaxLimit = 4.0 / 255.0 + 1.0e-6;

bool check(bool condition, const std::string& name, const std::string& detail = {}) {
    std::cout << name << ": " << (condition ? "PASS" : "FAIL");
    if (!detail.empty()) std::cout << " (" << detail << ')';
    std::cout << '\n';
    return condition;
}

bool has_cuda_device() {
    int count = 0;
    const cudaError_t error = cudaGetDeviceCount(&count);
    if (error != cudaSuccess || count == 0) {
        std::cout << "stage_r_cuda_preprocess: SKIP (CUDA device unavailable: "
                  << cudaGetErrorString(error) << ")\n";
        return false;
    }
    return true;
}

cv::Mat make_input(int width, int height, std::size_t row_stride,
                   std::vector<std::uint8_t>* storage) {
    storage->assign(static_cast<std::size_t>(height) * row_stride, 0U);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const std::size_t offset = static_cast<std::size_t>(y) * row_stride +
                                       static_cast<std::size_t>(x) * 3U;
            (*storage)[offset] = static_cast<std::uint8_t>((x * 17 + y * 3) & 0xff);
            (*storage)[offset + 1U] = static_cast<std::uint8_t>((x * 5 + y * 29) & 0xff);
            (*storage)[offset + 2U] = static_cast<std::uint8_t>((x * 41 + y * 7) & 0xff);
        }
    }
    return cv::Mat(height, width, CV_8UC3, storage->data(), row_stride);
}

bool compare_tensor(const std::vector<float>& actual,
                    const std::vector<float>& expected,
                    double* mae,
                    double* p99,
                    double* max_abs,
                    std::size_t* nonfinite) {
    if (actual.size() != expected.size() || actual.empty()) return false;
    std::vector<double> errors;
    errors.reserve(actual.size());
    double sum = 0.0;
    *max_abs = 0.0;
    *nonfinite = 0U;
    for (std::size_t index = 0; index < actual.size(); ++index) {
        if (!std::isfinite(actual[index]) || !std::isfinite(expected[index])) {
            ++(*nonfinite);
            continue;
        }
        const double error = std::abs(static_cast<double>(actual[index]) -
                                      static_cast<double>(expected[index]));
        sum += error;
        errors.push_back(error);
        *max_abs = std::max(*max_abs, error);
    }
    if (*nonfinite != 0U || errors.size() != actual.size()) {
        *mae = *p99 = *max_abs = std::numeric_limits<double>::infinity();
        return false;
    }
    std::sort(errors.begin(), errors.end());
    const double rank = 0.99 * static_cast<double>(errors.size() - 1U);
    const std::size_t lower = static_cast<std::size_t>(std::floor(rank));
    const std::size_t upper = static_cast<std::size_t>(std::ceil(rank));
    const double fraction = rank - static_cast<double>(lower);
    *mae = sum / static_cast<double>(actual.size());
    *p99 = errors[lower] + fraction * (errors[upper] - errors[lower]);
    return true;
}

int run() {
    if (!has_cuda_device()) return 77;

    constexpr int kWidth = 7;
    constexpr int kHeight = 5;
    constexpr std::size_t kStride = kWidth * 3U + 5U;
    std::vector<std::uint8_t> storage;
    const cv::Mat input = make_input(kWidth, kHeight, kStride, &storage);

    preprocess::ImageTransformMetadata geometry;
    auto status = stage_r::CudaPreprocessor::compute_geometry(
        kWidth, kHeight, &geometry);
    bool pass = check(status.ok(), "cpu_geometry_helper", status.message());
    pass = check(geometry.resized_width == 640 && geometry.resized_height == 457 &&
                     geometry.pad_left == 0 && geometry.pad_top == 91,
                 "non_square_geometry") && pass;

    std::unique_ptr<stage_r::CudaPreprocessor> cuda_preprocessor;
    status = stage_r::CudaPreprocessor::create(
        kWidth, kHeight, kStride, &cuda_preprocessor);
    pass = check(status.ok(), "persistent_resources", status.message()) && pass;
    if (!status.ok()) return 1;

    std::unique_ptr<stage_r::CudaPreprocessor> cuda_remediated;
    status = stage_r::CudaPreprocessor::create(
        kWidth, kHeight, kStride, &cuda_remediated,
        stage_r::ResizeSemantic::kOpenCv454AlignedFixedContract);
    pass = check(status.ok(), "v2r_fixed_contract_resources", status.message()) && pass;
    if (!status.ok()) return 1;
    std::unique_ptr<stage_r::CudaPreprocessor> cuda_pinned_semantic;
    status = stage_r::CudaPreprocessor::create(
        kWidth, kHeight, kStride, &cuda_pinned_semantic,
        stage_r::ResizeSemantic::kOpenCv454AlignedFixedContract);
    pass = check(status.ok(), "v3r_shared_semantic_resources", status.message()) && pass;
    if (!status.ok()) return 1;

    preprocess::PreprocessedFrame cpu_output;
    const edge_ai_defect::core::TensorInfo input_info{
        edge_ai_defect::core::TensorDataType::kFloat32,
        edge_ai_defect::core::TensorLayout::kNchw,
        {1, 3, 640, 640}};
    status = preprocess::Preprocessor().preprocess(input, input_info, &cpu_output);
    pass = check(status.ok(), "cpu_reference", status.message()) && pass;
    if (!status.ok()) return 1;

    status = cuda_preprocessor->preprocess(
        input.data, kWidth, kHeight, input.step, geometry);
    pass = check(status.ok(), "kernel_submission", status.message()) && pass;
    if (!status.ok()) return 1;

    status = cuda_remediated->preprocess(
        input.data, kWidth, kHeight, input.step, geometry);
    pass = check(status.ok(), "v2r_kernel_submission", status.message()) && pass;
    if (!status.ok()) return 1;
    status = cuda_pinned_semantic->preprocess(
        input.data, kWidth, kHeight, input.step, geometry);
    pass = check(status.ok(), "v3r_kernel_submission", status.message()) && pass;
    if (!status.ok()) return 1;

    std::vector<float> cuda_output(stage_r::CudaPreprocessor::kTargetElementCount);
    status = cuda_preprocessor->copy_output_to_host(
        cuda_output.data(), cuda_output.size());
    pass = check(status.ok(), "device_output_copy", status.message()) && pass;
    if (!status.ok()) return 1;
    std::vector<float> v2r_output(stage_r::CudaPreprocessor::kTargetElementCount);
    status = cuda_remediated->copy_output_to_host(v2r_output.data(), v2r_output.size());
    pass = check(status.ok(), "v2r_device_output_copy", status.message()) && pass;
    if (!status.ok()) return 1;
    std::vector<float> v3r_output(stage_r::CudaPreprocessor::kTargetElementCount);
    status = cuda_pinned_semantic->copy_output_to_host(v3r_output.data(), v3r_output.size());
    pass = check(status.ok(), "v3r_device_output_copy", status.message()) && pass;
    if (!status.ok()) return 1;

    double mae = 0.0;
    double p99 = 0.0;
    double max_abs = 0.0;
    std::size_t nonfinite = 0U;
    const bool finite = compare_tensor(cuda_output,
                                       cpu_output.tensor.data,
                                       &mae,
                                       &p99,
                                       &max_abs,
                                       &nonfinite);
    pass = check(finite && mae <= kMaeLimit && p99 <= kP99Limit &&
                     max_abs <= kMaxLimit,
                 "tensor_gate",
                 "mae=" + std::to_string(mae) +
                     " p99=" + std::to_string(p99) +
                     " max=" + std::to_string(max_abs) +
                     " nonfinite=" + std::to_string(nonfinite)) && pass;

    double v2r_mae = 0.0;
    double v2r_p99 = 0.0;
    double v2r_max_abs = 0.0;
    std::size_t v2r_nonfinite = 0U;
    const bool v2r_finite = compare_tensor(v2r_output, cpu_output.tensor.data,
                                           &v2r_mae, &v2r_p99, &v2r_max_abs,
                                           &v2r_nonfinite);
    pass = check(v2r_finite && v2r_mae <= kMaeLimit && v2r_p99 <= kP99Limit &&
                     v2r_max_abs <= kMaxLimit && v2r_nonfinite == 0U,
                 "v2r_tensor_gate",
                 "mae=" + std::to_string(v2r_mae) +
                     " p99=" + std::to_string(v2r_p99) +
                     " max=" + std::to_string(v2r_max_abs)) && pass;
    pass = check(v2r_output == v3r_output, "v2r_v3r_same_semantic") && pass;

    const std::size_t plane = static_cast<std::size_t>(640) * 640U;
    bool padding_pass = true;
    for (int y = 0; y < 640; ++y) {
        for (int x = 0; x < 640; ++x) {
            if (x < geometry.pad_left || x >= geometry.pad_left + geometry.resized_width ||
                y < geometry.pad_top || y >= geometry.pad_top + geometry.resized_height) {
                const std::size_t spatial = static_cast<std::size_t>(y) * 640U + x;
                for (int channel = 0; channel < 3; ++channel) {
                    padding_pass = padding_pass &&
                        cuda_output[static_cast<std::size_t>(channel) * plane + spatial] ==
                            114.0F / 255.0F;
                }
            }
        }
    }
    pass = check(padding_pass, "padding_value") && pass;
    pass = check(cuda_preprocessor->device_tensor().data != nullptr &&
                     cuda_preprocessor->device_tensor().element_count ==
                         stage_r::CudaPreprocessor::kTargetElementCount &&
                     cuda_preprocessor->stream() != nullptr,
                 "device_tensor_contract") && pass;

    return pass ? 0 : 1;
}

}  // namespace

int main() { return run(); }
