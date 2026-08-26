# Phase 7.1 — HFUT complete automated format remediation report

## 1. Verdict

`PHASE_7_1_HFUT_FORMAT_SATURATED_MANUAL_ITEMS_REMAIN`. `FORMAT_PATTERN_SATURATION = YES`; all 247 extracted source objects are classified. Automated, confirmed mismatches are closed. The remaining work is manual submission production or verified-metadata collection.

## 2. Baseline

Baseline was `main` at `e7d533a7c93232d13e42cf91ed9328d454adea52`, equal to `origin/main`, clean before this work.

## 3. Source hash verification

The four hashes were checked against `PAPER_PHASE2_5_TEMPLATE_SOURCE_MANIFEST_v1.0.csv` before conversion: `HFUT_FMT_DOC=e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d`; `HFUT_REF_DOC=5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651`; `HFUT_FIG_DOC=160960cdfcc73896cb443a1b7eeec91e9ad419febc4710bafff5b1882636138a`; `HFUT_TABLE_DOC=1764dd6bb74e4ea850aad2fd71f87a1a92badfd7d6854edd8ff9db7d09a0f009`. Legacy DOC inspection used temporary LibreOffice DOCX/PDF derivatives only.

## 4. User authority model

User authorship authority is Wang Kailun / WANG Kailun as first and corresponding author, with `2024180231@mail.hfut.edu.cn`; Wang Qi / WANG Qi is second author only.

## 5. Font-size-name resolution

`六号 = 7.5 pt`, not 6 pt. `PHASE7_1_CHINESE_FONT_SIZE_RESOLUTION = CONFIRMED`; reference entries, figure captions, table captions and table content remain 7.5 pt where the source says 六号.

## 6. Source-object saturation summary

`TOTAL_SOURCE_OBJECTS=247`, `UNCLASSIFIED_SOURCE_OBJECTS=0`. The inventory uses stable DOCX object locators; derived page numbers are not asserted as Microsoft Word pagination.

## 7. 排版格式及要求 — full-document audit

All body paragraphs and table/row objects in the formatting source were inventoried. Explicit rules and specimens were separated from editorial placeholders and manual production requirements.

## 8. Title findings

Chinese title remains within 20 characters. The English source says sentence-initial and proper-noun capitalization, so the title is now `Input data-path reconstruction for industrial defect detection on Jetson`.

## 9. Author findings

Chinese/English authors remain two authors. No one-affiliation superscript requirement was established; no numbering is emitted.

## 10. Affiliation findings

Source grouping parentheses are restored around the one shared Chinese and English affiliations.

## 11. Chinese abstract findings

The literal label is `摘 要：`; source geometry is left 420/right 295 twips, exact 14 pt line spacing.

## 12. Chinese keyword findings

Keywords independently use left 420/right 293 twips.

## 13. CLC/document-code findings

The source specimen carries `中图分类号` and `文献标识码：A`; the generated full and anonymous outputs emit both with source geometry.

## 14. English front-matter findings

English affiliation grouping is restored; English keyword label is `Key words：`.

## 15. Introduction-numbering finding

The original specimen is `0 引 言`, not an unnumbered introduction. The visible zero is retained and the source spacing restored.

## 16. Heading hierarchy findings

H1/H2/H3 remain 14 pt Heiti / 10.5 pt Heiti / 10.5 pt Kaiti; automatic Word numbering remains disabled.

## 17. Body/page geometry

Body first line remains 438 twips. Source-format validation confirms one-column front matter and two-column body without treating a project transition count as an HFUT rule.

## 18. First-page footer

The first-page biography is emitted in the first footer. No received/revised dates or funding absence statement was fabricated.

## 19. Corresponding-author remediation

Unsupported inline CN/EN corresponding-author paragraphs were removed. The correspondence marker and approved email are in Wang Kailun's footer biography.

## 20. Biography schema

`author-biographies` supports multiple structured records; empty biography records are skipped. `WANG_QI_BIOGRAPHY_DATA = PENDING_EXTERNAL_VERIFICATION`.

## 21. Reference-document full audit

All reference-source paragraphs were inventoried. Source confirms 7.5 pt Songti/Times New Roman and exact 14 pt lines. Variable specimen indentation is not falsely normalized to 6 pt or a purported official fixed 360 twips.

## 22. Figure-document full audit

Single/full width limits are 7.5/16.0 cm; internal typography and editable-object rules are recorded in the manual specification.

## 23. Table-document full audit

Source confirms three-line tables, 1 pt outer rules, 0.5 pt middle rule, 7.5 pt content, and no printed vertical lines. Word gridlines are not borders.

## 24. Equation/MathType audit

E1–E3 remain review-stage OMML. Source-required MathType conversion is deferred.

## 25. Published-paper corroboration

The two published PDFs were used only as secondary visual corroboration; their final editorial artifacts were not promoted to author-side requirements.

## 26. Legacy reference.docx failures

The old candidate lacked CN abstract/keyword/classification geometry and carried project-only validator assumptions. It remains a derived production reference, not an official template.

## 27. Template changes

The deterministic builder and rebuilt reference DOCX contain source-derived front-matter insets and labels.

## 28. Filter changes

The filter emits grouped affiliations, document code, source literal labels, and no inline correspondence.

## 29. Postprocessor changes

Existing first-footer movement is retained; structured biography generation feeds it. Figure float and Candidate-B offset are unchanged.

## 30. Validator changes

The source validator now validates source-derived front-matter geometry and accepts the actual float/table architecture rather than obsolete project layout assumptions.

## 31. Format-text changes

See `PAPER_PHASE7_1_FORMAT_TEXT_CHANGE_LEDGER_v1.0.csv`; each has scientific semantic change `NO`.

## 32. Anonymous-build changes

Anonymous output keeps title/abstract/keywords/CLC-code/body/figures/tables/references and removes all identity-bearing front matter and footer content.

## 33. Table non-regression

Three manuscript tables remain; printed vertical borders were not added.

## 34. Figure non-regression

Three figures and the Candidate-B Figure 3 one-related-paragraph offset remain unchanged.

## 35. Reference non-regression

Rendered references remain 22 cited entries; source typography remains 7.5 pt / exact 14 pt / left alignment.

## 36. Scientific non-regression

`validate_phase71_scientific_nonregression.py` passed: only the English-title capitalization and the source-required introduction spacing changed in manuscript Markdown. Frozen values, RQ1/RQ2, figures, tables, references, results, conclusions and limitations were preserved. The historical Phase 6.1 validator was also exercised but is not a current-chain gate: it asserts a superseded four-figure/five-equation inventory and fails independently of this format-only delta; it was not weakened or used as Phase 7.1 evidence.

## 37. Full build

`FULL_BUILD = PASS`.

## 38. Anonymous build

`ANONYMOUS_BUILD = PASS`, `FULL_ANONYMOUS_PARITY = PASS`.

## 39. Saturation metrics

`TOTAL_SOURCE_OBJECTS=247`; `AUTO_APPLICABLE_RULES=17`; `AUTO_MISMATCH_BEFORE=9`; `AUTO_REMEDIATED=9`; `AUTO_MATCH_AFTER=17`; `MANUAL_DEFERRED=4`; `EDITORIAL_ONLY=2`; `METADATA_PENDING=1`; `UNRESOLVED_AUTHORITY=0`; `UNCLASSIFIED_OBJECTS=0`.

## 40. Automatic remediation closure

`AUTOMATABLE_HFUT_FORMAT_MISMATCHES = 0`.

## 41. Manual deferred items

Visio Figure 1; Origin Figures 2–3; MathType E1–E3; Word Desktop visual QA; anonymous Word QA; Document Inspector; portal validation.

## 42. Metadata pending items

Wang Qi's verified biographical facts are pending. This is a metadata blocker, not a format-schema blocker.

## 43. Word Desktop QA targets

Inspect first-page footer position, title/affiliation grouping, CN inset geometry, floating-figure page flow, table rules, and final editable Visio/Origin/MathType assets.

## 44. Files changed

See Git diff; output DOCX files are ignored build products.

## 45. Git diff

Review required before commit; no scientific prose change is authorized.

## 46. Commit

One controlled local commit is permitted after the final diff audit; no push, tag, merge, reset, clean, rebase, or amend.

## 47. Exact next action

Commit the audited automation change, then obtain Wang Qi's verified biography and complete the specified Word Desktop/manual asset QA.
