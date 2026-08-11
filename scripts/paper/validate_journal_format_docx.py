#!/usr/bin/env python3
"""Validate the narrow Phase 4.8 journal-format contract on real manuscripts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx"
MANIFEST = ROOT / "docs/paper/manuscript/figures/figure_manifest.csv"
REFERENCE_SHA256 = "416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7"
BIOGRAPHY = "王凯伦（1999—），男，山东潍坊人，工学学士，硕士研究生，主要研究方向为端侧人工智能推理部署与优化。"
TITLE_CN = "Jetson端工业缺陷检测的INT8推理数据路径优化"
TITLE_EN = "Data-Path Optimization for INT8 Inference in Jetson-Based Industrial Defect Detection"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "a": A, "wp": WP, "r": R}
Q = lambda local: f"{{{W}}}{local}"


def text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).strip()


def attr(node: ET.Element | None, name: str, namespace: str = W) -> str | None:
    return None if node is None else node.get(f"{{{namespace}}}{name}")


def style_id(paragraph: ET.Element) -> str:
    return attr(paragraph.find("w:pPr/w:pStyle", NS), "val") or ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(payload: bytes) -> tuple[int, int]:
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("embedded figure is not PNG")
    return struct.unpack(">II", payload[16:24])


def load(path: Path) -> tuple[dict[str, bytes], dict[str, ET.Element]]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        parts = {name: archive.read(name) for name in archive.namelist()}
    parsed = {
        name: ET.fromstring(payload) for name, payload in parts.items()
        if name.endswith((".xml", ".rels"))
    }
    return parts, parsed


def manifest_captions() -> list[str]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row["word_caption"] for row in rows]


def style_contract(styles: ET.Element, errors: list[str]) -> None:
    expected = {
        "HFUTTitleCN": ("黑体", "Times New Roman", "30", "360"),
        "HFUTTitleEN": ("Times New Roman", "Times New Roman", "28", "336"),
        "HFUTBody": ("宋体", "Times New Roman", "21", "320"),
        "HFUTHeading1": ("黑体", "Times New Roman", "28", "320"),
        "HFUTHeading2": ("黑体", "Times New Roman", "21", "320"),
        "HFUTHeading3": ("楷体", "Times New Roman", "21", "320"),
        "HFUTAuthorBiography": ("宋体", "Times New Roman", "15", "280"),
        "HFUTFigureCaption": ("黑体", "Times New Roman", "15", "320"),
        "HFUTTableContent": ("宋体", "Times New Roman", "15", "240"),
        "HFUTReferenceEntry": ("宋体", "Times New Roman", "15", "280"),
        "Bibliography": ("宋体", "Times New Roman", "15", "280"),
    }
    found = {node.get(Q("styleId")): node for node in styles.findall("w:style", NS)}
    for sid, (east, latin, size, line) in expected.items():
        node = found.get(sid)
        if node is None:
            errors.append(f"missing style {sid}")
            continue
        fonts = node.find("w:rPr/w:rFonts", NS)
        spacing = node.find("w:pPr/w:spacing", NS)
        if (attr(fonts, "eastAsia"), attr(fonts, "ascii"), attr(node.find("w:rPr/w:sz", NS), "val"), attr(spacing, "line")) != (east, latin, size, line):
            errors.append(f"style contract mismatch: {sid}")
        if attr(spacing, "lineRule") != "exact":
            errors.append(f"style line rule is not exact: {sid}")


def validate_variant(path: Path, variant: str) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    out: dict[str, object] = {}
    parts, parsed = load(path)
    document = parsed["word/document.xml"]
    body = document.find("w:body", NS)
    assert body is not None
    paragraphs = body.findall("w:p", NS)
    body_text = "\n".join(text(p) for p in paragraphs)
    package_text = "\n".join(payload.decode("utf-8", "ignore") for name, payload in parts.items() if name.endswith((".xml", ".rels")))
    styles = parsed["word/styles.xml"]
    style_contract(styles, errors)

    sections = document.findall(".//w:sectPr", NS)
    section_columns = [attr(node.find("w:cols", NS), "num") for node in sections]
    out["section_columns"] = section_columns
    if section_columns != ["1", "2", "1", "2", "1", "2", "1", "2", "1", "2"]:
        errors.append(f"section transition mismatch: {section_columns}")
    for section in sections:
        size, margins, cols = section.find("w:pgSz", NS), section.find("w:pgMar", NS), section.find("w:cols", NS)
        actual = (attr(size, "w"), attr(size, "h"), attr(margins, "top"), attr(margins, "right"), attr(margins, "bottom"), attr(margins, "left"), attr(margins, "gutter"), attr(cols, "space"))
        if actual != ("11906", "16838", "1361", "1304", "1134", "1304", "0", "425"):
            errors.append(f"page geometry mismatch: {actual}")
        if section.find("w:pgNumType", NS) is not None and attr(section.find("w:pgNumType", NS), "start"):
            errors.append("page numbering restart present")
    if not sections or sections[0].find("w:titlePg", NS) is None:
        errors.append("first section lacks titlePg")

    rels = parsed["word/_rels/document.xml.rels"]
    footer_targets = {rel.get("Id"): "word/" + rel.get("Target", "") for rel in rels if rel.get("Type", "").endswith("/footer")}
    first_ref = next((node for node in sections[0].findall("w:footerReference", NS) if attr(node, "type") == "first"), None)
    default_ref = next((node for node in sections[0].findall("w:footerReference", NS) if attr(node, "type") == "default"), None)
    first_name = footer_targets.get(attr(first_ref, "id", R) or "", "")
    default_name = footer_targets.get(attr(default_ref, "id", R) or "", "")
    if first_name not in parsed or default_name not in parsed:
        errors.append("first/default footer relationship missing")
        footer_roots = []
    else:
        footer_roots = [parsed[first_name], parsed[default_name]]
    page_counts = [sum(1 for node in root.findall(".//w:fldSimple", NS) if "PAGE" in (attr(node, "instr") or "")) for root in footer_roots]
    if page_counts != [1, 1]:
        errors.append(f"PAGE field contract mismatch: {page_counts}")
    footer_text = "\n".join(text(root) for root in footer_roots)
    body_bio = body_text.count(BIOGRAPHY)
    package_bio = package_text.count(BIOGRAPHY)
    if variant == "full":
        if body_bio != 0 or package_bio != 1 or not footer_roots or text(footer_roots[0]).count(BIOGRAPHY) != 1:
            errors.append("Full first-page biography contract failed")
        if not footer_roots or "HFUTAuthorBiography" not in [style_id(p) for p in footer_roots[0].findall("w:p", NS)]:
            errors.append("Full biography style missing in first footer")
    elif body_bio or package_bio or BIOGRAPHY in footer_text:
        errors.append("Anonymous biography identity remains")

    title_paras = {style_id(p): text(p) for p in paragraphs if style_id(p) in {"HFUTTitleCN", "HFUTTitleEN"}}
    if title_paras != {"HFUTTitleCN": TITLE_CN, "HFUTTitleEN": TITLE_EN}:
        errors.append("title text/style contract failed")
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", TITLE_CN))
    out["title_chinese_chars"] = chinese_chars
    if chinese_chars > 20:
        errors.append("Chinese title exceeds safe 20-character limit")
    counts = {sid: sum(style_id(p) == sid for p in paragraphs) for sid in (
        "HFUTAbstractLabelCN", "HFUTAbstractBodyCN", "HFUTKeywordsLabelCN", "HFUTKeywordsBodyCN",
        "HFUTClassification", "HFUTAbstractLabelEN", "HFUTAbstractBodyEN", "HFUTKeywordsLabelEN", "HFUTKeywordsBodyEN")}
    if any(value != 1 for value in counts.values()):
        errors.append(f"front-matter semantic style usage mismatch: {counts}")
    cn_abstract = next((text(p) for p in paragraphs if style_id(p) == "HFUTAbstractBodyCN"), "")
    cn_keywords = next((text(p) for p in paragraphs if style_id(p) == "HFUTKeywordsBodyCN"), "")
    en_keywords = next((text(p) for p in paragraphs if style_id(p) == "HFUTKeywordsBodyEN"), "")
    out["cn_abstract_chinese_chars"] = len(re.findall(r"[\u4e00-\u9fff]", cn_abstract))
    out["cn_keywords"] = len([item for item in re.split(r"[;；]", cn_keywords) if item.strip()])
    out["en_keywords"] = len([item for item in en_keywords.split(";") if item.strip()])

    reference_headings = [p for p in paragraphs if text(p) == "参考文献"]
    if len(reference_headings) != 1 or style_id(reference_headings[0]) != "HFUTReferenceHeading" or reference_headings[0].find("w:pPr/w:numPr", NS) is not None:
        errors.append("unnumbered reference heading contract failed")
    if re.search(r"(?:^|\n)\s*\d+(?:\.\d+)*\s+参考文献", body_text):
        errors.append("visible numbered reference heading present")

    captions = manifest_captions()
    for caption in captions:
        if body_text.count(caption) != 1:
            errors.append(f"accepted figure caption missing/duplicated: {caption}")
    drawing_paragraphs = [
        paragraph for paragraph in body.findall("w:p", NS)
        if paragraph.find(".//w:drawing", NS) is not None
    ]
    drawings = document.findall(".//w:drawing", NS)
    if len(drawings) != 4:
        errors.append(f"expected four drawings, found {len(drawings)}")
    inline_count = sum(len(paragraph.findall(".//wp:inline", NS)) for paragraph in drawing_paragraphs)
    anchor_count = sum(len(paragraph.findall(".//wp:anchor", NS)) for paragraph in drawing_paragraphs)
    out["drawing_paragraphs"] = len(drawing_paragraphs)
    out["wp_inline"] = inline_count
    out["wp_anchor"] = anchor_count
    if len(drawing_paragraphs) != 4 or inline_count != 4 or anchor_count != 0:
        errors.append(
            f"publication drawing representation mismatch: paragraphs={len(drawing_paragraphs)} "
            f"inline={inline_count} anchor={anchor_count}"
        )
    for index, paragraph in enumerate(drawing_paragraphs, start=1):
        spacing = paragraph.find("w:pPr/w:spacing", NS)
        indent = paragraph.find("w:pPr/w:ind", NS)
        alignment = paragraph.find("w:pPr/w:jc", NS)
        if spacing is None or attr(spacing, "lineRule") == "exact":
            errors.append(f"FIGURE_INLINE_EXACT_LINE_SPACING_FORBIDDEN: F{index}")
        if (
            attr(spacing, "before"), attr(spacing, "after"),
            attr(spacing, "line"), attr(spacing, "lineRule")
        ) != ("0", "0", "320", "atLeast"):
            errors.append(f"figure paragraph spacing contract mismatch: F{index}")
        if attr(indent, "firstLine") != "0":
            errors.append(f"figure paragraph first-line indent is not zero: F{index}")
        if attr(alignment, "val") != "center":
            errors.append(f"figure paragraph alignment is not centered: F{index}")
    image_rels = {rel.get("Id"): rel.get("Target") for rel in rels if rel.get("Type", "").endswith("/image")}
    figures = []
    for drawing in drawings:
        extent = drawing.find(".//wp:extent", NS)
        blip = drawing.find(".//a:blip", NS)
        target = image_rels.get(attr(blip, "embed", R) or "", "")
        payload = parts.get("word/" + target, b"")
        pixels = png_size(payload)
        figures.append({"target": target, "cx": int(extent.get("cx", "0")), "cy": int(extent.get("cy", "0")), "pixels": pixels})
    out["figures"] = figures
    expected_widths = [5760000, 5760000, 2700000, 5760000]
    if any(abs(item["cx"] - expected) > 1 for item, expected in zip(figures, expected_widths)):
        errors.append(f"figure width contract mismatch: {[item['cx'] for item in figures]}")

    tables = body.findall("w:tbl", NS)
    if len(tables) != 3 or [len(table.findall("w:tr", NS)) - 1 for table in tables] != [3, 17, 4]:
        errors.append("T1/T2/T3 row contract failed")
    for table in tables:
        borders = table.find("w:tblPr/w:tblBorders", NS)
        actual = {node.tag.rsplit("}", 1)[-1]: (attr(node, "val"), attr(node, "sz")) for node in borders} if borders is not None else {}
        if actual.get("top") != ("single", "8") or actual.get("bottom") != ("single", "8") or any(actual.get(edge, (None,))[0] != "nil" for edge in ("left", "right", "insideH", "insideV")):
            errors.append(f"three-line table outer border contract failed: {actual}")

    if any(token in package_text for token in ("FULL_BODY_SECTION_START", "TOOLCHAIN TEST")):
        errors.append("forbidden build marker present")
    if any(token in body_text for token in ("PENDING", "TBD", "UNKNOWN")):
        errors.append("visible publication placeholder present")
    out["formal_equations"] = len(document.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara"))
    out["page_fields"] = sum(page_counts)
    out["biography_package_count"] = package_bio
    return errors, out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", required=True, type=Path)
    parser.add_argument("--anonymous", required=True, type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    reference_hash = sha256(REFERENCE)
    if reference_hash != REFERENCE_SHA256:
        errors.append(f"reference DOCX hash mismatch: {reference_hash}")
    results = {}
    for variant, path in (("full", args.full), ("anonymous", args.anonymous)):
        current_errors, details = validate_variant(path, variant)
        errors.extend(f"{variant}: {message}" for message in current_errors)
        results[variant] = details
    print(f"reference_docx_sha256={reference_hash}")
    for variant, details in results.items():
        print(f"{variant}={details}")
    if errors:
        print("verdict=FAIL")
        for message in errors:
            print(f"ERROR: {message}")
        return 1
    print("FORMAL_EQUATION_REQUIREMENT=NOT_APPLICABLE_TO_CURRENT_MANUSCRIPT")
    print("STRUCTURAL_REFERENCE_TYPOGRAPHY_PASS")
    print("verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
