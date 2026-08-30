# Paper Phase 7.3-J Length Compression Validation v1.0

## 1. Verdict

`PHASE_7_3_LENGTH_COMPRESSION_READY_FOR_MANUAL_APPLICATION`

The repository Markdown body was compressed by **886.0 CJK-weighted
equivalents**, within the requested 700–900 target. This is an engineering
estimate only; the manually formatted HFUT Word manuscript remains the page
count and pagination authority.

## 2. Baseline and scope

- Branch: `main`.
- Baseline commit: `470e692c0ed1df3b16edf9e3b5b9fa82b33a741e`.
- Baseline tracked worktree/index: clean.
- Preserved pre-existing untracked file:
  `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`.
- Abstract status: `ABSTRACT_UNCHANGED`.
- Abstract SHA-256 before/after:
  `214cec53c91bfc8ab2a89470532d3a66e2f2cb6cf088ec62c9f70a2e31d66a93`.
- Reference database changed: NO.
- Figure/table assets changed: NO.
- Production scripts changed: NO.
- Manually formatted HFUT Word file changed or regenerated: NO.

## 3. Files changed

Manuscript sources:

- `docs/paper/manuscript/sections/01_introduction.md`
- `docs/paper/manuscript/sections/02_problem_definition.md`
- `docs/paper/manuscript/sections/03_method.md`
- `docs/paper/manuscript/sections/04_experiment.md`
- `docs/paper/manuscript/sections/05_results.md`
- `docs/paper/manuscript/sections/06_conclusion.md`

Phase 7.3 reports:

- `docs/paper/phase7/PAPER_PHASE7_3_MANUAL_LENGTH_COMPRESSION_CHANGELOG_v1.0.md`
- `docs/paper/phase7/PAPER_PHASE7_3_LENGTH_COMPRESSION_VALIDATION_v1.0.md`

## 4. Counting method

The primary integer count is the number of non-whitespace Unicode source
characters after removing the unchanged `MANUSCRIPT_SECTION` HTML comments.
It includes unchanged headings, equations, captions and table text, so the
before/after body totals are reproducible directly from sections 01–06.

The CJK-weighted estimate uses the same text but assigns weight 1 to each
non-ASCII character and 0.5 to each ASCII character. This approximates Chinese
full-width-character equivalents; it does not model Word fonts, line breaks,
columns, MathType objects, Visio/Origin objects, or pagination rules.

## 5. Before/after metrics

| Section | Before chars | After chars | Net reduction | Reduction | Before CJK-eq | After CJK-eq | CJK-eq saved |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01 Introduction | 2264 | 2089 | 175 | 7.73% | 1801.0 | 1631.0 | 170.0 |
| 02 Problem definition | 2455 | 2216 | 239 | 9.74% | 1911.0 | 1723.0 | 188.0 |
| 03 Method | 1308 | 1144 | 164 | 12.54% | 1013.0 | 863.0 | 150.0 |
| 04 Experiment | 1139 | 1059 | 80 | 7.02% | 851.5 | 777.5 | 74.0 |
| 05 Results | 2109 | 1866 | 243 | 11.52% | 1737.0 | 1518.5 | 218.5 |
| 06 Conclusion | 536 | 445 | 91 | 16.98% | 460.5 | 375.0 | 85.5 |
| **Whole body 01–06** | **9811** | **8819** | **992** | **10.11%** | **7774.0** | **6888.0** | **886.0** |

The 16 exact replacement units contain 3954 before characters and 2962 after
characters, also yielding the same 992-character net reduction. Tier savings:

| Tier | Source characters saved | CJK-weighted saved | Cumulative CJK-weighted |
|---|---:|---:|---:|
| Tier 1 | 709 | 623.5 | 623.5 |
| Tier 2 | 192 | 177.0 | 800.5 |
| Tier 3 | 91 | 85.5 | 886.0 |

## 6. Citation and reference validation

- Citation occurrence sequence before/after: PASS.
- Citation key set before/after: PASS (`22` cited keys).
- Citation first-occurrence order before/after: PASS.
- Unresolved citation keys: `0`.
- `python3 scripts/paper/validate_citations.py`: PASS.
- Full rendered reference validation: PASS (`22` rendered references).
- Anonymous rendered reference validation: PASS.
- Full/Anonymous bibliography identity: PASS.
- Reference database modification: NONE.

## 7. Formula, table, figure, and structure freeze

- Equations (1)–(3): byte-for-byte extracted-block comparison PASS; count `3`.
- Equation numbering in Full/Anonymous builds: PASS (`E1=（1）`, `E2=（2）`, `E3=（3）`).
- Tables 1–3 captions and Markdown table blocks: exact comparison PASS; count `3`.
- Figure 1–3 captions: exact comparison PASS; count `3`.
- Figure/table cross-references: PASS.
- Section heading sequence and numbering: exact comparison PASS; `21` headings.
- Figure 1 governed early callout: PASS and retained verbatim.
- Two contributions: PASS; contribution paragraph unchanged.
- RQ1 and RQ2: PASS.
- Abstract: byte-identical PASS.

## 8. Scientific non-regression

`PHASE73_SCIENTIFIC_NONREGRESSION=PASS`

The automated Phase 7.3 comparison confirmed continued presence and meaning
of the frozen detector, input, Engine precision/I/O, workload, three paths,
descriptor, representations, staging policies, sequential topology, nominal
payloads, process/sample protocol, mean results, percentage comparisons and
opposite-direction tail results.

The following boundaries remain explicit:

- `40.96×` is a nominal structural copy-payload contrast, not measured
  traffic, bandwidth, H2D time, or transfer acceleration.
- `2.24×` belongs to the complete coupled path intervention and is not
  decomposed into GPU preprocessing, H2D, CUDA kernel, or representation
  contributions.
- V2R→V3R changes only `M` from pageable to pinned; no universal pinned-memory
  benefit is claimed.
- P95 `+0.15%` and P99 `−0.12%` have opposite directions; no consistent tail
  improvement or “pinned improves stability” conclusion is made.
- Results remain descriptive only; no statistical significance is claimed.
- Limitations still cover a single Jetson platform, single detector/Engine,
  single dataset/workload, offline replay, single-frame sequential topology,
  no continuous telemetry/power/energy, no stage timing, no bus/DRAM
  measurement, five-process descriptive interpretation, and no
  cross-platform/model generalization.

The historical `validate_manuscript_sources.py` skeleton gate and the Phase
7.1 scientific-freeze gate are not applicable to this explicitly authorized
manuscript-edit phase: the former expects pre-authoring skeleton files and the
latter deliberately rejects any source edit. They were not treated as active
Phase 7.3 gates. The current governed Full/Anonymous build and the dedicated
before/after Phase 7.3 freeze comparison are the relevant regression checks.

## 9. Build validation

Full manuscript:

- Command: `bash scripts/paper/build_manuscript_docx.sh --build-full`.
- Result: PASS.
- Structural format validation: PASS.
- Citation/reference validation: PASS.
- Phase 5.9C integration: PASS (`3` figures, `3` tables, `3` equations, `2`
  RQs, `2` contributions, `22` references).
- Output regression artifact SHA-256:
  `99ad62736a5526625e707dac8c95d7d7fff9b2bc0c5d511f65891e57de7615fa`.

Anonymous manuscript:

- Command: `bash scripts/paper/build_manuscript_docx.sh --build-anonymous`.
- Result: PASS.
- Anonymous identity scan: PASS.
- Full/Anonymous scientific-body parity: PASS.
- Full/Anonymous bibliography parity: PASS.
- Structural format validation: PASS.
- Output regression artifact SHA-256:
  `c3d6aadb819b57ae86857284feb19261292d451820c7d6c243fd77af320543a6`.

These automated DOCX outputs are regression artifacts only. Their pagination
is not authority for the user's manually formatted HFUT Word manuscript, and
the user's manual final Word file was not overwritten.

## 10. Narrative continuity judgment

PASS. The final read from Introduction → problem definition → method →
experiment → results → conclusion remains one continuous argument:

1. model/Engine fixation leaves an input-path evaluation gap;
2. \(P=(R,F,M,E)\) defines the controlled structural object;
3. V0/V2R/V3R instantiate hierarchical interventions;
4. the protocol admits performance comparison only after correctness;
5. results separate coupled path response, M-only mean response, and tail
   response;
6. the conclusion retains quantitative results and bounded generalization.

No section has been reduced to isolated notes, and no unique evidence was
deleted.

## 11. Remaining manual action

`OPEN THE CHANGELOG AND MANUALLY APPLY TIER-1 EDITS TO THE HFUT WORD MANUSCRIPT, THEN CHECK PAGINATION BEFORE APPLYING TIER 2.`
