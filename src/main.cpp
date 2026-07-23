#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/cli.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/console_sink.hpp"
#include "edge_ai_defect/runtime/directory_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"
#include "edge_ai_defect/runtime/serial_runner.hpp"

#include <exception>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

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

runtime::RunMetadata make_metadata(const runtime::RuntimeConfig& config,
                                   const model::ModelContract& contract) {
    runtime::RunMetadata metadata;
    metadata.schema_version = config.schema_version;
    metadata.backend_type = config.backend_type;
    metadata.model_filename = config.model_path.filename().string();
    metadata.model_sha256 = contract.expected_onnx_sha256;
    metadata.contract_filename = config.model_contract_path.filename().string();
    metadata.class_names = contract.class_names;
    metadata.postprocess_config = config.postprocess_config;
    metadata.timing_enabled = config.timing_enabled;
    return metadata;
}

struct ApplicationResult {
    core::Status status;
    bool runtime_failure = false;
};

ApplicationResult run_application(const runtime::RuntimeConfig& config) {
    model::ModelContract contract;
    core::Status status = model::ModelContractLoader::load(
        config.model_contract_path, &contract);
    if (!status.ok()) {
        return {status, false};
    }

    std::unique_ptr<runtime::DirectorySource> source;
    status = runtime::DirectorySource::create(config.input_directory, &source);
    if (!status.ok()) {
        return {status, false};
    }

    preprocess::Preprocessor preprocessor;
    backend_ort::OnnxRuntimeEngine engine;
    if (config.schema_version == 2U) {
        status = engine.initialize(config, contract, config.model_path);
    } else {
        status = engine.initialize(contract, config.model_path);
    }
    if (!status.ok()) {
        return {status, false};
    }

    postprocess::PostProcessor postprocessor(config.postprocess_config);

    std::unique_ptr<runtime::JsonSink> json_sink;
    status = runtime::JsonSink::create(config.output_json_path,
                                       config.output_overwrite,
                                       &json_sink);
    if (!status.ok()) {
        return {status, false};
    }

    std::vector<std::unique_ptr<runtime::IResultSink>> sinks;
    sinks.push_back(std::move(json_sink));
    if (config.output_console) {
        sinks.push_back(std::make_unique<runtime::ConsoleSink>(std::cout));
    }

    std::unique_ptr<runtime::CompositeSink> sink;
    status = runtime::CompositeSink::create(std::move(sinks), &sink);
    if (!status.ok()) {
        return {status, false};
    }

    const runtime::RunMetadata metadata = make_metadata(config, contract);
    runtime::SerialRunner runner(*source,
                                 preprocessor,
                                 contract.input.tensor_info,
                                 engine,
                                 postprocessor,
                                 *sink);
    runtime::RunSummary summary;
    return {runner.run(metadata, &summary), true};
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

        const edge_ai_defect::ApplicationResult result =
            edge_ai_defect::run_application(config);
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
