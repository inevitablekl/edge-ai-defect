#!/usr/bin/env python3
"""Derive and freeze Paper Phase 5.6B Level-B evidence without new runs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
VALIDATION = REPO / "tools" / "validation"
sys.path.insert(0, str(VALIDATION))

from evaluate_stage_k_task_metrics import evaluate_backend, load_ground_truth  # noqa: E402
from stage_r_v2_task_accuracy import normalize  # noqa: E402


OUTPUT = REPO / "docs" / "paper" / "phase5_6"
GATE = REPO / "docs" / "paper" / "phase0_5" / "evidence" / "v2r_gate_d_v1"
RAW = Path("/home/orin/edge-ai-local-evidence/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1")
GT = REPO / "results/validation/stage_k_task_eval_v2/ground_truth/test_ground_truth.json"
V0_RESULT = REPO / "results/validation/stage_q/q5_accuracy_v1/int8_result.json"
TEST_MANIFEST = REPO / "results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json"
TRAIN_MANIFEST = REPO / "results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json"
CAL_MANIFEST = REPO / "results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json"
CAL_ROOT = Path("/home/orin/edge-ai-local-models/stage_q/formal")
STARTING_HEAD = "9002c5ece26d93b54b89bffc88fa9fb361bf2d00"

LEVEL_A = {
    "v2r_v0_fps_ratio": 2.236671,
    "v2r_v0_mean_latency_reduction_percent": 55.4519,
    "v3r_v2r_fps_change_percent": 4.0738,
    "v3r_v2r_mean_latency_change_percent": -4.0349,
    "v3r_v2r_p95_change_percent": 0.1514,
    "v3r_v2r_p99_change_percent": -0.1184,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return str(path.resolve())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def evaluate_frozen_predictions() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    gt_artifact, gt_by_image = load_ground_truth(GT)
    paths = {"V0": V0_RESULT, "V2R": GATE / "v2r_result.json", "V3R": GATE / "v3r_result.json"}
    metrics: dict[str, Any] = {}
    classwise: dict[str, Any] = {}
    normalized: dict[str, Any] = {}
    for variant, path in paths.items():
        normalized[variant] = normalize(path, gt_artifact)
        by_image = {item["image_id"]: item["detections"] for item in normalized[variant]["images"]}
        metrics[variant], classwise[variant] = evaluate_backend(by_image, gt_by_image)

    test = load_json(TEST_MANIFEST)
    expected_paths = [entry["image_path"] for entry in test["entries"]]
    observed_paths = [item["image_path"] for item in normalized["V3R"]["images"]]
    if test["entry_count"] != 180 or expected_paths != observed_paths:
        raise RuntimeError("V3R predictions do not match the frozen 180-image workload")
    v3_source = load_json(paths["V3R"])
    if {item["width"] for item in v3_source["images"]} != {200} or {item["height"] for item in v3_source["images"]} != {200}:
        raise RuntimeError("frozen V3R geometry is not uniformly 200x200")

    comparisons = {}
    for baseline in ("V0", "V2R"):
        comparisons[baseline] = {
            "max_absolute_class_AP50_difference": max(
                abs(classwise["V3R"][name]["AP50"] - classwise[baseline][name]["AP50"])
                for name in classwise["V3R"]
            ),
            "max_absolute_class_Recall_difference": max(
                abs(classwise["V3R"][name]["recall"] - classwise[baseline][name]["recall"])
                for name in classwise["V3R"]
            ),
        }
    if any(value != 0.0 for item in comparisons.values() for value in item.values()):
        raise RuntimeError("V3R class-level metrics are not exactly equal to V0/V2R")

    task = {
        "schema_version": 1,
        "artifact_kind": "paper_phase56b_v3r_deterministic_task_metrics",
        "authority_level": "Level B — Derived Evidence",
        "governance": "new deterministic analysis of frozen predictions",
        "not_new_inference": True,
        "not_new_benchmark": True,
        "not_second_parameter_selection_gate": True,
        "not_new_gate_d": True,
        "prediction": {"path": repo_path(paths["V3R"]), "sha256": sha256(paths["V3R"]), "schema": 4, "images": 180, "detections": 447},
        "workload": {"path": repo_path(TEST_MANIFEST), "sha256": sha256(TEST_MANIFEST), "images": 180},
        "ground_truth": {"path": repo_path(GT), "sha256": sha256(GT)},
        "evaluator": {
            "wrapper_path": "tools/validation/stage_r_v2_task_accuracy.py",
            "wrapper_sha256": sha256(VALIDATION / "stage_r_v2_task_accuracy.py"),
            "module_path": "tools/validation/evaluate_stage_k_task_metrics.py",
            "module_sha256": sha256(VALIDATION / "evaluate_stage_k_task_metrics.py"),
            "iou_thresholds": metrics["V3R"]["iou_thresholds"],
            "matching": "class-aware one-to-one; highest-IoU eligible ground truth after confidence sorting",
            "ap": "101-point interpolated precision envelope",
            "confidence": "predictions already filtered by frozen 0.25 threshold; no additional filtering",
        },
        "metrics": metrics["V3R"],
        "class_metrics": classwise["V3R"],
        "comparisons": comparisons,
        "alters_level_a_authority": False,
    }

    correctness_rows = []
    class_rows = []
    authority = {"V0": "Existing formal correctness authority", "V2R": "Existing formal correctness authority", "V3R": "Phase56 deterministic evaluation of frozen predictions"}
    for variant in ("V0", "V2R", "V3R"):
        item = metrics[variant]
        correctness_rows.append({"Path": variant, "Precision": repr(item["precision"]), "Recall": repr(item["recall"]), "mAP50": repr(item["mAP50"]), "mAP50-95": repr(item["mAP50_95"]), "AuthorityType": authority[variant]})
        for name, class_item in classwise[variant].items():
            class_rows.append({"Path": variant, "Class": name, "AP50": repr(class_item["AP50"]), "Recall": repr(class_item["recall"]), "AuthorityType": authority[variant]})
    return task, correctness_rows, class_rows


def derive_runs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    pooled = {variant: [] for variant in ("V0", "V2R", "V3R")}
    fps = {variant: [] for variant in pooled}
    means = {variant: [] for variant in pooled}
    run_dirs = sorted((RAW / "formal_runs").iterdir())
    if len(run_dirs) != 15:
        raise RuntimeError("formal archive does not contain 15 process directories")
    for order, run_dir in enumerate(run_dirs, 1):
        metric_path = run_dir / "metrics.json"
        manifest_path = run_dir / "run_manifest.json"
        metric = load_json(metric_path)
        manifest = load_json(manifest_path)
        samples = [float(value) for value in metric["latency_ms"]]
        variant = metric["variant"]
        run_fps = metric["measured_frames"] / (metric["process_wall_ms"] / 1000.0)
        run_mean = statistics.fmean(samples)
        if len(samples) != 1080 or manifest["execution_mode"] != "FORMAL_AUTHORITY" or metric["evidence_class"] != "FORMAL_PERFORMANCE_EVIDENCE":
            raise RuntimeError(f"rejected formal-process contract: {run_dir}")
        pooled[variant].extend(samples)
        fps[variant].append(run_fps)
        means[variant].append(run_mean)
        rows.append({
            "variant": variant,
            "run_id": run_dir.name,
            "execution_order": order,
            "fps": repr(run_fps),
            "mean_latency_ms": repr(run_mean),
            "process_p95_ms": repr(percentile(samples, 0.95)),
            "process_p99_ms": repr(percentile(samples, 0.99)),
            "measured_frames": len(samples),
            "accepted": "true",
            "independence_semantics": "independent_process",
            "source_path": str(metric_path.resolve()),
            "source_sha256": sha256(metric_path),
        })
    if {variant: len(fps[variant]) for variant in fps} != {"V0": 5, "V2R": 5, "V3R": 5}:
        raise RuntimeError("accepted process count is not five per variant")
    if any(len(values) != 5400 for values in pooled.values()) or sum(map(len, pooled.values())) != 16200:
        raise RuntimeError("pooled latency sample count mismatch")
    aggregate = {
        variant: {
            "accepted_independent_processes": 5,
            "latency_samples": 5400,
            "mean_fps": statistics.fmean(fps[variant]),
            "sample_sd_fps": statistics.stdev(fps[variant]),
            "min_fps": min(fps[variant]),
            "max_fps": max(fps[variant]),
            "pooled_mean_latency_ms": statistics.fmean(pooled[variant]),
            "pooled_p95_ms": percentile(pooled[variant], 0.95),
            "pooled_p99_ms": percentile(pooled[variant], 0.99),
        }
        for variant in pooled
    }
    derived = {
        "v2r_v0_fps_ratio": aggregate["V2R"]["mean_fps"] / aggregate["V0"]["mean_fps"],
        "v2r_v0_mean_latency_reduction_percent": (1.0 - aggregate["V2R"]["pooled_mean_latency_ms"] / aggregate["V0"]["pooled_mean_latency_ms"]) * 100.0,
        "v3r_v2r_fps_change_percent": (aggregate["V3R"]["mean_fps"] / aggregate["V2R"]["mean_fps"] - 1.0) * 100.0,
        "v3r_v2r_mean_latency_change_percent": (aggregate["V3R"]["pooled_mean_latency_ms"] / aggregate["V2R"]["pooled_mean_latency_ms"] - 1.0) * 100.0,
        "v3r_v2r_p95_change_percent": (aggregate["V3R"]["pooled_p95_ms"] / aggregate["V2R"]["pooled_p95_ms"] - 1.0) * 100.0,
        "v3r_v2r_p99_change_percent": (aggregate["V3R"]["pooled_p99_ms"] / aggregate["V2R"]["pooled_p99_ms"] - 1.0) * 100.0,
    }
    precision = {"v2r_v0_fps_ratio": 6, "v2r_v0_mean_latency_reduction_percent": 4, "v3r_v2r_fps_change_percent": 4, "v3r_v2r_mean_latency_change_percent": 4, "v3r_v2r_p95_change_percent": 4, "v3r_v2r_p99_change_percent": 4}
    for key, expected in LEVEL_A.items():
        if round(derived[key], precision[key]) != expected:
            raise RuntimeError(f"Level-A identity mismatch for {key}")
    return rows, {"aggregate_verification": aggregate, "recomputed_for_verification_only": derived}


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    required = [RAW / "archive_manifest.tsv", GT, V0_RESULT, TEST_MANIFEST, TRAIN_MANIFEST, CAL_MANIFEST, CAL_ROOT / "engine_manifest_v2.json", CAL_ROOT / "calibration_cache.meta.json", OUTPUT / "PAPER_PHASE56B_MATERIAL_DISCREPANCY_REPORT.md"]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    if sha256(GATE / "v3r_result.json") != "3e04478c181a697ccffbf63f5405ab8eecfce61a8fe2db885b2ce81045514678":
        raise RuntimeError("V3R prediction SHA mismatch")

    task, correctness_rows, class_rows = evaluate_frozen_predictions()
    write_json(OUTPUT / "phase56b_v3r_task_metrics.json", task)
    write_csv(OUTPUT / "phase56b_correctness_table_source.csv", ["Path", "Precision", "Recall", "mAP50", "mAP50-95", "AuthorityType"], correctness_rows)
    write_csv(OUTPUT / "phase56b_correctness_class_metrics.csv", ["Path", "Class", "AP50", "Recall", "AuthorityType"], class_rows)

    payload = {
        "schema_version": 1,
        "artifact_kind": "paper_phase56b_nominal_input_copy_payload",
        "authority_level": "Level B — Derived Evidence",
        "V0": {"representation": "FP32 host NCHW tensor", "N": 1, "C": 3, "H": 640, "W": 640, "bytes_per_element": 4, "payload_bytes": 4915200, "payload_MB_decimal": 4.9152},
        "V2R_V3R": {"representation": "packed BGR uint8", "width": 200, "height": 200, "channels": 3, "bytes_per_element": 1, "source_pointer": "PageableRawStaging::data or PinnedRawStaging::data", "source_pitch": 600, "copy_width_bytes": 600, "copy_height": 200, "destination_pitch": 12288, "payload_bytes": 120000, "payload_MB_decimal": 0.12},
        "ratio": {"formula": "4915200 / 120000", "nominal_input_copy_payload_ratio": 40.96},
        "implementation_sources": [
            {"path": "configs/model_contracts/yolov8n_neudet_frozen.yaml", "sha256": sha256(REPO / "configs/model_contracts/yolov8n_neudet_frozen.yaml")},
            {"path": "src/tensorrt_engine.cpp", "sha256": sha256(REPO / "src/tensorrt_engine.cpp")},
            {"path": "backend_tensorrt/cuda_preprocessor.cu", "sha256": sha256(REPO / "backend_tensorrt/cuda_preprocessor.cu")},
            {"path": "backend_tensorrt/pageable_raw_staging.cpp", "sha256": sha256(REPO / "backend_tensorrt/pageable_raw_staging.cpp")},
            {"path": "backend_tensorrt/pinned_raw_staging.cpp", "sha256": sha256(REPO / "backend_tensorrt/pinned_raw_staging.cpp")},
        ],
        "workload_source": {"path": repo_path(TEST_MANIFEST), "sha256": sha256(TEST_MANIFEST), "images": 180, "all_observed_geometry": "200x200x3"},
        "boundary": "This is a deterministic representation/copy-size derivation from the frozen workload and implementation. It is not measured bus traffic.",
        "not_measured": ["total DRAM traffic", "PCIe traffic", "bandwidth", "H2D duration", "transfer acceleration", "E2E acceleration factor"],
        "alters_level_a_authority": False,
    }
    if payload["V2R_V3R"]["copy_width_bytes"] * payload["V2R_V3R"]["copy_height"] != 120000:
        raise RuntimeError("copy geometry arithmetic mismatch")
    write_json(OUTPUT / "phase56b_nominal_payload.json", payload)

    run_rows, run_summary = derive_runs()
    run_fields = ["variant", "run_id", "execution_order", "fps", "mean_latency_ms", "process_p95_ms", "process_p99_ms", "measured_frames", "accepted", "independence_semantics", "source_path", "source_sha256"]
    write_csv(OUTPUT / "phase56b_run_level_metrics.csv", run_fields, run_rows)
    display = {
        "schema_version": 1,
        "artifact_kind": "paper_phase56b_publication_display_values",
        "authority_level": "Level B verification/display mapping; Level A unchanged",
        "authority_precision": LEVEL_A,
        "publication_display_precision": {
            "v2r_v0_fps_ratio": "2.24×", "v2r_v0_mean_latency_reduction": "55.45%", "v3r_v2r_fps": "+4.07%", "v3r_v2r_mean_latency": "-4.03%", "v3r_v2r_p95": "+0.15%", "v3r_v2r_p99": "-0.12%", "absolute_fps_decimals": 3, "absolute_latency_ms_decimals": 3,
        },
        **run_summary,
        "process_semantics": "15 independent processes; not paired or matched repeated measures",
        "tail": {"verdict": "MIXED", "interpretation": "P95 and P99 relative changes are both below 0.2% and have opposite directions."},
        "aggregation": {"processes_per_variant": 5, "samples_per_process": 1080, "pooled_samples_per_variant": 5400, "total_samples": 16200, "p95_p99": "pooled variant-level latency samples; not mean(process-level percentile)"},
        "alters_level_a_authority": False,
    }
    write_json(OUTPUT / "phase56b_publication_display_values.json", display)

    formal_report = REPO / "docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md"
    preflight_env = REPO / "docs/paper/phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json"
    runtime = {
        "schema_version": 1, "artifact_kind": "paper_phase56b_runtime_state", "authority_level": "Level B — Derived Evidence",
        "proven": {"platform": "NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super", "architecture": "aarch64", "power_mode": "MAXN_SUPER", "nvpmodel_mode": 2, "clock_setting_command_invoked": False, "jetson_clocks_show": "unavailable as non-root", "independently_archived_clock_frequency_evidence": False, "pre_run_temperature_c_approx": "46.8–47.1", "post_run_temperature_c_approx": "48.7–49.6", "temperature_observation": "non-continuous pre/post observations"},
        "not_proven": ["no throttling", "fixed GPU frequency", "fixed CPU frequency", "fixed EMC frequency", "fixed fan speed", "continuous thermal stability", "stable power state"],
        "sources": [{"path": repo_path(formal_report), "sha256": sha256(formal_report)}, {"path": repo_path(preflight_env), "sha256": sha256(preflight_env)}],
        "alters_level_a_authority": False,
    }
    write_json(OUTPUT / "phase56b_runtime_state.json", runtime)

    train = load_json(TRAIN_MANIFEST)
    test = load_json(TEST_MANIFEST)
    calibration_manifest = load_json(CAL_MANIFEST)
    cache_meta = load_json(CAL_ROOT / "calibration_cache.meta.json")
    engine_manifest = load_json(CAL_ROOT / "engine_manifest_v2.json")
    train_shas = {item["image_sha256"] for item in train["entries"]}
    test_shas = {item["image_sha256"] for item in test["entries"]}
    if len(train_shas) != 1260 or train_shas & test_shas or calibration_manifest["image_count"] != 1260:
        raise RuntimeError("calibration split/count provenance mismatch")
    calibration = {
        "schema_version": 1, "artifact_kind": "paper_phase56b_calibration_provenance", "authority_level": "Level B — Derived Evidence",
        "calibration": {"images": 1260, "source": "deduplicated training split", "test_split_excluded": True, "calibrator": "IInt8EntropyCalibrator2", "batch_size": 1, "input_size": [640, 640], "preprocessing_identity": "production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255", "production_equivalent_preprocessing": True, "same_cuda_implementation_as_v2r_v3r": False, "builder_flags": ["INT8", "FP16"], "tensorrt": "10.3", "host_input_io": "FP32", "engine_terminology_en": "TensorRT INT8 mixed-precision Engine", "engine_terminology_zh": "TensorRT INT8混合精度Engine"},
        "cache": {"mode": "force-miss", "successful_calibration_batches": cache_meta["successful_calibration_batches"], "images_consumed": cache_meta["images_consumed"], "generated_after_calibration": True, "archived": True, "sha256": cache_meta["cache_sha256"], "pre_existing_cache_reused_as_formal_build_input": False, "wording": "calibration cache generated and archived after forced cache miss; not reused as formal-build input"},
        "engine": {"sha256": engine_manifest["engine_sha256"], "precision_mode": engine_manifest["precision_mode"], "int8_enabled": engine_manifest["int8_enabled"], "fp16_fallback_enabled": engine_manifest["fp16_fallback_enabled"], "host_io_dtype": engine_manifest["host_io_dtype"]},
        "sources": [
            {"path": repo_path(CAL_MANIFEST), "sha256": sha256(CAL_MANIFEST)}, {"path": repo_path(TRAIN_MANIFEST), "sha256": sha256(TRAIN_MANIFEST)}, {"path": repo_path(TEST_MANIFEST), "sha256": sha256(TEST_MANIFEST)}, {"path": "src/stage_q_int8_builder.cpp", "sha256": sha256(REPO / "src/stage_q_int8_builder.cpp")}, {"path": "src/preprocessor.cpp", "sha256": sha256(REPO / "src/preprocessor.cpp")}, {"path": str((CAL_ROOT / "calibration_cache.meta.json").resolve()), "sha256": sha256(CAL_ROOT / "calibration_cache.meta.json")}, {"path": str((CAL_ROOT / "engine_manifest_v2.json").resolve()), "sha256": sha256(CAL_ROOT / "engine_manifest_v2.json")},
        ],
        "alters_level_a_authority": False,
    }
    if cache_meta["successful_calibration_batches"] != 1260 or cache_meta["images_consumed"] != 1260 or engine_manifest["precision_mode"] != "INT8 + FP16 fallback":
        raise RuntimeError("formal calibration metadata mismatch")
    write_json(OUTPUT / "phase56b_calibration_provenance.json", calibration)

    aggregate = display["aggregate_verification"]
    run_table = "\n".join(
        f"| {row['variant']} | {row['run_id']} | {row['execution_order']} | {float(row['fps']):.6f} | {float(row['mean_latency_ms']):.6f} | {float(row['process_p95_ms']):.6f} | {float(row['process_p99_ms']):.6f} |"
        for row in run_rows
    )
    report = f"""# Paper Phase 5.6B Controlled Evidence Promotion Report

## Verdict

`PHASE56_DERIVED_EVIDENCE_FROZEN`

## Scope and authority

This evidence-only work unit performed deterministic reanalysis without new inference, benchmark, timing, telemetry, or power runs. Existing Level-A E2E authority and provenance are unchanged. The outputs in this directory are Level-B derived evidence.

## D-01 resolution

`D-01 = CLOSED`. Scientific Change Control adopted the precise wording: `calibration cache generated and archived after forced cache miss; not reused as formal-build input`. The unqualified candidate wording was retired. This is a provenance-wording correction, not experiment invalidation.

## V3R correctness

The governed wrapper `tools/validation/stage_r_v2_task_accuracy.py` reuses `tools/validation/evaluate_stage_k_task_metrics.py`. Frozen prediction SHA256: `{task['prediction']['sha256']}`; 180 images; 447 detections.

| Precision | Recall | mAP50 | mAP50-95 |
|---:|---:|---:|---:|
| {task['metrics']['precision']!r} | {task['metrics']['recall']!r} | {task['metrics']['mAP50']!r} | {task['metrics']['mAP50_95']!r} |

All four maximum absolute class AP50/Recall differences versus V0/V2R are exact zero. This is new deterministic analysis of frozen predictions, not new inference, a second parameter-selection gate, or a new Gate D. Under this frozen workload and governed protocol, the three paths have identical reported task and class AP50/Recall values; no universal or future-input equivalence is claimed.

## Nominal input-copy payload

- V0: `1 × 3 × 640 × 640 × 4 = 4,915,200 B = 4.9152 MB/frame`.
- V2R/V3R: `600 copy-width bytes × 200 rows = 120,000 B = 0.1200 MB/frame`.
- Ratio: `4,915,200 / 120,000 = 40.96×`.

This is derived from frozen workload geometry and implementation copy semantics. It is not measured bus/DRAM/PCIe traffic, bandwidth, H2D duration, transfer acceleration, or an E2E causal factor.

## Five-run evidence

Each row is an independent accepted process. Similar run identifiers do not imply pairing.

| Variant | Run | Order | FPS | Mean ms | Process P95 ms | Process P99 ms |
|---|---|---:|---:|---:|---:|---:|
{run_table}

There are five processes and 5,400 samples per variant, 16,200 total. Formal P95/P99 are pooled variant-level percentiles, not the mean of process percentiles. No paired differences, p-values, confidence intervals, or significance tests were produced.

## Level-A reconciliation and tail

Verification reproduced `2.236671×`, `55.4519%`, `+4.0738%`, `-4.0349%`, `+0.1514%`, and `-0.1184%` at authority precision. Tail remains `MIXED`: P95 and P99 relative changes are both below 0.2% and have opposite directions.

## Runtime state

Provenance supports the named Jetson platform, MAXN_SUPER/mode 2, no invoked clock-setting command, absent independently archived clock-frequency evidence, approximate pre/post observations of 46.8–47.1 °C and 48.7–49.6 °C, and non-continuous temperature observation. It does not prove fixed frequencies, no throttling, fixed fan speed, continuous thermal stability, or stable power.

## Calibration

The frozen facts are 1,260 deduplicated training images with test exclusion, `IInt8EntropyCalibrator2`, batch 1, 640×640, production-equivalent CPU `Preprocessor` identity `BGR-LetterBox640-RGB-NCHW-FP32/255`, INT8+FP16 flags, TensorRT 10.3, and FP32 host I/O. The safe term is `TensorRT INT8 mixed-precision Engine`; pure/all-INT8 terminology is unsupported. Calibration uses the production CPU Preprocessor identity; this does not claim that it uses the V2R/V3R CUDA implementation.

## Publication precision

Authority precision is retained in machine-readable evidence. Display mapping is `2.24×`, `55.45%`, `+4.07%`, `-4.03%`, `+0.15%`, `-0.12%`; candidate absolute precision is three decimals for FPS and latency. No manuscript was modified.

## Outputs and mutation boundary

Machine-readable sources, the Level-B addendum, manifest, and SHA list are colocated here. Level A, manuscript sources, DOCX, PDF, figures, tables, styles, equations, captions, bibliography, and journal templates were not modified.
"""
    (OUTPUT / "PAPER_PHASE56B_CONTROLLED_EVIDENCE_PROMOTION_REPORT.md").write_text(report, encoding="utf-8")

    class_table = "\n".join(f"| {name} | {item['AP50']!r} | {item['recall']!r} |" for name, item in task["class_metrics"].items())
    addendum = f"""# Paper Phase 5.6 Level-B Evidence Addendum v1.0

## 1. Authority Model

Level A is the unchanged formal E2E benchmark authority. Level B is deterministic evidence derived from frozen predictions, raw benchmark records, code, workload manifests, and provenance. Every Level-B item records `alters_level_a_authority = false`.

## 2. V3R Task-Level Correctness

V3R Precision `{task['metrics']['precision']!r}`, Recall `{task['metrics']['recall']!r}`, mAP50 `{task['metrics']['mAP50']!r}`, and mAP50-95 `{task['metrics']['mAP50_95']!r}` were produced by deterministic execution of the governed evaluator over the frozen prediction artifact.

| Class | AP50 | Recall |
|---|---:|---:|
{class_table}

All maximum absolute V3R class AP50/Recall differences versus both V0 and V2R are exact zero. This is not new inference, a new benchmark, a second selection gate, or a new Gate D.

## 3. Nominal Input-Copy Payload

V0 is 4,915,200 B (4.9152 decimal MB) and V2R/V3R are 120,000 B (0.1200 decimal MB), giving a 40.96× nominal input-copy payload ratio. For V2R/V3R the effective `cudaMemcpy2DAsync` width is 600 B and height is 200. This is not measured bus traffic or a transfer/E2E acceleration factor.

## 4. Five-Run Evidence

The source CSV contains 15 independent accepted processes, five per variant, with 1,080 measured samples per process. Formal tail percentiles pool 5,400 samples per variant; process percentiles remain run-level descriptors. Runs are not paired or matched, and no inferential statistics were performed.

## 5. Runtime-State Provenance

Recorded facts are the Jetson platform, MAXN_SUPER/mode 2, no invoked clock-setting command, no independently archived clock-frequency evidence, and non-continuous pre/post temperature observations. Fixed clocks, no throttling, fixed fan speed, continuous thermal stability, and stable power are not proven.

## 6. Calibration Provenance

Formal calibration consumed 1,260 deduplicated train images and excluded the test split. It used `IInt8EntropyCalibrator2`, batch 1, 640×640, production-equivalent `production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255`, INT8+FP16 builder flags, TensorRT 10.3, and FP32 I/O. Cache mode was force-miss; all 1,260 batches ran; the cache was generated afterward and archived; no pre-existing cache was reused as formal-build input. The Engine is a TensorRT INT8 mixed-precision Engine.

## 7. Publication Precision

Exact authority values map to `2.24×`, `55.45%`, `+4.07%`, `-4.03%`, `+0.15%`, and `-0.12%`. Exact and display precision are separate layers. Absolute FPS and latency candidates use three decimals.

## 8. Scientific Boundaries

The 40.96× ratio is not measured traffic/bandwidth/H2D time and cannot alone explain E2E speedup. V3R metrics are frozen-prediction analysis. Runs are independent, not paired. Tail is `MIXED`; there is no consistent tail-latency improvement evidence. Temperature observations are not continuous telemetry. Calibration claims are limited to direct repository provenance.

## 9. Scientific Change Control History

D-01 is closed by adopting precise forced-cache-miss wording. The historical discrepancy report is retained unchanged as governance history. The resolution is a wording correction, not experiment invalidation or scope change.

## 10. Source / SHA Manifest

`phase56b_evidence_manifest.json` maps each claim to frozen sources, deterministic transformation, tool, output SHA, and the explicit statement that Level A is not altered. `phase56b_sha256.txt` is the artifact checksum list.
"""
    (OUTPUT / "PAPER_PHASE56_LEVEL_B_EVIDENCE_ADDENDUM_v1.0.md").write_text(addendum, encoding="utf-8")

    output_names = [
        "PAPER_PHASE56B_MATERIAL_DISCREPANCY_REPORT.md", "PAPER_PHASE56B_CONTROLLED_EVIDENCE_PROMOTION_REPORT.md", "PAPER_PHASE56_LEVEL_B_EVIDENCE_ADDENDUM_v1.0.md", "phase56b_v3r_task_metrics.json", "phase56b_correctness_table_source.csv", "phase56b_correctness_class_metrics.csv", "phase56b_nominal_payload.json", "phase56b_run_level_metrics.csv", "phase56b_publication_display_values.json", "phase56b_runtime_state.json", "phase56b_calibration_provenance.json",
    ]
    transformations = {
        "phase56b_v3r_task_metrics.json": "governed evaluator execution over frozen V3R predictions",
        "phase56b_correctness_table_source.csv": "selection of governed V0/V2R/V3R task metrics",
        "phase56b_correctness_class_metrics.csv": "selection of governed per-class AP50 and Recall",
        "phase56b_nominal_payload.json": "integer arithmetic over frozen shapes and implementation copy geometry",
        "phase56b_run_level_metrics.csv": "per-process descriptive statistics from frozen raw latency arrays",
        "phase56b_publication_display_values.json": "verification-only aggregation and explicit display rounding",
        "phase56b_runtime_state.json": "structured extraction from frozen environment/report provenance",
        "phase56b_calibration_provenance.json": "structured extraction and split-identity checks over frozen calibration provenance",
    }
    sources = {
        "PAPER_PHASE56B_MATERIAL_DISCREPANCY_REPORT.md": ["src/stage_q_int8_builder.cpp", "docs/personal/STAGE_Q3_FORMAL_CALIBRATION_REPORT.md", str((CAL_ROOT / "calibration_cache.meta.json").resolve())],
        "PAPER_PHASE56B_CONTROLLED_EVIDENCE_PROMOTION_REPORT.md": [f"docs/paper/phase5_6/{name}" for name in output_names[3:]],
        "PAPER_PHASE56_LEVEL_B_EVIDENCE_ADDENDUM_v1.0.md": [f"docs/paper/phase5_6/{name}" for name in output_names[3:]],
        "phase56b_v3r_task_metrics.json": [repo_path(GATE / "v3r_result.json"), repo_path(GT), "tools/validation/stage_r_v2_task_accuracy.py", "tools/validation/evaluate_stage_k_task_metrics.py"],
        "phase56b_correctness_table_source.csv": [repo_path(GATE / "v2r_task_metrics.json"), repo_path(GATE / "v3r_result.json"), repo_path(V0_RESULT)],
        "phase56b_correctness_class_metrics.csv": [repo_path(GATE / "v2r_task_metrics.json"), repo_path(GATE / "v3r_result.json"), repo_path(V0_RESULT)],
        "phase56b_nominal_payload.json": [repo_path(TEST_MANIFEST), "configs/model_contracts/yolov8n_neudet_frozen.yaml", "src/tensorrt_engine.cpp", "backend_tensorrt/cuda_preprocessor.cu", "backend_tensorrt/pageable_raw_staging.cpp", "backend_tensorrt/pinned_raw_staging.cpp"],
        "phase56b_run_level_metrics.csv": [str((RAW / "formal_runs").resolve()), "docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md"],
        "phase56b_publication_display_values.json": [str((RAW / "formal_runs").resolve()), "docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md"],
        "phase56b_runtime_state.json": [repo_path(formal_report), repo_path(preflight_env)],
        "phase56b_calibration_provenance.json": [repo_path(CAL_MANIFEST), repo_path(TRAIN_MANIFEST), repo_path(TEST_MANIFEST), "src/stage_q_int8_builder.cpp", "src/preprocessor.cpp", str((CAL_ROOT / "calibration_cache.meta.json").resolve()), str((CAL_ROOT / "engine_manifest_v2.json").resolve())],
    }
    manifest = {
        "schema_version": 1, "artifact_kind": "paper_phase56b_level_b_evidence_manifest", "starting_head": STARTING_HEAD,
        "scope": "EVIDENCE_REANALYSIS_WITHOUT_NEW_RUNS", "d01": {"status": "CLOSED", "resolution": "precise forced-cache-miss wording adopted"},
        "generator": {"path": repo_path(Path(__file__)), "sha256": sha256(Path(__file__))},
        "items": [
            {"claim": name, "frozen_sources": sources[name], "deterministic_transformation": transformations.get(name, "governance synthesis from generated machine-readable evidence"), "tool": repo_path(Path(__file__)), "output": f"docs/paper/phase5_6/{name}", "output_sha256": sha256(OUTPUT / name), "alters_level_a_authority": False}
            for name in output_names
        ],
        "prohibitions_observed": {"inference_rerun": False, "benchmark_rerun": False, "new_timing": False, "new_telemetry": False, "manuscript_mutation": False},
    }
    write_json(OUTPUT / "phase56b_evidence_manifest.json", manifest)
    checksum_paths = [REPO / "scripts/paper/derive_phase56b_evidence.py"] + [OUTPUT / name for name in output_names] + [OUTPUT / "phase56b_evidence_manifest.json"]
    lines = [f"{sha256(path)}  {repo_path(path)}" for path in checksum_paths]
    (OUTPUT / "phase56b_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("PHASE56B_DERIVATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
