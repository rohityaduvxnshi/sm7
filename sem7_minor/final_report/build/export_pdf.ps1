# Opens the built DOCX in Word, updates the Table of Contents / List of Tables / List of Figures
# fields (twice, so page numbers settle after the lists grow), saves it, and exports the PDF.
param([Parameter(Mandatory = $true)][string]$Docx, [Parameter(Mandatory = $true)][string]$Pdf)
$ErrorActionPreference = 'Stop'
$Docx = (Resolve-Path $Docx).Path
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $doc = $w.Documents.Open($Docx, $false, $false)
  for ($pass = 1; $pass -le 2; $pass++) {
    $doc.Repaginate()
    for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) { $doc.TablesOfContents.Item($i).Update() }
    [void]$doc.Fields.Update()
  }
  # Word stamps theme-font (Calibri) run properties on regenerated TOC paragraphs; keep them in the body font
  for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) { $doc.TablesOfContents.Item($i).Range.Font.Name = 'Times New Roman' }
  $doc.Repaginate()
  Write-Output ("TOC fields: {0}; pages: {1}; words: {2}" -f $doc.TablesOfContents.Count, $doc.ComputeStatistics(2), $doc.ComputeStatistics(0))
  $doc.Save()
  # ExportAsFixedFormat(path, PDF=17, open=false, optimise for print=0, whole document=0, from, to,
  #                     content only=0, doc properties, keep IRM, heading bookmarks=1, structure tags,
  #                     bitmap missing fonts, PDF/A=false)
  $doc.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
  $doc.Close($false)
  Write-Output "exported $Pdf"
} finally {
  $w.Quit()
  [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($w)
}
