#!/usr/bin/env python3
"""Validate the Phase 4.7 citation, bibliography, and static cross-reference layer.

This validator intentionally checks only source citation order, bibliography rendering,
reference style structure, and the accepted static figure/table callouts. It does not
evaluate scientific prose, experimental values, or visual Word rendering.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
BIB_PATH = MANUSCRIPT / "references/references.bib"
MATRIX_PATH = MANUSCRIPT / "references/literature_matrix.csv"
AUDIT_PATH = MANUSCRIPT / "references/citation_final_audit.csv"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

SECTION_PATHS = (
    "00_title_abstract.md",
    "01_introduction.md",
    "02_problem_definition.md",
    "03_method.md",
    "04_experiment.md",
    "05_results.md",
    "06_conclusion.md",
)

# Citation order is a manuscript fact: it is checked rather than regenerated from
# bibliography file order. The final unused entry is deliberately retained under the
# Phase 3 PRE_DRAFT_ADMITTED_SOURCE decision.
EXPECTED_CITED_ORDER = (
    "song_yan_2013_neu_surface_defects",
    "shao_et_al_2024_td_net",
    "lema_et_al_2025_surface_defect_benchmark",
    "ultralytics_2023_yolov8_docs",
    "weiss_et_al_2024_realtime_component_inspection",
    "shin_kim_2022_jetson_yolo_frameworks",
    "tang_qian_2024_yolov8_jetson_orin",
    "liu_zhang_ruan_2024_hfut_yolov5_embedded",
    "kim_lee_kim_2024_hyq",
    "nvidia_tensorrt_10_3_release_notes",
    "nvidia_cuda_best_practices_12_6",
    "reddi_et_al_2019_mlperf_inference",
    "nvidia_jetpack_6_2_2",
    "nvidia_cuda_programming_guide_12_6",
)
UNUSED_ADMITTED_KEY = "reddi_et_al_2022_mlperf_mobile"

EXPECTED_TYPE = {
    "song_yan_2013_neu_surface_defects": "J",
    "shao_et_al_2024_td_net": "J",
    "lema_et_al_2025_surface_defect_benchmark": "J/OL",
    "ultralytics_2023_yolov8_docs": "EB/OL",
    "weiss_et_al_2024_realtime_component_inspection": "J",
    "shin_kim_2022_jetson_yolo_frameworks": "J",
    "tang_qian_2024_yolov8_jetson_orin": "J",
    "liu_zhang_ruan_2024_hfut_yolov5_embedded": "J",
    "kim_lee_kim_2024_hyq": "C",
    "nvidia_tensorrt_10_3_release_notes": "M",
    "nvidia_cuda_best_practices_12_6": "M",
    "reddi_et_al_2019_mlperf_inference": "PP/OL",
    "nvidia_jetpack_6_2_2": "EB/OL",
    "nvidia_cuda_programming_guide_12_6": "M",
}

TITLE_NEEDLES = {
    "song_yan_2013_neu_surface_defects": "hot-rolled steel strip",
    "shao_et_al_2024_td_net": "TD-Net",
    "lema_et_al_2025_surface_defect_benchmark": "Benchmarking deep learning models",
    "ultralytics_2023_yolov8_docs": "Explore Ultralytics YOLOv8",
    "weiss_et_al_2024_realtime_component_inspection": "Real-Time Defect Detection",
    "shin_kim_2022_jetson_yolo_frameworks": "Deep Learning Framework Performance",
    "tang_qian_2024_yolov8_jetson_orin": "High-speed railway track components",
    "liu_zhang_ruan_2024_hfut_yolov5_embedded": "Improved YOLOv5 staircase",
    "kim_lee_kim_2024_hyq": "HyQ:",
    "nvidia_tensorrt_10_3_release_notes": "TensorRT 10.3 Release Notes",
    "nvidia_cuda_best_practices_12_6": "CUDA C++ Best Practices Guide",
    "reddi_et_al_2019_mlperf_inference": "MLPerf Inference Benchmark",
    "nvidia_jetpack_6_2_2": "JetPack SDK",
    "nvidia_cuda_programming_guide_12_6": "CUDA C++ Programming Guide",
}

METADATA_STATUS = {
    "song_yan_2013_neu_surface_defects": ("REMEDIATED", "Added locally verified final volume and pages (285:858--864)."),
    "shao_et_al_2024_td_net": ("REMEDIATED", "Added locally verified final volume and pages (10:3943--3954)."),
    "lema_et_al_2025_surface_defect_benchmark": ("PASS", "Local article is online-first; no unverified final volume, issue, or pages were added."),
    "ultralytics_2023_yolov8_docs": ("REMEDIATED", "Converted to official webpage metadata with locally captured URL and access date."),
    "weiss_et_al_2024_realtime_component_inspection": ("REMEDIATED", "Added locally verified volume, issue, and article number (13(8):1551)."),
    "shin_kim_2022_jetson_yolo_frameworks": ("REMEDIATED", "Added locally verified article number (12(8):3734)."),
    "tang_qian_2024_yolov8_jetson_orin": ("PASS", "Local full text confirms existing volume and pagination."),
    "liu_zhang_ruan_2024_hfut_yolov5_embedded": ("REMEDIATED", "Added locally verified final pagination (47(7):879--887)."),
    "kim_lee_kim_2024_hyq": ("PASS", "Local full text and admitted BibTeX metadata confirm conference fields."),
    "nvidia_tensorrt_10_3_release_notes": ("PASS", "Phase 3 admitted limitation retained: no approved publication year is available."),
    "nvidia_cuda_best_practices_12_6": ("PASS", "Local official PDF confirms 2024 Release 12.6 manual metadata."),
    "reddi_et_al_2019_mlperf_inference": ("REMEDIATED", "Explicit preprint metadata and canonical arXiv URL permit [PP/OL] rendering."),
    "nvidia_jetpack_6_2_2": ("REMEDIATED", "Converted to official webpage metadata with locally captured URL and access date; no publication year invented."),
    "nvidia_cuda_programming_guide_12_6": ("PASS", "Local official PDF confirms 2024 Release 12.6 manual metadata."),
    UNUSED_ADMITTED_KEY: ("PASS", "A15 remains PRE_DRAFT_ADMITTED_SOURCE under the Phase 3 admission decision; it is intentionally not cited or rendered."),
}

FIGURE_TABLE_CAPTIONS = OrderedDict(
    (
        ("图1", ""),
        ("表1", "表1　平台、模型、数据集和统一运行协议"),
        ("表2", "表2　V0与V2R任务级正确性验证结果"),
        ("图2", "图2　V0、V2R和V3R平均帧率比较"),
        ("图3", "图3　V0、V2R和V3R平均及尾延迟比较"),
    )
)


def load_f1_caption_authority() -> str:
    manifest = MANUSCRIPT / "figures/figure_manifest.csv"
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = {row["figure_id"]: row for row in csv.DictReader(handle)}
    caption = rows.get("F1", {}).get("word_caption", "")
    if not caption:
        raise ValueError("Figure manifest has no F1 word_caption authority.")
    return caption


FIGURE_TABLE_CAPTIONS["图1"] = load_f1_caption_authority()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_bib_entries(text: str) -> OrderedDict[str, dict[str, object]]:
    """Read the small project BibTeX library without adding a parser dependency."""
    entries: OrderedDict[str, dict[str, object]] = OrderedDict()
    start_re = re.compile(r"@(?P<type>[A-Za-z]+)\s*\{(?P<key>[^,\s]+)\s*,", re.M)
    for match in start_re.finditer(text):
        depth = 1
        index = match.end()
        while index < len(text) and depth:
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
            index += 1
        if depth:
            raise ValueError(f"Unclosed BibTeX entry: {match.group('key')}")
        body = text[match.end() : index - 1]
        fields: dict[str, str] = {}
        for field_match in re.finditer(r"(?mi)^\s*([A-Za-z][A-Za-z0-9_-]*)\s*=\s*\{([^\n]*)\}\s*,?\s*$", body):
            fields[field_match.group(1).lower()] = field_match.group(2).strip()
        entries[match.group("key")] = {"type": match.group("type").lower(), "fields": fields}
    return entries


def citation_occurrences() -> tuple[list[str], dict[str, str], list[str]]:
    order: list[str] = []
    first_sections: dict[str, str] = {}
    manual_number_matches: list[str] = []
    for section_name in SECTION_PATHS:
        path = MANUSCRIPT / "sections" / section_name
        content = path.read_text(encoding="utf-8")
        if section_name == "00_title_abstract.md" and re.search(r"@[A-Za-z][A-Za-z0-9_.:-]*", content):
            raise ValueError("Abstract/title source contains a citation key.")
        for key in re.findall(r"@([A-Za-z][A-Za-z0-9_.:-]*)", content):
            if key not in first_sections:
                first_sections[key] = section_name
                order.append(key)
        manual_number_matches.extend(re.findall(r"\[\s*\d+(?:\s*[,;，、-]\s*\d+)*\s*\]", content))
    return order, first_sections, manual_number_matches


def matrix_rows() -> dict[str, dict[str, str]]:
    with MATRIX_PATH.open(encoding="utf-8", newline="") as handle:
        return {row["citation_key"]: row for row in csv.DictReader(handle)}


def validate_source_layer(entries: OrderedDict[str, dict[str, object]]) -> tuple[list[str], dict[str, str], list[str]]:
    errors: list[str] = []
    cited_order, first_sections, manual_numbers = citation_occurrences()
    expected_all = set(EXPECTED_CITED_ORDER) | {UNUSED_ADMITTED_KEY}

    if tuple(cited_order) != EXPECTED_CITED_ORDER:
        fail(errors, f"first-occurrence order mismatch: {cited_order!r}")
    if manual_numbers:
        fail(errors, f"manual numeric citation patterns in Markdown: {manual_numbers!r}")
    if set(entries) != expected_all or len(entries) != 15:
        fail(errors, f"bibliography library must contain exactly the admitted 15 keys; got {list(entries)!r}")
    unresolved = sorted(set(cited_order) - set(entries))
    if unresolved:
        fail(errors, f"unresolved citation keys: {unresolved!r}")
    uncited = sorted(set(entries) - set(cited_order))
    if uncited != [UNUSED_ADMITTED_KEY]:
        fail(errors, f"unexpected uncited entries: {uncited!r}")

    matrix = matrix_rows()
    if set(matrix) != set(entries):
        fail(errors, "literature_matrix.csv keys do not match references.bib")
    for key in EXPECTED_CITED_ORDER:
        fields = entries[key]["fields"]
        if not isinstance(fields, dict):
            fail(errors, f"internal BibTeX parse failure for {key}")
            continue
        for required in ("author", "title"):
            if not fields.get(required):
                fail(errors, f"{key}: missing required {required} metadata")
        if key in EXPECTED_TYPE and EXPECTED_TYPE[key] in {"J", "J/OL"}:
            for required in ("journal", "year", "doi"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing journal metadata {required}")
        if key in {"song_yan_2013_neu_surface_defects", "shao_et_al_2024_td_net", "weiss_et_al_2024_realtime_component_inspection", "shin_kim_2022_jetson_yolo_frameworks", "tang_qian_2024_yolov8_jetson_orin", "liu_zhang_ruan_2024_hfut_yolov5_embedded"}:
            for required in ("volume", "pages"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing final article metadata {required}")
        if key == "kim_lee_kim_2024_hyq":
            for required in ("booktitle", "publisher", "year", "pages", "doi"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing conference metadata {required}")
        if key in {"ultralytics_2023_yolov8_docs", "nvidia_jetpack_6_2_2"}:
            for required in ("url", "urldate"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing official webpage metadata {required}")
        if key == "reddi_et_al_2019_mlperf_inference":
            for required in ("year", "note", "url"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing preprint metadata {required}")
        doi = fields.get("doi")
        if doi and not re.fullmatch(r"10\.\S+/.+", doi):
            fail(errors, f"{key}: malformed DOI {doi!r}")
        url = fields.get("url")
        if url and not re.fullmatch(r"https://[^\s]+", url):
            fail(errors, f"{key}: malformed URL {url!r}")
    return errors, first_sections, cited_order


def write_audit(entries: OrderedDict[str, dict[str, object]], first_sections: dict[str, str]) -> None:
    fields = (
        "citation_key",
        "cited_yes_no",
        "first_occurrence_index",
        "first_occurrence_section",
        "source_type",
        "current_bib_type",
        "expected_rendered_type",
        "metadata_status",
        "render_status",
        "final_disposition",
        "notes",
    )
    matrix = matrix_rows()
    with AUDIT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index, key in enumerate(EXPECTED_CITED_ORDER, start=1):
            status, note = METADATA_STATUS[key]
            writer.writerow(
                {
                    "citation_key": key,
                    "cited_yes_no": "YES",
                    "first_occurrence_index": index,
                    "first_occurrence_section": first_sections[key],
                    "source_type": matrix[key]["source_type"],
                    "current_bib_type": entries[key]["type"],
                    "expected_rendered_type": f"[{EXPECTED_TYPE[key]}]",
                    "metadata_status": status,
                    "render_status": f"PASS_RENDERED_[{EXPECTED_TYPE[key]}]",
                    "final_disposition": "CITED_AND_RENDERED",
                    "notes": note,
                }
            )
        status, note = METADATA_STATUS[UNUSED_ADMITTED_KEY]
        writer.writerow(
            {
                "citation_key": UNUSED_ADMITTED_KEY,
                "cited_yes_no": "NO",
                "first_occurrence_index": "",
                "first_occurrence_section": "",
                "source_type": matrix[UNUSED_ADMITTED_KEY]["source_type"],
                "current_bib_type": entries[UNUSED_ADMITTED_KEY]["type"],
                "expected_rendered_type": "NOT_RENDERED",
                "metadata_status": status,
                "render_status": "NOT_RENDERED_BY_DESIGN",
                "final_disposition": "PRE_DRAFT_ADMITTED_SOURCE_RETAINED",
                "notes": note,
            }
        )


def markdown_cross_reference_errors() -> list[str]:
    errors: list[str] = []
    text = "\n".join((MANUSCRIPT / "sections" / name).read_text(encoding="utf-8") for name in SECTION_PATHS)
    positions: dict[str, int] = {}
    for label, caption in FIGURE_TABLE_CAPTIONS.items():
        matches = [match.start() for match in re.finditer(re.escape(caption), text)]
        if len(matches) != 1:
            fail(errors, f"{label}: expected exactly one accepted caption, found {len(matches)}")
            continue
        positions[label] = matches[0]
        callout_pattern = re.compile(rf"{re.escape(label)}(?!　)")
        callouts = [match.start() for match in callout_pattern.finditer(text) if match.start() < matches[0]]
        if not callouts:
            fail(errors, f"{label}: no body callout precedes its caption")
    figures = [positions.get(label, -1) for label in ("图1", "图2", "图3")]
    tables = [positions.get(label, -1) for label in ("表1", "表2")]
    if figures != sorted(figures) or -1 in figures:
        fail(errors, "figure captions are not sequential F1--F3")
    if tables != sorted(tables) or -1 in tables:
        fail(errors, "table captions are not sequential T1--T2")
    stale = re.findall(r"(?:图|Fig(?:ure)?\.?\s*)[4-9]|(?:表|Table\s*)[3-9]", text, flags=re.I)
    if stale:
        fail(errors, f"stale figure/table prototype labels found: {stale!r}")
    return errors


def docx_paragraphs(path: Path) -> list[tuple[str, str]]:
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs: list[tuple[str, str]] = []
    for paragraph in root.findall(".//w:body/w:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))
        style_node = paragraph.find("w:pPr/w:pStyle", NS)
        style = style_node.get(f"{{{W_NS}}}val") if style_node is not None else ""
        paragraphs.append((style or "", text))
    return paragraphs


def element_attr(element: ET.Element | None, name: str) -> str | None:
    return None if element is None else element.get(f"{{{W_NS}}}{name}")


def structural_style_errors(path: Path) -> list[str]:
    errors: list[str] = []
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/styles.xml"))
    styles = {style.get(f"{{{W_NS}}}styleId"): style for style in root.findall("w:style", NS)}
    for style_id in ("HFUTReferenceHeading", "HFUTReferenceEntry", "Bibliography"):
        if style_id not in styles:
            fail(errors, f"{path.name}: missing {style_id} style")
    for style_id in ("HFUTReferenceEntry", "Bibliography"):
        style = styles.get(style_id)
        if style is None:
            continue
        fonts = style.find("w:rPr/w:rFonts", NS)
        if element_attr(fonts, "eastAsia") != "宋体" or element_attr(fonts, "ascii") != "Times New Roman":
            fail(errors, f"{path.name}: {style_id} does not specify Songti/Times New Roman")
        size = style.find("w:rPr/w:sz", NS)
        if element_attr(size, "val") != "15":
            fail(errors, f"{path.name}: {style_id} size is not six-size (15 half-points)")
        spacing = style.find("w:pPr/w:spacing", NS)
        if element_attr(spacing, "line") != "280" or element_attr(spacing, "lineRule") != "exact":
            fail(errors, f"{path.name}: {style_id} line spacing is not exact 14 pt")
    return errors


def rendered_docx_errors(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    paragraphs = docx_paragraphs(path)
    bibliography = [text for style, text in paragraphs if style == "Bibliography"]
    if len(bibliography) != len(EXPECTED_CITED_ORDER):
        fail(errors, f"{path.name}: expected 14 bibliography entries, found {len(bibliography)}")
    for number, (key, entry) in enumerate(zip(EXPECTED_CITED_ORDER, bibliography), start=1):
        prefix = f"[{number}]"
        if not entry.startswith(prefix):
            fail(errors, f"{path.name}: bibliography entry {number} lacks sequential marker {prefix}")
        marker = f"[{EXPECTED_TYPE[key]}]"
        if marker not in entry:
            fail(errors, f"{path.name}: bibliography entry {number} lacks expected marker {marker}")
        if TITLE_NEEDLES[key].casefold() not in entry.casefold():
            fail(errors, f"{path.name}: bibliography entry {number} does not match {key}")
    if any("[Z]" in entry for entry in bibliography):
        fail(errors, f"{path.name}: unexpected [Z] bibliography marker")
    full_text = "\n".join(text for _, text in paragraphs)
    if re.search(r"@[A-Za-z][A-Za-z0-9_.:-]*", full_text):
        fail(errors, f"{path.name}: unrendered @citation key residue")
    for caption in FIGURE_TABLE_CAPTIONS.values():
        if caption not in full_text:
            fail(errors, f"{path.name}: missing accepted caption {caption}")
    errors.extend(structural_style_errors(path))
    return errors, bibliography


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", type=Path, action="append", default=[])
    parser.add_argument("--compare-full", type=Path)
    parser.add_argument("--write-audit", action="store_true")
    args = parser.parse_args()

    entries = parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))
    errors, first_sections, cited_order = validate_source_layer(entries)
    errors.extend(markdown_cross_reference_errors())
    if args.write_audit and not errors:
        write_audit(entries, first_sections)

    rendered: dict[Path, list[str]] = {}
    for path in args.docx:
        if not path.is_file():
            fail(errors, f"rendered DOCX missing: {path}")
            continue
        docx_errors, bibliography = rendered_docx_errors(path)
        errors.extend(docx_errors)
        rendered[path] = bibliography
    if args.compare_full:
        if not args.compare_full.is_file():
            fail(errors, f"full DOCX missing for bibliography comparison: {args.compare_full}")
        elif len(args.docx) != 1 or args.docx[0] not in rendered:
            fail(errors, "--compare-full requires exactly one validated anonymous DOCX")
        else:
            full_errors, full_bibliography = rendered_docx_errors(args.compare_full)
            errors.extend(full_errors)
            if rendered[args.docx[0]] != full_bibliography:
                fail(errors, "full and anonymous bibliography paragraphs differ")

    if errors:
        for message in errors:
            print(f"FAIL: {message}")
        return 1
    print(
        "PASS: CITATION_SOURCE_VALIDATED "
        f"bibliography_entries={len(entries)} cited={len(cited_order)} uncited=1 unresolved=0"
    )
    print("PASS: STATIC_CROSS_REFERENCE_VALIDATED figures=F1,F2,F3 tables=T1,T2")
    if args.docx:
        print(f"PASS: RENDERED_BIBLIOGRAPHY_VALIDATED docx={','.join(str(path) for path in args.docx)}")
        print("PASS: STRUCTURAL_REFERENCE_TYPOGRAPHY_VALIDATED Songti+Times; 7.5pt; exact14pt")
    if args.compare_full:
        print("PASS: FULL_ANONYMOUS_BIBLIOGRAPHY_IDENTITY_VALIDATED")
    if args.write_audit:
        print(f"PASS: CITATION_FINAL_AUDIT_WRITTEN path={AUDIT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
