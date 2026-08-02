#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/runtime/image_source.hpp"
#include "edge_ai_defect/runtime/result_sink.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <filesystem>

namespace edge_ai_defect::backend_tensorrt { class TensorRtEngine; }

namespace edge_ai_defect::stage_r {

class PageableRunner final {
public:
    PageableRunner(runtime::ImageSource& source,
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
