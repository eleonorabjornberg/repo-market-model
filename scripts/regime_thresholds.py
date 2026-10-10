"""Regime-specific warning thresholds: a separate cut-off when the as-of scarcity state is at least 2 (#461, a track of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The six rows, the state threshold and what is reported are in `metadata/regime_thresholds.json`, and
each variant row is a candidate file of its own (`metadata/pressure_judge/candidates/<row>+scarce_cutoff.json`);
this script refuses to read the declaration or the judge's declaration unless they are committed and unchanged.
The bar, the cut-off rule and the bootstrap are the judge's (`metadata/pressure_judge.json`), unchanged. Scored
days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/bench_hH.json
    ... each row's own forecast script, h = 1 to 5, as `docs/pivot/regime-thresholds-result.md` lists ...
    PYTHONPATH=src python3 scripts/regime_thresholds.py score --panel PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --row two_part_gbm='OUT/tp_h{h}.json' ... \\
        --output OUT/regime.json --markdown OUT/regime.md

`score` gives each declared row two flag cut-offs: the judge's own (chosen refit by refit on all the training days,
`pressure_judge.choose_cutoffs`) and, on days whose as-of scarcity state is at least 2, a cut-off chosen by the same
rule and limit on the training days in that state alone (`choose_cutoffs(scarce_at_least=2)`). It judges both, the
benchmarks beside them, and adds the onset recall by calendar year and the scarce cut-off's own diagnostics.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "regime_thresholds.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RESULT = REPO / "docs" / "pivot" / "judge-amendment-result.md"
CALLED_OUT = (2018, 2020, 2024)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


judge_script = _load("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
diagnostics = _load("onset_diagnostics_script", REPO / "scripts" / "onset_diagnostics.py")


def best_rows(count: int = 6) -> list:
    """The `count` best candidate rows of Table 1, read as #429 declared: most onsets flagged, then the smaller worst
    false alarms per onset, then name; the benchmarks and the published baseline are left out."""

    table = diagnostics.table_one()
    references = {"calendar_climatology", "persistence_logistic", "published_v1"}
    ranked = sorted(
        (name for name in table if name not in references),
        key=lambda name: (-table[name][0], table[name][2], name),
    )
    return ranked[:count]


def declared() -> dict:
    document = diagnostics.committed_declaration(DECLARATION)
    if document["rows"]["chosen"] != best_rows(len(document["rows"]["chosen"])):
        raise SystemExit("the declared rows are not the best rows of Table 1 under the declared reading")
    return document


def score_command(args) -> int:
    document = declared()
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    declaration_commit = judge_script.require_committed_declaration(DECLARATION)
    suffix = document["rows"]["variant_suffix"]
    wanted = document["rows"]["chosen"]
    templates = dict(item.split("=", 1) for item in args.row)
    if sorted(templates) != sorted(wanted):
        raise SystemExit(f"--row must name exactly the declared rows {wanted}; got {sorted(templates)}")
    at_least = int(document["scarce_cutoff"]["scarcity_state_at_least"])
    declaration = pj.load_declaration()
    # The weighted miss rule (#454), as `pressure_judge.py judge --rule` has it: forced on or off for one scratch run.
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    applied = {"declared": None, "weighted": True, "unweighted": False}[args.rule]
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=applied))
    primary = float(document["scoring"]["primary_threshold_bp"])
    horizons = declaration.horizons
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    by_horizon, panels = diagnostics.load_forecasts(args.bench, templates, horizons)
    flat = [f for h in horizons for f in by_horizon[h]]
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    grids = grids_of(flat)
    pooled = pj.choose_cutoffs(declaration, grids, flat, calendar)
    variants = pj.choose_cutoffs(
        declaration, grids, [f for f in flat if f.name in wanted], calendar, scarce_at_least=at_least
    )
    renamed = [
        pj.Forecast(
            name=f.name + suffix, horizon=f.horizon, dates=f.dates, probabilities=f.probabilities,
            cutoffs=f.cutoffs, cutoff_rule=f.cutoff_rule, cutoff_weighting=f.cutoff_weighting,
        )
        for f in variants
    ]
    everything = pooled + renamed
    candidates_wanted = set(declaration.candidates)
    everything = [f for f in everything if f.name in candidates_wanted]
    result = pj.judge(
        declaration, grids_of(everything), everything,
        calendar=calendar, holdouts=judge_script._holdouts(),
    )
    shown = {"calendar_climatology", "persistence_logistic", *wanted, *(n + suffix for n in wanted)}
    result["candidates"] = {n: c for n, c in result["candidates"].items() if n in shown}

    # Onset recall by calendar year, and the scarce cut-off's own diagnostics.
    final_grids = grids_of(everything)
    common = sorted(set.intersection(*(set(final_grids[h].dates) for h in horizons)))
    keep = set(common)
    reference_grid = final_grids[horizons[0]]
    onset_days = [d for d, o in zip(reference_grid.dates, reference_grid.onset) if o and d in keep]
    by_year = {}
    scarce_days = {}
    for name in [n for w in wanted for n in (w, w + suffix)]:
        caught = {d: 0 for d in onset_days}
        for h in horizons:
            f = next(x for x in everything if x.name == name and x.horizon == h)
            for p, c, d in zip(f.probabilities[primary], f.cutoffs[primary], f.dates):
                if p >= c and d in caught:
                    caught[d] = 1
        years = defaultdict(lambda: [0, 0])
        for d in onset_days:
            years[d.year][0] += 1
            years[d.year][1] += caught[d]
        by_year[name] = {str(y): {"onsets": v[0], "flagged": v[1]} for y, v in sorted(years.items())}
    diag = {}
    for name in wanted:
        per_h = {}
        for h in horizons:
            f = next(x for x in everything if x.name == name + suffix and x.horizon == h)
            g = final_grids[h]
            pooled_f = next(x for x in everything if x.name == name and x.horizon == h)
            blocks = range(0, len(f.dates), declaration.cutoff_refit_every)
            scarce_blocks = never = 0
            for start in blocks:
                days = [k for k in range(start, min(start + declaration.cutoff_refit_every, len(f.dates)))
                        if pj._state_at_least(g.groups["scarcity_state"][k], at_least)]
                if days:
                    scarce_blocks += 1
                    if f.cutoffs[primary][days[0]] == float("inf"):
                        never += 1
            scarce = [k for k, s in enumerate(g.groups["scarcity_state"]) if pj._state_at_least(s, at_least)]
            per_h[str(h)] = {
                "scored_days": len(f.dates),
                "scarce_days": len(scarce),
                "scarce_pressure_days": sum(g.outcomes[primary][k] for k in scarce),
                "scarce_onsets": sum(g.onset[k] for k in scarce),
                "blocks_with_a_scarce_day": scarce_blocks,
                "blocks_whose_scarce_cutoff_flags_nothing": never,
                "scarce_flags_pooled": sum(1 for k in scarce if pooled_f.probabilities[primary][k] >= pooled_f.cutoffs[primary][k]),
                "scarce_flags_scarce_cutoff": sum(1 for k in scarce if f.probabilities[primary][k] >= f.cutoffs[primary][k]),
            }
        diag[name] = per_h
    result["regime_thresholds"] = {
        "declaration": {"path": "metadata/regime_thresholds.json", "commit": declaration_commit},
        "judge_declaration_commit": judge_commit,
        "scarcity_state_at_least": at_least,
        "onsets": len(onset_days),
        "onsets_by_year": {str(y): sum(1 for d in onset_days if d.year == y) for y in sorted({d.year for d in onset_days})},
        "recall_by_year": by_year,
        "scarce_cutoff_diagnostics": diag,
        "forecast_panels": panels,
    }
    result["provenance"] = {"panel_sha256": digest, "declaration_commit": judge_commit}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "verdicts": {n: c["verdict"]["passes"] for n, c in result["candidates"].items()}}))
    return 0


def markdown(result: dict, document: dict) -> str:
    suffix = document["rows"]["variant_suffix"]
    wanted = document["rows"]["chosen"]
    info = result["regime_thresholds"]
    years = sorted(info["onsets_by_year"])
    lines = [judge_script.summary_tables(result), ""]
    lines += [
        "Table 4. Onsets flagged at lead of at least 1 (a flag on the onset day at any horizon 1 to 5), by calendar year, "
        "under the pooled cut-off and under the scarce-state cut-off (pooled / scarce); the number of onsets in the year in the header.",
        "",
        "| model | " + " | ".join(f"{y} ({info['onsets_by_year'][y]})" for y in years) + " | all (" + str(info["onsets"]) + ") |",
        "|---|" + "---|" * (len(years) + 1),
    ]
    for name in wanted:
        cells, total = [], [0, 0]
        for y in years:
            a = info["recall_by_year"][name].get(y, {"flagged": 0})["flagged"]
            b = info["recall_by_year"][name + suffix].get(y, {"flagged": 0})["flagged"]
            total[0] += a
            total[1] += b
            cells.append(f"{a} / {b}")
        lines.append(f"| {name} | " + " | ".join(cells) + f" | {total[0]} / {total[1]} |")
    lines += [
        "",
        f"Table 5. The scarce-state cut-off (as-of state at least {info['scarcity_state_at_least']}), h = 1 to 5: scored days in the state, "
        "its pressure days and onsets, refit blocks with a day in the state whose cut-off flags nothing, and the flags on those days "
        "under the pooled and the scarce-state cut-off.",
        "",
        "| model | h | scored days | scarce days | scarce pressure days | scarce onsets | blocks with a scarce day | of them, flag nothing | flags: pooled | flags: scarce cut-off |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in wanted:
        for h, d in info["scarce_cutoff_diagnostics"][name].items():
            lines.append(
                f"| {name} | {h} | {d['scored_days']} | {d['scarce_days']} | {d['scarce_pressure_days']} | {d['scarce_onsets']} | "
                f"{d['blocks_with_a_scarce_day']} | {d['blocks_whose_scarce_cutoff_flags_nothing']} | "
                f"{d['scarce_flags_pooled']} | {d['scarce_flags_scarce_cutoff']} |"
            )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="judge the declared rows under both cut-offs")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--bench", required=True, help="benchmark forecast file template, with {h}")
    score.add_argument("--row", action="append", required=True, help="NAME=template with {h}, once per declared row")
    score.add_argument(
        "--rule", choices=("declared", "weighted", "unweighted"), default="declared",
        help="how false alarms count (#454): as the switch in metadata/weighted_miss.json says (default), or forced",
    )
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(func=score_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
