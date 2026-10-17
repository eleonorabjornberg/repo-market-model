# H4 step 3 re-read: the back-fill against H5's candidate on the ruled interval (#870)

Hypothesis and step: **H4** step 3 (a re-read of #726's development nested test; not a new variant).

Development data only: it gives a score and an interval, never a verdict (scoring protocol v1, #640). It writes nothing into `docs/runs/`, publishes nothing, moves no published figure and scores no day after 2025-12-31 (`docs/decisions/lockbox.md`). Everything was declared in `metadata/backfill_h5_726_reread.json` and committed before any score. #759's declaration and page are not edited; this page supersedes nothing until Eleonora says so.

## What changed from #759

- **The guard (#862).** `scripts/backfill_h5_726.py` now reads the admitted list from `metadata/backfill_posting.json`, blanks back-filled rows to it, refuses an extended panel whose back-filled rows carry an unadmitted column (`LookAheadError`) and runs `backfill.require_series_admitted` on the series the fits draw from those rows. With today's list (TGCR, BGCR, SOFR) the panel is the same one: digest `1e09ae43…` is reproduced.
- **The interval (#861).** Every figure uses the studentized stationary bootstrap of ruling 1 (two-sided 90%). The superseded percentile interval is shown beside it.
- **The split (#859).** 2018-19 is split into half-years, and the comparison is repeated on decision days by the share of back-filled rows in the with arm's training frame.

The ten walks are #759's, re-run under the guard (both arms, h = 1 to 5, same candidate, features, settings and days). The 2018-19 figures reproduce #759's: CRPS 4.005 without, 4.119 with, mean d −0.114.

## Reading

d = CRPS(without) − CRPS(with), positive when the back-fill helps. Full table: `docs/pivot/evidence/backfill-h5-726-reread/score.md`.

| group | days | mean d | studentized 90% interval | percentile 90% (superseded) | mean − c·se | mean + c·se | reading |
|---|---|---|---|---|---|---|---|
| 2018-19 | 376 | −0.114 | [−0.180, −0.058] | [−0.168, −0.061] | −0.200 | −0.027 | cost shown |
| 2018 H2 | 124 | −0.229 | [−0.359, −0.114] | [−0.333, −0.129] | −0.412 | −0.045 | cost shown |
| 2019 H1 | 124 | −0.041 | [−0.085, +0.011] | [−0.079, +0.002] | −0.105 | +0.023 | covers zero |
| 2019 H2 | 126 | −0.060 | [−0.145, +0.051] | [−0.132, +0.021] | −0.182 | +0.062 | covers zero |
| 2019 | 250 | −0.051 | [−0.098, +0.006] | [−0.094, −0.005] | −0.120 | +0.019 | covers zero (the percentile interval said cost) |
| 2024 | 250 | −0.030 | [−0.077, −0.005] | [−0.064, −0.001] | −0.073 | +0.012 | cost on the ruled interval; covers zero at c |
| 2025-26 | 244 | −0.048 | [−0.088, −0.015] | [−0.083, −0.015] | −0.100 | +0.004 | cost on the ruled interval; covers zero at c |
| pooled | 1869 | −0.001 | [−0.037, +0.064] | [−0.038, +0.040] | −0.063 | +0.060 | covers zero |

c = 2.426, the 250-day reference of the grid comparison. `mean + c·se` below zero is a cost in the orientation d = without − with; `mean − c·se` above zero would be a gain. Under the reverse orientation of #830 the two columns swap roles and change sign. Which is in force is Eleonora's (#830). 2018 H1 has two decision days and is not tested.

### The mostly-imputed fits

The back-filled share of the with arm's training frame falls from 94% at the first refit to 33% at the last. The imputed share of input cells runs from 82% to 28%.

- **At most 50% back-filled:** no 2018-19 day qualifies (the share is 68% or more through 2019). The qualifying days are pooled −0.002 [−0.047, +0.121], and the 2024 and 2025-26 costs are unchanged because every day of those regimes qualifies.
- **At most 75% (declared sensitivity):** 2018-19 keeps 124 days (late 2019), −0.060 [−0.144, +0.058], covers zero. The days above 75% (252, all of 2018 and early 2019) are −0.140 [−0.233, −0.075], a cost.
- **At most 90% (declared sensitivity):** 2018-19 keeps 334 days, −0.086 [−0.144, −0.035], still a cost. The 42 days above 90% alone cover zero.

So the 2018-19 cost sits where the training frame is most imputed, as #859 found, but it does not vanish once the share drops: 2019 alone is borderline on the ruled interval (upper end +0.006).

## One line per reading against H4's kill clause (development, not a verdict)

- 2018-19, all days: cost shown (ruled interval; also at c).
- 2018 H2: cost shown. 2019 H1 and H2: neither shown.
- 2019 alone: neither shown on the ruled interval.
- 2018-19 on days at or under 50% back-filled: no day; under 75%: neither shown; under 90%: cost shown.
- 2024 and 2025-26: cost shown on the ruled interval, not at c; the pooled sample: neither shown.

Whether H4's kill is read, on which line, and under which orientation of c, is left to Eleonora. The kill clause's calibration part (coverage) is not re-read here; #759's coverage tables stand on the percentile interval.

## Questions (hers)

- The share threshold: 50% is the directive's example and leaves no 2018-19 day. 75% and 90% were added in the declaration so that a reading exists. She may name another.
- The orientation of the critical value (#830).
- Whether IORB and SOFR volume are admitted on back-filled rows (#742). The walks read today's list; with TGCR, BGCR and SOFR admitted, `sofr_volume` is the same series as SOFR and IORB is not a series.

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \
    --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
PYTHONPATH=src python3 scripts/backfill_h5_726.py panel --extended EXT.csv --output EXT_EST.csv
# for h in 1 2 3 4 5 and arm in without (PUBLISHED.csv) / with (EXT_EST.csv):
PYTHONPATH=src python3 scripts/backfill_h5_726.py forecasts --arm ARM --panel PANEL --published PUBLISHED.csv --horizon $h --output OUT/ARM_h$h.json
PYTHONPATH=src python3 scripts/backfill_h5_726.py reread --published PUBLISHED.csv --runs OUT --output score.json --markdown score.md
```

Set `OMP_NUM_THREADS=1` when walks run in parallel; ten walks at once on four cores thrash.

Not checked: any 2026 day, the 2014-18 days as scored days, any verdict under protocol v1, and the coverage clause of H4's kill.
