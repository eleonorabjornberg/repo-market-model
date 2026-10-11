# The onsets no model warns: was anything public? (#560, of #374)

A scratch diagnostic. It changes no model, rule, cut-off, threshold, declaration or published figure, writes nothing into
`docs/runs/`, and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`). It decides nothing; the readings it made are listed at
the end. The code is `scripts/unwarned_onsets.py`, the declaration `metadata/unwarned_onsets.json` (committed before any score was read),
the tests `tests/test_unwarned_onsets.py`, and the numbers `docs/pivot/evidence/unwarned-onsets/onsets.json` and `onsets.md`
(the full tables: every input's z-score, the ten largest, every row's probability and cut-off, and the events, per onset and lead).

## Result in one paragraph

Under the judge as it stands (the weighted rule in force) and the rows scored so far, **six of the directive's eight onsets are warned by
no model row** (2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28, 2020-03-04, 2024-12-26); the other two are each warned by a few rows at
one or two leads (2020-03-12 by the stress factor and two hurdle rows; 2024-09-30 by `risk_logistic` and by rows with the settlement
dating). **For the four of 2018 the question "was anything public" is not the binding one: the judge had no cut-off in force for almost every model
row on those days (the cut-off is infinite, so no probability can flag; 36 percent of all 2018-19 model-row cells have none, and none in any
later regime).** The rows' own probabilities on them were high against ordinary days: the skew-t forms and the settlement-dated rows put
2018-11-15, 2018-11-30 and 2018-12-17 above 92 to 99 percent of the regime's ordinary days at some lead, and 2018-12-28 above 93 to 94
percent. For the other two, which had cut-offs: 2020-03-04 has **a public signal no row reads** (the 3 March 2020 announced IORB cut), and
2024-12-26 has **no public signal of stress** (the rule's label rests on rate levels after the 2024 cuts). The one-line verdicts are in Table 1.
Where there is a signal it is a scheduled one (a Treasury settlement, an announced policy move), public days before the panel's availability
rule lets a row read it. That sets the ceiling for the next models: for 2018 the ceiling is the cut-off, not the information; for 2020-03-04 it is
a policy announcement the models do not read; for 2024-12-26 and for the rest, the panel and the sources named hold nothing a model could use.

## The onsets, the rows, the reads

* **The onsets** are the +5 bp onsets of tier 1 at lead >= 1 on the days scored at every horizon (26), the judge's own. The eight are the
  directive's list by regime: 2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28, 2020-03-04, 2020-03-12, 2024-09-30, 2024-12-26.
  **The list differs from the computed one** (above): the rows scored here under the judge's weighted rule warn 2020-03-12 and 2024-09-30,
  which `episode-post-mortem-result.md` (#474, the five passers under the cut-offs of #407) counted as missed by all five. The difference is
  the rows (the stress factor, the hurdle) and the rule, not an error in either page. The verdicts below are given for the declared eight
  anyway, computed on the rows that did not warn them.
* **The rows** are every row the scoring commands of #533 (`ngboost_laplace`), #539 (hurdle), #541 (settlement and H.4.1 dating, three arms),
  #542 (structural), #543 (stress factor), #544 (2008-2018 pre-training) and #545 (projected reserves) write, with the five tier-1
  passers and the two references: 57 rows in those families, and 19 further rows (the references, the every-day rows of the same files, the
  unselected `risk_quantile_skewt`) that are scored and listed in the evidence but do not count for "warned". Cut-offs are the judge's
  (`choose_cutoffs`, weighted rule). Three rows the files carry (`gbm_reference`, `ngboost_normal`, `qrf`) have no candidate file, so the
  judge cannot flag them; they are left out and listed in the evidence.
* **The inputs** are the 33 panel fields the information set can read at a decision instant (`INPUTS` in the script), read as of the decision
  instant of the day `L` scored days before the onset (`InformationRule`, horizon `L`, the leakage and staleness guards of
  `baseline._as_of_folds`). **Treasury settlements for the target day, and the announced-IORB fields, are not readable at leads 2 to 5**
  (the registry makes them observable at 15:00 the panel day before), and the guard refuses them there; they are listed per lead as
  "not public at this lead" and have no z-score. This is the declaration of availability, not a statement about when the settlement was announced
  (see Table 1, 2018-11-15, and `desk-standard-result.md`).
* **The z-score** is the input's as-of level at that lead against its mean and sample sd over the same regime's scored days that are not
  pressure days. It is in hindsight (the regime's whole window), so it describes and does not forecast. An input with an sd of 0 has none.
* **The announced net settlement** of the next 1 to 5 days is the column of `scripts/net_settlement.py`, read from the origin row.
* **Events** (Table 5 of the evidence): the calendar type of the target and origin days, the policy register as of the decision instant
  (`policy_events.policy_state`: IORB, ON RRP, standing repo, QT, SLR, reserve management, the debt-limit state and pending entries), the
  entries announced in the ten days before, FOMC statement days within ten days (Fed calendar pages, saved as the URLs in the script), and Treasury quarterly-refunding statement days within ten days (`REFUNDING`, each with its home.treasury.gov URL).

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panels as for #428, #542 and #545. `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1),
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_hurdle.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/hurdle_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/latent_factor.py run --panel AUG2.csv --published PUB.csv --horizon $h --risk OUT/risk_h$h.json --output OUT/lf_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/structural_liquidity.py run --panel AUG3.csv --published PUB.csv --risk OUT/risk_h$h.json --horizon $h --output OUT/sl_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/projected_reserves.py run --panel AUG4.csv --published PUB.csv --risk OUT/risk_h$h.json --horizon $h --output OUT/pr_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/effr_pretrain.py run --panel PUB.csv --horizon $h --output OUT/effr_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/effr_pretrain.py combine --panel PUB.csv --risk OUT/risk_h$h.json --transfer OUT/effr_h$h.json --output OUT/comb_h$h.json
for arm in settle h41 both; for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm $arm --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/${arm}_h$h.json
PYTHONPATH=src python3 scripts/unwarned_onsets.py run --panel PUB.csv --scratch-panel AUG4.csv --output-dir docs/pivot/evidence/unwarned-onsets \
    'OUT/bench_h{h}.json' 'OUT/risk_h{h}.json' 'OUT/q_h{h}.json' 'OUT/hurdle_h{h}.json' 'OUT/lf_h{h}.json' 'OUT/sl_h{h}.json' 'OUT/pr_h{h}.json' \
    'OUT/comb_h{h}.json' 'OUT/effr_h{h}.json' 'OUT/settle_h{h}.json' 'OUT/h41_h{h}.json' 'OUT/both_h{h}.json'
```

The scoring took about an hour on four cores with one thread per job; the diagnostic itself under two minutes.

## Table 1. One-line verdict per onset

"Rule" is the first of the three declared verdicts that holds (`metadata/unwarned_onsets.json`, `readings`): an input no row reads, at
|z| >= 3 at some lead, is "public and unused"; otherwise a row's probability at half its cut-off or more, or a row-read input at
|z| >= 3, is "public and too weak"; otherwise "no public signal found". The reading beside it is this page's own. The verdict on the model
families alone is the same for every onset as the verdict on all rows. "No cut-off in force" is the count of model-row cells (row x lead) whose cut-off is infinite.

| onset (regime, type) | warned by | rule | the signal (lead, z) and what the rows did | public source outside the panel |
|---|---|---|---|---|
| 2018-11-15 (2018-19, ordinary) | none | **signal public and unused**; and **no cut-off in force** (285 of 285 model-row cells) | The refunding settles on the 15th: `treasury_settlement_soma` +5.4, `treasury_settlement` +4.0, `treasury_settlement_coupons` +3.8 at lead 1 (readable only then). No other input moved (next largest +1.7). Rows' probabilities: `risk_quantile_skewt_base` 0.94 at lead 1 (above 98 percent of the regime's ordinary days), the settlement-dated skew-t row 0.96 at lead 4; the other passers 0.07 to 0.11 at lead 1 and about 0 at leads 2 to 5. No cut-off, so none could flag. | TreasuryDirect auction data: the 3-, 10- and 30-year auctions of 5, 6 and 7 November 2018 ($37bn, $27bn, $19bn) all issue on 15 November 2018, so the settlement was auctioned 8 to 10 days ahead. The quarterly refunding statement of 31 October 2018 announced the refunding (settling 15 November; the statement's own text names 15 November 2018): <https://home.treasury.gov/news/press-releases/sm538>. <https://www.treasurydirect.gov/TA_WS/securities/search?format=json&startDate=2018-11-01&endDate=2018-11-10&dateFieldName=auctionDate> |
| 2018-11-30 (2018-19, month end) | none | **signal public and unused**; and **no cut-off in force** (277 of 285) | `treasury_settlement_coupons` +6.6 (read by the passers) and `treasury_settlement_soma` +3.9 (read by none) at lead 1. Nothing else moves. `risk_quantile_skewt_base+h41` 1.00 at lead 5 and `structural_liquidity` 0.96 at lead 3 (above 99 and 92 percent of ordinary days); the base skew-t row had a cut-off of 0.94 at lead 1 (probability 0.69). | The month-end coupon settlement is scheduled in the same auction calendar; no document outside the panel is named for this one. |
| 2018-12-17 (2018-19, tax date) | none | **signal public and too weak**; and **no cut-off in force** (277 of 285) | Only `treasury_settlement_coupons` +3.6 at lead 1. The settlement-dated skew-t rows give 1.00 at leads 3 to 5 (above 97 to 99 percent of ordinary days); `risk_gbm` 0.08 to 0.12. A tax date is a calendar risk date. | The FOMC meeting of 18-19 December 2018 follows the onset; its statement (19 December) is not public at any lead. None named. |
| 2018-12-28 (2018-19, month end) | none | **no public signal found**; and **no cut-off in force** (277 of 285) | No input reaches |z| of 1.3 at any lead. The register's only entries in the ten days before are the 19 December IORB and ON RRP announcements. The settlement-dated skew-t row gives 0.81 at lead 5 (above 94 percent of ordinary days), from the month-end calendar. | None found. |
| 2020-03-04 (2020, ordinary) | none | **signal public and unused** | `iorb_announced_change_bps` at lead 1 (a z-score of -157 is an artefact of an sd near 0; the fact is a 50 bp cut announced the day before, a field no row reads). `latent_factor_resid` reached 0.99 and `latent_factor` 0.98 of their cut-offs at lead 1 and 5 without flagging. | Federal Reserve press release, 3 March 2020, 10:00 a.m. (50 bp cut to 1-1.25 percent): <https://www.federalreserve.gov/newsevents/pressreleases/monetary20200303a.htm> (the register's entry, `iorb-20200303`, cites `monetary20200303a1.htm`). |
| 2020-03-12 (2020, ordinary) | 6 rows at one lead each (`latent_factor`, `latent_factor_resid` at lead 1; `latent_factor_logit`, `risk_gbm+latent_factor_logit` and two hurdle rows at lead 5) | too weak, for the rows that did not warn | `spread_bps` +3.5 and `sofr_p75_iorb_bps` +3.0 at lead 5 (both read); `latent_factor_logit` reaches 1.63 of its cut-off at lead 5. The spread had already moved. | Open Market Desk statements of 11 March (repo operations of at least $175bn a day from 12 March) and 12 March 2020: <https://www.newyorkfed.org/markets/opolicy/operating_policy_200311>, <https://www.newyorkfed.org/markets/opolicy/operating_policy_200312a> |
| 2024-09-30 (2024, quarter end) | `risk_logistic` (lead 4, probability 0.04 over a cut-off of 0.02), and four rows with the settlement dating | too weak, for the rows that did not warn | `treasury_settlement_coupons` +3.8 at lead 1; no market input moves (largest +1.6). `risk_logistic+settle+h41` reaches 2.8 of its cut-off at lead 3. The quarter end is a calendar risk date. | FOMC statement of 18 September 2024 (IORB set to 4.90 percent, ON RRP 4.80, standing repo 5): <https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a1.htm> (the register's source). |
| 2024-12-26 (2024, ordinary) | none | **signal public and unused**, by the rule only | `ofr_tri_rate` -3.2, `sofr` -3.1, `bgcr` -3.1 at lead 1: rate **levels** after the cuts of 18 September, 7 November and 18 December 2024, against a regime mean from before them; a level shift and not a stress. `tga_daily_change` +4.1 at lead 5 is read by the passers; no row exceeds 0.37 of its cut-off. | FOMC statement of 18 December 2024: <https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a1.htm> (the register's source). Reading: no public signal of stress; the rule's label is an artefact of z-scoring a level. |

Contrast (criterion 3). The 2025 onsets the structural and projected-reserves rows both miss while `risk_gbm` warns are 2025-09-30, 2025-12-15
and 2025-12-26 (`risk_gbm+structural` and `risk_gbm+projected` warn them through the passer on risk dates, and the 2025-26 cells all have
cut-offs). Dozens of rows warn each, so there is no unwarned-onset question; the evidence gives their inputs on the same footing:
`treasury_settlement_coupons` +4.2 at lead 1 for the quarter end (read by the passers), and rate **levels** (`sofr` -3.9, `ofr_tri_rate`
-3.9 to -4.2) for the 15 and 26 December onsets, with `dealer_treasury_position` +3.2 at leads 2 to 4 for the 15th. What distinguishes them
from the 2018-2024 misses is the cut-off (present) and that the passers' risk-date probabilities, not a market input, carry the warning.

## What it says about the ceiling

* **The four 2018 misses are a cut-off fact first.** The judge picks each refit's cut-off from the model's earlier walk-forward probabilities
  (`pressure_judge.choose_cutoffs`; a block with none flags nothing). In the first year of the scored window that is infinite for most model
  rows: 36 percent of the 2018-19 model-row cells, none later. A row cannot warn those onsets whatever it believes. The rows that give the
  four a high probability are the skew-t form, the settlement-dated rows and the structural row, from the calendar and the settlement.
  Whether a finite cut-off would have been right is not tested here (it needs a rule for the early blocks, which is the judge's, hers). The
  practical reading for the next models: the 2018 misses cost every model equally and say nothing about its information.
* **How often the bars are crossed anyway.** On ordinary days of the same regime at lead 1, some input is at |z| >= 3 on 16 percent of days in
  2018-19, 15 percent in 2020, 17 percent in 2024 and 20 percent in 2025-26; one that no row reads, on 9, 10, 9 and 12 percent (Table 2 of
  the evidence). A single input over the bar is common, and the "unused" verdicts are not rare by themselves; the ones that stand are those
  where the input is a known scheduled event (the settlement, the announced cut).
* **The panel's market inputs carry nothing for the 2018 onsets.** The largest market-input z-score (settlements and the announced-IORB fields
  left aside) on 2018-11-15, 2018-11-30, 2018-12-17 and 2018-12-28 at any lead is 1.7, 1.6, 1.0 and 1.2.
* **Where the recoverable signal is.** In the settlement for 2018-11-15 and 2018-11-30: the amount was fixed by the auction days before the
  panel allows it to be read (`desk-standard-result.md`, point 1: 4 to 5 panel days ahead for bills, 5 to 14 for coupons, against the
  15:00-the-day-before declaration). The `settle` arm of #541 dates settlements from the announcement; its rows give the 15th a probability
  of 0.02 to 0.96 at leads 2 to 4 (Table 4 of the evidence), but with no cut-off in force.
* **2020-03-04** is the one onset where an announced policy move sat in the panel and was read by nothing: the 3 March cut, in
  `iorb_announced_change_bps`. The stress factor came within 1 to 2 percent of its cut-off (`latent_factor_resid` 0.99 at lead 1). The policy
  register (#412) carries IORB changes as features of its own; whether they would have flagged it is not tested here.
* **2024-12-26** has a finite cut-off in every row and the highest probability of any model row is 0.37 of it; its largest market-input moves
  are rate levels after the 2024 cuts and the Treasury account's daily change (+4.1 at lead 5, an input the passers read).

## Readings made by this pull request, for Eleonora

The directive leaves these open; each is declared in `metadata/unwarned_onsets.json` or the script. None changes a model, rule or figure.

1. **The bar** (`z_strong` = 3) and the **"half the cut-off"** line (`under_ratio` = 0.5, the post-mortem's `UNDER_RATIO`).
2. **"Unused"** means no candidate file of a scored row lists the input in its `features`. A row that reads the input at one horizon only
   (the settlement fields, dropped at h >= 2) counts as reading it.
3. **The reference for the z-score** is the whole regime's non-pressure days (hindsight), not a trailing window.
4. **Rate levels are z-scored as levels.** After a policy cut this labels the new level an outlier, which is why 2024-12-26 and two of the
   contrast onsets read "unused" on `sofr` and `ofr_tri_rate`. The page says so beside each; the rule was not changed after the scores were read.
5. **The row set** was widened beyond the directive's list after the declaration only in the sense that the files hold more rows than the
   directive names; "warned" counts the directive's families only, and the verdict is given on both sets (identical for every onset).
6. **FOMC statement days** are the last day of each meeting from the Fed's calendar pages for 2018, 2020 and 2024; the unscheduled actions of
   March 2020 are in the policy register. **Treasury quarterly-refunding statement days** (`REFUNDING` in the script) are the dates on the
   refunding statements themselves, each read on home.treasury.gov: 31 October 2018 (<https://home.treasury.gov/news/press-releases/sm538>),
   5 February 2020 (`sm896`), 6 May 2020 (`sm1001`), 31 July 2024 (`jy2512`), 30 October 2024 (`jy2697`), 30 July 2025 (`sb0212`) and
   5 November 2025 (`sb0305`), all under the same press-releases path. They are the quarters that bound the eight onsets and the three
   contrast onsets; the statements of the other quarters of those years were not fetched. The Table 5 line for each lead lists the ones
   within ten days of the origin (only the 31 October 2018 statement falls in a window, for 2018-11-15).
7. **The count of inputs.** `metadata/unwarned_onsets.json` (`inputs`), committed before any score was read, says "the 35 panel fields". That
   was a miscount: `INPUTS` in the script has 33, the fields the information set can read, and 33 are read. The declaration is left as it was
   committed; this entry is the correction, and no field was added or dropped after the scores were read.

## Not checked

* No source outside the panel was fetched into it or made an input. The TreasuryDirect, Federal Reserve and New York Fed pages named were read once
  each to confirm they exist and say what is cited; nothing else was fetched.
* The Desk's operation schedules for the other onsets, and market commentary, were not searched. An onset with "none named" is not shown to have no public source. The refunding statements of the quarters not listed in reading 6 were not fetched.
* The policy-register features (#412) were not run on these onsets.
* No 2026 day is scored; the confirmation window is not looked at.
