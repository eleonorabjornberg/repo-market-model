# H5: the splits the headline pages lacked, and the day 2019-09-18 (#805)

Hypothesis and step: **H5** (primary goal), development steps 1 to 3 of `docs/research/hypotheses/H5.md`: the headline claims of #634 (PR #711) and #707 (PR #756), re-read with the splits those pages promised or `CLAUDE.md` requires. **Development data, not a verdict** (scoring protocol v1, #640; #46 top block). Nothing here registers a candidate, changes a rule, or moves a published figure.

A scratch measurement (`scripts/h5_splits_805.py`). It fits no model: it re-ran #634's 25 walks unchanged on the rebuilt panels (published panel `4ddc3882…`, the declared one) and scored them with the protocol's scorer. **Every pooled figure of #634's tables and #707's remedy tables reproduces exactly** (skill and bound, grid CRPS, upper-tail twCRPS, variant (a) on its own five levels, the Brier means and event counts), so the splits below cut the same numbers. 1,868 decision days, 2018-06-29 to 2025-12-23; no day after 2025-12-31 is read. Studentized stationary bootstrap, block 10, 10,000 draws, one-sided 95%, seeded as the page being reproduced seeds it. Cells: skill [one-sided 95% bounds]. Full tables: `evidence/h5-splits-805/report.md`; data: `score.json`.

## What the finding verified

- Neither #634's page nor #707's carries the split by the type of the decision day's anchor that `docs/research/spike-blind-741.md` promised. B1 centres every lead on the anchor, so after a calendar spike it copies the spike forward.
- #634's upper-tail Brier claim for (c) was pooled only, and no tracked evidence held it by regime or by pressure-day type.

## Skill against B1 by the anchor's day type (grid CRPS)

Anchor types of the 1,868 decision days: ordinary 1,599; month-end 150; tax-date 89; quarter-end 30. The decision day 2019-09-18 is in the tax-date group: its anchor, 2019-09-17, is a tax date by the declared split.

| candidate | pooled | ordinary anchor | month-end anchor | quarter-end anchor | tax-date anchor |
|---|---|---|---|---|---|
| gbm | +20.7% [+13.3%, +40.0%] | **+9.0% [+4.6%, +14.9%]** | +29.1% [+19.9%, +43.5%] | +69.3% [+49.9%, +106.2%] | +69.6% [+19.8%, +196.1%] |
| (a) | +20.2% [+12.4%, +41.9%] | +8.5% [+4.5%, +14.2%] | +30.7% [+20.8%, +51.1%] | +64.2% [+39.5%, +116.5%] | +69.3% [+19.7%, +208.4%] |
| (b) | +20.1% [+12.3%, +41.4%] | +8.3% [+4.1%, +14.2%] | +30.8% [+21.0%, +48.6%] | +64.9% [+42.3%, +110.6%] | +69.5% [+17.4%, +200.1%] |
| (c) | +20.3% [+11.0%, +38.0%] | **+9.0% [+2.9%, +15.8%]** | +31.6% [+16.5%, +49.7%] | +69.2% [+56.7%, +83.5%] | +64.7% [+14.4%, +182.8%] |

**Reading.** The headline of about +20% against B1 is not an ordinary-day figure. On the 1,599 decision days whose anchor is an ordinary day, the four candidates are ahead of B1 by about +9% (the intervals exclude zero), and the gain concentrates on days that follow a calendar spike, where B1 carries the spike forward. The gain on ordinary-anchor days is real and resolved; it is less than half the pooled one. Whether declining to copy calendar spikes alone reaches the pooled figure is #741's question (B1 re-centred), not answered here. The same cut against B2, the upper-tail twCRPS and #707's three remedies are in the report; the shrink remedy is +14.5% [+9.8%, +19.4%] on ordinary-anchor days for (c) and +9.7% [+5.9%, +14.2%] for the gbm.

## Skill against B1 without decision day 2019-09-18

The day's anchor is 2019-09-17, a +315 bp spread day. B1's grid CRPS on 2019-09-18 is 297.6 bp, 6.9% of the sum of B1's 1,868 day scores. The candidates' scores that day come from the re-run walks, not an approximation: gbm 3.63, (a) 3.89, (b) 3.55, (c) 5.25 (B2 6.94). (The finding assumed 7 to 10; its result barely depended on it.)

| grid CRPS against B1 | with the day | without the day | change |
|---|---|---|---|
| gbm | +20.7% [+13.3%, +40.0%] | +14.9% [+10.3%, +21.3%] | −5.8 points |
| (a) | +20.2% [+12.4%, +41.9%] | +14.3% [+9.9%, +20.5%] | −5.9 |
| (b) | +20.1% [+12.3%, +41.4%] | +14.2% [+9.6%, +21.0%] | −5.9 |
| (c) | +20.3% [+11.0%, +38.0%] | +14.5% [+7.7%, +22.2%] | −5.8 |
| upper-tail twCRPS, gbm | +31.3% [+22.1%, +50.4%] | +22.5% [+13.7%, +32.2%] | −8.8 |
| upper-tail twCRPS, (c) | +35.7% [+26.3%, +51.6%] | +27.6% [+17.5%, +37.4%] | −8.1 |
| (a) on its own five levels, CRPS | +21.1% [+13.4%, +42.4%] | +15.4% [+10.9%, +21.5%] | −5.7 |

The finding's figures stand: about +15.0% for the gbm and +14.6% for (c). The skill stays resolved above zero without the day; the upper bounds, which the day inflated, fall from +40% to about +21%. Within the tax-date anchor group the skill without the day is +26.6% [−15.3%, +57.2%] (gbm) and +15.2% [−35.9%, +44.8%] (c): the group's resolved gain rests on that one day. #707's 2021-23 diagnoses are unaffected (the day is in 2018-19); its pooled remedy figures lose about the same 5.8 points (gbm+shrink +20.9% → +15.5%, (c)+shrink +23.9% → +19.9%).

## The upper-tail Brier claim, by regime and pressure-day type

#634's page says (c) has the lowest Brier score for P(> +5 bp) and P(> +10 bp), each with an interval above persistence-logistic and climatology. Pooled that holds, and holds without the day: P(> +5 bp) +19.0% [+13.7%, +23.7%] against persistence-logistic and +30.8% [+23.5%, +37.8%] against climatology; P(> +10 bp) +12.9% [+8.1%, +17.6%] and +18.2% [+10.3%, +25.2%]. Event counts decide how far it travels (event cells of P(> +5 bp) | P(> +10 bp)):

- **2018-19 holds most of the events:** 501 of 681 | 190 of 293 event cells. **2021-23 has none** (both thresholds), so no claim exists there. 2020 has 20 | 15, 2024 25 | 10, 2025-26 135 | 78.
- **By regime, P(> +5 bp):** the interval is above both benchmarks in 2018-19 (+14.7% [+8.3%, +20.1%], +16.6% [+9.9%, +23.0%]) and 2025-26 (+22.1% [+8.1%, +32.3%], +31.3% [+22.6%, +39.9%]); in 2024 only against persistence-logistic (+13.2% [+0.2%, +23.0%]; against climatology [−55.9%, +43.9%]); in 2020 neither.
- **By regime, P(> +10 bp):** above both in 2025-26 only; in 2018-19 above persistence-logistic (+11.5% [+5.1%, +17.5%]) but not climatology (+8.4% [−3.1%, +17.8%]); in 2024 and 2020 neither (2024: −0.5% [−3.9%, +4.6%] against persistence-logistic, where (c)'s score 0.0082 is not the lowest, persistence-logistic's 0.0081 is).
- **By target day type, P(> +5 bp):** above both on month-end and tax-date targets and on ordinary targets (+13.5% [+6.6%, +19.6%], +25.6% [+18.5%, +32.1%]); on quarter-end targets above persistence-logistic only (36 event cells). **P(> +10 bp):** above both on month-end and ordinary targets (+7.5% [+1.0%, +13.0%], +10.1% [+3.4%, +15.9%]); not on tax-date targets (+4.2% [−21.7%, +20.4%]); quarter-end against persistence-logistic only.

So the claim is true pooled and true in the two regimes with most events, but not "each with an interval above" in every regime or day type; the gain in 2018-19 against climatology at +10 bp, in 2020 and in 2024 is unresolved, and 2021-23 cannot speak to it.

## The calibrated critical value, with and without the day

`sp.calibrate_critical_value`, 20,000 windows, seed 1, the 1,868-day pool of S(B2) − S(B1) and its negative (the pool the pages score, to 2025-12-23; the values in force were calibrated on development days to 2026-09-03, so all-day values differ a little: 3.400 and 2.497 here against 3.419 and 2.426 in force).

| pool | series | c at 125 days | c at 250 days |
|---|---|---|---|
| all days | S(B2) − S(B1) | 3.400 | 2.497 |
| all days | S(B1) − S(B2) | 2.565 | 1.342 |
| without 2019-09-18 | S(B2) − S(B1) | 2.914 | 1.926 |
| without 2019-09-18 | S(B1) − S(B2) | 3.394 | 1.866 |

The finding's table is reproduced. At 250 days the gap between the orientations is 1.15 with the day and 0.06 without it; at 125 days the order reverses (2.565 against 3.400 becomes 3.394 against 2.914). The asymmetry between orientations rests on that one day. B1, the critical value in force (ruling 5) and the MME are unchanged: they are Eleonora's, and this page leaves them to her.

**A correction to the finding.** Its last bullet says the re-centred B1 of #741 still copies 2019-09-17 because that day "was not a calendar day". The declared split classes 2019-09-17 as a tax date (`SplitDeclaration.reporting_day_type`), and `b1_recentred_forecast` steps back past every anchor that is not ordinary, so on 2019-09-18 the re-centred B1 does not copy the +315 bp spike. #741's figures are therefore not subject to this day in the way the finding supposed; they are not re-read here.

## Variant count

None new: nine variants as in #634 (re-run, not refitted differently), three post-hoc transforms as in #707.

## Not checked, or for Eleonora

- The mean-reversion headline of #761 (PR #767), which the finding also names, is not on the pages of #634 or #707 and is not re-run here.
- Whether the ordinary-anchor figures change the reading of the pooled headline for a desk is for Eleonora; no rule changes. B1, the critical value and the MME stay as they are.
- A group with fewer than 20 decision days is counted and not tested (none arose in the anchor cuts). The Brier tests need an event in the group; event cells and days are printed beside every figure.
- The outcome is the panel's `spread_bps` (protocol §11). No day after 2025-12-31 is read.
- No published figure moves, so nothing is republished (`docs/decisions/publish-rule.md`) and no "Publish?" issue arises. The pages of #634 and #707 are left as they are; this page carries the splits.
