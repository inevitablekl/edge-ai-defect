# Paper Phase 2.5 Windows Word POC Observation v1.0

## 1. Scope and status

This record covers only the synthetic Step 6 full and anonymous POC files.
They remain `TOOLCHAIN_POC_ONLY`, `NOT_PAPER_CONTENT`, and
`NOT_SUBMISSION_MANUSCRIPT`. The recorded Step 7A entry status is:

```text
WORD_POC_REMEDIATION_REQUIRED
```

No Phase 3 manuscript body was created or edited.

## 2. Microsoft Word environment

The user supplied this exact Word identity on 2026-08-06:

```text
Microsoft® Word 2019 MSO
版本 2607
Build 16.0.20228.20124
32 位
```

The Windows version, reviewer identity, exact dialog text, screenshots, and
Document Inspector result were not supplied in this evidence set and are not
invented here.

## 3. Input classification

The two files whose names contain `word_repaired` are classified as:

```text
MICROSOFT_WORD_REPAIRED_DERIVATIVE
NOT_ORIGINAL_POC_OUTPUT
NOT_SUBMISSION_FILE
```

All four Windows input files were treated read-only. No input was overwritten.

## 4. File evidence

| File | Bytes | SHA256 | Structural observation |
|---|---:|---|---|
| `poc_full.docx` | 26,809 | `da0ded8249f8fc248b81a5a436417d4dfffe453667bcd5b0d57d86e0b8642731` | `file`: Microsoft OOXML; `unzip -t`: PASS |
| `poc_anonymous.docx` | 26,394 | `3f9799288a0953ab666c630a7c8372e45eb75dd7236cf8190069fa36591e12f2` | `file`: Microsoft OOXML; `unzip -t`: PASS |
| `poc_full_word_repaired.docx` | 41,069 | `d85cf438062d6dc6d4bcab316c0d1c79918fb5bbfd4791a72c01c47d2c61a11c` | `file`: Microsoft Word 2007+; `unzip -t`: PASS |
| `poc_anonymous_word_repaired.docx` | 40,475 | `72bd6ac6a3d391a746d0d31f8bce15e5f717ed553ca7f3c8d0a9d8e8b288fe1d` | `file`: Microsoft Word 2007+; `unzip -t`: PASS |
| `poc_full_word_export.pdf` | 303,391 | `37e18d0c99775450183b321bf005a976e00db14401698484df568e902aa77298` | Microsoft Word 2019 producer; 2 pages; A4 |
| `poc_anonymous_word_export.pdf` | 298,406 | `c614121349e9a8d79ee35cbab491dd1abab1460ecaa4d8a02f7914ece3878de7` | Microsoft Word 2019 producer; 2 pages; A4 |

The expected original DOCX hashes match exactly.

## 5. What the Windows derivatives prove

Both repaired DOCX packages have the same repair pattern. Word rewrote the
document, styles, numbering, settings, relationships, theme, font table,
footer, and property parts. It removed duplicate style IDs by renaming one
copy and changed paragraph references to those renamed definitions. It also
reordered the continuous section properties and table properties, removed
`w:updateFields`, discarded the unused SVG path, and retained the internally
embedded PNG display image.

This differential evidence is sufficient to diagnose a generator-side OOXML
compatibility defect. It does not establish that a newly generated candidate
opens without repair; that conclusion requires a fresh Word retest.

## 6. PDF observations

Both Word-exported PDFs are A4 and two pages. Extracted text retains the full
or anonymous front matter, the single-column to double-column transition,
heading numbers `0`, `1`, `1.1`, and `1.1.1`, OMML-rendered formula text, the
figure caption, table contents, five references, and page numbers.

The font inventory contains Times New Roman, SimSun, SimHei, Arial, and
Cambria Math. PDF presence is supplementary rendering evidence only; it does
not reverse the OOXML finding that front-matter paragraphs were retargeted to
Word-renamed placeholder styles lacking the intended local formatting.

## 7. Manual evidence still required

- Exact repair/unreadable-content dialog wording and any repair log.
- Windows version, inspection date, and reviewer record.
- Word Document Inspector result for the anonymous candidate.
- A fresh open/save/reopen and PDF export of both v2 candidates.
- Screenshots for any remaining repair prompt or layout regression.

## 8. Conclusion

```text
WINDOWS_REPAIR_EVIDENCE_ACCEPTED_FOR_DIFFERENTIAL_DIAGNOSIS
WORD_RETEST_OF_V2_REQUIRED
```
