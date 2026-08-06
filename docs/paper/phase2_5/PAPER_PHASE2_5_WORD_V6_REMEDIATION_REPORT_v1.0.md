# Paper Phase 2.5 Word v6 Remediation Result

## 1. Verdict

```text
WORD_V6_READY_FOR_RETEST
```

This means automated package validation is complete. Microsoft Word first-open
acceptance remains a required manual step.

## 2. Repository State

- Branch: `main`.
- Starting HEAD: `8f3587a43ca8f228f62b6b66dc4f08401ce029b7`.
- Starting worktree/index: clean; starting `git diff --check`: PASS.
- No reset, restore, checkout, stash, clean, merge, rebase, push, or tag
  operation was used.
- Phase 0/1/2 content was not changed; formal chapters remain
  `STRUCTURE_ONLY`.

## 3. Canonical Reference

The canonical reference was rebuilt deterministically. Current SHA256:

```text
c378063a04e18b8c1af261d00313fe58305636a5bc9833663644ce3e4d38a7c6
```

This value remains the historical v6 input hash. Step 7G later supersedes the
current canonical with
`416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7`
to synchronize the validated equation contract and canonical table-layout
governance. The v6 evidence and hashes in this report remain historical.

Two independent rebuilds matched byte-for-byte. Official OpenXmlValidator and
the custom reference Inspector both report zero errors.

Canonical part-level SHA comparison against the pre-Step-7E Git version found
content changes only in `word/theme/theme1.xml` and `word/fontTable.xml` for
the requested theme/font remediation, plus `word/styles.xml` and
`word/settings.xml` for independently observed official schema errors. No
document, numbering, footer, relationship, or media part changed.

## 4. v6 Outputs

Generated outside Git under
`/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7e_openxml_schema_validation_v1/poc/output/`:

| Variant | SHA256 | Custom Inspector | OpenXmlValidator |
|---|---|---:|---:|
| Full v6 | `aef3335e7f726c58a932852e29cd0c0e6808ae264b41b08c51e0fb9a01f83cdf` | 0 | 0 |
| Anonymous v6 | `cc4b105ff6fe950bb871a129b53c983426a22bd63e536bcdf63c393e638faa43` | 0 | 0 |

ZIP CRC tests, Content Types checks, theme/font checks, anonymous scanning,
and deterministic v6 re-run all pass.

## 5. Functional Regression Checks

Compared with the supplied v5 packages, both variants retain the same counts:

```text
Full:      59 paragraphs, 5 numbering uses, 2 sections, 5 OMML nodes,
           1 drawing, 1 table, 1 PAGE field
Anonymous: 53 paragraphs, 5 numbering uses, 2 sections, 5 OMML nodes,
           1 drawing, 1 table, 1 PAGE field
```

The v6 outputs retain A4 geometry, the single-column front matter /
double-column body boundary, title numbering, HFUT semantic styles, equations,
image, three-line table, ordered citations, and the Full/Anonymous content
boundary. LibreOffice previews are supplemental only and do not replace Word.

## 6. Windows Retest Requirement

Open each untouched v6 DOCX for the first time in Microsoft Word. Record only
whether “发现无法读取的内容” appears, then check equations, layout, image,
table, citations, PAGE, and identity boundary. Do not overwrite the v5 files.

## 7. Next Executor

```text
USER_MANUAL
```
