#!/usr/bin/env python3
"""Stage J v2 formal baseline orchestrator.

The public default is preflight-only.  The formal path is reachable only with
--execute-formal, --profile k5 and a new --evidence-id.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from m5_ort_cpu_common import (
    BenchmarkError,
    EvidenceError,
    PreflightError,
    atomic_publish,
    read_strict_json,
    sha256_file,
    stable_json_bytes,
    write_stable_json,
)
from stage_j_ort_cpu_analyze import (
    PROTOCOL,
    aggregate_formal_runs,
    analyze_formal_run,
    formal_frames_from_pilot,
    parse_benchmark_result,
    verify_cycle_correctness,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_BRANCH = "feature/jetson-onnxruntime"
CPU_SET = {1, 2, 3, 4, 5}
FROZEN_SHA = {
    "model": "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944",
    "contract": "9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190",
    "corpus_manifest": "235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab",
    "python_reference": "1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7",
    "expected_cycle": "dff5686b46de48416d9038ccc40b573eb1c59830ba9e96eac5becbdb6bb0746f",
}
EXPECTED_EXTERNAL_ARTIFACT_SHA256 = {
    "stage_j_profile_runner":
        "e5a69f3be8f64ed0ac086148998040e8380f4eb2610ae1959829ca215829c725",
    "edge_ai_defect":
        "bd02668f345dd0c232a0a84f64309d0b04017b177c33cbd29e32fcf45f114014",
}


def _git(*arguments: str, root: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise PreflightError(f"git {' '.join(arguments)} failed")
    return result.stdout.strip()


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (ImportError, OSError, UnicodeError, ValueError) as exc:
        raise PreflightError(f"cannot load RuntimeConfig: {exc}") from exc
    if not isinstance(value, dict):
        raise PreflightError("RuntimeConfig root must be a mapping")
    return value


def validate_profile(
    config: Mapping[str, Any],
    *,
    profile: str | None,
    cpu_set: set[int] = CPU_SET,
) -> None:
    if profile is not None and profile != "k5":
        raise PreflightError("only profile k5 is authorized")
    if cpu_set != CPU_SET:
        raise PreflightError("k5 CPU set must be exactly 1-5")
    try:
        valid = (
            config["schema_version"] == 2
            and config["backend"]["type"] == "onnxruntime_cpu"
            and config["onnxruntime"]["execution_mode"] == "sequential"
            and config["onnxruntime"]["intra_op_threads"] == 5
            and config["onnxruntime"]["inter_op_threads"] == 1
            and config["runtime"]["opencv_num_threads"] == 1
            and "timing" not in config
        )
    except (KeyError, TypeError):
        valid = False
    if not valid:
        raise PreflightError("RuntimeConfig is not the frozen Stage J k5 v2 profile")


def validate_asset_shas(paths: Mapping[str, Path]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, expected in FROZEN_SHA.items():
        path = paths.get(name)
        if path is None or not path.is_file():
            raise PreflightError(f"{name} asset is missing")
        observed[name] = sha256_file(path)
        if observed[name] != expected:
            raise PreflightError(f"{name} SHA drift")
    return observed


def validate_formal_platform(
    *,
    system: str | None = None,
    machine: str | None = None,
    model_text: str | None = None,
    nvpmodel_text: str | None = None,
    clocks_text: str | None = None,
    manual_verification_text: str | None = None,
) -> dict[str, str]:
    system = platform.system() if system is None else system
    machine = platform.machine() if machine is None else machine
    if system != "Linux" or machine != "aarch64":
        raise PreflightError("formal execution requires Linux aarch64")
    if model_text is None:
        try:
            model_text = Path("/proc/device-tree/model").read_text(
                encoding="utf-8", errors="replace").rstrip("\x00")
        except OSError as exc:
            raise PreflightError(f"cannot read Jetson model: {exc}") from exc
    if "Jetson Orin Nano" not in model_text:
        raise PreflightError("formal execution requires the frozen Jetson Orin Nano platform")
    if manual_verification_text is not None:
        required = (
            "manual platform verification",
            "Jetson Orin Nano",
            "R36.5",
            "0-5 online",
            "GPU",
            "EMC",
            "MAXN_SUPER",
            "FAN Dynamic Speed Control=disabled",
            "hwmon0_pwm1=255",
            "sudo jetson_clocks --show",
            "sudo nvpmodel -q",
        )
        if any(item not in manual_verification_text for item in required):
            raise PreflightError("manual platform verification is incomplete")
        return {"source": "manual_platform_verification"}
    if nvpmodel_text is None:
        result = subprocess.run(
            ["nvpmodel", "-q"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False)
        nvpmodel_text = result.stdout
        if result.returncode:
            raise PreflightError("nvpmodel query failed")
    if "MAXN_SUPER" not in nvpmodel_text:
        raise PreflightError("MAXN_SUPER is not active")
    if clocks_text is None:
        result = subprocess.run(
            ["jetson_clocks", "--show"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False)
        clocks_text = result.stdout
        if result.returncode:
            raise PreflightError("jetson_clocks state query failed")
    if "FreqOverride=1" not in clocks_text and "FreqOverride: 1" not in clocks_text:
        raise PreflightError("jetson_clocks locked state is not visible")
    if "FAN Dynamic Speed Control=disabled" not in clocks_text:
        raise PreflightError("jetson_clocks fan control is not frozen")
    return {"source": "live_read_only_platform_query"}


def parse_cpu_list(value: str) -> set[int]:
    result: set[int] = set()
    try:
        for component in value.strip().split(","):
            bounds = component.split("-", 1)
            first = int(bounds[0])
            last = int(bounds[-1])
            if first < 0 or last < first:
                raise ValueError
            result.update(range(first, last + 1))
    except ValueError as exc:
        raise BenchmarkError(f"invalid Linux CPU list: {value!r}") from exc
    if not result:
        raise BenchmarkError("Linux CPU list is empty")
    return result


def _read_status(path: Path) -> tuple[str, set[int], int | None]:
    text = path.read_text(encoding="utf-8")
    fields = {}
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key] = value.strip()
    affinity = parse_cpu_list(fields["Cpus_allowed_list"])
    vmrss = None
    if "VmRSS" in fields:
        parts = fields["VmRSS"].split()
        vmrss = int(parts[0])
    return fields.get("Name", "unknown"), affinity, vmrss


def sample_process_threads(pid: int) -> list[dict[str, Any]]:
    samples = []
    for status in sorted(
            Path(f"/proc/{pid}/task").glob("*/status"),
            key=lambda item: int(item.parent.name)):
        try:
            name, affinity, _ = _read_status(status)
        except (OSError, KeyError, ValueError, BenchmarkError):
            continue
        samples.append({
            "monotonic_ns": time.monotonic_ns(),
            "tid": int(status.parent.name),
            "name": name,
            "cpus_allowed": sorted(affinity),
        })
    return samples


def system_snapshot(previous_cpu: tuple[int, int] | None = None) -> tuple[dict[str, Any], tuple[int, int]]:
    cpu_values = []
    for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if fields and re.fullmatch(r"cpu[1-5]", fields[0]):
            cpu_values.append([int(value) for value in fields[1:8]])
    total = sum(sum(values) for values in cpu_values)
    idle = sum(values[3] + values[4] for values in cpu_values)
    utilization = None
    if previous_cpu is not None:
        delta_total = total - previous_cpu[0]
        delta_idle = idle - previous_cpu[1]
        if delta_total > 0:
            utilization = 100.0 * (delta_total - delta_idle) / delta_total
    memory: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition(":")
        if separator and key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
            memory[key] = int(value.split()[0])
    temperatures = {}
    for type_path in Path("/sys/class/thermal").glob("thermal_zone*/type"):
        try:
            zone_type = type_path.read_text(encoding="utf-8").strip()
            temperatures[zone_type] = int((type_path.parent / "temp").read_text())
        except (OSError, ValueError):
            continue
    frequencies = {}
    for frequency_path in Path("/sys/devices/system/cpu").glob(
            "cpufreq/policy*/scaling_cur_freq"):
        try:
            frequencies[frequency_path.parent.parent.name] = int(
                frequency_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    snapshot = {
        "monotonic_ns": time.monotonic_ns(),
        "cpu_utilization_percent_cpu1_5": utilization,
        "ram_kb": memory,
        "temperature_millicelsius": temperatures,
        "cpu_frequency_khz": frequencies,
    }
    return snapshot, (total, idle)


def check_preflight(
    *,
    runner: Path,
    config_template: Path,
    asset_paths: Mapping[str, Path],
    profile: str | None,
    execute_formal: bool,
    evidence_target: Path | None = None,
    local_attempt_target: Path | None = None,
    production_executable: Path | None = None,
    platform_verification: Path | None = None,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    if _git("branch", "--show-current", root=repo_root) != EXPECTED_BRANCH:
        raise PreflightError("unexpected branch")
    if _git("status", "--porcelain=v1", root=repo_root):
        raise PreflightError("worktree must be clean")
    commit = _git("rev-parse", "HEAD", root=repo_root)
    if not runner.is_file() or not os.access(runner, os.X_OK):
        raise PreflightError("stage_j_profile_runner is not executable")
    production = production_executable or runner.parent / "edge_ai_defect"
    if not production.is_file() or not os.access(production, os.X_OK):
        raise PreflightError("edge_ai_defect Release artifact is not executable")
    runner_sha = sha256_file(runner)
    production_sha = sha256_file(production)
    if runner_sha != EXPECTED_EXTERNAL_ARTIFACT_SHA256["stage_j_profile_runner"]:
        raise PreflightError("stage_j_profile_runner external artifact SHA drift")
    if production_sha != EXPECTED_EXTERNAL_ARTIFACT_SHA256["edge_ai_defect"]:
        raise PreflightError("edge_ai_defect external artifact SHA drift")
    config = _load_yaml(config_template)
    validate_profile(config, profile=profile)
    observed = validate_asset_shas(asset_paths)
    try:
        allowed = set(os.sched_getaffinity(0))
    except (AttributeError, OSError) as exc:
        raise PreflightError(f"CPU affinity unavailable: {exc}") from exc
    if not CPU_SET.issubset(allowed):
        raise PreflightError("CPU set 1-5 is not available")
    manual_text = None
    if platform_verification is not None:
        try:
            manual_text = platform_verification.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise PreflightError(f"cannot read manual platform verification: {exc}") from exc
    platform_info = validate_formal_platform(
        manual_verification_text=manual_text)
    if execute_formal:
        if profile != "k5":
            raise PreflightError("formal execution requires explicit --profile k5")
        for target in (evidence_target, local_attempt_target):
            if target is None or target.exists():
                raise PreflightError("formal output targets must be new")
        if not Path("/usr/bin/tegrastats").is_file():
            raise PreflightError("frozen /usr/bin/tegrastats is missing")
        try:
            online = parse_cpu_list(
                Path("/sys/devices/system/cpu/online").read_text(encoding="utf-8"))
        except OSError as exc:
            raise PreflightError(f"cannot read online CPU set: {exc}") from exc
        if online != {0, 1, 2, 3, 4, 5} or 0 not in allowed:
            raise PreflightError("frozen online/telemetry CPU set is unavailable")
    return {
        "status": "PASS",
        "branch": EXPECTED_BRANCH,
        "source_commit": commit,
        "profile": "k5",
        "cpu_set": [1, 2, 3, 4, 5],
        "asset_sha256": observed,
        "platform": platform_info,
        "build_artifact": {
            "scope": "external_verified_release_artifact",
            "stage_j_profile_runner": str(runner),
            "stage_j_profile_runner_sha256": runner_sha,
            "edge_ai_defect": str(production),
            "edge_ai_defect_sha256": production_sha,
        },
    }


def build_workload(corpus_dir: Path, target: Path, total_frames: int) -> dict[str, Any]:
    if total_frames <= 0 or total_frames % 20:
        raise BenchmarkError("workload frame count must be a positive multiple of 20")
    if target.exists():
        raise BenchmarkError("workload target already exists")
    manifest_path = corpus_dir / "benchmark_corpus_manifest.json"
    if sha256_file(manifest_path) != FROZEN_SHA["corpus_manifest"]:
        raise BenchmarkError("corpus manifest SHA drift")
    manifest = read_strict_json(manifest_path)
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != 20:
        raise BenchmarkError("frozen corpus must contain 20 entries")
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=str(target.parent)))
    workload_entries = []
    try:
        for sequence in range(total_frames):
            within = sequence % 20
            cycle = sequence // 20
            entry = entries[within]
            original = entry["prepared_filename"]
            source = corpus_dir / original
            expected = entry.get("prepared_sha256", entry.get("expected_sha256"))
            if not source.is_file() or source.is_symlink() or sha256_file(source) != expected:
                raise BenchmarkError(f"frozen corpus image mismatch: {original}")
            name = f"c{cycle:06d}_f{within:02d}_{original}"
            destination = staging / name
            try:
                os.link(source, destination)
            except OSError:
                shutil.copyfile(source, destination)
            if destination.is_symlink() or sha256_file(destination) != expected:
                raise BenchmarkError(f"staged workload image mismatch: {name}")
            workload_entries.append({
                "workload_sequence_index": sequence,
                "cycle_index": cycle,
                "within_cycle_index": within,
                "original_filename": original,
                "workload_filename": name,
                "sha256": expected,
            })
        output = {
            "schema_version": 1,
            "cycle_frames": 20,
            "total_frames": total_frames,
            "entries": workload_entries,
        }
        write_stable_json(staging / "workload_manifest.json", output)
        staging.rename(target)
        return output
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _runtime_config(template: Mapping[str, Any], workload: Path, output: Path) -> dict[str, Any]:
    config = copy.deepcopy(dict(template))
    config["input"]["directory"] = str(workload)
    config["output"]["json_path"] = str(output)
    config["output"]["console"] = False
    config["output"]["overwrite"] = False
    return config


def invoke_profile_runner(
    runner: Path,
    config: Path,
    trace: Path,
    *,
    cpu_set: set[int] = CPU_SET,
    formal_telemetry: bool = False,
) -> tuple[float, dict[str, Any]]:
    command = [str(runner), "--config", str(config), "--trace-jsonl", str(trace)]
    telemetry: dict[str, Any] = {
        "vmrss_kb_samples": [],
        "application_tid_affinity_samples": [],
        "telemetry_tid_affinity_samples": [],
        "tegrastats_lines": [],
        "system_samples": [],
    }
    tegrastats = None
    reader = None
    if formal_telemetry:
        if set(os.sched_getaffinity(0)) != {0}:
            raise BenchmarkError("formal telemetry wrapper must be pinned to CPU0")
        tegrastats = subprocess.Popen(
            ["/usr/bin/tegrastats", "--interval", "1000"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=lambda: os.sched_setaffinity(0, {0}))

        def collect_tegrastats() -> None:
            assert tegrastats is not None and tegrastats.stdout is not None
            for line in tegrastats.stdout:
                telemetry["tegrastats_lines"].append({
                    "realtime_ns": time.time_ns(),
                    "monotonic_ns": time.monotonic_ns(),
                    "raw": line.rstrip("\n"),
                    "vdd_in_mw": (
                        float(match.group(1)) if (match := re.search(
                            r"VDD_IN\s+(\d+(?:\.\d+)?)/", line)) else None),
                })

        reader = threading.Thread(target=collect_tegrastats, daemon=True)
        reader.start()
        time.sleep(3.0)
    started = time.monotonic()
    process = None
    process_ended = started
    previous_cpu = None
    try:
        process = subprocess.Popen(
            command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=lambda: os.sched_setaffinity(0, cpu_set))
        while process.poll() is None:
            try:
                _, process_affinity, vmrss = _read_status(
                    Path(f"/proc/{process.pid}/status"))
                if vmrss is not None:
                    telemetry["vmrss_kb_samples"].append(vmrss)
                if formal_telemetry:
                    snapshot, previous_cpu = system_snapshot(previous_cpu)
                    telemetry["system_samples"].append(snapshot)
                tid_samples = sample_process_threads(process.pid)
                telemetry["application_tid_affinity_samples"].extend(tid_samples)
                if not process_affinity.issubset(cpu_set):
                    raise BenchmarkError("application process affinity escaped k5")
                if any(not set(item["cpus_allowed"]).issubset(cpu_set)
                       for item in tid_samples):
                    raise BenchmarkError("application TID affinity escaped k5")
                if tegrastats is not None:
                    telemetry_samples = sample_process_threads(tegrastats.pid)
                    telemetry["telemetry_tid_affinity_samples"].extend(
                        telemetry_samples)
                    if any(set(item["cpus_allowed"]) != {0}
                           for item in telemetry_samples):
                        raise BenchmarkError("tegrastats TID affinity escaped CPU0")
            except (OSError, KeyError, ValueError):
                pass
            time.sleep(0.5 if formal_telemetry else 0.1)
        stdout, stderr = process.communicate()
        process_ended = time.monotonic()
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if tegrastats is not None:
            time.sleep(3.0)
            tegrastats.terminate()
            try:
                tegrastats.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                tegrastats.kill()
                tegrastats.wait()
            if reader is not None:
                reader.join(timeout=2.0)
    if process is None:
        raise BenchmarkError("profile runner could not be started")
    wall = process_ended - started
    if process.returncode:
        raise BenchmarkError(
            f"profile runner exited {process.returncode}: {stderr.strip()}")
    if stdout:
        raise BenchmarkError("profile runner unexpectedly wrote stdout")
    tid_samples = telemetry["application_tid_affinity_samples"]
    if not tid_samples or any(
            not set(sample["cpus_allowed"]).issubset(cpu_set)
            for sample in tid_samples):
        raise BenchmarkError("application affinity sampling failed")
    if formal_telemetry:
        lines = telemetry["tegrastats_lines"]
        if len(lines) < 2 or any(
                lines[index]["monotonic_ns"] - lines[index - 1]["monotonic_ns"]
                > 2_500_000_000 for index in range(1, len(lines))):
            raise BenchmarkError("tegrastats sampling coverage is invalid")
        if not telemetry["telemetry_tid_affinity_samples"]:
            raise BenchmarkError("tegrastats affinity was not sampled")
        if not telemetry["system_samples"]:
            raise BenchmarkError("system telemetry was not sampled")
        rail_names = ("VDD_IN", "VDD_CPU_GPU_CV", "VDD_SOC")
        if any(not any(name in item["raw"] for item in lines)
               for name in rail_names):
            raise BenchmarkError("frozen tegrastats rail set is missing")
    return wall, telemetry


def _execute_one(
    runner: Path,
    template: Mapping[str, Any],
    corpus: Path,
    run_dir: Path,
    total_frames: int,
    *,
    formal_telemetry: bool = False,
) -> tuple[dict[str, Any], float, dict[str, Any]]:
    run_dir.mkdir(parents=True)
    workload = run_dir / "workload"
    manifest = build_workload(corpus, workload, total_frames)
    result = run_dir / "result.json"
    trace = run_dir / "trace.jsonl"
    config = run_dir / "runtime.json"
    config.write_bytes(stable_json_bytes(_runtime_config(template, workload, result)))
    wall, telemetry = invoke_profile_runner(
        runner, config, trace, formal_telemetry=formal_telemetry)
    return parse_benchmark_result(result, trace, manifest), wall, telemetry


def execute_formal_campaign(
    *,
    runner: Path,
    config_template: Path,
    corpus: Path,
    expected_cycle_json: Path,
    local_attempt_target: Path,
    evidence_target: Path,
    source_commit: str,
) -> dict[str, Any]:
    """Run pilot + five processes and atomically publish validated summaries."""
    if local_attempt_target.exists() or evidence_target.exists():
        raise EvidenceError("formal target already exists")
    local_attempt_target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(
        prefix=f".{local_attempt_target.name}.", dir=str(local_attempt_target.parent)))
    original_affinity = set(os.sched_getaffinity(0))
    try:
        if 0 not in original_affinity:
            raise BenchmarkError("telemetry CPU0 is unavailable")
        os.sched_setaffinity(0, {0})
        template = _load_yaml(config_template)
        pilot, _, pilot_telemetry = _execute_one(
            runner, template, corpus, staging / "pilot", 260,
            formal_telemetry=True)
        verify_cycle_correctness(
            pilot["data"], expected_cycle_json, FROZEN_SHA["expected_cycle"])
        sizing = formal_frames_from_pilot(pilot["records"])
        total = int(sizing["formal_total_frames"])
        measured = int(sizing["formal_measured_frames"])
        summaries = []
        telemetry = [pilot_telemetry]
        for index in range(1, 6):
            run_dir = staging / f"run_{index:02d}"
            parsed, wall, samples = _execute_one(
                runner, template, corpus, run_dir, total,
                formal_telemetry=True)
            verify_cycle_correctness(
                parsed["data"], expected_cycle_json, FROZEN_SHA["expected_cycle"])
            summary = analyze_formal_run(
                parsed, measured, run_index=index, process_wall_seconds=wall)
            summary["payload_sha256"] = parsed["raw_sha256"]
            summary["trace_sha256"] = sha256_file(run_dir / "trace.jsonl")
            summary_path = run_dir / "summary.json"
            write_stable_json(summary_path, summary)
            summary["report_sha256"] = sha256_file(summary_path)
            summaries.append(summary)
            telemetry.append(samples)
        aggregate = aggregate_formal_runs(summaries)
        write_stable_json(staging / "sizing.json", sizing)
        write_stable_json(staging / "aggregate.json", aggregate)
        write_stable_json(staging / "telemetry_index.json", {
            "schema_version": 1,
            "sampler": "tegrastats, VmRSS, system metrics and all-TID affinity sampler",
            "runs": telemetry,
        })
        write_stable_json(staging / "verification_report.json", {
            "schema_version": 1,
            "status": "PASS",
            "profile": "k5",
            "pilot": {"status": "PASS", "frame_count": len(pilot["records"])},
            "formal_run_count": len(summaries),
            "formal_runs": [
                {"run_index": item["run_index"], "status": item["status"],
                 "payload_sha256": item["payload_sha256"],
                 "report_sha256": item["report_sha256"]}
                for item in summaries
            ],
            "expected_cycle_sha256": FROZEN_SHA["expected_cycle"],
            "semantic_comparison": "PASS",
            "outlier_policy": "keep_all_measured_samples",
        })
        staging.rename(local_attempt_target)

        evidence_target.parent.mkdir(parents=True, exist_ok=True)
        evidence_staging = Path(tempfile.mkdtemp(
            prefix=f".{evidence_target.name}.", dir=str(evidence_target.parent)))
        try:
            shutil.copyfile(local_attempt_target / "sizing.json",
                            evidence_staging / "sizing.json")
            shutil.copyfile(local_attempt_target / "aggregate.json",
                            evidence_staging / "aggregate.json")
            for name in ("telemetry_index.json", "verification_report.json"):
                shutil.copyfile(local_attempt_target / name, evidence_staging / name)
            runs_target = evidence_staging / "runs"
            runs_target.mkdir()
            for index in range(1, 6):
                shutil.copyfile(
                    local_attempt_target / f"run_{index:02d}" / "summary.json",
                    runs_target / f"run_{index:02d}_summary.json")
            (evidence_staging / "README.md").write_text(
                "# Stage J J5.6 Tuned k5 Formal Baseline\n\n"
                "Five independent formal runs passed the frozen k5 protocol.\n"
                "This Evidence was published atomically by the Stage J v2\n"
                "formal orchestrator. J5.7 was not executed.\n",
                encoding="utf-8", newline="\n")
            write_stable_json(evidence_staging / "provenance.json", {
                "schema_version": 1,
                "source_commit": source_commit,
                "profile": "k5",
                "cpu_set": [1, 2, 3, 4, 5],
                "formal_run_count": 5,
                "build_artifact_scope": "external_verified_release_artifact",
                "expected_cycle_sha256": FROZEN_SHA["expected_cycle"],
            })
            atomic_publish(evidence_staging, evidence_target)
        except Exception:
            shutil.rmtree(evidence_staging, ignore_errors=True)
            raise
        return aggregate
    except Exception as exc:
        if staging.exists() and not local_attempt_target.exists():
            try:
                write_stable_json(staging / "failure.json", {
                    "schema_version": 1,
                    "status": "FAIL",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                })
                staging.rename(local_attempt_target)
            except OSError:
                pass
        raise
    finally:
        os.sched_setaffinity(0, original_affinity)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stage J v2 baseline orchestrator.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--development-smoke", action="store_true")
    mode.add_argument("--execute-formal", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--evidence-id")
    parser.add_argument("--runner", required=True, type=Path)
    parser.add_argument("--production-executable", type=Path)
    parser.add_argument("--config-template", required=True, type=Path)
    parser.add_argument("--corpus-dir", required=True, type=Path)
    parser.add_argument("--expected-cycle-json", required=True, type=Path)
    parser.add_argument("--python-reference", required=True, type=Path)
    parser.add_argument("--platform-verification", type=Path)
    parser.add_argument("--local-attempt-root", type=Path, default=Path("/tmp/stage_j_attempts"))
    parser.add_argument(
        "--evidence-root", type=Path,
        default=REPO_ROOT / "results/benchmark/jetson_ort_cpu/profile_stability")
    parser.add_argument("--report-json", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        if args.execute_formal and (args.profile != "k5" or not args.evidence_id):
            raise PreflightError(
                "formal execution requires --profile k5 and --evidence-id")
        if not args.execute_formal and args.evidence_id:
            raise PreflightError("--evidence-id is only valid with --execute-formal")
        evidence_target = (
            args.evidence_root / args.evidence_id if args.evidence_id else None)
        local_target = (
            args.local_attempt_root / args.evidence_id if args.evidence_id else None)
        assets = {
            "model": REPO_ROOT / "models/onnx/yolov8n_neudet_frozen.onnx",
            "contract": REPO_ROOT / "configs/model_contracts/yolov8n_neudet_frozen.yaml",
            "corpus_manifest": args.corpus_dir / "benchmark_corpus_manifest.json",
            "python_reference": args.python_reference,
            "expected_cycle": args.expected_cycle_json,
        }
        info = check_preflight(
            runner=args.runner,
            production_executable=args.production_executable,
            config_template=args.config_template,
            asset_paths=assets,
            profile=args.profile,
            execute_formal=args.execute_formal,
            evidence_target=evidence_target,
            local_attempt_target=local_target,
            platform_verification=args.platform_verification,
        )
        report: dict[str, Any] = {"mode": "preflight-only", "preflight": info}
        if args.development_smoke:
            smoke_root = Path(tempfile.mkdtemp(prefix="stage_j_r2_smoke_"))
            parsed, wall, telemetry = _execute_one(
                args.runner, _load_yaml(args.config_template),
                args.corpus_dir, smoke_root / "run", 40)
            hashes = verify_cycle_correctness(
                parsed["data"], args.expected_cycle_json,
                FROZEN_SHA["expected_cycle"])
            report = {
                "mode": "development-smoke",
                "status": "PASS",
                "frame_count": len(parsed["records"]),
                "cycle_sha_pass_count": len(hashes),
                "trace_real_frame_count": len(parsed["trace_records"]) // 5,
                "process_wall_seconds": wall,
                "affinity_sample_count": len(
                    telemetry["application_tid_affinity_samples"]),
                "temporary_output": smoke_root.name,
            }
        elif args.execute_formal:
            report = {
                "mode": "execute-formal",
                "aggregate": execute_formal_campaign(
                    runner=args.runner,
                    config_template=args.config_template,
                    corpus=args.corpus_dir,
                    expected_cycle_json=args.expected_cycle_json,
                    local_attempt_target=local_target,
                    evidence_target=evidence_target,
                    source_commit=info["source_commit"],
                ),
            }
        if args.report_json:
            if args.report_json.exists():
                raise EvidenceError("report target already exists")
            write_stable_json(args.report_json, report)
        print(f"{report['mode']} PASS")
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except (BenchmarkError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
