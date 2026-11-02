#!/usr/bin/env bash
# Render viva_notes.html to PDF with headless Edge, then print page count and fonts. Run from Git Bash.
set -e
cd "$(dirname "$0")"
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
SRC="$(pwd -W)/viva_notes.html"
OUT="$(pwd -W)/G148_Sem7_Viva_Prep_Notes.pdf"
"$EDGE" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUT" "file:///$SRC" 2>/dev/null
pdfinfo "$OUT" | grep -E "^(Pages|Page size)"
pdffonts "$OUT"
