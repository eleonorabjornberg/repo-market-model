"""Track B's command-line surface: the model and evaluation subcommands.

Owned by **Track B (model and evaluation)**. The ownership gate fails a
`feature/data-layer` branch that touches this file.

`src/repo_model/cli.py` is a dispatcher that names no command. To add one, add
it here: build the subparser and call `set_defaults(handler=...)` on it. Nothing
outside this file changes -- not the dispatcher, not the contract, not the gate.
A handler takes the parsed namespace and returns an exit code; it may raise
`OSError` or any `ValueError` subclass (`SplitError` is one) and the dispatcher
will print it and exit 2.

This file is where the `event-holdout` subcommand belongs when it is written. It
was held out of Track B's event-window block only because `cli.py` had no owner;
that is now settled, and the subcommand is ordinary Track B work.

Reading Track A's modules from here is fine and expected -- `load_daily_panel`
is imported, not edited. Only writes are gated.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baseline import rolling_persistence_backtest
from .data import audit_panel, load_daily_panel


def _backtest(args: argparse.Namespace) -> int:
    rows = load_daily_panel(args.path)
    audit_panel(rows)
    report = rolling_persistence_backtest(
        rows, minimum_history=args.minimum_history
    )
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


def register(subparsers: argparse._SubParsersAction) -> None:
    """Add the model and evaluation subcommands to the shared parser."""

    backtest = subparsers.add_parser(
        "backtest", help="run the persistence benchmark"
    )
    backtest.add_argument("path", type=Path)
    backtest.add_argument("--minimum-history", type=int, default=20)
    backtest.set_defaults(handler=_backtest)
