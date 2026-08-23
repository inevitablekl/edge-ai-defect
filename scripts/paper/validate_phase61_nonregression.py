#!/usr/bin/env python3
"""Validate Paper Phase 6.1 scientific and Figure 1 layout non-regression."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
SECTIONS = ROOT / "docs/paper/manuscript/sections"
FIGURE1_SVG = (
    ROOT
    / "docs/paper/phase5_9/visual/production/figures/fig1_input_data_path_model_phase59c.svg"
)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W, "wp": WP}

EXPERIMENT_SHA256 = "20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa"
FROZEN_FIGURE_HASHES = {
    "docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png": (
        "dfa125e8d20c28c93cb8a210417d72103988057cfd2bca371f2bd1c17a802ea9"
    ),
    "docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png": (
        "c30ee465b6707064819504994c569d48a01067602b19c5a4c79b4b90fe296e96"
    ),
}

REQUIRED_SOURCE_TOKENS = {
    "research_configuration": (
        "YOLOv8n、640×640输入、batch size 1",
        "TensorRT INT8混合精度（INT8 + FP16 fallback）；Engine输入张量：FP32",
        "NEU-DET split-v2的180幅测试图像",
    ),
    "path_semantics": (
        "P=(R,F,M,E)",
        "R\)表示跨越主机—设备边界的数据表示",
        "F\)表示TensorRT输入张量的形成位置",
        "M\)表示额外打包原始图像的主机暂存策略",
        "E\)表示执行拓扑",
        "R,F,M\)发生变化而\(E\)保持不变",
        "R,F,E\)保持不变时只改变\(M",
    ),
    "protocol": (
        "60帧预热",
        "每进程1080帧",
        "每路径5个独立进程",
        "5400个逐帧延迟样本",
        "16200个样本",
        "路径间不构造运行配对",
        "所有统计均为描述性结果",
    ),
    "correctness": (
        "0.6913 / 0.6991 / 0.6476 / 0.3523",
        "类别级最大AP50与Recall路径间差异均为0",
        "任务级指标一致",
    ),
    "performance": (
        "54.600",
        "122.122",
        "127.097",
        "18.273 ms",
        "8.140 ms",
        "7.812 ms",
        "2.236671×",
        "2.24×",
        "55.4519%",
        "55.45%",
        "4.0738%",
        "+4.07%",
        "4.0349%",
        "−4.03%",
        "+0.1514%",
        "+0.15%",
        "−0.1184%",
        "−0.12%",
    ),
    "equation_and_rq_semantics": (
        "B(P)=H_R(P)W_R(P)C_R(P)s_R(P)",
        "T_{\\mathrm{E2E}}(P)=t_{\\mathrm{pre\\text{-}sink}}(P)-t_{\\mathrm{source}}(P)",
        "f_i=N/T_i",
        "RQ1，在固定推理对象、工作负载和任务语义时",
        "RQ2，在\(R,F,E\)、GPU预处理语义及下游结构保持不变时",
    ),
    "boundaries": (
        "不是延迟预测模型",
        "不用于分解各变量的延迟贡献",
        "不是实测总线或DRAM流量、带宽、H2D时间或传输加速比",
        "未形成一致的尾延迟改善证据",
        "不支持“pinned改善稳定性”",
        "不支持统计显著性推断",
        "未覆盖真实相机、跨平台、跨模型或跨数据集泛化",
    ),
}

FIGURE1_REQUIRED = (
    "主机—设备边界",
    "P₀ / V0",
    "P₂ / V2R",
    "P₃ / V3R",
    "R = FP32 NCHW",
    "R = packed BGR uint8",
    "F = 主机",
    "F = 设备",
    "M = 无",
    "M = Pageable",
    "M = Pinned",
    "E = 单帧顺序",
    "P₀ → P₂：路径级重构",
    "P₂ → P₃：暂存策略级细化",
    "干预层级表示结构变量范围，不表示收益大小或组件级因果关系",
)

OVERCLAIM_TERMS = (
    "bandwidth reduction",
    "bandwidth speedup",
    "transfer speedup",
    "bottleneck migration",
    "component contribution",
    "pinned improves stability",
    "statistically significant",
    "generalizes across platforms",
    "generalizes across models",
    "带宽",
    "传输加速",
    "瓶颈",
    "组件",
    "pinned改善稳定性",
    "统计显著",
    "跨平台",
    "跨模型",
)

BOUNDARY_CUES = (
    "不是",
    "不表示",
    "不预设",
    "不能",
    "不支持",
    "不进行",
    "不作",
    "未测量",
    "未覆盖",
    "不推出",
)

FIGURE1_CAPTION = (
    "图1　输入数据路径抽象及层级受控比较。"
    "图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()


def section_property(paragraph: ET.Element, local: str, attribute: str) -> str | None:
    node = paragraph.find(f"w:pPr/w:sectPr/w:{local}", NS)
    return None if node is None else node.get(qn(W, attribute))


def validate_source() -> tuple[list[str], list[dict[str, object]], dict[str, object]]:
    errors: list[str] = []
    matches: list[dict[str, object]] = []
    paths = sorted(SECTIONS.glob("*.md"))
    payloads = {path: path.read_text(encoding="utf-8") for path in paths}
    source = "\n".join(payloads.values())
    visible = source.replace("`", "")

    for group, tokens in REQUIRED_SOURCE_TOKENS.items():
        for token in tokens:
            if token not in visible:
                errors.append(f"{group}: missing frozen token: {token}")

    if visible.count("0.6913 / 0.6991 / 0.6476 / 0.3523") != 3:
        errors.append("correctness table must contain exactly three identical metric rows")
    if sha256(SECTIONS / "04_experiment.md") != EXPERIMENT_SHA256:
        errors.append("Section 3 experiment source changed from the frozen Phase 6.1 baseline")
    for relative, expected in FROZEN_FIGURE_HASHES.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            errors.append(f"frozen Figure 2/3 asset changed: {relative}")

    display_equations = re.findall(r"\\\[(.*?)\\\]", source, re.S)
    if len(display_equations) != 3:
        errors.append(f"display equation inventory changed: {len(display_equations)}")
    if len(re.findall(r"RQ1[，：]", source)) != 1 or len(re.findall(r"RQ2[，：]", source)) != 1:
        errors.append("formal RQ inventory changed")

    for path, payload in payloads.items():
        for line_number, line in enumerate(payload.splitlines(), start=1):
            lowered = line.lower()
            for term in OVERCLAIM_TERMS:
                if term.lower() not in lowered:
                    continue
                classification = (
                    "LEGITIMATE_NEGATION_OR_BOUNDARY"
                    if any(cue in line for cue in BOUNDARY_CUES)
                    else "VIOLATION"
                )
                matches.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "line": line_number,
                        "term": term,
                        "classification": classification,
                        "text": line,
                    }
                )
                if classification == "VIOLATION":
                    errors.append(f"unbounded overclaim match: {path.name}:{line_number}: {term}")

    figure_svg = FIGURE1_SVG.read_text(encoding="utf-8")
    for token in FIGURE1_REQUIRED:
        if token not in figure_svg:
            errors.append(f"Figure 1 semantic token missing: {token}")
    floating_line = "固定推理对象：同一检测器 / Engine / 工作负载 / 后处理语义"
    if floating_line in figure_svg:
        errors.append("Figure 1 retains the prohibited floating fixed-object sentence")

    details = {
        "experiment_source_sha256": sha256(SECTIONS / "04_experiment.md"),
        "figure2_figure3_hashes": {
            relative: sha256(ROOT / relative) for relative in FROZEN_FIGURE_HASHES
        },
        "display_equations": len(display_equations),
        "formal_rqs": {
            "RQ1": len(re.findall(r"RQ1[，：]", source)),
            "RQ2": len(re.findall(r"RQ2[，：]", source)),
        },
        "correctness_metric_rows": visible.count("0.6913 / 0.6991 / 0.6476 / 0.3523"),
    }
    return errors, matches, details


def validate_docx(path: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            return [f"{path.name}: ZIP CRC failure: {bad}"], {}
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        return [f"{path.name}: document body missing"], {}

    children = list(body)
    captions = [
        node
        for node in children
        if node.tag == qn(W, "p") and paragraph_text(node) == FIGURE1_CAPTION
    ]
    if len(captions) != 1:
        return [f"{path.name}: expected one Figure 1 caption, found {len(captions)}"], {}
    caption = captions[0]
    index = children.index(caption)
    if index < 2:
        return [f"{path.name}: Figure 1 drawing/callout structure missing"], {}
    drawing = children[index - 1]
    callout = children[index - 2]
    if drawing.find(".//w:drawing", NS) is None:
        errors.append(f"{path.name}: Figure 1 drawing is not immediately before caption")

    callout_columns = section_property(callout, "cols", "num")
    callout_type = section_property(callout, "type", "val")
    caption_columns = section_property(caption, "cols", "num")
    caption_type = section_property(caption, "type", "val")
    if (callout_columns, callout_type) != ("2", "continuous"):
        errors.append(
            f"{path.name}: pre-Figure 1 section is not two-column continuous: "
            f"{callout_columns}/{callout_type}"
        )
    if (caption_columns, caption_type) != ("1", "nextPage"):
        errors.append(
            f"{path.name}: Figure 1 section is not one-column next-page: "
            f"{caption_columns}/{caption_type}"
        )

    extent = drawing.find(".//wp:extent", NS)
    width_emu = None if extent is None else extent.get("cx")
    if width_emu is None or abs(int(width_emu) - 5_760_000) > 2:
        errors.append(f"{path.name}: Figure 1 width is not 16 cm: {width_emu}")

    details = {
        "figure1_callout_section": {
            "columns": callout_columns,
            "type": callout_type,
        },
        "figure1_section": {
            "columns": caption_columns,
            "type": caption_type,
            "width_emu": width_emu,
        },
        "drawing_count": len(root.findall(".//w:drawing", NS)),
        "table_count": len(root.findall(".//w:tbl", NS)),
        "display_equation_count": len(root.findall(".//m:oMathPara", {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"})),
    }
    return errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-docx", required=True, type=Path)
    parser.add_argument("--anonymous-docx", required=True, type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    errors, overclaim_matches, source_details = validate_source()
    docx_details: dict[str, object] = {}
    for path in (args.full_docx, args.anonymous_docx):
        docx_errors, details = validate_docx(path)
        errors.extend(docx_errors)
        docx_details[str(path)] = details

    report = {
        "phase": "PAPER_PHASE_6_1",
        "verdict": "PASS" if not errors else "FAIL",
        "scientific_nonregression": "PASS" if not errors else "FAIL",
        "source_details": source_details,
        "docx_details": docx_details,
        "overclaim_matches": overclaim_matches,
        "errors": errors,
    }
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"PHASE61_NONREGRESSION_REPORT={args.output_json}")

    print(f"PHASE61_SCIENTIFIC_NONREGRESSION={report['scientific_nonregression']}")
    print(f"OVERCLAIM_MATCHES={len(overclaim_matches)}")
    for match in overclaim_matches:
        print(
            "OVERCLAIM_AUDIT="
            f"{match['classification']} {match['file']}:{match['line']} term={match['term']}"
        )
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
