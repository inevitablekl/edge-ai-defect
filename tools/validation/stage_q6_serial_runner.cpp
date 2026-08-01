#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/inference/inference_engine_factory.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/model/tensorrt_engine_manifest.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/frame_trace.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/runtime_config.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
using edge_ai_defect::core::Status;

struct Args {
    fs::path config, manifest, output, trace, hashes, sidecar;
    std::string run_id;
    std::size_t max_frames = 5100;
    std::size_t cycles = 29;
};

fs::path value(int& index, int argc, char** argv, const char* option) {
    if (++index >= argc) throw std::runtime_error(std::string("missing value for ") + option);
    return argv[index];
}

std::size_t size_value(int& index, int argc, char** argv, const char* option) {
    const auto raw = value(index, argc, argv, option).string();
    try { return std::stoull(raw); } catch (...) { throw std::runtime_error(std::string("invalid ") + option); }
}

Args parse(int argc, char** argv) {
    Args args;
    for (int i = 1; i < argc; ++i) {
        const std::string option = argv[i];
        if (option == "--config") args.config = value(i, argc, argv, "--config");
        else if (option == "--manifest") args.manifest = value(i, argc, argv, "--manifest");
        else if (option == "--output") args.output = value(i, argc, argv, "--output");
        else if (option == "--trace") args.trace = value(i, argc, argv, "--trace");
        else if (option == "--hashes") args.hashes = value(i, argc, argv, "--hashes");
        else if (option == "--sidecar") args.sidecar = value(i, argc, argv, "--sidecar");
        else if (option == "--run-id") args.run_id = value(i, argc, argv, "--run-id").string();
        else if (option == "--max-frames") args.max_frames = size_value(i, argc, argv, "--max-frames");
        else if (option == "--cycles") args.cycles = size_value(i, argc, argv, "--cycles");
        else if (option == "--help") {
            std::cout << "stage_q6_serial_runner --config PATH --manifest PATH --output PATH"
                         " --trace PATH --hashes PATH --sidecar PATH --run-id ID\n";
            std::exit(0);
        } else throw std::runtime_error("unknown option: " + option);
    }
    if (args.config.empty() || args.manifest.empty() || args.output.empty() ||
        args.trace.empty() || args.hashes.empty() || args.sidecar.empty() || args.run_id.empty())
        throw std::runtime_error("all Q6 arguments are required");
    if (args.max_frames != 5100 || args.cycles != 29)
        throw std::runtime_error("Q6 requires max_frames=5100 and cycles=29");
    return args;
}

void write_hashes(const fs::path& path, const Args& args,
                  const edge_ai_defect::runtime::CanonicalHashSink& sink) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write hashes: " + path.string());
    out << "{\n  \"run_id\": \"" << args.run_id << "\",\n"
        << "  \"accepted_frames\": " << sink.frames().size() << ",\n"
        << "  \"run_sha256\": \"" << sink.run_hash() << "\",\n  \"cycle_sha256\": [\n";
    bool first = true;
    for (const auto& [cycle, digest] : sink.cycle_hashes()) {
        if (!first) out << ",\n";
        first = false;
        out << "    {\"cycle_id\": " << cycle << ", \"frame_count\": "
            << ((cycle + 1) * 180 <= sink.frames().size() ? 180 : sink.frames().size() - cycle * 180)
            << ", \"sha256\": \"" << digest << "\"}";
    }
    out << "\n  ]\n}\n";
}

void write_sidecar(const fs::path& path, const Args& args,
                   const edge_ai_defect::runtime::RuntimeConfig& config,
                   const edge_ai_defect::runtime::CanonicalHashSink& sink) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write sidecar: " + path.string());
    out << "{\n  \"run_id\": \"" << args.run_id << "\",\n"
        << "  \"backend\": \"" << config.backend_type << "\",\n"
        << "  \"runtime_mode\": \"" << config.runtime_mode << "\",\n"
        << "  \"input_type\": \"" << config.input_type << "\",\n"
        << "  \"cycle_length\": 180,\n  \"drop\": 0,\n"
        << "  \"ordering\": \"manifest order\",\n"
        << "  \"warmup_frames\": 100,\n  \"measured_frames\": 5000,\n"
        << "  \"accepted_frames\": " << sink.frames().size() << ",\n"
        << "  \"engine_path\": \"" << config.tensorrt.engine_path.string() << "\",\n"
        << "  \"engine_manifest_path\": \"" << config.tensorrt.engine_manifest_path.string() << "\"\n}\n";
}
}  // namespace

int main(int argc, char** argv) {
    try {
        const Args args = parse(argc, argv);
        edge_ai_defect::runtime::RuntimeConfig config;
        Status status = edge_ai_defect::runtime::RuntimeConfigLoader::load(args.config, &config);
        if (!status.ok()) throw std::runtime_error(status.message());
        if (config.schema_version != 5 || config.runtime_mode != "serial" ||
            config.input_type != "directory" ||
            (config.backend_type != "tensorrt_fp16" && config.backend_type != "tensorrt_int8") ||
            !config.timing_enabled)
            throw std::runtime_error("Q6 requires RuntimeConfig v5, Serial, directory, timing enabled, TRT FP16/INT8");

        auto source = std::unique_ptr<edge_ai_defect::runtime::CorpusReplaySource>{};
        status = edge_ai_defect::runtime::CorpusReplaySource::create(
            config.input_directory, args.manifest, args.cycles, &source, args.max_frames);
        if (!status.ok()) throw std::runtime_error(status.message());
        edge_ai_defect::model::ModelContract contract;
        status = edge_ai_defect::model::ModelContractLoader::load(config.model_contract_path, &contract);
        if (!status.ok()) throw std::runtime_error(status.message());
        auto manifest = std::make_unique<edge_ai_defect::model::TensorRtEngineManifest>();
        status = edge_ai_defect::model::TensorRtEngineManifestLoader::load(
            config.tensorrt.engine_manifest_path, &contract, manifest.get());
        if (!status.ok()) throw std::runtime_error(status.message());
        std::unique_ptr<edge_ai_defect::inference::IInferenceEngine> engine;
        status = edge_ai_defect::inference::create_inference_engine(config, contract, &engine);
        if (!status.ok()) throw std::runtime_error(status.message());
        fs::create_directories(args.output.parent_path());
        fs::create_directories(args.trace.parent_path());
        fs::create_directories(args.hashes.parent_path());
        fs::create_directories(args.sidecar.parent_path());
        std::unique_ptr<edge_ai_defect::runtime::JsonSink> json;
        status = edge_ai_defect::runtime::JsonSink::create(args.output, true, &json);
        if (!status.ok()) throw std::runtime_error(status.message());
        auto canonical = std::make_unique<edge_ai_defect::runtime::CanonicalHashSink>(
            edge_ai_defect::runtime::CanonicalHashScope::RUN_AND_CYCLE, 180);
        auto* canonical_ptr = canonical.get();
        auto trace = std::make_unique<edge_ai_defect::runtime::ConcurrentFrameTraceRecorder>();
        auto* trace_ptr = trace.get();
        std::vector<std::unique_ptr<edge_ai_defect::runtime::IResultSink>> children;
        children.push_back(std::move(json));
        children.push_back(std::move(canonical));
        std::unique_ptr<edge_ai_defect::runtime::CompositeSink> sink;
        status = edge_ai_defect::runtime::CompositeSink::create(std::move(children), &sink);
        if (!status.ok()) throw std::runtime_error(status.message());
        edge_ai_defect::runtime::RunMetadata metadata;
        metadata.schema_version = config.backend_type == "tensorrt_int8" ? 4U : 3U;
        metadata.backend_type = config.backend_type;
        metadata.model_filename = config.tensorrt.engine_path.filename().string();
        metadata.model_sha256 = manifest->engine_sha256;
        metadata.contract_filename = config.model_contract_path.filename().string();
        metadata.artifact_kind = "tensorrt_engine";
        metadata.source_onnx_sha256 = manifest->source_onnx_sha256;
        metadata.engine_manifest_filename = config.tensorrt.engine_manifest_path.filename().string();
        if (config.backend_type == "tensorrt_int8") {
            metadata.precision_v4 = edge_ai_defect::runtime::PrecisionMetadataV4{
                manifest->precision_mode, manifest->int8_enabled, manifest->fp16_fallback_enabled,
                manifest->host_io_dtype, edge_ai_defect::runtime::CalibrationMetadataV4{
                    "IInt8EntropyCalibrator2", "train", 1260U,
                    manifest->calibration_manifest_sha256, manifest->calibration_cache_sha256,
                    manifest->cache_metadata_sha256}};
        }
        metadata.class_names = contract.class_names;
        metadata.postprocess_config = config.postprocess_config;
        metadata.timing_enabled = true;
        metadata.runtime_v3 = edge_ai_defect::runtime::RuntimeMetadataV3{
            "serial", "directory", std::nullopt};
        edge_ai_defect::preprocess::Preprocessor preprocessor;
        edge_ai_defect::postprocess::PostProcessor postprocessor(config.postprocess_config);
        edge_ai_defect::runtime::RunSummary summary;
        const auto result = edge_ai_defect::application::run_with_components(
            config, *source, *sink, metadata, preprocessor, contract.input.tensor_info,
            *engine, postprocessor, &summary, edge_ai_defect::application::RunOptions{true, trace_ptr});
        std::ofstream trace_out(args.trace);
        if (!trace_out) throw std::runtime_error("cannot write trace");
        status = trace_ptr->flush(trace_out);
        if (!result.status.ok()) throw std::runtime_error(result.status.message());
        if (!status.ok()) throw std::runtime_error(status.message());
        if (canonical_ptr->frames().size() != 5100 || canonical_ptr->cycle_hashes().size() != 29)
            throw std::runtime_error("Q6 did not produce exactly 5100 frames and 29 cycle digests");
        write_hashes(args.hashes, args, *canonical_ptr);
        write_sidecar(args.sidecar, args, config, *canonical_ptr);
        std::cout << "Q6_" << config.backend_type << "_SERIAL_RUN_PASS\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Q6_SERIAL_RUN_FAILED: " << error.what() << '\n';
        return 1;
    }
}
