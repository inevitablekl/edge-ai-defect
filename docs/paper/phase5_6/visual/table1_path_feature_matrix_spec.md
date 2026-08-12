# Table 1 — Path Feature Matrix

Status: `CANDIDATE / SPECIFICATION`
Scientific role: make the controlled variables and sole V2R→V3R change legible within five seconds. Target width: up to `16.0 cm`; native three-line Word table in D-B.

## Frozen columns and rows

| Path feature | V0 | V2R | V3R |
|---|---|---|---|
| Detector / Engine | Same | Same | Same |
| CPU pixel preprocessing | Yes | No | No |
| CUDA preprocessing | No | Yes | Yes |
| Host FP32 input tensor | Yes | No | No |
| Packed raw-image staging | No | Pageable | Pinned |
| Raw-image H2D | No | Yes | Yes |
| Tensor formation | Host | Device | Device |
| Direct TRT device-input formation | No | Yes | Yes |
| TRT CUDA stream reuse | — | Yes | Yes |
| Cross-frame pipeline | No | No | No |

Each cell is traced to implementation authority in `phase56_visual_evidence_map.csv`; the matrix is not produced from the Master Plan. The em dash means the GPU-preprocessing stream-reuse comparison is not applicable to V0, not “unknown.” T1 must not duplicate platform/protocol rows from T2.

## Candidate caption

**V0、V2R和V3R受控数据路径的特征矩阵。** 三条路径使用相同detector和TensorRT Engine；V0在主机侧形成FP32输入张量，V2R/V3R在设备侧形成输入张量，且后两者仅在pageable与pinned原始图像暂存类型上不同。三条路径均为单帧顺序执行，无跨帧流水线。

## Candidate and D-B plan

- Candidate: `candidates/table1_path_feature_matrix_candidate.md`
- Generator: `scripts/generate_phase56d_table_candidates.py`
- D-B: create native three-line Word table, verify every cell against evidence map, fit within 16.0 cm, and integrate at the controlled-path definition.
