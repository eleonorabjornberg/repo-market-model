# Why the published exceedance curve flattens across thresholds

Directive #373, the item PLAN.md left open when phase 2 was closed. This page says why the published pressure
probability changes little from +5 bp to +50 bp, so that at the upper thresholds climatology wins. It is
descriptive: it changes no model, no published record, no input and nothing the live record logs. Remedies are at
the end, as candidates only; none is scored here.

Every figure is read from `docs/runs/v1_flattening_diagnosis.json`, made by
`scripts/exceedance_flattening_diagnosis.py` on the published panel (`4ddc3882…8999`). The model is pressure model v1
as published (`docs/runs/pressure_model_v1_h1.json` … `_h5.json`): the funding gradient-boosted quantile model
with nested conformal PID, its exceedance read off the issued law, then the out-of-fold Platt step. The walk repeats
the published run and its Brier score at +5 and +10 bp equals the published record's to the last digit at every
horizon (the assembly refuses to go on otherwise). The +20 and +50 bp thresholds are event-listed in the published
records, which carry no pooled figure there; the pooled figures here are diagnostic, not a skill claim.

**Window.** Days from 2018-06-29 to 2025-12-31, before the locked tiers (`docs/decisions/lockbox.md`). The assembly
refuses a walk that scores a later day. No comparison here scores a locked day.

**Benchmarks.** *Climatology* is the report's reference: the expanding unconditional exceedance rate. The
*persistence-logistic* is the published benchmark, refitted the same way. Intervals are 90% stationary-bootstrap
intervals on the paired Brier difference (climatology minus model, positive when the model is better), drawn at
h = 1 only; the other horizons are in the record as means and counts. At +20 and +50 bp the published records carry no
pooled skill claim, Brier score, interval or reliability curve (`docs/decisions/pressure-probability.md`); this page
and record follow that: there they give predicted and realised rates, descriptive reliability (which the directive asks
for) and discrimination, and compute no skill score, Brier score or interval.

## In short

- **The curve is flat because of the law the exceedance is read from, not because the model cannot rank.** The
  fitted quantiles stop at the 95th percentile. Above it, the law spreads the last 5% of mass at constant density
  from q95 to a top knot placed at the largest training residual about the median
  (`FittedGradientBoostedQuantiles._law`, `ml._law_knots`). From 2019-10-03 onward the top knot sits near +295 bp
  on every scored day. It jumps from +88 bp to +332 bp on that day, the first scored day after the refit that
  followed the single day of 2019-09-17 (+315 bp), and it never comes back. So P(> τ) is about
  0.05·(295 − τ)/(295 − q95): 4.9, 4.8, 4.6 and 4.1% at +5, +10, +20 and +50 bp, for any day on which τ lies above q95.
- **That is most days.** τ lies above q95 on 76% of days at +5 bp, 84% at +10, 92% at +20 and 99% at +50. On the days
  where τ sits in that last segment, the raw probability averages 4–5% at every threshold and the realised rate is
  0.1–0.8%.
- **The Platt step shrinks the level but cannot restore the shape.** It is fitted per threshold on a nearly
  constant input. Then the monotone running minimum ties the thresholds: on most days the published +50 bp
  probability *is* the +20 bp probability.
- **The literature's drivers are not the cause either, but the model lacks most of them.** Section 4 checks reserve
  demand, settlement timing, tax and quarter-end interactions and TGA with issuance against the model's nine inputs and the
  registry's lags: one is absent (the calendar), three are partly carried. They explain the quarter-end miss, not the
  flat curve; they are remedies 6 to 8.
- **The features rank well.** The raw +5 bp probability, used as a score for +20 and +50 bp events, ranks them
  better (AUC 0.94 and 0.91) than the raw +20 bp probability does for +20 bp events (0.70). The information is in the
  features and the lower quantiles; the tail law discards it.
- **Targets and class imbalance matter second.** Nothing is fitted above the 95th percentile, and there are 20 and 4
  events at +20 and +50 bp over the window, so no per-threshold step could learn a tail from them. All four +50 bp
  events fall before 2019-10-03, when the law's ceiling was still small (a top knot of +23 to +101 bp), and the model
  put 0% to 4% on them.

## 1. Predicted and realised exceedance rates by threshold

Mean forecast probability against the realised rate, h = 1, 1,873 scored days. *Ratio* is the threshold's value over
the +5 bp value; a calibrated curve would show the realised column's ratios.

| τ (bp) | Events | Realised rate | Mean raw (after PID) | Mean published (after Platt) | Mean climatology | Mean persistence-logistic |
|---|---|---|---|---|---|---|
| +5 | 140 | 7.5% | 10.9% | 9.6% | 11.4% | 7.8% |
| +10 | 61 | 3.3% | 7.0% | 4.7% | 4.2% | 3.2% |
| +20 | 20 | 1.1% | 5.1% | 2.2% | 1.5% | 1.5% |
| +50 | 4 | 0.21% | 3.7% | 1.6% | 0.43% | 0.57% |

| Ratio to +5 bp | +10 | +20 | +50 |
|---|---|---|---|
| Realised | 0.44 | 0.14 | 0.029 |
| Raw | 0.65 | 0.46 | 0.34 |
| Published | 0.49 | 0.23 | 0.17 |
| Climatology | 0.37 | 0.13 | 0.037 |

The realised rate falls 35-fold from +5 to +50 bp. The raw probability falls 3-fold and the published one 6-fold.
The same shape holds at h = 2 to 5 (`horizons.*.by_threshold` in the record).

The paired comparison at the two headline thresholds, h = 1, pooled over all scored days, climatology minus the
published model (positive favours the model), with the 90% interval:

| τ (bp) | Brier skill vs climatology | Climatology − published, Brier | 90% interval |
|---|---|---|---|
| +5 | +30% | +0.0212 | [+0.0155, +0.0273] |
| +10 | +10% | +0.0031 | [+0.0012, +0.0053] |

The model beats climatology at +5 and +10 bp. At +20 and +50 bp the published records carry no pooled skill figure and
this page computes none; the phase 2 verdict in PLAN.md already records that climatology beats the model's exceedance
probabilities there. What the table above shows is the mechanism: the climatology column is nearer the realised rate
than the model's raw and published columns at +20 and +50 bp.

## 2. Reliability by threshold, regime and pressure-day type

The CORP reliability diagram (the isotonic fit of the outcome on the forecast, `corp_reliability_curve`), h = 1,
all scored days, published probabilities (`reliability.*.corp_steps_final`; the raw probabilities' steps are beside
them in the record). A calibrated forecast has each step's observed rate equal to its forecast range.

| τ (bp) | Steps | Lowest step: forecast range → observed (days) | Highest step: forecast range → observed (days) |
|---|---|---|---|
| +5 | 20 | 0–3.2% → 0.6% (846) | 70–83% → 82% (17), then one day at 95% → 1 |
| +10 | 10 | 0–4.4% → 0.5% (1,319) | 40–62% → 75% (4) |
| +20 | 8 | 0–0.7% → 0 (253) | 18–21% → 14% (7); the 4.5–18% step holds 155 days and observes 5.2% |
| +50 | 3 | 0–2.0% → 0.15% (1,353) | 4.0–8.9% → 0.9% (110) |

The raw (pre-Platt) probabilities at +50 bp make **one** step: the isotonic fit finds no ordering in them, so the
curve is a horizontal line at the base rate (0.21%) across forecasts of 0 to 8.9%. At +20 bp they make six steps
and the busiest (63 days, forecasts of 16% to 35%) observes 9.5%. At +50 bp the published probabilities average 1.0%, 2.9% and 4.8% in the three steps against observed
0.15%, 0.24% and 0.91%: 5× to 12× too high. At +5 bp the diagram follows the diagonal from about 14% upward and
over-forecasts below it.

By regime (h = 1; published mean probability → realised rate, events in brackets):

| Regime | +5 bp | +10 bp | +20 bp | +50 bp |
|---|---|---|---|---|
| 2018–19 (375 days) | 26% → 27% (102) | 11% → 10% (39) | 4.7% → 3.7% (14) | 2.0% → 1.1% (4) |
| 2020 (251) | 9.4% → 1.6% (4) | 6.4% → 1.2% (3) | 3.4% → 0.4% (1) | 3.3% → 0 (0) |
| 2021–23 (748) | 3.2% → 0 (0) | 2.5% → 0 (0) | 1.4% → 0 (0) | 1.4% → 0 (0) |
| 2024 (250) | 2.6% → 2.0% (5) | 1.6% → 0.8% (2) | 0.8% → 0 (0) | 0.8% → 0 (0) |
| 2025–26 (249) | 11% → 12% (29) | 4.2% → 6.8% (17) | 1.0% → 2.0% (5) | 0.9% → 0 (0) |

The published probability at +20 and +50 bp is nearly the same number in each regime (1.4% in 2021–23 at both, 0.8%
in 2024 at both, 0.9–1.0% in 2025–26). The regime moves the level; the threshold barely does. In 2025–26 the upper
thresholds are under-forecast at +20 bp (1.0% against 2.0%, five events).

By pressure-day type (h = 1, published probability → realised):

| Day type | +5 bp | +10 bp | +20 bp | +50 bp |
|---|---|---|---|---|
| ordinary (1,595 days) | 9.4% → 6.4% | 4.6% → 2.4% | 2.2% → 0.6% | 1.6% → 0.06% |
| month end (158) | 9.9% → 10% | 5.1% → 7.0% | 2.3% → 2.5% | 1.7% → 0 |
| tax date (89) | 12% → 15% | 5.2% → 6.7% | 2.2% → 3.4% | 1.6% → 1.1% |
| quarter end (31) | 13% → 29% | 6.8% → 19% | 2.2% → 13% | 1.7% → 6.5% |

On ordinary days the +20 and +50 bp probabilities are over-forecast 4× and 27×; at quarter end every threshold is under-forecast, 2× to 6×. The
published +20 bp probability is 2.2% on both kinds of day. That is the flattening in its practical form: the curve
does not tell a quarter end from an ordinary Tuesday above +10 bp. Quarter-end counts are small (31 days, 4 events at
+20 bp, 2 at +50 bp), so these are descriptive.

The paired Brier differences against climatology by regime and day type, with intervals, are in
`reliability.*.by_regime` and `by_day_type` of the record at +5 and +10 bp. At +20 and +50 bp the record has the
rates and probabilities only, and the tables above are all the evidence this page offers there.

## 3. How the flattening arises

### 3a. The law (the main cause)

`ml._law_knots` builds seven knots: the five fitted quantiles at 0.05, 0.25, 0.5, 0.75, 0.95, plus a bottom and a top
knot at the training residual range about the median (`anchor + min(residuals)`, `anchor + max(residuals)`), widened
by the PID. P(> τ) is a straight-line inverse through them. Everything above the 0.95 quantile is one segment
carrying exactly 5% of mass.

| Check (h = 1) | Result |
|---|---|
| Largest spread in the window | +315 bp on 2019-09-17 |
| Scored days whose last segment is wider than 100 bp | 1,558 of 1,873, the first on 2019-10-03 |
| Top knot, deciles over days | the 10th percentile is +72 bp; every later decile is +289 to +301 bp |
| Last-segment width, median day | about 298 bp, a constant density of about 0.017 percentage points per bp |
| Days with τ inside the last segment: share, mean raw probability, realised rate | +5: 76%, 4.8%, 0.8% · +10: 83%, 4.6%, 0.8% · +20: 87%, 4.5%, 0.5% · +50: 93%, 3.9%, 0.1% |
| Median ratio raw P(> 50) / P(> 10) when both lie in the last segment | 0.86 (realised ratio of the rates: 0.07) |

So the curve between q95 and the top knot is a ramp of slope 0.05/298 per bp. Over +5 to +50 bp it loses 0.75 points of
probability, against a realised fall from 7.5% to 0.2%. One day (2019-09-17) fixes the top knot for every later forecast: the expanding training window keeps its residual.
The timing is the evidence (the knot jumps at the first refit after that day); the page does not isolate the residual itself.

Before the spike entered the sample the opposite held: the top knot was small (+23 to +101 bp on the four event days) and the law gave
exactly zero above it. All four +50 bp events are in that period, and the model assigned them 0% (twice), 2% and 4%.

### 3b. The recalibration step

The Platt step (`pressure.recalibrated`) fits `logit(p)` per threshold on the model's own earlier forecasts. With a raw
input that is almost constant (3a), the fit has no slope to learn: it can only move the level. It lowers the means
(7.0% → 4.7% at +10 bp, 5.1% → 2.2% at +20 bp, 3.7% → 1.6% at +50 bp) and leaves the shape. Then `recalibrated`
makes each curve non-increasing in τ by a running minimum.

| τ (bp) | Days the step is the identity | Days the published value equals the next threshold's | Blocks fitted |
|---|---|---|---|
| +5 | 252 | 1 | 78 |
| +10 | 252 | 19 | 78 |
| +20 | 252 | 1,562 | 78 |
| +50 | 408 | – | 0 |

(Identity days are the warm-up: the step is identity until 250 pairs hold 5 events.) No Platt curve is ever fitted at
+50 bp: the four events never reach the minimum of five. The published +50 bp probability on a day is the smaller of
that day's raw +50 bp value and its published +20 bp value, so it is the +20 bp value on 1,562 of 1,873 days. The +20 bp
and +50 bp columns of the published record are one column for most days. Last-block slopes at +10 and +20 bp are 1.36
and 1.35: the step is expanding a compressed signal, not correcting a mean.

### 3c. The features

The features are not what flattens the curve. As scores for the *same* event, h = 1:

| Event | AUC of the raw probability at its own threshold | AUC of the raw +5 bp probability | AUC of the published probability | AUC of persistence-logistic |
|---|---|---|---|---|
| > +5 bp (140) | 0.90 | 0.90 | 0.90 | 0.88 |
| > +10 bp (61) | 0.85 | 0.91 | 0.83 | 0.81 |
| > +20 bp (20) | 0.70 | 0.94 | 0.79 | 0.69 |
| > +50 bp (4) | 0.10 | 0.91 | 0.43 | 0.41 |

The same quantile fits, read at a lower threshold, rank an upper-threshold event much better than the exceedance read
at that threshold. The +50 bp row rests on four events and means little beyond the 0.10, which is the zero forecasts
of 3a on those days.

### 3d. The training targets and class imbalance

The model is fitted to the spread itself at five quantile levels; no fit sees a level above 0.95 and nothing is
fitted to an exceedance label (`predict_stress`: "Nothing here was fitted to a `stress_gt_*` label column"). What a
threshold above q95 gets is the tail law of 3a. The events behind each threshold over the window are 140, 61, 20 and 4,
and the first scored day at which five events had been seen was 2018-11-30, 2018-12-31, 2019-04-30 and never.
Imbalance therefore bites twice: the quantile levels carry no tail information, and the recalibration has nothing to fit a tail
with. A per-threshold remedy trained on these events inherits the same scarcity.

## 4. The drivers the literature names

Scope addition (Eleonora's ruling on #373, 7 October 2026): check the flattening against the drivers
`docs/pivot/literature.md` names, show for each whether the model's inputs carry it as of the decision instant, and
name the ones the model lacks as candidate remedies for #374. This section reads declarations, not scores: the model's
inputs are `GBM_FEATURES` of `scripts/pressure_model_v1.py`, the lags are the registry's (`metadata/sources.json`), and
no figure here is new. The decision instant is 16:00 New York on day D, for a target at D + h.

The model reads nine inputs: `reserve_balances`, `sofr_p25`, `sofr_p75`, `sofr_volume`, `spread_bps`, `tbill_13w`,
`tbill_4w`, `tga` and `treasury_settlement` (the last only at h = 1; it is scheduled one business day ahead, so it is not public at a longer horizon).
No calendar column enters the distributional model.

What each input is, as of 16:00 on D:

| Input | Source field | Newest value public at 16:00 on D |
|---|---|---|
| `sofr_p25`, `sofr_p75`, `sofr_volume` | `nyfed_sofr` | day D−1's, final at 15:00 on D (lag: one business day) |
| `spread_bps` | SOFR less IORB | IORB is available at 16:15 on its own date, after the decision, so the newest row with both is D−1's |
| `tbill_4w`, `tbill_13w` | `treasury_bill_rates` | quote date available at 16:30 on its own date, so D−1's |
| `reserve_balances` | `WRESBAL`, weekly (Wednesday level) | dated on a Wednesday and public five calendar days later at 16:30: the newest is 6 to 12 days old |
| `tga` | `WTREGEN`, weekly (Wednesday level) | the same five-calendar-day lag, so 6 to 12 days old |
| `treasury_settlement` (h = 1 only) | `treasury_auctions`, scheduled availability | the settlement of D+1, announced the day before at 15:00; the aggregate of bills, coupons and SOMA add-ons |

| Driver | Status | Which inputs carry it, and how | What is absent |
|---|---|---|---|
| Reserve-demand state | partly carried | `reserve_balances` (a level, 6 to 12 days old), `sofr_p25`, `sofr_p75` and `sofr_volume` (the 25th to 75th percentile spread of SOFR, one business day old) and `spread_bps` | the ratio of reserves to bank assets, a reserve-demand slope or elasticity (the NY Fed's monthly series is in no registry source), the ON RRP balance (declared but off in the published panel: `on_rrp` maps to `RRPONTSYD`, which the registry refuses, #45), EFFR less IORB (`effr_minus_iorb_bp`, declared, read by no published declaration), the 1st and 99th SOFR percentiles (`SOFR_p1`, `SOFR_p99` are registry fields, not inputs) and any regime state |
| Payment and settlement timing | partly carried | `treasury_settlement`, the day's aggregate, at h = 1 only | the bill, coupon and SOMA split (`treasury_settlement_bills`, `_coupons`, `_soma` are panel columns the model does not read), the settlement-day flags of #97 (`settlement_day`, `settlement_day_when_depleted`, composed features no declaration reads), and Fedwire payment data (monthly, not in the registry). At h = 2 to 5 no settlement input at all |
| Tax and quarter-end interactions with tightness | absent | none. `quarter_end`, `tax_date` and `days_to_month_end` are calendar columns known before the decision instant, and the model does not read them (they enter the direct candidates of `DIRECT_FEATURES`, not `GBM_FEATURES`); there is no interaction with tightness either | the three calendar columns, `quarter_end_window` (#140), and their products with a tightness measure |
| TGA and issuance | partly carried | `tga` (a level, 6 to 12 days old) and `treasury_settlement` (gross, h = 1) | net issuance, the change in the TGA, its interaction with reserves, `dealer_treasury_position` (the FR 2004 total, declared in `FEATURE_FIELDS`, not read) and the settlement split |

How each bears on the flattening, from the tables in sections 1 and 2:

- **Tax and quarter-end.** This is the driver the flattening hides most plainly. At quarter ends the published +10, +20
  and +50 bp probabilities are 6.8%, 2.2% and 1.7% against realised 19%, 13% and 6.5% (31 days: descriptive), and the
  +20 bp probability is the same 2.2% on a tax date, a month end and an ordinary day. A model without the calendar cannot
  tell them apart; with the law of 3a it could not tell them apart at the upper thresholds even if it knew the date.
- **Reserve-demand state.** The regimes in section 2 are the reserve-demand regimes in outline: the published probability
  tracks the level of pressure from regime to regime (26% in 2018 to 2019, 3.2% in 2021 to 2023 at +5 bp), so the weekly
  reserves level and the SOFR percentile spread carry the slow state. What they lack is a state variable: in 2025 to 2026
  the +20 bp probability is 1.0% against 2.0% realised, and the table cannot say whether that is the reserves ratio moving.
- **Settlement timing and TGA with issuance.** The model has the gross settlement the day before at h = 1 and a stale TGA
  level. It has neither the split that separates a dealer-financed bill settlement from a coupon settlement, nor any
  change in the TGA. Nothing in this page measures whether they would help: the check in 3c shows the information to rank
  events is already in the features, not that these drivers are missing from it.

**These drivers are not the cause of the flattening.** The cause is the law (3a). Adding any of them moves the lower
quantiles and so the ranking, which 3c shows is already good (AUC 0.94 at +20 bp for the raw +5 bp probability). They
cannot lift a probability above the 5% that the last segment carries. They are remedies for the level and the
quarter-end miss in section 2, and they come after the fitted tail (remedy 1) or beside it, not instead of it.

## Not checked, or for Eleonora

- **The data window.** Nothing after 2025-12-31 is scored. The 2026 behaviour of the curve was not read; the cause in
  3a is structural (the law's top knot), so I expect it to hold, but this page does not show it.
- **What would have been the top knot without 2019-09-17.** Not measured: it would be a counterfactual model, which
  belongs to a remedy directive (declared before scoring).
- **h = 2 to 5.** The record carries them with the same shape (the last segment, the ties and the AUC pattern); the
  tables above are h = 1 only, and the bootstrap intervals are drawn at h = 1 only.
- **The +20 and +50 bp pooled figures** are diagnostic. The published records treat those thresholds by event list
  (`docs/decisions/pressure-probability.md`), and nothing here is a skill claim at them.
- **Whether a tail may have a ceiling.** The remedies below touch the ruling of #63 (`docs/decisions/tail-shape-floor.md`:
  repo pressure has no hard ceiling). That is hers.

## Candidate remedies

Each is a separate directive, to be declared (the candidate, the threshold set, the windows, the decision rule) before
anything is scored, and each would face both benchmarks, paired, split by regime and day type, under
`docs/decisions/pressure-probability.md`. None changes the live record without her approval. In order of how directly
they answer a cause above:

1. **A fitted tail for the PID law (3a).** Replace the residual-range top knot with a fitted exceedance tail
   (the opt-in generalised-Pareto continuation already in `ml.py` is not wired to the PID path) so that mass above q95 decays with τ.
   Open question for the directive to declare: the tail's shape floor, given #63.
2. **A conditional chain across thresholds (3a, 3d).** Model P(> τ₂ | > τ₁) with a logistic on the features, fitted on
   the days above τ₁, and set P(> τ₂) = P(> τ₁)·that ratio. It fits each step on more events than a direct +50 bp fit
   and cannot cross thresholds. The AUCs in 3c say the +5 bp probability already carries the ranking.
3. **One shared recalibration slope across thresholds (3b, 3d).** Fit the Platt (or a beta calibration) pooled over
   thresholds with a threshold offset, so the +20 and +50 bp steps borrow the +5 and +10 bp events.
4. **Direct probability models at the upper thresholds (3d).** Logistic or gradient-boosted classifiers at +20 bp; #114
   already found them behind persistence-logistic at +5 and +10 bp.
5. **Stop printing a distinct +50 bp probability where it is the +20 bp value (3b).** A presentation change with no model
   change: publish the column as a tie, or drop it from the pooled table. It claims nothing new.
6. **Calendar and tightness interactions (tax and quarter-end interactions with tightness; section 4).** Add `quarter_end`,
   `tax_date`, `days_to_month_end` and their products with a tightness measure to the funding declaration's inputs. All
   are known before the decision instant. It faces the quarter-end miss of section 2 and needs the tail of remedy 1
   to move the upper thresholds at all.
7. **A reserve-demand state (reserve-demand state; section 4).** Add what the model lacks: the ON RRP balance in
   its depletion form (#88 declared it), `effr_minus_iorb_bp` (#98) and, if it can be downloaded as of its release, the
   NY Fed reserve demand elasticity. Each is a data or input decision that is hers.
8. **Settlement and TGA with issuance (payment and settlement timing; TGA and issuance; section 4).** Replace the gross
   settlement with the bill, coupon and SOMA split, add the change in the TGA and its product with reserves, and the
   settlement-day flags (#97).

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
for h in 1 2 3 4 5; do OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/exceedance_flattening_diagnosis.py walk --panel /tmp/funding_panel.csv --horizon $h --output /tmp/walk_h$h.json; done
PYTHONPATH=src python3 scripts/exceedance_flattening_diagnosis.py assemble --panel /tmp/funding_panel.csv --walks /tmp/walk_h1.json /tmp/walk_h2.json /tmp/walk_h3.json /tmp/walk_h4.json /tmp/walk_h5.json --output docs/runs/v1_flattening_diagnosis.json
```

| Cause | Check | Where in the record |
|---|---|---|
| 3a, the law | the last segment's width, the day it widens, τ inside it, the raw ratio | `horizons.*.mechanism.law`, `peak_spread` |
| 3b, the recalibration | identity days, ties, fitted blocks and their slopes | `horizons.*.mechanism.recalibration` |
| 3c, the features | AUC at each threshold, raw, published, benchmark and the +5 bp score | `horizons.*.mechanism.discrimination` |
| 3d, targets and imbalance | events, first day with five events, share of days with q95 below τ | `horizons.*.mechanism.targets`, `class_imbalance` |
| Section 1 and 2 | rates, bins, regime and day-type splits, paired Brier | `horizons.*.by_threshold`, `reliability` |
