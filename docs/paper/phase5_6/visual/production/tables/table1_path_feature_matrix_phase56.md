# V0、V2R和V3R路径特征矩阵

| 路径特征 | V0 | V2R | V3R |
|---|---:|---:|---:|
| Detector / Engine | 相同 | 相同 | 相同 |
| CPU像素预处理 | 是 | 否 | 否 |
| CUDA预处理 | 否 | 是 | 是 |
| 主机FP32输入张量 | 是 | 否 | 否 |
| 打包原始图像暂存 | 否 | Pageable | Pinned |
| 原始图像H2D | 否 | 是 | 是 |
| 张量形成位置 | 主机 | 设备 | 设备 |
| 直接形成TRT设备输入 | 否 | 是 | 是 |
| 复用TRT CUDA stream | — | 是 | 是 |
| 跨帧流水线 | 否 | 否 | 否 |

Source trace: `../../phase56_visual_evidence_map.csv`；30个数据单元分别映射到当前实现 authority。
