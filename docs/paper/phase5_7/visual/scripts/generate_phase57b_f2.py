#!/usr/bin/env python3
"""Generate the deterministic Phase 5.7B slim Figure 2 asset triplet."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OUTPUT = ROOT / "docs/paper/phase5_7/visual/production/figures"
STEM = "fig2_technical_implementation_phase57b"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, size: int = 28, weight: str = "400",
         anchor: str = "middle", fill: str = "#20252b") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        'font-family="Noto Serif CJK SC,Liberation Serif,serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{esc(value)}</text>'
    )


def multiline(x: int, y: int, values: list[str], size: int = 28,
              weight: str = "400", gap: int = 34) -> str:
    return "\n".join(
        text(x, y + index * gap, value, size=size, weight=weight)
        for index, value in enumerate(values)
    )


def box(x: int, y: int, width: int, height: int, values: list[str],
        fill: str = "#ffffff", size: int = 28, weight: str = "400") -> str:
    gap = 34
    first_y = y + height // 2 - (len(values) - 1) * gap // 2 + 10
    return "\n".join((
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" '
        f'fill="{fill}" stroke="#38434d" stroke-width="3"/>',
        multiline(x + width // 2, first_y, values, size=size, weight=weight, gap=gap),
    ))


def arrow(x1: int, y1: int, x2: int, y2: int, width: int = 4,
          marker: str = "arrow", stroke: str = "#38434d") -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{width}" marker-end="url(#{marker})"/>'
    )


def svg_payload() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="62mm" '
        'viewBox="0 0 1600 620" role="img">',
        '<title>V2R/V3R host-device input path</title>',
        '<defs>',
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
        'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="#38434d"/></marker>',
        '<marker id="stream-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
        'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L12,6 L0,12 z" fill="#315c76"/></marker>',
        '</defs>',
        '<rect width="1600" height="620" fill="#ffffff"/>',
        '<rect x="45" y="45" width="405" height="500" rx="12" fill="#f5f6f7" '
        'stroke="#38434d" stroke-width="3"/>',
        '<rect x="495" y="45" width="1060" height="500" rx="12" fill="#eef4f8" '
        'stroke="#38434d" stroke-width="3"/>',
        text(248, 88, "主机 / CPU", size=31, weight="700"),
        text(1025, 88, "设备 / GPU", size=31, weight="700"),
        '<line x1="473" y1="58" x2="473" y2="532" stroke="#6b7280" '
        'stroke-width="3" stroke-dasharray="10 8"/>',
        box(95, 135, 305, 88, ["Decoded CV_8UC3 BGR"], size=27),
        arrow(248, 223, 248, 268),
        box(95, 278, 305, 120, ["Pageable / pinned", "packed staging", "跨帧复用"],
            fill="#f3e8dc", size=27),
        arrow(400, 338, 590, 338),
        text(500, 447, "cudaMemcpy2DAsync", size=27, weight="700"),
        box(600, 283, 185, 110, ["device raw", "buffer"], size=27),
        arrow(785, 338, 830, 338),
        box(840, 268, 220, 140, ["fused CUDA", "preprocessing"],
            fill="#e6f1e8", size=27, weight="700"),
        arrow(1060, 338, 1105, 338),
        box(1115, 268, 255, 140, ["TensorRT-owned", "FP32 NCHW", "device input"], size=27),
        arrow(1370, 338, 1380, 338),
        '<rect x="1390" y="288" width="145" height="100" rx="10" fill="#e8edf2" '
        'stroke="#38434d" stroke-width="3"/>',
        '<text x="1462" y="348" text-anchor="middle" font-family="Liberation Mono,monospace" '
        'font-size="27" font-weight="700" fill="#20252b">enqueueV3</text>',
        '<path d="M500,145 L1515,145" fill="none" stroke="#315c76" stroke-width="7"/>',
        text(1008, 127, "同一 TensorRT CUDA stream（单帧顺序）", size=28,
             weight="700", fill="#315c76"),
        '<line x1="520" y1="145" x2="520" y2="284" stroke="#315c76" '
        'stroke-width="4" marker-end="url(#stream-arrow)"/>',
        '<line x1="950" y1="145" x2="950" y2="258" stroke="#315c76" '
        'stroke-width="4" marker-end="url(#stream-arrow)"/>',
        '<path d="M1515,145 L1540,145 L1540,338" fill="none" stroke="#315c76" '
        'stroke-width="4" marker-end="url(#stream-arrow)"/>',
        text(800, 505, "V2R / V3R仅主机暂存分配类型不同；无跨帧重叠", size=27,
             weight="700", fill="#4b5563"),
        '</svg>\n',
    ]
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
    with tempfile.TemporaryDirectory(prefix="phase57b-f2-") as temporary:
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
