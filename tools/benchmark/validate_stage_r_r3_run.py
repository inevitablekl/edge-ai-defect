#!/usr/bin/env python3
"""Validate Stage R R3 unified-harness run artifacts.

Checks per run directory:
  - Result JSON v4 parses and has the expected processed-frame count
  - sequence_index is 0..N-1 strictly increasing
  - relative_path order matches the frozen 180-image manifest (cycled N/180 times)
  - image dimensions match the manifest entries
  - run_manifest reports drop_count 0, EOS, worker join, and no CPU fallback
  - metrics.json processed_frames equals the expected measured count
  - V2/V3/V4 detection SHA identity is shared; V0 keeps its official baseline SHA

This is a harness-correctness check only; it does not re-run accuracy evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

V0_BASELINE_SHA = "12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2"
MANIFEST_PATH = Path("results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_run(run_dir: Path, variant: str, expected_frames: int,
                 manifest_paths: list[dict[str, object]]) -> dict[str, object]:
    errors: list[str] = []
    result_path = run_dir / "result.json"
    metrics_path = run_dir / "metrics.json"
    manifest_path = run_dir / "run_manifest.json"
    hashes_path = run_dir / "hashes.json"

    result = json.loads(result_path.read_text())
    if result["schema_version"] != 4:
        errors.append("result schema_version != 4")
    images = result["images"]
    if len(images) != expected_frames:
        errors.append(f"result images={len(images)} != expected {expected_frames}")
    for index, frame in enumerate(images):
        if frame["sequence_index"] != index:
            errors.append(f"frame {index}: sequence_index {frame['sequence_index']} out of order")
            break
    for index, frame in enumerate(images):
        expected = manifest_paths[index % len(manifest_paths)]
        if frame["relative_path"] != expected["image_path"]:
            errors.append(f"frame {index}: path {frame['relative_path']} != manifest {expected['image_path']}")
            break
        # Frozen corpus contract: every NEU-DET image is 200x200.
        if frame["width"] != 200 or frame["height"] != 200:
            errors.append(f"frame {index}: dimensions {frame['width']}x{frame['height']} != 200x200")
            break
        if "detections" not in frame:
            errors.append(f"frame {index}: missing detections array")
            break

    run_manifest = json.loads(manifest_path.read_text())
    if run_manifest.get("drop_count") != 0:
        errors.append(f"drop_count {run_manifest.get('drop_count')} != 0")
    if not run_manifest.get("eos"):
        errors.append("eos != true")
    if not run_manifest.get("worker_join"):
        errors.append("worker_join != true")
    if run_manifest.get("cpu_preprocessing_fallback") is not False:
        errors.append("cpu_preprocessing_fallback != false")
    if run_manifest.get("result_json_schema") != 4:
        errors.append("result_json_schema != 4")

    metrics = json.loads(metrics_path.read_text())
    if metrics["processed_frames"] != expected_frames:
        errors.append(f"metrics processed_frames={metrics['processed_frames']} != {expected_frames}")
    if metrics["drop_count"] != 0:
        errors.append(f"metrics drop_count={metrics['drop_count']} != 0")

    hashes = json.loads(hashes_path.read_text())
    if hashes.get("frames") != expected_frames:
        errors.append(f"hashes frames={hashes.get('frames')} != {expected_frames}")

    return {
        "variant": variant,
        "run_id": metrics["run_id"],
        "detection_sha256": hashes["detection_sha256"],
        "result_json_sha256": sha256(result_path),
        "summary_processed_frames": result["summary"]["processed_frames"],
        "summary_dropped_frames": result["summary"]["dropped_frames"],
        "binary_sha256": run_manifest["binary_sha256"],
        "commit": run_manifest["commit"],
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-frames", type=int, default=180)
    parser.add_argument("--v0-baseline-sha", default=V0_BASELINE_SHA)
    args = parser.parse_args()
    output = args.output_dir
    if not output.exists():
        raise SystemExit(f"validation output directory missing: {output}")

    manifest = json.loads(MANIFEST_PATH.read_text())
    entries = manifest["entries"]
    run_dirs = sorted((output / "runs").glob("set_*"))
    if not run_dirs:
        raise SystemExit("no run directories found under runs/")

    rows = []
    for run_dir in run_dirs:
        variant = run_dir.name.split("_")[2].upper()
        rows.append(validate_run(run_dir, variant, args.expected_frames, entries))

    shas = {row["variant"]: row["detection_sha256"] for row in rows}
    v2 = shas.get("V2")
    identity = all(shas.get(v) == v2 for v in ("V2", "V3", "V4"))
    v0_ok = shas.get("V0") == args.v0_baseline_sha
    summary = {
        "schema_version": 1,
        "classification": "R3_HARNESS_VALIDATION",
        "purpose": "unified harness correctness check; no accuracy evaluation",
        "expected_frames_per_run": args.expected_frames,
        "v0_baseline_sha256": args.v0_baseline_sha,
        "v2_v3_v4_detection_identity_pass": identity,
        "v0_baseline_detection_sha256_pass": v0_ok,
        "all_runs_pass": all(row["status"] == "PASS" for row in rows),
        "runs": rows,
    }
    (output / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    for row in rows:
        print(f"{row['status']} {row['variant']} detection_sha256={row['detection_sha256']}"
              f" processed={row['summary_processed_frames']} dropped={row['summary_dropped_frames']}")
        for error in row["errors"]:
            print(f"  ERROR {row['variant']}: {error}")
    print(f"V2/V3/V4 detection identity: {'PASS' if identity else 'FAIL'}")
    print(f"V0 baseline detection SHA:   {'PASS' if v0_ok else 'FAIL'}")
    print(f"overall: {'PASS' if summary['all_runs_pass'] and identity and v0_ok else 'FAIL'}")
    return 0 if summary["all_runs_pass"] and identity and v0_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
