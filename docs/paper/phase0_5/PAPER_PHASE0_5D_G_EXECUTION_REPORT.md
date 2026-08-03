# Paper Phase 0.5D-G Execution Report

## 1. Verdict

`COMPLETE`

Phase 0.5D-I2 timing-aligned formal benchmark evidence was frozen as a compact
paper evidence package and committed to Git. The 15-run result remains
`TIMING_ALIGNED_RERUN_PASS`.

## 2. Git

```text
Branch: main
Before commit SHA: 6885dc5c8d1099c34f1cd8d10c4b30426df61daf
Initial freeze commit SHA: 9d6f8c871d4ea3b762e871a2f9178e862a6d3f95
After amend SHA: verified as final repository HEAD after this report was staged
and committed with `git commit --amend --no-edit`.
Commit message: docs(paper): freeze timing aligned Stage R evidence
Push: none
Tag: none
Merge: none
```

The amended freeze commit contains the formal report, both Phase 0.5D reports,
and the compact evidence assets. The final amend SHA is intentionally verified
from repository HEAD rather than duplicated inside this self-referential
commit report.

## 3. Evidence

Tracked assets:

```text
docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md
docs/paper/phase0_5/PAPER_PHASE0_5D_G_EXECUTION_REPORT.md
docs/paper/phase0_5/PAPER_PHASE0_5D_I2_CLEANUP_REVIEW.md
docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/manifest.json
docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/artifact_sha256.txt
```

Raw formal evidence was not copied into Git. It was moved locally to:

```text
/home/orin/edge-ai-local-evidence/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/
```

The archive contains `archive_manifest.tsv`, all 112 raw files, and the
preserved failed-attempt evidence under `runs/set_01_p01_v0/`.

## 4. Verification

```text
Formal report SHA256: 3d9ea96fc430a94b090bcd2f9241313df81d5cd82bc7f7bcb7b05f47c95a85ec
Compact manifest SHA256: 74b77515020d4924060dd7f4c7bd773229684fb18d0bd5a6e004cfe41f5309c0
Raw archive files: 112
Raw archive total size: 12746622 bytes
Raw archive per-file SHA256 verification: PASS (112/112, 0 mismatches)
Original repository raw path: ABSENT
git diff --check: PASS
git diff --cached --check before commit: PASS
```

Final `git status --short` after the amend was empty. Both reports are part of
the amended freeze commit.

## 5. Scope Compliance

```text
Experiment rerun: no
Metrics regenerated: no
Runner modified: no
Benchmark logic modified: no
Configuration modified: no
CUDA/TensorRT/Stage R code modified: no
Formal raw evidence deleted: no
```

## 6. Recommended Next Actor

`Paper Project Manager`
