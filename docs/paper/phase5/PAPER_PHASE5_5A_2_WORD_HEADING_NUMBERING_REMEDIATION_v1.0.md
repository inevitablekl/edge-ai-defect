# Paper Phase 5.5A-2 Word Heading Numbering Remediation v1.0

## 1. Verdict

`WORD_HEADING_NUMBERING_REMEDIATED`

The generated Full and Anonymous DOCX files now use the explicit section
numbers stored in Markdown as their only heading numbers. Microsoft Word
automatic list numbering is no longer effective on manuscript heading
paragraphs.

## 2. Starting state

- Branch: `main`.
- Starting HEAD: `b8cf8dd35b0adb1d1e8f16e00dfa40f3bdcc104c`.
- Subject: `docs(paper): prepare second supervisor review package`.
- Worktree: clean.
- Index: clean.

## 3. Root cause

The Markdown headings already contain explicit visible numbers. The active
reference DOCX also placed `w:numPr` on `HFUTHeading1/2/3` and
`Heading1/2/3`, linked through `numId=1` to a multilevel list. Pandoc retained
the explicit text and assigned the HFUT styles. The Full postprocessor then
kept the first, numbered reference definitions while deduplicating style IDs.
Microsoft Word consequently rendered both numbering systems.

## 4. Remediation architecture

The authoritative model is now:

```text
explicit number in Markdown heading text
-> Pandoc
-> unnumbered HFUT heading typography/style
-> DOCX
-> Microsoft Word
```

No manuscript heading text was changed. The reference builder no longer
passes `num_id` or `ilvl` when creating `HFUTHeading1/2/3` or the compatible
`Heading1/2/3` styles. Font, size, weight, spacing, alignment, keep-with-next,
keep-lines and outline-level properties remain unchanged.

The existing `numId=1` / `abstractNumId=0` definition remains in
`numbering.xml` as inert compatibility data. XML inspection confirms that no
style references `numId=1`. It was not repurposed or attached elsewhere.

The first-definition-wins algorithm in
`postprocess_full_manuscript_docx.py` was retained unchanged. With the
corrected reference definitions, both duplicate definitions are unnumbered,
so the algorithm no longer activates automatic heading numbering.

## 5. Reference DOCX

Path:

`docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`

| State | Size | SHA-256 |
|---|---:|---|
| Before | 8,212 bytes | `416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7` |
| After | 8,185 bytes | `483183514a2521592d50ecb7f7a2b2f24a88981c4abba3824aa487a8e054d7b9` |

The corrected reference was regenerated with the deterministic standard-library
OOXML builder. A post-build style-only numbering audit is now part of that
builder.

| Style | Before | After |
|---|---|---|
| `HFUTHeading1` | `numId=1`, `ilvl=0` | no direct/effective `numPr` |
| `HFUTHeading2` | `numId=1`, `ilvl=1` | no direct/effective `numPr` |
| `HFUTHeading3` | `numId=1`, `ilvl=2` | no direct/effective `numPr` |
| `Heading1` | `numId=1`, `ilvl=0` | no direct/effective `numPr` |
| `Heading2` | `numId=1`, `ilvl=1` | no direct/effective `numPr` |
| `Heading3` | `numId=1`, `ilvl=2` | no direct/effective `numPr` |

The generated style map was updated to record that visible heading numbers are
source text and the Word styles are typography-only.

## 6. Defensive XML validation

`scripts/paper/validate_word_heading_numbering_docx.py` now checks:

- exactly one definition for every governed HFUT and compatible Heading style;
- no direct `w:numPr` on those style definitions;
- no effective `w:numPr` through any `w:basedOn` ancestor;
- no direct `w:numPr` on governed heading paragraphs;
- no numbering-level `w:pStyle` link to a governed heading style;
- preservation of eleven representative explicitly numbered heading strings.

The validator was first run against the previous Full DOCX and correctly
failed every numbered heading style and all 21 affected manuscript headings.
It is invoked by the Full build, Anonymous build and Full `--check` path.

## 7. Corrected Full DOCX audit

Path: `docs/paper/manuscript/output/draft_full.docx`

- Size: 309,562 bytes.
- SHA-256: `3048d453840b37300bb169918cf1f61bbfe2f5290d2cf01a38043f789a17f4e8`.
- All 21 heading paragraphs: direct `numPr=NO`, effective `numPr=NO`.

| Heading text | Style | Direct numPr | Effective/inherited numPr |
|---|---|---|---|
| `0 引言` | `HFUTHeading1` | NO | NO |
| `1 系统对象与问题定义` | `HFUTHeading1` | NO | NO |
| `1.1 模型、数据集与边缘部署平台` | `HFUTHeading2` | NO | NO |
| `1.2 端到端推理数据路径与受控变量` | `HFUTHeading2` | NO | NO |
| `1.3 端到端执行概念分解与优化覆盖关系` | `HFUTHeading2` | NO | NO |
| `1.4 统一计时边界与研究问题` | `HFUTHeading2` | NO | NO |
| `2 数据路径优化方法` | `HFUTHeading1` | NO | NO |
| `2.1 CPU/OpenCV基线路径` | `HFUTHeading2` | NO | NO |
| `3 实验设计` | `HFUTHeading1` | NO | NO |
| `4 结果与分析` | `HFUTHeading1` | NO | NO |
| `5 结论` | `HFUTHeading1` | NO | NO |

## 8. Corrected Anonymous DOCX audit

Path: `docs/paper/manuscript/output/draft_anonymous.docx`

- Size: 308,839 bytes.
- SHA-256: `13122eba7ae9b68214d5e982f8ac181951e27bd9a54c3ef18827f67fd09d58be`.
- All 21 heading paragraphs: direct `numPr=NO`, effective `numPr=NO`.
- Explicit heading text: preserved.
- Word-numbering regression: `PASS`.
- Scientific-body parity: `PASS`.
- Anonymity scan: `PASS`.

## 9. Supervisor review package

Directory:

`/home/orin/paper-external-outputs/phase5_second_supervisor_review/`

### DOCX

- Path: `Jetson端工业缺陷检测的INT8推理数据路径优化_导师二审稿_20260811.docx`.
- Size: 309,562 bytes.
- SHA-256: `3048d453840b37300bb169918cf1f61bbfe2f5290d2cf01a38043f789a17f4e8`.
- Byte-identical to authoritative Full DOCX: `YES`.
- Previous SHA-256: `66ffa9a4eace1d45c59e81c21e53c6a3fab8492c335d8e7f3072c80d05a55631`.

### PDF

- Path: `Jetson端工业缺陷检测的INT8推理数据路径优化_导师二审稿_20260811.pdf`.
- Size: 782,845 bytes.
- Pages: 12.
- Page size: A4.
- Producer: LibreOffice 7.3.
- SHA-256: `5f764aa877672b0ac137d5f2afc44921db386a351019d1179d1a8c0eda277b68`.
- Previous SHA-256: `2d2183a76bfd09ba31a5fe30c28f44c32f77c9531cbe56aea1b7cafa81967236`.

The delivery directory contains exactly the intended DOCX and PDF.

## 10. Structural and scientific regression

- Full build: `PASS`.
- Anonymous build: `PASS`.
- Citation validation: `PASS`; 27 source entries, 26 cited, zero unresolved.
- Rendered bibliography validation: `PASS`; 26 rendered entries.
- Full/Anonymous bibliography identity: `PASS`.
- Scientific-body parity: `PASS`.
- Anonymity scan: `PASS`.
- Journal-format validation: `PASS`.
- Figures: 4.
- Tables: 3.
- Display equations: 8 in Full and Anonymous.
- DOCX ZIP/XML integrity: `PASS`.
- `git diff --check`: `PASS`.
- Manuscript sections byte-identical to starting HEAD: `YES`.
- `references.bib` byte-identical to starting HEAD: `YES`.
- Figure/table authority changed: `NO`.

Frozen scientific results:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean-latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail: `MIXED`.

Contribution count: `2`.

Scientific content changed: `NO`.

## 11. Repository changes

Tracked source/governance changes:

- `scripts/paper/build_hfut_reference_docx.py`;
- `scripts/paper/build_manuscript_docx.sh`;
- `scripts/paper/validate_word_heading_numbering_docx.py`;
- `scripts/paper/validate_journal_format_docx.py`;
- `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`;
- `docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv`;
- `docs/paper/phase5/PAPER_PHASE5_5A_2_WORD_HEADING_NUMBERING_REMEDIATION_v1.0.md`.

Regenerated manuscript artifacts:

- `docs/paper/manuscript/output/draft_full.docx`;
- `docs/paper/manuscript/output/draft_anonymous.docx`;
- their normal raw/intermediate build artifacts.

## 12. Remaining manual review

`MICROSOFT_WORD_GUI_VERIFICATION_REQUIRED`

The corrected supervisor DOCX must be opened in Microsoft Word Desktop and
checked to confirm that each heading appears once, including:

```text
0 引言
1 系统对象与问题定义
1.1 模型、数据集与边缘部署平台
...
5 结论
```

PDF correctness is not a substitute for this Word-specific manual check.

## 13. Open risks

`NONE`, subject to the required Microsoft Word GUI verification.
