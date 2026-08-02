#!/usr/bin/env python3
"""Run and aggregate the frozen Stage R R3 V0/V2/V3/V4 ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


VARIANTS = ("V0", "V2", "V3", "V4")
CONFIGS = {
    "V0": "configs/stage_r/runtime_v6_v0_off.yaml",
    "V2": "configs/stage_r/runtime_v6_v2_pageable.yaml",
    "V3": "configs/stage_r/runtime_v6_v3_pinned.yaml",
    "V4": "configs/stage_r/runtime_v6_v4_double_buffer.yaml",
}
ORDERS = (
    ("V0", "V2", "V3", "V4"),
    ("V4", "V3", "V2", "V0"),
    ("V2", "V0", "V4", "V3"),
    ("V3", "V4", "V0", "V2"),
    ("V0", "V3", "V2", "V4"),
)
ACCURACY_DELTA = {"V0": 0.0, "V2": -0.00537575, "V3": -0.00537575, "V4": -0.00537575}


def attempt_1_status() -> str:
    return "BLOCKED_RUNNER_TOPOLOGY_MISMATCH"


def attempt_2_status() -> str:
    return "UNIFIED_HARNESS_COMPARABLE"


def comparability_status(attempt: int) -> str:
    return attempt_2_status() if attempt >= 2 else attempt_1_status()


def interpretation_status(attempt: int) -> str:
    return "FORMAL_ABLATION_AUTHORITY" if attempt >= 2 else "DESCRIPTIVE_ONLY"


def experiment_completion_status(attempt: int) -> str:
    return "COMPLETE_UNIFIED_HARNESS_COMPARABLE" if attempt >= 2 else "COMPLETE_SAMPLING_COMPARABILITY_BLOCKED"


def attempt_classification(attempt: int) -> str:
    return "R3_ATTEMPT_2_UNIFIED_HARNESS" if attempt >= 2 else "R3_ATTEMPT_1_NONCOMPARABLE_HARNESS"


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_output(command: list[str], cwd: Path) -> str:
    try:
        result = run(command, cwd=cwd, check=False)
    except FileNotFoundError:
        return "unavailable: executable not found"
    output = (result.stdout + result.stderr).strip()
    return output if len(output) <= 4000 else "...[truncated]...\n" + output[-4000:]


def temperatures() -> dict[str, float]:
    result: dict[str, float] = {}
    for path in sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp")):
        try:
            result[path.parent.name] = int(path.read_text().strip()) / 1000.0
        except (OSError, TypeError, ValueError):
            pass
    return result


def environment_snapshot(root: Path) -> dict[str, object]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "uname": command_output(["uname", "-a"], root),
        "architecture": command_output(["uname", "-m"], root),
        "nvpmodel": command_output(["nvpmodel", "-q"], root),
        "jetson_clocks_show": command_output(["jetson_clocks", "--show"], root),
        "cuda_version": command_output(["/usr/local/cuda/bin/nvcc", "--version"], root),
        "tensorrt_version": command_output(["trtexec", "--version"], root),
        "opencv_threads_contract": 1,
        "cpu_affinity_contract": "0-5",
        "temperatures_c": temperatures(),
    }


def parse_cpu_equivalent_cores(path: Path) -> float | None:
    values: list[float] = []
    pattern = re.compile(r"CPU \[([^\]]+)\]")
    for line in path.read_text(errors="replace").splitlines():
        match = pattern.search(line)
        if not match:
            continue
        busy = []
        for item in match.group(1).split(","):
            value = re.match(r"\s*([0-9]+(?:\.[0-9]+)?)%@", item)
            if value:
                busy.append(float(value.group(1)) / 100.0)
        if busy:
            values.append(sum(busy))
    return statistics.fmean(values) if values else None


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize_run(run_dir: Path, variant: str, order_index: int, attempt: int) -> dict[str, object]:
    metrics = json.loads((run_dir / "metrics.json").read_text())
    manifest = json.loads((run_dir / "run_manifest.json").read_text())
    hashes = json.loads((run_dir / "hashes.json").read_text())
    latency = [float(value) for value in metrics["latency_ms"]]
    cpu_cores = parse_cpu_equivalent_cores(run_dir / "tegrastats.log")
    return {
        "run_id": metrics["run_id"],
        "variant": variant,
        "order_index": order_index,
        "attempt": attempt,
        "measured_frames": metrics["measured_frames"],
        "processed_frames": metrics["processed_frames"],
        "drop_count": 0,
        "run_wall_ms": metrics["run_wall_ms"],
        "throughput_fps": metrics["throughput_fps"],
        "latency_mean_ms": statistics.fmean(latency),
        "latency_median_ms": statistics.median(latency),
        "latency_p95_ms": percentile(latency, 0.95),
        "latency_p99_ms": percentile(latency, 0.99),
        "latency_min_ms": min(latency),
        "latency_max_ms": max(latency),
        "latency_stddev_ms": statistics.pstdev(latency),
        "cpu_equivalent_cores": cpu_cores,
        "detection_sha": hashes["detection_sha256"],
        "tensor_digest": hashes["tensor_digest_sha256"] or None,
        "result_json_sha256": sha256(run_dir / "result.json"),
        "binary_sha256": manifest["binary_sha256"],
        "config_sha256": manifest["config_sha256"],
        "engine_sha256": manifest["engine_sha256"],
        "manifest_sha256": manifest["test_manifest_sha256"],
        "run_manifest_sha256": sha256(run_dir / "run_manifest.json"),
        "status": "PASS",
    }


def mean_or_none(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def aggregate(rows: list[dict[str, object]], variant: str) -> dict[str, object]:
    selected = [row for row in rows if row["variant"] == variant]
    fields = (
        "throughput_fps", "latency_mean_ms", "latency_median_ms", "latency_p95_ms",
        "latency_p99_ms", "latency_min_ms", "latency_max_ms", "latency_stddev_ms",
    )
    result: dict[str, object] = {
        "variant": variant,
        "run_count": len(selected),
        "measured_frames": sum(int(row["measured_frames"]) for row in selected),
        "measured_frames_per_run": selected[0]["measured_frames"] if selected else None,
        "drop_count": sum(int(row["drop_count"]) for row in selected),
        "cpu_equivalent_cores_mean": mean_or_none([row["cpu_equivalent_cores"] for row in selected]),
        "detection_sha": sorted({row["detection_sha"] for row in selected}),
        "tensor_digest": sorted({row["tensor_digest"] for row in selected}),
        "accuracy_source": "Stage R R2 remediated V2 Gate D result; V3/V4 inherit identical detection SHA",
    }
    output_names = {
        "throughput_fps": "throughput_mean",
        "latency_mean_ms": "latency_mean",
        "latency_median_ms": "latency_median",
        "latency_p95_ms": "latency_p95",
        "latency_p99_ms": "latency_p99",
        "latency_min_ms": "latency_min",
        "latency_max_ms": "latency_max",
        "latency_stddev_ms": "latency_stddev",
    }
    for field in fields:
        values = [float(row[field]) for row in selected]
        name = output_names[field]
        result[name] = statistics.fmean(values) if values else None
        result[name + "_stddev_across_runs"] = (
            statistics.pstdev(values) if len(values) > 1 else 0.0 if values else None
        )
    return result


def relative(candidate: float | None, baseline: float | None) -> float | None:
    if candidate is None or baseline in (None, 0):
        return None
    return (candidate - baseline) / baseline


def build_comparison(aggregates: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    pairs = (("V2", "V0", "V2_vs_V0"), ("V3", "V2", "V3_vs_V2"),
             ("V4", "V3", "V4_vs_V3"), ("V4", "V0", "V4_vs_V0"))
    increments = {
        "V2_vs_V0": "CUDA fused preprocessing with pageable raw staging",
        "V3_vs_V2": "replace pageable raw staging with long-lived pinned raw staging",
        "V4_vs_V3": "two pinned raw/device slots with limited fixed alternation",
        "V4_vs_V0": "complete V0 to V4 data-path increment",
    }
    rows = []
    for candidate, baseline, name in pairs:
        c, b = aggregates[candidate], aggregates[baseline]
        rows.append({
            "comparison": name,
            "candidate": candidate,
            "baseline": baseline,
            "absolute_fps_difference": c["throughput_mean"] - b["throughput_mean"],
            "relative_fps_change": relative(c["throughput_mean"], b["throughput_mean"]),
            "absolute_mean_latency_ms_difference": c["latency_mean"] - b["latency_mean"],
            "relative_mean_latency_change": relative(c["latency_mean"], b["latency_mean"]),
            "absolute_p95_latency_ms_difference": c["latency_p95"] - b["latency_p95"],
            "relative_p95_latency_change": relative(c["latency_p95"], b["latency_p95"]),
            "absolute_p99_latency_ms_difference": c["latency_p99"] - b["latency_p99"],
            "relative_p99_latency_change": relative(c["latency_p99"], b["latency_p99"]),
            "cpu_equivalent_cores_difference": c["cpu_equivalent_cores_mean"] - b["cpu_equivalent_cores_mean"],
            "accuracy_delta": ACCURACY_DELTA[candidate] - ACCURACY_DELTA[baseline],
            "implementation_increment": increments[name],
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runner", type=Path, default=Path("build_r3/stage_r_r3_ablation_runner"))
    parser.add_argument("--warmup-frames", type=int, default=60)
    parser.add_argument("--measured-frames", type=int, default=1080)
    parser.add_argument("--attempt", type=int, default=1,
                        help="attempt label for classification and status fields (1 = non-comparable, >=2 = unified harness)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="resume: keep run directories whose command.json records returncode 0 and result.json exists; "
                             "re-execute failed or partial runs once (failure records are retained in failure.json)")
    args = parser.parse_args()
    root = Path.cwd()
    output = args.output_dir
    if output.exists() and any(output.iterdir()) and not args.skip_existing:
        raise SystemExit(f"refusing non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    (output / "runs").mkdir(exist_ok=True)
    manifest_path = root / "results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json"
    binary = (root / args.runner).resolve()
    if not binary.exists():
        raise SystemExit(f"runner does not exist: {binary}")
    branch = command_output(["git", "branch", "--show-current"], root)
    commit = command_output(["git", "rev-parse", "HEAD"], root)
    status = command_output(["git", "status", "--short"], root)
    if branch != "feature/jetson-int8-data-path-optimization" or commit != "b789a672cf1ecbac4a4d7c25cb0c5a8575c5eba0":
        raise SystemExit(f"entry identity mismatch: branch={branch} commit={commit}")

    experiment = {
        "schema_version": 1,
        "stage": "R",
        "phase": "R3",
        "status": "RUNNING",
        "attempt": args.attempt,
        "classification": attempt_classification(args.attempt),
        "research_mode": "MULTI_BRANCH_ABLATION_MODE",
        "production_commit": commit,
        "branch": branch,
        "worktree_status_at_start": status,
        "runner_path": str(binary),
        "runner_sha256": sha256(binary),
        "corpus_manifest_path": str(manifest_path),
        "corpus_manifest_sha256": sha256(manifest_path),
        "warmup_frames": args.warmup_frames,
        "measured_frames_per_run": args.measured_frames,
        "independent_runs_per_variant": 5,
        "queue_capacity": 1,
        "drop_policy": "block",
        "order_schedule": [list(order) for order in ORDERS],
        "entry_environment": environment_snapshot(root),
        "variants": CONFIGS,
        "prohibited_during_sampling": ["production code changes", "CUDA resize changes", "retuning", "engine/model/postprocess changes"],
    }
    (output / "experiment_manifest.json").write_text(json.dumps(experiment, indent=2) + "\n")

    rows: list[dict[str, object]] = []
    for order_index, order in enumerate(ORDERS, start=1):
        for variant in order:
            run_id = f"set_{order_index:02d}_{variant.lower()}"
            run_dir = output / "runs" / run_id
            command_path = run_dir / "command.json"
            if args.skip_existing and command_path.exists():
                record = json.loads(command_path.read_text())
                if record.get("returncode") == 0 and (run_dir / "result.json").exists():
                    rows.append(summarize_run(run_dir, variant, order_index, args.attempt))
                    print(f"SKIP {run_id}: already completed", flush=True)
                    continue
                shutil.rmtree(run_dir)
            run_dir.mkdir()
            start_environment = environment_snapshot(root)
            (run_dir / "environment_start.json").write_text(json.dumps(start_environment, indent=2) + "\n")
            telemetry_path = run_dir / "tegrastats.log"
            telemetry = telemetry_path.open("w")
            sampler = subprocess.Popen(["tegrastats", "--interval", "1000"], stdout=telemetry, stderr=subprocess.STDOUT, text=True)
            started = time.monotonic()
            command = [
                "taskset", "--cpu-list", "0-5", str(binary),
                "--config", str(root / CONFIGS[variant]),
                "--corpus-manifest", str(manifest_path), "--run-id", run_id,
                "--warmup-frames", str(args.warmup_frames), "--measured-frames", str(args.measured_frames),
                "--result-json", str(run_dir / "result.json"),
                "--run-manifest", str(run_dir / "run_manifest.json"),
                "--hashes", str(run_dir / "hashes.json"), "--metrics", str(run_dir / "metrics.json"),
            ]
            proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
            elapsed = time.monotonic() - started
            sampler.terminate()
            try:
                sampler.wait(timeout=3)
            except subprocess.TimeoutExpired:
                sampler.kill()
                sampler.wait()
            telemetry.close()
            (run_dir / "command.json").write_text(json.dumps({"argv": command, "wall_seconds": elapsed, "returncode": proc.returncode}, indent=2) + "\n")
            (run_dir / "stdout.log").write_text(proc.stdout)
            (run_dir / "stderr.log").write_text(proc.stderr)
            (run_dir / "environment_end.json").write_text(json.dumps(environment_snapshot(root), indent=2) + "\n")
            if proc.returncode != 0:
                (output / "failure.json").write_text(json.dumps({"run_id": run_id, "variant": variant, "returncode": proc.returncode, "stderr": proc.stderr}, indent=2) + "\n")
                raise SystemExit(f"formal run failed: {run_id}; see {run_dir}")
            rows.append(summarize_run(run_dir, variant, order_index, args.attempt))
            print(f"PASS {run_id}: {rows[-1]['throughput_fps']:.3f} FPS, mean {rows[-1]['latency_mean_ms']:.3f} ms", flush=True)

    status = comparability_status(args.attempt)
    (output / "per_run_metrics.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(args.attempt), "comparability_status": status, "runs": rows}, indent=2) + "\n")
    aggregates = {variant: aggregate(rows, variant) for variant in VARIANTS}
    (output / "aggregate_metrics.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(args.attempt), "comparability_status": status, "variants": list(aggregates.values())}, indent=2) + "\n")
    comparisons = build_comparison(aggregates)
    (output / "comparison_matrix.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(args.attempt), "comparability_status": status, "interpretation_status": interpretation_status(args.attempt), "comparisons": comparisons}, indent=2) + "\n")
    tradeoff = []
    mechanisms = {
        "V0": "CPU/OpenCV preprocessing and pageable FP32 HostTensor",
        "V2": "CUDA fused preprocessing with pageable raw staging",
        "V3": "V2 plus long-lived pinned raw staging",
        "V4": "V3 plus limited two-slot alternation",
    }
    for variant in VARIANTS:
        tradeoff.append({
            "variant": variant,
            "performance": aggregates[variant],
            "accuracy_delta_mAP50": ACCURACY_DELTA[variant],
            "correctness_classification": "Stage Q correctness baseline" if variant == "V0" else "accuracy-trade-off experimental path; not Gate D equivalent replacement",
            "incremental_mechanism": mechanisms[variant],
            "selection_interpretation": "defer final Pareto selection to Stage R5",
        })
    (output / "performance_accuracy_tradeoff.json").write_text(json.dumps({"schema_version": 1, "classification": attempt_classification(args.attempt), "comparability_status": status, "selection_status": "NO_CANDIDATE_SELECTED", "variants": tradeoff}, indent=2) + "\n")
    experiment["status"] = experiment_completion_status(args.attempt)
    experiment["exit_environment"] = environment_snapshot(root)
    (output / "experiment_manifest.json").write_text(json.dumps(experiment, indent=2) + "\n")

    hash_lines = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "artifact_sha256.txt":
            hash_lines.append(f"{sha256(path)}  {path.relative_to(output)}")
    (output / "artifact_sha256.txt").write_text("\n".join(hash_lines) + "\n")
    print(f"R3 formal sampling complete: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("interrupted")
