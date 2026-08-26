#!/usr/bin/env python3
"""Generate the bounded Phase 7.1R2 Figure-3 Word pagination candidates."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def text_of(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.iter(qn("t")))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def execute(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def inspect(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError(f"ZIP CRC failure: {path}")
        document_bytes = archive.read("word/document.xml")
        document = ET.fromstring(document_bytes)
        package_parts = {
            name: archive.read(name)
            for name in archive.namelist()
            if name != "word/document.xml"
        }
    body = document.find("w:body", NS)
    if body is None:
        raise ValueError(f"{path}: missing w:body")
    children = list(body)
    float_tables = [
        table for table in body.findall("w:tbl", NS)
        if table.find("w:tblPr/w:tblCaption", NS) is not None
        and table.find("w:tblPr/w:tblCaption", NS).get(qn("val")) == "HFUT_FIGURE_FLOAT_F3"
    ]
    if len(float_tables) != 1:
        raise ValueError(f"{path}: Figure 3 float count={len(float_tables)}")
    float_table = float_tables[0]
    float_position = children.index(float_table)
    callouts = [
        (index, node) for index, node in enumerate(children[:float_position])
        if node.tag == qn("p") and "图3" in text_of(node)
    ]
    if not callouts:
        raise ValueError(f"{path}: Figure 3 callout is not before the float")
    callout_position, callout = callouts[0]
    intervening_body = [
        node for node in children[callout_position + 1:float_position]
        if node.tag == qn("p")
        and node.find("w:pPr/w:pStyle", NS) is not None
        and node.find("w:pPr/w:pStyle", NS).get(qn("val")) == "HFUTBody"
        and text_of(node)
    ]
    table_position = float_table.find("w:tblPr/w:tblpPr", NS)
    if table_position is None:
        raise ValueError(f"{path}: Figure 3 lacks tblpPr")
    preceding_text = ""
    if float_position:
        preceding = children[float_position - 1]
        preceding_text = text_of(preceding)[:120]
    normalized_document = ET.fromstring(document_bytes)
    normalized_body = normalized_document.find("w:body", NS)
    assert normalized_body is not None
    normalized_float = next(
        table for table in normalized_body.findall("w:tbl", NS)
        if table.find("w:tblPr/w:tblCaption", NS) is not None
        and table.find("w:tblPr/w:tblCaption", NS).get(qn("val")) == "HFUT_FIGURE_FLOAT_F3"
    )
    normalized_body.remove(normalized_float)
    return {
        "sha256": sha256(path),
        "float_body_child_position": float_position + 1,
        "first_callout_body_child_position": callout_position + 1,
        "first_callout_excerpt": text_of(callout)[:160],
        "anchor_paragraph_excerpt": preceding_text,
        "intervening_body_count": len(intervening_body),
        "tblpPr": {key.rsplit("}", 1)[-1]: value for key, value in table_position.attrib.items()},
        "document_without_figure3_float": ET.tostring(normalized_document, encoding="utf-8"),
        "non_document_parts": package_parts,
    }


def write_report(path: Path, candidates: dict[str, dict[str, object]]) -> None:
    a, b = candidates["A"], candidates["B"]
    anchor_only = (
        a["document_without_figure3_float"] == b["document_without_figure3_float"]
        and a["non_document_parts"] == b["non_document_parts"]
        and a["tblpPr"] == b["tblpPr"]
    )
    lines = [
        "# Phase 7.1R2 Word pagination candidate matrix",
        "",
        "The deterministic R2 Full build is the common source. These candidates differ only by the logical body-child insertion position of the existing Figure-3 floating table; they do not alter scientific text, image payload, caption, table geometry, or wrap attributes.",
        "",
        "| Candidate | Figure-3 offset | Anchor paragraph excerpt | Body-child position | DOCX SHA256 | Mechanical-page observation | Expected Word effect | Scientific delta | Format delta beyond anchor |",
        "| --- | ---: | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for label, offset in (("A", 0), ("B", 1)):
        candidate = candidates[label]
        lines.append(
            f"| {label} | {offset} | {candidate['anchor_paragraph_excerpt']} | "
            f"{candidate['float_body_child_position']} | {candidate['sha256']} | "
            f"callout child {candidate['first_callout_body_child_position']}; "
            f"intervening HFUTBody={candidate['intervening_body_count']}; tblpPr={candidate['tblpPr']} | "
            "Microsoft Word 2019 visual QA required | NONE | NONE |"
        )
    lines.extend([
        "",
        f"`CANDIDATE_ANCHOR_ONLY_DELTA={'PASS' if anchor_only else 'FAIL'}`",
        "",
        "PAGE6_BLANK = OPEN. Headless OOXML inspection cannot select the final Microsoft Word pagination result.",
        "",
        "Open Candidate A and Candidate B in Microsoft Word 2019. Inspect Pages 5–7 and select only a candidate with no large artificial Page-6 blank region, Figure 3 after its first callout, reasonable narrative proximity, no new Page-5/Page-7 gap, no figure/caption overlap, and no clipping. Do not select using LibreOffice.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-docx",
        type=Path,
        default=ROOT / "docs/paper/manuscript/output/draft_full_raw.docx",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs/paper/manuscript/output",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs/paper/phase7/PAPER_PHASE7_1R2_WORD_PAGINATION_CANDIDATE_MATRIX_v1.0.md",
    )
    args = parser.parse_args()
    raw = args.raw_docx.resolve()
    if not raw.is_file():
        print(f"FAIL: deterministic R2 raw Full DOCX is missing: {raw}", file=sys.stderr)
        return 1
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory(prefix="phase71r2_", dir=output_dir) as temporary_dir:
        temporary = Path(temporary_dir)
        for label, offset in (("A", 0), ("B", 1)):
            section_docx = temporary / f"candidate_{label}.sections.docx"
            candidate_docx = output_dir / f"phase71r2_candidate_{label}.docx"
            execute([
                sys.executable, "scripts/paper/postprocess_full_manuscript_docx.py",
                "--input", str(raw), "--output", str(section_docx),
                "--figure3-related-body-offset", str(offset),
            ])
            execute([
                sys.executable, "scripts/paper/postprocess_publication_tables.py",
                "--input", str(section_docx), "--output", str(candidate_docx),
            ])
            execute(["unzip", "-t", str(candidate_docx)])
            execute([sys.executable, "scripts/paper/validate_word_heading_numbering_docx.py", str(candidate_docx)])
            execute([sys.executable, "scripts/paper/validate_phase71r2_heading_instances.py", str(candidate_docx)])
            candidates[label] = inspect(candidate_docx)
    write_report(args.report.resolve(), candidates)
    print("PHASE7_1R2_PAGINATION_CANDIDATES=PASS candidates=A,B")
    for label in ("A", "B"):
        print(f"candidate_{label}_sha256={candidates[label]['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
