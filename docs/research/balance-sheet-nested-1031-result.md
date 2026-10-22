# The balance-sheet days on the turn days, nested into the calendar-aware candidate (#1031, H5 step 2 / H6 step 1): result

**Development data, not a verdict.** A measurement under scoring protocol v1: nothing is published or registered, no rule, published model, declaration or figure moves, and the turn relabel is not adopted. Design and declaration: `docs/research/balance-sheet-nested-1031.md` and `metadata/balance_sheet_nested_1031.json` (committed before any number). The full tables are `docs/research/balance-sheet-nested-1031/report.md`; every figure below is in `docs/research/balance-sheet-nested-1031/result.json`, extracted from `score.json`, which her Mac run wrote.

Published panel `4ddc3882…`, scratch panel `f9fae9dc…`; seed 1031, 10,000 draws, the studentized stationary bootstrap (Lens C's caveat on the lag-10 standard error applies). 1,855 decision days to 2025-12-23, every pair on the same days; no day after 2025-12-31 and no locked day is scored. Skill = mean(d) / mean(S(benchmark)), positive favouring the first-named model; intervals are two-sided 90% (the lower end is the one-sided 95% lower bound). Both arms read the calendar and the three flag columns at the target day on direct pairs, so neither is in the provisional-calendar class.

## What the flags add to the base (grid CRPS, the primary score)

| cut | days | coded over base | turn over base | turn over coded (the relabel alone) |
|---|---|---|---|---|
| pooled | 1,855 | +0.4% [+0.1%, +0.9%] | +0.3% [−0.3%, +0.9%] | −0.2% [−0.7%, +0.5%] |
| turn days (the relabelled flags' days) | 179 | −0.0% [−0.7%, +0.8%] | +0.9% [−1.0%, +3.0%] | +0.9% [−1.3%, +2.8%] |
| as-coded flag days | 166 | +0.8% [+0.1%, +1.6%] | +0.8% [−0.9%, +3.9%] | +0.0% [−1.8%, +2.5%] |
| days neither set flags | 1,604 | +0.4% [+0.0%, +0.9%] | +0.1% [−0.2%, +0.5%] | −0.3% [−0.8%, +0.2%] |
| quarter-end turn | 44 | +1.4% [−0.8%, +10.0%] | +4.4% [+0.4%, +13.6%] | +3.0% [−1.7%, +9.1%] |
| turn (all turn-type days) | 120 | −1.4% [−2.6%, −0.5%] | −0.4% [−4.3%, +1.5%] | +1.0% [−1.0%, +2.6%] |

Against B2 both arms are about +26% pooled (+26.1% and +26.0%), but so is the base alone (+25.8%): the flags add under one percentage point to that.

## Reading, by the declared rules

- **Turn arm over the base:** not shown to beat it on the turn days (one-sided 95% lower bound −1.0%); it does not lose on the days neither set flags.
- **Coded arm over the base:** beats it on the as-coded flag days (lower bound +0.1%) and does not lose elsewhere. The margin is a tenth of a percentage point on 166 days, one cell among many unadjusted ones.
- **The relabel alone** (turn over coded, on the turn days): not shown to help (+0.9%, lower bound −1.3%).
- **Quarter-end turns** (44 days) are the one place the turn arm's interval over the base clears zero (+4.4%, lower end +0.4%), and its interval over the coded arm does not (−1.7% to +9.1%). It is thin, not declared as a headline cut, and rests on a handful of quarters.
- **Upper-tail twCRPS** moves the same way and no further: pooled +0.4% for either arm, intervals spanning zero. Cells where B2's twCRPS is zero are undefined and are marked so in `result.json`.
- **By regime** nothing separates the arms from the base except the coded arm in 2024 (+2.1%, lower end +0.0%). On the turn-type days the coded arm is worse than the base (−1.4%, interval wholly below 0), the one cell where a flag set loses.
- 26 December (5 days) and the year-end target type (15 days) are under 20 days: listed, not tested.

## What this shows and does not show

The balance-sheet flags, coded or relabelled, add at most a few tenths of a percent to a candidate that already reads the calendar at the target day, and the relabel does not improve on the coding in any cut that is not thin. The calendar columns, the Treasury settlement and the model already carry most of what the flags point at. This is development data on one panel with many cuts and no multiplicity adjustment: it gives no verdict, and a cell at the edge of its interval is what chance produces. It does not say the turn days are uninteresting (#959 shows the spread is high on them), only that these three flag columns do not add to the base.

## Questions for Eleonora (as on the design page; none is settled here)

1. Adopt the turn relabel for the balance-sheet flags? **Default: no.** The relabel stays off in every published declaration; the result gives no case for adopting it.
2. Should the December turn also carry `foreign_bank_quarter_end`? **Default: both.** Not decided by this result (December is among the thin groups).
3. Nest into the aligned one-step variant too? **Default: no.**

## Environment

The walks and the score ran on Eleonora's Mac; `score.json` does not record its interpreter or library versions, and this page cannot supply them. `pyproject.toml` pins Python 3.11 and the `ml` extra (numpy ≥ 2.4.6, scikit-learn ≥ 1.9.1), and a gbm figure moves with scikit-learn's version. **For Eleonora:** paste `python --version` and `pip freeze | grep -iE 'numpy|scikit'` from the Mac environment if the versions are to be on record. This finishing session ran Python 3.11.17 on Linux without the `ml` extra, so it re-ran no walk and re-scored nothing; it read, extracted and checked the Mac's output only.

## Not checked

- The full suite (the pull request's CI runs it). No walk was re-run here; the scores are the Mac run's, read as written.
- The base (`gbm_funding_cal_direct`) and control (`gbm_funding`) walks are #1027's and were read from her Mac; this session does not hold them.
- No power or multiplicity analysis for the quarter-end-turn cell.
