"""Per-field staleness and imputation flags for a live-record row (#1132; #984 part 4; H5 groundwork G3).

A forecast reads each declared input at the latest value public at its decision instant
(`docs/decisions/information-set.md`). The record has said so only in aggregate (`asof.information_summary`). This
module writes, for one decision and for each horizon, what each declared feature actually was:

- `age_hours`: how long the observation behind the value had been observable at the decision instant, counted from the
  observation's own declared instant (`FieldRead.observation_hours`); `None` for a calendar column, which has no
  publication;
- `latest_public`: whether the row read is the latest whose declared instant is at or before the decision instant (the
  staleness guard's test, `InformationRule.check`, recorded instead of raised). A calendar or scheduled read is the
  latest when it is read at the scored row;
- `carried`: a weekly value carried on a later panel row than its own print (`docs/decisions/weekly-carry.md`), so its
  age is not its row's age;
- `imputed`: the cell read is a hole (`None`) at that row. A fitted model either fills a hole from its training-window
  mean (`baseline.FittedArx`) or refuses it; the record says the hole was there, not which.

The flags are facts. No threshold is set here, and what age counts as too stale is not decided. The block is built from
the same `InformationRule` reads the forecasts use, so it cannot name a value the forecast did not read.

Raises `LookAheadError` for a read whose declared instant is after the decision (a leak); `ValueError` for a malformed
block or a feature the registry cannot date. Stdlib only.
"""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

from .asof import KIND_CALENDAR, KIND_OBSERVED, KIND_SCHEDULED, InformationRule
from .splits import LookAheadError

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "field_flags_block": (
        "not_entry",
        "reads the as-of information set of the rows a live record's forecasts already read, only to flag "
        "each field's age, carry and imputation; it scores nothing, selects no scored day, and the live "
        "record's own scoring path refuses a locked day",
    ),
}

FIELD_FLAGS_VERSION = 1
FLAG_KEYS = ("age_hours", "latest_public", "carried", "imputed")
CELL_KEYS = ("kind", "fields", "read_date", "rows_before_scored") + FLAG_KEYS
BLOCK_KEYS = ("version", "basis", "horizons")
KINDS = (KIND_OBSERVED, KIND_SCHEDULED, KIND_CALENDAR)
BASIS = {
    "age_hours": (
        "hours from the declared instant of the observation behind the value to the decision instant; null for a "
        "calendar column"
    ),
    "latest_public": (
        "true when no later row than the one read was observable at the decision instant (a calendar or scheduled "
        "read: it is read at the scored row)"
    ),
    "carried": "true for a weekly value carried on a later panel row than its own print",
    "imputed": "true when the cell read is a hole at that row; a model fills it from its training mean or refuses it",
}


def flag_read(rule: InformationRule, dates: Sequence, rows: Sequence, info, read, group) -> Dict[str, object]:
    """The flags of one `FieldRead` of `info`, with the read's own descriptors.

    Raises:
        LookAheadError: the read's declared instant is after the decision instant.
    """

    if read.available_at is not None and read.available_at > info.decision_instant:
        raise LookAheadError(
            f"{read.feature!r} reads {dates[read.row]}, first observable at {read.available_at}, after the "
            f"{info.decision_instant} decision"
        )
    if read.kind == KIND_OBSERVED:
        following = read.row + 1
        latest_public = not (
            following < info.scored_index
            and rule.availability(dates, read.fields, following) <= info.decision_instant
        )
    else:
        latest_public = read.row == info.scored_index
    carried = (
        read.hours is not None
        and read.observation_hours is not None
        and read.observation_hours != read.hours
    )
    imputed = any(rows[read.row].values.get(column) is None for column in group.columns)
    return {
        "kind": read.kind,
        "fields": [f"{source}.{field}" for source, field in read.fields],
        "read_date": dates[read.row].isoformat(),
        "rows_before_scored": read.rows,
        "age_hours": None if read.observation_hours is None else round(read.observation_hours, 4),
        "latest_public": latest_public,
        "carried": carried,
        "imputed": imputed,
    }


def field_flags_block(
    panels: Mapping[int, Sequence],
    features: Mapping[int, Sequence[str]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time,
) -> Dict[str, object]:
    """The record's `field_flags` block.

    `panels[h]` is the panel extended through the h-th target (as `live_record.extend_panel` makes it): its last row
    is the scored row, and the decision instant is `decision_time` on the row `h` panel days before it. `features[h]`
    are the declared features read at that horizon.
    """

    horizons: Dict[str, object] = {}
    for h in sorted(panels):
        rows = panels[h]
        dates = [row.date for row in rows]
        rule = InformationRule(registry, tuple(dict.fromkeys(features[h])), decision_time=decision_time, horizon=h)
        info = rule.information_set(dates, len(rows) - 1)
        horizons[str(h)] = {
            read.feature: flag_read(rule, dates, rows, info, read, group)
            for read, group in zip(info.reads, rule.groups)
        }
    block = {"version": FIELD_FLAGS_VERSION, "basis": dict(BASIS), "horizons": horizons}
    validate_field_flags_block(block)
    return block


def validate_field_flags_block(block: object) -> None:
    """The block's schema. Raises `ValueError` naming what is wrong."""

    if not isinstance(block, dict) or set(block) != set(BLOCK_KEYS):
        raise ValueError(f"a field_flags block holds exactly {list(BLOCK_KEYS)}")
    if block["version"] != FIELD_FLAGS_VERSION:
        raise ValueError(f"field_flags.version must be {FIELD_FLAGS_VERSION}")
    if not isinstance(block["basis"], dict) or set(block["basis"]) != set(FLAG_KEYS):
        raise ValueError(f"field_flags.basis must explain exactly {list(FLAG_KEYS)}")
    horizons = block["horizons"]
    if not isinstance(horizons, dict) or not horizons:
        raise ValueError("field_flags.horizons must map each horizon to its features")
    for h, cells in horizons.items():
        if not isinstance(cells, dict) or not cells:
            raise ValueError(f"field_flags.horizons[{h}] must map each feature to its flags")
        for feature, cell in cells.items():
            where = f"field_flags.horizons[{h}][{feature}]"
            if not isinstance(cell, dict) or set(cell) != set(CELL_KEYS):
                raise ValueError(f"{where} holds exactly {list(CELL_KEYS)}")
            if cell["kind"] not in KINDS:
                raise ValueError(f"{where}.kind must be one of {list(KINDS)}")
            for key in ("latest_public", "carried", "imputed"):
                if not isinstance(cell[key], bool):
                    raise ValueError(f"{where}.{key} must be true or false")
            age = cell["age_hours"]
            if (age is None) != (cell["kind"] == KIND_CALENDAR) or (
                age is not None and (isinstance(age, bool) or not isinstance(age, (int, float)) or age < 0)
            ):
                raise ValueError(f"{where}.age_hours must be null for a calendar column and hours >= 0 otherwise")
