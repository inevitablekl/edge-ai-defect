#!/usr/bin/env python3
"""Generate the deterministic Phase 3 Figure 1 SVG prototype."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths.svg"


SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1260" viewBox="0 0 1600 1260">
  <title>V0, V2R, and V3R Data Paths with the Common Timing Boundary</title>
  <desc>Deterministic schematic of three frozen serial data paths and one common external timing boundary.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 Z" fill="#334155"/>
    </marker>
    <style>
      .title { font: 700 28px sans-serif; fill: #0f172a; }
      .subtitle { font: 18px sans-serif; fill: #475569; }
      .section { font: 700 18px sans-serif; fill: #0f172a; }
      .variant { font: 700 22px sans-serif; fill: #0f172a; }
      .label { font: 600 15px sans-serif; fill: #334155; }
      .body { font: 16px sans-serif; fill: #1e293b; }
      .small { font: 14px sans-serif; fill: #475569; }
      .boundary { font: 700 15px sans-serif; fill: #7c2d12; }
      .box { stroke: #475569; stroke-width: 2; rx: 14; }
      .shared { fill: #eff6ff; stroke: #2563eb; }
      .v0 { fill: #f8fafc; stroke: #64748b; }
      .v2r { fill: #f0fdf4; stroke: #16a34a; }
      .v3r { fill: #fefce8; stroke: #ca8a04; }
      .common { fill: #f5f3ff; stroke: #7c3aed; }
      .timing { fill: #fff7ed; stroke: #ea580c; }
      .excluded { fill: #f8fafc; stroke: #94a3b8; stroke-dasharray: 7 5; }
      .line { stroke: #334155; stroke-width: 2.5; fill: none; marker-end: url(#arrow); }
      .thin { stroke: #94a3b8; stroke-width: 1.5; fill: none; }
    </style>
  </defs>

  <rect width="1600" height="1260" fill="#ffffff"/>
  <text x="800" y="48" text-anchor="middle" class="title">V0、V2R和V3R数据路径及统一计时边界</text>
  <text x="800" y="78" text-anchor="middle" class="subtitle">V0, V2R, and V3R Data Paths with the Common Timing Boundary</text>

  <rect x="42" y="126" width="300" height="245" class="box shared"/>
  <text x="192" y="158" text-anchor="middle" class="section">Shared deployment object</text>
  <text x="66" y="194" class="body">YOLOv8n frozen model</text>
  <text x="66" y="220" class="body">640 × 640 input · batch 1</text>
  <text x="66" y="246" class="body">NEU-DET replay workload</text>
  <text x="66" y="272" class="body">TensorRT INT8 Engine</text>
  <text x="66" y="298" class="body">output / correctness contract</text>
  <text x="66" y="334" class="small">One frozen object for all three paths</text>

  <rect x="390" y="112" width="470" height="230" class="box v0"/>
  <text x="420" y="148" class="variant">V0</text>
  <text x="420" y="178" class="label">Raw staging / path</text>
  <text x="420" y="202" class="body">Host source / host tensor path</text>
  <text x="420" y="232" class="label">Preprocessing</text>
  <text x="420" y="256" class="body">CPU/OpenCV preprocessing path</text>
  <text x="420" y="286" class="label">Inference input</text>
  <text x="420" y="310" class="body">TensorRT INT8 device input contract</text>
  <text x="420" y="332" class="small">Role: correctness-first baseline</text>

  <rect x="390" y="382" width="470" height="230" class="box v2r"/>
  <text x="420" y="418" class="variant">V2R</text>
  <text x="420" y="448" class="label">Raw staging</text>
  <text x="420" y="472" class="body">pageable host raw staging</text>
  <text x="420" y="502" class="label">Preprocessing</text>
  <text x="420" y="526" class="body">OpenCV 4.5.4-aligned fixed-contract</text>
  <text x="420" y="550" class="body">CUDA preprocessing</text>
  <text x="420" y="580" class="label">Inference input</text>
  <text x="420" y="604" class="body">TensorRT INT8 device input</text>

  <rect x="390" y="652" width="470" height="230" class="box v3r"/>
  <text x="420" y="688" class="variant">V3R</text>
  <text x="420" y="718" class="label">Raw staging</text>
  <text x="420" y="742" class="body">pinned host raw staging</text>
  <text x="420" y="772" class="label">Preprocessing</text>
  <text x="420" y="796" class="body">the same CUDA preprocessing semantics</text>
  <text x="420" y="820" class="body">as V2R</text>
  <text x="420" y="850" class="label">Inference input</text>
  <text x="420" y="874" class="body">TensorRT INT8 device input</text>

  <path d="M342 248 H390" class="line"/>
  <path d="M342 248 C365 248 365 497 390 497" class="line"/>
  <path d="M342 248 C365 248 365 767 390 767" class="line"/>

  <rect x="960" y="112" width="585" height="770" class="box common"/>
  <text x="1252" y="150" text-anchor="middle" class="section">Common downstream path</text>
  <text x="1002" y="205" class="body">TensorRT INT8 execution</text>
  <text x="1002" y="250" class="body">required synchronization</text>
  <text x="1002" y="295" class="body">device-to-host transfer where required</text>
  <text x="1002" y="340" class="body">postprocessing / NMS</text>
  <text x="1002" y="385" class="body">frame-result construction</text>
  <path d="M860 227 H960" class="line"/>
  <path d="M860 497 H960" class="line"/>
  <path d="M860 767 H960" class="line"/>
  <text x="1252" y="454" text-anchor="middle" class="small">Shared engine, workload, output contract,</text>
  <text x="1252" y="478" text-anchor="middle" class="small">and downstream semantics</text>
  <path d="M1002 520 H1504" class="thin"/>
  <text x="1002" y="556" class="label">Variant isolation</text>
  <text x="1002" y="584" class="body">V2R → V3R: host staging memory / allocation type</text>
  <text x="1002" y="612" class="small">CUDA preprocessing semantics remain the same</text>
  <text x="1002" y="660" class="label">Correctness context</text>
  <text x="1002" y="688" class="body">same frame-result contract and lifecycle checks</text>
  <text x="1002" y="716" class="body">for the common serial comparison</text>

  <rect x="42" y="928" width="1503" height="178" class="box timing"/>
  <text x="74" y="966" class="section">Common external timing boundary</text>
  <text x="74" y="1002" class="boundary">START</text>
  <text x="168" y="1002" class="body">immediately before source pull / frame acquisition</text>
  <text x="74" y="1035" class="boundary">INCLUDED</text>
  <text x="168" y="1035" class="body">source pull/decode · variant path · preprocessing · transfer where applicable · TensorRT INT8 · synchronization · postprocessing · frame-result construction</text>
  <text x="74" y="1068" class="boundary">END</text>
  <text x="168" y="1068" class="body">after frame-result construction, immediately before result serialization/write</text>

  <rect x="42" y="1130" width="1503" height="82" class="box excluded"/>
  <text x="74" y="1162" class="label">EXCLUDED FROM THE BOUNDARY</text>
  <text x="74" y="1190" class="body">JSON serialization · file I/O · digest finalization/writing · summary persistence</text>
</svg>
'''


def main() -> None:
    output = Path(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(SVG, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
