# Paper Phase 5.4B Narrow Claim-Boundary Remediation v1.0

## 1. Verdict

`CLAIM_BOUNDARY_REMEDIATION_COMPLETE`

## 2. Starting state

- Branch: `main`.
- Starting HEAD: `6fe301c15a214880763e7a1cffd152d69e6a8679`.
- Starting subject: `docs(paper): integrate literature evidence and citations`.
- Worktree/index: clean.

## 3. Authorized changes

Only two subsection headings in `docs/paper/manuscript/sections/05_results.md` changed:

1. `## 4.2 CUDA预处理的主要性能收益`
   → `## 4.2 V0→V2R数据路径的主要性能收益`.
2. `## 4.3 Pinned内存的增量收益`
   → `## 4.3 V2R→V3R的增量性能表现`.

No substantive paragraph under §4.2 or §4.3 changed. The revised headings align with the already-correct body boundaries: V0→V2R is a complete tested data-path intervention, and V2R→V3R reports an E2E difference under a controlled staging-allocation change rather than an independently measured pinned-memory component saving.

## 4. Scientific regression audit

- V2R/V0 FPS ratio: `2.236671×`, unchanged.
- V2R/V0 mean-latency reduction: `55.4519%`, unchanged.
- V3R/V2R FPS: `+4.0738%`, unchanged.
- V3R/V2R mean latency: `-4.0349%`, unchanged.
- V3R/V2R P95: `+0.1514%`, higher/slower, unchanged.
- V3R/V2R P99: `-0.1184%`, lower/faster, unchanged.
- Tail: `MIXED`, unchanged.
- Contribution count: `2`.
- New scientific fact: `NONE`.
- Scientific claim change: `NONE`, except heading-level claim-boundary narrowing.
- T1/T2/T3: unchanged; source-marker occurrence counts equal the starting HEAD.

## 5. Citation and bibliography regression

- Citation keys: unchanged.
- Bibliography source: unchanged.
- Citation architecture: unchanged.
- Bibliography library: `27` entries, `26` cited/rendered, one governed unused entry.
- Unresolved citations: `0`.
- Static figure/table cross-references: PASS.

## 6. Build results

Full:

- Build: PASS.
- Pages: `11`, A4.
- SHA-256: `96658a6d856bee16530a5dd8b14a0f0530adeabca14b6574916818db68a9ac1b`.

Anonymous:

- Build: PASS.
- Pages: `12`, A4.
- SHA-256: `1c325cc32a2bdd9156882e41491e3bba37841dc3366c8900dfd0d560493ec781`.

The pre-existing one-page pagination difference remains compatible with PASS scientific-body parity.

## 7. Validation

- Full deterministic build: PASS.
- Anonymous deterministic build: PASS.
- Citation source validation: PASS.
- Final-reference and Full/Anonymous bibliography identity validation: PASS.
- Full manuscript structural/content validation: PASS.
- Anonymous identity scan: PASS.
- Full/Anonymous scientific-body parity: PASS.
- Journal-format mechanical validation: PASS.
- Figure/table cross-reference validation: PASS.
- ZIP/XML integrity: PASS.
- OMML/display equations: PASS; `8` display equations in each build.
- Frozen numerical token count comparison against starting HEAD: PASS.
- Tail-direction text comparison against starting HEAD: PASS.
- T1/T2/T3 marker-count comparison against starting HEAD: PASS.
- Contribution count check: PASS; exactly `2`.
- `git diff --check`: PASS before report creation and required again before commit.

## 8. Scope audit

- Manuscript body paragraphs changed: `NO`.
- Bibliography/citation files changed: `NO`.
- Title/abstract/keywords/conclusion changed: `NO`.
- Figures/tables changed: `NO`.
- Experiment, protocol or correctness boundary changed: `NO`.
- New contribution, variant or mechanism introduced: `NO`.

## 9. Recommendation

The narrow claim-boundary remediation is complete and ready for Main AI review. No push, merge or tag is authorized.
