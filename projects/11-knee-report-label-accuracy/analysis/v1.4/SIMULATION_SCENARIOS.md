# Frozen simulation scenarios (SAP v1.4)

All scenarios are repeated for each of twelve findings. See [SAP-v1.4.md](SAP-v1.4.md) for the data generator and estimands. The labels retain the empirical five-source-complete joint pattern distribution; latent truth and score-error inheritance are assumptions.

| Scenario | AUC A | AUC B | Inheritance variance | A inherits | Truth weight G1 | Truth slope | Prevalence multiplier | Replicates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| equal_true_auc | 0.85 | 0.85 | 0.5 | G1 | 0.5 | 4 | 1 | 2000 |
| A_better | 0.86 | 0.85 | 0.5 | G1 | 0.5 | 4 | 1 | 2000 |
| B_better | 0.85 | 0.86 | 0.5 | G1 | 0.5 | 4 | 1 | 2000 |
| no_inheritance | 0.85 | 0.85 | 0 | G1 | 0.5 | 4 | 1 | 1000 |
| weak_inheritance | 0.85 | 0.85 | 0.25 | G1 | 0.5 | 4 | 1 | 1000 |
| strong_inheritance | 0.85 | 0.85 | 0.75 | G1 | 0.5 | 4 | 1 | 1000 |
| swap_training_groups | 0.85 | 0.85 | 0.5 | G2 | 0.5 | 4 | 1 | 1000 |
| truth_favors_group1 | 0.85 | 0.85 | 0.5 | G1 | 0.75 | 4 | 1 | 1000 |
| truth_favors_group2 | 0.85 | 0.85 | 0.5 | G1 | 0.25 | 4 | 1 | 1000 |
| weak_truth_alignment | 0.85 | 0.85 | 0.5 | G1 | 0.5 | 2 | 1 | 1000 |
| strong_truth_alignment | 0.85 | 0.85 | 0.5 | G1 | 0.5 | 8 | 1 | 1000 |
| lower_prevalence | 0.85 | 0.85 | 0.5 | G1 | 0.5 | 4 | 0.5 | 1000 |
| higher_prevalence | 0.85 | 0.85 | 0.5 | G1 | 0.5 | 4 | 1.5 | 1000 |

G1 is Steven/Pilkwang/Lixin; G2 is Dread/Yunus. The first three rows are primary scenarios within this exploratory extension; remaining rows are prespecified sensitivities. Equal true AUC has no worse model, so its endpoint is directional selection preference, not misselection.
