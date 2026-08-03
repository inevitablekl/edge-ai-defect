#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
using edge_ai_defect::core::ErrorCode;
using edge_ai_defect::core::Status;
using edge_ai_defect::runtime::DataPathVariant;
using edge_ai_defect::runtime::RuntimeConfig;
using edge_ai_defect::runtime::RuntimeConfigLoader;

struct Arguments {
    fs::path v0;
    fs::path v2r;
    fs::path v3r;
    fs::path output;
};

void usage() {
    std::cout << "Usage: stage_r_phase0_5d_config_validator --v0 PATH --v2r PATH"
                 " --v3r PATH --output PATH\n";
}

Status parse_args(int argc, char** argv, Arguments* output) {
    Arguments args;
    for (int index = 1; index < argc; ++index) {
        const std::string option = argv[index];
        if (option == "--help" || option == "-h") {
            usage();
            return Status::failure(ErrorCode::kInvalidArgument, "help");
        }
        if (index + 1 >= argc) {
            return Status::failure(ErrorCode::kInvalidArgument, "missing value for " + option);
        }
        const fs::path value = argv[++index];
        if (option == "--v0") args.v0 = value;
        else if (option == "--v2r") args.v2r = value;
        else if (option == "--v3r") args.v3r = value;
        else if (option == "--output") args.output = value;
        else return Status::failure(ErrorCode::kInvalidArgument, "unknown option " + option);
    }
    if (args.v0.empty() || args.v2r.empty() || args.v3r.empty() || args.output.empty()) {
        return Status::failure(ErrorCode::kInvalidArgument, "all config and output paths are required");
    }
    *output = std::move(args);
    return Status::success();
}

std::string json_escape(const std::string& value) {
    std::string result;
    for (const char character : value) {
        if (character == '\\' || character == '"') result.push_back('\\');
        result.push_back(character);
    }
    return result;
}

Status load(const fs::path& path, RuntimeConfig* output) {
    Status status = RuntimeConfigLoader::load(path, output);
    if (!status.ok()) {
        return Status::failure(status.code(), path.string() + ": " + status.message());
    }
    if (output->schema_version != 6U || output->backend_type != "tensorrt_int8" ||
        output->timing_enabled || output->profiling_mode != edge_ai_defect::runtime::ProfilingMode::kOff ||
        output->runtime_mode != "serial" || output->pipeline.queue_capacity != 0U ||
        output->phase0_5d.execution_mode != "FORMAL_AUTHORITY" ||
        output->phase0_5d.warmup_frames != 60U || output->phase0_5d.measured_frames != 1080U ||
        output->phase0_5d.input_size != 640U || output->phase0_5d.batch != 1U ||
        output->phase0_5d.repetitions != 5U || output->phase0_5d.opencv_threads != 1U) {
        return Status::failure(ErrorCode::kSchemaViolation,
                               path.string() + ": timing-aligned common contract mismatch");
    }
    return Status::success();
}

bool common_equal(const RuntimeConfig& left, const RuntimeConfig& right) {
    return left.schema_version == right.schema_version &&
           left.backend_type == right.backend_type &&
           left.tensorrt.engine_path == right.tensorrt.engine_path &&
           left.tensorrt.engine_manifest_path == right.tensorrt.engine_manifest_path &&
           left.tensorrt.device_id == right.tensorrt.device_id &&
           left.model_contract_path == right.model_contract_path &&
           left.input_type == right.input_type && left.input_directory == right.input_directory &&
           left.runtime_mode == right.runtime_mode &&
           left.opencv_num_threads == right.opencv_num_threads &&
           left.output_json_path == right.output_json_path &&
           left.output_console == right.output_console &&
           left.output_overwrite == right.output_overwrite &&
           left.postprocess_config.confidence_threshold == right.postprocess_config.confidence_threshold &&
           left.postprocess_config.iou_threshold == right.postprocess_config.iou_threshold &&
           left.postprocess_config.max_nms == right.postprocess_config.max_nms &&
           left.postprocess_config.max_det == right.postprocess_config.max_det &&
           left.postprocess_config.max_wh == right.postprocess_config.max_wh &&
           left.postprocess_config.agnostic == right.postprocess_config.agnostic &&
           left.postprocess_config.multi_label == right.postprocess_config.multi_label &&
           left.timing_enabled == right.timing_enabled &&
           left.profiling_mode == right.profiling_mode &&
           left.phase0_5d.execution_mode == right.phase0_5d.execution_mode &&
           left.phase0_5d.warmup_frames == right.phase0_5d.warmup_frames &&
           left.phase0_5d.measured_frames == right.phase0_5d.measured_frames &&
           left.phase0_5d.input_size == right.phase0_5d.input_size &&
           left.phase0_5d.batch == right.phase0_5d.batch &&
           left.phase0_5d.repetitions == right.phase0_5d.repetitions &&
           left.phase0_5d.schedule_id == right.phase0_5d.schedule_id &&
           left.phase0_5d.result_root == right.phase0_5d.result_root &&
           left.phase0_5d.cpu_affinity == right.phase0_5d.cpu_affinity &&
           left.phase0_5d.opencv_threads == right.phase0_5d.opencv_threads &&
           left.phase0_5d.timing_boundary_id == right.phase0_5d.timing_boundary_id &&
           left.phase0_5d.sink_id == right.phase0_5d.sink_id &&
           left.phase0_5d.serialization_id == right.phase0_5d.serialization_id &&
           left.phase0_5d.digest_id == right.phase0_5d.digest_id;
}

const char* variant_name(DataPathVariant value) {
    return edge_ai_defect::runtime::data_path_variant_name(value);
}

Status write_text(const fs::path& path, const std::string& value) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) return Status::failure(ErrorCode::kIoError, "cannot write " + path.string());
    output << value;
    return output ? Status::success() : Status::failure(ErrorCode::kIoError, "write failed");
}
}  // namespace

int main(int argc, char** argv) {
    Arguments args;
    Status status = parse_args(argc, argv, &args);
    if (!status.ok()) {
        if (status.message() == "help") return 0;
        std::cerr << status.message() << '\n';
        usage();
        return 2;
    }
    RuntimeConfig v0, v2r, v3r;
    for (const auto& item : {std::pair<const fs::path*, RuntimeConfig*>(&args.v0, &v0),
                             std::pair<const fs::path*, RuntimeConfig*>(&args.v2r, &v2r),
                             std::pair<const fs::path*, RuntimeConfig*>(&args.v3r, &v3r)}) {
        status = load(*item.first, item.second);
        if (!status.ok()) { std::cerr << status.message() << '\n'; return 3; }
    }
    if (v0.data_path_variant != DataPathVariant::kV0 ||
        v2r.data_path_variant != DataPathVariant::kV2R ||
        v3r.data_path_variant != DataPathVariant::kV3R) {
        std::cerr << "config variants must be exactly V0, V2R, V3R\n";
        return 3;
    }
    if (!common_equal(v0, v2r) || !common_equal(v0, v3r)) {
        std::cerr << "common config identity mismatch\n";
        return 3;
    }
    const std::vector<std::string> schedule = {
        "V0,V2R,V3R", "V3R,V2R,V0", "V2R,V0,V3R", "V0,V3R,V2R", "V2R,V3R,V0"};
    std::ostringstream output;
    output << "{\n  \"schema_version\": 1,\n  \"status\": \"PASS\",\n"
           << "  \"common_identity_equal\": true,\n  \"variant_only_difference\": \"data_path.variant\",\n"
           << "  \"variants\": {\n"
           << "    \"V0\": {\"parsed_variant\": \"" << variant_name(v0.data_path_variant)
           << "\", \"implementation_path\": \"CPU/OpenCV HostTensor\"},\n"
           << "    \"V2R\": {\"parsed_variant\": \"" << variant_name(v2r.data_path_variant)
           << "\", \"implementation_path\": \"pageable staging + accepted aligned CUDA resize\"},\n"
           << "    \"V3R\": {\"parsed_variant\": \"" << variant_name(v3r.data_path_variant)
           << "\", \"implementation_path\": \"pinned staging + accepted aligned CUDA resize\"}\n  },\n"
           << "  \"schedule\": [\n";
    for (std::size_t index = 0; index < schedule.size(); ++index) {
        output << "    \"" << schedule[index] << "\"" << (index + 1U == schedule.size() ? "\n" : ",\n");
    }
    output << "  ],\n  \"schedule_positions\": 15,\n"
           << "  \"timing_enabled\": false,\n  \"profiling_mode\": \"off\",\n"
           << "  \"output_root\": \"" << json_escape(v0.phase0_5d.result_root) << "\"\n}\n";
    status = write_text(args.output, output.str());
    if (!status.ok()) { std::cerr << status.message() << '\n'; return 4; }
    std::cout << "CONFIG VALIDATION PASS common_identity_equal=true schedule_positions=15\n";
    return 0;
}
