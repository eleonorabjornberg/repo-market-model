# Scouting: the lag

These are not records. They are the scripts behind the numbers in `docs/pivot/lag-assessment.md`. They were written
to decide whether the as-of redesign was worth building, and they sit outside `scripts/` on purpose: they use pandas
and scikit-learn directly, and `scripts/` is held to the standard library by `tests/test_dependency_boundary.py`.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
mkdir -p /tmp/scout && OMP_NUM_THREADS=1 python3 notebooks/scouting/lag_scout.py /tmp/funding_panel.csv /tmp/scout
python3 notebooks/scouting/lag_analyze.py /tmp/funding_panel.csv /tmp/scout
```

`lag_scout.py` scores every design, 12 jobs of about 20–100 seconds each on one thread. It takes optional job tags,
so it can be split across workers. `lag_analyze.py` prints the tables. The output recorded for the assessment
follows. It was produced with scikit-learn 1.8, so expect small differences under the pinned version.

```
== point/quantile (MAE bp by slice; pinball; raw q05-q95 coverage, below/above miss)
                                      all  2018-19     2020  2021-23     2024  2025-26    press  pinball  cov90  below  above  calm/mid/stress cov
persistence pub rule                3.104    7.446    2.092    0.897    2.112    4.392    5.034
persistence as-of                   2.509    6.487    1.606    0.610    1.824    3.318    4.704
pub4__onestep__q                    2.623    5.049    1.881    1.169    1.978    3.897    5.241    0.995  0.671  0.209  0.119  0.70/0.67/0.65
pub4__direct__q                     2.794    5.518    2.138    1.369    1.902    3.848    5.505    1.010  0.726  0.167  0.106  0.74/0.73/0.71
asof4__onestep__q                   2.342    4.887    1.664    1.067    1.730    3.133    5.112    0.861  0.711  0.199  0.090  0.70/0.73/0.70
asof4__direct__q                    2.454    5.153    1.689    1.159    1.720    3.268    5.206    0.880  0.759  0.158  0.083  0.74/0.77/0.76
pub_full_calpub__direct__q          2.565    5.098    2.165    1.214    1.768    3.445    5.047    0.948  0.693  0.172  0.134  0.71/0.66/0.71
asof_full_nocal__direct__q          2.422    5.117    1.809    1.146    1.652    3.138    5.028    0.874  0.732  0.165  0.103  0.70/0.74/0.75
asof_full_calpub__direct__q         2.326    5.066    1.833    1.076    1.514    2.907    4.816    0.844  0.717  0.178  0.105  0.69/0.74/0.72
asof_full_calT__direct__q           2.344    5.125    1.780    1.088    1.517    2.948    4.910    0.838  0.751  0.155  0.094  0.76/0.74/0.76
asof_full_calT_setT__direct__q      2.268    4.937    1.838    1.037    1.496    2.817    4.674    0.818  0.753  0.163  0.083  0.75/0.76/0.75

== pressure probability: event = SOFR-IORB >= thr on the scored day
-- thr 5 bp: events on 163 of 2039 scored days (34 on pressure days)
                                     Brier     BSS   AUROC AUROC 25-26 Brier press AUROC press
climatology (expanding)             0.0740   0.000   0.607       0.478      0.1232       0.532
persistence-logit pub rule          0.0623   0.158   0.857       0.853      0.1091       0.847
persistence-logit as-of             0.0531   0.281   0.917       0.909      0.0972       0.884
pub_full_calpub__direct__cls        0.0679   0.082   0.880       0.760      0.1107       0.854
asof_full_calT__direct__cls         0.0698   0.056   0.905       0.859      0.0918       0.869
asof_full_calT_setT__direct__cls    0.0637   0.139   0.909       0.840      0.0829       0.905
-- thr 10 bp: events on 70 of 2039 scored days (20 on pressure days)
                                     Brier     BSS   AUROC AUROC 25-26 Brier press AUROC press
climatology (expanding)             0.0333   0.000   0.546       0.469      0.0798       0.508
persistence-logit pub rule          0.0329   0.012   0.753       0.812      0.0782       0.734
persistence-logit as-of             0.0303   0.090   0.820       0.914      0.0725       0.748
pub_full_calpub__direct__cls        0.0379  -0.138   0.824       0.761      0.0825       0.763
asof_full_calT__direct__cls         0.0342  -0.026   0.827       0.857      0.0806       0.737
asof_full_calT_setT__direct__cls    0.0322   0.032   0.844       0.903      0.0685       0.790

== P(>=5bp) around the two episodes
      date  spread  persistence-logit   pub_full_calpub  asof_full_calT_set
2019-09-12    10.0                0.29             0.04                0.83
2019-09-13    10.0                0.34             0.02                0.36
2019-09-16    33.0                0.57             0.18                0.98
2019-09-17   315.0                0.57             0.09                0.70
2019-09-18    45.0                0.99             0.05                0.96
2019-09-19    15.0                1.00             0.03                0.94
      date  spread  persistence-logit   pub_full_calpub  asof_full_calT_set
2025-10-27    12.0                0.48             0.00                0.00
2025-10-28    16.0                0.48             0.00                0.00
2025-10-29    12.0                0.66             0.04                0.17
2025-10-30    14.0                0.84             0.23                0.18
2025-10-31    32.0                0.66             0.09                0.96
2025-11-03    23.0                0.76             0.01                0.31
```
