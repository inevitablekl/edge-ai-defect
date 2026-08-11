#!/usr/bin/env python3
"""Generate the Phase 5 candidate Figure 4 from its two frozen CSV authorities."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent.parent
ABSOLUTE_CSV_PATH = FIGURE_DIR / "fig3_mean_tail_latency_origin_data.csv"
RELATIVE_CSV_PATH = FIGURE_DIR / "fig4_v3r_v2r_latency_change_origin_data.csv"
OUTPUT_STEM = FIGURE_DIR / "fig4_mean_tail_latency_phase5_final"

ABSOLUTE_SCHEMA = ["Variant", "Mean_ms", "P95_ms", "P99_ms"]
RELATIVE_SCHEMA = ["Metric", "Relative_Change_Percent", "Direction"]
EXPECTED_ABSOLUTE_ROWS = [
    ("V0", Decimal("18.273"), Decimal("18.854"), Decimal("19.068")),
    ("V2R", Decimal("8.140"), Decimal("9.827"), Decimal("11.529")),
    ("V3R", Decimal("7.812"), Decimal("9.842"), Decimal("11.515")),
]
EXPECTED_RELATIVE_ROWS = [
    ("Mean", Decimal("-4.0349"), "lower/faster"),
    ("P95", Decimal("+0.1514"), "higher/slower"),
    ("P99", Decimal("-0.1184"), "lower/faster"),
]
METRICS = [("Mean", 1), ("P95", 2), ("P99", 3)]

MM_PER_INCH = 25.4
FIGURE_SIZE_MM = (170.0, 70.0)
SVG_METADATA = {"Date": "2026-08-11"}
PNG_METADATA = {"Date": "2026-08-11"}


def read_frozen_absolute_rows(path: Path) -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """Read and exactly validate the absolute-latency authority."""

    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ABSOLUTE_SCHEMA:
            raise ValueError(
                f"Absolute CSV schema mismatch: expected {ABSOLUTE_SCHEMA!r}, "
                f"got {reader.fieldnames!r}"
            )
        raw_rows = list(reader)
    try:
        rows = [
            (
                str(row["Variant"]),
                Decimal(str(row["Mean_ms"])),
                Decimal(str(row["P95_ms"])),
                Decimal(str(row["P99_ms"])),
            )
            for row in raw_rows
        ]
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Absolute CSV contains a non-decimal latency value") from exc
    if rows != EXPECTED_ABSOLUTE_ROWS:
        raise ValueError(
            f"Frozen absolute rows mismatch: expected {EXPECTED_ABSOLUTE_ROWS!r}, got {rows!r}"
        )
    return rows


def read_frozen_relative_rows(path: Path) -> list[tuple[str, Decimal, str]]:
    """Read and exactly validate each relative value, sign, order, and direction."""

    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != RELATIVE_SCHEMA:
            raise ValueError(
                f"Relative CSV schema mismatch: expected {RELATIVE_SCHEMA!r}, "
                f"got {reader.fieldnames!r}"
            )
        raw_rows = list(reader)
    try:
        rows = [
            (
                str(row["Metric"]),
                Decimal(str(row["Relative_Change_Percent"])),
                str(row["Direction"]),
            )
            for row in raw_rows
        ]
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Relative CSV contains a non-decimal change value") from exc
    if rows != EXPECTED_RELATIVE_ROWS:
        raise ValueError(
            f"Frozen relative rows mismatch: expected {EXPECTED_RELATIVE_ROWS!r}, got {rows!r}"
        )
    return rows


def select_fonts() -> tuple[str, str]:
    """Select deterministic installed serif fonts for Latin and Chinese text."""

    installed = {entry.name for entry in font_manager.fontManager.ttflist}
    latin = next(
        (
            name
            for name in ("Times New Roman", "Liberation Serif", "Nimbus Roman")
            if name in installed
        ),
        None,
    )
    chinese = next(
        (
            name
            for name in (
                "Noto Serif CJK SC",
                "Noto Serif CJK JP",
                "Droid Sans Fallback",
                "Source Han Serif SC",
                "SimSun",
            )
            if name in installed
        ),
        None,
    )
    if latin is None or chinese is None:
        raise RuntimeError("Required deterministic Latin/Chinese serif fonts are unavailable")
    return latin, chinese


def build_figure(
    absolute_rows: list[tuple[str, Decimal, Decimal, Decimal]],
    relative_rows: list[tuple[str, Decimal, str]],
    latin_font: str,
    chinese_font: str,
) -> plt.Figure:
    """Build the accepted absolute-plus-relative two-panel design."""

    plt.rcParams.update(
        {
            "font.family": [latin_font, chinese_font],
            "font.size": 8.0,
            "axes.labelsize": 8.3,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.5,
            # Type 3 outlines avoid the old Matplotlib/fontTools TTC subsetting
            # failure while preserving every CJK glyph in the PDF export.
            "pdf.fonttype": 3,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "edge-ai-defect-phase5-figure4",
            "hatch.linewidth": 0.5,
        }
    )

    figure_size = tuple(value / MM_PER_INCH for value in FIGURE_SIZE_MM)
    fig, (absolute_ax, relative_ax) = plt.subplots(
        1,
        2,
        figsize=figure_size,
        gridspec_kw={"width_ratios": [1.18, 1.0]},
        constrained_layout=True,
    )

    group_positions = list(range(len(METRICS)))
    bar_width = 0.22
    styles = [
        {"color": "#D9D9D9", "hatch": ""},
        {"color": "#CFE2F3", "hatch": "///"},
        {"color": "#FCE5CD", "hatch": "xx"},
    ]
    for variant_index, (row, style) in enumerate(zip(absolute_rows, styles)):
        positions = [value + (variant_index - 1) * bar_width for value in group_positions]
        values = [float(row[column_index]) for _, column_index in METRICS]
        absolute_ax.bar(
            positions,
            values,
            width=bar_width,
            label=row[0],
            color=style["color"],
            edgecolor="black",
            linewidth=0.7,
            hatch=style["hatch"],
            zorder=3,
        )

    absolute_ax.set_xticks(group_positions, [metric for metric, _ in METRICS])
    absolute_ax.set_ylabel("延迟/ms", fontfamily=chinese_font)
    absolute_ax.set_ylim(0, 21)
    absolute_ax.set_yticks(range(0, 21, 5))
    absolute_ax.grid(axis="y", color="#D9D9D9", linewidth=0.4, zorder=0)
    absolute_ax.set_axisbelow(True)
    absolute_ax.legend(loc="upper left", ncol=3, frameon=False, columnspacing=0.9)
    absolute_ax.text(
        0.0,
        1.02,
        "（a）各路径绝对延迟",
        transform=absolute_ax.transAxes,
        ha="left",
        va="bottom",
        fontfamily=chinese_font,
        fontsize=8.3,
    )

    relative_values = [float(row[1]) for row in relative_rows]
    relative_positions = list(range(len(relative_rows)))
    bars = relative_ax.bar(
        relative_positions,
        relative_values,
        width=0.56,
        color="#D9D9D9",
        edgecolor="black",
        linewidth=0.75,
        hatch="//",
        zorder=3,
    )
    relative_ax.axhline(0, color="black", linewidth=0.85, zorder=4)
    relative_ax.set_xticks(relative_positions, [row[0] for row in relative_rows])
    relative_ax.set_ylabel("V3R相对V2R的延迟变化/%", fontfamily=chinese_font)
    relative_ax.set_ylim(-5, 5)
    relative_ax.set_yticks(range(-5, 6, 1))
    relative_ax.grid(axis="y", color="#D9D9D9", linewidth=0.4, zorder=0)
    relative_ax.set_axisbelow(True)
    relative_ax.text(
        0.0,
        1.02,
        "（b）V3R相对V2R的冻结变化",
        transform=relative_ax.transAxes,
        ha="left",
        va="bottom",
        fontfamily=chinese_font,
        fontsize=8.3,
    )
    relative_ax.text(
        0.5,
        0.965,
        "负值=降低/更快；正值=升高/更慢",
        transform=relative_ax.transAxes,
        ha="center",
        va="top",
        fontfamily=chinese_font,
        fontsize=7.2,
    )
    for bar, (_, decimal_value, _) in zip(bars, relative_rows):
        value = float(decimal_value)
        offset = 3.0 if value >= 0 else -3.0
        relative_ax.annotate(
            f"{value:+.4f}%",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if value >= 0 else "top",
            fontsize=7.4,
            color="black",
            clip_on=False,
        )

    for axis in (absolute_ax, relative_ax):
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_color("black")
        axis.tick_params(axis="both", colors="black", width=0.65, length=3)
    return fig


def normalize_svg(path: Path) -> None:
    """Remove backend-added trailing spaces without changing SVG semantics."""

    text = path.read_text(encoding="utf-8")
    normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8", newline="\n")


def main() -> None:
    absolute_rows = read_frozen_absolute_rows(ABSOLUTE_CSV_PATH)
    relative_rows = read_frozen_relative_rows(RELATIVE_CSV_PATH)
    latin_font, chinese_font = select_fonts()
    figure = build_figure(absolute_rows, relative_rows, latin_font, chinese_font)
    try:
        svg_path = Path(f"{OUTPUT_STEM}.svg")
        figure.savefig(svg_path, format="svg", metadata=SVG_METADATA)
        normalize_svg(svg_path)
        figure.savefig(f"{OUTPUT_STEM}.pdf", format="pdf")
        figure.savefig(f"{OUTPUT_STEM}.png", format="png", dpi=300, metadata=PNG_METADATA)
    finally:
        plt.close(figure)

    print(f"Panel A CSV authority: {ABSOLUTE_CSV_PATH}")
    for row in absolute_rows:
        print(f"{row[0]}: Mean {row[1]:.3f}, P95 {row[2]:.3f}, P99 {row[3]:.3f}")
    print(f"Panel B CSV authority: {RELATIVE_CSV_PATH}")
    for metric, value, direction in relative_rows:
        print(f"{metric}: {value:+.4f}% ({direction})")
    print(f"Fonts: Latin={latin_font}; Chinese={chinese_font}")
    print("Panel B y range: -5% to +5%")
    print(f"Outputs: {OUTPUT_STEM}.svg/.pdf/.png")


if __name__ == "__main__":
    main()
