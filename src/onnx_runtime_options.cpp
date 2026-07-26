#include "edge_ai_defect/backend_ort/onnx_runtime_options.hpp"

#include <cpu_provider_factory.h>
#include <onnxruntime_cxx_api.h>
#include <onnxruntime_session_options_config_keys.h>

#include <climits>
#include <cstdint>
#include <memory>
#include <string>
#include <utility>

namespace edge_ai_defect::backend_ort {
namespace {

using core::ErrorCode;
using core::Status;

Status invalid(const std::string& detail) {
    return Status::failure(ErrorCode::kSchemaViolation,
                           "onnxruntime options: " + detail);
}

}  // namespace

OrtOptionsRecord::OrtOptionsRecord(const runtime::RuntimeConfig& config)
    : schema_version_(config.schema_version),
      backend_type_(config.backend_type),
      execution_mode_(config.onnxruntime.execution_mode),
      graph_optimization_level_(config.onnxruntime.graph_optimization_level),
      intra_op_threads_(config.onnxruntime.intra_op_threads),
      inter_op_threads_(config.onnxruntime.inter_op_threads),
      intra_op_allow_spinning_(config.onnxruntime.intra_op_allow_spinning),
      inter_op_allow_spinning_(config.onnxruntime.inter_op_allow_spinning),
      cpu_arena_enabled_(config.onnxruntime.cpu_arena_enabled),
      memory_pattern_enabled_(config.onnxruntime.memory_pattern_enabled) {}

core::Status OrtOptionsRecord::create(
    const runtime::RuntimeConfig& config,
    std::unique_ptr<const OrtOptionsRecord>* output) {
    if (output == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "output: ORT options record pointer must not be null");
    }
    if (config.schema_version != 2U) {
        return invalid("schema_version must be exactly 2");
    }
    if (config.backend_type != "onnxruntime_cpu") {
        return invalid("backend.type must be exactly 'onnxruntime_cpu'");
    }
    if (config.onnxruntime.execution_mode != "sequential") {
        return invalid("execution_mode must be exactly 'sequential'");
    }
    if (config.onnxruntime.graph_optimization_level != "all") {
        return invalid("graph_optimization_level must be exactly 'all'");
    }
    if (config.onnxruntime.intra_op_threads == 0U ||
        config.onnxruntime.inter_op_threads == 0U ||
        config.onnxruntime.intra_op_threads > static_cast<std::uint32_t>(INT_MAX) ||
        config.onnxruntime.inter_op_threads > static_cast<std::uint32_t>(INT_MAX)) {
        return invalid("thread counts must be positive and fit int");
    }

    *output = std::unique_ptr<const OrtOptionsRecord>(
        new OrtOptionsRecord(config));
    return Status::success();
}

std::uint32_t OrtOptionsRecord::schema_version() const noexcept {
    return schema_version_;
}

const std::string& OrtOptionsRecord::backend_type() const noexcept {
    return backend_type_;
}

const std::string& OrtOptionsRecord::execution_mode() const noexcept {
    return execution_mode_;
}

const std::string& OrtOptionsRecord::graph_optimization_level() const noexcept {
    return graph_optimization_level_;
}

std::uint32_t OrtOptionsRecord::intra_op_threads() const noexcept {
    return intra_op_threads_;
}

std::uint32_t OrtOptionsRecord::inter_op_threads() const noexcept {
    return inter_op_threads_;
}

bool OrtOptionsRecord::intra_op_allow_spinning() const noexcept {
    return intra_op_allow_spinning_;
}

bool OrtOptionsRecord::inter_op_allow_spinning() const noexcept {
    return inter_op_allow_spinning_;
}

bool OrtOptionsRecord::cpu_arena_enabled() const noexcept {
    return cpu_arena_enabled_;
}

bool OrtOptionsRecord::memory_pattern_enabled() const noexcept {
    return memory_pattern_enabled_;
}

std::string OrtOptionsRecord::canonical_json() const {
    return "{\"schema_version\":" + std::to_string(schema_version_) +
           ",\"backend_type\":\"" + backend_type_ +
           "\",\"execution_mode\":\"" + execution_mode_ +
           "\",\"graph_optimization_level\":\"" +
           graph_optimization_level_ +
           "\",\"intra_op_threads\":" + std::to_string(intra_op_threads_) +
           ",\"inter_op_threads\":" + std::to_string(inter_op_threads_) +
           ",\"intra_op_allow_spinning\":" +
           (intra_op_allow_spinning_ ? "true" : "false") +
           ",\"inter_op_allow_spinning\":" +
           (inter_op_allow_spinning_ ? "true" : "false") +
           ",\"cpu_arena_enabled\":" +
           (cpu_arena_enabled_ ? "true" : "false") +
           ",\"memory_pattern_enabled\":" +
           (memory_pattern_enabled_ ? "true" : "false") + "}";
}

core::Status apply_ort_options(
    const runtime::RuntimeConfig& config,
    Ort::SessionOptions* session_options,
    std::unique_ptr<const OrtOptionsRecord>* applied_record) {
    if (session_options == nullptr) {
        return Status::failure(ErrorCode::kInvalidArgument,
                               "session_options must not be null");
    }

    std::unique_ptr<const OrtOptionsRecord> record;
    const Status record_status = OrtOptionsRecord::create(config, &record);
    if (!record_status.ok()) {
        return record_status;
    }

    try {
        session_options->SetExecutionMode(ORT_SEQUENTIAL);
        session_options->SetGraphOptimizationLevel(ORT_ENABLE_ALL);
        session_options->SetIntraOpNumThreads(
            static_cast<int>(record->intra_op_threads()));
        session_options->SetInterOpNumThreads(
            static_cast<int>(record->inter_op_threads()));
        session_options->AddConfigEntry(
            kOrtSessionOptionsConfigAllowIntraOpSpinning,
            record->intra_op_allow_spinning() ? "1" : "0");
        session_options->AddConfigEntry(
            kOrtSessionOptionsConfigAllowInterOpSpinning,
            record->inter_op_allow_spinning() ? "1" : "0");
        if (record->cpu_arena_enabled()) {
            session_options->EnableCpuMemArena();
        } else {
            session_options->DisableCpuMemArena();
        }
        if (record->memory_pattern_enabled()) {
            session_options->EnableMemPattern();
        } else {
            session_options->DisableMemPattern();
        }
        session_options->AppendExecutionProvider_CPU(
            record->cpu_arena_enabled() ? 1 : 0);
    } catch (const Ort::Exception& exception) {
        return Status::failure(
            ErrorCode::kBackendInitializationError,
            "ORT options initialization failed: " + std::string(exception.what()));
    }

    if (applied_record != nullptr) {
        *applied_record = std::move(record);
    }
    return Status::success();
}

}  // namespace edge_ai_defect::backend_ort
