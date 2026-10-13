# #610's rows rebuilt on the release-dated distance columns (#658)

Serves H5 input hygiene (exploration on development data only: scoring protocol v1 is not yet in force, #640; nothing here is a verdict for any
hypothesis). A measurement only: nothing is published, no day after 2025-12-31 is scored (`require_unlocked`), no rule changes. Dated 13 October 2026.

[`tailcap-floor-result.md`](tailcap-floor-result.md) (#610, PR #612) was scored before #623 (PR #647) made the satiation-distance columns read
reserves per H.4.1 release (#622). #623 re-scored #598's rows; #610's rows were not rebuilt because #612 was not on main. This page rebuilds them on
main at `fb9192d`. The earlier page and its evidence folders are not edited; the re-scored evidence is in
[`evidence/tailcap-floor-rebuild-658/`](evidence/tailcap-floor-rebuild-658/).

## Verdicts that change

**None**, under the judge in force (weighted rule, with the flat rule beside it), for any of the five rows of #610's summary table.

| row | rule | before: tier 1 pooled (limit 2) | after | tier 1 | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | flat | 15 of 26, 0.577 [0.400, 0.762], 1.85 | 15 of 26, 0.577 [0.400, 0.762], 1.81 | yes, unchanged | no, unchanged | no, unchanged | no |
| `risk_gbm+settle+h41+dist_roll` | weighted | 15 of 26, 0.577 [0.400, 0.762], 1.27 | 15 of 26, 0.577 [0.400, 0.762], 1.17 | yes, unchanged | no, unchanged | no, unchanged | no |
| `+tailcap75`, `+floor`, `+state_floor`, `+recent_floor` (both rules) | | as on the earlier page | identical | unchanged | unchanged | unchanged | no |

What moves is the comparator, `risk_gbm+settle+h41+dist_roll`, and with it every number that is paired against it:

- Tier 1 at leads 3 to 5, pooled false alarms per onset: flat 1.35 to 1.54, weighted 0.87 to 0.96 (onsets flagged unchanged, 12 of 26).
- Predicted against realised rate, 2018-19 (realised minus predicted): +0.1793 [+0.1046, +0.2532] to +0.1819 [+0.1076, +0.2560]; 2025-26:
  +0.0684 [+0.0051, +0.1500] to +0.0703 [+0.0063, +0.1522]. Week-ahead window (tier 5): +0.0617 [+0.0342, +0.0931] to +0.0647 [+0.0366, +0.0960].
- Paired Brier against `dist_roll`, all days, weighted (positive favours the row): `+tailcap75` +0.0002 [-0.0013, +0.0018] to +0.0004 [-0.0014, +0.0023];
  (a) `+floor` +0.0010 [-0.0036, +0.0065] to +0.0013 [-0.0036, +0.0069]; (b) `+state_floor` +0.0017 [-0.0031, +0.0073] to +0.0019 [-0.0030, +0.0077];
  (c) `+recent_floor` +0.0069 [-0.0007, +0.0153] to +0.0072 [-0.0006, +0.0157]. Every interval still includes zero; the by-regime and by-day-type
  cells moved by up to 0.01 (2025-26 against (a): +0.0054 [-0.0006, +0.0122] to +0.0082 [+0.0020, +0.0154], so that cell's interval now excludes zero).
- Onsets kept and lost against `dist_roll`: unchanged, 18 against 15 (`onsets-weighted.json` is byte-identical to the earlier one).

The rows of #610 themselves (`+tailcap75` and the three floors) are byte-identical in every table of the judge's report, so the earlier page's
conclusion stands: no variant passes. The reason is that they do not read the distance columns; only the comparator does. Because the judge's
report lists all candidates, the sections of `dist_roll`, `hinge_roll` and `base_hinge_roll` also differ from the earlier file, as #623's page shows.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG`, `AUG2` and `AUG2D` rebuilt from the tracked fixtures with the
commands in the docstring of [`scripts/satiation_distance_598.py`](../../scripts/satiation_distance_598.py); `/opt/rmm-venv`,
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. Forecasts for h = 1 to 5: `pressure_judge.py forecasts`, `risk_date_severity.py run`,
`pressure_track_q.py forecasts`, `announcement_dating_rescore.py run --arm both` for `risk_gbm` and `risk_gbm_base`, `satiation_587.py merge` and
`reference`, `satiation_distance_598.py run`, `iorb_every_day_579.py run`, `every_day_conditioning_601.py cap`, then `tailcap_floor_610.py run --cap`,
the judge under both rules, `compare --reference tailcap|distroll`, `pg onsets`, `pg summary` and `calibration`, as in the docstring of
[`scripts/tailcap_floor_610.py`](../../scripts/tailcap_floor_610.py), with the three corrections below.

## Not checked, or for Eleonora

- Whether any variant replaces a shortlist slot (#567) is hers. Nothing here is a confirmation and no input joins a published declaration, so no
  "Publish?" issue is raised.
- Step 1 (`diagnose`, the 2018-19 shortfall of `+tailcap75`) was not re-run: it reads the cap row's forecasts, which this rebuild leaves unchanged
  (the row is identical in every judge table), and not the distance columns.
- Findings in the docstring of `scripts/tailcap_floor_610.py` (not changed here): `run` needs `--cap OUT/cap_h$h.json` (the docstring omits it); the
  judge command names `OUT/bench_h?.json` twice (once alone and once in `$IN`), which the judge refuses; `diagnose` has no `--bench` option.
- Other pages that compare against `dist_roll` and were scored before #623 (for example the `every-day-conditioning` evidence of #601) carry the
  same stale comparator; they are for their own re-scores.
