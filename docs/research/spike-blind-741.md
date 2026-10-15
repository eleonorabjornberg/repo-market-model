# A forecaster that declines to copy a calendar spike, against B1 (#741)

Serves H1 ([`hypotheses/H1.md`](hypotheses/H1.md)), step 3: are the benchmarks right. It follows finding #741 and the simulated panel of #762 (PR #764). Development evidence on simulated data only. It changes no rule, no benchmark, no MME and no published figure: B1, B2, B3 and the MME are as scoring protocol v1 has them (Eleonora's ruling on #741, 14 October 2026).

## The question

B1 centres every lead on the anchor, the last public row. When the anchor is a quarter-end, tax-date or month-end spike, B1 carries it forward to all five leads. **Does a forecaster with no ordinary-day skill, which merely does not copy that spike, beat B1 by the MME (3%, protocol §6)?**

## The forecaster and the process

- `tests/benchmark_simulation.py: spike_blind_forecast`: B1 with the anchor's spread replaced by the spread of the last ordinary day at or before the anchor. No parameter. On an ordinary anchor it is B1 exactly, so it has no skill on ordinary days by construction (asserted). It reads nothing after the anchor (asserted).
- The process is #762's: a Gaussian AR(1) (phi 0.7, sigma 1 bp) around day-type levels (ordinary 0, tax date 2, month-end 3, quarter-end 8 bp), 2018-01-02 to 2021-12-31, scored on every third decision row from 2020-01-02 (about 166 decisions per panel). B1 runs under the registry's own availability declarations.
- The score is the protocol's: the mean over the five leads of the 23-level grid CRPS per decision day, skill `mean(d) / mean(S(B1))` with `d = S(B1) - S(candidate)`.
- Monte Carlo: 200 simulated panels (seeds 741000 to 741199). A cell is the mean skill over panels, with the normal-approximation 95% interval across panels; the last column is the share of panels whose own skill is at or above the MME.

```
PYTHONPATH=src python3 tests/benchmark_simulation.py spike-blind --replicates 200 --decision-step 3
PYTHONPATH=src python3 tests/benchmark_simulation.py spike-blind-no-spikes --replicates 200 --decision-step 3
```

## Result

On the declared process (spikes of 2, 3 and 8 bp):

| anchor day type | decision days per panel | skill against B1 | 95% interval | share of panels at or above the MME |
|---|---|---|---|---|
| pooled | 166 | +17.58% | [+17.33%, +17.84%] | 100% |
| ordinary | 144 | +0.00% | [+0.00%, +0.00%] | 0% |
| month_end | 14 | +52.29% | [+51.09%, +53.50%] | 100% |
| tax_date | 4 | +32.55% | [+29.22%, +35.87%] | 89% |
| quarter_end | 4 | +84.45% | [+83.82%, +85.09%] | 100% |

Control, the same forecaster on a process with no spikes (all four levels 0):

| anchor day type | decision days per panel | skill against B1 | 95% interval | share of panels at or above the MME |
|---|---|---|---|---|
| pooled | 166 | -1.27% | [-1.54%, -1.01%] | 1% |
| ordinary | 144 | +0.00% | [+0.00%, +0.00%] | 0% |
| month_end | 14 | -10.96% | [-13.40%, -8.52%] | 22% |
| tax_date | 4 | -6.45% | [-10.70%, -2.21%] | 44% |
| quarter_end | 4 | -21.03% | [-27.12%, -14.94%] | 28% |

(The control's per-type shares are shares of panels whose few anchors of that type happen to favour the forecaster; with four or fourteen days they are noisy and carry no weight.)

## Reading

**Yes: on a process where the calendar spikes are real and known and the ordinary days have no exploitable structure beyond what B1 uses, a forecaster with no ordinary-day skill beats B1 by far more than the MME** (pooled +17.6%, interval [+17.3%, +17.8%]; every one of the 200 panels is at or above the MME). The whole gain comes from the spike anchors, none from ordinary ones. With no spikes the same forecaster has no gain (slightly negative), so the gain is the spikes'. The size depends on the declared spike heights and the share of spike anchors (about 13% of decision days here); the figure describes this process, not the repository's panel, whose own development figure is in finding #741 (+14.9% on the published panel to 2025-12-31, computed there by a different route).

**This is candidate evidence (a) for a §13 change** (the ruling's wording). It is not a change. A change to B1 needs the auditor's confirmation and Eleonora's attested action. Nothing in this PR touches B1, B2, B3 or the MME, in code or text.

Not checked: other spike heights, a spike that varies from quarter to quarter, heavier tails, and the real panel (finding #741's table was not recomputed).

## H5 result pages

H5 result pages that score a candidate against B1 now report skill by the anchor's day type with the pooled figure beside it: `repo_model.anchor_day_type` supplies the split (the anchor is `protocol_benchmarks`' own) and `scripts/spread_mean_reversion_686.py` (the only H5 result page on main scored against protocol B1) reads it. Pages still in open pull requests (#634's, #761's, #707's, #758's) take the same two-line call when they merge; that is flagged on the pull request.
