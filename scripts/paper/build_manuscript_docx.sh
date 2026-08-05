#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

show_order() {
  printf '%s\n' \
    '01 docs/paper/manuscript/sections/00_title_abstract.md' \
    '02 docs/paper/manuscript/sections/01_introduction.md' \
    '03 docs/paper/manuscript/sections/02_problem_definition.md' \
    '04 docs/paper/manuscript/sections/03_method.md' \
    '05 docs/paper/manuscript/sections/04_experiment.md' \
    '06 docs/paper/manuscript/sections/05_results.md' \
    '07 docs/paper/manuscript/sections/06_conclusion.md'
}

show_command() {
  printf '%s\n' 'Future full-copy candidate (not executed):'
  printf '%s\n' 'pandoc --defaults docs/paper/manuscript/config/pandoc_common.yaml --metadata-file docs/paper/manuscript/metadata/metadata_private.yaml --output docs/paper/manuscript/output/draft_full.docx docs/paper/manuscript/sections/00_title_abstract.md docs/paper/manuscript/sections/01_introduction.md docs/paper/manuscript/sections/02_problem_definition.md docs/paper/manuscript/sections/03_method.md docs/paper/manuscript/sections/04_experiment.md docs/paper/manuscript/sections/05_results.md docs/paper/manuscript/sections/06_conclusion.md'
  printf '%s\n' 'Future anonymous-copy candidate (not executed):'
  printf '%s\n' 'pandoc --defaults docs/paper/manuscript/config/pandoc_common.yaml --metadata-file docs/paper/manuscript/metadata/metadata_anonymous.yaml --output docs/paper/manuscript/output/draft_anonymous.docx docs/paper/manuscript/sections/00_title_abstract.md docs/paper/manuscript/sections/01_introduction.md docs/paper/manuscript/sections/02_problem_definition.md docs/paper/manuscript/sections/03_method.md docs/paper/manuscript/sections/04_experiment.md docs/paper/manuscript/sections/05_results.md docs/paper/manuscript/sections/06_conclusion.md'
  printf '%s\n' 'CSL_STATUS: PENDING_STEP6_POC'
}

case "${1-}" in
  --check)
    python3 scripts/paper/validate_manuscript_sources.py
    python3 scripts/paper/validate_citations.py
    python3 scripts/paper/validate_manuscript_assets.py
    ;;
  --show-order)
    show_order
    ;;
  --show-command)
    show_command
    ;;
  '')
    printf '%s\n' 'PHASE2_5_POC_NOT_AUTHORIZED_BY_THIS_STEP' >&2
    exit 2
    ;;
  *)
    printf 'Usage: %s [--check|--show-order|--show-command]\n' "$0" >&2
    exit 2
    ;;
esac
