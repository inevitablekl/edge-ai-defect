#!/usr/bin/env python3
"""Generate deterministic Phase 5.6D-A structural candidate figures.

The SVG payloads are emitted with Python's standard library only. LibreOffice
is used only as the repository-available SVG-to-PDF compatibility converter;
volatile PDF metadata is normalized before the PDF is rasterized with
pdftocairo. These files are candidate previews, never manuscript authority.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = ROOT / "docs/paper/phase5_6/visual/candidates"

COLORS = {
    "ink": "#20252b",
    "muted": "#5f6973",
    "line": "#38434d",
    "host": "#f5f6f7",
    "device": "#eef4f8",
    "v0": "#d9dde1",
    "v2": "#cfe5f3",
    "v3": "#f6dcc6",
    "white": "#ffffff",
    "callout": "#faf7ea",
    "candidate": "#7f1d1d",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text(x: float, y: float, value: str, *, size: int = 28,
         weight: str = "400", anchor: str = "middle",
         family: str = "Noto Serif CJK SC, Liberation Serif, serif",
         fill: str = COLORS["ink"], extra: str = "") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" {extra}>{esc(value)}</text>'
    )


def multiline(x: float, y: float, lines: list[str], *, size: int = 26,
              gap: int = 32, weight: str = "400", anchor: str = "middle",
              family: str = "Noto Serif CJK SC, Liberation Serif, serif",
              fill: str = COLORS["ink"]) -> str:
    spans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else gap
        spans.append(f'<tspan x="{x}" dy="{dy}">{esc(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}">' + "".join(spans) + "</text>"
    )


def box(x: float, y: float, w: float, h: float, lines: list[str], *,
        fill: str = COLORS["white"], stroke: str = COLORS["line"],
        dash: str = "", size: int = 25, weight: str = "400",
        radius: int = 10, code: bool = False) -> str:
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    family = (
        "Liberation Mono, monospace"
        if code else "Noto Serif CJK SC, Liberation Serif, serif"
    )
    first_y = y + h / 2 - (len(lines) - 1) * 15 + 9
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="3" {dash_attr}/>'
        + multiline(x + w / 2, first_y, lines, size=size, gap=30,
                    weight=weight, family=family)
    )


def arrow(x1: float, y1: float, x2: float, y2: float, *,
          stroke: str = COLORS["line"], width: int = 4,
          dash: str = "", marker: bool = True) -> str:
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    marker_attr = 'marker-end="url(#arrow)"' if marker else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{width}" {dash_attr} {marker_attr}/>'
    )


def svg_document(width: int, height: int, body: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img">
  <title>Phase 5.6D-A candidate specification preview</title>
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6"
            orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L12,6 L0,12 z" fill="{COLORS['line']}"/>
    </marker>
    <pattern id="hatch-v2" width="12" height="12" patternUnits="userSpaceOnUse"
             patternTransform="rotate(45)">
      <rect width="12" height="12" fill="{COLORS['v2']}"/>
      <line x1="0" y1="0" x2="0" y2="12" stroke="#7ca9c5" stroke-width="2"/>
    </pattern>
    <pattern id="hatch-v3" width="12" height="12" patternUnits="userSpaceOnUse"
             patternTransform="rotate(-45)">
      <rect width="12" height="12" fill="{COLORS['v3']}"/>
      <line x1="0" y1="0" x2="0" y2="12" stroke="#c58c60" stroke-width="2"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" fill="white"/>
  {body}
</svg>
'''


def candidate_mark(width: int) -> str:
    return (
        f'<rect x="{width - 365}" y="18" width="335" height="44" rx="7" '
        f'fill="none" stroke="{COLORS["candidate"]}" stroke-width="3"/>'
        + text(width - 197, 49, "CANDIDATE / SPECIFICATION", size=23,
               weight="700", fill=COLORS["candidate"])
    )


def figure1() -> str:
    w, h = 1600, 930
    b: list[str] = [candidate_mark(w)]
    b += [
        text(55, 52, "受控输入数据路径工程总览", size=34, weight="700", anchor="start"),
        '<rect x="55" y="82" width="710" height="515" rx="12" '
        f'fill="{COLORS["host"]}" stroke="{COLORS["line"]}" stroke-width="3"/>',
        '<rect x="805" y="82" width="740" height="515" rx="12" '
        f'fill="{COLORS["device"]}" stroke="{COLORS["line"]}" stroke-width="3"/>',
        text(410, 122, "主机 / CPU", size=30, weight="700"),
        text(1175, 122, "设备 / GPU", size=30, weight="700"),
        arrow(785, 95, 785, 580, stroke=COLORS["muted"], width=3, dash="10 8", marker=False),
        text(785, 75, "memory domain boundary", size=20, fill=COLORS["muted"]),
    ]

    # V0 lane.
    b += [
        box(78, 160, 88, 82, ["V0"], fill=COLORS["v0"], weight="700", size=30),
        box(190, 160, 155, 82, ["Decoded", "BGR"], size=24),
        arrow(345, 201, 375, 201),
        box(380, 150, 175, 102, ["CPU/OpenCV", "预处理"], size=24),
        arrow(555, 201, 585, 201),
        box(590, 150, 165, 102, ["FP32 NCHW", "host tensor"], fill=COLORS["v0"], size=23),
        arrow(755, 201, 840, 201),
        text(797, 185, "FP32 H2D", size=20, fill=COLORS["muted"]),
        box(850, 150, 190, 102, ["TensorRT-owned", "device input"], size=22),
        arrow(1040, 201, 1080, 201),
        box(1085, 150, 430, 102, ["TensorRT INT8", "混合精度 Engine（同一）"], size=24, weight="700"),
    ]

    # V2R/V3R host branches and H2D.
    b += [
        box(78, 326, 88, 82, ["V2R"], fill="url(#hatch-v2)", weight="700", size=28),
        box(78, 456, 88, 82, ["V3R"], fill="url(#hatch-v3)", weight="700", size=28),
        box(190, 326, 155, 82, ["Decoded", "BGR"], size=24),
        box(190, 456, 155, 82, ["Decoded", "BGR"], size=24),
        arrow(345, 367, 375, 367), arrow(345, 497, 375, 497),
        box(380, 316, 250, 102, ["Pageable", "raw-image staging"], fill="url(#hatch-v2)", size=23),
        box(380, 446, 250, 102, ["Pinned", "raw-image staging"], fill="url(#hatch-v3)", size=23),
        arrow(630, 367, 840, 367), arrow(630, 497, 840, 497),
        text(735, 349, "raw-image H2D", size=20, fill=COLORS["muted"]),
        text(735, 479, "raw-image H2D", size=20, fill=COLORS["muted"]),
        box(850, 326, 155, 82, ["device raw", "buffer"], size=22),
        box(850, 456, 155, 82, ["device raw", "buffer"], size=22),
        arrow(1005, 367, 1060, 419), arrow(1005, 497, 1060, 445),
        box(1065, 381, 205, 102, ["融合 CUDA", "预处理"], fill="#e6f1e8", size=24, weight="700"),
        arrow(1270, 432, 1300, 432),
        box(1305, 381, 215, 102, ["TensorRT-owned", "FP32 NCHW input"], size=22),
        arrow(1412, 381, 1412, 260),
        text(1295, 560, "V2R / V3R：后半路径相同", size=24, weight="700"),
        arrow(1055, 565, 1515, 565, width=3, marker=False),
    ]

    # Footer: separate observation and payload regions.
    b += [
        '<rect x="55" y="625" width="1490" height="270" rx="14" '
        f'fill="{COLORS["callout"]}" stroke="{COLORS["line"]}" stroke-width="3"/>',
        text(80, 666, "完整路径 E2E 观察（非组件因果测量）", size=28, weight="700", anchor="start"),
        '<line x1="1015" y1="646" x2="1015" y2="875" '
        f'stroke="{COLORS["muted"]}" stroke-width="2"/>',
        box(90, 700, 395, 145, ["V0 → V2R", "2.24× FPS", "平均延迟降低 55.45%"],
            fill=COLORS["white"], size=25, weight="700"),
        box(535, 700, 395, 145, ["V2R → V3R", "+4.07% FPS", "平均延迟降低 4.03%"],
            fill=COLORS["white"], size=25, weight="700"),
        text(510, 872, "P95 / P99 变化均 <0.2%，且方向相反", size=23, fill=COLORS["muted"]),
        text(1045, 690, "名义输入复制载荷", size=27, weight="700", anchor="start"),
        text(1045, 735, "V0：4.915 MB/frame", size=24, anchor="start"),
        text(1045, 773, "V2R/V3R：0.120 MB/frame", size=24, anchor="start"),
        text(1045, 811, "名义尺寸比：40.96×", size=24, weight="700", anchor="start"),
        text(1045, 852, "名义值；非实测总线流量", size=22, fill=COLORS["muted"], anchor="start"),
    ]
    return svg_document(w, h, "\n".join(b))


def figure2() -> str:
    w, h = 1600, 820
    b: list[str] = [candidate_mark(w)]
    b += [
        text(55, 52, "GPU 路径实现与内存域", size=34, weight="700", anchor="start"),
        '<rect x="55" y="85" width="470" height="650" rx="12" '
        f'fill="{COLORS["host"]}" stroke="{COLORS["line"]}" stroke-width="3"/>',
        '<rect x="565" y="85" width="980" height="650" rx="12" '
        f'fill="{COLORS["device"]}" stroke="{COLORS["line"]}" stroke-width="3"/>',
        text(290, 126, "主机 / CPU", size=30, weight="700"),
        text(1055, 126, "设备 / GPU", size=30, weight="700"),
        arrow(545, 100, 545, 720, stroke=COLORS["muted"], width=3, dash="10 8", marker=False),
    ]

    # Main execution chain.
    b += [
        box(90, 170, 360, 88, ["Decoded CV_8UC3 BGR"], size=25),
        arrow(270, 258, 270, 292),
        box(90, 300, 360, 108, ["Pageable / pinned", "packed staging"], fill="#f3e8dc", size=25),
        arrow(450, 354, 625, 354),
        box(420, 265, 345, 52, ["cudaMemcpy2DAsync"], fill=COLORS["white"],
            size=24, code=True, radius=7),
        box(635, 300, 205, 108, ["persistent", "device raw buffer"], size=22),
        arrow(840, 354, 880, 354),
        box(890, 290, 220, 128, ["fused CUDA", "preprocessing", "kernel"],
            fill="#e6f1e8", size=21, code=True),
        arrow(1110, 354, 1150, 354),
        box(1160, 288, 330, 132, ["TensorRT-owned", "FP32 NCHW device input", "persistent / reused"], size=22),
        arrow(1325, 420, 1325, 465),
        box(1160, 475, 330, 92, ["enqueueV3"], fill="#e8edf2", size=26, code=True, weight="700"),
        arrow(1160, 521, 1105, 521),
        box(855, 475, 240, 92, ["device output", "buffer"], size=22),
        arrow(855, 521, 650, 521),
        text(752, 503, "output D2H", size=20, fill=COLORS["muted"]),
        box(90, 475, 360, 112, ["CPU decode / confidence", "filtering / NMS"], size=24),
        arrow(650, 521, 450, 531),
    ]

    # Same-stream rail and lifecycle notes.
    b += [
        '<path d="M610,250 L1475,250" fill="none" '
        f'stroke="#416b85" stroke-width="7"/>',
        arrow(735, 250, 735, 292, stroke="#416b85", width=4),
        arrow(1000, 250, 1000, 292, stroke="#416b85", width=4),
        arrow(1325, 250, 1325, 278, stroke="#416b85", width=4),
        text(1040, 225, "同一 TensorRT CUDA stream（单帧顺序）", size=25, weight="700", fill="#315c76"),
        '<rect x="90" y="625" width="470" height="85" rx="10" '
        f'fill="{COLORS["white"]}" stroke="{COLORS["line"]}" stroke-width="2" stroke-dasharray="8 6"/>',
        multiline(325, 657, ["staging：帧循环前分配，跨帧复用", "V2R/V3R 仅 allocation type 不同"], size=21, gap=29),
        '<rect x="600" y="625" width="500" height="85" rx="10" '
        f'fill="{COLORS["white"]}" stroke="{COLORS["line"]}" stroke-width="2" stroke-dasharray="8 6"/>',
        multiline(850, 657, ["device raw 与 TensorRT input 持久化", "backend owns / reuses input buffer"], size=21, gap=29),
        '<rect x="1140" y="625" width="350" height="85" rx="10" '
        f'fill="{COLORS["callout"]}" stroke="{COLORS["line"]}" stroke-width="2"/>',
        multiline(1315, 657, ["single-stream, single-frame", "无 cross-frame overlap"], size=21, gap=29, weight="700"),
        text(55, 790, "NO PERFORMANCE NUMBERS", size=22, weight="700", anchor="start", fill=COLORS["candidate"]),
    ]
    return svg_document(w, h, "\n".join(b))


def normalize_pdf(path: Path) -> None:
    payload = path.read_bytes()
    payload = re.sub(
        rb"/CreationDate\(D:\d{14}[+-]\d{2}'\d{2}'\)",
        b"/CreationDate(D:20000101000000+00'00')",
        payload,
    )
    payload = re.sub(rb"(?<=<)[0-9A-F]{32}(?=>)", b"0" * 32, payload)
    payload = re.sub(rb"(?<=/DocChecksum /)[0-9A-F]{32}", b"0" * 32, payload)
    path.write_bytes(payload)


def convert_svg(svg: Path, pdf: Path, png: Path) -> None:
    if shutil.which("libreoffice") is None or shutil.which("pdftocairo") is None:
        raise RuntimeError("libreoffice and pdftocairo are required")
    with tempfile.TemporaryDirectory(prefix="phase56d-svg-") as tmp:
        work = Path(tmp)
        source = work / svg.name
        shutil.copyfile(svg, source)
        profile = work / "lo-profile"
        subprocess.run(
            ["libreoffice", f"-env:UserInstallation=file://{profile}",
             "--headless", "--convert-to", "pdf", "--outdir", str(work), str(source)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        shutil.copyfile(work / f"{svg.stem}.pdf", pdf)
    normalize_pdf(pdf)
    subprocess.run(
        ["pdftocairo", "-png", "-singlefile", "-r", "300", str(pdf), str(png.with_suffix(""))],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures = {
        "fig1_hero_data_path_phase56_candidate": figure1(),
        "fig2_technical_implementation_phase56_candidate": figure2(),
    }
    for stem, payload in figures.items():
        svg = args.output_dir / f"{stem}.svg"
        pdf = args.output_dir / f"{stem}.pdf"
        png = args.output_dir / f"{stem}.png"
        svg.write_text(payload, encoding="utf-8", newline="\n")
        convert_svg(svg, pdf, png)
        print(f"GENERATED {svg.relative_to(ROOT)}")
        print(f"GENERATED {pdf.relative_to(ROOT)}")
        print(f"GENERATED {png.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
