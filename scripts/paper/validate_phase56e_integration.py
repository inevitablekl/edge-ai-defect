#!/usr/bin/env python3
"""Validate the Phase 5.6G remediation and manuscript-freeze-candidate contract."""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs/paper/manuscript"
SECTIONS = tuple(sorted((MANUSCRIPT / "sections").glob("*.md")))
CAPTIONS = ROOT / "docs/paper/phase5_6/visual/production/phase56_figure_table_captions.md"
F4_SVG = ROOT / "docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.svg"
T4_EVIDENCE = ROOT / "docs/paper/phase5_6/visual/phase56_related_work_attribute_evidence.csv"
TITLE_CN = "面向Jetson端TensorRT INT8工业缺陷检测的输入数据路径重构"
TITLE_EN = "Input Data-Path Reconstruction for TensorRT INT8 Industrial Defect Detection on Jetson"
OLD_TITLE_CN = "Jetson端工业缺陷检测的INT8输入数据路径重构"
OLD_TITLE_EN = "INT8 Input Data-Path Reconstruction for Jetson-Based Industrial Defect Detection"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}

OLD_VISIBLE_TEXT = (
    "V0、V2R和V3R数据路径示意",
    "端到端执行概念组成与受控干预范围",
    "V0、V2R和V3R平均帧率比较",
    "V0、V2R和V3R平均及尾延迟比较",
    "V0与V2R任务级正确性验证结果",
    "运行级稳定性与尾延迟",
    "仍缺少足够明确的受控工程证据",
    "L4T 36.4.3",
    OLD_TITLE_CN,
    OLD_TITLE_EN,
)
GOVERNANCE_TERMS = (
    "authority",
    "artifact",
    "manuscript-visible",
    "Level-A",
    "Level-B",
    "tail verdict",
    "MIXED",
)
PLAIN_ASYNC_TERMS = (
    "异步H2D",
    "异步二维H2D",
    "二维异步H2D",
    "异步主机到设备",
    "异步二维主机到设备",
    "asynchronous H2D",
    "asynchronous transfer path",
    "asynchronous two-dimensional host-to-device copying",
)
RUNTIME_OVERREACH = (
    "no throttling",
    "fixed clocks",
    "stable frequency",
    "stable thermal state",
    "无降频",
    "固定时钟",
    "稳定频率",
    "稳定热状态",
)
REQUIRED_RESULTS = (
    "2.24×",
    "55.45%",
    "+4.07%",
    "−4.03%",
    "+0.15%",
    "−0.12%",
    "54.600",
    "122.122",
    "127.097",
    "18.273",
    "8.140",
    "7.812",
    "4.9152",
    "0.1200",
    "0.6913",
    "0.6991",
    "0.6476",
    "0.3523",
)


def paragraph_text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).replace("\u00a0", " ").strip()


def contains_forbidden(text: str, value: str) -> bool:
    if value == "MIXED":
        return re.search(r"(?<![A-Za-z])MIXED(?![A-Za-z])", text) is not None
    return value.casefold() in text.casefold()


def load_docx(path: Path) -> tuple[ET.Element, list[str], list[str]]:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        root = ET.fromstring(archive.read("word/document.xml"))
        media = [name for name in archive.namelist() if name.startswith("word/media/")]
    paragraphs = [paragraph_text(node) for node in root.findall(".//w:body/w:p", NS)]
    return root, paragraphs, media


def validate_source(errors: list[str]) -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SECTIONS)
    visible_source = source.replace("`", "")
    publication_text = "\n".join((
        visible_source,
        CAPTIONS.read_text(encoding="utf-8").replace("`", ""),
        F4_SVG.read_text(encoding="utf-8"),
    ))

    for value in OLD_VISIBLE_TEXT:
        if value in publication_text:
            errors.append(f"stale active-manuscript text remains: {value}")
    if source.count(TITLE_CN) != 1 or source.count(TITLE_EN) != 1:
        errors.append("final Chinese/English title contract failed")
    for value in GOVERNANCE_TERMS + PLAIN_ASYNC_TERMS:
        if contains_forbidden(publication_text, value):
            errors.append(f"publication-facing forbidden wording remains: {value}")
    if "cudaMemcpy2DAsync" not in publication_text:
        errors.append("factual cudaMemcpy2DAsync API token is missing")
    if "4.4 运行级分布与尾延迟" not in source:
        errors.append("Section 4.4 title is not the frozen final title")
    if source.count("主要贡献包括两点") != 1 or "3）" in source:
        errors.append("contribution inventory is not exactly two")
    contribution2 = (
        "2）在统一的任务正确性、E2E延迟、进程级FPS与合并样本P95/P99评价口径下，"
        "通过V0→V2R和V2R→V3R两级受控比较，区分完整输入路径重构的主要性能收益与"
        "pinned暂存的有限平均增量，并利用5次独立进程考察运行级分布和尾延迟行为。"
    )
    if contribution2 not in source or "2）建立统一" in source:
        errors.append("Contribution 2 controlled-evidence wording contract failed")
    rq2 = (
        "RQ2：在GPU预处理、CUDA stream和下游拓扑保持不变时，将pageable原始图像暂存"
        "替换为pinned暂存，是否进一步改善平均性能，以及P95/P99是否呈现一致的尾延迟改善？"
    )
    if rq2 not in source or "稳定的平均性能" in source:
        errors.append("RQ2 neutral wording contract failed")
    criteria = (
        "边缘部署指在嵌入式或边缘设备上实际部署并报告实验结果",
        "模型固定指所比较系统配置中的研究变量不包含检测网络结构、权重或模型参数变化",
        "GPU预处理指论文明确由GPU/CUDA执行模型推理前的图像预处理",
        "host内存策略指论文明确研究或配置主机侧内存分配",
        "完整E2E指性能边界至少覆盖预处理、模型执行以及后处理或结果处理",
        "任务正确性指论文报告受比较部署或系统配置对应的任务级检测正确性指标",
        "尾延迟指论文报告P95、P99或其他明确的百分位尾延迟指标",
    )
    if not all(value in source for value in criteria):
        errors.append("Table 4 seven-criterion definition is incomplete")
    with T4_EVIDENCE.open(encoding="utf-8", newline="") as handle:
        related = list(csv.DictReader(handle))
    allowed = {"YES", "NO_IF_EXPLICIT", "NOT_REPORTED", "NOT_APPLICABLE"}
    if len(related) != 42 or {row["classification"] for row in related} - allowed:
        errors.append("Table 4 evidence is not 42 cells with allowed vocabulary only")
    presto_e2e = [row for row in related if row["work"] == "PRESTO (2025)" and row["attribute"] == "Complete E2E evaluation"]
    if len(presto_e2e) != 1 or presto_e2e[0]["classification"] != "NOT_REPORTED":
        errors.append("PRESTO complete-E2E conservative downgrade is missing")

    figure_captions = re.findall(r"^\*\*图([1-4])　", source, re.M)
    table_captions = re.findall(r"^\*\*表([1-4])　", source, re.M)
    if figure_captions != ["1", "2", "3", "4"]:
        errors.append(f"figure-caption inventory mismatch: {figure_captions}")
    if table_captions != ["1", "2", "3", "4"]:
        errors.append(f"table-caption inventory mismatch: {table_captions}")

    equations = re.findall(r"\\\[(.*?)\\\]", source, re.S)
    equation_contract = (
        "T_{\\mathrm{E2E}}",
        "f_i=",
        "\\mu_f=",
        "h=1+(n-1)p",
        "Q_p=",
    )
    if len(equations) != 5 or any(token not in equations[index] for index, token in enumerate(equation_contract)):
        errors.append("five-equation inventory/order contract failed")

    for value in REQUIRED_RESULTS:
        if value not in visible_source:
            errors.append(f"frozen result missing: {value}")
    if "名义输入复制载荷比为40.96×" not in visible_source:
        errors.append("40.96× is not explicitly governed as nominal input-copy payload")
    if "TensorRT INT8混合精度Engine" not in visible_source:
        errors.append("TensorRT INT8 mixed-precision wording is missing")
    if "两项相对变化均低于0.2%且方向相反，未形成一致的尾延迟改善证据" not in visible_source:
        errors.append("publication tail direction-opposite wording is missing")
    for value in (
        "强制cache miss",
        "生成并归档cache",
        "未将既有cache复用为正式构建输入",
        "MAXN_SUPER",
        "nvpmodel mode 2",
        "未调用jetson_clocks",
        "时钟频率没有独立归档",
        "非连续的前后观察",
    ):
        if value not in visible_source:
            errors.append(f"frozen calibration/runtime qualifier missing: {value}")
    for value in ("calibration cache used", "pre-existing cache reused") + RUNTIME_OVERREACH:
        if value.casefold() in visible_source.casefold():
            errors.append(f"ambiguous or overreaching runtime wording present: {value}")


def validate_docx(path: Path, errors: list[str]) -> tuple[list[str], list[tuple[tuple[str, ...], ...]]]:
    root, paragraphs, media = load_docx(path)
    text = "\n".join(paragraphs)
    figures = root.findall(".//w:drawing", NS)
    tables = root.findall(".//w:body/w:tbl", NS)
    equations = root.findall(".//m:oMathPara", NS)
    if (len(figures), len(tables), len(equations)) != (4, 4, 5):
        errors.append(
            f"{path.name}: inventory is figures={len(figures)} tables={len(tables)} equations={len(equations)}"
        )
    payloads = [Path(name).suffix.lower() for name in media]
    if payloads != [".png"] * 4:
        errors.append(f"{path.name}: DOCX figure payloads are not four PNG fallbacks: {payloads}")
    for prefix in ("图1　", "图2　", "图3　", "图4　", "表1　", "表2　", "表3　", "表4　"):
        if sum(value.startswith(prefix) for value in paragraphs) != 1:
            errors.append(f"{path.name}: caption count mismatch for {prefix.strip()}")
    for value in OLD_VISIBLE_TEXT:
        if value in text:
            errors.append(f"{path.name}: stale rendered text remains: {value}")
    if text.count(TITLE_CN) != 1 or text.count(TITLE_EN) != 1:
        errors.append(f"{path.name}: final title count mismatch")
    for value in GOVERNANCE_TERMS + PLAIN_ASYNC_TERMS:
        if contains_forbidden(text, value):
            errors.append(f"{path.name}: publication-facing forbidden wording remains: {value}")
    if "L4T R36.5" not in text or "L4T 36.4.3" in text:
        errors.append(f"{path.name}: Table 2 L4T R36.5 regression")
    if "V3R" not in "\n".join(paragraph_text(cell) for cell in tables[2].findall(".//w:tc", NS)):
        errors.append(f"{path.name}: V3R is absent from Table 3")
    t4_rows = tables[3].findall("w:tr", NS) if len(tables) == 4 else []
    if len(t4_rows) != 7 or any(len(row.findall("w:tc", NS)) != 8 for row in t4_rows):
        errors.append(f"{path.name}: Table 4 is not 6 works by 7 attributes")
    elif t4_rows:
        allowed_display = {"是", "明确否", "未报告", "不适用"}
        data_values = [paragraph_text(cell) for row in t4_rows[1:] for cell in row.findall("w:tc", NS)[1:]]
        if len(data_values) != 42 or set(data_values) - allowed_display:
            errors.append(f"{path.name}: Table 4 contains invalid display vocabulary")
        presto_values = [paragraph_text(cell) for cell in t4_rows[2].findall("w:tc", NS)]
        if len(presto_values) != 8 or presto_values[5] != "未报告":
            errors.append(f"{path.name}: PRESTO complete-E2E cell is not 未报告")
    signatures = [
        tuple(tuple(paragraph_text(cell) for cell in row.findall("w:tc", NS)) for row in table.findall("w:tr", NS))
        for table in tables
    ]
    return paragraphs, signatures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--compare-full", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    validate_source(errors)
    paragraphs, tables = validate_docx(args.docx, errors)
    if args.compare_full:
        full_paragraphs, full_tables = validate_docx(args.compare_full, errors)
        if tables != full_tables:
            errors.append("Full/Anonymous table parity failed")
        identity = (
            "王凯伦", "王琦", "WANG Kailun", "WANG Qi",
            "合肥工业大学数学学院", "School of Mathematics, Hefei University of Technology",
        )
        scientific_full = [value for value in full_paragraphs if value and not any(token in value for token in identity)]
        if [value for value in paragraphs if value] != scientific_full:
            errors.append("Full/Anonymous visible scientific paragraph parity failed")

    if errors:
        print("verdict=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE56G_FREEZE_CANDIDATE_VALIDATION=PASS")
    print("figures=4 tables=4 display_equations=5 contributions=2")
    print("table2_l4t=R36.5 stale_l4t_36.4.3=NO table3_v3r=YES table4=6x7")
    print("publication_tail=OPPOSITE_DIRECTION_NO_CONSISTENT_IMPROVEMENT nominal_payload_ratio=40.96x docx_payloads=PNG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
