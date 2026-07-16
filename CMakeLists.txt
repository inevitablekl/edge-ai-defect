cmake_minimum_required(VERSION 3.16)

project(
    edge_ai_defect
    VERSION 0.1.0
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CTest)

add_library(edge_ai_core STATIC
    src/core.cpp
)
target_include_directories(edge_ai_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

add_library(edge_ai_backend_ort STATIC
    src/backend_ort.cpp
)
target_include_directories(edge_ai_backend_ort
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

add_executable(edge_ai_infer
    src/main.cpp
)
target_compile_definitions(edge_ai_infer
    PRIVATE
        EDGE_AI_DEFECT_VERSION="${PROJECT_VERSION}"
)
target_link_libraries(edge_ai_infer
    PRIVATE
        edge_ai_core
        edge_ai_backend_ort
)
set_target_properties(edge_ai_infer
    PROPERTIES
        OUTPUT_NAME edge_ai_defect
)

if(BUILD_TESTING)
    add_executable(test_core
        tests/test_core.cpp
    )
    target_link_libraries(test_core
        PRIVATE
            edge_ai_core
    )
    add_test(NAME test_core COMMAND test_core)
endif()
