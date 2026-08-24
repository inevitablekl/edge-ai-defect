#!/usr/bin/env python3
"""Validate the active Phase 6.3 review-build and submission-gate contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
FIGURE_MANIFEST = MANUSCRIPT / "figures/figure_manifest.csv"
EQUATION_MANIFEST = MANUSCRIPT / "equations/equation_manifest.csv"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "m": M, "wp": WP, "a": A, "r": R, "pr": PR}

FIGURE_CAPTIONS = {
    "图1": "图1　输入数据路径抽象及层级受控比较。图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。",
    "图2": "图2　三条路径的端到端性能。(a) 为5个独立进程FPS的均值±样本标准差；(b)(c) 为每条路径合并5400个延迟样本的均值、P95和P99。",
    "图3": "图3　运行级分布与尾延迟。各点为独立进程级描述量，横向偏移仅用于区分，不表示运行配对。",
}
FIGURE_FLOAT_MARKERS = {
    "图1": "HFUT_FIGURE_FLOAT_F1",
    "图2": "HFUT_FIGURE_FLOAT_F2",
    "图3": "HFUT_FIGURE_FLOAT_F3",
}
STATISTICAL_REVIEW_PNGS = {
    "图2": ROOT / "docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png",
    "图3": ROOT / "docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png",
}
# Project QA advisory, not an HFUT publication limit. Report it to help detect
# unusually tall single-column figures, but never fail a build at this value.
ADVISORY_SINGLE_COLUMN_HEIGHT_CM = 15.5
# Artist-tight output should be close to symmetric, but raster antialiasing can
# differ by a few pixels. Two percent rejects the 10–13% baseline asymmetry
# without imposing a brittle zero-pixel rule.
MAX_HORIZONTAL_PADDING_ASYMMETRY = 0.02
MAX_BBOX_CENTER_OFFSET = 0.01
WORD_JOINER = "\u2060"
GOVERNED_NO_BREAK_PHRASE = f"每条路径报{WORD_JOINER}告5个进程级FPS"
TABLE_CAPTIONS = (
    "表1　三条输入数据路径的结构描述与派生量。名义输入复制载荷由跨边界表示推导，非实测流量。",
    "表2　平台、模型与统一基准协议。",
    "表3　三条路径在冻结工作负载和统一评价程序下的任务级正确性。",
)
REFERENCE_STYLE_IDS = ("HFUTReferenceEntry", "Bibliography")
REFERENCE_TEXT_SHA256 = "cc271cc81cc89342ef7652d8a51f81f25c431617d1da6b235faa72cca0c5ccef"
ACCENTED_SURNAME = "Sánchez-González"
PAGINATION_QA_CATEGORIES = (
    "ACCEPTABLE_TYPOGRAPHIC_RESERVE",
    "WIDOW_ORPHAN_RESERVE",
    "HEADING_KEEP_WITH_NEXT_RESERVE",
    "FLOAT_ANCHOR_FLOW_DEFECT",
    "UNKNOWN_LAYOUT_DEFECT",
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


def style_contract(style: ET.Element | None) -> tuple[object, ...]:
    if style is None:
        return (None,) * 11
    ppr = style.find("w:pPr", NS)
    rpr = style.find("w:rPr", NS)
    fonts = None if rpr is None else rpr.find("w:rFonts", NS)
    spacing = None if ppr is None else ppr.find("w:spacing", NS)
    indent = None if ppr is None else ppr.find("w:ind", NS)
    return (
        attr(fonts, "ascii"), attr(fonts, "hAnsi"), attr(fonts, "eastAsia"),
        attr(None if rpr is None else rpr.find("w:sz", NS), "val"),
        attr(None if rpr is None else rpr.find("w:szCs", NS), "val"),
        attr(spacing, "before"), attr(spacing, "after"),
        attr(spacing, "line"), attr(spacing, "lineRule"),
        attr(indent, "left"), attr(indent, "hanging"),
    )


def paragraph_style_id(paragraph: ET.Element) -> str | None:
    return attr(paragraph.find("w:pPr/w:pStyle", NS), "val")


def on_off_value(node: ET.Element | None) -> bool | None:
    if node is None:
        return None
    return attr(node, "val") not in {"0", "false", "off"}


def paragraph_pagination_audit(
    document: ET.Element, styles: ET.Element
) -> tuple[list[str], dict[str, object]]:
    """Audit effective body/heading pagination without changing Word defaults."""

    errors: list[str] = []
    properties = ("widowControl", "keepNext", "keepLines", "pageBreakBefore")
    style_map = {
        attr(style, "styleId"): style for style in styles.findall("w:style", NS)
    }

    def direct_values(parent: ET.Element | None) -> dict[str, bool | None]:
        ppr = None if parent is None else parent.find("w:pPr", NS)
        return {
            name: on_off_value(None if ppr is None else ppr.find(f"w:{name}", NS))
            for name in properties
        }

    default_values = direct_values(styles.find("w:docDefaults/w:pPrDefault", NS))
    # ISO/IEC 29500 defines widow/orphan prevention as on when widowControl is
    # never specified in the hierarchy. The other omitted pagination controls
    # are not promoted to enabled project rules.
    terminal_defaults = {
        "widowControl": True,
        "keepNext": False,
        "keepLines": False,
        "pageBreakBefore": False,
    }

    def style_chain(style_id: str) -> list[dict[str, object]]:
        chain: list[dict[str, object]] = []
        seen: set[str] = set()
        current: str | None = style_id
        while current and current not in seen:
            seen.add(current)
            style = style_map.get(current)
            chain.append({"style_id": current, "direct": direct_values(style)})
            current = attr(None if style is None else style.find("w:basedOn", NS), "val")
        return chain

    def effective(style_id: str, name: str) -> bool:
        for item in style_chain(style_id):
            value = item["direct"][name]  # type: ignore[index]
            if value is not None:
                return bool(value)
        value = default_values[name]
        return terminal_defaults[name] if value is None else value

    style_details: dict[str, object] = {}
    for style_id in ("HFUTBody", "HFUTHeading1", "HFUTHeading2", "HFUTHeading3"):
        effective_values = {name: effective(style_id, name) for name in properties}
        style_details[style_id] = {
            "chain": style_chain(style_id),
            "effective": effective_values,
        }

    body_paragraphs = [
        paragraph for paragraph in document.findall(".//w:p", NS)
        if paragraph_style_id(paragraph) == "HFUTBody"
    ]
    direct_body_enabled = {
        name: sum(
            on_off_value(paragraph.find(f"w:pPr/w:{name}", NS)) is True
            for paragraph in body_paragraphs
        )
        for name in properties
    }
    if direct_body_enabled["keepNext"] or direct_body_enabled["keepLines"]:
        errors.append(
            "HFUTBody contains a direct keep-with-next/keep-lines pagination chain"
        )
    if effective("HFUTBody", "keepNext") or effective("HFUTBody", "keepLines"):
        errors.append("HFUTBody style hierarchy enables an accidental keep chain")
    if not effective("HFUTBody", "widowControl"):
        errors.append("HFUTBody widow/orphan protection is disabled")
    for style_id in ("HFUTHeading1", "HFUTHeading2", "HFUTHeading3"):
        if not effective(style_id, "keepNext"):
            errors.append(f"{style_id} does not preserve keep-with-next")
        if not effective(style_id, "keepLines"):
            errors.append(f"{style_id} does not preserve keep-lines")
        if effective(style_id, "pageBreakBefore"):
            errors.append(f"{style_id} unexpectedly forces pageBreakBefore")

    return errors, {
        "document_defaults": default_values,
        "terminal_ooxml_defaults": terminal_defaults,
        "styles": style_details,
        "hfut_body_paragraph_count": len(body_paragraphs),
        "hfut_body_direct_enabled_counts": direct_body_enabled,
    }


def image_content_geometry(path: Path) -> dict[str, object]:
    """Measure non-background content with antialiasing noise suppressed."""

    with Image.open(path) as source:
        rgba = source.convert("RGBA")
    composite = Image.new("RGBA", rgba.size, "white")
    composite.alpha_composite(rgba)
    rgb = composite.convert("RGB")
    mask = rgb.point(lambda value: 255 if value < 245 else 0).convert("1")
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError(f"review PNG contains no visible content: {path}")
    left, top, right, bottom = bbox
    width, height = rgb.size
    left_padding = left
    right_padding = width - right
    top_padding = top
    bottom_padding = height - bottom
    return {
        "canvas_pixels": [width, height],
        "content_bbox": [left, top, right, bottom],
        "padding_pixels": {
            "left": left_padding, "right": right_padding,
            "top": top_padding, "bottom": bottom_padding,
        },
        "horizontal_padding_asymmetry": abs(left_padding - right_padding) / width,
        "bbox_center_offset": abs((left + right) / 2 - width / 2) / width,
        "content_centroid_pixels": [(left + right) / 2, (top + bottom) / 2],
    }


def validate_docx(path: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    details: dict[str, object] = {}
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            return [f"ZIP CRC failure: {bad}"], details
        document = ET.fromstring(archive.read("word/document.xml"))
        styles = ET.fromstring(archive.read("word/styles.xml"))
        relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    body = document.find("w:body", NS)
    if body is None:
        return ["document.xml has no body"], details
    children = list(body)
    paragraphs = document.findall(".//w:p", NS)
    text = "\n".join(text_of(node) for node in document.findall(".//w:p", NS))
    image_relationships = {
        rel.get("Id"): rel.get("Target") for rel in relationships
        if rel.get("Type", "").endswith("/image")
    }

    pagination_errors, pagination_details = paragraph_pagination_audit(document, styles)
    errors.extend(pagination_errors)
    details["paragraph_pagination_audit"] = pagination_details

    no_break_count = text.count(GOVERNED_NO_BREAK_PHRASE)
    if no_break_count != 1:
        errors.append(
            f"governed 报告 cross-column no-break count is {no_break_count}, expected 1"
        )
    details["governed_lexical_no_break_count"] = no_break_count

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
    figure_layout_contract: list[dict[str, object]] = []
    figure_callout_proximity: list[dict[str, object]] = []
    for index, (label, caption_text) in enumerate(FIGURE_CAPTIONS.items()):
        marker = FIGURE_FLOAT_MARKERS[label]
        float_tables = [
            node for node in body.findall("w:tbl", NS)
            if attr(node.find("w:tblPr/w:tblCaption", NS), "val") == marker
        ]
        if len(float_tables) != 1:
            errors.append(f"Figure {index + 1} floating-container count is {len(float_tables)}, expected 1")
            continue
        float_table = float_tables[0]
        matches = [node for node in float_table.findall(".//w:p", NS) if text_of(node) == caption_text]
        if len(matches) != 1:
            errors.append(f"Figure {index + 1} caption count mismatch")
            continue
        caption = matches[0]
        float_position = children.index(float_table)
        cell_paragraphs = float_table.findall("w:tr/w:tc/w:p", NS)
        if len(cell_paragraphs) != 2 or cell_paragraphs[1] is not caption:
            errors.append(f"Figure {index + 1} caption is not immediately below its drawing")
            continue
        drawing = cell_paragraphs[0]
        if drawing.find(".//w:drawing", NS) is None:
            errors.append(f"Figure {index + 1} floating container has no drawing before caption")
            continue
        extent = drawing.find(".//wp:extent", NS)
        width = int(extent.get("cx", "0") if extent is not None else 0)
        height = int(extent.get("cy", "0") if extent is not None else 0)
        drawing_widths.append(width)
        expected = 5_760_000 if index == 0 else 2_700_000
        if abs(width - expected) > 2:
            errors.append(f"Figure {index + 1} width is {width}, expected {expected} EMU")
        prior_callouts = [
            node for node in children[:float_position]
            if node.tag == qn(W, "p") and label in text_of(node)
        ]
        if not prior_callouts:
            errors.append(f"Figure {index + 1} first callout is not before its drawing")
        else:
            callout_position = children.index(prior_callouts[0])
            intervening = children[callout_position + 1:float_position]
            intervening_headings = [
                node for node in intervening
                if node.tag == qn(W, "p")
                and (paragraph_style_id(node) or "").startswith("HFUTHeading")
                and text_of(node)
            ]
            intervening_body = [
                node for node in intervening
                if node.tag == qn(W, "p")
                and paragraph_style_id(node) == "HFUTBody"
                and text_of(node)
            ]
            figure_callout_proximity.append({
                "label": label,
                "first_callout_document_position": callout_position + 1,
                "figure_document_position": float_position + 1,
                "intervening_heading_count": len(intervening_headings),
                "intervening_body_paragraph_count": len(intervening_body),
                "intervening_headings": [text_of(node) for node in intervening_headings],
            })
        drawing_ppr = drawing.find("w:pPr", NS)
        if drawing_ppr is None or drawing_ppr.find("w:keepNext", NS) is None:
            errors.append(f"Figure {index + 1} drawing is not kept with its caption")
        caption_ppr = caption.find("w:pPr", NS)
        if caption_ppr is not None and caption_ppr.find("w:keepNext", NS) is not None:
            errors.append(f"Figure {index + 1} caption incorrectly blocks following prose")
        section = caption.find("w:pPr/w:sectPr", NS)
        if section is not None:
            errors.append(f"Figure {index + 1} floating container incorrectly carries a section break")
        if drawing_ppr is not None and drawing_ppr.find("w:pageBreakBefore", NS) is not None:
            errors.append(f"Figure {index + 1} floating container has an unnecessary forced page break")

        table_position = float_table.find("w:tblPr/w:tblpPr", NS)
        overlap = float_table.find("w:tblPr/w:tblOverlap", NS)
        row = float_table.find("w:tr", NS)
        inline_count = len(float_table.findall(".//wp:inline", NS))
        anchor_count = len(float_table.findall(".//wp:anchor", NS))
        blips = float_table.findall(".//a:blip", NS)
        relationship_id = attr(blips[0], "embed", R) if len(blips) == 1 else None
        image_target = image_relationships.get(relationship_id or "")
        if table_position is None:
            errors.append(f"INLINE_FIGURE_FLOW_BARRIER: Figure {index + 1} has no floating-table positioning")
        if inline_count != 1 or anchor_count != 0:
            errors.append(
                f"Figure {index + 1} drawing representation mismatch inside float: "
                f"inline={inline_count} anchor={anchor_count}"
            )
        if image_target is None:
            errors.append(f"Figure {index + 1} floating drawing relationship is invalid")
        if attr(overlap, "val") != "never":
            errors.append(f"Figure {index + 1} floating container permits overlap")
        if row is None or row.find("w:trPr/w:cantSplit", NS) is None:
            errors.append(f"Figure {index + 1} drawing/caption row can split")
        expected_position = (
            ("margin", "margin", "center", "top", None)
            if index == 0 else ("text", "text", "center", None, "1")
        )
        actual_position = (
            attr(table_position, "vertAnchor"),
            attr(table_position, "horzAnchor"),
            attr(table_position, "tblpXSpec"),
            attr(table_position, "tblpYSpec"),
            attr(table_position, "tblpY"),
        )
        if actual_position != expected_position:
            errors.append(
                f"Figure {index + 1} floating positioning contract mismatch: {actual_position}"
            )
        figure_layout_contract.append({
            "label": label,
            "placement_type": "FLOATING",
            "floating_container": "WORD_TABLE",
            "width_emu": width,
            "height_emu": height,
            "height_cm": round(height / 360_000, 2),
            "height_advisory_cm": (
                None if index == 0 else ADVISORY_SINGLE_COLUMN_HEIGHT_CM
            ),
            "height_advisory_exceeded": (
                False if index == 0
                else height / 360_000 > ADVISORY_SINGLE_COLUMN_HEIGHT_CM
            ),
            "callout_precedes": bool(prior_callouts),
            "inline_inside_floating_container": inline_count == 1,
            "wp_anchor_count": anchor_count,
            "text_wrap_around_float_supported": table_position is not None,
            "backfill_before_logical_float_anchor_guaranteed": False,
            "microsoft_word_pagination_status": "PENDING",
            "horizontal_reference": attr(table_position, "horzAnchor"),
            "horizontal_centered": attr(table_position, "tblpXSpec") == "center",
            "vertical_reference": attr(table_position, "vertAnchor"),
            "vertical_page_top": attr(table_position, "tblpYSpec") == "top",
            "wrap_type": "FLOATING_TABLE_AROUND",
            "allow_overlap": attr(overlap, "val") != "never",
            "move_with_text": attr(table_position, "vertAnchor") == "text",
            "caption_association": "SINGLE_CANT_SPLIT_ROW",
            "relationship_id": relationship_id,
            "image_target": image_target,
            "drawing_keep_next": (
                drawing_ppr is not None and drawing_ppr.find("w:keepNext", NS) is not None
            ),
            "page_break_before": (
                drawing_ppr is not None
                and drawing_ppr.find("w:pageBreakBefore", NS) is not None
            ),
            "caption_section": None if section is None else section_values(section),
        })
    details["figure_widths_emu"] = drawing_widths
    details["figure_layout_contract"] = figure_layout_contract
    details["figure_callout_proximity"] = figure_callout_proximity

    optical_geometry: dict[str, dict[str, object]] = {}
    for label, png_path in STATISTICAL_REVIEW_PNGS.items():
        try:
            geometry = image_content_geometry(png_path)
        except (OSError, ValueError) as exc:
            errors.append(f"{label} optical-centering measurement failed: {exc}")
            continue
        optical_geometry[label] = geometry
        asymmetry = float(geometry["horizontal_padding_asymmetry"])
        center_offset = float(geometry["bbox_center_offset"])
        if asymmetry > MAX_HORIZONTAL_PADDING_ASYMMETRY:
            errors.append(
                f"{label} horizontal canvas-padding asymmetry is {asymmetry:.4f}, "
                f"above {MAX_HORIZONTAL_PADDING_ASYMMETRY:.4f}"
            )
        if center_offset > MAX_BBOX_CENTER_OFFSET:
            errors.append(
                f"{label} visual-content center offset is {center_offset:.4f}, "
                f"above {MAX_BBOX_CENTER_OFFSET:.4f}"
            )
    details["statistical_figure_optical_geometry"] = optical_geometry

    for caption_text in TABLE_CAPTIONS:
        matches = [node for node in paragraphs if text_of(node) == caption_text]
        if len(matches) != 1:
            errors.append(f"table caption count mismatch: {caption_text}")
            continue
        position = children.index(matches[0])
        following = next((node for node in children[position + 1:] if node.tag != qn(W, "p") or text_of(node)), None)
        if following is None or following.tag != qn(W, "tbl"):
            errors.append(f"table caption is not above its native Word table: {caption_text}")

    tables = [
        table for table in body.findall("w:tbl", NS)
        if not (attr(table.find("w:tblPr/w:tblCaption", NS), "val") or "").startswith("HFUT_FIGURE_FLOAT_")
    ]
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
    expected_reference_contract = (
        "Times New Roman", "Times New Roman", "宋体", "15", "15",
        "0", "0", "280", "exact", "360", "360",
    )
    reference_contracts: dict[str, tuple[object, ...]] = {}
    for style_id in REFERENCE_STYLE_IDS:
        style = style_map.get(style_id)
        contract = style_contract(style)
        reference_contracts[style_id] = contract
        if contract != expected_reference_contract:
            errors.append(f"{style_id} font/size/spacing/hanging-indent contract mismatch")
        if style is None or attr(style.find("w:pPr/w:jc", NS), "val") != "left":
            errors.append(f"{style_id} is not left-aligned for stable narrow-column rendering")

    references = [
        paragraph for paragraph in paragraphs
        if paragraph_style_id(paragraph) in REFERENCE_STYLE_IDS
    ]
    reference_texts = [text_of(paragraph) for paragraph in references]
    if len(reference_texts) != 22:
        errors.append(f"rendered reference count is {len(reference_texts)}, expected 22")
    numbers = []
    for reference in reference_texts:
        match = re.match(r"\[(\d+)\]", reference)
        numbers.append(int(match.group(1)) if match else None)
    if numbers != list(range(1, 23)):
        errors.append("rendered reference numbering is not sequential [1]-[22]")
    reference_hash = hashlib.sha256("\n".join(reference_texts).encode("utf-8")).hexdigest()
    if reference_hash != REFERENCE_TEXT_SHA256:
        errors.append("rendered reference metadata/content changed from the accepted Phase 6.3R1 set")
    if any("等" in reference for reference in reference_texts) or sum(
        "et al." in reference for reference in reference_texts
    ) != 9:
        errors.append("rendered et al./等 behavior changed")
    surname_references = [reference for reference in reference_texts if ACCENTED_SURNAME in reference]
    if len(surname_references) != 1:
        errors.append("Sánchez-González is not preserved as one contiguous source-text surname")
    surname_text_nodes = [
        node for paragraph in references for node in paragraph.findall(".//w:t", NS)
        if ACCENTED_SURNAME in (node.text or "")
    ]
    if len(surname_text_nodes) != 1:
        errors.append("Sánchez-González is split across OOXML text nodes")
    else:
        parent_run = next(
            (
                run for paragraph in references for run in paragraph.findall(".//w:r", NS)
                if surname_text_nodes[0] in list(run)
            ),
            None,
        )
        direct_fonts = None if parent_run is None else parent_run.find("w:rPr/w:rFonts", NS)
        for font_slot, governed_font in (
            ("ascii", "Times New Roman"), ("hAnsi", "Times New Roman"), ("eastAsia", "宋体")
        ):
            direct_value = attr(direct_fonts, font_slot)
            if direct_value is not None and direct_value != governed_font:
                errors.append(f"Sánchez-González has an incorrect direct {font_slot} font override")

    details["equation_numbers"] = [text_of(node) for node in equations]
    details["table_count"] = len(tables)
    details["a4"] = not any("A4" in error for error in errors)
    details["figure1_section_contract"] = None
    details["reference_contracts"] = reference_contracts
    details["reference_texts"] = reference_texts
    details["reference_text_sha256"] = reference_hash
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
        if details.get("figure1_section_contract") != full_details.get("figure1_section_contract"):
            errors.append("Full/Anonymous Figure 1 section-contract parity mismatch")
        if details.get("figure_layout_contract") != full_details.get("figure_layout_contract"):
            errors.append("Full/Anonymous figure placement-contract parity mismatch")
        if (
            details.get("statistical_figure_optical_geometry")
            != full_details.get("statistical_figure_optical_geometry")
        ):
            errors.append("Full/Anonymous statistical-figure optical-geometry parity mismatch")
        if (
            details.get("governed_lexical_no_break_count")
            != full_details.get("governed_lexical_no_break_count")
        ):
            errors.append("Full/Anonymous governed lexical no-break parity mismatch")
        if details.get("reference_contracts") != full_details.get("reference_contracts"):
            errors.append("Full/Anonymous reference-style parity mismatch")
        if details.get("reference_texts") != full_details.get("reference_texts"):
            errors.append("Full/Anonymous rendered-reference parity mismatch")
    if errors:
        for error in errors:
            print(f"PHASE63_FORMAT_ERROR: {error}")
        print("MANUSCRIPT_BUILD_FAIL")
        print("HFUT_SUBMISSION_NOT_READY")
        return 1
    print(f"MANUSCRIPT_BUILD_PASS docx={args.docx}")
    print("STRUCTURAL_FORMAT_VALIDATION=PASS")
    print("EQUATION_NUMBERING_COMPLETE E1=（1） E2=（2） E3=（3）")
    print("FIGURE_LIFECYCLE_VALID scientific=FROZEN review=PNG submission=OPEN")
    for contract in details.get("figure_layout_contract", []):
        print(
            "FIGURE_FLOW "
            f"label={contract['label']} placement_type={contract['placement_type']} "
            f"container={contract['floating_container']} "
            "text_wrap_around_float=SUPPORTED "
            "backfill_before_logical_float_anchor=NOT_GUARANTEED "
            f"caption_association={contract['caption_association']}"
        )
    for metric in details.get("figure_callout_proximity", []):
        print(
            "FIGURE_CALL_OUT_PROXIMITY "
            f"label={metric['label']} "
            f"callout_position={metric['first_callout_document_position']} "
            f"figure_position={metric['figure_document_position']} "
            f"intervening_headings={metric['intervening_heading_count']} "
            f"intervening_body_paragraphs={metric['intervening_body_paragraph_count']}"
        )
    print(
        "SINGLE_COLUMN_HEIGHT_15_5_CM="
        "PROJECT_QA_ADVISORY_NOT_PUBLICATION_REQUIREMENT"
    )
    print("PAGINATION_QA_TAXONOMY=" + ",".join(PAGINATION_QA_CATEGORIES))
    print("PAGINATION_QA_EVIDENCE_BOUNDARY=OOXML_CANNOT_CLASSIFY_PAGE_SPACE")
    print("MICROSOFT_WORD_PAGINATION_STATUS=PENDING")
    print("WORD_ARTIFACT_VISUAL_REVIEW_REQUIRED=YES")
    print("PAGE3_FLOW=IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW")
    print("PAGE5_FLOW=IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW")
    print("PAGE6_FLOW=IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW")
    print("HFUT_SUBMISSION_NOT_READY VISIO=OPEN ORIGIN=OPEN MATHTYPE=OPEN WORD_DESKTOP_QA=OPEN ANONYMOUS_QA=OPEN DOCUMENT_INSPECTOR=OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
