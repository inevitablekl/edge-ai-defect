#!/usr/bin/env python3
"""Validate every actual manuscript heading and the reopened HFUT reference heading."""

from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

ROOT = Path(__file__).resolve().parents[2]

HEADINGS = (
    ("docs/paper/manuscript/sections/01_introduction.md", "Introduction", "0  引  言", "0", "引  言", "HFUTIntroHeading", "黑体", "14", "TRUE", "TRUE", "HFUT_FMT_DOC P012"),
    ("docs/paper/manuscript/sections/02_problem_definition.md", "H1", "1  输入数据路径模型与问题表述", "1", "输入数据路径模型与问题表述", "HFUTHeading1", "黑体", "14", "TRUE", "FALSE", "HFUT_FMT_DOC P015"),
    ("docs/paper/manuscript/sections/02_problem_definition.md", "H2", "1.1  固定推理对象与系统边界", "1.1", "固定推理对象与系统边界", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/02_problem_definition.md", "H2", "1.2  路径描述符与名义复制载荷", "1.2", "路径描述符与名义复制载荷", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/02_problem_definition.md", "H2", "1.3  层级受控比较、正确性条件与评价问题", "1.3", "层级受控比较、正确性条件与评价问题", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/03_method.md", "H1", "2  受控输入数据路径重构", "2", "受控输入数据路径重构", "HFUTHeading1", "黑体", "14", "TRUE", "FALSE", "HFUT_FMT_DOC P015"),
    ("docs/paper/manuscript/sections/03_method.md", "H2", "2.1  V0基线路径", "2.1", "V0基线路径", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/03_method.md", "H2", "2.2  V2R路径级重构", "2.2", "V2R路径级重构", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/03_method.md", "H2", "2.3  V3R暂存策略细化", "2.3", "V3R暂存策略细化", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/03_method.md", "H2", "2.4  共同控制与正确性约束", "2.4", "共同控制与正确性约束", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/04_experiment.md", "H1", "3  实验协议", "3", "实验协议", "HFUTHeading1", "黑体", "14", "TRUE", "FALSE", "HFUT_FMT_DOC P015"),
    ("docs/paper/manuscript/sections/04_experiment.md", "H2", "3.1  实验平台与模型配置", "3.1", "实验平台与模型配置", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/04_experiment.md", "H2", "3.2  运行与正确性协议", "3.2", "运行与正确性协议", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/04_experiment.md", "H2", "3.3  E2E、FPS与尾延迟指标", "3.3", "E2E、FPS与尾延迟指标", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/05_results.md", "H1", "4  结果与分析", "4", "结果与分析", "HFUTHeading1", "黑体", "14", "TRUE", "FALSE", "HFUT_FMT_DOC P015"),
    ("docs/paper/manuscript/sections/05_results.md", "H2", "4.1  正确性约束验证", "4.1", "正确性约束验证", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/05_results.md", "H2", "4.2  路径级重构的E2E响应", "4.2", "路径级重构的E2E响应", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/05_results.md", "H2", "4.3  暂存策略的增量响应", "4.3", "暂存策略的增量响应", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/05_results.md", "H2", "4.4  平均性能与尾延迟响应", "4.4", "平均性能与尾延迟响应", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/05_results.md", "H2", "4.5  解释边界与局限性", "4.5", "解释边界与局限性", "HFUTHeading2", "黑体", "10.5", "TRUE", "FALSE", "HFUT_FMT_DOC P016"),
    ("docs/paper/manuscript/sections/06_conclusion.md", "H1", "5  结  论", "5", "结  论", "HFUTHeading1", "黑体", "14", "TRUE", "FALSE", "HFUT_FMT_DOC P094"),
)


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def attr(element: ET.Element | None, name: str) -> str | None:
    return None if element is None else element.get(qn(name))


def text_of(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.iter(qn("t")))


def on_off(element: ET.Element | None) -> bool | None:
    if element is None:
        return None
    return attr(element, "val") not in {"0", "false", "off"}


def style_map(root: ET.Element) -> dict[str, ET.Element]:
    return {
        style.get(qn("styleId"), ""): style
        for style in root.findall("w:style", NS)
    }


def style_chain(style_id: str, styles: dict[str, ET.Element]) -> list[ET.Element]:
    chain: list[ET.Element] = []
    seen: set[str] = set()
    while style_id and style_id not in seen:
        seen.add(style_id)
        style = styles.get(style_id)
        if style is None:
            break
        chain.append(style)
        style_id = attr(style.find("w:basedOn", NS), "val") or ""
    return chain


def inherited_ppr_value(
    paragraph: ET.Element,
    styles: dict[str, ET.Element],
    element_name: str,
    attribute: str,
    *,
    default: str | None = None,
) -> str | None:
    ppr = paragraph.find("w:pPr", NS)
    direct = None if ppr is None else ppr.find(f"w:{element_name}", NS)
    value = attr(direct, attribute)
    if value is not None:
        return value
    style_id = attr(None if ppr is None else ppr.find("w:pStyle", NS), "val") or ""
    for style in style_chain(style_id, styles):
        node = style.find(f"w:pPr/w:{element_name}", NS)
        value = attr(node, attribute)
        if value is not None:
            return value
    return default


def effective_run_property(
    run: ET.Element,
    paragraph: ET.Element,
    styles: dict[str, ET.Element],
    property_name: str,
    *,
    font_name: str | None = None,
) -> str | bool | None:
    run_properties = run.find("w:rPr", NS)
    direct = None if run_properties is None else run_properties.find(f"w:{property_name}", NS)
    if property_name == "b":
        value = on_off(direct)
    elif property_name == "rFonts":
        value = attr(direct, font_name or "eastAsia")
    else:
        value = attr(direct, "val")
    if value is not None:
        return value

    character_style = attr(None if run_properties is None else run_properties.find("w:rStyle", NS), "val")
    if character_style:
        for style in style_chain(character_style, styles):
            node = style.find(f"w:rPr/w:{property_name}", NS)
            if property_name == "b":
                value = on_off(node)
            elif property_name == "rFonts":
                value = attr(node, font_name or "eastAsia")
            else:
                value = attr(node, "val")
            if value is not None:
                return value

    paragraph_style = attr(paragraph.find("w:pPr/w:pStyle", NS), "val") or ""
    for style in style_chain(paragraph_style, styles):
        node = style.find(f"w:rPr/w:{property_name}", NS)
        if property_name == "b":
            value = on_off(node)
        elif property_name == "rFonts":
            value = attr(node, font_name or "eastAsia")
        else:
            value = attr(node, "val")
        if value is not None:
            return value
    return None


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def audit_headings(
    document: ET.Element, styles: dict[str, ET.Element]
) -> tuple[list[str], list[dict[str, str]]]:
    errors: list[str] = []
    body = document.find("w:body", NS)
    if body is None:
        return ["document has no body"], []
    actual = [
        paragraph for paragraph in body.findall("w:p", NS)
        if attr(paragraph.find("w:pPr/w:pStyle", NS), "val")
        in {"HFUTIntroHeading", "HFUTHeading1", "HFUTHeading2", "HFUTHeading3"}
    ]
    require(errors, len(actual) == len(HEADINGS), f"actual heading count={len(actual)}, expected {len(HEADINGS)}")
    rows: list[dict[str, str]] = []
    for index, expected in enumerate(HEADINGS):
        source_file, level, source_text, number, title, style_id, font, size, number_bold, title_bold, authority = expected
        paragraph = actual[index] if index < len(actual) else None
        row = {
            "section_source_file": source_file,
            "heading_level": level,
            "source_text": source_text,
            "visible_number": number,
            "visible_separator": "two literal spaces",
            "visible_title": title,
            "number_font": font,
            "number_size_pt": size,
            "number_bold": number_bold,
            "title_font": font,
            "title_size_pt": size,
            "title_bold": title_bold,
            "alignment": "left",
            "left_indent": "0",
            "space_preservation": "xml:space=preserve",
            "actual_docx_run_count": "0",
            "source_authority": authority,
            "pass_fail": "FAIL",
        }
        if paragraph is None:
            errors.append(f"missing heading {source_text!r}")
            rows.append(row)
            continue
        runs = paragraph.findall("w:r", NS)
        row["actual_docx_run_count"] = str(len(runs))
        visible = text_of(paragraph)
        style = attr(paragraph.find("w:pPr/w:pStyle", NS), "val")
        expected_runs = 5 if source_text == "5  结  论" else 3
        row_errors: list[str] = []
        if visible != source_text:
            row_errors.append(f"literal={visible!r}")
        if style != style_id:
            row_errors.append(f"style={style!r}")
        if len(runs) != expected_runs:
            row_errors.append(f"run_count={len(runs)}")
        if len(runs) >= 2:
            if text_of(runs[0]) != number:
                row_errors.append("number run mismatch")
            if text_of(runs[1]) != "  " or runs[1].find("w:t", NS).get(XML_SPACE) != "preserve":
                row_errors.append("separator is not one preserved two-space run")
        else:
            row_errors.append("missing number/separator runs")
        if source_text == "5  结  论" and len(runs) == 5:
            if [text_of(run) for run in runs[2:]] != ["结", "  ", "论"]:
                row_errors.append("conclusion internal spacing runs mismatch")
            elif runs[3].find("w:t", NS).get(XML_SPACE) != "preserve":
                row_errors.append("conclusion internal spaces are not preserved")
            title_runs = (runs[2], runs[4])
        else:
            title_runs = (runs[-1],) if runs else ()
        if inherited_ppr_value(paragraph, styles, "jc", "val") != "left":
            row_errors.append("not flush-left")
        for indent_name in ("left", "firstLine"):
            if inherited_ppr_value(paragraph, styles, "ind", indent_name, default="0") != "0":
                row_errors.append(f"indent {indent_name} is not zero")
        if paragraph.find("w:pPr/w:numPr", NS) is not None:
            row_errors.append("direct automatic numbering")
        if effective_run_property(runs[0], paragraph, styles, "rFonts", font_name="eastAsia") != font:
            row_errors.append("number font mismatch")
        if effective_run_property(runs[0], paragraph, styles, "sz") != str(int(float(size) * 2)):
            row_errors.append("number size mismatch")
        if (effective_run_property(runs[0], paragraph, styles, "b") is True) != (number_bold == "TRUE"):
            row_errors.append("number bold mismatch")
        for title_run in title_runs:
            if effective_run_property(title_run, paragraph, styles, "rFonts", font_name="eastAsia") != font:
                row_errors.append("title font mismatch")
            if effective_run_property(title_run, paragraph, styles, "sz") != str(int(float(size) * 2)):
                row_errors.append("title size mismatch")
            if (effective_run_property(title_run, paragraph, styles, "b") is True) != (title_bold == "TRUE"):
                row_errors.append("title bold mismatch")
        if row_errors:
            errors.append(f"{source_text}: {'; '.join(row_errors)}")
        else:
            row["pass_fail"] = "PASS"
        rows.append(row)
    return errors, rows


def audit_reference_heading(document: ET.Element, styles: dict[str, ET.Element]) -> list[str]:
    errors: list[str] = []
    body = document.find("w:body", NS)
    if body is None:
        return ["document has no body"]
    children = list(body)
    headings = [
        paragraph for paragraph in body.findall("w:p", NS)
        if attr(paragraph.find("w:pPr/w:pStyle", NS), "val") == "HFUTReferenceHeading"
    ]
    require(errors, len(headings) == 1, f"reference-heading count={len(headings)}, expected 1")
    if not headings:
        return errors
    paragraph = headings[0]
    runs = paragraph.findall("w:r", NS)
    require(errors, text_of(paragraph) == "[参 考 文 献]", "reference-heading literal mismatch")
    require(errors, [text_of(run) for run in runs] == ["[", "参 考 文 献", "]"], "reference-heading runs mismatch")
    require(errors, inherited_ppr_value(paragraph, styles, "jc", "val") == "center", "reference-heading is not centered")
    for indent_name in ("left", "firstLine"):
        require(errors, inherited_ppr_value(paragraph, styles, "ind", indent_name, default="0") == "0", f"reference-heading {indent_name} is not zero")
    for run, expected_bold in zip(runs, (False, True, True)):
        require(errors, effective_run_property(run, paragraph, styles, "rFonts", font_name="eastAsia") == "黑体", "reference-heading font mismatch")
        require(errors, effective_run_property(run, paragraph, styles, "sz") == "21", "reference-heading size mismatch")
        require(errors, effective_run_property(run, paragraph, styles, "b") == expected_bold, "reference-heading bold mismatch")
    try:
        position = children.index(paragraph)
    except ValueError:
        errors.append("reference-heading is not a body child")
        return errors
    following = [node for node in children[position + 1:] if node.tag == qn("p") and text_of(node)]
    require(
        errors,
        bool(following) and attr(following[0].find("w:pPr/w:pStyle", NS), "val") == "Bibliography",
        "reference-heading is not separated from the first bibliography entry",
    )
    return errors


def load_docx(path: Path) -> tuple[ET.Element, dict[str, ET.Element]]:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError("ZIP CRC failure")
        return ET.fromstring(archive.read("word/document.xml")), style_map(ET.fromstring(archive.read("word/styles.xml")))


def write_inventory(path: Path, rows: list[dict[str, str]]) -> None:
    fields = list(rows[0]) if rows else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--compare", type=Path, help="Anonymous DOCX that must have identical heading/reference output.")
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    try:
        document, styles = load_docx(args.docx)
        heading_errors, rows = audit_headings(document, styles)
        errors.extend(heading_errors)
        errors.extend(audit_reference_heading(document, styles))
        if args.inventory:
            write_inventory(args.inventory, rows)
        if args.compare:
            other_document, other_styles = load_docx(args.compare)
            other_errors, other_rows = audit_headings(other_document, other_styles)
            errors.extend(f"anonymous: {error}" for error in other_errors)
            errors.extend(f"anonymous: {error}" for error in audit_reference_heading(other_document, other_styles))
            if [(row["source_text"], row["actual_docx_run_count"], row["pass_fail"]) for row in rows] != [(row["source_text"], row["actual_docx_run_count"], row["pass_fail"]) for row in other_rows]:
                errors.append("Full/Anonymous heading-instance inventory differs")
    except (OSError, ValueError, ET.ParseError, zipfile.BadZipFile, KeyError) as exc:
        errors.append(f"DOCX inspection failed: {exc}")
        rows = []
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PHASE7_1R2_ACTUAL_HEADING_VALIDATION=PASS headings={len(rows)}")
    print("PHASE7_1R2_REFERENCE_HEADING_VALIDATION=PASS literal=[参 考 文 献] authority=HFUT_FMT_DOC_P097")
    if args.inventory:
        print(f"PHASE7_1R2_HEADING_INVENTORY_WRITTEN path={args.inventory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
