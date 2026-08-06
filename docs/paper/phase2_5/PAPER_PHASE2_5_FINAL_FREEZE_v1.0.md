# Paper Phase 2.5 Final Freeze Record v1.0

Freeze date: 2026-08-06

## 1. Verdict

`PHASE_2_5_COMPLETE_WITH_ACCEPTED_PUBLICATION_LIMITATIONS`

This record freezes the Paper Phase 2.5 authoring toolchain and publication
workflow administration. It does not authorize formal Phase 3 manuscript
drafting.

## 2. Freeze Scope

This freeze covers:

- the Markdown manuscript source contract and structure-only source skeleton;
- the Pandoc Markdown-to-DOCX build capability;
- the controlled `reference.docx` candidate;
- Full and Anonymous build variants;
- OpenXML validation, custom inspection, format-regression, citation, source,
  asset, and identity-scan capabilities;
- the recorded governance-drift and journal-format manifests; and
- the Microsoft Word manual-acceptance boundary.

This is not:

- final journal submission completion;
- completion of the manuscript body;
- completion of final MathType processing;
- completion of all formal Origin/Visio figures;
- completion of final real-manuscript pagination;
- completion of the final Word Document Inspector pass; or
- a declaration that every publication artifact is submission-ready.

## 3. Authority Basis

### Phase 2 authority

- Phase 2 Final Freeze:
  `docs/paper/phase2/PAPER_PHASE2_FINAL_FREEZE_v1.0.md`.
- Phase 2 freeze commit: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`.
- Phase 2 annotated tag: `paper-phase2-complete-v1.0`, peeled commit
  `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`.

### Phase 2.5 implementation and repair history

The Phase 2.5 baseline and subsequent repository evidence are the reviewed
commits in the following sequence:

- `60e90b28e2588d9ba0f3a2a1224cd057389c852e` — reference DOCX candidate;
- `b7695789b151ddc8c20593e0ed06da9d32be2a77` — structure-only manuscript
  source skeleton;
- `6cc775d456342ac9660bafb00047e749fb17fcbc` — Markdown-to-DOCX POC;
- `4cbc73e725b90adf181bbfdd205420a37e31da8c` — Word DOCX compatibility
  remediation;
- `17b7f4bb04914b3b83da738e3efe2e0bf772e44d` — first-open and equation
  layout remediation;
- `f39d03571e94c144a0a8f3ebfb2c5efc7d7bd795` — remaining v3 compatibility
  remediation;
- `8f3587a43ca8f228f62b6b66dc4f08401ce029b7` — OPC content-type ordering;
- `623ec31a9afc60e9c2129bd798a7a634dc6552eb` — canonical OOXML validation
  and repair;
- `2b26f219319c27c94582003e9a0ea232f6dcc000` — journal-format regression
  audit; and
- `23354bde4136806f4140576cf6dd906717b8d591` — current pre-freeze HEAD and
  Phase 2.5 format-contract reconciliation.

The current freeze-before-commit HEAD is
`23354bde4136806f4140576cf6dd906717b8d591`.

### Phase 2.5 evidence

The principal evidence is recorded in:

- `PAPER_PHASE2_5_REFERENCE_DOCX_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_MARKDOWN_DOCX_POC_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_OPENXML_VALIDATOR_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_WORD_COMPATIBILITY_REMEDIATION_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_JOURNAL_FORMAT_REMEDIATION_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_ANONYMOUS_METADATA_DIAGNOSIS_v1.0.md`;
- `PAPER_PHASE2_5_EQUATION_LAYOUT_DIAGNOSIS_v1.0.md`;
- `PAPER_PHASE2_5_STEP5_SOURCE_SKELETON_REPORT_v1.0.md`;
- `PAPER_PHASE2_5_JOURNAL_FORMAT_REGRESSION_MATRIX_v1.1.csv`;
- `PAPER_PHASE2_5_GOVERNANCE_DRIFT_REGISTER_v1.1.csv`;
- `PAPER_PHASE2_5_CSL_SOURCE_MANIFEST_v1.0.csv`; and
- `PAPER_PHASE2_5_DOC_CONVERSION_MANIFEST_v1.0.csv`.

### External acceptance fact

`EXTERNAL_USER_MANUAL_ACCEPTANCE`: on 2026-08-06, the user confirmed that
final Word v7 manual checking passed. This record preserves that fact without
inventing a Word build number, page-by-page result, object-level visual result,
Document Inspector result, MathType result, Origin/Visio result, pagination
result, or final Anonymous identity-cleanup result.

## 4. Entry-condition Closure

| Entry condition | Closure | Basis and boundary |
|---|---|---|
| Official input verification | `CLOSED_WITH_ACCEPTED_LIMITATIONS` | Archived input, specification, source, style, and conversion manifests are present. CSL HFUT-special-rule conformance remains a publication limitation. |
| Toolchain proof of concept | `CLOSED_WITH_ACCEPTED_LIMITATIONS` | Full and Anonymous POC build and inspection evidence is recorded in the Markdown DOCX POC report and remediation report. |
| OpenXML/custom validation | `CLOSED` | Canonical reference, Full, and Anonymous package validation evidence records zero OpenXML errors and custom-inspector success for the frozen candidates. |
| Full build capability | `CLOSED_WITH_ACCEPTED_LIMITATIONS` | Full variant capability is demonstrated by the recorded POC; it is not a final real-manuscript submission build. |
| Anonymous build capability | `CLOSED_WITH_ACCEPTED_LIMITATIONS` | Anonymous variant capability is demonstrated by the recorded POC; final Word-save metadata cleanup remains required. |
| Windows Word manual acceptance | `CLOSED_AS_EXTERNAL_USER_FACT` | `EXTERNAL_USER_MANUAL_ACCEPTANCE` only; no unprovided detailed Word facts are inferred. |
| Governance-drift closure | `CLOSED` | Governance drift register v1.1 marks GDR-001 through GDR-004 closed; regression matrix v1.1 has no automatic blocking audit item. |

The structure-only manuscript source remains explicitly `PHASE_3_NOT_AUTHORIZED`
and contains no formal manuscript prose, fabricated citation, result number,
or conclusion text.

## 5. Frozen Assets

The following SHA256 values were verified immediately before this record was
created.

| Asset | SHA256 |
|---|---|
| `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx` | `416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7` |
| `docs/paper/phase2/PAPER_PHASE2_FINAL_FREEZE_v1.0.md` | `0cf77a31ade510231f89fe3b106f334a8ad1d5f63ff7d1b60bba3e227a542a96` |
| `docs/paper/phase2/PAPER_PHASE2_RESEARCH_NARRATIVE_v1.0.md` | `9030559515b206ddb907c03f83df9dd40a47a1998252d149b5b77539ca41b522` |
| `docs/paper/phase2/PAPER_PHASE2_ARTICLE_OUTLINE_v1.0.md` | `66d3e35e397b3265b31ce4506c0fe5593a5d0a88220287581c151922b0676896` |
| `docs/paper/phase2/PAPER_PHASE2_CLAIM_ARCHITECTURE_v1.0.csv` | `b4e6f06a42a4e6ec452264847964cbee29449012c7b43262fe04e73922ffae7a` |
| `docs/paper/phase2/PAPER_PHASE2_FIGURE_TABLE_PLAN_v1.0.csv` | `ebfd42c1b24b56f067516282d32ae532a39b2f0a6fce18c9f5334bc90b1002da` |
| `docs/paper/phase2/PAPER_PHASE2_WRITING_PACKETS_v1.0.md` | `bb4496cced9bbe8ffa260df006ff81670e088260326f63f6f862d878640acf34` |
| `docs/paper/phase2_5/PAPER_PHASE2_5_JOURNAL_FORMAT_REGRESSION_MATRIX_v1.1.csv` | `79c6eed286f87dd2061071d63160e6c35ded833ab0476df15ffaac85d10861c7` |
| `docs/paper/phase2_5/PAPER_PHASE2_5_GOVERNANCE_DRIFT_REGISTER_v1.1.csv` | `c33e5d6aa1bf2d6161a920c5343c6e3724e67ef6a9758ce9f8d4ecbd76c632a8` |
| `scripts/paper/run_phase2_5_docx_poc.sh` | `2c1dea71221473c2dd2366da356b96160f89f00d41d5402daf5b6872108f9080` |
| `scripts/paper/postprocess_phase2_5_poc_docx.py` | `03a0bc56892fbb9f543a2ac34745fc87cb70b85abcf7ab460c527c1ed2c47e63` |
| `scripts/paper/inspect_phase2_5_poc_docx.py` | `406dd06391aaa0e5dff30559c6b5c7e1868848f56920fbb78567f2c0017d76de` |
| `scripts/paper/build_manuscript_docx.sh` | `f073fc303216f814719d36be647a23731c76780e626f0474bc82b84480bfb19a` |
| `scripts/paper/validate_manuscript_sources.py` | `debb3283d1935aaaafab16b2cb408abcb586b8f5bfbe8f523690fb989039000a` |
| `scripts/paper/validate_citations.py` | `5ed80dcd6b1b8f2e4cce14d0b8b49510fc338cce1730450d7183376b41dfc2de` |
| `scripts/paper/validate_manuscript_assets.py` | `453ba2478be21f9c43faed255b32ab49d2d7e02d727e351d82d8cf444b840414` |

The Phase 2 Final Freeze record's self-referential hash is intentionally not
used as an authority value; its governing commit and annotated tag are the
authority.

## 6. Accepted Publication Limitations

The following remain accepted publication items:

1. MathType finalization is not complete.
2. Formal Visio/Origin figures are not all complete.
3. The dedicated CSL rule for standard literature type `[S]` still requires
   final revision.
4. Dynamic cross-references still require final handling.
5. Real-manuscript pagination still requires checking.
6. Document Inspector has not been executed after the final Word save.
7. Final Anonymous identity cleanup has not been executed.
8. The visual state of figures, tables, equations, and references under the
   formal manuscript body still requires a later milestone check.

These are publication items. They do not block Phase 3 manuscript production,
subject to the separate final authorization review stated below.

## 7. Prohibited Reopening

This freeze prohibits, without a later explicit authorization:

- reopening template-platform development;
- creating v8/v9 compatibility candidates;
- changing Phase 1 values;
- changing Phase 2 narrative or claims;
- adding experiments;
- directly generating the complete paper;
- treating DOCX as the sole manuscript source; and
- changing the frozen journal-format rules by implication.

## 8. Phase 3 Handoff

```text
Paper Phase 3 Entry Review:
READY_FOR_FINAL_AUTHORIZATION_REVIEW

Formal manuscript drafting:
NOT SELF_AUTHORIZED_BY_THIS_RECORD
```

This record does not declare `PHASE_3_AUTHORIZED`.
