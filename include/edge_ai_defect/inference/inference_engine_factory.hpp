#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/inference/inference_engine.hpp"
#include "edge_ai_defect/model/model_contract.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <memory>

namespace edge_ai_defect::inference {

[[nodiscard]] core::Status create_inference_engine(
    const runtime::RuntimeConfig& config,
    const model::ModelContract& contract,
    std::unique_ptr<IInferenceEngine>* output);

}  // namespace edge_ai_defect::inference
