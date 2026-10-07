# Version bump: pressure model v2 joins the live record (#245)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #245. It takes effect only
when she merges it, and the pin moves only through her own approval (`docs/decisions/live-pin.md`: an owner-attested
comment, cited in `metadata/owner_attestations.json`).

Dated 7 October 2026.

## What changes

The code that makes the live record gains pressure model v2's distribution at h = 1 (`live_record.distributions_block`,
`live_record.v2_distribution_forecast`). A day's file made by it has `record_version` 2 and a new block,
`distributions.published_v2`. `scripts/live_score.py` reads files of both versions.

## What does not change

v1's output is unchanged. Every field v1 writes, `models`, `baselines` and the two sides of `distributions`, is written
by the same calls in the same order, with the same values and digests; `tests/test_live_v2.py` runs both versions on the
same inputs and compares them. Files already in `live-log` stay as they are, at `record_version` 1, and still score.

## The new pin

| id | SHA | Decided |
|---|---|---|
| `t1-v2-joins` | the merge commit of the pull request that closes #245 | not yet: the SHA does not exist until that pull request merges |

The bump is never retroactive: each day's file already carries the SHA it was made with, and `t0-first-record` stays
registered. The transition is added to `metadata/live_pin.json`, naming the merge commit, in a follow-up that carries
Eleonora's own approval (kind `live-pin`). Until then the workflow logs the code `t0-first-record` pins, which has no v2,
so no day is made with a half-applied pin. This pull request does not touch `metadata/live_pin.json`.

## Timing

The workflow logs whatever is pinned when it runs. This pull request must merge outside the window from 16:00 ET until
that day's live-log run finishes, and the pin follow-up likewise.

## Approval

Adding v2 to the live record is a `live-model` binding change (`scripts/owner_attested.py`): the `owner-attested` CI check
on this pull request stays red until Eleonora's own `GO #245` comment is cited in `metadata/owner_attestations.json`. The
issue's ruling was relayed by the orchestrating session, so it does not stand for that approval.
