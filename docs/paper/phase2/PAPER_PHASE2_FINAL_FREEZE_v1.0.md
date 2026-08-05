# Paper Phase 2 Final Freeze v1.0

## 1. Final Status

- Paper Phase 2: `COMPLETE`
- Independent review: `CONDITIONAL_PASS_WITH_MINOR_CLOSED`
- F1: `CLOSED`
- Open findings: `0`
- Paper Phase 2.5: `AUTHORIZED`
- Paper Phase 3: `NOT_AUTHORIZED`

## 2. Freeze Authorization

The eight Phase 2 writing-preparation assets and the review-disposition record
are frozen for use as the controlled inputs to Paper Phase 2.5. The freeze does
not authorize manuscript drafting, new experiments, changes to Phase 1 data, or
changes to the Phase 2 research narrative.

Phase 1 change request required: `NO`.

## 3. Authority Basis

This freeze is based on:

- the authoritative Phase 1 freeze at annotated tag
  `paper-phase1-complete-v1.0`;
- the Phase 1 claim-evidence map and gap register;
- the initial Phase 2 architecture commit
  `4e2b1266663c08ae53ef025cfa2d96f42f5f8272`;
- the external independent-review verdict `CONDITIONAL_PASS`, with zero
  blockers, zero major findings, one minor finding, and one note;
- the F1 remediation commit
  `c499df6e63f5199cb15cf54a8f1ce7c68389147f`;
- the exact closure record in
  `PAPER_PHASE2_REVIEW_DISPOSITION_v1.0.md`;
- the eight existing Phase 2 writing-preparation assets listed in Section 15.

The independent review originated in an external AI review interaction. The
review-disposition file records closure and does not purport to be the original
full independent-review report.

## 4. Frozen Research Question

Under the frozen Jetson platform, INT8 Engine, industrial defect detection
model, replay workload, correctness contract, and common timing boundary, how
do CPU preprocessing, CUDA preprocessing with pageable host staging, and CUDA
preprocessing with pinned host staging affect frame rate, mean latency, and
tail latency?

## 5. Frozen Core Contributions

Exactly two core contributions are frozen:

1. **Controlled data-path ablation under one boundary.** Establish a
   reproducible V0/V2R/V3R comparison using one frozen platform, model, INT8
   Engine, test workload, correctness contract, timing interval, and run
   protocol. This is an engineering measurement and evidence boundary, not a
   new neural-network, quantization, resize, or CUDA algorithm.
2. **Average-performance and tail-latency trade-off.** Show that V2R supplies
   the main observed average-performance benefit, whereas V3R supplies only a
   limited incremental FPS and mean-latency benefit. The V3R tail behavior is
   mixed: P95 is slightly higher and P99 is slightly lower than V2R, so the
   evidence does not establish a consistent tail-latency benefit.

No third A-level contribution is admitted.

## 6. Frozen Article Structure

```text
0 引言

1 系统对象与问题定义
  1.1 工业缺陷检测部署对象
  1.2 INT8推理数据路径
  1.3 研究问题与统一计时边界

2 数据路径优化方法
  2.1 CPU预处理基线路径
  2.2 CUDA预处理路径
  2.3 Pinned内存数据路径
  2.4 正确性约束与资源生命周期

3 实验设计
  3.1 实验平台与模型配置
  3.2 数据集与统一运行协议
  3.3 正确性和性能指标

4 结果与分析
  4.1 正确性验证结果
  4.2 CUDA预处理的主要性能收益
  4.3 Pinned内存的增量收益
  4.4 尾延迟与适用范围讨论

5 结论
```

This is an engineering-article structure, not a J-to-R stage chronology, a
thesis outline, or manuscript prose.

## 7. Frozen Claim Architecture Summary

The claim architecture contains nine records:

- Core: `A1->C1`, `A2->C2`, `A3->C3`.
- Supporting: `A4->C4` as protocol-local Stage Q prerequisite context.
- Supporting limitation/disclosure: `A5->C8`.
- Background/limitation only: `B1->C5`, `B2->C6`, `B3->C7`.
- Required guardrail: `G1->C9`.

F1 closure is part of the frozen architecture:

- `A4.figure_or_table = NONE`;
- `T1.claim_ids = A1;A5`;
- `T2.claim_ids = A1;A2;A3`;
- Q6 metrics `M_Q_SERIAL_INFERENCE_SPEEDUP` and
  `M_Q_SERIAL_THROUGHPUT_RATIO` remain protocol-local prerequisite context in
  the Writing Packet and do not create an independent Stage Q result line.

## 8. Frozen Figure/Table Plan

Five candidates are frozen at the planning/input level:

| ID | Type | Frozen purpose | Claim binding |
|---|---|---|---|
| `F1` | Schematic | V0/V2R/V3R data paths and common timing boundary | `A1;A2;A3;G1` |
| `T1` | Table | Platform, model, dataset, and common run protocol | `A1;A5` |
| `T2` | Table | Task-level correctness and V3R identity evidence | `A1;A2;A3` |
| `F2` | Bar chart | V0/V2R/V3R mean frame-rate comparison | `A1;A2;A3` |
| `F3` | Grouped bar chart | V0/V2R/V3R mean and tail-latency comparison | `A1;A2;A3` |

No figure, table, plotting script, preview, or manuscript result asset is
created by this freeze. Official width, font, DPI, line-weight, and table-rule
parameters remain pending.

## 9. Frozen Writing Packet Set

Seven evidence-aware writing packets are frozen:

1. `题名与摘要`
2. `0 引言`
3. `1 系统对象与问题定义`
4. `2 数据路径优化方法`
5. `3 实验设计`
6. `4 结果与分析`
7. `5 结论`

They remain planning assets. They are not completed abstract, introduction,
results, conclusion, or other manuscript body text.

## 10. Journal Requirement Status

The official submission-guide page and download-list metadata support the
verified web requirements already recorded in
`PAPER_PHASE2_JOURNAL_REQUIREMENTS_v1.0.md`, including the general title,
bilingual front matter, abstract, keyword, length, recent-work, abbreviation,
quantity/unit, figure/table, three-line-table, reference, Word-file, and
anonymous-review requirements.

The four official attachment payloads were not obtained or archived in the
repository. Their current status is:

```text
OFFICIAL_SOURCE_FILES_NOT_YET_ARCHIVED
SOURCE_VERIFICATION_PENDING_PHASE_2_5
```

No attachment filename, file type, exact byte count, SHA256, or detailed
typesetting parameter is treated as verified by this freeze.

The following specific terms or parameters are not newly accepted as verified
facts here: MathType, Visio, Origin, GB/T 7714—2025, exact font family/size,
figure width, figure-text size, three-line-table rule width, and reference line
spacing. Their status is:

```text
User-provided workflow planning input;
formal source verification deferred to Phase 2.5.
```

## 11. Accepted Input Gaps

The following gaps are accepted for Phase 2 completion but remain gates for
later work:

- the four official format/reference/figure/table source attachments are not
  archived or hash-verified;
- detailed Word style, figure, table, equation, and reference formatting
  parameters remain unverified;
- literature requirements `L1-L9` remain search-and-verification requirements,
  not a fabricated bibliography;
- the final title, English title, keywords, and manuscript text are not frozen;
- figure/table rendering and Word submission files have not been created or
  manually accepted.

These are input/toolchain gaps, not requests for new experiments or changes to
the Phase 1 evidence freeze.

## 12. Prohibited Phase 3 Statements

Until Phase 3 is explicitly authorized, do not:

- claim that the authoring toolchain complies with the journal's detailed
  format requirements;
- claim that unavailable official attachments were archived, parsed, or
  verified;
- present MathType, Visio, Origin, GB/T 7714—2025, exact typography, figure
  dimensions/text size, table-rule width, or reference spacing as verified
  official facts without direct source verification;
- produce formal long-form manuscript prose;
- add a third contribution, a new result storyline, a new experiment, or a
  new metric;
- alter Phase 1 evidence or the Phase 2 research narrative;
- fabricate literature, journal requirements, experimental results, figures,
  or tables;
- multiply independent J/K/Q/P/R protocol ratios or infer a total-system
  acceleration factor.

## 13. Phase 2.5 Authorization

Authorized phase:

```text
Paper Phase 2.5
Authoring Toolchain and Publication Workflow Freeze
论文写作工具链与出版流程冻结
```

Phase 2.5 is authorized only for:

- official format-input archiving and deduplication;
- requirement extraction;
- controlled `.doc` to `.docx` conversion;
- Word style inspection;
- `reference.docx` production;
- Markdown/BibTeX project scaffolding;
- Markdown-to-DOCX toolchain proof of concept;
- preparation for manual Windows Word acceptance.

Phase 2.5 does not authorize formal long-form manuscript writing, new
experiments, Phase 1 data changes, Phase 2 narrative changes, fabricated
journal requirements, or an early claim of journal-compliant tooling.

## 14. Phase 3 Entry Conditions

Paper Phase 3 remains `NOT_AUTHORIZED`. It may be authorized only after all of
the following are complete:

1. official input verification;
2. toolchain proof-of-concept pass;
3. manual Windows Word acceptance pass;
4. final authoring-toolchain freeze.

## 15. Frozen File Hashes

SHA256 values were computed deterministically with `sha256sum`:

| Frozen file | SHA256 governance |
|---|---|
| `PAPER_PHASE2_JOURNAL_REQUIREMENTS_v1.0.md` | `a96d7d24cfa05475c671eabcdd8893882d763146d3b71f2f8b2b6275a86e39bd` |
| `PAPER_PHASE2_RESEARCH_NARRATIVE_v1.0.md` | `9030559515b206ddb907c03f83df9dd40a47a1998252d149b5b77539ca41b522` |
| `PAPER_PHASE2_ARTICLE_OUTLINE_v1.0.md` | `66d3e35e397b3265b31ce4506c0fe5593a5d0a88220287581c151922b0676896` |
| `PAPER_PHASE2_CLAIM_ARCHITECTURE_v1.0.csv` | `b4e6f06a42a4e6ec452264847964cbee29449012c7b43262fe04e73922ffae7a` |
| `PAPER_PHASE2_FIGURE_TABLE_PLAN_v1.0.csv` | `ebfd42c1b24b56f067516282d32ae532a39b2f0a6fce18c9f5334bc90b1002da` |
| `PAPER_PHASE2_WRITING_PACKETS_v1.0.md` | `bb4496cced9bbe8ffa260df006ff81670e088260326f63f6f862d878640acf34` |
| `PAPER_PHASE2_LITERATURE_REQUIREMENTS_v1.0.md` | `93b2447cb02b2efdc0ddd566746390f9bf36b6e0b43f377a89892bff801f5f7c` |
| `PAPER_PHASE2_WRITING_PREPARATION_REPORT_v1.0.md` | `b8d299a0d89a2fbb5a927c34b611df56bdd75fd4ded26b24f9bdacf673e15893` |
| `PAPER_PHASE2_REVIEW_DISPOSITION_v1.0.md` | `2594649f7dad7824419f1096371f7d607e62d0e0c179dcf0d47639b2fc7101b4` |
| `PAPER_PHASE2_FINAL_FREEZE_v1.0.md` | `SELF` — governed by the Git commit and annotated tag; no self-referential SHA256 is recorded. |

## 16. Git Freeze Marker

The authoritative Git marker for this freeze is:

- commit message: `docs(paper): freeze phase 2 writing preparation`;
- annotated tag: `paper-phase2-complete-v1.0`;
- annotated tag message:
  `Paper Phase 2 complete: article writing architecture frozen`.

The authoritative frozen commit is the commit peeled from the annotated tag.
The Phase 1 tag `paper-phase1-complete-v1.0` must remain an ancestor of that
commit. The final-freeze file itself is governed by this commit and annotated
tag rather than a self-referential SHA256.
