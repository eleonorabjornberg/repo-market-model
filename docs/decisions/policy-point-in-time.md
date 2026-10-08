# Decision: policy and legislation are read from their announcement

**Status: drafted for Eleonora's review (#376, track P of #374). Not in force until she merges it.**
It extends the rule of `fomc-point-in-time.md` from FOMC dates to the whole policy register.

## The rule

`metadata/policy_events.json` lists the changes that bear on money-market pressure, one entry each, with its
announcement date and time, its effective date and a primary source. A feature may use an entry **only from its
announcement instant**, never from its effective date in hindsight.

- At a decision instant `D`, an entry is *known* if its announcement instant is at or before `D`. It is *in force*
  if it is known and its effective date is on or before `D`'s date. An entry that is known and not yet effective
  is *pending*. A proposal has no effective date and is never in force.
- A source that states no release time is public from 23:59:59 on its date (`time_basis` `not_stated`), so a
  decision on that day never sees it. This can read an entry a few hours late; it cannot read one early.
- Instants are America/New_York wall-clock times, as in `announced_iorb`.
- `repo_model.policy_events.require_announced` raises `LookAheadError` when an entry is used before its
  announcement. `load_register` raises `ValueError` for a malformed register, or one that has an entry in force
  before it is announced.
- **No entry is inferred from the spread.** An entry exists because a primary source announces it. Each entry
  records whether the source was read when the register was built (`read_at_source`).

## What it does not settle

Whether any feature built on the register earns a place in a declared comparison. That is #374's, under
`pressure-probability.md`. The register changes no published declaration, record or figure.
