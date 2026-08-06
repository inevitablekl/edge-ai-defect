#!/usr/bin/env python3
"""Deterministic OOXML post-processing for the Phase 2.5 Step 7C POC only."""

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


def insert_in_schema_order(
    parent: ET.Element,
    node: ET.Element,
    ordered_names: tuple[str, ...],
) -> None:
    """Insert a WordprocessingML child without creating a repair-only order."""
    local = node.tag.rsplit("}", 1)[-1]
    desired = ordered_names.index(local)
    for index, child in enumerate(parent):
        child_local = child.tag.rsplit("}", 1)[-1]
        if child_local in ordered_names and ordered_names.index(child_local) > desired:
            parent.insert(index, node)
            return
    parent.append(node)


def normalize_children(parent: ET.Element, ordered_names: tuple[str, ...]) -> None:
    """Reorder known children while retaining unknown extension children."""
    rank = {name: index for index, name in enumerate(ordered_names)}
    children = list(parent)
    known = sorted(
        (child for child in children if child.tag.rsplit("}", 1)[-1] in rank),
        key=lambda child: rank[child.tag.rsplit("}", 1)[-1]],
    )
    iterator = iter(known)
    parent[:] = [next(iterator) if child.tag.rsplit("}", 1)[-1] in rank else child
                 for child in children]


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
TCPR_ORDER = (
    "cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
    "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark",
    "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange",
)


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
    num_pr = ET.Element(qn(W, "numPr"))
    insert_in_schema_order(ppr, num_pr, PPR_ORDER)
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
        tbl_width = ET.Element(qn(W, "tblW"))
        insert_in_schema_order(tbl_pr, tbl_width, TBLPR_ORDER)
    tbl_width.set(qn(W, "w"), "4400")
    tbl_width.set(qn(W, "type"), "dxa")

    column_widths = (1400, 1400, 1600)
    grid = table.find("w:tblGrid", NS)
    if grid is not None:
        for grid_col, width in zip(grid.findall("w:gridCol", NS), column_widths):
            grid_col.set(qn(W, "w"), str(width))

    borders = tbl_pr.find("w:tblBorders", NS)
    if borders is None:
        borders = ET.Element(qn(W, "tblBorders"))
        insert_in_schema_order(tbl_pr, borders, TBLPR_ORDER)
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
                tc_borders = ET.Element(qn(W, "tcBorders"))
                insert_in_schema_order(tc_pr, tc_borders, TCPR_ORDER)
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
                insert_in_schema_order(section, section_type, SECTPR_ORDER)
            section_type.set(qn(W, "val"), "continuous")
            cols = section.find("w:cols", NS)
            if cols is None:
                cols = ET.Element(qn(W, "cols"))
                insert_in_schema_order(section, cols, SECTPR_ORDER)
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

        has_display_math = paragraph.find(".//m:oMathPara", NS) is not None
        has_inline_math = paragraph.find(".//m:oMath", NS) is not None and not has_display_math
        if has_display_math:
            set_paragraph_style(paragraph, "HFUTEquation")
        elif has_inline_math:
            # HFUTBody is intentionally exact-spaced for ordinary text.  An
            # inline OMML run needs only a small minimum-height exception.
            ppr = set_paragraph_style(paragraph, "HFUTBody")
            spacing = ppr.find("w:spacing", NS)
            if spacing is None:
                spacing = ET.Element(qn(W, "spacing"))
                insert_in_schema_order(ppr, spacing, PPR_ORDER)
            spacing.set(qn(W, "before"), "0")
            spacing.set(qn(W, "after"), "0")
            spacing.set(qn(W, "line"), "360")
            spacing.set(qn(W, "lineRule"), "atLeast")
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
        final_cols = ET.Element(qn(W, "cols"))
        insert_in_schema_order(final_sect, final_cols, SECTPR_ORDER)
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


def scrub_custom_properties(xml_bytes: bytes) -> bytes:
    """Remove machine-specific absolute paths from generator metadata."""
    root = ET.fromstring(xml_bytes)
    for property_node in root:
        if property_node.get("name") != "csl":
            continue
        value_node = next(iter(property_node), None)
        if value_node is not None:
            value_node.text = "china-national-standard-gb-t-7714-2025-numeric.csl"
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


def deduplicate_styles(parts: dict[str, bytes]) -> None:
    """Keep the canonical first definition for each styleId.

    Pandoc appends placeholder custom styles even when the reference DOCX
    already defines the same style IDs. Word repairs the duplicate IDs by
    renaming the placeholders and retargeting paragraphs to them, which drops
    the intended front-matter formatting.
    """
    root = ET.fromstring(parts["word/styles.xml"])
    seen: set[str] = set()
    for style in list(root.findall("w:style", NS)):
        style_id = style.get(qn(W, "styleId"), "")
        if style_id in seen:
            root.remove(style)
        else:
            seen.add(style_id)
    defined = {
        style.get(qn(W, "styleId"), "") for style in root.findall("w:style", NS)
    }
    for style in root.findall("w:style", NS):
        based_on = style.find("w:basedOn", NS)
        if based_on is not None and based_on.get(qn(W, "val"), "") not in defined:
            style.remove(based_on)
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def disable_open_time_field_updates(parts: dict[str, bytes]) -> None:
    root = ET.fromstring(parts["word/settings.xml"])
    for node in root.findall("w:updateFields", NS):
        root.remove(node)
    parts["word/settings.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_unused_svg(parts: dict[str, bytes]) -> None:
    """Remove the orphan SVG left after the drawing is retargeted to PNG."""
    rel_name = "word/_rels/document.xml.rels"
    rel_root = ET.fromstring(parts[rel_name])
    document = ET.fromstring(parts["word/document.xml"])
    used_relationship_ids = {
        value
        for node in document.iter()
        for name, value in node.attrib.items()
        if name.startswith(f"{{{R}}}")
    }
    removed_targets: list[str] = []
    for rel in list(rel_root):
        if (
            rel.get("Type", "").endswith("/image")
            and rel.get("Id") not in used_relationship_ids
            and rel.get("Target", "").lower().endswith(".svg")
        ):
            removed_targets.append(rel.get("Target", ""))
            rel_root.remove(rel)
    for target in removed_targets:
        parts.pop(f"word/{target}", None)
    ET.register_namespace("", PR)
    parts[rel_name] = ET.tostring(rel_root, encoding="utf-8", xml_declaration=True)

    content_types = ET.fromstring(parts["[Content_Types].xml"])
    if not any(name.lower().endswith(".svg") for name in parts):
        for node in list(content_types):
            if (node.get("Extension", "").lower() == "svg"
                    or node.get("PartName", "").lower().endswith(".svg")):
                content_types.remove(node)
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = ET.tostring(content_types, encoding="utf-8", xml_declaration=True)


def remove_empty_comments(parts: dict[str, bytes]) -> None:
    """Remove Pandoc's empty comments part and its now-unused relationship."""
    comments_name = "word/comments.xml"
    if comments_name not in parts:
        return
    root = ET.fromstring(parts[comments_name])
    if root.findall("w:comment", NS):
        return
    del parts[comments_name]
    rel_name = "word/_rels/document.xml.rels"
    rel_root = ET.fromstring(parts[rel_name])
    for rel in list(rel_root):
        if rel.get("Type", "").endswith("/comments"):
            rel_root.remove(rel)
    ET.register_namespace("", PR)
    parts[rel_name] = ET.tostring(rel_root, encoding="utf-8", xml_declaration=True)


def remove_dangling_content_type_overrides(parts: dict[str, bytes]) -> None:
    """Remove overrides whose package part is absent (not caught by unzip)."""
    content_types = ET.fromstring(parts["[Content_Types].xml"])
    present = set(parts)
    for node in list(content_types):
        part_name = node.get("PartName", "").lstrip("/")
        if part_name and part_name not in present:
            content_types.remove(node)
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = ET.tostring(content_types, encoding="utf-8", xml_declaration=True)


def repair_style_paragraph_properties(parts: dict[str, bytes]) -> None:
    """Normalize style-level w:pPr order before Word has to repair it."""
    root = ET.fromstring(parts["word/styles.xml"])
    for style in root.findall("w:style", NS):
        ppr = style.find("w:pPr", NS)
        if ppr is not None:
            normalize_children(ppr, PPR_ORDER)
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def repair_equation_style(parts: dict[str, bytes]) -> None:
    """Give display OMML a minimum height instead of a clipping exact height."""
    root = ET.fromstring(parts["word/styles.xml"])
    style = next((node for node in root.findall("w:style", NS)
                  if node.get(qn(W, "styleId")) == "HFUTEquation"), None)
    if style is None:
        raise ValueError("HFUTEquation style is missing")
    ppr = style.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.SubElement(style, qn(W, "pPr"))
    spacing = ppr.find("w:spacing", NS)
    if spacing is None:
        spacing = ET.Element(qn(W, "spacing"))
        insert_in_schema_order(ppr, spacing, PPR_ORDER)
    spacing.set(qn(W, "before"), "80")
    spacing.set(qn(W, "after"), "80")
    spacing.set(qn(W, "line"), "480")
    spacing.set(qn(W, "lineRule"), "atLeast")
    normalize_children(ppr, PPR_ORDER)
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_unused_explicit_relationships(parts: dict[str, bytes]) -> None:
    """Drop image/hyperlink relationships that no source XML node references."""
    for rel_name in sorted(name for name in parts if name.endswith(".rels") and "/_rels/" in name):
        rel_path = Path(rel_name)
        source_name = (rel_path.parent.parent / rel_path.name[:-5]).as_posix()
        if source_name not in parts:
            continue
        source = ET.fromstring(parts[source_name])
        used_ids = {
            value
            for node in source.iter()
            for name, value in node.attrib.items()
            if name.startswith(f"{{{R}}}")
        }
        root = ET.fromstring(parts[rel_name])
        for rel in list(root):
            rel_type = rel.get("Type", "")
            if (
                (rel_type.endswith("/image") or rel_type.endswith("/hyperlink"))
                and rel.get("Id") not in used_ids
            ):
                root.remove(rel)
        if len(root) == 0:
            del parts[rel_name]
        else:
            ET.register_namespace("", PR)
            parts[rel_name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite_docx(input_path: Path, output_path: Path, variant: str, fallback_png: Path | None) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    fallback_relationship_id = add_png_fallback(parts, fallback_png) if fallback_png else None
    parts["word/document.xml"] = transform_document(parts["word/document.xml"], fallback_relationship_id)
    deduplicate_styles(parts)
    disable_open_time_field_updates(parts)
    if fallback_relationship_id:
        remove_unused_svg(parts)
    remove_empty_comments(parts)
    remove_unused_explicit_relationships(parts)
    remove_dangling_content_type_overrides(parts)
    if "docProps/core.xml" in parts:
        parts["docProps/core.xml"] = scrub_core_properties(parts["docProps/core.xml"], variant)
    if "docProps/custom.xml" in parts:
        parts["docProps/custom.xml"] = scrub_custom_properties(parts["docProps/custom.xml"])
    repair_style_paragraph_properties(parts)
    repair_equation_style(parts)

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
