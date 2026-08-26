# Phase 7.1R3 manual submission handoff report

## 1. Verdict

`PHASE_7_1R3_CANDIDATE_B_AUTOMATION_FROZEN_MANUAL_HANDOFF_READY`

## 2. Baseline

The controlled baseline was `main` and `origin/main` at
`2775ca5da93b295041d7949c03906482385adaf0` (`paper: close HFUT heading
fidelity and regenerate Word candidates`). The worktree and index were clean
before this freeze; no baseline reconciliation was required.

## 3. A/B Word visual comparison

The user inspected the bounded R2 candidates in Microsoft Word 2019. Candidate
A retained an unacceptable large Page-6 blank region. Candidate B used Page 6
substantially better and left only a small ordinary page-bottom residue.

## 4. Candidate-B selection

Candidate B is selected by the user. Its Figure-3 related-body offset is `1`.
The R2 candidate matrix establishes that it differs from A only in the logical
Figure-3 float anchor, not scientific text, image payload, caption, table
geometry, wrap attributes, or scientific data.

## 5. Production identity verification

The production postprocessor already fixes
`FIGURE3_PRODUCTION_RELATED_BODY_OFFSET = 1`; no production-code change was
needed. Authoritative Full and Anonymous builds reproduced the selected
semantics without candidate tooling. In the rebuilt Full DOCX, the first
Figure-3 callout is child `83`, the floating table is child `85`, and exactly
one non-empty `HFUTBody` paragraph intervenes. Its `word/document.xml` and
media payloads equal the R2 B artifact; only regenerated core metadata changes
the package SHA256.

## 6. Page-6 closure

`PAGE6_LARGE_ARTIFICIAL_BLANK = CLOSED_BY_MICROSOFT_WORD_REVIEW`.

## 7. Accepted residual whitespace

`MINOR_PAGE_BOTTOM_RESIDUE = ACCEPTED_NORMAL_WORD_PAGINATION_RESIDUE`.
It is normal Word pagination residue; equal column bottom coordinates are not
required.

## 8. Pagination rules now frozen

No further automated pagination micro-tuning is authorized. In particular, do
not change Figure-3 offset, Figure-1/2 anchors, `tblpY`, wrap distances, figure
sizes, paragraph text, line spacing, widow/orphan controls, or heading
keep-rules.

## 9. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS`; `MANUSCRIPT_MARKDOWN_CHANGED = 0`.
No scientific manuscript content was changed in this work unit.

## 10. Full build

`bash scripts/paper/build_manuscript_docx.sh --build-full` passed, including
source/structural format, heading, reference, citation, equation, and
integration validation.

## 11. Anonymous build

`bash scripts/paper/build_manuscript_docx.sh --build-anonymous` passed,
including anonymity validation and Full/Anonymous bibliography and scientific
body parity.

## 12. Full DOCX SHA256

`7bae4c088f4410015ea50e6537ab88cbfcba3a72bde52b29cfbcbfe4c914f79e`

## 13. Anonymous DOCX SHA256

`2b047540076fe6cacefa2a540fca35ffef62577f88c6af3ae37e67c3b69aa3e0`

## 14. Manual submission workflow

1. Copy `draft_full.docx` to `HFUT_submission_manual_v1.docx` (or an
   equivalent separately named manual asset).
2. Use the official HFUT formatting DOC and Word Format Painter/manual Word
   formatting for remaining detailed visual work.
3. Replace Figure 1 with its final editable Visio object.
4. Replace Figures 2–3 with their final editable Origin objects.
5. Convert E1, E2, and E3 with MathType.
6. Complete Word Desktop visual QA.
7. Adapt and QA the anonymous manuscript.
8. Run Document Inspector.
9. Validate the submission portal.

## 15. Assets still requiring conversion

`F1_VISIO = OPEN`; `F2_ORIGIN = OPEN`; `F3_ORIGIN = OPEN`; `E1_MATHTYPE =
OPEN`; `E2_MATHTYPE = OPEN`; `E3_MATHTYPE = OPEN`.

## 16. Git status

The baseline worktree and index were clean. This freeze changes only this
report and the freeze manifest; generated DOCX outputs are not tracked.

## 17. Commit

`AUTO_WORD_BASELINE_COMMIT` is the commit containing this report and manifest.
The scientific baseline is `2775ca5da93b295041d7949c03906482385adaf0`.

## 18. Exact next action

Copy `docs/paper/manuscript/output/draft_full.docx` to a separate manual
submission filename and begin the official-HFUT Word Desktop formatting pass.

## Format-Painter safety note

Do not broadly format-paint entire pages or figure containers. High-risk
objects are floating figure tables, section boundaries, the Figure-1 area,
Figure-2/3 float containers, equation paragraphs, tables, and column
transitions. Apply Format Painter primarily to semantic text classes: front
matter, abstract, keywords, classification line, headings, body paragraphs,
figure captions, table captions, reference heading, reference entries, and
author biography. This limits pagination regressions.

`HFUT_SUBMISSION_READY = NO`.
