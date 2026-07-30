# P5R Evidence Index

## Reclassification

| Item | Result |
|---|---|
| Pilot attempts | capacity 1, 2, 4; all completed with 1100 accepted, 0 drop |
| Queue selection | all eligible; smallest eligible capacity = 1 |
| Formal attempts | six independent runs in the frozen 3-pair order |
| Formal accepted/processed | 5100 / 5100 for every run |
| Formal measured trace | 5000 complete frames for every run |
| Formal dropped frames | 0 for every run |
| Formal RUN SHA | all six equal `7e115aa5661f38864955bb9eb7481e86290d0a0cb55e6c308270401d683cd929` |
| Complete CYCLE SHA | all 28 complete cycles per run equal the P4 expected CYCLE SHA |
| Thermal status | `thermal_throttle_status=unavailable`, known limitation |
| Final verdict | `P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE` |

## Evidence paths

- Pilot raw Evidence: `p5_queue_pilot_v1/attempt_001/`
- Formal raw Evidence: `p5_serial_vs_pipeline_v1/attempt_001/`
- Historical report, retained unchanged:
  `p5_serial_vs_pipeline_v1/attempt_001/P5_QUEUE_PILOT_AND_FORMAL_BENCHMARK_REPORT.md`
- Protocol amendment: `P5R_PROTOCOL_AMENDMENT.md`
- Final reclassification: `P5_FINAL_RECLASSIFICATION_REPORT.md`

## Immutability statement

P5R did not modify raw trace, raw Result JSON, telemetry, hash, config, or
attempt-level files. The previous invalid-state report remains historical
Evidence: its conclusion was based on the superseded cross-window RUN-SHA
comparison. No benchmark, build, or runtime command was executed during P5R.

## Frozen identities

```text
Engine SHA:          6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
Manifest SHA:        39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63
ModelContract SHA:   9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190
Corpus SHA:          fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8
Executable SHA:      4d817adbac1b93a7fcbd14a923229d9dd4e8dfd9c442eb732d56a6d6e9e9d4dc
P4 CYCLE SHA:        6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3
```
