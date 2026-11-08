# Each power-study set-up's size and power, side by side (#1517)

**Dated note, 8 November 2026 (#1517; finding #1514).** Hypothesis and step: H5, M5 / H1, M4 (the confirmation design's power-study gate). Eleonora ruled (decision docket, 8 November 2026, 4:46 pm ET): "pair". Nothing is measured here: every figure below is read from `docs/research/confirmation-size-power-1392/result-full.json` (full mode, 500 simulated data sets per cell, development data, not a verdict) and appears on `docs/research/confirmation-size-power-1392-full-result.md` and in rule 6 of `docs/decisions/h5-confirmation-design.md`. `tests/test_size_power_pairing_1517.py` recomputes each one from the cells.

## What was wrong

The note of #1506 (section 9 of `docs/research/recalibration-1482-result.md`, and its research-log entry `2026-11-07-model-01506-H1-step4.md`) quoted "at most 1.4%" at the 3% boundary and "about 32-35%" power at 10% skill with 500 origins. The 1.4% is the pass rate with **both** baselines at 3% skill. The 32-35% is power with **B1′\* binding and B2 as developed**. They are figures of two different set-ups, and in each the figure left out is the less favourable one. The log entry is frozen once on main and is not edited; this note is its correction. The page was corrected in the same pull request (its section 9 bullet now gives each set-up its own pair).

## The two set-ups, side by side

Pass rate of claim A, in percent, test block 50. Size is the pass rate when the true skill is at the 3% boundary; power is the pass rate at 10% skill. Monte Carlo standard errors are on the study page.

| set-up | scheme | size at 3%, 500 origins | size at 3%, worst tested length | power at 10%, 500 origins |
|---|---|---|---|---|
| Rule 4 as written: against B1′\*-cap alone (B1′\* binding, B2 as developed) | block resampling | 6.2 | 8.6 (750 origins) | 34.6 |
| | regime chain | 6.4 | 10.8 (250 origins) | 31.6 |
| Both baselines at the stated skill | block resampling | 0.6 | 0.6 (250 and 500 origins) | 6.6 |
| | regime chain | 0.8 | 1.4 (250 origins) | 3.4 |

## Reading

- Against B1′\*-cap alone, the set-up rule 4 uses, the test is somewhat above the nominal 5% at the boundary (6.2% and 6.4% at 500 origins, up to 10.8% at other lengths) and has power of about a third at 10% skill with 500 origins. Eighty percent power is first reached at 2,500 origins (85.8% block, 87.0% regime).
- With both baselines held at the boundary the test is conservative (at most 1.4%) and has power of 6.6% and 3.4% at 10% skill with 500 origins. This is why rule 4 makes the claim against B1′\*-cap alone.
- No set-up has both a size at or below the nominal 5% and power above about 7% at 500 origins. The size and the power of one set-up are read together; the low size of one is never set beside the power of the other.
- These rates come from a bootstrap with far fewer draws than the 50,000 of rule 5 and from schemes that resample 2018 to 2026 origins. B2 stands in for B2\*, and the capped baselines are not built, so they describe the test and do not forecast this candidate's result.

## The gate

The gate on H1.M4 and the H5 registration, "wait on the confirmation design's own size-and-power study (#1392)" (`docs/research/hypotheses/H1.md`), reads as met by her 7 November 2026 "keep" ruling (decision docket, card why-confirm-1107, option keep): 500 origins, at least 24 months, one final analysis, and the power stated beside the result. The study is finished and published; with the pairing above stated, the registration carries both the size and the power of its set-up.

## Unchanged

No threshold, critical value, decision record, published record or registration is changed by this note. The MME stays at 3%. The size row for the registration draft (#1511, branch of #1510) is left to that branch's own session as a ready-to-apply patch on its pull request.
