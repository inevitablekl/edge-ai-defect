# Paper Phase 4.4 Figure/Table Source Preparation

## 1. Verdict

PHASE_4_4_SOURCE_PACKAGE_READY_FOR_USER_GUI

## 2. Figure 1

- final GUI owner: USER_MANUAL / Visio
- deterministic specification:
  `docs/paper/manuscript/figures/fig1_visio_spec_v1.0.md`
- deterministic preview:
  `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths.svg`
- scientific boundaries: V2R and V3R share CUDA preprocessing semantics; the
  isolated V2R→V3R variable is pageable versus pinned host staging; all paths
  remain single-frame sequential
- prototype remains non-final: YES
- final Visio/project export created: NO

## 3. Figure 2

- authoritative CSV:
  `docs/paper/manuscript/figures/fig2_mean_fps_origin_data.csv`
- Origin specification:
  `docs/paper/manuscript/figures/fig2_origin_spec_v1.0.md`
- frozen values: V0 `54.600 ± 0.223` FPS; V2R `122.122 ± 0.492` FPS;
  V3R `127.097 ± 1.279` FPS
- error-bar semantics: sample standard deviation of the same five independent
  process-level FPS samples used for each mean
- final Origin project/export created: NO

## 4. Figure 3

- authoritative CSV:
  `docs/paper/manuscript/figures/fig3_mean_tail_latency_origin_data.csv`
- Origin specification:
  `docs/paper/manuscript/figures/fig3_origin_spec_v1.0.md`
- frozen V0 values (Mean/P95/P99, ms): `18.273 / 18.854 / 19.068`
- frozen V2R values (Mean/P95/P99, ms): `8.140 / 9.827 / 11.529`
- frozen V3R values (Mean/P95/P99, ms): `7.812 / 9.842 / 11.515`
- statistical population: each statistic uses the corresponding variant's
  pooled 5,400 per-frame latency samples
- mixed-tail protection: no inset or truncated axis; V3R P95 is slightly
  higher/slower and P99 is slightly lower/faster than V2R
- final Origin project/export created: NO

## 5. Tables

- Table 1 publication source/specification:
  `docs/paper/manuscript/tables/table1_publication_spec_v1.0.md`
- Table 2 publication source/specification:
  `docs/paper/manuscript/tables/table2_publication_spec_v1.0.md`
- Table 1 preserves all accepted platform/model/dataset/run-protocol rows
- Table 2 preserves `claim_ids = A2` and
  `source_experiment = R_V0;R_V2R`
- V3R excluded from Table 2: YES

## 6. Scientific Freeze

- frozen values changed = NO
- contribution count = 2
- excluded evidence restored = NO
- new statistics = NO
- significance claims = NO

This phase prepares publication sources only. It does not alter the accepted
scientific body, rerun experiments, replace Phase 1 authority, or create final
GUI-authored figures.

## 7. Manual Work Remaining

- Figure 1 final Visio construction
- Figure 2 final Origin construction
- Figure 3 final Origin construction
- final publication exports
- visual review at manuscript placement size and in monochrome
