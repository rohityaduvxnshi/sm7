# Section 5 — Evaluation Metrics and Reporting Practice

## 5.1 The metrics

At the point of evaluation every detector surveyed here is a binary classifier, and the convention in this literature is to treat the AI-generated image as the positive class. Each decision then falls into one of four counts: a true positive (TP) is a generated image called generated, a false positive (FP) a real image called generated, a true negative (TN) a real image called real, and a false negative (FN) a generated image called real. Every metric below is a different summary of those four numbers. Figure 5.1 summarises the confusion matrix and the quantities derived from it.

Accuracy is the proportion of correct decisions:

`Accuracy = (TP + TN) / (TP + FP + FN + TN)`  (1)

It is the most frequently reported figure in this field, which is defensible only because the datasets involved are usually balanced by construction — CIFAKE, for instance, pairs 60,000 real with 60,000 generated images [C51]. On a skewed test set the same number would mostly describe the class prior.

Precision and recall split the errors by type. Precision asks what fraction of the images flagged as generated really were; recall, also called the true positive rate, asks what fraction of the generated images were caught:

`Precision = TP / (TP + FP)`  (2)

`Recall = TPR = TP / (TP + FN)`  (3)

The two trade against each other, and the F1 score reports their harmonic mean, which is low unless both are high:

`F1 = 2 · (Precision · Recall) / (Precision + Recall)`  (4)

All four depend on where the decision threshold is placed. The remaining metrics remove that dependence by sweeping the threshold across its whole range. Writing the false positive rate as

`FPR = FP / (FP + TN)`  (5)

the receiver operating characteristic (ROC) curve plots TPR against FPR over that sweep, and the area under it is

`AUC = ∫ TPR(FPR) d(FPR), integrated from FPR = 0 to 1`  (6)

An AUC of 0.5 corresponds to chance and 1.0 to perfect separation. Average precision (AP) applies the same idea to the precision-recall curve, summing the precision at each recall level weighted by the increase in recall since the previous one:

`AP = Σ_k (Recall_k − Recall_{k−1}) · Precision_k`  (7)

and where a detector is evaluated on several test sets — normally one per generator — the mean over them is reported as mean average precision:

`mAP = (1/N) Σ_i AP_i`  (8)

**Figure 5.1: Confusion matrix for real-versus-generated classification and the metrics derived from it.** The positive class is the AI-generated image. AUC and AP summarise performance over a sweep of decision thresholds rather than at a single operating point. Source file: `figures/metrics_overview.svg`.

## 5.2 How the surveyed literature reports

Several specialised conventions recur. The most common is mAP computed over per-generator test sets, introduced with the ForenSynths protocol and reported there as 90.8 mAP averaged over eleven unseen generators [C01]. A second is the accuracy-and-AUC pair, quoting a threshold-dependent and a threshold-free figure together, as in the 95.6% accuracy and 0.997 AUC reported over seven unseen GAN architectures [C11]. Patch-level and single-transfer results are often given as AP alone, for example 99.99 AP training on ProGAN and testing on StyleGAN [C02]. The most operationally explicit convention is the probability of detection at a fixed false alarm rate: Ricker et al. report Pd@1%FAR, giving 94.26% average detection for a diffusion-trained detector on GAN images against 26.34% for the reverse direction [C23].

This variety is the problem. Different studies report different metric combinations over different test suites: mAP over eleven GAN sets [C01], accuracy and AP over eight diffusion models [C25], AUC-ROC averaged over unseen text-to-image models [C33], AUC over nineteen generators [C34], and mAP together with accuracy over a twenty-one-model evaluation set [C35]. Because the suites differ, two headline numbers are rarely measuring the same thing, and a reader cannot recover one metric from another after the fact.

Thresholds compound this. Accuracy, precision, recall and F1 all assume an operating point that is usually left at the default and almost never calibrated across datasets, so an accuracy figure carries an unstated choice with it; AUC and AP avoid the choice but say nothing about performance at the point a deployed system would actually use. Pd@1%FAR [C23] is the exception that shows what is missing elsewhere.

The averages hide as much as they show. A mean over generators can be carried by easy cases while concealing a total failure: the spectrum classifier of Zhang et al. averages 97.2% accuracy under leave-one-out testing yet fails on GauGAN [C06], and on GenImage a ResNet-50 at 99.9% on its training generator scores 54.9% on Midjourney [C52]. The worst-case generator, not the mean, is what a forensic user meets. For this reason the comparative table in Section 6 records the metric, the test suite and the cross-generator condition alongside every figure, rather than the figure alone.

Word count: 688 (target ~700; band 550-850). Counted over prose only; headings, display equations (1)-(8), the figure caption block and this footer are excluded.

C-IDs cited: C01, C02, C06, C11, C23, C25, C33, C34, C35, C51, C52
