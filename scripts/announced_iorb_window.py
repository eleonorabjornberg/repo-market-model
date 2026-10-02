"""Paired losses inside and outside ±N business days of each IORB change (directive #38).

    python3 scripts/announced_iorb_window.py PANEL.csv REPORT.json [REPORT.json ...] --days 3

Each REPORT is a `repo_model.cli compare` record. The window is every panel row
within `--days` panel rows of an effective date in the tracked implementation
note table (`kind` `change`), the effective date's own row included. For each
report it prints the paired mean difference (model_a's loss less model_b's, the
record's own sign convention) over the window and outside it, each with a
stationary-bootstrap interval at the record's own block length, level and
replication count, and a fixed seed.

The window is a split of origins the record already scored, not a new
selection: it reads no outcome, and it is the one the directive names.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model.announced_iorb import load_announcements  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402

TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
SEED = 38


def window_dates(dates: list, days: int) -> set:
    effective = [row.effective for row in load_announcements(TABLE) if row.kind == "change"]
    out = set()
    for day in effective:
        if not dates[0] <= day <= dates[-1]:
            continue
        at = min(i for i, d in enumerate(dates) if d >= day)
        out.update(dates[max(0, at - days) : at + days + 1])
    return out


def summarise(values: list, interval: dict) -> dict:
    if not values:
        return {"count": 0}
    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx),
        len(values),
        block_length=interval["block_length"],
        seed=SEED,
        replications=interval["replications"],
        level=interval["level"],
    )
    return {"count": len(values), "mean": sum(values) / len(values), "lower": lower, "upper": upper}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("panel", type=Path)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--days", type=int, required=True)
    args = parser.parse_args(argv)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        dates = [date.fromisoformat(row["date"]) for row in csv.DictReader(handle)]
    window = window_dates(dates, args.days)
    result = {}
    for path in args.reports:
        record = json.loads(path.read_text(encoding="utf-8"))
        comparison = record["comparison"]
        inside, outside = [], []
        for origin in comparison["per_origin"]:
            target = inside if date.fromisoformat(origin["scored_date"]) in window else outside
            target.append(origin["difference_bps"])
        interval = comparison["mean_difference_interval"]
        result[path.name] = {
            "loss": comparison["loss"],
            "sign_convention": comparison["sign_convention"],
            "window_days": args.days,
            "inside": summarise(inside, interval),
            "outside": summarise(outside, interval),
            "bootstrap": {**{k: interval[k] for k in ("block_length", "level", "replications")}, "seed": SEED},
        }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
