# Table 4.1 — Datasets and benchmarks (Section 4)

Table 4.1: Datasets and benchmarks on which the surveyed detection literature trains and tests, ordered by year of introduction. "—" marks a property that the review's own extraction records do not state; it is not a claim that the dataset lacks that property.

| Dataset | Introduced by | Year | Scale | Real-image source | Generators covered | Notes / stated limitation |
|---|---|---|---|---|---|---|
| ForenSynths (CNNDetection) | Wang et al. [C01] | 2020 | 720K training images (20 ProGAN categories, 18,000 fake + 18,000 real each); 11 generator-specific test sets [C01, C15] | LSUN [C01] | Train: ProGAN. Test: StyleGAN, StyleGAN2, BigGAN, CycleGAN, StarGAN, GauGAN, DeepFakes, CRN, IMLE, SAN, SITD [C01] | The GAN-era protocol: train on ProGAN, test on unseen generators. Reused as the standard training set by [C15, C16, C22]; several other detectors train on ProGAN in the same 1-/2-/4-class arrangement [C21, C39, C40, C43, C48]. Authors' own "for now" caveat: later generators may evade it [C01] |
| UniversalFakeDetect | Ojha et al. [C37] | 2023 | 720K ProGAN training images; 19 test subsets [C37, C41, C48] | — (training set inherited from ForenSynths [C01]) | ProGAN, StyleGAN, BigGAN, CycleGAN, StarGAN, GauGAN, CRN, IMLE, SAN, SITD, DeepFakes, Guided, LDM, Glide, DALL-E [C37] | Extends the ForenSynths protocol on the test side with diffusion and autoregressive subsets; its 19 subsets became the standard evaluation suite for CLIP-feature detectors [C41, C48] |
| DiffusionForensics | Wang et al. [C25] | 2023 | — | LSUN-Bedroom, ImageNet [C25] | ADM, DDPM, iDDPM, PNDM, LDM, SD-v1, SD-v2, VQ-Diffusion (8 diffusion models) [C25] | Released with the DIRE detector; scope limited to diffusion-generated images [C25] |
| GenImage | Zhu et al. [C52] | 2023 | >1M fake images plus 1,331,167 real [C52] | ImageNet [C52] | Midjourney, SD v1.4, SD v1.5, ADM, GLIDE, Wukong, VQDM, BigGAN (8) [C52] | Defines an explicit cross-generator classification task and a degraded-image task. Authors report sharp degradation cross-generator and on low-resolution, JPEG-compressed and blurred images [C52]. Later shown to carry JPEG-compression and image-size biases [C31] |
| ArtiFact | Rahman et al. [C53] | 2023 | 2,496,738 images (964,989 real / 1,531,749 fake) [C53] | — | 25 methods: 13 GANs, 7 diffusion, 5 miscellaneous [C53] | Built for robustness and used in the IEEE VIP Cup 2022 tests; authors state that state-of-the-art detectors still struggle on generators unseen during training [C53] |
| TWIGMA | Chen et al. [C56] | 2023 | — | Not applicable — a dataset of AI-generated images with metadata collected from Twitter [C56] | — | Platform-collected rather than generated for research; screened in as evidence that synthetic images already circulate in the wild [C56] |
| CIFAKE | Bird & Lotfi [C51] | 2024 | 120,000 images (60,000 real + 60,000 synthetic) [C51] | CIFAR-10 [C51] | Stable Diffusion v1.4 (latent diffusion) [C51] | Single generator at 32×32 resolution; Grad-CAM analysis shows the classification is driven by imperfections in image backgrounds [C51] |
| D3 | Baraldi et al. [C49] | 2024 | — | — | — | Large diffusion-image collection released with a contrastive detection method (ECCV 2024); screened in as a secondary study, so no full-text extraction row exists [C49] |
| Chameleon | Yan et al. [C36] | 2025 | — | — | — | In-the-wild benchmark of realistic images. Detector accuracy falls from 92.77% on AIGCDetectBenchmark and 86.88% on GenImage to 65.77% on Chameleon; the authors state the problem is far from solved [C36] |
| Community Forensics | Park & Owens [C35] | 2025 | 2.7M images from 4,803 generators [C35] | — | 4,803 generators spanning latent and pixel diffusion, GANs, and commercial models [C35] | Built to test whether generator diversity buys generalisation. Authors note the dataset is skewed toward diffusion models and that error rates remain too high for critical applications [C35] |
| WildFake | Hong et al. [C54] | 2025 | — | — | — | Hierarchical dataset of AI-generated images; screened in as a secondary study for this table only, so no full-text extraction row exists [C54] |

Provenance: every cell above is copied from `references/extraction_table.csv`, `references/screened.csv`, or `references/screening_summary.md`; nothing is inferred from outside those records, and 15 of the 77 cells are "—" because the records state no value.

---

### Notes for Week 11 assembly

1. Eleven rows × seven columns is a wide table. It will need landscape orientation or a reduced font in the DOCX, and the "Notes / stated limitation" column is the one to trim first if it does not fit (CLAUDE.md §8, requirement 4).
2. Author surnames in the "Introduced by" column follow `extraction_table.csv` where a row exists. For C49, C54 and C56 there is no extraction row; the surnames there are taken from the `references.bib` entries and should be re-checked in the Week 11 verification pass.
3. Empty cells for C49, C54 and C56 are a consequence of these being secondary studies that were never full-text extracted. If the guide wants a fuller dataset table, promoting them to full-text extraction is the fix — roughly half a day's work, and it must not be filled in by guessing.
