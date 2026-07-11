# YOLOv8n NEU-DET Baseline Training

## Purpose

The baseline establishes a reproducible PyTorch reference model for later ONNX
export, TensorRT deployment, and runtime comparisons. It does not change the
YOLOv8n architecture or introduce a new training framework.

## Dataset

- Source: NEU-DET / NEU Surface Defect Database.
- Converted dataset: `data/yolo/neu_det`.
- Dataset configuration: `data/yolo/neu_det/dataset.yaml`.
- Split: train / val / test = 70 / 20 / 10 with seed 42.
- Classes: crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches.
- Exact duplicate YOLO bounding boxes are removed during conversion and recorded
  in `conversion_manifest.json`.

Raw and converted datasets are local inputs and are not tracked by Git.

## Model

- Architecture: YOLOv8n detection model.
- Initialization: `models/pretrained/yolov8n.pt`.
- The launcher validates that the local weight file exists and sets Ultralytics
  offline mode. Missing weights cause an explicit error rather than a download.

## Environment

Create and activate the project environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
```

The validated local environment is recorded in `environment_snapshot.txt`.
Formal training must create a run-specific environment snapshot under
`experiments/training/<run_id>/`.

## Frozen Parameters

The baseline uses `configs/train/yolov8n_neudet_baseline.yaml`:

```text
model: models/pretrained/yolov8n.pt
dataset_yaml: data/yolo/neu_det/dataset.yaml
imgsz: 640
epochs: 100
batch: 16
seed: 42
amp: false
```

Batch size and device must be reviewed against the formal training GPU before
the run. Any required change must be recorded as a separate configuration and
must not silently modify the frozen baseline file.

## Preflight

Validate paths and inspect the planned command without starting training:

```bash
source .venv/bin/activate
python scripts/train_yolo.py \
  --config configs/train/yolov8n_neudet_baseline.yaml \
  --dry-run
```

## Baseline Run

Run from the repository root on the designated training machine:

```bash
source .venv/bin/activate
python scripts/train_yolo.py \
  --config configs/train/yolov8n_neudet_baseline.yaml
```

Do not run this command until the formal training environment and available GPU
memory have been confirmed.

## Outputs

Each run is written to:

```text
experiments/training/yolov8n_neudet_baseline_<timestamp>/
```

Git retains the resolved configuration, command, environment snapshot, timing,
Git commit, and metrics summary. Checkpoints, caches, plots, prediction images,
and large framework outputs remain ignored.

## Evaluation Metrics

Record real validation and test values produced by the training or evaluation
pipeline:

- Precision and recall.
- mAP50.
- mAP50-95.
- Per-class metrics.
- Training and validation losses.

This document intentionally contains no baseline result values.
