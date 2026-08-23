#!/usr/bin/env python3
"""Generate the deterministic Phase 5.9C input data-path model figure."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = ROOT / "docs/paper/phase5_9/visual/production/figures"
STEM = "fig1_input_data_path_model_phase59c"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, *, size: int = 27, weight: str = "400",
         anchor: str = "middle", fill: str = "#20252b") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        'font-family="Noto Serif CJK SC,Liberation Serif,serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(value)}</text>'
    )


def multiline(x: int, y: int, values: list[str], *, size: int = 25,
              weight: str = "400", gap: int = 31, fill: str = "#20252b") -> str:
    return "\n".join(
        text(x, y + index * gap, value, size=size, weight=weight, fill=fill)
        for index, value in enumerate(values)
    )


def box(x: int, y: int, width: int, height: int, values: list[str], *,
        fill: str = "#ffffff", stroke: str = "#38434d", size: int = 25,
        weight: str = "400") -> str:
    gap = 31
    first_y = y + height // 2 - (len(values) - 1) * gap // 2 + 9
    return "\n".join((
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="3"/>',
        multiline(x + width // 2, first_y, values, size=size, weight=weight, gap=gap),
    ))


def arrow(x1: int, y1: int, x2: int, y2: int, *, stroke: str = "#38434d",
          width: int = 4, marker: str = "arrow") -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{width}" marker-end="url(#{marker})"/>'
    )


def svg_payload() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="79mm" '
        'viewBox="0 0 1600 790" role="img">',
        '<title>输入数据路径抽象及层级受控比较</title>',
        '<defs>',
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
        'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="#38434d"/></marker>',
        '<marker id="blue-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
        'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="#315c76"/></marker>',
        '</defs>',
        '<rect width="1600" height="790" fill="#ffffff"/>',
        '<rect x="170" y="78" width="585" height="540" rx="12" fill="#f5f6f7" stroke="#38434d" stroke-width="3"/>',
        '<rect x="845" y="78" width="585" height="540" rx="12" fill="#eef4f8" stroke="#38434d" stroke-width="3"/>',
        text(462, 116, "主机域", size=30, weight="700"),
        text(1137, 116, "设备域", size=30, weight="700"),
        '<line x1="800" y1="82" x2="800" y2="614" stroke="#6b7280" stroke-width="3" stroke-dasharray="10 8"/>',
        text(800, 70, "主机—设备边界", size=23, fill="#5f6973"),
    ]

    rows = (
        ("P₀ / V0", 160, "#e4e7ea", ["CPU输入形成", "FP32 NCHW"], "R = FP32 NCHW", ["TensorRT输入", "F = 主机"], "M = 无"),
        ("P₂ / V2R", 315, "#d8eaf5", ["Pageable暂存", "packed BGR uint8"], "R = packed BGR uint8", ["GPU融合输入形成", "F = 设备"], "M = Pageable"),
        ("P₃ / V3R", 470, "#f4dfcb", ["Pinned暂存", "packed BGR uint8"], "R = packed BGR uint8", ["GPU融合输入形成", "F = 设备"], "M = Pinned"),
    )
    for label, y, fill, host_values, representation, device_values, staging in rows:
        parts.extend((
            box(28, y + 10, 118, 92, [label], fill=fill, size=25, weight="700"),
            box(220, y, 450, 112, host_values, fill=fill, size=25, weight="700"),
            text(445, y + 139, staging, size=23, fill="#4b5563"),
            arrow(670, y + 56, 885, y + 56),
            text(777, y + 38, representation, size=22, weight="700", fill="#315c76"),
            box(900, y, 430, 112, device_values, fill="#ffffff", size=25, weight="700"),
            box(1345, y + 10, 225, 92, ["E = 单帧顺序"], fill="#faf7ea", size=22),
        ))

    parts.extend((
        '<path d="M88,272 L88,320" fill="none" stroke="#315c76" stroke-width="5" marker-end="url(#blue-arrow)"/>',
        box(170, 638, 585, 100, ["P₀ → P₂：路径级重构", "改变 R、F、M；E 保持不变"], fill="#e8f1f7", stroke="#315c76", size=24, weight="700"),
        '<path d="M88,427 L88,475" fill="none" stroke="#8a5a35" stroke-width="5" marker-end="url(#arrow)"/>',
        box(845, 638, 585, 100, ["P₂ → P₃：暂存策略级细化", "仅改变 M：Pageable → Pinned"], fill="#f8eadf", stroke="#8a5a35", size=24, weight="700"),
        text(800, 774, "干预层级表示结构变量范围，不表示收益大小或组件级因果关系", size=22, fill="#5f6973"),
        '</svg>\n',
    ))
    return "\n".join(parts)


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


def convert(svg: Path, pdf: Path, png: Path, grayscale: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="phase59c-f1-") as temporary:
        work = Path(temporary)
        source = work / svg.name
        shutil.copyfile(svg, source)
        profile = work / "lo-profile"
        subprocess.run(
            ["libreoffice", f"-env:UserInstallation=file://{profile}", "--headless",
             "--convert-to", "pdf", "--outdir", str(work), str(source)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        shutil.copyfile(work / f"{svg.stem}.pdf", pdf)
    normalize_pdf(pdf)
    subprocess.run(
        ["pdftocairo", "-png", "-singlefile", "-r", "300", str(pdf), str(png.with_suffix(""))],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    with Image.open(png) as image:
        image.convert("L").save(grayscale, optimize=False, compress_level=9)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    svg = args.output_dir / f"{STEM}.svg"
    pdf = args.output_dir / f"{STEM}.pdf"
    png = args.output_dir / f"{STEM}.png"
    grayscale = args.output_dir / f"{STEM}_grayscale.png"
    svg.write_text(svg_payload(), encoding="utf-8", newline="\n")
    convert(svg, pdf, png, grayscale)
    for path in (svg, pdf, png, grayscale):
        print(f"GENERATED={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
