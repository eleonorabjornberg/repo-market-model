"""Small command-line interface for the initial modeling workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .baseline import rolling_persistence_backtest
from .data import DataContractError, audit_panel, load_daily_panel


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            return _audit(args.path)
        if args.command == "backtest":
            return _backtest(args.path, args.minimum_history)
    except (DataContractError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

