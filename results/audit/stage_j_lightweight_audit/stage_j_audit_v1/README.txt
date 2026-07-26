Stage J Lightweight Research-Grade Audit

Audit ID: stage_j_audit_v1
Status: COMPLETE
Source HEAD: ceb188a3611e3a8e7705286f4000002e3329e64f

A. Scope
This is a research-grade lightweight audit of the Stage J CPU baseline chain.
It is not the original Stage J8 Deep Evidence Gate and does not perform
independent deep reconstruction. The audit is read-only: no benchmark or
inference was run, and J1-J7 Evidence, model, contract, corpus and runtime
configuration were not modified.

B. Verified assets
Model SHA256:
c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
Contract SHA256:
9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190
Corpus manifest SHA256:
235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab
Python reference SHA256:
1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7
Expected cycle SHA256:
dff5686b46de48416d9038ccc40b573eb1c59830ba9e96eac5becbdb6bb0746f

C. Stage status
J1 COMPLETE; J2 COMPLETE; J3 COMPLETE_WITH_ACCEPTED_THIRD_PARTY_LIMITATION;
J4 COMPLETE_WITH_ACCEPTED_J4_2_LIMITATION; J5.1-J5.6 COMPLETE;
J6 COMPLETE_WITH_RESEARCH_GRADE_EVIDENCE; J7 COMPLETE.

D. Experimental results summary
Controlled k1: five independent formal runs passed; 560 processed frames per
run; mean process-wall throughput 2.3086948023 FPS. The timing limitation is
documented in the J5.5 Evidence.
Tuned k5: five independent formal runs passed under CPU affinity 1-5 with ORT
intra/inter threads 5/1.
30-minute stability: 1800.0649718600034 seconds; 743 cycles; 14860 frames;
zero failures; correctness passed; no cycle hash drift.

E. Limitations
J5.5 retains its documented limitation: whole-process timing was available,
while per-frame timing distributions and independently reconstructable raw
telemetry were unavailable. J6 recorded unavailable power VDD_IN and other
interfaces as unavailable; no values were inferred. This audit does not make
a production-readiness claim.

F. Final decision
The Stage J research baseline is complete. The lightweight audit is complete.
The original deep reconstruction was not executed. Stage T may be considered
in next-stage planning review, but execution remains NOT_AUTHORIZED until the
required governance and authorization conditions are separately satisfied.
J9 remains NOT_STARTED.
