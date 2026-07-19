#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/model/model_contract.hpp"

#include <filesystem>

namespace edge_ai_defect::model {

class ModelContractLoader {
public:
    [[nodiscard]] static core::Status load(
        const std::filesystem::path& path,
        ModelContract* output);
};

}  // namespace edge_ai_defect::model
