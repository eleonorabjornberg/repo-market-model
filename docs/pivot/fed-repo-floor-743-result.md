# One take-up floor for the Fed repo columns, and #727 re-run (#743)

**Serves:** H3 step 1 screening (#692/#727) and the inputs of H5 step 2. **Exploration on development data only:** no verdict for any
hypothesis under scoring protocol v1 (#640). No 2026 day is read (`docs/decisions/lockbox.md`), nothing is published, the columns stay
off `FEATURE_FIELDS`, and no earlier record is edited: the figures below are published anew and supersede #727's where they differ.

**The rule** (Eleonora, 14 October 2026, ruling on #743; recorded in `docs/DATA_QUALITY_DECISIONS.md`). In every era a Fed repo
operation with less than $0.1 bn accepted counts as no take-up (`ingest.REPO_TAKE_UP_FLOOR`). It covers the six test operations of $64-66 mn before the
facility and the $1-7 mn trades after it. The operation still happened, so its date keeps a row at zero take-up.

**What changed in the data.** On the scratch panel 350 rows differ in `fed_repo_accepted`, from 2019-11-05 to 2025-12-24 (the trades after the
facility began), none before 2019-09-17, and `fed_repo_submitted` is unchanged. `fed_repo_days_since_positive` now rises to its cap
in the quiet years instead of staying low, as #743 predicted.

## 1. The ordinary-day AUROC gain of `fed_repo_days_since_positive` is gone

Pressure AUROC (+5 bp) on ordinary days, pooled, 90% stationary-bootstrap interval (full table with the 2018-19 and 2025-26 splits and the
other four take-up series: `evidence/fed-repo-floor-743/matrix-auroc.md`). `main` is the tree before this change, which reproduces #727's figures.

| series | lead | main | floor |
|---|---|---|---|
| `fed_repo_days_since_positive` | 1 | 0.64 [0.48, 0.79] | 0.50 [0.35, 0.65] |
| `fed_repo_days_since_positive` | 10 | 0.68 [0.51, 0.82] | 0.54 [0.39, 0.67] |
| `fed_repo_days_since_positive_sameday` | 1 | 0.63 [0.46, 0.79] | 0.50 [0.34, 0.64] |
| `fed_repo_days_since_positive_sameday` | 10 | 0.67 [0.50, 0.82] | 0.53 [0.38, 0.66] |

Every interval now contains 0.5. In 2018-19 (62 of the 82 ordinary-day pressure days) the AUROC is the same under both trees (0.49 to 0.53),
so the pooled gain came from the 2021-25 rows, not from 2018. Only the twelve `fed_repo_*` series change; the other 89 of the 101 series
are identical.

## 2. The 2018 warnings of `risk_logistic_base_dealer` do not rest on this column

Onsets flagged at some lead 1 to 5 under the judge's cut-offs, with the same passer `risk_logistic_base` (13 of 27, 0 of 5 in 2018, in all three).
`evidence/fed-repo-floor-743/paired-*.md` hold the paired Brier differences and the onset tables.

| arm | 2018 | 2019 | 2025 | all |
|---|---|---|---|---|
| `main` (the $1-7 mn trades counted) | 3/5 | 10/13 | 4/5 | 17/27 |
| floor | 3/5 | 10/13 | 5/5 | 18/27 |
| floor, `fed_repo_days_since_positive` (and `_sameday`) set to 0 | 3/5 | 10/13 | 5/5 | 18/27 |

The 2018 gain (0 to 3 of 5) is the same with the column present or removed, so the explanation in #743 (a regime dummy giving the first 2018
warnings) is not supported for this model: the other dealer inputs carry it. The paired Brier difference against the passer at h = 1 is
+0.0021 [-0.0002, +0.0047] with the floor (main +0.0022 [-0.0001, +0.0047]; column removed +0.0029 [+0.0002, +0.0058]): the candidate is no
better than its passer on Brier in any arm. The 2025 change from 4 to 5 of 5 is one onset and is not claimed.

**No 2018 warning gain is claimed** (acceptance criterion 4); this table says the gain exists with or without the column and that it
is not attributable to it.

## Not checked, or for Eleonora

* `srf_total_accepted` (`nyfed_srf`, the Standing Repo Facility total) still counts the small trades: the results page reads it, so
  changing it moves a published figure. Whether the floor applies to it is a question for her (a "Publish?" issue is opened).
* Only the two records #727 attributes to #662 were re-run (the source matrix and `risk_logistic_base_dealer`). The other records
  #727 lists read the same columns and were not re-run.
* One model (`risk_logistic_base_dealer`) and one passer at h = 1 to 5; the other eighteen candidates of the unused-inputs record were not
  re-fitted.
* "Without the column" sets `fed_repo_days_since_positive` and its `_sameday` twin to 0; the other six `fed_repo_*` columns stay.
* The scratch run of `source_matrix_629.py` bypassed its declared-panel-sha256 check (as #727 did), in an uncommitted copy; the declaration
  is untouched.

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
# panel chain of scripts/unused_inputs.py (pressure_v1_1, measurement_fields, net_settlement, fed_liquidity, policy_features) -> AUG5.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/unused_inputs.py run --panel AUG5.csv --published PUBLISHED.csv --horizon $h --candidate risk_logistic_base_dealer --output u$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/unused_inputs.py run --panel AUG5.csv --published PUBLISHED.csv --horizon $h --candidate risk_logistic_base --output c$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output bench_h$h.json
PYTHONPATH=src python3 scripts/unused_inputs.py report --panel PUBLISHED.csv --output paired.json --markdown paired.md bench_h?.json c?.json u?.json
# source matrix: the page's chain (docs/pivot/source-matrix-ordinary-days-result.md) with satiation_distance_598.py panel -> AUG2D.csv, then source_matrix_629.py run
```
"main" is the same commands on the tree before this change (`git stash` the change, or check out its parent).
