# Paper Phase 2.5 Word v2 Manual Result

## 1. Evidence classification

The following files were read from
`/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7_windows_word_poc_v2/windows_input`:

- `poc_full_v2_word_saved.docx`
- `poc_anonymous_v2_word_saved.docx`
- `poc_full_v2_word_export.pdf`
- `poc_anonymous_v2_word_export.pdf`
- `WORD_MANUAL_RESULT_v2.txt`

They are `MICROSOFT_WORD_SAVED_DERIVATIVE`, `READ_ONLY_EVIDENCE`, and
`NOT_SUBMISSION_FILE`. The original v2 candidates remain at the Step 6
output path and were not overwritten.

## 2. Registered manual conclusion

The supplied manual result establishes:

- both original v2 files still triggered Word first-open repair;
- no external-field prompt appeared;
- Word repair preserved layout, numbering, columns, formulas, figures,
  tables, and citations;
- Word save followed by reopen was normal for both files;
- OMML formulas remained editable;
- anonymous body identity fields were absent;
- Document Inspector found the document property `作者`;
- a footer was present and is treated as an expected page-number carrier,
  not as identity leakage;
- formula vertical space was insufficient and invaded adjacent text lines.

The manual text's historical overall line `WORD_POC_V2_PASS_WITH_LIMITATIONS`
is superseded for this execution. The project disposition is:

```text
WORD_POC_V2_REMEDIATION_REQUIRED
```

## 3. Metadata observation

Independent read-only inspection of the supplied Word-saved DOCX files found:

```text
dc:creator       = PAPER_PROJECT_AI_POC
cp:lastModifiedBy = 凯伦 王
cp:revision      = 1
```

The first value is a neutral generator marker in the original candidate;
the second is identity metadata written by the Word save environment. A
fresh Word Document Inspector run is still required after the v3 retest.

The original anonymous candidate also carried an absolute local CSL path in
`docProps/custom.xml`. This is classified as `GENERATOR_METADATA_LEAK` (a
machine-path leak, not a body identity field) and is removed from v3. The
Word-saved `cp:lastModifiedBy=凯伦 王` is classified separately as
`WORD_SAVE_ADDED_METADATA`.
