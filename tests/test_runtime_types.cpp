#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <iostream>
#include <type_traits>

namespace {

namespace runtime = edge_ai_defect::runtime;

static_assert(std::is_same_v<decltype(runtime::FrameTimings{}.source_ms), double>);
static_assert(std::is_same_v<decltype(runtime::FrameResult{}.sequence_index), std::size_t>);
static_assert(std::is_same_v<decltype(runtime::RunMetadata{}.schema_version), std::uint32_t>);

}  // namespace

int main() {
    runtime::FrameTimings timings{1.0, 2.0, 3.0, 4.0, 5.0};
    runtime::FrameResult frame;
    frame.sequence_index = 7;
    frame.relative_path = "nested/image.jpg";
    frame.image_width = 640;
    frame.image_height = 480;
    frame.timings = timings;

    runtime::RunMetadata metadata;
    metadata.schema_version = 1;
    metadata.backend_type = "onnxruntime_cpu";
    metadata.model_filename = "frozen.onnx";
    metadata.model_sha256 = "sha";
    metadata.contract_filename = "frozen.yaml";
    metadata.class_names = {"crazing"};
    metadata.timing_enabled = true;

    runtime::RunSummary summary{1, frame.detections.size()};
    if (!frame.timings.has_value() || summary.processed_images != 1U ||
        metadata.backend_type != "onnxruntime_cpu") {
        std::cerr << "Runtime data contracts did not retain assigned values\n";
        return 1;
    }

    std::cout << "Runtime data contracts test passed\n";
    return 0;
}
