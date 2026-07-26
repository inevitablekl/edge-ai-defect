#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/runtime/cli.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <exception>
#include <iostream>

namespace edge_ai_defect {
namespace {

constexpr int kExitSuccess = 0;
constexpr int kExitInternalError = 1;
constexpr int kExitCliOrConfigError = 2;
constexpr int kExitInitializationError = 3;
constexpr int kExitRuntimeError = 4;

void write_usage(std::ostream& output) {
    output << "Usage: edge_ai_defect --config <runtime.yaml>\n";
}

}  // namespace
}  // namespace edge_ai_defect

int main(int argc, const char* const argv[]) {
    using edge_ai_defect::core::Status;
    namespace runtime = edge_ai_defect::runtime;

    try {
        runtime::CliOptions options;
        Status status = runtime::parse_cli(argc, argv, &options);
        if (!status.ok()) {
            std::cerr << "error: " << status.message() << '\n';
            edge_ai_defect::write_usage(std::cerr);
            return edge_ai_defect::kExitCliOrConfigError;
        }
        if (options.action == runtime::CliAction::kHelp) {
            edge_ai_defect::write_usage(std::cout);
            return edge_ai_defect::kExitSuccess;
        }

        runtime::RuntimeConfig config;
        status = runtime::RuntimeConfigLoader::load(options.config_path, &config);
        if (!status.ok()) {
            std::cerr << "error: " << status.message() << '\n';
            return edge_ai_defect::kExitCliOrConfigError;
        }

        const edge_ai_defect::application::RunResult result =
            edge_ai_defect::application::run(config);
        if (!result.status.ok()) {
            std::cerr << "error: " << result.status.message() << '\n';
            return result.runtime_failure ? edge_ai_defect::kExitRuntimeError
                                          : edge_ai_defect::kExitInitializationError;
        }
        return edge_ai_defect::kExitSuccess;
    } catch (const std::exception&) {
        std::cerr << "internal error\n";
        return edge_ai_defect::kExitInternalError;
    } catch (...) {
        std::cerr << "internal error\n";
        return edge_ai_defect::kExitInternalError;
    }
}
