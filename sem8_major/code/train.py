"""Training entry point. Stub — Phase 1 implements it.

CLI:
    python code/train.py --config configs/resnet50_fe.yaml

Every hyperparameter is read from the YAML (fields documented in configs/template.yaml);
nothing is hardcoded here — including output paths, which come from cfg["output"]
(results_dir, runs_csv), so Kaggle runs can redirect to /kaggle/working without code edits.
cfg["seed"] (42) seeds python, numpy and torch before anything else runs.

Flow: build_model -> get_loaders -> SGD or AdamW per cfg["optimizer"] -> up to
cfg["max_epochs"] epochs, mixed precision when cfg["amp"], early stopping after
cfg["early_stopping_patience"] epochs without validation-loss improvement, keeping the
best-by-validation-loss checkpoint.

Writes, as the run proceeds (nothing is printed and later retyped), into
<results_dir>/<run_id>/:
    config_used.yaml     resolved copy of the config actually used
    learning_curve.csv   epoch,train_loss,train_acc,val_loss,val_acc
    best.pt              best checkpoint (gitignored)

On completion it evaluates the test split through eval.evaluate() and appends one row to
<runs_csv> using the schema in results/README.md, including split_file, train_time_min,
total_params, trainable_params, hardware (GPU model + VRAM), torch_version and timm_version.

run_id convention: <model>_<mode>_<YYYYMMDD-HHMM>.
"""


def main():
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


if __name__ == "__main__":
    main()
