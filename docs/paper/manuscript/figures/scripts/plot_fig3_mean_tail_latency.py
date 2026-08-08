#!/usr/bin/env python3
"""Produce publication Figure 3 from its authoritative latency CSV.

The input contains accepted display values.  This script only reshapes those
values for plotting and performs no statistical calculation.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = FIGURE_DIR / "fig3_mean_tail_latency_origin_data.csv"
OUTPUT_STEM = FIGURE_DIR / "fig3_mean_tail_latency_final"

EXPECTED_SCHEMA = ["Variant", "Mean_ms", "P95_ms", "P99_ms"]
EXPECTED_VARIANTS = ["V0", "V2R", "V3R"]
METRICS = [("Mean", "Mean_ms"), ("P95", "P95_ms"), ("P99", "P99_ms")]

MM_PER_INCH = 25.4
FIGURE_SIZE_MM = (82.0, 62.0)


def read_authoritative_rows(csv_path: Path) -> list[dict[str, object]]:
    """Read and validate the frozen CSV without recalculating its values."""

    with csv_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPECTED_SCHEMA:
            raise ValueError(
                f"CSV schema mismatch: expected {EXPECTED_SCHEMA!r}, "
                f"got {reader.fieldnames!r}"
            )
        raw_rows = list(reader)

    variants = [row["Variant"] for row in raw_rows]
    if variants != EXPECTED_VARIANTS:
        raise ValueError(
            f"Variant order mismatch: expected {EXPECTED_VARIANTS!r}, got {variants!r}"
        )
    if len(raw_rows) != len(EXPECTED_VARIANTS):
        raise ValueError(
            f"Unexpected row count: expected {len(EXPECTED_VARIANTS)}, "
            f"got {len(raw_rows)}"
        )

    rows: list[dict[str, object]] = []
    for row in raw_rows:
        parsed_row: dict[str, object] = {"Variant": row["Variant"]}
        for _, column in METRICS:
            try:
                value = float(row[column])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Non-numeric latency value in row {row!r}") from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid latency value in row {row!r}")
            parsed_row[column] = value
        rows.append(parsed_row)
    return rows


def select_serif_font() -> str:
    """Select Times New Roman when installed, otherwise the Figure 2 fallback."""

    installed_families = {entry.name for entry in font_manager.fontManager.ttflist}
    for family in ("Times New Roman", "Liberation Serif", "Nimbus Roman", "DejaVu Serif"):
        if family in installed_families:
            return family
    raise RuntimeError("No supported serif font found")


def build_figure(rows: list[dict[str, object]], font_family: str) -> plt.Figure:
    """Build the grouped grayscale bar chart with no uncertainty annotations."""

    variant_labels = [str(row["Variant"]) for row in rows]
    metric_labels = [label for label, _ in METRICS]
    group_positions = list(range(len(metric_labels)))
    bar_width = 0.16
    group_offset = 0.36

    plt.rcParams.update(
        {
            "font.family": font_family,
            "font.size": 7.7,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    figure_size_inches = tuple(size / MM_PER_INCH for size in FIGURE_SIZE_MM)
    fig, ax = plt.subplots(figsize=figure_size_inches, constrained_layout=True)

    # Grayscale fills and hatches preserve series identity in black-and-white.
    series_style = [
        {"color": "#B3B3B3", "hatch": ""},
        {"color": "#E0E0E0", "hatch": "///"},
        {"color": "#808080", "hatch": "..."},
    ]
    for series_index, (variant, style) in enumerate(zip(variant_labels, series_style)):
        variant_row = rows[series_index]
        values = [float(variant_row[column]) for _, column in METRICS]
        bar_positions = [
            position + (series_index - 1) * group_offset for position in group_positions
        ]
        bars = ax.bar(
            bar_positions,
            values,
            width=bar_width,
            label=variant,
            color=style["color"],
            edgecolor="black",
            linewidth=0.65,
            hatch=style["hatch"],
            zorder=3,
        )
        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value:.3f}",
                xy=(bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, 2.0),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=6.7,
                color="black",
                clip_on=False,
            )

    ax.set_xticks(group_positions, metric_labels)
    ax.set_ylabel("Latency / ms")
    ax.set_ylim(0, 22)
    ax.set_yticks(range(0, 23, 2))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("black")
    ax.spines["bottom"].set_color("black")
    ax.tick_params(axis="both", colors="black", width=0.6, length=3)
    ax.margins(x=0.12)
    ax.legend(
        loc="upper right",
        ncol=3,
        frameon=False,
        handlelength=1.5,
        handletextpad=0.35,
        columnspacing=0.8,
        borderaxespad=0.1,
    )

    return fig


def main() -> None:
    rows = read_authoritative_rows(CSV_PATH)
    font_family = select_serif_font()
    figure = build_figure(rows, font_family)
    try:
        figure.savefig(f"{OUTPUT_STEM}.pdf", format="pdf")
        figure.savefig(f"{OUTPUT_STEM}.svg", format="svg")
        figure.savefig(f"{OUTPUT_STEM}.png", format="png", dpi=300)
    finally:
        plt.close(figure)

    print(f"CSV: {CSV_PATH}")
    print(f"Font: {font_family}")
    print(f"Figure size: {FIGURE_SIZE_MM[0]:.1f} mm x {FIGURE_SIZE_MM[1]:.1f} mm")
    for row in rows:
        print(
            f"{row['Variant']} "
            + " ".join(f"{label} {float(row[column]):.3f}" for label, column in METRICS)
        )
    print(f"Outputs: {OUTPUT_STEM}.pdf, {OUTPUT_STEM}.svg, {OUTPUT_STEM}.png")


if __name__ == "__main__":
    main()
