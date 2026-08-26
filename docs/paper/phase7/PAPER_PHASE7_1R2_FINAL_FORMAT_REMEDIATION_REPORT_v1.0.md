# Phase 7.1R2 final format remediation report

## Verdict

`PHASE_7_1R2_FORMAT_FIDELITY_CLOSED_WORD_CANDIDATE_SELECTION_REQUIRED`

The source-deterministic heading and reference-heading work is closed. No
scientific prose, result, protocol, reference metadata, figure data, or table
value changed. Microsoft Word Page-6 visual closure remains intentionally
open until the user selects a bounded candidate in Word 2019.

## Special titles

| Element | Final literal | Authority |
| --- | --- | --- |
| Introduction | `引  言` after `0␠␠` | HFUT_FMT_DOC P012 |
| Conclusion | `结  论` after `5␠␠` | HFUT_FMT_DOC P094 |
| Reference heading | `[参 考 文 献]` | HFUT_FMT_DOC P097 |

The title-internal spacing in `引  言` and `结  论` is independent of the
two literal spaces separating a heading number from its title.

## Actual heading-instance matrix

| Heading instance | Number | Number bold | Separator | Title literal | Title font | Title bold | Left indent | Source evidence | PASS/FAIL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Introduction | 0 | TRUE | two spaces | 引  言 | 黑体 14 pt | TRUE | 0 | P012 | PASS |
| 1 | 1 | TRUE | two spaces | 输入数据路径模型与问题表述 | 黑体 14 pt | FALSE | 0 | P015 | PASS |
| 1.1 | 1.1 | TRUE | two spaces | 固定推理对象与系统边界 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 1.2 | 1.2 | TRUE | two spaces | 路径描述符与名义复制载荷 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 1.3 | 1.3 | TRUE | two spaces | 层级受控比较、正确性条件与评价问题 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 2 | 2 | TRUE | two spaces | 受控输入数据路径重构 | 黑体 14 pt | FALSE | 0 | P015 | PASS |
| 2.1 | 2.1 | TRUE | two spaces | V0基线路径 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 2.2 | 2.2 | TRUE | two spaces | V2R路径级重构 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 2.3 | 2.3 | TRUE | two spaces | V3R暂存策略细化 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 2.4 | 2.4 | TRUE | two spaces | 共同控制与正确性约束 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 3 | 3 | TRUE | two spaces | 实验协议 | 黑体 14 pt | FALSE | 0 | P015 | PASS |
| 3.1 | 3.1 | TRUE | two spaces | 实验平台与模型配置 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 3.2 | 3.2 | TRUE | two spaces | 运行与正确性协议 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 3.3 | 3.3 | TRUE | two spaces | E2E、FPS与尾延迟指标 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 4 | 4 | TRUE | two spaces | 结果与分析 | 黑体 14 pt | FALSE | 0 | P015 | PASS |
| 4.1 | 4.1 | TRUE | two spaces | 正确性约束验证 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 4.2 | 4.2 | TRUE | two spaces | 路径级重构的E2E响应 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 4.3 | 4.3 | TRUE | two spaces | 暂存策略的增量响应 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 4.4 | 4.4 | TRUE | two spaces | 平均性能与尾延迟响应 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 4.5 | 4.5 | TRUE | two spaces | 解释边界与局限性 | 黑体 10.5 pt | FALSE | 0 | P016 | PASS |
| 5 Conclusion | 5 | TRUE | two spaces | 结  论 | 黑体 14 pt | FALSE | 0 | P094 | PASS |

The machine-readable source/actual-DOCX inventory is
`PAPER_PHASE7_1R2_ACTUAL_MANUSCRIPT_HEADING_INVENTORY_v1.0.csv`; it records
the exact run counts and `xml:space="preserve"` contract for all 21 instances.

## Reference-heading decision

R1's statement that no actual manuscript reference-heading specimen existed
was **YES, wrong**. `HFUT_FMT_DOC P097` was missed because cross-document
source-role classification did not identify the black manuscript-tail specimen
between conclusion prose and red reference instructions. See
`PAPER_PHASE7_1R2_REFERENCE_HEADING_AUTHORITY_RECONCILIATION_v1.0.md`.

## Verification

| Check | Result |
| --- | --- |
| Full DOCX build | PASS |
| Anonymous DOCX build | PASS |
| Source-format / structural validator | PASS |
| Run-level actual-heading validator | PASS, 21 headings |
| Reopened reference-heading validator | PASS |
| Equation validator | PASS |
| Scientific non-regression | PASS; manuscript prose delta 0 |
| Full/Anonymous parity | PASS |

`ALL_ACTUAL_HEADINGS_SOURCE_MATCH = YES`
`CONCLUSION_SOURCE_MATCH = YES`
`REFERENCE_HEADING_SOURCE_MATCH = YES`
`REFERENCE_BODY_SOURCE_MATCH = YES`
`RUN_LEVEL_FORMAT_SATURATION = YES`
`SCIENTIFIC_NONREGRESSION = PASS`

## Page-6 status

`PAGE6_BLANK = OPEN`

The root cause remains
`INTERACTION_BETWEEN_SOURCE_FORMAT_GEOMETRY_AND_PROJECT_FLOAT_MECHANISM`.
The deterministic R2 heading/reference fixes changed document geometry, so the
old R1 candidates were not reused. Candidate A (Figure-3 related-body offset
0) and Candidate B (offset 1) were regenerated from the final R2 Full raw
build. Their figure geometry and `tblpPr` properties are identical; only the
logical float anchor differs. No Candidate C was needed.

Open both candidates in Microsoft Word 2019 and inspect Pages 5–7. Select the
one with no large artificial Page-6 blank region, Figure 3 after its first
callout, reasonable narrative proximity, no new Page-5/Page-7 gap, no
figure/caption overlap, and no clipping. Do not select from LibreOffice.
