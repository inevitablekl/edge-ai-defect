# Paper Phase 4 Final Figure Integration

## 1. Verdict

PHASE_4_FINAL_FIGURE_PACKAGE_INTEGRATED

## 2. Figure 1

- final VSDX: `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_final.vsdx`
- final PDF: `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_final.pdf`
- final SVG: `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_final.svg`
- final artifact = ACCEPT
- scientific correctness = PASS
- readability finding = CLOSED
- residual Word placement check = Phase 4.9

The accepted V0/V2R/V3R structure and the isolated pageable-versus-pinned
host-staging distinction are unchanged.

## 3. Figure 2

- authoritative CSV: `docs/paper/manuscript/figures/fig2_mean_fps_origin_data.csv`
- plotting script: `docs/paper/manuscript/figures/scripts/plot_fig2_mean_fps.py`
- final PDF: `docs/paper/manuscript/figures/fig2_mean_fps_final.pdf`
- final SVG: `docs/paper/manuscript/figures/fig2_mean_fps_final.svg`
- final PNG: `docs/paper/manuscript/figures/fig2_mean_fps_final.png`
- final artifact = ACCEPT
- error bars = sample standard deviation of five independent process-level FPS samples
- backend = matplotlib
- Origin final project = NOT_REQUIRED / SUPERSEDED
- font limitation = Liberation Serif fallback; deferred to Phase 4.8/4.9

The final script reads the authoritative CSV directly, uses `Mean_FPS` as Y,
and uses `Sample_SD_FPS` as symmetric Y error without inferential statistics.

## 4. Figure 3

- authoritative CSV: `docs/paper/manuscript/figures/fig3_mean_tail_latency_origin_data.csv`
- plotting script: `docs/paper/manuscript/figures/scripts/plot_fig3_mean_tail_latency.py`
- final PDF: `docs/paper/manuscript/figures/fig3_mean_tail_latency_final.pdf`
- final SVG: `docs/paper/manuscript/fig3_mean_tail_latency_final.svg`
- final PNG: `docs/paper/manuscript/fig3_mean_tail_latency_final.png`
- final artifact = ACCEPT
- latency series = Mean/P95/P99 in V0/V2R/V3R order
- tail interpretation = MIXED
- backend = matplotlib
- Origin final project = NOT_REQUIRED / SUPERSEDED
- font limitation = Liberation Serif fallback; deferred to Phase 4.8/4.9

V3R P95 remains slightly higher/slower than V2R, while V3R P99 remains
slightly lower/faster than V2R. The pooled-5,400-sample interpretation is
unchanged.

## 5. Captions

- Figure 1 caption PASS
- Figure 2 SD note PASS
- Figure 3 pooled-5400 note PASS

## 6. Scientific Freeze

- frozen values changed = NO
- new statistics = NO
- excluded evidence restored = NO
- significance claim = NO
- V3R mixed-tail interpretation preserved = YES

## 7. Publication Limitations

- Figure 1 final Word-scale readability: `DEFERRED_FINAL_VISUAL_CONFIRMATION`
- Figure 2/3 Liberation Serif: `TYPOGRAPHY_LIMITATION_DEFERRED`

Neither is a current blocker.

## 8. Next Step

Table 1 / Table 2 final three-line table finalization.
