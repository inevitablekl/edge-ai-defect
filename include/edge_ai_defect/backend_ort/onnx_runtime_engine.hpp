#pragma once

#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <memory>

namespace edge_ai_defect::backend_ort {

class OnnxRuntimeEngine final : public inference::IInferenceEngine {
public:
    OnnxRuntimeEngine();
    ~OnnxRuntimeEngine() override;

    OnnxRuntimeEngine(const OnnxRuntimeEngine&) = delete;
    OnnxRuntimeEngine& operator=(const OnnxRuntimeEngine&) = delete;
    OnnxRuntimeEngine(OnnxRuntimeEngine&&) = delete;
    OnnxRuntimeEngine& operator=(OnnxRuntimeEngine&&) = delete;

    [[nodiscard]] core::Status initialize(
        const model::ModelContract& contract,
        const std::filesystem::path& model_path) override;

    [[nodiscard]] core::Status initialize(
        const runtime::RuntimeConfig& config,
        const model::ModelContract& contract,
        const std::filesystem::path& model_path);

    [[nodiscard]] core::Status run(
        const core::HostTensor& input,
        core::HostTensor* output) override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace edge_ai_defect::backend_ort
