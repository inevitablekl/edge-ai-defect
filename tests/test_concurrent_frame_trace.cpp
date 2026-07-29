#include "edge_ai_defect/runtime/frame_trace.hpp"

#include <iostream>
#include <sstream>

int main() {
    using namespace edge_ai_defect::runtime;
    ConcurrentFrameTraceRecorder recorder;
    if (!recorder.on_stage_begin(0, FrameTraceStage::kSource, 10).ok() ||
        !recorder.on_stage_begin(0, FrameTraceStage::kInference, 20).ok() ||
        !recorder.on_stage_end(0, FrameTraceStage::kSource, 30).ok() ||
        !recorder.on_stage_end(0, FrameTraceStage::kInference, 40).ok()) return 1;
    if (recorder.has_complete_frame(0) || recorder.has_complete_frame(1)) return 1;
    if (!recorder.on_stage_begin(1, FrameTraceStage::kSource, 50).ok() ||
        !recorder.on_stage_end(1, FrameTraceStage::kSource, 60).ok()) return 1;
    std::ostringstream output;
    if (!recorder.flush(output).ok() || recorder.records().size() != 3U) return 1;
    if (recorder.aggregates().at(FrameTraceStage::kSource).count != 2U) return 1;
    std::cout << "Concurrent frame trace tests passed\n";
    return 0;
}
