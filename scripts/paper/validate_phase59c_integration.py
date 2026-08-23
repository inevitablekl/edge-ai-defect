#!/usr/bin/env python3
"""Validate the Phase 5.9C theory-oriented reconstruction contract."""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
SECTIONS = tuple(sorted((MANUSCRIPT / "sections").glob("*.md")))
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}

TITLE_CN = "Jetson端工业缺陷检测的输入数据路径重构"
TITLE_EN = "Input Data-Path Reconstruction for Industrial Defect Detection on Jetson"

CAPTIONS = (
    "图1　输入数据路径抽象及层级受控比较。图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。",
    "图2　三条路径的端到端性能。(a) 为5个独立进程FPS的均值±样本标准差；(b)(c) 为每条路径合并5400个延迟样本的均值、P95和P99。",
    "图3　运行级分布与尾延迟。各点为独立进程级描述量，横向偏移仅用于区分，不表示运行配对。",
    "表1　三条输入数据路径的结构描述与派生量。名义输入复制载荷由跨边界表示推导，非实测流量。",
    "表2　平台、模型与统一基准协议。",
    "表3　三条路径在冻结工作负载和统一评价程序下的任务级正确性。",
)

FIGURE_ASSETS = (
    ROOT / "docs/paper/phase5_9/visual/production/figures/fig1_input_data_path_model_phase59c.png",
    ROOT / "docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png",
    ROOT / "docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png",
)

FROZEN_VALUES = (
    "54.600", "18.273", "122.122", "8.140", "127.097", "7.812",
    "2.236671×", "2.24×", "55.4519%", "55.45%",
    "4.0738%", "+4.07%", "4.0349%", "−4.03%",
    "+0.1514%", "+0.15%", "−0.1184%", "−0.12%",
    "4.9152 MB/frame", "0.1200 MB/frame", "40.96×",
    "0.6913", "0.6991", "0.6476", "0.3523",
    "121.443–122.759", "125.595–128.301", "8.098–8.185", "7.740–7.894",
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def text_of(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).replace("\u00a0", " ").strip()


def table_signature(table: ET.Element) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple(text_of(cell) for cell in row.findall("w:tc", NS))
        for row in table.findall("w:tr", NS)
    )


def source_validation(errors: list[str]) -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SECTIONS)
    visible = source.replace("`", "")
    if source.count(TITLE_CN) != 1 or source.count(TITLE_EN) != 1:
        errors.append("title identity/count mismatch")
    contribution_lines = re.findall(r"^.*主要贡献包括两点：.*$", source, re.M)
    if (
        len(contribution_lines) != 1
        or contribution_lines[0].count("1）") != 1
        or contribution_lines[0].count("2）") != 1
        or "3）" in contribution_lines[0]
    ):
        errors.append("contribution inventory is not exactly two")
    if len(re.findall(r"RQ1[，：]", source)) != 1 or len(re.findall(r"RQ2[，：]", source)) != 1:
        errors.append("RQ inventory is not exactly one formal RQ1 and one formal RQ2")

    figures = re.findall(r"^\*\*图(\d+)　", source, re.M)
    tables = re.findall(r"^\*\*表(\d+)　", source, re.M)
    equations = re.findall(r"\\\[(.*?)\\\]", source, re.S)
    if figures != ["1", "2", "3"]:
        errors.append(f"figure inventory mismatch: {figures}")
    if tables != ["1", "2", "3"]:
        errors.append(f"table inventory mismatch: {tables}")
    if len(equations) != 3:
        errors.append(f"display equation inventory mismatch: {len(equations)}")
    else:
        for token, equation in zip(("P=(R,F,M,E)", "B(P)", "T_{\\mathrm{E2E}}(P)"), equations):
            if token not in equation.replace("\n", ""):
                errors.append(f"display equation semantic token missing: {token}")

    for caption in CAPTIONS:
        if visible.count(caption) != 1:
            errors.append(f"caption authority mismatch: {caption}")
    for value in FROZEN_VALUES:
        if value not in visible:
            errors.append(f"frozen scientific token missing: {value}")

    required = (
        "输入数据路径", "P=(R,F,M,E)", "名义输入复制载荷",
        "路径级重构", "暂存策略级细化", "任务正确性保持",
        "路径描述项", "R,F,M", r"E\)保持不变",
        "不独立测量H2D、预处理或CUDA核函数时间",
        "未形成一致的尾延迟改善证据", "平均响应和尾延迟是不同评价维度",
        "MAXN_SUPER", "nvpmodel mode 2", "未调用jetson_clocks",
        "60帧", "1080帧", "5个独立进程", "15个进程", "5400个",
    )
    for token in required:
        if token not in visible:
            errors.append(f"required Phase 5.9C semantic token missing: {token}")

    forbidden = (
        "新数据路径理论", "新理论", "首次", "首创", "达到40.96×传输加速",
        "获得40.96×带宽", "证明pinned改善尾延迟",
        "T_{\\mathrm{E2E}}\n=\n\\sum", "表4　", "图4　",
        "显著的完整路径平均响应", "确认比较身份", "生命周期准入",
        "内部数值门限和缓冲区释放过程不进入公开方法描述",
    )
    for token in forbidden:
        if token in visible:
            errors.append(f"forbidden claim or retired inventory residue: {token}")

    citation_keys = re.findall(r"@([A-Za-z][A-Za-z0-9_.:-]*)", source)
    if len(set(citation_keys)) != 22:
        errors.append(f"expected 22 cited references, found {len(set(citation_keys))}")

    figure_svg = FIGURE_ASSETS[0].with_suffix(".svg").read_text(encoding="utf-8")
    for token in (
        "主机—设备边界", "P₀ / V0", "P₂ / V2R", "P₃ / V3R",
        "R = FP32 NCHW", "R = packed BGR uint8", "F = 主机", "F = 设备",
        "M = 无", "M = Pageable", "M = Pinned", "E = 单帧顺序",
        "路径级重构", "改变 R、F、M；E 保持不变", "暂存策略级细化",
    ):
        if token not in figure_svg:
            errors.append(f"Figure 1 model token missing: {token}")
    for token in ("std::vector", "cudaFreeHost", "enqueueV3", "output D2H", "2.24×"):
        if token in figure_svg:
            errors.append(f"Figure 1 implementation/result residue: {token}")


def load_docx(path: Path) -> tuple[list[str], tuple[tuple[tuple[str, ...], ...], ...], set[str]]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        root = ET.fromstring(archive.read("word/document.xml"))
        media = [archive.read(name) for name in archive.namelist() if name.startswith("word/media/")]
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no body")
    paragraphs = [text_of(node) for node in body.findall("w:p", NS)]
    drawings = root.findall(".//w:drawing", NS)
    tables = body.findall("w:tbl", NS)
    equations = [
        node for node in body.findall("w:p", NS)
        if (node.find("w:pPr/w:pStyle", NS) is not None
            and node.find("w:pPr/w:pStyle", NS).get(f"{{{W}}}val") == "HFUTEquation"
            and node.find(".//m:oMath", NS) is not None)
    ]
    if (len(drawings), len(tables), len(equations)) != (3, 3, 3):
        raise ValueError(
            f"inventory mismatch: figures={len(drawings)} tables={len(tables)} equations={len(equations)}"
        )
    expected_media = {sha256(path.read_bytes()) for path in FIGURE_ASSETS}
    actual_media = {sha256(payload) for payload in media}
    if actual_media != expected_media:
        raise ValueError("embedded figure payloads do not match Phase 5.9C F1/F2/F3 authorities")
    signatures = tuple(table_signature(table) for table in tables)
    if len(signatures[0]) != 7 or any(len(row) != 4 for row in signatures[0]):
        raise ValueError("T1 is not header plus six structural-variable rows by four columns")
    if len(signatures[1]) != 10 or any(len(row) != 2 for row in signatures[1]):
        raise ValueError("T2 protocol structure mismatch")
    if len(signatures[2]) != 4 or any(len(row) != 2 for row in signatures[2]):
        raise ValueError("T3 correctness structure mismatch")
    reference_count = sum(
        1 for node in body.findall("w:p", NS)
        if (node.find("w:pPr/w:pStyle", NS) is not None
            and node.find("w:pPr/w:pStyle", NS).get(f"{{{W}}}val") == "Bibliography")
    )
    if reference_count != 22:
        raise ValueError(f"expected 22 rendered references, found {reference_count}")
    return paragraphs, signatures, actual_media


def docx_validation(path: Path, errors: list[str]) -> tuple[list[str], tuple[tuple[tuple[str, ...], ...], ...], set[str]]:
    try:
        paragraphs, tables, media = load_docx(path)
    except (ValueError, zipfile.BadZipFile, KeyError) as exc:
        errors.append(f"{path.name}: {exc}")
        return [], tuple(), set()
    text = "\n".join(paragraphs) + "\n" + "\n".join(
        cell for table in tables for row in table for cell in row
    )
    if text.count(TITLE_CN) != 1 or text.count(TITLE_EN) != 1:
        errors.append(f"{path.name}: title mismatch")
    for caption in CAPTIONS:
        if text.count(caption) != 1:
            errors.append(f"{path.name}: rendered caption mismatch: {caption}")
    for value in FROZEN_VALUES:
        if value not in text:
            errors.append(f"{path.name}: frozen scientific token missing: {value}")
    return paragraphs, tables, media


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--compare-full", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    source_validation(errors)
    paragraphs, tables, media = docx_validation(args.docx, errors)
    if args.compare_full:
        full_paragraphs, full_tables, full_media = docx_validation(args.compare_full, errors)
        if tables != full_tables:
            errors.append("Full/Anonymous table parity failed")
        if media != full_media:
            errors.append("Full/Anonymous figure-media parity failed")
        identity = (
            "王凯伦", "王琦", "WANG Kailun", "WANG Qi", "合肥工业大学数学学院",
            "School of Mathematics, Hefei University of Technology",
        )
        scientific_full = [line for line in full_paragraphs if not any(token in line for token in identity)]
        if paragraphs != scientific_full:
            errors.append("Full/Anonymous scientific paragraph parity failed")
    if errors:
        print("PHASE59C_INTEGRATION=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE59C_INTEGRATION=PASS figures=3 tables=3 equations=3 rqs=2 contributions=2 references=22")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
