#!/usr/bin/env python3
"""Generate deterministic Phase 5.6D-A Markdown table candidates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
VISUAL = ROOT / "docs/paper/phase5_6/visual"
OUTPUT = VISUAL / "candidates"
CORRECTNESS = ROOT / "docs/paper/phase5_6/phase56b_correctness_table_source.csv"
RUNS = ROOT / "docs/paper/phase5_6/phase56b_run_level_metrics.csv"
RUNTIME = ROOT / "docs/paper/phase5_6/phase56b_runtime_state.json"
CALIBRATION = ROOT / "docs/paper/phase5_6/phase56b_calibration_provenance.json"
RELATED = VISUAL / "phase56_related_work_attribute_evidence.csv"

MARK = "> **CANDIDATE / SPECIFICATION — not manuscript authority**\n\n"


def write(name: str, title: str, body: str, note: str) -> None:
    payload = f"# {title}\n\n{MARK}{body.rstrip()}\n\n{note.rstrip()}\n"
    path = OUTPUT / name
    path.write_text(payload, encoding="utf-8", newline="\n")
    print(f"GENERATED {path.relative_to(ROOT)}")


def table1() -> None:
    rows = [
        ("Detector / Engine", "Same", "Same", "Same"),
        ("CPU pixel preprocessing", "Yes", "No", "No"),
        ("CUDA preprocessing", "No", "Yes", "Yes"),
        ("Host FP32 input tensor", "Yes", "No", "No"),
        ("Packed raw-image staging", "No", "Pageable", "Pinned"),
        ("Raw-image H2D", "No", "Yes", "Yes"),
        ("Tensor formation", "Host", "Device", "Device"),
        ("Direct TRT device-input formation", "No", "Yes", "Yes"),
        ("TRT CUDA stream reuse", "—", "Yes", "Yes"),
        ("Cross-frame pipeline", "No", "No", "No"),
    ]
    lines = ["| Path feature | V0 | V2R | V3R |", "|---|---:|---:|---:|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    write("table1_path_feature_matrix_candidate.md", "Table 1 candidate — Path Feature Matrix",
          "\n".join(lines),
          "Evidence: every data cell maps separately in `../phase56_visual_evidence_map.csv`.")


def table2() -> None:
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    proven = runtime["proven"]
    cal = calibration["calibration"]
    engine = calibration["engine"]
    with RUNS.open(encoding="utf-8", newline="") as handle:
        runs = list(csv.DictReader(handle))
    if len(runs) != 15 or {int(x["measured_frames"]) for x in runs} != {1080}:
        raise ValueError("run protocol source does not contain 15 × 1080 accepted rows")
    rows = [
        ("Platform", proven["platform"]),
        ("Software", "L4T 36.4.3; CUDA 12.6; TensorRT 10.3; OpenCV 4.5.4"),
        ("Detector / input", "YOLOv8n; 640 × 640; batch 1"),
        ("Engine", f"TensorRT INT8 mixed precision ({engine['precision_mode']}); host input {engine['host_io_dtype']}"),
        ("Calibration", f"{cal['images']} deduplicated training images; {cal['calibrator']}; batch {cal['batch_size']}; test split excluded"),
        ("Workload", "fixed 180-image test workload"),
        ("Paths", "V0 / V2R / V3R; single-frame sequential"),
        ("Timing", "60 warm-up frames; 1080 measured frames/process; 5 independent processes/path"),
        ("Formal timing", "diagnostics and profiling disabled"),
    ]
    lines = ["| Item | Setting |", "|---|---|"]
    lines.extend(f"| {item} | {value} |" for item, value in rows)
    write("table2_platform_protocol_candidate.md", "Table 2 candidate — Platform / Model / Protocol",
          "\n".join(lines),
          "Allocation of additional facts: see `../table2_platform_protocol_spec.md` (`KEEP_IN_TABLE`, `KEEP_IN_TEXT`, `OMIT_AS_REDUNDANT`).")


def table3() -> None:
    with CORRECTNESS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if [row["Path"] for row in rows] != ["V0", "V2R", "V3R"]:
        raise ValueError("correctness source must contain V0, V2R, V3R in order")
    metrics = ("Precision", "Recall", "mAP50", "mAP50-95")
    lines = ["| Path | Precision | Recall | mAP50 | mAP50-95 |",
             "|---|---:|---:|---:|---:|"]
    for row in rows:
        values = [f"{float(row[key]):.4f}" for key in metrics]
        lines.append(f"| {row['Path']} | " + " | ".join(values) + " |")
    write("table3_correctness_candidate.md", "Table 3 candidate — Task-Level Correctness",
          "\n".join(lines),
          "Source: `../../phase56b_correctness_table_source.csv`. Class-level maximum AP50 and Recall differences are both 0; gate thresholds are intentionally omitted.")


def table4() -> None:
    attrs = [
        ("Edge deployment", "边缘部署"),
        ("Detector/model fixed within comparison", "模型固定"),
        ("GPU preprocessing", "GPU预处理"),
        ("Explicit host-memory strategy", "host内存策略"),
        ("Complete E2E evaluation", "完整E2E"),
        ("Task correctness", "任务正确性"),
        ("Tail latency", "尾延迟"),
    ]
    display = {
        "YES": "是", "NO_IF_EXPLICIT": "明确否",
        "NOT_REPORTED": "未报告", "NOT_APPLICABLE": "不适用",
    }
    with RELATED.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 42:
        raise ValueError(f"related-work evidence requires 42 rows, got {len(rows)}")
    matrix: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for row in rows:
        if row["classification"] not in display:
            raise ValueError(f"invalid classification: {row['classification']}")
        if row["work"] not in matrix:
            order.append(row["work"])
            matrix[row["work"]] = {}
        matrix[row["work"]][row["attribute"]] = display[row["classification"]]
    if any(set(matrix[work]) != {key for key, _ in attrs} for work in order):
        raise ValueError("each work must resolve all seven attributes")
    lines = ["| Work | " + " | ".join(label for _, label in attrs) + " |",
             "|---|" + "---:|" * len(attrs)]
    for work in order:
        display_work = "本文" if work == "This work" else work
        lines.append(f"| {display_work} | " + " | ".join(matrix[work][key] for key, _ in attrs) + " |")
    write("table4_related_work_candidate.md", "Table 4 candidate — Related-Work Qualitative Comparison",
          "\n".join(lines),
          "Cell vocabulary: 是 = explicitly reported; 明确否 = explicitly excluded; 未报告 = not found in the audited full text and is not equivalent to no. Cell-level sources/pages: `../phase56_related_work_attribute_evidence.csv`.")


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    table1()
    table2()
    table3()
    table4()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
