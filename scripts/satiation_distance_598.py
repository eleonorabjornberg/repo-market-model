"""The rolling satiation distance in the tier-1 passers (#598, follow-up to #587): scoring and report.

A scratch measurement, not a record: it writes JSON, Markdown and SVG to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/satiation_distance_598.json`, which this script refuses to read unless it is committed and unchanged,
and in the candidates in `metadata/pressure_judge/candidates/`. The rolling level is #587's, constants unchanged
(`metadata/satiation_587.json`). The two columns it adds are off in every published declaration and switched on for these runs only.
Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D.csv
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
    for h in 1 2 3 4 5: for m in risk_gbm risk_gbm_base: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model $m \\
        --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/both_${m}_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py merge --parents OUT/both_risk_gbm_h$h.json OUT/both_risk_gbm_base_h$h.json --output OUT/both_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_587.py reference --input OUT/q_h$h.json --output OUT/ql_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/satiation_distance_598.py run --panel AUG2D.csv --published PUBLISHED.csv --horizon $h --output OUT/dist_h$h.json
    for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json \\
        --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/dist_h?.json
    PYTHONPATH=src python3 scripts/satiation_distance_598.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/dist_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/satiation_distance_598.py report --compare OUT/compare.json --output OUT/report.md
    PYTHONPATH=src python3 scripts/satiation_distance_598.py hinge-share --panel AUG2.csv --output OUT/hinge-share.md

`run` scores the three variants of the declaration, each the parent passer (settlements dated from the announcement, the H.4.1 read per
release: the "both" arm of #541) with one extra input, walk-forward at +5 and +10 bp on the shared fold grid. The parents are the
`both` runs of `announcement_dating_rescore.py`. `compare` is the judge's own cut-offs and tiers under the weighted rule in force, onset
recall by calendar year, Brier score and log loss, predicted against realised rate by regime and day type, every variant paired with its
parent and with the references with 90% stationary-bootstrap intervals by regime and pressure-day type, and the onsets a variant gains
and loses against its parent by date. `report` writes the tables.
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
from typing import Dict, List, Sequence
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.exploration import panel_end  # noqa: E402
from repo_model import (  # noqa: E402
    contract, h41_release, measurement_fields, ml, pressure_judge as pj, satiation as sat, scarcity,
)
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "satiation_distance_598.json"
PARENT_DECLARATION = REPO / "metadata" / "satiation_587.json"
H41 = REPO / "metadata" / "h41_release_dating.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s587 = _load("satiation_587")
cm, ann, rds, fa = s587.cm, s587.ann, s587.rds, s587.fa


# -- the declaration -----------------------------------------------------------------------------------------------


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def all_rows() -> List[str]:
    document = declared_document()
    return list(document["rows"]["controls"]) + list(document["rows"]["new"])


def paired_with_model(name: str) -> List[str]:
    """The parent row of a variant."""

    parent = declared_document()["rows"]["pairs"].get(name)
    return [parent] if parent else []


def rolling_constants() -> dict:
    """The rolling level's constants, read from #587's declaration and checked against the module's."""

    rolling = rds.committed_declaration(PARENT_DECLARATION)["forms"]["rolling"]
    if (rolling["quantile"], rolling["window_rows"], rolling["minimum_rows"]) != (
        sat.ROLLING_QUANTILE, sat.ROLLING_WINDOW, sat.ROLLING_MINIMUM,
    ):
        raise SystemExit("the rolling level's constants in metadata/satiation_587.json are not the module's")
    return rolling


def parent_features(parent: str, horizon: int) -> tuple:
    """The parent passer's features at `horizon`, under the settlement and H.4.1 timing of the "both" arm."""

    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    model = parent.split("+")[0]
    return ann.features_for(parents, parents["candidates"][model], horizon, True)


def variant_features(name: str, horizon: int) -> tuple:
    """A variant's features: its parent's with the one column added."""

    spec = declared_document()["variants"][name]
    return parent_features(spec["parent"], horizon) + (spec["column"],)


def switched_on():
    """The scarcity state, the measurement fields and the two distance columns, for this run only."""

    import contextlib

    @contextlib.contextmanager
    def context():
        fields = {**measurement_fields.COLUMN_FIELDS, **sat.DISTANCE_COLUMN_FIELDS}
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

    return context()


# -- panel ---------------------------------------------------------------------------------------------------------


def _cell(value):
    return "" if value is None else repr(float(value))


def distance_rule() -> InformationRule:
    """The rule the distance columns read the two legs through: each leg per H.4.1 release (#541, #622).

    The rows these columns join read `reserve_balances` per release (`metadata/h41_release_dating.json`); the columns
    must read the same print, not the weekly lag that is one release older on Fridays and Mondays. Callers hold
    `h41_release.release_dating()` open while the rule reads.
    """

    registry = h41_release.release_dated_registry(measurement_fields.load_registry(), h41_release.load_release_dating(H41))
    return InformationRule(registry, sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)


def distance_rows(rows, end: date, check_every: int, rule: InformationRule = None, release: bool = True):
    """`rows` with the two distance columns, built on the release-dated rule and checked for look-ahead (#622).

    `release=False` with a `rule` reads the earlier weekly lag, for the comparison of #621 only.
    """

    rolling = rolling_constants()
    kw = dict(q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"])
    with switched_on(), (h41_release.release_dating() if release else contextlib.nullcontext()):
        rule = rule or distance_rule()
        built = sat.build_distance_columns(rows, rule, last_day=end, **kw)
        sat.check_distance_no_future(rows, built, rule, last_day=end, indices=range(0, len(built), check_every), **kw)
    return built


def hinge_share_by_year(built) -> Dict[str, List[int]]:
    """`{year: [days the hinge is on, days with a value]}`: the share of days the ratio is below the rolling level (#621)."""

    out: Dict[str, List[int]] = {}
    for row in built:
        value = row.values.get(sat.HINGE_COLUMN)
        if value is None:
            continue
        cell = out.setdefault(str(row.date.year), [0, 0])
        cell[0] += 1 if value > 0.0 else 0
        cell[1] += 1
    return out


def hinge_share_markdown(shares: Dict[str, Dict[str, List[int]]]) -> str:
    """Markdown table of the shares, one row per way of reading the reserves leg, from `{label: hinge_share_by_year}`."""

    years = sorted({year for share in shares.values() for year in share})
    lines = [
        "| reserves read | " + " | ".join(years) + " |",
        "|---|" + "---|" * len(years),
    ]
    for label, share in shares.items():
        cells = []
        for year in years:
            on, days = share.get(year, [0, 0])
            cells.append(f"{100.0 * on / days:.0f}% ({on} of {days})" if days else "–")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def hinge_share_command(args) -> int:
    """The share of days the rolling level's hinge is on, by year, on the weekly lag and on the per-release read (#621)."""

    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="satiation_distance_598")
    rows = [row for row in load_daily_panel(args.panel) if row.date <= end]
    old_rule = None
    with switched_on():
        old_rule = InformationRule(measurement_fields.load_registry(), sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
    shares = {
        "weekly lag (the first build, #598)": hinge_share_by_year(distance_rows(rows, end, args.check_every, rule=old_rule, release=False)),
        "per H.4.1 release (#622, in force)": hinge_share_by_year(distance_rows(rows, end, args.check_every)),
    }
    text = hinge_share_markdown(shares)
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def panel_command(args) -> int:
    declared = declared_document()
    end = panel_end(args.end, date.fromisoformat(declared["scoring"]["last_day"]), where="satiation_distance_598.panel")
    require_unlocked([end], where="satiation_distance_598")
    rows = [row for row in load_daily_panel(args.panel) if row.date <= end]
    built = distance_rows(rows, end, args.check_every)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + [sat.DISTANCE_COLUMN, sat.HINGE_COLUMN]))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary = {}
    for column in (sat.DISTANCE_COLUMN, sat.HINGE_COLUMN):
        values = [r.values[column] for r in built if r.values.get(column) is not None]
        summary[column] = {"rows": len(values), "min": min(values), "median": statistics.median(values), "max": max(values)}
    print(json.dumps({
        "output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "rows": len(built),
        "checked_rows": len(range(0, len(built), args.check_every)), **summary,
    }, indent=1))
    return 0


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    scoring = declared["scoring"]
    last = panel_end(args.end, date.fromisoformat(scoring["last_day"]), where="satiation_distance_598.run")
    require_unlocked([last], where="satiation_distance_598")
    rolling_constants()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    judge_commit = _load("pressure_judge").require_committed_declaration(pj.DEFAULT_DECLARATION)
    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, h)
    forecasts: Dict[str, dict] = {}
    settings: Dict[str, dict] = {}
    for name, spec in declared["variants"].items():
        features = variant_features(name, h)
        kind = parents["candidates"][spec["model"]]["kind"]
        predictor = ml.pressure_risk_date_exceedance(kind, features, splits, minimum_history=minimum)
        with switched_on(), h41_release.release_dating():
            report = rolling_exceedance_backtest(
                timed_rows, predictor=predictor, model_name=name, features=features, registry=timed_registry,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )
        forecasts[name] = rds.column(report)
        settings[name] = fa._settings(report)
        print(json.dumps({"horizon": h, "row": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare -------------------------------------------------------------------------------------------------------


def compare_command(args) -> int:
    """The combined page's comparison (`combined_model_561.compare_command`) over this measurement's rows, with the
    onsets each variant gains and loses against its parent added."""

    cm.declared_document = declared_document
    cm.all_rows = all_rows
    cm.paired_with_model = paired_with_model
    cm.DECLARATION = DECLARATION
    calls: List[tuple] = []
    original_load = cm._load

    def recording_load(name):
        module = original_load(name)
        if name == "ngboost_laplace_check":
            inner = module.only_this_row_warns

            def only_this_row_warns(days, onset, caught, others):
                calls.append((list(days), list(onset), list(caught)))
                return inner(days, onset, caught, others)

            module.only_this_row_warns = only_this_row_warns
        return module

    cm._load = recording_load
    args_markdown = args.markdown
    args.markdown = None
    try:
        status = cm.compare_command(args)
    finally:
        cm._load = original_load
        args.markdown = args_markdown
    rows_names = all_rows()
    if len(calls) != 2 * len(rows_names):
        raise SystemExit(f"expected two only-row calls per row, saw {len(calls)}")
    flags = {name: calls[2 * k] for k, name in enumerate(rows_names)}
    days = flags[rows_names[0]][0]
    onset = flags[rows_names[0]][1]
    result = json.loads(Path(args.output).read_text())
    gained_lost = {}
    for name in declared_document()["rows"]["new"]:
        parent = paired_with_model(name)[0]
        mine, theirs = flags[name][2], flags[parent][2]
        gained_lost[name] = {
            "parent": parent,
            "gained": [d.isoformat() for d, o, a, b in zip(days, onset, mine, theirs) if o and a and not b],
            "lost": [d.isoformat() for d, o, a, b in zip(days, onset, mine, theirs) if o and b and not a],
            "both": sum(1 for o, a, b in zip(onset, mine, theirs) if o and a and b),
            "onsets": int(sum(onset)),
        }
    result["gained_lost"] = gained_lost
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(_markdown(result, declared_document(), list(result["readings"]["weighted"]), rows_names), encoding="utf-8")
    return status


def _markdown(result: dict, document: dict, names: List[str], rows_names: List[str]) -> str:
    text = cm.markdown(result, document, names, rows_names)
    return text.replace("# The combined model (#561)", "# The rolling satiation distance in the tier-1 passers (#598)", 1)


# -- report --------------------------------------------------------------------------------------------------------

FAMILIES = (
    ("risk_gbm+settle+h41 (the passer of #541)", ("risk_gbm+settle+h41", "risk_gbm+settle+h41+dist_roll", "risk_gbm+settle+h41+hinge_roll")),
    ("risk_gbm_base+settle+h41", ("risk_gbm_base+settle+h41", "risk_gbm_base+settle+h41+hinge_roll")),
)
_audit = s587._audit


def _iv(cell) -> str:
    return cm.lf._iv(cell)


def report_text(compare: dict) -> str:
    out: List[str] = [
        "# The rolling satiation distance in the tier-1 passers (#598)", "",
        "Generated by `scripts/satiation_distance_598.py report`; not edited by hand.", "",
    ]
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
    out += ["## Verdicts that change against the parent (weighted rule in force)", "", *(changed or ["None: no tier or pass changes."]), ""]
    tables = compare["judge_tables"]["weighted"]
    for title, names in FAMILIES:
        out += [f"## {title}", ""]
        out += ["### The judge's Table 1 (weighted rule in force)", "", *s587.judge_table(tables, "Table 1.", names)]
        out += ["### Tier 1 at each lead alone, inside and outside 2018-19, equal-weight regime recall (the judge's Table 1b)", "", *s587.judge_lead_blocks(tables, names)]
        out += ["### Share of the pressure days flagged at h = 1, by regime and pressure-day type (the judge's Table 2)", "", *s587.judge_table(tables, "Table 2.", names)]
        years = sorted({y for n in names for y in compare["by_year"].get(n, {})})
        out += ["### Onsets warned by calendar year (lead >= 1, any horizon 1 to 5; 2019 and 2025 in bold)", "",
                "| row | " + " | ".join(f"**{y}**" if y in ("2019", "2025") else y for y in years) + " |", "|---|" + "---|" * len(years)]
        for n in names:
            cells = compare["by_year"][n]
            out.append(f"| {n} | " + " | ".join("–" if y not in cells else f"{cells[y][1]} of {cells[y][0]}" for y in years) + " |")
        out += ["", "### Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5", "",
                "| row | cell | days | predicted | realised |", "|---|---|---|---|---|"]
        for n in names:
            for key, c in compare["calibration"][n].items():
                out.append(f"| {n} | {key} | {c['days']:g} | {c['predicted']:.4f} | {c['realised']:.4f} |")
        out += ["", "### Brier score at +5 bp, pooled by horizon", "", "| row | " + " | ".join(f"h = {h}" for h in range(1, 6)) + " |", "|---|" + "---|" * 5]
        for n in names:
            sc = compare["scores"][n]
            out.append(f"| {n} | " + " | ".join(f"{sc[str(h)]['brier']:.4f}" for h in range(1, 6)) + " |")
        out.append("")
        for n in names[1:]:
            gl = compare["gained_lost"][n]
            out += [f"### {n}: onsets gained and lost against {gl['parent']}, by date (any horizon 1 to 5, lead >= 1)", "",
                    f"Warned by both: {gl['both']} of {gl['onsets']} onsets.", "",
                    f"Gained ({len(gl['gained'])}): " + (", ".join(gl["gained"]) or "none") + ".", "",
                    f"Lost ({len(gl['lost'])}): " + (", ".join(gl["lost"]) or "none") + ".", ""]
            for ref in dict.fromkeys(paired_with_model(n) + list(declared_document()["references"]["pair_against"])):
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
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    compare = json.loads(Path(args.compare).read_text())
    args.output.write_text(report_text(compare), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check-every", type=int, default=40)
    p.add_argument("--end", help="last day kept, ISO; default this script's own end (at most 2026-09-03, #684)")
    p = sub.add_parser("hinge-share")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check-every", type=int, default=40)
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--end", help="last scored day, ISO; default the committed declaration's own (at most 2026-09-03, #684: a scratch scored span, no published declaration moves)")
    p = sub.add_parser("compare")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("report")
    p.add_argument("--compare", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {"panel": panel_command, "hinge-share": hinge_share_command, "run": run_command, "compare": compare_command, "report": report_command}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
