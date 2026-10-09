# Fed repo operations and Standing Repo Facility take-up as inputs (#425, track F of #374)

A scratch measurement under the pressure-day judge (`metadata/pressure_judge.json`, as amended under #407): does the Fed's
use of its own repo facilities warn of pressure? It writes nothing into `docs/runs/` and moves no published figure, declaration
or live record. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary and +10 bp reported, 90% stationary-bootstrap
intervals. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not looked at.

## Result: the inputs do not help, and the classifier does not pass with them

Adding the Standing Repo Facility's take-up and the Desk's repo operations to the best classifier of #406 (the hierarchical
logistic, `hierarchical_logistic`) makes it **slightly worse, not better**, at every horizon: its Brier score is higher
than the same classifier's without them, with an interval that excludes zero at +5 bp for h = 2 to 4 (Table 4), and its AUROC
at +5 bp falls from 0.880 to 0.843 (h = 1) and from 0.847 to 0.783 (h = 2) (Table 5). Neither candidate passes the judge's bar
(tier 1: at most two false alarms per onset; tier 3: calibration in the regimes that had pressure; tier 5), neither passes
within the scarce regime alone, and neither beats persistence-logistic on the Brier score at +5 bp at any horizon with an interval
that excludes zero (Table 5). The control, the classifier without the inputs, reproduces its row in
`docs/pivot/judge-amendment-result.md` (15 of 26 onsets flagged, 3.65 worst false alarms per onset).

A descriptive look agrees with the model fits and is not a test: on days two panel days after a day with a non-zero take-up,
a day above +5 bp followed in 49 of 598 cases (8.2%) against 91 of 1,275 (7.1%) after a day without. The difference is in the
2025-26 regime alone (22 of 132 against 7 of 117); in 2018-19 the rates are the same (20 of 74 and 82 of 301), and 2021-23
has no pressure day at all.

## What was built

* **A source of its own, `nyfed_repo_ops`** (`src/repo_model/ingest.py`, declared in `metadata/sources_measurement.json`,
  not in `metadata/sources.json`, which the final-test pre-registration freezes by its bytes): the New York Fed's repo
  operation results, markets.newyorkfed.org, one unmodified yearly response for 2018 to 2025, saved with checksums in
  `tests/fixtures/snapshots/repo_ops_inputs/`:
  `PYTHONPATH=src python3 -m repo_model.cli fetch repo-ops --output-root tests/fixtures/snapshots/repo_ops_inputs --start 2018-01-01 --end 2025-12-31`.
  It covers the temporary operations of 2019 and 2020 and the Standing Repo Facility from 2021-07-29, overnight and term.
* **Publication time.** The Desk states no clock time; the one timestamp in each record is `lastUpdated`, a write time. The
  adapter records it per operation date (the latest of the date's operations, New York time) and reads the date's values at the
  later of that and the registry's declaration (16:00 ET on the next business day, as `nyfed_srf` declares). A rewritten record
  is therefore read after its rewrite: two dates, 2021-09-03 and 2021-09-10, were rewritten on 2021-09-16. For every other date
  the declaration is the later instant. The as-of rule reads the declaration, so a value published after the decision instant
  is invisible and the guard is `LookAheadError` (`tests/test_fed_liquidity.py`).
* **The columns** (`src/repo_model/fed_liquidity.py`, off in every published declaration): `fed_repo_log_accepted`
  (`ln(1 + USD billions accepted)`), its change from the previous panel row, `fed_repo_days_since_positive` (panel rows since a
  non-zero take-up, capped at 250), and for the wider candidate the amount submitted, the amount-weighted rate accepted minus
  IORB (bp) and the number of operations that accepted anything. A date with no operation is read as zero take-up.
* **Candidates** (declared in `metadata/pressure_judge.json` and committed before any was scored): `hierarchical_logistic_srf`
  (the directive's three inputs added to the hierarchical logistic) and `hierarchical_logistic_fed_repo` (those and the
  amount submitted, the rate and the count). The control is the unchanged `hierarchical_logistic`.

## Reproduce

Panel `4ddc3882…`, the published panel. The columns are added to the scratch panel of `pressure_v1_1.py panel`, the one the control is scored on.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG.csv --output AUG_F.csv
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/b_hH.json --published
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon H --output OUT/h_hH.json
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py forecasts --panel AUG_F.csv --published PUB.csv --horizon H --output OUT/f_hH.json
```

For h = 1 to 5. The control's files name the scratch panel's digest; give them the published panel's (`panel_sha256`, keeping
the scratch one as `scratch_panel_sha256`) after checking that their dates are the grid's, as `judge-amendment-result.md` does.

```
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/b_h?.json OUT/h_h?.json OUT/f_h?.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/fed_liquidity.py paired --panel PUB.csv --output OUT/paired.json --markdown OUT/paired.md OUT/h_h?.json OUT/f_h?.json
```

The judge's full report is `docs/pivot/evidence/fed-liquidity/judge.md`; the tables, `tables.md`; the paired comparison with the
control by regime and pressure-day type, `paired.md`.

## Tables

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo | 14 of 26 | 0.538 [0.368, 0.711] | 0.231 | 3.73 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_srf | 15 of 26 | 0.577 [0.389, 0.741] | 0.231 | 3.81 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_fed_repo | 0.60 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.48 (101) | 0.56 (9) | 0.62 (13) |
| hierarchical_logistic_srf | 0.53 (102) | 0.00 (4) | – | 0.00 (5) | 0.41 (29) | 0.59 (17) | 0.43 (101) | 0.56 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| hierarchical_logistic_fed_repo | +0.0190 [-0.0015, +0.0425] | +0.0186 [+0.0094, +0.0270] | +0.0130 [+0.0114, +0.0146] | +0.0015 [-0.0032, +0.0052] | +0.0322 [+0.0077, +0.0625] | +0.0332 [+0.0139, +0.0543] | +0.0108 [+0.0057, +0.0168] | +0.0896 [+0.0290, +0.1456] | +0.0545 [+0.0341, +0.0760] |
| hierarchical_logistic_srf | +0.0212 [+0.0016, +0.0433] | +0.0180 [+0.0084, +0.0260] | +0.0131 [+0.0114, +0.0148] | +0.0015 [-0.0030, +0.0052] | +0.0366 [+0.0081, +0.0709] | +0.0356 [+0.0132, +0.0600] | +0.0116 [+0.0059, +0.0178] | +0.0952 [+0.0340, +0.1534] | +0.0534 [+0.0312, +0.0756] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |


Table: Brier score against the two benchmarks, +5 bp (positive: better than the benchmark; paired, 90% stationary-bootstrap interval)

| model | benchmark | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic | calendar climatology | +0.0184 [+0.0114, +0.0260] | +0.0121 [+0.0066, +0.0178] | +0.0100 [+0.0053, +0.0146] | +0.0105 [+0.0057, +0.0154] | +0.0101 [+0.0050, +0.0151] |
| hierarchical_logistic | persistence-logistic | +0.0034 [-0.0007, +0.0073] | +0.0021 [-0.0016, +0.0061] | +0.0037 [-0.0001, +0.0076] | +0.0020 [-0.0023, +0.0062] | +0.0026 [-0.0020, +0.0071] |
| hierarchical_logistic_srf | calendar climatology | +0.0169 [+0.0108, +0.0238] | +0.0088 [+0.0041, +0.0140] | +0.0070 [+0.0028, +0.0110] | +0.0076 [+0.0035, +0.0117] | +0.0082 [+0.0036, +0.0131] |
| hierarchical_logistic_srf | persistence-logistic | +0.0018 [-0.0014, +0.0050] | -0.0012 [-0.0044, +0.0020] | +0.0007 [-0.0025, +0.0040] | -0.0009 [-0.0043, +0.0026] | +0.0007 [-0.0032, +0.0046] |
| hierarchical_logistic_fed_repo | calendar climatology | +0.0160 [+0.0107, +0.0222] | +0.0077 [+0.0032, +0.0126] | +0.0072 [+0.0027, +0.0117] | +0.0071 [+0.0028, +0.0117] | +0.0074 [+0.0028, +0.0119] |
| hierarchical_logistic_fed_repo | persistence-logistic | +0.0009 [-0.0022, +0.0039] | -0.0023 [-0.0054, +0.0008] | +0.0008 [-0.0026, +0.0044] | -0.0013 [-0.0047, +0.0024] | -0.0001 [-0.0040, +0.0038] |

Table: Brier score against the two benchmarks, +10 bp (positive: better than the benchmark; paired, 90% stationary-bootstrap interval)

| model | benchmark | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic | calendar climatology | +0.0060 [+0.0033, +0.0091] | +0.0018 [-0.0011, +0.0041] | +0.0024 [+0.0007, +0.0041] | +0.0033 [+0.0014, +0.0052] | +0.0036 [+0.0016, +0.0056] |
| hierarchical_logistic | persistence-logistic | +0.0028 [+0.0001, +0.0055] | +0.0017 [-0.0001, +0.0036] | +0.0018 [-0.0001, +0.0037] | +0.0011 [-0.0009, +0.0030] | +0.0015 [-0.0001, +0.0032] |
| hierarchical_logistic_srf | calendar climatology | +0.0050 [+0.0024, +0.0078] | +0.0016 [-0.0011, +0.0038] | +0.0022 [+0.0002, +0.0041] | +0.0022 [+0.0005, +0.0038] | +0.0027 [+0.0007, +0.0046] |
| hierarchical_logistic_srf | persistence-logistic | +0.0018 [-0.0006, +0.0042] | +0.0014 [-0.0002, +0.0032] | +0.0015 [+0.0002, +0.0031] | -0.0000 [-0.0018, +0.0018] | +0.0007 [-0.0010, +0.0024] |
| hierarchical_logistic_fed_repo | calendar climatology | +0.0034 [+0.0003, +0.0061] | +0.0012 [-0.0016, +0.0035] | +0.0024 [+0.0004, +0.0045] | +0.0022 [+0.0005, +0.0041] | +0.0025 [+0.0006, +0.0043] |
| hierarchical_logistic_fed_repo | persistence-logistic | +0.0002 [-0.0024, +0.0025] | +0.0010 [-0.0005, +0.0027] | +0.0018 [+0.0003, +0.0035] | +0.0000 [-0.0019, +0.0020] | +0.0005 [-0.0010, +0.0021] |

Table: AUROC and average precision, +5 bp

| model | AUROC h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | average precision h = 1 |
|---|---|---|---|---|---|---|
| hierarchical_logistic | 0.880 | 0.847 | 0.834 | 0.833 | 0.827 | 0.438 |
| hierarchical_logistic_srf | 0.843 | 0.783 | 0.766 | 0.762 | 0.772 | 0.427 |
| hierarchical_logistic_fed_repo | 0.835 | 0.763 | 0.762 | 0.753 | 0.757 | 0.408 |


Table 4. Brier score of the control minus the candidate's, paired on the same days (positive: the candidate is better),
overall; 90% stationary-bootstrap interval. By regime and pressure-day type: `docs/pivot/evidence/fed-liquidity/paired.md`.

| candidate | threshold | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| hierarchical_logistic_srf | +5 bp | -0.0015 [-0.0037, +0.0005] | -0.0033 [-0.0060, -0.0010] | -0.0030 [-0.0055, -0.0009] | -0.0029 [-0.0061, -0.0001] | -0.0019 [-0.0048, +0.0006] |
| hierarchical_logistic_fed_repo | +5 bp | -0.0025 [-0.0051, -0.0000] | -0.0044 [-0.0076, -0.0017] | -0.0029 [-0.0056, -0.0005] | -0.0033 [-0.0069, -0.0002] | -0.0027 [-0.0052, -0.0004] |
| hierarchical_logistic_srf | +10 bp | -0.0011 [-0.0024, +0.0000] | -0.0003 [-0.0010, +0.0004] | -0.0003 [-0.0013, +0.0009] | -0.0011 [-0.0028, +0.0001] | -0.0008 [-0.0022, +0.0001] |
| hierarchical_logistic_fed_repo | +10 bp | -0.0026 [-0.0065, +0.0002] | -0.0007 [-0.0014, -0.0001] | -0.0000 [-0.0011, +0.0011] | -0.0011 [-0.0028, +0.0002] | -0.0011 [-0.0025, -0.0001] |

## Not checked, or for Eleonora

* **The classifiers of #413 are not scored.** The directive names the best classifiers of #406 and #413. #413 (the quantile
  regression forest and natural-gradient boosting) is not merged, and its branch conflicts with main, so only #406's classifier
  is here. Its `qrf` and `ngboost_laplace` rows in `judge-amendment-result.md` flag 12 and 15 of the 26 onsets; adding these inputs to them is
  one more declaration once #413 is on main.
* **Whether the inputs join a published declaration** is a question for her; they stay off, and the evidence above is the
  separate "Publish?" issue's table.
* **The non-zero days include the Desk's operational tests** of 2018 and 2019 (about 65 million dollars each, announced by
  operating-policy notices and not called small-value exercises in the record's note), and the facility's few small
  takings of 2021 and 2022. They count as non-zero for `fed_repo_days_since_positive`, as `early_warning`'s
  `srf_take_up_positive` does. Log amounts keep them small.
* **A date with no operation is read as zero**, a measurement choice declared in `fed_liquidity`; the registry's structural-zero
  review is still open (`structural_zeros_reviewed`).
* **The 2019-2020 temporary operations are not the facility.** They answer a market that was short of reserves; the facility
  answers a repo rate above its minimum bid rate. The same column means different things in different regimes, and the
  hierarchical logistic does not give the inputs a per-regime effect.
* **No comparison scored a locked day;** the confirmation window and the blind tier were not looked at.
