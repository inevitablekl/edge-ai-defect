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
find_package(OpenCV 4 REQUIRED COMPONENTS core imgproc imgcodecs)
find_package(OpenSSL REQUIRED)

option(
    EDGE_AI_ENABLE_MODEL_SMOKE
    "Enable tests requiring the local frozen ONNX asset"
    OFF
)

if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64)$")
    set(_onnxruntime_platform_example "linux-aarch64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64)$")
    set(_onnxruntime_platform_example "linux-x64")
else()
    set(_onnxruntime_platform_example "linux-${CMAKE_SYSTEM_PROCESSOR}")
endif()

set(
    _onnxruntime_root_example
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/onnxruntime/1.23.2/${_onnxruntime_platform_example}"
)

message(STATUS "ONNX Runtime detected processor: ${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "ONNX Runtime selected SDK platform example: ${_onnxruntime_platform_example}")

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
            "-DONNXRUNTIME_ROOT=${_onnxruntime_root_example} "
            "-DEDGE_AI_ENABLE_MODEL_SMOKE=ON "
            "-DEDGE_AI_FROZEN_ONNX_PATH=${_edge_ai_frozen_onnx_example}"
        )
    endif()

    if(NOT EXISTS "${EDGE_AI_FROZEN_ONNX_PATH}")
        message(FATAL_ERROR
            "Frozen ONNX model does not exist: ${EDGE_AI_FROZEN_ONNX_PATH}\n"
            "Configure with:\n"
            "  cmake -S . -B build "
            "-DONNXRUNTIME_ROOT=${_onnxruntime_root_example} "
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

if(NOT ONNXRUNTIME_ROOT)
    message(FATAL_ERROR
        "ONNXRUNTIME_ROOT is empty.\n"
        "Expected SDK structure:\n"
        "  <root>/include/onnxruntime_cxx_api.h or\n"
        "  <root>/include/onnxruntime/onnxruntime_cxx_api.h\n"
        "  <root>/lib/libonnxruntime.so\n"
        "Configure with:\n"
        "  cmake -S . -B build -DONNXRUNTIME_ROOT=${_onnxruntime_root_example}"
    )
endif()

set(
    _onnxruntime_library
    "${ONNXRUNTIME_ROOT}/lib/libonnxruntime.so"
)

if(EXISTS "${ONNXRUNTIME_ROOT}/include/onnxruntime_cxx_api.h"
   AND EXISTS "${ONNXRUNTIME_ROOT}/include/onnxruntime_c_api.h")
    set(_onnxruntime_include_dir "${ONNXRUNTIME_ROOT}/include")
    set(_onnxruntime_header_layout "flat")
    set(_onnxruntime_header "${_onnxruntime_include_dir}/onnxruntime_cxx_api.h")
elseif(EXISTS "${ONNXRUNTIME_ROOT}/include/onnxruntime/onnxruntime_cxx_api.h"
       AND EXISTS "${ONNXRUNTIME_ROOT}/include/onnxruntime/onnxruntime_c_api.h")
    set(_onnxruntime_include_dir "${ONNXRUNTIME_ROOT}/include/onnxruntime")
    set(_onnxruntime_header_layout "nested")
    set(_onnxruntime_header "${_onnxruntime_include_dir}/onnxruntime_cxx_api.h")
else()
    message(FATAL_ERROR
        "ONNX Runtime C++ headers are missing. Checked:\n"
        "  ${ONNXRUNTIME_ROOT}/include/onnxruntime_cxx_api.h\n"
        "  ${ONNXRUNTIME_ROOT}/include/onnxruntime/onnxruntime_cxx_api.h\n"
        "Each candidate directory must also contain onnxruntime_c_api.h.\n"
        "Configure with:\n"
        "  cmake -S . -B build -DONNXRUNTIME_ROOT=${_onnxruntime_root_example}"
    )
endif()

message(STATUS "ONNX Runtime selected header layout: ${_onnxruntime_header_layout}")
message(STATUS "ONNX Runtime selected include directory type: ${_onnxruntime_header_layout}")

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
        INTERFACE_INCLUDE_DIRECTORIES "${_onnxruntime_include_dir}"
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
    src/onnx_runtime_options.cpp
    src/onnx_runtime_engine.cpp
)
target_include_directories(edge_ai_backend_ort
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)
target_link_libraries(edge_ai_backend_ort
    PRIVATE
        edge_ai_core
        onnxruntime::onnxruntime
        OpenSSL::Crypto
)

add_library(edge_ai_postprocess STATIC
    src/postprocess_config.cpp
    src/postprocessor.cpp
    src/postprocessor_decode.cpp
    src/postprocessor_nms.cpp
    src/postprocessor_transform.cpp
)
target_include_directories(edge_ai_postprocess
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)
target_link_libraries(edge_ai_postprocess
    PUBLIC
        edge_ai_core
)

add_library(edge_ai_runtime STATIC
    src/cli.cpp
    src/composite_sink.cpp
    src/console_sink.cpp
    src/directory_source.cpp
    src/json_sink.cpp
    src/opencv_thread_policy.cpp
    src/result_sink.cpp
    src/runtime_config.cpp
    src/serial_runner.cpp
)
target_include_directories(edge_ai_runtime
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)
target_link_libraries(edge_ai_runtime
    PUBLIC
        edge_ai_postprocess
    PRIVATE
        opencv_imgcodecs
        yaml-cpp
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
        edge_ai_runtime
)
set_target_properties(edge_ai_infer
    PROPERTIES
        BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
        OUTPUT_NAME edge_ai_defect
)

if(BUILD_TESTING)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.venv/bin/python")
        set(EDGE_AI_M5_PYTHON_EXECUTABLE "${CMAKE_CURRENT_SOURCE_DIR}/.venv/bin/python")
    else()
        set(EDGE_AI_M5_PYTHON_EXECUTABLE "${Python3_EXECUTABLE}")
    endif()

    add_test(
        NAME m5_corpus_preparation
        COMMAND
            ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_prepare_m5_corpus.py
    )
    set_tests_properties(m5_corpus_preparation
        PROPERTIES
            LABELS "m5;corpus;validation"
    )

    add_test(
        NAME m5_ort_cpu_common_unit
        COMMAND ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_ort_cpu_common.py
    )
    add_test(
        NAME m5_ort_cpu_analyzer_unit
        COMMAND ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_ort_cpu_analyze.py
    )
    add_test(
        NAME m5_ort_cpu_runner_unit
        COMMAND ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_ort_cpu_runner.py
    )
    set_tests_properties(
        m5_ort_cpu_common_unit
        m5_ort_cpu_analyzer_unit
        m5_ort_cpu_runner_unit
        PROPERTIES
            LABELS "m5;benchmark;validation"
    )

    add_test(
        NAME m5_level_c_reference_unit
        COMMAND
            ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_level_c_reference.py
    )
    add_test(
        NAME m5_level_c_compare_unit
        COMMAND
            ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_level_c_compare.py
    )
    add_test(
        NAME m5_level_c_runner_unit
        COMMAND
            ${EDGE_AI_M5_PYTHON_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_m5_level_c_runner.py
    )
    set_tests_properties(
        m5_level_c_reference_unit
        m5_level_c_compare_unit
        m5_level_c_runner_unit
        PROPERTIES
            LABELS "m5;level-c;validation"
    )

    add_executable(test_core
        tests/test_core.cpp
    )
    target_link_libraries(test_core
        PRIVATE
            edge_ai_core
    )
    add_test(NAME test_core COMMAND test_core)

    add_executable(test_postprocessor_contract
        tests/test_postprocessor_contract.cpp
    )
    target_link_libraries(test_postprocessor_contract
        PRIVATE
            edge_ai_postprocess
    )
    set_target_properties(test_postprocessor_contract
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME postprocessor_contract COMMAND test_postprocessor_contract)
    set_tests_properties(postprocessor_contract
        PROPERTIES
            LABELS "m3;postprocess;contract"
    )

    add_executable(test_postprocessor_decode
        tests/test_postprocessor_decode.cpp
    )
    target_include_directories(test_postprocessor_decode
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/src
    )
    target_link_libraries(test_postprocessor_decode
        PRIVATE
            edge_ai_postprocess
    )
    set_target_properties(test_postprocessor_decode
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME postprocessor_decode COMMAND test_postprocessor_decode)
    set_tests_properties(postprocessor_decode
        PROPERTIES
            LABELS "m3;postprocess;decode"
    )

    add_executable(test_postprocessor_nms
        tests/test_postprocessor_nms.cpp
    )
    target_include_directories(test_postprocessor_nms
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/src
    )
    target_link_libraries(test_postprocessor_nms
        PRIVATE
            edge_ai_postprocess
    )
    set_target_properties(test_postprocessor_nms
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME postprocessor_nms COMMAND test_postprocessor_nms)
    set_tests_properties(postprocessor_nms
        PROPERTIES
            LABELS "m3;postprocess;nms"
    )

    add_executable(test_postprocessor_process
        tests/test_postprocessor_process.cpp
    )
    target_link_libraries(test_postprocessor_process
        PRIVATE
            edge_ai_postprocess
    )
    set_target_properties(test_postprocessor_process
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME postprocessor_process COMMAND test_postprocessor_process)
    set_tests_properties(postprocessor_process
        PROPERTIES
            LABELS "m3;postprocess;process"
    )

    add_executable(test_postprocessor_reference
        tests/test_postprocessor_reference.cpp
    )
    target_link_libraries(test_postprocessor_reference
        PRIVATE
            edge_ai_postprocess
            yaml-cpp
    )
    set_target_properties(test_postprocessor_reference
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME postprocessor_reference
        COMMAND test_postprocessor_reference
            --data-root
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/data/postprocessor_reference"
            --cpp-output-root
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/postprocessor_only"
            --report-root
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/postprocessor_only"
    )
    set_tests_properties(postprocessor_reference
        PROPERTIES
            LABELS "m3;postprocess;reference;evidence"
    )
    add_test(
        NAME postprocessor_reference_malformed
        COMMAND "${CMAKE_COMMAND}"
            "-DVALIDATOR=$<TARGET_FILE:test_postprocessor_reference>"
            "-DDATA_ROOT=${CMAKE_CURRENT_SOURCE_DIR}/tests/data/postprocessor_reference"
            "-DTEMP_ROOT=${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/postprocessor_reference_malformed"
            -P "${CMAKE_CURRENT_SOURCE_DIR}/tests/cmake/verify_postprocessor_reference_malformed.cmake"
    )
    set_tests_properties(postprocessor_reference_malformed
        PROPERTIES
            LABELS "m3;postprocess;reference;evidence;negative"
    )

    add_executable(test_inference_engine
        tests/test_inference_engine.cpp
    )
    target_link_libraries(test_inference_engine
        PRIVATE
            edge_ai_core
    )
    add_test(NAME inference_engine_contract COMMAND test_inference_engine)
    set_tests_properties(inference_engine_contract
        PROPERTIES
            LABELS "m2;inference;contract"
    )

    add_executable(test_runtime_config
        tests/test_runtime_config.cpp
    )
    target_link_libraries(test_runtime_config
        PRIVATE
            edge_ai_runtime
            edge_ai_backend_ort
            onnxruntime::onnxruntime
    )
    set_target_properties(test_runtime_config
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME runtime_config
        COMMAND test_runtime_config
            --temp-dir
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/runtime_config"
    )
    set_tests_properties(runtime_config
        PROPERTIES
            LABELS "m4;runtime;config"
    )

    add_executable(test_cli
        tests/test_cli.cpp
    )
    target_link_libraries(test_cli
        PRIVATE
            edge_ai_runtime
    )
    set_target_properties(test_cli
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME cli_parser COMMAND test_cli)
    set_tests_properties(cli_parser
        PROPERTIES
            LABELS "m4;runtime;cli"
    )

    add_executable(test_runtime_types
        tests/test_runtime_types.cpp
    )
    target_link_libraries(test_runtime_types
        PRIVATE
            edge_ai_runtime
    )
    set_target_properties(test_runtime_types
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME runtime_types COMMAND test_runtime_types)
    set_tests_properties(runtime_types
        PROPERTIES
            LABELS "m4;runtime;contract"
    )

    add_executable(test_directory_source
        tests/test_directory_source.cpp
    )
    target_link_libraries(test_directory_source
        PRIVATE
            edge_ai_runtime
    )
    set_target_properties(test_directory_source
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME directory_source
        COMMAND test_directory_source
            --temp-dir
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/directory_source"
    )
    set_tests_properties(directory_source
        PROPERTIES
            LABELS "m4;runtime;source"
    )

    add_executable(test_result_sinks
        tests/test_result_sinks.cpp
    )
    target_link_libraries(test_result_sinks
        PRIVATE
            edge_ai_runtime
    )
    set_target_properties(test_result_sinks
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME result_sinks
        COMMAND test_result_sinks
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/result_sinks"
    )
    set_tests_properties(result_sinks
        PROPERTIES
            LABELS "m4;runtime;sink"
    )

    add_executable(test_serial_runner
        tests/test_serial_runner.cpp
    )
    target_link_libraries(test_serial_runner
        PRIVATE
            edge_ai_runtime
    )
    set_target_properties(test_serial_runner
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(NAME serial_runner COMMAND test_serial_runner)
    set_tests_properties(serial_runner
        PROPERTIES
            LABELS "m4;runtime;runner"
    )

    add_test(
        NAME application_cli
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_application_smoke.py
            --mode off
            --executable $<TARGET_FILE:edge_ai_infer>
            --temp-dir ${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/application_smoke
            --contract ${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml
    )
    set_tests_properties(application_cli
        PROPERTIES
            LABELS "m4;runtime;integration;cli"
    )

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

    add_library(preprocess_level_a_manifest_test_support STATIC
        tests/preprocess_level_a_manifest.cpp
    )
    target_include_directories(preprocess_level_a_manifest_test_support
        PUBLIC
            ${CMAKE_CURRENT_SOURCE_DIR}/tests
    )
    target_link_libraries(preprocess_level_a_manifest_test_support
        PUBLIC
            yaml-cpp
    )

    add_library(preprocess_level_a_compare_test_support STATIC
        tests/preprocess_level_a_compare.cpp
    )
    target_include_directories(preprocess_level_a_compare_test_support
        PUBLIC
            ${CMAKE_CURRENT_SOURCE_DIR}/tests
    )

    add_executable(test_preprocess_level_a
        tests/test_preprocess_level_a.cpp
    )
    target_link_libraries(test_preprocess_level_a
        PRIVATE
            edge_ai_core
            preprocess_level_a_compare_test_support
            preprocess_level_a_manifest_test_support
    )
    set_target_properties(test_preprocess_level_a
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME preprocess_level_a
        COMMAND test_preprocess_level_a
            --manifest
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/data/preprocess_level_a/manifest.yaml"
            --data-root
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/data/preprocess_level_a"
            --report
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/preprocess_level_a/level_a_report.json"
    )
    set_tests_properties(preprocess_level_a
        PROPERTIES
            LABELS "m1;preprocess;level-a"
    )

    add_executable(test_preprocess_level_a_manifest
        tests/test_preprocess_level_a_manifest.cpp
    )
    target_link_libraries(test_preprocess_level_a_manifest
        PRIVATE
            preprocess_level_a_manifest_test_support
    )
    set_target_properties(test_preprocess_level_a_manifest
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME preprocess_level_a_manifest_guard
        COMMAND test_preprocess_level_a_manifest
            --manifest
            "${CMAKE_CURRENT_SOURCE_DIR}/tests/data/preprocess_level_a/manifest.yaml"
            --temp-dir
            "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/preprocess_level_a_manifest_guard"
    )
    set_tests_properties(preprocess_level_a_manifest_guard
        PROPERTIES
            LABELS "m1;preprocess;level-a;manifest"
    )

    add_executable(test_preprocess_level_a_compare
        tests/test_preprocess_level_a_compare.cpp
    )
    target_link_libraries(test_preprocess_level_a_compare
        PRIVATE
            preprocess_level_a_compare_test_support
    )
    set_target_properties(test_preprocess_level_a_compare
        PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
    )
    add_test(
        NAME preprocess_level_a_numeric_guard
        COMMAND test_preprocess_level_a_compare
    )
    set_tests_properties(preprocess_level_a_numeric_guard
        PROPERTIES
            LABELS "m1;preprocess;level-a;numeric"
    )

    add_test(
        NAME preprocess_level_a_assets_sha256
        COMMAND ${CMAKE_COMMAND}
            -DDATA_ROOT=${CMAKE_CURRENT_SOURCE_DIR}/tests/data/preprocess_level_a
            -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/cmake/verify_preprocess_level_a_sha256.cmake
    )
    set_tests_properties(preprocess_level_a_assets_sha256
        PROPERTIES
            LABELS "m1;preprocess;level-a;evidence"
    )

    add_test(
        NAME preprocess_level_a_provenance
        COMMAND ${CMAKE_COMMAND}
            -DREPO_ROOT=${CMAKE_CURRENT_SOURCE_DIR}
            -DPROVENANCE_FILE=${CMAKE_CURRENT_SOURCE_DIR}/results/validation/preprocess_level_a/provenance.json
            -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/cmake/verify_preprocess_level_a_provenance.cmake
    )
    set_tests_properties(preprocess_level_a_provenance
        PROPERTIES
            LABELS "m1;preprocess;level-a;evidence;provenance"
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

        add_executable(test_onnx_runtime_engine_initialization
            tests/test_onnx_runtime_engine_initialization.cpp
        )
        target_link_libraries(test_onnx_runtime_engine_initialization
            PRIVATE
                edge_ai_backend_ort
                edge_ai_core
        )
        set_target_properties(test_onnx_runtime_engine_initialization
            PROPERTIES
                BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
                RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
        )
        add_test(
            NAME onnx_runtime_engine_initialization
            COMMAND test_onnx_runtime_engine_initialization
                --contract
                "${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml"
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
        )
        set_tests_properties(onnx_runtime_engine_initialization
            PROPERTIES
                LABELS "m2;onnxruntime;initialization;model-asset"
        )

        add_executable(test_onnx_runtime_engine_run
            tests/test_onnx_runtime_engine_run.cpp
        )
        target_link_libraries(test_onnx_runtime_engine_run
            PRIVATE
                edge_ai_backend_ort
                edge_ai_core
        )
        set_target_properties(test_onnx_runtime_engine_run
            PROPERTIES
                BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
                RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
        )
        add_test(
            NAME onnx_runtime_engine_run
            COMMAND test_onnx_runtime_engine_run
                --contract
                "${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml"
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
        )
        set_tests_properties(onnx_runtime_engine_run
            PROPERTIES
                LABELS "m2;onnxruntime;run;model-asset"
        )

        add_executable(test_onnx_runtime_engine_level_b
            tests/test_onnx_runtime_engine_level_b.cpp
        )
        target_link_libraries(test_onnx_runtime_engine_level_b
            PRIVATE
                edge_ai_backend_ort
                edge_ai_core
        )
        set_target_properties(test_onnx_runtime_engine_level_b
            PROPERTIES
                BUILD_RPATH "${ONNXRUNTIME_ROOT}/lib"
                RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/tests"
        )
        add_test(
            NAME onnx_runtime_engine_level_b
            COMMAND test_onnx_runtime_engine_level_b
                --contract
                "${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml"
                --model "${EDGE_AI_FROZEN_ONNX_PATH}"
                --input
                "${CMAKE_CURRENT_SOURCE_DIR}/tests/data/preprocess_level_a/golden/frozen_640_checkerboard.f32le"
                --golden
                "${CMAKE_CURRENT_SOURCE_DIR}/results/validation/onnx_runtime_engine_level_b/python_golden_output.f32le"
                --cpp-output
                "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/onnx_runtime_engine_level_b/cpp_output.f32le"
                --report
                "${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/onnx_runtime_engine_level_b/comparison_report.json"
        )
        set_tests_properties(onnx_runtime_engine_level_b
            PROPERTIES
                LABELS "m2;onnxruntime;level-b;model-asset;evidence"
        )

        add_test(
            NAME application_ort_smoke
            COMMAND
                ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_application_smoke.py
                --mode on
                --executable $<TARGET_FILE:edge_ai_infer>
                --temp-dir ${CMAKE_CURRENT_BINARY_DIR}/tests/tmp/application_smoke
                --contract ${CMAKE_CURRENT_SOURCE_DIR}/configs/model_contracts/yolov8n_neudet_frozen.yaml
                --model ${EDGE_AI_FROZEN_ONNX_PATH}
        )
        set_tests_properties(application_ort_smoke
            PROPERTIES
                LABELS "m4;runtime;integration;smoke;model-asset"
        )
    endif()
endif()
