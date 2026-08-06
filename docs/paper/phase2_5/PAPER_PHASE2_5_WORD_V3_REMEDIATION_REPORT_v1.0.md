# Paper Phase 2.5 Word v3 Remediation Result

## 1. Verdict

```text
WORD_V3_READY_FOR_RETEST
```

This means the generator repair and non-Word checks are complete. It does not
mean Microsoft Word first-open acceptance; Windows retest remains required.

## 2. Repository state

- Branch: `main`.
- Starting HEAD: `4cbc73e725b90adf181bbfdd205420a37e31da8c`.
- Starting worktree: clean; starting `git diff --check`: PASS.
- No reset, restore, checkout, stash, clean, merge, rebase, push, tag change,
  or dependency installation was used.
- Phase 0/1/2 files, formal chapters, references, and formal asset manifests
  were not modified.

## 3. Generator changes

`postprocess_phase2_5_poc_docx.py` now:

- removes dangling content-type overrides for absent package parts;
- removes the empty comments part and unused relationship;
- normalizes style-level paragraph-property order;
- repairs `HFUTEquation` to the bounded `atLeast` layout contract;
- applies the minimal inline-OMML line-height exception.

`inspect_phase2_5_poc_docx.py` now checks v3 names, content-type targets,
style-level paragraph-property order, and effective equation spacing.
`run_phase2_5_docx_poc.sh` now emits v3 names and validates both candidates.

## 4. Canonical reference DOCX

Not modified. SHA256 remains:

```text
c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71
```

## 5. POC v3 outputs

Generated outside Git under the Step 6 external POC root:

| File | SHA256 |
|---|---|
| `poc_full_v3.docx` | `940753da343d0fb8091444dac06206b255d081c2c33e695cdce3df0034d63b14` |
| `poc_anonymous_v3.docx` | `6fd580fc7cc41b2816eaa8bd1e5b495ed670e184dd1237f59927557721abd17f` |

The DOCX and PDF outputs are external artifacts and are not committed.

## 6. Automated validation

Passed for both v3 candidates:

- Pandoc generation, postprocessing, `unzip -t`, and inspector;
- zero inspector errors and zero duplicate style IDs;
- zero missing content-type override targets;
- style-level and document-level schema-order checks;
- A4 geometry, one-column front matter, two-column body, 425-twip spacing;
- PAGE retained and no external field/updateFields risk;
- OMML retained (`3 oMath`, `2 oMathPara`), not images;
- editable-equation layout contract present;
- figure, three-line table, ordered citations, and five references retained;
- anonymous forbidden-string scan: zero hits;
- LibreOffice preview: both A4 and two pages;
- formal references remain empty, chapter files remain `STRUCTURE_ONLY`;
- canonical reference SHA unchanged;
- `git diff --check`: PASS.

The generator's original and v3 anonymous core properties use the neutral
marker `PAPER_PROJECT_AI_POC`, and v3 custom properties contain only a CSL
filename rather than the old absolute workstation path. Word may write a
current-user value during save; therefore this is not a substitute for the
required post-save Document Inspector.

## 7. Windows retest requirements

The user/manual executor must open both v3 DOCX files in Microsoft Word and
record version, date, SHA256, repair/compatibility prompts, visual layout,
editable OMML, PAGE behavior after Ctrl+A/F9, and fresh PDF exports. For the
anonymous file, run Document Inspector and record whether `作者` or another
identity carrier is present; remove identity metadata only in a test copy and
record the result. Save under a new name, close, reopen, and verify no repair.

## 8. Next executor

```text
USER_MANUAL
```
