# -*- coding: utf-8 -*-
"""Content for the Group 148 Project Progress Report and NTCC project diary.

Every figure here is copied from the repository's own records:
sem7_minor/sections/*.md, sem7_minor/tables/, sem8_major/results/runs.csv.
"""

GROUP = "148"
TITLE_L1 = "Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision"
TITLE_L2 = "Transformer, and Explainable Approaches"
AREA = "Artificial Intelligence and Machine Learning (Computer Vision)"
SESSION = "Academic Session: 2026-27 "
GUIDE = "Dr. Richa Gupta "
PROGRAMME = "Programme:- B.TECH CSE "
YEARSEM = "Year/Semester:- 4th Year /7th Semester "

STUDENTS = [
    ("A2305223472", "Rohit Yadav"),
    ("A2305223568", "Vishal"),
    ("A2305223449", "Hardik Mehlawat"),
]

# ---------------------------------------------------------------- Paper Summary
SUMMARY = [
("h", "Introduction"),
("p", "Image generators such as generative adversarial networks and, more recently, diffusion "
      "models have made synthetic imagery cheap to produce and difficult to identify by eye. The "
      "practical consequences are already visible: fabricated photographic evidence, misinformation "
      "carried by realistic images, impersonation, and the contamination of image corpora scraped "
      "from the web that later become training data for other models. Manual inspection does not "
      "scale to the volume involved, so automated detection of AI-generated images has become a "
      "working requirement rather than an academic exercise."),
("p", "The technical difficulty is not building a detector that works. Published detectors reach "
      "near-perfect accuracy when the images they are tested on come from the same generator they "
      "were trained on. The difficulty is that this accuracy does not survive a change of generator. "
      "Much of what a detector learns is a consequence of one generator's design — its upsampling "
      "operator, its particular training run, its decoder — so a new generator that changes any of "
      "those does not merely present harder examples, it removes the evidence. The literature records "
      "the drop directly: a ResNet-50 reported at 99.9% accuracy on its own training generator scores "
      "54.9% on an unseen one, and detectors reaching 92.77% mean accuracy on a standard benchmark "
      "reach 65.77% on realistic images collected in the wild. This cross-generator generalisation gap "
      "is the central open problem in the field and is the organising idea of this project."),
("p", "This report covers the first phase of a two-semester project. The Semester VII deliverable is "
      "a review paper, which surveys and compares published detection methods and ends by identifying "
      "a specific gap for the second phase to fill. Studies were collected under a protocol fixed "
      "before collection began: six databases (IEEE Xplore, ScienceDirect, SpringerLink, the ACM "
      "Digital Library, arXiv and Google Scholar), eight query seeds covering GAN, diffusion and "
      "dataset-specific terms, and inclusion limited to still-image work published between 2019 and "
      "2026 that reports quantitative results and appears either in a peer-reviewed venue or as a "
      "well-cited preprint. Video and audio deepfake detection were excluded. The searches returned "
      "101 records; removing 26 duplicates left 75 for title-and-abstract screening, of which 74 were "
      "retained — 48 primary studies read in full and entered into a structured extraction table, 11 "
      "secondary studies used selectively, and 15 background references covering generators, backbones "
      "and explanation methods. The surveyed work is grouped below by the origin of the evidence a "
      "detector uses."),

("h", "1. Handcrafted, Statistical and Frequency-Domain Forensics"),
("p", "Fourteen of the 48 primary studies detect generated images by measuring a property of the "
      "signal rather than by learning one end to end. The starting observation is that the repeated "
      "upsampling steps inside a generator leave periodic traces that are visible in the frequency "
      "spectrum even when nothing is visible in the picture itself. Methods in this group classify the "
      "DCT coefficients, the azimuthal average of the Fourier spectrum, co-occurrence matrices of "
      "neighbouring pixels, or a per-model fingerprint estimated as the average residual of that "
      "model's output. The reported figures are the highest anywhere in the review: 100.00% on FFHQ "
      "from DCT coefficients, above 99% from co-occurrence matrices, 99.2% on uncompressed "
      "1024×1024 images, and 100% on a self-assembled face set from as few as 20 labelled samples."),
("p", "Those figures describe narrow conditions, and the qualifying results appear alongside them "
      "almost immediately. The same spectral-decay feature that gives 99.2% at full resolution falls to "
      "88.8% at 256×256 and becomes unusable once the image passes through 85% JPEG compression, "
      "because compression discards exactly the high frequencies the method reads. More damagingly, the "
      "traces are a consequence of a design choice rather than of synthesis itself: retraining the "
      "generators with bilinear upsampling instead of the usual operator takes detection accuracy built "
      "on those traces from 84.8–99.8% down to 0–0.3%. Later work in this group replaces "
      "hand-chosen filters with a learned frequency front-end, which is more robust in practice but "
      "inherits the same underlying dependence on how a particular generator was built."),

("h", "2. CNN-Based Detection and Transfer Learning"),
("p", "Nineteen studies — the largest group — treat detection as ordinary binary image "
      "classification and solve it with a convolutional network pretrained on ImageNet, either frozen "
      "as a feature extractor or fine-tuned end to end. The line begins with a broad claim: a ResNet-50 "
      "trained only on ProGAN images, with careful data augmentation, averages 90.8 mAP over eleven "
      "unseen GAN architectures. Later work raises that with contrastive training, reaching 95.6% "
      "accuracy and 0.997 AUC, and with ensembles that deliberately hold a generator out of training, "
      "reaching 0.9995 AUC. Patch-level variants restrict the receptive field so that the classifier is "
      "forced onto local texture rather than global composition."),
("p", "The arrival of diffusion models removed most of that margin, and the comparison table records "
      "the collapse twice. GAN-trained detectors tested on GLIDE, Latent Diffusion, Stable Diffusion, "
      "ADM and DALL-E 2 fall to roughly 60–76% accuracy on uncompressed images and to about "
      "50–61% once those images are compressed and resized. Measured differently, the same loss is "
      "an average 15.2% AUROC drop, and it is asymmetric: a diffusion-trained detector still reaches "
      "94.26% average detection probability on GAN images, while a GAN-trained one manages 26.34% in "
      "the reverse direction. The problem then repeats inside the diffusion family itself, where a "
      "ResNet-50 at 99.9% on its training generator scores 54.9% on another."),
("p", "The response visible in the most recent rows of this group is to stop giving the classifier the "
      "image. Instead the network classifies something derived from it — the gradient map taken from "
      "a pretrained model, for 86.3% mean accuracy over eight test generators; the relationships between "
      "neighbouring pixels, for 92.2% over 28 generators; or the residual between an image and its own "
      "diffusion reconstruction, for 99.9% average accuracy over eight diffusion models. A related idea "
      "removes the trained classifier altogether and scores an image by its autoencoder reconstruction "
      "distance. One caution recurs across this group and matters for the second phase of this project: "
      "fifteen of the 48 studies train on the same ProGAN distribution, so a large share of the "
      "published cross-generator evidence measures one particular transfer rather than transfer in "
      "general."),

("h", "3. Transformer and Attention-Based Approaches"),
("p", "Only two of the 48 primary studies belong here, which is itself a finding worth recording. A "
      "vision transformer divides an image into patches and models the relationships between them with "
      "self-attention, which suits semantic content but carries no obvious advantage when the evidence "
      "is a low-level forensic trace. The one study in the surveyed set that compares the two families "
      "under genuinely matched conditions trains a ViT-Base and an EfficientNetV2-M on the same data "
      "and tests both across fifteen manipulation methods: the CNN is better in-domain at 81.1% "
      "accuracy but falls to 47.0–57.0% on methods it has not seen, while the ViT is weaker "
      "in-domain and holds steadier at about 62.0%. The general caveat identified in this review is "
      "that backbone comparisons in this literature are usually confounded, because a change of "
      "architecture normally arrives together with a change of pretraining data and training objective, "
      "so the architecture is rarely the only variable. That observation is one of the direct reasons "
      "for the design of the second phase."),

("h", "4. Multimodal and Foundation-Model-Based Detection"),
("p", "Eight studies build on the finding that a large vision-language model trained for something "
      "else entirely already separates real images from generated ones. With CLIP's image encoder left "
      "frozen, a nearest-neighbour rule and a simple linear probe gain 15.07 mAP and 25.90% accuracy on "
      "unseen diffusion and autoregressive models relative to the CNN baselines of the time. The "
      "strategies built on that result read the same frozen features in different ways: a few-shot "
      "linear SVM at about 90.0% average AUC over 18 generators, intermediate encoder blocks rather "
      "than the final layer at 91.5% accuracy and 98.8 AP over 20 test sets, lightweight adapters at "
      "98% and 95% accuracy on unseen GANs and diffusion models, prompt tuning at 98.06% mAP over 18 "
      "unseen generators, and an orthogonal subspace decomposition at 99.41% mAP and 95.19% mean "
      "accuracy. These are currently the strongest cross-generator results in the review, and their "
      "common property is that the representation itself is never trained on detection data."),

("h", "5. Explainability in Detection"),
("p", "Explanation analysis appears in only four of the 48 rows. Grad-CAM and Grad-CAM++ are the "
      "standard tools: they weight the feature maps of a convolutional layer by the gradient of the "
      "class score and produce a heatmap of where the network looked. Applied to the small CNN released "
      "with the CIFAKE dataset, Grad-CAM shows that the classifier keys on small imperfections in image "
      "backgrounds rather than on the main subject — a useful result, because it exposes a shortcut, "
      "and a limited one, because it does not say which property of those pixels is synthetic. The "
      "remaining three rows are a patch-level map of which regions are detectable at all, a "
      "prototype-based classifier that is interpretable by construction, and a quantitative comparison "
      "of five explanation methods on a single detector. Only one of the four also carries a "
      "cross-generator test, so on the evidence of the table, explainability and generalisation are "
      "studied separately."),

("h", "6. Datasets, Benchmarks and Evaluation Metrics"),
("p", "Eleven datasets were compared in a single table recording, for each, the introducing study, the "
      "year, the scale, the source of the real images, the generators covered and the limitation its "
      "own authors state. The line of development runs from the GAN-era ForenSynths protocol — train "
      "on ProGAN, test on eleven unseen generators — through the diffusion-era GenImage and ArtiFact "
      "collections, to in-the-wild sets such as Chameleon and TWIGMA. Three problems recur. GenImage's "
      "real and generated images differ systematically in JPEG compression and image size, so a "
      "classifier can score well by reading those properties instead of any forensic trace; removing "
      "both biases raises cross-generator accuracy by more than eleven points for both a ResNet50 and a "
      "Swin-T. A single-generator dataset such as CIFAKE cannot expose a cross-generator drop at all. "
      "And every dataset fixes its generator list at publication, so all of them go stale."),
("p", "Eight evaluation metrics were then defined as numbered equations — accuracy, precision, "
      "recall, F1 score, false positive rate, AUC, average precision and mean average precision — "
      "and the review examined how the surveyed studies actually report against them. Roughly 38 quote "
      "an accuracy figure, 14 an average precision and 9 an AUC, and about 23 quote an accuracy figure "
      "and nothing else. Averages can hide the worst case: one spectrum classifier averaging 97.2% "
      "fails outright on a single generator inside its own test set. This is a direct argument for "
      "evaluating candidate architectures under one protocol rather than assembling headline figures "
      "from separate papers."),

("h", "7. Comparative Analysis and the Gap Identified"),
("p", "All 48 primary studies were placed in a single comparison table, ordered by year, with eight "
      "columns: study, detection approach, model or architecture, dataset used, generators covered, "
      "reported accuracy or AUC, whether a cross-generator test is reported, and the limitation the "
      "authors themselves state. The last two columns are what this review adds to the conventional "
      "comparison, and every count in the analysis was obtained by tallying a column of the table so "
      "that it can be re-checked against it. The finished table was verified against the extraction "
      "records by script, and all 48 rows matched with no discrepancy in author strings, accuracy "
      "figures or cross-generator flags."),
("p", "The counts give the shape of the field. Cross-generator evaluation is now common practice but "
      "not universal: 36 of the 48 studies report one and 12 do not. Twenty cover GAN-era generators "
      "only, eight diffusion-family generators only and nineteen cover both. Fifteen share the ProGAN "
      "training distribution. Ten name robustness to compression, resizing or other degradation in "
      "their own stated limitation, which makes it the most commonly acknowledged weakness in the "
      "table. Explanation analysis appears in four rows."),
("p", "Reading those counts together produces the gap. Several studies do compare architectures under "
      "one protocol, and several do produce an explanation analysis, but no row of the table combines "
      "all four of the following: several ImageNet-pretrained CNN backbones trained under a single "
      "protocol, a Vision Transformer benchmark trained under the same protocol, an analysis of what "
      "the trained models attend to, and a cross-generator test. Each element is well established "
      "somewhere in the table; the four together are not reported anywhere in it. That combination is "
      "the gap this review identifies, and it defines the study designed for the project's second "
      "phase: a transfer-learning comparison of ResNet50, DenseNet121, EfficientNet-B0 and VGG19, each "
      "in a feature-extraction and a fine-tuning configuration, benchmarked against a Vision "
      "Transformer under matched conditions on CIFAKE, with Grad-CAM applied to correct and incorrect "
      "predictions and a cross-generator test on a subset of GenImage."),

("h", "8. Implementation Work Begun on the Project Guide's Instruction"),
("p", "Following the guide's instruction of 15 August 2026 to begin preparing the implementation code "
      "ahead of Semester VIII, the experimental pipeline was built and the core experiment matrix has "
      "since been completed. None of what follows appears in the review paper, which reports no "
      "experimental results of its own; these numbers belong to the second phase of the project."),
("p", "The pipeline is configuration-driven: one YAML file per experiment, and every run logs its "
      "seed, split file, optimiser, learning rate, batch size, epoch count, parameter counts, hardware "
      "string, library versions and wall-clock training time into a results CSV, so that no number is "
      "transcribed by hand into a document. CIFAKE, which holds 120,000 images at 32×32 resolution, "
      "was split once with seed 42 into 90,000 training, 10,000 validation and 20,000 test images; that "
      "split file is committed and is never regenerated, and the official test set is used only for "
      "final evaluation. Training ran on the free tier of Kaggle notebooks, and the pipeline was proved "
      "end to end on the laptop CPU before any GPU time was spent on it."),
("p", "The full matrix of five backbones in two transfer-learning modes — ten runs — is now "
      "complete. Every run used the same Tesla T4 GPU, the same seed, the same split file and its "
      "committed batch size, for 19.89 hours of measured GPU time in total. Under fine-tuning the test "
      "accuracies are ViT-B/16 98.89%, VGG19 97.91%, DenseNet121 97.60%, EfficientNet-B0 97.56% and "
      "ResNet50 95.93%. Under feature extraction they are ViT-B/16 94.75%, DenseNet121 93.49%, "
      "EfficientNet-B0 92.87%, ResNet50 92.83% and VGG19 90.55%."),
("p", "Three observations are being carried into the second-phase write-up. The Vision Transformer "
      "wins in both modes, which is a direct answer to the CNN-versus-transformer question the project "
      "set out to ask. VGG19 inverts between the two modes — last under feature extraction and second "
      "under fine-tuning, with by far the largest gain of the five — which is consistent with its "
      "frozen ImageNet features encoding object semantics that transfer poorly to a task whose evidence "
      "is low-level texture. And the three fine-tuned results between 97.5% and 97.9% lie within a "
      "third of a percentage point of one another, so on a single seed they will be reported as "
      "statistically indistinguishable rather than ranked. Three of the ten runs stopped at the "
      "30-epoch ceiling with validation loss still improving, so those three are lower bounds rather "
      "than converged results and reruns at a higher ceiling have been prepared. Grad-CAM analysis "
      "across all five models and the cross-generator evaluation on GenImage are the next steps."),

("h", "Conclusion"),
("p", "The review paper is complete in draft: an abstract with six keywords, eight sections totalling "
      "roughly 9,850 words, a dataset comparison table covering 11 datasets, the master comparison "
      "table covering all 48 primary studies, and two figures. Every reference identifier in the "
      "bibliography — 74 in total — was opened and checked against its arXiv, Crossref or "
      "proceedings record, with the result logged one line per reference. The assembled draft was "
      "submitted for the departmental plagiarism check on 15 August 2026 and the result is awaited."),
("p", "Three conclusions carry into the second phase. Generalisation across generators is a structural "
      "problem rather than an engineering inconvenience, because a change of generator design can "
      "remove the evidence a detector relies on rather than merely obscure it. The strongest published "
      "cross-generator results share one of three properties: a representation that was never trained "
      "on detection data, an input derived from the image rather than the image itself, or training "
      "data spanning many generators. And cross-generator evaluation and explanation analysis are "
      "almost never carried out together, which is precisely the gap this project addresses. What "
      "remains for Semester VII is restyling the report into the official Amity template, the "
      "plagiarism-check result and any corrections arising from it, the team's own rewrite pass over "
      "the drafted prose, and the guide review in the final week."),
]

# ---------------------------------------------------------------- PERT chart
# (task, weeks 1..12 to tick). W1 = 20-26 Jul 2026 ... W12 = 5-9 Oct 2026.
PERT = [
 ("Scope, title finalisation, search protocol and section skeleton", [1]),
 ("Literature collection and title/abstract screening", [2]),
 ("Full-text reading of 48 primary studies; extraction table", [3]),
 ("Taxonomy finalisation and Section 1 (Introduction)", [4]),
 ("Section 2 (Background: GANs, diffusion models, artefacts)", [5]),
 ("Section 3 (Taxonomy of detection approaches, 3.1-3.5)", [6, 7]),
 ("Section 4 (Datasets) and Section 5 (Metrics) with tables and figures", [8]),
 ("Master comparison table (48 studies) and Section 6", [9]),
 ("Section 7 (Gap analysis), Section 8 (Conclusion) and Abstract", [10]),
 ("Report assembly, reference verification, plagiarism/AI-text check", [11]),
 ("Guide review, corrections, final formatting and submission", [12]),
 ("Implementation environment, CIFAKE pipeline and split file", [4, 5]),
 ("Transfer-learning experiment matrix (5 backbones x 2 modes)", [5, 6]),
 ("Grad-CAM analysis and cross-generator evaluation", [6, 7, 8]),
]

# ---------------------------------------------------------------- NTCC diary
DIARY = [
("20/07/2026 - 22/07/2026",
 "Project scope fixed as detection of AI-generated still images, that is, binary classification of "
 "an image as camera-captured or synthesised by a generative model. Video deepfake detection, audio "
 "detection and any deployed product were recorded as out of scope. Working repository set up for "
 "the semester with separate folders for section drafts, tables, figures, references and progress "
 "reports. Candidate titles drafted for the guide's approval."),
("23/07/2026 - 26/07/2026",
 "Literature search protocol written and recorded so that it can be reported in the paper itself: "
 "six databases (IEEE Xplore, ScienceDirect, SpringerLink, the ACM Digital Library, arXiv and Google "
 "Scholar), eight query seeds covering GAN, diffusion and dataset-specific terms, inclusion limited "
 "to still-image work from 2019 to 2026 reporting quantitative results, and exclusion of video-only, "
 "audio-only, non-English and inaccessible work. Section skeleton for the review paper fixed at "
 "eight sections with a word budget for each."),
("27/07/2026 - 29/07/2026",
 "Project title finalised as “Deep Learning for AI-Generated Image Detection: A Review of CNN, "
 "Vision Transformer, and Explainable Approaches” and adopted as the official minor project topic. "
 "Official Weekly Progress Report proforma received from the department and replicated as a one-page "
 "template for the semester's reports. Database searches run against the eight query seeds."),
("30/07/2026 - 02/08/2026",
 "Search results consolidated: 101 records identified, 26 duplicates removed, leaving 75 unique "
 "candidate papers recorded with venue and DOI or arXiv identifier. Title-and-abstract screening "
 "completed against the inclusion and exclusion criteria, shortlisting 48 primary studies for "
 "full-text reading, 11 secondary studies for selective use and 15 background references on "
 "generators, backbones and explanation methods. Stage counts recorded for the search-flow figure."),
("03/08/2026 - 05/08/2026",
 "Full-text reading of the first half of the 48 primary studies. For each study read, the "
 "eight-column extraction table was populated: detection approach, model or architecture, dataset "
 "used, generators covered, reported accuracy or AUC, whether a cross-generator test is reported, "
 "and the limitation stated by the authors themselves. Cells that could not be confirmed from a "
 "paper's text were marked for verification rather than filled with an estimate."),
("06/08/2026 - 09/08/2026",
 "Full-text reading of the remaining primary studies completed and the extraction table populated "
 "for all 48. Citation identifiers checked during reading: three DOIs confirmed, one missing DOI "
 "located, one preprint replaced by its published journal version, and one preprint excluded for "
 "failing the well-cited criterion of the search protocol."),
("10/08/2026 - 12/08/2026",
 "Taxonomy of detection approaches finalised and all 48 studies assigned to its five families: 14 "
 "handcrafted and frequency-domain, 19 CNN-based and transfer learning, 2 transformer and "
 "attention-based, 8 multimodal and foundation-model-based, and 4 explainability. Section 1 "
 "(Introduction) and Section 2 (Background) drafted. Reference infrastructure completed: a BibTeX "
 "file built for all 74 included references, every identifier opened and checked against its arXiv, "
 "Crossref or proceedings record, and one publication-year error corrected."),
("13/08/2026 - 14/08/2026",
 "Sections 3 to 8 drafted: the five taxonomy subsections, the datasets section with an 11-dataset "
 "comparison table, the metrics section with eight numbered equations, the comparative analysis "
 "built on the master table of all 48 studies, the gap analysis, the conclusion and the abstract. "
 "The master table was checked against the extraction records by script and all 48 rows matched. "
 "Two figures produced: the search-flow diagram and the metrics overview panel."),
("15/08/2026 - 17/08/2026",
 "Full draft assembled into a formatted report document with both comparison tables inserted where "
 "the text first refers to them and both figures embedded, then exported to a text-searchable PDF "
 "and submitted for the departmental plagiarism check. On the same day the project guide instructed "
 "the team to begin preparing the implementation code ahead of Semester VIII, so a second work track "
 "was opened alongside the paper."),
("18/08/2026 - 19/08/2026",
 "Implementation plan written, covering hardware, dataset handling, the experiment matrix, the "
 "training defaults with a one-line justification for each, and the schema of the results CSV. Local "
 "Python environment built and version-pinned. CIFAKE downloaded and its train, validation and test "
 "split generated with seed 42 and committed to the repository: 90,000 training, 10,000 validation "
 "and 20,000 test images, balanced between the real and generated classes."),
("20/08/2026 - 21/08/2026",
 "Six pipeline modules implemented — data loading, model construction, training, evaluation, "
 "Grad-CAM and results merging — together with the ten experiment configuration files of the "
 "matrix. An end-to-end smoke run was completed on the laptop CPU, producing a results row, a "
 "checkpoint that reloads and a Grad-CAM overlay. A code review was carried out and its findings "
 "fixed before any GPU time was spent."),
("22/08/2026 - 23/08/2026",
 "Pipeline verified on the Kaggle GPU: the smoke run reproduced the CPU result exactly, which is "
 "evidence that the protocol is reproducible across machines, and per-architecture timings were "
 "measured so that training sessions could be sized against the weekly GPU allowance. First three "
 "training sessions run, completing ResNet50, DenseNet121 and EfficientNet-B0 in both modes and the "
 "Vision Transformer in feature-extraction mode."),
("24/08/2026 - 25/08/2026",
 "VGG19 completed in both modes. Its two results were recorded as the clearest single finding so "
 "far: last of the five backbones under feature extraction at 90.55% test accuracy and second under "
 "fine-tuning at 97.91%, the largest gap between the two modes in the matrix. The publication plan "
 "was revised with the guide's approval to a single merged research paper covering both semesters' "
 "work, with the two Amity project reports left unchanged."),
("26/08/2026 - 27/08/2026",
 "Vision Transformer fine-tuning completed, closing the experiment matrix at ten runs out of ten, "
 "all on the same GPU type with the same seed and split file, for 19.89 hours of measured GPU time. "
 "Results merged into the results CSV and the three runs that stopped at the epoch ceiling flagged "
 "as lower bounds, with reruns prepared. Progress report and project diary prepared for the First "
 "Progress Review Presentation on 27 August 2026."),
]
