#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "preprocess_level_a_compare.hpp"
#include "preprocess_level_a_manifest.hpp"

#include <opencv2/core.hpp>
#include <opencv2/core/version.hpp>

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace level_a = edge_ai_defect::test::preprocess_level_a;
namespace preprocess = edge_ai_defect::preprocess;
namespace fs = std::filesystem;

constexpr int kComparisonFailure = 1;
constexpr int kInputFailure = 2;
constexpr int kPreprocessFailure = 3;
constexpr int kReportFailure = 4;
constexpr double kGainTolerance = 1.0e-12;

class InputError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class PreprocessError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class ReportError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

struct Options {
    fs::path manifest;
    fs::path data_root;
    fs::path report;
};

struct CaseResult {
    std::string id;
    std::string tolerance_profile;
    std::vector<std::int64_t> target_shape;
    std::size_t element_count = 0;
    double mae = 0.0;
    double max_abs = 0.0;
    double mae_limit = 0.0;
    double max_abs_limit = 0.0;
    bool metadata_pass = false;
    bool tensor_pass = false;
    bool overall_pass = false;
    std::size_t max_error_index = 0;
    int max_error_channel = 0;
    int max_error_y = 0;
    int max_error_x = 0;
    float golden_at_max_error = 0.0F;
    float actual_at_max_error = 0.0F;
    std::string max_error_region;
    bool nonfinite_detected = false;
    std::string nonfinite_source;
};

bool host_is_little_endian() noexcept {
    const std::uint16_t value = 1U;
    return *reinterpret_cast<const std::uint8_t*>(&value) == 1U;
}

Options parse_options(int argc, char** argv) {
    if (argc != 7) {
        throw InputError(
            "CLI: expected --manifest <path> --data-root <path> --report <path>");
    }
    Options options;
    bool have_manifest = false;
    bool have_data_root = false;
    bool have_report = false;
    for (int index = 1; index < argc; index += 2) {
        const std::string option = argv[index];
        const fs::path value = argv[index + 1];
        if (value.empty()) {
            throw InputError("CLI: option '" + option + "' has an empty value");
        }
        if (option == "--manifest" && !have_manifest) {
            options.manifest = value;
            have_manifest = true;
        } else if (option == "--data-root" && !have_data_root) {
            options.data_root = value;
            have_data_root = true;
        } else if (option == "--report" && !have_report) {
            options.report = value;
            have_report = true;
        } else {
            throw InputError("CLI: unknown or duplicate option '" + option + "'");
        }
    }
    if (!have_manifest || !have_data_root || !have_report) {
        throw InputError("CLI: all required options must be provided exactly once");
    }
    return options;
}

std::vector<std::uint8_t> read_bytes(const fs::path& path,
                                     const std::string& case_id,
                                     const std::string& category) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) {
        throw InputError(case_id + ": " + category + " file is not readable: " +
                         path.string());
    }
    const std::streampos end = input.tellg();
    if (end < 0) {
        throw InputError(case_id + ": cannot determine " + category + " file size: " +
                         path.string());
    }
    const auto unsigned_size = static_cast<std::uintmax_t>(end);
    if (unsigned_size > std::numeric_limits<std::size_t>::max() ||
        unsigned_size > static_cast<std::uintmax_t>(
                            std::numeric_limits<std::streamsize>::max())) {
        throw InputError(case_id + ": " + category + " file is too large");
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(unsigned_size));
    input.seekg(0, std::ios::beg);
    if (!bytes.empty()) {
        input.read(reinterpret_cast<char*>(bytes.data()),
                   static_cast<std::streamsize>(bytes.size()));
        if (!input) {
            throw InputError(case_id + ": failed to read complete " + category +
                             " file: " + path.string());
        }
    }
    return bytes;
}

bool compare_int_field(const std::string& case_id,
                       const std::string& field,
                       int actual,
                       int expected) {
    if (actual == expected) {
        return true;
    }
    std::cerr << case_id << ": metadata field " << field << " actual=" << actual
              << " expected=" << expected << '\n';
    return false;
}

bool compare_metadata(const std::string& case_id,
                      const preprocess::ImageTransformMetadata& actual,
                      const level_a::TransformMetadata& expected) {
    bool pass = true;
    pass = compare_int_field(
               case_id, "original_width", actual.original_width, expected.original_width) &&
           pass;
    pass = compare_int_field(case_id,
                             "original_height",
                             actual.original_height,
                             expected.original_height) &&
           pass;
    pass = compare_int_field(
               case_id, "target_width", actual.target_width, expected.target_width) &&
           pass;
    pass = compare_int_field(
               case_id, "target_height", actual.target_height, expected.target_height) &&
           pass;
    pass = compare_int_field(
               case_id, "resized_width", actual.resized_width, expected.resized_width) &&
           pass;
    pass = compare_int_field(case_id,
                             "resized_height",
                             actual.resized_height,
                             expected.resized_height) &&
           pass;
    const double gain_error = std::abs(actual.gain - expected.gain);
    if (!std::isfinite(actual.gain) || gain_error > kGainTolerance) {
        std::cerr << case_id << ": metadata field gain actual=" << actual.gain
                  << " expected=" << expected.gain
                  << " tolerance=" << kGainTolerance << '\n';
        pass = false;
    }
    pass = compare_int_field(
               case_id, "pad_left", actual.pad_left, expected.pad_left) &&
           pass;
    pass = compare_int_field(
               case_id, "pad_right", actual.pad_right, expected.pad_right) &&
           pass;
    pass = compare_int_field(case_id, "pad_top", actual.pad_top, expected.pad_top) &&
           pass;
    pass = compare_int_field(
               case_id, "pad_bottom", actual.pad_bottom, expected.pad_bottom) &&
           pass;
    return pass;
}

std::string classify_region(const level_a::CaseDefinition& definition, int y, int x) {
    const level_a::TransformMetadata& metadata = definition.metadata;
    if (x < metadata.pad_left || x >= metadata.target_width - metadata.pad_right ||
        y < metadata.pad_top || y >= metadata.target_height - metadata.pad_bottom) {
        return "padding";
    }
    return "source_or_resized";
}

CaseResult validate_case(const level_a::CaseDefinition& definition,
                         const level_a::ToleranceProfile& tolerance,
                         const fs::path& data_root) {
    const std::size_t input_size =
        static_cast<std::size_t>(definition.width) *
        static_cast<std::size_t>(definition.height) * 3U;
    fs::path input_path;
    level_a::resolve_asset_path_under_root(
        data_root, definition.input_path, &input_path);
    const std::vector<std::uint8_t> input_bytes =
        read_bytes(input_path, definition.id, "raw BGR input");
    if (input_bytes.size() != input_size) {
        throw InputError(definition.id + ": raw BGR input size actual=" +
                         std::to_string(input_bytes.size()) + " expected=" +
                         std::to_string(input_size));
    }
    cv::Mat input_bgr(definition.height, definition.width, CV_8UC3);
    if (input_bgr.empty() || !input_bgr.isContinuous()) {
        throw InputError(definition.id + ": failed to allocate contiguous CV_8UC3 input");
    }
    std::memcpy(input_bgr.data, input_bytes.data(), input_bytes.size());

    const core::TensorInfo input_info{
        core::TensorDataType::kFloat32,
        core::TensorLayout::kNchw,
        definition.target_shape,
    };
    preprocess::PreprocessedFrame actual;
    const preprocess::Preprocessor preprocessor;
    const core::Status preprocess_status =
        preprocessor.preprocess(input_bgr, input_info, &actual);
    if (!preprocess_status.ok()) {
        throw PreprocessError(definition.id + ": Preprocessor failed code=" +
                              std::to_string(static_cast<int>(preprocess_status.code())) +
                              " message=" + preprocess_status.message());
    }

    fs::path golden_path;
    level_a::resolve_asset_path_under_root(
        data_root, definition.golden_path, &golden_path);
    const std::vector<std::uint8_t> golden_bytes =
        read_bytes(golden_path, definition.id, "golden tensor");
    const std::size_t expected_golden_bytes = definition.golden_element_count * 4U;
    if (golden_bytes.size() != expected_golden_bytes) {
        throw InputError(definition.id + ": golden tensor byte size actual=" +
                         std::to_string(golden_bytes.size()) + " expected=" +
                         std::to_string(expected_golden_bytes));
    }
    std::vector<float> golden(definition.golden_element_count);
    std::memcpy(golden.data(), golden_bytes.data(), golden_bytes.size());

    CaseResult result;
    result.id = definition.id;
    result.tolerance_profile = definition.tolerance_profile;
    result.target_shape = definition.target_shape;
    result.element_count = definition.golden_element_count;
    result.mae_limit = tolerance.mae_limit;
    result.max_abs_limit = tolerance.max_abs_limit;
    result.metadata_pass =
        compare_metadata(definition.id, actual.transform, definition.metadata);

    const core::Status tensor_status = core::validate_host_tensor(actual.tensor);
    const bool tensor_info_pass =
        actual.tensor.info.dtype == core::TensorDataType::kFloat32 &&
        actual.tensor.info.layout == core::TensorLayout::kNchw &&
        actual.tensor.info.shape == definition.target_shape;
    const bool tensor_size_pass = actual.tensor.data.size() == golden.size();
    if (!tensor_status.ok()) {
        std::cerr << definition.id << ": output HostTensor invalid: "
                  << tensor_status.message() << '\n';
    }
    if (!tensor_info_pass) {
        std::cerr << definition.id << ": output TensorInfo does not match target_shape\n";
    }
    if (!tensor_size_pass) {
        std::cerr << definition.id << ": output element count actual="
                  << actual.tensor.data.size() << " expected=" << golden.size() << '\n';
    }

    const level_a::TensorComparisonResult comparison =
        level_a::compare_preprocess_tensors(actual.tensor.data,
                                            golden,
                                            definition.target_shape,
                                            tolerance.mae_limit,
                                            tolerance.max_abs_limit);
    result.mae = comparison.mae;
    result.max_abs = comparison.max_abs;
    result.max_error_index = comparison.max_error_index;
    result.max_error_channel = comparison.max_error_channel;
    result.max_error_y = comparison.max_error_y;
    result.max_error_x = comparison.max_error_x;
    result.golden_at_max_error = comparison.golden_at_max_error;
    result.actual_at_max_error = comparison.actual_at_max_error;
    result.nonfinite_detected = comparison.nonfinite_detected;
    result.nonfinite_source = comparison.nonfinite_source;
    if (comparison.nonfinite_detected) {
        result.max_error_index = comparison.nonfinite_index;
        result.max_error_channel = comparison.nonfinite_channel;
        result.max_error_y = comparison.nonfinite_y;
        result.max_error_x = comparison.nonfinite_x;
        result.golden_at_max_error = comparison.nonfinite_golden;
        result.actual_at_max_error = comparison.nonfinite_actual;
    }
    result.max_error_region = tensor_size_pass
                                  ? classify_region(definition,
                                                    result.max_error_y,
                                                    result.max_error_x)
                                  : "unavailable";
    result.tensor_pass = tensor_status.ok() && tensor_info_pass && tensor_size_pass &&
                         comparison.pass;
    result.overall_pass = result.metadata_pass && result.tensor_pass;

    std::cout << std::setprecision(17) << definition.id
              << ": elements=" << result.element_count << " mae=" << result.mae
              << " max_abs=" << result.max_abs
              << " mae_limit=" << result.mae_limit
              << " max_abs_limit=" << result.max_abs_limit
              << " metadata=" << (result.metadata_pass ? "PASS" : "FAIL")
              << " tensor=" << (result.tensor_pass ? "PASS" : "FAIL")
              << " overall=" << (result.overall_pass ? "PASS" : "FAIL") << '\n';
    if (!result.tensor_pass) {
        if (result.nonfinite_detected) {
            std::cerr << definition.id << ": non-finite comparison source="
                      << result.nonfinite_source
                      << " index=" << result.max_error_index
                      << " channel=" << result.max_error_channel
                      << " y=" << result.max_error_y << " x=" << result.max_error_x
                      << " golden=" << result.golden_at_max_error
                      << " actual=" << result.actual_at_max_error << '\n';
        }
        std::cerr << std::setprecision(17) << definition.id
                  << ": comparison failure mae=" << result.mae
                  << " max_abs=" << result.max_abs
                  << " max_index=" << result.max_error_index
                  << " channel=" << result.max_error_channel
                  << " y=" << result.max_error_y << " x=" << result.max_error_x
                  << " golden=" << result.golden_at_max_error
                  << " actual=" << result.actual_at_max_error
                  << " region=" << result.max_error_region
                  << " python_opencv=4.10.0 cpp_opencv=" << CV_VERSION << '\n';
    }
    return result;
}

std::string json_escape(const std::string& value) {
    std::ostringstream escaped;
    for (const unsigned char character : value) {
        switch (character) {
            case '"':
                escaped << "\\\"";
                break;
            case '\\':
                escaped << "\\\\";
                break;
            case '\n':
                escaped << "\\n";
                break;
            case '\r':
                escaped << "\\r";
                break;
            case '\t':
                escaped << "\\t";
                break;
            default:
                if (character < 0x20U) {
                    escaped << "\\u" << std::hex << std::setw(4)
                            << std::setfill('0') << static_cast<unsigned int>(character)
                            << std::dec << std::setfill(' ');
                } else {
                    escaped << static_cast<char>(character);
                }
        }
    }
    return escaped.str();
}

void write_shape(std::ostream& output,
                 const std::vector<std::int64_t>& shape) {
    output << '[';
    for (std::size_t index = 0; index < shape.size(); ++index) {
        if (index != 0U) {
            output << ", ";
        }
        output << shape[index];
    }
    output << ']';
}

void write_json_float(std::ostream& output, float value) {
    if (std::isnan(value)) {
        output << "\"nan\"";
    } else if (std::isinf(value)) {
        output << (value > 0.0F ? "\"+inf\"" : "\"-inf\"");
    } else {
        output << value;
    }
}

void write_report(const fs::path& report_path,
                  const level_a::Manifest& manifest,
                  const std::vector<CaseResult>& results) {
    if (results.empty()) {
        throw ReportError("report: no case results are available");
    }
    const fs::path parent = report_path.parent_path();
    std::error_code directory_error;
    if (!parent.empty()) {
        fs::create_directories(parent, directory_error);
        if (directory_error) {
            throw ReportError("report: cannot create parent directory: " +
                              directory_error.message());
        }
    }
    std::ofstream output(report_path);
    if (!output) {
        throw ReportError("report: cannot open output file: " + report_path.string());
    }
    output << std::setprecision(17);
    const auto exact = manifest.tolerances.at("exact");
    const auto resize = manifest.tolerances.at("resize");
    const std::size_t passed_count = static_cast<std::size_t>(std::count_if(
        results.begin(), results.end(), [](const CaseResult& result) {
            return result.overall_pass;
        }));
    double aggregate_max_mae = 0.0;
    double aggregate_max_abs = 0.0;
    double closest_margin = std::numeric_limits<double>::max();
    std::string closest_case;
    std::string closest_metric;
    for (const CaseResult& result : results) {
        aggregate_max_mae = std::max(aggregate_max_mae, result.mae);
        aggregate_max_abs = std::max(aggregate_max_abs, result.max_abs);
        const double mae_margin = result.mae_limit - result.mae;
        const double max_abs_margin = result.max_abs_limit - result.max_abs;
        if (mae_margin < closest_margin) {
            closest_margin = mae_margin;
            closest_case = result.id;
            closest_metric = "mae";
        }
        if (max_abs_margin < closest_margin) {
            closest_margin = max_abs_margin;
            closest_case = result.id;
            closest_metric = "max_abs";
        }
    }

    output << "{\n"
           << "  \"schema_version\": 1,\n"
           << "  \"validation\": \"preprocess_level_a\",\n"
           << "  \"reference\": {\n"
           << "    \"implementation\": \"" << json_escape(manifest.reference.implementation)
           << "\",\n"
           << "    \"python_version\": \"" << json_escape(manifest.reference.python_version)
           << "\",\n"
           << "    \"numpy_version\": \"" << json_escape(manifest.reference.numpy_version)
           << "\",\n"
           << "    \"opencv_version\": \"" << json_escape(manifest.reference.opencv_version)
           << "\",\n"
           << "    \"input_color_order\": \"BGR\",\n"
           << "    \"output_color_order\": \"RGB\",\n"
           << "    \"interpolation\": \"INTER_LINEAR\",\n"
           << "    \"padding_value\": 114\n"
           << "  },\n"
           << "  \"cpp\": {\n"
           << "    \"opencv_version\": \"" << CV_VERSION << "\"\n"
           << "  },\n"
           << "  \"tensor_format\": {\n"
           << "    \"dtype\": \"float32\",\n"
           << "    \"byte_order\": \"little_endian\",\n"
           << "    \"layout\": \"NCHW\"\n"
           << "  },\n"
           << "  \"tolerance_profiles\": {\n"
           << "    \"exact\": {\"mae_limit\": " << exact.mae_limit
           << ", \"max_abs_limit\": " << exact.max_abs_limit << "},\n"
           << "    \"resize\": {\"mae_limit\": " << resize.mae_limit
           << ", \"max_abs_limit\": " << resize.max_abs_limit << "}\n"
           << "  },\n"
           << "  \"cases\": [\n";
    for (std::size_t index = 0; index < results.size(); ++index) {
        const CaseResult& result = results[index];
        output << "    {\n"
               << "      \"id\": \"" << json_escape(result.id) << "\",\n"
               << "      \"target_shape\": ";
        write_shape(output, result.target_shape);
        output << ",\n"
               << "      \"tolerance_profile\": \""
               << json_escape(result.tolerance_profile) << "\",\n"
               << "      \"element_count\": " << result.element_count << ",\n"
               << "      \"mae\": " << result.mae << ",\n"
               << "      \"max_abs\": " << result.max_abs << ",\n"
               << "      \"mae_limit\": " << result.mae_limit << ",\n"
               << "      \"max_abs_limit\": " << result.max_abs_limit << ",\n"
               << "      \"metadata_pass\": "
               << (result.metadata_pass ? "true" : "false") << ",\n"
               << "      \"tensor_pass\": "
               << (result.tensor_pass ? "true" : "false") << ",\n"
               << "      \"overall_pass\": "
               << (result.overall_pass ? "true" : "false") << ",\n"
               << "      \"max_error\": {\n"
               << "        \"index\": " << result.max_error_index << ",\n"
               << "        \"channel\": " << result.max_error_channel << ",\n"
               << "        \"y\": " << result.max_error_y << ",\n"
               << "        \"x\": " << result.max_error_x << ",\n"
               << "        \"golden\": ";
        write_json_float(output, result.golden_at_max_error);
        output << ",\n"
               << "        \"actual\": ";
        write_json_float(output, result.actual_at_max_error);
        output << ",\n"
               << "        \"region\": \"" << json_escape(result.max_error_region)
               << "\"\n"
               << "      }\n"
               << "    }" << (index + 1U == results.size() ? "\n" : ",\n");
    }
    const bool final_pass = passed_count == results.size();
    output << "  ],\n"
           << "  \"aggregate\": {\n"
           << "    \"case_count\": " << results.size() << ",\n"
           << "    \"passed_case_count\": " << passed_count << ",\n"
           << "    \"max_mae\": " << aggregate_max_mae << ",\n"
           << "    \"max_abs\": " << aggregate_max_abs << ",\n"
           << "    \"closest_limit_case\": \"" << json_escape(closest_case)
           << "\",\n"
           << "    \"closest_limit_metric\": \"" << json_escape(closest_metric)
           << "\",\n"
           << "    \"closest_limit_margin\": " << closest_margin << ",\n"
           << "    \"final_pass\": " << (final_pass ? "true" : "false") << "\n"
           << "  },\n"
           << "  \"frozen_case\": {\n"
           << "    \"id\": \"frozen_640_checkerboard\",\n"
           << "    \"target_shape\": [1, 3, 640, 640]\n"
           << "  }\n"
           << "}\n";
    if (!output) {
        throw ReportError("report: failed while writing output file: " +
                          report_path.string());
    }
}

int run(int argc, char** argv) {
    if (!host_is_little_endian()) {
        throw InputError(
            "platform: little-endian host is required for .f32le golden tensors");
    }
    const Options options = parse_options(argc, argv);
    const level_a::Manifest manifest = level_a::load_manifest(
        options.manifest, options.data_root / "SHA256SUMS");
    std::vector<CaseResult> results;
    results.reserve(manifest.cases.size());
    for (const level_a::CaseDefinition& definition : manifest.cases) {
        results.push_back(validate_case(definition,
                                        manifest.tolerances.at(
                                            definition.tolerance_profile),
                                        options.data_root));
    }
    write_report(options.report, manifest, results);
    const bool all_pass = std::all_of(
        results.begin(), results.end(), [](const CaseResult& result) {
            return result.overall_pass;
        });
    return all_pass ? 0 : kComparisonFailure;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        return run(argc, argv);
    } catch (const PreprocessError& exception) {
        std::cerr << exception.what() << '\n';
        return kPreprocessFailure;
    } catch (const ReportError& exception) {
        std::cerr << exception.what() << '\n';
        return kReportFailure;
    } catch (const InputError& exception) {
        std::cerr << exception.what() << '\n';
        return kInputFailure;
    } catch (const level_a::ManifestError& exception) {
        std::cerr << exception.what() << '\n';
        return kInputFailure;
    } catch (const std::exception& exception) {
        std::cerr << "validator: unexpected input/schema error: " << exception.what()
                  << '\n';
        return kInputFailure;
    }
}
