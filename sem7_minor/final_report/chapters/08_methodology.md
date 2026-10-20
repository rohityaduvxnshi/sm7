# 8. REVIEW METHODOLOGY

This chapter sets out how the studies discussed in the rest of the report were found, filtered, read and checked. The procedure was written down as a protocol in Week 1 (20–26 July 2026), before a single paper had been collected, so that every record would be judged by the same rules and the process could be reported afterwards. The number of records entering and leaving each stage was logged as the work progressed, which allows the selection to be drawn as a PRISMA-style flow diagram.

## 8.1 Search Protocol

The protocol named six bibliographic databases: IEEE Xplore, ScienceDirect, SpringerLink, the ACM Digital Library, arXiv and Google Scholar. The searches were driven by eight query seeds:

- "AI-generated image detection"
- "synthetic image detection"
- "GAN image detection"
- "diffusion image detection"
- "deepfake image forensics"
- "CIFAKE"
- "GenImage"
- "cross-generator generalization"

The search was organised into six topic strands that follow the structure of the taxonomy: GAN-era CNN detection; diffusion-era detection; frequency-domain and handcrafted forensics; ViT- and CLIP-based detection; datasets, benchmarks and surveys; and explainability together with background material. The searches themselves were carried out in Week 2 (27 July to 2 August 2026). The seeds were run against arXiv, against the pages of publishers and proceedings (IEEE, ACM, CVF, NeurIPS, ICML, ICLR, AAAI, PeerJ and Wiley) and against Google Scholar, and the raw list of hits for each strand was kept. Every candidate record stores the URL at which the paper's existence was confirmed. The year stored with a record is the year of its publication venue, which can be one year later than the paper's first appearance on arXiv.

## 8.2 Inclusion and Exclusion Criteria

Each record was judged against the four inclusion criteria and the four exclusion criteria laid down in the protocol. Table 8.1 places the two lists side by side.

Table: 8.1 | Inclusion and exclusion criteria
| Inclusion criteria | Exclusion criteria |
|---|---|
| Published between 2019 and 2026 | Deepfake work on video only or audio only |
| Deals with still images, not video or audio | No quantitative evaluation |
| Presents numerical results, for example accuracy, AUC or F1 | Not written in English |
| Peer-reviewed, or a preprint that is well cited | Full text cannot be accessed |

The date window applies to detection studies only. Background references on generator models, backbone networks and explanation methods are allowed to fall outside it by design, and some of these classic papers date from 2014 to 2018.

## 8.3 Screening and Selection

The searches returned 101 records. Once 26 duplicates had been removed, 75 unique records remained, and each was screened on its title and abstract against the criteria in Table 8.1. Apart from the single exclusion described below, out-of-scope items had already been filtered out at search time, so they were never counted among the identified records. In total, 74 records were included and divided into three groups:

- 48 primary studies on detection methods and datasets, each read in full (Section 8.4);
- 11 secondary studies, retained and drawn on selectively;
- 15 background references, covering generators, backbone networks, explanation methods and earlier surveys.

Only one record was excluded: a preprint with a single citation, which failed the well-cited criterion for preprints when citation counts were checked in Week 3. Figure 8.1 traces the records through each stage.

[[FIGURE:prisma|8.1|Records at each stage of the review, from the database searches to the final set: 101 identified, 26 removed as duplicates, 75 unique records screened on title and abstract, 1 excluded and 74 included (48 primary studies, 11 secondary studies and 15 background references).]]

## 8.4 Data Extraction

During Week 3 (3–9 August 2026), all 48 primary studies were read in full, and each was entered as one row of an extraction table. The table has eight fields, listed in Table 8.2. These fields had been fixed in the Week 1 protocol, before any paper was read, and they later became the columns of the master comparison table in Chapter 12.

Table: 8.2 | Fields recorded for each primary study
| Field | What is recorded |
|---|---|
| Study (author, year) | First author and year of publication |
| Detection approach | A brief summary of the method or study design |
| Model or architecture | The network or classifier that makes the decision |
| Dataset used | The data used for training and testing |
| Generator(s) covered | The generators whose images the study uses |
| Reported accuracy / AUC | Headline result, in the metric the authors chose |
| Cross-generator tested? | Yes or No: is any test generator held out of training? |
| Key limitation | The main weakness that the authors themselves state; where they state none, the cell says so and may add the review's own note on the study's scope |

When a value could not be confirmed from a paper's own text, its cell was flagged for verification instead of being filled with an estimate. Ten cells were flagged in this way. All ten were later settled from the full texts, and every settled value was then checked against its paper a second time, so the finished table contains no flagged cells.

Reading the full texts also changed the cross-generator flag of two studies to No. {C07} showed the frequency-domain artefact they studied across the GANs they analysed, but none of their experiments trains on one GAN and then tests on a GAN held out of training; the result on unseen architectures that they refer to comes from {C01}. {C64} ran a cross-dataset test that switched the image content between ImageNet and Oxford-IIIT Pet, yet the generated images on both sides came from one Stable Diffusion image-to-image process, so no unseen generator was involved. Neither study is counted as cross-generator evidence in Chapters 12 and 13.

## 8.5 Taxonomy Assignment

After extraction, the primary studies were placed in the taxonomy that Chapter 9 describes. Its five families are separated by where a detector's evidence comes from: handcrafted, statistical and frequency-domain forensics; CNN-based approaches and transfer learning; transformer and attention-based approaches; multimodal and foundation-model-based approaches; and explainability in detection. The assignment was recorded against each study in the screening records and was fixed in Week 4, before the text of Chapter 9 was drafted. Three studies sit across two families and were assigned to both. Four primary studies are concerned mainly with datasets and benchmarks rather than with a detection method; these were left outside the five families and are analysed in Chapters 10, 12 and 13 instead. The number of studies in each family is reported in Chapter 9.

## 8.6 Verification and Quality Control

Three kinds of checks were built into the process, so that each reference and each quoted value can be traced back to a source.

The first concerned citations. Before drafting began, a rule was fixed that drafts would refer to a study only through its screening identifier, and that a BibTeX file of the included references would be keyed with the same identifiers. A study could be cited only if it had a row in the screening records and an entry in this file, and a paper discovered later, during writing, had to pass screening before it could be cited.

The second concerned the identifiers themselves. All 74 identifiers in the BibTeX file were opened and compared with an authoritative record: the arXiv metadata record for an arXiv identifier, the Crossref record for a DOI, and, for one paper without a DOI, the PMLR proceedings page. Titles and authors were compared with the screening rows, and for a DOI the venue, volume and pages were compared as well. All 74 were confirmed and none remained pending; six had already been spot-checked in Week 2 on their arXiv abstract pages. The pass found one wrong publication year. The journal version of one study [C50] is dated June 2026, but the screening files had recorded 2025, the year of acceptance that appears inside its DOI; the record was corrected to 2026. Where a preprint and its published version differed in title or author list, the published version was cited.

The third concerned the numbers. A script compared the master comparison table with the extraction records, and every one of the 48 rows agreed with them in its author names, accuracy figures and cross-generator flags. For this report the wording of the table was shortened, and a second script confirmed that every number and every Yes/No flag in the version printed in Chapter 12 still equals the checked original. Every value that Chapters 9 to 13 quote from a study is taken from the extraction records.
