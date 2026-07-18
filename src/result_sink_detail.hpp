#pragma once

#include "edge_ai_defect/runtime/runtime_types.hpp"

#include <string>

namespace edge_ai_defect::runtime::detail {

[[nodiscard]] core::Status validate_metadata(const RunMetadata& metadata);
[[nodiscard]] core::Status validate_frame(const FrameResult& frame,
                                          const RunMetadata& metadata,
                                          std::size_t expected_sequence_index);
[[nodiscard]] core::Status validate_summary(const RunSummary& summary,
                                            std::size_t received_frames,
                                            std::size_t received_detections);
[[nodiscard]] std::string json_escape(const std::string& value);
[[nodiscard]] std::string serialize_run(const RunMetadata& metadata,
                                        const std::vector<FrameResult>& frames,
                                        const RunSummary& summary);

}  // namespace edge_ai_defect::runtime::detail
