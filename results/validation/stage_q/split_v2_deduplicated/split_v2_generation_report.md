# Stage Q Split v2 Generation Report

## Verdict

`Q1B_SPLIT_REMEDIATION_PASS`

Generated `split_v2_deduplicated` from existing split_v1 entries without
reshuffling and without modifying split_v1.

## Policy

- Identity: image content SHA256.
- Resolution: sort normalized relative paths by UTF-8 byte order within each
  same-SHA group and keep the first entry.
- Removed later entries: 1.
- Random shuffle: not used.

## Duplicate Resolution

- SHA256: `4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071`
- Kept: `train` / `IMAGES/patches_101.jpg`
- Removed: `val` / `IMAGES/patches_105.jpg`
- Reason: same image content SHA256; first UTF-8 path retained.

## Counts

| Split | Before | After | GT boxes after |
|---|---:|---:|---:|
| train | 1260 | 1260 | 2916 |
| val | 360 | 359 | 825 |
| test | 180 | 180 | 442 |
| total | 1800 | 1799 | 4183 |

## Manifest SHA256

- train: `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6`
- val: `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9`
- test: `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`

## Isolation

Path isolation: PASS (`train/val=0`, `train/test=0`, `val/test=0`)
Content SHA256 isolation: PASS (`train/val=0`, `train/test=0`, `val/test=0`)

## Statistics

All six classes remain present in every split. Class image and GT-box counts
are in `split_v2_statistics.json`; GT-box counts follow the source generator's
exact duplicate-YOLO-row policy.

## Scope

The historical split_v1 files, model, training archive, Stage K/P Evidence,
and production code were not modified. No calibration manifest, calibration,
benchmark, accuracy experiment, or Q2 action was executed.
