"""The point-in-time register of policy and legislation (#376, track P of #374).

`metadata/policy_events.json` lists the changes that bear on money-market
pressure: administered-rate settings, the ON RRP and the standing repo facility,
balance-sheet runoff and reserve-management purchases, the supplementary
leverage ratio, Treasury buybacks and debt-limit acts. Each entry has the
instant it became public and the date it takes effect, and a primary source.

**Keyed on the announcement, never on the effective date**
(`docs/decisions/policy-point-in-time.md`, drafted for review; the rule is the
one `docs/decisions/fomc-point-in-time.md` states for FOMC dates). A forecast
made at instant `D` sees an entry only if its announcement instant is at or
before `D`. An entry that is announced but not yet effective is `pending`; it is
known, and it is not yet in force. Instants are America/New_York wall-clock
datetimes, like `announced_iorb`. A source that states no release time is public
from 23:59:59 on its date (`time_basis` is `not_stated`): a decision on that date
never sees it.

The guard is `require_announced`: using an entry at an instant before its
announcement raises `LookAheadError`. `policy_state` reads only what the guard
would admit.

Stdlib only.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, Iterable, NamedTuple, Optional, Sequence, Tuple

from .splits import LookAheadError

__all__ = [
    "KINDS",
    "PolicyEntry",
    "PolicyState",
    "REGISTER_PATH",
    "known_entries",
    "load_register",
    "policy_state",
    "require_announced",
]

REGISTER_PATH = Path(__file__).resolve().parents[2] / "metadata" / "policy_events.json"
KINDS = (
    "iorb_rate", "on_rrp", "standing_repo", "balance_sheet", "reserve_management",
    "slr", "treasury_buyback", "debt_ceiling",
)
#: The instant a date-only announcement is public: the last second of its date.
END_OF_DAY = time(23, 59, 59)
_REQUIRED = (
    "id", "kind", "action", "title", "announced_date", "announced_time", "time_basis",
    "effective_date", "effective_precision", "source_url", "read_at_source", "details",
)


class PolicyEntry(NamedTuple):
    """One change: when it was public, when it takes effect, and where it is sourced."""

    id: str
    kind: str
    action: str
    title: str
    announced_at: datetime  # America/New_York wall clock, naive
    time_basis: str  # "stated" or "not_stated"
    effective: Optional[date]  # None for a proposal, which is never in force
    source_url: str
    read_at_source: bool
    details: dict


class PolicyState(NamedTuple):
    """The register as known at `as_of`: announced entries, split by whether in force."""

    as_of: datetime
    in_force: Tuple[PolicyEntry, ...]  # announced, and effective on or before as_of's date
    pending: Tuple[PolicyEntry, ...]  # announced, not yet effective (or a proposal)

    def latest(self, kind: str) -> Optional[PolicyEntry]:
        """The entry of `kind` most recently in force: latest effective date, then announcement."""

        pool = [e for e in self.in_force if e.kind == kind]
        return max(pool, key=lambda e: (e.effective, e.announced_at)) if pool else None


def load_register(path: Path = REGISTER_PATH) -> Tuple[PolicyEntry, ...]:
    """Read and check the register, announcement order.

    Raises:
        ValueError: a malformed entry, a duplicate id, an unknown kind, a source
            that is not an https URL, or an entry in force before it is announced.
    """

    document = json.loads(Path(path).read_text(encoding="utf-8"))
    entries, seen = [], set()
    for number, raw in enumerate(document["entries"]):
        where = f"{path} entry {number}"
        missing = [k for k in _REQUIRED if k not in raw]
        if missing:
            raise ValueError(f"{where}: missing {missing}")
        if raw["id"] in seen:
            raise ValueError(f"{where}: duplicate id {raw['id']}")
        seen.add(raw["id"])
        if raw["kind"] not in KINDS:
            raise ValueError(f"{where}: unknown kind {raw['kind']!r}")
        if not str(raw["source_url"]).startswith("https://"):
            raise ValueError(f"{where}: source_url must be an https URL")
        if raw["time_basis"] not in ("stated", "not_stated"):
            raise ValueError(f"{where}: time_basis must be 'stated' or 'not_stated'")
        if (raw["announced_time"] is None) != (raw["time_basis"] == "not_stated"):
            raise ValueError(f"{where}: announced_time and time_basis disagree")
        try:
            day = date.fromisoformat(raw["announced_date"])
            clock = time.fromisoformat(raw["announced_time"]) if raw["announced_time"] else END_OF_DAY
            effective = date.fromisoformat(raw["effective_date"]) if raw["effective_date"] else None
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{where}: {exc}") from exc
        if effective is not None and effective < day:
            raise ValueError(f"{where}: effective {effective} is before its announcement {day}")
        entries.append(
            PolicyEntry(
                raw["id"], raw["kind"], raw["action"], raw["title"], datetime.combine(day, clock),
                raw["time_basis"], effective, raw["source_url"], bool(raw["read_at_source"]),
                dict(raw["details"]),
            )
        )
    entries.sort(key=lambda e: (e.announced_at, e.id))
    return tuple(entries)


def _check_instant(as_of: datetime) -> None:
    if not isinstance(as_of, datetime):
        raise ValueError(f"as_of must be a datetime, not {type(as_of).__name__}")
    if as_of.tzinfo is not None:
        raise ValueError("as_of is a naive America/New_York wall-clock datetime")


def require_announced(entry: PolicyEntry, as_of: datetime) -> PolicyEntry:
    """Return `entry`, or raise `LookAheadError` if it was not public at `as_of`."""

    _check_instant(as_of)
    if entry.announced_at > as_of:
        raise LookAheadError(
            f"policy entry {entry.id} is announced {entry.announced_at}, after the decision instant {as_of}"
        )
    return entry


def known_entries(register: Iterable[PolicyEntry], as_of: datetime) -> Tuple[PolicyEntry, ...]:
    """The entries announced at or before `as_of`, announcement order."""

    _check_instant(as_of)
    return tuple(e for e in register if e.announced_at <= as_of)


def policy_state(register: Sequence[PolicyEntry], as_of: datetime) -> PolicyState:
    """The policy state as of the decision instant `as_of`, from announcement only."""

    in_force, pending = [], []
    for entry in known_entries(register, as_of):
        require_announced(entry, as_of)
        if entry.effective is not None and entry.effective <= as_of.date():
            in_force.append(entry)
        else:
            pending.append(entry)
    return PolicyState(as_of, tuple(in_force), tuple(pending))
