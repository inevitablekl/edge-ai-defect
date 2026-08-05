#!/usr/bin/env python3
"""Inspect a Phase 2.5 Step 6 POC DOCX without claiming Word acceptance."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "m": M, "r": R, "pr": PR, "a": A}

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


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def xml_root(parts: dict[str, bytes], name: str) -> ET.Element:
    return ET.fromstring(parts[name])


def para_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def attr(node: ET.Element | None, name: str, default: str = "") -> str:
    return default if node is None else node.get(qn(W, name), default)


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
    if path.name != f"poc_{variant}.docx":
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
    if any(item["space_twips"] != 425 for item in columns):
        errors.append("column spacing is not 425 twips")
    expected_page = [11906, 16838]
    expected_margins = {"top": 1361, "right": 1304, "bottom": 1134, "left": 1304, "gutter": 0}
    if any(item["page_twips"] != expected_page or item["margins_twips"] != expected_margins for item in geometry):
        errors.append("page geometry or margins differ from reference candidate")
    if any(section.find("w:pgNumType", NS) is not None for section in section_nodes):
        errors.append("page-number restart found")
    result["page_number_continuity"] = "NO_RESTART_PROPERTY"

    defined_styles = {
        node.get(qn(W, "styleId"), "") for node in styles.findall("w:style", NS)
    }
    style_counts = Counter(
        node.get(qn(W, "val"), "") for node in document.findall(".//w:pStyle", NS)
    )
    required_used = set(COMMON_STYLES)
    if variant == "full":
        required_used |= FULL_ONLY_STYLES
    missing_defined = sorted(required_used - defined_styles)
    missing_used = sorted(style for style in required_used if style_counts[style] == 0)
    result["styles"] = {
        "defined_required_missing": missing_defined,
        "used_required_missing": missing_used,
        "actual_usage": dict(sorted(style_counts.items())),
    }
    if missing_defined or missing_used:
        errors.append(f"required style definition/use missing: defined={missing_defined}, used={missing_used}")

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
    result["heading_numbering"] = {
        "paragraph_numPr": headings,
        "num_to_abstract": num_to_abstract,
        "abstract_formats": abstract_formats,
        "visual_text_requires_renderer": True,
        "word_field_refresh_required": True,
    }
    if num_to_abstract.get(1) != 0 or num_to_abstract.get(2) != 1:
        errors.append("numbering numId/abstractNum relationship mismatch")

    math_inline = len(document.findall(".//m:oMath", NS))
    math_para = len(document.findall(".//m:oMathPara", NS))
    result["formulas"] = {
        "oMath_count": math_inline,
        "oMathPara_count": math_para,
        "representation": "OMML_NOT_IMAGE",
        "mathtype_status": "WORD_MANUAL_REQUIRED",
        "numbering": "STATIC_TEXT_ONLY",
        "cross_reference": "STATIC_TEXT_ONLY",
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
        "display_representation": "PNG_FALLBACK_WITH_SVG_PACKAGE_COPY",
        "caption_style_count": style_counts["HFUTFigureCaption"],
        "numbering": "STATIC_TEXT_ONLY",
        "cross_reference": "STATIC_TEXT_ONLY",
    }
    if ".svg" not in extensions or ".png" not in extensions or style_counts["HFUTFigureCaption"] < 1:
        errors.append("figure media or figure caption missing")

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

    field_instructions = [
        node.get(qn(W, "instr"), "").strip() for node in document.findall(".//w:fldSimple", NS)
    ] + [node.text.strip() for node in document.findall(".//w:instrText", NS) if node.text]
    result["fields_and_bookmarks"] = {
        "document_fields": field_instructions,
        "bookmark_count": len(document.findall(".//w:bookmarkStart", NS)),
        "dynamic_figure_table_equation_cross_refs": False,
        "future": "WORD_FIELD_POSTPROCESS_FUTURE_OR_WORD_MANUAL",
    }

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
    for name in relationship_parts:
        try:
            rel_root = ET.fromstring(parts[name])
        except ET.ParseError:
            continue
        for rel in rel_root.findall("pr:Relationship", NS):
            if rel.get("TargetMode") == "External":
                external_relationships.append({"part": name, "target": rel.get("Target", ""), "type": rel.get("Type", "")})
    result["relationships"] = {"parts": relationship_parts, "external": external_relationships}

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
