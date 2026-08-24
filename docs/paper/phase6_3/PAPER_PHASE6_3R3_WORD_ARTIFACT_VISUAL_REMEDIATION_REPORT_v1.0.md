# Paper Phase 6.3R3 Word Artifact Visual Remediation Report v1.0

## 1. Verdict

`PHASE_6_3_WORD_VISUAL_REMEDIATION_IMPLEMENTED`

```text
FMT-F03 = IMPLEMENTED_PENDING_WORD_REVIEW
FMT-F04 = IMPLEMENTED_PENDING_WORD_REVIEW
FMT-F05 = IMPLEMENTED_PENDING_WORD_REVIEW
FMT-F06 = CLOSED
SCIENTIFIC_NONREGRESSION = PASS
STRUCTURAL_FORMAT_VALIDATION = PASS
WORD_ARTIFACT_VISUAL_REVIEW_REQUIRED = YES
```

This is not `WORD_VISUAL_PASS` or `HFUT_SUBMISSION_READY`. Only a new PDF exported by Microsoft Word can close FMT-F03 through FMT-F05.

## 2. Baseline

The mandated pre-edit reconciliation passed on 2026-08-24:

- branch: `main`;
- `HEAD`: `7696e476ebc9adbb4a2538fa92e8f8349e1ad14e`;
- `origin/main`: `7696e476ebc9adbb4a2538fa92e8f8349e1ad14e`;
- worktree and index: clean;
- baseline commit: `paper: close Phase 6.3 reference metadata findings`.

No reset, clean, rebase, merge, tag, push, or unknown-work overwrite occurred.

## 3. FMT-F03 diagnosis

| Finding | Observed Word symptom | Current source/OOXML mechanism | Causal? | Selected repair |
|---|---|---|---|---|
| FMT-F03 | Page 3 left-column continuation plus approximately 9–10 cm abnormal whitespace | Figure 1 caption carried a one-column `w:sectPr` with `w:type=nextPage` at the original inline callout location | Yes | Move only the drawing/caption block to the end of Section 1; use coherent continuous 2-column → 1-column → 2-column sections; put `pageBreakBefore` on the drawing and keep it with the caption |
| FMT-F04 | Severe Word spacing expansion in narrow-column references | The postprocessor changed the template/raw-DOCX reference styles from `jc=left` to `jc=both` | Yes | Restore deterministic left alignment while preserving fonts, size, exact line spacing, and hanging indent |
| FMT-F05 | Accented surname appeared visually separated | Source contains one normal Unicode `Sánchez-González` text node/run; no literal space or surname-specific font override exists | Symptom of FMT-F04 pending Word review | Preserve the source/run and remove the justification expansion mechanism |
| FMT-F06 | Validators required the two mechanisms that caused the artifacts | Phase 6.3 and non-regression validators required `nextPage`; Phase 6.3 and reference validators required `jc=both` | Yes | Validate format invariants and the selected stable style contract instead |

The actual template, raw Pandoc DOCX, final pre-remediation DOCX, reference evidence, hanging indents, run segmentation, and Word compatibility mode 15 were inspected before editing.

## 4. FMT-F03 selected repair

The production postprocessor now:

1. confirms a Figure 1 textual callout precedes the drawing;
2. relocates only the Figure 1 drawing/caption block immediately before `2 受控输入数据路径重构`, retaining it at the end of Section 1;
3. closes the preceding body as a continuous two-column section;
4. uses a continuous one-column Figure 1 section;
5. applies `pageBreakBefore` to the drawing paragraph and `keepNext` between drawing and caption;
6. resumes the final continuous two-column body immediately below the caption.

Scientific prose order and meaning are unchanged. The Figure 1 first callout remains in Section 1.3 before the relocated figure object.

## 5. Rejected FMT-F03 alternatives

- Keeping `nextPage` at the original inline location was rejected because actual Word evidence proves its pagination side effect is unacceptable.
- Changing only `nextPage` to `continuous` was tested mechanically. It balanced both columns but still left a large blank lower half on Page 3, so it did not fully satisfy the whitespace outcome.
- Shrinking Figure 1 was rejected because its governed full width is closed.
- Allowing a mid-page one-column figure was rejected because page-top placement and no-sandwich layout are required.
- Rewriting or compressing Section 1 prose was rejected as outside scope.

## 6. FMT-F04 diagnosis

The repository template and raw Pandoc DOCX both specify the same reference contract:

```text
alignment = left
Chinese font = 宋体
Latin font = Times New Roman
size = 7.5 pt
line spacing = exact 14 pt
left indent = 360 twips
hanging indent = 360 twips
```

The final pre-remediation postprocessor changed only the alignment to `both`. Reference paragraphs contain ordinary single spaces/tabs and no source-level expanded spacing. Word compatibility settings contain only compatibility mode 15; no hyphenation or line-breaking override explains the symptom. The forced full justification is therefore the causal mechanism.

## 7. Reference-alignment authority reconciliation

The real requirement is clean journal-grade alignment without extreme stretching. Repository HFUT evidence records the sample reference paragraphs without an explicit justification requirement, and the project-derived template deliberately maps both `HFUTReferenceEntry` and Pandoc `Bibliography` to left alignment. Restoring `left` therefore follows the underlying format evidence while retaining the supervisor-governed typography, line spacing, and hanging layout.

## 8. FMT-F04 selected repair

Both reference styles now use a production-wide `jc=left` rule. The repair does not alter BibTeX, CSL output, literal spaces, individual references, line widths, URLs, or metadata. It is a deterministic style-level rule for all references.

## 9. FMT-F05 result

Generated OOXML validation confirms:

- the exact source spelling `Sánchez-González` is unchanged;
- the surname is contiguous in one `w:t` node;
- no literal space was inserted within it;
- no direct ASCII, high-ANSI, or East Asian font override conflicts with the governed Times New Roman/Songti style.

The mechanical render shows contiguous accented glyphs. Formal closure remains pending the next Microsoft Word render.

## 10. FMT-F06 validator redesign

The validators no longer require `("1", "nextPage")` or `jc == "both"`.

They now check:

- Figure 1 identity, 16 cm full width, drawing/caption adjacency, prior callout, end-of-Section-1 context, continuous section coherence, page-top paragraph break, and keep-with-caption;
- no Figure 2/3 full-width section regression;
- reference Songti/Times fonts, 7.5 pt size, exact 14 pt line spacing, 360-twip hanging indent, and stable left alignment;
- exactly 22 sequential references, the accepted Phase 6.3R1 rendered-reference content hash, unchanged `et al./等` behavior, and contiguous accented surname OOXML;
- Full/Anonymous figure, equation, reference-style, reference-content, and placement parity.

Validator output explicitly separates:

```text
STRUCTURAL_FORMAT_VALIDATION = PASS
MICROSOFT_WORD_VISUAL_QA = PENDING
WORD_ARTIFACT_VISUAL_REVIEW_REQUIRED = YES
```

## 11. Changed files

- `scripts/paper/postprocess_full_manuscript_docx.py` — Figure 1 placement/section rule and reference style production rule.
- `scripts/paper/validate_phase63_format.py` — Phase 6.3R3 invariant validation and explicit Word-QA boundary.
- `scripts/paper/validate_final_references.py` — stable narrow-column alignment validation.
- `scripts/paper/validate_phase61_nonregression.py` — Figure 1 structural non-regression without the obsolete `nextPage` contract.
- `docs/paper/phase6_3/phase6_3_scientific_nonregression.json` — regenerated PASS evidence for the final artifacts.
- `docs/paper/phase6_3/PAPER_PHASE6_3R3_WORD_ARTIFACT_VISUAL_REMEDIATION_REPORT_v1.0.md` — this report.

No manuscript Markdown, BibTeX, CSL, figure generator/data, table source, equation manifest, experimental file, or production C++ file changed.

## 12. Structural validation

`PASS` for Full and Anonymous:

- valid DOCX ZIP/OOXML;
- A4 and final two-column body;
- three figures, three native Word tables, and three display equations;
- Figure 1 width `5,759,999` EMU (nominal 16 cm), callout before figure, caption immediately below drawing, end-of-Section-1 placement, and coherent section transitions;
- Figure 2/3 single-column behavior unchanged;
- equation numbering `（1）`–`（3）` unchanged;
- 22 sequential references and Full/Anonymous reference identity;
- explicit `STRUCTURAL_FORMAT_VALIDATION=PASS` and `MICROSOFT_WORD_VISUAL_QA=PENDING`.

## 13. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS`.

- manuscript source files changed: `0`;
- frozen experiment source SHA-256: `20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa`;
- Figure 2/3 frozen data hashes: `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` and `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`;
- three equations, RQ1/RQ2, three correctness rows, all frozen metrics, and all 18 legitimate boundary/negation matches passed;
- Figure 1 semantic identity is unchanged;
- 22-reference rendered content SHA-256 remains `cc271cc81cc89342ef7652d8a51f81f25c431617d1da6b235faa72cca0c5ccef`;
- conference metadata, Lema metadata, DOI policy, and `et al./等` behavior are unchanged.

## 14. Full build

Authoritative command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-full
```

Result: `PASS` across heading, citation, final-reference, Full-DOCX, Phase 5.9c integration, and Phase 6.3R3 structural validation.

## 15. Anonymous build

Authoritative command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result: `PASS` across heading, citation, final-reference, anonymity, Full/Anonymous parity, Phase 5.9c integration, and Phase 6.3R3 structural validation.

## 16. Mechanical-render observations

LibreOffice 7.3 produced two eight-page A4 PDFs for gross regression inspection only:

- Full mechanical PDF: 708,116 bytes; SHA-256 `2322cbe6a57cdbf4310889451600cff7cced08dd4083c0b7e3667985c4c678da`;
- Anonymous mechanical PDF: 696,078 bytes; SHA-256 `0999067b292720ac06cfcdcd492a7af1d90b7d11ca24a135f39b5641866c347c`.

Observed mechanically: Page 3 uses both columns naturally without the prior large blank lower region; Figure 1 is full-width at Page 4 top with no body above it and two-column text below; references have no extreme expansion; `Sánchez-González` is contiguous; no gross figure/table/equation regression was seen.

These observations are not Microsoft Word pagination or typography proof. Mechanical page count is not an acceptance criterion.

## 17. Full DOCX path and SHA-256

- path: `docs/paper/manuscript/output/draft_full.docx`
- SHA-256: `85a2cb1072dd638256bb3799f57ee552c8da659b93f920944c39c649a318c221`

## 18. Anonymous DOCX SHA-256

- path: `docs/paper/manuscript/output/draft_anonymous.docx`
- SHA-256: `3813716ba2e3b913375b43a3ac575d17489b5c9a43bdd0739afc2517a95fb236`

## 19. Items requiring actual Microsoft Word review

Inspect the new Full DOCX and Word-exported PDF specifically:

1. Previous Page 3 / Figure 1 preceding page: both columns used naturally and no approximately 10 cm artificial whitespace.
2. Figure 1 page: page top, full width, no text above, caption below, no clipping, no sandwich regression, and two-column body below.
3. References `[6]`, `[7]`, `[10]`, `[11]`, `[12]`, `[15]`, `[18]`, `[19]`, and `[22]`: no extreme word/character stretching.
4. `Sánchez-González`: accent characters visually contiguous.
5. All other figures, tables, and equations: no regression.

## 20. Deferred Visio/Origin/MathType status

- Figure 1 Visio editable submission object: `OPEN`.
- Figure 2/3 Origin editable submission objects: `OPEN`.
- MathType conversion: `DEFERRED_FINAL_MATHTYPE`.
- Word Desktop QA, Anonymous QA, Document Inspector, and final submission adaptation: `OPEN`.

## 21. Git diff

Final pre-commit scope audit: 6 files changed, 483 insertions, and 42 deletions.

The diff contains only DOCX layout/reference production rules, validators, regenerated non-regression evidence, and this report. Cached diff is empty before the authorized commit; no unexpected file category is present.

## 22. Commit

Exactly one local commit is authorized with message:

```text
paper: remediate Phase 6.3 Word visual format findings
```

The definitive SHA is reported in the external handoff after commit creation to avoid an amend cycle. No push, tag, merge, rebase, reset, or clean is performed.

## 23. Exact next action

The user should manually push the local commit, then:

```text
take docs/paper/manuscript/output/draft_full.docx
→ open it in Microsoft Word
→ export a new PDF
→ submit both the exact DOCX and Word-generated PDF
→ request independent artifact-level format re-review against Section 19
```

Stop after handoff. Do not make further format changes before that review.
