# Paper Phase 6.3 Figure Layout Authority Ledger v1.0

This ledger separates governed publication requirements from project QA
heuristics. A project implementation choice must not be promoted to an HFUT
or supervisor requirement without new recorded authority.

| Rule | Source authority | Status |
|---|---|---|
| First textual callout precedes its figure | HFUT / academic production rule | MANDATORY |
| Figure caption is below and directly associated with its drawing | HFUT | MANDATORY |
| Figure numbering is sequential | HFUT | MANDATORY |
| Figure 1 is full-width | Accepted manuscript layout | MANDATORY |
| Full-width Figure 1 is at page top | Supervisor instruction | MANDATORY |
| Figure 1 must not form a two-column body → full-width figure → two-column body sandwich on one page | Supervisor instruction / accepted layout invariant | MANDATORY |
| Figures 2 and 3 are single-column compatible and no wider than 7.5 cm | HFUT / accepted manuscript layout | MANDATORY |
| Drawings remain readable and within manuscript bounds | HFUT / academic production rule | MANDATORY |
| Figure 1 is placed immediately before Section 3.3 | Project Phase 6.3 heuristic | REMOVED |
| Figure 2 is placed immediately before Section 4.3 | Project Phase 6.3 heuristic | REMOVED |
| Figure 3 is placed immediately before Section 4.5 | Project Phase 6.3 heuristic | REMOVED |
| A figure must be adjacent to a named subsection heading | Project Phase 6.3 heuristic | REMOVED |
| An HFUTBody paragraph must intervene between first callout and Figure 2/3 | Project Phase 6.3 heuristic | REMOVED |
| Single-column figure height must not exceed 15.5 cm | Project Phase 6.3 QA heuristic | ADVISORY_NOT_MANDATORY |
| Statistical-figure optical bounding-box and centering thresholds | Project Phase 6.3 QA heuristic | DIAGNOSTIC |
| Report callout/drawing positions and intervening headings/body paragraphs | Project Phase 6.3 QA diagnostic | DIAGNOSTIC |
| Allow remaining prose in the current top-level section to flow before a governed page-top full-width figure | Project implementation mechanism; derived from page-top and natural-flow invariants | ACTIVE_NOT_PUBLICATION_RULE |

The active placement model is source-order eligibility plus governed layout
invariants: after the first callout, an inline drawing/caption block is eligible
for Word's next feasible layout location. A governed page-top full-width figure
may allow the remaining prose in its current top-level section to flow first.
Ordinary prose is neither required nor forbidden between callout and drawing,
and no named semantic heading is a placement barrier.
