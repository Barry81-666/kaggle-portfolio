# Barry Wang · Biomedical Data Science & Kaggle Portfolio

I compete on Kaggle as [handudu](https://www.kaggle.com/handudu). This portfolio collects my biomedical competition work and selected projects in computational biology and medical imaging.

## Biomedical Competition Results

Kaggle Competitions **Expert** (ranked 807 of 221,860; highest 540), with **7 silver and 4 bronze** team competition medals; four of the silver medals are in biomedical imaging. Ranks are team ranks as listed on my Kaggle profile (October 2026). [Full competition record](COMPETITION_RESULTS.md)

| Competition | Team rank | Medal | My role | Code |
| --- | --- | --- | --- | --- |
| [BYU - Locating Bacterial Flagellar Motors 2025](https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025) | 15 / 1136 | Silver | Prepared slice-level training data and local validation, trained YOLO-family detectors, and built multi-model fusion with 3D non-maximum suppression. | [Notebook](projects/02-bacterial-motor-detection/) |
| [Sartorius - Cell Instance Segmentation](https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation) | 26 / 1505 | Silver | Trained MMDetection instance segmentation models and tuned class-specific score thresholds, minimum mask sizes and overlap removal. | [Notebook](projects/04-cell-instance-segmentation/) |
| [UW-Madison GI Tract Image Segmentation](https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation) | 29 / 1548 | Silver | Built slice-stacking preprocessing and case-grouped validation folds, trained segmentation models, and ensembled them with post-processing. | — |
| [RSNA Screening Mammography Breast Cancer Detection](https://www.kaggle.com/competitions/rsna-breast-cancer-detection) | 46 / 1687 | Silver | Built DICOM preprocessing and ROI cropping, trained image classifiers, and ensembled models with decision-threshold selection for the probabilistic F1 metric. | — |

The linked notebooks are public notebooks I published during these competitions; they are not presented as the teams' final submissions.

<details>
<summary>Seven additional competition results</summary>

| Competition | Team rank | Medal |
| --- | --- | --- |
| [WSDM Cup - Multilingual Chatbot Arena](https://www.kaggle.com/competitions/wsdm-cup-multilingual-chatbot-arena) | 27 / 950 | Silver |
| [Feedback Prize - Predicting Effective Arguments](https://www.kaggle.com/competitions/feedback-prize-effectiveness) | 42 / 1557 | Silver |
| [Feedback Prize - Evaluating Student Writing](https://www.kaggle.com/competitions/feedback-prize-2021) | 87 / 2058 | Silver |
| [CMI - Detect Behavior with Sensor Data](https://www.kaggle.com/competitions/cmi-detect-behavior-with-sensor-data) | 160 / 2657 | Bronze |
| [Image Matching Challenge 2025](https://www.kaggle.com/competitions/image-matching-challenge-2025) | 62 / 943 | Bronze |
| [Eedi - Mining Misconceptions in Mathematics](https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics) | 118 / 1446 | Bronze |
| [PetFinder.my - Pawpularity Contest](https://www.kaggle.com/competitions/petfinder-pawpularity-score) | 253 / 3537 | Bronze |

</details>

## Selected Projects

| Project | What it shows |
| --- | --- |
| [Knee Diagnostic Labels Without a Gold Standard](projects/11-knee-report-label-accuracy/) | Five public report-derived label sets for 4,349 knee MRI studies: aligning documented definitions for two sources resolves most of their disagreement, and simulations show how majority-vote references can favour models that share a labelling style. [Results](projects/11-knee-report-label-accuracy/report.md). |
| [Image2Biomass: Validation Across Split Designs](projects/03-image2biomass/) | Image regression of pasture biomass under four fold designs. Mean weighted R² falls from 0.68 with random folds to 0.58 with sampling-date folds and 0.49 with species folds; [full results](results/image2biomass.md). |
| [RNA Sequence and Structure Exploration](projects/01-rna-folding/) | Exploratory analysis of RNA sequences and 3D coordinates; silver Notebook medal. |
| [Coral Reef Object Detection with YOLOv5 and WBF](projects/08-reef-object-detection/) | Ecological image detection with weighted box fusion; bronze Notebook medal. |

<details>
<summary>Other machine learning projects</summary>

| Project | What it shows |
| --- | --- |
| [Time Series Validation for Tactical Allocation](projects/06-time-series-validation/) | Rolling-window validation and hyperparameter selection for market prediction; bronze Notebook medal. |
| [Multilingual Preference Prediction with Gemma and LoRA](projects/07-chatbot-preference-lora/) | LoRA adapter inference with swapped-response augmentation; bronze Notebook medal. |
| [Mathematical Reasoning with Code Execution](projects/09-llm-code-reasoning/) | Annotated study of a public code-execution solution. |
| [Tabular Fraud Classification with CatBoost](projects/10-tabular-fraud-catboost/) | CatBoost baseline with stratified cross-validation. |

</details>

Notebook medals are awarded for public notebooks and are separate from the competition results above.

Code is archived as published on Kaggle; data and weights are not included.

[Results and figures](results/) · [Sources and attribution](SOURCES.md)
