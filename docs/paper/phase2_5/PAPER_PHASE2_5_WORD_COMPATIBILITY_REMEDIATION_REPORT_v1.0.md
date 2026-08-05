# Paper Phase 2.5 Word Compatibility Remediation Result

## 1. Verdict

```text
REMEDIATION_CANDIDATE_READY_FOR_WORD_RETEST
```

This is not Word acceptance. It is the strongest permitted verdict before a
fresh Microsoft Word open/save/reopen test of both generated v2 files.

## 2. Repository State

- Required branch: `main`.
- Required starting HEAD:
  `6cc775d456342ac9660bafb00047e749fb17fcbc`.
- Starting worktree and index: clean.
- Starting `git diff --check`: PASS.
- No reset, restore, checkout, stash, clean, merge, rebase, push, tag change,
  or dependency installation was performed.
- Phase 0/1/2 and formal manuscript sections were not modified.
- The formal section files retain `STRUCTURE_ONLY`.

## 3. Windows Evidence

User-supplied Word identity:

```text
Microsoft® Word 2019 MSO (版本 2607 Build 16.0.20228.20124) 32 位
```

Both supplied repaired DOCX files pass ZIP integrity, and both supplied Word
PDF exports are A4/two-page files produced by Microsoft Word 2019. Their hashes
and classifications are recorded in
`PAPER_PHASE2_5_WINDOWS_WORD_POC_OBSERVATION_v1.0.md`.

## 4. Original/Repaired Package Diff

Both variants show the same repair classes: Word removes unused comments,
footnotes relationship, and SVG parts; retains the image as an internal PNG;
adds endnotes and a second footer; rewrites all major Word parts; makes style
IDs unique; retargets affected paragraphs; reorders section/table properties;
renumbers package definitions; and removes `updateFields`.

The complete row-level record is
`PAPER_PHASE2_5_WORD_REPAIR_DIFF_v1.0.csv`. XML counts and full package lists
are in `PAPER_PHASE2_5_WORD_REPAIR_DIAGNOSIS_v1.0.md`.

## 5. Root Cause

The generated originals contain 26 duplicate HFUT style IDs in full and 19 in
anonymous. The intended formatted definition and Pandoc's no-format
placeholder share the same ID. Word repairs the collision by renaming the
placeholder and changing paragraph references to it, which creates the
front-matter regression.

The postprocessor also emitted `sectPr` and `tblPr` children in invalid schema
order. These are direct generator defects. Unresolved `basedOn` references and
unused explicit relationships are additional compatibility defects removed by
the candidate postprocessor.

## 6. Unreadable Content Diagnosis

The unreadable-content repair is explained by the duplicate style definitions
plus invalid WordprocessingML child order. Word's repaired packages directly
normalize each of those structures. No duplicate numbering ID, duplicate
bookmark ID, duplicate drawing ID, invalid final-section placement, missing
internal target, missing image, or damaged OMML object was found.

## 7. External Field Diagnosis

The only field in either original is `PAGE`. There is no linked picture,
linked object, include field, DDE field, local absolute path, or `file://`
relationship. A permitted ordinary HTTPS hyperlink remains in the synthetic
web reference.

The original setting `w:updateFields=true` requested an open-time refresh and
Word removed it. The v2 generator removes this setting while preserving PAGE.

## 8. Front-Matter Style Regression

Word does not delete custom styles or clear paragraph style references. It
renames duplicate placeholder definitions (`HFUTTitleCN0`,
`HFUTAbstractBodyCN0`, and analogous IDs) and retargets paragraphs to them.
Those definitions lack the canonical paragraph/run formatting, so effective
formatting falls through the body-text/Normal inheritance chain. The defect is
therefore in both `styles.xml` and the rewritten `document.xml`, and is caused
by illegal duplicate styles.

The v2 files contain exactly one definition for every style ID and continue to
reference the original semantic IDs. All required first-page styles are both
defined and actually used.

## 9. Script Changes

### `postprocess_phase2_5_poc_docx.py`

- Keeps the first canonical definition of each duplicate style ID.
- Removes only `basedOn` references whose targets do not exist.
- Inserts `numPr`, `sectPr` children, `tblW`, `tblBorders`, and `tcBorders` in
  schema order.
- Removes `w:updateFields` without deleting PAGE.
- Emits an internally embedded PNG display and removes the unused SVG path.
- Removes unused explicit image/hyperlink relationships.

### `inspect_phase2_5_poc_docx.py`

- Accepts the governed `_v2.docx` names.
- Rejects duplicate style IDs, missing/cyclic `basedOn`, schema-order errors,
  forbidden external fields, open-time field updates, duplicate relationship
  IDs, missing internal targets, invalid external targets, and dangling
  explicit relationships.
- Requires PNG-only internal display, semantic style use, PAGE, sections,
  formulas, table, citations, and anonymization boundaries.

### `run_phase2_5_docx_poc.sh`

- Writes `poc_full_v2.docx` and `poc_anonymous_v2.docx` without overwriting the
  original POC inputs.
- Uses v2-specific inspection and preview names and records the retest status.

The Lua filter and canonical reference DOCX did not require modification.

## 10. POC v2 Outputs

External output root:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/output
```

| Candidate | Bytes | SHA256 | Status |
|---|---:|---|---|
| `poc_full_v2.docx` | 25,522 | `8cf23a373d29e6dfc0b610fc97ace7bb2d33f66eb4d7a40b4d4c906f2d0c8230` | compatibility remediation candidate |
| `poc_anonymous_v2.docx` | 25,175 | `3fdead078eea5fa2bc92b08d8ba07d66499a6e269bcc27f44d342fb30359db8b` | anonymized compatibility remediation candidate |

These external files are not submission files and are not committed.

## 11. Automated Validation

Passed for both v2 candidates:

- deterministic generation: two consecutive complete runs produced identical
  hashes;
- `file` identifies Microsoft OOXML and `unzip -t` passes;
- expanded inspector verdict: PASS;
- 77 style definitions, zero duplicate IDs, zero missing `basedOn`, zero
  `basedOn` cycles;
- every required semantic style is defined and used;
- first-page paragraphs retain HFUT semantic references, not `*0` repairs;
- zero schema-order violations in `pPr`, `rPr`, `sectPr`, `tblPr`, style
  definitions, and numbering levels;
- two A4 sections with 1-column then 2-column layout and 425-twip spacing;
- no page-number restart and PAGE retained;
- no forbidden external field and no open-time field update;
- no missing internal target, duplicate relationship ID, invalid external
  target, or dangling explicit relationship;
- one internal PNG drawing and no unused SVG;
- 3 `oMath`, 2 `oMathPara`, one table, required borders/data, numeric citation
  order, five reference entries, and governance markers preserved;
- anonymous forbidden-string scan: zero hits;
- non-authoritative LibreOffice previews: A4 and two pages;
- canonical reference DOCX unchanged at
  `c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71`;
- shell syntax, Python bytecode compilation, and `git diff --check`: PASS.

LibreOffice and ZIP success do not substitute for Microsoft Word acceptance.

## 12. Windows Retest Instructions

Use fresh local copies of the two v2 candidates in Microsoft Word 2019:

1. Record the Windows version, Word version, date, reviewer, and candidate
   SHA256 before opening.
2. Open each file and confirm there is no unreadable-content, repair,
   compatibility, or external-field-update prompt.
3. Inspect the Chinese/English titles, full-only authors/affiliations,
   abstracts, keywords, classification, and corresponding English styles.
   Confirm the paragraph styles are the original `HFUT*` IDs and formatting is
   not body-text/Normal fallback.
4. Confirm A4 geometry, margins, one-column front matter, continuous transition
   to two columns, and continuous page numbering.
5. Confirm heading numbers, editable OMML equations, internal PNG figure,
   caption, three-line table, citations, references, and PAGE field.
6. Press Ctrl+A then F9. PAGE may update; no external-file prompt or unexpected
   field text may appear.
7. For anonymous, run File → Info → Check for Issues → Inspect Document and
   record/remove any identity carrier.
8. Save each under a new name, close, reopen, and confirm there is still no
   repair prompt or style regression.
9. Export fresh PDFs and record hashes, page count, and screenshots for any
   failure. Do not overwrite the v2 candidates.

Until all checks pass, retain:

```text
MICROSOFT_WORD_RETEST_REQUIRED
NOT_SUBMISSION_FILE
```

## 13. Next Executor

```text
USER_MANUAL
```
