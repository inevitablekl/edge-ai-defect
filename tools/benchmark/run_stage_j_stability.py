#!/usr/bin/env python3
"""Stage J6 research-grade tuned k5 stability runner.

The runner reuses the existing RuntimeConfig loader contract through
``stage_j_profile_runner`` and the existing strict result/cycle analyzers.  It
does not contain a second preprocessing, inference or postprocessing path.
The campaign path is intentionally opt-in; ``--preflight-only`` performs no
workload execution.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from m5_ort_cpu_common import (
    BenchmarkError,
    atomic_publish,
    read_strict_json,
    sha256_bytes,
    sha256_file,
    stable_json_bytes,
    write_stable_json,
)
from run_stage_j_ort_cpu_formal import (
    CPU_SET,
    EXPECTED_EXTERNAL_ARTIFACT_SHA256,
    FROZEN_SHA,
    REQUIRED_THERMAL_TYPES,
    _load_yaml,
    build_workload,
    parse_cpu_list,
    safe_read_sysfs_text,
    system_snapshot,
    validate_formal_platform,
    validate_profile,
    validate_thermal_sources,
)
from stage_j_ort_cpu_analyze import (
    decode_staged_filename,
    parse_benchmark_result,
    verify_cycle_correctness,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNNER = Path("/home/orin/edge-ai-local-build/r2-stage-j-tooling-on/stage_j_profile_runner")
DEFAULT_REFERENCE = REPO_ROOT / "results/benchmark/jetson_ort_cpu/python_reference/j5_1_python_reference_v1/benchmark_python_reference_run_1.json"
DEFAULT_EXPECTED_CYCLE = Path("/home/orin/edge-ai-local-evidence/stage_j/j5_attempts/j5.2_candidate_semantic_precheck_v2/stability_cycle.json")
DEFAULT_PLATFORM_VERIFICATION = REPO_ROOT / "docs/personal/STAGE_J_J5_6_PREFLIGHT_REMEDIATION.md"
DEFAULT_LOCAL_ATTEMPTS = Path("/home/orin/edge-ai-local-evidence/stage_j/j6_attempts")
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "results/benchmark/jetson_ort_cpu/stability"
REQUIRED_THERMAL = set(REQUIRED_THERMAL_TYPES)
EXCLUDED_THERMAL = {"cv0", "cv1", "cv2"}


class StabilityError(BenchmarkError):
    """A stability campaign assertion failed."""


def parse_duration_minutes(value: str | int | float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("duration-minutes must be numeric") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise argparse.ArgumentTypeError("duration-minutes must be finite and positive")
    return result


def canonical_cycle_hash(cycle: dict[str, Any]) -> str:
    return sha256_bytes(stable_json_bytes(cycle))


def unavailable(path: str | Path, error: str = "interface unavailable") -> dict[str, Any]:
    return {"status": "unavailable", "path": str(path), "error": error}


def record_failure(path: Path, *, cycle: int | None, exception: BaseException) -> None:
    write_stable_json(path, {
        "schema_version": 1,
        "status": "FAIL",
        "cycle": cycle,
        "timestamp_monotonic_ns": time.monotonic_ns(),
        "exception": f"{type(exception).__name__}: {exception}",
    })


def _read_optional_int(path: Path) -> dict[str, Any]:
    result = safe_read_sysfs_text(path)
    if result["status"] != "ok":
        return unavailable(path, result.get("error", "read failed"))
    try:
        return {"status": "ok", "path": str(path), "value": int(result["value"])}
    except (TypeError, ValueError):
        return unavailable(path, "value is not an integer")


def _first_optional_int(paths: list[Path]) -> dict[str, Any]:
    for path in paths:
        result = _read_optional_int(path)
        if result["status"] == "ok":
            return result
    return unavailable(paths[0] if paths else "not discovered", "no readable source")


def _read_vmrss(pid: int) -> dict[str, Any]:
    path = Path(f"/proc/{pid}/status")
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return {"status": "ok", "value_kb": int(line.split()[1])}
    except (OSError, ValueError, IndexError):
        pass
    return unavailable(path, "VmRSS unavailable")


def _read_vdd_in(raw: str | None) -> dict[str, Any]:
    if raw is None:
        return unavailable("tegrastats:VDD_IN")
    match = re.search(r"VDD_IN\s+(\d+(?:\.\d+)?)/", raw)
    if match is None:
        return unavailable("tegrastats:VDD_IN", "VDD_IN not present")
    return {"status": "ok", "value_mw": float(match.group(1))}


class TegrastatsCollector:
    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.latest: str | None = None
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not Path("/usr/bin/tegrastats").is_file():
            return
        try:
            self.process = subprocess.Popen(
                ["/usr/bin/tegrastats", "--interval", "1000"],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                preexec_fn=lambda: os.sched_setaffinity(0, {0}),
            )
        except (OSError, ValueError):
            self.process = None
            return

        def read() -> None:
            assert self.process is not None and self.process.stdout is not None
            for line in self.process.stdout:
                with self._lock:
                    self.latest = line.rstrip("\n")

        self._thread = threading.Thread(target=read, daemon=True)
        self._thread.start()

    def current(self) -> str | None:
        with self._lock:
            return self.latest

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self._thread is not None:
            self._thread.join(timeout=2)


def telemetry_snapshot(pid: int, previous_cpu: tuple[int, int] | None,
                       tegrastats: TegrastatsCollector) -> tuple[dict[str, Any], tuple[int, int]]:
    snapshot, cpu_state = system_snapshot(previous_cpu)
    if snapshot.get("thermal_status") != "ok":
        raise StabilityError("required thermal telemetry unavailable")
    snapshot["timestamp_monotonic_ns"] = snapshot.pop("monotonic_ns")
    cpu_usage = snapshot.pop("cpu_utilization_percent_cpu1_5")
    snapshot["cpu_usage"] = (
        {"status": "ok", "value_percent": cpu_usage}
        if cpu_usage is not None
        else unavailable("/proc/stat", "insufficient samples")
    )
    snapshot["cpu_frequency"] = snapshot.pop("cpu_frequency_khz") or unavailable(
        "/sys/devices/system/cpu", "CPU frequency source unavailable")
    snapshot["temperature"] = snapshot.pop("temperature_millicelsius")
    snapshot["vmrss"] = _read_vmrss(pid)
    memory = snapshot.pop("ram_kb")
    snapshot["ram"] = {
        "status": "ok" if "MemAvailable" in memory else "unavailable",
        "value_kb": memory.get("MemAvailable"),
        "total_kb": memory.get("MemTotal"),
    }
    snapshot["swap"] = {
        "status": "ok" if "SwapTotal" in memory and "SwapFree" in memory else "unavailable",
        "total_kb": memory.get("SwapTotal"),
        "free_kb": memory.get("SwapFree"),
    }
    snapshot["frequency"] = {
        "cpu": snapshot["cpu_frequency"],
        "gpu": _first_optional_int([
            Path("/sys/devices/gpu.0/devfreq/17000000.gpu/cur_freq"),
            Path("/sys/class/devfreq/17000000.gpu/cur_freq"),
        ]),
        "emc": _first_optional_int([
            Path("/sys/devices/17000000.ga10b00.devfreq/cur_freq"),
            Path("/sys/class/devfreq/17000000.ga10b00.devfreq/cur_freq"),
        ]),
    }
    snapshot["vdd_in"] = _read_vdd_in(tegrastats.current())
    snapshot["thermal_status"] = "ok"
    snapshot["thermal_errors"] = []
    snapshot["excluded_thermal"] = snapshot.get("excluded_thermal", [])
    snapshot["optional_interfaces"] = {
        "oc_uv_throttle": {"status": "unavailable_on_platform"}
    }
    return snapshot, cpu_state


def _asset_paths(config: dict[str, Any], reference: Path, corpus: Path) -> dict[str, Path]:
    return {
        "model": Path(config["model"]["path"]),
        "contract": Path(config["model"]["contract_path"]),
        "corpus_manifest": corpus / "benchmark_corpus_manifest.json",
        "python_reference": reference,
    }


def validate_j6_preflight(*, config_path: Path, corpus: Path, runner: Path,
                          reference: Path, expected_cycle: Path,
                          platform_verification: Path,
                          evidence_target: Path, local_target: Path) -> dict[str, Any]:
    if platform.system() != "Linux" or platform.machine() != "aarch64":
        raise StabilityError("J6 requires Linux aarch64")
    if not runner.is_file() or not os.access(runner, os.X_OK):
        raise StabilityError("stage_j_profile_runner is missing or not executable")
    if sha256_file(runner) != EXPECTED_EXTERNAL_ARTIFACT_SHA256["stage_j_profile_runner"]:
        raise StabilityError("stage_j_profile_runner SHA drift")
    config = _load_yaml(config_path)
    validate_profile(config, profile="k5")
    assets = _asset_paths(config, reference, corpus)
    observed: dict[str, str] = {}
    expected_names = {
        "model": FROZEN_SHA["model"],
        "contract": FROZEN_SHA["contract"],
        "corpus_manifest": FROZEN_SHA["corpus_manifest"],
        "python_reference": FROZEN_SHA["python_reference"],
    }
    for name, path in assets.items():
        if not path.is_file():
            raise StabilityError(f"{name} asset is missing: {path}")
        observed[name] = sha256_file(path)
        if observed[name] != expected_names[name]:
            raise StabilityError(f"{name} SHA drift")
    if not expected_cycle.is_file() or sha256_file(expected_cycle) != FROZEN_SHA["expected_cycle"]:
        raise StabilityError("expected cycle SHA drift")
    try:
        allowed = set(os.sched_getaffinity(0))
        online = parse_cpu_list(Path("/sys/devices/system/cpu/online").read_text())
    except (OSError, ValueError, StabilityError) as exc:
        raise StabilityError(f"CPU affinity preflight failed: {exc}") from exc
    if not CPU_SET.issubset(allowed) or online != {0, 1, 2, 3, 4, 5}:
        raise StabilityError("frozen CPU 0-5 / k5 affinity is unavailable")
    manual = platform_verification.read_text(encoding="utf-8")
    platform_info = validate_formal_platform(manual_verification_text=manual)
    validate_thermal_sources()
    if evidence_target.exists() or local_target.exists():
        raise StabilityError("J6 output target already exists")
    return {
        "status": "PASS",
        "profile": "k5",
        "cpu_set": [1, 2, 3, 4, 5],
        "assets": observed | {"expected_cycle": sha256_file(expected_cycle)},
        "platform": platform_info,
        "runner": {"path": str(runner), "sha256": sha256_file(runner)},
        "targets": {"evidence": str(evidence_target), "local_attempt": str(local_target)},
    }


def _write_cycle_config(template: dict[str, Any], workload: Path,
                        result: Path) -> dict[str, Any]:
    config = copy.deepcopy(template)
    config["input"]["directory"] = str(workload)
    config["output"]["json_path"] = str(result)
    config["output"]["overwrite"] = False
    return config


def _normalize_cycle(data: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    images = data.get("images")
    golden_images = expected.get("images")
    if not isinstance(images, list) or len(images) != 20 or not isinstance(golden_images, list):
        raise StabilityError("cycle does not contain exactly 20 images")
    normalized = copy.deepcopy(data)
    output_images = []
    for within, image in enumerate(images):
        encoded_cycle, encoded_within, original = decode_staged_filename(image["relative_path"])
        if encoded_cycle != 0 or encoded_within != within or original != golden_images[within]["relative_path"]:
            raise StabilityError("cycle staged filenames are inconsistent")
        item = copy.deepcopy(image)
        item["sequence_index"] = within
        item["relative_path"] = original
        item.pop("timing_ms", None)
        output_images.append(item)
    normalized["images"] = output_images
    normalized["summary"] = {
        "processed_images": 20,
        "total_detections": sum(len(item["detections"]) for item in output_images),
    }
    return normalized


def _start_process(command: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        preexec_fn=lambda: os.sched_setaffinity(0, CPU_SET))


def run_stability_campaign(*, config_path: Path, corpus: Path, duration_minutes: float,
                           evidence_id: str, runner: Path, reference: Path,
                           expected_cycle: Path, platform_verification: Path,
                           local_root: Path, evidence_root: Path) -> dict[str, Any]:
    evidence_target = evidence_root / evidence_id
    local_target = local_root / evidence_id
    preflight = validate_j6_preflight(
        config_path=config_path, corpus=corpus, runner=runner, reference=reference,
        expected_cycle=expected_cycle, platform_verification=platform_verification,
        evidence_target=evidence_target, local_target=local_target)
    local_root.mkdir(parents=True, exist_ok=True)
    evidence_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{evidence_id}.", dir=str(local_root)))
    cycle = None
    telemetry: list[dict[str, Any]] = []
    cycles: list[dict[str, Any]] = []
    sampler = TegrastatsCollector()
    previous_cpu: tuple[int, int] | None = None
    measured_start = 0.0
    try:
        template = _load_yaml(config_path)
        workload_info = build_workload(corpus, staging / "workload", 20)
        expected_data = read_strict_json(expected_cycle)
        sampler.start()
        measured_start = time.monotonic()
        next_sample = measured_start
        while time.monotonic() - measured_start < duration_minutes * 60.0:
            cycle = len(cycles)
            cycle_dir = staging / "cycles" / f"cycle_{cycle:06d}"
            cycle_dir.mkdir(parents=True)
            result_path = cycle_dir / "result.json"
            trace_path = cycle_dir / "trace.jsonl"
            config_for_cycle = cycle_dir / "runtime.yaml"
            write_stable_json(cycle_dir / "command.json", {
                "runner": str(runner), "config": str(config_for_cycle),
                "trace": str(trace_path),
            })
            import yaml
            config_for_cycle.write_text(
                yaml.safe_dump(_write_cycle_config(template, staging / "workload", result_path),
                               sort_keys=False), encoding="utf-8")
            process = _start_process([str(runner), "--config", str(config_for_cycle),
                                      "--trace-jsonl", str(trace_path)])
            try:
                while process.poll() is None:
                    now = time.monotonic()
                    if now >= next_sample:
                        sample, previous_cpu = telemetry_snapshot(
                            process.pid, previous_cpu, sampler)
                        sample["elapsed_measured_seconds"] = now - measured_start
                        telemetry.append(sample)
                        next_sample = now + 5.0
                    time.sleep(0.2)
                stdout, stderr = process.communicate()
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5.0)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            if process.returncode != 0:
                raise StabilityError(f"cycle process exited {process.returncode}: {stderr.strip()}")
            if stdout:
                raise StabilityError("cycle process unexpectedly wrote stdout")
            parsed = parse_benchmark_result(result_path, trace_path, workload_info)
            verify_cycle_correctness(parsed["data"], expected_cycle, FROZEN_SHA["expected_cycle"])
            normalized = _normalize_cycle(parsed["data"], expected_data)
            cycle_hash = canonical_cycle_hash(normalized)
            if cycles and cycle_hash != cycles[0]["cycle_sha256"]:
                raise StabilityError("cycle hash drift")
            cycles.append({
                "cycle_id": cycle,
                "timestamp_monotonic_ns": time.monotonic_ns(),
                "frame_count": 20,
                "detections_count": normalized["summary"]["total_detections"],
                "cycle_sha256": cycle_hash,
                "payload_sha256": parsed["raw_sha256"],
                "expected_cycle_sha256": FROZEN_SHA["expected_cycle"],
                "correctness": "PASS",
                "success": True,
            })
        end = time.monotonic()
        if end - measured_start < duration_minutes * 60.0:
            raise StabilityError("measured stability duration is below target")
        sample, previous_cpu = telemetry_snapshot(process.pid, previous_cpu, sampler)
        sample["elapsed_measured_seconds"] = end - measured_start
        telemetry.append(sample)
        (staging / "cycle_hashes.jsonl").write_text(
            "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in cycles),
            encoding="utf-8")
        (staging / "telemetry.jsonl").write_text(
            "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in telemetry),
            encoding="utf-8")
        write_stable_json(staging / "environment.json", preflight)
        write_stable_json(staging / "stability_report.json", {
            "schema_version": 1, "status": "PASS", "evidence_id": evidence_id,
            "profile": "k5", "duration_minutes": duration_minutes,
            "measured_duration_seconds": end - measured_start,
            "cycle_count": len(cycles), "frame_count": len(cycles) * 20,
            "failure_count": 0, "correctness_failures": 0,
            "memory_observation": "telemetry_recorded" if telemetry else "unavailable",
        })
        write_stable_json(staging / "correctness_summary.json", {
            "status": "PASS", "cycle_count": len(cycles),
            "unique_cycle_sha256": sorted({item["cycle_sha256"] for item in cycles}),
            "expected_cycle_sha256": FROZEN_SHA["expected_cycle"],
            "hash_drift": False,
        })
        vmrss = [item["vmrss"]["value_kb"] for item in telemetry
                 if item.get("vmrss", {}).get("status") == "ok"]
        write_stable_json(staging / "resource_summary.json", {
            "vmrss_kb": {
                "status": "PASS" if vmrss else "unavailable",
                "starting": vmrss[0] if vmrss else None,
                "ending": vmrss[-1] if vmrss else None,
                "minimum": min(vmrss) if vmrss else None,
                "maximum": max(vmrss) if vmrss else None,
                "delta": vmrss[-1] - vmrss[0] if vmrss else None,
                "sample_count": len(vmrss),
            }
        })
        write_stable_json(staging / "provenance.json", {
            "schema_version": 1, "evidence_id": evidence_id, "profile": "k5",
            "source_commit": _git_rev(), "preflight": preflight,
            "duration_minutes": duration_minutes, "benchmark_rerun": True,
        })
        (staging / "commands.txt").write_text(
            "python3 tools/benchmark/run_stage_j_stability.py --config "
            f"{config_path} --corpus {corpus} --duration-minutes {duration_minutes:g} "
            f"--evidence-id {evidence_id}\n", encoding="utf-8")
        (staging / "README.md").write_text(
            "# Stage J6 Tuned k5 Research-Grade Stability\n\n"
            "Continuous measured stability window; J7/J8/J9 and Stage T were not executed.\n",
            encoding="utf-8")
        _write_sha256sums(staging)
        local_target.parent.mkdir(parents=True, exist_ok=True)
        staging.rename(local_target)
        evidence_staging = Path(tempfile.mkdtemp(prefix=f".{evidence_id}.", dir=str(evidence_root)))
        try:
            for name in ("README.md", "stability_report.json", "cycle_hashes.jsonl",
                         "telemetry.jsonl", "environment.json", "provenance.json",
                         "commands.txt", "correctness_summary.json", "resource_summary.json"):
                (evidence_staging / name).write_bytes((local_target / name).read_bytes())
            _write_sha256sums(evidence_staging)
            write_stable_json(evidence_staging / "verification_report.json", {
                "schema_version": 1, "status": "PASS", "duration": "PASS",
                "cycles": len(cycles), "frames": len(cycles) * 20,
                "failures": 0, "correctness": "PASS", "hash_drift": False,
                "telemetry_samples": len(telemetry), "profile": "k5",
            })
            _write_sha256sums(evidence_staging)
            atomic_publish(evidence_staging, evidence_target)
        except Exception:
            raise
        return {"status": "PASS", "evidence": str(evidence_target), "cycles": len(cycles)}
    except Exception as exc:
        sampler.stop()
        if staging.exists() and not local_target.exists():
            record_failure(staging / "failure.json", cycle=cycle, exception=exc)
            staging.rename(local_target)
        raise
    finally:
        sampler.stop()


def _write_sha256sums(directory: Path) -> None:
    lines = []
    for path in sorted(p for p in directory.iterdir() if p.is_file() and p.name != "sha256sums.txt"):
        lines.append(f"{sha256_file(path)}  {path.name}")
    (directory / "sha256sums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _git_rev() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage J6 tuned k5 stability runner")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--duration-minutes", type=parse_duration_minutes, default=30.0)
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--expected-cycle", type=Path, default=DEFAULT_EXPECTED_CYCLE)
    parser.add_argument("--platform-verification", type=Path, default=DEFAULT_PLATFORM_VERIFICATION)
    parser.add_argument("--local-attempt-root", type=Path, default=DEFAULT_LOCAL_ATTEMPTS)
    parser.add_argument("--evidence-root", type=Path, default=DEFAULT_EVIDENCE_ROOT)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        evidence_target = args.evidence_root / args.evidence_id
        local_target = args.local_attempt_root / args.evidence_id
        info = validate_j6_preflight(
            config_path=args.config, corpus=args.corpus, runner=args.runner,
            reference=args.reference, expected_cycle=args.expected_cycle,
            platform_verification=args.platform_verification,
            evidence_target=evidence_target, local_target=local_target)
        if args.preflight_only:
            print("J6_READY_FOR_EXECUTION")
            return 0
        result = run_stability_campaign(
            config_path=args.config, corpus=args.corpus,
            duration_minutes=args.duration_minutes, evidence_id=args.evidence_id,
            runner=args.runner, reference=args.reference,
            expected_cycle=args.expected_cycle,
            platform_verification=args.platform_verification,
            local_root=args.local_attempt_root, evidence_root=args.evidence_root)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (BenchmarkError, OSError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
