# Table 2 — Platform, Model, and Benchmark Protocol

Status: `CANDIDATE / SPECIFICATION`
Scientific role: a compact reproduction envelope, not a provenance dump. Target width: preferably `7.5–8.0 cm` if readable, otherwise at most `16.0 cm`; native three-line Word table in D-B.

## Content allocation

### KEEP_IN_TABLE

- Platform: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super.
- Software: L4T 36.4.3, CUDA 12.6, TensorRT 10.3, OpenCV 4.5.4.
- Detector/input: YOLOv8n, `640 × 640`, batch 1.
- Engine: frozen TensorRT INT8 mixed-precision Engine (`INT8 + FP16 fallback`, host input FP32).
- Calibration, compact: 1260 deduplicated training images, `IInt8EntropyCalibrator2`, batch 1, test split excluded.
- Workload: fixed 180-image test workload.
- Paths: V0 / V2R / V3R, single-frame sequential execution.
- Timing: 60 warm-up frames; 1080 measured frames/process; 5 independent processes/path.
- Measurement exclusions: diagnostics/profiling disabled during formal timing.

### KEEP_IN_TEXT

- `MAXN_SUPER`, nvpmodel mode 2.
- `jetson_clocks` was not invoked; clock frequencies were not independently archived.
- Approximate pre/post temperatures and the non-continuous observation boundary.
- Calibration forced-cache-miss detail and exact wording that the generated cache was archived but not reused as formal-build input.
- Explicit negative claims that cannot be proven: no throttling, fixed frequencies, fixed fan speed, continuous thermal stability, or stable power state.

### OMIT_AS_REDUNDANT

- Repository/local absolute source paths, file hashes, full engine/calibration manifests, and repeated narrative definitions already available in Level-B evidence.
- Long explanations of each path already carried by F1/T1.
- Governance labels and audit workflow language that do not aid scientific reproduction.

The existing T2 body remains the conceptual starting point, but D-B may only add compact, evidence-backed facts. The allocation above prevents width inflation.

## Evidence sources

- `docs/paper/phase5_6/phase56b_runtime_state.json`
- `docs/paper/phase5_6/phase56b_calibration_provenance.json`
- `docs/paper/phase5_6/phase56b_run_level_metrics.csv`
- current manuscript Table 2, read-only in D-A

## Candidate caption

**平台、模型与统一基准协议。** 三条路径在相同Jetson平台、YOLOv8n、冻结TensorRT INT8混合精度Engine、固定测试工作负载和统一预热/测量协议下执行；表内仅保留复现实验所需的紧凑条件。

## Candidate and D-B plan

- Candidate: `candidates/table2_platform_protocol_candidate.md`
- Generator: `scripts/generate_phase56d_table_candidates.py`
- D-B: reconcile compact rows with the then-current manuscript, create a native three-line table, and move the `KEEP_IN_TEXT` qualifiers into nearby prose only under explicit integration authorization.
