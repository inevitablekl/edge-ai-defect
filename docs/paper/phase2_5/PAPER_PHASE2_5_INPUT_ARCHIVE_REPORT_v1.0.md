# Paper Phase 2.5 Step 1 Input Archive Report v1.0

## 1. Verdict

`STEP_1_COMPLETE`

The external raw input inventory, read-only metadata capture, SHA256/MD5
inventory, file-type detection, permission observations, and byte-level
deduplication are complete. All eight raw files now have an identity and
provenance classification supported by the supplemented `SOURCE_NOTES.txt`
and official journal pages.

No DOC conversion, formal specification extraction, `reference.docx` creation,
Markdown-to-DOCX POC, or source-content rewriting was performed.

## 2. Repository State

- Branch: `main`
- Starting HEAD: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`
- Phase 2 tag: `paper-phase2-complete-v1.0`
- Tag type: `tag`
- Peeled tag commit: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`
- Starting worktree/index: clean
- Final worktree/index target: clean after the Step 1 commit

## 3. External Source Root

- External root ID: `HFUT_PHASE2_5_SOURCE_V1`
- Source root: `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1`
- Raw directory: `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/raw`
- Source notes: `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/source_notes/SOURCE_NOTES.txt`
- Source notes status: present and read; not copied into Git
- Collection date: `2026-08-05`; collector: `USER_MANUAL`
- Raw files modified: `NO`

The manifest uses portable `relative_external_path` values under the external
root; absolute paths are current-host audit locations only.

## 4. Files Discovered

Eight regular files were found: four journal attachment candidates, one
standard-copy PDF, one web-excerpt PDF, and two formally published articles
from the target journal. The complete inventory is in
`PAPER_PHASE2_5_TEMPLATE_SOURCE_MANIFEST_v1.0.csv`.

The two published-article PDFs are visual references only. They are not
submission templates and do not automatically enter the formal bibliography.

## 5. File Type Detection

Read-only `file` detection reported four `.doc` files as `Composite Document
File V2 Document` (OLE Compound Document), Little Endian, Windows, code page
936, and four `.pdf` files as PDF documents. No extension/type mismatch was
detected. No LibreOffice, Microsoft Word, Pandoc, or conversion program was
used.

## 6. SHA256 Inventory

All eight SHA256 values are unique and recorded in the manifest:

```text
UNIQUE_BY_SHA256: 8
BYTE_IDENTICAL_DUPLICATE: 0
```

MD5 is recorded as optional audit metadata; SHA256 is the primary identity key.

The task-supplied sample validation script hard-codes six rows. Its execution
returned `expected 6 source rows, got 8` because the actual raw directory
contains two additional files. The governing rule is one manifest row per
actual external raw file, so the actual eight-row validation is authoritative;
the discrepancy is recorded rather than silently omitting either PDF.

## 7. Provenance Classification

The four `.doc` files are `OFFICIAL_JOURNAL_ATTACHMENT_CANDIDATE`, based on the
source-notes journal download-list URL, matching filenames, collection date,
and `NONE` transformation. They are not upgraded to
`OFFICIAL_JOURNAL_ATTACHMENT_VERIFIED`, because an explicit attachment URL and
independent official payload chain are not recorded.

`GBT 7714—2025 信息与文献 参考文献著录规则.pdf` is
`USER_PROVIDED_STANDARD_COPY`, not an asserted official standard-body original.
`摘录-202608052030.pdf` is `USER_CAPTURED_WEB_EXCERPT`, not an official
template. The two article PDFs are both
`OFFICIAL_JOURNAL_PUBLISHED_ARTICLE_VERIFIED`, based on the supplemented
source notes and their official manuscript pages. They are formal published
visual references, not format-authority attachments or mandatory templates.

`1003-5060-2026-5-2.pdf` is the primary visual reference and related AI article;
`1003-5060-2026-1-3.pdf` is a secondary visual reference and general engineering
layout reference. Neither article is automatically a formal reference for the
current paper.

## 8. Duplicate Analysis

SHA256 grouping produced eight singleton groups. No byte-identical duplicate
exists. The four attachment filenames share a journal prefix but identify
different roles and have non-similar sizes; the two article PDFs also have
different sizes and distinct roles. No `POSSIBLE_SEMANTIC_DUPLICATE` group is
declared. This is a
filename/size/role review only; semantic content was not parsed.

## 9. Permission and File-System Observations

- Eight regular files; no symlink, zero-byte file, unexpected directory entry,
  duplicate filename, or extension/type mismatch.
- Chinese filenames and the em dash in the standard-copy filename were readable;
  no filename encoding anomaly was observed.
- Six files carry executable bits (`0775`); two additional PDFs are `0664`.
- No file is world-writable.
- Permissions, names, contents, and timestamps were not changed. Executable
  bits are recorded and do not by themselves establish corruption.

## 10. Missing or Deferred Inputs

- `UNKNOWN_SOURCE` count: `0`; all eight files have an identity
  classification.
- The four `.doc` files remain official attachment candidates. Their formal
  content authority will be checked in Step 2 against the source pages; their
  contents have not been extracted in Step 1.
- The supplied GBT PDF's official publication source/version chain is unverified.
- The two article PDFs remain visual references only and are not automatically
  added to the formal bibliography.

## 11. Git Inclusion Policy

Only these three governance files are eligible for this commit:

- `PAPER_PHASE2_5_EXECUTION_PLAN_v1.0.md`
- `PAPER_PHASE2_5_TEMPLATE_SOURCE_MANIFEST_v1.0.csv`
- `PAPER_PHASE2_5_INPUT_ARCHIVE_REPORT_v1.0.md`

Official `.doc` files, GB/T PDF, web-excerpt PDF, recent-paper PDFs, source
notes, and any conversion or temporary DOCX outputs remain external.

## 12. Step 2 Readiness

`READY_FOR_SPEC_EXTRACTION`

Step 2 textual specification extraction may begin for the four official
attachment candidates and other identified source inputs under the manifest
controls. This does not authorize DOC conversion or any later step.

## 13. Next Executor

`PAPER_PROJECT_AI`

## 14. Next Action

Perform only the authorized Step 2 specification-extraction task. Preserve raw
files as external read-only inputs; do not treat the published article PDFs as
templates, mandatory formatting authorities, or automatic bibliography entries.
