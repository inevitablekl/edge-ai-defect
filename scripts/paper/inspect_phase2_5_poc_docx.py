#!/usr/bin/env python3
"""Inspect a Phase 2.5 Step 7B POC DOCX without claiming Word acceptance."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS = {"w": W, "m": M, "r": R, "pr": PR, "ct": CT, "a": A, "mc": MC}

REQUIRED_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "docProps/core.xml",
    "word/document.xml",
    "word/styles.xml",
    "word/numbering.xml",
    "word/settings.xml",
}
COMMON_STYLES = {
    "HFUTSpecimenNotice",
    "HFUTTitleCN",
    "HFUTTitleEN",
    "HFUTAbstractLabelCN",
    "HFUTAbstractBodyCN",
    "HFUTAbstractLabelEN",
    "HFUTAbstractBodyEN",
    "HFUTKeywordsLabelCN",
    "HFUTKeywordsBodyCN",
    "HFUTKeywordsLabelEN",
    "HFUTKeywordsBodyEN",
    "HFUTClassification",
    "HFUTBody",
    "HFUTIntroHeading",
    "HFUTHeading1",
    "HFUTHeading2",
    "HFUTHeading3",
    "HFUTEquation",
    "HFUTFigureCaption",
    "HFUTTableCaption",
    "HFUTTableContent",
    "HFUTReferenceHeading",
    "HFUTReferenceEntry",
}
FULL_ONLY_STYLES = {
    "HFUTAuthorsCN",
    "HFUTAuthorsEN",
    "HFUTAffiliationCN",
    "HFUTAffiliationEN",
    "HFUTFunding",
    "HFUTAuthorBiography",
    "HFUTAcknowledgement",
}
FORBIDDEN_ANONYMOUS = (
    "POC测试作者",
    "POC测试单位",
    "poc@example.invalid",
    "基金测试字段",
    "作者简介测试字段",
    "致谢测试字段",
)
FORBIDDEN_EXTERNAL_FIELD_TYPES = {
    "INCLUDEPICTURE", "INCLUDETEXT", "LINK", "DDE", "DDEAUTO", "RD"
}
NEUTRAL_GENERATOR_IDENTITIES = {"", "PAPER_PROJECT_AI_POC", "PAPER_PROJECT_TOOLCHAIN"}
PPR_ORDER = (
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
    "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
    "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
    "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
    "suppressOverlap", "jc", "textDirection", "textAlignment",
    "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr",
    "pPrChange",
)
SECTPR_ORDER = (
    "headerReference", "footerReference", "footnotePr", "endnotePr", "type",
    "pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType", "pgNumType",
    "cols", "formProt", "vAlign", "noEndnote", "titlePg", "textDirection",
    "bidi", "rtlGutter", "docGrid", "printerSettings", "sectPrChange",
)
TBLPR_ORDER = (
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
    "tblDescription", "tblPrChange",
)
RPR_ORDER = (
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps",
    "strike", "dstrike", "outline", "shadow", "emboss", "imprint",
    "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
    "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect",
    "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang",
    "eastAsianLayout", "specVanish", "oMath", "rPrChange",
)
STYLE_ORDER = (
    "name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden",
    "uiPriority", "semiHidden", "unhideWhenUsed", "qFormat", "locked",
    "personal", "personalCompose", "personalReply", "rsid", "pPr", "rPr",
    "tblPr", "trPr", "tcPr", "tblStylePr",
)
LVL_ORDER = (
    "start", "numFmt", "lvlRestart", "pStyle", "isLgl", "suff", "lvlText",
    "lvlPicBulletId", "legacy", "lvlJc", "pPr", "rPr",
)
VALID_STYLE_TYPES = {"paragraph", "character", "table", "numbering"}


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def xml_root(parts: dict[str, bytes], name: str) -> ET.Element:
    return ET.fromstring(parts[name])


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def attr(node: ET.Element | None, name: str, default: str = "") -> str:
    return default if node is None else node.get(qn(W, name), default)


def local_name(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def order_violations(nodes: list[ET.Element], order: tuple[str, ...]) -> list[list[str]]:
    violations = []
    rank = {name: index for index, name in enumerate(order)}
    for node in nodes:
        children = [local_name(child) for child in node]
        known = [rank[name] for name in children if name in rank]
        if known != sorted(known):
            violations.append(children)
    return violations


def relationship_source_part(rel_part: str) -> str | None:
    path = Path(rel_part)
    if path.name == ".rels" and path.parent.as_posix() == "_rels":
        return None
    if path.parent.name != "_rels" or not path.name.endswith(".rels"):
        return None
    return (path.parent.parent / path.name[:-5]).as_posix()


def inspect(path: Path, variant: str) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    result: dict[str, object] = {
        "classification": [
            "TOOLCHAIN_POC_ONLY",
            "SYNTHETIC_CONTENT",
            "NOT_PAPER_CONTENT",
            "NOT_FORMAL_REFERENCE_DATA",
            "NOT_SUBMISSION_MANUSCRIPT",
            "PHASE_3_NOT_AUTHORIZED",
        ],
        "path": str(path),
        "variant": variant,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }
    if path.name not in {f"poc_{variant}.docx", f"poc_{variant}_v2.docx", f"poc_{variant}_v3.docx"}:
        errors.append("unexpected output filename")

    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            names = archive.namelist()
            parts = {name: archive.read(name) for name in names}
    except (zipfile.BadZipFile, OSError) as exc:
        errors.append(f"invalid DOCX ZIP: {exc}")
        result["errors"] = errors
        return result, errors

    result["zip_test"] = "PASS" if bad is None else f"FAIL:{bad}"
    missing = sorted(REQUIRED_PARTS - set(parts))
    result["required_parts_missing"] = missing
    if missing:
        errors.append(f"missing required parts: {missing}")

    document = xml_root(parts, "word/document.xml")
    styles = xml_root(parts, "word/styles.xml")
    numbering = xml_root(parts, "word/numbering.xml")
    body = document.find("w:body", NS)
    if body is None:
        errors.append("missing w:body")
        result["errors"] = errors
        return result, errors

    paragraphs = body.findall(".//w:p", NS)
    text = "\n".join(para_text(p) for p in paragraphs)
    result["document_text_length"] = len(text)
    result["governance_markers_present"] = {
        marker: marker in text
        for marker in ("TOOLCHAIN POC ONLY", "NOT PAPER CONTENT", "NOT SUBMISSION MANUSCRIPT")
    }
    if not all(result["governance_markers_present"].values()):
        errors.append("first-page governance markers incomplete")

    final_sect = body.find("w:sectPr", NS)
    section_nodes = body.findall("w:p/w:pPr/w:sectPr", NS) + ([final_sect] if final_sect is not None else [])
    columns = []
    geometry = []
    for section in section_nodes:
        cols = section.find("w:cols", NS)
        pg_sz = section.find("w:pgSz", NS)
        pg_mar = section.find("w:pgMar", NS)
        columns.append({"num": int(attr(cols, "num", "1")), "space_twips": int(attr(cols, "space", "0"))})
        geometry.append({
            "page_twips": [int(attr(pg_sz, "w", "0")), int(attr(pg_sz, "h", "0"))],
            "margins_twips": {
                side: int(attr(pg_mar, side, "0")) for side in ("top", "right", "bottom", "left", "gutter")
            },
        })
    result["sections"] = {"count": len(section_nodes), "columns": columns, "geometry": geometry}
    if len(section_nodes) != 2 or [item["num"] for item in columns] != [1, 2]:
        errors.append("expected single-column front matter and double-column body")
    direct_final_sections = [child for child in body if local_name(child) == "sectPr"]
    final_section_is_last = bool(direct_final_sections) and body[-1] is direct_final_sections[0]
    result["sections"]["direct_final_count"] = len(direct_final_sections)
    result["sections"]["final_section_is_last"] = final_section_is_last
    if len(direct_final_sections) != 1 or not final_section_is_last:
        errors.append("body must end with exactly one final sectPr")
    if any(item["space_twips"] != 425 for item in columns):
        errors.append("column spacing is not 425 twips")
    expected_page = [11906, 16838]
    expected_margins = {"top": 1361, "right": 1304, "bottom": 1134, "left": 1304, "gutter": 0}
    if any(item["page_twips"] != expected_page or item["margins_twips"] != expected_margins for item in geometry):
        errors.append("page geometry or margins differ from reference candidate")
    if any(section.find("w:pgNumType", NS) is not None for section in section_nodes):
        errors.append("page-number restart found")
    result["page_number_continuity"] = "NO_RESTART_PROPERTY"

    style_nodes = styles.findall("w:style", NS)
    style_ids = [node.get(qn(W, "styleId"), "") for node in style_nodes]
    duplicate_style_ids = sorted(style_id for style_id, count in Counter(style_ids).items() if count > 1)
    invalid_style_types = sorted({
        node.get(qn(W, "type"), "") for node in style_nodes
        if node.get(qn(W, "type"), "") not in VALID_STYLE_TYPES
    })
    default_style_counts = Counter(
        node.get(qn(W, "type"), "") for node in style_nodes
        if node.get(qn(W, "default"), "").lower() in {"1", "true", "on"}
    )
    duplicate_default_types = sorted(
        style_type for style_type, count in default_style_counts.items() if count > 1
    )
    defined_styles = set(style_ids)
    missing_based_on = []
    based_on: dict[str, str] = {}
    for node in style_nodes:
        style_id = node.get(qn(W, "styleId"), "")
        parent = node.find("w:basedOn", NS)
        if parent is not None:
            parent_id = attr(parent, "val")
            based_on[style_id] = parent_id
            if parent_id not in defined_styles:
                missing_based_on.append({"style": style_id, "basedOn": parent_id})
    based_on_cycles = []
    for style_id in sorted(based_on):
        trail: list[str] = []
        current = style_id
        while current in based_on:
            if current in trail:
                based_on_cycles.append(trail[trail.index(current):] + [current])
                break
            trail.append(current)
            current = based_on[current]
    style_counts = Counter(
        node.get(qn(W, "val"), "") for node in document.findall(".//w:pStyle", NS)
    )
    required_used = set(COMMON_STYLES)
    if variant == "full":
        required_used |= FULL_ONLY_STYLES
    missing_defined = sorted(required_used - defined_styles)
    missing_used = sorted(style for style in required_used if style_counts[style] == 0)
    result["styles"] = {
        "definition_count": len(style_nodes),
        "duplicate_style_ids": duplicate_style_ids,
        "invalid_style_types": invalid_style_types,
        "default_style_counts": dict(sorted(default_style_counts.items())),
        "duplicate_default_types": duplicate_default_types,
        "missing_based_on": missing_based_on,
        "based_on_cycles": based_on_cycles,
        "defined_required_missing": missing_defined,
        "used_required_missing": missing_used,
        "actual_usage": dict(sorted(style_counts.items())),
    }
    if (duplicate_style_ids or invalid_style_types or duplicate_default_types
            or missing_based_on or based_on_cycles):
        errors.append("style definition integrity failed")
    if missing_defined or missing_used:
        errors.append(f"required style definition/use missing: defined={missing_defined}, used={missing_used}")

    style_ppr_ordering = order_violations(
        [node for style in style_nodes for node in style.findall("w:pPr", NS)],
        PPR_ORDER,
    )
    result["styles"]["paragraph_property_ordering"] = style_ppr_ordering
    if style_ppr_ordering:
        errors.append("style-level paragraph property ordering failed")

    headings = []
    expected_numbering = {
        "HFUTIntroHeading": (0, 2),
        "HFUTHeading1": (0, 1),
        "HFUTHeading2": (1, 1),
        "HFUTHeading3": (2, 1),
    }
    for paragraph in paragraphs:
        pstyle = paragraph.find("w:pPr/w:pStyle", NS)
        style_id = attr(pstyle, "val")
        if style_id not in expected_numbering:
            continue
        ilvl = paragraph.find("w:pPr/w:numPr/w:ilvl", NS)
        num_id = paragraph.find("w:pPr/w:numPr/w:numId", NS)
        observed = (int(attr(ilvl, "val", "-1")), int(attr(num_id, "val", "-1")))
        expected = expected_numbering[style_id]
        headings.append({"style": style_id, "text": para_text(paragraph), "ilvl": observed[0], "numId": observed[1]})
        if observed != expected:
            errors.append(f"heading numbering mismatch for {style_id}: {observed} != {expected}")
    num_to_abstract = {
        int(node.get(qn(W, "numId"), "-1")): int(attr(node.find("w:abstractNumId", NS), "val", "-1"))
        for node in numbering.findall("w:num", NS)
    }
    abstract_formats = {
        int(node.get(qn(W, "abstractNumId"), "-1")): [attr(level.find("w:lvlText", NS), "val") for level in node.findall("w:lvl", NS)]
        for node in numbering.findall("w:abstractNum", NS)
    }
    abstract_ids = [int(node.get(qn(W, "abstractNumId"), "-1")) for node in numbering.findall("w:abstractNum", NS)]
    num_ids = [int(node.get(qn(W, "numId"), "-1")) for node in numbering.findall("w:num", NS)]
    duplicate_abstract_ids = sorted(value for value, count in Counter(abstract_ids).items() if count > 1)
    duplicate_num_ids = sorted(value for value, count in Counter(num_ids).items() if count > 1)
    missing_abstract_refs = sorted({value for value in num_to_abstract.values() if value not in set(abstract_ids)})
    result["heading_numbering"] = {
        "paragraph_numPr": headings,
        "num_to_abstract": num_to_abstract,
        "abstract_formats": abstract_formats,
        "duplicate_abstract_ids": duplicate_abstract_ids,
        "duplicate_num_ids": duplicate_num_ids,
        "missing_abstract_refs": missing_abstract_refs,
        "visual_text_requires_renderer": True,
        "word_field_refresh_required": True,
    }
    if num_to_abstract.get(1) != 0 or num_to_abstract.get(2) != 1:
        errors.append("numbering numId/abstractNum relationship mismatch")
    if duplicate_abstract_ids or duplicate_num_ids or missing_abstract_refs:
        errors.append("numbering definition integrity failed")

    math_inline = len(document.findall(".//m:oMath", NS))
    math_para = len(document.findall(".//m:oMathPara", NS))
    equation_layout = []
    inline_formula_paragraphs = []
    style_by_id = {
        node.get(qn(W, "styleId"), ""): node for node in style_nodes
    }
    for paragraph in paragraphs:
        has_display = paragraph.find(".//m:oMathPara", NS) is not None
        has_math = paragraph.find(".//m:oMath", NS) is not None
        if not has_math:
            continue
        ppr = paragraph.find("w:pPr", NS)
        pstyle = attr(ppr.find("w:pStyle", NS) if ppr is not None else None, "val")
        spacing = ppr.find("w:spacing", NS) if ppr is not None else None
        spacing_source = "paragraph"
        if spacing is None:
            style_ppr = style_by_id.get(pstyle, ET.Element(qn(W, "pPr"))).find("w:pPr", NS)
            spacing = style_ppr.find("w:spacing", NS) if style_ppr is not None else None
            spacing_source = "style"
        detail = {
            "style": pstyle,
            "display": has_display,
            "line": attr(spacing, "line"),
            "lineRule": attr(spacing, "lineRule"),
            "before": attr(spacing, "before"),
            "after": attr(spacing, "after"),
            "spacing_source": spacing_source,
        }
        equation_layout.append(detail)
        if has_display:
            if pstyle != "HFUTEquation" or detail["lineRule"] not in {"auto", "atLeast"}:
                errors.append("display equation uses an unsafe fixed line rule")
        else:
            inline_formula_paragraphs.append(detail)
            if detail["lineRule"] == "exact":
                errors.append("inline equation paragraph retains exact line spacing")
    result["formulas"] = {
        "oMath_count": math_inline,
        "oMathPara_count": math_para,
        "representation": "OMML_NOT_IMAGE",
        "mathtype_status": "WORD_MANUAL_REQUIRED",
        "numbering": "STATIC_TEXT_ONLY",
        "cross_reference": "STATIC_TEXT_ONLY",
        "layout": equation_layout,
        "display_style_contract": "HFUTEquation lineRule=atLeast, line=480, before=80, after=80",
        "inline_style_contract": "HFUTBody direct lineRule=atLeast, line=360",
    }
    if math_inline < 3 or math_para < 2:
        errors.append("expected inline and two display OMML formulas")

    media = sorted(name for name in names if name.startswith("word/media/"))
    extensions = sorted({Path(name).suffix.lower() for name in media})
    extents = [
        {"cx": int(node.get("cx", "0")), "cy": int(node.get("cy", "0"))}
        for node in document.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent")
    ]
    result["figure"] = {
        "media": media,
        "extensions": extensions,
        "drawing_extents_emu": extents,
        "svg_embedded": ".svg" in extensions,
        "svg_display_blip_count": len(document.findall(".//{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip")),
        "primary_image_relationship_count": len(document.findall(".//a:blip[@r:embed]", NS)),
        "raster_fallback_present": bool(set(extensions) & {".png", ".jpg", ".jpeg"}),
        "display_representation": "INTERNAL_PNG_WORD_COMPATIBILITY_CANDIDATE",
        "caption_style_count": style_counts["HFUTFigureCaption"],
        "numbering": "STATIC_TEXT_ONLY",
        "cross_reference": "STATIC_TEXT_ONLY",
    }
    alternate_content = document.findall(".//mc:AlternateContent", NS)
    invalid_alternate_content = []
    for node in alternate_content:
        children = [local_name(child) for child in node]
        choices = node.findall("mc:Choice", NS)
        fallbacks = node.findall("mc:Fallback", NS)
        if (not choices or len(fallbacks) != 1 or children[-1:] != ["Fallback"]
                or any(not choice.get("Requires") for choice in choices)):
            invalid_alternate_content.append(children)
    result["figure"]["alternate_content_count"] = len(alternate_content)
    result["figure"]["invalid_alternate_content"] = invalid_alternate_content
    if (".png" not in extensions or ".svg" in extensions
            or style_counts["HFUTFigureCaption"] < 1 or invalid_alternate_content):
        errors.append("figure must use one embedded PNG with a valid caption and no orphan SVG")

    tables = body.findall("w:tbl", NS)
    table_details = []
    for table in tables:
        tbl_style = table.find("w:tblPr/w:tblStyle", NS)
        borders = table.find("w:tblPr/w:tblBorders", NS)
        detail = {
            "style": attr(tbl_style, "val"),
            "rows": len(table.findall("w:tr", NS)),
            "columns_first_row": len(table.findall("w:tr[1]/w:tc", NS)),
            "cell_text": [para_text(cell) for cell in table.findall(".//w:tc", NS)],
            "top": [attr(borders.find("w:top", NS) if borders is not None else None, "val"), attr(borders.find("w:top", NS) if borders is not None else None, "sz")],
            "bottom": [attr(borders.find("w:bottom", NS) if borders is not None else None, "val"), attr(borders.find("w:bottom", NS) if borders is not None else None, "sz")],
            "insideV": attr(borders.find("w:insideV", NS) if borders is not None else None, "val"),
            "header_bottom_sizes": [attr(node, "sz") for node in table.findall("w:tr[1]/w:tc/w:tcPr/w:tcBorders/w:bottom", NS)],
        }
        table_details.append(detail)
        if detail["style"] != "HFUTThreeLineTable" or detail["top"] != ["single", "8"] or detail["bottom"] != ["single", "8"] or detail["insideV"] != "nil" or set(detail["header_bottom_sizes"]) != {"4"}:
            errors.append("three-line table direct formatting mismatch")
        if not all(token in detail["cell_text"] for token in ("1.20", "2.345", "3.0", "中文1", "English 2", "中英mix 3")):
            errors.append("synthetic table cell data missing")
    result["tables"] = {
        "count": len(tables),
        "details": table_details,
        "caption_style_count": style_counts["HFUTTableCaption"],
        "conclusion": "SUPPORTED_WITH_POSTPROCESS",
        "numbering": "STATIC_TEXT_ONLY",
        "cross_reference": "STATIC_TEXT_ONLY",
    }
    if len(tables) != 1 or style_counts["HFUTTableCaption"] < 1:
        errors.append("expected one table and one table caption")

    footer_names = sorted(name for name in names if re.fullmatch(r"word/footer\d+\.xml", name))
    page_instructions = []
    for name in footer_names:
        footer_root = ET.fromstring(parts[name])
        page_instructions.extend(
            node.get(qn(W, "instr"), "") for node in footer_root.findall(".//w:fldSimple", NS)
        )
        page_instructions.extend(
            node.text or "" for node in footer_root.findall(".//w:instrText", NS)
        )
    page_field = any(re.search(r"\bPAGE\b", instruction) for instruction in page_instructions)
    result["page_field"] = {"footer_parts": footer_names, "PAGE": page_field}
    if not page_field:
        errors.append("PAGE field missing")

    unresolved = sorted(set(re.findall(r"@POC_[A-Za-z0-9_:-]+", text)))
    citation_numbers = sorted(set(re.findall(r"\[(\d+(?:[-–,]\s*\d+)*)\]", text)))
    body_before_references = text.split("参考文献", 1)[0]
    expected_body_citations = ("[1]", "[2,3]", "[4]", "[5]")
    citation_positions = [body_before_references.find(token) for token in expected_body_citations]
    body_order_pass = all(position >= 0 for position in citation_positions) and citation_positions == sorted(citation_positions)
    result["citations"] = {
        "unresolved_keys": unresolved,
        "numeric_citation_tokens": citation_numbers,
        "toolchain_test_occurrences": text.count("TOOLCHAIN TEST"),
        "reference_entry_style_count": style_counts["HFUTReferenceEntry"],
        "order_expected": [1, 2, 3, 4, 5],
        "body_citation_tokens": list(expected_body_citations),
        "body_order_pass": body_order_pass,
        "rendered_document_type_markers": sorted(set(re.findall(r"\[(?:J|M|Z|S|EB/OL)\]", text))),
    }
    if unresolved or not body_order_pass or text.count("TOOLCHAIN TEST") < 5 or style_counts["HFUTReferenceEntry"] < 5:
        errors.append("citation/reference-list validation failed")

    all_fields = []
    for name in sorted(part for part in names if part.startswith("word/") and part.endswith(".xml")):
        root = ET.fromstring(parts[name])
        all_fields.extend({"part": name, "instruction": node.get(qn(W, "instr"), "").strip()}
                          for node in root.findall(".//w:fldSimple", NS))
        all_fields.extend({"part": name, "instruction": (node.text or "").strip()}
                          for node in root.findall(".//w:instrText", NS))
    forbidden_fields = []
    for field in all_fields:
        keyword_match = re.match(r"\s*([A-Za-z]+)", field["instruction"])
        if keyword_match and keyword_match.group(1).upper() in FORBIDDEN_EXTERNAL_FIELD_TYPES:
            forbidden_fields.append(field)
    settings = ET.fromstring(parts["word/settings.xml"])
    update_fields = settings.find("w:updateFields", NS)
    open_time_update = update_fields is not None and attr(update_fields, "val", "true").lower() not in {"0", "false", "off"}
    bookmark_start_ids = [node.get(qn(W, "id"), "") for node in document.findall(".//w:bookmarkStart", NS)]
    bookmark_end_ids = [node.get(qn(W, "id"), "") for node in document.findall(".//w:bookmarkEnd", NS)]
    duplicate_bookmark_ids = sorted(value for value, count in Counter(bookmark_start_ids).items() if count > 1)
    unmatched_bookmark_ids = sorted(set(bookmark_start_ids) ^ set(bookmark_end_ids))
    doc_pr_ids = [node.get("id", "") for node in document.iter() if local_name(node) == "docPr"]
    duplicate_doc_pr_ids = sorted(value for value, count in Counter(doc_pr_ids).items() if count > 1)
    result["fields_and_bookmarks"] = {
        "all_fields": all_fields,
        "forbidden_external_fields": forbidden_fields,
        "open_time_update_enabled": open_time_update,
        "bookmark_count": len(bookmark_start_ids),
        "duplicate_bookmark_ids": duplicate_bookmark_ids,
        "unmatched_bookmark_ids": unmatched_bookmark_ids,
        "drawing_docPr_ids": doc_pr_ids,
        "duplicate_drawing_docPr_ids": duplicate_doc_pr_ids,
        "dynamic_figure_table_equation_cross_refs": False,
        "future": "WORD_FIELD_POSTPROCESS_FUTURE_OR_WORD_MANUAL",
    }
    if forbidden_fields or open_time_update:
        errors.append("external or open-time-updating field risk present")

    core = ET.fromstring(parts["docProps/core.xml"])
    creator_node = core.find("dc:creator", {"dc": "http://purl.org/dc/elements/1.1/"})
    modifier_node = core.find("cp:lastModifiedBy", {"cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"})
    creator = "" if creator_node is None or creator_node.text is None else creator_node.text
    last_modified_by = "" if modifier_node is None or modifier_node.text is None else modifier_node.text
    absolute_path_hits = []
    for name, data in parts.items():
        if re.search(rb"(?:/home/[^/]+/|[A-Za-z]:\\Users\\|/Users/[^/]+/)", data):
            absolute_path_hits.append(name)
    result["metadata"] = {
        "creator": creator,
        "lastModifiedBy": last_modified_by,
        "creator_classification": "NEUTRAL_GENERATOR" if creator in NEUTRAL_GENERATOR_IDENTITIES else "UNKNOWN",
        "lastModifiedBy_classification": "NEUTRAL_GENERATOR" if last_modified_by in NEUTRAL_GENERATOR_IDENTITIES else "UNKNOWN",
        "absolute_path_parts": sorted(set(absolute_path_hits)),
        "word_save_identity_check": "WORD_DOCUMENT_INSPECTOR_REQUIRED",
    }
    if variant == "anonymous" and (
        creator not in NEUTRAL_GENERATOR_IDENTITIES
        or last_modified_by not in NEUTRAL_GENERATOR_IDENTITIES
        or absolute_path_hits
    ):
        errors.append("anonymous metadata contains non-neutral identity or absolute path")
    if duplicate_bookmark_ids or unmatched_bookmark_ids or duplicate_doc_pr_ids:
        errors.append("bookmark or drawing ID integrity failed")

    track_changes = len(document.findall(".//w:ins", NS)) + len(document.findall(".//w:del", NS))
    comments = sorted(name for name in names if "comment" in name.lower())
    comment_nodes = 0
    for name in comments:
        try:
            comment_nodes += len(ET.fromstring(parts[name]).findall(".//w:comment", NS))
        except ET.ParseError:
            comment_nodes += 1
    embedded = sorted(name for name in names if name.startswith("word/embeddings/"))
    result["review_artifacts"] = {
        "comments_parts": comments,
        "comment_nodes": comment_nodes,
        "track_change_nodes": track_changes,
        "embedded_files": embedded,
    }
    if comment_nodes or track_changes or embedded:
        errors.append("comments, tracked changes, or embedded files present")

    relationship_parts = sorted(name for name in names if name.endswith(".rels"))
    external_relationships = []
    invalid_external_relationships = []
    missing_internal_targets = []
    duplicate_relationship_ids = []
    dangling_explicit_relationships = []
    for name in relationship_parts:
        try:
            rel_root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        rel_nodes = rel_root.findall("pr:Relationship", NS)
        rel_ids = [rel.get("Id", "") for rel in rel_nodes]
        duplicate_relationship_ids.extend(
            {"part": name, "id": rel_id}
            for rel_id, count in Counter(rel_ids).items() if count > 1
        )
        source_part = relationship_source_part(name)
        source_root = None
        used_ids: set[str] = set()
        if source_part and source_part in parts:
            source_root = ET.fromstring(parts[source_part])
            used_ids = {
                value for node in source_root.iter() for key, value in node.attrib.items()
                if key.startswith(f"{{{R}}}")
            }
        for rel in rel_nodes:
            target = rel.get("Target", "")
            rel_type = rel.get("Type", "")
            if rel.get("TargetMode") == "External":
                record = {"part": name, "target": target, "type": rel_type}
                external_relationships.append(record)
                if not (rel_type.endswith("/hyperlink") and re.match(r"^https?://", target, re.IGNORECASE)):
                    invalid_external_relationships.append(record)
            else:
                base = "" if source_part is None else posixpath.dirname(source_part)
                resolved = posixpath.normpath(posixpath.join(base, target))
                if resolved not in parts:
                    missing_internal_targets.append({"part": name, "id": rel.get("Id", ""), "target": target})
            if source_root is not None and (rel_type.endswith("/image") or rel_type.endswith("/hyperlink")) and rel.get("Id") not in used_ids:
                dangling_explicit_relationships.append({"part": name, "id": rel.get("Id", ""), "target": target})
    result["relationships"] = {
        "parts": relationship_parts,
        "external": external_relationships,
        "invalid_external": invalid_external_relationships,
        "missing_internal_targets": missing_internal_targets,
        "duplicate_ids": duplicate_relationship_ids,
        "dangling_explicit": dangling_explicit_relationships,
    }
    if invalid_external_relationships or missing_internal_targets or duplicate_relationship_ids or dangling_explicit_relationships:
        errors.append("relationship integrity failed")

    content_types = ET.fromstring(parts["[Content_Types].xml"])
    present_parts = set(names)
    missing_content_type_targets = sorted(
        node.get("PartName", "")
        for node in content_types.findall("ct:Override", NS)
        if node.get("PartName", "").lstrip("/") not in present_parts
    )
    result["content_types"] = {"missing_override_targets": missing_content_type_targets}
    if missing_content_type_targets:
        errors.append("content-type override targets missing")

    ordering = {
        "pPr": order_violations(document.findall(".//w:pPr", NS), PPR_ORDER),
        "rPr": order_violations(document.findall(".//w:rPr", NS), RPR_ORDER),
        "sectPr": order_violations(document.findall(".//w:sectPr", NS), SECTPR_ORDER),
        "tblPr": order_violations(document.findall(".//w:tblPr", NS), TBLPR_ORDER),
        "style": order_violations(style_nodes, STYLE_ORDER),
        "numbering_lvl": order_violations(numbering.findall(".//w:lvl", NS), LVL_ORDER),
    }
    result["schema_ordering"] = ordering
    if any(ordering.values()):
        errors.append("WordprocessingML child ordering failed")

    anonymous_hits = []
    if variant == "anonymous":
        for token in FORBIDDEN_ANONYMOUS:
            for name, data in parts.items():
                if token.encode("utf-8") in data or token in name:
                    anonymous_hits.append({"token": token, "part": name})
        if anonymous_hits:
            errors.append("anonymous identity scan found forbidden tokens")
        if "ANONYMIZED_POC_CANDIDATE" not in text:
            errors.append("anonymous candidate marker missing")
    else:
        for token in FORBIDDEN_ANONYMOUS[:3]:
            if token not in text:
                errors.append(f"full POC identity token missing: {token}")
    result["anonymization"] = {
        "forbidden_hits": anonymous_hits,
        "status": "ANONYMIZED_POC_CANDIDATE" if variant == "anonymous" and not anonymous_hits else "FULL_SYNTHETIC_IDENTITY_POC",
        "word_document_inspector": "NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED",
    }

    result["errors"] = errors
    result["verdict"] = "PASS" if not errors else "FAIL"
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--variant", required=True, choices=("full", "anonymous"))
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result, errors = inspect(args.docx, args.variant)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
