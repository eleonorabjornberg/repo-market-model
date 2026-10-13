# Partly announced bill classes: audit, diagnosis and remedy (#679)

**This is a change of data meaning.** A class (the bill types or the coupon types) with some auctions announced by the
decision instant and others settling the same day not yet is now **left out** of every `net_settlement_*` column until it is
fully announced. Before, it netted its announced offerings against nothing maturing (#620, PR #647). The columns are off in every
published declaration, so no published figure moves. Serves H2 (the data we hold) and H5's inputs.

Figures are from `scripts/partly_announced_679.py` on the tracked fixture
(`tests/fixtures/snapshots/net_settlement_inputs/treasury_auctions/20261008T205048Z_568c69347867.json`); the tables are
committed in `docs/pivot/evidence/partly-announced/audit.md` and `audit.json`. Error is a rule's net less the completed day's net,
USD billion.

## 1. Audit: which figures are right

**#665's reproduce exactly.** Over the 117 (day, lead 2 to 5) cases where the old rule and #647's rule differ: #647's rule +83.2 mean
error, 85.7 MAE; the old rule -50.6 / 50.6; the class left out -28.4 / 37.2. (121 cases have a partly announced class; in 4 no
maturing figure was announced, so the old rule and #647's agree.) These are the cases the net columns read: a decision day, the
five settlement days after it, one lead each.

**#647's do not reproduce.** The PR reports 238 groups (old -136 / 136, announced offering alone -25 / 58, class left out -64 / 67).
That measurement is not tracked, and no decision-day definition rebuilds it:

| decision days | groups | announced MAE | left out MAE | old MAE |
|---|---|---|---|---|
| each announcement date of the class | 167 | 60.4 | 57.1 | 104.6 |
| business days within 5 of settlement (the leads the columns read) | 121 | 83.9 | 38.5 | 50.0 |
| business days within 10 of settlement | 464 | 56.5 | 59.8 | 107.3 |

Why they differ: #647's measure is a per-class group error pooled over decision days that can include leads beyond 5, which no
column reads; #665's measure is the day-lead case the model reads. The #647 population itself is not recoverable. Restricted to the leads the model reads (rows 2), leaving the class out wins by a wide margin; with groups out to 10 business
days (row 3) #647's ordering, announced offering alone ahead, appears. The PR's "67 against 58" is on neither.

## 2. Diagnosis: the 2018 concentration at h = 4 and 5

80 of the 121 partly announced cases are in 2018 at h = 4 and 5. In 2018 Treasury announced the 13- and 26-week bills on a Thursday
for the Thursday a week later (five business days out) and the 4- and 8-week bills on the Monday before that Thursday (three days
out). On the Friday, Saturday-Monday decision days of that week, and the Thursday before, the bill class held the two large
13- and 26-week offerings and not the 4-week; the maturing figure, one total for the whole class, was then netted against part of the
offering (old rule), or not at all (#647's rule, which reads the 90 announced as a 90 bn drain).

Worst cases (decision day, lead 4; `audit.md` has them all):

| settles | completed net | old | #647 rule | left out | what is late |
|---|---|---|---|---|---|
| 2018-10-04 | -15 | -55 | +90 | 0 | 4-week, announced Monday 2018-10-01 |
| 2021-10-07 | -2 | -27 | +118 | 0 | 8-day cash management bill, announced Monday 2021-10-04 |
| 2023-08-22 | 34.3 | 34.3 | +200 | 0 | 7-day cash management bill, announced Thursday 2023-08-17 |
| 2024-11-26 | 49 | 9 | +249 | 0 | 30-day cash management bill, announced Thursday 2024-11-21 |
| 2025-04-08 | 36 | -14 | +215 | 0 | 14-day cash management bill, announced Thursday 2025-04-03 |

In the later cases above the late piece is a small cash management bill; the regular 4-, 8- and 17-week bills are announced on the Tuesday before. Then
#647's rule reads the whole regular offering (200 to 250 bn) as a drain with nothing maturing.

## 3. Remedy

Per lead, mean absolute error against the completed net, cases with a partly announced class:

| lead | n | old | #647 rule | left out |
|---|---|---|---|---|
| 1 | 0 | | | |
| 2 | 2 | 55.0 | **41.8** | 70.7 |
| 3 | 10 | **46.5** | 53.5 | 80.0 |
| 4 | 55 | 49.1 | 87.7 | **32.8** |
| 5 | 54 | 51.7 | 87.5 | **35.9** |

Overall (leads 2 to 5, rules differing): left out 37.2, old 50.6, #647's rule 85.7. **The overall winner is leaving the class out
until it is fully announced**, which `net_settlement.net_for_day` now does (test first:
`PartlyAnnouncedTests`, recorded mutation in `tests/test_net_settlement.py`).

**Marked question for Eleonora (not settled in code):** at leads 2 and 3 another rule wins (#647's rule at lead 2 on two cases; the old rule
at lead 3 on ten). The samples are too small to read, and 109 of the 121 cases are at leads 4 and 5. Whether the rule should
differ by lead is her call. A second, larger question: by year, leaving out wins in 2018 (MAE 21.5 against 52.3 for the old rule) and
loses in 2020 (103.1 against 58.3), and the old rule has the smallest error in 2023 to 2025 (15.8, 40.0, 50.0 against 32.7, 49.0, 36.0;
n = 5, 2, 2). In the later years inspected (above) the late piece is a small cash management bill and the old rule is nearer. Those years are too few to choose a rule on, and a rule
that depends on the size of the late piece would use something not known at the instant.

## 4. What the change moves

No published record, declaration or page reads these columns (`docs/runs/`, `metadata/sources.json` and `metadata/pressure_judge.json`
carry none), so nothing published is re-published. The pivot evidence that reads them:

| evidence | status |
|---|---|
| structural liquidity (#542), projected reserves (#545), combined model (#561) | re-scored here: `docs/pivot/partly-announced-679-result.md` |
| `satiation` projected and structural rows (#587), kinked elasticity (#626) | read the columns; not re-scored here, need a re-run |
| source screen and source matrix (#629), derived features (#631), unused inputs, unwarned onsets, pressure audit, all inputs, weighted miss | read the columns; not re-scored here, need a re-run |
| `hierarchical_logistic_net`, `onset_logistic_net+recalibrated` and the #426 evidence | read the columns; not re-scored here |

#647's verdict changes, after the re-score (weighted rule in force): `structural_liquidity` tier 3 no to yes **survives**
(tiers 1 / 3 / 5 still no / yes / yes); `risk_gbm+structural` tier 3 no to yes **survives**, and its onsets stay at 15 of 26 (not 11);
no row passes either way. The two #647 combined-model changes (`risk_gbm+combined_nogate` and the `every_day+gate+settle+h41` control, tier 1 yes to
no) are not moved by this change. `projected_reserves` goes 12 to 11 of 26 onsets; no tier changes.
Files outside the re-scored three still carry #647's rule until re-run.
