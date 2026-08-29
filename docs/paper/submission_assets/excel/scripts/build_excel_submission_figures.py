#!/usr/bin/env python3
"""Build native Excel submission assets for manuscript Figures 2 and 3.

The frozen Phase 5.6 CSV/JSON files are the sole numerical authorities. The
accepted SVG/PNG files are visual references only and are never embedded.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import xlsxwriter
from xlsxwriter.utility import xl_range_abs, xl_rowcol_to_cell


ROOT = Path(__file__).resolve().parents[5]
PHASE56 = ROOT / "docs/paper/phase5_6"
OUTPUT_ROOT = ROOT / "docs/paper/submission_assets/excel"
RUN_SOURCE = PHASE56 / "phase56b_run_level_metrics.csv"
SUMMARY_SOURCE = PHASE56 / "phase56b_publication_display_values.json"
FIGURE2_OUTPUT = OUTPUT_ROOT / "Figure2_E2E_performance.xlsx"
FIGURE3_OUTPUT = OUTPUT_ROOT / "Figure3_run_level_distribution.xlsx"

EXPECTED_HASHES = {
    RUN_SOURCE: "f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31",
    SUMMARY_SOURCE: "0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655",
}
VARIANTS = ("V0", "V2R", "V3R")
COLORS = {"V0": "#C5CBD1", "V2R": "#B9D8EB", "V3R": "#EFC9A8"}
EDGES = {"V0": "#30363C", "V2R": "#356B8B", "V3R": "#9A5B2D"}
PATTERNS = {
    "V0": "dotted_grid",
    "V2R": "wide_upward_diagonal",
    "V3R": "wide_downward_diagonal",
}
MARKERS = {"V0": "square", "V2R": "circle", "V3R": "triangle"}
FIXED_JITTER = (-0.12, -0.06, 0.0, 0.06, 0.12)
EXPECTED_SHEETS = ("RawRuns", "DisplayValues", "Figure")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def typographic_sign(value: str) -> str:
    return value.replace("-", "−")


def assert_close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10):
        raise ValueError(f"{label} mismatch: {actual} != {expected}")


def load_authorities() -> tuple[list[dict[str, str]], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Load and fully reconcile the frozen scientific authorities."""
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"frozen source hash mismatch: {path}: {actual}")

    with RUN_SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {
            "variant", "run_id", "execution_order", "fps", "mean_latency_ms",
            "process_p95_ms", "process_p99_ms", "measured_frames", "accepted",
            "independence_semantics", "source_path", "source_sha256",
        }
        if set(reader.fieldnames or ()) != expected_fields:
            raise ValueError("run-level source schema mismatch")
        rows = list(reader)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        variant = row["variant"]
        if variant not in VARIANTS or row["accepted"] != "true":
            raise ValueError("unexpected variant or rejected run")
        if row["independence_semantics"] != "independent_process":
            raise ValueError("run independence contract mismatch")
        if int(row["measured_frames"]) != 1080:
            raise ValueError("measured frame count mismatch")
        grouped[variant].append({
            "run_id": row["run_id"],
            "execution_order": int(row["execution_order"]),
            "fps": float(row["fps"]),
            "mean": float(row["mean_latency_ms"]),
            "p95": float(row["process_p95_ms"]),
            "p99": float(row["process_p99_ms"]),
        })
    for variant in VARIANTS:
        grouped[variant].sort(key=lambda item: item["execution_order"])
        if len(grouped[variant]) != 5:
            raise ValueError(f"expected five accepted processes for {variant}")

    summary = json.loads(SUMMARY_SOURCE.read_text(encoding="utf-8"))
    if summary.get("process_semantics") != "15 independent processes; not paired or matched repeated measures":
        raise ValueError("summary process semantics mismatch")
    expected_aggregation = {
        "processes_per_variant": 5,
        "samples_per_process": 1080,
        "pooled_samples_per_variant": 5400,
        "total_samples": 16200,
        "p95_p99": "pooled variant-level latency samples; not mean(process-level percentile)",
    }
    if summary.get("aggregation") != expected_aggregation:
        raise ValueError("summary aggregation contract mismatch")
    if summary.get("alters_level_a_authority") is not False:
        raise ValueError("unexpected authority status")

    for variant in VARIANTS:
        authority = summary["aggregate_verification"][variant]
        values = grouped[variant]
        assert_close(statistics.mean(item["fps"] for item in values),
                     authority["mean_fps"], f"{variant} FPS mean")
        assert_close(statistics.stdev(item["fps"] for item in values),
                     authority["sample_sd_fps"], f"{variant} FPS sample SD")
        assert_close(min(item["fps"] for item in values),
                     authority["min_fps"], f"{variant} FPS minimum")
        assert_close(max(item["fps"] for item in values),
                     authority["max_fps"], f"{variant} FPS maximum")
        assert_close(statistics.mean(item["mean"] for item in values),
                     authority["pooled_mean_latency_ms"], f"{variant} pooled mean latency")
        if authority["accepted_independent_processes"] != 5 or authority["latency_samples"] != 5400:
            raise ValueError(f"{variant} aggregate count mismatch")

    return rows, grouped, summary


def workbook_formats(workbook: xlsxwriter.Workbook) -> dict[str, Any]:
    return {
        "title": workbook.add_format({
            "bold": True, "font_name": "Microsoft YaHei", "font_size": 14,
            "font_color": "#1F2937",
        }),
        "section": workbook.add_format({
            "bold": True, "font_name": "Microsoft YaHei", "font_color": "#FFFFFF",
            "bg_color": "#374151", "border": 1,
        }),
        "header": workbook.add_format({
            "bold": True, "font_name": "Microsoft YaHei", "font_color": "#FFFFFF",
            "bg_color": "#4B5563", "border": 1, "align": "center", "valign": "vcenter",
        }),
        "text": workbook.add_format({"font_name": "Microsoft YaHei", "border": 1}),
        "integer": workbook.add_format({
            "font_name": "Times New Roman", "num_format": "0", "border": 1,
        }),
        "number": workbook.add_format({
            "font_name": "Times New Roman", "num_format": "0.000000000", "border": 1,
        }),
        "display": workbook.add_format({
            "font_name": "Times New Roman", "num_format": "0.000", "border": 1,
        }),
        "note": workbook.add_format({
            "font_name": "Microsoft YaHei", "font_color": "#4B5563", "text_wrap": True,
        }),
    }


def configure_workbook(workbook: xlsxwriter.Workbook, title: str) -> None:
    workbook.set_properties({
        "title": title,
        "subject": "Native Excel chart submission asset generated from frozen Phase 5.6 data",
        "author": "Edge AI Industrial Defect Detection project",
        "comments": "Scientific authority: phase56b_run_level_metrics.csv and phase56b_publication_display_values.json",
        "created": datetime(2000, 1, 1),
    })


def write_raw_runs(worksheet: Any, rows: list[dict[str, str]], formats: dict[str, Any]) -> None:
    fields = list(rows[0].keys())
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(1, 0)
    worksheet.set_column(0, 0, 12)
    worksheet.set_column(1, 1, 24)
    worksheet.set_column(2, 9, 20)
    worksheet.set_column(10, 10, 110)
    worksheet.set_column(11, 11, 68)
    for column, field in enumerate(fields):
        worksheet.write(0, column, field, formats["header"])
    integer_fields = {"execution_order", "measured_frames"}
    number_fields = {"fps", "mean_latency_ms", "process_p95_ms", "process_p99_ms"}
    for out_row, source in enumerate(rows, start=1):
        for column, field in enumerate(fields):
            value: Any = source[field]
            fmt = formats["text"]
            if field in integer_fields:
                value = int(value)
                fmt = formats["integer"]
            elif field in number_fields:
                value = float(value)
                fmt = formats["number"]
            worksheet.write(out_row, column, value, fmt)
    worksheet.autofilter(0, 0, len(rows), len(fields) - 1)


def write_display_header(worksheet: Any, formats: dict[str, Any], figure_name: str) -> None:
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(3, 0)
    worksheet.set_column(0, 0, 23)
    worksheet.set_column(1, 12, 20)
    worksheet.write(0, 0, figure_name, formats["title"])
    worksheet.write(1, 0, "数值来源：冻结 CSV/JSON；绝对值显示精度为三位小数。", formats["note"])


def write_figure2_display(worksheet: Any, grouped: dict[str, list[dict[str, Any]]],
                          summary: dict[str, Any], formats: dict[str, Any]) -> dict[str, tuple[int, int, int, int]]:
    del grouped  # Run-level values are preserved in RawRuns; Figure 2 uses frozen aggregates.
    write_display_header(worksheet, formats, "Figure 2 — 三条路径的端到端性能")
    agg = summary["aggregate_verification"]
    display = summary["publication_display_precision"]

    worksheet.write(3, 0, "Panel (a): FPS mean ± sample SD", formats["section"])
    headers = ("variant", "mean_fps", "sample_sd_fps", "processes")
    worksheet.write_row(4, 0, headers, formats["header"])
    for index, variant in enumerate(VARIANTS, start=5):
        worksheet.write(index, 0, variant, formats["text"])
        worksheet.write_number(index, 1, agg[variant]["mean_fps"], formats["display"])
        worksheet.write_number(index, 2, agg[variant]["sample_sd_fps"], formats["display"])
        worksheet.write_number(index, 3, agg[variant]["accepted_independent_processes"], formats["integer"])

    worksheet.write(10, 0, "Panel (b): pooled mean E2E latency", formats["section"])
    worksheet.write_row(11, 0, ("variant", "pooled_mean_latency_ms", "pooled_samples"), formats["header"])
    for index, variant in enumerate(VARIANTS, start=12):
        worksheet.write(index, 0, variant, formats["text"])
        worksheet.write_number(index, 1, agg[variant]["pooled_mean_latency_ms"], formats["display"])
        worksheet.write_number(index, 2, agg[variant]["latency_samples"], formats["integer"])

    worksheet.write(17, 0, "Panel (c): pooled P95/P99", formats["section"])
    worksheet.write_row(18, 0, ("metric", *VARIANTS), formats["header"])
    for row_index, (label, key) in enumerate((("P95", "pooled_p95_ms"), ("P99", "pooled_p99_ms")), start=19):
        worksheet.write(row_index, 0, label, formats["text"])
        for column, variant in enumerate(VARIANTS, start=1):
            worksheet.write_number(row_index, column, agg[variant][key], formats["display"])

    worksheet.write(24, 0, "Accepted comparison annotations", formats["section"])
    worksheet.write_row(25, 0, ("comparison", "display_value"), formats["header"])
    comparisons = (
        ("V0→V2R FPS", display["v2r_v0_fps_ratio"]),
        ("V2R→V3R FPS", display["v3r_v2r_fps"]),
        ("V0→V2R mean latency", f'−{display["v2r_v0_mean_latency_reduction"]}'),
        ("V2R→V3R mean latency", typographic_sign(display["v3r_v2r_mean_latency"])),
    )
    for row_index, values in enumerate(comparisons, start=26):
        worksheet.write_row(row_index, 0, values, formats["text"])

    return {
        "fps": (5, 0, 7, 2),
        "mean_latency": (12, 0, 14, 1),
        "tails": (19, 0, 20, 3),
    }


def write_figure3_display(worksheet: Any, grouped: dict[str, list[dict[str, Any]]],
                          summary: dict[str, Any], formats: dict[str, Any]) -> dict[str, tuple[int, int, int, int]]:
    write_display_header(worksheet, formats, "Figure 3 — 运行级分布与尾延迟")
    agg = summary["aggregate_verification"]
    display = summary["publication_display_precision"]

    worksheet.write(3, 0, "Panel (a): process-level FPS points", formats["section"])
    headers = ("variant", "x", "fps", "run_id", "execution_order")
    worksheet.write_row(4, 0, headers, formats["header"])
    row_index = 5
    fps_ranges: dict[str, tuple[int, int, int, int]] = {}
    for base, variant in enumerate(VARIANTS, start=1):
        first = row_index
        for jitter, run in zip(FIXED_JITTER, grouped[variant]):
            worksheet.write(row_index, 0, variant, formats["text"])
            worksheet.write_number(row_index, 1, base + jitter, formats["number"])
            worksheet.write_number(row_index, 2, run["fps"], formats["number"])
            worksheet.write(row_index, 3, run["run_id"], formats["text"])
            worksheet.write_number(row_index, 4, run["execution_order"], formats["integer"])
            row_index += 1
        fps_ranges[variant] = (first, 1, row_index - 1, 2)

    worksheet.write(22, 0, "Panel (a): descriptive summary", formats["section"])
    worksheet.write_row(23, 0, ("variant", "x", "mean_fps", "sample_sd_fps"), formats["header"])
    for row_index, (base, variant) in enumerate(zip((1, 2, 3), VARIANTS), start=24):
        worksheet.write(row_index, 0, variant, formats["text"])
        worksheet.write_number(row_index, 1, base, formats["integer"])
        worksheet.write_number(row_index, 2, agg[variant]["mean_fps"], formats["number"])
        worksheet.write_number(row_index, 3, agg[variant]["sample_sd_fps"], formats["number"])

    worksheet.write(29, 0, "Panel (b): process-level latency points", formats["section"])
    worksheet.write_row(30, 0, ("variant", "metric", "x", "latency_ms", "run_id"), formats["header"])
    latency_ranges: dict[str, tuple[int, int, int, int]] = {}
    row_index = 31
    for variant, shift in (("V2R", -0.16), ("V3R", 0.16)):
        first = row_index
        for center, key in zip((1, 2, 3), ("mean", "p95", "p99")):
            for jitter, run in zip(FIXED_JITTER, grouped[variant]):
                worksheet.write(row_index, 0, variant, formats["text"])
                worksheet.write(row_index, 1, {"mean": "均值", "p95": "P95", "p99": "P99"}[key], formats["text"])
                worksheet.write_number(row_index, 2, center + shift + jitter * 0.55, formats["number"])
                worksheet.write_number(row_index, 3, run[key], formats["number"])
                worksheet.write(row_index, 4, run["run_id"], formats["text"])
                row_index += 1
        latency_ranges[variant] = (first, 2, row_index - 1, 3)

    worksheet.write(63, 0, "Accepted pooled-tail annotation", formats["section"])
    worksheet.write_row(64, 0, ("x", "y", "annotation"), formats["header"])
    worksheet.write_number(65, 0, 2.0, formats["number"])
    worksheet.write_number(65, 1, 7.72, formats["number"])
    annotation = (
        f'P95 {typographic_sign(display["v3r_v2r_p95"])}; '
        f'P99 {typographic_sign(display["v3r_v2r_p99"])}\n方向相反'
    )
    worksheet.write(65, 2, annotation, formats["text"])

    worksheet.write(68, 0, "Panel (a): native category-label helper", formats["section"])
    worksheet.write_row(69, 0, ("x", "y", "category_label"), formats["header"])
    for row_index, (x_value, label) in enumerate(zip((1, 2, 3), VARIANTS), start=70):
        worksheet.write_number(row_index, 0, x_value, formats["integer"])
        worksheet.write_number(row_index, 1, 50.5, formats["number"])
        worksheet.write(row_index, 2, label, formats["text"])

    worksheet.write(74, 0, "Panel (b): native metric-label helper", formats["section"])
    worksheet.write_row(75, 0, ("x", "y", "metric_label"), formats["header"])
    for row_index, (x_value, label) in enumerate(zip((1, 2, 3), ("均值", "P95", "P99")), start=76):
        worksheet.write_number(row_index, 0, x_value, formats["integer"])
        worksheet.write_number(row_index, 1, 7.55, formats["number"])
        worksheet.write(row_index, 2, label, formats["text"])

    return {
        **{f"fps_{key}": value for key, value in fps_ranges.items()},
        **{f"latency_{key}": value for key, value in latency_ranges.items()},
        "fps_summary": (24, 1, 26, 3),
        "annotation": (65, 0, 65, 2),
        "fps_axis_labels": (70, 0, 72, 2),
        "latency_axis_labels": (76, 0, 78, 2),
    }


def chart_base(chart: Any, y_title: str, y_min: float, y_max: float,
               title: str | None, legend: bool = False,
               y_num_format: str = "0",
               plot_layout: dict[str, float] | None = None) -> None:
    if title:
        chart.set_title({
            "name": title,
            "name_font": {
                "name": "Microsoft YaHei", "size": 9,
                "bold": False, "color": "#111827",
            },
        })
    chart.set_y_axis({
        "name": y_title,
        "name_font": {"name": "Microsoft YaHei", "size": 10},
        "num_font": {"name": "Times New Roman", "size": 9},
        "num_format": y_num_format,
        "min": y_min, "max": y_max,
        "major_gridlines": {"visible": True, "line": {"color": "#D8DDE2", "width": 0.75}},
        "line": {"color": "#111827", "width": 1.0},
        "major_tick_mark": "inside",
    })
    chart.set_x_axis({
        "num_font": {"name": "Times New Roman", "size": 9},
        "line": {"color": "#111827", "width": 1.0},
        "major_tick_mark": "inside",
    })
    chart.set_chartarea({"border": {"none": True}, "fill": {"color": "#FFFFFF"}})
    plotarea = {"border": {"none": True}, "fill": {"color": "#FFFFFF"}}
    if plot_layout:
        plotarea["layout"] = plot_layout
    chart.set_plotarea(plotarea)
    if not legend:
        chart.set_legend({"none": True})


def native_axis_caption(caption: str,
                        tick_font_name: str = "Times New Roman",
                        caption_layout: dict[str, float] | None = None) -> dict[str, Any]:
    """Return shared native X-axis title styling for below-panel captions."""
    axis = {
        "name": caption,
        "name_font": {
            "name": "Microsoft YaHei", "size": 9,
            "bold": False, "color": "#111827",
        },
        "num_font": {"name": tick_font_name, "size": 10},
        "line": {"color": "#111827", "width": 1.0},
        "major_tick_mark": "inside",
    }
    if caption_layout:
        axis["name_layout"] = caption_layout
    return axis


def add_native_scatter_axis_labels(chart: Any, source_range: tuple[int, int, int, int],
                                   font_name: str) -> None:
    """Add worksheet-backed text labels to a numeric scatter X-axis."""
    first_row, x_col, last_row, label_col = source_range
    custom_labels = []
    for row in range(first_row, last_row + 1):
        cell = xl_rowcol_to_cell(row, label_col, row_abs=True, col_abs=True)
        custom_labels.append({
            "value": f"=DisplayValues!{cell}",
            "font": {"name": font_name, "size": 10, "color": "#111827"},
        })
    chart.add_series({
        "name": "原生横轴标签",
        "categories": ["DisplayValues", first_row, x_col, last_row, x_col],
        "values": ["DisplayValues", first_row, 1, last_row, 1],
        "line": {"none": True},
        "marker": {"type": "none"},
        "data_labels": {"position": "below", "custom": custom_labels},
    })


def patterned_point(variant: str) -> dict[str, Any]:
    return {
        "pattern": {
            "pattern": PATTERNS[variant],
            "fg_color": EDGES[variant],
            "bg_color": COLORS[variant],
        },
        "line": {"color": EDGES[variant], "width": 1.25},
    }


def build_figure2(rows: list[dict[str, str]], grouped: dict[str, list[dict[str, Any]]],
                  summary: dict[str, Any]) -> None:
    workbook = xlsxwriter.Workbook(FIGURE2_OUTPUT)
    configure_workbook(workbook, "Figure 2 — 三条路径的端到端性能")
    formats = workbook_formats(workbook)
    raw = workbook.add_worksheet("RawRuns")
    display_sheet = workbook.add_worksheet("DisplayValues")
    figure = workbook.add_worksheet("Figure")
    write_raw_runs(raw, rows, formats)
    ranges = write_figure2_display(display_sheet, grouped, summary, formats)

    figure.hide_gridlines(2)
    figure.set_zoom(85)
    figure.set_column("A:A", 2)
    figure.set_column("B:J", 12)

    fps = workbook.add_chart({"type": "column"})
    fps.add_series({
        "name": "FPS",
        "categories": ["DisplayValues", ranges["fps"][0], 0, ranges["fps"][2], 0],
        "values": ["DisplayValues", ranges["fps"][0], 1, ranges["fps"][2], 1],
        "points": [patterned_point(variant) for variant in VARIANTS],
        "y_error_bars": {
            "type": "custom",
            "plus_values": f"=DisplayValues!{xl_range_abs(ranges['fps'][0], 2, ranges['fps'][2], 2)}",
            "minus_values": f"=DisplayValues!{xl_range_abs(ranges['fps'][0], 2, ranges['fps'][2], 2)}",
            "line": {"color": "#111111", "width": 1.0},
            "end_style": 1,
        },
        "data_labels": {
            "value": True, "num_format": "0.000", "position": "outside_end",
            "font": {"name": "Times New Roman", "size": 9},
        },
    })
    chart_base(
        fps, "FPS", 0, 170,
        f'V0→V2R  {summary["publication_display_precision"]["v2r_v0_fps_ratio"]}；'
        f'V2R→V3R  {summary["publication_display_precision"]["v3r_v2r_fps"]}',
        plot_layout={"x": 0.10, "y": 0.16, "width": 0.87, "height": 0.62},
    )
    fps.set_x_axis(native_axis_caption(
        "(a) FPS（均值±样本SD；每路径5进程）", "Times New Roman",
        {"x": 0.34, "y": 0.88},
    ))
    fps.set_style(10)
    fps.set_size({"width": 680, "height": 335})

    mean_latency = workbook.add_chart({"type": "column"})
    mean_latency.add_series({
        "name": "合并样本平均 E2E 延迟",
        "categories": ["DisplayValues", ranges["mean_latency"][0], 0, ranges["mean_latency"][2], 0],
        "values": ["DisplayValues", ranges["mean_latency"][0], 1, ranges["mean_latency"][2], 1],
        "points": [patterned_point(variant) for variant in VARIANTS],
        "data_labels": {
            "value": True, "num_format": "0.000", "position": "outside_end",
            "font": {"name": "Times New Roman", "size": 9},
        },
    })
    chart_base(
        mean_latency, "E2E 延迟 / ms", 0, 27,
        f'V0→V2R  −{summary["publication_display_precision"]["v2r_v0_mean_latency_reduction"]}；'
        f'V2R→V3R  {typographic_sign(summary["publication_display_precision"]["v3r_v2r_mean_latency"])}',
        plot_layout={"x": 0.10, "y": 0.16, "width": 0.87, "height": 0.62},
    )
    mean_latency.set_x_axis(native_axis_caption(
        "(b) 合并样本平均 E2E 延迟（n=5400/路径）",
        caption_layout={"x": 0.33, "y": 0.88},
    ))
    mean_latency.set_style(10)
    mean_latency.set_size({"width": 680, "height": 335})

    tails = workbook.add_chart({"type": "column"})
    for column, variant in enumerate(VARIANTS, start=1):
        tails.add_series({
            "name": variant,
            "categories": ["DisplayValues", ranges["tails"][0], 0, ranges["tails"][2], 0],
            "values": ["DisplayValues", ranges["tails"][0], column, ranges["tails"][2], column],
            **patterned_point(variant),
            "data_labels": {
                "value": True, "num_format": "0.000", "position": "outside_end",
                "font": {"name": "Times New Roman", "size": 8, "rotation": -90},
            },
        })
    chart_base(
        tails, "延迟 / ms", 0, 21, None, legend=True,
        plot_layout={"x": 0.10, "y": 0.06, "width": 0.87, "height": 0.62},
    )
    tails.set_x_axis(native_axis_caption(
        "(c) 合并样本 P95 / P99（n=5400/路径）", "Times New Roman",
        {"x": 0.34, "y": 0.75},
    ))
    tails.set_legend({
        "position": "bottom",
        "font": {"name": "Times New Roman", "size": 9},
    })
    tails.set_style(10)
    tails.set_size({"width": 680, "height": 355})

    figure.insert_chart("B1", fps, {
        "description": "Panel a: V0, V2R, V3R process-level FPS mean with sample SD error bars.",
    })
    figure.insert_chart("B18", mean_latency, {
        "description": "Panel b: pooled mean end-to-end latency for 5400 samples per path.",
    })
    figure.insert_chart("B35", tails, {
        "description": "Panel c: pooled P95 and P99 latency for V0, V2R, and V3R.",
    })
    figure.print_area("A1:J52")
    figure.fit_to_pages(1, 2)
    figure.set_margins(0.25, 0.25, 0.3, 0.3)
    figure.set_landscape()
    workbook.close()


def build_figure3(rows: list[dict[str, str]], grouped: dict[str, list[dict[str, Any]]],
                  summary: dict[str, Any]) -> None:
    workbook = xlsxwriter.Workbook(FIGURE3_OUTPUT)
    configure_workbook(workbook, "Figure 3 — 运行级分布与尾延迟")
    formats = workbook_formats(workbook)
    raw = workbook.add_worksheet("RawRuns")
    display_sheet = workbook.add_worksheet("DisplayValues")
    figure = workbook.add_worksheet("Figure")
    write_raw_runs(raw, rows, formats)
    ranges = write_figure3_display(display_sheet, grouped, summary, formats)

    figure.hide_gridlines(2)
    figure.set_zoom(85)
    figure.set_column("A:A", 2)
    figure.set_column("B:J", 12)

    fps = workbook.add_chart({"type": "scatter", "subtype": "straight_with_markers"})
    for variant in VARIANTS:
        first_row, x_col, last_row, y_col = ranges[f"fps_{variant}"]
        fps.add_series({
            "name": variant,
            "categories": ["DisplayValues", first_row, x_col, last_row, x_col],
            "values": ["DisplayValues", first_row, y_col, last_row, y_col],
            "line": {"none": True},
            "marker": {
                "type": MARKERS[variant], "size": 8,
                "border": {"color": EDGES[variant], "width": 1.25},
                "fill": {"color": COLORS[variant]},
            },
        })
    summary_first, x_col, summary_last, sd_col = ranges["fps_summary"]
    fps.add_series({
        "name": "均值±样本SD",
        "categories": ["DisplayValues", summary_first, x_col, summary_last, x_col],
        "values": ["DisplayValues", summary_first, 2, summary_last, 2],
        "line": {"none": True},
        "marker": {
            "type": "long_dash", "size": 14,
            "border": {"color": "#111111", "width": 1.5},
            "fill": {"color": "#111111"},
        },
        "y_error_bars": {
            "type": "custom",
            "plus_values": f"=DisplayValues!{xl_range_abs(summary_first, sd_col, summary_last, sd_col)}",
            "minus_values": f"=DisplayValues!{xl_range_abs(summary_first, sd_col, summary_last, sd_col)}",
            "line": {"color": "#111111", "width": 1.0},
            "end_style": 1,
        },
    })
    add_native_scatter_axis_labels(fps, ranges["fps_axis_labels"], "Times New Roman")
    chart_base(
        fps, "进程级 FPS", 50, 132,
        None,
        plot_layout={"x": 0.11, "y": 0.05, "width": 0.86, "height": 0.73},
    )
    fps_axis = native_axis_caption(
        "(a) 进程级 FPS（点：独立进程；横线/误差：均值±样本SD）",
        caption_layout={"x": 0.26, "y": 0.88},
    )
    fps_axis.update({
        "min": 0.5, "max": 3.5, "major_unit": 1,
        "num_format": "0",
        "label_position": "none",
    })
    fps.set_x_axis(fps_axis)
    fps.set_style(10)
    fps.set_size({"width": 680, "height": 370})

    latency = workbook.add_chart({"type": "scatter", "subtype": "straight_with_markers"})
    for variant in ("V2R", "V3R"):
        first_row, x_col, last_row, y_col = ranges[f"latency_{variant}"]
        latency.add_series({
            "name": variant,
            "categories": ["DisplayValues", first_row, x_col, last_row, x_col],
            "values": ["DisplayValues", first_row, y_col, last_row, y_col],
            "line": {"none": True},
            "marker": {
                "type": MARKERS[variant], "size": 8,
                "border": {"color": EDGES[variant], "width": 1.25},
                "fill": {"color": COLORS[variant]},
            },
        })
    add_native_scatter_axis_labels(latency, ranges["latency_axis_labels"], "Microsoft YaHei")
    annotation_row, annotation_x_col, _, annotation_text_col = ranges["annotation"]
    latency.add_series({
        "name": "尾延迟说明",
        "categories": ["DisplayValues", annotation_row, annotation_x_col, annotation_row, annotation_x_col],
        "values": ["DisplayValues", annotation_row, 1, annotation_row, 1],
        "line": {"none": True},
        "marker": {"type": "none"},
        "data_labels": {
            "position": "above",
            "custom": [{
                "value": "=DisplayValues!$C$66",
                "font": {"name": "Microsoft YaHei", "size": 10, "color": "#111827"},
                "fill": {"color": "#FAF7EA", "transparency": 5},
                "border": {"color": "#6B7280", "width": 0.75},
            }],
        },
    })
    del annotation_text_col
    chart_base(
        latency, "进程级延迟 / ms", 7.45, 12.05,
        None, legend=True, y_num_format="0.0",
        plot_layout={"x": 0.11, "y": 0.11, "width": 0.86, "height": 0.65},
    )
    latency_axis = native_axis_caption(
        "(b) 进程级延迟比较（独立进程；横向偏移仅用于区分）",
        caption_layout={"x": 0.28, "y": 0.87},
    )
    latency_axis.update({
        "min": 0.5, "max": 3.5, "major_unit": 1,
        "num_format": "0",
        "label_position": "none",
    })
    latency.set_x_axis(latency_axis)
    latency.set_legend({
        "position": "top",
        "font": {"name": "Times New Roman", "size": 9},
        "delete_series": [2, 3],
    })
    latency.set_style(10)
    latency.set_size({"width": 680, "height": 390})

    figure.insert_chart("B1", fps, {
        "description": "Panel a: five independent process-level FPS points per path with mean and sample SD.",
    })
    figure.insert_chart("B20", latency, {
        "description": "Panel b: process-level mean, P95, and P99 latency points for V2R and V3R; pooled tail changes have opposite directions.",
    })
    figure.print_area("A1:J39")
    figure.fit_to_pages(1, 2)
    figure.set_margins(0.25, 0.25, 0.3, 0.3)
    figure.set_landscape()
    workbook.close()


def xml_visible_text(element: ElementTree.Element | None) -> str:
    if element is None:
        return ""
    text_tags = {
        "{http://schemas.openxmlformats.org/drawingml/2006/main}t",
        "{http://schemas.openxmlformats.org/drawingml/2006/chart}v",
    }
    return "".join(node.text or "" for node in element.iter() if node.tag in text_tags)


def validate_workbook(path: Path, expected_chart_count: int,
                      required_chart_tokens: tuple[str, ...],
                      expected_x_axis_captions: tuple[str, ...],
                      expected_y_axis_formats: tuple[str, ...] | None = None,
                      hide_numeric_x_labels: bool = False,
                      required_per_chart_tokens: dict[int, tuple[str, ...]] | None = None) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size < 10_000:
        raise RuntimeError(f"workbook missing or unexpectedly small: {path}")
    if not zipfile.is_zipfile(path):
        raise RuntimeError(f"not a valid XLSX ZIP container: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required_parts = {"[Content_Types].xml", "xl/workbook.xml"}
        if not required_parts.issubset(names):
            raise RuntimeError(f"required XLSX parts missing: {path}")
        chart_parts = sorted(name for name in names if name.startswith("xl/charts/chart") and name.endswith(".xml"))
        worksheet_parts = sorted(name for name in names if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
        media_parts = sorted(name for name in names if name.startswith("xl/media/"))
        if media_parts:
            raise RuntimeError(f"workbook unexpectedly embeds raster/vector media: {path}: {media_parts}")
        if len(chart_parts) != expected_chart_count:
            raise RuntimeError(
                f"STOP_EXCEL_NATIVE_CHART_GENERATION_FAILURE: {path} has "
                f"{len(chart_parts)} charts, expected {expected_chart_count}"
            )
        if len(worksheet_parts) != len(EXPECTED_SHEETS):
            raise RuntimeError(f"unexpected worksheet part count: {path}")
        root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        sheets = tuple(sheet.attrib["name"] for sheet in root.findall("main:sheets/main:sheet", namespace))
        if sheets != EXPECTED_SHEETS:
            raise RuntimeError(f"sheet structure mismatch in {path}: {sheets}")
        drawing_parts = sorted(name for name in names if name.startswith("xl/drawings/drawing") and name.endswith(".xml"))
        if not drawing_parts:
            raise RuntimeError(f"STOP_EXCEL_NATIVE_CHART_GENERATION_FAILURE: no drawing parts in {path}")
        chart_xml = "\n".join(archive.read(name).decode("utf-8") for name in chart_parts)
        if "DisplayValues!" not in chart_xml:
            raise RuntimeError(f"chart series do not reference DisplayValues in {path}")
        missing_tokens = [token for token in required_chart_tokens if token not in chart_xml]
        if missing_tokens:
            raise RuntimeError(f"accepted chart labels missing in {path}: {missing_tokens}")

        chart_namespace = {
            "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        }
        top_titles: list[str] = []
        x_axis_captions: list[str] = []
        y_axis_formats: list[str] = []
        plot_area_lefts: list[float] = []
        plot_area_rights: list[float] = []
        plot_area_bottoms: list[float] = []
        caption_positions: list[dict[str, float]] = []
        caption_clearances: list[float] = []
        for index, (part, expected_caption) in enumerate(
                zip(chart_parts, expected_x_axis_captions)):
            chart_root = ElementTree.fromstring(archive.read(part))
            top_title = xml_visible_text(chart_root.find("./c:chart/c:title", chart_namespace))
            if any(panel in top_title for panel in ("(a)", "(b)", "(c)")):
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_NATIVE_PLACEMENT_FAILURE: top title still contains panel label: {part}"
                )
            top_titles.append(top_title or "NONE")

            plot_layout = chart_root.find(
                "./c:chart/c:plotArea/c:layout/c:manualLayout", chart_namespace
            )
            if plot_layout is None:
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_CLEARANCE_FAILURE: no manual plot layout in {part}"
                )
            plot_y = plot_layout.find("c:y", chart_namespace)
            plot_x = plot_layout.find("c:x", chart_namespace)
            plot_width = plot_layout.find("c:w", chart_namespace)
            plot_height = plot_layout.find("c:h", chart_namespace)
            if any(value is None for value in (plot_x, plot_y, plot_width, plot_height)):
                raise RuntimeError(f"incomplete plot-area layout in {part}")
            plot_left = float(plot_x.attrib["val"])
            plot_right = plot_left + float(plot_width.attrib["val"])
            plot_bottom = float(plot_y.attrib["val"]) + float(plot_height.attrib["val"])
            if plot_left > 0.111 or plot_right < 0.969:
                raise RuntimeError(
                    f"STOP_CHART_CANVAS_TIGHTENING_FAILURE: horizontal plot bounds "
                    f"{plot_left}, {plot_right} in {part}"
                )
            if plot_bottom > 0.79:
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_CLEARANCE_FAILURE: plot bottom {plot_bottom} in {part}"
                )
            plot_area_lefts.append(plot_left)
            plot_area_rights.append(plot_right)
            plot_area_bottoms.append(plot_bottom)

            axes = [
                *chart_root.findall(".//c:catAx", chart_namespace),
                *chart_root.findall(".//c:valAx", chart_namespace),
            ]
            bottom_axes = [
                axis for axis in axes
                if axis.find("c:axPos", chart_namespace) is not None
                and axis.find("c:axPos", chart_namespace).attrib.get("val") == "b"
            ]
            left_axes = [
                axis for axis in axes
                if axis.find("c:axPos", chart_namespace) is not None
                and axis.find("c:axPos", chart_namespace).attrib.get("val") == "l"
            ]
            if len(bottom_axes) != 1 or len(left_axes) != 1:
                raise RuntimeError(f"axis structure mismatch in {part}")
            axis_title = bottom_axes[0].find("c:title", chart_namespace)
            caption = xml_visible_text(axis_title)
            if caption != expected_caption:
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_NATIVE_PLACEMENT_FAILURE: {part}: {caption!r} != {expected_caption!r}"
                )
            x_axis_captions.append(caption)
            caption_layout = axis_title.find(
                "c:layout/c:manualLayout", chart_namespace
            ) if axis_title is not None else None
            if caption_layout is None:
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_SEPARATION_FAILURE: no native caption layout in {part}"
                )
            caption_x = caption_layout.find("c:x", chart_namespace)
            caption_y = caption_layout.find("c:y", chart_namespace)
            if caption_x is None or caption_y is None:
                raise RuntimeError(f"incomplete native caption layout in {part}")
            caption_position = {
                "x": float(caption_x.attrib["val"]),
                "y": float(caption_y.attrib["val"]),
            }
            caption_clearance = caption_position["y"] - plot_bottom
            if caption_clearance < 0.065 or caption_position["y"] > 0.89:
                raise RuntimeError(
                    f"STOP_PANEL_CAPTION_SEPARATION_FAILURE: caption y/clearance "
                    f"{caption_position['y']}, {caption_clearance} in {part}"
                )
            caption_positions.append(caption_position)
            caption_clearances.append(caption_clearance)
            if hide_numeric_x_labels:
                tick_position = bottom_axes[0].find("c:tickLblPos", chart_namespace)
                if tick_position is None or tick_position.attrib.get("val") != "none":
                    raise RuntimeError(f"numeric scatter X-axis labels remain visible in {part}")
            number_format = left_axes[0].find("c:numFmt", chart_namespace)
            y_axis_formats.append(number_format.attrib.get("formatCode", "General") if number_format is not None else "General")

            if required_per_chart_tokens and index in required_per_chart_tokens:
                part_xml = archive.read(part).decode("utf-8")
                missing = [token for token in required_per_chart_tokens[index] if token not in part_xml]
                if missing:
                    raise RuntimeError(
                        f"STOP_FIGURE3_CATEGORY_MAPPING_FAILURE: {part} missing {missing}"
                    )

        if len(expected_x_axis_captions) != len(chart_parts):
            raise RuntimeError("panel-caption validation count mismatch")
        if expected_y_axis_formats and tuple(y_axis_formats) != expected_y_axis_formats:
            raise RuntimeError(
                f"axis number-format mismatch in {path}: {y_axis_formats} != {expected_y_axis_formats}"
            )

        figure_sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet3.xml"))
        figure_cells = figure_sheet.findall(".//main:c", namespace)
        if figure_cells:
            raise RuntimeError(f"Figure worksheet contains non-chart cell content: {path}")
        drawing_xml = "\n".join(archive.read(name).decode("utf-8") for name in drawing_parts)
        graphic_frames = drawing_xml.count("<xdr:graphicFrame")
        if graphic_frames != expected_chart_count:
            raise RuntimeError(f"drawing/chart object count mismatch in {path}: {graphic_frames}")
        drawing_namespace = {
            "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
        }
        drawing_root = ElementTree.fromstring(archive.read(drawing_parts[0]))
        anchors = drawing_root.findall("xdr:twoCellAnchor", drawing_namespace)
        anchor_start_rows = [
            int(anchor.find("xdr:from/xdr:row", drawing_namespace).text)
            for anchor in anchors
        ]
        anchor_end_rows = [
            int(anchor.find("xdr:to/xdr:row", drawing_namespace).text)
            for anchor in anchors
        ]
        inter_panel_row_gaps = [
            anchor_start_rows[index + 1] - anchor_end_rows[index]
            for index in range(len(anchors) - 1)
        ]
        if len(anchors) != expected_chart_count or any(
                gap < 0 or gap > 1 for gap in inter_panel_row_gaps):
            raise RuntimeError(
                f"STOP_EXCESSIVE_SPACING_REMEDIATION_FAILURE: anchor gaps {inter_panel_row_gaps}"
            )
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "sheets": list(sheets),
        "chart_xml_parts": len(chart_parts),
        "worksheet_xml_parts": len(worksheet_parts),
        "drawing_xml_parts": len(drawing_parts),
        "native_chart_objects": graphic_frames,
        "embedded_media_parts": len(media_parts),
        "figure_sheet_cells": len(figure_cells),
        "top_titles": top_titles,
        "x_axis_panel_captions": x_axis_captions,
        "y_axis_number_formats": y_axis_formats,
        "plot_area_left_fractions": plot_area_lefts,
        "plot_area_right_fractions": plot_area_rights,
        "plot_area_bottom_fractions": plot_area_bottoms,
        "caption_positions": caption_positions,
        "caption_clearance_fractions": caption_clearances,
        "anchor_start_rows": anchor_start_rows,
        "anchor_end_rows": anchor_end_rows,
        "inter_panel_row_gaps": inter_panel_row_gaps,
    }


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "previews").mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "reports").mkdir(parents=True, exist_ok=True)
    rows, grouped, summary = load_authorities()
    hashes_before = {str(path): sha256(path) for path in EXPECTED_HASHES}
    build_figure2(rows, grouped, summary)
    build_figure3(rows, grouped, summary)
    hashes_after = {str(path): sha256(path) for path in EXPECTED_HASHES}
    if hashes_after != hashes_before:
        raise RuntimeError("STOP_SCIENTIFIC_NONREGRESSION_FAILURE: frozen source hash changed")
    validation = {
        "scientific_non_regression": "PASS",
        "source_hashes": hashes_after,
        "workbooks": [
            validate_workbook(
                FIGURE2_OUTPUT, 3,
                ("均值±样本SD", "V0→V2R", "V2R→V3R", "P95", "P99", "E2E 延迟 / ms"),
                (
                    "(a) FPS（均值±样本SD；每路径5进程）",
                    "(b) 合并样本平均 E2E 延迟（n=5400/路径）",
                    "(c) 合并样本 P95 / P99（n=5400/路径）",
                ),
            ),
            validate_workbook(
                FIGURE3_OUTPUT, 2,
                ("独立进程", "V2R", "V3R", "P95 +0.15%; P99 −0.12%", "方向相反"),
                (
                    "(a) 进程级 FPS（点：独立进程；横线/误差：均值±样本SD）",
                    "(b) 进程级延迟比较（独立进程；横向偏移仅用于区分）",
                ),
                expected_y_axis_formats=("0", "0.0"),
                hide_numeric_x_labels=True,
                required_per_chart_tokens={
                    0: (
                        "DisplayValues!$C$71", "DisplayValues!$C$72", "DisplayValues!$C$73",
                        "<c:v>V0</c:v>", "<c:v>V2R</c:v>", "<c:v>V3R</c:v>",
                    ),
                    1: (
                        "DisplayValues!$C$77", "DisplayValues!$C$78", "DisplayValues!$C$79",
                        "<c:v>均值</c:v>", "<c:v>P95</c:v>", "<c:v>P99</c:v>",
                    ),
                },
            ),
        ],
    }
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
