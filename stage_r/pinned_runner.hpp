#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/runtime/image_source.hpp"
#include "edge_ai_defect/runtime/result_sink.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <filesystem>

namespace edge_ai_defect::backend_tensorrt { class TensorRtEngine; }

namespace edge_ai_defect::stage_r {

// V3 serial adapter: identical frame flow to the V2 pageable runner, but the
// raw host staging is a long-lived pinned buffer allocated once at init and
// released at shutdown. No per-frame CUDA allocation occurs.
class PinnedRunner final {
public:
    PinnedRunner(runtime::ImageSource& source,
                 backend_tensorrt::TensorRtEngine& engine,
                 postprocess::PostProcessor& postprocessor,
                 runtime::IResultSink& sink);

    [[nodiscard]] core::Status run(const runtime::RunMetadata& metadata,
                                   runtime::RunSummary* summary);

private:
    runtime::ImageSource& source_;
    backend_tensorrt::TensorRtEngine& engine_;
    postprocess::PostProcessor& postprocessor_;
    runtime::IResultSink& sink_;
};

}  // namespace edge_ai_defect::stage_r
