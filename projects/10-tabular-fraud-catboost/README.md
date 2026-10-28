# Tabular Fraud Classification with CatBoost

I include this historical CatBoost binary-classification notebook using private tabular data as a learning baseline, with its preprocessing and AUC limitations documented below.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/tianchi-finance), version ID `116279535`. Published from my Kaggle account; credits to other authors inside the source are kept intact.

## Running and Interpreting the Archive

The data are private. The code fits an encoder on combined training/test tables and calculates validation AUC from hard class predictions. A new analysis should use fold-specific preprocessing and predicted probabilities; this source is preserved unchanged apart from language edits.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/10-tabular-fraud-catboost/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
