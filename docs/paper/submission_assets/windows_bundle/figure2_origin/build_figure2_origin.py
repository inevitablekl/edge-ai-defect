"""Build Figure 2 as native Origin worksheets/plots on Windows.

Run only from a Windows Python environment configured for the installed Origin
version. The script never imports the SVG/PNG reference into the OPJU.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

try:
    import originpro as op
except ImportError as exc:  # Windows dependency, intentionally unavailable on Jetson
    raise SystemExit("Origin's Python package 'originpro' is required on Windows") from exc


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "figure2_data.csv"
DISPLAY_PATH = HERE / "figure2_display_values.json"
SPEC_PATH = HERE / "figure2_origin_spec.json"
OUTPUT_PATH = HERE / "Figure2_E2E_performance.opju"
PREVIEW_PNG = HERE / "Figure2_E2E_performance_preview.png"
PREVIEW_PDF = HERE / "Figure2_E2E_performance_preview.pdf"
VARIANTS = ("V0", "V2R", "V3R")


def load_and_validate() -> tuple[list[dict[str, str]], dict, dict]:
    with DATA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if [row["variant"] for row in rows] != list(VARIANTS):
        raise ValueError("F2 path order must remain V0, V2R, V3R")
    if any(int(row["accepted_independent_processes"]) != 5 for row in rows):
        raise ValueError("F2 requires five independent processes per path")
    if any(int(row["pooled_latency_samples"]) != 5400 for row in rows):
        raise ValueError("F2 requires 5400 pooled latency samples per path")
    for row in rows:
        variant = row["variant"]
        if f'{float(row["mean_fps"]):.3f}' != display["panel_a"]["bar_labels"][variant]:
            raise ValueError(f"F2 FPS display mismatch for {variant}")
        if f'{float(row["pooled_mean_latency_ms"]):.3f}' != display["panel_b"]["bar_labels"][variant]:
            raise ValueError(f"F2 mean-latency display mismatch for {variant}")
    return rows, display, spec


def new_sheet(name: str, columns: list[tuple[str, str, list]]) :
    wks = op.new_sheet("w", lname=name)
    for index, (long_name, units, values) in enumerate(columns):
        wks.from_list(index, values, lname=long_name, units=units)
    return wks


def add_layer(page):
    if not hasattr(page, "add_layer"):
        raise RuntimeError("Installed originpro lacks GPage.add_layer; update Origin/originpro")
    return page.add_layer()


def add_plot(layer, sheet, y_col: int, x_col: int, kinds: tuple[str, ...]):
    errors = []
    for kind in kinds:
        try:
            return layer.add_plot(sheet, y_col, x_col, type=kind)
        except Exception as exc:  # API plot aliases differ among supported Origin releases
            errors.append(f"{kind}: {exc}")
    raise RuntimeError("No supported native plot alias succeeded: " + " | ".join(errors))


def set_plot_style(plot, style: dict, marker: bool = False) -> None:
    """Apply native style properties; fail loudly if the core color cannot be set."""
    plot.color = style["edge"]
    setters = (
        ("set_str", "color", style["edge"]),
        ("set_str", "fillcolor", style["fill"]),
        ("set_str", "pattern", style.get("hatch", "none")),
    )
    failures = []
    for method, prop, value in setters:
        try:
            getattr(plot, method)(prop, value)
        except Exception as exc:
            failures.append(f"{prop}={value}: {exc}")
    if marker:
        marker_codes = {"square": 1, "circle": 3, "triangle_up": 8}
        try:
            plot.set_int("symbol.kind", marker_codes[style["marker"]])
        except Exception as exc:
            failures.append(f"symbol.kind: {exc}")
    if failures:
        print("STYLE_API_WARNING=" + " | ".join(failures), file=sys.stderr)


def set_layer_frame(layer, frame: dict, page: dict) -> None:
    left = 100.0 * frame["left"] / page["width_mm"]
    top = 100.0 * (page["height_mm"] - frame["bottom"] - frame["height"]) / page["height_mm"]
    width = 100.0 * frame["width"] / page["width_mm"]
    height = 100.0 * frame["height"] / page["height_mm"]
    layer.activate()
    op.lt_exec(
        f"layer.left={left:.8f}; layer.top={top:.8f}; "
        f"layer.width={width:.8f}; layer.height={height:.8f};"
    )


def add_native_text(layer, text: str, x: float, y: float):
    label = layer.add_text(text, x=x, y=y)
    has_cjk = any("\u3400" <= character <= "\u9fff" for character in text)
    family = "SimSun" if has_cjk else "Times New Roman"
    failures = []
    try:
        label.set_str("font", family)
    except Exception as exc:
        failures.append(f"font={family}: {exc}")
    try:
        label.set_float("size", 7.5)
    except Exception as exc:
        failures.append(f"size=7.5: {exc}")
    if failures:
        print("TEXT_STYLE_API_WARNING=" + " | ".join(failures), file=sys.stderr)
    return label


def set_axes(layer, x_range: tuple[float, float], y_spec: dict) -> None:
    layer.set_xlim(begin=x_range[0], end=x_range[1], step=1)
    layer.set_ylim(begin=y_spec["range"][0], end=y_spec["range"][1], step=y_spec["major_step"])
    try:
        axis_label = layer.label("yl")
        axis_label.text = y_spec["title"]
        axis_label.set_str("font", "SimSun" if any("\u3400" <= c <= "\u9fff" for c in y_spec["title"]) else "Times New Roman")
        axis_label.set_float("size", 7.5)
    except Exception:
        add_native_text(layer, y_spec["title"], x=x_range[0] - 0.35, y=sum(y_spec["range"]) / 2)
    layer.lt_exec("layer.grid=1;")


def add_category_labels(layer, labels: list[str], y: float) -> None:
    layer.lt_exec("layer.x.showlabels=0;")
    for x, label in enumerate(labels):
        add_native_text(layer, label, x=x, y=y)


def add_annotations(layer, annotations: list[dict], x_range: tuple[float, float], y_range: tuple[float, float]) -> None:
    for item in annotations:
        x = x_range[0] + float(item["x"]) * (x_range[1] - x_range[0])
        y = y_range[0] + float(item["y"]) * (y_range[1] - y_range[0])
        add_native_text(layer, item["text"], x=x, y=y)


def add_point_labels(layer, labels: list[str], xs: list[float], ys: list[float], offset: float) -> None:
    for label, x, y in zip(labels, xs, ys):
        add_native_text(layer, label, x=x, y=y + offset)


def build(rows: list[dict[str, str]], display: dict, spec: dict) -> None:
    op.set_show(True)
    op.new()
    styles = spec["series_style"]
    x = [0.0, 1.0, 2.0]
    fps = [float(row["mean_fps"]) for row in rows]
    fps_sd = [float(row["sample_sd_fps"]) for row in rows]
    mean_latency = [float(row["pooled_mean_latency_ms"]) for row in rows]
    p95 = [float(row["pooled_p95_ms"]) for row in rows]
    p99 = [float(row["pooled_p99_ms"]) for row in rows]

    source = new_sheet("F2_Data", [
        ("Path", "", list(VARIANTS)), ("X", "", x), ("Mean FPS", "FPS", fps),
        ("Sample SD FPS", "FPS", fps_sd), ("Pooled mean latency", "ms", mean_latency),
        ("Pooled P95", "ms", p95), ("Pooled P99", "ms", p99),
        ("Independent processes", "", [5, 5, 5]), ("Pooled samples", "", [5400, 5400, 5400]),
    ])

    page = op.new_graph(template="Origin", lname="Figure2_E2E_performance")
    layers = [page[0], add_layer(page), add_layer(page)]
    page.activate()
    width_units = round(spec["page"]["width_mm"] / 25.4 * 1000)
    height_units = round(spec["page"]["height_mm"] / 25.4 * 1000)
    op.lt_exec(f"page.width={width_units}; page.height={height_units};")

    # Panel (a): native columns plus native Y-error plots.
    layer = layers[0]
    set_layer_frame(layer, spec["layers"][0]["frame_mm"], spec["page"])
    for index, variant in enumerate(VARIANTS):
        sheet = new_sheet(f"F2A_{variant}", [
            ("X", "", [x[index]]), ("Mean FPS", "FPS", [fps[index]]),
            ("Sample SD", "FPS", [fps_sd[index]]),
        ])
        plot = add_plot(layer, sheet, 1, 0, ("column", "bar"))
        set_plot_style(plot, styles[variant])
        try:
            plot.lname = variant
        except Exception:
            pass
        error = add_plot(layer, sheet, 2, 0, ("yError", "yerr", "error"))
        error.color = "#111111"
    a = spec["layers"][0]
    set_axes(layer, tuple(a["x"]["range"]), a["y"])
    add_category_labels(layer, list(VARIANTS), -8.0)
    add_point_labels(layer, [display["panel_a"]["bar_labels"][v] for v in VARIANTS], x, fps, 5.0)
    add_annotations(layer, a["annotations"], tuple(a["x"]["range"]), tuple(a["y"]["range"]))
    layer.lt_exec("legend -d;")

    # Panel (b): pooled mean E2E latency.
    layer = layers[1]
    set_layer_frame(layer, spec["layers"][1]["frame_mm"], spec["page"])
    for index, variant in enumerate(VARIANTS):
        sheet = new_sheet(f"F2B_{variant}", [("X", "", [x[index]]), ("Pooled mean", "ms", [mean_latency[index]])])
        plot = add_plot(layer, sheet, 1, 0, ("column", "bar"))
        set_plot_style(plot, styles[variant])
        try:
            plot.lname = variant
        except Exception:
            pass
    b = spec["layers"][1]
    set_axes(layer, tuple(b["x"]["range"]), b["y"])
    add_category_labels(layer, list(VARIANTS), -1.3)
    add_point_labels(layer, [display["panel_b"]["bar_labels"][v] for v in VARIANTS], x, mean_latency, 0.55)
    add_annotations(layer, b["annotations"], tuple(b["x"]["range"]), tuple(b["y"]["range"]))
    layer.lt_exec("legend -d;")

    # Panel (c): pooled P95/P99, three native series.
    layer = layers[2]
    set_layer_frame(layer, spec["layers"][2]["frame_mm"], spec["page"])
    offsets = (-0.23, 0.0, 0.23)
    for index, variant in enumerate(VARIANTS):
        sheet = new_sheet(f"F2C_{variant}", [
            ("X", "", [offsets[index], 1.0 + offsets[index]]),
            (variant, "ms", [p95[index], p99[index]]),
        ])
        plot = add_plot(layer, sheet, 1, 0, ("column", "bar"))
        set_plot_style(plot, styles[variant])
        try:
            plot.lname = variant
        except Exception:
            pass
    c = spec["layers"][2]
    set_axes(layer, tuple(c["x"]["range"]), c["y"])
    add_category_labels(layer, ["P95", "P99"], -1.0)
    for metric_index, metric in enumerate(("P95", "P99")):
        values = p95 if metric == "P95" else p99
        for variant_index, variant in enumerate(VARIANTS):
            add_native_text(layer, display["panel_c"]["bar_labels"][metric][variant],
                            x=metric_index + offsets[variant_index], y=values[variant_index] + 0.22)
    add_annotations(layer, c["annotations"], tuple(c["x"]["range"]), tuple(c["y"]["range"]))
    layer.lt_exec("legend -r;")

    page.activate()
    op.save(str(OUTPUT_PATH))
    for output, image_type in ((PREVIEW_PNG, "png"), (PREVIEW_PDF, "pdf")):
        try:
            page.save_fig(str(output), type=image_type)
            print(f"PREVIEW={output}")
        except Exception as exc:
            print(f"PREVIEW_EXPORT_WARNING={output}: {exc}", file=sys.stderr)
    page.activate()  # leave final native graph active for Windows-side QA
    print(f"CREATED={OUTPUT_PATH}")
    print("MANUAL_QA_REQUIRED=Compare against figure2_reference.svg/png; verify axes, hatches, legend, fonts, and all native objects.")


if __name__ == "__main__":
    build(*load_and_validate())
