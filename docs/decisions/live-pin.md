# The live record's code pin

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #255. It takes effect only
when she merges it. The registered transition below records the pin the first live record was made with; it is a
record of her decision on #215, not a new pin.

## Rule

The live record is made by pinned code, and the pin is a literal, not a rule evaluated on `main`.

- `metadata/live_pin.json` holds the current pin and every registered transition. `scripts/live_pin.py` checks it.
- The live workflow reads the pin from that file with `jq` and checks that commit out before any repository Python
  runs. It then verifies the registry: each transition's SHA is an ancestor of `main`, and is named in the decision
  record the transition cites.
- `scripts/live_score.py` refuses a record whose `code.pinned_sha` is not a registered transition.
- A pin change needs all of: a new transition in the manifest, a dated decision record in this directory that names
  the new SHA, a version bump where the record's schema or declaration changes, and Eleonora's own approval. That
  approval is an owner-attested comment on GitHub (`scripts/owner_attested.py`, kind `live-pin`), cited in
  `metadata/owner_attestations.json`.
- The live record never moves retroactively: each record carries the SHA it was made with, and an earlier transition
  stays registered.

## Registered transitions

| id | SHA | Decided |
|---|---|---|
| `t0-first-record` | c69a361965fd601a4e69fdbc92643d669dba8e9e | Eleonora's decision of 3 October 2026 (#215): the merge commit that brought `scripts/live_record.py` onto `main`; the first record, `live/2026-10-05.json`, was made with it. |

## What this does not do

It does not protect `main`. A direct push to `main` can still edit the manifest. Requiring a pull request on `main`,
with `tests.yml` required, is a repository setting only Eleonora can change (#269, item 2). Until it is on, the
manifest's owner-attestation check runs on pull requests only.
