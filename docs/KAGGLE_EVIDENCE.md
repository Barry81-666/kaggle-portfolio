# Read-Only Kaggle Evidence Retrieval

Public original-source downloads worked during this revision, and all ten version hashes matched the prior archive. No local Kaggle credential was available. The authenticated leaderboard/list endpoints returned an authentication failure; other attempted output routes returned generic HTML rather than an output listing. Final RSNA team standings and output files therefore remain unverified.

## Retrieve Only the Needed Evidence

Use a locally authenticated [official Kaggle CLI](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md), from a working directory **outside this repository**. Do not put a token on the command line or paste it into chat. These commands list or download only; they do not submit a competition entry or publish a notebook.

```bash
mkdir -p evidence-review/rsna-knee
kaggle kernels list --mine --competition rsna-knee-abnormality-detection --page-size 100 --csv
kaggle kernels files handudu/rsna-knee-teacher-probs-exp017-v1-infer --csv
kaggle kernels pull handudu/rsna-knee-teacher-probs-exp017-v1-infer -p evidence-review/rsna-knee -m
```

The unversioned commands above inspect the latest accessible version. Record its version number before downloading outputs. The CLI's trailing `/NUMBER` is the notebook's **ordinal version number**, not the global version ID `358098927`. Use the matching ordinal version obtained from Kaggle; do not guess one. For example, set the value below from the verified version history, then list and download only the required output names:

```bash
read -r rsna_version_number
kaggle kernels files "handudu/rsna-knee-teacher-probs-exp017-v1-infer/${rsna_version_number}" --csv
kaggle kernels output "handudu/rsna-knee-teacher-probs-exp017-v1-infer/${rsna_version_number}" -p evidence-review/rsna-knee --file-pattern '.*(metrics|evaluation|freeze|manifest).*\.json$'
```

Review the file list first. The output command can also retrieve the run log, and matching files may contain study identifiers. Keep raw downloads local until their contents and release permissions have been checked. An inference notebook may have no local training/CV/gold metrics; in that case those records must come from the actual training environment.

The exact public source used here can be downloaded without selecting a newer version:

```bash
curl --fail --location --output evidence-review/rsna-knee/inference.py 'https://www.kaggle.com/kernels/scriptcontent/358098927/download'
shasum -a 256 evidence-review/rsna-knee/inference.py
```

Expected SHA-256: `a2c1689549f01c5fa791608edd6d9db5764e66603426495e04c1fe924ce2fb32`. The [catalog](../meta/catalog.json) gives corresponding exact version IDs and hashes for the other nine sources; those downloads and the Image2Biomass/RNA output extraction are already complete.

## Locate CIBMTR Work Without Publishing It

```bash
kaggle kernels list --mine --competition equity-post-HCT-survival-predictions --page-size 100 --csv
```

Continue with subsequent pages if the result fills a page. Initially share only candidate titles, URLs, version identities and the permission status, not private source or patient data. Obtain teammate agreement for shared materials before any public commit. Final RSNA public/private rank and score also need the team identity and dated leaderboard/submission evidence; source-code availability alone does not verify them.

[Consolidated evidence checklist](CONTRIBUTIONS_AND_EVIDENCE.md)
