#!/usr/bin/env python3
"""Validate the structure-only manuscript source contract."""

from pathlib import Path
import hashlib
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
EXPECTED_HASH = "416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7"
CHAPTERS = [
    ("00_title_abstract.md", "# 题名与摘要"),
    ("01_introduction.md", "# 0 引言"),
    ("02_problem_definition.md", "# 1 系统对象与问题定义"),
    ("03_method.md", "# 2 数据路径优化方法"),
    ("04_experiment.md", "# 3 实验设计"),
    ("05_results.md", "# 4 结果与分析"),
    ("06_conclusion.md", "# 5 结论"),
]


def fail(message):
    print(f"FAIL: {message}")
    return False


def validate_chapters():
    ok = True
    chapter_dir = MANUSCRIPT / "sections"
    actual = sorted(path.name for path in chapter_dir.glob("*.md"))
    expected = [name for name, _ in CHAPTERS]
    if actual != expected:
        ok = fail(f"chapter set/order mismatch: {actual!r}")
    for name, heading in CHAPTERS:
        path = chapter_dir / name
        if not path.is_file():
            ok = fail(f"missing chapter: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("STRUCTURE_ONLY", "PHASE_3_NOT_AUTHORIZED", "NO_MANUSCRIPT_PROSE"):
            if marker not in text:
                ok = fail(f"{name} lacks {marker}")
        if heading not in text:
            ok = fail(f"{name} has wrong frozen heading")
        without_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        content_lines = [
            line.strip()
            for line in without_comments.splitlines()
            if line.strip()
        ]
        allowed = {heading, "<!-- CONTENT_PENDING_PHASE_3 -->"}
        unexpected = [line for line in content_lines if line not in allowed]
        if unexpected:
            ok = fail(f"{name} contains non-skeleton content: {unexpected!r}")
        if re.search(r"@[A-Za-z][A-Za-z0-9_.:-]*", text):
            ok = fail(f"{name} contains a citation key")
        if re.search(r"\[\s*\d+(?:\s*[,;，、-]\s*\d+)*\s*\]", text):
            ok = fail(f"{name} contains manual numeric citation syntax")
    return ok


def validate_bibliography():
    path = MANUSCRIPT / "references/references.bib"
    text = path.read_text(encoding="utf-8")
    entries = re.findall(r"^\s*@(?!(?:comment|preamble|string)\b)[A-Za-z]+\s*\{", text, re.I | re.M)
    return not entries if not entries else fail(f"references.bib has formal entries: {entries!r}")


def validate_metadata():
    ok = True
    for path in (MANUSCRIPT / "metadata").glob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I):
            ok = fail(f"metadata contains an email-like value: {path}")
        if re.search(r"\b(?:\+?\d[\d -]{7,}\d)\b", text):
            ok = fail(f"metadata contains a phone-like value: {path}")
        if path.name == "metadata_common.yaml":
            for marker in ("TOOLCHAIN_SKELETON_ONLY", "PHASE_3_NOT_AUTHORIZED"):
                if marker not in text:
                    ok = fail(f"metadata_common.yaml lacks {marker}")
        if path.name == "metadata_anonymous.yaml":
            for marker in ("HIDDEN", "ANONYMOUS"):
                if marker not in text:
                    ok = fail(f"metadata_anonymous.yaml lacks anonymous marker {marker}")
    return ok


def validate_template_hash():
    path = MANUSCRIPT / "template/hfut_journal_reference_v1.0.docx"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest == EXPECTED_HASH if digest == EXPECTED_HASH else fail(
        f"reference.docx SHA256 mismatch: {digest}"
    )


def main():
    checks = [validate_chapters(), validate_bibliography(), validate_metadata(), validate_template_hash()]
    if all(checks):
        print("PASS: manuscript sources are structure-only and privacy-safe")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
