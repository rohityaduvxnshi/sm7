# -*- coding: utf-8 -*-
"""Content for the Group 148 Project Progress Report, second progress review
(progress to the end of Week 10, 27 September 2026).

Everything not overridden here is Review 1's content, unchanged: the review paper has
not changed since Review 1, so Introduction and Sections 1-7 carry over verbatim.
Overridden: Section 8, the Conclusion and the PERT chart.

Every figure is copied from sem8_major/results/runs.csv and
sem8_major/results/canonical_runs.txt (accuracies converted to percent, rounded half-up
exactly as in Review 1), or from the learning_curve.csv of the run it describes.

Build: python build.py content_review2
"""
from content import *          # noqa: F401,F403  (identity block, Intro, Sections 1-7, refs)
import content as _c

REPORT_NAME = "G148_Sem7_ProjectProgressReport_2"
REPORT_TITLE = "Project Progress Report 2 - Group 148"

_i8 = next(i for i, (k, t) in enumerate(_c.SUMMARY) if k == "h" and t.startswith("8. "))
_PIPELINE = _c.SUMMARY[_i8 + 2]            # pipeline paragraph: still exactly true, reused
_CONCL_H = ("h", "Conclusion")

SUMMARY = _c.SUMMARY[:_i8] + [
("h", "8. Implementation Work Begun on the Project Guide's Instruction"),
("p", "Following the guide's instruction of 15 August 2026 to begin preparing the implementation "
      "code ahead of Semester VIII, the experimental pipeline was built, the core experiment matrix "
      "was completed and, since the first progress review on 27 August, its three lower-bound runs "
      "have been repeated at a higher epoch ceiling. None of what follows appears in the review "
      "paper, which reports no experimental results of its own; these numbers belong to the second "
      "phase of the project."),
_PIPELINE,
("p", "The full matrix of five backbones in two transfer-learning modes — ten runs — was completed "
      "by 26 August. The three runs that had stopped at the 30-epoch ceiling with validation loss "
      "still improving were then repeated with a 50-epoch ceiling and every other setting unchanged, "
      "so the results file now holds 13 runs. Every run used the same Tesla T4 GPU, the same seed, "
      "the same split file and its committed batch size, for 30.12 hours of measured GPU time in "
      "total: 19.89 hours for the ten-run matrix and 10.23 hours for the three repeats. Taking the "
      "repeat in place of the original where one exists, the test accuracies under fine-tuning are "
      "ViT-B/16 98.89%, VGG19 97.91%, DenseNet121 97.60%, EfficientNet-B0 97.56% and ResNet50 "
      "96.51%. Under feature extraction they are ViT-B/16 94.75%, DenseNet121 93.49%, ResNet50 "
      "92.98%, EfficientNet-B0 92.87% and VGG19 90.55%."),
("p", "Four observations are being carried into the second-phase write-up. The Vision Transformer "
      "wins in both modes, which is a direct answer to the CNN-versus-transformer question the "
      "project set out to ask; its lead over the best CNN under fine-tuning is about one "
      "percentage point, several times the sampling error on 20,000 test images, though from a "
      "single seed. VGG19 inverts between the two modes — last under feature extraction and second "
      "under fine-tuning, with by far the largest gain of the five — which is consistent with its "
      "frozen ImageNet features encoding object semantics that transfer poorly to a task whose "
      "evidence is low-level texture. The fine-tuned results of VGG19, DenseNet121 and "
      "EfficientNet-B0, between 97.5% and 97.9%, lie within 0.36 percentage points of one another, "
      "so on a single seed they will be reported as statistically indistinguishable rather than "
      "ranked."),
("p", "The fourth observation comes from the repeats, which had two different outcomes. "
      "EfficientNet-B0 under feature extraction returned the same best epoch and the same accuracy "
      "and stopped early on its own, so its original result was already converged. ResNet50 "
      "improved in both modes, from 92.83% to 92.98% under feature extraction and from 95.93% to "
      "96.51% under fine-tuning, but its best epochs fell at 49 and 48 of 50 with validation loss "
      "still falling slowly, so both rows remain lower bounds. The ceiling was not raised a third "
      "time: ResNet50 stays last under fine-tuning by about one percentage point, so its position "
      "is not an artefact of the epoch limit, and the write-up will state that it converges more "
      "slowly than the other four backbones under the committed training settings."),
("p", "The next steps are the Grad-CAM analysis across all five models and the cross-generator "
      "evaluation on GenImage. Both are built and have been tested locally on a synthetic copy of "
      "the GenImage folder layout, and are set up to run as a single evaluation session on Kaggle "
      "over the ten selected checkpoints, including an 80-cell cross-generator sweep. The first "
      "launch attempt on 23 September was rejected by Kaggle with an authorisation error before any "
      "computation began, so this stage is behind the schedule shown in the first progress report "
      "(Weeks 6 to 8); the next step is to replace the access credential and relaunch."),

_CONCL_H,
("p", "The review paper remains complete in draft: an abstract with six keywords, eight sections "
      "totalling roughly 9,850 words, a dataset comparison table covering 11 datasets, the master "
      "comparison table covering all 48 primary studies, and three figures. Every reference "
      "identifier in the bibliography — 74 in total — was opened and checked against its arXiv, "
      "Crossref or proceedings record, with the result logged one line per reference. The assembled "
      "draft was submitted for the departmental plagiarism check on 15 August 2026 and the result "
      "is awaited."),
("p", "Three conclusions carry into the second phase. Generalisation across generators is a "
      "structural problem rather than an engineering inconvenience, because a change of generator "
      "design can remove the evidence a detector relies on rather than merely obscure it. The "
      "strongest published cross-generator results share one of three properties: a representation "
      "that was never trained on detection data, an input derived from the image rather than the "
      "image itself, or training data spanning many generators. And cross-generator evaluation and "
      "explanation analysis are almost never carried out together, which is precisely the gap this "
      "project addresses. What remains for Semester VII is restyling the report into the official "
      "Amity template, the plagiarism-check result and any corrections arising from it, the team's "
      "own rewrite pass over the drafted prose, and the guide review in the final week, 5 to 9 "
      "October. For the second phase, the evaluation stage described above is the immediate step, "
      "followed by the planned ablations and the consolidation of all results into tables and "
      "figures. On 25 August 2026 the publication plan was revised, with the guide's approval, to "
      "a single merged research paper covering both semesters' work; the two Amity project reports "
      "are unchanged."),
]

# ---------------------------------------------------------------- PERT chart
# Review 1's chart with two changes: the three lower-bound reruns are added (run in Week 6,
# merged in Week 7), and the Grad-CAM / cross-generator row is moved from Weeks 6-8 to Week 11
# and labelled as revised, so the slip is visible rather than overwritten.
_MATRIX = next(i for i, (t, _) in enumerate(_c.PERT) if t.startswith("Transfer-learning"))
PERT = _c.PERT[:_MATRIX + 1] + [
 ("Lower-bound reruns of three runs at a 50-epoch ceiling", [6, 7]),
 ("Grad-CAM analysis and cross-generator evaluation (prepared; run pending, "
  "originally Weeks 6-8)", [11]),
]
