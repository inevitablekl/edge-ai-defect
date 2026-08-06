# Paper Phase 2.5 Word v4 Remediation Result

## 1. Verdict

```text
WORD_V4_READY_FOR_RETEST
```

This verdict means the concrete v3 repair cause is remediated and all available
non-Word checks pass. It is not a Microsoft Word first-open pass. Phase 2.5 and
Phase 3 remain unapproved until the required manual retest is recorded.

## 2. Repository state

- Starting branch: `main`.
- Starting HEAD: `17b7f4bb04914b3b83da738e3efe2e0bf772e44d`.
- Starting worktree/index: clean; `git diff --check`: PASS.
- No reset, restore, checkout, stash, clean, merge, rebase, push, tag change or
  dependency installation was used.
- Phase 0/1/2 artifacts and formal paper chapters were not modified.

## 3. Generator changes

- Repaired the canonical reference builder so numbering levels contain one
  valid `w:rPr`, not nested `w:rPr` elements.
- Reordered the canonical table-style properties to
  `tblBorders, tblLayout, tblCellMar` without removing fixed layout or the
  three-line-table feature.
- Strengthened both inspectors for nested numbering properties, style-level
  `tblPr`, `tcPr`, abstract-number/number order, content-type duplicates and
  v4 filenames.
- Updated the runner and manuscript hash gate for v4 and the repaired canonical
  reference.

No formula styling parameter was changed.

## 4. Canonical reference

| Artifact | SHA256 |
|---|---|
| repaired `hfut_journal_reference_v1.0.docx` | `98d96d4eafac104c0972bf4e90c2b97db89d8fb35f98f8570eb3ca2ef9024e1e` |
| external Step 4 specimen | `30e7dfed1bb225b46860e2abf7b27c46a075e1620b71a34ffc06e5793c8ddd66` |

Two consecutive canonical builds produced identical bytes. The repaired
reference passes ZIP and the strengthened reference inspector.

## 5. POC v4 outputs

Generated outside Git under the Step 6 POC root:

| Output | SHA256 |
|---|---|
| `poc_full_v4.docx` | `30c75255f03bc2bbe88c9bee3f9b755a9f57d5997a9c7698250aa86560600a5a` |
| `poc_anonymous_v4.docx` | `a14dbc883c0abb4e0ed9b2b61b1a8969b80caae8950567df73b5ffb39ec562f6` |

The DOCX, generated PDFs, logs, inspection JSON and extracted OOXML remain
external and are not submission files.

## 6. Automated validation

Both v4 candidates pass:

- deterministic generation, ZIP CRC, and strengthened inspector with zero
  errors;
- zero nested numbering `w:rPr`, invalid known child order, duplicate style,
  duplicate numbering ID, duplicate relationship ID, content-type duplicate,
  missing part, dangling relationship or invalid external relationship;
- A4, one-column front matter, two-column body, 425-twip column spacing, one
  final `sectPr`, and no page-number restart;
- semantic HFUT styles and heading numbering `0 / 1 / 1.1 / 1.1.1`;
- PAGE as the only field, no automatic `updateFields`, and no forbidden field;
- three editable OMML objects including two display equations; display
  480-twip `atLeast` spacing with 80-twip before/after and inline 360-twip
  `atLeast` spacing;
- one internal PNG figure, one three-line table, ordered citations and five
  styled reference entries, including one permitted HTTPS text hyperlink;
- Anonymous neutral `creator/lastModifiedBy`, no absolute path, no prohibited
  identity token, and no body identity field;
- LibreOffice supplemental previews: A4 and two pages for both variants;
- formal bibliography empty and every formal chapter still `STRUCTURE_ONLY`;
- manuscript-source validator, Python compilation, shell syntax and
  `git diff --check`.

LibreOffice, ZIP and custom inspector results do not substitute for Microsoft
Word first-open testing.

## 7. Equation layout disposition

```text
EQUATION_LAYOUT = CLOSED_PENDING_ARCHIVE
```

The supplied Word v3 PDFs are A4/two-page and show no formula crop or overlap.
v3 and v4 retain identical OMML counts and effective `atLeast` spacing. No
equation remediation was added in v4.

## 8. Windows retest requirements

The user/manual executor must use the exact v4 hashes above and, for each file:

1. record Microsoft Word version and test time;
2. open the untouched v4 file and record whether any repair, unreadable-content,
   compatibility or external-content prompt appears;
3. verify titles, identity boundary, sections, heading numbering, editable
   equations, figure, table, references and PAGE;
4. save under a new name, close and reopen it;
5. export a PDF and inspect both pages for crop/overlap;
6. for Anonymous, run Document Inspector after the final Word save, remove
   personal properties, then save/reopen/inspect again.

Only successful fresh Word first-open evidence can advance Phase 2.5. The next
executor is:

```text
USER_MANUAL
```
