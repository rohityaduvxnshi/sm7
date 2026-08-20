$ErrorActionPreference = 'Stop'
$src = 'C:\Users\rohit\Desktop\AuthentiScan\sem7_minor\submission\manuscript_v2.html'
$out = 'C:\Users\rohit\Desktop\AuthentiScan\sem7_minor\submission\source_docx\G148_Sem7_MinorProjectReport_draft_v2.docx'

$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$doc = $w.Documents.Open($src, $false, $false)

# embed linked images
Write-Output "inline shapes: $($doc.InlineShapes.Count)  shapes: $($doc.Shapes.Count)"
$n = 0
for ($i = 1; $i -le $doc.InlineShapes.Count; $i++) {
  $s = $doc.InlineShapes.Item($i)
  Write-Output ("  shape {0} type {1}" -f $i, $s.Type)
  try {
    $s.LinkFormat.SavePictureWithDocument = $true
    $s.LinkFormat.BreakLink()
    $n++
  } catch { Write-Output ("  no link on shape {0}" -f $i) }
}
Write-Output "images embedded: $n"

# page setup: A4, 2 cm margins
$ps = $doc.PageSetup
$ps.PaperSize = 7
$ps.TopMargin = $w.CentimetersToPoints(2)
$ps.BottomMargin = $w.CentimetersToPoints(2)
$ps.LeftMargin = $w.CentimetersToPoints(2)
$ps.RightMargin = $w.CentimetersToPoints(2)

# continuous section break before "1. Introduction" so the body can be 2-column
$intro = $null
foreach ($p in $doc.Paragraphs) {
  $t = $p.Range.Text.Trim()
  if ($t -eq '1. Introduction') { $intro = $p; break }
}
if ($intro -ne $null) {
  $r = $intro.Range
  $r.Collapse(1)
  $r.InsertBreak(3)   # wdSectionBreakContinuous
  Write-Output "section break inserted; sections: $($doc.Sections.Count)"
  $body = $doc.Sections.Item($doc.Sections.Count)
  $body.PageSetup.TextColumns.SetCount(2)
  $body.PageSetup.TextColumns.Spacing = $w.CentimetersToPoints(0.6)
  $body.PageSetup.TextColumns.EvenlySpaced = $true
  Write-Output "body columns: $($body.PageSetup.TextColumns.Count)"
} else {
  Write-Output "HEADING NOT FOUND - shipping single column"
}

$doc.SaveAs2($out, 16)
Write-Output "pages: $($doc.ComputeStatistics(2)) words: $($doc.ComputeStatistics(0))"
$doc.Close($false)
$w.Quit()
Write-Output "saved $out"
