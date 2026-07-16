#include "edge_ai_defect/model/model_contract_loader.hpp"

#include "edge_ai_defect/core/tensor.hpp"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

namespace edge_ai_defect::model {
namespace {

using core::ErrorCode;
using core::Status;

Status schema_error(const std::string& path, const std::string& detail) {
    return Status::failure(ErrorCode::kSchemaViolation,
                           path + ": " + detail);
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
        const std::string key_path = path == "$" ? "$." + key
                                                   : path + "." + key;
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
                    Value& output) {
    const Status scalar_status = require_scalar(node, path);
    if (!scalar_status.ok()) {
        return scalar_status;
    }

    try {
        output = node.as<Value>();
    } catch (const YAML::BadConversion& exception) {
        return parse_error(path,
                           "scalar conversion failed: " +
                               std::string(exception.what()));
    }
    return Status::success();
}

Status parse_nonempty_string(const YAML::Node& node,
                             const std::string& path,
                             std::string& output) {
    const Status status = parse_scalar(node, path, output);
    if (!status.ok()) {
        return status;
    }
    if (output.empty()) {
        return schema_error(path, "must not be empty");
    }
    return Status::success();
}

Status parse_positive_integer(const YAML::Node& node,
                              const std::string& path,
                              std::uint64_t& output) {
    std::int64_t value = 0;
    const Status status = parse_scalar(node, path, value);
    if (!status.ok()) {
        return status;
    }
    if (value <= 0) {
        return schema_error(path, "must be greater than zero");
    }
    output = static_cast<std::uint64_t>(value);
    return Status::success();
}

Status parse_shape(const YAML::Node& node,
                   const std::string& path,
                   std::vector<std::int64_t>& output) {
    if (!node.IsSequence()) {
        return Status::failure(ErrorCode::kInvalidShape,
                               path + ": expected a sequence");
    }
    if (node.size() == 0) {
        return Status::failure(ErrorCode::kInvalidShape,
                               path + ": shape must not be empty");
    }

    std::vector<std::int64_t> shape;
    shape.reserve(node.size());
    for (std::size_t index = 0; index < node.size(); ++index) {
        const std::string dimension_path =
            path + "[" + std::to_string(index) + "]";
        std::int64_t dimension = 0;
        const Status status =
            parse_scalar(node[index], dimension_path, dimension);
        if (!status.ok()) {
            return status;
        }
        if (dimension <= 0) {
            return Status::failure(
                ErrorCode::kInvalidShape,
                dimension_path + ": dimension must be positive");
        }
        shape.push_back(dimension);
    }

    std::size_t element_count = 0;
    const Status count_status =
        core::checked_element_count(shape, element_count);
    if (!count_status.ok()) {
        return Status::failure(count_status.code(),
                               path + ": " + count_status.message());
    }

    output = std::move(shape);
    return Status::success();
}

Status parse_tensor_contract(const YAML::Node& node,
                             const std::string& path,
                             TensorContract& output) {
    const Status mapping_status = validate_mapping(
        node, path, {"name", "dtype", "layout", "shape"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    TensorContract contract;
    Status status =
        parse_nonempty_string(node["name"], path + ".name", contract.name);
    if (!status.ok()) {
        return status;
    }

    std::string dtype;
    status = parse_scalar(node["dtype"], path + ".dtype", dtype);
    if (!status.ok()) {
        return status;
    }
    if (dtype != "float32") {
        return Status::failure(ErrorCode::kUnsupportedDataType,
                               path + ".dtype: unsupported value '" +
                                   dtype + "'");
    }
    contract.tensor_info.dtype = core::TensorDataType::kFloat32;

    std::string layout;
    status = parse_scalar(node["layout"], path + ".layout", layout);
    if (!status.ok()) {
        return status;
    }
    if (layout == "NCHW") {
        contract.tensor_info.layout = core::TensorLayout::kNchw;
    } else if (layout == "BCN") {
        contract.tensor_info.layout = core::TensorLayout::kBcn;
    } else {
        return Status::failure(ErrorCode::kUnsupportedLayout,
                               path + ".layout: unsupported value '" +
                                   layout + "'");
    }

    status = parse_shape(
        node["shape"], path + ".shape", contract.tensor_info.shape);
    if (!status.ok()) {
        return status;
    }

    output = std::move(contract);
    return Status::success();
}

Status parse_model(const YAML::Node& node, ModelContract& output) {
    const Status mapping_status = validate_mapping(
        node, "model", {"id", "format", "sha256", "size_bytes"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    Status status =
        parse_nonempty_string(node["id"], "model.id", output.model_id);
    if (!status.ok()) {
        return status;
    }

    status = parse_scalar(node["format"], "model.format", output.format);
    if (!status.ok()) {
        return status;
    }
    if (output.format != "onnx") {
        return schema_error("model.format", "must be exactly 'onnx'");
    }

    status = parse_scalar(node["sha256"],
                          "model.sha256",
                          output.expected_onnx_sha256);
    if (!status.ok()) {
        return status;
    }
    const bool valid_sha256 = output.expected_onnx_sha256.size() == 64 &&
        std::all_of(output.expected_onnx_sha256.begin(),
                    output.expected_onnx_sha256.end(),
                    [](unsigned char character) {
                        return std::isdigit(character) != 0 ||
                            (character >= 'a' && character <= 'f');
                    });
    if (!valid_sha256) {
        return schema_error(
            "model.sha256",
            "must contain exactly 64 lowercase hexadecimal characters");
    }

    return parse_positive_integer(node["size_bytes"],
                                  "model.size_bytes",
                                  output.expected_onnx_size_bytes);
}

Status parse_classes(const YAML::Node& node, ModelContract& output) {
    const Status mapping_status =
        validate_mapping(node, "classes", {"count", "names"});
    if (!mapping_status.ok()) {
        return mapping_status;
    }

    std::uint64_t expected_count = 0;
    Status status = parse_positive_integer(
        node["count"], "classes.count", expected_count);
    if (!status.ok()) {
        return status;
    }

    const YAML::Node names = node["names"];
    if (!names.IsSequence()) {
        return schema_error("classes.names", "expected a sequence");
    }

    std::vector<std::string> class_names;
    class_names.reserve(names.size());
    std::unordered_set<std::string> seen_names;
    for (std::size_t index = 0; index < names.size(); ++index) {
        const std::string name_path =
            "classes.names[" + std::to_string(index) + "]";
        std::string class_name;
        status = parse_nonempty_string(names[index], name_path, class_name);
        if (!status.ok()) {
            return status;
        }
        if (!seen_names.insert(class_name).second) {
            return schema_error(name_path,
                                "duplicate class name '" + class_name +
                                    "'");
        }
        class_names.push_back(std::move(class_name));
    }

    if (expected_count != class_names.size()) {
        return schema_error(
            "classes.count",
            "does not match classes.names size " +
                std::to_string(class_names.size()));
    }

    output.class_names = std::move(class_names);
    return Status::success();
}

Status parse_contract(const YAML::Node& root, ModelContract& output) {
    const Status root_status = validate_mapping(
        root, "$", {"schema_version", "model", "input", "output", "classes"});
    if (!root_status.ok()) {
        return root_status;
    }

    ModelContract contract;
    std::int64_t schema_version = 0;
    Status status = parse_scalar(
        root["schema_version"], "schema_version", schema_version);
    if (!status.ok()) {
        return status;
    }
    if (schema_version != 1) {
        return schema_error("schema_version", "must be exactly 1");
    }
    contract.schema_version = 1;

    status = parse_model(root["model"], contract);
    if (!status.ok()) {
        return status;
    }
    status = parse_tensor_contract(root["input"], "input", contract.input);
    if (!status.ok()) {
        return status;
    }
    status =
        parse_tensor_contract(root["output"], "output", contract.output);
    if (!status.ok()) {
        return status;
    }
    status = parse_classes(root["classes"], contract);
    if (!status.ok()) {
        return status;
    }

    output = std::move(contract);
    return Status::success();
}

}  // namespace

core::Status ModelContractLoader::load(const std::filesystem::path& path,
                                       ModelContract* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "output: ModelContract pointer must not be null");
    }

    std::ifstream input(path);
    if (!input.is_open()) {
        return Status::failure(ErrorCode::kIoError,
                               path.string() + ": contract file is not readable");
    }

    try {
        const YAML::Node root = YAML::Load(input);
        if (input.bad()) {
            return Status::failure(
                ErrorCode::kIoError,
                path.string() + ": failed while reading contract file");
        }

        ModelContract parsed_contract;
        const Status status = parse_contract(root, parsed_contract);
        if (!status.ok()) {
            return status;
        }

        *output = std::move(parsed_contract);
        return Status::success();
    } catch (const YAML::Exception& exception) {
        return parse_error("$", "YAML error: " + std::string(exception.what()));
    }
}

}  // namespace edge_ai_defect::model
