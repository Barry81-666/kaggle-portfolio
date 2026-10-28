# Tabular Fraud Classification with CatBoost

A historical CatBoost binary-classification notebook using private tabular data. It is retained as a learning baseline, with its preprocessing and AUC limitations explicitly documented.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/tianchi-finance), version ID `116279535`. The public inventory did not mark this as a fork; that is not an independent-authorship audit. Publication under the handudu account is recorded; task-specific personal contributions have not been independently established.

## Running and Interpreting the Archive

The data are private. The code fits an encoder on combined training/test tables and calculates validation AUC from hard class predictions. A new analysis should use fold-specific preprocessing and predicted probabilities; this source is preserved unchanged apart from language edits.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/10-tabular-fraud-catboost/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
