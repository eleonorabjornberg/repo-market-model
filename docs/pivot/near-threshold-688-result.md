# A near-threshold bill input and a post-month-end window for the spread distribution (#688)

H5 (primary goal), research step 2 (add inputs one family at a time, with an ablation), and H2. **Exploration on development days, not a verdict**
(scoring protocol v1, #640): every interval below describes 2018-2025 and none decides anything. Nothing is published, neither input joins a
published declaration, no day after 2025-12-31 is scored and no day of the blind tier is read (`docs/decisions/lockbox.md`). These are inputs to the
spread distribution, not new +5 bp classification variants (paused).

The declaration (`metadata/near_threshold_688.json`) was committed before any number was computed. One amendment followed the first screen and is
recorded in the declaration itself: a screen statistic is reported only where its own strata hold the declared minimum, where the first wording applied
the minimum to the whole cell. The stricter reading is the one used throughout.

## What was done

- **The base.** #634's model has not landed, so the base row is the strongest spread-distribution row on main: the two-part model of #632 (gradient-boosted
  quantiles; a risk-date part and an every-day part), here refitted at the protocol's 23 levels in place of #632's 13. It is the **control**.
- **Input 1 (#676), the raw bill column.** `treasury_settlement_bills`, announcement-dated at the lead, added to the every-day inputs beside the as-of
  spread that those inputs already hold. The trees form the interaction themselves. The product flag (as-of spread 2 to 5 bp, and a bill settlement on the
  scored day) is what the screen measures, but it cannot be a model column: it mixes the as-of row with the scored day. This is a reading of the avenue, put
  to Eleonora below.
- **Input 2 (#677), a window flag.** `post_month_end_window`: 1 on the first three market days of a month, a function of the date and the holiday table, known in
  advance and declared a calendar feature for the run. Bridged persistence (the other form the avenue names) was not run; see below.
- **Screen** (`screen`): ordinary days, at each lead h = 1 to 5, with the as-of spread band and the scarcity state band as controls (Mantel-Haenszel
  stratified rate difference), pooled and by regime, with 90% stationary-bootstrap intervals.
- **Model test** (`walk`, `score`): each input added to the control's every-day part, 3 rows by 5 leads walked forward on the shared fold grid, scored with the
  scorer of scoring protocol v1 (`repo_model.scoring_protocol`: grid CRPS over h = 1 to 5, upper-tail twCRPS), paired with the control and with B1 and B2.
  Evidence: `docs/pivot/evidence/near-threshold-688/` (`report.md` has every table, `screen.json` and `score.json` the data).

## Screen: is there anything on the ordinary days?

Pressure rate on the ordinary days (`risk_gbm`'s risk-date rule, coupon clause on), input on against input off, at lead 1 and pooled over 2018-2025.
Differences are percentage points; intervals are 90%.

| input | cell | with | without | raw difference [90%] | stratified over spread band and scarcity state [90%] |
|---|---|---|---|---|---|
| bill settlement | as-of spread 2 to 5 bp | 13/44 (0.30) | 5/60 (0.08) | +21.2 [+8.3, +33.6] | +21.0 [+8.3, +33.4] |
| bill settlement | as-of spread above +5 bp (persistence) | 26/46 (0.57) | 26/63 (0.41) | +15.3 [+4.7, +26.1] | |
| bill settlement | all ordinary days | 631 input days | | +2.7 [+1.1, +4.5] | +2.9 [+1.4, +4.5] |
| first three market days | all ordinary days | 243 input days | | +4.2 [+0.8, +7.5] | +1.2 [−1.3, +3.8] |
| first three market days | as-of spread above +5 bp (persistence) | 16/35 (0.46) | 36/74 (0.49) | −2.9 [−21.8, +16.1] | |

- **Bill settlement.** The audit's near-threshold contrast reproduces on the pooled ordinary days, and the stratified difference equals the raw one: the
  as-of spread band and the scarcity state do not account for any of it. It shrinks with the lead (near band, raw: +21.2 at lead 1, +15.7 at 2, +15.6 at 3, +11.5 at 4, and not reported at 5, where the
  near band holds 29 days with a bill settlement). By regime it is a 2018-19 effect (stratified +9.2 [+2.7, +15.7] at lead 1); the 2025-26 regime holds 15 pressure days and its
  near-band cells are too thin to report, the stratified point +4.2 [+0.0, +8.9]. 2020, 2021-23 and 2024 hold 3, 0 and 2 pressure days between them: they can say nothing.
- **Post-month-end window.** At lead 1 the raw rise (+4.2) is plain persistence: stratified over the as-of band it is +1.2 [−1.3, +3.8], the persistence share 71% [33%, 190%], and
  given an as-of spread above +5 bp the rate with the window is not higher (0.46 against 0.49). At leads 3 to 5 the stratified difference is larger than the raw one (+5.1, +5.2, +5.0 against +4.2): it is not persistence there, and by regime it sits in 2018-19
  (+22.1 [+9.8, +34.7] at lead 3; 2025-26 is flat, −0.9 to +1.8 at every lead).
- The cells of the screen number 60, and 164 statistics carry an interval. Nothing is corrected for multiplicity. Every cell above rests on 82 ordinary pressure days,
  62 of them in 2018-19.

## Model test: do they improve the spread distribution?

Decision days 2018-06-29 to 2025-12-23 (their fifth target on or before 2025-12-31); every row has no law on the same two decision days (their every-day inputs were not public) and takes B1's there.
Grid CRPS in bp, averaged over h = 1 to 5. A pair is the reference's score minus the candidate's (positive favours the candidate); skill is that difference over the reference's mean;
bounds are the protocol's one-sided 95% (studentized stationary bootstrap, ruling 1; mean block 10, 10,000 draws).

| row | mean grid CRPS | against B1 (skill [95% bounds]) | against B2 | mean twCRPS above 0 bp |
|---|---|---|---|---|
| B1 as-of persistence | 2.3024 | | | 1.3789 |
| B2 calendar climatology | 2.5143 | | | 1.1261 |
| control (two-part, #632) | 1.8589 | +19.26% [+10.55%, +39.09%] | +26.07% [+16.98%, +34.86%] | 0.9134 |
| + bill settlement (#676) | 1.8609 | +19.18% [+10.47%, +38.81%] | +25.99% [+16.92%, +34.72%] | 0.9109 |
| + post-month-end window (#677) | 1.8397 | +20.10% [+11.59%, +39.30%] | +26.83% [+17.69%, +35.60%] | 0.9094 |

**Each input against the row without it** (the control; paired, grid CRPS):

| input | pooled | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| bill settlement | −0.10% [−0.54%, +0.28%] | −0.03% | +0.48% | −0.12% | −0.43% | −0.36% [−0.76%, −0.01%] |
| post-month-end window | **+1.03% [+0.44%, +1.64%]** | −0.08% | +0.31% | **+1.30% [+0.39%, +2.18%]** | **+1.74% [+0.80%, +2.65%]** | **+1.69% [+0.88%, +2.53%]** |

On the upper-tail twCRPS (the key secondary) neither input moves the score beyond its interval: bill settlement +0.27% [−0.40%, +0.94%], window +0.44% [−0.35%, +1.23%].

- **Bill settlement adds nothing.** Pooled it is level with the control (−0.10%), at no lead is its interval above zero, and by regime the only interval above zero is 2024 (+1.21% [+0.61%, +1.85%]), in a regime with 2 pressure days. The
  screen's near-threshold contrast is real on the ordinary days of 2018-19 but the trees do not turn it into a better distribution: the contrast rests on 13 pressure days with a bill settlement
  and 5 without, in a band the model already forecasts as uncertain.
- **The window flag helps, at h = 3 to 5, and not on the pressure days.** It gains +1.0% on the grid CRPS pooled (interval above zero), the gain growing with the lead, with an interval above zero at every pinball level but 0.05 and 0.95
  and on the median's absolute error (+0.95% [+0.27%, +1.64%]). By regime the interval is above zero only in 2021-23 (+2.45% [+1.42%, +3.66%]), a regime with no ordinary pressure day, and by pressure-day type only for the ordinary days
  (+1.55% [+0.66%, +2.38%]); it is exactly zero on quarter-ends (identical forecasts) and has no interval on tax dates (the difference cannot be studentized). So what the flag
  improves is the level of the spread in the first days of a month, which a calm regime has, and not the upper tail the screen asked about.
- **Both rows keep their lead over the benchmarks** (control against B1 +19.26%, with the window +20.10%): the inputs are measured against the control, and neither changes the standing against B1 or B2.
- Coverage is below nominal in every row (central 50%: 0.38 to 0.39; central 90%: 0.77 to 0.78), as it was for #632's two-part row. The inputs do not repair it.

## Re-score on the ruled interval (#804)

The intervals above were first computed with the percentile bootstrap that ruling 1 (Eleonora, 13 October 2026; PR #660, #739) replaced: #731 merged without
re-scoring after #695 brought in the studentized interval. They are now the scorer's own studentized stationary-bootstrap bounds, from the same walks refitted
on the same published panel (`4ddc3882…`), with the same 1,868 decision days, seed (688), 10,000 draws and block length. Every point value and the whole screen reproduce
byte for byte (`screen.json` is identical); only the interval ends moved. `score.json` and `report.md` in the evidence folder are the re-scored ones; the earlier bytes are in git history.

- **The headline survives, slightly wider.** Window flag, grid CRPS against the control: +1.03% [+0.44%, +1.64%] (was [+0.50%, +1.61%]); h = 3, 4, 5 still each above zero
  (+1.30% [+0.39%, +2.18%], +1.74% [+0.80%, +2.65%], +1.69% [+0.88%, +2.53%]). The bill input is still level with the control (−0.10% [−0.54%, +0.28%]).
- **One interval crossed zero:** the window flag's pinball loss at the 0.05 level, +1.09% [−0.03%, +2.23%] (was [+0.12%, +2.14%]). No other pooled, lead, regime or measure cell changed sign.
- **Against B1 and B2 the intervals are the asymmetric ones** (control against B1 +19.26% [+10.55%, +39.09%]; the percentile pair was nearly symmetric, [+8.36%, +28.35%]); the lower bounds rose, the upper bounds rose more.
- **Two pressure-day types lost their interval.** Quarter-end days: both inputs leave the forecast unchanged (difference exactly zero). Tax-date days: the difference is nearly constant and the scorer refuses to studentize it; the
  report says "no interval" there. No percentile figure stands in for it.
- The screen's own intervals (stationary bootstrap on rate differences) are not the scorer's paired test and are unchanged; ruling 1 does not cover them.

## Acceptance criteria

1. **Declaration committed before any number; tests first; as-of guards hold; any new guard has a recorded mutation.** `metadata/near_threshold_688.json` is the first commit of the branch. The readings
   and the as-of reads of both inputs are tested in `tests/test_near_threshold_688.py` (the test file was written before the script it tests); three guards each have a recorded mutation and the test that kills it, in that file's docstring.
2. **Each input screened with the as-of spread and the scarcity state as controls (partial, per lead, per regime, with intervals), then added to the spread-distribution model and scored with #660's scorer, paired, split by regime.** Above, and in `report.md`.
3. **How much of each effect is plain persistence (P | as-of spread > 5 bp).** The first table, and the persistence share column of `report.md`.
4. **Variants counted (#567); no published figure moves; the full suite and the three `--check`s.** Variants tried: two (the two inputs), against one control; the screen is not a model variant (60 cells, counted above).

## Not checked, or for Eleonora

- **Question (the input's form):** the bill input is the raw column beside the as-of spread, not the product flag the avenue describes. A product column would need ml.py to build it from the as-of read and the scored day's. If the product is wanted, that is a model change and hers.
- **Question (the grid):** the control was refitted at the 23 levels, not mapped from #632's 13 by the linear law (the question #655 leaves to her). Refitting changes the control's own figures from #632's.
- **Not run: bridged persistence** (#677's other form: the risk part's forecast for the unseen turn day as the persistence input at h = 1). It feeds one model's forecast into another's input and leaves the one-row design the as-of rule reads. It is an avenue for her decision.
- **The window flag's gain is not the avenue's claim.** #677 expected it to catch ordinary pressure days; the screen finds that at lead 1 it is persistence and at leads 3 to 5 only 2018-19, and the model gain is in calm regimes. Whether a calm-regime gain is worth a place in #634's model is H5 step 2 after #634 lands.
- The screen's ordinary days are #631's (the risk-date rule the models serve). #682 (open) defines "not a risk date" once; if its definition differs, the screen's cells move.
- The outcome is the panel's `spread_bps`, not first-published vintages (protocol section 11). The as-of scarcity-state split of protocol section 7 was not run. The first decision day (2018-06-28) has no B2 and is not scored.
- The near-blind tier (2026-01-01 to 2026-09-03) is ordinary history and is not used here, so as to keep the days comparable with the control; the same measurement on those days is a choice for later, and only as description.
- The progress page's variant count (`scripts/emit_progress.py`) reads `metadata/spread_distribution_*.json` and does not see this declaration; reported as a finding.
