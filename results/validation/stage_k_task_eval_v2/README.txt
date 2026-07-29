Stage K Task-Level Evaluation Preparation v1

Status
------

READY_FOR_FULL_TASK_EVALUATION

This directory freezes the deterministic split and evaluation protocol only.
No FP32/FP16 inference was executed by this task.

Split statistics
----------------

  dataset: data/raw/NEU-DET
  seed: 42
  split ratio: 0.70 / 0.20 / 0.10
  train images: 1260
  val images: 360
  test images: 180
  train bboxes after dedup: 2916
  val bboxes after dedup: 828
  test bboxes after dedup: 442
  no image overlap: PASS

Class bbox distribution
-----------------------

  class              train   val   test
  crazing              469   145     74
  inclusion            683   214    113
  patches              646   154     80
  pitted_surface       312    87     33
  rolled-in_scale      429   124     75
  scratches            377   104     67

Manifest SHA256
---------------

  train_manifest.json: 82687d1b969ac7b9af2a759ea0c39fbf68f71161a13765f3ceb27443c67c8591
  val_manifest.json:   d7de5f3ee47353144ac8a11706cd8cfcfe89285fe08ab01b7ee60f0a2d757ebf
  test_manifest.json:  fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8
  split_metadata.json:  ad1bf88319abd7293e6a920b49780e114df9cadc383e7d3a74de45da921cf889

Reproducibility
---------------

Same-seed regeneration with seed 42 produced identical SHA256 values for all
three split manifests. The generator uses sorted XML paths, the established
three-duplicate-bbox removal policy, and random.Random(42).shuffle.

Protocol
--------

  docs/personal/STAGE_K_TASK_EVALUATION_PROTOCOL.md
  protocol/protocol_metadata.json

The later task-level run must evaluate the 180-image test split only, using
the frozen strict FP32 noTF32 reference and TensorRT FP16 candidate with
identical preprocessing, postprocessing, evaluator, and ordered test manifest.

Scope
-----

No Engine, ONNX, Runtime, comparator tolerance, K5 gate, raw image, XML, or
official Stage K document was modified. No inference, benchmark, or tensor
dump was created.
