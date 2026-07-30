# Stage P P0 Baseline Report

## Execution identity

- Timestamp: `2026-07-30T01:17:41+08:00 CST`
- Repository: `inevitablekl/edge-ai-defect`
- Repository root: `/home/orin/edge-ai/edge-ai-defect`
- Initial branch: `main`
- Initial HEAD: `c6890d86e7534500cfe31c40dd73f151d77d5362`
- Local main: `c6890d86e7534500cfe31c40dd73f151d77d5362`
- `origin/main`: `c6890d86e7534500cfe31c40dd73f151d77d5362`
- Tag: `stage-k-tensorrt-fp16-complete-v1.0`
- Tag object type: `tag` (annotated)
- Tag peeled commit: `c6890d86e7534500cfe31c40dd73f151d77d5362`
- Equality: PASS
- Initial index/tracked worktree: clean
- Worktrees: one, repository root at baseline on `main`
- Stage P branch checks before creation: local branch absent; remote-tracking
  branch absent; exact remote head query returned no ref.
- Created branch: `feature/jetson-pipeline-runtime`
- Branch starting/current pre-freeze HEAD:
  `c6890d86e7534500cfe31c40dd73f151d77d5362`

## Pre-existing planning audit disposition

The only initial untracked files were read and classified as the
`Stage P Planning Input Audit v1` dated 2026-07-29. They were not mixed with
production/config/test/Evidence assets. Each was untracked (not ignored) and
was moved without content change to:

`/home/orin/edge-ai-local-evidence/stage_p/p0_planning_audit/20260730T011741+0800/stage_p_planning_audit_v1/`

| Original repository-relative path | Bytes | Pre-move SHA256 | Post-move SHA256 |
|---|---:|---|---|
| `results/validation/stage_p_planning_audit_v1/README.txt` | 5774 | `b4fd4ac251eb846658143e73f511933d34334ea8023a92dbcdc3ed0b8740f428` | same |
| `results/validation/stage_p_planning_audit_v1/architecture_snapshot.md` | 8769 | `ed61f259ff7d00d1dae97f4448b78378926dbc1733759680d2492b8c11d9566a` | same |
| `results/validation/stage_p_planning_audit_v1/paper_experiment_inventory.md` | 4538 | `a73bd8db757c1d205548972abdc5427d215c183dcaee5ed49ed956151575de7f` | same |
| `results/validation/stage_p_planning_audit_v1/runtime_capability_matrix.md` | 3945 | `58f3b6523948a5f96a41db36b226e963cd0e9ad66df3c5ccf701b1fc57f6eaca` | same |
| `results/validation/stage_p_planning_audit_v1/stage_k_final_baseline.md` | 3387 | `91eb9ba04c7a2f51af27ef3c305152380c1d28a59793a3510b46b199da22648b` | same |
| `results/validation/stage_p_planning_audit_v1/stage_p_candidate_direction.md` | 5440 | `cbd9344fa411ec549100ec9eb951b696f13873177e3e6ec22132399e34436607` | same |

## Stage K relationship and frozen identities

Stage K is `COMPLETE`; its post-finalization cleanup is also `COMPLETE`.
D066 accepts the Original TensorRT FP16 Engine from task-level accuracy,
stability, and formal serial performance. Raw TensorRT Level B remains
`FAIL — retained known limitation`. No Stage K historical Evidence was edited.

| Asset | Accurate tracked path | SHA256 |
|---|---|---|
| Frozen Stage K 180-image manifest | `results/validation/stage_k_task_eval_v2/split/test_manifest.json` | `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8` |
| Original TensorRT FP16 Engine manifest | `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json` | `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63` |
| Engine content identity recorded by manifest | local-only Engine (not copied) | `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` |
| ModelContract | `configs/model_contracts/yolov8n_neudet_frozen.yaml` | `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` |

## Current implementation facts (read-only inventory)

- `RunSummary` currently has only `processed_images` and
  `total_detections`.
- `RunMetadata` has no `runtime_v3`.
- RuntimeConfig has no `runtime.mode`, `pipeline`, or `video_file` union.
- Result JSON supports historical schema v1 and TensorRT schema v2.
- `TraceRecorder` supports one active interval.
- `CompositeSink` forwards `begin_run` and `write_frame` in declaration
  order and `end_run` in reverse order.
- Current OpenCV components are `core`, `imgproc`, and `imgcodecs`.
- `opencv_videoio` is not configured.
- `Threads::Threads` is not configured.
- Production application composition remains Serial; no PipelineRunner,
  BoundedQueue, VideoFileSource, CorpusReplaySource, or Stage P experiment
  runner is present.

Relevant current CMake targets include:

- `edge_ai_core`, `edge_ai_backend_ort`, `edge_ai_backend_trt`,
  `edge_ai_postprocess`, `edge_ai_runtime`, `edge_ai_backend_factory`,
  `edge_ai_application`;
- `edge_ai_infer`, `stage_j_profile_runner`,
  `stage_k_raw_tensor_runner`.

Relevant current test targets/files include:

- `test_runtime_config`, `test_runtime_types`, `test_result_sinks`,
  `test_serial_runner`, `test_directory_source`, `test_cli`;
- `tests/test_application_smoke.py`;
- existing Stage K foundation, TensorRT engine, raw tensor runner, model
  contract, preprocessing, postprocessing and ONNX Runtime tests registered
  conditionally by the current CMake configuration.

## P0 changed-file allowlist

Only these Markdown paths are authorized:

- `docs/personal/STAGE_P_EXECUTION_PLAN.md`
- `docs/personal/STAGE_P_TASK_CARDS.md`
- `docs/personal/STAGE_P_BASELINE_REPORT.md`
- `docs/personal/DECISIONS.md`
- `docs/personal/TASKS.md`
- `docs/personal/EXPERIMENT_PLAN.md`
- `docs/PROJECT_BRIEF.md`
- `docs/REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `README.md`

## v1.1 → v1.2 normalization crosswalk

| Instruction normalization | v1.2 location/effect |
|---|---|
| Dual CanonicalHashSink scope | N1; independent RUN=1 and CYCLE=2 streams; exact P4–P7 scope mapping |
| `source_frames` and EOS | N2; counts only successfully returned non-EOS frames; block-only equality |
| Empty input | N2 and P3 card; failure, one probe, no `end_run`, unchanged summary |
| WSL v4 smoke boundary | N3, section 20 platform matrix, P3/P4 cards |
| Video identity/max_frames/codec | N4, section 29, P6 card |
| P6 dependency | N5, sections 29/35 and P5/P6 cards |
| Trace failures | N6 and P1/P3 cards; production JSON atomic commit is not rolled back |
| Measured-window/exact identity | N7; D066 raw limitation retained |

The frozen route is unchanged.

## Verification scope

No build, CTest, TensorRT Engine build, inference, formal benchmark, stability
run, or formal Evidence attempt was executed. P0 is documentation freeze and
read-only inventory work; runtime testing would violate or exceed this task.
No push, merge, rebase, or tag was performed.
