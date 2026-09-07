"""Track B's command-line surface: the model and evaluation subcommands.

Owned by **Track B (model and evaluation)**. The ownership gate fails a
`feature/data-layer` branch that touches this file.

`src/repo_model/cli.py` is a dispatcher that names no command. To add one, add
it here: build the subparser and call `set_defaults(handler=...)` on it. Nothing
outside this file changes -- not the dispatcher, not the contract, not the gate.
A handler takes the parsed namespace and returns an exit code; it may raise
`OSError` or any `ValueError` subclass (`SplitError` is one) and the dispatcher
will print it and exit 2.

`event-holdout` lives here, added without touching `cli.py`, which is the
property "Decided: who owns the CLI" was written to get.

Reading Track A's modules from here is fine and expected -- `load_daily_panel`
is imported, not edited. Only writes are gated.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import json
from datetime import time
from pathlib import Path

from .baseline import climatology_exceedance, rolling_persistence_backtest
from .data import audit_panel, load_daily_panel, load_stress_thresholds
from .event_eval import evaluate_event_window, load_events_file
from .registry import max_release_lag_days
from .splits import SplitError


def _purge_days(args: argparse.Namespace) -> int:
    """The gap, from `registry.max_release_lag_days` over the named sources.

    Both evaluation paths reach it through this one function. `_event_holdout`'s
    docstring states the design and it is not path-specific: the gap is a
    function of which sources the features come from, `--source` is how a caller
    changes it, and `--decision-time` is required because a default would be a
    silent assumption about when the forecast is made.
    """

    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    return max_release_lag_days(
        registry, args.source, decision_time=time.fromisoformat(args.decision_time)
    )


def _backtest(args: argparse.Namespace) -> int:
    """Run the purged rolling-origin benchmark and report what sized the gap.

    **There is no `--purge` here either.** The event path has not had one since
    it was written, and the two paths now mean the same thing by a gap and take
    the number from the same place -- which was already written down in
    `_event_holdout` and is only now true. A hand-set gap on this path would be
    reached for at exactly the moment it must not be: the purge drops training
    rows, a short panel then has fewer origins, and the flag would be right
    there.

    `purge_days` and `sources` are reported beside the metrics for the reason
    `model_config` carries them on the event path: a benchmark whose gap came
    from somewhere an auditor cannot follow is not a benchmark.
    """

    rows = load_daily_panel(args.path)
    audit_panel(rows)
    purge = _purge_days(args)
    report = rolling_persistence_backtest(
        rows, purge=purge, minimum_history=args.minimum_history
    )
    print(
        json.dumps(
            {
                "forecast_count": len(report.forecasts),
                "mae_bps": round(report.mae_bps, 4),
                "interval_coverage": round(report.interval_coverage, 4),
                "purge_days": purge,
                "sources": sorted(args.source),
                "minimum_history": args.minimum_history,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _event_holdout(args: argparse.Namespace) -> int:
    """Score declared knowledge-holdout windows, once each, and report the curves.

    Every number this command needs that somebody else declared, it reads from
    where they declared it. That is the whole design, and it is the same rule
    three times:

    * **The windows** come from `event_eval.load_events_file`, whose path is
      `--events`. Boundaries are never constants in evaluator code, and a
      command that defaulted the path would be naming Track A's layout.
    * **The tau family** comes from `data.load_stress_thresholds`, whose path is
      `--thresholds`. `AGENT_CONTRACT.md` declares `{5, 10, 20, 50}` bp and
      Track A's file carries it; this module contains no tau.
    * **The purge gap** comes from `registry.max_release_lag_days` over the
      sources named by `--source`, exactly as `rolling_origin`'s caller sizes
      it. The two evaluation paths mean the same thing by a gap and take the
      number from the same place.

    **There is no `--purge`.** A flag that set it by hand would be a way to
    shrink the gap at the one moment shrinking it is tempting -- when the
    training set that cleared it turned out to be too short -- and the row it
    would admit is a row published after the window opened. The gap is a
    function of which sources the features come from, so naming the sources is
    how a caller changes it, and that change is one an auditor can follow.

    Reruns are visible, not blocked. `event_eval` appends a record per scoring
    and refuses to deduplicate; whether a second run was authorised is a
    question for the human reading the journal, and this command does not
    invent an answer it was not given either.
    """

    rows = load_daily_panel(args.panel)
    dates = [row.date for row in rows]
    spreads = [row.spread_bps for row in rows]

    declaration = load_stress_thresholds(args.thresholds)
    taus = tuple(float(tau) for tau in declaration["taus_bp"])

    purge = _purge_days(args)

    windows = load_events_file(args.events)
    if args.window:
        declared = {window.name: window for window in windows}
        unknown = [name for name in args.window if name not in declared]
        if unknown:
            raise SplitError(
                f"{args.events} declares no window named {', '.join(unknown)}; "
                f"it declares {', '.join(sorted(declared))}"
            )
        windows = tuple(declared[name] for name in args.window)

    fit_predict = climatology_exceedance(minimum_history=args.minimum_history)
    model_config = {
        "model": "climatology",
        "minimum_history": args.minimum_history,
        "taus_bp": list(taus),
        "purge_days": purge,
        "sources": sorted(args.source),
    }

    reported = []
    for window in windows:
        report = evaluate_event_window(
            dates,
            spreads,
            fit_predict,
            window,
            purge,
            taus=taus,
            model_config=model_config,
            journal_path=args.journal,
        )
        reported.append(
            {
                "window": {
                    "name": report.window.name,
                    "start": report.window.start.isoformat(),
                    "end": report.window.end.isoformat(),
                    "checksum": report.window.checksum,
                },
                "holdout_role": report.record.holdout_role,
                "purge_days": report.purge_days,
                "train_rows": report.train_rows,
                "last_train_date": report.last_train_date.isoformat(),
                "taus_bp": list(report.taus),
                # The exceedance curve and the realized path, and nothing that
                # aggregates them. AGENT_CONTRACT.md, "Metrics": "Event windows
                # get the exceedance curve and realized path. No aggregate Brier
                # or reliability number on a single event window." Ten stressed
                # days cannot support a calibration statistic, and one printed
                # here would be averaged into the main table by whoever read the
                # two as the same kind of number.
                "days": [
                    {
                        "date": when.isoformat(),
                        "realized_bps": realized,
                        "exceedance": list(curve),
                    }
                    for when, realized, curve in zip(
                        report.scored_dates, report.realized, report.exceedance
                    )
                ],
            }
        )

    print(json.dumps(reported, indent=2, sort_keys=True))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Add the model and evaluation subcommands to the shared parser."""

    backtest = subparsers.add_parser(
        "backtest", help="run the purged rolling-origin benchmark"
    )
    backtest.add_argument("path", type=Path)
    backtest.add_argument("--minimum-history", type=int, default=20)
    backtest.add_argument("--registry", type=Path, required=True)
    backtest.add_argument(
        "--source",
        action="append",
        required=True,
        metavar="ID",
        help="a feature source, repeatable; these size the purge gap",
    )
    backtest.add_argument("--decision-time", required=True, metavar="HH:MM")
    # No --purge. See _backtest.
    backtest.set_defaults(handler=_backtest)

    holdout = subparsers.add_parser(
        "event-holdout",
        help="score declared knowledge-holdout windows, once each",
    )
    holdout.add_argument("--panel", type=Path, required=True)
    holdout.add_argument(
        "--events",
        type=Path,
        required=True,
        help="the declared event-window file; no default, it is not ours to name",
    )
    holdout.add_argument("--thresholds", type=Path, required=True)
    holdout.add_argument("--registry", type=Path, required=True)
    holdout.add_argument(
        "--journal",
        type=Path,
        required=True,
        help="append-only provenance log; a scoring that is not recorded did not happen",
    )
    holdout.add_argument(
        "--source",
        action="append",
        required=True,
        metavar="ID",
        help="a feature source, repeatable; these size the purge gap",
    )
    holdout.add_argument("--decision-time", required=True, metavar="HH:MM")
    holdout.add_argument(
        "--window",
        action="append",
        metavar="NAME",
        help="score only this declared window, repeatable; default is all of them",
    )
    holdout.add_argument("--minimum-history", type=int, default=20)
    # No --purge. See _event_holdout.
    holdout.set_defaults(handler=_event_holdout)
