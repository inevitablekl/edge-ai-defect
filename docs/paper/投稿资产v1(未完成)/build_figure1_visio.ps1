[CmdletBinding()]
param(
    [string]$GeometryPath = (Join-Path $PSScriptRoot "figure1_geometry.json"),
    [string]$OutputPath = (Join-Path $PSScriptRoot "Figure1_input_data_path_model.vsdx")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Convert-MmToInches([double]$Millimetres) {
    return $Millimetres / 25.4
}

function Convert-HexToVisioRgb([string]$Hex) {
    if ($Hex -notmatch '^#([0-9A-Fa-f]{6})$') {
        throw "Invalid sRGB color: $Hex"
    }
    $r = [Convert]::ToInt32($Hex.Substring(1, 2), 16)
    $g = [Convert]::ToInt32($Hex.Substring(3, 2), 16)
    $b = [Convert]::ToInt32($Hex.Substring(5, 2), 16)
    return "RGB($r,$g,$b)"
}

function Set-CellFormula($Shape, [string]$CellName, [string]$Formula) {
    if ($Shape.CellExistsU($CellName, 0) -ne 0) {
        $Shape.CellsU.Item($CellName).FormulaU = $Formula
    }
}

function Add-SemanticGroupCell($Shape, [string]$GroupName) {
    if ($Shape.SectionExists(242) -eq 0) { # visSectionUser
        [void]$Shape.AddSection(242)
    }
    if ($Shape.CellExistsU("User.SemanticGroup", 0) -eq 0) {
        [void]$Shape.AddNamedRow(242, "SemanticGroup", 0)
    }
    $escaped = $GroupName.Replace('"', '""')
    $Shape.CellsU.Item("User.SemanticGroup").FormulaU = "`"$escaped`""
}

if (-not (Test-Path -LiteralPath $GeometryPath -PathType Leaf)) {
    throw "Geometry file not found: $GeometryPath"
}
$geometry = Get-Content -LiteralPath $GeometryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$pageWidthMm = [double]$geometry.page_width_mm
$pageHeightMm = [double]$geometry.page_height_mm

$visio = $null
$document = $null
try {
    $visio = New-Object -ComObject Visio.Application
    $visio.Visible = $true
    $document = $visio.Documents.Add("")
    $page = $document.Pages.Item(1)
    $page.Name = "Figure1"
    $page.PageSheet.CellsU.Item("PageWidth").FormulaU = "${pageWidthMm} mm"
    $page.PageSheet.CellsU.Item("PageHeight").FormulaU = "${pageHeightMm} mm"
    $page.PageSheet.CellsU.Item("DrawingScale").FormulaU = "1 in"
    $page.PageSheet.CellsU.Item("PageScale").FormulaU = "1 in"

    foreach ($item in ($geometry.rectangles | Sort-Object z_order)) {
        $left = Convert-MmToInches ([double]$item.x)
        $right = Convert-MmToInches ([double]$item.x + [double]$item.width)
        $bottom = Convert-MmToInches ($pageHeightMm - [double]$item.y - [double]$item.height)
        $top = Convert-MmToInches ($pageHeightMm - [double]$item.y)
        $shape = $page.DrawRectangle($left, $bottom, $right, $top)
        $shape.NameU = [string]$item.id
        Set-CellFormula $shape "FillForegnd" (Convert-HexToVisioRgb ([string]$item.fill))
        Set-CellFormula $shape "FillPattern" "1"
        if ([string]$item.stroke -eq "none") {
            Set-CellFormula $shape "LinePattern" "0"
        } else {
            Set-CellFormula $shape "LineColor" (Convert-HexToVisioRgb ([string]$item.stroke))
            Set-CellFormula $shape "LineWeight" "$([double]$item.stroke_width) mm"
        }
        if ([double]$item.corner_radius -gt 0) {
            Set-CellFormula $shape "Rounding" "$([double]$item.corner_radius) mm"
        }
        Add-SemanticGroupCell $shape ([string]$item.group)
    }

    foreach ($item in ($geometry.lines_arrows | Sort-Object z_order)) {
        $x1 = Convert-MmToInches ([double]$item.x1)
        $y1 = Convert-MmToInches ($pageHeightMm - [double]$item.y1)
        $x2 = Convert-MmToInches ([double]$item.x2)
        $y2 = Convert-MmToInches ($pageHeightMm - [double]$item.y2)
        $shape = $page.DrawLine($x1, $y1, $x2, $y2)
        $shape.NameU = [string]$item.id
        Set-CellFormula $shape "LineColor" (Convert-HexToVisioRgb ([string]$item.stroke))
        Set-CellFormula $shape "LineWeight" "$([double]$item.stroke_width) mm"
        if ([string]$item.dash -ne "solid") {
            Set-CellFormula $shape "LinePattern" "2"
        }
        Set-CellFormula $shape "BeginArrow" $(if ([string]$item.start_arrow -eq "triangle") { "4" } else { "0" })
        Set-CellFormula $shape "EndArrow" $(if ([string]$item.end_arrow -eq "triangle") { "4" } else { "0" })
        Add-SemanticGroupCell $shape ([string]$item.group)
    }

    foreach ($item in ($geometry.text_blocks | Sort-Object z_order)) {
        $left = Convert-MmToInches ([double]$item.x)
        $right = Convert-MmToInches ([double]$item.x + [double]$item.width)
        $bottom = Convert-MmToInches ($pageHeightMm - [double]$item.y - [double]$item.height)
        $top = Convert-MmToInches ($pageHeightMm - [double]$item.y)
        $shape = $page.DrawRectangle($left, $bottom, $right, $top)
        $shape.NameU = [string]$item.id
        $shape.Text = ([string]$item.text).Replace("\n", "`r")
        Set-CellFormula $shape "FillPattern" "0"
        Set-CellFormula $shape "LinePattern" "0"
        Set-CellFormula $shape "Char.Size" "$([double]$item.font_size_pt) pt"
        $fontName = if ([string]$item.Chinese_or_Latin -eq "Latin") { "Times New Roman" } else { "SimSun" }
        Set-CellFormula $shape "Char.Font" "FONT(`"$fontName`")"
        Set-CellFormula $shape "Char.Style" $(if ([bool]$item.bold -and [bool]$item.italic) { "3" } elseif ([bool]$item.bold) { "1" } elseif ([bool]$item.italic) { "2" } else { "0" })
        Set-CellFormula $shape "Para.HorzAlign" "1"
        Set-CellFormula $shape "VerticalAlign" "1"
        Set-CellFormula $shape "LeftMargin" "0 mm"
        Set-CellFormula $shape "RightMargin" "0 mm"
        Set-CellFormula $shape "TopMargin" "0 mm"
        Set-CellFormula $shape "BottomMargin" "0 mm"
        if ([string]$item.Chinese_or_Latin -eq "mixed") {
            $latinFontId = $visio.Fonts.ItemU("Times New Roman").ID
            foreach ($match in [regex]::Matches($shape.Text, '[A-Za-z0-9₀₂₃=/+%×−→. ]+')) {
                $characters = $shape.Characters
                $characters.Begin = $match.Index
                $characters.End = $match.Index + $match.Length
                $characters.CharProps(0) = $latinFontId # visCharacterFont
                [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($characters)
            }
        }
        Add-SemanticGroupCell $shape ([string]$item.group)
    }

    $fullOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
    [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($fullOutputPath))
    $document.SaveAs($fullOutputPath)
    Write-Host "CREATED=$fullOutputPath"
    Write-Host "MANUAL_QA_REQUIRED=Compare against figure1_reference.svg/png and verify every object is editable."
}
finally {
    if ($document -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) }
    if ($visio -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($visio) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
