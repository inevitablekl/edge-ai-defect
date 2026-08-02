#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/postprocess/postprocessor.hpp"
#include "edge_ai_defect/runtime/image_source.hpp"
#include "edge_ai_defect/runtime/result_sink.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <cstddef>

namespace edge_ai_defect::backend_tensorrt { class TensorRtEngine; }

namespace edge_ai_defect::stage_r {

struct V4RunStats {
    std::size_t buffer_count = 2U;
    std::size_t allocation_count = 0U;
    std::size_t reuse_count = 0U;
    std::size_t synchronization_count = 0U;
    std::size_t processed_frames = 0U;
    std::string tensor_digest_sha256;
};

class DoubleBufferRunner final {
public:
    DoubleBufferRunner(runtime::ImageSource& source,
                       backend_tensorrt::TensorRtEngine& engine,
                       postprocess::PostProcessor& postprocessor,
                       runtime::IResultSink& sink);

    [[nodiscard]] core::Status run(const runtime::RunMetadata& metadata,
                                   runtime::RunSummary* summary,
                                   V4RunStats* stats);

private:
    runtime::ImageSource& source_;
    backend_tensorrt::TensorRtEngine& engine_;
    postprocess::PostProcessor& postprocessor_;
    runtime::IResultSink& sink_;
};

}  // namespace edge_ai_defect::stage_r
