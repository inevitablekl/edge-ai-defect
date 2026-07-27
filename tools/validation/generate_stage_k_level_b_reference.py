#!/usr/bin/env python3
"""Freeze the Stage K K5.1 Python ORT 16-tensor reference bundle.

This is intentionally a thin raw-tensor generator.  It owns corpus/model/
environment checks, frozen preprocessing, one CPU-only ORT session, and the
bundle metadata.  It does not perform NMS, confidence filtering, or any other
postprocessing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import onnxruntime as ort

from m5_level_c_common import load_model_contract, preprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COMMIT = "c9586c219178eeec17864c8c2cf75a1d5bc90101"
EXPECTED_BRANCH = "feature/jetson-tensorrt-fp16"
EXPECTED_CORPUS_SHA256 = "687682f37d1affbe8813a9e7287b42dc28a9a8b9ea8d67f8b85175960f3e2dcd"
EXPECTED_MODEL_SHA256 = "c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944"
EXPECTED_CONTRACT_SHA256 = "9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190"
EXPECTED_ORT = "1.23.2"
EXPECTED_OPENCV = "4.10.0"
EXPECTED_NUMPY = "1.26.4"
INPUT_SHAPE = [1, 3, 640, 640]
OUTPUT_SHAPE = [1, 10, 8400]
INPUT_ELEMENTS = 1_228_800
OUTPUT_ELEMENTS = 84_000
INPUT_BYTES = INPUT_ELEMENTS * 4
OUTPUT_BYTES = OUTPUT_ELEMENTS * 4
MODEL_PATH = REPO_ROOT / "models/onnx/yolov8n_neudet_frozen.onnx"
CONTRACT_PATH = REPO_ROOT / "configs/model_contracts/yolov8n_neudet_frozen.yaml"
GENERATOR_PATH = Path(__file__).resolve()
SOURCE_CORPUS_LOGICAL_PATH = "results/validation/jetson_ort_level_c/j4_3_level_c_v2/corpus_manifest.json"


class GenerationError(RuntimeError):
    """A K5.1 precondition or generation contract failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_atomic(path: Path, data: bytes, *, refuse_existing: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if refuse_existing and path.exists():
        raise GenerationError(f"refusing to overwrite existing file: {path}")
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: Any, *, refuse_existing: bool = True) -> None:
    raw = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    write_atomic(path, raw.encode("utf-8"), refuse_existing=refuse_existing)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def validate_git_state() -> tuple[str, str]:
    branch = git_value("branch", "--show-current")
    commit = git_value("rev-parse", "HEAD")
    if branch != EXPECTED_BRANCH or commit != EXPECTED_COMMIT:
        raise GenerationError(f"source git state mismatch: branch={branch}, commit={commit}")
    return branch, commit


def validate_environment() -> dict[str, Any]:
    if sys.version_info[:3] != (3, 10, 12):
        raise GenerationError(f"Python version mismatch: {platform.python_version()}")
    if ort.__version__ != EXPECTED_ORT:
        raise GenerationError(f"ONNX Runtime version mismatch: {ort.__version__}")
    if cv2.__version__ != EXPECTED_OPENCV:
        raise GenerationError(f"OpenCV version mismatch: {cv2.__version__}")
    if np.__version__ != EXPECTED_NUMPY:
        raise GenerationError(f"NumPy version mismatch: {np.__version__}")
    if "CPUExecutionProvider" not in ort.get_available_providers():
        raise GenerationError("CPUExecutionProvider is unavailable")
    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "onnxruntime_version": ort.__version__,
        "onnxruntime_available_providers": ort.get_available_providers(),
        "onnxruntime_providers": ["CPUExecutionProvider"],
        "opencv_version": cv2.__version__,
        "numpy_version": np.__version__,
    }


def validate_frozen_files() -> tuple[str, str]:
    model_sha = sha256_file(MODEL_PATH)
    contract_sha = sha256_file(CONTRACT_PATH)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise GenerationError("frozen ONNX SHA256 mismatch")
    if contract_sha != EXPECTED_CONTRACT_SHA256:
        raise GenerationError("frozen ModelContract SHA256 mismatch")
    try:
        contract = load_model_contract(CONTRACT_PATH, MODEL_PATH)["source"]
    except Exception as exc:
        raise GenerationError(f"frozen ModelContract could not be validated: {exc}") from exc
    if contract["input"] != {"name": "images", "dtype": "float32", "layout": "NCHW", "shape": INPUT_SHAPE}:
        raise GenerationError("frozen ModelContract input identity mismatch")
    if contract["output"] != {"name": "output0", "dtype": "float32", "layout": "BCN", "shape": OUTPUT_SHAPE}:
        raise GenerationError("frozen ModelContract output identity mismatch")
    return model_sha, contract_sha


def create_deterministic_archive(bundle_dir: Path, archive_path: Path) -> None:
    if archive_path.exists():
        raise GenerationError(f"refusing to overwrite existing archive: {archive_path}")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive_path.with_name(f".{archive_path.name}.tmp")
    if temporary.exists():
        raise GenerationError(f"temporary archive path already exists: {temporary}")
    try:
        with temporary.open("wb") as raw_archive:
            with gzip.GzipFile(fileobj=raw_archive, mode="wb", filename="", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                    paths = [bundle_dir] + sorted(bundle_dir.rglob("*"), key=lambda item: item.relative_to(bundle_dir).as_posix())
                    for path in paths:
                        relative = path.relative_to(bundle_dir).as_posix()
                        arcname = f"{bundle_dir.name}/{relative}" if relative != "." else bundle_dir.name
                        info = archive.gettarinfo(str(path), arcname=arcname)
                        info.uid = 0
                        info.gid = 0
                        info.uname = ""
                        info.gname = ""
                        info.mtime = 0
                        if path.is_file():
                            with path.open("rb") as stream:
                                archive.addfile(info, stream)
                        else:
                            archive.addfile(info)
            raw_archive.flush()
            os.fsync(raw_archive.fileno())
        os.replace(temporary, archive_path)
    finally:
        temporary.unlink(missing_ok=True)


def read_manifest(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise GenerationError(f"corpus manifest is not a regular file: {path}")
    if sha256_file(path) != EXPECTED_CORPUS_SHA256:
        raise GenerationError("corpus manifest SHA256 mismatch")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"cannot parse corpus manifest: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        raise GenerationError("corpus manifest entries are missing")
    if len(value["entries"]) != 16:
        raise GenerationError("corpus manifest must contain exactly 16 entries")
    return value


def validate_corpus(corpus_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if corpus_dir.is_symlink() or not corpus_dir.is_dir():
        raise GenerationError(f"corpus directory is not a real directory: {corpus_dir}")
    manifest = read_manifest(corpus_dir / "prepared_corpus_manifest.json")
    entries = manifest["entries"]
    jpg_count = sum(Path(entry.get("prepared_filename", "")).suffix.lower() == ".jpg" for entry in entries)
    bmp_count = sum(Path(entry.get("prepared_filename", "")).suffix.lower() == ".bmp" for entry in entries)
    if (jpg_count, bmp_count) != (12, 4):
        raise GenerationError(f"corpus composition mismatch: JPG={jpg_count}, BMP={bmp_count}")
    for index, entry in enumerate(entries):
        filename = entry.get("prepared_filename")
        if not isinstance(filename, str) or not filename.startswith(f"{index:04d}_"):
            raise GenerationError(f"corpus ordering mismatch at index {index}")
        path = corpus_dir / filename
        if path.is_symlink() or not path.is_file():
            raise GenerationError(f"corpus image is not a regular file: {path}")
        if sha256_file(path) != entry.get("prepared_sha256"):
            raise GenerationError(f"corpus image SHA256 mismatch: {filename}")
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None or image.ndim != 3 or image.dtype != np.uint8 or image.shape[2] != 3:
            raise GenerationError(f"corpus image cannot be decoded as BGR: {filename}")
        if [image.shape[1], image.shape[0]] != [entry.get("width"), entry.get("height")]:
            raise GenerationError(f"corpus image dimensions mismatch: {filename}")
    return manifest, entries


def create_session() -> tuple[ort.InferenceSession, dict[str, Any]]:
    options = ort.SessionOptions()
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(MODEL_PATH), sess_options=options, providers=["CPUExecutionProvider"])
    if session.get_providers() != ["CPUExecutionProvider"]:
        raise GenerationError(f"unexpected active ORT providers: {session.get_providers()}")
    inputs, outputs = session.get_inputs(), session.get_outputs()
    if len(inputs) != 1 or len(outputs) != 1:
        raise GenerationError("frozen model must have exactly one input and one output")
    actual_input, actual_output = inputs[0], outputs[0]
    if (actual_input.name, actual_input.type, actual_input.shape) != ("images", "tensor(float)", INPUT_SHAPE):
        raise GenerationError(f"input contract mismatch: {actual_input.name} {actual_input.type} {actual_input.shape}")
    if (actual_output.name, actual_output.type, actual_output.shape) != ("output0", "tensor(float)", OUTPUT_SHAPE):
        raise GenerationError(f"output contract mismatch: {actual_output.name} {actual_output.type} {actual_output.shape}")
    return session, {"input": actual_input, "output": actual_output}


def image_id(filename: str) -> str:
    return Path(filename).stem


def tensor_contract(dtype: str, layout: str, shape: list[int], element_count: int, byte_size: int) -> dict[str, Any]:
    return {"dtype": dtype, "byte_order": "little_endian", "layout": layout, "shape": shape, "element_count": element_count, "byte_size": byte_size}


def generate(args: argparse.Namespace) -> dict[str, Any]:
    branch, commit = validate_git_state()
    environment = validate_environment()
    model_sha, contract_sha = validate_frozen_files()
    corpus_dir = args.corpus_dir.resolve()
    corpus_manifest, corpus_entries = validate_corpus(corpus_dir)
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise GenerationError(f"formal/scratch output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    (output_dir / "inputs").mkdir()
    (output_dir / "reference_outputs").mkdir()
    session, metadata = create_session()
    creation_timestamp = utc_now()
    input_entries: list[dict[str, Any]] = []
    output_entries: list[dict[str, Any]] = []
    tensor_sha_lines: list[str] = []
    try:
        for corpus_entry in corpus_entries:
            filename = corpus_entry["prepared_filename"]
            source = corpus_dir / filename
            image = cv2.imread(str(source), cv2.IMREAD_COLOR)
            input_tensor, _ = preprocess(image)
            if input_tensor.dtype != np.float32 or list(input_tensor.shape) != INPUT_SHAPE or not input_tensor.flags.c_contiguous or not np.isfinite(input_tensor).all():
                raise GenerationError(f"input tensor contract failure: {filename}")
            input_bytes = np.ascontiguousarray(input_tensor, dtype="<f4").tobytes(order="C")
            if len(input_bytes) != INPUT_BYTES:
                raise GenerationError(f"input tensor byte size mismatch: {filename}")
            identifier = image_id(filename)
            input_name = f"inputs/{identifier}.input.f32le"
            output_name = f"reference_outputs/{identifier}.python_ort_output.f32le"
            write_atomic(output_dir / input_name, input_bytes)
            input_sha = sha256_file(output_dir / input_name)
            output_tensor = session.run([metadata["output"].name], {metadata["input"].name: input_tensor})[0]
            if output_tensor.dtype != np.float32 or list(output_tensor.shape) != OUTPUT_SHAPE or not output_tensor.flags.c_contiguous or not np.isfinite(output_tensor).all():
                raise GenerationError(f"raw output contract failure: {filename}")
            output_bytes = np.ascontiguousarray(output_tensor, dtype="<f4").tobytes(order="C")
            if len(output_bytes) != OUTPUT_BYTES:
                raise GenerationError(f"raw output byte size mismatch: {filename}")
            write_atomic(output_dir / output_name, output_bytes)
            output_sha = sha256_file(output_dir / output_name)
            source_sha = corpus_entry["prepared_sha256"]
            input_entry = {
                "image_id": identifier,
                "corpus_relative_identity": filename,
                "source_image_sha256": source_sha,
                "original_width": corpus_entry["width"],
                "original_height": corpus_entry["height"],
                "input_tensor_path": input_name,
                "input_tensor_sha256": input_sha,
                "input_filename": input_name,
                **tensor_contract("float32", "NCHW", INPUT_SHAPE, INPUT_ELEMENTS, INPUT_BYTES),
            }
            input_entries.append(input_entry)
            output_entries.append({
                "image_id": identifier,
                "corpus_relative_identity": filename,
                "source_image_sha256": source_sha,
                "original_width": corpus_entry["width"],
                "original_height": corpus_entry["height"],
                "input_filename": input_name,
                "input_sha256": input_sha,
                "output_filename": output_name,
                "output_sha256": output_sha,
                "output_byte_size": OUTPUT_BYTES,
                **tensor_contract("float32", "BCN", OUTPUT_SHAPE, OUTPUT_ELEMENTS, OUTPUT_BYTES),
                "finite_count": OUTPUT_ELEMENTS,
                "status": "success",
            })
            tensor_sha_lines.extend([f"{input_sha}  {input_name}", f"{output_sha}  {output_name}"])
    except Exception:
        raise
    input_manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_raw_tensor_input_manifest",
        "bundle_id": args.bundle_id,
        "source_git_commit": commit,
        "corpus_manifest_sha256": EXPECTED_CORPUS_SHA256,
        "model_contract_sha256": contract_sha,
        "dtype": "float32",
        "byte_order": "little_endian",
        "layout": "NCHW",
        "shape": INPUT_SHAPE,
        "element_count": INPUT_ELEMENTS,
        "byte_size": INPUT_BYTES,
        "entry_count": len(input_entries),
        "entries": input_entries,
    }
    write_json(output_dir / "input_manifest.json", input_manifest)
    output_manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_raw_tensor_output_manifest",
        "run_id": args.run_id,
        "backend_type": "python_onnxruntime_cpu",
        "source_git_commit": commit,
        "input_manifest_sha256": sha256_file(output_dir / "input_manifest.json"),
        "entry_count": len(output_entries),
        "success_count": len(output_entries),
        "failure_count": 0,
        "overall_status": "SUCCESS",
        "creation_timestamp": creation_timestamp,
        "tensor_contract": tensor_contract("float32", "BCN", OUTPUT_SHAPE, OUTPUT_ELEMENTS, OUTPUT_BYTES),
        "limitations": ["raw Python ORT reference only", "no preprocessing in runner", "no postprocessing"],
        "entries": output_entries,
    }
    write_json(output_dir / "reference_output_manifest.json", output_manifest)
    common = {
        "schema_version": 1,
        "bundle_id": args.bundle_id,
        "source_git_commit": commit,
        "source_branch": branch,
        "corpus_manifest_sha256": EXPECTED_CORPUS_SHA256,
        "model_onnx_sha256": model_sha,
        "model_contract_sha256": contract_sha,
        "generator_script_sha256": sha256_file(GENERATOR_PATH),
        "creation_timestamp": creation_timestamp,
        "entry_count": len(input_entries),
    }
    bundle_manifest = {
        "schema_version": 1,
        "bundle_id": args.bundle_id,
        "artifact_kind": "stage_k_level_b_reference_bundle",
        "generator_script_path": repo_relative(GENERATOR_PATH),
        "generator_script_sha256": common["generator_script_sha256"],
        "source_git_commit": commit,
        "source_branch": branch,
        "source_corpus_manifest_path": SOURCE_CORPUS_LOGICAL_PATH,
        "source_corpus_manifest_sha256": EXPECTED_CORPUS_SHA256,
        "model_path": repo_relative(MODEL_PATH),
        "model_onnx_sha256": model_sha,
        "model_contract_path": repo_relative(CONTRACT_PATH),
        "model_contract_sha256": contract_sha,
        **{key: environment[key] for key in ("python_version", "python_executable", "platform", "architecture", "onnxruntime_version", "onnxruntime_providers", "opencv_version", "numpy_version")},
        "preprocess_contract_identity": "frozen_m5_level_c_common.preprocess_letterbox_bgr_rgb_nchw_float32_v1",
        "input_tensor_contract": tensor_contract("float32", "NCHW", INPUT_SHAPE, INPUT_ELEMENTS, INPUT_BYTES),
        "raw_output_tensor_contract": tensor_contract("float32", "BCN", OUTPUT_SHAPE, OUTPUT_ELEMENTS, OUTPUT_BYTES),
        "creation_timestamp": creation_timestamp,
        "entry_count": len(input_entries),
        "limitations": [
            "Generated on WSL2 x86_64.",
            "Python ORT Reference is authoritative.",
            "TensorRT was not executed in this round.",
            "No Level C or final K5 disposition was performed.",
            "Byte-identical regeneration is not required for bundle identity, but was checked in this round.",
            "Bundle identity is frozen by the corpus manifest and file SHA values.",
            "No NMS, confidence filtering, inverse LetterBox, or detection serialization was performed.",
        ],
        "entries": [
            {**input_entry, "input": {"filename": input_entry["input_tensor_path"], "sha256": input_entry["input_tensor_sha256"], "byte_size": INPUT_BYTES, "dtype": "float32", "byte_order": "little_endian", "layout": "NCHW", "shape": INPUT_SHAPE, "element_count": INPUT_ELEMENTS, "finite_count": INPUT_ELEMENTS}, "reference_output": {"filename": output_entry["output_filename"], "sha256": output_entry["output_sha256"], "byte_size": OUTPUT_BYTES, "dtype": "float32", "byte_order": "little_endian", "layout": "BCN", "shape": OUTPUT_SHAPE, "element_count": OUTPUT_ELEMENTS, "finite_count": OUTPUT_ELEMENTS}}
            for input_entry, output_entry in zip(input_entries, output_entries)
        ],
    }
    write_json(output_dir / "bundle_manifest.json", bundle_manifest)
    generation_report = {
        **common,
        "artifact_kind": "stage_k_level_b_reference_generation_report",
        "status": "COMPLETE",
        "corpus": {"path": str(corpus_dir), "entry_count": 16, "jpg_count": 12, "bmp_count": 4, "manifest_sha256": EXPECTED_CORPUS_SHA256, "ordering_verified": True, "source_sha_verified": True, "dimensions_verified": True},
        "input_tensor_count": len(input_entries),
        "input_tensor_total_bytes": len(input_entries) * INPUT_BYTES,
        "raw_output_count": len(output_entries),
        "raw_output_total_bytes": len(output_entries) * OUTPUT_BYTES,
        "contract_verification": {"input_finite": "16/16", "output_finite": "16/16", "input_shape": "16/16", "output_shape": "16/16", "input_sha256": "16/16", "output_sha256": "16/16"},
        "session_contract": {"execution_mode": "ORT_SEQUENTIAL", "graph_optimization_level": "ORT_ENABLE_ALL", "intra_op_num_threads": 1, "inter_op_num_threads": 1, "providers": ["CPUExecutionProvider"], "session_count": 1},
        "preprocessing": {"new_shape": [640, 640], "auto": False, "scale_fill": False, "scaleup": True, "center": True, "stride": 32, "padding_value": 114, "interpolation": "INTER_LINEAR", "padding_rounding": ["round(dw/2 - 0.1)", "round(dw/2 + 0.1)", "round(dh/2 - 0.1)", "round(dh/2 + 0.1)"], "implementation": "tools/validation/m5_level_c_common.py::preprocess"},
    }
    write_json(output_dir / "generation_report.json", generation_report)
    provenance = {
        **common,
        "artifact_kind": "stage_k_level_b_reference_provenance",
        "source_corpus_manifest_path": SOURCE_CORPUS_LOGICAL_PATH,
        "model_path": repo_relative(MODEL_PATH),
        "model_contract_path": repo_relative(CONTRACT_PATH),
        "reference": "python_onnxruntime_explicit_cpu_raw_output",
        "preprocess_contract_identity": bundle_manifest["preprocess_contract_identity"],
        "no_contract_changes": True,
        "tensor_files": [{"image_id": entry["image_id"], "input_sha256": entry["input_tensor_sha256"], "output_sha256": next(item["output_sha256"] for item in output_entries if item["image_id"] == entry["image_id"])} for entry in input_entries],
    }
    write_json(output_dir / "provenance.json", provenance)
    commands = "\n".join([
        "./.venv/bin/python tools/validation/generate_stage_k_level_b_reference.py \\",
        "  --corpus-dir <J4.3_V2_PREPARED_CORPUS> \\",
        f"  --output-dir <{args.bundle_id}> \\",
        f"  --run-id {args.run_id}",
        "",
        "# Frozen preprocessing: m5_level_c_common.preprocess; one CPU-only ORT session; no NMS/postprocess.",
    ]) + "\n"
    write_atomic(output_dir / "commands.txt", commands.encode("utf-8"))
    write_atomic(output_dir / "sha256sums.txt", ("\n".join(sorted(tensor_sha_lines)) + "\n").encode("utf-8"))
    if args.archive_path:
        archive_path = args.archive_path.resolve()
        create_deterministic_archive(output_dir, archive_path)
        archive_provenance = {
            "schema_version": 1,
            "artifact_kind": "stage_k_level_b_reference_archive_provenance",
            "bundle_id": args.bundle_id,
            "archive_filename": archive_path.name,
            "archive_sha256": sha256_file(archive_path),
            "archive_size_bytes": archive_path.stat().st_size,
            "bundle_manifest_sha256": sha256_file(output_dir / "bundle_manifest.json"),
            "sha256sums_sha256": sha256_file(output_dir / "sha256sums.txt"),
            "source_git_commit": commit,
            "creation_timestamp": utc_now(),
            "limitations": ["canonical bundle archive only", "raw source images are excluded", "TensorRT was not executed in this round"],
        }
        archive_provenance_path = archive_path.parent / "archive_provenance.json"
        write_json(archive_provenance_path, archive_provenance)
    else:
        archive_provenance = None
        archive_provenance_path = None
    if args.tracked_metadata_dir:
        tracked = args.tracked_metadata_dir.resolve()
        tracked.mkdir(parents=True, exist_ok=False)
        for name in ("bundle_manifest.json", "input_manifest.json", "sha256sums.txt", "generation_report.json", "provenance.json", "commands.txt"):
            shutil.copyfile(output_dir / name, tracked / name)
        if archive_provenance_path is not None:
            shutil.copyfile(archive_provenance_path, tracked / "archive_provenance.json")
    return {"bundle_manifest": bundle_manifest, "generation_report": generation_report, "output_manifest": output_manifest, "archive_provenance": archive_provenance}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--bundle-id", default="stage_k_level_b_reference_v1")
    parser.add_argument("--run-id", default="stage_k_level_b_reference_v1")
    parser.add_argument("--tracked-metadata-dir", type=Path)
    parser.add_argument("--archive-path", type=Path)
    return parser.parse_args()


def main() -> int:
    try:
        result = generate(parse_args())
        print(json.dumps({"status": result["generation_report"]["status"], "entry_count": result["generation_report"]["entry_count"]}))
        return 0
    except (GenerationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"generate_stage_k_level_b_reference: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
