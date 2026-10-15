# A Fed repo operation is no take-up only if it is a test trade, and #743's evidence re-run (#802)

**Serves:** H3 step 1 screening (the Fed repo take-up columns; #692/#727/#743) and the inputs of H5 step 2. **Exploration on development data only:** no verdict for any
hypothesis under scoring protocol v1 (#640). No 2026 day is read (`docs/decisions/lockbox.md`), nothing is published, the columns stay off `FEATURE_FIELDS`, and no earlier
record is edited: `docs/pivot/fed-repo-floor-743-result.md` and its evidence stand, and the figures below are published anew beside them.

**The rule** (Eleonora, 15 October 2026, ruling on #802, option (b); recorded in `docs/DATA_QUALITY_DECISIONS.md`). It replaces #743's floor ("under $0.1 bn accepted is no take-up").
A Fed repo operation counts as no take-up only if it is a *test trade*:

1. an operation whose `note` names a small value exercise is dropped, as before (`ingest._is_small_value_exercise`); and
2. otherwise an operation is a test trade if it accepted more than zero and at most `ingest.TEST_TRADE_MAX` (USD 7 million) **and** a whole number of millions
   (`ingest._is_test_trade`). Every other operation counts in full.

It is judged per operation, not per day: a day with a $3 mn trade and a $9 mn trade has $9 mn of take-up. One amount, no date, so the rule builds no regime dummy (#672). The operation still happened,
so its date keeps a row, at zero. `srf_total_accepted` is not changed (#787 applies whichever rule lands).

**What the tracked snapshots hold.** No operation under $44 mn carries a test note (the 20 operations whose note names a small value exercise, repo and reverse repo, accepted $44-116 mn, and are already dropped), so
the Desk's data marks no small trade as a test; the rule above is the ruling's "otherwise" arm. Of the 1,506 kept facility-era repo operations under $0.1 bn, 360 accepted something and 314 of those are whole-million trades of $7 mn or less.
All 314 amounts are whole millions, so "round" excludes nothing in these snapshots and is a guard for later data.

**What changed in the data**, over the 1,570 facility-era operation dates: 296 dates have take-up under this rule, against 254 under #743's floor and 596 when every trade counted. 46 dates differ from the floor
(from 2019-11-05 to 2025-11-18) and 309 from the tree before #743. The dates of the finding keep their take-up (checked in `tests/test_fed_liquidity.py`):

| date | counted | $0.1 bn floor | test-trade rule |
|---|---|---|---|
| 2024-09-23 | $15 mn | 0 | $15 mn |
| 2024-09-24 | $59 mn | 0 | $57 mn |
| 2024-12-23 | $50 mn | 0 | $50 mn |
| 2025-09-10 | $12 mn | 0 | $9 mn |
| 2025-09-22 | $30 mn | 0 | $30 mn |
| 2025-10-06 | $20 mn | 0 | $20 mn |

The dates with $1 bn or more are the same set under every rule.

## 1. Ordinary-day AUROC of the take-up series, by rule

Pressure AUROC (+5 bp) on ordinary days, 90% stationary-bootstrap interval, three rules side by side (`evidence/test-trade-802/matrix-auroc.md` has all 60 cells; the first two columns are #743's, copied).

| series | lead | counted | floor $0.1 bn | test trade |
|---|---|---|---|---|
| `fed_repo_days_since_positive` | 1 | 0.64 [0.48, 0.79] | 0.50 [0.35, 0.65] | 0.60 [0.42, 0.76] |
| `fed_repo_days_since_positive` | 10 | 0.68 [0.51, 0.82] | 0.54 [0.39, 0.67] | 0.64 [0.46, 0.79] |
| `fed_repo_log_accepted` | 1 | 0.53 [0.43, 0.65] | 0.58 [0.50, 0.67] | 0.57 [0.49, 0.67] |
| `fed_repo_ops` | 1 | 0.52 [0.42, 0.62] | 0.57 [0.49, 0.66] | 0.57 [0.49, 0.66] |

Every interval contains 0.5 under the test-trade rule at lead 1 and 10 for `fed_repo_days_since_positive`; its pooled point estimate sits between the two earlier rules, so
the floor's drop to 0.50 was partly the narrower rule's own gain removed. The 2018-19 AUROC is the same under all three rules, as in #743.

## 2. The 2018 onset warnings, by arm

Onsets flagged at some lead 1 to 5 under the judge's cut-offs by `risk_logistic_base_dealer`; the passer `risk_logistic_base` flags 13 of 27 and 0 of 5 in 2018 in every arm. The "zeroed" arms set the columns to 0.0 in the scratch panel (a constant column carries nothing); they are not removed from the design.

| arm | 2018 | 2019 | 2025 | all | paired Brier vs passer, h = 1 |
|---|---|---|---|---|---|
| counted (before #743), from #743's record | 3/5 | 10/13 | 4/5 | 17/27 | +0.0022 [-0.0001, +0.0047] |
| floor $0.1 bn, from #743's record | 3/5 | 10/13 | 5/5 | 18/27 | +0.0021 [-0.0002, +0.0047] |
| **test trade (this change)** | 3/5 | 10/13 | 4/5 | 18/27 | +0.0021 [-0.0002, +0.0046] |
| test trade, `fed_repo_days_since_positive` and its `_sameday` twin zeroed | 3/5 | 10/13 | 4/5 | 17/27 | +0.0028 [+0.0002, +0.0057] |
| test trade, **all fourteen `fed_repo_*` columns zeroed** (the seven conservative columns and their `_sameday` twins) | 3/5 | 10/13 | 4/5 | 17/27 | +0.0014 [-0.0011, +0.0043] |

(The 2020 and 2024 columns are in `evidence/test-trade-802/paired-*.md`; 2024 is 1 of 2 with the narrowed rule in place and 0 of 2 in both zeroed arms.)

The 2018 gain (0 to 3 of 5) is the same with the whole Fed repo group removed, so it is carried by `dealer_treasury_position`, not by any `fed_repo_*` column: #743's reading ("the other dealer inputs carry it") is now shown, not only inferred.
The candidate is no better than its passer on Brier in any arm (the one interval that excludes zero, the column-zeroed arm, is on the wrong side, in favour of the passer). **No 2018 warning gain is claimed for the Fed repo columns**, and no verdict follows.

## Not checked, or for Eleonora

* **Marked question (hers):** the data mark no small trade as a test, so "round and at most $7 mn" is a size rule and cannot tell a test from a real $1-7 mn borrow. If the Desk ever publishes such a note, the rule should read it first. The ruling already settles the rule; this is only a reminder that it cannot be checked against the Desk's own labels.
* `srf_total_accepted` (`nyfed_srf`) is not changed; #787 applies the rule there and publishes.
* The source-matrix run used an uncommitted scratch copy of `source_matrix_629.py` with its declared-panel-hash and declared-series checks bypassed (as #727 and #743 did); the declaration is untouched. The columns are not on `FEATURE_FIELDS`.
* Only the two records #727 attributes to #662 were re-run, as in #743. One model and one passer at h = 1 to 5.

## Reproduce

Run from the repository root (`/opt/rmm-venv` or any environment with the `ml` extra for the model runs).

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
# the panel chain of scripts/unused_inputs.py: pressure_v1_1, measurement_fields, net_settlement, policy_features, fed_liquidity -> AUG5.csv; nowcast -> AUG6.csv
# arms: AUG5_col.csv sets fed_repo_days_since_positive and fed_repo_days_since_positive_sameday to 0.0; AUG5_all.csv sets every column starting fed_repo_ to 0.0
for h in 1 2 3 4 5: scripts/unused_inputs.py run --panel AUG5[_col|_all].csv --published PUB.csv --horizon $h --candidate risk_logistic_base_dealer --output u$h.json
for h in 1 2 3 4 5: scripts/unused_inputs.py run --panel AUG5.csv --published PUB.csv --horizon $h --candidate risk_logistic_base --output c$h.json
for h in 1 2 3 4 5: scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output bench_h$h.json
scripts/unused_inputs.py report --panel PUB.csv --output paired.json --markdown paired.md bench_h?.json c?.json u?.json
# source matrix: satiation_distance_598.py panel -> AUG2D.csv; source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv AUG2D.csv -> SCREEN.csv; source_matrix_629.py run
```
