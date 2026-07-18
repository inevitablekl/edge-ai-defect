#include "edge_ai_defect/inference/inference_engine.hpp"

#include <filesystem>
#include <iostream>
#include <type_traits>

namespace {

namespace core = edge_ai_defect::core;
namespace inference = edge_ai_defect::inference;
namespace model = edge_ai_defect::model;

class MockInferenceEngine final : public inference::IInferenceEngine {
public:
    [[nodiscard]] core::Status initialize(
        const model::ModelContract&,
        const std::filesystem::path&) override {
        return core::Status::success();
    }

    [[nodiscard]] core::Status run(const core::HostTensor&,
                                   core::HostTensor*) override {
        return core::Status::success();
    }
};

static_assert(std::has_virtual_destructor_v<inference::IInferenceEngine>);
static_assert(!std::is_copy_constructible_v<inference::IInferenceEngine>);
static_assert(!std::is_copy_assignable_v<inference::IInferenceEngine>);
static_assert(!std::is_move_constructible_v<inference::IInferenceEngine>);
static_assert(!std::is_move_assignable_v<inference::IInferenceEngine>);
static_assert(std::is_base_of_v<inference::IInferenceEngine, MockInferenceEngine>);

}  // namespace

int main() {
    MockInferenceEngine engine;
    const model::ModelContract contract;
    core::HostTensor input;
    core::HostTensor output;

    const core::Status initialize_status =
        engine.initialize(contract, std::filesystem::path("model.onnx"));
    const core::Status run_status = engine.run(input, &output);
    if (!initialize_status.ok() || !run_status.ok()) {
        std::cerr << "Mock inference engine status must succeed\n";
        return 1;
    }

    std::cout << "Inference engine contract test passed\n";
    return 0;
}
