"""Prospective logging for scoring protocol v1 (#656; `docs/decisions/scoring-protocol.md` §11 and §12 item 2).

The live record (`scripts/live_record.py`) writes one frozen file per business day, before any outcome of that day
exists. From record version 3 the file also carries a `protocol` block, built here:

- the 23-quantile forecast for h = 1..5 of **B1** and **B2** (`protocol_benchmarks`), made at the decision instant
  of `docs/decisions/information-set.md`;
- **B3**, the incumbent: the published v1 declaration forecasts five levels, and §4 does not say how it is put on the
  23-level grid, so the block names it (`B3`) and points at the five-level forecast the same file already carries
  under `distributions.published`; it maps nothing (`protocol_benchmarks.b3_forecast` refuses a forecast off the grid);
- every **registered candidate**'s forecast on the same grid (`REGISTERED_CANDIDATES`; none yet. A registration is
  Eleonora's attested action, and the tuple changes only with it);
- the **H7m hook**: a registered estimate read from a liquidity-repository snapshot pinned by digest (Eleonora's
  decision on eleonorabjornberg/repo-market-liquidity#20, Q4). Built only; nothing is registered (`REGISTERED_H7M`).

**The guards.** A block is refused (`LookAheadError`) when it is written at or after 23:59 ET on its decision day
(`require_written_by_decision_day_end`; Eleonora's ruling on #740, a reading of protocol §1: 16:00 would refuse every
scheduled live-log run, and the outcome's first print, about 08:00, leaves the target day's session open), or at or
after the instant its first outcome is published (`require_written_before_outcome`, which the cut-off now precedes).
The block stores `written_at`, and `filled_candidate` refuses a day whose stored `written_at` or commit time is past
the cut-off. An H7m estimate is refused when the snapshot's digest is not the pinned one
(`ValueError`), or when the estimate was made available after the decision instant (`LookAheadError`).

**Missing days (§11).** A candidate must log every business day. `filled_candidate` reads a log back and scores a day
without the candidate's forecast as B1's forecast, counts it, and voids the registration above 5% missing
(`scoring_protocol.fill_missing`). B1 is a function of the panel as of the day, so a day whose file was never written
at all takes B1 rebuilt from that panel (`b1_by_day`); without it the day is refused, never silently skipped.

Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Optional, Sequence
from zoneinfo import ZoneInfo

from . import protocol_benchmarks as pb
from . import scoring_protocol as sp
from .asof import InformationRule
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .splits import LookAheadError

PROTOCOL_VERSION = 1
EASTERN = ZoneInfo("America/New_York")

#: The candidates logged each day. A registration (Eleonora's attested action, protocol §2) adds one; none is registered.
REGISTERED_CANDIDATES: tuple = ()
#: The H7m estimates logged each day: a registered liquidity-repository snapshot digest. None is registered.
REGISTERED_H7M: tuple = ()

#: B3 is named in the block, not mapped: see the module docstring.
B3 = {
    "on_grid": False,
    "reference": "distributions.published.quantiles_bps",
    "reason": "the published v1 declaration forecasts five levels; how it is put on the protocol's 23-level grid is not decided",
}
H7M_KEYS = ("snapshot_sha256", "day", "available_at", "deployable", "lower", "upper", "state")
BLOCK_KEYS = ("version", "grid", "benchmarks", "candidates", "h7m", "written_at")
#: A block is written and committed before this time on its decision day (Eleonora's ruling on #740, 14 October 2026).
DECISION_DAY_CUTOFF = time(23, 59)


# -- the write-before-outcome guard ------------------------------------------------------------------------------------


def outcome_published_at(
    dates: Sequence[date], decision_index: int, registry: Mapping[str, Mapping[str, object]], decision_time: time
) -> datetime:
    """When the first outcome of the decision on row `decision_index` is public: the h = 1 target's SOFR and IORB.

    A naive datetime on the market's clock, as `InformationRule` dates every read. The later leads' outcomes are
    published later still, so the first is the instant the whole block must precede.
    """

    rule = InformationRule(registry, (), decision_time=decision_time, horizon=1)
    return rule.availability(dates, rule.groups[0].fields, decision_index + 1)


def require_written_before_outcome(written_at: datetime, published_at: datetime) -> None:
    """Refuse a record written at or after the instant its first outcome is published.

    Raises:
        ValueError: `written_at` carries no time zone (it cannot be placed against the market's clock).
        LookAheadError: the record was written at or after `published_at`.
    """

    if written_at.tzinfo is None:
        raise ValueError("the instant a record is written needs a time zone")
    local = written_at.astimezone(EASTERN).replace(tzinfo=None)
    if local >= published_at:
        raise LookAheadError(
            f"the record was written at {local.isoformat()}, not before its first outcome is published at "
            f"{published_at.isoformat()}"
        )


def require_written_by_decision_day_end(written_at: datetime, decision_day: date) -> None:
    """Refuse a record written at or after 23:59 ET on its decision day (#740).

    Raises:
        ValueError: `written_at` carries no time zone.
        LookAheadError: the record was written at or after the cut-off (a record made on an earlier day passes).
    """

    if written_at.tzinfo is None:
        raise ValueError("the instant a record is written needs a time zone")
    local = written_at.astimezone(EASTERN).replace(tzinfo=None)
    if local >= datetime.combine(decision_day, DECISION_DAY_CUTOFF):
        raise LookAheadError(
            f"the record for {decision_day} was written at {local.isoformat()}, not before "
            f"{DECISION_DAY_CUTOFF.isoformat(timespec='minutes')} ET on its decision day"
        )


# -- the block ---------------------------------------------------------------------------------------------------------


def _vector(values: Sequence[float], where: str) -> List[float]:
    out = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{where} holds a value that is not a finite number: {value!r}")
        out.append(float(value))
    if len(out) != len(sp.GRID):
        raise ValueError(f"{where} holds {len(out)} quantiles; the grid has {len(sp.GRID)}")
    if any(b < a for a, b in zip(out, out[1:])):
        raise ValueError(f"{where} has crossing quantiles")
    return out


def _leads(forecast: Mapping, where: str) -> Dict[str, List[float]]:
    got = {str(h) for h in forecast}
    if got != {str(h) for h in sp.HORIZONS}:
        raise ValueError(f"{where} carries leads {sorted(got)}, not {[str(h) for h in sp.HORIZONS]}")
    return {str(h): _vector(forecast[h] if h in forecast else forecast[str(h)], f"{where}, lead {h}") for h in sp.HORIZONS}


def protocol_block(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    written_at: datetime,
    candidates: Optional[Mapping[str, Mapping[int, Sequence[float]]]] = None,
    h7m: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    """The `protocol` block of the decision on row `decision_index` of `panel`.

    `panel` carries the decision day's row and its five target rows (the calendar columns at least), as
    `protocol_benchmarks` requires. `written_at` is the instant the record is being made.

    Raises:
        LookAheadError: `written_at` is not before the first outcome's publication, or a benchmark would read a row
            after the anchor.
        ValueError: a candidate's forecast is off the grid, crossing, or misses a lead.
    """

    dates = [row.date for row in panel]
    require_written_by_decision_day_end(written_at, dates[decision_index])
    require_written_before_outcome(written_at, outcome_published_at(dates, decision_index, registry, decision_time))
    b1 = pb.b1_forecast(panel, decision_index, registry=registry, decision_time=decision_time)
    b2 = pb.b2_forecast(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits)
    block = {
        "version": PROTOCOL_VERSION,
        "grid": list(sp.GRID),
        "benchmarks": {
            "b1": _leads(b1, "B1"),
            "b2": _leads(b2, "B2"),
            "b3": dict(B3),
        },
        "candidates": {
            str(name): _leads(forecast, f"candidate {name}") for name, forecast in sorted((candidates or {}).items())
        },
        "h7m": None if h7m is None else dict(h7m),
        "written_at": written_at.astimezone(EASTERN).isoformat(),
    }
    validate_protocol_block(block)
    return block


def validate_protocol_block(block: object, decision_day: Optional[date] = None) -> None:
    """The block's schema. Raises `ValueError` naming what is wrong.

    With `decision_day`, also refuses (`LookAheadError`) a block whose stored `written_at` is past the cut-off.
    """

    if not isinstance(block, dict) or set(block) != set(BLOCK_KEYS):
        raise ValueError(f"a protocol block holds exactly {list(BLOCK_KEYS)}")
    if block["version"] != PROTOCOL_VERSION:
        raise ValueError(f"protocol.version must be {PROTOCOL_VERSION}")
    if list(block["grid"]) != list(sp.GRID):
        raise ValueError("protocol.grid must be the scoring protocol's 23 levels")
    benchmarks = block["benchmarks"]
    if not isinstance(benchmarks, dict) or set(benchmarks) != {"b1", "b2", "b3"}:
        raise ValueError("protocol.benchmarks holds exactly b1, b2 and b3")
    for name in ("b1", "b2"):
        _leads(benchmarks[name], f"protocol.benchmarks.{name}")
    if benchmarks["b3"] != B3:
        raise ValueError("protocol.benchmarks.b3 is the incumbent's note, not a forecast on the grid")
    if not isinstance(block["candidates"], dict):
        raise ValueError("protocol.candidates is a mapping")
    for name, forecast in block["candidates"].items():
        _leads(forecast, f"protocol.candidates.{name}")
    h7m = block["h7m"]
    if h7m is not None and (not isinstance(h7m, dict) or set(h7m) != set(H7M_KEYS)):
        raise ValueError(f"protocol.h7m is null or holds exactly {list(H7M_KEYS)}")
    try:
        written_at = datetime.fromisoformat(block["written_at"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"protocol.written_at is not an ISO instant: {exc}") from exc
    if written_at.tzinfo is None:
        raise ValueError("protocol.written_at needs a time zone")
    if decision_day is not None:
        require_written_by_decision_day_end(written_at, decision_day)


# -- missing days (§11) ------------------------------------------------------------------------------------------------


def _b1_stand_ins(
    blocks: Mapping[date, Mapping], b1_by_day: Optional[Mapping[date, Mapping[int, Sequence[float]]]]
) -> Dict[date, Dict[int, Sequence[float]]]:
    out = {day: {int(h): q for h, q in block["benchmarks"]["b1"].items()} for day, block in blocks.items()}
    for day, forecast in (b1_by_day or {}).items():
        out.setdefault(day, {int(h): q for h, q in forecast.items()})
    return out


def filled_candidate(
    blocks: Mapping[date, Mapping],
    candidate_id: str,
    decision_days: Sequence[date],
    *,
    committed_at: Mapping[date, datetime],
    b1_by_day: Optional[Mapping[date, Mapping[int, Sequence[float]]]] = None,
) -> sp.Filled:
    """The candidate's logged forecasts over `decision_days`, B1's standing in where one is missing (§11).

    `blocks` maps a decision day to its `protocol` block. A day with no block, or a block without the candidate, is
    missing. `b1_by_day` supplies B1 for a day with no block at all (rebuilt from the panel as of that day).
    `committed_at` maps each logged day to the commit time of its file; a day's stored `written_at` and commit time
    must both be before 23:59 ET on its decision day (#740).

    Raises:
        LookAheadError: a block was written or committed at or after the cut-off on its decision day.
        ValueError: a logged day has no commit time, or a block is malformed.
        RegistrationVoid: more than 5% of the days are missing.
        ProtocolError: a missing day has no B1 to stand in.
    """

    candidate: Dict[date, Dict[int, Sequence[float]]] = {}
    for day, block in blocks.items():
        validate_protocol_block(block, decision_day=day)
        if day not in committed_at:
            raise ValueError(f"the log for {day} has no commit time to check against the cut-off")
        require_written_by_decision_day_end(committed_at[day], day)
        logged = block["candidates"].get(candidate_id)
        if logged is not None:
            candidate[day] = {int(h): q for h, q in logged.items()}
    return sp.fill_missing(candidate, _b1_stand_ins(blocks, b1_by_day), decision_days)


# -- the H7m hook ------------------------------------------------------------------------------------------------------


def read_h7m_estimate(
    snapshot: bytes, pinned_sha256: str, day: date, decision_instant: datetime
) -> Dict[str, object]:
    """The registered estimate for `day`, read from a liquidity-repository snapshot pinned by digest.

    The snapshot is JSON, `{"estimates": [{"day", "available_at", "deployable", "lower", "upper", "state"}, ...]}`,
    with `available_at` an ISO instant with a zone. Only the row for `day` is read, and only if it was available at
    or before `decision_instant`. The format is a proposal, to be agreed with the liquidity repository; nothing is
    registered (`REGISTERED_H7M`).

    Raises:
        ValueError: the snapshot's SHA-256 is not `pinned_sha256`, it is not the format above, or it has no row for `day`.
        LookAheadError: the row was made available after the decision instant.
    """

    digest = hashlib.sha256(snapshot).hexdigest()
    if digest != pinned_sha256:
        raise ValueError(f"the snapshot's digest is {digest}, not the pinned {pinned_sha256}")
    try:
        rows = json.loads(snapshot.decode("utf-8"))["estimates"]
        row = next((r for r in rows if r["day"] == day.isoformat()), None)
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"the snapshot is not an H7m estimates file: {exc}") from exc
    if row is None:
        raise ValueError(f"the snapshot has no estimate for {day}")
    available_at = datetime.fromisoformat(row["available_at"])
    if available_at.tzinfo is None:
        raise ValueError("an estimate's available_at needs a time zone")
    if decision_instant.tzinfo is None:
        raise ValueError("the decision instant needs a time zone")
    if available_at > decision_instant:
        raise LookAheadError(
            f"the estimate for {day} was made available at {available_at.isoformat()}, after the decision "
            f"instant {decision_instant.isoformat()}"
        )
    out = {
        "snapshot_sha256": digest, "day": day.isoformat(), "available_at": available_at.isoformat(),
        "deployable": row["deployable"], "lower": row["lower"], "upper": row["upper"], "state": row["state"],
    }
    if set(out) != set(H7M_KEYS):
        raise ValueError("internal: the estimate's keys drifted from H7M_KEYS")
    return out
