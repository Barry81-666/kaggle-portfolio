# Knee MRI Classification: Weak Labels and Grouped Validation

A source-based study of validation for 12-label knee MRI classification, centered on report-derived supervision, patient overlap and a reserved expert-labeled evaluation set. The public inference script and its 22 embedded Python modules are available here; measured CV and gold-set performance still require experiment records.

## Research Question

How can MRI classification trained with report-derived targets be evaluated without confusing agreement with weak labels, discrimination against expert labels, and separation of repeated examinations? The implementation makes these distinct evaluation questions, using grouped folds, training-only comparators and a reserved expert set.

## Data and Labels

The source targets the [RSNA Knee Abnormality Detection competition](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection). Its 12 findings cover ligament and meniscal injury, osteoarthritis, effusion, synovitis, Baker's cyst, contusion and fracture; exact names are in [common.py](source/rsna/common.py).

- **Weak / “silver” labels:** probabilities derived from radiology reports in a separate label file. They provide training supervision; agreement with them is not equivalent to agreement with expert annotations. Optional teacher probabilities can override training targets, with validation excluded from that operation.
- **Expert / “gold” labels:** studies with any official target present in `train.csv` are reserved by the fold builder. Gold evaluation requires complete official targets for all evaluated studies.
- **Images:** DICOM processing builds spatially normalized views and records missing inputs with masks. Missing images are not treated as negative labels. The public wrapper packages one fold-0 checkpoint configuration; the checkpoint itself is a private dependency.

## My Contribution

I published [this inference version on Kaggle as handudu](https://www.kaggle.com/code/handudu/rsna-knee-teacher-probs-exp017-v1-infer), version ID `358098927`. Specific implementation and team responsibilities await confirmation in the [contribution checklist](../../docs/CONTRIBUTIONS_AND_EVIDENCE.md); the design analysis below describes the archived code, with upstream model and augmentation credits retained under Sources.

## Validation Design

| Design decision | Implementation and reason | Boundary |
| --- | --- | --- |
| Keep linked examinations together | [audit.py](source/rsna/audit.py) identifies duplicates from canonical volumes/masks and inspects DICOM patient identifiers. [folds.py](source/rsna/folds.py) uses union-find to combine patient and duplicate associations, then assigns groups to five multilabel-stratified folds. | Patient identifiers are screened heuristically, not clinically adjudicated. If patient IDs are absent or incomplete, grouping falls back to study/verified duplicate groups; patient-level independence is then unproven. |
| Reserve expert labels | Gold studies and weak-label studies linked to their groups are excluded from weak-label folds. Frozen fold metadata records source hashes. | This prevents the overlaps recognized by the audit, not all possible undocumented patient relationships. |
| Freeze before gold evaluation | [evaluate.py](source/rsna/evaluate.py) requires a recipe-freeze file matching the checkpoint hash, complete gold labels and no overlap with training study IDs. | The guard checks the supplied receipt. It cannot establish that nobody inspected gold performance earlier. |
| Compare against simple priors | [metrics.py](source/rsna/metrics.py) estimates class probabilities only from the training fold and evaluates them on validation, alongside a constant 0.5 comparator. | These are comparators, not clinical prevalence estimates. Their actual measured values are unavailable. |
| Separate tuning from final assessment | [train.py](source/rsna/train.py) selects checkpoints by minimum unweighted weak-label validation BCE. Training class weights and optional teacher overrides use training rows. | A selected validation minimum is optimistic for final performance. Smoke/overfit modes are diagnostics, not validation results. |

### What Each Metric Answers

**BCE** penalizes probabilistic disagreement and is the implemented checkpoint-selection criterion on weak-label validation. **Brier score** measures mean squared error of probabilities against the available targets; on weak labels it measures agreement with those probabilities. Neither a Brier score alone nor its implementation establishes calibration.

**AUC** measures ranking discrimination. Weak-label AUC thresholds the target probabilities at 0.5; gold AUC uses expert targets. The implementation reports `macro_auc` only when **all 12 classes** have computable AUC. `available_class_mean_auc` is a separately named partial average and must not be substituted for full macro AUC. Missing target values are masked; per-class sample and outcome counts accompany the metrics.

Gold evaluation implements **2,000 bootstrap replicates by default**, seed 42, with percentile 2.5%/97.5% bounds for macro AUC. It resamples **studies, not patients**. Multiple examinations per patient can make intervals too narrow. Replicates missing a computable AUC for any class are skipped and their retained count is recorded; rare classes can make the resulting interval unstable or conditional on a selective subset of replicates. A patient-cluster bootstrap would be a future analysis requiring reliable patient identifiers.

## Evaluation and Results

| Evidence / outcome | Split and setting | Verified value or status |
| --- | --- | --- |
| Public source artifact | Kaggle version `358098927`; inference wrapper + 22 modules | Retrieved and hash-matched to the archived source; no runtime evaluation performed in this revision. |
| Prior baseline and trained model BCE / Brier / per-class and macro AUC | Weak-label validation, selected fold/epoch to be identified | Not available: requires metrics files, fold manifest and checkpoint identity. |
| Gold macro AUC and 95% bootstrap interval | Frozen checkpoint; complete expert labels; study resampling | Not available: requires freeze receipt, metrics JSON, class counts and retained replicate count. |
| Final public rank / score | Selected competition team submission | Not verified. |
| Final private rank / score | Selected competition team submission | Not verified. |

The [official overview](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview) lists the final submission deadline as **2026-10-22**. Final rank/score and the archived version's relationship to that submission remain open evidence items. Embedded visible-reference probabilities are parity-check fixtures, not outcome-based evaluation. No claim of demonstrated generalization, calibration or clinical utility follows from the available source.

## Limitations

The patient-grouping fallback and study-level bootstrap are material statistical limits. Report-derived labels can reflect report errors and differences in reporting practice. Expert-set completeness is enforced at evaluation, but set size, case mix and class counts cannot be assessed without the missing records. External-site performance is unmeasured here.

The archive also lacks private weights, complete training configurations and supporting experiment files referenced by the pipeline. Dense formatting is preserved to keep the source unchanged. Architectural alternatives in the package are not evidence that each was trained, selected or submitted.

## Reproduction Instructions

1. Read the [original Kaggle version](https://www.kaggle.com/code/handudu/rsna-knee-teacher-probs-exp017-v1-infer) and its inputs. Obtain authorized access to competition data and the exact private checkpoint; do not substitute an unrelated checkpoint when comparing results.
2. Record data, weak-label, configuration, runtime and checkpoint hashes. The [unpacked-file manifest](../../meta/projects/05-rsna-knee-inference/unpacked-files.json) identifies the 22 modules extracted from `inference.py`.
3. For a training reproduction, recover the missing experiment config and audit artifacts before using [pipeline.py](source/rsna/pipeline.py). Rebuild and review DICOM/patient audits, freeze group folds and record preprocessing versions. The pipeline references files outside this archive and includes Linux-specific checks.
4. With the original trained checkpoint and compatible cache available, evaluation is exposed through `python -m rsna.evaluate --checkpoint PATH --split silver --output PATH` from the `source/` directory. Gold evaluation additionally needs `--split gold --recipe-freeze PATH`; use a genuinely frozen protocol before the first gold evaluation. These are interface examples, not commands verified runnable with the public archive alone.
5. Preserve metric JSON, class counts, split identity and configuration alongside any publishable aggregate results. Do not add patient-level predictions or private data to this repository without a separate review.

[Read-only evidence retrieval](../../docs/KAGGLE_EVIDENCE.md) · [Missing evidence checklist](../../docs/CONTRIBUTIONS_AND_EVIDENCE.md) · [Archive notes](../../docs/ARCHIVE_NOTES.md)

## Sources

- [handudu's public inference script](https://www.kaggle.com/code/handudu/rsna-knee-teacher-probs-exp017-v1-infer), version `358098927`, published 2026-10-13; [provenance and hashes](../../meta/projects/05-rsna-knee-inference/provenance.json).
- The source in [model.py](source/rsna/model.py) credits **Dread Development** for a public twelve-finding training script/MIL head and **Heliosli** for image/geometry attention adaptations. [geometry_views.py](source/rsna/geometry_views.py) documents the alternative geometry path.
- [augmentation.py](source/rsna/augmentation.py) credits **goodpjw2008** and **nartaa** for referenced augmentation recipes. An upstream score mentioned in the source is not a result of this portfolio.
- No fork flag was exposed for this script in the public inventory. That does not establish independent authorship; the source's attributions remain intact.
