#!/usr/bin/env python3
"""Validate the compact Phase 0.5D-I1 timing-aligned preflight artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


VARIANTS = ("V0", "V2R", "V3R")
PER_FRAME_FIELDS = {"sequence_index", "relative_path", "width", "height", "detections"}
RESULT_TOP_FIELDS = {"schema_version", "backend", "model", "precision", "runtime", "postprocess", "images", "summary"}
V0_CONFIG = Path("configs/stage_r/runtime_v6_v0_timing_aligned.yaml")
V2R_CONFIG = Path("configs/stage_r/runtime_v6_v2r_timing_aligned.yaml")
V3R_CONFIG = Path("configs/stage_r/runtime_v6_v3r_timing_aligned.yaml")
HISTORICAL_ROOT = Path("results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load JSON {path}: {exc}")


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else key
            result.update(flatten(value[key], child))
        return result
    if isinstance(value, list):
        result = {}
        for index, item in enumerate(value):
            result.update(flatten(item, f"{prefix}[{index}]"))
        return result
    return {prefix: value}


def config_diff(configs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    flattened = {variant: flatten(data) for variant, data in configs.items()}
    all_paths = sorted(set().union(*(set(values) for values in flattened.values())))
    intentional = {"data_path.variant"}
    hidden_differences: dict[str, dict[str, Any]] = {}
    for path in all_paths:
        values = {variant: flattened[variant].get(path) for variant in VARIANTS}
        if len({json.dumps(value, sort_keys=True) for value in values.values()}) > 1:
            if path not in intentional:
                hidden_differences[path] = values
    return {
        "schema_version": 1,
        "status": "PASS" if not hidden_differences else "HARNESS_INVALID",
        "config_files": {variant: str(path) for variant, path in {
            "V0": V0_CONFIG, "V2R": V2R_CONFIG, "V3R": V3R_CONFIG}.items()},
        "config_sha256": {variant: sha256(path) for variant, path in {
            "V0": V0_CONFIG, "V2R": V2R_CONFIG, "V3R": V3R_CONFIG}.items()},
        "intentional_difference_paths": sorted(intentional),
        "hidden_difference_paths": hidden_differences,
        "common_field_equality": not hidden_differences,
        "timing_enabled": {variant: configs[variant]["timing"]["enabled"] for variant in VARIANTS},
        "profiling_mode": {variant: ("off" if configs[variant]["profiling"]["mode"] is False
                                     else configs[variant]["profiling"]["mode"])
                           for variant in VARIANTS},
        "parsed_variants": {variant: configs[variant]["data_path"]["variant"] for variant in VARIANTS},
    }


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
    except OSError as exc:
        return f"unavailable: {exc}"
    output = (result.stdout + result.stderr).strip()
    return output if output else f"returncode={result.returncode}"


def environment_snapshot() -> dict[str, Any]:
    temperatures: dict[str, Any] = {}
    for path in sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp")):
        try:
            temperatures[path.parent.name] = int(path.read_text().strip()) / 1000.0
        except (OSError, TypeError, ValueError):
            temperatures[path.parent.name] = "unavailable"
    return {
        "schema_version": 1,
        "observation_class": "I1_PREFLIGHT_ENVIRONMENT_CAPABILITY",
        "uname": command_output(["uname", "-a"]),
        "architecture": command_output(["uname", "-m"]),
        "jetson_board": command_output(["bash", "-lc", "tr -d '\\0' < /proc/device-tree/model"])
        if Path("/proc/device-tree/model").exists() else "unavailable",
        "l4t_release": command_output(["bash", "-lc", "cat /etc/nv_tegra_release 2>/dev/null"]),
        "jetpack": "unavailable unless exposed by platform tools",
        "cuda": command_output(["bash", "-lc", "nvcc --version 2>/dev/null || cat /usr/local/cuda/version.json 2>/dev/null"]),
        "tensorrt": command_output(["bash", "-lc", "trtexec --version 2>/dev/null || dpkg-query -W -f='${Version}' tensorrt 2>/dev/null"]),
        "opencv": command_output(["pkg-config", "--modversion", "opencv4"]),
        "power_mode": command_output(["nvpmodel", "-q"]),
        "clock_state": command_output(["jetson_clocks", "--show"]),
        "cpu_affinity_contract": "0-5",
        "observed_process_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else "unavailable",
        "opencv_threads_contract": 1,
        "swap_zram": command_output(["bash", "-lc", "cat /proc/swaps 2>/dev/null"]),
        "temperatures_c": temperatures,
        "fan_state": command_output(["bash", "-lc", "for f in /sys/class/thermal/cooling_device*/cur_state; do printf '%s=' \"$f\"; cat \"$f\"; done 2>/dev/null"]),
        "background_load": command_output(["bash", "-lc", "ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -12"]),
        "start_end_time_source": "each run_manifest process_wall_start/end_utc",
    }


def recursive_keys(value: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            keys.add(path)
            keys.update(recursive_keys(child, path))
    elif isinstance(value, list):
        for child in value:
            keys.update(recursive_keys(child, prefix + "[]"))
    return keys


def validate_run(run_dir: Path, variant: str, measured: int, manifest_entries: list[dict[str, Any]]) -> dict[str, Any]:
    result = load_json(run_dir / "result.json")
    metrics = load_json(run_dir / "metrics.json")
    hashes = load_json(run_dir / "hashes.json")
    run_manifest = load_json(run_dir / "run_manifest.json")
    errors: list[str] = []
    if set(result) != RESULT_TOP_FIELDS:
        errors.append(f"result top-level fields differ: {sorted(result)}")
    if result.get("schema_version") != 4:
        errors.append("result schema_version != 4")
    images = result.get("images", [])
    if len(images) != measured:
        errors.append(f"image count {len(images)} != {measured}")
    field_sets = {frozenset(frame) for frame in images}
    if field_sets != {frozenset(PER_FRAME_FIELDS)}:
        errors.append(f"per-frame fields differ: {[sorted(fields) for fields in field_sets]}")
    if any("timing_ms" in key or "timing" in key for key in recursive_keys(result)):
        errors.append("internal timing field found in result")
    for index, frame in enumerate(images):
        if frame.get("sequence_index") != index:
            errors.append(f"sequence index mismatch at {index}")
            break
        expected = manifest_entries[index % len(manifest_entries)]["image_path"]
        if frame.get("relative_path") != expected:
            errors.append(f"manifest order mismatch at {index}")
            break
        if (frame.get("width"), frame.get("height")) != (200, 200):
            errors.append(f"image dimensions mismatch at {index}")
            break
    for field, expected in (("evidence_class", "NOT_FORMAL_PERFORMANCE_EVIDENCE"),
                            ("execution_mode", "PREFLIGHT_ONLY"),
                            ("profiling_mode", "off")):
        if run_manifest.get(field) != expected:
            errors.append(f"run_manifest {field} mismatch")
    if run_manifest.get("timing_enabled_config") is not False or run_manifest.get("timing_enabled_metadata") is not False:
        errors.append("effective timing is not false")
    if run_manifest.get("internal_timing_fields") is not False or run_manifest.get("per_frame_timing_field") is not False:
        errors.append("timing field contract is not false")
    if run_manifest.get("processed_frames") != measured or run_manifest.get("drop_count") != 0:
        errors.append("processed/drop count mismatch")
    if run_manifest.get("eos") is not True or run_manifest.get("worker_join") is not True:
        errors.append("EOS or worker join failed")
    if metrics.get("processed_frames") != measured or metrics.get("drop_count") != 0 or metrics.get("eos") is not True:
        errors.append("metrics count/EOS mismatch")
    latency = metrics.get("latency_ms")
    if not isinstance(latency, list) or len(latency) != measured or any(not isinstance(v, (int, float)) or v < 0 for v in latency):
        errors.append("latency samples incomplete or non-finite")
    detection_sha = hashes.get("detection_sha256", "")
    if not isinstance(detection_sha, str) or len(detection_sha) != 64:
        errors.append("invalid detection SHA")
    return {
        "variant": variant,
        "run_dir": str(run_dir),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "schema_version": result.get("schema_version"),
        "top_level_fields": sorted(result),
        "per_frame_fields": sorted(PER_FRAME_FIELDS),
        "detection_sha256": detection_sha,
        "processed_frames": run_manifest.get("processed_frames"),
        "drop_count": run_manifest.get("drop_count"),
        "evidence_class": run_manifest.get("evidence_class"),
        "timing_enabled": run_manifest.get("timing_enabled_metadata"),
        "profiling_mode": run_manifest.get("profiling_mode"),
        "latency_sample_count": len(latency) if isinstance(latency, list) else 0,
    }


def main() -> int:
    import argparse
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--repo-root", type=Path, default=Path("."))
        parser.add_argument("--output-root", type=Path, required=True)
        parser.add_argument("--evidence-dir", type=Path, required=True)
        parser.add_argument("--runner", type=Path, default=Path("stage_r_phase0_5d_timing_aligned_runner"))
        parser.add_argument("--config-validator", type=Path, default=Path("stage_r_phase0_5d_config_validator"))
        parser.add_argument("--measured-frames", type=int, default=16)
        args = parser.parse_args()
        output_root = args.output_root
        evidence_dir = args.evidence_dir
        if output_root.exists():
            fail(f"preflight output root already exists: {output_root}")
        output_root.mkdir(parents=True)
        if not HISTORICAL_ROOT.is_dir():
            fail(f"historical result root missing for preservation check: {HISTORICAL_ROOT}")
        configs = {}
        import yaml
        for variant, path in (("V0", V0_CONFIG), ("V2R", V2R_CONFIG), ("V3R", V3R_CONFIG)):
            configs[variant] = yaml.safe_load(path.read_text())
        validator_output = output_root / "config_validator_output.json"
        validator = subprocess.run([
            str(args.config_validator.resolve()), "--v0", str(V0_CONFIG), "--v2r", str(V2R_CONFIG),
            "--v3r", str(V3R_CONFIG), "--output", str(validator_output),
        ], text=True, capture_output=True, check=False)
        (output_root / "config_validator_stdout.log").write_text(validator.stdout)
        (output_root / "config_validator_stderr.log").write_text(validator.stderr)
        if validator.returncode != 0:
            fail(f"config validator failed: {validator.stderr.strip()}")
        diff = config_diff(configs)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "config_diff.json").write_text(json.dumps(diff, indent=2, sort_keys=True) + "\n")
        if diff["status"] != "PASS":
            fail("hidden configuration differences found")

        manifest_path = Path("results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json")
        manifest = load_json(manifest_path)
        entries = manifest["entries"]
        schedule = {
            "schema_version": 1,
            "schedule_id": "stage_r_v0_v2r_v3r_timing_aligned_v1",
            "execution_mode": "PREFLIGHT_ONLY",
            "formal_schedule_status": "FROZEN_NOT_RUN",
            "sets": [
                ["V0", "V2R", "V3R"], ["V3R", "V2R", "V0"],
                ["V2R", "V0", "V3R"], ["V0", "V3R", "V2R"],
                ["V2R", "V3R", "V0"],
            ],
            "positions": 15,
            "each_variant_count": {variant: 5 for variant in VARIANTS},
        }
        if len(schedule["sets"]) != 5 or any(sorted(item) != sorted(VARIANTS) for item in schedule["sets"]):
            fail("frozen schedule is invalid")
        schedule_bytes = json.dumps(schedule, sort_keys=True, separators=(",", ":")).encode()
        schedule["schedule_sha256"] = hashlib.sha256(schedule_bytes).hexdigest()
        (evidence_dir / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n")

        env = environment_snapshot()
        (evidence_dir / "environment.json").write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
        source_files = [
            Path("tools/benchmark/stage_r_phase0_5d_timing_aligned_runner.cpp"),
            Path("src/serial_runner.cpp"), Path("stage_r/pageable_runner.cpp"),
            Path("stage_r/pinned_runner.cpp"), Path("src/runtime_config.cpp"),
            Path("src/result_sink.cpp"), Path("src/canonical_hash_sink.cpp"),
            Path("src/corpus_replay_source.cpp"),
        ]
        source_identity = {"commit": command_output(["git", "rev-parse", "HEAD"]),
                           "files": {str(path): sha256(path) for path in source_files}}
        (evidence_dir / "source_identity.json").write_text(json.dumps(source_identity, indent=2, sort_keys=True) + "\n")

        # Verify the runner's refusal to reuse an existing directory without
        # touching the historical Attempt 2 result root.
        probe = output_root / "existing_output_probe"
        probe.mkdir()
        sentinel = probe / "sentinel.txt"
        sentinel.write_text("preserve")
        refusal_command = [
            str(args.runner.resolve()),
            "--config", str(V0_CONFIG), "--manifest", str(manifest_path),
            "--output-dir", str(probe), "--warmup-frames", "1", "--measured-frames", "1",
            "--execution-mode", "PREFLIGHT_ONLY",
        ]
        refusal = subprocess.run(refusal_command, text=True, capture_output=True, check=False)
        (evidence_dir / "output_root_policy.json").write_text(json.dumps({
            "historical_root": str(HISTORICAL_ROOT),
            "historical_root_exists": HISTORICAL_ROOT.is_dir(),
            "new_root": str(output_root),
            "existing_directory_probe": str(probe),
            "sentinel_preserved": sentinel.read_text() == "preserve",
            "refusal_returncode": refusal.returncode,
            "refusal_pass": refusal.returncode == 2,
        }, indent=2) + "\n")

        runs = []
        for variant in VARIANTS:
            run_dir = output_root / "runs" / f"preflight_{variant.lower()}"
            run_dir.parent.mkdir(parents=True, exist_ok=True)
            command = [
            str(args.runner.resolve()),
                "--config", str({"V0": V0_CONFIG, "V2R": V2R_CONFIG, "V3R": V3R_CONFIG}[variant]),
                "--manifest", str(manifest_path), "--output-dir", str(run_dir),
                "--warmup-frames", "3", "--measured-frames", str(args.measured_frames),
                "--execution-mode", "PREFLIGHT_ONLY",
            ]
            completed = subprocess.run(command, text=True, capture_output=True, check=False)
            (output_root / f"{variant.lower()}_stdout.log").write_text(completed.stdout)
            (output_root / f"{variant.lower()}_stderr.log").write_text(completed.stderr)
            if completed.returncode == 0:
                runs.append(validate_run(run_dir, variant, args.measured_frames, entries))
            else:
                runs.append({"variant": variant, "status": "FAIL", "returncode": completed.returncode,
                             "stdout": completed.stdout[-1000:], "stderr": completed.stderr[-1000:]})

        passing = [row for row in runs if row.get("status") == "PASS"]
        schema_comparison = {
            "schema_version_equal": len({row.get("schema_version") for row in passing}) == 1 and len(passing) == 3,
            "top_level_fields_equal": len({tuple(row.get("top_level_fields", [])) for row in passing}) == 1 and len(passing) == 3,
            "per_frame_fields_equal": len({tuple(row.get("per_frame_fields", [])) for row in passing}) == 1 and len(passing) == 3,
            "internal_timing_field_absent": len(passing) == 3,
            "runs": runs,
        }
        (evidence_dir / "schema_field_comparison.json").write_text(json.dumps(schema_comparison, indent=2, sort_keys=True) + "\n")
        shas = {row["variant"]: row.get("detection_sha256") for row in passing}
        validity = {
            "schema_version": 1,
            "decision": "HARNESS_READY_FOR_FORMAL_RUN" if len(passing) == 3 and
                schema_comparison["schema_version_equal"] and schema_comparison["top_level_fields_equal"] and
                schema_comparison["per_frame_fields_equal"] and shas.get("V2R") == shas.get("V3R") else "HARNESS_INVALID",
            "evidence_class": "NOT_FORMAL_PERFORMANCE_EVIDENCE",
            "formal_schedule": "NOT RUN",
            "preflight_metrics": "NOT FORMAL PERFORMANCE EVIDENCE",
            "v2r_v3r_detection_identity_pass": shas.get("V2R") == shas.get("V3R"),
            "runs": runs,
        }
        (evidence_dir / "preflight_validity.json").write_text(json.dumps(validity, indent=2, sort_keys=True) + "\n")
        (evidence_dir / "preflight_manifest.json").write_text(json.dumps({
            "schema_version": 1, "execution_mode": "PREFLIGHT_ONLY",
            "evidence_class": "NOT_FORMAL_PERFORMANCE_EVIDENCE",
            "output_root": str(output_root), "measured_frames": args.measured_frames,
            "runs": runs, "historical_result_root_preserved": True,
        }, indent=2, sort_keys=True) + "\n")
        if validity["decision"] != "HARNESS_READY_FOR_FORMAL_RUN":
            fail(validity["decision"])
        print("HARNESS_READY_FOR_FORMAL_RUN")
        return 0
    except Exception as exc:
        print(f"HARNESS_INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
