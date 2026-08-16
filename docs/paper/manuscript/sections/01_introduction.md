<!-- MANUSCRIPT_SECTION: 0; INTRODUCTION -->

# 0 引言

金属表面缺陷自动检测是工业视觉的重要应用，NEU-DET提供开裂、夹杂、斑块、点蚀表面、轧制氧化皮和划痕等典型缺陷数据 [@lv_et_al_2020_metallic_defects; @song_yan_2013_neu_surface_defects]。现有研究通过轻量化骨干、注意力和多尺度特征融合改善检测精度与复杂度权衡 [@shao_et_al_2024_td_net; @chu_yu_rong_2024_strip_steel_yolov8; @zhang_pang_jiang_2024_gdm_yolo]，YOLOv8提供多尺度检测模型及训练、推理和导出能力 [@ultralytics_2023_yolov8_docs]。面向资源受限边缘平台时，完整检测还包括预处理、推理、后处理和数据管理 [@stacker_et_al_2021_edge_runtime; @lee_han_kim_2025_presto]，并需在现场附近完成完整处理流程 [@weiss_et_al_2024_realtime_component_inspection]。

INT8部署可降低网络侧计算开销，但量化扰动仍需任务正确性约束 [@jacob_et_al_2018_integer_inference; @nagel_et_al_2020_adaround]，且网络低精度化不会自动消除图像解码后的主机侧输入形成和主机—设备数据移动。本文以TensorRT 10.3校准式INT8混合精度推理为固定前提；该版本传统隐式INT8量化和calibrator接口已标记为弃用，结论因而限定于本文软件栈 [@nvidia_tensorrt_10_3_release_notes]。研究范围收敛到固定检测器与Engine条件下的输入形成位置、主机数据表示、输入复制载荷和pageable/pinned暂存。

本文设置三条受控路径：V0在主机侧形成FP32 NCHW张量并复制至设备；V2R改为packed BGR原始图像暂存、`cudaMemcpy2DAsync`二维H2D复制和GPU融合预处理，直接形成TensorRT设备输入；V3R保持CUDA预处理、CUDA stream和下游拓扑不变，仅将pageable暂存替换为pinned暂存。

本文的主要贡献包括两点：1）在固定YOLOv8n和TensorRT INT8混合精度Engine条件下，将主机FP32张量输入路径重构为原始图像H2D与GPU融合预处理，并通过pageable/pinned配置隔离主机暂存类型；2）在统一的任务正确性、E2E延迟、进程级FPS和合并样本P95/P99口径下，通过V0→V2R与V2R→V3R两级受控比较，区分完整输入路径重构的主要收益与pinned暂存的有限平均增量，并以每条路径5个独立进程考察运行级分布和尾延迟。受控路径见图1。

**图1　V0、V2R和V3R三条受控数据路径。图中数值为完整路径E2E观测，输入复制载荷为名义值。**
