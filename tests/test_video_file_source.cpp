#include "edge_ai_defect/runtime/video_file_source.hpp"

#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <memory>
#include <optional>
#include <string>
#include <system_error>
#include <utility>

namespace {

namespace fs = std::filesystem;
namespace runtime = edge_ai_defect::runtime;

class TestContext {
public:
    void expect(bool condition, const std::string& name,
                const std::string& detail) {
        if (!condition) {
            ++failures_;
            std::cerr << "FAILED: " << name << ": " << detail << '\n';
        }
    }

    [[nodiscard]] int failures() const noexcept { return failures_; }

private:
    int failures_ = 0;
};

bool write_video(const fs::path& path, int frame_count) {
    const cv::Size size(32, 24);
    cv::VideoWriter writer;
    if (!writer.open(path.string(), cv::VideoWriter::fourcc('M', 'J', 'P', 'G'),
                     15.0, size, true)) {
        return false;
    }
    for (int index = 0; index < frame_count; ++index) {
        cv::Mat frame(size, CV_8UC3,
                      cv::Scalar(index + 1, index + 2, index + 3));
        writer.write(frame);
    }
    writer.release();
    return fs::exists(path) && fs::file_size(path) > 0;
}

std::string fourcc_text(double value) {
    const auto code = static_cast<unsigned int>(std::llround(value));
    std::string result(4, '\0');
    for (int index = 0; index < 4; ++index) {
        result[static_cast<std::size_t>(index)] =
            static_cast<char>((code >> (8 * index)) & 0xffU);
    }
    return result;
}

bool write_codec_preflight(const fs::path& video_path,
                           const fs::path& output_path,
                           int generated_frame_count) {
    cv::VideoCapture capture(video_path.string(), cv::CAP_ANY);
    if (!capture.isOpened()) {
        std::cout << "P6_BLOCKED_CODEC_PREFLIGHT\n";
        return false;
    }
    const std::string observed_fourcc =
        fourcc_text(capture.get(cv::CAP_PROP_FOURCC));
    int decoded_frame_count = 0;
    cv::Mat frame;
    while (capture.read(frame)) {
        if (frame.empty()) {
            std::cout << "P6_BLOCKED_CODEC_PREFLIGHT\n";
            return false;
        }
        ++decoded_frame_count;
    }
    const double reported_frame_count = capture.get(cv::CAP_PROP_FRAME_COUNT);
    const int width = static_cast<int>(std::llround(
        capture.get(cv::CAP_PROP_FRAME_WIDTH)));
    const int height = static_cast<int>(std::llround(
        capture.get(cv::CAP_PROP_FRAME_HEIGHT)));
    const double nominal_fps = capture.get(cv::CAP_PROP_FPS);
    capture.release();
    const bool exact = decoded_frame_count == generated_frame_count;
    std::ofstream output(output_path);
    if (!output) return false;
    output << "{\n"
           << "  \"status\": \"" << (exact ? "PASS" : "P6_BLOCKED_CODEC_PREFLIGHT") << "\",\n"
           << "  \"requested_codec\": \"MJPG\",\n"
           << "  \"observed_fourcc\": \"" << observed_fourcc << "\",\n"
           << "  \"width\": " << width << ",\n"
           << "  \"height\": " << height << ",\n"
           << "  \"nominal_fps\": " << nominal_fps << ",\n"
           << "  \"generated_frame_count\": " << generated_frame_count << ",\n"
           << "  \"decoded_frame_count\": " << decoded_frame_count << ",\n"
           << "  \"cap_prop_frame_count\": " << reported_frame_count << "\n"
           << "}\n";
    return exact && output.good();
}

void test_open_metadata_sequence_and_eof(TestContext& context,
                                          const fs::path& root) {
    const fs::path path = root / "test_video.avi";
    context.expect(write_video(path, 4), "open success", "MJPG AVI could not be written");

    std::unique_ptr<runtime::VideoFileSource> source;
    const auto create_status = runtime::VideoFileSource::create(path, &source);
    context.expect(create_status.ok(), "open success", create_status.message());
    if (!create_status.ok()) return;

    const runtime::VideoFileMetadata& metadata = source->metadata();
    context.expect(metadata.width == 32 && metadata.height == 24,
                   "metadata", "resolution mismatch");
    context.expect(std::isfinite(metadata.nominal_fps) && metadata.nominal_fps > 0.0,
                   "metadata", "nominal FPS missing");
    context.expect(metadata.decoded_frame_count == 0,
                   "metadata", "decoded count must start at zero");

    for (std::size_t index = 0; index < 4; ++index) {
        std::optional<runtime::ImageItem> item;
        const auto status = source->next(&item);
        context.expect(status.ok(), "sequential decode", status.message());
        context.expect(item.has_value(), "sequential decode", "frame missing");
        if (!status.ok() || !item.has_value()) return;
        context.expect(item->sequence_index == index, "frame index", "index is not zero-based/continuous");
        context.expect(item->relative_path.generic_string() ==
                           std::string("test_video.avi/frame_") +
                               (index < 10 ? "00000" : "") + std::to_string(index),
                       "frame identity", "relative path mismatch");
        context.expect(item->image_bgr.cols == 32 && item->image_bgr.rows == 24 &&
                           item->image_bgr.type() == CV_8UC3,
                       "decoded frame", "decoded image contract mismatch");
    }
    context.expect(source->metadata().decoded_frame_count == 4,
                   "decoded count", "decoded count mismatch");

    std::optional<runtime::ImageItem> item;
    const auto eof_status = source->next(&item);
    context.expect(eof_status.ok(), "EOF", eof_status.message());
    context.expect(!item.has_value(), "EOF", "EOF must return nullopt");
}

void test_max_frames(TestContext& context, const fs::path& root) {
    const fs::path path = root / "limited_video.avi";
    context.expect(write_video(path, 4), "max_frames setup", "MJPG AVI could not be written");

    std::unique_ptr<runtime::VideoFileSource> source;
    const auto create_status = runtime::VideoFileSource::create(path, &source, 2);
    context.expect(create_status.ok(), "max_frames", create_status.message());
    if (!create_status.ok()) return;
    for (std::size_t index = 0; index < 2; ++index) {
        std::optional<runtime::ImageItem> item;
        const auto status = source->next(&item);
        context.expect(status.ok() && item.has_value(), "max_frames", "limited frame missing");
    }
    std::optional<runtime::ImageItem> item;
    const auto status = source->next(&item);
    context.expect(status.ok() && !item.has_value(), "max_frames", "limit did not produce EOS");
    context.expect(source->metadata().decoded_frame_count == 2,
                   "max_frames", "decoded count exceeded constructor limit");

    std::unique_ptr<runtime::VideoFileSource> unused;
    const auto zero_status = runtime::VideoFileSource::create(path, &unused, 0);
    context.expect(!zero_status.ok(), "max_frames zero", "zero limit must be rejected");
}

void test_failures(TestContext& context, const fs::path& root) {
    std::unique_ptr<runtime::VideoFileSource> source;
    const auto missing_status = runtime::VideoFileSource::create(
        root / "missing.avi", &source);
    context.expect(!missing_status.ok(), "open failure", "missing video must fail-fast");

    const fs::path corrupt = root / "corrupt.avi";
    {
        std::ofstream output(corrupt, std::ios::binary);
        output << "not a video";
    }
    const auto corrupt_status = runtime::VideoFileSource::create(corrupt, &source);
    context.expect(!corrupt_status.ok(), "decode failure", "corrupt video must fail-fast");

    const auto null_status = runtime::VideoFileSource::create(root / "missing.avi", nullptr);
    context.expect(!null_status.ok(), "null factory output", "null output must fail");
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 3 || std::string(argv[1]) != "--temp-dir") {
        std::cerr << "Usage: test_video_file_source --temp-dir <path>"
                     " [--asset-output <path> --preflight-output <path>]\n";
        return 2;
    }
    const fs::path root = argv[2];
    fs::path asset_output;
    fs::path preflight_output;
    for (int index = 3; index < argc; ++index) {
        const std::string option = argv[index];
        if (index + 1 >= argc) return 2;
        if (option == "--asset-output") {
            asset_output = argv[++index];
        } else if (option == "--preflight-output") {
            preflight_output = argv[++index];
        } else {
            return 2;
        }
    }
    std::error_code error;
    fs::remove_all(root, error);
    fs::create_directories(root, error);
    if (error) {
        std::cerr << "cannot prepare test directory: " << error.message() << '\n';
        return 2;
    }

    TestContext context;
    test_open_metadata_sequence_and_eof(context, root);
    test_max_frames(context, root);
    test_failures(context, root);
    if (!asset_output.empty()) {
        const bool asset_ok = write_video(asset_output, 16);
        context.expect(asset_ok, "codec preflight writer", "MJPG VideoWriter could not open");
        if (asset_ok && !preflight_output.empty()) {
            context.expect(write_codec_preflight(asset_output, preflight_output, 16),
                           "codec preflight decoder",
                           "decoded frame count did not match generated count");
        }
    }
    fs::remove_all(root, error);
    return context.failures() == 0 ? 0 : 1;
}
