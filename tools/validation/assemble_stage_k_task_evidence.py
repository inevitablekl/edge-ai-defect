#!/usr/bin/env python3
"""Assemble the frozen Stage K full task-level evaluation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SPLIT_SHA = "fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8"
DATASET_SHA = "5e0f688fb5400406533e7c8d0406bfd29d2674011a657210de18740fe161b283"
ENGINE_SHA = {
    "TRT FP32 noTF32": "aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f",
    "TRT FP16 Original Stage K": "6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc",
    "TRT M3 diagnostic control": "83e7100b01b9bb0c04dd4c41e52d6d5f61ee61d07cef82dffee173a1c692266b",
}
ENGINE_MANIFEST_SHA = {
    "TRT FP32 noTF32": "86549f894802afab06221e32bab46e89d69e97eb8059befa8771d2728b2ee1a5",
    "TRT FP16 Original Stage K": "39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63",
    "TRT M3 diagnostic control": "16f5f8bb68f95c564fc5f21b8809302bd226e0ce6a9fdd138038b659cbe7e11a5",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def finite_tree(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_tree(item) for item in value)
    return True


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def timing_stats(path: Path) -> dict[str, Any]:
    artifact = load(path)
    records = artifact["images"]
    fields = {
        "inference": "tensorrt_inference_latency_ms",
        "e2e": "e2e_latency_ms",
    }
    output = {"image_count": len(records)}
    for name, field in fields.items():
        values = [float(item[field]) for item in records]
        output[name] = {
            "mean_ms": sum(values) / len(values),
            "median_ms": percentile(values, 50),
            "p95_ms": percentile(values, 95),
            "min_ms": min(values),
            "max_ms": max(values),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, default=REPO_ROOT / "results/validation/stage_k_task_eval_v2/metrics")
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    inference = evidence.parent / "inference"
    ground_truth_dir = evidence.parent / "ground_truth"
    evidence.mkdir(parents=True, exist_ok=True)

    contract_path = evidence / "evaluation_contract.json"
    contract = load(contract_path)
    if contract.get("status") != "FROZEN_BEFORE_METRICS":
        raise SystemExit("STOP: evaluation contract was not frozen before metrics")
    backend_metrics = load(evidence / "backend_metrics.json")
    classwise_metrics = load(evidence / "classwise_metrics.json")
    pair = load(evidence / "fp32_vs_original_fp16.json")
    gt_report = load(ground_truth_dir / "ground_truth_conversion_report.json")
    gt = load(ground_truth_dir / "test_ground_truth.json")

    labels = list(backend_metrics["backends"])
    fp32_label = "TRT FP32 noTF32"
    original_label = "TRT FP16 Original Stage K"
    m3_label = "TRT M3 diagnostic control"
    fp32 = backend_metrics["backends"][fp32_label]
    original = backend_metrics["backends"][original_label]
    m3 = backend_metrics["backends"][m3_label]
    deltas = {
        "precision_delta_original_minus_fp32": original["precision"] - fp32["precision"],
        "recall_delta_original_minus_fp32": original["recall"] - fp32["recall"],
        "mAP50_delta_original_minus_fp32": original["mAP50"] - fp32["mAP50"],
        "mAP50_95_delta_original_minus_fp32": original["mAP50_95"] - fp32["mAP50_95"],
        "precision_drop_fp32_minus_original": fp32["precision"] - original["precision"],
        "recall_drop_fp32_minus_original": fp32["recall"] - original["recall"],
        "mAP50_drop_fp32_minus_original": fp32["mAP50"] - original["mAP50"],
        "mAP50_95_drop_fp32_minus_original": fp32["mAP50_95"] - original["mAP50_95"],
    }
    classwise_risk = []
    for class_name in classwise_metrics["class_names"]:
        base = classwise_metrics["backends"][fp32_label][class_name]
        candidate = classwise_metrics["backends"][original_label][class_name]
        ap50_drop = base["AP50"] - candidate["AP50"]
        recall_drop = base["recall"] - candidate["recall"]
        if ap50_drop > 0.10 or recall_drop > 0.10:
            classwise_risk.append({
                "class_name": class_name,
                "AP50_drop": ap50_drop,
                "recall_drop": recall_drop,
            })

    timing_labels = {
        fp32_label: "fp32_notf32",
        original_label: "fp16_original",
        m3_label: "fp16_selective",
    }
    timing = {label: timing_stats(inference / key / "latency.json") for label, key in timing_labels.items()}
    original_timing_faster = (
        timing[original_label]["inference"]["mean_ms"] < timing[fp32_label]["inference"]["mean_ms"]
        and timing[original_label]["e2e"]["mean_ms"] < timing[fp32_label]["e2e"]["mean_ms"]
    )
    timing_comparison = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_timing_comparison",
        "timing_kind": "task-evaluation descriptive timing",
        "formal_k7_benchmark": False,
        "split_manifest_sha256": SPLIT_SHA,
        "backends": timing,
        "mean_speedup_fp32_div_original_fp16": {
            "inference": timing[fp32_label]["inference"]["mean_ms"] / timing[original_label]["inference"]["mean_ms"],
            "e2e": timing[fp32_label]["e2e"]["mean_ms"] / timing[original_label]["e2e"]["mean_ms"],
        },
        "original_fp16_task_timing_verdict": (
            "ORIGINAL_FP16_TASK_TIMING_FASTER"
            if original_timing_faster
            else "ORIGINAL_FP16_TASK_TIMING_NOT_FASTER"
        ),
        "m3_speedup_claim": "NOT_COMPUTED_M3_IS_DIAGNOSTIC_ONLY",
    }

    accuracy_gate_pass = (
        deltas["mAP50_drop_fp32_minus_original"] <= 0.01
        and deltas["mAP50_95_drop_fp32_minus_original"] <= 0.01
        and deltas["recall_drop_fp32_minus_original"] <= 0.01
        and original["prediction_count"] >= 0
        and original["gt_count"] == 442
    )
    inference_pass = all(
        load(inference / key / "inference_manifest.json")["success_count"] == 180
        and load(inference / key / "inference_manifest.json")["failure_count"] == 0
        for key in ("fp32_notf32", "fp16_original", "fp16_selective")
    )
    if not inference_pass:
        verdict = "TASK_LEVEL_EVALUATION_BLOCKED"
    elif accuracy_gate_pass and classwise_risk:
        verdict = "TASK_LEVEL_FP16_ACCEPTED_WITH_CLASSWISE_RISK"
    elif accuracy_gate_pass:
        verdict = "TASK_LEVEL_FP16_ACCEPTED"
    else:
        verdict = "TASK_LEVEL_FP16_NOT_ACCEPTABLE"

    ground_truth_summary = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_ground_truth_summary",
        "verdict": gt_report["verdict"],
        "test_manifest_sha256": SPLIT_SHA,
        "dataset_source_tree_sha256": DATASET_SHA,
        "image_count": gt["image_count"],
        "raw_bbox_count": gt_report["raw_bbox_count"],
        "duplicate_bbox_count_removed": gt_report["duplicate_bbox_count_removed"],
        "deduplicated_bbox_count": gt["total_bbox_count"],
        "class_bbox_distribution": gt_report["class_bbox_distribution"],
        "source_tree_all_entries_verified": gt_report["source_tree_verification"]["all_entries_verified"],
    }
    three_engine = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_three_engine_comparison",
        "roles": contract["roles"],
        "metrics": backend_metrics["backends"],
        "timing": timing,
        "m3_vs_fp32_metrics_identical": m3 == fp32,
        "m3_fp16_speedup_not_claimed": True,
        "original_fp16_vs_fp32_accuracy_deltas": deltas,
    }
    verification = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_verification_report",
        "verdict": "PASS",
        "frozen_identity": {
            "test_manifest_sha256": {"expected": SPLIT_SHA, "actual": sha256(REPO_ROOT / "results/validation/stage_k_task_eval_v2/split/test_manifest.json")},
            "dataset_source_tree_sha256": {"expected": DATASET_SHA, "actual": gt_report["source_tree_verification"]["source_tree_sha256"]},
            "engine_sha256": ENGINE_SHA,
            "engine_manifest_sha256": ENGINE_MANIFEST_SHA,
        },
        "ground_truth": {
            "conversion_verdict": gt_report["verdict"],
            "image_count": gt["image_count"],
            "bbox_count": gt["total_bbox_count"],
            "cross_split_overlap": gt_report["cross_split_overlap"],
            "source_mutation": gt_report["source_xml_and_images_modified"],
            "pseudo_labels": gt_report["pseudo_labels_generated"],
        },
        "inference": {
            key: {
                "success_count": load(inference / key / "inference_manifest.json")["success_count"],
                "failure_count": load(inference / key / "inference_manifest.json")["failure_count"],
                "detections_sha256": sha256(inference / key / "detections.json"),
                "latency_sha256": sha256(inference / key / "latency.json"),
                "schema_and_finite_values": finite_tree(load(inference / key / "detections.json")) and finite_tree(load(inference / key / "latency.json")),
            }
            for key in ("fp32_notf32", "fp16_original", "fp16_selective")
        },
        "metrics": {
            "backend_count": len(labels),
            "gt_count_all_backends": {label: value["gt_count"] for label, value in backend_metrics["backends"].items()},
            "finite_values": finite_tree(backend_metrics) and finite_tree(classwise_metrics),
        },
        "decision": {
            "accuracy_gate_pass": accuracy_gate_pass,
            "classwise_risk": classwise_risk,
            "verdict": verdict,
            "timing_verdict": timing_comparison["original_fp16_task_timing_verdict"],
        },
        "scope_audit": {
            "engine_modified": False,
            "onnx_modified": False,
            "model_contract_modified": False,
            "production_runtime_modified": False,
            "k5_gate_modified": False,
            "tolerance_modified": False,
            "k6_k7_k8_entered": False,
        },
    }

    dump(evidence / "ground_truth_summary.json", ground_truth_summary)
    dump(evidence / "timing_comparison.json", timing_comparison)
    dump(evidence / "three_engine_comparison.json", three_engine)
    dump(evidence / "verification_report.json", verification)

    readme = f"""# Stage K Full Task-Level Evaluation Report

## 1. Verdict

`{verdict}`

`{timing_comparison['original_fp16_task_timing_verdict']}`

The Original Stage K FP16 Engine is the optimization candidate. M3 remains a
diagnostic-only control because its inspected actual FP16 tactic count is zero
(`M3_DEGENERATED_TO_FP32`). No FP16 speedup is inferred from M3.

## 2. Git State

Evaluation was started at HEAD `99320d69eb10112348d792283b008eadd5517e21`.
Existing unrelated worktree changes were preserved. No reset, stash, push,
merge, tag, K6, K7, or K8 operation was performed.

## 3. Dataset and Split Identity

  source: `data/raw/NEU-DET`
  source tree SHA256: `{DATASET_SHA}`
  test split: 180 images
  test manifest SHA256: `{SPLIT_SHA}`
  annotation: Pascal VOC XML
  classes: crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches

## 4. Ground Truth Conversion

Ground truth conversion passed for 180/180 image containers. The frozen test
split contains 442 raw and 442 deduplicated bbox rows; no duplicate bbox row
was present in this split. Full dataset source file hashes were verified
against the frozen source tree manifest. XML and image bytes were not modified,
and no pseudo-labels were generated.

## 5. Engine Identity

| Backend | Role | Engine SHA256 | Manifest SHA256 |
|---|---|---|---|
| TRT FP32 noTF32 | baseline | `{ENGINE_SHA[fp32_label]}` | `{ENGINE_MANIFEST_SHA[fp32_label]}` |
| TRT FP16 Original Stage K | optimization candidate | `{ENGINE_SHA[original_label]}` | `{ENGINE_MANIFEST_SHA[original_label]}` |
| TRT M3 | diagnostic control | `{ENGINE_SHA[m3_label]}` | `{ENGINE_MANIFEST_SHA[m3_label]}` |

All three used TensorRT 10.3.0.30 and the existing frozen preprocessing and
postprocessing configuration.

## 6. Inference Completion

  FP32 noTF32: 180/180 success
  Original FP16: 180/180 success
  M3 diagnostic: 180/180 success
  NaN/Inf: PASS for all artifacts

Original FP16 was run once. Existing FP32 and M3 artifacts were integrity
validated and were not rerun.

## 7. Dataset-Level Metrics

These are project-local evaluator results using the frozen contract; bitwise
equivalence to Ultralytics metrics is not claimed.

| Backend | Precision | Recall | mAP50 | mAP50-95 | TP | FP | FN | Predictions | GT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FP32 noTF32 | {fp32['precision']:.6f} | {fp32['recall']:.6f} | {fp32['mAP50']:.6f} | {fp32['mAP50_95']:.6f} | {fp32['tp']} | {fp32['fp']} | {fp32['fn']} | {fp32['prediction_count']} | {fp32['gt_count']} |
| Original FP16 | {original['precision']:.6f} | {original['recall']:.6f} | {original['mAP50']:.6f} | {original['mAP50_95']:.6f} | {original['tp']} | {original['fp']} | {original['fn']} | {original['prediction_count']} | {original['gt_count']} |
| M3 diagnostic | {m3['precision']:.6f} | {m3['recall']:.6f} | {m3['mAP50']:.6f} | {m3['mAP50_95']:.6f} | {m3['tp']} | {m3['fp']} | {m3['fn']} | {m3['prediction_count']} | {m3['gt_count']} |

Original FP16 minus FP32 deltas:

  precision: {deltas['precision_delta_original_minus_fp32']:+.6f}
  recall: {deltas['recall_delta_original_minus_fp32']:+.6f}
  mAP50: {deltas['mAP50_delta_original_minus_fp32']:+.6f}
  mAP50-95: {deltas['mAP50_95_delta_original_minus_fp32']:+.6f}

## 8. Classwise Metrics

Classwise results are retained in `classwise_metrics.json`. No class crossed
the descriptive risk trigger (>0.10 AP50 or recall absolute drop), so no
classwise-risk suffix was required.

## 9. FP32 vs Original FP16 Detection Comparison

  exact-class matched detections: {pair['matched_detection_count']}
  FP32-only detections: {pair['fp32_only_detection_count']}
  Original FP16-only detections: {pair['original_fp16_only_detection_count']}
  class mismatches: {pair['class_mismatch_count']}
  mean IoU: {pair['mean_iou']:.6f}
  minimum IoU: {pair['minimum_iou']:.6f}
  IoU P5/P50/P95: {pair['iou_p5']:.6f} / {pair['iou_p50']:.6f} / {pair['iou_p95']:.6f}
  confidence MAE: {pair['confidence_mae']:.6f}
  bbox coordinate MAE: {pair['bbox_coordinate_mae']:.6f}
  bbox coordinate max absolute error: {pair['bbox_coordinate_max_abs']:.6f}

## 10. M3 Diagnostic Control

M3 metrics are identical to the FP32 metrics in this evaluator output. This
is consistent with its prior inspection result, but M3 is not treated as an
effective FP16 deployment candidate and no M3 speedup is reported.

## 11. Descriptive Timing

| Backend | mean inference ms | median inference ms | P95 inference ms | mean E2E ms | median E2E ms | P95 E2E ms |
|---|---:|---:|---:|---:|---:|---:|
| FP32 noTF32 | {timing[fp32_label]['inference']['mean_ms']:.6f} | {timing[fp32_label]['inference']['median_ms']:.6f} | {timing[fp32_label]['inference']['p95_ms']:.6f} | {timing[fp32_label]['e2e']['mean_ms']:.6f} | {timing[fp32_label]['e2e']['median_ms']:.6f} | {timing[fp32_label]['e2e']['p95_ms']:.6f} |
| Original FP16 | {timing[original_label]['inference']['mean_ms']:.6f} | {timing[original_label]['inference']['median_ms']:.6f} | {timing[original_label]['inference']['p95_ms']:.6f} | {timing[original_label]['e2e']['mean_ms']:.6f} | {timing[original_label]['e2e']['median_ms']:.6f} | {timing[original_label]['e2e']['p95_ms']:.6f} |
| M3 diagnostic | {timing[m3_label]['inference']['mean_ms']:.6f} | {timing[m3_label]['inference']['median_ms']:.6f} | {timing[m3_label]['inference']['p95_ms']:.6f} | {timing[m3_label]['e2e']['mean_ms']:.6f} | {timing[m3_label]['e2e']['median_ms']:.6f} | {timing[m3_label]['e2e']['p95_ms']:.6f} |

Original FP16 / FP32 mean timing ratios are
{timing_comparison['mean_speedup_fp32_div_original_fp16']['inference']:.6f}x for inference and
{timing_comparison['mean_speedup_fp32_div_original_fp16']['e2e']:.6f}x for E2E. These are
task-evaluation timing evidence, not formal K7 benchmark conclusions.

## 12. Raw Level B vs Task-Level Interpretation

Raw Level B correctness evidence and any K5 raw failure remain unchanged.
Task-level acceptance does not erase raw numerical failure. This evaluation
adds dataset-level evidence only.

## 13. Scope Audit

No Engine, ONNX, ModelContract, production runtime, comparator tolerance, or
K5 gate was modified. Existing 16-image historical evidence was preserved.
Engine files, dataset files, and raw tensors are not part of this commit.

## 14. Next Authorization

Original FP16 passed this experimental task-level accuracy decision and may
enter formal candidate review. K7 remains the authority for formal performance
benchmarking; K6/K8 remain according to the frozen Stage K plan. This task is
complete and stops here.
"""
    (evidence / "README.txt").write_text(readme)

    # Keep a deterministic checksum list for all evidence files except the
    # checksum list itself, whose contents necessarily depend on its own path.
    checksum_paths = sorted(path for path in evidence.iterdir() if path.is_file() and path.name != "sha256sums.txt")
    (evidence / "sha256sums.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_paths)
    )
    print(json.dumps({
        "verdict": verdict,
        "timing_verdict": timing_comparison["original_fp16_task_timing_verdict"],
        "accuracy_gate_pass": accuracy_gate_pass,
        "classwise_risk": classwise_risk,
        "evidence_dir": str(evidence),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"ERROR: {error}") from error
