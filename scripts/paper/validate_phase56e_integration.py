#!/usr/bin/env python3
"""Validate the frozen Phase 5.6E manuscript-integration contract."""

from __future__ import annotations

import argparse
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

OLD_VISIBLE_TEXT = (
    "V0、V2R和V3R数据路径示意",
    "端到端执行概念组成与受控干预范围",
    "V0、V2R和V3R平均帧率比较",
    "V0、V2R和V3R平均及尾延迟比较",
    "V0与V2R任务级正确性验证结果",
    "运行级稳定性与尾延迟",
    "仍缺少足够明确的受控工程证据",
    "L4T 36.4.3",
)
RUNTIME_OVERREACH = (
    "no throttling",
    "fixed clocks",
    "stable frequency",
    "stable thermal state",
    "无降频",
    "固定时钟",
    "稳定频率",
    "稳定热状态",
)
REQUIRED_RESULTS = (
    "2.24×",
    "55.45%",
    "+4.07%",
    "−4.03%",
    "+0.15%",
    "−0.12%",
    "MIXED",
)


def paragraph_text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).replace("\u00a0", " ").strip()


def load_docx(path: Path) -> tuple[ET.Element, list[str], list[str]]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        root = ET.fromstring(archive.read("word/document.xml"))
        media = [name for name in archive.namelist() if name.startswith("word/media/")]
    paragraphs = [paragraph_text(node) for node in root.findall(".//w:body/w:p", NS)]
    return root, paragraphs, media


def validate_source(errors: list[str]) -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SECTIONS)
    visible_source = source.replace("`", "")

    for value in OLD_VISIBLE_TEXT:
        if value in visible_source:
            errors.append(f"stale active-manuscript text remains: {value}")
    if "4.4 运行级分布与尾延迟" not in source:
        errors.append("Section 4.4 title is not the frozen final title")
    if source.count("主要贡献包括两点") != 1 or "3）" in source:
        errors.append("contribution inventory is not exactly two")

    figure_captions = re.findall(r"^\*\*图([1-4])　", source, re.M)
    table_captions = re.findall(r"^\*\*表([1-4])　", source, re.M)
    if figure_captions != ["1", "2", "3", "4"]:
        errors.append(f"figure-caption inventory mismatch: {figure_captions}")
    if table_captions != ["1", "2", "3", "4"]:
        errors.append(f"table-caption inventory mismatch: {table_captions}")

    equations = re.findall(r"\\\[(.*?)\\\]", source, re.S)
    equation_contract = (
        "T_{\\mathrm{E2E}}",
        "f_i=",
        "\\mu_f=",
        "h=1+(n-1)p",
        "Q_p=",
    )
    if len(equations) != 5 or any(token not in equations[index] for index, token in enumerate(equation_contract)):
        errors.append("five-equation inventory/order contract failed")

    for value in REQUIRED_RESULTS:
        if value not in visible_source:
            errors.append(f"frozen result missing: {value}")
    if "名义输入复制载荷比为40.96×" not in visible_source:
        errors.append("40.96× is not explicitly governed as nominal input-copy payload")
    if "TensorRT INT8混合精度Engine" not in visible_source:
        errors.append("TensorRT INT8 mixed-precision wording is missing")
    for value in (
        "强制cache miss",
        "生成并归档cache",
        "未将既有cache复用为正式构建输入",
        "MAXN_SUPER",
        "nvpmodel mode 2",
        "未调用jetson_clocks",
        "时钟频率没有独立归档",
        "非连续的前后观察",
    ):
        if value not in visible_source:
            errors.append(f"frozen calibration/runtime qualifier missing: {value}")
    for value in ("calibration cache used", "pre-existing cache reused") + RUNTIME_OVERREACH:
        if value.casefold() in visible_source.casefold():
            errors.append(f"ambiguous or overreaching runtime wording present: {value}")


def validate_docx(path: Path, errors: list[str]) -> tuple[list[str], list[tuple[tuple[str, ...], ...]]]:
    root, paragraphs, media = load_docx(path)
    text = "\n".join(paragraphs)
    figures = root.findall(".//w:drawing", NS)
    tables = root.findall(".//w:body/w:tbl", NS)
    equations = root.findall(".//m:oMathPara", NS)
    if (len(figures), len(tables), len(equations)) != (4, 4, 5):
        errors.append(
            f"{path.name}: inventory is figures={len(figures)} tables={len(tables)} equations={len(equations)}"
        )
    payloads = [Path(name).suffix.lower() for name in media]
    if payloads != [".png"] * 4:
        errors.append(f"{path.name}: DOCX figure payloads are not four PNG fallbacks: {payloads}")
    for prefix in ("图1　", "图2　", "图3　", "图4　", "表1　", "表2　", "表3　", "表4　"):
        if sum(value.startswith(prefix) for value in paragraphs) != 1:
            errors.append(f"{path.name}: caption count mismatch for {prefix.strip()}")
    for value in OLD_VISIBLE_TEXT:
        if value in text:
            errors.append(f"{path.name}: stale rendered text remains: {value}")
    if "L4T R36.5" not in text or "L4T 36.4.3" in text:
        errors.append(f"{path.name}: Table 2 L4T R36.5 regression")
    if "V3R" not in "\n".join(paragraph_text(cell) for cell in tables[2].findall(".//w:tc", NS)):
        errors.append(f"{path.name}: V3R is absent from Table 3")
    t4_rows = tables[3].findall("w:tr", NS) if len(tables) == 4 else []
    if len(t4_rows) != 7 or any(len(row.findall("w:tc", NS)) != 8 for row in t4_rows):
        errors.append(f"{path.name}: Table 4 is not 6 works by 7 attributes")
    signatures = [
        tuple(tuple(paragraph_text(cell) for cell in row.findall("w:tc", NS)) for row in table.findall("w:tr", NS))
        for table in tables
    ]
    return paragraphs, signatures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--compare-full", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    validate_source(errors)
    paragraphs, tables = validate_docx(args.docx, errors)
    if args.compare_full:
        full_paragraphs, full_tables = validate_docx(args.compare_full, errors)
        if tables != full_tables:
            errors.append("Full/Anonymous table parity failed")
        identity = (
            "王凯伦", "王琦", "WANG Kailun", "WANG Qi",
            "合肥工业大学数学学院", "School of Mathematics, Hefei University of Technology",
        )
        scientific_full = [value for value in full_paragraphs if value and not any(token in value for token in identity)]
        if [value for value in paragraphs if value] != scientific_full:
            errors.append("Full/Anonymous visible scientific paragraph parity failed")

    if errors:
        print("verdict=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE56E_INTEGRATION_VALIDATION=PASS")
    print("figures=4 tables=4 display_equations=5 contributions=2")
    print("table2_l4t=R36.5 stale_l4t_36.4.3=NO table3_v3r=YES table4=6x7")
    print("tail=MIXED nominal_payload_ratio=40.96x docx_payloads=PNG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
