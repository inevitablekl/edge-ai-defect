# Table 2 Publication Specification v1.0

## 1. Publication identity

- Table: T2
- Title: `表2　V0与V2R任务级正确性验证结果`
- Columns: `指标 | V0 | V2R | 绝对差异 | 允许差异 | 结果`
- Claim IDs: A2
- Source experiments: R_V0;R_V2R
- Scientific content authority:
  `docs/paper/manuscript/sections/05_results.md`
- Final DOCX assembly: VSCODE_CODEX / BUILD_PIPELINE_READY
- Three-line-table rendering: VALIDATED_BY_ISOLATED_T1_T2_ARTIFACT
- Manual visual inspection: DEFERRED_TO_PHASE_4_9

## 2. Frozen table source

| 指标 | V0 | V2R | 绝对差异 | 允许差异 | 结果 |
|---|---:|---:|---:|---:|---|
| Precision | 0.6913 | 0.6913 | 0 | 0.010 | 通过 |
| Recall | 0.6991 | 0.6991 | 0 | 0.010 | 通过 |
| mAP50 | 0.6476 | 0.6476 | 0 | 0.005 | 通过 |
| mAP50-95 | 0.3523 | 0.3523 | 0 | 0.005 | 通过 |

## 3. Three-line-table construction

- Place the title above the table using the journal template's table-caption
  style.
- Use exactly three horizontal rules: one at the table top, one below the
  header row, and one at the table bottom. Do not use vertical rules or body
  row gridlines.
- Left align the metric labels. Center the result column. Align numeric
  columns consistently by decimal point or right edge.
- Preserve four decimal places for V0 and V2R, three decimal places for the
  allowed differences, and the exact displayed integer `0` for every absolute
  difference.
- Use the journal template's final typeface, size, line spacing, and rule
  weights; do not invent them before the official attachment settings are
  confirmed.

## 4. Content boundary

This table reports task-level correctness for V0 and V2R only. Do not add V3R,
digest fields, detection counts, raw-tensor or bitwise-equality statements,
additional metrics, or new thresholds. The companion-identity evidence for
V3R remains outside Table 2 and is not an independent task-level evaluation.

## 5. Manual completion checklist

- [ ] Only V0 and V2R appear as evaluated variants.
- [ ] All four metrics and frozen thresholds match Section 4.1.
- [ ] Three horizontal rules and no vertical rules are used.
- [ ] Numeric precision is preserved exactly.
- [ ] No identity evidence is presented as task-level correctness.
