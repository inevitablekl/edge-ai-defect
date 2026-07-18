#include "edge_ai_defect/runtime/directory_source.hpp"

#include <opencv2/imgcodecs.hpp>

#include <algorithm>
#include <filesystem>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;
namespace fs = std::filesystem;

std::string ascii_lowercase(std::string value) {
    for (char& character : value) {
        if (character >= 'A' && character <= 'Z') {
            character = static_cast<char>(character - 'A' + 'a');
        }
    }
    return value;
}

bool is_supported_image_path(const fs::path& path) {
    const std::string extension = ascii_lowercase(path.extension().string());
    return extension == ".jpg" || extension == ".jpeg" ||
           extension == ".png" || extension == ".bmp";
}

Status filesystem_failure(const std::string& stage,
                          const fs::path& path,
                          const std::error_code& error) {
    return Status::failure(
        ErrorCode::kIoError,
        stage + " for '" + path.generic_string() + "': " + error.message());
}

Status decode_failure(const fs::path& relative_path, const std::string& detail) {
    return Status::failure(
        ErrorCode::kImageProcessingError,
        "decode image '" + relative_path.generic_string() + "': " + detail);
}

}  // namespace

DirectorySource::DirectorySource(
    std::filesystem::path root,
    std::vector<std::filesystem::path> relative_paths)
    : root_(std::move(root)), relative_paths_(std::move(relative_paths)) {}

core::Status DirectorySource::create(
    const std::filesystem::path& root,
    std::unique_ptr<DirectorySource>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "DirectorySource create output must not be null");
    }
    if (root.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "DirectorySource root must not be empty");
    }

    std::error_code error;
    const fs::path absolute_root = fs::absolute(root, error).lexically_normal();
    if (error) {
        return filesystem_failure("resolve input directory", root, error);
    }

    const fs::file_status root_status = fs::status(absolute_root, error);
    if (error) {
        return filesystem_failure("inspect input directory", root, error);
    }
    if (!fs::exists(root_status)) {
        return Status::failure(ErrorCode::kIoError,
                               "input directory does not exist: '" +
                                   root.generic_string() + "'");
    }
    if (!fs::is_directory(root_status)) {
        return Status::failure(ErrorCode::kIoError,
                               "input root is not a directory: '" +
                                   root.generic_string() + "'");
    }

    std::vector<fs::path> relative_paths;
    fs::directory_iterator iterator(absolute_root, error);
    if (error) {
        return filesystem_failure("enumerate input directory", root, error);
    }

    const fs::directory_iterator end;
    while (iterator != end) {
        const fs::path entry_path = iterator->path();
        const fs::file_status entry_status = fs::symlink_status(entry_path, error);
        if (error) {
            return filesystem_failure("inspect directory entry", entry_path, error);
        }

        if (!fs::is_symlink(entry_status) && fs::is_regular_file(entry_status) &&
            is_supported_image_path(entry_path)) {
            const fs::path relative_path = entry_path.lexically_relative(absolute_root);
            if (relative_path.empty() || relative_path.is_absolute()) {
                return Status::failure(
                    ErrorCode::kIoError,
                    "derive relative path for input entry failed");
            }
            relative_paths.push_back(relative_path);
        }

        iterator.increment(error);
        if (error) {
            return filesystem_failure("continue input directory enumeration", root,
                                      error);
        }
    }

    std::sort(relative_paths.begin(), relative_paths.end(),
              [](const fs::path& left, const fs::path& right) {
                  return left.generic_string() < right.generic_string();
              });
    if (relative_paths.empty()) {
        return Status::failure(
            ErrorCode::kIoError,
            "input directory contains no supported regular image files: '" +
                root.generic_string() + "'");
    }

    std::unique_ptr<DirectorySource> candidate(
        new DirectorySource(absolute_root, std::move(relative_paths)));
    *output = std::move(candidate);
    return Status::success();
}

core::Status DirectorySource::next(std::optional<ImageItem>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "DirectorySource next output must not be null");
    }
    if (cursor_ == relative_paths_.size()) {
        *output = std::nullopt;
        return Status::success();
    }

    const fs::path& relative_path = relative_paths_[cursor_];
    cv::Mat image_bgr;
    try {
        image_bgr = cv::imread((root_ / relative_path).string(), cv::IMREAD_COLOR);
    } catch (const cv::Exception& exception) {
        return decode_failure(relative_path, exception.what());
    }

    if (image_bgr.empty()) {
        return decode_failure(relative_path, "cv::imread returned an empty image");
    }
    if (image_bgr.type() != CV_8UC3) {
        return decode_failure(relative_path, "decoded image is not CV_8UC3");
    }
    if (image_bgr.cols <= 0 || image_bgr.rows <= 0) {
        return decode_failure(relative_path, "decoded image has non-positive dimensions");
    }

    ImageItem item;
    item.sequence_index = cursor_;
    item.relative_path = relative_path;
    item.image_bgr = std::move(image_bgr);

    *output = std::move(item);
    ++cursor_;
    return Status::success();
}

}  // namespace edge_ai_defect::runtime
