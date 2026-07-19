#pragma once

#include "edge_ai_defect/core/status.hpp"

#include <filesystem>

namespace edge_ai_defect::runtime {

enum class CliAction {
    kRun,
    kHelp,
};

struct CliOptions {
    CliAction action = CliAction::kRun;
    std::filesystem::path config_path;
};

[[nodiscard]] core::Status parse_cli(
    int argc,
    const char* const argv[],
    CliOptions* output);

}  // namespace edge_ai_defect::runtime
