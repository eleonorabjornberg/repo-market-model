"""A time-varying satiation level for the reserve-demand terms (#587, ruling on #569): scoring and report.

A scratch measurement, not a record: it writes JSON, Markdown and SVG to the paths it is given and nothing into
`docs/runs/`. Every choice is in `metadata/satiation_587.json`, which this script refuses to read unless it is committed
and unchanged, and in the candidates in `metadata/pressure_judge/candidates/`. Every input beyond the published panel is
off in every published declaration and switched on for these runs only. Scored days are 2018-06-29 to 2025-12-31; no
day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/satiation_587.py panel --panel AUG4.csv --output AUG5.csv
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
    for h in 1 2 3 4 5: for m in risk_gbm risk_logistic: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model $m --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/both_${m}_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py merge --parents OUT/both_risk_gbm_h$h.json OUT/both_risk_logistic_h$h.json --output OUT/both_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py reference --input OUT/q_h$h.json --output OUT/ql_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py run --panel AUG5.csv --published PUBLISHED.csv --horizon $h \\
        --parents OUT/both_h$h.json --output OUT/sat_h$h.json
    for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json \\
        --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/sat_h?.json
    PYTHONPATH=src python3 scripts/satiation_587.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/sat_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/satiation_587.py levels --panel AUG5.csv --rows 'OUT/sat_h{h}.json' --output OUT/levels.json --svg OUT/levels.svg
    PYTHONPATH=src python3 scripts/satiation_587.py report --compare OUT/compare.json --levels OUT/levels.json --output OUT/report.md

`run` scores the three models of the declaration (the structural model of #542, projected reserves of #545 and the
combined model of #563) under each form, with the models as scored on main as the fixed-0.12 controls, walk-forward at
+5 and +10 bp on the shared fold grid. `compare` is the judge's own cut-offs and tiers under the weighted rule in force,
onset recall by calendar year, Brier score and log loss, and every row paired with its fixed version and with the
references, with 90% stationary-bootstrap intervals by regime and pressure-day type. `levels` is the level each form sets
over time against the reserves ratio. `report` writes the tables.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import json
import statistics
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Optional, Sequence
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import (  # noqa: E402
    contract, measurement_fields, ml, net_settlement as ns, pressure_judge as pj, projected_reserves as pr, satiation as sat,
    scarcity, structural_liquidity as sl,
)
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "satiation_587.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
FORMS = ("rolling", "fitted")
TIMING_SUFFIX = "+settle+h41"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


cm = _load("combined_model_561")
rds, ann, fa = cm.rds, cm.ann, cm.fa


# -- the declaration -----------------------------------------------------------------------------------------------


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def all_rows() -> List[str]:
    document = declared_document()
    return list(document["rows"]["controls"]) + list(document["rows"]["new"])


def paired_with_model(name: str) -> List[str]:
    """The fixed-0.12 version of `name`; for a time-varying projected row also the linear model as scored."""

    document = declared_document()
    mine = document["rows"]["pairs"].get(name)
    out = [mine] if mine else []
    if mine and mine in document["rows"]["pairs"]:
        out.append(document["rows"]["pairs"][mine])
    return out


@contextlib.contextmanager
def switched_on():
    """The scarcity state, #377's fields, the net settlement and projected columns and the satiation column."""

    fields = {**measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS, **sat.COLUMN_FIELDS}
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


# -- panel ---------------------------------------------------------------------------------------------------------


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="satiation_587")
    rolling = declared["forms"]["rolling"]
    rows = [row for row in load_daily_panel(args.panel) if row.date <= end]
    with switched_on():
        rule = InformationRule(measurement_fields.load_registry(), sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        built = sat.build_columns(
            rows, rule, last_day=end, q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"]
        )
        sat.check_no_future(
            rows, built, rule, last_day=end, indices=range(0, len(built), args.check_every),
            q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"],
        )
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + [sat.ROLLING_COLUMN]))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    values = [r.values[sat.ROLLING_COLUMN] for r in built if r.values.get(sat.ROLLING_COLUMN) is not None]
    print(json.dumps({
        "output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "rows": len(built),
        "checked_rows": len(range(0, len(built), args.check_every)),
        "satiation_roll": {"rows": len(values), "min": min(values), "median": statistics.median(values), "max": max(values)},
    }, indent=1))
    return 0


# -- small plumbing ------------------------------------------------------------------------------------------------


def merge_command(args) -> int:
    """The announcement-dating runs of the two passers as one document, as the combined model's page does."""

    documents = [json.loads(Path(p).read_text()) for p in args.parents]
    out = dict(documents[0])
    out["forecasts"] = {}
    for document in documents:
        if document["panel_sha256"] != documents[0]["panel_sha256"] or document["horizon"] != documents[0]["horizon"]:
            raise SystemExit("the passers were scored on different panels or horizons")
        out["forecasts"].update(document["forecasts"])
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "rows": sorted(out["forecasts"])}))
    return 0


def reference_command(args) -> int:
    """`q_h.json` with only the ngboost_laplace row (the judge refuses the undeclared rows)."""

    document = json.loads(Path(args.input).read_text())
    document["forecasts"] = {"ngboost_laplace": document["forecasts"]["ngboost_laplace"]}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- run -----------------------------------------------------------------------------------------------------------


def _logged(predictor, log: list):
    """The predictor, unchanged, with each refit's satiation record kept."""

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        result = predictor(train_rows, feature_rows, taus, information=information, histories=histories)
        settings = dict(result.model_settings)
        entry = {
            "first_anchor": feature_rows[0].date.isoformat(),
            "last_training_row": train_rows[-1].date.isoformat(),
            "training_rows": len(train_rows),
            "served_days": len(feature_rows),
        }
        if hasattr(predictor, "fits") and predictor.fits:
            record = predictor.fits[-1]
            entry.update({k: v for k, v in record.items() if k in ("satiation_level", "fitted", "reason", "pairs", "slope")})
        for key in ("satiation_fit", "combined_satiation_fit"):
            if key in settings:
                entry.update({k: v for k, v in settings[key].items()})
        if "combined_satiation_level" in settings:
            entry["satiation_level"] = settings["combined_satiation_level"]
        if "satiation_fit" in settings:
            entry["satiation_level"] = settings["satiation_fit"]["satiation_level"]
        log.append(entry)
        return result

    return fit_predict


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="satiation_587")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]
    judge_script = _load("pressure_judge")
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)

    def backtest(predictor, name, features):
        with switched_on():
            return rolling_exceedance_backtest(
                rows, predictor=predictor, model_name=name, features=features, registry=registry,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )

    def standalone(report, name):
        forecast = pj.report_forecast(name, report)
        return {f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, values)} for tau, values in forecast.probabilities.items()}

    standalone_columns: Dict[str, dict] = {}
    refits: Dict[str, list] = {}
    settings: Dict[str, dict] = {}
    # the structural model: the control (as scored) and the two forms
    for name, form in (("structural_liquidity", "fixed"), ("structural_rolling", "rolling"), ("structural_fitted", "fitted")):
        features = sl.features_at_horizon(h, form)
        log: list = []
        inner = sl.structural_exceedance(features, splits, minimum_history=minimum, satiation=form)
        report = backtest(_logged(inner, log), name, features)
        standalone_columns[name], refits[name] = standalone(report, name), log
        settings[name] = {k: v for k, v in report.model_settings.items()}
        print(json.dumps({"horizon": h, "row": name, "refits": len(log), "done": True}), flush=True)
    # projected reserves: the control (linear, as scored), the fixed hinge, and the two forms
    for name, form in (
        ("projected_reserves", "fixed"), ("projected_hinge_fixed", "fixed_kink"),
        ("projected_rolling", "rolling"), ("projected_fitted", "fitted"),
    ):
        features = tuple(pr.features_at_horizon(h)) + ((sat.ROLLING_COLUMN,) if form == "rolling" else ())
        log = []
        if form == "fixed":
            inner = ml.pressure_logistic_exceedance(features, splits, minimum_history=minimum)
        else:
            inner = ml.pressure_projected_hinge_exceedance(features, splits, minimum, horizon=h, satiation=form)
        report = backtest(_logged(inner, log), name, features)
        standalone_columns[name], refits[name] = standalone(report, name), log
        settings[name] = {k: v for k, v in report.model_settings.items()}
        print(json.dumps({"horizon": h, "row": name, "refits": len(log), "done": True}), flush=True)
    # the combined model: the control (as scored) and the three variants, under the passer and the gate
    components: Dict[str, dict] = {}
    for name, form in (
        ("risk_gbm+combined", "fixed"), ("risk_gbm+combined_hinge_fixed", "fixed_kink"),
        ("risk_gbm+combined_rolling", "rolling"), ("risk_gbm+combined_fitted", "fitted"),
    ):
        design, features = cm.component_features(h, ml.COMBINED_BLOCKS)
        if form == "rolling":
            design, features = design + (sat.ROLLING_COLUMN,), features + (sat.ROLLING_COLUMN,)
        log = []
        inner = ml.pressure_combined_ordinary_exceedance(
            design, splits, minimum_history=minimum, blocks=ml.COMBINED_BLOCKS, calibration=ml.COMBINED_CALIBRATION, satiation=form
        )
        report = backtest(_logged(inner, log), name, features)
        components[name] = rds.column(report)
        refits[name] = log
        settings[name] = fa._settings(report)
        print(json.dumps({"horizon": h, "row": name, "refits": len(log), "done": True}), flush=True)
    parents_doc = json.loads(Path(args.parents).read_text())
    if parents_doc["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit(f"{args.parents} was scored on another panel")
    timed_rows, _registry = ann.arm_inputs("both", rows, registry, h)
    by_date = {row.date: row for row in timed_rows}
    days = sorted(next(iter(components.values()))[f"{taus[0]:g}"])
    off = {day: not ann.risk_flag(splits, by_date[date.fromisoformat(day)].values, True) for day in days}
    passer = parents_doc["forecasts"]["risk_gbm" + TIMING_SUFFIX]
    forecasts = dict(standalone_columns)
    for name, column in components.items():
        forecasts[name] = cm.apply_gate(cm.combine(passer, column, off), off)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "risk_date_check": {"scored_days": len(days), "risk_dates": sum(1 for v in off.values() if not v)},
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
    return text.replace("# The latent funding-stress factor (#543)", "# Time-varying satiation level (#587)", 1)


# -- levels --------------------------------------------------------------------------------------------------------


def levels_command(args) -> int:
    """The satiation level each form sets over time, and the reserves ratio, from the panel and the run outputs."""

    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    rows = [r for r in load_daily_panel(args.panel) if r.date <= end]
    with switched_on():
        rule = InformationRule(measurement_fields.load_registry(), sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        ratios = sat.asof_ratios(rows, rule, last_day=end)
    rolling = [r.values.get(sat.ROLLING_COLUMN) for r in rows]
    series = {
        "dates": [r.date.isoformat() for r in rows],
        "ratio": ratios,
        "rolling": rolling,
        "fixed": [sat.FIXED] * len(rows),
    }
    fitted: Dict[str, Dict[str, list]] = {}
    for h in declared["horizons"]:
        document = json.loads(Path(str(args.rows).format(h=h)).read_text())
        for name in ("structural_fitted", "projected_fitted", "risk_gbm+combined_fitted"):
            fitted.setdefault(name, {})[str(h)] = [
                {"from": entry["first_anchor"], "level": entry.get("satiation_level"), "fitted": entry.get("fitted"), "pairs": entry.get("pairs")}
                for entry in document["refits"][name]
            ]
    out = {"series": series, "fitted": fitted}
    args.output.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    if args.svg:
        args.svg.write_text(_svg(series, fitted["structural_fitted"]["1"]), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "svg": str(args.svg) if args.svg else None}))
    return 0


def _svg(series: dict, fitted: list) -> str:
    """The reserves ratio (grey), the rolling level (blue), the fitted level of the structural model at h = 1 (orange) and 0.12."""

    width, height, left, bottom, top = 920, 420, 60, 40, 24
    dates = series["dates"]
    n = len(dates)
    lo, hi = 0.06, 0.20
    x = lambda i: left + (width - left - 20) * i / max(1, n - 1)
    y = lambda v: top + (height - top - bottom) * (1 - (v - lo) / (hi - lo))
    place = {d: i for i, d in enumerate(dates)}

    def path(values, color, dash=""):
        pts = [f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values) if v is not None]
        return f'<polyline fill="none" stroke="{color}" stroke-width="1.5" {dash} points="{" ".join(pts)}"/>'

    steps = []
    for k, entry in enumerate(fitted):
        if entry["level"] is None:
            continue
        start = place.get(entry["from"], 0)
        stop = place.get(fitted[k + 1]["from"], n - 1) if k + 1 < len(fitted) else n - 1
        steps.append(f'<line x1="{x(start):.1f}" x2="{x(stop):.1f}" y1="{y(entry["level"]):.1f}" y2="{y(entry["level"]):.1f}" stroke="#e08a1e" stroke-width="2"/>')
    ticks = []
    for year in range(int(dates[0][:4]), int(dates[-1][:4]) + 1):
        d = next((dd for dd in dates if dd >= f"{year}-01-01"), None)
        if d:
            ticks.append(f'<text x="{x(place[d]):.1f}" y="{height - 14}" font-size="11" text-anchor="middle" fill="#555">{year}</text>')
    for v in (0.08, 0.10, 0.12, 0.14, 0.16, 0.18):
        ticks.append(f'<text x="{left - 6}" y="{y(v) + 4:.1f}" font-size="11" text-anchor="end" fill="#555">{v:.2f}</text>')
        ticks.append(f'<line x1="{left}" x2="{width - 20}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#ddd"/>')
    legend = (
        '<text x="70" y="16" font-size="12" fill="#888">reserves / bank assets (as-of)</text>'
        '<text x="290" y="16" font-size="12" fill="#2b6cb0">rolling level (form a)</text>'
        '<text x="470" y="16" font-size="12" fill="#e08a1e">fitted level, structural model at h = 1 (form b)</text>'
        '<text x="790" y="16" font-size="12" fill="#333">fixed 0.12</text>'
    )
    body = "".join(ticks) + path(series["ratio"], "#999") + path(series["rolling"], "#2b6cb0") + "".join(steps) + path(series["fixed"], "#333", 'stroke-dasharray="4 3"')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="sans-serif"><rect width="{width}" height="{height}" fill="#fff"/>{legend}{body}</svg>\n'
    )


# -- report --------------------------------------------------------------------------------------------------------

_audit = _load("audit_fixes_578")

FAMILIES = (
    ("Structural liquidity (#542)", ("structural_liquidity", "structural_rolling", "structural_fitted")),
    ("Projected reserves (#545)", ("projected_reserves", "projected_hinge_fixed", "projected_rolling", "projected_fitted")),
    ("Combined model (#563) under the passer and the gate",
     ("risk_gbm+combined", "risk_gbm+combined_hinge_fixed", "risk_gbm+combined_rolling", "risk_gbm+combined_fitted")),
)


def _iv(cell) -> str:
    return cm.lf._iv(cell)


def _blocks(text: str) -> List[str]:
    return text.split("\n\n")


def judge_table(text: str, title: str, names: Sequence[str]) -> List[str]:
    """The judge's own table that starts with `title`, cut to the rows of `names` in their order."""

    blocks = _blocks(text)
    for k, block in enumerate(blocks):
        if block.startswith(title):
            table = blocks[k + 1].split("\n")
            rows = {line.split("|")[1].strip(): line for line in table[2:]}
            return [block.split("\n")[0], "", table[0], table[1], *[rows[n] for n in names if n in rows], ""]
    raise SystemExit(f"the judge's tables have no {title!r}")


def judge_lead_blocks(text: str, names: Sequence[str]) -> List[str]:
    """The judge's Table 1b entries (tier 1 at each lead alone, inside and outside 2018-19, equal-weight regime recall)."""

    blocks = _blocks(text)
    start = next(k for k, b in enumerate(blocks) if b.startswith("Table 1b."))
    out: List[str] = []
    for n in names:
        for k in range(start + 1, len(blocks) - 2):
            if blocks[k] == f"{n}:":
                out += [f"**{n}**", "", blocks[k + 1], "", blocks[k + 2], ""]
                break
    return out


def report_text(compare: dict, levels: Optional[dict]) -> str:
    out: List[str] = ["# Time-varying satiation level (#587)", "", "Generated by `scripts/satiation_587.py report`; not edited by hand.", ""]
    verdicts = compare["judge"]["weighted"]
    changed: List[str] = []
    for title, names in FAMILIES:
        control = names[0]
        for n in names[1:]:
            b, a = verdicts[control]["verdict"], verdicts[n]["verdict"]
            moved = [
                f"{label} {_audit._yes(b[key])} to {_audit._yes(a[key])}"
                for key, label in (("tier_1_onset_warning", "tier 1"), ("tier_3_no_crying_wolf", "tier 3"), ("tier_5_week_ahead", "tier 5"), ("passes", "pass"))
                if b[key] != a[key]
            ]
            if moved:
                changed.append(f"- {title}: `{n}` against `{control}`: " + ", ".join(moved))
    out += ["## Verdicts that change against the fixed-0.12 version (weighted rule in force)", "", *(changed or ["None: no tier or pass changes."]), ""]
    tables = compare["judge_tables"]["weighted"]
    for title, names in FAMILIES:
        out += [f"## {title}", ""]
        out += ["### The judge's Table 1 (weighted rule in force)", "", *judge_table(tables, "Table 1.", names)]
        out += ["### Tier 1 at each lead alone, inside and outside 2018-19, equal-weight regime recall (the judge's Table 1b)", "", *judge_lead_blocks(tables, names)]
        out += ["### Share of the pressure days flagged at h = 1, by regime and pressure-day type (the judge's Table 2)", "", *judge_table(tables, "Table 2.", names)]
        years = sorted({y for n in names for y in compare["by_year"].get(n, {})})
        out += ["### Onsets warned by calendar year (lead >= 1, any horizon 1 to 5; 2018, 2020, 2024 and 2025 in bold)", "",
                "| row | " + " | ".join(f"**{y}**" if y in ("2018", "2020", "2024", "2025") else y for y in years) + " |", "|---|" + "---|" * len(years)]
        for n in names:
            cells = compare["by_year"][n]
            out.append(f"| {n} | " + " | ".join("–" if y not in cells else f"{cells[y][1]} of {cells[y][0]}" for y in years) + " |")
        out += ["", "### Brier score at +5 bp, pooled by horizon", "", "| row | " + " | ".join(f"h = {h}" for h in range(1, 6)) + " |", "|---|" + "---|" * 5]
        for n in names:
            sc = compare["scores"][n]
            out.append(f"| {n} | " + " | ".join(f"{sc[str(h)]['brier']:.4f}" for h in range(1, 6)) + " |")
        out.append("")
        for n in names[1:]:
            fixed = _fixed_of(n)
            for ref in dict.fromkeys(paired_with_model(n)):
                paired = compare["paired"].get(n, {}).get(ref)
                if not paired:
                    continue
                out += [f"### {n} against {ref}: Brier difference, reference minus row (positive: the row is better), 90% interval", "",
                        "| h | pooled |", "|---|---|"]
                out += [f"| {h} | {_iv(c['pooled'])} |" for h, c in paired["brier"].items()]
                for dimension in ("regime", "day_type", "scarcity_state"):
                    labels = sorted(paired["brier"]["1"].get(dimension, {}))
                    if not labels:
                        continue
                    out += ["", f"By {dimension}, Brier difference at h = 1 / 3 / 5:", "", f"| {dimension} | days | h = 1 | h = 3 | h = 5 |", "|---|---|---|---|---|"]
                    for label in labels:
                        cells = [paired["brier"][h][dimension][label] for h in ("1", "3", "5")]
                        out.append(f"| {label} | {cells[0]['days']:g} | " + " | ".join(_iv(c) for c in cells) + " |")
                rec = paired["recall"]
                out += ["", f"Onset recall difference, row minus {ref} (each at its own cut-offs, any horizon), pooled: {_iv(rec['pooled'])} on {rec['pooled']['onsets']} onsets.", ""]
    if levels:
        out += ["## The satiation level over time", "",
                "Each form's level against the as-of reserves ratio, by year (the rolling level is the median of its daily values; the fitted "
                "level is the structural model's at h = 1, the median over that year's refits).", "",
                "| year | median ratio | min ratio | rolling level (median) | fitted level, structural h = 1 (median) | fixed |", "|---|---|---|---|---|---|"]
        by_year: Dict[str, dict] = {}
        for i, d in enumerate(levels["series"]["dates"]):
            cell = by_year.setdefault(d[:4], {"ratio": [], "rolling": [], "fitted": []})
            if levels["series"]["ratio"][i] is not None:
                cell["ratio"].append(levels["series"]["ratio"][i])
            if levels["series"]["rolling"][i] is not None:
                cell["rolling"].append(levels["series"]["rolling"][i])
        for entry in levels["fitted"]["structural_fitted"]["1"]:
            if entry["level"] is not None:
                by_year.setdefault(entry["from"][:4], {"ratio": [], "rolling": [], "fitted": []})["fitted"].append(entry["level"])
        med = lambda v: "–" if not v else f"{statistics.median(v):.4f}"
        for year in sorted(by_year):
            c = by_year[year]
            out.append(f"| {year} | {med(c['ratio'])} | {'–' if not c['ratio'] else format(min(c['ratio']), '.4f')} | {med(c['rolling'])} | {med(c['fitted'])} | 0.1200 |")
        out.append("")
    return "\n".join(out) + "\n"


def _fixed_of(name: str) -> str:
    return declared_document()["rows"]["pairs"][name]


def report_command(args) -> int:
    compare = json.loads(Path(args.compare).read_text())
    levels = json.loads(Path(args.levels).read_text()) if args.levels else None
    args.output.write_text(report_text(compare, levels), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check-every", type=int, default=40)
    p = sub.add_parser("merge")
    p.add_argument("--parents", nargs=2, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("reference")
    p.add_argument("--input", required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--parents", required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("compare")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("levels")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--rows", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--svg", type=Path)
    p = sub.add_parser("report")
    p.add_argument("--compare", required=True)
    p.add_argument("--levels")
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {
        "panel": panel_command, "merge": merge_command, "reference": reference_command, "run": run_command,
        "compare": compare_command, "levels": levels_command, "report": report_command,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
