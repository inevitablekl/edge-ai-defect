# Table 1 candidate — Path Feature Matrix

> **CANDIDATE / SPECIFICATION — not manuscript authority**

| Path feature | V0 | V2R | V3R |
|---|---:|---:|---:|
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

Evidence: every data cell maps separately in `../phase56_visual_evidence_map.csv`.
