#!/usr/bin/env python3
"""Assemble bounded V2/V2R/V3R preprocessing evidence only."""

import argparse
import csv
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical", type=Path, required=True)
    parser.add_argument("--v2r", type=Path, required=True)
    parser.add_argument("--v3r", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    historical = load(args.historical)
    v2r = load(args.v2r)
    v3r = load(args.v3r)
    h_cases = {case["id"]: case for case in historical["cases"]}
    r_cases = {case["id"]: case for case in v2r["cases"]}
    p_cases = {case["id"]: case for case in v3r["cases"]}
    if set(h_cases) != set(r_cases) or set(r_cases) != set(p_cases):
        raise SystemExit("case identity mismatch")

    case_rows = []
    for case_id in h_cases:
        h = h_cases[case_id]
        r = r_cases[case_id]
        p = p_cases[case_id]
        case_rows.append({
            "id": case_id,
            "historical_v2_mae": h["mae"],
            "v2r_mae": r["mae"],
            "mae_delta_v2r_minus_v2": r["mae"] - h["mae"],
            "historical_v2_p99": h["p99"],
            "v2r_p99": r["p99"],
            "historical_v2_max_abs": h["max_abs"],
            "v2r_max_abs": r["max_abs"],
            "historical_v2_nonfinite": h["nonfinite"],
            "v2r_nonfinite": r["nonfinite"],
            "historical_v2_geometry": h["geometry"],
            "v2r_geometry": r["geometry"],
            "v3r_geometry": p["geometry"],
            "historical_v2_padding_mae": h["padding_mae"],
            "v2r_padding_mae": r["padding_mae"],
            "historical_v2_resize_mae": h["resize_mae"],
            "v2r_resize_mae": r["resize_mae"],
        })

    h_gate = historical["gate"]
    r_gate = v2r["gate"]
    absolute_pass = (
        r_gate["mae"] <= 5e-4
        and r_gate["p99"] <= 2 / 255 + 1e-6
        and r_gate["max_abs"] <= 4 / 255 + 1e-6
        and r_gate["nonfinite"] == 0
        and all(row["v2r_geometry"] == "PASS" for row in case_rows)
    )
    relative_pass = (
        r_gate["mae"] < h_gate["mae"]
        and r_gate["p99"] <= h_gate["p99"]
        and r_gate["max_abs"] <= h_gate["max_abs"]
        and r_gate["nonfinite"] <= h_gate["nonfinite"]
        and all(row["v2r_geometry"] == row["historical_v2_geometry"] == "PASS"
                for row in case_rows)
    )
    identity_pass = (
        v2r["tensor_digest_sha256"] == v3r["tensor_digest_sha256"]
        and all(row["v3r_geometry"] == row["v2r_geometry"] == "PASS"
                for row in case_rows)
    )
    aggregate = {
        "historical_v2": {
            "mae": h_gate["mae"], "p99": h_gate["p99"],
            "max_abs": h_gate["max_abs"], "nonfinite": h_gate["nonfinite"],
            "tensor_digest_sha256": historical["tensor_digest_sha256"],
            "padding_region": historical["padding_region"],
            "resize_region": historical["resize_region"],
        },
        "v2r": {
            "mae": r_gate["mae"], "p99": r_gate["p99"],
            "max_abs": r_gate["max_abs"], "nonfinite": r_gate["nonfinite"],
            "tensor_digest_sha256": v2r["tensor_digest_sha256"],
            "padding_region": v2r["padding_region"],
            "resize_region": v2r["resize_region"],
        },
        "v3r": {"tensor_digest_sha256": v3r["tensor_digest_sha256"]},
        "delta_v2r_minus_historical_v2": {
            "mae": r_gate["mae"] - h_gate["mae"],
            "p99": r_gate["p99"] - h_gate["p99"],
            "max_abs": r_gate["max_abs"] - h_gate["max_abs"],
        },
    }
    evidence = {
        "schema_version": 1,
        "validation": "paper_phase0_5c_i1_gate_c1_preprocess_differential",
        "corpus": historical["corpus_id"],
        "case_count": len(case_rows),
        "implementation_contract": {
            "remediation_id": "opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1",
            "resize_reference": "OpenCV C++ 4.5.4 CV_8UC3 INTER_LINEAR on aarch64",
            "scope": "fixed 640x640 letterbox, uint8 resize result, RGB NCHW FP32 /255",
        },
        "thresholds": {"mae": 5e-4, "p99": 2 / 255 + 1e-6,
                       "max_abs": 4 / 255 + 1e-6, "nonfinite": 0},
        "aggregate": aggregate,
        "checks": {"absolute_threshold_pass": absolute_pass,
                    "relative_improvement_pass": relative_pass,
                    "v2r_v3r_identity_pass": identity_pass,
                    "overall_c1_pass": absolute_pass and relative_pass and identity_pass},
        "cases": case_rows,
        "formal_gate_d": "NOT RUN",
        "task_metrics": "NOT GENERATED",
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(evidence, indent=2) + "\n")
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(case_rows[0]))
        writer.writeheader()
        writer.writerows(case_rows)
    return 0 if evidence["checks"]["overall_c1_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
