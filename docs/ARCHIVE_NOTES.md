# Archive and Reproduction Notes

This portfolio separates three kinds of evidence: **implementation** visible in source; **historical execution** recorded in a specific public output; and **evaluation results** tied to a defined split and metric. The ten source versions are not asserted to be the selected final competition submissions.

## Source Handling

The previous archive cleared notebook outputs, execution counts and execution metadata. This revision translates Chinese comments, Markdown and documentation/display text. Operational identifiers, expressions, paths and keys are preserved. Existing English comments, author credits and copyright text remain unchanged. RSNA's wrapper and all 22 extracted modules remain byte-identical.

Comment-only changes preserve the complete non-comment code-token sequence. Translated docstrings, printed messages and f-string text necessarily change string tokens: all 88 occurrences are listed in [translation-exceptions.json](../meta/translation-exceptions.json), and the validator permits only those exact substitutions. F-string expressions are unchanged. A Chinese report-matching regex and a historical output filename are intentionally retained; translating either would change behavior. Historical source titles and the before/after audit ledger also retain original Chinese text.

Each [project provenance file](../meta/projects/) preserves the Kaggle version ID, original download SHA-256 and pre-translation archive SHA-256 under `original`, with the current/translated SHA-256 separately recorded. The public source download may contain original outputs; its hash is therefore different from the output-cleared archive hash.

Repeated code, dense one-line modules and mixed-language RNA code cells are preserved. Their limitations are described on the project pages instead of silently changing the historical implementation. Existing source attribution and copyright notices are retained; no replacement repository-wide license is introduced.

## Execution and Inputs

No model training, inference, generated-code execution or installation cell was run during this revision. [Selected public outputs](../results/) were recovered from hash-matched original versions; they are not new experiments. Dataset files, model weights, local credentials, private notebooks and team code newly obtained from private sources are not included.

Most notebooks depend on Kaggle competition data, historical packages or private model inputs. Use the original page and exact version to inspect dependencies. The RSNA archive also lacks complete experiment configs and referenced training assets. Successful static checks are not a runnable-environment guarantee.

[Read-only retrieval instructions](KAGGLE_EVIDENCE.md) · [Validation](../VALIDATION.md) · [Evidence to complete](CONTRIBUTIONS_AND_EVIDENCE.md)
