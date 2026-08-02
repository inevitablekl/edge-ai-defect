#pragma once

#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <memory>
#include <vector>

namespace edge_ai_defect::backend_tensorrt {

struct TensorRtDiagnosticSample {
    std::size_t measured_frame = 0;
    std::size_t cycle_index = 0;
    std::size_t frame_in_cycle = 0;
    double h2d_ms = 0.0;
    double tensorrt_ms = 0.0;
    double d2h_ms = 0.0;
    double host_output_construction_ms = 0.0;
    double host_roundtrip_ms = 0.0;
};

class TensorRtEngine final : public inference::IInferenceEngine {
public:
    TensorRtEngine();
    ~TensorRtEngine() override;

    TensorRtEngine(const TensorRtEngine&) = delete;
    TensorRtEngine& operator=(const TensorRtEngine&) = delete;
    TensorRtEngine(TensorRtEngine&&) = delete;
    TensorRtEngine& operator=(TensorRtEngine&&) = delete;

    [[nodiscard]] core::Status initialize(
        const model::ModelContract& contract,
        const std::filesystem::path& model_path) override;

    [[nodiscard]] core::Status initialize(
        const runtime::RuntimeConfig& config,
        const model::ModelContract& contract);

    [[nodiscard]] core::Status run(
        const core::HostTensor& input,
        core::HostTensor* output) override;

    // Backend-only Stage R capability. The pointer must be this engine's
    // persistent device input allocation; callers cannot replace ownership.
    [[nodiscard]] void* device_input_buffer() const noexcept;
    [[nodiscard]] std::size_t device_input_bytes() const noexcept;
    [[nodiscard]] void* cuda_stream_handle() const noexcept;
    [[nodiscard]] core::Status run_device_input(
        const void* device_input,
        std::size_t input_bytes,
        core::HostTensor* output);

    // Stage R V4-only backend capability. The caller owns the fixed device
    // slot; execution still uses this engine's single context and stream.
    [[nodiscard]] core::Status run_device_input_slot(
        const void* device_input,
        std::size_t input_bytes,
        core::HostTensor* output);

    [[nodiscard]] core::Status set_diagnostic_profiling(bool enabled);
    [[nodiscard]] core::Status reset_diagnostic_profiling();
    [[nodiscard]] const std::vector<TensorRtDiagnosticSample>& diagnostic_samples() const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace edge_ai_defect::backend_tensorrt
