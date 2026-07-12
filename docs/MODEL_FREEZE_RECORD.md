# Model Freeze Record

## Frozen Model

- **Model Name**: `yolov8n_neudet_frozen.pt`
- **Architecture**: YOLOv8n (Ultralytics 8.4.50)
- **Task**: Object Detection (NEU-DET 6-class defect detection)

## Origin

- **Source Experiment**: `experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145/`
- **Source best.pt**: `experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145/train/weights/best.pt`
- **Frozen Model Path**: `models/pytorch/yolov8n_neudet_frozen.pt`

## Integrity

- **SHA256**: `5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7`
- Verified: source and destination SHA256 match.

## Git Context

- **Branch**: `feature/dataset-training`
- **Commit**: `2fddb7f35fd8fcf2a5066fddb2bec0df47b7133e`

## Training Configuration

```yaml
experiment_name: yolov8n_neudet_baseline_seed7
dataset_yaml: data/yolo/neu_det/dataset.yaml
model: models/pretrained/yolov8n.pt
task: detect
mode: train
imgsz: 640
epochs: 100
batch: 16
device: 0
workers: 4
patience: 30
seed: 7
deterministic: true
optimizer: auto
amp: false
mosaic: 1.0
```

## Training Command

```
yolo detect train model=models/pretrained/yolov8n.pt data=data/yolo/neu_det/dataset.yaml imgsz=640 epochs=100 batch=16 device=0 workers=4 patience=30 seed=7 deterministic=true optimizer=auto amp=False mosaic=1.0 project=experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145 name=train exist_ok=False
```

## Validation Metrics (val split)

### Overall

| Metric    | Value   |
|-----------|---------|
| mAP50     | 0.76660 |
| mAP50-95  | 0.45085 |
| Precision | 0.69223 |
| Recall    | 0.74469 |

### Per-Class

| Class          | AP50   | AP50-95 | Precision | Recall  |
|----------------|--------|---------|-----------|---------|
| crazing        | 0.4718 | 0.1827  | 0.5108    | 0.4176  |
| inclusion      | 0.8330 | 0.4655  | 0.7330    | 0.8084  |
| patches        | 0.9350 | 0.6373  | 0.7771    | 0.9221  |
| pitted_surface | 0.7916 | 0.4908  | 0.6819    | 0.7471  |
| rolled-in_scale| 0.6051 | 0.3014  | 0.5861    | 0.6210  |
| scratches      | 0.9632 | 0.6274  | 0.8646    | 0.9519  |

## Test Metrics (test split, 180 images)

Evaluated with the frozen model at `experiments/evaluation/yolov8n_neudet_frozen_test_20260712_163356/`.

### Overall

| Metric    | Value |
|-----------|-------|
| mAP50     | 0.769 |
| mAP50-95  | 0.431 |
| Precision | 0.724 |
| Recall    | 0.728 |

### Per-Class

| Class          | AP50   | AP50-95 | Precision | Recall  |
|----------------|--------|---------|-----------|---------|
| crazing        | 0.405  | 0.168   | 0.460     | 0.311   |
| inclusion      | 0.742  | 0.396   | 0.676     | 0.673   |
| patches        | 0.921  | 0.568   | 0.799     | 0.912   |
| pitted_surface | 0.857  | 0.541   | 0.831     | 0.848   |
| rolled-in_scale| 0.729  | 0.324   | 0.677     | 0.699   |
| scratches      | 0.963  | 0.590   | 0.900     | 0.925   |

**Note**: test split 结果仅用于最终报告，不用于模型选择或训练调参。

## Selection Rationale

1. **mAP50-95 (Priority 1)**: 0.45085 — 在三个 deterministic baseline 运行中名义最高。与 seed=42 deterministic 的差距（0.001）远小于三次种子实验观察到的波动范围（σ≈0.006），两者属于同一性能水平。
2. **Recall (Priority 2)**: 0.74469 — 高于 seed=42 deterministic（0.73257），满足性能相当模型优先选择较高 Recall 的工程规则。
3. **Deterministic**: Training used `deterministic=true`, ensuring full reproducibility.
4. **Within baseline range**: All metrics fall within the 3-seed deterministic baseline fluctuation range.
5. **Complete records**: Training completed all 100 epochs with full training logs, results.csv, and best.pt.

## Known Weaknesses

- **crazing**: val AP50-95 = 0.1827, test AP50-95 = 0.168（所有实验中均最弱的类别）。检测困难可能与弥散纹理、边界模糊、类内差异大及与 scratches/patches 的类间相似性有关。
- **rolled-in_scale**: val AP50-95 = 0.3014, test AP50-95 = 0.324（第二弱类别）。
- These are consistent with all baseline runs and reflect inherent difficulty of these defect types rather than model-specific deficiencies.

## Intended Use

This frozen model is the canonical training output and will be used for:
1. **ONNX export** — for deployment optimization
2. **TensorRT conversion** — for NVIDIA Jetson inference
3. **Edge deployment** — final integration on target hardware

The model must NOT be retrained, fine-tuned, or modified. All future work builds on this frozen artifact.
