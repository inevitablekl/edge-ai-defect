# Q1 Platform and Asset Preflight Report

## Verdict

`Q1_BLOCKED_SPLIT_ISOLATION_FAILURE`

Platform, ONNX, FP16 Engine, FP16 manifest, TensorRT capability, and manifest counts passed. Split isolation failed: train and val have one shared image-content SHA256 despite having distinct normalized relative paths.

## Git

branch: `feature/jetson-tensorrt-int8`
HEAD: `8acde5cac5d5a2560d164f41d521ba6b50bd61bc`
worktree: clean before evidence generation

## Platform

JetPack/L4T: JetPack not directly reported; L4T `R36.5.0`
Device: `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`
Ubuntu: `22.04.5 LTS`
Kernel: `5.15.185-tegra`
CUDA: `nvidia-smi` reports `12.6`; `nvcc` is `NOT AVAILABLE` (`nvcc command not found`)
TensorRT: package `10.3.0.30-1+cuda12.5`; Python binding `10.3.0`

## Frozen Assets

ONNX: exists, 12,242,487 bytes
SHA: `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` — verified

FP16 Engine: exists, 8,928,756 bytes
SHA: `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` — verified

FP16 Manifest: exists
SHA: `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63` — verified

FP16 recovery: Stage K local Evidence and `/home/orin/edge-ai-local-models/stage_k/` contain the frozen artifact. No rebuild was needed or attempted.

## Dataset

train: 1260; manifest SHA `82687d1b969ac7b9af2a759ea0c39fbf68f71161a13765f3ceb27443c67c8591`
val: 360; manifest SHA `d7de5f3ee47353144ac8a11706cd8cfcfe89285fe08ab01b7ee60f0a2d757ebf`
test: 180; manifest SHA `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8`

normalized relative path isolation: PASS (`0/0/0`)
image content SHA256 isolation: FAIL: train ∩ val = 1; train ∩ test = 0; val ∩ test = 0
collision: SHA `4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071`, `IMAGES/patches_101.jpg` and `IMAGES/patches_105.jpg`

## TensorRT Capability

version: `10.3.0.30` package / `10.3.0` Python binding
Builder API: available
INT8 support: `BuilderFlag.INT8` available
IInt8EntropyCalibrator2: available

No builder, calibrator instance, cache, engine build, benchmark, or accuracy experiment was executed.

## Disk

Root filesystem: 233G total, 33G used, 188G available, 15% used. This is recorded only; no cache or engine was created.

## Evidence

Path: `results/validation/stage_q/q1_platform_asset_preflight_v1/`

## Authorization

Q1 historical preflight: `Q1_BLOCKED_SPLIT_ISOLATION_FAILURE`
Resolution: resolved by `split_v2_deduplicated`
Final Q1 gate: `Q1_PLATFORM_AND_ASSET_PASS_WITH_SPLIT_REMEDIATION`
Q2: NOT AUTHORIZED UNTIL REVIEW
Production: NOT AUTHORIZED

## Q1-B Split Remediation Closure

The original split-isolation failure above is retained unchanged as historical
evidence. Q1-B generated the versioned authority at
`results/validation/stage_q/split_v2_deduplicated/` without modifying the
historical split. The v2 train/val/test counts are `1260/359/180`; path and
content SHA256 isolation both pass. Training impact is `PENDING VERIFICATION`.
Stage K/P test corpus identity is unchanged. Stage Q uses the v2 train split
as the future calibration source; no calibration manifest or calibration run
was generated.
