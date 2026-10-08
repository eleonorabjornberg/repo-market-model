# Draft amendment to `lockbox.md`: the live record

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #215, as that directive
asks, amended by the ones that close #277, #257 and #245 (pressure model v2). It takes effect only when Eleonora merges the
section below into `docs/decisions/lockbox.md`, under the heading it carries. Since #277
(Eleonora's ruling on #269 item 6), `scripts/live_score.py` no longer reads that heading: it scores only through
`lockbox.require_unlocked`, so it refuses any day `metadata/lockbox.json` has not opened. A scoring date opens
only the days before it, by splitting the blind tier there (`lockbox.split_tier`); committing that split is
Eleonora's own action (#256).

The section to merge, as drafted:

---

## Amendment: the live record (#215)

**Decided by Eleonora on the date this section merges.** Her decision of 3 October 2026 (#215) logs the published
pressure model's forecast every business day as a frozen live record, written before its outcome exists, on the
append-only `live-log` branch (`.github/workflows/live-log.yml`, `scripts/live_record.py`).

- **The live record's days are blind-tier days.** They are opened only on the scoring dates #215 pre-registers
  (`FIRST_SCORING_DATES` in `scripts/live_score.py`, then every 1 October), and only for the models the record carries. The scorer
  enforces two things about the date, and neither opens a day: it refuses a date that is not a scoring date
  (`require_scoring_date`), and a date that has not come in America/New_York (`require_clock`; an override flag
  is recorded in the output). Which days may be scored is `metadata/lockbox.json` and nothing else
  (`lockbox.require_unlocked`). On those dates every logged day whose outcome is observable is scored, cumulatively from the
  first logged day, and published whatever it shows. No other comparison scores a logged day, and opening them
  for the live record opens nothing else.
- **No overlap with the final test.** The final test (#150, #151) scores no day after the panel end,
  2026-09-03. The live record contains no day it scores: the first logged day falls after 2026-09-03 by
  construction, and `scripts/live_record.py` refuses to write a record for any day on or before it.
- **Training is unchanged.** As this record already says, a model may be trained on, and forecast, the days its
  as-of information set allows. Each day's forecast is fitted on what that day's as-of information set allows,
  and its record carries the code SHA, the declaration digest and the inputs it was made with.
- **The primary result is the CRPS cell at h = 1** (Eleonora's ruling of 4 October 2026 on #215): the published
  distribution (#169's gbm with nested conformal PID) against as-of persistence, both saved in each day's file,
  under the final test's pass rule (#220, #221): the mean paired difference (persistence − published) above 0 and
  its 90% lower bound above 0, labelled "not distinguishable" or "worse" otherwise, with the block-length-10
  interval reported. CRPS at h = 2 to 5 and every Brier cell (+5 bp, +10 bp, the plain leap) are reported only.
- **The CRPS cells at h = 2 to 5 are not evidence** (Eleonora's ruling of 4 October 2026, #229). At h = 1 the
  published distribution uses the CRPS record's settings; at h = 2 to 5 it uses pressure model v1's published
  declaration, because the CRPS record's declaration reads the target-day settlement, which the as-of rule
  refuses at h > 1; and the as-of persistence quantiles are the same at every horizon. Wherever these cells are
  reported, each carries this label, verbatim, next to its verdict label:

  > different model from h = 1, and as-of persistence does not widen with horizon, so this comparison favours the model; not evidence.
- **The verdict is fixed once**, at the first scoring date that scores any day of the primary cell (CRPS has no
  minimum event count). Every later scoring date is reported as an update and never replaces it.
- **The blind gap is scored once, reported only** (Eleonora's ruling of 5 October 2026 on #235, "Option 2", and
  "keep reported only"). At horizon *h*, the gap is every target day after 2026-09-03 and before the first target
  day the live record carries at *h* (read from `live/2026-10-05.json`'s `targets`): at h = 1, 2026-09-04 to
  2026-10-05. No target day is in both the gap and the live record at the same horizon.
  - The gap's days are opened once, on the first scoring date only (`GAP_SCORING_DATE` in
    `scripts/live_score.py`, the first of `FIRST_SCORING_DATES`), for the published model and the live record's
    baselines. Opening them opens nothing else.
  - They are scored with the live record's cells, in the same run as that date's live cells, as a separate block
    (`scripts/live_score.py`, `score_gap`). Every gap cell is **reported only**: it cannot pass or fail, and it
    never enters or changes the verdict. No later scoring date scores them again.
  - Their forecasts are reconstructed after the fact, each as of its own 16:00 ET decision instant, by the code
    the live record is pinned to (`scripts/live_gap.py`). They are never written to `live-log`, and the live
    record's no-backfill rule is unchanged.
  - Each gap cell carries this label, verbatim, next to any verdict label:

    > blind but not live: forecasts reconstructed after the fact by the frozen code from inputs fetched at scoring time (latest vintage); reported only, not evidence

  - The CRPS gap cells at h = 2 to 5 also carry the "not evidence" label above (#229).
- **Pressure model v2 is logged alongside the unchanged v1** (Eleonora's ruling of 6 October 2026 on #245; #244
  built v2). Each day's file also carries `distributions.published_v2`: v2's quantiles at h = 1, its record
  (`docs/runs/pressure_model_v2_distribution_h1.json`) and its declaration digest. v1's fields, its pre-registration
  and its verdict are unchanged. v2's days are blind-tier days, **opened only on the scoring dates above**, and only
  for the days on which v2 was logged. v2 was chosen on 2018–2025, after #243, so only its live record is evidence
  for it.
  - v2's primary cell is CRPS at h = 1, v2 against as-of persistence, over v2's logged days only, under the final
    test's pass rule, labels and bootstrap settings. A second cell, v1's published distribution against v2 on the
    days both are logged, is reported only. v2's block is separate and labelled, and it never enters v1's verdict.
  - v2's verdict is fixed once, at the first scoring date that scores any day of v2's primary cell. **Proposed:** the
    same dates as v1 (`FIRST_SCORING_DATES`, then every 1 October). **A question for Eleonora to confirm or change.**
    It is fixed at the first scoring date with a scored v2 day, not at a calendar date.

### The scoring procedure, the outcome source, the observation cutoff and the publication behaviour (#257)

Drafted for her. It fixes how a scoring run is made, so that the evidence can be reproduced from bytes.

- **The raw inputs are archived.** Each day's live run copies the raw snapshots its record was built from to
  `raw/<day>/` of the append-only `live-raw` branch (`scripts/live_raw.py archive`, in `live-log.yml`), content
  addressed by the digests the record already carries, in one add-only commit by the bot that is checked
  before the push (`check-append`). The record format does not change. The ruleset on `live-raw` (no deletion,
  no non-fast-forward push) is the repository setting `live-log` has, and is Eleonora's to add. A failed archive
  never blocks a record; it is reported to the failed-runs issue, and that day is listed as unarchived.
- **The outcome source is the archive.** The outcome panel is built only by `live_raw.py build-panel`, from the
  latest archived day on or before the scoring date, with the repository's own `build`, the live record's columns
  and decision time, and the build cutoff set to the latest retrieval time in that day. The scorer refuses any
  other panel (`require_registered_panel`): one with no build manifest, bytes that differ from it, no provenance
  sidecar, or a source digest the archive does not hold.
- **The observation cutoff.** A logged day is scored at a horizon only if its target day is before the scoring
  date and is in the outcome panel. Every record and horizon not scored is listed in the result with its reason:
  the target day is not in the outcome panel, or it is not before the scoring date. Nothing is skipped silently.
- **The scoring procedure.** The scoring workflow (`.github/workflows/live-score.yml`, started by hand on or after
  a scoring date) verifies the log (hash chain, digests, add-only commits, Rekor anchors, registered pins) and the
  raw archive, builds the panel from the archive, and runs `scripts/live_score.py`. The scorer refuses a date that
  has not come, a locked day, and an unregistered panel. The workflow never passes the clock override.
- **What a result records.** Its start time (UTC), the clock it read, the outcome panel's SHA-256 and the command
  that built it, the digests and retrieval times of every input the panel was built from, the scoring command, the
  code SHA, `sys.version`, the digest of the dependency lock, every live record's digest, each earlier result's
  digest, which days are archived and which are not, and the skipped list above.
- **The event cells.** The Brier cells (+5 bp, +10 bp, the plain leap) use the stationary bootstrap with mean block
  length h + 1, the horizon overlap the final test's event cells and the live CRPS cells use (it was h). Each
  cell's seed is `baseline._seed_from((scoring date, cell, horizon, model, baseline[, regime or day type]))`.
  *Proposed, hers to merge:* the block rule and the seed derivation are part of this amendment.
- **The final test's groups and false-alarm level (#363).** Each Brier cell also reports the group the final test
  (`scripts/final_test_opening.py`) reports for it, at every horizon, reported only: the plain leap's **leap-onset
  group** (`leap_onset_days`: no leap on the five panel days before the day, `onset.leap_onset_group`), and the
  +5 bp and +10 bp cells' **at-risk group** (`onset_days`: five panel days before it, all at or below 5 bp,
  `onset.day_groups`). Both are read from the outcome panel's rows before the scoring date only. A group cell has
  the cell's Brier, the model paired against each baseline over all its days, by regime and by day type (the same
  regime and day-type splits, minimum cell size and h + 1 block rule as the cell), the final test's label for the
  all-days pair (`shown better`, `shown worse`, `not shown`), and the **false-alarm level**: each column's mean
  probability on the group's days whose outcome is 0, computed by the final test's own `false_alarm_level`. A
  group with fewer than `MINIMUM_EVENTS` events is `inconclusive` and carries only its false-alarm level. The
  seeds add the group's name after the baseline. No other cell moves.
- **The frozen scorer (#282).** The live scorer is frozen the way the final test's CRPS functions are
  (`final_test_preregistration.py`, `crps_declaration_checksum`), by a checksum of its own,
  `scripts/live_score.py`'s `live_declaration_checksum`: the SHA-256 of every top-level definition the scoring
  functions reach, in `live_score.py` and in the modules they call into, with the constants they read. It covers the
  cells (`score`, `score_crps`, the group cells), the intervals (`_paired`, `_paired_cell`,
  `stationary_bootstrap_interval`, the seeds), the minimum-cell rule (`_small_cell`), the regime and month-end splits
  (`_regime`, `SplitDeclaration`, `MONTH_END_RULE`) and the gap scoring (`score_gap` and its helpers); the final
  test's two checksums do not move. `tests/test_live_score_freeze.py` fails when any covered function changes and
  when a scoring function is added outside the checksum. It was taken after the declarations, the `lockbox.json`
  routing, the `month_end` re-split, #257, #231 and the final test's groups (#363) had merged, so #282 is the
  last change not under it. A later change to a covered function is a decision of hers and re-pins this value.
  The pin was re-taken for #370 (her `GO #370`, attested in `metadata/owner_attestations.json`): the freeze also covers
  the decision-day calendar helpers (`next_decision_days`, `previous_decision_day` in `scripts/live_record.py`, with
  what they reach there) and the group labels (`onset.GROUP_ONSET`, `onset.GROUP_LEAP_ONSET`), which set the blind
  gap's day boundaries and the group cells.
  *Proposed, hers to merge:* the pin in the next two lines.

- **Live scorer checksum:** `d508b30d94da822d6b3f816fb9e9a5616c83f29b266878e72722f7f6eac82a79`
- **Live scorer checksum taken at:** `da7aa3dd3bcb5bb6591e9c711fd3421223f085db`
- **The gap.** The blind gap's raw inputs, fetched once at scoring time, are archived on `live-raw` as
  `raw/<date>-gap/` before the reconstruction reads them. Its day boundaries are computed by the pinned code's own
  calendar and the scorer asserts they equal the ones it computes from main's; a difference refuses the run.
- **Publication.** A result is published whatever it shows, as a new record in `docs/runs/` by a pull request
  (`docs/decisions/publish-rule.md`), together with the skipped list and the provenance above. The scoring
  workflow itself writes only to its artifact.
