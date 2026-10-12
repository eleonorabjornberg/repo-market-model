# Always-flag reading of tier 1 (#588): summary

Tier 1 re-scored under the judge in force (false alarms pooled across horizons since the rulings of 10 October 2026) with and
without `Declaration.always_flag_not_warning`, on 2018-06-29 to 2025-12-31. Tables, per-lead figures, always-flag blocks per row
and horizon and the onsets lost are in `result.md` (weighted rule in force, then the flat count). Command: the header of
`scripts/always_flag_588.py`.

Under the weighted rule in force, with the option on: `risk_gbm+settle+h41` and `risk_gbm` are unchanged and pass;
`risk_gbm+every_day+gate+settle+h41+iorb` is unchanged and fails (3.46 false alarms per onset, over the limit of 2);
`ngboost_laplace` falls from 17 of 26 to 13 of 26 warned (recall 0.500, on the bar) and its false alarms from 2.34 to 1.81, so it
moves from a fail to a pass. Under the flat count it fails either way.
