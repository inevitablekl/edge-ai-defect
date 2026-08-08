#!/usr/bin/env python3
"""Validate the accepted manuscript citation and bibliography source layer."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"


def main():
    bib = MANUSCRIPT / "references/references.bib"
    bib_text = bib.read_text(encoding="utf-8")
    bib_keys = re.findall(r"^\s*@(?!(?:comment|preamble|string)\b)[A-Za-z]+\s*\{([^,]+),", bib_text, re.I | re.M)
    markdown = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((MANUSCRIPT / "sections").glob("*.md"))
    )
    citation_keys = re.findall(r"@([A-Za-z][A-Za-z0-9_.:-]*)", markdown)
    manual_numbers = re.findall(r"\[\s*\d+(?:\s*[,;，、-]\s*\d+)*\s*\]", markdown)
    unresolved = sorted(set(citation_keys) - set(bib_keys))
    if unresolved:
        print(f"FAIL: unresolved Markdown citation keys: {unresolved!r}")
        return 1
    if manual_numbers:
        print(f"FAIL: manual numeric citation patterns found: {manual_numbers!r}")
        return 1
    uncited = sorted(set(bib_keys) - set(citation_keys))
    print(f"PASS: bibliography entries={len(bib_keys)}; cited keys={len(set(citation_keys))}; unresolved=0; uncited={uncited!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
