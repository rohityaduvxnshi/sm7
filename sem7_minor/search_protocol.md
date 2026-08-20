# Literature Search Protocol (Week 1)

Defined before collection starts so that screening is consistent and can be reported in the paper (PRISMA-style flow figure planned).

## Databases

1. IEEE Xplore
2. ScienceDirect
3. SpringerLink
4. ACM Digital Library
5. arXiv
6. Google Scholar

## Query seeds

- "AI-generated image detection"
- "synthetic image detection"
- "GAN image detection"
- "diffusion image detection"
- "deepfake image forensics"
- "CIFAKE"
- "GenImage"
- "cross-generator generalization"

## Inclusion criteria

- Published 2019–2026.
- Image domain (still images), not video or audio.
- Reports quantitative results (accuracy, AUC, F1, or similar).
- Peer-reviewed, or a well-cited preprint.

## Exclusion criteria

- Video-only or audio-only deepfake work.
- No quantitative evaluation.
- Non-English.
- Full text not accessible.

## Screening process

1. **Identified** — all hits from the query seeds across the six databases, deduplicated. Recorded in `references/candidates.csv`. Target: 70–90.
2. **Screened** — title/abstract screening against the criteria above. Recorded in `references/screened.csv`. Target: ~45.
3. **Included** — full-text read; one row per paper in `references/extraction_table.csv`.

Counts at each stage are recorded for the PRISMA-style flow figure.

## Extraction table columns (fixed now, filled in Week 3)

`Study (Author, Year) | Detection Approach | Model / Architecture | Dataset Used | Generator(s) Covered | Reported Accuracy / AUC | Cross-Generator Tested? | Key Limitation`

## Verification rule

Every included reference gets one line in `references/verification_log.md` confirming its DOI / arXiv ID was opened and checked. No unverified citation enters the paper.
