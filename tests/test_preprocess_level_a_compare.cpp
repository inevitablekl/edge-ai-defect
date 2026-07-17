#include "preprocess_level_a_compare.hpp"

#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace {

namespace level_a = edge_ai_defect::test::preprocess_level_a;

const std::vector<std::int64_t> kShape{1, 3, 2, 2};

bool check(bool condition, const std::string& name) {
    std::cout << name << ": " << (condition ? "PASS" : "FAIL") << '\n';
    return condition;
}

int run() {
    const std::vector<float> zeros(12U, 0.0F);
    bool pass = true;

    {
        const auto result =
            level_a::compare_preprocess_tensors(zeros, zeros, kShape, 0.0, 0.0);
        pass = check(result.pass && result.mae == 0.0 && result.max_abs == 0.0,
                     "exact_equality") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[5] = 0.25F;
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 1.0, 1.0);
        pass = check(result.pass && result.max_error_index == 5U &&
                         result.actual_at_max_error == 0.25F,
                     "finite_mismatch_diagnostic") &&
               pass;
    }
    {
        std::vector<float> actual(12U, 0.2F);
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 0.1, 0.3);
        pass = check(!result.pass && result.mae > 0.1 && result.max_abs < 0.3,
                     "mae_limit_failure") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[0] = 0.2F;
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 0.1, 0.1);
        pass = check(!result.pass && result.mae < 0.1 && result.max_abs > 0.1,
                     "max_abs_limit_failure") &&
               pass;
    }
    {
        std::vector<float> golden = zeros;
        golden[3] = std::numeric_limits<float>::quiet_NaN();
        const auto result = level_a::compare_preprocess_tensors(
            zeros, golden, kShape, 1.0, 1.0);
        pass = check(!result.pass && result.nonfinite_detected &&
                         result.nonfinite_source == "golden" &&
                         result.nonfinite_index == 3U,
                     "golden_nan") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[4] = std::numeric_limits<float>::quiet_NaN();
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 1.0, 1.0);
        pass = check(!result.pass && result.nonfinite_source == "actual" &&
                         result.nonfinite_index == 4U,
                     "actual_nan") &&
               pass;
    }
    {
        std::vector<float> golden = zeros;
        golden[7] = std::numeric_limits<float>::infinity();
        const auto result = level_a::compare_preprocess_tensors(
            zeros, golden, kShape, 1.0, 1.0);
        pass = check(!result.pass && result.nonfinite_source == "golden" &&
                         std::isinf(result.nonfinite_golden),
                     "golden_positive_infinity") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[8] = -std::numeric_limits<float>::infinity();
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 1.0, 1.0);
        pass = check(!result.pass && result.nonfinite_source == "actual" &&
                         std::isinf(result.nonfinite_actual) &&
                         result.nonfinite_actual < 0.0F,
                     "actual_negative_infinity") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[7] = 1.0F;
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 1.0, 1.0);
        pass = check(result.max_error_channel == 1 && result.max_error_y == 1 &&
                         result.max_error_x == 1,
                     "nchw_coordinate_mapping") &&
               pass;
    }
    {
        std::vector<float> actual = zeros;
        actual[0] = 0.25F;
        actual[8] = 0.5F;
        const auto result = level_a::compare_preprocess_tensors(
            actual, zeros, kShape, 1.0, 1.0);
        pass = check(result.max_error_index == 8U &&
                         result.max_error_channel == 2 && result.max_error_y == 0 &&
                         result.max_error_x == 0,
                     "red_blue_plane_mapping") &&
               pass;
    }

    std::cout << "numeric_guard: " << (pass ? "10/10 PASS" : "FAIL") << '\n';
    return pass ? 0 : 1;
}

}  // namespace

int main() {
    return run();
}
