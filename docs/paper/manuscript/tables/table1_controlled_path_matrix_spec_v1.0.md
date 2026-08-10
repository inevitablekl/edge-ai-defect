# Target Table 1 Controlled-Path Matrix Specification v1.0

Status: `PHASE5_PREPARATION_ONLY`; intended publication form: three-line table.

## Caption and placement

- Chinese: `表1　V0、V2R和V3R受控数据路径配置与比较变量`
- English source: `Table 1 Controlled data-path configurations and comparison variables for V0, V2R, and V3R`
- Intended location: near the beginning of Section 2, before the detailed V0/V2R/V3R method subsections.

## Exact proposed contents

| 路径 | 主要像素级预处理位置 | 原始图像主机暂存 | 与前级路径相比的受控变化 | 比较角色 |
|---|---|---|---|---|
| V0 | CPU/OpenCV | 主机图像及主机FP32张量路径；未将其分配类型定义为V2R/V3R同类原始图像暂存变量 | － | 受控基线 |
| V2R | CUDA/GPU | pageable host raw-image staging | 相对V0改变预处理执行位置及相关输入准备/数据路径 | 较宽的结构/配置干预终点；V2R→V3R参照 |
| V3R | CUDA/GPU（与V2R相同语义） | pinned host raw-image staging | 相对V2R仅改变主机原始图像暂存分配类型 | 较窄的结构/配置干预终点 |

## Cell-level authority

| Cell group | Authority and acceptance rationale |
|---|---|
| Variant labels | Frozen manuscript paths in `sections/03_method.md`, Sections 2.1–2.3. |
| V0 preprocessing | `03_method.md` Section 2.1: CPU/OpenCV letterbox, conversion, layout, normalization and host FP32 tensor. |
| V0 staging wording | Deliberately bounded to the established host image/host tensor path. It does not guess that V0 uses a V2R/V3R-style pageable or pinned raw-image staging allocation. |
| V2R preprocessing and staging | `03_method.md` Section 2.2 and `docs/personal/STAGE_R_EXECUTION_PLAN.md`: row-aware copy to contiguous pageable raw staging and CUDA preprocessing. |
| V3R preprocessing and staging | `03_method.md` Section 2.3: long-lived pinned raw staging and the same CUDA semantics as V2R. |
| V0→V2R controlled change | `03_method.md` Section 2.2 and manuscript Section 1.3: preprocessing execution location plus related input-preparation/data-path changes; structurally broader only. |
| V2R→V3R controlled change | `03_method.md` Section 2.3: the formal isolated variable is host raw-image staging allocation type. |
| Comparison roles | Structural/configuration scope only; no Amdahl `α`, expected speedup, independent stage timing, or universal superiority is assigned. |

## Publication rules

- Use only top rule, header separator, and bottom rule; no vertical rules.
- Keep `pageable` and `pinned` in Latin type. Allow controlled line wrapping rather than shrinking below journal minimum size.
- `－` means no preceding-path delta is defined for the baseline; it is not missing data.
- Do not add columns for independent stage time, Amdahl fraction, transfer overlap, zero-copy, pipeline, or predicted gain.
- Do not state or imply that pinned memory universally improves performance.
