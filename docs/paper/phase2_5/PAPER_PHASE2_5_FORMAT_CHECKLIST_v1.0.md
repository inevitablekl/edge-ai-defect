# Paper Phase 2.5 Format Checklist v1.0

## 1. Status

This checklist is for later Word acceptance. No item has been executed or
marked pass in Step 2.

Allowed current statuses are `PLANNED`, `PENDING_STEP3`, `PENDING_POC`,
`PENDING_WINDOWS_CHECK`, and `NOT_APPLICABLE`.

## 2. Checklist

| 检查项 | 规则ID | 检查阶段 | 自动检查或人工检查 | 所需软件 | 检查方法 | 通过条件 | 失败处理 | 状态 |
|---|---|---|---|---|---|---|---|---|
| 稿件构成完整 | HFUT-WEB-001 | SOURCE_WRITING | 混合 | text checker + editor | 对照必备字段清单 | 所有适用中英文前置字段、正文、参考文献和作者简介存在 | 补字段，不编造内容 | PLANNED |
| 中文题名长度 | HFUT-WEB-002; HFUT-FMT-001 | SOURCE_WRITING | 自动+人工 | Unicode count script | 统计汉字并人工检查中英数混排 | 不超过20个汉字且无无意副题名 | 缩短题名并重新语义审查 | PLANNED |
| 中英文题名语义和英文大小写 | HFUT-WEB-004; HFUT-FMT-008 | SOURCE_WRITING | 人工 | editor | 双语逐项比较 | 含义一致且英文大小写符合规则 | 修改英文题名并复审 | PLANNED |
| 作者和单位字段 | HFUT-FMT-002; HFUT-FMT-009 | SOURCE_WRITING | 混合 | editor | 核对二级单位、地域邮编和英文姓名 | 字段齐全并经作者确认 | 向作者核实并修正 | PLANNED |
| 中文摘要内容与长度 | HFUT-WEB-005; HFUT-WEB-006; HFUT-WEB-007; HFUT-FMT-004 | SOURCE_WRITING | 混合 | character counter + editor | 字数统计及四要素/禁用项检查 | 至少150字、以约300字为目标且满足写法要求 | 重写摘要，不添加无证据结论 | PLANNED |
| 中英文摘要一致 | HFUT-WEB-008; HFUT-FMT-010 | FINAL_SUBMISSION_REVIEW | 人工 | Microsoft Word | 双语逐句语义比较 | 目的、方法、结果和结论一致 | 修订翻译并再次审查 | PENDING_WINDOWS_CHECK |
| 摘要字体和行距 | HFUT-FMT-003; HFUT-FMT-010 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word | 检查样式和段落对话框 | 中文标签/正文和英文摘要匹配已核验参数 | 修订reference.docx或后处理规则 | PENDING_STEP3 |
| 关键词数量、对应和规范性 | HFUT-WEB-009; HFUT-WEB-010; HFUT-FMT-005; HFUT-FMT-011 | SOURCE_WRITING | 混合 | list checker + editor | 比较中英列表、计数、检查缩写 | 中文不少于4个；双语词义、数量、顺序一致 | 修订关键词集 | PLANNED |
| 中图分类号 | HFUT-FMT-006 | FINAL_SUBMISSION_REVIEW | 人工 | browser + Microsoft Word | 查询并由作者复核 | 存在且适合论文主题 | 重新检索或咨询编辑部 | PLANNED |
| 文献标识码处理 | HFUT-FMT-007 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word | 查看Step 3结论和投稿系统要求 | 不复制未经确认的示例A | 留空或按确认结果处理 | PENDING_STEP3 |
| 全文字数 | HFUT-WEB-011 | FINAL_SUBMISSION_REVIEW | 混合 | counter + Microsoft Word | 对比源计数和Word字数 | 一般不超过10000字 | 压缩非必要内容，不删关键证据 | PLANNED |
| 引言近2年工作覆盖 | HFUT-WEB-012 | SOURCE_WRITING | 混合 | bibliography manager | 检查引言引用年份和内容 | 反映投稿时点最近2年且来源相关 | 补检索和阅读，不凑数引用 | PLANNED |
| 结论证据边界 | HFUT-WEB-013 | SOURCE_WRITING | 人工 | editor | 对照冻结claim-evidence map | 结论来自真实结果且不简单重复 | 收窄或改写结论 | PLANNED |
| 缩略语首次出现 | HFUT-WEB-014 | SOURCE_WRITING | 混合 | text checker | 扫描缩略语首次位置 | 非公知缩写给中文翻译或外文全称 | 增补首次释义 | PLANNED |
| 量、单位、正斜体和上下标 | HFUT-WEB-015 | FINAL_SUBMISSION_REVIEW | 混合 | text checker + Microsoft Word | 符号清单与视觉检查 | 全文符号和法定单位一致 | 逐项修正并回归检查 | PENDING_WINDOWS_CHECK |
| 页面、页边距、分栏和段落参数 | HFUT-WEB-032; HFUT-FMT-028 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word + OOXML inspector | 按Step 3证据检查节和段落属性 | 与受控样式分析结论一致 | 修订Step 4模板或后处理 | PENDING_STEP3 |
| 正文字体 | HFUT-FMT-012 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word | 抽查并扫描字体运行 | 中文五号宋体、英文五号Times New Roman | 修订样式并清理直接格式 | PENDING_STEP3 |
| 标题层级、编号和字体 | HFUT-FMT-013; HFUT-FMT-014; HFUT-FMT-015 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word | 检查Heading样式和编号 | 0/1/1.1/1.1.1结构及字体正确 | 修订多级列表与样式 | PENDING_STEP3 |
| 标题不换行 | HFUT-FMT-016 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word | 逐标题检查最终分页 | 无标题跨成两行 | 修改标题或排版，不改变含义 | PENDING_WINDOWS_CHECK |
| 正文标点、数字和外文字母细则 | HFUT-FMT-029 | FINAL_SUBMISSION_REVIEW | 混合 | text checker + Microsoft Word | 按后续来源核验结论扫描并抽查 | 只应用已确认规则且全文一致 | 回到Step 3或标准来源核验，不猜测 | PENDING_STEP3 |
| MathType对象 | HFUT-FMT-018 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + MathType | 检查公式对象类型和可编辑性 | 全部公式为可编辑MathType并显示正确 | 手工重建或按已验证POC修复 | PENDING_POC |
| 公式变量、角标、矩阵向量和释义 | HFUT-FMT-019; HFUT-FMT-020; HFUT-FMT-021; HFUT-FMT-022 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + MathType | 逐公式符号审查 | 正斜体、粗体、单字母变量和释义正确 | 在MathType及正文中修正 | PENDING_WINDOWS_CHECK |
| 公式编号、引用、标点和长式 | HFUT-FMT-023 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + MathType | 按Step 3结论逐式检查 | 与受控来源视觉/样式结论一致 | 回到Step 3或手工调整 | PENDING_STEP3 |
| 图宽 | HFUT-FIG-002 | DOCX_POSTPROCESS | 自动+人工 | OOXML inspector + Microsoft Word | 读取图形extent并用标尺确认 | 单栏≤7.5 cm；通栏≤16.0 cm | 缩放源图并重新插入 | PLANNED |
| 图中文字字体字号 | HFUT-FIG-003; HFUT-FIG-004; HFUT-FMT-025 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + Visio/Origin | 检查源对象和Word显示 | 中文/英文数字字体正确；Visio 8 pt；其他图六号等效 | 修改源图并重新复制 | PENDING_STEP3 |
| 曲线图来源和可编辑性 | HFUT-FIG-005; HFUT-FIG-006 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + Origin | 检查对象类型、背景、轴和单位 | 非截图；对象可编辑；必要元素完整 | 在Origin重绘并复制页面 | PENDING_WINDOWS_CHECK |
| 流程图/框图可编辑性 | HFUT-FIG-007; HFUT-FIG-008 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + Visio | 检查对象与文字层 | 不是扁平图片且文字可编辑 | 在Visio重建并复制 | PENDING_WINDOWS_CHECK |
| 图的先文后图和编号 | HFUT-FIG-009; HFUT-FIG-010 | PANDOC_BUILD | 自动+人工 | build script + Microsoft Word | 检查首次引用、图序和子图引用 | 全文连续且先引用后出现 | 修正引用键、位置或编号 | PENDING_POC |
| 坐标轴、标目、变量和单位 | HFUT-FIG-011; HFUT-FIG-012; HFUT-FIG-013 | WINDOWS_WORD_REVIEW | 人工 | Origin/Visio + Microsoft Word | 逐图检查轴、斜体、单位和标签 | 所有适用项符合文字要求 | 修改源图并重新导入 | PENDING_WINDOWS_CHECK |
| 图题样式 | HFUT-FIG-017 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word | 按Step 3结论比较Caption样式 | 不把示例样式误当已确认规则 | 使用Step 3确认值或记录待询 | PENDING_STEP3 |
| 图例与中英文图题 | HFUT-FIG-020 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word + source drawing tool | 按Step 3或期刊确认结果检查 | 图例清楚且不虚构双语图题要求 | 请求期刊确认或保留待核验 | PENDING_STEP3 |
| 图文件格式、DPI、颜色和线宽 | HFUT-FIG-018 | FINAL_SUBMISSION_REVIEW | 人工 | source tools + Microsoft Word | 查阅后续核验结论 | 仅执行有权威来源的参数 | 请求期刊确认，不猜测 | PENDING_STEP3 |
| 地图规则 | HFUT-FIG-016; HFUT-FIG-019 | FINAL_SUBMISSION_REVIEW | 人工 | Microsoft Word | 确认最终图清单无地图 | 无地图 | 若新增地图则重新启用全部地图检查 | NOT_APPLICABLE |
| 三线表及线宽 | HFUT-TBL-003; HFUT-TBL-004 | DOCX_POSTPROCESS | 自动+人工 | OOXML inspector + Microsoft Word | 检查表格边框 | 仅三线；上下1 pt、次线0.5 pt | 修订OOXML或Word边框 | PLANNED |
| 表内字体 | HFUT-TBL-005 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word | 扫描表格runs并人工抽查 | 汉字六号宋体；字母数字六号Times New Roman | 修订表样式/直接格式 | PENDING_STEP3 |
| 表头量与单位及栏目名 | HFUT-TBL-006; HFUT-TBL-007 | SOURCE_WRITING | 混合 | table validator + editor | 检查每栏标题和单位语法 | 每栏准确命名且量/单位格式正确 | 修改源表头 | PLANNED |
| 表内精度和缺失值语义 | HFUT-TBL-008; HFUT-TBL-009 | SOURCE_WRITING | 自动+人工 | table validator + source logs | 按列检查小数位并追溯－/0/空白 | 显示精度一致且语义与真实日志相符 | 回查原始数据，禁止猜值 | PLANNED |
| 表题、对齐、续表和注释 | HFUT-TBL-010; HFUT-TBL-011; HFUT-TBL-012 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word | 按Step 3结论和表结构检查 | 只采用已确认规则，示例不被泛化 | 回到Step 3或请求期刊确认 | PENDING_STEP3 |
| 引用顺序与至少8篇 | HFUT-WEB-023; HFUT-WEB-024 | PANDOC_BUILD | 自动 | Pandoc + CSL | 检查首次出现顺序和条目数 | 顺序编码；一般不少于8篇真实引用 | 修正引用；不得用无关条目补数 | PENDING_POC |
| 文献真实性、已读和近3年覆盖 | HFUT-WEB-021; HFUT-WEB-022 | SOURCE_WRITING | 人工 | Zotero/BibTeX + source ledger | 检查来源、阅读状态、年份和相关性 | 每条可追溯且覆盖要求合理 | 补读/替换，不编造 | PLANNED |
| 参考文献字体和行距 | HFUT-REF-002 | WINDOWS_WORD_REVIEW | 混合 | Microsoft Word | 检查字体和段落行距 | 中六宋、英数六号TNR、14 pt行距 | 修订参考文献样式 | PENDING_STEP3 |
| 各文献类型字段和标识 | HFUT-REF-003; HFUT-REF-007; HFUT-REF-008; HFUT-REF-009; HFUT-REF-010; HFUT-REF-011; HFUT-REF-012; HFUT-REF-013; HFUT-REF-014 | PANDOC_BUILD | 自动+人工 | Pandoc + CSL + Zotero | 与附件模式逐类型比较 | 所有实际类型字段顺序和标识正确 | 调整CSL或人工修正并记录 | PENDING_POC |
| 作者人数阈值、DOI和中文文献英文对照 | HFUT-REF-016; HFUT-REF-017; HFUT-REF-018; GBT-001 | FINAL_SUBMISSION_REVIEW | 人工 | authoritative standard text + Microsoft Word | 使用后续来源链结论 | 不依据示例猜规则 | 获得权威可读来源或询问期刊 | PENDING_POC |
| 作者稿与匿名稿均为Word | HFUT-WEB-028 | FINAL_SUBMISSION_REVIEW | 自动+人工 | Microsoft Word | 检查两个文件可正常打开 | 两份Word文件内容角色正确 | 重新构建并复查 | PENDING_WINDOWS_CHECK |
| 文章编号、收稿和修回日期责任 | HFUT-WEB-033; HFUT-PUB-EX-007 | FINAL_SUBMISSION_REVIEW | 人工 | journal portal + Microsoft Word | 按投稿系统和后续确认判断 | 不把成刊字段擅自作为作者稿必填项 | 留空或按编辑部确认处理 | PENDING_STEP3 |
| 匿名稿正文身份信息 | HFUT-WEB-029 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word | 搜索姓名、单位、简介和联系方式 | 无作者相关信息 | 删除并再次全文搜索 | PENDING_WINDOWS_CHECK |
| 匿名稿属性、批注、修订、基金和致谢 | HFUT-WEB-031 | WINDOWS_WORD_REVIEW | 人工 | Microsoft Word Document Inspector | 检查全部潜在身份载体 | 所有保守匿名检查完成且范围有记录 | 清理后另存并重新检查 | PENDING_WINDOWS_CHECK |
| 投稿平台联系方式 | HFUT-WEB-030 | FINAL_SUBMISSION_REVIEW | 人工 | journal submission portal | 与作者确认表对照 | 所有作者联系方式准确 | 更正平台元数据 | PLANNED |
| 成刊样例不升级为强制规则 | HFUT-PUB-EX-001; HFUT-PUB-EX-003; HFUT-PUB-EX-004; HFUT-PUB-EX-006; HFUT-PUB-EX-007 | FINAL_SUBMISSION_REVIEW | 人工 | review checklist | 审核每项样式的来源ID和level | 无规则仅以成刊视觉为强制依据 | 降级为EXAMPLE_ONLY或补权威来源 | PLANNED |
| 样例论文不自动入参考文献 | HFUT-PUB-EX-008 | SOURCE_WRITING | 人工 | Zotero/BibTeX | 检查导入来源和引用理由 | 未因版式参考身份而进入bibliography | 删除无实际相关性条目 | NOT_APPLICABLE |

## 3. Failure Governance

Any failed check returns to the implementation layer named in the rule
crosswalk. Missing evidence does not become a guessed default. Experimental
claims and data remain governed by the Phase 1/2 freezes and are not altered by
format remediation.
