#!/usr/bin/env python3
"""Build an auditable evidence archive from existing training artifacts.

This archive utility never trains or validates a model. Metrics must already
exist as machine-readable JSON/CSV inputs declared by the experiment manifest.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import shutil
import tarfile
from pathlib import Path
from typing import Any


SUMMARY_ARG_KEYS = (
    "model",
    "data",
    "epochs",
    "imgsz",
    "batch",
    "optimizer",
    "lr0",
    "seed",
    "deterministic",
    "mosaic",
    "close_mosaic",
    "cos_lr",
    "warmup_epochs",
    "patience",
    "amp",
    "device",
)
CHECKPOINT_SUFFIXES = {".pt", ".pth", ".onnx", ".engine", ".plan", ".trt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive existing training evidence without running training or validation."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--experiment-manifest", type=Path, required=True)
    parser.add_argument("--frozen-model", type=Path, required=True)
    parser.add_argument("--test-evaluation-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true", help="Replace only the requested output paths.")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required structured file not found: {path}")
    if path.suffix.lower() == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
    else:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for YAML evidence manifests.") from exc
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return loaded


def resolve_path(project_root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (project_root / path).resolve()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required {label} not found: {path}")
    return path


def require_directory(path: Path, label: str) -> Path:
    if not path.is_dir():
        raise FileNotFoundError(f"Required {label} directory not found: {path}")
    return path


def parse_results(results_path: Path) -> tuple[int, int | None]:
    with results_path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError(f"Training results are empty: {results_path}")
    completed_epochs = int(float(rows[-1]["epoch"]))
    metric_key = next(
        (key for key in rows[0] if key.strip() == "metrics/mAP50-95(B)"),
        None,
    )
    if metric_key is None:
        return completed_epochs, None
    best_row = max(rows, key=lambda row: float(row[metric_key]))
    return completed_epochs, int(float(best_row["epoch"]))


def load_effective_args(path: Path) -> dict[str, Any]:
    loaded = load_mapping(path)
    return {key: value for key, value in loaded.items() if not isinstance(value, (dict, list))}


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    experiments = manifest.get("experiments")
    if not isinstance(experiments, list) or not experiments:
        raise ValueError("Experiment manifest must contain a non-empty 'experiments' list.")
    required = {"experiment_name", "slug", "directory", "config_path"}
    for index, experiment in enumerate(experiments):
        if not isinstance(experiment, dict):
            raise ValueError(f"Experiment entry {index} must be a mapping.")
        missing = sorted(required - experiment.keys())
        if missing:
            raise ValueError(f"Experiment entry {index} is missing fields: {missing}")
    return experiments


def collect_inputs(
    project_root: Path,
    manifest: dict[str, Any],
    frozen_model: Path,
    test_evaluation_dir: Path,
) -> dict[str, Any]:
    experiments = validate_manifest(manifest)
    records = []
    for experiment in experiments:
        experiment_dir = require_directory(
            resolve_path(project_root, experiment["directory"]),
            f"experiment '{experiment['experiment_name']}'",
        )
        train_dir = experiment_dir / "train"
        records.append(
            {
                **experiment,
                "experiment_dir": experiment_dir,
                "config": require_file(
                    resolve_path(project_root, experiment["config_path"]), "training config"
                ),
                "args": require_file(train_dir / "args.yaml", "Ultralytics args.yaml"),
                "results": require_file(train_dir / "results.csv", "Ultralytics results.csv"),
                "checkpoint": require_file(train_dir / "weights" / "best.pt", "best checkpoint"),
                "git_commit": require_file(experiment_dir / "git_commit.txt", "experiment Git record"),
            }
        )

    evidence_keys = (
        "validation_metrics_json",
        "validation_metrics_csv",
        "validation_command",
        "test_metrics_json",
        "test_metrics_csv",
        "test_command",
        "test_environment",
    )
    evidence = {}
    for key in evidence_keys:
        if key not in manifest:
            raise ValueError(f"Experiment manifest is missing '{key}'.")
        evidence[key] = require_file(resolve_path(project_root, manifest[key]), key)

    return {
        "experiments": records,
        "evidence": evidence,
        "frozen_model": require_file(frozen_model, "frozen model"),
        "test_evaluation_dir": require_directory(test_evaluation_dir, "test evaluation"),
        "frozen_source_experiment": manifest.get("frozen_source_experiment"),
    }


def ensure_output_available(output_dir: Path, overwrite: bool) -> tuple[Path, Path]:
    archive_path = Path(str(output_dir) + ".tar.gz")
    checksum_path = Path(str(archive_path) + ".sha256")
    existing = [path for path in (output_dir, archive_path, checksum_path) if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(f"Output already exists; use --overwrite to replace it: {existing}")
    return archive_path, checksum_path


def clear_requested_outputs(output_dir: Path, archive_path: Path, checksum_path: Path) -> None:
    if output_dir.is_dir():
        shutil.rmtree(output_dir)
    elif output_dir.exists():
        output_dir.unlink()
    for path in (archive_path, checksum_path):
        if path.exists():
            path.unlink()


def validate_output_location(
    project_root: Path,
    output_dir: Path,
    inputs: dict[str, Any],
) -> None:
    if output_dir == project_root or output_dir in project_root.parents:
        raise ValueError(f"Output directory must not contain or replace project root: {project_root}")
    protected = [
        inputs["frozen_model"],
        inputs["test_evaluation_dir"],
        *[record["experiment_dir"] for record in inputs["experiments"]],
    ]
    for source in protected:
        source = source.resolve()
        if output_dir == source or output_dir in source.parents or source in output_dir.parents:
            raise ValueError(f"Output directory must not contain or replace an input path: {source}")


def project_display_path(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_test_artifacts(source_dir: Path, destination_dir: Path) -> None:
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if source.suffix.lower() in CHECKPOINT_SUFFIXES:
            continue
        copy_file(source, destination_dir / source.relative_to(source_dir))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_evidence_tree(
    project_root: Path,
    output_dir: Path,
    inputs: dict[str, Any],
) -> None:
    args_summary = []
    provenance = []
    frozen_hash = sha256_file(inputs["frozen_model"])
    source_checkpoint_hash = None

    copy_file(
        inputs["experiment_manifest"],
        output_dir / f"experiment_manifest{inputs['experiment_manifest'].suffix.lower()}",
    )

    for record in inputs["experiments"]:
        slug = record["slug"]
        args_destination = output_dir / "experiment_args" / f"{slug}_args.yaml"
        results_destination = output_dir / "experiment_results" / f"{slug}_results.csv"
        config_destination = output_dir / "configs" / record["config"].name
        copy_file(record["args"], args_destination)
        copy_file(record["results"], results_destination)
        copy_file(record["config"], config_destination)

        effective_args = load_effective_args(record["args"])
        completed_epochs, best_epoch = parse_results(record["results"])
        checkpoint_hash = sha256_file(record["checkpoint"])
        git_commit = record["git_commit"].read_text(encoding="utf-8").strip()
        if record["experiment_name"] == inputs["frozen_source_experiment"]:
            source_checkpoint_hash = checkpoint_hash

        args_summary.append(
            {
                "experiment_name": record["experiment_name"],
                "effective_args_path": str(args_destination.relative_to(output_dir)),
                "configured_epochs": effective_args.get("epochs"),
                "completed_epochs": completed_epochs,
                "best_epoch_by_map50_95": best_epoch,
                **{key: effective_args.get(key) for key in SUMMARY_ARG_KEYS},
                "all_effective_args": effective_args,
            }
        )
        provenance.append(
            {
                "experiment_name": record["experiment_name"],
                "config_path": str(config_destination.relative_to(output_dir)),
                "effective_args_path": str(args_destination.relative_to(output_dir)),
                "results_csv_path": str(results_destination.relative_to(output_dir)),
                "historical_experiment_path": str(record["experiment_dir"]),
                "checkpoint_historical_path": str(record["checkpoint"]),
                "checkpoint_sha256": checkpoint_hash,
                "validation_metrics_path": "validation_metrics_by_experiment.json",
                "git_commit": git_commit,
                "evidence_status": "checkpoint_hashed_on_source_host",
            }
        )

    if not inputs["frozen_source_experiment"]:
        raise ValueError("Manifest must declare 'frozen_source_experiment'.")
    if source_checkpoint_hash is None:
        raise ValueError("Frozen source experiment does not match an experiment entry.")
    if source_checkpoint_hash != frozen_hash:
        raise ValueError("Frozen model SHA256 does not match its declared source checkpoint.")

    for key, source in inputs["evidence"].items():
        destination_name = {
            "validation_metrics_json": "validation_metrics_by_experiment.json",
            "validation_metrics_csv": "validation_metrics_by_experiment.csv",
            "validation_command": "validation_command.txt",
            "test_metrics_json": "frozen_test_metrics.json",
            "test_metrics_csv": "frozen_test_metrics.csv",
            "test_command": "frozen_test_command.txt",
            "test_environment": "frozen_test_environment.txt",
        }[key]
        copy_file(source, output_dir / destination_name)

    copy_test_artifacts(inputs["test_evaluation_dir"], output_dir / "frozen_test_artifacts")
    write_json(output_dir / "experiment_effective_args_summary.json", args_summary)
    write_json(
        output_dir / "EXPERIMENT_PROVENANCE.json",
        {
            "training_experiments": provenance,
            "frozen_model": {
                "source_experiment": inputs["frozen_source_experiment"],
                "source_checkpoint_sha256": source_checkpoint_hash,
                "frozen_model_project_path": project_display_path(project_root, inputs["frozen_model"]),
                "frozen_model_sha256": frozen_hash,
                "hashes_match": True,
                "test_metrics_path": "frozen_test_metrics.json",
                "test_command_path": "frozen_test_command.txt",
            },
        },
    )
    (output_dir / "README.txt").write_text(
        "Training evidence archive\n"
        "=========================\n\n"
        "Generated from existing machine-readable training and evaluation artifacts.\n"
        "No training or validation is executed by this utility. Checkpoints are hashed\n"
        "for provenance but are not copied into the evidence package.\n",
        encoding="utf-8",
    )


def write_manifest(output_dir: Path) -> Path:
    manifest_path = output_dir / "MANIFEST.txt"
    rows = []
    for path in sorted(item for item in output_dir.rglob("*") if item.is_file()):
        if path == manifest_path:
            continue
        rows.append(
            f"{sha256_file(path)}  {path.stat().st_size}  ./{path.relative_to(output_dir)}"
        )
    manifest_path.write_text(
        "Training Evidence Manifest\n"
        "Format: SHA256  SIZE  PATH\n"
        "---\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


def write_deterministic_archive(output_dir: Path, archive_path: Path) -> None:
    with archive_path.open("wb") as raw_output:
        with gzip.GzipFile(fileobj=raw_output, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in sorted([output_dir, *output_dir.rglob("*")]):
                    arcname = Path(output_dir.name) / path.relative_to(output_dir)
                    info = archive.gettarinfo(str(path), arcname=str(arcname))
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    if path.is_file():
                        with path.open("rb") as source:
                            archive.addfile(info, source)
                    else:
                        archive.addfile(info)


def generate_evidence_package(
    project_root: Path,
    output_dir: Path,
    experiment_manifest: Path,
    frozen_model: Path,
    test_evaluation_dir: Path,
    overwrite: bool = False,
) -> tuple[Path, Path]:
    project_root = project_root.resolve()
    output_dir = output_dir.resolve()
    manifest_path = resolve_path(project_root, experiment_manifest)
    frozen_model = resolve_path(project_root, frozen_model)
    test_evaluation_dir = resolve_path(project_root, test_evaluation_dir)
    manifest = load_mapping(manifest_path)
    inputs = collect_inputs(project_root, manifest, frozen_model, test_evaluation_dir)
    inputs["experiment_manifest"] = manifest_path
    validate_output_location(project_root, output_dir, inputs)
    archive_path, checksum_path = ensure_output_available(output_dir, overwrite)
    if overwrite:
        clear_requested_outputs(output_dir, archive_path, checksum_path)

    output_dir.mkdir(parents=True, exist_ok=False)
    build_evidence_tree(project_root, output_dir, inputs)
    write_manifest(output_dir)
    write_deterministic_archive(output_dir, archive_path)
    checksum_path.write_text(
        f"{sha256_file(archive_path)}  {archive_path.name}\n",
        encoding="utf-8",
    )
    return archive_path, checksum_path


def main() -> int:
    args = parse_args()
    try:
        archive_path, checksum_path = generate_evidence_package(
            project_root=args.project_root,
            output_dir=args.output_dir,
            experiment_manifest=args.experiment_manifest,
            frozen_model=args.frozen_model,
            test_evaluation_dir=args.test_evaluation_dir,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Evidence archive: {archive_path}")
    print(f"SHA256 record: {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
