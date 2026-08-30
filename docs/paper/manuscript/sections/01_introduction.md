<!-- MANUSCRIPT_SECTION: 0; INTRODUCTION -->

# 0 引 言

金属表面缺陷会影响产品质量与后续制造过程，因而需要在生产现场及时完成视觉检测。NEU-DET覆盖开裂、夹杂、斑块、点蚀表面、轧制氧化皮和划痕等典型热轧钢带缺陷，为这一任务提供了公开研究对象 [@lv_et_al_2020_metallic_defects; @song_yan_2013_neu_surface_defects]。当检测过程部署到靠近数据源的边缘设备时，系统评价不仅涉及模型精度，还涉及从数据源取帧、输入形成、模型执行、后处理到结果构造的完整端到端（end-to-end，E2E）响应；仅以网络执行时间代替完整处理响应，无法覆盖模型入口之前的数据组织成本。

检测模型通过轻量化骨干、注意力机制和多尺度特征融合改善精度与复杂度权衡 [@shao_et_al_2024_td_net; @chu_yu_rong_2024_strip_steel_yolov8; @zhang_pang_jiang_2024_gdm_yolo]，YOLOv8也提供训练、推理和导出链路 [@ultralytics_2023_yolov8_docs]；这些工作为边缘执行提供推理基础，但不能描述模型入口前的数据组织。

完整边缘检测链涵盖数据获取、预处理、模型执行、后处理与数据管理 [@stacker_et_al_2021_edge_runtime]；CPU与GPU间的预处理调度会改变运行时路径 [@lee_han_kim_2025_presto]，现场应用也要求在设备附近完成端到端处理 [@weiss_et_al_2024_realtime_component_inspection]。低精度虽可压缩网络侧开销，量化误差仍须受任务正确性约束 [@jacob_et_al_2018_integer_inference; @nagel_et_al_2020_adaround]。因此本文固定检测器、输入、TensorRT INT8混合精度Engine、工作负载与后处理语义；TensorRT 10.3传统隐式INT8量化及calibrator接口存在版本边界 [@nvidia_tensorrt_10_3_release_notes]，性能比较应维持任务行为 [@kim_lee_kim_2024_hyq]。但固定网络与Engine仍不唯一决定输入数据路径。

推理对象固定后，输入路径仍需决定跨边界表示、输入张量形成位置、额外打包原始图像的主机暂存组织和执行拓扑。Jetson检测部署已有多种端到端组织 [@tang_qian_2024_yolov8_jetson_orin]；主机内存与异步复制有特定适用条件 [@nvidia_cuda_best_practices_12_6]，内存策略响应取决于平台、工作负载和访问方式 [@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]，并受流与复制规则约束 [@nvidia_cuda_programming_guide_12_6]；并发或流水化研究还表明执行拓扑本身是系统选择 [@kim_et_al_2025_concurrent_edge_detection]。

上述工作为具体结构选择提供了实现与评价依据，但如果缺少统一的路径描述，不同改变容易被组织为彼此孤立的优化技巧：表示变化、张量形成位置迁移、暂存策略调整和执行拓扑变化可能在一次比较中同时发生，也可能只有一个变量改变。由此产生的核心评价问题不是若干技术“组合得不够”，而是缺少一个能够在正确性保持和统一E2E边界下区分耦合路径级干预与单变量局部细化的评价对象。平均响应之外，尾部响应还是独立的系统性能维度 [@dean_barroso_2013_tail_scale]；Jetson平台比较具有配置依赖性 [@shin_kim_2022_jetson_yolo_frameworks]，缺陷检测基准也要求明确数据和评价边界 [@lema_et_al_2025_surface_defect_benchmark]。因此，结构变量的干预范围和响应维度均需被显式控制，而不能事后由某个API或组件名称代替。

为填补该缺口，本文以结构描述符\(P=(R,F,M,E)\)表示固定推理对象下的输入数据路径，并以任务正确性保持为性能比较准入条件。据此研究：固定推理对象、工作负载和任务语义时，路径级耦合重构对完整E2E平均响应的影响；其余结构变量、GPU预处理语义及下游结构固定时，主机暂存策略的单变量变化是否带来额外平均响应及一致的P95/P99改善。形式化表述见1.3节。

本文的主要贡献包括两点：1）面向固定推理对象，建立由跨主机—设备边界表示、输入张量形成位置、额外打包原始图像暂存策略和执行拓扑构成的输入数据路径抽象，使两级比较能够按受控结构变量范围区分；2）在任务正确性保持条件下，分别评价路径级耦合重构和暂存策略级细化，联合给出E2E均值、吞吐率及P95/P99响应，并形成受限于本文平台与配置的路径评价原则。
