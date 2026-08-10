# Paper Phase 5.4A Visual Needs v1.0

## 1. Status and boundary

- Status: `SPECIFICATION_ONLY`
- Production phase: Paper Phase 5.4C
- Phase 5.4A action: record purpose and validation needs only

No final figure, table, Visio asset, Origin asset, publication numbering, or source-data claim is created by this document. Phase 5.4C must validate every visual statement against current implementation and frozen evidence authorities.

## 2. Figure needs

### VF-01 — Theoretical E2E data path and optimization scope

Purpose: show the shared-semantic E2E path, the structurally broader V0→V2R intervention, and the structurally narrower V2R→V3R intervention. The figure should distinguish conceptual stage composition from measured quantities and must not imply that stages were independently timed, that Amdahl parameters were fitted, that structural breadth orders alpha or speedup, or that the interventions form a causal decomposition.

### VF-02 — Existing implementation data-path figure upgrade

Purpose: improve the current V0/V2R/V3R implementation-path figure after checking exact buffers, execution locations, transfers, synchronization, and unchanged downstream processing against implementation authority. It must not introduce zero-copy, double buffering, multi-stream overlap, or cross-frame overlap.

### VF-03 — FPS figure restyling

Purpose: restyle the current mean-FPS figure with consistent visual encoding for V0, V2R, and V3R and preserve the existing mean and five-run sample-standard-deviation semantics. It must not display confidence intervals or imply significance.

### VF-04 — Mean/P95/P99 latency figure restyling

Purpose: restyle the current latency figure so that the contrast between average improvement and mixed V3R/V2R tail behavior is legible. V3R P95 must remain higher/slower by 0.1514%, while V3R P99 remains lower/faster by 0.1184%; no visual encoding may imply consistent tail improvement.

## 3. Table need

### VT-01 — Controlled-path matrix

Purpose: provide a compact, implementation-validated comparison of controlled path properties.

Candidate columns:

| Candidate column |
|---|
| Variant |
| Host staging |
| Preprocessing location |
| Tensor preparation/data-path property |
| Changed component |
| Optimization scope |

Phase 5.4C must derive final cell content from implementation authority and manuscript semantics. VF-01 and VT-01 must not visually imply that broader structural scope means a larger alpha or larger speedup. This specification does not authorize final wording or a new publication table.
