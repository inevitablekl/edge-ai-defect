#include "edge_ai_defect/application/application_runner.hpp"

#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/console_sink.hpp"
#include "edge_ai_defect/runtime/directory_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/opencv_thread_policy.hpp"
#include "edge_ai_defect/runtime/serial_runner.hpp"

#include <iostream>
#include <memory>
#include <utility>
#include <vector>

namespace edge_ai_defect::application {
namespace {

runtime::RunMetadata make_metadata(const runtime::RuntimeConfig& config,
                                   const model::ModelContract& contract,
                                   const RunOptions& options) {
    runtime::RunMetadata metadata;
    metadata.schema_version = 1U;
    metadata.backend_type = config.backend_type;
    metadata.model_filename = config.model_path.filename().string();
    metadata.model_sha256 = contract.expected_onnx_sha256;
    metadata.contract_filename = config.model_contract_path.filename().string();
    metadata.class_names = contract.class_names;
    metadata.postprocess_config = config.postprocess_config;
    metadata.timing_enabled =
        options.timing_enabled_override.value_or(config.timing_enabled);
    return metadata;
}

}  // namespace

RunResult run(const runtime::RuntimeConfig& config, const RunOptions& options) {
    std::unique_ptr<const runtime::OpenCvThreadPolicyRecord> opencv_policy_record;
    if (config.schema_version == 2U) {
        const core::Status policy_status =
            runtime::OpenCvThreadPolicyRecord::apply(config, &opencv_policy_record);
        if (!policy_status.ok()) {
            return {policy_status, false};
        }
    }

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
    std::unique_ptr<inference::IInferenceEngine> engine;
    status = inference::create_inference_engine(config, contract, &engine);
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

    const runtime::RunMetadata metadata = make_metadata(config, contract, options);
    runtime::SerialRunner runner(*source,
                                 preprocessor,
                                 contract.input.tensor_info,
                                 *engine,
                                 postprocessor,
                                 *sink,
                                 options.trace_observer);
    runtime::RunSummary summary;
    return {runner.run(metadata, &summary), true};
}

}  // namespace edge_ai_defect::application
