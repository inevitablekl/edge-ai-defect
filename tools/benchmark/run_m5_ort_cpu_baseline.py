#!/usr/bin/env python3
"""M5.3 benchmark orchestrator.

The default CLI is preflight-only.  Formal execution is intentionally explicit
and keeps all frozen protocol values internal to this module.  Tests inject a
subprocess function and clock/sleep function, so no unit test waits 30 seconds
or launches a real five-run benchmark.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from m5_ort_cpu_analyze import analyze_run
from m5_ort_cpu_common import (
    MANIFEST,
    PROTOCOL,
    BenchmarkError,
    EvidenceError,
    PreflightError,
    atomic_publish,
    build_workload,
    collect_environment,
    compute_formal_frame_counts,
    gzip_file_deterministic,
    load_benchmark_manifest,
    prepare_single_cycle,
    repo_relative,
    select_lowest_cpu,
    set_cpu_affinity,
    sha256_file,
    stable_json_bytes,
    validate_prepared_cycle,
    write_stable_json,
)


EXIT_SUCCESS = 0
EXIT_CLI = 2
EXIT_PREFLIGHT = 3
EXIT_RUN = 4
EXIT_EVIDENCE = 5


@dataclass(frozen=True)
class ProcessRecord:
    phase: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    pid: int | None = None


def frozen_protocol() -> dict[str, Any]:
    return copy.deepcopy(PROTOCOL)


def build_runtime_config(contract_path: Path, model_path: Path, input_dir: Path,
                         output_json: Path) -> dict[str, Any]:
    """Build the existing RuntimeConfig schema; benchmark knobs do not enter it."""
    return {"schema_version": 1,
            "backend": {"type": "onnxruntime_cpu"},
            "model": {"contract_path": str(contract_path), "model_path": str(model_path)},
            "input": {"type": "directory", "directory": str(input_dir)},
            "output": {"json_path": str(output_json), "console": False, "overwrite": True},
            "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000,
                            "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False},
            "timing": {"enabled": True}}


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise PreflightError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def check_preflight(dataset_root: Path, cpp_executable: Path, build_dir: Path,
                    output_root: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    branch = _git(root, "branch", "--show-current")
    commit = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--short")
    if status:
        raise PreflightError("worktree must be clean")
    upstream = _git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    divergence = _git(root, "rev-list", "--left-right", "--count", "@{upstream}...HEAD").split()
    if len(divergence) != 2 or int(divergence[0]) != 0:
        raise PreflightError("upstream must be resolvable and behind must be zero")
    if not cpp_executable.is_file() or not os.access(cpp_executable, os.X_OK):
        raise PreflightError("C++ binary must be a regular executable")
    if not build_dir.is_dir():
        raise PreflightError("build directory is missing")
    cache = build_dir / "CMakeCache.txt"
    cache_text = cache.read_text(encoding="utf-8") if cache.is_file() else ""
    required = ["CMAKE_BUILD_TYPE:STRING=Release", "EDGE_AI_ENABLE_MODEL_SMOKE:BOOL=ON",
                f"EDGE_AI_FROZEN_ONNX_PATH:FILEPATH={root / 'models/onnx/yolov8n_neudet_frozen.onnx'}"]
    if any(item not in cache_text for item in required):
        raise PreflightError("build must be Release with Model Smoke ON")
    if not dataset_root.is_dir() or dataset_root.is_symlink():
        raise PreflightError("dataset root must be a real directory")
    manifest = load_benchmark_manifest()
    source_sha = sha256_file(root / "configs/model_contracts/yolov8n_neudet_frozen.yaml")
    onnx_sha = sha256_file(root / "models/onnx/yolov8n_neudet_frozen.onnx")
    if output_root.exists() and any(output_root.iterdir()):
        raise PreflightError("benchmark output root must be empty for a new evidence set")
    try:
        allowed = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError) as exc:
        raise PreflightError(f"CPU affinity is unavailable: {exc}") from exc
    selected = select_lowest_cpu(allowed)
    return {"branch": branch, "source_commit": commit, "upstream": upstream,
            "upstream_behind": int(divergence[0]), "upstream_ahead": int(divergence[1]),
            "binary_sha256": sha256_file(cpp_executable), "model_contract_sha256": source_sha,
            "onnx_sha256": onnx_sha, "manifest": manifest, "allowed_cpus": allowed,
            "selected_cpu": selected, "platform": platform.system() + " " + platform.machine()}


def invoke_application(executable: Path, config: Path, *, cwd: Path,
                       runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> ProcessRecord:
    command = [str(executable), "--config", str(config)]
    result = runner(command, cwd=str(cwd), text=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=False)
    return ProcessRecord("application", command, int(result.returncode), result.stdout or "", result.stderr or "",
                         getattr(result, "pid", None))


def execute_process_sequence(commands: Sequence[Sequence[str]], *, invoke: Callable[..., Any] = subprocess.run,
                             sleep_fn: Callable[[float], None] = time.sleep,
                             cwd: Path | None = None) -> list[ProcessRecord]:
    """Run pilot + five independent formal invocations with four waits."""
    if len(commands) != 6:
        raise BenchmarkError("process sequence must contain one pilot and five formal commands")
    records: list[ProcessRecord] = []
    for index, command in enumerate(commands):
        phase = "pilot" if index == 0 else f"formal_run_{index}"
        result = invoke(list(command), cwd=str(cwd) if cwd else None, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        record = ProcessRecord(phase, list(command), int(result.returncode), result.stdout or "", result.stderr or "",
                               getattr(result, "pid", None))
        records.append(record)
        if record.returncode != 0:
            raise BenchmarkError(f"{phase} application exited {record.returncode}")
        if 1 <= index <= 4:
            sleep_fn(PROTOCOL["inter_run_wait_seconds"])
    return records


def execute_formal_runs(commands: Sequence[Sequence[str]], *, invoke: Callable[..., Any] = subprocess.run,
                        sleep_fn: Callable[[float], None] = time.sleep,
                        cwd: Path | None = None) -> list[ProcessRecord]:
    return execute_process_sequence(commands, invoke=invoke, sleep_fn=sleep_fn, cwd=cwd)


def stage_evidence(parent: Path, evidence_id: str, files: Mapping[str, bytes | str | Path], *,
                   max_bytes: int = 25 * 1024 * 1024) -> Path:
    """Atomically publish a fully prepared evidence tree; target must not exist."""
    target = parent / evidence_id
    if target.exists():
        raise EvidenceError("evidence target already exists")
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{evidence_id}.", dir=str(parent)))
    try:
        for relative, value in files.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(value, Path):
                shutil.copyfile(value, path)
            elif isinstance(value, bytes):
                path.write_bytes(value)
            else:
                path.write_text(value, encoding="utf-8", newline="\n")
        size = sum(path.stat().st_size for path in staging.rglob("*") if path.is_file())
        if size > max_bytes:
            raise EvidenceError("evidence exceeds 25 MiB")
        for path in staging.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                raise EvidenceError("evidence must not contain image assets")
        raw_json = [path for path in staging.rglob("raw_application.json") if path.is_file()]
        if raw_json:
            raise EvidenceError("uncompressed raw application JSON is forbidden in evidence")
        if "sha256sums.txt" not in files:
            checks = []
            for path in sorted((item for item in staging.rglob("*") if item.is_file()), key=lambda item: item.relative_to(staging).as_posix()):
                relative = path.relative_to(staging).as_posix()
                checks.append(f"{sha256_file(path)}  {relative}")
            (staging / "sha256sums.txt").write_text("\n".join(checks) + "\n", encoding="utf-8", newline="\n")
        target_parent = target.parent
        staging.rename(target)
        return target
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M5 WSL2 ORT CPU baseline harness (formal protocol frozen).")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--cpp-executable", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--development-smoke", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.development_smoke and "results/benchmark/ort_cpu" in args.output_root.as_posix():
            raise PreflightError("development smoke cannot write formal benchmark results")
        result = check_preflight(args.dataset_root, args.cpp_executable, args.build_dir, args.output_root)
        print("NON-FORMAL DEVELOPMENT SMOKE" if args.development_smoke else "preflight PASS")
        if args.check_only or args.development_smoke:
            return EXIT_SUCCESS
        raise PreflightError("formal execution is reserved for M5.4")
    except SystemExit as exc:
        return int(exc.code)
    except PreflightError as exc:
        print(f"preflight error: {exc}", file=sys.stderr)
        return EXIT_PREFLIGHT
    except BenchmarkError as exc:
        print(f"benchmark error: {exc}", file=sys.stderr)
        return EXIT_RUN
    except Exception as exc:  # pragma: no cover
        print(f"internal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
