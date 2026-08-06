# Paper Phase 2.5 Theme and Font Schema Diagnosis

## 1. Verdict

```text
DRAWINGML_THEME_SCHEMA_INVALID
WORDPROCESSINGML_FONT_FAMILY_ENUM_INVALID
```

These are generator-side OOXML defects confirmed by package comparison and
the official OpenXmlValidator.

## 2. Theme Differential

For the original v5 packages, `word/theme/theme1.xml` contains the expected
`clrScheme`, `fontScheme`, and `fmtScheme`, but the four `fmtScheme` lists are
empty:

```text
fillStyleLst=0
lnStyleLst=0
effectStyleLst=0
bgFillStyleLst=0
```

The supplied Word-saved packages contain three legal children in each list.
They also contain `objectDefaults`, `extraClrSchemeLst`, and `extLst`.

The repair uses the deterministic `word/theme/theme1.xml` bytes from Pandoc
3.10.1's built-in `default reference.docx`, embedded in the canonical builder
so generation does not depend on a user's local Pandoc data directory. The
repaired theme retains the legal `clrScheme`/`fontScheme`/`fmtScheme` order,
all four lists at `3`, and the optional structural containers.

## 3. Font Differential

The original v5 font table uses numeric values:

```text
宋体=3, 黑体=2, 楷体=3, Times New Roman=1
```

The allowed lexical enumeration is:

```text
decorative, modern, roman, script, swiss, auto
```

The canonical repair uses `宋体=auto`, `黑体=modern`, `楷体=modern`, and
`Times New Roman=roman`. It also uses valid ten-byte `panose1` values and
checks the required child order beginning with `altName`, `panose1`,
`charset`, `family`, `notTrueType`, `pitch`, and `sig`.

## 4. Additional Canonical Findings

Official validation of the pre-repair canonical reference found 58 errors:
43 style-level paragraph-property sequence errors, 2 negative `firstLine`
lexical errors, 1 table-style `tblLayout` error, 7 font-table errors, 4 theme
errors, and 1 settings error. These were repaired because they are explicit
schema findings; no Word user-saved package was used as the whole template.

## 5. Result

The fixed canonical reference has all four theme lists at `3`, no invalid font
family values, valid font child order, and zero official OpenXmlValidator
errors. The custom Inspector reports the same theme/font facts.
