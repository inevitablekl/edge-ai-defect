# Paper Phase 3 Literature Archive Inventory Report v1.1

## 1. Status

`LITERATURE_ARCHIVE_INVENTORIED_V1_1`

This v1.1 register supersedes v1.0 for current Phase 3 use. The v1.0
acquisition snapshot is retained unchanged.

## 2. Archive scope

- Archive: `/home/orin/paper-external-inputs/hfut-journal/phase3_literature_v1`
- Raw assets: 32
- Unique contents: 31
- Exact duplicate groups: 1
- PDFs remain external assets and are not copied into Git.
- Archive acquisition and formal bibliography admission are separate controls.

## 3. Stable identity and additions

RAW001–RAW030 are copied from the v1.0 register without reordering or
renumbering. Only the following assets were appended:

| ID | File | Size bytes | SHA256 | PDF pages | arXiv candidate | Admission relation |
|---|---|---:|---|---:|---|---|
| RAW031 | `reddi_et_al_2019_mlperf_inference_benchmark.pdf` | 1185996 | `ab71faac2c06fa5c317f559e3e96c7baa24a7d15bcf757efcee085ee1a3a1efd` | 15 | `1911.02549` | P04 / A14 |
| RAW032 | `MLPerf Mobile Inference Benchmark arXiv PDF.pdf` | 2444614 | `078ebeae4f86ee83280edf061704a646ac9c811d94ad82500b635ae2d279b6c1` | 18 | `2012.02328` | supplementary L6 / A15; no P ID |

Neither new SHA256 matches any RAW001–RAW030 SHA256. Both new assets are
unique. The two existing Jetson carrier-board files remain the only duplicate
group:

- DG001 SHA256: `4a0f7ba948bce4881e176f0f8636ef3dbd40e3df9dd33134e6a7433359d18c02`
- canonical: `Jetson-Orin-Nano-DevKit-Carrier-Board-Specification_SP-11324-001_v1.3.pdf`
- exact duplicate retained: `Jetson-Orin-Nano-DevKit-Carrier-Board-Specification_SP-11324-001_v1.3 (1).pdf`

## 4. Formal retrieval decision

- P04 = `reddi_et_al_2019_mlperf_inference_benchmark.pdf`
- P04 status: `MAIN_AI_ADMISSION_MATCH`
- Basis: Paper Phase 3 Main AI Literature Admission Review, 2026-08-07,
  L6 final closure.
- `MLPerf Mobile Inference Benchmark arXiv PDF.pdf` receives no new P ID and
  remains a supplementary L6 source.

## 5. Generated metadata

- `metadata/PAPER_PHASE3_LITERATURE_RAW_INVENTORY_v1.1.csv`
- `metadata/PAPER_PHASE3_LITERATURE_RAW_SHA256_v1.1.txt`
- v1.0 metadata files were not overwritten.

## 6. Boundary

The archive inventory records acquisition identity only. It does not admit a
source into the formal bibliography. That decision is recorded separately in
`PAPER_PHASE3_LITERATURE_ADMISSION_REGISTER_v1.0.csv`.
