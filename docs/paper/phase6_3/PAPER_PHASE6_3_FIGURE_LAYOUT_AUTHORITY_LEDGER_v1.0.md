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
| `wp:inline` figure block as a publication float | Retired project implementation assumption | RETIRED_INCORRECT_IMPLEMENTATION_ASSUMPTION |
| Word floating figure/container | Project implementation used to satisfy natural-flow and caption-association invariants | ACTIVE_PROJECT_IMPLEMENTATION_NOT_A_JOURNAL_RULE |
| One-row `w:tblpPr` floating table containing editable drawing plus caption | Paper Phase 6.3R7 production implementation | ACTIVE_PROJECT_IMPLEMENTATION_NOT_A_JOURNAL_RULE |
| Figure 1 page-margin-top floating-table position | Supervisor page-top invariant implemented by the project | ACTIVE_PROJECT_IMPLEMENTATION_NOT_A_JOURNAL_RULE |
| Figure 2/3 text-column-relative floating-table position | Project implementation | ACTIVE_PROJECT_IMPLEMENTATION_NOT_A_JOURNAL_RULE |
| Figure 1 placement before the next `HFUTHeading1` | Retired project structural heuristic | REMOVED |
| Figure 1 `pageBreakBefore` | Retired project implementation mechanism | REMOVED |
| Figure-only continuous two-column → one-column section transition | Retired project implementation mechanism | REMOVED |

The active placement model is source-order eligibility plus a Word-native
floating container. After the first callout, each drawing and its editable
caption occupy one non-splitting floating-table row. The container is outside
the main text flow, so later ordinary prose is not trapped behind a drawing
that cannot fit at the anchor location. Figure 1 uses the supervisor-governed
page-top/full-width invariant; Figures 2 and 3 use column-relative placement.
Ordinary prose is neither required nor forbidden between callout and floating
block, and no named semantic heading is a placement barrier.

The scientific drawing remains an inline DrawingML payload *inside* the
floating table. This nested `wp:inline` is not treated as the float mechanism;
`w:tblpPr` is the governing non-blocking container. The drawing and caption
remain editable, adjacent, and inseparable through a single `w:cantSplit` row.
