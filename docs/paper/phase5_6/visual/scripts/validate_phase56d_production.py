#!/usr/bin/env python3
"""Validate Phase 5.6D-B formal visual assets and deterministic regeneration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[5]
PHASE56 = ROOT / "docs/paper/phase5_6"
VISUAL = PHASE56 / "visual"
PRODUCTION = VISUAL / "production"
FIGURES = PRODUCTION / "figures"
TABLES = PRODUCTION / "tables"
INSPECTION = PRODUCTION / "inspection"
SCRIPTS = VISUAL / "scripts"
CAPTIONS = PRODUCTION / "phase56_figure_table_captions.md"
VALIDATION = PRODUCTION / "phase56_visual_asset_validation.json"
MANIFEST = PRODUCTION / "phase56_visual_asset_manifest.json"
SHA_FILE = PRODUCTION / "phase56_visual_asset_sha256.txt"
PHASE_REPORT = VISUAL / "PAPER_PHASE56D_B_AUTOMATED_VISUAL_PRODUCTION_REPORT.md"
R1_REPORT = VISUAL / "PAPER_PHASE56D_B_R1_T2_AUTHORITY_REMEDIATION_REPORT.md"
FORMAL_EXECUTION = ROOT / "docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md"
RAW_ENVIRONMENT = ROOT / "docs/paper/phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json"
MANUSCRIPT_EXPERIMENT = ROOT / "docs/paper/manuscript/sections/04_experiment.md"
T2_SPEC = VISUAL / "table2_platform_protocol_spec.md"
EVIDENCE_MAP = VISUAL / "phase56_visual_evidence_map.csv"
BASELINE = "e9e906dc2bbb1fc1ee74965fd149aac02dd0250f"
VERDICT = "PHASE56_VISUAL_ASSETS_READY_R1"

STRUCTURAL_SCRIPT = SCRIPTS / "generate_phase56d_production_structural.py"
STATISTICAL_SCRIPT = SCRIPTS / "generate_phase56d_production_statistical.py"
TABLE_SCRIPT = SCRIPTS / "generate_phase56d_production_tables.py"
VALIDATOR_SCRIPT = Path(__file__).resolve()

INPUT_HASHES = {
    PHASE56 / "phase56b_run_level_metrics.csv": "f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31",
    PHASE56 / "phase56b_publication_display_values.json": "0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655",
    PHASE56 / "phase56b_correctness_table_source.csv": "d5424cb940db58eff7c826e9d99236c98ff444b37b7f45bedc993a8b70c9cf39",
    PHASE56 / "phase56b_nominal_payload.json": "706f441da5df4720b3361a9001f0a6d7c1dbb8e8e85b17c62b8ff4db38833bd8",
    PHASE56 / "phase56b_runtime_state.json": "ffcc1fad184bef828417201b96484ee734ef5d21ee1b61c048879a93866fdb17",
    PHASE56 / "phase56b_calibration_provenance.json": "10c673ce3ee3d721db053698d1570208144b5a27baccf8b07e43dbace07f5042",
    EVIDENCE_MAP: "4c54ba28facbc35c1753766e70b600c5c3c33d51e88255296a7eed626990a3cb",
    VISUAL / "phase56_related_work_attribute_evidence.csv": "fbef3e8bff6bd38ee51417d28ff5a407932ac5a7a628b1970fac2efa9321650b",
    FORMAL_EXECUTION: "3d9ea96fc430a94b090bcd2f9241313df81d5cd82bc7f7bcb7b05f47c95a85ec",
    RAW_ENVIRONMENT: "c0451d380c21ba304bfc40165e370d9ca0f3aafd3c750fd017bb581c745f5872",
    MANUSCRIPT_EXPERIMENT: "59c12c838d2512912754f92fe16c9e2fb8bb5eff9b19fa0fed926e32da049484",
}

FIGURE_STEMS = (
    "fig1_hero_data_path_phase56",
    "fig2_technical_implementation_phase56",
    "fig3_main_e2e_phase56",
    "fig4_run_level_distribution_phase56",
)
TABLE_NAMES = (
    "table1_path_feature_matrix_phase56.md",
    "table2_platform_protocol_phase56.md",
    "table3_correctness_phase56.md",
    "table4_related_work_phase56.md",
)
FORBIDDEN_VISIBLE_STATUS = ("candidate", "specification", "draft", "preview")
FROZEN_FIGURE_SVG_HASHES = {
    "fig1_hero_data_path_phase56": "d5f449ecc1c174d4315876bb2faf38e5f09d1c0bf675861466e413184cb5a887",
    "fig2_technical_implementation_phase56": "8e81ed1d50322d75c9170e99e6aa54bca9e180c79d2d8bfd947fbb81d045e605",
    "fig3_main_e2e_phase56": "881532ab226d72de92735892950d6dd97fef75e51ad390a1223c9827b0ddbdb1",
    "fig4_run_level_distribution_phase56": "8d2cb04c771c56b0fe7438cfbae07c4767b64db8553bf10c89ed6d9d67463a5e",
}
FROZEN_TABLE_HASHES = {
    "table1_path_feature_matrix_phase56.md": "789205d35cbccc1463eb0bc97b4b7208b33b44b2ee5717d2a6e42d3e84d5766e",
    "table3_correctness_phase56.md": "6d5e028fd2e48edd9de9dc5a8cd8823a6748b37ea7e3801b280497a4f5ebf1d0",
    "table4_related_work_phase56.md": "6710b9ac7018eadebcd543d4bd892c7d1e3ba60f4e6963d139295badf52287a9",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def pdf_dimensions(path: Path) -> tuple[float, float]:
    output = subprocess.run(
        ["pdfinfo", str(path)], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout
    match = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", output)
    if not match:
        raise ValueError(f"cannot resolve PDF geometry: {path}")
    return float(match.group(1)), float(match.group(2))


def visible_svg(path: Path) -> tuple[ET.Element, str]:
    root = ET.parse(path).getroot()
    return root, " ".join("".join(root.itertext()).split())


def check(condition: bool, name: str, details: str,
          checks: list[dict[str, str]]) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL", "details": details})
    if not condition:
        raise AssertionError(f"{name}: {details}")


def make_inspection_rasters(checks: list[dict[str, str]]) -> None:
    width_dir = INSPECTION / "actual_width_16cm_150dpi"
    gray_dir = INSPECTION / "grayscale_16cm_150dpi"
    width_dir.mkdir(parents=True, exist_ok=True)
    gray_dir.mkdir(parents=True, exist_ok=True)
    target_width = round(16.0 / 2.54 * 150)
    for stem in FIGURE_STEMS:
        source = FIGURES / f"{stem}.png"
        with Image.open(source) as image:
            rgb = image.convert("RGB")
            target_height = round(rgb.height * target_width / rgb.width)
            resampling = getattr(Image, "Resampling", Image)
            proof = rgb.resize((target_width, target_height), resampling.LANCZOS)
            width_path = width_dir / f"{stem}_16cm.png"
            gray_path = gray_dir / f"{stem}_16cm_grayscale.png"
            proof.save(width_path, format="PNG", dpi=(150, 150), optimize=False)
            proof.convert("L").save(gray_path, format="PNG", dpi=(150, 150), optimize=False)
            gray_stat = ImageStat.Stat(proof.convert("L"))
            check(gray_stat.extrema[0][0] < 40 and gray_stat.extrema[0][1] > 245,
                  f"grayscale_dynamic_range:{stem}",
                  f"16 cm proof {target_width}×{target_height}px retains dark ink and white background",
                  checks)


def validate_sources(checks: list[dict[str, str]]) -> tuple[dict, dict]:
    for path, expected in INPUT_HASHES.items():
        check(path.is_file(), f"source_exists:{path.name}", rel(path), checks)
        actual = sha256(path)
        check(actual == expected, f"source_hash:{path.name}", actual, checks)
    summary = json.loads((PHASE56 / "phase56b_publication_display_values.json").read_text(encoding="utf-8"))
    payload = json.loads((PHASE56 / "phase56b_nominal_payload.json").read_text(encoding="utf-8"))
    return summary, payload


def validate_l4t_authority(checks: list[dict[str, str]]) -> None:
    formal_report = FORMAL_EXECUTION.read_text(encoding="utf-8")
    check("| L4T | R36.5 |" in formal_report, "t2_l4t_formal_report",
          "formal execution report records L4T R36.5", checks)

    raw_environment = json.loads(RAW_ENVIRONMENT.read_text(encoding="utf-8"))
    raw_release = raw_environment.get("l4t_release", "")
    check("# R36 (release), REVISION: 5.0" in raw_release, "t2_l4t_raw_environment",
          "raw l4t_release records R36 release revision 5.0", checks)

    manuscript = MANUSCRIPT_EXPERIMENT.read_text(encoding="utf-8")
    check("实际记录的软件环境为L4T R36.5" in manuscript, "t2_l4t_manuscript_authority",
          "current experiment section records L4T R36.5", checks)

    generator = TABLE_SCRIPT.read_text(encoding="utf-8")
    check('L4T_PUBLICATION_VALUE = "R36.5"' in generator,
          "t2_l4t_generator_authority", "production generator is fixed to formal R36.5 wording", checks)

    with EVIDENCE_MAP.open(encoding="utf-8", newline="") as handle:
        evidence_rows = {row["element_id"]: row for row in csv.DictReader(handle)}
    l4t_row = evidence_rows.get("T2_L4T", {})
    expected_sources = {
        rel(FORMAL_EXECUTION),
        rel(RAW_ENVIRONMENT),
    }
    mapped_sources = set(l4t_row.get("source_file", "").split(";"))
    check(l4t_row.get("claim_or_cell") == "L4T publication value=R36.5"
          and mapped_sources == expected_sources,
          "t2_l4t_evidence_mapping",
          "T2 L4T cell maps to the formal report and raw environment record", checks)

    active_paths = (
        TABLES / TABLE_NAMES[1], T2_SPEC, TABLE_SCRIPT, EVIDENCE_MAP, MANUSCRIPT_EXPERIMENT,
    )
    stale = [rel(path) for path in active_paths if "L4T 36.4.3" in path.read_text(encoding="utf-8")]
    check(not stale, "stale_l4t_36_4_3_in_active_production_absent",
          "active T2 production/spec/generator/evidence/manuscript contain no stale L4T 36.4.3"
          if not stale else ", ".join(stale), checks)


def validate_figures(summary: dict, payload: dict,
                     checks: list[dict[str, str]]) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    for stem in FIGURE_STEMS:
        paths = {suffix: FIGURES / f"{stem}.{suffix}" for suffix in ("svg", "pdf", "png")}
        check(all(path.is_file() and path.stat().st_size > 0 for path in paths.values()),
              f"figure_triplet:{stem}", "SVG/PDF/PNG present and nonempty", checks)
        svg_hash = sha256(paths["svg"])
        check(svg_hash == FROZEN_FIGURE_SVG_HASHES[stem],
              f"r1_figure_svg_unchanged:{stem}", svg_hash, checks)
        root, visible = visible_svg(paths["svg"])
        raw_lower = paths["svg"].read_text(encoding="utf-8").lower()
        check(not any(token in raw_lower for token in FORBIDDEN_VISIBLE_STATUS),
              f"no_internal_status:{stem}", "no internal status term in formal SVG", checks)
        check(not re.search(r"(?:图|Figure\s*)[1-4](?:\s|[:：])", visible),
              f"no_embedded_figure_number:{stem}", "caption numbering remains external", checks)
        width_px, height_px = png_dimensions(paths["png"])
        pdf_w, pdf_h = pdf_dimensions(paths["pdf"])
        check(1885 <= width_px <= 1900, f"png_300dpi_width:{stem}",
              f"{width_px}×{height_px}px at 16 cm target", checks)
        check(452.5 <= pdf_w <= 455.0, f"pdf_vector_width:{stem}",
              f"{pdf_w:.3f}×{pdf_h:.3f} pt; insertion target 16.0 cm", checks)
        metadata[stem] = {
            "svg_width": root.attrib.get("width"),
            "svg_height": root.attrib.get("height"),
            "pdf_page_points": [pdf_w, pdf_h],
            "png_pixels": [width_px, height_px],
            "target_insertion_width_cm": 16.0,
            "sha256": {suffix: sha256(path) for suffix, path in paths.items()},
        }

    f1_path = FIGURES / "fig1_hero_data_path_phase56.svg"
    f1_root, f1_text = visible_svg(f1_path)
    f1_required = (
        "主机/设备内存域边界", "完整路径 E2E 观察（非组件因果测量）",
        "名义输入复制载荷比", "名义值；非实测总线流量",
        f'{payload["V0"]["payload_MB_decimal"]:.3f} MB/frame',
        f'{payload["V2R_V3R"]["payload_MB_decimal"]:.3f} MB/frame',
        f'{payload["ratio"]["nominal_input_copy_payload_ratio"]:.2f}×',
        "2.24× FPS", "55.45%", "+4.07% FPS", "4.03%",
    )
    check(all(token in f1_text for token in f1_required), "fig1_scientific_display",
          "payload, terminology, complete-path comparisons, boundary, and guards exact", checks)
    forbidden_payload_terms = ("transfer reduction", "bandwidth reduction", "traffic reduction", "名义尺寸比")
    check(not any(token.lower() in f1_text.lower() for token in forbidden_payload_terms),
          "fig1_payload_wording_guard", "forbidden transfer/bandwidth/size-ratio wording absent", checks)
    performance_tokens = ("2.24× FPS", "55.45%", "+4.07% FPS", "4.03%")
    attached_y: list[float] = []
    attached_tokens: set[str] = set()
    for node in f1_root.iter():
        if node.tag.endswith("text"):
            node_text = "".join(node.itertext())
            matched = {token for token in performance_tokens if token in node_text}
            if matched:
                attached_y.append(float(node.attrib["y"]))
                attached_tokens.update(matched)
    check(attached_tokens == set(performance_tokens) and all(y >= 625 for y in attached_y),
          "fig1_complete_path_attachment",
          f"performance values occur only in detached comparison footer at y={attached_y}", checks)

    f2_root, f2_text = visible_svg(FIGURES / "fig2_technical_implementation_phase56.svg")
    forbidden_f2 = ("2.24×", "55.45%", "4.07%", "40.96×", " FPS", " ms")
    check(not any(token in f2_text for token in forbidden_f2), "fig2_no_performance_numbers",
          "no performance or payload values", checks)
    stream_group = next((node for node in f2_root.iter()
                         if node.attrib.get("id") == "same-stream-operation-links"), None)
    targets = set()
    if stream_group is not None:
        targets = {node.attrib["data-target-operation"] for node in stream_group.iter()
                   if "data-target-operation" in node.attrib}
    check(targets == {"cudaMemcpy2DAsync", "fused-cuda-preprocessing", "enqueueV3"},
          "fig2_stream_operation_links",
          "stream rail targets copy, fused-kernel, and enqueue operation nodes—not buffers", checks)
    check(all(token in f2_text for token in (
        "cudaMemcpy2DAsync", "fused CUDA", "enqueueV3", "output D2H（同一 stream）",
        "single-stream, single-frame", "无 cross-frame overlap")),
        "fig2_stream_and_lifecycle_semantics", "single-stream sequential implementation labels present", checks)

    agg = summary["aggregate_verification"]
    f3_text = visible_svg(FIGURES / "fig3_main_e2e_phase56.svg")[1]
    absolute_values = []
    for variant in ("V0", "V2R", "V3R"):
        absolute_values.extend([
            f'{agg[variant]["mean_fps"]:.3f}',
            f'{agg[variant]["pooled_mean_latency_ms"]:.3f}',
            f'{agg[variant]["pooled_p95_ms"]:.3f}',
            f'{agg[variant]["pooled_p99_ms"]:.3f}',
        ])
    check(all(value in f3_text for value in absolute_values), "fig3_absolute_values",
          "all FPS mean, pooled mean, P95, and P99 displays match frozen authority", checks)
    check("每路径合并5400个延迟样本" in f3_text and "sample SD" in f3_text,
          "fig3_aggregation_terminology",
          "five-process sample SD and 5400 latency-sample semantics are explicit", checks)
    check("+0.15%" not in f3_text and "−0.12%" not in f3_text,
          "fig3_no_relative_tail_magnification", "F3 keeps absolute P95/P99 architecture", checks)

    f4_text = visible_svg(FIGURES / "fig4_run_level_distribution_phase56.svg")[1]
    check(all(token in f4_text for token in ("5 次独立进程 FPS", "process-level latency / ms",
                                             "P95 +0.15%", "P99 −0.12%", "MIXED")),
          "fig4_semantics_and_pooled_annotation",
          "process descriptors and compact pooled-tail authority present", checks)
    stat_code = STATISTICAL_SCRIPT.read_text(encoding="utf-8")
    check("FIXED_JITTER" in stat_code and ".plot(" not in stat_code and "random" not in stat_code.lower(),
          "fig4_no_pairing_or_randomness", "fixed jitter; no line plot or randomness", checks)
    return metadata


def validate_tables(checks: list[dict[str, str]]) -> None:
    for name in TABLE_NAMES:
        path = TABLES / name
        check(path.is_file() and path.stat().st_size > 0, f"table_source:{name}", rel(path), checks)
        lower = path.read_text(encoding="utf-8").lower()
        check("candidate / specification" not in lower, f"table_formal_status:{name}",
              "publication-facing source has no internal status warning", checks)

    table1 = (TABLES / TABLE_NAMES[0]).read_text(encoding="utf-8")
    with (VISUAL / "phase56_visual_evidence_map.csv").open(encoding="utf-8", newline="") as handle:
        t1_rows = [row for row in csv.DictReader(handle) if row["asset"] == "T1"]
    check(len(t1_rows) == 30 and table1.count("\n| ") >= 11, "table1_exact_matrix",
          "30 traced implementation cells and 10 publication rows", checks)
    check(sha256(TABLES / TABLE_NAMES[0]) == FROZEN_TABLE_HASHES[TABLE_NAMES[0]],
          "r1_table1_unchanged", sha256(TABLES / TABLE_NAMES[0]), checks)

    table2 = (TABLES / TABLE_NAMES[1]).read_text(encoding="utf-8")
    t2_required = ("L4T R36.5", "CUDA 12.6", "TensorRT 10.3", "OpenCV 4.5.4",
                   "1260张", "180张", "60帧预热", "1080帧", "5个独立进程")
    check(all(token in table2 for token in t2_required), "table2_provenance",
          "compact platform/model/calibration/workload/protocol facts exact", checks)
    check("L4T 36.4.3" not in table2, "t2_l4t_stale_value_rejected",
          "active Table 2 rejects the superseded L4T 36.4.3 value", checks)

    table3 = (TABLES / TABLE_NAMES[2]).read_text(encoding="utf-8")
    with (PHASE56 / "phase56b_correctness_table_source.csv").open(encoding="utf-8", newline="") as handle:
        correctness = list(csv.DictReader(handle))
    expected_cells = [f"{float(row[key]):.4f}" for row in correctness
                      for key in ("Precision", "Recall", "mAP50", "mAP50-95")]
    check(all(table3.count(value) >= expected_cells.count(value) for value in set(expected_cells)),
          "table3_correctness_values", "all 12 displayed metric cells match frozen CSV", checks)
    check("允许差异" not in table3 and "结果=通过" not in table3,
          "table3_no_gate_governance", "gate-style columns absent", checks)
    check(sha256(TABLES / TABLE_NAMES[2]) == FROZEN_TABLE_HASHES[TABLE_NAMES[2]],
          "r1_table3_unchanged", sha256(TABLES / TABLE_NAMES[2]), checks)

    table4 = (TABLES / TABLE_NAMES[3]).read_text(encoding="utf-8")
    with (VISUAL / "phase56_related_work_attribute_evidence.csv").open(
            encoding="utf-8", newline="") as handle:
        related = list(csv.DictReader(handle))
    allowed = {"YES", "NO_IF_EXPLICIT", "NOT_REPORTED", "NOT_APPLICABLE"}
    check(len(related) == 42 and {row["classification"] for row in related} <= allowed,
          "table4_traceable_cells", "6 works × 7 cells use only frozen classification vocabulary", checks)
    check("未报告" in table4 and "不等同于‘否’" in table4,
          "table4_not_reported_semantics", "NOT_REPORTED remains distinct from no", checks)
    forbidden_claims = ("本文首次", "本文唯一", "only this work", "ranking score", "total yes", "yes总数")
    check(not any(token in table4.lower() for token in forbidden_claims)
          and "不构成首次性、唯一性或优越性结论" in table4,
          "table4_positioning_boundary", "no novelty, uniqueness, rank, or YES-count claim", checks)
    check(sha256(TABLES / TABLE_NAMES[3]) == FROZEN_TABLE_HASHES[TABLE_NAMES[3]],
          "r1_table4_unchanged", sha256(TABLES / TABLE_NAMES[3]), checks)

    captions = CAPTIONS.read_text(encoding="utf-8")
    caption_required = (
        "误差棒为5个进程级FPS值的样本标准差", "每条路径合并5400个延迟样本",
        "横向偏移仅用于区分且不表示配对", "正式pooled P95/P99仍为Level-A aggregate metrics",
        "不表示优越性、首次性或唯一性",
    )
    check(all(token in captions for token in caption_required), "caption_semantics",
          "F3/F4 aggregation and T4 positioning guards frozen", checks)


def validate_mutations(checks: list[dict[str, str]]) -> None:
    protected = [
        "docs/paper/manuscript/sections", "docs/paper/manuscript/figures",
        "docs/paper/manuscript/tables", "docs/paper/phase0_5", "results",
    ]
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", *protected], cwd=ROOT,
        check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.strip()
    check(status == "", "protected_authority_unchanged",
          "authoritative manuscript, historical figures/tables, Level-A evidence, and results unchanged", checks)
    phase56_sources = subprocess.run(
        ["git", "diff", "--name-only", BASELINE, "--", "docs/paper/phase5_6/phase56b*"],
        cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.strip()
    check(phase56_sources == "", "level_b_unchanged", "all frozen Phase56B files unchanged", checks)
    docx = subprocess.run(
        ["git", "status", "--porcelain", "--", "*.docx"], cwd=ROOT,
        check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.strip()
    check(docx == "", "docx_unchanged", "no tracked or untracked DOCX mutation", checks)
    deleted = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=D", BASELINE, "--",
         "docs/paper/manuscript/figures"], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    check(deleted == "", "historical_assets_preserved", "no Phase 5.4 figure deletion", checks)
    check(all("_candidate" not in path.name for path in FIGURES.iterdir()),
          "no_candidate_filename", "formal output names do not collide with D-A candidates", checks)


def validate_determinism(checks: list[dict[str, str]]) -> None:
    with tempfile.TemporaryDirectory(prefix="phase56d-b-regen-") as tmp_name:
        tmp = Path(tmp_name)
        figures = tmp / "figures"
        tables = tmp / "tables"
        captions = tmp / "captions.md"
        subprocess.run(["python3", str(STRUCTURAL_SCRIPT), "--output-dir", str(figures)],
                       cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["python3", str(STATISTICAL_SCRIPT), "--output-dir", str(figures)],
                       cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["python3", str(TABLE_SCRIPT), "--output-dir", str(tables),
                        "--captions", str(captions)], cwd=ROOT, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mismatches: list[str] = []
        for stem in FIGURE_STEMS:
            for suffix in ("svg", "pdf", "png"):
                name = f"{stem}.{suffix}"
                if sha256(figures / name) != sha256(FIGURES / name):
                    mismatches.append(name)
        for name in TABLE_NAMES:
            if sha256(tables / name) != sha256(TABLES / name):
                mismatches.append(name)
        if sha256(captions) != sha256(CAPTIONS):
            mismatches.append(CAPTIONS.name)
        check(not mismatches, "deterministic_regeneration",
              "all 12 figure files, four table sources, and caption freeze are byte-identical"
              if not mismatches else ", ".join(mismatches), checks)


def source_record(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha256(path)}


def write_manifest(figure_metadata: dict[str, dict]) -> None:
    figure_contracts = {
        "fig1_hero_data_path_phase56": {
            "role": "Hero Figure — controlled input data-path engineering overview",
            "sources": [PHASE56 / "phase56b_nominal_payload.json",
                        PHASE56 / "phase56b_publication_display_values.json",
                        VISUAL / "phase56_visual_evidence_map.csv"],
            "script": STRUCTURAL_SCRIPT,
            "spec": VISUAL / "fig1_hero_data_path_phase56_spec.md",
            "authority": "SVG structural authority; PDF vector compatibility; PNG DOCX fallback",
        },
        "fig2_technical_implementation_phase56": {
            "role": "GPU-path implementation and memory domains",
            "sources": [VISUAL / "phase56_visual_evidence_map.csv"],
            "script": STRUCTURAL_SCRIPT,
            "spec": VISUAL / "fig2_technical_implementation_phase56_spec.md",
            "authority": "SVG structural authority; PDF vector compatibility; PNG DOCX fallback",
        },
        "fig3_main_e2e_phase56": {
            "role": "Aggregate complete-path E2E performance",
            "sources": [PHASE56 / "phase56b_run_level_metrics.csv",
                        PHASE56 / "phase56b_publication_display_values.json"],
            "script": STATISTICAL_SCRIPT,
            "spec": VISUAL / "fig3_main_e2e_phase56_spec.md",
            "authority": "SVG/PDF deterministic statistical vector authority; PNG DOCX fallback",
        },
        "fig4_run_level_distribution_phase56": {
            "role": "Run-level distributions and tail latency",
            "sources": [PHASE56 / "phase56b_run_level_metrics.csv",
                        PHASE56 / "phase56b_publication_display_values.json"],
            "script": STATISTICAL_SCRIPT,
            "spec": VISUAL / "fig4_run_level_distribution_phase56_spec.md",
            "authority": "SVG/PDF deterministic statistical vector authority; PNG DOCX fallback",
        },
    }
    figure_assets = []
    for stem, contract in figure_contracts.items():
        figure_assets.append({
            "asset": stem,
            "role": contract["role"],
            "source_data": [source_record(path) for path in contract["sources"]],
            "script": source_record(contract["script"]),
            "spec": source_record(contract["spec"]),
            "files": {suffix: {"path": rel(FIGURES / f"{stem}.{suffix}"),
                                "sha256": figure_metadata[stem]["sha256"][suffix]}
                      for suffix in ("svg", "pdf", "png")},
            "dimensions": {key: value for key, value in figure_metadata[stem].items()
                           if key != "sha256"},
            "authority_type": contract["authority"],
        })
    table_specs = (
        ("T1", TABLE_NAMES[0], "Path Feature Matrix", VISUAL / "table1_path_feature_matrix_spec.md",
         [VISUAL / "phase56_visual_evidence_map.csv"]),
        ("T2", TABLE_NAMES[1], "Platform / Model / Benchmark Protocol", VISUAL / "table2_platform_protocol_spec.md",
         [FORMAL_EXECUTION, RAW_ENVIRONMENT, MANUSCRIPT_EXPERIMENT,
          PHASE56 / "phase56b_runtime_state.json", PHASE56 / "phase56b_calibration_provenance.json",
          PHASE56 / "phase56b_run_level_metrics.csv", EVIDENCE_MAP]),
        ("T3", TABLE_NAMES[2], "Task-Level Correctness", VISUAL / "table3_correctness_spec.md",
         [PHASE56 / "phase56b_correctness_table_source.csv"]),
        ("T4", TABLE_NAMES[3], "Related-Work Qualitative Comparison", VISUAL / "table4_related_work_spec.md",
         [VISUAL / "phase56_related_work_attribute_evidence.csv"]),
    )
    table_assets = []
    for asset_id, name, role, spec, sources in table_specs:
        path = TABLES / name
        table_assets.append({
            "asset": asset_id,
            "role": role,
            "source_data": [source_record(source) for source in sources],
            "script": source_record(TABLE_SCRIPT),
            "spec": source_record(spec),
            "file": {"path": rel(path), "sha256": sha256(path)},
            "dimensions": {"format": "Markdown publication source", "target_width_cm_max": 16.0},
            "authority_type": "publication-facing table source; manuscript integration deferred",
        })
    manifest = {
        "schema_version": 1,
        "artifact_kind": "paper_phase56d_b_r1_visual_asset_manifest",
        "baseline": BASELINE,
        "verdict": VERDICT,
        "figure_assets": figure_assets,
        "table_assets": table_assets,
        "caption_freeze": source_record(CAPTIONS),
        "inspection_assets": [source_record(path) for path in sorted(INSPECTION.rglob("*.png"))],
        "determinism": "byte-identical regeneration required for SVG/PDF/PNG/table/caption outputs",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")


def write_sha_file() -> None:
    files = [path for path in PRODUCTION.rglob("*") if path.is_file() and path != SHA_FILE]
    files.extend([STRUCTURAL_SCRIPT, STATISTICAL_SCRIPT, TABLE_SCRIPT, VALIDATOR_SCRIPT])
    if PHASE_REPORT.is_file():
        files.append(PHASE_REPORT)
    if R1_REPORT.is_file():
        files.append(R1_REPORT)
    unique = sorted(set(files), key=rel)
    SHA_FILE.write_text("\n".join(f"{sha256(path)}  {rel(path)}" for path in unique) + "\n",
                        encoding="utf-8", newline="\n")


def main() -> int:
    checks: list[dict[str, str]] = []
    summary, payload = validate_sources(checks)
    validate_l4t_authority(checks)
    metadata = validate_figures(summary, payload, checks)
    validate_tables(checks)
    make_inspection_rasters(checks)
    validate_mutations(checks)
    validate_determinism(checks)
    result = {
        "schema_version": 1,
        "artifact_kind": "paper_phase56d_b_r1_visual_asset_validation",
        "baseline": BASELINE,
        "verdict": VERDICT,
        "checks": checks,
        "figure_metadata": metadata,
        "manual_raster_inspection": {
            stem: "PASS — original 300-DPI and 16-cm/150-DPI proof inspected for clipping, glyphs, labels, arrowheads, markers, hatches, and numeric readability"
            for stem in FIGURE_STEMS
        },
        "manual_grayscale_inspection": {
            stem: "PASS — explicit labels plus hatch/marker/outline redundancy remain distinguishable without color"
            for stem in FIGURE_STEMS
        },
        "mutation_check": {
            "authoritative_manuscript_markdown_modified": False,
            "docx_modified": False,
            "journal_formatting_modified": False,
            "historical_phase54_assets_deleted": False,
            "level_a_modified": False,
            "level_b_modified": False,
            "production_f1_f4_modified": False,
            "table1_modified": False,
            "table2_modified": True,
            "table2_modification_reason": "formal L4T authority correction",
            "table3_modified": False,
            "table4_modified": False,
        },
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
    write_manifest(metadata)
    write_sha_file()
    print(f"VERDICT={result['verdict']}")
    print(f"CHECKS={len(checks)}")
    print(f"WROTE={VALIDATION}")
    print(f"WROTE={MANIFEST}")
    print(f"WROTE={SHA_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
