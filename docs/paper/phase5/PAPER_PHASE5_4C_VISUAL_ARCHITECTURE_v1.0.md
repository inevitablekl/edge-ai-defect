# Paper Phase 5.4C Visual Architecture v1.0

Status: `VISUAL_ARCHITECTURE_PREPARATION_COMPLETE`; scope: source preparation only.

## 1. Authority boundary

This package prepares the target four-figure/three-table architecture. It does not alter the current manuscript sections, citations, bibliography, accepted final figures, current figure/table manifests, or DOCX numbering. New SVG artwork is a deterministic non-final preview. Visio and Origin publication production remains `USER_MANUAL` work followed by scientific/visual acceptance and a separate integration step.

The scientific freeze is unchanged: V2R/V0 FPS `2.236671×`; V2R/V0 mean-latency reduction `55.4519%`; V3R/V2R FPS `+4.0738%`; mean latency `-4.0349%`; P95 `+0.1514%` higher/slower; P99 `-0.1184%` lower/faster; tail `MIXED`; contribution count exactly `2`.

## 2. Current asset audit and reconciliation

| Asset | Current authority | Editable/source availability | Data authority | Accepted export | Reconciliation |
|---|---|---|---|---|---|
| F1 implementation paths | `figure_manifest.csv` status `FINAL_ACCEPTED` | accepted `.vsdx`; historical specs and deterministic preview | implementation/manuscript path authority | final `.pdf` and `.svg` present | Old v1 spec status prose predates the final source. Actual files plus manifest govern; nothing is deleted or downgraded. |
| F2 mean FPS | current manifest `FINAL_ACCEPTED` | deterministic Python script; Origin production spec | `fig2_mean_fps_origin_data.csv` | final `.pdf/.svg/.png` present | Historical Origin status does not negate accepted reproducible exports. |
| F3 latency | current manifest `FINAL_ACCEPTED` | deterministic Python script; Origin production spec | `fig3_mean_tail_latency_origin_data.csv` | final `.pdf/.svg/.png` present | Historical Origin status does not negate accepted reproducible exports. |
| T1 platform/protocol | current `table_manifest.csv`, `PUBLICATION_STRUCTURE_READY` | Word/Markdown three-line spec | frozen experiment/protocol sources | integrated Word table | Retained as current T1; future target T2 only. |
| T2 correctness | current manifest, `PUBLICATION_STRUCTURE_READY` | Word/Markdown three-line spec | frozen V0/V2R correctness evidence | integrated Word table | Retained as current T2; future target T3 only. |

No existing source conflict requires invention. In particular, the new controlled-path table uses bounded V0 host-path wording and does not assign an unverified V0 raw-staging allocation type.

## 3. Target architecture

| Target | Role | Intended location | Production | Source authority |
|---|---|---|---|---|
| F1 | actual tested V0/V2R/V3R implementation paths | Section 1.3/current callout area | Visio | accepted F1 VSDX + current implementation/method authority |
| F2 | conceptual E2E composition and intervention scopes | Section 1.3 | Visio | Section 1.3 concepts + frozen path-boundary language |
| F3 | mean FPS and five-run sample SD | Results Section 4.2 | Origin | current authoritative FPS CSV |
| F4 | absolute Mean/P95/P99 and frozen V3R/V2R changes | Results Section 4.2 | Origin | current latency CSV + frozen relative-change CSV |
| T1 | compact controlled-path matrix | beginning of Section 2 | Word three-line table | Method Sections 2.1–2.3 + implementation contract |
| T2 | platform/model/dataset/common protocol | current Section 3.1 location | existing Word table | current T1 authority |
| T3 | V0/V2R task-level correctness | current Section 4.1 location | existing Word table | current T2 authority |

F1 is implementation-specific; F2 is conceptual. F2 boxes never represent independently measured stage durations.

## 4. Figure 2 conceptual design

The six common components are `数据源获取/解码`, `主机暂存/输入准备`, `预处理`, `必要数据移动`, `TensorRT INT8推理与同步`, and `后处理/结果构造`. A neutral dashed scope band spans input preparation through necessary movement for `V0→V2R：较宽的结构/配置干预`. A neutral dotted scope band isolates host staging for `V2R→V3R：较窄的结构/配置干预（仅主机原始图像暂存分配类型）`.

The mandatory note is: `较宽/较窄仅描述受控变量覆盖的结构与配置范围，不表示 Amdahl α 大小，也不预测实际加速比。` Scope bands have equal luminance/weight and contain no performance values, timing labels, arrows of improvement, or causal prediction. Specification and non-final preview are recorded in the Phase 5 preparation manifest.

## 5. Figure 1 upgrade boundary

The accepted VSDX is the future manual base. Upgrade only alignment, lane hierarchy, common-stage recognition, isolated-variable visibility, timing-boundary readability, typography, and grayscale print behavior. Preserve topology, stage semantics, single-frame ordering, and the V2R/V3R shared CUDA algorithm. The sole V2R→V3R highlighted difference is pageable versus pinned host raw-image staging.

Forbidden additions are zero-copy, mapped memory, pinned output, double buffering, multiple streams, transfer-compute overlap, cross-frame pipeline, GPU NMS, asynchronous overlap, or a second CUDA preprocessing algorithm.

## 6. Global visual encoding contract

Where variant identity is needed in F1, F3, and F4 Panel A:

| Variant | Fill | Pattern | Outline | Meaning |
|---|---|---|---|---|
| V0 | white | none | solid black | identity only |
| V2R | white | 45-degree diagonal hatch | solid black | identity only |
| V3R | white | cross-hatch | solid black | identity only |

All variants have equal apparent luminance and line weight; darker/lighter never means better. Labels remain present so hatch is redundant encoding. No gradient, 3D, shadow, traffic-light color, glossy decoration, or changing identity between figures. F2 scope annotations use neutral dash patterns and do not reuse performance/variant semantics.

## 7. Figure 3 plan

Use three zero-baseline bars and symmetric SD error bars: V0 `54.600 ± 0.223`, V2R `122.122 ± 0.492`, V3R `127.097 ± 1.279` FPS. SD is the sample standard deviation across five independent process-level FPS runs. It is not CI, SE, population SD, or a significance interval. The Origin project must import the existing CSV directly.

## 8. Figure 4 design decision

The current grouped design is strong for absolute magnitude but makes the small, opposite V2R/V3R tail movements hard to read. A zoomed/broken axis would exaggerate them. The recommended two-panel design retains the grouped absolute values in Panel A and adds an honest symmetric `-5%` to `+5%` relative panel with explicit zero in Panel B.

Panel B uses only the frozen changes: Mean `-4.0349%`, P95 `+0.1514%` higher/slower, P99 `-0.1184%` lower/faster. It defines negative as lower/faster and positive as higher/slower. Exact labels make the mixed directions legible while the shared scale shows their relative smallness. No statistical significance or causal mechanism is implied. Recommendation: two-panel design.

## 9. Controlled-path matrix

The exact proposed table appears in `table1_controlled_path_matrix_spec_v1.0.md`. It records CPU/OpenCV V0, pageable raw staging plus CUDA V2R, and pinned raw staging plus the same CUDA semantics V3R. V0 is bounded as a host image/host FP32 tensor path; its allocation type is intentionally not guessed. The matrix calls V0→V2R broader and V2R→V3R narrower only in structural/configuration scope, not in `α` or expected gain.

## 10. Numbering migration

- current F1 → target F1
- new conceptual asset → target F2
- current F2 → target F3
- current F3 → target F4
- new controlled-path matrix → target T1
- current T1 → target T2
- current T2 → target T3

The exact captions and later cross-reference operations are in `figure_table_caption_renumbering_map_phase5_v1.0.md`. No migration is applied in this preparation stage.

## 11. Ownership and integration plan

- `USER_MANUAL_VISIO`: create editable F1/F2 VSDX and PDF/SVG exports from the specified sources.
- `USER_MANUAL_ORIGIN`: create editable F3/F4 OPJU and PDF/SVG/PNG exports by importing the authoritative CSVs.
- Main scientific/visual review: verify path semantics, values, grayscale/print quality, and mixed-tail wording.
- Later repository integration: accept final assets, atomically update current manifests/captions/callouts/numbering and validators, rebuild Full/Anonymous, and perform manual Word review.

The preparation manifests are deliberately separate from current publication manifests, preventing premature authority promotion.

## 12. Anti-causal and regression gates

Acceptance requires: no independent `T_k` measurement implication; no broader-scope-equals-larger-`α` implication; no universal pinned-memory benefit; no consistent tail-improvement claim; no new mechanism, metric, variant, experiment, inference, significance annotation, or third contribution. The current manuscript must remain byte-reproducible in scientific source and regression-clean in both build variants.

## 13. Phase 5.4C-A validation record

- Full authoritative build: PASS; `11` A4 pages; SHA-256 `3ce015f2c6288ec2588ddc022bdbdfec01cc3e857f5dce709babcac01e795d1c`.
- Anonymous authoritative build: PASS; `12` A4 pages; SHA-256 `49a8e21838ba9c8ceff9572566edd0caeeb0d2a17374f8ccfec07ac6d02c16a0`.
- Citation source: PASS (`27` entries, `26` cited, zero unresolved, one governed unused entry).
- Rendered bibliography and Full/Anonymous bibliography identity: PASS.
- Current static cross-references: PASS (`F1/F2/F3`, `T1/T2`).
- Full/Anonymous scientific-body parity and anonymous identity scan: PASS.
- Journal-format structural validation: PASS; each build contains `8` display OMML equations.
- Current manuscript sections, references, and current publication manifests unchanged from starting HEAD: PASS. This also preserves T1/T2/T3 formulas, frozen result prose, tail direction, and exactly two contributions.
- Phase 5 CSV exact-value audit: PASS for all FPS, absolute latency, and relative-change values.
- Conceptual SVG regeneration: PASS with stable SHA-256 `2358343497584efe19a8c76c8736b614341167ec950b408d238a77aa9fddcf77` across consecutive runs.
- Conceptual preview anti-causal scan: PASS; no frozen performance result or `T_k` label appears in the SVG, and the required `α`/speedup boundary appears explicitly.
- `git diff --check`: PASS.
