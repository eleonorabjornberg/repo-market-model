# Version bump: the protocol block joins the live record (#656)

**Status: approved by Eleonora's own `GO #656` (comment 6172786156, 14 October 2026); the pin moves when #736's pull request merges.** Drafted by the pull request that closes #656. It takes effect only
when she merges it, and the pin moves only through her own approval (`docs/decisions/live-pin.md`: an owner-attested
comment, cited in `metadata/owner_attestations.json`).

Dated 13 October 2026. Serves H5 groundwork G3 (prospective logging) and scoring protocol v1, §12 item 2.

## What changes

The code that makes the live record gains a `protocol` block (`live_record.protocol_for`,
`repo_model.prospective_log`). A day's file made by it has `record_version` 3 and the new block:

- B1 and B2: the 23-quantile forecast for h = 1 to 5, from `repo_model.protocol_benchmarks`, made at the decision
  instant;
- B3, the incumbent: **named, not mapped.** The published v1 declaration forecasts five levels, and the protocol does
  not say how it is put on the 23-level grid. The block points at the five-level forecast the same file already
  carries under `distributions.published`. This is a question for Eleonora, in the pull request;
- the forecast of every registered candidate (none: `prospective_log.REGISTERED_CANDIDATES` is empty, and registering
  one is her attested action);
- the H7m hook (`prospective_log.read_h7m_estimate`): a registered estimate read from a liquidity-repository snapshot
  pinned by digest. Nothing is registered (`REGISTERED_H7M` is empty), so the block's `h7m` is null.

A record is refused (`LookAheadError`) if it is written at or after the instant its first outcome is published.

## What does not change

Every field a version 2 file has is written as before, by the same calls in the same order; `tests/test_live_v3.py`
strips the new block and the version and compares the bytes with a version 2 file. Files already in `live-log` stay
as they are, at `record_version` 1 or 2, and still score. `scripts/live_score.py` reads all three. The models logged
(`MODELS`) and the published records the file names are unchanged, so this is not a `live-model` change.

## The new pin

| id | SHA | Decided |
|---|---|---|
| the next transition after `t0-first-record` and, if registered first, `t1-v2-joins` (id: `protocol-block`) | `492c53d65b09a0181065f5532f0197291b24ea14` (the merge commit of #699, which closes #656) | Eleonora, `GO #656` (comment 6172786156), 14 October 2026 |

The bump is never retroactive: each day's file already carries the SHA it was made with. The transition is added to
`metadata/live_pin.json`, naming the merge commit, in a follow-up that carries Eleonora's own approval (kind
`live-pin`). Until then the workflow logs the code the current pin names, which has no protocol block. This pull
request does not touch `metadata/live_pin.json`, `PINNED_CODE_SHA` or `resolve_pin`.

## Timing

The workflow logs whatever is pinned when it runs. This pull request must merge outside the window from 16:00 ET until
that day's live-log run finishes, and the pin follow-up likewise.

## Not yet in this record

The workflow `live-log.yml` is unchanged: it runs the script at the pinned SHA, so the protocol block reaches the
live record only when the pin moves. Candidates and the H7m estimate are added by their own registrations.
