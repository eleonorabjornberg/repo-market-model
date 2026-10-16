"""The announced IORB change in the every-day component of the control row (#579, from #560's diagnosis).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
One row changes. The control `risk_gbm+every_day+gate+settle+h41` (#541, PR #563) serves a day that is not a risk date from a
ridge logistic on `spread_bps`, `sofr_p75_iorb_bps` and `sofr_p99_iorb_bps`, then the gate. The new row,
`risk_gbm+every_day+gate+settle+h41+iorb`, adds `iorb_announced_change_bps` to that logistic and to nothing else: the
risk-date model, the gate, the timing arm (settlements dated from the announcement, the H.4.1 read per release) and the
estimators are the control's. The input is the one `docs/decisions/fomc-point-in-time.md` and `repo_model.announced_iorb`
declare: the IORB change that takes effect after the previous panel day's decision instant and on or before the scored day,
from the notes announced at or before that instant. It is public one panel day ahead only, so it is read at h = 1; at
h >= 2 the as-of rule refuses it (as in `metadata/model_defects_540.json`) and the row's forecasts are the control's,
copied. The declaration is `metadata/iorb_every_day_579.json`, committed before any score; this script refuses a declaration
that is not committed. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read
(`docs/decisions/lockbox.md`; `require_unlocked`).

    # AUG2.csv is the scratch panel of risk_date_severity.py (pressure_v1_1.py panel, then measurement_fields.py panel)
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py declare
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model risk_gbm --panel AUG2.csv \\
        --published PUBLISHED.csv --horizon H --output OUT/both_hH.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H \\
        --parent OUT/both_hH.json --output OUT/iorb_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule RULE --output OUT/judge_RULE.json \\
        --markdown OUT/judge_RULE.md OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py compare --rule RULE --panel PUBLISHED.csv --output OUT/compare_RULE.json \\
        --markdown OUT/compare_RULE.md OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py days --rule RULE --panel PUBLISHED.csv --scratch AUG2.csv \\
        --output OUT/days_RULE.json OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json \\
        --output OUT/summary.md
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from dataclasses import replace
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import panel_end  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "iorb_every_day_579.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
MODEL = "risk_gbm"
ANNOUNCED = "iorb_announced_change_bps"
ARM = "both"
PARENT = "risk_gbm+every_day+gate+settle+h41"
NEW = PARENT + "+iorb"
#: Table 3's header. The statistic is the judge's (`pressure_judge._paired_vectors`): the parent's squared error minus the row's.
PAIRED_BRIER_HEADER = (
    "Table 3. Paired Brier difference against the parent, +5 bp (the parent's squared error minus the row's, so positive favours "
    "the row), 90% interval, h = 1: all days, by regime and by pressure-day type."
)
#: the horizons at which the input is public (one panel day ahead); at the others the row is the control's
READ_AT = (1,)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
fa = _load("risk_date_false_alarm_controls")
ann = _load("announcement_dating_rescore")


# -- the declaration ---------------------------------------------------------------------------------------


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #579 before any score was computed; a measurement, not a record. Nothing here is "
            "published: the input is off in every published declaration, no 2026 day is scored, no rule changes and the live record and "
            "pin do not move"
        ),
        "issue": 579,
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parent": {
            "row": PARENT,
            "model": MODEL,
            "declaration": "metadata/announcement_dating.json, arm both: metadata/risk_date_severity.json's risk_gbm with the every-day component of metadata/risk_date_every_day.json and the 'gate' control of metadata/risk_date_false_alarm_controls.json, scored with settlements dated from the auction announcement and the H.4.1 weeklies read per release (PR #563)",
            "every_day_inputs": list(ml.EVERY_DAY_COMPONENT_INPUTS),
        },
        "row": {
            "name": NEW,
            "change": f"{ANNOUNCED} is added to the every-day component's inputs, and to nothing else: the risk-date model, the gate, the timing arm and the estimators are the parent's",
            "every_day_inputs": list(ml.EVERY_DAY_COMPONENT_INPUTS) + [ANNOUNCED],
            "input": (
                f"{ANNOUNCED} as repo_model.announced_iorb builds it under docs/decisions/fomc-point-in-time.md: the IORB change, in "
                "basis points, that takes effect after the previous panel day's decision instant and on or before the scored day, "
                "summed over the notes announced at or before that decision instant (0.0 when none)"
            ),
            "read_at_horizons": list(READ_AT),
            "at_other_horizons": "the input is not public that far ahead (metadata/sources.json declares it one panel business day before the scored day), so the row's forecasts are the parent's, copied; the same reading as the 'iorb' variant of metadata/model_defects_540.json",
        },
        "variants": "this row and its parent only; no other variant, parent or input",
        "judge": "the judge as declared (metadata/pressure_judge.json), unchanged, under the flat and the weighted rule in force; the benchmarks and the evaluation days, tiers and onsets do not depend on the row",
        "pairing": "the row against its parent, with 90% stationary-bootstrap intervals (the judge's bootstrap), split by regime and pressure-day type and by year",
        "announcement_days": "the scored days on which the input is not 0 (a note announced by the previous decision instant takes effect by the scored day): for each, the parent's and the row's flag at h = 1 under the judge's cut-offs and the outcome; and the flags the row adds or drops on every other day",
        "published": "nothing; the input does not join any published declaration",
    }


def declare_command(args) -> int:
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    DECLARATION.write_text(json.dumps(declaration_document(parents), indent=2) + "\n", encoding="utf-8")
    base = json.loads((CANDIDATES / f"{PARENT}.json").read_text(encoding="utf-8"))
    entry = dict(base)
    entry["track"] = "#579"
    entry["parent"] = PARENT
    entry["features"] = list(base["features"]) + [ANNOUNCED]
    entry["features_at_horizon_2_or_more"] = (
        base["features_at_horizon_2_or_more"] + f"; without {ANNOUNCED} (read at h = 1 only; the row's forecasts are the parent's)"
    )
    entry["calibration"] = (
        base["calibration"].split("; scored under ")[0].replace(
            "changed by one thing: a ridge logistic on spread_bps, sofr_p75_iorb_bps and sofr_p99_iorb_bps serves",
            f"changed by one thing: a ridge logistic on spread_bps, sofr_p75_iorb_bps, sofr_p99_iorb_bps and {ANNOUNCED} serves",
        )
        + "; scored under settlements dated from the auction announcement (metadata/settlement_announcement_dating.json) and the H.4.1 weeklies read per release (metadata/h41_release_dating.json); metadata/iorb_every_day_579.json"
    )
    (CANDIDATES / f"{NEW}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION), "candidate": str(CANDIDATES / f"{NEW}.json")}))
    return 0


# -- run ---------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = panel_end(args.end, date.fromisoformat(declared["scoring"]["last_day"]), where="iorb_every_day_579.run")
    require_unlocked([last], where="iorb_every_day_579")
    parent_document = json.loads(args.parent.read_text(encoding="utf-8"))
    if parent_document["horizon"] != h or parent_document["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit(f"{args.parent} is not the parent's forecasts at h = {h} on this panel")
    if PARENT not in parent_document["forecasts"]:
        raise SystemExit(f"{args.parent} has no {PARENT!r} row")
    if h not in READ_AT:
        forecasts = {NEW: parent_document["forecasts"][PARENT]}
        settings = {NEW: {"identical_to_the_parent": f"{ANNOUNCED} is not public at h = {h}"}}
    else:
        declaration = ann.rds.committed_declaration(ann.DECLARATION)
        spec = declaration["models"][MODEL]
        rows = load_daily_panel(args.panel)
        audit_panel(rows)
        registry = measurement_fields.load_registry()
        rows, registry = ann.arm_inputs(ARM, rows, registry, h)
        by_date = {row.date: row for row in rows}
        splits = load_split_declaration(rds.SPLITS)
        taus = tuple(float(t) for t in declared["thresholds_bp"])
        minimum = declared["scoring"]["minimum_history"]
        settle, h41, _suffix = ann.ARMS[ARM]
        parent_features = ann.features_for(parents, spec, h, settle)
        component_inputs = ml.EVERY_DAY_COMPONENT_INPUTS + (ANNOUNCED,)
        predictor = ml.pressure_risk_date_variant_exceedance(
            spec["kind"], parent_features, splits, minimum, every_day=True, early_prior=False, component_inputs=component_inputs
        )
        features = tuple(dict.fromkeys(parent_features + component_inputs))
        with rds.switched_on(), (h41_release.release_dating() if h41 else contextlib.nullcontext()):
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=NEW,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        column = rds.column(report)
        keys = [f"{tau:g}" for tau in taus]
        days = sorted(column[keys[0]])
        raw = [[column[key][day] for day in days] for key in keys]
        off = [not ann.risk_flag(splits, by_date[date.fromisoformat(day)].values, settle or h == 1) for day in days]
        out = fa.apply_control("gate", fa.CONTROLS["gate"], raw, off, [None] * len(days))
        forecasts = {NEW: {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}}
        settings = {NEW: fa._settings(report)}
    document = {
        "arm": ARM,
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": parent_document["scratch_panel_sha256"] if h not in READ_AT else panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


# -- compare -----------------------------------------------------------------------------------------------


def markdown(document: dict, pairs) -> str:
    out = []
    _arm, name, ref = pairs[0]
    out.append(f"Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the parent `{ref}` and the row `{name}`.\n")
    out.append("| cell | onsets | parent | row | recall difference (90% interval) |")
    out.append("|---|---|---|---|---|")
    for cell, n_onsets in document["onsets_in_cell"].items():
        difference = ann._interval(document["recall_at_some_lead"][name][cell]["recall_difference"])
        out.append(f"| {cell} | {n_onsets} | {document['caught_at_some_lead'][ref][cell]} | {document['caught_at_some_lead'][name][cell]} | {difference} |")
    out.append("\nTable 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.\n")
    out.append("| row | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for label in (ref, name):
        cells = []
        for h in ("1", "2", "3", "4", "5"):
            c = document["flags"][label][h]
            cells.append(f"{c['flags']}({c['false_alarms']}); {c['onsets_flagged']}/{c['onsets']}; {ann._f(c['false_alarms_per_onset'], 2)}")
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    out.append("\n" + PAIRED_BRIER_HEADER + "\n")
    out.append("| cell | days | difference |")
    out.append("|---|---|---|")
    for cell, c in document["brier"][name]["1"].items():
        out.append(f"| {cell} | {int(c['days'])} | {ann._interval(c['vs_published'])} |")
    return "\n".join(out)


def compare_command(args) -> int:
    """`announcement_dating_rescore.py compare` with this row against its parent."""

    ann.DECLARATION = DECLARATION
    ann.rows_of_pairs = lambda: [("iorb", NEW, PARENT)]
    ann.markdown = markdown
    return ann.compare_command(args)


# -- the announcement days ---------------------------------------------------------------------------------


def days_command(args) -> int:
    """For h = 1 at the judge's cut-offs: the flags the row adds or drops, and each day on which the input is not 0."""

    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    rds.committed_declaration(DECLARATION)
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    scratch = {row.date: row for row in load_daily_panel(args.scratch)}
    splits = load_split_declaration(rds.SPLITS)
    forecasts = fa._load_forecasts(pj, panel_sha256(args.panel), args.inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, fa._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = fa._grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    grid, parent, new = grids[1], by_name[PARENT][1], by_name[NEW][1]
    outcomes, onsets = grid.outcomes[tau], grid.onset_at(tau, tau)
    flag = lambda f, k: f.probabilities[tau][k] >= f.cutoffs[tau][k]
    announced, added, dropped = [], [], []
    for k, day in enumerate(grid.dates):
        value = scratch[day].values.get(ANNOUNCED)
        was, now = flag(parent, k), flag(new, k)
        entry = {
            "date": day.isoformat(),
            "regime": grid.groups["regime"][k],
            "day_type": grid.groups["day_type"][k],
            "pressure_day": bool(outcomes[k]),
            "onset": bool(onsets[k]),
            "parent_flag": bool(was),
            "row_flag": bool(now),
            "parent_probability": parent.probabilities[tau][k],
            "row_probability": new.probabilities[tau][k],
        }
        if value:
            announced.append(dict(entry, announced_change_bps=value))
        if now and not was:
            added.append(entry)
        if was and not now:
            dropped.append(entry)

    def tally(items):
        return {
            "flags": len(items),
            "false_alarms": sum(1 for e in items if not e["pressure_day"]),
            "onsets": sum(1 for e in items if e["onset"]),
        }

    other = [e for e in added if e["date"] not in {a["date"] for a in announced}]
    document = {
        "rule": args.rule,
        "tau_bp": tau,
        "horizon": 1,
        "scored_days": len(grid.dates),
        "announcement_days": announced,
        "added_flags": tally(added),
        "added_flags_on_announcement_days": tally([e for e in added if e not in other]),
        "added_flags_on_other_days": tally(other),
        "dropped_flags": tally(dropped),
        "added_flag_days": added,
        "dropped_flag_days": dropped,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in document.items() if not k.endswith("_days") and k != "announcement_days"}, indent=1))
    return 0


def summary_rows(judged: dict) -> list:
    """The judge's tier 1 (pooled over leads 1 to 5, and leads 3 to 5), tier 3 and tier 5 rows for the parent and the new row, per rule."""

    yes = lambda x: "yes" if x else "no"
    lines = [
        "| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], worst false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%] | tier 3 | tier 5 | passes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name in (PARENT, NEW):
        for rule, candidates in judged.items():
            entry = candidates[name]
            tier, late = entry["tiers"]["onset_warning"]["lead_at_least_1"], entry["tiers"]["onset_warning"]["lead_at_least_3"]
            key = "worst_weighted_false_alarms_per_onset" if rule == "weighted" else "worst_false_alarms_per_onset"
            worst = tier.get(key, tier["worst_false_alarms_per_onset"])
            cell = lambda t: f"{t['onsets_flagged']:g} of {t['onsets']} , {t['recall']['mean']:.3f} [{t['recall']['interval']['lower']:.3f}, {t['recall']['interval']['upper']:.3f}]"
            verdict = entry["verdict"]
            lines.append(
                f"| {name} | {rule} | {cell(tier)} , {worst:.2f} | {yes(verdict['tier_1_onset_warning'])} | {cell(late)} | {yes(verdict['tier_3_no_crying_wolf'])} | "
                f"{yes(verdict['tier_5_week_ahead'])} | {yes(verdict['passes'])} |"
            )
    return lines


def summary_command(args) -> int:
    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    text = "\n".join(summary_rows(judged)) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--end", help="last scored day, ISO; default the committed declaration's own (at most 2026-09-03, #684: a scratch scored span, no published declaration moves)")
    run.add_argument("--parent", type=Path, required=True, help="announcement_dating_rescore.py run --arm both output at this horizon")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    compare = sub.add_parser("compare")
    compare.add_argument("--rule", choices=("unweighted", "weighted"), default="unweighted")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(func=compare_command)
    days = sub.add_parser("days")
    days.add_argument("--rule", choices=("unweighted", "weighted"), default="unweighted")
    days.add_argument("--panel", type=Path, required=True)
    days.add_argument("--scratch", type=Path, required=True)
    days.add_argument("--output", type=Path, required=True)
    days.add_argument("inputs", nargs="+", type=Path)
    days.set_defaults(func=days_command)
    summary = sub.add_parser("summary")
    summary.add_argument("--flat", type=Path, required=True)
    summary.add_argument("--weighted", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    summary.set_defaults(func=summary_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
