# Paper Phase 2.5 Equation Layout Diagnosis

## 1. Observed failure

The supplied Word PDF and overlap image show that the display fraction/sum
and the ratio formula intrude into adjacent text lines. The formulas are
editable OMML, not images. The affected paragraphs are normal document body
paragraphs, not table cells or text boxes.

## 2. v2 OOXML measurements

| Formula case | Paragraph style | Effective spacing in v2 | Interpretation |
|---|---|---|---|
| Inline `t̄` | `HFUTBody` | `line=320`, `lineRule=exact`, `before/after=0` | Fixed 16 pt line box is tight for an OMML run |
| Display mean/sum | `HFUTEquation` | `line=320`, `lineRule=exact`, `before/after=0` | Fraction and summation exceed the fixed line box |
| Display ratio | `HFUTEquation` | `line=320`, `lineRule=exact`, `before/after=0` | Same clipping/overlap mechanism |
| Formula number candidate | static body text | inherited body spacing | No dynamic field or reference is involved |

The Word PDF renders the fraction and summation taller than the 320-twip
exact box. This explains vertical intrusion without requiring a MathType
replacement hypothesis.

## 3. Minimal v3 layout contract

The generator now applies:

- `HFUTEquation`: `lineRule=atLeast`, `line=480` twips, `spaceBefore=80`,
  `spaceAfter=80` twips;
- paragraphs containing only inline OMML within body text: direct
  `lineRule=atLeast`, `line=360` twips, zero before/after;
- ordinary body paragraphs without inline OMML: unchanged `HFUTBody`
  spacing;
- formula numbers: remain static text boundaries; no space-based alignment
  or complex dynamic cross-reference is introduced.

The 480-twip minimum is a bounded 24 pt display-equation line box, selected
from the observed 16 pt exact-box failure and checked against the v3
LibreOffice preview. It does not scale the formula, rasterize it, remove
fractions/sums, or expand all body paragraphs.

## 4. v3 verification

The v3 inspector reports one inline OMML paragraph at 360 twips `atLeast` and
two display OMML paragraphs using `HFUTEquation` at 480 twips `atLeast` with
80-twip before/after spacing. Counts remain `3 x m:oMath` and `2 x
m:oMathPara`. The A4 two-page LibreOffice preview shows visible separation
between both display formulas and neighboring text; this is supplementary
preview evidence, not Microsoft Word acceptance.
