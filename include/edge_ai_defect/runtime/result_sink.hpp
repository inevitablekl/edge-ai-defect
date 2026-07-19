#pragma once

#include "edge_ai_defect/core/status.hpp"
#include "edge_ai_defect/runtime/runtime_types.hpp"

namespace edge_ai_defect::runtime {

class IResultSink {
public:
    virtual ~IResultSink() = default;

    [[nodiscard]] virtual core::Status begin_run(
        const RunMetadata& metadata) = 0;
    [[nodiscard]] virtual core::Status write_frame(
        const FrameResult& frame) = 0;
    [[nodiscard]] virtual core::Status end_run(
        const RunSummary& summary) = 0;
};

}  // namespace edge_ai_defect::runtime
