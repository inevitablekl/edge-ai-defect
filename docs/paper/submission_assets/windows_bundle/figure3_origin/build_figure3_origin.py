"""Build Figure 3 as native Origin worksheets/plots on Windows.

Run only with Windows Python plus the `originpro` package supplied for the
installed Origin release. Reference SVG/PNG files are never imported.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

try:
    import originpro as op
except ImportError as exc:
    raise SystemExit("Origin's Python package 'originpro' is required on Windows") from exc


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "figure3_data.csv"
DISPLAY_PATH = HERE / "figure3_display_values.json"
SPEC_PATH = HERE / "figure3_origin_spec.json"
OUTPUT_PATH = HERE / "Figure3_run_level_distribution.opju"
PREVIEW_PNG = HERE / "Figure3_run_level_distribution_preview.png"
PREVIEW_PDF = HERE / "Figure3_run_level_distribution_preview.pdf"
VARIANTS = ("V0", "V2R", "V3R")
JITTER = (-0.12, -0.06, 0.0, 0.06, 0.12)


def load_and_validate() -> tuple[list[dict[str, str]], dict, dict]:
    with DATA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if len(rows) != 15 or sorted(int(row["execution_order"]) for row in rows) != list(range(1, 16)):
        raise ValueError("F3 requires the exact 15 process rows and execution orders 1..15")
    grouped = {variant: [row for row in rows if row["variant"] == variant] for variant in VARIANTS}
    if any(len(grouped[variant]) != 5 for variant in VARIANTS):
        raise ValueError("F3 requires five independent processes per path")
    if any(row["accepted"] != "true" or row["independence_semantics"] != "independent_process" for row in rows):
        raise ValueError("F3 contains a rejected or non-independent row")
    for variant in VARIANTS:
        fps = [float(row["fps"]) for row in grouped[variant]]
        if not math.isclose(statistics.mean(fps), display["panel_a"]["mean_fps"][variant], rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"F3 FPS mean mismatch for {variant}")
        if not math.isclose(statistics.stdev(fps), display["panel_a"]["sample_sd_fps"][variant], rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"F3 sample-SD mismatch for {variant}")
    if display["panel_b"]["annotation_line_1"] != "P95 +0.15%; P99 −0.12%" or display["panel_b"]["annotation_line_2"] != "方向相反":
        raise ValueError("F3 frozen tail annotation changed")
    return rows, display, spec


def new_sheet(name: str, columns: list[tuple[str, str, list]]):
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
        except Exception as exc:
            errors.append(f"{kind}: {exc}")
    raise RuntimeError("No supported native plot alias succeeded: " + " | ".join(errors))


def set_plot_style(plot, style: dict) -> None:
    plot.color = style["edge"]
    marker_codes = {"square": 1, "circle": 3, "triangle_up": 8}
    failures = []
    for method, prop, value in (
        ("set_str", "color", style["edge"]),
        ("set_str", "fillcolor", style["fill"]),
        ("set_int", "symbol.kind", marker_codes[style["marker"]]),
        ("set_float", "symbol.size", 4.5),
    ):
        try:
            getattr(plot, method)(prop, value)
        except Exception as exc:
            failures.append(f"{prop}={value}: {exc}")
    if failures:
        print("STYLE_API_WARNING=" + " | ".join(failures), file=sys.stderr)


def set_layer_frame(layer, frame: dict, page: dict) -> None:
    left = 100.0 * frame["left"] / page["width_mm"]
    top = 100.0 * (page["height_mm"] - frame["bottom"] - frame["height"]) / page["height_mm"]
    width = 100.0 * frame["width"] / page["width_mm"]
    height = 100.0 * frame["height"] / page["height_mm"]
    layer.activate()
    op.lt_exec(f"layer.left={left:.8f}; layer.top={top:.8f}; layer.width={width:.8f}; layer.height={height:.8f};")


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
    layer.lt_exec("layer.grid=1; layer.x.showlabels=0;")


def add_category_labels(layer, labels: list[str], y: float) -> None:
    for x, label in enumerate(labels):
        add_native_text(layer, label, x=x, y=y)


def add_fraction_text(layer, text: str, x_fraction: float, y_fraction: float,
                      x_range: tuple[float, float], y_range: tuple[float, float]) -> None:
    x = x_range[0] + x_fraction * (x_range[1] - x_range[0])
    y = y_range[0] + y_fraction * (y_range[1] - y_range[0])
    add_native_text(layer, text, x=x, y=y)


def build(rows: list[dict[str, str]], display: dict, spec: dict) -> None:
    op.set_show(True)
    op.new()
    grouped = {variant: [row for row in rows if row["variant"] == variant] for variant in VARIANTS}

    # Complete native source worksheet, in the frozen execution order.
    ordered = sorted(rows, key=lambda row: int(row["execution_order"]))
    new_sheet("F3_Run_Level_Data", [
        ("Variant", "", [row["variant"] for row in ordered]),
        ("Run ID", "", [row["run_id"] for row in ordered]),
        ("Execution order", "", [int(row["execution_order"]) for row in ordered]),
        ("FPS", "FPS", [float(row["fps"]) for row in ordered]),
        ("Mean latency", "ms", [float(row["mean_latency_ms"]) for row in ordered]),
        ("Process P95", "ms", [float(row["process_p95_ms"]) for row in ordered]),
        ("Process P99", "ms", [float(row["process_p99_ms"]) for row in ordered]),
        ("Measured frames", "", [int(row["measured_frames"]) for row in ordered]),
        ("Accepted", "", [row["accepted"] for row in ordered]),
        ("Independence semantics", "", [row["independence_semantics"] for row in ordered]),
        ("Evidence source path", "", [row["source_path"] for row in ordered]),
        ("Evidence source SHA256", "", [row["source_sha256"] for row in ordered]),
    ])

    page = op.new_graph(template="Origin", lname="Figure3_run_level_distribution")
    layers = [page[0], add_layer(page)]
    page.activate()
    width_units = round(spec["page"]["width_mm"] / 25.4 * 1000)
    height_units = round(spec["page"]["height_mm"] / 25.4 * 1000)
    op.lt_exec(f"page.width={width_units}; page.height={height_units};")

    # Panel (a): five process points per path, plus mean and sample-SD summary.
    layer = layers[0]
    a = spec["layers"][0]
    set_layer_frame(layer, a["frame_mm"], spec["page"])
    for base, variant in enumerate(VARIANTS):
        fps = [float(row["fps"]) for row in grouped[variant]]
        point_sheet = new_sheet(f"F3A_{variant}_Points", [
            ("Jittered X", "", [base + jitter for jitter in JITTER]),
            ("Process FPS", "FPS", fps),
        ])
        plot = add_plot(layer, point_sheet, 1, 0, ("scatter", "s"))
        set_plot_style(plot, spec["series_style"][variant])

        mean = display["panel_a"]["mean_fps"][variant]
        sample_sd = display["panel_a"]["sample_sd_fps"][variant]
        summary_sheet = new_sheet(f"F3A_{variant}_Summary", [
            ("Path center", "", [base]), ("Mean FPS", "FPS", [mean]), ("Sample SD", "FPS", [sample_sd]),
        ])
        mean_plot = add_plot(layer, summary_sheet, 1, 0, ("scatter", "s"))
        mean_plot.color = "#111111"
        try:
            mean_plot.set_int("symbol.kind", 11)  # horizontal-line marker in Origin
            mean_plot.set_float("symbol.size", 15)
        except Exception as exc:
            print(f"MEAN_MARKER_API_WARNING={variant}: {exc}", file=sys.stderr)
        error_plot = add_plot(layer, summary_sheet, 2, 0, ("yError", "yerr", "error"))
        error_plot.color = "#111111"
    set_axes(layer, tuple(a["x"]["range"]), a["y"])
    add_category_labels(layer, list(VARIANTS), 46.5)
    add_fraction_text(layer, "点：独立进程\n横线/误差：均值±样本SD", 0.02, 0.70,
                      tuple(a["x"]["range"]), tuple(a["y"]["range"]))
    add_fraction_text(layer, "(a)", 0.5, -0.24, tuple(a["x"]["range"]), tuple(a["y"]["range"]))
    layer.lt_exec("legend -d;")

    # Panel (b): V2R/V3R process-level mean, P95, and P99 points.
    layer = layers[1]
    b = spec["layers"][1]
    set_layer_frame(layer, b["frame_mm"], spec["page"])
    columns = ("mean_latency_ms", "process_p95_ms", "process_p99_ms")
    for variant, shift in (("V2R", -0.16), ("V3R", 0.16)):
        xs: list[float] = []
        ys: list[float] = []
        for metric_index, column in enumerate(columns):
            xs.extend(metric_index + shift + jitter * 0.55 for jitter in JITTER)
            ys.extend(float(row[column]) for row in grouped[variant])
        point_sheet = new_sheet(f"F3B_{variant}_Points", [
            ("Jittered metric X", "", xs), (variant, "ms", ys),
        ])
        plot = add_plot(layer, point_sheet, 1, 0, ("scatter", "s"))
        set_plot_style(plot, spec["series_style"][variant])
        try:
            plot.lname = variant
        except Exception:
            pass
    set_axes(layer, tuple(b["x"]["range"]), b["y"])
    add_category_labels(layer, ["均值", "P95", "P99"], 7.28)
    add_fraction_text(layer, "P95 +0.15%; P99 −0.12%\n方向相反", 0.5, 0.04,
                      tuple(b["x"]["range"]), tuple(b["y"]["range"]))
    add_fraction_text(layer, "(b)", 0.5, -0.24, tuple(b["x"]["range"]), tuple(b["y"]["range"]))
    layer.lt_exec("legend -r;")

    page.activate()
    op.save(str(OUTPUT_PATH))
    for output, image_type in ((PREVIEW_PNG, "png"), (PREVIEW_PDF, "pdf")):
        try:
            page.save_fig(str(output), type=image_type)
            print(f"PREVIEW={output}")
        except Exception as exc:
            print(f"PREVIEW_EXPORT_WARNING={output}: {exc}", file=sys.stderr)
    page.activate()
    print(f"CREATED={OUTPUT_PATH}")
    print("MANUAL_QA_REQUIRED=Compare against figure3_reference.svg/png; verify point order, summary marks, annotation, fonts, and all native objects.")


if __name__ == "__main__":
    build(*load_and_validate())
