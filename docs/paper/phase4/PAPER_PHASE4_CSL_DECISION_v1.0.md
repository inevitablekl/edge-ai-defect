# Paper Phase 4 CSL Decision v1.0

## 1. Decision

`PROJECT_LOCAL_DERIVATIVE_REQUIRED_AND_ADOPTED`

The official GB/T 7714—2025 numeric CSL candidate is valid numeric CSL, but it
is not compliant with the actual manuscript's HFUT reference-type requirements
without a narrow local derivative. The final build uses:

```text
docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl
```

The derivative is used by both the Full and Anonymous DOCX build paths.

## 2. Exact upstream candidate

The derivative starts from the archived official Zotero style:

| Field | Value |
| --- | --- |
| Title | `China National Standard GB/T 7714-2025 (numeric, 中文)` |
| ID | `http://www.zotero.org/styles/china-national-standard-gb-t-7714-2025-numeric` |
| Source URL | `https://www.zotero.org/styles/china-national-standard-gb-t-7714-2025-numeric` |
| Upstream updated | `2026-05-10T01:39:45+00:00` |
| Archived size | 17,228 bytes |
| Archived SHA256 | `4df240a008123cb070dfd5224f45514f868e1fb27fb2dc678edc6b01fd314900` |
| License | CC BY-SA 3.0, retained in the copied CSL information block |

This matches the candidate recorded in the Phase 2.5 Markdown/DOCX POC
report. The upstream bytes were first copied unchanged; the tracked file is a
derivative rather than a claim that it is the untouched official download.

## 3. Demonstrated actual incompatibility

With the actual admitted bibliography, upstream renders final DOI-bearing
journal and conference records as `[J/OL]` and `[C/OL]` solely because a DOI is
present. For example, the locally verified final records for Song, Shao,
Weiss, Shin, Tang, Liu, and Kim rendered with `/OL` under the upstream file.

The HFUT source pattern requires `[J]` for final journal articles and `[C]`
for final conference papers. A DOI by itself does not prove that the cited
carrier is an online resource. This is an actual manuscript incompatibility,
not the Phase 2.5 synthetic-standard condition.

The Phase 2.5 `[Z]` versus `[S]` observation remains documented but is not
patched here: the accepted manuscript contains no standards, so no actual
standard record is affected.

## 4. Scoped derivative changes

Only the following behavior differs from the archived upstream candidate:

1. The CSL title, ID, self link, updated time, and summary identify this tracked file as a
   local derivative.
2. `entry-medium-id` does not append `OL` to a final journal or conference
   record merely because it has a DOI or URL. A journal record lacking final
   volume and issue metadata remains `[J/OL]`; this covers the locally archived
   online-first Lema article without inventing unavailable final fields.
3. Pandoc maps the admitted arXiv MLPerf Inference record to
   `article-journal`. The explicit `note = {Preprint}` in that one admitted
   record permits the derivative to render its verified preprint carrier as
   `[PP/OL]`.

Explicit online webpages continue to render `[EB/OL]`; the three archived NVIDIA
manual PDFs continue to render `[M]`. No style logic is added for a standard,
and no new literature is added.

## 5. Verification boundary

The Phase 4.7 validator checks the citation sequence, 14 rendered entries,
expected type markers, source/Full/Anonymous bibliography identity, and the
OOXML reference-style structure (Songti, Times New Roman, six-size, exact
14 pt). It does not claim a Windows Word visual inspection or modify scientific
prose, results, figures, tables, or front matter.
