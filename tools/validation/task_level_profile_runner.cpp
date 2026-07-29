#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <exception>
#include <iostream>
#include <string>

namespace {

void usage(std::ostream& output) {
    output << "Usage: task_level_profile_runner --config <runtime_v3.yaml>\n";
}

}  // namespace

int main(int argc, const char* const argv[]) {
    if (argc != 3 || std::string(argv[1]) != "--config") {
        usage(std::cerr);
        return 2;
    }

    try {
        edge_ai_defect::runtime::RuntimeConfig config;
        const edge_ai_defect::core::Status config_status =
            edge_ai_defect::runtime::RuntimeConfigLoader::load(argv[2], &config);
        if (!config_status.ok()) {
            std::cerr << "error: " << config_status.message() << '\n';
            return 2;
        }

        edge_ai_defect::application::RunOptions options;
        options.timing_enabled_override = true;
        const edge_ai_defect::application::RunResult result =
            edge_ai_defect::application::run(config, options);
        if (!result.status.ok()) {
            std::cerr << "error: " << result.status.message() << '\n';
            return result.runtime_failure ? 4 : 3;
        }
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "internal error: " << exception.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "internal error\n";
        return 1;
    }
}
