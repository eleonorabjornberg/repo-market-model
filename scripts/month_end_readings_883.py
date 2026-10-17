"""The two month-end readings, measured side by side (#883, H5 groundwork G1 / step 3).

A scratch measurement, not a record: it changes no definition, no default and no page. `repo_model.risk_dates` keeps two readings of the
month-end part of a day type: the split declaration's window (`SplitDeclaration.day_type`: `days_to_month_end` at most
`month_end_window` calendar days) and the reporting reading (`SplitDeclaration.reporting_day_type`: one of the month's last two business
days, `data.in_last_business_days_of_month`). Which one is shared is Eleonora's open ruling (#800). This script lists the days on which
they disagree and re-reads the ordinary-day headlines of four pages under both. It recommends nothing.

Development data, not a verdict (scoring protocol v1, #640). No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/month_end_readings_883.py days --published PUBLISHED.csv --output days.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
LAST_DAY = date(2025, 12, 31)
#: a pressure day, for the list only: the spread, on whole basis points, above this (`data.exceeds_bp`).
PRESSURE_BP = 5.0
WINDOW, REPORTING = "window", "reporting"


def reading_type(splits, reading: str, row) -> str:
    """The pressure-day type of `row` under one reading."""

    if reading == WINDOW:
        return splits.day_type(row.values)
    if reading == REPORTING:
        return splits.reporting_day_type(row.date, row.values)
    raise ValueError(f"unknown reading {reading!r}; use {WINDOW!r} or {REPORTING!r}")


def disagreeing_days(rows, splits):
    """Every panel day up to `LAST_DAY` whose day type differs between the two readings."""

    out = []
    for row in rows:
        if row.date > LAST_DAY:
            continue
        window, reporting = reading_type(splits, WINDOW, row), reading_type(splits, REPORTING, row)
        if window == reporting:
            continue
        spread = row.spread_bps
        out.append({
            "date": row.date.isoformat(),
            "window": window,
            "reporting": reporting,
            "month_end_by": ("both" if "month_end" in (window, reporting) and window == reporting else
                              "window only" if window == "month_end" else "reporting only"),
            "spread_bp": None if spread is None else round(float(spread), 3),
            "pressure_day": None if spread is None else bool(exceeds_bp(spread, PRESSURE_BP)),
        })
    return out


def summarise(days):
    by_year = Counter(d["date"][:4] for d in days)
    by_type = Counter(f"{d['window']} -> {d['reporting']}" for d in days)
    return {"days": len(days), "by_year": dict(sorted(by_year.items())), "by_type": dict(by_type),
            "pressure_days": sum(1 for d in days if d["pressure_day"])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    days = sub.add_parser("days", help="list the days on which the two readings disagree")
    days.add_argument("--published", type=Path, required=True)
    days.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    require_unlocked([LAST_DAY], where="month_end_readings_883")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    listed = disagreeing_days(rows, load_split_declaration(SPLITS))
    args.output.write_text(json.dumps({"summary": summarise(listed), "days": listed}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summarise(listed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
