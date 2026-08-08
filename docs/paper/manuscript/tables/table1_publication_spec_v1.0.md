# Table 1 Publication Specification v1.0

## 1. Publication identity

- Table: T1
- Title: `表1　平台、模型、数据集和统一运行协议`
- Structure: two columns, `项目 | 配置`
- Scientific content authority:
  `docs/paper/manuscript/sections/04_experiment.md`
- Final DOCX assembly: VSCODE_CODEX / BUILD_PIPELINE_READY
- Three-line-table rendering: VALIDATED_BY_ISOLATED_T1_T2_ARTIFACT
- Manual visual inspection: DEFERRED_TO_PHASE_4_9

## 2. Frozen table source

| 项目 | 配置 |
|---|---|
| 边缘平台 | NVIDIA Jetson Orin Nano Super |
| L4T | R36.5 |
| CUDA | 12.6.11，runtime 12.6.68 |
| TensorRT | 10.3.0.30 |
| OpenCV | 4.5.4 |
| 检测模型 | YOLOv8n |
| 推理对象 | 冻结 TensorRT INT8 混合精度 Engine |
| 输入尺寸 | 640×640 |
| Batch size | 1 |
| 数据集 | NEU-DET，去重后的 split-v2 |
| 测试集 | 固定 180 幅图像 |
| 正式比较路径 | V0、V2R、V3R |
| 单次预热 | 60 帧 |
| 单次测量 | 1080 帧，即 180 幅图像完整回放 6 个周期 |
| 独立运行次数 | 每种路径 5 次，共 15 个独立进程 |
| 内部诊断计时 | 关闭 |
| Profiling | 关闭 |

## 3. Three-line-table construction

- Place the title above the table using the journal template's table-caption
  style.
- Use exactly three horizontal rules: one at the table top, one below the
  header row, and one at the table bottom. Do not use vertical rules or body
  row gridlines.
- Keep the first column compact and left aligned. Left align the configuration
  column so long protocol descriptions remain readable.
- Use the journal template's final typeface, size, line spacing, and rule
  weights; do not invent them before the official attachment settings are
  confirmed.
- Keep the table on one page if the final template permits. If wrapping is
  needed, prefer natural breaks in the configuration column, for example after
  `1080 帧` or before `共 15 个独立进程`; do not split version strings.
- Preserve `640×640`, the en dash in `split-v2`, and all version-number
  punctuation exactly.

## 4. Content boundary

All 17 protocol rows are required. Do not add unrecorded clock/power state,
resource utilization, real-camera conditions, or new hardware assumptions.
Do not remove a row in a way that changes the frozen experiment identity or
interpretation.

## 5. Manual completion checklist

- [ ] Source values match Section 3.1 of the accepted manuscript.
- [ ] Three horizontal rules and no vertical rules are used.
- [ ] No required protocol row is omitted.
- [ ] Final wrapping does not alter text or numeric strings.
- [ ] Table remains legible at final manuscript width.
