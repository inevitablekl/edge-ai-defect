#!/usr/bin/env python3
"""M5.2A temporary Level C dry-run orchestrator."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from m5_level_c_common import ContractError, InitError, atomic_write, read_yaml
from m5_level_c_compare import compare
from m5_level_c_reference import run_reference


class RunnerError(RuntimeError):
    pass


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run_cpp(executable: Path, config_path: Path, expected_output: Path, work_dir: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(executable.resolve()), "--config", str(config_path.resolve())], cwd=str(work_dir.resolve()), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RunnerError(f"C++ subprocess failed with exit {result.returncode}: {result.stderr.strip()}")
    if not expected_output.is_file():
        raise RunnerError("C++ subprocess succeeded without output JSON")
    return result


def _write_cpp_config(base_config: dict, path: Path, input_dir: Path, output_path: Path) -> None:
    config = {key: value for key, value in base_config.items()}
    config["input"] = {"type": "directory", "directory": str(input_dir.resolve())}
    config["output"] = {"json_path": str(output_path.resolve()), "console": False, "overwrite": True}
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def run_dry(config_path: Path, prepared_input_dir: Path, cpp_executable: Path, work_dir: Path) -> dict:
    if work_dir.exists():
        raise InitError("work-dir must not already exist")
    if "results" in work_dir.parts and "validation" in work_dir.parts:
        raise InitError("formal results directory is forbidden in M5.2A")
    if not cpp_executable.is_file():
        raise InitError(f"C++ executable does not exist: {cpp_executable}")
    if not prepared_input_dir.is_dir():
        raise InitError(f"prepared input directory does not exist: {prepared_input_dir}")
    base_config = read_yaml(config_path)
    work_dir.mkdir(parents=True, exist_ok=True)
    created = True
    try:
        python_outputs = [work_dir / "python_run_1.json", work_dir / "python_run_2.json"]
        cpp_outputs = [work_dir / "cpp_run_1.json", work_dir / "cpp_run_2.json"]
        cpp_configs = [work_dir / "runtime_run_1.yaml", work_dir / "runtime_run_2.yaml"]
        for index, output in enumerate(python_outputs):
            run_reference(config_path, prepared_input_dir, output)
        if python_outputs[0].read_bytes() != python_outputs[1].read_bytes():
            raise RunnerError("Python Run 1 and Run 2 are not byte-identical")
        for config_output, cpp_output in zip(cpp_configs, cpp_outputs):
            _write_cpp_config(base_config, config_output, prepared_input_dir, cpp_output)
            _run_cpp(cpp_executable, config_output, cpp_output, work_dir)
        if cpp_outputs[0].read_bytes() != cpp_outputs[1].read_bytes():
            raise RunnerError("C++ Run 1 and Run 2 are not byte-identical")
        report, passed = compare(python_outputs[0], cpp_outputs[0])
        atomic_write(work_dir / "comparison_report.json", report)
        if not passed:
            raise RunnerError("semantic comparison failed")
        summary = {"status": "PASS", "python_run_1_sha256": _sha(python_outputs[0]), "python_run_2_sha256": _sha(python_outputs[1]), "cpp_run_1_sha256": _sha(cpp_outputs[0]), "cpp_run_2_sha256": _sha(cpp_outputs[1]), "comparison_report": "comparison_report.json", "image_count": report["aggregate"]["image_count"], "passed_images": report["aggregate"]["passed_images"], "max_confidence_abs_error": max((item["max_confidence_abs_error"] for item in report["image_results"]), default=0.0), "max_bbox_coordinate_abs_error": max((item["max_bbox_coordinate_abs_error"] for item in report["image_results"]), default=0.0)}
        (work_dir / "commands.txt").write_text("python reference run 1\npython reference run 2\ncpp application run 1\ncpp application run 2\nsemantic comparator\n", encoding="utf-8")
        atomic_write(work_dir / "dry_run_summary.json", summary)
        return summary
    except Exception:
        if created:
            shutil.rmtree(work_dir, ignore_errors=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a temporary M5.2A Level C dry run.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--prepared-input-dir", required=True, type=Path)
    parser.add_argument("--cpp-executable", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        summary = run_dry(args.config, args.prepared_input_dir, args.cpp_executable, args.work_dir)
        print(f"dry-run PASS: {summary['passed_images']}/{summary['image_count']} images")
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except (ContractError, InitError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except RunnerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
