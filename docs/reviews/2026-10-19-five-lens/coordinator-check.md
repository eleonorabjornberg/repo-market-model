# Coordinator's check (independent of the five reviewers)

Performed 2026-10-19 ~15:10 ET on the same clone (`ddaf391e`) and the verified panel (digest `4ddc3882…`).

## Read-only compliance
- `git status --porcelain` empty in both clones; HEADs unchanged (`ddaf391e`, `b216a8bc`); branch `main`; no stash. No GitHub API write was possible from the container (the proxy refused even reads; an attach with credentials was blocked by the permission classifier and not retried). No issue, PR or comment was created.
- Issue list: titles for #1–#942 fetched read-only via the owner's Chrome; bodies for 553 issues from the owner's `gh issue list` export (to #951). Nine items (#943–#951) were opened today after the title fetch; reviewers were told before finalising.

## Numbers re-derived by the coordinator (one-line pandas on the panel unless stated)
| claim (lens) | reviewer | coordinator | verdict |
|---|---|---|---|
| Non-quarter-end months 2018–19: 2nd-last bday mean / share > 5 bp; last; first next (A) | +0.3 / 7%; +11.5 / 71%; +8.1 / 57% | +0.3 / 7%; +11.5 / 71%; +10.3 / 64% (first-day definition differs slightly) | verified in substance |
| Same, 2024-09..2026-09 (A) | −1.5 / 12%; +2.7 / 12%; +2.1 / 20% | −1.4 / 12%; +2.6 / 12%; +2.6 / 18% | verified |
| Quarter-end months: 2nd-last −4.6 / 9%, last +2.9 / 26% (A) | | −4.7 / 9%; +2.9 / 27% | verified |
| 2019-10-15 and 2025-10-15 not tax dates; prints +25 / +15 (A) | | tax_date = 0 on both; 2019-10-15 +20, 2019-10-16 +25; 2025-10-15 +14 | verified (reviewer quoted the 15th–17th maximum) |
| `MONTH_END_BUSINESS_DAYS = 2` data.py:2647; `RUN_UP_DAYS = 3` balance_sheet_days.py:46; `TAX_DEADLINE_MONTHS = (4,6,9,12)` data.py:2769 (A) | | all three lines read as cited | verified |
| No 2024-11-25 SOFR-methodology event and no 2025-06-26 SRF morning-operation event in `metadata/policy_events.json` (A) | | grep finds neither (only `slr-20250627`) | verified |
| 2021–23: variance 5.7 bp², 70% zero-change days, lag-1 AC 0.935, 46% at −10 bp (B) | | 5.73; 70.3%; 0.935; 46% | verified |
| `satiation.fit_level` is a least-squares hinge on all pairs (B, satiation.py:153-207) | | lines read as cited | verified |
| Protocol §11: >5% missing voids the registration (B) | | scoring-protocol.md:257 | verified |
| `policy_features.py` reads only qt_start/qt_taper/qt_end; 7 `balance_sheet` entries, none QE (B) | | lines 90–91; 7 entries; no QE string | verified |
| Spread integer on all rows; mass −10: 372, −9: 268, 0: 148, −1: 144 (C) | | identical | verified |
| Episodes ≥ +5 / +10 / +20 bp with gap > 10: 17 / 15 / 11; 28 IORB steps (C) | | identical | verified |
| GRID 23 levels; BLOCK_LENGTH, WINDOW_BLOCK, HAC_LAG = 10; circular blocks at scoring_protocol.py:702-707 (C) | | lines read as cited | verified |
| Protocol lists coverage/PIT as "reported, not decision rules" (D, scoring-protocol.md:194-197) | | verbatim | verified |
| Candidate 90% band 0.695, 50% band 0.307; B3 0.886; CRPS −0.9% [−2.7%, +0.8%] (D) | | report.md:335-336 and result.md:36 read as cited | verified |
| Published PID h=1: 211/1873 misses, LR_uc 3.2, LR_ind 143, P(miss|miss) 0.40 vs 0.075 (D) | | recomputed from `docs/runs/published_distribution_daily_h1.json`: identical | verified |
| `live_score.py` scoring dates 2027-04-01, 2027-10-01, then each 1 October (D) | | lines 6–12, 125 | verified |
| Candidate features list (D, final_test_preregistration.py:837-838) | | verbatim | verified |
| 4-week bill level vs next-day spread: +0.12 (2018–19), −0.46 (2024), −0.41 (2025–26) (D) | | +0.12, −0.44, −0.41 | verified |
| OFR: "preliminary release is published daily at 3 p.m."; cleared repo "one-day lag"; tri-party "two-day lag" (E) | | fetched today, verbatim | verified |
| DTCC fact sheet: posted "at approximately 3:30 p.m. EST"; website shows 12 months (E) | | fetched today, verbatim | verified |
| `sources.json:635-643` declares OFR at 16:00 + 2 business days (E) | | verbatim | verified |
| OFR `REPO-GCF_AR_OO-P` null on 1,847 of 2,102 days (E) | | snapshot `…6c8f58bd04f0.json`: 2102 points, 1847 null | verified |
| DTCC blocked in due diligence for want of a publication instant (E, new-sources-due-diligence.md:33) | | verbatim | verified |
| `contract.py:298-299` maps reserves/TGA to WRESBAL/WTREGEN; information-set.md:31-33 says "Wednesday level" (E) | | verbatim | verified |

## Not re-derived (taken as the reviewer's computation, each marked so in its report)
- Lens A's gross-vs-net Spearman correlations (uses the repo's `net_for_day`), the DVP-premium decomposition.
- Lens B's +1.3% / +2.6% B1-pool replication (its own CRPS, not the grid scorer).
- Lens C's B1′ (+15.6%), ACF 0.73, Politis–White 108, and the 6.05 / 2.93 / 2.37 generator percentiles (on a B1/B2 proxy of the d series, not gbm_funding's actual walks).
- Lens E's 144-day GCF pilot (stress-tilted sample, crude bias; the reviewer says so).

## Already-raised compliance
None of the nine excluded items is proposed as new. Items filed today (#947–#951, #950's parked list, #941's extended scope) are marked "already tracked" wherever touched; where a reviewer re-assesses a parked item it is labelled as such and not counted among its five.
