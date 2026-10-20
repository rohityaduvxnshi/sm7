# Semester 7 final report — source and build

The final Minor Project report (Amity "Project Plan" format, ETMN100 guidelines 2026-27) is generated
from the files in this folder. Edit the Markdown, rebuild, and the DOCX and PDF in `../submission/`
are regenerated; do not hand-edit the DOCX if you intend to rebuild.

## Layout

| Path | What it is |
|---|---|
| `chapters/00_abstract.md`, `00_acknowledgement.md` | Pre-page text (title page, declaration and certificate are fixed in `build/build_docx.js`) |
| `chapters/01_*.md` … `15_*.md` | Chapters 1–15 (`09a`/`09b` are the two halves of Chapter 9) |
| `chapters/A1_*.md` | Appendix A, placed after the references |
| `tables/t10_1.json`, `tables/t12_1.json` | The two landscape tables (datasets; 48-study comparison) |
| `figures/` | Figure PNGs (rendered from the SVGs at 3x) and the Amity logo cropped from the guideline scan |
| `build/` | Build scripts, checkers, and `sources/` (facts sheet and the original table rows used for checking) |

## Rebuild

```powershell
powershell -ExecutionPolicy Bypass -File sem7_minor\final_report\build\build_report.ps1
```

This runs `prep_bib.py` (references.bib → bib.json), `build_docx.js` (Markdown → DOCX, fails on a
missing citation key, a table or figure placed before it is mentioned, or a numbering gap),
`export_pdf.ps1` (Word updates the contents, list of tables and list of figures, then exports a
PDF with embedded fonts) and `check_report.py` (table cells against the original rows, cross-references,
own-results wording). Outputs: `submission/source_docx/G148_Sem7_MinorProjectReport_FINAL.docx` and
`submission/pdf/G148_Sem7_MinorProjectReport_FINAL.pdf`.

## Markup used in the chapter files

- `# 9. TITLE` chapter heading (new page), `## 9.1 Title` section heading; blank line between paragraphs.
- `[C01]` → (Wang et al., 2020); `[C01, C11]` → one grouped parenthesis; `{C01}` → Wang et al. (2020).
  Keys are the screening IDs in `references/references.bib`; the reference list is built from the keys
  actually cited, sorted alphabetically, with a/b year suffixes where labels collide.
- `- item` bullets, `1. item` numbered lists.
- `Table: 6.1 | Caption` followed by a pipe table; `[[TABLE:t12_1]]` for a landscape table;
  `[[FIGURE:prisma|8.1|Caption]]`; `[[EQ:11.1]]` for the display equations defined in `build_docx.js`.

## Similarity pre-check

`build/plag/fetch_sources.py` downloads a comparison corpus (arXiv abstracts and full texts of the
cited papers, Wikipedia pages on the core concepts) into a folder outside the repo;
`build/plag/plag_check.py <pdf> <corpus>` reports the share of the report inside runs of 8+ words
shared with that corpus. It is an indicator only — Turnitin's corpus is far larger.
