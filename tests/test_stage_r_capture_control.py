#!/usr/bin/env python3
"""Contract checks for the Stage R measured NVTX capture boundary."""

import argparse
import json
from pathlib import Path


START_MARKER = 'nvtxMarkA("stage_r.measured_phase_start");'
RANGE_BEGIN = 'nvtxRangePushA("stage_r.measured");'
END_MARKER = 'nvtxMarkA("stage_r.measured_phase_end");'
RANGE_END = "nvtxRangePop();"
EXPECTED_SHA = "12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    source = (root / "tools/validation/stage_r_experiment_runner.cpp").read_text()

    for expression, name in (
        (START_MARKER, "measured start marker"),
        (RANGE_BEGIN, "measured range begin"),
        (END_MARKER, "measured end marker"),
        (RANGE_END, "measured range end"),
    ):
        require(source.count(expression) == 1, f"{name} must occur exactly once")

    warmup = source.index("status = run_phase(config, *warmup_source")
    metrics = source.index("MetricsSink metrics(*composite);")
    start_marker = source.index(START_MARKER)
    range_begin = source.index(RANGE_BEGIN)
    measured = source.index("status = run_phase(config, *measured_source")
    end_marker = source.index(END_MARKER)
    range_end = source.index(RANGE_END)
    require(warmup < metrics < start_marker < range_begin < measured < end_marker < range_end,
            "NVTX boundary order does not match warmup -> measured contract")

    require(source.count("metrics.frames() != a.measured_frames") == 1,
            "measured frame-count validation changed")
    require("measured_summary.processed_images != a.measured_frames" in source,
            "measured processed-image validation is missing")

    summary = json.loads((root / "results/validation/stage_r/r1_baseline_profiling_v1/profiling_summary.json").read_text())
    equivalence = json.loads((root / "results/validation/stage_r/r1_baseline_profiling_v1/baseline_equivalence_summary.json").read_text())
    require(equivalence["result_json_schema"] == 4, "Result JSON schema changed")
    require(summary["measured_frames"] == 1800, "formal measured frame count changed")
    require(equivalence["warmup_frames"] == 180 and equivalence["measured_frames"] == 180,
            "equivalence frame counts changed")
    require(summary["off"]["detection_sha256"] == EXPECTED_SHA, "off detection SHA changed")
    require(summary["diagnostic"]["detection_sha256"] == EXPECTED_SHA,
            "diagnostic detection SHA changed")
    require(equivalence["expected_detection_sha256"] == EXPECTED_SHA,
            "canonical detection SHA changed")
    require(equivalence["v5"]["detection_sha256"] == EXPECTED_SHA and
            equivalence["v6"]["detection_sha256"] == EXPECTED_SHA,
            "baseline detection SHA changed")
    print("Stage R capture control contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
