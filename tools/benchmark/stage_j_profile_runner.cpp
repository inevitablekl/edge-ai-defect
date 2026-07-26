#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <exception>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

namespace {

constexpr int kExitInternalError = 1;
constexpr int kExitCliOrConfigError = 2;
constexpr int kExitInitializationError = 3;
constexpr int kExitRuntimeError = 4;

struct Options {
    std::filesystem::path config;
    std::filesystem::path trace;
};

void usage(std::ostream& output) {
    output << "Usage: stage_j_profile_runner --config <runtime_v2.yaml> "
              "--trace-jsonl <trace.jsonl>\n";
}

bool parse_options(int argc, const char* const argv[], Options* options) {
    if (options == nullptr || argc != 5) {
        return false;
    }
    bool have_config = false;
    bool have_trace = false;
    for (int index = 1; index < argc; index += 2) {
        const std::string key(argv[index]);
        if (key == "--config" && !have_config) {
            options->config = argv[index + 1];
            have_config = !options->config.empty();
        } else if (key == "--trace-jsonl" && !have_trace) {
            options->trace = argv[index + 1];
            have_trace = !options->trace.empty();
        } else {
            return false;
        }
    }
    return have_config && have_trace;
}

}  // namespace

int main(int argc, const char* const argv[]) {
    try {
        Options options;
        if (!parse_options(argc, argv, &options)) {
            std::cerr << "error: invalid arguments\n";
            usage(std::cerr);
            return kExitCliOrConfigError;
        }

        edge_ai_defect::runtime::RuntimeConfig config;
        const edge_ai_defect::core::Status config_status =
            edge_ai_defect::runtime::RuntimeConfigLoader::load(
                options.config, &config);
        if (!config_status.ok()) {
            std::cerr << "error: " << config_status.message() << '\n';
            return kExitCliOrConfigError;
        }
        if (config.schema_version != 2U ||
            config.backend_type != "onnxruntime_cpu") {
            std::cerr << "error: Stage J profile runner requires schema_version 2 "
                         "and backend.type onnxruntime_cpu\n";
            return kExitCliOrConfigError;
        }

        std::error_code error;
        if (std::filesystem::exists(options.trace, error) || error) {
            std::cerr << "error: trace JSONL target already exists or cannot be inspected\n";
            return kExitCliOrConfigError;
        }
        std::ofstream trace_stream(options.trace, std::ios::out | std::ios::trunc);
        if (!trace_stream) {
            std::cerr << "error: cannot create trace JSONL target\n";
            return kExitInitializationError;
        }
        edge_ai_defect::runtime::TraceRecorder recorder(trace_stream);
        edge_ai_defect::application::RunOptions run_options;
        run_options.timing_enabled_override = true;
        run_options.trace_observer = &recorder;
        const edge_ai_defect::application::RunResult result =
            edge_ai_defect::application::run(config, run_options);
        if (!result.status.ok()) {
            std::cerr << "error: " << result.status.message() << '\n';
            return result.runtime_failure ? kExitRuntimeError
                                          : kExitInitializationError;
        }
        const edge_ai_defect::core::Status flush_status = recorder.flush();
        if (!flush_status.ok()) {
            std::cerr << "error: " << flush_status.message() << '\n';
            return kExitRuntimeError;
        }
        return 0;
    } catch (const std::exception&) {
        std::cerr << "internal error\n";
        return kExitInternalError;
    } catch (...) {
        std::cerr << "internal error\n";
        return kExitInternalError;
    }
}
