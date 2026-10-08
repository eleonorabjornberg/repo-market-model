"""Measurement fields from the new point-in-time sources (#377): the scratch panel.

A scratch measurement input, not a record: it writes a CSV and a summary to the
paths it is given, and nothing into `docs/runs/`. Every column is off in every
published declaration (`repo_model.measurement_fields`); a track switches them
on for its own run with `switched_on()`.

    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel PUBLISHED.csv --output AUG.csv

`panel` adds to the published panel the raw columns (SOFR's 1st and 99th
percentiles, the daily TGA, the OFR tri-party and GCF rates) from the tracked
snapshots and then the derived ones, and keeps the rows up to 2025-12-31
(`docs/decisions/lockbox.md`). A track that scores with the columns does so
inside `switched_on()`:

    with measurement_fields_script.switched_on():
        ...  # contract.FEATURE_FIELDS carries measurement_fields.COLUMN_FIELDS
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402

SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
#: The published panel's build cutoff (`metadata/funding_panel_manifest.json`).
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
#: The last day any comparison may score, or any row of the scratch panel carry
#: (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)


@contextlib.contextmanager
def switched_on():
    """`measurement_fields.COLUMN_FIELDS` in the feature map, for this run only."""

    fields = dict(measurement_fields.COLUMN_FIELDS)
    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{
                    column: tuple(sorted({source for source, _f in pairs}))
                    for column, pairs in fields.items()
                },
            }
        ),
    ):
        yield


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    published = load_daily_panel(args.panel)
    rows, summary = measurement_fields.assemble(
        published, SNAPSHOTS, cutoff=BUILD_CUTOFF, end=END
    )
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + list(measurement_fields.RAW_COLUMNS) + list(measurement_fields.DERIVED_COLUMNS)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary.update(
        output=str(args.output),
        sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
        rows=len(rows),
        first=rows[0].date.isoformat(),
        last=rows[-1].date.isoformat(),
    )
    print(json.dumps(summary, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel", help="the published panel plus the measurement fields")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
