# One-step fits refuse calendar and scheduled columns (#947)

**Development data, not a verdict.** This page scores nothing. It records a guard that Eleonora approved on 19 October
2026 (relayed, on the fixed-income reviews of main at 362df84) and what it does to the committed arms. Serves H5 step 3
onward, and every fitter that trains on one-step pairs (finding #914).

## The error the guard stops

`asof` rule 2 serves a calendar column (`contract.CALENDAR_FEATURES`) and a field a source declares in
`scheduled_availability` from the scored row `T`. A one-step fitter trains row `p` against the spread of `p + 1`, so it
reads such a column from the row *before* the target and is served it on the target's own row. The flag learns the
reversal the day after the turn.

A one-step fit given such a column now raises `ValueError`, naming the column and the two fixes (direct pairs, or drop
the column). The check is `repo_model.one_step_guard.check_one_step_regressors`.

## Fitters covered

| Fitter | Covered | How |
|---|---|---|
| `baseline.fit_arx` | yes | its regressors |
| `baseline.fit_threshold` | yes | its regressors and its threshold variable (the regime is read from the origin row) |
| `ml.fit_gradient_boosted_quantiles` | yes, unless `training_pairs="direct"` | its regressors, checked by the `one_step_guard.guard_one_step_fit` decorator on the def line, so the fitter's body (which the final test's frozen declarations checksum) is unchanged (Eleonora's ruling of 20 October 2026, "move the guard") |
| `ml.fit_depth_limited_quantiles` | yes | passes through to the gradient-boosted fitter |
| `baseline.fit_rolling_residual_law` | not applicable | takes no regressors |
| `ml.fit_off_risk_day_model`, `ml.fit_censored_gpd`, `ml.fit_markov_switching`, `ml.fit_latent_factor` | not applicable | take matrices or series the caller built; they name no column. The caller that builds a one-step design from a named column is not guarded by this directive. |

## The allow-list

`one_step_guard.ONE_STEP_ALLOW_LIST` is the only exemption. An entry matches a fit by fitter and by the ordered
regressors; a test pins the exact contents. There is no switch.

| Entry | Fitter | Regressors | Why it is exempt |
|---|---|---|---|
| `published_distribution_crps` | `fit_gradient_boosted_quantiles` | the published distribution's h = 1 inputs, `treasury_settlement` among them | the final test's frozen `CRPS_COMMAND` (hashed by the pre-registration) and the live record fit it on one-step pairs; their bytes and records must reproduce |
| `gbm_funding_634` | `fit_gradient_boosted_quantiles` | the same inputs | `gbm_funding` of `metadata/spread_distribution_634.json` is the phase 2 gbm on the published features; its figures must reproduce |

Pressure model v1 fits no guarded fitter (a logistic on its own design), so it needs no entry. At h > 1 the published
declaration drops `treasury_settlement`, so the guard never meets it there.

## Committed arms the guard would now refuse

Found by running the guard over the feature lists the scripts declare; the arms were not re-run.

- `scripts/spread_distribution_634.py`, variants (a) `a_published_new` and (b) `b_gbm_new`, at every lead: their inputs
  add `tax_date` (calendar) and, at h = 1, `iorb_announced_change_bps` and `iorb_days_to_announced_change` (scheduled),
  and keep `treasury_settlement` at every lead. They train on one-step pairs, so each was fitted one row off.
- Scripts that take their feature lists from `spread_distribution_634` (`new_features`) and fit a guarded fitter
  inherit the same refusal where they pass those lists on: `h5_step3_707`, `h5_step4_758`, `h3_nested_708`,
  `h9_nested_842`, `richer_targets_706`, `backfill_h5_726` for its non-published arms, `twin_diagnosis_865` (its
  `treasury_settlement` forward read). Each needs its own run to confirm.

Committed records in `docs/runs/` and `docs/pivot/` are not edited.

**Question for Eleonora (marked; the PR does not settle it).** Does any refused arm get re-run, on direct pairs
or without the column? Re-running is a new scored experiment, so it is hers to order.
