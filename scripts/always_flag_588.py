"""Tier 1 with and without the always-flag reading (#588, on Eleonora's ruling on #570): a scratch measurement.

It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The rows, the rules and what is
reported are in `metadata/always_flag_588.json`, which this script refuses to read unless it is committed and unchanged;
the judge in force, its bar, its cut-off rule, the weighted miss rule and the bootstrap are unchanged. The reading is
`Declaration.always_flag_not_warning`, off in the declaration in force. Scored days are 2018-06-29 to 2025-12-31; no day of
the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model risk_gbm --panel AUG2.csv \\
        --published PUBLISHED.csv --horizon H --output OUT/both_hH.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H \\
        --parent OUT/both_hH.json --output OUT/iorb_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json \\
        --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/always_flag_588.py score --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --both 'OUT/both_h{h}.json' --iorb 'OUT/iorb_h{h}.json' --q 'OUT/q_h{h}.json' \\
        --output OUT/always_flag.json --markdown OUT/always_flag.md

For each rule (the weighted rule in force, and the flat count) the cut-offs are chosen once and tier 1 is read at lead of
at least 1 to 5, with the option off and on. Off at lead of at least 1 is checked against `judge`'s own row.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "always_flag_588.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RULES = ("weighted", "unweighted")


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", relative],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def slim(cell: dict) -> dict:
    """The figures of one tier 1 cell that the summary reads."""

    if "unavailable" in cell:
        return {"unavailable": cell["unavailable"]}
    recall = cell["recall"]
    interval = recall.get("interval")
    out = {
        "onsets": cell["onsets"],
        "onsets_flagged": cell["onsets_flagged"],
        "recall": recall["mean"],
        "recall_interval": [interval["lower"], interval["upper"]] if interval else None,
        "climatology_recall": cell["climatology_recall"],
        "worst_false_alarms_per_onset": cell["worst_false_alarms_per_onset"],
        "worst_weighted_false_alarms_per_onset": cell.get("worst_weighted_false_alarms_per_onset"),
        "pooled_false_alarms_per_onset": cell.get("pooled_false_alarms_per_onset"),
        "pooled_weighted_false_alarms_per_onset": cell.get("pooled_weighted_false_alarms_per_onset"),
        "complete": cell["complete"],
    }
    if "criteria" in cell:
        out["criteria"] = cell["criteria"]
        out["passes"] = cell["passes"]
    if "always_flag" in cell:
        out["always_flag"] = cell["always_flag"]
    return out


def _load(template: str, h: int) -> dict:
    return json.loads(Path(template.format(h=h)).read_text())


def score_command(args) -> int:
    document = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if base.always_flag_not_warning:
        raise SystemExit("the declaration in force has the always-flag reading on; this measurement needs it off")
    names = sum((document["rows"][k] for k in ("frozen_candidates", "parent", "benchmarks")), [])
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    if list(horizons) != document["scoring"]["horizons"]:
        raise SystemExit("the judge's horizons are not the declared ones")
    sources = [("bench", args.bench), ("risk", args.risk), ("both", args.both), ("iorb", args.iorb), ("q", args.q)]
    unique, panels = {}, {}
    for h in horizons:
        for label, template in sources:
            doc = _load(template, h)
            if label == "bench" and doc["panel_sha256"] != digest:
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            for f in pj.forecasts_from_horizon_document(doc):
                if f.name in names:
                    unique.setdefault((f.name, f.horizon), f)
    missing = [(n, h) for n in names for h in horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    forecasts = list(unique.values())
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == base.climatology)
            out[h] = pj.build_grid(base, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    grids = grids_of(forecasts)
    leads = document["scoring"]["leads"]
    result: Dict[str, object] = {"tier_1": {}, "cross_check": {}}
    for rule in RULES:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
        chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
        by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
        for f in chosen:
            by_name[f.name][f.horizon] = f
        result["tier_1"][rule] = {}
        for option in ("off", "on"):
            run = replace(declaration, always_flag_not_warning=(option == "on"))
            judged = pj.judge(run, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts())
            cells = {}
            for name in names:
                scored = [h for h in horizons if h in by_name[name]]
                cells[name] = {
                    f"lead_at_least_{lead}": slim(pj._onset_tier(run, name, lead, scored, grids, by_name, calendar))
                    for lead in leads
                }
                mine = cells[name]["lead_at_least_1"]
                theirs = judged["candidates"][name]["tiers"]["onset_warning"]["lead_at_least_1"]
                agree = (
                    abs(theirs["onsets_flagged"] - mine["onsets_flagged"]) < 1e-9
                    and abs(theirs["recall"]["mean"] - mine["recall"]) < 1e-9
                    and theirs.get("passes") == mine.get("passes")
                )
                result["cross_check"].setdefault(f"{rule}/{option}", {})[name] = agree
                if not agree:
                    raise SystemExit(f"tier 1 of {name} under the {rule} rule, option {option}, does not match the judge's own row")
            result["tier_1"][rule][option] = cells
    result["declaration"] = {"path": "metadata/always_flag_588.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- the summary --------------------------------------------------------------


def _f(value, places=2):
    return "–" if value is None else f"{value:.{places}f}"


def _v(cell):
    return "pass" if cell.get("passes") else "fail"


def _fig(cell):
    if "unavailable" in cell:
        return "–"
    low, high = cell["recall_interval"] or (None, None)
    return f"{cell['onsets_flagged']:g} of {cell['onsets']}, {_f(cell['recall'], 3)} [{_f(low, 3)}, {_f(high, 3)}]"


def markdown(result: dict, document: dict) -> str:
    names = sum((document["rows"][k] for k in ("frozen_candidates", "parent", "benchmarks")), [])
    lines = ["# Tier 1 with and without the always-flag reading (#588)", ""]
    titles = {"weighted": "Weighted rule in force", "unweighted": "Flat count"}
    for rule, by_option in result["tier_1"].items():
        off, on = by_option["off"], by_option["on"]
        limit = "pooled_weighted_false_alarms_per_onset" if rule == "weighted" else "pooled_false_alarms_per_onset"
        lines += [f"## {titles[rule]}", "", "### Tier 1, leads 1 to 5 (pooled)", "",
                  "| row | option | onsets warned, recall [90%] | pooled false alarms per onset (limit 2) | criteria met | tier 1 |",
                  "|---|---|---|---|---|---|"]
        for n in names:
            for label, cells in (("off", off), ("on", on)):
                c = cells[n]["lead_at_least_1"]
                met = "–" if "criteria" not in c else " ".join("y" if v else "n" for v in c["criteria"].values())
                lines.append(f"| {n} | {label} | {_fig(c)} | {_f(c.get(limit))} | {met} | {_v(c)} |")
        lines += ["", "### Onsets warned at lead of at least 1 to 5, off → on", "",
                  "| row | " + " | ".join(f"≥ {k}" for k in range(1, 6)) + " |", "|---|---|---|---|---|---|"]
        for n in names:
            cells = []
            for k in range(1, 6):
                key = f"lead_at_least_{k}"
                a, b = off[n][key], on[n][key]
                cells.append("–" if "unavailable" in a else f"{a['onsets_flagged']:g} → {b['onsets_flagged']:g}")
            lines.append(f"| {n} | " + " | ".join(cells) + " |")
        lines += ["", "### Always-flag blocks per row and horizon (leads 1 to 5 reading), and what they carried", "",
                  "| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | flags dropped (h = 1 … 5) | onsets lost |", "|---|---|---|---|---|---|---|---|"]
        for n in names:
            af = on[n]["lead_at_least_1"].get("always_flag")
            if not af:
                lines.append(f"| {n} | – | – | – | – | – | – | – |")
                continue
            counts = [str(af["blocks_by_horizon"][str(h)]["count"]) for h in range(1, 6)]
            dropped = " / ".join(str(af["flags_dropped_by_horizon"][str(h)]) for h in range(1, 6))
            lost = ", ".join(af["onsets_lost"]) or "none"
            lines.append(f"| {n} | " + " | ".join(counts) + f" | {dropped} | {len(af['onsets_lost'])}: {lost} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    for flag in ("bench", "risk", "both", "iorb", "q"):
        score.add_argument(f"--{flag}", required=True, help="path template with {h}")
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(func=score_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
