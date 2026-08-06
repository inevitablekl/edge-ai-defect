# Paper Phase 2.5 OpenXML Validator Report

## 1. Official Toolchain

The validator is a repository-external .NET console tool using the official
NuGet package `DocumentFormat.OpenXml` version `3.5.1`.

```text
SDK: .NET 10.0.302
RID: linux-arm64
SDK install: /home/orin/paper-tools/dotnet/
SDK archive SHA256: 1c56318e4099990719f6369184e08bbad0248c09c5ad7532d2516e3cdfc3ab6d
Package SHA256: 71375a11a53eeb554005477ce6ca127909aebed474900e92298360b49a68307f
Target: FileFormatVersions.Office2019
```

The SDK URL was
`https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.302/dotnet-sdk-10.0.302-linux-arm64.tar.gz`.
The tool project and NuGet cache remain outside Git.

## 2. Frozen Pre-Repair Results

Validation JSON is outside the repository at
`/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7e_openxml_schema_validation_v1/validation/`.

| Package | Official errors | Main categories |
|---|---:|---|
| original v5 Full | 26 | 12 table-cell order; 1 table-style order; 2 negative `firstLine`; 7 font-table; 4 theme |
| original v5 Anonymous | 26 | same schema set as Full |
| pre-repair canonical reference | 58 | 46 styles; 7 font-table; 4 theme; 1 settings |

The complete per-error records contain `Id`, `ErrorType`, `Description`,
`Part.Uri`, `Path.XPath`, `Node.LocalName`, and `RelatedNode`.

## 3. Fixed Results

| Package | Official error count | Result JSON |
|---|---:|---|
| canonical reference | 0 | `reference_fixed_openxml_errors.json` |
| Full v6 | 0 | `v6_full_openxml_errors.json` |
| Anonymous v6 | 0 | `v6_anonymous_openxml_errors.json` |

The file `reference_openxml_errors.json` intentionally remains the frozen
pre-repair canonical baseline; it is not the fixed result.

## 4. Validator Contract

The external tool opens `WordprocessingDocument`, runs `OpenXmlValidator` for
Office 2019, writes JSON, and returns `0` for zero errors, `1` for validation
errors, and `2` for tool/runtime failure. It is not replaced by the custom
Inspector.
