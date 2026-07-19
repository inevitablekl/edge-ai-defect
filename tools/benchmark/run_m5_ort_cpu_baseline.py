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
import datetime as _datetime
import json
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
    read_strict_json,
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
    wall_clock_seconds: float = 0.0


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
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise PreflightError("formal baseline requires Linux x86_64")
    release = platform.release()
    if "microsoft" not in release.lower() and "wsl" not in release.lower():
        raise PreflightError("formal baseline requires a WSL2 kernel")
    manifest = load_benchmark_manifest()
    source_sha = sha256_file(root / "configs/model_contracts/yolov8n_neudet_frozen.yaml")
    onnx_sha = sha256_file(root / "models/onnx/yolov8n_neudet_frozen.onnx")
    if output_root.exists() and output_root.is_file():
        raise PreflightError("benchmark output root must be a directory")
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


def invoke_application(executable: Path, config: Path, *, cwd: Path, selected_cpu: int | None = None,
                       runner: Callable[..., subprocess.CompletedProcess[str]] | None = None) -> ProcessRecord:
    command = [str(executable), "--config", str(config)]
    started = time.monotonic()
    if runner is None:
        preexec = (lambda: set_cpu_affinity(selected_cpu)) if selected_cpu is not None else None
        process = subprocess.Popen(command, cwd=str(cwd), text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, preexec_fn=preexec)
        stdout, stderr = process.communicate()
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        pid = process.pid
    else:
        result = runner(command, cwd=str(cwd), text=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, check=False)
        pid = getattr(result, "pid", None)
    return ProcessRecord("application", command, int(result.returncode), result.stdout or "", result.stderr or "",
                         pid, time.monotonic() - started)


def execute_process_sequence(commands: Sequence[Sequence[str]], *, invoke: Callable[..., Any] = subprocess.run,
                             sleep_fn: Callable[[float], None] = time.sleep,
                             cwd: Path | None = None,
                             protocol: Mapping[str, Any] = PROTOCOL) -> list[ProcessRecord]:
    """Run pilot + five independent formal invocations with four waits."""
    if len(commands) != 6:
        raise BenchmarkError("process sequence must contain one pilot and five formal commands")
    records: list[ProcessRecord] = []
    for index, command in enumerate(commands):
        phase = "pilot" if index == 0 else f"formal_run_{index}"
        started = time.monotonic()
        result = invoke(list(command), cwd=str(cwd) if cwd else None, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        record = ProcessRecord(phase, list(command), int(result.returncode), result.stdout or "", result.stderr or "",
                               getattr(result, "pid", None), time.monotonic() - started)
        records.append(record)
        if record.returncode != 0:
            raise BenchmarkError(f"{phase} application exited {record.returncode}")
        if 1 <= index <= 4:
            sleep_fn(protocol["inter_run_wait_seconds"])
    return records


def execute_formal_runs(commands: Sequence[Sequence[str]], *, invoke: Callable[..., Any] = subprocess.run,
                        sleep_fn: Callable[[float], None] = time.sleep,
                        cwd: Path | None = None,
                        protocol: Mapping[str, Any] = PROTOCOL) -> list[ProcessRecord]:
    return execute_process_sequence(commands, invoke=invoke, sleep_fn=sleep_fn, cwd=cwd, protocol=protocol)


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


def _portable_path(value: str | Path, root: Path) -> str:
    path = Path(value)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "<temporary>/" + path.name if path.is_absolute() else path.as_posix()


def _portable_command(command: Sequence[str], root: Path) -> list[str]:
    return [_portable_path(item, root) if Path(item).is_absolute() else item for item in command]


def _write_runtime_config(path: Path, config: Mapping[str, Any]) -> None:
    # JSON is a strict YAML 1.2 subset and keeps temporary configs deterministic.
    path.write_bytes(stable_json_bytes(config))


def _verify_sha256sums(directory: Path) -> None:
    sums = directory / "sha256sums.txt"
    if not sums.is_file():
        raise EvidenceError("sha256sums.txt is missing")
    for line in sums.read_text(encoding="utf-8").splitlines():
        digest, separator, relative = line.partition("  ")
        if separator != "  " or len(digest) != 64:
            raise EvidenceError("invalid sha256sums.txt line")
        path = directory / relative
        if not path.is_file() or sha256_file(path) != digest:
            raise EvidenceError(f"sha256 mismatch: {relative}")


def _existing_source_evidence(output_root: Path, source_commit: str) -> bool:
    if not output_root.is_dir():
        return False
    for provenance in output_root.rglob("provenance.json"):
        try:
            value = read_strict_json(provenance)
        except BenchmarkError:
            continue
        if isinstance(value, dict) and value.get("source_commit") == source_commit:
            return True
    return False


def run_formal_orchestrator(
    dataset_root: Path,
    cpp_executable: Path,
    build_dir: Path,
    output_root: Path,
    *,
    repo_root: Path | None = None,
    work_root: Path | None = None,
    preflight_fn: Callable[..., Mapping[str, Any]] = check_preflight,
    prepare_cycle_fn: Callable[[Path, Path], Any] = prepare_single_cycle,
    build_workload_fn: Callable[..., Mapping[str, Any]] = build_workload,
    invoke_fn: Callable[[Sequence[str], Path, int], ProcessRecord] | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    clock_fn: Callable[[], float] = time.monotonic,
    environment_fn: Callable[..., Mapping[str, Any]] = collect_environment,
    date_fn: Callable[[], str] | None = None,
    protocol: Mapping[str, Any] = PROTOCOL,
) -> dict[str, Any]:
    """Execute the complete formal path; all side effects remain in work/evidence staging."""
    if dict(protocol) != dict(PROTOCOL):
        # Internal tests may inject a short protocol, but the public CLI never does.
        formal_protocol = dict(protocol)
    else:
        formal_protocol = frozen_protocol()
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    info = dict(preflight_fn(dataset_root, cpp_executable, build_dir, output_root, repo_root=root))
    source_commit = str(info["source_commit"])
    if _existing_source_evidence(output_root, source_commit):
        raise EvidenceError("formal evidence already exists for this source commit")
    short_commit = source_commit[:7]
    evidence_date = date_fn() if date_fn is not None else _datetime.datetime.now().strftime("%Y%m%d")
    evidence_id = f"{evidence_date}_{short_commit}"
    if (output_root / evidence_id).exists():
        raise EvidenceError("formal evidence target already exists")

    owned_work = work_root is None
    if work_root is None:
        work_root = root / "build-m5-4-formal-work" / evidence_id
    work_root = Path(work_root)
    if work_root.exists():
        raise EvidenceError("formal work directory already exists")
    work_root.mkdir(parents=True)
    single_cycle = work_root / "single_cycle"
    pilot_workload = work_root / "pilot_workload"
    formal_workload = work_root / "formal_workload"
    prepare_cycle_fn(dataset_root, single_cycle)
    validate_prepared_cycle(single_cycle)
    pilot_manifest = build_workload_fn(single_cycle, pilot_workload, formal_protocol["pilot_frames"], formal=False)

    selected_cpu = int(info["selected_cpu"])
    records: list[ProcessRecord] = []
    command_records: list[dict[str, Any]] = []

    def app_invoke(command: Sequence[str], phase: str) -> ProcessRecord:
        started = clock_fn()
        if invoke_fn is not None:
            record = invoke_fn(command, work_root, selected_cpu)
        else:
            record = invoke_application(Path(command[0]), Path(command[2]), cwd=work_root,
                                        selected_cpu=selected_cpu)
        elapsed = clock_fn() - started
        if record.wall_clock_seconds == 0.0:
            record = ProcessRecord(record.phase, record.command, record.returncode, record.stdout,
                                   record.stderr, record.pid, elapsed)
        record = ProcessRecord(phase, list(record.command), record.returncode, record.stdout,
                               record.stderr, record.pid, record.wall_clock_seconds)
        records.append(record)
        command_records.append({"phase": phase, "command": _portable_command(record.command, root),
                                "exit_code": record.returncode, "pid": record.pid,
                                "wall_clock_seconds": record.wall_clock_seconds,
                                "stdout": record.stdout, "stderr": record.stderr})
        if record.returncode != 0:
            raise BenchmarkError(f"{phase} application exited {record.returncode}")
        return record

    pilot_dir = work_root / "pilot"
    pilot_raw = work_root / "pilot_raw_application.json"
    pilot_config = work_root / "pilot_runtime.yaml"
    _write_runtime_config(pilot_config, build_runtime_config(
        root / "configs/model_contracts/yolov8n_neudet_frozen.yaml",
        root / "models/onnx/yolov8n_neudet_frozen.onnx", pilot_workload, pilot_raw))
    pilot_record = app_invoke([str(cpp_executable), "--config", str(pilot_config)], "pilot")
    from m5_ort_cpu_analyze import parse_application_json
    pilot_parsed = parse_application_json(pilot_raw, pilot_manifest)
    if len(pilot_parsed["records"]) != formal_protocol["pilot_frames"]:
        raise BenchmarkError("pilot frame count is invalid")
    pilot_summary = analyze_run(pilot_raw, workload_manifest=pilot_manifest, run_index=0,
                                formal=False, output_dir=pilot_dir, protocol=formal_protocol,
                                process_exit_code=pilot_record.returncode,
                                process_wall_clock_seconds=pilot_record.wall_clock_seconds)
    pilot_mean = sum(item["pre_sink_total_ms"] for item in pilot_parsed["records"][formal_protocol["pilot_discard"]:]) / 80
    frame_counts = compute_formal_frame_counts(
        [item["pre_sink_total_ms"] for item in pilot_parsed["records"]], formal_protocol)
    build_workload_fn(single_cycle, formal_workload, frame_counts["formal_total_frames"], formal=True)

    run_summaries: list[dict[str, Any]] = []
    run_records: list[ProcessRecord] = []
    for run_index in range(1, formal_protocol["formal_run_count"] + 1):
        run_dir = work_root / f"run_{run_index:02d}"
        raw_path = work_root / f"run_{run_index:02d}_raw_application.json"
        config_path = work_root / f"run_{run_index:02d}_runtime.yaml"
        _write_runtime_config(config_path, build_runtime_config(
            root / "configs/model_contracts/yolov8n_neudet_frozen.yaml",
            root / "models/onnx/yolov8n_neudet_frozen.onnx", formal_workload, raw_path))
        record = app_invoke([str(cpp_executable), "--config", str(config_path)], f"formal_run_{run_index}")
        run_records.append(record)
        summary = analyze_run(raw_path, workload_manifest=read_strict_json(formal_workload / "workload_manifest.json"),
                              run_index=run_index, formal=True, output_dir=run_dir,
                              protocol=formal_protocol, process_exit_code=record.returncode,
                              process_wall_clock_seconds=record.wall_clock_seconds)
        run_summaries.append(summary)
        if run_index < formal_protocol["formal_run_count"]:
            sleep_fn(formal_protocol["inter_run_wait_seconds"])

    aggregate = __import__("m5_ort_cpu_analyze", fromlist=["aggregate_summaries"]).aggregate_summaries(
        run_summaries, source_commit=source_commit, protocol=formal_protocol)
    aggregate_path = work_root / "aggregate_summary.json"
    write_stable_json(aggregate_path, aggregate)
    protocol_path = work_root / "benchmark_protocol.json"
    write_stable_json(protocol_path, formal_protocol)
    env = dict(environment_fn(selected_cpu=selected_cpu, binary_sha256=info["binary_sha256"],
                              model_sha256=info["onnx_sha256"],
                              model_contract_sha256=info["model_contract_sha256"],
                              effective_affinity=[selected_cpu]))
    environment_path = work_root / "environment.json"
    write_stable_json(environment_path, env)
    provenance = {"schema_version": 1, "evidence_id": evidence_id, "source_commit": source_commit,
                  "branch": info["branch"], "upstream": info["upstream"],
                  "upstream_behind": info["upstream_behind"], "upstream_ahead": info["upstream_ahead"],
                  "worktree_clean": True, "binary_sha256": info["binary_sha256"],
                  "model_contract_sha256": info["model_contract_sha256"], "onnx_sha256": info["onnx_sha256"],
                  "benchmark_manifest_sha256": sha256_file(MANIFEST),
                  "protocol_sha256": sha256_file(protocol_path), "environment_sha256": sha256_file(environment_path),
                  "protocol": formal_protocol, "pilot": {"record": command_records[0],
                  "raw_sha256": pilot_summary["raw_application_uncompressed_sha256"],
                  "mean_pre_sink_total_ms": pilot_mean, "frame_counts": frame_counts},
                  "formal_runs": [{"record": command_records[index],
                                   "raw_sha256": summary["raw_application_uncompressed_sha256"],
                                   "compressed_sha256": summary["raw_application_compressed_sha256"],
                                   "timings_sha256": summary["timings_tsv_sha256"],
                                   "summary_sha256": sha256_file(work_root / f"run_{index:02d}" / "summary.json"),
                                   "measured_count": summary["measured_frame_count"],
                                   "measured_duration_ms": summary["measured_pre_sink_duration_ms"],
                                   "status": summary["status"]}
                                  for index, summary in enumerate(run_summaries, start=1)],
                  "waits_seconds": [formal_protocol["inter_run_wait_seconds"]] * (formal_protocol["formal_run_count"] - 1),
                  "aggregate_sha256": sha256_file(aggregate_path), "outlier_policy": formal_protocol["outlier_policy"]}
    provenance_path = work_root / "provenance.json"
    write_stable_json(provenance_path, provenance)
    commands_lines = [f"{item['phase']}: {' '.join(item['command'])} exit={item['exit_code']} pid={item['pid']}"
                      for item in command_records]
    (work_root / "commands.txt").write_text("\n".join(commands_lines) + "\n", encoding="utf-8", newline="\n")
    (work_root / "README.txt").write_text(
        "WSL2 x86_64 ONNX Runtime CPU Engineering Baseline\n"
        "Formal five-run evidence; not a Jetson or TensorRT result.\n", encoding="utf-8", newline="\n")
    files: dict[str, Path | bytes | str] = {
        "README.txt": work_root / "README.txt", "benchmark_corpus_manifest.json": MANIFEST,
        "benchmark_protocol.json": protocol_path, "environment.json": environment_path,
        "provenance.json": provenance_path, "commands.txt": work_root / "commands.txt",
        "aggregate_summary.json": aggregate_path,
        "pilot/raw_application.json.gz": pilot_dir / "raw_application.json.gz",
        "pilot/summary.json": pilot_dir / "summary.json", "pilot/command.txt": " ".join(command_records[0]["command"]) + "\n",
        "pilot/exit_code.txt": f"{pilot_record.returncode}\n",
    }
    for run_index in range(1, formal_protocol["formal_run_count"] + 1):
        run_dir = work_root / f"run_{run_index:02d}"
        record = run_records[run_index - 1]
        files.update({f"run_{run_index:02d}/raw_application.json.gz": run_dir / "raw_application.json.gz",
                      f"run_{run_index:02d}/timings.tsv": run_dir / "timings.tsv",
                      f"run_{run_index:02d}/summary.json": run_dir / "summary.json",
                      f"run_{run_index:02d}/command.txt": " ".join(_portable_command(record.command, root)) + "\n",
                      f"run_{run_index:02d}/exit_code.txt": f"{record.returncode}\n"})
    published = stage_evidence(output_root, evidence_id, files)
    _verify_sha256sums(published)
    return {"evidence_id": evidence_id, "evidence_path": published, "preflight": info,
            "pilot_summary": pilot_summary, "frame_counts": frame_counts,
            "run_summaries": run_summaries, "aggregate": aggregate,
            "command_records": command_records, "waits_seconds": [formal_protocol["inter_run_wait_seconds"]] * 4,
            "environment": env, "source_commit": source_commit, "work_root": work_root,
            "owned_work": owned_work}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="M5 WSL2 ORT CPU baseline harness (formal protocol frozen).")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--cpp-executable", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check-only", action="store_true")
    modes.add_argument("--development-smoke", action="store_true")
    modes.add_argument("--formal", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.development_smoke and "results/benchmark/ort_cpu" in args.output_root.as_posix():
            raise PreflightError("development smoke cannot write formal benchmark results")
        if args.check_only or args.development_smoke:
            check_preflight(args.dataset_root, args.cpp_executable, args.build_dir, args.output_root)
            print("NON-FORMAL DEVELOPMENT SMOKE" if args.development_smoke else "preflight PASS")
            return EXIT_SUCCESS
        result = run_formal_orchestrator(args.dataset_root, args.cpp_executable, args.build_dir,
                                         args.output_root)
        print(f"formal PASS: {result['evidence_id']}")
        return EXIT_SUCCESS
    except SystemExit as exc:
        return int(exc.code)
    except PreflightError as exc:
        print(f"preflight error: {exc}", file=sys.stderr)
        return EXIT_PREFLIGHT
    except EvidenceError as exc:
        print(f"evidence error: {exc}", file=sys.stderr)
        return EXIT_EVIDENCE
    except BenchmarkError as exc:
        print(f"benchmark error: {exc}", file=sys.stderr)
        return EXIT_RUN
    except Exception as exc:  # pragma: no cover
        print(f"internal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
