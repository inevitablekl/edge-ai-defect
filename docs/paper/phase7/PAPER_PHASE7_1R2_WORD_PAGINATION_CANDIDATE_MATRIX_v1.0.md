# Phase 7.1R2 Word pagination candidate matrix

The deterministic R2 Full build is the common source. These candidates differ only by the logical body-child insertion position of the existing Figure-3 floating table; they do not alter scientific text, image payload, caption, table geometry, or wrap attributes.

| Candidate | Figure-3 offset | Anchor paragraph excerpt | Body-child position | DOCX SHA256 | Mechanical-page observation | Expected Word effect | Scientific delta | Format delta beyond anchor |
| --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| A | 0 | 5个独立进程中，V2R与V3R的进程级FPS范围分别为121.443–122.759和125.595–128.301，进程平均延迟范围分别为8.098–8.185 ms和7.740–7.894 ms，分布见图3。V3R相对V2R的合并样本P | 84 | 7cb27066001614f2c503fc6938cff607754a6ea617fd1bb74814583109ab9e0f | callout child 83; intervening HFUTBody=0; tblpPr={'leftFromText': '0', 'rightFromText': '0', 'topFromText': '0', 'bottomFromText': '0', 'vertAnchor': 'text', 'horzAnchor': 'text', 'tblpXSpec': 'center', 'tblpY': '1'} | Microsoft Word 2019 visual QA required | NONE | NONE |
| B | 1 | 进程级均值范围均不重叠，说明平均响应在5个独立进程中重复观察到，而非仅由单一异常进程形成；与此同时，P95与P99变化方向相反，未形成一致的尾延迟改善证据。两类观测共同表明，平均响应和尾延迟是不同评价维度，局部策略在本实验中改善均值并不意味 | 85 | 9360ff81c3080044fc763d12e258fe9bb5d36329705cef09b2a47731079ebed2 | callout child 83; intervening HFUTBody=1; tblpPr={'leftFromText': '0', 'rightFromText': '0', 'topFromText': '0', 'bottomFromText': '0', 'vertAnchor': 'text', 'horzAnchor': 'text', 'tblpXSpec': 'center', 'tblpY': '1'} | Microsoft Word 2019 visual QA required | NONE | NONE |

`CANDIDATE_ANCHOR_ONLY_DELTA=PASS`

PAGE6_BLANK = OPEN. Headless OOXML inspection cannot select the final Microsoft Word pagination result.

Open Candidate A and Candidate B in Microsoft Word 2019. Inspect Pages 5–7 and select only a candidate with no large artificial Page-6 blank region, Figure 3 after its first callout, reasonable narrative proximity, no new Page-5/Page-7 gap, no figure/caption overlap, and no clipping. Do not select using LibreOffice.
