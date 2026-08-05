# Paper Phase 2.5 Manuscript Source Contract v1.0

## Status

This contract governs the Paper Phase 2.5 Step 5 Markdown, bibliography, and
manuscript-source skeleton. It establishes source structure only. The current
state is `TOOLCHAIN_SKELETON_ONLY`; `PHASE_3_NOT_AUTHORIZED` remains in force.

## 1. Authority model

Before Word finalization, Markdown is the content authority. BibTeX is the
verified literature metadata exchange source. Equation, figure, and table CSV
manifests are the structured asset authorities. The supplied
`template/hfut_journal_reference_v1.0.docx` is a format candidate only. After
final submission layout is authorized, `final_submission.docx` may become the
submission authority, subject to the divergence policy below.

The frozen Phase 2 outline, claim architecture, figure/table plan, writing
packets, literature requirements, final freeze, and Phase 2.5 format inputs are
read-only authorities for this skeleton. They are not copied into manuscript
sections as prose.

## 2. Directory contract

`docs/paper/manuscript/` contains seven ordered Markdown sections,
non-identity metadata, a header-only literature matrix and BibTeX library,
empty equation manifest, planned figure/table manifests, data-boundary notes,
candidate Pandoc configuration, a Word divergence log, and a Git-ignored
output directory. The existing reference template remains unchanged.

## 3. Chapter ordering

The build order is fixed and numeric:

1. title and abstract;
2. `0` introduction;
3. `1` system object and problem definition;
4. `2` data-path optimization method;
5. `3` experiment design;
6. `4` results and analysis;
7. `5` conclusion.

Every current section is `STRUCTURE_ONLY`, `NO_MANUSCRIPT_PROSE`, and
`PHASE_3_NOT_AUTHORIZED`. Only status comments, packet mapping, claim IDs,
planned asset IDs, frozen headings, and a content-pending marker are allowed.

## 4. Metadata and privacy boundary

`metadata_common.yaml` contains non-identity placeholders and explicit phase
status. `metadata_private.example.yaml` documents field structure with obvious
placeholders only; a local `metadata_private.yaml` is ignored by Git.
`metadata_anonymous.yaml` hides authors, affiliations, funding, biography,
acknowledgements, and contact fields. It does not claim that Word Document
Inspector anonymization has passed. Real identity and contact information must
not be committed to a public repository.

## 5. Citation contract

Future source citations use stable, unique Pandoc citation keys and are rendered
in sequential numeric order by the later citation workflow. Manual `[1]`,
`[2]`, `[3]` maintenance is prohibited. Step 5 contains zero bibliography
entries, zero Markdown citation keys, and zero unresolved citations. CSL is
explicitly `PENDING_STEP6_POC`.

## 6. Literature matrix contract

`references/literature_matrix.csv` is header-only until a real source has been
found, opened, read, and verified. Each future row must record metadata,
requirement coverage, supported statements, limitations, prohibited uses,
verification, full-text availability, and reading status. Visual reference
papers do not enter automatically, and no fabricated or toolchain-test entry is
permitted.

## 7. Equation contract

`equations/equation_manifest.csv` is header-only in Step 5. A later equation
must have a stable ID, section, semantic formula, LaTeX source, variable and
unit rules, claim/metric provenance, cross-reference key, and lifecycle status.
The allowed lifecycle statuses are `PLANNED`, `SOURCE_DEFINED`,
`POC_VALIDATED`, `WORD_INSERTED`, and `FINAL_VERIFIED`. MathType remains a
later manual/POC concern; no equation asset is created here.

## 8. Figure contract

The manifest contains exactly the three frozen formal candidates `F1`, `F2`,
and `F3`, with Phase 2 claim bindings and source experiment/metric provenance.
All are `PLANNED_FROM_PHASE2`. F1 records Visio as a later candidate; F2/F3
record deterministic Python preview and Origin as a later publication
candidate. None is claimed to have been created. No numeric result or image is
copied into this skeleton, and V3R must not be represented as cross-frame
overlap.

## 9. Table contract

The manifest contains exactly the two frozen formal candidates `T1` and `T2`,
with Phase 2 claim bindings and source provenance. Both are
`PLANNED_FROM_PHASE2`. The manifest records three-line-table intent and missing
value semantics but contains no experimental values. Future data must come from
Phase 1 frozen assets and pass provenance validation.

## 10. Build contract

`config/pandoc_common.yaml` is the common candidate configuration and points to
the unchanged reference template, source resource paths, common metadata, and
empty BibTeX library. CSL is not supplied. The full and anonymous YAML files
are composition profiles expressed as comments; no unsupported defaults
inheritance is assumed. A future build script may combine common settings with
the selected identity boundary.

`build_manuscript_docx.sh` currently supports only `--check`, `--show-order`,
and `--show-command`. It never performs a DOCX build in Step 5. Running it
without an argument stops with `PHASE2_5_POC_NOT_AUTHORIZED_BY_THIS_STEP`.

## 11. Output and Git policy

`output/` ignores all generated files except `.gitignore`. No DOCX, PDF,
temporary figure/table asset, or build log is generated in Step 5. External
official DOC/PDF payloads and real contact information remain outside this
repository. Large datasets, models, engines, videos, and generated logs remain
outside the skeleton unless separately authorized.

## 12. Word divergence policy

Before finalization, substantive Word edits must be synchronized back to
Markdown. If synchronization is not possible, record one row in
`governance/word_divergence_log.csv` with the DOCX version, section, change,
reason, author, Markdown status, commit, and resolution. No virtual historical
row is added in Step 5.

## 13. Phase 3 authorization boundary

Phase 3 is not authorized. This change does not authorize formal manuscript
prose, bibliography population, equation insertion, figure/table generation,
Markdown-to-DOCX POC, final DOCX production, new experiments, or a claim that
the toolchain is journal-compliant.

## 14. Prohibited actions

Do not fabricate literature, claims, metrics, figures, tables, author data,
journal parameters, CSL paths, or Word acceptance results. Do not modify the
frozen template or Phase 0/1/2/2.5 authority files. Do not rerun benchmarks,
enter unsupported values, create Origin/Visio/MathType assets, or treat output
DOCX as source.
