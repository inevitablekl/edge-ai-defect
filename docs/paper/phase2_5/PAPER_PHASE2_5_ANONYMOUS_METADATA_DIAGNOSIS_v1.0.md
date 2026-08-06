# Paper Phase 2.5 Anonymous Metadata Diagnosis

## 1. Classification

```text
WORD_SAVE_ADDED_METADATA
```

The generator did not place a real author identity in the original Anonymous
v3 core or custom properties. Microsoft Word added the Windows user identity
when saving the repaired document.

## 2. Core-property comparison

| Property | Original Anonymous v3 | Word-saved Anonymous v3 | Source conclusion |
|---|---|---|---|
| `dc:creator` | `PAPER_PROJECT_AI_POC` | `PAPER_PROJECT_AI_POC` | neutral generator marker retained |
| `cp:lastModifiedBy` | `PAPER_PROJECT_AI_POC` | `凯伦 王` | identity added by Word save |
| `cp:revision` | absent | `1` | added by Word save |
| `dcterms:created` | `2026-08-06T00:00:00Z` | `2026-08-06T00:00:00Z` | unchanged |
| `dcterms:modified` | `2026-08-06T00:00:00Z` | `2026-08-06T12:20:00Z` | updated by Word save |

## 3. Custom properties

The following custom properties are semantically identical before and after
Word save: `anonymous-status=ANONYMIZED_POC_CANDIDATE`, empty `bibliography`,
CSL filename only, `poc-identity-enabled=False`, `poc-variant=anonymous`,
`reference-section-title=参考文献`, and
`word-inspector-status=NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED`. There is no
absolute workstation path and no real identity value in these properties.

The Anonymous body contains no author, affiliation, email, funding, biography,
acknowledgement or other prohibited identity field. The PAGE footer is an
expected non-identity footer and must not be removed.

## 4. Required handling

The generator cannot be expected to prevent Microsoft Word from recording its
current user during a later save. Therefore:

1. generate the Anonymous DOCX with neutral or empty core properties;
2. complete all Word edits and the final Word save;
3. run Document Inspector again on that final saved copy;
4. remove document properties and personal information;
5. save, close, reopen, and inspect the actual final candidate again.

This manual final-save cleanup is frozen as a mandatory submission step even
when automated generation reports no identity metadata.

## 5. Phase boundary

This classification does not make v3 or Phase 2.5 pass. Phase 3 remains
unauthorized.
