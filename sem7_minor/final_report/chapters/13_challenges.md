# 13. CHALLENGES AND GAP ANALYSIS

Chapters 9 to 12 covered the detectors that have been built and how their performance is measured. This chapter turns to the problems those chapters leave unsolved. It groups them into five named sub-problems and ends with the research gap behind the planned second phase of the project.

## 13.1 Cross-Generator Generalisation

Chapter 7 argued that weak transfer to new generators is a structural problem and not simply an engineering nuisance. The evidence that a detector learns may be a side effect of something specific to one generator: its upsampling operator, its training run or its decoder. If so, a new generator that alters any of these does more than supply harder examples: it takes away the detector's evidence.

In the GAN era, transfer looked dependable at first: a ResNet-50 trained with ProGAN as its only generator averaged 90.8 mAP across eleven test generators, ten of which it had never seen [C01]. Diffusion models brought this period to an end. Detectors trained on GAN output lose an average of 15.2% AUROC when they are tested on diffusion images [C23], and in another study four GAN-trained detectors averaged only about 52–76% accuracy over twelve generators that included five diffusion models [C24]. The same weakness then appeared within the diffusion family: in the GenImage benchmark, a ResNet-50 tested on its training generator is 99.9% accurate, while the same model tested on Midjourney is just 54.9% accurate [C52]. Lastly, the gap does not only divide generator families; it also separates benchmark data from what a detector would face in practice. On realistic in-the-wild images, a detector with a mean accuracy of 92.77% on a standard benchmark falls to 65.77% [C36]. Section 12.3 found three features shared by the strongest cross-generator rows: frozen general-purpose representations, derived inputs and diversity in the training data. None of them closes the gap.

## 13.2 Robustness to Compression and Post-Processing

Robustness is a weak point that authors often acknowledge in Table 12.1: in ten of the 48 studies, the authors' own stated limitation concerns degraded or low-resolution input (Section 12.1). The reason again lies in the nature of the evidence. Generator traces are concentrated at high frequencies, the very part of the signal that lossy compression removes (Section 7.3). At 85% JPEG compression, the spectrum of a generated image becomes essentially impossible to tell apart from that of a real one [C18]; routine post-processing is also able to alter or conceal the artefacts [C30].

The effect has also been measured directly. Four GAN-trained detectors averaged roughly 52–76% accuracy over twelve generators on uncompressed images, and only about 50–61% once the same images had been resized and compressed [C24]. A zero-shot detector (Section 9.2) averages about 90.0% AUC, yet its own authors call it unreliable when inputs have been heavily compressed or resized [C34]. The accuracy of a CLIP-feature detector also falls once blurring, cropping, compression and added noise are applied together [C39]. Compression is not a form of attack; it is applied by default on every platform that a suspect image would pass through.

## 13.3 Dataset Bias and Staleness

A detector can score well on a dataset without detecting anything at all. {C31} found two systematic differences between the real and the generated images of GenImage, one in JPEG compression and one in image size. A classifier can therefore score well by picking up these two properties instead of any forensic trace. Once both biases are removed, cross-generator accuracy improves by over eleven points, both for a ResNet50 and for a Swin-T [C31].

Datasets built from one generator raise a narrower form of the same problem. CIFAKE, for instance, covers a single generator at 32×32 resolution. The Grad-CAM analysis that accompanies the dataset finds that the trained network bases its decisions on small imperfections in the image backgrounds, which are a property of that generator and not a general sign of synthesis [C51]. With only one generator, a dataset of this kind cannot reveal a cross-generator drop in the first place. Staleness has the same root. Each dataset freezes its list of generators when it is published. Apart from a few in-the-wild collections (Section 10.1), the field has answered by making the lists longer rather than by moving away from the fixed-list format. The gap between benchmark and in-the-wild performance that {C36} report is what this choice eventually costs.

## 13.4 Interpretability

Of the 48 rows in Table 12.1, only four include any form of explanation (Section 12.5), and these four mostly offer post-hoc saliency maps. Such a map, computed for an already trained network, shows where the network looked but not what it found there. The difference matters more in detection than in object recognition, since the traces a detector relies on are often invisible to the eye.

Applied to the CIFAKE network, Grad-CAM exposes a shortcut, the reliance on background imperfections noted in Section 13.3, but it does not identify which property of the highlighted pixels is synthetic [C51]. A prototype-based classifier is interpretable by design, yet its cross-dataset test used the same generator on both the training and the test side [C64]. The only row that compares explanation methods quantitatively is confined to one detector and one dataset [C63]. Frozen-feature detectors are furthest from an explanation: their own authors note that it is still an open question why a CLIP representation tells real images apart from generated ones [C37, C38]. Revealing a shortcut has value, yet it does not amount to stating what a detector measures.

## 13.5 Reproducibility and Comparability

One further, smaller problem makes the others worse. Chapter 11 noted that studies report different combinations of metrics on different test suites, which means two headline figures seldom measure the same quantity. Around 23 of the 48 studies give an accuracy figure and no other metric (Section 12.1). Cross-study comparisons are therefore weaker evidence than they first appear. This is a reason to compare candidate architectures under one common protocol rather than to piece together figures from separate papers.

## 13.6 The Research Gap

Section 12.6 identified the combination that is missing. No row of Table 12.1 brings together all four of the following elements:

1. Several ImageNet-pretrained CNN backbones, all trained with one protocol.
2. A Vision Transformer benchmark trained with that same protocol.
3. An analysis that shows which image regions the trained models pay attention to.
4. A cross-generator test, on generators the models did not see in training.

Each element can be found in at least one row. The GenImage benchmark places a ResNet-50 beside transformer backbones [C52]; {C44} change only the architecture and hold the training data constant; and the CIFAKE study includes a Grad-CAM analysis [C51]. No row, however, holds all four. The study planned to address this gap is set out in Section 14.3.
