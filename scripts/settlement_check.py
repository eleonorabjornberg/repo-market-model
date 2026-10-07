"""Does the settlement driver pick up the 15th, month-end and Thursday/Tuesday bills? (#339)

Eleonora's ruling on #339 states the Treasury settlement pattern: 3-, 10- and 30-year notes and bonds settle on
the 15th (or the next business day); 2-, 5- and 7-year notes settle on the last day of the month; bills mostly
settle on Thursdays, some on Tuesdays. This script lists, for 2018-04-03 to 2025-12-31, the days the published
panel's settlement columns flag against that pattern and every mismatch, from the tracked Treasury auction
snapshot. It reads two inputs (the published panel and the tracked auction snapshot) and writes JSON; it changes
no feature, panel or record. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/settlement_check.py --panel PUB.csv --output OUT/settlement_check.json

`PUB.csv` is the published panel (`docs/pivot/next-session.md`). Standard library only.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUCTIONS = (REPO / "tests/fixtures/snapshots/funding_inputs/treasury_auctions"
            / "20260914T051023Z_722359ea9bc7.json")
FIRST = date(2018, 4, 3)
LAST = date(2025, 12, 31)  # the last day read; the lockbox's near-blind tier starts on 2026-01-01
COUPON_TYPES = ("Note", "Bond")


def kind(record: dict) -> str:
    """The pattern's name for an auction record, from its own fields.

    `mid_month`: 3-, 10- and 30-year nominal securities, with the reopenings the snapshot labels by remaining
    term (`9-Year 10-Month`, `29-Year 11-Month`). `month_end`: 2-, 5- and 7-year nominal notes. `other`: FRNs,
    TIPS, 20-year bonds and anything else the snapshot carries as a Note or Bond.
    """
    if record["floating_rate"] == "Yes" or record["inflation_index_security"] == "Yes":
        return "other"
    term = record["security_term"]
    if term in ("3-Year", "10-Year", "30-Year") or term.startswith(("9-Year", "29-Year")):
        return "mid_month"
    if term in ("2-Year", "5-Year", "7-Year"):
        return "month_end"
    return "other"


def check(panel_rows: list[dict], auction_rows: list[dict]) -> dict:
    """The comparison. `panel_rows` are the panel's dict rows, `auction_rows` the snapshot's `data`."""
    days = sorted(date.fromisoformat(r["date"]) for r in panel_rows if FIRST <= date.fromisoformat(r["date"]) <= LAST)
    by_day = {date.fromisoformat(r["date"]): r for r in panel_rows}

    def next_business_day(day: date):
        return next((d for d in days if d >= day), None)  # None: the panel ends first

    expected: dict[date, str] = {}
    for year in range(FIRST.year, LAST.year + 1):
        for month in range(1, 13):
            if not FIRST <= date(year, month, 28) <= LAST:
                continue
            for day, name in ((date(year, month, 15), "mid_month"),
                              (date(year, month, calendar.monthrange(year, month)[1]), "month_end")):
                settles = next_business_day(day)
                if settles is not None:
                    expected[settles] = name

    coupon_days = {d for d in days if float(by_day[d]["treasury_settlement_coupons"]) > 0}
    bill_days = {d for d in days if float(by_day[d]["treasury_settlement_bills"]) > 0}

    # What the snapshot says settles on each day (issue_date), by the pattern's names.
    issued: dict[date, Counter] = defaultdict(Counter)
    bill_issue_days: Counter = Counter()
    for r in auction_rows:
        day = date.fromisoformat(r["issue_date"])
        if not FIRST <= day <= LAST:
            continue
        if r["security_type"] in COUPON_TYPES:
            issued[day][kind(r)] += 1
        elif r["security_type"] in ("Bill", "CMB"):
            bill_issue_days[(r["security_type"], day.strftime("%a"))] += 1

    missed = sorted(d for d in expected if d not in coupon_days)
    # Dates the pattern names that the panel flags, by pattern.
    pattern_flagged = {d: expected[d] for d in expected if d in coupon_days}
    extra = {}
    for d in sorted(coupon_days - set(expected)):
        extra[d] = dict(issued.get(d, {}))
    unexplained_by_data = sorted(d for d in coupon_days if d not in issued)
    # The data's own mid-month and month-end settlements that are not on the pattern's dates.
    off_pattern_data = {}
    for d, kinds in sorted(issued.items()):
        for k in ("mid_month", "month_end"):
            if kinds.get(k) and expected.get(d) != k:
                off_pattern_data.setdefault(d.isoformat(), {})[k] = kinds[k]

    weekday = Counter(d.strftime("%a") for d in bill_days)
    # Tuesday bill settlements begin in the snapshot's own history (4- and 8-week bills moved to Tuesday in
    # December 2018), so a Tuesday is expected to carry bills only from the first Tuesday issue on.
    first_tuesday = min((date.fromisoformat(r["issue_date"]) for r in auction_rows
                         if r["security_type"] in ("Bill", "CMB")
                         and date.fromisoformat(r["issue_date"]).strftime("%a") == "Tue"
                         and date.fromisoformat(r["issue_date"]) >= FIRST), default=None)
    tue_thu_without_bills = [d.isoformat() for d in days
                             if d not in bill_days and (d.strftime("%a") == "Thu"
                                                        or (d.strftime("%a") == "Tue" and first_tuesday and d >= first_tuesday))]

    announced_late = sorted(
        {r["issue_date"] for r in auction_rows
         if FIRST <= date.fromisoformat(r["issue_date"]) <= LAST
         and r["announcemt_date"] not in ("null", None)
         and date.fromisoformat(r["announcemt_date"]) >= date.fromisoformat(r["issue_date"])})

    by_year = {}
    for year in range(FIRST.year, LAST.year + 1):
        in_year = [d for d in expected if d.year == year]
        by_year[str(year)] = {
            "pattern_dates": len(in_year),
            "pattern_dates_flagged": sum(1 for d in in_year if d in coupon_days),
            "other_coupon_days_flagged": sum(1 for d in extra if d.year == year),
        }
    return {
        "window": [FIRST.isoformat(), LAST.isoformat()],
        "pattern_dates": {d.isoformat(): k for d, k in sorted(expected.items())},
        "pattern_dates_not_flagged": [d.isoformat() for d in missed],
        "pattern_dates_flagged": len(pattern_flagged),
        "flagged_outside_pattern": {d.isoformat(): v for d, v in extra.items()},
        "flagged_without_a_coupon_issue_in_snapshot": [d.isoformat() for d in unexplained_by_data],
        "snapshot_mid_month_or_month_end_issues_off_pattern_dates": off_pattern_data,
        "by_year": by_year,
        "bills": {
            "flagged_by_weekday": dict(sorted(weekday.items())),
            "snapshot_issue_weekday_by_type": {f"{t} {w}": n for (t, w), n in sorted(bill_issue_days.items())},
            "first_tuesday_bill_issue": first_tuesday.isoformat() if first_tuesday else None,
            "thursdays_and_tuesdays_since_the_first_without_bills": tue_thu_without_bills,
        },
        "issue_dates_announced_on_or_after_the_issue_date": announced_late,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    with args.panel.open(newline="") as handle:
        panel = [r for r in csv.DictReader(handle) if date.fromisoformat(r["date"]) <= LAST]
    auctions = json.loads(AUCTIONS.read_text())["data"]
    result = check(panel, auctions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in result.items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
