# -*- coding: utf-8 -*-
"""Build the Group 148 Project Progress Report and NTCC project diary as DOCX,
by splicing new content into the exact XML skeleton of the supplied sample.

Styles, fonts, margins, table borders, heading styles and the Amity logo all
come from the sample package unchanged; only word/document.xml is rewritten.
"""
import json, re, shutil, zipfile, os
import content as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# Format template only: supplied by Rohit as an example of the departmental
# proforma. No content from it is reused - layout, styles and the Amity logo only.
SAMPLE = os.path.join(ROOT, "Project Progress Report (1).docx")
OUTDIR = os.path.join(ROOT, "sem7_minor", "submission", "source_docx")

DOC = zipfile.ZipFile(SAMPLE).read("word/document.xml").decode("utf-8")
B0 = DOC.index("<w:body>") + len("<w:body>")
B1 = DOC.rindex("</w:body>")
BODY = DOC[B0:B1]
SEG = re.findall(r"<w:tbl>.*?</w:tbl>|<w:p\b[^>]*/>|<w:p\b.*?</w:p>|<w:sectPr.*?</w:sectPr>",
                 BODY, re.S)
assert len(SEG) == 82, len(SEG)

REFS = json.load(open(os.path.join(HERE, "refs.json"), encoding="utf-8"))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ppr_of(seg):
    """The <w:pPr> block of a paragraph template ('' if it has none)."""
    m = re.search(r"<w:pPr>.*?</w:pPr>", seg, re.S)
    return m.group(0) if m else ""


def run(text, rpr=""):
    return "<w:r>%s<w:t xml:space=\"preserve\">%s</w:t></w:r>" % (rpr, esc(text))


def para(tmpl, runs):
    """New paragraph with the template's paragraph properties and given runs."""
    return "<w:p>" + ppr_of(tmpl) + "".join(runs) + "</w:p>"


BOLD = "<w:rPr><w:b/></w:rPr>"
BCS = "<w:rPr><w:bCs/></w:rPr>"
BBCS = "<w:rPr><w:b/><w:bCs/></w:rPr>"

# --------------------------------------------------------------- table helpers
BORDER = ("<w:tcBorders>"
          "<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"000000\"/>"
          "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"000000\"/>"
          "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"000000\"/>"
          "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"000000\"/>"
          "</w:tcBorders>")


def tc(width, text, bold=False, sz=None, fill=None, align="left", color=None,
       symbol=False, span=None):
    pr = "<w:tcPr><w:tcW w:w=\"%d\" w:type=\"dxa\"/>" % width
    if span:
        pr += "<w:gridSpan w:val=\"%d\"/>" % span
    pr += BORDER
    if fill:
        pr += "<w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"%s\"/>" % fill
    pr += "</w:tcPr>"
    rpr = "<w:rPr>"
    if symbol:
        rpr += ("<w:rFonts w:ascii=\"Segoe UI Symbol\" w:eastAsia=\"Segoe UI Symbol\""
                " w:hAnsi=\"Segoe UI Symbol\" w:cs=\"Segoe UI Symbol\"/>")
    if bold:
        rpr += "<w:b/>"
    if color:
        rpr += "<w:color w:val=\"%s\"/>" % color
    if sz:
        rpr += "<w:sz w:val=\"%d\"/>" % sz
    rpr += "</w:rPr>"
    if rpr == "<w:rPr></w:rPr>":
        rpr = ""
    p = ("<w:p><w:pPr><w:spacing w:after=\"0\" w:line=\"259\" w:lineRule=\"auto\"/>"
         "<w:ind w:left=\"40\" w:firstLine=\"0\"/><w:jc w:val=\"%s\"/></w:pPr>%s</w:p>"
         % (align, run(text, rpr)))
    return "<w:tc>" + pr + p + "</w:tc>"


def tr(cells, height=None, header=False, cant_split=False):
    pr = ""
    if height or header or cant_split:
        pr = "<w:trPr>"
        if cant_split:
            pr += "<w:cantSplit/>"    # keep a diary entry whole on one page
        if header:
            pr += "<w:tblHeader/>"          # repeat this row at every page break
        if height:
            pr += "<w:trHeight w:val=\"%d\"/>" % height
        pr += "</w:trPr>"
    return "<w:tr>" + pr + "".join(cells) + "</w:tr>"


def table(widths, rows):
    pr = ("<w:tbl><w:tblPr><w:tblStyle w:val=\"TableGrid\"/>"
          "<w:tblW w:w=\"%d\" w:type=\"dxa\"/><w:tblInd w:w=\"6\" w:type=\"dxa\"/>"
          "<w:tblCellMar><w:top w:w=\"39\" w:type=\"dxa\"/><w:left w:w=\"48\" w:type=\"dxa\"/>"
          "<w:bottom w:w=\"39\" w:type=\"dxa\"/><w:right w:w=\"48\" w:type=\"dxa\"/></w:tblCellMar>"
          "<w:tblLook w:val=\"04A0\" w:firstRow=\"1\" w:lastRow=\"0\" w:firstColumn=\"1\""
          " w:lastColumn=\"0\" w:noHBand=\"0\" w:noVBand=\"1\"/></w:tblPr><w:tblGrid>%s</w:tblGrid>"
          % (sum(widths), "".join("<w:gridCol w:w=\"%d\"/>" % w for w in widths)))
    return pr + "".join(rows) + "</w:tbl>"


def write_docx(body_segments, out_path, title):
    new_doc = DOC[:B0] + "".join(body_segments) + DOC[B1:]
    shutil.copyfile(SAMPLE, out_path)
    # rewrite document.xml (and scrub the sample's metadata) inside the package
    src = zipfile.ZipFile(SAMPLE)
    tmp = out_path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                data = new_doc.encode("utf-8")
            elif item.filename == "docProps/core.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>%s</dc:title>" % title, s)
                s = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator>Group 148</dc:creator>", s)
                s = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>",
                           "<cp:lastModifiedBy>Group 148</cp:lastModifiedBy>", s)
                data = s.encode("utf-8")
            z.writestr(item, data)
    src.close()
    os.replace(tmp, out_path)


# =============================================================== identity block
def identity_block(subtitle_seg3=None):
    out = []
    out.append(SEG[0])                      # Amity logo
    out.append(SEG[1])
    out.append(SEG[2])                      # AMITY SCHOOL OF ENGINEERING & TECHNOLOGY
    out.append(subtitle_seg3 if subtitle_seg3 else SEG[3])
    out.append(SEG[4])                      # B. Tech (Computer Science and Engineering)
    out.append(SEG[5])
    out.append(para(SEG[6], [run("Group No: "),
                             run(C.GROUP, "<w:rPr><w:b w:val=\"0\"/></w:rPr>"),
                             run("  ")]))
    out.append(para(SEG[7], [run("Project Title: ", BOLD), run(C.TITLE_L1 + " ")]))
    out.append(para(SEG[8], [run(C.TITLE_L2 + " ")]))
    out.append(para(SEG[9], [run("Area: ", BOLD), run(C.AREA + " ")]))
    out.append(SEG[10])                     # Academic Session: 2026-27
    out.append(para(SEG[11], [run("Project Guide: ", BOLD), run(C.GUIDE)]))
    out.append(SEG[12])                     # Details of Project Team:
    out.append(SEG[13])
    # student table: reuse the sample table, substituting the three rows
    t = SEG[14]
    t = t.replace("Programme:- B.TECH CSE ", C.PROGRAMME)
    t = t.replace("Year/Semester:- 4th Year /7th Semester ", C.YEARSEM)
    subs = [("A2305223262", "Vrinda Aggarwal"), ("A2305223287", "Archita Bhattacharya"),
            ("A2305223295", "Sampoorna Singh")]
    for (old_en, old_nm), (new_en, new_nm) in zip(subs, C.STUDENTS):
        t = t.replace(old_en, new_en).replace(old_nm, new_nm)
    out.append(t)
    return out


def signature_block():
    out = []
    out.append(SEG[68])
    out.append(SEG[69])                     # Signature(s) of project team:
    out.extend(SEG[70:73])
    names = "%s(%s) \t    %s(%s) \t%s(%s) " % (
        C.STUDENTS[0][1], C.STUDENTS[0][0], C.STUDENTS[1][1], C.STUDENTS[1][0],
        C.STUDENTS[2][1], C.STUDENTS[2][0])
    sz = "<w:rPr><w:sz w:val=\"20\"/><w:szCs w:val=\"28\"/></w:rPr>"
    runs = []
    for i, part in enumerate(names.split("\t")):
        if i:
            runs.append("<w:r>%s<w:tab/></w:r>" % sz)
        runs.append(run(part, sz))
    out.append(para(SEG[73], runs))
    out.append(SEG[74])
    out.append(SEG[75])                     # Signature of project guide
    out.extend(SEG[76:79])
    out.append(para(SEG[79], [run(C.GUIDE)]))
    out.append(SEG[80])                     # Date:
    out.append(SEG[81])                     # sectPr
    return out


# ================================================= 1. Project Progress Report
def build_report():
    body = identity_block()
    body.append(SEG[15])
    body.append(SEG[16])                    # Paper Summary:
    for kind, text in C.SUMMARY:
        if kind == "h":
            body.append(para(SEG[17], [run(text, BBCS)]))
        else:
            body.append(para(SEG[18], [run(text, BCS)]))
    body.append(SEG[36])
    # start the PERT chart on a fresh page so the 14-row table is not split
    body.append(SEG[37].replace("<w:pPr>", "<w:pPr><w:pageBreakBefore/>", 1))
    body.append(SEG[38])

    W = [2900] + [546] * 12                 # 9452 twips, inside the 9414 text column
    hdr = [tc(W[0], "Task", bold=True, sz=18, fill="1F4E79", color="FFFFFF", align="center")]
    hdr += [tc(W[i + 1], "W%d" % (i + 1), bold=True, sz=18, fill="1F4E79", color="FFFFFF",
               align="center") for i in range(12)]
    rows = [tr(hdr, 375, header=True)]
    for task, weeks in C.PERT:
        cells = [tc(W[0], task, sz=16)]
        for w in range(1, 13):
            if w in weeks:
                cells.append(tc(W[w], "\u2713", sz=18, fill="2E75B6", color="FFFFFF",
                                align="center", symbol=True))
            else:
                cells.append(tc(W[w], " ", sz=20, align="center"))
        rows.append(tr(cells, 375))
    body.append(table(W, rows))

    body.append(SEG[40])
    body.append(SEG[41])
    body.append(SEG[42])                    # References heading
    body.append(SEG[43])
    for i, ref in enumerate(REFS, 1):
        body.append(para(SEG[45], [run("[%d] %s" % (i, ref))]))
    body.extend(signature_block())
    write_docx(body, os.path.join(OUTDIR, "G148_Sem7_ProjectProgressReport.docx"),
               "Project Progress Report - Group 148")


# ============================================================ 2. NTCC diary
def build_diary():
    seg3 = para(SEG[3], [run("NTCC Project Diary ", "<w:rPr><w:b/><w:sz w:val=\"28\"/></w:rPr>")])
    body = identity_block(seg3)
    body.append(SEG[15])
    body.append(para(SEG[16], [run("Project Diary:", "<w:rPr><w:b/><w:u w:val=\"single\""
                                   " w:color=\"000000\"/></w:rPr>"),
                               run("  ", BOLD)]))
    body.append(para(SEG[18], [run(
        "Record of work carried out on the minor project between 20 July 2026 and 27 August 2026, "
        "in steps of two to three days. Each entry corresponds to material held in the project's "
        "working repository.", BCS)]))
    body.append(SEG[36])

    W = [620, 1560, 5570, 1660]             # 9410 twips
    head = ["S. No.", "Duration", "Work carried out", "Signature of Guide"]
    rows = [tr([tc(W[i], head[i], bold=True, sz=18, fill="1F4E79", color="FFFFFF",
                   align="center") for i in range(4)], 375, header=True)]
    for n, (dur, work) in enumerate(C.DIARY, 1):
        rows.append(tr([tc(W[0], "%d." % n, sz=18, align="center"),
                        tc(W[1], dur, sz=18),
                        tc(W[2], work, sz=18),
                        tc(W[3], " ", sz=18)], cant_split=True))
    body.append(table(W, rows))
    body.extend(signature_block())
    write_docx(body, os.path.join(OUTDIR, "G148_Sem7_NTCC_ProjectDiary.docx"),
               "NTCC Project Diary - Group 148")


if __name__ == "__main__":
    build_report()
    build_diary()
    print("built ->", OUTDIR)
