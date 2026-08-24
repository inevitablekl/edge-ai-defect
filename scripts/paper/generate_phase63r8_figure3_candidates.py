#!/usr/bin/env python3
"""Generate bounded Figure 3 logical-anchor candidates from an R7 DOCX.

This helper changes only the top-level story position of the existing Figure 3
floating table.  It does not alter the drawing, caption, positioning metadata,
or manuscript text.  Candidate offsets are counted in related ``HFUTBody``
paragraphs after the first Figure 3 callout, so no named heading is used as an
anchor rule.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
FIGURE3_LABEL = "图3"
FIGURE3_MARKER = "HFUT_FIGURE_FLOAT_F3"

ET.register_namespace("w", W)


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def attr(element: ET.Element | None, local: str) -> str | None:
    return None if element is None else element.get(qn(local))


def paragraph_text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.findall(".//w:t", NS)).strip()


def paragraph_style(element: ET.Element) -> str | None:
    return attr(element.find("w:pPr/w:pStyle", NS), "val")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relocate_figure3(document_xml: bytes, body_paragraph_offset: int) -> bytes:
    root = ET.fromstring(document_xml)
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")

    children = list(body)
    floats = [
        node
        for node in children
        if node.tag == qn("tbl")
        and attr(node.find("w:tblPr/w:tblCaption", NS), "val") == FIGURE3_MARKER
    ]
    if len(floats) != 1:
        raise ValueError(f"expected one Figure 3 float, found {len(floats)}")
    figure = floats[0]
    figure_index = children.index(figure)

    callouts = [
        node
        for node in children[:figure_index]
        if node.tag == qn("p") and FIGURE3_LABEL in paragraph_text(node)
    ]
    if not callouts:
        raise ValueError("Figure 3 has no preceding textual callout")
    first_callout = callouts[0]

    body.remove(figure)
    children = list(body)
    callout_index = children.index(first_callout)
    related_body = []
    for node in children[callout_index + 1 :]:
        if node.tag == qn("p") and paragraph_style(node) == "HFUTBody" and paragraph_text(node):
            related_body.append(node)
            if len(related_body) == body_paragraph_offset:
                break
        elif node.tag == qn("p") and (paragraph_style(node) or "").startswith("HFUTHeading"):
            break

    if len(related_body) != body_paragraph_offset:
        raise ValueError(
            "Figure 3 candidate offset exceeds the related body paragraphs "
            f"before the next heading: requested={body_paragraph_offset} found={len(related_body)}"
        )

    anchor = first_callout if body_paragraph_offset == 0 else related_body[-1]
    body.insert(list(body).index(anchor) + 1, figure)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite(input_path: Path, output_path: Path, body_paragraph_offset: int) -> None:
    if body_paragraph_offset == 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(input_path, output_path)
        return

    with zipfile.ZipFile(input_path) as source:
        document_xml = relocate_figure3(
            source.read("word/document.xml"), body_paragraph_offset
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent, suffix=".docx", delete=False
        ) as handle:
            temporary = Path(handle.name)
        try:
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as target:
                for source_info in source.infolist():
                    payload = (
                        document_xml
                        if source_info.filename == "word/document.xml"
                        else source.read(source_info.filename)
                    )
                    info = zipfile.ZipInfo(source_info.filename, (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o600 << 16
                    target.writestr(info, payload)
            temporary.replace(output_path)
        finally:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--body-paragraph-offset", required=True, type=int, choices=(0, 1, 2)
    )
    args = parser.parse_args()
    rewrite(args.input, args.output, args.body_paragraph_offset)
    print(
        "PHASE63R8_FIGURE3_CANDIDATE=PASS "
        f"offset={args.body_paragraph_offset} output={args.output} sha256={sha256(args.output)}"
    )
    print("MICROSOFT_WORD_PAGINATION_STATUS=PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
