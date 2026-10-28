# Public RSNA code review

Reviewed 2026-10-28: 16 repositories (10 knee, 6 lumbar-spine). All README files and repository trees were inspected; selected source files were read in 11 repositories (13 Python files plus one license). This is a focused review, not a claim to have audited every source file or reproduced any author's result. The complete inspected-file list and pinned revisions are in [repositories.json](repositories.json).

## Screening decisions

| Repository | Terms at inspected revision | Relevant evidence and decision |
| --- | --- | --- |
| [homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection](https://github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection/tree/a6040355cfc5d03688846ad6afd8aac4b30bbb92) | Not declared | Label-availability audit and report coverage; use as a schema reference. Published label agreement is specific to that author's labeler. |
| [SathishKumarAI/rsna-knee-2026](https://github.com/SathishKumarAI/rsna-knee-2026/tree/c5e882073d570cdfd377d36c17b30584dfde3246) | Not declared | Per-finding metrics and subgroup hooks; skips undefined classes in its headline mean, so that convention is not adopted. |
| [Sibusiso-K/RSNA-Knee-Abnormality-Detection](https://github.com/Sibusiso-K/RSNA-Knee-Abnormality-Detection/tree/e68ba6bcbf174b4b3327a73b94ca5a794d0e225e) | Not declared | Fresh evaluation explicitly retains 57 gold rows and states checkpoints were selected on validation folds; counts and selection history require auditing. |
| [Tomashcv/RSNAKnee2026-Showcase](https://github.com/Tomashcv/RSNAKnee2026-Showcase/tree/bb57074b098a9646c05f3e29802c219dbfabc143) | Not declared | Documentation-only showcase at the inspected revision; no executable pipeline available to reuse. |
| [NTejas-1/RSNA-Knee-Abnormality-Detection](https://github.com/NTejas-1/RSNA-Knee-Abnormality-Detection/tree/1c386ac71385ba7683f550b87a465386ba6c36a8) | MIT; component exclusions | OOF uniqueness and label-audit scripts; own-code MIT with third-party exclusions. Row-level labels/OOF are present upstream but were not downloaded. |
| [AhmadEnan/RSNA-Knee-Abnormality-Detection](https://github.com/AhmadEnan/RSNA-Knee-Abnormality-Detection/tree/b9327f58e17a03fd442cbeb4910be32ac5534332) | MIT | Minimal README and no standalone Python files in the inspected tree; insufficient evidence of a reusable evaluation pipeline. |
| [liamd-schneider/RSNA-Knee-Abnormality-Detection](https://github.com/liamd-schneider/RSNA-Knee-Abnormality-Detection/tree/a0c20aaf4dab696288c44ad8a2b8e8d7235de58f) | MIT | MIT DICOM utility and label-extraction/training files; code exists, but no matched prediction contract established for this study. |
| [switzloco/creaky](https://github.com/switzloco/creaky/tree/f14f3dba883e12909a5fb2bc3b1a2f32ebb62447) | Apache-2.0 | Apache-2.0 gold/silver comparison and label-audit code; some AUC code drops 0.5 labels and averages only defined classes. Neither rule is silently inherited. |
| [trungdo1810/RSNA2026-Knee](https://github.com/trungdo1810/RSNA2026-Knee/tree/fd62ba0a2b26e79a23cdd6dea1b49225d224dc3d) | Not declared | Scanner-fingerprint fold construction; scanner-grouped splitting answers a different question from patient/duplicate clustering. |
| [Evan2001ok/rsna-knee-abnormality-detection](https://github.com/Evan2001ok/rsna-knee-abnormality-detection/tree/32a89014d40f0244623b43118ea89d6855814e48) | Not declared | Pipeline documentation/notebooks, no standalone Python module at inspected revision; not treated as an immediately reproducible prediction source. |
| [yu4u/kaggle-rsna2024-4th](https://github.com/yu4u/kaggle-rsna2024-4th/tree/fe7bd995e8ff61b63d035337c9dac8b6a732bc38) | MIT | MIT spine pipeline with explicit fold filtering and OOF artifacts. Useful engineering reference; different disease labels and outcome metric. |
| [lhwcv/solution-rsna-2024-lumbar-spine](https://github.com/lhwcv/solution-rsna-2024-lumbar-spine/tree/f466285646a2ca4047cf794c4be6fe34afd9ecbf) | MIT | MIT spine DICOM normalization and two-stage models. Reference for imaging preparation only, not a knee-label statistical validation. |
| [hengck23/solution-rsna-2024-lumbar-spine](https://github.com/hengck23/solution-rsna-2024-lumbar-spine/tree/8587dae47ff9ba0a3f3ab1d120cc2a8f5cc54f25) | MIT | MIT one-stage spine solution; README distinguishes a historical augmentation bug and corrected models. Useful model-lineage documentation. |
| [siwooyong/RSNA-2024-Lumbar-Spine-Degenerative-Classification](https://github.com/siwooyong/RSNA-2024-Lumbar-Spine-Degenerative-Classification/tree/2b88d91aa7a4bcf570fbdc08743275b4d27e3e07) | Not declared | Two-stage spine method description and notebooks; no declared repository license. Method reference only. |
| [TheoViel/kaggle_rsna_lumbar_spine](https://github.com/TheoViel/kaggle_rsna_lumbar_spine/tree/0e4dbea8ce16249792ec64cefa4cd5510eda7cdb) | Apache-2.0 | Apache-2.0 spine metric module; missing-class AUC may be replaced by 0.5. This behavior is explicitly rejected for the twelve-finding knee estimand. |
| [phalendj/rsna2024](https://github.com/phalendj/rsna2024/tree/a9cd947297bdccfbef8b1714a8b3e48210a15c8e) | MIT | MIT spine evaluation and spatial preprocessing; demonstrates why geometry/selection must be specified. Not a source of knee results. |

## What is used here

The new R analysis is independently implemented from the SAP and statistical references. No external competition code, weights, reports, labels or predictions are vendored. The exporter supports ordinary wide CSV predictions and configurable column names, so existing pipelines can supply inputs without re-training. Upstream license obligations would apply to any future copied implementation; a public repository alone is not permission to relicense it.

Priority references are NTejas-1 for OOF coverage checks, switzloco for paired gold/weak label audit, Sibusiso-K for cohort/selection provenance, and yu4u for fold bookkeeping. Their published metrics remain their results, not Barry Wang's. Some public repositories contain individual-level files; this review did not retrieve them.

## Findings that changed the analysis

- Gold must be identified by local labels and inclusion audits. A nominal 58 is not a guaranteed analytic sample size.
- A unique OOF row is necessary, but training-membership and patient/duplicate-group checks are also required.
- AUC over only defined classes must not be labeled the twelve-class macro AUC. Undefined is not 0.5.
- An ensemble evaluated on gold and per-fold predictions evaluated on silver represent different scoring protocols.
- Some upstream studies selected checkpoints on the same validation folds. Conditional uncertainty does not remove that selection bias.
- Scanner, study and patient are different grouping units. Do not equate them.

