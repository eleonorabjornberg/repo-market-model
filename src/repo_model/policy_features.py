"""Policy-register features for the pressure classifiers (#412, track P of #374).

The point-in-time register of `repo_model.policy_events` (#376) as columns: the
active policy settings and the days since and until known policy events, each as
of the decision instant of the row that carries it. Eleonora's directive of 7
October 2026 (#412): add them to the best rare-event classifier of #381 and to
track O (#409), and judge the result against the same classifiers without them.

**The columns** (`COLUMNS`), one value per panel row, never missing:

* `policy_days_since_known`: calendar days from the latest announcement at or
  before the decision instant to the decision day, capped at `DAYS_CAP`.
* `policy_days_until_effective`: calendar days from the decision day to the
  earliest effective date among the entries that are known and not yet in force,
  capped at `DAYS_CAP`; `DAYS_CAP` when none is pending (a proposal has no
  effective date and is not counted).
* `policy_pending_count`: the entries known and not yet in force, proposals
  included.
* `policy_iorb_offset_bp`: the IORB offset from the bottom of the target range,
  in basis points, of the latest IORB entry in force.
* `policy_qt_in_force`: 1 while balance-sheet runoff is in force (the latest
  runoff entry in force is a start or a taper, not an end), else 0.
* `policy_standing_repo_in_force`: 1 once the standing repo facility is in force.
* `policy_slr_exclusion_in_force`: 1 while the temporary exclusion of reserves
  and Treasuries from the supplementary leverage ratio is in force.
* `policy_reserve_management_in_force`: 1 once reserve-management operations are
  in force.
* `policy_debt_limit_reinstated`: 1 while the latest debt-limit entry in force is
  a reinstatement (the limit binds), 0 after a suspension or an increase.

**Keyed on the announcement, never on the effective date**
(`docs/decisions/policy-point-in-time.md`). Every value is computed from
`policy_events.policy_state(register, as_of)`, which admits only entries announced
at or before `as_of`, and every entry used is passed through
`policy_events.require_announced`, which raises `LookAheadError` otherwise. A row
is read at `datetime.combine(row.date, decision_time)`, the instant a forecast
made on that row's day is made; a source that states no release time is public
from 23:59:59 on its date, so a decision on that day never sees it.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published
panel, declaration or record reads these columns. A track switches them on for
its own run (`scripts/policy_features.py`). The source they draw on,
`policy_register`, is declared in `metadata/sources_measurement.json`, not in
`metadata/sources.json`, which the final-test pre-registration freezes by its
bytes.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .data import DailyObservation
from .policy_events import PolicyEntry, load_register, policy_state, require_announced

__all__ = [
    "COLUMNS",
    "COLUMN_FIELDS",
    "DAYS_CAP",
    "SOURCE_ID",
    "add_columns",
    "policy_feature_values",
]

SOURCE_ID = "policy_register"
#: The cap on both day counts, in calendar days. A cap, not a missing value: a
#: stretch with no known event reads as a long wait.
DAYS_CAP = 90

COLUMNS = (
    "policy_days_since_known",
    "policy_days_until_effective",
    "policy_pending_count",
    "policy_iorb_offset_bp",
    "policy_qt_in_force",
    "policy_standing_repo_in_force",
    "policy_slr_exclusion_in_force",
    "policy_reserve_management_in_force",
    "policy_debt_limit_reinstated",
)

#: Every column's source field, for the as-of rule: one field per column, in the
#: source `policy_register` of `metadata/sources_measurement.json`. **Off**.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    name: ((SOURCE_ID, name),) for name in COLUMNS
}

_RUNOFF_ON = ("qt_start", "qt_taper")
_RUNOFF_OFF = ("qt_end",)


def _latest(entries: Sequence[PolicyEntry], kind: str) -> Optional[PolicyEntry]:
    pool = [e for e in entries if e.kind == kind]
    return max(pool, key=lambda e: (e.effective, e.announced_at)) if pool else None


def _latest_with_action(
    entries: Sequence[PolicyEntry], kind: str, actions: Sequence[str]
) -> Optional[PolicyEntry]:
    pool = [e for e in entries if e.kind == kind and e.action in actions]
    return max(pool, key=lambda e: (e.effective, e.announced_at)) if pool else None


def policy_feature_values(
    register: Sequence[PolicyEntry], as_of: datetime
) -> Dict[str, float]:
    """The columns as of the decision instant `as_of`, from announcements at or before it.

    Raises:
        LookAheadError: an entry that was not public at `as_of` reached a value
            (cannot happen through `policy_state`; the guard is explicit).
        ValueError: `as_of` is not a naive wall-clock datetime.
    """

    state = policy_state(register, as_of)
    for entry in state.in_force + state.pending:
        require_announced(entry, as_of)
    today = as_of.date()
    known = state.in_force + state.pending
    since = (
        min(DAYS_CAP, (today - max(e.announced_at for e in known).date()).days) if known else DAYS_CAP
    )
    dated = [e.effective for e in state.pending if e.effective is not None]
    until = min(DAYS_CAP, (min(dated) - today).days) if dated else DAYS_CAP

    iorb = [e for e in state.in_force if e.kind == "iorb_rate" and "offset_from_range_bottom_bps" in e.details]
    offset = max(iorb, key=lambda e: (e.effective, e.announced_at)).details["offset_from_range_bottom_bps"] if iorb else 0

    runoff = _latest_with_action(state.in_force, "balance_sheet", _RUNOFF_ON + _RUNOFF_OFF)
    exclusion = _latest_with_action(state.in_force, "slr", ("exclusion_start", "exclusion_expiry"))
    debt = _latest(state.in_force, "debt_ceiling")
    return {
        "policy_days_since_known": float(since),
        "policy_days_until_effective": float(until),
        "policy_pending_count": float(len(state.pending)),
        "policy_iorb_offset_bp": float(offset),
        "policy_qt_in_force": float(runoff is not None and runoff.action in _RUNOFF_ON),
        "policy_standing_repo_in_force": float(any(e.kind == "standing_repo" for e in state.in_force)),
        "policy_slr_exclusion_in_force": float(exclusion is not None and exclusion.action == "exclusion_start"),
        "policy_reserve_management_in_force": float(any(e.kind == "reserve_management" for e in state.in_force)),
        "policy_debt_limit_reinstated": float(debt is not None and debt.action == "reinstatement"),
    }


def add_columns(
    rows: Sequence[DailyObservation],
    register: Optional[Sequence[PolicyEntry]] = None,
    *,
    decision_time: time = time(16, 0),
) -> List[DailyObservation]:
    """`rows` with the columns added, each read at its own row's decision instant.

    A row's values depend on that row's date and the register alone, so they are
    the same whatever rows follow.
    """

    entries = load_register() if register is None else register
    out: List[DailyObservation] = []
    for row in rows:
        values = dict(row.values)
        values.update(policy_feature_values(entries, datetime.combine(row.date, decision_time)))
        out.append(DailyObservation(row.date, values))
    return out
