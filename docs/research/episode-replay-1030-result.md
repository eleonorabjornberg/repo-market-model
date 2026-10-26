# Per-episode stress replay (#1030)

**Hypothesis and step:** H5 (primary goal), step 6 (the validation report). **Development data, not a verdict** (scoring protocol v1, #640). Nothing is refitted: the published model's quantiles are read from `docs/runs/published_distribution_daily_h1.json`; B1, B2 and B1′ are the protocol's zero-parameter functions of the panel (no record holds their daily quantiles). Lead h = 1, target days; the forecast for a target day is made at 16:00 the business day before. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

Each cell is q05 / q50 / q95 in bp of SOFR − IORB. A **bold** cell is a miss: the print is outside the q05–q95 band. The 2025 year-end turn stops at 2025-12-31, the last unlocked day.

## Calendar status of each row (#1028)

- **Published model:** provisional: calendar not read at the target day (class a+b at lead 1, the register's first row).
- **B1:** provisional: reads no calendar day (a zero-parameter reference; nothing to re-run).
- **B2:** not provisional: reads the target day's reporting type (a zero-parameter reference).
- **B1′:** not provisional: reads the target day's reporting type (a zero-parameter reference).

## 2018 year-end turn (2018-12-26 to 2019-01-03)

| Target day | Print, bp | Published model | B1 | B2 | B1′ |
|---|---|---|---|---|---|
| 2018-12-26 | +4.0 | -6.5 / -0.5 / +9.6 | -5.0 / +0.0 / +5.0 | -8.0 / -2.0 / +5.3 | -4.0 / +0.0 / +5.0 |
| 2018-12-27 | +4.0 | -6.7 / +0.5 / +8.2 | -3.9 / +1.0 / +6.0 | -8.0 / -2.0 / +5.3 | -3.0 / +1.0 / +6.0 |
| 2018-12-28 | +6.0 | -9.3 / +1.0 / +12.4 | -0.9 / +4.0 / +9.0 | -5.1 / -2.0 / +6.7 | +0.0 / +4.0 / +11.9 |
| 2018-12-31 | +60.0 | **-10.1 / +1.0 / +14.1** | **-0.8 / +4.0 / +9.0** | **+5.6 / +11.0 / +16.4** | **+0.0 / +4.0 / +11.8** |
| 2019-01-02 | +75.0 | **-5.9 / +1.0 / +9.0** | **+1.2 / +6.0 / +11.0** | **-8.0 / -2.0 / +5.2** | **+0.0 / +4.0 / +9.0** |
| 2019-01-03 | +30.0 | **-5.4 / +6.2 / +20.8** | **+55.3 / +60.0 / +65.0** | **-8.0 / -2.0 / +5.2** | **+0.0 / +4.0 / +9.0** |

| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |
|---|---|---|---|---|---|
| Published model | 6 | 3 | 0 | 2018-12-31 | 24.2, 14.8, 26.2 |
| B1 | 6 | 2 | 1 | 2018-12-31 | 9.8, 9.8, 9.7 |
| B2 | 6 | 3 | 0 | 2018-12-31 | 10.8, 13.2, 13.2 |
| B1′ | 6 | 3 | 0 | 2018-12-31 | 11.8, 9.0, 9.0 |

## September 2019 (2019-09-16 to 2019-09-18)

| Target day | Print, bp | Published model | B1 | B2 | B1′ |
|---|---|---|---|---|---|
| 2019-09-16 | +33.0 | **+0.3 / +6.5 / +14.4** | **+4.0 / +10.0 / +16.9** | **-1.9 / +6.5 / +11.4** | **+5.1 / +10.0 / +18.9** |
| 2019-09-17 | +315.0 | **+2.2 / +5.9 / +12.0** | **+4.0 / +10.0 / +16.9** | **-1.9 / +6.5 / +11.4** | **+5.1 / +10.0 / +18.9** |
| 2019-09-18 | +45.0 | **+2.5 / +10.4 / +33.3** | **+27.0 / +33.0 / +40.0** | **-1.9 / +8.5 / +21.4** | **+5.2 / +10.0 / +19.0** |

| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |
|---|---|---|---|---|---|
| Published model | 3 | 3 | 0 | 2019-09-16 | 14.1, 9.8, 30.8 |
| B1 | 3 | 3 | 0 | 2019-09-16 | 12.9, 12.9, 13.0 |
| B2 | 3 | 3 | 0 | 2019-09-16 | 13.3, 13.3, 23.3 |
| B1′ | 3 | 3 | 0 | 2019-09-16 | 13.9, 13.8, 13.8 |

## March 2020 (2020-03-11 to 2020-03-17)

| Target day | Print, bp | Published model | B1 | B2 | B1′ |
|---|---|---|---|---|---|
| 2020-03-11 | +5.0 | **-3.8 / -0.2 / +3.3** | -8.9 / -1.0 / +7.0 | -2.0 / +3.0 / +13.3 | **-6.0 / -1.0 / +4.0** |
| 2020-03-12 | +10.0 | **-3.0 / +0.5 / +6.3** | **-6.9 / +1.0 / +9.0** | -2.0 / +3.0 / +13.3 | **-4.0 / +1.0 / +6.0** |
| 2020-03-13 | +0.0 | -2.7 / +1.4 / +5.9 | -2.8 / +5.0 / +13.0 | -2.0 / +3.0 / +13.3 | +0.0 / +5.0 / +10.0 |
| 2020-03-16 | +16.0 | **-0.7 / +3.9 / +9.0** | +2.2 / +10.0 / +18.0 | **-2.0 / +3.0 / +13.3** | **+5.0 / +10.0 / +15.0** |
| 2020-03-17 | +44.0 | **-4.1 / -0.3 / +4.9** | **-8.0 / +0.0 / +8.0** | **-2.0 / +3.0 / +13.4** | **-5.0 / +0.0 / +5.0** |

| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |
|---|---|---|---|---|---|
| Published model | 5 | 4 | 0 | 2020-03-11 | 7.1, 9.4, 8.5, 9.7, 9.0 |
| B1 | 5 | 2 | 0 | 2020-03-12 | 15.9, 15.8, 15.8, 16.0 |
| B2 | 5 | 2 | 0 | 2020-03-16 | 15.3, 15.4 |
| B1′ | 5 | 4 | 0 | 2020-03-11 | 10.0, 10.0, 10.0, 10.0, 10.0 |

## 2024 year-end turn (2024-12-26 to 2025-01-03)

| Target day | Print, bp | Published model | B1 | B2 | B1′ |
|---|---|---|---|---|---|
| 2024-12-26 | +13.0 | **-12.5 / -8.9 / -2.8** | **-11.0 / -9.0 / -7.0** | **-9.0 / -8.0 / -3.0** | **-10.0 / -9.0 / -8.0** |
| 2024-12-27 | +6.0 | **-8.9 / -2.4 / +5.6** | **-2.0 / +0.0 / +2.0** | **-9.0 / -8.0 / -2.6** | **-1.0 / +0.0 / +1.0** |
| 2024-12-30 | -3.0 | -6.1 / +4.1 / +27.3 | **+11.0 / +13.0 / +15.0** | -9.0 / -7.0 / +0.0 | **+11.9 / +13.0 / +17.0** |
| 2024-12-31 | +9.0 | -6.6 / +1.4 / +22.5 | **+4.0 / +6.0 / +8.0** | **-6.9 / -6.0 / +4.8** | **+4.8 / +6.0 / +8.0** |
| 2025-01-02 | +0.0 | -10.7 / -4.6 / +0.4 | **-5.0 / -3.0 / -1.0** | **-9.0 / -8.0 / -1.7** | **+4.3 / +6.0 / +7.7** |
| 2025-01-03 | -9.0 | **-6.3 / +2.2 / +24.9** | **+7.0 / +9.0 / +11.0** | -9.0 / -8.0 / -2.6 | **+4.3 / +6.0 / +7.7** |

| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |
|---|---|---|---|---|---|
| Published model | 6 | 2 | 1 | 2024-12-26 | 9.7, 14.5, 33.3, 29.2, 11.1, 31.2 |
| B1 | 6 | 4 | 2 | 2024-12-26 | 4.0, 4.0, 4.0, 4.0, 4.0, 4.0 |
| B2 | 6 | 4 | 0 | 2024-12-26 | 6.0, 6.4, 9.0, 11.7, 7.4, 6.4 |
| B1′ | 6 | 3 | 3 | 2024-12-26 | 2.0, 2.0, 5.1, 3.2, 3.4, 3.4 |

## 2025 year-end turn (2025-12-26 to 2025-12-31)

| Target day | Print, bp | Published model | B1 | B2 | B1′ |
|---|---|---|---|---|---|
| 2025-12-26 | +11.0 | **-4.9 / +1.7 / +7.7** | **-4.0 / +1.0 / +6.0** | **-12.0 / -5.0 / +10.0** | **-3.0 / +1.0 / +5.0** |
| 2025-12-29 | +12.0 | **-3.8 / +1.7 / +10.9** | **-4.0 / +1.0 / +6.0** | **-12.0 / -5.0 / +10.0** | **-3.0 / +1.0 / +5.0** |
| 2025-12-30 | +6.0 | -1.1 / +7.1 / +18.5 | +6.0 / +11.0 / +16.0 | -7.1 / -2.5 / +22.5 | **+7.9 / +12.0 / +19.3** |
| 2025-12-31 | +22.0 | -1.6 / +9.5 / +22.1 | **+7.0 / +12.0 / +17.0** | **+1.6 / +7.0 / +9.0** | **+8.0 / +12.0 / +17.0** |

| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |
|---|---|---|---|---|---|
| Published model | 4 | 2 | 0 | 2025-12-26 | 12.6, 14.8, 19.5, 23.7 |
| B1 | 4 | 3 | 0 | 2025-12-26 | 10.0, 10.0, 10.0, 10.0 |
| B2 | 4 | 3 | 0 | 2025-12-26 | 22.0, 22.0, 29.6, 7.4 |
| B1′ | 4 | 3 | 1 | 2025-12-26 | 8.0, 8.0, 11.4, 9.0 |

## Lens D's reading, against the tables (published model)

| Episode | Days | Print above q95 | Band wider on a later day than on the first-miss day |
|---|---|---|---|
| 2018 year-end turn | 6 | 3 | yes |
| September 2019 | 3 | 3 | yes |
| March 2020 | 5 | 4 | yes |
| 2024 year-end turn | 6 | 2 | yes |
| 2025 year-end turn | 4 | 2 | yes |

The reading is that on every onset the q95 sat below the print and the band widened after the first miss. Where a row above shows otherwise, the reading does not hold for that episode.

## What this shows, and does not

- It replays the days the directive names, from records already on main. It scores nothing, ranks nothing and decides nothing: three or four days per episode, and episodes chosen because they were stress days.
- The published row and B1 read no calendar day at the target day; B2 and B1′ read the target day's reporting type. A miss by a row marked provisional is not evidence about a calendar-aware model.
- The episode windows are the directive's dates for September 2019 and March 2020; the year-end windows (26 December to 3 January) are this study's choice, pinned in `tests/test_episode_replay_1030.py`.
