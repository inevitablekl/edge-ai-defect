#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/model/model_contract.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace edge_ai_defect::model {

struct TensorRtEngineManifest {
    std::uint32_t schema_version = 0;
    std::string artifact_kind;
    std::string engine_id;
    std::filesystem::path engine_path;
    std::filesystem::path source_onnx_path;
    std::filesystem::path model_contract_path;
    std::string engine_sha256;
    std::string source_onnx_sha256;
    std::string model_contract_sha256;
    TensorContract input;
    TensorContract output;
};

class TensorRtEngineManifestLoader {
public:
    [[nodiscard]] static core::Status load(
        const std::filesystem::path& manifest_path,
        const ModelContract* expected_contract,
        TensorRtEngineManifest* output);
};

}  // namespace edge_ai_defect::model
