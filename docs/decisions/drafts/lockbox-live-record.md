# Draft amendment to `lockbox.md`: the live record

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #215, as that directive
asks. It takes effect only when Eleonora merges the section below into `docs/decisions/lockbox.md`, under the
heading it carries. Until then `scripts/live_score.py` refuses to run at all: it reads that heading in
`lockbox.md`, not in this file.

The section to merge, as drafted:

---

## Amendment: the live record (#215)

**Decided by Eleonora on the date this section merges.** Her decision of 3 October 2026 (#215) logs the published
pressure model's forecast every business day as a frozen live record, written before its outcome exists, on the
append-only `live-log` branch (`.github/workflows/live-log.yml`, `scripts/live_record.py`).

- **The live record's days are blind-tier days.** They are opened only on the scoring dates #215 pre-registers,
  fixed in `scripts/live_score.py` (`FIRST_SCORING_DATES`, then every 1 October), and only for the models the
  record carries. On those dates every logged day whose outcome is observable is scored, cumulatively from the
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
