# History, consolidated: 7–30 September 2026

This file consolidates the project's round log, error log and handoff up to the pivot. The raw logs
stay, frozen, in the Cowork project "v2 Model Repo Market" (`claude/round-log.md`,
`claude/error-log.md`). They are not copied here because they transcribe suite sizes, which
`tests/test_docs_freshness.py` rightly refuses in published Markdown. Git history is the record of
what changed. This file is the record of what it meant.

## 1. What was built, and still stands

- **A point-in-time data layer.** Checksummed snapshots from the NY Fed, FRED/ALFRED, Treasury and
  FR 2004. Every field has a declared release lag and availability instant. There is a panel builder
  with explicit rules for holes, settlement zeros (rule 8) and bounded weekly carries (rule 10), and
  its manifest is digest-bound. The published panel rebuilds from tracked fixtures in seconds and
  reproduces digest `d8b716cf`.
- **An evaluation stack:**
  - purged rolling-origin splits;
  - persistence, climatology, ARX, GARCH, gbm quantile and exceedance models;
  - conformal and CV+ calibration;
  - CRPS, threshold-weighted CRPS, Brier decompositions and stationary-bootstrap comparisons;
  - event holdouts for September 2019 and March 2020.
- **Reproducibility machinery:**
  - provenance on every record;
  - seeds recomputable from the record's own fields;
  - pages generated from records (`scripts/emit_results.py`) and guarded by `test_generated_results`;
  - a docs guard against transcribed counts, future dates and broken commands.
- **The leakage guarantee.** No published record used information unavailable at its decision instant.

## 2. What was measured, and where it stands after the pivot

Every model figure below was scored with inputs read 4–5 business days before the scored day. See
[`lag-assessment.md`](lag-assessment.md).

| Finding (as published or reported) | Status now |
|---|---|
| gbm beats persistence on MAE/CRPS | **Re-measure.** Both sides were handicapped. As-of persistence beats every published backtest on MAE (scouting) |
| Funding columns: −11% threshold-weighted CRPS, paired interval excluding zero | **Direction likely holds, size unknown.** Re-score under the as-of rule |
| The settlement split helps a little (−0.7% twCRPS) | **Re-measure.** Scouting finds scheduled settlements at T worth −3% MAE |
| Calendar columns first helped (13 Sep), then hurt (15 Sep) | **Void as tests.** The calendar was read a week early |
| Dealer positions scored worse than leaving them out | **Confounded.** Declaring them widened the purge and staled every input |
| ARX, GARCH and lags make the exceedance metric worse | **Re-measure.** They were computed from the stale row |
| Calibration: conformal dominated by CV+; 2022's "4 bp location bias" is the split; asymmetric variants retired; partial scaling interpolates by tercile | **Re-measure before any verdict is repeated.** The raw bands are flat by tercile in scouting under both rules, so the tercile pattern comes from, or is exposed by, the calibration layer on the stale design |
| The tail: probability zero at ≥ 50 bp on many days; the GPD fits only from 2024; 2022–23 has zero excesses; B44's refusal rule | **Re-measure.** The ≥ 50 bp tail also leaves the headline (4 days in 8 years) |
| Phase 2: interval criterion "met", tail clause "fails / held" | **Suspended** pending the re-score |
| 2025 weakness is the market (TGCR − IORB volatility), not the panel | **Stands** as a data fact. The model reading needs re-measuring |
| The `on_rrp_h41` side run refused on publication timing | **Resolved by the rule.** Under the as-of rule the print is admissible from the first decision after it |

## 3. Lessons that remain in force

These survive the workflow change. Each lives where it is enforced.

1. **Suspect the probe first.** In the old logs, the probe was more often wrong than the thing it
   measured. A probe that judges a published artifact first reproduces that artifact's own value as a
   control. The pivot's scouting did this: persistence reproduced exactly.
2. **A guard that has never been seen to fail is a comment.** Assert it against a case it must reject.
   Guards run both ways: leakage *and* staleness (`docs/decisions/information-set.md`).
3. **A regime claim needs per-regime evidence.** An aggregate coverage of 85.5% hid 64.3% beside 95.2%.
   Headline claims are split by regime and pressure-day type (`CLAUDE.md`).
4. **When one change moves two quantities, attribute them before acting on either.** The cheapest
   attribution is a third configuration with one mechanism and not the other.
5. **A number carries the path of the artifact it came from**, or it is labelled "measured once, not
   reproducible".
6. **Records and the pages rendered from them land together.** Generated blocks are never hand-edited
   (`docs/decisions/publish-rule.md`).
7. **Read the manifest before calling a column usable.** "Buildable" is not "carries data".
8. **A gate checks every property its accompanying claim asserts.** "Same panel" means comparing
   `panel.sha256`.
9. **A declaration is part of the result.** Adding a slow series once moved the fold grid and every
   input's staleness. Under the as-of rule the grid is fixed.
10. **Score the pass that can be refused first.** A one-second declaration check comes before an
    hour-long control.
11. **A brief's premise is a claim to check.** A block that refuted its own brief was usually the most
    valuable output of its round.
12. **The design question is not answered by the verification apparatus.** None of the logged failures
    concerned the information set. It was found by asking what a forecaster actually knows at 16:00.

## 4. What the old workflow cost, and what retired it

The error log held about 75 entries.

| Class | ≈ entries | Retired by |
|---|---|---|
| Reach and environment (folder grants on scheduled firings, VM against Mac, sleep, DNS, `index.lock`, moved paths, deny lists) | 22 | cloud sessions on clones |
| Probes and scripts (shell quoting, Linux-isms on macOS, wrong field names, exit codes lost in pipes) | 20 | CI, plus PR review of any script that judges a record |
| Orchestration and serialisation (job order, filename reuse, publish windows, an orphaned half-publish) | 15 | one PR per result; the publish rule |
| State drift (handoff wrong about lane and branch state, stale scheduled prompts) | 9 | PR descriptions and git as the state; `next-session.md` names a check for every claim |
| Wrong brief premises | 8 | briefs cite the file and line they rely on |
| Methodology and inference | 6 | lessons 3, 4, 8 and 9 above |

**Throughput bottlenecks:**
- One gbm scoring run took about 80–90 minutes on the Mac: a daily refit, times five quantile levels, times six fits
  under CV+.
- A single scoring lane.
- A publish window tied to the integration checkout's `HEAD`.
- Round closes in lockstep, with a verification ritual of about 20–25 minutes under contention.
- Ownership walls that turned small changes into human commits.

The same panel builds in seconds in a cloud checkout. A monthly-refit configuration scores in about 90 seconds there.

## 5. Timeline

- **7–9 Sep.** Contract and tracks set up. Milestone A: a frozen panel from real snapshots, with the persistence and
  climatology records.
- **10–11 Sep.** gbm and calibration built. Cross-conformal published. The purge audit under the declared schedules
  was recorded as Phase 2's interval criterion "met".
- **12 Sep.** The tail line: the exceedance curve saturates at zero, the fitted GPD tail is built, and the tail proves
  unmeasurable by the existing commands until B39.
- **13 Sep.** The feature strand is closed negative. The calendar columns are built. The folders move to
  `Desktop/Projects/RM Model`.
- **13–14 Sep.** The rebuild to a dense panel (`d8b716cf`). The fleet is reconstructed. The funding columns enter a
  declaration for the first time: −11% threshold-weighted CRPS.
- **14 Sep.** The coverage round: 2022–23 turns out under-covered, not over. The location bias is attributed to the
  fit-rows-only split.
- **15–16 Sep.** DFF, WRESBAL and WTREGEN lags are corrected. WLRRAOL is priced. The asymmetric calibrations are
  retired. Scaled and partial CV+ are built.
- **16–19 Sep.** Partial scaling is scored. `on_rrp_h41` is refused on publication timing. The lanes stop.
- **30 Sep.** The partial record is published after the orphaned half-publish from 19 Sep is cleared. The checkout
  had by then moved to `Desktop/Projects/Portfolio/RM Model`. **The pivot**: the lag is found and measured. The as-of rule, the
  cloud-and-PR workflow and the publish rule are decided, and the logs are consolidated here.
