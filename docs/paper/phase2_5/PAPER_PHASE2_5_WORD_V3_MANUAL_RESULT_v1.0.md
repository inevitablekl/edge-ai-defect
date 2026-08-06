# Paper Phase 2.5 Word v3 Manual Result

## 1. Verdict

```text
WORD_V3_REMEDIATION_REQUIRED
```

Phase 2.5 has not passed. Phase 3 remains unauthorized.

## 2. Evidence classification

All files under the Windows evidence directory are classified as:

```text
MICROSOFT_WORD_REPAIRED_OR_SAVED_DERIVATIVE
READ_ONLY_EVIDENCE
NOT_SUBMISSION_FILE
```

| Evidence | SHA256 |
|---|---|
| `WORD_MANUAL_RESULT_v3.txt` | `3e99f4bf95fc4d8063eb74dbdb70ee36293bdf918db0ff1ff7b206716e1d6da2` |
| `poc_full_v3_word_saved.docx` | `5944a838fd95c30061a19c8b2f770b2f7e2dac8fde0516089fed376a15d93aa8` |
| `poc_anonymous_v3_word_saved.docx` | `76cfb4a07cfa87cdec6bbbd2b4f6dfe83c85c165ac48bf64c4de5dc76dad03a7` |
| `poc_full_v3_word_export.pdf` | `e8bd41df86f33c61a8860c72045e66fa7ab379fa03c9460d10755eb8a3961ce1` |
| `poc_anonymous_v3_word_export.pdf` | `f0e75efb173640b0dec4939ff4a570c36c46333c835d40ae3f3aff381ce973cb` |

The supplied `screenshots/` directory exists but contains no regular files, so
there are no screenshot filenames or hashes to register. No evidence input was
modified or copied into Git.

## 3. Manual findings

- Full original v3 first open: **FAIL**, unreadable-content repair prompt.
- Anonymous original v3 first open: **FAIL**, unreadable-content repair prompt.
- After Word repair, content and visible layout were basically normal.
- Both Word-saved derivatives reopened normally.
- Equation vertical layout: **PASS**.
- OMML equations remained editable.
- Anonymous body identity fields were absent.
- Document Inspector found an author document property; metadata had not been
  removed before evidence capture.

The first-open failure overrides the earlier automated readiness status. v3 is
not `WORD_V3_READY_FOR_RETEST` and is not a pass.

## 4. Equation disposition

```text
EQUATION_LAYOUT = CLOSED_PENDING_ARCHIVE
```

Both Word-exported PDFs are two-page A4 files. Page-by-page visual review found
no equation clipping or overlap. The original v3 OOXML retains three `m:oMath`
objects, two `m:oMathPara` objects, display spacing of 480 twips `atLeast` with
80-twip before/after spacing, and an inline 360-twip `atLeast` exception. No
equation style change is authorized or required by this evidence.

## 5. Scope boundary

This result records synthetic POC evidence only. No formal paper body,
experiment result, submission manuscript, or Phase 3 work is authorized.
