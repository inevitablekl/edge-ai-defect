#!/usr/bin/env python3
"""Apply the narrow Full-manuscript section boundary after Pandoc output."""

from __future__ import annotations

import argparse
import copy
import csv
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W, "m": M}
ET.register_namespace("w", W)
ET.register_namespace("r", R)

MARKER = "FULL_BODY_SECTION_START"
WIDE_FIGURE_CAPTIONS = {
    "图1": (
        "图1　输入数据路径抽象及层级受控比较。图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。"
    ),
}
WIDE_TABLE_CAPTIONS = {
    "表1": "表1　三条输入数据路径的结构描述与派生量。名义输入复制载荷由跨边界表示推导，非实测流量。",
}
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


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def insert_in_schema_order(parent: ET.Element, node: ET.Element, order: tuple[str, ...]) -> None:
    local = node.tag.rsplit("}", 1)[-1]
    desired = order.index(local)
    for index, child in enumerate(parent):
        child_local = child.tag.rsplit("}", 1)[-1]
        if child_local in order and order.index(child_local) > desired:
            parent.insert(index, node)
            return
    parent.append(node)


def ensure_first(parent: ET.Element, local: str) -> ET.Element:
    node = parent.find(f"w:{local}", NS)
    if node is None:
        node = ET.Element(qn(local))
        parent.insert(0, node)
    return node


def set_paragraph_style(paragraph: ET.Element, style_id: str) -> ET.Element:
    ppr = ensure_first(paragraph, "pPr")
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is None:
        pstyle = ET.Element(qn("pStyle"))
        ppr.insert(0, pstyle)
    pstyle.set(qn("val"), style_id)
    return ppr


def normalize_equation_paragraphs(root: ET.Element) -> None:
    """Restore the validated display and inline OMML paragraph contract."""
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")

    for paragraph in body.findall("w:p", NS):
        has_display_math = paragraph.find(".//m:oMathPara", NS) is not None
        has_inline_math = paragraph.find(".//m:oMath", NS) is not None and not has_display_math

        if has_display_math:
            # Use the existing named style so its complete validated contract
            # remains authoritative for display equations.
            set_paragraph_style(paragraph, "HFUTEquation")
            continue

        pstyle = paragraph.find("w:pPr/w:pStyle", NS)
        is_body_paragraph = pstyle is not None and pstyle.get(qn("val")) == "HFUTBody"
        if not has_inline_math or not is_body_paragraph:
            continue

        # Preserve HFUTBody's font, alignment, and indentation while giving an
        # inline OMML run the narrow minimum-height exception validated in
        # Phase 2.5.
        ppr = set_paragraph_style(paragraph, "HFUTBody")
        spacing = ppr.find("w:spacing", NS)
        if spacing is None:
            spacing = ET.Element(qn("spacing"))
            insert_in_schema_order(ppr, spacing, PPR_ORDER)
        spacing.set(qn("before"), "0")
        spacing.set(qn("after"), "0")
        spacing.set(qn("line"), "360")
        spacing.set(qn("lineRule"), "atLeast")


def load_equation_numbers() -> list[tuple[str, str, str]]:
    manifest = Path("docs/paper/manuscript/equations/equation_manifest.csv")
    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    expected_ids = ["E1", "E2", "E3"]
    if [row["equation_id"] for row in rows] != expected_ids:
        raise ValueError("equation manifest must contain E1, E2 and E3 in order")
    result: list[tuple[str, str, str]] = []
    for row in rows:
        number = row["word_equation_number"].strip()
        if not number.isdigit():
            raise ValueError(f"invalid visible equation number for {row['equation_id']}: {number!r}")
        result.append((row["equation_id"], row["semantic_name"], number))
    return result


def set_math_run_size(math: ET.Element, half_points: str) -> None:
    for run in math.findall(".//m:r", NS):
        run_properties = run.find("w:rPr", NS)
        if run_properties is None:
            run_properties = ET.Element(qn("rPr"))
            math_properties = run.find("m:rPr", NS)
            run.insert(1 if math_properties is not None else 0, run_properties)
        fonts = run_properties.find("w:rFonts", NS)
        if fonts is None:
            fonts = ET.SubElement(run_properties, qn("rFonts"))
        fonts.set(qn("ascii"), "Times New Roman")
        fonts.set(qn("hAnsi"), "Times New Roman")
        fonts.set(qn("eastAsia"), "宋体")
        for local in ("sz", "szCs"):
            size = run_properties.find(f"w:{local}", NS)
            if size is None:
                size = ET.SubElement(run_properties, qn(local))
            size.set(qn("val"), half_points)


def apply_visible_equation_numbers(root: ET.Element) -> None:
    """Consume the equation manifest into centered OMML plus right-side numbers."""
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    paragraphs = [
        paragraph for paragraph in body.findall("w:p", NS)
        if paragraph.find(".//m:oMathPara", NS) is not None
    ]
    manifest = load_equation_numbers()
    if len(paragraphs) != len(manifest):
        raise ValueError(
            f"equation manifest/display count mismatch: manifest={len(manifest)} display={len(paragraphs)}"
        )
    for paragraph, (equation_id, semantic_name, number) in zip(paragraphs, manifest):
        math_paragraph = paragraph.find("m:oMathPara", NS)
        equations = [] if math_paragraph is None else math_paragraph.findall("m:oMath", NS)
        if len(equations) != 1:
            raise ValueError(f"{equation_id} must contain exactly one OMML equation")
        equation = equations[0]
        math_paragraph.remove(equation)
        paragraph.remove(math_paragraph)
        set_math_run_size(equation, "21")

        ppr = set_paragraph_style(paragraph, "HFUTEquation")
        alignment = ppr.find("w:jc", NS)
        if alignment is None:
            alignment = ET.Element(qn("jc"))
            insert_in_schema_order(ppr, alignment, PPR_ORDER)
        alignment.set(qn("val"), "left")
        tabs = ppr.find("w:tabs", NS)
        if tabs is not None:
            ppr.remove(tabs)
        tabs = ET.Element(qn("tabs"))
        ET.SubElement(tabs, qn("tab"), {qn("val"): "center", qn("pos"): "2205"})
        ET.SubElement(tabs, qn("tab"), {qn("val"): "right", qn("pos"): "4410"})
        insert_in_schema_order(ppr, tabs, PPR_ORDER)

        leading_tab = ET.Element(qn("r"))
        ET.SubElement(leading_tab, qn("tab"))
        trailing_tab = ET.Element(qn("r"))
        ET.SubElement(trailing_tab, qn("tab"))
        number_run = ET.Element(qn("r"))
        number_properties = ET.SubElement(number_run, qn("rPr"))
        ET.SubElement(number_properties, qn("rFonts"), {
            qn("ascii"): "Times New Roman", qn("hAnsi"): "Times New Roman",
            qn("eastAsia"): "宋体",
        })
        ET.SubElement(number_properties, qn("sz"), {qn("val"): "21"})
        ET.SubElement(number_properties, qn("szCs"), {qn("val"): "21"})
        ET.SubElement(number_run, qn("t")).text = f"（{number}）"
        paragraph.extend((leading_tab, equation, trailing_tab, number_run))


def set_body_columns(root: ET.Element) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_sect = body.find("w:sectPr", NS)
    if final_sect is None:
        raise ValueError("word/document.xml has no final w:sectPr")
    section_type = final_sect.find("w:type", NS)
    if section_type is None:
        section_type = ET.Element(qn("type"))
        insert_in_schema_order(final_sect, section_type, SECTPR_ORDER)
    section_type.set(qn("val"), "continuous")
    columns = final_sect.find("w:cols", NS)
    if columns is None:
        columns = ET.Element(qn("cols"))
        insert_in_schema_order(final_sect, columns, SECTPR_ORDER)
    columns.set(qn("num"), "2")
    columns.set(qn("space"), "425")


def section_copy(
    final_section: ET.Element,
    columns: str,
    section_type_value: str = "continuous",
) -> ET.Element:
    section = copy.deepcopy(final_section)
    section_type = section.find("w:type", NS)
    if section_type is None:
        section_type = ET.Element(qn("type"))
        insert_in_schema_order(section, section_type, SECTPR_ORDER)
    section_type.set(qn("val"), section_type_value)
    cols = section.find("w:cols", NS)
    if cols is None:
        cols = ET.Element(qn("cols"))
        insert_in_schema_order(section, cols, SECTPR_ORDER)
    cols.set(qn("num"), columns)
    cols.set(qn("space"), "425")
    title_page = section.find("w:titlePg", NS)
    if title_page is not None:
        section.remove(title_page)
    return section


def set_paragraph_section(paragraph: ET.Element, section: ET.Element) -> None:
    ppr = ensure_first(paragraph, "pPr")
    old = ppr.find("w:sectPr", NS)
    if old is not None:
        ppr.remove(old)
    insert_in_schema_order(ppr, section, PPR_ORDER)


def span_wide_figures(root: ET.Element) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_section = body.find("w:sectPr", NS)
    if final_section is None:
        raise ValueError("word/document.xml has no final w:sectPr")
    children = list(body)
    for label, expected_caption in WIDE_FIGURE_CAPTIONS.items():
        captions = [
            node
            for node in children
            if node.tag == qn("p") and paragraph_text(node) == expected_caption
        ]
        if len(captions) != 1:
            raise ValueError(f"expected one {label} caption, found {len(captions)}")
        caption = captions[0]
        caption_index = children.index(caption)
        if caption_index < 2:
            raise ValueError(f"{label} caption has no preceding callout and drawing")
        drawing = children[caption_index - 1]
        callout = children[caption_index - 2]
        if drawing.tag != qn("p") or drawing.find(".//w:drawing", NS) is None:
            raise ValueError(f"{label} caption is not immediately preceded by its drawing")
        if callout.tag != qn("p") or label not in paragraph_text(callout):
            raise ValueError(f"{label} drawing is not preceded by its callout paragraph")
        set_paragraph_section(callout, section_copy(final_section, "2"))
        # Section properties on the caption govern the one-column figure
        # section. Starting that section on the next page keeps Figure 1 at
        # page top; the following continuous two-column section resumes below.
        break_type = "nextPage" if label == "图1" else "continuous"
        set_paragraph_section(caption, section_copy(final_section, "1", break_type))
        drawing_ppr = ensure_first(drawing, "pPr")
        if drawing_ppr.find("w:keepNext", NS) is None:
            insert_in_schema_order(drawing_ppr, ET.Element(qn("keepNext")), PPR_ORDER)


def span_wide_tables(root: ET.Element) -> None:
    """Place the governed full-width tables across the complete text width."""

    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_section = body.find("w:sectPr", NS)
    if final_section is None:
        raise ValueError("word/document.xml has no final w:sectPr")
    children = list(body)
    for label, expected_caption in WIDE_TABLE_CAPTIONS.items():
        children = list(body)
        captions = [
            node
            for node in children
            if node.tag == qn("p") and paragraph_text(node) == expected_caption
        ]
        if len(captions) != 1:
            raise ValueError(f"expected one {label} caption, found {len(captions)}")
        caption = captions[0]
        caption_index = children.index(caption)
        if caption_index < 1:
            raise ValueError(f"{label} caption has no preceding callout")
        callout = children[caption_index - 1]
        if callout.tag != qn("p") or label not in paragraph_text(callout):
            raise ValueError(f"{label} caption is not preceded by its callout paragraph")
        table = next(
            (node for node in children[caption_index + 1 :] if node.tag == qn("tbl")),
            None,
        )
        if table is None:
            raise ValueError(f"{label} caption is not followed by a table")

        set_paragraph_section(callout, section_copy(final_section, "2"))
        section_break = ET.Element(qn("p"))
        set_paragraph_section(section_break, section_copy(final_section, "1"))
        ppr = ensure_first(section_break, "pPr")
        spacing = ET.Element(
            qn("spacing"),
            {qn("before"): "0", qn("after"): "0", qn("line"): "1", qn("lineRule"): "exact"},
        )
        insert_in_schema_order(ppr, spacing, PPR_ORDER)
        body.insert(list(body).index(table) + 1, section_break)


def normalize_publication_drawing_paragraphs(root: ET.Element) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    paragraphs = [
        paragraph for paragraph in body.findall("w:p", NS)
        if paragraph.find(".//w:drawing", NS) is not None
    ]
    if len(paragraphs) != 3:
        raise ValueError(f"expected three publication drawing paragraphs, found {len(paragraphs)}")
    for paragraph in paragraphs:
        ppr = ensure_first(paragraph, "pPr")
        spacing = ppr.find("w:spacing", NS)
        if spacing is None:
            spacing = ET.Element(qn("spacing"))
            insert_in_schema_order(ppr, spacing, PPR_ORDER)
        spacing.set(qn("before"), "0")
        spacing.set(qn("after"), "0")
        spacing.set(qn("line"), "320")
        spacing.set(qn("lineRule"), "atLeast")

        indent = ppr.find("w:ind", NS)
        if indent is None:
            indent = ET.Element(qn("ind"))
            insert_in_schema_order(ppr, indent, PPR_ORDER)
        indent.attrib.pop(qn("hanging"), None)
        indent.set(qn("firstLine"), "0")

        alignment = ppr.find("w:jc", NS)
        if alignment is None:
            alignment = ET.Element(qn("jc"))
            insert_in_schema_order(ppr, alignment, PPR_ORDER)
        alignment.set(qn("val"), "center")


def first_footer_xml(biography: str | None) -> bytes:
    footer = ET.Element(qn("ftr"))
    if biography is not None:
        paragraph = ET.SubElement(footer, qn("p"))
        ppr = ET.SubElement(paragraph, qn("pPr"))
        ET.SubElement(ppr, qn("pStyle"), {qn("val"): "HFUTAuthorBiography"})
        run = ET.SubElement(paragraph, qn("r"))
        ET.SubElement(run, qn("t")).text = biography
    paragraph = ET.SubElement(footer, qn("p"))
    ppr = ET.SubElement(paragraph, qn("pPr"))
    ET.SubElement(ppr, qn("pStyle"), {qn("val"): "PageNumber"})
    ET.SubElement(ppr, qn("jc"), {qn("val"): "center"})
    field = ET.SubElement(paragraph, qn("fldSimple"), {qn("instr"): " PAGE "})
    run = ET.SubElement(field, qn("r"))
    rpr = ET.SubElement(run, qn("rPr"))
    ET.SubElement(rpr, qn("noProof"))
    return ET.tostring(footer, encoding="utf-8", xml_declaration=True)


def deduplicate_styles(parts: dict[str, bytes]) -> None:
    root = ET.fromstring(parts["word/styles.xml"])
    seen: set[str] = set()
    for style in list(root.findall("w:style", NS)):
        style_id = style.get(qn("styleId"), "")
        if style_id in seen:
            root.remove(style)
        else:
            seen.add(style_id)
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def apply_phase5_equation_style(parts: dict[str, bytes]) -> None:
    """Apply the accepted adaptive display contract to production output only."""
    root = ET.fromstring(parts["word/styles.xml"])
    style = next(
        (node for node in root.findall("w:style", NS)
         if node.get(qn("styleId")) == "HFUTEquation"),
        None,
    )
    if style is None:
        raise ValueError("HFUTEquation style is missing")
    ppr = style.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.SubElement(style, qn("pPr"))
    spacing = ppr.find("w:spacing", NS)
    if spacing is None:
        spacing = ET.Element(qn("spacing"))
        insert_in_schema_order(ppr, spacing, PPR_ORDER)
    spacing.set(qn("before"), "0")
    spacing.set(qn("after"), "0")
    spacing.set(qn("line"), "320")
    spacing.set(qn("lineRule"), "atLeast")
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def justify_reference_styles(parts: dict[str, bytes]) -> None:
    root = ET.fromstring(parts["word/styles.xml"])
    for style_id in ("HFUTReferenceEntry", "Bibliography"):
        style = next(
            (node for node in root.findall("w:style", NS)
             if node.get(qn("styleId")) == style_id),
            None,
        )
        if style is None:
            raise ValueError(f"{style_id} style is missing")
        ppr = style.find("w:pPr", NS)
        if ppr is None:
            ppr = ET.SubElement(style, qn("pPr"))
        alignment = ppr.find("w:jc", NS)
        if alignment is None:
            alignment = ET.Element(qn("jc"))
            insert_in_schema_order(ppr, alignment, PPR_ORDER)
        alignment.set(qn("val"), "both")
    parts["word/styles.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_biography_custom_property(parts: dict[str, bytes]) -> None:
    name = "docProps/custom.xml"
    if name not in parts:
        return
    root = ET.fromstring(parts[name])
    for node in list(root):
        if node.get("name", "") == "author-biography":
            root.remove(node)
    parts[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def move_biography_to_first_footer(root: ET.Element, parts: dict[str, bytes]) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    biographies = [
        paragraph for paragraph in body.findall("w:p", NS)
        if (paragraph.find("w:pPr/w:pStyle", NS) is not None
            and paragraph.find("w:pPr/w:pStyle", NS).get(qn("val")) == "HFUTAuthorBiography")
    ]
    if len(biographies) > 1:
        raise ValueError(f"expected at most one body biography, found {len(biographies)}")
    biography = paragraph_text(biographies[0]) if biographies else None
    if biographies:
        body.remove(biographies[0])

    footer_numbers = [
        int(match.group(1)) for name in parts
        for match in [re.fullmatch(r"word/footer(\d+)\.xml", name)] if match
    ]
    footer_number = max(footer_numbers, default=0) + 1
    footer_name = f"word/footer{footer_number}.xml"
    parts[footer_name] = first_footer_xml(biography)

    rel_name = "word/_rels/document.xml.rels"
    rel_root = ET.fromstring(parts[rel_name])
    numeric_ids = [
        int(match.group(1)) for rel in rel_root
        for match in [re.fullmatch(r"rId(\d+)", rel.get("Id", ""))] if match
    ]
    relationship_id = f"rId{max(numeric_ids, default=0) + 1}"
    ET.SubElement(rel_root, f"{{{PR}}}Relationship", {
        "Id": relationship_id,
        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer",
        "Target": f"footer{footer_number}.xml",
    })
    ET.register_namespace("", PR)
    parts[rel_name] = ET.tostring(rel_root, encoding="utf-8", xml_declaration=True)

    sections = root.findall(".//w:sectPr", NS)
    if not sections:
        raise ValueError("document has no section for first-page footer")
    first_section = sections[0]
    for existing in list(first_section.findall("w:footerReference", NS)):
        if existing.get(qn("type")) == "first":
            first_section.remove(existing)
    first_reference = ET.Element(qn("footerReference"), {
        qn("type"): "first", f"{{{R}}}id": relationship_id,
    })
    insert_in_schema_order(first_section, first_reference, SECTPR_ORDER)
    if first_section.find("w:titlePg", NS) is None:
        insert_in_schema_order(first_section, ET.Element(qn("titlePg")), SECTPR_ORDER)

    types = ET.fromstring(parts["[Content_Types].xml"])
    part_name = f"/{footer_name}"
    if not any(node.get("PartName") == part_name for node in types):
        ET.SubElement(types, f"{{{CT}}}Override", {
            "PartName": part_name,
            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml",
        })
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = ET.tostring(types, encoding="utf-8", xml_declaration=True)


def insert_continuous_boundary(root: ET.Element) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_sect = body.find("w:sectPr", NS)
    if final_sect is None:
        raise ValueError("word/document.xml has no final w:sectPr")
    markers = [p for p in body.findall("w:p", NS) if paragraph_text(p) == MARKER]
    if len(markers) != 1:
        raise ValueError(f"expected one {MARKER} paragraph, found {len(markers)}")
    marker = markers[0]
    ppr = ensure_first(marker, "pPr")
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is None:
        pstyle = ET.Element(qn("pStyle"), {qn("val"): "HFUTSpecimenNotice"})
        ppr.insert(0, pstyle)
    else:
        pstyle.set(qn("val"), "HFUTSpecimenNotice")
    for child in list(marker):
        if child is not ppr:
            marker.remove(child)

    section = copy.deepcopy(final_sect)
    section_type = section.find("w:type", NS)
    if section_type is None:
        section_type = ET.Element(qn("type"))
        insert_in_schema_order(section, section_type, SECTPR_ORDER)
    section_type.set(qn("val"), "continuous")
    columns = section.find("w:cols", NS)
    if columns is None:
        columns = ET.Element(qn("cols"))
        insert_in_schema_order(section, columns, SECTPR_ORDER)
    columns.set(qn("num"), "1")
    columns.set(qn("space"), "425")
    old_section = ppr.find("w:sectPr", NS)
    if old_section is not None:
        ppr.remove(old_section)
    insert_in_schema_order(ppr, section, PPR_ORDER)


def rewrite(input_path: Path, output_path: Path) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    root = ET.fromstring(parts["word/document.xml"])
    deduplicate_styles(parts)
    apply_phase5_equation_style(parts)
    justify_reference_styles(parts)
    remove_biography_custom_property(parts)
    set_body_columns(root)
    insert_continuous_boundary(root)
    span_wide_figures(root)
    span_wide_tables(root)
    normalize_publication_drawing_paragraphs(root)
    normalize_equation_paragraphs(root)
    apply_visible_equation_numbers(root)
    move_biography_to_first_footer(root, parts)
    parts["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output_path.parent, suffix=".docx", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(parts):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o600 << 16
                archive.writestr(info, parts[name])
        temporary.replace(output_path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rewrite(args.input, args.output)
    print(f"full_docx_postprocess=PASS output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
