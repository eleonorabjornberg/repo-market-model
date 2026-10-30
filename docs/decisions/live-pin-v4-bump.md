# Version bump: the live record moves to the 18:00 decision instant (#1313)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1313, which is a draft until her own
`GO #1313` on that issue (a comment by her, not through an app), cited in `metadata/owner_attestations.json`. It takes effect only
when she merges it, and the pin moves only through her own approval (`docs/decisions/live-pin.md`: an owner-attested
comment, cited in `metadata/owner_attestations.json`, in a follow-up that edits `metadata/live_pin.json`).

Serves H5 groundwork G3 (prospective logging) and scoring protocol v1, §12 item 2. Step 2 of 3 of moving the decision instant
from 16:00 to 18:00 America/New_York, her ruling of 29 October 2026 (chat, relayed on #1312; ledger item 77). Step 1
(`docs/decisions/information-set.md`, "Amendment: the decision instant is 18:00 New York time") moved the instant for the
information set, the panel build and the final test, and is merged. Step 3 is the re-runs of the results that matter.

## What changes

1. **The 16:00 live record is closed.** The `live-log` branch holds the days logged at 16:00, each a frozen file with its chain,
   its digest, its Rekor anchor and its raw inputs on `live-raw`. Nothing is appended to it from the **last 16:00 day** named
   below. No entry of it is edited, re-scored at another instant or relabelled: each stays a record of the 16:00 instant, as
   the amendment of #1312 says (item 3). It is closed because the instant it was made at is no longer the project's decision
   instant. A forecast made at 16:00 does not see what the sources publish between 16:00 and 18:00 (the GCF Repo Index at about
   16:00 to 16:05, H.15, H.8, FR 2004, and the H.4.1 on Thursdays), which the project now treats as public at its decision.
   Logging two records a day, or switching the instant inside one chain, would make the days of one record not comparable with
   each other.
2. **A new live record opens at 18:00.** Its days are made by the code the new pin names, at 18:00 America/New_York
   (`repo_model.decision_instant.DECISION_TIME`), on the same `live-log` branch, in the same append-only chain (the ruleset that
   protects it names the branch, and moving to another branch is a repository setting that is hers). Every file already says
   which instant it was made at (`decision_instant`) and which code (`code.pinned_sha`), so the two records are told apart by the
   file and by the pin transition, never by the file's position.
3. **The workflow runs later.** `live-log.yml` no longer has the 21:30 UTC slot, which is 17:30 EDT and 16:30 EST, before the new
   instant. Its two remaining slots start after 18:00 ET in both offsets, and its "skip before the decision instant" step skips
   before 18:00 ET, not 16:00. `live-score.yml` has no schedule (it is started by hand on a scoring date), so it has no cron to
   move. The workflow reads the pin, not a date, to decide which record a run writes.

| Cron (UTC) | Days (UTC) | ET in EDT (summer time) | ET in EST (winter time) | Role |
|---|---|---|---|---|
| `15 23 * * 1-5` | Monday to Friday | 19:15, same ET day | 18:15, same ET day | primary |
| `15 1 * * 2-6` | Tuesday to Saturday | 21:15, the ET day before (Monday to Friday) | 20:15, the ET day before (Monday to Friday) | fallback for a delayed or dropped run |
| removed: `30 21 * * 1-5` | Monday to Friday | 17:30 | 16:30 | before the instant either way |

The decision instant itself is 22:00 UTC in EDT and 23:00 UTC in EST. A slot that finds the day already on `live-log` does
nothing, and a run that starts before 18:00 ET ends green with nothing written (#937).

## The dates

| | Day | Decided |
|---|---|---|
| the last 16:00 day | the last business day whose record the 16:00 pin writes before the pin follow-up merges | by the pin follow-up, which names it |
| the first 18:00 day | the first business day whose run reads the new pin | by the pin follow-up, which names it |

**Marked question for Eleonora (numbered options; default 1).** I have not typed a calendar date in this record: a date written
before it has happened is refused by `tests/test_docs_freshness.py`, and the right date depends on when the two pull requests
merge. Which day does the new record start?

1. The first business day that begins after the pin follow-up has merged (default). The follow-up is not merged between 18:00 ET
   and the end of that day's live-log run, and it states both days in its description.
2. A day she names in her `GO #1313` comment; the follow-up then merges at least one full business day before it.

## The new pin

| id | SHA | Decided |
|---|---|---|
| the next transition after `protocol-block` (id: `decision-instant-1800`) | **not yet known:** the merge commit of the pull request that makes the live code read 18:00 (see "Not yet in this record") | Eleonora, `GO #1313` (comment id to be cited), date to be filled in by the follow-up |

The bump is never retroactive: each day's file already carries the SHA it was made with. The transition is added to
`metadata/live_pin.json`, naming that merge commit, in a follow-up that carries Eleonora's own approval (kind `live-pin`). Until
then the workflow logs the code the current pin names, which makes 16:00 records. This pull request does not touch
`metadata/live_pin.json`, `PINNED_CODE_SHA` or `resolve_pin`.

## What does not change

- No entry of the 16:00 record. `live/*.json`, their `.rekor` files, `live-raw/` and the digest issue are as they are.
- `scripts/live_score.py` and the scoring of the days already logged. A 16:00 record keeps scoring against the instant it
  declares.
- The models logged (`MODELS`), the published records the file names, the scoring protocol, the lockbox and every published
  record.

## Not yet in this record (marked questions)

The code a day's record is made by still reads 16:00: `scripts/live_record.py` takes `DECISION` from the published pressure model
v1 script (`pressure_model_v1.DECISION`, a frozen declaration), builds its panel with `--decision-time 16:00:00`, and
`scripts/live_raw.py` (`DECISION_TIME`) and `scripts/live_monitor.py` hold the same clock. Pinning today's code would therefore
write 16:00 records after 18:00. Two questions come with that, each a judgement call that is hers and so not settled here:

1. **Which code makes the 18:00 record?** Options: (a) a separate directive, before the pin moves, makes `live_record.py`,
   `live_raw.py` and `live_monitor.py` read `repo_model.decision_instant.DECISION_TIME` and keeps each reader of a 16:00 file
   reading it against the instant the file declares (default); (b) the same pull request as the pin follow-up. Either way the
   published model v1's own `DECISION` constant and its declaration checksum are not edited in place.
2. **Is the published pressure model v1 run at 18:00 still "the published model"?** At 18:00 it reads a later row of several
   inputs (#1312's table), so its forecasts differ from what the same code gives at 16:00. Options: (a) log it as the same
   model with the instant in each file (default; the file already carries the instant and the pin); (b) register it as a new
   model, which is a `live-model` change and hers.

Candidates and the H7m estimate are added by their own registrations, as before.

## Timing

The workflow logs whatever is pinned when it runs. This pull request must merge outside the window from 18:00 ET until that
day's live-log run finishes, and the pin follow-up likewise. The first run on the new schedule after this merges is the
primary slot of the same evening or the next, and it logs the code the current pin names.
