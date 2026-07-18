#include "edge_ai_defect/postprocess/postprocessor.hpp"

#include <yaml-cpp/yaml.h>

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace core = edge_ai_defect::core;
namespace fs = std::filesystem;
namespace postprocess = edge_ai_defect::postprocess;
namespace preprocess = edge_ai_defect::preprocess;

constexpr std::size_t kElementCount = 84000U;
constexpr double kConfidenceLimit = 1.0e-6;
constexpr double kBboxLimit = 1.0e-4;

struct Options {
    fs::path data_root;
    fs::path cpp_output_root;
    fs::path report_root;
};

struct DetectionRecord {
    float x1 = 0.0F;
    float y1 = 0.0F;
    float x2 = 0.0F;
    float y2 = 0.0F;
    float confidence = 0.0F;
    int class_id = 0;
    std::size_t candidate_index = 0U;
};

struct Comparison {
    std::size_t golden_count = 0U;
    std::size_t cpp_count = 0U;
    bool count_match = false;
    bool order_match = true;
    bool class_id_match = true;
    bool candidate_index_match = true;
    bool finite = true;
    double confidence_sum_abs = 0.0;
    double confidence_max_abs = 0.0;
    std::size_t confidence_max_index = 0U;
    double bbox_sum_abs = 0.0;
    double bbox_max_abs = 0.0;
    std::size_t bbox_max_index = 0U;
    std::string bbox_max_coordinate = "x1";
    std::string first_exact_mismatch;
    bool pass = false;
};

bool host_is_little_endian() noexcept {
    const std::uint16_t value = 1U;
    return *reinterpret_cast<const std::uint8_t*>(&value) == 1U;
}

Options parse_options(int argc, char* argv[]) {
    if (argc != 7) {
        throw std::runtime_error(
            "Expected --data-root <path> --cpp-output-root <path> --report-root <path>");
    }
    Options options;
    for (int index = 1; index < argc; index += 2) {
        const std::string name = argv[index];
        const fs::path value = argv[index + 1];
        if (name == "--data-root") {
            options.data_root = value;
        } else if (name == "--cpp-output-root") {
            options.cpp_output_root = value;
        } else if (name == "--report-root") {
            options.report_root = value;
        } else {
            throw std::runtime_error("Unknown option: " + name);
        }
    }
    if (options.data_root.empty() || options.cpp_output_root.empty() ||
        options.report_root.empty()) {
        throw std::runtime_error("PostProcessor reference paths must not be empty");
    }
    return options;
}

std::vector<float> read_f32le(const fs::path& path) {
    if (!host_is_little_endian()) {
        throw std::runtime_error("PostProcessor reference requires little-endian host");
    }
    std::error_code error;
    if (!fs::is_regular_file(path, error) || error ||
        fs::file_size(path, error) != kElementCount * sizeof(float)) {
        throw std::runtime_error("Invalid raw f32le asset: " + path.string());
    }
    std::vector<float> values(kElementCount);
    std::ifstream input(path, std::ios::binary);
    input.read(reinterpret_cast<char*>(values.data()),
               static_cast<std::streamsize>(values.size() * sizeof(float)));
    if (!input) {
        throw std::runtime_error("Cannot read raw f32le asset: " + path.string());
    }
    return values;
}

float parse_float(const std::string& token) {
    std::istringstream stream(token);
    stream.imbue(std::locale::classic());
    float value = 0.0F;
    stream >> value;
    if (!stream || !stream.eof()) {
        throw std::runtime_error("Invalid float TSV field: " + token);
    }
    return value;
}

int parse_int(const std::string& token) {
    std::istringstream stream(token);
    stream.imbue(std::locale::classic());
    int value = 0;
    stream >> value;
    if (!stream || !stream.eof()) {
        throw std::runtime_error("Invalid integer TSV field: " + token);
    }
    return value;
}

std::size_t parse_size(const std::string& token) {
    std::istringstream stream(token);
    stream.imbue(std::locale::classic());
    std::size_t value = 0U;
    stream >> value;
    if (!stream || !stream.eof()) {
        throw std::runtime_error("Invalid size TSV field: " + token);
    }
    return value;
}

std::vector<std::string> split_tsv(const std::string& line) {
    std::vector<std::string> fields;
    std::istringstream stream(line);
    std::string field;
    while (std::getline(stream, field, '\t')) {
        fields.push_back(field);
    }
    return fields;
}

std::vector<DetectionRecord> read_tsv(const fs::path& path) {
    std::ifstream input(path);
    input.imbue(std::locale::classic());
    if (!input) {
        throw std::runtime_error("Cannot read golden TSV: " + path.string());
    }
    std::string line;
    if (!std::getline(input, line) ||
        line != "x1\ty1\tx2\ty2\tconfidence\tclass_id\tcandidate_index") {
        throw std::runtime_error("Invalid TSV header: " + path.string());
    }
    std::vector<DetectionRecord> values;
    while (std::getline(input, line)) {
        const std::vector<std::string> fields = split_tsv(line);
        if (fields.size() != 7U) {
            throw std::runtime_error("Invalid TSV record: " + path.string());
        }
        values.push_back({parse_float(fields[0]),
                          parse_float(fields[1]),
                          parse_float(fields[2]),
                          parse_float(fields[3]),
                          parse_float(fields[4]),
                          parse_int(fields[5]),
                          parse_size(fields[6])});
    }
    return values;
}

postprocess::PostprocessConfig read_config(const fs::path& path) {
    const YAML::Node root = YAML::LoadFile(path.string());
    postprocess::PostprocessConfig config;
    config.confidence_threshold = root["confidence_threshold"].as<float>();
    config.iou_threshold = root["iou_threshold"].as<float>();
    config.max_nms = root["max_nms"].as<std::size_t>();
    config.max_det = root["max_det"].as<std::size_t>();
    config.max_wh = root["max_wh"].as<float>();
    config.agnostic = root["agnostic"].as<bool>();
    config.multi_label = root["multi_label"].as<bool>();
    return config;
}

preprocess::ImageTransformMetadata read_metadata(const fs::path& path) {
    const YAML::Node root = YAML::LoadFile(path.string());
    return {root["original_width"].as<int>(),
            root["original_height"].as<int>(),
            root["target_width"].as<int>(),
            root["target_height"].as<int>(),
            root["resized_width"].as<int>(),
            root["resized_height"].as<int>(),
            root["gain"].as<double>(),
            root["pad_left"].as<int>(),
            root["pad_right"].as<int>(),
            root["pad_top"].as<int>(),
            root["pad_bottom"].as<int>()};
}

std::vector<DetectionRecord> to_records(
    const std::vector<postprocess::Detection>& detections) {
    std::vector<DetectionRecord> records;
    records.reserve(detections.size());
    for (const postprocess::Detection& detection : detections) {
        records.push_back({detection.x1,
                           detection.y1,
                           detection.x2,
                           detection.y2,
                           detection.confidence,
                           detection.class_id,
                           detection.candidate_index});
    }
    return records;
}

void write_tsv(const fs::path& path, const std::vector<DetectionRecord>& records) {
    fs::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::trunc);
    output.imbue(std::locale::classic());
    if (!output) {
        throw std::runtime_error("Cannot write C++ TSV: " + path.string());
    }
    output << std::setprecision(9)
           << "x1\ty1\tx2\ty2\tconfidence\tclass_id\tcandidate_index\n";
    for (const DetectionRecord& record : records) {
        output << record.x1 << '\t' << record.y1 << '\t' << record.x2 << '\t'
               << record.y2 << '\t' << record.confidence << '\t' << record.class_id
               << '\t' << record.candidate_index << '\n';
    }
    if (!output) {
        throw std::runtime_error("Cannot finish C++ TSV: " + path.string());
    }
}

bool finite(const DetectionRecord& record) noexcept {
    return std::isfinite(record.x1) && std::isfinite(record.y1) &&
           std::isfinite(record.x2) && std::isfinite(record.y2) &&
           std::isfinite(record.confidence);
}

void update_bbox_error(Comparison& comparison,
                       double error,
                       std::size_t index,
                       const char* coordinate) {
    comparison.bbox_sum_abs += error;
    if (error > comparison.bbox_max_abs) {
        comparison.bbox_max_abs = error;
        comparison.bbox_max_index = index;
        comparison.bbox_max_coordinate = coordinate;
    }
}

Comparison compare(const std::vector<DetectionRecord>& golden,
                   const std::vector<DetectionRecord>& actual) {
    Comparison comparison;
    comparison.golden_count = golden.size();
    comparison.cpp_count = actual.size();
    comparison.count_match = golden.size() == actual.size();
    const std::size_t common_count = std::min(golden.size(), actual.size());
    for (std::size_t index = 0U; index < common_count; ++index) {
        const DetectionRecord& expected = golden[index];
        const DetectionRecord& observed = actual[index];
        if (!finite(expected) || !finite(observed)) {
            comparison.finite = false;
            comparison.confidence_max_abs = std::numeric_limits<double>::infinity();
            comparison.bbox_max_abs = std::numeric_limits<double>::infinity();
            if (comparison.first_exact_mismatch.empty()) {
                comparison.first_exact_mismatch = "non-finite field at detection " +
                                                  std::to_string(index);
            }
            continue;
        }
        if (expected.class_id != observed.class_id) {
            comparison.order_match = false;
            comparison.class_id_match = false;
            if (comparison.first_exact_mismatch.empty()) {
                comparison.first_exact_mismatch = "class_id at detection " +
                                                  std::to_string(index);
            }
        }
        if (expected.candidate_index != observed.candidate_index) {
            comparison.order_match = false;
            comparison.candidate_index_match = false;
            if (comparison.first_exact_mismatch.empty()) {
                comparison.first_exact_mismatch = "candidate_index at detection " +
                                                  std::to_string(index);
            }
        }
        const double confidence_error = std::abs(
            static_cast<double>(expected.confidence) - observed.confidence);
        comparison.confidence_sum_abs += confidence_error;
        if (confidence_error > comparison.confidence_max_abs) {
            comparison.confidence_max_abs = confidence_error;
            comparison.confidence_max_index = index;
        }
        update_bbox_error(comparison,
                          std::abs(static_cast<double>(expected.x1) - observed.x1),
                          index,
                          "x1");
        update_bbox_error(comparison,
                          std::abs(static_cast<double>(expected.y1) - observed.y1),
                          index,
                          "y1");
        update_bbox_error(comparison,
                          std::abs(static_cast<double>(expected.x2) - observed.x2),
                          index,
                          "x2");
        update_bbox_error(comparison,
                          std::abs(static_cast<double>(expected.y2) - observed.y2),
                          index,
                          "y2");
    }
    if (!comparison.count_match) {
        comparison.first_exact_mismatch = "detection count";
    }
    comparison.pass = comparison.count_match && comparison.class_id_match &&
                      comparison.order_match && comparison.candidate_index_match &&
                      comparison.finite &&
                      comparison.confidence_max_abs <= kConfidenceLimit &&
                      comparison.bbox_max_abs <= kBboxLimit;
    return comparison;
}

void write_report(const fs::path& path,
                  const std::string& case_name,
                  const Comparison& comparison) {
    fs::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::trunc);
    output.imbue(std::locale::classic());
    if (!output) {
        throw std::runtime_error("Cannot write comparison report: " + path.string());
    }
    const double confidence_mean = comparison.golden_count == 0U
                                       ? 0.0
                                       : comparison.confidence_sum_abs /
                                             static_cast<double>(comparison.golden_count);
    const double bbox_mean = comparison.golden_count == 0U
                                 ? 0.0
                                 : comparison.bbox_sum_abs /
                                       static_cast<double>(comparison.golden_count * 4U);
    output << std::setprecision(17)
           << "{\n"
           << "  \"schema_version\": 1,\n"
           << "  \"evidence_id\": \"postprocessor_only\",\n"
           << "  \"case\": \"" << case_name << "\",\n"
           << "  \"cpp_environment\": {\"compiler\": \"GCC " << __VERSION__
           << "\", \"cplusplus\": " << __cplusplus << "},\n"
           << "  \"comparison\": {\n"
           << "    \"golden_detection_count\": " << comparison.golden_count << ",\n"
           << "    \"cpp_detection_count\": " << comparison.cpp_count << ",\n"
           << "    \"count_match\": " << (comparison.count_match ? "true" : "false") << ",\n"
           << "    \"order_match\": " << (comparison.order_match ? "true" : "false") << ",\n"
           << "    \"class_id_match\": " << (comparison.class_id_match ? "true" : "false") << ",\n"
           << "    \"candidate_index_match\": " << (comparison.candidate_index_match ? "true" : "false") << ",\n"
           << "    \"finite\": " << (comparison.finite ? "true" : "false") << ",\n"
           << "    \"confidence_max_abs\": " << comparison.confidence_max_abs << ",\n"
           << "    \"confidence_mean_abs\": " << confidence_mean << ",\n"
           << "    \"confidence_max_abs_detection_index\": " << comparison.confidence_max_index << ",\n"
           << "    \"bbox_max_abs\": " << comparison.bbox_max_abs << ",\n"
           << "    \"bbox_mean_abs\": " << bbox_mean << ",\n"
           << "    \"bbox_max_abs_detection_index\": " << comparison.bbox_max_index << ",\n"
           << "    \"bbox_max_abs_coordinate\": \"" << comparison.bbox_max_coordinate << "\",\n"
           << "    \"confidence_abs_limit\": " << kConfidenceLimit << ",\n"
           << "    \"bbox_coordinate_abs_limit\": " << kBboxLimit << ",\n"
           << "    \"first_exact_mismatch\": \"" << comparison.first_exact_mismatch << "\",\n"
           << "    \"pass\": " << (comparison.pass ? "true" : "false") << "\n"
           << "  }\n"
           << "}\n";
}

bool validate_case(const Options& options, const std::string& case_name) {
    const fs::path case_dir = options.data_root / case_name;
    const std::vector<float> raw = read_f32le(case_dir / "raw_output.f32le");
    const postprocess::PostprocessConfig config = read_config(case_dir / "config.json");
    const preprocess::ImageTransformMetadata metadata =
        read_metadata(case_dir / "metadata.json");
    const std::vector<DetectionRecord> golden =
        read_tsv(case_dir / "python_golden_detections.tsv");

    const core::HostTensor raw_output{
        {core::TensorDataType::kFloat32, core::TensorLayout::kBcn, {1, 10, 8400}},
        raw};
    postprocess::PostProcessor processor(config);
    std::vector<postprocess::Detection> detections;
    const core::Status process_status =
        processor.process(raw_output, metadata, &detections);
    if (!process_status.ok()) {
        throw std::runtime_error("PostProcessor::process failed for " + case_name +
                                 ": " + process_status.message());
    }

    const std::vector<DetectionRecord> actual = to_records(detections);
    write_tsv(options.cpp_output_root / case_name / "cpp_detections.tsv", actual);
    const Comparison comparison = compare(golden, actual);
    write_report(options.report_root / case_name / "comparison_report.json",
                 case_name,
                 comparison);
    if (!comparison.pass) {
        std::cerr << case_name << " failed: " << comparison.first_exact_mismatch
                  << " confidence_max_abs=" << comparison.confidence_max_abs
                  << " bbox_max_abs=" << comparison.bbox_max_abs << '\n';
    }
    return comparison.pass;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const Options options = parse_options(argc, argv);
        const std::vector<std::string> cases{
            "case_no_padding", "case_odd_padding", "case_odd_vertical_padding"};
        bool pass = true;
        for (const std::string& case_name : cases) {
            pass = validate_case(options, case_name) && pass;
        }
        if (!pass) {
            return 2;
        }
        std::cout << "PostProcessor-only Validation passed for " << cases.size()
                  << " cases\n";
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "PostProcessor-only Validation failed: " << exception.what()
                  << '\n';
        return 3;
    }
}
