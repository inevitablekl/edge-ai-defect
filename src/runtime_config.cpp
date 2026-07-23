#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <limits>
#include <string>
#include <system_error>
#include <unordered_set>
#include <utility>
#include <vector>

namespace edge_ai_defect::runtime {
namespace {

using core::ErrorCode;
using core::Status;

Status schema_error(const std::string& path, const std::string& detail) {
    return Status::failure(ErrorCode::kSchemaViolation, path + ": " + detail);
}

Status parse_error(const std::string& path, const std::string& detail) {
    return Status::failure(ErrorCode::kParseError, path + ": " + detail);
}

Status validate_mapping(const YAML::Node& node,
                        const std::string& path,
                        const std::vector<std::string>& allowed_keys) {
    if (!node.IsMap()) {
        return schema_error(path, "expected a mapping");
    }

    std::unordered_set<std::string> seen_keys;
    for (const auto& entry : node) {
        if (!entry.first.IsScalar()) {
            return schema_error(path, "mapping key must be a scalar");
        }

        const std::string key = entry.first.Scalar();
        const std::string key_path =
            path == "$" ? "$." + key : path + "." + key;
        if (!seen_keys.insert(key).second) {
            return schema_error(key_path, "duplicate key");
        }
        if (std::find(allowed_keys.begin(), allowed_keys.end(), key) ==
            allowed_keys.end()) {
            return schema_error(key_path, "unknown field");
        }
    }

    for (const std::string& key : allowed_keys) {
        if (!node[key].IsDefined()) {
            const std::string key_path =
                path == "$" ? "$." + key : path + "." + key;
            return schema_error(key_path, "missing required field");
        }
    }
    return Status::success();
}

Status require_scalar(const YAML::Node& node, const std::string& path) {
    if (!node.IsScalar()) {
        return schema_error(path, "expected a scalar");
    }
    return Status::success();
}

template <typename Value>
Status parse_scalar(const YAML::Node& node,
                    const std::string& path,
                    Value* output) {
    const Status scalar_status = require_scalar(node, path);
    if (!scalar_status.ok()) {
        return scalar_status;
    }

    try {
        *output = node.as<Value>();
    } catch (const YAML::BadConversion& exception) {
        return parse_error(path,
                           "scalar conversion failed: " +
                               std::string(exception.what()));
    }
    return Status::success();
}

Status parse_nonempty_path(const YAML::Node& node,
                           const std::string& path,
                           const std::filesystem::path& config_directory,
                           std::filesystem::path* output) {
    std::string raw_path;
    const Status parse_status = parse_scalar(node, path, &raw_path);
    if (!parse_status.ok()) {
        return parse_status;
    }
    if (raw_path.empty()) {
        return schema_error(path, "must not be empty");
    }

    const std::filesystem::path parsed_path(raw_path);
    *output = (parsed_path.is_absolute() ? parsed_path
                                         : config_directory / parsed_path)
                  .lexically_normal();
    return Status::success();
}

Status parse_schema_version(const YAML::Node& root, std::int64_t* output) {
    std::int64_t schema_version = 0;
    const Status status =
        parse_scalar(root["schema_version"], "schema_version", &schema_version);
    if (!status.ok()) {
        return status;
    }
    *output = schema_version;
    return Status::success();
}

Status parse_positive_uint32(const YAML::Node& node,
                             const std::string& path,
                             std::uint32_t* output) {
    std::int64_t value = 0;
    const Status status = parse_scalar(node, path, &value);
    if (!status.ok()) {
        return status;
    }
    if (value <= 0 || static_cast<std::uint64_t>(value) >
                          std::numeric_limits<std::uint32_t>::max()) {
        return schema_error(path, "must be a positive uint32");
    }
    *output = static_cast<std::uint32_t>(value);
    return Status::success();
}

Status parse_backend(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(node, "backend", {"type"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status = parse_scalar(node["type"], "backend.type", &output->backend_type);
    if (!status.ok()) {
        return status;
    }
    if (output->backend_type != "onnxruntime_cpu") {
        return schema_error("backend.type", "must be exactly 'onnxruntime_cpu'");
    }
    return Status::success();
}

Status parse_model(const YAML::Node& node,
                   const std::filesystem::path& config_directory,
                   RuntimeConfig* output) {
    const Status mapping_status =
        validate_mapping(node, "model", {"contract_path", "model_path"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status = parse_nonempty_path(node["contract_path"],
                                        "model.contract_path",
                                        config_directory,
                                        &output->model_contract_path);
    if (!status.ok()) {
        return status;
    }
    return parse_nonempty_path(node["model_path"],
                               "model.model_path",
                               config_directory,
                               &output->model_path);
}

Status parse_input(const YAML::Node& node,
                   const std::filesystem::path& config_directory,
                   RuntimeConfig* output) {
    const Status mapping_status =
        validate_mapping(node, "input", {"type", "directory"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status = parse_scalar(node["type"], "input.type", &output->input_type);
    if (!status.ok()) {
        return status;
    }
    if (output->input_type != "directory") {
        return schema_error("input.type", "must be exactly 'directory'");
    }
    return parse_nonempty_path(node["directory"],
                               "input.directory",
                               config_directory,
                               &output->input_directory);
}

Status parse_output(const YAML::Node& node,
                    const std::filesystem::path& config_directory,
                    RuntimeConfig* output) {
    const Status mapping_status =
        validate_mapping(node, "output", {"json_path", "console", "overwrite"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status = parse_nonempty_path(node["json_path"],
                                        "output.json_path",
                                        config_directory,
                                        &output->output_json_path);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["console"], "output.console", &output->output_console);
    if (!status.ok()) {
        return status;
    }
    return parse_scalar(node["overwrite"],
                        "output.overwrite",
                        &output->output_overwrite);
}

Status parse_postprocess(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(
        node,
        "postprocess",
        {"confidence_threshold", "iou_threshold", "max_nms", "max_det",
         "max_wh", "agnostic", "multi_label"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    postprocess::PostprocessConfig config;
    Status status = parse_scalar(node["confidence_threshold"],
                                 "postprocess.confidence_threshold",
                                 &config.confidence_threshold);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["iou_threshold"],
                          "postprocess.iou_threshold",
                          &config.iou_threshold);
    if (!status.ok()) {
        return status;
    }

    std::int64_t max_nms = 0;
    status = parse_scalar(node["max_nms"], "postprocess.max_nms", &max_nms);
    if (!status.ok()) {
        return status;
    }
    std::int64_t max_det = 0;
    status = parse_scalar(node["max_det"], "postprocess.max_det", &max_det);
    if (!status.ok()) {
        return status;
    }
    if (max_nms < 0 || max_det < 0 ||
        static_cast<std::uint64_t>(max_nms) >
            std::numeric_limits<std::size_t>::max() ||
        static_cast<std::uint64_t>(max_det) >
            std::numeric_limits<std::size_t>::max()) {
        return schema_error("postprocess", "max_nms and max_det must fit size_t");
    }
    config.max_nms = static_cast<std::size_t>(max_nms);
    config.max_det = static_cast<std::size_t>(max_det);

    status = parse_scalar(node["max_wh"], "postprocess.max_wh", &config.max_wh);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["agnostic"], "postprocess.agnostic", &config.agnostic);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["multi_label"],
                          "postprocess.multi_label",
                          &config.multi_label);
    if (!status.ok()) {
        return status;
    }

    status = postprocess::validate_postprocess_config(config);
    if (!status.ok()) {
        return Status::failure(status.code(),
                               "postprocess: " + status.message());
    }
    output->postprocess_config = config;
    return Status::success();
}

Status parse_timing(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(node, "timing", {"enabled"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }
    return parse_scalar(node["enabled"], "timing.enabled", &output->timing_enabled);
}

Status parse_model_v2(const YAML::Node& node,
                      const std::filesystem::path& config_directory,
                      RuntimeConfig* output) {
    const Status mapping_status =
        validate_mapping(node, "model", {"path", "contract_path"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status = parse_nonempty_path(node["path"],
                                        "model.path",
                                        config_directory,
                                        &output->model_path);
    if (!status.ok()) {
        return status;
    }
    return parse_nonempty_path(node["contract_path"],
                               "model.contract_path",
                               config_directory,
                               &output->model_contract_path);
}

Status parse_onnxruntime_v2(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(
        node,
        "onnxruntime",
        {"execution_mode", "graph_optimization_level", "intra_op_threads",
         "inter_op_threads", "intra_op_allow_spinning",
         "inter_op_allow_spinning", "cpu_arena_enabled",
         "memory_pattern_enabled"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    OnnxRuntimeConfig config;
    Status status = parse_scalar(node["execution_mode"],
                                 "onnxruntime.execution_mode",
                                 &config.execution_mode);
    if (!status.ok()) {
        return status;
    }
    if (config.execution_mode != "sequential") {
        return schema_error("onnxruntime.execution_mode",
                            "must be exactly 'sequential'");
    }
    status = parse_scalar(node["graph_optimization_level"],
                          "onnxruntime.graph_optimization_level",
                          &config.graph_optimization_level);
    if (!status.ok()) {
        return status;
    }
    if (config.graph_optimization_level != "all") {
        return schema_error("onnxruntime.graph_optimization_level",
                            "must be exactly 'all'");
    }
    status = parse_positive_uint32(node["intra_op_threads"],
                                   "onnxruntime.intra_op_threads",
                                   &config.intra_op_threads);
    if (!status.ok()) {
        return status;
    }
    status = parse_positive_uint32(node["inter_op_threads"],
                                   "onnxruntime.inter_op_threads",
                                   &config.inter_op_threads);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["intra_op_allow_spinning"],
                          "onnxruntime.intra_op_allow_spinning",
                          &config.intra_op_allow_spinning);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["inter_op_allow_spinning"],
                          "onnxruntime.inter_op_allow_spinning",
                          &config.inter_op_allow_spinning);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["cpu_arena_enabled"],
                          "onnxruntime.cpu_arena_enabled",
                          &config.cpu_arena_enabled);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["memory_pattern_enabled"],
                          "onnxruntime.memory_pattern_enabled",
                          &config.memory_pattern_enabled);
    if (!status.ok()) {
        return status;
    }

    output->onnxruntime = config;
    return Status::success();
}

Status parse_runtime_v2(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(
        node, "runtime", {"opencv_num_threads"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }
    return parse_positive_uint32(node["opencv_num_threads"],
                                 "runtime.opencv_num_threads",
                                 &output->opencv_num_threads);
}

Status parse_postprocess_v2(const YAML::Node& node, RuntimeConfig* output) {
    const Status mapping_status = validate_mapping(
        node,
        "postprocess",
        {"conf_threshold", "iou_threshold", "max_nms", "max_det",
         "max_wh", "agnostic"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    postprocess::PostprocessConfig config;
    Status status = parse_scalar(node["conf_threshold"],
                                 "postprocess.conf_threshold",
                                 &config.confidence_threshold);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["iou_threshold"],
                          "postprocess.iou_threshold",
                          &config.iou_threshold);
    if (!status.ok()) {
        return status;
    }

    std::int64_t max_nms = 0;
    status = parse_scalar(node["max_nms"], "postprocess.max_nms", &max_nms);
    if (!status.ok()) {
        return status;
    }
    std::int64_t max_det = 0;
    status = parse_scalar(node["max_det"], "postprocess.max_det", &max_det);
    if (!status.ok()) {
        return status;
    }
    if (max_nms < 0 || max_det < 0 ||
        static_cast<std::uint64_t>(max_nms) >
            std::numeric_limits<std::size_t>::max() ||
        static_cast<std::uint64_t>(max_det) >
            std::numeric_limits<std::size_t>::max()) {
        return schema_error("postprocess", "max_nms and max_det must fit size_t");
    }
    config.max_nms = static_cast<std::size_t>(max_nms);
    config.max_det = static_cast<std::size_t>(max_det);

    status = parse_scalar(node["max_wh"], "postprocess.max_wh", &config.max_wh);
    if (!status.ok()) {
        return status;
    }
    status = parse_scalar(node["agnostic"], "postprocess.agnostic", &config.agnostic);
    if (!status.ok()) {
        return status;
    }
    config.multi_label = false;

    status = postprocess::validate_postprocess_config(config);
    if (!status.ok()) {
        return Status::failure(status.code(),
                               "postprocess: " + status.message());
    }
    output->postprocess_config = config;
    return Status::success();
}

Status parse_runtime_config_v1(const YAML::Node& root,
                               const std::filesystem::path& config_directory,
                               RuntimeConfig* output) {
    const Status root_status = validate_mapping(
        root,
        "$",
        {"schema_version", "backend", "model", "input", "output",
         "postprocess", "timing"});
    if (!root_status.ok()) {
        return root_status;
    }

    RuntimeConfig config;
    config.schema_version = 1;
    Status status = parse_backend(root["backend"], &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_model(root["model"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_input(root["input"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_output(root["output"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_postprocess(root["postprocess"], &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_timing(root["timing"], &config);
    if (!status.ok()) {
        return status;
    }

    *output = std::move(config);
    return Status::success();
}

Status parse_runtime_config_v2(const YAML::Node& root,
                               const std::filesystem::path& config_directory,
                               RuntimeConfig* output) {
    const Status root_status = validate_mapping(
        root,
        "$",
        {"schema_version", "backend", "onnxruntime", "runtime", "model",
         "input", "output", "postprocess"});
    if (!root_status.ok()) {
        return root_status;
    }

    RuntimeConfig config;
    config.schema_version = 2;
    Status status = parse_backend(root["backend"], &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_onnxruntime_v2(root["onnxruntime"], &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_runtime_v2(root["runtime"], &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_model_v2(root["model"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_input(root["input"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_output(root["output"], config_directory, &config);
    if (!status.ok()) {
        return status;
    }
    status = parse_postprocess_v2(root["postprocess"], &config);
    if (!status.ok()) {
        return status;
    }

    *output = std::move(config);
    return Status::success();
}

Status parse_runtime_config(const YAML::Node& root,
                            const std::filesystem::path& config_directory,
                            RuntimeConfig* output) {
    std::int64_t schema_version = 0;
    Status status = parse_schema_version(root, &schema_version);
    if (!status.ok()) {
        return status;
    }
    if (schema_version == 1) {
        return parse_runtime_config_v1(root, config_directory, output);
    }
    if (schema_version == 2) {
        return parse_runtime_config_v2(root, config_directory, output);
    }
    return schema_error("schema_version", "must be exactly 1 or 2");
}

}  // namespace

core::Status RuntimeConfigLoader::load(
    const std::filesystem::path& config_path,
    RuntimeConfig* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "output: RuntimeConfig pointer must not be null");
    }
    if (config_path.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "config_path must not be empty");
    }

    std::error_code error;
    const std::filesystem::path resolved_config_path =
        std::filesystem::absolute(config_path, error).lexically_normal();
    if (error) {
        return Status::failure(ErrorCode::kIoError,
                               "Cannot resolve runtime config path '" +
                                   config_path.string() + "': " + error.message());
    }

    std::ifstream input(resolved_config_path);
    if (!input.is_open()) {
        return Status::failure(ErrorCode::kIoError,
                               "Runtime config file is not readable: " +
                                   resolved_config_path.string());
    }

    try {
        const YAML::Node root = YAML::Load(input);
        if (input.bad()) {
            return Status::failure(ErrorCode::kIoError,
                                   "Failed while reading runtime config: " +
                                       resolved_config_path.string());
        }

        RuntimeConfig parsed_config;
        const Status parse_status = parse_runtime_config(
            root, resolved_config_path.parent_path(), &parsed_config);
        if (!parse_status.ok()) {
            return parse_status;
        }

        *output = std::move(parsed_config);
        return Status::success();
    } catch (const YAML::Exception& exception) {
        return parse_error("$", "YAML error: " + std::string(exception.what()));
    }
}

}  // namespace edge_ai_defect::runtime
