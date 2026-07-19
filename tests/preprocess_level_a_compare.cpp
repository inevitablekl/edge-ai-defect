#include "preprocess_level_a_compare.hpp"

#include <cmath>
#include <limits>
#include <stdexcept>

namespace edge_ai_defect::test::preprocess_level_a {
namespace {

void set_coordinates(std::size_t index,
                     const std::vector<std::int64_t>& shape,
                     int* channel,
                     int* y,
                     int* x) {
    const std::size_t height = static_cast<std::size_t>(shape[2]);
    const std::size_t width = static_cast<std::size_t>(shape[3]);
    const std::size_t plane_size = height * width;
    *channel = static_cast<int>(index / plane_size);
    const std::size_t spatial_index = index % plane_size;
    *y = static_cast<int>(spatial_index / width);
    *x = static_cast<int>(spatial_index % width);
}

void record_nonfinite(TensorComparisonResult* result,
                      const std::string& source,
                      std::size_t index,
                      float actual,
                      float golden,
                      const std::vector<std::int64_t>& shape) {
    if (result->nonfinite_detected) {
        return;
    }
    result->nonfinite_detected = true;
    result->nonfinite_source = source;
    result->nonfinite_index = index;
    result->nonfinite_actual = actual;
    result->nonfinite_golden = golden;
    set_coordinates(index,
                    shape,
                    &result->nonfinite_channel,
                    &result->nonfinite_y,
                    &result->nonfinite_x);
}

}  // namespace

TensorComparisonResult compare_preprocess_tensors(
    const std::vector<float>& actual,
    const std::vector<float>& golden,
    const std::vector<std::int64_t>& shape,
    double mae_limit,
    double max_abs_limit) {
    if (shape.size() != 4U || shape[0] != 1 || shape[1] != 3 || shape[2] <= 0 ||
        shape[3] <= 0) {
        throw std::invalid_argument("comparison shape must be positive [1,3,H,W]");
    }
    if (!std::isfinite(mae_limit) || mae_limit < 0.0 ||
        !std::isfinite(max_abs_limit) || max_abs_limit < 0.0) {
        throw std::invalid_argument("comparison limits must be finite and nonnegative");
    }

    TensorComparisonResult result;
    result.element_count = golden.size();
    result.size_match = actual.size() == golden.size();
    const std::size_t expected_count = static_cast<std::size_t>(shape[1]) *
                                       static_cast<std::size_t>(shape[2]) *
                                       static_cast<std::size_t>(shape[3]);
    if (!result.size_match || golden.size() != expected_count) {
        result.mae = std::numeric_limits<double>::max();
        result.max_abs = std::numeric_limits<double>::max();
        return result;
    }

    double absolute_error_sum = 0.0;
    for (std::size_t index = 0; index < golden.size(); ++index) {
        const float actual_float = actual[index];
        const float golden_float = golden[index];
        const double actual_value = static_cast<double>(actual_float);
        const double golden_value = static_cast<double>(golden_float);
        if (!std::isfinite(actual_value)) {
            record_nonfinite(
                &result, "actual", index, actual_float, golden_float, shape);
            continue;
        }
        if (!std::isfinite(golden_value)) {
            record_nonfinite(
                &result, "golden", index, actual_float, golden_float, shape);
            continue;
        }
        const double difference = std::abs(actual_value - golden_value);
        if (!std::isfinite(difference)) {
            record_nonfinite(
                &result, "difference", index, actual_float, golden_float, shape);
            continue;
        }
        absolute_error_sum += difference;
        if (difference > result.max_abs) {
            result.max_abs = difference;
            result.max_error_index = index;
            result.golden_at_max_error = golden_float;
            result.actual_at_max_error = actual_float;
        }
    }
    result.mae = absolute_error_sum / static_cast<double>(golden.size());
    set_coordinates(result.max_error_index,
                    shape,
                    &result.max_error_channel,
                    &result.max_error_y,
                    &result.max_error_x);
    result.pass = !result.nonfinite_detected && result.mae <= mae_limit &&
                  result.max_abs <= max_abs_limit;
    return result;
}

}  // namespace edge_ai_defect::test::preprocess_level_a
