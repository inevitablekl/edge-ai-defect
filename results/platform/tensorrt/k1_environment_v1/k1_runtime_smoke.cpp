#include <cuda_runtime_api.h>

#include <NvInferRuntime.h>
#include <NvInferVersion.h>

#include <cstdlib>
#include <iostream>

namespace
{

class SmokeLogger final : public nvinfer1::ILogger
{
public:
    void log(Severity severity, nvinfer1::AsciiChar const* message) noexcept override
    {
        if (severity <= Severity::kWARNING)
        {
            std::cerr << "[TensorRT] " << message << '\n';
        }
    }
};

bool checkCuda(cudaError_t status, char const* operation)
{
    if (status == cudaSuccess)
    {
        std::cout << operation << ": PASS\n";
        return true;
    }

    std::cerr << operation << ": FAIL: " << cudaGetErrorString(status) << '\n';
    return false;
}

} // namespace

int main()
{
    std::cout << "compile_time_tensorrt_version=" << NV_TENSORRT_MAJOR << '.' << NV_TENSORRT_MINOR << '.'
              << NV_TENSORRT_PATCH << '.' << NV_TENSORRT_BUILD << '\n';
    std::cout << "runtime_tensorrt_version=" << getInferLibMajorVersion() << '.' << getInferLibMinorVersion() << '.'
              << getInferLibPatchVersion() << '.' << getInferLibBuildVersion() << '\n';

    int runtimeVersion = 0;
    if (!checkCuda(cudaRuntimeGetVersion(&runtimeVersion), "cudaRuntimeGetVersion"))
    {
        return EXIT_FAILURE;
    }
    std::cout << "cuda_runtime_version=" << runtimeVersion << '\n';

    int driverVersion = 0;
    if (!checkCuda(cudaDriverGetVersion(&driverVersion), "cudaDriverGetVersion"))
    {
        return EXIT_FAILURE;
    }
    std::cout << "cuda_driver_version=" << driverVersion << '\n';

    int deviceCount = 0;
    if (!checkCuda(cudaGetDeviceCount(&deviceCount), "cudaGetDeviceCount"))
    {
        return EXIT_FAILURE;
    }
    std::cout << "cuda_device_count=" << deviceCount << '\n';
    if (deviceCount < 1)
    {
        std::cerr << "cuda_device_count: FAIL: expected at least one device\n";
        return EXIT_FAILURE;
    }

    cudaDeviceProp deviceProperties{};
    if (!checkCuda(cudaGetDeviceProperties(&deviceProperties, 0), "cudaGetDeviceProperties(device=0)"))
    {
        return EXIT_FAILURE;
    }
    std::cout << "device_name=" << deviceProperties.name << '\n';
    std::cout << "compute_capability=" << deviceProperties.major << '.' << deviceProperties.minor << '\n';
    std::cout << "total_global_memory=" << deviceProperties.totalGlobalMem << '\n';

    if (!checkCuda(cudaSetDevice(0), "cudaSetDevice(device=0)"))
    {
        return EXIT_FAILURE;
    }

    cudaStream_t stream = nullptr;
    if (!checkCuda(cudaStreamCreate(&stream), "cudaStreamCreate"))
    {
        return EXIT_FAILURE;
    }
    if (!checkCuda(cudaStreamDestroy(stream), "cudaStreamDestroy"))
    {
        return EXIT_FAILURE;
    }

    SmokeLogger logger;
    nvinfer1::IRuntime* runtime = nvinfer1::createInferRuntime(logger);
    if (runtime == nullptr)
    {
        std::cerr << "createInferRuntime: FAIL: returned null\n";
        return EXIT_FAILURE;
    }
    std::cout << "createInferRuntime: PASS\n";
    delete runtime;
    std::cout << "TensorRT Runtime cleanup: PASS\n";
    return EXIT_SUCCESS;
}
