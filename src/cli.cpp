#include "edge_ai_defect/runtime/cli.hpp"

#include <string>
#include <utility>

namespace edge_ai_defect::runtime {

core::Status parse_cli(int argc,
                       const char* const argv[],
                       CliOptions* output) {
    if (output == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "output: CliOptions pointer must not be null");
    }
    if (argc < 1 || argv == nullptr) {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "argc and argv must describe a process invocation");
    }

    if (argc == 2 && argv[1] != nullptr && std::string(argv[1]) == "--help") {
        *output = CliOptions{CliAction::kHelp, {}};
        return core::Status::success();
    }

    if (argc != 3 || argv[1] == nullptr || argv[2] == nullptr) {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "Usage requires exactly '--config <runtime.yaml>' or standalone '--help'");
    }

    if (std::string(argv[1]) != "--config") {
        return core::Status::failure(
            core::ErrorCode::kInvalidArgument,
            "Only '--config <runtime.yaml>' is supported");
    }
    if (std::string(argv[2]).empty() || std::string(argv[2]) == "--help") {
        return core::Status::failure(core::ErrorCode::kInvalidArgument,
                                     "--config requires a non-empty path value");
    }

    *output = CliOptions{CliAction::kRun, std::filesystem::path(argv[2])};
    return core::Status::success();
}

}  // namespace edge_ai_defect::runtime
