"""How many fitted-kink refits are "not identified" under the tie rule of #747: a scratch count, no forecast is scored.

H7 (the model side of the estimator). `repo_model.satiation.fit_level` used to keep a grid point only if its squared
error was lower than the best by more than an absolute 1e-12. It now treats points within `KINK_TIE_RTOL` of the best as
tied and, when the tied set spans more than one grid step, reports "not identified" and serves the fixed 0.12. This
script re-runs the walk-forward refits of the fitted-level rows of #587 (the structural, projected-reserves and
combined models) and of #626 (the kinked structural model) and counts, by calendar year of the refit's first served
anchor, the refits that are "not identified" and the refits whose level the old rule set differently. It scores nothing:
it reads each refit's training pairs and the level, and writes only the counts. Scored days stop at the declared last
day (2018-06-29 to 2025-12-31); no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/satiation_ties_747.py --panel AUG5.csv --horizon 1 --output ties_h1.json
    PYTHONPATH=src python3 scripts/satiation_ties_747.py summary --inputs 'ties_h{h}.json' --output ties.json
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from collections import Counter
from datetime import date, time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import (  # noqa: E402
    h41_release, measurement_fields, ml, projected_reserves as pr, satiation as sat, structural_liquidity as sl,
)
from repo_model.baseline import rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


k626 = _load("kinked_626")
s587 = k626.s587
SPLITS = k626.SPLITS


def old_level(ratios, spreads):
    """`fit_level` as it was before #747: a point wins only by an absolute 1e-12 of squared error."""

    n = len(ratios)
    if n < sat.KINK_MINIMUM_PAIRS:
        return sat.FIXED
    y_mean = sum(spreads) / n
    best = None
    for k in sat.KINK_GRID:
        x = [sat.hinge(r, k) for r in ratios]
        x_mean = sum(x) / n
        sxx = sum((v - x_mean) ** 2 for v in x)
        if sxx <= 0.0:
            continue
        slope = sum((v - x_mean) * (s - y_mean) for v, s in zip(x, spreads)) / sxx
        if slope < 0.0:
            continue
        intercept = y_mean - slope * x_mean
        sse = sum((s - intercept - slope * v) ** 2 for v, s in zip(x, spreads))
        if best is None or sse < best[0] - 1e-12:
            best = (sse, float(k))
    return sat.FIXED if best is None else best[1]


RTOL = sat.KINK_TIE_RTOL
# the tolerance is also tried at wider values, to show how far it can be raised before a real refit counts as tied
SENSITIVITY = (1e-9, 1e-6, 1e-4, 1e-3, 1e-2)


@contextlib.contextmanager
def recording(calls: list):
    real = sat.fit_level

    def wrapped(ratios, spreads, **kwargs):
        level, record = real(ratios, spreads, **kwargs)
        wider = {}
        for rtol in SENSITIVITY:
            sat.KINK_TIE_RTOL = rtol
            try:
                wider[f"{rtol:g}"] = not real(ratios, spreads, **kwargs)[1]["fitted"] and (
                    real(ratios, spreads, **kwargs)[1].get("tied") is not None
                )
            finally:
                sat.KINK_TIE_RTOL = RTOL
        calls.append({"not_identified_at": wider,
            "pairs": len(ratios), "level": level, "fitted": record["fitted"], "reason": record.get("reason"),
            "tied": record.get("tied"), "old_level": old_level(ratios, spreads),
        })
        return level, record

    sat.fit_level, sl.fit_level = wrapped, wrapped
    try:
        yield
    finally:
        sat.fit_level, sl.fit_level = real, real


def run_command(args) -> int:
    declared = k626.declared_document()
    h = args.horizon
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="satiation_ties_747")
    k626.rolling_constants()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    dated = k626.dated_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]

    def backtest(predictor, name, features, per_release):
        scope = h41_release.release_dating() if per_release else contextlib.nullcontext()
        with s587.switched_on(), scope:
            return rolling_exceedance_backtest(
                rows, predictor=predictor, model_name=name, features=features,
                registry=dated if per_release else registry,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )

    def build(name):
        if name == "structural_fitted":
            f = sl.features_at_horizon(h, "fitted")
            return sl.structural_exceedance(f, splits, minimum_history=minimum, satiation="fitted"), f, False
        if name == "structural_kinked_fitted":
            f = sl.features_at_horizon(h, "kinked_fitted")
            return sl.structural_exceedance(f, splits, minimum_history=minimum, satiation="kinked_fitted"), f, True
        if name == "projected_fitted":
            f = tuple(pr.features_at_horizon(h))
            return ml.pressure_projected_hinge_exceedance(f, splits, minimum, horizon=h, satiation="fitted"), f, False
        design, f = s587.cm.component_features(h, ml.COMBINED_BLOCKS)
        return ml.pressure_combined_ordinary_exceedance(
            design, splits, minimum_history=minimum, blocks=ml.COMBINED_BLOCKS,
            calibration=ml.COMBINED_CALIBRATION, satiation="fitted",
        ), f, False

    out: Dict[str, list] = {}
    for name in ("structural_fitted", "projected_fitted", "risk_gbm+combined_fitted", "structural_kinked_fitted"):
        inner, features, per_release = build(name)
        log: list = []
        calls: list = []
        with recording(calls):
            backtest(s587._logged(inner, log), name, features, per_release)
        if len(calls) != len(log):
            raise SystemExit(f"{name}: {len(calls)} fits for {len(log)} refits")
        out[name] = [
            {"first_anchor": entry["first_anchor"], **call} for entry, call in zip(log, calls)
        ]
        print(json.dumps({"horizon": h, "row": name, "refits": len(log)}), flush=True)
    args.output.write_text(json.dumps({"horizon": h, "refits": out}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def summary_command(args) -> int:
    table: Dict[str, Counter] = {}
    rows = Counter()
    for h in range(1, 6):
        document = json.loads(Path(args.inputs.format(h=h)).read_text(encoding="utf-8"))
        for name, refits in document["refits"].items():
            for r in refits:
                year = r["first_anchor"][:4]
                if r["reason"] == "too few pairs":
                    kind = "too_few_pairs"
                elif r["reason"] and r["reason"].startswith("not identified"):
                    kind = "not_identified"
                elif abs(r["old_level"] - r["level"]) > 1e-12:
                    kind = "level_moved"
                else:
                    kind = "unchanged"
                table.setdefault(f"{name}|{year}", Counter())[kind] += 1
                for rtol, tied in r["not_identified_at"].items():
                    if tied:
                        table[f"{name}|{year}"][f"not_identified_at_rtol_{rtol}"] += 1
                rows[(name, kind)] += 1
    result = {k: dict(v) for k, v in sorted(table.items())}
    args.output.write_text(json.dumps({"by_row_and_year": result}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    p.add_argument("--panel", type=Path)
    p.add_argument("--horizon", type=int)
    p.add_argument("--output", type=Path, required=False)
    s = sub.add_parser("summary")
    s.add_argument("--inputs", required=True)
    s.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.command == "summary":
        return summary_command(args)
    return run_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
