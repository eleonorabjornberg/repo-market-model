"""Write a panel with the two announced-IORB columns added (directive #38).

    python3 scripts/announced_iorb_panel.py PANEL.csv OUT.csv --decision-time 16:00 --before 2026-01-01

Reads a built panel, adds `iorb_announced_change_bps` and
`iorb_days_to_announced_change` from the tracked implementation-note table
(`repo_model.announced_iorb`), and writes the result. Every other column is
copied as the panel wrote it. `--before` drops every row on or after that date,
so no comparison run on the output scores a day `docs/decisions/lockbox.md`
locks. The output is a scratch input to `repo_model.cli compare`, never a
published panel.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model.announced_iorb import FEATURES, announced_iorb_features, load_announcements  # noqa: E402

TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("panel", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--decision-time", required=True, type=time.fromisoformat)
    parser.add_argument("--before", type=date.fromisoformat)
    args = parser.parse_args(argv)

    with args.panel.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or ())
        rows = [row for row in reader]
    clash = [name for name in FEATURES if name in columns]
    if clash:
        raise SystemExit(f"{args.panel} already carries {clash}")
    if args.before is not None:
        rows = [row for row in rows if date.fromisoformat(row["date"]) < args.before]
    dates = [date.fromisoformat(row["date"]) for row in rows]
    added = announced_iorb_features(dates, load_announcements(TABLE), decision_time=args.decision_time)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns + list(FEATURES), lineterminator="\n")
        writer.writeheader()
        for row, values in zip(rows, added):
            writer.writerow(
                {**row, **{name: "" if value is None else repr(value) for name, value in values.items()}}
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
