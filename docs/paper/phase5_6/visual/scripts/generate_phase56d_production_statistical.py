#!/usr/bin/env python3
"""Generate deterministic Phase 5.6D-B statistical figure assets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402


ROOT = Path(__file__).resolve().parents[5]
PHASE56 = ROOT / "docs/paper/phase5_6"
RUN_SOURCE = PHASE56 / "phase56b_run_level_metrics.csv"
SUMMARY_SOURCE = PHASE56 / "phase56b_publication_display_values.json"
DEFAULT_OUTPUT = PHASE56 / "visual/production/figures"

EXPECTED_HASHES = {
    RUN_SOURCE: "f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31",
    SUMMARY_SOURCE: "0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655",
}
VARIANTS = ("V0", "V2R", "V3R")
COLORS = {"V0": "#c5cbd1", "V2R": "#b9d8eb", "V3R": "#efc9a8"}
EDGES = {"V0": "#30363c", "V2R": "#356b8b", "V3R": "#9a5b2d"}
HATCHES = {"V0": "..", "V2R": "///", "V3R": "\\\\"}
MARKERS = {"V0": "s", "V2R": "o", "V3R": "^"}
FIXED_JITTER = (-0.12, -0.06, 0.0, 0.06, 0.12)
# Accepted Phase 6.3R10 artist-tight canvases, expressed in figure inches.
# Keeping the absolute export boxes fixed prevents localized text metrics from
# changing the Word drawing aspect ratio or its accepted pagination geometry.
GOVERNED_EXPORT_BBOXES = {
    "fig3_main_e2e_phase56": (0.2836171805555556, 0.1673761944444447,
                               2.901499986111111, 5.577),
    "fig4_run_level_distribution_phase56": (0.3426171805555555, 0.2483007777777777,
                                              2.901499986111111, 4.401),
}
GOVERNED_PNG_CANVAS_PIXELS = {
    "fig3_main_e2e_phase56": (786, 1623),
    "fig4_run_level_distribution_phase56": (768, 1246),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def typographic_sign(value: str) -> str:
    return value.replace("-", "−")


def configure() -> tuple[FontProperties, FontProperties]:
    def fc_path(family: str) -> str:
        result = subprocess.run(
            ["fc-match", "-f", "%{file}", family], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        path = result.stdout.strip()
        if not path or not Path(path).is_file():
            raise RuntimeError(f"required font is unavailable: {family}")
        return path

    cjk = FontProperties(
        family="Noto Serif CJK SC", fname=fc_path("Noto Serif CJK SC")
    )
    latin = FontProperties(
        family="Liberation Serif", fname=fc_path("Liberation Serif")
    )
    mpl.font_manager.fontManager.addfont(cjk.get_file())
    mpl.font_manager.fontManager.addfont(latin.get_file())
    mpl.rcParams.update({
        # Times New Roman and SimSun are not installed in the Linux review
        # environment. Liberation Serif and Noto Serif CJK SC are the metric-
        # compatible review fallbacks; final Origin objects remain deferred.
        "font.family": [latin.get_name(), cjk.get_name()],
        "font.size": 7.5,
        "axes.linewidth": 0.8,
        "axes.unicode_minus": False,
        "pdf.fonttype": 3,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "phase56d-b-formal",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
    })
    return cjk, latin


def load_sources() -> tuple[dict[str, list[dict[str, float]]], dict]:
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"frozen source hash mismatch: {path}: {actual}")
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    with RUN_SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected = {
            "variant", "run_id", "execution_order", "fps", "mean_latency_ms",
            "process_p95_ms", "process_p99_ms", "measured_frames", "accepted",
            "independence_semantics", "source_path", "source_sha256",
        }
        if set(reader.fieldnames or ()) != expected:
            raise ValueError("run-level source schema mismatch")
        for row in reader:
            variant = row["variant"]
            if variant not in VARIANTS or row["accepted"] != "true":
                raise ValueError("unexpected variant or rejected row")
            if row["independence_semantics"] != "independent_process":
                raise ValueError("run independence contract mismatch")
            if int(row["measured_frames"]) != 1080:
                raise ValueError("measured frame count mismatch")
            grouped[variant].append({
                "fps": float(row["fps"]),
                "mean": float(row["mean_latency_ms"]),
                "p95": float(row["process_p95_ms"]),
                "p99": float(row["process_p99_ms"]),
            })
    if any(len(grouped[v]) != 5 for v in VARIANTS):
        raise ValueError("expected five accepted processes per path")
    summary = json.loads(SUMMARY_SOURCE.read_text(encoding="utf-8"))
    if summary["aggregation"] != {
        "processes_per_variant": 5,
        "samples_per_process": 1080,
        "pooled_samples_per_variant": 5400,
        "total_samples": 16200,
        "p95_p99": "pooled variant-level latency samples; not mean(process-level percentile)",
    }:
        raise ValueError("summary aggregation contract mismatch")
    for variant in VARIANTS:
        values = grouped[variant]
        authority = summary["aggregate_verification"][variant]
        if not math.isclose(statistics.mean(x["fps"] for x in values),
                            authority["mean_fps"], rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"{variant} FPS mean mismatch")
        if not math.isclose(statistics.stdev(x["fps"] for x in values),
                            authority["sample_sd_fps"], rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"{variant} FPS SD mismatch")
    return grouped, summary


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#d8dde2", linewidth=0.55, zorder=0)
    ax.tick_params(direction="in", width=0.8, length=3, labelsize=7.5)


def panel_label(ax: plt.Axes, label: str, y: float) -> None:
    ax.text(
        0.5, y, label, transform=ax.transAxes, ha="center", va="top",
        fontsize=7.5, fontfamily="Liberation Serif", clip_on=False,
    )


def save(fig: plt.Figure, output: Path) -> None:
    metadata = {
        "Creator": "Phase56D-B deterministic figure generator",
        "CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
    }
    # R10 used the artists' tight extent plus 0.04-inch padding. Freeze those
    # accepted final boxes explicitly so later label localization cannot alter
    # the exported aspect ratio and therefore the Word drawing extent.
    try:
        governed_bbox = Bbox.from_extents(*GOVERNED_EXPORT_BBOXES[output.name])
    except KeyError as exc:
        raise ValueError(f"no governed export bbox for {output.name}") from exc
    vector_options = {"bbox_inches": governed_bbox, "pad_inches": 0}
    fig.savefig(
        output.with_suffix(".svg"), metadata={"Date": "2000-01-01"}, **vector_options
    )
    fig.savefig(output.with_suffix(".pdf"), metadata=metadata, **vector_options)
    png_width, png_height = GOVERNED_PNG_CANVAS_PIXELS[output.name]
    png_bbox = Bbox.from_extents(
        governed_bbox.x1 - png_width / 300,
        governed_bbox.y1 - png_height / 300,
        governed_bbox.x1,
        governed_bbox.y1,
    )
    fig.savefig(
        output.with_suffix(".png"), dpi=300,
        metadata={"Software": "Phase56D-B deterministic figure generator"},
        bbox_inches=png_bbox, pad_inches=0,
    )
    plt.close(fig)
    svg = output.with_suffix(".svg")
    normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n"
    svg.write_text(normalized, encoding="utf-8", newline="\n")


def figure3(grouped: dict[str, list[dict[str, float]]], summary: dict,
            output: Path, cjk: FontProperties) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(2.95, 5.65), constrained_layout=False)
    fig.subplots_adjust(left=0.23, right=0.97, bottom=0.13, top=0.98, hspace=0.72)
    agg = summary["aggregate_verification"]
    display = summary["publication_display_precision"]

    means = [agg[v]["mean_fps"] for v in VARIANTS]
    sds = [agg[v]["sample_sd_fps"] for v in VARIANTS]
    bars = axes[0].bar(
        range(3), means, yerr=sds, capsize=3.2,
        color=[COLORS[v] for v in VARIANTS], edgecolor=[EDGES[v] for v in VARIANTS],
        hatch=[HATCHES[v] for v in VARIANTS], linewidth=1.0, zorder=3,
    )
    axes[0].set_ylim(0, 170)
    axes[0].set_ylabel("FPS")
    axes[0].set_xticks(range(3), VARIANTS)
    for bar, value in zip(bars, means):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value + 5.0, f"{value:.3f}",
                     ha="center", va="bottom", fontsize=7.5, fontfamily="Liberation Serif")
    axes[0].text(0.98, 0.98, "均值±样本SD；每路径5进程",
                 transform=axes[0].transAxes, ha="right", va="top", fontsize=7.5,
                 fontproperties=cjk)
    axes[0].text(0.03, 0.84,
                 f'V0→V2R  {display["v2r_v0_fps_ratio"]}\nV2R→V3R  {display["v3r_v2r_fps"]}',
                 transform=axes[0].transAxes, fontsize=7.5, va="top")
    panel_label(axes[0], "(a)", -0.25)

    latency = [agg[v]["pooled_mean_latency_ms"] for v in VARIANTS]
    bars = axes[1].bar(
        range(3), latency, color=[COLORS[v] for v in VARIANTS],
        edgecolor=[EDGES[v] for v in VARIANTS], hatch=[HATCHES[v] for v in VARIANTS],
        linewidth=1.0, zorder=3,
    )
    axes[1].set_ylim(0, 27)
    axes[1].set_ylabel("E2E 延迟 / ms", fontproperties=cjk)
    axes[1].set_xticks(range(3), VARIANTS)
    for bar, value in zip(bars, latency):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 0.55, f"{value:.3f}",
                     ha="center", va="bottom", fontsize=7.5, fontfamily="Liberation Serif")
    axes[1].text(0.98, 0.73, "合并 n=5400/路径",
                 transform=axes[1].transAxes, ha="right", va="top", fontsize=7.5,
                 fontproperties=cjk)
    axes[1].text(0.05, 0.98,
                 f'V0→V2R  −{display["v2r_v0_mean_latency_reduction"]}\n'
                 f'V2R→V3R  {typographic_sign(display["v3r_v2r_mean_latency"])}',
                 transform=axes[1].transAxes, fontsize=7.5, va="top")
    panel_label(axes[1], "(b)", -0.25)

    x = [0, 1]
    width = 0.23
    for offset, variant in zip((-width, 0, width), VARIANTS):
        values = [agg[variant]["pooled_p95_ms"], agg[variant]["pooled_p99_ms"]]
        bars = axes[2].bar(
            [p + offset for p in x], values, width=width, label=variant,
            color=COLORS[variant], edgecolor=EDGES[variant], hatch=HATCHES[variant],
            linewidth=1.0, zorder=3,
        )
        for bar, value in zip(bars, values):
            axes[2].text(bar.get_x() + bar.get_width() / 2, value + 0.22, f"{value:.3f}",
                         ha="center", va="bottom", fontsize=7.5, rotation=90,
                         fontfamily="Liberation Serif")
    axes[2].set_ylim(0, 21)
    axes[2].set_ylabel("延迟 / ms", fontproperties=cjk)
    axes[2].set_xticks(x, ["P95", "P99"])
    axes[2].legend(frameon=False, ncol=3, loc="lower center", fontsize=7.5,
                   bbox_to_anchor=(0.5, -0.29), handlelength=1.8, columnspacing=0.9)
    panel_label(axes[2], "(c)", -0.40)
    for ax in axes:
        style_axis(ax)
    save(fig, output)


def figure4(grouped: dict[str, list[dict[str, float]]], summary: dict,
            output: Path, cjk: FontProperties) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(2.95, 4.45), constrained_layout=False)
    fig.subplots_adjust(left=0.25, right=0.97, bottom=0.16, top=0.98, hspace=0.66)
    agg = summary["aggregate_verification"]
    display = summary["publication_display_precision"]

    for base, variant in enumerate(VARIANTS):
        values = [x["fps"] for x in grouped[variant]]
        axes[0].scatter(
            [base + j for j in FIXED_JITTER], values, s=27, marker=MARKERS[variant],
            facecolor=COLORS[variant], edgecolor=EDGES[variant], linewidth=0.9, zorder=4,
        )
        axes[0].errorbar(
            base, agg[variant]["mean_fps"], yerr=agg[variant]["sample_sd_fps"],
            fmt="_", markersize=15, color="#111111", linewidth=1.2, capsize=4, zorder=5,
        )
    axes[0].set_xlim(-0.45, 2.45)
    axes[0].set_ylim(50, 132)
    axes[0].set_xticks(range(3), VARIANTS)
    axes[0].set_ylabel("进程级 FPS", fontproperties=cjk, labelpad=1)
    axes[0].text(0.02, 0.70, "点：独立进程\n横线/误差：均值±样本SD",
                 transform=axes[0].transAxes, va="top", fontsize=7.5,
                 fontproperties=cjk)
    panel_label(axes[0], "(a)", -0.24)

    metric_keys = ("mean", "p95", "p99")
    metric_labels = ("均值", "P95", "P99")
    centers = range(3)
    for variant, shift in (("V2R", -0.16), ("V3R", 0.16)):
        for base, key in zip(centers, metric_keys):
            values = [x[key] for x in grouped[variant]]
            xs = [base + shift + j * 0.55 for j in FIXED_JITTER]
            axes[1].scatter(
                xs, values, s=27, marker=MARKERS[variant], facecolor=COLORS[variant],
                edgecolor=EDGES[variant], linewidth=0.9,
                label=variant if base == 0 else None, zorder=4,
            )
    axes[1].set_xlim(-0.55, 2.55)
    axes[1].set_ylim(7.45, 12.05)
    axes[1].set_xticks(list(centers), metric_labels, fontproperties=cjk)
    axes[1].set_ylabel("进程级延迟 / ms", fontproperties=cjk, labelpad=1)
    axes[1].legend(frameon=False, loc="upper left", fontsize=7.5, ncol=2)
    axes[1].text(
        0.5, 0.04,
        f'P95 {typographic_sign(display["v3r_v2r_p95"])}; '
        f'P99 {typographic_sign(display["v3r_v2r_p99"])}\n方向相反',
        transform=axes[1].transAxes, ha="center", va="bottom", fontsize=7.5,
        fontproperties=cjk,
        bbox={"boxstyle": "round,pad=0.16", "facecolor": "#faf7ea",
              "edgecolor": "#6b7280", "linewidth": 0.7},
    )
    panel_label(axes[1], "(b)", -0.24)
    for ax in axes:
        style_axis(ax)
    save(fig, output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cjk, _latin = configure()
    grouped, summary = load_sources()
    figure3(grouped, summary, args.output_dir / "fig3_main_e2e_phase56", cjk)
    figure4(grouped, summary, args.output_dir / "fig4_run_level_distribution_phase56", cjk)
    print(f"RUN_SOURCE_SHA256={sha256(RUN_SOURCE)}")
    print(f"SUMMARY_SOURCE_SHA256={sha256(SUMMARY_SOURCE)}")
    for stem in ("fig3_main_e2e_phase56", "fig4_run_level_distribution_phase56"):
        for suffix in ("svg", "pdf", "png"):
            print(f"GENERATED={args.output_dir / f'{stem}.{suffix}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
