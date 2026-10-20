# 11. EVALUATION METRICS

## 11.1 Metrics Used in Detection

At test time, every detector reviewed here acts as a binary classifier labelling each image real or generated. By convention in this literature, the AI-generated image is the positive class, so every prediction falls in one of four cells. A generated image labelled generated is a true positive (TP), while one passed as real is a false negative (FN). A real image labelled real is a true negative (TN), while one flagged as generated is a false positive (FP). Each metric below condenses these four counts differently; Figure 11.1 shows them as a confusion matrix with the derived metrics.

[[FIGURE:metrics|11.1|Confusion matrix for real-or-generated classification (generated images as the positive class) and the measures computed from it. AUC and AP are threshold-free, summarising behaviour over all decision thresholds rather than one operating point.]]

Accuracy is the fraction of all predictions that are correct:

[[EQ:11.1]]

No measure is reported more often in this field. Its popularity can be defended only because benchmark datasets are usually balanced by design; CIFAKE, for example, holds 60,000 of each class [C51]. On an imbalanced test set the same value would mostly reflect the class prior, the proportion of each class.

Precision and recall separate the two kinds of error. Precision is the share of images flagged as generated that really are generated, so false positives lower it. Recall, or the true positive rate (TPR), is the share of generated images that are caught, so false negatives lower it:

[[EQ:11.2]]

[[EQ:11.3]]

The two pull in opposite directions; the F1 score merges them into their harmonic mean, an average that is high only when both are high:

[[EQ:11.4]]

These four metrics all depend on the decision threshold, the score above which an image is called generated. The remaining measures avoid fixing one threshold by sweeping it through its entire range. The first of them also uses the false positive rate (FPR), the share of real images flagged as generated:

[[EQ:11.5]]

Plotting TPR against FPR across the sweep gives the receiver operating characteristic (ROC) curve, and the area under that curve is the AUC:

[[EQ:11.6]]

An AUC of 0.5 matches random guessing, and 1.0 means perfect separation. Average precision (AP) extends the same reasoning to the precision–recall curve, weighting the precision reached at each recall level by the gain in recall since the level before, then summing:

[[EQ:11.7]]

When results come from N separate test sets, usually one per generator, their AP values are averaged into the mean average precision (mAP):

[[EQ:11.8]]

## 11.2 How the Surveyed Studies Report Results

Several specialised reporting conventions recur. The most frequent, mAP over per-generator test sets, dates from the ForenSynths protocol, under which {C01} report 90.8 mAP averaged across eleven test generators, ten of them unseen in training. Another convention pairs accuracy with AUC, setting a threshold-dependent figure beside a threshold-free one; {C11}, for example, report 95.6% accuracy with 0.997 AUC on seven GAN architectures unseen in training. Patch-level and single-transfer results often appear as AP alone, for instance 99.99 AP for a ProGAN-trained detector tested on StyleGAN [C02]. The option closest to operational practice fixes the false alarm rate and reports the probability of detection (Pd) at that rate. At a 1% false alarm rate (Pd@1%FAR), {C23} report that a diffusion-trained detector averages 94.26% detection on GAN images, while the reverse direction yields 26.34%.

The trouble lies in that variety. Studies differ in both their metrics and their test sets: mAP on eleven per-generator test sets [C01], accuracy with AP on eight diffusion models [C25], an averaged AUC-ROC on unseen text-to-image models [C33], AUC on nineteen generators [C34], and mAP plus accuracy on an evaluation set of twenty-one models [C35]. Because the test sets differ, two headline figures rarely describe the same quantity, and no reader can convert one metric into another afterwards.

Thresholds complicate matters further. Precision, recall, F1 and accuracy all rest on one operating point, usually the default, which is almost never recalibrated between datasets; any accuracy figure therefore hides a threshold choice. AUC and AP escape that choice, yet are silent on performance at the threshold a deployed system would really use. The exception is Pd@1%FAR [C23], which shows what the other conventions are missing.

The reported averages conceal as much as they reveal: a high mean can sit beside a complete failure on a generator that was never averaged in. A spectrum classifier from {C06} reaches 97.2% average accuracy in leave-one-out testing, but it fails on GauGAN. On GenImage, a ResNet-50 scoring 99.9% on its own training generator manages only 54.9% on images from Midjourney [C52]. In forensic use the generator that matters is the worst case, not the average. The master comparison table in Chapter 12 therefore pairs every figure with its metric, its test suite and its cross-generator status.
