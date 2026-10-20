# The B2 leg of "Supported" on contiguous post-2020 windows (#1015, H1 step 3)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES`, `docs/decisions/scoring-protocol.md` and the draft amendment of PR #953 are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is declared in `metadata/b2_leg_contiguous_1015.json` before any score and read from `docs/research/b2-leg-contiguous-1015/result.json` by `scripts/b2_leg_contiguous_1015.py report`. It adds to the page of #963 (`contiguous-calibration-963-result.md`), which stands: that page reads only the leg against B1.

## Questions for Eleonora (marked)

1. **Does the 250-day confirmation window stay, given both legs?** The readings below apply #963's declared rules to each leg; the design is hers.
2. **Is the joint reading (the worse of the two legs) the one to use,** or should a joint rule be written? It is stated here as the plain consequence of "Supported" needing both legs, not decided.

## Series

1429 decision days 2020-04-03 to 2025-12-23, the days of #963's page. The leg against B1 is d = S(B1) - S(candidate); the leg against B2 is d = S(B2) - S(candidate); both positive when the candidate is better. The recomputed leg against B1 reproduces #963's recorded c in every cell (to 1e-9).

| candidate | mean d, leg against B1 | mean d, leg against B2 |
|---|---|---|
| spread_mr_ctx | 0.161 | 0.734 |
| gbm_funding | 0.152 | 0.725 |

## 1. Critical values of the leg against B2

c is the 0.95 quantile of the window statistics. Size is the share of the generator's windows above the value: in force (125 days 3.419; 250 days 2.426; 500 days has none and is read at the 250-day value) and the draft values of PR #953 for this leg (125 days 2.682; 250 days 1.701; 500 days read at the 250-day value). The draft is not in force.

| candidate | days | non-overlapping | c contiguous | c stationary-10 | c circular-10 | size in force, contiguous | size in force, stationary-10 | size in force, circular-10 | size at draft, contiguous | size at draft, stationary-10 | size at draft, circular-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spread_mr_ctx | 125 | 11.4 | 6.61 | 2.01 | 1.65 | 8.4% | 0.6% | 0.0% | 9.7% | 1.8% | 0.4% |
| spread_mr_ctx | 250 | 5.7 | 3.50 | 1.98 | 1.65 | 10.6% | 2.2% | 0.7% | 15.3% | 7.9% | 4.5% |
| spread_mr_ctx | 500 | 2.9 | 1.50 | 2.01 | 1.70 | 0.0% | 2.3% | 0.8% | 1.0% | 8.4% | 4.9% |
| gbm_funding | 125 | 11.4 | 6.46 | 2.02 | 1.67 | 9.5% | 0.6% | 0.0% | 10.7% | 1.7% | 0.4% |
| gbm_funding | 250 | 5.7 | 3.86 | 1.99 | 1.65 | 13.6% | 2.2% | 0.8% | 18.1% | 8.2% | 4.5% |
| gbm_funding | 500 | 2.9 | 1.69 | 2.02 | 1.69 | 1.1% | 2.3% | 0.8% | 4.2% | 8.5% | 4.9% |

## 2. Readings (#963's rule, declared)

Survives below 3.0, fails above 4.0, neither rule applies between; on the contiguous-window c at 250 days. "Supported" needs both legs, so the joint reading is the worse of the two.

| candidate | c, leg against B1 | reading | c, leg against B2 | reading | joint reading |
|---|---|---|---|---|---|
| spread_mr_ctx | 1.92 | survives | 3.50 | neither | neither |
| gbm_funding | 2.07 | survives | 3.86 | neither | neither |

## Limits

Development data seen before the declaration. Contiguous windows overlap heavily, so a quantile of them rests on a handful of independent stretches; the non-overlapping count says how few. B1' (#960) has not replaced B1, as in #963. The draft values of #953 are read as a comparison; whether they are adopted is hers. Nothing here is registered or changed.
