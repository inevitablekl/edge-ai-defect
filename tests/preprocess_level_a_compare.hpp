#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace edge_ai_defect::test::preprocess_level_a {

struct TensorComparisonResult {
    bool pass = false;
    bool size_match = false;
    std::size_t element_count = 0U;
    double mae = 0.0;
    double max_abs = 0.0;
    std::size_t max_error_index = 0U;
    int max_error_channel = 0;
    int max_error_y = 0;
    int max_error_x = 0;
    float golden_at_max_error = 0.0F;
    float actual_at_max_error = 0.0F;
    bool nonfinite_detected = false;
    std::string nonfinite_source;
    std::size_t nonfinite_index = 0U;
    int nonfinite_channel = 0;
    int nonfinite_y = 0;
    int nonfinite_x = 0;
    float nonfinite_actual = 0.0F;
    float nonfinite_golden = 0.0F;
};

TensorComparisonResult compare_preprocess_tensors(
    const std::vector<float>& actual,
    const std::vector<float>& golden,
    const std::vector<std::int64_t>& shape,
    double mae_limit,
    double max_abs_limit);

}  // namespace edge_ai_defect::test::preprocess_level_a
