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

set(
    ONNXRUNTIME_ROOT
    ""
    CACHE PATH
    "Path to the ONNX Runtime C++ SDK root"
)

set(
    _onnxruntime_root_example
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/onnxruntime/1.23.2/linux-x64"
)

if(NOT ONNXRUNTIME_ROOT)
    message(FATAL_ERROR
        "ONNXRUNTIME_ROOT is empty.\n"
        "Expected SDK structure:\n"
        "  <root>/include/onnxruntime_cxx_api.h\n"
        "  <root>/lib/libonnxruntime.so\n"
        "Configure with:\n"
        "  cmake -S . -B build -DONNXRUNTIME_ROOT=${_onnxruntime_root_example}"
    )
endif()

set(
    _onnxruntime_header
    "${ONNXRUNTIME_ROOT}/include/onnxruntime_cxx_api.h"
)
set(
    _onnxruntime_library
    "${ONNXRUNTIME_ROOT}/lib/libonnxruntime.so"
)

if(NOT EXISTS "${_onnxruntime_header}")
    message(FATAL_ERROR
        "ONNX Runtime C++ header is missing: ${_onnxruntime_header}\n"
        "Expected SDK structure: <root>/include/onnxruntime_cxx_api.h\n"
        "Configure with:\n"
        "  cmake -S . -B build -DONNXRUNTIME_ROOT=${_onnxruntime_root_example}"
    )
endif()

if(NOT EXISTS "${_onnxruntime_library}")
    message(FATAL_ERROR
        "ONNX Runtime shared library is missing: ${_onnxruntime_library}\n"
        "Expected SDK structure: <root>/lib/libonnxruntime.so\n"
        "Configure with:\n"
        "  cmake -S . -B build -DONNXRUNTIME_ROOT=${_onnxruntime_root_example}"
    )
endif()

add_library(onnxruntime::onnxruntime SHARED IMPORTED GLOBAL)
set_target_properties(onnxruntime::onnxruntime
    PROPERTIES
        IMPORTED_LOCATION "${_onnxruntime_library}"
        INTERFACE_INCLUDE_DIRECTORIES "${ONNXRUNTIME_ROOT}/include"
)

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
target_link_libraries(edge_ai_backend_ort
    PRIVATE
        onnxruntime::onnxruntime
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
        BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
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
