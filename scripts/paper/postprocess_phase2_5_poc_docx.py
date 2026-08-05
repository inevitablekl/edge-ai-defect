#!/usr/bin/env python3
"""Deterministic OOXML post-processing for the Phase 2.5 Step 6 POC only."""

from __future__ import annotations

import argparse
import copy
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
ASVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS = {"w": W, "m": M, "r": R, "a": A, "asvg": ASVG, "cp": CP, "dc": DC, "dcterms": DCTERMS}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def ensure_first(parent: ET.Element, tag: str) -> ET.Element:
    node = parent.find(tag, NS)
    if node is None:
        node = ET.Element(qn(W, tag.split(":", 1)[1]))
        parent.insert(0, node)
    return node


def set_paragraph_style(paragraph: ET.Element, style_id: str) -> ET.Element:
    ppr = ensure_first(paragraph, "w:pPr")
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is None:
        pstyle = ET.Element(qn(W, "pStyle"))
        ppr.insert(0, pstyle)
    pstyle.set(qn(W, "val"), style_id)
    return ppr


def set_heading_numbering(paragraph: ET.Element, ilvl: int, num_id: int) -> None:
    ppr = set_paragraph_style(
        paragraph,
        "HFUTIntroHeading" if num_id == 2 else f"HFUTHeading{ilvl + 1}",
    )
    old = ppr.find("w:numPr", NS)
    if old is not None:
        ppr.remove(old)
    num_pr = ET.SubElement(ppr, qn(W, "numPr"))
    ET.SubElement(num_pr, qn(W, "ilvl"), {qn(W, "val"): str(ilvl)})
    ET.SubElement(num_pr, qn(W, "numId"), {qn(W, "val"): str(num_id)})


def set_border(parent: ET.Element, edge: str, value: str, size: int | None = None) -> None:
    old = parent.find(f"w:{edge}", NS)
    if old is not None:
        parent.remove(old)
    attrs = {qn(W, "val"): value}
    if size is not None:
        attrs.update({qn(W, "sz"): str(size), qn(W, "space"): "0", qn(W, "color"): "000000"})
    ET.SubElement(parent, qn(W, edge), attrs)


def apply_three_line_table(table: ET.Element) -> None:
    tbl_pr = ensure_first(table, "w:tblPr")
    tbl_style = tbl_pr.find("w:tblStyle", NS)
    if tbl_style is None:
        tbl_style = ET.Element(qn(W, "tblStyle"))
        tbl_pr.insert(0, tbl_style)
    tbl_style.set(qn(W, "val"), "HFUTThreeLineTable")
    tbl_width = tbl_pr.find("w:tblW", NS)
    if tbl_width is None:
        tbl_width = ET.SubElement(tbl_pr, qn(W, "tblW"))
    tbl_width.set(qn(W, "w"), "4400")
    tbl_width.set(qn(W, "type"), "dxa")

    column_widths = (1400, 1400, 1600)
    grid = table.find("w:tblGrid", NS)
    if grid is not None:
        for grid_col, width in zip(grid.findall("w:gridCol", NS), column_widths):
            grid_col.set(qn(W, "w"), str(width))

    borders = tbl_pr.find("w:tblBorders", NS)
    if borders is None:
        borders = ET.SubElement(tbl_pr, qn(W, "tblBorders"))
    set_border(borders, "top", "single", 8)
    set_border(borders, "left", "nil")
    set_border(borders, "bottom", "single", 8)
    set_border(borders, "right", "nil")
    set_border(borders, "insideH", "nil")
    set_border(borders, "insideV", "nil")

    rows = table.findall("w:tr", NS)
    for row_index, row in enumerate(rows):
        for column_index, cell in enumerate(row.findall("w:tc", NS)):
            tc_pr = ensure_first(cell, "w:tcPr")
            cell_width = tc_pr.find("w:tcW", NS)
            if cell_width is None:
                cell_width = ET.SubElement(tc_pr, qn(W, "tcW"))
            cell_width.set(qn(W, "w"), str(column_widths[min(column_index, 2)]))
            cell_width.set(qn(W, "type"), "dxa")
            tc_borders = tc_pr.find("w:tcBorders", NS)
            if tc_borders is None:
                tc_borders = ET.SubElement(tc_pr, qn(W, "tcBorders"))
            set_border(tc_borders, "left", "nil")
            set_border(tc_borders, "right", "nil")
            if row_index == 0:
                set_border(tc_borders, "bottom", "single", 4)
            else:
                set_border(tc_borders, "top", "nil")
                set_border(tc_borders, "bottom", "nil")
            for paragraph in cell.findall("w:p", NS):
                set_paragraph_style(paragraph, "HFUTTableContent")


def transform_document(xml_bytes: bytes, fallback_relationship_id: str | None = None) -> bytes:
    root = ET.fromstring(xml_bytes)
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_sect = body.find("w:sectPr", NS)
    if final_sect is None:
        raise ValueError("word/document.xml has no final w:sectPr")

    boundary_count = 0
    references_started = False
    for paragraph in body.findall("w:p", NS):
        text = paragraph_text(paragraph).strip()
        pstyle = paragraph.find("w:pPr/w:pStyle", NS)
        style = pstyle.get(qn(W, "val")) if pstyle is not None else ""

        if text == "BODY_SECTION_START_MARKER":
            boundary_count += 1
            ppr = set_paragraph_style(paragraph, "HFUTSpecimenNotice")
            for child in list(paragraph):
                if child is not ppr:
                    paragraph.remove(child)
            section = copy.deepcopy(final_sect)
            section_type = section.find("w:type", NS)
            if section_type is None:
                section_type = ET.Element(qn(W, "type"))
                section.insert(0, section_type)
            section_type.set(qn(W, "val"), "continuous")
            cols = section.find("w:cols", NS)
            if cols is None:
                cols = ET.SubElement(section, qn(W, "cols"))
            cols.set(qn(W, "num"), "1")
            cols.set(qn(W, "space"), "425")
            ppr.append(section)
            continue

        if style == "HFUTIntroHeading":
            set_heading_numbering(paragraph, 0, 2)
        elif style == "HFUTHeading1":
            set_heading_numbering(paragraph, 0, 1)
        elif style == "HFUTHeading2":
            set_heading_numbering(paragraph, 1, 1)
        elif style == "HFUTHeading3":
            set_heading_numbering(paragraph, 2, 1)

        if paragraph.find(".//m:oMathPara", NS) is not None:
            set_paragraph_style(paragraph, "HFUTEquation")
        if text.startswith("图1 "):
            set_paragraph_style(paragraph, "HFUTFigureCaption")
        if paragraph.find(".//w:drawing", NS) is not None:
            ppr = set_paragraph_style(paragraph, "HFUTBody")
            spacing = ppr.find("w:spacing", NS)
            if spacing is None:
                spacing = ET.SubElement(ppr, qn(W, "spacing"))
            spacing.set(qn(W, "before"), "0")
            spacing.set(qn(W, "after"), "0")
            spacing.set(qn(W, "line"), "240")
            spacing.set(qn(W, "lineRule"), "auto")
            justification = ppr.find("w:jc", NS)
            if justification is None:
                justification = ET.SubElement(ppr, qn(W, "jc"))
            justification.set(qn(W, "val"), "center")
        if text.startswith("表1 "):
            set_paragraph_style(paragraph, "HFUTTableCaption")
        if text == "参考文献":
            set_paragraph_style(paragraph, "HFUTReferenceHeading")
            references_started = True
        elif references_started and text:
            set_paragraph_style(paragraph, "HFUTReferenceEntry")

    if boundary_count != 1:
        raise ValueError(f"expected one body section marker, found {boundary_count}")
    final_cols = final_sect.find("w:cols", NS)
    if final_cols is None:
        final_cols = ET.SubElement(final_sect, qn(W, "cols"))
    final_cols.set(qn(W, "num"), "2")
    final_cols.set(qn(W, "space"), "425")
    for table in body.findall("w:tbl", NS):
        apply_three_line_table(table)
    if fallback_relationship_id:
        svg_blips = [
            node for node in root.findall(".//a:blip", NS)
            if node.find("a:extLst/a:ext/asvg:svgBlip", NS) is not None
        ]
        if len(svg_blips) != 1:
            raise ValueError(f"expected one SVG blip, found {len(svg_blips)}")
        svg_blips[0].set(qn(R, "embed"), fallback_relationship_id)
        for extension_list in svg_blips[0].findall("a:extLst", NS):
            for extension in list(extension_list):
                if extension.find("asvg:svgBlip", NS) is not None:
                    extension_list.remove(extension)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def scrub_core_properties(xml_bytes: bytes, variant: str) -> bytes:
    root = ET.fromstring(xml_bytes)
    values = {
        qn(DC, "title"): f"Phase 2.5 Step 6 {variant} toolchain POC",
        qn(DC, "subject"): "TOOLCHAIN_POC_ONLY; NOT_PAPER_CONTENT; NOT_SUBMISSION_MANUSCRIPT",
        qn(DC, "creator"): "PAPER_PROJECT_AI_POC",
        qn(CP, "lastModifiedBy"): "PAPER_PROJECT_AI_POC",
        qn(DC, "description"): "SYNTHETIC_CONTENT; PHASE_3_NOT_AUTHORIZED",
    }
    for tag, value in values.items():
        node = root.find(tag)
        if node is None:
            node = ET.SubElement(root, tag)
        node.text = value
    for local in ("created", "modified"):
        node = root.find(qn(DCTERMS, local))
        if node is None:
            node = ET.SubElement(root, qn(DCTERMS, local))
        node.set(qn(XSI, "type"), "dcterms:W3CDTF")
        node.text = "2026-08-06T00:00:00Z"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def add_png_fallback(parts: dict[str, bytes], png_path: Path) -> str:
    media_name = "word/media/poc_figure_fallback.png"
    relationship_id = "rId26"
    parts[media_name] = png_path.read_bytes()

    rel_name = "word/_rels/document.xml.rels"
    rel_root = ET.fromstring(parts[rel_name])
    ET.SubElement(rel_root, qn(PR, "Relationship"), {
        "Id": relationship_id,
        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        "Target": "media/poc_figure_fallback.png",
    })
    ET.register_namespace("", PR)
    parts[rel_name] = ET.tostring(rel_root, encoding="utf-8", xml_declaration=True)

    content_types = ET.fromstring(parts["[Content_Types].xml"])
    if not any(node.get("Extension") == "png" for node in content_types):
        ET.SubElement(content_types, qn(CT, "Default"), {
            "Extension": "png",
            "ContentType": "image/png",
        })
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = ET.tostring(content_types, encoding="utf-8", xml_declaration=True)
    return relationship_id


def rewrite_docx(input_path: Path, output_path: Path, variant: str, fallback_png: Path | None) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    fallback_relationship_id = add_png_fallback(parts, fallback_png) if fallback_png else None
    parts["word/document.xml"] = transform_document(parts["word/document.xml"], fallback_relationship_id)
    if "docProps/core.xml" in parts:
        parts["docProps/core.xml"] = scrub_core_properties(parts["docProps/core.xml"], variant)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output_path.parent, suffix=".docx", delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(parts):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o600 << 16
                archive.writestr(info, parts[name])
        temp_path.replace(output_path)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--variant", required=True, choices=("full", "anonymous"))
    parser.add_argument("--figure-fallback-png", type=Path)
    args = parser.parse_args()
    rewrite_docx(args.input, args.output, args.variant, args.figure_fallback_png)
    print(f"postprocess=PASS variant={args.variant} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
