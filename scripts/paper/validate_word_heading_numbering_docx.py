#!/usr/bin/env python3
"""Reject automatic Word numbering on explicitly numbered manuscript headings."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
HEADING_STYLES = {
    "HFUTHeading1",
    "HFUTHeading2",
    "HFUTHeading3",
    "Heading1",
    "Heading2",
    "Heading3",
}
REQUIRED_HEADINGS = {
    "0 引言": "HFUTHeading1",
    "1 系统对象与问题定义": "HFUTHeading1",
    "1.1 模型、数据集与部署环境": "HFUTHeading2",
    "1.2 E2E数据路径与受控变量": "HFUTHeading2",
    "1.3 统一计时边界与研究问题": "HFUTHeading2",
    "2 数据路径工程方法": "HFUTHeading1",
    "2.1 V0：主机侧FP32张量形成": "HFUTHeading2",
    "2.2 V2R：pageable raw staging与GPU输入形成": "HFUTHeading2",
    "2.3 V3R：pinned raw staging隔离变量": "HFUTHeading2",
    "2.4 正确性与生命周期控制": "HFUTHeading2",
    "3 实验设计": "HFUTHeading1",
    "4 结果与分析": "HFUTHeading1",
    "4.1 正确性": "HFUTHeading2",
    "4.2 整体E2E性能": "HFUTHeading2",
    "4.3 数据路径分析": "HFUTHeading2",
    "4.4 运行级稳定性与尾延迟": "HFUTHeading2",
    "4.5 相关工作定位": "HFUTHeading2",
    "4.6 局限性": "HFUTHeading2",
    "5 结论": "HFUTHeading1",
}


def attr(node: ET.Element | None, local: str) -> str | None:
    return None if node is None else node.get(f"{{{W}}}{local}")


def paragraph_text(node: ET.Element) -> str:
    return "".join(child.text or "" for child in node.findall(".//w:t", NS)).strip()


def paragraph_style(node: ET.Element) -> str:
    return attr(node.find("w:pPr/w:pStyle", NS), "val") or ""


def effective_style_numpr(
    style_id: str, styles: dict[str, ET.Element]
) -> tuple[ET.Element | None, list[str]]:
    chain: list[str] = []
    while style_id and style_id not in chain:
        chain.append(style_id)
        style = styles.get(style_id)
        if style is None:
            return None, chain
        num_pr = style.find("w:pPr/w:numPr", NS)
        if num_pr is not None:
            return num_pr, chain
        style_id = attr(style.find("w:basedOn", NS), "val") or ""
    return None, chain


def audit_heading_numbering_roots(
    document: ET.Element,
    styles_root: ET.Element,
    numbering: ET.Element | None,
    *,
    require_explicit_headings: bool,
) -> tuple[list[str], list[dict[str, str]]]:
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    style_nodes: dict[str, list[ET.Element]] = {}
    for style in styles_root.findall("w:style", NS):
        style_nodes.setdefault(attr(style, "styleId") or "", []).append(style)

    for style_id in sorted(HEADING_STYLES):
        count = len(style_nodes.get(style_id, []))
        if count != 1:
            errors.append(f"heading style {style_id} count is {count}, expected 1")

    styles = {
        style_id: nodes[0]
        for style_id, nodes in style_nodes.items()
        if len(nodes) == 1
    }
    for style_id in sorted(HEADING_STYLES):
        num_pr, chain = effective_style_numpr(style_id, styles)
        if num_pr is not None:
            errors.append(
                f"heading style {style_id} has effective numPr via {' > '.join(chain)}"
            )

    if numbering is not None:
        for level in numbering.findall(".//w:lvl", NS):
            linked_style = attr(level.find("w:pStyle", NS), "val")
            if linked_style in HEADING_STYLES:
                errors.append(
                    f"numbering level links directly to heading style {linked_style}"
                )

    body = document.find("w:body", NS)
    if body is None:
        return errors + ["word/document.xml has no w:body"], rows

    heading_paragraphs: list[tuple[ET.Element, str, str]] = []
    for paragraph in body.findall("w:p", NS):
        style_id = paragraph_style(paragraph)
        if style_id not in HEADING_STYLES:
            continue
        text = paragraph_text(paragraph)
        direct = paragraph.find("w:pPr/w:numPr", NS)
        effective, chain = effective_style_numpr(style_id, styles)
        rows.append(
            {
                "heading": text,
                "style": style_id,
                "direct_numPr": "YES" if direct is not None else "NO",
                "effective_numPr": "YES" if effective is not None else "NO",
            }
        )
        heading_paragraphs.append((paragraph, style_id, text))
        if direct is not None:
            errors.append(f"heading paragraph {text!r} has direct numPr")
        if effective is not None:
            errors.append(
                f"heading paragraph {text!r} inherits numPr via {' > '.join(chain)}"
            )

    if require_explicit_headings:
        for text, expected_style in REQUIRED_HEADINGS.items():
            matches = [
                style_id
                for _, style_id, current_text in heading_paragraphs
                if current_text == text
            ]
            if matches != [expected_style]:
                errors.append(
                    f"explicit heading {text!r} styles are {matches}, expected [{expected_style!r}]"
                )

    return errors, rows


def audit_docx_heading_numbering(
    path: Path, *, require_explicit_headings: bool = True
) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                return [f"ZIP CRC failure: {bad}"], []
            document = ET.fromstring(archive.read("word/document.xml"))
            styles = ET.fromstring(archive.read("word/styles.xml"))
            numbering = (
                ET.fromstring(archive.read("word/numbering.xml"))
                if "word/numbering.xml" in archive.namelist()
                else None
            )
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        return [f"invalid DOCX package: {exc}"], []
    return audit_heading_numbering_roots(
        document,
        styles,
        numbering,
        require_explicit_headings=require_explicit_headings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", nargs="+", type=Path)
    parser.add_argument("--styles-only", action="store_true")
    args = parser.parse_args()
    all_errors: list[str] = []
    for path in args.docx:
        errors, rows = audit_docx_heading_numbering(
            path, require_explicit_headings=not args.styles_only
        )
        print(f"docx={path}")
        print("heading_text\tstyle\tdirect_numPr\teffective_numPr")
        for row in rows:
            print(
                f"{row['heading']}\t{row['style']}\t"
                f"{row['direct_numPr']}\t{row['effective_numPr']}"
            )
        if errors:
            all_errors.extend(f"{path}: {error}" for error in errors)
            print("word_heading_numbering=FAIL")
        else:
            print("word_heading_numbering=PASS")
    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
