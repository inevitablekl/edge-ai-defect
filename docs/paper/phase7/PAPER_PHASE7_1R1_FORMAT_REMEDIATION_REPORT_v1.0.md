# Phase 7.1R1 HFUT run-level format remediation report

## Verdict

`PHASE_7_1R1_FORMAT_FIXED_WORD_PAGINATION_CANDIDATE_SELECTION_REQUIRED`

`RUN_LEVEL_FORMAT_SATURATION = YES`; `SOURCE_ROLE_CLASSIFICATION = YES`; `UNCLASSIFIED_RELEVANT_RUNS = 0`; `KNOWN_RUN_LEVEL_MISMATCHES = 0` after the deterministic template/filter/validator changes. Microsoft Word pagination remains pending candidate selection.

## Finding ledger

| Finding | Verdict | Evidence and remediation |
| --- | --- | --- |
| R1-F01 | CONFIRMED | P004 black `摘  要` has Heiti 9 pt without `w:b`; removed explicit bold. |
| R1-F02 | CONFIRMED | P005 black `关键词` has Heiti 9 pt without `w:b`; removed explicit bold. |
| R1-F03 | CONFIRMED | P006 follows P005 and precedes P007; CLC line now follows CN keywords. |
| R1-F04 | CONFIRMED | P006 is emitted as label/value/document-label/value runs. |
| R1-F05 | CONFIRMED | P006 `文献标识码：` black run has `w:b`; dedicated char style added. |
| R1-F06 | CONFIRMED | P012 uses numId 2; literal number/tab and two-space `引  言` result are validated. |
| R1-F07 | CONFIRMED | P015 number-only `w:b`; H1 is mixed runs. |
| R1-F08 | CONFIRMED | P016 number-only `w:b`; H2 is mixed runs. |
| R1-F09 | REJECTED | P017 has no explicit bold runs; H3 remains non-bold Kaiti. |
| R1-F10 | CONFIRMED | P024 is `FORMAT_DOCUMENT_OWN_HEADING`, not a generic manuscript H1 specimen. |
| R1-F11 | CONFIRMED | Word page-5 blank space is a float/geometry interaction; Word re-review required. |
| R1-F12 | CONFIRMED | Word page-6 blank space is a float/geometry interaction; Word re-review required. |
| R1-F13 | CONFIRMED | Full reference run/example audit completed; fixed 360 twips is honestly project-stable. |

## Heading contract

| Element | Number font | Number size | Number bold | Separator | Title font | Title size | Title bold | Paragraph alignment | Source paragraph |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Introduction | Heiti | 14 pt | true (numbering level) | two preserved spaces (420-twip tab equivalent) | Heiti | 14 pt | true | left | HFUT_FMT_DOC P012 |
| H1 | Heiti | 14 pt | true | two spaces | Heiti | 14 pt | false | left | HFUT_FMT_DOC P015 |
| H2 | Heiti | 10.5 pt | true | two spaces | Heiti | 10.5 pt | false | left | HFUT_FMT_DOC P016 |
| H3 | Kaiti | 10.5 pt | false | two spaces | Kaiti | 10.5 pt | false | left | HFUT_FMT_DOC P017 |

## Front-matter contract

| Element | Font | Size | Bold | Order | Source runs |
| --- | --- | --- | --- | --- | --- |
| CN Abstract label | Heiti | 9 pt | false | 4 | P004 r1/r7 |
| CN Keywords label | Heiti | 9 pt | false | 5 | P005 r1/r7 |
| CLC label | Heiti | 9 pt | false | 6 | P006 r1 |
| CLC value | Songti | 9 pt | false | 6 | P006 r2-r3; red annotation excluded |
| Document-code label | Heiti | 9 pt | true | 6 | P006 r9 |
| Document-code value | Songti | 9 pt | false | 6 | P006 r10 |
| Abstract EN label | Times New Roman | 10.5 pt | true | 9 | P010 r1-r2 |
| Key words EN label | Times New Roman | 10.5 pt | `Key words` true; colon false | 10 | P011 r1-r2 |
