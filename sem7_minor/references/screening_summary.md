# Literature Collection Round 1 — Screening Summary (Week 2)

Counts for the PRISMA-style flow figure (Section: methodology of the review).

| Stage | Count |
|---|---|
| Records collected via protocol searches (six topic strands, query seeds from `search_protocol.md`) | 101 |
| Duplicates removed | 26 |
| Unique candidates screened by title/abstract (`candidates.csv`) | 75 |
| Included — primary detection/dataset studies (full-text extraction in Week 3) | 48 |
| Included — secondary studies (kept; used selectively) | 11 |
| Background references (generators, backbones, XAI methods, prior surveys) | 15 |
| Excluded | 1 (TruthLens, arXiv:2503.15867 — preprint with 1 citation, fails well-cited criterion; other out-of-scope items were filtered at search time per protocol) |

## How the search was run

Candidates were collected using the protocol's query seeds against arXiv, publisher/proceedings pages (IEEE, ACM, CVF/CVPR/ICCV/ECCV/WACV, NeurIPS/ICML/ICLR/AAAI, PeerJ, Wiley) and Google Scholar, in six topic strands matching the paper's taxonomy: GAN-era CNN detection, diffusion-era detection, frequency/handcrafted forensics, ViT/CLIP-based detection, datasets/benchmarks/surveys, and explainability + background. Raw per-strand lists are in `references/raw/`.

Every entry carries the URL where its existence was confirmed. Year recorded = publication venue year (arXiv submission year can be one earlier).

## Spot-check log (Week 2; full verification pass is Week 11)

Six entries re-verified by opening the arXiv abstract page directly — exact title and first author matched in all six:

| id | arXiv | Checked |
|---|---|---|
| C01 | 1912.11035 | title + first author (Sheng-Yu Wang) match |
| C51 | 2303.14126 | title + first author (Jordan J. Bird) match |
| C39 | 2402.19091 | title + first author (Christos Koutlis) match |
| C24 | 2211.00680 | title + first author (Riccardo Corvi) match |
| C36 | 2406.19435 | title + first author (Shilin Yan) match |
| C61 | 1610.02391 | title + first author (Ramprasaath R. Selvaraju) match |

## Identifier checks — RESOLVED 8 August 2026 (Week 3)

- C15 (LGrad): DOI 10.1109/CVPR52729.2023.01165 confirmed via doi.org → IEEE Xplore 10203908. No arXiv version exists. CVF open access pp. 12105–12114 is the free full text.
- C32 (DRCT): formal citation is PMLR 235:7621–7639, 2024 (PMLR carries no DOI).
- C55 (Synthbuster): DOI 10.1109/OJSP.2023.3337714 confirmed → Xplore 10334046; IEEE Open Journal of Signal Processing, vol. 5, 2024 (the 2023 in the DOI suffix is acceptance-year encoding).
- C64 (Aghasanli): IEEE DOI exists — 10.1109/ICCVW60793.2023.00053 (Xplore 10350382); not CVF-only.
- C42 (AntifakePrompt): 77 citations (Semantic Scholar) — passes well-cited-preprint criterion; still arXiv-only.
- C47 (MoLE): 34 citations — acceptable; still arXiv-only.
- C50 (LASTED): published as IEEE Transactions on Artificial Intelligence, DOI 10.1109/TAI.2025.3641104 — cite the journal version, not the preprint.
- C65 (TruthLens): 1 citation — FAILS the well-cited-preprint criterion; moved to excluded. (Caution: do not conflate with same-named arXiv:2503.15342.) Rohit can override this decision.

## Remaining [VERIFY] items (extraction cells, not identifiers) — ALL RESOLVED 12 August 2026

All 10 open cells in `extraction_table.csv` (C05, C07, C15, C29, C32, C40, C64) were filled from the papers' own full text on 12 August 2026. Nothing remains open; `extraction_table.csv` now contains zero `[VERIFY]` markers.

Resolved cells and source used:

- C05 `reported_accuracy_auc` — 90.3% uncompressed / 90.1% at JPEG QF=95 confirmed verbatim in Section 4 (source identification). Source: arXiv:1812.11842 PDF.
- C07 `cross_generator_tested` — changed to **no**. Frank et al. Sections 4.1–4.5 contain detection, upsampling, source identification, frequency-domain training and perturbation experiments, but no train-on-one-GAN / test-on-unseen-GAN experiment; the unseen-architecture claim they cite belongs to Wang et al. (2020). Source: arXiv:2003.08685 PDF.
- C15 `dataset_used`, `generators_covered`, `reported_accuracy_auc` — training set of Wang et al. (20 ProGAN categories, 18,000 fake + 18,000 real each; 1-/2-/4-class settings); 8 test models (ProGAN, StyleGAN, StyleGAN2, BigGAN, CycleGAN, StarGAN, GauGAN, Deepfake); 86.3% mean ACC / 92.7% mean AP (1-class, StyleGAN-bedroom), which is the +11.4% ACC / +13.4% AP gain over FrePGAN quoted in the abstract. Source: CVF open-access PDF, Sections 4.3.2–4.3.3 and Table 3.
- C29 `key_limitation` — authors' own Section 5.6 wording: both their model and the baseline still overlap real and fake features on unseen generators (Midjourney, ADM, BigGAN); Section 5.5.5 states LaRE alone is insufficient as sole input because of latent-space information loss. Source: arXiv:2403.17465 PDF.
- C32 `key_limitation` — taken from the paper's explicit "Limitations" paragraph in Section 5 (Discussions): smaller gain on non-diffusion/GAN images, and evaluation limited to globally generated images rather than small locally generated regions. Source: PMLR v235 PDF (chen24ay).
- C40 `key_limitation` — taken from the paper's "Limitations and future works" paragraph: room to improve on diffusion models such as Guided, and the GAN vs diffusion artefact relationship left to future work. Source: arXiv:2312.16649 PDF.
- C64 `reported_accuracy_auc`, `cross_generator_tested` — Tables 1–3: within-dataset best 99.5% / 96.7% / 99.7% / 99.4% (fine-tuned ViT + MLP head), SVM on fine-tuned features 93.0–97.2%, cross-dataset 81.3% and 84.0%. Cross-generator set to **no**: the cross-dataset test swaps image domains (ImageNet vs Oxford-IIIT Pet) but both sets are generated by the same Stable Diffusion image-to-image pipeline. Source: CVF open-access PDF (ICCV2023W/DFAD).

Note for the Week 11 pass: two `cross_generator_tested` values changed from `[VERIFY]` to `no` (C07, C64). Section 6/7 text must not count these two studies as cross-generator evidence.

## Notes

- The 48 primary studies are the input to Week 3's `extraction_table.csv` (one row per paper, all eight extraction columns).
- The paper's final reference list (target 45-60) is assembled in Week 11 from primary + background first, then secondary as needed; not every screened-in study must be cited.
- Background classics (2014-2018) sit outside the 2019-2026 inclusion window by design; the window applies to detection studies, not to generator/backbone/XAI method references.
