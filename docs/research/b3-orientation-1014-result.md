# The B3 five-level critical value in the orientation `report` reads (H1, #1014)

**Development data only; no verdict, no lockbox day scored.** Every figure is read from `docs/research/b3-orientation-1014/result.json` by `scripts/b3_orientation_1014.py report`. `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read, and PR #953 is untouched.

## What was calibrated

`report` reads B3 as the benchmark: d = S(B3) - S(B1), B3 the benchmark, as `scoring_protocol.report` reads its against-B3 test. The drafts of #873 and #886 calibrated the B3 value on S(B1) - S(B3), the reverse; the daily difference is skewed, so the two quantiles differ (#830). This page calibrates on S(B3) - S(B1) over 1429 decision days (2020-04-03 to 2025-12-23), 20,000 windows at each look, circular blocks of 10 days, seed 1, as the record in force.

## The value and each value's null share

The null share is the share of 2,000 null paths (no true difference, the first 250 days of a stationary-bootstrap resample of the same S(B3) - S(B1) series, #699's rule, ungated) detected by that look. A value calibrated for this series has a null share near its nominal level: 0.6% at 125 days and 4.8% by 250 days (the overall size is 5%).

| value | source | critical 125 | critical 250 | null share by 125 | null share by 250 |
|---|---|---|---|---|---|
| in force | `scoring_protocol.CRITICAL_VALUES` | 9.501 | 5.455 | 0.0% | 0.1% |
| #873 draft | `protocol-calibration-873/result.json` (S(B1) - S(B3), full history) | 1.434 | 1.006 | 22.9% | 35.0% |
| #886 draft | `protocol-calibration-886/result.json` (S(B1) - S(B3), post-2020 stationary windows) | 2.267 | 1.583 | 11.4% | 21.9% |
| calibrated here | `scripts/b3_orientation_1014.py` (S(B3) - S(B1), post-2020-04) | 4.359 | 2.554 | 1.1% | 6.8% |

## For Eleonora (nothing settled in code)

Adopting any of these values is a section 13 decision and is hers; this page changes no constant. For the draft in #953, a marked line it could carry: *"B3 five-level critical values: calibrate on S(B3) - S(B1), the orientation `report` reads; value pending Eleonora's decision."*
