# 2. GOALS AND OBJECTIVES

## 2.1 Project Goals and Objectives

The project aimed to collect, check and bring together the published evidence on deep-learning detection of AI-generated images, so that both what is known and what is still missing become clear. Two questions were given particular weight. The first is cross-generator generalisation: does a detector that learnt from the images of one generator still work on generators it never saw during training? The second is explainability: can a person see why a detector labelled an image as real or generated? The gaps that the evidence leaves open were then to shape the experiment that the team will run in its Semester 8 major project. The four broad objectives of the synopsis were broken down into nine concrete steps:

1. To write the search protocol, with its databases, query seeds and inclusion and exclusion criteria, before any literature was collected, so that later decisions followed fixed rules (Sections 8.1 and 8.2).
2. To run eight fixed query seeds, among them "synthetic image detection", "CIFAKE" and "cross-generator generalization", through the search sources named in the protocol (Section 8.1).
3. To screen every unique record on its title and abstract and to note how many records remained after each stage, from identification to final inclusion (Section 8.3).
4. To read each of the 48 primary studies in full and log it in an extraction table of eight fixed fields, from the detection approach and architecture to the reported accuracy or AUC (area under the ROC curve) and the key limitation (Section 8.4).
5. To sort the primary detection studies into a taxonomy of five families, running from handcrafted and frequency-domain forensics to work on explainability (Section 8.5 and Chapter 9).
6. To compare the datasets and benchmarks used to test detectors, and the metrics through which the surveyed studies report their results (Chapters 10 and 11).
7. To build a master comparison table whose *Cross-Generator Tested?* and *Key Limitation* columns show, study by study, whether a detector was tried on unseen generators and where it falls short (Chapter 12).
8. To analyse the open challenges and state the research gap clearly enough to define the Semester 8 study (Chapter 13 and Section 14.3).
9. To check the identifier of every included reference, whether a DOI, an arXiv ID or a proceedings page, so that the reference list holds no unverified entry (Section 8.6).

## 2.2 Project Deliverables

The project produced the deliverables below; for tables and figures that appear in this report, the chapter is given in brackets.

- This final report, prepared in the Amity report format in October 2026, once the twelve-week window had ended on 9 October.
- The master comparison table of the 48 primary studies (Chapter 12); a script compared each of its rows with the extraction records, and all 48 matched.
- The dataset comparison table, which sets 11 datasets side by side (Chapter 10).
- Three figures drawn as SVG vector graphics: the flow of records through search and screening (Chapter 8), the taxonomy of detection approaches (Chapter 9) and an overview of the evaluation metrics (Chapter 11).
- The screening and extraction records, kept as CSV files: the 75 screened candidates with the decision taken on each, and the eight-field extraction table for the 48 primary studies.
- A BibTeX database holding the 74 included references under their screening IDs; every one of its 74 identifiers was confirmed against an arXiv, Crossref or PMLR record.
- The twelve weekly progress reports on the official one-page proforma, the reports for the first and second progress reviews (Project Progress Reports 1 and 2, dated 27 August and 1 October 2026), and the NTCC project diary.
