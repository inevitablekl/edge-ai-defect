#!/usr/bin/env python3
"""Generate the Phase 5 candidate Figure 3 from its frozen CSV authority."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt


FIGURE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = FIGURE_DIR / "fig2_mean_fps_origin_data.csv"
OUTPUT_STEM = FIGURE_DIR / "fig3_mean_fps_phase5_final"

EXPECTED_SCHEMA = ["Variant", "Mean_FPS", "Sample_SD_FPS"]
EXPECTED_ROWS = [
    ("V0", Decimal("54.600"), Decimal("0.223")),
    ("V2R", Decimal("122.122"), Decimal("0.492")),
    ("V3R", Decimal("127.097"), Decimal("1.279")),
]

MM_PER_INCH = 25.4
FIGURE_SIZE_MM = (82.0, 62.0)
SVG_METADATA = {"Date": "2026-08-11"}
PNG_METADATA = {"Date": "2026-08-11"}


def read_frozen_rows(csv_path: Path) -> list[tuple[str, Decimal, Decimal]]:
    """Read the CSV and reject any schema, order, or frozen-value change."""

    with csv_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPECTED_SCHEMA:
            raise ValueError(
                f"CSV schema mismatch: expected {EXPECTED_SCHEMA!r}, "
                f"got {reader.fieldnames!r}"
            )
        raw_rows = list(reader)

    try:
        rows = [
            (
                str(row["Variant"]),
                Decimal(str(row["Mean_FPS"])),
                Decimal(str(row["Sample_SD_FPS"])),
            )
            for row in raw_rows
        ]
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("CSV contains a non-decimal FPS value") from exc

    if rows != EXPECTED_ROWS:
        raise ValueError(f"Frozen FPS rows mismatch: expected {EXPECTED_ROWS!r}, got {rows!r}")
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
    rows: list[tuple[str, Decimal, Decimal]], latin_font: str, chinese_font: str
) -> plt.Figure:
    """Build the zero-baseline bar chart with symmetric sample-SD error bars."""

    plt.rcParams.update(
        {
            "font.family": [latin_font, chinese_font],
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            # Type 3 outlines avoid the old Matplotlib/fontTools TTC subsetting
            # failure while preserving every CJK glyph in the PDF export.
            "pdf.fonttype": 3,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "edge-ai-defect-phase5-figure3",
            "hatch.linewidth": 0.55,
        }
    )

    figure_size = tuple(value / MM_PER_INCH for value in FIGURE_SIZE_MM)
    fig, ax = plt.subplots(figsize=figure_size, constrained_layout=True)
    labels = [row[0] for row in rows]
    means = [float(row[1]) for row in rows]
    sample_sds = [float(row[2]) for row in rows]
    styles = [
        {"color": "#D9D9D9", "hatch": ""},
        {"color": "#CFE2F3", "hatch": "///"},
        {"color": "#FCE5CD", "hatch": "xx"},
    ]

    for position, (mean, sample_sd, style) in enumerate(zip(means, sample_sds, styles)):
        ax.bar(
            position,
            mean,
            width=0.58,
            yerr=sample_sd,
            capsize=2.5,
            color=style["color"],
            edgecolor="black",
            linewidth=0.75,
            hatch=style["hatch"],
            error_kw={"ecolor": "black", "elinewidth": 0.75, "capthick": 0.75},
            zorder=3,
        )
        ax.annotate(
            f"{mean:.3f}",
            xy=(position, mean + sample_sd),
            xytext=(0, 2.5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.6,
            color="black",
            clip_on=False,
        )

    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel(r"平均帧率/(frame·s$^{-1}$)", fontfamily=chinese_font)
    ax.set_ylim(0, 150)
    ax.set_yticks(range(0, 151, 25))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("black")
    ax.tick_params(axis="both", colors="black", width=0.65, length=3)
    ax.margins(x=0.24)
    return fig


def normalize_svg(path: Path) -> None:
    """Remove backend-added trailing spaces without changing SVG semantics."""

    text = path.read_text(encoding="utf-8")
    normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(normalized, encoding="utf-8", newline="\n")


def main() -> None:
    rows = read_frozen_rows(CSV_PATH)
    latin_font, chinese_font = select_fonts()
    figure = build_figure(rows, latin_font, chinese_font)
    try:
        svg_path = Path(f"{OUTPUT_STEM}.svg")
        figure.savefig(svg_path, format="svg", metadata=SVG_METADATA)
        normalize_svg(svg_path)
        figure.savefig(f"{OUTPUT_STEM}.pdf", format="pdf")
        figure.savefig(f"{OUTPUT_STEM}.png", format="png", dpi=300, metadata=PNG_METADATA)
    finally:
        plt.close(figure)

    print(f"CSV authority: {CSV_PATH}")
    for variant, mean, sample_sd in rows:
        print(f"{variant}: Mean {mean:.3f}, sample SD {sample_sd:.3f}")
    print(f"Fonts: Latin={latin_font}; Chinese={chinese_font}")
    print(f"Y range: 0 to 150 FPS")
    print(f"Outputs: {OUTPUT_STEM}.svg/.pdf/.png")


if __name__ == "__main__":
    main()
