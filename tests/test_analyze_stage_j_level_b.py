#!/usr/bin/env python3
import json
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/validation/analyze_stage_j_level_b.py"
COUNT = 84000
V1_GOLDEN = ROOT / "results/validation/onnx_runtime_engine_level_b/python_golden_output.f32le"
V1_ACTUAL = Path("/home/orin/edge-ai-local-evidence/stage_j/j4_attempts/j4.2_level_b_v1/run_1/raw_output.f32le")


def write(path, values):
    path.write_bytes(struct.pack("<%df" % len(values), *values))


def run(golden, actual, expected=0):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        golden_path, actual_path, report_path = directory / "g.f32le", directory / "a.f32le", directory / "r.json"
        write(golden_path, golden)
        write(actual_path, actual)
        result = subprocess.run([sys.executable, str(ANALYZER), "--golden", str(golden_path), "--actual", str(actual_path), "--report", str(report_path)], capture_output=True)
        assert result.returncode == expected, (result.returncode, result.stderr)
        return json.loads(report_path.read_text(encoding="utf-8")), report_path.read_bytes()


def test_exact_and_groups():
    values = [0.0] * COUNT
    report, _ = run(values, values)
    assert report["stage_j_pass"] and report["m2_strict_equivalent"]
    assert report["bbox_group"]["element_count"] == 33600
    assert report["score_group"]["element_count"] == 50400
    assert len(report["per_channel"]) == 10

    actual = values[:]
    actual[2 * 8400 + 7] = 0.001
    report, _ = run(values, actual, expected=1)
    assert report["per_channel"][2]["max_candidate"] == 7
    assert abs(report["bbox_group"]["max_abs"] - 0.001) < 1e-8

    actual = values[:]
    actual[7 * 8400 + 11] = 0.00001
    report, _ = run(values, actual)
    assert report["score_group"]["max_error_flat_index"] == 7 * 8400 + 11


def test_boundaries_and_nonfinite():
    values = [0.0] * COUNT
    actual = values[:]
    actual[0] = 0.000011
    report, _ = run(values, actual)
    assert report["stage_j_pass"] and not report["m2_strict_equivalent"]
    actual[0] = 0.00011
    report, _ = run(values, actual, expected=1)
    assert not report["stage_j_pass"]
    for value, key in [(float("nan"), "nan_count"), (float("inf"), "positive_inf_count"), (-float("inf"), "negative_inf_count")]:
        actual = values[:]
        actual[0] = value
        report, _ = run(values, actual, expected=1)
        assert report["actual"][key] == 1 and not report["stage_j_pass"]


def test_d048_accepts_preserved_jetson_result_without_overwriting_strict():
    with tempfile.TemporaryDirectory() as directory:
        report_path = Path(directory) / "r.json"
        result = subprocess.run([sys.executable, str(ANALYZER), "--golden", str(V1_GOLDEN), "--actual", str(V1_ACTUAL), "--report", str(report_path)], capture_output=True)
        assert result.returncode == 0, result.stderr
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["strict_plan_gate"]["pass"] is False
        assert report["d048_cross_arch_policy"]["pass"] is True
        assert report["final_disposition"]["strict_plan_gate_pass"] is False
        assert report["final_disposition"]["d048_cross_arch_acceptance_pass"] is True
        assert report["final_disposition"]["final_j4_2_acceptance"] is True
        assert report["final_disposition"]["final_status"] == "COMPLETE_WITH_ACCEPTED_CROSS_ARCH_NUMERICAL_LIMITATION"


def test_d048_rejects_policy_limits_and_sha():
    values = [0.0] * COUNT
    actual = values[:]
    actual[0] = 0.0002
    report, _ = run(values, actual, expected=1)
    assert report["strict_plan_gate"]["pass"] is False
    assert report["d048_cross_arch_policy"]["pass"] is False

    actual[3 * 8400 + 1] = 0.02
    report, _ = run(values, actual, expected=1)
    assert report["d048_cross_arch_policy"]["pass"] is False

    actual = values[:]
    actual[5 * 8400 + 1] = 0.0002
    report, _ = run(values, actual, expected=1)
    assert report["d048_cross_arch_policy"]["pass"] is False


def test_wrong_count_and_determinism():
    values = [0.0] * COUNT
    report_one, bytes_one = run(values, values)
    report_two, bytes_two = run(values, values)
    assert report_one == report_two
    assert bytes_one == bytes_two
    run(values[:-1], values[:-1], expected=1)


if __name__ == "__main__":
    for test in (test_exact_and_groups, test_boundaries_and_nonfinite, test_d048_accepts_preserved_jetson_result_without_overwriting_strict, test_d048_rejects_policy_limits_and_sha, test_wrong_count_and_determinism):
        test()
    print("Stage J Level B analyzer tests passed")
