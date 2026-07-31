#include "edge_ai_defect/stage_q/stage_q_int8_builder.hpp"
#include <iostream>

int main(int argc, char** argv) {
    try { return edge_ai_defect::stage_q::run_builder(argc, argv); }
    catch (const std::exception& error) { std::cerr << "Q2_BUILDER_IMPLEMENTATION_FAILED: " << error.what() << '\n'; return 1; }
}
