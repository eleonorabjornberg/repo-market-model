# Same-day reading of SRF and Fed repo operation availability (#442, a sensitivity test of #425)

A measurement only. The published declaration of `nyfed_srf` (`metadata/sources.json`: a day's take-up is available at 16:00 ET
on the next business day) is **unchanged**, and so is `nyfed_repo_ops`; the same-day reading is a source of its own,
`nyfed_repo_ops_sameday`, off in every published declaration and live record, and no published figure moves. Changing the
declaration is Eleonora's decision, and it is asked as a separate issue ("Publish? Same-day reading of SRF availability (#442)"),
not settled here. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary and +10 bp reported, 90% stationary-bootstrap
intervals. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not looked at.

## Result: the same-day reading does not improve on the conservative one

Reading each operation date's take-up at 16:00 ET on the date itself, instead of on the next business day, does not make the Fed
liquidity inputs useful.

* **Against the conservative reading** (Table 1, the same candidate with only the availability reading changed): the Brier
  difference, same-day minus conservative, is small and changes sign across horizons and thresholds. At +5 bp no overall interval
  excludes zero for `hierarchical_logistic_srf_sameday` and only h = 1 does for `hierarchical_logistic_fed_repo_sameday`
  (-0.0010 [-0.0022, -0.0000]). At +10 bp the same-day reading is *worse* at h = 1 for the SRF candidate (+0.0023 [+0.0001, +0.0049])
  and slightly better at h = 2 (-0.0006 [-0.0015, -0.0000]). Split by regime and pressure-day type
  (`paired_sameday_minus_conservative_*.md`), cells whose interval excludes zero fall on both sides, with no regime or day type
  favoured consistently.
* **Against the control** (Table 2, `hierarchical_logistic` without the inputs): no interval excludes zero in the same-day candidates' favour;
  their Brier score is higher than the control's in most cells, and the interval excludes zero at +5 bp for h = 3 (both), h = 4
  (SRF) and h = 2 and 5 (Fed repo), as for the conservative candidates (Table 3).
* **The judge's verdicts** (Table 4): no candidate passes. Tier verdicts (1 / 3 / 5) are no / no / no for the control, both
  conservative candidates and `hierarchical_logistic_srf_sameday`. `hierarchical_logistic_fed_repo_sameday` passes tier 5 alone
  (calibrated, and ahead of climatology) and fails tiers 1 and 3; within the scarce regime alone, no candidate passes. The pass rule
  needs all three tiers. Both flag 15 of the 26 onsets, as the control does, and their worst false alarms per onset (3.85 and 4.08) are
  above the control's (3.65) and above the limit of 2.

So: the less conservative reading does not improve pressure-day prediction, and there is no case in this evidence for changing the
declaration. The question is still put to Eleonora in the "Publish?" issue, with this table.

## What was built

* **The reading** (`ingest.repo_operation_same_day_available_at`): a date is available at 16:00 ET on its operation date, unless
  its `lastUpdated` is later. A record written after that 16:00 but no later than 16:00 on the next business day is available at
  that next decision instant (the write time rounded up). A record written after that (a rewrite) stays on the conservative
  reading, at its write time: the first publication cannot be established. On the tracked snapshots exactly five operation
  dates are written after their own 16:00: 2021-12-28 (16:10), 2023-03-22 (17:22), 2023-05-11 (next day 09:29) and the rewrites of
  2021-09-03 and 2021-09-10 (both on 2021-09-16). `tests/test_fed_liquidity.py` pins them.
* **The registry** (`metadata/sources_measurement.json`, `nyfed_repo_ops_sameday`, days = 0): `nyfed_srf`'s evidence (a median 0.7
  minutes and a 99th percentile of 3.3 minutes between the close and `lastUpdated`) is in its provenance. Unlike the lag, the column
  assembly withholds the five late dates from their own day: such a row reads as zero, as a date with no operation does, so a value
  written at 16:10 is invisible to that day's 16:00 decision (`fed_liquidity.assemble(..., reading=SAME_DAY)`).
* **The columns** (`_sameday` suffix on each of #425's seven columns, `fed_liquidity.COLUMN_FIELDS_SAME_DAY`), off in every published
  declaration. A forecast of day T, decided at 16:00 on the panel day before, reads the take-up of that very day. Both guards hold
  under this reading: reading the scored day raises `LookAheadError`, and reading an older row than the latest admissible raises
  `StaleReadError` (`tests/test_fed_liquidity.py`, `SameDayAsOfTests`).
* **Two candidates** committed to `metadata/pressure_judge.json` before any score was computed (commit `a4e931e`):
  `hierarchical_logistic_srf_sameday` and `hierarchical_logistic_fed_repo_sameday`, each identical to its #425 counterpart except
  for the availability reading. The judge refuses an uncommitted declaration. Nothing was tuned on scored days.

## Reproduce

Panel `4ddc3882…`, the published panel, built and verified as in `docs/pivot/fed-liquidity-result.md`. `scripts/fed_liquidity.py panel` now
adds both sets of columns.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG.csv --output AUG_F.csv
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/b_hH.json --published
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon H --output OUT/h_hH.json
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py forecasts --panel AUG_F.csv --published PUB.csv --horizon H --output OUT/f_hH.json
```

For h = 1 to 5. The control's files name the scratch panel's digest; give them the published panel's (keeping the scratch one as
`scratch_panel_sha256`), as `fed-liquidity-result.md` does. Then:

```
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/b_h?.json OUT/h_h?.json OUT/f_h?.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py paired --panel PUB.csv --candidate-minus-control --control hierarchical_logistic_srf --only hierarchical_logistic_srf_sameday --output OUT/pc_srf.json --markdown OUT/pc_srf.md OUT/f_h?.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py paired --panel PUB.csv --candidate-minus-control --control hierarchical_logistic_fed_repo --only hierarchical_logistic_fed_repo_sameday --output OUT/pc_fed.json --markdown OUT/pc_fed.md OUT/f_h?.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py paired --panel PUB.csv --candidate-minus-control --only hierarchical_logistic_srf_sameday --only hierarchical_logistic_fed_repo_sameday --output OUT/pctl_sameday.json --markdown OUT/pctl_sameday.md OUT/h_h?.json OUT/f_h?.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py paired --panel PUB.csv --candidate-minus-control --only hierarchical_logistic_srf --only hierarchical_logistic_fed_repo --output OUT/pctl_cons.json --markdown OUT/pctl_cons.md OUT/h_h?.json OUT/f_h?.json
```

The judge's full report is `docs/pivot/evidence/fed-liquidity-sameday/judge.md`; the tier tables, `tables.md`; the paired comparisons by
regime and pressure-day type, `paired_*.md`, in the same folder. The control and the conservative candidates reproduce their rows in
`docs/pivot/evidence/fed-liquidity/`.

## Tables

Table 1. Brier score of the same-day candidate minus the conservative candidate's, paired on the same days, overall (negative:
the same-day reading is better); 90% stationary-bootstrap interval.

| candidate | threshold | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic_srf_sameday | +5 bp | -0.0007 [-0.0018, +0.0001] | -0.0008 [-0.0023, +0.0006] | +0.0007 [-0.0001, +0.0015] | +0.0001 [-0.0006, +0.0007] | +0.0004 [-0.0004, +0.0013] |
| hierarchical_logistic_srf_sameday | +10 bp | +0.0023 [+0.0001, +0.0049] | -0.0006 [-0.0015, -0.0000] | +0.0001 [-0.0003, +0.0007] | +0.0000 [-0.0001, +0.0001] | +0.0003 [+0.0000, +0.0007] |
| hierarchical_logistic_fed_repo_sameday | +5 bp | -0.0010 [-0.0022, -0.0000] | -0.0012 [-0.0029, +0.0006] | +0.0010 [-0.0000, +0.0021] | -0.0004 [-0.0014, +0.0003] | +0.0004 [-0.0007, +0.0015] |
| hierarchical_logistic_fed_repo_sameday | +10 bp | +0.0004 [-0.0004, +0.0013] | -0.0007 [-0.0017, +0.0002] | +0.0004 [-0.0004, +0.0015] | +0.0001 [-0.0001, +0.0002] | +0.0002 [-0.0002, +0.0005] |

Table 2. Brier score of the same-day candidate minus the control's (`hierarchical_logistic`), overall (negative: the candidate is better).

| candidate | threshold | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic_srf_sameday | +5 bp | +0.0008 [-0.0016, +0.0030] | +0.0024 [-0.0002, +0.0052] | +0.0037 [+0.0010, +0.0065] | +0.0030 [+0.0002, +0.0061] | +0.0023 [-0.0007, +0.0056] |
| hierarchical_logistic_srf_sameday | +10 bp | +0.0033 [+0.0005, +0.0067] | -0.0003 [-0.0014, +0.0005] | +0.0004 [-0.0008, +0.0015] | +0.0011 [-0.0001, +0.0029] | +0.0012 [+0.0000, +0.0027] |
| hierarchical_logistic_fed_repo_sameday | +5 bp | +0.0014 [-0.0012, +0.0043] | +0.0032 [+0.0004, +0.0064] | +0.0039 [+0.0014, +0.0068] | +0.0029 [-0.0004, +0.0067] | +0.0032 [+0.0002, +0.0065] |
| hierarchical_logistic_fed_repo_sameday | +10 bp | +0.0030 [+0.0003, +0.0064] | +0.0000 [-0.0013, +0.0012] | +0.0005 [-0.0004, +0.0013] | +0.0011 [-0.0002, +0.0030] | +0.0013 [+0.0001, +0.0029] |

Table 3. The same, for the conservative candidates (from #425), for reference.

| candidate | threshold | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic_srf | +5 bp | +0.0015 [-0.0005, +0.0037] | +0.0033 [+0.0010, +0.0060] | +0.0030 [+0.0009, +0.0055] | +0.0029 [+0.0001, +0.0061] | +0.0019 [-0.0006, +0.0048] |
| hierarchical_logistic_srf | +10 bp | +0.0011 [-0.0000, +0.0024] | +0.0003 [-0.0004, +0.0010] | +0.0003 [-0.0009, +0.0013] | +0.0011 [-0.0001, +0.0028] | +0.0008 [-0.0001, +0.0022] |
| hierarchical_logistic_fed_repo | +5 bp | +0.0025 [+0.0000, +0.0051] | +0.0044 [+0.0017, +0.0076] | +0.0029 [+0.0005, +0.0056] | +0.0033 [+0.0002, +0.0069] | +0.0027 [+0.0004, +0.0052] |
| hierarchical_logistic_fed_repo | +10 bp | +0.0026 [-0.0002, +0.0065] | +0.0007 [+0.0001, +0.0014] | +0.0000 [-0.0011, +0.0011] | +0.0011 [-0.0002, +0.0028] | +0.0011 [+0.0001, +0.0025] |

Table 4. Tiers and shares of the pressure days flagged. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo | 14 of 26 | 0.538 [0.368, 0.711] | 0.231 | 3.73 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo_sameday | 15 of 26 | 0.577 [0.389, 0.758] | 0.231 | 3.85 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| hierarchical_logistic_srf | 15 of 26 | 0.577 [0.389, 0.741] | 0.231 | 3.81 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_srf_sameday | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 4.08 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

## Not checked, or for Eleonora

* **Whether the declaration of `nyfed_srf` changes** is hers, and the evidence points against a change. It is the "Publish?" issue's
  question; nothing here moves a published figure.
* **The rewritten 2021-09 records.** In #425's conservative columns the two rewritten dates (2021-09-03 and 2021-09-10) sit on their
  operation date's row and are read at the declared lag, although they were rewritten on 2021-09-16. The same-day columns
  withhold them. The amounts are a few million dollars; this is a finding for #425, not changed here.
* **A withheld date reads as zero**, as a date with no operation does, and its value is not placed on a later row. Only five dates
  are affected, two with a non-zero take-up.
* **#413's classifiers are not scored** (as in #425). The near-blind and blind tiers were not scored.
