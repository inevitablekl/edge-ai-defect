<!-- MANUSCRIPT_SECTION: FRONT_MATTER; TITLE_ABSTRACT -->

# 题名与摘要

## 中文题名

Jetson端工业缺陷检测的输入数据路径重构

## 中文摘要

针对边缘工业缺陷检测中网络低精度化不能直接消除输入形成与主机—设备数据移动开销的问题，本文将固定推理对象下的输入数据路径抽象为跨边界表示、输入张量形成位置、额外打包原始图像暂存策略和执行拓扑四类结构变量。在固定YOLOv8n、TensorRT INT8混合精度Engine和单帧顺序拓扑的条件下，构造V0→V2R路径级重构与V2R→V3R暂存策略级细化两级受控干预，并以任务正确性保持为性能比较约束。冻结的180幅图像离线回放实验表明，三条路径的任务级指标一致；V2R相对V0达到2.24× FPS，平均端到端延迟降低55.45%；V3R相对V2R的FPS提高4.07%，平均延迟降低4.03%，而P95增加0.15%、P99降低0.12%，尾延迟变化方向相反。结果说明，在受测平台与配置下，输入表示和张量形成位置的联合重构对应显著的完整路径平均响应，局部暂存策略变化仅产生有限平均增量，且未形成一致的尾延迟改善证据。输入表示、张量形成位置和主机暂存策略应作为不同的数据路径变量评价，并分别考察平均与尾部响应。

## 中文关键词

Jetson；工业缺陷检测；输入数据路径；端到端推理；受控比较

## English Title

Input Data-Path Reconstruction for Industrial Defect Detection on Jetson

## English Abstract

For edge-based industrial defect detection, reducing network precision does not by itself eliminate input formation and host-device data-movement costs. This study abstracts the input data path of a fixed inference object by four structural variables: the representation crossing the host-device boundary, the location where the input tensor is formed, the policy for additional packed raw-image host staging, and the execution topology. With a fixed YOLOv8n detector, TensorRT INT8 mixed-precision Engine, and sequential single-frame topology, two hierarchical controlled interventions are constructed: the V0-to-V2R path-level reconstruction and the V2R-to-V3R staging-policy refinement. Performance comparisons are admitted only under preserved task correctness. Offline replay of the frozen 180-image workload yields identical task-level metrics for all three paths. Relative to V0, V2R achieves 2.24× FPS and 55.45% lower mean end-to-end latency. Relative to V2R, V3R improves FPS by 4.07% and lowers mean latency by 4.03%, whereas P95 increases by 0.15% and P99 decreases by 0.12%, giving opposite tail-latency directions. Under the tested platform and configuration, jointly reconstructing the input representation and tensor-formation location corresponds to a substantial complete-path mean response, while the local staging-policy change yields only a limited mean increment and no consistent tail-latency improvement. Input representation, tensor-formation location, and host staging policy should therefore be evaluated as distinct data-path variables, with mean and tail responses considered separately.

## English Keywords

Jetson; industrial defect detection; input data path; end-to-end inference; controlled comparison
