# The OFR cleared-repo series on the days the government is closed (#1016)

**Serves:** H3 (new public data adds signal), step 1 (the segment screen), as a correction to the availability declaration of #968 (finding #1003). Development data, never a verdict (scoring protocol v1). No published declaration, panel, record or figure changes.

## Answer

**Nothing in the screen's verdict changes, and the lookahead is closed.** `ofr_stfm_repo_cleared` counted its one-day lag on the panel's rows, which are SOFR publication days. The OFR "do[es] not publish" releases "on government holidays" and publishes the affected days' data "on the next day the government is open" (its data-release page, quoted in `metadata/sources_measurement.json`). On the three statutory holidays the market opened (`statutory_days_the_market_opened` in `metadata/market_holidays.json`: 2021-06-18, 2021-12-31, 2023-11-10), the decision read the value dated the day before at 15:00 on the holiday, up to three days before the OFR published it. It now reads the value before that.

* **The screen.** Only the two `_1d` columns that hold a value on those days move, and only in the fourth decimal: the DVP rate minus BGCR at lead 1 goes from +0.1767 (panel rows) to +0.1768, and keeps rank 20 of 62; the DVP rate from +0.0155 to +0.0155; the GCF rate does not move. Every other series is identical to the screen of #968, to the last digit.
* **The paired test of #187** for `ofr_dvp_minus_bgcr_bp`, re-run on the same days under the corrected dating: **no effect**, as at the declared lag and at #968's panel-row reading. No paired Brier mean differs from #968's one-day reading by more than 0.000007, none changes sign, and none moves an interval's lower bound across zero. The CRPS difference at h = 1 is +0.0101 bp [-0.0044, +0.0243] in both.
* **Kill (#1016 criterion 4): no change in the screen's verdict.**

Whether any OFR series joins a published declaration is Eleonora's decision, and this page does not ask it.

## What changed

* `repo_model.government_calendar`: `government_open_dating()` counts the business-day lag of a source whose registry entry sets `government_open_days_only` on panel rows the government is open, from the statutory rows already in `metadata/market_holidays.json` (`basis: statute`, and `statutory_days_the_market_opened`); no new calendar source. `asof.py` is frozen by the final-test pre-registration, so the rule is swapped for the length of a run, as `h41_release.release_dating()` does, and restored on the way out. A source that does not opt in is dated by the original function.
* `metadata/sources_measurement.json`: `ofr_stfm_repo_cleared` sets `government_open_days_only`, and its `availability_provenance` note no longer says the holiday rule "is covered by counting business days". The source stays off in every published declaration; `ofr_stfm_repo` and `ofr_stfm_repo_segments` and the frozen `metadata/sources.json` are unchanged, so every record already scored reads what it read.
* `tests/test_government_calendar.py`: the decision on the three days does not see the previous day's value; the guard raises `LookAheadError` on the value the unadjusted rule reads; an ordinary day, an executive-order closure and a source that does not opt in read as before; the swap is undone after a raise. One recorded mutation.
* `scripts/source_screen.py` and `scripts/dvp_segment_inputs.py` take `--government-open-days`; `scripts/ofr_cleared_lag_968.py compare` takes it too (it counts, instead of requiring, the identity "a copy at lead L is the original at lead L - 1", which no longer holds on the days after those holidays); `scripts/ofr_cleared_holidays_1016.py` sets the three readings beside each other.

## Marked question for Eleonora (#1016, criterion 3)

The executive-order closures that were market days (2020-12-24, 2024-12-24, 2025-01-09, 2025-12-24, 2025-12-26) are **not** counted as government holidays: the table lists statutes, and whether the OFR treats a closure by executive order as a "government holiday" is a data meaning. A test (`test_an_executive_order_closure_is_not_counted`) pins that they read as before. If she rules they count, they are added to the set `government_closed_days()` reads, with a source for each date.

## The three readings

Both lags are read in the scratch panel of #968 (sha256 `f46cfc571940…`, 2,042 scored days from 2018-06-29 to 2026-09-03) and the paired test on `dvp_segment_inputs.py`'s scoring panel (sha256 `608f872d…`, to 2025-12-31), with #968's runs, folds, seeds and bootstrap; only the dating of the cleared source differs. The Holm correction runs over the corrected reading's own 41 comparisons, as in #968, so the outcomes compare with #968's and not with #187's. The declared and panel-row columns are read from `docs/research/ofr-cleared-lag-968/`.

### Screen: pooled Spearman correlation at lead 1, and rank at the strongest lead

| series | declared (2 days) | panel rows (#968) | government-open days (#1016) | rank, declared / #968 / #1016 |
|---|---|---|---|---|
| `ofr_dvp_minus_bgcr_bp` | +0.1751 | +0.1767 | +0.1768 | 16 of 62 / 20 of 62 / 20 of 62 |
| `ofr_dvp_rate` | +0.0163 | +0.0155 | +0.0155 | 49 of 62 / 48 of 62 / 48 of 62 |
| `ofr_gcf_rate` | -0.0590 | -0.0781 | -0.0781 | 37 of 62 / 36 of 62 / 36 of 62 |

### Paired test (#187) for `ofr_dvp_minus_bgcr_bp`: Brier difference, benchmark minus candidate, and one-sided p

| day set | h | comparison | declared (2 days) | panel rows (#968) | government-open days (#1016) |
|---|---|---|---|---|---|
| all_days | 1 | +5.0 bp vs pressure_model_v1 | -0.0001 [-0.0004, +0.0001]; p 0.7693 | -0.0002 [-0.0005, -0.0000]; p 0.9204 | -0.0002 [-0.0005, -0.0000]; p 0.9204 |
| all_days | 1 | +5.0 bp vs persistence_logistic | -0.0025 [-0.0058, +0.0002]; p 0.9080 | -0.0026 [-0.0059, +0.0003]; p 0.9150 | -0.0026 [-0.0059, +0.0003]; p 0.9150 |
| all_days | 1 | +10.0 bp vs pressure_model_v1 | -0.0000 [-0.0002, +0.0001]; p 0.6551 | -0.0001 [-0.0003, +0.0001]; p 0.7447 | -0.0001 [-0.0003, +0.0001]; p 0.7447 |
| all_days | 1 | +10.0 bp vs persistence_logistic | +0.0002 [-0.0010, +0.0016]; p 0.3713 | +0.0002 [-0.0011, +0.0015]; p 0.3866 | +0.0002 [-0.0011, +0.0015]; p 0.3866 |
| all_days | 2 | +5.0 bp vs pressure_model_v1 | +0.0003 [+0.0000, +0.0007]; p 0.0797 | +0.0003 [+0.0000, +0.0007]; p 0.0783 | +0.0003 [+0.0000, +0.0007]; p 0.0783 |
| all_days | 2 | +5.0 bp vs persistence_logistic | +0.0003 [-0.0030, +0.0036]; p 0.4391 | +0.0003 [-0.0030, +0.0034]; p 0.4403 | +0.0003 [-0.0030, +0.0034]; p 0.4403 |
| all_days | 2 | +10.0 bp vs pressure_model_v1 | +0.0004 [+0.0001, +0.0009]; p 0.0473 | +0.0004 [+0.0001, +0.0009]; p 0.0481 | +0.0004 [+0.0001, +0.0009]; p 0.0481 |
| all_days | 2 | +10.0 bp vs persistence_logistic | +0.0011 [+0.0002, +0.0021]; p 0.0485 | +0.0010 [+0.0002, +0.0021]; p 0.0502 | +0.0010 [+0.0002, +0.0021]; p 0.0502 |
| all_days | 3 | +5.0 bp vs pressure_model_v1 | +0.0004 [+0.0001, +0.0007]; p 0.0350 | +0.0004 [+0.0001, +0.0007]; p 0.0384 | +0.0004 [+0.0001, +0.0007]; p 0.0384 |
| all_days | 3 | +5.0 bp vs persistence_logistic | +0.0020 [-0.0010, +0.0056]; p 0.1418 | +0.0020 [-0.0010, +0.0054]; p 0.1440 | +0.0020 [-0.0010, +0.0054]; p 0.1440 |
| all_days | 3 | +10.0 bp vs pressure_model_v1 | +0.0002 [+0.0000, +0.0004]; p 0.0822 | +0.0002 [-0.0000, +0.0006]; p 0.0929 | +0.0002 [-0.0000, +0.0006]; p 0.0929 |
| all_days | 3 | +10.0 bp vs persistence_logistic | +0.0011 [+0.0002, +0.0021]; p 0.0517 | +0.0011 [+0.0002, +0.0023]; p 0.0486 | +0.0011 [+0.0002, +0.0023]; p 0.0486 |
| all_days | 4 | +5.0 bp vs pressure_model_v1 | +0.0003 [+0.0001, +0.0006]; p 0.0532 | +0.0003 [+0.0001, +0.0006]; p 0.0525 | +0.0003 [+0.0001, +0.0006]; p 0.0525 |
| all_days | 4 | +5.0 bp vs persistence_logistic | +0.0022 [-0.0003, +0.0052]; p 0.1045 | +0.0022 [-0.0004, +0.0053]; p 0.1050 | +0.0022 [-0.0004, +0.0053]; p 0.1050 |
| all_days | 4 | +10.0 bp vs pressure_model_v1 | +0.0000 [-0.0000, +0.0001]; p 0.2223 | +0.0000 [-0.0001, +0.0001]; p 0.3765 | +0.0000 [-0.0001, +0.0001]; p 0.3765 |
| all_days | 4 | +10.0 bp vs persistence_logistic | +0.0012 [+0.0003, +0.0023]; p 0.0449 | +0.0012 [+0.0003, +0.0022]; p 0.0463 | +0.0012 [+0.0003, +0.0022]; p 0.0463 |
| all_days | 5 | +5.0 bp vs pressure_model_v1 | +0.0005 [+0.0001, +0.0009]; p 0.0490 | +0.0005 [+0.0001, +0.0009]; p 0.0506 | +0.0005 [+0.0001, +0.0009]; p 0.0506 |
| all_days | 5 | +5.0 bp vs persistence_logistic | +0.0013 [-0.0008, +0.0038]; p 0.1786 | +0.0013 [-0.0008, +0.0041]; p 0.1785 | +0.0013 [-0.0008, +0.0041]; p 0.1785 |
| all_days | 5 | +10.0 bp vs pressure_model_v1 | +0.0000 [-0.0000, +0.0001]; p 0.1678 | +0.0000 [-0.0000, +0.0001]; p 0.1660 | +0.0000 [-0.0000, +0.0001]; p 0.1660 |
| all_days | 5 | +10.0 bp vs persistence_logistic | +0.0015 [+0.0002, +0.0034]; p 0.0805 | +0.0015 [+0.0002, +0.0033]; p 0.0802 | +0.0015 [+0.0002, +0.0033]; p 0.0802 |
| onset_days | 1 | +5.0 bp vs pressure_model_v1 | -0.0000 [-0.0002, +0.0001]; p 0.7692 | -0.0001 [-0.0002, +0.0000]; p 0.9015 | -0.0001 [-0.0002, +0.0000]; p 0.9015 |
| onset_days | 1 | +5.0 bp vs persistence_logistic | -0.0007 [-0.0018, +0.0003]; p 0.8646 | -0.0007 [-0.0018, +0.0002]; p 0.8768 | -0.0007 [-0.0018, +0.0002]; p 0.8768 |
| onset_days | 1 | +10.0 bp vs pressure_model_v1 | -0.0000 [-0.0001, +0.0000]; p 0.8658 | -0.0001 [-0.0001, -0.0000]; p 0.9615 | -0.0001 [-0.0001, -0.0000]; p 0.9615 |
| onset_days | 1 | +10.0 bp vs persistence_logistic | -0.0000 [-0.0002, +0.0002]; p 0.5251 | -0.0000 [-0.0002, +0.0002]; p 0.6240 | -0.0000 [-0.0002, +0.0002]; p 0.6240 |
| onset_days | 2 | +5.0 bp vs pressure_model_v1 | +0.0001 [-0.0001, +0.0005]; p 0.2208 | +0.0001 [-0.0001, +0.0005]; p 0.2113 | +0.0001 [-0.0001, +0.0005]; p 0.2113 |
| onset_days | 2 | +5.0 bp vs persistence_logistic | +0.0007 [-0.0006, +0.0021]; p 0.2063 | +0.0007 [-0.0006, +0.0021]; p 0.2031 | +0.0007 [-0.0006, +0.0021]; p 0.2031 |
| onset_days | 2 | +10.0 bp vs pressure_model_v1 | -0.0000 [-0.0001, +0.0000]; p 0.8256 | -0.0000 [-0.0001, +0.0001]; p 0.7263 | -0.0000 [-0.0001, +0.0001]; p 0.7263 |
| onset_days | 2 | +10.0 bp vs persistence_logistic | +0.0002 [-0.0001, +0.0006]; p 0.1440 | +0.0002 [-0.0001, +0.0006]; p 0.1477 | +0.0002 [-0.0001, +0.0006]; p 0.1477 |
| onset_days | 3 | +5.0 bp vs pressure_model_v1 | +0.0001 [+0.0000, +0.0002]; p 0.0879 | +0.0001 [-0.0000, +0.0002]; p 0.1110 | +0.0001 [-0.0000, +0.0002]; p 0.1110 |
| onset_days | 3 | +5.0 bp vs persistence_logistic | +0.0023 [-0.0000, +0.0051]; p 0.0938 | +0.0023 [-0.0000, +0.0051]; p 0.0957 | +0.0023 [-0.0000, +0.0051]; p 0.0957 |
| onset_days | 3 | +10.0 bp vs pressure_model_v1 | -0.0000 [-0.0001, +0.0000]; p 0.8975 | -0.0001 [-0.0002, -0.0000]; p 0.9062 | -0.0001 [-0.0002, -0.0000]; p 0.9062 |
| onset_days | 3 | +10.0 bp vs persistence_logistic | +0.0006 [-0.0000, +0.0014]; p 0.0920 | +0.0006 [-0.0000, +0.0014]; p 0.0953 | +0.0006 [-0.0000, +0.0014]; p 0.0953 |
| onset_days | 4 | +5.0 bp vs pressure_model_v1 | +0.0001 [-0.0000, +0.0003]; p 0.1209 | +0.0001 [-0.0000, +0.0002]; p 0.1595 | +0.0001 [-0.0000, +0.0002]; p 0.1595 |
| onset_days | 4 | +5.0 bp vs persistence_logistic | +0.0023 [-0.0000, +0.0053]; p 0.0937 | +0.0023 [-0.0000, +0.0053]; p 0.0954 | +0.0023 [-0.0000, +0.0053]; p 0.0954 |
| onset_days | 4 | +10.0 bp vs pressure_model_v1 | -0.0000 [-0.0000, +0.0000]; p 0.6157 | -0.0000 [-0.0001, +0.0000]; p 0.7493 | -0.0000 [-0.0001, +0.0000]; p 0.7493 |
| onset_days | 4 | +10.0 bp vs persistence_logistic | +0.0007 [-0.0000, +0.0016]; p 0.0993 | +0.0007 [-0.0000, +0.0016]; p 0.1012 | +0.0007 [-0.0000, +0.0016]; p 0.1012 |
| onset_days | 5 | +5.0 bp vs pressure_model_v1 | +0.0002 [+0.0000, +0.0005]; p 0.0829 | +0.0002 [+0.0000, +0.0005]; p 0.0824 | +0.0002 [+0.0000, +0.0005]; p 0.0824 |
| onset_days | 5 | +5.0 bp vs persistence_logistic | +0.0018 [-0.0000, +0.0044]; p 0.0992 | +0.0019 [+0.0000, +0.0044]; p 0.0992 | +0.0019 [+0.0000, +0.0044]; p 0.0992 |
| onset_days | 5 | +10.0 bp vs pressure_model_v1 | +0.0000 [+0.0000, +0.0001]; p 0.0668 | +0.0000 [+0.0000, +0.0001]; p 0.0794 | +0.0000 [+0.0000, +0.0001]; p 0.0794 |
| onset_days | 5 | +10.0 bp vs persistence_logistic | +0.0013 [+0.0001, +0.0032]; p 0.1106 | +0.0013 [+0.0000, +0.0032]; p 0.1113 | +0.0013 [+0.0000, +0.0032]; p 0.1113 |

### CRPS, horizon 1: control minus candidate, bp

| reading | CRPS candidate | difference | p improve |
|---|---|---|---|
| declared (2 days) | 1.0672 | +0.0103 [-0.0031, +0.0242] | 0.1006 |
| panel rows (#968) | 1.0674 | +0.0101 [-0.0044, +0.0243] | 0.1189 |
| government-open days (#1016) | 1.0674 | +0.0101 [-0.0044, +0.0243] | 0.1191 |

### The win rule (#187), as `dvp_segment.classify` reads it

| reading | outcome | +5 bp | +10 bp |
|---|---|---|---|
| declared (2 days) | **no effect** | no effect; survives at h=– | no effect; survives at h=– |
| panel rows (#968) | **no effect** | no effect; survives at h=– | no effect; survives at h=– |
| government-open days (#1016) | **no effect** | no effect; survives at h=– | no effect; survives at h=– |

Evidence: `docs/research/ofr-cleared-holidays-1016/` (`screen_compare.json` every compared cell, `gbm.json` every paired comparison of the corrected reading).

## Not checked, or for Eleonora

* **The executive-order closures** (above).
* **Whether the cleared columns replace the two-day ones in the records**, as on the page of #968: unchanged, hers.
* **Values dated before a holiday's own release.** The rule counts the first government-open panel row. A day on which the government is open and the market is closed (Good Friday) is not a panel row, so a value waits for the next market day there; that is the safe side and was the rule before.
* **The 15:00 instant is the page's statement, not a measured first print**, as for #968.
* **Not re-run:** the matrix of #629 (its panel no longer rebuilds on main, as #968 noted) and #187's own family.

## Reproduce

The panels are built as in `docs/research/ofr-cleared-lag-968.md` (`PUB.csv` `4ddc3882…`; `SCREEN.csv` `f46cfc57…`; `DVP25.csv` `608f872d…`). Then:

```
PYTHONPATH=src python3 scripts/source_screen.py --government-open-days run --panel SCREEN.csv --output OUT/screen.json
PYTHONPATH=src python3 scripts/ofr_cleared_lag_968.py compare OUT/screen.json --government-open-days --output OUT/screen_compare.json --markdown OUT/screen_compare.md
for H in 1 2 3 4 5; do for RUN in control@ofr persistence_logistic@ofr ofr_dvp_minus_bgcr_bp@1d; do
  PYTHONPATH=src python3 scripts/dvp_segment_inputs.py --government-open-days run --panel DVP25.csv --run $RUN --horizon $H --output OUT/runs/${RUN}_h$H.pickle; done; done
for H in 1 2 3 4 5; do PYTHONPATH=src python3 scripts/dvp_segment_inputs.py --government-open-days pair --panel DVP25.csv --runs OUT/runs --run ofr_dvp_minus_bgcr_bp@1d --horizon $H; done
PYTHONPATH=src python3 scripts/dvp_segment_inputs.py --government-open-days crps --panel DVP25.csv --run ofr_dvp_minus_bgcr_bp@1d --output OUT/runs/crps_ofr_dvp_minus_bgcr_bp@1d.json
PYTHONPATH=src python3 scripts/ofr_cleared_holidays_1016.py gbm --runs OUT/runs --output OUT/gbm.json     # needs the ml extra
PYTHONPATH=src python3 scripts/ofr_cleared_holidays_1016.py page --screen OUT/screen_compare.json --gbm OUT/gbm.json --output OUT/tables.md
```

The screen takes half a minute; each run of the paired test about a minute, the whole set under half an hour.

## Note (#1071): the `crps` command above no longer runs on main, and the figures are provisional

**Development data, not a verdict; nothing above is edited.** The distribution side of #187's test (the `crps` command in "Reproduce", and the table "CRPS, horizon 1" above) fits both arms of `compare --loss crps` on one-step pairs. Both arms read `treasury_settlement`, a scheduled field served from the target row, so it was learned one row off at lead 1 (class b of the [provisional register](provisional-calendar-register.md); this page's result (#1035) and #968's (#988) are both listed there). Since the one-step guard (#947) the command is refused: the candidate arm's regressors are not on the allow-list, and it exits with `fit_gradient_boosted_quantiles trains on one-step pairs ... 'treasury_settlement' ... is served from the scored row itself`. The figure above stays as published, one-step and provisional.

The working replacement on main runs both arms on direct pairs, so the control is the published features fitted on direct pairs and the difference measures the added column and not a change of pairing:

```
PYTHONPATH=src python3 scripts/dvp_segment_inputs.py --government-open-days crps --panel DVP25.csv --run ofr_dvp_minus_bgcr_bp@1d --training-pairs direct --output OUT/runs/crps_ofr_dvp_minus_bgcr_bp@1d.json
```

(`--training-pairs` applies to both arms; `cli compare` refuses a nested comparison whose arms name different pairings.) On the same panel (`DVP25.csv` `608f872d…`), the CRPS difference at h = 1, control minus candidate, over 1263 origins, is +0.0158 bp (90% stationary-bootstrap interval [+0.0037, +0.0276]; CRPS 1.1547 control, 1.1388 candidate), against +0.0101 bp [-0.0044, +0.0243] on one-step pairs above. By day type the means are +0.0111 ordinary (1074 days), +0.0332 month-end, +0.0366 tax dates and +0.1083 quarter-end (21 days, interval [-0.1205, +0.4046]); by regime, +0.0026 in 2021-23 and +0.0671 in 2025-26 (interval [+0.0233, +0.1141]). The direct-pairs figure is a development figure on the sample the page already used; it is not a confirmation, and what it means for the screen's verdict is not settled here. The other commands of "Reproduce" (the paired Brier runs and the `gbm` step) were not re-run for this note.
