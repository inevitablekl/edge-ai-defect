#pragma once

#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <memory>

namespace edge_ai_defect::backend_tensorrt {

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

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace edge_ai_defect::backend_tensorrt
