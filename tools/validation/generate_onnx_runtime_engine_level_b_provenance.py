#!/usr/bin/env python3
"""Generate stable provenance for M2 Level B evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate provenance for ONNX Runtime Engine Level B evidence."
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "input_manifest.json"
    report_path = output_dir / "comparison_report.json"
    cpp_output_path = output_dir / "cpp_output.f32le"
    required_paths = (manifest_path, report_path, cpp_output_path)
    if any(not path.is_file() for path in required_paths):
        raise ValueError("Level B manifest, report, and C++ output must exist")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    provenance = {
        "schema_version": 1,
        "evidence_id": "onnx_runtime_engine_level_b",
        "python_environment": manifest["environment"],
        "cpp_environment": report["cpp_environment"],
        "model": manifest["model"],
        "input": manifest["input"],
        "files": {
            "input_manifest": {
                "path": "results/validation/onnx_runtime_engine_level_b/input_manifest.json",
                "sha256": sha256_file(manifest_path),
            },
            "python_golden_output": manifest["python_golden_output"],
            "cpp_output": {
                "path": "results/validation/onnx_runtime_engine_level_b/cpp_output.f32le",
                "sha256": sha256_file(cpp_output_path),
            },
            "comparison_report": {
                "path": "results/validation/onnx_runtime_engine_level_b/comparison_report.json",
                "sha256": sha256_file(report_path),
            },
        },
        "comparison": report["comparison"],
    }
    output_path = output_dir / "provenance.json"
    output_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"Level B provenance: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
