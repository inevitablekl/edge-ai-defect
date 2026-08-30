# Paper Phase 7.4-J 投稿资产包审计与冻结报告 v1

## 1. 审计结论

```text
PACKAGE_AUDIT = PASS_WITH_WARNINGS
CORE_SUBMISSION_ASSETS = COMPLETE
PACKAGE_FREEZE = PASS
SCIENTIFIC_CONTENT_MODIFIED = NO
```

投稿资产包已包含本阶段要求的四类核心归档对象：最终 Full Word
原稿、图1原生 Visio VSDX、图2最终 Origin OPJU 以及图3最终
Origin OPJU。用户已明确确认两个 `MASTER_WORKING.opju` 为实际最终采用
版本，本报告与 JSON 清单将其固定为权威资产。

本阶段未修改论文文字、数值、公式、图形、参考文献、Word 格式、
Visio 对象或 Origin 对象。

## 2. 最终权威资产

| 角色 | 最终文件 | 状态 |
|---|---|---|
| `FULL_MANUSCRIPT` | `Jetson端工业缺陷检测的输入数据路径重构.doc` | FINAL |
| `FIGURE_1` | `Figure1_input_data_path_model.vsdx` | FINAL |
| `FIGURE_2` | `Figure2_MASTER_WORKING.opju` | FINAL / USER CONFIRMED |
| `FIGURE_3` | `Figure3_MASTER_WORKING.opju` | FINAL / USER CONFIRMED |
| `PDF` | 未包含 | WARNING |
| `ANONYMOUS_MANUSCRIPT` | 未包含，后续派生 | EXPECTED LATER DERIVATIVE |

## 3. Word 原稿完整性

- 文件是有效的 Microsoft Word 97–2003 OLE Compound File。
- Word 文档元数据记录页数为 7 页。
- 检测到 3 个 Word 原生表格；项目政策不要求独立 Excel 表格源。
- 参考文献列表包含 `[1]`–`[22]`。
- 检测到 54 个 `MathType 7.0 Equation` OLE 对象。
- 检测到 1 个嵌入 Visio 对象和 2 个嵌入 Origin 对象。
- MathType 状态为
  `MANUAL_WINDOWS_VALIDATION_PREVIOUSLY_REQUIRED / STRUCTURAL_OLE_PRESENT`。

Linux LibreOffice 的临时转换可以读取文档，但 Linux 字体和分页不代替
Microsoft Word 人工分页验收；最终 7 页状态以用户完成的 Windows Word 原稿
及文档元数据为准。

## 4. 图1 VSDX 完整性

- `file` 识别为 `Microsoft Visio 2013+`。
- ZIP/OOXML 包完整性测试通过，无损坏成员。
- `[Content_Types].xml`、关系文件、`visio/document.xml`、页面索引和
  `visio/pages/page1.xml` 均存在。
- 11 个 XML/关系文件全部可解析。
- 检测到 47 个原生 Visio 形状和 24 个非空文本节点。
- `P₀ / V0`、`P₂ / V2R`、`P₃ / V3R`、`Pageable`、`Pinned`、主机域、
  设备域、主机—设备边界以及两级干预说明均存在。
- 包含缩略图但主体为原生形状，不是重命名图片或单一嵌入 SVG。

## 5. 图2、图3 OPJU 完整性

两个文件均为非零大小，具有 Origin OPJU 的 `CPYUA` 文件头和
`PrvwOPJU` 标记。

图2项目包含：

- `F2_Panel_A`、`F2_Panel_B`、`F2_Panel_C` 数据/图层标记；
- FPS、平均 E2E 延迟、P95/P99 图层和权威显示值；
- `54.600`、`122.122`、`127.097`、`18.273`、`8.140`、`7.812` 等冻结标签。

图3项目包含：

- `F3_Run_Level_Data` 工作表结构；
- V0/V2R/V3R 进程级 FPS 点、汇总和 V2R/V3R 延迟图层标记；
- `Process P95`、`Process P99` 及尾延迟注释结构。

Linux 结构检查不代替 Origin Desktop 的最终视觉检查；用户已确认这两个
OPJU 是实际采用的最终版本。

## 6. 支持资产和重复/过期检查

- 图1 PNG、SVG、几何 JSON、文本 CSV、Visio 规范和 PowerShell 构建源文件
  均可读。
- 六个图1支持文件与仓库 Windows bundle 权威副本逐字节相同。
- 投稿包内未发现相同 SHA256 的重复 payload。
- 未发现明确的 `FAILED`、`DIAGNOSTIC` 或 `BACKUP` 资产。

## 7. 非阻塞性警告

1. 匿名/送审稿尚未包含，按当前流程归类为后续派生文件。
2. 图2、图3未单独提供 PNG/PDF/SVG 预览；OPJU 本身及 Word 嵌入对象已存在。
3. 未包含最终 PDF；当前提交权威是人工验收的 Word 原稿。
4. 目录名仍保留用户提供的 `(未完成)` 后缀；实际冻结状态由本报告和
   `SUBMISSION_ASSET_MANIFEST_v1.json` 界定。

上述项目不影响当前四类核心归档对象的完整性结论。

## 8. 冻结与校验规则

- `SUBMISSION_ASSET_MANIFEST_v1.json` 记录 payload 完整清单、大小、时间戳和 SHA256。
- `SHA256SUMS.txt` 覆盖全部 payload、JSON 清单和本审计报告。
- `SHA256SUMS.txt` 不包含它自身，以避免自引用校验。
- 冻结后任何二进制资产变化都必须重新审计并更新清单。
