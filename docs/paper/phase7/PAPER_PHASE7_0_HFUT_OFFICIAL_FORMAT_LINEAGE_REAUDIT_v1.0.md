# Phase 7.0 — HFUT official-format source-to-manuscript lineage re-audit

## 1. Verdict

`PHASE_7_0_FORMAT_LINEAGE_REAUDIT_COMPLETE_REMEDIATION_REQUIRED`.

The full manuscript was rebuilt from `8e465715c2d6f1ebd049b4c7c2a246497f9233c3` through the authoritative full pipeline and passed all current automated validators. That pass does not establish conformance with every visual/source-format rule: the validators encode several project choices that are now shown to diverge from the original HFUT specimen.

No manuscript, template, metadata, Lua, postprocessor, validator, figure, table, equation, CSL, or bibliography file was changed in this work unit.

## 2. Baseline

| Item | Observed |
| --- | --- |
| branch | `main` |
| HEAD / origin/main | `8e465715c2d6f1ebd049b4c7c2a246497f9233c3` / same |
| baseline status | clean index and worktree before audit |
| full build | `scripts/paper/build_manuscript_docx.sh --build-full` passed |
| rebuilt artifact | `docs/paper/manuscript/output/draft_full.docx`, SHA-256 `382f85a703e806b7367127e2afc9ad78e7177c2df8d3446e22762ce0ed507e5a` |
| Word truth boundary | Microsoft Word Desktop visual/pagination verification remains pending; LibreOffice was used only as derived evidence |

## 3. Original-source identity / hash verification

All eight manifest entries in `PAPER_PHASE2_5_TEMPLATE_SOURCE_MANIFEST_v1.0.csv` were present under `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/raw/` and SHA-256 matched the manifest. In particular: format DOC `e29119e…d0594d`; figure DOC `160960…6138a`; table DOC `1764dd…f009`; reference DOC `5ef440…f651`; GB/T PDF `215ed5…8a38`; published PDFs `5f7838…dd2a` and `139138…6fad`; web excerpt `a51066…f20c`.

## 4. Sources inspected and evidence classes

All four legacy DOC attachments were independently converted outside the repository with LibreOffice to both PDF and DOCX, then inspected as rendered pages and OOXML. The two published PDFs, GB/T 7714—2025 PDF, and web excerpt were also opened. Evidence is labelled below as `SOURCE_TEXT_EXPLICIT`, `SOURCE_VISUAL_DIRECT`, `CONVERSION_DERIVED_STRUCTURE`, `PUBLISHED_PDF_VISUAL`, `CURRENT_PRODUCTION_STRUCTURE`, or `CURRENT_WORD_VISUAL` (the latter is pending Word Desktop except for historical review records).

The LibreOffice conversion is not asserted to be bit-identical to Microsoft Word. Findings requiring Word-specific rendering are marked accordingly.

## 5. Existing Phase 2.5 lineage assessment

Phase 2.5 did inspect the source documents substantially. It recorded the Chinese-abstract indents in `PAPER_PHASE2_5_PARAGRAPH_FORMAT_OBSERVATIONS_v1.0.csv` and classified them as direct formatting; it also recorded footer evidence, three-line-table rules, MathType, and source geometry. However, its reference DOCX deliberately consolidated volatile direct formatting into reusable named styles. The later template omitted the Chinese abstract indents and parentheses, while the Phase 4 filter deliberately added correspondence lines. Thus the legacy pipeline was **PARTIALLY** created from textual requirements: important visual formatting was observed, but not all of it was preserved or enforced downstream.

## 6. Chinese abstract width finding

**UF-01: CONFIRMED — MAJOR_FORMAT.** The original format DOC paragraph P004 has direct `left=420 twips = 21.00 pt`, `right=295 twips = 14.75 pt`, exact 14 pt spacing, 9 pt Chinese abstract text and a bold 9 pt SimHei label. The English abstract P010 has no corresponding direct left/right indent in the conversion-derived paragraph structure. Its 10.5 pt Times New Roman body size is textually stated; exact English run inheritance is conversion-ambiguous.

`HFUTAbstractBodyCN` in `reference.docx` and the rebuilt Full DOCX has exact 14 pt and 9 pt body, but no `w:ind`; `HFUTAbstractBodyEN` also has no indent. The divergence was therefore observed in Phase 2.5, lost when the reference DOCX style was normalized, and not enforced by the full/anonymous/Phase 6.3 validators. Remediation belongs in the reference DOCX (or a narrowly scoped OOXML postprocessor) plus validators; it is not a Pandoc loss.

## 7. Affiliation-parentheses finding

**UF-02: CONFIRMED — MAJOR_FORMAT.** The original P003 visibly contains the affiliation block in literal parentheses: `(1.合肥工业大学 …，安徽 合肥 230009；2.… 230009)` followed by a red instructional parenthetical. The outer parentheses are specimen content, not the red instruction. English affiliation P009 likewise has literal surrounding parentheses. The current CN/EN metadata values and `HFUTAffiliationCN`/`HFUTAffiliationEN` output omit both grouping punctuation and affiliation markers.

This was source-observable in Phase 2.5 but was not made a metadata or style contract: `metadata_private.yaml` stores a bare single affiliation, the Lua filter emits it verbatim, and validators assert the bare value. Root cause: `RULE_LOST_IN_REFERENCE_DOCX` plus `VALIDATOR_FAILED_TO_ENFORCE`.

## 8. Corresponding-author placement finding

**UF-03: CONFIRMED — MAJOR_FORMAT.** The official main front-matter sample has author and affiliation lines followed immediately by the abstract; it does not show an inline `通信作者：…` or English equivalent there. Correspondence is instead present in the sample's first-page bottom `作者简介` block. Published-paper PDFs are secondary published-layout evidence and do not authorize an author-side inline line.

The inline lines are **PROJECT-CREATED / INCORRECT_FOR_SUBMISSION_FORMAT** on current evidence. They are introduced in `scripts/paper/full_manuscript_filter.lua:65,69`, emitted in `HFUTBody`, and required by `validate_full_manuscript_docx.py:144–145`; anonymous exclusion logic also names them. They are not caused by Pandoc or the original source.

## 9. First-page bottom-matter finding and biography schema

**UF-04: PARTIALLY_CONFIRMED — BLOCKING_FOR_SUBMISSION.** The web rule explicitly requires author biography and, if applicable, funding at the first-page footer. The original footer has a rule line then example `收稿日期`, `修回日期`, `基金项目`, and `作者简介`; it supplies two author biographies and identifies the corresponding author plus `E-mail` in the corresponding author's biography. Current output retains only one biography in a first-page footer.

| Field | Classification |
| --- | --- |
| 收稿日期 / 修回日期 | `EDITORIAL_SUPPLIED` / `TEMPLATE_PLACEHOLDER`; do not fabricate dates |
| 基金项目 | `AUTHOR_SUPPLIED_IF_APPLICABLE`; web excerpt says include type and identifier |
| 作者简介 | `AUTHOR_SUPPLIED_REQUIRED`; web excerpt specifies name, birth year, gender, native place, degree, title |
| 通信作者 / E-mail | `AUTHOR_SUPPLIED_IF_APPLICABLE`, in the biography/footer schema, not established as inline front matter |

The specimen gives biographies for both authors: first-author text then second-author text, with the latter marked correspondence and email. It supports an all-authors biography block in this two-author sample, not a first-author-only rule. The exact rule for larger author lists is unresolved and should be confirmed with HFUT if consequential.

`WANG_QI_REQUIRED_FIELDS`: birth year; gender; native place; degree; academic identity/title; research direction if required by later editorial instruction; correspondence status; email only if she is corresponding. Do not infer any values.

## 10. Table dotted-line / gridline finding and table audit

**UF-05: REJECTED — NONPRINTING_UI.** The table DOC explicitly says all tables use three lines: top/bottom 1 pt and middle 0.5 pt. In converted OOXML, ordinary specimen cells carry only horizontal top/bottom borders; no vertical border is defined. The apparent dotted verticals are consistent with Microsoft Word non-printing table gridlines. Do not add vertical borders.

Current Tables 1–3 have 1 pt top/bottom (`w:sz=8`), 0.5 pt header rule (`w:sz=4`), nil verticals, 7.5 pt Songti/Times, and centered table content. This is conformant for the ordinary examples. The source has special examples (notably a turned-column table with double verticals); those are example-specific, not a general override. Table captions are 7.5 pt bold SimHei and visually above tables; unit-at-upper-right, grouped headers, auxiliary horizontal rules, and wide/turned-table treatments require manual case review when applicable.

## 11. First-page/front-matter and body-format audit

Source confirms: Chinese title ≤20 characters; centered CN author line (14 pt KaiTi); literal affiliation grouping; Chinese abstract/keywords 9 pt, Chinese abstract exact 14 pt; English title sentence-style capitalization; surname uppercase / given-name initial-cap author convention; A4; source page margins approximately top 2.4 cm, bottom 2.0 cm, left/right 2.3 cm; single-column front matter then two-column body with about 0.748 cm gap; body Songti/Times 10.5 pt, justified and approximately 2-character first-line indent; heading hierarchy as stated in the format DOC.

The current named styles preserve the principal A4/two-column/body/font/heading architecture, but intentionally homogenize front-matter widths and simplify affiliation/correspondence/footer behavior. Footer line/absolute placement and final page geometry require `WORD_DESKTOP_CONFIRMATION_REQUIRED`.

## 12. Figure, equation, and reference audit

Figures: the original figure DOC explicitly requires ≤7.5 cm one-column and ≤16.0 cm full-width; Songti Chinese and Times New Roman Latin; Visio text 8 pt, other figure text comparable to Word six-point; Origin curves inserted by copy-page rather than screenshot/image; Visio flow/block diagrams copied to Word; no background for curves; continuous figure numbering; centered 6 pt bold SimHei captions; and editable-object workflow. Current Figure 1/2/3 submission assets remain open for the required Visio/Origin remediation, so no format pass is claimed.

Equations: the format DOC explicitly requires MathType entry/editing; variables italic, explanatory subscripts upright, variable subscripts italic, and vectors/matrices bold italic. Current OMML is structurally reviewable but **FINAL_SUBMISSION_REQUIRES_MATHTYPE**; classify current review as `CURRENT_REVIEW_OK`, not final-submission complete.

References: the original reference DOC explicitly invokes GB/T 7714—2025 and specifies 6 pt Songti/Times with exact 14 pt leading. The rebuilt manuscript reports 22 rendered/cited references and passes its citation/reference validators. No new original-source mismatch was found requiring metadata reopening; final GB/T/Word rendering remains a submission QA item.

## 13. Published-paper comparison

Both PDFs were opened, but their embedded character maps prevented reliable text extraction. They remain `PUBLISHED_PDF_VISUAL` only. Their production pages can corroborate broad layout and first-page field presence, but cannot override explicit author-submission attachment rules. No published-layout-only feature was promoted to a mandatory author requirement here.

## 14. Source → template → production lineage failures

| Confirmed gap | Phase 2.5 observed? | Failure point | Root cause |
| --- | --- | --- | --- |
| CN abstract width | Yes | reference DOCX; validators | `RULE_LOST_IN_REFERENCE_DOCX`; `VALIDATOR_FAILED_TO_ENFORCE` |
| affiliation parentheses | Yes, visually/content present | metadata/template/filter/validator | `CURRENT_TEMPLATE_INTENTIONAL_SIMPLIFICATION`; `VALIDATOR_FAILED_TO_ENFORCE` |
| inline correspondence | Source omission was visible | Lua filter/validator | `PROJECT_RULE_OVERRULED_OFFICIAL_FORMAT` |
| footer incomplete | Yes | postprocessor/metadata/filter/validator | `CURRENT_TEMPLATE_INTENTIONAL_SIMPLIFICATION` |
| dotted vertical borders | N/A; source already contradicted premise | none | `NONPRINTING_WORD_UI`, no remediation |
| MathType assets | Yes | deferred manual production stage | `CURRENT_TEMPLATE_INTENTIONAL_SIMPLIFICATION` |

## 15. User-finding ledger

| ID | Verdict | Severity |
| --- | --- | --- |
| UF-01 Chinese abstract narrower | CONFIRMED | MAJOR_FORMAT |
| UF-02 affiliation parentheses | CONFIRMED | MAJOR_FORMAT |
| UF-03 inline 通信作者 below affiliation | CONFIRMED | MAJOR_FORMAT |
| UF-04 bottom matter incomplete | PARTIALLY_CONFIRMED | BLOCKING_FOR_SUBMISSION |
| UF-05 dotted vertical table lines | REJECTED (`VISUAL_UI_GRIDLINES_NOT_PRINTED`) | NONPRINTING_UI |
| UF-06 template does not fully reproduce source | CONFIRMED | BLOCKING_FOR_SUBMISSION |

## 16. New authorship remediation preview — do not implement in this phase

New authority is 王凯伦 / `WANG Kailun` first author and corresponding author; 王琦 / `WANG Qi` second author; corresponding email `2024180231@mail.hfut.edu.cn`. Current ignored `metadata_private.yaml` instead names 王琦 / WANG Qi as corresponding author with no email.

Later work must update private metadata; any front-matter output policy; footer biography schema/data; English correspondence data; `full_manuscript_filter.lua`; `postprocess_full_manuscript_docx.py`; full and anonymous validators; anonymous sanitizer/exclusions; and the submission metadata report/portal checklist. Anonymous output must continue to contain no names, affiliation, biography, corresponding-author text, or email. No facts about Wang Qi may be guessed.

## 17. Final submission adaptation inventory

Open: Figure 1 → Visio; Figures 2/3 → Origin; equations → MathType; full first-page metadata/biographies; Word Desktop layout QA; anonymous Word QA; Document Inspector; and portal metadata. These items were inventoried only, not executed.

## 18. Required changes, manual changes, and protected items

Automated remediation later: encode Chinese-only abstract indents; affiliation punctuation/grouping; remove current inline correspondence behavior; model full footer fields without invented editorial dates; change corresponding-author authority; update assertions and anonymous exclusions.

Manual remediation later: obtain Wang Qi biography facts; decide applicable funding; construct MathType and editable Visio/Origin objects; perform Word Desktop visual/pagination QA, Document Inspector, and portal entry.

Must not change: received/revised dates, unless editorially assigned; table vertical borders; scientific content/evidence; reference metadata absent an original-source mismatch; or any status in this audit.

## 19. Proposed next work units, authority questions, and exact next action

1. **Phase 7.1 format-remediation design:** update the template/metadata/filter/postprocessor/validator contract for UF-01–UF-04, after approving an explicit footer responsibility matrix.
2. **Phase 7.2 authorship verification:** collect official Wang Qi biographical fields and confirm all-author biography expectation; do not use web inference.
3. **Phase 7.3 Word production:** create MathType/Visio/Origin final assets and conduct Desktop QA.

Open authority questions: whether all-author biographies apply beyond the two-author specimen; whether an unfunded paper should omit the funding line or use an approved absence statement; and exact handling of editorial received/revised dates. Exact next action: authorize the Phase 7.1 remediation design only after answering those questions; do not implement from this audit alone.
