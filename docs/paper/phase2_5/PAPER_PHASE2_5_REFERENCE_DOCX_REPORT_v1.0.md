# Paper Phase 2.5 Step 4 Reference DOCX Result

## 1. Verdict

`STEP_4_COMPLETE_WITH_POC_ITEMS`

The candidate reference DOCX, deterministic builder, inspector, Style Map,
design record, and external style specimen were generated and inspected.
Automatic numbering, Pandoc output, MathType, column-section semantics, table
continuation, and Microsoft Word acceptance remain explicit POC/manual items.

## 2. Repository State

- Required branch: `main`.
- Starting HEAD: `6f250edcd424179dc301d3099801e86e377dd2f4`.
- Starting worktree/index: clean; starting `git diff --check`: pass.
- Phase 2 tag type: `tag`.
- Phase 2 peeled commit: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`.
- No reset, restore, checkout, stash, clean, merge, rebase, push, or tag
  modification was performed.

The final commit will contain only the six authorized Step 4 files listed in
Section 18.

## 3. Dependencies

| Dependency | Observed result | Use |
|---|---|---|
| Pandoc | not installed | no Pandoc generation in Step 4 |
| `python-docx` | not installed | no third-party DOCX generation |
| Python | 3.10.12 | deterministic OOXML build and inspection |
| LibreOffice | 7.3.7.2 | headless PDF render/open compatibility check only |
| unzip | Info-ZIP 6.00 | ZIP validation |
| zip | Zip 3.0 | available; builder uses Python `zipfile` |

No package installation command was run.

## 4. Template Identity

The DOCX core/custom properties contain:

```text
DERIVED_REFERENCE_DOCX_CANDIDATE
NOT_OFFICIAL_JOURNAL_TEMPLATE
NOT_FINAL_SUBMISSION_FILE
PENDING_PANDOC_POC
PENDING_MICROSOFT_WORD_REVIEW
```

No official source DOCX was copied, overwritten, or used as a template. No
real author, unit, funding, contact, received date, or revised date was added.

## 5. Base Document Strategy

Because Pandoc and `python-docx` were absent, the builder creates a fixed
minimal OOXML baseline with the Python standard library. LibreOffice was used
after generation to convert both the canonical candidate and external
specimen to PDF without GUI interaction; the conversion succeeded.

## 6. Page and Section Design

The candidate contains A4 portrait geometry, 2.4/2.0/2.3/2.3 cm margins,
zero gutter, `zh-CN`/`en-US` language settings, no formal header, a PAGE-only
footer, and a 0.748 cm column-gap candidate. The default section is single
column for front matter. Body double columns are a documented target whose
semantic section boundary must be applied by the later builder, OOXML step,
or Word; the source document's multiple section breaks were not copied.

## 7. Semantic Style System

All 28 required HFUT semantic styles are present, along with `Normal`, `Body
Text`, `Title`, `Subtitle`, `Author`, `Abstract`, `Heading 1`–`Heading 3`,
`Caption`, `Table`, and `Bibliography` mappings. The Style Map has 42 unique
style IDs/rows, including the external specimen notice and three-line table
style.

The main body candidate is 10.5 pt Chinese Songti/Latin Times New Roman,
justified, with 16 pt exact line spacing and 200 twips first-line indent. The
heading, caption, table, and reference candidates follow the Step 2/Step 3
evidence and are marked individually as confirmed or derived/pending in the
CSV rather than promoted to unconditional official rules.

## 8. Heading and Numbering Design

The candidate uses a separate `0` introduction numbering definition and a
multilevel definition for `1`, `1.1`, and `1.1.1`. This is Option A from the
design report. It is an OOXML candidate only; Word update/restart behavior and
Pandoc heading mapping require the later POC.

## 9. Formula Handling Boundary

`HFUTEquation` exists as a centered paragraph style. No MathType formula,
OMML formula, equation number, or space-aligned equation was created. MathType
creation/editability and equation layout are not claimed.

## 10. Figure and Caption Styles

Separate 7.5 pt centered Heiti candidates exist for figure and table captions.
No figure, image, Visio, Origin, DPI, or image-format claim was embedded.

## 11. Table and Three-Line Style

`HFUTThreeLineTable` and `HFUTTableContent` are present. Border candidates are
top 1 pt, secondary horizontal 0.5 pt, bottom 1 pt, and no internal vertical
lines. Cell margins are 108 twips left/right and zero top/bottom. The external
specimen includes one small virtual table. Merged cells, continuation tables,
and Word-specific border rendering remain pending.

## 12. Reference Style

`HFUTReferenceEntry` and `Bibliography` use 7.5 pt Songti/Times New Roman and
14 pt exact line spacing. The selected 360-twip hanging-indent candidate is
documented as `PENDING_POC`, chosen to cover one-, two-, and three-digit
reference labels without copying the source's inconsistent 227–396 twips
values as if they were one rule.

## 13. Page Number Field

The footer uses a `PAGE` field and `updateFields=true`; it does not write a
fixed page-number paragraph. LibreOffice rendered the test page number as
`1`, confirming the field is usable in the headless conversion path. Microsoft
Word update behavior remains a manual check.

## 14. Deterministic Build Results

Two consecutive builds produced identical bytes:

```text
reference_sha256=c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71
byte_determinism=PASS
```

The deterministic claim is limited to the builder's package output. Any Word
or LibreOffice save can legitimately change package metadata and is not part
of this claim.

## 15. Inspection Results

Passed checks:

- canonical DOCX exists and passes `unzip -t`;
- canonical and specimen DOCX pass the Python OOXML inspector;
- all required OOXML parts are present;
- A4 geometry and margins match the candidate values;
- required style IDs and Style Map IDs are present and unique;
- body, heading, caption, and bibliography candidates are named styles;
- `numbering.xml` contains `0`, `%1`, `%1.%2`, and `%1.%2.%3` candidates;
- footer contains a `PAGE` field;
- three-line border candidates are present with 1/0.5/1 pt values and no
  internal vertical border;
- identity markers are present and forbidden source/real-content markers are
  absent;
- LibreOffice headless PDF conversion succeeded for both DOCX files;
- no formal paper body, bibliography, CSL, figure, or real experiment data was
  created.

## 16. External Style Specimen

Generated and retained outside Git at:

`/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step4_reference_docx_v1/generated/hfut_reference_style_specimen_v1.0.docx`

It contains the required governance notice, virtual bilingual front matter,
heading candidates, two body paragraphs, equation placeholder, figure/table
captions, one three-line table, three virtual references, and a PAGE field.
It is explicitly marked `TOOLCHAIN STYLE SPECIMEN ONLY`, `NOT PAPER CONTENT`,
and `NOT SUBMISSION MANUSCRIPT`.

## 17. Pending POC Items

- Pandoc Markdown-to-DOCX mapping and full POC are not performed in Step 4.
- Word multilevel numbering update, introduction restart, and cross-reference
  behavior require Microsoft Word.
- Body single-to-double-column semantic section placement requires the later
  build/post-processing/manual step.
- MathType object creation and equation typography require MathType/Word.
- Table borders, merged cells, continuation tables, and print pagination need
  Word review.
- Figure object editability and figure delivery parameters remain pending.
- Reference CSL rendering, GB/T 7714—2025 edge cases, and citation order are
  deferred to the later project step.

## 18. Files Created

Exactly these six authorized repository files were created/updated:

1. `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`
2. `scripts/paper/build_hfut_reference_docx.py`
3. `scripts/paper/inspect_hfut_reference_docx.py`
4. `docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv`
5. `docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_DOCX_DESIGN_v1.0.md`
6. `docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_DOCX_REPORT_v1.0.md`

The specimen, PDFs, logs, metadata, extracted OOXML directory, and temporary
profile directory remain outside the repository.

## 19. Validation

The final validation command set is:

```text
python3 scripts/paper/build_hfut_reference_docx.py
python3 scripts/paper/inspect_hfut_reference_docx.py docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx
unzip -t docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx
git diff --check
git status --short
git diff --name-only 6f250edcd424179dc301d3099801e86e377dd2f4
```

The last command is intended to be run with the exact starting HEAD recorded
above; the final report records the result after commit.

## 20. Step 5 Readiness

`READY_WITH_POC_DEPENDENCIES`

The reference candidate is ready to support a later Markdown/Bibliography
project skeleton, subject to the listed Pandoc, Word, MathType, column, table,
and reference-format POC items.

## 21. Next Executor

`PAPER_PROJECT_AI`
