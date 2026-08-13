#!/usr/bin/env python3
"""Validate anonymous DOCX privacy, structure, frozen content, and parity."""

from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ASVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
DC = "http://purl.org/dc/elements/1.1/"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
NS = {"w": W, "a": A, "r": R, "asvg": ASVG, "dc": DC, "cp": CP}

T1_TITLE = "表1　"
T2_TITLE = "表2　"
T3_TITLE = "表3　"
T4_TITLE = "表4　"
IDENTITY_TOKENS = (
    "王凯伦",
    "王琦",
    "WANG Kailun",
    "WANG Qi",
    "合肥工业大学数学学院",
    "School of Mathematics, Hefei University of Technology",
)
IDENTITY_LABELS = ("通信作者：", "Corresponding author:", "作者简介")
IDENTITY_PROPERTY_NAMES = (
    "author",
    "affiliation",
    "corresponding",
    "biography",
    "email",
    "contact",
)
REQUIRED_SECTIONS = (
    "0 引言",
    "1 系统对象与问题定义",
    "2 数据路径工程方法",
    "3 实验设计",
    "4 结果与分析",
    "5 结论",
)
FROZEN_VALUES = (
    "2.24×",
    "55.45%",
    "+4.07%",
    "−4.03%",
    "+0.15%",
    "−0.12%",
)
FORBIDDEN_SCIENTIFIC_ADDITIONS = (
    "V4",
    "Attempt 2",
    "cross-stage acceleration multiplication",
    "Gate D",
)


def qn(local: str, namespace: str = W) -> str:
    return f"{{{namespace}}}{local}"


def attr(node: ET.Element | None, local: str, namespace: str = W) -> str | None:
    return node.get(qn(local, namespace)) if node is not None else None


def text_of(node: ET.Element) -> str:
    return "".join(child.text or "" for child in node.findall(".//w:t", NS)).replace("\u00a0", " ").strip()


def paragraph_style(node: ET.Element) -> str:
    return attr(node.find("w:pPr/w:pStyle", NS), "val") or ""


def load_package(path: Path) -> tuple[dict[str, bytes], dict[str, ET.Element], list[str]]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"ZIP CRC failure: {bad}")
        parts = {name: archive.read(name) for name in archive.namelist()}
    parsed: dict[str, ET.Element] = {}
    for name, payload in parts.items():
        if not name.endswith((".xml", ".rels")):
            continue
        try:
            parsed[name] = ET.fromstring(payload)
        except ET.ParseError as exc:
            errors.append(f"XML parse failure in {name}: {exc}")
    return parts, parsed, errors


def body_from(parsed: dict[str, ET.Element]) -> ET.Element:
    document = parsed.get("word/document.xml")
    if document is None:
        raise ValueError("word/document.xml is missing or invalid")
    body = document.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    return body


def all_package_text(parts: dict[str, bytes]) -> dict[str, str]:
    return {
        name: payload.decode("utf-8", errors="replace")
        for name, payload in parts.items()
        if name.endswith((".xml", ".rels")) or name.startswith("docProps/")
    }


def visible_paragraphs(body: ET.Element) -> list[tuple[str, str]]:
    return [(paragraph_style(node), text_of(node)) for node in body.findall("w:p", NS) if text_of(node)]


def table_signature(table: ET.Element) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple(text_of(cell) for cell in row.findall("w:tc", NS))
        for row in table.findall("w:tr", NS)
    )


def reference_paragraphs(body: ET.Element) -> list[str]:
    paragraphs = body.findall("w:p", NS)
    heading = next((i for i, node in enumerate(paragraphs) if text_of(node) == "参考文献"), None)
    if heading is None:
        return []
    return [text_of(node) for node in paragraphs[heading + 1:] if paragraph_style(node) == "Bibliography"]


def identity_paragraph(style: str, text: str) -> bool:
    return (
        style in {
            "HFUTAuthorsCN",
            "HFUTAffiliationCN",
            "HFUTAuthorsEN",
            "HFUTAffiliationEN",
            "HFUTAuthorBiography",
        }
        or text in {"通信作者：王琦", "Corresponding author: WANG Qi"}
    )


def validate_t2_layout(errors: list[str], table: ET.Element) -> None:
    rows = table.findall("w:tr", NS)
    exact_measurement = "60帧预热；每进程1080帧；每路径5个独立进程"
    exact_matches = 0
    table_borders = table.find("w:tblPr/w:tblBorders", NS)
    for edge in ("insideH", "insideV"):
        if attr(table_borders.find(f"w:{edge}", NS) if table_borders is not None else None, "val") != "nil":
            errors.append(f"Table 2 {edge} border is not nil")
    for row_index, row in enumerate(rows):
        for column_index, cell in enumerate(row.findall("w:tc", NS)):
            label = f"Table 2 row {row_index} column {column_index}"
            if text_of(cell) == exact_measurement:
                exact_matches += 1
            borders = cell.find("w:tcPr/w:tcBorders", NS)
            if borders is None:
                errors.append(f"{label} has no direct cell borders")
            else:
                expected_top = ("single", "8") if row_index == 0 else ("nil", None)
                expected_bottom = (
                    ("single", "4") if row_index == 0
                    else (("single", "8") if row_index == len(rows) - 1 else ("nil", None))
                )
                for edge, expected in (("top", expected_top), ("bottom", expected_bottom)):
                    node = borders.find(f"w:{edge}", NS)
                    actual = (attr(node, "val"), attr(node, "sz"))
                    if actual != expected:
                        errors.append(f"{label} {edge} border mismatch: {actual}")
                for edge in ("left", "right"):
                    if attr(borders.find(f"w:{edge}", NS), "val") != "nil":
                        errors.append(f"{label} {edge} border is not nil")
            expected_alignment = "center" if row_index == 0 else "left"
            for paragraph in cell.findall("w:p", NS):
                ppr = paragraph.find("w:pPr", NS)
                if attr(ppr.find("w:pStyle", NS) if ppr is not None else None, "val") != "HFUTTableContent":
                    errors.append(f"{label} paragraph style is not HFUTTableContent")
                indent = ppr.find("w:ind", NS) if ppr is not None else None
                actual_indent = (attr(indent, "left"), attr(indent, "right"), attr(indent, "firstLine"))
                forbidden_indents = ("hanging", "hangingChars", "leftChars", "rightChars", "firstLineChars")
                if actual_indent != ("0", "0", "0") or any(
                    attr(indent, name) is not None for name in forbidden_indents
                ):
                    errors.append(f"{label} paragraph direct indent mismatch: {actual_indent}")
                if ppr is not None and ppr.find("w:tabs", NS) is not None:
                    errors.append(f"{label} paragraph contains unexpected tabs")
                if attr(ppr.find("w:jc", NS) if ppr is not None else None, "val") != expected_alignment:
                    errors.append(f"{label} paragraph alignment is not {expected_alignment}")
    if exact_matches != 1:
        errors.append(f"Table 2 exact single-measurement text count is {exact_matches}, expected 1")


def validate_anonymous(path: Path) -> tuple[bool, list[str], dict[str, object], dict[str, bytes], dict[str, ET.Element]]:
    errors: list[str] = []
    details: dict[str, object] = {}
    if not path.is_file():
        return False, [f"missing DOCX: {path}"], details, {}, {}
    try:
        parts, parsed, package_errors = load_package(path)
    except (OSError, zipfile.BadZipFile) as exc:
        return False, [f"invalid DOCX package: {exc}"], details, {}, {}
    errors.extend(package_errors)
    try:
        body = body_from(parsed)
    except ValueError as exc:
        return False, errors + [str(exc)], details, parts, parsed

    paragraphs = visible_paragraphs(body)
    all_text = "\n".join(text for _, text in paragraphs)
    details["body_paragraphs"] = len(paragraphs)

    for token in IDENTITY_TOKENS + IDENTITY_LABELS:
        if token in all_text:
            errors.append(f"identity token in visible manuscript text: {token}")
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", all_text):
        errors.append("email address in visible manuscript text")

    text_parts = all_package_text(parts)
    filename_hits = [
        f"{name}:{token}"
        for name in parts
        for token in IDENTITY_TOKENS
        if token in name
    ]
    if filename_hits:
        errors.append(f"identity token in DOCX filename/media part: {filename_hits}")
    details["filename_identity_hits"] = filename_hits
    package_hits = [
        f"{name}:{token}"
        for name, payload in text_parts.items()
        for token in IDENTITY_TOKENS + IDENTITY_LABELS
        if token in payload
    ]
    if package_hits:
        errors.append(f"identity token in DOCX package: {package_hits}")
    details["package_identity_hits"] = package_hits

    mailto_hits = [f"{name}:mailto:" for name, payload in text_parts.items() if "mailto:" in payload.lower()]
    email_hits = [
        f"{name}:email"
        for name, payload in text_parts.items()
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", payload)
    ]
    details["email_hits"] = mailto_hits + email_hits
    relationship_hits = [
        f"{name}:{rel.get('Target')}:{token}"
        for name, root in parsed.items()
        if name.endswith(".rels")
        for rel in root
        for token in IDENTITY_TOKENS
        if token in rel.get("Target", "")
    ]
    details["relationship_identity_hits"] = relationship_hits
    if relationship_hits:
        errors.append(f"identity token in relationship target: {relationship_hits}")
    if mailto_hits or email_hits:
        errors.append(f"email/contact material in DOCX package: {mailto_hits + email_hits}")

    custom = parsed.get("docProps/custom.xml")
    custom_property_names: list[str] = []
    if custom is not None:
        custom_property_names = [node.get("name", "") for node in list(custom)]
        identity_properties = [
            name for name in custom_property_names
            if any(token in name.lower() for token in IDENTITY_PROPERTY_NAMES)
        ]
        if identity_properties:
            errors.append(f"identity-bearing custom properties remain: {identity_properties}")
    details["custom_properties"] = custom_property_names or "NONE"

    core = parsed.get("docProps/core.xml")
    creator = "MISSING"
    last_modified_by = "MISSING"
    if core is not None:
        creator_node = core.find("dc:creator", NS)
        last_node = core.find("cp:lastModifiedBy", NS)
        creator = (creator_node.text or "") if creator_node is not None else "MISSING"
        last_modified_by = (last_node.text or "") if last_node is not None else "MISSING"
        if (creator not in {"", "MISSING"}) or (last_modified_by not in {"", "MISSING"}):
            errors.append(
                f"non-neutral core properties: dc:creator={creator!r}; cp:lastModifiedBy={last_modified_by!r}"
            )
    else:
        errors.append("docProps/core.xml is missing")
    details["dc:creator"] = creator
    details["cp:lastModifiedBy"] = last_modified_by

    comments = 0
    tracked_changes = 0
    comment_references = 0
    revision_authors: list[str] = []
    for name, root in parsed.items():
        for node in root.iter():
            local = node.tag.rsplit("}", 1)[-1]
            if local == "comment":
                comments += 1
            if local in {"ins", "del", "moveFrom", "moveTo", "rPrChange", "pPrChange"}:
                tracked_changes += 1
                author = node.get(qn("author"))
                if author:
                    revision_authors.append(f"{name}:{author}")
            if local in {"commentRangeStart", "commentReference", "commentRangeEnd"}:
                comment_references += 1
    details["comments"] = comments
    details["tracked_changes"] = tracked_changes
    details["comment_references"] = comment_references
    details["revision_authors"] = revision_authors
    details["hidden_identity"] = False
    if comments or tracked_changes or comment_references or revision_authors:
        errors.append("comments, tracked changes, or revision authors found")

    required_text = {
        "CN title": "Jetson端工业缺陷检测的输入数据路径重构",
        "EN title": "Input Data-Path Reconstruction for Industrial Defect Detection on Jetson",
        "CN keywords": "Jetson；工业缺陷检测；INT8混合精度推理；CUDA预处理；主机—设备数据路径",
        "EN keywords": "Jetson; industrial defect detection; INT8 mixed-precision inference; CUDA preprocessing; host-device data path",
        "CLC": "TP391.41",
        "CN abstract label": "摘要",
        "EN abstract label": "Abstract",
        "CN keywords label": "关键词",
        "EN keywords label": "Keywords",
        "reference heading": "参考文献",
    }
    for label, value in required_text.items():
        if value not in all_text:
            errors.append(f"missing {label}: {value}")
    for style in ("HFUTAbstractBodyCN", "HFUTAbstractBodyEN"):
        if not any(current_style == style and text for current_style, text in paragraphs):
            errors.append(f"missing non-empty {style}")
    headings = {text for style, text in paragraphs if style.startswith("HFUTHeading")}
    for section in REQUIRED_SECTIONS:
        if section not in headings:
            errors.append(f"missing section heading: {section}")

    document = parsed["word/document.xml"]
    drawings = document.findall(".//w:drawing", NS)
    details["figure_count"] = len(drawings)
    if len(drawings) != 4:
        errors.append(f"expected four figure drawings, found {len(drawings)}")
    body_paragraphs = body.findall("w:p", NS)
    for caption in ("图1　", "图2　", "图3　", "图4　"):
        count = sum(text_of(node).startswith(caption) for node in body_paragraphs)
        if count != 1:
            errors.append(f"missing or duplicated figure caption: {caption}")
    for title, label in ((T1_TITLE, "Table 1"), (T2_TITLE, "Table 2"), (T3_TITLE, "Table 3"), (T4_TITLE, "Table 4")):
        captions = [node for node in body_paragraphs if text_of(node).startswith(title)]
        if len(captions) != 1:
            errors.append(f"{label} caption count is {len(captions)}, expected 1")
            continue
        has_page_break = captions[0].find("w:pPr/w:pageBreakBefore", NS) is not None
        if has_page_break:
            errors.append(f"Anonymous {label} caption has unauthorized pageBreakBefore")

    tables = body.findall("w:tbl", NS)
    details["table_count"] = len(tables)
    if len(tables) != 4:
        errors.append(f"expected four manuscript tables, found {len(tables)}")
    else:
        t1_rows = tables[0].findall("w:tr", NS)
        t2_rows = tables[1].findall("w:tr", NS)
        t3_rows = tables[2].findall("w:tr", NS)
        t4_rows = tables[3].findall("w:tr", NS)
        details["table1_rows"] = len(t1_rows) - 1
        details["table2_rows"] = len(t2_rows) - 1
        details["table3_rows"] = len(t3_rows) - 1
        details["table4_rows"] = len(t4_rows) - 1
        if len(t1_rows) != 11 or any(len(row.findall("w:tc", NS)) != 4 for row in t1_rows):
            errors.append("Table 1 is not 10 data rows by 4 columns")
        if len(t2_rows) != 10 or any(len(row.findall("w:tc", NS)) != 2 for row in t2_rows):
            errors.append("Table 2 is not 9 data rows by 2 columns")
        if len(t3_rows) != 4 or any(len(row.findall("w:tc", NS)) != 5 for row in t3_rows):
            errors.append("Table 3 is not 3 data rows by 5 columns")
        if len(t4_rows) != 7 or any(len(row.findall("w:tc", NS)) != 8 for row in t4_rows):
            errors.append("Table 4 is not 6 works by 7 attributes")
        t1_values = "\n".join(text_of(cell) for row in t1_rows for cell in row.findall("w:tc", NS))
        for value in (
            "Detector / Engine", "CPU像素预处理", "CUDA预处理",
            "打包原始图像暂存", "Pageable", "Pinned", "复用TRT CUDA stream",
        ):
            if value not in t1_values:
                errors.append(f"Table 1 missing controlled-path value: {value}")
        t2_values = "\n".join(text_of(cell) for row in t2_rows for cell in row.findall("w:tc", NS))
        for value in (
            "NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super",
            "L4T R36.5；CUDA 12.6；TensorRT 10.3；OpenCV 4.5.4", "YOLOv8n",
            "TensorRT INT8混合精度（INT8 + FP16 fallback）；host input FP32",
            "1260张去重训练图像；IInt8EntropyCalibrator2；batch 1；排除test split",
            "固定180张test图像", "V0 / V2R / V3R；单帧顺序执行",
            "60帧预热；每进程1080帧；每路径5个独立进程", "关闭diagnostics与profiling",
        ):
            if value not in t2_values:
                errors.append(f"Table 2 missing frozen value: {value}")
        t3_values = "\n".join(text_of(cell) for row in t3_rows for cell in row.findall("w:tc", NS))
        for value in (
            "Precision", "Recall", "mAP50", "mAP50-95", "0.6913", "0.6991",
            "0.6476", "0.3523", "V3R",
        ):
            if value not in t3_values:
                errors.append(f"Table 3 missing frozen value: {value}")
        t4_values = "\n".join(text_of(cell) for row in t4_rows for cell in row.findall("w:tc", NS))
        for value in ("Kim et al. (2025)", "PRESTO (2025)", "Tang & Qian (2024)", "Shin & Kim (2022)", "Bateni et al. (2020)", "本文", "明确否", "未报告"):
            if value not in t4_values:
                errors.append(f"Table 4 missing governed value: {value}")
        validate_t2_layout(errors, tables[1])

    for value in FROZEN_VALUES:
        if value not in all_text:
            errors.append(f"scientific freeze value missing: {value}")
    directionality = {
        "FPS increase": "FPS变化为+4.07%",
        "mean latency decrease": "平均延迟变化为−4.03%",
        "P95 increase": "P95为+0.15%",
        "P99 decrease": "P99为−0.12%",
    }
    compact_text = all_text.replace(" ", "")
    for label, value in directionality.items():
        if value not in all_text and value.replace(" ", "") not in compact_text:
            errors.append(f"frozen directionality missing: {label}")
    if "主要贡献包括两点" not in all_text or "1）" not in all_text or "2）" not in all_text:
        errors.append("contribution count of two is not preserved")
    for value in FORBIDDEN_SCIENTIFIC_ADDITIONS:
        if value in all_text:
            errors.append(f"forbidden scientific restoration/claim present: {value}")

    rels = parsed.get("word/_rels/document.xml.rels")
    if rels is None:
        errors.append("word/_rels/document.xml.rels is missing")
    else:
        image_relationships = {
            rel.get("Id") for rel in rels
            if rel.get("Type", "").endswith("/image")
        }
        used_relationships = {
            node.get(qn("embed", R))
            for node in document.findall(".//a:blip", NS) + document.findall(".//asvg:svgBlip", NS)
        }
        if len(image_relationships & used_relationships) != 4:
            errors.append("four embedded figure image relationships are not all used")

    section_columns = [attr(node, "num") for node in document.findall(".//w:sectPr/w:cols", NS)]
    details["section_columns"] = section_columns
    if "1" not in section_columns or "2" not in section_columns:
        errors.append(f"expected front-matter/body column sections, found {section_columns}")

    details["rendered_references"] = len(reference_paragraphs(body))
    if not reference_paragraphs(body):
        errors.append("no rendered bibliography entries found")
    details["identity_scan"] = (
        "PASS"
        if not filename_hits and not package_hits and not relationship_hits and not mailto_hits and not email_hits
        else "FAIL"
    )
    return not errors, errors, details, parts, parsed


def parity_signature(body: ET.Element) -> list[tuple[object, ...]]:
    signature: list[tuple[object, ...]] = []
    for node in body:
        local = node.tag.rsplit("}", 1)[-1]
        if local == "p":
            style = paragraph_style(node)
            text = text_of(node)
            if text and not identity_paragraph(style, text):
                signature.append(("p", style, text))
        elif local == "tbl":
            signature.append(("tbl", table_signature(node)))
    return signature


def validate_parity(
    full_parts: dict[str, bytes],
    anonymous_parts: dict[str, bytes],
    full_parsed: dict[str, ET.Element],
    anonymous_parsed: dict[str, ET.Element],
) -> tuple[bool, list[str], dict[str, object]]:
    errors: list[str] = []
    details: dict[str, object] = {}
    full_body = body_from(full_parsed)
    anonymous_body = body_from(anonymous_parsed)
    full_identity = [
        (style, text)
        for style, text in visible_paragraphs(full_body)
        if identity_paragraph(style, text)
    ]
    details["full_identity_paragraphs_removed"] = len(full_identity)
    if len(full_identity) != 6:
        errors.append(f"expected six Full body identity-only paragraphs, found {len(full_identity)}")

    if parity_signature(full_body) != parity_signature(anonymous_body):
        errors.append("scientific body paragraph/table sequence differs between Full and Anonymous")

    full_refs = reference_paragraphs(full_body)
    anonymous_refs = reference_paragraphs(anonymous_body)
    details["full_rendered_references"] = len(full_refs)
    details["anonymous_rendered_references"] = len(anonymous_refs)
    if full_refs != anonymous_refs:
        errors.append("rendered reference list differs between Full and Anonymous")

    full_media = {
        name: hashlib.sha256(payload).hexdigest()
        for name, payload in full_parts.items() if name.startswith("word/media/")
    }
    anonymous_media = {
        name: hashlib.sha256(payload).hexdigest()
        for name, payload in anonymous_parts.items() if name.startswith("word/media/")
    }
    if full_media != anonymous_media:
        errors.append("embedded figure media differs between Full and Anonymous")

    full_tables = [table_signature(table) for table in full_body.findall("w:tbl", NS)]
    anonymous_tables = [table_signature(table) for table in anonymous_body.findall("w:tbl", NS)]
    if full_tables != anonymous_tables:
        errors.append("table content differs between Full and Anonymous")
    full_figures = [text_of(node) for node in full_body.findall("w:p", NS) if text_of(node).startswith("图")]
    anonymous_figures = [text_of(node) for node in anonymous_body.findall("w:p", NS) if text_of(node).startswith("图")]
    if full_figures != anonymous_figures:
        errors.append("figure captions differ between Full and Anonymous")
    details["scientific_body_parity"] = "PASS" if not errors else "FAIL"
    return not errors, errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("anonymous_docx", type=Path)
    parser.add_argument("--full", type=Path)
    args = parser.parse_args()

    ok, errors, details, anonymous_parts, anonymous_parsed = validate_anonymous(args.anonymous_docx)
    if args.full is not None:
        try:
            full_parts, full_parsed, full_errors = load_package(args.full)
            errors.extend(full_errors)
            parity_ok, parity_errors, parity_details = validate_parity(
                full_parts, anonymous_parts, full_parsed, anonymous_parsed
            )
            errors.extend(parity_errors)
            ok = ok and parity_ok and not full_errors
            details.update(parity_details)
            details["parity"] = "PASS" if parity_ok else "FAIL"
        except (OSError, zipfile.BadZipFile, ValueError, KeyError) as exc:
            errors.append(f"Full/Anonymous parity inspection failed: {exc}")
            ok = False
    else:
        details["parity"] = "SKIPPED_FULL_ARTIFACT_MISSING"

    for key, value in details.items():
        if key != "body_text":
            print(f"{key}={value}")
    if details.get("identity_scan") == "PASS":
        print("ANONYMITY_SCAN_PASS")
    if details.get("parity") == "PASS":
        print("PARITY_PASS")
    if ok:
        print("verdict=PASS")
        return 0
    print("verdict=FAIL")
    for error in errors:
        print(f"ERROR: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
