#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/model/model_contract.hpp"

#include <filesystem>

namespace edge_ai_defect::inference {

class IInferenceEngine {
public:
    virtual ~IInferenceEngine() = default;

    IInferenceEngine(const IInferenceEngine&) = delete;
    IInferenceEngine& operator=(const IInferenceEngine&) = delete;
    IInferenceEngine(IInferenceEngine&&) = delete;
    IInferenceEngine& operator=(IInferenceEngine&&) = delete;

    [[nodiscard]] virtual core::Status initialize(
        const model::ModelContract& contract,
        const std::filesystem::path& model_path) = 0;

    [[nodiscard]] virtual core::Status run(
        const core::HostTensor& input,
        core::HostTensor* output) = 0;

protected:
    IInferenceEngine() = default;
};

}  // namespace edge_ai_defect::inference
