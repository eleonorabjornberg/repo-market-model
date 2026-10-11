"""A start-up cut-off for the pressure-day judge, measured on the three frozen rows (#584, from #560).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The
judge picks each refit block's flag cut-off from the forecast's own earlier probabilities and the outcomes known at the block's
first decision instant; a block whose training window holds no onset flags nothing, which is almost every block in 2018, so no
2018 onset can be warned whatever the forecast (#560). This script re-runs the judge on the same forecasts under the judge as
declared and under the two start-up rules of `metadata/startup_cutoff_584.json` (`pressure_judge.StartupRule`), and reports what
each changes. Nothing in `metadata/pressure_judge.json` changes and no 2026 day is read (`docs/decisions/lockbox.md`;
`require_unlocked`). The declaration must be committed before this script runs.

    # PUB.csv is the published panel; the forecasts are those of the three frozen rows and the two benchmarks
    PYTHONPATH=src python3 scripts/startup_cutoff_584.py run --panel PUB.csv --output OUT/startup.json --markdown OUT/startup.md \\
        OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json OUT/q_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "startup_cutoff_584.json"

FROZEN = ("risk_gbm+every_day+gate+settle+h41+iorb", "risk_gbm+settle+h41", "ngboost_laplace")
BENCHMARKS = ("calendar_climatology", "persistence_logistic")
#: the declared judge first, then the two start-up rules, in the order of the declaration
RULES = (
    ("declared", None),
    ("a: climatology rate", pj.StartupRule("climatology_rate")),
    ("b: fixed 0.2", pj.StartupRule("fixed_probability", 0.2)),
)
WEIGHTINGS = ("weighted", "flat")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
fa = _load("risk_date_false_alarm_controls")
pj_script = _load("pressure_judge")


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None:
        return "–"
    if "interval" in cell:
        i = cell["interval"]
        return f"{cell['mean']:+.3f} [{i['lower']:+.3f}, {i['upper']:+.3f}]"
    return f"{_f(cell['mean'])} (no interval)"


def _recall(cell):
    i = cell["interval"]
    return f"{cell['mean']:.3f} [{i['lower']:.3f}, {i['upper']:.3f}]"


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="startup_cutoff_584")
    base = pj.load_declaration()
    if base.last_day != last:
        raise SystemExit("the judge's last scored day is not the declaration's")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    digest = panel_sha256(args.panel)
    keep = set(FROZEN) | set(BENCHMARKS)
    forecasts = [f for f in fa._load_forecasts(pj, digest, args.inputs) if f.name in keep]
    for name in sorted(keep):
        horizons = sorted(f.horizon for f in forecasts if f.name == name)
        if horizons != list(base.horizons):
            raise SystemExit(f"{name!r} has forecasts at horizons {horizons}, not {list(base.horizons)}")
    states = {h: pj_script._scarcity_states(h, base.last_day) for h in base.horizons}
    calendar = [row.date for row in rows]
    holdouts = pj_script._holdouts()
    seed = base.seed

    runs = {}
    for weighting in WEIGHTINGS:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(weighting == "weighted")))
        for label, startup in RULES:
            chosen = pj.choose_cutoffs(
                declaration, fa._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar, startup=startup
            )
            grids = fa._grids(pj, declaration, rows, splits, states, chosen)
            judged = pj.judge(declaration, grids, chosen, calendar=calendar, holdouts=holdouts, confirmation=False)
            runs[(weighting, label)] = (declaration, chosen, grids, judged)
            print(json.dumps({"weighting": weighting, "rule": label, "done": True}), flush=True)

    document = {"declaration": declared, "panel_sha256": digest, "rows": list(FROZEN), "benchmarks": list(BENCHMARKS), "runs": {}}
    tau = base.primary
    for (weighting, label), (declaration, chosen, grids, judged) in runs.items():
        by_name = {}
        for f in chosen:
            by_name.setdefault(f.name, {})[f.horizon] = f
        horizons = list(declaration.horizons)
        common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
        place = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
        onset = [float(grids[1].onset[place[1][day]]) for day in common]
        count = len(common)

        def flagged(name, h, day, by=by_name, p=place):
            f = by[name][h]
            k = p[h][day]
            return f.probabilities[tau][k] >= f.cutoffs[tau][k]

        _, _, ref_grids, ref_judged = runs[(weighting, "declared")]
        ref_by = {}
        for f in runs[(weighting, "declared")][1]:
            ref_by.setdefault(f.name, {})[f.horizon] = f

        def ref_flagged(name, h, day):
            f = ref_by[name][h]
            k = place[h][day]
            return f.probabilities[tau][k] >= f.cutoffs[tau][k]

        years = sorted({day.year for day in common})
        regimes = [grids[1].groups["regime"][place[1][day]] for day in common]
        kinds = [grids[1].groups["day_type"][place[1][day]] for day in common]
        cells_for = {
            "all": [1.0] * count,
            **{f"year {y}": [1.0 if day.year == y else 0.0 for day in common] for y in years},
            **{f"regime {r}": [1.0 if x == r else 0.0 for x in regimes] for r in sorted(set(regimes))},
            **{f"day type {t}": [1.0 if x == t else 0.0 for x in kinds] for t in sorted(set(kinds))},
        }
        stats = {
            "recall": pj._ratio(1, 0),
            "reference_recall": pj._ratio(2, 0),
            "recall_difference": lambda t: (t[1] - t[2]) / t[0] if t[0] else None,
        }
        entry = {"rows": {}}
        for name in sorted(keep):
            caught = [(1.0 if any(flagged(name, h, d) for h in horizons) else 0.0) * onset[i] for i, d in enumerate(common)]
            ref_caught = [
                (1.0 if any(ref_flagged(name, h, d) for h in horizons) else 0.0) * onset[i] for i, d in enumerate(common)
            ]
            cells = {
                cell: [
                    [m * o for m, o in zip(inside, onset)],
                    [m * c for m, c in zip(inside, caught)],
                    [m * c for m, c in zip(inside, ref_caught)],
                ]
                for cell, inside in cells_for.items()
            }
            versus = pj._bootstrap(declaration, cells, stats, count, seed=pj._seed(seed, "startup", name, label))
            onsets_in = {cell: int(sum(m * o for m, o in zip(inside, onset))) for cell, inside in cells_for.items()}
            caught_in = {cell: int(sum(m * c for m, c in zip(inside, caught))) for cell, inside in cells_for.items()}
            # the flags this rule adds against the declared judge, by horizon and year (the cut-off was infinite there)
            added, added_days, blocks = {}, {}, {}
            for h in horizons:
                f, r, g = by_name[name][h], ref_by[name][h], grids[h]
                outcomes, onsets = g.outcomes[tau], g.onset_at(tau, tau)
                per_year, days_added = {}, []
                for k, day in enumerate(g.dates):
                    if f.probabilities[tau][k] >= f.cutoffs[tau][k] and not r.probabilities[tau][k] >= r.cutoffs[tau][k]:
                        cell = per_year.setdefault(str(day.year), {"flags": 0, "false_alarms": 0, "onsets": 0})
                        cell["flags"] += 1
                        cell["false_alarms"] += 0 if outcomes[k] else 1
                        cell["onsets"] += 1 if onsets[k] else 0
                        days_added.append(
                            {"date": day.isoformat(), "pressure_day": bool(outcomes[k]), "onset": bool(onsets[k]),
                             "probability": f.probabilities[tau][k], "cutoff": f.cutoffs[tau][k]}
                        )
                added[str(h)] = per_year
                added_days[str(h)] = days_added
                served, start = [], 0
                while start < len(g.dates):
                    end = start
                    while end + 1 < len(g.dates) and f.cutoffs[tau][end + 1] == f.cutoffs[tau][start]:
                        end += 1
                    if math.isinf(r.cutoffs[tau][start]) and not math.isinf(f.cutoffs[tau][start]):
                        served.append([g.dates[start].isoformat(), g.dates[end].isoformat(), f.cutoffs[tau][start]])
                    start = end + 1
                blocks[str(h)] = served
            per_lead = {}
            tier_one = judged["candidates"][name]["tiers"]["onset_warning"]["lead_at_least_1"] if name in judged["candidates"] else {}
            for h in horizons:
                caught_h = [(1.0 if flagged(name, h, d) else 0.0) * onset[i] for i, d in enumerate(common)]
                cells = {
                    "all": [onset, caught_h],
                    "year 2018": [[m * o for m, o in zip(cells_for["year 2018"], onset)], [m * c for m, c in zip(cells_for["year 2018"], caught_h)]],
                }
                lead_stats = {"recall": pj._ratio(1, 0)}
                interval = pj._bootstrap(declaration, cells, lead_stats, count, seed=pj._seed(seed, "lead", name, label, h))
                g, f = grids[h], by_name[name][h]
                raised = [k for k in range(len(g.dates)) if f.probabilities[tau][k] >= f.cutoffs[tau][k]]
                per_lead[str(h)] = {
                    "onsets": int(sum(onset)),
                    "onsets_flagged": int(sum(caught_h)),
                    "recall": interval["all"]["recall"],
                    "onsets_2018": int(sum(cells["year 2018"][0])),
                    "onsets_flagged_2018": int(sum(cells["year 2018"][1])),
                    "flags": len(raised),
                    "false_alarms_per_onset": tier_one.get("false_alarms_by_horizon", {}).get(str(h), {}).get("per_onset"),
                    "weighted_false_alarms_per_onset": tier_one.get("weighted_false_alarms_by_horizon", {}).get(str(h), {}).get("per_onset"),
                    "days_never_flag": sum(1 for c in f.cutoffs[tau] if math.isinf(c)),
                }
            # the row against each benchmark under the same rule: onsets flagged at some lead
            against = {}
            for bench in BENCHMARKS:
                bench_caught = [(1.0 if any(flagged(bench, h, d) for h in horizons) else 0.0) * onset[i] for i, d in enumerate(common)]
                pair_cells = {
                    cell: [
                        [m * o for m, o in zip(inside, onset)],
                        [m * c for m, c in zip(inside, caught)],
                        [m * c for m, c in zip(inside, bench_caught)],
                    ]
                    for cell, inside in cells_for.items()
                }
                result = pj._bootstrap(declaration, pair_cells, stats, count, seed=pj._seed(seed, "bench", name, bench, label))
                against[bench] = {cell: result[cell]["recall_difference"] for cell in ("all", "year 2018")}
            entry["rows"][name] = {
                "judge": judged["candidates"][name],
                "per_lead": per_lead,
                "onsets_in_cell": onsets_in,
                "caught_at_some_lead": caught_in,
                "recall_versus_declared": versus,
                "recall_versus_benchmarks": against,
                "flags_added_against_declared": added,
                "flag_days_added_against_declared": added_days,
                "blocks_served": blocks,
            }
        document["runs"][f"{weighting} | {label}"] = entry

    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _tier(entry):
    judge = entry["judge"]
    tier = judge["tiers"]["onset_warning"]["lead_at_least_1"]
    late = judge["tiers"]["onset_warning"].get("lead_at_least_3", {})
    return judge, tier, late


def markdown(document: dict) -> str:
    out = []
    labels = [label for _w, label in ((w, l) for w in WEIGHTINGS for l, _ in RULES)]
    for weighting in WEIGHTINGS:
        out.append(f"\n### Tier 1, 3 and 5, {weighting} rule\n")
        out.append(
            "| row | start-up rule | onsets flagged at leads 1 to 5, recall [90%], worst false alarms per onset (limit 2) | tier 1 | "
            "leads 3 to 5: flagged, recall [90%] | tier 3 | tier 5 | passes |"
        )
        out.append("|---|---|---|---|---|---|---|---|")
        for name in document["rows"] + document["benchmarks"]:
            for label, _ in RULES:
                judge, tier, late = _tier(document["runs"][f"{weighting} | {label}"]["rows"][name])
                if "recall" not in tier:
                    out.append(f"| {name} | {label} | not judged | | | | | |")
                    continue
                worst = tier.get("worst_weighted_false_alarms_per_onset", tier["worst_false_alarms_per_onset"]) if weighting == "weighted" else tier["worst_false_alarms_per_onset"]
                verdict = judge["verdict"]
                yes = lambda x: "yes" if x else "no"
                lcell = f"{late['onsets_flagged']:g} of {late['onsets']}, {_recall(late['recall'])}" if "recall" in late else "–"
                out.append(
                    f"| {name} | {label} | {tier['onsets_flagged']:g} of {tier['onsets']}, {_recall(tier['recall'])}, {_f(worst, 2)} | "
                    f"{yes(verdict['tier_1_onset_warning'])} | {lcell} | {yes(verdict['tier_3_no_crying_wolf'])} | "
                    f"{yes(verdict['tier_5_week_ahead'])} | {yes(verdict['passes'])} |"
                )
        key = "weighted_false_alarms_per_onset" if weighting == "weighted" else "false_alarms_per_onset"
        out.append(f"\n### Tier 1 per lead, +5 bp, {weighting} rule: onsets flagged of the 26 and recall [90%]; 2018 onsets flagged of 4; {weighting} false alarms per onset (limit 2)\n")
        out.append("| row | start-up rule | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
        out.append("|---|---|" + "---|" * 5)
        for name in document["rows"]:
            for label, _ in RULES:
                lead = document["runs"][f"{weighting} | {label}"]["rows"][name]["per_lead"]
                out.append(
                    f"| {name} | {label} | "
                    + " | ".join(
                        f"{lead[str(h)]['onsets_flagged']}/{lead[str(h)]['onsets']} {_recall(lead[str(h)]['recall'])}; 2018 {lead[str(h)]['onsets_flagged_2018']}/{lead[str(h)]['onsets_2018']}; {_f(lead[str(h)][key], 2)}"
                        for h in (1, 2, 3, 4, 5)
                    )
                    + " |"
                )
        out.append(f"\n### The rows against the benchmarks under the same start-up rule, {weighting} rule: onsets flagged at some lead, difference in recall (90% interval); all and 2018\n")
        out.append("| row | start-up rule | vs calendar_climatology: all | 2018 | vs persistence_logistic: all | 2018 |")
        out.append("|---|---|---|---|---|---|")
        for name in document["rows"]:
            for label, _ in RULES:
                a = document["runs"][f"{weighting} | {label}"]["rows"][name]["recall_versus_benchmarks"]
                out.append(
                    f"| {name} | {label} | " + " | ".join(_interval(a[b][c]) for b in BENCHMARKS for c in ("all", "year 2018")) + " |"
                )
        out.append(f"\n### Onsets flagged at some lead, by year (of the onsets of the year), {weighting} rule; difference from the declared judge with its 90% interval\n")
        years = [c for c in next(iter(document["runs"].values()))["rows"][FROZEN[0]]["onsets_in_cell"] if c.startswith("year ")]
        out.append("| row | start-up rule | all | " + " | ".join(years) + " |")
        out.append("|---|---|---|" + "---|" * len(years))
        for name in document["rows"] + document["benchmarks"]:
            for label, _ in RULES:
                row = document["runs"][f"{weighting} | {label}"]["rows"][name]
                cells = ["all"] + years
                text = []
                for cell in cells:
                    n = row["onsets_in_cell"][cell]
                    c = row["caught_at_some_lead"][cell]
                    d = row["recall_versus_declared"][cell]["recall_difference"]
                    text.append(f"{c}/{n}" + ("" if label == "declared" else f" ({_interval(d)})"))
                out.append(f"| {name} | {label} | " + " | ".join(text) + " |")
        out.append(f"\n### Recall difference from the declared judge, by regime and day type, {weighting} rule\n")
        cells = [c for c in next(iter(document["runs"].values()))["rows"][FROZEN[0]]["onsets_in_cell"] if c.startswith(("regime", "day type"))]
        out.append("| row | start-up rule | " + " | ".join(f"{c} ({next(iter(document['runs'].values()))['rows'][FROZEN[0]]['onsets_in_cell'][c]})" for c in cells) + " |")
        out.append("|---|---|" + "---|" * len(cells))
        for name in document["rows"] + document["benchmarks"]:
            for label, _ in RULES[1:]:
                row = document["runs"][f"{weighting} | {label}"]["rows"][name]
                out.append(f"| {name} | {label} | " + " | ".join(_interval(row["recall_versus_declared"][c]["recall_difference"]) for c in cells) + " |")
        out.append(f"\n### Flags the start-up rule adds against the declared judge, by year, {weighting} rule: flags (of which not pressure days; onsets), over h = 1 to 5\n")
        out.append("| row | start-up rule | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
        out.append("|---|---|" + "---|" * 5)
        for name in document["rows"] + document["benchmarks"]:
            for label, _ in RULES[1:]:
                added = document["runs"][f"{weighting} | {label}"]["rows"][name]["flags_added_against_declared"]
                cells_h = []
                for h in (1, 2, 3, 4, 5):
                    per_year = added[str(h)]
                    cells_h.append(
                        "; ".join(f"{y}: {v['flags']} ({v['false_alarms']}; {v['onsets']})" for y, v in sorted(per_year.items())) or "none"
                    )
                out.append(f"| {name} | {label} | " + " | ".join(cells_h) + " |")
    out.append("\n### Blocks whose cut-off came from the start-up rule (+5 bp, weighted run): first day, last day, cut-off\n")
    for name in document["rows"] + document["benchmarks"]:
        for label, _ in RULES[1:]:
            served = document["runs"][f"weighted | {label}"]["rows"][name]["blocks_served"]
            out.append(f"* `{name}`, {label}: " + "; ".join(f"h = {h}: {len(v)} blocks" + (f" ({v[0][0]} to {v[-1][1]}; first cut-off {v[0][2]:.4g})" if v else "") for h, v in sorted(served.items())))
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--markdown", type=Path)
    run.add_argument("inputs", nargs="+", type=Path)
    run.set_defaults(func=run_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
