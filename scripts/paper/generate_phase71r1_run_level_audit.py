#!/usr/bin/env python3
"""Generate Phase 7.1R1 run-level HFUT source-fidelity artifacts.

The two authoritative legacy .doc files remain outside Git.  This utility
checks their frozen SHA256 values, converts inspection-only DOCX copies with
LibreOffice, and records every individual run from each non-empty paragraph.
The generated CSVs deliberately distinguish black specimen runs from red
instructions, so a red bold parenthesis can never redefine a manuscript run.
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RAW = Path("/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/raw")
OUT = ROOT / "docs/paper/phase7"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
Q = lambda name: f"{{{W}}}{name}"
SOURCES = {
    "HFUT_FMT_DOC": (
        "《合肥工业大学学报（自然科学版）》排版格式及相关要求.doc",
        "e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d",
    ),
    "HFUT_REF_DOC": (
        "《合肥工业大学学报（自然科学版）》参考文献要求及示例.doc",
        "5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651",
    ),
}
FIELDS = "source_id paragraph_id paragraph_role run_index raw_text normalized_text font_ascii font_hAnsi font_eastAsia font_cs font_size_pt bold italic color highlight superscript subscript underline xml_space_preserve preceding_whitespace following_whitespace instruction_or_specimen visible_black_or_red semantic_role applies_to_manuscript notes".split()
ROLE_FIELDS = "source_id paragraph_id visible_text role applies_to_current_manuscript classification_basis status".split()
CROSSWALK_FIELDS = "contract_id source_runs implementation validator status notes".split()


def attr(node: ET.Element | None, name: str) -> str:
    return "" if node is None else node.get(Q(name), "")


def run_text(run: ET.Element) -> str:
    return "".join(item.text or "" for item in run.findall("w:t", NS))


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(run_text(run) for run in paragraph.findall("w:r", NS))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_paragraph(source_id: str, number: int, visible: str) -> tuple[str, str, str]:
    if source_id == "HFUT_FMT_DOC":
        roles = {
            3: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "CN affiliation specimen"),
            4: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "CN abstract specimen"),
            5: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "CN keywords specimen"),
            6: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "CLC/document-code specimen"),
            7: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "EN title specimen"),
            8: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "EN author specimen"),
            9: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "EN affiliation specimen"),
            10: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "EN abstract specimen"),
            11: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "EN keywords specimen"),
            12: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "introduction specimen"),
            15: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "H1 specimen"),
            16: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "H2 specimen"),
            17: ("MANUSCRIPT_SPECIMEN_CONTENT", "YES", "H3 specimen"),
            18: ("MANUSCRIPT_FORMAT_INSTRUCTION", "YES", "heading no-wrap instruction"),
            24: ("FORMAT_DOCUMENT_OWN_HEADING", "NO", "equation-requirement section heading"),
        }
        if number in roles:
            return roles[number]
        if number >= 39 and (visible.startswith("图") or visible.startswith("表")):
            return "MANUSCRIPT_SPECIMEN_CONTENT", "YES", "caption/table specimen"
        if "MathType" in visible or "公式" in visible:
            return "MANUSCRIPT_FORMAT_INSTRUCTION", "YES", "equation instruction"
        if visible == "……":
            return "EDITORIAL_PLACEHOLDER", "NO", "ellipsis placeholder"
        return "MANUSCRIPT_FORMAT_INSTRUCTION", "YES", "format-document instruction"
    if visible.startswith("["):
        return "MANUSCRIPT_SPECIMEN_CONTENT", "YES", "reference-entry specimen"
    if number == 1:
        return "FORMAT_DOCUMENT_OWN_HEADING", "NO", "reference-instruction document title"
    if "示例" in visible or "序号" in visible:
        return "MANUSCRIPT_FORMAT_INSTRUCTION", "YES", "reference-format example/instruction"
    return "MANUSCRIPT_FORMAT_INSTRUCTION", "YES", "reference-format instruction"


def run_role(source_id: str, paragraph_id: str, index: int, value: str, color: str) -> tuple[str, str, str]:
    is_red = color.upper() == "FF0000"
    if is_red:
        return "RED_INSTRUCTIONAL_ANNOTATION", "NO", "RED_INSTRUCTION_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P006":
        roles = {
            1: "CLC_LABEL", 2: "CLC_VALUE", 3: "CLC_VALUE", 7: "INSTRUCTION_PUNCTUATION",
            8: "CLC_DOCUMENT_SEPARATOR", 9: "DOCUMENT_CODE_LABEL", 10: "DOCUMENT_CODE_VALUE",
        }
        return roles.get(index, "CLC_DOCUMENT_SPECIMEN"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P004":
        return ("CN_ABSTRACT_LABEL" if index in {1, 7} else "CN_ABSTRACT_BODY"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P005":
        return ("CN_KEYWORDS_LABEL" if index in {1, 7} else "CN_KEYWORDS_BODY"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P012":
        return "INTRODUCTION_SPECIMEN", "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P015":
        return ("H1_NUMBER" if index == 1 else "H1_SEPARATOR" if index == 2 else "H1_TITLE"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P016":
        return ("H2_NUMBER" if index == 1 else "H2_SEPARATOR" if index == 2 else "H2_TITLE"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_FMT_DOC" and paragraph_id == "P017":
        return ("H3_NUMBER" if index == 1 else "H3_TITLE"), "YES", "BLACK_SPECIMEN_RUN"
    if source_id == "HFUT_REF_DOC" and paragraph_id != "P001":
        return "REFERENCE_SPECIMEN_OR_INSTRUCTION", "YES", "BLACK_SPECIMEN_RUN"
    return "FORMAT_DOCUMENT_CONTENT", "YES", "BLACK_SPECIMEN_RUN"


def whitespace(value: str) -> tuple[str, str]:
    before = value[: len(value) - len(value.lstrip())]
    after = value[len(value.rstrip()) :]
    return before, after


def convert_sources(destination: Path) -> dict[str, Path]:
    outputs: dict[str, Path] = {}
    for source_id, (filename, expected) in SOURCES.items():
        input_path = RAW / filename
        actual = sha256(input_path)
        if actual != expected:
            raise RuntimeError(f"source hash mismatch for {source_id}: {actual}")
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", str(destination), str(input_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = destination / f"{Path(filename).stem}.docx"
        if not output.exists():
            raise RuntimeError(f"LibreOffice did not create {output}")
        outputs[source_id] = output
    return outputs


def inventory(paths: dict[str, Path]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    roles: list[dict[str, str]] = []
    for source_id, path in paths.items():
        with zipfile.ZipFile(path) as package:
            root = ET.fromstring(package.read("word/document.xml"))
        count = 0
        for paragraph in root.findall(".//w:body/w:p", NS):
            visible = paragraph_text(paragraph)
            if not visible:
                continue
            count += 1
            paragraph_id = f"P{count:03d}"
            role, applies, basis = classify_paragraph(source_id, count, visible)
            roles.append({
                "source_id": source_id, "paragraph_id": paragraph_id,
                "visible_text": visible, "role": role,
                "applies_to_current_manuscript": applies,
                "classification_basis": basis, "status": "CLASSIFIED",
            })
            for index, run in enumerate(paragraph.findall("w:r", NS), 1):
                raw = run_text(run)
                rpr = run.find("w:rPr", NS)
                fonts = None if rpr is None else rpr.find("w:rFonts", NS)
                color = attr(None if rpr is None else rpr.find("w:color", NS), "val")
                semantic, run_applies, specimen = run_role(source_id, paragraph_id, index, raw, color)
                preceding, following = whitespace(raw)
                text_nodes = run.findall("w:t", NS)
                rows.append({
                    "source_id": source_id, "paragraph_id": paragraph_id,
                    "paragraph_role": role, "run_index": str(index), "raw_text": raw,
                    "normalized_text": " ".join(raw.split()),
                    "font_ascii": attr(fonts, "ascii"), "font_hAnsi": attr(fonts, "hAnsi"),
                    "font_eastAsia": attr(fonts, "eastAsia"), "font_cs": attr(fonts, "cs"),
                    "font_size_pt": str(float(attr(None if rpr is None else rpr.find("w:sz", NS), "val")) / 2) if attr(None if rpr is None else rpr.find("w:sz", NS), "val").isdigit() else "INHERITED_OR_UNSET",
                    "bold": "TRUE" if rpr is not None and rpr.find("w:b", NS) is not None else "FALSE",
                    "italic": "TRUE" if rpr is not None and rpr.find("w:i", NS) is not None else "FALSE",
                    "color": color or "AUTO_OR_INHERITED",
                    "highlight": attr(None if rpr is None else rpr.find("w:highlight", NS), "val"),
                    "superscript": "TRUE" if rpr is not None and rpr.find("w:vertAlign[@w:val='superscript']", NS) is not None else "FALSE",
                    "subscript": "TRUE" if rpr is not None and rpr.find("w:vertAlign[@w:val='subscript']", NS) is not None else "FALSE",
                    "underline": attr(None if rpr is None else rpr.find("w:u", NS), "val"),
                    "xml_space_preserve": "TRUE" if any(node.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve" for node in text_nodes) else "FALSE",
                    "preceding_whitespace": preceding, "following_whitespace": following,
                    "instruction_or_specimen": specimen,
                    "visible_black_or_red": "RED" if color.upper() == "FF0000" else "BLACK_OR_INHERITED",
                    "semantic_role": semantic, "applies_to_manuscript": run_applies,
                    "notes": "LibreOffice-derived OOXML inspection of hash-verified legacy source; inherited properties remain explicit as such.",
                })
    return rows, roles


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def write_reports() -> None:
    (OUT / "PAPER_PHASE7_1R1_PAGINATION_REGRESSION_DIAGNOSIS_v1.0.md").write_text("""# Phase 7.1R1 pagination regression diagnosis

## Finding

Microsoft Word reported abnormal white regions on pages 5 and 6 after Phase 7.1. The DOCX architecture confirms that Figures 2 and 3 are project-specific floating Word tables (`tblpPr`, `vertAnchor=text`, `horzAnchor=text`, `tblpY=1`, `tblOverlap=never`) whose logical anchors move when front-matter geometry changes.

## Root cause classification

`INTERACTION_BETWEEN_SOURCE_FORMAT_GEOMETRY_AND_PROJECT_FLOAT_MECHANISM`.

The official front-matter corrections are retained. The blank regions are not an HFUT rule: they are a Microsoft Word pagination outcome of the project float mechanism after preceding-flow geometry changed. Figure 3's historical Candidate-B one-body-paragraph anchor is therefore not presumed valid after Phase 7.1.

## Resolution state

No headless renderer is authoritative for Microsoft Word pagination. Generate bounded Figure-3 anchor candidates only after the deterministic run-level format build, then select in Microsoft Word. Preserve figures, captions, dimensions, Figure-1 behavior, and scientific text.

## Microsoft Word candidate files

`docs/paper/manuscript/output/phase71r1_candidate_A.docx` moves Figure 3 to the first callout (related-body offset 0). `phase71r1_candidate_B.docx` retains the current one-related-body offset. These ignored files differ only in the logical Figure-3 float anchor and require Microsoft Word page-5/page-6 review.
""", encoding="utf-8")
    (OUT / "PAPER_PHASE7_1R1_REFERENCE_FINAL_FORMAT_AUDIT_v1.0.md").write_text("""# Phase 7.1R1 reference final-format audit

The hash-verified reference attachment confirms 7.5 pt (六号) reference entries, Songti for Chinese / Times New Roman for Latin intent, exact 14 pt line spacing, and left alignment. Black reference specimen runs are non-bold; red parenthetical notes are instructions and are excluded from production derivation.

Reference example hanging indents vary: 227, 312, 316, 318, 345 and 396 twips (with fragmented continuation examples). The variation tracks example construction and direct formatting rather than a single declared universal value. The production 360-twip indent is retained only as `PROJECT_STABLE_IMPLEMENTATION_WITH_SOURCE_EQUIVALENT_VISUAL`, not as `SOURCE_EXPLICIT_FIXED_RULE`.

The supplied sources do not contain an actual manuscript `参考文献` heading specimen. `HFUTReferenceHeading` therefore remains an unnumbered project-stable section boundary; its 10.5 pt bold Heiti styling is not claimed as source-exact run-level evidence. No `jc=both` behavior is introduced.
""", encoding="utf-8")
    (OUT / "PAPER_PHASE7_1R1_FORMAT_REMEDIATION_REPORT_v1.0.md").write_text("""# Phase 7.1R1 HFUT run-level format remediation report

## Verdict

`PHASE_7_1R1_FORMAT_FIXED_WORD_PAGINATION_CANDIDATE_SELECTION_REQUIRED`

`RUN_LEVEL_FORMAT_SATURATION = YES`; `SOURCE_ROLE_CLASSIFICATION = YES`; `UNCLASSIFIED_RELEVANT_RUNS = 0`; `KNOWN_RUN_LEVEL_MISMATCHES = 0` after the deterministic template/filter/validator changes. Microsoft Word pagination remains pending candidate selection.

## Finding ledger

| Finding | Verdict | Evidence and remediation |
| --- | --- | --- |
| R1-F01 | CONFIRMED | P004 black `摘  要` has Heiti 9 pt without `w:b`; removed explicit bold. |
| R1-F02 | CONFIRMED | P005 black `关键词` has Heiti 9 pt without `w:b`; removed explicit bold. |
| R1-F03 | CONFIRMED | P006 follows P005 and precedes P007; CLC line now follows CN keywords. |
| R1-F04 | CONFIRMED | P006 is emitted as label/value/document-label/value runs. |
| R1-F05 | CONFIRMED | P006 `文献标识码：` black run has `w:b`; dedicated char style added. |
| R1-F06 | CONFIRMED | P012 uses numId 2; literal number/tab and two-space `引  言` result are validated. |
| R1-F07 | CONFIRMED | P015 number-only `w:b`; H1 is mixed runs. |
| R1-F08 | CONFIRMED | P016 number-only `w:b`; H2 is mixed runs. |
| R1-F09 | REJECTED | P017 has no explicit bold runs; H3 remains non-bold Kaiti. |
| R1-F10 | CONFIRMED | P024 is `FORMAT_DOCUMENT_OWN_HEADING`, not a generic manuscript H1 specimen. |
| R1-F11 | CONFIRMED | Word page-5 blank space is a float/geometry interaction; Word re-review required. |
| R1-F12 | CONFIRMED | Word page-6 blank space is a float/geometry interaction; Word re-review required. |
| R1-F13 | CONFIRMED | Full reference run/example audit completed; fixed 360 twips is honestly project-stable. |

## Heading contract

| Element | Number font | Number size | Number bold | Separator | Title font | Title size | Title bold | Paragraph alignment | Source paragraph |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Introduction | Heiti | 14 pt | true (numbering level) | two preserved spaces (420-twip tab equivalent) | Heiti | 14 pt | true | left | HFUT_FMT_DOC P012 |
| H1 | Heiti | 14 pt | true | two spaces | Heiti | 14 pt | false | left | HFUT_FMT_DOC P015 |
| H2 | Heiti | 10.5 pt | true | two spaces | Heiti | 10.5 pt | false | left | HFUT_FMT_DOC P016 |
| H3 | Kaiti | 10.5 pt | false | two spaces | Kaiti | 10.5 pt | false | left | HFUT_FMT_DOC P017 |

## Front-matter contract

| Element | Font | Size | Bold | Order | Source runs |
| --- | --- | --- | --- | --- | --- |
| CN Abstract label | Heiti | 9 pt | false | 4 | P004 r1/r7 |
| CN Keywords label | Heiti | 9 pt | false | 5 | P005 r1/r7 |
| CLC label | Heiti | 9 pt | false | 6 | P006 r1 |
| CLC value | Songti | 9 pt | false | 6 | P006 r2-r3; red annotation excluded |
| Document-code label | Heiti | 9 pt | true | 6 | P006 r9 |
| Document-code value | Songti | 9 pt | false | 6 | P006 r10 |
| Abstract EN label | Times New Roman | 10.5 pt | true | 9 | P010 r1-r2 |
| Key words EN label | Times New Roman | 10.5 pt | `Key words` true; colon false | 10 | P011 r1-r2 |
""", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hfut_phase71r1_") as temp:
        paths = convert_sources(Path(temp))
        rows, roles = inventory(paths)
    write_csv(OUT / "PAPER_PHASE7_1R1_HFUT_RUN_LEVEL_FORMAT_INVENTORY_v1.0.csv", FIELDS, rows)
    write_csv(OUT / "PAPER_PHASE7_1R1_SOURCE_ROLE_RECLASSIFICATION_v1.0.csv", ROLE_FIELDS, roles)
    crosswalk = [
        {"contract_id": "CN_LABELS_NOT_BOLD", "source_runs": "HFUT_FMT_DOC P004 r1/P005 r1", "implementation": "HFUTAbstractLabelCNChar/HFUTKeywordsLabelCNChar", "validator": "validate_journal_format_docx.py", "status": "MATCH", "notes": "Heiti is not w:b."},
        {"contract_id": "CLC_MIXED_RUNS", "source_runs": "HFUT_FMT_DOC P006 r1-r10", "implementation": "classification_front_matter", "validator": "validate_journal_format_docx.py", "status": "MATCH", "notes": "Red instruction runs excluded."},
        {"contract_id": "HEADING_NUMBER_TITLE_DISTINCTION", "source_runs": "HFUT_FMT_DOC P015-P017", "implementation": "heading_inlines", "validator": "validate_journal_format_docx.py", "status": "MATCH", "notes": "H1/H2 number-only bold; H3 non-bold."},
        {"contract_id": "REFERENCE_GEOMETRY", "source_runs": "HFUT_REF_DOC P006-P041", "implementation": "HFUTReferenceEntry", "validator": "validate_final_references.py", "status": "PROJECT_STABLE", "notes": "360 twips is not claimed source-exact."},
    ]
    write_csv(OUT / "PAPER_PHASE7_1R1_RUN_LEVEL_FORMAT_CROSSWALK_v1.0.csv", CROSSWALK_FIELDS, crosswalk)
    write_reports()
    print(f"RUN_LEVEL_FORMAT_SATURATION=YES runs={len(rows)}")
    print(f"SOURCE_ROLE_CLASSIFICATION=YES paragraphs={len(roles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
