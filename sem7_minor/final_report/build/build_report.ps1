# Rebuilds the final report: chapters/*.md + tables/*.json -> DOCX (docx-js) -> PDF (Word), then checks.
# Usage (from any folder):  powershell -ExecutionPolicy Bypass -File <this file> [-Tag FINAL]
param([string]$Tag = 'FINAL')
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$sub = (Resolve-Path (Join-Path $here '..\..\submission')).Path
$docx = Join-Path $sub "source_docx\G148_Sem7_MinorProjectReport_$Tag.docx"
$pdf = Join-Path $sub "pdf\G148_Sem7_MinorProjectReport_$Tag.pdf"
if (-not (Test-Path (Join-Path $here 'node_modules\docx'))) { Push-Location $here; npm install --no-audit --no-fund; Pop-Location }
python (Join-Path $here 'prep_bib.py'); if ($LASTEXITCODE) { throw 'prep_bib.py failed' }
node (Join-Path $here 'build_docx.js') $docx; if ($LASTEXITCODE) { throw 'build_docx.js reported problems (see above)' }
& (Join-Path $here 'export_pdf.ps1') -Docx $docx -Pdf $pdf
python (Join-Path $here 'check_report.py'); if ($LASTEXITCODE) { throw 'check_report.py reported problems (see above)' }
Write-Output "done: $pdf"
