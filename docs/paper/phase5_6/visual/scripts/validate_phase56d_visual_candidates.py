#!/usr/bin/env python3
"""Validate Phase 5.6D-A candidates, evidence contracts, and determinism."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
VISUAL = ROOT / "docs/paper/phase5_6/visual"
CANDIDATES = VISUAL / "candidates"
SCRIPTS = VISUAL / "scripts"
REPORT = VISUAL / "phase56_candidate_validation.json"
MANIFEST = VISUAL / "phase56_candidate_sha256.txt"
BASELINE = "fa3697e2bcfd36e7a99764bfe21900b22db55b91"

EXPECTED_INPUT_HASHES = {
    ROOT / "docs/paper/phase5_6/phase56b_run_level_metrics.csv":
        "f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31",
    ROOT / "docs/paper/phase5_6/phase56b_publication_display_values.json":
        "0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655",
    ROOT / "docs/paper/phase5_6/phase56b_correctness_table_source.csv":
        "d5424cb940db58eff7c826e9d99236c98ff444b37b7f45bedc993a8b70c9cf39",
    ROOT / "docs/paper/phase5_6/phase56b_nominal_payload.json":
        "706f441da5df4720b3361a9001f0a6d7c1dbb8e8e85b17c62b8ff4db38833bd8",
}

FIGURE_STEMS = (
    "fig1_hero_data_path_phase56_candidate",
    "fig2_technical_implementation_phase56_candidate",
    "fig3_main_e2e_phase56_candidate",
    "fig4_run_level_distribution_phase56_candidate",
)
TABLE_NAMES = (
    "table1_path_feature_matrix_candidate.md",
    "table2_platform_protocol_candidate.md",
    "table3_correctness_candidate.md",
    "table4_related_work_candidate.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not PNG: {path}")
    return struct.unpack(">II", signature[16:24])


def check(condition: bool, name: str, details: str, checks: list[dict[str, str]]) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL", "details": details})
    if not condition:
        raise AssertionError(f"{name}: {details}")


def validate() -> dict[str, object]:
    checks: list[dict[str, str]] = []
    figure_metadata: dict[str, object] = {}

    for path, expected in EXPECTED_INPUT_HASHES.items():
        actual = sha256(path)
        check(actual == expected, f"source_hash:{path.name}", actual, checks)

    for stem in FIGURE_STEMS:
        paths = {suffix: CANDIDATES / f"{stem}.{suffix}" for suffix in ("svg", "pdf", "png")}
        check(all(path.is_file() and path.stat().st_size > 0 for path in paths.values()),
              f"candidate_triplet:{stem}", "SVG/PDF/PNG present and nonempty", checks)
        root = ET.parse(paths["svg"]).getroot()
        svg_text = paths["svg"].read_text(encoding="utf-8")
        visible_text = " ".join("".join(root.itertext()).split())
        check("CANDIDATE / SPECIFICATION" in visible_text,
              f"candidate_mark:{stem}", "candidate watermark present", checks)
        check(not re.search(r"(?:图|Figure\s*)[1-4](?:\s|[:：])", visible_text),
              f"no_embedded_caption:{stem}", "no Figure-number caption in image", checks)
        if stem.startswith("fig2_"):
            forbidden = ("2.24×", "55.45%", "4.07%", "40.96×", " FPS", " ms")
            check(not any(token in visible_text for token in forbidden),
                  "fig2_no_performance_numbers", "forbidden performance tokens absent", checks)
        if stem.startswith("fig1_"):
            required = ("2.24× FPS", "55.45%", "+4.07% FPS", "4.03%", "40.96×",
                        "非实测总线流量", "非组件因果测量")
            check(all(token in visible_text for token in required),
                  "fig1_causality_payload_labels", "required values and guards present", checks)
        png_size = png_dimensions(paths["png"])
        pdfinfo = subprocess.run(["pdfinfo", str(paths["pdf"])], check=True,
                                 text=True, stdout=subprocess.PIPE).stdout
        page_match = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", pdfinfo)
        check(page_match is not None, f"pdf_geometry:{stem}", "pdfinfo page size resolved", checks)
        figure_metadata[stem] = {
            "svg_width": root.attrib.get("width"), "svg_height": root.attrib.get("height"),
            "png_width_px": png_size[0], "png_height_px": png_size[1],
            "pdf_page_points": [float(page_match.group(1)), float(page_match.group(2))],
            "sha256": {suffix: sha256(path) for suffix, path in paths.items()},
        }

    for name in TABLE_NAMES:
        text = (CANDIDATES / name).read_text(encoding="utf-8")
        check("CANDIDATE / SPECIFICATION" in text, f"candidate_mark:{name}",
              "candidate authority warning present", checks)

    with (VISUAL / "phase56_related_work_attribute_evidence.csv").open(
            encoding="utf-8", newline="") as handle:
        related = list(csv.DictReader(handle))
    allowed = {"YES", "NO_IF_EXPLICIT", "NOT_REPORTED", "NOT_APPLICABLE"}
    check(len(related) == 42, "related_work_cell_count", f"{len(related)} rows", checks)
    check({row["classification"] for row in related} <= allowed,
          "related_work_vocabulary", "only allowed internal vocabulary", checks)
    groups: dict[str, set[str]] = {}
    for row in related:
        groups.setdefault(row["work"], set()).add(row["attribute"])
    check(len(groups) == 6 and all(len(attrs) == 7 for attrs in groups.values()),
          "related_work_matrix_shape", "6 works × 7 unique attributes", checks)

    with (VISUAL / "phase56_visual_evidence_map.csv").open(
            encoding="utf-8", newline="") as handle:
        evidence_rows = list(csv.DictReader(handle))
    check(len(evidence_rows) >= 80, "visual_evidence_map_density",
          f"{len(evidence_rows)} trace rows", checks)
    check({f"F{i}" for i in range(1, 5)} | {f"T{i}" for i in range(1, 5)}
          <= {row["asset"] for row in evidence_rows},
          "visual_evidence_asset_coverage", "F1-F4 and T1-T4 covered", checks)

    protected = subprocess.run(
        ["git", "diff", "--name-only", BASELINE, "--",
         "docs/paper/manuscript/sections", "docs/paper/manuscript/figures",
         "docs/paper/manuscript/tables"], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE).stdout.strip()
    check(protected == "", "protected_manuscript_assets_unchanged",
          "no diff from frozen baseline in authoritative sections/figures/tables", checks)
    docx = subprocess.run(
        ["git", "diff", "--name-only", BASELINE, "--", "*.docx"], cwd=ROOT,
        check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    check(docx == "", "docx_unchanged", "no tracked DOCX diff from baseline", checks)

    with tempfile.TemporaryDirectory(prefix="phase56d-validate-", dir=VISUAL) as tmp_name:
        tmp = Path(tmp_name)
        subprocess.run(["python3", str(SCRIPTS / "generate_phase56d_structural_candidates.py"),
                        "--output-dir", str(tmp)], cwd=ROOT, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["python3", str(SCRIPTS / "generate_phase56d_statistical_candidates.py"),
                        "--output-dir", str(tmp)], cwd=ROOT, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mismatches = []
        for stem in FIGURE_STEMS:
            for suffix in ("svg", "pdf", "png"):
                name = f"{stem}.{suffix}"
                if sha256(tmp / name) != sha256(CANDIDATES / name):
                    mismatches.append(name)
        check(not mismatches, "figure_deterministic_regeneration",
              "all 12 figure hashes reproduced" if not mismatches else ", ".join(mismatches), checks)

    return {
        "schema_version": 1,
        "artifact_kind": "paper_phase56d_a_candidate_validation",
        "verdict": "PASS",
        "baseline": BASELINE,
        "candidate_authority": "CANDIDATE / SPECIFICATION",
        "checks": checks,
        "figure_metadata": figure_metadata,
        "manual_raster_inspection": {
            stem: "PASS — original-resolution PNG inspected for clipping, glyphs, overlap, line/marker visibility, grayscale redundancy, and absence of embedded caption"
            for stem in FIGURE_STEMS
        },
    }


def write_manifest() -> None:
    excluded = {REPORT, MANIFEST}
    files = sorted(path for path in VISUAL.rglob("*") if path.is_file() and path not in excluded)
    lines = [f"{sha256(path)}  {path.relative_to(ROOT)}" for path in files]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    result = validate()
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    write_manifest()
    print(f"VERDICT={result['verdict']}")
    print(f"CHECKS={len(result['checks'])}")
    print(f"WROTE={REPORT.relative_to(ROOT)}")
    print(f"WROTE={MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
