"""A kinked elasticity in the structural model, so a fitted satiation level can bite (#626, ruling on #597): scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/kinked_626.json`, which this script refuses to read unless it is committed and unchanged, and in the
candidates in `metadata/pressure_judge/candidates/`. The inputs beyond the published panel are off in every published declaration
and switched on for these runs only. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read
(`docs/decisions/lockbox.md`). The reserves leg of the ratio, the rolling level and the distance columns are read per H.4.1
release (`metadata/h41_release_dating.json`, ruling on #541; #622).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/kinked_626.py panel --panel AUG4.csv --output AUG5.csv
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model risk_gbm --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/both_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py reference --input OUT/q_h$h.json --output OUT/ql_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/kinked_626.py run --panel AUG5.csv --published PUBLISHED.csv --horizon $h --output OUT/kinked_h$h.json
    for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json \\
        --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/kinked_h?.json
    PYTHONPATH=src python3 scripts/kinked_626.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/kinked_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/kinked_626.py extras --published PUBLISHED.csv --scratch AUG5.csv --bench 'OUT/bench_h{h}.json' \\
        --parents 'OUT/both_h{h}.json' --rows 'OUT/kinked_h{h}.json' --output OUT/extras.json --markdown OUT/extras.md
    PYTHONPATH=src python3 scripts/kinked_626.py report --compare OUT/compare.json --extras OUT/extras.json --output OUT/report.md

`run` scores, walk-forward at +5 and +10 bp on the shared fold grid, the structural model as it stands on main
(`structural_liquidity`), the same model with the reserves read per release (`structural_liquidity+h41`, the like-for-like
control), the two kinked variants (`structural_kinked_fitted`, `structural_kinked_rolling`) and the tier-1 candidate of #598
(`risk_gbm+settle+h41+dist_roll`) with its distance column built per release. `compare` is the judge's own cut-offs and tiers
under the weighted rule in force, onset recall by calendar year, Brier score and log loss, and every row paired with its
controls and the references, with 90% stationary-bootstrap intervals by regime and pressure-day type. `extras` is the share of
days on which the kink is active, by year, and, on the days that are not risk dates, the AUROC and the reliability slope and
intercept (#616) of each row. `report` writes the tables.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
from datetime import date, time
from operator import itemgetter
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Optional, Sequence
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import (  # noqa: E402
    contract, h41_release, measurement_fields, ml, net_settlement as ns, pressure_judge as pj, projected_reserves as pr,
    satiation as sat, scarcity, structural_liquidity as sl,
)
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "kinked_626.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
COMPARATOR = "risk_gbm+settle+h41+dist_roll"
OFF = "risk_gbm+settle+h41"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


sd = _load("satiation_distance_598")
s587 = sd.s587
cm, ann, rds, fa = s587.cm, s587.ann, s587.rds, s587.fa


# -- the declaration -----------------------------------------------------------------------------------------------


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def all_rows() -> List[str]:
    document = declared_document()
    return list(document["rows"]["controls"]) + list(document["rows"]["new"])


def paired_with_model(name: str) -> List[str]:
    """The like-for-like control a row is paired with, then that control's own pair (the structural model as it stands)."""

    document = declared_document()
    mine = document["rows"]["pairs"].get(name)
    out = [mine] if mine else []
    if mine and mine in document["rows"]["pairs"]:
        out.append(document["rows"]["pairs"][mine])
    return out


def rolling_constants() -> dict:
    return sd.rolling_constants()


@contextlib.contextmanager
def switched_on():
    """The scarcity state, #377's fields, the net settlement, projected and satiation columns, for this run only."""

    fields = {
        **measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS, **sat.COLUMN_FIELDS, **sat.DISTANCE_COLUMN_FIELDS,
    }
    with scarcity.measurement_declaration(), mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


def dated_registry() -> dict:
    """The measurement registry with the H.4.1 fields dated by their release (#541, #622)."""

    return h41_release.release_dated_registry(measurement_fields.load_registry(), h41_release.load_release_dating(ann.H41))


# -- panel ---------------------------------------------------------------------------------------------------------


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="kinked_626")
    rolling = rolling_constants()
    kw = dict(q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"])
    rows = [row for row in load_daily_panel(args.panel) if row.date <= end]
    with switched_on(), h41_release.release_dating():
        rule = InformationRule(dated_registry(), sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        built = sat.build_columns(rows, rule, last_day=end, **kw)
        built = sat.build_distance_columns(built, rule, last_day=end, **kw)
        indices = range(0, len(built), args.check_every)
        sat.check_no_future(rows, built, rule, last_day=end, indices=indices, **kw)
        sat.check_distance_no_future(rows, built, rule, last_day=end, indices=indices, **kw)
    columns = [sat.ROLLING_COLUMN, sat.DISTANCE_COLUMN, sat.HINGE_COLUMN]
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + columns))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary = {}
    for column in columns:
        values = [r.values[column] for r in built if r.values.get(column) is not None]
        summary[column] = {"rows": len(values), "min": min(values), "median": statistics.median(values), "max": max(values)}
    print(json.dumps({
        "output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "rows": len(built),
        "checked_rows": len(indices), **summary,
    }, indent=1))
    return 0


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="kinked_626")
    rolling_constants()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    dated = dated_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]
    judge_commit = _load("pressure_judge").require_committed_declaration(pj.DEFAULT_DECLARATION)

    def backtest(predictor, name, features, *, per_release, data=rows, reg=None):
        scope = h41_release.release_dating() if per_release else contextlib.nullcontext()
        with switched_on(), scope:
            return rolling_exceedance_backtest(
                data, predictor=predictor, model_name=name, features=features,
                registry=reg if reg is not None else (dated if per_release else registry),
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )

    forecasts: Dict[str, dict] = {}
    refits: Dict[str, list] = {}
    settings: Dict[str, dict] = {}
    for name, form, per_release in (
        ("structural_liquidity", "fixed", False),
        ("structural_liquidity+h41", "fixed", True),
        ("structural_kinked_fitted", "kinked_fitted", True),
        ("structural_kinked_rolling", "kinked_rolling", True),
    ):
        features = sl.features_at_horizon(h, form)
        log: list = []
        inner = sl.structural_exceedance(features, splits, minimum_history=minimum, satiation=form)
        report = backtest(s587._logged(inner, log), name, features, per_release=per_release)
        forecast = pj.report_forecast(name, report)
        forecasts[name] = {
            f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, values)} for tau, values in forecast.probabilities.items()
        }
        refits[name] = log
        settings[name] = dict(report.model_settings)
        print(json.dumps({"horizon": h, "row": name, "refits": len(log), "done": True}), flush=True)
    # the tier-1 candidate of #598, its distance column per release (the panel's column), settlements dated from the
    # announcement and the H.4.1 read per release: the "both" arm of #541
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    spec = sd.declared_document()["variants"][COMPARATOR]
    features = sd.variant_features(COMPARATOR, h)
    kind = parents["candidates"][spec["model"]]["kind"]
    predictor = ml.pressure_risk_date_exceedance(kind, features, splits, minimum_history=minimum)
    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, h)
    report = backtest(predictor, COMPARATOR, features, per_release=True, data=timed_rows, reg=timed_registry)
    forecasts[COMPARATOR] = rds.column(report)
    settings[COMPARATOR] = fa._settings(report)
    print(json.dumps({"horizon": h, "row": COMPARATOR, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "declarations": settings,
        "refits": refits,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare -------------------------------------------------------------------------------------------------------


def compare_command(args) -> int:
    """The combined page's comparison (`combined_model_561.compare_command`) over this measurement's rows."""

    cm.declared_document = declared_document
    cm.all_rows = all_rows
    cm.paired_with_model = paired_with_model
    cm.DECLARATION = DECLARATION
    cm.markdown = lambda result, document, names, rows_names: _markdown(result, document, names, rows_names)
    return cm.compare_command(args)


def _markdown(result: dict, document: dict, names: List[str], rows_names: List[str]) -> str:
    text = cm.lf.markdown(result, document, names, rows_names)
    return text.replace("# The latent funding-stress factor (#543)", "# Kinked elasticity in the structural model (#626)", 1)


# -- extras --------------------------------------------------------------------------------------------------------


def _logit(p: float) -> float:
    p = min(1.0 - 1e-6, max(1e-6, float(p)))
    return math.log(p / (1.0 - p))


def reliability(p: Sequence[float], y: Sequence[int]) -> Optional[tuple]:
    """`(intercept, slope)` of the logistic regression of the outcome on the logit of the forecast; `None` if it is not identified."""

    x = [_logit(v) for v in p]
    events = sum(y)
    if events == 0 or events == len(y) or max(x) - min(x) < 1e-9:
        return None
    a = b = 0.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for xi, yi in zip(x, y):
            mu = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, a + b * xi))))
            w = mu * (1.0 - mu) + 1e-9
            g0 += yi - mu
            g1 += (yi - mu) * xi
            h00 += w
            h01 += w * xi
            h11 += w * xi * xi
        g0 -= 1e-6 * a
        g1 -= 1e-6 * b
        h00 += 1e-6
        h11 += 1e-6
        det = h00 * h11 - h01 * h01
        if det <= 0.0:
            return None
        step0 = (h11 * g0 - h01 * g1) / det
        step1 = (h00 * g1 - h01 * g0) / det
        a, b = a + step0, b + step1
        if max(abs(step0), abs(step1)) < 1e-8:
            break
    if max(abs(a), abs(b)) > 25.0:
        return None
    return a, b


def _interval(values: Sequence[Optional[float]], level: float) -> Optional[List[float]]:
    kept = sorted(v for v in values if v is not None)
    if len(kept) < 0.5 * len(values) or not kept:
        return None
    lo, hi = (1.0 - level) / 2.0, 1.0 - (1.0 - level) / 2.0
    return [kept[int(lo * (len(kept) - 1))], kept[int(hi * (len(kept) - 1))]]


def extras_command(args) -> int:
    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="kinked_626")
    judge_script = _load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    base = pj.load_declaration()
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    scratch = [r for r in load_daily_panel(args.scratch) if r.date <= end]
    place = {r.date: k for k, r in enumerate(scratch)}
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in base.horizons}
    # ---- the share of days on which the kink is active, by year (h = 1: the decision row is the row before the scored day)
    with switched_on(), h41_release.release_dating():
        rule = InformationRule(dated_registry(), sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        ratios = sat.asof_ratios(scratch, rule, last_day=end)
    rolling = [r.values.get(sat.ROLLING_COLUMN) for r in scratch]
    docs = {h: json.loads(Path(args.rows.format(h=h)).read_text()) for h in base.horizons}
    fitted_log = sorted(
        (entry["first_anchor"], entry.get("satiation_level")) for entry in docs[1]["refits"]["structural_kinked_fitted"]
    )
    first = next(iter(json.loads(Path(args.bench.format(h=1)).read_text())["forecasts"].values()))
    scored = sorted(date.fromisoformat(d) for d in first[f"{base.primary:g}"])
    share: Dict[str, Dict[str, List[int]]] = {"kinked_rolling": {}, "kinked_fitted": {}, "fixed_0.12": {}}
    for day in scored:
        k = place[day] - 1
        if k < 0 or ratios[k] is None:
            continue
        year = str(day.year)
        level_roll = rolling[k]
        level_fit = None
        for anchor, level in fitted_log:
            if anchor <= day.isoformat():
                level_fit = level
        for key, level in (("kinked_rolling", level_roll), ("kinked_fitted", level_fit), ("fixed_0.12", sat.FIXED)):
            if level is not None:
                cell = share[key].setdefault(year, [0, 0])
                cell[0] += 1
                cell[1] += int(ratios[k] < level)
    # ---- off risk dates: AUROC and the reliability line, per horizon
    level, replications, block, seed = base.level, base.replications, base.block_length, base.seed
    names = [
        "structural_liquidity", "structural_liquidity+h41", "structural_kinked_fitted", "structural_kinked_rolling",
        OFF, COMPARATOR, base.persistence, base.climatology,
    ]
    off_days: Dict[str, dict] = {}
    for h in base.horizons:
        columns: Dict[str, Dict[str, float]] = {}
        for template in (args.bench, args.parents, args.rows):
            doc = json.loads(Path(template.format(h=h)).read_text())
            for name, column in doc["forecasts"].items():
                if name in names:
                    columns.setdefault(name, column[f"{base.primary:g}"])
        days = sorted(date.fromisoformat(d) for d in columns[base.climatology])
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=states[h])
        keep = [k for k, label in enumerate(grid.groups["risk_date"]) if label == "0"]
        outcome = [grid.outcomes[base.primary][k] for k in keep]
        p = {n: [columns[n][days[k].isoformat()] for k in keep] for n in names}
        rng = random.Random(seed + h)
        resamples = [pj.stationary_bootstrap_indices(len(keep), block, rng) for _ in range(replications)]
        cell: Dict[str, dict] = {"days": len(keep), "events": sum(outcome)}
        boot = {n: {"auroc": [], "int": [], "slope": []} for n in names}
        for idx in resamples:
            pick = itemgetter(*idx)
            y_b = list(pick(outcome))
            for n in names:
                p_b = list(pick(p[n]))
                boot[n]["auroc"].append(pj.auroc(p_b, y_b))
                line = reliability(p_b, y_b)
                boot[n]["int"].append(None if line is None else line[0])
                boot[n]["slope"].append(None if line is None else line[1])
        control = "structural_liquidity+h41"
        control_auc = pj.auroc(p[control], outcome)
        for n in names:
            line = reliability(p[n], outcome)
            diffs = [
                None if a is None or b is None else a - b for a, b in zip(boot[n]["auroc"], boot[control]["auroc"])
            ]
            auc = pj.auroc(p[n], outcome)
            cell[n] = {
                "auroc": auc, "auroc_interval": _interval(boot[n]["auroc"], level),
                "auroc_minus_control": None if auc is None or control_auc is None else auc - control_auc,
                "auroc_minus_control_interval": _interval(diffs, level),
                "intercept": None if line is None else line[0], "intercept_interval": _interval(boot[n]["int"], level),
                "slope": None if line is None else line[1], "slope_interval": _interval(boot[n]["slope"], level),
                "mean_forecast": sum(p[n]) / len(p[n]), "realised": sum(outcome) / len(outcome),
            }
        off_days[str(h)] = cell
        print(json.dumps({"horizon": h, "off_risk_days": len(keep)}), flush=True)
    out = {"hinge_on_share_by_year": share, "off_risk_dates": off_days, "level": level, "replications": replications}
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(extras_text(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _iv(point, interval, places=3):
    if point is None:
        return "–"
    if interval is None:
        return f"{point:.{places}f}"
    return f"{point:.{places}f} [{interval[0]:.{places}f}, {interval[1]:.{places}f}]"


def extras_text(extras: dict) -> str:
    out = ["# Kinked elasticity: the kink's share of days, and the off-risk-date record (#626)", "",
           "Generated by `scripts/kinked_626.py extras`; not edited by hand.", ""]
    years = sorted({y for cells in extras["hinge_on_share_by_year"].values() for y in cells})
    out += ["## Share of scored days on which the kink is active (the as-of ratio is below the level), by year", "",
            "| level | " + " | ".join(years) + " |", "|---|" + "---|" * len(years)]
    labels = {"kinked_rolling": "rolling level (variant b)", "kinked_fitted": "fitted level (variant a)", "fixed_0.12": "fixed 0.12 (the control's kink point)"}
    for key, cells in extras["hinge_on_share_by_year"].items():
        out.append(f"| {labels[key]} | " + " | ".join(
            "–" if y not in cells else f"{100.0 * cells[y][1] / cells[y][0]:.0f}%" for y in years) + " |")
    out += ["", "## Days that are not risk dates: AUROC and reliability line at +5 bp, by horizon", "",
            "The outcome is regressed on the logit of the forecast, `logit P(y = 1) = intercept + slope * logit(p)`: a calibrated forecast has "
            "intercept 0 and slope 1 (#616). 90% stationary-bootstrap intervals. A row that forecasts a constant on these days has no slope.", ""]
    for h, cell in sorted(extras["off_risk_dates"].items()):
        out += [f"### h = {h}: {cell['days']} days, {cell['events']} above +5 bp", "",
                "| row | AUROC | AUROC minus structural_liquidity+h41 | intercept | slope | mean forecast / realised |", "|---|---|---|---|---|---|"]
        for name, c in cell.items():
            if not isinstance(c, dict):
                continue
            out.append(
                f"| {name} | {_iv(c['auroc'], c['auroc_interval'])} | {_iv(c['auroc_minus_control'], c['auroc_minus_control_interval'])} | "
                f"{_iv(c['intercept'], c['intercept_interval'])} | {_iv(c['slope'], c['slope_interval'])} | {c['mean_forecast']:.4f} / {c['realised']:.4f} |"
            )
        out.append("")
    return "\n".join(out) + "\n"


# -- report --------------------------------------------------------------------------------------------------------

FAMILIES = (
    ("Structural liquidity (#542) and its kinked forms (#626)",
     ("structural_liquidity", "structural_liquidity+h41", "structural_kinked_fitted", "structural_kinked_rolling")),
    ("The tier-1 comparator (#598)", ("risk_gbm+settle+h41", COMPARATOR)),
)


def report_text(compare: dict, extras: Optional[dict]) -> str:
    s587.FAMILIES = FAMILIES
    s587.paired_with_model = paired_with_model
    s587._fixed_of = lambda name: declared_document()["rows"]["pairs"].get(name, "")
    text = s587.report_text(compare, None).replace("# Time-varying satiation level (#587)", "# Kinked elasticity in the structural model (#626)", 1).replace("scripts/satiation_587.py report", "scripts/kinked_626.py report", 1)
    if extras:
        text += "\n" + extras_text(extras).split("\n", 3)[3]
    return text


def report_command(args) -> int:
    compare = json.loads(Path(args.compare).read_text())
    extras = json.loads(Path(args.extras).read_text()) if args.extras else None
    args.output.write_text(report_text(compare, extras), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check-every", type=int, default=40)
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("compare")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("extras")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    for name in ("bench", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("report")
    p.add_argument("--compare", required=True)
    p.add_argument("--extras")
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {
        "panel": panel_command, "run": run_command, "compare": compare_command, "extras": extras_command, "report": report_command,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
