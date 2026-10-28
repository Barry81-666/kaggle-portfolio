# Barry Wang · Biomedical Data Science & Kaggle Portfolio

I publish on Kaggle as [handudu](https://www.kaggle.com/handudu). This portfolio brings together biomedical competition achievements and selected projects in computational biology, medical imaging and machine learning. Project pages explain modeling choices and present historical results with their evaluation settings.

## Biomedical Team Competition Results

Kaggle Competitions **Expert**; **7 silver and 4 bronze team competition medals** in the recorded account history. The four biomedical silver medals below are **team competition results**. Source: the repository's authenticated Kaggle **Your Work → Competitions** record, verified **2026-10-24**; [full record and evidence scope](COMPETITION_RESULTS.md).

| Competition | Team rank / teams | Medal | My role | Related code |
| --- | --- | --- | --- | --- |
| [BYU - Locating Bacterial Flagellar Motors 2025](https://www.kaggle.com/competitions/byu-locating-bacterial-flagellar-motors-2025) | 15 / 1136 | Silver | Prepared slice-level training data and local validation, trained YOLO-family detectors, and built multi-model fusion with 3D non-maximum suppression. | [Related code (forked inference notebook)](projects/02-bacterial-motor-detection/) |
| [Sartorius - Cell Instance Segmentation](https://www.kaggle.com/competitions/sartorius-cell-instance-segmentation) | 26 / 1505 | Silver | Trained MMDetection instance segmentation models and tuned class-specific score thresholds, minimum mask sizes and overlap removal. | [Related code (forked inference notebook)](projects/04-cell-instance-segmentation/) |
| [UW-Madison GI Tract Image Segmentation](https://www.kaggle.com/competitions/uw-madison-gi-tract-image-segmentation) | 29 / 1548 | Silver | Built slice-stacking preprocessing and case-grouped validation folds, trained segmentation models, and ensembled them with post-processing. | — |
| [RSNA Screening Mammography Breast Cancer Detection](https://www.kaggle.com/competitions/rsna-breast-cancer-detection) | 46 / 1687 | Silver | Built DICOM preprocessing and ROI cropping, trained image classifiers, and ensembled models with decision-threshold selection for the probabilistic F1 metric. | — |

<details>
<summary>Seven additional team competition results</summary>

| Competition | Team rank / teams | Medal |
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

| Project | Method / evidence to inspect |
| --- | --- |
| [Knee Diagnostic Labels Without a Gold Standard](projects/11-rsna-knee-leaderboard-reliability/) | Five public label sources across 4,349 studies; agreement and latent-model diagnostics; simulations showing when AUC misclassification correction fails. [Results](analysis/rsna-knee-public/report.md). |
| [Image2Biomass: Validation Across Split Designs](projects/03-image2biomass/) | Image regression; recovered five-fold logs across four split settings. Mean best-fold weighted R²: 0.6820 for random splits, 0.5774 for sampling-date splits; [settings and selection caveats](results/image2biomass.md). |
| [RNA Sequence and Structure Exploration](projects/01-rna-folding/) | Descriptive sequence/structure analysis with a recovered EDA figure; mixed Python/R source. |
| [Time Series Validation for Tactical Allocation](projects/06-time-series-validation/) | Rolling validation and hyperparameter selection. |
| [Multilingual Preference Prediction with Gemma and LoRA](projects/07-chatbot-preference-lora/) | Adapter inference and swapped-response augmentation. |
| [Coral Reef Object Detection with YOLOv5 and WBF](projects/08-reef-object-detection/) | Detection ensemble and weighted box fusion. |
| [Mathematical Reasoning with Code Execution](projects/09-llm-code-reasoning/) | Annotated learning/debugging fork. |
| [Tabular Fraud Classification with CatBoost](projects/10-tabular-fraud-catboost/) | Historical tabular baseline with evaluation caveats. |

Notebook recognition is separate from competition ranking: RNA has one **silver Notebook medal**; time series, multilingual preference and reef detection each have a **bronze Notebook medal** (Kaggle snapshot 2026-10-24).

Code is archived as published on Kaggle; data and weights are not included.

[Results and figures](results/) · [Sources and attribution](SOURCES.md)
