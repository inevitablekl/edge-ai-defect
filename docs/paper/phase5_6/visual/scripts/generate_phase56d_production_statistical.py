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

    cjk = FontProperties(fname=fc_path("Noto Serif CJK SC"))
    latin = FontProperties(fname=fc_path("Liberation Serif"))
    mpl.font_manager.fontManager.addfont(cjk.get_file())
    mpl.font_manager.fontManager.addfont(latin.get_file())
    mpl.rcParams.update({
        "font.family": [cjk.get_name()],
        "font.size": 8.5,
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
    ax.tick_params(direction="out", width=0.8, length=3)
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontfamily("Liberation Serif")


def save(fig: plt.Figure, output: Path) -> None:
    metadata = {
        "Creator": "Phase56D-B deterministic figure generator",
        "CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
    }
    fig.savefig(output.with_suffix(".svg"), metadata={"Date": "2000-01-01"})
    fig.savefig(output.with_suffix(".pdf"), metadata=metadata)
    fig.savefig(output.with_suffix(".png"), dpi=300,
                metadata={"Software": "Phase56D-B deterministic figure generator"})
    plt.close(fig)
    svg = output.with_suffix(".svg")
    normalized = "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n"
    svg.write_text(normalized, encoding="utf-8", newline="\n")


def figure3(grouped: dict[str, list[dict[str, float]]], summary: dict,
            output: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(6.30, 2.42), constrained_layout=False)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.20, top=0.88, wspace=0.38)
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
    axes[0].set_title("(a) 进程级 FPS", loc="left", fontsize=9.2, weight="bold")
    for bar, value in zip(bars, means):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value + 5.0, f"{value:.3f}",
                     ha="center", va="bottom", fontsize=6.8, fontfamily="Liberation Serif")
    axes[0].text(0.98, 0.98, "mean ± sample SD；5 processes / path",
                 transform=axes[0].transAxes, ha="right", va="top", fontsize=6.5)
    axes[0].text(0.03, 0.88,
                 f'V0→V2R  {display["v2r_v0_fps_ratio"]}；V2R→V3R  {display["v3r_v2r_fps"]}',
                 transform=axes[0].transAxes, fontsize=6.5, va="top")

    latency = [agg[v]["pooled_mean_latency_ms"] for v in VARIANTS]
    bars = axes[1].bar(
        range(3), latency, color=[COLORS[v] for v in VARIANTS],
        edgecolor=[EDGES[v] for v in VARIANTS], hatch=[HATCHES[v] for v in VARIANTS],
        linewidth=1.0, zorder=3,
    )
    axes[1].set_ylim(0, 27)
    axes[1].set_ylabel("E2E latency / ms")
    axes[1].set_xticks(range(3), VARIANTS)
    axes[1].set_title("(b) 平均 E2E 延迟", loc="left", fontsize=9.2, weight="bold")
    for bar, value in zip(bars, latency):
        axes[1].text(bar.get_x() + bar.get_width() / 2, value + 0.55, f"{value:.3f}",
                     ha="center", va="bottom", fontsize=6.8, fontfamily="Liberation Serif")
    axes[1].text(0.98, 0.98, "每路径合并5400个延迟样本",
                 transform=axes[1].transAxes, ha="right", va="top", fontsize=6.5)
    axes[1].text(0.05, 0.88,
                 f'V0→V2R  −{display["v2r_v0_mean_latency_reduction"]}\n'
                 f'V2R→V3R  {typographic_sign(display["v3r_v2r_mean_latency"])}',
                 transform=axes[1].transAxes, fontsize=6.5, va="top")

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
                         ha="center", va="bottom", fontsize=6.5, rotation=90,
                         fontfamily="Liberation Serif")
    axes[2].set_ylim(0, 21)
    axes[2].set_ylabel("latency / ms")
    axes[2].set_xticks(x, ["P95", "P99"])
    axes[2].set_title("(c) 尾延迟", loc="left", fontsize=9.2, weight="bold")
    axes[2].legend(frameon=False, ncol=3, loc="lower center", fontsize=6.7,
                   bbox_to_anchor=(0.5, -0.33), handlelength=1.8, columnspacing=0.9)
    for ax in axes:
        style_axis(ax)
    save(fig, output)


def figure4(grouped: dict[str, list[dict[str, float]]], summary: dict,
            output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.30, 2.82), constrained_layout=False)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.25, top=0.88, wspace=0.31)
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
    axes[0].set_ylabel("process-level FPS")
    axes[0].set_title("(a) 5 次独立进程 FPS", loc="left", fontsize=9.2, weight="bold")
    axes[0].text(0.02, 0.70, "点：独立 process\n横线/误差棒：mean ± sample SD",
                 transform=axes[0].transAxes, va="top", fontsize=6.8)

    metric_keys = ("mean", "p95", "p99")
    metric_labels = ("Mean", "P95", "P99")
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
    axes[1].set_xticks(list(centers), metric_labels)
    axes[1].set_ylabel("process-level latency / ms")
    axes[1].set_title("(b) V2R / V3R 运行级延迟", loc="left", fontsize=9.2, weight="bold")
    axes[1].legend(frameon=False, loc="upper left", fontsize=7.0, ncol=2)
    fig.text(
        0.75, 0.045,
        f'pooled：P95 {typographic_sign(display["v3r_v2r_p95"])}，'
        f'P99 {typographic_sign(display["v3r_v2r_p99"])} → MIXED',
        ha="center", va="bottom", fontsize=6.5,
        bbox={"boxstyle": "round,pad=0.16", "facecolor": "#faf7ea",
              "edgecolor": "#6b7280", "linewidth": 0.7},
    )
    for ax in axes:
        style_axis(ax)
    save(fig, output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configure()
    grouped, summary = load_sources()
    figure3(grouped, summary, args.output_dir / "fig3_main_e2e_phase56")
    figure4(grouped, summary, args.output_dir / "fig4_run_level_distribution_phase56")
    print(f"RUN_SOURCE_SHA256={sha256(RUN_SOURCE)}")
    print(f"SUMMARY_SOURCE_SHA256={sha256(SUMMARY_SOURCE)}")
    for stem in ("fig3_main_e2e_phase56", "fig4_run_level_distribution_phase56"):
        for suffix in ("svg", "pdf", "png"):
            print(f"GENERATED={args.output_dir / f'{stem}.{suffix}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
