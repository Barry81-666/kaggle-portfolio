# Decisions and amendments

| Date | Decision | Outcome exposure |
| --- | --- | --- |
| 2026-10-28 | Adopt public-only leaderboard/label SAP v1.0; supersede personal-model and Gold58-reference plans. | Public write-up aggregates and dataset schemas inspected; no empirical analysis under this SAP. |
| 2026-10-28 | Correct identification assumptions, separate selected finals from public maxima, treat external counts as versioned reports, and exclude image-derived fusion from the report-only primary cohort. | Source feasibility review only. |

## SAP v1.1 approval and freeze

The owner approved SAP commit `0c7fecb0d2fb48203097786b54063389101ee5a7` on 2026-10-28, conditional on four amendments, and explicitly authorized the first A checkpoint without merging main. These amendments were recorded before any empirical outcome analysis:

1. All selected final submissions form the primary cohort; bootstrap whole teams. Private-best selection is sensitivity only.
2. Stratify the variance benchmark using the sample-size-weighted score mean M; private-score strata are sensitivity only.
3. Interpret latent estimates as report-extraction quantities. C uses Se/Sp grids primarily; B-derived scenarios are extraction-error-only. A strict image-misclassification lower bound is not mathematically guaranteed without extra assumptions, so it is not claimed.
4. Minimum delivery is A3.1/A3.2/B4.1 and C baseline rho=0/0.2, n=58/977. Statistical computation is capped at 120 minutes, downloads at 30 active minutes. Dependent LCM and the joint stress grid are extensions.

**Outcome exposure at amendment:** public write-up aggregate claims, file schemas and synthetic software tests had been seen. No empirical leaderboard association, label agreement or latent-accuracy result had been calculated for this project. Thus “no results seen” refers to new project empirical outcomes, not to previously read public source claims.

The v1.1 freeze is the Git commit introducing this section and the matching SAP version. Its exact SHA is stored in the local approval receipt and later execution records. Main must not be merged without separate owner approval.
