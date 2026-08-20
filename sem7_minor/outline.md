# Paper 1 — Outline (Week 1)

## Title (finalised)

Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches

## Objective

A review/survey paper on detecting AI-generated images (binary: real vs AI-generated). The paper surveys published detection approaches, datasets, and evaluation practice, and ends with a gap analysis that motivates the Semester 8 experimental work (transfer-learning comparison of ResNet50, DenseNet121, EfficientNet-B0, VGG19 against a ViT benchmark on CIFAKE, with Grad-CAM explainability and cross-generator testing on GenImage).

No experiments are run this semester. The paper reports no results of our own.

## Section skeleton

| § | Section | Approx. share | Word budget | Written in week (12-week plan) |
|---|---|---|---|---|
| — | Abstract (200–250 words) + 5–6 keywords | — | 200–250 | 10 |
| 1 | Introduction | 10% | ~850 | 4 |
| 2 | Background — GANs, diffusion models, generator artefacts | 12% | ~1,000 | 5 |
| 3 | Taxonomy of detection approaches | 30% | ~2,550 | 6–7 |
| 3.1 | Handcrafted / statistical / frequency-domain forensics | | ~500 | 6 |
| 3.2 | CNN-based approaches and transfer learning | | ~550 | 6 |
| 3.3 | Transformer and attention-based approaches | | ~500 | 7 |
| 3.4 | Multimodal and foundation-model-based approaches (CLIP-feature detectors) | | ~500 | 7 |
| 3.5 | Explainability in detection (Grad-CAM and related) | | ~500 | 7 |
| 4 | Datasets and benchmarks — CIFAKE, GenImage, ArtiFact, others | 12% | ~1,000 | 8 |
| 5 | Evaluation metrics | 8% | ~700 | 8 |
| 6 | Comparative analysis — master literature table + synthesis | 15% | ~1,300 | 9 |
| 7 | Challenges and gap analysis | 10% | ~850 | 10 |
| 8 | Conclusion and the case for the Semester 8 work | 3% | ~250 | 10 |
| — | References (45–60, all verified) | — | — | 11 (verification pass; assembly week) |

Word budgets assume a body of ~8,500 words excluding references, tables, and captions. This is a venue-agnostic default; revise when the Amity page/word limit (open item 2) or target venue (open item 5) is known. Budgets are targets ±20%, not hard walls.

## Citation system (fixed 12 August 2026, before section writing starts)

- Drafts cite by screened-set ID: `[C01]`, or `[C01, C24]` for multiple. IDs come only from `references/screened.csv` (decision include-primary, include-secondary, or background). No citation may appear in a section without a matching row there and an entry in `references/references.bib`.
- `references/references.bib` is keyed by the same C-IDs. At Week 11 assembly, C-IDs are replaced by IEEE-style numeric citations `[1]…[n]` in order of first appearance (IEEE numeric is the default style until the venue is chosen).
- New sources discovered during writing are not cited directly: they go through the screening protocol first (add to candidates.csv → screen → then cite).

## Status after Week 1

- Scope and structure fixed as above.
- Search protocol defined in `search_protocol.md`.
- Section placeholder files created under `sections/`.
- Literature collection (target 70–90 candidates) begins in Week 2.

## Open points carried from Week 1

- Target venue for the paper not yet chosen (affects reference style and length).

## Week calendar

Week 1 = 20 July 2026 – 26 July 2026. Each week runs Monday–Sunday; Week n starts 7×(n−1) days after 20 July 2026. The NTCC window is 20 July – 9 October 2026 = 12 weeks (Week 12 is short: 5–9 October), so there are **12 WPRs**, not 13. (Rohit once mentioned 13 WPRs — flagged, unresolved; if the department expects a 13th, it would be a final/summary WPR, to be confirmed with the guide.)

## Status (15 August 2026)

All content complete and reviewer-verified: abstract + Sections 1–8 (~9,850 words), Table 1 (datasets), Table 2 (48-study master table), three figures, 73-entry verified reference list. Two assembled drafts exist in `submission/`: draft v1 (single-column, IEEE numeric) and draft v2 (journal-style two-column, author–year, per the three sample papers — format only). **Draft v2 was submitted for the department plagiarism check on 15 August 2026; result pending.** Remaining paper work: Rohit's rewrite pass, guide decisions (venue, reference trim, template), Amity-template restyle, WPR uploads on their Wednesdays. Separately, implementation (code) begins early per the guide's 15 Aug instruction — see CLAUDE.md §13 Track B.

## Acceleration mode (adopted 12 August 2026)

Content work for Weeks 4–11 is executed ahead of calendar as sprints, in week order, each gated by a review pass (citation keys checked against `screened.csv`, numbers checked against `extraction_table.csv`, no own-results claims, register and word budget). The WPR for a week is rendered once that week's deliverable is approved, carries its scheduled Wednesday date, and is uploaded on schedule. Calendar Week 12 (guide review, corrections, submission pack) still happens in real time — guide review cannot be accelerated. Drafts remain inputs for Rohit's own rewrite pass before submission (plagiarism/AI-text rule in CLAUDE.md §10).
