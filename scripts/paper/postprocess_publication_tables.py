#!/usr/bin/env python3
"""Apply the publication three-line treatment to manuscript Tables 1--4."""

from __future__ import annotations

import argparse
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)

T1_TITLE = "表1　三条受控路径的特征矩阵。检测器和TensorRT Engine相同；三条路径均为单帧顺序执行，无跨帧流水线。"
T2_TITLE = "表2　平台、模型与统一基准协议。"
T3_TITLE = "表3　三条路径在冻结工作负载和统一评价程序下的任务级正确性。"
T4_TITLE = "表4　相关工作的定性定位。“未报告”不等同于“否”。"
TBLPR_ORDER = (
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
    "tblDescription", "tblPrChange",
)
TCBORDER_ORDER = ("top", "left", "bottom", "right", "insideH", "insideV")
PPR_ORDER = (
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
    "spacing", "ind", "jc", "sectPr", "pPrChange",
)


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def ensure_first(parent: ET.Element, local: str) -> ET.Element:
    tag = qn(local)
    node = parent.find(f"w:{local}", NS)
    if node is None:
        node = ET.Element(tag)
        parent.insert(0, node)
    return node


def insert_in_schema_order(parent: ET.Element, node: ET.Element, order: tuple[str, ...]) -> None:
    local = node.tag.rsplit("}", 1)[-1]
    desired = order.index(local)
    for index, child in enumerate(parent):
        child_local = child.tag.rsplit("}", 1)[-1]
        if child_local in order and order.index(child_local) > desired:
            parent.insert(index, node)
            return
    parent.append(node)


def set_border(parent: ET.Element, edge: str, value: str, size: int | None = None) -> None:
    old = parent.find(f"w:{edge}", NS)
    if old is not None:
        parent.remove(old)
    attrs = {qn("val"): value}
    if size is not None:
        attrs.update({qn("sz"): str(size), qn("space"): "0", qn("color"): "000000"})
    node = ET.Element(qn(edge), attrs)
    desired = TCBORDER_ORDER.index(edge)
    for index, child in enumerate(parent):
        local = child.tag.rsplit("}", 1)[-1]
        if local in TCBORDER_ORDER and TCBORDER_ORDER.index(local) > desired:
            parent.insert(index, node)
            return
    parent.append(node)


def set_paragraph_style_and_alignment(
    paragraph: ET.Element, alignment: str, neutralize_indentation: bool = False
) -> None:
    ppr = ensure_first(paragraph, "pPr")
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is None:
        pstyle = ET.Element(qn("pStyle"), {qn("val"): "HFUTTableContent"})
        ppr.insert(0, pstyle)
    else:
        pstyle.set(qn("val"), "HFUTTableContent")
    jc = ppr.find("w:jc", NS)
    if jc is None:
        jc = ET.Element(qn("jc"), {qn("val"): alignment})
        ppr.insert(1, jc)
    else:
        jc.set(qn("val"), alignment)
    if neutralize_indentation:
        tabs = ppr.find("w:tabs", NS)
        if tabs is not None:
            ppr.remove(tabs)
        indent = ppr.find("w:ind", NS)
        if indent is None:
            indent = ET.Element(qn("ind"))
            ppr.insert(1, indent)
        indent.attrib.pop(qn("hanging"), None)
        indent.attrib.pop(qn("hangingChars"), None)
        indent.attrib.pop(qn("leftChars"), None)
        indent.attrib.pop(qn("rightChars"), None)
        indent.attrib.pop(qn("firstLineChars"), None)
        indent.set(qn("left"), "0")
        indent.set(qn("right"), "0")
        indent.set(qn("firstLine"), "0")


def set_cell_width_and_borders(
    cell: ET.Element,
    width: int,
    row_index: int,
    last_row_index: int,
    compact: bool,
) -> None:
    tc_pr = ensure_first(cell, "tcPr")
    tc_width = tc_pr.find("w:tcW", NS)
    if tc_width is None:
        tc_width = ET.Element(qn("tcW"))
        tc_pr.insert(0, tc_width)
    tc_width.set(qn("w"), str(width))
    tc_width.set(qn("type"), "dxa")

    borders = tc_pr.find("w:tcBorders", NS)
    if borders is None:
        borders = ET.Element(qn("tcBorders"))
        tc_pr.insert(1, borders)
    first_row = row_index == 0
    last_row = row_index == last_row_index
    set_border(borders, "top", "single" if first_row else "nil", 8 if first_row else None)
    set_border(borders, "left", "nil")
    set_border(
        borders,
        "bottom",
        "single" if first_row or last_row else "nil",
        4 if first_row else (8 if last_row else None),
    )
    set_border(borders, "right", "nil")
    if compact:
        margins = tc_pr.find("w:tcMar", NS)
        if margins is None:
            margins = ET.Element(qn("tcMar"))
            tc_pr.insert(2, margins)
        for edge, margin in (("top", 0), ("left", 108), ("bottom", 0), ("right", 108)):
            node = margins.find(f"w:{edge}", NS)
            if node is None:
                node = ET.SubElement(margins, qn(edge))
            node.set(qn("w"), str(margin))
            node.set(qn("type"), "dxa")


def set_row_pagination(row: ET.Element, repeat_header: bool) -> None:
    tr_pr = row.find("w:trPr", NS)
    if tr_pr is None:
        tr_pr = ET.Element(qn("trPr"))
        row.insert(0, tr_pr)
    if tr_pr.find("w:cantSplit", NS) is None:
        ET.SubElement(tr_pr, qn("cantSplit"))
    header = tr_pr.find("w:tblHeader", NS)
    if repeat_header and header is None:
        ET.SubElement(tr_pr, qn("tblHeader"))
    elif not repeat_header and header is not None:
        tr_pr.remove(header)


def apply_table(table: ET.Element, table_id: str) -> None:
    rows = table.findall("w:tr", NS)
    if not rows:
        raise ValueError(f"{table_id} has no rows")
    column_count = len(rows[0].findall("w:tc", NS))
    if table_id == "T1":
        widths = (3200, 1957, 1957, 1958)
        if column_count != 4:
            raise ValueError(f"T1 expected 4 columns, found {column_count}")
    elif table_id == "T2":
        widths = (1500, 2900)
        if column_count != 2:
            raise ValueError(f"T2 expected 2 columns, found {column_count}")
    elif table_id == "T3":
        widths = (1000, 3400)
        if column_count != 2:
            raise ValueError(f"T3 expected 2 columns, found {column_count}")
    else:
        widths = (2100, 1414, 1414, 1414, 1414, 1416)
        if column_count != 6:
            raise ValueError(f"T4 expected 6 columns, found {column_count}")

    tbl_pr = ensure_first(table, "tblPr")
    tbl_style = tbl_pr.find("w:tblStyle", NS)
    if tbl_style is None:
        tbl_style = ET.Element(qn("tblStyle"))
        tbl_pr.insert(0, tbl_style)
    tbl_style.set(qn("val"), "HFUTThreeLineTable")

    tbl_width = tbl_pr.find("w:tblW", NS)
    if tbl_width is None:
        tbl_width = ET.Element(qn("tblW"))
        desired = TBLPR_ORDER.index("tblW")
        for index, child in enumerate(tbl_pr):
            local = child.tag.rsplit("}", 1)[-1]
            if local in TBLPR_ORDER and TBLPR_ORDER.index(local) > desired:
                tbl_pr.insert(index, tbl_width)
                break
        else:
            tbl_pr.append(tbl_width)
    tbl_width.set(qn("w"), str(sum(widths)))
    tbl_width.set(qn("type"), "dxa")

    borders = tbl_pr.find("w:tblBorders", NS)
    if borders is None:
        borders = ET.Element(qn("tblBorders"))
        desired = TBLPR_ORDER.index("tblBorders")
        for index, child in enumerate(tbl_pr):
            local = child.tag.rsplit("}", 1)[-1]
            if local in TBLPR_ORDER and TBLPR_ORDER.index(local) > desired:
                tbl_pr.insert(index, borders)
                break
        else:
            tbl_pr.append(borders)
    set_border(borders, "top", "single", 8)
    set_border(borders, "left", "nil")
    set_border(borders, "bottom", "single", 8)
    set_border(borders, "right", "nil")
    set_border(borders, "insideH", "nil")
    set_border(borders, "insideV", "nil")

    grid = table.find("w:tblGrid", NS)
    if grid is None:
        grid = ET.Element(qn("tblGrid"))
        table.insert(1, grid)
        for _ in widths:
            ET.SubElement(grid, qn("gridCol"))
    grid_columns = grid.findall("w:gridCol", NS)
    if len(grid_columns) != len(widths):
        raise ValueError(f"{table_id} grid/column mismatch")
    for grid_col, width in zip(grid_columns, widths):
        grid_col.set(qn("w"), str(width))

    for row_index, row in enumerate(rows):
        set_row_pagination(row, repeat_header=row_index == 0)
        cells = row.findall("w:tc", NS)
        if len(cells) != len(widths):
            raise ValueError(f"{table_id} row {row_index} column count mismatch")
        for column_index, cell in enumerate(cells):
            set_cell_width_and_borders(
                cell,
                widths[column_index],
                row_index,
                len(rows) - 1,
                table_id in {"T3", "T4"},
            )
            if table_id == "T1":
                alignment = "center" if row_index == 0 or column_index > 0 else "left"
            elif table_id == "T2":
                alignment = "center" if row_index == 0 else "left"
            elif table_id == "T4":
                alignment = "center" if row_index == 0 or column_index > 0 else "left"
            elif row_index == 0:
                alignment = "center"
            elif column_index == 0:
                alignment = "left"
            elif column_index == len(widths) - 1:
                alignment = "center"
            else:
                alignment = "right"
            for paragraph in cell.findall("w:p", NS):
                set_paragraph_style_and_alignment(
                    paragraph, alignment, neutralize_indentation=table_id in {"T1", "T2", "T4"}
                )


def locate_captioned_tables(
    root: ET.Element,
    anonymous_t2_page_break: bool,
    anonymous_t4_page_break: bool,
) -> dict[str, ET.Element]:
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    children = list(body)
    titles = {T1_TITLE: "T1", T2_TITLE: "T2", T3_TITLE: "T3", T4_TITLE: "T4"}
    found: dict[str, ET.Element] = {}
    for index, child in enumerate(children):
        if child.tag != qn("p"):
            continue
        table_id = titles.get(paragraph_text(child).strip())
        if table_id is None:
            continue
        following = next((candidate for candidate in children[index + 1:] if candidate.tag != qn("p") or paragraph_text(candidate).strip()), None)
        if following is None or following.tag != qn("tbl"):
            raise ValueError(f"{table_id} caption is not followed by a table")
        if table_id in found:
            raise ValueError(f"duplicate {table_id} caption")
        found[table_id] = following
        set_paragraph_style_and_alignment(child, "center")
        pstyle = child.find("w:pPr/w:pStyle", NS)
        pstyle.set(qn("val"), "HFUTTableCaption")
        if (
            (table_id == "T2" and anonymous_t2_page_break)
            or (table_id == "T4" and anonymous_t4_page_break)
        ):
            ppr = ensure_first(child, "pPr")
            if ppr.find("w:pageBreakBefore", NS) is None:
                insert_in_schema_order(ppr, ET.Element(qn("pageBreakBefore")), PPR_ORDER)
    if set(found) != {"T1", "T2", "T3", "T4"}:
        raise ValueError(f"expected T1, T2, T3 and T4 captions, found {sorted(found)}")
    return found


def rewrite(
    input_path: Path,
    output_path: Path,
    anonymous_t2_page_break: bool = False,
    anonymous_t4_page_break: bool = False,
) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    root = ET.fromstring(parts["word/document.xml"])
    tables = locate_captioned_tables(
        root, anonymous_t2_page_break, anonymous_t4_page_break
    )
    apply_table(tables["T1"], "T1")
    apply_table(tables["T2"], "T2")
    apply_table(tables["T3"], "T3")
    apply_table(tables["T4"], "T4")
    parts["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output_path.parent, suffix=".docx", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(parts):
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o600 << 16
                archive.writestr(info, parts[name])
        temporary.replace(output_path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--anonymous-t2-page-break", action="store_true")
    parser.add_argument("--anonymous-t4-page-break", action="store_true")
    args = parser.parse_args()
    rewrite(
        args.input,
        args.output,
        args.anonymous_t2_page_break,
        args.anonymous_t4_page_break,
    )
    print(f"publication_tables=PASS output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
