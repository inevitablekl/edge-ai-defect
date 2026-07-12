NEU-DET training evidence
=========================

This directory contains lightweight, machine-readable evidence copied from the
external training evidence patch and corrected during final training closeout.
It intentionally excludes checkpoints, predictions, plots, caches, datasets,
and complete experiment directories.

Sources
-------

- Original training archive:
  edge-ai-defect_training_stage_20260712.tar.gz
  SHA256: a8b62be94e08f1d3e41c6e589f2171b001490cf772b0ab13ca60fa4d41660756
- Training evidence patch:
  edge-ai-defect_training_evidence_patch_20260712.tar.gz
  SHA256: 7c44f5ad992a6b539027d29e249e9f87717661b6750552b33f0a2a8015ac8341
- Training code commit:
  2fddb7f35fd8fcf2a5066fddb2bec0df47b7133e

Contents
--------

- effective_args/: actual Ultralytics args.yaml for all nine experiments.
- experiment_effective_args_summary.json: selected effective parameters.
- validation_metrics_by_experiment.json/.csv: validation metrics re-run on the
  historical best.pt files during evidence generation.
- frozen_test_metrics.json/.csv: final frozen-model test metrics and counts.
- EXPERIMENT_PROVENANCE.json: archive-relative and historical provenance.
- validation_command.txt / frozen_test_command.txt: evaluation commands.
- frozen_test_environment.txt: framework versions and frozen-model hash.

Test summary note
-----------------

The test metrics were retained from the existing frozen-model test evaluation.
The image count was computed from data/yolo/neu_det/images/test, and the instance
count was computed from non-empty lines in the fixed YOLO test labels. This
closeout did not run training or validation. The test split was used only after
model selection and was not used for tuning.

Storage boundary
----------------

The frozen .pt model and both tar archives remain local-only assets and are not
tracked by Git. The canonical frozen-model SHA256 is
5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7.
