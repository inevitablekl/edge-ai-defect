#!/usr/bin/env python3
"""Validate the Phase 4.5 Full-manuscript DOCX structure and content contract."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "a": A, "r": R}

T1_TITLE = "表1　平台、模型、数据集和统一运行协议"
T2_TITLE = "表2　V0与V2R任务级正确性验证结果"
MARKER = "FULL_BODY_SECTION_START"


def attr(node: ET.Element | None, local: str, namespace: str = W) -> str | None:
    return node.get(f"{{{namespace}}}{local}") if node is not None else None


def text_of(node: ET.Element) -> str:
    return "".join(child.text or "" for child in node.findall(".//w:t", NS)).strip()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(path: Path) -> tuple[bool, list[str], dict[str, object]]:
    errors: list[str] = []
    details: dict[str, object] = {}
    if not path.is_file():
        return False, [f"missing DOCX: {path}"], details

    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                fail(errors, f"ZIP CRC failure: {bad}")
            names = set(archive.namelist())
            required = {"[Content_Types].xml", "word/document.xml", "word/styles.xml", "word/_rels/document.xml.rels"}
            missing = sorted(required - names)
            if missing:
                fail(errors, f"missing OOXML parts: {missing}")
            parts = {name: archive.read(name) for name in names}
    except (OSError, zipfile.BadZipFile) as exc:
        return False, [f"invalid DOCX package: {exc}"], details

    parsed: dict[str, ET.Element] = {}
    for name, payload in parts.items():
        if not name.endswith((".xml", ".rels")):
            continue
        try:
            parsed[name] = ET.fromstring(payload)
        except ET.ParseError as exc:
            fail(errors, f"XML parse failure in {name}: {exc}")

    document = parsed.get("word/document.xml")
    relationships = parsed.get("word/_rels/document.xml.rels")
    if document is None:
        return False, errors, details
    body = document.find("w:body", NS)
    if body is None:
        fail(errors, "document has no w:body")
        return False, errors, details

    body_paragraphs = body.findall("w:p", NS)
    body_text = "\n".join(text_of(node) for node in body_paragraphs)
    all_text = "\n".join(text_of(node) for node in document.findall(".//w:p", NS))
    details["body_text"] = body_text

    required_text = {
        "CN title": "Jetson端工业缺陷检测的INT8推理数据路径优化",
        "EN title": "Data-Path Optimization for INT8 Inference in Jetson-Based Industrial Defect Detection",
        "CN keywords": "Jetson；工业缺陷检测；INT8推理；CUDA预处理；数据路径优化",
        "EN keywords": "Jetson; industrial defect detection; INT8 inference; CUDA preprocessing; data-path optimization",
        "authors CN": "王凯伦，王琦",
        "authors EN": "WANG Kailun, WANG Qi",
        "affiliation CN": "合肥工业大学数学学院，安徽 合肥 230601",
        "affiliation EN": "School of Mathematics, Hefei University of Technology, Hefei 230601, China",
        "CLC": "TP391.41",
        "corresponding CN": "通信作者：王琦",
        "corresponding EN": "Corresponding author: WANG Qi",
    }
    for label, value in required_text.items():
        if value not in all_text:
            fail(errors, f"missing {label}: {value}")

    forbidden = ("PENDING", "TBD", "UNKNOWN", "example@example.com", "[NO_SUBTITLE_PLANNED]", "NONE")
    for value in forbidden:
        if value in all_text:
            fail(errors, f"forbidden publication placeholder/content present: {value}")
    if re.search(r"@[A-Za-z][A-Za-z0-9_.:-]*", all_text):
        fail(errors, "unresolved citation key remains in DOCX text")

    if body_text.count("Jetson端工业缺陷检测的INT8推理数据路径优化") != 1:
        fail(errors, "CN title is duplicated or missing")
    if body_text.count("Data-Path Optimization for INT8 Inference in Jetson-Based Industrial Defect Detection") != 1:
        fail(errors, "EN title is duplicated or missing")
    if body_text.count("参考文献") != 1:
        fail(errors, "reference heading is duplicated or missing")

    drawings = document.findall(".//w:drawing", NS)
    details["figure_count"] = len(drawings)
    if len(drawings) != 3:
        fail(errors, f"expected three figure drawings, found {len(drawings)}")
    if relationships is not None:
        image_relationships = {
            rel.get("Id")
            for rel in relationships
            if rel.get("Type", "").endswith("/image")
        }
        used_relationships = {
            node.get(f"{{{R}}}embed")
            for node in document.findall(".//a:blip", NS)
        }
        if len(used_relationships & image_relationships) != 3:
            fail(errors, "three embedded figure image relationships are not all used")
    for caption in ("图1　", "图2　", "图3　"):
        if sum(text.startswith(caption) for text in (text_of(p) for p in body_paragraphs)) != 1:
            fail(errors, f"missing or duplicated figure caption: {caption}")

    tables = body.findall("w:tbl", NS)
    details["table_count"] = len(tables)
    if len(tables) != 2:
        fail(errors, f"expected two manuscript tables, found {len(tables)}")
    else:
        t1, t2 = tables
        t1_rows = t1.findall("w:tr", NS)
        t2_rows = t2.findall("w:tr", NS)
        details["table1_rows"] = len(t1_rows) - 1
        details["table2_rows"] = len(t2_rows) - 1
        if len(t1_rows) != 18 or any(len(row.findall("w:tc", NS)) != 2 for row in t1_rows):
            fail(errors, "Table 1 is not 17 data rows by 2 columns")
        if len(t2_rows) != 5 or any(len(row.findall("w:tc", NS)) != 6 for row in t2_rows):
            fail(errors, "Table 2 is not 4 data rows by 6 columns")

        t1_values = "\n".join(text_of(cell) for row in t1_rows for cell in row.findall("w:tc", NS))
        for value in (
            "NVIDIA Jetson Orin Nano Super", "R36.5", "12.6.11，runtime 12.6.68",
            "10.3.0.30", "4.5.4", "YOLOv8n", "冻结 TensorRT INT8 混合精度 Engine",
            "640×640", "NEU-DET，去重后的 split-v2", "固定 180 幅图像", "V0、V2R、V3R",
            "60 帧", "1080 帧，即 180 幅图像完整回放 6 个周期",
            "每种路径 5 次，共 15 个独立进程", "内部诊断计时", "Profiling",
        ):
            if value not in t1_values:
                fail(errors, f"Table 1 missing frozen value: {value}")

        t2_values = "\n".join(text_of(cell) for row in t2_rows for cell in row.findall("w:tc", NS))
        for value in ("Precision", "Recall", "mAP50", "mAP50-95", "0.6913", "0.6991", "0.6476", "0.3523", "0.010", "0.005"):
            if value not in t2_values:
                fail(errors, f"Table 2 missing frozen value: {value}")
        if "V3R" in t2_values:
            fail(errors, "V3R appears in Table 2")

        for table in tables:
            borders = table.find("w:tblPr/w:tblBorders", NS)
            expected = {"top": "single", "left": "nil", "bottom": "single", "right": "nil", "insideH": "nil", "insideV": "nil"}
            actual = {node.tag.rsplit("}", 1)[-1]: attr(node, "val") for node in borders} if borders is not None else {}
            if actual != expected:
                fail(errors, f"table border contract mismatch: {actual}")
            if attr(borders.find("w:top", NS), "sz") != "8" or attr(borders.find("w:bottom", NS), "sz") != "8":
                fail(errors, "table top/bottom rule width is not 1 pt")
            rows = table.findall("w:tr", NS)
            for cell in rows[0].findall("w:tc", NS):
                border = cell.find("w:tcPr/w:tcBorders/w:bottom", NS)
                if attr(border, "val") != "single" or attr(border, "sz") != "4":
                    fail(errors, "table header rule is not 0.5 pt")
            for row in rows[1:]:
                for cell in row.findall("w:tc", NS):
                    border = cell.find("w:tcPr/w:tcBorders", NS)
                    if attr(border.find("w:top", NS), "val") != "nil" or attr(border.find("w:bottom", NS), "val") != "nil":
                        fail(errors, "internal body gridline is present")

    reference_heading_index = next((index for index, p in enumerate(body_paragraphs) if text_of(p) == "参考文献"), None)
    rendered_references = 0
    if reference_heading_index is not None:
        for paragraph in body_paragraphs[reference_heading_index + 1:]:
            style = paragraph.find("w:pPr/w:pStyle", NS)
            if attr(style, "val") == "Bibliography":
                rendered_references += 1
    details["rendered_references"] = rendered_references
    bib_path = Path(__file__).resolve().parents[2] / "docs/paper/manuscript/references/references.bib"
    source_references = len(re.findall(r"^\s*@(?!(?:comment|preamble|string)\b)[A-Za-z]+\s*\{[^,]+,", bib_path.read_text(encoding="utf-8"), re.I | re.M))
    details["source_references"] = source_references
    if rendered_references == 0:
        fail(errors, "no rendered bibliography entries found")
    if source_references != 15:
        fail(errors, f"expected 15 bibliography source entries, found {source_references}")

    for value in ("2.236671×", "55.4519%", "4.0738%", "4.0349%", "0.1514%", "0.1184%"):
        if value not in all_text:
            fail(errors, f"scientific freeze value missing: {value}")
    if "主要贡献包括两点" not in all_text or "1）" not in all_text or "2）" not in all_text:
        fail(errors, "contribution count of two is not preserved")
    for value in ("V4", "Attempt 2", "cross-stage acceleration multiplication", "Gate D"):
        if value in all_text:
            fail(errors, f"forbidden scientific restoration/claim present: {value}")

    section_columns = [attr(node, "num") for node in document.findall(".//w:sectPr/w:cols", NS)]
    details["section_columns"] = section_columns
    if "1" not in section_columns or "2" not in section_columns:
        fail(errors, f"expected front-matter/body column sections, found {section_columns}")
    if MARKER in all_text:
        fail(errors, "section boundary marker remains in publication DOCX")

    return not errors, errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    ok, errors, details = validate(args.docx)
    print(f"docx={args.docx}")
    for key, value in details.items():
        if key != "body_text":
            print(f"{key}={value}")
    if ok:
        print("verdict=PASS")
        return 0
    print("verdict=FAIL")
    for error in errors:
        print(f"ERROR: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
