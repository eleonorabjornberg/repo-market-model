"""Before and after the own-leg scarcity state (#586): the judge's verdicts side by side, and recall by calendar year.

A scratch measurement, not a record: it writes the files it is given and nothing into `docs/runs/`. Both subcommands read
forecast files scored on the published panel and the judge in force (`metadata/pressure_judge.json`, the weighted-miss
switch applied as `--rule` says). Scored days are 2018-06-29 to 2025-12-31 (`require_unlocked`).

    # the judge's two outputs, one per read (scripts/own_leg_rescore.py own_leg|same_row pressure_judge judge ...)
    PYTHONPATH=src python3 scripts/own_leg_compare.py table --after OUT/own_leg/judge_RULE.json \\
        --before OUT/same_row/judge_RULE.json --output OUT/table_RULE.md ROW...
    # recall by calendar year at lead >= 1, under one read of the state (run through own_leg_rescore.py)
    PYTHONPATH=src python3 scripts/own_leg_rescore.py own_leg own_leg_compare years --rule RULE --panel PUBLISHED.csv \\
        --output OUT/years_own_leg_RULE.json --rows ROW... -- OUT/shared/bench_h?.json OUT/shared/ql_h?.json OUT/own_leg/*_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def _cell(tier):
    if not tier or "recall" not in tier:
        return "–"
    r = tier["recall"]
    return f"{tier['onsets_flagged']:g} of {tier['onsets']}, {r['mean']:.3f} [{r['interval']['lower']:.3f}, {r['interval']['upper']:.3f}]"


def _row(candidate):
    tiers, verdict = candidate["tiers"], candidate["verdict"]
    one, far = tiers["onset_warning"]["lead_at_least_1"], tiers["onset_warning"].get("lead_at_least_3")
    weighted = one.get("weighted_miss_applied")
    worst = one.get("worst_weighted_false_alarms_per_onset") if weighted else one.get("worst_false_alarms_per_onset")
    # the count tier 1's limit is read on (pooled over the leads, ruling of 10 October 2026, #509); the worst lead is only reported
    pooled = one.get("pooled_weighted_false_alarms_per_onset") if weighted else one.get("pooled_false_alarms_per_onset")
    scarce = verdict.get("scarce_regime", {})
    return {
        "tier1_pooled": _cell(one),
        "tier1_pooled_false_alarms": None if pooled is None else round(pooled, 2),
        "tier1_worst_false_alarms": None if worst is None else round(worst, 2),
        "tier1_leads_3_to_5": _cell(far),
        "tier1": verdict["tier_1_onset_warning"],
        "tier3": verdict["tier_3_no_crying_wolf"],
        "tier5": verdict["tier_5_week_ahead"],
        "passes": verdict["passes"],
        "scarce_regime": None if not scarce else {
            "tiers": [scarce.get("tier_1_onset_warning"), scarce.get("tier_3_no_crying_wolf"), scarce.get("tier_5_week_ahead")],
            "passes": scarce.get("passes"),
        },
    }


def table_command(args) -> int:
    after = json.loads(args.after.read_text())["candidates"]
    before = json.loads(args.before.read_text())["candidates"]
    lines = [
        "| row | read | tier 1 pooled: onsets flagged, recall [90%] | pooled false alarms per onset (the count tier 1 reads) | worst single lead (earlier counting) | tier 1 leads 3 to 5 | tier 1 | tier 3 | tier 5 | passes | scarce regime alone (1 / 3 / 5) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    out, changed = {}, []
    yes = lambda v: "–" if v is None else ("yes" if v else "no")
    for name in args.rows:
        out[name] = {}
        for label, source in (("before", before), ("after", after)):
            row = _row(source[name])
            out[name][label] = row
            scarce = row["scarce_regime"]
            s = "–" if not scarce else " / ".join(yes(v) for v in scarce["tiers"])
            lines.append(
                f"| {name} | {label} | {row['tier1_pooled']} | {row['tier1_pooled_false_alarms']} | {row['tier1_worst_false_alarms']} | {row['tier1_leads_3_to_5']} | "
                f"{yes(row['tier1'])} | {yes(row['tier3'])} | {yes(row['tier5'])} | {yes(row['passes'])} | {s} |"
            )
        b, a = out[name]["before"], out[name]["after"]
        flips = [k for k in ("tier1", "tier3", "tier5", "passes") if b[k] != a[k]]
        if flips:
            changed.append(f"{name}: {', '.join(f'{k} {yes(b[k])} -> {yes(a[k])}' for k in flips)}")
    lines += ["", "Verdicts that change: " + ("; ".join(changed) if changed else "none."), ""]
    args.output.write_text("\n".join(lines), encoding="utf-8")
    args.output.with_suffix(".json").write_text(json.dumps({"rows": out, "changed": changed}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "changed": changed}))
    return 0


def years_command(args) -> int:
    from repo_model import pressure_judge as pj
    from repo_model.baseline import panel_sha256
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    fa = _load("risk_date_false_alarm_controls")
    judge = _load("pressure_judge")
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    require_unlocked([declaration.last_day], where="own_leg_compare.years")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(fa.rds.SPLITS)
    keep = set(args.rows) | {declaration.climatology, declaration.persistence}
    seen, forecasts = set(), []
    for f in fa._load_forecasts(pj, panel_sha256(args.panel), args.inputs):
        if f.name in keep and (f.name, f.horizon) not in seen:
            seen.add((f.name, f.horizon))
            forecasts.append(f)
    states = {h: judge._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, fa._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = fa._grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = defaultdict(dict)
    for f in chosen:
        by_name[f.name][f.horizon] = f
    horizons = list(declaration.horizons)
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    onset = [float(grids[1].onset[position[1][day]]) for day in common]
    result = {}
    for name in args.rows:
        caught = [0.0] * len(common)
        for h in horizons:
            at = [position[h][day] for day in common]
            chosen_f = by_name[name][h]
            flags = pj._alarm_flags(
                declaration, name, [1 if chosen_f.probabilities[tau][k] >= chosen_f.cutoffs[tau][k] else 0 for k in at], onset
            )
            caught = [max(c, float(f)) for c, f in zip(caught, flags)]
        per_year = {}
        for day, o, c in zip(common, onset, caught):
            if o:
                cell = per_year.setdefault(str(day.year), {"onsets": 0, "flagged": 0})
                cell["onsets"] += 1
                cell["flagged"] += int(c)
        result[name] = {"onsets": int(sum(onset)), "flagged": int(sum(o * c for o, c in zip(onset, caught))), "by_year": per_year}
    args.output.write_text(json.dumps({"rule": args.rule, "read": __import__("os").environ.get("RMM_SCARCITY_READ", "own_leg"), "rows": result}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("table")
    t.add_argument("--after", type=Path, required=True)
    t.add_argument("--before", type=Path, required=True)
    t.add_argument("--output", type=Path, required=True)
    t.add_argument("rows", nargs="+")
    t.set_defaults(func=table_command)
    y = sub.add_parser("years")
    y.add_argument("--rule", choices=("weighted", "unweighted"), required=True)
    y.add_argument("--panel", type=Path, required=True)
    y.add_argument("--output", type=Path, required=True)
    y.add_argument("--rows", nargs="+", required=True)
    y.add_argument("inputs", nargs="+", type=Path)
    y.set_defaults(func=years_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
