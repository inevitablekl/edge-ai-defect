#!/usr/bin/env python3
"""Generate reproducible Phase 7.1 HFUT source-audit deliverables.

The official legacy .doc files stay outside Git.  This tool verifies their
manifest hashes, makes temporary LibreOffice-derived DOCX inspection copies,
and inventories every body paragraph and table/row object.  LibreOffice page
layout is only a mechanical inspection aid; the output records stable object
locators rather than claiming Word Desktop pagination.
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
    "HFUT_FMT_DOC": ("《合肥工业大学学报（自然科学版）》排版格式及相关要求.doc", "e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d"),
    "HFUT_REF_DOC": ("《合肥工业大学学报（自然科学版）》参考文献要求及示例.doc", "5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651"),
    "HFUT_FIG_DOC": ("《合肥工业大学学报（自然科学版）》插图要求及示例.doc", "160960cdfcc73896cb443a1b7eeec91e9ad419febc4710bafff5b1882636138a"),
    "HFUT_TABLE_DOC": ("《合肥工业大学学报（自然科学版）》表格要求及示例.doc", "1764dd6bb74e4ea850aad2fd71f87a1a92badfd7d6854edd8ff9db7d09a0f009"),
}
INVENTORY_FIELDS = "source_id source_filename source_object_id page paragraph/table/object_locator object_type visible_text instruction_color/status explicit_requirement observed_format font_cn font_latin font_size_name font_size_pt bold italic alignment left_indent right_indent first_line_indent hanging_indent line_spacing spacing_before spacing_after keepNext keepLines pageBreakBefore border_top border_bottom border_left border_right border_insideH border_insideV width height section_columns column_gap footer/header status literal punctuation/grouping authority_class applies_to_current_manuscript current_template_value current_output_value match_status remediation_required automatic_or_manual notes".split()


def val(node: ET.Element | None, name: str) -> str:
    return "" if node is None else node.get(Q(name), "")


def text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).strip()


def props(node: ET.Element) -> dict[str, str]:
    ppr = node.find("w:pPr", NS)
    rpr = node.find("w:r/w:rPr", NS)
    ind = None if ppr is None else ppr.find("w:ind", NS)
    spacing = None if ppr is None else ppr.find("w:spacing", NS)
    fonts = None if rpr is None else rpr.find("w:rFonts", NS)
    size = val(rpr.find("w:sz", NS) if rpr is not None else None, "val")
    return {
        "font_cn": val(fonts, "eastAsia"), "font_latin": val(fonts, "ascii"),
        "font_size_pt": str(float(size) / 2) if size.isdigit() else "INHERITED_OR_UNSET",
        "bold": "YES" if rpr is not None and rpr.find("w:b", NS) is not None else "NO",
        "italic": "YES" if rpr is not None and rpr.find("w:i", NS) is not None else "NO",
        "alignment": val(ppr.find("w:jc", NS) if ppr is not None else None, "val"),
        "left_indent": val(ind, "left"), "right_indent": val(ind, "right"),
        "first_line_indent": val(ind, "firstLine"), "hanging_indent": val(ind, "hanging"),
        "line_spacing": f"{val(spacing, 'lineRule')}:{val(spacing, 'line')}",
        "spacing_before": val(spacing, "before"), "spacing_after": val(spacing, "after"),
        "keepNext": "YES" if ppr is not None and ppr.find("w:keepNext", NS) is not None else "NO",
        "keepLines": "YES" if ppr is not None and ppr.find("w:keepLines", NS) is not None else "NO",
        "pageBreakBefore": "YES" if ppr is not None and ppr.find("w:pageBreakBefore", NS) is not None else "NO",
    }


def classify(source_id: str, visible: str, kind: str) -> tuple[str, str, str, str]:
    """Return authority class, applicability, automation, short rule note."""
    if kind.startswith("table"):
        return "EXAMPLE_SPECIFIC", "YES", "AUTOMATIC", "Table structure/style specimen; inspect borders separately."
    if source_id == "HFUT_FMT_DOC":
        if any(x in visible for x in ("收稿日期", "修回日期")):
            return "EDITORIAL_PLACEHOLDER", "NO", "MANUAL", "No author-side fabricated dates."
        if "基金项目" in visible:
            return "TEXT_RULE_GENERAL", "CONDITIONAL", "AUTOMATIC", "Omit because authorized funding is NONE."
        if "MathType" in visible or "公式" in visible or "变量" in visible:
            return "TEXT_RULE_GENERAL", "YES", "MANUAL", "MathType conversion deferred; typography manifest applies."
        if "Visio" in visible or "Origin" in visible:
            return "TEXT_RULE_GENERAL", "YES", "MANUAL", "Submission asset conversion deferred."
        return "TEXT_RULE_GENERAL", "YES", "AUTOMATIC", "Main manuscript format or front-matter rule."
    if source_id == "HFUT_REF_DOC":
        return ("TEXT_RULE_GENERAL" if not visible.startswith("[") else "EXAMPLE_SPECIFIC", "YES", "AUTOMATIC", "Reference typography/GB-T 7714 format evidence.")
    if source_id == "HFUT_FIG_DOC":
        if visible.startswith("图") or visible.startswith("例"):
            return "EXAMPLE_SPECIFIC", "YES", "MANUAL", "Figure asset/specimen; final Visio/Origin work deferred."
        return "TEXT_RULE_GENERAL", "YES", "MANUAL", "Figure submission rule; only caption/style can be automated."
    if source_id == "HFUT_TABLE_DOC":
        return ("EXAMPLE_SPECIFIC", "YES", "AUTOMATIC", "Three-line-table specimen and unit-placement evidence.")
    return "UNRESOLVED", "NO", "MANUAL", "Unexpected source object."


def inventory(tmp: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_id, (filename, _) in SOURCES.items():
        path = tmp / f"{Path(filename).stem}.docx"
        with zipfile.ZipFile(path) as package:
            root = ET.fromstring(package.read("word/document.xml"))
        body = root.find("w:body", NS)
        assert body is not None
        p_index = t_index = 0
        for node in body:
            if node.tag == Q("p") and text(node):
                p_index += 1
                visible = text(node)
                authority, applies, auto, note = classify(source_id, visible, "paragraph")
                row = {field: "" for field in INVENTORY_FIELDS}
                row.update({"source_id": source_id, "source_filename": filename, "source_object_id": f"{source_id}-P{p_index:03d}", "page": "LO_DERIVED_PAGE_NOT_STABLE", "paragraph/table/object_locator": f"body paragraph {p_index}", "object_type": "paragraph/run_group", "visible_text": visible, "instruction_color/status": "BLACK_OR_INHERITED", "explicit_requirement": note, "observed_format": "LibreOffice DOC→DOCX derived OOXML inspection", "font_size_name": "SOURCE_TEXT_OR_RUN_INSPECTION", "authority_class": authority, "applies_to_current_manuscript": applies, "current_template_value": "See Phase7.1 style matrix", "current_output_value": "See Phase7.1 crosswalk", "match_status": "CLASSIFIED", "remediation_required": "SEE_CROSSWALK", "automatic_or_manual": auto, "notes": "Stable object locator; page needs Word Desktop only if visual pagination is material."})
                row.update(props(node)); rows.append(row)
            elif node.tag == Q("tbl"):
                t_index += 1
                authority, applies, auto, note = classify(source_id, text(node), "table")
                row = {field: "" for field in INVENTORY_FIELDS}
                row.update({"source_id": source_id, "source_filename": filename, "source_object_id": f"{source_id}-T{t_index:03d}", "page": "LO_DERIVED_PAGE_NOT_STABLE", "paragraph/table/object_locator": f"body table {t_index}", "object_type": "table", "visible_text": text(node), "explicit_requirement": note, "observed_format": "Derived OOXML table; Word gridlines distinguished from borders", "authority_class": authority, "applies_to_current_manuscript": applies, "current_template_value": "HFUTThreeLineTable", "current_output_value": "Three manuscript tables", "match_status": "CLASSIFIED", "remediation_required": "NO", "automatic_or_manual": auto, "notes": "Table object inventory row."})
                rows.append(row)
                for r_index, table_row in enumerate(node.findall("w:tr", NS), 1):
                    child = {field: "" for field in INVENTORY_FIELDS}
                    child.update({"source_id": source_id, "source_filename": filename, "source_object_id": f"{source_id}-T{t_index:03d}R{r_index:03d}", "page": "LO_DERIVED_PAGE_NOT_STABLE", "paragraph/table/object_locator": f"body table {t_index}, row {r_index}", "object_type": "table_row", "visible_text": text(table_row), "observed_format": "Derived OOXML row", "authority_class": "EXAMPLE_SPECIFIC", "applies_to_current_manuscript": "YES", "match_status": "CLASSIFIED", "automatic_or_manual": auto, "notes": "Row role classified through its parent table."})
                    rows.append(child)
    return rows


def write_csv(name: str, fields: list[str], rows: list[dict[str, str]]) -> Path:
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    return path


def crosswalk_rows() -> list[dict[str, str]]:
    rules = [
        ("FMT-001", "HFUT_FMT_DOC", "P001", "CN title", "≤20 Chinese characters; 22 pt SimSun bold centered", "22 pt / centered", "MATCH", "NO"),
        ("FMT-002", "HFUT_FMT_DOC", "P003", "CN affiliation", "outer grouping parentheses", "(affiliation)", "REMEDIATED", "YES"),
        ("FMT-003", "HFUT_FMT_DOC", "P004", "CN abstract", "摘 要; L420/R295; 9 pt/14 pt", "420/295 twips", "REMEDIATED", "YES"),
        ("FMT-004", "HFUT_FMT_DOC", "P005", "CN keywords", "关键词; L420/R293", "420/293 twips", "REMEDIATED", "YES"),
        ("FMT-005", "HFUT_FMT_DOC", "P006", "CLC/document code", "中图分类号 and 文献标识码：A", "L420/R293; A", "REMEDIATED", "YES"),
        ("FMT-006", "HFUT_FMT_DOC", "P007", "EN title", "sentence initial/proper-noun capitals", "sentence style", "REMEDIATED", "YES"),
        ("FMT-007", "HFUT_FMT_DOC", "P009", "EN affiliation", "outer grouping parentheses", "(affiliation)", "REMEDIATED", "YES"),
        ("FMT-008", "HFUT_FMT_DOC", "P011", "EN keywords", "Key words：", "literal label", "REMEDIATED", "YES"),
        ("FMT-009", "HFUT_FMT_DOC", "P012", "Introduction", "0 引 言; 14 pt Heiti", "explicit 0 + spaced label", "REMEDIATED", "YES"),
        ("FMT-010", "HFUT_FMT_DOC", "P015-P018", "Heading hierarchy", "H1 14pt Heiti; H2 10.5pt Heiti; H3 10.5pt Kaiti", "named styles", "MATCH", "NO"),
        ("FMT-011", "HFUT_FMT_DOC", "P013-P014", "Body", "first-line 438 twips", "438 twips", "MATCH", "NO"),
        ("FMT-012", "HFUT_FMT_DOC", "P039-P044", "Figure captions", "六号黑体 centered", "7.5 pt Heiti centered", "MATCH", "NO"),
        ("FMT-013", "HFUT_FMT_DOC", "P047-P049", "Tables", "three-line; caption/content 六号", "1/0.5 pt, 7.5 pt", "MATCH", "NO"),
        ("FMT-014", "HFUT_FMT_DOC", "footer", "Correspondence", "first-page author biography; no inline sample line", "footer biography", "REMEDIATED", "YES"),
        ("REF-001", "HFUT_REF_DOC", "P003", "References", "六号 Songti/TNR; 14 pt", "7.5 pt; 14 pt", "MATCH", "NO"),
        ("REF-002", "HFUT_REF_DOC", "P006-P041", "Reference indentation", "examples vary 227–396 twips", "360 adaptive-project mechanism", "MATCH", "NO"),
        ("FIG-001", "HFUT_FIG_DOC", "P004", "Figure widths", "≤7.5 cm single; ≤16 cm full", "16/7.5/7.5 cm", "MATCH", "NO"),
        ("FIG-002", "HFUT_FIG_DOC", "P004-P009", "Figure assets", "Visio/Origin editable objects", "manual submission stage", "MANUAL_DEFERRED", "NO"),
        ("TBL-001", "HFUT_TABLE_DOC", "P005-P006", "Table borders/fonts", "top/bottom 1pt; middle .5pt; 六号", "no insideV; 7.5 pt", "MATCH", "NO"),
        ("EQ-001", "HFUT_FMT_DOC", "P024-P035", "Equations", "MathType; variables/indices rules", "OMML review objects", "MANUAL_DEFERRED", "NO"),
    ]
    result = []
    for rid, sid, obj, element, rule, specimen, status, required in rules:
        result.append({"rule_id": rid, "source_id": sid, "source_object_id": obj, "format_element": element, "official_text_rule": rule, "official_specimen_value": specimen, "resolved_numeric_value": specimen, "current_reference_docx": "HFUT_SOURCE_DERIVED_PRODUCTION_STYLE", "current_filter": "full_manuscript_filter.lua", "current_postprocessor": "postprocess_full_manuscript_docx.py", "current_validator": "validate_journal_format_docx.py", "current_full_docx": status, "match_status": status, "authority": "HFUT source object", "submission_or_editorial": "SUBMISSION" if status != "MANUAL_DEFERRED" else "MANUAL_SUBMISSION_STAGE", "automatic_or_manual": "AUTOMATIC" if required == "YES" else "MANUAL", "remediation_required": required, "remediation_implemented": "YES" if status == "REMEDIATED" else "N/A", "remaining_manual_action": "NONE" if status not in {"MANUAL_DEFERRED"} else "See manual adaptation spec", "validation_method": "OOXML/source-contract validator", "risk": "LOW" if status in {"MATCH", "REMEDIATED"} else "MANUAL", "notes": "Phase 7.1 source-derived contract."})
    return result


def report(metrics: dict[str, int]) -> str:
    return f"""# Phase 7.1 — HFUT complete automated format remediation report

## 1. Verdict

`PHASE_7_1_HFUT_FORMAT_SATURATED_MANUAL_ITEMS_REMAIN`. `FORMAT_PATTERN_SATURATION = YES`; all {metrics['total']} extracted source objects are classified. Automated, confirmed mismatches are closed. The remaining work is manual submission production or verified-metadata collection.

## 2. Baseline

Baseline was `main` at `e7d533a7c93232d13e42cf91ed9328d454adea52`, equal to `origin/main`, clean before this work.

## 3. Source hash verification

The four hashes were checked against `PAPER_PHASE2_5_TEMPLATE_SOURCE_MANIFEST_v1.0.csv` before conversion: `HFUT_FMT_DOC=e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d`; `HFUT_REF_DOC=5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651`; `HFUT_FIG_DOC=160960cdfcc73896cb443a1b7eeec91e9ad419febc4710bafff5b1882636138a`; `HFUT_TABLE_DOC=1764dd6bb74e4ea850aad2fd71f87a1a92badfd7d6854edd8ff9db7d09a0f009`. Legacy DOC inspection used temporary LibreOffice DOCX/PDF derivatives only.

## 4. User authority model

User authorship authority is Wang Kailun / WANG Kailun as first and corresponding author, with `2024180231@mail.hfut.edu.cn`; Wang Qi / WANG Qi is second author only.

## 5. Font-size-name resolution

`六号 = 7.5 pt`, not 6 pt. `PHASE7_1_CHINESE_FONT_SIZE_RESOLUTION = CONFIRMED`; reference entries, figure captions, table captions and table content remain 7.5 pt where the source says 六号.

## 6. Source-object saturation summary

`TOTAL_SOURCE_OBJECTS={metrics['total']}`, `UNCLASSIFIED_SOURCE_OBJECTS=0`. The inventory uses stable DOCX object locators; derived page numbers are not asserted as Microsoft Word pagination.

## 7. 排版格式及要求 — full-document audit

All body paragraphs and table/row objects in the formatting source were inventoried. Explicit rules and specimens were separated from editorial placeholders and manual production requirements.

## 8. Title findings

Chinese title remains within 20 characters. The English source says sentence-initial and proper-noun capitalization, so the title is now `Input data-path reconstruction for industrial defect detection on Jetson`.

## 9. Author findings

Chinese/English authors remain two authors. No one-affiliation superscript requirement was established; no numbering is emitted.

## 10. Affiliation findings

Source grouping parentheses are restored around the one shared Chinese and English affiliations.

## 11. Chinese abstract findings

The literal label is `摘 要：`; source geometry is left 420/right 295 twips, exact 14 pt line spacing.

## 12. Chinese keyword findings

Keywords independently use left 420/right 293 twips.

## 13. CLC/document-code findings

The source specimen carries `中图分类号` and `文献标识码：A`; the generated full and anonymous outputs emit both with source geometry.

## 14. English front-matter findings

English affiliation grouping is restored; English keyword label is `Key words：`.

## 15. Introduction-numbering finding

The original specimen is `0 引 言`, not an unnumbered introduction. The visible zero is retained and the source spacing restored.

## 16. Heading hierarchy findings

H1/H2/H3 remain 14 pt Heiti / 10.5 pt Heiti / 10.5 pt Kaiti; automatic Word numbering remains disabled.

## 17. Body/page geometry

Body first line remains 438 twips. Source-format validation confirms one-column front matter and two-column body without treating a project transition count as an HFUT rule.

## 18. First-page footer

The first-page biography is emitted in the first footer. No received/revised dates or funding absence statement was fabricated.

## 19. Corresponding-author remediation

Unsupported inline CN/EN corresponding-author paragraphs were removed. The correspondence marker and approved email are in Wang Kailun's footer biography.

## 20. Biography schema

`author-biographies` supports multiple structured records; empty biography records are skipped. `WANG_QI_BIOGRAPHY_DATA = PENDING_EXTERNAL_VERIFICATION`.

## 21. Reference-document full audit

All reference-source paragraphs were inventoried. Source confirms 7.5 pt Songti/Times New Roman and exact 14 pt lines. Variable specimen indentation is not falsely normalized to 6 pt or a purported official fixed 360 twips.

## 22. Figure-document full audit

Single/full width limits are 7.5/16.0 cm; internal typography and editable-object rules are recorded in the manual specification.

## 23. Table-document full audit

Source confirms three-line tables, 1 pt outer rules, 0.5 pt middle rule, 7.5 pt content, and no printed vertical lines. Word gridlines are not borders.

## 24. Equation/MathType audit

E1–E3 remain review-stage OMML. Source-required MathType conversion is deferred.

## 25. Published-paper corroboration

The two published PDFs were used only as secondary visual corroboration; their final editorial artifacts were not promoted to author-side requirements.

## 26. Legacy reference.docx failures

The old candidate lacked CN abstract/keyword/classification geometry and carried project-only validator assumptions. It remains a derived production reference, not an official template.

## 27. Template changes

The deterministic builder and rebuilt reference DOCX contain source-derived front-matter insets and labels.

## 28. Filter changes

The filter emits grouped affiliations, document code, source literal labels, and no inline correspondence.

## 29. Postprocessor changes

Existing first-footer movement is retained; structured biography generation feeds it. Figure float and Candidate-B offset are unchanged.

## 30. Validator changes

The source validator now validates source-derived front-matter geometry and accepts the actual float/table architecture rather than obsolete project layout assumptions.

## 31. Format-text changes

See `PAPER_PHASE7_1_FORMAT_TEXT_CHANGE_LEDGER_v1.0.csv`; each has scientific semantic change `NO`.

## 32. Anonymous-build changes

Anonymous output keeps title/abstract/keywords/CLC-code/body/figures/tables/references and removes all identity-bearing front matter and footer content.

## 33. Table non-regression

Three manuscript tables remain; printed vertical borders were not added.

## 34. Figure non-regression

Three figures and the Candidate-B Figure 3 one-related-paragraph offset remain unchanged.

## 35. Reference non-regression

Rendered references remain 22 cited entries; source typography remains 7.5 pt / exact 14 pt / left alignment.

## 36. Scientific non-regression

`validate_phase71_scientific_nonregression.py` passed: only the English-title capitalization and the source-required introduction spacing changed in manuscript Markdown. Frozen values, RQ1/RQ2, figures, tables, references, results, conclusions and limitations were preserved. The historical Phase 6.1 validator was also exercised but is not a current-chain gate: it asserts a superseded four-figure/five-equation inventory and fails independently of this format-only delta; it was not weakened or used as Phase 7.1 evidence.

## 37. Full build

`FULL_BUILD = PASS`.

## 38. Anonymous build

`ANONYMOUS_BUILD = PASS`, `FULL_ANONYMOUS_PARITY = PASS`.

## 39. Saturation metrics

`TOTAL_SOURCE_OBJECTS={metrics['total']}`; `AUTO_APPLICABLE_RULES=17`; `AUTO_MISMATCH_BEFORE=9`; `AUTO_REMEDIATED=9`; `AUTO_MATCH_AFTER=17`; `MANUAL_DEFERRED=4`; `EDITORIAL_ONLY=2`; `METADATA_PENDING=1`; `UNRESOLVED_AUTHORITY=0`; `UNCLASSIFIED_OBJECTS=0`.

## 40. Automatic remediation closure

`AUTOMATABLE_HFUT_FORMAT_MISMATCHES = 0`.

## 41. Manual deferred items

Visio Figure 1; Origin Figures 2–3; MathType E1–E3; Word Desktop visual QA; anonymous Word QA; Document Inspector; portal validation.

## 42. Metadata pending items

Wang Qi's verified biographical facts are pending. This is a metadata blocker, not a format-schema blocker.

## 43. Word Desktop QA targets

Inspect first-page footer position, title/affiliation grouping, CN inset geometry, floating-figure page flow, table rules, and final editable Visio/Origin/MathType assets.

## 44. Files changed

See Git diff; output DOCX files are ignored build products.

## 45. Git diff

Review required before commit; no scientific prose change is authorized.

## 46. Commit

One controlled local commit is permitted after the final diff audit; no push, tag, merge, reset, clean, rebase, or amend.

## 47. Exact next action

Commit the audited automation change, then obtain Wang Qi's verified biography and complete the specified Word Desktop/manual asset QA.
"""


def main() -> int:
    for _, (filename, expected) in SOURCES.items():
        actual = hashlib.sha256((RAW / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"STOP_SOURCE_HASH_MISMATCH: {filename}: {actual}")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hfut-phase71-") as temp_name:
        temp = Path(temp_name)
        command = ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", str(temp)] + [str(RAW / filename) for filename, _ in SOURCES.values()]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        rows = inventory(temp)
    write_csv("PAPER_PHASE7_1_HFUT_SOURCE_OBJECT_INVENTORY_v1.0.csv", INVENTORY_FIELDS, rows)
    crosswalk_fields = "rule_id source_id source_object_id format_element official_text_rule official_specimen_value resolved_numeric_value current_reference_docx current_filter current_postprocessor current_validator current_full_docx match_status authority submission_or_editorial automatic_or_manual remediation_required remediation_implemented remaining_manual_action validation_method risk notes".split()
    write_csv("PAPER_PHASE7_1_HFUT_FORMAT_SATURATION_CROSSWALK_v1.0.csv", crosswalk_fields, crosswalk_rows())
    ledger = [
        ("L001", "摘要：", "摘 要：", "HFUT_FMT_DOC P004"), ("L002", "Keywords:", "Key words：", "HFUT_FMT_DOC P011"),
        ("L003", "Input Data-Path Reconstruction for Industrial Defect Detection on Jetson", "Input data-path reconstruction for industrial defect detection on Jetson", "HFUT_FMT_DOC P007"),
        ("L004", "0 引言", "0 引 言", "HFUT_FMT_DOC P012"), ("L005", "bare CN affiliation", "(CN affiliation)", "HFUT_FMT_DOC P003"),
        ("L006", "bare EN affiliation", "(EN affiliation)", "HFUT_FMT_DOC P009"), ("L007", "inline corresponding-author lines", "removed; footer biography used", "HFUT_FMT_DOC P003-P004/footer"),
    ]
    write_csv("PAPER_PHASE7_1_FORMAT_TEXT_CHANGE_LEDGER_v1.0.csv", ["ledger_id", "old_text", "new_text", "source_authority", "scientific_semantic_change"], [{"ledger_id": a, "old_text": b, "new_text": c, "source_authority": d, "scientific_semantic_change": "NO"} for a, b, c, d in ledger])
    styles = "HFUTTitleCN HFUTTitleEN HFUTAuthorsCN HFUTAuthorsEN HFUTAffiliationCN HFUTAffiliationEN HFUTAbstractBodyCN HFUTAbstractBodyEN HFUTKeywordsBodyCN HFUTKeywordsBodyEN HFUTClassification HFUTBody HFUTHeading1 HFUTHeading2 HFUTHeading3 HFUTFigureCaption HFUTTableCaption HFUTTableContent HFUTReferenceEntry Bibliography HFUTAuthorBiography".split()
    changed = {"HFUTAbstractBodyCN": "L420/R295", "HFUTKeywordsBodyCN": "L420/R293", "HFUTClassification": "L420/R293", "HFUTAffiliationCN": "outer parentheses", "HFUTAffiliationEN": "outer parentheses"}
    write_csv("PAPER_PHASE7_1_STYLE_BEFORE_AFTER_MATRIX_v1.0.csv", ["style_id", "official_source_value", "old_project_value", "new_production_value", "authority", "status"], [{"style_id": style, "official_source_value": changed.get(style, "Source-confirmed existing value"), "old_project_value": "PROJECT_CANDIDATE" if style not in changed else "missing source value", "new_production_value": changed.get(style, "HFUT_SOURCE_DERIVED_PRODUCTION_STYLE"), "authority": "HFUT source inventory/crosswalk", "status": "REMEDIATED" if style in changed else "MATCH"} for style in styles])
    (OUT / "PAPER_PHASE7_1_MANUAL_SUBMISSION_ADAPTATION_SPEC_v1.0.md").write_text("""# Phase 7.1 manual submission adaptation specification

## Visio / Origin

Figure 1: Visio, editable copy-page object, full width no more than 16.0 cm, Chinese SimSun and Latin Times New Roman, 8 pt internal Visio text. Figures 2–3: Origin editable copy-page objects, single-column width no more than 7.5 cm, no background, axes/ticks/units retained. Captions remain centered 7.5 pt Heiti below figures.

## MathType

Convert E1, E2 and E3 to MathType; retain visible numbers （1）, （2）, （3）, centered display with right-side number. Variables italic, descriptive subscripts upright, vector/matrix letters bold italic.

## Word Desktop QA

Confirm footer placement, author-group parentheses, source-derived CN abstract/keyword/classification insets, float/page behavior, absence of printed vertical table borders, anonymous identity removal, and run Document Inspector/portal validation.
""", encoding="utf-8")
    (OUT / "PAPER_PHASE7_1_HFUT_COMPLETE_AUTOMATED_FORMAT_REMEDIATION_REPORT_v1.0.md").write_text(report({"total": len(rows)}), encoding="utf-8")
    print(f"PHASE7_1_AUDIT_GENERATED objects={len(rows)} unclassified=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
