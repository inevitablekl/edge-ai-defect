# Paper Phase 5.4C-B Automated Figure Route Addendum v1.0

Status: `CANDIDATE_ASSET_PRODUCTION_COMPLETE`; manuscript integration: `NOT_STARTED`.

## 1. Production route

The Phase 5 target production route is now:

| Target | Owner and route | Status |
|---|---|---|
| Figure 1 | `USER_MANUAL` / Visio | unchanged |
| Figure 2 | `USER_MANUAL` / Visio | unchanged |
| Figure 3 | `VSCODE_CODEX` / deterministic Python plotting script | candidate assets generated |
| Figure 4 | `VSCODE_CODEX` / deterministic Python plotting script | candidate assets generated |

This is a production-route substitution only. It supersedes the Figure 3 and
Figure 4 `USER_MANUAL_ORIGIN` route recorded in the earlier Phase 5.4C manual
production package, but does not change the frozen data, captions, scientific
interpretation, or target numbering.

## 2. Authority boundary

The new SVG, PDF, and PNG files are candidate publication assets. They are not
integrated into the manuscript and do not replace current publication authority.
The current accepted Figure 2 and Figure 3 exports, current manuscript callouts,
captions, numbering, and figure manifest remain authoritative until a later
explicitly authorized acceptance and integration task.

No manuscript section, bibliography, table authority, raw evidence, equation,
metric definition, protocol definition, or scientific claim is changed here.

## 3. Deterministic sources

- Target Figure 3 script:
  `docs/paper/manuscript/figures/scripts/generate_fig3_mean_fps_phase5.py`.
- Target Figure 3 data authority:
  `docs/paper/manuscript/figures/fig2_mean_fps_origin_data.csv`.
- Target Figure 4 script:
  `docs/paper/manuscript/figures/scripts/generate_fig4_mean_tail_latency_phase5.py`.
- Target Figure 4 data authorities:
  `docs/paper/manuscript/figures/fig3_mean_tail_latency_origin_data.csv` and
  `docs/paper/manuscript/figures/fig4_v3r_v2r_latency_change_origin_data.csv`.

Both scripts reject any schema, row order, precision-preserving decimal value,
sign, or direction mismatch against the frozen authorities. Stable SVG metadata
and fixed Matplotlib hash salts make repeated SVG generation byte-identical in
the validated repository environment.

## 4. Scientific freeze

The six frozen results remain unchanged:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean-latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail interpretation remains `MIXED`. Contribution count remains exactly `2`.
No new scientific fact is introduced.

## 5. Visual boundary

Figure 3 uses a zero baseline, a 0–150 FPS range, symmetric sample-SD error
bars, black outlines, and redundant color-plus-hatch identity. It contains no
speedup, latency, significance, CI, or SE annotation.

Figure 4 Panel A uses zero-baseline grouped absolute-latency bars without error
bars or inferential annotation. Panel B uses one neutral bar style, an explicit
zero line, the mandatory symmetric `-5%` to `+5%` range, exact signed four-place
labels, and the direction key. The common scale keeps the small, opposite P95
and P99 movements visually small and preserves the `MIXED` tail interpretation.
No red/green or win/loss semantics are used.

## 6. Validation record

- Figure 3 frozen CSV exact-value validation: `PASS`.
- Figure 4 Panel A frozen CSV exact-value validation: `PASS`.
- Figure 4 Panel B value, sign, order, and direction validation: `PASS`.
- SVG/PDF/PNG generation for both figures: `PASS`.
- Consecutive SVG regeneration: `PASS`; Figure 3 SHA-256
  `5438d61eeff785d850929809755e34ab42c35f1f122ebe2639bd2c434f19128a`;
  Figure 4 SHA-256
  `672fc9d5ed235195ecc75b6a86f7d0dfadd7f6fd7929b636258607e31ce87af6`.
- Figure 3 prohibited speedup/latency/significance annotation scan: `PASS`.
- Figure 4 exact visible-label, fixed-range, neutral-style, and mixed-tail
  audits: `PASS`.
- Manual raster inspection for clipping, legibility, zero baseline/line,
  grayscale-safe identity, and honest tail scale: `PASS`.
- Current Full authoritative build: `PASS`; SHA-256
  `4dbde9a34db010347de8a38e2339f86761932f3901e7cab0a948e3493d1fac08`.
- Current Anonymous authoritative build: `PASS`; SHA-256
  `e9271f9304c7f56fcaec21e20ef7da2d604c9536e781b21859a729e9a2862abf`.
- Citation source, rendered bibliography, bibliography identity, and current
  static figure/table cross-reference validation: `PASS`.
- Full/Anonymous scientific-body parity and anonymous identity scan: `PASS`.
- Journal-format structural validation and DOCX ZIP integrity: `PASS`.
- OMML validation: `PASS`; `8` display equations in each build.
- Frozen numerical-result scan, T1/T2/T3 preservation, and contribution-count
  audit: `PASS`; contribution count `2`.
- Manuscript section, bibliography, and table-authority diff scans: empty.
- `git diff --check`: `PASS`.
