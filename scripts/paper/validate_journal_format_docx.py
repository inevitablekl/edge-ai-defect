#!/usr/bin/env python3
"""Validate the narrow Phase 4.8 journal-format contract on real manuscripts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from validate_word_heading_numbering_docx import audit_heading_numbering_roots


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx"
MANIFEST = ROOT / "docs/paper/manuscript/figures/figure_manifest.csv"
BIOGRAPHY = "王凯伦（1999—），男，山东潍坊人，工学学士，硕士研究生，主要研究方向为端侧人工智能推理部署与优化，通信作者，E-mail:2024180231@mail.hfut.edu.cn。"
TITLE_CN = "Jetson端工业缺陷检测的输入数据路径重构"
TITLE_EN = "Input data-path reconstruction for industrial defect detection on Jetson"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "a": A, "wp": WP, "r": R}
Q = lambda local: f"{{{W}}}{local}"


def text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).strip()


def raw_text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS))


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
    # Every asserted production rule below is derived from the Phase 7.1
    # source-object crosswalk (HFUT_FMT_DOC / HFUT_REF_DOC / HFUT_FIG_DOC /
    # HFUT_TABLE_DOC), never from an earlier project-only validator.
    source_contract = "PAPER_PHASE7_1_HFUT_FORMAT_SATURATION_CROSSWALK_v1.0.csv"
    expected = {
        # eastAsia, Latin, half-points, line, lineRule, alignment, bold,
        # first-line indent. For lineRule=auto, w:line=240 is a single-line
        # multiplier rather than an exact 12 pt line box.
        "HFUTTitleCN": ("宋体", "Times New Roman", "44", "240", "auto", "center", True, None),
        "HFUTAuthorsCN": ("楷体", "Times New Roman", "28", None, None, "center", False, None),
        "HFUTTitleEN": ("Times New Roman", "Times New Roman", "28", None, None, "center", True, None),
        "HFUTAuthorsEN": ("Times New Roman", "Times New Roman", "21", None, None, "center", True, None),
        "HFUTBody": ("宋体", "Times New Roman", "21", "320", "exact", "both", False, "438"),
        "HFUTIntroHeading": ("黑体", "Times New Roman", "28", "320", "exact", "left", True, None),
        "HFUTHeading1": ("黑体", "Times New Roman", "28", "320", "exact", "left", False, None),
        "HFUTHeading2": ("黑体", "Times New Roman", "21", "320", "exact", "left", False, None),
        "HFUTHeading3": ("楷体", "Times New Roman", "21", "320", "exact", "left", False, None),
        "HFUTAuthorBiography": ("宋体", "Times New Roman", "15", "280", "exact", "left", False, None),
        "HFUTFigureCaption": ("黑体", "Times New Roman", "15", "320", "exact", "center", True, None),
        "HFUTTableContent": ("宋体", "Times New Roman", "15", "240", "exact", "center", False, None),
        "HFUTReferenceEntry": ("宋体", "Times New Roman", "15", "280", "exact", "left", False, None),
        "Bibliography": ("宋体", "Times New Roman", "15", "280", "exact", "left", False, None),
        "HFUTAbstractLabelCNChar": ("黑体", "Times New Roman", "18", None, None, None, False, None),
        "HFUTKeywordsLabelCNChar": ("黑体", "Times New Roman", "18", None, None, None, False, None),
        "HFUTAbstractLabelENChar": ("Times New Roman", "Times New Roman", "21", None, None, None, True, None),
        "HFUTKeywordsLabelENChar": ("Times New Roman", "Times New Roman", "21", None, None, None, True, None),
        "HFUTClassificationLabelCNChar": ("黑体", "Times New Roman", "18", None, None, None, False, None),
        "HFUTClassificationValueChar": ("宋体", "Times New Roman", "18", None, None, None, False, None),
        "HFUTDocumentCodeLabelCNChar": ("黑体", "Times New Roman", "18", None, None, None, True, None),
        "HFUTDocumentCodeValueChar": ("宋体", "Times New Roman", "18", None, None, None, False, None),
        "HFUTHeadingNumber1Char": ("黑体", "Times New Roman", "28", None, None, None, True, None),
        "HFUTHeadingTitle1Char": ("黑体", "Times New Roman", "28", None, None, None, False, None),
        "HFUTHeadingNumber2Char": ("黑体", "Times New Roman", "21", None, None, None, True, None),
        "HFUTHeadingTitle2Char": ("黑体", "Times New Roman", "21", None, None, None, False, None),
        "HFUTHeadingNumber3Char": ("楷体", "Times New Roman", "21", None, None, None, False, None),
        "HFUTHeadingTitle3Char": ("楷体", "Times New Roman", "21", None, None, None, False, None),
    }
    found = {node.get(Q("styleId")): node for node in styles.findall("w:style", NS)}
    for sid, (east, latin, size, line, line_rule, alignment, bold, first_line) in expected.items():
        node = found.get(sid)
        if node is None:
            errors.append(f"missing style {sid}")
            continue
        fonts = node.find("w:rPr/w:rFonts", NS)
        spacing = node.find("w:pPr/w:spacing", NS)
        actual = (
            attr(fonts, "eastAsia"), attr(fonts, "ascii"),
            attr(node.find("w:rPr/w:sz", NS), "val"),
            attr(spacing, "line"), attr(spacing, "lineRule"),
            attr(node.find("w:pPr/w:jc", NS), "val"),
            node.find("w:rPr/w:b", NS) is not None,
            attr(node.find("w:pPr/w:ind", NS), "firstLine"),
        )
        if actual != (east, latin, size, line, line_rule, alignment, bold, first_line):
            errors.append(f"style contract mismatch: {sid}; source={source_contract}")

    # HFUT_FMT_DOC P004–P006 direct paragraph geometry. The source specimens
    # distinguish these widths, so the validator must not homogenize them.
    for sid, expected_ind in {
        "HFUTAbstractBodyCN": ("420", "295"),
        "HFUTKeywordsBodyCN": ("420", "293"),
        "HFUTClassification": ("420", "293"),
    }.items():
        node = found.get(sid)
        ind = None if node is None else node.find("w:pPr/w:ind", NS)
        actual_ind = (attr(ind, "left"), attr(ind, "right"))
        if actual_ind != expected_ind:
            errors.append(
                f"front-matter geometry mismatch: {sid}={actual_ind}; "
                f"source=HFUT_FMT_DOC P004-P006"
            )


def title_line_box_contract(
    paragraphs: list[ET.Element], styles: ET.Element, errors: list[str]
) -> dict[str, object]:
    style_nodes = {
        node.get(Q("styleId")): node for node in styles.findall("w:style", NS)
    }
    style = style_nodes.get("HFUTTitleCN")
    title_paragraphs = [p for p in paragraphs if style_id(p) == "HFUTTitleCN"]
    if style is None or len(title_paragraphs) != 1:
        errors.append("Chinese title line-box inputs are missing")
        return {"status": "FAIL"}

    title = title_paragraphs[0]
    def chain(style_id_value: str) -> list[ET.Element]:
        result: list[ET.Element] = []
        seen: set[str] = set()
        while style_id_value and style_id_value not in seen:
            seen.add(style_id_value)
            node = style_nodes.get(style_id_value)
            if node is None:
                break
            result.append(node)
            based_on = node.find("w:basedOn", NS)
            style_id_value = attr(based_on, "val") or ""
        return result

    title_chain = chain("HFUTTitleCN")
    default_spacing = styles.find("w:docDefaults/w:pPrDefault/w:pPr/w:spacing", NS)
    spacing_sources = [title.find("w:pPr/w:spacing", NS)] + [
        node.find("w:pPr/w:spacing", NS) for node in title_chain
    ] + [default_spacing]

    def first_value(nodes: list[ET.Element | None], name: str) -> str | None:
        return next((value for node in nodes if (value := attr(node, name)) is not None), None)

    line_rule = first_value(spacing_sources, "lineRule")
    line = first_value(spacing_sources, "line")
    title_style_size = first_value(
        [node.find("w:rPr/w:sz", NS) for node in title_chain]
        + [styles.find("w:docDefaults/w:rPrDefault/w:rPr/w:sz", NS)],
        "val",
    )
    effective_run_sizes: list[int] = []
    for run in title.findall("w:r", NS):
        run_style_id = attr(run.find("w:rPr/w:rStyle", NS), "val") or ""
        run_sources = [run.find("w:rPr/w:sz", NS)]
        run_sources.extend(node.find("w:rPr/w:sz", NS) for node in chain(run_style_id))
        run_sources.extend(node.find("w:rPr/w:sz", NS) for node in title_chain)
        run_sources.append(styles.find("w:docDefaults/w:rPrDefault/w:rPr/w:sz", NS))
        effective_run_sizes.append(int(first_value(run_sources, "val") or "0"))
    max_size_half_points = max(effective_run_sizes or [int(title_style_size or "0")])
    font_size_twips = max_size_half_points * 10
    line_twips = int(line or "0")
    exact_too_small = line_rule == "exact" and line_twips < font_size_twips
    direct_spacing = title.find("w:pPr/w:spacing", NS)
    snap_to_grid = first_value(
        [title.find("w:pPr/w:snapToGrid", NS)]
        + [node.find("w:pPr/w:snapToGrid", NS) for node in title_chain]
        + [styles.find("w:docDefaults/w:pPrDefault/w:pPr/w:snapToGrid", NS)],
        "val",
    )
    run_positioning = [
        (attr(run.find("w:rPr/w:position", NS), "val"),
         attr(run.find("w:rPr/w:vertAlign", NS), "val"))
        for run in title.findall("w:r", NS)
    ]

    if (line_rule, line) != ("auto", "240"):
        errors.append(f"Chinese title automatic line-box override mismatch: {(line_rule, line)}")
    if snap_to_grid != "false":
        errors.append(f"Chinese title snapToGrid must be false: {snap_to_grid}")
    if direct_spacing is not None:
        errors.append("Chinese title has an unexpected direct paragraph spacing override")
    if any(position is not None or vertical is not None for position, vertical in run_positioning):
        errors.append(f"Chinese title uses forbidden run positioning: {run_positioning}")
    if exact_too_small:
        errors.append(
            "TITLE_VERTICAL_CLIPPING_RISK: exact line box is smaller than effective title font"
        )
    return {
        "font_size_half_points": max_size_half_points,
        "font_size_twips": font_size_twips,
        "line_rule": line_rule,
        "line_value": line_twips,
        "line_value_semantics": "single-line multiplier" if line_rule == "auto" else "twips",
        "snap_to_grid": snap_to_grid,
        "direct_paragraph_spacing": direct_spacing is not None,
        "line_box_smaller_than_font": exact_too_small,
        "vertical_clipping_risk": exact_too_small,
        "status": "PASS" if not exact_too_small else "FAIL",
    }


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
    out["chinese_title_line_box"] = title_line_box_contract(paragraphs, styles, errors)
    heading_errors, heading_rows = audit_heading_numbering_roots(
        document,
        styles,
        parsed.get("word/numbering.xml"),
        require_explicit_headings=True,
    )
    errors.extend(heading_errors)
    out["word_heading_numbering"] = "PASS" if not heading_errors else "FAIL"
    out["heading_paragraphs"] = len(heading_rows)

    sections = document.findall(".//w:sectPr", NS)
    section_columns = [attr(node.find("w:cols", NS), "num") for node in sections]
    out["section_columns"] = section_columns
    # HFUT source establishes one-column front matter and two-column body.
    # The count of implementation section transitions is document-specific.
    if not section_columns or section_columns[0] != "1" or "2" not in section_columns:
        errors.append(f"section transition mismatch: {section_columns}")
    for section in sections:
        size, margins, cols = section.find("w:pgSz", NS), section.find("w:pgMar", NS), section.find("w:cols", NS)
        actual = (attr(size, "w"), attr(size, "h"), attr(margins, "top"), attr(margins, "right"), attr(margins, "bottom"), attr(margins, "left"), attr(margins, "gutter"), attr(cols, "space"))
        if actual != ("11906", "16838", "1361", "1304", "1134", "1304", "0", "425"):
            errors.append(f"page geometry mismatch: {actual}")
        if attr(margins, "footer") != "907":
            errors.append(f"official footer distance mismatch: {attr(margins, 'footer')}")
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
        "HFUTAbstractBodyCN", "HFUTKeywordsBodyCN", "HFUTClassification",
        "HFUTAbstractBodyEN", "HFUTKeywordsBodyEN")}
    if any(value != 1 for value in counts.values()):
        errors.append(f"front-matter semantic style usage mismatch: {counts}")
    front_contract = {
        "HFUTAbstractBodyCN": ("摘 要：", "HFUTAbstractLabelCNChar"),
        "HFUTKeywordsBodyCN": ("关键词：", "HFUTKeywordsLabelCNChar"),
        "HFUTAbstractBodyEN": ("Abstract:", "HFUTAbstractLabelENChar"),
        "HFUTKeywordsBodyEN": ("Key words：", "HFUTKeywordsLabelENChar"),
    }
    for paragraph_style, (prefix, run_style) in front_contract.items():
        matches = [p for p in paragraphs if style_id(p) == paragraph_style]
        if len(matches) != 1 or not text(matches[0]).startswith(prefix):
            errors.append(f"same-paragraph front-matter prefix mismatch: {paragraph_style}")
            continue
        first_run_style = attr(matches[0].find("w:r/w:rPr/w:rStyle", NS), "val")
        if first_run_style != run_style:
            errors.append(f"inline label character style mismatch: {paragraph_style}={first_run_style}")

    # The official specimen is not a paragraph-level font contract.  These
    # checks bind each semantic front-matter token to its source-derived run.
    classification = [p for p in paragraphs if style_id(p) == "HFUTClassification"]
    if len(classification) != 1:
        errors.append("classification paragraph count mismatch")
    else:
        classification_runs = classification[0].findall("w:r", NS)
        observed = [
            (raw_text(run), attr(run.find("w:rPr/w:rStyle", NS), "val"))
            for run in classification_runs
            if raw_text(run) or run.find("w:tab", NS) is not None
        ]
        # Pandoc writes each requested space as its own unstyled run.  Treat
        # that mechanically split sequence as the one three-space source
        # separator while preserving style-token checks either side of it.
        normalized_observed: list[tuple[str, str | None]] = []
        for value, run_style in observed:
            if run_style is None and value == " " and normalized_observed and normalized_observed[-1] == ("   ", None):
                continue
            if run_style is None and value == " " and len(normalized_observed) >= 2 and normalized_observed[-1] == (" ", None):
                normalized_observed[-1] = ("  ", None)
            elif run_style is None and value == " " and normalized_observed and normalized_observed[-1] == ("  ", None):
                normalized_observed[-1] = ("   ", None)
            else:
                normalized_observed.append((value, run_style))
        expected = [
            ("中图分类号：", "HFUTClassificationLabelCNChar"),
            ("TP391.41", "HFUTClassificationValueChar"),
            ("   ", None),
            ("文献标识码：", "HFUTDocumentCodeLabelCNChar"),
            ("A", "HFUTDocumentCodeValueChar"),
        ]
        if normalized_observed != expected:
            errors.append(f"classification mixed-run contract mismatch: {observed}")

    heading_contract = {
        "HFUTIntroHeading": ("HFUTHeading1", "HFUTHeading1"),
        "HFUTHeading1": ("HFUTHeadingNumber1Char", "HFUTHeadingTitle1Char"),
        "HFUTHeading2": ("HFUTHeadingNumber2Char", "HFUTHeadingTitle2Char"),
        "HFUTHeading3": ("HFUTHeadingNumber3Char", "HFUTHeadingTitle3Char"),
    }
    for heading_style, (number_style, title_style) in heading_contract.items():
        for paragraph in [p for p in paragraphs if style_id(p) == heading_style]:
            if heading_style == "HFUTIntroHeading":
                # P012 uses bold number and title; it is intentionally not a
                # generic H1 specimen.  Its literal number/tab is checked by
                # the heading-numbering validator.
                continue
            runs = [run for run in paragraph.findall("w:r", NS) if text(run)]
            styled = [attr(run.find("w:rPr/w:rStyle", NS), "val") for run in runs]
            if len(styled) != 2 or styled != [number_style, title_style]:
                errors.append(
                    f"heading mixed-run contract mismatch: {heading_style}={styled}"
                )

    required_front_order = [
        "HFUTTitleCN", "HFUTAbstractBodyCN", "HFUTKeywordsBodyCN",
        "HFUTClassification", "HFUTTitleEN", "HFUTAbstractBodyEN",
        "HFUTKeywordsBodyEN",
    ]
    positions = {
        current: next((index for index, p in enumerate(paragraphs) if style_id(p) == current), -1)
        for current in required_front_order
    }
    if any(positions[current] < 0 for current in required_front_order) or (
        [positions[current] for current in required_front_order]
        != sorted(positions[current] for current in required_front_order)
    ):
        errors.append(f"front-matter order mismatch: {positions}")
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
    document_text = "\n".join(text(p) for p in document.findall(".//w:p", NS))
    for caption in captions:
        if document_text.count(caption) != 1:
            errors.append(f"accepted figure caption missing/duplicated: {caption}")
    drawing_paragraphs = [
        paragraph for paragraph in document.findall(".//w:p", NS)
        if paragraph.find(".//w:drawing", NS) is not None
    ]
    drawings = document.findall(".//w:drawing", NS)
    if len(drawings) != 3:
        errors.append(f"expected three drawings, found {len(drawings)}")
    inline_count = sum(len(paragraph.findall(".//wp:inline", NS)) for paragraph in drawing_paragraphs)
    anchor_count = sum(len(paragraph.findall(".//wp:anchor", NS)) for paragraph in drawing_paragraphs)
    out["drawing_paragraphs"] = len(drawing_paragraphs)
    out["wp_inline"] = inline_count
    out["wp_anchor"] = anchor_count
    if len(drawing_paragraphs) != 3 or inline_count != 3 or anchor_count != 0:
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
    # HFUT_FIG_DOC P004: F1 is full-width (<=16 cm); F2/F3 are single
    # column (<=7.5 cm). The current widths intentionally preserve this.
    expected_widths = [5760000, 2700000, 2700000]
    if any(abs(item["cx"] - expected) > 1 for item, expected in zip(figures, expected_widths)):
        errors.append(f"figure width contract mismatch: {[item['cx'] for item in figures]}")

    tables = [
        table for table in body.findall("w:tbl", NS)
        if not (attr(table.find("w:tblPr/w:tblCaption", NS), "val") or "").startswith("HFUT_FIGURE_FLOAT_")
    ]
    if len(tables) != 3 or [len(table.findall("w:tr", NS)) - 1 for table in tables] != [6, 9, 3]:
        errors.append("T1/T2/T3 row contract failed")
    for table_index, table in enumerate(tables, start=1):
        borders = table.find("w:tblPr/w:tblBorders", NS)
        actual = {node.tag.rsplit("}", 1)[-1]: (attr(node, "val"), attr(node, "sz")) for node in borders} if borders is not None else {}
        if actual and actual.get("insideV", (None,))[0] != "nil":
            errors.append(f"printed vertical table border present: T{table_index} {actual}")

    if any(token in package_text for token in ("FULL_BODY_SECTION_START", "TOOLCHAIN TEST")):
        errors.append("forbidden build marker present")
    if any(token in body_text for token in ("PENDING", "TBD", "UNKNOWN")):
        errors.append("visible publication placeholder present")
    out["formal_equations"] = len(document.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara"))
    out["equation_submission_object"] = "MATHTYPE_DEFERRED_MANUAL_SUBMISSION_STAGE"
    out["page_fields"] = sum(page_counts)
    out["biography_package_count"] = package_bio
    return errors, out


def normalized_layout_text(value: str) -> str:
    return re.sub(r"\s+", "", value).casefold()


def pdf_layout_lines(path: Path) -> tuple[int, list[dict[str, object]]]:
    completed = subprocess.run(
        ["pdftotext", "-bbox-layout", str(path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    root = ET.fromstring(completed.stdout)
    pages = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "page"]
    lines: list[dict[str, object]] = []
    for page_index, page in enumerate(pages, start=1):
        for node in page.iter():
            if node.tag.rsplit("}", 1)[-1] != "line":
                continue
            value = "".join(node.itertext()).strip()
            if not value:
                continue
            lines.append(
                {
                    "page": page_index,
                    "text": value,
                    "norm": normalized_layout_text(value),
                    "width_pt": float(node.get("xMax", "0")) - float(node.get("xMin", "0")),
                }
            )
    return len(pages), lines


def locate_rendered_text(lines: list[dict[str, object]], target: str) -> list[dict[str, object]]:
    needle = normalized_layout_text(target)
    for line in lines:
        if needle in str(line["norm"]):
            return [line]
    for start in range(len(lines)):
        joined = str(lines[start]["norm"])
        if not needle.startswith(joined):
            continue
        page = lines[start]["page"]
        for end in range(start + 1, min(start + 4, len(lines))):
            if lines[end]["page"] != page:
                break
            joined += str(lines[end]["norm"])
            if joined == needle:
                return lines[start : end + 1]
            if not needle.startswith(joined):
                break
    return []


def validate_pdf_layout(docx_path: Path, pdf_path: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    page_count, lines = pdf_layout_lines(pdf_path)
    _, parsed = load(docx_path)
    paragraphs = parsed["word/document.xml"].findall(".//w:body/w:p", NS)
    heading_texts = [
        text(paragraph) for paragraph in paragraphs
        if style_id(paragraph) in {
            "HFUTIntroHeading", "HFUTHeading1", "HFUTHeading2",
            "HFUTHeading3", "HFUTReferenceHeading",
        }
    ]
    title_results: dict[str, object] = {}
    for label, title in (("chinese", TITLE_CN), ("english", TITLE_EN)):
        located = locate_rendered_text(lines, title)
        line_count = len(located)
        width_pt = max((float(item["width_pt"]) for item in located), default=0.0)
        title_results[label] = {
            "line_count": line_count,
            "actual_break": line_count > 1,
            "max_rendered_line_width_pt": round(width_pt, 3),
            "max_rendered_line_width_cm": round(width_pt * 2.54 / 72.0, 3),
        }
        if not located:
            errors.append(f"{label} title not located in mechanical PDF")
    if title_results["chinese"]["line_count"] != 1:
        errors.append("PHASE56G_FMT_TITLE_LENGTH_NEEDS_MAIN_AI_DECISION_R2")

    wrapped_headings: list[str] = []
    missing_headings: list[str] = []
    for heading in heading_texts:
        located = locate_rendered_text(lines, heading)
        if not located:
            missing_headings.append(heading)
        elif len(located) != 1:
            wrapped_headings.append(heading)
    if missing_headings:
        errors.append(f"headings not located in mechanical PDF: {missing_headings}")
    if wrapped_headings:
        errors.append(f"wrapped headings in mechanical PDF: {wrapped_headings}")
    return errors, {
        "page_count": page_count,
        "titles": title_results,
        "heading_count": len(heading_texts),
        "wrapped_headings": wrapped_headings,
        "english_title_status": (
            "ONE_LINE" if title_results["english"]["line_count"] == 1
            else "OFFICIAL_COMPATIBLE_TITLE_WRAP"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", required=True, type=Path)
    parser.add_argument("--anonymous", required=True, type=Path)
    parser.add_argument("--full-pdf", required=True, type=Path)
    parser.add_argument("--anonymous-pdf", required=True, type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    reference_hash = sha256(REFERENCE)
    results = {}
    for variant, path, pdf_path in (
        ("full", args.full, args.full_pdf),
        ("anonymous", args.anonymous, args.anonymous_pdf),
    ):
        current_errors, details = validate_variant(path, variant)
        errors.extend(f"{variant}: {message}" for message in current_errors)
        pdf_errors, pdf_details = validate_pdf_layout(path, pdf_path)
        errors.extend(f"{variant}: {message}" for message in pdf_errors)
        details["mechanical_pdf"] = pdf_details
        results[variant] = details
    print(f"reference_docx_sha256={reference_hash}")
    for variant, details in results.items():
        print(f"{variant}={details}")
    full_line_box = results.get("full", {}).get("chinese_title_line_box", {})
    full_render = results.get("full", {}).get("mechanical_pdf", {}).get("titles", {}).get("chinese", {})
    print("CHINESE_TITLE_FONT=SimSun")
    print("CHINESE_TITLE_SIZE=22_pt")
    print("CHINESE_TITLE_BOLD=YES")
    print("CHINESE_TITLE_ALIGNMENT=CENTER")
    print(f"CHINESE_TITLE_RENDERED_LINES={full_render.get('line_count', 'UNKNOWN')}")
    print(f"TITLE_LINE_RULE={full_line_box.get('line_rule', 'UNKNOWN')}")
    print("TITLE_LINE_HEIGHT=240_AUTO_SINGLE_LINE_MULTIPLIER")
    print(
        "TITLE_LINE_BOX_SMALLER_THAN_FONT="
        + ("YES" if full_line_box.get("line_box_smaller_than_font") else "NO")
    )
    print(
        "TITLE_VERTICAL_CLIPPING_RISK="
        + ("YES" if full_line_box.get("vertical_clipping_risk") else "NO")
    )
    print("ENGLISH_TITLE_STYLE_MUTATION=NO")
    if errors:
        print("verdict=FAIL")
        for message in errors:
            print(f"ERROR: {message}")
        return 1
    print("SUBMISSION_EXCEPTION_MATHTYPE=DOCUMENTED_SUBMISSION_EXCEPTION")
    print("SUBMISSION_EXCEPTION_VISIO_ORIGIN=DOCUMENTED_SUBMISSION_EXCEPTION")
    print("STRUCTURAL_REFERENCE_TYPOGRAPHY_PASS")
    print("verdict=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
