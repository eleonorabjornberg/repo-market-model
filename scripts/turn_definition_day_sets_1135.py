#!/usr/bin/env python3
"""Which business days change reporting day type under the month-end turn record (#1135), from the calendar alone.

No panel, no score and no day after 2025-12-31 is read: the legacy type is `SplitDeclaration.legacy_reporting_day_type`, the new
one `turn_days.turn_day_type`, both functions of the date and `metadata/market_holidays.json`. Prints a markdown table.

    PYTHONPATH=src python3 scripts/turn_definition_day_sets_1135.py
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import turn_days as td  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

#: The holiday table starts 2018-01-01, so the turn label of January 2018 (which needs December 2017) is refused; start in February.
FIRST_DAY = date(2018, 2, 1)
LAST_DAY = date(2025, 12, 31)


def table(splits=None) -> str:
    splits = splits or load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
    first = FIRST_DAY
    changes = td.day_set_changes(first, LAST_DAY, splits=splits)
    lines = [f"Business days {first} to {LAST_DAY}, calendar only.", "", "| legacy type | turn-record type | days |", "|---|---|---|"]
    for (old, new), days in sorted(changes["relabelled"].items()):
        lines.append(f"| {old} | {new} | {len(days)} |")
    by_regime = Counter()
    for day in changes["leave_month_end"]:
        by_regime[("leave", splits.regime(day))] += 1
    for day in changes["join_turn"]:
        by_regime[("join", splits.regime(day))] += 1
    lines += ["", "| regime | leave month_end | join a turn type |", "|---|---|---|"]
    for label in splits.regime_labels:
        lines.append(f"| {label} | {by_regime[('leave', label)]} | {by_regime[('join', label)]} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(table())
