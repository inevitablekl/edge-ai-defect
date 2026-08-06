# Paper Phase 2.5 Word v2 Repair Diagnosis

## 1. Verdict

```text
WORD_POC_V2_REMEDIATION_REQUIRED
```

This diagnosis covers the current Step 6 v2 candidates and the supplied
Microsoft Word saved derivatives. It does not claim that either v3 candidate
has passed Microsoft Word.

## 2. Package differential

Both variants have the same structural classes. The v2 package has 17 parts;
the Word-saved derivative has 18 parts. Word adds `word/endnotes.xml`,
`word/footer2.xml`, and `word/media/image1.png`; removes the empty
`word/comments.xml`, renames the embedded PNG, and removes the old image/SVG
paths. The PNG bytes are preserved.

The current v2 package also contains this invalid reference:

```text
[Content_Types].xml Override PartName=/word/media/rId16.svg
```

There is no `word/media/rId16.svg` part. Word removes that override during the
first-open rewrite. `unzip -t` does not detect this dangling content-type
override, so it was added as an explicit inspector check for v3.

## 3. Minimum first-open repair set

The smallest generator-side set supported by the current differential is:

1. Remove the dangling SVG content-type override after the unused SVG path is
   removed.
2. Normalize `w:pPr` child order inside `word/styles.xml`. For example,
   `HFUTEquation` is emitted as `jc, spacing, keepLines` in v2, while Word
   saves it as `keepLines, spacing, jc`; the same canonical style-template
   ordering pattern affects title, body, heading, caption, and reference
   styles.

The empty comments part and unused comments relationship are also removed as
package hygiene. They are not content loss: no comment nodes exist. Word's
added footer2, endnotes part, relationship renumbering, namespace additions,
and image filename normalization are save-time normalization, not evidence
of deleted visible content.

## 4. Other structures checked

- No duplicate style IDs remain in the current v2 candidate; the earlier
  duplicate-style defect is not present in this exact starting package.
- No duplicate numbering IDs, bookmark IDs, or drawing `docPr` IDs were
  found.
- The original has two sections: A4, 425-twip column spacing, one column then
  two columns. Word preserves those semantics.
- The only field is `PAGE` in `word/footer1.xml`; no INCLUDEPICTURE,
  INCLUDETEXT, LINK, DDE, DDEAUTO, RD, SEQ, or REF field exists.
- The current v2 settings do not contain `w:updateFields`; the PAGE field is
  therefore not an open-time external update request.
- The ordinary HTTPS hyperlink in the synthetic bibliography is external
  text-link metadata, not an external field or embedded object.
- `mc:Ignorable` is absent in v2 and Word adds compatibility namespaces in
  the saved derivative. This is a Word serialization difference, not the
  minimal defect identified above.
- Header parts are absent in both packages. Footer presence is retained as
  the expected PAGE carrier.

## 5. Anonymous metadata classification

The v2 anonymous candidate has neutral `dc:creator` and
`cp:lastModifiedBy` values (`PAPER_PROJECT_AI_POC`), and no body author,
affiliation, email, funding, biography, or acknowledgement fields. Its
custom `csl` property nevertheless contains an absolute `/home/orin/...`
path. This is:

```text
GENERATOR_METADATA_LEAK
```

The Word-saved anonymous derivative changes `cp:lastModifiedBy` to `凯伦 王`
and adds `cp:revision=1`. This is:

```text
WORD_SAVE_ADDED_METADATA
```

The footer is:

```text
EXPECTED_NONIDENTITY_FOOTER
```

because its only field is the normal PAGE field. The v3 postprocessor removes
the absolute CSL path and keeps the neutral core properties. Only a fresh
Word Document Inspector can determine what the next Word save writes.

## 6. Visible-content preservation

The supplied Word PDFs and saved DOCX confirm preservation of titles,
front-matter boundaries, numbering, columns, editable OMML, figure/table
content, citations, references, and page numbering after Word repair. The
repair prompt therefore identifies package compatibility, not loss of those
objects.

## 7. Canonical reference disposition

The canonical reference DOCX was not modified. Its SHA256 remains:

```text
c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71
```

The v3 generator repairs the copied style XML and does not alter the
canonical template.
