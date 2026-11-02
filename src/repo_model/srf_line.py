"""The Standing Repo Facility line: the minimum bid rate less the IORB, in bp (#1241; H5 step 3).

The facility's minimum bid rate is an administered rate above the SOFR - IORB spread (`docs/decisions/pressure-probability.md`).
This module reads it from the point-in-time register `metadata/policy_events.json` (`repo_model.policy_events`): the `standing_repo`
entry in force on the target day, less the `iorb_rate` entry in force on the same day, each in percent, times 100. It reads +10 bp
wherever the register says the minimum bid is at the top of the range and IORB 15 bp over its bottom in a 25 bp range, and it reads
whatever the register says elsewhere: the number is never written here.

**Information set.** The line on a target day, as a decision at `as_of` could know it, uses only the entries announced at or before
`as_of` (the instant a forecast is made, 16:00 on its decision day) that are effective on or before the target day: a change announced
at an FOMC meeting after the decision instant is not known, and a change already announced and scheduled for the target day is, the
same rule the scheduled IORB follows (`announced_iorb`, `scheduled_availability`). Each entry used is passed through
`policy_events.require_announced`, so a read of an entry announced after `as_of` raises `LookAheadError`. The declaration of
availability is in `metadata/srf_cap_1241.json`.

**Before the facility** (established 2021-07-28, effective 2021-07-29) there is no line: `srf_line_bps` returns `None` and a cap leaves
the forecast unchanged.

**The cap** (`cap_quantiles`) clips each quantile at the line plus a margin. It is monotone, so the levels stay ordered.

Stdlib only.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional, Sequence

from .decision_instant import LEGACY_DECISION_TIME
from .policy_events import PolicyEntry, known_entries, require_announced

__all__ = ["DECISION_TIME", "FACILITY_EFFECTIVE", "cap_quantiles", "srf_line_bps"]

#: The instant #1241's and #1252's declarations state as `available_time`: the decision instant when they were
#: declared (16:00), kept as those dated declarations record it (#1312). The cap is not adopted, and a re-declaration
#: at the new instant is a later directive's.
DECISION_TIME = LEGACY_DECISION_TIME
#: The first day of the facility in the register (`standing_repo-20210728`, effective 2021-07-29).
FACILITY_EFFECTIVE = date(2021, 7, 29)
_SRF, _IORB = "standing_repo", "iorb_rate"


def _in_force(known: Sequence[PolicyEntry], kind: str, target: date) -> Optional[PolicyEntry]:
    """The entry of `kind` with the latest effective day on or before `target`, then the latest announcement."""

    pool = [e for e in known if e.kind == kind and e.effective is not None and e.effective <= target]
    return max(pool, key=lambda e: (e.effective, e.announced_at)) if pool else None


def srf_line_bps(register: Sequence[PolicyEntry], as_of: datetime, target: date) -> Optional[float]:
    """The minimum bid rate less the IORB on `target`, in bp, as known at the naive America/New_York instant `as_of`.

    Returns `None` when no facility entry is effective on or before `target` among those announced by `as_of`.

    Raises:
        ValueError: `as_of` is not a naive datetime; or the facility is in force but no IORB entry is.
        LookAheadError: an entry read was announced after `as_of`.
    """

    known = known_entries(register, as_of)
    srf = _in_force(known, _SRF, target)
    if srf is None:
        return None
    iorb = _in_force(known, _IORB, target)
    if iorb is None:
        raise ValueError(f"the facility is in force on {target} but the register has no IORB entry announced by {as_of} and effective by then")
    for used in (srf, iorb):
        require_announced(used, as_of)
    return round(100.0 * (float(srf.details["rate_percent"]) - float(iorb.details["rate_percent"])), 6)


def cap_quantiles(quantiles: Sequence[float], line: Optional[float], margin: float) -> List[float]:
    """The quantiles with every value above `line + margin` set to `line + margin`; unchanged where there is no line.

    Raises:
        ValueError: `margin` is negative.
    """

    if margin < 0:
        raise ValueError(f"the margin is not negative, got {margin}")
    if line is None:
        return list(quantiles)
    ceiling = line + margin
    return [min(float(q), ceiling) for q in quantiles]
