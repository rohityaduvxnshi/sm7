# 5. REQUIREMENT ANALYSIS

In a software project, requirement analysis sets out what a system must do and the conditions it has to meet. The minor project builds no system; what it produces is a systematic review of published work on AI-generated image detection, together with the report that presents it. The requirements in this chapter therefore describe what the review process and its outputs must deliver. The functional requirements in Section 5.1 name the tasks the review has to carry out, the non-functional requirements in Section 5.2 set the qualities its outputs must have, and Sections 5.3 and 5.4 list the software and hardware the work needed.

## 5.1 Functional Requirements

- **FR1 – Search.** The review must run the eight query seeds recorded in the search protocol through the search sources the protocol names, and keep each candidate together with the page where its existence was confirmed (Section 8.1).
- **FR2 – Screening.** Every record found must be de-duplicated and then screened by its title and abstract against the inclusion and exclusion criteria fixed before collection began, with the number of records logged at each stage (Sections 8.2 and 8.3).
- **FR3 – Extraction.** For each primary study the eight extraction fields must be filled from the full text, and any cell that cannot be confirmed must be marked for verification rather than estimated (Section 8.4).
- **FR4 – Taxonomy.** Each primary detection study must be assigned to one of the five families of the taxonomy in Chapter 9 (or to two, where it belongs to both), while studies centred on a dataset or benchmark are analysed in Chapters 10, 12 and 13 instead.
- **FR5 – Datasets.** The datasets and benchmarks used across the surveyed studies must be compared side by side in one table, and their known problems must be discussed (Chapter 10).
- **FR6 – Metrics.** Each evaluation metric the review relies on must be defined by its formula, with the AI-generated image taken as the positive class, so that every quoted figure has a stated meaning (Chapter 11).
- **FR7 – Master table.** All 48 primary studies must appear in one comparison table that includes the Cross-Generator Tested? and Key Limitation columns, with every cell drawn from the extraction records (Chapter 12).
- **FR8 – Gap analysis.** The research gap and the study planned for Semester 8 must be derived from the review's findings, with each element of the planned study justified by a finding and presented only as future work (Chapter 13 and Section 14.3).
- **FR9 – Bibliography.** The review must keep one bibliography of the included references, with each entry keyed by its screening ID, and no entry may be cited until its identifier has been opened and checked (Section 8.6).
- **FR10 – Reporting.** Progress must be reported every week through a WPR on the official proforma, and the final report must be delivered in the Amity format along with the Minor Project Diary and the full set of WPRs.

## 5.2 Non-Functional Requirements

- **NFR1 – Traceability.** Every number and claim taken from the literature must lead back to a cited source, and every cell of the master table must match the extraction records.
- **NFR2 – Verifiability.** Each reference must carry a DOI, an arXiv identifier or a stable proceedings page that an evaluator can open to confirm it.
- **NFR3 – Reproducibility of the search.** The databases, query seeds, criteria and counts at each stage must be recorded in enough detail for another reader to repeat the search and the screening.
- **NFR4 – Consistency.** The same eight extraction fields must be applied to every primary study, and each metric must keep a single definition throughout the report.
- **NFR5 – Originality.** The report must be written in the team's own words, with a similarity index of no more than 15% when checked through Turnitin.
- **NFR6 – Readability.** The text must be clear to an evaluator who is not a specialist in image forensics, with technical terms explained at first use and every table and figure numbered by chapter and listed in the front matter.
- **NFR7 – Timeliness.** Each WPR must reach Amizone by the Wednesday following its week, and the final report must be uploaded by the NTCC deadline of 26 October 2026.
- **NFR8 – Maintainability.** Working files must be kept in plain-text formats (Markdown drafts, CSV records and a BibTeX reference file) so that they can be edited, compared across versions and checked by script.

## 5.3 Software Requirements

Table 5.1 lists the software and tools the work relied on, from the literature search through to the final PDF; no software licence was bought for any of them (Section 3.3).

Table: 5.1 | Software and tools used in the project
| Software / tool | Purpose |
|---|---|
| Scholarly databases and search engines named in the protocol (FR1) | Running the query seeds; confirming candidates on publisher and proceedings pages |
| CSV files | Candidate list, screening decisions and extraction table |
| BibTeX | Bibliography of the 74 included references, each keyed by its screening ID |
| arXiv, Crossref and PMLR records | Confirming each reference's identifier, title and first author |
| Visual Studio Code and Markdown | Editor and plain-text format for the chapter drafts |
| Python | Scripted checks, e.g. comparing the master table with the extraction records |
| SVG vector graphics | Drawing the three figures |
| Microsoft Word | Assembling the report and producing its PDF |
| Microsoft Edge (headless mode) | Turning each WPR proforma into a PDF |
| Poppler PDF tools | Checking PDFs for selectable text and embedded fonts |
| Git and GitHub | Version control in a private repository, adopted on 20 August 2026 |

## 5.4 Hardware Requirements

The review work was carried out on the laptop described in Table 5.2. Because a review trains no models, no GPU was needed, and the project bought no hardware (Section 3.3).

Table: 5.2 | Hardware used in the project
| Component | Specification |
|---|---|
| Processor | Intel Core i5-1135G7 |
| Memory | 16 GB RAM |
| Operating system | Windows 10 |
| Network | Ordinary internet connection |
| GPU | Not required for the review |
