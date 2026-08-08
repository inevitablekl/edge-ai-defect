#!/usr/bin/env python3
"""Apply the narrow Full-manuscript section boundary after Pandoc output."""

from __future__ import annotations

import argparse
import copy
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)

MARKER = "FULL_BODY_SECTION_START"
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


def set_body_columns(root: ET.Element) -> None:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    final_sect = body.find("w:sectPr", NS)
    if final_sect is None:
        raise ValueError("word/document.xml has no final w:sectPr")
    columns = final_sect.find("w:cols", NS)
    if columns is None:
        columns = ET.Element(qn("cols"))
        insert_in_schema_order(final_sect, columns, SECTPR_ORDER)
    columns.set(qn("num"), "2")
    columns.set(qn("space"), "425")


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
    set_body_columns(root)
    insert_continuous_boundary(root)
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
