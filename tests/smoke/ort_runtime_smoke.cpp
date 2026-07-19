#include <onnxruntime_cxx_api.h>

#include <algorithm>
#include <exception>
#include <iostream>
#include <string>
#include <vector>

namespace {

bool contains_provider(const std::vector<std::string>& providers,
                       const std::string& expected_provider) {
    return std::find(providers.begin(), providers.end(), expected_provider) !=
           providers.end();
}

}  // namespace

int main(int argc, char* argv[]) {
    std::string stage = "argument validation";

    try {
        if (argc > 2) {
            std::cerr << "Smoke stage failed: " << stage
                      << "; expected zero or one version argument\n";
            return 2;
        }

        const std::string expected_version =
            argc == 2 ? argv[1] : EDGE_AI_EXPECTED_ORT_VERSION;

        stage = "runtime version query";
        const char* version_string = OrtGetApiBase()->GetVersionString();
        if (version_string == nullptr) {
            std::cerr << "Smoke stage failed: " << stage
                      << "; exception message: version string is null\n";
            return 3;
        }

        const std::string actual_version(version_string);
        std::cout << "ONNX Runtime version: " << actual_version << '\n';
        if (actual_version != expected_version) {
            std::cerr << "Smoke stage failed: runtime version comparison\n"
                      << "Expected version: " << expected_version << '\n'
                      << "Actual version: " << actual_version << '\n';
            return 4;
        }

        stage = "provider query";
        const std::vector<std::string> providers = Ort::GetAvailableProviders();
        std::cout << "Available providers:\n";
        for (const std::string& provider : providers) {
            std::cout << "- " << provider << '\n';
        }

        if (providers.empty()) {
            std::cerr << "Smoke stage failed: " << stage
                      << "; exception message: provider list is empty\n";
            return 5;
        }

        const std::string cpu_provider = "CPUExecutionProvider";
        const std::vector<std::string> empty_providers;
        const std::vector<std::string> other_providers{
            "OtherExecutionProvider"};
        if (contains_provider(empty_providers, cpu_provider) ||
            contains_provider(other_providers, cpu_provider) ||
            !contains_provider({cpu_provider}, cpu_provider)) {
            std::cerr << "Smoke stage failed: provider matching logic\n";
            return 6;
        }

        if (!contains_provider(providers, cpu_provider)) {
            std::cerr << "Smoke stage failed: " << stage
                      << "; exception message: CPUExecutionProvider is missing\n";
            return 7;
        }
        std::cout << "CPUExecutionProvider: PASS\n";

        stage = "Ort::Env lifecycle";
        {
            Ort::Env env(ORT_LOGGING_LEVEL_WARNING,
                         "edge_ai_m0_runtime_smoke");
        }
        std::cout << "Ort::Env creation: PASS\n";

        stage = "Ort::SessionOptions lifecycle";
        {
            Ort::SessionOptions session_options;
        }
        std::cout << "Ort::SessionOptions creation: PASS\n";
        std::cout << "M0.3 runtime smoke: PASS\n";
        return 0;
    } catch (const Ort::Exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; Ort::Exception message: " << exception.what() << '\n';
    } catch (const std::exception& exception) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; std::exception message: " << exception.what() << '\n';
    } catch (...) {
        std::cerr << "Smoke stage failed: " << stage
                  << "; exception message: unknown exception\n";
    }

    return 10;
}
