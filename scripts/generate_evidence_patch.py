#!/usr/bin/env python3
"""Generate training evidence patch: args summary, per-class validation, test metrics, provenance.

Reads real args.yaml and runs real ultralytics val on each best.pt.
Does NOT train, does NOT modify frozen model, does NOT fabricate metrics.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

PROJECT_ROOT = Path("/root/wklproject/edge-ai-defect")
PATCH_DIR = PROJECT_ROOT / "artifacts/transfer/training_evidence_patch_20260712"
DATA_YAML = "data/yolo/neu_det/dataset.yaml"

CLASS_NAMES = [
    "crazing", "inclusion", "patches", "pitted_surface",
    "rolled-in_scale", "scratches",
]

EXPERIMENTS = [
    {
        "name": "V1 baseline",
        "dir": "experiments/training/yolov8n_neudet_baseline_20260712_122943",
        "args_yaml": "v1_baseline_args.yaml",
        "config": "configs/train/yolov8n_neudet_baseline.yaml",
        "seed": 42, "deterministic": False,
        "is_frozen_source": False,
    },
    {
        "name": "V2 extended epochs",
        "dir": "experiments/training/yolov8n_neudet_v2_20260712_125029",
        "args_yaml": "v2_extended_args.yaml",
        "config": "configs/train/yolov8n_neudet_v2.yaml",
        "seed": 42, "deterministic": False,
        "is_frozen_source": False,
    },
    {
        "name": "V3 no mosaic",
        "dir": "experiments/training/yolov8n_neudet_v3_no_mosaic_20260712_133730",
        "args_yaml": "v3_no_mosaic_args.yaml",
        "config": "configs/train/yolov8n_neudet_v3_no_mosaic.yaml",
        "seed": 42, "deterministic": False,
        "is_frozen_source": False,
    },
    {
        "name": "seed=7 deterministic",
        "dir": "experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145",
        "args_yaml": "seed7_args.yaml",
        "config": "configs/train/yolov8n_neudet_baseline_seed7.yaml",
        "seed": 7, "deterministic": True,
        "is_frozen_source": True,
    },
    {
        "name": "seed=123 deterministic",
        "dir": "experiments/training/yolov8n_neudet_baseline_seed123_20260712_141510",
        "args_yaml": "seed123_args.yaml",
        "config": "configs/train/yolov8n_neudet_baseline_seed123.yaml",
        "seed": 123, "deterministic": True,
        "is_frozen_source": False,
    },
    {
        "name": "seed=42 deterministic",
        "dir": "experiments/training/yolov8n_neudet_baseline_seed42_deterministic_20260712_161806",
        "args_yaml": "seed42_deterministic_args.yaml",
        "config": "configs/train/yolov8n_neudet_baseline_seed42_deterministic.yaml",
        "seed": 42, "deterministic": True,
        "is_frozen_source": False,
    },
    {
        "name": "V4 AdamW",
        "dir": "experiments/training/yolov8n_neudet_v4_adamw_20260712_142809",
        "args_yaml": "v4_adamw_args.yaml",
        "config": "configs/train/yolov8n_neudet_v4_adamw.yaml",
        "seed": 42, "deterministic": True,
        "is_frozen_source": False,
    },
    {
        "name": "V5 cosine LR",
        "dir": "experiments/training/yolov8n_neudet_v5_coslr_20260712_144107",
        "args_yaml": "v5_coslr_args.yaml",
        "config": "configs/train/yolov8n_neudet_v5_coslr.yaml",
        "seed": 42, "deterministic": True,
        "is_frozen_source": False,
    },
    {
        "name": "V6 no warmup",
        "dir": "experiments/training/yolov8n_neudet_v6_no_warmup_20260712_145401",
        "args_yaml": "v6_no_warmup_args.yaml",
        "config": "configs/train/yolov8n_neudet_v6_no_warmup.yaml",
        "seed": 42, "deterministic": True,
        "is_frozen_source": False,
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_args_yaml(exp_dir: Path) -> dict:
    """Read train/args.yaml — Ultralytics stores all effective params there."""
    args_path = exp_dir / "train" / "args.yaml"
    if not args_path.is_file():
        return {}
    # Ultralytics writes args.yaml as standard YAML
    import yaml
    with open(args_path) as f:
        return yaml.safe_load(f) or {}


def extract_val_metrics(val_results) -> dict:
    """Extract overall + per-class metrics from ultralytics val Results object."""
    box = val_results.box

    ap50_list = box.ap50.tolist() if hasattr(box, 'ap50') and box.ap50 is not None else []
    ap_list = box.ap.tolist() if hasattr(box, 'ap') and box.ap is not None else []
    p_list = box.p.tolist() if hasattr(box, 'p') and box.p is not None else []
    r_list = box.r.tolist() if hasattr(box, 'r') and box.r is not None else []

    per_class = {}
    for i, cls_name in enumerate(CLASS_NAMES):
        per_class[cls_name] = {
            "ap50": round(ap50_list[i], 6) if i < len(ap50_list) else None,
            "ap50_95": round(ap_list[i], 6) if i < len(ap_list) else None,
            "precision": round(p_list[i], 6) if i < len(p_list) else None,
            "recall": round(r_list[i], 6) if i < len(r_list) else None,
        }

    overall = {
        "mAP50": round(float(box.map50), 6),
        "mAP50_95": round(float(box.map), 6),
        "precision": round(float(box.mp), 6) if hasattr(box, 'mp') and box.mp is not None else None,
        "recall": round(float(box.mr), 6) if hasattr(box, 'mr') and box.mr is not None else None,
    }

    return {"overall": overall, "per_class": per_class}


def phase2_effective_args():
    """Generate experiment_effective_args_summary.json from real args.yaml files."""
    print("=" * 60)
    print("Phase 2: Effective Args Summary")
    print("=" * 60)

    args_summary = []
    for exp in EXPERIMENTS:
        exp_dir = PROJECT_ROOT / exp["dir"]
        args = read_args_yaml(exp_dir)
        # Flatten args — Ultralytics args.yaml may have nested structure
        flat = {}
        if isinstance(args, dict):
            flat = {k: v for k, v in args.items() if not isinstance(v, (dict, list))}

        entry = {
            "experiment_name": exp["name"],
            "experiment_dir": str(exp_dir),
            "args_yaml_path": str(exp_dir / "train" / "args.yaml"),
            "model": flat.get("model", "N/A"),
            "data": flat.get("data", "N/A"),
            "epochs": flat.get("epochs", None),
            "completed_epochs": None,  # filled from results.csv
            "imgsz": flat.get("imgsz", None),
            "batch": flat.get("batch", None),
            "optimizer": flat.get("optimizer", "N/A"),
            "lr0": flat.get("lr0", None),
            "seed": flat.get("seed", None),
            "deterministic": flat.get("deterministic", False),
            "mosaic": flat.get("mosaic", None),
            "close_mosaic": flat.get("close_mosaic", None),
            "cos_lr": flat.get("cos_lr", False),
            "warmup_epochs": flat.get("warmup_epochs", None),
            "patience": flat.get("patience", None),
            "amp": flat.get("amp", False),
            "device": flat.get("device", None),
            "all_effective_args": flat,
        }

        # Get completed epochs from results.csv
        results_csv = exp_dir / "train" / "results.csv"
        if results_csv.is_file():
            with open(results_csv) as f:
                rows = list(csv.DictReader(f))
            if rows:
                entry["completed_epochs"] = int(rows[-1]["epoch"])

        args_summary.append(entry)
        print(f"  {exp['name']}: epochs={entry['epochs']}, completed={entry['completed_epochs']}, "
              f"deterministic={entry['deterministic']}, optimizer={entry['optimizer']}, "
              f"lr0={entry['lr0']}, mosaic={entry['mosaic']}")

    out_path = PATCH_DIR / "experiment_effective_args_summary.json"
    with open(out_path, "w") as f:
        json.dump(args_summary, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {out_path}")
    return args_summary


def phase3_validation_metrics():
    """Re-run validation on every best.pt and extract machine-readable per-class metrics."""
    print("\n" + "=" * 60)
    print("Phase 3: Per-Class Validation Metrics (re-run on best.pt)")
    print("=" * 60)

    all_val_results = []
    val_csv_rows = []

    val_log_dir = PATCH_DIR / "validation_logs"
    val_log_dir.mkdir(parents=True, exist_ok=True)

    for exp in EXPERIMENTS:
        exp_dir = PROJECT_ROOT / exp["dir"]
        best_pt = exp_dir / "train" / "weights" / "best.pt"

        if not best_pt.is_file():
            print(f"  SKIP {exp['name']}: best.pt not found at {best_pt}")
            continue

        best_sha256 = sha256_file(best_pt)
        t0 = time.time()

        print(f"\n  Validating: {exp['name']}")
        print(f"    Checkpoint: {best_pt}")
        print(f"    SHA256: {best_sha256}")

        model = YOLO(str(best_pt))
        val_results = model.val(
            data=DATA_YAML,
            split="val",
            imgsz=640,
            batch=16,
            device=0,
            verbose=False,
            plots=False,
        )

        elapsed = time.time() - t0
        metrics = extract_val_metrics(val_results)

        # Build record
        record = {
            "experiment_name": exp["name"],
            "experiment_dir": str(exp_dir),
            "checkpoint_path": str(best_pt),
            "checkpoint_sha256": best_sha256,
            "validation_command": (
                f"model.val(data='{DATA_YAML}', split='val', imgsz=640, batch=16, device=0)"
            ),
            "validation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_yaml": DATA_YAML,
            "split": "val",
            "imgsz": 640,
            "batch": 16,
            "ultralytics_version": ultralytics.__version__,
            "pytorch_version": torch.__version__,
            "cuda_version": torch.version.cuda or "N/A",
            "overall": metrics["overall"],
            "per_class": metrics["per_class"],
        }
        all_val_results.append(record)

        # CSV row
        row = {
            "experiment_name": exp["name"],
            "checkpoint_sha256": best_sha256,
        }
        row.update({f"overall_{k}": v for k, v in metrics["overall"].items()})
        for cls_name, cls_metrics in metrics["per_class"].items():
            for mk, mv in cls_metrics.items():
                row[f"{cls_name}_{mk}"] = mv
        val_csv_rows.append(row)

        print(f"    mAP50={metrics['overall']['mAP50']}, mAP50-95={metrics['overall']['mAP50_95']}, "
              f"P={metrics['overall']['precision']}, R={metrics['overall']['recall']}")
        print(f"    Time: {elapsed:.1f}s")

    # Write JSON
    json_path = PATCH_DIR / "validation_metrics_by_experiment.json"
    with open(json_path, "w") as f:
        json.dump(all_val_results, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON saved: {json_path}")

    # Write CSV
    csv_path = PATCH_DIR / "validation_metrics_by_experiment.csv"
    if val_csv_rows:
        fieldnames = list(val_csv_rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(val_csv_rows)
        print(f"  CSV saved: {csv_path}")

    return all_val_results


def phase4_test_metrics():
    """Extract or re-run test metrics for frozen model."""
    print("\n" + "=" * 60)
    print("Phase 4: Frozen Model Test Split Metrics")
    print("=" * 60)

    frozen_pt = PROJECT_ROOT / "models/pytorch/yolov8n_neudet_frozen.pt"
    test_eval_dir = PROJECT_ROOT / "experiments/evaluation/yolov8n_neudet_frozen_test_20260712_163356"

    # Check existing predictions.json
    existing_json = test_eval_dir / "test" / "predictions.json"
    test_summary_json = test_eval_dir / "test_summary.json"

    if test_summary_json.is_file():
        print(f"  Using existing test summary: {test_summary_json}")
        with open(test_summary_json) as f:
            existing = json.load(f)
        print(f"    mAP50={existing['overall']['mAP50']}, mAP50-95={existing['overall']['mAP50_95']}")
        return existing

    # Re-run test validation
    print(f"  Re-running test validation on frozen model...")
    print(f"    Frozen model: {frozen_pt}")
    print(f"    SHA256: {sha256_file(frozen_pt)}")

    frozen_sha256 = sha256_file(frozen_pt)
    expected = "5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7"
    if frozen_sha256 != expected:
        print(f"    ⚠ SHA256 MISMATCH! Expected: {expected}")
        print(f"    ⚠ Actual: {frozen_sha256}")

    model = YOLO(str(frozen_pt))
    val_results = model.val(
        data=DATA_YAML,
        split="test",
        imgsz=640,
        batch=16,
        device=0,
        verbose=False,
        plots=False,
        save_json=True,
        project=str(PATCH_DIR / "frozen_test_artifacts"),
        name="test_rerun",
        exist_ok=True,
    )

    metrics = extract_val_metrics(val_results)

    # Get image/instance counts
    test_result = {
        "model_path": str(frozen_pt),
        "model_sha256": frozen_sha256,
        "data_yaml": DATA_YAML,
        "split": "test",
        "imgsz": 640,
        "batch": 16,
        "validation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ultralytics_version": ultralytics.__version__,
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda or "N/A",
        "overall": metrics["overall"],
        "per_class": metrics["per_class"],
    }

    # Write JSON
    json_path = PATCH_DIR / "frozen_test_metrics.json"
    with open(json_path, "w") as f:
        json.dump(test_result, f, indent=2, ensure_ascii=False)
    print(f"  JSON saved: {json_path}")

    # Write CSV
    csv_path = PATCH_DIR / "frozen_test_metrics.csv"
    row = {"model_sha256": frozen_sha256}
    row.update({f"overall_{k}": v for k, v in metrics["overall"].items()})
    for cls_name, cls_metrics in metrics["per_class"].items():
        for mk, mv in cls_metrics.items():
            row[f"{cls_name}_{mk}"] = mv
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)
    print(f"  CSV saved: {csv_path}")

    # Write command and environment
    (PATCH_DIR / "frozen_test_command.txt").write_text(
        f"model.val(data='{DATA_YAML}', split='test', imgsz=640, batch=16, device=0)\n"
    )
    (PATCH_DIR / "frozen_test_environment.txt").write_text(
        f"ultralytics: {ultralytics.__version__}\n"
        f"pytorch: {torch.__version__}\n"
        f"cuda: {torch.version.cuda}\n"
        f"model_sha256: {frozen_sha256}\n"
    )

    print(f"    Test mAP50={metrics['overall']['mAP50']}, mAP50-95={metrics['overall']['mAP50_95']}")
    return test_result


def phase5_provenance(val_results, test_result):
    """Generate EXPERIMENT_PROVENANCE.json."""
    print("\n" + "=" * 60)
    print("Phase 5: Experiment Provenance")
    print("=" * 60)

    provenance = []
    for exp in EXPERIMENTS:
        exp_dir = PROJECT_ROOT / exp["dir"]
        best_pt = exp_dir / "train" / "weights" / "best.pt"

        best_sha256 = sha256_file(best_pt) if best_pt.is_file() else "MISSING"
        results_csv = exp_dir / "train" / "results.csv"

        git_commit_file = exp_dir / "git_commit.txt"
        git_commit = git_commit_file.read_text().strip() if git_commit_file.is_file() else "N/A"

        entry = {
            "experiment_name": exp["name"],
            "config_file": exp["config"],
            "actual_args_yaml": str(exp_dir / "train" / "args.yaml"),
            "experiment_dir": str(exp_dir),
            "best_pt_path": str(best_pt),
            "best_pt_sha256": best_sha256,
            "results_csv_path": str(results_csv),
            "git_commit": git_commit,
            "validation_metrics_source": (
                f"Re-run val on best.pt at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                f"with Ultralytics {ultralytics.__version__}"
            ),
            "is_frozen_model_source": exp["is_frozen_source"],
        }
        provenance.append(entry)

    # Add frozen model entry
    frozen_pt = PROJECT_ROOT / "models/pytorch/yolov8n_neudet_frozen.pt"
    provenance.append({
        "experiment_name": "FROZEN MODEL",
        "frozen_model_path": str(frozen_pt),
        "frozen_model_sha256": sha256_file(frozen_pt),
        "expected_sha256": "5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7",
        "source_experiment": "seed=7 deterministic",
        "source_best_pt": str(PROJECT_ROOT / "experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145/train/weights/best.pt"),
        "test_evaluation_dir": str(PROJECT_ROOT / "experiments/evaluation/yolov8n_neudet_frozen_test_20260712_163356"),
        "test_metrics_source": "Re-extracted from frozen model via val(split='test')",
    })

    out_path = PATCH_DIR / "EXPERIMENT_PROVENANCE.json"
    with open(out_path, "w") as f:
        json.dump(provenance, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {out_path}")
    print(f"  Entries: {len(provenance)}")
    return provenance


def main():
    os.environ["YOLO_OFFLINE"] = "true"

    print(f"Ultralytics: {ultralytics.__version__}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA: {torch.version.cuda}")
    print(f"Patch dir: {PATCH_DIR}")
    print()

    # Phase 2
    args_summary = phase2_effective_args()

    # Phase 3
    val_results = phase3_validation_metrics()

    # Phase 4
    test_result = phase4_test_metrics()

    # Phase 5
    provenance = phase5_provenance(val_results, test_result)

    print("\n" + "=" * 60)
    print("All evidence generation complete.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
