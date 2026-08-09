# Paper Phase 5.0A-2 Equation Layout Remediation Report

## 1. Verdict

`EQUATION_LAYOUT_REMEDIATION_COMPLETE`

## 2. Starting State

- HEAD: `92daafb7cc39b036fa624d39effa87866a87befd`
- Branch: `main`
- Worktree/index: clean at start
- Phase 5.0A-2 audit verdict: `D. DISPLAY_AND_INLINE_LAYOUT_REGRESSION`

## 3. Root Cause

The reference style definition was already correct, but the formal manuscript
pipeline did not propagate the Phase 2.5 paragraph-level OMML normalization.
The Lua filter assigned all ordinary `Para` blocks to `HFUTBody`, including
display equations. The current DOCX postprocessor had no display-OMML or
inline-OMML rule.

## 4. Files Modified

- `scripts/paper/postprocess_full_manuscript_docx.py`
- `docs/paper/phase5/PAPER_PHASE5_EQUATION_LAYOUT_REMEDIATION_v1.0.md`

No Markdown source, reference DOCX, figures, tables, or Phase 4 governance
files were changed.

## 5. Remediation

The postprocessor now inspects direct manuscript body paragraphs semantically:

- Paragraphs containing `m:oMathPara` use the existing `HFUTEquation` style.
- `HFUTBody` paragraphs containing inline `m:oMath`, without display math,
  receive direct `before=0`, `after=0`, `line=360`, `lineRule=atLeast`.
- Ordinary body paragraphs remain unchanged and inherit `HFUTBody`.

The existing named style was reused; no new Word style or mathematical content
was introduced.

## 6. Display Equation Matrix

| ID | Semantic content | Full p | Anonymous p | pStyle | Effective layout | Result |
|---|---|---:|---:|---|---|---|
| EQ-001 | `f_i=N/T_i` | 74 | 68 | `HFUTEquation` | `480/atLeast`, `80/80`, centered, keepLines | PASS |
| EQ-002 | `bar f=(1/5) sum f_i` | 77 | 71 | `HFUTEquation` | `480/atLeast`, `80/80`, centered, keepLines | PASS |
| EQ-003 | sample standard deviation `s_f` | 79 | 73 | `HFUTEquation` | `480/atLeast`, `80/80`, centered, keepLines | PASS |
| EQ-004 | Type-7 intermediate definitions | 82 | 76 | `HFUTEquation` | `480/atLeast`, `80/80`, centered, keepLines | PASS |
| EQ-005 | `Q_p` interpolation expression | 84 | 78 | `HFUTEquation` | `480/atLeast`, `80/80`, centered, keepLines | PASS |

All five paragraphs contain `m:oMathPara`; display formula text and OMML
structure remain unchanged from Phase 5.0A-1.

## 7. Inline Formula Paragraph Matrix

| Context | Full p | Anonymous p | pStyle | Direct spacing | Result |
|---|---:|---:|---|---|---|
| Variable `i` in FPS context | 73 | 67 | `HFUTBody` | `360/atLeast`, `0/0` | PASS |
| EQ-006 `N=1080` and `T_i` | 75 | 69 | `HFUTBody` | `360/atLeast`, `0/0` | PASS |
| EQ-007 `n=5400`, `x_(1)...x_(n)`, `p` | 81 | 75 | `HFUTBody` | `360/atLeast`, `0/0` | PASS |
| EQ-008 `p=0.95` and EQ-009 `p=0.99` | 85 | 79 | `HFUTBody` | `360/atLeast`, `0/0` | PASS |

Multiple inline formulas in one paragraph were counted as one affected
paragraph.

## 8. Ordinary Body Negative Controls

Representative paragraphs before, between, and after the equation sequence
remain `HFUTBody` with no direct spacing and effective `320/exact`, `0/0`.
Examples include Full paragraphs 67, 76, 78, 80, 83, and 86; the corresponding
Anonymous paragraphs show the same contract with front-matter offset only.

The remediation did not globally increase manuscript body spacing.

## 9. Full DOCX

- Build: PASS — `scripts/paper/build_manuscript_docx.sh --build-full`
- OMML: 5 display equations, 4 formal inline equations, 13 `m:oMath`
- Equation layout: PASS
- SHA256: `2dfc5382f136ea16661805cefd87b8f9a89ef217343d9f7985414898634d787e`
- Render: 9 pages, A4
- Git state: generated artifact ignored/local

## 10. Anonymous DOCX

- Build: PASS — `scripts/paper/build_manuscript_docx.sh --build-anonymous`
- OMML: 5 display equations, 4 formal inline equations, 13 `m:oMath`
- Equation layout: PASS
- SHA256: `8fc8e96464b790c34f2a58d1e2c324296f07f02a44189b97f5d85a0a13283485`
- Render: 9 pages, A4
- Git state: generated artifact ignored/local

## 11. Full / Anonymous Parity

PASS. Display and inline formula content, OMML representation, paragraph
contracts, and ordinary-body controls are identical. Differences are limited
to authorized identity/anonymity content and paragraph indexes.

## 12. Document Validation

Passed:

- Full and Anonymous production builds.
- `build_manuscript_docx.sh --check`.
- Existing Full/Anonymous custom validators.
- Citation and cross-reference validation.
- Journal-format mechanical audit; reference DOCX SHA256 unchanged.
- Anonymous identity and scientific-body parity checks.
- ZIP integrity and XML parsing.
- LibreOffice render check: both outputs are 9-page A4 documents.
- `git diff --check`.

## 13. Scientific Freeze Check

- Frozen central results changed: NO
- Contribution count: 2
- Metric semantics changed: NO
- Comparison object changed: NO
- Excluded evidence restored: NO
- Scientific impact: NONE

## 14. Governance Asset

Created: `docs/paper/phase5/PAPER_PHASE5_EQUATION_LAYOUT_REMEDIATION_v1.0.md`

## 15. Git State

- Commit: created after validation
- Subject: `docs(paper): restore equation layout contract`
- Worktree: expected clean after commit
- Index: expected clean after commit
- Pushed: NO

## 16. Remaining Manual Requirement

Microsoft Word visual check remains required before MathType conversion.

MathType conversion has NOT been performed.

## 17. Recommended Next Executor

`MAIN_AI`
