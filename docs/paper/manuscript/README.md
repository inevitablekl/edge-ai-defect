# Manuscript Source

This directory contains the Markdown manuscript authority and the derived
authoring/publication assets established through Paper Phases 2.5 and 3.

## Source contract

- Markdown is the content authority before Word finalization.
- `reference.docx` is a derived format candidate, not a content source.
- Files under `output/` are generated candidates and are never manuscript
  source.
- The seven section files are built in their fixed numeric order.
- Citations will use Pandoc citation keys only; manual `[1]`, `[2]`, `[3]`
  maintenance is prohibited.
- Equations, figures, and tables require a corresponding manifest record.
- Any substantive Word change must be written back to Markdown or recorded in
  `governance/word_divergence_log.csv`.
- Real author contact details must not be committed to a public Git repository.
- External official DOC/PDF files must not be copied into this repository.

## Current boundary

Paper Phase 5.9C reconstructs the integrated manuscript around a fixed-object
input data-path model. The seven section files, three display equations, three
figures, three tables, and 22 rendered citations form the current scientific
source inventory. Full and Anonymous DOCX/PDF candidates are generated from
these Markdown sources through the existing HFUT format pipeline. MathType and
Visio/Origin submission conversions remain deferred until scientific approval;
the deterministic SVG/PNG and native Word-table route remains authoritative in
the interim.

## Fixed section order

1. `sections/00_title_abstract.md` — 题名与摘要
2. `sections/01_introduction.md` — 0 引 言
3. `sections/02_problem_definition.md` — 1 输入数据路径模型与问题表述
4. `sections/03_method.md` — 2 受控输入数据路径重构
5. `sections/04_experiment.md` — 3 实验协议
6. `sections/05_results.md` — 4 结果与分析
7. `sections/06_conclusion.md` — 5 结论

Writing Packet identifiers used by the skeleton are stable local labels that
map one-to-one to the seven packets in
`docs/paper/phase2/PAPER_PHASE2_WRITING_PACKETS_v1.0.md`.
