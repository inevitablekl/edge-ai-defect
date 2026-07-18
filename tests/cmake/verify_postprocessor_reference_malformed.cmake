cmake_minimum_required(VERSION 3.16)

foreach(required_variable VALIDATOR DATA_ROOT TEMP_ROOT)
    if(NOT DEFINED ${required_variable} OR "${${required_variable}}" STREQUAL "")
        message(FATAL_ERROR "${required_variable} is required")
    endif()
endforeach()

if(NOT EXISTS "${VALIDATOR}")
    message(FATAL_ERROR "Validator does not exist: ${VALIDATOR}")
endif()
if(NOT EXISTS "${DATA_ROOT}/case_no_padding/python_golden_detections.tsv")
    message(FATAL_ERROR "Reference data root is incomplete: ${DATA_ROOT}")
endif()

set(header "x1\ty1\tx2\ty2\tconfidence\tclass_id\tcandidate_index")
set(first_record "150\t150\t250\t250\t0.949999988\t0\t100")
set(golden_name "case_no_padding/python_golden_detections.tsv")
file(READ "${DATA_ROOT}/${golden_name}" original)

function(require_rejection name mutated_contents)
    set(work_root "${TEMP_ROOT}/${name}")
    file(REMOVE_RECURSE "${work_root}")
    file(COPY "${DATA_ROOT}/" DESTINATION "${work_root}/data")
    file(WRITE "${work_root}/data/${golden_name}" "${mutated_contents}")

    execute_process(
        COMMAND "${VALIDATOR}"
            --data-root "${work_root}/data"
            --cpp-output-root "${work_root}/cpp"
            --report-root "${work_root}/reports"
        RESULT_VARIABLE validator_result
        OUTPUT_VARIABLE validator_stdout
        ERROR_VARIABLE validator_stderr
    )
    if(validator_result EQUAL 0)
        message(FATAL_ERROR
            "Malformed golden '${name}' was accepted by validator.\n"
            "stdout: ${validator_stdout}\nstderr: ${validator_stderr}")
    endif()
    message(STATUS "Malformed golden rejected: ${name}")
endfunction()

string(REPLACE "${first_record}" "${first_record}\t" trailing_empty "${original}")
require_rejection("trailing_empty_field" "${trailing_empty}")

string(REPLACE "${first_record}" "${first_record}\textra" extra_nonempty "${original}")
require_rejection("extra_nonempty_field" "${extra_nonempty}")

string(REPLACE "${first_record}" "150\t150\t250\t250\t0.949999988\t0" missing_field "${original}")
require_rejection("missing_field" "${missing_field}")

string(REPLACE "${first_record}" "${first_record}\n${header}" duplicate_header "${original}")
require_rejection("duplicate_header" "${duplicate_header}")

string(REPLACE "${first_record}" "1.25abc\t150\t250\t250\t0.949999988\t0\t100" corrupt_float "${original}")
require_rejection("corrupt_float" "${corrupt_float}")

string(REPLACE "${first_record}" "150\t150\t250\t250\t0.949999988\t3abc\t100" corrupt_integer "${original}")
require_rejection("corrupt_integer" "${corrupt_integer}")

string(REPLACE "${first_record}" "nan\t150\t250\t250\t0.949999988\t0\t100" nan_value "${original}")
require_rejection("nan" "${nan_value}")

string(REPLACE "${first_record}" "inf\t150\t250\t250\t0.949999988\t0\t100" inf_value "${original}")
require_rejection("inf" "${inf_value}")

string(REPLACE "${first_record}\n" "" missing_record "${original}")
require_rejection("missing_record" "${missing_record}")

string(REPLACE "${first_record}" "${first_record}\n1\t1\t2\t2\t0.5\t0\t999" extra_record "${original}")
require_rejection("unexpected_extra_record" "${extra_record}")

string(REPLACE "${first_record}" "${first_record}\n" blank_line "${original}")
require_rejection("blank_line" "${blank_line}")

message(STATUS "PostProcessor malformed TSV validation: 11/11 rejection cases PASS")
