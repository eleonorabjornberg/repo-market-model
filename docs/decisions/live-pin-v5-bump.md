# Version bump: the live pin moves to the decision-row fix (#1475)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1475. Her own `GO #1475` (comment
6662675639, 5 November 2026) and her ruling on #1471, option (a) (the decision docket, relayed on #1475), authorise the pin
move. It takes effect only when she merges the pull request; the merge is hers.

Dated 5 November 2026. Serves H5 groundwork G3 (prospective logging).

## Why

The pin in force (`decision-instant-1800`, `2eba843b35e197ed92cac968aa45aaf514a35e2a`, the merge of #1384) does not contain
the fix of #1403. At the 18:00 instant the decision row must carry the day's own bill rates (`tbill_4w`, `tbill_13w`,
public at 16:30 ET), and the code at that pin reads them off a placeholder row. The live-log run of 4 November (run
41962103151, 5 November 03:31 UTC) failed with `LookAheadError: the forecast of 2026-11-05 reads tbill_13w (observed) on
2026-11-04, a placeholder row that does not carry it`. Every business day is lost until the pin moves (#1471).

## The new pin

| id | SHA | Decided |
|---|---|---|
| `decision-row-bills` (after `decision-instant-1800`) | `6d95ebb93db369892b2ee46b30b5e87ddb2e63e2` (the merge of #1408, "Live decision row carries the day's own bill rates at 18:00", for #1403) | Eleonora, `GO #1475` (comment 6662675639); ruling on #1471, option (a) |

The transition is added to `metadata/live_pin.json`. The bump is never retroactive: each day's file carries the SHA it was
made with, and every file already on `live-log` still scores.

## What the live code changes between the two pins

`git diff 2eba843b 6d95ebb9` restricted to the files the live job runs changes two scripts:

- `scripts/live_record.py` (#1408, for #1403): the decision day's row carries `tbill_4w` and `tbill_13w`
  (`DECISION_ROW_COLUMNS`), read from the point-in-time panel as public at the instant (`decision_row_values`), after
  `require_decision_row_declared` checks the declaration. `require_reads_on_real_rows` admits an observed read of those two
  columns on the decision row only, and no other observed read, and none on a target row.
- `scripts/live_h10.py` (#1405, for #1401, her `GO #1401`): an onset the registered method refused on every day its report
  window was open becomes final as "refused at window close" (`counted: false`, in the denominator) and keeps its refusal,
  instead of "not attributable".

The same range also holds `src/repo_model/availability_poll.py` and `.github/workflows/availability-poll.yml` (the
availability poll, #1343, a separate workflow that writes no live record), and study scripts and tests. None of them is run
by `live-log.yml`.

## Lost days

4 November 2026 is lost: no 18:00 record exists for it. Any later business day on which the live-log run fails before this
pull request merges is lost the same way. **Nothing is back-filled** (a forecast made after its instant would not be a
prospective record). The days written so far are not edited.

## The first day the new pin writes

The first business day whose live-log run starts after the merge and finds the pin moved. Merged before 18:00 ET on the day
of the merge, that day's run is the first; merged after that day's live-log run has finished, the next business day is. The
pull request must not merge between 18:00 ET and the end of that day's live-log run. Whether the first run on the new pin
wrote a record is not known until it has run.

## What does not change

`PINNED_CODE_SHA` and `resolve_pin`, the models logged, the scoring protocol, the lockbox, every published record and every
file on `live-log`.
