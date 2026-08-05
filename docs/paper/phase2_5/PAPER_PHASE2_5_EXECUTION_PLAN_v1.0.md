# Paper Phase 2.5 Execution Plan v1.0

## Scope

Paper Phase 2.5 is the authoring-toolchain and publication-workflow freeze.
This plan records the authorized sequence after the Paper Phase 2 freeze. Raw
source files remain external and read-only; no raw source is copied into Git.

## Authorized Step Sequence

1. **Step 1 — 输入归档、来源登记、哈希与去重**
   (`Source Input Archive, Provenance and Deduplication`).
2. **Step 2 — 规范提取**
3. **Step 3 — DOC→DOCX受控转换与格式解析**
4. **Step 4 — reference.docx制作**
5. **Step 5 — Markdown/BibTeX工程骨架**
6. **Step 6 — Markdown→DOCX POC**
7. **Step 7 — Windows人工验收**
8. **Step 8 — 工具链最终冻结**

## Current Step Boundary

This execution covers Step 1 only. It records external input identity,
provenance, hashes, type detection, permissions, and duplicate analysis. It
does not perform formal specification extraction, DOC conversion,
`reference.docx` production, or Markdown-to-DOCX proof-of-concept work.

## Governance Constraints

- `Phase 3 NOT AUTHORIZED`.
- No new experiments.
- No manuscript drafting or completed article prose.
- Raw source files remain external.
- Official source files, standards PDFs, screenshots/excerpts, recent-paper
  PDFs, conversion outputs, and source notes are not Git inputs.
- Source classification must not exceed the evidence in `SOURCE_NOTES.txt`.
- A file is not declared semantically duplicate without content parsing.

## Step Gates

| Step | Gate status |
|---|---|
| Step 1 | Current task; archive/provenance report required. |
| Step 2 | Requires Step 1 inventory and provenance review. |
| Step 3 | Requires approved source selection and controlled conversion plan. |
| Step 4 | Requires verified reference-format inputs. |
| Step 5 | Requires verified requirements and literature-input decisions. |
| Step 6 | Requires a controlled toolchain POC scope. |
| Step 7 | Requires Windows Word manual acceptance. |
| Step 8 | Requires all preceding gates and final evidence record. |
