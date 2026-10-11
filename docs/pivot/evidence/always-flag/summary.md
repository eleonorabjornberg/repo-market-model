# Always-flag reading of tier 1 (#588): summary

Tier 1 re-scored under the judge in force with and without `Declaration.always_flag_not_warning`, on 2018-06-29 to
2025-12-31. Tables, per-lead figures, always-flag blocks per row and horizon and the onsets lost are in `result.md`
(weighted rule in force, then the flat count). Command: the header of `scripts/always_flag_588.py`.

Under the weighted rule in force, all three frozen candidates and `risk_gbm` still pass tier 1 with the option on. Two of the three
frozen candidates and `risk_gbm` are unchanged (no always-flag block carries an onset for them). `ngboost_laplace` falls from 17 of
26 to 13 of 26 (recall 0.500, at the limit) and its worst false alarms from 1.73 to 1.04. Under the flat count it fails tier 1
either way.
