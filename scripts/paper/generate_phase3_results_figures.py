#!/usr/bin/env python3
"""Generate deterministic Phase 3 Section 4 result figures and specs.

The sole data input is the frozen Section 4 result data register. The script
performs SVG layout calculations only; it does not derive or recalculate any
reported result metric.
"""

from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv"
FIGURE_DIR = ROOT / "docs/paper/manuscript/figures"
FIG2_PATH = FIGURE_DIR / "fig2_mean_fps.svg"
FIG2_SPEC_PATH = FIGURE_DIR / "fig2_mean_fps_spec.md"
FIG3_PATH = FIGURE_DIR / "fig3_mean_tail_latency.svg"
FIG3_SPEC_PATH = FIGURE_DIR / "fig3_mean_tail_latency_spec.md"

FPS_IDS = {
    "V0": ("M_R_V0_FPS", "M_R_V0_FPS_SD"),
    "V2R": ("M_R_V2R_FPS", "M_R_V2R_FPS_SD"),
    "V3R": ("M_R_V3R_FPS", "M_R_V3R_FPS_SD"),
}
LATENCY_IDS = {
    "V0": ("M_R_V0_LAT_MEAN", "M_R_V0_P95", "M_R_V0_P99"),
    "V2R": ("M_R_V2R_LAT_MEAN", "M_R_V2R_P95", "M_R_V2R_P99"),
    "V3R": ("M_R_V3R_LAT_MEAN", "M_R_V3R_P95", "M_R_V3R_P99"),
}


def load_register() -> dict[str, dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))

    by_id: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for row in rows:
        metric_id = row["metric_id"]
        if metric_id in by_id:
            duplicates.append(metric_id)
        by_id[metric_id] = row
    if duplicates:
        raise ValueError(f"Duplicate metric IDs in result register: {sorted(set(duplicates))}")

    required = {
        metric_id
        for pair in FPS_IDS.values()
        for metric_id in pair
    } | {
        metric_id
        for group in LATENCY_IDS.values()
        for metric_id in group
    }
    missing = sorted(required - by_id.keys())
    if missing:
        raise ValueError(f"Missing required metric IDs in result register: {missing}")
    return by_id


def value(row: dict[str, str]) -> Decimal:
    return Decimal(row["frozen_value"])


def coord(number: Decimal) -> str:
    return format(number.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP), "f")


def svg_document(title: str, description: str, body: list[str]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620">',
        f"  <title>{title}</title>",
        f"  <desc>{description}</desc>",
        "  <style>",
        "    text { font-family: sans-serif; fill: #1f2937; }",
        "    .title { font-size: 24px; font-weight: 700; }",
        "    .axis-label { font-size: 17px; font-weight: 600; }",
        "    .tick { font-size: 14px; }",
        "    .value { font-size: 13px; font-weight: 600; }",
        "    .legend { font-size: 14px; }",
        "    .axis { stroke: #374151; stroke-width: 1.5; }",
        "    .grid { stroke: #d1d5db; stroke-width: 1; }",
        "    .error { stroke: #111827; stroke-width: 2; }",
        "  </style>",
        '  <rect width="960" height="620" fill="#ffffff"/>',
        *body,
        "</svg>",
        "",
    ]
    return "\n".join(lines)


def generate_fig2(rows: dict[str, dict[str, str]]) -> str:
    top = Decimal("95")
    bottom = Decimal("510")
    height = bottom - top
    y_max = Decimal("140")
    centers = {"V0": Decimal("260"), "V2R": Decimal("500"), "V3R": Decimal("740")}
    colors = {"V0": "#64748b", "V2R": "#0f766e", "V3R": "#d97706"}

    def y(pixel_value: Decimal) -> Decimal:
        return bottom - pixel_value / y_max * height

    body = [
        '  <text x="480" y="42" text-anchor="middle" class="title">V0、V2R和V3R平均帧率比较</text>',
        '  <line x1="105" y1="95" x2="105" y2="510" class="axis"/>',
        '  <line x1="105" y1="510" x2="900" y2="510" class="axis"/>',
    ]
    for tick in range(0, 141, 20):
        tick_y = y(Decimal(tick))
        body.extend(
            [
                f'  <line x1="105" y1="{coord(tick_y)}" x2="900" y2="{coord(tick_y)}" class="grid"/>',
                f'  <text x="92" y="{coord(tick_y + Decimal("5"))}" text-anchor="end" class="tick">{tick}</text>',
            ]
        )

    for variant in ("V0", "V2R", "V3R"):
        mean_id, sd_id = FPS_IDS[variant]
        mean_row, sd_row = rows[mean_id], rows[sd_id]
        mean, sd = value(mean_row), value(sd_row)
        center = centers[variant]
        bar_y = y(mean)
        bar_height = bottom - bar_y
        high_y = y(mean + sd)
        low_y = y(mean - sd)
        body.extend(
            [
                f'  <rect class="bar fps-bar" data-metric-id="{mean_id}" x="{coord(center - Decimal("65"))}" y="{coord(bar_y)}" width="130" height="{coord(bar_height)}" fill="{colors[variant]}"/>',
                f'  <g class="error-bar" data-metric-id="{sd_id}">',
                f'    <line x1="{coord(center)}" y1="{coord(high_y)}" x2="{coord(center)}" y2="{coord(low_y)}" class="error"/>',
                f'    <line x1="{coord(center - Decimal("18"))}" y1="{coord(high_y)}" x2="{coord(center + Decimal("18"))}" y2="{coord(high_y)}" class="error"/>',
                f'    <line x1="{coord(center - Decimal("18"))}" y1="{coord(low_y)}" x2="{coord(center + Decimal("18"))}" y2="{coord(low_y)}" class="error"/>',
                "  </g>",
                f'  <text x="{coord(center)}" y="{coord(high_y - Decimal("10"))}" text-anchor="middle" class="value">{mean_row["display_value"]} ± {sd_row["display_value"]}</text>',
                f'  <text x="{coord(center)}" y="538" text-anchor="middle" class="axis-label">{variant}</text>',
            ]
        )
    body.extend(
        [
            '  <text x="28" y="300" text-anchor="middle" class="axis-label" transform="rotate(-90 28 300)">平均帧率/FPS</text>',
            '  <text x="480" y="585" text-anchor="middle" class="legend">误差棒：5次运行FPS的冻结样本标准差</text>',
        ]
    )
    return svg_document(
        "Mean Frame-Rate Comparison of V0, V2R, and V3R",
        "Three mean FPS bars with frozen sample-standard-deviation error bars.",
        body,
    )


def generate_fig3(rows: dict[str, dict[str, str]]) -> str:
    top = Decimal("95")
    bottom = Decimal("510")
    height = bottom - top
    y_max = Decimal("22")
    group_centers = {"V0": Decimal("260"), "V2R": Decimal("500"), "V3R": Decimal("740")}
    series = (
        ("mean", 0, Decimal("-66"), "#2563eb"),
        ("P95", 1, Decimal("0"), "#0f766e"),
        ("P99", 2, Decimal("66"), "#d97706"),
    )

    def y(pixel_value: Decimal) -> Decimal:
        return bottom - pixel_value / y_max * height

    body = [
        '  <text x="480" y="42" text-anchor="middle" class="title">V0、V2R和V3R平均及尾延迟比较</text>',
        '  <line x1="105" y1="95" x2="105" y2="510" class="axis"/>',
        '  <line x1="105" y1="510" x2="900" y2="510" class="axis"/>',
    ]
    for tick in (0, 5, 10, 15, 20):
        tick_y = y(Decimal(tick))
        body.extend(
            [
                f'  <line x1="105" y1="{coord(tick_y)}" x2="900" y2="{coord(tick_y)}" class="grid"/>',
                f'  <text x="92" y="{coord(tick_y + Decimal("5"))}" text-anchor="end" class="tick">{tick}</text>',
            ]
        )

    for variant in ("V0", "V2R", "V3R"):
        metric_ids = LATENCY_IDS[variant]
        center = group_centers[variant]
        for label, index, offset, color in series:
            row = rows[metric_ids[index]]
            metric_value = value(row)
            bar_y = y(metric_value)
            bar_height = bottom - bar_y
            x = center + offset - Decimal("28")
            body.extend(
                [
                    f'  <rect class="bar latency-bar" data-metric-id="{metric_ids[index]}" data-statistic="{label}" x="{coord(x)}" y="{coord(bar_y)}" width="56" height="{coord(bar_height)}" fill="{color}"/>',
                    f'  <text x="{coord(center + offset)}" y="{coord(bar_y - Decimal("8"))}" text-anchor="middle" class="value">{row["display_value"]}</text>',
                ]
            )
        body.append(f'  <text x="{coord(center)}" y="538" text-anchor="middle" class="axis-label">{variant}</text>')

    legend_items = (("均值", "#2563eb", 345), ("P95", "#0f766e", 465), ("P99", "#d97706", 575))
    for label, color, x in legend_items:
        body.extend(
            [
                f'  <rect x="{x}" y="566" width="22" height="14" fill="{color}"/>',
                f'  <text x="{x + 30}" y="579" class="legend">{label}</text>',
            ]
        )
    body.append('  <text x="28" y="300" text-anchor="middle" class="axis-label" transform="rotate(-90 28 300)">延迟/ms</text>')
    return svg_document(
        "Mean and Tail Latency Comparison of V0, V2R, and V3R",
        "Grouped bars for nine distinct frozen mean, P95, and P99 latency metrics.",
        body,
    )


def generate_fig2_spec(rows: dict[str, dict[str, str]]) -> str:
    lines = [
        "# Figure 2 deterministic specification",
        "",
        "## Identity",
        "",
        "- Candidate: `F2`",
        "- Chinese title: `V0、V2R和V3R平均帧率比较`",
        "- English title: `Mean Frame-Rate Comparison of V0, V2R, and V3R`",
        "- Artifact type: bar chart",
        "- Y-axis: `平均帧率/FPS`",
        "",
        "## Frozen data",
        "",
        "| Variant | Mean metric ID | Raw mean | Display mean | SD metric ID | Raw SD | Display SD |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for variant in ("V0", "V2R", "V3R"):
        mean_id, sd_id = FPS_IDS[variant]
        mean_row, sd_row = rows[mean_id], rows[sd_id]
        lines.append(
            f'| {variant} | `{mean_id}` | {mean_row["frozen_value"]} | '
            f'{mean_row["display_value"]} | `{sd_id}` | {sd_row["frozen_value"]} | '
            f'{sd_row["display_value"]} |'
        )
    lines.extend(
        [
            "",
            "## Error-bar semantics",
            "",
            "Each error bar is the corresponding frozen FPS sample SD over five",
            "process-level FPS values. It is not a confidence interval, standard",
            "error, min-max range, or significance marker.",
            "",
            "## Limitations",
            "",
            "- Descriptive evidence from one Jetson platform, one frozen YOLOv8n",
            "  INT8 Engine, 640 x 640 input, batch 1, and 180-image offline replay.",
            "- Five processes per variant; no significance test.",
            "- No power, resource, endurance, or real-camera result.",
            "- No ratio, percentage, or superiority annotation is included.",
            "",
            "## Generation",
            "",
            "The SVG is emitted by `scripts/paper/generate_phase3_results_figures.py`.",
            "Its only data input is",
            "`docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`.",
            "No reported result metric is recalculated.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_fig3_spec(rows: dict[str, dict[str, str]]) -> str:
    lines = [
        "# Figure 3 deterministic specification",
        "",
        "## Identity",
        "",
        "- Candidate: `F3`",
        "- Chinese title: `V0、V2R和V3R平均及尾延迟比较`",
        "- English title: `Mean and Tail Latency Comparison of V0, V2R, and V3R`",
        "- Artifact type: grouped bar chart",
        "- Y-axis: `延迟/ms`",
        "- Groups: `V0`; `V2R`; `V3R`",
        "- Series: `mean`; `P95`; `P99`",
        "",
        "## Frozen data",
        "",
        "| Variant | Statistic | Metric ID | Raw value (ms) | Display value (ms) | Aggregation |",
        "|---|---|---|---:|---:|---|",
    ]
    labels = ("mean", "P95", "P99")
    for variant in ("V0", "V2R", "V3R"):
        for label, metric_id in zip(labels, LATENCY_IDS[variant]):
            row = rows[metric_id]
            lines.append(
                f'| {variant} | {label} | `{metric_id}` | {row["frozen_value"]} | '
                f'{row["display_value"]} | {row["aggregation"]} |'
            )
    lines.extend(
        [
            "",
            "## Statistic semantics",
            "",
            "All latency values are pooled 5400-sample frozen metrics. Mean, P95,",
            "and P99 are three distinct statistics; the percentile bars are not",
            "variance measures or error bars.",
            "",
            "## Limitations",
            "",
            "- Descriptive evidence from one Jetson platform, one frozen YOLOv8n",
            "  INT8 Engine, 640 x 640 input, batch 1, and 180-image offline replay.",
            "- Five processes per variant; no significance test.",
            "- No power, resource, endurance, or real-camera result.",
            "- No speedup, percentage, confidence interval, or significance",
            "  annotation is included.",
            "- V3R tail directions are mixed and V3R has no independent Gate D.",
            "",
            "## Generation",
            "",
            "The SVG is emitted by `scripts/paper/generate_phase3_results_figures.py`.",
            "Its only data input is",
            "`docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`.",
            "No reported result metric is recalculated.",
            "",
        ]
    )
    return "\n".join(lines)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    rows = load_register()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    write_text(FIG2_PATH, generate_fig2(rows))
    write_text(FIG2_SPEC_PATH, generate_fig2_spec(rows))
    write_text(FIG3_PATH, generate_fig3(rows))
    write_text(FIG3_SPEC_PATH, generate_fig3_spec(rows))


if __name__ == "__main__":
    main()
