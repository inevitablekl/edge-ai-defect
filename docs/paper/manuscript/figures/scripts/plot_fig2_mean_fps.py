#!/usr/bin/env python3
"""Produce the publication Figure 2 mean-FPS bar chart from its frozen CSV.

The CSV is the only source of the plotted means and sample standard deviations.
This script intentionally performs no aggregation or statistical calculation.
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
CSV_PATH = FIGURE_DIR / "fig2_mean_fps_origin_data.csv"
OUTPUT_STEM = FIGURE_DIR / "fig2_mean_fps_final"

EXPECTED_SCHEMA = ["Variant", "Mean_FPS", "Sample_SD_FPS"]
EXPECTED_VARIANTS = ["V0", "V2R", "V3R"]

MM_PER_INCH = 25.4
FIGURE_SIZE_MM = (75.0, 58.0)


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
        try:
            mean = float(row["Mean_FPS"])
            sample_sd = float(row["Sample_SD_FPS"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Non-numeric FPS value in row {row!r}") from exc
        if not math.isfinite(mean) or not math.isfinite(sample_sd):
            raise ValueError(f"Non-finite FPS value in row {row!r}")
        if sample_sd < 0:
            raise ValueError(f"Negative Sample_SD_FPS in row {row!r}")
        rows.append(
            {
                "Variant": row["Variant"],
                "Mean_FPS": mean,
                "Sample_SD_FPS": sample_sd,
            }
        )
    return rows


def select_serif_font() -> str:
    """Select Times New Roman when installed, otherwise a serif fallback."""

    installed_families = {entry.name for entry in font_manager.fontManager.ttflist}
    for family in ("Times New Roman", "Liberation Serif", "Nimbus Roman", "DejaVu Serif"):
        if family in installed_families:
            return family
    raise RuntimeError("No supported serif font found")


def build_figure(rows: list[dict[str, object]], font_family: str) -> plt.Figure:
    """Build the ordinary grayscale vertical bar chart required by Figure 2."""

    labels = [str(row["Variant"]) for row in rows]
    means = [float(row["Mean_FPS"]) for row in rows]
    sample_sds = [float(row["Sample_SD_FPS"]) for row in rows]

    plt.rcParams.update(
        {
            "font.family": font_family,
            "font.size": 8.0,
            "axes.titlesize": 8.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    figure_size_inches = tuple(size / MM_PER_INCH for size in FIGURE_SIZE_MM)
    fig, ax = plt.subplots(figsize=figure_size_inches, constrained_layout=True)

    positions = range(len(labels))
    ax.bar(
        positions,
        means,
        width=0.58,
        yerr=sample_sds,
        capsize=2.4,
        color="#BFBFBF",
        edgecolor="black",
        linewidth=0.75,
        error_kw={
            "ecolor": "black",
            "elinewidth": 0.75,
            "capthick": 0.75,
        },
        zorder=3,
    )

    ax.set_xticks(list(positions), labels)
    ax.set_ylabel("FPS")
    ax.set_ylim(0, 140)
    ax.set_yticks(range(0, 141, 20))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("black")
    ax.spines["bottom"].set_color("black")
    ax.tick_params(axis="both", colors="black", width=0.65, length=3)
    ax.margins(x=0.24)

    for position, mean, sample_sd in zip(positions, means, sample_sds):
        # Labels show the frozen Mean_FPS value to exactly three decimals.
        ax.annotate(
            f"{mean:.3f}",
            xy=(position, mean + sample_sd),
            xytext=(0, 2.5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.7,
            color="black",
            clip_on=False,
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
            f"{row['Variant']} Mean {float(row['Mean_FPS']):.3f} "
            f"SD {float(row['Sample_SD_FPS']):.3f}"
        )
    print(f"Outputs: {OUTPUT_STEM}.pdf, {OUTPUT_STEM}.svg, {OUTPUT_STEM}.png")


if __name__ == "__main__":
    main()
