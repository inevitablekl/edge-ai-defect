#!/usr/bin/env python3
"""Derive a deterministic, limitation-aware J5.5 k1 supplement.

This tool reads only the immutable published J5.5 Evidence directory.  It
never treats whole-process wall time as per-frame latency and never fills
missing resource or timing values from aggregate data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from m5_ort_cpu_common import (
    BenchmarkError,
    read_strict_json,
    sha256_file,
    stable_json_bytes,
    summarize_values,
    write_stable_json,
)


RUN_COUNT = 5
RUN_NAMES = tuple(f"run_{index:02d}_summary.json" for index in range(1, RUN_COUNT + 1))


def _verify_manifest(source: Path) -> list[dict[str, str]]:
    manifest = source / "sha256sums.txt"
    if not manifest.is_file():
        raise BenchmarkError("J5.5 sha256sums.txt is missing")
    entries: list[dict[str, str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, separator, relative = line.partition("  ")
        if not separator or len(expected) != 64:
            raise BenchmarkError(f"invalid J5.5 manifest line: {line!r}")
        path = source / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise BenchmarkError(f"J5.5 manifest mismatch: {relative}")
        entries.append({"path": relative, "sha256": expected})
    return entries


def _required_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BenchmarkError(f"missing or invalid numeric value: {name}")
    return float(value)


def load_j5_5_runs(source: Path) -> list[dict[str, Any]]:
    _verify_manifest(source)
    runs: list[dict[str, Any]] = []
    for name in RUN_NAMES:
        path = source / "k1" / name
        if not path.is_file():
            raise BenchmarkError(f"required J5.5 run is missing: {name}")
        value = read_strict_json(path)
        if not isinstance(value, dict):
            raise BenchmarkError(f"J5.5 run is not an object: {name}")
        for field in ("process_wall_ms", "fps", "processed_frames",
                      "semantic_pass", "expected_cycle_sha256", "payload_sha256"):
            if field not in value:
                raise BenchmarkError(f"J5.5 run {name} lacks {field}")
        if value["semantic_pass"] is not True or value["processed_frames"] != 560:
            raise BenchmarkError(f"J5.5 run {name} failed correctness/frame gate")
        runs.append(value)
    return runs


def build_supplement(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if len(runs) != RUN_COUNT:
        raise BenchmarkError("exactly five J5.5 runs are required")
    wall_values = [_required_number(run.get("process_wall_ms"), "process_wall_ms")
                   for run in runs]
    fps_values = [_required_number(run.get("fps"), "fps") for run in runs]
    vmrss_values = []
    for run in runs:
        if "max_VmRSS_kB" in run:
            vmrss_values.append(_required_number(run["max_VmRSS_kB"], "max_VmRSS_kB"))
    expected = {run["expected_cycle_sha256"] for run in runs}
    payloads = {run["payload_sha256"] for run in runs}
    return {
        "schema_version": 1,
        "status": "PASS_WITH_DOCUMENTED_LIMITATION",
        "profile": "k1",
        "source_scope": "immutable published J5.5 summaries only",
        "process_count": RUN_COUNT,
        "processed_frames_each_run": 560,
        "latency_scope": "whole_process_wall_time",
        "whole_process_wall_time_ms": summarize_values(wall_values),
        "fps_scope": "published whole-process FPS values",
        "fps": summarize_values(fps_values),
        "resource_summary": {
            "max_VmRSS_kB": summarize_values(vmrss_values)
            if len(vmrss_values) == RUN_COUNT else {
                "status": "not_available_per_run",
                "available_run_count": len(vmrss_values),
            },
        },
        "correctness": {
            "all_runs_semantic_pass": all(run["semantic_pass"] for run in runs),
            "expected_cycle_sha256_values": sorted(expected),
            "payload_sha256_values": sorted(payloads),
        },
        "not_available": [
            "measured_window_per_frame_latency_distribution",
            "per_frame_latency_P50_P95_P99",
            "per_frame_latency_sample_standard_deviation",
            "independently_reconstructable_raw_telemetry",
        ],
        "prohibited_inference": [
            "process_wall_ms / frame_count was not used as per-frame latency",
            "no per-frame distribution was inferred from aggregate values",
        ],
    }


def _source_index(source: Path, manifest_entries: list[dict[str, str]]) -> dict[str, Any]:
    names = ["benchmark_report.json", *RUN_NAMES, "provenance.json", "environment.json",
             "sha256sums.txt"]
    files = []
    for relative in names:
        path = source / (Path("k1") / relative if relative.startswith("run_") else relative)
        files.append({"path": path.relative_to(source).as_posix(), "sha256": sha256_file(path)})
    return {
        "schema_version": 1,
        "source_evidence_id": "j5_5_profile_baseline_v1",
        "source_root": "results/benchmark/jetson_ort_cpu/profile_baseline/j5_5_profile_baseline_v1",
        "source_manifest_status": "PASS",
        "source_manifest_entries": manifest_entries,
        "inputs_used": files,
    }


def generate(source: Path, output: Path) -> None:
    if output.exists():
        raise BenchmarkError(f"supplement output already exists: {output}")
    manifest_entries = _verify_manifest(source)
    runs = load_j5_5_runs(source)
    report = build_supplement(runs)
    output.mkdir(parents=True)
    write_stable_json(output / "controlled_supplement_report.json", report)
    write_stable_json(output / "source_evidence_index.json",
                      _source_index(source, manifest_entries))
    write_stable_json(output / "provenance.json", {
        "schema_version": 1,
        "evidence_id": "j5_5_controlled_supplement_v1",
        "source_evidence_id": "j5_5_profile_baseline_v1",
        "source_manifest_status": "PASS",
        "generation_scope": "deterministic derivation from published summaries",
        "benchmark_rerun": False,
        "per_frame_data_invented": False,
        "latency_scope": "whole_process_wall_time",
        "source_evidence_sha256": sha256_file(source / "sha256sums.txt"),
    })
    (output / "README.md").write_text(
        "# J5.5 Controlled k1 Historical Statistics Supplement\n\n"
        "This supplement is deterministically derived from the immutable published "
        "J5.5 summaries. It does not modify or replace the original Evidence.\n\n"
        "`latency_scope=whole_process_wall_time`. Per-frame latency distributions "
        "and independently reconstructable raw telemetry are not available and "
        "were not inferred.\n",
        encoding="utf-8", newline="\n")
    (output / "commands.txt").write_text(
        "1. cd results/benchmark/jetson_ort_cpu/profile_baseline/"
        "j5_5_profile_baseline_v1 && sha256sum -c sha256sums.txt\n"
        "2. python3 tools/benchmark/generate_j5_5_controlled_supplement.py "
        "--source results/benchmark/jetson_ort_cpu/profile_baseline/"
        "j5_5_profile_baseline_v1 --output results/benchmark/jetson_ort_cpu/"
        "controlled_supplement/j5_5_controlled_supplement_v1\n"
        "3. cd results/benchmark/jetson_ort_cpu/controlled_supplement/"
        "j5_5_controlled_supplement_v1 && sha256sum -c sha256sums.txt\n",
        encoding="utf-8", newline="\n")
    entries = []
    for path in sorted(p for p in output.rglob("*") if p.is_file() and p.name != "sha256sums.txt"):
        entries.append(f"{sha256_file(path)}  {path.relative_to(output).as_posix()}")
    (output / "sha256sums.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate(args.source, args.output)
    print("supplement PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
