# Training Archive Index

The completed NEU-DET training stage is preserved in three independent, Git-excluded archives.

| Archive | Purpose | SHA256 |
|---|---|---|
| `edge-ai-defect_training_stage_20260712.tar.gz` | Original training-stage reports, test artifacts, and lightweight experiment records | `a8b62be94e08f1d3e41c6e589f2171b001490cf772b0ab13ca60fa4d41660756` |
| `edge-ai-defect_training_evidence_patch_20260712.tar.gz` | Machine-readable metrics, effective args, commands, and evidence | `7c44f5ad992a6b539027d29e249e9f87717661b6750552b33f0a2a8015ac8341` |
| `edge-ai-defect_training_checkpoints_patch_20260712.tar.gz` | All nine formal-training `best.pt` checkpoints and metadata | `a50525dc3e68a569e81d6319b9bf9d9cc43f9db26c5df3d87e09f48b8a765847` |

Canonical frozen model SHA256:

```text
5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7
```

The checkpoint archive member `checkpoints/seed7/best.pt` has the same SHA256 as the frozen model. The archive files and model weights are not tracked by Git; only lightweight documentation and provenance are committed. Archive integrity is verified using each external SHA256 record and internal MANIFEST.

Keep at least two independent local copies of these archives. This index intentionally records no workstation paths, server addresses, credentials, or other sensitive storage details.
