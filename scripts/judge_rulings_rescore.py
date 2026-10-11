"""Re-score the judge's rows under the rulings of 10 October 2026 (#536): a scratch measurement.

It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The rows and what is reported are in
`metadata/judge_rulings_rescore.json`, which this script refuses to read unless it is committed and unchanged; the judge
is `src/repo_model/pressure_judge.py` as amended by `docs/decisions/judge-rulings-10-october.md` (a draft for Eleonora).
Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/judge_rulings_rescore.py score --panel PUBLISHED.csv --rule weighted --output OUT/weighted.json OUT/bench_h?.json ...
    PYTHONPATH=src python3 scripts/judge_rulings_rescore.py render --weighted OUT/weighted.json --unweighted OUT/unweighted.json \\
        --readings docs/pivot/evidence/judge-readings/readings.json --markdown OUT/rescore.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "judge_rulings_rescore.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
HORIZONS = ("1", "2", "3", "4", "5")


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


def declared_names(document: dict) -> List[str]:
    rows = document["rows"]
    return rows["risk_date_passers"] + rows["best_recall_rows"] + rows["gate_rows"] + rows["references"]


# -- score ----------------------------------------------------------------------


def score_command(args) -> int:
    document = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if list(base.horizons) != document["scoring"]["horizons"] or base.last_day.isoformat() != document["scoring"]["last_day"]:
        raise SystemExit("the judge's horizons or last scored day are not the declared ones")
    names = declared_names(document)
    declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    unique: Dict[tuple, "pj.Forecast"] = {}
    for path in args.inputs:
        doc = json.loads(Path(path).read_text())
        if doc["panel_sha256"] != digest and Path(path).name.startswith("bench"):
            raise SystemExit(f"{path} was scored on another panel")
        for forecast in pj.forecasts_from_horizon_document(doc):
            if forecast.name in names:
                unique.setdefault((forecast.name, forecast.horizon), forecast)
    missing = [(n, h) for n in names for h in declaration.horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    forecasts = list(unique.values())
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    result = pj.judge(declaration, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts())
    result["provenance"] = {
        "panel_sha256": digest, "declaration_commit": commit, "rule": args.rule,
        "rescore_declaration": "metadata/judge_rulings_rescore.json", "forecast_files": [str(p) for p in args.inputs],
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "rule": args.rule, "rows": sorted(result["candidates"])}))
    return 0


# -- render ---------------------------------------------------------------------


def _f(value, places=2):
    return "–" if value is None else f"{value:.{places}f}"


def _v(flag):
    return "pass" if flag else "fail"


def _stat(stat, places=3):
    if not stat:
        return "–"
    interval = stat.get("interval")
    tail = f" [{interval['lower']:.{places}f}, {interval['upper']:.{places}f}]" if interval else " (no interval)"
    return f"{stat['mean']:.{places}f}{tail}"


def near_cell(candidate: dict) -> dict:
    return candidate["tiers"]["onset_warning"]["lead_at_least_1"]


def pooled_figure(cell: dict, rule: str) -> float:
    return cell["pooled_weighted_false_alarms_per_onset" if rule == "weighted" else "pooled_false_alarms_per_onset"]


def tier3(candidate: dict, horizon: str = "1") -> dict:
    """Tier 3's calibration at one horizon: the regimes tested, those reported only, and the pressure days of each."""

    wolf = candidate["tiers"]["no_crying_wolf"][horizon]
    splits = candidate["horizons"][horizon]["5"]["splits"]["regime"]
    return {
        "tested": {label: splits[label]["events"] for label in wolf["calibrated_by_regime"]},
        "passed": {label: ok for label, ok in wolf["calibrated_by_regime"].items()},
        "reported": {label: c["events"] for label, c in wolf["calibration_reported_regimes"].items()},
    }


def cross_check(result: dict, readings: dict, rule: str) -> List[dict]:
    """Where the new rules coincide with readings (b) and (e) of #523 the figures must reproduce.

    (b2) is the pooled reading: onsets warned and false alarms per onset, flat and weighted. (b1) is each horizon
    alone. (e)'s onsets warned and recall outside 2018-19 do not depend on how false alarms are counted.
    """

    rows = []
    old = readings["readings"][rule]
    for name, candidate in result["candidates"].items():
        if name not in old:
            continue
        cell = near_cell(candidate)
        b2, b1, e = old[name]["b2"], old[name]["b1"], old[name]["e"]["outside_2018_19"]
        checks = {
            "b2 onsets warned": (cell["onsets_flagged"], b2["onsets_flagged"]),
            "b2 recall": (cell["recall"]["mean"], b2["recall"]),
            "b2 flat false alarms per onset": (cell["pooled_false_alarms_per_onset"], b2["false_alarms_per_onset_flat"]),
            "b2 weighted false alarms per onset": (cell["pooled_weighted_false_alarms_per_onset"], b2["false_alarms_per_onset_weighted"]),
            "e onsets warned outside": (cell["early_years"]["outside"]["onsets_flagged"], e["onsets_flagged"]),
            "e recall outside": (cell["early_years"]["outside"]["recall"]["mean"], e["recall"]),
        }
        for h, lead in cell["per_lead"].items():
            checks[f"b1 h={h} onsets warned"] = (lead["onsets_flagged"], b1[h]["onsets_flagged"])
            checks[f"b1 h={h} flat false alarms per onset"] = (
                lead["false_alarms_per_onset"]["flat"]["mean"], b1[h]["false_alarms_per_onset_flat"])
            checks[f"b1 h={h} weighted false alarms per onset"] = (
                lead["false_alarms_per_onset"]["weighted"]["mean"], b1[h]["false_alarms_per_onset_weighted"])
        for what, (new, before) in checks.items():
            rows.append({"row": name, "rule": rule, "what": what, "new": new, "readings": before,
                         "agree": new is not None and before is not None and abs(new - before) < 1e-6})
    return rows


def markdown(weighted: dict, unweighted: dict, readings: dict, document: dict) -> str:
    rows = document["rows"]
    sections = [
        ("The five risk-date passers", rows["risk_date_passers"]),
        ("The six best-recall rows (#461)", rows["best_recall_rows"]),
        ("The `+gate` rows (#534)", rows["gate_rows"]),
        ("The benchmarks", rows["references"]),
    ]
    out: List[str] = []
    for rule, result, title in (
        ("weighted", weighted, "Weighted rule in force"),
        ("unweighted", unweighted, "Flat rule (for scale)"),
    ):
        out += [f"## {title}", ""]
        out += [
            "Tier 1 at lead of at least 1, pooled: a day flagged at any horizon is one false alarm. "
            f"The limit reads the {'weighted' if rule == 'weighted' else 'flat'} count. "
            "Then tier 3 (calibration tested only in regimes with at least 20 pressure days), tier 5 and the full rule.",
            "",
            "| row | onsets warned | recall [90%] | false alarms per onset, flat | weighted | tier 1 | tier 3 | tier 5 | full rule |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for heading, names in sections:
            out.append(f"| **{heading}** | | | | | | | | |")
            for n in names:
                c = result["candidates"][n]
                cell, v = near_cell(c), c["verdict"]
                weight = cell.get("pooled_weighted_false_alarms_per_onset")
                out.append(
                    f"| {n} | {cell['onsets_flagged']:g} of {cell['onsets']} | {_stat(cell['recall'])} "
                    f"| {_f(cell['pooled_false_alarms_per_onset'])} | {_f(weight)} | {_v(v['tier_1_onset_warning'])} "
                    f"| {_v(v['tier_3_no_crying_wolf'])} | {_v(v['tier_5_week_ahead'])} | {'PASS' if v['passes'] else 'fail'} |"
                )
        out += ["", "### Tier 1 at each lead alone", "",
                "Onsets warned by that horizon alone / false alarms per onset that horizon raises "
                f"({'weighted' if rule == 'weighted' else 'flat'} count) and the tier 1 verdict at that lead.", "",
                "| row | " + " | ".join(f"h = {h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
        for heading, names in sections:
            for n in names:
                cell = near_cell(result["candidates"][n])
                parts = []
                for h in cell["per_lead"]:
                    lead = cell["per_lead"][h]
                    parts.append(
                        "–" if "onsets_flagged" not in lead else
                        f"{lead['onsets_flagged']:g} / "
                        f"{_f(lead['false_alarms_per_onset']['weighted' if rule == 'weighted' else 'flat']['mean'])} {_v(lead['passes'])}"
                    )
                out.append(f"| {n} | " + " | ".join(parts) + " |")
        out += ["", "### Inside and outside 2018-19, and the recall with equal weight per regime", "",
                "Reported, not part of the pass rule. Recall with its 90% interval; false alarms per onset "
                f"({'weighted' if rule == 'weighted' else 'flat'}) with its interval where the onset count allows one.", "",
                "| row | inside: warned | recall [90%] | false alarms per onset [90%] | outside: warned | recall [90%] | false alarms per onset [90%] | equal-weight recall by regime |",
                "|---|---|---|---|---|---|---|---|"]
        kind = "weighted" if rule == "weighted" else "flat"
        for heading, names in sections:
            for n in names:
                cell = near_cell(result["candidates"][n])
                early = cell["early_years"]

                def span(c):
                    if "onsets_flagged" not in c:
                        return ["–", "–", "–"]
                    return [f"{c['onsets_flagged']:g} of {c['onsets']}", _stat(c["recall"]), _stat(c["false_alarms_per_onset"][kind], 2)]

                equal = cell["regime_equal_weight_recall"]
                by_regime = ", ".join(f"{k} {c['onsets_flagged']:g}/{c['onsets']}" for k, c in equal["regimes"].items())
                out.append(
                    f"| {n} | " + " | ".join(span(early["inside"]) + span(early["outside"]))
                    + f" | {_f(equal['recall'], 3)} ({by_regime}) |"
                )
        out += ["", "### Tier 3: the regimes tested", "",
                "Pressure days (+5 bp) in each regime at h = 1; a regime is tested when it has at least 20. "
                "\"ok\" is that the regime's calibration interval covers zero.", "",
                "| row | tested (pressure days, ok) at h = 1 | reported only (pressure days) | tier 3 at each horizon |", "|---|---|---|---|"]
        for heading, names in sections:
            for n in names:
                c = result["candidates"][n]
                t = tier3(c)
                tested = ", ".join(f"{k} ({t['tested'][k]}, {'ok' if t['passed'][k] else 'miscalibrated'})" for k in t["tested"]) or "none"
                reported = ", ".join(f"{k} ({d})" for k, d in t["reported"].items()) or "none"
                by_h = " / ".join(_v(ok) for ok in c["verdict"]["tier_3_no_crying_wolf_by_horizon"].values())
                out.append(f"| {n} | {tested} | {reported} | {by_h} |")
        out.append("")

    checks = cross_check(weighted, readings, "weighted") + cross_check(unweighted, readings, "unweighted")
    disagree = [c for c in checks if not c["agree"]]
    out += ["## Cross-check against readings (b) and (e) of #523", "",
            f"Where the new rules coincide with readings (b1) (each horizon alone), (b2) (pooled) and (e) (onsets warned and recall "
            f"outside 2018-19), the figures reproduce. {len(checks) - len(disagree)} of {len(checks)} compared figures agree to 1e-6 "
            f"over the {len({c['row'] for c in checks})} rows both pages score, under both rules.", ""]
    if disagree:
        out += ["Figures that differ:", "", "| row | rule | figure | this page | #523 page |", "|---|---|---|---|---|"]
        out += [f"| {c['row']} | {c['rule']} | {c['what']} | {c['new']} | {c['readings']} |" for c in disagree]
        out.append("")
    return "\n".join(out) + "\n"


def render_command(args) -> int:
    document = committed_declaration(DECLARATION)
    weighted = json.loads(args.weighted.read_text())
    unweighted = json.loads(args.unweighted.read_text())
    readings = json.loads(args.readings.read_text())
    text = markdown(weighted, unweighted, readings, document)
    args.markdown.write_text(text, encoding="utf-8")
    checks = cross_check(weighted, readings, "weighted") + cross_check(unweighted, readings, "unweighted")
    bad = [c for c in checks if not c["agree"]]
    print(json.dumps({"markdown": str(args.markdown), "checked": len(checks), "differ": len(bad)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="judge the declared rows under one rule")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--rule", choices=("weighted", "unweighted"), required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("inputs", nargs="+", type=Path)
    score.set_defaults(func=score_command)
    render = sub.add_parser("render", help="write the Markdown tables from the two scores")
    render.add_argument("--weighted", type=Path, required=True)
    render.add_argument("--unweighted", type=Path, required=True)
    render.add_argument("--readings", type=Path, required=True)
    render.add_argument("--markdown", type=Path, required=True)
    render.set_defaults(func=render_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
