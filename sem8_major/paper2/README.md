# paper2/ — Paper 2 draft (plan §10 phase P1)

The experimental paper: the core of the Semester 8 major project report and the experimental half
of the merged publication. Drafted after gate G6 (every table and figure regenerates from a clean
checkout). Karki et al. (2024) is the structural template (CLAUDE.md §4).

```
sections/00_front.md … 07_backmatter.md   the prose; tables, figures and references appear only as
                                           {{table:<name>|caption}}, {{figure:<name>|caption}}, {{refs}}
build_paper.py                             assembles paper2_draft_v1.md: inserts results/tables/<name>.md
                                           verbatim (caption above, the table's own notes below), links
                                           figures/<name>.png, renders the cited [Cxx] keys from
                                           sem7_minor/references/references.bib; fails on a missing
                                           figure or key, a table/figure not mentioned in the body before
                                           it appears, a numbering gap, or first mentions out of order
check_numbers.py                           checks that every number in the assembled prose coincides with
                                           a value in the generated tables or committed results CSVs (or a
                                           rounding of one), a quantity derived in the script, or an
                                           allow-listed external fact; exit 1 otherwise. It catches a
                                           retyped or stale table value, not a wrong small integer or a
                                           wrong one-/two-decimal fraction, which usually coincide with
                                           some logged value — those remain a reading check
paper2_draft_v1.md                         the assembled draft (generated; committed so it reads
                                           without running anything)
```

Build and audit, from `sem8_major/` with the venv python (two commands; PowerShell 5.1 has no `&&`):

    python paper2/build_paper.py
    python paper2/check_numbers.py

Both scripts have a `--selfcheck`.

## Rules this directory follows

- Nothing numeric is typed from memory. A table is never retyped; a number in the prose must
  pass `check_numbers.py`. If a sentence needs a number the checker cannot trace, derive it in the
  checker (with the formula) or add it to the allow-list with its source — never silence the checker.
- `results/tables/` is authoritative over every number in CLAUDE.md, the plan and the handoff.
- `[VERIFY]` and `[UNKNOWN]` markers stay in the text until resolved; they are listed below.
- The draft is input for Rohit's own rewrite (CLAUDE.md §10). It is not submission-ready prose,
  and no plagiarism/AI-text tool is ever used to reword it. Sections 1 and 2 were reworded away from
  the companion review's sentences on 17 Oct 2026 after the review workflow flagged near-verbatim
  overlap; P5's rewrite is still mandatory and P6's self-similarity disclosure covers any remainder.
- Table 9 (ablations) is a PENDING block until the A5 rows land; rebuilding then fills it in.

## Open items specific to this draft

| # | Item | Where |
|---|---|---|
| 1 | Pretrained weight tags were not logged per run. Resolved with timm 1.0.28 locally (`resnet50.a1_in1k`, `densenet121.ra_in1k`, `efficientnet_b0.ra_in1k`, `vgg19.tv_in1k`, `vit_base_patch16_224.augreg2_in21k_ft_in1k`); confirm the 1.0.26 defaults on Kaggle match | §3.3, §5.2 |
| 2 | Library versions of the 15 Oct 2026 evaluation session (timm, pytorch-grad-cam, and Kaggle's torch/torchvision/scikit-learn on that date) are unrecorded: installed unpinned, no version fields in crossgen.csv; its GPU name rests on the session log, which is not in the repository | §3.9 |
| 3 | CIFAKE licence terms before any gallery image is reproduced (CLAUDE.md item 21) | §5.7, Declarations |
| 4 | Author contributions need the role split (CLAUDE.md item 4) | Back matter |
| 5 | AI-assistance disclosure wording, if required (CLAUDE.md item 18) | Declarations |
| 6 | Repository release decision (private now) | Data availability |
| 7 | How the companion review is cited once the merged-paper shape is chosen (P2, item 19) | §1, §2 |
| 8 | ViT Grad-CAM: the seven empty panels are all panels whose predicted class was generated (one generated-target panel did produce a map). Caption disclosure only, or an attention-rollout rerun (CLAUDE.md item 23)? The pattern is recorded, not diagnosed | §4.4, §5.6 |
| 9 | Ablations pending (A5) — Table 9 and the sentences that point to it | §4.5, §5.5, §5.7 |
| 10 | Software citations (PyTorch, timm, scikit-learn, pytorch-grad-cam) are named with versions/URL but not in the C-keyed bib; add at P4 when the reference list is unified and re-verified | §3.6, §3.8, §3.9 |
| 11 | Front matter: author order and the guide's designation (CLAUDE.md items 4 and 11) | Front matter |
| 12 | The structural template (Karki et al. 2024, doi:10.1016/j.scienta.2024.113241) is not cited anywhere; decide at P4, with item 10, whether to credit it for the fe/ft design and the SGD setup. Not added to references.bib or verification_log.md before P4 | §1, §3.4, Table 2 |
| 13 | CIFAR-10 (Krizhevsky 2009) is credited in words in the Figure 6 caption and §3.1 but has no reference entry; add and verify at P4 | Figure 6, §3.1 |
| 14 | The tiny-genimage Kaggle dataset is named by slug and URL only; a dataset reference (title, URL, licence, access date) is to be added and verified at P4 | §3.1, Data availability |
