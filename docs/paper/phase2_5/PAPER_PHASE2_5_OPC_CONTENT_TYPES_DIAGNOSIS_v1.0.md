# Paper Phase 2.5 OPC Content Types Diagnosis

## 1. Original v4 Content Types order

Both original v4 packages have the same sequence:

```text
Default(xml)
Default(rels)
Default(odttf)
Override(/word/webSettings.xml)
Override(/word/numbering.xml)
Override(/word/settings.xml)
Override(/word/theme/theme1.xml)
Override(/word/fontTable.xml)
Override(/docProps/app.xml)
Override(/docProps/core.xml)
Override(/docProps/custom.xml)
Override(/word/styles.xml)
Override(/word/document.xml)
Override(/word/footnotes.xml)
Override(/word/footer1.xml)
Default(png)
```

The inspector reports `default_after_override_count=1` and
`OPC_CONTENT_TYPES_ORDER_VIOLATION` for both v4 files.

## 2. Word-saved v4 order

The supplied Word-repaired/saved packages normalize the sequence to:

```text
Default(xml)
Default(rels)
Default(odttf)
Override(/word/webSettings.xml)
Override(/word/numbering.xml)
Override(/word/settings.xml)
Override(/word/theme/theme1.xml)
Override(/word/fontTable.xml)
Override(/docProps/app.xml)
Override(/docProps/core.xml)
Override(/docProps/custom.xml)
Override(/word/styles.xml)
Override(/word/document.xml)
Override(/word/footnotes.xml)
Override(/word/footer1.xml)
Override(... remaining package overrides ...)
```

The checked Word-saved samples have `default_after_override_count=0` and no
Content Types audit errors.

## 3. OPC requirement

For the package Content Types root, declarations must be ordered as:

```text
Default* followed by Override*
```

The `Default` declaration for `png` therefore must precede the first
`Override`. Defaults and overrides must also be unique, non-empty, and cover
the package parts without dangling overrides.

## 4. Generator defect

The former PNG fallback logic used:

```python
ET.SubElement(content_types, qn(CT, "Default"), {
    "Extension": "png",
    "ContentType": "image/png",
})
```

That appends the new `Default` at the root tail, after existing overrides.
The repaired generator inserts it immediately before the first `Override` and
then applies `normalize_content_types`, which preserves relative order within
the two groups, preserves extension children after them, and rejects duplicate
declarations.

## 5. Inspector gap

The old inspector checked duplicate Default extensions, duplicate Override
PartNames, and dangling Override targets, but did not inspect the root child
sequence. It also did not verify that every package part was covered by an
Override or a Default, nor did it report empty ContentType values. Therefore
the v4 package could receive a PASS despite the deterministic ordering defect.

The revised inspector reports `content_types_order`, counts, ordering
violations, uniqueness violations, missing part content types, dangling
overrides, unsupported nodes, and empty ContentType values.

## 6. Order-only differential test

Diagnostic files were generated outside Git:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7d_opc_content_types_order_v1/output/poc_full_v4_ct_order_only.docx
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7d_opc_content_types_order_v1/output/poc_anonymous_v4_ct_order_only.docx
```

| Variant | Diagnostic SHA256 | Differing content parts | Non-Content-Types part SHA changes |
|---|---|---|---|
| Full | `3d28c3e3b5f4d9f9d6bda340931816ebc0243ccd5e8537d738835e6e619ecb75` | `[Content_Types].xml` only | 0 |
| Anonymous | `412c79af5a64622afb4854caa1643c6af1f570cc84fea36c715a0f750096a91f` | `[Content_Types].xml` only | 0 |

The source v4 package SHA values were verified as
`30c75255f03bc2bbe88c9bee3f9b755a9f57d5997a9c7698250aa86560600a5a` and
`a14dbc883c0abb4e0ed9b2b61b1a8969b80caae8950567df73b5ffb39ec562f6`. ZIP
container metadata changed in the diagnostic copies, as permitted.

## 7. v5 Content Types validation

Both v5 packages contain 4 Defaults and 12 Overrides. Both have:

```text
default_after_override_count = 0
duplicate_default_extensions = []
duplicate_override_part_names = []
missing_part_content_types = []
dangling_overrides = []
```

## 8. Scope not changed in this remediation

This round did not intentionally change formula spacing, single/double-column
strategy, heading numbering, three-line table borders, citation formatting,
anonymous body content, image dimensions, PAGE fields, or canonical style
values. The formal Phase 0/1/2 artifacts remain untouched and formal chapters
remain `STRUCTURE_ONLY`.
