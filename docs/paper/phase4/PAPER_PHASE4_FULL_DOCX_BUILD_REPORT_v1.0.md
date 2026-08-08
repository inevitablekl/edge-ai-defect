# Paper Phase 4.5 Full Manuscript DOCX Build Report

## 1. Verdict

FULL_DOCX_BUILD_PASS_WITH_PUBLICATION_LIMITATIONS

The first formal complete identity-bearing Full DOCX was built and passed the
automatic Phase 4.5 checks. No Anonymous DOCX was built.

## 2. Repository State

- Starting HEAD: `616543488a4b68bd22a91268a4309b9c7e52c697`
- Final HEAD: commit created for this Phase 4.5 build; exact SHA is recorded
  in the Git handoff.
- Branch: `main`
- Starting worktree/index: clean
- Final worktree/index: clean after the authorized source/tooling/report
  commit

## 3. Build Inputs

- Sections: `docs/paper/manuscript/sections/00_title_abstract.md` through
  `06_conclusion.md`, in fixed order.
- Bibliography: `docs/paper/manuscript/references/references.bib`.
- Full metadata: local ignored
  `docs/paper/manuscript/metadata/metadata_private.yaml`.
- Reference DOCX:
  `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`.
- Figures: FINAL_ACCEPTED Figure 1/2/3 assets from
  `docs/paper/manuscript/figures/figure_manifest.csv`.
- Tables: accepted Markdown Table 1/2 plus
  `scripts/paper/postprocess_publication_tables.py`.
- Build/tooling: Pandoc 3.10.1, the Full-manuscript Lua bridge, Full DOCX
  section postprocessor, and the Phase 4.5 DOCX validator.

## 4. Output

- Full DOCX:
  `docs/paper/manuscript/output/draft_full.docx`
- File size: 129487 bytes
- SHA256:
  `e7f582ad598d8aa941062f3bafb8f48654b27f4a13c7d09476f5821609f32970`
- Build command: `scripts/paper/build_manuscript_docx.sh --build-full`
- Build result: PASS
- Mechanical PDF conversion: PASS, A4, 9 pages

The DOCX and intermediate build assets remain in the ignored manuscript output
directory. Private metadata was not committed.

## 5. Front Matter

- CN title: present and preserved.
- EN title: present and preserved.
- CN abstract/keywords: present and preserved.
- EN abstract/keywords: present and preserved.
- Authors: 王凯伦，王琦 / WANG Kailun, WANG Qi.
- Affiliation: present in Chinese and English.
- Corresponding author: 王琦 / WANG Qi retained.
- Corresponding-author email: omitted because the local field is empty and
  remains `PUBLICATION_METADATA_PENDING`; no email was fabricated.
- CLC: `TP391.41` present.
- Funding: omitted; no funding-none placeholder was inserted.
- Biography: present from local accepted metadata.

## 6. Figures

- F1: present; accepted final SVG was mechanically converted to PNG because
  Pandoc could not embed SVG without `rsvg-convert`.
- F2: present using the accepted final PNG asset.
- F3: present using the accepted final PNG asset.
- Figure drawings detected: 3.
- Prototype assets were not used.

## 7. Tables

T1:

- present;
- 17 data rows preserved;
- three-line structure present;
- vertical rules and internal body gridlines absent.

T2:

- present;
- V0/V2R only;
- V3R absent;
- 4 data rows preserved;
- thresholds and numeric precision preserved;
- three-line structure present;
- vertical rules and internal body gridlines absent.

## 8. References / Citations

- Bibliography source entries: 15.
- Rendered references: 14 cited entries.
- Uncited existing source entry: `reddi_et_al_2022_mlperf_mobile`.
- Unresolved citation keys: 0.
- Manual numeric citation patterns: 0.
- CSL state: structural Pandoc default rendering used; no semantic CSL
  selection was made. Dedicated CSL/publication-style review remains for
  Phase 4.7.

## 9. Automatic DOCX Validation

- ZIP integrity: PASS.
- WordprocessingML/XML parse integrity: PASS.
- OpenXML validator equivalent: unavailable in the environment.
- Reference DOCX inspector: PASS.
- Custom Full DOCX validator: PASS.
- Required section/front-matter checks: PASS.
- Figure/table presence and frozen-content checks: PASS.
- Citation/cross-reference source check: PASS; unresolved keys 0.
- Obvious broken figure/table references: none detected mechanically.
- Duplicate title/abstract sections: none detected.
- Repair/error state: none detected mechanically.
- Microsoft Word visual inspection: `MANUAL_WORD_REVIEW_PENDING`.

## 10. Scientific Freeze

- Six core results unchanged: YES.
- Contribution count = 2: YES.
- Excluded evidence restored: NO.
- New statistic: NO.
- Frozen values verified in DOCX: `2.236671×`, `55.4519%`, `4.0738%`,
  `4.0349%`, `0.1514%`, and `0.1184%`.
- V4, historical Attempt 2 restoration, cross-stage acceleration
  multiplication, statistical significance claim, and V3R independent
  task-level Gate D were not added.

## 11. Publication Limitations

- Corresponding-author email remains pending and is omitted from this Full
  draft.
- CSL/journal bibliography styling remains a Phase 4.7 review item.
- Figure 1 Word placement/readability remains pending.
- Figure 2/3 font fallback remains pending.
- Final pagination, rule appearance, font consistency, and page-number review
  require Microsoft Word visual inspection in Phase 4.8/4.9.

## 12. Recommendation

PHASE_4_6_READY
