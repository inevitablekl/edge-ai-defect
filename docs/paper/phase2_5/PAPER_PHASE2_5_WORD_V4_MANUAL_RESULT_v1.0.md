# Paper Phase 2.5 Word v4 Manual Result

## 1. Verdict

```text
WORD_V4_RETEST_FAILED_OPC_CONTENT_TYPES_ORDER
```

This is the user-provided Microsoft Word result for the untouched v4
artifacts. Both original v4 files failed first-open acceptance; Word repaired
and saved copies could be reopened. Phase 2.5 remains pending the v5 manual
retest.

## 2. Tested v4 artifacts

| Variant | SHA256 |
|---|---|
| `poc_full_v4.docx` | `30c75255f03bc2bbe88c9bee3f9b755a9f57d5997a9c7698250aa86560600a5a` |
| `poc_anonymous_v4.docx` | `a14dbc883c0abb4e0ed9b2b61b1a8969b80caae8950567df73b5ffb39ec562f6` |

## 3. Manual observation

- First open of both untouched v4 files in Microsoft Word: FAIL.
- Word repair and Save As copies: reopenable.
- No new visible anomaly was reported for formulas, layout, columns,
  figures, tables, or citations after Word repair/save.
- This repository report records the supplied manual observation; it does not
  claim an automated Microsoft Word run.

## 4. Deterministic cause

Both originals contain a `Default` for `png` after one or more `Override`
elements in `[Content_Types].xml`. This is classified as
`OPC_CONTENT_TYPES_ORDER_VIOLATION`, not as ordinary Word normalization.

## 5. Disposition

The generator has been corrected and v5 artifacts are ready for a fresh
Microsoft Word first-open retest. The canonical reference DOCX was already
legal and was not modified.
