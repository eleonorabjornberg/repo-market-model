# Narrowed coupon-settlement flag: the test, declared before scoring (#339)

Status: declared in a commit before any candidate was scored. Eleonora's ruling on #339 ("Publish if it improves the
model") and her ruling on PR #341 set the test below; this file only fixes its details. The candidate and the test
are run by `scripts/settlement_flag_candidate.py`; nothing in this file changes after the scoring commit except by a
new commit that says why.

## The candidate

The published declaration reads the coupon-settlement day only through its conformal PID scorecaster's fourth
indicator (`recalibration.SCORECASTER_INDICATORS`, `coupon_settlement`: `treasury_settlement_coupons > 0`, read at
h = 1; at h = 2 to 5 the indicator is already dropped, #170). The candidate replaces that indicator with the
narrowed flag and changes nothing else: same features, same fits, same refits, same grid, same nested selection.

**Narrowed flag, on the scored day:** 1 when the tracked Treasury auction snapshot lists a nominal (not floating-rate,
not inflation-indexed) Note or Bond that settles that day and is

- a 3-, 10- or 30-year security (with the reopenings the snapshot labels by remaining term, `9-Year n-Month`,
  `29-Year n-Month`) settling on the 15th of the month or the next business day of the panel; or
- a 2-, 5- or 7-year note settling on the month's last calendar day or the next business day of the panel.

FRN, TIPS, 20-year and any other settlement, and a nominal settlement off those dates, do not mark the day. The flag
is a subset of the days the published flag marks, from the same auction records and the same announcement dates, so
it is public no later than the published flag is, and the published flag's availability guard
(`scorecaster_calendar`) still runs on every day.

## The test

- **Days:** the published window, 2018-06-29 to 2025-12-31 only. No row after 2025-12-31 is loaded into the walk.
- **Pairing:** each scored day, published declaration against candidate, both walked in one process.
- **Five-quantile score:** `metrics.crps_from_quantiles` per day, the published CRPS record's loss. Paired difference
  = CRPS(published) - CRPS(candidate); a positive mean favours the candidate. 90% stationary-bootstrap interval, block
  length `final_test_preregistration.CRPS_BLOCK_LENGTH`, seed `onset._seed("#339", "crps")`.
- **Pressure probability:** pressure model v1's declaration (`scripts/pressure_model_v1.py publish`), probability read
  from the same calibrated distribution, at +5 bp and +10 bp. Brier paired the same way
  (`baseline.benchmark_comparison_document`, candidate as the model, published as the reference); a positive mean
  favours the candidate. The model reads the flag through the distribution, so the Brier test applies.
- **Splits:** each paired figure split by regime and by pressure-day type (`baseline.split_document`), as the records
  are. A cell under 20 days is "too few days" and decides nothing.

## The rule

The narrowed flag joins the published declaration in this pull request only if all of these hold:

1. CRPS: mean difference above 0 and the 90% interval's lower bound above 0.
2. Brier at +5 bp: mean difference above 0 and the lower bound above 0.
3. Brier at +10 bp: mean difference above 0 and the lower bound above 0.
4. No regime cell and no pressure-day-type cell (cells of 20 days or more) of the CRPS or of either Brier figure has
   its interval's upper bound below 0.

Otherwise the flag stays off, and the pull request reports the figures only. The live record and its pin are not
touched either way.
