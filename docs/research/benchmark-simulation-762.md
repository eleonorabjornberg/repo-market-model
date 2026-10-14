# The benchmarks of protocol v1 on a simulated panel with known dynamics (#762)

Serves H1 ([`hypotheses/H1.md`](hypotheses/H1.md)), step 3's question "is each benchmark computed as specified?". It follows finding #744: the synthetic suite of protocol v1 never calls `repo_model.protocol_benchmarks`, and the by-hand check on the published panel restates the definition. Development evidence on simulated data only. It changes no rule, no benchmark and no published figure.

## What was built

`tests/benchmark_simulation.py` simulates a `DailyObservation` panel on the market calendar (business days from 2018-01-02 to 2021-12-31, no holidays from `metadata/market_holidays.json`). The spread in bp is a level that depends on the day type, plus a Gaussian AR(1):

- levels: ordinary 0, tax date 2, month-end 3, quarter-end 8; AR coefficient 0.7; innovation standard deviation 1 bp;
- day types are assigned from the simulated rows (the last row of a quarter's last month, the last two rows of a month, the first row from the 15th in January, April, June, September and December), not by the repository's calendar code; a test checks that `SplitDeclaration.reporting_day_type` agrees with them;
- the benchmarks run with the registry's own availability declarations (`metadata/sources.json`) at a 16:00 decision time, so both `InformationRule` guards run in `protocol_benchmarks._anchor`.

The known conditional law of row `t + h`, given the last public row `t - 1`, is normal with mean `level + 0.7^(h+1) x[t-1]` and variance `sigma^2 (1 - 0.7^(2 (h+1))) / (1 - 0.7^2)`.

## The alignment, asserted (`tests/test_benchmark_simulation.py`)

| Ruled alignment | How it is asserted |
|---|---|
| The anchor is the last public row | On a ramp (every row 0.1 bp above the last), B1's 23 quantiles at lead h all equal the spread of row `t - 1` plus 0.1 h, after weekends and holidays too |
| B1 at lead h adds h-row changes (ruling 6) | The same ramp, exactly; on the AR(1) panel, against a separately written selection of the trailing two years' changes; and `richer_targets.b1_quantiles` against both |
| B2 equals the day-type climatology | On a panel whose spread is the level of its day type, every quantile of every lead equals the target type's level; on the AR(1) panel, against the trailing year's same-type spreads up to the anchor, and the decision day's own row would change the answer |

Three mutations each fail these tests with `AssertionError`; they are recorded in the test module's docstring (changes over h + 1 rows, an anchor one row late, and the same h + 1 slip in `richer_targets`).

## Coverage of the central 90%, measured and not asserted

200 simulated panels (seeds 762000 to 762199); on each, every third decision row from 2020-01-02 (so each benchmark has at least two years behind it). "True" is the probability under the process's conditional law that the target falls between the benchmark's 5th and 95th percentiles; "realised" is the share of simulated targets that did. Each is a mean over decisions, then over panels; the interval is the normal-approximation 95% interval of the mean across panels. Command:

```
PYTHONPATH=src python3 tests/benchmark_simulation.py --replicates 200 --decision-step 3
```

| Benchmark | Lead | True coverage | 95% interval | Realised coverage | 95% interval |
|---|---|---|---|---|---|
| B1 | 1 | 0.804 | [0.802, 0.805] | 0.806 | [0.803, 0.810] |
| B1 | 2 | 0.867 | [0.866, 0.869] | 0.868 | [0.865, 0.871] |
| B1 | 3 | 0.889 | [0.887, 0.890] | 0.891 | [0.888, 0.893] |
| B1 | 4 | 0.876 | [0.874, 0.878] | 0.878 | [0.875, 0.881] |
| B1 | 5 | 0.873 | [0.871, 0.875] | 0.873 | [0.870, 0.876] |
| B2 | 1 | 0.870 | [0.867, 0.872] | 0.868 | [0.866, 0.871] |
| B2 | 2 | 0.866 | [0.864, 0.868] | 0.866 | [0.863, 0.869] |
| B2 | 3 | 0.869 | [0.867, 0.872] | 0.870 | [0.867, 0.873] |
| B2 | 4 | 0.869 | [0.866, 0.872] | 0.868 | [0.865, 0.871] |
| B2 | 5 | 0.863 | [0.860, 0.866] | 0.863 | [0.860, 0.866] |
| richer_targets B1 | 1 | 0.804 | [0.802, 0.805] | 0.806 | [0.803, 0.810] |
| richer_targets B1 | 2 | 0.867 | [0.866, 0.869] | 0.868 | [0.865, 0.871] |
| richer_targets B1 | 3 | 0.889 | [0.887, 0.890] | 0.891 | [0.888, 0.893] |
| richer_targets B1 | 4 | 0.876 | [0.874, 0.878] | 0.878 | [0.875, 0.881] |
| richer_targets B1 | 5 | 0.873 | [0.871, 0.875] | 0.873 | [0.870, 0.876] |

**Reading.** Every benchmark's central 90% interval covers less than 90% on this process, and the intervals exclude 0.90 at every lead. `richer_targets.b1_quantiles` is identical to B1. The figures describe this process, not the repository's panel.

Two scratch diagnostics (40 panels, not committed, so not reproducible from the tree) point at the causes:

- **B1.** The anchor is the last public row, one row before the decision day, so a lead-h target is h + 1 rows from it, while §4 and ruling 6 take h-row changes. With h + 1-row changes in a scratch copy, the same measure is between 0.875 and 0.898 across leads. The shortfall is largest at lead 1 (0.804 against about 0.88), where the missing row is the largest share of the gap.
- **B2.** The shortfall sits in the rare types. Per target type at lead 1 the scratch run gave 0.89 for ordinary days, 0.80 for month-end, 0.65 for tax dates and 0.50 for quarter-end. A type has few rows in a trailing year (a handful of quarter-end days), so the sample's 5th and 95th percentiles sit inside the type's true ones.

## Marked questions for Eleonora

1. **B1's definition is hers (ruling 6, #741).** Does B1 keep h-row changes from an anchor that is h + 1 rows before the target, or take h + 1? Nothing here changes it: the departure is reported.
2. Is a benchmark whose central 90% interval covers 80 to 89% on a known process acceptable as the comparator of protocol v1? Coverage is not what a CRPS comparison tests, so this may be no problem; it is her call.

Not checked: the real panel's coverage (finding #744's figure on days to 2025-12-31 was not recomputed); other processes (a regime break, heavier tails); the incumbent B3, whose forecasts come from a recorded run, not a rule.
