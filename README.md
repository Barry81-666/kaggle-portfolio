# Barry_Wang · Kaggle Portfolio

A curated source archive of computational biology, biomedical imaging, data science, and machine learning projects from [Barry_Wang's public Kaggle work](https://www.kaggle.com/handudu).

Selected from 20 public notebooks and scripts, this portfolio features **10 projects**: five focused on biology and medicine, and five on data science, time series, and machine learning. The selection includes **one silver and three bronze Notebook medals**. These are **Kaggle Notebook medals**, not competition placements or prizes.

The public profile lists a **Competitions Expert** tier, with **seven silver and four bronze competition medals**, plus **one silver and three bronze Notebook medals**. All 11 competition medals and team ranks were verified while signed in and are documented in [Competition Results](COMPETITION_RESULTS.md). The relationship between the archived code versions and the final scored submissions still needs verification. See the [account snapshot](account-snapshot.json).

## Projects

| Project | Focus | Notebook Medal |
| --- | --- | --- |
| [RNA 3D Folding · EDA](projects/01-rna-folding) | Computational biology / Exploratory data analysis | 🥈 Silver |
| [Bacterial Flagellar Motor Detection](projects/02-bacterial-motor-detection) | Computational biology / 3D object localization | — |
| [Image2Biomass Training Baseline](projects/03-image2biomass) | Biology and agriculture / Regression modeling | — |
| [Cell Instance Segmentation with MMDetection](projects/04-cell-instance-segmentation) | Biomedical imaging / Instance segmentation | — |
| [RSNA Knee MRI Inference](projects/05-rsna-knee-inference) | Medical imaging / Classification inference | — |
| [Hull Tactical · Time Series Validation](projects/06-time-series-validation) | Data science / Time series | 🥉 Bronze |
| [Multilingual Chatbot Preference · LoRA](projects/07-chatbot-preference-lora) | Machine learning / Large language model inference | 🥉 Bronze |
| [Great Barrier Reef · YOLOv5 + WBF](projects/08-reef-object-detection) | Ecological imaging / Object detection | 🥉 Bronze |
| [Mathematical Reasoning · Annotated Notebook](projects/09-llm-code-reasoning) | Machine learning / Mathematical reasoning | — |
| [Tabular Fraud Classification · CatBoost](projects/10-tabular-fraud-catboost) | Data science / Tabular classification | — |

The biology projects focus on RNA exploration, biological image detection, segmentation, and regression. The current public collection does not include dedicated projects on clinical trials, survival analysis, or causal inference.

## How to Use

1. Open each project's README for its scope, upstream sources, and dependency constraints.
2. Preview `notebook.ipynb` on GitHub, or browse the RSNA project's `source/rsna/` modules.
3. To run a project, start with its original Kaggle page and configure the data, models, and environment according to its inputs and original setup.

This repository is a source archive and project index. Training and inference were not run, and leaderboard results were not reproduced during archiving. Most projects require the original model weights, and some input sources are private. Dataset files, model weights, credentials, and notebook outputs are excluded.

The silver-medal RNA notebook contains unexecuted R cells in its later sections, and the MMDetection project uses an older environment. Methodological and environment limitations in some learning and debugging code are documented in the individual project READMEs. Source code is preserved as published, with notebook execution outputs removed.

## Sources, Versions, and Validation

- [Project catalog](catalog.json) / [CSV index](catalog.csv): versions, medals, sources, SHA-256 hashes, and dependencies.
- [Screening record for all 20 public projects](inventory.json): reasons for exclusion and empty exports.
- [Sources and contributions](SOURCES.md): distinguishes published versions from upstream work. Fork relationships are recorded in each project's provenance file; inclusion does not imply sole authorship.
- [Static validation record](VALIDATION.md): the scope of checks on file structure, source fidelity, and sensitive content.
