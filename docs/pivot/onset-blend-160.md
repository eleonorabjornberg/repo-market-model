# Onset-day pressure probability: the blend candidate (#160)

**Declared before any scoring. Written in the commit that precedes every score of the candidate.**

## The finding

On onset days (a scored day whose previous panel day was at or below +5 bp) the published pressure
probability (pressure model v1, `scripts/pressure_model_v1.py publish`, h = 1) has a higher Brier score than the
persistence-logistic at both thresholds (#160).

## The one candidate

`blend`: the unweighted mean of two probabilities that already exist on the shared fold grid at each threshold, v1's
recalibrated probability and the persistence-logistic's probability. No weight is fitted and no group is read to
choose it. One candidate is declared, so no choice among candidates is made on the scored days.

## The test (Eleonora's ruling of 7 October 2026 on #339, applied to a pressure probability)

The candidate is scored once, at h = 1, on scored days before 2026-01-01 only, paired against the current published
declaration (pressure model v1 at h = 1). The sign convention is Brier(v1) minus Brier(blend): positive favours
the blend. The interval is the 90% stationary bootstrap of `onset.paired_difference` (block length from the fold
grid). The blend passes only if all of these hold:

1. **All days:** the interval's lower bound is above zero at +5 bp and at +10 bp.
2. **Cells:** no regime cell and no pressure-day-type cell (`metadata/evaluation_splits.json`) has an interval
   entirely below zero, at either threshold. A cell with fewer than 20 days is "too few days" and is not judged.
3. Otherwise the blend stays off and the PR reports it only.

The onset groups (#209's at-risk group and #160's one-day variant) are reported for both the blend and v1 against the
persistence-logistic. They are descriptive and are not part of the test above.

## What a pass or a fail changes

No published record, declaration, page or generated block changes in this PR, whatever the result. A pass is
reported, and putting the blend into the published declaration is a later pull request. The live record and its pin
are untouched.
