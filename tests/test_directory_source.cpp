#include "edge_ai_defect/runtime/directory_source.hpp"

#include <opencv2/imgcodecs.hpp>

#include <cerrno>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

#if defined(__linux__)
#include <sys/stat.h>
#endif

namespace {

namespace core = edge_ai_defect::core;
namespace runtime = edge_ai_defect::runtime;
namespace fs = std::filesystem;

class TestContext {
public:
    void expect(bool condition,
                const std::string& case_name,
                const std::string& detail) {
        if (!condition) {
            ++failure_count_;
            std::cerr << "FAILED: " << case_name << ": " << detail << '\n';
        }
    }

    [[nodiscard]] int failure_count() const noexcept {
        return failure_count_;
    }

private:
    int failure_count_ = 0;
};

struct Options {
    fs::path temp_dir;
};

bool parse_options(int argc, char* argv[], Options* options) {
    if (options == nullptr) {
        return false;
    }
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        if (argument == "--temp-dir" && index + 1 < argc) {
            options->temp_dir = argv[++index];
        } else {
            std::cerr << "Unknown or incomplete argument: " << argument << '\n';
            return false;
        }
    }
    if (options->temp_dir.empty()) {
        std::cerr << "Usage: test_directory_source --temp-dir <path>\n";
        return false;
    }
    return true;
}

class TestWorkspace {
public:
    explicit TestWorkspace(fs::path root) : root_(std::move(root)) {}

    ~TestWorkspace() {
        std::error_code error;
        fs::remove_all(root_, error);
    }

    [[nodiscard]] bool prepare() const {
        std::error_code error;
        fs::remove_all(root_, error);
        if (error) {
            return false;
        }
        fs::create_directories(root_, error);
        return !error;
    }

    [[nodiscard]] fs::path make_case(const std::string& name) const {
        const fs::path path = root_ / name;
        std::error_code error;
        fs::create_directories(path, error);
        return error ? fs::path{} : path;
    }

    void cleanup(TestContext& context) const {
        std::error_code error;
        fs::remove_all(root_, error);
        context.expect(!error, "test workspace cleanup", error.message());
    }

private:
    fs::path root_;
};

bool write_color_image(const fs::path& path, int width, int height, int value) {
    std::error_code error;
    fs::create_directories(path.parent_path(), error);
    if (error) {
        return false;
    }
    const cv::Mat image(height, width, CV_8UC3,
                        cv::Scalar(value, value + 1, value + 2));
    return cv::imwrite(path.string(), image);
}

bool write_text_file(const fs::path& path, const std::string& content) {
    std::ofstream output(path);
    output << content;
    output.close();
    return output.good();
}

bool image_equal(const cv::Mat& left, const cv::Mat& right) {
    return left.size() == right.size() && left.type() == right.type() &&
           cv::norm(left, right) == 0.0;
}

bool item_equal(const runtime::ImageItem& left, const runtime::ImageItem& right) {
    return left.sequence_index == right.sequence_index &&
           left.relative_path == right.relative_path &&
           image_equal(left.image_bgr, right.image_bgr);
}

runtime::ImageItem sentinel_item() {
    runtime::ImageItem item;
    item.sequence_index = 999;
    item.relative_path = "sentinel.png";
    item.image_bgr = cv::Mat(2, 3, CV_8UC3, cv::Scalar(9, 8, 7)).clone();
    return item;
}

void expect_factory_failure_preserves_output(
    TestContext& context,
    const std::string& case_name,
    const fs::path& root,
    std::unique_ptr<runtime::DirectorySource>* output) {
    runtime::DirectorySource* const sentinel = output->get();
    const core::Status status = runtime::DirectorySource::create(root, output);
    context.expect(!status.ok(), case_name, "create must fail");
    context.expect(!status.message().empty(), case_name, "failure message missing");
    context.expect(output->get() == sentinel,
                   case_name,
                   "factory failure must preserve caller output");
}

std::unique_ptr<runtime::DirectorySource> create_sentinel_source(
    TestContext& context,
    const fs::path& root) {
    context.expect(write_color_image(root / "sentinel.png", 2, 2, 1),
                   "sentinel source setup",
                   "could not write image");
    std::unique_ptr<runtime::DirectorySource> source;
    const core::Status status = runtime::DirectorySource::create(root, &source);
    context.expect(status.ok(), "sentinel source setup", status.message());
    return source;
}

void test_create_failures(TestContext& context, const TestWorkspace& workspace) {
    const fs::path sentinel_root = workspace.make_case("create_sentinel");
    std::unique_ptr<runtime::DirectorySource> output =
        create_sentinel_source(context, sentinel_root);
    if (!output) {
        return;
    }

    const core::Status null_output =
        runtime::DirectorySource::create(sentinel_root, nullptr);
    context.expect(!null_output.ok(), "null factory output", "create must fail");
    context.expect(null_output.code() == core::ErrorCode::kInvalidArgument,
                   "null factory output",
                   "unexpected error code");

    expect_factory_failure_preserves_output(
        context, "empty root", fs::path{}, &output);
    expect_factory_failure_preserves_output(
        context, "missing root", workspace.make_case("missing") / "gone", &output);

    const fs::path regular_file = workspace.make_case("not_directory") / "file.txt";
    context.expect(write_text_file(regular_file, "not a directory"),
                   "not directory setup",
                   "could not write regular file");
    expect_factory_failure_preserves_output(context, "root is regular file", regular_file,
                                            &output);

    expect_factory_failure_preserves_output(
        context, "empty directory", workspace.make_case("empty"), &output);

    const fs::path no_images = workspace.make_case("no_images");
    context.expect(write_text_file(no_images / "note.txt", "not an image"),
                   "no images setup",
                   "could not write text file");
    expect_factory_failure_preserves_output(
        context, "directory without supported images", no_images, &output);
}

void test_filter_sort_decode_and_eos(TestContext& context,
                                     const TestWorkspace& workspace) {
    const fs::path root = workspace.make_case("filter_sort");
    context.expect(write_color_image(root / "z.jpg", 12, 13, 10),
                   "filter setup", "could not write jpg");
    context.expect(write_color_image(root / "m.JPEG", 10, 11, 20),
                   "filter setup", "could not write jpeg");
    context.expect(write_color_image(root / ".hidden.PnG", 8, 9, 30),
                   "filter setup", "could not write hidden png");
    context.expect(write_color_image(root / "a.bmp", 6, 7, 40),
                   "filter setup", "could not write bmp");
    context.expect(write_text_file(root / "ignored.gif", "not supported"),
                   "filter setup", "could not write unsupported file");
    context.expect(write_text_file(root / "note.txt", "not an image"),
                   "filter setup", "could not write text file");

    const fs::path nested = root / "nested";
    std::error_code error;
    fs::create_directories(nested, error);
    context.expect(!error, "filter setup", "could not create nested directory");
    context.expect(write_color_image(nested / "inside.png", 3, 4, 50),
                   "filter setup", "could not write nested image");

    fs::create_symlink("z.jpg", root / "linked.jpg", error);
    context.expect(!error,
                   "file symlink setup",
                   "Linux source tests require file symlink support: " + error.message());
    error.clear();
    fs::create_directory_symlink("nested", root / "linked_directory", error);
    context.expect(!error,
                   "directory symlink setup",
                   "Linux source tests require directory symlink support: " +
                       error.message());

#if defined(__linux__)
    const std::string fifo_path = (root / "stream.png").string();
    const int fifo_result = ::mkfifo(fifo_path.c_str(), 0600);
    context.expect(fifo_result == 0,
                   "non-regular file setup",
                   fifo_result == 0 ? "" : std::strerror(errno));
#endif

    std::unique_ptr<runtime::DirectorySource> source;
    const core::Status create_status = runtime::DirectorySource::create(root, &source);
    context.expect(create_status.ok(), "filter and sorting", create_status.message());
    if (!create_status.ok()) {
        return;
    }

    const core::Status null_next = source->next(nullptr);
    context.expect(!null_next.ok(), "null next output", "next must fail");
    context.expect(null_next.code() == core::ErrorCode::kInvalidArgument,
                   "null next output",
                   "unexpected error code");

    const std::vector<std::string> expected_paths{
        ".hidden.PnG", "a.bmp", "m.JPEG", "z.jpg"};
    const std::vector<std::pair<int, int>> expected_dimensions{
        {8, 9}, {6, 7}, {10, 11}, {12, 13}};
    std::vector<std::string> first_order;
    for (std::size_t index = 0; index < expected_paths.size(); ++index) {
        std::optional<runtime::ImageItem> item;
        const core::Status status = source->next(&item);
        context.expect(status.ok(), "decode supported image", status.message());
        context.expect(item.has_value(), "decode supported image", "item missing");
        if (!status.ok() || !item.has_value()) {
            return;
        }
        first_order.push_back(item->relative_path.generic_string());
        context.expect(item->sequence_index == index,
                       "sequence index",
                       "indices must start at zero and be contiguous");
        context.expect(item->relative_path.generic_string() == expected_paths[index],
                       "relative path byte order",
                       "path does not match deterministic sort order");
        context.expect(!item->relative_path.is_absolute(),
                       "relative path",
                       "ImageItem must not expose an absolute path");
        context.expect(!item->image_bgr.empty(), "decoded image", "image is empty");
        context.expect(item->image_bgr.type() == CV_8UC3,
                       "decoded image",
                       "image must be CV_8UC3");
        context.expect(item->image_bgr.cols == expected_dimensions[index].first &&
                           item->image_bgr.rows == expected_dimensions[index].second,
                       "decoded image dimensions",
                       "unexpected width or height");
    }

    std::optional<runtime::ImageItem> eos = sentinel_item();
    core::Status status = source->next(&eos);
    context.expect(status.ok() && !eos.has_value(),
                   "end of stream",
                   status.ok() ? "EOS must return nullopt" : status.message());
    eos = sentinel_item();
    status = source->next(&eos);
    context.expect(status.ok() && !eos.has_value(),
                   "repeated end of stream",
                   status.ok() ? "EOS must remain nullopt" : status.message());

    std::unique_ptr<runtime::DirectorySource> repeat_source;
    status = runtime::DirectorySource::create(root, &repeat_source);
    context.expect(status.ok(), "repeat source creation", status.message());
    std::vector<std::string> repeated_order;
    if (status.ok()) {
        for (std::size_t index = 0; index < expected_paths.size(); ++index) {
            std::optional<runtime::ImageItem> item;
            status = repeat_source->next(&item);
            if (!status.ok() || !item.has_value()) {
                context.expect(false, "repeat deterministic order", status.message());
                break;
            }
            repeated_order.push_back(item->relative_path.generic_string());
        }
    }
    context.expect(first_order == repeated_order,
                   "repeat deterministic order",
                   "recreated source order differs");
}

void expect_next_failure_preserves_output(TestContext& context,
                                          const std::string& case_name,
                                          runtime::DirectorySource* source,
                                          const std::string& path_fragment) {
    std::optional<runtime::ImageItem> output = sentinel_item();
    const std::optional<runtime::ImageItem> expected = output;
    const core::Status status = source->next(&output);
    context.expect(!status.ok(), case_name, "next must fail");
    context.expect(status.code() == core::ErrorCode::kImageProcessingError,
                   case_name,
                   "unexpected error code");
    context.expect(status.message().find("decode image") != std::string::npos &&
                       status.message().find(path_fragment) != std::string::npos,
                   case_name,
                   "message must identify decode stage and relative path");
    context.expect(output.has_value() && expected.has_value() &&
                       item_equal(*output, *expected),
                   case_name,
                   "failure must preserve caller output");
}

void test_decode_failures(TestContext& context, const TestWorkspace& workspace) {
    const fs::path bad_root = workspace.make_case("bad_image");
    context.expect(write_text_file(bad_root / "corrupt.jpg", "not a JPEG"),
                   "bad image setup",
                   "could not write corrupt image");
    std::unique_ptr<runtime::DirectorySource> bad_source;
    core::Status status = runtime::DirectorySource::create(bad_root, &bad_source);
    context.expect(status.ok(), "bad image creation", status.message());
    if (status.ok()) {
        expect_next_failure_preserves_output(context, "corrupt image", bad_source.get(),
                                             "corrupt.jpg");
    }

    const fs::path deleted_root = workspace.make_case("deleted_image");
    const fs::path deleted_path = deleted_root / "vanish.png";
    context.expect(write_color_image(deleted_path, 4, 5, 6),
                   "deleted image setup",
                   "could not write image");
    std::unique_ptr<runtime::DirectorySource> deleted_source;
    status = runtime::DirectorySource::create(deleted_root, &deleted_source);
    context.expect(status.ok(), "deleted image creation", status.message());
    std::error_code error;
    fs::remove(deleted_path, error);
    context.expect(!error, "deleted image setup", error.message());
    if (status.ok() && !error) {
        expect_next_failure_preserves_output(context,
                                             "image deleted after enumeration",
                                             deleted_source.get(),
                                             "vanish.png");
    }
}

}  // namespace

int main(int argc, char* argv[]) {
    Options options;
    if (!parse_options(argc, argv, &options)) {
        return 2;
    }

    TestContext context;
    TestWorkspace workspace(options.temp_dir / "directory_source_cases");
    context.expect(workspace.prepare(), "test workspace setup", "could not prepare");
    if (context.failure_count() == 0) {
        test_create_failures(context, workspace);
        test_filter_sort_decode_and_eos(context, workspace);
        test_decode_failures(context, workspace);
    }
    workspace.cleanup(context);

    if (context.failure_count() != 0) {
        std::cerr << context.failure_count() << " DirectorySource test(s) failed\n";
        return 1;
    }

    std::cout << "All DirectorySource tests passed\n";
    return 0;
}
