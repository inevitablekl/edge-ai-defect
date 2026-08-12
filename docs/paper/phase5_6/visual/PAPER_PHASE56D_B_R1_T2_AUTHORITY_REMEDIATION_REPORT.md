# Paper Phase 5.6D-B-R1 — Table 2 L4T Authority Remediation Report

## 1. Trigger

Phase 5.6E preflight stopped with `PHASE56E_SCIENTIFIC_BLOCKER` because the
active D-B Table 2 reported `L4T 36.4.3`, while the formal execution evidence
and current manuscript reported `L4T R36.5`. This R1 is an
`UPSTREAM_METADATA_AUTHORITY_CORRECTION`; it is not a new experiment,
measurement, platform change, or benchmark invalidation.

## 2. Incorrect Value

The superseded D-B Table 2 field was:

```text
L4T 36.4.3
```

## 3. Formal Authority

The corrected publication wording is:

```text
L4T R36.5
```

No JetPack-to-L4T inference was used.

## 4. Authority Sources

The correction is jointly supported by:

- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`,
  whose environment table records `R36.5`;
- `docs/paper/phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json`,
  whose raw `l4t_release` records R36 release revision 5.0;
- `docs/paper/manuscript/sections/04_experiment.md`, whose current experiment
  environment records `L4T R36.5`.

The formal report and raw environment record are now attached directly to the
T2 L4T cell in `phase56_visual_evidence_map.csv` and to the T2 manifest entry.

## 5. Root Cause

`36.4.3` was hard-coded in the D-A T2 specification, the historical candidate
generator, the D-B production generator, and the D-B production validator. The
active evidence map only pointed the general T2 platform row to
`phase56b_runtime_state.json`, which establishes runtime-state conclusions but
does not contain the L4T version. Consequently, deterministic generation and
validation reproduced the stale value without checking the formal execution
environment.

R1 corrects the active spec/production chain and adds exact source validation.
The historical candidate, candidate generator, and original D-B report remain
unchanged so the audit trail still shows where `36.4.3` appeared.

## 6. Files Corrected

- `visual/table2_platform_protocol_spec.md`: corrected the single L4T field and
  added the formal report/raw environment sources.
- `visual/phase56_visual_evidence_map.csv`: added the exact `T2_L4T` cell and
  its two-source provenance.
- `visual/scripts/generate_phase56d_production_tables.py`: bound T2 generation
  to the hashed formal report, raw environment, and current manuscript checks.
- `visual/scripts/validate_phase56d_production.py`: added R1 authority,
  stale-value rejection, frozen figure hashes, and non-target table hashes.
- `visual/production/tables/table2_platform_protocol_phase56.md`: regenerated
  the corrected T2 and source trace.
- `visual/production/phase56_visual_asset_manifest.json`: promoted the R1
  verdict and expanded the T2 source chain.
- `visual/production/phase56_visual_asset_validation.json`: regenerated with
  93 PASS checks and the R1 mutation disposition.
- `visual/production/phase56_visual_asset_sha256.txt`: regenerated after the
  active production chain and this report were finalized.
- this R1 remediation report.

## 7. Assets Proven Unchanged

The frozen production SVG hashes remain:

| Figure | SHA256 |
|---|---|
| F1 | `d5f449ecc1c174d4315876bb2faf38e5f09d1c0bf675861466e413184cb5a887` |
| F2 | `8e81ed1d50322d75c9170e99e6aa54bca9e180c79d2d8bfd947fbb81d045e605` |
| F3 | `881532ab226d72de92735892950d6dd97fef75e51ad390a1223c9827b0ddbdb1` |
| F4 | `8d2cb04c771c56b0fe7438cfbae07c4767b64db8553bf10c89ed6d9d67463a5e` |

The non-target table hashes also remain unchanged:

| Table | SHA256 |
|---|---|
| T1 | `789205d35cbccc1463eb0bc97b4b7208b33b44b2ee5717d2a6e42d3e84d5766e` |
| T3 | `6d5e028fd2e48edd9de9dc5a8cd8823a6748b37ea7e3801b280497a4f5ebf1d0` |
| T4 | `6710b9ac7018eadebcd543d4bd892c7d1e3ba60f4e6963d139295badf52287a9` |

T4's 42 classifications were not re-audited or changed. The caption freeze is
also byte-identical at
`a7401295a6571b85864869aa54468c73aa88b4b9390b4ef8991a420858f6bc26`.

## 8. Manifest and SHA Update

The active manifest and validation artifacts now use the verdict
`PHASE56_VISUAL_ASSETS_READY_R1` and the starting baseline
`e9e906dc2bbb1fc1ee74965fd149aac02dd0250f`. T2 changed from SHA256
`5a019055782b0337a9ffbe29aafc7033c107bea3e946c9ef22218f4ba9b68538`
to `41ea42c945ca60be8b6e957d019fd7a914c117b9ce155478ea94189c5874f309`.
The exhaustive SHA list was regenerated from the finalized production tree.

## 9. Validation

Commands:

```bash
python3 docs/paper/phase5_6/visual/scripts/generate_phase56d_production_tables.py
python3 docs/paper/phase5_6/visual/scripts/validate_phase56d_production.py
git diff --check
```

Results:

```text
formal report contains R36.5 = PASS
raw environment mapping is consistent = PASS
current manuscript experiment environment is R36.5 = PASS
active T2 is L4T R36.5 = PASS
active T2 contains L4T 36.4.3 = NO
generator authority is R36.5 = PASS
evidence map binds formal report + raw environment = PASS
validator requires R36.5 and rejects 36.4.3 = PASS
deterministic regeneration = PASS
F1–F4 frozen SVG hashes unchanged = PASS
T1/T3/T4 hashes unchanged = PASS
Level-A unchanged = PASS
Level-B unchanged = PASS
authoritative manuscript Markdown unchanged = PASS
DOCX unchanged = PASS
git diff --check = PASS
```

## 10. Scientific Consequence

There is no change to benchmark results, conclusions, experimental protocol,
calibration, runtime-state conclusions, contribution architecture, or any
Level-A/Level-B metric. The only scientific field changed is the erroneous T2
L4T metadata value.

## 11. Supersession

The original D-B report and commit remain historical provenance. R1 supersedes
only the D-B Table 2 field `L4T 36.4.3`; all other D-B visual and table
authorities remain in force. The active disposition is:

```text
PHASE56_VISUAL_ASSETS_READY_R1
```
