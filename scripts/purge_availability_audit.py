"""Audit the purge against the decision instant, fold by fold.

`splits.clears_purge` states the gap against the *target* date: a row is eligible
when ``row_date + purge < opens``. The decision is made at the declared decision
time on the last panel day strictly before the scored date, which is the calendar
day before only when the two are consecutive. After a weekend or a holiday the
decision is earlier than that, so the rule alone stops establishing that the last
training row was published by then.

This script measures the distance, for a published run record, two ways:

* **stated** -- the conservative gap the run was purged at, at the slowest
  source's declared availability time;
* **actual** -- each field's own declared release lag in `metadata/sources.json`,
  business days counted on the panel's own dates.

A fold is reported when availability falls after the decision instant. The stated
view failing and the actual view passing is the expected shape: the purge is
allowed to purge more than the evidence requires, never less.

A business-day lag that runs off the end of the panel is late, not unknown. The panel is the only calendar this script has; a value whose declared
publication day is not on it has not been published by any instant the panel can
name, and the evaluation path settled the same case the same way (block B29,
`tests/test_baseline.py`). Returning `None` there -- which this script did -- made the
audit silently skip exactly the folds at the end of the panel, where a long-lagged
column is least likely to have arrived. That is the direction an audit must not fail
in. The two remaining `None`s mean something else and stay: a snapshot-timestamp basis
is not a row-relative lag at all, and a source declaring no `days` has made no claim to
check.

    python3 scripts/purge_availability_audit.py [RECORD] [PANEL]
"""

import csv
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from repo_model import splits  # noqa: E402

# Later than any deadline the panel can express, so a field whose declared publication
# day runs off the panel is reported late rather than skipped.
NEVER_ON_THIS_PANEL = datetime.max

DEFAULT_RECORD = "docs/runs/backtest_gbm_cross_conformal_mh61.json"
DEFAULT_PANEL = "data/processed/funding_panel.csv"


def panel_dates(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return [date.fromisoformat(row["date"]) for row in csv.DictReader(handle)]


def field_availability(registry, source_id, field, row, dates, index):
    """First instant the field's value for `row` is declared observable."""
    source = registry[source_id]
    lags = source.get("field_release_lags") or {}
    lag = lags.get(field) or source.get("release_lag") or {}
    if lag.get("basis") == "snapshot_retrieved_at":
        return None  # inherits a snapshot timestamp; not a row-relative lag
    days = lag.get("days")
    if days is None:
        return None
    moment = time.fromisoformat(lag.get("available_time", "23:59"))
    if lag.get("unit") == "business_days":
        i = index[row] + days
        if i >= len(dates):
            return NEVER_ON_THIS_PANEL
        return datetime.combine(dates[i], moment)
    return datetime.combine(row + timedelta(days=int(days)), moment)


def main(argv):
    record_path = argv[1] if len(argv) > 1 else DEFAULT_RECORD
    panel_path = argv[2] if len(argv) > 2 else DEFAULT_PANEL
    record = json.loads(Path(record_path).read_text(encoding="utf-8"))
    declaration, derived = record["declaration"], record["derived"]
    purge = derived["purge_days"]
    decision = time.fromisoformat(declaration["decision_time"])
    registry = json.loads(Path("metadata/sources.json").read_text(encoding="utf-8"))
    dates = panel_dates(panel_path)
    index = {value: position for position, value in enumerate(dates)}
    folds = list(
        splits.rolling_origin(
            dates, min_train=declaration["minimum_history"], step=1, purge=purge
        )
    )
    stated_time = max(
        time.fromisoformat(
            (registry[source].get("release_lag") or {}).get("available_time", "00:00")
        )
        for source in derived["sources"]
    )
    pairs = [tuple(name.split(".", 1)) for name in derived["fields"]]

    print("record %s" % record_path)
    print("folds reproduced: %d, %s .. %s" % (len(folds), dates[folds[0][1][0]], dates[folds[-1][1][0]]))
    late = {"stated": [], "actual": []}
    for train, test in folds:
        row, scored = dates[train[-1]], dates[test[0]]
        position = index[scored]
        if position == 0:
            continue
        deadline = datetime.combine(dates[position - 1], decision)
        stated = datetime.combine(row + timedelta(days=purge), stated_time)
        if stated > deadline:
            late["stated"].append((scored, row, (stated - deadline).total_seconds() / 86400.0))
        for source_id, field in pairs:
            actual = field_availability(registry, source_id, field, row, dates, index)
            if actual is not None and actual > deadline:
                late["actual"].append((scored, row, "%s.%s" % (source_id, field)))
                break
    for view in ("stated", "actual"):
        entries = late[view]
        if not entries:
            print("%s: clear" % view)
            continue
        worst = max(entries, key=lambda entry: entry[2] if isinstance(entry[2], float) else 0)
        print("%s: late on %d folds; worst scored %s (last row %s) by %s"
              % (view, len(entries), worst[0], worst[1],
                 "%.2f days" % worst[2] if isinstance(worst[2], float) else worst[2]))
    return 1 if late["actual"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
