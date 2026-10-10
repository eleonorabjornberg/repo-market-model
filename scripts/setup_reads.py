#!/usr/bin/env python3
"""The staleness of what a forecast reads (#517): a correction to the data-integrity check of `setup_diagnostic.py`.

**Reported only. No model change, no bar change, nothing published moves, no 2026 day is read.**
`setup_diagnostic.py` measured how long a value had stayed unchanged on the panel rows, which for a weekly series carried
on later rows is at most about a week by construction. This script reads each scored day through the as-of rule
(`asof.InformationRule.information_set`), the way the forecast does, and measures the age of the weekly observation it
reads, in calendar days from its Wednesday to the decision day, and which panel row the daily rates are read from.

    PYTHONPATH=src python3 scripts/setup_reads.py --panel PUB.csv --output OUT/setup_reads.json --markdown OUT/setup_reads.md

`PUB.csv` is the published panel (digest `4ddc3882…`). The threshold of 7 calendar days is the one the setup diagnostic's
blinding rule used (`metadata/setup_diagnostic.json`, `data_integrity.checks.repeat`).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields  # noqa: E402
from repo_model import pressure as pressure_module  # noqa: E402
from repo_model import setup_diagnostic as sd  # noqa: E402
from repo_model.asof import InformationRule, fold_grid  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

LAST = date(2025, 12, 31)
DECISION = time(16, 0)
MINIMUM_HISTORY = 61
HORIZONS = (1, 2, 3, 4, 5)
THRESHOLD_DAYS = 7
TAU = 5.0
WEEKLY = ("reserve_balances", "tga", "dealer_treasury_position")
DAILY = ("spread_bps",)
COPY_COLUMNS = ("sofr", "sofr_volume", "sofr_p25", "sofr_p75", "tgcr", "bgcr")
WINDOW = 10


def measure(rows, dates, registry) -> dict:
    """Ages of the weekly reads and the rows of the daily read, over every scored day and around each episode."""

    raw = [dict(r.values) for r in rows]
    grids = {
        h: [i for i in fold_grid(dates, registry, decision_time=DECISION, minimum_history=MINIMUM_HISTORY, horizon=h) if dates[i] <= LAST]
        for h in HORIZONS
    }
    shared = sorted(set.intersection(*(set(dates[i] for i in grid) for grid in grids.values())))
    onsets = pressure_module.onsets(rows, TAU, shared)
    position = {d: k for k, d in enumerate(dates)}
    out = {"threshold_calendar_days": THRESHOLD_DAYS, "onsets": [d.isoformat() for d in onsets], "horizons": {}, "episodes": {}}
    per_day = {}
    for h in HORIZONS:
        rule = InformationRule(registry, WEEKLY + DAILY, decision_time=DECISION, horizon=h)
        ages = {f: [] for f in WEEKLY}
        daily_rows_back, copied_at_read, stale_days = {}, 0, 0
        for i in grids[h]:
            info = rule.information_set(dates, i)
            decision_day = info.decision_instant.date()
            reads = {read.feature: read for read in info.reads}
            day_ages = {f: sd.read_age_days(decision_day, dates[reads[f].row]) for f in WEEKLY}
            for f, age in day_ages.items():
                ages[f].append(age)
            back = reads["spread_bps"].rows
            daily_rows_back[str(back)] = daily_rows_back.get(str(back), 0) + 1
            copied = sd.is_copied_row(raw, reads["spread_bps"].row, COPY_COLUMNS)
            copied_at_read += int(copied)
            stale = [f for f, age in day_ages.items() if age > THRESHOLD_DAYS]
            stale_days += int(bool(stale))
            per_day[(h, dates[i])] = {"ages": day_ages, "spread_rows_back": back, "copied_at_the_row_read": copied, "stale": stale}
        out["horizons"][str(h)] = {
            "scored_days": len(grids[h]),
            "weekly_age_days": {f: sd.age_summary(ages[f], threshold=THRESHOLD_DAYS) for f in WEEKLY},
            "scored_days_with_a_weekly_read_older_than_the_threshold": stale_days,
            "spread_read_panel_days_before_the_scored_day": dict(sorted(daily_rows_back.items())),
            "scored_days_whose_spread_row_read_is_a_copied_row": copied_at_read,
        }
    for onset in onsets:
        entry = {}
        for h in HORIZONS:
            window = [dates[k] for k in range(max(position[onset] - WINDOW, 0), position[onset])]
            cells = [per_day[(h, d)] for d in window if (h, d) in per_day]
            entry[str(h)] = {
                "decision_days_read": len(cells),
                "stale_reads": sorted({f for c in cells for f in c["stale"]}),
                "days_with_a_stale_read": sum(1 for c in cells if c["stale"]),
                "copied_rows_read": sum(1 for c in cells if c["copied_at_the_row_read"]),
                "at_the_onset": per_day.get((h, onset)),
            }
        out["episodes"][onset.isoformat()] = entry
    return out


def markdown(doc: dict) -> str:
    lines = [
        "# What the forecast reads: the age of the weekly observations (#517)",
        "",
        f"Age = calendar days from the observation's Wednesday to the decision day, read through the as-of rule. Threshold: {doc['threshold_calendar_days']} days.",
        "",
        "| h | scored days | feature | min / median / max (days) | reads older than the threshold | scored days with any weekly read older | spread read, panel days before the scored day | copied row read |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for h, block in doc["horizons"].items():
        rows_back = ", ".join(f"{k}: {v}" for k, v in block["spread_read_panel_days_before_the_scored_day"].items())
        for n, (feature, summary) in enumerate(block["weekly_age_days"].items()):
            first = n == 0
            lines.append(
                f"| {h if first else ''} | {block['scored_days'] if first else ''} | {feature} | {summary['min']:g} / {summary['median']:g} / {summary['max']:g} | "
                f"{summary['older_than_threshold']} of {summary['reads']} | "
                f"{block['scored_days_with_a_weekly_read_older_than_the_threshold'] if first else ''} | {rows_back if first else ''} | "
                f"{block['scored_days_whose_spread_row_read_is_a_copied_row'] if first else ''} |"
            )
    lines += ["", "Distribution of ages (days: reads), h = 1:", ""]
    for feature, summary in doc["horizons"]["1"]["weekly_age_days"].items():
        lines.append(f"* {feature}: " + ", ".join(f"{k}: {v}" for k, v in sorted(summary["by_age"].items(), key=lambda kv: int(kv[0]))))
    lines += [
        "",
        f"Around each of the {len(doc['onsets'])} episodes, the {WINDOW} panel days before it that the judge scores, at h = 1 (stale = a weekly read older than the threshold):",
        "",
        "| episode | decision days | days with a stale read | features | copied rows read |",
        "|---|---|---|---|---|",
    ]
    for day, by_h in doc["episodes"].items():
        cell = by_h["1"]
        lines.append(f"| {day} | {cell['decision_days_read']} | {cell['days_with_a_stale_read']} | {', '.join(cell['stale_reads']) or 'none'} | {cell['copied_rows_read']} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    rows = [r for r in load_daily_panel(args.panel) if r.date <= LAST]
    dates = [r.date for r in rows]
    sd.require_window(dates, LAST)
    require_unlocked([LAST], where="setup_reads")
    audit_panel(rows)
    doc = measure(rows, dates, measurement_fields.load_registry())
    doc["panel_sha256"] = panel_sha256(args.panel)
    args.output.write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(doc), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "onsets": len(doc["onsets"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
