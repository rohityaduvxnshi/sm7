# 12. COMPARATIVE ANALYSIS AND FINDINGS

Chapters 9 to 11 discussed detection approaches, datasets and metrics separately. This chapter compares the surveyed studies directly, using Table 12.1, which gives each of the 48 primary studies one row in order of publication. A row records the approach, model, data, generators covered and headline result, plus two further entries: whether the detector was tested on generators held out of training, and the limitation that its authors acknowledge. Those two final columns are this review's addition to the usual comparison. Every count below comes from tallying one column of Table 12.1 and can be verified there.

[[TABLE:t12_1]]

## 12.1 What the Comparison Table Shows

Table 12.2 gathers the main tallies, which the paragraphs that follow discuss in turn.

Table: 12.2 | Tallies drawn from Table 12.1
| Measure | Count |
|---|---|
| Studies reporting a cross-generator evaluation | 36 of 48 (12 do not) |
| Generator coverage: GAN-era generators only | 20 |
| Generator coverage: diffusion-family generators only | 8 |
| Generator coverage: both | 19 |
| Generator coverage: face-manipulation methods only | 1 |
| Studies trained on ProGAN-generated images (14 of them on the ForenSynths training set) | 15 |
| Studies quoting an accuracy figure | roughly 38 |
| Studies quoting average precision | 15 |
| Studies quoting AUC or AUROC | 9 |
| Studies reporting no detection metric | 1 |
| Studies giving an accuracy figure and nothing else | around 23 |
| Studies naming robustness to degraded or low-resolution input as a limitation | 10 |
| Studies including an explanation analysis | 4 |

Cross-generator testing has become common, though not universal: it appears in 36 of the 48 studies and is missing from 12. Among those twelve, three are early spectral studies evaluated dataset by dataset [C08, C17, C18], two attribute images among a closed set of known GANs [C04, C05], and three are limited to one generator or one detector [C27, C51, C63]. The other four are an analysis paper that proposes no detector [C30], a counter-study that trains a separate classifier for each GAN [C19], a DCT analysis in which no GAN is held out [C07], and a prototype-based method whose cross-dataset test uses Stable Diffusion images on both sides [C64].

To count coverage, each study was classified by the generator families on its list, with benchmark names expanded into the generator lists of Table 10.1. On this count, 20 studies use only GAN-era generators, 8 use only diffusion-family generators, 19 use both, and one study covers nothing but face-manipulation methods [C63]. Training data is concentrated: fifteen studies, close to a third of all those surveyed, train on ProGAN-generated images [C01, C02, C03, C11, C12, C15, C16, C21, C22, C37, C39, C40, C41, C43, C48]. Fourteen of them use the ProGAN training set released with ForenSynths; the exception, {C02}, trains on ProGAN-generated face images instead.

Metrics are concentrated similarly. Accuracy is quoted by roughly 38 studies, average precision by 15 and AUC or AUROC by 9; one study reports no detection metric of any kind [C30]. Around 23 quote accuracy alone, a figure that, as Chapter 11 noted, hides a choice of decision threshold. Ten studies' stated limitations concern robustness to degraded or low-resolution images, the degradation being compression, resizing, blurring or other post-processing [C14, C17, C18, C23, C24, C30, C34, C39, C43, C52].

## 12.2 The Chronological Arc

In order of publication, the table shows a clear progression. The first rows pair a single artefact with a simple classifier and report near-perfect numbers. Co-occurrence matrices give above 99% [C10] and DCT coefficients 100.00% on FFHQ [C07]; a spectral-decay feature reaches 99.2% for uncompressed images at 1024×1024 [C18]; and one study scores 100% on a face set its authors assembled, even when only 20 samples were labelled [C17]. Such figures hold only in narrow conditions, and qualifying rows follow quickly. At 256×256 the same feature manages only 88.8%, and under 85% JPEG compression it becomes unusable [C18]. Retraining the generators with bilinear upsampling cuts the detection rate of detectors relying on that feature from 84.8–99.8% to 0–0.3% [C19].

Transfer-learning CNNs enter in the same years with a wider claim. A ResNet-50 trained on ProGAN images alone averages 90.8 mAP over eleven test generators, ten of which it never saw [C01]. A contrastively trained detector averages an AUC of 0.997 and an accuracy of 95.6% on seven unseen GANs [C11], and an ensemble that kept StyleGAN3 out of training reaches 0.9995 AUC [C13]. Yet {C03}, evaluating seven state-of-the-art GAN-image detectors side by side, concluded that reliable tools were still far off.

Diffusion models then wiped out most of this lead, a collapse that two rows record. In the first, four GAN-trained detectors were run on twelve generators, five of them diffusion models (ADM, DALL·E 2, GLIDE, Latent Diffusion and Stable Diffusion); across all twelve they averaged roughly 52–76% accuracy without compression and about 50–61% once resizing and compression were added, and the diffusion models were among the hardest cases [C24]. The second reports an average drop of 15.2% in AUROC when such detectors meet diffusion output, and shows that the effect depends on direction: trained on diffusion images, a detector still reaches an average Pd@1%FAR of 94.26% on GAN images, whereas the reverse arrangement gives only 26.34% [C23]. The same failure appears even when both generators come from the diffusion family: in the GenImage benchmark, a ResNet-50 trained on Stable Diffusion v1.4 images scores 99.9% on test images from that generator but 54.9% on the Midjourney test set [C52].

Several 2023–2024 rows answer by deriving a signal from each image and handing that signal, with or without the image, to the detector. LGrad passes it gradients from a pretrained network and averages 86.3% accuracy across the eight models it was tested on [C15]; NPR uses relationships between neighbouring pixels and reaches 92.2% across 28 generators [C16]; DIRE reconstructs each image with DDIM and classifies the residual between the two, averaging 99.9% accuracy across eight diffusion models [C25]. AEROBLADE dispenses with the trained classifier, scoring each image by its distance from an autoencoder reconstruction for a mean AP of 0.992 [C28]. LaRE² computes the same kind of error in latent space [C29], while FakeInversion draws on the inversion of Stable Diffusion, recording an average AUC-ROC of 0.759 on text-to-image models absent from its training data [C33].

The latest rows converge on a further idea: keep a large general-purpose network frozen and train only a small component on top of it. {C37} established the idea by classifying frozen CLIP features with a linear probe or a nearest-neighbour rule. On diffusion and autoregressive models absent from training, this raised accuracy by 25.90% and mAP by 15.07 over the earlier best. Later rows use these features in other ways:

- a few-shot linear SVM, averaging about 90.0% AUC across 18 generators [C38];
- intermediate encoder-block outputs, giving 91.5% accuracy with 98.8 AP on 20 test sets [C39];
- a trainable adapter, which scores 98% on GANs held out of training and 95% on held-out diffusion models [C40];
- prompt tuning, with 98.06% mAP across 18 generators held out of training [C43];
- a prompt injected into the text encoder, reaching 93.79% accuracy across 19 test subsets [C41];
- an orthogonal subspace decomposition, with 95.19% mean accuracy and 99.41% mAP on the same 19 subsets [C48].

## 12.3 What the Strongest Cross-Generator Results Share

The rows with the best unseen-generator results tend to share three properties. First, the representation is not learned from detection data. The foundation-model rows freeze the backbone and train only a prompt, an adapter or a probe [C37, C38, C39, C40, C41, C43, C48], and ZED, trained on real images alone, still averages about 90.0% AUC over 19 generators [C34]. Second, the decision does not rest on the raw pixels alone but on something computed from the image, such as gradient maps [C15], relations between neighbouring pixels [C16] or signals derived from reconstructing it [C25, C28, C29, C33]. Third, the training side is diverse. A detector trained on Community Forensics, which holds 2.7M images produced by 4,803 generators, reaches 89.2% accuracy and 0.987 mAP on a set of 21 models it was not trained on [C35]; and training data matter in a second way, since once the JPEG-compression and image-size biases in GenImage are removed, the cross-generator accuracy of both a ResNet50 and a Swin-T rises by more than eleven points [C31]. In none of the three cases does a network have to learn, from scratch, an artefact that belongs to a single generator.

## 12.4 What the Headline Figures Hide

These headline figures must be read alongside the two columns to their right. Most record one move from training to test data, often starting from ProGAN-generated images, the training source of fifteen rows, so they measure a single transfer and not transfer in general. Averages also mask the worst case: a classifier built on the frequency spectrum, with a 97.2% average, breaks down completely on GauGAN [C06], and the authors of LaRE² concede that real and fake features still overlap for Midjourney, ADM and BigGAN images [C29]. Performance on benchmarks and in the wild can differ sharply. The detector proposed with the Chameleon benchmark averages 92.77% on AIGCDetectBenchmark and 86.88% on GenImage but only 65.77% on Chameleon's realistic images, where every detector its authors tested comes close to failing [C36]. The ten stated limitations about degraded input are supported by the compression and resizing results given in Section 12.2 [C24] and by a zero-shot detector that its authors describe as unreliable once images are heavily compressed or resized [C34]. Chapters 10 and 11 traced the dataset and metric causes; here the point is that, in Table 12.1, the rightmost columns qualify the headline one.

## 12.5 Where Explainability Appears

Explanations are analysed in just four of the 48 rows, usually after the detector has been built. {C51} applied Grad-CAM to a small CNN trained on CIFAKE and found its decisions driven by imperfections in the background. {C02} produced a map of the patches in which a fake can be detected, by limiting how much of the image each decision sees. {C64} instead built interpretability into the detector, using the support vectors of an SVM fitted on fine-tuned ViT features as prototypes. {C63} compared five explanation methods on a single detector and rated LIME best, because altering the segments it ranked highest lowered the detector’s accuracy the most (to 0.579 on NeuralTextures after one segment, and to 0.245 on DeepFakes after three). Of these four, only {C02} also tested their detector on unseen generators; the other three carry No in the cross-generator column of Table 12.1. On this evidence, explainability and generalisation are pursued as separate questions.

## 12.6 The Combination No Study Reports

Architectures are compared under a single protocol in a few rows. The GenImage benchmark tests ResNet-50, DeiT-S and Swin-T classifiers alongside four detectors built for the task [C52], and {C31} applied one bias-correction procedure to both a ResNet50 and a Swin-T. {C44} came nearest to isolating architecture alone: they trained an EfficientNetV2-M and a ViT-Base on identical ForgeryNet subsets and tested both on fifteen manipulation methods. In one of their experiments the CNN reached 81.1% on one of its three training methods but only 47.0% and 57.0% on the other two, while the ViT stayed near 62.0% on all three; overall, the authors found that the CNN specialises more and generalises worse to new methods. Still, none of them compares several of the ImageNet-pretrained CNN backbones discussed in Section 9.2, and none analyses explanations.

The opposite combination is absent as well. The only row built on CIFAKE relies on a custom CNN, the best of 36 topologies, instead of pretrained backbones; it covers a single generator and offers Grad-CAM explanations without any cross-generator result [C51]. The interpretable, prototype-based row also carries a No [C64], and the only study that scores explanation quality numerically looks at just one detector, on FaceForensics++ [C63]. As a result, no row of Table 12.1 combines all four of these elements:

- several CNN backbones pretrained on ImageNet, all trained under a common protocol;
- a Vision Transformer, trained the same way, as a benchmark;
- an explanation analysis showing which image regions the trained models focus on;
- an evaluation on generators withheld from training.

Each element is well established in at least one row. What no surveyed study reports is all four at once, on a dataset small enough for such a matched comparison to stay manageable. The gap is this combination rather than any one element, and Chapter 13 builds the gap analysis on it.
