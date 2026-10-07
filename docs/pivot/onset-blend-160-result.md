# Onset-day blend: the result (#160)

**The blend fails its declared test. It is reported only; no published figure, record, declaration or page moves.**
The candidate and the test are in [`onset-blend-160.md`](onset-blend-160.md), committed before any scoring.
Reproduce: `OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/onset_blend_160.py --panel PANEL --output OUT.json`
(panel digest `4ddc3882…`, the published panel; h = 1; 1,873 scored days, 2018-06-29 to 2025-12-31, no locked day).

## The test: Brier(v1) minus Brier(blend), 90% stationary bootstrap

Positive favours the blend. A cell is "worse beyond its interval" when its whole interval is below zero. Every cell
here has at least 20 days.

| Cell | +5 bp | +10 bp |
|---|---|---|
| All days | −0.0016 [−0.0033, +0.0001] | +0.0004 [−0.0004, +0.0013] |
| Regime 2018-19 | **−0.0080 [−0.0161, −0.0002]** | +0.0031 [−0.0003, +0.0070] |
| Regime 2020 | **−0.0035 [−0.0059, −0.0017]** | +0.0005 [−0.0002, +0.0011] |
| Regime 2021-23 | +0.0002 [+0.0001, +0.0003] | +0.0002 [+0.0002, +0.0002] |
| Regime 2024 | −0.0005 [−0.0013, +0.0001] | +0.0000 [−0.0001, +0.0001] |
| Regime 2025-26 | +0.0034 [−0.0018, +0.0089] | −0.0028 [−0.0062, +0.0002] |
| Month end | −0.0040 [−0.0092, +0.0012] | **−0.0040 [−0.0077, −0.0008]** |
| Ordinary | −0.0008 [−0.0027, +0.0009] | +0.0011 [+0.0003, +0.0018] |
| Quarter end | −0.0135 [−0.0329, +0.0012] | **−0.0171 [−0.0358, −0.0027]** |
| Tax date | −0.0073 [−0.0193, +0.0026] | +0.0024 [−0.0009, +0.0061] |

It fails twice over. Condition 1: the all-days interval does not clear zero at either threshold (the point estimate at
+5 bp favours v1). Condition 2: bold cells are worse beyond their intervals (+5 bp: regimes 2018-19 and 2020; +10 bp:
month end and quarter end).

## The finding, on the same days (descriptive, not part of the test)

Brier(persistence-logistic) minus Brier(model); positive favours the model. The v1 column reproduces #160's and
#209's published figures.

| Group | Threshold | Days / events | Logistic minus v1 | Logistic minus blend |
|---|---|---|---|---|
| At-risk (#209) | +5 bp | 1,586 / 27 | +0.0003 [−0.0009, +0.0014] | +0.0006 [+0.0000, +0.0011] |
| At-risk (#209) | +10 bp | 1,586 / 11 | −0.0005 [−0.0010, +0.0000] | −0.0001 [−0.0004, +0.0002] |
| One-day (#160) | +5 bp | 1,734 / 47 | −0.0014 [−0.0034, +0.0006] | +0.0003 [−0.0007, +0.0012] |
| One-day (#160) | +10 bp | 1,734 / 19 | −0.0010 [−0.0017, −0.0003] | −0.0002 [−0.0005, +0.0002] |

## What it says

- The blend removes the onset-day deficit: the one interval that excluded zero for v1 (one-day variant, +10 bp)
  includes it for the blend.
- It pays for that on the days the model exists for: stress regimes (2018-19, 2020) at +5 bp, and month ends and
  quarter ends at +10 bp, where it is clearly worse than v1.
- So averaging in the persistence-logistic is not a fix. The deficit is real and small; a candidate that closes it has
  to do so without weakening the model on turn days. The onset groups rest on 11 to 47 events and decide nothing
  (`docs/decisions/pressure-probability.md`).
- One candidate was declared and scored once. No other candidate was tried.

## Not checked

Horizons 2 to 5 (the finding is about h = 1); the +20 and +50 bp thresholds; the five-quantile score (the blend
does not touch the distribution); any day from 2026-01-01.
