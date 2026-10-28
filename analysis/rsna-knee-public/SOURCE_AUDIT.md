# Public-source feasibility audit

Checked 2026-10-28. This document records the pre-analysis metadata and schema audit; empirical findings are in [the report](report.md). [datasets.csv](datasets.csv) pins the selected file/version for 11 screened sources; [discovery.csv](discovery.csv) contains 35 unique search hits, including weights and other ineligible assets. Thirty-five hits do not mean 35 independent label sets.

## Retired leaderboard feasibility work

[Meta Kaggle](https://www.kaggle.com/datasets/kaggle/meta-kaggle), version 2370, lists an **Apache 2.0** license. The publisher says this is a filtered/transformed snapshot, not a complete database dump. Anonymous metadata, file listing and byte-range reads succeeded. A full Competitions download timed out after a partial transfer. Competition inclusion, full-precision availability for its submissions and final leaderboard completeness remain unverified. No statistical leaderboard result has been calculated.

Submissions headers include `IsSelected`, `IsAfterDeadline`, both display scores, both full-precision scores and submission/scoring dates. Teams includes `CompetitionId`, both leaderboard submission IDs, benchmark and medal fields. Submissions has `TeamId` rather than `CompetitionId`; an out-of-memory-safe scan must join through Teams. These verified headers support a feasible acquisition plan but do not establish valid row coverage.

An anonymous competition-list API request returned 401. No credentials were supplied and no competition files were requested. If public metadata cannot establish coverage, follow the fallback in the SAP rather than accessing personal submission records.

## Requested label sources

| Source | License shown by publisher | Schema/decision |
| --- | --- | --- |
| [Dread](https://www.kaggle.com/datasets/dreaddevelopment/rsna-knee-labels), v3 | CC0 | 4,349 rows; ID + 12 scores. Original extraction; author describes Gold58 exclusion. Primary analysis source. |
| [JEV](https://www.kaggle.com/datasets/riadmohamed42/jev-knee-labels), v5 | CC0 | Selected score file: 4,407 rows; ID + 12 scores. Shared Steven/Pilkwang ancestry and expert-panel tuning; secondary. Expert evaluation files in the release are not used. |
| [flight](https://www.kaggle.com/datasets/flight0234/rsna-knee-hybrid-report-labels), v1 | CC0 | 4,407 rows; 12 scores + 12 confidence fields + ID. Steven v4 with a Pilkwang fracture substitution chosen using expert-panel performance. Secondary. |
| [Steven](https://www.kaggle.com/datasets/stevenleehans/rsna-knee-llm-report-labels), v6 | CC0 | Original full file: 4,407 rows; ID + 12 scores. v2/v4 are separate, derived versions; do not count them as independent raters. |
| [Pilkwang](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels), v1 | CC0 | 4,406 rows; ID, 12 scores, confidence and verdict fields. Scores are not guaranteed calibrated probabilities. Primary analysis source. |
| [11-label fusion](https://www.kaggle.com/datasets/omerzalman/rsna-knee-11-label-evidence-fusion), v2 | CC BY-NC 4.0 | Publisher reports 4,407 studies and 11 findings; Synovitis absent. Its attribution file describes text sources, MRI readers and expert-panel development. Excluded from report-only primary analysis; label values were not downloaded for this audit. |

Additional schema-checked CC0 sources are Yunus's report extraction and Lixin's GPT extraction (each 4,407 rows, ID + 12 scores), a four-source merge and a consensus release. The latter two are derivative comparisons. Qwen is a candidate with CC0 metadata but its file/schema eligibility has not yet been checked. See the manifest for exact URLs and versions.

The pre-analysis audit inspected row/column counts, public descriptions and attribution. At that stage it did **not** calculate prevalence, agreement, sensitivity/specificity, Gold58 comparisons or leaderboard associations. Label raw files acquired during earlier source exploration remain outside the repository; this study will use only the new manifest's allowed files. Earlier expert-label proposals and materials are excluded.

## File and ancestry controls

Download only an approved label CSV, never the complete archive. Never download `train.csv`, expert-label evaluation sets, `study_metadata.csv`, report-review files, weights or image predictions. Check the selected CSV against the allowed score/confidence/verdict schema before retaining it. A missing finding is missing, not negative.

No raw tables are redistributed. Dataset authors are credited as sources, not evaluated as teams. Source-level license declarations are recorded; a derivative source is not proof of independent evidence or of downstream permission for every unrelated file in its archive.

## External numerical evidence

The [pinned public write-up](https://github.com/TaeyanG4/rsna-knee-abnormality-detection/blob/3f79eae93147c303f788e07144f590ace092edb0/README.md) supplies aggregate claims and source ancestry. It updates preliminary leaderboard counts on 2026-10-28; both versions are retained in parameters.csv with verification flags. We do not use that team's personal submission ledger or copy its training code.

[RSNA's announcement](https://www.rsna.org/news/2026/august/ai-challenge-knee-mri) provides official challenge context. [This independent public repository](https://github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection) reports a random/grouped validation difference; this is an external claim, not a replicated finding. Neither published agreement percentages nor a single source's validation difference determines latent sensitivity/specificity.

No third-party code is vendored. The R foundation in this project is newly written; the methods are attributed in the SAP. Unverified counts or source summaries are not presented as this project's results.

## B/C execution scope

SAP v1.2 discontinued empirical leaderboard acquisition. Only the five original extraction files listed in [source_files.csv](../../results/rsna-knee-public/source_files.csv) were used for B. The manifest preserves public dataset version numbers and SHA-256 of the selected files. The five-source intersection contains 4,349 studies. Dread and Lixin are thresholded at 0.5; Pilkwang uses YES/NO/UNK verdicts; Steven 0.5 and Yunus 0.05/0.5 are documented unknowns. The old boolean `half_is_unknown` column is a screening field, not the complete harmonization specification; SAP v1.2 and R/21_label_analysis.R are authoritative. Known derivative releases were screened but not analyzed in the final main study. The current downloader fetches only the five primary files and their public metadata.

## Post-hoc provenance review, 2026-10-29

Following inspection of F5, the public descriptions cached in the 2026-10-28 metadata audit were reread to distinguish label definitions from demonstrable file ancestry. These are publisher statements, not independent checks of every extraction step.

| Primary source/file | Relevant public description | What it does and does not establish |
| --- | --- | --- |
| [Steven](https://www.kaggle.com/datasets/stevenleehans/rsna-knee-llm-report-labels), `llm_labels_full.csv` | The original v1 file is retained for reproducibility. The page credits Pilkwang's baseline and other contributors. Separate v2/v4 files use additional rules; **v4 explicitly blends v2 with Lixin**. The page also describes expert-panel benchmarking. | Attribution does not establish that original labels were copied. The documented later blend is not the selected primary file. Exposure to published expert-panel feedback cannot be excluded. |
| [Pilkwang](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels), `report_labels_v2.csv` | Original-language extraction with YES/NO/UNK verdicts and separate severity information; YES denotes an asserted finding. | Its binary verdict is not the same rule as thresholding severity at 0.5. No explicit reuse of another label file was identified in this description. |
| [Yunus](https://www.kaggle.com/datasets/yunusgmsoy/rsna-knee-llm-report-labels), `yunus_llm_labels.csv` | Described as pure Gemini Flash extraction without blending or post-processing. Mild/trace findings receive 0.25, moderate 0.55, uncertain 0.50, and unmentioned 0.05. The page reports expert-panel benchmarking. | Under this study's 0.5 threshold, mild/trace is negative, whereas an asserted mild finding can be positive in Pilkwang's verdict. This is a documented operational distinction, not proof of the cause of each disagreement. |
| [Dread](https://www.kaggle.com/datasets/dreaddevelopment/rsna-knee-labels), `labels_llm_soft.csv` | Describes soft scores extracted from reports by an LLM. | No sufficiently detailed severity/abstention rule or upstream-label ancestry is documented in the reviewed description. Publisher calibration claims are not validated here. |
| [Lixin](https://www.kaggle.com/datasets/lixin73/rsna-knee-llm-report-labels-sol56), `labels_llm_gpt56sol.csv` | The title names a GPT extraction; the description is empty. Steven's later blend credits this source. | Detailed prompting, thresholds and the primary file's ancestry remain undocumented. This is not evidence of either independence or copying. |

The selected files show similarity clusters, while public documentation confirms some **later derivative** relationships and differing label conventions. Neither finding establishes shared errors conditional on true report state. All sources observe the same reports, so they also share an unmeasured report-to-image discrepancy. We do not interpret clusters as an effective number of independent sources, nor import external co-error percentages from other versions/cohorts as if measured here.
