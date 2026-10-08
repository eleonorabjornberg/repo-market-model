"""The time-to-pressure hazard model (#387, track Z of #374): forecasts for the judge, and the window.

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`. The model, its features,
its cut-offs and the window are in `metadata/pressure_hazard.json` (and the
candidate's entry in `metadata/pressure_judge.json`), which this script refuses
to read unless both are committed and unchanged.

    PYTHONPATH=src python3 scripts/pressure_hazard.py forecasts --panel PANEL --horizon H --output OUT/hazard_hH.json
    PYTHONPATH=src python3 scripts/pressure_hazard.py window --panel PANEL --output OUT/window.json --markdown OUT/window.md

`forecasts` writes the walk-forward per-day probabilities P(SOFR - IORB > tau) at
+5 and +10 bp for one horizon, in the shape the judge reads
(`pressure_judge.py judge ... OUT/hazard_hH.json`): the file `pressure_judge.py
forecasts` writes for the benchmarks has the same shape, so the two are passed
together. Days are before 2026-01-01 (`docs/decisions/lockbox.md`, #374).

`window` scores the desk-facing summary, P(at least one pressure day in the next
5 business days) from each decision at horizon 1, against the two window
benchmarks the declaration names: Brier and its CORP decomposition, AUROC, the
paired Brier difference with a stationary-bootstrap interval, by regime and by
reserve-scarcity state (#115), and the lead time to each +5 bp onset. A window
that would run past the declared last scored day is not scored.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_hazard as hz  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import corp_decomposition, stationary_bootstrap_interval  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
CALENDAR = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
BLOCK_LENGTH = 10
REPLICATIONS = 2000
LEVEL = 0.90
SEED = 387


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _commits(judge):
    """The commits of the two declarations, refusing one that is not committed."""

    return {
        "pressure_hazard": judge.require_committed_declaration(hz.DEFAULT_DECLARATION),
        "pressure_judge": judge.require_committed_declaration(pj.DEFAULT_DECLARATION),
    }


def _run(rows, predictor, name, features, declaration, horizon, registry):
    return rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=name,
        features=features,
        registry=registry,
        decision_time=declaration.decision_time,
        taus=declaration.thresholds,
        minimum_history=declaration.minimum_history,
        refit_every=declaration.refit_every,
        end=declaration.last_day,
        horizon=horizon,
    )


# -- forecasts ----------------------------------------------------------------


def forecasts_command(args) -> int:
    judge = _judge_script()
    declaration = hz.load_declaration()
    commits = _commits(judge)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    report = _run(
        rows,
        hz.pressure_hazard_exceedance(declaration.features, splits, minimum_history=declaration.minimum_history),
        declaration.candidate,
        declaration.features,
        declaration,
        args.horizon,
        registry,
    )
    forecast = pj.report_forecast(declaration.candidate, report)
    document = {
        "horizon": args.horizon,
        "panel_sha256": panel_sha256(args.panel),
        "declaration_commits": commits,
        "declaration_sha256": declaration.sha256,
        "scored_window": {
            "first": report.scored_dates[0].isoformat(),
            "last": report.scored_dates[-1].isoformat(),
            "days": len(report.scored_dates),
        },
        "model_settings": dict(report.model_settings),
        "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- the window ---------------------------------------------------------------


def _brier(p, y):
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(p)


def _paired(p_a, p_b, y):
    """Mean of (a - y)^2 - (b - y)^2 with its stationary-bootstrap interval."""

    diff = [(a - o) ** 2 - (b - o) ** 2 for a, b, o in zip(p_a, p_b, y)]

    def statistic(indices):
        return sum(diff[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        statistic, len(diff), block_length=BLOCK_LENGTH, seed=SEED, replications=REPLICATIONS, level=LEVEL
    )
    return {"mean": sum(diff) / len(diff), "interval": {"lower": lower, "upper": upper, "level": LEVEL}}


def _cell(p, y, climatology, persistence):
    n = len(p)
    cell = {"days": n, "events": int(sum(y)), "base_rate": sum(y) / n if n else None}
    if not n:
        return cell
    cell["brier"] = _brier(p, y)
    cell["climatology_brier"] = _brier(climatology, y)
    cell["persistence_brier"] = _brier(persistence, y)
    cell["auroc"] = pj.auroc(p, y)
    if 0 < sum(y) < n:
        d = corp_decomposition(p, y)
        cell["corp"] = {
            "reliability": d.reliability, "resolution": d.resolution, "uncertainty": d.uncertainty,
        }
    if n >= 40:
        cell["vs_climatology"] = _paired(p, climatology, y)
        cell["vs_persistence"] = _paired(p, persistence, y)
    return cell


def _onsets(rows, tau, first, last):
    """Row indices of pressure days with none among the five panel rows before them."""

    pressure = [row.spread_bps > tau for row in rows]
    return [
        r for r in range(5, len(rows))
        if pressure[r] and not any(pressure[r - 5:r]) and first <= rows[r].date <= last
    ]


def _lead_time(rows, tau, series, cutoff, first, last):
    """Per lead k = 1..5: how many +tau onsets had a window forecast >= cutoff k days before."""

    onsets = _onsets(rows, tau, first, last)
    by_lead = {}
    flagged_any = 0
    scored = 0
    for k in range(1, 6):
        count = flagged = 0
        for r in onsets:
            day = rows[r - k + 1].date  # the scored day of the decision k panel days before the onset
            if day not in series:
                continue
            count += 1
            flagged += series[day] >= cutoff
        by_lead[str(k)] = {"onsets_scored": count, "flagged": flagged,
                           "share": flagged / count if count else None}
    for r in onsets:
        days = [rows[r - k + 1].date for k in range(1, 6)]
        if all(d in series for d in days):
            scored += 1
            flagged_any += any(series[d] >= cutoff for d in days)
    return {"onsets": len(onsets), "by_lead": by_lead, "all_leads_scored": scored, "flagged_at_some_lead": flagged_any}


def window_command(args) -> int:
    judge = _judge_script()
    declaration = hz.load_declaration()
    commits = _commits(judge)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    n = declaration.window_days
    runs = {
        declaration.candidate: _run(
            rows,
            hz.pressure_hazard_exceedance(
                declaration.features, splits, minimum_history=declaration.minimum_history, window=n
            ),
            f"{declaration.candidate}_window", declaration.features, declaration, 1, registry,
        ),
        "window_climatology": _run(
            rows,
            hz.window_benchmark_exceedance("climatology", CALENDAR, splits,
                                           minimum_history=declaration.minimum_history, window=n),
            "window_climatology", CALENDAR, declaration, 1, registry,
        ),
        "window_persistence": _run(
            rows,
            hz.window_benchmark_exceedance("persistence", CALENDAR, splits,
                                           minimum_history=declaration.minimum_history, window=n),
            "window_persistence", CALENDAR, declaration, 1, registry,
        ),
    }
    reference = runs[declaration.candidate]
    index_of = {row.date: i for i, row in enumerate(rows)}
    keep = [
        k for k, day in enumerate(reference.scored_dates)
        if index_of[day] + n - 1 < len(rows) and rows[index_of[day] + n - 1].date <= declaration.last_day
    ]
    days = [reference.scored_dates[k] for k in keep]
    pj.require_scored_days(
        pj.load_declaration(), [rows[index_of[d] + n - 1].date for d in days], where="the window's last day"
    )
    for name, run in runs.items():
        if run.scored_dates != reference.scored_dates:
            raise SystemExit(f"{name} was scored on other days than the hazard window")
    scarcity = judge._scarcity_states(1, declaration.last_day)
    result = {
        "declaration_commits": commits,
        "declaration_sha256": declaration.sha256,
        "panel_sha256": panel_sha256(args.panel),
        "window_days": n,
        "scored_window": {"first": days[0].isoformat(), "last": days[-1].isoformat(), "days": len(days)},
        "ml_libraries": None if reference.ml_libraries is None else dict(reference.ml_libraries),
        "thresholds": {},
    }
    for position, tau in enumerate(declaration.thresholds):
        label = f"{tau:g}"
        y = [int(any(rows[index_of[d] + j].spread_bps > tau for j in range(n))) for d in days]
        probabilities = {
            name: [run.forecast[k][position] for k in keep] for name, run in runs.items()
        }
        p = probabilities[declaration.candidate]
        clim = probabilities["window_climatology"]
        pers = probabilities["window_persistence"]
        entry = {"pooled": _cell(p, y, clim, pers), "by_regime": {}, "by_scarcity_state": {}}
        for regime, first, last in splits.regimes:
            take = [i for i, d in enumerate(days) if first <= d <= last]
            if take:
                entry["by_regime"][regime] = _cell(
                    [p[i] for i in take], [y[i] for i in take], [clim[i] for i in take], [pers[i] for i in take]
                )
        states = sorted({scarcity.get(d) for d in days if scarcity.get(d) is not None})
        for state in states:
            take = [i for i, d in enumerate(days) if scarcity.get(d) == state]
            entry["by_scarcity_state"][str(int(state))] = _cell(
                [p[i] for i in take], [y[i] for i in take], [clim[i] for i in take], [pers[i] for i in take]
            )
        cutoff = declaration.window_cutoffs[tau]
        flags = [v >= cutoff for v in p]
        flagged = sum(flags)
        entry["cutoff"] = cutoff
        entry["flags"] = {
            "flagged": flagged,
            "share_of_days": flagged / len(p),
            "per_252_days": 252.0 * flagged / len(p),
            "precision": (sum(1 for f, o in zip(flags, y) if f and o) / flagged) if flagged else None,
            "recall": (sum(1 for f, o in zip(flags, y) if f and o) / sum(y)) if sum(y) else None,
        }
        entry["lead_time"] = {}
        for name, values in probabilities.items():
            series = dict(zip(days, values))
            benchmark_cutoff = cutoff
            entry["lead_time"][name] = _lead_time(
                rows, tau, series, benchmark_cutoff, days[0], declaration.last_day
            )
        result["thresholds"][label] = entry
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, declaration), encoding="utf-8")
    print(json.dumps({"output": str(args.output), **result["scored_window"]}))
    return 0


# -- the summary --------------------------------------------------------------


def _f(value, places=4):
    return "–" if value is None else f"{value:.{places}f}"


def _d(cell):
    if not cell:
        return "–"
    i = cell["interval"]
    return f"{cell['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"


def markdown(result, declaration) -> str:
    lines = [
        "# Time-to-pressure hazard: the 5-day window (#387)",
        "",
        f"Scored days {result['scored_window']['first']} to {result['scored_window']['last']} "
        f"({result['scored_window']['days']} decisions at horizon 1). P(at least one pressure day in the "
        f"next {result['window_days']} business days). Declaration `{declaration.path}` sha256 "
        f"`{declaration.sha256[:12]}…`.",
        "",
    ]
    for tau, entry in result["thresholds"].items():
        pooled = entry["pooled"]
        lines += [
            f"## +{tau} bp",
            "",
            f"Base rate {_f(pooled['base_rate'])}; events {pooled['events']}.",
            "",
            "| | Brier | reliability | resolution | AUROC |",
            "|---|---|---|---|---|",
            f"| hazard | {_f(pooled['brier'])} | {_f(pooled.get('corp', {}).get('reliability'))} | "
            f"{_f(pooled.get('corp', {}).get('resolution'))} | {_f(pooled['auroc'], 3)} |",
            f"| window climatology | {_f(pooled['climatology_brier'])} | | | |",
            f"| window persistence | {_f(pooled['persistence_brier'])} | | | |",
            "",
            f"ΔBrier, hazard − climatology: {_d(pooled.get('vs_climatology'))}; "
            f"hazard − persistence: {_d(pooled.get('vs_persistence'))} (negative favours the hazard; "
            f"{pooled['days'] and int(LEVEL * 100)}% stationary bootstrap).",
            "",
            "| group | days | events | hazard Brier | clim. Brier | pers. Brier | Δ vs clim. | Δ vs pers. | AUROC |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for kind in ("by_regime", "by_scarcity_state"):
            for label, cell in entry[kind].items():
                lines.append(
                    f"| {kind[3:]} {label} | {cell['days']} | {cell['events']} | {_f(cell.get('brier'))} | "
                    f"{_f(cell.get('climatology_brier'))} | {_f(cell.get('persistence_brier'))} | "
                    f"{_d(cell.get('vs_climatology'))} | {_d(cell.get('vs_persistence'))} | {_f(cell.get('auroc'), 3)} |"
                )
        flags = entry["flags"]
        lines += [
            "",
            f"Flagged at the declared cut-off {entry['cutoff']:g}: {flags['flagged']} days "
            f"({_f(flags['per_252_days'], 1)} per 252), precision {_f(flags['precision'], 3)}, "
            f"recall of windows with a pressure day {_f(flags['recall'], 3)}.",
            "",
            "Lead time to the +5 bp onsets (share of onsets whose window forecast, issued k business days "
            "before the onset, reached the cut-off):",
            "",
            "| forecast | onsets | k = 1 | k = 2 | k = 3 | k = 4 | k = 5 | some k |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for name, lead in entry["lead_time"].items():
            cells = " | ".join(
                f"{lead['by_lead'][str(k)]['flagged']}/{lead['by_lead'][str(k)]['onsets_scored']}"
                for k in range(1, 6)
            )
            lines.append(
                f"| {name} | {lead['onsets']} | {cells} | {lead['flagged_at_some_lead']}/{lead['all_leads_scored']} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.set_defaults(run=forecasts_command)
    window = commands.add_parser("window")
    window.add_argument("--panel", type=Path, required=True)
    window.add_argument("--output", type=Path, required=True)
    window.add_argument("--markdown", type=Path)
    window.set_defaults(run=window_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
