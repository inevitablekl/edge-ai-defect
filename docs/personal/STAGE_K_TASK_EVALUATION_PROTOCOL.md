# Stage K Task-Level Evaluation Protocol v1

Status: `FROZEN_FOR_PREPARATION_ONLY`

This protocol freezes the dataset, split, preprocessing, postprocessing, and
engine identities for the later full test-split comparison. It does not run
inference and does not alter the Stage K official plan, K5 gate, comparator,
Engine, ONNX model, ModelContract, or production runtime.

## Dataset

| Field | Frozen value |
|---|---|
| Source | `data/raw/NEU-DET` |
| Images | 1800 |
| Annotation format | Pascal VOC XML |
| Raw objects | 4189 |
| Duplicate bbox policy | Remove 3 exact duplicate bbox rows during provenance-preserving conversion |
| Objects after deduplication | 4186 |
| Classes | `crazing`, `inclusion`, `patches`, `pitted_surface`, `rolled-in_scale`, `scratches` |

The raw dataset is read-only input. No XML or image is repaired, deleted, or
rewritten by the task split generator.

## Split

| Split | Count |
|---|---:|
| Train | 1260 |
| Val | 360 |
| Test | 180 |

```text
ratio: 0.70 / 0.20 / 0.10
random seed: 42
ordering: sorted annotation paths, then random.Random(42).shuffle
```

The evaluation target is the `test` split only. The split generator records
image and annotation SHA256 values and uses the same deduplication and split
semantics as `scripts/convert_neudet_to_yolo.py`.

## Evaluation engines

Only these two frozen local engines are in scope:

| Role | Engine | SHA256 | Manifest |
|---|---|---|---|
| Reference | TensorRT strict FP32 noTF32 | `aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f` | `results/build/tensorrt/strict_fp32_notf32_investigation_v1/manifest.json` |
| Candidate | TensorRT FP16 | `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` | `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json` |

Both engines use the frozen ONNX source
`models/onnx/yolov8n_neudet_frozen.onnx`, SHA256
`c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`, with
static batch 1 and input shape `1x3x640x640`.

## Preprocessing

The same preprocessing must be used for both engines:

```text
input image: BGR
resize: aspect-preserving LetterBox to 640x640
interpolation: INTER_LINEAR
padding value: 114
color/layout: BGR -> RGB, HWC -> NCHW
tensor dtype: FP32
normalization: pixel / 255.0
```

## Postprocessing

The same YOLOv8 postprocessing must be used for both engines:

```text
confidence threshold: 0.25
IoU threshold: 0.45
max_nms: 30000
max_det: 300
max_wh: 7680.0
agnostic: false
multi_label: false
```

The existing backend-neutral postprocessing and comparator contracts remain
unchanged.

## Accuracy evaluation

The later run must use the same ordered `test_manifest.json` for both engines
and the same evaluator:

```text
evaluator: tools/validation/task_level_dataset_metrics.py
ground truth: Pascal VOC annotations selected by the frozen split manifest
metrics: Precision, Recall, mAP50, mAP50-95
matching: deterministic class-aware one-to-one IoU matching
```

The split manifest is an identity/control list; its `class_list` and
`bbox_count` fields are not a replacement for bbox coordinates. Before the
formal run, evaluator-compatible ground truth must be derived from the XML
files using the established provenance-preserving conversion and duplicate-bbox
policy. No labels may be inferred from filenames or from class counts.

The run must save FP32 and FP16 predictions and metrics under the task-level
evidence directory. Raw prediction dumps and large generated files remain
local-only unless separately approved.

## Performance scope

This protocol freezes the accuracy test corpus. It does not authorize or
execute the performance campaign. Any later performance measurement must state
its warmup, measured-frame count, Jetson power mode, environment, and timing
definition separately.

## Reproducibility and acceptance

The split generator must produce byte-identical manifests for repeated runs
with the same input tree, seed, class order, and deduplication policy. The
manifest SHA256 values and source-tree SHA256 are recorded in
`results/validation/stage_k_task_eval_v2/split/split_metadata.json`.

No FP32/FP16 accuracy conclusion is made by this preparation task. The later
task-level result must report both backend metrics, FP16-minus-FP32 deltas, and
the decision classification only from real measured data.
