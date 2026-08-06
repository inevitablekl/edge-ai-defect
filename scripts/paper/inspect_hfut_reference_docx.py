#!/usr/bin/env python3
"""Inspect the generated HFUT reference DOCX candidate without external packages."""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}

REQUIRED_PARTS = {
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
    "word/_rels/document.xml.rels",
    "word/styles.xml",
    "word/numbering.xml",
    "word/settings.xml",
    "word/footer1.xml",
    "docProps/core.xml",
    "docProps/custom.xml",
}
REQUIRED_STYLES = [
    "HFUTTitleCN", "HFUTTitleEN", "HFUTAuthorsCN", "HFUTAuthorsEN",
    "HFUTAffiliationCN", "HFUTAffiliationEN", "HFUTAbstractLabelCN",
    "HFUTAbstractBodyCN", "HFUTAbstractLabelEN", "HFUTAbstractBodyEN",
    "HFUTKeywordsLabelCN", "HFUTKeywordsBodyCN", "HFUTKeywordsLabelEN",
    "HFUTKeywordsBodyEN", "HFUTClassification", "HFUTBody", "HFUTHeading1",
    "HFUTHeading2", "HFUTHeading3", "HFUTEquation", "HFUTFigureCaption",
    "HFUTTableCaption", "HFUTTableContent", "HFUTReferenceHeading",
    "HFUTReferenceEntry", "HFUTAuthorBiography", "HFUTFunding",
    "HFUTAcknowledgement", "HFUTThreeLineTable",
]
COMMON_STYLES = [
    "Normal", "BodyText", "Title", "Subtitle", "Author", "Abstract",
    "Heading1", "Heading2", "Heading3", "Caption", "Table", "Bibliography",
]
IDENTITY_MARKERS = [
    "DERIVED_REFERENCE_DOCX_CANDIDATE",
    "NOT_OFFICIAL_JOURNAL_TEMPLATE",
    "NOT_FINAL_SUBMISSION_FILE",
    "PENDING_PANDOC_POC",
    "PENDING_MICROSOFT_WORD_REVIEW",
]
FORBIDDEN_SOURCE_CONTENT = [
    "排版格式及相关要求",
    "插图要求及示例",
    "表格要求及示例",
    "参考文献要求及示例",
    "张光明",
    "李 四",
    "230009",
    "收稿日期",
    "修回日期",
    "基金项目",
]
TBLPR_ORDER = (
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
    "tblDescription", "tblPrChange",
)


def attr(element: ET.Element, name: str) -> str | None:
    return element.attrib.get(f"{{{W}}}{name}") or element.attrib.get(name)


def local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def children_in_order(element: ET.Element, order: tuple[str, ...]) -> bool:
    rank = {name: index for index, name in enumerate(order)}
    known = [rank[local_name(child)] for child in element if local_name(child) in rank]
    return known == sorted(known)


def check(path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not path.exists():
        return False, [f"missing DOCX: {path}"]
    try:
        with zipfile.ZipFile(path) as package:
            bad = package.testzip()
            if bad:
                errors.append(f"ZIP CRC failure: {bad}")
            names = set(package.namelist())
            missing = sorted(REQUIRED_PARTS - names)
            if missing:
                errors.append("missing OOXML parts: " + ", ".join(missing))
            raw = {name: package.read(name) for name in names if name.endswith((".xml", ".rels"))}
    except (OSError, zipfile.BadZipFile) as exc:
        return False, [f"invalid DOCX ZIP: {exc}"]

    def root(part: str) -> ET.Element | None:
        try:
            return ET.fromstring(raw[part])
        except (KeyError, ET.ParseError) as exc:
            errors.append(f"invalid XML {part}: {exc}")
            return None

    document = root("word/document.xml")
    styles = root("word/styles.xml")
    numbering = root("word/numbering.xml")
    footer = root("word/footer1.xml")
    core = root("docProps/core.xml")
    custom = root("docProps/custom.xml")

    if document is not None:
        sect = document.find(".//w:sectPr", NS)
        if sect is None:
            errors.append("document has no sectPr")
        else:
            pg = sect.find("w:pgSz", NS)
            mar = sect.find("w:pgMar", NS)
            cols = sect.find("w:cols", NS)
            if pg is None or attr(pg, "w") != "11906" or attr(pg, "h") != "16838":
                errors.append("page size is not A4 11906x16838 twips")
            expected_margins = {"top": "1361", "bottom": "1134", "left": "1304", "right": "1304", "gutter": "0"}
            if mar is None or any(attr(mar, key) != value for key, value in expected_margins.items()):
                errors.append("page margins are not 2.4/2.0/2.3/2.3 cm with zero gutter")
            if cols is None or attr(cols, "num") != "1":
                errors.append("default section is not the declared single-column front-matter candidate")

    style_elements: dict[str, ET.Element] = {}
    if styles is not None:
        style_elements = {element.attrib.get(f"{{{W}}}styleId", ""): element for element in styles.findall("w:style", NS)}
        for style_id in REQUIRED_STYLES + COMMON_STYLES:
            if style_id not in style_elements:
                errors.append(f"missing required style: {style_id}")
        if len(style_elements) != len(set(style_elements)):
            errors.append("duplicate style IDs")
        for style_id in ("HFUTBody", "HFUTHeading1", "HFUTHeading2", "HFUTHeading3", "HFUTFigureCaption", "HFUTTableCaption", "HFUTReferenceEntry"):
            if style_id not in style_elements:
                continue
            style = style_elements[style_id]
            rpr_element = style.find("w:rPr", NS)
            ppr_element = style.find("w:pPr", NS)
            if rpr_element is None or rpr_element.find("w:rFonts", NS) is None or rpr_element.find("w:sz", NS) is None:
                errors.append(f"style {style_id} lacks font/size")
            if ppr_element is None or ppr_element.find("w:jc", NS) is None:
                errors.append(f"style {style_id} lacks paragraph alignment")
        table_style = style_elements.get("HFUTThreeLineTable")
        if table_style is not None:
            if any(not children_in_order(node, TBLPR_ORDER)
                   for node in table_style.findall(".//w:tblPr", NS)):
                errors.append("three-line table style has invalid tblPr child order")
            border_nodes = table_style.findall(".//w:tblBorders", NS)
            border_values = []
            inside_v_values = []
            for border_node in border_nodes:
                for border in list(border_node):
                    border_name = border.tag.rsplit("}", 1)[-1]
                    border_values.append((border_name, attr(border, "val") or "", attr(border, "sz") or ""))
                    if border.tag == f"{{{W}}}insideV":
                        inside_v_values.append(attr(border, "val"))
            if ("top", "single", "8") not in border_values or ("bottom", "single", "8") not in border_values or ("insideH", "single", "4") not in border_values:
                errors.append("three-line table style lacks 1 pt / 0.5 pt borders")
            if "nil" not in inside_v_values:
                errors.append("three-line table style does not explicitly disable inside vertical borders")
    if numbering is not None:
        levels = numbering.findall(".//w:lvl", NS)
        if numbering.findall(".//w:lvl/w:rPr/w:rPr", NS):
            errors.append("numbering level contains nested w:rPr")
        level_texts = [attr(level.find("w:lvlText", NS), "val") if level.find("w:lvlText", NS) is not None else None for level in levels]
        for expected in ("%1", "%1.%2", "%1.%2.%3", "0"):
            if expected not in level_texts:
                errors.append(f"numbering candidate missing level text {expected}")
    if footer is not None:
        instructions = " ".join((node.text or "") for node in footer.findall(".//w:instrText", NS))
        instructions += " " + " ".join(attr(node, "instr") or "" for node in footer.findall(".//w:fldSimple", NS))
        if "PAGE" not in instructions:
            errors.append("footer has no PAGE field")
    all_text = ""
    for payload in raw.values():
        try:
            parsed = ET.fromstring(payload)
            all_text += " ".join(text for text in parsed.itertext() if text) + "\n"
        except ET.ParseError:
            pass
    for marker in IDENTITY_MARKERS:
        if marker not in all_text:
            errors.append(f"missing template identity marker: {marker}")
    for forbidden in FORBIDDEN_SOURCE_CONTENT:
        if forbidden in all_text:
            errors.append(f"source/real-content marker found: {forbidden}")
    if core is not None:
        core_text = " ".join(text for text in core.itertext() if text)
        if "PAPER_PROJECT_AI" not in core_text or "NOT_FINAL_SUBMISSION_FILE" not in core_text:
            errors.append("core properties do not carry candidate identity")
    if custom is not None:
        custom_text = " ".join(text for text in custom.itertext() if text)
        if "ColumnStrategy" not in raw["docProps/custom.xml"].decode("utf-8", errors="ignore") or "body double-column target" not in custom_text:
            errors.append("custom properties do not record column strategy")
    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    ok, errors = check(args.docx)
    sha = hashlib.sha256(args.docx.read_bytes()).hexdigest() if args.docx.exists() else "MISSING"
    print(f"docx={args.docx}")
    print(f"sha256={sha}")
    print("verdict=PASS" if ok else "verdict=FAIL")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
