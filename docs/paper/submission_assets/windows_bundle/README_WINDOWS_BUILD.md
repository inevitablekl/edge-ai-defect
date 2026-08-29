# HFUT native figure Windows build bundle

## Scope

This self-contained bundle comes from the frozen scientific/reproducible master at repository commit `944bbb45da4d7675e1b80463358546e46e663b24`. Windows-side work is proprietary-object translation only.

Do not edit scientific values, regenerate scientific analysis, reinterpret the figures, infer values from previews, or replace any reference/source file. The SVG and PNG files are visual references only; they are not the required final proprietary objects.

## Verify before building

Extract the ZIP without renaming its `windows_bundle` root. From PowerShell in that directory, verify every listed bundle artifact:

```powershell
$failed = $false
Get-Content .\SHA256SUMS.txt | ForEach-Object {
    if ($_ -match '^([0-9a-f]{64})  (.+)$') {
        $expected = $Matches[1]
        $path = Join-Path $PWD ($Matches[2] -replace '/', '\')
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { Write-Error "SHA256 mismatch: $path"; $failed = $true }
    }
}
if ($failed) { throw "Bundle verification failed" }
```

`SHA256SUMS.txt` intentionally does not list itself because a checksum file cannot contain a stable checksum of its own complete contents. Source-of-record hashes are independently frozen in `bundle_manifest.json` and `validation/scientific_asset_manifest.json`.

## Windows dependencies

- 64-bit Microsoft Windows.
- Microsoft Visio Desktop with COM automation and VSDX support.
- Microsoft PowerShell 5.1 or PowerShell 7 running in a Windows desktop session.
- Origin Desktop with Python automation support and the matching `originpro` package. Use the Python environment configured for that installed Origin release.
- Windows fonts `宋体`/SimSun and Times New Roman.

No proprietary output was built or claimed on Jetson Linux. The recipes have only been statically syntax-checked there.

## Build order

1. Build F1 in Visio:

   ```powershell
   Set-Location .\figure1_visio
   powershell -ExecutionPolicy Bypass -File .\build_figure1_visio.ps1
   ```

   Expected output: `Figure1_input_data_path_model.vsdx`.

2. Build F2 in the Windows Python environment connected to Origin:

   ```powershell
   Set-Location ..\figure2_origin
   python .\build_figure2_origin.py
   ```

   Expected output: `Figure2_E2E_performance.opju` plus preview exports where supported.

3. Build F3:

   ```powershell
   Set-Location ..\figure3_origin
   python .\build_figure3_origin.py
   ```

   Expected output: `Figure3_run_level_distribution.opju` plus preview exports where supported.

4. Export native-page PNG and PDF previews from Visio/Origin if automation did not export them.
5. Compare each native result at 100% zoom against its bundled SVG and PNG references. Inspect text, axes, tick positions, color/hatch/marker distinction, annotation wording, and panel geometry.
6. Save the VSDX/OPJU only after the native-object checks in `validation/expected_output_contract.md` pass.

## Font and manual QA boundary

F1 uses 8 pt internal text. F2/F3 use 7.5 pt figure text. Chinese must target SimSun and Latin must target Times New Roman. Origin/Visio releases can differ in mixed-run font and hatch property exposure; if a script emits an API warning, use the JSON specification—not the preview image—to apply the stated native property, then record that manual translation adjustment. Never change data or displayed precision.

After validation, copy each native figure page/object into the user's manually formatted Word submission document. Do not rebuild or modify the repository Word master, MathType objects, pagination, or manuscript scientific content.
