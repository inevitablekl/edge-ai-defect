#include "edge_ai_defect/postprocess/postprocessor.hpp"

#include <utility>

namespace edge_ai_defect::postprocess {

PostProcessor::PostProcessor(PostprocessConfig config)
    : config_(std::move(config)) {}

}  // namespace edge_ai_defect::postprocess
