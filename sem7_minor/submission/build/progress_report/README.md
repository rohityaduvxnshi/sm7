# Progress Report + NTCC diary builder

Generates two DOCX deliverables for the First Progress Review Presentation
(27 August 2026), then exports both to PDF:

| Output | Where |
|---|---|
| `G148_Sem7_ProjectProgressReport.docx` | `sem7_minor/submission/source_docx/` |
| `G148_Sem7_NTCC_ProjectDiary.docx` | same |
| both `.pdf` | `sem7_minor/submission/pdf/` |

## How it works

`build.py` does not lay out a document from scratch. It opens the departmental
proforma that Rohit supplied as an example, keeps the whole OOXML package
(styles, fonts, margins, table borders, heading styles, the Amity logo and its
relationship) untouched, and rewrites only `word/document.xml` with content from
`content.py` and `refs.json`. Paragraphs and table cells are cloned from the
sample's own templates, so the output is format-identical to the sample.

**The sample is a format template only.** No sentence, number, task or reference
from it is reused — see `CLAUDE.md` and the `samples-are-format-only` rule. Its
authors' names and enrolment numbers are substituted out; the build asserts this
is complete.

## Files

- `build.py` — the builder. Run it from anywhere: `python build.py`
- `content.py` — all report and diary text, the PERT chart spans, the team block
- `refs.json` — the 73 IEEE-numbered references, extracted from
  `sem7_minor/submission/manuscript.html` so they stay in step with the paper

## Dependency, deliberately not committed

`build.py` reads `Project Progress Report (1).docx` from the repository root.
That file is another student group's document and is gitignored rather than
committed, so a fresh clone needs it placed back at the root before rebuilding.

## PDF export

DOCX to PDF is a separate step (Word COM, same route as `make_docx.ps1`):

```powershell
$w = New-Object -ComObject Word.Application; $w.Visible = $false
foreach ($n in @('G148_Sem7_ProjectProgressReport','G148_Sem7_NTCC_ProjectDiary')) {
  $d = $w.Documents.Open("$PWD\..\..\source_docx\$n.docx", $false, $false)
  $d.SaveAs2("$PWD\..\..\pdf\$n.pdf", 17); $d.Close($false)
}
$w.Quit()
```

Both exports were checked against the CLAUDE.md §8 rules: selectable text, all
fonts embedded, tables legible, logo carried through.
