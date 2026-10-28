# Multilingual Preference Prediction with Gemma and LoRA

Gemma inference with PEFT/LoRA adapters for multilingual response-preference prediction. The notebook uses two GPUs and combines predictions after swapping response order; some explanatory Markdown describes alternative code rather than executed cells.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/lmsys-peft0-14-0), version ID `217218292`. The public inventory did not mark this as a fork; that is not an independent-authorship audit. Publication under the handudu account is recorded; task-specific personal contributions have not been independently established.

## Running and Interpreting the Archive

The notebook requires specific offline wheels, a base model, two GPUs and LoRA weights; three inputs were private in the source snapshot. Model loading and inference were not rerun.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/07-chatbot-preference-lora/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
