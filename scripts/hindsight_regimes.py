#!/usr/bin/env python3
"""What the hindsight regime labels contribute (#515, of #524): a reported-only comparison.

The calibrated stack (#475) and the per-regime recalibration (#471) read the regime of `metadata/evaluation_splits.json`, whose
boundaries were drawn after the fact. `metadata/hindsight_regimes.json` (committed before any variant was scored) declares two
variants of each: the regime term removed, and replaced by the as-of reserve-scarcity state.

    PYTHONPATH=src python3 scripts/calibrated_stack.py forecasts --panel PUB.csv --horizon H --regime-term MODE \\
        --output OUT/stack_MODE_hH.json OUT/regime_hH.json                 # MODE: declared, none, scarcity
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/regime_recalibration.py run --panel AUG2.csv --published PUB.csv \\
        --horizon H --groupings none,scarcity --output OUT/variants_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule RULE --output OUT/judge_RULE.json \\
        OUT/bench_h?.json OUT/regime_h?.json OUT/variants_h?.json OUT/stack_*_h?.json
    PYTHONPATH=src python3 scripts/hindsight_regimes.py report --panel PUB.csv --judge-flat OUT/judge_unweighted.json \\
        --judge-weighted OUT/judge_weighted.json --output OUT/hindsight.json --markdown OUT/hindsight.md \\
        OUT/bench_h?.json OUT/regime_h?.json OUT/variants_h?.json OUT/stack_*_h?.json

Scored days are before 2026-01-01 (`docs/decisions/lockbox.md`); nothing is written into `docs/runs/`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "hindsight_regimes.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
BASES = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")
STACKS = ("calibrated_stack_logistic", "calibrated_stack_isotonic")
STACK_SUFFIX = {"declared": "", "no regime": "+no_regime", "scarcity": "+scarcity"}
RECAL_SUFFIX = {"raw": "", "regime (declared)": "+regime_recal", "no group": "+regime_recal_none", "scarcity": "+regime_recal_scarcity"}
YEARS = ("2018", "2019", "2020", "2024", "2025")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed(path: Path) -> dict:
    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def row_names() -> list:
    names = [s + suffix for s in STACKS for suffix in STACK_SUFFIX.values()]
    names += [b + suffix for b in BASES for suffix in RECAL_SUFFIX.values()]
    return names


def _tiers(judged: dict, name: str) -> dict:
    candidate = judged["candidates"][name]
    near = candidate["tiers"]["onset_warning"]["lead_at_least_1"]
    verdict = candidate["verdict"]
    return {
        "onsets": near["onsets"],
        "onsets_flagged": near["onsets_flagged"],
        "worst_false_alarms_per_onset": near["worst_false_alarms_per_onset"],
        "worst_weighted_false_alarms_per_onset": near.get("worst_weighted_false_alarms_per_onset"),
        "tier_1": verdict["tier_1_onset_warning"],
        "tier_3": verdict["tier_3_no_crying_wolf"],
        "tier_5": verdict["tier_5_week_ahead"],
        "passes": verdict["passes"],
    }


def report_command(args) -> int:
    committed(DECLARATION)
    judge_script = _load("pressure_judge")
    sens = _load("setup_sensitivity")
    declaration = pj.load_declaration()
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    names = row_names()
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        forecasts.extend(f for f in pj.forecasts_from_horizon_document(document) if f.name in names or f.name in (declaration.climatology, declaration.persistence))
    missing = [n for n in names if not any(f.name == n for f in forecasts)]
    if missing:
        raise SystemExit(f"no forecasts for {missing}")
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    grids = {}
    for h in declaration.horizons:
        reference = next(f for f in forecasts if f.horizon == h and f.name == declaration.climatology)
        grids[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
    calendar = [r.date for r in rows]
    judged = {
        "flat": json.loads(args.judge_flat.read_text(encoding="utf-8")),
        "weighted": json.loads(args.judge_weighted.read_text(encoding="utf-8")),
    }
    result = {"declaration": "metadata/hindsight_regimes.json", "panel_sha256": panel_sha256(args.panel), "rows": {}}
    by_year = {}
    for label, applied in (("flat", False), ("weighted", True)):
        rule = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=applied))
        chosen = pj.choose_cutoffs(rule, grids, forecasts, calendar)
        by_year[label] = sens.tier_readings(rule, chosen, grids, None)
    for name in names:
        result["rows"][name] = {
            label: {**_tiers(judged[label], name), "by_year": by_year[label][name]["by_year"]} for label in ("flat", "weighted")
        }
    # the regime coefficients the declared stack fits (h = 1, +5 bp): in 2019 and over all fitted refits
    traces = {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if int(document.get("horizon", 0)) == 1 and "stack" in document and "stack_declared" in Path(path).name:
            refits = [r for r in document["stack"]["refits"]["5"] if r["mode"] == "fitted"]
            in_2019 = [r for r in refits if r["first_day"] < "2020-01-01"]
            labels = list(refits[-1]["regime_coefficients"])
            traces = {
                "fitted_refits": len(refits),
                "fitted_refits_before_2020": len(in_2019),
                "largest_absolute_coefficient_before_2020": max((abs(v) for r in in_2019 for v in r["regime_coefficients"].values()), default=None),
                "mean_over_fitted_refits": {k: sum(r["regime_coefficients"][k] for r in refits) / len(refits) for k in labels},
            }
    result["declared_stack_regime_coefficients_h1_5bp"] = traces
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _yn(value) -> str:
    return "pass" if value else "fail"


def _line(label, cell) -> str:
    year = " | ".join(
        f"{cell['flat']['by_year'][y]['onsets_flagged']} of {cell['flat']['by_year'][y]['onsets']}" if y in cell["flat"]["by_year"] else "–" for y in YEARS
    )
    flat, weighted = cell["flat"], cell["weighted"]
    return (
        f"| {label} | {flat['onsets_flagged']} of {flat['onsets']} | {flat['worst_false_alarms_per_onset']:.2f} | "
        f"{_yn(flat['tier_1'])} / {_yn(flat['tier_3'])} / {_yn(flat['tier_5'])} | {weighted['onsets_flagged']} of {weighted['onsets']} | "
        f"{weighted['worst_weighted_false_alarms_per_onset']:.2f} | {_yn(weighted['tier_1'])} / {_yn(weighted['tier_3'])} / {_yn(weighted['tier_5'])} | {year} |"
    )


HEADER = (
    "| form | flagged, flat | worst FA per onset, flat | tiers 1 / 3 / 5, flat | flagged, weighted | worst FA per onset, weighted count "
    "| tiers 1 / 3 / 5, weighted | recall by year, flat rule: " + " | ".join(YEARS) + " |\n|---|---|---|---|---|---|---|" + "---|" * len(YEARS)
)


def markdown(result: dict) -> str:
    lines = [
        "# What the hindsight regime labels contribute (#515)",
        "",
        "Onsets flagged of 26 at some horizon 1 to 5 (+5 bp), worst false alarms per onset (the weighted column is the weighted count), tiers 1, 3 and 5, and",
        "onsets flagged by calendar year of the onset under the flat rule.",
        "",
        "## Table 1. The calibrated stack, the regime term as declared, removed, and replaced by the as-of scarcity state",
        "",
        HEADER,
    ]
    for stack in STACKS:
        for label, suffix in STACK_SUFFIX.items():
            lines.append(_line(f"{stack} / {label}", result["rows"][stack + suffix]))
    lines += ["", "## Table 2. The per-regime recalibration of each passer: raw, by the declared regime, with no group, and by the as-of scarcity state", "", HEADER]
    for base in BASES:
        for label, suffix in RECAL_SUFFIX.items():
            lines.append(_line(f"{base} / {label}", result["rows"][base + suffix]))
    trace = result["declared_stack_regime_coefficients_h1_5bp"]
    if trace:
        lines += [
            "",
            f"The declared stack's regime coefficients (h = 1, +5 bp): over its {trace['fitted_refits']} fitted refits the mean is "
            + ", ".join(f"{k} {v:+.2f}" for k, v in trace["mean_over_fitted_refits"].items())
            + f"; over the {trace['fitted_refits_before_2020']} fitted refits before 2020 the largest absolute coefficient is "
            f"{trace['largest_absolute_coefficient_before_2020']:.2f}.",
        ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--judge-flat", type=Path, required=True)
    report.add_argument("--judge-weighted", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--markdown", type=Path)
    report.add_argument("inputs", nargs="+", type=Path)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
