# Draft: a monitoring read of the live record, decoupled from verdict scoring (#969)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #969, as that directive asks
(five-lens review, Lens D, #958). It takes effect only when she moves it to `docs/decisions/live-monitoring.md`
herself. The lockbox and the live record are owner-attested (#256): nothing in this pull request reads a locked
outcome, and `repo_model.live_monitor.require_decision_record` refuses to until that file exists outside `drafts/`.

## Why

The live record is frozen, chained and anchored, and written before any outcome. Its only reader,
`scripts/live_score.py`, runs on 2027-04-01, 2027-10-01 and each 1 October after, refuses every locked day, and
computes CRPS and Brier cells. The earliest anyone could learn that the live model is mis-calibrated is therefore
2027-04-01. A bank's model-risk standard (SR 11-7) separates *monitoring*, which reads outcomes as they print, from
*evidence*, which the lockbox protects. This record makes the first possible without touching the second.

## The rule, as drafted

---

## Decision: the monitoring read of the live record (#969)

**Decided by Eleonora on the date this file is moved into `docs/decisions/`.**

- **A monitoring read is not a "comparison" in the sense of `lockbox.md`.** It chooses no candidate, declaration,
  feature or setting, scores nothing against a benchmark for a verdict, and opens no tier. A tier is opened only as
  `lockbox.md` and `metadata/lockbox.json` say, by her.
- **What it may compute and publish, and nothing else:** per lead, the rolling 60-day coverage of the 90% band; the
  125-day Kupiec and Christoffersen tests at q95; the 6-bin PIT and the share at or below q25; the ratio of the
  published distribution's CRPS to B1's and to B2's; per-source input staleness against `metadata/sources.json`;
  and the pin check against `metadata/live_pin.json`. It runs no new forecast. Every output carries the label
  "monitoring, not evidence" and `decides: nothing`.
- **It carries no verdict and is cited only as a trigger.** A monitoring figure is never a result in a research-log
  entry, a result page or a pull request's evidence table, and never decides which model joins or leaves the live
  record. A flag may prompt her to review; what follows is a new candidate, evaluated prospectively on days the
  flag did not use, under the scoring protocol.
- **The verdict is unchanged.** `scripts/live_score.py`, its scoring dates, its primary result and the blind gap
  are as `live-scoring-declaration.md` and the lockbox amendment say. The monitoring read neither replaces nor
  precedes them as evidence.
- **The read is available only while this record is in `docs/decisions/`.** If she removes it, the job refuses
  again.
- **Thresholds are not part of this decision** unless she adds them (see the questions).

---

## Thresholds, as proposals only

`metadata/live_monitoring_969.json` holds the directive author's proposals, which Lens D's own amber and stop
thresholds (#958) would replace; #950 row 8 stays parked for her. The replay on the published model's development
days to 2025-12-31 (`docs/research/live-monitoring-969-result.md`) shows what they would have shown, and that they do
not discriminate: at least one flag is set on most days.

| figure (per lead) | amber | stop |
|---|---|---|
| 60-day 90% band coverage | below 0.80 or above 0.98 | below 0.70 |
| Kupiec at q95, 125 days | p below 0.01 | both tests below 0.01 on the same day |
| Christoffersen at q95, 125 days | p below 0.01 | (as above) |
| share at or below q25, 125 days | outside [0.15, 0.35] | none |
| CRPS ratio to B1, 125 days | above 1.0 | above 1.1 |
| input staleness | a source older than its worst-case lag | none |
| pin check | none | a record at an unregistered pin |

## Questions for Eleonora (marked; not settled in code)

1. **Is reading a blind-tier outcome for monitoring, before the scoring date, a "comparison" under `lockbox.md`?**
   This draft says it is not, on the conditions above (reported only, no verdict, cited only as a trigger). The
   risk it accepts: a flag could lead to a change of model, and a change made after seeing blind days would make
   those days no longer blind. The draft's answer is that such a change is a new candidate scored only on days the
   flag did not use. If she judges the risk too large, the read could be limited to coverage and plumbing, without
   the CRPS ratio.
2. **Cadence and place.** This pull request adds no workflow and no schedule. Whether the job runs daily or weekly,
   and where its output is published, is hers.
3. **Thresholds.** Whether to adopt any, and Lens D's or these. The replay says these fire too often to be a stop
   rule.
