"""Tier 1 with and without the always-flag reading, option B (#685, on Eleonora's ruling of 13 October 2026 on #666).

The #588 measurement (`scripts/always_flag_588.py`) counted a flag from an always-flag block as neither a warning nor a false
alarm. The ruling is that it is not a warning but is still a false alarm. This re-scores `ngboost_laplace` and the benchmarks under
that reading, on the same panel, the same forecasts and the same declared scoring days (2018-06-29 to 2025-12-31). It writes JSON
and Markdown to the paths it is given and nothing into `docs/runs/`; the rows are in `metadata/always_flag_685.json`, which this
script refuses to read unless it is committed and unchanged. The reading is `Declaration.always_flag_not_warning`, off in the
declaration in force. The #588 evidence is not edited.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/q_hH.json \\
        --distribution OUT/qdist_hH.json
    PYTHONPATH=src python3 scripts/always_flag_685.py score --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --q 'OUT/q_h{h}.json' --output OUT/always_flag.json --markdown OUT/always_flag.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "always_flag_685.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RULES = ("weighted", "unweighted")


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def score_command(args) -> int:
    earlier = _module("always_flag_588")
    document = earlier.committed_declaration(DECLARATION)
    judge_script = earlier._judge_script()
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
    unique, panels = {}, {}
    for h in horizons:
        for label, template in (("bench", args.bench), ("q", args.q)):
            doc = json.loads(Path(template.format(h=h)).read_text())
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
    result: Dict[str, object] = {"tier_1": {}}
    for rule in RULES:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
        chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
        by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
        for f in chosen:
            by_name[f.name][f.horizon] = f
        result["tier_1"][rule] = {}
        for option in ("off", "on"):
            run = replace(declaration, always_flag_not_warning=(option == "on"))
            cells = {
                name: {
                    f"lead_at_least_{lead}": earlier.slim(
                        pj._onset_tier(run, name, lead, [h for h in horizons if h in by_name[name]], grids, by_name, calendar)
                    )
                    for lead in leads
                }
                for name in names
            }
            result["tier_1"][rule][option] = cells
    result["declaration"] = {"path": "metadata/always_flag_685.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        text = earlier.markdown(result, document).replace(
            "# Tier 1 with and without the always-flag reading (#588)",
            "# Tier 1 with and without the always-flag reading, option B: a dropped flag is not a warning but still a false alarm (#685)",
            1,
        )
        args.markdown.write_text(text, encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--bench", required=True, help="path template with {h}")
    score.add_argument("--q", required=True, help="path template with {h}")
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(func=score_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
