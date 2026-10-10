"""Gradient-boosted conditional quantiles: the `ml` extra's one module.

Owned by **Track B (model and evaluation)**. This is the *only* module in the
package allowed to reach numpy or scikit-learn, and it may reach them only from
inside the functions that use them --- `AGENT_CONTRACT.md`'s working rules and
`tests/test_dependency_boundary.py`, which fails this file for a module-level
`import sklearn`. The rule is not stylistic: `repo_model`'s two conformance
walks (`tests/test_contract.py::ForecastInterfaceCoverageTests` and
`tests/test_baseline.py::ExceedancePredictorCoverageTests`) import every module
of this package, so a module-level optional import would turn the *core* suite
red on every checkout without the extra rather than skipping one test file.

What is here is one model in two shapes, the two shapes this repository already
has interfaces for:

* `FittedGradientBoostedQuantiles` / `fit_gradient_boosted_quantiles` --- the
  forecast interface (`baseline.FittedForecastModel`).
* `gbm_exceedance` --- the exceedance interface
  (`baseline.ExceedancePredictor`), derived from the same fitted quantiles and
  not fitted apart from them.

**One fit per contract level.** `HistGradientBoostingRegressor(loss="quantile",
quantile=level)` is fitted once for each level in `contract.QUANTILE_LEVELS`,
on the one-step-ahead design `fit_arx` builds --- last observed spread plus the
declared regressors --- minus the intercept, which a tree ensemble does not
need and cannot use. The design, the imputation of an unobserved regressor by
its training-window mean, and the refusal to coerce an absent column to `0.0`
are `fit_arx`'s and are reached through `baseline`'s own helpers rather than
restated here: two spellings of one design is how two models stop being
comparable.

**The two traps this model has, named.**

*Quantile crossing.* Five independent fits are not constrained to be ordered,
and on a small or heteroscedastic window they are not: the 0.25 fit can land
above the 0.50 fit on a particular row. Reported as-is, that is a predictive
distribution whose CDF decreases, and every consumer downstream --- the
`P(Y > tau)` monotonicity `event_eval` checks, CRPS, the interval coverage
statistic --- reads it as a broken law. **The rearrangement used here is
sorting**, which for a finite level grid is exactly the rearrangement of
Chernozhukov, Fernandez-Val and Galichon: the sorted vector is a valid quantile
function, and it is never further from the true quantile curve than the crossed
one it replaces. It is applied in `_rearranged`, which is the single place a
predicted vector is produced, so `predict`, `point_forecast`, the fitted
residual sample and `predict_stress` all read the *same* rearranged vector and
cannot disagree about it.

*Non-determinism.* `HistGradientBoostingRegressor`'s `early_stopping` default is
`"auto"`, which turns early stopping **on** above 10 000 rows and then draws an
internal validation split; with no `random_state` that split moves between fits
and two fits of the same model on the same rows return different numbers. A
published record produced that way cannot be re-scored. Both are therefore set
explicitly here --- `early_stopping=False` and a fixed `random_state` --- rather
than left at a default that changes behaviour with the size of the panel.

**The band's calibration, opt-in (B22).** Every level is fitted in-sample, and a
boosted quantile fit is tight on the rows it was fitted on, so the outer
`0.05`-`0.95` band under-covers out of sample: the published backtest at
`--minimum-history 61` puts its nominal 90% at well under that. `calibration=
"conformal"` is conformalized quantile regression (Romano, Patterson and Candes,
2019), done causally inside the one training frame a fold hands over:

* the frame is split by date. The most recent `calibration_share` of its rows
  are **calibration rows**; the **fit rows** are the frame's prefix through the
  first calibration row's anchor (`asof.InformationRule.anchor`) -- label
  observability, the rule the fold loop trains by, so no fit row's target is
  one the forecaster could not have had when the calibration slice opens;
* every level is fitted on the fit rows **only**, and never refitted on the
  union afterwards: a refit scores the calibration rows with a model that has
  seen them, which is the in-sample residual tail again and voids the
  finite-sample guarantee;
* each calibration row is scored `s = max(Q_lo - y, y - Q_hi)` off the
  rearranged vector, its feature row the as-of observation at its own decision
  instant (`asof.InformationRule.observation`) -- the rule a scored day's
  feature row is chosen by, so a calibration score is at the horizon the
  backtest scores at -- and the `ceil((1 - alpha)(n + 1))`-th
  smallest score is the **widening**, with `1 - alpha` the declared band's own
  span. `Q_lo` moves down and `Q_hi` up by it, and it may be negative. The
  interior levels are untouched; an outer level that a negative widening would
  carry past its neighbour stops at the neighbour, so the vector stays
  non-decreasing; and the two outer knots `predict_stress` reads move with the
  band.

`calibration="none"` is the default and is the model every published record was
produced with: no split, no widening, and no float operation on a reported
vector that the uncalibrated model did not already perform.

**Cross-conformal, opt-in (B25).** Split-conformal pays for its band with a
quarter of the frame and the unobservable labels before it: every level, the median and so the CRPS are
fitted on the rows that are left. `calibration="cross_conformal"` is CV+
(Barber, Candes, Ramdas and Tibshirani, 2021) applied to conformalized quantile
regression, done causally inside the one training frame a fold hands over:

* **the reported vector is the full fit's.** Every level is fitted on all of
  the frame's rows exactly as `none` fits them, and the interior levels are
  reported as `none` reports them, bit for bit;
* the frame is split, **by date and never shuffled**, into `calibration_folds`
  contiguous blocks. Each block's **excluding model** is fitted on the other
  blocks' rows, by label observability in both directions: a row before the
  block trains only if its label was observable at the block's first decision
  instant, a row after it only if the block's last label was observable at that
  row's own decision instant. A design pair trains only if its origin and its
  target both do, so no pair's target is a held-out row or an unobservable
  one. The rows it may not train on are **holes** to
  it -- a lag or a GARCH variance that would read one is missing, by the rules
  below -- so an excluding model reads nothing of its block through a feature
  either;
* each held-out row is scored `s = max(Q_lo - y, y - Q_hi)` by its own block's
  excluding model, from its own as-of observation, as a calibration row is
  under `conformal`. A held-out row with no such observation inside the frame
  -- the frame's first rows, before any label or declared field is observable,
  or before a lag has rows to read -- has no forecast to score and is
  not scored;
* a forecast's band is CV+'s: with `alpha = 1 - (Q_hi level - Q_lo level)` and
  `n` scores, the lower edge is the `floor(alpha (n + 1))`-th smallest of
  `Q_lo_-k(i)(x) - s_i` and the upper the `ceil((1 - alpha)(n + 1))`-th
  smallest of `Q_hi_-k(i)(x) + s_i`, every excluding model read at the
  forecast's own feature row. The full fit's outer levels move to those edges
  by `_calibrated`'s neighbour rule, and the tail knots `predict_stress` reads
  move with them.

Runtime is the full fit plus one fit per block, and every forecast reads each
excluding model once more.

**Per-held-out-row masking, opt-in (#78).** `docs/decisions/information-set.md`
(Method notes) accepts one bias in the cross-conformal calibrations: the frame
a fold hands over is masked at the **fold's** decision instant, so a declared
column slower than the target (the H.4.1 weeklies) can reach an excluding
model's training rows before its block with a value that was public at the
fold's decision but not yet at a held-out row's. `calibration_masking=
"held_out_row"` removes it for measurement:

* each held-out row's mask is the set of declared values on the training rows
  before its block that `InformationRule.frame` would hole at that row's own
  decision instant. Rows after the block are not masked: CV+ trains on them,
  labels included, by construction, and the Method note is about the declared
  columns before the block;
* the held-out rows of a block are grouped by their mask, and each group is
  scored by its own excluding model, fitted on the block's training pairs with
  that mask applied (a masked value is a hole, so it takes the model's fitted
  imputation, as any hole does). The group with the empty mask is the block's
  model as `None` fits it, bit for bit; a declaration with no column slower
  than the target therefore fits exactly what `None` fits;
* the band is CV+'s as before: each score is paired with the excluding model
  that produced it, so `calibration_blocks` may hold more than one model per
  block, each carrying its own rows' scores;
* the full fit, and so the reported interior, is untouched.

Refused under `none`, `conformal` and `conformal_asymmetric`, which train no
excluding model, and with `training_pairs="direct"` (#37): a direct pair reads
only what was public at its own target's decision, which comes before any
held-out row's after it, so there is nothing to mask. Runtime grows by one fit
per extra mask group.

**Asymmetric split-conformal, opt-in (B51).** B51 introduced this as the half of
`cross_conformal`'s change that is not the fit, on the reading that CV+ takes its
two edges from separate order statistics. **That reading was an equivocation;
see the taxonomy below (B54).** CV+'s two order statistics are over *one pooled
score* at the *band* rate, so `conformal` to `cross_conformal` changes the fit
and not the score, and `conformal_asymmetric` isolates a change `cross_conformal`
never made. What it is stands: `conformal` in everything but how the
calibration scores are reduced -- the same split, the same fit rows only and no
refit, the same feature rows, the same `calibration_share` -- and then:

* each calibration row keeps **two** scores, `s_lo = Q_lo - y` and
  `s_hi = y - Q_hi`, which are never pooled. `Q_lo` moves down by the
  `ceil((1 - lo)(n + 1))`-th smallest `s_lo` and `Q_hi` up by the
  `ceil(hi (n + 1))`-th smallest `s_hi`, with `lo` and `hi` the declared outer
  levels, exact by `_side_probabilities` -- for the declared grid, the
  `ceil(0.95 (n + 1))`-th of each. Either may be negative, and each goes through
  `_banded`, so an outer level a negative widening would carry past its
  neighbour stops there, as under `conformal`;
* **the guarantee claimed is per side, and two-sided by their sum.** Each rank
  is the one-sided split-conformal rank at that side's own miss rate, so under
  exchangeability `P(y < lower) <= lo` and `P(y > upper) <= 1 - hi`. The two
  misses are disjoint -- `_banded` keeps `lower <= Q_(2) <= Q_(k-1) <= upper` --
  so the two-sided miss is their sum, at most `alpha = 1 - (hi - lo)`, and not
  a union bound that gives anything away. With no ties each side also misses at
  least its rate less `1 / (n + 1)`, so coverage sits in
  `[1 - alpha, 1 - alpha + 2 / (n + 1)]`: one `1 / (n + 1)` looser above than
  `conformal`, in exchange for a statement about each side that `conformal`
  does not make at all -- its pooled score can spend the whole `alpha` below.
  **Not** `conformal`'s rank `ceil((1 - alpha)(n + 1))` applied to each side:
  that lets each side miss `alpha`, and the band only `2 alpha`;
* so it does **not** reproduce `conformal`'s figure when the two score sets
  coincide. It reduces to `conformal`'s *construction* -- equal widenings move
  the band exactly as `_calibrated` moves it -- at a higher rank;
* the per-side rank names a score only while `n >= p / (1 - p)` at the larger
  side probability `p`: **nineteen** calibration rows for the declared band, not
  `conformal`'s nine, and the fitter refuses below it;
* no tail: `tail` is refused with it, as under `cross_conformal`, because the
  tail's threshold is `conformal`'s single widening and is not wired here.

**The calibrations, taken apart (B54).** What each one varies, read off the code
-- fit rows; what is ordered; the rate a rank is taken at; the floor on scores
for the declared band; the guarantee claimed:

* `none` -- the frame; nothing; no rank; no floor; no guarantee.
* `conformal` -- the fit rows; one pooled score per calibration row, reduced to
  one scalar widening; the band's `alpha`; nine; band coverage `>= 1 - alpha`.
* `conformal_asymmetric` -- the fit rows; two signed scores per row, reduced to
  two scalar widenings; each side's own miss rate; nineteen; each side misses
  at most its own rate.
* `cross_conformal` -- the frame, plus one excluding model per block; edges
  `Q_lo_-k(i)(x) - s_i` and `Q_hi_-k(i)(x) + s_i` over one pooled `s_i`; the
  band's `alpha` on both edges; nine; band coverage `>= 1 - 2 alpha`.
* `cross_conformal_asymmetric` -- the frame, plus one excluding model per
  block; the same edges over two signed scores; each side's own miss rate;
  nineteen; each side misses at most twice its own rate.

Why that is two axes and not three:

* **The ordered quantity and the fit are one axis, not two.** A split fit is
  read once, so its scores reduce to a scalar widening of that one fit; a CV+
  fit has an excluding model per block, so its order statistic is an edge in
  level space with each model's own read at `x` inside it. A full fit moved by
  a scalar widening of out-of-block scores is neither: its scores come from
  models it is not, and it has no guarantee -- B25 recorded it as a mutation,
  not a calibration.
* **The rank rate and the score are one axis, not two.** A pooled score
  `max(Q_lo - y, y - Q_hi)` already counts both misses in one number, so it is
  ranked at the band's `alpha`; two signed scores count one miss each, so each
  is ranked at its own side's miss rate. Pairing them the other way round is
  the error `conformal_asymmetric`'s bullets refuse.
* **CV+'s rank is `conformal`'s, not a per-side one.** `floor(alpha (n + 1))`
  on `a - s_i` is `a - ` the `ceil((1 - alpha)(n + 1))`-th smallest `s_i`,
  since `n + 1 - floor(alpha (n + 1)) = ceil((1 - alpha)(n + 1))`. So where
  every excluding model agrees at `x`, `cross_conformal`'s edges are exactly
  `conformal`'s pooled widening: each edge is taken at the full band `alpha`
  on the pooled score, not at half of it and not at the side's own rate. Its
  two order statistics differ only through the excluding models' spread at
  `x`, which is the fit axis.
* **So the grid is square, and its fourth cell was empty.** Split or CV+,
  against pooled score at the band rate or signed scores at the side rates.
  `cross_conformal` is (CV+, pooled), not (CV+, separate); the queue sheet's
  "`cross_conformal` (full, separate)" was the equivocation, and "separate
  edges" named two different things in the two calibrations. The empty cell
  is `cross_conformal_asymmetric`, below. B51's published comparison of
  `conformal` with `conformal_asymmetric` therefore attributes nothing about
  `cross_conformal`'s lower misses: that change was the fit's.
* **CV+'s guarantee is the factor-two one.** Barber et al.'s CV+ bound is
  `1 - 2 alpha` less a K-fold term; `cross_conformal` claims no more, and
  `tests/test_ml.py` holds it to `1 - alpha` only on a stationary fixture,
  where it attains that.

**Asymmetric cross-conformal, opt-in (B54).** `calibration=
"cross_conformal_asymmetric"` is `cross_conformal` in everything but how the
held-out scores are reduced -- the same full fit reported, the same purged date
blocks and excluding models, the same held-out rows and feature rows, the same
`calibration_folds` -- and then:

* each held-out row keeps **two** signed scores off its own block's excluding
  model, `s_lo = Q_lo_-k(i) - y` and `s_hi = y - Q_hi_-k(i)`, never pooled;
* the lower edge is the `floor(lo (n + 1))`-th smallest of
  `Q_lo_-k(i)(x) - s_lo_i` and the upper the `ceil(hi (n + 1))`-th smallest of
  `Q_hi_-k(i)(x) + s_hi_i`, with `lo` and `hi` the declared outer levels exact
  by `_side_probabilities`, every excluding model read at the forecast's own
  feature row. The full fit's outer levels move there through `_banded`, and
  the tail knots move with them, as under `cross_conformal`;
* **the guarantee is CV+'s, per side.** CV+'s argument never uses that the
  score is two-sided: a miss above the upper edge means the test row's `s_hi`
  beats `s_hi_i` for at least `ceil(hi (n + 1))` rows, and the tournament bound
  gives `P(y > upper) <= 2 (1 - hi)` less the K-fold term; below, by the same
  count with `n + 1 - floor(lo (n + 1)) = ceil((1 - lo)(n + 1))`,
  `P(y < lower) <= 2 lo`. The reported band's misses are disjoint -- `_banded`
  keeps `lower <= upper` -- so the band's worst case is `1 - 2 alpha`, as
  `cross_conformal`'s is. The per-side statement is what is new, and it is
  CV+'s factor two weaker than `conformal_asymmetric`'s, exactly as
  `cross_conformal`'s band is than `conformal`'s;
* **its floor is nineteen held-out scores, derived.** `floor(lo (n + 1)) >= 1`
  exactly when `n >= (1 - lo) / lo`, and `ceil(hi (n + 1)) <= n` exactly when
  `n >= hi / (1 - hi)`: `_minimum_asymmetric_calibration_rows`' bound, which is
  that same `p / (1 - p)` at each side's probability. The fitter refuses below
  it, as `cross_conformal` refuses below nine;
* no tail, for `cross_conformal`'s reason (B53) twice over: the knot would be
  an order statistic over every excluding model, and now of a side score set
  no `conformal` widening ever formed.

**Volatility-scaled cross-conformal, opt-in (B-SCALED).** Job 657 found
`cross_conformal`'s over-coverage is not a uniform over-width: its band is far
too wide in calm stretches and too thin in stressed ones, sorted by a trailing
volatility known before each origin. A uniform shrink would deepen the stressed
under-coverage, so `calibration="cross_conformal_scaled"` divides the score by
a scale read at each row's own decision time. It is `cross_conformal` in the
fit -- the same full fit reported, the same date blocks and excluding
models, the same held-out rows and feature rows, the same `calibration_folds`
-- and then:

* **the scale.** `_trailing_scale`: the root mean square, about zero as the
  GARCH takes the changes, of the observed one-step spread changes into the
  `SCALE_WINDOW` rows ending at the **feature row**, floored at
  `SCALE_FLOOR_BPS`. A held-out row's feature row is its as-of observation,
  dated at its anchor, so the window ends at or before the last row whose
  spread was observable at that row's decision: every spread it reads was
  published by the decision that forecasts the row. A forecast's feature row
  is the fold loop's as-of observation, dated at the frame's last row. A window
  that ended at the target, or was centred on the feature row, or ran over the
  whole frame, would read spreads the forecaster did not have;
* **the score** is `r_i = |y_i - m_-k(i)(x_i)| / sigma(x_i)`, `m` the
  excluding model's rearranged median and `sigma(x_i)` the held-out row's
  scale. The residual, not CQR's `max(Q_lo - y, y - Q_hi)`: a boosted outer
  level with no volatility column does not widen with the regime, so CQR's
  score divided by a scale would still differ in law between a calm row and a
  stressed one. The residual about the median divided by the scale does not,
  when the scale tracks the regime -- which is the property this calibration
  is for;
* **the band** is CV+'s, at `cross_conformal`'s ranks, over
  `m_-k(i)(x) - sigma(x) r_i` and `m_-k(i)(x) + sigma(x) r_i`, every
  excluding model read at the forecast's feature row and `sigma(x)` that row's
  scale. The full fit's outer levels move there through `_banded`; the
  interior is the full fit's, bit for bit. The band is centred on the
  excluding models' medians: the fit's own skew in `Q_lo` and `Q_hi` does not
  reach the edges;
* **the guarantee is CV+'s**, `1 - 2 alpha` less the K-fold term: the scale is
  a fixed function of the history, fitted on nothing, so the scores are CV+
  scores of the one fixed map `|y - m(x)| / sigma(x)`;
* **rows with no scale are not scored.** A held-out row whose feature row has
  fewer than `SCALE_WINDOW` rows before it in the frame, or no observed change
  among them, has no scale and is left out, as a row with too few rows for its
  lags is. A forecast from such a row is refused (`ValueError`), never given a
  made-up scale;
* **a flat stretch takes the floor.** A window whose every observed change is
  zero has a root mean square of zero, and a score divided by it is infinite.
  `SCALE_FLOOR_BPS` is the smallest scale a window with any one-tick move can
  have, so a flat window is priced as the calmest non-flat one;
* no tail, for `cross_conformal`'s reason (B53).

**Partially scaled cross-conformal, opt-in (B-PARTIAL).** Job 662 scored
`cross_conformal_scaled` and found it over-corrects: calm now under-covers and
stressed over-covers, and centring on the median lost the fit's lower-tail skew
in calm stretches. `calibration="cross_conformal_partial"` is
`cross_conformal` in the fit and in the score, and scales only the conformal
correction, by less:

* **the score** is `cross_conformal`'s own, `s_i = max(Q_lo_-k(i)(x_i) - y_i,
  y_i - Q_hi_-k(i)(x_i))` off the held-out row's excluding model -- the fit's
  quantile edges, not the median -- divided by `f_i = sigma(x_i) **
  PARTIAL_SCALE_EXPONENT`, `sigma(x_i)` `_trailing_scale` at the held-out
  row's feature row: the same window, floor and purge argument as
  `cross_conformal_scaled`'s, and the same rule that a row with no scale is
  not scored;
* **the band** is CV+'s, at `cross_conformal`'s ranks, over
  `Q_lo_-k(i)(x) - f(x) s_i / f_i` and `Q_hi_-k(i)(x) + f(x) s_i / f_i`, every
  excluding model read at the forecast's feature row and `f(x)` that row's
  factor. The fit's own edges, and so its skew, are kept; only the correction
  moves with the regime. At an exponent of zero every factor is exactly one
  and the band is `cross_conformal`'s bit for bit on the rows both score; at
  one the correction is fully proportional;
* **no reference scale.** The rule as ruled is `(sigma / ref) ** gamma`. One
  `ref` is shared by every held-out row and the forecast, so it enters the
  edge only as `(sigma(x) / ref) ** gamma / (sigma(x_i) / ref) ** gamma =
  (sigma(x) / sigma(x_i)) ** gamma`: it cancels, and no value is declared for
  it. `f` is `sigma ** gamma` in basis points, which is `ref = 1 bp`, a unit
  and not a setting;
* **the guarantee is CV+'s**, for `cross_conformal_scaled`'s reason: `f` is a
  fixed function of the history, fitted on nothing, and the exponent was fixed
  before any fold was scored;
* no tail, for `cross_conformal`'s reason (B53).

**Lagged spread changes, opt-in (B23).** `spread_change_lags=k` adds `k`
regressors, `spread_change_lag_1` .. `spread_change_lag_k`: the change in
`spread_bps` between consecutive rows, the `j`-th ending `j - 1` rows before the
feature row, so lag 1 is the feature row's spread minus the row before it.

* **Where the prior rows come from.** The forecast interface hands a model one
  feature row, so the rows before it are the training frame's own: the fitted
  model keeps each frame row's date and spread, and reads a feature row's lags
  back by that row's *position* in the frame. The frame is what the fold loop
  handed over, ending at the anchor, and the feature row the loop builds is
  dated at that anchor -- so no row after the feature date is reachable from here at
  all, and a feature row the frame does not carry is refused rather than
  looked up somewhere else.
* **Between refits, the as-of history** (issue #34). Under `refit_every`
  above 1 a forecast after its block's first row has a feature row newer than
  the fitted frame. The rows between were public at its decision, so the fold
  loop hands the model the as-of frame at that decision (`with_history`), and
  the lags are read from it by the same rule: the fitted values are the
  block's, the history is the forecast's own. `positional_history` is the one
  reader, for the lags, the GARCH variance and the trailing scale alike, and
  `history_end` is what the fold loop checks is the anchor.
* **Inside the design, the same rule.** A training row's lags end at that row,
  never at its target: the change *into* the day being forecast is lag 0, and
  it is the target minus the autoregressive term. A calibration row's lags end
  at its as-of observation's anchor. One helper,
  `_spread_changes`, reads every one of them.
* **By row, not by calendar day.** A Monday's lag 1 is Friday's change, not a
  Sunday nobody observed.
* **A hole is missing, not bridged.** A row whose `sofr` or `iorb` is `None` has
  no spread, so every change touching it is missing and gets its fitted
  imputation, exactly as a declared regressor carried as `None` does. It is
  never differenced against the last observed row before it.
* **The first `k` rows of a frame start changes and are not design rows.** Their
  lags would reach before the frame, which is not a hole but no data, and
  imputing it would put a column of training means in every fit.

**A GARCH(1,1) variance, opt-in (B24).** `volatility_feature="garch11"` adds one
regressor, `garch11_variance`: the one-step conditional variance of the spread
change, fitted inside the one training frame a fold hands over.

* **The fit.** The innovations are the daily spread changes between consecutive
  fit rows, by row and taken as zero-mean. `f_p`, the variance of the change
  into row `p + 1` forecast at row `p`, is `omega + alpha * e_p + beta *
  f_(p-1)`, where `e_p` is the squared change into row `p` -- or `f_(p-1)`, its
  expectation, where that change touches a hole, and on the frame's first row,
  which has no change into it. `f_(-1)` is the mean squared observed change of
  the fit rows. `(omega, alpha, beta)` maximise the Gaussian quasi-likelihood of
  the fit rows' changes subject to `omega > 0`, `alpha, beta >= 0` and
  `alpha + beta < 1`, by a Nelder-Mead search written here in the standard
  library: the `ml` extra is numpy and scikit-learn, and an optimiser package
  is a dependency this block does not add.
* **Per fold, on the fit rows only.** Nothing is fitted on the panel: the
  fitter is handed one fold's frame and fits there, so two folds with different
  training ends fit different parameters. Under `calibration="conformal"` the
  parameters come from the fit rows alone, and the calibration rows are
  *filtered* with them -- the recursion run on through those rows -- never
  refitted on themselves.
* **The feature at row `t` is `f_t`.** It reads changes at or before `t`, and
  forecasts the change into `t + 1`: for a training row that is the change
  into its target, and it is never an input. A calibration row's variance is
  its feature row's; a forecast's is the feature row's, filtered through the
  history's own rows by position, the lag columns' rule.
* **Refused, never flattened.** Fewer than `GARCH_MINIMUM_CHANGES` observed
  changes among the fit rows, and a search that does not converge -- including
  a frame whose every observed change is zero, where omega runs to 0 and there
  is no maximum -- raise `ValueError`. A constant-variance column in their
  place would be a feature that says nothing, published under a declaration
  that says it was read.

Absent is the default and is today's gbm, bit for bit.

**An ARX one-step forecast, opt-in (B26).** `arx_feature="declared"` adds one
regressor, `arx_forecast`: the point forecast of `baseline.fit_arx` -- the
repository's one ARX fitter, the model `--model arx` runs -- fitted on gbm's
own declared regressors, exactly the columns `--model arx` gets from the same
`--feature` flags. `declared` is the only value: no new column enters a
declaration, and the purge is already sized over every column the ARX reads.

* **Per fold, on the fit rows only.** The ARX is fitted inside the one training
  frame a fold hands over, on the rows the gbm's own estimators are fitted on:
  the frame under `none`, the fit rows under `conformal`. Two folds with
  different training ends fit two ARXs; nothing is fitted on the panel.
* **The feature at row `t` is the ARX's forecast from `t`.** `FittedArx.
  point_forecast` reads row `t`'s spread and declared regressors and nothing
  else, so the column reads no row after `t`; for a training row that means its
  successor, its target, is never an input. What a training row does share
  with its target is the coefficients, fitted on pairs that include it -- the
  in-sample property the GARCH parameters and every imputation mean here
  already have. A calibration row's forecast is its feature row's, from the fit
  rows' ARX, never refitted; so is a forecast's.
* **Under `cross_conformal`**, each block's excluding model fits its own ARX on
  the one-step pairs whose two rows it may train on -- every pair outside its
  block and the purge gaps around it -- through `fit_arx`'s `origins`, so no
  pair spans the block. Its training rows, its held-out scores and its read of
  a forecast all use that ARX; the full fit's is never lent to it.
* **Refused, never substituted.** The ARX's own refusals are its own: too few
  rows for `fit_arx`'s default minimum, a singular design, a regressor
  unobserved on every row. They propagate as `fit_arx` raises them, and a
  forecast column is never filled in when the fit fails. Integration order
  `d = 0`: the target is a spread level, and the ARX is fitted on levels.

Absent is the default and is today's gbm, bit for bit.

**Direct (horizon-matched) training pairs, opt-in (#37).** The default design
is one-step pairs: row `p`'s own values train on row `p + 1`'s spread, and the
fitted model is then served the as-of observation, which sits two or more rows
before the scored day. `training_pairs="direct"` trains on the gap it is served
at instead. Each target row `t` is paired with the observation a forecast of
`t` reads -- `asof.InformationRule.observation` at `t`'s own decision instant,
every declared field at its latest row observable there -- and its lags and
GARCH variance end at `t`'s anchor, as a forecast's do. It is the read a
calibration row is already scored from, so under a calibration the fit and the
held-out scores are made at one horizon.

* **Guarded as a forecast is.** Every pair's read goes through
  `InformationRule.check`, the leakage and staleness guards a scored day's
  read goes through, and is refused with their exceptions. A target with no
  read at its decision -- the frame's first rows -- trains no pair.
* **Needs the run's rule.** `information` is required, under every
  calibration, `none` included, and its absence is `SplitError`.
* **Under the cross-conformal calibrations**, an excluding model trains a
  pair only if its target and every row its read touches are rows it may
  train on, by the rule its one-step pairs follow; `training_dates` lists
  all of them.
* **The ARX feature is unchanged**: `fit_arx` is a one-step model, fitted on
  its own pairs, and its forecast is a column read off the feature row.

Absent is the default and is today's gbm, bit for bit.

**A generalised Pareto tail, opt-in (B36).** `tail="gpd"` continues the law
`predict_stress` inverts above its top declared quantile with `_fit_gpd_pwm`'s
fitted tail, where the knot law has only one straight segment to the largest
residual ever seen and then an exceedance of exactly `0.0`.

* **The threshold is the reported top quantile.** The knot at `levels[-1]` of
  the law this model reports for the row, calibration included --- the value
  `predict` returns last --- and not the uncalibrated fit's.
* **The sample is the calibration rows' residual excesses above that same
  threshold.** Each calibration row is read from its feature row by the
  estimators fitted on the fit rows, exactly as its conformal score is, and its
  excess is its target less that row's *calibrated* top quantile, kept where
  positive. No fit row enters it, and the threshold the excesses are measured
  from is the one the tail is attached at: collecting them above the
  uncalibrated quantile and attaching the tail at the calibrated one would put
  a jump in the curve at the join.
* **Above the threshold** `P(Y > tau) = (1 - levels[-1]) * S(tau - threshold)`,
  `S` the fitted survival function. At the threshold that is `1 - levels[-1]`,
  which the knot law already returns there, so the curve does not jump; at and
  below it nothing changes at all.
* **Three states, recorded as `tail` and `tail_fit`.** A fitted shape
  (`fallback` false); `_fit_gpd_pwm`'s exponential fallback on fewer than
  `GPD_MINIMUM_EXCESSES` excesses (`fallback` true), which the early folds of an
  expanding window take; and **no excesses at all**, where there is nothing to
  fit, `tail_fit` is `None` under `tail="gpd"`, and the law is the default's
  bit for bit. That third state is not a shape of zero: an `xi` of `0.0` there
  would be indistinguishable from a fallback that saw nineteen excesses. A
  `backtest` record of a tail run carries each fold's state under
  `folds.tail`, through `tail_account` (B38), and an `exceedance-backtest`
  record does the same (B40).
* **A fourth state: a negative shape is floored at zero (#63).** Repo
  pressure has no hard ceiling, so a fit whose raw shape is negative takes
  `xi = 0.0` and the sample's mean excess as its scale, the exponential the
  fallback uses, and the record says `floored` and keeps the raw estimate. The
  tail never assigns probability zero above a level. This replaces B44's
  refusal at the lower bound; records written before it still carry
  `refused`. See `_fit_gpd_pwm`.
* **Refused under `none`, `cross_conformal`, `conformal_asymmetric`,
  `cross_conformal_asymmetric`, `cross_conformal_scaled` and
  `cross_conformal_partial`.** The last two for `cross_conformal`'s reason;
  their knots are also scaled per row.
  `none` holds nothing out, so its only sample is rows the estimators were
  fitted on --- an in-sample tail. `conformal_asymmetric` moves the two edges
  by two widenings and the tail's knot is `conformal`'s one.
  `cross_conformal_asymmetric` has both of the other two reasons. `cross_conformal`
  holds every row out in some block, and the coherent sample there is a
  different construction that is not wired; a mixed-provenance tail in the
  meantime would be worse than the refusal. `cli_eval` refuses the same three
  at selection, before a fit is attempted.
* **Why `cross_conformal` cannot simply be wired (B53).** `conformal`'s sample
  holds two properties at once: each excess is read by a map fitted on no row
  it measures, and that map --- `Q_hi` of the fit rows plus one widening --- is
  the very one the tail is attached at. Under CV+ no held-out row can have
  both. The knot the tail would be attached at is CV+'s upper edge, an order
  statistic of `Q_hi_-k(i)(x) + s_i` over *every* block's excluding model read
  at the forecast's row. Read at a held-out row's own feature row, all but its
  own block's model were fitted on that row's pair, feature row and target: an
  in-sample tail, as under `none`, diluted by one block in `calibration_folds`.
  The out-of-sample alternative, each row read by its own block's excluding
  model alone, is measured against a threshold that is not the attached one;
  and there is no per-block calibrated top quantile to measure against, since
  an `_ExcludingModel` keeps its pooled scores and CV+ never forms a per-block
  widening. Pooling five blocks' thresholds into one fit is the mixed
  provenance, and attaching it at CV+'s edge is the jump at the join. A
  coherent CV+ tail would have to be rebuilt per forecast row, from
  `Q_hi_-k(i)(x)` and each row's own excess, and so would no longer be the one
  per-fit `tail_fit` that `tail_account` records per fold: a redesign, not a
  wiring. `GpdCrossConformalSampleTests` holds the premise. `cli_eval`'s
  selection refusal names the first three; the fitter refuses
  `cross_conformal_asymmetric` itself.

Absent is the default and is today's gbm, bit for bit. The tail is stdlib
arithmetic.

Stdlib plus the `ml` extra, inside functions.
"""

from __future__ import annotations

import copy
import math
import random
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from types import MappingProxyType
from typing import Any, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .baseline import (
    SPREAD_COMPONENTS,
    ExceedanceCurves,
    ExceedancePredictor,
    FittedArx,
    _raw_regressor,
    _validate_taus_bp,
    fit_arx,
)
from .contract import DERIVED_FEATURES, QUANTILE_LEVELS
from .data import DailyObservation, exceeds_bp, load_stress_thresholds
from .metrics import _validate_levels
from .pressure import ONSET_QUIET_DAYS
from .asof import InformationRule
from .splits import (
    LookAheadError,
    SplitError,
    ensure_strictly_ascending,
)

__all__ = [
    "paired_bootstrap_p_values",
    "PRESSURE_QRF_SETTINGS",
    "PRESSURE_NATURAL_GRADIENT_SETTINGS",
    "PRESSURE_DISTRIBUTION_SELECTION",
    "pressure_qrf_exceedance",
    "pressure_natural_gradient_exceedance",
    "MARKOV_SWITCHING_SETTINGS",
    "FittedMarkovSwitching",
    "fit_markov_switching",
    "filter_markov_switching",
    "markov_switching_exceedance",
    "markov_switching_exceedance_curve",
    "markov_switching_state_probabilities",
    "ARX_FEATURES",
    "CALIBRATIONS",
    "DEFAULT_CALIBRATION_FOLDS",
    "DEFAULT_CALIBRATION_SHARE",
    "GARCH_MINIMUM_CHANGES",
    "GPD_MINIMUM_EXCESSES",
    "GPD_SHAPE_BOUNDS",
    "PARTIAL_SCALE_EXPONENT",
    "SCALE_FLOOR_BPS",
    "SCALE_WINDOW",
    "TAIL_FAMILIES",
    "TRAINING_PAIRS",
    "VOLATILITY_FEATURES",
    "FittedTail",
    "MissingMLExtraError",
    "FittedGradientBoostedQuantiles",
    "fit_gradient_boosted_quantiles",
    "gbm_exceedance",
    "DYNAMIC_LOGIT_SETTINGS",
    "DYNAMIC_ORDINAL_SETTINGS",
    "STACKED_COMBINER",
    "dynamic_logit_exceedance",
    "dynamic_ordinal_exceedance",
    "stacked_combiner",
    "PRESSURE_CLASSIFIER_SETTINGS",
    "PRESSURE_LOGISTIC_SETTINGS",
    "SCARCITY_STATE",
    "TGA_CHANGE_ROWS",
    "pressure_classifier_exceedance",
    "pressure_probit_exceedance",
    "pressure_two_part_exceedance",
    "TWO_PART_SETTINGS",
    "pressure_quantile_exceedance",
    "pressure_logistic_exceedance",
    "PRESSURE_TAIL_SETTINGS",
    "TAIL_SCALE_COLUMNS",
    "CensoredGpd",
    "fit_censored_gpd",
    "pressure_tail_exceedance",
]

#: The level the point forecast is read at. The contract grid carries it, and a
#: grid that does not is refused rather than given a made-up centre: with an
#: even number of levels there is no middle entry of the rearranged vector, and
#: averaging the two straddling it would report a centre that no fit produced.
_MEDIAN_LEVEL = 0.50

#: The seed every fit uses unless a caller names another. The *value* is
#: arbitrary; that it is fixed is not. See the module docstring on early
#: stopping: an unseeded fit above 10 000 rows is not reproducible, and the
#: published records this repository keeps are re-scored against their own
#: figures by `tests/test_generated_results.py`.
DEFAULT_RANDOM_STATE = 0


#: How much of a row's own declared band is used as a tail when the fitted
#: residual range is narrower than that band. A fifth on each side puts the
#: outer knots one declared level-step beyond the 0.05 and 0.95 knots at
#: constant density, which is the least the knot set can be widened by and
#: still be increasing.
_TAIL_SHARE = 0.2

#: The tail width when a row's band has zero width --- every fit agreeing to
#: the last bit. Positive so the knot set is still increasing; small enough
#: that it is not a distribution anybody would read as informative.
_MINIMUM_TAIL = 1e-9

#: The band calibrations a fit can be asked for. `none` first: it is the
#: default, and the model every published record was produced with. See the
#: module docstring for `conformal`, `cross_conformal`, `conformal_asymmetric`,
#: `cross_conformal_asymmetric`, `cross_conformal_scaled` and
#: `cross_conformal_partial`, each appended rather than slotted beside its
#: sibling so no existing name's position moves.
CALIBRATIONS = (
    "none",
    "conformal",
    "cross_conformal",
    "conformal_asymmetric",
    "cross_conformal_asymmetric",
    "cross_conformal_scaled",
    "cross_conformal_partial",
)

#: The calibrations that report the full fit and calibrate it with excluding
#: models over `calibration_folds` date blocks.
_CROSS_CALIBRATIONS = (
    "cross_conformal",
    "cross_conformal_asymmetric",
    "cross_conformal_scaled",
    "cross_conformal_partial",
)

#: How a cross-conformal excluding model's training rows are masked. `None`,
#: the default, is the model every published record was produced with: the
#: frame as the fold masked it. `"held_out_row"` masks, for each held-out row,
#: the declared values on the training rows before its block that were not yet
#: public at that row's own decision instant (directive #78; see the module
#: docstring).
CALIBRATION_MASKINGS = ("held_out_row",)

#: The calibration whose scores are divided by `_trailing_scale`.
_SCALED_CALIBRATION = "cross_conformal_scaled"

#: The calibration whose scores are divided by `_partial_factor`.
_PARTIAL_CALIBRATION = "cross_conformal_partial"

#: The calibrations that read `_trailing_scale` at every held-out row and at
#: the forecast, and score no row without one.
_TRAILING_SCALE_CALIBRATIONS = (_SCALED_CALIBRATION, _PARTIAL_CALIBRATION)

#: `gamma` in `cross_conformal_partial`'s factor `sigma ** gamma`. One half:
#: Eleonora's ruling of 16 September 2026, fixed before any fold was scored
#: under it, after job 662 found the fully proportional `cross_conformal_scaled`
#: over-corrected in both regimes. A declared rule and not a fitted one: no
#: grid was searched and no fold chose it.
PARTIAL_SCALE_EXPONENT = 0.5

#: How many one-step spread changes `_trailing_scale` reads, ending at a feature
#: row. Twenty: about a month of business days, the trailing window job 657's
#: diagnosis sorted the published `cross_conformal` misses by, and long enough
#: that one day's move is a twentieth of the mean square rather than all of it.
#: A window is a statement about the recent regime, so it is short against the
#: sixty-one-row minimum history rather than a share of the frame.
SCALE_WINDOW = 20

#: The least `_trailing_scale` returns, in basis points. The spread is quoted to
#: one basis point (SOFR is published in percent to two decimals), so the
#: smallest root mean square a `SCALE_WINDOW` window with any move in it can
#: have is one one-tick change in twenty: `1 / sqrt(SCALE_WINDOW)`. A flat
#: window -- every observed change zero -- would divide a score by zero; at the
#: floor it is priced as the calmest window that moved at all. Derived from the
#: window, so the two cannot drift apart.
SCALE_FLOOR_BPS = 1.0 / math.sqrt(SCALE_WINDOW)

#: The share of a training frame held out as calibration rows when
#: `calibration="conformal"` names none. A quarter: at `--minimum-history 61`
#: the first fold still has more calibration rows than the conformal quantile
#: needs to be finite, and three quarters of the frame are left to fit on.
DEFAULT_CALIBRATION_SHARE = 0.25

#: The contiguous date blocks `calibration="cross_conformal"` splits a training
#: frame into when it names none. Five: each excluding model is fitted on four
#: fifths of the frame less the purge, and a forecast costs five more reads.
DEFAULT_CALIBRATION_FOLDS = 5

#: The volatility features gbm can be built with. See the module docstring.
VOLATILITY_FEATURES = ("garch11",)

#: The design name of the `garch11` column.
_GARCH_COLUMN = "garch11_variance"

#: The ARX features gbm can be built with. See the module docstring: the ARX is
#: fitted on the model's own declared regressors, and nothing else is offered.
ARX_FEATURES = ("declared",)

#: The design name of the ARX forecast column.
_ARX_COLUMN = "arx_forecast"

#: The training pairings gbm can be built with besides the default one-step
#: pairs. See the module docstring (#37).
TRAINING_PAIRS = ("direct",)

#: The tail families gbm's law can be continued with above its top declared
#: quantile. See the module docstring.
TAIL_FAMILIES = ("gpd",)

#: What a tail was at one fit, as `tail_account` spells it on a record: a
#: fitted shape, `_fit_gpd_pwm`'s exponential fallback, no excesses at all, and
#: a negative shape floored at zero (#63). See `FittedTail` on why the first is
#: the only one that is evidence.
#:
#: `refused` is B44's state, a shape refused at the old lower bound of `-0.5`.
#: No fit makes it since the floor (#63), which takes in that case. It stays
#: here so the published records that carry it still read
#: (`tail_diagnostics`).
TAIL_STATES = ("fitted", "fallback", "no_excesses", "floored", "refused")

#: The fewest observed spread changes among a frame's fit rows a GARCH(1,1) is
#: fitted from: ten per fitted parameter. Below it the three parameters are
#: pinned by a handful of squared changes and the search converges to whichever
#: of them was largest. At `--minimum-history 61` under `--calibration
#: conformal` and a six-day gap the first fold's fit rows still carry more.
GARCH_MINIMUM_CHANGES = 30

#: The Nelder-Mead iteration cap. A search still moving after this many steps
#: is refused, not read off where it stopped.
_GARCH_MAX_ITERATIONS = 2000

#: Convergence: the simplex's criterion values agree to this share of the best
#: one, and its vertices to this much in `(log(omega / f_-1), alpha, beta)`.
_GARCH_TOLERANCE = 1e-8

#: Hosking and Wallis' plotting position offset: the `j`-th of `n` ascending
#: excesses is placed at `(j - 0.35) / n`. It is the offset their own study of
#: the generalised Pareto recommends for probability-weighted moments, and it is
#: a *convention*, not a tuning knob --- the sample moments below are only the
#: moments of the fitted law under this one choice, so moving it does not make
#: the fit better or worse, it makes the two sides of the estimator disagree.
_GPD_PLOTTING_OFFSET = 0.35

#: The fewest excesses `_fit_gpd_pwm` will read a *shape* from; below it the
#: exponential fallback is taken and recorded.
#:
#: Twenty. The PWM shape's sampling error falls like `1 / sqrt(n)`, so at ten
#: excesses it is of the same order as `0.5`, the upper end of
#: `GPD_SHAPE_BOUNDS` below: the fit could not tell one end of its range from
#: the other, and a
#: shape reported at that precision reads as evidence while carrying none. At
#: twenty it is about half that, which is the least that distinguishes a heavy
#: tail from a bounded one.
#:
#: The early folds of an expanding window are exactly this case --- a few
#: hundred training rows put five per cent of them above the conditional
#: `Q(0.95)` --- and they are the reason the fallback is recorded on the record
#: rather than signalled by a shape of zero. A caller cannot otherwise tell a
#: fitted `xi` that landed near zero from one that was never fitted.
GPD_MINIMUM_EXCESSES = 20

#: The interval the fitted shape is held to. The two ends are there for
#: different reasons, and neither is a preference.
#:
#: `0.5` above is a clamp. At `xi >= 0.5` the fitted law has infinite variance
#: and at `xi >= 1` an infinite mean; about a hundred excesses cannot evidence a
#: tail that heavy, and what produces such a fit is one large residual. The wide
#: taus are read a long way out, so that residual's opinion would arrive at
#: `P(spread > 50 bp)` multiplied rather than averaged away. A shape above it is
#: brought down to it and kept, and `clamped` says so.
#:
#: `0.0` below is a floor, and it is Eleonora's ruling on #63
#: (`docs/decisions/tail-shape-floor.md`): **repo pressure has no hard
#: ceiling.** The Standing Repo Facility is a soft cap, not a bound. A negative
#: `xi` puts a hard ceiling `sigma / -xi` above the threshold, beyond which the
#: model returns exactly zero, and that is the zero the tail exists to remove.
#: On about thirty excesses the shape's sign also turned on the fitter's
#: version (#63). So a fit whose raw shape is negative takes `xi = 0.0`, with
#: the sample's mean excess as its scale, and is recorded as `floored` with the
#: raw estimate beside it. It is not a clamp. A clamp would keep the PWM scale,
#: which no longer belongs to the shape. At `xi = 0.0` the PWM pair is exactly
#: the exponential with the sample's mean, the law the fallback already uses.
#:
#: The floor replaces B44 (`docs/decisions/tail-refusal.md`), which refused a
#: shape at or below the old lower bound of `-0.5` and kept an interior negative
#: shape with its ceiling. The floor takes in both.
GPD_SHAPE_BOUNDS = (0.0, 0.5)

#: How far `a_0 - 2 a_1` may fall, as a share of `a_0`, before the fit is
#: refused rather than divided by. For a sample that is not identically zero the
#: exact denominator is at least `0.3 a_0 / n` --- both `x_j` and `2 p_j - 1`
#: ascend, so Chebyshev's sum inequality bounds it below by `a_0` times the mean
#: of the weights, which is `0.3 / n` --- so it cannot vanish on its own. A
#: computed value at or under this share is therefore an all-zero sample or the
#: cancellation of two sums of equal size, and in neither is there a shape.
_GPD_MINIMUM_DENOMINATOR = 1e-12


def _band_probability(levels: Sequence[float]) -> Fraction:
    """The declared band's span, exactly: `Fraction` of the outer two levels.

    Exact because it feeds a ceiling. `0.95 - 0.05` is `0.8999999999999999` in
    floating point, and a rank computed as `ceil(q * (n + 1))` from a `q` one
    representable step off can land one position away from the rank the
    guarantee is stated for.
    """

    return Fraction(repr(float(levels[-1]))) - Fraction(repr(float(levels[0])))


def _minimum_calibration_rows(levels: Sequence[float]) -> int:
    """The fewest calibration scores at which the conformal quantile is finite.

    The rank is `ceil(q (n + 1))` for band probability `q`, and it names a
    score only while it is at most `n`, which holds exactly when
    `n >= q / (1 - q)`. Nine for the declared `0.05`-`0.95` band. Below it the
    honest widening is infinite, and a finite one would be a band claiming a
    coverage its calibration cannot support.
    """

    q = _band_probability(levels)
    return math.ceil(q / (1 - q))


def _side_probabilities(levels: Sequence[float]) -> Tuple[Fraction, Fraction]:
    """Each edge's one-sided coverage, exactly: `(1 - lo, hi)` of the outer two levels.

    Exact for `_band_probability`'s reason. Their misses, `lo` and `1 - hi`,
    sum to the band's `alpha`; see the module docstring on why that sum is the
    two-sided guarantee `conformal_asymmetric` claims.
    """

    return (
        1 - Fraction(repr(float(levels[0]))),
        Fraction(repr(float(levels[-1]))),
    )


def _minimum_asymmetric_calibration_rows(levels: Sequence[float]) -> int:
    """The fewest calibration rows at which both of `conformal_asymmetric`'s ranks are finite.

    `_minimum_calibration_rows`' bound at each side's own probability, and the
    larger of the two. Nineteen for the declared `0.05`-`0.95` band.
    """

    return max(math.ceil(p / (1 - p)) for p in _side_probabilities(levels))


def _asymmetric_widenings(
    lower_scores: Sequence[float],
    upper_scores: Sequence[float],
    levels: Sequence[float],
) -> Tuple[float, float]:
    """How far `conformal_asymmetric` moves the lower edge down and the upper edge up.

    Each score set reduced on its own, at its own side's rank. The two sets
    are one per calibration row, so they have one length, and both ranks name
    an entry exactly when that length is at least
    `_minimum_asymmetric_calibration_rows(levels)`, which the fitter refuses
    below.
    """

    lower_p, upper_p = _side_probabilities(levels)
    down = sorted(lower_scores)[math.ceil(lower_p * (len(lower_scores) + 1)) - 1]
    up = sorted(upper_scores)[math.ceil(upper_p * (len(upper_scores) + 1)) - 1]
    return down, up


def _spread_change_names(lags: int) -> Tuple[str, ...]:
    """The lag columns' design names, in lag order: lag 1 first."""

    return tuple(f"spread_change_lag_{lag}" for lag in range(1, lags + 1))


def _observed_spread(row: DailyObservation, label: str) -> Optional[float]:
    """`row.spread_bps`, or `None` where either leg of it is a hole.

    A leg absent from the row is `_raw_regressor`'s refusal, as it is for every
    other column this model reads; a leg carried as `None` makes the spread
    unobserved, and that is a missing change, not a zero and not yesterday's.
    """

    for component in SPREAD_COMPONENTS:
        observed = _raw_regressor(
            row,
            component,
            label,
            role="a leg of the spread whose lagged changes this model reads",
        )
        if observed is None:
            return None
    return float(row.spread_bps)


def _spread_changes(
    spreads: Sequence[Optional[float]], position: int, lags: int, label: str
) -> List[Optional[float]]:
    """The `lags` spread changes ending at `spreads[position]`, lag 1 first.

    Lag `j` is `spreads[position - j + 1] - spreads[position - j]`: by row, and
    never reaching past `position`. A change with a hole at either end is
    `None`. Every lag this model reads -- a training row's, a calibration
    row's, a forecast's -- comes through here.
    """

    if position < lags:
        raise ValueError(
            f"the lagged spread changes of the {label} need {lags} rows before "
            f"it and its frame has {position}; a lag reaching before the "
            f"frame's first row has no row to read, and a negative position "
            f"would wrap to the frame's latest rows and read them as its oldest"
        )
    changes: List[Optional[float]] = []
    for lag in range(1, lags + 1):
        later = spreads[position - lag + 1]
        earlier = spreads[position - lag]
        changes.append(None if later is None or earlier is None else later - earlier)
    return changes


def _trailing_scale(
    spreads: Sequence[Optional[float]], position: int
) -> Optional[float]:
    """`cross_conformal_scaled`'s scale at the feature row `spreads[position]`.

    The root mean square of the observed one-step changes into rows
    `position - SCALE_WINDOW + 1 .. position`, floored at `SCALE_FLOOR_BPS`.
    Reads `spreads[position - SCALE_WINDOW : position + 1]` and nothing after
    `position`: a caller may hand over the whole frame. A change touching a
    hole is left out, as `_squared_changes` leaves it out. `None` -- no scale --
    when the window would reach before the frame or holds no observed change.
    """

    if position < SCALE_WINDOW:
        return None
    window = spreads[position - SCALE_WINDOW : position + 1]
    squares = [
        (later - earlier) * (later - earlier)
        for earlier, later in zip(window[:-1], window[1:])
        if earlier is not None and later is not None
    ]
    if not squares:
        return None
    return max(math.sqrt(math.fsum(squares) / len(squares)), SCALE_FLOOR_BPS)


def _partial_factor(scale: float) -> float:
    """`cross_conformal_partial`'s factor at a row whose `_trailing_scale` is `scale`.

    `scale ** PARTIAL_SCALE_EXPONENT`, the exponent read at call time. No
    reference scale divides it: one shared reference cancels between a
    held-out row's factor and the forecast's (see the module docstring). At an
    exponent of zero it is exactly `1.0`.
    """

    return scale ** PARTIAL_SCALE_EXPONENT


def _squared_changes(spreads: Sequence[Optional[float]]) -> List[Optional[float]]:
    """The squared change into each row, `None` at the first row and at a hole."""

    squares: List[Optional[float]] = [None]
    for earlier, later in zip(spreads[:-1], spreads[1:]):
        if later is None or earlier is None:
            squares.append(None)
        else:
            change = later - earlier
            squares.append(change * change)
    return squares


def _garch_variances(
    squares: Sequence[Optional[float]],
    parameters: Tuple[float, float, float],
    initial: float,
) -> List[float]:
    """`f_p` for every row `p`: the variance of the change into row `p + 1`.

    `f_p = omega + alpha * e_p + beta * f_(p-1)`, with `e_p` row `p`'s own
    squared change, or `f_(p-1)` where it has none, and `f_(-1) = initial`. By
    construction `f_p` reads `squares[: p + 1]` and nothing after: the one
    recursion the fit's likelihood, the training design, the calibration rows
    and a forecast all read.
    """

    omega, alpha, beta = parameters
    variances: List[float] = []
    previous = initial
    for square in squares:
        shock = previous if square is None else square
        previous = omega + alpha * shock + beta * previous
        variances.append(previous)
    return variances


def _garch_criterion(
    squares: Sequence[Optional[float]],
    parameters: Tuple[float, float, float],
    initial: float,
) -> float:
    """Twice the negative Gaussian quasi-log-likelihood, constants dropped.

    Each observed change into row `p + 1` is scored against `f_p`, the variance
    forecast at the row before it.
    """

    total = 0.0
    variances = _garch_variances(squares, parameters, initial)
    for variance, square in zip(variances, squares[1:]):
        if square is not None:
            total += math.log(variance) + square / variance
    return total


def _nelder_mead(
    criterion: Any, start: Sequence[float], steps: Sequence[float]
) -> Tuple[Tuple[float, ...], bool]:
    """Minimise `criterion` from `start`; return the best vertex and convergence.

    The Lagarias et al. (1998) moves -- reflection 1, expansion 2, contraction
    and shrink 1/2 -- with ties kept in vertex order, so a search is
    deterministic. Converged when the simplex's values agree to
    `_GARCH_TOLERANCE` of the best and its vertices to `_GARCH_TOLERANCE`;
    otherwise, after `_GARCH_MAX_ITERATIONS`, not.
    """

    dimension = len(start)
    simplex = [tuple(float(value) for value in start)]
    for axis, step in enumerate(steps):
        simplex.append(
            tuple(
                value + step if index == axis else value
                for index, value in enumerate(simplex[0])
            )
        )
    values = [criterion(vertex) for vertex in simplex]

    def between(origin, target, weight):
        return tuple(o + weight * (t - o) for o, t in zip(origin, target))

    for _ in range(_GARCH_MAX_ITERATIONS):
        order = sorted(range(dimension + 1), key=values.__getitem__)
        simplex = [simplex[index] for index in order]
        values = [values[index] for index in order]
        best = simplex[0]
        if values[-1] - values[0] <= _GARCH_TOLERANCE * (1.0 + abs(values[0])) and all(
            abs(coordinate - anchor) <= _GARCH_TOLERANCE
            for vertex in simplex[1:]
            for coordinate, anchor in zip(vertex, best)
        ):
            return best, True
        centroid = tuple(
            sum(vertex[axis] for vertex in simplex[:-1]) / dimension
            for axis in range(dimension)
        )
        worst = simplex[-1]
        reflected = between(centroid, worst, -1.0)
        reflected_value = criterion(reflected)
        if reflected_value < values[0]:
            expanded = between(centroid, worst, -2.0)
            expanded_value = criterion(expanded)
            if expanded_value < reflected_value:
                simplex[-1], values[-1] = expanded, expanded_value
            else:
                simplex[-1], values[-1] = reflected, reflected_value
            continue
        if reflected_value < values[-2]:
            simplex[-1], values[-1] = reflected, reflected_value
            continue
        if reflected_value < values[-1]:
            contracted = between(centroid, reflected, 0.5)
            contracted_value = criterion(contracted)
            accepted = contracted_value <= reflected_value
        else:
            contracted = between(centroid, worst, 0.5)
            contracted_value = criterion(contracted)
            accepted = contracted_value < values[-1]
        if accepted:
            simplex[-1], values[-1] = contracted, contracted_value
            continue
        simplex = [best] + [between(best, vertex, 0.5) for vertex in simplex[1:]]
        values = [values[0]] + [criterion(vertex) for vertex in simplex[1:]]
    return simplex[0], False


def _fit_garch11(
    spreads: Sequence[Optional[float]], label: str
) -> Tuple[Tuple[float, float, float], float]:
    """`((omega, alpha, beta), f_-1)` fitted on `spreads`, or refuse.

    `spreads` are the fit rows' and nothing else; the caller filters any later
    row with what this returns. The search runs over `(log(omega / f_-1),
    alpha, beta)`, scale-free in the spread's units, from a persistent start
    `(0.05, 0.05, 0.90)`; a point outside the constraints scores infinity.
    """

    squares = _squared_changes(spreads)
    observed = [square for square in squares if square is not None]
    if len(observed) < GARCH_MINIMUM_CHANGES:
        raise ValueError(
            f"volatility_feature garch11 needs at least {GARCH_MINIMUM_CHANGES} "
            f"observed spread changes among the {label}, got {len(observed)}; "
            f"three parameters fitted from fewer are pinned by a handful of "
            f"squared changes, not estimated"
        )
    initial = sum(observed) / len(observed)
    if not initial > 0.0:
        raise ValueError(
            f"the GARCH(1,1) fit on the {label} did not converge: every one of "
            f"its {len(observed)} observed spread changes is zero, so omega runs "
            f"to 0 and the quasi-likelihood has no maximum. Refused rather than "
            f"read as a constant variance"
        )

    def criterion(point: Tuple[float, ...]) -> float:
        scale, alpha, beta = point
        if not (alpha >= 0.0 and beta >= 0.0 and alpha + beta < 1.0):
            return math.inf
        if not -700.0 < scale < 700.0:
            return math.inf
        return _garch_criterion(
            squares, (initial * math.exp(scale), alpha, beta), initial
        )

    point, converged = _nelder_mead(
        criterion, (math.log(0.05), 0.05, 0.90), (0.5, 0.05, 0.05)
    )
    if not converged:
        raise ValueError(
            f"the GARCH(1,1) fit on the {label} did not converge in "
            f"{_GARCH_MAX_ITERATIONS} Nelder-Mead iterations; refused rather "
            f"than read off where the search stopped, and never replaced by a "
            f"constant variance"
        )
    scale, alpha, beta = point
    return (initial * math.exp(scale), alpha, beta), initial


def _design(
    row: DailyObservation,
    regressors: Sequence[str],
    imputations: Mapping[str, float],
    label: str,
    changes: Sequence[Optional[float]] = (),
    variance: Optional[float] = None,
    arx: Optional[FittedArx] = None,
) -> List[float]:
    """One row as the design reads it: the spread, each regressor, each lag, the variance, the ARX.

    A regressor carried as `None` gets its fitted imputation; one missing from
    the row is `_raw_regressor`'s refusal. A missing spread change gets its
    lag's imputation, by the same rule. The GARCH variance, when there is one,
    is never missing: `_garch_variances` carries a hole forward by its
    expectation. The ARX forecast is `arx.point_forecast(row)`, off this row
    alone, under the ARX's own imputations. The one spelling the fit, the
    calibration scores and `FittedGradientBoostedQuantiles.design_row` share.
    """

    values = [float(row.spread_bps)]
    for name in regressors:
        observed = _raw_regressor(row, name, label)
        values.append(imputations[name] if observed is None else observed)
    for name, change in zip(_spread_change_names(len(changes)), changes):
        values.append(imputations[name] if change is None else change)
    if variance is not None:
        values.append(variance)
    if arx is not None:
        values.append(arx.point_forecast(row))
    return values


def _calibrated(vector: Sequence[float], widening: float) -> Tuple[float, ...]:
    """The rearranged vector with its outer two levels moved by `widening`.

    Down at the bottom, up at the top, interior untouched. A negative widening
    narrows the band, and an outer level it would carry past its neighbour
    stops at that neighbour: the vector stays non-decreasing without re-sorting,
    which would move a calibrated value onto an interior level.
    """

    return _banded(vector, vector[0] - widening, vector[-1] + widening)


def _banded(vector: Sequence[float], lower: float, upper: float) -> Tuple[float, ...]:
    """The rearranged vector with its outer two levels moved to `lower` and `upper`.

    `_calibrated`'s neighbour rule, stated once: an outer level that would pass
    its neighbour stops at it, and the interior is untouched.
    """

    values = list(vector)
    values[0] = min(lower, values[1])
    values[-1] = max(upper, values[-2])
    return tuple(values)


def _cross_conformal_edges(
    lows: Sequence[float], highs: Sequence[float], levels: Sequence[float]
) -> Tuple[float, float]:
    """CV+'s band edges from `Q_lo_-k(i)(x) - s_i` and `Q_hi_-k(i)(x) + s_i`.

    The `floor(alpha (n + 1))`-th smallest low and the `ceil((1 - alpha)(n +
    1))`-th smallest high, `alpha` exact by `_band_probability`. Both ranks name
    an entry exactly when `n >= _minimum_calibration_rows(levels)`, which the
    fitter refuses below.
    """

    q = _band_probability(levels)
    count = len(lows)
    lower = sorted(lows)[math.floor((1 - q) * (count + 1)) - 1]
    upper = sorted(highs)[math.ceil(q * (count + 1)) - 1]
    return lower, upper


def _cross_conformal_asymmetric_edges(
    lows: Sequence[float], highs: Sequence[float], levels: Sequence[float]
) -> Tuple[float, float]:
    """CV+'s edges from `Q_lo_-k(i)(x) - s_lo_i` and `Q_hi_-k(i)(x) + s_hi_i`, per side.

    The `floor(lo (n + 1))`-th smallest low and the `ceil(hi (n + 1))`-th
    smallest high, `lo` and `hi` the outer levels exact by
    `_side_probabilities`. Both ranks name an entry exactly when
    `n >= _minimum_asymmetric_calibration_rows(levels)`, which the fitter
    refuses below.
    """

    lower_p, upper_p = _side_probabilities(levels)
    count = len(lows)
    lower = sorted(lows)[math.floor((1 - lower_p) * (count + 1)) - 1]
    upper = sorted(highs)[math.ceil(upper_p * (count + 1)) - 1]
    return lower, upper


@dataclass(frozen=True)
class FittedTail:
    """A generalised Pareto fit to a sample of excesses, and how it was got.

    `xi` and `sigma` alone are not enough to read a fit by. Quite different
    things come out of `_fit_gpd_pwm` as a pair of floats --- a shape the
    sample supported, a shape the sample proposed and the clamp took back, a
    negative shape the floor set to zero, and no shape at all --- and only the
    first is evidence about a tail. So the record carries which happened:

    * `excesses` --- how many excesses the fit saw.
    * `clamped` --- the PWM shape fell above the upper end of
      `GPD_SHAPE_BOUNDS` and was brought down to it. `sigma` is the unclamped
      fit's scale; it is not re-estimated against the clamped shape, because
      the pair is then no longer a PWM fit of anything and pretending otherwise
      is what the flag exists to prevent.
    * `fallback` --- fewer than `GPD_MINIMUM_EXCESSES` excesses, so no shape was
      fitted: `xi` is exactly `0.0` and `sigma` is the mean of the excesses,
      which is the exponential the two-parameter family collapses to there.
    * `floored`, `xi_estimate` --- enough excesses were seen, but the raw PWM
      shape was negative, so the floor at the lower end of `GPD_SHAPE_BOUNDS`
      set it to zero (#63). `xi` is `0.0` and `sigma` the mean of the excesses,
      the fallback's exponential, and `xi_estimate` is the raw negative shape.
      `None` on every fit that was not floored. Only the record tells a floored
      fit from a fallback or from a shape fitted at zero, which is why this flag
      exists.

    B44's `refused` flag is gone: the floor takes in the shapes it refused.

    A caller that ignores these still gets a usable law. A record that
    ignores them publishes a fitted shape that was not fitted.
    """

    xi: float
    sigma: float
    excesses: int
    clamped: bool
    fallback: bool
    floored: bool = False
    xi_estimate: Optional[float] = None


def _fit_gpd_pwm(excesses: Sequence[float]) -> FittedTail:
    """A generalised Pareto fitted to `excesses` by probability-weighted moments.

    Excesses are non-negative and are *residual* excesses above a conditional
    quantile, never level excesses. The distinction is the whole reason this
    estimator can be fitted at all: the conditional law's anchor moves from fold
    to fold with the feature row, so a level-space excess would re-learn that
    anchor every fold from about a hundred points, while a residual excess is
    the part that is exchangeable across folds.

    Sort ascending as `x_1 <= ... <= x_n`, place `x_j` at
    `p_j = (j - _GPD_PLOTTING_OFFSET) / n`, and form

        a_0 = mean(x_j)
        a_1 = mean(x_j (1 - p_j))
        xi    = 2 - a_0 / (a_0 - 2 a_1)
        sigma = 2 a_0 a_1 / (a_0 - 2 a_1)

    `xi` is the extreme-value convention: positive is heavy-tailed, the fitted
    mean is `sigma / (1 - xi)`, and negative would put a finite upper endpoint
    at `sigma / -xi`. The two moments are the population moments of that law
    inverted, so `sigma / (1 - xi)` is identically `a_0` for any sample the
    estimator accepts and does not clamp --- which is what `tests/test_ml.py`'s
    `FittedTailPwmTests` holds it to.

    **A negative shape is floored at zero (#63).** The returned fit then has
    `xi = 0.0` and `sigma = a_0`, the exponential with the sample's mean, which
    keeps `sigma / (1 - xi) == a_0`. It is `floored`, with the raw shape as
    `xi_estimate`. Repo pressure has no hard ceiling, so no fit returned here
    has an upper endpoint. See `GPD_SHAPE_BOUNDS`.

    Both sums are `math.fsum` rather than `sum`, which is the one place this
    module departs from the repository's plain-summation idiom and does so on
    purpose. `a_0` is summed over the *sorted* sample while a caller holds the
    excesses in whatever order it collected them, and the identity above is
    stated as an equality; `fsum` is correctly rounded and therefore
    order-independent, so the two agree bit for bit. `sum` would make the
    criterion depend on the order the excesses arrived in, and --- see
    `CLAUDE.md` on the 3.12 ceiling --- on the interpreter.

    Stdlib arithmetic throughout: sorting and sums. This module may import numpy
    and `FittedGradientBoostedQuantiles` does, but an estimator that needs no
    array library is one `tests/test_dependency_boundary.py` never has to argue
    about, and one a caller on a checkout without the extra can still reach.

    Args:
        excesses: non-negative finite excesses above a threshold, any order.

    Returns:
        A `FittedTail`. See its docstring: `clamped`, `fallback` and `floored`
        are the difference between a shape this sample supported and a shape it
        did not.

    Raises:
        ValueError: an empty sample; a negative or non-finite excess; or a
            degenerate `a_0 - 2 a_1`, which has no shape in it and is refused
            rather than smoothed or defaulted. The message names the sample
            size, because at these sizes the size is the first thing a caller
            debugging one wants to know.
    """

    ordered = sorted(float(value) for value in excesses)
    count = len(ordered)
    if count == 0:
        raise ValueError("cannot fit a tail to an empty sample; sample size 0")
    for value in ordered:
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(
                f"excesses must be non-negative and finite; got {value!r} in a "
                f"sample of size {count}"
            )

    a_0 = math.fsum(ordered) / count
    if count < GPD_MINIMUM_EXCESSES:
        return FittedTail(
            xi=0.0, sigma=a_0, excesses=count, clamped=False, fallback=True
        )

    a_1 = (
        math.fsum(
            value * (1.0 - (rank - _GPD_PLOTTING_OFFSET) / count)
            for rank, value in enumerate(ordered, start=1)
        )
        / count
    )
    denominator = a_0 - 2.0 * a_1
    if denominator <= _GPD_MINIMUM_DENOMINATOR * a_0:
        raise ValueError(
            f"the probability-weighted moments are degenerate "
            f"(a_0 - 2 a_1 = {denominator!r}, a_0 = {a_0!r}); there is no shape "
            f"in a sample of size {count}"
        )

    xi = 2.0 - a_0 / denominator
    sigma = 2.0 * a_0 * a_1 / denominator
    lower, upper = GPD_SHAPE_BOUNDS
    # #63: a negative shape is floored at zero, every negative shape, with the
    # sample's mean as the scale. This subsumes B44's refusal of a shape at or
    # below `-0.5`, which also fell back to this exponential, and it removes
    # the ceiling an interior negative shape used to keep. See
    # `GPD_SHAPE_BOUNDS`.
    if xi < lower:
        return FittedTail(
            xi=0.0,
            sigma=a_0,
            excesses=count,
            clamped=False,
            fallback=False,
            floored=True,
            xi_estimate=xi,
        )
    clamped = xi > upper
    if clamped:
        xi = upper
    return FittedTail(
        xi=xi, sigma=sigma, excesses=count, clamped=clamped, fallback=False
    )


def _gpd_survival(tail: FittedTail, excess: float) -> float:
    """`P(X > excess)` under the generalised Pareto `tail`, for `excess >= 0`.

    `(1 + xi x / sigma) ** (-1 / xi)`, or `exp(-x / sigma)` at `xi == 0.0` ---
    the fallback's exponential, and the family's own limit there. A negative
    `xi` would put the endpoint at `sigma / -xi`, at and beyond which this is
    `0.0`. No fit has one since the floor (#63; `GPD_SHAPE_BOUNDS`). The branch
    is kept because it is the law's, not the estimator's.
    """

    if tail.xi == 0.0:
        return math.exp(-excess / tail.sigma)
    base = 1.0 + tail.xi * excess / tail.sigma
    if base <= 0.0:
        return 0.0
    return base ** (-1.0 / tail.xi)


class _ExcludingModel:
    """One cross-conformal block: the model fitted without it, and its scores.

    * `estimators`, `imputations`, `garch_parameters`,
      `garch_initial_variance`, `arx` --- the fit on the rows outside the block
      and its purge gaps, in `FittedGradientBoostedQuantiles`' own fields'
      meaning.
    * `held_out_start`, `held_out_end` --- the block's first and last dates.
    * `training_dates` --- every row a design pair of this fit read, as an
      origin or as a target, ascending. Carried so the purge can be checked
      against a calendar rather than taken on trust.
    * `scored_dates`, `scores` --- the held-out rows this model scored, and
      their pooled scores `max(Q_lo - y, y - Q_hi)`, in date order.
    * `lower_scores`, `upper_scores` --- the same rows' two signed scores,
      `Q_lo - y` and `y - Q_hi`, in the same order. Read only under
      `cross_conformal_asymmetric`; `scores` is their elementwise maximum.
    * `scales`, `scaled_residuals` --- under `cross_conformal_scaled`, the same
      rows' `_trailing_scale` at their feature rows and their scores
      `|y - m| / scale` about this model's rearranged median, in the same
      order. Empty under every other calibration. `scales` is carried under
      `cross_conformal_partial` too.
    * `partial_scores` --- under `cross_conformal_partial`, the same rows'
      `scores`, each divided by `_partial_factor` of its scale, in the same
      order. Empty under every other calibration.
    """

    __slots__ = (
        "arx",
        "estimators",
        "garch_initial_variance",
        "garch_parameters",
        "held_out_end",
        "held_out_start",
        "imputations",
        "lower_scores",
        "partial_scores",
        "scaled_residuals",
        "scales",
        "scored_dates",
        "scores",
        "training_dates",
        "upper_scores",
    )

    def __init__(
        self,
        *,
        estimators: Sequence[Any],
        imputations: Mapping[str, float],
        garch_parameters: Optional[Tuple[float, float, float]],
        garch_initial_variance: Optional[float],
        held_out_start: date,
        held_out_end: date,
        training_dates: Sequence[date],
        scored_dates: Sequence[date],
        scores: Sequence[float],
        arx: Optional[FittedArx] = None,
        lower_scores: Sequence[float] = (),
        upper_scores: Sequence[float] = (),
        scales: Sequence[float] = (),
        scaled_residuals: Sequence[float] = (),
        partial_scores: Sequence[float] = (),
    ) -> None:
        self.partial_scores: Tuple[float, ...] = tuple(partial_scores)
        self.scales: Tuple[float, ...] = tuple(scales)
        self.scaled_residuals: Tuple[float, ...] = tuple(scaled_residuals)
        self.lower_scores: Tuple[float, ...] = tuple(lower_scores)
        self.upper_scores: Tuple[float, ...] = tuple(upper_scores)
        self.arx: Optional[FittedArx] = arx
        self.estimators: Tuple[Any, ...] = tuple(estimators)
        self.imputations: Mapping[str, float] = MappingProxyType(dict(imputations))
        self.garch_parameters = garch_parameters
        self.garch_initial_variance = garch_initial_variance
        self.held_out_start: date = held_out_start
        self.held_out_end: date = held_out_end
        self.training_dates: Tuple[date, ...] = tuple(training_dates)
        self.scored_dates: Tuple[date, ...] = tuple(scored_dates)
        self.scores: Tuple[float, ...] = tuple(scores)


class MissingMLExtraError(ValueError):
    """The `ml` extra is not installed on this interpreter.

    A `ValueError` subclass, not a bare `ImportError`, because the command-line
    dispatcher catches `(OSError, ValueError)` and prints the message: a caller
    who typed `--model gbm` on a checkout without the extra should be told to
    install it and get exit 2, not a traceback from four frames down.
    """


def _estimator_class() -> Any:
    """`HistGradientBoostingRegressor`, imported here and nowhere else.

    The import lives inside a function because
    `tests/test_dependency_boundary.py` requires it to --- see the module
    docstring. It is wrapped rather than bare so the absence of the extra is a
    refusal in this repository's vocabulary instead of an `ImportError` from
    inside a fit.
    """

    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
    except ImportError as error:  # pragma: no cover - exercised without the extra
        raise MissingMLExtraError(
            "the gradient-boosted quantile model needs the optional 'ml' extra "
            "(numpy and scikit-learn); install it with `pip install -e \".[ml]\"`. "
            "Every other model in this repository is standard-library only and "
            "runs without it"
        ) from error
    return HistGradientBoostingRegressor


def _library_versions() -> Mapping[str, str]:
    """The numpy and scikit-learn versions this process fits with.

    Read off the **imported modules' own `__version__`**, not off
    `importlib.metadata`: the metadata answers what an installer recorded in a
    `site-packages` directory, and the module answers what is actually loaded
    in this interpreter. The two agree on a clean install and disagree exactly
    when it matters -- a second copy earlier on `sys.path`, an editable build,
    a module already imported before an environment changed under it -- and a
    record's provenance is a claim about the code that fitted, which is the
    module.

    Called from `fit_gradient_boosted_quantiles` after `_estimator_class`, so
    the extra is known to be present and a caller without it has already been
    refused in this repository's vocabulary. The imports are inside the
    function for the reason every third-party import in this module is; see
    the module docstring.
    """

    import numpy
    import sklearn

    return MappingProxyType(
        {"numpy": numpy.__version__, "scikit-learn": sklearn.__version__}
    )


class FittedGradientBoostedQuantiles:
    """One gradient-boosted fit per contract level, rearranged into a law.

    Fitted state, all of it set in `fit_gradient_boosted_quantiles` and nowhere
    else:

    * `regressors` --- the ordered exogenous names this model was fitted on,
      carried for the reason `FittedArx` carries them: a model that cannot say
      what it read cannot be audited, and two models compared on quietly
      different regressor sets are not being compared.
    * `imputations` --- the training-window mean of each regressor's observed
      values, over the *origin* rows. The one transform with learned parameters,
      and the same one `fit_arx` fits.
    * `_estimators` --- one fitted estimator per entry of `levels`, in that
      order.
    * `_residuals` --- the sorted training residuals about this model's own
      rearranged median. This is the sample `predict_stress` reads for the two
      tail knots of its law; see `predict_stress`.
    * `cutoff` --- the last date the training frame was allowed to contain, with
      the same meaning and the same `trained_beyond` question as persistence.
    * `ml_libraries` --- `{"numpy": ..., "scikit-learn": ...}`, the versions
      of the modules this model was fitted with, read by `_library_versions`
      at the fit. Required and undefaulted: this is the one fitted model in the
      package that reached a third-party library, and every record a run of it
      publishes names those versions under `provenance.ml_libraries` --- see
      `baseline._ml_libraries` and `baseline._run_provenance`. A model built
      without them would publish a record that silently lost that key.
    * `calibration`, `calibration_share`, `widening` --- which band calibration
      this model was built with, the share of its frame held out for it
      (`None` under `none`), and the amount the outer two levels were moved
      by (`0.0` under `none`). See the module docstring.
    * `edge_widenings` --- under `conformal_asymmetric`, how far the lower
      edge was moved down and the upper edge up, `(down, up)`, each off its
      own score set; `widening` is `0.0` there, since no single amount was
      applied. `(0.0, 0.0)` under every other calibration.
    * `fit_end`, `calibration_start`, `calibration_end` --- the last row the
      estimators were fitted on, and the first and last calibration rows
      (`None` under `none`, where the fit rows are the whole frame). Carried
      so a reader can check the purge between the two slices against a
      calendar rather than take it on trust. Under `cross_conformal` the fit
      rows are the whole frame and the calibration dates are the first and
      last held-out rows scored.
    * `calibration_folds`, `calibration_blocks` --- under `cross_conformal`,
      `cross_conformal_asymmetric`, `cross_conformal_scaled` and
      `cross_conformal_partial`, how many blocks the frame was split into and one `_ExcludingModel` per
      block, in date order (`None` and empty otherwise).
    * `spread_change_lags`, `_history_dates`, `_history_spreads` --- how many
      lagged spread changes the design carries (`None` when it carries none),
      and the training frame's own dates and spreads, which are the only rows
      a feature row's lags are read back from -- or, on a model
      `with_history` returned, the as-of history it was handed. See the
      module docstring.
    * `volatility_feature`, `garch_parameters`, `garch_initial_variance` ---
      the volatility feature the design carries (`None` when it carries none),
      the `(omega, alpha, beta)` fitted on the fit rows, and `f_-1`, the fit
      rows' mean squared observed change the recursion starts from. A feature
      row's variance is filtered through the same frame rows its lags are read
      from.
    * `arx_feature`, `arx` --- the ARX feature the design carries (`None` when
      it carries none) and the `baseline.FittedArx` fitted on the fit rows,
      whose point forecast from a feature row is that row's column.
    * `training_pairs` --- `"direct"` when the design was trained on direct
      pairs, `None` for one-step pairs. See the module docstring.
    * `tail`, `tail_fit` --- the tail family the law is continued with above
      its top declared quantile (`None` when it is not) and the `FittedTail`
      fitted to the calibration rows' excesses above that quantile. Four
      states under `tail="gpd"`: `tail_fit.fallback` false, a fitted shape;
      true, the exponential fallback; `tail_fit.floored` true, a negative shape
      floored at zero, with that same exponential (#63); and `tail_fit` `None`,
      **no excesses at all**, where nothing was fitted and the law is the
      default's. See the
      module docstring, and `tail_account` for how a record spells them.

    **What `residuals` is here, and what it is not.** For persistence and the
    ARX the fitted residual sample *is* the whole law: `predict` is an anchor
    plus a residual quantile and `predict_stress` inverts the same sample, so
    the predictive distribution is a location shift of one fixed shape. This
    model is not that. Its band is conditional --- `predict` reads five fits, so
    the *width* of the predictive distribution moves with the feature row and
    not only its centre --- and no row-independent sample can represent a shape
    that moves. So `residuals` is what the name says and no more: the training
    residuals about the model's own centre. `predict_stress` reads it for where
    the law runs out, and reads the rearranged quantile vector for everything
    between.

    A feature row missing a declared regressor raises `MissingRegressorError`; a
    feature row carrying it as `None` gets the fitted mean. Neither becomes
    `0.0`. Both behaviours are `baseline._raw_regressor`'s, reached rather than
    reimplemented.

    `_last_law` is the one slot that is **not** fitted state and is not set by
    the fitter: it is `_shared_law`'s one-row memo, written by whichever of
    `law_knots` and `predict_stress` asks about a row first so that the other
    reads the same evaluation rather than a second one. Nothing it holds is
    reported, and clearing it at any moment changes no answer --- only how many
    times the estimators were called for that answer. See `_shared_law`.
    """

    __slots__ = (
        "_estimators",
        "_history_dates",
        "_history_spreads",
        "_last_law",
        "_residuals",
        "arx",
        "arx_feature",
        "calibration",
        "calibration_blocks",
        "calibration_end",
        "calibration_folds",
        "calibration_masking",
        "calibration_share",
        "calibration_start",
        "cutoff",
        "edge_widenings",
        "fit_end",
        "garch_initial_variance",
        "garch_parameters",
        "imputations",
        "levels",
        "ml_libraries",
        "random_state",
        "regressors",
        "spread_change_lags",
        "tail",
        "tail_fit",
        "training_pairs",
        "volatility_feature",
        "widening",
    )

    def __init__(
        self,
        estimators: Sequence[Any],
        regressors: Sequence[str],
        imputations: Mapping[str, float],
        residuals: Sequence[float],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
        random_state: int = DEFAULT_RANDOM_STATE,
        *,
        ml_libraries: Mapping[str, str],
        calibration: str = "none",
        calibration_share: Optional[float] = None,
        widening: float = 0.0,
        fit_end: Optional[date] = None,
        calibration_start: Optional[date] = None,
        calibration_end: Optional[date] = None,
        spread_change_lags: Optional[int] = None,
        history: Sequence[Tuple[date, Optional[float]]] = (),
        volatility_feature: Optional[str] = None,
        garch_parameters: Optional[Tuple[float, float, float]] = None,
        garch_initial_variance: Optional[float] = None,
        calibration_folds: Optional[int] = None,
        calibration_blocks: Sequence[_ExcludingModel] = (),
        arx_feature: Optional[str] = None,
        arx: Optional[FittedArx] = None,
        tail: Optional[str] = None,
        tail_fit: Optional[FittedTail] = None,
        edge_widenings: Tuple[float, float] = (0.0, 0.0),
        calibration_masking: Optional[str] = None,
        training_pairs: Optional[str] = None,
    ) -> None:
        self.calibration_masking: Optional[str] = calibration_masking
        self.training_pairs: Optional[str] = training_pairs
        self.edge_widenings: Tuple[float, float] = (
            float(edge_widenings[0]),
            float(edge_widenings[1]),
        )
        self.tail: Optional[str] = tail
        self.tail_fit: Optional[FittedTail] = tail_fit
        self.arx_feature: Optional[str] = arx_feature
        self.arx: Optional[FittedArx] = arx
        self.calibration_folds: Optional[int] = calibration_folds
        self.calibration_blocks: Tuple[_ExcludingModel, ...] = tuple(calibration_blocks)
        self.volatility_feature: Optional[str] = volatility_feature
        self.garch_parameters: Optional[Tuple[float, float, float]] = (
            None if garch_parameters is None else tuple(garch_parameters)
        )
        self.garch_initial_variance: Optional[float] = garch_initial_variance
        self.spread_change_lags: Optional[int] = spread_change_lags
        self._history_dates: Tuple[date, ...] = tuple(when for when, _ in history)
        self._history_spreads: Tuple[Optional[float], ...] = tuple(
            spread for _, spread in history
        )
        self.ml_libraries: Mapping[str, str] = MappingProxyType(dict(ml_libraries))
        self.calibration: str = calibration
        self.calibration_share: Optional[float] = calibration_share
        self.widening: float = float(widening)
        self.fit_end: date = cutoff if fit_end is None else fit_end
        self.calibration_start: Optional[date] = calibration_start
        self.calibration_end: Optional[date] = calibration_end
        self.regressors: Tuple[str, ...] = tuple(regressors)
        self._estimators: Tuple[Any, ...] = tuple(estimators)
        self.imputations: Mapping[str, float] = MappingProxyType(
            {
                name: float(imputations[name])
                for name in self.regressors
                + _spread_change_names(spread_change_lags or 0)
            }
        )
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self._last_law: Optional[
            Tuple[
                Tuple[date, Tuple[Tuple[str, Optional[float]], ...]],
                Tuple[Tuple[float, ...], Tuple[float, ...]],
            ]
        ] = None
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)
        self.random_state: int = int(random_state)
        if len(self._estimators) != len(self.levels):
            raise ValueError(
                f"{len(self._estimators)} fitted estimators against "
                f"{len(self.levels)} declared levels; one fit per level is what "
                f"makes the reported vector a quantile vector"
            )

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedGradientBoostedQuantiles(cutoff={self.cutoff.isoformat()}, "
            f"regressors={list(self.regressors)}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def design_names(self) -> Tuple[str, ...]:
        """The design column order. `design_row(row)[i]` is column `[i]`.

        No intercept: a tree ensemble has no coefficient for one, and reporting
        a column the model does not read would put `features_read` --- which is
        derived from this --- out of step with the fit.

        The lag columns come after the regressors, lag 1 first, then the GARCH
        variance, and the ARX forecast last.
        """

        return (
            ("spread_bps",)
            + self.regressors
            + _spread_change_names(self.spread_change_lags or 0)
            + ((_GARCH_COLUMN,) if self.volatility_feature is not None else ())
            + ((_ARX_COLUMN,) if self.arx_feature is not None else ())
        )

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The training residuals about this model's own centre, ascending."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """Every panel column this model reads off a feature row.

        Derived from `design_names` rather than rebuilt from `regressors`, for
        the reason `FittedArx.features_read` is: `design_row` reads the row in
        `design_names` order, so anything that column order gains this answer
        gains too.

        **Except the lag columns, the GARCH variance and the ARX forecast, which
        are not panel columns.** Each is read off `spread_bps` -- the ARX
        forecast off `spread_bps` and the declared regressors -- on rows at or
        before the feature row, and every one of those is already here. Naming
        `spread_change_lag_1`, `garch11_variance` or `arx_forecast` would ask
        the purge check to find a source for a column no source ingests.
        """

        return self.design_names[: 1 + len(self.regressors)]

    @property
    def model_settings(self) -> Mapping[str, Any]:
        """The calibration settings a record names, keyed as the command line spells them.

        Read by `baseline._model_settings`, which cannot import this module and
        so cannot ask `isinstance`. Empty under `calibration="none"` -- absent,
        not `"none"` -- so a record of the uncalibrated model declares exactly
        what every gbm record published before calibration existed declares.
        `spread_change_lags`, `volatility_feature`, `arx_feature`, `tail` and
        `training_pairs` and `calibration_masking` by the same rule: named when set, absent when not. Each calibration names its own setting and
        only its own: `calibration_share` for `conformal` and
        `conformal_asymmetric`, `calibration_folds` for `cross_conformal`,
        `cross_conformal_asymmetric`, `cross_conformal_scaled` and
        `cross_conformal_partial`.

        `tail` is what the command declared, not evidence that a shape was
        fitted: a rolling backtest refits at every origin, so what each fold's
        `tail_fit` found is not recorded here. It is `tail_account`'s, read per
        fold (B38).
        """

        settings: dict = {}
        if self.calibration in ("conformal", "conformal_asymmetric"):
            settings["calibration"] = self.calibration
            settings["calibration_share"] = self.calibration_share
        elif self.calibration in _CROSS_CALIBRATIONS:
            settings["calibration"] = self.calibration
            settings["calibration_folds"] = self.calibration_folds
        if self.spread_change_lags is not None:
            settings["spread_change_lags"] = self.spread_change_lags
        if self.volatility_feature is not None:
            settings["volatility_feature"] = self.volatility_feature
        if self.arx_feature is not None:
            settings["arx_feature"] = self.arx_feature
        if self.tail is not None:
            settings["tail"] = self.tail
        if self.training_pairs is not None:
            settings["training_pairs"] = self.training_pairs
        if self.calibration_masking is not None:
            settings["calibration_masking"] = self.calibration_masking
        return MappingProxyType(settings)

    @property
    def tail_account(self) -> Optional[Mapping[str, Any]]:
        """What this fit's tail was, as a record names it, or `None` without one.

        Read by `baseline.rolling_persistence_backtest` off each fold's own
        fitted model, the one that fold scored, the way `model_settings` is
        read: `baseline` cannot import this module. Read unchanged by
        `baseline.rolling_exceedance_backtest` too, off the curves
        `gbm_exceedance` returns at each fold, which carry it from the model
        that produced them (B40). `None` under `tail=None`
        --- absent, not a state --- so a run without a tail records nothing.

        Under `tail="gpd"` one of `TAIL_STATES`, and only the numbers that
        state has:

        * `fitted` --- `xi`, `sigma`, `excesses` and `clamped`. A clamped shape
          is still this state and says so; see `FittedTail` on why it is not
          a shape the sample supported. `xi` is never negative (#63).
        * `fallback` --- `sigma` and `excesses`, and no `xi`. The fallback's
          `xi` is the `0.0` the family collapses to, not a fitted value, and
          a record carrying it would read as a shape of zero.
        * `no_excesses` --- `excesses` of `0` alone: `tail_fit` is `None` and
          there is nothing else to report.
        * `floored` --- `sigma`, `excesses` and `xi_estimate`, and no `xi`,
          like `fallback`: the raw shape was negative and the floor set it to
          zero, so the law is the fallback's exponential (#63). `xi_estimate`
          is the raw negative estimate. A separate state so a reader can count
          floored folds apart from shapes fitted non-negative, which is the sign
          split #63 raised.

        Read off `tail_fit`, the fit the law was continued with. The excesses
        are not kept, so nothing here could recompute it.

        **No ceiling since the floor (#63).** Until then a fitted negative
        shape also carried `upper_endpoint_excess`, `sigma / -xi`, the excess
        above the top declared quantile beyond which the tail gave probability
        exactly zero (B41). B44's `refused` was a fifth state, for a shape at
        or below `-0.5`. No fit makes either now. Published records still
        carry both, and `tail_diagnostics` reads them.

        Raises:
            ValueError: a `tail_fit` that is neither floored nor a fallback
                with a negative `xi`. `_fit_gpd_pwm` cannot return one, and
                this refuses to record one as `fitted`, with no ceiling, when
                its law has one.
        """

        if self.tail is None:
            return None
        fit = self.tail_fit
        if fit is None:
            account: dict = {"state": "no_excesses", "excesses": 0}
        elif fit.floored:
            account = {
                "state": "floored",
                "sigma": fit.sigma,
                "excesses": fit.excesses,
                "xi_estimate": fit.xi_estimate,
            }
        elif fit.fallback:
            account = {"state": "fallback", "sigma": fit.sigma, "excesses": fit.excesses}
        elif fit.xi < 0.0:
            raise ValueError(
                f"a fitted tail with a negative shape ({fit.xi!r}) is not one "
                f"this model publishes; a negative shape is floored at zero (#63)"
            )
        else:
            account = {
                "state": "fitted",
                "xi": fit.xi,
                "sigma": fit.sigma,
                "excesses": fit.excesses,
                "clamped": fit.clamped,
            }
        return MappingProxyType(account)

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?"""

        return feature_row.date < self.cutoff

    def design_row(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """The feature row as this model reads it, in `design_names` order.

        With lags, the rows before `feature_row` are the history's
        (`positional_history`): the fitted frame's, or the as-of history
        `with_history` handed over. The feature row's own spread ends lag 1. A
        row the history does not carry is refused: it has no position there,
        and the nearest one would hand it another row's lags.

        The GARCH variance by the same rule: the recursion is run with the
        fitted parameters through the history's rows before `feature_row` and
        then `feature_row`'s own spread, and its last value is the column.

        The ARX forecast is the fitted ARX's point forecast from `feature_row`,
        which reads that row and no other.
        """

        return self._design_row(
            feature_row,
            self.imputations,
            self.garch_parameters,
            self.garch_initial_variance,
            self.arx,
        )

    def _design_row(
        self,
        feature_row: DailyObservation,
        imputations: Mapping[str, float],
        garch_parameters: Optional[Tuple[float, float, float]],
        garch_initial_variance: Optional[float],
        arx: Optional[FittedArx] = None,
    ) -> Tuple[float, ...]:
        """`design_row` under one fit's imputations, GARCH parameters and ARX.

        The full fit's, or an excluding model's: the frame's rows are the
        history either way, because a forecast's inputs are every row at or
        before its feature row, and only what a fit *learned* differs.
        """

        changes: Sequence[Optional[float]] = ()
        variance: Optional[float] = None
        lags = self.spread_change_lags
        if lags is not None or self.volatility_feature is not None:
            spreads = self.positional_history(feature_row)
            position = len(spreads) - 1
            if lags is not None:
                changes = _spread_changes(
                    spreads, position, lags, f"feature row for {feature_row.date}"
                )
            if self.volatility_feature is not None:
                variance = _garch_variances(
                    _squared_changes(spreads),
                    garch_parameters,
                    garch_initial_variance,
                )[position]
        return tuple(
            _design(
                feature_row,
                self.regressors,
                imputations,
                "feature row",
                changes,
                variance,
                arx,
            )
        )

    @property
    def history_end(self) -> Optional[date]:
        """The last row of the history this model reads by position.

        `None` when it reads none: no lags, no GARCH variance and neither
        scaled calibration. Otherwise the fitted frame's last row, or, on a
        model `with_history` returned, the last row it was handed. The fold
        loops check it against the anchor of the forecast being made
        (`baseline._check_history_end`): a positional read that ends before
        the latest observable row is stale.
        """

        return self._history_dates[-1] if self._history_dates else None

    def with_history(
        self, history: Sequence[DailyObservation]
    ) -> "FittedGradientBoostedQuantiles":
        """This fit, reading history by position from `history` instead.

        What the fold loops hand a forecast made after its block's fit: the
        refit cadence bounds the training labels, not the forecast-time reads,
        and the rows between the fit and the forecast were public at the
        forecast's decision instant. `history` is the as-of frame at that
        instant, ending at its anchor, the feature row. Every fitted value is
        this model's own; only the rows lags, the GARCH recursion and the
        trailing scale are read from change, so a forecast here reads exactly
        the rows a fit made at its own decision would have.

        `self`, unchanged, when this model reads no history. The fitted
        frame's rows must be a prefix of `history`, date and spread alike: a
        history that rewrote a row the fit was made on is another panel, and
        is refused (`ValueError`) rather than read.
        """

        if not self._history_dates:
            return self
        rows = list(history)
        dates = tuple(row.date for row in rows)
        spreads = tuple(_observed_spread(row, "history row") for row in rows)
        fitted = len(self._history_dates)
        if (
            dates[:fitted] != self._history_dates
            or spreads[:fitted] != self._history_spreads
        ):
            raise ValueError(
                f"the history handed over ({dates[0] if dates else None}.."
                f"{dates[-1] if dates else None}) does not begin with the "
                f"{fitted} rows this model was fitted on "
                f"({self._history_dates[0]}..{self._history_dates[-1]}); a "
                f"positional read from it would not be this fit's history"
            )
        view = copy.copy(self)
        view._history_dates = dates
        view._history_spreads = spreads
        # The memo is keyed on the feature row alone, and the law now reads
        # another history: the copy starts without one.
        view._last_law = None
        return view

    def positional_history(
        self, feature_row: DailyObservation
    ) -> Tuple[Optional[float], ...]:
        """The spreads a positional read of `feature_row` sees, oldest first.

        The history's rows before `feature_row`, found by its date, then
        `feature_row`'s own spread, which is last: lags, the GARCH recursion
        and the trailing scale all end there. The one reader of the history
        by position, so no two of them can find a row two ways. A row the
        history does not carry is refused: it has no position, and the nearest
        one would hand it another row's history.
        """

        position = bisect_left(self._history_dates, feature_row.date)
        if (
            position == len(self._history_dates)
            or self._history_dates[position] != feature_row.date
        ):
            span = (
                f"{self._history_dates[0]}..{self._history_dates[-1]}"
                if self._history_dates
                else "no rows"
            )
            raise ValueError(
                f"feature row for {feature_row.date} is not a row of the "
                f"history this model reads ({span}); its lagged spread "
                f"changes, its GARCH variance and its trailing scale are read "
                f"off that history's own rows by position, and a row the "
                f"history does not carry has none"
            )
        return self._history_spreads[:position] + (
            _observed_spread(feature_row, "feature row"),
        )

    def _origin_scale(self, feature_row: DailyObservation) -> float:
        """`cross_conformal_scaled`'s and `cross_conformal_partial`'s scale at a forecast's feature row.

        `_trailing_scale` over `positional_history`: the history's spreads
        *before* the feature row and the feature row's own spread. The list
        handed over ends at the feature row, so no history row after it is
        reachable here whatever the window reads. A row the history does not
        carry, or one with no scale, is refused.
        """

        spreads = self.positional_history(feature_row)
        position = len(spreads) - 1
        scale = _trailing_scale(spreads, position)
        if scale is None:
            raise ValueError(
                f"feature row for {feature_row.date} has no scale: calibration "
                f"{self.calibration!r} reads the {SCALE_WINDOW} spread changes "
                f"ending at it, and its frame has {position} row(s) before it or "
                f"no observed change among them. A made-up scale would be a band "
                f"with no calibration behind it"
            )
        return scale

    def _quantile_vector(self, design_row: Sequence[float]) -> Tuple[float, ...]:
        """One design row's rearranged quantile vector. See `_rearranged`."""

        return _rearranged(self._estimators, [design_row])[0]

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The rearranged median: the centre the reported quantiles agree on.

        Read out of `predict`'s own vector rather than off the `0.50` estimator
        directly. The two differ exactly when that estimator crossed one of its
        neighbours, and in that case the estimator's value is not the middle of
        the distribution this model reports.
        """

        return self.predict(feature_row)[self.levels.index(_MEDIAN_LEVEL)]

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        Non-decreasing by construction: `_quantile_vector` sorts, and
        `_calibrated` stops an outer level at its neighbour. A zero widening --
        every uncalibrated model -- touches nothing, so no reported value moves
        by so much as the sign of a zero.
        """

        return self._reported(feature_row)[0]

    def _reported(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], float, float]:
        """The reported vector, and how far its lower and upper edges were moved out.

        The full fit's rearranged vector in every case; a calibration moves only
        its two outer levels. Under `cross_conformal` the edges are CV+'s, read
        off every excluding model at this feature row. Under
        `conformal_asymmetric` each edge moves by its own `edge_widenings`
        entry, through `_banded`'s neighbour rule. Under
        `cross_conformal_asymmetric` the edges are CV+'s over each block's two
        signed score sets, at each side's own rank. Under
        `cross_conformal_scaled` they are CV+'s over each excluding model's
        median plus and minus this row's scale times its block's scaled
        residuals, at `cross_conformal`'s ranks. Under
        `cross_conformal_partial` they are CV+'s over each excluding model's
        own lower and upper edges moved out by this row's `_partial_factor`
        times its block's `partial_scores`, at `cross_conformal`'s ranks.
        """

        vector = self._quantile_vector(self.design_row(feature_row))
        if self.calibration == _SCALED_CALIBRATION:
            scale = self._origin_scale(feature_row)
            centre = self.levels.index(_MEDIAN_LEVEL)
            lows: List[float] = []
            highs: List[float] = []
            for block in self.calibration_blocks:
                if not block.scaled_residuals:
                    continue
                middle = _rearranged(
                    block.estimators,
                    [
                        self._design_row(
                            feature_row,
                            block.imputations,
                            block.garch_parameters,
                            block.garch_initial_variance,
                            block.arx,
                        )
                    ],
                )[0][centre]
                lows.extend(middle - scale * score for score in block.scaled_residuals)
                highs.extend(middle + scale * score for score in block.scaled_residuals)
            lower, upper = _cross_conformal_edges(lows, highs, self.levels)
            return _banded(vector, lower, upper), vector[0] - lower, upper - vector[-1]
        if self.calibration == "conformal_asymmetric":
            down, up = self.edge_widenings
            return _banded(vector, vector[0] - down, vector[-1] + up), down, up
        if self.calibration in _CROSS_CALIBRATIONS:
            asymmetric = self.calibration == "cross_conformal_asymmetric"
            partial = self.calibration == _PARTIAL_CALIBRATION
            factor = (
                _partial_factor(self._origin_scale(feature_row)) if partial else None
            )
            lows: List[float] = []
            highs: List[float] = []
            for block in self.calibration_blocks:
                if not block.scores:
                    continue
                excluded = _rearranged(
                    block.estimators,
                    [
                        self._design_row(
                            feature_row,
                            block.imputations,
                            block.garch_parameters,
                            block.garch_initial_variance,
                            block.arx,
                        )
                    ],
                )[0]
                if asymmetric:
                    lows.extend(excluded[0] - score for score in block.lower_scores)
                    highs.extend(excluded[-1] + score for score in block.upper_scores)
                    continue
                if partial:
                    lows.extend(excluded[0] - factor * score for score in block.partial_scores)
                    highs.extend(excluded[-1] + factor * score for score in block.partial_scores)
                    continue
                lows.extend(excluded[0] - score for score in block.scores)
                highs.extend(excluded[-1] + score for score in block.scores)
            lower, upper = (
                _cross_conformal_asymmetric_edges(lows, highs, self.levels)
                if asymmetric
                else _cross_conformal_edges(lows, highs, self.levels)
            )
            return _banded(vector, lower, upper), vector[0] - lower, upper - vector[-1]
        if not self.widening:
            return vector, 0.0, 0.0
        return _calibrated(vector, self.widening), self.widening, self.widening

    def _law(self, feature_row: DailyObservation) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """The predictive law for one row, as `(values, levels)` knots.

        `values` is strictly ascending except where two fits agree exactly, and
        `levels` runs `0.0 .. 1.0`. The interior knots are the rearranged
        quantile vector at the declared levels; the two outer knots are where
        the law runs out.

        **The outer knots are the fitted residual range about this row's
        centre.** The model's own evidence about how far the target strays from
        the centre it predicts is its training residual sample, so
        `anchor + min(residuals)` and `anchor + max(residuals)` are where its
        mass stops --- no Gaussian tail, no parametric family, no smoothing, for
        the reason `climatology_exceedance` gives at length. They are widened,
        and only widened, when a row's own declared band would otherwise escape
        them: a knot set that is not increasing is not a distribution, and a
        band wider than the residual range is the model saying this row is
        unusual, which is not something to clip away. `_TAIL_SHARE` of the
        band's own width is the width used then.

        Under a calibration the residual range moves out with the band, by the
        same widening, so the tail knots stay where the calibrated band puts the
        law's edges rather than where the in-sample fit did. Under
        `cross_conformal` each tail moves by as much as its own edge did.
        """

        interior, down, up = self._reported(feature_row)
        return _law_knots(
            interior, down, up, self._residuals[0], self._residuals[-1], self.levels
        )

    def cross_conformal_parts(self, feature_row: DailyObservation) -> "CrossConformalParts":
        """What CV+'s band at `feature_row` is built from, for a recalibration (#116).

        The full fit's rearranged vector before its edges move, every
        held-out row's terms `Q_lo_-k(i)(x) - s_i` and `Q_hi_-k(i)(x) + s_i`
        read at this feature row, in block and date order, with each row's
        date, and the residual range the law's tails are laid from.
        `_banded(vector, *_cross_conformal_edges(lows, highs, levels))` is
        `predict`'s vector, and `law_from_band` at those edges is
        `law_knots`', bit for bit: the terms are computed exactly as
        `_reported` computes them.

        Raises:
            ValueError: unless this model is calibrated by `cross_conformal`
                and carries no tail; under any other calibration the terms are
                not CV+'s, and a tail's law is not `law_from_band`'s.
        """

        if self.calibration != "cross_conformal" or self.tail_fit is not None:
            raise ValueError(
                f"cross_conformal_parts reads a cross_conformal fit with no tail; "
                f"this one is calibrated by {self.calibration!r}"
                f"{' and carries a tail' if self.tail_fit is not None else ''}"
            )
        vector = self._quantile_vector(self.design_row(feature_row))
        dates: List[date] = []
        lows: List[float] = []
        highs: List[float] = []
        for block in self.calibration_blocks:
            if not block.scores:
                continue
            excluded = _rearranged(
                block.estimators,
                [
                    self._design_row(
                        feature_row,
                        block.imputations,
                        block.garch_parameters,
                        block.garch_initial_variance,
                        block.arx,
                    )
                ],
            )[0]
            dates.extend(block.scored_dates)
            lows.extend(excluded[0] - score for score in block.scores)
            highs.extend(excluded[-1] + score for score in block.scores)
        return CrossConformalParts(
            vector,
            tuple(dates),
            tuple(lows),
            tuple(highs),
            self._residuals[0],
            self._residuals[-1],
        )

    def _shared_law(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """`_law` for one row, evaluated **once** however many callers ask.

        Both `law_knots` and `predict_stress` come through here, and that is the
        point: a record that carries the knots beside the probabilities read off
        them has to be able to say the two came from one evaluation of one fit.
        Two evaluations of a deterministic fit agree, so nothing a caller can
        assert afterwards distinguishes "derived" from "re-derived" --- the
        distinction is in the call graph or it is nowhere, which is why it is
        built here rather than checked downstream.

        A memo of one row, keyed on the row's date and its columns, because a
        scoring job walks rows in order and asks about each one twice. The key
        is compared by value, so a row rebuilt from the same numbers hits and a
        row carrying a `NaN` column misses forever; a miss costs an extra
        evaluation and changes no answer, which is the direction a cache is
        allowed to be wrong in. A failed evaluation is not memoised: the
        refusal propagates before the slot is written.
        """

        key = (
            feature_row.date,
            tuple(sorted(feature_row.values.items(), key=lambda item: item[0])),
        )
        remembered = self._last_law
        if remembered is not None and remembered[0] == key:
            return remembered[1]
        law = self._law(feature_row)
        self._last_law = (key, law)
        return law

    def law_knots(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """This row's predictive law as `(values, levels)` knots.

        The law `predict_stress` inverts, handed out rather than described:
        `values` is non-decreasing and `levels` is `(0.0,) + self.levels +
        (1.0,)`, and `P(spread > tau)` for any `tau` is fixed by the pair. What
        it buys a caller is *where* a tau fell --- a tau above the top declared
        level is read inside the single segment `[Q(0.95), high]`, and a curve
        that flattens because every tau it was asked about landed in one
        straight segment looks exactly like a curve that flattened because the
        learner had nothing to say. Only the knots tell the two apart, and
        `predict_stress` returns floats and throws them away.

        The same evaluation `predict_stress` uses for that row, not a second
        one; see `_shared_law`. A feature row missing a declared regressor
        raises `MissingRegressorError` from the fit's own read of it, uncaught
        --- a caller asking where its tau fell on a row the model cannot read
        is asking the wrong question, and a knot set invented to answer it
        would be the worst possible answer.
        """

        return self._shared_law(feature_row)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, read off the law `predict` reports.

        The exceedance is the *inverse of the reported quantile vector*, not a
        second opinion about it: at a declared level `q`, `predict` reports the
        quantile `Q(q)` and this places exactly `1 - q` above it, because the
        pair `(Q(q), q)` is one of the knots interpolated between. That is the
        contract's "an exceedance derived from the predictive distribution", and
        it is what `ForecastInterfaceConformance::
        test_predict_stress_agrees_with_the_quantiles_predict_reports` checks.

        Nothing here was fitted to a `stress_gt_*` label column.

        The interpolation is linear in level between neighbouring knots and
        saturates outside them --- 1.0 below the lowest, 0.0 at or above the
        highest --- which is `_exceedance_from_residuals`' convention, one level
        up: that function inverts an *empirical sample* read at positions
        `k / (n - 1)`, and this inverts a *declared grid* read at its own
        levels. The two are the same map wherever the sample and the grid agree,
        and this model's grid is the contract's rather than a sample's, so the
        inversion is written against the grid rather than routed through a
        sample that would have to be manufactured to hold it.

        Ties are the one place the inversion is approximate, exactly as there: if
        two fits agree to the last bit the knot set is flat over a range of
        levels and has no single inverse, and the higher level is returned.

        `law_knots` hands out the knots these floats were read off, from this
        same evaluation, for a caller that needs to know which segment a tau
        landed in and not only what came out.

        Under `tail="gpd"` with a fitted `tail_fit`, a tau strictly above the
        top declared quantile `values[-2]` is read off the fitted tail instead,
        as `(1 - levels[-1]) * S(tau - values[-2])`; see the module docstring.
        At and below that knot, and with no `tail_fit`, nothing changes.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        values, levels = self._shared_law(feature_row)
        if self.tail_fit is None:
            return tuple(_exceedance_from_law(values, levels, tau) for tau in family)
        threshold = values[-2]
        return tuple(
            (1.0 - self.levels[-1]) * _gpd_survival(self.tail_fit, tau - threshold)
            if tau > threshold
            else _exceedance_from_law(values, levels, tau)
            for tau in family
        )


class CrossConformalParts(NamedTuple):
    """`FittedGradientBoostedQuantiles.cross_conformal_parts` for one feature row."""

    vector: Tuple[float, ...]
    held_out_dates: Tuple[date, ...]
    lows: Tuple[float, ...]
    highs: Tuple[float, ...]
    residual_low: float
    residual_high: float


def _law_knots(
    interior: Sequence[float],
    down: float,
    up: float,
    residual_low: float,
    residual_high: float,
    levels: Sequence[float],
) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """`FittedGradientBoostedQuantiles._law`'s knots from its parts; see there."""

    interior = tuple(interior)
    anchor = interior[tuple(levels).index(_MEDIAN_LEVEL)]
    pad = max(_TAIL_SHARE * (interior[-1] - interior[0]), _MINIMUM_TAIL)
    bottom = anchor + residual_low
    top = anchor + residual_high
    if down or up:
        bottom -= down
        top += up
    low = bottom if bottom < interior[0] else interior[0] - pad
    high = top if top > interior[-1] else interior[-1] + pad
    return (low,) + interior + (high,), (0.0,) + tuple(levels) + (1.0,)


def law_from_band(
    vector: Sequence[float],
    lower: float,
    upper: float,
    residual_low: float,
    residual_high: float,
    levels: Sequence[float],
) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """The law of an uncalibrated `vector` whose band edges move to `lower`, `upper`.

    `_law`'s rule for a calibrated fit, given the pieces
    `cross_conformal_parts` hands out: the outer levels move by `_banded`'s
    neighbour rule, and each tail by as much as its own edge did. At CV+'s
    edges it is `law_knots`; at another calibration's edges it is the law that
    calibration would report (#116).
    """

    return _law_knots(
        _banded(vector, lower, upper),
        vector[0] - lower,
        upper - vector[-1],
        residual_low,
        residual_high,
        levels,
    )


def _rearranged(
    estimators: Sequence[Any], design_rows: Sequence[Sequence[float]]
) -> Tuple[Tuple[float, ...], ...]:
    """Each design row read at every level, **rearranged by sorting**.

    The single place a predicted vector is produced --- `predict`,
    `point_forecast`, the fitted residual sample and the law `predict_stress`
    inverts all come through here, so a caller cannot be shown a rearranged
    vector beside an exceedance derived from a crossed one. Written as a module
    function rather than a method because the fit needs it before there is a
    fitted object to call it on, and a second spelling of the rearrangement in
    the fitter is exactly the drift this centralisation prevents.

    One `predict` call per estimator over the whole batch rather than one per
    row per estimator: a rolling backtest refits at every origin, and the
    per-row form made the residual sample `n` times more estimator calls than
    it needs to be.
    """

    rows = [[float(value) for value in row] for row in design_rows]
    columns = [
        [float(value) for value in estimator.predict(rows)]
        for estimator in estimators
    ]
    return tuple(
        tuple(sorted(column[index] for column in columns))
        for index in range(len(rows))
    )


def _exceedance_from_law(
    values: Sequence[float], levels: Sequence[float], tau: float
) -> float:
    """`P(Y > tau)` under the piecewise-linear law `(values, levels)`.

    Walks the quantile map backwards, as `baseline._exceedance_from_residuals`
    does for an empirical sample: find the segment `tau` sits in, convert its
    position along that segment into a level, and return the mass above it.
    """

    if tau < values[0]:
        return 1.0
    if tau >= values[-1]:
        return 0.0
    lower = bisect_right(values, tau) - 1
    span = values[lower + 1] - values[lower]
    weight = 0.0 if span <= 0.0 else (tau - values[lower]) / span
    level = levels[lower] + weight * (levels[lower + 1] - levels[lower])
    return 1.0 - level


def _training_design(
    rows: Sequence[DailyObservation],
    dates: Sequence[date],
    spreads: Sequence[Optional[float]],
    garch_spreads: Sequence[Optional[float]],
    origins: Sequence[int],
    names: Tuple[str, ...],
    lags: int,
    volatility_feature: Optional[str],
    label: str,
    arx_feature: Optional[str] = None,
    arx_frame: Sequence[DailyObservation] = (),
    arx_origins: Optional[Sequence[int]] = None,
    pairs: Optional[Sequence[Tuple[int, DailyObservation, int]]] = None,
) -> Tuple[
    Mapping[str, float],
    Optional[Tuple[float, float, float]],
    Optional[float],
    List[List[float]],
    List[float],
    List[float],
    Optional[FittedArx],
]:
    """One fit's imputations, GARCH, ARX, design and targets, over the pairs at `origins`.

    `origins` are frame positions `p` whose one-step pair `(p, p + 1)` trains;
    every one is at least `lags`. `pairs`, when given, replaces them with
    direct pairs `(anchor, observation, target)` from `_direct_pairs`: the
    lags and variance are read at `anchor`, the regressors off `observation`,
    and the target is row `target`'s spread. `spreads` is what the training lags and
    variances are read off -- the frame's own, or, for an excluding model, the
    frame's with every row it may not train on made a hole -- and
    `garch_spreads` what the GARCH is fitted on. The ARX is `fit_arx` on
    `arx_frame`, at `arx_origins` when given. The one spelling the full fit,
    the split-conformal fit and every excluding model share: two spellings of
    one design is how two models stop being comparable.

    Returns `(imputations, garch_parameters, garch_initial_variance, design,
    targets, variances, arx)`, `variances` being the recursion filtered over
    `spreads` (empty without the volatility feature) and `arx` `None` without
    the ARX feature.
    """

    change_names = _spread_change_names(lags)
    if pairs is None:
        pairs = [(position, rows[position], position + 1) for position in origins]
    origins = [anchor for anchor, _, _ in pairs]

    # The GARCH(1,1), fitted on `garch_spreads` and nothing after them, then
    # filtered over `spreads` with those parameters: rows it did not fit on are
    # run through the recursion, never fitted on. `variances[p]` reads rows at
    # or before `p`.
    garch: Optional[Tuple[float, float, float]] = None
    initial: Optional[float] = None
    variances: List[float] = []
    if volatility_feature is not None:
        garch, initial = _fit_garch11(garch_spreads, label)
        variances = _garch_variances(_squared_changes(spreads), garch, initial)

    # The imputation is fitted on the origins and only these -- contract test
    # 3's "recomputed on a training window alone", the same rows `fit_arx` uses.
    changes = [
        _spread_changes(spreads, position, lags, f"training row for {dates[position]}")
        for position in origins
    ]
    if lags and not any(None not in row_changes for row_changes in changes):
        raise ValueError(
            f"spread_change_lags {lags} leaves no training row with every lag "
            f"defined: none of the {len(changes)} training rows of the {label} "
            f"with {lags} rows before them observes all {lags}. A lag imputed "
            f"on every design row is a column of training means, not a regressor"
        )
    observed: Mapping[str, List[float]] = {name: [] for name in names + change_names}
    for row_changes in changes:
        for name, change in zip(change_names, row_changes):
            if change is not None:
                observed[name].append(change)
    for _, feature, _ in pairs:
        for name in names:
            value = _raw_regressor(feature, name, "training row")
            if value is not None:
                observed[name].append(value)

    imputations = {}
    for name in names:
        seen = observed[name]
        if not seen:
            raise ValueError(
                f"regressor {name!r} is unobserved on every row of the training "
                f"window ({dates[origins[0]]}..{dates[origins[-1]]}); there is "
                f"nothing to fit an imputation from, and filling it with 0.0 would "
                f"be the coercion contract test 5 prohibits"
            )
        imputations[name] = sum(seen) / len(seen)
    for name in change_names:
        seen = observed[name]
        imputations[name] = sum(seen) / len(seen)

    # The ARX, by `baseline.fit_arx` and no second fitter, on the declared
    # regressors and the rows this fit trains on. Its own minimum and its own
    # refusals: the defaults, not gbm's `minimum_history`, which is a statement
    # about the frame rather than about the rows the ARX is handed.
    arx: Optional[FittedArx] = None
    if arx_feature is not None:
        arx = fit_arx(arx_frame, names, origins=arx_origins)

    design = []
    targets = []
    for (position, feature, target), row_changes in zip(pairs, changes):
        # The origin's variance and ARX forecast, `position`: the target row's
        # would read the target.
        design.append(
            _design(
                feature,
                names,
                imputations,
                "training row",
                row_changes,
                variances[position] if variances else None,
                arx,
            )
        )
        targets.append(float(rows[target].spread_bps))
    return imputations, garch, initial, design, targets, variances, arx


def _direct_pairs(
    information: InformationRule,
    rows: Sequence[DailyObservation],
    dates: Sequence[date],
    targets: Sequence[int],
    lags: int,
    kept: Optional[Sequence[bool]] = None,
) -> Tuple[List[Tuple[int, DailyObservation, int]], List[int]]:
    """The direct pairs at `targets`, and every row they read (#37).

    Each target `t` is paired with its as-of read at its own decision instant,
    checked by both guards, as `_held_out_read` reads a held-out row. A target
    with no read, or whose anchor has fewer than `lags` rows before it, trains
    no pair. With `kept`, a pair trains only if its target and every row its
    read touches are kept: an excluding model reads nothing of its block
    through a feature.

    Returns `(pairs, read)`: the `(anchor, observation, target)` triples in
    target order, and the ascending positions of every row they read,
    targets included.
    """

    pairs: List[Tuple[int, DailyObservation, int]] = []
    read: set = set()
    for target in targets:
        if target < 1:
            continue
        try:
            info = information.information_set(dates, target)
        except SplitError:
            continue
        information.check(dates, info)
        if info.anchor < lags:
            continue
        touched = {target, info.anchor, *(field.row for field in info.reads)}
        if kept is not None and not all(kept[position] for position in touched):
            continue
        pairs.append((info.anchor, information.observation(rows, info), target))
        read.update(touched)
    return pairs, sorted(read)


def _fitted_levels(
    estimator_class: Any,
    grid: Sequence[float],
    design: Sequence[Sequence[float]],
    targets: Sequence[float],
    random_state: int,
    min_samples_leaf: int,
) -> List[Any]:
    """One estimator per level, fitted on `design` and `targets`, in level order."""

    estimators = []
    for level in grid:
        estimator = estimator_class(
            loss="quantile",
            quantile=level,
            # Both explicit, both load-bearing. See the module docstring: the
            # `"auto"` default turns early stopping on above 10 000 rows and
            # draws a validation split, so a model that is reproducible on a
            # fixture stops being reproducible on a panel.
            early_stopping=False,
            random_state=random_state,
            min_samples_leaf=min_samples_leaf,
        )
        estimator.fit(design, targets)
        estimators.append(estimator)
    return estimators


def _require_information(information: object, calibration: str) -> None:
    """Refuse a calibration that was handed no as-of rule to split by."""

    if not isinstance(information, InformationRule):
        raise SplitError(
            f"calibration {calibration!r} scores held-out rows as forecasts and "
            f"needs the run's as-of rule to read them (information=), got "
            f"{information!r}; a calibration split with no rule is a split "
            f"nobody declared"
        )


def _held_out_read(
    information: InformationRule,
    rows: Sequence[DailyObservation],
    dates: Sequence[date],
    index: int,
) -> Optional[Tuple[int, DailyObservation]]:
    """A held-out row's anchor and as-of feature row, or `None` if it has none.

    The frame's own rows and dates, so business days are counted on the frame;
    every read is at or before the row's decision instant, which is inside the
    frame, and is checked both ways by `InformationRule.check`.
    """

    if index < 1:
        return None
    try:
        info = information.information_set(dates, index)
    except SplitError:
        return None
    information.check(dates, info)
    return info.anchor, information.observation(rows, info)


def _held_out_mask(
    information: InformationRule,
    rows: Sequence[DailyObservation],
    dates: Sequence[date],
    before: int,
    index: int,
) -> Tuple[Tuple[int, Tuple[str, ...]], ...]:
    """The declared values before a block that held-out row `index` could not yet see.

    `(position, columns)` for every row at or before `before` -- the last row
    the block's excluding model may train on before the block -- whose
    declared `columns` carry a value in the frame that `InformationRule.frame`
    holes at `index`'s own decision instant, ascending by position. Empty when
    every such value was public by then. The frame masks only its tail, so the
    scan stops at the first row the held-out row's frame leaves as it is.
    """

    if before < 0:
        return ()
    seen = information.frame(rows, information.information_set(dates, index))
    mask = []
    for position in range(before, -1, -1):
        if seen[position] is rows[position]:
            break
        columns = tuple(
            sorted(
                column
                for column, value in seen[position].values.items()
                if value is None and rows[position].values.get(column) is not None
            )
        )
        if columns:
            mask.append((position, columns))
    return tuple(reversed(mask))


def _masked_rows(
    rows: Sequence[DailyObservation], mask: Sequence[Tuple[int, Tuple[str, ...]]]
) -> Sequence[DailyObservation]:
    """`rows` with every value `mask` names made a hole; `rows` itself when it names none."""

    if not mask:
        return rows
    out = list(rows)
    for position, columns in mask:
        values = dict(out[position].values)
        for column in columns:
            values[column] = None
        out[position] = DailyObservation(out[position].date, values)
    return out


def fit_gradient_boosted_quantiles(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples_leaf: int = 20,
    calibration: str = "none",
    calibration_share: Optional[float] = None,
    information: Optional[InformationRule] = None,
    spread_change_lags: Optional[int] = None,
    volatility_feature: Optional[str] = None,
    calibration_folds: Optional[int] = None,
    arx_feature: Optional[str] = None,
    tail: Optional[str] = None,
    calibration_masking: Optional[str] = None,
    training_pairs: Optional[str] = None,
) -> FittedGradientBoostedQuantiles:
    """Fit one gradient-boosted quantile regressor per level and return the model.

    Args:
        train_frame: the training rows, strictly ascending by date. The design is
            this frame's own one-step-ahead pairs and nothing else, so a fit on
            `n` rows has `n - 1` design rows --- the same count, and the same
            construction, as `fit_arx`.
        regressors: the ordered exogenous regressor names. **Required, with no
            default**, for the reason `fit_arx` refuses one: a default would be a
            silent assumption about which columns a model is entitled to read.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date.
        minimum_history: the shortest frame that may produce a fitted model.
        levels: the quantile grid, defaulting to the declared one. Must contain
            `0.50`; see `_MEDIAN_LEVEL`.
        random_state: the seed handed to every fit. See `DEFAULT_RANDOM_STATE`.
        min_samples_leaf: passed straight to the estimator. Present because a
            fixture-sized frame cannot be split at scikit-learn's default at
            all, not as a tuned value --- tuning is not this block's.
        calibration: one of `CALIBRATIONS`. `"none"`, the default, fits every
            row and reports the band as fitted; `"conformal"` holds out the
            most recent rows and widens the band by their conformal score;
            `"cross_conformal"` reports the full fit and moves its band to
            CV+'s edges over `calibration_folds` date blocks;
            `"conformal_asymmetric"` splits as `"conformal"` does and moves
            each edge by its own side's score;
            `"cross_conformal_asymmetric"` blocks as `"cross_conformal"` does
            and takes each edge off its own side's signed scores at its own
            side's rank; `"cross_conformal_scaled"` blocks as
            `"cross_conformal"` does and divides each residual by a trailing
            scale read at its own feature row; `"cross_conformal_partial"`
            blocks as `"cross_conformal"` does, keeps its score and edges, and
            divides each score by that scale to the power
            `PARTIAL_SCALE_EXPONENT`. See the module docstring.
        calibration_share: the share of the frame held out as calibration rows,
            strictly inside `(0, 1)`. `None` means `DEFAULT_CALIBRATION_SHARE`
            under `conformal`, and is the only value `none` accepts: a share
            handed to a model that holds nothing out would be read as a setting
            that took effect.
        information: the run's `asof.InformationRule`, handed over by the fold
            loop (`baseline._fit_at_origin`) and never built here. A
            calibration scores held-out rows as forecasts, so it reads each
            one's feature row as the rule reads it at that row's own decision
            instant, and trains its fit rows (or excluding models) only on
            labels observable there: before a held-out block, the rows at or
            before its first row's anchor; after it, the rows whose own anchor
            reaches past the block. Required under every calibration; read by
            nothing under `none`, which splits nothing.
        spread_change_lags: how many lagged spread changes the design carries,
            at least 1. `None`, the default, carries none and is the model every
            published gbm record was produced with. See the module docstring.
        volatility_feature: one of `VOLATILITY_FEATURES`, or `None`, the
            default, which carries no volatility column and is the model every
            published gbm record was produced with. `"garch11"` fits a
            GARCH(1,1) on the fit rows' spread changes and adds its one-step
            conditional variance. See the module docstring.
        calibration_folds: the contiguous date blocks `cross_conformal`,
            `cross_conformal_asymmetric`, `cross_conformal_scaled` and
            `cross_conformal_partial` split the frame into, an int of at least
            2. `None` means `DEFAULT_CALIBRATION_FOLDS` under all four, and is the
            only value the other calibrations accept, for `calibration_share`'s
            reason; `calibration_share` is refused under `cross_conformal` by
            the same rule.
        arx_feature: one of `ARX_FEATURES`, or `None`, the default, which
            carries no ARX column and is the model every published gbm record
            was produced with. `"declared"` fits `baseline.fit_arx` on the fit
            rows over `regressors` and adds its one-step point forecast. See
            the module docstring.
        tail: one of `TAIL_FAMILIES`, or `None`, the default, which ends the
            law at its knots and is the model every published gbm record was
            produced with. `"gpd"` fits `_fit_gpd_pwm` to the calibration
            rows' residual excesses above their reported top quantile and
            continues the law above that quantile with it; `conformal` only.
            See the module docstring.
        calibration_masking: one of `CALIBRATION_MASKINGS`, or `None`, the
            default, which trains each excluding model on the frame as the
            fold masked it and is the model every published record was
            produced with. `"held_out_row"` scores each held-out row with an
            excluding model whose training rows before its block carry only
            the declared values public at that row's own decision instant.
            Cross-conformal calibrations only. See the module docstring.
        training_pairs: one of `TRAINING_PAIRS`, or `None`, the default,
            which trains on one-step pairs and is the model every published
            gbm record was produced with. `"direct"` pairs each target row
            with its own as-of read, the gap a forecast is served at, and
            needs `information`. See the module docstring.

    Returns:
        A `FittedGradientBoostedQuantiles` carrying its fitted estimators, its
        regressor names, its fitted imputation means, its sorted residuals, its
        cutoff, and its calibration: the settings, the widening and the dates
        of both slices.

    Raises:
        MissingMLExtraError: if the optional `ml` extra is not installed.
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date, or if a
            calibration is given no `information`.
        MissingRegressorError: if a training row does not carry a declared
            regressor.
        MetricError: if a declared level is outside `(0, 1)`, or the grid is not
            strictly ascending. `MetricError` is a `ValueError`, and the phrase
            is `metrics._validate_levels`' own: one statement of what a quantile
            level may be, not a second one here.
        ValueError: if no regressors are declared, if one is declared twice, if
            the grid does not carry `0.50`, if the frame is shorter than
            `minimum_history`, if a regressor is unobserved on every row of
            the training window; and, for the calibration, if `calibration`
            is not one of `CALIBRATIONS`, if `calibration_share` is outside
            `(0, 1)` or is given to `none`, if the calibration slice holds
            fewer rows than the conformal quantile needs to be finite, or if
            label observability leaves fewer than two fit rows; and, for the
            cross-conformal calibration, if `calibration_folds` is not an int
            of at least 2 or is given to another calibration, if
            `calibration_share` is given to it, if a block holds out no row or
            leaves its excluding model no training pair after the purge, or if
            fewer held-out rows are scored than CV+'s ranks need; and, for the
            lags, if
            `spread_change_lags` is not an int of at least 1, if it leaves no
            training row with every lag defined, or if a calibration row's
            feature row has fewer rows than that before it; and, for the
            volatility feature, if `volatility_feature` is not one of
            `VOLATILITY_FEATURES`, if the fit rows carry fewer than
            `GARCH_MINIMUM_CHANGES` observed spread changes, or if the GARCH
            fit does not converge; and, for the ARX feature, if `arx_feature`
            is not one of `ARX_FEATURES`. Whatever `baseline.fit_arx` raises
            on the rows it is handed -- fewer than its default minimum, a
            singular design -- propagates as it raised it; and, for the tail,
            if `tail` is not one of `TAIL_FAMILIES`, or is given with
            calibration `none` (an in-sample tail), `cross_conformal`,
            `conformal_asymmetric`, `cross_conformal_asymmetric`,
            `cross_conformal_scaled` or `cross_conformal_partial` (not wired). Under `conformal_asymmetric` and
            `cross_conformal_asymmetric` the score floor is the per-side one,
            not `conformal`'s or `cross_conformal`'s; and, for the masking, if
            `calibration_masking` is not one of `CALIBRATION_MASKINGS`, or is
            given to a calibration that trains no excluding model, or with
            `training_pairs="direct"`.
    """

    grid = _validate_levels(levels)
    if _MEDIAN_LEVEL not in grid:
        raise ValueError(
            f"the declared levels {list(grid)} do not carry {_MEDIAN_LEVEL}; the "
            f"point forecast is the rearranged median and there is no honest "
            f"substitute for it -- an average of the two levels straddling the "
            f"middle is a centre no fit produced"
        )

    # The calibration's own arguments, before anything about the frame: each is
    # a statement about what the caller asked for, owed whether or not the
    # frame would have fitted.
    if calibration not in CALIBRATIONS:
        raise ValueError(
            f"unknown calibration {calibration!r}; this model can be built with "
            f"{', '.join(CALIBRATIONS)}. A misspelt calibration fitted as 'none' "
            f"would publish the in-sample band under a record that asked for "
            f"another"
        )
    if calibration_folds is not None and calibration not in _CROSS_CALIBRATIONS:
        raise ValueError(
            f"calibration_folds {calibration_folds} was given, but calibration "
            f"{calibration!r} splits the frame into no blocks; only "
            f"{', '.join(_CROSS_CALIBRATIONS)} do. A setting "
            f"that is accepted and ignored is read by the next person as a "
            f"setting that took effect"
        )
    if calibration_masking is not None:
        if calibration_masking not in CALIBRATION_MASKINGS:
            raise ValueError(
                f"unknown calibration_masking {calibration_masking!r}; this model "
                f"can be built with {', '.join(CALIBRATION_MASKINGS)}, or None for "
                f"the frame as the fold masked it"
            )
        if calibration not in _CROSS_CALIBRATIONS:
            raise ValueError(
                f"calibration_masking {calibration_masking!r} was given, but "
                f"calibration {calibration!r} trains no excluding model to mask; "
                f"only {', '.join(_CROSS_CALIBRATIONS)} do. A setting that is "
                f"accepted and ignored is read by the next person as a setting "
                f"that took effect"
            )
        if training_pairs == "direct":
            raise ValueError(
                f"calibration_masking {calibration_masking!r} was given with "
                f"training_pairs 'direct', whose every pair reads only what was "
                f"public at its own target's decision, before any held-out row's "
                f"after it: there is nothing to mask. A setting that is accepted "
                f"and ignored is read by the next person as a setting that took "
                f"effect"
            )
    folds: Optional[int] = None
    if calibration == "none":
        if calibration_share is not None:
            raise ValueError(
                f"calibration_share {calibration_share} was given, but "
                f"calibration 'none' holds no rows out. A setting that is "
                f"accepted and ignored is read by the next person as a setting "
                f"that took effect"
            )
        share: Optional[float] = None
    elif calibration in _CROSS_CALIBRATIONS:
        if calibration_share is not None:
            raise ValueError(
                f"calibration_share {calibration_share} was given, but "
                f"calibration {calibration!r} holds out every row in turn, "
                f"not a share of them; its setting is calibration_folds. A "
                f"setting that is accepted and ignored is read by the next "
                f"person as a setting that took effect"
            )
        share = None
        folds = (
            DEFAULT_CALIBRATION_FOLDS if calibration_folds is None else calibration_folds
        )
        if isinstance(folds, bool) or not isinstance(folds, int) or folds < 2:
            raise ValueError(
                f"calibration_folds must be an int of at least 2, got {folds!r}; "
                f"one block holds out the whole frame and leaves its excluding "
                f"model nothing to fit on"
            )
        _require_information(information, calibration)
    else:
        share = (
            DEFAULT_CALIBRATION_SHARE
            if calibration_share is None
            else calibration_share
        )
        if (
            isinstance(share, bool)
            or not isinstance(share, (int, float))
            or not 0.0 < share < 1.0
        ):
            raise ValueError(
                f"calibration_share must be a number strictly inside (0, 1), "
                f"got {share!r}; a share of 0 holds nothing out to calibrate "
                f"on, and a share of 1 leaves nothing to fit"
            )
        share = float(share)
        _require_information(information, calibration)

    if spread_change_lags is not None and (
        isinstance(spread_change_lags, bool)
        or not isinstance(spread_change_lags, int)
        or spread_change_lags < 1
    ):
        raise ValueError(
            f"spread_change_lags must be an int of at least 1, got "
            f"{spread_change_lags!r}; lag 0 would be the change into the day "
            f"being forecast, which is the target minus the autoregressive term, "
            f"and a model with no lags is spelled by leaving the setting out"
        )
    lags = spread_change_lags or 0

    if volatility_feature is not None and volatility_feature not in VOLATILITY_FEATURES:
        raise ValueError(
            f"unknown volatility_feature {volatility_feature!r}; this model can "
            f"be built with {', '.join(VOLATILITY_FEATURES)}, or with none by "
            f"leaving the setting out. A misspelt feature fitted without one "
            f"would publish today's gbm under a declaration naming a volatility "
            f"model"
        )

    if arx_feature is not None and arx_feature not in ARX_FEATURES:
        raise ValueError(
            f"unknown arx_feature {arx_feature!r}; this model can be built with "
            f"{', '.join(ARX_FEATURES)} -- the ARX fitted on this model's own "
            f"declared regressors -- or with none by leaving the setting out. A "
            f"misspelt feature fitted without one would publish today's gbm "
            f"under a declaration naming an ARX"
        )

    if tail is not None and tail not in TAIL_FAMILIES:
        raise ValueError(
            f"unknown tail {tail!r}; this model's law can be continued with "
            f"{', '.join(TAIL_FAMILIES)}, or ended at its knots by leaving the "
            f"setting out. A misspelt tail fitted without one would publish "
            f"today's saturating law under a declaration naming a tail"
        )
    if tail is not None and calibration == "none":
        raise ValueError(
            f"tail {tail!r} needs held-out calibration rows, and calibration "
            f"'none' holds none out: its only sample is the rows the estimators "
            f"were fitted on, and an in-sample tail is the leakage this "
            f"repository refuses. Use calibration 'conformal'"
        )
    if tail is not None and calibration == "cross_conformal":
        raise ValueError(
            f"tail {tail!r} is not wired for calibration 'cross_conformal': "
            f"every row is held out by some block there, and the coherent "
            f"sample is a different construction. A tail from in-sample or "
            f"mixed-provenance excesses in the meantime would be worse than "
            f"this refusal. Use calibration 'conformal'"
        )
    if tail is not None and calibration == "conformal_asymmetric":
        raise ValueError(
            f"tail {tail!r} is not wired for calibration 'conformal_asymmetric': "
            f"the tail is attached at the top quantile moved by one widening, and "
            f"this calibration moves the two edges by two. A tail attached at "
            f"the wrong knot would put a jump in the curve at the join. Use "
            f"calibration 'conformal'"
        )
    if tail is not None and calibration == "cross_conformal_asymmetric":
        raise ValueError(
            f"tail {tail!r} is not wired for calibration "
            f"'cross_conformal_asymmetric': the knot would be a per-side CV+ "
            f"edge over every excluding model, which has cross_conformal's "
            f"missing sample and conformal_asymmetric's second widening both. "
            f"Use calibration 'conformal'"
        )
    if tail is not None and calibration == _SCALED_CALIBRATION:
        raise ValueError(
            f"tail {tail!r} is not wired for calibration "
            f"{_SCALED_CALIBRATION!r}: the knot would be a CV+ edge over every "
            f"excluding model, cross_conformal's missing sample, and scaled per "
            f"row besides. Use calibration 'conformal'"
        )
    if tail is not None and calibration == _PARTIAL_CALIBRATION:
        raise ValueError(
            f"tail {tail!r} is not wired for calibration "
            f"{_PARTIAL_CALIBRATION!r}: the knot would be a CV+ edge over every "
            f"excluding model, cross_conformal's missing sample, and its "
            f"correction scaled per row besides. Use calibration 'conformal'"
        )
    if training_pairs is not None and training_pairs not in TRAINING_PAIRS:
        raise ValueError(
            f"unknown training_pairs {training_pairs!r}; this model can be "
            f"trained on {', '.join(TRAINING_PAIRS)} pairs, or on one-step "
            f"pairs by leaving the setting out. A misspelt pairing fitted on "
            f"one-step pairs would publish today's gbm under a declaration "
            f"naming another"
        )
    direct = training_pairs == "direct"
    if direct and not isinstance(information, InformationRule):
        raise SplitError(
            f"training_pairs 'direct' pairs each target with its as-of read and "
            f"needs the run's as-of rule to read it (information=), got "
            f"{information!r}"
        )
    scaled = calibration == _SCALED_CALIBRATION
    partial = calibration == _PARTIAL_CALIBRATION
    trailing = calibration in _TRAILING_SCALE_CALIBRATIONS

    names = tuple(str(name) for name in regressors)
    if not names:
        raise ValueError(
            "no regressors declared; an empty list is how a caller omits the "
            "decision rather than makes it. Name the regressors, even if the "
            "honest answer is one of them"
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(
            f"regressors declared more than once: {duplicates}; a column handed "
            f"to the ensemble twice splits on itself and its importance is "
            f"meaningless individually"
        )

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"gbm needs at least {minimum_history} training rows, got {len(rows)}; "
            f"a boosted quantile fit from fewer is not a fitted model"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff {declared}; "
            f"a fitted model may not contain a row it was not allowed to see"
        )

    # The calibration split, by date. The calibration rows are the most recent
    # share of the frame; the fit rows are the earlier rows that clear the purge
    # before the first of them, by the splitter's own comparison. Under `none`
    # the fit rows are the frame.
    fit_rows = rows
    calibration_rows: List[DailyObservation] = []
    if share is not None:
        count = int(Fraction(repr(share)) * len(rows))
        needed = (
            _minimum_asymmetric_calibration_rows(grid)
            if calibration == "conformal_asymmetric"
            else _minimum_calibration_rows(grid)
        )
        if count < needed:
            raise ValueError(
                f"{calibration} calibration needs at least {needed} calibration "
                f"rows, got {count} ({share} of {len(rows)} training rows); "
                f"below {needed} the conformal quantile of a "
                f"{float(_band_probability(grid))} band is infinite, and a "
                f"finite widening there would claim a coverage the "
                f"calibration cannot support"
            )
        first = len(rows) - count
        opens = dates[first]
        calibration_rows = rows[first:]
        # The fit rows are the labels observable at the first calibration
        # row's decision instant: the frame's prefix through its anchor.
        fit_rows = rows[: information.anchor(dates, first) + 1]
        if len(fit_rows) < 2:
            raise ValueError(
                f"label observability before the calibration rows opening "
                f"{opens} leaves {len(fit_rows)} fit row(s) of {len(rows)}; the "
                f"design needs at least one origin and its successor"
            )

    # Every row's spread, `None` at a hole, for the lags, the variance and the
    # trailing scale of the two scaled calibrations alone. Over the whole frame, which is the only
    # history any of them is ever read from; the fit rows are its prefix, so a
    # position in one is the same position in the other.
    spreads = (
        [_observed_spread(row, "training row") for row in rows]
        if lags or volatility_feature is not None or trailing
        else []
    )

    # The origins: every fit row that has a successor among the fit rows, less
    # the first `lags`, whose changes would reach before the frame. The GARCH is
    # fitted on the fit rows' spreads and filtered over the whole frame, so the
    # calibration rows are run through the recursion, never fitted on.
    # The ARX is fitted on the fit rows as one frame, which is what
    # `--model arx` fits on the same rows.
    # Direct pairs: every fit row as a target, read as a forecast of it is.
    # Every read is before its target, so inside the fit rows.
    fit_pairs = (
        _direct_pairs(information, rows, dates, range(len(fit_rows)), lags)[0]
        if direct
        else None
    )
    if direct and not fit_pairs:
        raise ValueError(
            f"training_pairs 'direct' leaves no training pair in the "
            f"{len(fit_rows)} fit rows: no target has an as-of read with "
            f"{lags} rows before its anchor"
        )
    imputations, garch, initial, design, targets, variances, arx = _training_design(
        rows,
        dates,
        spreads,
        spreads[: len(fit_rows)],
        range(lags, len(fit_rows) - 1),
        names,
        lags,
        volatility_feature,
        "fit rows",
        arx_feature,
        fit_rows,
        pairs=fit_pairs,
    )

    # The cross-conformal blocks, planned and designed before anything is
    # fitted: every refusal about them is a statement about the frame. Blocks
    # are contiguous runs of the frame's rows in date order, never shuffled.
    plans = []
    if folds is not None:
        bounds = [len(rows) * number // folds for number in range(folds + 1)]
        for number in range(folds):
            start, stop = bounds[number], bounds[number + 1]
            kept: List[bool] = []
            origins: List[int] = []
            if start < stop:
                # A row before the block trains only if its label was
                # observable at the block's first decision instant; a row
                # after it only if, at its own decision instant, the block's
                # last label was already observable -- the as-of rule's label
                # observability, in both directions.
                before = information.anchor(dates, start) if start > 0 else -1
                kept = [
                    position <= before
                    if position < start
                    else position >= stop
                    and information.anchor(dates, position) >= stop - 1
                    for position in range(len(dates))
                ]
                # A pair trains only if its origin and its target both do.
                origins = [
                    position
                    for position in range(lags, len(rows) - 1)
                    if kept[position] and kept[position + 1]
                ]
            block_pairs = None
            training_positions = sorted(
                {p for origin in origins for p in (origin, origin + 1)}
            )
            if direct and start < stop:
                # Direct: a pair trains only if its target and every row its
                # read touches do.
                block_pairs, training_positions = _direct_pairs(
                    information, rows, dates, range(len(rows)), lags, kept
                )
                origins = [anchor for anchor, _, _ in block_pairs]
            if not origins:
                raise ValueError(
                    f"cross-conformal block {number + 1} of {folds} holds out "
                    f"{stop - start} of {len(rows)} rows and leaves its excluding "
                    f"model {len(origins)} training pair(s) after label "
                    f"observability on both sides; a gbm fit needs its "
                    f"block to hold out at least one row, and at least one "
                    f"origin with its successor to fit on"
                )
            # The rows this model may not train on are holes to it, so no lag
            # and no variance in its design reads one.
            masked = [
                spread if keep else None for spread, keep in zip(spreads, kept)
            ]
            label = f"training rows of cross-conformal block {number + 1} of {folds}"
            # Its ARX trains on every one-step pair whose two rows it may train
            # on, from the frame's first row -- the full fit's ARX reads every
            # pair of its rows, not only those past the lags -- and never on a
            # pair that spans the block.
            arx_origins = [
                position
                for position in range(len(rows) - 1)
                if kept[position] and kept[position + 1]
            ]
            reads = []
            for index in range(start, stop):
                # No row of the frame is observable at this row's decision, or
                # a declared field has none yet, or its feature row has too few
                # rows before it for its lags: there is no forecast of it to
                # score.
                read = _held_out_read(information, rows, dates, index)
                if read is None:
                    continue
                position, feature = read
                if position < lags:
                    continue
                # The scale ends at the feature row, the held-out row's own
                # anchor: its decision-time spreads, and none after them. No
                # scale, no score.
                scale = _trailing_scale(spreads, position) if trailing else None
                if trailing and scale is None:
                    continue
                reads.append((index, position, feature, scale))
            # One excluding model per mask: under `calibration_masking` each
            # held-out row is scored by a model whose training rows before the
            # block carry only what was public at its own decision; otherwise,
            # and for the rows whose mask is empty, the block's one model.
            groups: dict = {}
            for entry in reads:
                mask = (
                    _held_out_mask(information, rows, dates, before, entry[0])
                    if calibration_masking is not None
                    else ()
                )
                groups.setdefault(mask, []).append(entry)
            if not groups:
                groups[()] = []
            for mask, entries in groups.items():
                training = _masked_rows(rows, mask)
                (
                    block_imputations,
                    block_garch,
                    block_initial,
                    block_design,
                    block_targets,
                    _,
                    block_arx,
                ) = _training_design(
                    training,
                    dates,
                    masked,
                    masked,
                    origins,
                    names,
                    lags,
                    volatility_feature,
                    label,
                    arx_feature,
                    training,
                    arx_origins,
                    pairs=block_pairs,
                )
                # Its scored rows' inputs are every row at or before their
                # feature row, as a forecast's are; only what the model learned
                # is its own.
                filtered = (
                    _garch_variances(
                        _squared_changes(spreads), block_garch, block_initial
                    )
                    if volatility_feature is not None
                    else []
                )
                held_out = [
                    (
                        _design(
                            feature,
                            names,
                            block_imputations,
                            "held-out feature row",
                            _spread_changes(
                                spreads,
                                position,
                                lags,
                                f"held-out feature row for {dates[position]}",
                            ),
                            filtered[position] if filtered else None,
                            block_arx,
                        ),
                        float(rows[index].spread_bps),
                        dates[index],
                        scale,
                    )
                    for index, position, feature, scale in entries
                ]
                plans.append(
                    (
                        start,
                        stop,
                        training_positions,
                        block_imputations,
                        block_garch,
                        block_initial,
                        block_arx,
                        block_design,
                        block_targets,
                        held_out,
                    )
                )
        count = sum(len(plan[-1]) for plan in plans)
        needed = (
            _minimum_asymmetric_calibration_rows(grid)
            if calibration == "cross_conformal_asymmetric"
            else _minimum_calibration_rows(grid)
        )
        if count < needed:
            raise ValueError(
                f"{calibration} calibration needs at least {needed} held-out "
                f"scores, got {count} over {folds} blocks of {len(rows)} training "
                f"rows; below {needed} CV+'s ranks for a "
                f"{float(_band_probability(grid))} band name no score, and a band "
                f"read off an index that wrapped would claim a coverage the "
                f"calibration cannot support"
            )

    # Imported here rather than at the top of the function: every refusal
    # above is a statement about the arguments and is owed to a caller whether
    # or not the extra is installed.
    estimator_class = _estimator_class()
    # Read in the same breath as the class the fits are made with, so the
    # versions a record publishes are those of the modules that did the fitting.
    versions = _library_versions()

    estimators = _fitted_levels(
        estimator_class, grid, design, targets, random_state, min_samples_leaf
    )

    # The residual sample, about this model's own rearranged median rather than
    # about the 0.50 fit: the two differ exactly on the rows where that fit
    # crossed a neighbour, and there the estimator's value is not the centre of
    # the distribution the model reports.
    centre = grid.index(_MEDIAN_LEVEL)
    residuals = [
        target - vector[centre]
        for vector, target in zip(_rearranged(estimators, design), targets)
    ]

    # The widening: every calibration row scored by the estimators fitted
    # above -- not refitted, and never on a fit row -- from the feature row the
    # backtest's own rule would choose for it, then the conformal rank.
    widening = 0.0
    edge_widenings = (0.0, 0.0)
    tail_fit: Optional[FittedTail] = None
    if calibration_rows:
        first = len(rows) - len(calibration_rows)
        scored = []
        for index in range(first, len(rows)):
            # The calibration row's own as-of read: its anchor, and each
            # declared field at its latest row observable at its decision.
            read = _held_out_read(information, rows, dates, index)
            if read is None:
                raise ValueError(
                    f"calibration row {dates[index]} has no as-of read inside "
                    f"the frame; a calibration row with no forecast has no score"
                )
            position, feature = read
            # The lags end at the feature row, never at the row being scored.
            scored.append(
                (
                    _design(
                        feature,
                        names,
                        imputations,
                        "calibration row",
                        _spread_changes(
                            spreads,
                            position,
                            lags,
                            f"calibration feature row for {dates[position]}",
                        ),
                        variances[position] if variances else None,
                        # The fit rows' ARX, never refitted on these rows.
                        arx,
                    ),
                    float(rows[index].spread_bps),
                )
            )
        vectors = _rearranged(estimators, [features for features, _ in scored])
    if calibration_rows and calibration == "conformal_asymmetric":
        # The two score sets, kept apart and reduced apart. No pooled score and
        # no single widening: that is `conformal`, below.
        edge_widenings = _asymmetric_widenings(
            [vector[0] - target for vector, (_, target) in zip(vectors, scored)],
            [target - vector[-1] for vector, (_, target) in zip(vectors, scored)],
            grid,
        )
    elif calibration_rows:
        scores = sorted(
            max(vector[0] - target, target - vector[-1])
            for vector, (_, target) in zip(vectors, scored)
        )
        rank = math.ceil(_band_probability(grid) * (len(scores) + 1))
        widening = scores[rank - 1]
        # The tail's sample: the same rows, the same vectors, each target's
        # excess above its own *calibrated* top quantile -- the knot the tail is
        # attached at -- where it has one.
        if tail is not None:
            excesses = []
            for vector, (_, target) in zip(vectors, scored):
                top = _calibrated(vector, widening)[-1]
                if target > top:
                    excesses.append(target - top)
            if excesses:
                tail_fit = _fit_gpd_pwm(excesses)

    # The excluding models: each fitted on its own design, and each held-out
    # row scored by its own block's model and no other.
    blocks = []
    for (
        start,
        stop,
        training_positions,
        block_imputations,
        block_garch,
        block_initial,
        block_arx,
        block_design,
        block_targets,
        held_out,
    ) in plans:
        block_estimators = _fitted_levels(
            estimator_class,
            grid,
            block_design,
            block_targets,
            random_state,
            min_samples_leaf,
        )
        vectors = (
            _rearranged(block_estimators, [features for features, _, _, _ in held_out])
            if held_out
            else ()
        )
        blocks.append(
            _ExcludingModel(
                estimators=block_estimators,
                imputations=block_imputations,
                garch_parameters=block_garch,
                garch_initial_variance=block_initial,
                arx=block_arx,
                held_out_start=dates[start],
                held_out_end=dates[stop - 1],
                training_dates=[dates[p] for p in training_positions],
                scored_dates=[when for _, _, when, _ in held_out],
                scores=[
                    max(vector[0] - target, target - vector[-1])
                    for vector, (_, target, _, _) in zip(vectors, held_out)
                ],
                lower_scores=[
                    vector[0] - target for vector, (_, target, _, _) in zip(vectors, held_out)
                ],
                upper_scores=[
                    target - vector[-1] for vector, (_, target, _, _) in zip(vectors, held_out)
                ],
                scales=[scale for _, _, _, scale in held_out] if trailing else (),
                scaled_residuals=[
                    abs(target - vector[centre]) / scale
                    for vector, (_, target, _, scale) in zip(vectors, held_out)
                ]
                if scaled
                else (),
                partial_scores=[
                    max(vector[0] - target, target - vector[-1]) / _partial_factor(scale)
                    for vector, (_, target, _, scale) in zip(vectors, held_out)
                ]
                if partial
                else (),
            )
        )
    held_out_dates = [when for block in blocks for when in block.scored_dates]
    if calibration_rows:
        calibration_start: Optional[date] = calibration_rows[0].date
        calibration_end: Optional[date] = calibration_rows[-1].date
    elif held_out_dates:
        calibration_start, calibration_end = held_out_dates[0], held_out_dates[-1]
    else:
        calibration_start = calibration_end = None

    return FittedGradientBoostedQuantiles(
        estimators,
        names,
        imputations,
        residuals,
        declared,
        grid,
        random_state,
        ml_libraries=versions,
        calibration=calibration,
        calibration_share=share,
        widening=widening,
        fit_end=fit_rows[-1].date,
        calibration_start=calibration_start,
        calibration_end=calibration_end,
        spread_change_lags=spread_change_lags,
        history=tuple(zip(dates, spreads)),
        volatility_feature=volatility_feature,
        garch_parameters=garch,
        garch_initial_variance=initial,
        calibration_folds=folds,
        calibration_blocks=blocks,
        arx_feature=arx_feature,
        arx=arx,
        tail=tail,
        tail_fit=tail_fit,
        edge_widenings=edge_widenings,
        calibration_masking=calibration_masking,
        training_pairs=training_pairs,
    )


#: Pressure model v2's trees (#244): v1's, with a maximum depth of 3. #247's candidate (iv) applied the setting by
#: replacing the estimator class inside its own script; it is declared here, in the module that fits, and applied by
#: `fit_depth_limited_quantiles`. The inner block chose it (`scripts/pressure_model_v2.py`, `V2_TREE_SETTINGS`).
V2_TREE_SETTINGS = MappingProxyType({"max_depth": 3})


def fit_depth_limited_quantiles(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    *,
    max_depth: int,
    information: Optional[InformationRule] = None,
    **settings: Any,
) -> FittedGradientBoostedQuantiles:
    """`fit_gradient_boosted_quantiles`, with every tree limited to `max_depth` levels.

    The published fitter itself, run with the estimator it builds limited in depth for the length of one fit: the
    full fit's estimators and every excluding model's carry the setting. Everything else is
    `fit_gradient_boosted_quantiles`' own: its arguments, its guards and its refusals. **The published fitter's
    source is not touched** (the final test's CRPS declaration hashes it, and the definitions it reads), so a fit
    made without this function builds exactly the estimators every published gbm record was produced with, and the
    estimator class is put back when this fit ends, however it ends.

    Args:
        max_depth: an int of at least 1, **required**: a depth is a choice, and a default would be a silent one.
        information: handed to `fit_gradient_boosted_quantiles` (named here so a fold loop sees that this fitter
            reads the as-of rule, as it does for the published fitter).

    Raises:
        ValueError: if `max_depth` is not an int of at least 1; `MissingMLExtraError` without the `ml` extra; and
            whatever `fit_gradient_boosted_quantiles` raises.
    """

    if isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 1:
        raise ValueError(f"max_depth must be an int of at least 1, got {max_depth!r}")
    published = _estimator_class()

    def limited(**kwargs: Any) -> Any:
        return published(**kwargs, max_depth=max_depth)

    module = globals()
    original = module["_estimator_class"]
    module["_estimator_class"] = lambda: limited
    try:
        return fit_gradient_boosted_quantiles(
            train_frame, regressors, cutoff, minimum_history, information=information, **settings
        )
    finally:
        module["_estimator_class"] = original


def gbm_exceedance(
    regressors: Sequence[str],
    minimum_history: int = 20,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples_leaf: int = 20,
    calibration: str = "none",
    calibration_share: Optional[float] = None,
    calibration_folds: Optional[int] = None,
    tail: Optional[str] = None,
    spread_change_lags: Optional[int] = None,
    volatility_feature: Optional[str] = None,
    arx_feature: Optional[str] = None,
    calibration_masking: Optional[str] = None,
    training_pairs: Optional[str] = None,
) -> ExceedancePredictor:
    """Conditional exceedance from the gradient-boosted quantiles' own law.

    The fourth implementer of `ExceedancePredictor`, and the first whose
    predictive *width* moves with the feature row. `arx_exceedance`'s curve
    moves because the centre moves and the residual law is carried along
    unchanged; `threshold_exceedance` adds a second reason by switching which
    fitted relationship produces that centre. This one's band is fitted at each
    level separately, so two rows with the same centre can still get different
    curves --- which is what a conditional quantile model is for, and what
    nothing in `event_eval` had scored before.

    `fit_gradient_boosted_quantiles` is fitted on the training rows the
    evaluator hands over --- everything that cleared the purge gap ahead of the
    window and nothing from inside it --- and the fitted model is then read once
    per feature row.

    **Derived, not re-derived.** The construction is
    `FittedGradientBoostedQuantiles.predict_stress`, which is the inverse of the
    vector `predict` reports. Reading the fits a second time here would be a
    second opinion about one distribution.

    `features_read` comes off the fitted model, so it is `spread_bps` plus the
    declared regressors --- the autoregressive term included, which is the half
    a predictor reporting only what it was handed would leave out.

    Args:
        regressors: the ordered exogenous regressor names, as
            `fit_gradient_boosted_quantiles` takes them. Required, with no
            default.
        minimum_history: the shortest training frame that may produce a fitted
            model. Passed through, and refused below.
        random_state: the seed every fit uses.
        min_samples_leaf: passed through to the estimator.
        training_pairs: passed straight to `fit_gradient_boosted_quantiles` by the same rule, defaulting to its own
            `None` (#453): `"direct"` trains each target on the feature row it is served at prediction.
        calibration, calibration_share, calibration_folds, tail: the settings
            that change the law the curve is read off, passed straight to
            `fit_gradient_boosted_quantiles` and neither checked nor re-derived
            here; that function refuses each inconsistency (B39). The defaults
            are its own, so a predictor built with none of them fits exactly
            what this one fitted before it took any.
        spread_change_lags, volatility_feature, arx_feature: the feature
            settings that change the design the law is fitted on, by the same
            rule: passed straight to `fit_gradient_boosted_quantiles`, neither
            checked nor re-derived here, defaulting to its own (B42).
        calibration_masking: passed straight to
            `fit_gradient_boosted_quantiles` by the same rule, defaulting to
            its own `None` (#78).

    **The as-of rule reaches the fit from the fold loop.** `fit_predict` names
    `information`, so `rolling_exceedance_backtest` and
    `event_eval.evaluate_event_window` hand over the run's rule, as
    `baseline._fit_at_origin` does for `backtest`; a calibration needs it and
    `none` reads nothing. A caller that passes none gets the fitter's refusal
    under a calibration.

    **Before B39 the tail could not be measured.** `backtest` and `compare`
    score the quantile vector, which a tail by design never moves, and this
    was the one predictor whose curve a tail does move -- and it took no tail.

    **Before B42 no feature setting could be scored on the curve.** Every
    feature this model can be built with had been scored on the quantile vector
    by `backtest` and `compare`, and none on the exceedance curve, because this
    predictor took none of them.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`
        and for `rolling_exceedance_backtest`. The curves carry the fit's
        `model_settings`, so a record names the calibration, tail and feature
        settings it was read off.

    Raises:
        MissingMLExtraError, ValueError, MissingRegressorError, LookAheadError:
            at call time, whatever the fitter raises on the frame it is given.
            Not caught and re-wrapped: a refusal to fit is the fitter's
            statement about the frame.
    """

    declared = tuple(str(name) for name in regressors)

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
        uncalibrated: bool = False,
    ) -> ExceedanceCurves:
        model = fit_gradient_boosted_quantiles(
            train_rows,
            declared,
            minimum_history=minimum_history,
            random_state=random_state,
            min_samples_leaf=min_samples_leaf,
            calibration=calibration,
            calibration_share=calibration_share,
            calibration_folds=calibration_folds,
            information=information,
            tail=tail,
            spread_change_lags=spread_change_lags,
            volatility_feature=volatility_feature,
            arx_feature=arx_feature,
            calibration_masking=calibration_masking,
            training_pairs=training_pairs,
        )
        # One model per feature row: the fit, reading history by position
        # from that row's own as-of history where the evaluator handed one.
        if histories is None:
            views = [model] * len(feature_rows)
        else:
            if len(histories) != len(feature_rows):
                raise ValueError(
                    f"{len(histories)} histories for {len(feature_rows)} feature "
                    f"rows; each feature row reads its own"
                )
            views = [model.with_history(history) for history in histories]
        return ExceedanceCurves(
            tuple(
                view.predict_stress(row, taus)
                for view, row in zip(views, feature_rows)
            ),
            model.features_read,
            # Off the model that produced the curves, not read again here: the
            # versions a record names are the fit's.
            ml_libraries=model.ml_libraries,
            # Empty under the defaults, so a default record is unchanged.
            model_settings=model.model_settings,
            # This fit's tail, off this model, for this fold's entry (B40);
            # `None` without a tail, so a record without one is unchanged.
            tail_account=model.tail_account,
            # Where each curve's positional reads ended, for the evaluator's
            # staleness check (`baseline._check_history_end`).
            history_ends=tuple(view.history_end for view in views),
            # What an online calibration moves (#124), when the fold loop asks
            # (`uncalibrated`), from an uncalibrated fit without a tail only: the vector each view reports, and the
            # residual range its law's tails are laid from.
            uncalibrated=(
                tuple(
                    (view.predict(row), model.residuals[0], model.residuals[-1])
                    for view, row in zip(views, feature_rows)
                )
                if uncalibrated and calibration == "none" and tail is None
                else None
            ),
        )

    return fit_predict


# --------------------------------------------------------------------------
# Direct pressure-probability models (#114)
# --------------------------------------------------------------------------
#
# `docs/decisions/pressure-probability.md` lets the pressure probability come
# from a model fitted to the exceedance label directly, beside the exceedance
# read off a predictive distribution. These are the two direct candidates of
# pressure model v1 (plan §1): a logistic and a gradient-boosted classifier,
# fitted per threshold to the label `spread > tau` and served under the as-of
# rule. Both read one design, built by `_PressureDesign` from the declared
# features, so the two differ only in the estimator.


#: The settings the two direct models are fitted with, declared once and named
#: in every curve's `model_settings`. Not tuned: chosen before scoring, as the
#: scikit-learn defaults where they exist, and stated so a record can say so.
PRESSURE_LOGISTIC_SETTINGS = MappingProxyType(
    {"C": 1.0, "penalty": "l2", "standardized": True, "max_iter": 5000}
)
#: The literature-scan predictors (#372; `docs/pivot/literature.md`, Copeland-Duffie-Yang
#: SR 974): a ridge probit of the label, and a linear quantile regression of the spread read
#: as a conditional law. Chosen before scoring, not tuned.
PRESSURE_PROBIT_SETTINGS = MappingProxyType(
    {"link": "probit", "ridge": 1.0, "standardized": True, "iterations": 50}
)
PRESSURE_QUANTILE_SETTINGS = MappingProxyType(
    {
        "estimator": "QuantileRegressor",
        "solver": "highs",
        "alpha": 0.0,
        "standardized": True,
        "quantile_grid": (0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99),
        "reading": "P(spread > tau) = 1 - F(floor(tau) + 0.5), F linear between the grid's quantiles "
        "and continued at the outer segments' slopes to 0 and 1",
    }
)
#: The two-part pressure model (#382, track S of #374): P(spike) from a classifier, times a
#: conditional law of the spike's size. Chosen before scoring, not tuned. The size is the
#: spread's whole-bp excess over the spike threshold, geometric on 1, 2, ... with a
#: log-linear mean on the same design (a ridge Poisson fit of excess - 1, so the mean is
#: consistent without a distributional assumption), pooled to one mean when the training
#: frame has fewer than `min_spike_days` spikes.
TWO_PART_SETTINGS = MappingProxyType(
    {
        "spike_bp": 5.0,
        "size_law": "geometric excess over the spike threshold",
        "size_mean": "1 + PoissonRegressor(alpha, log link) on the standardized design, fitted on spike days",
        "alpha": 1.0,
        "max_iter": 1000,
        "min_spike_days": 20,
        "reading": "P(spread > tau) = P(spike) * (1 - 1/mean)^(tau - spike_bp) for tau >= spike_bp",
    }
)
#: The quantile regression of the settlement-timing track (#379; Adrian, Boyarchenko &
#: Giannone 2019): the quantile grid of `PRESSURE_QUANTILE_SETTINGS`, smoothed into a
#: skew-t by least squares on the predicted quantiles, in place of linear interpolation.
#: Chosen before scoring, not tuned.
PRESSURE_QUANTILE_SKEWT_SETTINGS = MappingProxyType(
    {
        "estimator": "QuantileRegressor",
        "solver": "highs",
        "alpha": 0.0,
        "standardized": True,
        "quantile_grid": PRESSURE_QUANTILE_SETTINGS["quantile_grid"],
        "smoother": "Azzalini-Capitanio skew-t (location, scale, shape, degrees of freedom), "
        "fitted to the day's sorted predicted quantiles by least squares on the quantile "
        "function (Nelder-Mead, fixed start); the CDF is the density's trapezoid integral "
        "on a fixed grid",
        "start": {"shape": 0.0, "degrees_of_freedom": 8.0},
        "reading": "P(spread > tau) = 1 - F(floor(tau) + 0.5)",
    }
)
PRESSURE_CLASSIFIER_SETTINGS = MappingProxyType(
    {
        "estimator": "HistGradientBoostingClassifier",
        "learning_rate": 0.05,
        "max_iter": 200,
        "max_leaf_nodes": 15,
        "min_samples_leaf": 20,
        "random_state": DEFAULT_RANDOM_STATE,
    }
)

#: Rare-event training (#381; `docs/pivot/literature.md`): fit the pressure label so the model
#: learns from the spikes rather than the calm majority. Declared before any score, not tuned.
#: `class_weight` weights each class by n / (2 n_class) in the fit. `focal` is a gradient-boosted
#: classifier on the focal loss (Lin et al. 2017) of `gamma` and positive-class weight `alpha`,
#: built from scikit-learn regression trees with Newton leaf values (`l2` on the hessian sum).
#: `balanced_bootstrap` fits `bags` models, each on a bootstrap of the *training rows only*
#: with half its draws from the events and half from the calm days, and averages them.
#: Reweighting distorts probabilities, so every candidate is also read recalibrated out of fold
#: (`pressure.recalibrated`), which is the form the judge scores.
PRESSURE_RARE_EVENT_SETTINGS = MappingProxyType(
    {
        "treatments": ("class_weight", "focal", "balanced_bootstrap"),
        "class_weight": "balanced",
        "focal": MappingProxyType(
            {
                "gamma": 2.0,
                "alpha": 0.75,
                "rounds": 200,
                "learning_rate": 0.05,
                "max_leaf_nodes": 15,
                "min_samples_leaf": 20,
                "l2": 0.1,
                "hessian_floor": 1e-6,
                "hessian_step": 1e-4,
            }
        ),
        "balanced_bootstrap": MappingProxyType(
            {"bags": MappingProxyType({"logistic": 10, "gbm_classifier": 5}), "event_share": 0.5}
        ),
    }
)

#: Recency-weighted and windowed training of the class-weighted logistic (#411). Declared, not
#: tuned. A pair's age is the number of panel rows between its label and the fit's last training
#: row. `decay` weights a pair by 0.5 ** (age / half_life) and balances the classes on the
#: weighted totals; `window` keeps only the pairs younger than the window, and falls back to
#: the whole history when the window holds fewer than `minimum_window_events` events at the
#: threshold (a calm stretch has none, and a fit without events has nothing to learn).
PRESSURE_RECENCY_SETTINGS = MappingProxyType(
    {
        "modes": ("decay", "window"),
        "half_lives": (63, 126, 252),
        "windows": (252, 504),
        "minimum_window_events": 10,
    }
)

#: What the two full-distribution models (#385) are built with, declared in
#: `metadata/pressure_track_q.json` before any score; a test pins the two together.
#: Both pick one hyperparameter on the pressure-day labels (`PRESSURE_DISTRIBUTION_SELECTION`).
PRESSURE_QRF_SETTINGS = MappingProxyType(
    {
        "estimator": "RandomForestRegressor",
        "reading": "Meinshausen quantile regression forest: the weight of training pair i at a served "
        "row is the mean over trees of 1/|leaf| where i shares the served row's leaf; "
        "P(spread > tau) = sum of weights of the pairs whose spread is above tau on whole basis points",
        "n_estimators": 200,
        "max_features": 0.5,
        "bootstrap": False,
        "min_samples_leaf_grid": (5, 10, 20, 40),
        "default_min_samples_leaf": 20,
        "random_state": DEFAULT_RANDOM_STATE,
    }
)
PRESSURE_NATURAL_GRADIENT_SETTINGS = MappingProxyType(
    {
        "estimator": "natural-gradient boosting of a two-parameter law, numpy and scikit-learn trees",
        "families": ("normal", "laplace"),
        "reading": "P(spread > tau) = 1 - F(floor(tau) + 0.5) under the boosted location and log-scale, "
        "and 0 for a tau more than support_above_training_max_bp above the largest training spread",
        "learning_rate": 0.05,
        "max_depth": 3,
        "min_samples_leaf": 20,
        "stage_grid": (25, 50, 100, 200, 400),
        "default_stages": 100,
        "scale_floor_bp": 0.25,
        "scale_ceiling_bp": 100.0,
        "support_above_training_max_bp": 100.0,
        "random_state": DEFAULT_RANDOM_STATE,
    }
)
#: How the one hyperparameter of each distribution model is chosen: on the
#: last `share` of the training pairs (after an embargo of one horizon), by the
#: Brier score of the pressure label at each of `taus`, never on the spread's own loss.
PRESSURE_DISTRIBUTION_SELECTION = MappingProxyType(
    {
        "share": 0.25,
        "taus": (5.0, 10.0),
        "criterion": "mean Brier score of the pressure label over taus",
        "minimum_fit_pairs": 40,
        "minimum_validation_pairs": 10,
    }
)

#: The panel days over which the TGA change is measured: one week of panel
#: rows, the H.4.1 print's cadence.
TGA_CHANGE_ROWS = 5

#: The scarcity state the scheduled-pressure terms are interacted with:
#: reserve balances in USD trillions, read as-of. Provisional until the
#: declared scarcity state (#115) exists; a record names it.
SCARCITY_STATE = "reserve_balances_usd_tn"

_CALENDAR_INPUTS = ("days_to_month_end", "quarter_end", "tax_date")
_PRESSURE_DAY_TYPES = ("quarter_end", "month_end", "tax_date")
#: The day types the settlement x state interaction variant crosses with (#378).
_INTERACTION_DAY_TYPES = ("quarter_end", "tax_date")
#: The FR 2004 net Treasury position, the balance-sheet design's dealer input (#427).
_DEALER_POSITION = "dealer_treasury_position"


def _balance_sheet_rules():
    from . import balance_sheet_days

    return balance_sheet_days.RULES
#: The regime-pooled variant's shrinkage (#378): a regime's deviation columns are
#: scaled by this before the one L2 penalty, so its deviations carry
#: `1 / scale ** 2` times the pooled columns' penalty. Declared, not tuned.
REGIME_POOLING_SCALE = 0.5
#: The hierarchical logistic's candidate deviation scales (#386): the regime
#: deviations' prior standard deviation, as a multiple of the pooled columns'.
#: Each fit takes the one whose Laplace-approximated evidence is greatest
#: (empirical Bayes). The grid is declared, not tuned; the smallest value is
#: almost complete pooling, the largest an almost unshrunk regime-by-regime fit.
REGIME_SHRINKAGE_GRID = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0)
#: The scheduled settlement columns the design reads as scheduled-pressure
#: terms: the total (#114) and the coupon part alone (#137).
_SETTLEMENT_INPUTS = ("treasury_settlement", "treasury_settlement_coupons")


class _PressureDesign:
    """The direct models' design, from the declared features.

    * `spread_bps`, required: the latest spread public at the decision.
    * Each other observed declared column, linearly, as read as-of. With
      `reserve_balances` declared it is the scarcity state, in USD trillions.
    * The three calendar columns, all declared or none: the scored day's
      pressure-day type, as the split declaration defines it, one indicator
      per type other than `ordinary`.
    * `treasury_settlement`, and `treasury_settlement_coupons` (#137), each a
      scheduled input, linearly, in USD billions.
    * With `reserve_balances` declared, each scheduled-pressure term (the type
      indicators and the settlements) times the scarcity state.
    * With `tga` and `reserve_balances` declared, the TGA's change over
      `TGA_CHANGE_ROWS` panel rows ending at its as-of read, and that change
      times the scarcity state.
    * Each declared product (#127), last: the product of two terms, each a
      declared column other than a calendar one, or `tga_change`, as read, in
      their own units. Empty by default, so pressure model v1's design is
      unchanged.
    """

    def __init__(
        self,
        features: Sequence[str],
        declaration: Any,
        products: Sequence[Tuple[str, str]] = (),
    ) -> None:
        declared = tuple(dict.fromkeys(str(name) for name in features))
        if "spread_bps" not in declared:
            raise ValueError(
                "a direct pressure model reads the latest public spread; declare "
                "spread_bps"
            )
        calendar = [name for name in _CALENDAR_INPUTS if name in declared]
        if calendar and len(calendar) != len(_CALENDAR_INPUTS):
            raise ValueError(
                f"the pressure-day type is read from {list(_CALENDAR_INPUTS)} "
                f"together; {calendar} were declared"
            )
        self.calendar = bool(calendar)
        if self.calendar and not hasattr(declaration, "day_type"):
            raise ValueError(
                "the pressure-day type needs the split declaration that defines it"
            )
        self.declaration = declaration
        self.features = declared
        self.scarcity = "reserve_balances" in declared
        self.tga = "tga" in declared and self.scarcity
        self.settlements = tuple(name for name in declared if name in _SETTLEMENT_INPUTS)
        self.linear = tuple(
            name
            for name in declared
            if name not in _CALENDAR_INPUTS
            and name not in ("spread_bps", "tga")
            and name not in _SETTLEMENT_INPUTS
            and name not in SPREAD_COMPONENTS
        )
        if "tga" in declared and not self.scarcity:
            # Read only through the change × reserves term.
            raise ValueError(
                "tga enters the direct pressure models only as its change times "
                "reserves; declare reserve_balances with it"
            )
        names: List[str] = ["spread_bps"]
        names += list(self.linear)
        scheduled: List[str] = []
        if self.calendar:
            scheduled += list(_PRESSURE_DAY_TYPES)
        scheduled += list(self.settlements)
        names += scheduled
        if self.scarcity:
            names += [f"{name}_x_scarcity" for name in scheduled]
        if self.tga:
            names += ["tga_change", "tga_change_x_scarcity"]
        self.products = tuple((str(a), str(b)) for a, b in products)
        for pair in self.products:
            for term in pair:
                known = (term == "tga_change" and self.tga) or (
                    term in declared and term not in _CALENDAR_INPUTS
                )
                if not known:
                    raise ValueError(
                        f"a product term reads {term!r}, which this design does not "
                        f"declare (a declared non-calendar column, or tga_change "
                        f"with tga and reserve_balances declared)"
                    )
            names.append(f"{pair[0]}_x_{pair[1]}")
        self.names = tuple(names)

    def needs_history(self) -> bool:
        return self.tga

    def _value(self, row: DailyObservation, column: str) -> float:
        value = row.values.get(column)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"{row.date}: the as-of read of {column!r} is missing; a direct "
                f"pressure model is not fitted on an unobserved input"
            )
        return float(value)

    def row(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        """One design row from an as-of observation and its TGA change."""

        values = [float(observation.spread_bps)]
        for name in self.linear:
            value = self._value(observation, name)
            values.append(value / 1000.0 if name == "reserve_balances" else value)
        scheduled: List[float] = []
        if self.calendar:
            kind = self.declaration.day_type(observation.values)
            scheduled += [1.0 if kind == name else 0.0 for name in _PRESSURE_DAY_TYPES]
        for name in self.settlements:
            scheduled.append(self._value(observation, name))
        values += scheduled
        if self.scarcity:
            state = self._value(observation, "reserve_balances") / 1000.0
            values += [term * state for term in scheduled]
            if self.tga:
                if tga_change is None:  # pragma: no cover - callers supply it
                    raise ValueError("the TGA change is required when tga is declared")
                values += [tga_change, tga_change * state]
        for a, b in self.products:
            values.append(self._term(observation, a, tga_change) * self._term(observation, b, tga_change))
        return values

    def _term(
        self, observation: DailyObservation, name: str, tga_change: Optional[float]
    ) -> float:
        """One product factor: `tga_change`, or a declared column as read."""

        if name == "tga_change":
            if tga_change is None:  # pragma: no cover - callers supply it
                raise ValueError("the TGA change is required for a product with it")
            return tga_change
        if name == "spread_bps":
            return float(observation.spread_bps)
        return self._value(observation, name)


def _tga_change_at(rows: Sequence[DailyObservation], position: int) -> Optional[float]:
    """The TGA's change over `TGA_CHANGE_ROWS` rows ending at row `position`.

    `None` when the earlier row is off the frame or either value is a hole.
    Every row before an as-of read is older than it, and every declared lag is
    monotone in the row, so both values were public whenever the read was.
    """

    earlier = position - TGA_CHANGE_ROWS
    if earlier < 0:
        return None
    now = rows[position].values.get("tga")
    before = rows[earlier].values.get("tga")
    if now is None or before is None:
        return None
    return float(now) - float(before)


def _served_tga_change(
    history: Sequence[DailyObservation], observation: DailyObservation
) -> float:
    """The TGA change a forecast reads, off its own as-of history.

    The history is the as-of frame at the forecast's decision instant: each
    declared column a hole where it was not yet public. Its latest row with a
    TGA value is the TGA's as-of read, and that value must be the one the
    observation carries.

    Raises:
        LookAheadError: if the history's latest public TGA is not the value the
            observation read, so the change would be measured from a row other
            than the as-of read.
        ValueError: if the history is too short to measure a change.
    """

    position = len(history) - 1
    while position >= 0 and history[position].values.get("tga") is None:
        position -= 1
    read = observation.values.get("tga")
    if position < 0 or read is None or float(history[position].values["tga"]) != float(read):
        raise LookAheadError(
            f"the forecast read tga {read!r} at {observation.date}, but its as-of "
            f"history's latest public tga is "
            f"{None if position < 0 else history[position].values['tga']!r}; the "
            f"change would be measured from a row other than the as-of read"
        )
    change = _tga_change_at(history, position)
    if change is None:
        raise ValueError(
            f"{observation.date}: fewer than {TGA_CHANGE_ROWS} rows of TGA history "
            f"before its as-of read"
        )
    return change


def _pressure_pairs(
    design: _PressureDesign,
    information: InformationRule,
    train_rows: Sequence[DailyObservation],
    cache: dict,
    positions: Optional[List[int]] = None,
) -> Tuple[List[List[float]], List[float]]:
    """Direct (horizon-matched) training pairs under the as-of rule.

    `positions`, when given, receives each pair's label row index in `train_rows`.

    Each label `t` is paired with the design row a forecast of `t` would have
    read at its own decision instant (`information.information_set`), checked
    by both guards. A label with no read, a missing input or no TGA history
    trains no pair. Cached by date: a pair reads only rows public by its own
    decision, which every later frame carries unmasked.
    """

    dates = [row.date for row in train_rows]
    xs: List[List[float]] = []
    ys: List[float] = []
    key_base = (information.horizon, information.features)
    for target in range(1, len(train_rows)):
        key = (key_base, dates[target])
        if key not in cache:
            cache[key] = None
            try:
                info = information.information_set(dates, target)
            except SplitError:
                continue
            information.check(dates, info)
            tga_change: Optional[float] = None
            if design.tga:
                (read,) = [r for r in info.reads if r.feature == "tga"]
                tga_change = _tga_change_at(train_rows, read.row)
                if tga_change is None:
                    continue
            try:
                features = design.row(information.observation(train_rows, info), tga_change)
            except ValueError:
                continue
            cache[key] = (features, float(train_rows[target].spread_bps))
        pair = cache[key]
        if pair is not None:
            xs.append(pair[0])
            ys.append(pair[1])
            if positions is not None:
                positions.append(target)
    return xs, ys


#: The pooled design's last column (#129): 1 on a pre-SOFR history pair, 0 on
#: every SOFR pair and every served row.
HISTORY_MARKET_COLUMN = "effr_market"


def _direct_pressure_predictor(
    kind: str,
    features: Sequence[str],
    declaration: Any,
    minimum_history: int,
    products: Sequence[Tuple[str, str]] = (),
    history: Optional[Tuple[Sequence[Any], Any]] = None,
    design: Optional[Any] = None,
    rare: Optional[str] = None,
    recency: Optional[Tuple[str, int]] = None,
) -> Any:
    """The fit-and-predict behind both direct models; `kind` picks the estimator.

    `recency`, for the recency study (#411): `(mode, parameter)`, a mode of
    `PRESSURE_RECENCY_SETTINGS["modes"]` with its half-life or window in panel
    rows. It applies to the class-weighted logistic only (`kind="logistic"`,
    `rare="class_weight"`) and is read off the fit's own training pairs, by their
    age from that fit's last training row (`_fit_recency_logistic`).

    `rare`, for the rare-event study (#381): a treatment of
    `PRESSURE_RARE_EVENT_SETTINGS["treatments"]`, applied inside each fit to
    its training pairs only (`_fit_rare_event`). It is refused for the probit
    and quantile kinds, and checked here so a bad name fails at construction.

    `design`, for the scarcity-conditioned calendar (#128) only: a prebuilt
    design (`_ScarcityCalendarDesign`) used in place of `_PressureDesign`'s
    from `features` and `products`. Its `monotone` constraints, when it has
    them, reach the classifier.

    `history`, for the pre-SOFR history study (#129) only: `(rows, rule)`, the
    `effr_history` rows and their as-of rule. Their direct pairs are built with
    this design (`effr_history.history_pairs`), pooled with every fit's SOFR
    pairs, and told apart by `HISTORY_MARKET_COLUMN`; a forecast is served as
    the SOFR market. Every fit refuses a pooled label not public before its
    last training day (`effr_history.require_pool_public`), and a rule whose
    horizon is not the run's. No public factory takes it: it is a study
    candidate, not a declared model.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    if rare is not None:
        if kind not in ("logistic", "gbm_classifier"):
            raise ValueError(f"a rare-event treatment is the logistic's or the classifier's, not {kind!r}")
        if rare not in PRESSURE_RARE_EVENT_SETTINGS["treatments"]:
            raise ValueError(
                f"unknown rare-event treatment {rare!r}; one of "
                f"{list(PRESSURE_RARE_EVENT_SETTINGS['treatments'])}"
            )
        if rare == "focal" and kind != "gbm_classifier":
            raise ValueError("the focal loss is the gradient-boosted classifier's")
    if recency is not None:
        mode, parameter = recency
        if kind != "logistic" or rare != "class_weight":
            raise ValueError("recency weighting is the class-weighted logistic's")
        if mode not in PRESSURE_RECENCY_SETTINGS["modes"]:
            raise ValueError(f"unknown recency mode {mode!r}; one of {list(PRESSURE_RECENCY_SETTINGS['modes'])}")
        if parameter < 1:
            raise ValueError(f"a recency half-life or window must be positive, got {parameter}")
    if design is None:
        design = _PressureDesign(features, declaration, products)
    monotone = getattr(design, "monotone", None)
    cache: dict = {}
    pooled: dict = {}
    selections: List[Mapping[str, Any]] = []
    shrinkage: List[float] = []
    effects: List[dict] = []

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None:
            raise ValueError(
                "a direct pressure model pairs each training label with what was "
                "public at that label's own decision instant, which only the as-of "
                "rule can say; it was called without one"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a direct pressure model needs at least {minimum_history} training "
                f"rows, got {len(train_rows)}"
            )
        if design.needs_history() and (
            histories is None or len(histories) != len(feature_rows)
        ):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; "
                "one history per feature row is required"
            )
        positions: List[int] = []
        xs, spreads = _pressure_pairs(design, information, train_rows, cache, positions)
        if not xs:
            raise ValueError("no training label has a complete as-of read")
        ages = [len(train_rows) - 1 - position for position in positions]
        served = [
            design.row(
                row,
                _served_tga_change(histories[day], row) if design.needs_history() else None,
            )
            for day, row in enumerate(feature_rows)
        ]
        if history is not None:
            from . import effr_history

            history_rows, history_rule = history
            if history_rule.horizon != information.horizon:
                raise ValueError(
                    f"the history is read at horizon {history_rule.horizon}, the run "
                    f"at {information.horizon}"
                )
            if "pool" not in pooled:
                pooled["pool"] = effr_history.history_pairs(design, history_rule, history_rows)
            pool = pooled["pool"]
            effr_history.require_pool_public(pool.available_at, train_rows[-1].date)
            xs = [list(x) + [0.0] for x in xs] + [list(x) + [1.0] for x in pool.xs]
            spreads = list(spreads) + list(pool.spreads)
            served = [list(x) + [0.0] for x in served]
        columns: List[List[float]] = []
        # Two thresholds with no training spread between them have one label
        # vector, so one fit: the estimator is deterministic in its labels.
        fitted: dict = {}
        shrinkage.clear()
        effects.clear()
        if kind in ("quantile", "quantile_skewt"):
            law = _quantile_exceedance(
                xs, spreads, served, [float(tau) for tau in taus], smoother="skew_t" if kind == "quantile_skewt" else "linear"
            )
            columns = [[curve[k] for curve in law] for k in range(len(taus))]
        elif kind in _DISTRIBUTION_KINDS:
            law, chosen = _distribution_exceedance(
                kind, xs, spreads, served, [float(tau) for tau in taus], information.horizon
            )
            selections.append(chosen)
            columns = [[curve[k] for curve in law] for k in range(len(taus))]
        if kind.startswith("two_part_"):
            columns = _two_part_columns(
                kind[len("two_part_"):], xs, spreads, served, [float(tau) for tau in taus], monotone
            )
        for tau in (
            taus
            if kind not in ("quantile", "quantile_skewt")
            and kind not in _DISTRIBUTION_KINDS
            and not kind.startswith("two_part_")
            else ()
        ):
            labels = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
            if len(set(labels)) < 2:
                columns.append([float(labels[0])] * len(served))
                continue
            key = tuple(labels)
            if key not in fitted:
                fitted[key] = _fit_classifier(
                    kind,
                    xs,
                    labels,
                    served,
                    monotone=monotone,
                    pooling=getattr(design, "pooling", None),
                    rare=rare,
                    shrinkage_trace=shrinkage,
                    effects_trace=effects,
                    recency=None if recency is None else (recency[0], recency[1], ages),
                )
            columns.append(fitted[key])
        curves = []
        for day in range(len(served)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(
            {
                "logistic": PRESSURE_LOGISTIC_SETTINGS,
                "probit": PRESSURE_PROBIT_SETTINGS,
                "quantile": PRESSURE_QUANTILE_SETTINGS,
                "two_part_logistic": {**PRESSURE_LOGISTIC_SETTINGS, "two_part": dict(TWO_PART_SETTINGS)},
                "two_part_gbm_classifier": {**PRESSURE_CLASSIFIER_SETTINGS, "two_part": dict(TWO_PART_SETTINGS)},
                "quantile_skewt": PRESSURE_QUANTILE_SKEWT_SETTINGS,
                "qrf": PRESSURE_QRF_SETTINGS,
                "ng_normal": PRESSURE_NATURAL_GRADIENT_SETTINGS,
                "ng_laplace": PRESSURE_NATURAL_GRADIENT_SETTINGS,
            }.get(kind, PRESSURE_CLASSIFIER_SETTINGS)
        )
        if kind in _DISTRIBUTION_KINDS:
            settings["selection"] = dict(PRESSURE_DISTRIBUTION_SELECTION)
            if kind != "qrf":
                settings["family"] = kind[len("ng_"):]
        settings["design"] = list(design.names)
        if rare is not None:
            settings["rare_event"] = {
                "treatment": rare,
                **{
                    key: _plain(value)
                    for key, value in PRESSURE_RARE_EVENT_SETTINGS.items()
                    if key in ("class_weight", rare)
                },
            }
        if recency is not None:
            settings["recency"] = {
                "mode": recency[0],
                "parameter": recency[1],
                "minimum_window_events": PRESSURE_RECENCY_SETTINGS["minimum_window_events"],
            }
        if history is not None:
            pool = pooled["pool"]
            settings["design"].append(HISTORY_MARKET_COLUMN)
            settings["pooled_history"] = {
                "pairs": len(pool.xs),
                "first": pool.dates[0].isoformat() if pool.dates else None,
                "last": pool.dates[-1].isoformat() if pool.dates else None,
                "horizon": pool.horizon,
            }
        if design.scarcity:
            settings["scarcity_state"] = SCARCITY_STATE
        if design.tga:
            settings["tga_change_rows"] = TGA_CHANGE_ROWS
        if design.products:
            settings["products"] = [list(pair) for pair in design.products]
        if isinstance(design, _ScarcityCalendarDesign):
            settings["scarcity_calendar"] = design.settings()
            if shrinkage:
                settings["regime_shrinkage_chosen"] = list(shrinkage)
            if effects:
                settings["regime_effects"] = list(effects)
        if monotone is not None:
            settings["monotonic_cst"] = list(monotone)
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=(
                None
                if histories is None
                else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    #: What each distribution fit chose on the pressure-day labels, one entry per fit.
    fit_predict.selections = selections  # type: ignore[attr-defined]
    return fit_predict


def _geometric_size_survival(
    xs: Sequence[Sequence[float]],
    excess: Sequence[float],
    served: Sequence[Sequence[float]],
    steps: Sequence[float],
) -> List[Tuple[float, ...]]:
    """P(excess > t | x) at each served row and each step t, for a geometric size law (#382).

    `xs` and `excess` are the spike days' design rows and whole-bp excess over the
    spike threshold (each at least 1). The excess is geometric on 1, 2, ... with mean
    m(x) = 1 + exp(linear index), the index fitted by a ridge Poisson regression of
    `excess - 1` on the standardized design (`TWO_PART_SETTINGS`); then
    P(excess > t) = (1 - 1/m)^t, which is 1 at t = 0 and non-increasing in t. With fewer
    than `TWO_PART_SETTINGS["min_spike_days"]` spike days the mean is the pooled one.
    """

    import numpy

    settings = TWO_PART_SETTINGS
    e = numpy.asarray(excess, dtype=float)
    if len(e) and float(e.min()) < 1.0:
        raise ValueError("the excess over the spike threshold is at least one whole basis point")
    z = numpy.asarray(served, dtype=float)
    if len(e) == 0:
        mean = numpy.full(len(z), 1.0)
    elif len(e) < settings["min_spike_days"]:
        mean = numpy.full(len(z), float(e.mean()))
    else:
        from sklearn.linear_model import PoissonRegressor

        x = numpy.asarray(xs, dtype=float)
        centre, scale = _standardizer(x)
        model = PoissonRegressor(alpha=settings["alpha"], max_iter=settings["max_iter"])
        model.fit((x - centre) / scale, e - 1.0)
        mean = 1.0 + model.predict((z - centre) / scale)
    ratio = numpy.clip(1.0 - 1.0 / numpy.maximum(mean, 1.0), 0.0, 1.0)
    return [tuple(float(r) ** float(t) for t in steps) for r in ratio]


def _two_part_columns(
    classifier: str,
    xs: Sequence[Sequence[float]],
    spreads: Sequence[float],
    served: Sequence[Sequence[float]],
    taus: Sequence[float],
    monotone: Optional[Sequence[int]],
) -> List[List[float]]:
    """One exceedance column per tau: P(spike) times the conditional size survival (#382)."""

    spike = float(TWO_PART_SETTINGS["spike_bp"])
    labels = [1 if exceeds_bp(value, spike) else 0 for value in spreads]
    if len(set(labels)) < 2:
        p_spike = [float(labels[0])] * len(served)
    else:
        p_spike = _fit_classifier(classifier, xs, labels, served, monotone=monotone)
    spike_rows = [x for x, label in zip(xs, labels) if label]
    excess = [round(float(value)) - spike for value, label in zip(spreads, labels) if label]
    above = [tau for tau in taus if tau >= spike]
    survival = _geometric_size_survival(spike_rows, excess, served, [tau - spike for tau in above])
    columns = []
    for tau in taus:
        if tau >= spike:
            k = above.index(tau)
            columns.append([p_spike[day] * survival[day][k] for day in range(len(served))])
            continue
        # below the spike threshold the size law says nothing: the classifier on that threshold's own label
        direct = [1 if exceeds_bp(value, tau) else 0 for value in spreads]
        columns.append(
            [float(direct[0])] * len(served)
            if len(set(direct)) < 2
            else _fit_classifier(classifier, xs, direct, served, monotone=monotone)
        )
    # No smoothing and no prior: the parametric tail never reaches past the largest
    # spread the fit has seen, so a threshold above every training spread is a hard zero.
    for k, tau in enumerate(taus):
        if not any(exceeds_bp(value, tau) for value in spreads):
            columns[k] = [0.0] * len(served)
    return columns


def _fit_classifier(
    kind: str,
    xs: Sequence[Sequence[float]],
    labels: Sequence[int],
    served: Sequence[Sequence[float]],
    monotone: Optional[Sequence[int]] = None,
    pooling: Optional[Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[float, ...], Optional[float]]] = None,
    shrinkage_trace: Optional[List[float]] = None,
    effects_trace: Optional[List[dict]] = None,
    rare: Optional[str] = None,
    recency: Optional[Tuple[str, int, Sequence[int]]] = None,
) -> List[float]:
    """Fit one estimator to one threshold's labels; P(label = 1) at `served`.

    `recency`, the class-weighted logistic's only (#411): `(mode, parameter,
    ages)`, one age per training pair (`_fit_recency_logistic`).

    `pooling`, the logistic's only (#378): `(pooled columns, deviation columns,
    regimes, scale)`. Column 1 is the regime. The fit is the pooled columns plus,
    for each regime, an intercept and the deviation columns, each multiplied by
    `scale` and by the regime's indicator, under the one L2 penalty: a regime's
    deviations are shrunk toward the pooled fit, and a regime with no training
    day is served the pooled fit. `None` passes nothing, so every other fit is
    unchanged. A `scale` of `None` (#386) is estimated from this fit's training
    pairs alone by `_empirical_bayes_scale` and appended to `shrinkage_trace`;
    `effects_trace`, if given, receives `_regime_effects` of the fit.

    `rare`, the rare-event treatments' (#381): one of
    `PRESSURE_RARE_EVENT_SETTINGS["treatments"]`, applied to the training rows
    handed in and to nothing else (`_fit_rare_event`). `None`, the default,
    passes nothing, so every existing fit is unchanged.

    `monotone`, the classifier's only: one of -1, 0, +1 per design column,
    passed to scikit-learn as `monotonic_cst` (#128). `None`, the default,
    passes nothing, so every existing fit is unchanged.
    """

    _estimator_class()  # the extra's refusal, in this repository's vocabulary
    import numpy

    x = numpy.asarray(xs, dtype=float)
    y = numpy.asarray(labels, dtype=int)
    z = numpy.asarray(served, dtype=float)
    if recency is not None:
        if kind != "logistic" or rare != "class_weight" or monotone is not None:
            raise ValueError("recency weighting is the unconstrained class-weighted logistic's")
        return _fit_recency_logistic(x, y, z, numpy.asarray(recency[2], dtype=float), recency[0], recency[1])
    if rare is not None:
        if monotone is not None:
            raise ValueError("a monotone constraint is not combined with a rare-event treatment")
        return _fit_rare_event(kind, rare, x, y, z)
    if kind == "logistic":
        if monotone is not None:
            raise ValueError("a monotone constraint is the gradient-boosted classifier's, not the logistic's")
        from sklearn.linear_model import LogisticRegression

        centre = x.mean(axis=0)
        scale = x.std(axis=0)
        scale[scale == 0.0] = 1.0
        if pooling is not None:
            pooled, deviating, regimes, shrink = pooling
            if shrink is None:
                shrink = _empirical_bayes_scale(x, y, pooled, deviating, regimes)
                if shrinkage_trace is not None:
                    shrinkage_trace.append(shrink)
            original_scale = scale
            x = _pool_columns((x - centre) / scale, x[:, 1], pooled, deviating, regimes, shrink)
            z = _pool_columns((z - centre) / scale, z[:, 1], pooled, deviating, regimes, shrink)
            centre, scale = numpy.zeros(x.shape[1]), numpy.ones(x.shape[1])
        model = LogisticRegression(
            C=PRESSURE_LOGISTIC_SETTINGS["C"],
            max_iter=PRESSURE_LOGISTIC_SETTINGS["max_iter"],
        )
        model.fit((x - centre) / scale, y)
        if pooling is not None and effects_trace is not None:
            effects_trace.append(
                _regime_effects(model.coef_[0], pooled, deviating, regimes, shrink, original_scale)
            )
        return [float(p) for p in model.predict_proba((z - centre) / scale)[:, 1]]
    if kind == "probit":
        return _fit_probit(x, y, z)
    from sklearn.ensemble import HistGradientBoostingClassifier

    settings = PRESSURE_CLASSIFIER_SETTINGS
    constraint = {}
    if monotone is not None:
        if len(monotone) != x.shape[1] or any(value not in (-1, 0, 1) for value in monotone):
            raise ValueError(
                f"a monotone constraint is one of -1, 0, +1 per design column; got "
                f"{list(monotone)} for {x.shape[1]} columns"
            )
        constraint = {"monotonic_cst": [int(value) for value in monotone]}
    model = HistGradientBoostingClassifier(
        learning_rate=settings["learning_rate"],
        max_iter=settings["max_iter"],
        max_leaf_nodes=settings["max_leaf_nodes"],
        min_samples_leaf=settings["min_samples_leaf"],
        random_state=settings["random_state"],
        early_stopping=False,
        **constraint,
    )
    model.fit(x, y)
    return [float(p) for p in model.predict_proba(z)[:, 1]]


def _plain(value: Any) -> Any:
    """A read-only settings tree as plain dicts and lists, for a JSON record."""

    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _balanced_indices(labels: Any, seed: int) -> Any:
    """Row indices of one event-balanced bootstrap of the training labels.

    Half the draws (`PRESSURE_RARE_EVENT_SETTINGS["balanced_bootstrap"]["event_share"]`)
    are made with replacement from the rows labelled 1, the rest from the rows
    labelled 0. It reads only `labels`, the training rows of one fit, and a
    seed: no served row and no later label can enter it.
    """

    import numpy

    y = numpy.asarray(labels, dtype=int)
    events = numpy.flatnonzero(y == 1)
    calm = numpy.flatnonzero(y == 0)
    if len(events) == 0 or len(calm) == 0:
        raise ValueError("a balanced bootstrap needs both classes among the training labels")
    share = PRESSURE_RARE_EVENT_SETTINGS["balanced_bootstrap"]["event_share"]
    drawn_events = int(round(share * len(y)))
    rng = numpy.random.default_rng(seed)
    return numpy.concatenate(
        [
            rng.choice(events, size=drawn_events, replace=True),
            rng.choice(calm, size=len(y) - drawn_events, replace=True),
        ]
    )


def _focal_gradient(logit: Any, labels: Any, gamma: float, alpha: float) -> Any:
    """d(focal loss)/d(logit), per row (Lin et al. 2017).

    `FL = -alpha (1 - p)^gamma log p` for a 1 and `-(1 - alpha) p^gamma log(1 - p)`
    for a 0, with `p = sigmoid(logit)`.
    """

    import numpy

    p = numpy.clip(1.0 / (1.0 + numpy.exp(-numpy.asarray(logit, dtype=float))), 1e-12, 1.0 - 1e-12)
    y = numpy.asarray(labels, dtype=int)
    positive = alpha * (gamma * (1.0 - p) ** gamma * p * numpy.log(p) - (1.0 - p) ** (gamma + 1.0))
    negative = -(1.0 - alpha) * (
        gamma * p**gamma * (1.0 - p) * numpy.log(1.0 - p) - p ** (gamma + 1.0)
    )
    return numpy.where(y == 1, positive, negative)


def _fit_focal(x: Any, y: Any, z: Any) -> List[float]:
    """A gradient-boosted classifier on the focal loss, numpy and scikit-learn only.

    Newton boosting: each round fits a regression tree (`max_leaf_nodes`,
    `min_samples_leaf` of `PRESSURE_RARE_EVENT_SETTINGS["focal"]`) to
    `-g / h` weighted by `h`, then sets each leaf to `-sum(g) / (sum(h) + l2)`.
    `g` is `_focal_gradient`; `h` is its central difference in the logit,
    floored (the focal loss is not convex). Starts from the training event
    rate's logit. Deterministic. Returns P(label = 1) at `z`.
    """

    import numpy
    from sklearn.tree import DecisionTreeRegressor

    cfg = PRESSURE_RARE_EVENT_SETTINGS["focal"]
    rate = min(max(float(y.mean()), 1e-6), 1.0 - 1e-6)
    base = math.log(rate / (1.0 - rate))
    score = numpy.full(len(y), base)
    served = numpy.full(len(z), base)
    step = cfg["hessian_step"]
    for _ in range(cfg["rounds"]):
        g = _focal_gradient(score, y, cfg["gamma"], cfg["alpha"])
        h = (
            _focal_gradient(score + step, y, cfg["gamma"], cfg["alpha"])
            - _focal_gradient(score - step, y, cfg["gamma"], cfg["alpha"])
        ) / (2.0 * step)
        h = numpy.maximum(h, cfg["hessian_floor"])
        tree = DecisionTreeRegressor(
            max_leaf_nodes=cfg["max_leaf_nodes"],
            min_samples_leaf=cfg["min_samples_leaf"],
            random_state=DEFAULT_RANDOM_STATE,
        )
        tree.fit(x, -g / h, sample_weight=h)
        leaf = tree.apply(x)
        leaves = numpy.unique(leaf)
        value = {
            int(node): float(-g[leaf == node].sum() / (h[leaf == node].sum() + cfg["l2"]))
            for node in leaves
        }
        score = score + cfg["learning_rate"] * numpy.array([value[int(node)] for node in leaf])
        served = served + cfg["learning_rate"] * numpy.array(
            [value.get(int(node), 0.0) for node in tree.apply(z)]
        )
    return [float(p) for p in 1.0 / (1.0 + numpy.exp(-served))]


def _fit_recency_logistic(x: Any, y: Any, z: Any, ages: Any, mode: str, parameter: float) -> List[float]:
    """The class-weighted logistic fitted to favour recent pairs (#411); P(label = 1) at `z`.

    `ages` is each pair's age in panel rows from the fit's last training row, so it reads
    the training pairs of this one fit and nothing later.

    * `decay`: pair weight 0.5 ** (age / parameter), times a class weight that balances the
      two classes on the *weighted* totals (n_w / (2 W_class), the form
      `class_weight="balanced"` takes for unit weights).
    * `window`: only pairs with age < parameter, class-balanced; the whole history when the
      window holds fewer than `PRESSURE_RECENCY_SETTINGS["minimum_window_events"]` events or
      lacks a class.
    """

    import numpy
    from sklearn.linear_model import LogisticRegression

    if mode not in PRESSURE_RECENCY_SETTINGS["modes"]:
        raise ValueError(f"unknown recency mode {mode!r}; one of {list(PRESSURE_RECENCY_SETTINGS['modes'])}")
    if len(ages) != len(y):
        raise ValueError("one age per training pair is required")
    if mode == "decay":
        weight = 0.5 ** (ages / float(parameter))
    else:
        keep = ages < parameter
        if y[keep].sum() < PRESSURE_RECENCY_SETTINGS["minimum_window_events"] or y[keep].sum() == keep.sum():
            keep = numpy.ones(len(y), dtype=bool)
        weight = keep.astype(float)
    total = weight.sum()
    for label in (0, 1):
        mass = weight[y == label].sum()
        if mass <= 0.0:
            raise ValueError("a recency fit needs both classes among its weighted pairs")
        weight = numpy.where(y == label, weight * total / (2.0 * mass), weight)
    used = weight > 0.0
    centre = x[used].mean(axis=0)
    scale = x[used].std(axis=0)
    scale[scale == 0.0] = 1.0
    model = LogisticRegression(C=PRESSURE_LOGISTIC_SETTINGS["C"], max_iter=PRESSURE_LOGISTIC_SETTINGS["max_iter"])
    model.fit((x[used] - centre) / scale, y[used], sample_weight=weight[used])
    return [float(p) for p in model.predict_proba((z - centre) / scale)[:, 1]]


def standardised_logistic_probabilities(
    train_x: Sequence[Sequence[float]],
    train_y: Sequence[int],
    test_x: Sequence[Sequence[float]],
    *,
    c: float = 1.0,
    max_iter: int = 1000,
) -> List[float]:
    """P(y = 1) at each row of `test_x`, from a logistic regression on features standardised by the training rows (#453).

    The turning-point switch of `scripts/turning_point_variant.py` fits this at each refit block. A column with no
    variance in the training rows is left unscaled. Needs both classes in `train_y`.

    Raises:
        MissingMLExtraError: numpy or scikit-learn is not installed.
        ValueError: `train_y` holds one class only.
    """

    try:
        import numpy
        from sklearn.linear_model import LogisticRegression
    except ImportError as error:  # pragma: no cover - exercised without the extra
        raise MissingMLExtraError(
            "the standardised logistic needs the optional 'ml' extra (numpy and scikit-learn); install it with "
            "`pip install -e \".[ml]\"`"
        ) from error
    x = numpy.asarray(train_x, dtype=float)
    y = numpy.asarray(train_y, dtype=int)
    if y.min() == y.max():
        raise ValueError("a logistic fit needs both classes among its training rows")
    centre = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0.0] = 1.0
    model = LogisticRegression(C=c, max_iter=max_iter)
    model.fit((x - centre) / scale, y)
    z = numpy.asarray(test_x, dtype=float)
    return [float(p) for p in model.predict_proba((z - centre) / scale)[:, 1]]


def _fit_rare_event(kind: str, treatment: str, x: Any, y: Any, z: Any) -> List[float]:
    """One threshold's fit with a rare-event treatment (#381); P(label = 1) at `z`.

    * `class_weight`: the logistic or the histogram gradient-boosted classifier
      with `class_weight="balanced"`.
    * `focal`: `_fit_focal` (the gradient-boosted classifier only).
    * `balanced_bootstrap`: `bags` fits, each on `_balanced_indices` of the
      training rows with the plain estimator, averaged. Seeds are the
      classifier's `random_state` plus the bag number.

    Everything is computed from `x` and `y`, the training rows of the one fit.
    """

    import numpy

    if treatment not in PRESSURE_RARE_EVENT_SETTINGS["treatments"]:
        raise ValueError(
            f"unknown rare-event treatment {treatment!r}; one of "
            f"{list(PRESSURE_RARE_EVENT_SETTINGS['treatments'])}"
        )
    if kind not in ("logistic", "gbm_classifier"):
        raise ValueError(f"a rare-event treatment is the logistic's or the classifier's, not {kind!r}")
    if treatment == "focal":
        if kind != "gbm_classifier":
            raise ValueError("the focal loss is the gradient-boosted classifier's")
        return _fit_focal(x, y, z)

    def estimator(weighted: bool):
        if kind == "logistic":
            from sklearn.linear_model import LogisticRegression

            return LogisticRegression(
                C=PRESSURE_LOGISTIC_SETTINGS["C"],
                max_iter=PRESSURE_LOGISTIC_SETTINGS["max_iter"],
                class_weight=PRESSURE_RARE_EVENT_SETTINGS["class_weight"] if weighted else None,
            )
        from sklearn.ensemble import HistGradientBoostingClassifier

        cfg = PRESSURE_CLASSIFIER_SETTINGS
        return HistGradientBoostingClassifier(
            learning_rate=cfg["learning_rate"],
            max_iter=cfg["max_iter"],
            max_leaf_nodes=cfg["max_leaf_nodes"],
            min_samples_leaf=cfg["min_samples_leaf"],
            random_state=cfg["random_state"],
            early_stopping=False,
            class_weight=PRESSURE_RARE_EVENT_SETTINGS["class_weight"] if weighted else None,
        )

    if kind == "logistic":
        centre, scale = _standardizer(x)
        x, z = (x - centre) / scale, (z - centre) / scale
    if treatment == "class_weight":
        return [float(p) for p in estimator(True).fit(x, y).predict_proba(z)[:, 1]]
    bags = PRESSURE_RARE_EVENT_SETTINGS["balanced_bootstrap"]["bags"][kind]
    total = numpy.zeros(len(z))
    for bag in range(bags):
        rows = _balanced_indices(y, PRESSURE_CLASSIFIER_SETTINGS["random_state"] + bag)
        total += estimator(False).fit(x[rows], y[rows]).predict_proba(z)[:, 1]
    return [float(p) for p in total / bags]


def _pool_columns(
    standardized: Any,
    regime: Any,
    pooled: Sequence[int],
    deviating: Sequence[int],
    regimes: Sequence[float],
    shrink: float,
) -> Any:
    """The partially pooled design (#378): pooled columns, then each regime's shrunk deviations."""

    import numpy

    blocks = [standardized[:, list(pooled)]]
    for level in regimes:
        indicator = (regime == level).astype(float)[:, None]
        blocks.append(shrink * indicator)
        blocks.append(shrink * indicator * standardized[:, list(deviating)])
    return numpy.hstack(blocks)


def _regime_effects(
    coefficients: Any,
    pooled: Sequence[int],
    deviating: Sequence[int],
    regimes: Sequence[float],
    shrink: float,
    scale: Any,
) -> dict:
    """A partially pooled logistic's coefficients, per regime and in the design's own units (#386).

    `coefficients` are those of `_pool_columns`'s columns. For each regime, by
    design column index: the logit change per unit of that column, which is the
    pooled coefficient (if the column is pooled) plus the regime's shrunk
    deviation (if it deviates), divided by the column's training scale; and
    `"intercept"`, the regime's own shrunk intercept shift. Also the `"pooled"`
    coefficients on their own and the `shrink` used.
    """

    width = len(pooled)
    block = 1 + len(deviating)
    effects: dict = {"shrink": float(shrink), "pooled": {int(j): float(coefficients[i] / scale[j]) for i, j in enumerate(pooled)}}
    by_regime: dict = {}
    for k, level in enumerate(regimes):
        start = width + k * block
        entry = {"intercept": float(shrink * coefficients[start])}
        for i, j in enumerate(deviating):
            deviation = shrink * coefficients[start + 1 + i]
            total = deviation + (coefficients[list(pooled).index(j)] if j in pooled else 0.0)
            entry[int(j)] = float(total / scale[j])
        for i, j in enumerate(pooled):
            entry.setdefault(int(j), float(coefficients[i] / scale[j]))
        by_regime[float(level)] = entry
    effects["regimes"] = by_regime
    return effects


def _laplace_log_evidence(design: Any, y: Any) -> float:
    """The Laplace-approximated log marginal likelihood of a ridge logistic (#386).

    The model is `LogisticRegression`'s: an unpenalized intercept and a Gaussian
    prior of variance `C` on every column of `design`, `C` from
    `PRESSURE_LOGISTIC_SETTINGS`. The posterior mode is found by Newton's method
    and the evidence is `-nll(w) - |w|^2 / 2C - log det(H) / 2 + k log(1/C) / 2`,
    with `H` the penalized Hessian at the mode. The `log det` term is the Occam
    factor: a deviation column the data do not need lowers the evidence.
    """

    import numpy
    from scipy.special import expit

    n, k = design.shape
    prior = 1.0 / PRESSURE_LOGISTIC_SETTINGS["C"]
    a = numpy.hstack([numpy.ones((n, 1)), design])
    precision = numpy.diag([0.0] + [prior] * k)
    w = numpy.zeros(k + 1)
    rate = min(max(float(y.mean()), 1e-6), 1 - 1e-6)
    w[0] = math.log(rate / (1 - rate))
    for _ in range(100):
        p = expit(a @ w)
        gradient = a.T @ (p - y) + precision @ w
        hessian = (a.T * (p * (1.0 - p))) @ a + precision + 1e-10 * numpy.eye(k + 1)
        step = numpy.linalg.solve(hessian, gradient)
        w = w - numpy.clip(step, -4.0, 4.0)
        if float(numpy.max(numpy.abs(step))) < 1e-9:
            break
    eta = a @ w
    nll = float(numpy.sum(numpy.logaddexp(0.0, eta) - y * eta))
    p = expit(eta)
    hessian = (a.T * (p * (1.0 - p))) @ a + precision + 1e-10 * numpy.eye(k + 1)
    _, logdet = numpy.linalg.slogdet(hessian)
    penalized = w[1:]
    return float(-nll - 0.5 * prior * float(penalized @ penalized) - 0.5 * logdet + 0.5 * k * math.log(prior))


def _empirical_bayes_scale(
    x: Any, y: Any, pooled: Sequence[int], deviating: Sequence[int], regimes: Sequence[float]
) -> float:
    """The deviation scale in `REGIME_SHRINKAGE_GRID` with the greatest evidence (#386).

    Empirical Bayes: the prior spread of the regime deviations is chosen by
    maximizing the Laplace-approximated marginal likelihood of this fit's own
    training pairs, so it reads nothing but `x` and `y`. A tie goes to the
    smaller scale (more pooling). Column 1 of `x` is the regime.
    """

    import numpy

    centre = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0.0] = 1.0
    standardized = (x - centre) / scale
    best, best_evidence = None, -math.inf
    for candidate in REGIME_SHRINKAGE_GRID:
        evidence = _laplace_log_evidence(_pool_columns(standardized, x[:, 1], pooled, deviating, regimes, candidate), y)
        if evidence > best_evidence:
            best, best_evidence = candidate, evidence
    return float(best)


def _fit_probit(x: Any, y: Any, z: Any) -> List[float]:
    """A ridge probit by Fisher scoring, numpy and scipy only; P(y = 1) at `z`.

    Columns standardized on `x`; the intercept is unpenalized, the other
    coefficients carry `ridge` (`PRESSURE_PROBIT_SETTINGS`). Deterministic.
    """

    import numpy
    from scipy.stats import norm

    centre, scale = _standardizer(x)
    design = numpy.hstack([numpy.ones((len(x), 1)), (x - centre) / scale])
    ridge = numpy.full(design.shape[1], PRESSURE_PROBIT_SETTINGS["ridge"])
    ridge[0] = 0.0
    rate = min(max(float(y.mean()), 1e-6), 1 - 1e-6)
    w = numpy.zeros(design.shape[1])
    w[0] = norm.ppf(rate)

    def objective(weights: Any) -> float:
        eta = design @ weights
        p = numpy.clip(norm.cdf(eta), 1e-12, 1 - 1e-12)
        return float(-numpy.sum(y * numpy.log(p) + (1 - y) * numpy.log1p(-p)) + 0.5 * numpy.sum(ridge * weights**2))

    current = objective(w)
    for _ in range(PRESSURE_PROBIT_SETTINGS["iterations"]):
        eta = design @ w
        p = numpy.clip(norm.cdf(eta), 1e-12, 1 - 1e-12)
        density = norm.pdf(eta)
        gradient = design.T @ (density * (p - y) / (p * (1 - p))) + ridge * w
        weight = density**2 / (p * (1 - p))
        fisher = (design * weight[:, None]).T @ design + numpy.diag(ridge) + 1e-10 * numpy.eye(len(w))
        step = numpy.linalg.solve(fisher, gradient)
        size = 1.0
        while True:
            trial = w - size * step
            value = objective(trial)
            if value <= current + 1e-12 or size < 1e-8:
                break
            size /= 2.0
        converged = abs(current - value) < 1e-10
        w, current = trial, value
        if converged:
            break
    return [float(p) for p in norm.cdf(w[0] + ((z - centre) / scale) @ w[1:])]


#: The fixed grid the skew-t's CDF is integrated on (#379): the standardized variable
#: from about -2,700 to +2,700, dense near zero, so a heavy tail (a few degrees of
#: freedom) still has its mass inside the grid.
_SKEW_T_POINTS = 1501
_SKEW_T_SPAN = 7.5
_SKEW_T_MINIMUM_SCALE = 1e-3


def _skew_t_cdf_grid(shape: float, dof: float) -> Tuple[Any, Any]:
    """The Azzalini-Capitanio skew-t's standardized CDF on the fixed grid.

    The density is `2 t_dof(z) T_(dof+1)(shape z sqrt((dof+1) / (z^2 + dof)))`;
    its trapezoid integral is normalized to end at 1. Returns `(z, cdf)`.
    """

    import numpy
    from scipy import stats

    z = numpy.sinh(numpy.linspace(-_SKEW_T_SPAN, _SKEW_T_SPAN, _SKEW_T_POINTS)) * 3.0
    density = 2.0 * stats.t.pdf(z, dof) * stats.t.cdf(shape * z * numpy.sqrt((dof + 1.0) / (z * z + dof)), dof + 1.0)
    cdf = numpy.concatenate([[0.0], numpy.cumsum(0.5 * (density[1:] + density[:-1]) * numpy.diff(z))])
    return z, cdf / cdf[-1]


def _skew_t_exceedance(
    quantiles: Any, probabilities: Any, cuts: Sequence[float]
) -> Tuple[float, ...]:
    """P(spread > cut) from one day's predicted quantiles, through a fitted skew-t.

    Adrian, Boyarchenko & Giannone (2019): the predicted quantiles of the
    conditional distribution are smoothed into a skewed t by least squares on the
    quantile function over the grid's probabilities; the exceedance is read off the
    fitted CDF. The start is fixed (`PRESSURE_QUANTILE_SKEWT_SETTINGS`), so a day's
    law does not depend on the days fitted before it. Non-increasing in the cut by
    construction. A day whose quantiles are all equal is a point mass there.

    Args:
        quantiles: the day's predicted quantiles, sorted, one per probability.
        probabilities: the quantile grid, increasing, inside (0, 1).
        cuts: the spread levels (bp) at which the exceedance is read.
    """

    import numpy
    from scipy.optimize import minimize

    q = numpy.asarray(quantiles, dtype=float)
    p = numpy.asarray(probabilities, dtype=float)
    if q.shape != p.shape:
        raise ValueError(f"{len(q)} quantiles for {len(p)} probabilities")
    if float(q[-1] - q[0]) < _SKEW_T_MINIMUM_SCALE:
        return tuple(1.0 if float(q.mean()) > cut else 0.0 for cut in cuts)
    start = PRESSURE_QUANTILE_SKEWT_SETTINGS["start"]
    spread = max(float(q[-1] - q[0]) / 4.0, _SKEW_T_MINIMUM_SCALE)

    def law(theta: Any) -> Tuple[Any, Any, float, float]:
        z, cdf = _skew_t_cdf_grid(float(theta[2]), 1.0 + math.exp(float(theta[3])))
        return z, cdf, float(theta[0]), math.exp(float(theta[1]))

    def loss(theta: Any) -> float:
        if abs(theta[2]) > 50.0 or not -3.0 < theta[3] < 8.0:
            return 1e12
        z, cdf, location, scale = law(theta)
        return float(numpy.sum((location + scale * numpy.interp(p, cdf, z) - q) ** 2))

    theta0 = numpy.array(
        [float(numpy.median(q)), math.log(spread), start["shape"], math.log(start["degrees_of_freedom"] - 1.0)]
    )
    # Nelder-Mead's default simplex perturbs a zero start (the shape) by 0.00025, which
    # leaves it a symmetric law; the simplex is spelled out, one step per parameter.
    steps = numpy.array([0.25 * spread, 0.3, 1.5, 0.7])
    simplex = numpy.vstack([theta0] + [theta0 + numpy.eye(4)[k] * steps[k] for k in range(4)])
    fit = minimize(
        loss, theta0, method="Nelder-Mead",
        options={"maxiter": 400, "xatol": 1e-3, "fatol": 1e-9, "initial_simplex": simplex},
    )
    z, cdf, location, scale = law(fit.x)
    below = numpy.interp((numpy.asarray(cuts, dtype=float) - location) / scale, z, cdf)
    return tuple(float(min(1.0, max(0.0, 1.0 - value))) for value in below)


def _quantile_exceedance(
    xs: Sequence[Sequence[float]],
    spreads: Sequence[float],
    served: Sequence[Sequence[float]],
    taus: Sequence[float],
    smoother: str = "linear",
) -> List[Tuple[float, ...]]:
    """Linear quantile regressions of the spread, read as P(spread > tau) per day.

    `smoother` is `"linear"` (the default: linear interpolation between the
    predicted quantiles) or `"skew_t"` (`_skew_t_exceedance`, #379).

    One `QuantileRegressor` per grid quantile (`PRESSURE_QUANTILE_SETTINGS`), on
    columns standardized on `xs`. A day's predicted quantiles are sorted (the
    crossing fix), the law is linear between them, and the curve at `tau` is
    `1 - F(floor(tau) + 0.5)`: the whole-basis-point event of
    `data.exceeds_bp`. Non-increasing in `tau` by construction.
    """

    _estimator_class()
    import numpy
    from sklearn.linear_model import QuantileRegressor

    x = numpy.asarray(xs, dtype=float)
    y = numpy.asarray(spreads, dtype=float)
    centre, scale = _standardizer(x)
    train = (x - centre) / scale
    given = (numpy.asarray(served, dtype=float) - centre) / scale
    grid = PRESSURE_QUANTILE_SETTINGS["quantile_grid"]
    predicted = numpy.column_stack(
        [
            QuantileRegressor(
                quantile=q, alpha=PRESSURE_QUANTILE_SETTINGS["alpha"], solver="highs"
            ).fit(train, y).predict(given)
            for q in grid
        ]
    )
    predicted.sort(axis=1)
    probabilities = numpy.asarray(grid, dtype=float)
    if smoother == "skew_t":
        return [
            _skew_t_exceedance(row, probabilities, [math.floor(float(tau)) + 0.5 for tau in taus])
            for row in predicted
        ]
    if smoother != "linear":
        raise ValueError(f"a quantile smoother is 'linear' or 'skew_t', got {smoother!r}")
    curves = []
    for row in predicted:
        # Beyond the outer quantiles the law runs on at the outer segment's slope
        # to probability 0 / 1, so the curve reaches 0 and 1 (np.interp needs
        # increasing knots: ties are nudged by one part in a million of a bp).
        knots = row + 1e-6 * numpy.arange(len(row))
        low = (knots[1] - knots[0]) / (probabilities[1] - probabilities[0])
        high = (knots[-1] - knots[-2]) / (probabilities[-1] - probabilities[-2])
        edges = numpy.concatenate(
            [[knots[0] - probabilities[0] * low], knots, [knots[-1] + (1.0 - probabilities[-1]) * high]]
        )
        levels = numpy.concatenate([[0.0], probabilities, [1.0]])
        curve = []
        for tau in taus:
            cut = math.floor(float(tau)) + 0.5
            below = float(numpy.interp(cut, edges, levels))
            curve.append(float(min(1.0, max(0.0, 1.0 - below))))
        curves.append(tuple(curve))
    return curves


def pressure_logistic_exceedance(
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    products: Sequence[Tuple[str, str]] = (),
) -> ExceedancePredictor:
    """A direct logistic model of the pressure label (#114).

    At each threshold, a logistic regression of `spread > tau` on
    `_PressureDesign`'s design, standardized on the training pairs, with the
    settings in `PRESSURE_LOGISTIC_SETTINGS`. The pairs are direct: each label
    is paired with what a forecast of it would have read under the run's
    as-of rule, at the run's horizon (`_pressure_pairs`). A threshold whose
    training labels are all one value gets that value. The curve is made
    non-increasing in tau by a running minimum.

    Args:
        features: the declared feature set; the design follows from it.
        declaration: the split declaration that defines the pressure-day types
            (`evaluation_splits.load_split_declaration`).
        minimum_history: the shortest training frame that may produce a fit.
        products: product terms added to the design (`_PressureDesign`, #127);
            empty for pressure model v1.

    Raises:
        ValueError: on a design the features cannot support, a short frame, or
            a call without the as-of rule.
        LookAheadError: if a served TGA change would not start at its as-of
            read (`_served_tga_change`).
    """

    return _direct_pressure_predictor(
        "logistic", features, declaration, minimum_history, products
    )


def pressure_classifier_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """A gradient-boosted classifier of the pressure label (#114).

    `pressure_logistic_exceedance` with a histogram gradient-boosted classifier
    in place of the logistic, fitted with `PRESSURE_CLASSIFIER_SETTINGS`, on the
    same design and the same direct pairs.
    """

    return _direct_pressure_predictor("gbm_classifier", features, declaration, minimum_history)


def pressure_rare_event_exceedance(
    kind: str,
    treatment: str,
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    recency: Optional[Tuple[str, int]] = None,
) -> ExceedancePredictor:
    """The direct logistic or classifier fitted for the rare event (#381).

    `recency`, `(mode, parameter)` of `PRESSURE_RECENCY_SETTINGS` (#411): the
    class-weighted logistic with a decaying sample weight or a trailing window.

    `kind` is `"logistic"` or `"gbm_classifier"`; `treatment` is one of
    `PRESSURE_RARE_EVENT_SETTINGS["treatments"]`: `class_weight`, `focal`
    (classifier only) or `balanced_bootstrap`. The design, the direct pairs and
    the guards are those of `pressure_logistic_exceedance`; only the fit
    differs, and it reads that fit's training pairs alone. The probabilities
    are distorted on purpose; read them recalibrated out of fold
    (`pressure.recalibrated`).
    """

    return _direct_pressure_predictor(
        kind, features, declaration, minimum_history, rare=treatment, recency=recency
    )


# --------------------------------------------------------------------------
# The onset classifier (#409, track O of #374)
# --------------------------------------------------------------------------
#
# Separate definitions, not options of `_direct_pressure_predictor`: that function and the design and
# pair builders it reaches are hashed into the final test's pre-registered checksums
# (`docs/decisions/final-test-preregistration.md`), so an option added to them would move a pinned
# checksum. These reuse them without changing them.


class _OnsetDesign(_PressureDesign):
    """`_PressureDesign` with declared columns that may be unobserved (#409).

    An `optional` column is a declared linear column other than `reserve_balances`. It enters as its
    value, zero where not yet public, followed by an `<name>_observed` indicator (1 or 0), so a
    series with a short or gappy history trains on every day.
    """

    def __init__(self, features: Sequence[str], declaration: Any, optional: Sequence[str] = ()) -> None:
        super().__init__(features, declaration)
        self.optional = tuple(dict.fromkeys(str(name) for name in optional))
        for name in self.optional:
            if name not in self.linear or name == "reserve_balances":
                raise ValueError(
                    f"an optional column is a declared linear column other than reserve_balances; "
                    f"{name!r} is not"
                )
        names = list(self.names)
        for name in self.optional:
            names.insert(names.index(name) + 1, f"{name}_observed")
        self.names = tuple(names)

    def row(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        seen = {}
        values = dict(observation.values)
        for name in self.optional:
            raw = values.get(name)
            seen[name] = raw is not None and math.isfinite(float(raw))
            if not seen[name]:
                values[name] = 0.0
        out = super().row(DailyObservation(observation.date, values), tga_change)
        # `_PressureDesign.row`: the spread, then the linear columns in declared order.
        position = 1
        for name in self.linear:
            position += 1
            if name in self.optional:
                out.insert(position, 1.0 if seen[name] else 0.0)
                position += 1
        return out


def _onset_labels(
    labels: Sequence[int], targets: Sequence[int], train_rows: Sequence[DailyObservation], tau: float
) -> List[int]:
    """The exceedance labels of the pairs, kept only where the day is an onset (#409).

    `labels[k]` is 1 when the pair's target day, row `targets[k]` of `train_rows`, is above `tau`.
    It stays 1 only when none of the `ONSET_QUIET_DAYS` rows before the target is:
    `pressure.onsets`' rule, read off the training rows alone, every one of which is at or before
    the target.
    """

    return [
        1
        if label
        and not any(
            exceeds_bp(float(prior.spread_bps), tau)
            for prior in train_rows[target - ONSET_QUIET_DAYS : target]
        )
        else 0
        for label, target in zip(labels, targets)
    ]


def pressure_onset_exceedance(
    kind: str,
    treatment: Optional[str],
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    optional: Sequence[str] = (),
    fitter: Optional[Any] = None,
) -> ExceedancePredictor:
    """The direct logistic or classifier fitted to the onset label (#409).

    `fitter`, when given (#479), replaces `_fit_classifier` for the fits: it is called as
    `fitter(kind, xs, labels, served)` and returns the probabilities at `served`. `None`, the
    default, changes nothing.

    `kind` is `"logistic"` or `"gbm_classifier"`; `treatment` is `None` or one of
    `PRESSURE_RARE_EVENT_SETTINGS["treatments"]` (#381). The label at each threshold is an onset
    (`pressure.onsets`: a day above it with no such day on the five panel days before it), read off
    the training rows alone; a training day with fewer than that many panel days before it trains
    no pair. The design, the direct pairs and the guards are those of
    `pressure_logistic_exceedance`; `optional` names declared columns that enter with an observed
    indicator (`_OnsetDesign`). The curve across thresholds is made non-increasing, as the
    exceedance-curve interface requires. The probabilities are those of an onset, not of a pressure
    day; read them recalibrated out of fold (`pressure.recalibrated`).
    """

    if kind not in ("logistic", "gbm_classifier"):
        raise ValueError(f"an onset classifier is the logistic or the classifier, not {kind!r}")
    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    if treatment is not None and treatment not in PRESSURE_RARE_EVENT_SETTINGS["treatments"]:
        raise ValueError(
            f"unknown rare-event treatment {treatment!r}; one of "
            f"{list(PRESSURE_RARE_EVENT_SETTINGS['treatments'])}"
        )
    if treatment == "focal" and kind != "gbm_classifier":
        raise ValueError("the focal loss is the gradient-boosted classifier's")
    design = _OnsetDesign(features, declaration, optional)
    cache: dict = {}

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None:
            raise ValueError(
                "an onset classifier pairs each training label with what was public at that label's "
                "own decision instant, which only the as-of rule can say; it was called without one"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"an onset classifier needs at least {minimum_history} training rows, got {len(train_rows)}"
            )
        if design.needs_history() and (histories is None or len(histories) != len(feature_rows)):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; one history per "
                "feature row is required"
            )
        xs, spreads = _pressure_pairs(design, information, train_rows, cache)
        # The pairs' label positions, from the cache `_pressure_pairs` just filled.
        base = (information.horizon, information.features)
        targets = [
            target
            for target in range(1, len(train_rows))
            if cache.get((base, train_rows[target].date)) is not None
        ]
        if len(targets) != len(xs):  # pragma: no cover - construction bug
            raise ValueError("the onset label positions and the training pairs are out of step")
        kept = [k for k, target in enumerate(targets) if target >= ONSET_QUIET_DAYS]
        xs = [xs[k] for k in kept]
        spreads = [spreads[k] for k in kept]
        targets = [targets[k] for k in kept]
        if not xs:
            raise ValueError("no training label has a complete as-of read")
        served = [
            design.row(
                row,
                _served_tga_change(histories[day], row) if design.needs_history() else None,
            )
            for day, row in enumerate(feature_rows)
        ]
        columns: List[List[float]] = []
        fitted: dict = {}
        for tau in taus:
            exceeds = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
            labels = _onset_labels(exceeds, targets, train_rows, float(tau))
            if len(set(labels)) < 2:
                columns.append([float(labels[0])] * len(served))
                continue
            key = tuple(labels)
            if key not in fitted:
                fitted[key] = (
                    _fit_classifier(kind, xs, labels, served, rare=treatment)
                    if fitter is None
                    else fitter(kind, xs, labels, served)
                )
            columns.append(fitted[key])
        curves = []
        for day in range(len(served)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(PRESSURE_LOGISTIC_SETTINGS if kind == "logistic" else PRESSURE_CLASSIFIER_SETTINGS)
        settings["design"] = list(design.names)
        settings["onset_label"] = f"exceedance with {ONSET_QUIET_DAYS} quiet panel days before"
        if treatment is not None:
            settings["rare_event"] = {
                "treatment": treatment,
                **{
                    key: _plain(value)
                    for key, value in PRESSURE_RARE_EVENT_SETTINGS.items()
                    if key in ("class_weight", treatment)
                },
            }
        if design.scarcity:
            settings["scarcity_state"] = SCARCITY_STATE
        if design.tga:
            settings["tga_change_rows"] = TGA_CHANGE_ROWS
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=(
                None
                if histories is None
                else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


# --------------------------------------------------------------------------
# The all-inputs onset classifiers (#479)
# --------------------------------------------------------------------------
#
# One model that reads every collected input at once. The design, the pair builder, the onset label
# and the guards are `pressure_onset_exceedance`'s; only the fit differs: the penalty (logistic) or the
# depth limit (gradient-boosted classifier) is chosen from a declared grid on the training pairs alone.

#: Declared in `metadata/all_inputs.json` before any score; not tuned on a scored day.
ALL_INPUTS_SETTINGS = MappingProxyType(
    {
        "folds": 4,
        "embargo_pairs": 5,
        "criterion": "log loss of the pooled held-out blocks",
        "logistic": MappingProxyType(
            {"penalties": ("l1", "l2"), "C": (0.01, 0.03, 0.1, 0.3, 1.0), "solver": "liblinear", "max_iter": 5000}
        ),
        "gbm": MappingProxyType(
            {
                "max_depth": (2, 3, 4),
                "learning_rate": 0.05,
                "max_iter": 200,
                "min_samples_leaf": 20,
                "l2_regularization": 1.0,
            }
        ),
        "default": MappingProxyType({"logistic": ("l2", 1.0), "gbm": (3,)}),
    }
)


def _blocked_folds(count: int, folds: int, embargo: int) -> List[Tuple[range, range]]:
    """Expanding-window folds over `count` pairs in time order: (train, validation) index ranges.

    The pairs are cut into `folds + 1` contiguous blocks; fold `j` validates on block `j` and trains on
    the blocks before it, less the last `embargo` pairs before the block, so no validation pair has a
    training pair within `embargo` positions of it. Only earlier pairs ever train a fold.
    """

    if folds < 1 or embargo < 0:
        raise ValueError("folds must be positive and the embargo not negative")
    edges = [round(count * k / (folds + 1)) for k in range(folds + 2)]
    out = []
    for j in range(1, folds + 1):
        train = range(0, max(0, edges[j] - embargo))
        out.append((train, range(edges[j], edges[j + 1])))
    return out


def _fit_with_setting(kind: str, setting: Tuple, x: Any, y: Any, z: Any) -> Any:
    """One fit at one grid point; the probabilities at `z`."""

    declared = ALL_INPUTS_SETTINGS["gbm" if kind == "gbm" else "logistic"]
    if kind == "logistic":
        from sklearn.linear_model import LogisticRegression

        penalty, c = setting
        centre = x.mean(axis=0)
        scale = x.std(axis=0)
        scale[scale == 0.0] = 1.0
        # scikit-learn 1.9 spells the penalty as the L1 share: 1 is L1, 0 is L2.
        model = LogisticRegression(
            l1_ratio=1.0 if penalty == "l1" else 0.0, C=c, solver=declared["solver"], max_iter=declared["max_iter"]
        )
        model.fit((x - centre) / scale, y)
        return model.predict_proba((z - centre) / scale)[:, 1]
    from sklearn.ensemble import HistGradientBoostingClassifier

    (depth,) = setting
    model = HistGradientBoostingClassifier(
        learning_rate=declared["learning_rate"],
        max_iter=declared["max_iter"],
        max_depth=depth,
        min_samples_leaf=declared["min_samples_leaf"],
        l2_regularization=declared["l2_regularization"],
        random_state=DEFAULT_RANDOM_STATE,
        early_stopping=False,
    )
    model.fit(x, y)
    return model.predict_proba(z)[:, 1]


def _grid_of(kind: str) -> List[Tuple]:
    if kind == "logistic":
        spec = ALL_INPUTS_SETTINGS["logistic"]
        return [(penalty, c) for c in spec["C"] for penalty in spec["penalties"]]
    return [(depth,) for depth in ALL_INPUTS_SETTINGS["gbm"]["max_depth"]]


def select_all_inputs_setting(kind: str, xs: Any, labels: Any) -> Tuple[Tuple, bool]:
    """The grid point with the lowest pooled held-out log loss on these training pairs alone.

    Returns `(setting, selected)`: `selected` is False when no fold could be scored (a training part
    with one class) and the declared default is returned. Ties go to the first point of the grid,
    the strongest penalty or the shallowest depth.
    """

    import numpy

    x = numpy.asarray(xs, dtype=float)
    y = numpy.asarray(labels, dtype=int)
    spec = ALL_INPUTS_SETTINGS
    folds = [
        (train, valid)
        for train, valid in _blocked_folds(len(y), spec["folds"], spec["embargo_pairs"])
        if len(train) and len(set(y[train.start : train.stop])) == 2 and len(valid)
    ]
    default = tuple(spec["default"]["logistic" if kind == "logistic" else "gbm"])
    if not folds:
        return default, False
    best, best_loss = default, None
    for setting in _grid_of(kind):
        loss, seen = 0.0, 0
        for train, valid in folds:
            p = _fit_with_setting(
                kind, setting, x[train.start : train.stop], y[train.start : train.stop], x[valid.start : valid.stop]
            )
            p = numpy.clip(p, 1e-6, 1.0 - 1e-6)
            yv = y[valid.start : valid.stop]
            loss -= float(numpy.sum(yv * numpy.log(p) + (1 - yv) * numpy.log(1.0 - p)))
            seen += len(yv)
        loss /= seen
        if best_loss is None or loss < best_loss - 1e-12:
            best, best_loss = setting, loss
    return best, True


def pressure_all_inputs_exceedance(
    kind: str,
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    optional: Sequence[str] = (),
) -> ExceedancePredictor:
    """The onset classifier on every declared input, its penalty or depth chosen on the training pairs (#479).

    `kind` is `"logistic"` (an L1 or L2 penalty and `C` from the declared grid) or `"gbm_classifier"` (a
    depth limit from the declared grid). Everything else is `pressure_onset_exceedance`. The predictor
    carries `selections`, one dict per fit: the chosen setting, whether it was selected or the default,
    and the pairs and onsets it rests on.
    """

    if kind not in ("logistic", "gbm_classifier"):
        raise ValueError(f"an all-inputs onset classifier is the logistic or the classifier, not {kind!r}")
    selections: List[dict] = []
    short = "logistic" if kind == "logistic" else "gbm"

    def fitter(_kind: str, xs: Any, labels: Any, served: Any) -> List[float]:
        import numpy

        setting, selected = select_all_inputs_setting(short, xs, labels)
        selections.append(
            {"setting": list(setting), "selected": selected, "pairs": len(labels), "onsets": int(sum(labels))}
        )
        p = _fit_with_setting(short, setting, numpy.asarray(xs, dtype=float), numpy.asarray(labels, dtype=int),
                              numpy.asarray(served, dtype=float))
        return [float(value) for value in p]

    predictor = pressure_onset_exceedance(
        kind, None, features, declaration, minimum_history=minimum_history, optional=optional, fitter=fitter
    )
    predictor.selections = selections  # type: ignore[attr-defined]
    return predictor


# --------------------------------------------------------------------------
# The five-day-window onset target (#460)
# --------------------------------------------------------------------------
#
# Separate definitions again: the design, the pair builder and `_fit_classifier` are reused, not changed.

#: The window of the target: a pressure onset on any of the next `WINDOW_ONSET_DAYS` panel days, the
#: first of which is the day a one-day-ahead forecast scores. It is the judge's week-ahead width
#: (`metadata/pressure_judge.json`, `tiers.week_ahead.days`).
WINDOW_ONSET_DAYS = 5


def _window_onset_labels(
    onsets: Sequence[int], targets: Sequence[int], width: int = WINDOW_ONSET_DAYS
) -> List[int]:
    """1 where an onset falls on a row of `targets[k] .. targets[k] + width - 1`, else 0 (#460).

    `onsets[r]` is 1 when row `r` of the training rows is an onset (`_onset_labels`' rule). A window
    reads the `width - 1` rows after its first, and a training frame ends at the refit's last known
    day, so a window that reaches past the last row would read a day whose outcome was not known
    at the refit.

    Raises:
        LookAheadError: if a window reaches past the last training row.
    """

    labels = []
    for target in targets:
        if target + width > len(onsets):
            raise LookAheadError(
                f"the window of row {target} reads rows up to {target + width - 1}, but the training "
                f"frame ends at row {len(onsets) - 1}; a window must end by the refit's last known day"
            )
        labels.append(1 if any(onsets[target : target + width]) else 0)
    return labels


def pressure_window_onset_exceedance(
    kind: str,
    treatment: Optional[str],
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    design: Optional[Any] = None,
) -> ExceedancePredictor:
    """The direct logistic or classifier fitted to "an onset in the next five panel days" (#460).

    Called at horizon 1, so a forecast made at day d is trained on pairs (as-of design at d', label
    of target row t = d' + 1) whose label is 1 when an onset (`pressure.onsets`' rule, as
    `_onset_labels`) falls on any of rows t .. t + 4. A pair whose window reaches past the last
    training row trains nothing (`_window_onset_labels` refuses it), as does a target with fewer than
    `ONSET_QUIET_DAYS` rows before it. `design`, when given, is a prebuilt design
    (`_ScarcityCalendarDesign`) used in place of `_PressureDesign`'s; its `monotone` and `pooling`
    reach the fit as in `_direct_pressure_predictor`. The probability is of an onset in the window,
    not of a pressure day; read it recalibrated out of fold against the window's outcome.
    """

    if kind not in ("logistic", "gbm_classifier"):
        raise ValueError(f"a window-onset classifier is the logistic or the classifier, not {kind!r}")
    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    if treatment is not None and treatment not in PRESSURE_RARE_EVENT_SETTINGS["treatments"]:
        raise ValueError(
            f"unknown rare-event treatment {treatment!r}; one of "
            f"{list(PRESSURE_RARE_EVENT_SETTINGS['treatments'])}"
        )
    if treatment == "focal" and kind != "gbm_classifier":
        raise ValueError("the focal loss is the gradient-boosted classifier's")
    if design is None:
        design = _PressureDesign(features, declaration)
    monotone = getattr(design, "monotone", None)
    cache: dict = {}
    shrinkage: List[float] = []
    effects: List[dict] = []

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None:
            raise ValueError(
                "a window-onset classifier pairs each training label with what was public at that "
                "label's own decision instant, which only the as-of rule can say; it was called "
                "without one"
            )
        if information.horizon != 1:
            raise ValueError(
                f"a window-onset classifier is called at horizon 1, the window's first day; got "
                f"{information.horizon}"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a window-onset classifier needs at least {minimum_history} training rows, "
                f"got {len(train_rows)}"
            )
        if design.needs_history() and (histories is None or len(histories) != len(feature_rows)):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; one history per "
                "feature row is required"
            )
        positions: List[int] = []
        xs, spreads = _pressure_pairs(design, information, train_rows, cache, positions)
        kept = [
            k
            for k, target in enumerate(positions)
            if target >= ONSET_QUIET_DAYS and target + WINDOW_ONSET_DAYS <= len(train_rows)
        ]
        xs = [xs[k] for k in kept]
        targets = [positions[k] for k in kept]
        if not xs:
            raise ValueError("no training label has a complete as-of read and a complete window")
        served = [
            design.row(
                row,
                _served_tga_change(histories[day], row) if design.needs_history() else None,
            )
            for day, row in enumerate(feature_rows)
        ]
        row_spreads = [float(row.spread_bps) for row in train_rows]
        columns: List[List[float]] = []
        fitted: dict = {}
        shrinkage.clear()
        effects.clear()
        for tau in taus:
            exceeds = [1 if exceeds_bp(value, float(tau)) else 0 for value in row_spreads]
            onsets = _onset_labels(exceeds, list(range(len(train_rows))), train_rows, float(tau))
            labels = _window_onset_labels(onsets, targets)
            if len(set(labels)) < 2:
                columns.append([float(labels[0])] * len(served))
                continue
            key = tuple(labels)
            if key not in fitted:
                fitted[key] = _fit_classifier(
                    kind,
                    xs,
                    labels,
                    served,
                    monotone=monotone,
                    pooling=getattr(design, "pooling", None),
                    rare=treatment,
                    shrinkage_trace=shrinkage,
                    effects_trace=effects,
                )
            columns.append(fitted[key])
        curves = []
        for day in range(len(served)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(PRESSURE_LOGISTIC_SETTINGS if kind == "logistic" else PRESSURE_CLASSIFIER_SETTINGS)
        settings["design"] = list(design.names)
        settings["window_onset_label"] = (
            f"an onset ({ONSET_QUIET_DAYS} quiet panel days before) on any of the next "
            f"{WINDOW_ONSET_DAYS} panel days, the first being the scored day"
        )
        if treatment is not None:
            settings["rare_event"] = {
                "treatment": treatment,
                **{
                    key: _plain(value)
                    for key, value in PRESSURE_RARE_EVENT_SETTINGS.items()
                    if key in ("class_weight", treatment)
                },
            }
        if design.scarcity:
            settings["scarcity_state"] = SCARCITY_STATE
        if design.tga:
            settings["tga_change_rows"] = TGA_CHANGE_ROWS
        if isinstance(design, _ScarcityCalendarDesign):
            settings["scarcity_calendar"] = design.settings()
            if shrinkage:
                settings["regime_shrinkage_chosen"] = list(shrinkage)
            if effects:
                settings["regime_effects"] = list(effects)
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=(
                None
                if histories is None
                else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


# --------------------------------------------------------------------------
# The risk-date severity model (#428, track V of #374)
# --------------------------------------------------------------------------
#
# About 22 of the 26 scored onsets fall on dates the calendar names in advance. This model is fitted
# on those dates alone and forecasts nothing on any other day: its probability on an ordinary day is
# exactly 0 at every threshold, so it never flags one. Separate definitions, as the onset
# classifier's are: the design and the pair builder are reused, not changed (the final test's
# pinned checksums hash `_direct_pressure_predictor` and its helpers).

#: The estimators of the risk-date model: a logistic and a gradient-boosted classifier of the pressure
#: label, and a skew-t quantile regression of the spread itself (the severity of the day).
#: Declared in `metadata/risk_date_severity.json`, not tuned.
RISK_DATE_KINDS = ("logistic", "gbm_classifier", "quantile_skewt")


class _RiskDateDesign(_PressureDesign):
    """`_PressureDesign`'s row with the risk-date membership appended as its last element (#428).

    A day is a *risk date* when its pressure-day type, read from the calendar columns as
    `EvaluationSplits.day_type` reads them, is not `ordinary` (a quarter-end, a month-end or a tax
    date), or when `treasury_settlement_coupons` is a declared input and the day settles a coupon.
    Both are facts about the scored day known in advance; the coupon column is declared only at
    horizon 1, where a settlement is public (`docs/decisions/information-set.md`). A day outside the
    set returns a row of zeros: it is neither trained nor served, so none of its inputs is read.
    """

    def __init__(self, features: Sequence[str], declaration: Any, products: Sequence[Tuple[str, str]] = ()) -> None:
        super().__init__(features, declaration, products)
        if not self.calendar:
            raise ValueError(
                f"a risk date is named by the calendar columns {list(_CALENDAR_INPUTS)}; declare all three"
            )

    def member(self, observation: DailyObservation) -> bool:
        if self.declaration.day_type(observation.values) != "ordinary":
            return True
        if "treasury_settlement_coupons" in self.settlements:
            return self._value(observation, "treasury_settlement_coupons") > 0.0
        return False

    def row(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        if not self.member(observation):
            return [0.0] * (len(self.names) + 1)
        return super().row(observation, tga_change) + [1.0]


def pressure_risk_date_exceedance(
    kind: str,
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
) -> ExceedancePredictor:
    """A model fitted and served on the declared risk dates only (#428).

    `kind` is one of `RISK_DATE_KINDS`. Training pairs are the direct pairs of
    `pressure_logistic_exceedance` (each label paired with what a forecast of it read at its own
    decision instant) kept where the label day is a risk date (`_RiskDateDesign`); the logistic
    and the classifier are fitted to `spread > tau` on those pairs, the quantile regression to the
    spread of those days, read as a skew-t law (`_quantile_exceedance`). A forecast of a risk date
    is the fit's probability; a forecast of any other day is exactly 0 at every threshold. The
    curve across thresholds is made non-increasing. A risk date in the served rows needs a fit: a
    frame with no risk-date pair raises `ValueError`.
    """

    if kind not in RISK_DATE_KINDS:
        raise ValueError(f"a risk-date model is one of {list(RISK_DATE_KINDS)}, got {kind!r}")
    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    design = _RiskDateDesign(features, declaration)
    cache: dict = {}

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None:
            raise ValueError(
                "a risk-date model pairs each training label with what was public at that label's "
                "own decision instant, which only the as-of rule can say; it was called without one"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a risk-date model needs at least {minimum_history} training rows, got {len(train_rows)}"
            )
        if design.needs_history() and (histories is None or len(histories) != len(feature_rows)):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; one history per "
                "feature row is required"
            )
        pairs, spreads = _pressure_pairs(design, information, train_rows, cache)
        flags = [pair[-1] for pair in pairs]
        xs = [pair[:-1] for pair, flag in zip(pairs, flags) if flag]
        spreads = [spread for spread, flag in zip(spreads, flags) if flag]
        served_all = [
            design.row(
                row,
                _served_tga_change(histories[day], row) if design.needs_history() else None,
            )
            for day, row in enumerate(feature_rows)
        ]
        members = [day for day, served in enumerate(served_all) if served[-1]]
        served = [served_all[day][:-1] for day in members]
        columns: List[List[float]] = [[0.0] * len(feature_rows) for _ in taus]
        if members:
            if not xs:
                raise ValueError("no risk-date training label has a complete as-of read")
            fitted: dict = {}
            if kind == "quantile_skewt":
                law = _quantile_exceedance(
                    xs, spreads, served, [float(tau) for tau in taus], smoother="skew_t"
                )
                fits = [[curve[k] for curve in law] for k in range(len(taus))]
            else:
                fits = []
                for tau in taus:
                    labels = [1 if exceeds_bp(value, float(tau)) else 0 for value in spreads]
                    if len(set(labels)) < 2:
                        fits.append([float(labels[0])] * len(served))
                        continue
                    key = tuple(labels)
                    if key not in fitted:
                        fitted[key] = _fit_classifier(kind, xs, labels, served)
                    fits.append(fitted[key])
            for position, fit in enumerate(fits):
                for day, value in zip(members, fit):
                    columns[position][day] = value
        curves = []
        for day in range(len(feature_rows)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(
            {
                "logistic": PRESSURE_LOGISTIC_SETTINGS,
                "quantile_skewt": PRESSURE_QUANTILE_SKEWT_SETTINGS,
            }.get(kind, PRESSURE_CLASSIFIER_SETTINGS)
        )
        settings["design"] = list(design.names)
        settings["risk_dates"] = (
            "quarter-end, month-end or tax date (day_type != ordinary)"
            + (", or a coupon settlement" if "treasury_settlement_coupons" in design.settlements else "")
        )
        settings["risk_date_training_pairs"] = len(xs)
        if design.scarcity:
            settings["scarcity_state"] = SCARCITY_STATE
        if design.tga:
            settings["tga_change_rows"] = TGA_CHANGE_ROWS
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=(
                None
                if histories is None
                else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


def pressure_probit_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """A ridge probit of the pressure label (#372; Copeland-Duffie-Yang, SR 974).

    `pressure_logistic_exceedance` with a probit link, fitted with
    `PRESSURE_PROBIT_SETTINGS`, on the same design and the same direct pairs.
    """

    return _direct_pressure_predictor("probit", features, declaration, minimum_history)


def pressure_two_part_exceedance(
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    classifier: str = "logistic",
) -> ExceedancePredictor:
    """A two-part (hurdle) model of the pressure label and its size (#382).

    Part one is `classifier` ("logistic" or "gbm_classifier") on `spread > +5 bp`,
    the spike. Part two is the conditional law of the spike's size (the whole-bp
    excess over +5 bp) on the same design, fitted on the spike days only
    (`_geometric_size_survival`). The exceedance at tau >= 5 bp is their product,
    `P(spike) * P(excess > tau - 5 | spike)`, so the curve is non-increasing in tau by
    construction and its +5 bp value is the classifier's. A threshold below +5 bp, where
    the size law is silent, is the classifier on that threshold's own label. Fitted on the
    direct, as-of-paired pairs (`_pressure_pairs`) like the other direct models.

    Raises:
        ValueError: on a design the features cannot support, a short frame, or a call
            without the as-of rule.
    """

    if classifier not in ("logistic", "gbm_classifier"):
        raise ValueError(f"the spike part is a logistic or a gbm_classifier, got {classifier!r}")
    return _direct_pressure_predictor(
        f"two_part_{classifier}", features, declaration, minimum_history
    )


def pressure_quantile_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """Quantile regressions of the spread, read as an exceedance curve (#372).

    A linear quantile regression of the spread (not of a label) at each grid
    quantile of `PRESSURE_QUANTILE_SETTINGS`, on the same design and the same
    direct pairs, smoothed to a distribution by linear interpolation
    (`_quantile_exceedance`; Adrian-Boyarchenko-Giannone, Copeland-Duffie-Yang).
    """

    return _direct_pressure_predictor("quantile", features, declaration, minimum_history)


#: The settlement-timing track's two estimators (#379), by the kind each names. Study
#: candidates, not declared models: no public factory and no `--model` name reaches
#: them, as with `SCARCITY_CALENDAR_KINDS`.
SETTLEMENT_TIMING_KINDS = MappingProxyType({"probit": "probit", "quantile_skewt": "quantile_skewt"})


def _settlement_timing_predictor(
    form: str,
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
) -> Any:
    """A probit or a skew-t quantile regression on settlement timing and scarcity (#379).

    `form` is `"probit"`, the ridge probit of #372 at each threshold, or
    `"quantile_skewt"`, the linear quantile regressions of #372 smoothed into a skew-t
    in the Adrian-Boyarchenko-Giannone way, both on `_PressureDesign`'s design of
    `features` (settlement size and timing, the calendar, the reserve-scarcity state
    and the TGA, as declared) and the same direct pairs under the as-of rule.
    """

    if form not in SETTLEMENT_TIMING_KINDS:
        raise ValueError(f"a settlement-timing form is one of {sorted(SETTLEMENT_TIMING_KINDS)}, got {form!r}")
    return _direct_pressure_predictor(SETTLEMENT_TIMING_KINDS[form], features, declaration, minimum_history)


# --------------------------------------------------------------------------
# The extreme-value tail (#383, track E of #374)
# --------------------------------------------------------------------------
#
# P(spread > tau) = P(spread > u) * S(tau - u), for a declared high threshold
# `u` below the lowest tau: a logistic body for the exceedance of `u`, and a
# generalised Pareto survival `S` for the excess, its scale a log-linear
# function of the reserve-scarcity state and the pressure-day type, fitted by
# maximum likelihood on the training excesses. Declared in
# `metadata/pressure_tail.json` before any score was computed.
#
# The spread is published to the basis point, so an integer spread `k` is an
# excess in an interval, not a point. With the continuous latent spread rounded
# to the basis point, `spread > u` is the latent spread above `u + 0.5`, the
# excess `Z` is measured from there, `spread = k` is `Z` in `[k - u - 1, k - u)`,
# and `spread > tau` is `Z >= tau - u`. The likelihood of an observation is the
# probability of its bin, `S(k - u - 1) - S(k - u)`, and a forecast of
# `spread > tau` is `S(tau - u)`.

#: Chosen before scoring, not tuned. The scale's columns are standardised on the
#: excess rows and ridge-penalised with `C` as the direct logistic's, the shape
#: is one constant per fit inside `GPD_SHAPE_BOUNDS` (the floor of
#: `docs/decisions/tail-shape-floor.md`), and a fit with fewer excesses than
#: `minimum_excesses` is an exponential (shape 0) with one constant scale.
PRESSURE_TAIL_SETTINGS = MappingProxyType(
    {
        "body": "logistic (PRESSURE_LOGISTIC_SETTINGS) on the label spread > u",
        "tail": "generalised Pareto on the excess over u + 0.5 bp, interval-censored to the basis point",
        "estimator": "maximum likelihood, BFGS with finite-difference gradient (numpy)",
        "scale": "log-linear in reserves (USD trillions) and the pressure-day type, standardised",
        "C": 1.0,
        "shape": "constant per fit, 0.5 * expit(s), inside GPD_SHAPE_BOUNDS",
        "minimum_excesses": 30,
        "fallback": "exponential, constant scale, below minimum_excesses; no excess: tail probability 0",
    }
)

#: The scale's design columns, in `_PressureDesign`'s names.
TAIL_SCALE_COLUMNS = ("reserve_balances",) + _PRESSURE_DAY_TYPES


class CensoredGpd(NamedTuple):
    """A fitted generalised Pareto tail with a log-linear scale.

    `mode` is `"gpd"` (shape fitted), `"exponential"` (too few excesses for a
    shape) or `"none"` (no excess at all: the tail probability is 0).
    """

    mode: str
    excesses: int
    intercept: float
    coefficients: Any
    centre: Any
    scale: Any
    shape: float
    log_likelihood: float

    def sigma(self, columns: Any) -> Any:
        import numpy

        z = (numpy.atleast_2d(numpy.asarray(columns, dtype=float)) - self.centre) / self.scale
        return numpy.exp(self.intercept + z @ self.coefficients)

    def survival(self, excess: float, columns: Any) -> Any:
        """`S(excess)` at each row of `columns`; 0 when there is no excess to read."""

        import numpy

        rows = numpy.atleast_2d(numpy.asarray(columns, dtype=float)).shape[0]
        if self.mode == "none":
            return numpy.zeros(rows)
        return numpy.exp(_gpd_log_survival(float(excess), self.sigma(columns), self.shape))


def _gpd_log_survival(z: Any, sigma: Any, shape: float) -> Any:
    """`log S(z)` of a generalised Pareto with scale `sigma` and `shape` >= 0."""

    import numpy

    z = numpy.asarray(z, dtype=float)
    if shape < 1e-8:
        return -z / sigma
    return -numpy.log1p(shape * z / sigma) / shape


def fit_censored_gpd(
    columns: Any,
    bins: Any,
    c: float = 1.0,
    minimum_excesses: int = 30,
) -> CensoredGpd:
    """Maximum-likelihood generalised Pareto tail for basis-point-rounded excesses.

    Args:
        columns: one row per excess, the scale's covariates.
        bins: each excess `k - u` as an integer of at least 1: the observation
            is the interval `[bins - 1, bins)` of the excess over `u + 0.5`.
        c: the ridge's `C` on the standardised columns (the intercept is free).
        minimum_excesses: fewer rows than this fit an exponential, constant
            scale; no rows at all fit nothing.

    Raises:
        ValueError: on a bin below 1 or rows and bins of different length.
    """

    _estimator_class()
    import numpy

    x = numpy.asarray(columns, dtype=float)
    k = numpy.asarray(bins, dtype=float)
    if len(k) == 0 and x.size == 0:
        width = x.shape[1] if x.ndim == 2 else 0
        return CensoredGpd("none", 0, 0.0, numpy.zeros(width), numpy.zeros(width), numpy.ones(width), 0.0, 0.0)
    if x.ndim != 2 or len(x) != len(k):
        raise ValueError(f"{len(k)} excesses need as many covariate rows, got shape {x.shape}")
    width = x.shape[1]
    if (k < 1.0).any():
        raise ValueError("an excess bin is at least 1 basis point above the threshold")
    centre, scale = _standardizer(x)
    z = (x - centre) / scale
    lower, upper = k - 1.0, k
    penalty = 1.0 / c
    gpd = len(k) >= minimum_excesses

    def unpack(theta: Any) -> Tuple[float, Any, float]:
        if not gpd:
            return float(theta[0]), numpy.zeros(width), 0.0
        return float(theta[0]), theta[1 : 1 + width], 0.5 * float(_expit(theta[1 + width]))

    def objective(theta: Any) -> float:
        intercept, beta, shape = unpack(theta)
        with numpy.errstate(all="ignore"):  # a wild line-search step is refused by `_bfgs`
            sigma = numpy.exp(intercept + z @ beta)
            log_low = _gpd_log_survival(lower, sigma, shape)
            log_high = _gpd_log_survival(upper, sigma, shape)
            gap = numpy.maximum(-numpy.expm1(log_high - log_low), 1e-300)
            value = -float(numpy.sum(log_low + numpy.log(gap)))
        return value + 0.5 * penalty * float(numpy.sum(beta**2))

    def with_gradient(theta: Any) -> Tuple[float, Any]:
        value = objective(theta)
        gradient = numpy.zeros(len(theta))
        for index in range(len(theta)):
            step = 1e-6 * max(1.0, abs(float(theta[index])))
            up, down = theta.copy(), theta.copy()
            up[index] += step
            down[index] -= step
            gradient[index] = (objective(up) - objective(down)) / (2.0 * step)
        return value, gradient

    start = [math.log(float(numpy.mean(k - 0.5)))]
    if gpd:
        start += [0.0] * width + [-2.0]
    theta, value = _bfgs(with_gradient, numpy.asarray(start, dtype=float))
    intercept, beta, shape = unpack(theta)
    penalised = 0.5 * penalty * float(numpy.sum(beta**2))
    return CensoredGpd(
        "gpd" if gpd else "exponential",
        int(len(k)),
        intercept,
        beta,
        centre,
        scale,
        shape,
        -(value - penalised),
    )


def pressure_tail_exceedance(
    features: Sequence[str],
    declaration: Any,
    *,
    minimum_history: int,
    threshold_bp: float,
    record: Optional[List[Mapping[str, Any]]] = None,
) -> Any:
    """A logistic body with a conditional generalised Pareto tail (#383).

    `P(spread > tau) = P(spread > u) * S(tau - u)` with `u = threshold_bp`.
    The body is a direct logistic of `spread > u` on `_PressureDesign`'s design
    (as `pressure_logistic_exceedance` fits any threshold); the tail is
    `fit_censored_gpd` on the training pairs whose spread exceeds `u`, its scale
    depending on `TAIL_SCALE_COLUMNS`. Both are fitted on the direct pairs under
    the run's as-of rule, so a training label is paired with what was public at
    its own decision instant, and a forecast's TGA change is read off its own
    as-of history.

    `record`, when a list, receives one mapping per fit: its fit summary and,
    for each served row in order (`anchor` is the row's own date, the latest day
    whose spread was public), the body probability and the scale, which with the
    fit's shape is what the tail diagnostics are computed from.

    Raises:
        ValueError: on a design without reserves and the calendar (the scale
            depends on both), a `tau` not above `u`, a short frame, or a call
            without the as-of rule.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    design = _PressureDesign(features, declaration)
    if not (design.scarcity and design.calendar):
        raise ValueError(
            "the tail's scale depends on the reserve-scarcity state and the pressure-day "
            "type; declare reserve_balances and the three calendar columns"
        )
    scale_index = [design.names.index(name) for name in TAIL_SCALE_COLUMNS]
    settings_minimum = int(PRESSURE_TAIL_SETTINGS["minimum_excesses"])
    cache: dict = {}

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None:
            raise ValueError(
                "a tail model pairs each training label with what was public at that "
                "label's own decision instant, which only the as-of rule can say; it "
                "was called without one"
            )
        for tau in taus:
            if float(tau) <= threshold_bp:
                raise ValueError(
                    f"the tail starts at u = {threshold_bp:g} bp and gives no probability "
                    f"at tau = {float(tau):g} bp, which is not above it"
                )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a tail model needs at least {minimum_history} training rows, got "
                f"{len(train_rows)}"
            )
        if design.needs_history() and (
            histories is None or len(histories) != len(feature_rows)
        ):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; "
                "one history per feature row is required"
            )
        xs, spreads = _pressure_pairs(design, information, train_rows, cache)
        if not xs:
            raise ValueError("no training label has a complete as-of read")
        served = [
            design.row(
                row,
                _served_tga_change(histories[day], row) if design.needs_history() else None,
            )
            for day, row in enumerate(feature_rows)
        ]
        labels = [1 if exceeds_bp(value, threshold_bp) else 0 for value in spreads]
        if len(set(labels)) < 2:
            body = [float(labels[0])] * len(served)
        else:
            body = _fit_classifier("logistic", xs, labels, served)
        excess_rows = [i for i, label in enumerate(labels) if label]
        tail = fit_censored_gpd(
            [[xs[i][j] for j in scale_index] for i in excess_rows],
            [round(spreads[i] - threshold_bp) for i in excess_rows],
            c=PRESSURE_TAIL_SETTINGS["C"],
            minimum_excesses=settings_minimum,
        )
        served_scale = [[row[j] for j in scale_index] for row in served]
        columns = [
            [float(b * s) for b, s in zip(body, tail.survival(float(tau) - threshold_bp, served_scale))]
            for tau in taus
        ]
        if record is not None:
            sigmas = [float(s) for s in tail.sigma(served_scale)] if tail.mode != "none" else [0.0] * len(served)
            record.append(
                {
                    "mode": tail.mode,
                    "excesses": tail.excesses,
                    "train_rows": len(train_rows),
                    "train_end": train_rows[-1].date.isoformat(),
                    "shape": tail.shape,
                    "intercept": tail.intercept,
                    "coefficients": {
                        name: float(value) for name, value in zip(TAIL_SCALE_COLUMNS, tail.coefficients)
                    },
                    "log_likelihood": tail.log_likelihood,
                    "served": [
                        {"anchor": row.date.isoformat(), "body": float(b), "sigma": s}
                        for row, b, s in zip(feature_rows, body, sigmas)
                    ],
                }
            )
        curves = []
        for day in range(len(served)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(PRESSURE_TAIL_SETTINGS)
        settings["threshold_bp"] = threshold_bp
        settings["design"] = list(design.names)
        settings["scale_columns"] = list(TAIL_SCALE_COLUMNS)
        settings["scarcity_state"] = SCARCITY_STATE
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=(
                None
                if histories is None
                else tuple(history[-1].date if history else None for history in histories)
            ),
        )

    return fit_predict


# --------------------------------------------------------------------------
# Full predictive distributions with better tails (#385; track Q of #374)
# --------------------------------------------------------------------------
#
# Two models of the whole conditional distribution of the spread, on the same
# direct design and pairs as the probit and the quantile regressions of #372:
# a quantile regression forest, which keeps each leaf's outcomes and so can put
# mass wherever the training spreads went, and a natural-gradient boosting of a
# parametric law (normal or Laplace), numpy plus scikit-learn trees. Both are
# read as `P(spread > tau)` on whole basis points, so a curve can be taken at
# every whole basis point and scored by CRPS as well as at +5 and +10 bp.
# Each has one hyperparameter, chosen on the pressure-day labels at +5 and +10
# bp over the last quarter of the training pairs, never on the spread's own loss.

_DISTRIBUTION_KINDS = ("qrf", "ng_normal", "ng_laplace")


def _selection_blocks(count: int, horizon: int) -> Optional[Tuple[slice, slice]]:
    """The training pairs' fit block and the later validation block, `None` if too few.

    The pairs run in target-date order. The validation block is the last
    `share` of them; the `horizon` pairs before it are dropped, so no fit pair's
    label window overlaps a validation pair's. Too few pairs for either block
    gives `None`: the declared default is used and nothing is selected.
    """

    rule = PRESSURE_DISTRIBUTION_SELECTION
    valid = max(int(count * float(rule["share"])), 0)
    fit_end = count - valid - horizon
    if fit_end < int(rule["minimum_fit_pairs"]) or valid < int(rule["minimum_validation_pairs"]):
        return None
    return slice(0, fit_end), slice(count - valid, count)


def _label_brier(probabilities: Any, spreads: Any, taus: Sequence[float]) -> float:
    """Mean over `taus` of the Brier score of `P(spread > tau)` against the whole-bp label."""

    import numpy

    total = 0.0
    for column, tau in enumerate(taus):
        labels = numpy.array([1.0 if exceeds_bp(v, tau) else 0.0 for v in spreads])
        total += float(numpy.mean((probabilities[:, column] - labels) ** 2))
    return total / len(taus)


def _forest(x: Any, y: Any, min_samples_leaf: int) -> Any:
    from sklearn.ensemble import RandomForestRegressor

    settings = PRESSURE_QRF_SETTINGS
    return RandomForestRegressor(
        n_estimators=settings["n_estimators"],
        max_features=settings["max_features"],
        bootstrap=settings["bootstrap"],
        min_samples_leaf=int(min_samples_leaf),
        random_state=settings["random_state"],
        n_jobs=1,
    ).fit(x, y)


def _forest_exceedance(forest: Any, x: Any, y: Any, z: Any, taus: Sequence[float]) -> Any:
    """Meinshausen's weights at the rows of `z`, read as `P(spread > tau)`: (rows, taus)."""

    import numpy

    leaves_train = forest.apply(x)
    leaves_given = forest.apply(z)
    weight = numpy.zeros((len(z), len(x)))
    for tree in range(leaves_train.shape[1]):
        sizes = numpy.bincount(leaves_train[:, tree])
        same = leaves_given[:, tree][:, None] == leaves_train[:, tree][None, :]
        weight += same / sizes[leaves_given[:, tree]][:, None]
    weight /= leaves_train.shape[1]
    above = numpy.array([[1.0 if exceeds_bp(v, tau) else 0.0 for tau in taus] for v in y])
    return weight @ above


def _family_survival(family: str, cut: float, location: Any, log_scale: Any) -> Any:
    import numpy

    scale = numpy.exp(log_scale)
    if family == "normal":
        from scipy.stats import norm

        return norm.sf(cut, loc=location, scale=scale)
    from scipy.stats import laplace

    return laplace.sf(cut, loc=location, scale=scale)


def _natural_gradient(family: str, y: Any, location: Any, log_scale: Any) -> Tuple[Any, Any]:
    """The natural gradient of the negative log-likelihood in (location, log-scale).

    The ordinary gradient times the inverse Fisher information, which for
    both families is diagonal: normal, `(-(y - m), (1 - z^2) / 2)` with
    `z = (y - m) / s`; Laplace, `(-b * sign(y - m), 1 - |y - m| / b)`.
    """

    import numpy

    scale = numpy.exp(log_scale)
    residual = y - location
    if family == "normal":
        return -residual, 0.5 * (1.0 - (residual / scale) ** 2)
    return -scale * numpy.sign(residual), 1.0 - numpy.abs(residual) / scale


class _NaturalGradientFit(NamedTuple):
    family: str
    location: float
    log_scale: float
    trees: Tuple[Tuple[Any, Any], ...]


def _fit_natural_gradient(family: str, x: Any, y: Any, stages: int) -> _NaturalGradientFit:
    """Boost the two parameters with regression trees on the natural gradient, deterministic."""

    import numpy
    from sklearn.tree import DecisionTreeRegressor

    settings = PRESSURE_NATURAL_GRADIENT_SETTINGS
    floor = math.log(float(settings["scale_floor_bp"]))
    ceiling = math.log(float(settings["scale_ceiling_bp"]))
    location0 = float(numpy.median(y))
    spread0 = float(numpy.mean(numpy.abs(y - location0))) if family == "laplace" else float(numpy.std(y))
    log_scale0 = min(max(math.log(max(spread0, 1e-9)), floor), ceiling)
    location = numpy.full(len(y), location0)
    log_scale = numpy.full(len(y), log_scale0)
    rate = float(settings["learning_rate"])
    trees = []
    for _ in range(int(stages)):
        grad_location, grad_scale = _natural_gradient(family, y, location, log_scale)
        pair = []
        for target in (grad_location, grad_scale):
            tree = DecisionTreeRegressor(
                max_depth=settings["max_depth"],
                min_samples_leaf=settings["min_samples_leaf"],
                random_state=settings["random_state"],
            ).fit(x, target)
            pair.append(tree)
        location = location - rate * pair[0].predict(x)
        log_scale = numpy.clip(log_scale - rate * pair[1].predict(x), floor, ceiling)
        trees.append(tuple(pair))
    return _NaturalGradientFit(family, location0, log_scale0, tuple(trees))


def _natural_gradient_parameters(fit: _NaturalGradientFit, z: Any, stage_grid: Sequence[int]) -> dict:
    """{stages: (location, log_scale)} at the rows of `z`, for each stage count in the grid."""

    import numpy

    settings = PRESSURE_NATURAL_GRADIENT_SETTINGS
    floor = math.log(float(settings["scale_floor_bp"]))
    ceiling = math.log(float(settings["scale_ceiling_bp"]))
    rate = float(settings["learning_rate"])
    location = numpy.full(len(z), fit.location)
    log_scale = numpy.full(len(z), fit.log_scale)
    wanted = set(int(n) for n in stage_grid)
    out = {}
    if 0 in wanted:
        out[0] = (location.copy(), log_scale.copy())
    for count, (tree_location, tree_scale) in enumerate(fit.trees, start=1):
        location = location - rate * tree_location.predict(z)
        log_scale = numpy.clip(log_scale - rate * tree_scale.predict(z), floor, ceiling)
        if count in wanted:
            out[count] = (location.copy(), log_scale.copy())
    return out


def _parametric_exceedance(
    family: str, location: Any, log_scale: Any, taus: Sequence[float]
) -> Any:
    import numpy

    return numpy.column_stack(
        [_family_survival(family, math.floor(float(tau)) + 0.5, location, log_scale) for tau in taus]
    )


def _distribution_exceedance(
    kind: str,
    xs: Sequence[Sequence[float]],
    spreads: Sequence[float],
    served: Sequence[Sequence[float]],
    taus: Sequence[float],
    horizon: int,
) -> Tuple[List[Tuple[float, ...]], Mapping[str, Any]]:
    """`P(spread > tau)` per served row from a full conditional distribution, and what was chosen.

    The hyperparameter (the forest's leaf size, the boosting's stage count) is
    chosen on the validation block of `_selection_blocks` by the label Brier
    score at `PRESSURE_DISTRIBUTION_SELECTION["taus"]`; the model is then
    refitted on every pair. With too few pairs for a validation block the
    declared default is used.
    """

    _estimator_class()
    import numpy

    x = numpy.asarray(xs, dtype=float)
    y = numpy.asarray(spreads, dtype=float)
    z = numpy.asarray(served, dtype=float)
    selection_taus = [float(t) for t in PRESSURE_DISTRIBUTION_SELECTION["taus"]]
    blocks = _selection_blocks(len(y), horizon)
    if kind == "qrf":
        grid = [int(v) for v in PRESSURE_QRF_SETTINGS["min_samples_leaf_grid"]]
        chosen = int(PRESSURE_QRF_SETTINGS["default_min_samples_leaf"])
        scores = {}
        if blocks is not None:
            fit_block, valid_block = blocks
            for leaf in grid:
                forest = _forest(x[fit_block], y[fit_block], leaf)
                given = _forest_exceedance(forest, x[fit_block], y[fit_block], x[valid_block], selection_taus)
                scores[leaf] = _label_brier(given, y[valid_block], selection_taus)
            chosen = min(grid, key=lambda leaf: (scores[leaf], leaf))
        forest = _forest(x, y, chosen)
        curves = _forest_exceedance(forest, x, y, z, taus)
        record = {"kind": kind, "min_samples_leaf": chosen, "validation_brier": scores}
    else:
        family = kind[len("ng_"):]
        grid = [int(v) for v in PRESSURE_NATURAL_GRADIENT_SETTINGS["stage_grid"]]
        chosen = int(PRESSURE_NATURAL_GRADIENT_SETTINGS["default_stages"])
        scores = {}
        if blocks is not None:
            fit_block, valid_block = blocks
            fitted = _fit_natural_gradient(family, x[fit_block], y[fit_block], max(grid))
            staged = _natural_gradient_parameters(fitted, x[valid_block], grid)
            for stages in grid:
                location, log_scale = staged[stages]
                given = _parametric_exceedance(family, location, log_scale, selection_taus)
                scores[stages] = _label_brier(given, y[valid_block], selection_taus)
            chosen = min(grid, key=lambda stages: (scores[stages], stages))
        fitted = _fit_natural_gradient(family, x, y, chosen)
        location, log_scale = _natural_gradient_parameters(fitted, z, [chosen])[chosen]
        curves = _parametric_exceedance(family, location, log_scale, taus)
        # The law has no mass beyond the declared support: a threshold that far above
        # anything fitted gets a hard zero, as every other implementer's does.
        limit = float(y.max()) + float(PRESSURE_NATURAL_GRADIENT_SETTINGS["support_above_training_max_bp"])
        for column, tau in enumerate(taus):
            if tau > limit:
                curves[:, column] = 0.0
        record = {"kind": kind, "stages": chosen, "validation_brier": scores}
    out = [tuple(float(min(1.0, max(0.0, v))) for v in row) for row in curves]
    return out, record


def pressure_qrf_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """A quantile regression forest of the spread, read as an exceedance curve (#385).

    Meinshausen's forest on the direct design and pairs of #114: each served
    row's conditional distribution is the training spreads weighted by how often
    they share its leaves, `PRESSURE_QRF_SETTINGS`. The leaf size is chosen on
    the pressure-day labels (`PRESSURE_DISTRIBUTION_SELECTION`). The curve is
    non-increasing in tau by construction and by the running minimum.
    """

    return _direct_pressure_predictor("qrf", features, declaration, minimum_history)


def pressure_natural_gradient_exceedance(
    features: Sequence[str],
    declaration: Any,
    minimum_history: int = 20,
    family: str = "laplace",
) -> ExceedancePredictor:
    """Natural-gradient boosting of a normal or Laplace law of the spread (#385).

    Trees boosted on the natural gradient of the negative log-likelihood in the
    law's location and log-scale (Duan et al., NGBoost, in numpy and
    scikit-learn), `PRESSURE_NATURAL_GRADIENT_SETTINGS`, on the same design and
    pairs. The stage count is chosen on the pressure-day labels.

    Raises:
        ValueError: on a family other than the two declared, as on the other
            direct models for a short frame or a call without the as-of rule.
    """

    if family not in PRESSURE_NATURAL_GRADIENT_SETTINGS["families"]:
        raise ValueError(
            f"family must be one of {list(PRESSURE_NATURAL_GRADIENT_SETTINGS['families'])}, got {family!r}"
        )
    return _direct_pressure_predictor(f"ng_{family}", features, declaration, minimum_history)


# --------------------------------------------------------------------------
# The scarcity-conditioned calendar (#128)
# --------------------------------------------------------------------------
#
# The scheduled-pressure terms enter *through* the reserve-scarcity state
# (#115), never alongside it, so the calm years teach that a quarter-end with
# abundant reserves is no pressure. Declared in `repo_model.scarcity_calendar`
# before scoring; the two forms are the direct logistic and the direct
# gradient-boosted classifier of #114 on this one design, the classifier
# constrained non-decreasing in the state.


class _ScarcityCalendarDesign:
    """The scarcity-conditioned calendar's design (#128).

    * `spread_bps`, required: the latest spread public at the decision.
    * `reserve_scarcity_state`, required: #115's state as read as-of, mapped
      through `state_levels` (`scarcity_calendar.STATE_FORMS`). A level off
      the mapping is refused, never guessed.
    * Each other declared column that is not a calendar or settlement column,
      linearly, as read (the scarcity measures).
    * Each scheduled-pressure term times the mapped state, and never alone: the
      scored day's pressure-day type (quarter-end, month-end, tax date, from
      the three calendar columns, all required, through the split declaration),
      and `treasury_settlement` when declared, in USD billions.

    With `monotone`, `monotone` is the classifier's constraint per column:
    non-decreasing (+1) in the state and in each term times the state, free (0)
    elsewhere. Every scheduled term and the state are non-negative, so the
    probability never falls as the state rises with the calendar fixed.
    """

    tga = False
    scarcity = False
    products: Tuple[Tuple[str, str], ...] = ()

    def __init__(
        self,
        features: Sequence[str],
        declaration: Any,
        state_levels: Mapping[float, float],
        *,
        monotone: bool = False,
        interactions: bool = False,
        regime_pooled: bool = False,
        regime_hierarchical: bool = False,
        balance_sheet: bool = False,
    ) -> None:
        from .scarcity import RESERVE_SCARCITY_STATE, STATE_LABELS

        if sum((interactions, regime_pooled, regime_hierarchical)) > 1:
            raise ValueError(
                "the interaction, regime-pooled and hierarchical variants are separate candidates"
            )
        regime_pooled = regime_pooled or regime_hierarchical
        if regime_pooled and monotone:
            raise ValueError("partial pooling is the logistic's; the classifier's constraint does not apply to it")
        declared = tuple(dict.fromkeys(str(name) for name in features))
        for required in ("spread_bps", RESERVE_SCARCITY_STATE) + _CALENDAR_INPUTS:
            if required not in declared:
                raise ValueError(
                    f"the scarcity-conditioned calendar reads {required!r}; declare it "
                    f"(the spread, the state and {list(_CALENDAR_INPUTS)} are all required)"
                )
        if not hasattr(declaration, "day_type"):
            raise ValueError("the pressure-day type needs the split declaration that defines it")
        levels = {float(key): float(value) for key, value in state_levels.items()}
        if set(levels) != {float(level) for level in STATE_LABELS}:
            raise ValueError(
                f"a state form maps every level of the state, {sorted(STATE_LABELS)}; got "
                f"{sorted(levels)}"
            )
        if any(value < 0.0 for value in levels.values()):
            raise ValueError(f"a mapped state is non-negative, got {levels}")
        self.declaration = declaration
        self.features = declared
        self.state_column = RESERVE_SCARCITY_STATE
        self.state_levels = levels
        self.settlement = "treasury_settlement" in declared
        self.linear = tuple(
            name
            for name in declared
            if name not in ("spread_bps", RESERVE_SCARCITY_STATE, "treasury_settlement")
            and name not in _CALENDAR_INPUTS
            and name not in SPREAD_COMPONENTS
        )
        scheduled = list(_PRESSURE_DAY_TYPES) + (["treasury_settlement"] if self.settlement else [])
        names = ["spread_bps", RESERVE_SCARCITY_STATE, *self.linear] + [f"{name}_x_state" for name in scheduled]
        # The interaction variant (#378): the settlement's size times the state
        # times the tax date or the quarter-end (the September 2019 pattern).
        # It needs the settlement, which is public only at horizon 1, so
        # without it the variant adds nothing and is the base form.
        self.interaction_types: Tuple[str, ...] = (
            _INTERACTION_DAY_TYPES if interactions and self.settlement else ()
        )
        names += [f"treasury_settlement_x_state_x_{kind}" for kind in self.interaction_types]
        # Balance-sheet days (#427): the three calendar rules of
        # `balance_sheet_days`, each times the state, and the FR 2004 net
        # Treasury position (already a linear column) times the state, times
        # the state on a balance-sheet day, and times the state and the
        # scheduled settlement.
        self.balance_sheet = balance_sheet
        self.position_terms: Tuple[str, ...] = ()
        if balance_sheet:
            if _DEALER_POSITION not in declared:
                raise ValueError(
                    f"the balance-sheet design reads {_DEALER_POSITION!r}; declare it (the FR 2004 net Treasury position)"
                )
            from . import balance_sheet_days

            names += [f"{rule}_x_state" for rule in balance_sheet_days.NAMES]
            self.position_terms = ("dealer_position_x_state", "dealer_position_x_balance_sheet_day_x_state") + (
                ("dealer_position_x_settlement_x_state",) if self.settlement else ()
            )
            names += list(self.position_terms)
        # The regime-pooled variant (#378): the scheduled terms and the spread
        # get a deviation per scarcity regime, shrunk toward the pooled fit.
        self.pooling: Optional[Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[float, ...], Optional[float]]] = None
        if regime_pooled:
            pooled_columns = tuple(range(len(names)))
            raw = list(_PRESSURE_DAY_TYPES) + (["treasury_settlement"] if self.settlement else [])
            names += raw
            deviation_columns = (0,) + tuple(range(len(pooled_columns), len(names)))
            # The hierarchical variant (#386) has no fixed scale: each fit
            # estimates it by empirical Bayes (`None`).
            self.pooling = (
                pooled_columns,
                deviation_columns,
                tuple(sorted(set(self.state_levels.values()))),
                None if regime_hierarchical else REGIME_POOLING_SCALE,
            )
        self.names = tuple(names)
        self.monotone: Optional[Tuple[int, ...]] = (
            tuple(
                [0, 1] + [0] * len(self.linear) + [1] * len(scheduled) + [1] * len(self.interaction_types)
                + ([1] * 3 + [0] * len(self.position_terms) if balance_sheet else [])
            )
            if monotone
            else None
        )

    def needs_history(self) -> bool:
        return False

    def settings(self) -> dict:
        return {
            "directive": "#128",
            "state_column": self.state_column,
            "state_levels": {f"{key:g}": value for key, value in sorted(self.state_levels.items())},
            "scheduled_terms": "each times the mapped state only, no main effect",
            "interaction_terms": [f"treasury_settlement x state x {kind}" for kind in self.interaction_types],
            "balance_sheet": (
                None
                if not self.balance_sheet
                else {
                    "rules": {
                        rule.name: {"description": rule.description, "public_from": rule.public_from.isoformat(),
                                    "sources": list(rule.sources)}
                        for rule in _balance_sheet_rules()
                    },
                    "position_terms": list(self.position_terms),
                    "scored_day": "recovered from the row's calendar columns (balance_sheet_days.scored_day)",
                }
            ),
            "regime_partial_pooling": (
                None
                if self.pooling is None
                else {
                    "regimes": list(self.pooling[2]),
                    "deviation_scale": "empirical Bayes" if self.pooling[3] is None else self.pooling[3],
                    "grid": list(REGIME_SHRINKAGE_GRID) if self.pooling[3] is None else None,
                }
            ),
        }

    def _value(self, row: DailyObservation, column: str) -> float:
        # A derived feature (`contract.DERIVED_FEATURES`, such as #98's EFFR -
        # IORB) is a property of the row over its constituents, not a value.
        if column in DERIVED_FEATURES:
            value = getattr(row, column)
        else:
            value = row.values.get(column)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"{row.date}: the as-of read of {column!r} is missing; a direct "
                f"pressure model is not fitted on an unobserved input"
            )
        return float(value)

    def row(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        """One design row from an as-of observation (`tga_change` is unused)."""

        level = self._value(observation, self.state_column)
        if level not in self.state_levels:
            raise ValueError(
                f"{observation.date}: the state read {level!r}, which the state form "
                f"does not map ({sorted(self.state_levels)})"
            )
        state = self.state_levels[level]
        values = [float(observation.spread_bps), state]
        values += [self._value(observation, name) for name in self.linear]
        kind = self.declaration.day_type(observation.values)
        scheduled = [1.0 if kind == name else 0.0 for name in _PRESSURE_DAY_TYPES]
        if self.settlement:
            scheduled.append(self._value(observation, "treasury_settlement"))
        values += [term * state for term in scheduled]
        if self.interaction_types:
            size = self._value(observation, "treasury_settlement")
            values += [size * state * (1.0 if kind == name else 0.0) for name in self.interaction_types]
        if self.balance_sheet:
            from . import balance_sheet_days

            day = balance_sheet_days.scored_day(observation.date, observation.values)
            flagged = balance_sheet_days.flags(day, observation.date)
            values += [flagged[name] * state for name in balance_sheet_days.NAMES]
            position = self._value(observation, _DEALER_POSITION)
            any_day = 1.0 if any(flagged.values()) else 0.0
            values += [position * state, position * any_day * state]
            if self.settlement:
                values.append(position * self._value(observation, "treasury_settlement") * state)
        if self.pooling is not None:
            values += scheduled[:len(_PRESSURE_DAY_TYPES)]
            if self.settlement:
                values.append(self._value(observation, "treasury_settlement"))
        return values


#: The two forms of the scarcity-conditioned calendar, by the estimator each names.
SCARCITY_CALENDAR_KINDS = MappingProxyType({"logistic": "logistic", "gbm": "gbm_classifier"})


def _scarcity_calendar_predictor(
    form: str,
    features: Sequence[str],
    declaration: Any,
    state_levels: Mapping[float, float],
    minimum_history: int = 20,
    *,
    interactions: bool = False,
    regime_pooled: bool = False,
    regime_hierarchical: bool = False,
    balance_sheet: bool = False,
) -> Any:
    """The scarcity-conditioned calendar (#128), as a direct pressure model.

    `form` is `"logistic"`, the direct logistic of #114 on
    `_ScarcityCalendarDesign`, or `"gbm"`, the direct gradient-boosted
    classifier of #114 on the same design, constrained non-decreasing in the
    state and in each scheduled term times the state. Pairs, horizons and the
    as-of rule are `pressure_logistic_exceedance`'s.

    A study candidate, not a declared model: no public factory takes it and no
    `--model` name reaches it, as with the pooled history of #129
    (`_direct_pressure_predictor(history=...)`). The state it reads is off in
    every published declaration; adopting it is Eleonora's, and an adoption
    would give it a public factory, a conformance case and a `--model` name.

    Two variants (#378, `repo_model.scarcity_event_bar`): `interactions` adds
    the settlement's size x state x quarter-end and x tax date; `regime_pooled`
    (the logistic only) gives the spread and each scheduled term a deviation per
    scarcity regime, partially pooled toward the pooled fit. A third (#386),
    `regime_hierarchical`, is the same design with the pooling strength estimated
    in each fit by empirical Bayes (`_empirical_bayes_scale`) instead of declared.
    """

    if form not in SCARCITY_CALENDAR_KINDS:
        raise ValueError(f"a scarcity-calendar form is one of {sorted(SCARCITY_CALENDAR_KINDS)}, got {form!r}")
    design = _ScarcityCalendarDesign(
        features, declaration, state_levels, monotone=form == "gbm",
        interactions=interactions, regime_pooled=regime_pooled, regime_hierarchical=regime_hierarchical,
        balance_sheet=balance_sheet,
    )
    return _direct_pressure_predictor(
        SCARCITY_CALENDAR_KINDS[form], features, declaration, minimum_history, design=design
    )


# --------------------------------------------------------------------------
# Dynamic pressure logit, its ordinal version, and the stacked combiner (#137)
# --------------------------------------------------------------------------
#
# The persistence-logistic built out into a dynamic model rather than given
# more capacity (Kauppi & Saikkonen 2008; Beutel, List & von Schweinitz 2019).
# Every term is declared here, before any scoring:
#
# * `_PressureDesign`'s design on the declared features: the latest public
#   spread, the scarcity state, the scored day's pressure-day type, the
#   scheduled settlement, and each scheduled-pressure term times the scarcity
#   state;
# * the lagged event indicator, `1(spread > tau)` at the last as-of read of the
#   spread (in the ordinal model, one per cut);
# * the model's own lagged linear index (`_index_chain`).
#
# Each model is direct: fitted per horizon on labels paired with what their own
# decision instant read, with the scored day's calendar terms, which are known
# in advance. Nothing is iterated.


#: The dynamic logit, declared before scoring. `persistence_grid` is the set of
#: values the lagged index's coefficient is profiled over at each fit; 0 is the
#: static logit. The penalty and standardization are the direct logistic's
#: (#114), on every column but the intercept.
DYNAMIC_LOGIT_SETTINGS = MappingProxyType(
    {
        "estimator": "dynamic_logit",
        "lagged_index": (
            "Kauppi-Saikkonen: index_t = x_t'b + alpha * index_a(t), a(t) the label's "
            "last as-of read (the anchor of t's decision); a chain with no index at "
            "its anchor starts at its stationary value x_t'b / (1 - alpha)"
        ),
        "persistence_grid": (0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95),
        "persistence_choice": "the grid value with the highest penalized likelihood on the training pairs",
        "C": 1.0,
        "penalty": "l2",
        "standardized": True,
    }
)

#: The ordinal version: a cumulative (proportional-odds) logit of the category
#: the spread falls in between the requested thresholds, so the exceedance
#: probabilities share one index and are ordered by construction.
DYNAMIC_ORDINAL_SETTINGS = MappingProxyType(
    {
        **DYNAMIC_LOGIT_SETTINGS,
        "estimator": "dynamic_ordinal_logit",
        "link": "cumulative logit, proportional odds; P(spread > tau_k) = sigmoid(index - theta_k)",
        "thresholds": "theta_1 free, theta_k = theta_(k-1) + exp(delta_k), so ordered by construction",
    }
)

#: The stacked combiner, declared before scoring.
STACKED_COMBINER = MappingProxyType(
    {
        "method": "stacked_logistic_out_of_fold",
        "description": (
            "a logistic of the outcome on logit(p) of each base forecast, fitted per "
            "threshold at each refit block on the bases' out-of-fold forecasts of earlier "
            "scored days at or before the block's last training label, then applied to "
            "the block's forecasts; before minimum_pairs pairs with minimum_events "
            "events, sigmoid of the bases' mean logit"
        ),
        "minimum_pairs": 250,
        "minimum_events": 5,
        "probability_floor": 1e-6,
        "C": 1.0,
        "penalty": "l2",
        "standardized": True,
    }
)

_NEWTON_ITERATIONS = 100
_BFGS_ITERATIONS = 2000


class _Logit(NamedTuple):
    """A fitted penalized logit on standardized columns."""

    centre: Any
    scale: Any
    coefficients: Any
    objective: float

    def probability(self, x: Any) -> Any:
        import numpy

        z = (numpy.asarray(x, dtype=float) - self.centre) / self.scale
        return _expit(self.coefficients[0] + z @ self.coefficients[1:])


def _expit(value: Any) -> Any:
    import numpy

    value = numpy.asarray(value, dtype=float)
    out = numpy.empty_like(value)
    positive = value >= 0
    out[positive] = 1.0 / (1.0 + numpy.exp(-value[positive]))
    e = numpy.exp(value[~positive])
    out[~positive] = e / (1.0 + e)
    return out


def _standardizer(x: Any) -> Tuple[Any, Any]:
    centre = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0.0] = 1.0
    return centre, scale


def _fit_logit(x: Any, y: Any, c: float = 1.0) -> _Logit:
    """Penalized logistic regression by Newton's method, numpy only.

    Columns standardized on `x`; the loss is the summed negative
    log-likelihood plus `|b|^2 / (2c)` on every coefficient but the intercept
    (scikit-learn's `C`). Deterministic.
    """

    import numpy

    x = numpy.asarray(x, dtype=float)
    y = numpy.asarray(y, dtype=float)
    centre, scale = _standardizer(x)
    z = numpy.hstack([numpy.ones((len(x), 1)), (x - centre) / scale])
    penalty = numpy.full(z.shape[1], 1.0 / c)
    penalty[0] = 0.0
    rate = min(max(y.mean(), 1e-6), 1 - 1e-6)
    w = numpy.zeros(z.shape[1])
    w[0] = math.log(rate / (1 - rate))

    def objective(weights: Any) -> float:
        eta = z @ weights
        return float(numpy.sum(numpy.logaddexp(0.0, eta) - y * eta) + 0.5 * numpy.sum(penalty * weights**2))

    current = objective(w)
    for _ in range(_NEWTON_ITERATIONS):
        p = _expit(z @ w)
        gradient = z.T @ (p - y) + penalty * w
        hessian = (z * (p * (1 - p))[:, None]).T @ z + numpy.diag(penalty) + 1e-10 * numpy.eye(len(w))
        step = numpy.linalg.solve(hessian, gradient)
        size = 1.0
        while True:
            candidate = w - size * step
            value = objective(candidate)
            if value <= current or size < 1e-8:
                break
            size /= 2.0
        if current - value < 1e-12 * max(1.0, abs(current)):
            w, current = (candidate, value) if value <= current else (w, current)
            break
        w, current = candidate, value
    return _Logit(centre, scale, w, current)


class _Ordinal(NamedTuple):
    """A fitted penalized cumulative logit on standardized columns."""

    centre: Any
    scale: Any
    thresholds: Any
    coefficients: Any
    objective: float

    def exceedance(self, x: Any) -> Any:
        """`P(category > k)` for each cut `k`, one row per row of `x`."""

        import numpy

        eta = ((numpy.asarray(x, dtype=float) - self.centre) / self.scale) @ self.coefficients
        return _expit(eta[:, None] - self.thresholds[None, :])


def _thresholds(parameters: Any, cuts: int) -> Any:
    import numpy

    return parameters[0] + numpy.concatenate([[0.0], numpy.cumsum(numpy.exp(parameters[1:cuts]))])


def _fit_ordinal(x: Any, categories: Any, cuts: int, c: float = 1.0) -> _Ordinal:
    """Penalized proportional-odds logit by BFGS, numpy only.

    `categories[i]` is how many of the `cuts` ordered thresholds row `i`
    exceeds, 0 to `cuts`. `P(category > k) = sigmoid(x'b - theta_k)`, with
    `theta_k = theta_1 + sum exp(delta)`: ordered whatever the data, so the
    exceedance probabilities are coherent by construction. The penalty is
    `|b|^2 / (2c)` on standardized columns; the thresholds are unpenalized.
    """

    import numpy

    x = numpy.asarray(x, dtype=float)
    k = numpy.asarray(categories, dtype=int)
    centre, scale = _standardizer(x)
    z = (x - centre) / scale
    count = len(k)
    rows = numpy.arange(count)
    rates = numpy.array([(k > j).mean() for j in range(cuts)])
    rates = numpy.clip(rates, 1e-6, 1 - 1e-6)
    start = -numpy.log(rates / (1 - rates))
    start = numpy.maximum.accumulate(start + 1e-3 * numpy.arange(cuts))
    gaps = numpy.diff(start)
    initial = numpy.concatenate(
        [[start[0]], numpy.log(numpy.maximum(gaps, 1e-3)), numpy.zeros(z.shape[1])]
    )

    def objective_and_gradient(parameters: Any) -> Tuple[float, Any]:
        theta = _thresholds(parameters, cuts)
        beta = parameters[cuts:]
        eta = z @ beta
        u = _expit(eta[:, None] - theta[None, :])
        padded = numpy.hstack([numpy.ones((count, 1)), u, numpy.zeros((count, 1))])
        upper = padded[rows, k]
        lower = padded[rows, k + 1]
        # The edge categories directly, so a small probability keeps its digits.
        probability = numpy.where(
            k == 0,
            _expit(theta[0] - eta),
            numpy.where(k == cuts, upper, upper - lower),
        )
        probability = numpy.maximum(probability, 1e-300)
        v = padded * (1 - padded)
        v_upper = v[rows, k]
        v_lower = v[rows, k + 1]
        value = float(-numpy.sum(numpy.log(probability)) + 0.5 * numpy.sum(beta**2) / c)
        d_eta = (v_upper - v_lower) / probability
        d_theta = numpy.zeros((count, cuts + 2))
        d_theta[rows, k] -= v_upper / probability
        d_theta[rows, k + 1] += v_lower / probability
        d_theta = d_theta[:, 1 : cuts + 1].sum(axis=0)
        gradient = numpy.empty_like(parameters)
        # theta_j = p_0 + sum_{i <= j} exp(p_i): d/dp_0 sums all, d/dp_i sums j >= i.
        tail = numpy.cumsum(d_theta[::-1])[::-1]
        gradient[0] = -tail[0]
        gradient[1:cuts] = -tail[1:] * numpy.exp(parameters[1:cuts])
        gradient[cuts:] = -(z.T @ d_eta) + beta / c
        return value, gradient

    parameters, value = _bfgs(objective_and_gradient, initial)
    return _Ordinal(centre, scale, _thresholds(parameters, cuts), parameters[cuts:], value)


def _bfgs(objective_and_gradient: Any, initial: Any) -> Tuple[Any, float]:
    """Minimize by BFGS with a backtracking (Armijo) line search. Deterministic."""

    import numpy

    x = numpy.asarray(initial, dtype=float)
    value, gradient = objective_and_gradient(x)
    inverse = numpy.eye(len(x))
    for _ in range(_BFGS_ITERATIONS):
        if numpy.max(numpy.abs(gradient)) < 1e-7 * max(1.0, abs(value)):
            break
        direction = -inverse @ gradient
        slope = float(gradient @ direction)
        if slope >= 0:
            inverse = numpy.eye(len(x))
            direction = -gradient
            slope = float(gradient @ direction)
        size = 1.0
        while True:
            candidate = x + size * direction
            new_value, new_gradient = objective_and_gradient(candidate)
            if numpy.isfinite(new_value) and new_value <= value + 1e-4 * size * slope:
                break
            size /= 2.0
            if size < 1e-12:
                return x, value
        s = candidate - x
        y = new_gradient - gradient
        sy = float(s @ y)
        if sy > 1e-12:
            rho = 1.0 / sy
            identity = numpy.eye(len(x))
            inverse = (identity - rho * numpy.outer(s, y)) @ inverse @ (
                identity - rho * numpy.outer(y, s)
            ) + rho * numpy.outer(s, s)
        improvement = value - new_value
        x, value, gradient = candidate, new_value, new_gradient
        if improvement < 1e-12 * max(1.0, abs(value)):
            break
    return x, value


def _index_chain(xs: Sequence[Optional[Sequence[float]]], anchors: Sequence[int], alpha: float) -> List[Any]:
    """The lagged-index regressors: `chain_t = x_t + alpha * chain_anchor(t)`.

    The dynamic index is `b'chain_t`, and with it `index_t = b'x_t + alpha *
    index_anchor(t)`, Kauppi and Saikkonen's recursion with the lag at the
    label's last as-of read. A row with no complete design has no index; a row
    whose anchor has none starts the chain at its stationary value,
    `x_t / (1 - alpha)`. Every anchor is an earlier row, so one forward pass.
    """

    import numpy

    out: List[Any] = []
    for position, x in enumerate(xs):
        if x is None:
            out.append(None)
            continue
        row = numpy.asarray(x, dtype=float)
        anchor = anchors[position]
        if anchor >= position:  # pragma: no cover - an anchor is always earlier
            raise LookAheadError(f"row {position}'s anchor {anchor} is not before it")
        previous = out[anchor] if anchor >= 0 else None
        out.append(row / (1.0 - alpha) if previous is None else row + alpha * previous)
    return out


def _dynamic_rows(
    design: _PressureDesign,
    information: InformationRule,
    rows: Sequence[DailyObservation],
    cache: dict,
) -> Tuple[List[Optional[List[float]]], List[int]]:
    """Each row's design under the as-of rule, and the row of its anchor.

    Row `t`'s design is what a forecast of `t` read at its own decision instant
    (`information.information_set`), checked by both guards; its anchor is the
    latest row whose label was public then. `None` and -1 where there is no
    read or an input is missing. Cached by date: a row's reads are public by
    its own decision, so every later as-of frame carries them unmasked.
    """

    dates = [row.date for row in rows]
    where = {when: position for position, when in enumerate(dates)}
    key_base = ("dynamic", information.horizon, information.features)
    xs: List[Optional[List[float]]] = []
    anchors: List[int] = []
    for target in range(len(rows)):
        key = (key_base, dates[target])
        if key not in cache:
            cache[key] = None
            try:
                info = information.information_set(dates, target)
            except SplitError:
                pass
            else:
                information.check(dates, info)
                try:
                    features = design.row(information.observation(rows, info), None)
                except ValueError:
                    features = None
                cache[key] = (features, dates[info.anchor])
        entry = cache[key]
        if entry is None:
            xs.append(None)
            anchors.append(-1)
        else:
            xs.append(entry[0])
            anchors.append(where[entry[1]])
    return xs, anchors


def _with_indicators(
    xs: Sequence[Optional[Sequence[float]]], cuts: Sequence[float]
) -> List[Optional[List[float]]]:
    """Each design row with `1(lagged spread > cut)` appended per cut."""

    return [
        None if x is None else [*x, *(1.0 if exceeds_bp(x[0], cut) else 0.0 for cut in cuts)]
        for x in xs
    ]


def _dynamic_predictor(
    kind: str, features: Sequence[str], declaration: Any, minimum_history: int
) -> Any:
    """The fit-and-predict behind both dynamic models; `kind` picks the link."""

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    design = _PressureDesign(features, declaration)
    if design.tga:
        raise ValueError(
            "the dynamic pressure models do not read the TGA change; declare the "
            "terms #137 names"
        )
    cache: dict = {}
    settings_base = DYNAMIC_LOGIT_SETTINGS if kind == "logit" else DYNAMIC_ORDINAL_SETTINGS
    grid = settings_base["persistence_grid"]

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        import numpy

        if information is None:
            raise ValueError(
                "a dynamic pressure model pairs each training label with what was "
                "public at that label's own decision instant, which only the as-of "
                "rule can say; it was called without one"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a dynamic pressure model needs at least {minimum_history} training "
                f"rows, got {len(train_rows)}"
            )
        if histories is None or len(histories) != len(feature_rows):
            raise ValueError(
                "the lagged index is read off each forecast's own as-of history; one "
                "history per feature row is required"
            )
        taus = tuple(float(tau) for tau in taus)
        if kind == "ordinal" and any(b <= a for a, b in zip(taus, taus[1:])):
            raise ValueError(
                f"the ordinal model's categories are cut at strictly ascending taus, got {taus}"
            )
        # Every history and the training frame are prefixes of one panel: the
        # chain is computed once, on the longest, and read at each history's end.
        longest = max([train_rows, *histories], key=len)
        for frame in (train_rows, *histories):
            if frame and (len(frame) > len(longest) or frame[-1].date != longest[len(frame) - 1].date):
                raise ValueError("the as-of histories are not prefixes of one panel")
        base, anchors = _dynamic_rows(design, information, longest, cache)
        served_base = [design.row(row, None) for row in feature_rows]
        served_lag = [len(history) - 1 for history in histories]
        spreads = [float(row.spread_bps) for row in train_rows]
        trainable = [t for t in range(len(train_rows)) if base[t] is not None]
        if not trainable:
            raise ValueError("no training label has a complete as-of read")
        labels_at = {
            tau: [1 if exceeds_bp(spreads[t], tau) else 0 for t in trainable] for tau in taus
        }

        def chained(cuts: Sequence[float], alpha: float) -> Tuple[Any, Any]:
            chain = _index_chain(_with_indicators(base, cuts), anchors, alpha)
            train_x = numpy.asarray([chain[t] for t in trainable], dtype=float)
            served = []
            for x, lag in zip(_with_indicators(served_base, cuts), served_lag):
                previous = chain[lag] if lag >= 0 else None
                row = numpy.asarray(x, dtype=float)
                served.append(row / (1.0 - alpha) if previous is None else row + alpha * previous)
            return train_x, numpy.asarray(served, dtype=float)

        chosen: dict = {}
        columns: List[Any] = []
        if kind == "logit":
            fitted: dict = {}
            for tau in taus:
                labels = labels_at[tau]
                if len(set(labels)) < 2:
                    columns.append(numpy.full(len(feature_rows), float(labels[0])))
                    continue
                key = (tuple(labels), tau)
                if key not in fitted:
                    best = None
                    for alpha in grid:
                        train_x, served_x = chained((tau,), alpha)
                        fit = _fit_logit(train_x, labels, settings_base["C"])
                        if best is None or fit.objective < best[0].objective - 1e-9:
                            best = (fit, served_x, alpha)
                    fitted[key] = (best[0].probability(best[1]), best[2])
                columns.append(fitted[key][0])
                chosen[f"{tau:g}"] = fitted[key][1]
        else:
            # Cuts whose training labels are all one value get that value; the
            # rest, grouped by identical label vectors, are the ordinal's cuts.
            groups: List[List[float]] = []
            for tau in taus:
                labels = labels_at[tau]
                if len(set(labels)) < 2:
                    continue
                if groups and labels_at[groups[-1][0]] == labels:
                    groups[-1].append(tau)
                else:
                    groups.append([tau])
            exceed: dict = {}
            if groups:
                cuts = [group[0] for group in groups]
                categories = numpy.zeros(len(trainable), dtype=int)
                for cut in cuts:
                    categories += numpy.asarray(labels_at[cut])
                best = None
                for alpha in grid:
                    train_x, served_x = chained(cuts, alpha)
                    fit = _fit_ordinal(train_x, categories, len(cuts), settings_base["C"])
                    if best is None or fit.objective < best[0].objective - 1e-9:
                        best = (fit, served_x, alpha)
                probabilities = best[0].exceedance(best[1])
                for position, group in enumerate(groups):
                    for tau in group:
                        exceed[tau] = probabilities[:, position]
                chosen["ordinal"] = best[2]
                chosen["cuts"] = tuple(cuts)
            for tau in taus:
                if tau in exceed:
                    columns.append(exceed[tau])
                else:
                    columns.append(numpy.full(len(feature_rows), float(labels_at[tau][0])))
        curves = []
        for day in range(len(feature_rows)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, float(column[day])))
                # The binary fits are per tau, so made non-increasing; the
                # ordinal's curve is ordered by construction and left as fitted.
                curve.append(value if not curve or kind == "ordinal" else min(curve[-1], value))
            curves.append(tuple(curve))
        settings = dict(settings_base)
        settings["persistence_grid"] = list(grid)
        indicator_names = ["lagged_event"] if kind == "logit" else [
            f"lagged_event_{cut:g}" for cut in chosen.get("cuts", ())
        ]
        settings["design"] = list(design.names) + indicator_names
        if kind == "logit":
            settings["persistence"] = next(iter(chosen.values()), 0.0)
            settings["persistence_by_tau"] = chosen
        else:
            settings["persistence"] = chosen.get("ordinal", 0.0)
        if design.scarcity:
            settings["scarcity_state"] = SCARCITY_STATE
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=tuple(history[-1].date if history else None for history in histories),
        )

    return fit_predict


def dynamic_logit_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """A dynamic logit of the pressure label (#137).

    At each threshold, a penalized logit of `spread > tau` on
    `_PressureDesign`'s design, the lagged event indicator `1(latest public
    spread > tau)` and the model's own lagged linear index (`_index_chain`,
    Kauppi-Saikkonen), with the index's persistence profiled over
    `DYNAMIC_LOGIT_SETTINGS["persistence_grid"]`. Direct: fitted on labels
    paired with what their own decision instant read, at the run's horizon.
    The served index is chained through each forecast's own as-of history,
    whose end the fold loop checks is the forecast's anchor (`history_ends`).
    The curve is made non-increasing in tau by a running minimum.

    Raises:
        ValueError: on a design the features cannot support, a short frame, a
            call without the as-of rule or without the histories.
    """

    return _dynamic_predictor("logit", features, declaration, minimum_history)


def dynamic_ordinal_exceedance(
    features: Sequence[str], declaration: Any, minimum_history: int = 20
) -> ExceedancePredictor:
    """The dynamic logit as one ordinal model across the thresholds (#137).

    A proportional-odds logit of the category the spread falls in between the
    requested (strictly ascending) thresholds, on the same design, one lagged
    event indicator per cut, and the lagged index. `P(spread > tau_k) =
    sigmoid(index - theta_k)` with ordered `theta`, so `P(> +10) <= P(> +5)` on
    every day by construction (`DYNAMIC_ORDINAL_SETTINGS`).
    """

    return _dynamic_predictor("ordinal", features, declaration, minimum_history)


def _check_out_of_fold(bases: Mapping[str, Any], pairs: Sequence[int], fit_end: date) -> None:
    """Raise unless every pair is an out-of-fold base forecast with an observable outcome.

    `pairs` index the scored days a combiner fitted at `fit_end` (its block's
    last training label) learns from. Each day's outcome must be observable
    then (scored on or before `fit_end`), and each base's forecast of it must
    have been made by a fit trained only on labels before that day -- not a
    fitted value from a window that included it.

    Raises:
        LookAheadError: naming the base and the day.
    """

    for name, report in bases.items():
        for day in pairs:
            fold = report.folds[day]
            if fold.scored_date > fit_end:
                raise LookAheadError(
                    f"the combiner fitted at {fit_end} would learn from the outcome of "
                    f"{fold.scored_date}, not yet observable"
                )
            if fold.train_end >= fold.scored_date:
                raise LookAheadError(
                    f"base {name!r}'s forecast of {fold.scored_date} was made by a fit "
                    f"trained through {fold.train_end}, which includes the day it "
                    f"forecast; the combiner learns only from out-of-fold forecasts"
                )


def stacked_combiner(
    bases: Mapping[str, Any],
    *,
    minimum_pairs: int = STACKED_COMBINER["minimum_pairs"],
    minimum_events: int = STACKED_COMBINER["minimum_events"],
    model_name: str = "stacked_combiner",
) -> Any:
    """A logistic of the outcome on each base's logit(p), fitted out of fold (#137).

    `bases` are `ExceedanceBacktestReport`s on one grid: the same scored days,
    taus and outcomes. The combiner refits on the first base's refit blocks: a
    block is the run of its folds sharing a training frame, whose last label is
    `train_end`. At each block and
    threshold the combiner is fitted on the pairs of every earlier scored day
    at or before that date -- outcomes observable when the block was fitted --
    and every base forecast in those pairs must itself be out of fold
    (`_check_out_of_fold`). The block's forecasts are then mapped through it.
    The curve is made non-increasing in tau by a running minimum.

    Raises:
        ValueError: if the bases are not on one grid.
        LookAheadError: if a pair would use an in-sample base forecast or an
            outcome not observable at the combiner's fit.
    """

    import dataclasses
    import numpy

    names = list(bases)
    if len(names) < 2:
        raise ValueError("a stacked combiner needs at least two bases")
    first = bases[names[0]]
    for name in names[1:]:
        other = bases[name]
        if (
            other.scored_dates != first.scored_dates
            or tuple(other.taus) != tuple(first.taus)
            or other.outcomes != first.outcomes
        ):
            raise ValueError(f"base {name!r} is not on {names[0]!r}'s grid")
    floor = STACKED_COMBINER["probability_floor"]

    def logit(probability: float) -> float:
        p = min(1.0 - floor, max(floor, probability))
        return math.log(p / (1.0 - p))

    count = len(first.folds)
    x = numpy.asarray(
        [[[logit(bases[name].forecast[day][position]) for name in names]
          for position in range(len(first.taus))] for day in range(count)],
        dtype=float,
    ).reshape(count, len(first.taus), len(names))
    columns = [[0.0] * count for _ in first.taus]
    for position in range(len(first.taus)):
        outcomes = [first.outcomes[day][position] for day in range(count)]
        start = 0
        while start < count:
            end_label = first.folds[start].train_end
            stop = start
            while stop < count and first.folds[stop].train_end == end_label:
                stop += 1
            past = [day for day in range(start) if first.folds[day].scored_date <= end_label]
            events = sum(outcomes[day] for day in past)
            if len(past) >= minimum_pairs and minimum_events <= events < len(past):
                _check_out_of_fold(bases, past, end_label)
                fit = _fit_logit(
                    x[past, position, :], [outcomes[day] for day in past], STACKED_COMBINER["C"]
                )
                values = fit.probability(x[start:stop, position, :])
            else:
                values = _expit(x[start:stop, position, :].mean(axis=1))
            for offset, value in enumerate(values):
                columns[position][start + offset] = float(value)
            start = stop
    curves = []
    for day in range(count):
        curve: List[float] = []
        for position in range(len(first.taus)):
            value = columns[position][day]
            curve.append(value if not curve else min(curve[-1], value))
        curves.append(tuple(curve))
    settings = dict(STACKED_COMBINER)
    settings["minimum_pairs"] = minimum_pairs
    settings["minimum_events"] = minimum_events
    settings["bases"] = names
    return dataclasses.replace(
        first,
        forecast=tuple(curves),
        model_name=model_name,
        model_settings=MappingProxyType(settings),
    )


def paired_bootstrap_p_values(
    series: Sequence[Sequence[float]],
    *,
    block_length: float,
    seed: int,
    replications: int,
    chunk: int = 1000,
) -> List[Tuple[float, float]]:
    """One-sided stationary-bootstrap p-values for the mean of each paired series (#187).

    `series` are paired differences on one grid of scored days, each oriented
    so that a positive mean favours the candidate. All of them are resampled
    with the same draws, from `metrics.stationary_bootstrap_indices` driven by
    one `random.Random(seed)`, so the comparisons of one grid share their
    resamples as the days they score are shared. For a series with observed
    mean `m` and bootstrap means `m*`, centred under the null as `m* - m`:

    * improvement: `(1 + #{m* - m >= m}) / (replications + 1)`;
    * deterioration: `(1 + #{m* - m <= m}) / (replications + 1)`.

    The +1 keeps every p-value above zero; the smallest attainable is
    `1 / (replications + 1)`, so a Holm correction over a family of size K at
    level a needs `replications` above K / a. A resample is a count vector
    over the days, so its mean is a matrix product, computed `chunk`
    resamples at a time.

    Returns `[(p_improve, p_worse), ...]`, one per series.
    """

    import numpy

    from .metrics import stationary_bootstrap_indices

    if not series:
        return []
    lengths = {len(values) for values in series}
    if len(lengths) != 1:
        raise ValueError(f"the series are not on one grid: lengths {sorted(lengths)}")
    (n,) = lengths
    if n < 2:
        raise ValueError("a p-value needs at least two paired days")
    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 1:
        raise ValueError(f"replications must be a positive int, got {replications!r}")
    data = numpy.asarray(series, dtype=float).T  # days x series
    if not numpy.all(numpy.isfinite(data)):
        raise ValueError("a paired difference is not finite")
    mean = data.mean(axis=0)
    rng = random.Random(seed)
    up = numpy.zeros(data.shape[1], dtype=numpy.int64)
    down = numpy.zeros(data.shape[1], dtype=numpy.int64)
    tolerance = 1e-12
    done = 0
    while done < replications:
        size = min(chunk, replications - done)
        counts = numpy.zeros((size, n))
        for row in range(size):
            counts[row] = numpy.bincount(
                stationary_bootstrap_indices(n, block_length, rng), minlength=n
            )
        centred = counts @ data / n - mean
        up += (centred >= mean - tolerance).sum(axis=0)
        down += (centred <= mean + tolerance).sum(axis=0)
        done += size
    total = replications + 1
    return [(float((1 + u) / total), float((1 + d) / total)) for u, d in zip(up, down)]


# --------------------------------------------------------------------------
# Markov-switching regimes (#384; track M of #374)
# --------------------------------------------------------------------------
#
# A hidden Markov model of the spread (SOFR - IORB, bp) with two or three latent
# states -- calm, tight, stressed -- each Gaussian in the spread. The transition
# matrix is one of two, picked by a binary covariate: whether the reserve-scarcity
# state of #115 read as of the source day is tight or scarce (state 2 or 3). The
# model is fitted by EM on the training frame, then *forward-filtered* through each
# forecast's own as-of history: the filter never smooths, so no future row reaches
# a state probability. The probability of a pressure day `h` panel days ahead is
# the filtered state distribution carried `h` steps by the transition matrix of
# the latest known covariate, then the mixture's tail above the threshold.

#: What the fit is built with. Declared in `metadata/pressure_track_m.json`
#: before any scoring; a test pins the two together.
MARKOV_SWITCHING_SETTINGS = MappingProxyType(
    {
        "variance_floor_bp": 0.25,
        "transition_prior": 1.0,
        "max_iterations": 200,
        "tolerance": 1e-7,
        "tight_state_at_least": 2,
    }
)

#: The share of the sorted training spreads each initial state starts from, by
#: state count: most days calm, a tail stressed. Fixed, so the fit is deterministic.
_MARKOV_INITIAL_SHARES = MappingProxyType({2: (0.8, 0.2), 3: (0.6, 0.3, 0.1)})


class FittedMarkovSwitching(NamedTuple):
    """A fitted Gaussian hidden Markov model with covariate-dependent transitions."""

    means: Tuple[float, ...]
    sigmas: Tuple[float, ...]
    #: `transitions[z][i][j]`: from state i to j when the source day's covariate is z.
    transitions: Tuple[Tuple[Tuple[float, ...], ...], ...]
    initial: Tuple[float, ...]
    log_likelihood: float
    iterations: int


def _gaussian_density(y: Any, means: Any, sigmas: Any) -> Any:
    import numpy

    z = (y[:, None] - means[None, :]) / sigmas[None, :]
    density = numpy.exp(-0.5 * z * z) / (sigmas[None, :] * math.sqrt(2.0 * math.pi))
    # A missing spread informs no state.
    density[numpy.isnan(y), :] = 1.0
    return density


def _forward(density: Any, transitions: Any, covariates: Any, initial: Any) -> Tuple[Any, Any]:
    """Scaled forward pass: the filtered distribution at each row, and the scales."""

    import numpy

    length, states = density.shape
    alpha = numpy.empty((length, states))
    scales = numpy.empty(length)
    step = initial * density[0]
    for t in range(length):
        if t:
            step = (alpha[t - 1] @ transitions[covariates[t - 1]]) * density[t]
        total = step.sum()
        if not total > 0.0:
            # A spread no state can reach (the floor keeps this to a float underflow).
            total = 1e-300
            step = numpy.full(states, 1.0 / states) * total
        scales[t] = total
        alpha[t] = step / total
    return alpha, scales


def fit_markov_switching(
    spreads: Sequence[Optional[float]],
    covariates: Sequence[int],
    states: int = 3,
) -> FittedMarkovSwitching:
    """Baum-Welch on the training spreads, deterministic.

    Args:
        spreads: the spread in bp per training row, `None` where unobserved.
        covariates: 0 or 1 per row; the transition out of row t uses matrix
            `covariates[t]`.
        states: 2 or 3.

    Raises:
        ValueError: on a state count off the declared two, a covariate that is
            not 0 or 1, rows of unequal length, or too few observed spreads for
            the states.
    """

    import numpy

    if states not in _MARKOV_INITIAL_SHARES:
        raise ValueError(f"states must be one of {sorted(_MARKOV_INITIAL_SHARES)}, got {states!r}")
    if len(spreads) != len(covariates):
        raise ValueError("spreads and covariates must have one entry per row")
    if any(c not in (0, 1) for c in covariates):
        raise ValueError("a transition covariate is 0 or 1")
    y = numpy.array([numpy.nan if v is None else float(v) for v in spreads])
    z = numpy.asarray(covariates, dtype=int)
    observed = y[~numpy.isnan(y)]
    if len(observed) < 5 * states:
        raise ValueError(f"{len(observed)} observed spreads cannot fit {states} states")
    floor = float(MARKOV_SWITCHING_SETTINGS["variance_floor_bp"])
    prior = float(MARKOV_SWITCHING_SETTINGS["transition_prior"])

    ordered = numpy.sort(observed)
    edges = numpy.cumsum((0.0,) + _MARKOV_INITIAL_SHARES[states])
    means = numpy.empty(states)
    sigmas = numpy.empty(states)
    for k in range(states):
        lo, hi = int(edges[k] * len(ordered)), max(int(edges[k + 1] * len(ordered)), int(edges[k] * len(ordered)) + 2)
        part = ordered[lo:hi]
        means[k] = part.mean()
        sigmas[k] = max(part.std(), floor)
    stay = 0.9
    base = numpy.full((states, states), (1.0 - stay) / (states - 1))
    numpy.fill_diagonal(base, stay)
    transitions = numpy.stack([base, base])
    initial = numpy.full(states, 1.0 / states)

    previous = -math.inf
    iterations = 0
    log_likelihood = -math.inf
    for iterations in range(1, int(MARKOV_SWITCHING_SETTINGS["max_iterations"]) + 1):
        density = _gaussian_density(y, means, sigmas)
        alpha, scales = _forward(density, transitions, z, initial)
        log_likelihood = float(numpy.log(scales).sum())
        beta = numpy.ones_like(alpha)
        for t in range(len(y) - 2, -1, -1):
            beta[t] = transitions[z[t]] @ (density[t + 1] * beta[t + 1]) / scales[t + 1]
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True)
        counts = numpy.zeros((2, states, states))
        for t in range(len(y) - 1):
            xi = alpha[t][:, None] * transitions[z[t]] * (density[t + 1] * beta[t + 1])[None, :]
            counts[z[t]] += xi / xi.sum()
        counts += prior / states
        transitions = counts / counts.sum(axis=2, keepdims=True)
        initial = gamma[0] / gamma[0].sum()
        weight = gamma[~numpy.isnan(y)]
        values = y[~numpy.isnan(y)]
        mass = weight.sum(axis=0)
        means = (weight * values[:, None]).sum(axis=0) / mass
        variance = (weight * (values[:, None] - means[None, :]) ** 2).sum(axis=0) / mass
        sigmas = numpy.maximum(numpy.sqrt(variance), floor)
        if abs(log_likelihood - previous) < float(MARKOV_SWITCHING_SETTINGS["tolerance"]) * max(1.0, abs(log_likelihood)):
            break
        previous = log_likelihood
    order = numpy.argsort(means)
    return FittedMarkovSwitching(
        means=tuple(float(v) for v in means[order]),
        sigmas=tuple(float(v) for v in sigmas[order]),
        transitions=tuple(
            tuple(tuple(float(v) for v in row) for row in matrix[numpy.ix_(order, order)])
            for matrix in transitions
        ),
        initial=tuple(float(v) for v in initial[order]),
        log_likelihood=log_likelihood,
        iterations=iterations,
    )


def filter_markov_switching(
    fitted: FittedMarkovSwitching,
    spreads: Sequence[Optional[float]],
    covariates: Sequence[int],
) -> Tuple[float, ...]:
    """The filtered state distribution at the last row: forward pass only.

    Row t's distribution reads rows 0..t and nothing after it; there is no
    backward pass, so this is what a forecaster at row t could have computed.
    """

    import numpy

    if not len(spreads) or len(spreads) != len(covariates):
        raise ValueError("a filter needs one covariate per spread, and at least one row")
    y = numpy.array([numpy.nan if v is None else float(v) for v in spreads])
    density = _gaussian_density(y, numpy.array(fitted.means), numpy.array(fitted.sigmas))
    alpha, _ = _forward(
        density,
        numpy.array(fitted.transitions),
        numpy.asarray(covariates, dtype=int),
        numpy.array(fitted.initial),
    )
    return tuple(float(v) for v in alpha[-1])


def markov_switching_state_probabilities(
    fitted: FittedMarkovSwitching, filtered: Sequence[float], covariate: int, steps: int
) -> Tuple[float, ...]:
    """The state distribution `steps` rows after a filtered one, the covariate held."""

    import numpy

    if steps < 0:
        raise ValueError(f"steps must not be negative, got {steps}")
    matrix = numpy.linalg.matrix_power(numpy.array(fitted.transitions[covariate]), steps)
    return tuple(float(v) for v in numpy.asarray(filtered, dtype=float) @ matrix)


def markov_switching_exceedance_curve(
    fitted: FittedMarkovSwitching, distribution: Sequence[float], taus: Sequence[float]
) -> Tuple[float, ...]:
    """`P(spread > tau)` on whole basis points: the mixture's tail above `tau + 1/2`."""

    curve = []
    for tau in taus:
        total = 0.0
        for weight, mean, sigma in zip(distribution, fitted.means, fitted.sigmas):
            total += weight * 0.5 * math.erfc((float(tau) + 0.5 - mean) / (sigma * math.sqrt(2.0)))
        curve.append(min(1.0, max(0.0, total)))
    return tuple(curve)


def _tight_covariates(rows: Sequence[DailyObservation], column: Optional[str]) -> List[int]:
    """The transition covariate per row: 1 where the scarcity state read is tight or scarce.

    A row whose state is unread carries the last read forward (that value was
    public before it); before any read the covariate is 0.
    """

    if column is None:
        return [0] * len(rows)
    threshold = MARKOV_SWITCHING_SETTINGS["tight_state_at_least"]
    out: List[int] = []
    latest = 0
    for row in rows:
        value = row.values.get(column)
        if value is not None and math.isfinite(float(value)):
            latest = 1 if float(value) >= threshold else 0
        out.append(latest)
    return out


def markov_switching_exceedance(
    states: int = 3,
    minimum_history: int = 20,
    scarcity_column: Optional[str] = None,
) -> ExceedancePredictor:
    """Pressure probabilities from a Markov-switching spread model (#384).

    Fitted by EM on each refit block's training frame, filtered forward through
    each forecast's own as-of history, carried `information.horizon` rows ahead.
    With `scarcity_column` (`scarcity.RESERVE_SCARCITY_STATE`) the transition
    matrix depends on whether that state, as read, is tight or scarce.

    Raises:
        ValueError: on a short frame, a call without the as-of rule or without
            each row's history, or a state count off the declared two.
        LookAheadError: if a history runs past its forecast's anchor.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[InformationRule] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> ExceedanceCurves:
        if information is None or histories is None or len(histories) != len(feature_rows):
            raise ValueError(
                "a Markov-switching forecast is filtered through its own as-of history; "
                "it was called without the rule or without one history per feature row"
            )
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a Markov-switching model needs at least {minimum_history} training "
                f"rows, got {len(train_rows)}"
            )
        fitted = fit_markov_switching(
            [_observed_spread(row, "markov_switching") for row in train_rows],
            _tight_covariates(train_rows, scarcity_column),
            states=states,
        )
        curves = []
        for feature_row, history in zip(feature_rows, histories):
            if not history:
                raise ValueError("a forecast's as-of history is empty")
            if history[-1].date > feature_row.date:
                raise LookAheadError(
                    f"the filter for the forecast anchored {feature_row.date} was handed "
                    f"history through {history[-1].date}"
                )
            covariates = _tight_covariates(history, scarcity_column)
            filtered = filter_markov_switching(
                fitted, [_observed_spread(row, "markov_switching") for row in history], covariates
            )
            distribution = markov_switching_state_probabilities(
                fitted, filtered, covariates[-1], information.horizon
            )
            curves.append(markov_switching_exceedance_curve(fitted, distribution, taus))
        read = ("spread_bps",) + ((scarcity_column,) if scarcity_column else ())
        settings = dict(MARKOV_SWITCHING_SETTINGS, states=states)
        if scarcity_column:
            settings["scarcity_state"] = scarcity_column
        return ExceedanceCurves(
            tuple(curves),
            read,
            ml_libraries=_library_versions(),
            model_settings=MappingProxyType(settings),
            history_ends=tuple(history[-1].date for history in histories),
        )

    return fit_predict
