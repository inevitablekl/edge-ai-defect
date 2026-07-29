#!/usr/bin/env python3
"""Run the frozen Stage K Original TensorRT FP16 engine for K6 stability.

The existing task-level C++ runner is deliberately reused.  It performs one
serial directory pass per subprocess, so the validation workload has one
inference process at a time, batch=1, and no pipeline concurrency.  Each pass
contains the complete frozen 180-image test split.  This tool only orchestrates
the run and writes validation evidence; it does not build or modify an engine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPLIT = REPO_ROOT / "results/validation/stage_k_task_eval_v2/split/test_manifest.json"
DEFAULT_ENGINE = Path(
    "/home/orin/edge-ai-local-models/stage_k/"
    "yolov8n_neudet_trt10.3_fp16_b1_640.engine"
)
DEFAULT_ENGINE_MANIFEST = REPO_ROOT / "models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json"
DEFAULT_RUNNER = Path(
    "/home/orin/edge-ai-local-build/k5_correctness_v1/c54020c_release/"
    "task_level_profile_runner"
)
DEFAULT_OUTPUT = REPO_ROOT / "results/validation/stage_k6/stability_v1"
EXPECTED_SPLIT_SHA256 = "fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8"
EXPECTED_BACKEND = "tensorrt_fp16"
EXPECTED_IMAGE_COUNT = 180


class StabilityError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_timestamp(value: dt.datetime) -> str:
    return value.isoformat(timespec="milliseconds")


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def run_text(command: list[str], *, timeout: float = 10.0) -> dict[str, Any]:
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout, check=False)
        return {"command": command, "returncode": result.returncode,
                "output": result.stdout.strip()}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": command, "returncode": None, "output": str(error)}


def load_protocol(split_path: Path, engine_path: Path, manifest_path: Path,
                  runner_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if sha256_file(split_path) != EXPECTED_SPLIT_SHA256:
        raise StabilityError("frozen test manifest SHA256 mismatch")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    entries = split.get("entries")
    if split.get("split") != "test" or not isinstance(entries, list) or len(entries) != EXPECTED_IMAGE_COUNT:
        raise StabilityError("frozen test manifest is not the required 180-image test split")
    if not engine_path.is_file() or not manifest_path.is_file() or not runner_path.is_file():
        raise StabilityError("engine, manifest, or runner is unavailable")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    engine_sha = sha256_file(engine_path)
    manifest_sha = sha256_file(manifest_path)
    if manifest.get("engine_sha256") != engine_sha:
        raise StabilityError("Original FP16 Engine SHA256 does not match its manifest")
    if manifest.get("batch") != 1 or manifest.get("dynamic_shapes") is not False:
        raise StabilityError("engine manifest does not describe static batch=1")
    if manifest.get("precision_mode") != "FP32+FP16 mixed precision":
        raise StabilityError("engine manifest is not the Original mixed-precision FP16 candidate")

    protocol = {
        "split_manifest_sha256": EXPECTED_SPLIT_SHA256,
        "split_entry_count": len(entries),
        "engine_sha256": engine_sha,
        "engine_manifest_sha256": manifest_sha,
        "runner_sha256": sha256_file(runner_path),
        "engine_path": str(engine_path),
        "engine_manifest_path": str(manifest_path),
        "runner_path": str(runner_path),
        "batch": 1,
        "runtime_mode": "serial",
        "threading": "single inference process at a time; OpenCV threads=1",
    }
    return split, manifest, protocol


def make_runtime_config(engine_path: Path, engine_manifest: Path, input_dir: Path,
                        output_json: Path) -> str:
    contract = REPO_ROOT / "configs/model_contracts/yolov8n_neudet_frozen.yaml"
    return f"""schema_version: 3
backend:
  type: tensorrt_fp16
tensorrt:
  engine_path: {engine_path}
  engine_manifest_path: {engine_manifest}
  device_id: 0
runtime:
  opencv_num_threads: 1
model:
  contract_path: {contract}
input:
  type: directory
  directory: {input_dir}
output:
  json_path: {output_json}
  console: false
  overwrite: true
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680.0
  agnostic: false
"""


def prepare_input_directory(root: Path, split: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dataset_root = Path(split["dataset_root"])
    if not dataset_root.is_absolute():
        dataset_root = REPO_ROOT / dataset_root
    if not dataset_root.is_dir():
        raise StabilityError(f"dataset root is unavailable: {dataset_root}")
    root.mkdir(parents=True, exist_ok=False)
    by_filename: dict[str, dict[str, Any]] = {}
    for entry in split["entries"]:
        source = dataset_root / entry["image_path"]
        if not source.is_file() or sha256_file(source) != entry["image_sha256"]:
            raise StabilityError(f"test image is unavailable or changed: {source}")
        destination = root / Path(entry["image_path"]).name
        if destination.name in by_filename:
            raise StabilityError(f"duplicate input basename: {destination.name}")
        os.link(source, destination)
        by_filename[destination.name] = entry
    if len(by_filename) != EXPECTED_IMAGE_COUNT:
        raise StabilityError("prepared input directory does not contain 180 images")
    return by_filename


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "mean_ms": None, "median_ms": None, "p95_ms": None, "max_ms": None}
    return {"count": len(values), "mean_ms": statistics.fmean(values),
            "median_ms": statistics.median(values), "p95_ms": percentile(values, 0.95),
            "max_ms": max(values)}


def parse_result(raw_path: Path, expected: dict[str, dict[str, Any]], cycle_id: int,
                 iteration_base: int, cycle_start: dt.datetime) -> tuple[list[dict[str, Any]], bool, str | None]:
    try:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        images = raw.get("images")
        if not isinstance(images, list) or len(images) != EXPECTED_IMAGE_COUNT:
            return [], False, "runner output does not contain 180 images"
        seen: set[str] = set()
        records: list[dict[str, Any]] = []
        elapsed_ms = 0.0
        for offset, item in enumerate(images):
            filename = Path(str(item.get("relative_path", ""))).name
            if filename not in expected or filename in seen:
                return [], False, f"runner output image set is invalid at offset {offset}"
            seen.add(filename)
            timing = item.get("timing_ms")
            detections = item.get("detections")
            if not isinstance(timing, dict) or not isinstance(detections, list):
                return [], False, f"missing timing or detection list for {filename}"
            inference_ms = timing.get("inference")
            e2e_ms = timing.get("pre_sink_total")
            timing_finite = finite(inference_ms) and finite(e2e_ms) and float(inference_ms) >= 0 and float(e2e_ms) >= 0
            detections_finite = True
            for detection in detections:
                values = [detection.get(key) for key in ("x1", "y1", "x2", "y2", "confidence")]
                detections_finite = detections_finite and all(finite(value) for value in values)
                detections_finite = detections_finite and isinstance(detection.get("class_id"), int)
            finite_check = timing_finite and detections_finite
            if timing_finite:
                inference_float = float(inference_ms)
                e2e_float = float(e2e_ms)
                timestamp = cycle_start + dt.timedelta(milliseconds=elapsed_ms)
                elapsed_ms += e2e_float
            else:
                inference_float = None
                e2e_float = None
                timestamp = cycle_start
            records.append({
                "iteration": iteration_base + offset,
                "cycle": cycle_id,
                "image_id": Path(filename).stem,
                "image_path": expected[filename]["image_path"],
                "image_sha256": expected[filename]["image_sha256"],
                "timestamp_utc": iso_timestamp(timestamp),
                "timestamp_source": "cycle_start_plus_cumulative_runner_e2e_ms",
                "inference_latency_ms": inference_float,
                "e2e_latency_ms": e2e_float,
                "detection_count": len(detections),
                "finite_check": finite_check,
                "success": finite_check,
            })
        if seen != set(expected):
            return [], False, "runner output image set does not match frozen split"
        return records, all(item["success"] for item in records), None
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        return [], False, f"cannot parse runner output: {error}"


def failed_cycle_records(expected: dict[str, dict[str, Any]], cycle_id: int,
                         iteration_base: int, timestamp: dt.datetime, reason: str) -> list[dict[str, Any]]:
    records = []
    for offset, filename in enumerate(sorted(expected)):
        records.append({
            "iteration": iteration_base + offset,
            "cycle": cycle_id,
            "image_id": Path(filename).stem,
            "image_path": expected[filename]["image_path"],
            "image_sha256": expected[filename]["image_sha256"],
            "timestamp_utc": iso_timestamp(timestamp),
            "timestamp_source": "failed_cycle_start",
            "inference_latency_ms": None,
            "e2e_latency_ms": None,
            "detection_count": None,
            "finite_check": False,
            "success": False,
            "failure_reason": reason,
        })
    return records


def parse_tegrastats(path: Path) -> dict[str, Any]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    def values(pattern: str) -> list[float]:
        result = []
        for line in lines:
            match = re.search(pattern, line)
            if match:
                result.append(float(match.group(1)))
        return result
    ram_used = values(r"RAM (\d+)/")
    ram_total = values(r"RAM \d+/(\d+)MB")
    gr3d = values(r"GR3D_FREQ (\d+)%")
    tj = values(r"tj@([0-9.]+)C")
    gpu_temp = values(r"gpu@([0-9.]+)C")
    power = values(r"VDD_IN (\d+)mW")
    def summary(items: list[float], unit: str) -> dict[str, Any]:
        if not items:
            return {"sample_count": 0, "unit": unit, "min": None, "mean": None, "max": None}
        return {"sample_count": len(items), "unit": unit, "min": min(items),
                "mean": statistics.fmean(items), "max": max(items)}
    return {
        "sample_count": len(lines),
        "log_path": str(path),
        "first_sample": lines[0] if lines else None,
        "last_sample": lines[-1] if lines else None,
        "ram_used_mb": summary(ram_used, "MB"),
        "ram_total_mb": summary(ram_total, "MB"),
        "gr3d_frequency_percent": summary(gr3d, "%"),
        "temperature_tj_c": summary(tj, "C"),
        "temperature_gpu_c": summary(gpu_temp, "C"),
        "vdd_in_mw": summary(power, "mW"),
    }


def latency_growth(records: list[dict[str, Any]], field: str, window_count: int = 10) -> dict[str, Any]:
    values = [float(item[field]) for item in records if finite(item.get(field))]
    if not values:
        return {"field": field, "window_count": 0, "window_means_ms": [],
                "strictly_increasing_all_windows": False,
                "continuous_growth_detected": False}
    count = min(window_count, len(values))
    means = []
    for index in range(count):
        start = index * len(values) // count
        end = (index + 1) * len(values) // count
        means.append(statistics.fmean(values[start:end]))
    increasing = len(means) > 1 and all(right > left for left, right in zip(means, means[1:]))
    return {"field": field, "window_count": count, "window_means_ms": means,
            "first_window_mean_ms": means[0], "last_window_mean_ms": means[-1],
            "strictly_increasing_all_windows": increasing,
            "continuous_growth_detected": increasing}


def write_sha256sums(directory: Path) -> None:
    lines = []
    for path in sorted(item for item in directory.iterdir() if item.is_file() and item.name != "sha256sums.txt"):
        lines.append(f"{sha256_file(path)}  {path.name}")
    (directory / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def environment_snapshot(engine_manifest: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    cuda_version = run_text(["bash", "-lc", "if test -f /usr/local/cuda/version.json; then sed -n '1,240p' /usr/local/cuda/version.json; else echo unavailable; fi"])
    tegra_release = Path("/etc/nv_tegra_release").read_text(encoding="utf-8", errors="replace").strip() if Path("/etc/nv_tegra_release").is_file() else "unavailable"
    trt_python = run_text([sys.executable, "-c", "import tensorrt as trt; print(trt.__version__)"])
    l4t = run_text(["dpkg-query", "-W", "-f=${Version}\\n", "nvidia-l4t-core"])
    return {
        "host": {"platform": platform.platform(), "machine": platform.machine(), "python": platform.python_version()},
        "engine_manifest_identity": {
            "tensorrt_version_declared": engine_manifest.get("tensorrt_version"),
            "tensorrt_runtime_version_declared": engine_manifest.get("tensorrt_runtime_version"),
            "cuda_version_declared": engine_manifest.get("cuda_version"),
            "l4t_version_declared": engine_manifest.get("l4t_version"),
            "jetson_model_declared": engine_manifest.get("jetson_model"),
        },
        "observed": {
            "nv_tegra_release": tegra_release,
            "nvidia_l4t_core": l4t,
            "python_tensorrt": trt_python,
            "cuda_version_json": cuda_version,
            "tegrastats_help": run_text(["/usr/bin/tegrastats", "--help"]),
        },
        "protocol": protocol,
    }


def run(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise StabilityError(f"evidence directory is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    split, engine_manifest, protocol = load_protocol(args.split.resolve(), args.engine.resolve(), args.engine_manifest.resolve(), args.runner.resolve())
    expected = {Path(entry["image_path"]).name: entry for entry in split["entries"]}
    (output / "environment.json").write_text(json.dumps(environment_snapshot(engine_manifest, protocol), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "commands.txt").write_text(
        "python3 tools/validation/run_stage_k6_stability.py "
        f"--duration-minutes {args.duration_minutes:g} --split {args.split} "
        f"--engine {args.engine} --engine-manifest {args.engine_manifest} "
        f"--runner {args.runner} --output {args.output}\n",
        encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="stage_k6_inputs_") as temp_root:
        input_dir = Path(temp_root) / "test_images"
        prepare_input_directory(input_dir, split)
        records_path = output / "inference_records.jsonl"
        records_stream = records_path.open("w", encoding="utf-8")
        monitor_log = output / "tegrastats.log"
        monitor = subprocess.Popen(["/usr/bin/tegrastats", "--interval", "1000", "--logfile", str(monitor_log)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        all_records: list[dict[str, Any]] = []
        runner_failures: list[dict[str, Any]] = []
        cycle_summaries: list[dict[str, Any]] = []
        started = now_utc()
        measured_start = time.monotonic()
        target_seconds = args.duration_minutes * 60.0
        cycle_id = 0
        try:
            while time.monotonic() - measured_start < target_seconds:
                cycle_start = now_utc()
                cycle_started_mono = time.monotonic()
                with tempfile.TemporaryDirectory(prefix="stage_k6_cycle_") as cycle_root:
                    cycle_dir = Path(cycle_root)
                    raw_output = cycle_dir / "result.json"
                    config_path = cycle_dir / "runtime.yaml"
                    config_path.write_text(make_runtime_config(args.engine.resolve(), args.engine_manifest.resolve(), input_dir, raw_output), encoding="utf-8")
                    command = [str(args.runner.resolve()), "--config", str(config_path)]
                    completed = subprocess.run(command, cwd=REPO_ROOT, text=True,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                    cycle_wall_ms = (time.monotonic() - cycle_started_mono) * 1000.0
                    if completed.returncode == 0 and raw_output.is_file():
                        cycle_records, cycle_success, error = parse_result(raw_output, expected, cycle_id, len(all_records) + 1, cycle_start)
                    else:
                        error = f"runner exit={completed.returncode}; stderr={completed.stderr.strip()}"
                        cycle_records, cycle_success = [], False
                    if not cycle_success:
                        cycle_records = failed_cycle_records(expected, cycle_id, len(all_records) + 1, cycle_start, error or "invalid runner output")
                        runner_failures.append({"cycle": cycle_id, "returncode": completed.returncode, "stderr": completed.stderr.strip(), "stdout": completed.stdout.strip(), "error": error})
                    for record in cycle_records:
                        records_stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                    records_stream.flush()
                    all_records.extend(cycle_records)
                    cycle_summaries.append({"cycle": cycle_id, "started_at_utc": iso_timestamp(cycle_start),
                                            "wall_elapsed_ms": cycle_wall_ms, "frame_count": len(cycle_records),
                                            "success": cycle_success, "runner_returncode": completed.returncode})
                    if not cycle_success:
                        break
                cycle_id += 1
        finally:
            records_stream.close()
            try:
                monitor.terminate()
                monitor.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                monitor.kill()
                monitor.wait(timeout=5)
        completed_at = now_utc()
        duration_seconds = time.monotonic() - measured_start

    inference_values = [float(item["inference_latency_ms"]) for item in all_records if finite(item.get("inference_latency_ms"))]
    e2e_values = [float(item["e2e_latency_ms"]) for item in all_records if finite(item.get("e2e_latency_ms"))]
    success_count = sum(1 for item in all_records if item.get("success") is True)
    failure_count = len(all_records) - success_count
    finite_failures = sum(1 for item in all_records if item.get("finite_check") is not True)
    latency = {"inference": stats(inference_values), "e2e": stats(e2e_values),
               "inference_growth": latency_growth(all_records, "inference_latency_ms"),
               "e2e_growth": latency_growth(all_records, "e2e_latency_ms")}
    write_json(output / "latency_summary.json", {"schema_version": 1, "artifact_kind": "stage_k6_latency_summary",
                                                  "total_frames": len(all_records), **latency})
    monitor_summary = parse_tegrastats(output / "tegrastats.log") if (output / "tegrastats.log").is_file() else {"sample_count": 0}
    write_json(output / "system_monitor_summary.json", {"schema_version": 1, "artifact_kind": "stage_k6_tegrastats_summary",
                                                          "sampling_interval_ms": 1000, **monitor_summary})
    checks = {
        "manifest_sha256_match": protocol["split_manifest_sha256"] == EXPECTED_SPLIT_SHA256,
        "engine_sha256_match": protocol["engine_sha256"] == engine_manifest.get("engine_sha256"),
        "duration_target_complete": duration_seconds >= target_seconds,
        "duration_30_minutes_complete": duration_seconds >= 30.0 * 60.0,
        "inference_success_100_percent": len(all_records) > 0 and success_count == len(all_records),
        "crash_zero": len(runner_failures) == 0,
        "nan_inf_zero": finite_failures == 0,
        "latency_no_continuous_growth": not latency["inference_growth"]["continuous_growth_detected"] and not latency["e2e_growth"]["continuous_growth_detected"],
        "tegrastats_log_present": monitor_summary.get("sample_count", 0) > 0,
    }
    verdict = "K6_STABILITY_PASS" if all(checks.values()) else "K6_STABILITY_FAIL"
    stability = {
        "schema_version": 1, "artifact_kind": "stage_k6_tensorrt_fp16_stability_report",
        "verdict": verdict, "started_at_utc": iso_timestamp(started), "completed_at_utc": iso_timestamp(completed_at),
        "runtime_duration_seconds": duration_seconds, "target_duration_seconds": target_seconds,
        "total_frames": len(all_records), "success_count": success_count, "failure_count": failure_count,
        "runner_failure_count": len(runner_failures), "finite_failure_count": finite_failures,
        "cycle_count": len(cycle_summaries), "protocol": protocol, "cycles": cycle_summaries,
        "runner_failures": runner_failures, "checks": checks,
        "latency_summary_file": "latency_summary.json", "records_file": "inference_records.jsonl",
        "script_sha256": sha256_file(Path(__file__).resolve()),
    }
    write_json(output / "stability_report.json", stability)
    readme = f"""Stage K6 TensorRT FP16 Stability Validation v1

Verdict: {verdict}

1. Engine identity

- Engine: Original TensorRT FP16 Engine
- Engine path: {protocol['engine_path']}
- Engine SHA256: {protocol['engine_sha256']}
- Manifest path: {protocol['engine_manifest_path']}
- Manifest SHA256: {protocol['engine_manifest_sha256']}
- Split manifest SHA256: {protocol['split_manifest_sha256']}

2. Environment

- TensorRT (manifest): {engine_manifest.get('tensorrt_version')}
- CUDA runtime (manifest): {engine_manifest.get('cuda_version')}
- JetPack/L4T (manifest): {engine_manifest.get('l4t_version')}
- Jetson model (manifest): {engine_manifest.get('jetson_model')}
- Observed environment details: environment.json

3. Test protocol

- Frozen test split: 180 images
- Repeat inference for target duration: {args.duration_minutes:g} minutes
- Runtime: single serial inference process at a time, single-thread OpenCV policy, batch=1
- Input: fixed local test split via hard links; no dataset files are copied to evidence
- Monitoring: tegrastats at 1 second; raw log is tegrastats.log

4. Runtime result

- Total frames: {len(all_records)}
- Success count: {success_count}
- Failure count: {failure_count}
- Runner crashes: {len(runner_failures)}
- Runtime duration seconds: {duration_seconds:.3f}
- Success rate: {(100.0 * success_count / len(all_records)) if all_records else 0.0:.6f}%

5. Latency statistics

- Inference: latency_summary.json (`mean`, `median`, `p95`, `max`)
- E2E: latency_summary.json (`mean`, `median`, `p95`, `max`)
- Per-inference records: inference_records.jsonl
- Growth check: continuous growth means all ten equal-count window means strictly increase; see latency_summary.json.

6. tegrastats summary

- Samples: {monitor_summary.get('sample_count', 0)}
- Summary: system_monitor_summary.json

7. Verdict

The machine-readable verdict is {verdict}. Verification checks are in verification_report.json.
No Engine, ONNX, ModelContract, RuntimeConfig, comparator tolerance, K5 evidence, watchdog,
ROS2, camera streaming, multi-thread pipeline, or DeepStream component was modified by this task.
"""
    (output / "README.txt").write_text(readme, encoding="utf-8")
    write_json(output / "verification_report.json", {"schema_version": 1, "artifact_kind": "stage_k6_verification_report",
                                                       "verdict": verdict, "checks": checks,
                                                       "total_frames": len(all_records), "success_count": success_count,
                                                       "failure_count": failure_count, "runtime_duration_seconds": duration_seconds,
                                                       "engine_sha256": protocol["engine_sha256"],
                                                       "engine_manifest_sha256": protocol["engine_manifest_sha256"],
                                                       "split_manifest_sha256": protocol["split_manifest_sha256"]})
    if runner_failures:
        write_json(output / "runner_failures.json", runner_failures)
    write_sha256sums(output)
    print(json.dumps({"verdict": verdict, "total_frames": len(all_records), "duration_seconds": duration_seconds,
                      "success_rate": (success_count / len(all_records)) if all_records else 0.0,
                      "mean_inference_ms": latency["inference"]["mean_ms"],
                      "p95_inference_ms": latency["inference"]["p95_ms"], "output": str(output)}, indent=2))
    return 0 if verdict == "K6_STABILITY_PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage K6 Original TensorRT FP16 stability validation")
    parser.add_argument("--duration-minutes", type=float, default=30.0)
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE)
    parser.add_argument("--engine-manifest", type=Path, default=DEFAULT_ENGINE_MANIFEST)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not math.isfinite(args.duration_minutes) or args.duration_minutes <= 0:
        parser.error("--duration-minutes must be positive and finite")
    try:
        return run(args)
    except (OSError, StabilityError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"K6_STABILITY_FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
