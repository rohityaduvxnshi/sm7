# AuthentiScan — Project Brief and Operating Manual for Claude Code

**Purpose of this file:** This is the permanent context document for a two-semester B.Tech final-year project. Read it fully before doing any work. Treat it as the single source of truth for scope, deliverables, standards, and schedule. If a request in chat conflicts with this file, say so before acting.

**Status flag:** Sections marked `[CONFIRMED]` are settled facts. Sections marked `[ASSUMED]` are working assumptions that must be verified with the guide before they are relied on. Sections marked `[UNKNOWN]` are missing data — do not invent values for these.

---

## 0. How Claude Code must use this file

1. Load this file at the start of every session. Do not re-derive the plan from memory.
2. Before any deliverable, restate which week of the plan you are executing and which deliverable you are producing.
3. Never mark a week complete without producing the artefact listed for that week.
4. Never fabricate: no invented citations, DOIs, author names, accuracy figures, dataset sizes, or dates. If a number is not verified, write `[VERIFY]` next to it and list it in the open-items log.
5. Keep all output at student level, not at senior-researcher level. The work must be plausibly written by a final-year B.Tech student.
6. No emojis. No motivational language. No filler.

---

## 1. Who you are working with `[CONFIRMED]`

| Field | Value |
|---|---|
| Primary user | Rohit |
| Programme | B.Tech, Computer Science and Engineering, final year |
| Institution | Amity University Uttar Pradesh — Amity School of Engineering and Technology (ASET) |
| Group number | Group 148 |
| Semester code on synopsis | IV/VII (as recorded on the submitted Amity synopsis) |
| Project guide | Dr. Richa Gupta (designation `[UNKNOWN]` — needed for offer letters) |
| Team members | Rohit Yadav — roll 472, A2305223472, rohit.yadav15@s.amity.edu; Vishal — roll 568 `[ASSUMED]`, A2305223568, vishal25@s.amity.edu; Hardik Mehlawat — roll 449 `[ASSUMED]`, A2305223449, hardik.mehlawat@s.amity.edu |
| NTCC course / window | Minor Project ETMN100, 20 July 2026 – 9 October 2026 (82 days, 12 weeks) `[CONFIRMED]` |
| Working title | AuthentiScan (internal only — never on submission documents) |

Rolls 568/449 are derived from the last three enrollment digits (pattern matches Rohit's 472) — confirm once before any submission that lists them.

### User working preferences (apply to every response)

- Straight, strict, practical, objective. Tell what is good, bad, risky, or not worth doing.
- Separate confirmed facts from assumptions explicitly.
- If data is missing, state exactly what is missing rather than guessing.
- Do only what is asked. Do not expand scope unilaterally.
- Prefer simple, clean, working, beginner-understandable solutions. Do not over-engineer.
- Preserve existing logic unless a change is requested. Warn clearly if a change may break something.
- Recheck important reasoning before answering.
- Preferred explanation register: plain-language explanation with correct technical terms woven in naturally (the "middle register"). Not dumbed down, not jargon-dense.
- `[CONFIRMED — Rohit, 22 Aug 2026; amended same day]` **Execution split:** Claude makes the file changes, verifies locally, and **commits/pushes to git itself — without a Claude co-author line in commit messages**. Everything that spends quota or reaches a portal stays with Rohit: Kaggle pushes/launches (a push auto-starts a run), Amizone uploads, and any submission. Automated push/retry loops against Kaggle remain out; hand over ready-to-run commands for those instead.

### Role split within the team `[UNKNOWN]`

Not yet defined. Ask Rohit for the split before assigning tasks to Vishal or Hardik in any WPR. Do not assume roles.

---

## 2. The project `[CONFIRMED]`

### Topic

**AI-generated image detection** — binary classification of images as *real* (camera-captured) vs *AI-generated* (synthesised by GANs or diffusion models).

### Why this topic matters (the framing to use in writing)

Generative models have made synthetic imagery cheap, fast, and visually indistinguishable from photographs to an untrained human eye. This creates concrete downstream problems: misinformation, fabricated evidence, identity fraud, synthetic media in journalism, and contamination of training datasets scraped from the web. Automated detection is therefore a practical need, not an academic curiosity. The technical difficulty is that detectors trained on one generator family often fail on another — this generalisation gap is the central open problem in the field and is the intellectual hook for both papers.

### Technical approach (the implementation plan, executed in Semester 8)

- **Paradigm:** transfer learning from ImageNet-pretrained backbones.
- **CNN architectures (four):** ResNet50, DenseNet121, EfficientNet-B0, VGG19.
- **Benchmark model:** a Vision Transformer (ViT), used as a comparison point against the CNN family.
- **Explainability:** Grad-CAM, to visualise which image regions drive the real/fake decision.
- **Primary dataset:** CIFAKE.
- **Optional secondary dataset:** GenImage, used for cross-generator generalisation testing (test on generators not seen during training).

### What is explicitly out of scope

- Video deepfake detection.
- Audio detection.
- Building a deployed web product or mobile app.
- Any real-time or production system.

---

## 3. Two-semester structure `[CONFIRMED]`

| | Semester 7 (now) | Semester 8 |
|---|---|---|
| Project classification | Minor Project | Major Project |
| Deliverable type | Research-paper-style report only | Full implementation + major project report |
| Working demo required | **No** | Yes |
| Presentation required | **No** | Yes (assume standard viva/demo) `[ASSUMED]` |
| Paper produced | **Paper 1 — Review / Survey paper** | **Paper 2 — Experimental implementation paper** |
| Code written | None required | All of it |
| WPR track | Minor Project WPR | Major Project WPR |

**The single most important constraint for this semester:** Semester 7 is the *literature* semester. No experiments are run. No results are produced. Paper 1 must never claim that the team trained, tested, or measured anything. It surveys and analyses what others have published, and ends by identifying the gap that Semester 8 will fill.

If any draft text implies the team obtained its own experimental results this semester, that is a hard error. Flag and remove it.

**Amendment `[CONFIRMED — guide instruction, 15 August 2026]`:** Dr. Richa Gupta has instructed the team to begin preparing the implementation code now, ahead of the original Semester 8 start. This pulls the Setup/early-coding phases of §6 into the Semester 7 calendar. It does **not** change Paper 1: the review paper (draft v2 submitted for plagiarism check on 15 Aug 2026) reports no experimental results, and no number produced by early code may be added to it. All results belong to Paper 2 and the Semester 8 major report. The no-results rule above now protects Paper 1 specifically, not the calendar.

### Publication goal `[CONFIRMED — amended 25 Aug 2026, guide-approved]`

**One co-authored research paper**, merging the Semester 7 review (Paper 1) and the Semester 8 experimental work (Paper 2). The two semester projects stay fully separate on the Amity side — separate reports, separate WPR tracks — but the external publication is a single merged paper. Paper 1 and Paper 2 are still both drafted in full (Paper 1 is the Sem 7 report; Paper 2 is the core of the Sem 8 report); neither is submitted to a venue on its own. Merge pipeline: `sem8_major/implementation_plan.md` §10. The merged paper's shape (hybrid review+experiment vs experimental paper with deep related work) is deliberately undecided until major-project development completes (Rohit, 25 Aug 2026). Target venue not yet chosen — see open items.

---

## 4. Reference paper schema (extracted from the three uploaded papers)

Three published journal papers were supplied as structural and stylistic templates. They are real peer-reviewed papers, not student reports, so treat them as the *ceiling* for structure and the *reference point* for section ordering — not as a standard the writing quality must match exactly.

### Paper A — Karki et al. (2024), *Scientia Horticulturae* 332:113241
"Strawberry disease detection using transfer learning of deep convolutional neural networks."

- Four ImageNet-pretrained CNNs: VGG19, InceptionV3, ResNet50, DenseNet121.
- Three configurations compared: feature extraction (frozen base), fine-tuning (full update), and training from scratch without transfer learning.
- Dataset: 3,271 original images augmented to 22,897; 8 classes; 80/10/10 split.
- Setup reported explicitly: PyTorch 2.1.0, SGD, learning rate 0.01, 200 epochs, exact CPU/RAM/GPU specification.
- Metrics: accuracy, precision, recall, F1, AUC — with formulas written out as numbered equations.
- Result artefacts: per-configuration metric tables, class-wise metric tables, confusion matrices, per-class ROC curves, learning curves, and a table of depth / model size / trainable parameters / training time.
- Best result: ResNet-50 fine-tuned, 94.4% accuracy.

**This is the direct template for Paper 2 (Semester 8).**

### Paper B — Deshmukh et al. (2025), *Trends in Food Science & Technology* 161:105055
"Towards intelligent food safety: Machine learning approaches for aflatoxin detection and risk prediction."

This is a **review paper** and is therefore the direct structural template for Paper 1. Its section skeleton:

1. Introduction — the problem, why it matters, why existing methods are inadequate, what makes this review different from prior reviews.
2. Methods taxonomy — types of ML (supervised / unsupervised / reinforcement), how each family of algorithms actually works, explained with plain-language analogies plus correct terminology.
3. Performance evaluation metrics — defined with formulas, presented as a figure.
4. Case studies — a large comparative table (~40 rows) plus narrative walkthrough of notable studies.
5. Challenges and future scope — broken into named sub-problems (data limitations, generalisation across domains, black-box/interpretability, real-time deployment, prevention vs detection, end-user accessibility).
6. Conclusion.

Its Table 1 column structure is:
`Case Study | Detection Technique | ML Model/Tool Used | Accuracy/R²/LOD | Overarching Trend | Target Sample Type`

**Adapt this to AuthentiScan as:**
`Study (Author, Year) | Detection Approach | Model / Architecture | Dataset Used | Generator(s) Covered | Reported Accuracy / AUC | Cross-Generator Tested? | Key Limitation`

The `Cross-Generator Tested?` and `Key Limitation` columns are the ones that build the argument for Semester 8. Do not drop them.

### Paper C — Cengel et al. (2025), *Journal of Food Science* 90:e17553
"Automating egg damage detection for improved quality control in the food industry using deep learning."

- Four CNNs: GoogLeNet, VGG-19, MobileNet-v2, ResNet-50.
- Small dataset (794 images), imbalanced (632 vs 162), 80/20 split.
- Very explicit hyperparameter table: initial learning rate, solver, validation frequency, mini-batch size, max epochs — each choice justified in one or two sentences.
- Confusion matrix per model, training-time comparison, and an honest discussion of why the most accurate model was also the slowest.

**Takeaway to copy:** every hyperparameter choice gets a one-line justification. Every result gets a "what this means practically" sentence. This is what makes a student paper read as considered rather than assembled.

### Common schema across all three

`Abstract → Keywords → Introduction → Related Work → Materials and Methods (dataset, architectures, transfer learning technique, experimental setup, evaluation metrics with formulas) → Results (tables, confusion matrices, ROC, learning curves) → Discussion → Conclusion → Author contributions → Data availability → References`

Paper 1 replaces *Materials and Methods / Results* with *Taxonomy of approaches → Datasets and benchmarks → Comparative analysis → Gap analysis → Challenges and future scope*.

---

## 5. Semester 7 master plan — Paper 1 (Review / Survey)

### Title `[CONFIRMED]`

*"Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches"*

Finalised by Rohit (29 July 2026). This is the official minor project topic and the Paper 1 title. Use it on all WPRs and submission documents; "AuthentiScan" remains the internal working name only.

### Target structure for Paper 1

| § | Section | Approx. share |
|---|---|---|
| — | Abstract (200–250 words) + 5–6 keywords | — |
| 1 | Introduction — rise of generative models, threat landscape, why detection is needed, contributions of this review, paper organisation | 10% |
| 2 | Background — how images get generated: GANs, diffusion models, and what artefacts each tends to leave behind | 12% |
| 3 | Taxonomy of detection approaches | 30% |
| 3.1 | Handcrafted / statistical / frequency-domain forensics | |
| 3.2 | CNN-based approaches and transfer learning | |
| 3.3 | Transformer and attention-based approaches | |
| 3.4 | Multimodal and foundation-model-based approaches (e.g. CLIP-feature detectors) | |
| 3.5 | Explainability in detection (Grad-CAM and related) | |
| 4 | Datasets and benchmarks — CIFAKE, GenImage, ArtiFact, and others; comparative dataset table | 12% |
| 5 | Evaluation metrics and how the literature reports them | 8% |
| 6 | Comparative analysis — the master literature table + synthesis of trends | 15% |
| 7 | Challenges and gap analysis — generalisation, compression/post-processing robustness, dataset bias, interpretability, dataset staleness | 10% |
| 8 | Conclusion and the case for the proposed Semester 8 work | 3% |
| — | References (target 45–60 verified sources) | — |

### Search protocol (define this in Week 1 and record it in the paper)

- Databases: IEEE Xplore, ScienceDirect, SpringerLink, ACM DL, arXiv, Google Scholar.
- Query seeds: `AI-generated image detection`, `synthetic image detection`, `GAN image detection`, `diffusion image detection`, `deepfake image forensics`, `CIFAKE`, `GenImage`, `cross-generator generalization`.
- Inclusion: published 2019–2026, image domain (not video/audio), reports quantitative results, peer-reviewed or well-cited preprint.
- Exclusion: video-only, audio-only, no quantitative evaluation, non-English, inaccessible full text.
- Record counts at each stage (identified → screened → included). A simple PRISMA-style flow figure is a cheap way to make the review look methodical. Recommended.

### Week-by-week plan — Semester 7 `[CONFIRMED dates]`

The NTCC window is 20 July – 9 October 2026: **12 weeks, not the original 15**. The plan below is the compressed version (original Weeks 8–9 merged into Week 8, 11–12 into Week 10, 12–13 into Week 11, 14 into Week 12; no buffer week — any slippage eats guide-review time in Week 12, so do not let writing weeks slip). Weeks run Monday–Sunday.

| Week | Dates (2026) | Objective | Deliverable artefact | Status |
|---|---|---|---|---|
| 1 | 20–26 Jul | Scope, title, search protocol, section skeleton, repo structure | `outline.md`, `search_protocol.md`, section files | DONE |
| 2 | 27 Jul–2 Aug | Literature collection round 1 + title/abstract screening | `references/candidates.csv` (75), `references/screened.csv` (48 primary / 12 secondary / 15 background), `screening_summary.md` | DONE |
| 3 | 3–9 Aug | Full-text read of the 48 primary studies; populate extraction table | `references/extraction_table.csv` (all columns filled or `[VERIFY]`) | DONE |
| 4 | 10–16 Aug | Finalise taxonomy; write **Section 1 — Introduction** | `sections/01_introduction.md` | DONE (accel., 12 Aug) |
| 5 | 17–23 Aug | Write **Section 2 — Background** | `sections/02_background.md` | DONE (accel., 12 Aug) |
| 6 | 24–30 Aug | Write **Sections 3.1–3.2** | `sections/03_approaches.md` (part) | DONE (accel., 12 Aug) |
| 7 | 31 Aug–6 Sep | Write **Sections 3.3–3.5** | `sections/03_approaches.md` (complete) | DONE (accel., 12 Aug) |
| 8 | 7–13 Sep | Write **Section 4 — Datasets** + **Section 5 — Metrics**; dataset table + metrics figure | `sections/04_datasets.md`, `tables/dataset_comparison.md`, `sections/05_metrics.md`, `figures/metrics_overview` | DONE (accel., 12 Aug; + PRISMA figure) |
| 9 | 14–20 Sep | Master literature table + **Section 6 — Comparative analysis** | `tables/literature_comparison.md`, `sections/06_comparative.md` | DONE (accel., 12 Aug; table machine-verified 48/48) |
| 10 | 21–27 Sep | **Section 7 — Challenges/gap** + **Section 8 — Conclusion** + Abstract | `sections/07_challenges.md`, `sections/08_conclusion.md`, `sections/00_abstract.md` | DONE (accel., 12 Aug) |
| 11 | 28 Sep–4 Oct | Full assembly into template DOCX; reference verification pass; plagiarism/AI-text checks | draft v1 DOCX, `references/verification_log.md` | DONE except Amity-template restyle + plagiarism check (blocked on open items 1, 3); draft v1 DOCX+PDF in `submission/`, generic style |
| 12 | 5–9 Oct | Guide review, corrections, final formatting, submission pack | Final report + all WPRs | |

### Acceleration mode `[CONFIRMED — adopted 12 August 2026 at Rohit's request]`

Content work for Weeks 4–11 is executed ahead of calendar, sprint by sprint in week order, each sprint gated by a review pass before the next starts (citations checked against `screened.csv` + `references.bib`, numbers checked against `extraction_table.csv`, no own-results claims, register, word budget). Rules that survive acceleration unchanged:

1. WPR N is rendered only after week N's deliverable is approved, carries its scheduled Wednesday date, and is uploaded on the normal Amizone schedule — work done early is still real, artefact-backed progress.
2. Calendar Week 12 (guide review, corrections, submission) happens in real time; it cannot be accelerated.
3. Week 11's DOCX assembly is done in a clean generic style until the official Amity template (open item 1) arrives; re-styling into the template is the only step that then remains.
4. Drafts are inputs for Rohit's own rewrite pass before submission (§10 plagiarism/AI-text rule). Acceleration produces complete, verified draft material — not submission-ready prose.
5. Process changes adopted with acceleration: citation-key system (`[Cxx]` keys from `screened.csv`, `references/references.bib` keyed the same way, IEEE numeric at assembly) fixed before any section is written; the 10 `[VERIFY]` extraction cells are resolved before Section 6 is written, not in Week 11; `verification_log.md` is maintained incrementally, not retrofitted.

---

## 6. Semester 8 outline — Paper 2 (Experimental Implementation)

The detailed implementation plan was written 18 Aug 2026 per the guide's 15 Aug instruction: **`sem8_major/implementation_plan.md`** (build weeks B0–B7 dated 17 Aug–9 Oct 2026 inside Semester 7; Semester 8 phases relative until its calendar is known). The phase table below is retained as the original outline.

| Phase | Approx. weeks | Objective |
|---|---|---|
| Setup | 1–2 | Environment, CIFAKE acquisition, data pipeline, fixed random seeds, train/val/test split locked and documented |
| Baseline CNNs | 3–4 | ResNet50 and DenseNet121 — feature extraction and fine-tuning configurations |
| Remaining CNNs | 5–6 | EfficientNet-B0 and VGG19, same two configurations |
| Transformer benchmark | 7–8 | ViT trained/fine-tuned under matched conditions |
| Explainability | 9 | Grad-CAM heatmaps for correct and incorrect predictions across all models |
| Generalisation test | 10 | Cross-generator evaluation on a GenImage subset (train on CIFAKE, test on unseen generators) |
| Ablations | 11 | Feature extraction vs fine-tuning, augmentation on/off, input resolution |
| Consolidation | 12 | All result tables, confusion matrices, ROC curves, learning curves, training-time table |
| Paper 2 writing | 13–14 | Full draft following the Karki et al. schema |
| Report + viva | 15 | Major project report, demo preparation, submission |

**Reproducibility rules for Semester 8 (set now, so they are not retrofitted later):**
- One config file per experiment. No hardcoded hyperparameters scattered in scripts.
- Every run logs: seed, split, epochs, learning rate, optimiser, batch size, hardware, wall-clock training time.
- Results written to CSV as they are produced, never transcribed by hand into the paper.
- Record the exact hardware used (CPU, RAM, GPU model and VRAM) — all three reference papers report this and it is expected.

---

## 7. Weekly Progress Reports (WPR)

Two **separate** WPR tracks must be maintained. Do not merge them.

| Track | Semester | Covers |
|---|---|---|
| **Minor Project WPR** | Semester 7 | Literature review work only |
| **Major Project WPR** | Semester 8 | Implementation work only |

### WPR generation rules for Claude Code

1. At the end of every planned week, generate that week's WPR **without being asked**. Prompt Rohit if the week's artefact is missing.
2. Each WPR entry must be traceable to the week's deliverable artefact in the repo. If the artefact does not exist, the WPR must say the week is incomplete. Do not write progress that did not happen.
3. Keep entries factual and short. Amity WPRs are checked for consistency across weeks, not for eloquence.
4. Maintain a cumulative WPR log file so the full set can be printed at submission time.

### Official WPR proforma `[CONFIRMED — received 29 July 2026]`

One A4 page. Header: "Weekly Progress Report / Amity School of Engineering & Technology / B. Tech: Program"; then a WPR No + Duration row; caption line "Weekly Progress Report (WPR) for Minor Project"; a "To be filled by Students" table (Students Name, Roll no., Enrollment no., Project Title finalized, Synopsis submitted, Literature review, Technical & Economical Feasibility, Bill of Material, PERT Chart, Design of critical components, Fabrication %, Experimental %, Result and Analysis, Report writing, Signature of students); a "Work done in this week" paragraph; a "To be filled by Guide" block; date fields.

**Rules for generating a WPR:**
1. 12 WPRs total, one per project week. Group WPR — all three members listed.
2. WPRs are due on Amizone by **Wednesday of the following week**; the date fields carry that Wednesday (WPR 1 → 29 Jul, WPR 2 → 5 Aug, and so on).
3. Pipeline: copy `sem7_minor/wpr/wpr_week01.html`, edit WPR No., duration, content rows and the work-done paragraph, render with headless Edge (`msedge --headless=new --no-pdf-header-footer --print-to-pdf=...`), output to `sem7_minor/submission/pdf/G148_Sem7_WPR_WeekNN.pdf`. Verify the render: exactly one page, selectable text.
4. Every content row must be traceable to artefacts in the repo — no invented progress.
5. Each upload also needs the Amizone portal fields (Target For The Week / Achievements / Future Work Plans) — keep them consistent with the PDF and log them in `sem7_minor/wpr/amizone_entries.md`.
6. Maintain `sem7_minor/wpr/wpr_cumulative.md` (one row per WPR).

---

## 8. Document format and submission pipeline `[CONFIRMED]`

Every document submitted for this project — synopsis, weekly progress reports, minor project report, major project report, and both papers — is submitted as **PDF**. This applies from the first submission to the last, across both semesters.

### PDF is the output format, not the working format

Do not author directly in PDF.

| Document | Author in | Export to |
|---|---|---|
| Report / paper | DOCX using the official Amity template | PDF |
| WPRs | HTML replica of the official proforma (`sem7_minor/wpr/`), rendered via headless Edge | PDF (one A4 page, text-searchable) |
| Working drafts and sections | Markdown, in the repo | assembled into DOCX at Week 12 |

Rationale: Amity supplies templates as Word documents with fixed margins, fonts, heading numbering and caption styles. Generating a PDF directly from Markdown or LaTeX will not reproduce that template and will cost marks on formatting compliance. Author inside the template, export at the end.

### PDF requirements

1. **Text-searchable.** The PDF must contain selectable text, not page images. Plagiarism and AI-detection tools cannot process image-only PDFs, and a submission that fails to process is usually treated as not submitted.
2. **Fonts embedded.** Export with font embedding enabled so the layout does not shift on the evaluator's machine.
3. **Export, do not print-to-image.** Use Word's Save as PDF / Export. Not a print-to-image driver, not a photograph, not a scan of a printout.
4. **Figures and tables legible at 100% zoom.** Check confusion matrices and the master comparison table specifically — wide tables are the first thing to degrade on export.
5. **Verify the export, not the source.** Page numbers, headers, group number, and guide details must survive the conversion. Open the PDF and check.

### Signature handling on WPRs `[UNKNOWN]`

WPRs normally require student and guide signatures. If signatures are physical, the usual route is print → sign → scan, which produces an image-only PDF and breaks requirement 1 above. Confirm with the guide which is acceptable:

- typed or digital signature blocks placed in the DOCX before export, or
- text PDF submitted for records with a signed hard copy held separately, or
- scanned signed copy accepted as-is because WPRs are not run through plagiarism checks.

Do not assume. Ask in Week 1. This is the one place where the PDF-only rule and the text-searchable rule can conflict.

### File naming convention `[ASSUMED]`

Until Amity specifies otherwise:

```
G148_Sem7_WPR_Week01.pdf
G148_Sem7_MinorProjectReport_v1.pdf
G148_Sem7_MinorProjectReport_FINAL.pdf
G148_Sem8_MajorProjectReport_FINAL.pdf
```

Keep every version. Never overwrite a PDF that has already been submitted.

### Claude Code responsibility

- Produce DOCX using the docx skill when an Amity template is supplied. Produce Markdown only for internal working drafts.
- Never deliver a final submission artefact as Markdown, plain text, or HTML.
- Before declaring any submission ready, confirm the PDF exists, opens, has selectable text, and is within any size limit Amity specifies.
- Keep both the source DOCX and the exported PDF in `submission/`. The source is needed for corrections; the PDF is what gets handed in.

---

## 9. Repository structure

```
authentiscan/
├── CLAUDE.md                      # this file
├── README.md
├── sem7_minor/
│   ├── outline.md
│   ├── search_protocol.md
│   ├── sections/
│   │   ├── 01_introduction.md
│   │   ├── 02_background.md
│   │   ├── 03_approaches.md
│   │   ├── 04_datasets.md
│   │   ├── 05_metrics.md
│   │   ├── 06_comparative.md
│   │   ├── 07_challenges.md
│   │   └── 08_conclusion.md
│   ├── tables/
│   │   ├── literature_comparison.md
│   │   └── dataset_comparison.md
│   ├── figures/
│   ├── references/
│   │   ├── candidates.csv
│   │   ├── screened.csv
│   │   ├── extraction_table.csv
│   │   ├── references.bib
│   │   └── verification_log.md
│   ├── wpr/
│   │   ├── wpr_week01.md ...
│   │   └── wpr_cumulative.md
│   └── submission/
│       ├── source_docx/
│       └── pdf/            # what actually gets submitted
├── sem8_major/
│   ├── (created at start of Semester 8)
└── docs/
    ├── amity_synopsis.pdf
    ├── amity_report_template.docx
    └── reference_papers/
```

`sem8_major/` was created 18 Aug 2026: `implementation_plan.md`, `README.md`, `requirements.txt`, `.gitignore`, and the skeleton `{code/ (5 contract stubs), configs/ (template.yaml + resnet50_fe.yaml), data/ (gitignored), results/, figures/, notebooks/}`. Code never lives in `sem7_minor/`.

---

## 10. Hard rules

### Citation integrity — non-negotiable

- Every reference must have a real, checkable DOI, arXiv ID, or stable URL.
- Every number quoted from a paper (accuracy, dataset size, year) must be traceable to that paper's text.
- If a claim cannot be verified, either remove it or mark `[VERIFY]` and log it. Never smooth over a gap with plausible-sounding text.
- Maintain `verification_log.md`: one line per reference, recording that it was opened and confirmed.
- A fabricated citation in an academic submission is a serious integrity issue and is trivially caught by a guide who checks two references at random. Treat this rule as absolute.

### Writing rules

- Middle register: accessible explanations with correct technical terminology used naturally.
- No inflated claims. Do not write that a method "revolutionises" anything.
- Every table must be referenced in the body text before it appears.
- Every figure must have a caption in the style of the reference papers.
- Paraphrase; do not copy sentence structures from source papers.
- Expect a plagiarism and AI-text check. Produce drafts that Rohit edits and rewrites in his own voice before submission. Do not treat generated prose as submission-ready.

### Scope rules

- Semester 7 produces zero experimental results. Enforce this.
- Do not add architectures, datasets, or techniques beyond those listed in Section 2 without an explicit decision from Rohit.
- Do not restructure the paper outline mid-semester without flagging the cost in weeks.

### Formatting rules

- Amity template compliance is mandatory and takes precedence over aesthetic preference.
- Margins, fonts, heading numbering, table/figure caption placement, and reference style must match the supplied Amity template exactly.
- Do not guess the template. Ask for it.
- All final submissions are PDF. See Section 8 for the authoring and export pipeline.

---

## 11. Definition of done — Semester 7

The semester is complete when all of the following exist:

- [ ] Paper 1 full draft, formatted to the Amity report template
- [ ] 45–60 references, every one verified in `verification_log.md`
- [ ] Master comparative literature table with `Cross-Generator Tested?` and `Key Limitation` columns populated
- [ ] Dataset comparison table
- [ ] Gap analysis section that explicitly names what Semester 8 will do and why
- [ ] All weekly Minor Project WPRs, signed, in the official Amity format
- [ ] Plagiarism / AI-text check passed at whatever threshold Amity specifies `[UNKNOWN]`
- [ ] Final report exported to PDF: text-searchable, fonts embedded, tables legible
- [ ] All Minor Project WPRs exported to PDF and named per convention
- [ ] Source DOCX retained alongside every submitted PDF
- [ ] Guide sign-off from Dr. Richa Gupta

---

## 12. Open items — must be resolved, do not invent

**Resolved:**

| Item | Resolution |
|---|---|
| Academic calendar | NTCC window 20 Jul – 9 Oct 2026 (82 days, 12 weeks); WPR due on Amizone by Wednesday each week |
| Official WPR proforma | Received 29 Jul 2026; replicated in `sem7_minor/wpr/wpr_week01.html` (see §7) |
| Paper 1 title | Finalised (see §5) |
| Item 13 — extraction `[VERIFY]` cells | All 10 resolved 12 Aug 2026 from the papers' full text (see `screening_summary.md`). Two findings: C07 and C64 are NOT cross-generator tested — Sections 6/7 must not count them as such. C15/C32/C64 values verified from CVF/PMLR PDFs by the work agent with section/table pointers; direct re-check queued for the Week 11 verification pass. |
| C50 (LASTED) publication year | Journal version is June 2026 (IEEE TAI vol 7 no 6, pp. 3485-3496; Crossref-confirmed 12 Aug 2026). `screened.csv`/`candidates.csv` corrected 2025 → 2026; `references.bib` already uses 2026. |
| Reference infrastructure | `references/references.bib` (74 entries, C-ID keys) and `references/verification_log.md` (74/74 identifiers opened and verified 12 Aug 2026) built ahead of section writing. |
| Hardware (item 7) | Resolved 18 Aug 2026 (Rohit's decision): Kaggle notebooks free tier for all training — CIFAKE is Kaggle-hosted, free GPU covers the estimated 20–35 GPU-h budget. Local laptop (i5-1135G7, 16 GB RAM, no CUDA GPU; Python 3.12.10 installed) for development and CPU smoke tests only. Recorded in `sem8_major/implementation_plan.md` §2. |

**Still open:**

| # | Item | Needed by |
|---|---|---|
| 1 | Official Amity minor project report template (fonts, margins, reference style) | Before Week 11 assembly |
| 2 | Word/page limit for the Semester 7 report | Before Week 11 |
| 3 | Plagiarism / AI-content threshold enforced by the department. Draft v2 was submitted for the check on 15 Aug 2026 — result pending; threshold number itself still unknown | Result pending |
| 4 | Role split between Rohit, Vishal, and Hardik Mehlawat | ASAP (WPRs currently name no per-member tasks) |
| 5 | Target journal or conference for the **merged paper** (affects reference style and length; decided with the guide at merge gate P2 — `sem8_major/implementation_plan.md` §10) | P2, Semester 8 |
| 6 | Whether the guide wants a mid-semester review checkpoint | Week 3–4 |
| 8 | Whether WPR signatures may be digital, or must be physical and scanned | Before next upload |
| 9 | Whether Amity mandates a PDF file-naming convention or size limit | Before Week 12 |
| 10 | Whether a hard copy is required in addition to the PDF | Before Week 12 |
| 11 | Dr. Richa Gupta's designation + student phone numbers (blank in offer letters) | Before offer letters are signed |
| 12 | Confirm Vishal's roll 568 and Hardik's roll 449 (derived, not stated) | Before next WPR upload |
| 14 | Rohit to confirm (or override) the exclusion of TruthLens (arXiv:2503.15867, 1 citation — fails well-cited-preprint criterion). Default (exclusion) was applied; master table has 48 rows without it | Before submission |
| 15 | Final reference list has 73 entries vs the 45–60 target in §11. Not an error (48 primary + support set), but decide with the guide whether to trim secondary/background support citations at the template pass | Before Week 12 |
| 17 | ~~Table 6.1 legibility~~ RESOLVED 15 Aug: draft v2 restyles it full-width Elsevier-fashion (Table 2, pp. 12–15); apply the same treatment in the Amity template | — |
| 18 | Whether Amity and/or the target venue require an AI-assistance disclosure statement (AI-assisted drafting and code with human verification). Ask the guide; if yes, draft the statement | Before Week 11 upload / with venue choice |
| 19 | Merged-paper shape: hybrid review+experiment (review survives as condensed taxonomy + 48-study table + gap analysis, ~12–14k words) vs experimental paper with deep related work (review compressed to 2–3 pages). Decided after major-project development completes, at merge gate P2 (`implementation_plan.md` §10) | P2, Semester 8 |

---

## 13. Current status and next to-dos (updated 4 September 2026)

**Phase-completion rule `[CONFIRMED — Rohit, 20 Aug 2026]`:** at every Track B phase gate,
three documents are updated in the same pass, each carrying the date: this file (§13),
`sem8_major/implementation_plan.md`, and **`handoff.md`** at the repo root — the handoff
carries Goal / Current State / Active Files / Changes it made / Failed Attempts / Next steps
for the phase just closed, newest phase first. Read `handoff.md` after this file when
resuming work.

**15 Aug events:** draft v2 submitted for the department plagiarism check (result pending, open item 3). Dr. Richa Gupta instructed the team to begin preparing the implementation code now (see the §3 amendment). Two tracks now run in parallel; the detailed to-dos for both are at the end of this section.

**18 Aug events:** hardware decided (item 7 resolved — Kaggle free tier + local laptop for dev; see §12 Resolved). Implementation plan written and verified (`sem8_major/implementation_plan.md`) and the `sem8_major/` skeleton created (5 contract stubs, config template + first config, results/data/notebooks READMEs, requirements.txt, .gitignore). Produced by Opus drafting agents, checked by three verification agents (2 major + 12 minor findings, all fixed before anything was written to disk). Same evening, the local half of B0 was executed: `.venv` built and `requirements.lock` frozen (46 pins; torch 2.13.0+cpu, timm 1.0.28, imports smoke-tested), `make_split` implemented in `code/data.py` with a passing `--selfcheck`, empty `results/runs.csv` with the Table 4 schema header, and the GenImage access path resolved in `data/genimage_access_note.md` (primary: Tiny-GenImage HF mirror; fallback: official Google Drive; counts `[VERIFY at download]`). Later that evening Rohit supplied a Kaggle API token (stored at `~/.kaggle/access_token`; valid — verified by direct API call; the CLI's `datasets list` subcommand mishandles it but downloads work): CIFAKE was downloaded locally (105 MB zip, layout confirmed `train|test / REAL|FAKE`), `data/cifake_split_seed42.csv` generated and verified (120,000 rows; 45k/45k train, 5k/5k val, 10k/10k test), and the GenImage note upgraded — primary route is now the Kaggle-native `yangsangtai/tiny-genimage` (official GenImage folder convention, attachable to the eval notebook). Remaining B0: Kaggle notebook set up + CIFAKE attached there + actual GPU-quota check (browser login, Rohit). Repo is still not git-initialised (plan §8.8 recommends `git init` — Rohit's call).

**19–20 Aug events — B0 COMPLETE:** Rohit attached the official CIFAKE (`birdy654/...`) to his Kaggle notebook `yaduvxnshi/notebook322addb147` (private; token-verified; GPU and Internet off until B1 needs them) and the quota page confirmed **30 h GPU + 20 h TPU per week** — the plan's estimate was exact. Kaggle mount path recorded in `notebooks/README.md` and `configs/template.yaml`. Also pulled: a third-party reference notebook (`reference_thirdparty_y5cy5c_keras_cifake.ipynb`, provenance warning in the README — no code or numbers from it may be reused). Next Track B step: B1 (24–30 Aug) — end-to-end ResNet50-fe smoke run, local CPU first (venv + data + split all ready locally), then one short Kaggle GPU run.

The acceleration run of 12–13 Aug (see §5 "Acceleration mode") completed all content work for Weeks 4–11. Every deliverable passed a review gate: citations checked against `screened.csv`/`references.bib`, numbers checked against `extraction_table.csv` (the master table machine-verified 48/48 with zero mismatches), no own-results claims anywhere.

**What exists now:**

- Full paper draft: abstract + keywords, Sections 1–8 (~9,850 words), Table 4.1 (11 datasets), Table 6.1 (48 studies, with `Cross-Generator Tested?` and `Key Limitation` columns), PRISMA and metrics figures (SVG + PNG)
- Assembled draft v1: `sem7_minor/submission/source_docx/G148_Sem7_MinorProjectReport_draft_v1.docx` + 31-page text-searchable PDF, IEEE-numeric citations (73 refs, map in `submission/citation_map.csv`), generic style pending the Amity template
- Draft v2 (15 Aug, from Rohit's three sample papers — format only, no publisher branding): journal-style two-column layout, author–year citations (8 surname+year collisions given a/b suffixes), new taxonomy diagram (`figures/taxonomy_overview.svg/.png`, = Fig. 1), Table 2 restyled full-width Elsevier-fashion across pp. 12–15; `submission/manuscript_v2.html` → 19-page PDF + two-column DOCX (`..._draft_v2.*`); rebuild scripts in `submission/build/`. v1 untouched. C32/C64 extraction values source-verified 15 Aug (poppler) — item 16 closed.
- `references/references.bib` (74 C-keyed entries) + `references/verification_log.md` (74/74 identifiers verified)
- WPRs 4–10 rendered, one page each, dated their due Wednesdays — **upload each on its scheduled Wednesday, not before**; Amizone portal text in `wpr/amizone_entries.md`

*(WPRs 4–11 are all rendered and verified — WPR 11 included; item 16 closed 15 Aug; item 17 closed by draft v2.)*

### Track A — paper (Semester 7 deliverable), in order

- [ ] Plagiarism-check result on draft v2: if over threshold, the fix is Rohit's rewrite pass (§10), not a paraphrasing tool — see the ai-research-workflow verdict: no "humanizer"/AI-detector-evasion tools, ever [Rohit, then Claude re-verifies citations after any rewrite]
- [ ] Rewrite pass over all drafted prose in Rohit's own voice — required regardless of the plag result before final submission [Rohit]
- [ ] Upload WPRs on their scheduled Wednesdays — next: WPR 4 on 19 Aug, then weekly through WPR 11 on 7 Oct; portal text in `wpr/amizone_entries.md`; signatures per open item 8 [Rohit]
- [ ] Ask the guide: Amity template + word limit (items 1–2), signature mode (8), AI-assistance disclosure (18), reference-count trim 73→45–60 (15), mid-sem checkpoint (6) [Rohit]
- [ ] Decide: venue (5), TruthLens (14), roll numbers (12) [Rohit]
- [ ] When the Amity template arrives: restyle into it (v2 pipeline in `submission/build/` regenerates from the sections mechanically), re-export, verify PDF rules of §8 [Claude]
- [ ] Week 12 (5–9 Oct): guide review, corrections, submission pack [all]

**20 Aug events — Track B acceleration adopted (Rohit's request: work continuously, no calendar waits).** The full accelerated schedule is `implementation_plan.md` §7a: phases A1–A6 with gates G1–G6, adversarially verified the same day by a 5-lens review workflow (32 findings, all fixed — including a config that would have leaked a smoke-subset row into Paper 2's results table, a WPR-rule wording that could have put Track B work into Minor WPRs without the guide's consent, and an overclaim about the down32 cross-generator condition now reworded as a stated limitation). Key new rules: smoke runs quarantined in `results/smoke_runs.csv`; `n_train_images` column added to `runs.csv`; Track A always preempts Track B for Rohit's time; no Kaggle sessions 5–9 Oct; D1 default = private GitHub unless Rohit objects by 22 Aug. Same day (Rohit: "go", repo name **sm7**): `git init` done at project root (initial commit 0d7fa93; a stray file named after the Kaggle API token was deleted before staging and KGAT_* gitignored), and **A1 completed + G1 passed** — all six modules implemented (data/models/train/eval/gradcam/merge_runs), ten matrix configs + smoke config, CPU smoke run end-to-end, 4-lens adversarial code review (16 findings, all fixed — see plan §7a G1 note; biggest: cp1252 configs that would have crashed every Kaggle run, unpicklable worker seeder, imagenet_midjourney folder miss). **A2 (20 Aug, in progress):** D1 resolved — private GitHub repo `rohityaduvxnshi/sm7` created by Rohit; project history pushed (`750c522`, the repo's auto-README merged rather than force-overwritten; no credential file in any commit). A2 tooling written and CPU-tested (`calibrate.py`, `record_env.py`, `run_session.py` with verified failure isolation) and `notebooks/phase_a2_smoke.ipynb` pushed to Kaggle by REST API as version 2 — private, GPU on, Internet on, CIFAKE attached. Notebook slug is now **`yaduvxnshi/authentiscan-a2-gpu-smoke-and-calibration`**. Note: the laptop deletes files containing the Kaggle token (`~/.kaggle/access_token` vanished twice) — pass it inline. Second clone at `Documents\GitHub\sm7` is not the working copy.

**22 Aug — A2 COMPLETE, G2 PASSED; A3 started.** The Kaggle session ran: Tesla T4 15 GB, torch 2.10.0+cu128, timm 1.0.26 (differ from the local lock — logged per run); GPU smoke val 0.7175 / test 0.7925, *bit-identical to the CPU smoke*; Grad-CAM verified on GPU; all five backbones timed (`results/calibration.csv`). Headline planning fact: the matrix is **31.3 GPU-h worst case vs a 30 h weekly quota** (≈12.5 h with realistic early stopping), so `train.py` gained a `time_budget_min` guard and a `stop_reason` column so a run stops cleanly instead of dying at the session cap. A3 runs as six generated notebooks (`notebooks/make_a3_notebook.py`); session 1 (resnet50 fe+ft) is pushed as `yaduvxnshi/authentiscan-a3-session-1` and awaits Rohit's Run All, then gate G3 (val_acc sanity, mid-90s expected). Handoff detail in `handoff.md`.

**23 Aug (later) — Kaggle-first amendment (supersedes the carve-out's run placement).** Rohit: exhaust Kaggle quota on the remaining six runs (sessions 3–6) before using the Victus for training — if they all land on T4, the full 10-run matrix is hardware-consistent at committed batch sizes, no per-GPU caveat in Paper 2. Victus = A4–A6 machine + training fallback. Plan §7a amendment 2.

**23 Aug — Kaggle DenseNet session COMPLETE.** Session 2 merged: densenet121_fe val 93.59/test 93.49; densenet121_ft val **97.64/test 97.60** (AUC 0.9972) — matrix leader, ahead of resnet50_ft. Early stopping fired (2.3 h vs 6.5 worst case). `runs.csv` = 4 of 10 rows, all T4 at committed batch sizes. Remaining six runs (effnet/vgg/vit fe+ft) are the Victus's job. All four checkpoint dirs live on the old laptop only — transfer checklist in `handoff.md`.

**23 Aug — Kaggle session 3 COMPLETE; matrix 7 of 10, all T4.** efficientnet_b0_fe val 92.67/test 92.87; efficientnet_b0_ft val **97.50**/test 97.56 (AUC 0.9971); vit_base_patch16_224_fe val 94.62/test 94.75 (AUC 0.9881). 4.2 h against a 7.6 h worst-case budget, two of three early-stopped. EfficientNet-B0-ft is statistically tied with the DenseNet121-ft leader (97.56 vs 97.60 test on one seed) — Paper 2 reports them as tied, not ranked. ViT-fe beats every CNN fe row, the expected linear-probe result. Every row so far is Tesla T4 at its committed batch size, seed 42, same split file, so amendment 2's no-per-GPU-caveat goal is holding. Remaining: vgg19 fe (session 4, notebook generated), vgg19 ft (session 5), vit ft (session 6). Also fixed this pass: a GitHub PAT had been pasted into `.gitignore` as a literal line — replaced with a `github_pat_*` pattern; the token was never committed, but it must be treated as exposed and revoked.

**4 Sep — SESSION 8 COMPLETE; the lower-bound rerun phase is CLOSED (3 of 3); A4 is next.** resnet50_ft at a 50-epoch ceiling (`resnet50_ft_20260827-0206`): val 96.32 / test **96.51** (AUC 0.9941, F1 0.9651), up from 95.66 / 95.93 (+0.66 / +0.58 pp); 323 min against a 317 min projection (1.02×); Tesla T4, seed 42, same split, same torch/timm versions as every other row. **Reproducibility note for Paper 2:** the rerun's first 30 epochs are bit-identical to the original run's learning curve (diff-verified), so the 30-epoch row is a strict prefix of the 50-epoch row and the whole improvement is the extra 20 epochs. **Still formally unconverged** — best epoch 48 of 50, `stop_reason=max_epochs`, the same outcome as resnet50_fe — but the tail is diminishing returns (val_loss fell 0.0143 over epochs 31–40 and only 0.0042 over 41–50; last-10 val_acc band 95.99–96.35%; train/val gap 0.9 pp, no overfitting). **Decision: the ceiling is not extended again for either ResNet50 row.** Paper 2 carries one architecture-level caveat — ResNet50 under the committed SGD rates converges more slowly than the other four backbones and did not trigger patience-5 within 50 epochs in either mode — rather than two row caveats. **The 25 Aug worry that resnet50_ft's last place was an epoch-budget artefact is settled: it is not.** Twenty extra epochs closed 0.58 pp of a 1.63 pp gap to the three-way tie band; 1.05 pp remains, about 8 SE on 20,000 test images (SE ≈ 0.13 pp). Canonical ft ranking: vit 98.89 > vgg19 97.91 > densenet121 97.60 ≈ efficientnet_b0 97.56 > resnet50 96.51. Canonical fe ranking: vit 94.75 > densenet121 93.48 > resnet50 92.98 ≈ efficientnet_b0 92.86 > vgg19 90.55 (0.12 pp, noise). ResNet50's fe→ft gain rises to +3.53 (from +3.10), still the smallest; the VGG19 inversion (+7.36) and the ViT lead are unaffected. `runs.csv` = 13 rows (10 matrix + 3 reruns, nothing overwritten), every row `Tesla T4, 15 GB` / torch 2.10.0+cu128 / timm 1.0.26; 30.12 h total measured GPU time (19.89 h matrix + 10.23 h reruns). A6's `canonical_runs.txt` should select `resnet50_fe_20260826-0457`, `resnet50_ft_20260827-0206` and either efficientnet_b0_fe row (metrics identical). **Nothing is pending on Kaggle; A4 (Grad-CAM + cross-generator) is the next phase.** All 13 checkpoints (2.2 GB) sit on this laptop (DESKTOP-GKS9MUQ, no GPU; repo now at `d:\Desktop\AuthentiScan`); the USB transfer to the Victus remains A4's practical gate.

**26 Aug (later) — SESSION 7 COMPLETE: one confirmation, one partial fix.** Both reruns finished. **efficientnet_b0_fe is now CONFIRMED CONVERGED** — 50 epochs of room found the identical best epoch (29) and produced bit-identical val/test numbers (92.67/92.86, AUC 0.9802), this time via `stop_reason=early_stopping` instead of `max_epochs`; the original number was correct all along and needs no further disclosure. **resnet50_fe improved but is technically still unresolved** — best epoch landed at 49 of 50, still `stop_reason=max_epochs`; test acc moved 92.83 → 92.98 (+0.15pp). The learning curve shows this is diminishing returns rather than an open trajectory (val_loss flat 0.1775→0.1740 over the final 10 epochs, val_acc noise-banded 93.0–93.2%) — **recommendation: do not extend the ceiling again**, report the 50-epoch number with a narrowly-scoped caveat on this one row. `runs.csv` is now 12 rows (10 matrix + 2 timestamped reruns, nothing overwritten); `canonical_runs.txt` doesn't exist yet (A6) but should select the 50-epoch resnet50_fe row when it's built. **resnet50_ft (session 8) is still pending** — no inference drawn from this result; notebook prepared and pushed, needs its `GITHUB_PAT` toggle and a quota check.

**26 Aug — SESSION 6 COMPLETE; THE 10-RUN MATRIX IS CLOSED; G3 fully passed.** vit_base_patch16_224_ft val 98.98/test **98.89** (AUC 0.9994), 204 min against a 6.8 h worst case, early-stopped at epoch 15 — **the final matrix leader**. All ten rows: Tesla T4 15 GB, seed 42, `cifake_split_seed42.csv`, 90,000 train images, committed batch sizes; **19.89 h total measured GPU time**; one hardware string across the whole matrix, so amendment 2's no-per-GPU-caveat goal is achieved in full. Final ft ranking: vit 98.89 > vgg19 97.91 > densenet121 97.60 ≈ efficientnet_b0 97.56 > resnet50 95.93. Final fe ranking: vit 94.75 > densenet121 93.48 > efficientnet_b0 92.86 ≈ resnet50 92.83 > vgg19 90.55. **Three findings for Paper 2's discussion:** (1) **ViT wins both modes outright** — best frozen representation and best fine-tuned model; at ~0.1 pp standard error on 20,000 test images its ~1 pp lead over VGG19-ft is about 7 SE, a real separation and the cleanest answer to the project's CNN-vs-transformer question; (2) the **VGG19 inversion survives completion** — last on fe (90.55), second on ft (97.91), largest fe→ft gain (+7.36), scoped to this dataset; (3) the **97.5–97.9 band is a three-way tie, not a ranking** — vgg19/densenet121/efficientnet_b0 sit within 0.35 pp and densenet-vs-effnet (0.04 pp) is noise, so Paper 2 must report them as statistically indistinguishable on one seed. **Lower-bound disclosure confirmed against the complete matrix:** exactly three runs hit `max_epochs` with best epoch at/next to the ceiling (resnet50_fe 30/30, resnet50_ft 30/30, efficientnet_b0_fe 29/30); the other seven early-stopped. Session 7 reruns those three at `max_epochs: 50`. **Quota estimate after session 6:** 19.89 h train × ~1.25 ≈ 24.9 h of the 30 h weekly allowance, leaving ~5 h — **session 7's 7–11 h worst case does not fit**, so it waits for the reset unless the week has rolled over; Kaggle exposes no quota API, so check the page. **A4 (Grad-CAM, cross-generator) is now unblocked**; its practical gate is the ~2.1 GB checkpoint transfer.

**25 Aug (later) — single-paper publication plan ADOPTED (guide-approved); session 7 reruns decided.** The publication goal is amended (§3): one merged research paper instead of two — Amity deliverables and WPR tracks unchanged, Paper 2 still drafted in full as the Sem 8 report core. Merge pipeline recorded as `implementation_plan.md` §10 (P1 Paper 2 draft → P2 shape+venue gate with the guide → P3 content map → P4 assembly in a new `publication/` dir reusing the `build_v2.py`/`make_docx.ps1` pipeline → P5 Rohit's rewrite + citation re-verify → P6 venue formatting + self-similarity disclosure → P7 sign-off and submission, all portal actions Rohit's). Merge shape deferred to P2 (open item 19). **Session 7 decision (Rohit):** after session 6 — which runs to completion untouched — a new Kaggle T4 session reruns the three lower-bound rows (resnet50_fe, resnet50_ft, efficientnet_b0_fe) at `max_epochs: 50`, patience 5, all else identical; ~7–11 GPU-h worst case, quota-checked before launch; new run_ids, with A6's `canonical_runs.txt` selecting the table rows. No repo change beyond the three governing documents; no Kaggle action taken.

**25 Aug — session 5 COMPLETE, matrix 9 of 10; session 6 prepared (final run).** vgg19_ft val 98.19/test **97.91** (AUC 0.9979), 216 min against an 8.0 h worst case, early-stopped at epoch 14 — **the new matrix leader**, ahead of densenet121_ft (97.60) and efficientnet_b0_ft (97.56). **The matrix's headline finding is an inversion worth building Paper 2's discussion around:** VGG19 is *last* under feature extraction (90.55) and *first* under fine-tuning (97.91), a +7.36 gain versus +4.69 (effnet), +4.11 (densenet), +3.10 (resnet50). Frozen VGG features encode ImageNet object semantics that transfer poorly to CIFAKE, where the signal is low-level generative artefact; unfrozen, its plain conv stack has the capacity and inductive bias to relearn those filters. Scope that claim to this dataset — it is not a general ranking. **Disclosure item:** resnet50_fe, resnet50_ft and efficientnet_b0_fe stopped at `max_epochs` with best epoch at/next to the ceiling and val loss still improving, so those three are **lower bounds, not converged results**; this matters most for resnet50_ft, whose last place among ft runs is partly an epoch-budget artefact. State it wherever the ft ranking appears, or rerun the three at a higher ceiling. All nine rows: Tesla T4, seed 42, `cifake_split_seed42.csv`, 90,000 train images, committed batch sizes; 16.5 h measured GPU time. **Session 6 (vit_base_patch16_224_ft) generated and verified, awaiting Rohit's Kaggle push**; when it merges A3 closes at 10 of 10 and A4 (Grad-CAM, cross-generator) begins. Checkpoint pile to transfer to the Victus is now ~1.75 GB, ~2.1 GB after session 6.

**24 Aug — session 4 COMPLETE, matrix 8 of 10; session 5 initialised.** vgg19_fe val 90.54/test 90.55 (AUC 0.9669), 76 min against a 4.8 h worst case, early-stopped at epoch 13. It is the weakest row in the matrix and that is a **real architectural result, not a fault**: AUC 0.9669, balanced confusion matrix, trainable_params 8194 (head only, correct for fe), curve climbing 86%→90.5%. Frozen VGG19 features are less linearly separable than newer backbones', giving a coherent fe ranking for Paper 2 — vgg19 90.55 < resnet50 92.83 ≈ efficientnet_b0 92.86 < densenet121 93.48 < vit 94.75. An epoch-7 val_loss spike (0.4426, val_acc dipping to 85.15% before recovering) is reported as SGD instability, not smoothed away. All eight rows are Tesla T4, seed 42, `cifake_split_seed42.csv`, 90,000 train images, committed batch sizes; 12.9 h measured GPU time. **Session 5 (vgg19_ft, 8.0 h worst case, the heaviest run) generated, committed and pushed to GitHub, but NOT yet launched** — the Kaggle push was refused by the local permission classifier, so it awaits Rohit's one command; only session 6 (vit_ft) then remains. Note: Kaggle exposes no quota API, so remaining GPU hours could not be verified from here — the ~16 h-of-30 figure is an estimate; the non-T4 hard-abort and `time_budget_min` guard mean an exhausted quota fails fast or stops cleanly rather than corrupting a row.

**23 Aug — session 4 launched (vgg19_fe), running.** Pushed as `yaduvxnshi/authentiscan-a3-session-4` version 1 (kernel id 131730234); worst case 4.8 h. Two post-launch status checks returned `running` with no failure, so cell 1 cleared and the per-notebook `GITHUB_PAT` secret was already attached — the session-2 secret failure did not recur. **No session 4 results exist yet; the matrix stays at 7 of 10 rows** until `results_a3_s4.zip` is downloaded and merged. Two process notes: (a) this Kaggle push was executed by Claude on Rohit's explicit instruction with the token supplied inline — the §1 execution split (Kaggle pushes/launches are Rohit's) is **unchanged** and this is a one-off override, not a precedent; (b) **two credentials await rotation** — the GitHub PAT formerly pasted into `.gitignore` (never committed) and the Kaggle API token used for this push, which entered the chat transcript. Rotation steps in `handoff.md`. Remaining after session 4: vgg19 ft (session 5, heaviest in the matrix — check quota first) and vit ft (session 6).

**22 Aug (evening) — Victus carve-out decided.** New training machine: HP Victus, RTX 4070 laptop 8 GB (VRAM probe: effnet/vgg/vit fit at matrix batch sizes; densenet121@128 hits 8.05 GB → silent driver memory-fallback measured 4.7× slower per image — unusable, not merely tight). Victus GPU smoke is **bit-identical to the CPU and T4 smokes** (0.7175/0.7925) on torch 2.11.0+cu128 — four-way reproducibility for Paper 2. Decision (Rohit): 6 runs local (effnet/vgg/vit, both modes), resnet50 T4 rows kept as-is, densenet finishes in Kaggle session 2 at batch 128 — config fidelity over hardware uniformity; Paper 2's training-time table gets per-GPU annotation. Full record: plan §7a "A3 amendment — Victus carve-out"; setup guide `sem8_major/victus_setup.md`; Victus runs its own Claude session (kickoff in guide §9). Victus pending: real git clone (current copy is a ZIP, cannot commit), Omen power profile (GPU capped at 80 of 120 W), Windows Update.

**22 Aug (later) — A3 session 1 COMPLETE, G3 PASSED.** After two documented false starts (Kaggle notebook-storage glitch; Kaggle's new `/kaggle/input/datasets/<owner>/<slug>` mount convention — notebooks now autodetect the mount and hard-abort on non-T4 GPUs), the session ran on T4: resnet50_fe val 93.01%/test 92.83%, resnet50_ft val **95.66%**/test 95.93% (AUC 0.9925), both full 30 epochs. Rows merged into `results/runs.csv`; checkpoints archived locally. Times ran ~1.25× calibration and nothing early-stopped → remaining sessions re-budgeted (~34 h worst case; 2–4 this quota week, 5–6 after reset). Execution rule in force: Claude prepares, Rohit launches every push/commit. Next: session 2 (densenet121, ~6.5 h).

### Track B — implementation (guide-instructed early start). Plan written 18 Aug 2026 (`sem8_major/implementation_plan.md`), accelerated 20 Aug (§7a); next = A1. Original inputs kept for the record:

1. **Hardware first (open item 7).** RESOLVED 18 Aug: Kaggle free tier for training; local laptop (Python 3.12.10 installed, no CUDA GPU) for dev and CPU smoke tests. (The earlier "no Python installed" note was stale.)
2. **Environment.** Python 3.11+ (Miniconda suggested), PyTorch + torchvision, timm (ViT and EfficientNet weights), scikit-learn (metrics), matplotlib (figures), a Grad-CAM implementation (library or ~50 lines hand-rolled). Pin versions in an `environment.yml` — Paper 2 must report exact versions (all three reference papers do).
3. **Repo skeleton** (create in the plan session): `sem8_major/{code/{data.py, models.py, train.py, eval.py, gradcam.py}, configs/ (one YAML per experiment), data/ (gitignored), results/ (CSVs, one row per run), figures/, notebooks/}`.
4. **Data.** CIFAKE (~120k images at 32×32, small download, source: the dataset release cited as C51) with a fixed, documented train/val/test split and fixed seeds (§6 rules). GenImage: decide the test-only subset in the plan — the full corpus is impractically large; a 2–4 unseen-generator slice of a few thousand images each is enough for the cross-generator table.
5. **Experiment matrix** (from §2 and the paper's §7.6): 4 CNN backbones (ResNet50, DenseNet121, EfficientNet-B0, VGG19) × {feature extraction, fine-tuning} = 8 runs + ViT benchmark ×2 configurations = 10 core runs; then Grad-CAM on correct and incorrect predictions per model; then cross-generator evaluation (train CIFAKE → test GenImage subset); then ablations (augmentation on/off, input resolution) if time allows.
6. **Build order.** Phase 0: environment + data + split file + results-CSV schema. Phase 1: end-to-end smoke run (ResNet50 feature extraction, small subset) proving data→train→eval→CSV→Grad-CAM before any full run. Phase 2: the 10-run matrix. Phases 3–5: Grad-CAM, cross-generator, ablations. Never hand-transcribe a number: Paper 2 tables generate from `results/*.csv`.
7. **Metrics module** implements exactly the §5 equations of Paper 1 (accuracy, precision, recall, F1, AUC, AP + confusion matrices, ROC and learning curves) so Paper 2's reporting matches the review's own standards.
8. **Integrity guardrails.** No result flows into Paper 1 (already at plag check). Results live in `sem8_major/results/` for Paper 2 only. Whether early code work appears in a Minor-track WPR is the guide's call — ask before writing it into WPR 12.

---

## Appendix A — Kickoff message to paste into a fresh Claude Code session

> Read `CLAUDE.md` in full before responding. This is a two-semester B.Tech final-year project at Amity University Uttar Pradesh — Group 148, guide Dr. Richa Gupta, team Rohit / Vishal / Hardik Mehlawat. Project is AuthentiScan, AI-generated image detection.
>
> Semester 7 is the literature semester: the only deliverable is a review/survey paper plus weekly Minor Project WPRs. No code, no experiments, no results. Semester 8 is the implementation semester.
>
> Confirm you have read the file by stating: (a) which week of the Semester 7 plan we are currently in, (b) what that week's deliverable artefact is, and (c) the list of open items from Section 12 that are still unresolved. Then wait for instructions. Do not start writing anything yet.

---

## Appendix B — Standing reminders

- Semester 7 has no results. If a draft implies otherwise, that is an error.
- Two WPR tracks, kept separate.
- Every citation verified, or marked `[VERIFY]`.
- Amity template compliance beats everything except factual correctness.
- Everything submitted is PDF, exported from a template-compliant DOCX. Never authored in PDF.
- When uncertain, say so and ask. Do not fill gaps with plausible text.
