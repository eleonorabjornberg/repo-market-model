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
from .contract import sources_for_features
from .data import audit_panel, load_daily_panel, load_stress_thresholds
from .event_eval import evaluate_event_window, load_events_file
from .splits import SplitError


def _registry(args: argparse.Namespace) -> dict:
    """The parsed source registry at `--registry`. One reader, two commands."""

    return json.loads(Path(args.registry).read_text(encoding="utf-8"))


def _derived_sources(args: argparse.Namespace) -> tuple[str, ...]:
    """The sources the declared feature set draws on.

    `contract.sources_for_features` is the only supported way from a feature set
    to source IDs, and this module makes no second attempt at the mapping. There
    is no `--source`: sources are derived, never supplied. A caller who could
    name the sources by hand could name a set that did not cover what the model
    reads, and the gap computed from it would be correct arithmetic over the
    wrong evidence -- which is the failure that survives every check the purge
    block installed, because the number itself looks fine.
    """

    return sources_for_features(args.feature)


# There is no `_purge_days` here any more. Both evaluation paths derive the gap
# inside the function that uses it, from the feature set the caller declared, so
# this module hands over `--feature`, `--registry` and `--decision-time` and
# never holds the number. A gap computed here and passed in would be a second
# place the number could come from, and the CLI is the one place a caller would
# reach to change it.


def _backtest(args: argparse.Namespace) -> int:
    """Run the purged rolling-origin benchmark and report what sized the gap.

    **There is no `--purge` here either.** The event path has not had one since
    it was written, and the two paths now mean the same thing by a gap and take
    the number from the same place -- which was already written down in
    `_event_holdout` and is only now true. A hand-set gap on this path would be
    reached for at exactly the moment it must not be: the purge drops training
    rows, a short panel then has fewer origins, and the flag would be right
    there.

    **And there is no `--source`.** The gap is derived from the sources, and the
    sources are derived from the declared feature set. A caller who could name
    the sources by hand could name a set that did not cover what the model
    reads; the purge would then be computed correctly over the wrong evidence,
    and nothing downstream could tell. `--feature` is the one declaration, and
    everything else follows from it.

    `features`, `sources` and `purge_days` are reported beside the metrics for
    the reason `model_config` carries them on the event path: a benchmark whose
    gap came from somewhere an auditor cannot follow is not a benchmark. All
    three are read off the report rather than recomputed here, so what is
    printed is what shaped the run.
    """

    rows = load_daily_panel(args.path)
    audit_panel(rows)
    report = rolling_persistence_backtest(
        rows,
        features=args.feature,
        registry=_registry(args),
        decision_time=time.fromisoformat(args.decision_time),
        minimum_history=args.minimum_history,
    )
    print(
        json.dumps(
            {
                "forecast_count": len(report.forecasts),
                "mae_bps": round(report.mae_bps, 4),
                "interval_coverage": round(report.interval_coverage, 4),
                "features": sorted(report.features),
                "purge_days": report.purge_days,
                "sources": sorted(report.sources),
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
      sources `contract.sources_for_features` derives from `--feature`, exactly
      as the rolling path sizes it. The two evaluation paths mean the same thing
      by a gap and take the number from the same place, by the same derivation
      -- and, since this block, in the same place: `evaluate_event_window`
      derives it, and this command passes the declaration rather than the gap.

    **There is no `--purge`.** A flag that set it by hand would be a way to
    shrink the gap at the one moment shrinking it is tempting -- when the
    training set that cleared it turned out to be too short -- and the row it
    would admit is a row published after the window opened.

    **And no `--source`.** The gap is a function of which sources the features
    come from, and which sources the features come from is a function of the
    features -- declared once, in `contract.FEATURE_SOURCES`, which neither
    track may edit. Naming sources by hand was the remaining way to size a gap
    that did not cover what the model reads, and it was the way that left no
    trace: the arithmetic is right, the reported number looks right, and the
    only thing wrong is the set it ranged over.

    Reruns are visible, not blocked. `event_eval` appends a record per scoring
    and refuses to deduplicate; whether a second run was authorised is a
    question for the human reading the journal, and this command does not
    invent an answer it was not given either.
    """

    rows = load_daily_panel(args.panel)

    declaration = load_stress_thresholds(args.thresholds)
    taus = tuple(float(tau) for tau in declaration["taus_bp"])

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

    # The gap is no longer computed here. `evaluate_event_window` derives it
    # from the declared feature set, by the same call this module used to make
    # -- so the number in `model_config` and the number the run was purged at
    # cannot be two numbers. The sources are still derived here, and only for
    # the hash: `_derived_sources` and the evaluator both reach
    # `contract.sources_for_features`, which is the one mapping.
    sources = _derived_sources(args)
    fit_predict = climatology_exceedance(minimum_history=args.minimum_history)
    model_config = {
        "model": "climatology",
        "minimum_history": args.minimum_history,
        "taus_bp": list(taus),
        "features": sorted(args.feature),
        "sources": sorted(sources),
    }

    reported = []
    for window in windows:
        report = evaluate_event_window(
            rows,
            fit_predict,
            window,
            features=args.feature,
            registry=_registry(args),
            decision_time=time.fromisoformat(args.decision_time),
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
                # The declaration and what it resolved to, beside the gap they
                # produced. The journal carries them inside the hashed
                # `model_config`; a reader of stdout should not have to open the
                # journal to see which feature set this window was scored under.
                # Read off the report, as on the rolling path, so what is
                # printed is what shaped the run.
                "features": sorted(report.features),
                "sources": sorted(report.sources),
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
                        # The row the curve was conditioned on. A curve without
                        # it cannot be told from a hindsight by a reader.
                        "feature_date": feature.isoformat(),
                    }
                    for when, realized, curve, feature in zip(
                        report.scored_dates,
                        report.realized,
                        report.exceedance,
                        report.feature_dates,
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
        "--feature",
        action="append",
        required=True,
        metavar="COLUMN",
        help="a panel column the model reads, repeatable; these derive the "
        "sources, which size the purge gap",
    )
    backtest.add_argument("--decision-time", required=True, metavar="HH:MM")
    # No --purge and no --source. See _backtest.
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
        "--feature",
        action="append",
        required=True,
        metavar="COLUMN",
        help="a panel column the model reads, repeatable; these derive the "
        "sources, which size the purge gap",
    )
    holdout.add_argument("--decision-time", required=True, metavar="HH:MM")
    holdout.add_argument(
        "--window",
        action="append",
        metavar="NAME",
        help="score only this declared window, repeatable; default is all of them",
    )
    holdout.add_argument("--minimum-history", type=int, default=20)
    # No --purge and no --source. See _event_holdout.
    holdout.set_defaults(handler=_event_holdout)
