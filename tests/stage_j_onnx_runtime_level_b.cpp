#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"
#include "edge_ai_defect/runtime/portable_control.hpp"

#include <openssl/evp.h>
#include <opencv2/core.hpp>

#include <array>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
namespace fs = std::filesystem;
namespace core = edge_ai_defect::core;
namespace model = edge_ai_defect::model;
namespace backend_ort = edge_ai_defect::backend_ort;
namespace runtime = edge_ai_defect::runtime;

struct Options {
    fs::path config;
    fs::path input;
    fs::path raw_output;
    fs::path runtime_record;
    fs::path control_directory;
};

std::string escape(const std::string& value) {
    std::string result;
    for (const char c : value) {
        if (c == '"') result += "\\\"";
        else if (c == '\\') result += "\\\\";
        else if (c == '\n') result += "\\n";
        else if (c == '\r') result += "\\r";
        else if (c == '\t') result += "\\t";
        else result += c;
    }
    return result;
}

bool path_exists(const fs::path& path) {
    std::error_code error;
    return fs::exists(path, error) && !error;
}

std::string sha256_file(const fs::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open file for SHA256: " + path.string());
    using Context = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    Context context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context || EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) != 1)
        throw std::runtime_error("cannot initialize SHA256");
    std::array<char, 16384> buffer{};
    while (input.good()) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize count = input.gcount();
        if (count > 0 && EVP_DigestUpdate(context.get(), buffer.data(),
                                           static_cast<std::size_t>(count)) != 1)
            throw std::runtime_error("cannot update SHA256");
    }
    if (!input.eof()) throw std::runtime_error("cannot read file for SHA256");
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int size = 0;
    if (EVP_DigestFinal_ex(context.get(), digest.data(), &size) != 1)
        throw std::runtime_error("cannot finalize SHA256");
    std::ostringstream result;
    result << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < size; ++i) result << std::setw(2) << static_cast<unsigned>(digest[i]);
    return result.str();
}

std::string sha256_bytes(const std::string& bytes) {
    using Context = std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)>;
    Context context(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!context || EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) != 1 ||
        EVP_DigestUpdate(context.get(), bytes.data(), bytes.size()) != 1)
        throw std::runtime_error("cannot hash bytes");
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int size = 0;
    if (EVP_DigestFinal_ex(context.get(), digest.data(), &size) != 1)
        throw std::runtime_error("cannot finalize byte SHA256");
    std::ostringstream result;
    result << std::hex << std::setfill('0');
    for (unsigned int i = 0; i < size; ++i) result << std::setw(2) << static_cast<unsigned>(digest[i]);
    return result.str();
}

std::vector<float> read_f32le(const fs::path& path, std::size_t count) {
    const std::uint16_t one = 1;
    if (*reinterpret_cast<const std::uint8_t*>(&one) != 1) throw std::runtime_error("little-endian host required");
    std::error_code error;
    if (!fs::is_regular_file(path, error) || error || fs::file_size(path, error) != count * sizeof(float) || error)
        throw std::runtime_error("invalid tensor input size: " + path.string());
    std::vector<float> values(count);
    std::ifstream input(path, std::ios::binary);
    input.read(reinterpret_cast<char*>(values.data()), static_cast<std::streamsize>(values.size() * sizeof(float)));
    if (!input) throw std::runtime_error("cannot read tensor input: " + path.string());
    return values;
}

void write_f32le(const fs::path& path, const std::vector<float>& values) {
    if (path_exists(path)) throw std::runtime_error("raw output already exists: " + path.string());
    std::ofstream output(path, std::ios::binary);
    if (!output) throw std::runtime_error("cannot open raw output: " + path.string());
    output.write(reinterpret_cast<const char*>(values.data()), static_cast<std::streamsize>(values.size() * sizeof(float)));
    if (!output) throw std::runtime_error("cannot write raw output: " + path.string());
}

Options parse(int argc, char** argv) {
    if (argc != 11) throw std::runtime_error("expected five option/path pairs");
    Options result;
    for (int i = 1; i < argc; i += 2) {
        const std::string key = argv[i];
        const fs::path value = argv[i + 1];
        if (value.empty()) throw std::runtime_error("empty path: " + key);
        if (key == "--config") result.config = value;
        else if (key == "--input") result.input = value;
        else if (key == "--raw-output") result.raw_output = value;
        else if (key == "--runtime-record") result.runtime_record = value;
        else if (key == "--control-directory") result.control_directory = value;
        else throw std::runtime_error("unknown option: " + key);
    }
    return result;
}

std::string parallel_framework(const std::string& info) {
    const std::string marker = "Parallel framework:";
    const std::size_t begin = info.find(marker);
    if (begin == std::string::npos) return "unknown";
    const std::size_t value_begin = begin + marker.size();
    const std::size_t end = info.find('\n', value_begin);
    std::string value = info.substr(value_begin, end == std::string::npos ? std::string::npos : end - value_begin);
    const std::size_t first = value.find_first_not_of(" \t");
    return first == std::string::npos ? "unknown" : value.substr(first);
}

std::string options_record_json(const backend_ort::OrtOptionsRecord& record) {
    return record.canonical_json();
}

void write_record(const Options& options, const runtime::PortableControlSession& control,
                  const backend_ort::OnnxRuntimeEngine& engine, const model::ModelContract& contract,
                  const core::HostTensor& output) {
    if (path_exists(options.runtime_record)) throw std::runtime_error("runtime record already exists: " + options.runtime_record.string());
    const auto* applied = engine.applied_options_record();
    if (applied == nullptr) throw std::runtime_error("applied ORT options record is null");
    const std::string build = cv::getBuildInformation();
    std::size_t finite = 0, nan = 0, pos_inf = 0, neg_inf = 0;
    for (const float value : output.data) {
        if (std::isfinite(value)) ++finite;
        else if (std::isnan(value)) ++nan;
        else if (value > 0) ++pos_inf;
        else ++neg_inf;
    }
    std::ofstream out(options.runtime_record);
    if (!out) throw std::runtime_error("cannot open runtime record");
    out << "{\n"
        << "  \"requested_runtime_options\": " << options_record_json(control.ort_options()) << ",\n"
        << "  \"applied_runtime_options\": " << options_record_json(*applied) << ",\n"
        << "  \"requested_applied_match\": " << (control.ort_options().canonical_json() == applied->canonical_json() ? "true" : "false") << ",\n"
        << "  \"session_creation_succeeded\": true,\n"
        << "  \"queried_runtime_options\": {\n"
        << "    \"runtime_queryable\": false,\n"
        << "    \"verification_method\": \"successful_applied_api_call\"\n  },\n"
        << "  \"field_verification\": {\n"
        << "    \"execution_provider\": \"CPUExecutionProvider\",\n"
        << "    \"execution_provider_only\": true\n  },\n"
        << "  \"opencv_thread_policy\": {\n"
        << "    \"requested\": " << control.opencv_thread_policy().requested_threads() << ",\n"
        << "    \"reported\": " << control.opencv_thread_policy().applied_threads() << ",\n"
        << "    \"opencv_version\": \"" << escape(control.opencv_thread_policy().opencv_version()) << "\",\n"
        << "    \"build_information_sha256\": \"" << sha256_bytes(build) << "\",\n"
        << "    \"parallel_framework\": \"" << escape(parallel_framework(build)) << "\"\n  },\n"
        << "  \"input_contract\": {\"dtype\": \"float32\", \"layout\": \"NCHW\", \"shape\": [1, 3, 640, 640], \"element_count\": 1228800},\n"
        << "  \"output_contract\": {\"dtype\": \"float32\", \"layout\": \"BCN\", \"shape\": [1, 10, 8400], \"element_count\": " << output.data.size() << "},\n"
        << "  \"output_finite_count\": " << finite << ",\n"
        << "  \"output_nan_count\": " << nan << ",\n"
        << "  \"output_positive_inf_count\": " << pos_inf << ",\n"
        << "  \"output_negative_inf_count\": " << neg_inf << "\n}\n";
    if (!out) throw std::runtime_error("cannot write runtime record");
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const Options options = parse(argc, argv);
        if (path_exists(options.raw_output) || path_exists(options.runtime_record)) throw std::runtime_error("output target already exists");
        std::unique_ptr<const runtime::PortableControlSession> control;
        const runtime::PortableControlOptions control_options{
            fs::absolute(argv[0]), options.config, options.control_directory, {}, false};
        core::Status status = runtime::PortableControlSession::start(control_options, &control);
        if (!status.ok()) throw std::runtime_error(status.message());
        model::ModelContract contract;
        status = model::ModelContractLoader::load(control->config().model_contract_path, &contract);
        if (!status.ok()) throw std::runtime_error(status.message());
        std::size_t input_count = 0, output_count = 0;
        if (!core::checked_element_count(contract.input.tensor_info.shape, input_count).ok() ||
            !core::checked_element_count(contract.output.tensor_info.shape, output_count).ok()) throw std::runtime_error("invalid contract shape");
        core::HostTensor input{contract.input.tensor_info, read_f32le(options.input, input_count)};
        if (!core::validate_host_tensor(input).ok()) throw std::runtime_error("invalid input HostTensor");
        backend_ort::OnnxRuntimeEngine engine;
        status = engine.initialize(control->config(), contract, control->config().model_path);
        if (!status.ok()) throw std::runtime_error(status.message());
        if (engine.applied_options_record() == nullptr) throw std::runtime_error("missing applied options record");
        core::HostTensor output;
        status = engine.run(input, &output);
        if (!status.ok()) throw std::runtime_error(status.message());
        if (output.data.size() != output_count || output.info.layout != core::TensorLayout::kBcn) throw std::runtime_error("output contract mismatch");
        write_f32le(options.raw_output, output.data);
        write_record(options, *control, engine, contract, output);
        status = control->write_evidence_record();
        if (!status.ok()) throw std::runtime_error(status.message());
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "Stage J Level B runner failed: " << exception.what() << '\n';
        return 1;
    }
}
