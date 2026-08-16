#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

full_sections=(
  docs/paper/manuscript/sections/00_title_abstract.md
  docs/paper/manuscript/sections/01_introduction.md
  docs/paper/manuscript/sections/02_problem_definition.md
  docs/paper/manuscript/sections/03_method.md
  docs/paper/manuscript/sections/04_experiment.md
  docs/paper/manuscript/sections/05_results.md
  docs/paper/manuscript/sections/06_conclusion.md
)

validate_current_figure_assets() {
  local phase56_dir="docs/paper/phase5_6/visual/production/figures"
  local phase57_dir="docs/paper/phase5_7/visual/production/figures"
  local source
  for source in \
    "$phase56_dir/fig1_hero_data_path_phase56.png" \
    "$phase57_dir/fig2_technical_implementation_phase57b.png" \
    "$phase56_dir/fig3_main_e2e_phase56.png" \
    "$phase56_dir/fig4_run_level_distribution_phase56.png"; do
    if [[ ! -s "$source" ]]; then
      printf 'PHASE56_FIGURE_ASSET_VALIDATION_FAILED: source is missing: %s\n' "$source" >&2
      return 1
    fi
  done
  printf '%s\n' 'PHASE57B_DOCX_FIGURE_PAYLOADS=PNG reason=LibreOffice_SVG_blank_render'
}

build_full() {
  local pandoc_bin="${PAPER_PANDOC_BIN:-/home/orin/.local/bin/pandoc}"
  local output_dir="docs/paper/manuscript/output"
  local raw_docx="$output_dir/draft_full_raw.docx"
  local full_docx="$output_dir/draft_full.docx"
  local csl_path="docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl"

  if [[ ! -x "$pandoc_bin" ]]; then
    printf 'FULL_BUILD_FAILED: Pandoc executable unavailable: %s\n' "$pandoc_bin" >&2
    return 1
  fi
  if [[ ! -s docs/paper/manuscript/metadata/metadata_private.yaml ]]; then
    printf '%s\n' 'FULL_BUILD_FAILED: local private metadata is missing' >&2
    return 1
  fi
  if [[ ! -s "$csl_path" ]]; then
    printf 'FULL_BUILD_FAILED: final CSL is missing: %s\n' "$csl_path" >&2
    return 1
  fi
  mkdir -p "$output_dir"
  validate_current_figure_assets

  "$pandoc_bin" \
    --from=markdown+tex_math_single_backslash \
    --to=docx \
    --standalone \
    --reference-doc=docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx \
    --bibliography=docs/paper/manuscript/references/references.bib \
    --csl="$csl_path" \
    --citeproc \
    --resource-path=docs/paper/manuscript:docs/paper/manuscript/figures:docs/paper/manuscript/tables:docs/paper/phase5_6/visual/production/figures:docs/paper/phase5_7/visual/production/figures \
    --metadata-file=docs/paper/manuscript/metadata/metadata_private.yaml \
    --lua-filter=scripts/paper/full_manuscript_filter.lua \
    --output="$raw_docx" \
    "${full_sections[@]}"

  python3 scripts/paper/postprocess_full_manuscript_docx.py \
    --input "$raw_docx" --output "$raw_docx.full"
  python3 scripts/paper/postprocess_publication_tables.py \
    --input "$raw_docx.full" --output "$full_docx"
  unzip -t "$full_docx" > /dev/null
  python3 scripts/paper/validate_word_heading_numbering_docx.py "$full_docx"
  python3 scripts/paper/validate_citations.py
  python3 scripts/paper/validate_final_references.py --docx "$full_docx" --write-audit
  python3 scripts/paper/validate_full_manuscript_docx.py "$full_docx"
  python3 scripts/paper/validate_phase57b_integration.py --phase57g --docx "$full_docx"
  printf 'FULL_BUILD_OUTPUT=%s\n' "$full_docx"
  sha256sum "$full_docx"
}

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
  printf '%s\n' 'Full build command (authorized):'
  printf '%s\n' 'scripts/paper/build_manuscript_docx.sh --build-full'
  printf '%s\n' 'Anonymous build command (authorized):'
  printf '%s\n' 'scripts/paper/build_manuscript_docx.sh --build-anonymous'
  printf '%s\n' 'CSL_STATUS: PHASE_4_7_LOCAL_DERIVATIVE_VALIDATED; SEE_PAPER_PHASE4_CSL_DECISION_v1.0.md'
}

build_anonymous() {
  local pandoc_bin="${PAPER_PANDOC_BIN:-/home/orin/.local/bin/pandoc}"
  local output_dir="docs/paper/manuscript/output"
  local raw_docx="$output_dir/draft_anonymous_raw.docx"
  local section_docx="$output_dir/draft_anonymous_raw.docx.anonymous"
  local table_docx="$output_dir/draft_anonymous_raw.docx.tables"
  local anonymous_docx="$output_dir/draft_anonymous.docx"
  local csl_path="docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl"

  if [[ ! -x "$pandoc_bin" ]]; then
    printf 'ANONYMOUS_BUILD_FAILED: Pandoc executable unavailable: %s\n' "$pandoc_bin" >&2
    return 1
  fi
  if [[ ! -s "$csl_path" ]]; then
    printf 'ANONYMOUS_BUILD_FAILED: final CSL is missing: %s\n' "$csl_path" >&2
    return 1
  fi
  mkdir -p "$output_dir"
  validate_current_figure_assets

  "$pandoc_bin" \
    --from=markdown+tex_math_single_backslash \
    --to=docx \
    --standalone \
    --reference-doc=docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx \
    --bibliography=docs/paper/manuscript/references/references.bib \
    --csl="$csl_path" \
    --citeproc \
    --resource-path=docs/paper/manuscript:docs/paper/manuscript/figures:docs/paper/manuscript/tables:docs/paper/phase5_6/visual/production/figures:docs/paper/phase5_7/visual/production/figures \
    --metadata-file=docs/paper/manuscript/metadata/metadata_anonymous.yaml \
    --lua-filter=scripts/paper/full_manuscript_filter.lua \
    --output="$raw_docx" \
    "${full_sections[@]}"

  python3 scripts/paper/postprocess_full_manuscript_docx.py \
    --input "$raw_docx" --output "$section_docx"
  python3 scripts/paper/postprocess_publication_tables.py \
    --input "$section_docx" --output "$table_docx" \
    --anonymous-t4-page-break
  python3 scripts/paper/sanitize_anonymous_manuscript_docx.py \
    --input "$table_docx" --output "$anonymous_docx"
  unzip -t "$anonymous_docx" > /dev/null
  python3 scripts/paper/validate_word_heading_numbering_docx.py "$anonymous_docx"
  python3 scripts/paper/validate_citations.py
  if [[ -s "$output_dir/draft_full.docx" ]]; then
    python3 scripts/paper/validate_final_references.py \
      --docx "$anonymous_docx" --compare-full "$output_dir/draft_full.docx" --write-audit
    python3 scripts/paper/validate_anonymous_manuscript_docx.py \
      "$anonymous_docx" --full "$output_dir/draft_full.docx"
    python3 scripts/paper/validate_phase57b_integration.py --phase57g \
      --docx "$anonymous_docx" --compare-full "$output_dir/draft_full.docx"
  else
    python3 scripts/paper/validate_final_references.py --docx "$anonymous_docx" --write-audit
    python3 scripts/paper/validate_anonymous_manuscript_docx.py "$anonymous_docx"
    python3 scripts/paper/validate_phase57b_integration.py --phase57g --docx "$anonymous_docx"
  fi
  printf 'ANONYMOUS_BUILD_OUTPUT=%s\n' "$anonymous_docx"
  sha256sum "$anonymous_docx"
}

case "${1-}" in
  --build-full)
    build_full
    ;;
  --build-anonymous)
    build_anonymous
    ;;
  --check)
    if [[ ! -s docs/paper/manuscript/output/draft_full.docx ]]; then
      printf '%s\n' 'PHASE4_5_CHECK_FAILED: Full DOCX is missing; run --build-full first' >&2
      exit 1
    fi
    unzip -t docs/paper/manuscript/output/draft_full.docx > /dev/null
    python3 scripts/paper/validate_word_heading_numbering_docx.py \
      docs/paper/manuscript/output/draft_full.docx
    python3 scripts/paper/validate_citations.py
    python3 scripts/paper/validate_final_references.py \
      --docx docs/paper/manuscript/output/draft_full.docx --write-audit
    python3 scripts/paper/validate_full_manuscript_docx.py docs/paper/manuscript/output/draft_full.docx
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
    printf 'Usage: %s [--build-full|--build-anonymous|--check|--show-order|--show-command]\n' "$0" >&2
    exit 2
    ;;
esac
