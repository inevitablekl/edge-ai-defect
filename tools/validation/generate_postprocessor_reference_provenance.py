#!/usr/bin/env python3
"""Generate stable provenance for M3.5 PostProcessor-only Validation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np

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
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument(
        "--source-worktree-clean",
        choices=("true",),
        required=True,
        help="Assert that the source snapshot was clean before evidence generation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = args.data_root.resolve()
    results_root = args.results_root.resolve()
    source_commit = args.source_commit
    if len(source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in source_commit
    ):
        raise ValueError("source_commit must be a full lowercase Git SHA")
    subprocess.check_call(
        ["git", "cat-file", "-e", f"{source_commit}^{{commit}}"], cwd=REPO_ROOT
    )
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
        comparison = report["comparison"]
        cases[case_dir.name] = {
            "manifest": {"path": manifest_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(manifest_path)},
            "raw_output": manifest["raw_output"],
            "metadata": manifest["metadata"],
            "config": manifest["config"],
            "python_golden_detections": manifest["python_golden_detections"],
            "cpp_detections": {"path": cpp_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(cpp_path)},
            "comparison_report": {"path": report_path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(report_path)},
            "detection_count": comparison["cpp_detection_count"],
            "result": "PASS" if comparison["pass"] else "FAIL",
            "comparison": comparison,
        }
    source_files = {
        "python_reference": "tools/validation/postprocessor_reference.py",
        "asset_generator": "tools/validation/generate_postprocessor_reference_assets.py",
        "provenance_generator": "tools/validation/generate_postprocessor_reference_provenance.py",
        "validator": "tests/test_postprocessor_reference.cpp",
        "malformed_ctest_driver": "tests/cmake/verify_postprocessor_reference_malformed.cmake",
        "cmake_lists": "CMakeLists.txt",
    }
    provenance = {
        "schema_version": 2,
        "evidence_id": "postprocessor_only",
        "source_commit": source_commit,
        "source_branch": args.source_branch,
        "source_worktree_clean": True,
        "environment": {"python_version": platform.python_version(), "numpy_version": np.__version__, "cmake_version": run("cmake", "--version").splitlines()[0], "cpp_compiler": run("c++", "--version").splitlines()[0], "os": platform.platform(), "architecture": platform.machine()},
        "ultralytics_semantic_source_version": "8.4.50 (not a runtime dependency)",
        "source_files": {
            path: {"path": path, "sha256": sha256_file(REPO_ROOT / path)}
            for path in source_files.values()
        },
        "validation_commands": [
            "./.venv/bin/python tools/validation/generate_postprocessor_reference_assets.py --output-root tests/data/postprocessor_reference",
            "./.venv/bin/python tools/validation/postprocessor_reference.py --data-root tests/data/postprocessor_reference",
            "build/tests/test_postprocessor_reference --data-root tests/data/postprocessor_reference --cpp-output-root results/validation/postprocessor_only --report-root results/validation/postprocessor_only",
            "ctest --test-dir build --output-on-failure -R '^postprocessor_reference(_.*)?$'",
        ],
        "thresholds": {
            "confidence_abs": 1.0e-6,
            "bbox_coordinate_abs": 1.0e-4,
            "exact_fields": [
                "detection_count",
                "order",
                "class_id",
                "candidate_index",
            ],
        },
        "overall_result": "PASS",
        "cases": cases,
    }
    results_root.mkdir(parents=True, exist_ok=True)
    output_path = results_root / "provenance.json"
    output_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"PostProcessor-only provenance: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
