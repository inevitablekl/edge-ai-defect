#include "edge_ai_defect/core/tensor.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/preprocess/preprocessor.hpp"

#include <NvInfer.h>
#include <cuda_runtime_api.h>
#include <opencv2/imgcodecs.hpp>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

class Logger final : public nvinfer1::ILogger {
public:
    void log(Severity severity, const char* message) noexcept override {
        if (severity <= Severity::kWARNING) {
            std::cerr << "[TensorRT] " << message << '\n';
        }
    }
};

double milliseconds(Clock::time_point start, Clock::time_point end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

void check_cuda(cudaError_t status, const char* operation) {
    if (status != cudaSuccess) {
        throw std::runtime_error(std::string(operation) + ": " +
                                 cudaGetErrorString(status));
    }
}

struct Image {
    fs::path path;
    cv::Mat bgr;
};

std::vector<Image> load_images(const fs::path& directory) {
    std::vector<fs::path> paths;
    for (const auto& entry : fs::directory_iterator(directory)) {
        if (!entry.is_regular_file()) continue;
        const std::string extension = entry.path().extension().string();
        if (extension == ".jpg" || extension == ".jpeg" || extension == ".png" ||
            extension == ".bmp") {
            paths.push_back(entry.path());
        }
    }
    std::sort(paths.begin(), paths.end());
    std::vector<Image> images;
    images.reserve(paths.size());
    for (const fs::path& path : paths) {
        cv::Mat image = cv::imread(path.string(), cv::IMREAD_COLOR);
        if (image.empty() || image.type() != CV_8UC3) {
            throw std::runtime_error("cannot decode CV_8UC3 image: " + path.string());
        }
        images.push_back(Image{path.filename(), std::move(image)});
    }
    return images;
}

struct DeviceBuffer {
    void* input = nullptr;
    void* output = nullptr;
    cudaStream_t stream = nullptr;
    std::size_t input_bytes = 1U * 3U * 640U * 640U * sizeof(float);
    std::size_t output_bytes = 1U * 10U * 8400U * sizeof(float);

    ~DeviceBuffer() {
        if (input != nullptr) cudaFree(input);
        if (output != nullptr) cudaFree(output);
        if (stream != nullptr) cudaStreamDestroy(stream);
    }
};

struct Engine {
    Logger logger;
    std::unique_ptr<nvinfer1::IRuntime> runtime;
    std::unique_ptr<nvinfer1::ICudaEngine> engine;
    std::unique_ptr<nvinfer1::IExecutionContext> context;
    DeviceBuffer buffers;
    const char* input_name = "images";
    const char* output_name = "output0";

    explicit Engine(const fs::path& path) {
        std::ifstream input(path, std::ios::binary | std::ios::ate);
        if (!input.is_open()) throw std::runtime_error("cannot open engine: " + path.string());
        const std::streamsize size = input.tellg();
        if (size <= 0) throw std::runtime_error("engine is empty: " + path.string());
        std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));
        input.seekg(0);
        if (!input.read(reinterpret_cast<char*>(bytes.data()), size)) {
            throw std::runtime_error("cannot read engine: " + path.string());
        }
        runtime.reset(nvinfer1::createInferRuntime(logger));
        if (!runtime) throw std::runtime_error("createInferRuntime failed");
        engine.reset(runtime->deserializeCudaEngine(bytes.data(), bytes.size()));
        if (!engine) throw std::runtime_error("deserializeCudaEngine failed");
        context.reset(engine->createExecutionContext());
        if (!context) throw std::runtime_error("createExecutionContext failed");
        if (engine->getNbIOTensors() != 2 ||
            engine->getTensorDataType(input_name) != nvinfer1::DataType::kFLOAT ||
            engine->getTensorDataType(output_name) != nvinfer1::DataType::kFLOAT) {
            throw std::runtime_error("engine IO contract is not FP32 images/output0");
        }
        check_cuda(cudaStreamCreate(&buffers.stream), "cudaStreamCreate");
        check_cuda(cudaMalloc(&buffers.input, buffers.input_bytes), "cudaMalloc input");
        check_cuda(cudaMalloc(&buffers.output, buffers.output_bytes), "cudaMalloc output");
        if (!context->setTensorAddress(input_name, buffers.input) ||
            !context->setTensorAddress(output_name, buffers.output)) {
            throw std::runtime_error("setTensorAddress failed");
        }
    }

    struct Timing {
        double h2d_ms = 0.0;
        double inference_ms = 0.0;
    };

    Timing infer(const edge_ai_defect::core::HostTensor& tensor,
                 std::vector<float>* output) {
        output->resize(1U * 10U * 8400U);
        const auto h2d_start = Clock::now();
        check_cuda(cudaMemcpyAsync(buffers.input, tensor.data.data(), buffers.input_bytes,
                                   cudaMemcpyHostToDevice, buffers.stream),
                   "cudaMemcpyAsync H2D");
        check_cuda(cudaStreamSynchronize(buffers.stream), "cudaStreamSynchronize H2D");
        const auto h2d_end = Clock::now();

        const auto start = Clock::now();
        if (!context->enqueueV3(buffers.stream)) throw std::runtime_error("enqueueV3 failed");
        check_cuda(cudaMemcpyAsync(output->data(), buffers.output, buffers.output_bytes,
                                   cudaMemcpyDeviceToHost, buffers.stream),
                   "cudaMemcpyAsync D2H");
        check_cuda(cudaStreamSynchronize(buffers.stream), "cudaStreamSynchronize D2H");
        const auto end = Clock::now();
        return Timing{milliseconds(h2d_start, h2d_end), milliseconds(start, end)};
    }
};

void usage() {
    std::cerr << "usage: stage_k7_trt_benchmark --engine PATH --input-dir PATH "
                 "--output-csv PATH --warmup N --iterations N\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        fs::path engine_path;
        fs::path input_dir;
        fs::path output_csv;
        std::size_t warmup = 0U;
        std::size_t iterations = 0U;
        for (int index = 1; index < argc; ++index) {
            const std::string option = argv[index];
            if (index + 1 >= argc) { usage(); return 2; }
            if (option == "--engine") engine_path = argv[++index];
            else if (option == "--input-dir") input_dir = argv[++index];
            else if (option == "--output-csv") output_csv = argv[++index];
            else if (option == "--warmup") warmup = std::stoull(argv[++index]);
            else if (option == "--iterations") iterations = std::stoull(argv[++index]);
            else { usage(); return 2; }
        }
        if (engine_path.empty() || input_dir.empty() || output_csv.empty() ||
            warmup == 0U || iterations == 0U) { usage(); return 2; }

        const std::vector<Image> images = load_images(input_dir);
        if (images.size() != 180U) {
            throw std::runtime_error("expected exactly 180 input images, got " +
                                     std::to_string(images.size()));
        }
        edge_ai_defect::core::TensorInfo input_info;
        input_info.layout = edge_ai_defect::core::TensorLayout::kNchw;
        input_info.shape = {1, 3, 640, 640};
        edge_ai_defect::preprocess::Preprocessor preprocessor;
        edge_ai_defect::postprocess::PostprocessConfig postprocess_config;
        edge_ai_defect::postprocess::PostProcessor postprocessor(postprocess_config);
        Engine engine(engine_path);
        edge_ai_defect::core::HostTensor output;
        output.info.dtype = edge_ai_defect::core::TensorDataType::kFloat32;
        output.info.layout = edge_ai_defect::core::TensorLayout::kBcn;
        output.info.shape = {1, 10, 8400};

        std::ofstream csv(output_csv);
        if (!csv.is_open()) throw std::runtime_error("cannot open output CSV: " + output_csv.string());
        csv << "phase,iteration,image_index,image_name,preprocess_ms,h2d_ms,inference_ms,"
               "postprocess_ms,e2e_ms,detection_count\n";
        const std::size_t total = warmup + iterations;
        for (std::size_t ordinal = 0U; ordinal < total; ++ordinal) {
            const std::size_t image_index = ordinal % images.size();
            const Image& image = images[image_index];
            const auto e2e_start = Clock::now();
            edge_ai_defect::preprocess::PreprocessedFrame frame;
            const auto preprocess_start = Clock::now();
            const auto preprocess_status = preprocessor.preprocess(image.bgr, input_info, &frame);
            const auto preprocess_end = Clock::now();
            if (!preprocess_status.ok()) throw std::runtime_error(preprocess_status.message());
            const Engine::Timing engine_timing = engine.infer(frame.tensor, &output.data);
            std::vector<edge_ai_defect::postprocess::Detection> detections;
            const auto postprocess_start = Clock::now();
            const auto postprocess_status = postprocessor.process(output, frame.transform, &detections);
            const auto postprocess_end = Clock::now();
            if (!postprocess_status.ok()) throw std::runtime_error(postprocess_status.message());
            const bool measured = ordinal >= warmup;
            const std::size_t measured_index = measured ? ordinal - warmup : 0U;
            const double preprocess_ms = milliseconds(preprocess_start, preprocess_end);
            const double e2e_ms = milliseconds(e2e_start, postprocess_end);
            csv << (measured ? "measure" : "warmup") << ',' << measured_index << ','
                << image_index << ',' << image.path.string() << ','
                << std::fixed << std::setprecision(9) << preprocess_ms << ','
                << engine_timing.h2d_ms << ',' << engine_timing.inference_ms << ','
                << milliseconds(postprocess_start, postprocess_end) << ','
                << e2e_ms << ',' << detections.size() << '\n';
        }
        csv.flush();
        std::cout << "completed warmup=" << warmup << " iterations=" << iterations
                  << " images=" << images.size() << '\n';
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "stage_k7_trt_benchmark: " << exception.what() << '\n';
        return 1;
    }
}
