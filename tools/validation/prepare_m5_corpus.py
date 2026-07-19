#!/usr/bin/env python3
"""Validate and prepare the frozen M5 corpus without importing image assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import cv2


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_ROOT = REPO_ROOT / "tests" / "data" / "m5" / "manifests"
ORIGINAL_MANIFEST = MANIFEST_ROOT / "level_c_original_corpus.json"
DERIVED_MANIFEST = MANIFEST_ROOT / "level_c_derived_corpus.json"
BENCHMARK_MANIFEST = MANIFEST_ROOT / "benchmark_corpus.json"
CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
CLASS_IDS = {name: index for index, name in enumerate(CLASSES)}

ORIGINAL_TOP = ["schema_version", "corpus_id", "dataset", "split", "image_root_semantics", "entries", "coverage"]
ORIGINAL_ENTRY = ["sequence_index", "source_filename", "prepared_filename", "expected_sha256", "expected_width", "expected_height", "gt_classes", "roles"]
DERIVED_TOP = ["schema_version", "corpus_id", "encoding", "generation", "entries"]
DERIVED_GEN = ["interpolation", "border_type", "border_bgr"]
DERIVED_ENTRY = ["sequence_index", "source_filename", "source_expected_sha256", "prepared_filename", "target_width", "target_height", "resized_width", "resized_height", "top", "bottom", "left", "right", "expected_output_sha256"]
BENCHMARK_TOP = ["schema_version", "corpus_id", "dataset", "split", "image_root_semantics", "entries", "coverage"]
BENCHMARK_ENTRY = ["sequence_index", "source_filename", "prepared_filename", "expected_sha256", "expected_width", "expected_height", "gt_classes"]


class ManifestError(ValueError):
    pass


class PreparationError(RuntimeError):
    pass


def _duplicate_key(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            raw = handle.read()
        if not raw.endswith("\n") or raw.endswith("\n\n"):
            raise ManifestError("manifest must end with exactly one LF")
        return json.loads(raw, object_pairs_hook=_duplicate_key)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest {path}: {exc}") from exc


def _keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict):
        raise ManifestError(f"{where} must be an object")
    actual = list(value)
    if actual != expected:
        missing = [key for key in expected if key not in value]
        unknown = [key for key in actual if key not in expected]
        raise ManifestError(f"{where} fields/order invalid; missing={missing}, unknown={unknown}")


def _string(value: Any, where: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise ManifestError(f"{where} must be a non-empty string")
    return value


def _integer(value: Any, where: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise ManifestError(f"{where} must be >= {minimum}")
    return value


def _sha(value: Any, where: str) -> str:
    value = _string(value, where)
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ManifestError(f"{where} must be lowercase SHA256")
    return value


def _safe_relpath(value: Any, where: str) -> str:
    value = _string(value, where)
    if "\\" in value or value.startswith("/"):
        raise ManifestError(f"{where} must be a relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ManifestError(f"{where} is not lexically safe")
    return value


def _string_list(value: Any, where: str, *, allowed: set[str] | None = None) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ManifestError(f"{where} must be a string list")
    if allowed is not None and any(item not in allowed for item in value):
        raise ManifestError(f"{where} contains an unknown value")
    return value


def _coverage(entries: list[dict[str, Any]], *, benchmark: bool = False) -> None:
    classes: set[int] = set()
    counts = {name: 0 for name in CLASSES}
    for entry in entries:
        for class_id in entry["gt_classes"]:
            classes.add(class_id)
            counts[CLASSES[class_id]] += 1
    if classes != set(range(len(CLASSES))):
        raise ManifestError("all six classes must be covered")
    minimum = 3 if benchmark else 2
    if any(count < minimum for count in counts.values()):
        raise ManifestError(f"each class must occur at least {minimum} times")


def validate_original(data: Any) -> dict[str, Any]:
    _keys(data, ORIGINAL_TOP, "original manifest")
    if data["schema_version"] != 1 or isinstance(data["schema_version"], bool):
        raise ManifestError("schema_version must be 1")
    if data["corpus_id"] != "m5_level_c_original_v1" or data["dataset"] != "NEU-DET":
        raise ManifestError("invalid original corpus identity")
    if data["split"] != "validation" or data["image_root_semantics"] != "user_supplied_validation_image_root":
        raise ManifestError("invalid original split/root semantics")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 12:
        raise ManifestError("original manifest must contain exactly 12 entries")
    expected_indexes = list(range(12))
    indexes: list[int] = []
    source_names: set[str] = set()
    prepared_names: set[str] = set()
    hashes: set[str] = set()
    for position, entry in enumerate(entries):
        _keys(entry, ORIGINAL_ENTRY, f"original entry {position}")
        index = _integer(entry["sequence_index"], f"original entry {position}.sequence_index", minimum=0)
        indexes.append(index)
        if index != position:
            raise ManifestError("original sequence_index must be contiguous 0..11")
        source = _safe_relpath(entry["source_filename"], f"original entry {position}.source_filename")
        prepared = _safe_relpath(entry["prepared_filename"], f"original entry {position}.prepared_filename")
        if source in source_names or prepared in prepared_names:
            raise ManifestError("duplicate original source/prepared filename")
        source_names.add(source)
        prepared_names.add(prepared)
        if not prepared.startswith(f"{index:04d}_"):
            raise ManifestError("prepared filename prefix does not match sequence index")
        digest = _sha(entry["expected_sha256"], f"original entry {position}.expected_sha256")
        if digest in hashes:
            raise ManifestError("duplicate original SHA256")
        hashes.add(digest)
        if _integer(entry["expected_width"], "expected_width", minimum=1) != 200 or _integer(entry["expected_height"], "expected_height", minimum=1) != 200:
            raise ManifestError("original images must be 200x200")
        classes = _integer_list(entry["gt_classes"], f"original entry {position}.gt_classes", maximum=len(CLASSES) - 1)
        if not classes:
            raise ManifestError("gt_classes must not be empty")
        roles = _string_list(entry["roles"], f"original entry {position}.roles")
        if len(set(roles)) != len(roles):
            raise ManifestError("roles must be unique")
    if indexes != expected_indexes:
        raise ManifestError("original indexes are not contiguous")
    coverage = data["coverage"]
    _keys(coverage, ["class_names", "class_counts", "required_roles"], "original coverage")
    if coverage["class_names"] != CLASSES:
        raise ManifestError("coverage class_names mismatch")
    _coverage(entries)
    actual_counts = {name: 0 for name in CLASSES}
    for entry in entries:
        for class_id in entry["gt_classes"]:
            actual_counts[CLASSES[class_id]] += 1
    if coverage["class_counts"] != actual_counts:
        raise ManifestError("coverage class_counts mismatch")
    role_values = {role for entry in entries for role in entry["roles"]}
    if "zero_detection" not in role_values or sum("multi_detection" in e["roles"] for e in entries) < 3 or sum("near_threshold" in e["roles"] for e in entries) < 2:
        raise ManifestError("original role coverage is insufficient")
    return data


def _integer_list(value: Any, where: str, *, maximum: int) -> list[int]:
    if not isinstance(value, list) or any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise ManifestError(f"{where} must be an integer list")
    if any(item < 0 or item > maximum for item in value) or len(set(value)) != len(value):
        raise ManifestError(f"{where} contains invalid or duplicate class ids")
    return value


def validate_derived(data: Any, original: dict[str, Any]) -> dict[str, Any]:
    _keys(data, DERIVED_TOP, "derived manifest")
    if data["schema_version"] != 1 or data["corpus_id"] != "m5_level_c_derived_v1" or data["encoding"] != "bmp_24bit":
        raise ManifestError("invalid derived identity")
    _keys(data["generation"], DERIVED_GEN, "derived generation")
    if data["generation"]["interpolation"] != "cv2.INTER_LINEAR" or data["generation"]["border_type"] != "cv2.BORDER_CONSTANT" or data["generation"]["border_bgr"] != [114, 114, 114]:
        raise ManifestError("invalid derived generation rules")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 4:
        raise ManifestError("derived manifest must contain exactly 4 entries")
    original_by_name = {entry["source_filename"]: entry for entry in original["entries"]}
    hashes: set[str] = set()
    prepared: set[str] = set()
    for position, entry in enumerate(entries):
        _keys(entry, DERIVED_ENTRY, f"derived entry {position}")
        if _integer(entry["sequence_index"], "derived sequence_index") != position + 12:
            raise ManifestError("derived sequence_index must be 12..15")
        source = _safe_relpath(entry["source_filename"], "derived source_filename")
        if source not in original_by_name:
            raise ManifestError("derived source is not in original manifest")
        if entry["source_expected_sha256"] != original_by_name[source]["expected_sha256"]:
            raise ManifestError("derived source SHA mismatch")
        output = _safe_relpath(entry["prepared_filename"], "derived prepared_filename")
        if output in prepared or not output.startswith(f"{position + 12:04d}_") or not output.endswith(".bmp"):
            raise ManifestError("invalid or duplicate derived prepared filename")
        prepared.add(output)
        target_w = _integer(entry["target_width"], "target_width", minimum=1)
        target_h = _integer(entry["target_height"], "target_height", minimum=1)
        resized_w = _integer(entry["resized_width"], "resized_width", minimum=1)
        resized_h = _integer(entry["resized_height"], "resized_height", minimum=1)
        top = _integer(entry["top"], "top", minimum=0)
        bottom = _integer(entry["bottom"], "bottom", minimum=0)
        left = _integer(entry["left"], "left", minimum=0)
        right = _integer(entry["right"], "right", minimum=0)
        if resized_w + left + right != target_w or resized_h + top + bottom != target_h:
            raise ManifestError("derived padding arithmetic mismatch")
        if f"derived_{target_w}x{target_h}_" not in output:
            raise ManifestError("derived target dimensions do not match output filename")
        digest = _sha(entry["expected_output_sha256"], "derived expected_output_sha256")
        if digest in hashes:
            raise ManifestError("duplicate derived output SHA256")
        hashes.add(digest)
    return data


def validate_benchmark(data: Any) -> dict[str, Any]:
    _keys(data, BENCHMARK_TOP, "benchmark manifest")
    if data["schema_version"] != 1 or data["corpus_id"] != "m5_ort_cpu_benchmark_original_v1" or data["dataset"] != "NEU-DET":
        raise ManifestError("invalid benchmark identity")
    if data["split"] != "validation" or data["image_root_semantics"] != "user_supplied_validation_image_root":
        raise ManifestError("invalid benchmark split/root semantics")
    entries = data["entries"]
    if not isinstance(entries, list) or len(entries) != 20:
        raise ManifestError("benchmark manifest must contain exactly 20 entries")
    seen: set[str] = set()
    prepared_names: set[str] = set()
    hashes: set[str] = set()
    for position, entry in enumerate(entries):
        _keys(entry, BENCHMARK_ENTRY, f"benchmark entry {position}")
        if _integer(entry["sequence_index"], "benchmark sequence_index") != position:
            raise ManifestError("benchmark sequence_index must be contiguous 0..19")
        source = _safe_relpath(entry["source_filename"], "benchmark source_filename")
        prepared = _safe_relpath(entry["prepared_filename"], "benchmark prepared_filename")
        if source in seen or prepared in prepared_names or not prepared.startswith(f"{position:04d}_"):
            raise ManifestError("duplicate or invalid benchmark filename")
        seen.add(source)
        prepared_names.add(prepared)
        digest = _sha(entry["expected_sha256"], "benchmark expected_sha256")
        if digest in hashes:
            raise ManifestError("duplicate benchmark SHA256")
        hashes.add(digest)
        if _integer(entry["expected_width"], "benchmark expected_width", minimum=1) != 200 or _integer(entry["expected_height"], "benchmark expected_height", minimum=1) != 200:
            raise ManifestError("benchmark images must be 200x200")
        _integer_list(entry["gt_classes"], "benchmark gt_classes", maximum=len(CLASSES) - 1)
    _coverage(entries, benchmark=True)
    actual_counts = {name: 0 for name in CLASSES}
    for entry in entries:
        for class_id in entry["gt_classes"]:
            actual_counts[CLASSES[class_id]] += 1
    if data["coverage"]["class_counts"] != actual_counts:
        raise ManifestError("coverage class_counts mismatch")
    return data


def load_manifests() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    original = validate_original(_read_json(ORIGINAL_MANIFEST))
    derived = validate_derived(_read_json(DERIVED_MANIFEST), original)
    benchmark = validate_benchmark(_read_json(BENCHMARK_MANIFEST))
    if [e["source_filename"] for e in benchmark["entries"][:12]] != [e["source_filename"] for e in original["entries"]]:
        raise ManifestError("benchmark first 12 entries must equal original corpus")
    return original, derived, benchmark


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_file(root: Path, filename: str) -> Path:
    path = root / filename
    if not path.exists():
        raise PreparationError(f"source file missing: {filename}")
    if path.is_symlink() or not path.is_file():
        raise PreparationError(f"source is not a regular file: {filename}")
    return path


def _copy_entry(root: Path, destination: Path, entry: dict[str, Any]) -> dict[str, Any]:
    source = _source_file(root, entry["source_filename"])
    if _sha256(source) != entry["expected_sha256"]:
        raise PreparationError(f"source SHA mismatch: {entry['source_filename']}")
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None or image.shape[:2] != (entry["expected_height"], entry["expected_width"]):
        raise PreparationError(f"source image decode/size mismatch: {entry['source_filename']}")
    output = destination / entry["prepared_filename"]
    shutil.copyfile(source, output)
    return {"source_filename": entry["source_filename"], "prepared_filename": entry["prepared_filename"], "source_sha256": entry["expected_sha256"], "prepared_sha256": _sha256(output), "width": int(image.shape[1]), "height": int(image.shape[0]), "derived": False}


def _derived_entry(root: Path, destination: Path, entry: dict[str, Any]) -> dict[str, Any]:
    source = _source_file(root, entry["source_filename"])
    if _sha256(source) != entry["source_expected_sha256"]:
        raise PreparationError(f"source SHA mismatch: {entry['source_filename']}")
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None or image.shape[:2] != (200, 200):
        raise PreparationError(f"source image decode/size mismatch: {entry['source_filename']}")
    resized = cv2.resize(image, (entry["resized_width"], entry["resized_height"]), interpolation=cv2.INTER_LINEAR)
    output_image = cv2.copyMakeBorder(resized, entry["top"], entry["bottom"], entry["left"], entry["right"], cv2.BORDER_CONSTANT, value=(114, 114, 114))
    if output_image.shape[:2] != (entry["target_height"], entry["target_width"]) or output_image.dtype.name != "uint8" or output_image.ndim != 3 or output_image.shape[2] != 3:
        raise PreparationError(f"derived image geometry/type mismatch: {entry['source_filename']}")
    output = destination / entry["prepared_filename"]
    if not cv2.imwrite(str(output), output_image):
        raise PreparationError(f"failed to write derived BMP: {entry['prepared_filename']}")
    if _sha256(output) != entry["expected_output_sha256"]:
        raise PreparationError(f"derived output SHA mismatch: {entry['prepared_filename']}")
    decoded = cv2.imread(str(output), cv2.IMREAD_COLOR)
    if decoded is None or decoded.shape[:2] != (entry["target_height"], entry["target_width"]):
        raise PreparationError(f"derived output cannot be decoded: {entry['prepared_filename']}")
    return {"source_filename": entry["source_filename"], "prepared_filename": entry["prepared_filename"], "source_sha256": entry["source_expected_sha256"], "prepared_sha256": entry["expected_output_sha256"], "width": entry["target_width"], "height": entry["target_height"], "derived": True}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def prepare(mode: str, dataset_root: Path, output_dir: Path) -> dict[str, Any]:
    if not dataset_root.exists() or not dataset_root.is_dir() or dataset_root.is_symlink():
        raise PreparationError("dataset-root must be an existing real directory")
    if output_dir.exists():
        if not output_dir.is_dir() or any(output_dir.iterdir()):
            raise PreparationError("output-dir must not exist or must be empty")
        raise PreparationError("output-dir already exists")
    original, derived, benchmark = load_manifests()
    entries: list[dict[str, Any]] = []
    if mode == "level-c":
        selected: Iterable[dict[str, Any]] = original["entries"]
        derived_entries = derived["entries"]
    else:
        selected = benchmark["entries"]
        derived_entries = []
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=str(output_dir.parent)))
    try:
        for entry in selected:
            entries.append(_copy_entry(dataset_root, temp_dir, entry))
        for entry in derived_entries:
            entries.append(_derived_entry(dataset_root, temp_dir, entry))
        expected_count = 16 if mode == "level-c" else 20
        image_files = [path for path in temp_dir.iterdir() if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]
        if len(image_files) != expected_count or any(path.is_symlink() for path in image_files):
            raise PreparationError("prepared image count or file type mismatch")
        manifest_path = "tests/data/m5/manifests/level_c_original_corpus.json" if mode == "level-c" else "tests/data/m5/manifests/benchmark_corpus.json"
        prepared = {"schema_version": 1, "corpus_mode": mode, "manifest_path": manifest_path, "manifest_sha256": _sha256(ORIGINAL_MANIFEST if mode == "level-c" else BENCHMARK_MANIFEST), "entries": entries}
        _write_json(temp_dir / "prepared_corpus_manifest.json", prepared)
        temp_dir.rename(output_dir)
        return prepared
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare the frozen M5 corpus from a local validation image root.")
    parser.add_argument("--mode", choices=("level-c", "benchmark"), required=True)
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        prepared = prepare(args.mode, Path(args.dataset_root), Path(args.output_dir))
        print(f"prepared {len(prepared['entries'])} images for {args.mode}")
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except (ManifestError, PreparationError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2 if isinstance(exc, ManifestError) else 3
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
