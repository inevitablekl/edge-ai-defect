#include "backend_tensorrt/pinned_raw_staging.hpp"

#include <cuda_runtime_api.h>
#include <opencv2/core.hpp>

#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

void require_pinned(const std::uint8_t* pointer) {
    cudaPointerAttributes attributes{};
    const cudaError_t error = cudaPointerGetAttributes(&attributes, pointer);
    require(error == cudaSuccess, "cudaPointerGetAttributes failed");
    require(attributes.type == cudaMemoryTypeHost, "allocation is not pinned host memory");
}
}  // namespace

int main() {
    try {
        // The pinned buffer must be allocated explicitly before use; calling
        // prepare() without allocate() is an explicit error, not a fallback.
        edge_ai_defect::stage_r::PinnedRawStaging staging;
        cv::Mat backing(3, 7, CV_8UC3, cv::Scalar(0, 0, 0));
        cv::Mat image = backing(cv::Rect(1, 0, 4, 3)); // non-contiguous, padded stride
        require(!staging.prepare(image).ok(), "prepare without allocate must fail explicitly");

        require(staging.allocate(4096).ok(), "initial allocate failed");
        require(staging.capacity() == 4096, "capacity mismatch after allocate");
        require_pinned(staging.data());
        const auto* buffer = staging.data();

        // Idempotent re-allocate must reuse the existing pinned buffer.
        require(staging.allocate(4096).ok(), "repeat allocate failed");
        require(staging.data() == buffer, "repeat allocate must not reallocate");

        for (int row = 0; row < image.rows; ++row) {
            for (int col = 0; col < image.cols; ++col) {
                image.at<cv::Vec3b>(row, col) = cv::Vec3b(
                    static_cast<unsigned char>(row * 10 + col),
                    static_cast<unsigned char>(100 + row * 10 + col),
                    static_cast<unsigned char>(200 + row * 10 + col));
            }
        }
        require(staging.prepare(image).ok(), "non-contiguous image rejected");
        require(staging.data() == buffer, "prepare must not reallocate");
        require(staging.channels() == 3 && staging.width() == 4 && staging.height() == 3,
                "metadata mismatch");
        require(staging.source_row_stride() == image.step && staging.packed_row_bytes() == 12,
                "stride metadata mismatch");
        require(staging.total_packed_bytes() == 36, "packed size mismatch");
        for (int row = 0; row < image.rows; ++row) {
            for (int col = 0; col < image.cols; ++col) {
                const auto* actual = staging.data() + row * 12 + col * 3;
                const auto expected = image.at<cv::Vec3b>(row, col);
                require(actual[0] == expected[0] && actual[1] == expected[1] && actual[2] == expected[2],
                        "row-aware packed copy mismatch");
            }
        }

        // An image that does not fit the allocated capacity must fail
        // explicitly; there is no silent growth and no pageable fallback.
        cv::Mat oversized(2, 700, CV_8UC3, cv::Scalar(0, 0, 0)); // 4200 > 4096
        require(!staging.prepare(oversized).ok(), "oversized image must fail explicitly");
        require(staging.allocate(4096U * 3U).ok(), "grow allocate failed");
        require_pinned(staging.data());
        require(staging.prepare(oversized).ok(), "grew buffer should accept the image");

        // A smaller re-allocate must not shrink an adequate buffer.
        const auto* grown = staging.data();
        require(staging.allocate(8).ok(), "smaller allocate failed");
        require(staging.data() == grown, "smaller allocate must not shrink the buffer");
        require(staging.prepare(image).ok(), "prepare after smaller allocate failed");
        require(staging.data() == grown, "prepare must not reallocate");

        std::cout << "Pinned raw staging tests passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Pinned raw staging test failed: " << error.what() << '\n';
        return 1;
    }
}
