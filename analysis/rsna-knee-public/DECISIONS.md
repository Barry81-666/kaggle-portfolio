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

## Execution after the v1.1 freeze

- SAP v1.1 freeze: `074d903aebfcef77bb7418e270380a9b693cc70d`.
- 2026-10-28: owner chose in-place extraction in a private Kaggle R notebook. The new extractor retains all submissions, excludes names/user IDs and records dataset version/checksums. No notebook was created, published or modified by this assistant.
- 2026-10-28 14:46:50–14:48:07 UTC: completed the synthetic A3.2 reference (16 scenarios × 2,000 replicates; 1.29 minutes). No real leaderboard observations had been analyzed. T3 currently has no observed variance or excess-variance ratio; F2 contains only the sampling reference. This is a staged deliverable, not a substitution for empirical T1/T2/F1.
- Remaining cumulative statistical-computation budget: approximately 118.71 minutes. Data transfers were stopped after timeouts and an HTTP 401 from the anonymous leaderboard download; full-table acquisition is superseded by the owner's in-place extraction.

## SAP v1.2: owner-directed B/C focus

Before any B or C outcomes, the owner instructed that label evaluation and misclassification become the main project, and that empirical A be dropped because little A work had been done. The completed A sampling reference is retained only as a supplement. The owner no longer needs to produce the four Meta Kaggle files.

The SAP records source-specific abstention rules (including Yunus's unmentioned 0.05), a complete-case estimand for the independent latent model, native-R Gibbs computation with explicit orientation constraints, and the exact C minimum simulation/interval design. These choices were frozen before the first B/C analysis; source descriptions, schemas and A simulations had already been inspected.
