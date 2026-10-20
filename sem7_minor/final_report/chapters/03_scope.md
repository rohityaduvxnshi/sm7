# 3. SCOPE

## 3.1 Scope Definition

The project covers a single problem: deciding whether a still image was produced by a generative model. Detection is treated as binary classification, in which the detector looks at one image and assigns it to one of two classes, real (captured by a camera) or AI-generated. No particular generator is singled out. The review takes in whichever generators the surveyed studies train and test on, which means generative adversarial networks (GANs), diffusion models and any further generators that appear in those studies' experiments; GANs and diffusion models are described in Chapter 7. On the detection side, the approaches in scope run from handcrafted and frequency-domain forensics, through CNN transfer learning and Vision Transformers, to detectors built on CLIP features and explanation methods such as Grad-CAM. The scope also takes in the datasets and benchmarks on which these detectors are evaluated and the metrics in which their results are reported.

A detection or benchmark study entered the review only if it met the inclusion criteria of the protocol. It had to deal with still images, to have been published between 2019 and 2026, to report quantitative results such as accuracy, AUC or F1, and to be either peer-reviewed or a well-cited preprint. The publication window binds these studies alone. Background references on generators, backbone networks and explanation methods are not held to it, which is why some of them date from 2014 to 2018.

Within these limits, the work of the project consisted of the following activities:

1. Defining the search protocol and its criteria.
2. Running the eight query seeds through the search sources named in the protocol.
3. Screening the records by title and abstract.
4. Extracting data from the full texts of the primary studies.
5. Building the taxonomy of detection approaches.
6. Comparing the datasets and benchmarks.
7. Reviewing the evaluation metrics and how studies report them.
8. Comparing the reported results across the primary studies.
9. Analysing the challenges and identifying the research gap.
10. Verifying the identifier of every included reference.
11. Writing the review and this report.

## 3.2 Limitations of Scope

Some boundaries were drawn on purpose. Deepfake detection in video and in audio is left out, and studies that deal only with those media were filtered out when the search was run. The project neither builds nor deploys a detection system, so it produces no app and no real-time tool. The review itself also contains no experiment. Every accuracy, AUC or other performance figure quoted in this report is the value published by the original authors, and none of these values has been reproduced by the team. Experiments on the problem are reserved for the Semester 8 major project.

Other boundaries come from the protocol and from the timing of the search. Papers not written in English, papers whose full text could not be accessed and studies without a quantitative evaluation were all excluded. The well-cited rule for preprints also led to the exclusion of one candidate, a preprint with only a single citation. Because the search was run in Week 2 (27 July to 2 August 2026), research that appeared after that week is not part of the surveyed set.

Finally, the included studies did not all receive the same depth of treatment. The 48 primary studies were each read in full and extracted field by field. The 11 secondary studies were drawn on selectively and did not go through full-text extraction, so none of them has a row in the master comparison table of Chapter 12. Section 14.2 discusses the limitations of the review as a whole.

## 3.3 Projected Budget

Because the project reads and analyses published work instead of building a system, nothing had to be bought to carry it out: no hardware, no software licence, no dataset and no database subscription. The resources it did rely on are described here along with the extra money each one required.

Papers were read in freely accessible versions wherever such versions existed, for example arXiv preprints and open-access proceedings, and the team paid for no subscription. The software was either free or already installed on the machine in use (Section 5.3). The review work needed no GPU, so the team's existing laptop was enough (Section 5.4). Internet access and electricity came from the members' existing personal resources. The one expense still ahead is printing and binding: the Amity guidelines ask for two spiral-bound copies of the report with a blue back cover, and that cost falls at submission. Since the amount is not yet known, Table 3.1 leaves it open instead of guessing a figure.

Table: 3.1 | Estimated additional cost of the project
| Resource | Use in the project | Additional cost (Rs.) |
|---|---|---|
| Literature | Free versions of papers where available; no paid subscription | 0 |
| Software | Free tools or software already installed | 0 |
| Hardware | Existing laptop; no GPU needed | 0 |
| Internet and electricity | Existing personal resources | 0 |
| Printing and binding | Two spiral-bound copies with blue back cover, paid at submission | Not yet known |
| Total additional development cost | Excluding printing and binding | 0 |
