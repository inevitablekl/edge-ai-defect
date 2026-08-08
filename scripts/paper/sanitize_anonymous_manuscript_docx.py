#!/usr/bin/env python3
"""Remove identity-bearing OpenXML package metadata from an anonymous DOCX."""

from __future__ import annotations

import argparse
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
CUSTOM = "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"

ET.register_namespace("cp", CP)
ET.register_namespace("dc", DC)
ET.register_namespace("dcterms", "http://purl.org/dc/terms/")
ET.register_namespace("dcmitype", "http://purl.org/dc/dcmitype/")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")


def qn(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def sanitize_core(payload: bytes) -> bytes:
    root = ET.fromstring(payload)
    creator = root.find(qn(DC, "creator"))
    if creator is not None:
        creator.text = ""
    last_modified_by = root.find(qn(CP, "lastModifiedBy"))
    if last_modified_by is not None:
        root.remove(last_modified_by)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def sanitize_app(payload: bytes) -> bytes:
    root = ET.fromstring(payload)
    application = root.find(qn(EP, "Application"))
    if application is not None:
        application.text = "Anonymous manuscript build"
    company = root.find(qn(EP, "Company"))
    if company is not None:
        company.text = ""
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def sanitize_custom(payload: bytes) -> bytes:
    root = ET.fromstring(payload)
    for property_node in list(root):
        if property_node.get("name", "") != "classification":
            root.remove(property_node)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rewrite(input_path: Path, output_path: Path) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}

    if "docProps/core.xml" not in parts or "docProps/app.xml" not in parts:
        raise ValueError("DOCX is missing required document property parts")
    parts["docProps/core.xml"] = sanitize_core(parts["docProps/core.xml"])
    parts["docProps/app.xml"] = sanitize_app(parts["docProps/app.xml"])
    if "docProps/custom.xml" in parts:
        parts["docProps/custom.xml"] = sanitize_custom(parts["docProps/custom.xml"])

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
    args = parser.parse_args()
    rewrite(args.input, args.output)
    print(f"anonymous_package_sanitize=PASS output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
