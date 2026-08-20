# Reference verification log

Required by CLAUDE.md Section 10 (citation integrity). One line per reference in
`references.bib`. A line records that the reference's identifier was actually
opened and that the title and first author matched the row in `screened.csv` /
`candidates.csv`.

**Rule: no citation enters the paper unless its line below reads `verified`.**
A `pending` line means the identifier has not yet been opened by anyone on the
team; it must be closed in the Week 11 verification pass or the reference is
dropped from the reference list.

How the checks below were made on 12 August 2026:

- **arXiv record** — the paper's arXiv metadata record was retrieved from
  `export.arxiv.org` (the same record served by `https://arxiv.org/abs/<ID>`)
  and its title and author list compared against the repo row.
- **Crossref DOI record** — the DOI's registered metadata was retrieved from
  `api.crossref.org/works/<DOI>`, confirming the DOI exists and that its
  registered title, authors, venue, volume and pages match the repo row.
- **PMLR proceedings page** — the publisher's proceedings page was opened
  (used for C32, which carries no DOI).
- Six entries (C01, C24, C36, C39, C51, C61) were also spot-checked in Week 2
  by opening the arXiv abstract page directly; that is noted in their rows.

C65 (TruthLens, arXiv:2503.15867) is excluded by the screening protocol, has no
entry in `references.bib`, and is therefore not listed below.

| ID | Identifier (DOI / arXiv) | Verified via | Date | Status |
|---|---|---|---|---|
| C01 | arXiv:1912.11035 | arXiv record (also spot-checked Week 2) | 12 Aug 2026 | verified |
| C02 | arXiv:2008.10588 | arXiv record | 12 Aug 2026 | verified |
| C03 | arXiv:2104.02617 | arXiv record | 12 Aug 2026 | verified |
| C04 | arXiv:1811.08180 | arXiv record | 12 Aug 2026 | verified |
| C05 | arXiv:1812.11842 | arXiv record | 12 Aug 2026 | verified |
| C06 | arXiv:1907.06515 | arXiv record | 12 Aug 2026 | verified |
| C07 | arXiv:2003.08685 | arXiv record | 12 Aug 2026 | verified |
| C08 | arXiv:2003.01826 | arXiv record | 12 Aug 2026 | verified |
| C09 | arXiv:2002.00133 | arXiv record | 12 Aug 2026 | verified |
| C10 | arXiv:1903.06836 | arXiv record | 12 Aug 2026 | verified |
| C11 | arXiv:2112.12606 | arXiv record | 12 Aug 2026 | verified |
| C12 | arXiv:2202.03347 | arXiv record | 12 Aug 2026 | verified |
| C13 | arXiv:2203.02246 | arXiv record | 12 Aug 2026 | verified |
| C14 | arXiv:2203.13964 | arXiv record | 12 Aug 2026 | verified |
| C15 | 10.1109/CVPR52729.2023.01165 | Crossref DOI record (no arXiv version exists) | 12 Aug 2026 | verified |
| C16 | arXiv:2312.10461 | arXiv record | 12 Aug 2026 | verified |
| C17 | arXiv:1911.00686 | arXiv record | 12 Aug 2026 | verified |
| C18 | arXiv:1911.06465 | arXiv record (journal-ref gives NeurIPS 33, pp. 3022-3032) | 12 Aug 2026 | verified |
| C19 | arXiv:2103.17195 | arXiv record | 12 Aug 2026 | verified |
| C20 | arXiv:2111.02447 | arXiv record | 12 Aug 2026 | verified |
| C21 | arXiv:2109.00911 | arXiv record | 12 Aug 2026 | verified |
| C22 | arXiv:2403.07240 | arXiv record | 12 Aug 2026 | verified |
| C23 | arXiv:2210.14571 | arXiv record | 12 Aug 2026 | verified |
| C24 | arXiv:2211.00680 | arXiv record (also spot-checked Week 2) | 12 Aug 2026 | verified |
| C25 | arXiv:2303.09295 | arXiv record | 12 Aug 2026 | verified |
| C26 | arXiv:2210.06998; 10.1145/3576915.3616588 | arXiv record + Crossref DOI record | 12 Aug 2026 | verified |
| C27 | arXiv:2307.06272 | arXiv record | 12 Aug 2026 | verified |
| C28 | arXiv:2401.17879 | arXiv record | 12 Aug 2026 | verified |
| C29 | arXiv:2403.17465 | arXiv record | 12 Aug 2026 | verified |
| C30 | arXiv:2304.06408 | arXiv record | 12 Aug 2026 | verified |
| C31 | arXiv:2403.17608 | arXiv record | 12 Aug 2026 | verified |
| C32 | PMLR 235:7621-7639 (no DOI) | PMLR proceedings page (publisher BibTeX) | 12 Aug 2026 | verified |
| C33 | arXiv:2406.08603 | arXiv record (journal-ref gives CVPR 2024) | 12 Aug 2026 | verified |
| C34 | arXiv:2409.15875 | arXiv record | 12 Aug 2026 | verified |
| C35 | arXiv:2411.04125 | arXiv record (journal-ref gives CVPR 2025, pp. 8245-8257) | 12 Aug 2026 | verified |
| C36 | arXiv:2406.19435 | arXiv record (also spot-checked Week 2) | 12 Aug 2026 | verified |
| C37 | arXiv:2302.10174 | arXiv record | 12 Aug 2026 | verified |
| C38 | arXiv:2312.00195 | arXiv record | 12 Aug 2026 | verified |
| C39 | arXiv:2402.19091 | arXiv record (also spot-checked Week 2) | 12 Aug 2026 | verified |
| C40 | arXiv:2312.16649 | arXiv record | 12 Aug 2026 | verified |
| C41 | arXiv:2408.09647 | arXiv record | 12 Aug 2026 | verified |
| C42 | arXiv:2310.17419 | arXiv record | 12 Aug 2026 | verified |
| C43 | arXiv:2402.12927 | arXiv record | 12 Aug 2026 | verified |
| C44 | arXiv:2206.13829; 10.1145/3512732.3533582 | arXiv record + Crossref DOI record | 12 Aug 2026 | verified |
| C45 | 10.7717/peerj-cs.2127 | Crossref DOI record | 12 Aug 2026 | verified |
| C46 | 10.1111/exsy.13829 | Crossref DOI record | 12 Aug 2026 | verified |
| C47 | arXiv:2404.04883 | arXiv record | 12 Aug 2026 | verified |
| C48 | arXiv:2411.15633 | arXiv record | 12 Aug 2026 | verified |
| C49 | arXiv:2407.20337 | arXiv record | 12 Aug 2026 | verified |
| C50 | 10.1109/TAI.2025.3641104 (preprint arXiv:2305.13800) | Crossref DOI record + arXiv record of the preprint | 12 Aug 2026 | verified (year discrepancy, see note 1) |
| C51 | arXiv:2303.14126; 10.1109/ACCESS.2024.3356122 | arXiv record (also spot-checked Week 2) + Crossref DOI record | 12 Aug 2026 | verified |
| C52 | arXiv:2306.08571 | arXiv record | 12 Aug 2026 | verified |
| C53 | arXiv:2302.11970 | arXiv record | 12 Aug 2026 | verified |
| C54 | arXiv:2402.11843; 10.1609/aaai.v39i4.32363 | arXiv record + Crossref DOI record | 12 Aug 2026 | verified (title/author discrepancy, see note 2) |
| C55 | 10.1109/OJSP.2023.3337714 | Crossref DOI record | 12 Aug 2026 | verified |
| C56 | arXiv:2306.08310 | arXiv record | 12 Aug 2026 | verified |
| C57 | arXiv:2405.00196 | arXiv record | 12 Aug 2026 | verified |
| C58 | arXiv:2402.00045 | arXiv record | 12 Aug 2026 | verified |
| C59 | arXiv:2202.07145 | arXiv record | 12 Aug 2026 | verified |
| C60 | arXiv:2001.06564; 10.1109/JSTSP.2020.3002101 | arXiv record + Crossref DOI record | 12 Aug 2026 | verified |
| C61 | arXiv:1610.02391 | arXiv record (also spot-checked Week 2) | 12 Aug 2026 | verified |
| C62 | arXiv:1710.11063; 10.1109/WACV.2018.00097 | arXiv record + Crossref DOI record | 12 Aug 2026 | verified (title discrepancy, see note 3) |
| C63 | arXiv:2404.18649 | arXiv record | 12 Aug 2026 | verified |
| C64 | 10.1109/ICCVW60793.2023.00053 | Crossref DOI record | 12 Aug 2026 | verified |
| C66 | arXiv:1406.2661 | arXiv record | 12 Aug 2026 | verified |
| C67 | arXiv:1912.04958 | arXiv record | 12 Aug 2026 | verified |
| C68 | arXiv:2006.11239 | arXiv record | 12 Aug 2026 | verified |
| C69 | arXiv:2112.10752 | arXiv record | 12 Aug 2026 | verified |
| C70 | arXiv:2010.11929 | arXiv record | 12 Aug 2026 | verified |
| C71 | arXiv:2103.00020 | arXiv record | 12 Aug 2026 | verified |
| C72 | arXiv:1512.03385 | arXiv record | 12 Aug 2026 | verified |
| C73 | arXiv:1608.06993 | arXiv record | 12 Aug 2026 | verified |
| C74 | arXiv:1905.11946 | arXiv record | 12 Aug 2026 | verified |
| C75 | arXiv:1409.1556 | arXiv record | 12 Aug 2026 | verified |

**Totals: 74 references, 74 verified, 0 pending.**

## Discrepancies found during verification (12 August 2026)

1. **C50 (LASTED) — year.** `screened.csv` records 2025. The Crossref record for
   DOI 10.1109/TAI.2025.3641104 gives IEEE Transactions on Artificial
   Intelligence, vol. 7, no. 6, pp. 3485-3496, issue date June 2026 (the 2025 in
   the DOI string is the acceptance year). `references.bib` uses 2026, the year
   the DOI resolves to. RESOLVED 12 Aug 2026: 2026 adopted after an independent
   Crossref re-check; `screened.csv` and `candidates.csv` reconciled the same day.
   The study stays inside the 2019-2026 inclusion window. Rohit may override.

2. **C54 (WildFake) — title and author list.** arXiv:2402.11843 (v1, 2024) is
   titled "WildFake: A Large-scale Challenging Dataset for AI-Generated Images
   Detection" with two authors (Yan Hong, Jianfu Zhang). The published AAAI 2025
   version, DOI 10.1609/aaai.v39i4.32363, is titled "WildFake: A Large-Scale and
   Hierarchical Dataset for AI-Generated Images Detection" with seven authors.
   `references.bib` cites the published AAAI version, which matches the title in
   `screened.csv`.

3. **C62 (Grad-CAM++) — title and one author spelling.** arXiv:1710.11063 is
   titled "Grad-CAM++: Improved Visual Explanations for Deep Convolutional
   Networks"; the published WACV 2018 version (DOI 10.1109/WACV.2018.00097) is
   titled "Grad-CAM++: Generalized Gradient-Based Visual Explanations for Deep
   Convolutional Networks". `references.bib` uses the published title. The IEEE
   record also spells the first author "Chattopadhay"; the author-supplied arXiv
   spelling "Chattopadhyay" is used.

4. **C60 (Verdoliva) — capitalisation only.** arXiv titles the paper "Media
   Forensics and DeepFakes: an overview"; the published IEEE JSTSP title is
   "Media Forensics and DeepFakes: An Overview". No substantive difference.

## Identifiers newly confirmed during this pass

These DOIs were not recorded in `screened.csv` / `candidates.csv` and were
confirmed from the Crossref record while building the bib. They are safe to copy
back into the CSVs:

| ID | Newly confirmed identifier | Publication details confirmed |
|---|---|---|
| C26 | 10.1145/3576915.3616588 | ACM CCS 2023, pp. 3418-3432 |
| C44 | 10.1145/3512732.3533582 | 1st Int. Workshop on Multimedia AI against Disinformation (MAD), 2022, pp. 52-58 |
| C51 | 10.1109/ACCESS.2024.3356122 | IEEE Access, vol. 12, pp. 15642-15650, 2024 |
| C54 | 10.1609/aaai.v39i4.32363 | AAAI 2025, vol. 39, no. 4, pp. 3500-3508 |
| C60 | 10.1109/JSTSP.2020.3002101 | IEEE JSTSP, vol. 14, no. 5, pp. 910-932, 2020 |
| C62 | 10.1109/WACV.2018.00097 | WACV 2018, pp. 839-847 |

## Still to close in the Week 11 pass

Identifiers are all verified, but for the entries below the **venue** in
`references.bib` rests on the Week 2 collection record only — the fetched arXiv
record carried no journal-ref or acceptance comment, and there is no DOI. Confirm
the proceedings name and year (and add page numbers where the publisher lists
them) before the reference list is frozen:

C02, C03, C05, C08, C09, C10, C11, C12, C13, C14, C16, C20, C21, C24, C25, C30,
C31, C34, C36, C37, C38, C40, C41, C43, C48, C52, C53, C56, C57, C66, C67, C68,
C71, C72, C75.

Page numbers are omitted throughout `references.bib` wherever no source stated
them. Missing page ranges are a formatting gap to fill in Week 11, not a
citation-integrity problem; invented page numbers would be.

## Extraction-VALUE re-check status (12 Aug 2026, reviewer pass)

Identifier verification above is complete (74/74). Separately, the 10 extraction-table
cells resolved on 12 Aug 2026 were re-checked against the papers' full text by the reviewer:

- C05, C07, C29, C40 — re-verified directly (ar5iv full text; quotes matched verbatim).
- C15 — indirectly confirmed: Table 3 values (86.3 ACC / 92.7 AP) arithmetically reproduce
  the abstract's independently-extracted "+11.4 ACC / +13.4 AP over FrePGAN (74.9/79.3)".
- C32, C64 — resolved by the work agent from the PMLR/CVF PDFs with exact section/table
  pointers; direct re-check still open because those PDFs resist local text extraction
  (CVF blocks fetch tools; Word PDF conversion unavailable). To close: open the two PDFs
  in a browser and check DRCT Sec. 5 "Limitations" and Aghasanli Tables 1-3 / Sec. 4.2.
  Estimated five minutes by hand. Until then these two rows carry a residual-risk flag.

**UPDATE 15 Aug 2026:** C32 and C64 re-checked directly from the papers' full text
(poppler pdftotext over the PMLR and CVF PDFs). DRCT Sec. 5 Limitations: both clauses
confirmed verbatim (smaller gain on GAN images; globally- vs locally-generated scope).
Aghasanli Tables 1-3: all six within-dataset values (99.5/96.7/99.7/99.4, SVM 93.0-97.2)
and both cross-dataset values (81.3/84.0) confirmed; datasets built with Latent/Stable
Diffusion, supporting the "same generator both sides" reading. The residual-risk flag
above is closed. All 10 resolved extraction cells are now reviewer-verified.
