# GenImage access note — B0 deliverable (18 August 2026)

Resolves the `[VERIFY]` item from `implementation_plan.md` §3/§9: how the four cross-generator
test subsets (Midjourney, ADM, BigGAN, VQDM) are obtained. Checked 18 Aug 2026 by web
verification only — no download has been performed yet. Facts below marked `[VERIFY at
download]` still need one confirmation pass when the data is actually fetched (B5 at the
latest; earlier is better).

## What was verified

- **Official release** (github.com/GenImage-Dataset/GenImage): distributed per generator via a
  public Google Drive folder (link in the repo README, added March 2024) and Baidu Yunpan
  (access code `ztf1`). No form or login beyond a Google account. Folders are per generator
  with train/val splits of paired real (ImageNet) and fake images. Full per-generator subsets
  are far too large for this project (search results cite Kaggle mirror sizes of ~39 GB for
  ADM, ~24 GB for BigGAN, ~107 GB for one Midjourney part) — full downloads are ruled out.
- **Kaggle mirrors** exist but are fragmentary: the most visible one
  (kaggle.com/datasets/vtphatt2/genimage-stable-diffusion-v1-4) covers only the SD v1.4
  subset, which our plan **excludes** (same generator family as CIFAKE). Per-generator full
  mirrors exist but carry the same size problem locally; attached natively inside a Kaggle
  notebook the size does not matter, but coverage of all four needed generators by one
  well-formed mirror was not confirmed. `[VERIFY at first Kaggle login]`
- **Tiny-GenImage** (huggingface.co/datasets/TheKernel01/Tiny-GenImage): a 35,000-image,
  8.36 GB parquet redistribution covering real images plus all eight GenImage generators —
  including all four we need. License CC-BY-NC-SA-4.0 (fine for academic use, cite both this
  mirror and the GenImage paper, C-key per `references.bib`). Per-generator counts are not
  stated on the card; at ~35k/9 sources it should land near the plan's 2,000–3,000 balanced
  images per generator. `[VERIFY at download: per-generator real/fake counts and that "real"
  is GenImage's paired ImageNet real set]`

## Decision (recommended route)

**Update 18 Aug 2026, API-verified:** the Tiny-GenImage original lives on Kaggle —
`yangsangtai/tiny-genimage` (8.35 GB, CC BY-NC-SA 4.0; the Hugging Face copy re-hosts it as
parquet). Confirmed via authenticated API file listing: it preserves GenImage's official
directory convention `imagenet_ai_<date>_<generator>/{train,val}/{ai,nature}` — per-generator
folders with paired real ("nature") images as loose PNGs, no parquet conversion needed.

1. **Primary: `yangsangtai/tiny-genimage` on Kaggle.** For the B5 evaluation, attach it
   natively to the Kaggle notebook (size is then irrelevant); locally, download only the
   folders for the four target generators if a local check is wanted. Use each generator's
   `val` split as the test slice. At first use, verify all four target generators are present
   and count real/fake per generator `[VERIFY at download]`.
2. **Mirror of the same data: Tiny-GenImage on Hugging Face** (parquet; needs a conversion
   step to the folder layout).
3. **Fallback: official Google Drive**, downloading only enough zip parts of each of the four
   generators to fill 2,000–3,000 balanced images per generator.

SD v1.4/v1.5 and Wukong subsets are excluded in either route (SD family = CIFAKE's generator;
Wukong is SD-derived and outside the plan's four).

## Still open (moves to the Kaggle-side checklist)

- Confirm Tiny-GenImage per-generator counts and real-image provenance at download.
- Confirm whether a single Kaggle-native mirror of the four subsets exists worth attaching
  instead, once Rohit's Kaggle account is set up.
