#!/usr/bin/env python3
"""Build the Phase 2.5 HFUT reference DOCX candidate.

This builder deliberately uses only the Python standard library.  The package
is assembled from a fixed OOXML baseline so that ZIP timestamps, entry order,
relationship identifiers, and core properties do not vary between runs.
It creates the repository reference candidate and an external, virtual style
specimen; the specimen is never used as the reference template.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile
import zlib

from inspect_phase2_5_poc_docx import inspect_content_types
from validate_word_heading_numbering_docx import audit_docx_heading_numbering


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx"
DEFAULT_EXTERNAL = Path(
    "/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/"
    "step4_reference_docx_v1"
)
SPECIMEN_NAME = "hfut_reference_style_specimen_v1.0.docx"
STYLE_MAP = REPO / "docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RT = "http://schemas.openxmlformats.org/package/2006/relationships"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"


def q(name: str) -> str:
    return f"{{{W}}}{name}"


def xml_escape(value: str) -> str:
    return escape(value, {"\"": "&quot;", "'": "&apos;"})


def r_fonts(east: str = "宋体", ascii_font: str = "Times New Roman") -> str:
    return (
        f'<w:rFonts w:ascii="{xml_escape(ascii_font)}" '
        f'w:hAnsi="{xml_escape(ascii_font)}" w:eastAsia="{xml_escape(east)}" '
        f'w:cs="{xml_escape(ascii_font)}"/>'
    )


def rpr(
    east: str = "宋体",
    ascii_font: str = "Times New Roman",
    size: str = "21",
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
) -> str:
    bits = [r_fonts(east, ascii_font)]
    if bold:
        bits.append("<w:b/><w:bCs/>")
    if italic:
        bits.append("<w:i/><w:iCs/>")
    if color:
        bits.append(f'<w:color w:val="{color}"/>')
    bits.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    bits.append('<w:lang w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA"/>')
    return "<w:rPr>" + "".join(bits) + "</w:rPr>"


def spacing(
    line: int | None = None,
    before: str = "0",
    after: str = "0",
    exact: bool = False,
    line_rule: str | None = None,
) -> str:
    attrs = [f'w:before="{before}"', f'w:after="{after}"']
    if line is not None:
        attrs.extend([
            f'w:line="{line}"',
            f'w:lineRule="{line_rule or ("exact" if exact else "auto")}"',
        ])
    return "<w:spacing " + " ".join(attrs) + "/>"


def ppr(
    *,
    align: str | None = None,
    first: int | None = None,
    left: int | None = None,
    right: int | None = None,
    line: int | None = None,
    before: str = "0",
    after: str = "0",
    exact: bool = False,
    keep_next: bool = False,
    keep_lines: bool = False,
    page_break_before: bool = False,
    outline: int | None = None,
    num_id: int | None = None,
    ilvl: int | None = None,
    tabs: str = "",
    line_rule: str | None = None,
) -> str:
    bits: list[str] = []
    if keep_next:
        bits.append("<w:keepNext/>")
    if keep_lines:
        bits.append("<w:keepLines/>")
    if page_break_before:
        bits.append("<w:pageBreakBefore/>")
    if num_id is not None:
        bits.append(f'<w:numPr><w:ilvl w:val="{ilvl or 0}"/><w:numId w:val="{num_id}"/></w:numPr>')
    bits.append(spacing(line, before, after, exact, line_rule))
    ind_attrs = []
    if first is not None:
        if first < 0:
            ind_attrs.append(f'w:hanging="{-first}"')
        else:
            ind_attrs.append(f'w:firstLine="{first}"')
    if left is not None:
        ind_attrs.append(f'w:left="{left}"')
    if right is not None:
        ind_attrs.append(f'w:right="{right}"')
    if ind_attrs:
        bits.append("<w:ind " + " ".join(ind_attrs) + "/>" )
    if align:
        bits.append(f'<w:jc w:val="{align}"/>')
    if outline is not None:
        bits.append(f'<w:outlineLvl w:val="{outline}"/>')
    if tabs:
        bits.append(tabs)
    return "<w:pPr>" + "".join(bits) + "</w:pPr>"


def para_style(
    style_id: str,
    name: str,
    *,
    based_on: str = "Normal",
    east: str = "宋体",
    ascii_font: str = "Times New Roman",
    size: str = "21",
    bold: bool = False,
    italic: bool = False,
    align: str | None = None,
    first: int | None = None,
    left: int | None = None,
    right: int | None = None,
    line: int | None = None,
    before: str = "0",
    after: str = "0",
    exact: bool = False,
    keep_next: bool = False,
    keep_lines: bool = False,
    page_break_before: bool = False,
    outline: int | None = None,
    num_id: int | None = None,
    ilvl: int | None = None,
    qformat: bool = True,
    line_rule: str | None = None,
) -> str:
    qfmt = "<w:qFormat/>" if qformat else ""
    based = f'<w:basedOn w:val="{based_on}"/>' if based_on else ""
    return (
        f'<w:style w:type="paragraph" w:styleId="{style_id}">'
        f'<w:name w:val="{xml_escape(name)}"/>{based}{qfmt}'
        + ppr(
            align=align, first=first, left=left, right=right, line=line,
            before=before, after=after, exact=exact, keep_next=keep_next,
            keep_lines=keep_lines, page_break_before=page_break_before,
            outline=outline, num_id=num_id, ilvl=ilvl,
            line_rule=line_rule,
        )
        + rpr(east, ascii_font, size, bold, italic)
        + "</w:style>"
    )


def char_style(style_id: str, name: str, *, based_on: str = "DefaultParagraphFont", east: str = "宋体", ascii_font: str = "Times New Roman", size: str = "21", bold: bool = False, italic: bool = False) -> str:
    return (
        f'<w:style w:type="character" w:styleId="{style_id}">'
        f'<w:name w:val="{xml_escape(name)}"/><w:basedOn w:val="{based_on}"/><w:qFormat/>'
        + rpr(east, ascii_font, size, bold, italic)
        + "</w:style>"
    )


def table_style() -> str:
    # Word border sizes are eighths of a point: 1 pt = 8, 0.5 pt = 4.
    borders = (
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:left w:val="nil"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:right w:val="nil"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        '<w:insideV w:val="nil"/>'
        '</w:tblBorders>'
    )
    margins = '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar>'
    first_row = '<w:tblStylePr w:type="firstRow"><w:tblPr>' + '<w:tblBorders><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders>' + '</w:tblPr></w:tblStylePr>'
    return (
        '<w:style w:type="table" w:styleId="HFUTThreeLineTable">'
        '<w:name w:val="HFUT Three Line Table"/><w:basedOn w:val="TableNormal"/><w:qFormat/>'
        '<w:tblPr>' + borders + margins + '</w:tblPr>'
        + first_row + '</w:style>'
    )


def styles_xml() -> str:
    styles = [
        para_style("Normal", "Normal", based_on="", east="宋体", size="21", align="both", first=200, line=320, exact=True),
        para_style("PageNumber", "Page Number", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="18", align="center", first=0, line=240, exact=True, qformat=False),
        para_style("HFUTSpecimenNotice", "HFUT Specimen Notice", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="18", bold=True, align="center", line=240, exact=True, keep_next=True),
        para_style("HFUTBody", "HFUT Body", based_on="Normal", east="宋体", size="21", align="both", first=200, line=320, exact=True),
        para_style("HFUTTitleCN", "HFUT Title CN", based_on="Normal", east="黑体", ascii_font="Times New Roman", size="30", bold=True, align="center", line=360, exact=True, keep_next=True),
        para_style("HFUTTitleEN", "HFUT Title EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="28", align="center", line=336, exact=True, keep_next=True),
        para_style("HFUTAuthorsCN", "HFUT Authors CN", based_on="Normal", east="宋体", size="21", align="center", line=300, exact=True),
        para_style("HFUTAuthorsEN", "HFUT Authors EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="21", align="center", line=300, exact=True),
        para_style("HFUTAffiliationCN", "HFUT Affiliation CN", based_on="Normal", east="宋体", size="15", align="center", line=240, exact=True),
        para_style("HFUTAffiliationEN", "HFUT Affiliation EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="15", align="center", line=240, exact=True),
        para_style("HFUTAbstractLabelCN", "HFUT Abstract Label CN", based_on="Normal", east="黑体", size="18", bold=True, align="both", line=280, exact=True),
        para_style("HFUTAbstractBodyCN", "HFUT Abstract Body CN", based_on="Normal", east="宋体", size="18", align="both", line=280, exact=True),
        para_style("HFUTAbstractLabelEN", "HFUT Abstract Label EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="18", bold=True, align="both", line=280, exact=True),
        para_style("HFUTAbstractBodyEN", "HFUT Abstract Body EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="21", align="both", line=280, exact=True),
        para_style("HFUTKeywordsLabelCN", "HFUT Keywords Label CN", based_on="Normal", east="黑体", size="18", bold=True, align="both", line=280, exact=True),
        para_style("HFUTKeywordsBodyCN", "HFUT Keywords Body CN", based_on="Normal", east="宋体", size="18", align="both", line=280, exact=True),
        para_style("HFUTKeywordsLabelEN", "HFUT Keywords Label EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="18", bold=True, align="both", line=280, exact=True),
        para_style("HFUTKeywordsBodyEN", "HFUT Keywords Body EN", based_on="Normal", east="Times New Roman", ascii_font="Times New Roman", size="21", align="both", line=280, exact=True),
        para_style("HFUTClassification", "HFUT Classification", based_on="Normal", east="宋体", size="18", align="left", line=280, exact=True),
        para_style("HFUTHeading1", "HFUT Heading 1", based_on="Normal", east="黑体", size="28", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=0),
        para_style("HFUTHeading2", "HFUT Heading 2", based_on="Normal", east="黑体", size="21", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=1),
        para_style("HFUTHeading3", "HFUT Heading 3", based_on="Normal", east="楷体", size="21", align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=2),
        para_style("HFUTIntroHeading", "HFUT Introduction Heading", based_on="HFUTHeading1", east="黑体", size="28", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=0, num_id=2, ilvl=0),
        para_style(
            "HFUTEquation", "HFUT Equation", based_on="Normal",
            east="Times New Roman", ascii_font="Times New Roman", size="21",
            align="center", line=480, before="80", after="80",
            line_rule="atLeast", keep_lines=True,
        ),
        para_style("HFUTFigureCaption", "HFUT Figure Caption", based_on="Normal", east="黑体", size="15", bold=True, align="center", line=320, exact=True, keep_lines=True),
        para_style("HFUTTableCaption", "HFUT Table Caption", based_on="Normal", east="黑体", size="15", bold=True, align="center", line=320, exact=True, keep_lines=True),
        para_style("HFUTTableContent", "HFUT Table Content", based_on="Normal", east="宋体", size="15", align="center", line=240, exact=True, keep_lines=True),
        para_style("HFUTReferenceHeading", "HFUT Reference Heading", based_on="Normal", east="黑体", size="21", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True),
        para_style("HFUTReferenceEntry", "HFUT Reference Entry", based_on="Normal", east="宋体", size="15", align="left", left=360, first=-360, line=280, exact=True, keep_lines=True),
        para_style("HFUTAuthorBiography", "HFUT Author Biography", based_on="Normal", east="宋体", size="15", align="left", line=280, exact=True),
        para_style("HFUTFunding", "HFUT Funding", based_on="Normal", east="宋体", size="15", align="left", line=280, exact=True),
        para_style("HFUTAcknowledgement", "HFUT Acknowledgement", based_on="Normal", east="宋体", size="15", align="left", line=280, exact=True),
        para_style("BodyText", "Body Text", based_on="HFUTBody", east="宋体", size="21", align="both", first=200, line=320, exact=True),
        para_style("Title", "Title", based_on="HFUTTitleCN", east="黑体", size="30", bold=True, align="center", line=360, exact=True, keep_next=True),
        para_style("Subtitle", "Subtitle", based_on="HFUTTitleEN", east="Times New Roman", ascii_font="Times New Roman", size="28", align="center", line=336, exact=True, keep_next=True),
        para_style("Author", "Author", based_on="HFUTAuthorsEN", east="Times New Roman", ascii_font="Times New Roman", size="21", align="center", line=300, exact=True),
        para_style("Abstract", "Abstract", based_on="HFUTAbstractBodyEN", east="Times New Roman", ascii_font="Times New Roman", size="21", align="both", line=280, exact=True),
        para_style("Heading1", "Heading 1", based_on="HFUTHeading1", east="黑体", size="28", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=0),
        para_style("Heading2", "Heading 2", based_on="HFUTHeading2", east="黑体", size="21", bold=True, align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=1),
        para_style("Heading3", "Heading 3", based_on="HFUTHeading3", east="楷体", size="21", align="left", line=320, exact=True, keep_next=True, keep_lines=True, outline=2),
        para_style("Caption", "Caption", based_on="HFUTFigureCaption", east="黑体", size="15", bold=True, align="center", line=320, exact=True, keep_lines=True),
        para_style("Table", "Table", based_on="HFUTTableContent", east="宋体", size="15", align="center", line=240, exact=True, keep_lines=True),
        para_style("Bibliography", "Bibliography", based_on="HFUTReferenceEntry", east="宋体", size="15", align="left", left=360, first=-360, line=280, exact=True, keep_lines=True),
        char_style("HFUTLatin", "HFUT Latin", east="Times New Roman", ascii_font="Times New Roman", size="21"),
        table_style(),
    ]
    return (
        f'<w:styles xmlns:w="{W}">'
        '<w:docDefaults><w:rPrDefault><w:rPr>' + r_fonts("宋体", "Times New Roman") + '<w:lang w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr>' + spacing(320, exact=True) + '</w:pPr></w:pPrDefault></w:docDefaults>'
        + "".join(styles) + "</w:styles>"
    )


def numbering_xml() -> str:
    return f'''<w:numbering xmlns:w="{W}">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="multilevel"/>
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="0"/></w:tabs><w:ind w:left="0" w:hanging="0"/></w:pPr>{rpr("黑体", "Times New Roman", "28", True)}</w:lvl>
    <w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1.%2"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr>{rpr("黑体", "Times New Roman", "21", True)}</w:lvl>
    <w:lvl w:ilvl="2"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1.%2.%3"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr>{rpr("楷体", "Times New Roman", "21")}</w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:multiLevelType w:val="singleLevel"/>
    <w:lvl w:ilvl="0"><w:start w:val="0"/><w:numFmt w:val="decimal"/><w:lvlText w:val="0"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:hanging="0"/></w:pPr>{rpr("黑体", "Times New Roman", "28", True)}</w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>'''


def settings_xml() -> str:
    return f'''<w:settings xmlns:w="{W}">
  <w:zoom w:percent="100"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
  <w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>
</w:settings>'''


def footer_xml() -> str:
    return f'''<w:ftr xmlns:w="{W}" xmlns:r="{R}">
  <w:p><w:pPr><w:pStyle w:val="PageNumber"/><w:jc w:val="center"/></w:pPr>
    <w:fldSimple w:instr=" PAGE "><w:r><w:rPr><w:noProof/></w:rPr></w:r></w:fldSimple>
  </w:p>
</w:ftr>'''


def paragraph(style: str, text: str = "", *, num_id: int | None = None, ilvl: int = 0) -> str:
    num = ""
    if num_id is not None:
        num = f'<w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/></w:numPr>'
    body = f'<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>' if text else '<w:r/>'
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{num}</w:pPr>{body}</w:p>'


def table_specimen() -> str:
    def cell(value: str) -> str:
        return f'<w:tc><w:tcPr><w:tcW w:w="3600" w:type="dxa"/></w:tcPr>{paragraph("HFUTTableContent", value)}</w:tc>'
    borders = '<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/><w:left w:val="nil"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/><w:right w:val="nil"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:insideV w:val="nil"/></w:tblBorders>'
    rows = [
        ["列名A", "Value"],
        ["示例项", "0.00"],
        ["占位项", "－"],
    ]
    return '<w:tbl><w:tblPr><w:tblStyle w:val="HFUTThreeLineTable"/><w:tblW w:w="7200" w:type="dxa"/>' + borders + '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid><w:gridCol w:w="3600"/><w:gridCol w:w="3600"/></w:tblGrid>' + ''.join('<w:tr>' + ''.join(cell(v) for v in row) + '</w:tr>' for row in rows) + '</w:tbl>'


def sect_pr(*, columns: int = 1) -> str:
    # A4: 11906 x 16838 twips; 2.4/2.0/2.3/2.3 cm -> 1361/1134/1304/1304 twips.
    return (
        f'<w:sectPr xmlns:w="{W}" xmlns:r="{R}"><w:footerReference w:type="default" r:id="rId4"/>'
        '<w:pgSz w:w="11906" w:h="16838" w:orient="portrait"/>'
        '<w:pgMar w:top="1361" w:right="1304" w:bottom="1134" w:left="1304" w:header="720" w:footer="720" w:gutter="0"/>'
        f'<w:cols w:num="{columns}" w:space="425"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )


def document_xml(specimen: bool = False) -> str:
    if not specimen:
        body = '<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr><w:r/></w:p>'
    else:
        parts = [
            paragraph("HFUTSpecimenNotice", "TOOLCHAIN STYLE SPECIMEN ONLY"),
            paragraph("HFUTSpecimenNotice", "NOT PAPER CONTENT"),
            paragraph("HFUTSpecimenNotice", "NOT SUBMISSION MANUSCRIPT"),
            paragraph("HFUTTitleCN", "中文题名占位"),
            paragraph("HFUTTitleEN", "English Title Placeholder"),
            paragraph("HFUTAuthorsCN", "作者占位"),
            paragraph("HFUTAuthorsEN", "Author Placeholder"),
            paragraph("HFUTAffiliationCN", "单位占位；省、市、邮编占位"),
            paragraph("HFUTAffiliationEN", "Affiliation Placeholder; Province, City, Postcode Placeholder"),
            paragraph("HFUTAbstractLabelCN", "摘 要："),
            paragraph("HFUTAbstractBodyCN", "此处为中文摘要样式展示占位，不是论文内容。"),
            paragraph("HFUTAbstractLabelEN", "Abstract: "),
            paragraph("HFUTAbstractBodyEN", "This is an English abstract style placeholder, not paper content."),
            paragraph("HFUTKeywordsLabelCN", "关键词："),
            paragraph("HFUTKeywordsBodyCN", "关键词占位；边缘计算；视觉检测；部署"),
            paragraph("HFUTKeywordsLabelEN", "Key words: "),
            paragraph("HFUTKeywordsBodyEN", "keyword placeholder; edge computing; visual inspection; deployment"),
            paragraph("HFUTClassification", "中图分类号：占位"),
            paragraph("HFUTIntroHeading", "引言占位", num_id=2),
            paragraph("HFUTHeading1", "一级标题占位"),
            paragraph("HFUTHeading2", "二级标题占位"),
            paragraph("HFUTHeading3", "三级标题占位"),
            paragraph("HFUTBody", "这是用于检查正文样式的中文占位段落。English and numbers 123 use the same named paragraph style."),
            paragraph("HFUTBody", "第二段正文占位，用于检查首行缩进、两端对齐和精确行距。"),
            paragraph("HFUTEquation", "公式占位：x = y + z（MathType 对象待后续 POC）"),
            paragraph("HFUTFigureCaption", "图1 图题占位（无正式图像）"),
            paragraph("HFUTTableCaption", "表1 表题占位"),
            table_specimen(),
            paragraph("HFUTReferenceHeading", "参考文献"),
            paragraph("HFUTReferenceEntry", "[1] Reference entry placeholder."),
            paragraph("HFUTReferenceEntry", "[2] 中文参考文献占位。"),
            paragraph("HFUTReferenceEntry", "[3] Mixed Chinese and English reference placeholder."),
        ]
        body = "".join(parts)
    return f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{body}{sect_pr(columns=1)}</w:body></w:document>'


def core_xml() -> str:
    return f'''<cp:coreProperties xmlns:cp="{CP}" xmlns:dc="{DC}" xmlns:dcterms="{DCTERMS}" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="{XSI}">
  <dc:title>hfut_journal_reference_v1.0.docx</dc:title>
  <dc:subject>DERIVED_REFERENCE_DOCX_CANDIDATE; NOT_OFFICIAL_JOURNAL_TEMPLATE; NOT_FINAL_SUBMISSION_FILE; PENDING_PANDOC_POC; PENDING_MICROSOFT_WORD_REVIEW</dc:subject>
  <dc:creator>PAPER_PROJECT_AI</dc:creator>
  <cp:keywords>reference DOCX; deterministic OOXML; HFUT candidate</cp:keywords>
  <dc:description>DERIVED_REFERENCE_DOCX_CANDIDATE. NOT_OFFICIAL_JOURNAL_TEMPLATE. NOT_FINAL_SUBMISSION_FILE. PENDING_PANDOC_POC. PENDING_MICROSOFT_WORD_REVIEW.</dc:description>
  <cp:lastModifiedBy>PAPER_PROJECT_AI</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-08-05T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-08-05T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def custom_xml() -> str:
    props = [
        ("TemplateIdentity", "DERIVED_REFERENCE_DOCX_CANDIDATE"),
        ("OfficialStatus", "NOT_OFFICIAL_JOURNAL_TEMPLATE"),
        ("SubmissionStatus", "NOT_FINAL_SUBMISSION_FILE"),
        ("PandocStatus", "PENDING_PANDOC_POC"),
        ("WordStatus", "PENDING_MICROSOFT_WORD_REVIEW"),
        ("ColumnStrategy", "front matter single-column target; body double-column target; section boundary pending"),
    ]
    entries = []
    for idx, (name, value) in enumerate(props, 2):
        entries.append(f'<property name="{name}" fmtid="{{D5CDD505-2E9C-101B-9397-08002B2CF9AE}}" pid="{idx}"><vt:lpwstr>{xml_escape(value)}</vt:lpwstr></property>')
    return f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">{"".join(entries)}</Properties>'


def app_xml() -> str:
    return f'<Properties xmlns="{EP}"><Application>Python standard library deterministic OOXML builder</Application><DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><Company>Project-owned candidate</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>1.0</AppVersion></Properties>'


def font_table_xml() -> str:
    return f'''<w:fonts xmlns:w="{W}">
  <w:font w:name="宋体"><w:altName w:val="SimSun"/><w:panose1 w:val="02010600030101010101"/><w:charset w:val="86"/><w:family w:val="auto"/><w:pitch w:val="variable"/></w:font>
  <w:font w:name="黑体"><w:altName w:val="SimHei"/><w:panose1 w:val="02010609060101010101"/><w:charset w:val="86"/><w:family w:val="modern"/><w:pitch w:val="fixed"/></w:font>
  <w:font w:name="楷体"><w:panose1 w:val="02010609060101010101"/><w:charset w:val="86"/><w:family w:val="modern"/><w:pitch w:val="fixed"/></w:font>
  <w:font w:name="Times New Roman"><w:panose1 w:val="02020603050405020304"/><w:charset w:val="00"/><w:family w:val="roman"/><w:pitch w:val="variable"/></w:font>
</w:fonts>'''


def theme_xml() -> str:
    # This is the deterministic theme1.xml from Pandoc 3.10.1's built-in
    # default reference.docx. Keeping its bytes embedded avoids making the
    # canonical builder depend on a user's local Pandoc data directory.
    compressed = (
        "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"
    )
    return zlib.decompress(base64.b64decode(compressed)).decode("utf-8")


def content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/><Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/><Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/><Override PartName="/docProps/custom.xml" ContentType="application/vnd.openxmlformats-officedocument.custom-properties+xml"/></Types>'''


def package_rels() -> str:
    return f'''<Relationships xmlns="{RT}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties" Target="docProps/custom.xml"/></Relationships>'''


def document_rels() -> str:
    return f'''<Relationships xmlns="{RT}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/><Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/><Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/></Relationships>'''


def package_parts(specimen: bool) -> dict[str, bytes]:
    parts = {
        "[Content_Types].xml": content_types_xml(),
        "_rels/.rels": package_rels(),
        "docProps/core.xml": core_xml(),
        "docProps/app.xml": app_xml(),
        "docProps/custom.xml": custom_xml(),
        "word/document.xml": document_xml(specimen),
        "word/_rels/document.xml.rels": document_rels(),
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": numbering_xml(),
        "word/settings.xml": settings_xml(),
        "word/footer1.xml": footer_xml(),
        "word/fontTable.xml": font_table_xml(),
        "word/theme/theme1.xml": theme_xml(),
    }
    return {name: value.encode("utf-8") for name, value in parts.items()}


def write_deterministic_docx(path: Path, *, specimen: bool = False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    parts = package_parts(specimen)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in sorted(parts):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            info.external_attr = 0
            info.extra = b""
            info.comment = b""
            zf.writestr(info, parts[name])
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style_map_rows() -> list[dict[str, str]]:
    fields = [
        "style_id", "style_name", "style_type", "semantic_role", "pandoc_source_element", "based_on",
        "east_asia_font", "ascii_font", "font_size_pt", "bold", "italic", "alignment",
        "first_line_indent_twips", "left_indent_twips", "right_indent_twips", "space_before_pt",
        "space_after_pt", "line_spacing_rule", "line_spacing_value", "keep_next", "keep_lines",
        "page_break_before", "numbering_level", "implementation_source", "source_rule_ids",
        "step3_evidence", "authority_status", "poc_status", "windows_check_required", "notes",
    ]
    rows: list[dict[str, str]] = []

    def add(style_id: str, style_name: str, role: str, pandoc: str, based: str, east: str, ascii_font: str, size: str, bold: str, align: str, first: str, left: str, line_rule: str, line: str, keep: str, level: str, source: str, rules: str, evidence: str, authority: str, poc: str, windows: str, notes: str):
        rows.append({
            "style_id": style_id, "style_name": style_name, "style_type": "table" if style_id == "HFUTThreeLineTable" else "paragraph", "semantic_role": role,
            "pandoc_source_element": pandoc, "based_on": based, "east_asia_font": east, "ascii_font": ascii_font, "font_size_pt": size,
            "bold": bold, "italic": "FALSE", "alignment": align, "first_line_indent_twips": first, "left_indent_twips": left,
            "right_indent_twips": "0", "space_before_pt": "0", "space_after_pt": "0", "line_spacing_rule": line_rule,
            "line_spacing_value": line, "keep_next": keep, "keep_lines": "TRUE" if "Heading" in style_id or "Caption" in style_id or style_id in {"HFUTEquation", "HFUTTableContent", "HFUTReferenceEntry", "Bibliography"} else "FALSE",
            "page_break_before": "FALSE", "numbering_level": level, "implementation_source": source, "source_rule_ids": rules,
            "step3_evidence": evidence, "authority_status": authority, "poc_status": poc, "windows_check_required": windows, "notes": notes,
        })

    add("HFUTTitleCN", "HFUT Title CN", "Chinese title", "title", "Normal", "黑体", "Times New Roman", "15", "TRUE", "center", "0", "0", "exact", "18", "TRUE", "", "OOXML named style", "HFUT-FMT-001", "title evidence; exact title size not universal", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "candidate only; no official title content")
    add("HFUTTitleEN", "HFUT Title EN", "English title", "title", "Normal", "Times New Roman", "Times New Roman", "14", "FALSE", "center", "0", "0", "exact", "16.8", "TRUE", "", "OOXML named style", "HFUT-FMT-008", "English title evidence; size candidate", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "sentence-initial/proper-noun capitalization remains source-writing rule")
    add("HFUTAuthorsCN", "HFUT Authors CN", "Chinese authors", "author", "Normal", "宋体", "Times New Roman", "10.5", "FALSE", "center", "0", "0", "exact", "15", "FALSE", "", "OOXML named style", "HFUT-FMT-002", "front-matter conversion evidence", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "no real author information")
    add("HFUTAuthorsEN", "HFUT Authors EN", "English authors", "author", "Normal", "Times New Roman", "Times New Roman", "10.5", "FALSE", "center", "0", "0", "exact", "15", "FALSE", "", "OOXML named style", "HFUT-FMT-009", "front-matter conversion evidence", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "no real author information")
    add("HFUTAffiliationCN", "HFUT Affiliation CN", "Chinese affiliation", "author", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "center", "0", "0", "exact", "12", "FALSE", "", "OOXML named style", "HFUT-FMT-002", "7.5 pt affiliation evidence", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "province/city/postcode are content fields")
    add("HFUTAffiliationEN", "HFUT Affiliation EN", "English affiliation", "author", "Normal", "Times New Roman", "Times New Roman", "7.5", "FALSE", "center", "0", "0", "exact", "12", "FALSE", "", "OOXML named style", "HFUT-FMT-009", "7.5 pt affiliation evidence", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "province/city/postcode are content fields")
    add("HFUTAbstractLabelCN", "HFUT Abstract Label CN", "Chinese abstract label", "abstract", "Normal", "黑体", "Times New Roman", "9", "TRUE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-003", "9 pt Heiti; exact 14 pt", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "label can share paragraph with body only when needed")
    add("HFUTAbstractBodyCN", "HFUT Abstract Body CN", "Chinese abstract body", "abstract", "Normal", "宋体", "Times New Roman", "9", "FALSE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-003", "9 pt Song; exact 14 pt", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "minimum/target length is source writing")
    add("HFUTAbstractLabelEN", "HFUT Abstract Label EN", "English abstract label", "abstract", "Normal", "Times New Roman", "Times New Roman", "9", "TRUE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-010", "mixed-format source; label candidate", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "English abstract label size needs Word check")
    add("HFUTAbstractBodyEN", "HFUT Abstract Body EN", "English abstract body", "abstract", "Normal", "Times New Roman", "Times New Roman", "10.5", "FALSE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-010", "Step 2 five-size TNR", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "semantic equivalence is manual")
    add("HFUTKeywordsLabelCN", "HFUT Keywords Label CN", "Chinese keyword label", "keywords", "Normal", "黑体", "Times New Roman", "9", "TRUE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-005", "9 pt Heiti", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "keyword count is source validation")
    add("HFUTKeywordsBodyCN", "HFUT Keywords Body CN", "Chinese keywords", "keywords", "Normal", "宋体", "Times New Roman", "9", "FALSE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-005", "9 pt Song", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "keyword count/order is source validation")
    add("HFUTKeywordsLabelEN", "HFUT Keywords Label EN", "English keyword label", "keywords", "Normal", "Times New Roman", "Times New Roman", "9", "TRUE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-011", "label candidate", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "English keyword label needs Word check")
    add("HFUTKeywordsBodyEN", "HFUT Keywords Body EN", "English keywords", "keywords", "Normal", "Times New Roman", "Times New Roman", "10.5", "FALSE", "both", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-011", "five-size TNR", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "keyword count/order is source validation")
    add("HFUTClassification", "HFUT Classification", "Chinese Library Classification", "metadata", "Normal", "宋体", "Times New Roman", "9", "FALSE", "left", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-FMT-006", "front-matter field evidence", "TEXTUALLY_CONFIRMED", "PENDING_POC", "YES", "do not copy sample TU 411.01")
    add("HFUTBody", "HFUT Body", "main body", "paragraph", "Normal", "宋体", "Times New Roman", "10.5", "FALSE", "both", "200", "0", "exact", "16", "FALSE", "", "OOXML named style", "HFUT-FMT-012; HFUT-FMT-028", "Normal 10.5; Style19 200/16 exact", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "200 twips and 16 pt are derived candidates, not universal official rules")
    add("HFUTHeading1", "HFUT Heading 1", "level-1 heading", "heading", "Normal", "黑体", "Times New Roman", "14", "TRUE", "left", "0", "0", "exact", "16", "TRUE", "", "OOXML named style; explicit number in source text", "HFUT-FMT-013; HFUT-FMT-016", "14 pt Heiti; keep-next candidate", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "automatic Word numbering disabled; Markdown supplies the visible number")
    add("HFUTHeading2", "HFUT Heading 2", "level-2 heading", "heading", "Normal", "黑体", "Times New Roman", "10.5", "TRUE", "left", "0", "0", "exact", "16", "TRUE", "", "OOXML named style; explicit number in source text", "HFUT-FMT-014; HFUT-FMT-016", "10.5 pt Heiti", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "automatic Word numbering disabled; Markdown supplies the visible number")
    add("HFUTHeading3", "HFUT Heading 3", "level-3 heading", "heading", "Normal", "楷体", "Times New Roman", "10.5", "FALSE", "left", "0", "0", "exact", "16", "TRUE", "", "OOXML named style; explicit number in source text", "HFUT-FMT-015; HFUT-FMT-016", "10.5 pt Kaiti", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "automatic Word numbering disabled; Markdown supplies the visible number")
    add("HFUTEquation", "HFUT Equation", "equation paragraph", "math", "Normal", "Times New Roman", "Times New Roman", "10.5", "FALSE", "center", "0", "0", "atLeast", "24", "FALSE", "", "OOXML named style", "HFUT-FMT-017; HFUT-FMT-023", "Word POC validated 480-twip minimum line with 80-twip before/after spacing", "VALIDATED_PROJECT_DERIVED_CANDIDATE", "WORD_POC_VALIDATED", "YES", "Microsoft Word POC-derived spacing; not a textual journal line-spacing rule; does not create or replace MathType; never auto-restore exact 16 pt")
    rows[-1]["space_before_pt"] = "4"
    rows[-1]["space_after_pt"] = "4"
    add("HFUTFigureCaption", "HFUT Figure Caption", "figure caption", "caption", "Normal", "黑体", "Times New Roman", "7.5", "TRUE", "center", "0", "0", "exact", "16", "FALSE", "", "OOXML named style", "HFUT-FIG-017", "7.5 pt Heiti centered candidate", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "caption evidence remains candidate-level")
    add("HFUTTableCaption", "HFUT Table Caption", "table caption", "caption", "Normal", "黑体", "Times New Roman", "7.5", "TRUE", "center", "0", "0", "exact", "16", "FALSE", "", "OOXML named style", "HFUT-TBL-010", "7.5 pt Heiti centered candidate", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "unit placement and continuation pending")
    add("HFUTTableContent", "HFUT Table Content", "table content", "table", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "center", "0", "0", "exact", "12", "FALSE", "", "OOXML named style", "HFUT-TBL-005; HFUT-TBL-012", "7.5 pt content; 108 twip cell margins", "STYLE_EVIDENCE_CONFIRMED", "PENDING_POC", "YES", "generic table cell alignment is a candidate")
    add("HFUTReferenceHeading", "HFUT Reference Heading", "reference heading", "bibliography", "Normal", "黑体", "Times New Roman", "10.5", "TRUE", "left", "0", "0", "exact", "16", "TRUE", "", "OOXML named style", "HFUT-REF-002", "reference section boundary", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "reference title wording is not official content")
    add("HFUTReferenceEntry", "HFUT Reference Entry", "reference entry", "bibliography", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "left", "-360", "360", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-REF-002", "7.5 pt; 14 pt exact; source hanging values 227-396", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "360 twips selected to cover [1]/[12]/[123]; PENDING_POC")
    add("HFUTAuthorBiography", "HFUT Author Biography", "author biography", "author-bio", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "left", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-WEB-025", "footer field requirement; no content supplied", "TEXTUALLY_CONFIRMED", "PENDING_WINDOWS_CHECK", "YES", "not populated in candidate")
    add("HFUTFunding", "HFUT Funding", "funding", "funding", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "left", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-WEB-026", "conditional funding requirement", "TEXTUALLY_CONFIRMED", "PENDING_WINDOWS_CHECK", "YES", "not populated; no funding invented")
    add("HFUTAcknowledgement", "HFUT Acknowledgement", "acknowledgement", "acknowledgement", "Normal", "宋体", "Times New Roman", "7.5", "FALSE", "left", "0", "0", "exact", "14", "FALSE", "", "OOXML named style", "HFUT-WEB-031", "anonymous-copy pending check", "PENDING_WINDOWS_CHECK", "PENDING_POC", "YES", "not populated")
    add("HFUTThreeLineTable", "HFUT Three Line Table", "three-line table", "table", "TableNormal", "宋体", "Times New Roman", "7.5", "FALSE", "", "0", "0", "", "", "FALSE", "", "OOXML table style", "HFUT-WEB-018; HFUT-TBL-003; HFUT-TBL-004", "canonical may legally inherit TableNormal; Pandoc output removes the parent when undefined; final layout uses direct tblW/gridCol/borders/cell properties without fixed layout", "TEXTUALLY_CONFIRMED", "WORD_POC_VALIDATED", "YES", "TableNormal and fixed layout are not journal requirements; do not force missing basedOn or tblLayout=fixed into generated output")
    add("HFUTSpecimenNotice", "HFUT Specimen Notice", "external specimen notice", "none", "Normal", "Times New Roman", "Times New Roman", "9", "TRUE", "center", "0", "0", "exact", "12", "TRUE", "", "OOXML named style", "", "external specimen governance text", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "external specimen only; not canonical manuscript content")
    add("Normal", "Normal", "base paragraph mapping", "paragraph", "", "宋体", "Times New Roman", "10.5", "FALSE", "both", "200", "0", "exact", "16", "FALSE", "", "OOXML base style", "HFUT-FMT-012; HFUT-FMT-028", "base font and body candidate", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc compatibility style")
    add("BodyText", "Body Text", "Pandoc body-text mapping", "paragraph", "HFUTBody", "宋体", "Times New Roman", "10.5", "FALSE", "both", "200", "0", "exact", "16", "FALSE", "", "Pandoc compatibility style", "HFUT-FMT-012; HFUT-FMT-028", "maps to HFUTBody", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc common-style mapping")
    add("Title", "Title", "Pandoc title mapping", "title", "HFUTTitleCN", "黑体", "Times New Roman", "15", "TRUE", "center", "0", "0", "exact", "18", "TRUE", "", "Pandoc compatibility style", "HFUT-FMT-001", "maps to HFUTTitleCN", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc common-style mapping")
    add("Subtitle", "Subtitle", "Pandoc subtitle mapping", "subtitle", "HFUTTitleEN", "Times New Roman", "Times New Roman", "14", "FALSE", "center", "0", "0", "exact", "16.8", "TRUE", "", "Pandoc compatibility style", "HFUT-FMT-008", "maps to HFUTTitleEN", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc common-style mapping")
    add("Author", "Author", "Pandoc author mapping", "author", "HFUTAuthorsEN", "Times New Roman", "Times New Roman", "10.5", "FALSE", "center", "0", "0", "exact", "15", "FALSE", "", "Pandoc compatibility style", "HFUT-FMT-009", "maps to HFUTAuthorsEN", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc common-style mapping")
    add("Abstract", "Abstract", "Pandoc abstract mapping", "abstract", "HFUTAbstractBodyEN", "Times New Roman", "Times New Roman", "10.5", "FALSE", "both", "0", "0", "exact", "14", "FALSE", "", "Pandoc compatibility style", "HFUT-FMT-010", "maps to HFUTAbstractBodyEN", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "Pandoc common-style mapping")
    add("Heading1", "Heading 1", "Pandoc level-1 heading mapping", "heading 1", "HFUTHeading1", "黑体", "Times New Roman", "14", "TRUE", "left", "0", "0", "exact", "16", "TRUE", "", "Pandoc compatibility style; explicit number in source text", "HFUT-FMT-013", "maps to HFUTHeading1", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "automatic Word numbering disabled")
    add("Heading2", "Heading 2", "Pandoc level-2 heading mapping", "heading 2", "HFUTHeading2", "黑体", "Times New Roman", "10.5", "TRUE", "left", "0", "0", "exact", "16", "TRUE", "", "Pandoc compatibility style; explicit number in source text", "HFUT-FMT-014", "maps to HFUTHeading2", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "automatic Word numbering disabled")
    add("Heading3", "Heading 3", "Pandoc level-3 heading mapping", "heading 3", "HFUTHeading3", "楷体", "Times New Roman", "10.5", "FALSE", "left", "0", "0", "exact", "16", "TRUE", "", "Pandoc compatibility style; explicit number in source text", "HFUT-FMT-015", "maps to HFUTHeading3", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "automatic Word numbering disabled")
    add("Caption", "Caption", "Pandoc caption mapping", "caption", "HFUTFigureCaption", "黑体", "Times New Roman", "7.5", "TRUE", "center", "0", "0", "exact", "16", "FALSE", "", "Pandoc compatibility style", "HFUT-FIG-017; HFUT-TBL-010", "maps to figure/table caption candidates", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "figure/table split remains semantic styles")
    add("Table", "Table", "Pandoc table mapping", "table", "HFUTTableContent", "宋体", "Times New Roman", "7.5", "FALSE", "center", "0", "0", "exact", "12", "FALSE", "", "Pandoc compatibility style", "HFUT-TBL-005", "maps to HFUTTableContent", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "border is table-style candidate")
    add("Bibliography", "Bibliography", "Pandoc bibliography mapping", "bibliography", "HFUTReferenceEntry", "宋体", "Times New Roman", "7.5", "FALSE", "left", "-360", "360", "exact", "14", "FALSE", "", "Pandoc compatibility style", "HFUT-REF-002", "maps to HFUTReferenceEntry", "PROJECT_DERIVED_CANDIDATE", "PENDING_POC", "YES", "CSL output not tested")
    return [{key: row.get(key, "") for key in fields} for row in rows]


def write_style_map() -> None:
    STYLE_MAP.parent.mkdir(parents=True, exist_ok=True)
    rows = style_map_rows()
    with STYLE_MAP.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_external_tree(root: Path, canonical_hash: str, specimen_hash: str) -> None:
    for name in ("base", "generated", "extracted_ooxml", "rendered", "logs", "metadata", "temporary_profiles"):
        (root / name).mkdir(parents=True, exist_ok=True)
    (root / "base/baseline_manifest.txt").write_text(
        "DETERMINISTIC_STANDARD_LIBRARY_OOXML_BASELINE\n"
        "NOT_OFFICIAL_ORIGINAL\nNOT_REFERENCE_DOCX_SOURCE\n\n",
        encoding="utf-8",
    )
    (root / "logs/build_sha256.txt").write_text(
        f"reference_sha256={canonical_hash}\nspecimen_sha256={specimen_hash}\n",
        encoding="utf-8",
    )
    metadata = {
        "tool": "scripts/paper/build_hfut_reference_docx.py",
        "python": "standard-library-only",
        "canonical_output": "docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx",
        "canonical_sha256": canonical_hash,
        "specimen_output": SPECIMEN_NAME,
        "specimen_sha256": specimen_hash,
        "identity": ["DERIVED_REFERENCE_DOCX_CANDIDATE", "NOT_OFFICIAL_JOURNAL_TEMPLATE", "NOT_FINAL_SUBMISSION_FILE", "PENDING_PANDOC_POC", "PENDING_MICROSOFT_WORD_REVIEW"],
    }
    (root / "metadata/build_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_content_types(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        parts = {name: archive.read(name) for name in names}
    result, errors = inspect_content_types(parts, names)
    if errors or result["default_after_override_count"] != 0:
        raise RuntimeError(f"invalid reference Content Types in {path}: {errors}")


def validate_heading_numbering(path: Path) -> None:
    errors, _ = audit_docx_heading_numbering(path, require_explicit_headings=False)
    if errors:
        raise RuntimeError(f"invalid heading-numbering contract in {path}: {errors}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--external-root", type=Path, default=DEFAULT_EXTERNAL)
    parser.add_argument("--no-specimen", action="store_true")
    args = parser.parse_args()
    write_style_map()
    canonical_hash = write_deterministic_docx(args.output, specimen=False)
    validate_content_types(args.output)
    validate_heading_numbering(args.output)
    specimen_path = args.external_root / "generated" / SPECIMEN_NAME
    specimen_hash = "NOT_GENERATED"
    if not args.no_specimen:
        specimen_hash = write_deterministic_docx(specimen_path, specimen=True)
        validate_content_types(specimen_path)
        validate_heading_numbering(specimen_path)
    make_external_tree(args.external_root, canonical_hash, specimen_hash)
    print(f"reference={args.output}")
    print(f"reference_sha256={canonical_hash}")
    if not args.no_specimen:
        print(f"specimen={specimen_path}")
        print(f"specimen_sha256={specimen_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
