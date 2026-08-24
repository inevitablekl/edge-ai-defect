#!/usr/bin/env python3
"""Validate the citation, bibliography, and static cross-reference layer.

This validator intentionally checks only source citation order, bibliography rendering,
verified reference metadata, reference style structure, and the accepted static
figure/table callouts. It does not evaluate scientific prose, experimental values, or
visual Word rendering.
"""

from __future__ import annotations

import argparse
import csv
import json
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
CONFERENCE_AUTHORITY_PATH = (
    ROOT / "docs/paper/phase6_3/phase6_3r1_conference_metadata_audit.json"
)
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
# bibliography file order. Unused library entries are deliberately retained under the
# Phase 3 PRE_DRAFT_ADMITTED_SOURCE decision.
EXPECTED_CITED_ORDER = (
    "lv_et_al_2020_metallic_defects",
    "song_yan_2013_neu_surface_defects",
    "shao_et_al_2024_td_net",
    "chu_yu_rong_2024_strip_steel_yolov8",
    "zhang_pang_jiang_2024_gdm_yolo",
    "ultralytics_2023_yolov8_docs",
    "stacker_et_al_2021_edge_runtime",
    "lee_han_kim_2025_presto",
    "weiss_et_al_2024_realtime_component_inspection",
    "jacob_et_al_2018_integer_inference",
    "nagel_et_al_2020_adaround",
    "nvidia_tensorrt_10_3_release_notes",
    "kim_lee_kim_2024_hyq",
    "tang_qian_2024_yolov8_jetson_orin",
    "nvidia_cuda_best_practices_12_6",
    "bateni_et_al_2020_integrated_memory",
    "rodriguez_et_al_2025_gpu_memory_allocation",
    "nvidia_cuda_programming_guide_12_6",
    "kim_et_al_2025_concurrent_edge_detection",
    "dean_barroso_2013_tail_scale",
    "shin_kim_2022_jetson_yolo_frameworks",
    "lema_et_al_2025_surface_defect_benchmark",
)
UNUSED_KEYS = (
    "archet_et_al_2023_embedded_soc",
    "nvidia_jetpack_6_2_2",
    "hill_marty_2008_amdahl",
    "reddi_et_al_2019_mlperf_inference",
    "reddi_et_al_2022_mlperf_mobile",
)

EXPECTED_TYPE = {
    "lv_et_al_2020_metallic_defects": "J",
    "song_yan_2013_neu_surface_defects": "J",
    "shao_et_al_2024_td_net": "J",
    "chu_yu_rong_2024_strip_steel_yolov8": "J",
    "zhang_pang_jiang_2024_gdm_yolo": "J",
    "lema_et_al_2025_surface_defect_benchmark": "J",
    "ultralytics_2023_yolov8_docs": "EB/OL",
    "stacker_et_al_2021_edge_runtime": "C",
    "kim_et_al_2025_concurrent_edge_detection": "J",
    "lee_han_kim_2025_presto": "C",
    "weiss_et_al_2024_realtime_component_inspection": "J",
    "shin_kim_2022_jetson_yolo_frameworks": "J",
    "tang_qian_2024_yolov8_jetson_orin": "J",
    "jacob_et_al_2018_integer_inference": "C",
    "nagel_et_al_2020_adaround": "C",
    "kim_lee_kim_2024_hyq": "C",
    "nvidia_tensorrt_10_3_release_notes": "EB/OL",
    "nvidia_cuda_best_practices_12_6": "EB/OL",
    "dean_barroso_2013_tail_scale": "J",
    "reddi_et_al_2019_mlperf_inference": "C",
    "nvidia_jetpack_6_2_2": "EB/OL",
    "bateni_et_al_2020_integrated_memory": "C",
    "rodriguez_et_al_2025_gpu_memory_allocation": "C",
    "nvidia_cuda_programming_guide_12_6": "EB/OL",
    "hill_marty_2008_amdahl": "J",
    "archet_et_al_2023_embedded_soc": "C",
}

EXPECTED_CITED_CONFERENCE_KEYS = tuple(
    key for key in EXPECTED_CITED_ORDER if EXPECTED_TYPE[key] == "C"
)

PUBLICATION_CLASS_BY_TYPE = {
    "J": "FINAL_JOURNAL",
    "C": "FINAL_CONFERENCE",
    "J/OL": "ONLINE_FIRST_JOURNAL",
    "EB/OL": "OFFICIAL_WEB_RESOURCE",
}

LEMA_FINAL_METADATA = {
    "journal": "Journal of Intelligent Manufacturing",
    "volume": "37",
    "number": "7",
    "pages": "3001--3018",
    "year": "2026",
    "doi": "10.1007/s10845-025-02672-8",
}

TITLE_NEEDLES = {
    "lv_et_al_2020_metallic_defects": "Deep Metallic Surface Defect Detection",
    "song_yan_2013_neu_surface_defects": "hot-rolled steel strip",
    "shao_et_al_2024_td_net": "TD-Net",
    "chu_yu_rong_2024_strip_steel_yolov8": "Lightweight Strip Steel Surface Defect",
    "zhang_pang_jiang_2024_gdm_yolo": "GDM-YOLO",
    "lema_et_al_2025_surface_defect_benchmark": "Benchmarking deep learning models",
    "ultralytics_2023_yolov8_docs": "Explore Ultralytics YOLOv8",
    "stacker_et_al_2021_edge_runtime": "Deployment of Deep Neural Networks",
    "kim_et_al_2025_concurrent_edge_detection": "Concurrent Multi-Frame Processing",
    "lee_han_kim_2025_presto": "Hybrid CPU-GPU Preprocessing",
    "weiss_et_al_2024_realtime_component_inspection": "Real-Time Defect Detection",
    "shin_kim_2022_jetson_yolo_frameworks": "Deep Learning Framework Performance",
    "tang_qian_2024_yolov8_jetson_orin": "High-speed railway track components",
    "jacob_et_al_2018_integer_inference": "Integer-Arithmetic-Only Inference",
    "nagel_et_al_2020_adaround": "Adaptive Rounding",
    "kim_lee_kim_2024_hyq": "HyQ:",
    "nvidia_tensorrt_10_3_release_notes": "TensorRT 10.3 Release Notes",
    "nvidia_cuda_best_practices_12_6": "CUDA C++ Best Practices Guide",
    "dean_barroso_2013_tail_scale": "The Tail at Scale",
    "reddi_et_al_2019_mlperf_inference": "MLPerf Inference Benchmark",
    "nvidia_jetpack_6_2_2": "JetPack SDK",
    "bateni_et_al_2020_integrated_memory": "Co-Optimizing Performance and Memory Footprint",
    "rodriguez_et_al_2025_gpu_memory_allocation": "GPU Memory Allocation Characteristics",
    "nvidia_cuda_programming_guide_12_6": "CUDA C++ Programming Guide",
    "hill_marty_2008_amdahl": "Law in the Multicore Era",
    "archet_et_al_2023_embedded_soc": "Embedded Heterogeneous SoC",
}

METADATA_STATUS = {
    "lv_et_al_2020_metallic_defects": ("PASS", "Publisher and DOI metadata confirm Sensors 20(6), article 1562."),
    "song_yan_2013_neu_surface_defects": ("REMEDIATED", "Added locally verified final volume and pages (285:858--864)."),
    "shao_et_al_2024_td_net": ("REMEDIATED", "Added locally verified final volume and pages (10:3943--3954)."),
    "chu_yu_rong_2024_strip_steel_yolov8": ("PASS", "Publisher and DOI metadata confirm Sensors 24(19), article 6495."),
    "zhang_pang_jiang_2024_gdm_yolo": ("PASS", "DOI metadata confirm IEEE Access 12:148817--148825."),
    "lema_et_al_2025_surface_defect_benchmark": ("REMEDIATED", "Official Springer final metadata confirm Journal of Intelligent Manufacturing 37(7):3001--3018 (2026); source DOI retained and rendered DOI suppressed."),
    "ultralytics_2023_yolov8_docs": ("REMEDIATED", "Converted to official webpage metadata with locally captured URL and access date."),
    "stacker_et_al_2021_edge_runtime": ("REMEDIATED", "Phase 6.3R1 authority confirms ICCVW 2021:1015--1022 and IEEE publisher place Piscataway, NJ, USA; Online is retained only as event traceability."),
    "kim_et_al_2025_concurrent_edge_detection": ("PASS", "DOI and DBLP metadata confirm IEEE Access 13:1522--1533."),
    "lee_han_kim_2025_presto": ("REMEDIATED", "Phase 6.3R1 authority confirms MobiSys 2025:735--740 and Association for Computing Machinery publisher place New York, NY, USA; Anaheim remains event traceability only."),
    "weiss_et_al_2024_realtime_component_inspection": ("REMEDIATED", "Added locally verified volume, issue, and article number (13(8):1551)."),
    "shin_kim_2022_jetson_yolo_frameworks": ("REMEDIATED", "Added locally verified article number (12(8):3734)."),
    "tang_qian_2024_yolov8_jetson_orin": ("PASS", "Local full text confirms existing volume and pagination."),
    "jacob_et_al_2018_integer_inference": ("REMEDIATED", "Phase 6.3R1 authority confirms CVPR 2018:2704--2713 and IEEE publisher place Piscataway, NJ, USA; Salt Lake City remains event traceability only."),
    "nagel_et_al_2020_adaround": ("REMEDIATED", "Phase 6.3R1 authority confirms ICML/PMLR 119:7197--7206 and PMLR/JMLR publication place Cambridge, MA, USA; Virtual remains event traceability only."),
    "kim_lee_kim_2024_hyq": ("REMEDIATED", "Phase 6.3R1 authority confirms IJCAI-24:4291--4299 and the publisher's official principal place Menlo Park, CA, USA; Jeju remains event traceability only."),
    "nvidia_tensorrt_10_3_release_notes": ("REMEDIATED", "Official online PDF carrier, release year, URL, and governed access date verified; rendered as EB/OL."),
    "nvidia_cuda_best_practices_12_6": ("REMEDIATED", "Official NVIDIA archive page, Release 12.6 year, URL, and governed access date verified; rendered as EB/OL."),
    "dean_barroso_2013_tail_scale": ("PASS", "ACM DOI metadata confirm Communications of the ACM 56(2):74--80."),
    "reddi_et_al_2019_mlperf_inference": ("UPGRADE_METADATA", "Same logical source upgraded from the 2019 preprint to ISCA 2020:446--459."),
    "nvidia_jetpack_6_2_2": ("REMEDIATED", "Converted to official webpage metadata with locally captured URL and access date; no publication year invented."),
    "bateni_et_al_2020_integrated_memory": ("REMEDIATED", "Phase 6.3R1 authority confirms RTAS 2020:310--323 and IEEE publisher place Piscataway, NJ, USA; Sydney remains event traceability only."),
    "rodriguez_et_al_2025_gpu_memory_allocation": ("PASS", "Phase 6.3R1 authority confirms OASIcs 127:1:1--1:15 and unchanged Schloss Dagstuhl publisher place Dagstuhl, Germany; Barcelona is event traceability only."),
    "nvidia_cuda_programming_guide_12_6": ("REMEDIATED", "Official NVIDIA archive page, Release 12.6 year, URL, and governed access date verified; rendered as EB/OL."),
    "hill_marty_2008_amdahl": ("PASS", "IEEE DOI metadata confirm Computer 41(7):33--38."),
    "archet_et_al_2023_embedded_soc": ("PASS", "IEEE DOI metadata confirm DSD 2023:30--38."),
    "reddi_et_al_2022_mlperf_mobile": ("PASS", "A15 remains PRE_DRAFT_ADMITTED_SOURCE under the Phase 3 admission decision; it is intentionally not cited or rendered."),
}

def load_caption_authority() -> OrderedDict[str, str]:
    captions: OrderedDict[str, str] = OrderedDict()
    for directory, filename, id_field, prefix in (
        ("figures", "figure_manifest.csv", "figure_id", "图"),
        ("tables", "table_manifest.csv", "table_id", "表"),
    ):
        manifest = MANUSCRIPT / directory / filename
        with manifest.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            label = prefix + row[id_field][1:]
            caption = row.get("word_caption", "")
            if not caption:
                raise ValueError(f"{filename} has no caption for {row[id_field]}.")
            captions[label] = caption
    return captions


FIGURE_TABLE_CAPTIONS = load_caption_authority()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def normalized_metadata_text(value: str) -> str:
    """Normalize equivalent BibTeX/CSL spellings before rendered-field checks."""
    replacements = {
        r'{\"u}': "ü",
        r'\"{u}': "ü",
        "--": "-",
        "–": "-",
        "—": "-",
        "−": "-",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.replace("{", "").replace("}", "").casefold()


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


def conference_authority_errors(entries: OrderedDict[str, dict[str, object]]) -> list[str]:
    """Validate cited conference metadata against the Phase 6.3R1 authority artifact."""
    errors: list[str] = []
    if not CONFERENCE_AUTHORITY_PATH.is_file():
        return [f"conference metadata authority missing: {CONFERENCE_AUTHORITY_PATH}"]
    try:
        authority = json.loads(CONFERENCE_AUTHORITY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        return [f"conference metadata authority is unreadable: {error}"]

    allowed_statuses = {
        "VERIFIED",
        "UNCHANGED_VERIFIED",
        "CORRECTED_VERIFIED",
        "UNRESOLVED",
    }
    if set(authority.get("allowed_verification_statuses", [])) != allowed_statuses:
        fail(errors, "conference metadata authority has an invalid status vocabulary")
    records = authority.get("records")
    if not isinstance(records, list):
        return errors + ["conference metadata authority records must be a list"]
    records_by_key = {
        record.get("citation_key"): record for record in records if isinstance(record, dict)
    }
    if set(records_by_key) != set(EXPECTED_CITED_CONFERENCE_KEYS) or len(records_by_key) != len(
        EXPECTED_CITED_CONFERENCE_KEYS
    ):
        fail(
            errors,
            "conference metadata authority set does not match the cited conference set: "
            f"{tuple(records_by_key)!r}",
        )

    field_map = {
        "proceedings_title": "booktitle",
        "publisher": "publisher",
        "publisher_place": "address",
        "year": "year",
        "pages": "pages",
    }
    for key in EXPECTED_CITED_CONFERENCE_KEYS:
        record = records_by_key.get(key)
        if not isinstance(record, dict):
            fail(errors, f"{key}: missing per-record conference metadata authority")
            continue
        status = record.get("verification_status")
        if status not in allowed_statuses:
            fail(errors, f"{key}: invalid conference verification status {status!r}")
        if status == "UNRESOLVED":
            fail(errors, f"{key}: publisher place remains UNRESOLVED")
        sources = record.get("official_evidence_sources")
        if not isinstance(sources, list) or not sources or any(
            not isinstance(source, str) or not source.startswith("https://") for source in sources
        ):
            fail(errors, f"{key}: official evidence sources are missing or malformed")
        event_location = record.get("event_location")
        publisher_place = record.get("publisher_place")
        if not event_location or not publisher_place:
            fail(errors, f"{key}: event location or publisher place is empty")
        elif normalized_metadata_text(str(event_location)) == normalized_metadata_text(str(publisher_place)):
            fail(errors, f"{key}: event location is still equated with publisher place")

        entry = entries.get(key)
        fields = None if entry is None else entry.get("fields")
        if not isinstance(fields, dict):
            fail(errors, f"{key}: conference BibTeX entry is missing")
            continue
        for authority_field, bib_field in field_map.items():
            expected = record.get(authority_field)
            actual = fields.get(bib_field)
            if not expected or actual != expected:
                fail(
                    errors,
                    f"{key}: {bib_field} does not match verified authority; "
                    f"expected {expected!r}, got {actual!r}",
                )
        after = record.get("repository_value_after")
        before = record.get("repository_value_before")
        if not isinstance(before, dict) or not isinstance(after, dict):
            fail(errors, f"{key}: before/after repository traceability is missing")
        elif after.get("publisher") != fields.get("publisher") or after.get("address") != fields.get("address"):
            fail(errors, f"{key}: repository_value_after does not match references.bib")
    return errors


def validate_source_layer(entries: OrderedDict[str, dict[str, object]]) -> tuple[list[str], dict[str, str], list[str]]:
    errors: list[str] = []
    cited_order, first_sections, manual_numbers = citation_occurrences()
    expected_all = set(EXPECTED_CITED_ORDER) | set(UNUSED_KEYS)

    if tuple(cited_order) != EXPECTED_CITED_ORDER:
        fail(errors, f"first-occurrence order mismatch: {cited_order!r}")
    if manual_numbers:
        fail(errors, f"manual numeric citation patterns in Markdown: {manual_numbers!r}")
    if set(entries) != expected_all or len(entries) != 27:
        fail(errors, f"bibliography library must contain exactly the admitted 27 keys; got {list(entries)!r}")
    unresolved = sorted(set(cited_order) - set(entries))
    if unresolved:
        fail(errors, f"unresolved citation keys: {unresolved!r}")
    uncited = sorted(set(entries) - set(cited_order))
    if uncited != sorted(UNUSED_KEYS):
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
        if fields.get("language") != "en":
            fail(errors, f"{key}: accepted English reference lacks language=en metadata")
        if key in EXPECTED_TYPE and EXPECTED_TYPE[key] in {"J", "J/OL"}:
            for required in ("journal", "year", "doi"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing journal metadata {required}")
        if EXPECTED_TYPE.get(key) == "J":
            for required in ("volume", "pages"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing final article metadata {required}")
        if EXPECTED_TYPE.get(key) == "C":
            for required in ("booktitle", "publisher", "address", "year", "pages"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing conference metadata {required}")
        if EXPECTED_TYPE.get(key) == "EB/OL":
            for required in ("url", "urldate"):
                if not fields.get(required):
                    fail(errors, f"{key}: missing official webpage metadata {required}")
        if key in {
            "nvidia_tensorrt_10_3_release_notes",
            "nvidia_cuda_best_practices_12_6",
            "nvidia_cuda_programming_guide_12_6",
        } and not fields.get("year"):
            fail(errors, f"{key}: missing verified release year")
        doi = fields.get("doi")
        if doi and not re.fullmatch(r"10\.\S+/.+", doi):
            fail(errors, f"{key}: malformed DOI {doi!r}")
        url = fields.get("url")
        if url and not re.fullmatch(r"https://[^\s]+", url):
            fail(errors, f"{key}: malformed URL {url!r}")
    lema_fields = entries["lema_et_al_2025_surface_defect_benchmark"]["fields"]
    if isinstance(lema_fields, dict):
        for field, expected in LEMA_FINAL_METADATA.items():
            if lema_fields.get(field) != expected:
                fail(
                    errors,
                    f"lema_et_al_2025_surface_defect_benchmark: {field} must match "
                    f"official Springer final metadata {expected!r}",
                )
    doi_owners: dict[str, str] = {}
    title_owners: dict[str, str] = {}
    for key, entry in entries.items():
        fields = entry["fields"]
        if not isinstance(fields, dict):
            continue
        doi = fields.get("doi", "").casefold().strip()
        if doi:
            if doi in doi_owners:
                fail(errors, f"duplicate DOI for {doi_owners[doi]} and {key}: {doi}")
            doi_owners[doi] = key
        title = re.sub(r"[^a-z0-9]+", "", fields.get("title", "").casefold())
        if title:
            if title in title_owners:
                fail(errors, f"duplicate normalized title for {title_owners[title]} and {key}")
            title_owners[title] = key
    errors.extend(conference_authority_errors(entries))
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
        "publication_class",
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
                    "publication_class": PUBLICATION_CLASS_BY_TYPE[EXPECTED_TYPE[key]],
                    "metadata_status": status,
                    "render_status": f"PASS_RENDERED_[{EXPECTED_TYPE[key]}]",
                    "final_disposition": "CITED_AND_RENDERED",
                    "notes": note,
                }
            )
        for key in UNUSED_KEYS:
            status, note = METADATA_STATUS[key]
            phase57_removed = key != "reddi_et_al_2022_mlperf_mobile"
            phase57g_orphaned = key == "archet_et_al_2023_embedded_soc"
            writer.writerow(
                {
                    "citation_key": key,
                    "cited_yes_no": "NO",
                    "first_occurrence_index": "",
                    "first_occurrence_section": "",
                    "source_type": matrix[key]["source_type"],
                    "current_bib_type": entries[key]["type"],
                    "expected_rendered_type": "NOT_RENDERED",
                    "publication_class": "NOT_RENDERED_BY_DESIGN",
                    "metadata_status": status,
                    "render_status": "NOT_RENDERED_BY_DESIGN",
                    "final_disposition": (
                        "PHASE57G_CITATION_CORRECTED"
                        if phase57g_orphaned else
                        "PHASE57B_PROSE_AND_CITATION_REMOVED"
                        if phase57_removed else
                        "PRE_DRAFT_ADMITTED_SOURCE_RETAINED"
                    ),
                    "notes": (
                        "Phase 5.7G replaced the sole citation with two directly supporting memory-management sources."
                        if phase57g_orphaned else
                        "Phase 5.7B primary compression removed the associated prose and rendered citation."
                        if phase57_removed else
                        note
                    ),
                }
            )


def markdown_cross_reference_errors() -> list[str]:
    errors: list[str] = []
    text = "\n".join((MANUSCRIPT / "sections" / name).read_text(encoding="utf-8") for name in SECTION_PATHS)
    normalized_text = text.replace("`", "")
    positions: dict[str, int] = {}
    for label, caption in FIGURE_TABLE_CAPTIONS.items():
        matches = [match.start() for match in re.finditer(re.escape(caption), normalized_text)]
        if len(matches) != 1:
            fail(errors, f"{label}: expected exactly one accepted caption, found {len(matches)}")
            continue
        positions[label] = matches[0]
        callout_pattern = re.compile(rf"{re.escape(label)}(?!　)")
        callouts = [match.start() for match in callout_pattern.finditer(normalized_text) if match.start() < matches[0]]
        if not callouts:
            fail(errors, f"{label}: no body callout precedes its caption")
    figures = [positions.get(label, -1) for label in ("图1", "图2", "图3")]
    tables = [positions.get(label, -1) for label in ("表1", "表2", "表3")]
    if figures != sorted(figures) or -1 in figures:
        fail(errors, "figure captions are not sequential F1--F3")
    if tables != sorted(tables) or -1 in tables:
        fail(errors, "table captions are not sequential T1--T3")
    stale = re.findall(r"(?:图|Fig(?:ure)?\.?\s*)[5-9]|(?:表|Table\s*)[5-9]", text, flags=re.I)
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
        alignment = style.find("w:pPr/w:jc", NS)
        if element_attr(alignment, "val") != "left":
            fail(
                errors,
                f"{path.name}: {style_id} bibliography alignment is not the stable "
                "narrow-column left-aligned contract",
            )
    return errors


def rendered_docx_errors(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    paragraphs = docx_paragraphs(path)
    bibliography = [text for style, text in paragraphs if style == "Bibliography"]
    if len(bibliography) != len(EXPECTED_CITED_ORDER):
        fail(errors, f"{path.name}: expected {len(EXPECTED_CITED_ORDER)} bibliography entries, found {len(bibliography)}")
    for number, (key, entry) in enumerate(zip(EXPECTED_CITED_ORDER, bibliography), start=1):
        prefix = f"[{number}]"
        if not entry.startswith(prefix):
            fail(errors, f"{path.name}: bibliography entry {number} lacks sequential marker {prefix}")
        marker = f"[{EXPECTED_TYPE[key]}]"
        if marker not in entry:
            fail(errors, f"{path.name}: bibliography entry {number} lacks expected marker {marker}")
        if TITLE_NEEDLES[key].casefold() not in entry.casefold():
            fail(errors, f"{path.name}: bibliography entry {number} does not match {key}")
        source_fields = parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))[key]["fields"]
        if not isinstance(source_fields, dict):
            fail(errors, f"{path.name}: internal source metadata failure for {key}")
            continue
        author_count = len(re.split(r"\s+and\s+", source_fields["author"], flags=re.I))
        if author_count >= 4 and "et al." not in entry:
            fail(errors, f"{path.name}: English multi-author entry {number} does not use et al.")
        if "等" in entry:
            fail(errors, f"{path.name}: English bibliography entry {number} incorrectly uses 等")
        if EXPECTED_TYPE[key] in {"J", "C"} and "DOI:" in entry:
            fail(errors, f"{path.name}: final publication entry {number} incorrectly renders DOI")
        if EXPECTED_TYPE[key] == "J/OL" and "DOI:" not in entry:
            fail(errors, f"{path.name}: online-first entry {number} does not retain DOI")
        if key == "lema_et_al_2025_surface_defect_benchmark":
            for field in ("year", "volume", "number", "pages"):
                value = LEMA_FINAL_METADATA[field]
                if normalized_metadata_text(value) not in normalized_metadata_text(entry):
                    fail(errors, f"{path.name}: final Lema entry omits {field}: {value}")
        if EXPECTED_TYPE[key] == "C":
            for field in ("booktitle", "publisher", "address", "year", "pages"):
                value = source_fields[field]
                if normalized_metadata_text(value) not in normalized_metadata_text(entry):
                    fail(errors, f"{path.name}: conference entry {number} omits {field}: {value}")
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
        f"bibliography_entries={len(entries)} cited={len(cited_order)} "
        f"uncited={len(UNUSED_KEYS)} unresolved=0"
    )
    print("PASS: STATIC_CROSS_REFERENCE_VALIDATED figures=F1,F2,F3 tables=T1,T2,T3")
    if args.docx:
        print(f"PASS: RENDERED_BIBLIOGRAPHY_VALIDATED docx={','.join(str(path) for path in args.docx)}")
        print(
            "PASS: STRUCTURAL_REFERENCE_TYPOGRAPHY_VALIDATED "
            "Songti+Times; 7.5pt; exact14pt; left-aligned"
        )
        print("PASS: LANGUAGE_AWARE_REFERENCE_TERMS_VALIDATED English=et al.; Chinese=等_if_present")
        print("PASS: DOI_POLICY_VALIDATED final_J_C=suppressed; online_first=retained")
        print(
            "PASS: CONFERENCE_METADATA_AUTHORITY_VALIDATED "
            f"records={len(EXPECTED_CITED_CONFERENCE_KEYS)} unresolved=0 "
            f"path={CONFERENCE_AUTHORITY_PATH}"
        )
        print("PASS: CONFERENCE_METADATA_VALIDATED title+publisher+place+year+pages")
    if args.compare_full:
        print("PASS: FULL_ANONYMOUS_BIBLIOGRAPHY_IDENTITY_VALIDATED")
    if args.write_audit:
        print(f"PASS: CITATION_FINAL_AUDIT_WRITTEN path={AUDIT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
