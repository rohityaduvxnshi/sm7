# results/ — every number Paper 2 reports

**Rule: never hand-transcribe a result.** Metrics are written here by `train.py` and `eval.py`
as they are produced, and Paper 2's tables and figures are generated from these files. A number
that exists only in a notebook cell, a screenshot or a chat message does not exist.

## Layout

```
results/
├── runs.csv                  one row per completed FULL training run (schema below)
├── smoke_runs.csv            smoke-run rows only (subset runs from *_smoke.yaml configs) —
│                             quarantined so no subset number can reach a Paper 2 table;
│                             train.py refuses to write a smoke row into runs.csv
├── crossgen.csv              one row per cross-generator evaluation of an existing checkpoint:
│                             run_id, generator, condition, n_real, n_fake,
│                             acc, precision, recall, f1, auc, ap
│                             (merge key: run_id + generator + condition)
├── canonical_runs.txt        committed manifest of the exact run_ids Paper 2 tables use;
│                             make_tables.py fails loudly on a missing or ambiguous entry
└── <run_id>/                 run_id = <model>_<mode>_<YYYYMMDD-HHMM>
    ├── config_used.yaml      resolved copy of the config the run actually used
    ├── learning_curve.csv    epoch,train_loss,train_acc,val_loss,val_acc
    ├── confusion_matrix.csv  2x2, rows true / columns predicted, label order [real, fake]
    ├── roc_points.csv        fpr,tpr,threshold
    └── best.pt               best-by-validation-loss checkpoint (gitignored, not committed)
```

Paper 2 table/figure scripts read **only** `runs.csv`, `crossgen.csv` and the per-run
artefact CSVs, filtered through `canonical_runs.txt`. `smoke_runs.csv` is never read by them.

Cross-generator evaluations write their `confusion_matrix.csv` and `roc_points.csv` into
`<run_id>/genimage_<generator>_<condition>/`.

## runs.csv schema

| Column | Meaning |
|---|---|
| `run_id` | `<model>_<mode>_<YYYYMMDD-HHMM>`; matches the artefact directory name |
| `date` | run date, YYYY-MM-DD |
| `config_path` | config the run was launched with |
| `model` | timm model name |
| `mode` | `fe` (feature extraction) or `ft` (fine-tuning) |
| `seed` | 42 for every planned run |
| `split_file` | path to the committed split file (`data/cifake_split_seed42.csv`) |
| `n_train_images` | realised training-image count (90,000 for a full run; smaller values only ever appear in `smoke_runs.csv` rows) |
| `resolution` | input size in pixels (224 baseline) |
| `batch_size` | mini-batch size |
| `optimizer` | `sgd` or `adamw` |
| `lr` | initial learning rate |
| `weight_decay` | weight decay |
| `max_epochs` | epoch ceiling from the config |
| `best_epoch` | epoch the kept checkpoint came from |
| `early_stopped` | true if patience triggered before `max_epochs` |
| `train_time_min` | wall-clock training time in minutes |
| `total_params` | total parameter count of the model |
| `trainable_params` | trainable parameter count (differs by mode; Paper 2 reports it) |
| `hardware` | GPU model + VRAM, e.g. `Tesla T4, 16 GB`, or `local i5-1135G7 CPU` for smoke runs — Paper 2 must report it |
| `torch_version` | resolved torch version for this run |
| `timm_version` | resolved timm version for this run |
| `val_acc` | accuracy on the 10k validation split at the best epoch |
| `val_loss` | validation loss at the best epoch (the early-stopping criterion) |
| `test_acc` | accuracy on the untouched 20k CIFAKE test set |
| `test_precision` | precision, fake = positive class |
| `test_recall` | recall, fake = positive class |
| `test_f1` | F1, fake = positive class |
| `test_auc` | ROC-AUC |
| `test_ap` | average precision |

All `test_*` values come from scikit-learn on the official CIFAKE test split, which is never
used for training, validation or model selection.
