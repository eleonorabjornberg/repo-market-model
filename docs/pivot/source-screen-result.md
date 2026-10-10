# Screen of every data source against the spread and pressure days (#478)

An exploratory measurement for #473 and #477, not a record and not a model: nothing is selected, no model changes, no published
figure moves, and nothing is written into `docs/runs/`. No comparison scores a locked day (`docs/decisions/lockbox.md`): the screen
reads days from 2018-06-29 to 2025-12-31 only, its script refuses a panel that runs past 2025-12-31, and the confirmation window
is not looked at. Every series is read as of each decision instant under `docs/decisions/information-set.md`, with the as-of rule's
own reads (`repo_model.asof.InformationRule`), never at the row it sits on.

**Caution: this is a screen across many series, so every correlation here is exploratory.** The pooled table is 77 series
(the 76 series the panels carry that the as-of rule can read, and the spread's own as-of lag) at 5 leads against 3 targets: 1,155
correlations. Each is also split into 3 regimes and 8 years, and the pre-onset comparison adds a further 77 contrasts split the same
way. No correction for the number of tests is applied, no interval is drawn, and nothing here is a result in the sense of
`CLAUDE.md` (paired, bootstrapped, split by regime and day type). A series that ranks high is a candidate for the paired test
that #473 and #477 would run, not evidence that it carries signal.

## Method, in short

* **Days.** The 1,873 scored days of the published fold grid, 2018-06-29 to 2025-12-31, of which 140 are above +5 bp (strictly,
  on whole basis points) and 27 open an episode (`repo_model.pressure.onsets`). The same days at every lead.
* **Leads.** 1, 2, 3, 5 and 10 panel days: the as-of rule's `horizon`, the decision being made that many panel days before the scored
  day. A lead of 1 is the rule every published record was scored under (decision on the last panel day before the scored day, the
  NY Fed's daily rates then read two panel days back). Series announced for the scored day itself (the Treasury settlements, the
  announced IORB change) are public at a lead of 1 only; at longer leads they are holes, counted in `screen.json` under
  `not_public_at_lead`, not leaks.
* **Targets.** The spread level; the change in the spread over the scored day (at a lead of 1 the next-day change after the decision);
  the +5 bp pressure indicator. Spearman correlation, left empty (`-`) when a cell has under 30 days, under 3 pressure days, or a
  constant side.
* **Pre-onset window.** The series read at a lead of 1 on the 1 to 5 panel days before each of the 27 onsets (130 scored days),
  against every other scored day: the two means, the difference in units of the other days' standard deviation, and the AUC.
* **Regime.** The as-of reserve-scarcity state (`repo_model.scarcity`), at the same lead: ample (0 and 1) on 1,359 days, scarce (2 and
  3) on 514, no day without a reading.
* **Two screens on which nothing is drawn.** The five tier-1 passers are `risk_gbm`, `risk_gbm_base`, `risk_logistic`,
  `risk_logistic_base` and `risk_quantile_skewt_base` (`docs/pivot/weighted-miss-result.md`, Table 1, tier 1 under the unweighted rule;
  their inputs are `metadata/risk_date_severity.json`). A series is marked as used by a passer when that declaration names it.

## What the screen shows

The numbers are in `docs/pivot/evidence/source-screen/tables.md`; the heatmap, series by lead, is `heatmap.svg` there and every
cell is in `screen.json`. Table 1 gives the top of the ranking.

Table 1. Spearman correlation with the +5 bp pressure indicator, pooled, the 12 series with the largest absolute value over leads 1 to 10.

| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | days at lead 1 | used by tier-1 passers |
|---|---|---|---|---|---|---|---|
| `sofr_p75_iorb_bps` | +0.395 | +0.385 | +0.379 | +0.374 | +0.381 | 1871 | `risk_gbm`, `risk_logistic` |
| `spread_bps` | +0.393 | +0.379 | +0.370 | +0.368 | +0.380 | 1873 | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| `sofr_p99_iorb_bps` | +0.392 | +0.371 | +0.367 | +0.360 | +0.370 | 1873 | `risk_gbm`, `risk_logistic` |
| `policy_reserve_management_in_force` | -0.359 | -0.364 | -0.368 | -0.377 | -0.389 | 1873 | no |
| `ofr_gcf_rate` | -0.291 | -0.315 | -0.326 | -0.386 | -0.305 | 144 | no |
| `reserve_scarcity_state` | +0.365 | +0.365 | +0.365 | +0.364 | +0.363 | 1873 | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| `sofr_above_effr_share_20` | +0.355 | +0.351 | +0.348 | +0.340 | +0.320 | 1873 | no |
| `spread_nowcast_bps` | +0.351 | +0.340 | +0.319 | +0.320 | +0.341 | 1873 | no |
| `reserve_balances` | -0.348 | -0.347 | -0.347 | -0.345 | -0.340 | 1873 | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| `sofr_p99_iorb_sd15_bps` | +0.316 | +0.301 | +0.296 | +0.311 | +0.283 | 1873 | no |
| `on_rrp_below_100bn` | +0.301 | +0.305 | +0.305 | +0.305 | +0.301 | 1873 | no |
| `on_rrp` | -0.233 | -0.241 | -0.247 | -0.227 | -0.231 | 1873 | `risk_gbm`, `risk_logistic` |


## Findings

1. **The strongest correlates of a pressure day are the spread's own recent history.** The spread's as-of lag, and SOFR's 75th and 99th
   percentiles above IORB, correlate +0.36 to +0.40 with the pressure indicator at every lead, and barely decay from 1 to 10 days
   (the spread's lag: +0.39, +0.38, +0.37, +0.37, +0.38). That is persistence of a state, not information that arrives early. Any
   other series has to be read against it (the persistence benchmark of `CLAUDE.md`), not against zero.
2. **The slow regime series carry signal pooled and none inside a regime.** The reserve-scarcity state, reserves, ON RRP and the policy
   indicators correlate 0.23 to 0.39 with the pressure indicator, equally at every lead. Inside the ample regime no series exceeds
   0.24 in absolute value (the best, `quarter_end` at lead 10, rests on 7 pressure days); inside the scarce regime only the spread's own
   distribution measures exceed 0.4. The pre-onset comparison says the same: `reserve_scarcity_state` is +1.47 standard deviations
   higher before onsets than on other days (AUC 0.83) pooled, and 0.00 (AUC 0.50) inside the scarce regime, where 114 of the 130
   pre-onset days fall. The pooled figure is the regime itself, which the tier-1 passers already use.
3. **Series the tier-1 passers do not use that rank high** are either functions of what they use or are thin. `on_rrp_below_100bn`
   is a threshold of `on_rrp`; `spread_nowcast_bps` and `sofr_p99_iorb_sd15_bps` are built from the spread and SOFR's percentiles;
   `policy_reserve_management_in_force` is an indicator that switches on once, on 2019-10-15, and stays on, so it tracks the era; `ofr_gcf_rate` has
   values on only 144 scored days (2020-10-23 to 2025-12-24) and ranks fifth on that. `sofr_above_effr_share_20` (+0.35 at lead 1) is the one
   such series that holds a little inside the regimes (+0.11 inside ample on 6 pressure days, +0.25 inside scarce; +2.1 standard
   deviations before the onsets inside ample, on 16 days); it is a function of SOFR and EFFR over 20 days, not a new source.
4. **Raw rate levels are not stress signals.** Inside the scarce regime `sofr_p99`, `sofr_p1`, `bgcr` and `tgcr` rank 4 to 8 (+0.36 to
   +0.37 at lead 10); their level follows the policy rate path, which is why the same columns are near 0 pooled. The screen does not
   difference them.
5. **Nothing reads the next-day change.** Among series read as observed, the largest absolute correlation with the day's change is
   0.15 (`ofr_gcf_rate`, on 144 days) and, on all days, 0.14 (SOFR's 99th percentile above IORB, negative: a high
   reading is followed by a smaller change). The larger ones are series known in advance for the scored day (the Treasury settlements,
   0.20 to 0.32, and `days_to_month_end`, 0.17), at a lead of 1 only for the settlements. The spread level correlates 0.6 to 0.9 with the
   slow series because the level is itself the regime (Table `Against the spread` in `tables.md`).
6. **The years carry unequal weight.** 89 of the 140 pressure days are in 2019 and 29 in 2025; 2018 has 13, 2020 has 4, 2024 has 5 and
   2021 to 2023 have none, so those cells are empty. In 2018, 2020 and 2024 the strongest series differ from year to year
   (`policy_days_until_effective` and `bank_total_assets` in 2018; `iorb_announced_change_bps` in 2020; `on_rrp_below_100bn` and
   `quarter_end` in 2024, +0.44 each at 5 pressure days), none holds in more than one of the three, and each rests on 4 to 13 pressure
   days: they are anecdotes about a few episodes.

## What this does and does not support

It supports the plain reading that the tier-1 passers' inputs already include the series the screen finds strongest, and that
the pooled signal of the rest sits in the regime. It does not show that any series is a leading indicator: there is no paired test,
no interval and no correction for 1,155 correlations, the pooled correlations of trending series are confounded by the era, and the
episode count (27) is small. It selects nothing; #473 and #477 take it as a map of where to look.

## Inventory: every snapshot, and what could be read

Every directory under `tests/fixtures/snapshots/` is accounted for (`tests/test_source_screen.py` refuses a new one that is not).

**Read as a daily (or forward-filled) series as of its publication time:**

| snapshot | series |
|---|---|
| `dts_inputs` | tga_daily, the daily Treasury General Account balance, and its change |
| `fed-iorb-announcements` | iorb_announced_change_bps, iorb_days_to_announced_change |
| `fr2004` | dealer_treasury_position (FR 2004 weekly) |
| `funding_inputs` | NY Fed SOFR/TGCR/BGCR rates and volumes, FRED H.4.1 weeklies (reserves, TGA), Treasury bills and settlement: the published panel's columns |
| `h8_inputs` | bank_total_assets and reserve_scarcity_state (H.8 first prints) |
| `net_settlement_inputs` | net settlement columns (net_settlement, net_settlement_bills, net_settlement_due_5d) |
| `nyfed-rrp-results` | the Desk's ON RRP operation results the on_rrp column is built from |
| `nyfed_effr_inputs` | effr |
| `ofr_inputs` | OFR repo segment rates (ofr_tri_rate, ofr_gcf_rate, ofr_dvp_rate) and the DVP-segment columns |
| `on_rrp_inputs` | on_rrp, the Desk's ON RRP operation results |
| `repo_ops_inputs` | the Desk's repo operations (fed_repo_* columns, both availability readings) |
| `srf_inputs` | srf_take_up, the standing repo facility take-up |
| `treasury_auctions` | gross settlement columns of the published panel (treasury_settlement*) |
| `treasury_bills` | Treasury bill rates (tbill_4w, tbill_13w), by year |

**Cannot be read, and why:**

| snapshot | why |
|---|---|
| `alfred-dff` | ALFRED vintage pulls at three dates, kept to study revisions: not a daily series with a first print per day |
| `alfred-dff-first-print` | ALFRED pulls at five dates, kept to study first prints: not a daily series |
| `alfred-h41-first-print` | ALFRED first-print pulls around three dates: a revision study, not a daily series |
| `alfred-ioer` | ALFRED vintage pulls at three dates: IORB/IOER is read from the NY Fed and the announcements table |
| `alfred-rrpontsyd` | ALFRED vintage pulls at dated vintages: on_rrp is read from the Desk's results |
| `alfred-wlrrafoial` | ALFRED vintage pulls (H.4.1 reverse repos, foreign official): a revision study, no daily first prints |
| `alfred-wlrral` | ALFRED vintage pulls (H.4.1 reverse repos): a revision study, no daily first prints |
| `alfred-wlrraol` | ALFRED vintage pulls (H.4.1 reverse repos, other): a revision study, no daily first prints |
| `alfred-wresbal` | ALFRED vintage pulls: reserve_balances is read from the FRED latest-vintage snapshot under the registry's declared lag |
| `alfred-wtregen` | ALFRED vintage pulls at four dates: tga is read from the FRED latest-vintage snapshot under the registry's declared lag |
| `frb_ddp` | the Board's H.15 and PRATES SDMX files, read only by repo_model.effr_history for the pre-SOFR study; EFFR and IOER are already read from the NY Fed and FRED, and the primary credit rate is a step series set by the policy register |
| `nyfed-primary-dealer` | a hand-downloaded 'latest' CSV with no recorded retrieval time (its manifest says 'None'): the as-of rule cannot say when any row was public; its weekly positions are the FR 2004's, already read |
| `treasury_bill_rates_page` | the Treasury text-view page as served: evidence for #445 (its 3:30 pm quote time), not a data input; no series is built from it |

**Columns of the scratch panels that were not screened:** `nowcast_naive`, `nowcast_published_only`, `nowcast_rrp`, `nowcast_rrp_settlement`, `nowcast_rrp_settlement_calendar`, `nowcast_settlement`. They are the nowcast module's intermediate variants (for
example the settlement-only and the reverse-repo-only nowcasts); `repo_model.nowcast` declares one column, `spread_nowcast_bps`,
and the as-of rule refuses the others for having no declared availability (`UndeclaredFeatureError`, in `screen.json` under
`unreadable`). `sofr` and `iorb` are the target's legs, which `spread_bps` carries. The `mmf_assets` (SEC N-MFP) series the contract
declares has no tracked snapshot to read, and `fed_repo_*` columns are screened in both of their availability readings (with and
without `_sameday`).

## Not checked

* No paired test, bootstrap interval or multiple-testing correction. Nothing here is an acceptance of any series.
* Correlations are not differenced or detrended; a trending series is confounded by the era (finding 4).
* The pre-onset contrast is read at a lead of 1 only, and its by-regime and by-year splits sit in `screen.json` without a table
  (the regime splits are too thin to read: 16 pre-onset days inside ample).
* Lead 2 and beyond for the scheduled series are holes by the as-of rule, not zeros.
* Pressure-day type (quarter-end, month-end, tax date, ordinary) is not split here: the three calendar columns are screened as series,
  not used to stratify.
* The +10 bp threshold and the 2026 days (`docs/decisions/lockbox.md`) are not looked at.

## Reproduce

Panel `4ddc3882…` (the published panel, rebuilt from the tracked fixtures); the scratch panel merged for this screen has sha256
`d1bb988fee5c…`. `OUT` is any scratch directory.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG3.csv --output AUG4.csv
PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG4.csv --output AUG5.csv
PYTHONPATH=src python3 scripts/nowcast.py panel --panel AUG5.csv --output AUG6.csv --summary OUT/nowcast_panel.json
PYTHONPATH=src python3 scripts/dvp_segment_inputs.py panel --panel PUB.csv --output DVP.csv
PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv
PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv --output SCREEN.csv
PYTHONPATH=src python3 scripts/source_screen.py run --panel SCREEN.csv --output docs/pivot/evidence/source-screen/screen.json
PYTHONPATH=src python3 scripts/source_screen.py report docs/pivot/evidence/source-screen/screen.json --tables docs/pivot/evidence/source-screen/tables.md --heatmap docs/pivot/evidence/source-screen/heatmap.svg
```

Evidence: `docs/pivot/evidence/source-screen/` (`screen.json` every cell, `tables.md` the readable tables, `heatmap.svg` series by lead).
