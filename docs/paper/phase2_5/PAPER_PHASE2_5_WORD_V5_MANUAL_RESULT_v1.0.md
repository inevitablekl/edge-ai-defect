# Paper Phase 2.5 Word v5 Manual Result

## 1. Scope

This record preserves the Microsoft Word observation supplied for Step 7E. It
is a user-manual result, not an automated replacement for Microsoft Word.

## 2. v5 First-Open Result

Both untouched v5 packages reportedly showed Word's first-open message
“发现无法读取的内容”:

- Full: `poc_full_v5.docx`, SHA256
  `3d28c3e3b5f4d9f9d6bda340931816ebc0243ccd5e8537d738835e6e619ecb75`.
- Anonymous: `poc_anonymous_v5.docx`, SHA256
  `412c79af5a64622afb4854caa1643c6af1f570cc84fea36c715a0f750096a91f`.

The supplied Word-saved evidence files are read-only inputs. Their observed
theme lists are `3/3/3/3`; their observed font-family tokens are lexical
values such as `roman`, `modern`, and `auto` rather than numeric values.

## 3. Content Types Disposition

The v5 `[Content_Types].xml` order and coverage audit is confirmed valid:
`Default*` precedes `Override*`, with zero Default-after-Override entries,
unique declarations, no dangling overrides, and complete part coverage.
Content Types is therefore not the current Word repair cause.

## 4. Confirmed Schema Evidence

The original v5 packages contain empty DrawingML theme style lists and numeric
Word font-family values. Official OpenXmlValidator additionally identified
invalid font `panose1` lexical lengths and POC table-cell border ordering.

## 5. v6 Manual Requirement

No new Microsoft Word result is claimed here. `poc_full_v6.docx` and
`poc_anonymous_v6.docx` require a fresh first-open test in Microsoft Word,
without overwriting the v5 evidence. Record whether the unreadable-content
message appears and then inspect equations, columns, image, table, citations,
PAGE, and Full/Anonymous identity boundaries.

Next executor: `USER_MANUAL`.
