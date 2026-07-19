#!/usr/bin/env python3
"""Frozen M5.3 protocol helpers.

This module deliberately contains no application-specific inference code.  It
owns the benchmark contract, strict JSON/timing validation, deterministic
serialization/compression, workload copies, statistics primitives, affinity,
and small evidence staging utilities used by the analyzer and orchestrator.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "tests/data/m5/manifests/benchmark_corpus.json"
CLASS_NAMES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
TIMING_FIELDS = ["source", "preprocess", "inference", "postprocess", "pre_sink_total"]
TIMING_COLUMNS = ["source_ms", "preprocess_ms", "inference_ms", "postprocess_ms", "pre_sink_total_ms"]
PROTOCOL = {
    "pilot_frames": 100,
    "pilot_discard": 20,
    "formal_warmup": 50,
    "minimum_measured_frames": 500,
    "target_measured_duration_ms": 33000,
    "minimum_valid_duration_ms": 30000,
    "formal_run_count": 5,
    "inter_run_wait_seconds": 30,
    "corpus_size": 20,
    "gzip_level": 9,
    "gzip_mtime": 0,
    "percentile_method": "hyndman_fan_type_7",
    "sample_stddev": "n_minus_1",
    "outlier_policy": "keep_all_measured_samples",
}


class BenchmarkError(ValueError):
    """Invalid frozen protocol, input or generated artifact."""


class PreflightError(BenchmarkError):
    """Environment or repository preflight failed."""


class TimingError(BenchmarkError):
    """Application timing JSON is not a valid M4 contract."""


class EvidenceError(BenchmarkError):
    """Staging or evidence validation failed."""


def stable_json_bytes(value: Any) -> bytes:
    """Return deterministic JSON with one LF and no non-finite values."""
    return (json.dumps(value, ensure_ascii=False, indent=2, separators=(",", ": "),
                       allow_nan=False) + "\n").encode("utf-8")


def write_stable_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stable_json_bytes(value))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise TimingError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _reject_constant(value: str) -> Any:
    raise TimingError(f"non-finite JSON constant: {value}")


def read_strict_json(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TimingError(f"cannot read JSON {path}: {exc}") from exc
    if not raw.endswith("\n") or raw.endswith("\n\n"):
        raise TimingError("JSON must end with exactly one LF")
    try:
        return json.loads(raw, object_pairs_hook=_duplicate_pairs, parse_constant=_reject_constant)
    except (json.JSONDecodeError, TimingError) as exc:
        if isinstance(exc, TimingError):
            raise
        raise TimingError(f"invalid JSON: {exc}") from exc


def _keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict) or list(value) != expected:
        raise TimingError(f"{where} fields/order mismatch")


def _int(value: Any, where: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise TimingError(f"{where} must be an integer >= {minimum}")
    return value


def finite_nonnegative(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TimingError(f"{where} must be a number")
    converted = float(value)
    if not math.isfinite(converted) or converted < 0.0:
        raise TimingError(f"{where} must be finite and non-negative")
    return converted


def _safe_relative(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        raise TimingError(f"{where} must be a relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise TimingError(f"{where} is unsafe")
    return value


def validate_benchmark_manifest(data: Any) -> dict[str, Any]:
    """Validate the tracked 20-image benchmark manifest without changing it."""
    expected_top = ["schema_version", "corpus_id", "dataset", "split", "image_root_semantics", "entries", "coverage"]
    _keys(data, expected_top, "benchmark manifest")
    if data["schema_version"] != 1 or data["corpus_id"] != "m5_ort_cpu_benchmark_original_v1":
        raise BenchmarkError("invalid benchmark manifest identity")
    if data["dataset"] != "NEU-DET" or data["split"] != "validation":
        raise BenchmarkError("benchmark manifest must use validation split")
    if data["image_root_semantics"] != "user_supplied_validation_image_root":
        raise BenchmarkError("benchmark image root semantics are invalid")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 20:
        raise BenchmarkError("benchmark manifest must contain exactly 20 entries")
    seen_source: set[str] = set()
    seen_prepared: set[str] = set()
    seen_sha: set[str] = set()
    counts = [0] * 6
    expected_entry = ["sequence_index", "source_filename", "prepared_filename", "expected_sha256", "expected_width", "expected_height", "gt_classes"]
    for index, entry in enumerate(entries):
        _keys(entry, expected_entry, f"benchmark entry {index}")
        if _int(entry["sequence_index"], "sequence_index") != index:
            raise BenchmarkError("sequence_index must be contiguous 0..19")
        source = _safe_relative(entry["source_filename"], "source_filename")
        prepared = _safe_relative(entry["prepared_filename"], "prepared_filename")
        if source in seen_source or prepared in seen_prepared or not prepared.startswith(f"{index:04d}_"):
            raise BenchmarkError("benchmark filenames are not unique or ordered")
        seen_source.add(source)
        seen_prepared.add(prepared)
        digest = entry["expected_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest) or digest in seen_sha:
            raise BenchmarkError("benchmark expected SHA256 is invalid or duplicated")
        seen_sha.add(digest)
        if _int(entry["expected_width"], "expected_width", 1) != 200 or _int(entry["expected_height"], "expected_height", 1) != 200:
            raise BenchmarkError("benchmark images must be 200x200")
        classes = entry["gt_classes"]
        if (not isinstance(classes, list) or not classes or len(set(classes)) != len(classes)
                or any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < 6 for x in classes)):
            raise BenchmarkError("gt_classes is invalid")
        for class_id in set(classes):
            counts[class_id] += 1
    if any(count < 3 for count in counts):
        raise BenchmarkError("each class must occur at least three times")
    coverage = data["coverage"]
    _keys(coverage, ["class_names", "class_counts", "required_roles"], "benchmark coverage")
    if coverage["class_names"] != CLASS_NAMES or coverage["class_counts"] != dict(zip(CLASS_NAMES, counts)):
        raise BenchmarkError("benchmark coverage mismatch")
    return data


def load_benchmark_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw, object_pairs_hook=_duplicate_pairs, parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"cannot read benchmark manifest: {exc}") from exc
    return validate_benchmark_manifest(data)


def prepare_single_cycle(dataset_root: Path, output_dir: Path) -> dict[str, Any]:
    """Reuse the M5.1 importer; no duplicate SHA/copy implementation here."""
    validation_dir = REPO_ROOT / "tools" / "validation"
    if str(validation_dir) not in sys.path:
        sys.path.insert(0, str(validation_dir))
    try:
        from prepare_m5_corpus import prepare
        return prepare("benchmark", dataset_root, output_dir)
    except Exception as exc:
        if isinstance(exc, BenchmarkError):
            raise
        raise BenchmarkError(str(exc)) from exc


def validate_prepared_cycle(directory: Path, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest_data = read_strict_json(directory / "prepared_corpus_manifest.json") if manifest is None else dict(manifest)
    if manifest_data.get("corpus_mode") != "benchmark" or len(manifest_data.get("entries", [])) != 20:
        raise BenchmarkError("prepared cycle must contain the 20-image benchmark corpus")
    entries = manifest_data["entries"]
    expected_names = {entry.get("prepared_filename") for entry in entries if isinstance(entry, Mapping)}
    actual_names = {path.name for path in directory.iterdir() if path.is_file() and path.name != "prepared_corpus_manifest.json"}
    if len(expected_names) != 20 or actual_names != expected_names:
        raise BenchmarkError("prepared cycle must contain exactly the manifest images")
    for index, entry in enumerate(entries):
        filename = entry.get("prepared_filename")
        if not isinstance(filename, str) or filename != f"{index:04d}_" + filename.split("_", 1)[-1]:
            raise BenchmarkError("prepared cycle order is invalid")
        path = directory / filename
        expected_sha = entry.get("prepared_sha256")
        if not isinstance(expected_sha, str) or not path.is_file() or path.is_symlink() or sha256_file(path) != expected_sha:
            raise BenchmarkError(f"prepared image mismatch: {filename}")
        if path.stat().st_nlink != 1:
            raise BenchmarkError("prepared workload must not use hard links")
    return manifest_data


def build_workload(single_cycle: Path, output_dir: Path, total_frames: int, *, formal: bool = True) -> dict[str, Any]:
    """Repeat the validated 20-file cycle as independent regular-file copies."""
    if isinstance(total_frames, bool) or not isinstance(total_frames, int) or total_frames <= 0:
        raise BenchmarkError("total_frames must be a positive integer")
    if formal and total_frames % 20 != 0:
        raise BenchmarkError("formal workload total_frames must be a multiple of 20")
    if output_dir.exists():
        raise BenchmarkError("workload output directory already exists")
    cycle = validate_prepared_cycle(single_cycle)
    entries = cycle["entries"]
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=str(output_dir.parent)))
    workload_entries: list[dict[str, Any]] = []
    try:
        for workload_index in range(total_frames):
            source_index = workload_index % 20
            source = entries[source_index]
            source_path = single_cycle / source["prepared_filename"]
            name = f"{workload_index:06d}_{source['prepared_filename'].split('_', 1)[-1]}"
            destination = staging / name
            shutil.copyfile(source_path, destination)
            if destination.stat().st_nlink != 1 or destination.is_symlink():
                raise BenchmarkError("workload output is not an independent regular file")
            workload_entries.append({
                "workload_sequence_index": workload_index,
                "cycle_index": workload_index // 20,
                "source_sequence_index": source_index,
                "source_filename": source["source_filename"],
                "source_sha256": source["source_sha256"],
                "prepared_filename": source["prepared_filename"],
                "prepared_sha256": source["prepared_sha256"],
                "workload_filename": name,
                "workload_sha256": sha256_file(destination),
            })
        manifest = {"schema_version": 1, "workload_mode": "benchmark_repeat", "corpus_size": 20,
                    "total_frames": total_frames, "entries": workload_entries}
        write_stable_json(staging / "workload_manifest.json", manifest)
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def compute_formal_frame_counts(pilot_pre_sink_ms: Iterable[float], protocol: Mapping[str, int] = PROTOCOL) -> dict[str, float | int]:
    samples = [finite_nonnegative(x, "pilot timing") for x in pilot_pre_sink_ms]
    if len(samples) != protocol["pilot_frames"]:
        raise BenchmarkError("pilot must contain exactly 100 timing samples")
    analyzed = samples[protocol["pilot_discard"]:]
    if len(analyzed) != 80:
        raise BenchmarkError("pilot discard must leave 80 samples")
    mean = sum(analyzed) / len(analyzed)
    if not math.isfinite(mean) or mean <= 0:
        raise BenchmarkError("pilot mean must be finite and positive")
    target = max(protocol["minimum_measured_frames"], math.ceil(protocol["target_measured_duration_ms"] / mean))
    raw_total = protocol["formal_warmup"] + target
    formal_total = math.ceil(raw_total / protocol["corpus_size"]) * protocol["corpus_size"]
    return {"pilot_sample_count": len(samples), "pilot_discard_count": protocol["pilot_discard"],
            "pilot_analyzed_count": len(analyzed), "pilot_mean_pre_sink_total_ms": mean,
            "target_measured_frames": target, "raw_total_frames": raw_total,
            "formal_total_frames": formal_total, "formal_measured_frames": formal_total - protocol["formal_warmup"]}


def type7_quantile(values: Iterable[float], probability: float) -> float:
    samples = [float(x) for x in values]
    if not samples or not 0.0 <= probability <= 1.0 or any(not math.isfinite(x) for x in samples):
        raise BenchmarkError("Type 7 requires finite non-empty values and p in [0,1]")
    ordered = sorted(samples)
    h = (len(ordered) - 1) * probability
    lower, upper = math.floor(h), math.ceil(h)
    return ordered[lower] + (h - lower) * (ordered[upper] - ordered[lower])


def sample_stddev(values: Iterable[float]) -> float:
    samples = [float(x) for x in values]
    if len(samples) < 2 or any(not math.isfinite(x) for x in samples):
        raise BenchmarkError("sample standard deviation requires at least two finite values")
    mean = sum(samples) / len(samples)
    return math.sqrt(sum((x - mean) ** 2 for x in samples) / (len(samples) - 1))


def summarize_values(values: Iterable[float]) -> dict[str, float | int]:
    samples = [finite_nonnegative(x, "statistic sample") for x in values]
    if len(samples) < 2:
        raise BenchmarkError("statistics require at least two samples")
    return {"sample_count": len(samples), "mean": sum(samples) / len(samples), "minimum": min(samples),
            "maximum": max(samples), "P50": type7_quantile(samples, 0.50), "P95": type7_quantile(samples, 0.95),
            "P99": type7_quantile(samples, 0.99), "sample_standard_deviation": sample_stddev(samples)}


def deterministic_gzip(data: bytes) -> bytes:
    import io
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", filename="", compresslevel=9, mtime=0) as gz:
        gz.write(data)
    return stream.getvalue()


def gzip_file_deterministic(source: Path, destination: Path) -> tuple[str, str]:
    raw = source.read_bytes()
    compressed = deterministic_gzip(raw)
    destination.write_bytes(compressed)
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as gz:
        if gz.read() != raw:
            raise EvidenceError("gzip round-trip changed raw application JSON")
    return sha256_bytes(raw), sha256_bytes(compressed)


def select_lowest_cpu(allowed: Iterable[int]) -> int:
    values = sorted(set(allowed))
    if not values:
        raise PreflightError("allowed CPU set is empty")
    return values[0]


def set_cpu_affinity(cpu: int, allowed: Iterable[int] | None = None) -> set[int]:
    before = set(os.sched_getaffinity(0) if allowed is None else allowed)
    if cpu not in before:
        raise PreflightError("selected CPU is not in allowed affinity")
    try:
        os.sched_setaffinity(0, {cpu})
        effective = set(os.sched_getaffinity(0))
    except (AttributeError, OSError) as exc:
        raise PreflightError(f"cannot set CPU affinity: {exc}") from exc
    if effective != {cpu}:
        raise PreflightError("effective CPU affinity does not match selected CPU")
    return effective


def collect_environment(*, selected_cpu: int | None = None, binary_sha256: str | None = None,
                        model_sha256: str | None = None, model_contract_sha256: str | None = None,
                        runtime_config_sha256: str | None = None,
                        effective_affinity: Iterable[int] | None = None) -> dict[str, Any]:
    try:
        allowed = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        allowed = []
    memory = None
    try:
        memory = int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    except (AttributeError, OSError, ValueError):
        pass
    libc_name, libc_version = platform.libc_ver()
    return {"schema_version": 1, "baseline_name": "WSL2 x86_64 ONNX Runtime CPU Engineering Baseline",
            "OS": platform.platform(), "WSL_kernel": platform.release(), "architecture": platform.machine(),
            "CPU_model": platform.processor() or "unknown", "visible_logical_cpu_count": os.cpu_count(),
            "allowed_affinity_before": allowed, "selected_cpu": selected_cpu,
            "effective_affinity": sorted(set(effective_affinity)) if effective_affinity is not None
            else sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else [],
            "memory_total_bytes": memory, "python_version": platform.python_version(),
            "python_executable_semantics": ".venv/bin/python", "binary_sha256": binary_sha256,
            "model_sha256": model_sha256, "model_contract_sha256": model_contract_sha256,
            "runtime_config_sha256": runtime_config_sha256,
            "python_package_versions": {}, "GCC_version": None, "CMake_version": None,
            "glibc": f"{libc_name} {libc_version}".strip(), "C++_OpenCV_version": None,
            "Python_OpenCV_version": None, "ONNX_Runtime_C++_version": "1.23.2",
            "ONNX_Runtime_Python_version": None, "CMAKE_BUILD_TYPE": "Release",
            "compile_flags": None, "SessionOptions": {"execution_provider": "CPUExecutionProvider",
                "execution_mode": "ORT_SEQUENTIAL", "graph_optimization": "ORT_ENABLE_ALL",
                "intra_op_num_threads": 1, "inter_op_num_threads": 1, "cpu_arena": True},
            "cache_policy": "warm-cache; caches not dropped",
            "limitations": ["WSL2", "warm-cache", "caches not dropped", "Windows host load uncontrolled",
                             "CPU frequency/governor not fixed", "not a Jetson result", "not used for TensorRT speedup"]}


def atomic_publish(staging: Path, target: Path) -> None:
    if target.exists():
        raise EvidenceError("evidence target already exists")
    if not staging.is_dir():
        raise EvidenceError("evidence staging directory does not exist")
    staging.rename(target)
