#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <memory>
#include <string>

namespace Ort {
struct SessionOptions;
}

namespace edge_ai_defect::backend_ort {

class OrtOptionsRecord final {
public:
    OrtOptionsRecord(const OrtOptionsRecord&) = delete;
    OrtOptionsRecord& operator=(const OrtOptionsRecord&) = delete;
    OrtOptionsRecord(OrtOptionsRecord&&) = delete;
    OrtOptionsRecord& operator=(OrtOptionsRecord&&) = delete;
    ~OrtOptionsRecord() = default;

    [[nodiscard]] static core::Status create(
        const runtime::RuntimeConfig& config,
        std::unique_ptr<const OrtOptionsRecord>* output);

    [[nodiscard]] std::uint32_t schema_version() const noexcept;
    [[nodiscard]] const std::string& backend_type() const noexcept;
    [[nodiscard]] const std::string& execution_mode() const noexcept;
    [[nodiscard]] const std::string& graph_optimization_level() const noexcept;
    [[nodiscard]] std::uint32_t intra_op_threads() const noexcept;
    [[nodiscard]] std::uint32_t inter_op_threads() const noexcept;
    [[nodiscard]] bool intra_op_allow_spinning() const noexcept;
    [[nodiscard]] bool inter_op_allow_spinning() const noexcept;
    [[nodiscard]] bool cpu_arena_enabled() const noexcept;
    [[nodiscard]] bool memory_pattern_enabled() const noexcept;
    [[nodiscard]] std::string canonical_json() const;

private:
    OrtOptionsRecord(const runtime::RuntimeConfig& config);

    const std::uint32_t schema_version_;
    const std::string backend_type_;
    const std::string execution_mode_;
    const std::string graph_optimization_level_;
    const std::uint32_t intra_op_threads_;
    const std::uint32_t inter_op_threads_;
    const bool intra_op_allow_spinning_;
    const bool inter_op_allow_spinning_;
    const bool cpu_arena_enabled_;
    const bool memory_pattern_enabled_;
};

[[nodiscard]] core::Status apply_ort_options(
    const runtime::RuntimeConfig& config,
    Ort::SessionOptions* session_options,
    std::unique_ptr<const OrtOptionsRecord>* applied_record);

}  // namespace edge_ai_defect::backend_ort
