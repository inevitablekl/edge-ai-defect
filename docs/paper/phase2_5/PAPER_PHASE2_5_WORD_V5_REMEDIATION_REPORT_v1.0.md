# Paper Phase 2.5 Word v5 Remediation Result

## 1. Verdict

```text
WORD_V5_READY_FOR_RETEST
```

Automated package validation is complete. Microsoft Word first-open retest of
the untouched v5 files remains required.

## 2. Repository State

- Branch: `main`.
- Starting HEAD: `f39d03571e94c144a0a8f3ebfb2c5efc7d7bd795`.
- Starting worktree/index: clean; `git diff --check`: PASS.
- No reset, restore, checkout, stash, clean, merge, rebase, push, or tag
  operation was used.
- Phase 0/1/2 artifacts were not modified; formal chapters remain
  `STRUCTURE_ONLY`.

## 3. v4 Windows Result

The supplied manual result is that both original v4 files failed Microsoft
Word first open, while Word-repaired Save As copies reopened successfully.
The v4 package diagnosis is the deterministic
`OPC_CONTENT_TYPES_ORDER_VIOLATION` described below.

## 4. Confirmed OPC Root Cause

The PNG `Default` declaration was appended after existing `Override` nodes in
`[Content_Types].xml`. The required CT_Types order is `Default*` followed by
`Override*`. Both v4 inspectors now fail with
`OPC_CONTENT_TYPES_ORDER_VIOLATION` and
`default_after_override_count=1`.

## 5. Generator Defect

The former `ET.SubElement(content_types, Default, ...)` call appended the PNG
declaration to the root tail. The new `normalize_content_types` function
collects Defaults and Overrides, preserves extension children after them,
rejects duplicate declarations, validates non-empty attributes, and writes
`Default* + Override*`.
PNG is inserted before the first Override.

## 6. Inspector Gap

The former inspector did not check Default-after-Override order or complete
part coverage. It now reports the required sequence, counts, uniqueness,
missing part content types, dangling overrides, unknown nodes, and empty
ContentType values.

## 7. Order-Only Differential Test

The two external order-only diagnostic copies changed only
`[Content_Types].xml` at the part-content level. All other package part SHAs
were unchanged; ZIP container metadata was allowed to differ. Details and
paths are recorded in `PAPER_PHASE2_5_OPC_CONTENT_TYPES_DIAGNOSIS_v1.0.md`.

## 8. Script Changes

Modified:

- `scripts/paper/postprocess_phase2_5_poc_docx.py`
- `scripts/paper/inspect_phase2_5_poc_docx.py`
- `scripts/paper/run_phase2_5_docx_poc.sh`
- `scripts/paper/build_hfut_reference_docx.py`
- `scripts/paper/inspect_hfut_reference_docx.py`

The runner now produces and inspects `poc_full_v5.docx` and
`poc_anonymous_v5.docx`. It does not use a Word-saved file as the generation
baseline.

## 9. Canonical Reference Disposition

The canonical reference already passed the same Content Types audit. Its
content and SHA were preserved:

```text
98d96d4eafac104c0972bf4e90c2b97db89d8fb35f98f8570eb3ca2ef9024e1e
```

A temporary builder output independently reproduced the same SHA and passed
the builder-side Content Types validation.

## 10. POC v5 Outputs

Generated outside Git:

| Variant | Path | SHA256 | CT statistics |
|---|---|---|---|
| Full | `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/output/poc_full_v5.docx` | `3d28c3e3b5f4d9f9d6bda340931816ebc0243ccd5e8537d738835e6e619ecb75` | 4 Default, 12 Override, 0 Default-after-Override |
| Anonymous | `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/output/poc_anonymous_v5.docx` | `412c79af5a64622afb4854caa1643c6af1f570cc84fea36c715a0f750096a91f` | 4 Default, 12 Override, 0 Default-after-Override |

Both have unique Default extensions, unique Override PartNames, complete part
coverage, and no dangling Override.

## 11. Automated Validation

- v5 full and anonymous inspectors: PASS with zero errors.
- ZIP CRC tests: PASS.
- Deterministic second run: both v5 SHA256 values unchanged.
- A4 geometry and 425-twip column spacing: PASS.
- Single-column front matter and double-column body: PASS.
- OMML equations retained: 3 OMML objects, with the existing equation
  spacing contract retained.
- Styles, numbering, image, three-line table, ordered citations and PAGE
  field: PASS.
- Anonymous identity scan: PASS.
- LibreOffice supplemental previews: 2 pages and A4 for both variants.
- Formal bibliography remains empty; formal sections remain `STRUCTURE_ONLY`.
- Python compilation, shell syntax, and `git diff --check`: PASS.

These checks do not substitute for Microsoft Word first-open acceptance.

## 12. Windows Retest Requirements

Open each untouched v5 file for the first time in Microsoft Word and record
whether a repair, unreadable-content, compatibility, or external-content
prompt appears. Confirm the existing equations, layout, image, table,
citations, PAGE field, and Full/Anonymous identity boundary. Save only under a
new name for the follow-up reopen check.

## 13. Next Executor

```text
USER_MANUAL
```
