#include <opencv2/core.hpp>
#include <opencv2/core/version.hpp>

#include <iostream>
#include <string>

#define main stage_j_preprocess_level_a_legacy_main
#include "test_preprocess_level_a.cpp"
#undef main

int main(int argc, char** argv) {
    cv::setNumThreads(1);
    const int reported_threads = cv::getNumThreads();
    std::cout << "STAGE_J_OPENCV_THREAD_POLICY={\"requested_threads\":1,\"reported_threads\":"
              << reported_threads << ",\"opencv_version\":\"" << CV_VERSION
              << "\",\"policy_active\":"
              << (reported_threads == 1 ? "true" : "false") << "}\n";

    std::cout << "STAGE_J_OPENCV_BUILD_INFORMATION_BEGIN\n";
    const std::string build_information = cv::getBuildInformation();
    std::cout << build_information;
    if (build_information.empty() || build_information.back() != '\n') {
        std::cout << '\n';
    }
    std::cout << "STAGE_J_OPENCV_BUILD_INFORMATION_END\n";

    if (reported_threads != 1) {
        return 5;
    }
    return stage_j_preprocess_level_a_legacy_main(argc, argv);
}
