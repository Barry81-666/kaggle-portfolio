# Contribution and Evidence Checklist

This is the single list of information needed to extend the portfolio's claims. Unknown details are omitted from public achievement claims rather than filled with assumed responsibilities or results.

| Item | Material needed | What it would support |
| --- | --- | --- |
| Personal work on RSNA Knee and the four biomedical silver-medal competitions | A short account per competition: team name, own tasks, specific methods/code authored or changed, collaborators and a supporting commit/notebook version where available | A precise “My role” column and a substantive personal-contribution statement |
| Bacterial motor inference fork | Parent-version comparison, own changes and selected-final-submission mapping | Decide whether the archive can become a featured project |
| Cell inference fork | Confirm which observed differences in the [upstream comparison](CELL_UPSTREAM_COMPARISON.md) are personal work; identify the historical parent and final submission | Attribute changes and distinguish demonstration code from the team solution |
| RSNA Knee final results | Team name; final public/private rank, score and dated leaderboard/submission evidence | Fill the final competition result rows |
| RSNA Knee local validation | Config and checkpoint identity; fold/patient/duplicate manifest hashes; CV/OOF metrics and logs; train-only baseline values | Verify BCE, Brier and AUC on a known split |
| RSNA Knee gold evaluation | Pre-evaluation freeze receipt; metrics JSON; sample and class counts; bootstrap settings and retained replicate count; patient clustering information | Report a supported gold result with the correct uncertainty boundary |
| Image2Biomass splits | Fold-generation code and publishable summary of split membership or grouping policy | Determine what the historical random/date/species comparisons actually test |
| CIBMTR work | Existing notebook URL or local code path, data dictionary, accessible data and prior logs | Decide whether the [proposed survival analysis](CIBMTR_ANALYSIS_PLAN.md) can start |
| Private or shared work | An explicit list of files/results approved for public release, collaborator credit and any required teammate consent | Publish only agreed materials; avoid disclosing private records |

Tokens are not evidence files. Keep Kaggle credentials in local credential storage and never paste them into chat, notebook cells, commands saved in this repository or public logs. Aggregate metrics are preferable to patient-level predictions for the first evidence handoff.
