#!/usr/bin/env python3
"""Validate the intentionally empty Step 5 citation layer."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"


def main():
    bib = MANUSCRIPT / "references/references.bib"
    bib_text = bib.read_text(encoding="utf-8")
    entry_matches = re.findall(
        r"^\s*@(?!(?:comment|preamble|string)\b)[A-Za-z]+\s*\{",
        bib_text,
        re.I | re.M,
    )
    if entry_matches:
        print(f"FAIL: expected zero BibTeX entries, found {len(entry_matches)}")
        return 1

    # Governance documents may quote the prohibited syntax as documentation;
    # only manuscript section source is citation-bearing content at this stage.
    markdown = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((MANUSCRIPT / "sections").glob("*.md"))
    )
    citation_keys = re.findall(r"@[A-Za-z][A-Za-z0-9_.:-]*", markdown)
    manual_numbers = re.findall(r"\[\s*\d+(?:\s*[,;，、-]\s*\d+)*\s*\]", markdown)
    if citation_keys:
        print(f"FAIL: Markdown citation keys found: {citation_keys!r}")
        return 1
    if manual_numbers:
        print(f"FAIL: manual numeric citation patterns found: {manual_numbers!r}")
        return 1
    print("PASS: BibTeX and Markdown citation key counts are zero; no unresolved citations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
