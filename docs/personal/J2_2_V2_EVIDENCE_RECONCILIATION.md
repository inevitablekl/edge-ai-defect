# J2.2 v2 Evidence Reconciliation v1

Status: `FROZEN`

## 1. Scope

This document reconciles only non-build evidence gaps in the PASS
`j2.2_formal_clean_v2` attempt. It does not modify the formal attempt, formal
source, build or SDK; it does not generate a new build result; and it does not
replace J2.3 Published Evidence. No ORT rebuild, install, test, inference,
benchmark, J2.3, J2.4, J2.5 or J3 operation is part of this reconciliation.

## 2. Immutable Inputs

| Input | Value |
|---|---|
| Reconciliation repository HEAD | `5713615ec2ae9ccddabe9d732996e9a2116edd8a` |
| Formal attempt repository source commit | `26c72c63d9466899c53bd5edaeb232d0f002fcf0` |
| D044 commit | `26c72c63d9466899c53bd5edaeb232d0f002fcf0` |
| D045 contract commit | placeholder; pending owner-reviewed repository commit |
| Formal attempt ID | `j2.2_formal_clean_v2` |
| Formal attempt manifest SHA256 | `a4028cbca5ced9abbd95d1aedaa5f83b55ee062820700fb44fbd6e479f2d2b32` |
| ORT tag | `v1.23.2` |
| ORT source commit | `a83fc4d58cb48eb68890dd689f94f28288cf2278` |
| ORT VERSION_NUMBER | `1.23.2` |
| Formal SDK main library SHA256 | `6eb17924b41234997354dd006b997ef079a10ddbe5fe082ae6373b6581b36740` |
| v1 relation | `j2.2_formal_clean_v1` is `BLOCKED` and immutable |
| Historical development build relation | technically valid artifact; `SUPERSEDED` as formal Evidence authority |

All paths in this document are logical or repository-relative. Local staging
paths are intentionally omitted.

## 3. Attempt Integrity

The immutable attempt contains exactly these 11 regular files:

```text
README.txt
artifact_inventory.txt
build_configuration.txt
commands.txt
environment.txt
exit_codes.tsv
sha256sums.txt
source_provenance.txt
stderr.log
stdout.log
timestamps.tsv
```

The attempt manifest hash is exact and `sha256sum -c sha256sums.txt` reports
10/10 `OK` entries. The original attempt is unchanged. The substantive build
and install stdout/stderr records remain complete in their original files;
the build output reaches the final target and the install output is preserved
in the same raw stdout record after the build boundary.

## 4. Command-to-Exit Reconciliation

The table below reconciles the immutable `commands.txt` and
`exit_codes.tsv`. A dash means that no historical independent exit row is
claimed. It is not replaced with a current verification exit code.

| Command sequence | Command ID | Semantic operation | Exit row(s) | Exit code | Classification | Basis |
|---:|---|---|---|---:|---|---|
| 001 | `repository_gate` | Repository/D044 live-status gate | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 002 | `frozen_asset_hashes` | Frozen plan/task/inventory hashes | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 003 | `v1_immutability` | v1 roots and manifest check | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 004 | `v2_path_disk_gate` | v2 roots and disk gate | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 005 | `external_cmake_verification` | CMake and archive verification | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 006 | `attempt_initialization` | Fixed roots and attempt-file initialization | — | — | `HISTORICAL_EXIT_CODE_NOT_RECORDED` | Recorded command only |
| 007 | `environment_preflight` | Read-only environment preflight | 1 | 0 | `PASS` | Exit row uses semantic ID |
| 008a | `clone_launcher` | Failed logging redirection before clone | 2a | 1 | `HARMLESS_WRAPPER_TYPO` | No clone executed |
| 009 | `clone_superproject` | Official ORT v1.23.2 clone | 3 | 0 | `PASS` | Recorded successful clone |
| 010 | `top_level_revision_verification` | Commit/tag/version verification | 4 | 0 | `PASS` | Recorded source gate |
| 011 | `submodule_sync` | Recursive submodule sync | 5 | 0 | `PASS` | Recorded successful sync |
| 012 | `submodule_update` | Recursive submodule initialization | 6 | 0 | `PASS` | Recorded successful update |
| 013a | `snapshot_logging_wrapper` | Failed snapshot logging wrapper | 7a | 1 | `RECORDED_NON_SUBSTANTIVE_FAILURE` | Read-only snapshots ran but were not saved |
| 014 | `stable_snapshot_1_recorded` | First source/submodule snapshot | 8, 9 | 0, 0 | `PASS` | Two operations in one command |
| 015 | `sleep_2_seconds` | Inter-snapshot sleep | — | — | `NON_SUBSTANTIVE_NO_INDEPENDENT_ROW` | No build/install gate is affected |
| 016 | `stable_snapshot_2_recorded` | Second source/submodule snapshot | 10, 11 | 0, 0 | `PASS` | Two operations in one command |
| 017 | `source_diff_gate` | Worktree/index source diff gate | 12, 13 | 0, 0 | `PASS` | Both diff checks succeeded |
| 018a | `provenance_logging_wrapper` | Failed provenance logging wrapper | 14a | 1 | `RECORDED_NON_SUBSTANTIVE_FAILURE` | Read-only inventory ran but was not saved |
| 019 | `source_provenance_inventory_recorded` | Source provenance and aggregate record | 15 | 0 | `PASS` | Recorded provenance output |
| 020a | `help_logging_wrapper` | Failed help logging wrapper | 16a | 1 | `HARMLESS_WRAPPER_TYPO` | Help was not executed by wrapper |
| 021 | `build_sh_help` | Actual `build.sh --help` | 17 | 0 | `PASS` | Correct command executed later |
| 022 | `prebuild_source_gate` | Pre-build source and empty-build gate | 18–21 | 0, 0, 0, 0 | `PASS` | All four gate rows succeeded |
| 023 | `formal_build` | Formal CPU-only Release build | 24 | 0 | `PASS` | Substantive build exit recorded |
| 024 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 025 | `postbuild_source_gate` | Post-build source and output gate | 25–28 | 0, 0, 0, 0 | `PASS` | All four gate rows succeeded |
| 026 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 027 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 028 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 029 | `install` | Independent CMake install | 29 | 0 | `PASS` | Substantive install exit recorded |
| 030 | `sdk_validation` | Required SDK paths/symlinks/package checks | 30–32 | 0, 0, 0 | `PASS` | Recorded validation rows |
| 031 | `artifact_verification` | Initial artifact probe | 33 | 0 | `SUPERSEDED_NON_AUTHORITATIVE_CHECK` | Corrected verification is authoritative |
| 032 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 033 | — | No command entry recorded | — | — | `NOT_RECORDED_RESERVED_SEQUENCE` | No execution is inferred |
| 034 | `final_build_config_and_artifact_facts` | Corrected build/configuration facts | 34 | 0 | `PASS` | Recorded final facts |
| 035 | `corrected_artifact_verification` | Corrected public-layout artifact verification | 35 | 0 | `PASS` | Authoritative corrected check |
| 036 | `local_manifest` | Exact attempt inventory/manifest | 36 | 0 | `PASS` | Substantive manifest exit recorded |

The integer labels 008, 013, 018 and 020 are represented by the actual
wrapper IDs 008a, 013a, 018a and 020a in the immutable command log. All
substantive build, install, artifact and manifest operations map to recorded
successful exit rows; therefore the reconciliation is not blocked.

## 5. Wrapper Typo Reconciliation

| Original ID | Stage | Observed exit | Substantive operation executed | Correct later command | Side effect | Classification |
|---|---|---:|---|---|---|---|
| 008a | Clone logging wrapper | 1 | No | 009 clone | No file written to wrong target; clone did not run in wrapper | `HARMLESS_WRAPPER_TYPO` |
| 013a | Snapshot logging wrapper | 1 | Yes, read-only | 014 and 016 snapshots | Source was not changed; wrapper output was not saved | `RECORDED_NON_SUBSTANTIVE_FAILURE` |
| 018a | Provenance logging wrapper | 1 | Yes, read-only | 019 provenance inventory | Source was not changed; wrapper output was not saved | `RECORDED_NON_SUBSTANTIVE_FAILURE` |
| 020a | Help logging wrapper | 1 | No | 021 help | No file written to wrong target; help did not run in wrapper | `HARMLESS_WRAPPER_TYPO` |

No later evidence was copied from another attempt or spliced into v2.

## 6. Timestamp Reconciliation

The following events are copied exactly from the immutable attempt. Values are
not recomputed from filesystem metadata.

| Event | Historical ISO-8601 local time | Historical monotonic ns |
|---|---|---:|
| `attempt_start` | `2026-07-23T20:03:09+08:00` | 3189146463305 |
| `environment_preflight_end` | `2026-07-23T20:03:09+08:00` | 3189288443424 |
| `source_clone_start` | `2026-07-23T20:03:37+08:00` | 3217253286755 |
| `source_clone_end` | `2026-07-23T20:06:16+08:00` | 3375978118867 |
| `submodule_update_start` | `2026-07-23T20:07:08+08:00` | 3428246139549 |
| `submodule_update_end` | `2026-07-23T20:07:30+08:00` | 3450551615720 |
| `source_gate_snapshot_1` | `2026-07-23T20:08:46+08:00` | 3525892210122 |
| `source_gate_snapshot_2` | `2026-07-23T20:08:49+08:00` | 3528641556581 |
| `build_start` | `2026-07-23T20:11:37+08:00` | 3697492521487 |
| `build_end` | `2026-07-23T21:16:20+08:00` | 7579664886582 |
| `install_start` | `2026-07-23T21:17:16+08:00` | 7636222724211 |
| `install_end` | `2026-07-23T21:17:16+08:00` | 7636423208431 |
| `local_manifest_start` | `2026-07-23T21:22:21+08:00` | 7941505473354 |
| `local_manifest_end` | `2026-07-23T21:22:21+08:00` | 7941543513616 |

| Missing event | Value | Status | No backfill |
|---|---|---|---|
| `source_ready` | `null` | `not_recorded` | `true` |
| `verification_end` | `null` | `not_recorded` | `true` |
| `attempt_end` | `null` | `not_recorded` | `true` |

Build and install boundaries remain verifiable from their recorded monotonic
events, exit rows and raw logs. Build elapsed time is approximately 3882.17 s
(reported operationally as 3883 s); install elapsed time is approximately
0.020 s.

## 7. Source Provenance Reconciliation

Read-only source verification passed:

- tag: `v1.23.2`;
- commit: `a83fc4d58cb48eb68890dd689f94f28288cf2278`;
- `VERSION_NUMBER`: `1.23.2`;
- top-level status: clean;
- recursive submodule status: clean, with no abnormal prefix;
- expected/current submodule commits agree.

The four recursive submodules are:

```text
419021fa040428bc69ef1559b325addb8e10211f cmake/external/emsdk
7a2ed51a6b682a83e345ff49fc4cfd7ca47550db cmake/external/libprotobuf-mutator
e709452ef2bbc1d113faf678c24e6d3467696e83 cmake/external/onnx
a2e59f0e7065404b44dfe92a28aca47ba1378dc4 cmake/external/onnx/third_party/pybind11
```

### Canonical aggregate

Algorithm name: `stage_j_ort_source_aggregate_v1`

Canonical payload encoding is UTF-8 with LF line endings:

```text
schema=stage_j_ort_source_aggregate_v1
superproject_commit=<commit>
entries:
<mode><TAB><content_identity><TAB><repo-relative-path>
...
submodules:
<commit><TAB><repo-relative-submodule-path>
...
```

The superproject index is read with `git ls-files --stage -z`. Entries are
sorted by repository-relative path UTF-8 bytes. For ordinary blobs and
symlinks, content identity is SHA256 of the Git object blob bytes obtained
with `git cat-file`; worktree symlinks are never followed. Gitlinks retain
mode `160000` and use the recorded submodule commit as identity. Recursive
submodules must have a normal prefix and matching current/expected commits,
then are sorted by UTF-8 path bytes. The SHA256 is computed over the complete
canonical payload bytes.

Observed result:

| Field | Value |
|---|---:|
| Superproject commit | `a83fc4d58cb48eb68890dd689f94f28288cf2278` |
| Git index entry count | 9431 |
| Recursive submodule count | 4 |
| Canonical payload bytes | 1247113 |
| Canonical payload SHA256 | `c060f538ac72eb5d801781ac1c5fb6c1a12001ce57f873a952ea37aebce3f81c` |

The following code is an independently reproducible implementation. Set
`SOURCE_ROOT` to the source checkout before running it; it writes no files.

```python
import hashlib
import os
import subprocess
from pathlib import Path

root = Path(os.environ["SOURCE_ROOT"])

def git(*args):
    return subprocess.check_output(["git", *args], cwd=root)

superproject = git("rev-parse", "HEAD").decode().strip()
entries = []
for record in git("ls-files", "--stage", "-z").split(b"\0"):
    if not record:
        continue
    meta, path_bytes = record.split(b"\t", 1)
    mode_bytes, oid_bytes, _stage = meta.split()
    mode = mode_bytes.decode("ascii")
    oid = oid_bytes.decode("ascii")
    identity = oid if mode == "160000" else hashlib.sha256(
        git("cat-file", "blob", oid)
    ).hexdigest()
    entries.append((path_bytes, mode, identity,
                    path_bytes.decode("utf-8")))
entries.sort(key=lambda item: item[0])

submodules = []
for line in git("submodule", "status", "--recursive").splitlines():
    if not line:
        continue
    if line[:1] != b" ":
        raise RuntimeError("abnormal submodule prefix")
    commit, path, *_ = line[1:].decode("utf-8").split()
    submodules.append((path.encode("utf-8"), commit, path))
submodules.sort(key=lambda item: item[0])

lines = [
    "schema=stage_j_ort_source_aggregate_v1",
    f"superproject_commit={superproject}",
    "entries:",
]
lines.extend(f"{mode}\t{identity}\t{path}"
             for _path_bytes, mode, identity, path in entries)
lines.append("submodules:")
lines.extend(f"{commit}\t{path}"
             for _path_bytes, commit, path in submodules)
payload = ("\n".join(lines) + "\n").encode("utf-8")
print("entry_count", len(entries))
print("submodule_count", len(submodules))
print("payload_sha256", hashlib.sha256(payload).hexdigest())
```

The historical recorded aggregate
`4f460795adeab01ac3a0b207ff18ec9d6af01d3957456af59dcb201645e9c5ab` remains
`historical_recorded_not_future_authority`. Its original algorithm was not
persisted, so it is not claimed to be independently rebuildable and is not
required to equal the canonical v1 aggregate.

## 8. Build and Install Integrity

- Formal build exit row: `24 / formal_build / 0`.
- Independent install exit row: `29 / install / 0`.
- Build: native AArch64, Release, shared library, CPU-only, external CMake
  3.28.6, parallel 4, upstream tests skipped.
- The raw stdout reaches `[100%] Built target onnxruntime_test_all`; raw stderr
  contains compiler warnings but no unexplained fatal build failure.
- The install manifest has 24 recorded entries and 23 unique paths. The one
  duplicate entry is `include/onnxruntime/cpu_provider_factory.h` and is
  informational. Unexpected installed unique files: 0.
- The formal attempt retains the complete raw stdout/stderr files and the
  local manifest verification is exit 0.

## 9. SDK Integrity

- Main library SHA256:
  `6eb17924b41234997354dd006b997ef079a10ddbe5fe082ae6373b6581b36740`.
- Main library is ELF64, little-endian, AArch64.
- SONAME is `libonnxruntime.so.1`.
- Symlink chain is `libonnxruntime.so` → `libonnxruntime.so.1` →
  `libonnxruntime.so.1.23.2`.
- `ldd` reports no `not found` dependency. The main library has no CUDA,
  TensorRT or cuDNN NEEDED dependency.
- The CMake package uses relocatable prefix computation and contains no
  private staging path.
- SDK binary execution, CTest, inference, benchmark and RPATH smoke were not
  executed by the J2.2 contract and remain outside this reconciliation.

## 10. Limitations

- Three historical timestamp events are `null`, `not_recorded`, with
  `no_backfill=true`.
- Several preflight or wrapper operations have no independent historical exit
  row; missing rows are not fabricated.
- The historical aggregate algorithm was not persisted.
- The canonical aggregate is a post-PASS reconciliation identity, not
  historical timestamp evidence.
- These limitations do not affect the formal build, install or SDK technical
  conclusions because their substantive operations have successful exit rows,
  preserved logs and matching artifacts.

## 11. Rebuild Decision

```text
rebuild_required=false
```

The only future rebuild invalidation conditions are:

- ORT tag, commit or version changes;
- any recursive submodule commit changes;
- compiler, external CMake or formal build command changes;
- SDK library, header, symlink or SONAME changes;
- main library SHA256 drift;
- corruption of formal build/install key logs or exit codes;
- a canonical source aggregate mismatch when recomputed under the same source
  state.

## 12. J2.3 Entry Gate

This reconciliation is `PASS`; therefore J2.3 is `READY`. J2.3 has not been
executed. It must use only the formal v2 SDK, must not use the historical
development SDK, and must not rebuild ORT. J2.3 Published Evidence must cite
D045 and this reconciliation document.
