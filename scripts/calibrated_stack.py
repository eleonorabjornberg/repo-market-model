"""The calibrated stack of the five tier-1 passers for the pressure-day judge (#475, a track of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The stack, its ridge, refit blocks and fallback are in `metadata/calibrated_stack.json`, and the two
candidates (`calibrated_stack_logistic`, `calibrated_stack_isotonic`) in their own files under
`metadata/pressure_judge/candidates/`; this script refuses to read the declaration unless it is committed and
unchanged (`pressure_judge.py`'s own check).

    PYTHONPATH=src python3 scripts/calibrated_stack.py forecasts --panel PUB.csv --horizon H \\
        --output OUT/stack_hH.json OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule weighted --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json OUT/stack_h?.json
    PYTHONPATH=src python3 scripts/calibrated_stack.py pair --panel PUB.csv --rule weighted --judge OUT/judge.json \\
        --output OUT/pair.json --markdown OUT/pair.md OUT/bench_h?.json OUT/risk_h?.json OUT/stack_h?.json

`forecasts` reads the five passers' walk-forward probabilities (the files `risk_date_severity.py run` writes, picked
out by name), checks they share their scored days and that none is after the declared last scored day, and writes the
two stacks' probabilities at +5 and +10 bp in the shape the judge reads. `pair` reads the same forecasts with the
judge's flag cut-offs and writes what the judge does not: each stack against the best single passer (the passer
with the most onsets warned in tier 1, then the fewest false alarms per onset), paired by the judge's stationary
bootstrap on the days, and onset recall by year.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import calibrated_stack as cstack, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _members(declaration, paths, digest, horizon, last_day):
    found, scratch = {}, {}
    for path in paths:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if document["panel_sha256"] != digest:
            scratch[str(path)] = document["panel_sha256"]
        if int(document["horizon"]) != horizon:
            raise SystemExit(f"{path} is horizon {document['horizon']}, not {horizon}")
        for forecast in pj.forecasts_from_horizon_document(document):
            if forecast.name in declaration.members:
                if forecast.name in found:
                    raise SystemExit(f"member {forecast.name!r} appears in two files")
                found[forecast.name] = forecast
    missing = [name for name in declaration.members if name not in found]
    if missing:
        raise SystemExit(f"members missing from the files given: {missing}")
    dates = {found[name].dates for name in declaration.members}
    if len(dates) != 1:
        raise SystemExit("the members do not share their scored days")
    days = next(iter(dates))
    if days[-1] > last_day:
        raise ValueError(f"member days run to {days[-1]}, after the declared last scored day {last_day}")
    for name in declaration.members:
        for tau in declaration.thresholds:
            if tau not in found[name].probabilities:
                raise SystemExit(f"member {name!r} has no probabilities at {tau:g} bp")
    return found, days, scratch


def forecasts_command(args) -> int:
    declaration = cstack.load_declaration()
    commit = _judge_script().require_committed_declaration(cstack.DEFAULT_DECLARATION)
    judge = pj.load_declaration()
    if judge.thresholds != declaration.thresholds:
        raise ValueError("the stack's thresholds are not the judge's")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    digest = panel_sha256(args.panel)
    splits = _judge_script().load_split_declaration(SPLITS)
    found, days, scratch = _members(declaration, args.files, digest, args.horizon, judge.last_day)
    by_date = {row.date: row for row in rows}
    calendar = [row.date for row in rows]
    regimes = [splits.regime(day) for day in days]
    forecasts, trace = [], {}
    results = {declaration.logistic: {}, declaration.isotonic: {}}
    for tau in declaration.thresholds:
        members = {name: found[name].probabilities[tau] for name in declaration.members}
        outcomes = [int(exceeds_bp(by_date[day].spread_bps, tau)) for day in days]
        result = cstack.calibrated_stack(
            days, calendar, members, regimes, outcomes, regime_labels=declaration.regime_labels,
            horizon=args.horizon, step=declaration.step, ridge=declaration.ridge, clip=declaration.clip,
            fallback=declaration.fallback, iterations=declaration.iterations, tolerance=declaration.tolerance,
        )
        results[declaration.logistic][tau] = result.stacked
        results[declaration.isotonic][tau] = result.recalibrated
        trace[f"{tau:g}"] = list(result.trace)
    for name, probabilities in results.items():
        forecasts.append(pj.Forecast(name=name, horizon=args.horizon, dates=days, probabilities=probabilities))
    document = _judge_script()._document(args.horizon, digest, forecasts)
    document["declaration_commit"] = commit
    document["scratch_panel_files"] = scratch
    document["stack"] = {"members": list(declaration.members), "refits": trace}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "days": len(days), "output": str(args.output)}))
    return 0


def _flags(forecast, tau):
    return [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]


def _best_passer(judge_result, members):
    """The single passer with the most onsets warned in tier 1, then the fewest false alarms per onset."""

    def key(name):
        tier = judge_result["candidates"][name]["tiers"]["onset_warning"]["lead_at_least_1"]
        warned = tier["onsets_flagged"]
        applied = tier.get("worst_weighted_false_alarms_per_onset", tier["worst_false_alarms_per_onset"])
        return (-warned, applied, name)

    return sorted(members, key=key)[0]


def _interval(values, level=0.9):
    ordered = sorted(values)
    tail = (1 - level) / 2
    return ordered[int(tail * (len(ordered) - 1))], ordered[int(round((1 - tail) * (len(ordered) - 1)))]


def pair_command(args) -> int:
    script = _judge_script()
    script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    script.require_committed_declaration(cstack.DEFAULT_DECLARATION)
    stack = cstack.load_declaration()
    declaration = pj.load_declaration()
    script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    applied = {"declared": None, "weighted": True, "unweighted": False}[args.rule]
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=applied))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    digest = panel_sha256(args.panel)
    splits = script.load_split_declaration(SPLITS)
    judge_result = json.loads(args.judge.read_text(encoding="utf-8"))
    names = {declaration.climatology, declaration.persistence, *stack.members, stack.logistic, stack.isotonic}
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        forecasts.extend(f for f in pj.forecasts_from_horizon_document(document) if f.name in names)
    states = {h: script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    grids = {}
    for h in declaration.horizons:
        reference = next(f for f in forecasts if f.horizon == h and f.name == declaration.climatology)
        grids[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
    calendar = [row.date for row in rows]
    forecasts = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
    chosen = {(f.name, f.horizon): f for f in forecasts}
    best = _best_passer(judge_result, stack.members)
    tau = declaration.primary

    # Onset recall by year: an onset is warned when it is flagged at some horizon h >= 1 (tier 1's reading).
    horizons = list(declaration.horizons)
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    first = horizons[0]
    onset_days = [day for day in common if grids[first].onset[position[first][day]]]

    def warned(name):
        caught = set()
        for h in horizons:
            flags = _flags(chosen[(name, h)], tau)
            for day in onset_days:
                if flags[position[h][day]]:
                    caught.add(day)
        return caught

    rows_out = {}
    shown = [*stack.members, stack.logistic, stack.isotonic]
    caught = {name: warned(name) for name in shown}
    for name in shown:
        by_year = {}
        for year in sorted({d.year for d in onset_days}):
            total = [d for d in onset_days if d.year == year]
            by_year[str(year)] = {"onsets": len(total), "warned": sum(1 for d in total if d in caught[name])}
        rows_out[name] = {"warned": len(caught[name]), "by_year": by_year}

    # Paired differences against the best single passer on shared stationary-bootstrap resamples, h = 1 to 5.
    rng = random.Random(declaration.seed)
    paired = {}
    for name in (stack.logistic, stack.isotonic):
        per_horizon = {}
        for h in horizons:
            grid = grids[h]
            outcomes = grid.outcomes[tau]
            p_stack = chosen[(name, h)].probabilities[tau]
            p_best = chosen[(best, h)].probabilities[tau]
            gain = [(p_best[i] - outcomes[i]) ** 2 - (p_stack[i] - outcomes[i]) ** 2 for i in range(len(outcomes))]
            n = len(gain)
            draws = []
            for _ in range(declaration.replications):
                idx = stationary_bootstrap_indices(n, declaration.block_length, rng)
                draws.append(sum(gain[i] for i in idx) / n)
            lo, hi = _interval(draws, declaration.level)
            per_horizon[str(h)] = {
                "brier_gain_over_best_passer": sum(gain) / n, "interval": [lo, hi],
                "positive_means": "the stack's Brier score is lower than the best single passer's",
            }
        onsets = len(onset_days)
        per_horizon["onsets_warned_minus_best"] = len(caught[name]) - len(caught[best])
        per_horizon["onsets"] = onsets
        paired[name] = per_horizon
    result = {
        "panel_sha256": digest, "rule": args.rule, "best_single_passer": best, "primary_threshold_bp": tau,
        "onsets": len(onset_days), "per_row": rows_out, "paired_vs_best_single_passer": paired,
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        years = sorted({y for r in rows_out.values() for y in r["by_year"]})
        lines = [f"Best single passer ({args.rule} rule): `{best}`. Onsets {len(onset_days)} (warned at some h >= 1).", "",
                 "| row | warned | " + " | ".join(f"{y} (of {rows_out[best]['by_year'][y]['onsets']})" for y in years) + " |",
                 "|---|---|" + "---|" * len(years)]
        for name in shown:
            r = rows_out[name]
            lines.append(f"| {name} | {r['warned']} | " + " | ".join(str(r["by_year"][y]["warned"]) for y in years) + " |")
        lines += ["", f"Brier gain over `{best}` at +5 bp (mean per day, 90% stationary-bootstrap interval; positive: the stack is better).", "",
                  "| candidate | " + " | ".join(f"h={h}" for h in horizons) + " | onsets warned minus best |", "|---|" + "---|" * (len(horizons) + 1)]
        for name, cells in paired.items():
            lines.append(f"| {name} | " + " | ".join(
                f"{cells[str(h)]['brier_gain_over_best_passer']:+.4f} [{cells[str(h)]['interval'][0]:+.4f}, {cells[str(h)]['interval'][1]:+.4f}]"
                for h in horizons) + f" | {cells['onsets_warned_minus_best']:+d} |")
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"best": best, "output": str(args.output)}))
    return 0


def _cell(cell):
    interval = cell.get("interval")
    if interval is None:
        return "n/a"
    return f"{cell['mean']:+.4f} [{interval['lower']:+.4f}, {interval['upper']:+.4f}]"


def table_command(args) -> int:
    """Tables of the judge's result for the stacks, their five members and the benchmarks."""

    result = json.loads(args.judge.read_text(encoding="utf-8"))
    stack = cstack.load_declaration()
    declaration = pj.load_declaration()
    names = [stack.logistic, stack.isotonic, *stack.members, declaration.climatology, declaration.persistence]
    candidates = result["candidates"]
    horizons = [str(h) for h in declaration.horizons]
    primary = f"{declaration.primary:g}"
    lines = [
        "Table 1. Tiers 1, 3 and 5 at +5 bp. Tier 1: onsets warned at lead of at least 1 (of the onsets), worst false "
        "alarms per onset over h = 1 to 5 (flat / weighted). Tier 3: horizons that pass, and the regimes whose "
        "calibration fails (a regime with a pressure day, h = 1 to 5 together). Tier 5: the week-ahead probability "
        "beats climatology's Brier and is calibrated.",
        "",
        "| row | tier 1 | warned | FA/onset worst (flat / weighted) | tier 3 horizons passing | regimes not calibrated (h = 1 / h = 5) | tier 5 | pass rule |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        c = candidates[name]
        t = c["tiers"]["onset_warning"]["lead_at_least_1"]
        v = c["verdict"]
        wolf = v["tier_3_no_crying_wolf_by_horizon"]
        bad = {}
        for h in ("1", "5"):
            cal = c["horizons"][h][primary]["no_crying_wolf"]["calibrated_by_regime"]
            bad[h] = ", ".join(r for r, ok in cal.items() if not ok) or "none"
        weighted = t.get("worst_weighted_false_alarms_per_onset")
        fa = f"{t['worst_false_alarms_per_onset']:.2f}" + ("" if weighted is None else f" / {weighted:.2f}")
        wa = c["tiers"]["week_ahead"]
        lines.append(
            f"| {name} | {'pass' if v['tier_1_onset_warning'] else 'fail'} | {t['onsets_flagged']:g} of {t['onsets']} | {fa} "
            f"| {sum(1 for ok in wolf.values() if ok)} of {len(wolf)} | {bad['1']} / {bad['5']} "
            f"| {'pass' if v['tier_5_week_ahead'] else 'fail'} ({'beats climatology' if wa['criteria']['beats_climatology_brier'] else 'does not beat climatology'}, "
            f"{'calibrated' if wa['criteria']['calibrated'] else 'not calibrated'}) | {'pass' if v['passes'] else 'fail'} |"
        )
    lines += [
        "",
        "Table 2. Brier difference at +5 bp, pooled over the scored days (positive: the row beats the benchmark), mean "
        "[90% stationary-bootstrap interval], paired by day.",
        "",
        "| row | benchmark | " + " | ".join(f"h = {h}" for h in horizons) + " |",
        "|---|---|" + "---|" * len(horizons),
    ]
    for name in names[:-2]:
        for key, label in (("vs_calendar_climatology", "climatology"), ("vs_persistence_logistic", "persistence-logistic")):
            cells = [_cell(candidates[name]["horizons"][h][primary]["paired"][key]["brier_difference"]) for h in horizons]
            lines.append(f"| {name} | {label} | " + " | ".join(cells) + " |")
    for dimension, title in (("regime", "regime"), ("day_type", "pressure-day type")):
        lines += [
            "",
            f"Table 3 ({title}). Brier difference at +5 bp against climatology / against persistence-logistic, by "
            f"{title}, h = 1 and h = 5 (days; events).",
            "",
            "| row | h | " + " | ".join(sorted(candidates[stack.logistic]["horizons"]["1"][primary]["splits"][dimension])) + " |",
            "|---|---|" + "---|" * len(candidates[stack.logistic]["horizons"]["1"][primary]["splits"][dimension]),
        ]
        for name in names[:-2]:
            for h in ("1", "5"):
                split = candidates[name]["horizons"][h][primary]["splits"][dimension]
                row = []
                for label in sorted(candidates[stack.logistic]["horizons"]["1"][primary]["splits"][dimension]):
                    cell = split[label]
                    row.append(
                        f"{_cell(cell['brier_difference_vs_climatology'])} / {_cell(cell['brier_difference_vs_persistence'])} "
                        f"({cell['days']:g}; {cell['events']})"
                    )
                lines.append(f"| {name} | {h} | " + " | ".join(row) + " |")
    text = "\n".join(lines) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    f = commands.add_parser("forecasts")
    f.add_argument("--panel", type=Path, required=True)
    f.add_argument("--horizon", type=int, required=True)
    f.add_argument("--output", type=Path, required=True)
    f.add_argument("files", type=Path, nargs="+")
    f.set_defaults(run=forecasts_command)
    p = commands.add_parser("pair")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--judge", type=Path, required=True)
    p.add_argument("--rule", choices=("declared", "weighted", "unweighted"), default="declared")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p.add_argument("inputs", nargs="+", type=Path)
    p.set_defaults(run=pair_command)
    t = commands.add_parser("table")
    t.add_argument("judge", type=Path)
    t.add_argument("--output", type=Path, required=True)
    t.set_defaults(run=table_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
