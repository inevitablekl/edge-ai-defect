Stage K Post-Finalization Repository Cleanup Audit v1
=====================================================

Audit date: 2026-07-29
Source commit: d4b50739c2f5f1db9ba7b48e653618b2af9cd98a
Scope: repository cleanup only; no experiment was executed.

Result
------

The Stage K repository cleanup preserved the official evidence trees and
archived diagnostic assets without changing their contents. The detailed
per-file inventory is in cleanup_inventory.json.

Official assets kept at their original paths:

  results/validation/stage_k6/
  results/validation/stage_k7/
  results/validation/stage_k_task_eval_v2/
  results/validation/stage_k8/

Diagnostic assets moved to:

  results/archive/stage_k_diagnostics_v1/

The archive contains the 108 moved files listed in archive_manifest.json.
Each entry records its original path, archive path, size, and SHA256. The
old task-evaluation v1 files and strict/FP32 control investigations were
preserved as historical diagnostic material, not deleted.

Temporary cleanup
-----------------

Three confirmed Python bytecode cache files under tools/diagnostic/__pycache__/
were deleted. No Engine, ONNX, ModelContract, source implementation,
comparator tolerance, or formal K5/K6/K7/K8 Evidence was modified.

Git and verification policy
----------------------------

The repository now ignores raw TensorRT engine files, raw .f32le tensor dumps,
and narrowly named debug dump directories. Formal reports, manifests, JSON
summaries, and existing tracked Evidence remain unaffected. SHA256 verification
of the Stage K8 summary, K6 Evidence, and K7 Evidence is required before the
cleanup commit is finalized.
