"""Small command-line interface for the initial modeling workflow."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .baseline import rolling_persistence_backtest
from .data import DataContractError, audit_panel, load_daily_panel
from .ingest import fetch_fred_macro, fetch_nyfed_reference_rate


def _audit(path: Path) -> int:
    report = audit_panel(load_daily_panel(path))
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


def _backtest(path: Path, minimum_history: int) -> int:
    rows = load_daily_panel(path)
    audit_panel(rows)
    report = rolling_persistence_backtest(rows, minimum_history=minimum_history)
    print(
        json.dumps(
            {
                "forecast_count": len(report.forecasts),
                "mae_bps": round(report.mae_bps, 4),
                "interval_coverage": round(report.interval_coverage, 4),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repo-model")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="validate and summarize a daily panel")
    audit.add_argument("path", type=Path)

    backtest = subparsers.add_parser("backtest", help="run the persistence benchmark")
    backtest.add_argument("path", type=Path)
    backtest.add_argument("--minimum-history", type=int, default=20)

    fetch = subparsers.add_parser("fetch", help="download an immutable public-data snapshot")
    fetch.add_argument("source", choices=("nyfed-sofr", "fred-macro"))
    fetch.add_argument("--start", default="2018-04-03", help="effective start date")
    fetch.add_argument("--end", default=date.today().isoformat(), help="effective end date")
    fetch.add_argument("--output-root", type=Path, default=Path("data/raw"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            return _audit(args.path)
        if args.command == "backtest":
            return _backtest(args.path, args.minimum_history)
        if args.command == "fetch":
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
    except (DataContractError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
