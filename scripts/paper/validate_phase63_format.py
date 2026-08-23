#!/usr/bin/env python3
"""Validate the active Phase 6.3 review-build and submission-gate contract."""

from __future__ import annotations

import argparse
import csv
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
FIGURE_MANIFEST = MANUSCRIPT / "figures/figure_manifest.csv"
EQUATION_MANIFEST = MANUSCRIPT / "equations/equation_manifest.csv"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "m": M, "wp": WP}

FIGURE_CAPTIONS = (
    "图1　输入数据路径抽象及层级受控比较。图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。",
    "图2　三条路径的端到端性能。(a) 为5个独立进程FPS的均值±样本标准差；(b)(c) 为每条路径合并5400个延迟样本的均值、P95和P99。",
    "图3　运行级分布与尾延迟。各点为独立进程级描述量，横向偏移仅用于区分，不表示运行配对。",
)
TABLE_CAPTIONS = (
    "表1　三条输入数据路径的结构描述与派生量。名义输入复制载荷由跨边界表示推导，非实测流量。",
    "表2　平台、模型与统一基准协议。",
    "表3　三条路径在冻结工作负载和统一评价程序下的任务级正确性。",
)


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def attr(node: ET.Element | None, local: str, namespace: str = W) -> str | None:
    return None if node is None else node.get(qn(namespace, local))


def text_of(node: ET.Element) -> str:
    text_tags = {qn(W, "t"), qn(M, "t")}
    return "".join(item.text or "" for item in node.iter() if item.tag in text_tags).strip()


def load_manifest_errors() -> list[str]:
    errors: list[str] = []
    with FIGURE_MANIFEST.open(encoding="utf-8", newline="") as handle:
        figures = list(csv.DictReader(handle))
    required = {
        "scientific_master", "review_payload", "submission_object",
        "scientific_status", "submission_status",
    }
    if len(figures) != 3 or not required.issubset(figures[0] if figures else {}):
        errors.append("figure lifecycle manifest schema/inventory mismatch")
    for row in figures:
        if row["scientific_status"] != "FROZEN":
            errors.append(f"{row['figure_id']}: scientific status is not FROZEN")
        if row["submission_status"] != "OPEN":
            errors.append(f"{row['figure_id']}: submission status must remain OPEN in Phase 6.3")
        if not row["review_payload"].endswith(".png"):
            errors.append(f"{row['figure_id']}: review payload is not the DOCX-compatible PNG")
        expected = "VISIO:" if row["figure_id"] == "F1" else "ORIGIN:"
        if not row["submission_object"].startswith(expected):
            errors.append(f"{row['figure_id']}: submission object type mismatch")
        if row["width_mode"] != ("FULL_WIDTH" if row["figure_id"] == "F1" else "SINGLE_COLUMN"):
            errors.append(f"{row['figure_id']}: width lifecycle/layout mismatch")

    with EQUATION_MANIFEST.open(encoding="utf-8", newline="") as handle:
        equations = list(csv.DictReader(handle))
    if [row["equation_id"] for row in equations] != ["E1", "E2", "E3"]:
        errors.append("equation manifest inventory/order mismatch")
    if [row["word_equation_number"] for row in equations] != ["1", "2", "3"]:
        errors.append("equation manifest visible-number sequence mismatch")
    if any(row["mathtype_required"] != "DEFERRED_FINAL_MATHTYPE" for row in equations):
        errors.append("MathType must remain explicitly deferred for final submission adaptation")
    return errors


def section_values(section: ET.Element) -> tuple[str | None, str | None]:
    return (
        attr(section.find("w:cols", NS), "num"),
        attr(section.find("w:type", NS), "val"),
    )


def validate_docx(path: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    details: dict[str, object] = {}
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            return [f"ZIP CRC failure: {bad}"], details
        document = ET.fromstring(archive.read("word/document.xml"))
        styles = ET.fromstring(archive.read("word/styles.xml"))
    body = document.find("w:body", NS)
    if body is None:
        return ["document.xml has no body"], details
    children = list(body)
    paragraphs = body.findall("w:p", NS)
    text = "\n".join(text_of(node) for node in document.findall(".//w:p", NS))

    final_section = body.find("w:sectPr", NS)
    if final_section is None:
        errors.append("document has no final section properties")
    else:
        page_size = final_section.find("w:pgSz", NS)
        margins = final_section.find("w:pgMar", NS)
        if (attr(page_size, "w"), attr(page_size, "h")) != ("11906", "16838"):
            errors.append("page size is not the preserved A4 contract")
        if margins is None:
            errors.append("page margins are missing")
        if attr(final_section.find("w:cols", NS), "num") != "2":
            errors.append("final manuscript body is not double-column")

    drawing_widths: list[int] = []
    for index, caption_text in enumerate(FIGURE_CAPTIONS):
        matches = [node for node in paragraphs if text_of(node) == caption_text]
        if len(matches) != 1:
            errors.append(f"Figure {index + 1} caption count mismatch")
            continue
        caption = matches[0]
        position = children.index(caption)
        if position == 0 or children[position - 1].find(".//w:drawing", NS) is None:
            errors.append(f"Figure {index + 1} caption is not immediately below its drawing")
            continue
        drawing = children[position - 1]
        extent = drawing.find(".//wp:extent", NS)
        width = int(extent.get("cx", "0") if extent is not None else 0)
        drawing_widths.append(width)
        expected = 5_760_000 if index == 0 else 2_700_000
        if abs(width - expected) > 2:
            errors.append(f"Figure {index + 1} width is {width}, expected {expected} EMU")
        section = caption.find("w:pPr/w:sectPr", NS)
        if index == 0:
            if section is None or section_values(section) != ("1", "nextPage"):
                errors.append("Figure 1 is not in a next-page one-column section")
            if position < 2:
                errors.append("Figure 1 has no governed preceding callout")
            else:
                callout_section = children[position - 2].find("w:pPr/w:sectPr", NS)
                if callout_section is None or section_values(callout_section)[0] != "2":
                    errors.append("Figure 1 callout does not close the preceding two-column section")
        elif section is not None:
            errors.append(f"Figure {index + 1} incorrectly creates a full-width section")
    details["figure_widths_emu"] = drawing_widths

    for caption_text in TABLE_CAPTIONS:
        matches = [node for node in paragraphs if text_of(node) == caption_text]
        if len(matches) != 1:
            errors.append(f"table caption count mismatch: {caption_text}")
            continue
        position = children.index(matches[0])
        following = next((node for node in children[position + 1:] if node.tag != qn(W, "p") or text_of(node)), None)
        if following is None or following.tag != qn(W, "tbl"):
            errors.append(f"table caption is not above its native Word table: {caption_text}")

    tables = body.findall("w:tbl", NS)
    if len(tables) != 3:
        errors.append(f"native manuscript table count is {len(tables)}, expected 3")
    else:
        t1_text = "\n".join(text_of(cell) for cell in tables[0].findall(".//w:tc", NS))
        if "名义输入复制载荷 B(P)/(MB/frame)" not in t1_text:
            errors.append("Table 1 quantity/unit header formulation is missing")
        if "4.9152 MB/frame" in t1_text or "0.1200 MB/frame" in t1_text:
            errors.append("Table 1 repeats MB/frame in numeric cells")
        for run in tables[0].findall(".//m:r", NS):
            if attr(run.find("w:rPr/w:sz", NS), "val") != "15":
                errors.append("Table 1 inline math is not coordinated to six-size table text")
                break
        t3_rows = tables[2].findall("w:tr", NS)
        for row in t3_rows[:-1]:
            for paragraph in row.findall(".//w:p", NS):
                if paragraph.find("w:pPr/w:keepNext", NS) is None:
                    errors.append("Table 3 keep-with-next pagination chain is incomplete")
                    break

    equations = [
        node for node in paragraphs
        if attr(node.find("w:pPr/w:pStyle", NS), "val") == "HFUTEquation"
    ]
    if len(equations) != 3:
        errors.append(f"visible equation paragraph count is {len(equations)}, expected 3")
    for number, paragraph in enumerate(equations, start=1):
        if len(paragraph.findall("m:oMath", NS)) != 1:
            errors.append(f"Equation {number} does not contain exactly one OMML object")
        if not text_of(paragraph).endswith(f"（{number}）"):
            errors.append(f"Equation {number} visible number mismatch: {text_of(paragraph)!r}")
        tabs = paragraph.findall("w:pPr/w:tabs/w:tab", NS)
        if [(attr(tab, "val"), attr(tab, "pos")) for tab in tabs] != [
            ("center", "2205"), ("right", "4410")
        ]:
            errors.append(f"Equation {number} center/right tab layout mismatch")
        spacing = paragraph.find("w:pPr/w:spacing", NS)
        if spacing is not None and (
            attr(spacing, "before"), attr(spacing, "after"),
            attr(spacing, "line"), attr(spacing, "lineRule")
        ) != ("0", "0", "320", "atLeast"):
            errors.append(f"Equation {number} spacing override mismatch")
    for number in range(1, 4):
        if f"式（{number}）" not in text:
            errors.append(f"body reference 式（{number}） is missing")

    style_map = {attr(node, "styleId"): node for node in styles.findall("w:style", NS)}
    for style_id in ("HFUTReferenceEntry", "Bibliography"):
        style = style_map.get(style_id)
        if style is None or attr(style.find("w:pPr/w:jc", NS), "val") != "both":
            errors.append(f"{style_id} is not justified")

    details["equation_numbers"] = [text_of(node) for node in equations]
    details["table_count"] = len(tables)
    details["a4"] = not any("A4" in error for error in errors)
    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--compare-full", type=Path)
    args = parser.parse_args()
    errors = load_manifest_errors()
    docx_errors, details = validate_docx(args.docx)
    errors.extend(f"{args.docx.name}: {error}" for error in docx_errors)
    if args.compare_full:
        full_errors, full_details = validate_docx(args.compare_full)
        errors.extend(f"{args.compare_full.name}: {error}" for error in full_errors)
        if details.get("figure_widths_emu") != full_details.get("figure_widths_emu"):
            errors.append("Full/Anonymous figure layout parity mismatch")
        if details.get("equation_numbers") != full_details.get("equation_numbers"):
            errors.append("Full/Anonymous equation-number parity mismatch")
    if errors:
        for error in errors:
            print(f"PHASE63_FORMAT_ERROR: {error}")
        print("MANUSCRIPT_BUILD_FAIL")
        print("HFUT_SUBMISSION_NOT_READY")
        return 1
    print(f"MANUSCRIPT_BUILD_PASS docx={args.docx}")
    print("EQUATION_NUMBERING_COMPLETE E1=（1） E2=（2） E3=（3）")
    print("FIGURE_LIFECYCLE_VALID scientific=FROZEN review=PNG submission=OPEN")
    print("HFUT_SUBMISSION_NOT_READY VISIO=OPEN ORIGIN=OPEN MATHTYPE=OPEN WORD_DESKTOP_QA=OPEN ANONYMOUS_QA=OPEN DOCUMENT_INSPECTOR=OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
