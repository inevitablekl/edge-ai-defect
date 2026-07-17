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

find_package(yaml-cpp 0.7 REQUIRED CONFIG)
find_package(OpenCV 4 REQUIRED COMPONENTS core imgproc)

option(
    EDGE_AI_ENABLE_MODEL_SMOKE
    "Enable tests requiring the local frozen ONNX asset"
    OFF
)

set(
    EDGE_AI_FROZEN_ONNX_PATH
    ""
    CACHE FILEPATH
    "Path to the frozen ONNX model used by M0 smoke tests"
)

set(
    _edge_ai_frozen_onnx_example
    "${CMAKE_CURRENT_SOURCE_DIR}/models/onnx/yolov8n_neudet_frozen.onnx"
)

if(EDGE_AI_ENABLE_MODEL_SMOKE)
    if(NOT EDGE_AI_FROZEN_ONNX_PATH)
        message(FATAL_ERROR
            "EDGE_AI_FROZEN_ONNX_PATH is empty while model smoke tests are enabled.\n"
            "Configure with:\n"
            "  cmake -S . -B build "
            "-DONNXRUNTIME_ROOT=${CMAKE_CURRENT_SOURCE_DIR}/third_party/onnxruntime/1.23.2/linux-x64 "
            "-DEDGE_AI_ENABLE_MODEL_SMOKE=ON "
            "-DEDGE_AI_FROZEN_ONNX_PATH=${_edge_ai_frozen_onnx_example}"
        )
    endif()

    if(NOT EXISTS "${EDGE_AI_FROZEN_ONNX_PATH}")
        message(FATAL_ERROR
            "Frozen ONNX model does not exist: ${EDGE_AI_FROZEN_ONNX_PATH}\n"
            "Configure with:\n"
            "  cmake -S . -B build "
            "-DONNXRUNTIME_ROOT=${CMAKE_CURRENT_SOURCE_DIR}/third_party/onnxruntime/1.23.2/linux-x64 "
            "-DEDGE_AI_ENABLE_MODEL_SMOKE=ON "
            "-DEDGE_AI_FROZEN_ONNX_PATH=${_edge_ai_frozen_onnx_example}"
        )
    endif()
endif()

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
    src/letterbox.cpp
    src/model_contract.cpp
    src/preprocessor.cpp
)
target_include_directories(edge_ai_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        ${OpenCV_INCLUDE_DIRS}
)
target_link_libraries(edge_ai_core
    PUBLIC
        opencv_core
        opencv_imgproc
    PRIVATE
        yaml-cpp
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

    add_executable(test_model_contract
        tests/test_model_contract.cpp
    )
    target_link_libraries(test_model_contract
        PRIVATE
            edge_ai_core
    )
    set_target_properties(test_model_contract
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME model_contract
        COMMAND test_model_contract
            --contract
            "${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml"
            --temp-dir
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/model_contract"
    )
    set_tests_properties(model_contract
        PROPERTIES
            LABELS "m1;model-contract"
    )

    add_executable(test_letterbox
        tests/test_letterbox.cpp
    )
    target_link_libraries(test_letterbox
        PRIVATE
            edge_ai_core
    )
    set_target_properties(test_letterbox
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME letterbox_geometry COMMAND test_letterbox)
    set_tests_properties(letterbox_geometry
        PROPERTIES
            LABELS "m1;preprocess;letterbox"
    )

    add_executable(test_preprocessor
        tests/test_preprocessor.cpp
    )
    target_link_libraries(test_preprocessor
        PRIVATE
            edge_ai_core
    )
    set_target_properties(test_preprocessor
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME cpu_preprocessor COMMAND test_preprocessor)
    set_tests_properties(cpu_preprocessor
        PROPERTIES
            LABELS "m1;preprocess;cpu"
    )

    add_executable(test_ort_runtime_smoke
        tests/smoke/ort_runtime_smoke.cpp
    )
    target_compile_definitions(test_ort_runtime_smoke
        PRIVATE
            EDGE_AI_EXPECTED_ORT_VERSION="1.23.2"
    )
    target_link_libraries(test_ort_runtime_smoke
        PRIVATE
            onnxruntime::onnxruntime
    )
    set_target_properties(test_ort_runtime_smoke
        PROPERTIES
            BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME ort_runtime_smoke COMMAND test_ort_runtime_smoke)
    set_tests_properties(ort_runtime_smoke
        PROPERTIES
            LABELS "m0;smoke;onnxruntime"
    )

    if(EDGE_AI_ENABLE_MODEL_SMOKE)
        add_library(edge_ai_ort_smoke_support STATIC
            tests/smoke/ort_smoke_test_support.cpp
        )
        target_include_directories(edge_ai_ort_smoke_support
            PUBLIC
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/smoke
        )
        target_link_libraries(edge_ai_ort_smoke_support
            PUBLIC
                onnxruntime::onnxruntime
        )

        add_executable(test_ort_model_contract_smoke
            tests/smoke/ort_model_contract_smoke.cpp
        )
        target_link_libraries(test_ort_model_contract_smoke
            PRIVATE
                edge_ai_ort_smoke_support
                onnxruntime::onnxruntime
        )
        set_target_properties(test_ort_model_contract_smoke
            PROPERTIES
                BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
                RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
        )

        add_test(
            NAME ort_model_contract_smoke
            COMMAND test_ort_model_contract_smoke
                --mode positive
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
        )
        add_test(
            NAME ort_model_missing_path
            COMMAND test_ort_model_contract_smoke
                --mode missing-model
                --model /tmp/edge_ai_defect_missing_model_m0_4.onnx
        )
        add_test(
            NAME ort_model_contract_mismatch
            COMMAND test_ort_model_contract_smoke
                --mode contract-mismatch
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
        )

        add_executable(test_ort_inference_smoke
            tests/smoke/ort_inference_smoke.cpp
        )
        target_link_libraries(test_ort_inference_smoke
            PRIVATE
                edge_ai_ort_smoke_support
                onnxruntime::onnxruntime
        )
        set_target_properties(test_ort_inference_smoke
            PROPERTIES
                BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
                RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
        )
        add_test(
            NAME ort_inference_smoke
            COMMAND test_ort_inference_smoke
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
        )

        set_tests_properties(
            ort_model_contract_smoke
            ort_model_missing_path
            ort_model_contract_mismatch
            ort_inference_smoke
            PROPERTIES
                LABELS "m0;smoke;onnxruntime;model-asset"
        )
    endif()
endif()
