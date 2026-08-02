#include "backend_tensorrt/pageable_raw_staging.hpp"

#include <opencv2/core.hpp>

#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
}

int main() {
    try {
        cv::Mat backing(3, 7, CV_8UC3, cv::Scalar(0, 0, 0));
        cv::Mat image = backing(cv::Rect(1, 0, 4, 3)); // non-contiguous, padded stride
        for (int row = 0; row < image.rows; ++row) {
            for (int col = 0; col < image.cols; ++col) {
                image.at<cv::Vec3b>(row, col) = cv::Vec3b(
                    static_cast<unsigned char>(row * 10 + col),
                    static_cast<unsigned char>(100 + row * 10 + col),
                    static_cast<unsigned char>(200 + row * 10 + col));
            }
        }
        edge_ai_defect::stage_r::PageableRawStaging staging;
        const auto status = staging.prepare(image);
        require(status.ok(), "non-contiguous image rejected");
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
        const auto old_capacity = staging.capacity();
        require(staging.prepare(image).ok(), "repeat prepare failed");
        require(staging.capacity() == old_capacity, "staging capacity unexpectedly changed");
        std::cout << "Pageable raw staging tests passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Pageable raw staging test failed: " << error.what() << '\n';
        return 1;
    }
}
