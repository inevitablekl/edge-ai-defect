# Paper Phase 4.6 Anonymous Manuscript DOCX Build Report

## 1. Verdict

ANONYMOUS_DOCX_BUILD_PASS_WITH_PUBLICATION_LIMITATIONS

The anonymous manuscript was built from the same accepted sections,
bibliography, figures, tables, reference DOCX, and citation processing as the
Full manuscript. Identity-only publication paragraphs and identity-bearing
package properties were suppressed or sanitized. Scientific-content parity
and the anonymous identity scan passed.

## 2. Repository State

- Starting HEAD: `47129588542fb3d63d3065b3f1fd712ab02dbb64`
- Starting subject: `docs(paper): build full manuscript draft`
- Final HEAD: authorized Phase 4.6 commit containing this report; exact SHA is
  recorded in the Git handoff.
- Branch: `main`
- Starting worktree/index: clean.
- Final worktree/index: clean after the authorized Phase 4.6 commit.

## 3. Build

- Command: `scripts/paper/build_manuscript_docx.sh --build-anonymous`
- Result: PASS.
- Output: `docs/paper/manuscript/output/draft_anonymous.docx`
- Size: 128767 bytes.
- SHA256:
  `f38182d99f39e151a20db4be3d240e43d514ad8984cb55d9845c93605a1c496e`
- Private metadata dependency: `NONE`.
- Reproducibility check: the ignored private metadata file was temporarily
  moved out of its expected path during the anonymous build; construction and
  validation still passed.

## 4. Identity Removal

- CN authors (`王凯伦，王琦`): ABSENT.
- EN authors (`WANG Kailun, WANG Qi`): ABSENT.
- CN affiliation: ABSENT.
- EN affiliation: ABSENT.
- Corresponding-author designation: ABSENT.
- Email/contact fields: ABSENT.
- First-author biography: ABSENT.
- Author footnotes: ABSENT.
- Funding/acknowledgement identity: ABSENT; no funding field was generated.

## 5. Package Metadata

- `dc:creator`: empty.
- `cp:lastModifiedBy`: absent.
- Comments: none; the comments part contains zero comment records.
- Tracked changes: absent.
- Custom properties: only neutral `classification=TP391.41`; identity
  properties were removed.
- Hidden identity: not found.
- Filename/media filename identity: not found.
- Relationship-target identity: not found.
- Identity leakage scan: PASS; `ANONYMITY_SCAN_PASS`.

## 6. Front Matter Retained

- CN title: present.
- CN abstract: present.
- CN keywords: present.
- EN title: present.
- EN abstract: present.
- EN keywords: present.
- CLC `TP391.41`: present.

## 7. Scientific / Structural Parity

- Numbered scientific sections 0–5, representing all current manuscript body
  sections, are present; the reference list is also present.
- Figures: 3.
- Tables: 2.
- Rendered citations/references: retained; rendered reference list matches
  Full.
- Six frozen results: retained with the same magnitudes and directionality:
  `2.236671×`, `55.4519%`, FPS `+4.0738%`, mean latency `-4.0349%`, P95
  `+0.1514%`, and P99 `-0.1184%`.
- Contribution count: 2.
- Full identity-only paragraphs excluded from parity: 7.
- Scientific body, table, figure-caption, embedded-media, and rendered
  reference parity: PASS; `PARITY_PASS`.

## 8. Figures

- F1: present; same accepted embedded media as Full.
- F2: present; same accepted embedded media as Full.
- F3: present; same accepted embedded media as Full.

## 9. Tables

T1:

- present;
- 17 data rows;
- content matches Full.

T2:

- present;
- 4 data rows;
- V0/V2R only;
- V3R absent;
- content matches Full.

## 10. References

- Bibliography source entries: 15.
- Rendered references: 14.
- Unresolved citation keys: 0.
- Uncited existing entry: `reddi_et_al_2022_mlperf_mobile`.
- CSL state: structural Pandoc default rendering retained; CSL selection is
  not decided in Phase 4.6 and remains a Phase 4.7 item.

## 11. Automatic Validation

- ZIP integrity: PASS (`unzip -t`).
- XML parse: PASS for all XML and relationship parts.
- OpenXML/package metadata inspection: PASS through the custom sanitizer and
  validator; no separate OpenXML validator was installed or available.
- Full manuscript validator: PASS.
- Citation validator: PASS.
- Table postprocessor: PASS.
- Anonymous validator: PASS.
- Identity scan: PASS.
- Full/Anonymous parity validator: PASS.
- `git diff --check`: PASS.
- Mechanical LibreOffice conversion: PASS; A4, 9 pages. Full also converted
  mechanically to A4, 9 pages.
- Microsoft Word visual review: not performed.

## 12. Scientific Freeze

- Frozen values changed: NO.
- Scientific manuscript prose changed: NO.
- New statistics: NO.
- Excluded evidence restored: NO.
- V4 added: NO.
- Historical Attempt 2 restored: NO.
- Cross-stage multiplication added: NO.
- V3R independent task-level Gate D changed: NO.

## 13. Publication Limitations

The open manual and publication limitations are listed in §16. They do not
block the structural, privacy, or scientific-parity handoff to Phase 4.7.

## 14. Files Changed

- `scripts/paper/build_manuscript_docx.sh`
- `scripts/paper/full_manuscript_filter.lua`
- `scripts/paper/sanitize_anonymous_manuscript_docx.py`
- `scripts/paper/validate_anonymous_manuscript_docx.py`
- `docs/paper/manuscript/metadata/metadata_anonymous.yaml`
- `docs/paper/manuscript/config/pandoc_anonymous.yaml`
- `docs/paper/phase4/PAPER_PHASE4_ANONYMOUS_DOCX_BUILD_REPORT_v1.0.md`

Generated DOCX and intermediate files remain governed by the existing ignored
local artifact policy. Private metadata was not added.

## 15. Git Result

- No push, tag, amend, or squash was performed.
- Authorized tooling, configuration status, and governance report changes
  were committed on `main`.

## 16. Open Publication Limitations

- Microsoft Word final typography, pagination, and rendering were not
  manually reviewed.
- Figure 1 raster sharpness and Figure 2/3 typography consistency remain
  manual review items.
- Exact figure placement, table rule-weight appearance, and final page-level
  layout remain later Phase 4.8/4.9 items.
- CSL/journal bibliography styling remains a Phase 4.7 review item.

## 17. Recommendation

PHASE_4_7_READY
