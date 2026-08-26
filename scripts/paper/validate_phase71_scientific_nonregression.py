#!/usr/bin/env python3
"""Reject uncontrolled manuscript-prose changes in the Phase 7.1 diff."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "docs/paper/manuscript/sections/00_title_abstract.md": (
        "Input Data-Path Reconstruction for Industrial Defect Detection on Jetson",
        "Input data-path reconstruction for industrial defect detection on Jetson",
    ),
    "docs/paper/manuscript/sections/01_introduction.md": ("# 0 引言", "# 0 引 言"),
}


def main() -> int:
    changed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "docs/paper/manuscript/sections"],
        cwd=ROOT, check=True, text=True, capture_output=True,
    ).stdout.splitlines()
    # Phase 7.1R1 intentionally keeps manuscript Markdown unchanged: heading
    # separator rendering is now deterministic in the DOCX filter.  Retain
    # the historical Phase 7.1 two-token allowance for replaying that commit.
    if not changed:
        print("PHASE7_1R2_SCIENTIFIC_NONREGRESSION=PASS")
        print("MANUSCRIPT_PROSE_DELTA=0; FORMAT_TEXT_LEDGER_DELTA=0")
        return 0
    if sorted(changed) != sorted(ALLOWED):
        print(f"FAIL: unexpected manuscript source files changed: {changed}")
        return 1
    for path, (old, new) in ALLOWED.items():
        diff = subprocess.run(
            ["git", "diff", "--unified=0", "HEAD", "--", path],
            cwd=ROOT, check=True, text=True, capture_output=True,
        ).stdout
        if f"-{old}" not in diff or f"+{new}" not in diff:
            print(f"FAIL: format-text ledger mismatch: {path}")
            return 1
    print("PHASE7_1_SCIENTIFIC_NONREGRESSION=PASS")
    print("MANUSCRIPT_PROSE_DELTA=0; FORMAT_TEXT_LEDGER_DELTA=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
