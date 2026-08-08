# Paper Phase 4 Final Table Integration

## 1. Verdict

PHASE_4_FINAL_TABLE_STRUCTURE_READY

## 2. Existing Workflow Assessment

- Pandoc table behavior: Pandoc emits the manuscript tables with the generic
  `Table` paragraph style and no direct `w:tblBorders`; Pandoc alone does not
  produce the required three-line structure.
- reference.docx table style: `HFUTThreeLineTable` is present and contains the
  journal-candidate top/bottom rules, header-rule style, disabled vertical
  rules, and table cell margins.
- postprocess behavior: the existing Phase 2.5 POC postprocessor already
  demonstrates direct three-line OOXML enforcement, but its synthetic rule is
  hard-coded for a three-column table and centers all cells.
- remediation required: YES
- implementation scope: the narrow
  `scripts/paper/postprocess_publication_tables.py` rule identifies the exact
  T1/T2 captions, applies the existing `HFUTThreeLineTable` style plus direct
  borders, assigns table-specific widths, and applies the required alignment.
  The future build command now invokes this postprocessor after Pandoc.

## 3. Table 1

- 17 rows preserved: YES
- title preserved: `表1　平台、模型、数据集和统一运行协议`
- three-line structure: VALIDATED_BY_ISOLATED_T1_T2_ARTIFACT
- vertical rules: ABSENT
- internal body gridlines: ABSENT
- scientific content changed: NO
- final Word visual inspection: DEFERRED

The two-column table keeps both columns left aligned in the body and permits
natural wrapping in the configuration column. Version strings, `640×640`, and
`split-v2` remain intact.

## 4. Table 2

- V0/V2R only: YES
- V3R absent: YES
- four metrics preserved: YES
- thresholds preserved: YES
- numeric precision preserved: YES
- three-line structure: VALIDATED_BY_ISOLATED_T1_T2_ARTIFACT
- vertical rules: ABSENT
- internal body gridlines: ABSENT
- scientific content changed: NO
- final Word visual inspection: DEFERRED

The four frozen rows retain `0.6913`, `0.6991`, `0.6476`, and `0.3523` for
both V0 and V2R, exact displayed integer `0` differences, and thresholds
`0.010`, `0.010`, `0.005`, and `0.005`.

## 5. Tooling Changes

- Added `scripts/paper/postprocess_publication_tables.py` for caption-keyed,
  T1/T2-only DOCX formatting.
- Updated `scripts/paper/build_manuscript_docx.sh` future build commands to
  run the dedicated postprocessor after Pandoc.
- Updated `scripts/paper/validate_manuscript_assets.py` to accept the
  publication-ready status for the two table-manifest rows while retaining
  the Phase 2 planned status for figures.

The legacy Phase 2 asset validator still reports pre-existing figure/status
and claim-binding assumptions outside this Phase 4 table gate; those findings
do not affect the direct T1/T2 source and isolated-DOCX checks above.

## 6. Scientific Freeze

- frozen protocol changed = NO
- frozen correctness data changed = NO
- V3R added to Table 2 = NO
- new metric/statistic = NO

## 7. Open Publication Items

- final Word typography/width;
- page-break visual inspection;
- final rule-weight/font appearance.

These belong to later Phase 4.8/4.9 review. The isolated validation artifact
was not treated as the formal Full manuscript or Anonymous manuscript.

## 8. Recommendation

PHASE_4_4_READY_TO_CLOSE
