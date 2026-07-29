#!/usr/bin/env python3
"""Run the frozen Stage K7 TensorRT FP32/FP16 performance benchmark."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT_DEFAULT = ROOT / "results/validation/stage_k7/performance_v1"
SPLIT_DEFAULT = ROOT / "results/validation/stage_k_task_eval_v2/split/test_manifest.json"
BUILD_DEFAULT = Path("/home/orin/edge-ai-local-build/k5_correctness_v1/c54020c_release")
BINARY_DEFAULT = Path("/home/orin/edge-ai-local-build/stage_k7_performance_v1/stage_k7_trt_benchmark")
RUNNER_SOURCE = ROOT / "tools/benchmark/stage_k7_trt_benchmark.cpp"
EXPECTED_SPLIT_SHA = "fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8"
EXPECTED_ONNX_SHA = "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944"
EXPECTED_CONTRACT_SHA = "9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190"

ENGINES = {
    "fp32_notf32": {
        "label": "Strict FP32 TensorRT noTF32",
        "engine": Path(
            "/home/orin/edge-ai-local-models/stage_k/strict_fp32_notf32_v1/"
            "yolov8n_neudet_trt10.3_strict_fp32_notf32_b1_640.engine"
        ),
        "manifest": ROOT / "results/build/tensorrt/strict_fp32_notf32_investigation_v1/manifest.json",
        "sha256": "aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f",
    },
    "fp16_original": {
        "label": "Original TensorRT FP16",
        "engine": Path(
            "/home/orin/edge-ai-local-models/stage_k/"
            "yolov8n_neudet_trt10.3_fp16_b1_640.engine"
        ),
        "manifest": ROOT / "models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json",
        "sha256": "6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def command_result(command: list[str]) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "output": completed.stdout,
        "elapsed_ms": (time.monotonic() - started) * 1000.0,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_split(path: Path) -> tuple[dict[str, Any], str]:
    actual_sha = sha256_file(path)
    if actual_sha != EXPECTED_SPLIT_SHA:
        raise RuntimeError(f"test split SHA mismatch: expected {EXPECTED_SPLIT_SHA}, got {actual_sha}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("split") != "test" or manifest.get("entry_count") != 180:
        raise RuntimeError("frozen test split is not the expected 180-image test manifest")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != 180:
        raise RuntimeError("frozen test split entries are invalid")
    return manifest, actual_sha


def validate_engines() -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    for key, definition in ENGINES.items():
        engine = definition["engine"]
        manifest_path = definition["manifest"]
        if not engine.is_file() or not manifest_path.is_file():
            raise RuntimeError(f"missing {key} engine or manifest")
        actual_sha = sha256_file(engine)
        if actual_sha != definition["sha256"]:
            raise RuntimeError(f"{key} engine SHA mismatch: {actual_sha}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("engine_sha256") != actual_sha:
            raise RuntimeError(f"{key} manifest does not identify the engine SHA")
        if manifest.get("source_onnx_sha256") != EXPECTED_ONNX_SHA:
            raise RuntimeError(f"{key} source ONNX SHA mismatch")
        if manifest.get("model_contract_sha256") != EXPECTED_CONTRACT_SHA:
            raise RuntimeError(f"{key} ModelContract SHA mismatch")
        identities[key] = {
            "key": key,
            "label": definition["label"],
            "engine_path": str(engine),
            "engine_sha256": actual_sha,
            "engine_size_bytes": engine.stat().st_size,
            "manifest_path": str(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "tensorrt_version": manifest.get("tensorrt_version"),
            "cuda_version": manifest.get("cuda_version"),
            "l4t_version": manifest.get("l4t_version"),
            "jetson_model": manifest.get("jetson_model"),
            "source_onnx_sha256": manifest.get("source_onnx_sha256"),
            "model_contract_sha256": manifest.get("model_contract_sha256"),
            "precision_mode": manifest.get("precision_mode"),
        }
    return identities


def freeze_environment(identities: dict[str, dict[str, Any]], runner: Path) -> dict[str, Any]:
    governor: dict[str, str] = {}
    for path in sorted(Path("/sys/devices/system/cpu").glob("cpu*/cpufreq/scaling_governor")):
        try:
            governor[str(path)] = path.read_text().strip()
        except OSError as error:
            governor[str(path)] = f"unavailable: {error}"
    commands = {
        "uname": ["uname", "-a"],
        "l4t_release": ["bash", "-lc", "cat /etc/nv_tegra_release"],
        "jetson_model": ["bash", "-lc", "tr -d '\\0' < /proc/device-tree/model"],
        "nvpmodel_query": ["nvpmodel", "-q"],
        "jetson_clocks_show": ["jetson_clocks", "--show"],
        "cuda_nvcc": ["bash", "-lc", "command -v nvcc && nvcc --version"],
        "tensorrt_library": ["bash", "-lc", "ldconfig -p | grep libnvinfer.so | head -5"],
        "tool_versions": ["dpkg-query", "-W", "-f=${Package} ${Version}\\n",
                           "nvidia-l4t-core", "nvidia-l4t-cuda", "nvidia-l4t-tools"],
    }
    observed = {name: command_result(command) for name, command in commands.items()}
    gpu_dir = Path("/sys/devices/platform/17000000.gpu/devfreq/17000000.gpu")
    gpu_state: dict[str, str] = {}
    for name in ("governor", "cur_freq", "min_freq", "max_freq"):
        path = gpu_dir / name
        try:
            gpu_state[name] = path.read_text().strip()
        except OSError as error:
            gpu_state[name] = f"unavailable: {error}"
    return {
        "captured_at_utc": now_utc(),
        "host": {
            "uname": platform.uname()._asdict(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
            "jetson_model": observed["jetson_model"]["output"].strip(),
            "l4t_release": observed["l4t_release"]["output"].strip(),
        },
        "jetson": {
            "nvpmodel": observed["nvpmodel_query"],
            "gpu_power_mode": observed["nvpmodel_query"]["output"].strip(),
            "nvpmodel_service_state": command_result(["systemctl", "is-active", "nvpmodel.service"]),
            "jetson_clocks": observed["jetson_clocks_show"],
            "jetson_clocks_state": "unavailable_without_root" if observed["jetson_clocks_show"]["returncode"] else "reported",
        },
        "software": {
            "l4t_release_command": observed["l4t_release"],
            "cuda": observed["cuda_nvcc"],
            "tensorrt_library": observed["tensorrt_library"],
            "packages": observed["tool_versions"],
            "engine_manifest_identities": identities,
        },
        "cpu_governor": governor,
        "gpu_frequency_state": gpu_state,
        "runner": {
            "path": str(runner),
            "sha256": sha256_file(runner),
        },
    }


def prepare_input_directory(root: Path, split: dict[str, Any]) -> list[dict[str, Any]]:
    dataset_root = ROOT / split["dataset_root"]
    entries = split["entries"]
    prepared: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        source = dataset_root / entry["image_path"]
        if not source.is_file() or sha256_file(source) != entry["image_sha256"]:
            raise RuntimeError(f"test image unavailable or changed: {source}")
        destination = root / f"{index:04d}{source.suffix.lower()}"
        os.link(source, destination)
        prepared.append({
            "sequence_index": index,
            "source_image_path": entry["image_path"],
            "prepared_name": destination.name,
            "image_sha256": entry["image_sha256"],
        })
    return prepared


def compile_runner(build_dir: Path, output: Path) -> list[str]:
    pkg = subprocess.run(["pkg-config", "--cflags", "--libs", "opencv4"],
                         text=True, stdout=subprocess.PIPE, check=True)
    opencv_flags = pkg.stdout.split()
    command = [
        "g++", "-std=c++17", "-O2", "-DNDEBUG",
        f"-I{ROOT / 'include'}",
        "-I/usr/local/cuda-12.6/targets/aarch64-linux/include",
        "-I/usr/include/aarch64-linux-gnu",
        str(RUNNER_SOURCE),
        str(build_dir / "libedge_ai_core.a"),
        str(build_dir / "libedge_ai_postprocess.a"),
        "-L/usr/local/cuda-12.6/targets/aarch64-linux/lib",
        "-Wl,--no-as-needed", "-lnvinfer", "-lcudart", "-Wl,--as-needed",
        "-o", str(output),
        *opencv_flags,
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise RuntimeError("benchmark runner compilation failed:\n" + completed.stderr)
    return command


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def stats(values: list[float]) -> dict[str, float | int]:
    if not values or any(not math.isfinite(value) or value < 0.0 for value in values):
        raise RuntimeError("latency samples are empty or non-finite")
    mean = statistics.fmean(values)
    return {
        "count": len(values),
        "mean_ms": mean,
        "median_ms": statistics.median(values),
        "std_ms": statistics.pstdev(values),
        "p50_ms": percentile(values, 0.50),
        "p95_ms": percentile(values, 0.95),
        "p99_ms": percentile(values, 0.99),
        "min_ms": min(values),
        "max_ms": max(values),
        "fps": 1000.0 / mean,
    }


def read_samples(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 5100:
        raise RuntimeError(f"{path}: expected 5100 rows including warmup, got {len(rows)}")
    warmups = [row for row in rows if row["phase"] == "warmup"]
    measured = [row for row in rows if row["phase"] == "measure"]
    if len(warmups) != 100 or len(measured) != 5000:
        raise RuntimeError(f"{path}: warmup/measure count mismatch")
    for index, row in enumerate(measured):
        if int(row["iteration"]) != index or int(row["image_index"]) != (index + 100) % 180:
            raise RuntimeError(f"{path}: non-deterministic image sequence at measured row {index}")
        for field in ("preprocess_ms", "h2d_ms", "inference_ms", "postprocess_ms", "e2e_ms"):
            value = float(row[field])
            if not math.isfinite(value) or value < 0.0:
                raise RuntimeError(f"{path}: invalid {field}")
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in rows if row["phase"] == "measure"]
    return {
        "inference": stats([float(row["inference_ms"]) for row in measured]),
        "e2e": stats([float(row["e2e_ms"]) for row in measured]),
        "preprocess": stats([float(row["preprocess_ms"]) for row in measured]),
        "h2d": stats([float(row["h2d_ms"]) for row in measured]),
        "postprocess": stats([float(row["postprocess_ms"]) for row in measured]),
        "detection_count": sum(int(row["detection_count"]) for row in measured),
        "warmup_count": sum(1 for row in rows if row["phase"] == "warmup"),
        "measured_count": len(measured),
    }


def run_one(binary: Path, backend_dir: Path, run_id: str, identity: dict[str, Any],
            input_dir: Path, warmup: int, iterations: int) -> dict[str, Any]:
    run_dir = backend_dir / run_id
    run_dir.mkdir(parents=True)
    samples = run_dir / "latency_samples.csv"
    stdout_path = run_dir / "runner.stdout.txt"
    stderr_path = run_dir / "runner.stderr.txt"
    command = [str(binary), "--engine", identity["engine_path"], "--input-dir", str(input_dir),
               "--output-csv", str(samples), "--warmup", str(warmup), "--iterations", str(iterations)]
    telemetry_path = run_dir / "tegrastats.log"
    telemetry = telemetry_path.open("w", encoding="utf-8")
    telemetry_process = subprocess.Popen(["tegrastats", "--interval", "1000"],
                                         stdout=telemetry, stderr=subprocess.STDOUT, text=True)
    started = now_utc()
    wall_start = time.monotonic()
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    wall_elapsed = (time.monotonic() - wall_start) * 1000.0
    completed_at = now_utc()
    try:
        telemetry_process.terminate()
        telemetry_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        telemetry_process.kill()
        telemetry_process.wait(timeout=5)
    telemetry.close()
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"{identity['key']} {run_id} failed; see {stderr_path}")
    rows = read_samples(samples)
    summary = summarize(rows)
    run_manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k7_performance_run",
        "backend": identity,
        "run_id": run_id,
        "started_at_utc": started,
        "completed_at_utc": completed_at,
        "command": command,
        "returncode": completed.returncode,
        "subprocess_wall_elapsed_ms": wall_elapsed,
        "warmup_iterations": warmup,
        "measured_iterations": iterations,
        "input_image_count": 180,
        "latency_summary": summary,
        "tegrastats": {
            "path": "tegrastats.log",
            "sample_interval_ms": 1000,
            "line_count": sum(1 for _ in telemetry_path.open(encoding="utf-8")),
        },
        "timing_definitions": {
            "inference": "host timestamp immediately before enqueueV3 through D2H cudaStreamSynchronize completion; H2D is excluded",
            "e2e": "host timestamp before preprocess through postprocess completion; image decode and result serialization are excluded",
        },
    }
    write_json(run_dir / "manifest.json", run_manifest)
    return {"run_id": run_id, "rows": rows, "summary": summary, "manifest": run_manifest}


def aggregate_backend(backend_dir: Path, identity: dict[str, Any], runs: list[dict[str, Any]],
                      protocol: dict[str, Any]) -> dict[str, Any]:
    all_rows: list[dict[str, Any]] = []
    for run in runs:
        for row in run["rows"]:
            all_rows.append({"backend": identity["key"], "run_id": run["run_id"], **row})
    aggregate_csv = backend_dir / "latency_samples.csv"
    fields = ["backend", "run_id", "phase", "iteration", "image_index", "image_name",
              "preprocess_ms", "h2d_ms", "inference_ms", "postprocess_ms", "e2e_ms",
              "detection_count"]
    with aggregate_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)
    measured = [row for row in all_rows if row["phase"] == "measure"]
    aggregate = {
        "inference": stats([float(row["inference_ms"]) for row in measured]),
        "e2e": stats([float(row["e2e_ms"]) for row in measured]),
        "preprocess": stats([float(row["preprocess_ms"]) for row in measured]),
        "h2d": stats([float(row["h2d_ms"]) for row in measured]),
        "postprocess": stats([float(row["postprocess_ms"]) for row in measured]),
        "run_count": len(runs),
        "valid_run_count": sum(1 for run in runs if run["manifest"]["returncode"] == 0),
        "measured_count": len(measured),
        "warmup_count": sum(1 for row in all_rows if row["phase"] == "warmup"),
        "detection_count": sum(int(row["detection_count"]) for row in measured),
        "raw_tensor_correctness": "not measured by K7; task-level K5 accepted and K6 stability pass are inherited",
    }
    report = {
        "schema_version": 1,
        "artifact_kind": "stage_k7_performance_benchmark_report",
        "backend": identity,
        "protocol": protocol,
        "statistics": aggregate,
        "runs": [{"run_id": run["run_id"], "summary": run["summary"],
                  "manifest": f"{run['run_id']}/manifest.json"} for run in runs],
        "artifacts": {
            "latency_samples": "latency_samples.csv",
            "tegrastats": "tegrastats.log",
        },
    }
    write_json(backend_dir / "benchmark_report.json", report)
    with (backend_dir / "tegrastats.log").open("w", encoding="utf-8") as aggregate_log:
        for run in runs:
            aggregate_log.write(f"# BEGIN {run['run_id']}\n")
            aggregate_log.write((backend_dir / run["run_id"] / "tegrastats.log").read_text(encoding="utf-8"))
            aggregate_log.write(f"# END {run['run_id']}\n")
    write_json(backend_dir / "manifest.json", {
        "schema_version": 1,
        "artifact_kind": "stage_k7_performance_backend_manifest",
        "backend": identity,
        "protocol": protocol,
        "benchmark_report_sha256": sha256_file(backend_dir / "benchmark_report.json"),
        "latency_samples_sha256": sha256_file(aggregate_csv),
        "tegrastats_sha256": sha256_file(backend_dir / "tegrastats.log"),
        "runs": [run["manifest"] for run in runs],
    })
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--split", type=Path, default=SPLIT_DEFAULT)
    parser.add_argument("--build-dir", type=Path, default=BUILD_DEFAULT)
    parser.add_argument("--binary", type=Path, default=BINARY_DEFAULT)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=5000)
    args = parser.parse_args()
    if args.runs != 3 or args.warmup != 100 or args.iterations != 5000:
        raise SystemExit("K7 v1 is frozen at 3 runs, 100 warmup iterations, and 5000 measured iterations")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty output: {output}")
    if not RUNNER_SOURCE.is_file():
        raise SystemExit(f"benchmark source missing: {RUNNER_SOURCE}")
    split, split_sha = load_split(args.split.resolve())
    identities = validate_engines()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage_k7_input_") as temp_input:
        prepared = prepare_input_directory(Path(temp_input), split)
        prepared_manifest = {
            "schema_version": 1,
            "artifact_kind": "stage_k7_prepared_input_manifest",
            "source_split_manifest": str(args.split.resolve()),
            "source_split_sha256": split_sha,
            "entry_count": len(prepared),
            "entries": prepared,
        }
        write_json(output / "prepared_input_manifest.json", prepared_manifest)
        binary = args.binary.resolve()
        binary.parent.mkdir(parents=True, exist_ok=True)
        build_command = compile_runner(args.build_dir.resolve(), binary)
        protocol = {
            "schema_version": 1,
            "stage": "K7",
            "benchmark_version": "performance_v1",
            "input_split": "Stage K test split",
            "input_split_manifest_sha256": split_sha,
            "input_image_count": 180,
            "warmup_iterations": args.warmup,
            "measured_iterations_per_run": args.iterations,
            "independent_processes_per_backend": args.runs,
            "sequence": "sorted frozen test-manifest order; image index = (ordinal % 180); measured index starts after warmup",
            "runtime_mode": "serial",
            "preprocessing": "existing repository Preprocessor, BGR LetterBox 640x640, RGB NCHW FP32 / 255",
            "postprocessing": "existing repository PostProcessor, confidence 0.25, IoU 0.45, max_det 300",
            "inference_timing": "enqueueV3 start through D2H cudaStreamSynchronize completion; H2D excluded",
            "e2e_timing": "preprocess start through postprocess completion; decode and result serialization excluded",
            "statistics": "population std; Hyndman-Fan Type 7 percentiles; FPS = 1000 / mean_ms",
            "build_command": build_command,
            "benchmark_source": str(RUNNER_SOURCE),
            "benchmark_source_sha256": sha256_file(RUNNER_SOURCE),
        }
        write_json(output / "protocol.json", protocol)
        environment = freeze_environment(identities, binary)
        write_json(output / "environment.json", environment)
        backend_reports: dict[str, Any] = {}
        for key, identity in identities.items():
            backend_dir = output / key
            backend_dir.mkdir()
            runs = []
            for run_number in range(1, args.runs + 1):
                runs.append(run_one(binary, backend_dir, f"run_{run_number:03d}", identity,
                                    Path(temp_input), args.warmup, args.iterations))
            backend_reports[key] = aggregate_backend(backend_dir, identity, runs, protocol)

    fp32 = backend_reports["fp32_notf32"]["statistics"]
    fp16 = backend_reports["fp16_original"]["statistics"]
    inference_speedup = fp32["inference"]["mean_ms"] / fp16["inference"]["mean_ms"]
    e2e_speedup = fp32["e2e"]["mean_ms"] / fp16["e2e"]["mean_ms"]
    comparison = {
        "schema_version": 1,
        "artifact_kind": "stage_k7_comparison_report",
        "verdict": "K7_PERFORMANCE_COMPLETE",
        "reference": "fp32_notf32",
        "candidate": "fp16_original",
        "engine_identities": {key: value for key, value in identities.items()},
        "statistics": {
            "fp32_notf32": fp32,
            "fp16_original": fp16,
        },
        "speedup": {
            "inference": inference_speedup,
            "inference_latency_reduction_percent": 100.0 * (1.0 - 1.0 / inference_speedup),
            "e2e": e2e_speedup,
            "e2e_latency_reduction_percent": 100.0 * (1.0 - 1.0 / e2e_speedup),
        },
        "accuracy_context": {
            "k5": "TASK_LEVEL_FP16_ACCEPTED",
            "k6": "K6_STABILITY_PASS",
            "raw_tensor_correctness": "K7 does not claim bitwise raw-tensor equivalence; raw tensor correctness remains a limitation recorded by prior validation.",
        },
        "limitations": [
            "No Engine, ONNX, ModelContract, production runtime, or K5 gate was modified.",
            "M3 selective and Debug Engine were not used.",
            "Resource metrics are retained as raw 1-second tegrastats logs; fields absent from tegrastats remain unavailable.",
        ],
    }
    write_json(output / "comparison_report.json", comparison)
    readme = f"""Stage K7 TensorRT Performance Benchmark v1
============================================

Verdict: K7_PERFORMANCE_COMPLETE

The frozen Stage K test split (180 images, SHA256 {split_sha}) was replayed in
deterministic order for 100 warmup iterations and 5000 measured iterations in
each of three independent processes per backend.

Aggregate performance (15,000 measured samples per backend)
------------------------------------------------------------

                         mean inference ms   mean E2E ms   inference FPS   E2E FPS
  Strict FP32 noTF32     {fp32['inference']['mean_ms']:.6f}              {fp32['e2e']['mean_ms']:.6f}       {fp32['inference']['fps']:.6f}       {fp32['e2e']['fps']:.6f}
  Original FP16          {fp16['inference']['mean_ms']:.6f}              {fp16['e2e']['mean_ms']:.6f}       {fp16['inference']['fps']:.6f}       {fp16['e2e']['fps']:.6f}

  inference speedup (FP32 / FP16): {inference_speedup:.6f}x
  E2E speedup (FP32 / FP16):       {e2e_speedup:.6f}x

Timing definitions
------------------

Inference timing starts immediately before TensorRT enqueueV3 and ends after
the D2H cudaStreamSynchronize completes. H2D is recorded separately and is
excluded from inference timing. E2E timing starts before preprocessing and ends
after postprocessing; image decode and result serialization are excluded.

Environment and telemetry
-------------------------

The environment freeze is in environment.json. Each backend retains raw
1-second tegrastats output in tegrastats.log and per-process run directories.
If EMC or another field is absent from the raw tegrastats output, it is not
invented in this report.

Performance conclusion
----------------------

Compared with the strict FP32 TensorRT noTF32 baseline, the Original TensorRT
FP16 Engine changed measured inference latency by
{100.0 * (1.0 - 1.0 / inference_speedup):.3f}% and changed measured E2E latency by
{100.0 * (1.0 - 1.0 / e2e_speedup):.3f}% (positive means reduction). These are
descriptive measurements from this frozen Jetson environment, not a universal
performance guarantee.

Accuracy limitation
-------------------

K5 task-level validation was TASK_LEVEL_FP16_ACCEPTED and K6 stability was
K6_STABILITY_PASS. This K7 benchmark does not claim bitwise raw-tensor
correctness; raw tensor correctness remains a documented limitation of the
prior validation evidence.

Artifacts
---------

  fp32_notf32/benchmark_report.json
  fp32_notf32/latency_samples.csv
  fp32_notf32/tegrastats.log
  fp32_notf32/manifest.json
  fp16_original/benchmark_report.json
  fp16_original/latency_samples.csv
  fp16_original/tegrastats.log
  fp16_original/manifest.json
  comparison_report.json
"""
    (output / "README.txt").write_text(readme, encoding="utf-8")
    print(json.dumps({
        "verdict": comparison["verdict"],
        "output": str(output),
        "fp32_mean_inference_ms": fp32["inference"]["mean_ms"],
        "fp32_mean_e2e_ms": fp32["e2e"]["mean_ms"],
        "fp16_mean_inference_ms": fp16["inference"]["mean_ms"],
        "fp16_mean_e2e_ms": fp16["e2e"]["mean_ms"],
        "inference_speedup": inference_speedup,
        "e2e_speedup": e2e_speedup,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
