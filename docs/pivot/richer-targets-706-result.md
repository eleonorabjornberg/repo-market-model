# H9 step 2: the richer targets modelled with #634's model class (#706)

A measurement on development data for hypothesis **H9** (the secondary goal: richer targets carry more learnable signal), step 2 of `docs/research/hypotheses/H9.md`. It is not a record and **not a verdict**: development data never gives one
(`docs/decisions/scoring-protocol.md` §1, ruling of Eleonora on #639, 13 October 2026). Nothing is published: no target joins any published declaration, no published figure moves, nothing is written into `docs/runs/`. No day after
2025-12-31 is read (`docs/decisions/lockbox.md`; the script refuses a locked day). The regimes are the as-of scarcity state and the day type, both known at the decision instant (ruling on #515). Every choice is in
`metadata/richer_targets_706.json`, committed before any score; `scripts/richer_targets_706.py` refuses to read it unless it is committed and unchanged. The page rests on #634's five-level fix of the spread row, so it is resynced and re-scored
on main before review.

## The three targets (the rule of 13 October, applied to step 1's tables)

| step | target | overlap with SOFR − IORB (pooled, level) | onsets | pre-onset AUC, ample / scarce / mean | outcome |
|---|---|---|---|---|---|
| 1 | `bgcr_iorb_bps`, `tgcr_iorb_bps`, `sofr_p99_iorb_bps`, `on_rrp_bn` | +0.95, +0.95, +0.83, −0.81 | 26 | | dropped: magnitude 0.8 or more |
| 2 | `srf_take_up_bn` | +0.31 | 7 | | dropped: fewer than 15 onsets |
| 3 | `bgcr_dispersion_bps` | +0.03 | 26 | 0.653 / 0.406 / **0.529** | **chosen** (1) |
| 3 | `on_rrp_change_bn` | −0.10 | 26 | 0.543 / 0.464 / **0.504** | **chosen** (2) |
| 3 | `sofr_dispersion_bps` | +0.06 | 26 | 0.560 / 0.410 / **0.485** | **chosen** (3) |
| 3 | `tgcr_dispersion_bps` | −0.16 | 26 | 0.536 / 0.434 / 0.485 | fourth |
| 3 | `effr_iorb_bps` | +0.63 | 26 | 0.264 / 0.520 / 0.392 | fifth |

Two readings are marked as questions for Eleonora in the pull request, because they change what is modelled:

* **The AUC is taken as step 1 tabulated it** (above one half when the value reads high before onsets). The rule's words are "the pre-onset AUC". A target that reads *low* before onsets (EFFR − IORB at 0.39) ranks low. Ranked by distance from one half, the
  order would be EFFR − IORB, BGCR dispersion, TGCR dispersion, SOFR dispersion, ON RRP change, and the top three would differ by two targets. The declaration records both orders; the signed one is applied.
* **Third and fourth place are 0.0003 of AUC apart** (SOFR dispersion 0.4854, TGCR dispersion 0.4851). The tie-break (forecastability) never applies, since the AUCs are not equal. A ranking that close does not show one leads more than the other.

## The model

#634's candidate (b): `ml.fit_gradient_boosted_quantiles` on the protocol's 23 levels with the inputs of `spread_distribution_634.new_features`, walk-forward on the shared fold grid (minimum history 61, refit every 21 days), leads 1 to 5. Only the label changes.
`richer_targets.as_target` puts the target in the slot the model reads as SOFR − IORB, and `richer_targets.swap_target_fields` puts the target's own sources and release lag there too, so the as-of rule reads the label under the sources it comes from
(the ON RRP operation results, or the secured rate's percentiles), not SOFR's or IORB's. **Consequence:** the model's autoregressive input is the target's own as-of value; SOFR − IORB itself is not an input. The first panel day has no ON RRP change and is
dropped for that target. Each target is scored against its own B1 (the last public value plus the lead's own changes over two years) and B2 (a year of values on days of the target day's type), `richer_targets.b1_quantiles` and `b2_quantiles`, at every lead.

## Results (grid CRPS on the 23 levels, mean over leads 1 to 5 per decision day, 2018-07 to 2025-12-23)

| target | decision days | CRPS B1 | CRPS B2 | CRPS model | skill over B1 (lower 95%) | skill over B2 (lower 95%) | B1 over B2 |
|---|---|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | 1846 | 8.197 | 6.517 | 5.500 | +0.329 (lower +0.271) | +0.156 (lower +0.080) | -0.258 (lower -0.468) |
| `on_rrp_change_bn` | 1845 | 22.563 | 14.119 | 15.572 | +0.310 (lower +0.286) | -0.103 (lower -0.142) | -0.598 (lower -0.662) |
| `sofr_dispersion_bps` | 1846 | 4.628 | 3.670 | 3.101 | +0.330 (lower +0.241) | +0.155 (lower +0.054) | -0.261 (lower -0.820) |
| (for scale) SOFR − IORB, #634 candidate (b) | - | - | - | - | +0.201 (lower +0.123) | +0.268 (lower +0.175) | - |

Skill is `mean(S(benchmark) − S(model)) / mean(S(benchmark))`; positive favours the model. The last row is #634's spread row: the same model class, inputs, leads and bootstrap for SOFR − IORB.

## By lead (skill over B1, lower 95% bound)

| target | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | +0.278 (lower +0.198) | +0.343 (lower +0.285) | +0.326 (lower +0.261) | +0.327 (lower +0.258) | +0.362 (lower +0.300) |
| `on_rrp_change_bn` | +0.327 (lower +0.299) | +0.331 (lower +0.303) | +0.314 (lower +0.288) | +0.283 (lower +0.250) | +0.293 (lower +0.259) |
| `sofr_dispersion_bps` | +0.300 (lower +0.226) | +0.340 (lower +0.255) | +0.335 (lower +0.243) | +0.333 (lower +0.234) | +0.337 (lower +0.235) |

## By as-of scarcity state of the decision day (skill over B1)

| target | ample | scarce |
|---|---|---|
| `bgcr_dispersion_bps` | +0.293 (lower +0.233) (1356 days) | +0.404 (lower +0.279) (490 days) |
| `on_rrp_change_bn` | +0.303 (lower +0.279) (1356 days) | +0.400 (lower +0.291) (489 days) |
| `sofr_dispersion_bps` | +0.171 (lower +0.114) (1356 days) | +0.429 (lower +0.295) (490 days) |

## By day type of the target day (skill over B1)

| target | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | +0.162 (lower -0.226) (495) | +0.385 (lower +0.302) (1846) | -0.067 (lower -0.194) (127) | +0.061 (lower -0.069) (210) |
| `on_rrp_change_bn` | +0.160 (lower +0.070) (495) | +0.326 (lower +0.301) (1845) | -0.260 (lower -0.375) (127) | +0.219 (lower +0.119) (210) |
| `sofr_dispersion_bps` | +0.144 (lower +0.073) (495) | +0.407 (lower +0.259) (1846) | -0.103 (lower -0.141) (127) | -0.052 (lower -0.194) (210) |

## Lead on the +5 bp episodes (pre-onset AUC at lead 1, within the as-of state)

| target | series | state | onsets | AUC | 90% interval |
|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | as_of_value | ample | 4 | 0.653 | [0.563, 0.759] |
| `bgcr_dispersion_bps` | as_of_value | scarce | 23 | 0.406 | [0.361, 0.454] |
| `bgcr_dispersion_bps` | model_median | ample | 4 | 0.573 | [0.451, 0.642] |
| `bgcr_dispersion_bps` | model_median | scarce | 23 | 0.379 | [0.312, 0.444] |
| `on_rrp_change_bn` | as_of_value | ample | 4 | 0.543 | [0.380, 0.692] |
| `on_rrp_change_bn` | as_of_value | scarce | 23 | 0.465 | [0.426, 0.503] |
| `on_rrp_change_bn` | model_median | ample | 4 | 0.421 | [0.310, 0.526] |
| `on_rrp_change_bn` | model_median | scarce | 23 | 0.528 | [0.459, 0.598] |
| `sofr_dispersion_bps` | as_of_value | ample | 4 | 0.560 | [0.508, 0.593] |
| `sofr_dispersion_bps` | as_of_value | scarce | 23 | 0.410 | [0.348, 0.470] |
| `sofr_dispersion_bps` | model_median | ample | 4 | 0.489 | [0.457, 0.509] |
| `sofr_dispersion_bps` | model_median | scarce | 23 | 0.390 | [0.306, 0.468] |

## Reading against H9's kill criterion (development, not a verdict)

* `bgcr_dispersion_bps`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is +0.504 (above zero).
* `on_rrp_change_bn`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is -2.079 (not above zero).
* `sofr_dispersion_bps`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is +0.298 (above zero).

**Reading.** No chosen target shows both skill over persistence and a lead on the +5 bp episodes on development data; the kill criterion as worded is met. This is not a verdict, and it rests on days that confirmation will not use.


## What the tables say, and what they do not

* **Skill over persistence is large, and persistence is a weak yardstick for these targets.** Step 1 found B2 (the calendar climatology) ahead of B1 for the three dispersions from lead 2 and for the ON RRP change at every lead. The model's skill over B1 (+0.31 to +0.33)
  is therefore easier to earn than the spread's (+0.20). Against the climatology the dispersions keep a smaller gain (+0.16, lower bounds above zero) and **the ON RRP change loses to it** (−0.10, interval below zero).
* **Where it is not there:** quarter-end target days (all three targets negative, `on_rrp_change_bn` −0.26, lower bound −0.38) and, for the SOFR dispersion, tax dates (−0.05). The gain sits on ordinary days and in the scarce state.
* **No lead on the +5 bp episodes is shown.** Within the scarce state, which holds 23 of the 26 onsets, the pre-onset AUC of the modelled median is 0.38 (BGCR dispersion), 0.53 (ON RRP change) and 0.39 (SOFR dispersion), none with an interval above one half; the as-of values
  do no better (0.41, 0.47, 0.41). In the ample state four onsets give wide intervals. Step 1's reading stands: the lead of the rate-level and dispersion series is the scarcity state, not a signal within it.
* **Beside #634's spread row** (the same model class, inputs, leads and bootstrap for SOFR − IORB, skill over B1 +0.20 [lower +0.12], over B2 +0.27 [lower +0.17]): the dispersions are more learnable than the spread against persistence and less against the climatology.
  The units differ, so the comparison is of skill, not of CRPS.

## Reading against H9's kill criterion

The criterion ("no forecast skill over persistence, or no lead on the +5 bp episodes") is read as the declaration reads it: a target meets it when it shows no skill or no lead, and H9 is alive on development data only if at least one target shows both. On
development data **no chosen target shows both**, so the criterion as worded is met. This is a reading, not a verdict, and it rests on days that confirmation will not use. Whether the wording is "or" or "and" (`H9.md` says "and no nested gain for H5"; the queue says "or")
is Eleonora's call: under "and" the criterion also needs step 3's nested test, which this page does not run.

## Not done, and for Eleonora

* The next step, the nested test with H5's best candidate with and without each target's forecast as an input, is not run (it needs #634 merged).
* The nested test of the directive is read as "beside #634's spread row", not as a nested model comparison (marked as a question in the pull request).
* The two readings of the target choice above, and the kill-criterion wording.
* Intervals are not corrected for the three targets, five leads and several splits. A cell that stands out is a candidate for a declared test, not evidence.

Reproduce: the commands in the docstring of `scripts/richer_targets_706.py`; the scratch panel digest is in the declaration. Evidence: `docs/pivot/evidence/richer-targets-706/` (`score.json`, `report.md`).
