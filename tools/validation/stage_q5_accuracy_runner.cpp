#include "edge_ai_defect/application/application_runner.hpp"
#include "edge_ai_defect/runtime/canonical_hash_sink.hpp"
#include "edge_ai_defect/runtime/composite_sink.hpp"
#include "edge_ai_defect/runtime/corpus_replay_source.hpp"
#include "edge_ai_defect/runtime/json_sink.hpp"
#include "edge_ai_defect/runtime/timed_json_sink.hpp"

#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

namespace {
using namespace edge_ai_defect;

struct Options {
    std::string backend;
    std::filesystem::path dataset_root;
    std::filesystem::path manifest;
    std::filesystem::path engine;
    std::filesystem::path engine_manifest;
    std::filesystem::path output;
    std::filesystem::path hash_output;
};

Options parse(int argc, char** argv) {
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string arg(argv[index]);
        const auto value = [&](const std::string& name) {
            if (arg.rfind(name + "=", 0) != 0) throw std::runtime_error("expected " + name + "=<value>");
            return std::filesystem::path(arg.substr(name.size() + 1));
        };
        if (arg.rfind("--backend=", 0) == 0) options.backend = arg.substr(10);
        else if (arg.rfind("--dataset-root=", 0) == 0) options.dataset_root = value("--dataset-root");
        else if (arg.rfind("--manifest=", 0) == 0) options.manifest = value("--manifest");
        else if (arg.rfind("--engine=", 0) == 0) options.engine = value("--engine");
        else if (arg.rfind("--engine-manifest=", 0) == 0) options.engine_manifest = value("--engine-manifest");
        else if (arg.rfind("--output=", 0) == 0) options.output = value("--output");
        else if (arg.rfind("--hash-output=", 0) == 0) options.hash_output = value("--hash-output");
        else throw std::runtime_error("unknown argument: " + arg);
    }
    if ((options.backend != "fp16" && options.backend != "int8") ||
        options.dataset_root.empty() || options.manifest.empty() || options.engine.empty() ||
        options.engine_manifest.empty() || options.output.empty() || options.hash_output.empty())
        throw std::runtime_error("all Q5 runner arguments are required");
    return options;
}

void write_hash(const std::filesystem::path& path, const std::string& backend,
                const std::string& cycle_hash, const std::string& run_hash,
                std::size_t frame_count) {
    std::ofstream output(path);
    if (!output) throw std::runtime_error("cannot write hash authority: " + path.string());
    output << "{\n  \"backend\": \"" << backend << "\",\n"
           << "  \"cycles\": 1,\n  \"accepted_frames\": " << frame_count << ",\n"
           << "  \"expected_cycle_sha\": \"" << cycle_hash << "\",\n"
           << "  \"run_sha\": \"" << run_hash << "\"\n}\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse(argc, argv);
        auto source = std::unique_ptr<runtime::CorpusReplaySource>{};
        auto status = runtime::CorpusReplaySource::create(
            options.dataset_root, options.manifest, 1U, &source, 180U);
        if (!status.ok()) throw std::runtime_error(status.message());

        runtime::RuntimeConfig config;
        config.schema_version = options.backend == "int8" ? 5U : 4U;
        config.backend_type = options.backend == "int8" ? "tensorrt_int8" : "tensorrt_fp16";
        config.model_contract_path = "configs/model_contracts/yolov8n_neudet_frozen.yaml";
        config.tensorrt.engine_path = options.engine;
        config.tensorrt.engine_manifest_path = options.engine_manifest;
        config.tensorrt.device_id = 0;
        config.runtime_mode = "serial";
        config.input_type = "directory";
        config.postprocess_config.confidence_threshold = 0.25F;
        config.postprocess_config.iou_threshold = 0.45F;
        config.postprocess_config.max_nms = 30000U;
        config.postprocess_config.max_det = 300U;
        config.postprocess_config.max_wh = 7680.0F;
        config.postprocess_config.agnostic = false;
        config.postprocess_config.multi_label = false;

        std::filesystem::create_directories(options.output.parent_path());
        std::filesystem::create_directories(options.hash_output.parent_path());
        std::unique_ptr<runtime::JsonSink> json;
        status = runtime::JsonSink::create(options.output, true, &json);
        if (!status.ok()) throw std::runtime_error(status.message());
        auto timed = std::make_unique<runtime::TimedJsonSink>(*json);
        auto canonical = std::make_unique<runtime::CanonicalHashSink>(
            runtime::CanonicalHashScope::RUN_AND_CYCLE, 180U);
        auto* canonical_ptr = canonical.get();
        std::vector<std::unique_ptr<runtime::IResultSink>> children;
        children.push_back(std::move(timed));
        children.push_back(std::move(canonical));
        std::unique_ptr<runtime::CompositeSink> sink;
        status = runtime::CompositeSink::create(std::move(children), &sink);
        if (!status.ok()) throw std::runtime_error(status.message());

        application::RunOptions run_options;
        run_options.timing_enabled_override = false;
        const application::RunResult result = application::run_with_components(
            config, *source, *sink, run_options);
        if (!result.status.ok()) throw std::runtime_error(result.status.message());
        const auto cycle = canonical_ptr->cycle_hashes().find(0U);
        if (cycle == canonical_ptr->cycle_hashes().end() || canonical_ptr->frames().size() != 180U)
            throw std::runtime_error("Q5 runner did not produce exactly one 180-frame cycle");
        write_hash(options.hash_output, options.backend, cycle->second,
                   canonical_ptr->run_hash(), canonical_ptr->frames().size());
        std::cout << "Q5_" << options.backend << "_INVOCATION_PASS\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Q5_INVOCATION_FAILED: " << error.what() << '\n';
        return 1;
    }
}
