# Project facts for the final report (compiled 20 October 2026 from the repo records and the Amity guidelines)

Every statement here is sourced; anything not listed here or in the other named source files must not be stated in the report.

## Project and team (CLAUDE.md section 1; diary; synopsis)
- Title: Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches (finalised 29 July 2026; submitted as the synopsis topic on Amizone on 29 July 2026).
- Programme: B.Tech, Computer Science and Engineering, 4th year / 7th semester, academic session 2026-27.
- Institution: Amity School of Engineering and Technology (ASET), Amity University Uttar Pradesh, Noida.
- Group 148. Members: Rohit Yadav (A2305223472), Vishal (A2305223568), Hardik Mehlawat (A2305223449).
- Faculty guide: Dr. Richa Gupta. No industry guide.
- Area: Artificial Intelligence and Machine Learning (Computer Vision).
- Course: Non-Teaching Credit Course (NTCC) Minor Project, code ETMN100, 4 credit units, 12 weeks.
- Project window: 20 July 2026 to 9 October 2026 (82 days, 12 weeks). Week 1 = 20-26 July; each week runs Monday-Sunday; Week 12 is short (5-9 October).
- Weekly Progress Reports (WPRs): one per week, 12 in total, uploaded on Amizone by the Wednesday after the week, on the official one-page WPR proforma, listing all three members.
- Progress reviews: First progress review presentation on 27 August 2026 (Project Progress Report 1 and the NTCC project diary prepared for it). Second progress review: Project Progress Report 2 dated 1 October 2026, covering progress to the end of Week 10. (Amity calendar windows: first review 24-27 August 2026; second review 28 September - 1 October 2026.)
- Semester 7 scope rule: the minor project is a literature review; no experiments are run and no experimental results of the team's own are reported.
- Semester 8 (major project) will carry out the experimental study that the review motivates.
- Roles: the team decided that all three members worked jointly on every work package; no per-person split is to be stated.
- Implementation track (state at most once, in Section 14.3, with no numbers): on 15 August 2026 the guide instructed the team to begin preparing the implementation code ahead of Semester 8; this runs as a separate work track that belongs to the Semester 8 major project and is reported there. Nothing else about it may appear in this report.

## What the project produced (WPR log; outline; screening summary)
- Search protocol and section outline (Week 1).
- Literature collection and screening (Week 2): 101 records identified, 26 duplicates removed, 75 unique records screened by title and abstract, 74 included (48 primary, 11 secondary, 15 background), 1 excluded (a preprint with one citation that failed the well-cited criterion).
- Full-text extraction of all 48 primary studies into an eight-field table (Week 3); ten cells first marked for verification, all resolved from the full texts; two studies' cross-generator flags changed to "No" after full-text checking.
- Reference infrastructure: a BibTeX file of the 74 included references keyed by screening ID; all 74 identifiers opened and checked against arXiv metadata records, Crossref DOI records or (for one paper) the PMLR proceedings page: 74 verified, 0 pending; one publication-year error corrected (a paper's journal version dated June 2026).
- Taxonomy: 48 primary studies assigned to five families (14 handcrafted/frequency-domain, 19 CNN-based and transfer learning, 2 transformer and attention-based, 8 multimodal and foundation-model-based, 4 explainability; 3 studies assigned to two families; 4 dataset/benchmark-focused studies analysed in the datasets, comparative and challenges parts instead).
- Review text: abstract and eight sections drafted (about 9,850 words); dataset comparison table (11 datasets); master comparison table of all 48 primary studies (checked against the extraction table by script: 48 of 48 rows matched); three figures (search-flow diagram, metrics overview, taxonomy diagram) drawn as SVG vector graphics.
- Draft v1 (generic style, IEEE numeric references, 31-page PDF) and draft v2 (journal-style two-column, author-year references, 19-page PDF, 15 August 2026). Draft v2 was submitted for the departmental plagiarism check on 15 August 2026.
- WPRs 1-12, Project Progress Reports 1 and 2, and the NTCC project diary.
- WPR 12 (5-9 October): the project window closed on 9 October; no new deliverable that week; the submission pack was reviewed; open at that point: the official report format, the plagiarism-check result, the guide's review of the draft.
- After the window (October 2026): this final report was prepared in the Amity format for submission (final report upload due on Amizone on 26 October 2026 per the NTCC calendar).

## Tools and hardware actually used (repo records)
- Scholarly databases searched: IEEE Xplore, ScienceDirect, SpringerLink, ACM Digital Library, arXiv, Google Scholar; candidates also confirmed on publisher/proceedings pages (IEEE, ACM, CVF, NeurIPS/ICML/ICLR/AAAI, PeerJ, Wiley).
- Working files: Markdown section drafts; CSV files for candidates, screening and extraction; BibTeX for references; Python scripts for consistency checks (e.g. the master table against the extraction records); SVG figures; Microsoft Word for assembling the report and exporting PDF; Microsoft Edge in headless mode for rendering the WPR proforma to PDF; Poppler PDF tools for checking selectable text and embedded fonts; Visual Studio Code as the editor; Git and a private GitHub repository for version control (adopted on 20 August 2026, during the project).
- Identifier verification sources: export.arxiv.org metadata records, api.crossref.org DOI records, the PMLR proceedings page.
- Hardware: a laptop with an Intel Core i5-1135G7 processor and 16 GB RAM running Windows 10; an ordinary internet connection; no GPU was needed for the review work.
- No hardware, software licence, dataset or paid database subscription was bought for the project.

## Amity guideline facts (MINOR PROJECT (ETMN100) guidelines, 2026-27)
- NTCC calendar: commencement 20 July 2026; synopsis, offer letter and first WPR uploaded 27 July 2026; first progress review 24-27 August 2026; second progress review 28 September - 1 October 2026; end date of NTCC 9 October 2026; online upload of the final NTCC report and completion certificate 26 October 2026 (initial report checked for plagiarism by the guide with open-source software first; final report checked through Turnitin on Amizone); NTCC committee review 27-29 October 2026; evaluation 2-6 November 2026.
- Plagiarism: the report must be in the students' own words; similarity index must not exceed 15% (Turnitin or similar); a report above 15% must be rewritten.
- Eligibility: 90% of WPRs submitted and 80% satisfactory; WPRs and the Minor Project Diary are submitted with the final report.
- Report requirements: 2 copies, spiral binding with a blue back cover.
- Writing format: English; A4; text justified; left and right margins 1.25 inch, top and bottom 1.0 inch; 1.5 line spacing (tables, figures and appendix material may be single-spaced); first line of every paragraph indented 0.5 inch; pre-pages numbered in lower-case Roman numerals centred at the bottom (first visible number ii); main text numbered 1, 2, 3 at the top right; tables and figures numbered within chapters (e.g. Table 10.1) and listed in a List of Tables and a List of Figures; references cited in text by surname and year, e.g. (Edwards, 2010), and listed alphabetically by family name with a 0.5 inch hanging indent; appendices lettered.
- Arrangement: title page, declaration, faculty guide certificate, acknowledgement, table of contents, list of tables, list of figures, abstract; text in chapters; references; appendix.
- Final assessment components: introduction and statement of the problem; review of related literature; methodology; data collection, analysis and findings; future scope and limitations; quality of work and written expression; presentation; student learning outcomes.
