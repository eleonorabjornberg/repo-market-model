"""Track A's command-line surface: the data layer's subcommands.

Owned by **Track A (data layer)**. The ownership gate fails a
`feature/model-eval` branch that touches this file.

`src/repo_model/cli.py` is a dispatcher that names no command. To add one, add
it here: build the subparser and call `set_defaults(handler=...)` on it. Nothing
outside this file changes -- not the dispatcher, not the contract, not the gate.
A handler takes the parsed namespace and returns an exit code; it may raise
`OSError` or any `ValueError` subclass (`DataContractError` is one) and the
dispatcher will print it and exit 2.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .data import audit_panel, load_daily_panel
from .ingest import fetch_fred_macro, fetch_nyfed_reference_rate


def _audit(args: argparse.Namespace) -> int:
    report = audit_panel(load_daily_panel(args.path))
    print(
        json.dumps(
            {
                "rows": report.row_count,
                "start_date": report.start_date.isoformat(),
                "end_date": report.end_date.isoformat(),
                "missing_counts": report.missing_counts,
                "warnings": list(report.warnings),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _fetch(args: argparse.Namespace) -> int:
    if args.source == "nyfed-sofr":
        artifacts = fetch_nyfed_reference_rate(
            output_root=args.output_root,
            rate_name="sofr",
            start=args.start,
            end=args.end,
        )
    else:
        artifacts = fetch_fred_macro(output_root=args.output_root)
    print(json.dumps([artifact.as_dict() for artifact in artifacts], indent=2))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Add the data layer's subcommands to the shared parser."""

    audit = subparsers.add_parser("audit", help="validate and summarize a daily panel")
    audit.add_argument("path", type=Path)
    audit.set_defaults(handler=_audit)

    fetch = subparsers.add_parser(
        "fetch", help="download an immutable public-data snapshot"
    )
    fetch.add_argument("source", choices=("nyfed-sofr", "fred-macro"))
    fetch.add_argument("--start", default="2018-04-03", help="effective start date")
    fetch.add_argument(
        "--end", default=date.today().isoformat(), help="effective end date"
    )
    fetch.add_argument("--output-root", type=Path, default=Path("data/raw"))
    fetch.set_defaults(handler=_fetch)
