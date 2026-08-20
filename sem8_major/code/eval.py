"""Evaluation and metrics. Stub — Phase 1 implements it.

CLI (re-evaluating a checkpoint that train.py already produced):
    python code/eval.py --run-id <run_id> [--dataset cifake|genimage]
        [--generator midjourney|adm|biggan|vqdm] [--condition down32|direct224]

Contract:

    evaluate(model, loader, out_dir) -> dict
        Every metric comes from scikit-learn — no hand-rolled formulas. Exactly the suite
        defined in Paper 1 Section 5: accuracy, precision, recall, F1, ROC-AUC, average
        precision, plus the confusion matrix and ROC curve. Fake (label 1) is the positive
        class. Returns the scalars that become the test_* columns of the runs.csv row.

Writes into out_dir (results/<run_id>/ for CIFAKE, results/<run_id>/genimage_<generator>_<condition>/
for cross-generator evaluations):
    confusion_matrix.csv   2x2, rows true / columns predicted, label order [real, fake]
    roc_points.csv         fpr,tpr,threshold

Cross-generator evaluations reuse an existing checkpoint rather than training, so they append
to results/crossgen.csv instead of runs.csv, one row per (checkpoint, generator, condition):
    run_id, generator, condition, n_real, n_fake, acc, precision, recall, f1, auc, ap
"""


def evaluate(model, loader, out_dir):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


def main():
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


if __name__ == "__main__":
    main()
