# Public-source feasibility audit

Checked 2026-10-28. This document records metadata and schemas, not statistical findings. [datasets.csv](datasets.csv) pins the selected file/version for 11 screened sources; [discovery.csv](discovery.csv) contains 35 unique search hits, including weights and other ineligible assets. Thirty-five hits do not mean 35 independent label sets.

## Official metadata

[Meta Kaggle](https://www.kaggle.com/datasets/kaggle/meta-kaggle), version 2370, lists an **Apache 2.0** license. The publisher says this is a filtered/transformed snapshot, not a complete database dump. Anonymous metadata, file listing and byte-range reads succeeded. A full Competitions download timed out after a partial transfer. Competition inclusion, full-precision availability for its submissions and final leaderboard completeness remain unverified. No statistical leaderboard result has been calculated.

Submissions headers include `IsSelected`, `IsAfterDeadline`, both display scores, both full-precision scores and submission/scoring dates. Teams includes `CompetitionId`, both leaderboard submission IDs, benchmark and medal fields. Submissions has `TeamId` rather than `CompetitionId`; an out-of-memory-safe scan must join through Teams. These verified headers support a feasible acquisition plan but do not establish valid row coverage.

An anonymous competition-list API request returned 401. No credentials were supplied and no competition files were requested. If public metadata cannot establish coverage, follow the fallback in the SAP rather than accessing personal submission records.

## Requested label sources

| Source | License shown by publisher | Schema/decision |
| --- | --- | --- |
| [Dread](https://www.kaggle.com/datasets/dreaddevelopment/rsna-knee-labels), v3 | CC0 | 4,349 rows; ID + 12 scores. Original extraction; author describes Gold58 exclusion. Primary candidate. |
| [JEV](https://www.kaggle.com/datasets/riadmohamed42/jev-knee-labels), v5 | CC0 | Selected score file: 4,407 rows; ID + 12 scores. Shared Steven/Pilkwang ancestry and expert-panel tuning; secondary. Expert evaluation files in the release are not used. |
| [flight](https://www.kaggle.com/datasets/flight0234/rsna-knee-hybrid-report-labels), v1 | CC0 | 4,407 rows; 12 scores + 12 confidence fields + ID. Steven v4 with a Pilkwang fracture substitution chosen using expert-panel performance. Secondary. |
| [Steven](https://www.kaggle.com/datasets/stevenleehans/rsna-knee-llm-report-labels), v6 | CC0 | Original full file: 4,407 rows; ID + 12 scores. v2/v4 are separate, derived versions; do not count them as independent raters. |
| [Pilkwang](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels), v1 | CC0 | 4,406 rows; ID, 12 scores, confidence and verdict fields. Scores are not guaranteed calibrated probabilities. Primary candidate. |
| [11-label fusion](https://www.kaggle.com/datasets/omerzalman/rsna-knee-11-label-evidence-fusion), v2 | CC BY-NC 4.0 | Publisher reports 4,407 studies and 11 findings; Synovitis absent. Its attribution file describes text sources, MRI readers and expert-panel development. Excluded from report-only primary analysis; label values were not downloaded for this audit. |

Additional schema-checked CC0 sources are Yunus's report extraction and Lixin's GPT extraction (each 4,407 rows, ID + 12 scores), a four-source merge and a consensus release. The latter two are derivative comparisons. Qwen is a candidate with CC0 metadata but its file/schema eligibility has not yet been checked. See the manifest for exact URLs and versions.

The audit inspected row/column counts, public descriptions and attribution. It did **not** calculate prevalence, agreement, sensitivity/specificity, Gold58 comparisons or leaderboard associations. Label raw files acquired during earlier source exploration remain outside the repository; this study will use only the new manifest's allowed files. Earlier expert-label proposals and materials are excluded.

## File and ancestry controls

Download only an approved label CSV, never the complete archive. Never download `train.csv`, expert-label evaluation sets, `study_metadata.csv`, report-review files, weights or image predictions. Check the selected CSV against the allowed score/confidence/verdict schema before retaining it. A missing finding is missing, not negative.

No raw tables are redistributed. Dataset authors are credited as sources, not evaluated as teams. Source-level license declarations are recorded; a derivative source is not proof of independent evidence or of downstream permission for every unrelated file in its archive.

## External numerical evidence

The [pinned public write-up](https://github.com/TaeyanG4/rsna-knee-abnormality-detection/blob/3f79eae93147c303f788e07144f590ace092edb0/README.md) supplies aggregate claims and source ancestry. It updates preliminary leaderboard counts on 2026-10-28; both versions are retained in parameters.csv with verification flags. We do not use that team's personal submission ledger or copy its training code.

[RSNA's announcement](https://www.rsna.org/news/2026/august/ai-challenge-knee-mri) provides official challenge context. [This independent public repository](https://github.com/homeshwarnelakurthi/RSNA-Knee-Abnormality-Detection) reports a random/grouped validation difference; this is an external claim, not a replicated finding. Neither published agreement percentages nor a single source's validation difference determines latent sensitivity/specificity.

No third-party code is vendored. The R foundation in this project is newly written; the methods are attributed in the SAP. Unverified counts or source summaries are not presented as this project's results.
