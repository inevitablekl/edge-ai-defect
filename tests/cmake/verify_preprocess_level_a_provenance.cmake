cmake_minimum_required(VERSION 3.19)

if(NOT DEFINED REPO_ROOT OR REPO_ROOT STREQUAL "")
    message(FATAL_ERROR "REPO_ROOT is required")
endif()
if(NOT DEFINED PROVENANCE_FILE OR PROVENANCE_FILE STREQUAL "")
    message(FATAL_ERROR "PROVENANCE_FILE is required")
endif()
if(NOT EXISTS "${PROVENANCE_FILE}")
    message(FATAL_ERROR "Provenance file does not exist: ${PROVENANCE_FILE}")
endif()

file(READ "${PROVENANCE_FILE}" provenance_json)

function(read_json output)
    string(JSON value ERROR_VARIABLE json_error GET "${provenance_json}" ${ARGN})
    if(NOT json_error STREQUAL "NOTFOUND")
        message(FATAL_ERROR "Invalid provenance JSON at ${ARGN}: ${json_error}")
    endif()
    set(${output} "${value}" PARENT_SCOPE)
endfunction()

read_json(schema_version schema_version)
read_json(evidence_id evidence_id)
if(NOT schema_version EQUAL 1 OR NOT evidence_id STREQUAL "preprocess_level_a")
    message(FATAL_ERROR "Unexpected provenance schema or evidence_id")
endif()

read_json(source_commit source_commit)
if(NOT source_commit MATCHES "^[0-9a-f]+$")
    message(FATAL_ERROR "source_commit must be lowercase hexadecimal")
endif()
string(LENGTH "${source_commit}" source_commit_length)
if(NOT source_commit_length EQUAL 40)
    message(FATAL_ERROR "source_commit must have exactly 40 characters")
endif()

execute_process(
    COMMAND git -C "${REPO_ROOT}" cat-file -e "${source_commit}^{commit}"
    RESULT_VARIABLE source_exists
    ERROR_VARIABLE source_error
)
if(NOT source_exists EQUAL 0)
    message(FATAL_ERROR "source_commit does not exist: ${source_error}")
endif()
execute_process(
    COMMAND git -C "${REPO_ROOT}" merge-base --is-ancestor "${source_commit}" HEAD
    RESULT_VARIABLE source_is_ancestor
    ERROR_VARIABLE ancestor_error
)
if(NOT source_is_ancestor EQUAL 0)
    message(FATAL_ERROR
        "source_commit is not an ancestor of current HEAD: ${ancestor_error}")
endif()

set(evidence_keys
    generator
    validator
    manifest_parser
    compare_helper
    manifest
    sha256sums
    formal_report
)
foreach(key IN LISTS evidence_keys)
    read_json(relative_path "${key}" path)
    read_json(expected_sha "${key}" sha256)
    if(IS_ABSOLUTE "${relative_path}" OR
       relative_path MATCHES "(^|/)\\.\\.(/|$)" OR
       relative_path MATCHES "(^|/)(build|tmp)(/|$)")
        message(FATAL_ERROR "Unsafe provenance path for ${key}: ${relative_path}")
    endif()
    if(NOT expected_sha MATCHES "^[0-9a-f]+$")
        message(FATAL_ERROR "Invalid SHA256 for ${key}")
    endif()
    string(LENGTH "${expected_sha}" sha_length)
    if(NOT sha_length EQUAL 64)
        message(FATAL_ERROR "SHA256 must have 64 characters for ${key}")
    endif()
    set(evidence_path "${REPO_ROOT}/${relative_path}")
    if(NOT EXISTS "${evidence_path}")
        message(FATAL_ERROR "Provenance evidence does not exist: ${relative_path}")
    endif()
    file(SHA256 "${evidence_path}" actual_sha)
    if(NOT actual_sha STREQUAL expected_sha)
        message(FATAL_ERROR
            "Provenance SHA256 mismatch for ${relative_path}: expected=${expected_sha} actual=${actual_sha}")
    endif()
endforeach()

read_json(python_version environment python_version)
read_json(numpy_version environment numpy_version)
read_json(python_opencv_version environment python_opencv_version)
read_json(cpp_opencv_version environment cpp_opencv_version)
if(NOT python_version STREQUAL "3.10.12" OR
   NOT numpy_version STREQUAL "1.26.4" OR
   NOT python_opencv_version STREQUAL "4.10.0" OR
   NOT cpp_opencv_version STREQUAL "4.5.4")
    message(FATAL_ERROR "Provenance environment versions are not frozen values")
endif()

read_json(case_count case_count)
read_json(final_result final_result)
read_json(mae_aggregate mae_aggregate)
read_json(max_abs_aggregate max_abs_aggregate)
if(NOT case_count EQUAL 8 OR NOT final_result STREQUAL "PASS" OR
   NOT mae_aggregate EQUAL 0 OR NOT max_abs_aggregate EQUAL 0)
    message(FATAL_ERROR "Provenance validation summary is not the frozen PASS result")
endif()
foreach(index RANGE 0 3)
    read_json(shape_${index} frozen_input_shape ${index})
endforeach()
if(NOT shape_0 EQUAL 1 OR NOT shape_1 EQUAL 3 OR
   NOT shape_2 EQUAL 640 OR NOT shape_3 EQUAL 640)
    message(FATAL_ERROR "Provenance frozen input shape is not [1,3,640,640]")
endif()

message(STATUS
    "Preprocess Level A provenance: PASS source_commit=${source_commit}")
