#include "edge_ai_defect/backend_ort/onnx_runtime_engine.hpp"
#include "edge_ai_defect/model/model_contract_loader.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

namespace backend_ort = edge_ai_defect::backend_ort;
namespace core = edge_ai_defect::core;
namespace model = edge_ai_defect::model;
namespace fs = std::filesystem;

constexpr double kMaeLimit = 1.0e-6;
constexpr double kMaxAbsLimit = 1.0e-5;

struct Options {
    fs::path contract_path;
    fs::path model_path;
    fs::path input_path;
    fs::path golden_path;
    fs::path cpp_output_path;
    fs::path report_path;
};

struct Comparison {
    double mae = 0.0;
    double max_abs = 0.0;
    std::size_t max_abs_index = 0;
    std::size_t max_abs_channel = 0;
    std::size_t max_abs_candidate = 0;
    std::size_t golden_finite_count = 0;
    std::size_t cpp_finite_count = 0;
    bool pass = false;
};

bool host_is_little_endian() noexcept {
    const std::uint16_t value = 1U;
    return *reinterpret_cast<const std::uint8_t*>(&value) == 1U;
}

Options parse_options(int argc, char* argv[]) {
    if (argc != 13) {
        throw std::runtime_error(
            "Expected --contract <path> --model <path> --input <path> "
            "--golden <path> --cpp-output <path> --report <path>");
    }
    Options options;
    for (int index = 1; index < argc; index += 2) {
        const std::string option = argv[index];
        const fs::path path = argv[index + 1];
        if (path.empty()) {
            throw std::runtime_error("Empty path for option: " + option);
        }
        if (option == "--contract") {
            options.contract_path = path;
        } else if (option == "--model") {
            options.model_path = path;
        } else if (option == "--input") {
            options.input_path = path;
        } else if (option == "--golden") {
            options.golden_path = path;
        } else if (option == "--cpp-output") {
            options.cpp_output_path = path;
        } else if (option == "--report") {
            options.report_path = path;
        } else {
            throw std::runtime_error("Unknown option: " + option);
        }
    }
    return options;
}

std::vector<float> read_f32le(const fs::path& path, std::size_t expected_count) {
    if (!host_is_little_endian()) {
        throw std::runtime_error("Level B requires a little-endian host");
    }
    std::error_code error;
    if (!fs::is_regular_file(path, error) || error) {
        throw std::runtime_error("Tensor asset is not a readable regular file: " +
                                 path.string());
    }
    const std::uintmax_t expected_size =
        static_cast<std::uintmax_t>(expected_count) * sizeof(float);
    const std::uintmax_t actual_size = fs::file_size(path, error);
    if (error || actual_size != expected_size) {
        throw std::runtime_error("Tensor asset byte size mismatch: " + path.string());
    }
    std::vector<float> values(expected_count);
    std::ifstream input(path, std::ios::binary);
    input.read(reinterpret_cast<char*>(values.data()),
               static_cast<std::streamsize>(actual_size));
    if (!input) {
        throw std::runtime_error("Cannot read tensor asset: " + path.string());
    }
    return values;
}

void write_f32le(const fs::path& path, const std::vector<float>& values) {
    fs::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) {
        throw std::runtime_error("Cannot open C++ output path: " + path.string());
    }
    output.write(reinterpret_cast<const char*>(values.data()),
                 static_cast<std::streamsize>(values.size() * sizeof(float)));
    if (!output) {
        throw std::runtime_error("Cannot write C++ output path: " + path.string());
    }
}

Comparison compare_outputs(const std::vector<float>& golden,
                           const std::vector<float>& actual) {
    if (golden.size() != actual.size() || golden.size() != 84000U) {
        throw std::runtime_error("Level B output element count must be 84000");
    }
    Comparison comparison;
    double absolute_sum = 0.0;
    for (std::size_t index = 0; index < golden.size(); ++index) {
        if (std::isfinite(golden[index])) {
            ++comparison.golden_finite_count;
        }
        if (std::isfinite(actual[index])) {
            ++comparison.cpp_finite_count;
        }
        if (!std::isfinite(golden[index]) || !std::isfinite(actual[index])) {
            comparison.mae = std::numeric_limits<double>::infinity();
            comparison.max_abs = std::numeric_limits<double>::infinity();
            continue;
        }
        const double difference = std::abs(static_cast<double>(golden[index]) -
                                           static_cast<double>(actual[index]));
        absolute_sum += difference;
        if (difference > comparison.max_abs) {
            comparison.max_abs = difference;
            comparison.max_abs_index = index;
        }
    }
    comparison.mae = absolute_sum / static_cast<double>(golden.size());
    comparison.max_abs_channel = comparison.max_abs_index / 8400U;
    comparison.max_abs_candidate = comparison.max_abs_index % 8400U;
    comparison.pass = comparison.golden_finite_count == golden.size() &&
                      comparison.cpp_finite_count == actual.size() &&
                      comparison.mae <= kMaeLimit &&
                      comparison.max_abs <= kMaxAbsLimit;
    return comparison;
}

void write_report(const fs::path& path,
                  const Comparison& comparison,
                  const std::string& command) {
    fs::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::trunc);
    if (!output) {
        throw std::runtime_error("Cannot open report path: " + path.string());
    }
    output << std::setprecision(17)
           << "{\n"
           << "  \"schema_version\": 1,\n"
           << "  \"command\": \"" << command << "\",\n"
           << "  \"cpp_environment\": {\n"
           << "    \"compiler\": \"GCC " << __VERSION__ << "\",\n"
           << "    \"cplusplus\": " << __cplusplus << "\n"
           << "  },\n"
           << "  \"comparison\": {\n"
           << "    \"shape\": [1, 10, 8400],\n"
           << "    \"element_count\": 84000,\n"
           << "    \"golden_finite_count\": " << comparison.golden_finite_count
           << ",\n"
           << "    \"cpp_finite_count\": " << comparison.cpp_finite_count << ",\n"
           << "    \"mae\": " << comparison.mae << ",\n"
           << "    \"max_abs\": " << comparison.max_abs << ",\n"
           << "    \"max_abs_index\": " << comparison.max_abs_index << ",\n"
           << "    \"max_abs_channel\": " << comparison.max_abs_channel << ",\n"
           << "    \"max_abs_candidate\": " << comparison.max_abs_candidate << ",\n"
           << "    \"mae_limit\": " << kMaeLimit << ",\n"
           << "    \"max_abs_limit\": " << kMaxAbsLimit << ",\n"
           << "    \"pass\": " << (comparison.pass ? "true" : "false") << "\n"
           << "  }\n"
           << "}\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const Options options = parse_options(argc, argv);
        model::ModelContract contract;
        const core::Status contract_status =
            model::ModelContractLoader::load(options.contract_path, &contract);
        if (!contract_status.ok()) {
            std::cerr << contract_status.message() << '\n';
            return 2;
        }

        std::size_t input_count = 0;
        std::size_t output_count = 0;
        if (!core::checked_element_count(contract.input.tensor_info.shape, input_count).ok() ||
            !core::checked_element_count(contract.output.tensor_info.shape, output_count).ok()) {
            std::cerr << "ModelContract tensor element count is invalid\n";
            return 3;
        }
        core::HostTensor input{contract.input.tensor_info,
                               read_f32le(options.input_path, input_count)};
        if (!core::validate_host_tensor(input).ok()) {
            std::cerr << "Level B input HostTensor is invalid\n";
            return 4;
        }
        const std::vector<float> golden = read_f32le(options.golden_path, output_count);

        backend_ort::OnnxRuntimeEngine engine;
        const core::Status initialize_status =
            engine.initialize(contract, options.model_path);
        if (!initialize_status.ok()) {
            std::cerr << initialize_status.message() << '\n';
            return 5;
        }
        core::HostTensor actual;
        const core::Status run_status = engine.run(input, &actual);
        if (!run_status.ok()) {
            std::cerr << run_status.message() << '\n';
            return 6;
        }
        if (actual.info.dtype != core::TensorDataType::kFloat32 ||
            actual.info.layout != core::TensorLayout::kBcn ||
            actual.info.shape != contract.output.tensor_info.shape ||
            actual.data.size() != output_count) {
            std::cerr << "C++ Engine output contract mismatch\n";
            return 7;
        }

        std::ostringstream command;
        for (int index = 0; index < argc; ++index) {
            if (index != 0) {
                command << ' ';
            }
            command << argv[index];
        }
        write_f32le(options.cpp_output_path, actual.data);
        const Comparison comparison = compare_outputs(golden, actual.data);
        write_report(options.report_path, comparison, command.str());
        if (!comparison.pass) {
            std::cerr << "Level B comparison failed: MAE=" << comparison.mae
                      << " max_abs=" << comparison.max_abs << '\n';
            return 8;
        }
        std::cout << "Level B comparison passed: MAE=" << comparison.mae
                  << " max_abs=" << comparison.max_abs << '\n';
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "Level B validation failed: " << exception.what() << '\n';
        return 9;
    }
}
