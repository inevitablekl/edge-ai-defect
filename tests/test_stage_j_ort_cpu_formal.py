#!/usr/bin/env python3

import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/benchmark"))

from m5_ort_cpu_common import PreflightError
from run_stage_j_ort_cpu_formal import (
    CPU_SET,
    validate_asset_shas,
    validate_formal_platform,
    validate_profile,
    parse_cpu_list,
)


def profile():
    return {
        "schema_version": 2,
        "backend": {"type": "onnxruntime_cpu"},
        "onnxruntime": {
            "execution_mode": "sequential",
            "intra_op_threads": 5,
            "inter_op_threads": 1,
        },
        "runtime": {"opencv_num_threads": 1},
    }


class StageJFormalTests(unittest.TestCase):
    def test_rejects_x86_formal(self):
        with self.assertRaises(PreflightError):
            validate_formal_platform(
                system="Linux", machine="x86_64",
                model_text="NVIDIA Jetson Orin Nano",
                nvpmodel_text="MAXN_SUPER",
                clocks_text="FreqOverride=1")

    def test_accepts_manual_platform_verification_without_fan1_input(self):
        from run_stage_j_ort_cpu_formal import validate_formal_platform
        text = """manual platform verification
sudo jetson_clocks --show
Jetson Orin Nano Engineering Reference Developer Kit Super
R36.5
CPU 0-5 online
GPU 1020 MHz locked
EMC 3199000000 MHz
MAXN_SUPER
FAN Dynamic Speed Control=disabled
hwmon0_pwm1=255
sudo nvpmodel -q
"""
        self.assertEqual(
            validate_formal_platform(
                system="Linux", machine="aarch64",
                manual_verification_text=text)["source"],
            "manual_platform_verification")

    def test_rejects_wrong_profile_and_cpu_set(self):
        with self.assertRaises(PreflightError):
            validate_profile(profile(), profile="k4")
        with self.assertRaises(PreflightError):
            validate_profile(profile(), profile="k5", cpu_set={1, 2, 3, 4})
        validate_profile(profile(), profile="k5", cpu_set=CPU_SET)

    def test_linux_cpu_list_parser(self):
        self.assertEqual(parse_cpu_list("0-3,5\n"), {0, 1, 2, 3, 5})
        with self.assertRaises(Exception):
            parse_cpu_list("5-1")

    def test_rejects_wrong_k_value(self):
        value = profile()
        value["onnxruntime"]["intra_op_threads"] = 4
        with self.assertRaises(PreflightError):
            validate_profile(value, profile="k5")

    def test_rejects_timing_in_v2_profile(self):
        value = profile()
        value["timing"] = {"enabled": True}
        with self.assertRaises(PreflightError):
            validate_profile(value, profile="k5")

    def test_rejects_asset_sha_drift(self):
        with self.assertRaises(PreflightError):
            validate_asset_shas({})

    def test_formal_authorization_is_explicit_in_cli(self):
        source = (ROOT / "tools/benchmark/run_stage_j_ort_cpu_formal.py").read_text(
            encoding="utf-8")
        self.assertIn("if args.execute_formal and (args.profile != \"k5\" or not args.evidence_id)", source)
        self.assertIn("mode.add_argument(\"--execute-formal\"", source)


if __name__ == "__main__":
    unittest.main()
