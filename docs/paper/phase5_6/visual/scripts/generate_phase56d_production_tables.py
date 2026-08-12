#!/usr/bin/env python3
"""Generate Phase 5.6D-B publication-facing table sources and caption freeze."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PHASE56 = ROOT / "docs/paper/phase5_6"
VISUAL = PHASE56 / "visual"
DEFAULT_OUTPUT = VISUAL / "production/tables"
DEFAULT_CAPTIONS = VISUAL / "production/phase56_figure_table_captions.md"

CORRECTNESS = PHASE56 / "phase56b_correctness_table_source.csv"
RUNS = PHASE56 / "phase56b_run_level_metrics.csv"
RUNTIME = PHASE56 / "phase56b_runtime_state.json"
CALIBRATION = PHASE56 / "phase56b_calibration_provenance.json"
SUMMARY = PHASE56 / "phase56b_publication_display_values.json"
EVIDENCE_MAP = VISUAL / "phase56_visual_evidence_map.csv"
RELATED = VISUAL / "phase56_related_work_attribute_evidence.csv"
FORMAL_EXECUTION = ROOT / "docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md"
RAW_ENVIRONMENT = ROOT / "docs/paper/phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json"
MANUSCRIPT_EXPERIMENT = ROOT / "docs/paper/manuscript/sections/04_experiment.md"
L4T_PUBLICATION_VALUE = "R36.5"

EXPECTED_HASHES = {
    CORRECTNESS: "d5424cb940db58eff7c826e9d99236c98ff444b37b7f45bedc993a8b70c9cf39",
    RUNS: "f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31",
    RUNTIME: "ffcc1fad184bef828417201b96484ee734ef5d21ee1b61c048879a93866fdb17",
    CALIBRATION: "10c673ce3ee3d721db053698d1570208144b5a27baccf8b07e43dbace07f5042",
    SUMMARY: "0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655",
    EVIDENCE_MAP: "4c54ba28facbc35c1753766e70b600c5c3c33d51e88255296a7eed626990a3cb",
    RELATED: "fbef3e8bff6bd38ee51417d28ff5a407932ac5a7a628b1970fac2efa9321650b",
    FORMAL_EXECUTION: "3d9ea96fc430a94b090bcd2f9241313df81d5cd82bc7f7bcb7b05f47c95a85ec",
    RAW_ENVIRONMENT: "c0451d380c21ba304bfc40165e370d9ca0f3aafd3c750fd017bb581c745f5872",
    MANUSCRIPT_EXPERIMENT: "59c12c838d2512912754f92fe16c9e2fb8bb5eff9b19fa0fed926e32da049484",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_hashes() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"frozen source hash mismatch: {path}: {actual}")


def resolve_l4t_publication_value() -> str:
    formal_report = FORMAL_EXECUTION.read_text(encoding="utf-8")
    if "| L4T | R36.5 |" not in formal_report:
        raise ValueError("formal execution report does not fix L4T at R36.5")
    raw_environment = json.loads(RAW_ENVIRONMENT.read_text(encoding="utf-8"))
    if "# R36 (release), REVISION: 5.0" not in raw_environment.get("l4t_release", ""):
        raise ValueError("raw environment record is inconsistent with L4T R36.5")
    manuscript = MANUSCRIPT_EXPERIMENT.read_text(encoding="utf-8")
    if "实际记录的软件环境为L4T R36.5" not in manuscript:
        raise ValueError("current manuscript experiment section is inconsistent with L4T R36.5")
    return L4T_PUBLICATION_VALUE


def write(path: Path, title: str, body: str, source_note: str) -> None:
    payload = (
        f"# {title}\n\n"
        f"{body.rstrip()}\n\n"
        f"Source trace: {source_note.rstrip()}\n"
    )
    path.write_text(payload, encoding="utf-8", newline="\n")
    print(f"GENERATED={path}")


def load_evidence_map() -> dict[str, dict[str, str]]:
    with EVIDENCE_MAP.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    mapped = {row["element_id"]: row for row in rows if row["asset"] == "T1"}
    if len(mapped) != 30:
        raise ValueError(f"T1 requires exactly 30 traced cells, got {len(mapped)}")
    for row in mapped.values():
        for source in (item.strip() for item in row["source_file"].split(";")):
            if not (ROOT / source).is_file():
                raise ValueError(f"T1 implementation source is missing: {source}")
    return mapped


def mapped_value(rows: dict[str, dict[str, str]], element_id: str) -> str:
    claim = rows[element_id]["claim_or_cell"]
    match = re.search(r"=([^=]+)$", claim)
    if not match:
        raise ValueError(f"T1 evidence cell has no exact value: {element_id}: {claim}")
    return match.group(1).strip()


def table1(output: Path) -> None:
    evidence = load_evidence_map()
    row_specs = [
        ("Detector / Engine", ("T1_DETECTOR_V0", "T1_DETECTOR_V2", "T1_DETECTOR_V3")),
        ("CPU像素预处理", ("T1_CPU_PRE_V0", "T1_CPU_PRE_V2", "T1_CPU_PRE_V3")),
        ("CUDA预处理", ("T1_CUDA_PRE_V0", "T1_CUDA_PRE_V2", "T1_CUDA_PRE_V3")),
        ("主机FP32输入张量", ("T1_HOST_FP32_V0", "T1_HOST_FP32_V2", "T1_HOST_FP32_V3")),
        ("打包原始图像暂存", ("T1_STAGE_V0", "T1_STAGE_V2", "T1_STAGE_V3")),
        ("原始图像H2D", ("T1_RAW_H2D_V0", "T1_RAW_H2D_V2", "T1_RAW_H2D_V3")),
        ("张量形成位置", ("T1_FORM_V0", "T1_FORM_V2", "T1_FORM_V3")),
        ("直接形成TRT设备输入", ("T1_DIRECT_V0", "T1_DIRECT_V2", "T1_DIRECT_V3")),
        ("复用TRT CUDA stream", ("T1_STREAM_V0", "T1_STREAM_V2", "T1_STREAM_V3")),
        ("跨帧流水线", ("T1_PIPE_V0", "T1_PIPE_V2", "T1_PIPE_V3")),
    ]
    translate = {
        "Same": "相同", "Yes": "是", "No": "否", "Pageable": "Pageable",
        "Pinned": "Pinned", "Host": "主机", "Device": "设备", "Not applicable": "—",
    }
    lines = ["| 路径特征 | V0 | V2R | V3R |", "|---|---:|---:|---:|"]
    for label, ids in row_specs:
        values = [translate[mapped_value(evidence, element_id)] for element_id in ids]
        lines.append(f"| {label} | " + " | ".join(values) + " |")
    write(
        output / "table1_path_feature_matrix_phase56.md",
        "V0、V2R和V3R路径特征矩阵",
        "\n".join(lines),
        "`../../phase56_visual_evidence_map.csv`；30个数据单元分别映射到当前实现 authority。",
    )


def table2(output: Path) -> None:
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    proven = runtime["proven"]
    cal = calibration["calibration"]
    engine = calibration["engine"]
    with RUNS.open(encoding="utf-8", newline="") as handle:
        runs = list(csv.DictReader(handle))
    if len(runs) != 15 or any(row["accepted"] != "true" for row in runs):
        raise ValueError("formal protocol source must contain 15 accepted processes")
    if {int(row["measured_frames"]) for row in runs} != {1080}:
        raise ValueError("formal protocol measured-frame count mismatch")
    if len({row["variant"] for row in runs}) != 3:
        raise ValueError("formal protocol path population mismatch")
    l4t = resolve_l4t_publication_value()
    rows = [
        ("平台", proven["platform"]),
        ("软件栈", f"L4T {l4t}；CUDA 12.6；TensorRT 10.3；OpenCV 4.5.4"),
        ("Detector / 输入", "YOLOv8n；640 × 640；batch 1"),
        ("Engine", f"TensorRT INT8混合精度（{engine['precision_mode']}）；host input {engine['host_io_dtype']}"),
        ("校准", f"{cal['images']}张去重训练图像；{cal['calibrator']}；batch {cal['batch_size']}；排除test split"),
        ("工作负载", "固定180张test图像"),
        ("路径", "V0 / V2R / V3R；单帧顺序执行"),
        ("计时协议", "60帧预热；每进程1080帧；每路径5个独立进程"),
        ("正式计时", "关闭diagnostics与profiling"),
    ]
    lines = ["| 项目 | 设置 |", "|---|---|"]
    lines.extend(f"| {item} | {value} |" for item, value in rows)
    write(
        output / "table2_platform_protocol_phase56.md",
        "平台、模型与统一基准协议",
        "\n".join(lines),
        "`../../../phase56b_runtime_state.json`、`../../../phase56b_calibration_provenance.json`、"
        "`../../../phase56b_run_level_metrics.csv`、`../../../../phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`、"
        "`../../../../phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json`与"
        "`../../table2_platform_protocol_spec.md`。",
    )


def table3(output: Path) -> None:
    with CORRECTNESS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if [row["Path"] for row in rows] != ["V0", "V2R", "V3R"]:
        raise ValueError("correctness source must contain V0, V2R, V3R in order")
    metrics = ("Precision", "Recall", "mAP50", "mAP50-95")
    lines = ["| Path | Precision | Recall | mAP50 | mAP50-95 |", "|---|---:|---:|---:|---:|"]
    for row in rows:
        values = [f"{float(row[key]):.4f}" for key in metrics]
        lines.append(f"| {row['Path']} | " + " | ".join(values) + " |")
    write(
        output / "table3_correctness_phase56.md",
        "V0、V2R和V3R任务级正确性",
        "\n".join(lines) +
        "\n\n注：类别级AP50和Recall的最大路径间差异均为0；内部gate阈值不进入本表。",
        "`../../../phase56b_correctness_table_source.csv`；显示精度固定为四位小数。",
    )


def table4(output: Path) -> None:
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
        if not row["source_file"] or not row["page_or_section"] or not row["supporting_paraphrase"]:
            raise ValueError("every T4 cell must retain full source trace")
        if row["work"] not in matrix:
            order.append(row["work"])
            matrix[row["work"]] = {}
        matrix[row["work"]][row["attribute"]] = display[row["classification"]]
    expected_attrs = {key for key, _ in attrs}
    if len(order) != 6 or any(set(matrix[work]) != expected_attrs for work in order):
        raise ValueError("related-work matrix must be 6 works × 7 attributes")
    lines = ["| 工作 | " + " | ".join(label for _, label in attrs) + " |",
             "|---|" + "---:|" * len(attrs)]
    for work in order:
        work_label = "本文" if work == "This work" else work
        lines.append(f"| {work_label} | " + " | ".join(matrix[work][key] for key, _ in attrs) + " |")
    note = (
        "注：‘明确否’仅表示原文明确排除；‘未报告’表示在本次审阅的全文中未找到相关报告，"
        "不等同于‘否’。本表仅用于研究属性的定性定位，不构成首次性、唯一性或优越性结论。"
    )
    write(
        output / "table4_related_work_phase56.md",
        "相关工作的研究属性定性比较",
        "\n".join(lines) + "\n\n" + note,
        "`../../phase56_related_work_attribute_evidence.csv`；42个单元均保留全文页码/章节与释义。",
    )


def captions(path: Path) -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    display = summary["publication_display_precision"]
    if summary["aggregation"]["pooled_samples_per_variant"] != 5400:
        raise ValueError("caption aggregation authority mismatch")
    payload = f"""# Phase 5.6 Figure and Table Caption Freeze

Scope: caption text frozen for later Phase 5.6E integration. This file does not modify or integrate the manuscript.

## Figures

### F1

**V0、V2R和V3R受控数据路径及完整路径观测。** V0在主机侧形成FP32 NCHW输入张量，V2R/V3R将打包原始图像复制到设备并在GPU侧形成TensorRT输入；V3R仅将V2R的pageable暂存替换为pinned暂存。性能数字表示完整端到端路径比较，不归因于单一组件。输入复制载荷为名义值，不等同于实测总线流量。

### F2

**V2R/V3R的主机—设备内存域、缓冲区生命周期与单流执行语义。** 两条路径仅在主机侧pageable/pinned暂存类型上不同；`cudaMemcpy2DAsync`、融合CUDA预处理、`enqueueV3`及输出D2H沿同一TensorRT CUDA stream顺序执行，暂存区、设备原始图像缓冲区和后端输入缓冲区跨帧复用。图中不表示跨帧重叠或流水线。

### F3

**三条受控路径的端到端性能。** (a) 柱高为每条路径5个独立进程FPS的均值，误差棒为5个进程级FPS值的样本标准差；(b) 为每条路径合并5400个延迟样本得到的平均端到端延迟；(c) 为相同5400个pooled延迟样本的P95和P99。比较值描述完整路径差异，不构成对单一组件的因果归因。

### F4

**运行级分布与尾延迟。** (a) 展示每条路径5个独立进程的FPS及描述性均值与样本标准差；(b) 展示V2R/V3R各进程的平均、P95和P99延迟。各点为独立进程级描述量，横向偏移仅用于区分且不表示配对。正式pooled P95/P99仍为Level-A aggregate metrics，来自每路径5400个延迟样本；P95变化{display['v3r_v2r_p95'].replace('-', '−')}、P99变化{display['v3r_v2r_p99'].replace('-', '−')}，方向相反，判定为MIXED。

## Tables

### T1

**V0、V2R和V3R受控数据路径的特征矩阵。** 三条路径使用相同detector和TensorRT Engine；V0在主机侧形成FP32输入张量，V2R/V3R在设备侧形成输入张量，且后两者仅在pageable与pinned原始图像暂存类型上不同。三条路径均为单帧顺序执行，无跨帧流水线。

### T2

**平台、模型与统一基准协议。** 三条路径在相同Jetson平台、YOLOv8n、冻结TensorRT INT8混合精度Engine、固定测试工作负载和统一预热/测量协议下执行；表内仅保留复现实验所需的紧凑条件。

### T3

**V0、V2R和V3R的任务级正确性。** Precision、Recall、mAP50和mAP50-95均由冻结预测证据按统一评估口径获得；各路径的汇总指标一致，类别级AP50与Recall的最大路径间差异均为0。

### T4

**相关工作的研究属性定性比较。** 表中汇总所审阅工作明确报告的研究属性；“明确否”仅用于原文明确排除的情形，“未报告”不等同于“否”。该比较用于定性定位，不表示优越性、首次性或唯一性。
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8", newline="\n")
    print(f"GENERATED={path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--captions", type=Path, default=DEFAULT_CAPTIONS)
    args = parser.parse_args()
    validate_hashes()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    table1(args.output_dir)
    table2(args.output_dir)
    table3(args.output_dir)
    table4(args.output_dir)
    captions(args.captions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
