# Manuscript Source Skeleton

This directory is the Paper Phase 2.5 Step 5 authoring-toolchain skeleton.
It contains structure and source-governance assets only. Phase 3 is not
authorized.

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

All section files are `STRUCTURE_ONLY`, `NO_MANUSCRIPT_PROSE`, and
`PHASE_3_NOT_AUTHORIZED`. The bibliography and literature matrix are empty
until a later, verified literature workflow. No DOCX/PDF build is authorized
by this step.

## Fixed section order

1. `sections/00_title_abstract.md` — 题名与摘要
2. `sections/01_introduction.md` — 0 引言
3. `sections/02_problem_definition.md` — 1 系统对象与问题定义
4. `sections/03_method.md` — 2 数据路径优化方法
5. `sections/04_experiment.md` — 3 实验设计
6. `sections/05_results.md` — 4 结果与分析
7. `sections/06_conclusion.md` — 5 结论

Writing Packet identifiers used by the skeleton are stable local labels that
map one-to-one to the seven packets in
`docs/paper/phase2/PAPER_PHASE2_WRITING_PACKETS_v1.0.md`.
