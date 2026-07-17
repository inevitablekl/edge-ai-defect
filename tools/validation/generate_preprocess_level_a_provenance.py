#!/usr/bin/env python3
"""Generate deterministic provenance for preprocessing Level A evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


EVIDENCE_FILES = (
    ("generator", "tools/validation/generate_preprocess_level_a.py"),
    ("validator", "tests/test_preprocess_level_a.cpp"),
    ("manifest_parser", "tests/preprocess_level_a_manifest.cpp"),
    ("compare_helper", "tests/preprocess_level_a_compare.cpp"),
    ("manifest", "tests/data/preprocess_level_a/manifest.yaml"),
    ("sha256sums", "tests/data/preprocess_level_a/SHA256SUMS"),
    ("formal_report", "results/validation/preprocess_level_a/level_a_report.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic preprocessing Level A provenance."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_report_contract(report: dict[str, object]) -> None:
    aggregate = report.get("aggregate")
    frozen_case = report.get("frozen_case")
    reference = report.get("reference")
    cpp = report.get("cpp")
    if not isinstance(aggregate, dict) or not isinstance(frozen_case, dict):
        raise ValueError("formal report is missing aggregate or frozen_case")
    if not isinstance(reference, dict) or not isinstance(cpp, dict):
        raise ValueError("formal report is missing reference environment")
    if aggregate.get("case_count") != 8 or aggregate.get("passed_case_count") != 8:
        raise ValueError("formal report must contain 8/8 passing cases")
    if aggregate.get("final_pass") is not True:
        raise ValueError("formal report final_pass must be true")
    if aggregate.get("max_mae") != 0 or aggregate.get("max_abs") != 0:
        raise ValueError("formal report aggregate errors must be zero")
    if frozen_case.get("target_shape") != [1, 3, 640, 640]:
        raise ValueError("formal report frozen input shape is not [1,3,640,640]")
    expected_versions = {
        "python_version": "3.10.12",
        "numpy_version": "1.26.4",
        "opencv_version": "4.10.0",
    }
    for key, expected in expected_versions.items():
        if reference.get(key) != expected:
            raise ValueError(f"formal report {key} must be {expected}")
    if cpp.get("opencv_version") != "4.5.4":
        raise ValueError("formal report C++ OpenCV version must be 4.5.4")


def generate(repo_root: Path, source_commit: str, output: Path) -> None:
    if re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("source commit must be 40 lowercase hexadecimal characters")
    repo_root = repo_root.resolve(strict=True)
    evidence: dict[str, dict[str, str]] = {}
    for key, relative in EVIDENCE_FILES:
        path = repo_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"evidence file does not exist: {relative}")
        evidence[key] = {"path": relative, "sha256": sha256_file(path)}

    report_path = repo_root / dict(EVIDENCE_FILES)["formal_report"]
    with report_path.open("r", encoding="utf-8") as input_file:
        report = json.load(input_file)
    if not isinstance(report, dict):
        raise ValueError("formal report root must be an object")
    require_report_contract(report)

    provenance: dict[str, object] = {
        "schema_version": 1,
        "evidence_id": "preprocess_level_a",
        "source_commit": source_commit,
        **evidence,
        "environment": {
            "python_version": "3.10.12",
            "numpy_version": "1.26.4",
            "python_opencv_version": "4.10.0",
            "cpp_opencv_version": "4.5.4",
        },
        "case_count": 8,
        "frozen_input_shape": [1, 3, 640, 640],
        "final_result": "PASS",
        "mae_aggregate": 0,
        "max_abs_aggregate": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    generate(args.repo_root, args.source_commit, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
