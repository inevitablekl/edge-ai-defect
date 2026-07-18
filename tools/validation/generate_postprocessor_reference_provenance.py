#!/usr/bin/env python3
"""Generate stable provenance for M3.5 PostProcessor-only Validation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=REPO_ROOT, text=True).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate M3.5 evidence provenance.")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = args.data_root.resolve()
    results_root = args.results_root.resolve()
    cases: dict[str, object] = {}
    for case_dir in sorted(path for path in data_root.iterdir() if path.is_dir() and path.name.startswith("case_")):
        result_dir = results_root / case_dir.name
        manifest_path = case_dir / "manifest.json"
        cpp_path = result_dir / "cpp_detections.tsv"
        report_path = result_dir / "comparison_report.json"
        if not manifest_path.is_file() or not cpp_path.is_file() or not report_path.is_file():
            raise ValueError(f"Missing M3.5 evidence for {case_dir.name}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if not report["comparison"]["pass"]:
            raise ValueError(f"Cannot generate PASS provenance from failed case {case_dir.name}")
        cases[case_dir.name] = {
            "manifest": {"path": manifest_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(manifest_path)},
            "raw_output": manifest["raw_output"],
            "metadata": manifest["metadata"],
            "config": manifest["config"],
            "python_golden_detections": manifest["python_golden_detections"],
            "cpp_detections": {"path": cpp_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(cpp_path)},
            "comparison_report": {"path": report_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(report_path)},
            "comparison": report["comparison"],
        }
    provenance = {
        "schema_version": 1,
        "evidence_id": "postprocessor_only",
        "git": {"branch": run("git", "branch", "--show-current"), "commit": run("git", "rev-parse", "HEAD"), "status_short": run("git", "status", "--short")},
        "environment": {"python_version": platform.python_version(), "cmake_version": run("cmake", "--version").splitlines()[0], "cpp_compiler": run("c++", "--version").splitlines()[0], "os": platform.platform(), "architecture": platform.machine()},
        "ultralytics_semantic_source_version": "8.4.50 (not a runtime dependency)",
        "reference_script": {"path": "tools/validation/postprocessor_reference.py", "sha256": sha256_file(REPO_ROOT / "tools/validation/postprocessor_reference.py")},
        "validation_command": "ctest --test-dir build --output-on-failure -R '^postprocessor_reference$'",
        "thresholds": {"confidence_abs": 1.0e-6, "bbox_coordinate_abs": 1.0e-4},
        "cases": cases,
    }
    results_root.mkdir(parents=True, exist_ok=True)
    output_path = results_root / "provenance.json"
    output_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"PostProcessor-only provenance: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
