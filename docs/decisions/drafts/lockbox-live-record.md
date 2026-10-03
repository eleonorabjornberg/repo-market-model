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
- **The headline verdict is fixed once**, at the first scoring date whose headline cell (the plain leap at
  h = 1, against each baseline) holds `onset.MINIMUM_EVENTS` events. Every later scoring date is reported as an
  update and never replaces it.
