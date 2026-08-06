#!/usr/bin/env python3
"""Read-only Phase 2.5 journal-format regression audit for canonical/v6 DOCX.

The audit uses only the Python standard library.  It does not repair or rewrite
any DOCX.  Its repository CSV output is the governance-facing regression
matrix; the detailed JSON is written to the external derived audit tree by
default.  A blocking, unauthorized regression deliberately returns exit 1.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from xml.etree import ElementTree as ET
import zipfile


REPO = Path(__file__).resolve().parents[2]
STYLE_MAP_DEFAULT = REPO / "docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv"
MATRIX_DEFAULT = REPO / "docs/paper/phase2_5/PAPER_PHASE2_5_JOURNAL_FORMAT_REGRESSION_MATRIX_v1.0.csv"
EXTERNAL_AUDIT_ROOT = Path(
    "/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/"
    "step7f_journal_format_regression_audit_v1"
)
JSON_DEFAULT = EXTERNAL_AUDIT_ROOT / "audit_hfut_format_regression_v1.0.json"

EXPECTED_SHA256 = {
    "reference": "c378063a04e18b8c1af261d00313fe58305636a5bc9833663644ce3e4d38a7c6",
    "full": "aef3335e7f726c58a932852e29cd0c0e6808ae264b41b08c51e0fb9a01f83cdf",
    "anonymous": "cc4b105ff6fe950bb871a129b53c983426a22bd63e536bcdf63c393e638faa43",
}

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
VT = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
NS = {"w": W, "m": M, "r": R, "a": A, "wp": WP, "cp": CP, "dc": DC, "vt": VT}

MATRIX_FIELDS = [
    "audit_id", "rule_id", "source_id", "source_authority", "requirement",
    "requirement_class", "target_part_or_style", "expected_value",
    "actual_value_full", "actual_value_anonymous", "actual_source",
    "automatic_result", "visual_result", "windows_result", "compliance_status",
    "governance_status", "blocking_for_phase2_5", "blocking_for_phase3",
    "required_action", "notes",
]


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def wattr(node: ET.Element | None, name: str, default: str = "") -> str:
    return default if node is None else node.get(qn(W, name), default)


def local_name(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xml(parts: dict[str, bytes], name: str) -> ET.Element:
    return ET.fromstring(parts[name])


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def paragraph_record(paragraph: ET.Element) -> dict[str, Any]:
    ppr = paragraph.find("w:pPr", NS)
    style = wattr(ppr.find("w:pStyle", NS) if ppr is not None else None, "val")
    num_pr = ppr.find("w:numPr", NS) if ppr is not None else None
    spacing = ppr.find("w:spacing", NS) if ppr is not None else None
    return {
        "text": paragraph_text(paragraph),
        "style": style,
        "direct_numPr": None if num_pr is None else {
            "ilvl": wattr(num_pr.find("w:ilvl", NS), "val"),
            "numId": wattr(num_pr.find("w:numId", NS), "val"),
        },
        "direct_spacing": None if spacing is None else {
            key: wattr(spacing, key) for key in ("lineRule", "line", "before", "after")
        },
        "keepNext": ppr is not None and ppr.find("w:keepNext", NS) is not None,
        "keepLines": ppr is not None and ppr.find("w:keepLines", NS) is not None,
        "pageBreakBefore": ppr is not None and ppr.find("w:pageBreakBefore", NS) is not None,
        "omath": len(paragraph.findall(".//m:oMath", NS)),
        "omathPara": len(paragraph.findall(".//m:oMathPara", NS)),
        "drawings": len(paragraph.findall(".//w:drawing", NS)),
    }


def properties(root: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for node in root:
        name = node.get("name") or local_name(node)
        value = "".join(node.itertext()).strip()
        result[name] = value
    return result


def style_record(style: ET.Element) -> dict[str, Any]:
    ppr = style.find("w:pPr", NS)
    rpr = style.find("w:rPr", NS)
    fonts = rpr.find("w:rFonts", NS) if rpr is not None else None
    spacing = ppr.find("w:spacing", NS) if ppr is not None else None
    indent = ppr.find("w:ind", NS) if ppr is not None else None
    based = style.find("w:basedOn", NS)
    tbl_pr = style.find("w:tblPr", NS)
    tbl_borders = tbl_pr.find("w:tblBorders", NS) if tbl_pr is not None else None
    tbl_margin = tbl_pr.find("w:tblCellMar", NS) if tbl_pr is not None else None

    def style_border(edge: str) -> dict[str, str]:
        node = tbl_borders.find(f"w:{edge}", NS) if tbl_borders is not None else None
        return {"val": wattr(node, "val"), "sz": wattr(node, "sz")}

    return {
        "style_id": wattr(style, "styleId"),
        "type": wattr(style, "type"),
        "basedOn": wattr(based, "val") if based is not None else "",
        "fonts": {} if fonts is None else {
            key: wattr(fonts, key) for key in ("eastAsia", "ascii", "hAnsi", "cs")
        },
        "size_half_points": wattr(rpr.find("w:sz", NS) if rpr is not None else None, "val"),
        "bold": rpr is not None and rpr.find("w:b", NS) is not None,
        "italic": rpr is not None and rpr.find("w:i", NS) is not None,
        "alignment": wattr(ppr.find("w:jc", NS) if ppr is not None else None, "val"),
        "indent": {} if indent is None else {
            key: wattr(indent, key) for key in ("firstLine", "hanging", "left", "right")
        },
        "spacing": {} if spacing is None else {
            key: wattr(spacing, key) for key in ("lineRule", "line", "before", "after")
        },
        "keepNext": ppr is not None and ppr.find("w:keepNext", NS) is not None,
        "keepLines": ppr is not None and ppr.find("w:keepLines", NS) is not None,
        "numbering": None if ppr is None or ppr.find("w:numPr", NS) is None else {
            "ilvl": wattr(ppr.find("w:numPr/w:ilvl", NS), "val"),
            "numId": wattr(ppr.find("w:numPr/w:numId", NS), "val"),
        },
        "table_properties": None if tbl_pr is None else {
            "children": [local_name(node) for node in tbl_pr],
            "layout": wattr(tbl_pr.find("w:tblLayout", NS), "type")
            if tbl_pr.find("w:tblLayout", NS) is not None else "ABSENT",
            "borders": {edge: style_border(edge) for edge in
                        ("top", "left", "bottom", "right", "insideH", "insideV")},
            "cell_margins": {} if tbl_margin is None else {
                edge: {"w": wattr(tbl_margin.find(f"w:{edge}", NS), "w"),
                       "type": wattr(tbl_margin.find(f"w:{edge}", NS), "type")}
                for edge in ("top", "left", "bottom", "right")
            },
            "conditional_first_row_borders": [
                {edge: {"val": wattr(node.find(f"w:tblPr/w:tblBorders/w:{edge}", NS), "val"),
                        "sz": wattr(node.find(f"w:tblPr/w:tblBorders/w:{edge}", NS), "sz")}
                 for edge in ("top", "left", "bottom", "right", "insideH", "insideV")}
                for node in style.findall("w:tblStylePr", NS)
                if wattr(node, "type") == "firstRow"
            ],
        },
    }


def table_record(table: ET.Element) -> dict[str, Any]:
    tbl_pr = table.find("w:tblPr", NS)
    tbl_width = tbl_pr.find("w:tblW", NS) if tbl_pr is not None else None
    layout = tbl_pr.find("w:tblLayout", NS) if tbl_pr is not None else None
    borders = tbl_pr.find("w:tblBorders", NS) if tbl_pr is not None else None
    margin = tbl_pr.find("w:tblCellMar", NS) if tbl_pr is not None else None

    def border(edge: str) -> dict[str, str]:
        node = borders.find(f"w:{edge}", NS) if borders is not None else None
        return {"val": wattr(node, "val"), "sz": wattr(node, "sz")}

    direct_cell_margins = []
    run_fonts = []
    for cell in table.findall(".//w:tc", NS):
        cell_margin = cell.find("w:tcPr/w:tcMar", NS)
        if cell_margin is not None:
            direct_cell_margins.append({
                edge: {
                    "w": wattr(cell_margin.find(f"w:{edge}", NS), "w"),
                    "type": wattr(cell_margin.find(f"w:{edge}", NS), "type"),
                } for edge in ("top", "left", "bottom", "right")
            })
        for rpr in cell.findall(".//w:rPr", NS):
            fonts = rpr.find("w:rFonts", NS)
            size = rpr.find("w:sz", NS)
            if fonts is not None or size is not None:
                run_fonts.append({
                    "eastAsia": wattr(fonts, "eastAsia"),
                    "ascii": wattr(fonts, "ascii"),
                    "size_half_points": wattr(size, "val"),
                })
    return {
        "style": wattr(tbl_pr.find("w:tblStyle", NS) if tbl_pr is not None else None, "val"),
        "tblW": {"w": wattr(tbl_width, "w"), "type": wattr(tbl_width, "type")},
        "layout": wattr(layout, "type") if layout is not None else "ABSENT",
        "gridCol_twips": [wattr(node, "w") for node in table.findall("w:tblGrid/w:gridCol", NS)],
        "borders": {edge: border(edge) for edge in ("top", "left", "bottom", "right", "insideH", "insideV")},
        "tblCellMar": {} if margin is None else {
            edge: wattr(margin.find(f"w:{edge}", NS), "w") for edge in ("top", "left", "bottom", "right")
        },
        "direct_cell_margins": direct_cell_margins,
        "direct_run_fonts": run_fonts,
        "rows": len(table.findall("w:tr", NS)),
        "cells": len(table.findall(".//w:tc", NS)),
    }


def inspect_docx(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as package:
        bad_member = package.testzip()
        names = package.namelist()
        parts = {name: package.read(name) for name in names}
    document = xml(parts, "word/document.xml")
    styles_root = xml(parts, "word/styles.xml")
    settings = xml(parts, "word/settings.xml")
    body = document.find("w:body", NS)
    if body is None:
        raise ValueError(f"{path}: missing w:body")
    paragraph_nodes = body.findall(".//w:p", NS)
    paragraphs = [paragraph_record(node) for node in paragraph_nodes]
    styles = {
        wattr(node, "styleId"): style_record(node)
        for node in styles_root.findall("w:style", NS)
        if wattr(node, "styleId").startswith("HFUT")
    }
    sections = []
    for section in document.findall(".//w:sectPr", NS):
        pg = section.find("w:pgSz", NS)
        mar = section.find("w:pgMar", NS)
        cols = section.find("w:cols", NS)
        stype = section.find("w:type", NS)
        sections.append({
            "type": wattr(stype, "val") if stype is not None else "nextPage(default)",
            "page": {"w": wattr(pg, "w"), "h": wattr(pg, "h"), "orient": wattr(pg, "orient")},
            "margins": {key: wattr(mar, key) for key in ("top", "right", "bottom", "left", "header", "footer", "gutter")},
            "columns": {"num": wattr(cols, "num", "1"), "space": wattr(cols, "space")},
            "titlePg": section.find("w:titlePg", NS) is not None,
        })
    drawings = []
    for extent in document.findall(".//wp:extent", NS):
        cx = int(extent.get("cx", "0")); cy = int(extent.get("cy", "0"))
        drawings.append({
            "cx_emu": cx, "cy_emu": cy,
            "width_cm": round(cx / 360000, 4), "height_cm": round(cy / 360000, 4),
        })
    footer_parts = sorted(name for name in names if re.fullmatch(r"word/footer\d+\.xml", name))
    fields = []
    for name in sorted(name for name in names if name.startswith("word/") and name.endswith(".xml")):
        root = ET.fromstring(parts[name])
        fields.extend({"part": name, "instruction": wattr(node, "instr").strip()}
                      for node in root.findall(".//w:fldSimple", NS))
        fields.extend({"part": name, "instruction": (node.text or "").strip()}
                      for node in root.findall(".//w:instrText", NS))
    update_fields = settings.find("w:updateFields", NS)
    result = {
        "path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size,
        "zip_test": "PASS" if bad_member is None else f"FAIL:{bad_member}",
        "package_parts": names, "part_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in parts.items()},
        "sections": sections, "styles": styles, "paragraphs": paragraphs,
        "style_usage": dict(sorted(Counter(row["style"] for row in paragraphs if row["style"]).items())),
        "drawings": drawings, "tables": [table_record(node) for node in body.findall("w:tbl", NS)],
        "fields": fields, "footer_parts": footer_parts,
        "settings": {
            "updateFields_present": update_fields is not None,
            "updateFields_value": wattr(update_fields, "val") if update_fields is not None else "ABSENT",
        },
        "core_properties": properties(xml(parts, "docProps/core.xml")) if "docProps/core.xml" in parts else {},
        "custom_properties": properties(xml(parts, "docProps/custom.xml")) if "docProps/custom.xml" in parts else {},
        "page_breaks": [wattr(node, "type", "textWrapping") for node in document.findall(".//w:br", NS)],
        "openxml_parts": parts,
    }
    return result


def read_style_map(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty Style Map: {path}")
    by_id = {row["style_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Style Map contains duplicate style_id values")
    return rows, by_id


def validation_history(full_path: Path) -> dict[str, Any]:
    validation_dir = full_path.parents[2] / "validation"
    files = {
        "reference": validation_dir / "reference_fixed_openxml_errors.json",
        "full": validation_dir / "v6_full_openxml_errors.json",
        "anonymous": validation_dir / "v6_anonymous_openxml_errors.json",
    }
    result: dict[str, Any] = {"validation_dir": str(validation_dir), "files": {}}
    for key, path in files.items():
        if not path.exists():
            result["files"][key] = {"path": str(path), "status": "MISSING"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        result["files"][key] = {
            "path": str(path), "validator": payload.get("validator"),
            "package_version": payload.get("package_version"),
            "target_file_format": payload.get("target_file_format"),
            "error_count": payload.get("error_count"),
            "status": "PASS" if payload.get("error_count") == 0 else "FAIL",
        }
    return result


def normalized_common_paragraphs(doc: dict[str, Any]) -> list[dict[str, Any]]:
    identity_styles = {
        "HFUTAuthorsCN", "HFUTAuthorsEN", "HFUTAffiliationCN", "HFUTAffiliationEN",
        "HFUTFunding", "HFUTAuthorBiography", "HFUTAcknowledgement",
    }
    identity_text = (
        "POC测试作者", "POC测试单位", "POC SYNTHETIC AUTHOR", "POC Synthetic Unit",
        "poc@example.invalid", "基金测试字段", "作者简介测试字段", "致谢测试字段",
        "ANONYMIZED_POC_CANDIDATE", "NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED",
    )
    result = []
    for row in doc["paragraphs"]:
        if row["style"] in identity_styles or any(token in row["text"] for token in identity_text):
            continue
        result.append(row)
    return result


def compare_variants(full: dict[str, Any], anonymous: dict[str, Any]) -> dict[str, Any]:
    full_parts = set(full["package_parts"]); anon_parts = set(anonymous["package_parts"])
    identity_parts = {"word/document.xml", "docProps/core.xml", "docProps/custom.xml"}
    common_nonidentity = sorted((full_parts & anon_parts) - identity_parts)
    differing = [name for name in common_nonidentity
                 if full["part_sha256"][name] != anonymous["part_sha256"][name]]
    normalized_equal = normalized_common_paragraphs(full) == normalized_common_paragraphs(anonymous)
    return {
        "member_sets_equal": full_parts == anon_parts,
        "full_only_parts": sorted(full_parts - anon_parts),
        "anonymous_only_parts": sorted(anon_parts - full_parts),
        "identity_related_parts": sorted(identity_parts),
        "nonidentity_parts_compared": common_nonidentity,
        "nonidentity_part_differences": differing,
        "nonidentity_parts_equal": not differing,
        "normalized_nonidentity_document_equal": normalized_equal,
    }


def compact(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_matrix(reference: dict[str, Any], full: dict[str, Any], anonymous: dict[str, Any],
                 style_map: dict[str, dict[str, str]], history: dict[str, Any],
                 variant_compare: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(audit_id: str, rule_id: str, source_id: str, source_authority: str,
            requirement: str, requirement_class: str, target: str, expected: Any,
            actual_full: Any, actual_anon: Any, actual_source: str, automatic: str,
            visual: str, windows: str, compliance: str, governance: str,
            block25: str, block3: str, action: str, notes: str = "") -> None:
        values = [audit_id, rule_id, source_id, source_authority, requirement,
                  requirement_class, target, compact(expected), compact(actual_full),
                  compact(actual_anon), actual_source, automatic, visual, windows,
                  compliance, governance, block25, block3, action, notes]
        rows.append(dict(zip(MATRIX_FIELDS, values)))

    fs = full["styles"]; ans = anonymous["styles"]
    fp = full["paragraphs"]; ap = anonymous["paragraphs"]
    fref = next(row for row in fp if row["text"] == "参考文献")
    aref = next(row for row in ap if row["text"] == "参考文献")
    ref_map = style_map["HFUTReferenceHeading"]
    eq_map = style_map["HFUTEquation"]
    table_map = style_map["HFUTThreeLineTable"]
    ftable = full["tables"][0]; atable = anonymous["tables"][0]
    fidentity_styles = {key: full["style_usage"].get(key, 0) for key in (
        "HFUTAuthorsCN", "HFUTAuthorsEN", "HFUTAffiliationCN", "HFUTAffiliationEN",
        "HFUTFunding", "HFUTAuthorBiography", "HFUTAcknowledgement")}
    aidentity_styles = {key: anonymous["style_usage"].get(key, 0) for key in fidentity_styles}
    validator_result = {key: item.get("error_count") for key, item in history["files"].items()}

    add("JFR-001", "HFUT-WEB-032", "HFUT_FMT_DOC", "STYLE_EVIDENCE_CONFIRMED",
        "A4 portrait page geometry", "STYLE_EMBEDDED", "word/document.xml sectPr/pgSz",
        {"w": "11906", "h": "16838"}, full["sections"], anonymous["sections"], "DOCX OOXML",
        "PASS", "LibreOffice preview reports A4", "WINDOWS_FINAL_REQUIRED",
        "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT", "NO", "NO", "Retain and recheck in final Word output")
    add("JFR-002", "HFUT-FMT-028", "HFUT_FMT_DOC", "STYLE_EVIDENCE_CONFIRMED",
        "Margins 1361/1304/1134/1304 twips; gutter 0", "STYLE_EMBEDDED", "sectPr/pgMar",
        {"top": "1361", "right": "1304", "bottom": "1134", "left": "1304", "gutter": "0"},
        full["sections"], anonymous["sections"], "DOCX OOXML", "PASS", "A4 preview consistent",
        "WINDOWS_FINAL_REQUIRED", "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT", "NO", "NO",
        "Retain and recheck in final Word output")
    add("JFR-003", "HFUT-AUDIT-COLUMNS", "HFUT_FMT_DOC", "STYLE_EVIDENCE_CONFIRMED",
        "Single-column front matter to two-column body; 425-twip gap", "PROJECT_DERIVED_CANDIDATE",
        "sectPr/type and cols", [{"num": "1", "space": "425"}, {"num": "2", "space": "425"}],
        full["sections"], anonymous["sections"], "DOCX OOXML", "PASS",
        "LibreOffice preview shows page-2 two-column body", "WINDOWS_FINAL_REQUIRED",
        "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT", "NO", "NO", "Retain candidate; Word final review")
    add("JFR-004", "HFUT-AUDIT-PAGE", "REFERENCE_DOCX_DESIGN", "PROJECT_DERIVED_CANDIDATE",
        "Footer carries PAGE field without page-number restart", "PROJECT_DERIVED_CANDIDATE",
        "word/footer*.xml; sectPr/pgNumType", "PAGE present; pgNumType absent",
        full["fields"], anonymous["fields"], "DOCX OOXML", "PASS",
        "LibreOffice preview shows pages 1 and 2", "WINDOWS_FINAL_REQUIRED",
        "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT", "NO", "NO", "Refresh/check PAGE manually in Word")
    add("JFR-005", "HFUT-FMT-001", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Chinese title semantic role and <=20-character content rule", "TEXTUALLY_EXPLICIT",
        "HFUTTitleCN", "Style used; final title <=20 Chinese characters",
        full["style_usage"].get("HFUTTitleCN", 0), anonymous["style_usage"].get("HFUTTitleCN", 0),
        "DOCX style usage", "PASS", "Synthetic title only", "FINAL_CONTENT_PENDING",
        "FINAL_CONTENT_PENDING", "NO_DRIFT", "NO", "YES", "Validate real title during Phase 3")
    add("JFR-006", "HFUT-FMT-008", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "English title corresponds to Chinese and uses required capitalization", "TEXTUALLY_EXPLICIT",
        "HFUTTitleEN", "Style used; bilingual semantic review",
        full["style_usage"].get("HFUTTitleEN", 0), anonymous["style_usage"].get("HFUTTitleEN", 0),
        "DOCX style usage", "PASS", "Synthetic title only", "FINAL_CONTENT_PENDING",
        "FINAL_CONTENT_PENDING", "NO_DRIFT", "NO", "YES", "Validate real bilingual title during Phase 3")
    add("JFR-007", "HFUT-FMT-002;HFUT-FMT-009", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Full includes author/affiliation roles; Anonymous omits identity roles", "TEXTUALLY_EXPLICIT",
        "HFUTAuthors*/HFUTAffiliation*", "Full used; Anonymous absent", fidentity_styles, aidentity_styles,
        "DOCX style usage", "PASS", "Synthetic identity only", "WINDOWS_FINAL_REQUIRED",
        "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT", "NO", "NO", "Populate only verified real identity in final Full")
    add("JFR-008", "HFUT-WEB-025;HFUT-WEB-026;HFUT-WEB-031", "HFUT_WEB_EXCERPT_PDF",
        "TEXTUALLY_EXPLICIT_REQUIREMENT", "Author biography must be in first-page footer; funding conditional; acknowledgement governed",
        "TEXTUALLY_EXPLICIT", "first-page footer versus body paragraphs", "Biography in first-page footer",
        "Funding/biography/acknowledgement are ordinary body paragraphs; footer contains PAGE only",
        "Identity roles omitted; footer contains PAGE only", "DOCX paragraph and footer inspection", "FAIL",
        "LibreOffice preview places all three in first-page body flow", "NOT_TESTED_IN_MICROSOFT_WORD_V6",
        "POC_NOT_COVERED", "NO_DRIFT", "YES", "NO", "Design and run a minimal first-page-footer POC before Phase 2.5 closeout",
        "No claim is made that funding or acknowledgement share the biography footer rule")
    add("JFR-009", "HFUT-FMT-003", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Chinese abstract label/body fonts and 14-pt line spacing", "TEXTUALLY_EXPLICIT",
        "HFUTAbstractLabelCN/HFUTAbstractBodyCN", "9 pt Heiti/Songti; exact 14 pt",
        {key: fs[key] for key in ("HFUTAbstractLabelCN", "HFUTAbstractBodyCN")},
        {key: ans[key] for key in ("HFUTAbstractLabelCN", "HFUTAbstractBodyCN")}, "DOCX styles.xml",
        "PASS", "Synthetic content renders", "WINDOWS_FINAL_REQUIRED", "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT",
        "NO", "NO", "Retain styles and validate final abstract")
    add("JFR-010", "HFUT-FMT-010", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "English abstract five-size Times New Roman and semantic equivalence", "TEXTUALLY_EXPLICIT",
        "HFUTAbstractBodyEN", "10.5 pt Times New Roman; final bilingual review", fs["HFUTAbstractBodyEN"],
        ans["HFUTAbstractBodyEN"], "DOCX styles.xml", "PASS", "Synthetic content only", "FINAL_CONTENT_PENDING",
        "FINAL_CONTENT_PENDING", "NO_DRIFT", "NO", "YES", "Validate real bilingual abstract")
    add("JFR-011", "HFUT-WEB-009;HFUT-WEB-010;HFUT-FMT-005;HFUT-FMT-011", "HFUT_WEB_EXCERPT_PDF;HFUT_FMT_DOC",
        "TEXTUALLY_EXPLICIT_REQUIREMENT", "Bilingual keyword styles; >=4 Chinese keywords; paired order",
        "TEXTUALLY_EXPLICIT", "HFUTKeywords*", "Required styles used; final content pending",
        {key: full["style_usage"].get(key, 0) for key in fs if key.startswith("HFUTKeywords")},
        {key: anonymous["style_usage"].get(key, 0) for key in ans if key.startswith("HFUTKeywords")},
        "DOCX style usage", "PASS", "Four synthetic keywords", "FINAL_CONTENT_PENDING", "FINAL_CONTENT_PENDING",
        "NO_DRIFT", "NO", "YES", "Validate final keyword meaning/count/order")
    add("JFR-012", "HFUT-FMT-006", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Chinese Library Classification field exists", "TEXTUALLY_EXPLICIT", "HFUTClassification",
        "Field/style present; real value required", full["style_usage"].get("HFUTClassification", 0),
        anonymous["style_usage"].get("HFUTClassification", 0), "DOCX style usage", "PASS",
        "Placeholder only", "FINAL_CONTENT_PENDING", "FINAL_CONTENT_PENDING", "NO_DRIFT", "NO", "YES",
        "Determine and author-confirm final classification")
    add("JFR-013", "HFUT-FMT-012", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Body Chinese Songti and Latin Times New Roman at 10.5 pt", "TEXTUALLY_EXPLICIT",
        "HFUTBody", "宋体/Times New Roman; 10.5 pt", fs["HFUTBody"], ans["HFUTBody"],
        "DOCX styles.xml", "PASS", "Preview supports candidate", "WINDOWS_FINAL_REQUIRED",
        "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT", "NO", "NO", "Retain and scan final direct formatting")
    add("JFR-014", "HFUT-FMT-028", "HFUT_FMT_DOC", "STYLE_EVIDENCE_CONFIRMED",
        "Body first-line 200 twips and exact 16-pt spacing", "PROJECT_DERIVED_CANDIDATE",
        "HFUTBody", "firstLine=200; exact 320 twips", fs["HFUTBody"], ans["HFUTBody"],
        "Style Map plus DOCX styles.xml", "PASS", "Preview supports candidate", "WINDOWS_FINAL_REQUIRED",
        "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT", "NO", "NO", "Retain project-derived candidate")
    add("JFR-015", "HFUT-FMT-013", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Introduction numbered 0 and uses level-1 heading role", "TEXTUALLY_EXPLICIT",
        "HFUTIntroHeading/numPr", "numId=2 ilvl=0; rendered 0",
        [row for row in fp if row["style"] == "HFUTIntroHeading"],
        [row for row in ap if row["style"] == "HFUTIntroHeading"], "DOCX document.xml/numbering.xml",
        "PASS", "LibreOffice preview displays 0", "WINDOWS_FINAL_REQUIRED", "PASS_TEXTUALLY_EXPLICIT",
        "NO_DRIFT", "NO", "NO", "Retest edit/restart behavior in Word")
    add("JFR-016", "HFUT-FMT-013;HFUT-FMT-014;HFUT-FMT-015;HFUT-FMT-016", "HFUT_FMT_DOC",
        "TEXTUALLY_EXPLICIT_REQUIREMENT", "Three heading levels: numbering/font/size and keep-next candidate",
        "TEXTUALLY_EXPLICIT_AND_STYLE_EVIDENCE", "HFUTHeading1/2/3", "1/1.1/1.1.1; Heiti/Heiti/Kaiti; 14/10.5/10.5 pt",
        {key: fs[key] for key in ("HFUTHeading1", "HFUTHeading2", "HFUTHeading3")},
        {key: ans[key] for key in ("HFUTHeading1", "HFUTHeading2", "HFUTHeading3")}, "DOCX styles.xml/numbering.xml",
        "PASS", "LibreOffice preview displays all three levels", "WINDOWS_FINAL_REQUIRED",
        "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT", "NO", "NO", "Word final no-wrap/keep-next check")
    add("JFR-017", "HFUT-FMT-018", "HFUT_FMT_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Equations are entered and editable with MathType", "TEXTUALLY_EXPLICIT", "equation objects",
        "Editable MathType objects", "3 OMML objects; no MathType embedding", "3 OMML objects; no MathType embedding",
        "DOCX OMML/embeddings inspection", "FAIL", "OMML visible and historically editable in Word",
        "WINDOWS_FINAL_REQUIRED", "WINDOWS_FINAL_REQUIRED", "NO_DRIFT", "NO", "NO",
        "Convert/rebuild final equations in MathType during publication-asset stage")
    add("JFR-018", "HFUT-AUDIT-EQUATION-STYLE", "WORD_V3_MANUAL_RESULT", "VALIDATED_WORD_RESULT",
        "Display equation spacing avoids clipping/overlap", "PROJECT_DERIVED_CANDIDATE", "HFUTEquation",
        "Style Map says exact 16 pt, 0/0; validated v6 uses atLeast 480, 80/80",
        {"style_map": {key: eq_map[key] for key in ("line_spacing_rule", "line_spacing_value", "space_before_pt", "space_after_pt")}, "actual": fs["HFUTEquation"]},
        {"style_map": {key: eq_map[key] for key in ("line_spacing_rule", "line_spacing_value", "space_before_pt", "space_after_pt")}, "actual": ans["HFUTEquation"]},
        "Style Map; v6 styles.xml; Word v3 manual result", "PASS", "Word-export evidence found no clipping/overlap",
        "WORD_RESULT_SUPPORTS_CANDIDATE", "PASS_PROJECT_DERIVED_CANDIDATE", "GOVERNANCE_DRIFT", "YES", "NO",
        "Keep v6 spacing; reconcile Style Map/Design/Report instead of restoring unsafe exact spacing")
    add("JFR-019", "HFUT-FIG-002", "HFUT_FIG_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Single-column figure width <=7.5 cm", "TEXTUALLY_EXPLICIT", "wp:extent", "<=7.5 cm",
        full["drawings"], anonymous["drawings"], "DOCX drawing extent", "PASS",
        "Figure visible in preview", "WINDOWS_FINAL_REQUIRED", "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT",
        "NO", "NO", "Validate every final figure extent")
    add("JFR-020", "HFUT-FIG-009;HFUT-FIG-010;HFUT-FIG-017", "HFUT_FIG_DOC", "TEXTUALLY_EXPLICIT_AND_EXAMPLE",
        "Figure called out before placement; continuous number; caption candidate", "MIXED_AUTHORITY",
        "HFUTFigureCaption and paragraph order", "Callout precedes figure; static Figure 1 candidate",
        full["style_usage"].get("HFUTFigureCaption", 0), anonymous["style_usage"].get("HFUTFigureCaption", 0),
        "DOCX paragraph order/style usage", "PASS", "Preview confirms order/caption", "WINDOWS_FINAL_REQUIRED",
        "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT", "NO", "NO", "Final numbering and caption review; do not elevate caption example")
    add("JFR-021", "HFUT-FIG-005;HFUT-FIG-006;HFUT-FIG-007;HFUT-FIG-008", "HFUT_FIG_DOC",
        "TEXTUALLY_EXPLICIT_REQUIREMENT", "Origin/Visio figures remain editable and are not screenshots", "TEXTUALLY_EXPLICIT",
        "embedded figure objects", "Editable Origin/Visio where applicable", "PNG fallback only", "PNG fallback only",
        "DOCX media/embeddings inspection", "FAIL", "PNG displays", "WINDOWS_FINAL_REQUIRED",
        "POC_NOT_COVERED", "NO_DRIFT", "NO", "NO", "Validate final publication assets with Origin/Visio")
    add("JFR-022", "HFUT-WEB-018;HFUT-TBL-003;HFUT-TBL-004", "HFUT_WEB_EXCERPT_PDF;HFUT_TABLE_DOC",
        "TEXTUALLY_EXPLICIT_REQUIREMENT", "Three-line table with top/bottom 1 pt and header rule 0.5 pt", "TEXTUALLY_EXPLICIT",
        "table direct borders", "top/bottom sz=8; header-cell bottom sz=4; no verticals", ftable, atable,
        "DOCX table properties", "PASS", "Preview visually shows three-line candidate", "WINDOWS_FINAL_REQUIRED",
        "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT", "NO", "NO", "Retain direct border enforcement")
    add("JFR-023", "HFUT-TBL-005;HFUT-TBL-012", "HFUT_TABLE_DOC", "TEXT_AND_STYLE_EVIDENCE",
        "Table content 7.5 pt Songti/TNR; cell-margin candidate", "TEXTUALLY_EXPLICIT_AND_PROJECT_DERIVED",
        "HFUTTableContent/table cells", "7.5 pt Songti/TNR; margin evidence 108/0 twips",
        {"content_style": fs["HFUTTableContent"], "table_style": fs["HFUTThreeLineTable"], "table": ftable},
        {"content_style": ans["HFUTTableContent"], "table_style": ans["HFUTThreeLineTable"], "table": atable},
        "DOCX styles.xml/document.xml", "PASS", "Preview supports candidate", "WINDOWS_FINAL_REQUIRED",
        "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT", "NO", "NO", "Validate final table fonts and cell margins")
    add("JFR-024", "HFUT-AUDIT-TABLE-CONTRACT", "REFERENCE_STYLE_MAP;REFERENCE_DOCX_DESIGN",
        "PROJECT_GOVERNANCE", "Table inheritance and layout strategy remain synchronized", "PROJECT_DERIVED_CANDIDATE",
        "HFUTThreeLineTable basedOn; tblPr/tblW/tblLayout/gridCol", "Style Map based_on=TableNormal; earlier specimen fixed layout",
        {"style_map_based_on": table_map["based_on"], "actual_based_on": fs["HFUTThreeLineTable"]["basedOn"], "table": ftable},
        {"style_map_based_on": table_map["based_on"], "actual_based_on": ans["HFUTThreeLineTable"]["basedOn"], "table": atable},
        "Style Map; canonical/v6 styles.xml; v6 document.xml", "FAIL", "Stable preview candidate",
        "WORD_RESULT_SUPPORTS_DIRECT_LAYOUT", "PASS_PROJECT_DERIVED_CANDIDATE", "GOVERNANCE_DRIFT", "YES", "NO",
        "Record removed inheritance/fixed layout and direct tblW/gridCol/border dependency in Style Map and Design")
    add("JFR-025", "HFUT-AUDIT-REFERENCE-HEADING-STYLE", "REFERENCE_STYLE_MAP", "PROJECT_GOVERNANCE",
        "Reference heading uses HFUTReferenceHeading", "PROJECT_DERIVED_CANDIDATE", "reference heading paragraph style",
        "HFUTReferenceHeading", fref["style"], aref["style"], "DOCX document.xml", "PASS",
        "Preview shows reference heading", "WINDOWS_FINAL_REQUIRED", "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT",
        "NO", "NO", "Retain semantic style")
    add("JFR-026", "HFUT-AUDIT-REFERENCE-HEADING-NUMBERING", "HFUT_WEB_EXCERPT_PDF;HFUT_REF_DOC",
        "NO_SOURCE_AUTHORIZATION_FOUND", "Reference heading must not inherit unauthorized body-heading numbering",
        "PROJECT_GOVERNANCE", "reference heading pPr/numPr and Style Map numbering_level", "No direct numPr; Style Map numbering_level blank",
        {"paragraph": fref, "style_map_numbering_level": ref_map["numbering_level"], "resolved_visual": "2 参考文献"},
        {"paragraph": aref, "style_map_numbering_level": ref_map["numbering_level"], "resolved_visual": "2 参考文献"},
        "DOCX document.xml; Style Map; frozen LibreOffice preview", "FAIL",
        "Both v6 previews display 2 参考文献", "NOT_AUTHORIZED_BY_WINDOWS_VISUAL_ACCEPTANCE",
        "FAIL", "REFERENCE_HEADING_NUMBERING_DRIFT", "YES", "YES",
        "Remove direct numPr from reference heading in a later authorized remediation and rerun Word/schema checks",
        "Neither journal source nor Style Map authorizes reference-heading numbering")
    add("JFR-027", "HFUT-REF-002", "HFUT_REF_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "Reference entries use 7.5 pt Songti/TNR and exact 14-pt spacing", "TEXTUALLY_EXPLICIT",
        "HFUTReferenceEntry", "7.5 pt Songti/TNR; exact 280 twips",
        fs["HFUTReferenceEntry"], ans["HFUTReferenceEntry"], "DOCX styles.xml", "PASS",
        "Preview supports candidate", "WINDOWS_FINAL_REQUIRED", "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT",
        "NO", "NO", "Retain and validate final mixed-language runs")
    add("JFR-028", "HFUT-WEB-023;HFUT-REF-002", "HFUT_WEB_EXCERPT_PDF;HFUT_REF_DOC",
        "TEXTUALLY_EXPLICIT_AND_PROJECT_DERIVED", "References ordered by first citation; hanging indent candidate",
        "MIXED_AUTHORITY", "citations and HFUTReferenceEntry", "Sequential order; 360-twip project candidate",
        {"style": fs["HFUTReferenceEntry"], "entry_count": full["style_usage"].get("HFUTReferenceEntry", 0)},
        {"style": ans["HFUTReferenceEntry"], "entry_count": anonymous["style_usage"].get("HFUTReferenceEntry", 0)},
        "DOCX style usage and content", "PASS", "Synthetic references are sequential", "FINAL_CONTENT_PENDING",
        "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT", "NO", "YES", "Validate real citation order and CSL special rules")
    add("JFR-029", "HFUT-WEB-029;HFUT-WEB-031", "HFUT_WEB_EXCERPT_PDF", "TEXTUALLY_EXPLICIT_AND_PENDING",
        "Full/Anonymous identity boundary", "TEXTUALLY_EXPLICIT_WITH_CONSERVATIVE_CHECKS",
        "document body/properties/review artifacts", "Anonymous omits author-related information",
        fidentity_styles, aidentity_styles, "DOCX style/content/property inspection", "PASS",
        "Anonymous preview omits synthetic identity block", "DOCUMENT_INSPECTOR_REQUIRED",
        "PASS_TEXTUALLY_EXPLICIT", "NO_DRIFT", "NO", "NO", "Run final Word Document Inspector")
    add("JFR-030", "HFUT-AUDIT-NONIDENTITY-PARTS", "PROJECT_POC_CONTRACT", "PROJECT_GOVERNANCE",
        "Full/Anonymous non-identity formatting parts are identical", "PROJECT_DERIVED_CANDIDATE",
        "all package parts except document/core/custom plus normalized common document structure", "Exact nonidentity match",
        variant_compare, variant_compare, "Part SHA256 and normalized paragraph comparison", "PASS" if variant_compare["nonidentity_parts_equal"] and variant_compare["normalized_nonidentity_document_equal"] else "FAIL",
        "Common visual format consistent", "WINDOWS_FINAL_REQUIRED",
        "PASS_PROJECT_DERIVED_CANDIDATE" if variant_compare["nonidentity_parts_equal"] and variant_compare["normalized_nonidentity_document_equal"] else "FAIL",
        "NO_DRIFT", "NO", "NO", "Retain variant differential audit")
    add("JFR-031", "HFUT-WEB-031", "HFUT_WEB_EXCERPT_PDF", "PENDING_VERIFICATION",
        "Document properties/comments/revisions are conservatively inspected", "CONSERVATIVE_PROJECT_CHECK",
        "docProps and review artifacts", "Neutral generator metadata; final Document Inspector",
        {"core": full["core_properties"], "custom": full["custom_properties"]},
        {"core": anonymous["core_properties"], "custom": anonymous["custom_properties"]}, "DOCX properties",
        "PASS", "Not a visual claim", "DOCUMENT_INSPECTOR_REQUIRED", "WINDOWS_FINAL_REQUIRED", "NO_DRIFT",
        "NO", "NO", "Run Document Inspector after final Word save")
    add("JFR-032", "HFUT-AUDIT-OPENXML", "OPENXML_VALIDATOR_REPORT", "OFFICIAL_TOOL_RESULT",
        "Official OpenXmlValidator reports zero errors", "SCHEMA_VALIDATION", "all OOXML parts", "0 errors each",
        validator_result, validator_result, "Frozen DocumentFormat.OpenXml 3.5.1 report", "PASS" if all(value == 0 for value in validator_result.values()) else "FAIL",
        "Not a visual/layout acceptance claim", "NOT_APPLICABLE", "PASS_STYLE_EVIDENCE_CONFIRMED", "NO_DRIFT",
        "NO", "NO", "Rerun after any remediation")
    add("JFR-033", "HFUT-AUDIT-WORD-FIRST-OPEN", "WORD_V6_REMEDIATION_REPORT", "REQUIRED_MANUAL_ACCEPTANCE",
        "Untouched v6 first-open in Microsoft Word produces no repair prompt", "WINDOWS_MANUAL",
        "Full/Anonymous v6 packages", "No unreadable-content prompt", "Not tested", "Not tested",
        "Word v6 remediation report", "NOT_AUTOMATABLE", "LibreOffice cannot substitute", "WINDOWS_FINAL_REQUIRED",
        "WINDOWS_FINAL_REQUIRED", "NO_DRIFT", "YES", "NO", "Open untouched v6 files in Microsoft Word and record result")
    add("JFR-034", "HFUT-AUDIT-WORD-REOPEN", "WINDOWS_WORD_POC_CHECKLIST", "REQUIRED_MANUAL_ACCEPTANCE",
        "Save, close, and reopen both accepted v6 documents", "WINDOWS_MANUAL", "Word-saved v6 derivatives",
        "Normal reopen; no repair prompt", "Not tested for v6", "Not tested for v6", "Frozen Windows checklist",
        "NOT_AUTOMATABLE", "Not covered by LibreOffice preview", "WINDOWS_FINAL_REQUIRED", "WINDOWS_FINAL_REQUIRED",
        "NO_DRIFT", "YES", "NO", "Perform save/close/reopen after v6 first-open acceptance")
    add("JFR-035", "HFUT-AUDIT-FIRST-PAGE-FLOW", "PUBLISHED_VISUAL_EXAMPLES", "VISUAL_EXAMPLE_ONLY",
        "First-page body flow is assessed without elevating a visual example to a rule", "VISUAL_CANDIDATE",
        "section break/page breaks/rendered pagination", "No mandatory first-page body-start rule established",
        {"sections": full["sections"], "explicit_breaks": full["page_breaks"], "observed": "body begins page 2"},
        {"sections": anonymous["sections"], "explicit_breaks": anonymous["page_breaks"], "observed": "body begins page 2"},
        "DOCX OOXML plus frozen LibreOffice preview", "PASS", "Body starts page 2 due front-matter length/keep/continuous column conversion; no explicit pageBreak",
        "WINDOWS_FINAL_REQUIRED", "PASS_PROJECT_DERIVED_CANDIDATE", "NO_DRIFT", "NO", "NO",
        "Treat as visual candidate only; reassess with real front matter", "No frozen textual rule requires body on page 1")
    add("JFR-036", "HFUT-AUDIT-FIELD-POLICY", "REFERENCE_DOCX_DESIGN;REFERENCE_DOCX_REPORT", "PROJECT_GOVERNANCE",
        "Field-update policy is described consistently", "PROJECT_DERIVED_CANDIDATE", "word/settings.xml updateFields",
        "Design says update on open; Report/current implementation say disabled", reference["settings"], full["settings"],
        "Design/Report; canonical/v6 settings.xml", "FAIL", "PAGE renders in preview", "MANUAL_REFRESH_REQUIRED",
        "PASS_PROJECT_DERIVED_CANDIDATE", "DESIGN_DOCUMENT_STALE", "YES", "NO",
        "Update Design to state updateFields is absent and PAGE requires manual/F9 refresh")
    add("JFR-037", "HFUT-AUDIT-NATIVE-TOOLS", "HFUT_FMT_DOC;HFUT_FIG_DOC", "TEXTUALLY_EXPLICIT_REQUIREMENT",
        "MathType/Visio/Origin publication-object boundary remains explicit", "TOOL_BOUNDARY",
        "embeddings and native editability", "Applicable final objects editable in required native tools",
        "POC contains OMML and PNG only", "POC contains OMML and PNG only", "DOCX embeddings/media inspection",
        "NOT_AUTOMATABLE", "Display candidates only", "WINDOWS_FINAL_REQUIRED", "POC_NOT_COVERED", "NO_DRIFT",
        "NO", "NO", "Defer native-tool checks to final publication assets; do not claim POC coverage")
    return rows


def validate_matrix(rows: list[dict[str, str]]) -> None:
    if len(rows) < 25:
        raise ValueError("audit matrix has fewer than 25 required coverage rows")
    audit_ids = [row["audit_id"] for row in rows]
    if len(audit_ids) != len(set(audit_ids)):
        raise ValueError("audit_id values are not unique")
    allowed = {
        "PASS_TEXTUALLY_EXPLICIT", "PASS_STYLE_EVIDENCE_CONFIRMED",
        "PASS_PROJECT_DERIVED_CANDIDATE", "POC_NOT_COVERED",
        "FINAL_CONTENT_PENDING", "WINDOWS_FINAL_REQUIRED", "GOVERNANCE_DRIFT",
        "FAIL", "NOT_APPLICABLE",
    }
    invalid = sorted({row["compliance_status"] for row in rows} - allowed)
    if invalid:
        raise ValueError(f"invalid compliance status values: {invalid}")
    pending_as_pass = [row["audit_id"] for row in rows
                       if "Not tested" in row["actual_value_full"]
                       and row["compliance_status"].startswith("PASS_")]
    if pending_as_pass:
        raise ValueError(f"pending items were defaulted to PASS: {pending_as_pass}")


def serializable_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in doc.items() if key != "openxml_parts"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--full", required=True, type=Path)
    parser.add_argument("--anonymous", required=True, type=Path)
    parser.add_argument("--style-map", type=Path, default=STYLE_MAP_DEFAULT)
    parser.add_argument("--matrix-output", type=Path, default=MATRIX_DEFAULT)
    parser.add_argument("--json-output", type=Path, default=JSON_DEFAULT)
    args = parser.parse_args()

    inputs = {"reference": args.reference, "full": args.full, "anonymous": args.anonymous}
    for key, path in inputs.items():
        if not path.is_file():
            print(f"ERROR: missing {key} DOCX: {path}", file=sys.stderr)
            return 2
    hashes = {key: sha256(path) for key, path in inputs.items()}
    hash_results = {key: hashes[key] == EXPECTED_SHA256[key] for key in inputs}
    if not all(hash_results.values()):
        for key in inputs:
            if not hash_results[key]:
                print(f"ERROR: {key} SHA mismatch expected={EXPECTED_SHA256[key]} actual={hashes[key]}", file=sys.stderr)
        return 2

    style_rows, style_map = read_style_map(args.style_map)
    reference = inspect_docx(args.reference)
    full = inspect_docx(args.full)
    anonymous = inspect_docx(args.anonymous)
    history = validation_history(args.full)
    variants = compare_variants(full, anonymous)
    matrix = build_matrix(reference, full, anonymous, style_map, history, variants)
    validate_matrix(matrix)

    args.matrix_output.parent.mkdir(parents=True, exist_ok=True)
    with args.matrix_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATRIX_FIELDS, lineterminator="\n")
        writer.writeheader(); writer.writerows(matrix)

    blocking_unauthorized = [row for row in matrix
                             if row["blocking_for_phase2_5"] == "YES"
                             and (row["compliance_status"] in {"FAIL", "POC_NOT_COVERED", "WINDOWS_FINAL_REQUIRED"}
                                  or row["governance_status"] != "NO_DRIFT")]
    result = {
        "audit_identity": "PAPER_PHASE2_5_STEP7F_JOURNAL_FORMAT_REGRESSION_AUDIT_V1.0",
        "read_only_docx_audit": True,
        "inputs": {key: {"path": str(inputs[key]), "expected_sha256": EXPECTED_SHA256[key],
                         "actual_sha256": hashes[key], "sha_match": hash_results[key]} for key in inputs},
        "style_map": {"path": str(args.style_map), "row_count": len(style_rows), "rows": style_rows},
        "documents": {"reference": serializable_doc(reference), "full": serializable_doc(full),
                      "anonymous": serializable_doc(anonymous)},
        "openxml_validation_history": history,
        "variant_comparison": variants,
        "matrix": {"path": str(args.matrix_output), "row_count": len(matrix), "rows": matrix},
        "blocking_unauthorized_audit_ids": [row["audit_id"] for row in blocking_unauthorized],
        "verdict": "FORMAT_REMEDIATION_REQUIRED" if blocking_unauthorized else "FORMAT_REGRESSION_PASS",
        "exit_contract": "1=blocking unauthorized difference; 2=audit/tool failure; 0=no blocking difference",
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"reference_sha256={hashes['reference']} match=PASS")
    print(f"full_sha256={hashes['full']} match=PASS")
    print(f"anonymous_sha256={hashes['anonymous']} match=PASS")
    print(f"openxml_error_counts={compact({key: value.get('error_count') for key, value in history['files'].items()})}")
    print(f"nonidentity_parts_equal={variants['nonidentity_parts_equal']}")
    print(f"normalized_nonidentity_document_equal={variants['normalized_nonidentity_document_equal']}")
    print(f"matrix_rows={len(matrix)} unique_audit_rows=PASS")
    print(f"matrix_output={args.matrix_output}")
    print(f"json_output={args.json_output}")
    print(f"verdict={result['verdict']}")
    if blocking_unauthorized:
        print("blocking_unauthorized=" + ",".join(row["audit_id"] for row in blocking_unauthorized))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
