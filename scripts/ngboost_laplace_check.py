"""The `ngboost_laplace` check (#533): a scratch measurement of the tier 1 pass that #527 found.

It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The row, the references and what
is reported are in `metadata/ngboost_laplace_check.json`, which this script refuses to read unless it is committed and
unchanged; the judge, its bar, its cut-off rule, the weighted miss rule in force and the bootstrap are unchanged.
Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/ngboost_laplace_check.py score --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --row 'OUT/q_h{h}.json' --output OUT/check.json --markdown OUT/check.md

It reuses the helpers of `scripts/judge_readings.py` (#523) for readings (a) to (e), adds the onsets warned by year,
the onsets only this row warns, the refits at which the row is constant or degenerate, and the paired comparison with
`risk_gbm`, calendar climatology and the persistence-logistic.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "ngboost_laplace_check.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RULES = ("unweighted", "weighted", "weighted/before_only")
CONSTANT_RANGE = 1e-9


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- helpers ------------------------------------------------------------------


def warned_by_year(days: Sequence[date], onset: Sequence[float], caught: Sequence[float]) -> Dict[int, List[int]]:
    """{year: [onsets, onsets warned]} over the days given; a year with no onset is absent."""

    if not (len(days) == len(onset) == len(caught)):
        raise ValueError("days, onsets and warnings must have one entry per day")
    out: Dict[int, List[int]] = {}
    for day, o, c in zip(days, onset, caught):
        if o:
            cell = out.setdefault(day.year, [0, 0])
            cell[0] += 1
            cell[1] += 1 if c else 0
    return out


def only_this_row_warns(
    days: Sequence[date], onset: Sequence[float], row_caught: Sequence[float], others: Sequence[Sequence[float]]
) -> List[date]:
    """The onset days the row warns and none of `others` warns."""

    if any(len(o) != len(days) for o in others) or not (len(days) == len(onset) == len(row_caught)):
        raise ValueError("every series needs one entry per day")
    return [
        day for k, day in enumerate(days)
        if onset[k] and row_caught[k] and not any(o[k] for o in others)
    ]


def refit_blocks(probabilities: Sequence[float], cutoffs: Sequence[float], dates: Sequence[date], step: int) -> List[dict]:
    """Each refit block of `step` scored days, and whether the row is constant or degenerate on it (#533).

    `constant`: the probability's range is at most `CONSTANT_RANGE`; `all_zero`: 0 on every day; `never_flag`: the
    cut-off in force is infinite; `always_flag`: the cut-off is at most the block's smallest probability, so every
    day flags. The cut-off of a block is the one on its first day.
    """

    if not (len(probabilities) == len(cutoffs) == len(dates)):
        raise ValueError("probabilities, cutoffs and dates must have one entry per day")
    if step < 1:
        raise ValueError("a refit block needs at least one day")
    out = []
    for start in range(0, len(dates), step):
        p = probabilities[start:start + step]
        cutoff = cutoffs[start]
        out.append({
            "first_day": dates[start].isoformat(),
            "days": len(p),
            "constant": max(p) - min(p) <= CONSTANT_RANGE,
            "all_zero": all(x == 0.0 for x in p),
            "never_flag": cutoff == float("inf"),
            "always_flag": cutoff != float("inf") and cutoff <= min(p),
            "distinct": len(set(p)),
        })
    return out


def block_summary(blocks: Sequence[dict]) -> dict:
    return {
        "refits": len(blocks),
        **{k: sum(1 for b in blocks if b[k]) for k in ("constant", "all_zero", "never_flag", "always_flag")},
        "first_days_constant": [b["first_day"] for b in blocks if b["constant"]],
    }


# -- the paired comparison ------------------------------------------------------


def _interval(cell: dict):
    iv = cell.get("interval")
    return [iv["lower"], iv["upper"]] if iv else None


def paired_brier(declaration, grid, row_p, ref_p, label_seed) -> dict:
    """Brier difference, reference minus row (positive: the row is better), pooled and by regime / day type."""

    tau = declaration.primary
    outcomes = grid.outcomes[tau]
    count = len(outcomes)
    gain = [(ref_p[i] - outcomes[i]) ** 2 - (row_p[i] - outcomes[i]) ** 2 for i in range(count)]

    def vectors(members=None):
        inside = [1.0] * count if members is None else [0.0] * count
        for k in members or ():
            inside[k] = 1.0
        return [inside, [i * g for i, g in zip(inside, gain)]]

    cells = {"pooled": vectors()}
    keys = {}
    for dimension in dict.fromkeys(declaration.groupings + ("regime",)):
        for label, members in pj._group_cells(grid, dimension).items():
            key = f"{dimension}\x00{label}"
            cells[key] = vectors(members)
            keys[key] = (dimension, label)
    stats = {"difference": pj._ratio(1, 0)}
    evidence = pj._bootstrap(declaration, cells, stats, count, seed=pj._seed(declaration.seed, "ngb-brier", *label_seed))
    out = {"pooled": _pack(evidence["pooled"], "difference")}
    for key, (dimension, label) in keys.items():
        out.setdefault(dimension, {})[label] = _pack(evidence[key], "difference")
    return out


def _pack(cell: dict, stat: str) -> dict:
    return {"days": cell["days"], "mean": cell[stat]["mean"], "interval": _interval(cell[stat])}


def paired_recall(declaration, days, onset, row_caught, ref_caught, groups, label_seed) -> dict:
    """Onset recall, row minus reference, pooled and by regime / day type of the onset day."""

    count = len(days)

    def vectors(members=None):
        inside = [1.0] * count if members is None else [1.0 if k in members else 0.0 for k in range(count)]
        return [
            [i * o for i, o in zip(inside, onset)],
            [i * o * c for i, o, c in zip(inside, onset, row_caught)],
            [i * o * c for i, o, c in zip(inside, onset, ref_caught)],
        ]

    cells = {"pooled": vectors()}
    keys = {}
    for dimension, labels in groups.items():
        for label in sorted(set(labels)):
            members = {k for k, x in enumerate(labels) if x == label}
            cells[f"{dimension}\x00{label}"] = vectors(members)
            keys[f"{dimension}\x00{label}"] = (dimension, label)
    stats = {"difference": pj._ONSET_STATS["recall_difference"]}
    evidence = pj._bootstrap(declaration, cells, stats, count, seed=pj._seed(declaration.seed, "ngb-recall", *label_seed))
    out = {"pooled": _pack(evidence["pooled"], "difference")}
    out["pooled"]["onsets"] = int(sum(cells["pooled"][0]))
    for key, (dimension, label) in keys.items():
        cell = _pack(evidence[key], "difference")
        cell["onsets"] = int(sum(cells[key][0]))
        out.setdefault(dimension, {})[label] = cell
    return out


# -- the command ----------------------------------------------------------------


def score_command(args) -> int:
    jr = _script("judge_readings")
    judge_script = _script("pressure_judge")
    document = jr.committed_declaration(DECLARATION)
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if not pj.load_weighted_miss().in_force:
        raise SystemExit("the weighted miss rule is not in force; this check reads the rule in force")
    row_name = document["row"]
    passers = document["risk_date_passers"]
    references = [base.climatology, base.persistence]
    names = [row_name, *passers, *references]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    if list(horizons) != document["scoring"]["horizons"] or base.last_day != date.fromisoformat(document["scoring"]["last_day"]):
        raise SystemExit("the judge's horizons or last day are not the declared ones")
    forecasts, panels = [], {}
    for h in horizons:
        for label, template in (("bench", args.bench), ("risk", args.risk), ("row", args.row)):
            doc = jr._load(template, h)
            if doc["panel_sha256"] != digest and label == "bench":
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            forecasts.extend(f for f in pj.forecasts_from_horizon_document(doc) if f.name in names)
    unique = {}
    for f in forecasts:
        unique.setdefault((f.name, f.horizon), f)
    forecasts = list(unique.values())
    missing = [(n, h) for n in names for h in horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == base.climatology)
            out[h] = pj.build_grid(base, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    grids = grids_of(forecasts)
    tau = base.primary
    result: Dict[str, object] = {
        "readings": {}, "training_checks": {}, "judge": {}, "judge_tables": {}, "by_year": {}, "only_row": {},
        "blocks": {}, "paired": {}, "cross_check": {},
    }
    original = pj.false_alarm_weights
    runs = [
        ("unweighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=False)), original),
        ("weighted", replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), original),
        ("weighted/before_only", replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), jr.before_only_weights),
    ]
    for key, declaration, weight_fn in runs:
        pj.false_alarm_weights = weight_fn
        try:
            chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
            by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
            for f in chosen:
                by_name[f.name][f.horizon] = f
            series = {n: jr.RowSeries(declaration, grids, by_name, n, place, weight_fn) for n in names}
            result["readings"][key] = {
                n: jr.readings_for(declaration, series[n], limited_weighted=key.startswith("weighted")) for n in names
            }
            result["training_checks"][key] = {
                n: jr.training_checks(declaration, grids, chosen, calendar, n) for n in (row_name, passers[0])
            }
            if key == "weighted/before_only":
                continue
            judged = pj.judge(
                declaration, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts()
            )
            result["judge"][key] = {
                n: {
                    "verdict": c["verdict"],
                    "onset_warning": c["tiers"]["onset_warning"],
                    "scarce_regime": c["verdict"].get("scarce_regime"),
                }
                for n, c in judged["candidates"].items() if n in names
            }
            result["judge_tables"][key] = judge_script.summary_tables(
                {**judged, "candidates": {n: c for n, c in judged["candidates"].items() if n in names}}
            )
            for n in names:
                near = judged["candidates"][n]["tiers"]["onset_warning"]["lead_at_least_1"]
                mine = result["readings"][key][n]["a"]
                theirs = near["worst_weighted_false_alarms_per_onset" if key == "weighted" else "worst_false_alarms_per_onset"]
                agree = (
                    abs(near["onsets_flagged"] - mine["onsets_flagged"]) < 1e-9
                    and abs(theirs - mine["false_alarms_per_onset_limited"]) < 1e-9
                    and abs(near["recall"]["mean"] - mine["recall"]) < 1e-9
                )
                result["cross_check"].setdefault(key, {})[n] = agree
                if not agree:
                    raise SystemExit(f"reading (a) of {n} under the {key} rule does not match the judge's own row")
            if key != "weighted":
                continue
            # The year, episode, degenerate-refit and paired figures are read under the rule in force.
            first = horizons[0]
            row_series = series[row_name]
            days = row_series.days
            caught = {n: [max(series[n].flags[h][k] for h in series[n].horizons) for k in range(len(days))] for n in names}
            result["by_year"] = {n: warned_by_year(days, row_series.onset, caught[n]) for n in [row_name, *passers, *references]}
            only = only_this_row_warns(days, row_series.onset, caught[row_name], [caught[n] for n in passers])
            reverse = only_this_row_warns(days, row_series.onset, _any_of([caught[n] for n in passers]), [caught[row_name]])
            result["only_row"] = {
                "row_only": [
                    {"day": d.isoformat(), "horizons": [h for h in row_series.horizons if row_series.flags[h][days.index(d)]]}
                    for d in only
                ],
                "passers_only": [d.isoformat() for d in reverse],
                "onsets": int(sum(row_series.onset)),
                "row_warns": int(sum(1 for o, c in zip(row_series.onset, caught[row_name]) if o and c)),
                "at_least_one_passer_warns": int(sum(1 for o, c in zip(row_series.onset, _any_of([caught[n] for n in passers])) if o and c)),
                "each_passer_warns": {n: int(sum(1 for o, c in zip(row_series.onset, caught[n]) if o and c)) for n in passers},
            }
            for h in horizons:
                f = by_name[row_name][h]
                blocks = refit_blocks(f.probabilities[tau], f.cutoffs[tau], f.dates, declaration.cutoff_refit_every)
                result["blocks"][str(h)] = {
                    **block_summary(blocks),
                    "days_probability_zero": sum(1 for p in f.probabilities[tau] if p == 0.0),
                    "days": len(f.dates),
                    "distinct_probabilities": len(set(f.probabilities[tau])),
                    "blocks": blocks,
                }
            at_first = {d: k for k, d in enumerate(grids[first].dates)}
            groups = {
                dim: [grids[first].groups[dim][at_first[d]] for d in days]
                for dim in dict.fromkeys(declaration.groupings + ("regime",))
            }
            for ref in document["pair_against"]:
                result["paired"][ref] = {"brier": {}, "recall": {}}
                for h in horizons:
                    grid = grids[h]
                    row_p, ref_p = (by_name[n][h].probabilities[tau] for n in (row_name, ref))
                    result["paired"][ref]["brier"][str(h)] = paired_brier(declaration, grid, row_p, ref_p, (ref, h))
                result["paired"][ref]["recall"] = paired_recall(
                    declaration, days, row_series.onset, caught[row_name], caught[ref], groups, (ref,)
                )
        finally:
            pj.false_alarm_weights = original
    result["declaration"] = {"path": "metadata/ngboost_laplace_check.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _any_of(series: Sequence[Sequence[float]]) -> List[float]:
    return [max(values) for values in zip(*series)]


# -- the summary ----------------------------------------------------------------


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _iv(cell):
    return f"{_f(cell['mean'])} [{_f(cell['interval'][0])}, {_f(cell['interval'][1])}]" if cell.get("interval") else f"{_f(cell['mean'])} [–]"


def markdown(result: dict, document: dict) -> str:
    row = document["row"]
    passers = document["risk_date_passers"]
    names = [row, *passers, "calendar_climatology", "persistence_logistic"]
    lines = ["# The ngboost_laplace check (#533)", ""]
    for key, rows in result["readings"].items():
        lines += [f"## Tier 1 under {key}", "", "| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |", "|---|---|---|---|---|"]
        for n in names:
            r = rows[n]

            def short(c):
                if "unavailable" in c:
                    return "–"
                return f"{c['onsets_flagged']:g} / {c['false_alarms_per_onset_limited']:.2f} {'pass' if c['passes'] else 'fail'}"

            best = r["b1_best"]
            lines.append(
                f"| {n} | {short(r['a'])} | {'pass (h = ' + str(best['horizon']) + ')' if best['passes'] else 'fail'} "
                f"| {short(r['b2'])} | {short(r['e']['outside_2018_19'])} |"
            )
        lines.append("")
    for key, table in result["judge_tables"].items():
        lines += [f"## The judge's tables under the {key} rule", "", table, ""]
    lines += ["## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule", "",
              "| row | " + " | ".join(str(y) for y in sorted(result["by_year"][row], key=int)) + " |",
              "|---|" + "---|" * len(result["by_year"][row])]
    years = sorted(result["by_year"][row], key=int)
    for n, cells in result["by_year"].items():
        lines.append(f"| {n} | " + " | ".join(f"{cells.get(y, [0, 0])[1]} of {cells.get(y, [0, 0])[0]}" for y in years) + " |")
    lines.append("")
    only = result["only_row"]
    lines += [
        "## Onsets only this row warns", "",
        f"{row} warns {only['row_warns']} of {only['onsets']} onsets; at least one of the five passers warns {only['at_least_one_passer_warns']}. "
        f"{len(only['row_only'])} are warned by {row} and by none of the five passers:", "",
    ]
    lines += [f"* {e['day']} (flagged at h = {', '.join(str(h) for h in e['horizons'])})" for e in only["row_only"]]
    lines += ["", f"Warned by a passer and not by {row}: " + (", ".join(only["passers_only"]) or "none"), ""]
    lines += ["## Constant or degenerate refits", "",
              "| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |",
              "|---|---|---|---|---|---|---|---|"]
    for h, b in result["blocks"].items():
        lines.append(
            f"| {h} | {b['refits']} | {b['constant']} | {b['all_zero']} | {b['never_flag']} | {b['always_flag']} "
            f"| {b['days_probability_zero']} of {b['days']} | {b['distinct_probabilities']} |"
        )
    lines.append("")
    for ref, doc in result["paired"].items():
        lines += [f"## {row} against {ref}", "", "Brier difference, reference minus row (positive: the row is better), 90% interval.", "",
                  "| h | pooled |", "|---|---|"]
        for h, cells in doc["brier"].items():
            lines.append(f"| {h} | {_iv(cells['pooled'])} |")
        lines.append("")
        for dimension in ("regime", "day_type", "scarcity_state"):
            labels = sorted(doc["brier"]["1"].get(dimension, {}))
            if not labels:
                continue
            lines += [f"By {dimension}, Brier difference at h = 1 / 3 / 5:", "", "| " + dimension + " | days | h = 1 | h = 3 | h = 5 |", "|---|---|---|---|---|"]
            for label in labels:
                cells = [doc["brier"][h][dimension][label] for h in ("1", "3", "5")]
                lines.append(f"| {label} | {cells[0]['days']:g} | " + " | ".join(_iv(c) for c in cells) + " |")
            lines.append("")
        rec = doc["recall"]
        lines += [f"Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: {_iv(rec['pooled'])} on {rec['pooled']['onsets']} onsets.", ""]
        for dimension in ("regime", "day_type", "scarcity_state"):
            if dimension not in rec:
                continue
            lines += [f"| {dimension} | onsets | recall difference [90%] |", "|---|---|---|"]
            lines += [f"| {label} | {c['onsets']} | {_iv(c)} |" for label, c in sorted(rec[dimension].items())]
            lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="check the row under the declared readings")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--bench", required=True)
    score.add_argument("--risk", required=True)
    score.add_argument("--row", required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(func=score_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
