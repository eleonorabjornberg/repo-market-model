# Design note: the distribution the candidate emits, and two coherent rules for the cap (#1389)

**Development data and a design draft, not a verdict, not a decision.** H5 (primary goal), registration design (forecast object); part of the H5
registration priority on #46, after the second outside review (a pre-registration design review of `sc_s3c_ann_net` at 95d21b1f). The rules are
`repo_model.capped_law`, behind a flag whose default is the published reading; nothing published changes. Scores are on
[the result page](cap-tail-rule-1389-result.md). Which rule the registration freezes is hers (the marked question on that page).

## What the candidate emits today

The forecast object of (s3c-ann-net), for a decision day and a lead, is 23 quantiles at the levels of `scoring_protocol.GRID`
(0.01, 0.025, 0.05, 0.10 to 0.90 in steps of 0.05, 0.95, 0.975, 0.99). On a target day at full allotment `s3c_candidate` clips each at
`min(q, line + 0)`; elsewhere the vector is (s3)'s own. The probabilities (`spread_mean_reversion.exceedance`, `ml.exceedance_from_quantiles`) are read
from that vector as follows, and the table says what the cap does to each part.

| part of the law | how it is read today | what the cap does to it |
|---|---|---|
| the 23 quantiles | the model's, sorted | every value above the line is set to the line: a run of equal values at the top |
| between two quantiles | F is linear between the knots | between a kept knot and a capped one F rises over the shorter distance, so the density just under the line is higher than the model's |
| below q1 and above q99 (the completion) | F runs on at the outer segment's slope to 0 and to 1: the tail is `0.01` of probability spread over `0.01` times the slope of the last segment | the last segment is now the capped one. With one capped level it is the segment from q97.5 to the line; with several it is a tie, with slope zero |
| ties | each knot is nudged by `1e-6` bp times its level index so that F is strictly increasing | the nudge is all that is left of the segments between capped levels: a near-vertical F, so an atom at the line of the mass between the first capped level and q99, and a tail above q99 of about `2e-6` bp |
| the event | whole basis points, `data.exceeds_bp`: P(spread > tau) is `1 - F(floor(tau) + 0.5)`, so P(> 10 bp) is read at 10.5 | a tail that runs less than half a basis point above the line has no probability above 10 bp, whatever its mass |
| the randomized PIT | none is defined today | (the rules below define it: `F(k - 0.5)` to `F(k + 0.5)` for the outcome's whole basis point `k`) |

So the same cap gives different laws above the line, depending on how many levels it reached. The cases, each on a synthetic vector in
`tests/test_capped_law_1389.py` (the line is 10 bp):

1. **The cap does not reach q99.** The law is the model's, completion included. The completion may run past the line: nothing bounds it.
2. **One level capped** (the review's example: q97.5 = 9, q99 = 30 before the cap, 10 after). The last segment is 1 bp over 0.015 of probability, 66.7 bp
   per unit, so the 1% tail runs 0.67 bp above the line: P(> 9 bp) = 0.0175, P(> 10 bp) = 0.0025, and the law ends at 10.67 bp.
3. **Several levels capped** (four upper levels at 10 after the cap). F is vertical at 10 from level 0.90 to 0.99: an atom of 9% at the line, the tail
   `2e-6` bp, P(> 10 bp) below `1e-6`. The same line, the same cap, and a probability of 0.0025 in case 2 and none in case 3.

Calibration and the cap can also undo one another. The candidate's only calibrating step is the refit of its residual pool and term effects every 21
decision days (#1366 audited this on the tree: no conformal or cross-conformal subfit, no probability recalibration), and it comes before the cap. A
recalibration of the probabilities applied after the cap (isotonic, Platt, a conformal adjustment) would move mass across a line the cap has just drawn;
one applied before the cap would be clipped by it. Neither exists in the candidate; the registration should freeze the order below so that none can be
added without a change to it.

## Two coherent rules

Both keep the quantile vector exactly as it is: the grid CRPS and the upper-tail twCRPS read the vector, so neither rule moves a published figure, and the
study checks that each rule's law has the capped vector as its quantiles at all 23 levels. They differ in what is said beyond the vector. In both, the
quantiles, the probabilities and any randomized PIT are read from one distribution function (`capped_law.PiecewiseLaw`).

**(a) A bounded law with an atom at the line** (`rule="atom_at_line"`). *Order: calibrate, cap, read.* The uncapped law (the model's quantiles with the
completion above) is the calibrated one. The cap is a transformation of the variable, `Y = min(Y_uncapped, line)`: the mass the uncapped law had above
the line becomes an atom at the line, and nothing lies above it. P(> tau) for `tau` at or above the line is zero by rule; below the line it is the
uncapped law's. The quantiles of this law are the capped vector. Case 2 gives an atom of 2.4% at the line and P(> 9 bp) = 0.0246; case 3 an atom of 10.8%.
A cap that does not reach q99 still bounds the completion at the line. The rule claims that the spread cannot exceed the facility's minimum bid; the
facility is a ceiling on repo rates for its counterparties, not on every rate (outcomes above the line occur in the development window, see the result page).
The PIT of an outcome at the line is the interval over the whole atom; of an outcome above it, 1.

**(b) The capped percentiles with an explicitly unbounded completion** (`rule="open_tail"`). *Order: calibrate, cap the percentiles, complete the capped
percentiles.* The law is read from the capped vector alone: linear between the levels below the line, an atom at the line of the mass between the first
capped level and q99, and the last 1% (the mass above q99, which the percentiles themselves allow above the line) running on above the line, linearly, at
the slope of the last segment that still opens, the one that ends at the first capped level. If no level is under the line there is no open segment and the
law is bounded (`OPEN_TAIL_NO_SLOPE`). Case 2 is the status quo (P(> 10 bp) = 0.0025). Case 3 has the 9% atom and a tail 1 bp long: P(> 10 bp) = 0.005,
independent of how many levels the cap reached. It makes no claim that the tail beyond the line is impossible, and claims at most 1% of mass there.
Its limit: the tail's length is the slope of the last open segment, which is short where the cap reaches low levels, so on whole basis points a tail under
half a basis point has no probability above 10 bp (the result page's table of cells by levels changed). A tail that matters at the line would need a tail
scale published beside the percentiles.

**The status quo** is neither: its law above the line is the one in cases 1 to 3, a function of the number of capped levels.

## What is not done here

No cap, candidate, record or scoring code is changed: `spread_mean_reversion.exceedance` and `ml.exceedance_from_quantiles` are untouched and the
default rule reproduces them (`StatusQuoTests`). No live record carries the candidate, so no probability from a rule is published. The 16:00 instants of
the earlier cap studies (#1241, #1252) are not re-run. The result page scores the rules on the development window and on the 2026 days apart; it settles
nothing.
