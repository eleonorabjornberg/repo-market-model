# New data sources for the ordinary-day gap: screen and correlation matrices (#630)

An exploratory measurement for #630, not a record and not a model: nothing is selected, no published declaration or figure moves, and
nothing is written into `docs/runs/`. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`); the script refuses a panel past it and every
reader drops a later day. The due diligence is in `docs/pivot/new-sources-due-diligence.md` (committed before any fetch, with a section on what step 2
found). The code is `scripts/new_sources.py` and `src/repo_model/new_sources.py`; the evidence is in `docs/pivot/evidence/new-sources/`
(`screen.json`, `tables.md`, `inter_source_{pooled,ample,scarce}.csv`, `heatmap.svg`).

**Caution: this is a screen across many series, so every number is exploratory.** The statistical comparisons run are 16,522 in all (4,022 Spearman correlations, 996 AUROCs,
257 pre-onset contrasts, 170 partial rank correlations, 11,077 inter-source correlations). **None is corrected for multiplicity.** The intervals are
90 % percentile bootstraps that resample days independently, so serial dependence is ignored and they are too narrow. Only six onsets fall on ordinary
days, so every pre-onset interval rests on six events.

## What was added

Four measurement sources, each registered in `metadata/sources_measurement.json` with its publication-instant rule, read by a reader with a guard and a
recorded mutation (`tests/test_new_sources.py`), and off in every published declaration. Twelve columns:

| source | columns | publication instant used |
|---|---|---|
| `nyfed_pd_financing` | `pd_repo_ust`, `pd_reverse_repo_ust`, `pd_repo_mbs`, `pd_fails_deliver_ust`, `pd_fails_receive_ust` | weekly, six business days after the Wednesday as-of date (the held positions' release) |
| `treasury_auction_results` | `auc_accepted_bn`, `auc_dealer_share`, `auc_indirect_share`, `auc_cover` | 15:00 on the auction day; every auction closes by 14:30 |
| `nyfed_on_rrp_counterparties` | `rrp_counterparties` | next business day 16:00 (the held amount accepted's rule); rewritten records excluded |
| `treasury_dts_debt_cash` | `dts_debt_issues_bn`, `dts_debt_net_bn` | next business day 16:30 (the held TGA balance's rule) |

Sources not taken, and why, are in the due-diligence page: the ON RRP counterparty-type split (added a month late), EFFR volume, the OFR collateral
breakdown and the H.4.1 detail lines (leads for a later directive), and DTCC and the SIFMA tables (blocked).

## Method

The scored days are #478's: 1,873 days from 2018-06-29 to 2025-12-31, every series read as of each decision instant with the as-of rule at leads of 1, 2, 3,
5 and 10 panel days. An **ordinary day** is a scored day whose pressure-day type is `ordinary` (not a quarter-end, month-end or tax date) and that settles no
coupon: 1,469 days, 82 of them above +5 bp, with six onsets (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12, 2024-12-26). Regimes are the
as-of reserve-scarcity bands (ample, scarce) and states; no hindsight labels. The incremental check removes the as-of scarcity state and the tail spread
(`sofr_p99_iorb_bps`, #601) from both sides by rank before correlating. The screen machinery is #478's (`scripts/source_screen.py`); #629's ordinary-day
script is not on main yet, so this PR carries its own ordinary-day screen over the same machinery, and the run should be repeated with #629's script when it
merges (this directive is queued to merge after #629).

## Result

Tables 1 to 4 are in `docs/pivot/evidence/new-sources/tables.md`; the heatmap is `heatmap.svg`. Plainly:

1. **No new series adds clear information about ordinary-day pressure beyond the scarcity state and the tail spread.** The partial rank correlations of the new
   series are all within 0.12 of zero. Of the 25 series with the largest partial correlation, two are new.
2. **What the raw numbers show is mostly level and trend.** `rrp_counterparties` has the largest raw association (AUROC 0.22, interval 0.19 to 0.25), but it is
   0.95 correlated with the held `on_rrp` and its partial correlation is +0.07; the primary dealer financing series are 0.89 to 0.90 correlated with held volume and
   balance-sheet levels. Their pooled correlations with held series are inflated by shared trends, which the by-band matrices (`inter_source_ample.csv`,
   `inter_source_scarce.csv`) show less of; the matrices are of levels, not changes.
3. **Duplicates.** The five dealer series fall in redundant groups with held series (`pd_repo_ust` and `pd_reverse_repo_ust` with `bank_total_assets`;
   `pd_repo_mbs` with `bgcr_volume` and `sofr_volume`; the two fails series with each other). `rrp_counterparties` is in the `on_rrp` group.
   The auction and DTS series are in no group with a held series.

## Ranked leads

Ranked by the incremental rank correlation (Table 4), new series beside the held ones. A lead is a candidate for a declared model test in #624 or after, not evidence.

| rank | series | new | partial rho [90 %] | reason | risk that it is noise |
|---|---|---|---|---|---|
| 1 | `policy_debt_limit_reinstated` | no | +0.21 [0.14, 0.26] | strongest incremental value among all series | six-episode event dummy; sits in a few stretches |
| 2 | `policy_slr_exclusion_in_force` | no | -0.18 [-0.20, -0.15] | incremental after scarcity and tail | a regime dummy that switches once |
| 3 | `sofr_p99_iorb_sd15_bps` | no | +0.16 [0.13, 0.19] | volatility of the tail spread | derived from the tail spread already controlled |
| 4 | `pd_reverse_repo_ust` | **yes** | +0.11 [0.06, 0.15] | dealers' reverse repo financing of Treasuries; the strongest new series | raw correlation is -0.05, so the partial value appears only after the controls; in a level-and-trend group with `bank_total_assets`; weekly, eight days stale |
| 5 | `pd_repo_ust` | **yes** | +0.10 [0.06, 0.15] | dealers' repo financing of Treasuries | same as above; 0.90 correlated with `sofr_volume` |
| 6 | `auc_dealer_share` | **yes** | -0.07 [-0.13, 0.00] | the only new series whose ordinary-day AUROC interval is clear of 0.5 with a plausible mechanism (more dealer take-down, weaker bidding): AUROC 0.58 [0.51, 0.66], pre-onset AUC 0.65 [0.49, 0.79] | the partial sign is opposite to the AUROC's; the pre-onset interval touches 0.5 and rests on six onsets; present only on auction days |
| 7 | `pd_fails_deliver_ust` | **yes** | +0.06 [0.01, 0.11] | fails are the direct sign of collateral scarcity | AUROC 0.53 [0.46, 0.58] straddles 0.5; pre-onset AUC 0.36 [0.26, 0.47] points the other way |

Not leads: `auc_accepted_bn`, `auc_cover`, `auc_indirect_share`, `dts_debt_issues_bn`, `dts_debt_net_bn`, `pd_repo_mbs`, `pd_fails_receive_ust` (partial values within
0.08 of zero, or intervals that include it), and `rrp_counterparties` (a duplicate of `on_rrp`).

## Correction (#680): withheld weeks and the carry cap

#630 stated that the dealer financing series have no gap, and it carried every value forward with no limit. Both were wrong. The export withholds some weeks (85 of 666 weekly dates for `pd_repo_ust` (2022-01-12 onward; 15 in 2022, 16 in 2023, 21 in 2024, 33 in 2025; longest run 12 weeks, 2025-01-08 to 2025-03-26), 72 for `pd_reverse_repo_ust` (2022-07-13 onward; 17, 13, 16 and 26 in 2022 to 2025; longest run 9 weeks, 2025-04-16 to 2025-06-11) and 3 for `pd_repo_mbs` (one each in 2022, 2024 and 2025); `pd_fails_deliver_ust` and `pd_fails_receive_ust` have none), and the decided rule (`docs/decisions/weekly-carry.md`) stops a weekly carry 13 days after the value's own date. The code now does (`new_sources.add_columns`), and the withheld weeks are listed by `new_sources.parse_pd_suppressed`. The table and the leads above are #630's as published and are left as they were; the re-screen with the cap (`docs/pivot/evidence/new-sources-capped/`, `comparison.md`) moves the two financing series down: the partial rank correlation with the pressure indicator on ordinary days falls from +0.112 to +0.087 (`pd_reverse_repo_ust`) and from +0.104 to +0.076 (`pd_repo_ust`), their rank among the screened series from 20th and 24th to 28th and 31st, and the scarce-band AUROC at a lead of 1 moves from 0.656 to 0.648 and from 0.647 to 0.616. The ordinary days with a value fall from 1,469 to 1,330 and 1,282. No later model row read these columns. Whether to admit the source, given the withheld weeks, is Eleonora's call; the columns stay off the published declaration. The whole account is in `docs/pivot/new-sources-withheld-weeks.md`.

## Not checked

* A model test: nothing here is a paired comparison against the stated benchmark, split by regime and pressure-day type; it is a screen.
* Changes rather than levels: the matrices and correlations are of levels (and the targets' level, change and indicator). A first-difference matrix would
  separate shared trend from shared movement.
* Dependence-respecting intervals (a block bootstrap), and any correction for the 16,522 comparisons.
* The sources listed as not taken or blocked.
* The primary dealer export is not revised in vintage form; a restated figure cannot be seen.
* The six `nowcast_*` variants are unreadable by the as-of rule in this screen exactly as in #478 (undeclared in the contract); they are listed in `screen.json`.

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
# the scratch panels of scripts/source_screen.py (its docstring lists them), ending in SCREEN.csv
PYTHONPATH=src python3 scripts/new_sources.py panel --panel SCREEN.csv --output NEW.csv
PYTHONPATH=src python3 scripts/new_sources.py screen --panel NEW.csv --output docs/pivot/evidence/new-sources
PYTHONPATH=src python3 scripts/new_sources.py report --output docs/pivot/evidence/new-sources
```
