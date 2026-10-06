# Decision: the final test, pre-registered

**Status: a draft for Eleonora (#150), in force once she merges it.** It fixes the design of the final test before any
locked day is scored. #151 opens the lockbox once and runs exactly what is frozen here. Her two rulings of
3 October 2026 on #216, on the reading of "within the interval of the best" and on the CRPS target, are recorded
below ("The reading of the selection rule" and "The test").

**The success criterion is the CRPS cell,** since her ruling of 4 October 2026 on #221 (below, "Amendment,
4 October 2026: the full-range test is the primary cell"): the published distribution (#169's gbm with nested PID)
against as-of persistence, by CRPS, at h = 1, on the 169 scored days from 2026-01-02 to 2026-09-03. It is
near-blind, not blind. **Every other cell is reported only** and cannot pass or fail the test: CRPS at horizons 2 to
5, and every leap and threshold cell (the plain leap, the leap onset, the pressure leap, +5 and +10 bp).

The leap test (the frozen dynamic logit, recalibrated by recency-weighted Platt, on the plain leap at h = 1, against
both of #139's baselines) was the primary cell from #216's merge until that amendment. The dynamic logit and the
six-candidate selection below stay as they are: they are the chosen model for the jump question, which is now
secondary.

Her request, 2 October 2026: "Build the simple pressure model with the scarcity state, fix its design in advance, then
open the 2026 lockbox once. If it beats the S-curve on days when pressure starts, you have a real forecasting result. If
not, you still have the case study." "The S-curve" means the persistence-logistic baseline (her clarification of
2 October 2026 on #150).

## What is frozen

- **Primary cell:** `crps, h = 1`
- **Model:** `dynamic_logit`
- **Calibrator:** `platt_recency`
- **Declaration checksum:** `28ad819321d50a44b50adf69f78af1fbe28d6c4f6a9a813544e13d06deed4432`
- **Code:** the model is `ml.dynamic_logit_exceedance` under `ml.DYNAMIC_LOGIT_SETTINGS` (#137), with the inputs of
  `scripts/pressure_dynamic_logit.py`'s `DYNAMIC_FEATURES`: the latest spread, reserves as the scarcity state, the
  scored day's quarter end, month end and tax date, the Treasury coupon settlement, each scheduled term times the
  scarcity state, and the lagged index (Kauppi–Saikkonen, persistence chosen on the grid by penalized likelihood at
  each refit). At horizons 2 to 5 the settlement and its interaction drop, because they are not public at the decision
  instant. The one recalibration step is recency-weighted Platt
  (`probability_calibration.walk_forward("platt_recency", …)`, half-life 504 scored days), applied walk-forward to the
  model's raw probabilities.
- **Commit:** the code on `main` at `019d1d062e2c133437d453e28c54e412677a8435`, with this record's pull request. The
  run is `scripts/final_test_preregistration.py`, whose `_dynamic_logit` runner is the frozen model.
- **The checksum** is `scripts/final_test_preregistration.py declaration`. It covers:
  - the inputs, the calibrator and its constants;
  - *J_h* at every horizon, the onset and leap-onset calm lengths, and the minimum event count;
  - the fold grid and the interval;
  - the sha256 of the source of every top-level definition the model, the calibrator, the leap targets, the leap
    baselines and the backtest reach in their own files;
  - the cells of the test and the role of each (`CELLS`, `PRIMARY_CELL`): the CRPS cell at h = 1 is primary, every
    other cell is reported only. These were added by the amendment that made the CRPS cell primary, which moved this
    checksum from #216's `5f084e7568f242bc76b6faa34fdcae2cb0ca786d328ca86d1f1ccf00385c0449`. Without them the
    declaration is byte-for-byte #216's, and a test checks that.

  `tests/test_final_test_freeze.py` fails if any of these changes after this record merges.

- **CRPS declaration checksum:** `d0847824027e80e06392b7ba641908cd83a60e38d21ceffff6b9d9d57cf14b59`
- **CRPS sensitivity seed:** `1970125677`
- **The CRPS checksum** is `scripts/final_test_preregistration.py crps-declaration`, added by the amendment of
  4 October 2026 (point 4). It is separate from the leap test's. It covers the CRPS test as set out under
  "Amendment, 4 October 2026, before any opening", with her rulings of the same day on #221: the labels and the
  block-10 sensitivity interval under its declared seed, then the primary cell at h = 1, the cells and their roles,
  and the claim.

The commands, on the published panel rebuilt from the tracked fixtures (digest `4ddc3882…`), and on the two scratch
panels the candidates were measured on:

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output V11.csv
PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py candidate --name NAME --panel PANEL --output OUT/NAME.pickle
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py calibrator --panel PUB.csv --runs OUT --output OUT/calibrator.json
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py select --panel PUB.csv --runs OUT --calibrator platt_recency --output OUT/selection.json
PYTHONPATH=src python3 scripts/final_test_preregistration.py declaration
```

`PANEL` is `V11.csv` (digest `4137d0ad…`) for `scarcity_calendar` and `v1_1`, `EW.csv` (digest `f74536e7…`, the
panel #172 was measured on) for `direct_logistic_sofr_p1`, and `PUB.csv` for the other three. numpy 2.4.6 and
scikit-learn 1.9.1 (`/opt/rmm-venv`).

## The amendments, in the order she made them

All are Eleonora's, made on 3 October 2026 before the lockbox is opened, and relayed by the orchestrating session on
#150.

1. **The onset definition.** #150's onset days are #209's at-risk days: every scored day whose previous five panel
   days were all at or below +5 bp, whatever its outcome. The onsets are the events within that group, and the
   leap-onset target is amended the same way. Five calm days, as #139 declared; the calm length is not changed after
   seeing results. #209's one-day variant (#160's definition) is reported beside it, descriptive only. *Reason:*
   #139's group held only days that turned out to be onsets, so every outcome in it was 1, and the Brier score there
   rewarded a higher forecast, sharper or not. The amended group is mostly calm days, so its score mostly measures
   false alarms.
2. **The selection score.** The model is chosen by plain-leap Brier at h = 1, at #139's *J₁*, on all pre-2026 days,
   from walk-forward (out-of-sample) forecasts on the test's own fold grid. Onset-day Brier, on the at-risk group, is
   reported beside it as descriptive only. *Reason:* item 1 of #150 used onset-day Brier, left over from an earlier
   draft. When the plain leap at h = 1 became the primary cell, the selection rule was not updated to match.
3. **The candidate list, closed at six; a fixed simplicity ranking; one recalibration step for all.** The scarcity
   state is not required. Every candidate is scored after the same single recalibration step, applied to its raw
   probabilities. For the published v1 and v1.1 that step replaces their out-of-fold recalibration. For the stacked
   combiner it is applied once, to the combiner's output. *Reason:* the two leads left standing by the "Publish?" round
   (#168, #172), and the model already published, are tested on equal terms with the earlier candidates. With a
   common step, no candidate wins because of how it was calibrated. With a ranking fixed now, "simplest" cannot be
   argued after the scores are seen.
4. **Which calibrator is "#138's winning method".** One calibrator for every candidate, among isotonic, Platt, beta and
   recency-weighted Platt. The choosing score is the published v1's plain-leap Brier at h = 1, at *J₁*, on all
   pre-2026 days, walk-forward, from its raw probabilities. Platt is the default. Another method replaces it only if
   its paired gain over Platt has a 90% interval excluding zero; if several do, the largest gain wins. *Disclosure*,
   as she recorded it: before the rule was written, the orchestrating session had read #210's summary and #212, but
   not this cell. *Reason:* #138 merged without naming a single winner.
5. **The calibrator-selection cell is computed, not read.** It was computed by the run that drafted this record, with
   the command above. It was not read from #210, #212 or their comments.
6. **No overlap with the live record.** This test scores no day after the panel end, 2026-09-03. The live record of
   #215 has no day this test scores: its first logged day falls after 2026-09-03, and its script refuses any earlier
   day.

## The choice, on pre-2026 evidence only

Every figure below is on the published fold grid at h = 1. The scored days are 2018-06-29 to **2025-12-31**, 1873
days with 164 plain leaps at *J₁* = 3 bp. Walk-forward, expanding window, refit every 21 scored days, decision 16:00.
**No locked day is scored**, and each run refuses one. Intervals are 90% stationary-bootstrap intervals, 2000
replications, block length 2.

**The calibrator.** Published v1's raw plain-leap probability (the distributional gbm before any recalibration), with
each calibrator fitted walk-forward. Gain = Brier(Platt) − Brier(method).

| Calibrator | Brier | Gain over Platt |
|---|---|---|
| isotonic | 0.0811 | +0.0006 [−0.0002, +0.0014] |
| Platt (default) | 0.0817 | – |
| beta | 0.0815 | +0.0002 [−0.0002, +0.0005] |
| **recency-weighted Platt** | **0.0805** | **+0.0011 [+0.0008, +0.0014]** |

Only recency-weighted Platt's gain has an interval excluding zero, so the rule chooses it.

**The model.** Each candidate's raw plain-leap probability, recalibrated once by recency-weighted Platt. The best is
the lowest Brier. "Versus the best" = Brier(best) − Brier(candidate). Under the paired reading she ruled on (see
"The reading of the selection rule"), a candidate is within the interval of the best when that paired interval
reaches zero.

| Rank | Candidate | Brier, raw | Brier, recalibrated | Versus the best | Within |
|---|---|---|---|---|---|
| 1 | #128's scarcity-conditioned calendar (logistic, state alone, four levels) | 0.0843 | 0.0789 | −0.0044 [−0.0068, −0.0021] | no |
| 2 | **#137's dynamic logit** | 0.0787 | **0.0745** | best | **yes** |
| 3 | v1's direct logistic + `sofr_p1` (#172) | 0.0846 | 0.0788 | −0.0043 [−0.0065, −0.0021] | no |
| 4 | the published v1 (#169) | 0.0889 | 0.0805 | −0.0060 [−0.0105, −0.0014] | no |
| 5 | #117's v1.1 (`joint`) | 0.0868 | 0.0790 | −0.0045 [−0.0086, −0.0003] | no |
| 6 | the stacked combiner (#137, as measured for #168) | 0.0777 | 0.0767 | −0.0023 [−0.0042, −0.0002] | no |

The dynamic logit has the lowest Brier, and every other candidate is worse than it with an interval excluding zero.
The highest-ranked candidate within the interval of the best is therefore the dynamic logit.

**Descriptive only; these choose nothing.** Onset-day Brier at +5 bp on #209's at-risk group (1586 days, 27 onsets) and
on the one-day variant (1734 days, 47 events). Plain-leap Brier on the leap-onset at-risk group (1366 days, 64 leap
onsets). Each is after the same recalibration step.

| Candidate | +5 bp, at-risk group | +5 bp, one-day variant | Plain leap, leap-onset at-risk group |
|---|---|---|---|
| scarcity-conditioned calendar | 0.0179 | 0.0285 | 0.0492 |
| dynamic logit | 0.0163 | 0.0261 | 0.0440 |
| direct logistic + `sofr_p1` | 0.0146 | 0.0238 | 0.0477 |
| published v1 | 0.0173 | 0.0299 | 0.0470 |
| v1.1 | 0.0174 | 0.0302 | 0.0461 |
| stacked combiner | 0.0159 | 0.0262 | 0.0459 |

**Context only, not the test.** On these pre-2026 days, the frozen model against the two leap baselines on the primary
cell: +0.0052 [+0.0004, +0.0095] against calendar climatology, and +0.0073 [+0.0018, +0.0122] against the
persistence-logistic (baseline minus model; positive favours the model). These days chose the model, so this is not
evidence that it will pass. Only the locked period can say that.

**#160, folded in (context for the test, not a cell of it).** The published v1 against the persistence-logistic, on
#155's whole-bp labels, at h = 1, 2018-06-29 to 2025-12-31 (#209's worked example, `scripts/onset_at_risk_example.py`).
Brier(persistence-logistic) − Brier(v1):

- At-risk group: +0.0003 [−0.0009, +0.0014] at +5 bp, and −0.0005 [−0.0010, +0.0001] at +10 bp.
- One-day variant: −0.0014 [−0.0034, +0.0006] at +5 bp, and −0.0010 [−0.0017, −0.0003] at +10 bp.

## The reading of the selection rule

**Eleonora's ruling, 3 October 2026, on #216.** "Within the bootstrap interval of the best" means the paired reading:
a candidate is within when the 90% interval of its paired Brier difference from the best reaches zero. Under it every
candidate but the dynamic logit is outside, so **the dynamic logit (#137) is the frozen model.**

- **The reading was fixed after both outcomes had been shown.** Under the paired reading the rule chooses the dynamic
  logit. Under the unpaired reading (a candidate is within when its Brier lies inside the 90% bootstrap interval of the
  best's own Brier, [0.0643, 0.0849]) every candidate is inside, and the highest-ranked, #128's scarcity-conditioned
  calendar, would have been chosen.
- **Why the paired reading.** The project's evidence rule is paired comparison: a headline claim "is paired, carries a
  bootstrap interval" (`CLAUDE.md`, "Benchmarks"). The unpaired interval mostly measures day-to-day variation in the
  Brier, so it barely separates candidates.

**The CRPS target, her ruling of the same day.** Both readings choose a direct model of the event, which has no
predictive distribution, so it has no CRPS. Target 2 is kept as drafted: the published distribution (#169's gbm with
nested PID) against as-of persistence, reported only. It is **the published model, not the chosen model.** Her
amendment of 4 October 2026 made it a second primary test, and her ruling of the same day on #221 made its cell at
h = 1 the primary cell (below).

## The test (#151)

**The period.** The near-blind tier, 2026-01-01 to 2026-09-03 (`lockbox.md`), opened once by Eleonora. No day after
2026-09-03 is scored. Every model is refitted walk-forward on the same fold grid as above, with the same constants, so
the 2026 forecasts continue the pre-2026 walk.

**The targets, in this order.**

1. **Small leaps (the primary target until the amendments of 4 October 2026; now reported only).** #139's as-of
   leap at #139's *J_h*, exactly as merged
   (`docs/decisions/pressure-probability.md`, "Onset view and small-leap targets"). The jump is measured against each
   forecast's as-of anchor, never the day before. *J_h* is fixed by #139's percentile rule on 2018-06-29 to
   2025-12-31: 3 bp at h = 1, and 4 bp at h = 2 to 5. Also on this target: the leap onset, on #209's at-risk
   leap-onset group, and #139's pressure leap (a leap that ends above IORB), which is secondary.
2. **Absolute numbers.** The CRPS of the full forecast distribution of the spread, every day, paired against as-of
   persistence (the distribution benchmark in `CLAUDE.md`). The dynamic logit is a direct model of the event and has no
   predictive distribution. The CRPS cell is therefore the published distribution (the gbm with nested PID, #169),
   **the published model, not the chosen model**, against as-of persistence. Since the amendments of 4 October
   2026 its cell at h = 1, on the window's 169 scored days, is **the primary cell** (below).
3. **The original thresholds.** +5 bp, then +10 bp, with the onsets on #209's at-risk group, kept for continuity.
   Reported only.

**The comparators.**

- **Leap targets:** both of #139's named baselines.
  - *The persistence-logistic* ("the S-curve"): a logistic regression of the plain-leap event on two inputs, both read
    at the forecast's as-of anchor: the latest as-of jump and the latest as-of spread level. It is fitted walk-forward
    on the same fold grid, with no other inputs and no interactions (`onset.leap_persistence_logistic`).
  - *Calendar climatology:* the walk-forward leap frequency by `metadata/evaluation_splits.json` day type
    (`onset.leap_calendar_climatology`).
- **+5 and +10 bp:** calendar climatology and the persistence-logistic, as `pressure-probability.md` declares them.
- **The distribution:** as-of persistence. If Eleonora meant a different S-curve, for example a reserve-demand sigmoid,
  she corrects this before #151.

**The metrics.** Brier on each event target and CRPS on the distribution, each paired against its comparators, with
the 90% stationary-bootstrap interval. Horizons 1 to 5.

**The success criterion: one primary cell, the CRPS cell** (amended twice on 4 October 2026; see the amendments
below). The published distribution against as-of persistence, by CRPS, at h = 1, on the window's 169 scored days.
It **passes** when the mean paired difference (persistence − published) is above 0 **and** its 90% lower bound is
above 0. Otherwise it fails, labelled "worse" when the 90% upper bound is below 0 and "not distinguishable"
otherwise. Every other cell is **reported only** and cannot pass or fail the test: CRPS at horizons 2 to 5, the plain
leap at every horizon, the leap onset, the pressure leap, and +5 and +10 bp. The plain leap at h = 1, at *J₁* = 3 bp,
is still scored as declared above: the frozen model's Brier against **each** named baseline's, with each paired
difference's 90% stationary-bootstrap interval. It decides nothing.

**Too few events.** Each event target has the minimum event count #139 already declared: **20 events** in the scored
period (`onset.MINIMUM_EVENTS`). Below it, that target is reported as inconclusive, with no claim either way. The
plain leap at h = 1 below 20 events is reported with its estimate and interval and labelled **inconclusive**; it
no longer decides the test. CRPS has no minimum, because every day counts. Events in the locked period are counted only when #151 scores it, never before.

**Secondary metrics.** The all-days Brier on every event target, and the false-alarm level on calm days. That level is
the mean forecast probability on the days of #209's at-risk group whose outcome is 0. It is a mean with no
cut-point, so no threshold has to be chosen for it. 2026 is largely a calm, reserve-management regime.

**The split.** Every cell is split by regime and by pressure-day type, as every published comparison is. The split is
reported, and it decides nothing.

## Recorded with the design

- **The target was changed partly because of what is known about 2026.** `lockbox.md` publishes the locked period's
  event counts (5 days above +5 bp, none above +10 bp), and public Fed commentary describes 2026 as calm. The leap
  target was added knowing that, though no model was scored on 2026.
- **The 90% interval is the project's standard,** fixed in advance and not chosen for this test.
- **The leap is measured on signed jumps:** all daily changes, not up-days only, per #139.
- **#139's pressure leap** (a leap ending above IORB) is reported as a secondary target.
- **The claim wording, if the test passes:** "the published model's one-day-ahead forecast of the full distribution
  of SOFR − IORB was more accurate than as-of persistence over January to September 2026". It never says "warns of
  stress". (Until the amendments of 4 October 2026 the claim was the leap test's: "forecasts as-of jumps in
  SOFR − IORB better than calendar climatology and the persistence-logistic".)
- **Framing.** The CRPS cell is the primary test because Eleonora is interested in the full forecast distribution,
  not in jumps. The leap and the +5 and +10 bp results, ties included, are reported next to it. Neither a leap
  forecast nor a range forecast is a stress warning.
- **No threshold is chosen by looking at 2026.** *J_h*, the calm lengths and the minimum event count all come from
  pre-2026 data or from earlier rules, and are fixed above. Counting events in the locked period, to choose a threshold
  or for any other reason, is not allowed before #151 scores it.
- **Labels are on whole basis points** (#155), so the test is scored on the corrected labels.
- **`_refuse_locked` is a fixed boundary** (recorded on #279, Eleonora's ruling of 6 October 2026, #269 item 20).
  The selection run's own lockbox check, `final_test_preregistration._refuse_locked`, refuses any scored day on or
  after 2026-01-01. That date is part of the test's definition, not of the lockbox: the final test's selection is
  defined on data through 2025-12-31, and it stays so whatever the lockbox later opens (the near-blind tier was
  opened on 2026-10-05, and the selection is unchanged). The check is not under the declaration checksums, because
  it is not among the definitions they hash; `RefuseLockedTests` in `tests/test_final_test_freeze.py` protects it,
  with its recorded mutation. The frozen script is not edited to say this.

## Amendment, 4 October 2026, before any opening

Eleonora's amendment, posted on #151 on 4 October 2026 and relayed by the orchestrating session. It was made before
the lockbox was opened. Directive #220 writes it into this record and extends the freeze. **Her later amendment of
the same day (next section) makes the CRPS cell the one primary cell and the leap test reported only.** What stays
from this section: the near-blind disclosure, the CRPS test with its pass rule, labels and block-10 sensitivity, and
the extended freeze. Points 1 to 3 are kept below as she made them, as amended there.

**The reason.** At the pre-2026 leap rate (164 plain leaps in 1873 scored days), the 169 scored days of the window
give about 169 × 164 / 1873 ≈ 14.8 expected leap events. The minimum is 20. The count of 169 comes from the panel's
dates only. No 2026 outcome was read to make it.

1. **A second primary test: CRPS.** The CRPS of the published distribution, exactly as published in #169, against
   as-of persistence, on all 169 scored days of the window. **Pass:** the published distribution's CRPS is lower,
   and the 90% paired interval of the difference excludes zero. The claim, if it passes: "the published range
   forecast beats as-of persistence on the near-blind 2026 days". It never says "warns of stress".
2. **The leap test is unchanged.** The frozen dynamic logit, recency-weighted Platt, the plain leap at h = 1, both
   baselines, and a minimum of 20 events. Below the minimum it is reported with its estimate and interval and labelled
   **inconclusive**. The live record (#215) continues it.
3. **The two tests are separate claims.** Each is reported on its own. Neither can stand in for the other.
4. **The freeze is extended** to the published distribution's declaration and code, and to the CRPS comparison
   path, by a pull request merged before any opening (#220). The CRPS declaration checksum is pinned above ("What is
   frozen"). The leap test's checksum is unchanged.
5. **Disclosure.** These 2026 days were already scored inside pooled CRPS aggregates of the archived records from
   before #169 (the CV+ records). No 2026-only CRPS was published. The CRPS test is therefore **near-blind, not
   blind**.

**What the CRPS checksum covers.** `scripts/final_test_preregistration.py crps-declaration` prints it, and
`tests/test_final_test_freeze.py` fails if it moves:

- **The published distribution,** as `docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json`
  declares it: the gbm (`ml.fit_gradient_boosted_quantiles`, the model `compare --model-b gbm` scores) on the nine
  funding features, with conformal PID under nested walk-forward selection (`recalibration.NestedFoldPid`), its
  grid, its fallback and its fixed constants. A test checks that this declaration equals the published record's.
- **The benchmark:** as-of persistence on `spread_bps`.
- **The fold grid:** expanding window, minimum history 61, refit every 21 scored days, decision 16:00, end
  2026-09-03.
- **The CRPS path:** the paired comparison (`baseline.paired_model_comparison`), the CRPS (`metrics.crps_from_quantiles`
  through the comparison's `crps` loss), the paired stationary bootstrap (`metrics.stationary_bootstrap_interval`) at
  90%, 2000 replications, mean block length 2, and seed 1970125677. The seed is `compare`'s own, derived from the
  published panel's digest and the two sides. It is the seed of the published CRPS record.
- **The sensitivity interval:** the same 90% paired stationary bootstrap, 2000 replications, at mean block length
  10, with seed 1970125677, declared now (her ruling on #221, (b), below). It is reported beside the primary interval
  and decides nothing.
- **The labels:** pass, "not distinguishable" and "worse" (her ruling on #221, (a), below).
- **The window:** 2026-01-01 to 2026-09-03, 169 scored days.
- **The primary cell, the cells and the claim** (her later ruling of the same day, in the next section): the horizon
  (h = 1), every cell's role (`CELLS`, `PRIMARY_CELL`) and the claim wording.
- **The cell and the pass rule:** `crps_cell` and `crps_verdict` in the same script. The cell scores the frozen
  run's paired differences on the window's days only. It is split by regime and by pressure-day type, and the split
  decides nothing. It refuses while the near-blind tier is locked, and refuses a record that is not the frozen run.
- **The code:** the sha256 of the source of every top-level definition these reach in their own files, as for the
  leap test.

**The commands the opening run types,** on the published panel rebuilt as above (`PUB.csv`, digest `4ddc3882…`),
once Eleonora has opened the near-blind tier in `metadata/lockbox.json`:

```
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python -m repo_model.cli compare PUB.csv \
  --registry metadata/sources.json --decision-time 16:00 --minimum-history 61 --refit-every 21 \
  --splits metadata/evaluation_splits.json --end 2026-09-03 --loss crps \
  --model-a persistence --feature-a spread_bps \
  --model-b gbm --calibration-b conformal_pid_nested \
  --feature-b reserve_balances --feature-b sofr_p25 --feature-b sofr_p75 --feature-b sofr_volume \
  --feature-b spread_bps --feature-b tbill_13w --feature-b tbill_4w --feature-b tga \
  --feature-b treasury_settlement --report OUT/crps.json
PYTHONPATH=src python3 scripts/final_test_preregistration.py crps --report OUT/crps.json --panel PUB.csv \
  --output OUT/crps_cell.json
```

**Her ruling of 4 October 2026 on #221,** relayed by the orchestrating session, accepts three choices for the CRPS
cell and adds two reporting rules:

1. The cell comes from **one walk-forward `compare` to 2026-09-03** (the command above), with its per-origin
   differences cut to the window's 169 days.
2. The interval is **a fresh stationary bootstrap on those 169 differences**, with the published settings (mean
   block length 2) and the fixed seed 1970125677.
3. **Pass:** the mean of (persistence − published) is above 0, and the 90% lower bound is above 0.

Reporting only. These add no change to the rule, so a pass stays exactly as in point 3:

- (a) A non-pass is labelled **"not distinguishable"** if the 90% interval contains 0, and **"worse"** if its upper
  bound is below 0. An interval above 0 around a mean that is not above 0 is a fail, labelled **"not
  distinguishable"** (her ruling of 4 October 2026 on #221, in the next section). It is not a pass under the rule.
- (b) The same 90% interval is **also reported with mean block length 10**, with seed 1970125677 (pinned above as
  "CRPS sensitivity seed"; it is the primary interval's seed, so only the block length differs). It is a sensitivity
  report only and decides nothing.

`crps_cell` writes both intervals, `crps_verdict` labels the cell from the primary interval only, and `crps_result`
turns the label into the test's pass or fail. All three are under the CRPS checksum.

**The day count.** The window holds 169 scored days. The count is of the published panel's dates from 2026-01-01 to
2026-09-03, read from its date column only (`window_dates`). `tests/test_final_test_freeze.py` checks it that way,
and reads no 2026 outcome. Nothing in #220 scores a 2026 day.

## Amendment, 4 October 2026: the full-range test is the primary cell

Eleonora's ruling on #221, 4 October 2026, relayed by the orchestrating session. It was made before any locked day
was scored. Directive #220 writes it into this record and regenerates both checksums.

1. **The success criterion is the CRPS cell:** the published distribution (#169's gbm with nested conformal PID)
   against as-of persistence, at **h = 1**, over **2026-01-01 to 2026-09-03** (169 scored days, 2026-01-02 to
   2026-09-03). The pass rule is the one ruled on #221 that morning: the mean paired difference (persistence −
   published) above 0 **and** the 90% lower bound above 0, with the "not distinguishable" and "worse" labels and the
   block-length-10 sensitivity reported. **Horizons 2 to 5 are reported only.** `compare` scores one day ahead, so
   the frozen command (above) is the primary cell's.
2. **Every leap and threshold cell is reported only** and cannot pass or fail the test: the plain leap, the leap
   onset, the pressure leap, +5 and +10 bp. The dynamic logit and the six-candidate selection stay in the record as
   they are, as the chosen model for the jump question, which is now secondary.
3. **The claim wording, if the test passes:** "the published model's one-day-ahead forecast of the full distribution
   of SOFR − IORB was more accurate than as-of persistence over January to September 2026". It never says "warns of
   stress".
4. **Recorded with the amendment:**
   - Made on 4 October 2026, before any locked day was scored.
   - *Reason:* Eleonora is interested in the full forecast distribution, not in jumps.
   - *Known when deciding:* 2026 is calm (the lockbox record's counts: 5 days above +5 bp and none above +10 bp).
   - *Also seen before deciding, on pre-2026 data only:* the published CRPS record
     (`docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json`) split into each year's first
     169 scored days, 2019–2025. The lower bound was above zero in 4 of 7 years (2019, 2023, 2024 and 2025), and the
     model was clearly worse in 2022, so about 60% of 169-day windows passed. That 60% is how often a window passed in the years seen, which is the test's power if the model has the skill it showed then. It is not a base rate of false positives: under no skill the pass rate is the test's own false-positive rate, which this planning computation did not measure. (A wording correction proposed in #267, for Eleonora to review.) This was computed in a planning session
     with a stationary bootstrap at block length 2. It is context, not a figure for the record.
5. **Both checksums are regenerated.** Both declarations carry the cells and their roles (`CELLS`, `PRIMARY_CELL`),
   and the CRPS declaration also carries the horizon and the claim. The pins are above ("What is frozen"). Without the
   cells, the leap declaration is #216's, byte for byte.

**The edge case** (an interval above 0 around a mean that is not above 0) is a **fail**, labelled **"not
distinguishable"**. It is not a pass under the rule.

**What stays from the first amendment of the day:** the near-blind disclosure, the two tests as amended here (the
CRPS cell primary, the leap test reported only), the labels and the block-10 sensitivity. The leap test was the
primary cell from #216's merge until this amendment.

## Amendment, 4 October 2026 (second), before any opening

Eleonora's amendment, posted on #151 on 4 October 2026 and relayed by the orchestrating session, with her scope
comment of the same day on #222. It was made before the lockbox was opened. Directive #222 writes it into this record.
**It opens nothing, scores no 2026 day and reads no 2026 outcome.** It changes neither checksum: the leap test's and
the CRPS test's pins ("What is frozen") are as #221 left them. The CRPS cell stays the one primary cell; every leap
cell is reported only.

**1. Expected leap events, written down now.**

- The window has **169 scored days** (2026-01-02 to 2026-09-03), counted from the published panel's date column only
  (`window_dates`).
- The pre-2026 plain-leap rate at h = 1 at *J₁* = 3 bp, on the published fold grid (2018-06-29 to 2025-12-31), is
  **164 of 1873** scored days (0.0876).
- So the expected count on the window is 169 × 164 / 1873 **≈ 14.8 leaps, against the minimum of 20 events**
  (`onset.MINIMUM_EVENTS`). If the pre-2026 rate holds, P(≥ 20) **≈ 0.11** (Poisson).
- **That 0.11 assumes the average 2018–2025 leap rate.** Calm years had far fewer plain leaps in the same
  January–August stretch, recounted below. 2026 is known to be calm (the lockbox record's counts: 5 days above
  +5 bp, none above +10 bp), so the chance of reaching 20 is likely lower than 0.11.
- "Inconclusive" for the reported leap cells on the 2026 window is therefore **the expected outcome**, not a surprise.

Each pre-2026 year's plain leaps at h = 1, *J₁* = 3 bp, on scored days from 1 January to 31 August, on the published
fold grid. "At the year's rate" scales that year's January–August rate to the window's 169 days.

| Year | Scored days, Jan–Aug | Plain leaps | Expected on 169 days, at the year's rate | P(≥ 20), Poisson |
|---|---|---|---|---|
| 2018 (from 2018-06-29) | 45 | 10 | 37.6 | 0.999 |
| 2019 | 168 | 30 | 30.2 | 0.98 |
| 2020 | 168 | 8 | 8.0 | < 0.001 |
| 2021 | 167 | 2 | 2.0 | < 0.001 |
| 2022 | 167 | 3 | 3.0 | < 0.001 |
| 2023 | 167 | 2 | 2.0 | < 0.001 |
| 2024 | 168 | 2 | 2.0 | < 0.001 |
| 2025 | 166 | 24 | 24.4 | 0.84 |

2018's scored days start on 2018-06-29, so its row covers July and August only. The counts were recounted by the run
that drafted this section, on pre-2026 panel data only, with the commands below, and agree with the ones in her scope
comment (2020: 8; 2021–2024: 2 to 3 each). No 2026 day is read or counted except by date: the script refuses a run
whose scored days reach the near-blind tier, before any label is read.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py candidate --name dynamic_logit --panel PUB.csv --output OUT/dynamic_logit.pickle
PYTHONPATH=src python3 scripts/final_test_leap_counts.py --panel PUB.csv --run OUT/dynamic_logit.pickle
```

**2. Three outcome labels.**

- **"shown better"**: pass under the cell's rule.
- **"not shown"**: the 90% interval contains 0.
- **"shown worse"**: the upper bound of the 90% interval is below 0.

For the primary CRPS cell these are the labels already ruled on #221: "shown better" is its pass, "not shown" is
"not distinguishable", and "shown worse" is "worse", with the edge case as ruled there. The same three labels are
applied to each reported leap and threshold comparison. "Inconclusive" still applies below the minimum of 20 events.

**3. No substitute event target.** No other event target with more 2026 events (for example a lower threshold)
replaces the plain leap among the reported jump cells.
