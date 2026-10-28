# Knee MRI Classification: Weak Labels and Grouped Validation

A validation-focused case study of 12-label knee MRI classification, with a recorded historical Kaggle public score of **0.942** and an inspectable inference package.

## Research Question

How should a classifier trained on radiology-report targets be evaluated when expert annotations are scarce and patients may have repeated examinations? The implementation separates weak-label agreement, expert-label discrimination and examination grouping.

## Data and Labels

The [RSNA competition](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection) targets 12 knee findings. Report-derived probabilities provide weak (“silver”) supervision; official expert (“gold”) labels define a reserved evaluation set. Any study with an official target enters the gold reservation; gold evaluation requires complete labels. Optional teacher probabilities affect training rows only.

DICOM preprocessing creates spatially normalized views and missing-input masks. Missing images are not negative labels. The public inference configuration packages one fold-0 model with anatomical left/right augmentation; its checkpoint is a private dependency.

## My Contribution

I published [this inference version as handudu](https://www.kaggle.com/code/handudu/rsna-knee-teacher-probs-exp017-v1-infer), version ID `358098927`. This case study explains its implementation; source-level credits identify upstream model and augmentation work.

## Validation Design

| Decision | Implementation and purpose | Boundary |
| --- | --- | --- |
| Group related examinations | [Audit](source/rsna/audit.py) identifies duplicate volumes and patient associations; [union-find](source/rsna/folds.py) merges associations before five-fold multilabel stratification. | Missing/incomplete patient IDs cause fallback to study/duplicate groups; patient independence is then uncertain. |
| Reserve expert labels | Exclude gold studies and linked weak-label studies from training folds; freeze fold hashes. | Protection covers detected relationships. |
| Freeze before gold evaluation | Require a checkpoint-matched recipe-freeze receipt and no training-study overlap. | A receipt cannot establish absence of earlier gold-set inspection. |
| Use simple comparators | Estimate class priors from the training fold; compare with constant 0.5 probabilities. | Priors describe training targets, not clinical prevalence. |
| Separate selection and assessment | Select checkpoints by minimum weak-label validation BCE. | The selected minimum is optimistic; smoke/overfit modes are diagnostics. |

**BCE** assesses probabilistic disagreement; **Brier score** measures squared probability error, without alone establishing calibration. Weak-label **AUC** thresholds targets at 0.5; gold AUC uses expert labels. Full macro AUC requires all **12 classes** to be computable; the separately named available-class average is not equivalent.

Gold evaluation uses **2,000 bootstrap replicates**, seed 42, and percentile 95% bounds by default. Sampling is by **study**, so repeated patients may produce narrow intervals. Replicates lacking any class AUC are excluded; the retained count must accompany the interval.

## Evaluation and Results

| Recorded result | Value | Interpretation |
| --- | --- | --- |
| Notebook-associated best public score | **0.942** | Official Kaggle `bestPublicScore`, recorded 2026-10-24 and checked again 2026-10-28; not a local CV or final private score. |

The [score record](../../results/rsna-knee-public-score.json) preserves the source fields and version identity. Local fold/baseline metrics and final private standings were not available in the inspected records. Embedded reference predictions test inference parity, not outcome discrimination. The competition closed on 2026-10-22.

## Limitations

Report noise, incomplete patient identities and study-level resampling limit interpretation. The public score does not establish external-site generalization, calibration or clinical utility. Private checkpoints and complete experiment configurations are absent; source remains unchanged.

## Reproduction Instructions

Use the original Kaggle inputs and exact checkpoint. Record data/configuration hashes, review patient/duplicate audits and freeze folds before evaluation. From `source/`, the evaluation interface is `python -m rsna.evaluate --checkpoint PATH --split silver --output PATH`; gold evaluation requires `--split gold --recipe-freeze PATH`. These interfaces require assets beyond this archive. See [archive notes](../../docs/ARCHIVE_NOTES.md).

## Sources

[Provenance](../../meta/projects/05-rsna-knee-inference/provenance.json) and the [22-module manifest](../../meta/projects/05-rsna-knee-inference/unpacked-files.json) identify the source. [Model code](source/rsna/model.py) credits Dread Development and Heliosli; [augmentation code](source/rsna/augmentation.py) credits goodpjw2008 and nartaa. Their reported scores are not attributed to this project.
