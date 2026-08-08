#!/usr/bin/env python3
"""Validate Phase 2 figure/table manifests and empty Step 5 asset areas."""

from pathlib import Path
import csv
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
PHASE2_PLAN = ROOT / "docs/paper/phase2/PAPER_PHASE2_FIGURE_TABLE_PLAN_v1.0.csv"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fail(message):
    print(f"FAIL: {message}")
    return False


def check_manifest(path, id_field, expected_ids):
    rows = read_csv(path)
    ids = [row[id_field] for row in rows]
    ok = True
    allowed_statuses = {"PLANNED_FROM_PHASE2"}
    if path.name == "table_manifest.csv":
        allowed_statuses.add("PUBLICATION_STRUCTURE_READY")
    if ids != expected_ids:
        ok = fail(f"{path.name} IDs/order mismatch: {ids!r}")
    if len(ids) != len(set(ids)):
        ok = fail(f"{path.name} contains duplicate IDs")
    for row in rows:
        if row.get("status") not in allowed_statuses:
            ok = fail(f"{path.name} row {row.get(id_field)} has invalid status")
    return ok, rows


def check_plan_binding(manifest_rows, plan_rows, id_field):
    plan = {row["candidate_id"]: row for row in plan_rows}
    ok = True
    for row in manifest_rows:
        item_id = row[id_field]
        source = plan.get(item_id)
        if source is None:
            ok = fail(f"{item_id} missing from Phase 2 plan")
            continue
        planned_claims = set(filter(None, source["claim_ids"].split(";")))
        actual_claims = set(filter(None, row["claim_ids"].split(";")))
        if actual_claims != planned_claims:
            ok = fail(f"{item_id} claim binding mismatch: {actual_claims!r} != {planned_claims!r}")
    return ok


def check_equations():
    rows = read_csv(MANUSCRIPT / "equations/equation_manifest.csv")
    return not rows if not rows else fail("equation manifest must be header-only")


def check_empty_assets():
    ok = True
    output = MANUSCRIPT / "output"
    generated = [path for path in output.rglob("*") if path.is_file() and path.name != ".gitignore"]
    if generated:
        ok = fail(f"output contains generated files: {generated!r}")
    forbidden_extensions = {".vsdx", ".vssx", ".opju", ".origin", ".mwx", ".mtx"}
    forbidden_words = re.compile(r"(?:origin|visio|mathtype)", re.I)
    for path in MANUSCRIPT.rglob("*"):
        if not path.is_file() or path.name.startswith("README"):
            continue
        if path.suffix.lower() in forbidden_extensions or forbidden_words.search(path.name):
            ok = fail(f"formal authoring asset exists: {path}")
    return ok


def main():
    plan_rows = read_csv(PHASE2_PLAN)
    plan_ids = {row["candidate_id"] for row in plan_rows}
    if plan_ids != {"F1", "F2", "F3", "T1", "T2"}:
        print(f"FAIL: unexpected Phase 2 plan IDs: {plan_ids!r}")
        return 1
    figure_result, figure_rows = check_manifest(
        MANUSCRIPT / "figures/figure_manifest.csv", "figure_id", ["F1", "F2", "F3"]
    )
    table_result, table_rows = check_manifest(
        MANUSCRIPT / "tables/table_manifest.csv", "table_id", ["T1", "T2"]
    )
    checks = [
        figure_result,
        table_result,
        check_plan_binding(figure_rows, plan_rows, "figure_id"),
        check_plan_binding(table_rows, plan_rows, "table_id"),
        check_equations(),
        check_empty_assets(),
    ]
    if all(checks):
        print("PASS: figure/table manifests and empty asset boundaries are valid")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
