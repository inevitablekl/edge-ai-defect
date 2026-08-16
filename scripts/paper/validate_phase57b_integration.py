#!/usr/bin/env python3
"""Validate the Phase 5.7B contract or its approved Phase 5.7E restoration."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
SECTIONS = tuple(sorted((MANUSCRIPT / "sections").glob("*.md")))
F2_SVG = ROOT / "docs/paper/phase5_7/visual/production/figures/fig2_technical_implementation_phase57b.svg"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}
TITLE_CN = "Jetson端工业缺陷检测的输入数据路径重构"
TITLE_EN = "Input Data-Path Reconstruction for Industrial Defect Detection on Jetson"

CAPTIONS = (
    "图1　V0、V2R和V3R三条受控数据路径。图中数值为完整路径E2E观测，输入复制载荷为名义值。",
    "图2　V2R/V3R主机—设备输入路径。两者仅pageable/pinned暂存不同；复制、融合CUDA预处理与enqueueV3沿同一TensorRT CUDA stream单帧顺序执行，不表示跨帧重叠。",
    "图3　三条路径的端到端性能。(a) 为5个独立进程FPS的均值±样本标准差；(b)(c) 为每条路径合并5400个延迟样本的均值、P95和P99。",
    "图4　运行级分布与尾延迟。各点为独立进程级描述量，横向偏移仅用于区分，不表示运行配对。",
    "表1　三条受控路径的特征矩阵。检测器和TensorRT Engine相同；三条路径均为单帧顺序执行，无跨帧流水线。",
    "表2　平台、模型与统一基准协议。",
    "表3　三条路径在冻结工作负载和统一评价程序下的任务级正确性。",
    "表4　相关工作的定性定位。“未报告”不等同于“否”。",
)

FROZEN_FIGURE_HASHES = {
    "fig1_hero_data_path_phase56.png": "9fcd9388b6d12bfc027adfb7c0a1aac8690a324f7b987efe6229b7109e4fcb05",
    "fig3_main_e2e_phase56.png": "dfa125e8d20c28c93cb8a210417d72103988057cfd2bca371f2bd1c17a802ea9",
    "fig4_run_level_distribution_phase56.png": "c30ee465b6707064819504994c569d48a01067602b19c5a4c79b4b90fe296e96",
}

T4_EXPECTED = (
    ("工作", "GPU预处理", "host内存策略", "完整E2E", "任务正确性", "尾延迟"),
    ("Kim et al. (2025)", "未报告", "未报告", "是", "未报告", "未报告"),
    ("PRESTO (2025)", "是", "未报告", "未报告", "未报告", "未报告"),
    ("Tang & Qian (2024)", "明确否", "未报告", "是", "是", "未报告"),
    ("Shin & Kim (2022)", "未报告", "未报告", "未报告", "是", "未报告"),
    ("Bateni et al. (2020)", "明确否", "是", "明确否", "未报告", "未报告"),
    ("本文", "是", "是", "是", "是", "是"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def paragraph_text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).replace("\u00a0", " ").strip()


def table_signature(table: ET.Element) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple(paragraph_text(cell) for cell in row.findall("w:tc", NS))
        for row in table.findall("w:tr", NS)
    )


def source_validation(errors: list[str], phase57e: bool = False, phase57g: bool = False) -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SECTIONS)
    visible = source.replace("`", "")
    if source.count(TITLE_CN) != 1 or source.count(TITLE_EN) != 1:
        errors.append("title identity/count mismatch")
    if source.count("主要贡献包括两点") != 1 or "3）" in source:
        errors.append("contribution inventory is not exactly two")
    figures = re.findall(r"^\*\*图([1-4])　", source, re.M)
    tables = re.findall(r"^\*\*表([1-4])　", source, re.M)
    equations = re.findall(r"\\\[(.*?)\\\]", source, re.S)
    if figures != ["1", "2", "3", "4"] or tables != ["1", "2", "3", "4"]:
        errors.append(f"figure/table inventory mismatch: figures={figures} tables={tables}")
    if len(equations) != 2 or "T_{\\mathrm{E2E}}" not in equations[0] or "f_i=" not in equations[1]:
        errors.append("display-equation inventory/order is not T_E2E plus f_i")
    for caption in CAPTIONS:
        if source.replace("`", "").count(caption) != 1:
            errors.append(f"caption authority mismatch: {caption}")
    removed_tokens = [
        "@nvidia_jetpack_6_2_2", "@hill_marty_2008_amdahl",
        "@reddi_et_al_2019_mlperf_inference", "全文首先",
        "强制cache miss", "\\mu_f=",
    ]
    if not (phase57e or phase57g):
        removed_tokens.extend(("Q_p=", "h=1+(n-1)p"))
    for removed in removed_tokens:
        if removed in source:
            errors.append(f"primary-cut residue remains: {removed}")
    required = (
        "2.24×", "55.45%", "+4.07%", "−4.03%", "+0.15%", "−0.12%",
        "40.96×", "4.9152", "0.1200", "121.443–122.759", "125.595–128.301",
        "8.098–8.185", "7.740–7.894", "0.6913", "0.6991", "0.6476", "0.3523",
        "60帧", "1080", "5个独立进程", "15个独立进程", "5400",
        "MAXN_SUPER", "nvpmodel mode 2", "未调用jetson_clocks", "频率未独立归档",
        "非连续", "描述性", "不进行置信区间、假设检验或统计显著性推断",
        "不是实测总线流量", "不用于阶段级归因", "未形成一致的尾延迟改善证据",
    )
    for value in required:
        if value not in visible:
            errors.append(f"preserved scientific/runtime token missing: {value}")
    if "完整E2E”表示所报告边界覆盖预处理、模型执行及后处理/结果处理" not in visible:
        errors.append("compact complete-E2E classification rule missing")
    if "未报告信息不视为否定" not in visible:
        errors.append("NOT_REPORTED semantic rule missing")

    if phase57e or phase57g:
        restoration_tokens = (
            "按V0的OpenCV 4.5.4 INTER_LINEAR预处理语义建立受控对齐合同",
            "不构成通用CUDA/OpenCV等价性声明",
            "置信度阈值0.25", "IoU阈值0.45", "max_nms=30000", "max_det=300",
            "class-aware单标签后处理", "V2R在预设任务级差异门限下通过",
            "x_{(1)}\\leq\\cdots\\leq x_{(n)}", "p=0.95", "p=0.99",
            "h=1+(n-1)p", "j=\\lfloor h\\rfloor", "\\gamma=h-j",
            "Q_p=(1-\\gamma)x_{(j)}+\\gamma x_{(j+1)}",
            "运行级分布中重复观察到", "单一异常进程产生", "独立且不配对",
            "预处理是否移至GPU", "host暂存是否成为变量",
            "完整E2E是否覆盖预处理—模型执行—后处理/结果处理",
            "路径比较是否验证任务正确性", "报告均值外的百分位尾延迟",
            "不作首次性、唯一性或跨论文性能排名",
        )
        for token in restoration_tokens:
            if token not in visible:
                errors.append(f"Phase 5.7E restoration token missing: {token}")
        for hidden_gate in ("0.005", "0.010", "0.020", "0.030"):
            if hidden_gate in visible:
                errors.append(f"internal correctness-gate value was restored: {hidden_gate}")

    if phase57g:
        required_minor_remediations = (
            "额外打包原始图像暂存",
            "TensorRT INT8混合精度（INT8 + FP16 fallback）；Engine输入张量：FP32",
            "[@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]",
        )
        for token in required_minor_remediations:
            if token not in source:
                errors.append(f"Phase 5.7G remediation token missing: {token}")
        for superseded in ("host input FP32", "[@archet_et_al_2023_embedded_soc]"):
            if superseded in source:
                errors.append(f"Phase 5.7G superseded wording remains: {superseded}")

    with (MANUSCRIPT / "tables/table_manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest = {row["table_id"]: row for row in csv.DictReader(handle)}
    if manifest["T4"]["columns"].split(";") != list(T4_EXPECTED[0]):
        errors.append("T4 compact manifest columns mismatch")

    f2 = ET.fromstring(F2_SVG.read_text(encoding="utf-8"))
    if f2.get("width") != "160mm" or f2.get("height") != "62mm":
        errors.append("F2 geometry is not 160 mm x 62 mm")
    f2_text = "".join(f2.itertext())
    for token in (
        "主机 / CPU", "设备 / GPU", "Pageable / pinned", "cudaMemcpy2DAsync",
        "device raw", "fused CUDA", "TensorRT-owned", "enqueueV3",
        "同一 TensorRT CUDA stream",
    ):
        if token not in f2_text:
            errors.append(f"F2 topology token missing: {token}")
    for token in ("confidence", "NMS", "output D2H", "device output"):
        if token in f2_text:
            errors.append(f"F2 removed-detail residue: {token}")
    for name, expected in FROZEN_FIGURE_HASHES.items():
        path = ROOT / "docs/paper/phase5_6/visual/production/figures" / name
        if sha256_bytes(path.read_bytes()) != expected:
            errors.append(f"frozen Phase 5.6 figure hash changed: {name}")


def load_docx(path: Path) -> tuple[list[str], tuple[tuple[tuple[str, ...], ...], ...]]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        root = ET.fromstring(archive.read("word/document.xml"))
        media = [archive.read(name) for name in archive.namelist() if name.startswith("word/media/")]
    paragraphs = [paragraph_text(node) for node in root.findall(".//w:body/w:p", NS)]
    drawings = root.findall(".//w:drawing", NS)
    tables = root.findall(".//w:body/w:tbl", NS)
    equations = root.findall(".//m:oMathPara", NS)
    if (len(drawings), len(tables), len(equations)) != (4, 4, 2):
        raise ValueError(
            f"inventory mismatch: figures={len(drawings)} tables={len(tables)} equations={len(equations)}"
        )
    expected_media = {
        sha256_bytes((ROOT / "docs/paper/phase5_6/visual/production/figures/fig1_hero_data_path_phase56.png").read_bytes()),
        sha256_bytes((ROOT / "docs/paper/phase5_7/visual/production/figures/fig2_technical_implementation_phase57b.png").read_bytes()),
        sha256_bytes((ROOT / "docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png").read_bytes()),
        sha256_bytes((ROOT / "docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png").read_bytes()),
    }
    if {sha256_bytes(payload) for payload in media} != expected_media:
        raise ValueError("DOCX embedded figure payload hashes do not match F1/F2/F3/F4 authorities")
    signatures = tuple(table_signature(table) for table in tables)
    if len(signatures[0]) != 8 or any(len(row) != 4 for row in signatures[0]):
        raise ValueError("T1 is not header plus seven rows by four columns")
    if signatures[3] != T4_EXPECTED:
        raise ValueError("T4 compact cells/classifications mismatch")
    return paragraphs, signatures


def docx_validation(path: Path, errors: list[str]) -> tuple[list[str], tuple[tuple[tuple[str, ...], ...], ...]]:
    try:
        paragraphs, tables = load_docx(path)
    except (ValueError, zipfile.BadZipFile, KeyError) as exc:
        errors.append(f"{path.name}: {exc}")
        return [], tuple()
    text = "\n".join(paragraphs)
    if text.count(TITLE_CN) != 1 or text.count(TITLE_EN) != 1:
        errors.append(f"{path.name}: title mismatch")
    for caption in CAPTIONS:
        if text.count(caption) != 1:
            errors.append(f"{path.name}: rendered caption mismatch: {caption}")
    return paragraphs, tables


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--compare-full", type=Path)
    parser.add_argument(
        "--phase57e", action="store_true",
        help="validate the approved Phase 5.7E targeted-restoration contract",
    )
    parser.add_argument(
        "--phase57g", action="store_true",
        help="validate the approved Phase 5.7G final minor-remediation contract",
    )
    args = parser.parse_args()
    if args.phase57e and args.phase57g:
        parser.error("--phase57e and --phase57g are mutually exclusive")
    errors: list[str] = []
    source_validation(errors, phase57e=args.phase57e, phase57g=args.phase57g)
    paragraphs, tables = docx_validation(args.docx, errors)
    if args.compare_full:
        full_paragraphs, full_tables = docx_validation(args.compare_full, errors)
        if tables != full_tables:
            errors.append("Full/Anonymous table parity failed")
        identity = (
            "王凯伦", "王琦", "WANG Kailun", "WANG Qi", "合肥工业大学数学学院",
            "School of Mathematics, Hefei University of Technology",
        )
        scientific_full = [value for value in full_paragraphs if value and not any(token in value for token in identity)]
        if [value for value in paragraphs if value] != scientific_full:
            errors.append("Full/Anonymous visible scientific paragraph parity failed")
    if errors:
        print("verdict=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.phase57g:
        phase = "PHASE57G_FINAL_MINOR_REMEDIATION"
        reference_count = 22
    elif args.phase57e:
        phase = "PHASE57E_TARGETED_RESTORATION"
        reference_count = 23
    else:
        phase = "PHASE57B_INTEGRATION"
        reference_count = 23
    print(f"{phase}_VALIDATION=PASS")
    print(f"figures=4 tables=4 display_equations=2 contributions=2 references={reference_count}")
    print("t1_rows=7 t4_attributes=5 f2_mm=160x62 frozen_f1_f3_f4_hashes=PASS")
    print("tail=OPPOSITE_DIRECTION_NO_CONSISTENT_IMPROVEMENT nominal_payload_ratio=40.96x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
