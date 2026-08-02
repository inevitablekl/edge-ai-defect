# Stage R R0 Evidence Provenance Remediation

Initial state:
R0 commit `60a04a2`.

Detected by:
R1 entry verification.

Problem:
The two `source_evidence_sha256` fields contained descriptive placeholders
instead of SHA256 digests for a single, reviewable source-evidence aggregate.

Classification:
R0 Evidence provenance defect. No production or plan defect.

Remediation:
Added two aggregate source-evidence files, replaced both values with full
64-character SHA256 digests, and separated observed environment facts from
the frozen Stage R experiment contract.

Experiments executed:
none.

Production code modified:
none.

Official R0 gate after remediation:
`R0_PASS`.

R1:
`NOT EXECUTED` — `NOT AUTHORIZED UNTIL USER REVIEW`.
