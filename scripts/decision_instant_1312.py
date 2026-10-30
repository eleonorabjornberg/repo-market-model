"""The source audit for moving the decision instant from 16:00 to 18:00 New York time (#1312, step 1 of 3).

Her ruling of 29 October 2026 (relayed on #1312, ledger item 77): a forecast is made at 18:00 on the last panel day
before the scored day, not at 16:00. This script answers, from `metadata/sources.json` and the published panel's dates
and from nothing else, three questions about the move:

1. **Which declared availabilities does the window 16:00 to 18:00 hold?** (`window_declarations`.) A source whose
   first-observable instant falls after 16:00 and at or before 18:00 was invisible to the old decision and is visible
   to the new one. The H.15 at 16:15 (IORB, IOER, EFFR, the bill rates at 16:30), the H.4.1 weeklies at 16:30 (Thursday,
   as the registry's conservative five-day lag counts them), the weekly FR 2004 at 16:30 and the H.8 at 16:15.
2. **Which forecasts read a different row?** (`moves`.) For every declared field and every scored day, the latest row
   public at the decision instant, under the old instant and under the new one, from the registry's own declared
   availability (`asof.declared_availability`) and the same scan the as-of rule makes (`InformationRule._latest`).
3. **Does anything the target day's spread is computed from become visible?** (`target_day_leaks`.) The spread of day
   `T` is SOFR(T) minus IORB(T). Neither value of `T` is public at the decision on the day before it, at 18:00 or at any
   instant on that day: SOFR(T) prints at 08:00 on the next business day (declared 15:00), IORB(T) is public at 16:15
   on `T` itself. The check reads the registry and refuses (`LookAheadError`) if a declaration ever said otherwise.

It reads no outcome and scores nothing. The studies that run at a recorded instant (the dated `metadata/*.json`
declarations) are not rewritten; `OTHER_READERS` lists what else reads the instant and what was done with each.

    python3 scripts/decision_instant_1312.py audit --panel PUB.csv --output docs/research/decision-instant-1312/audit.json
    python3 scripts/decision_instant_1312.py check

`check` reads the committed audit and the registry and fails when the audit no longer describes the registry (a source
declared inside the window that the audit does not list, or a listed move that is not the registry's). Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import asof  # noqa: E402
from repo_model.decision_instant import DECISION_TIME, LEGACY_DECISION_TIME  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
RECORD = REPO / "docs" / "research" / "decision-instant-1312" / "audit.json"

#: The clock in `available_time` of a declaration that is keyed on the decision instant itself and so must equal it.
DECISION_KEYED = (("fed_iorb_announcements", "scheduled_availability"),)

#: What else reads the decision instant, and what the pull request that moved it did with each. The test checks that every
#: path exists; the rest is the account the pull request body carries.
OTHER_READERS = (
    {"reader": "metadata/sources_measurement.json", "instant": "16:00 (ten fields: ON RRP, SRF, OFR, same-day sensitivities)",
     "done": "unchanged: a measurement registry whose instants are declared source publication instants, not the decision "
             "instant; every one is at or before 16:00, so no row moves"},
    {"reader": "metadata/h41_release_dating.json", "instant": "16:30 Thursday, measured and off",
     "done": "unchanged: no published declaration reads it (the per-release H.4.1 reading is still off in the registry)"},
    {"reader": "metadata/sources_pd_financing_1296.json", "instant": "16:30 Thursday (FR 2004), a dated study's source",
     "done": "unchanged: a record of #1296; its source is not in the registry"},
    {"reader": "metadata/settlement_announcement_dating.json", "instant": "12:00 on the announcement date",
     "done": "unchanged: the declared instant is 12:00, before both instants; #1301 found four announcements stated later "
             "(12:50, 13:30, 13:30, 16:15), all before 18:00"},
    {"reader": "metadata/srf_cap_1241.json", "instant": "16:00 (announcement instant of the SRF line)",
     "done": "unchanged: a dated study's declaration; `srf_line.DECISION_TIME` keeps the 16:00 it records"},
    {"reader": "src/repo_model/gcf_index.py", "instant": "DTCC GCF Repo Index, posted about 16:00 to 16:05 (her Mac, 27 to 29 October)",
     "done": "decision instant now 18:00, so a fetch from 16:00 to 18:00 is a capture and not `fetched_after_decision`; a "
             "record made at 16:00 still reads against the instant it declares"},
)


def _declared(registry: Mapping[str, Mapping[str, object]]) -> List[Tuple[str, str]]:
    """Every (source, field) pair the registry makes a row-relative availability claim for."""

    pairs = []
    for source_id, source in registry.items():
        if not isinstance(source, Mapping):
            continue
        fields = list(source.get("fields") or ())
        for field in (source.get("field_release_lags") or {}):
            if field not in fields:
                fields.append(field)
        for field in fields:
            pairs.append((source_id, field))
    return pairs


def _block(registry: Mapping[str, Mapping[str, object]], source_id: str, field: str) -> Optional[dict]:
    """The block that dates `field`: the scheduled block, the field's own lag, or the source's."""

    source = registry[source_id]
    scheduled = source.get(asof.SCHEDULED_AVAILABILITY_KEY)
    if isinstance(scheduled, Mapping) and field in (scheduled.get("fields") or ()):
        return {"kind": "scheduled", **{k: scheduled.get(k) for k in ("basis", "unit", "days", "available_time")}}
    lag = (source.get("field_release_lags") or {}).get(field) or source.get("release_lag") or {}
    if lag.get("days") is None or lag.get("basis") == "snapshot_retrieved_at":
        return None
    return {"kind": "observed", **{k: lag.get(k) for k in ("basis", "unit", "days", "available_time")}}


def window_declarations(
    registry: Mapping[str, Mapping[str, object]], old: time = LEGACY_DECISION_TIME, new: time = DECISION_TIME
) -> List[dict]:
    """The declared fields whose first-observable clock falls after `old` and at or before `new`.

    A field with no row-relative claim (a snapshot basis) is left out: the as-of rule cannot read it at all.
    """

    found = []
    for source_id, field in _declared(registry):
        block = _block(registry, source_id, field)
        if block is None:
            continue
        clock = time.fromisoformat(str(block["available_time"] or "23:59"))
        if old < clock <= new:
            found.append({"source": source_id, "field": field, **block})
    return found


def _latest_readable(registry, source_id, field, dates, scored, clock) -> int:
    """The latest row before `scored` public at `clock` on the day before it (the as-of rule's scan); -1 if none."""

    deadline = datetime.combine(dates[scored - 1], clock)
    position = scored - 1
    while position >= 0:
        moment = asof.declared_availability(registry, source_id, field, dates, position)
        if moment is not None and moment <= deadline:
            return position
        position -= 1
    return position


def moves(
    registry: Mapping[str, Mapping[str, object]],
    dates: Sequence[date],
    old: time = LEGACY_DECISION_TIME,
    new: time = DECISION_TIME,
) -> List[dict]:
    """For each declared field, how many scored days read a later row at `new` than at `old`, and by how many rows."""

    out = []
    for source_id, field in _declared(registry):
        block = _block(registry, source_id, field)
        if block is None:
            continue
        shifts: Dict[int, int] = {}
        weekdays: Dict[str, int] = {}
        for scored in range(1, len(dates)):
            before = _latest_readable(registry, source_id, field, dates, scored, old)
            after = _latest_readable(registry, source_id, field, dates, scored, new)
            if before < 0 or after < 0:
                continue
            if after != before:
                shifts[after - before] = shifts.get(after - before, 0) + 1
                name = dates[scored - 1].strftime("%A")
                weekdays[name] = weekdays.get(name, 0) + 1
        out.append({
            "source": source_id, "field": field, **block,
            "days_moved": sum(shifts.values()),
            "rows_later": {str(k): v for k, v in sorted(shifts.items())},
            "decision_weekdays": dict(sorted(weekdays.items())),
        })
    return out


def target_day_leaks(
    registry: Mapping[str, Mapping[str, object]], dates: Sequence[date], clock: time = DECISION_TIME
) -> List[dict]:
    """Every scored day on which a value of the target day itself is public at the decision instant. Empty is the answer.

    The target `spread_bps` is composed of `sofr` and `iorb` (`asof.TARGET_COLUMNS`). For each scored day `T`, the first
    instant each component's value *for `T`* is public must come after the decision instant on the day before `T`.
    """

    from repo_model.contract import field_sources_for_features

    leaks = []
    for source_id, field in field_sources_for_features((asof.TARGET,)):
        for scored in range(1, len(dates)):
            moment = asof.declared_availability(registry, source_id, field, dates, scored)
            deadline = datetime.combine(dates[scored - 1], clock)
            if moment is not None and moment <= deadline:
                leaks.append({"source": source_id, "field": field, "scored": dates[scored].isoformat(),
                              "public_at": moment.isoformat(), "decision": deadline.isoformat()})
    return leaks


def require_no_target_leak(registry, dates, clock: time = DECISION_TIME) -> None:
    """Raise `LookAheadError` when a value of the target day is public at the decision instant."""

    leaks = target_day_leaks(registry, dates, clock)
    if leaks:
        first = leaks[0]
        raise LookAheadError(
            f"{first['source']}.{first['field']} for {first['scored']} is public at {first['public_at']}, "
            f"at or before the {first['decision']} decision ({len(leaks)} such days)"
        )


def decision_keyed_problems(registry: Mapping[str, Mapping[str, object]], clock: time = DECISION_TIME) -> List[str]:
    """Declarations keyed on the decision instant whose `available_time` is not `clock`."""

    problems = []
    for source_id, key in DECISION_KEYED:
        block = registry[source_id][key]
        if time.fromisoformat(block["available_time"]) != clock:
            problems.append(f"{source_id}.{key}.available_time is {block['available_time']}, not {clock.isoformat('minutes')}")
    return problems


def panel_dates(path: Path) -> List[date]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        column = next(reader).index("date")
        return [date.fromisoformat(row[column]) for row in reader]


def build_record(registry: Mapping[str, Mapping[str, object]], dates: Sequence[date]) -> dict:
    require_no_target_leak(registry, dates)
    moved = moves(registry, dates)
    return {
        "directive": 1312,
        "old_instant": LEGACY_DECISION_TIME.isoformat("minutes"),
        "new_instant": DECISION_TIME.isoformat("minutes"),
        "panel": {"first": dates[0].isoformat(), "last": dates[-1].isoformat(), "rows": len(dates)},
        "window": window_declarations(registry),
        "moves": [m for m in moved if m["days_moved"]],
        "unmoved": sorted(f"{m['source']}.{m['field']}" for m in moved if not m["days_moved"]),
        "target_day_leaks": target_day_leaks(registry, dates),
        "decision_keyed": [f"{s}.{k}" for s, k in DECISION_KEYED],
        "other_readers": list(OTHER_READERS),
        "reads_no_outcome": True,
    }


def audit_command(args) -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    record = build_record(registry, panel_dates(args.panel))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"moves": len(record["moves"]), "window": len(record["window"]), "output": str(args.output)}))
    return 0


def check_command(args) -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    problems = decision_keyed_problems(registry)
    listed = {(e["source"], e["field"]) for e in record["window"]}
    now = {(e["source"], e["field"]) for e in window_declarations(registry)}
    if listed != now:
        problems.append(f"the window holds {sorted(now ^ listed)} that the audit does not account for")
    if record["target_day_leaks"]:
        problems.append("the audit records a target-day leak")
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="write the audit record from the registry and a panel's dates")
    audit.add_argument("--panel", type=Path, required=True)
    audit.add_argument("--output", type=Path, default=RECORD)
    audit.set_defaults(run=audit_command)
    check = sub.add_parser("check", help="the committed audit still describes the registry")
    check.set_defaults(run=check_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
