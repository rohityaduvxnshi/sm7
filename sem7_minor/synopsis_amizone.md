# Amizone Synopsis Entry (submitted 29 July 2026)

Project duration fixed by portal: 82 days, 20/07/2026 – 09/10/2026. Offer letter uploaded: OfferLetter_MinorProject_<name>.pdf.

## Topic

Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches

## Project Objective

1. To review published deep learning approaches for detecting AI-generated images, covering frequency/forensic methods, CNN-based transfer learning, Vision Transformer and attention-based methods, foundation-model (CLIP-feature) detectors, and explainability techniques such as Grad-CAM.
2. To compare the benchmark datasets used in this field (CIFAKE, GenImage, ArtiFact and others) and the evaluation metrics reported in the literature.
3. To build a comparative table of published results, with specific attention to whether each method was tested across different image generators (cross-generator generalisation).
4. To identify the open research gaps and use them to define the experimental study planned as the major project in Semester 8.

## Methodology to be adopted

A systematic literature review will be carried out. Papers from 2019–2026 will be collected from IEEE Xplore, ScienceDirect, SpringerLink, ACM Digital Library, arXiv, and Google Scholar using defined search terms, and screened using fixed inclusion/exclusion criteria (image domain only, quantitative results reported). Counts at each screening stage will be recorded in a PRISMA-style flow. Each included paper will be read in full and logged in a structured extraction table (approach, architecture, dataset, generators covered, reported accuracy/AUC, cross-generator testing, key limitation). The approaches will then be organised into a taxonomy, compared, and analysed to produce a dataset comparison, a master literature table, and a gap analysis. Every citation will be verified against its DOI or arXiv ID.

## Brief Summary of the project

Modern generative models such as GANs and diffusion models can produce images that are visually indistinguishable from real photographs, which raises practical problems like misinformation, fabricated evidence, and identity fraud. This project is a review-based study of how deep learning is used to detect AI-generated images. It covers how generators leave detectable artefacts, the main families of detection methods (handcrafted/frequency-domain, CNN transfer learning, Vision Transformers, multimodal CLIP-based, and explainable approaches), the datasets and metrics used to evaluate them, and a comparative analysis of reported results. Particular focus is placed on the cross-generator generalisation problem, where detectors trained on one generator family fail on unseen generators. The outcome is a research-paper-style report that consolidates the current state of the field, identifies its open challenges, and defines the experimental comparison of CNN and Vision Transformer models planned as the Semester 8 major project.
