# The lag: what it is, how far it reaches, and the fix

**30 September 2026.** Written in a Cowork cloud session from a read-only clone of `origin/main` at
`f88be75`. The panel was rebuilt from the tracked fixtures and verified against the manifest (digest
`d8b716cf…`, 4 s). The numbers below come from scouting scripts, not records. Scripts and raw output
are in `notebooks/scouting/`. Every figure has to be reproduced through the repository's own code
before it appears anywhere public.

## 1. Root cause: one conversion, applied to every day

At a 16:00 decision on business day D, forecasting the next business day T, the latest public SOFR is D−1's.
It is published at 08:00 on D and final by 15:00 (the `nyfed_sofr` declaration). That value is **two rows
before T on every day of the sample**, holidays included, because the lag is one *business* day.

The project turned that business-day lag into calendar days at its **worst case**
(`worst_case_calendar_days: 6`). It made that the purge (`splits.clears_purge`: `row + 6 < scored`), and then used
the purge to choose the feature row as well as to trim training labels (`baseline._feature_index`). The docstring
there is right that row T−1 would leak. The rule also discards T−2 to T−4 on every ordinary day, to cover the
worst holiday week.

| What was checked | Where | Finding |
|---|---|---|
| Fold dates in every published record | `docs/runs/*.json`, `folds.last` | **All 44 records** (11 backtest, 19 compare, 13 exceedance, 1 persistence): feature date = scored date − 7 calendar days |
| Rows between the feature row and the scored row | rebuilt panel | 5 rows on 1,704 days, 4 rows on 376 |
| Call sites that pick a feature row this way | `grep _feature_index` | backtest, compare, exceedance-backtest, event-holdout, tail diagnostics, and the conformal/CV+ calibration rows in `ml.py` |
| How regressors are read | `ml._design_row` | every regressor, calendar included, comes off that row |
| How the gbm is trained | `ml.fit_gradient_boosted_quantiles` | one-step pairs, served at a 4–5-row gap |
| Slow series | FR 2004: 6 business days → worst case 11 calendar | declaring dealer positions made the purge 11 days, so **every** input went about 8 business days stale |

So the published "next-business-day" results are really forecasts from inputs about a week old. The old
design is leak-free. It is simply more conservative than the information set allows, by 2–3 business days on
every day.

## 2. Measured impact (scouting; 2,039 scored days, 2018-07-05 → 2026-09-03)

The controls come first. Persistence under the published rule reproduces `backtest_persistence_mh61.json` exactly
(MAE 3.104). The published gbm construction (4 features, one-step pairs) gives 2.623 against the records' 2.593.
The difference is monthly versus daily refit and sklearn 1.8 versus 1.6.1.

**Point and quantile forecasts** (MAE bp; pinball averaged over the 5 contract levels; raw uncalibrated q05–q95
coverage):

| Design | all | 2018–19 | 2021–23 | 2025–26 | pressure days | pinball | raw cov |
|---|---|---|---|---|---|---|---|
| Persistence, published rule | 3.104 | 7.45 | 0.90 | 4.39 | 5.03 | – | – |
| **Persistence, as-of** | **2.509** | 6.49 | 0.61 | 3.32 | 4.70 | – | – |
| gbm 4 feat., published rule (≈ published model) | 2.623 | 5.05 | 1.17 | 3.90 | 5.24 | 0.995 | 0.67 |
| gbm 4 feat., **as-of, nothing else changed** | **2.342** | 4.89 | 1.07 | 3.13 | 5.11 | 0.861 | 0.71 |
| gbm 4 feat., as-of, direct pairs | 2.454 | 5.15 | 1.16 | 3.27 | 5.21 | 0.880 | 0.76 |
| gbm full, published rule | 2.565 | 5.10 | 1.21 | 3.45 | 5.05 | 0.948 | 0.69 |
| gbm full, as-of, no calendar | 2.422 | 5.12 | 1.15 | 3.14 | 5.03 | 0.874 | 0.73 |
| gbm full, as-of, calendar read week-old | 2.326 | 5.07 | 1.08 | 2.91 | 4.82 | 0.844 | 0.72 |
| gbm full, as-of, calendar at T | 2.344 | 5.13 | 1.09 | 2.95 | 4.91 | 0.838 | 0.75 |
| gbm full, as-of, calendar + settlements at T ⚠ | **2.268** | 4.94 | 1.04 | 2.82 | 4.67 | **0.818** | 0.75 |

"Full" means the 4 rates plus TGCR/BGCR − IORB, 4w/13w bills, reserves, TGA and the settlement split. ⚠ The settlement
arm is **not admissible under today's registry**. `treasury_auctions` dates availability at 23:59 on the settlement
day (`basis record_date`, which is conservative by design). Admitting it needs an auction-date availability declaration.

**Pressure probability**, where the event is SOFR − IORB ≥ +5 bp on T (163 events, 34 of them on the 233 scheduled
pressure days). Monthly refit throughout.

| Model | Brier | skill vs climatology | AUROC | Brier, pressure days | AUROC, pressure days |
|---|---|---|---|---|---|
| Climatology (expanding) | 0.0740 | 0 | 0.61 | 0.123 | 0.53 |
| Persistence-logistic, published rule | 0.0623 | 0.16 | 0.86 | 0.109 | 0.85 |
| **Persistence-logistic, as-of** | **0.0531** | **0.28** | **0.92** | 0.097 | 0.88 |
| gbm classifier, published rule | 0.0679 | 0.08 | 0.88 | 0.111 | 0.85 |
| gbm classifier, as-of, calendar + settlements at T ⚠ | 0.0637 | 0.14 | 0.91 | **0.083** | **0.91** |

At ≥ +10 bp (70 events) the pattern is the same. On pressure days the as-of model scores Brier 0.069 against
0.073 for as-of persistence, and 0.083 for the published-rule model.

Around the two episodes, P(≥ 5 bp) came out as follows:

| Day | Published-rule model | As-of model ⚠ |
|---|---|---|
| 16 Sep 2019 | 0.18 | 0.98 |
| 17 Sep 2019 | 0.09 | 0.70 |
| 31 Oct 2025 | 0.09 | 0.96 |

**But on 27–28 Oct 2025, with the spread already at 12–16 bp, the as-of model said 0.00.** Persistence said 0.48.

## 3. What the numbers say

1. **Timing is the dominant defect.** Moving from the published control (2.623) to the best arm (2.268) is
   −0.355 bp. Of that, **79% (−0.281) is reading the same four inputs at the right time**. Features and scheduled
   inputs account for the remaining 21%.
2. **Every published comparison sets a handicapped model against a handicapped benchmark.** Fair persistence (2.509)
   beats every published backtest (best 2.593). Against fair persistence, the published 4-feature model's real edge is
   −6.7% (2.342), and the full as-of model's is −9.6%.
3. **For the pressure probability, the benchmark to beat is a one-variable logistic on the latest spread.** It beats
   every gbm classifier overall. The rich model only wins on scheduled pressure days, and it misses the onset of a new
   regime. Its trees rank well (AUROC) but its probabilities are miscalibrated. That argues for an interpretable,
   calibrated probability model with regime and calendar interactions, recalibrated and judged on reliability.
4. **Two of my earlier claims were wrong, and I'm correcting them here.**
   - The calendar misalignment is real, but it barely moves MAE (2.326 vs 2.344), because `days_to_month_end` read a week
     early still carries month-end timing. Calendar at T improves pinball and coverage a little. It does not explain the
     calendar contradictions on its own.
   - The horizon-mismatch idea is refuted for the point forecast. One-step pairs beat direct pairs under both rules.
     Direct pairs give better raw coverage, so the choice waits for the calibrated comparison.
5. **The raw bands are flat across volatility terciles under both designs** (published 0.70/0.67/0.65, as-of
   0.75/0.76/0.75). So the calm/stressed pattern in the published CV+ results is produced or exposed by the calibration
   layer on the stale design. It has to be re-diagnosed, not carried over.

## 4. How far it reaches

**Affected: re-measure before citing.**
- **All 44 run records** and the event-holdout journals. They stay valid as measurements of the conservative design,
  but they do not measure a next-day forecast.
- **The benchmark.** Every "beats persistence" figure and every skill figure relative to it.
- **The calibration line, 11–19 Sep.** Conformal vs CV+, both asymmetric variants and their retirement, scaled and
  partial, the 2022 "4 bp location bias", the calm-tercile over-coverage and the 2025 reading. All of it was
  calibrating week-old inputs. The decisions may survive, but their evidence does not.
- **Feature verdicts.** Calendar (both readings). Dealer positions ("worse than leaving it out" is confounded, because
  declaring it made every other input eight days stale). ARX, GARCH and lags (computed from the week-old row). The
  funding +11% twCRPS result (its direction probably holds, its size is unknown).
- **The tail line.** "Probability zero on 125 days", "GPD fits only from 2024", the 2022–23 zero excesses, B44's refusal
  rule, and Phase 2's tail clause ("fails, held") and interval criterion ("met").
- **Refusals created by the rule itself.** `on_rrp_h41` (refused because the purge is stated against the scored date),
  job 536's unpaired comparison, and the "price the purge per column" ritual.
- **Public statements that say next-day.** `README.md` (its generated blocks and its prose), `PLAN.md`,
  `METHODOLOGY.md`, `docs/DATA_QUALITY_DECISIONS.md`, `docs/RESEARCH_NOTES.md`, the executive summary, project
  status, portfolio case study, the website page, and both Notion advisor pages.

**Not affected:** the data layer (panel, fixtures, availability declarations, settlement zeros, rule-10 carries), the
leakage guarantee, reproducibility, seeds, provenance and the panel digest.

**Why no guard caught it:** `_check_decision_relative_availability` and the A23 audit only ask whether a row was
*published* by the decision instant. Nothing asks whether a *newer* one was.

## 5. The fix

**Rule: a forecast uses exactly the information public at its decision instant.**

1. **Per-field as-of reads.** For each declared (source, field), read the latest row whose `_declared_availability(…)`
   is at or before the decision instant: 16:00 on the panel day before T. This reuses the registry's existing
   declarations, and nothing new is assumed. Under them, daily NY Fed rates and bills land at T−2 and H.4.1 weekly
   series at their latest print. This is your 19 Sep `on_rrp_h41` ruling (b), applied to every field.
2. **Scheduled inputs are a declared class.** A value that refers to the scored date but is announced earlier: the
   calendar (always known), FOMC meeting schedules (`docs/decisions/fomc-point-in-time.md` already dates a schedule by when it became
   public), and settlements (from the auction
   results time, *once declared*). Each carries its own availability instant, and the same guard checks it.
3. **The purge becomes label observability.** A training target is used only if it was public by the fold's decision
   instant (for SOFR, t ≤ T0 − 2). The feature row and the purge are no longer one number.
4. **One fold grid for every declaration.** Adding a slow feature no longer moves the grid or stales other inputs, so
   any two declarations are paired by construction. The per-column purge pricing retires.
5. **Two-sided guards.**
   - Leakage (keep): nothing read is newer than the decision instant.
   - **Staleness (new):** no admissible newer value exists. Mutating the read to p − 1 must fail.
   - Future perturbation: changing any value published after the decision instant leaves the forecast bit-identical.
   - Records publish the per-field staleness in rows and hours, so a reader can see the information set.
6. **Training pairs are a measured choice, not a doctrine.** Keep one-step pairs as the default (better MAE here). The
   direct variant is one flag, compared on calibrated metrics.

**Alternatives considered and rejected:**
- A shorter uniform purge (for example 1 business day as calendar days) leaks in holiday weeks.
- A per-day uniform purge set by the slowest declared field still stales fast series and still moves the grid.
- Moving the decision time buys nothing public: SOFR for D is not out until 08:00 on D+1.

The per-field as-of join is the standard treatment of the "ragged edge" in real-time forecasting (Giannone, Reichlin &
Small 2008; Bańbura et al. 2013). It is also what the registry's per-field declarations were built to support.

## 6. What must happen, in order

1. **Your rulings.** The information-set rule goes in `docs/decisions/` (draft in the plan). Rule on the settlement
   declaration, record handling and refit cadence (questions pending).
2. **Implementation PR.** As-of reads, scheduled class, label purge and one grid, with the staleness guard written red
   first. `_check_decision_relative_availability` must still pass on every fold.
3. **Re-score the fleet on the new rule, in the cloud.** Minimum set: persistence, gbm with none and cross_conformal,
   the published funding declaration, and the pressure-probability baselines (climatology, persistence-logistic).
   Then re-diagnose calibration by regime and tercile before any calibration verdict is repeated.
4. **Archive the 44 old records under a labelled folder.** Regenerate the README, and correct every next-day
   statement listed in §4.
5. **Re-open the verdicts only after the re-score.** That covers the calendar, dealer positions, `on_rrp_h41` (now
   admissible) and the tail line.
