NEU-DET training evidence
=========================

This directory contains lightweight, machine-readable training evidence tracked
by Git. It intentionally excludes checkpoints, predictions, plots, caches,
datasets, and complete experiment directories.

Offline archives
----------------

1. edge-ai-defect_training_stage_20260712.tar.gz
   SHA256: a8b62be94e08f1d3e41c6e589f2171b001490cf772b0ab13ca60fa4d41660756
   Purpose: training reports, test artifacts, configurations, environment
   snapshots, and lightweight per-experiment records.

2. edge-ai-defect_training_evidence_patch_20260712.tar.gz
   SHA256: 7c44f5ad992a6b539027d29e249e9f87717661b6750552b33f0a2a8015ac8341
   Purpose: machine-readable validation/test metrics, effective args, commands,
   test artifacts, and provenance.

3. edge-ai-defect_training_checkpoints_patch_20260712.tar.gz
   SHA256: a50525dc3e68a569e81d6319b9bf9d9cc43f9db26c5df3d87e09f48b8a765847
   Purpose: all nine formal-training best.pt checkpoints and their metadata.

All three archives are local-only and excluded from Git. Their external SHA256
records and internal MANIFEST files provide transfer and per-file integrity
verification. Git retains only lightweight documentation, metrics, args,
commands, hashes, and provenance.

Contents
--------

- effective_args/: actual Ultralytics args.yaml for all nine experiments.
- experiment_effective_args_summary.json: selected effective parameters.
- validation_metrics_by_experiment.json/.csv: validation metrics for all nine
  historical best.pt files.
- frozen_test_metrics.json/.csv: final frozen-model test metrics and counts.
- EXPERIMENT_PROVENANCE.json: archive-relative and historical provenance.
- validation_command.txt / frozen_test_command.txt: evaluation commands.
- frozen_test_environment.txt: framework versions and frozen-model hash.

Current evidence boundary
-------------------------

The historical evidence-patch README referred to a test_summary.json that was
not emitted by the original evaluation. That statement is superseded by this
Git-tracked evidence: test metrics come from the retained evaluation records,
and image/instance counts come from the fixed local test split. No training or
validation was rerun during closeout, and the test split was not used for model
selection or tuning.

The canonical frozen-model SHA256 is:
5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7
