#!/usr/bin/env bash
set -euo pipefail

# Paper Phase 2.5 Step 6 — TOOLCHAIN_POC_ONLY.
# Generates only synthetic derivatives outside Git.

REPO_ROOT="${PHASE2_5_REPO_ROOT:-/home/orin/edge-ai/edge-ai-defect}"
POC_ROOT="${PHASE2_5_POC_ROOT:-/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1}"
PANDOC_BIN="${PHASE2_5_PANDOC:-/home/orin/.local/bin/pandoc}"
REFERENCE_DOCX="$REPO_ROOT/docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx"
CSL_URL="https://www.zotero.org/styles/china-national-standard-gb-t-7714-2025-numeric"
EXPECTED_REFERENCE_SHA="c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71"

SOURCE_DIR="$POC_ROOT/source"
CSL_DIR="$POC_ROOT/csl"
FIGURE_DIR="$POC_ROOT/figures"
OUTPUT_DIR="$POC_ROOT/output"
RENDERED_DIR="$POC_ROOT/rendered"
INSPECTION_DIR="$POC_ROOT/inspection"
LOG_DIR="$POC_ROOT/logs"
METADATA_DIR="$POC_ROOT/metadata"
TEMP_DIR="$POC_ROOT/temporary"

mkdir -p "$SOURCE_DIR" "$CSL_DIR" "$FIGURE_DIR" "$OUTPUT_DIR" \
  "$RENDERED_DIR" "$INSPECTION_DIR" "$LOG_DIR" "$METADATA_DIR" "$TEMP_DIR"

cd "$REPO_ROOT"

if [[ ! -x "$PANDOC_BIN" ]]; then
  echo "POC_FAILED: Pandoc executable unavailable: $PANDOC_BIN" >&2
  exit 1
fi
actual_reference_sha="$(sha256sum "$REFERENCE_DOCX" | awk '{print $1}')"
if [[ "$actual_reference_sha" != "$EXPECTED_REFERENCE_SHA" ]]; then
  echo "POC_FAILED: canonical reference DOCX hash changed" >&2
  exit 1
fi

cat > "$SOURCE_DIR/poc_references.bib" <<'BIB'
% TOOLCHAIN_POC_ONLY
% SYNTHETIC_CONTENT
% NOT_FORMAL_REFERENCE_DATA
@article{POC_CN_JOURNAL,
  author  = {{虚拟甲 and 虚拟乙}},
  title   = {TOOLCHAIN TEST 中文期刊虚拟条目},
  journal = {虚拟工具链测试期刊},
  year    = {2091},
  volume  = {1},
  number  = {1},
  pages   = {1--9}
}
@article{POC_EN_JOURNAL,
  author  = {{Synthetic Alpha and Synthetic Beta}},
  title   = {TOOLCHAIN TEST English journal placeholder},
  journal = {Synthetic Toolchain Journal},
  year    = {2092},
  volume  = {2},
  number  = {2},
  pages   = {10--19}
}
@book{POC_BOOK,
  author    = {{Synthetic Book Author}},
  title     = {TOOLCHAIN TEST synthetic book placeholder},
  address   = {Synthetic City},
  publisher = {Synthetic Publisher},
  year      = {2093}
}
@standard{POC_STANDARD,
  author = {{Synthetic Standards Group}},
  title  = {POC-0000 TOOLCHAIN TEST synthetic standard placeholder},
  year   = {2094}
}
@online{POC_WEB_RESOURCE,
  author  = {{Synthetic Web Group}},
  title   = {TOOLCHAIN TEST synthetic web resource placeholder},
  year    = {2095},
  url     = {https://example.invalid/toolchain-test},
  urldate = {2095-01-02}
}
BIB

cat > "$SOURCE_DIR/poc_full.yaml" <<'YAML'
lang: zh-CN
reference-section-title: 参考文献
poc-variant: full
poc-identity-enabled: true
poc-author-cn: POC测试作者
poc-affiliation-cn: POC测试单位（虚拟），测试省测试市 000000
poc-author-en: POC SYNTHETIC AUTHOR
poc-affiliation-en: POC Synthetic Unit, Synthetic City 000000, China
poc-contact: poc@example.invalid
poc-funding: 基金测试字段：TOOLCHAIN TEST 虚拟基金 POC-000
poc-biography: 作者简介测试字段：TOOLCHAIN TEST 虚拟简介
poc-acknowledgement: 致谢测试字段：TOOLCHAIN TEST 虚拟致谢
YAML

cat > "$SOURCE_DIR/poc_anonymous.yaml" <<'YAML'
lang: zh-CN
reference-section-title: 参考文献
poc-variant: anonymous
poc-identity-enabled: false
anonymous-status: ANONYMIZED_POC_CANDIDATE
word-inspector-status: NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED
YAML

cat > "$FIGURE_DIR/poc_figure.svg" <<'SVG'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="720" height="420" viewBox="0 0 720 420">
  <rect width="720" height="420" fill="white"/>
  <g stroke="#222" stroke-width="2" fill="none">
    <line x1="90" y1="330" x2="660" y2="330"/>
    <line x1="90" y1="330" x2="90" y2="60"/>
  </g>
  <g fill="#4472c4">
    <rect x="150" y="230" width="90" height="100"/>
    <rect x="330" y="170" width="90" height="160"/>
    <rect x="510" y="100" width="90" height="230"/>
  </g>
  <g font-family="Times New Roman, serif" font-size="22" fill="#111" text-anchor="middle">
    <text x="195" y="360">POC-A</text><text x="375" y="360">POC-B</text><text x="555" y="360">POC-C</text>
    <text x="375" y="400">Variant</text>
    <text x="375" y="35" font-weight="bold">SYNTHETIC TOOLCHAIN TEST DATA</text>
  </g>
  <text x="24" y="200" transform="rotate(-90 24 200)" font-family="Times New Roman, serif" font-size="22" text-anchor="middle">Synthetic Value / a.u.</text>
</svg>
SVG

figure_profile="$TEMP_DIR/libreoffice_figure_profile.$$.tmp"
mkdir -p "$figure_profile"
libreoffice "-env:UserInstallation=file://$figure_profile" --headless \
  --convert-to png --outdir "$FIGURE_DIR" "$FIGURE_DIR/poc_figure.svg" \
  > "$LOG_DIR/libreoffice_figure_fallback.stdout.log" \
  2> "$LOG_DIR/libreoffice_figure_fallback.stderr.log"
if [[ ! -s "$FIGURE_DIR/poc_figure.png" ]]; then
  echo "POC_FAILED: deterministic SVG fallback conversion did not produce PNG" >&2
  exit 1
fi

cat > "$SOURCE_DIR/poc_article.md" <<'MARKDOWN'
::: {custom-style="HFUTSpecimenNotice"}
TOOLCHAIN POC ONLY
:::

::: {custom-style="HFUTSpecimenNotice"}
SYNTHETIC_CONTENT · NOT_PAPER_CONTENT · NOT_FORMAL_REFERENCE_DATA · PHASE_3_NOT_AUTHORIZED
:::

::: {custom-style="HFUTSpecimenNotice"}
NOT PAPER CONTENT
:::

::: {custom-style="HFUTSpecimenNotice"}
NOT SUBMISSION MANUSCRIPT
:::

::: {custom-style="HFUTTitleCN"}
Markdown到Word工具链测试题名
:::

::: {custom-style="HFUTTitleEN"}
Markdown-to-Word toolchain test title
:::

POC_IDENTITY_BLOCK_MARKER

::: {custom-style="HFUTAbstractLabelCN"}
摘要
:::

::: {custom-style="HFUTAbstractBodyCN"}
本段仅用于验证中英文前置信息、样式映射和分页行为。所有叙述均为合成工具链内容，不构成论文摘要、实验结果或学术主张。测试覆盖混合文字、字段边界、文档生成与结构检查，并明确保留Microsoft Word、MathType及出版资产工具的人工验收边界。
:::

::: {custom-style="HFUTKeywordsLabelCN"}
关键词
:::

::: {custom-style="HFUTKeywordsBodyCN"}
工具链测试；合成内容；文档转换；结构检查
:::

::: {custom-style="HFUTClassification"}
中图分类号：POC-CLASSIFICATION-PLACEHOLDER
:::

::: {custom-style="HFUTAbstractLabelEN"}
Abstract
:::

::: {custom-style="HFUTAbstractBodyEN"}
This synthetic paragraph tests bilingual front matter, semantic styles, and document generation. It is not a paper abstract, an experimental result, or a scholarly claim. Microsoft Word, MathType, and publication-asset acceptance remain manual checks.
:::

::: {custom-style="HFUTKeywordsLabelEN"}
Keywords
:::

::: {custom-style="HFUTKeywordsBodyEN"}
toolchain test; synthetic content; document conversion; structural inspection
:::

BODY_SECTION_START_MARKER

# 引言测试 {#poc-introduction}

这是用于验证的短段落。中文、English、数字123和缩略语POC（proof of concept）混排；行内公式为 $\bar{t}$。首次顺序编码引用使用虚拟中文期刊条目 [@POC_CN_JOURNAL]，后续多条引用使用虚拟英文期刊和专著条目 [@POC_EN_JOURNAL; @POC_BOOK]。这些条目仅检查转换能力。

# 一级标题测试 {#poc-level-1}

本节只验证层级、公式、图表和引用，不写正式论文claim。独立公式测试如下：

$$
\bar{t}=\frac{1}{N}\sum_{i=1}^{N}t_i
$$

公式编号候选：（1）STATIC_TEXT_ONLY。正文中的“式（1）”也是静态文本交叉引用候选，分类为 POSTPROCESS_CANDIDATE，不是动态Word域，不得误判为自动交叉引用。

比例公式测试如下：

$$
r=\frac{x_{\mathrm{new}}-x_{\mathrm{base}}}{x_{\mathrm{base}}}\times100\%
$$

单位、变量正斜体、上下标以及MathType兼容性仍需Microsoft Word和MathType人工确认。标准类虚拟条目在此首次出现 [@POC_STANDARD]。

## 二级标题测试 {#poc-level-2}

如图1所示，以下对象只包含三组确定性虚拟数据；“图1”为 STATIC_TEXT_ONLY，首次引用和图题均不是Word动态SEQ或REF域。该SVG不代表Origin或最终出版资产。

![](../figures/poc_figure.svg){width=7.2cm}

::: {custom-style="HFUTFigureCaption"}
图1 三组虚拟工具链测试数据（SYNTHETIC_CONTENT）
:::

### 三级标题测试 {#poc-level-3}

表1在此处首次引用。表题和表号为 STATIC_TEXT_ONLY；三线表边框由确定性OOXML后处理验证。数值仅用于测试不同小数位输入、显示补零以及中英文数字混排，没有实验意义。

::: {custom-style="HFUTTableCaption"}
表1 虚拟三线表候选（单位：a.u.）
:::

| Variant / 变体 | Synthetic Value / a.u. | Note / 备注 |
|:---|---:|:---|
| POC-A | 1.20 | 中文1 |
| POC-B | 2.345 | English 2 |
| POC-C | 3.0 | 中英mix 3 |

网页资源虚拟条目在此首次出现 [@POC_WEB_RESOURCE]。全部五类条目题名均含“TOOLCHAIN TEST”；它们不是正式参考文献数据。前置信息单栏与正文双栏以语义marker为边界，栏间距候选为425 twips（约0.748 cm），页码应连续。
MARKDOWN

CSL_PATH="$CSL_DIR/china-national-standard-gb-t-7714-2025-numeric.csl"
DOWNLOAD_AT="$(date --iso-8601=seconds)"
curl --fail --silent --show-error --location \
  --dump-header "$LOG_DIR/csl_download_headers.log" \
  --output "$CSL_PATH" \
  --write-out 'http_status=%{http_code}\nfinal_url=%{url_effective}\nsize_bytes=%{size_download}\n' \
  "$CSL_URL" > "$LOG_DIR/csl_download_result.log"

python3 - "$CSL_PATH" "$METADATA_DIR/csl_validation.json" "$CSL_URL" "$DOWNLOAD_AT" <<'PY'
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

p = Path(sys.argv[1])
output = Path(sys.argv[2])
source_url = sys.argv[3]
downloaded_at = sys.argv[4]
root = ET.parse(p).getroot()
ns = {"c": "http://purl.org/net/xbiblio/csl"}

def text(xpath):
    node = root.find(xpath, ns)
    return "" if node is None or node.text is None else node.text.strip()

category = root.find("c:info/c:category[@citation-format]", ns)
rights = root.find("c:info/c:rights", ns)
data = {
    "classification": [
        "OFFICIAL_ZOTERO_STYLE_REPOSITORY_CANDIDATE",
        "POC_ONLY",
        "NOT_YET_VALIDATED_AGAINST_HFUT_SPECIAL_RULES",
    ],
    "download_url": source_url,
    "downloaded_at": downloaded_at,
    "size_bytes": p.stat().st_size,
    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    "title": text("c:info/c:title"),
    "id": text("c:info/c:id"),
    "updated": text("c:info/c:updated"),
    "citation_format": "" if category is None else category.get("citation-format", ""),
    "rights": "" if rights is None or rights.text is None else rights.text.strip(),
    "license": "" if rights is None else rights.get("license", ""),
    "csl_version": root.get("version", ""),
    "xml_parse": "PASS",
}
data["title_check"] = "PASS" if "GB/T 7714-2025" in data["title"] else "FAIL"
data["numeric_check"] = "PASS" if data["citation_format"] == "numeric" else "FAIL"
output.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
assert data["title_check"] == data["numeric_check"] == "PASS"
PY

build_one() {
  local variant="$1"
  local metadata="$SOURCE_DIR/poc_$variant.yaml"
  local raw_docx="$TEMP_DIR/poc_"$variant"_raw.docx"
  local final_docx="$OUTPUT_DIR/poc_$variant.docx"
  local stdout_log="$LOG_DIR/pandoc_$variant.stdout.log"
  local stderr_log="$LOG_DIR/pandoc_$variant.stderr.log"
  local command_log="$LOG_DIR/pandoc_"$variant"_command.log"
  local started_at ended_at start_ns end_ns rc

  started_at="$(date --iso-8601=seconds)"
  start_ns="$(date +%s%N)"
  set +e
  "$PANDOC_BIN" \
    --standalone \
    --from=markdown \
    --to=docx \
    --reference-doc="$REFERENCE_DOCX" \
    --citeproc \
    --bibliography="$SOURCE_DIR/poc_references.bib" \
    --csl="$CSL_PATH" \
    --resource-path="$SOURCE_DIR:$FIGURE_DIR" \
    --metadata-file="$metadata" \
    --lua-filter="$REPO_ROOT/scripts/paper/phase2_5_poc_styles.lua" \
    --output="$raw_docx" \
    "$SOURCE_DIR/poc_article.md" >"$stdout_log" 2>"$stderr_log"
  rc=$?
  set -e
  end_ns="$(date +%s%N)"
  ended_at="$(date --iso-8601=seconds)"
  {
    printf 'classification=TOOLCHAIN_POC_ONLY;SYNTHETIC_CONTENT;NOT_SUBMISSION_MANUSCRIPT\n'
    printf 'started_at=%s\nended_at=%s\nduration_ns=%s\nreturn_code=%s\n' \
      "$started_at" "$ended_at" "$((end_ns - start_ns))" "$rc"
    printf 'command='
    printf '%q ' "$PANDOC_BIN" --standalone --from=markdown --to=docx \
      "--reference-doc=$REFERENCE_DOCX" --citeproc \
      "--bibliography=$SOURCE_DIR/poc_references.bib" "--csl=$CSL_PATH" \
      "--resource-path=$SOURCE_DIR:$FIGURE_DIR" "--metadata-file=$metadata" \
      "--lua-filter=$REPO_ROOT/scripts/paper/phase2_5_poc_styles.lua" \
      "--output=$raw_docx" "$SOURCE_DIR/poc_article.md"
    printf '\nstdout_log=%s\nstderr_log=%s\n' "$stdout_log" "$stderr_log"
  } > "$command_log"
  if [[ "$rc" -ne 0 ]]; then
    echo "POC_FAILED: Pandoc $variant build failed; see $stderr_log" >&2
    exit "$rc"
  fi

  python3 "$REPO_ROOT/scripts/paper/postprocess_phase2_5_poc_docx.py" \
    --input "$raw_docx" --output "$final_docx" --variant "$variant" \
    --figure-fallback-png "$FIGURE_DIR/poc_figure.png" \
    > "$LOG_DIR/postprocess_$variant.log" 2>&1
  python3 "$REPO_ROOT/scripts/paper/inspect_phase2_5_poc_docx.py" \
    "$final_docx" --variant "$variant" \
    --json-output "$INSPECTION_DIR/poc_"$variant"_inspection.json" \
    > "$LOG_DIR/inspection_$variant.log" 2>&1
  file "$final_docx" > "$INSPECTION_DIR/poc_"$variant"_file.txt"
  sha256sum "$final_docx" > "$INSPECTION_DIR/poc_"$variant"_sha256.txt"
  unzip -t "$final_docx" > "$INSPECTION_DIR/poc_"$variant"_unzip_test.txt"
}

build_one full
build_one anonymous

for variant in full anonymous; do
  lo_profile="$TEMP_DIR/libreoffice_profile_$variant.$$.tmp"
  mkdir -p "$lo_profile"
  libreoffice "-env:UserInstallation=file://$lo_profile" --headless \
    --convert-to pdf --outdir "$RENDERED_DIR" "$OUTPUT_DIR/poc_$variant.docx" \
    > "$LOG_DIR/libreoffice_$variant.stdout.log" \
    2> "$LOG_DIR/libreoffice_$variant.stderr.log"
  mv -f "$RENDERED_DIR/poc_$variant.pdf" "$RENDERED_DIR/poc_"$variant"_preview.pdf"
  pdfinfo "$RENDERED_DIR/poc_"$variant"_preview.pdf" \
    > "$INSPECTION_DIR/poc_"$variant"_preview_pdfinfo.txt"
  page_count="$(awk '/^Pages:/{print $2}' "$INSPECTION_DIR/poc_"$variant"_preview_pdfinfo.txt")"
  if [[ "$page_count" -lt 2 || "$page_count" -gt 4 ]]; then
    echo "POC_FAILED: $variant preview has $page_count pages; expected 2-4" >&2
    exit 1
  fi
  if ! rg -q '^Page size:.*A4' "$INSPECTION_DIR/poc_"$variant"_preview_pdfinfo.txt"; then
    echo "POC_FAILED: $variant preview is not reported as A4" >&2
    exit 1
  fi
done

if rg -n 'POC测试作者|POC测试单位|poc@example\.invalid|基金测试字段|作者简介测试字段|致谢测试字段' \
  "$INSPECTION_DIR/poc_anonymous_inspection.json" \
  "$LOG_DIR/pandoc_anonymous_command.log" \
  "$LOG_DIR/pandoc_anonymous.stdout.log" \
  "$LOG_DIR/pandoc_anonymous.stderr.log"; then
  echo "POC_FAILED: anonymous build records contain a forbidden identity token" >&2
  exit 1
fi

if rg -q '^@' "$REPO_ROOT/docs/paper/manuscript/references/references.bib"; then
  echo "POC_FAILED: formal references.bib is no longer empty" >&2
  exit 1
fi
for section in "$REPO_ROOT"/docs/paper/manuscript/sections/*.md; do
  if ! rg -q 'STRUCTURE_ONLY' "$section"; then
    echo "POC_FAILED: formal chapter lost STRUCTURE_ONLY marker: $section" >&2
    exit 1
  fi
done

cat > "$METADATA_DIR/poc_run_status.txt" <<EOF
TOOLCHAIN_POC_ONLY
SYNTHETIC_CONTENT
NOT_PAPER_CONTENT
NOT_FORMAL_REFERENCE_DATA
NOT_SUBMISSION_MANUSCRIPT
PHASE_3_NOT_AUTHORIZED
NON_AUTHORITATIVE_LIBREOFFICE_PREVIEW
MICROSOFT_WORD_RENDERING_NOT_VERIFIED
full_docx=$OUTPUT_DIR/poc_full.docx
anonymous_docx=$OUTPUT_DIR/poc_anonymous.docx
full_preview=$RENDERED_DIR/poc_full_preview.pdf
anonymous_preview=$RENDERED_DIR/poc_anonymous_preview.pdf
EOF

echo "POC_RUN_PASS"
echo "root=$POC_ROOT"
