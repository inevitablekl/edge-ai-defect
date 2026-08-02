#!/usr/bin/env python3
"""Rebuild R3 aggregate evidence from completed per-run artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.benchmark.run_stage_r_r3_ablation import (
    ACCURACY_DELTA,
    VARIANTS,
    aggregate,
    attempt_classification,
    build_comparison,
    comparability_status,
    environment_snapshot,
    experiment_completion_status,
    interpretation_status,
    sha256,
    summarize_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir
    run_dirs = sorted((output / "runs").glob("set_*"))
    if len(run_dirs) != 20:
        raise SystemExit(f"expected 20 completed run directories, found {len(run_dirs)}")
    attempt = int(json.loads((output / "experiment_manifest.json").read_text()).get("attempt", 1))
    rows = []
    for run_dir in run_dirs:
        parts = run_dir.name.split("_")
        rows.append(summarize_run(run_dir, parts[2].upper(), int(parts[1]), attempt))
    if any(row["status"] != "PASS" for row in rows):
        raise SystemExit("one or more run artifacts are not PASS")
    status = comparability_status(attempt)
    (output / "per_run_metrics.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(attempt), "comparability_status": status, "runs": rows}, indent=2) + "\n")
    aggregates = {variant: aggregate(rows, variant) for variant in VARIANTS}
    (output / "aggregate_metrics.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(attempt), "comparability_status": status, "variants": list(aggregates.values())}, indent=2) + "\n")
    (output / "comparison_matrix.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(attempt), "comparability_status": status, "interpretation_status": interpretation_status(attempt), "comparisons": build_comparison(aggregates)}, indent=2) + "\n")
    mechanisms = {
        "V0": "CPU/OpenCV preprocessing and pageable FP32 HostTensor",
        "V2": "CUDA fused preprocessing with pageable raw staging",
        "V3": "V2 plus long-lived pinned raw staging",
        "V4": "V3 plus limited two-slot alternation",
    }
    tradeoff = []
    for variant in VARIANTS:
        tradeoff.append({
            "variant": variant,
            "performance": aggregates[variant],
            "accuracy_delta_mAP50": ACCURACY_DELTA[variant],
            "correctness_classification": "Stage Q correctness baseline" if variant == "V0" else "accuracy-trade-off experimental path; not Gate D equivalent replacement",
            "incremental_mechanism": mechanisms[variant],
            "selection_interpretation": "defer final Pareto selection to Stage R5",
        })
    (output / "performance_accuracy_tradeoff.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(attempt), "comparability_status": status, "selection_status": "NO_CANDIDATE_SELECTED", "variants": tradeoff}, indent=2) + "\n")
    temperature_rows = []
    for run_dir in run_dirs:
        samples = (run_dir / "tegrastats.log").read_text(errors="replace").splitlines()
        temperatures = []
        for line in samples:
            match = re.search(r"tj@([0-9]+(?:\.[0-9]+)?)C", line)
            if match:
                temperatures.append(float(match.group(1)))
        temperature_rows.append({
            "run_id": run_dir.name,
            "sample_count": len(temperatures),
            "start_temperature_c_from_first_tegrastats_sample": temperatures[0] if temperatures else None,
            "end_temperature_c_from_last_tegrastats_sample": temperatures[-1] if temperatures else None,
        })
    (output / "temperature_summary.json").write_text(json.dumps({"schema_version": 1, "runs": temperature_rows}, indent=2) + "\n")
    manifest_path = output / "experiment_manifest.json"
    experiment = json.loads(manifest_path.read_text())
    experiment["status"] = experiment_completion_status(attempt)
    experiment["completed_run_count"] = len(rows)
    experiment["exit_environment"] = environment_snapshot(Path.cwd())
    manifest_path.write_text(json.dumps(experiment, indent=2) + "\n")
    lines = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "artifact_sha256.txt":
            lines.append(f"{sha256(path)}  {path.relative_to(output)}")
    (output / "artifact_sha256.txt").write_text("\n".join(lines) + "\n")
    print(f"R3 aggregates rebuilt: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
