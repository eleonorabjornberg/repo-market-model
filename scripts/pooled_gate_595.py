"""Where the best row's pooled false alarms come from, and three declared gates on its every-day part (#595).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
The row is `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582). Under the judge in force since #550 tier 1 counts a
false alarm once however many leads flag it, and the row fails the limit of 2 on that pooled count. `diagnose` lists the
pooled false-alarm days by lead, year and source (a risk date, the every-day part, or a day on which the IORB input is not 0).
`run` scores the variants declared in `metadata/pooled_gate_595.json`, which this script refuses to read unless it is committed
and unchanged. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`;
`require_unlocked`).

    # AUG2.csv is the scratch panel of risk_date_severity.py (pressure_v1_1.py panel, then measurement_fields.py panel)
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model risk_gbm --panel AUG2.csv \\
        --published PUBLISHED.csv --horizon H --output OUT/both_hH.json
    PYTHONPATH=src python3 scripts/iorb_every_day_579.py run --panel AUG2.csv --published PUBLISHED.csv --horizon H \\
        --parent OUT/both_hH.json --output OUT/iorb_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/pooled_gate_595.py diagnose --rule weighted --panel PUBLISHED.csv --scratch AUG2.csv \\
        --output OUT/diagnosis_weighted.json --markdown OUT/diagnosis_weighted.md OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import contextlib
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, ml  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "pooled_gate_595.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
MODEL = "risk_gbm"
ARM = "both"
PARENT = "risk_gbm+every_day+gate+settle+h41"
ROW = PARENT + "+iorb"
ANNOUNCED = "iorb_announced_change_bps"
TAIL = "sofr_p99_iorb_bps"
LEADS = (1, 2, 3, 4, 5)
#: the horizons at which the announced IORB change is public (one panel day ahead)
READ_AT = (1,)
#: (a) one gate across leads, (b) a stricter gate, (c) the every-day part on the tail signal alone
VARIANTS = {
    "leadgate": ROW + "+leadgate",
    "gate95": ROW + "+gate95",
    "tail": ROW + "+tail",
}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
fa = _load("risk_date_false_alarm_controls")
ann = _load("announcement_dating_rescore")

#: the gate of #532 as the parent serves it, and the one stricter value of variant (b)
GATE = dict(fa.CONTROLS["gate"])
STRICT_GATE = dict(GATE, quantile=0.95)


def judged_forecasts(pj, declaration, rows, splits, panel, inputs):
    """The forecasts with the judge's flag cut-offs chosen (`pressure_judge.choose_cutoffs`), and the grid of each lead."""

    pj_script = _load("pressure_judge")
    forecasts = fa._load_forecasts(pj, panel_sha256(panel), inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, fa._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = fa._grids(pj, declaration, rows, splits, states, chosen)
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    return by_name, grids, calendar


# -- the declaration ---------------------------------------------------------------------------------------


def tail_inputs(horizon: int) -> tuple:
    """Variant (c)'s every-day inputs: the spread (a direct pressure model always reads the latest public spread), the tail signal,
    and the announced IORB change where it is public."""

    return ("spread_bps", TAIL, ANNOUNCED) if horizon in READ_AT else ("spread_bps", TAIL)


def row_inputs(horizon: int) -> tuple:
    """The row's every-day inputs: the parent's, and the announced IORB change where it is public (#579)."""

    return ml.EVERY_DAY_COMPONENT_INPUTS + (ANNOUNCED,) if horizon in READ_AT else ml.EVERY_DAY_COMPONENT_INPUTS


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #595 before any variant was scored; a measurement, not a record. Nothing here is "
            "published: no variant joins any published declaration, no 2026 day is scored, no rule changes and the live record and pin "
            "do not move. The variants were chosen after seeing 2018-2025 (the diagnosis of the row's false alarms), so a pass is not a "
            "confirmation (ruling of 11 October 2026 on #567)"
        ),
        "issue": 595,
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "parent": {
            "row": ROW,
            "declaration": "metadata/iorb_every_day_579.json (PR #582): the risk-date model of metadata/risk_date_severity.json on a risk date; on any other day the ridge logistic of the every-day component, then the gate of #532; settlements dated from the auction announcement, the H.4.1 weeklies read per release; the announced IORB change in the component at h = 1 only",
            "second_parent": "risk_gbm+settle+h41 (the row that passes tier 1 under the pooled count), the pairing reference",
        },
        "gate": dict(GATE, rule="the gate of #532 as the parent serves it (metadata/risk_date_false_alarm_controls.json)"),
        "variants": {
            "leadgate": {
                "name": VARIANTS["leadgate"],
                "issue_text": "(a) one gate across leads: the every-day part may flag a day only if it clears the gate at the day's own nearest lead, so a day's flag is consistent across leads",
                "reading": (
                    "the literal text reads lead 1's forecast of a day when issuing that day's forecast at leads 2 to 5, and lead 1's forecast is issued one panel day "
                    "before the day, after the decision instant of every farther lead: a forecast may not read it (docs/decisions/information-set.md). The variant is "
                    "therefore run in the form no forecast contradicts: on a day that is not a risk date, the forecast at lead h is kept only if the gate was also cleared "
                    "at every farther lead h' > h at which the day is scored (each of those forecasts was issued before the lead-h decision instant); otherwise it is 0. "
                    "A risk date keeps the row's forecast, and so does a day at lead 5. Whether the nearest-lead text was meant otherwise is Eleonora's to say"
                ),
                "fit": "none: a rule on the row's own gated forecasts at the five leads",
                "reads": "the row's forecasts at the same day and at farther leads, each issued before this lead's decision instant, and nothing else",
            },
            "gate95": {
                "name": VARIANTS["gate95"],
                "issue_text": "(b) a stricter declared gate on the every-day part (one value, declared, read from nothing scored)",
                "gate": STRICT_GATE,
                "reading": "the row with the gate's quantile 0.95 in place of 0.9, window and minimum_earlier unchanged; the value is declared here, the next round number above the gate in force, and was not chosen on a score",
                "fit": "the row's fits, unchanged; only the gate changes",
            },
            "tail": {
                "name": VARIANTS["tail"],
                "issue_text": "(c) the every-day part restricted to the signal that warned the onsets it added (the 2019 onsets and 2020-03-04), with the IORB term kept to announced-change days only",
                "reading": (
                    "the diagnosis (docs/pivot/pooled-gate-result.md) lists the onsets the every-day part adds: 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04 and 2020-03-12. "
                    f"What sets them apart from the median day is the SOFR 99th percentile above IORB ({TAIL}), not the 75th percentile. The component is "
                    f"the ridge logistic on spread_bps (a direct pressure model always reads the latest public spread; ml._PressureDesign refuses a design without it) and {TAIL}, "
                    f"and on {ANNOUNCED} where that is public (h = 1); it drops sofr_p75_iorb_bps. The announced change is 0 on every day but an announced-change day, "
                    "so its term acts on those days only. The gate, the risk-date model and the timing arm are the row's"
                ),
                "every_day_inputs": {"h=1": list(tail_inputs(1)), "h>=2": list(tail_inputs(2))},
            },
        },
        "variants_declared": "these three and the row and its parent; no other variant, parent or input",
        "judge": "the judge as in force on main (metadata/pressure_judge.json, unchanged), under the weighted rule in force and the flat rule beside it; the benchmarks and the evaluation days, tiers and onsets do not depend on the row",
        "pairing": "each variant against the row and against risk_gbm+settle+h41, with 90% stationary-bootstrap intervals (the judge's bootstrap), split by regime and pressure-day type and by year",
        "published": "nothing; no variant joins any published declaration",
    }


def candidate_entries() -> dict:
    base = json.loads((CANDIDATES / f"{ROW}.json").read_text(encoding="utf-8"))
    entries = {}
    for key, name in VARIANTS.items():
        entry = dict(base)
        entry["track"] = "#595"
        entry["parent"] = ROW
        calibration = base["calibration"]
        head = calibration.split("; scored under ")[0]
        tail_text = "; scored under settlements dated from the auction announcement (metadata/settlement_announcement_dating.json) and the H.4.1 weeklies read per release (metadata/h41_release_dating.json); metadata/pooled_gate_595.json"
        if key == "leadgate":
            head += "; then on a day that is not a risk date the forecast at lead h is kept only if the gate was also cleared at every farther lead h' > h (a day's flag is consistent across leads, reading only forecasts issued earlier)"
        elif key == "gate95":
            head = head.replace("strictly above the quantile (nearest rank)", "strictly above the 0.95 quantile (nearest rank)")
        else:
            head = head.replace(
                "a ridge logistic on spread_bps, sofr_p75_iorb_bps, sofr_p99_iorb_bps and iorb_announced_change_bps serves",
                "a ridge logistic on spread_bps, sofr_p99_iorb_bps and iorb_announced_change_bps (at h = 1; without it at h >= 2) serves",
            )
            entry["features_at_horizon_2_or_more"] = base["features_at_horizon_2_or_more"].replace(
                "; without iorb_announced_change_bps (read at h = 1 only; the row's forecasts are the parent's)",
                "; the every-day component reads spread_bps and sofr_p99_iorb_bps (iorb_announced_change_bps at h = 1 only), not sofr_p75_iorb_bps; the risk-date model's inputs are the row's",
            )
        entry["calibration"] = head + tail_text
        entries[name] = entry
    return entries


def declare_command(args) -> int:
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    DECLARATION.write_text(json.dumps(declaration_document(parents), indent=2) + "\n", encoding="utf-8")
    written = [str(DECLARATION)]
    for name, entry in candidate_entries().items():
        path = CANDIDATES / f"{name}.json"
        path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))
    print(json.dumps({"written": written}, indent=1))
    return 0


# -- variant (a): one gate across leads -------------------------------------------------------------------


def _read_only_farther(lead: int, read) -> None:
    """The lead-`lead` forecast of a day is issued at that day's decision instant `lead` panel days before it: it may read the
    same day's forecasts at farther leads (issued earlier) and never at nearer ones (issued later)."""

    nearer = sorted(x for x in read if x <= lead)
    if nearer:
        raise LookAheadError(
            f"the forecast at lead {lead} would read the same day's forecast at lead {nearer}, which is issued after its decision instant"
        )


def lead_gate(forecasts: dict, not_risk_date: dict) -> dict:
    """Variant (a): `forecasts[lead][key][day]` with a day that is not a risk date kept at lead h only if every farther lead cleared it.

    `not_risk_date[lead][day]` is True on a day the every-day part serves. A forecast is "cleared" when the gate left it above 0
    (the gate returns 0 for a probability not strictly above its cut). A risk date keeps its forecast, a day at the farthest lead
    reads nothing, and a day not scored at a farther lead is not conditioned on it.
    """

    leads = sorted(forecasts)
    out: dict = {}
    for lead in leads:
        farther = [x for x in leads if x > lead]
        _read_only_farther(lead, farther)
        out[lead] = {}
        for key, by_day in forecasts[lead].items():
            kept = {}
            for day, value in by_day.items():
                if not_risk_date[lead].get(day, False):
                    value = value if all(forecasts[x][key].get(day, 1.0) > 0.0 for x in farther) else 0.0
                kept[day] = value
            out[lead][key] = kept
    for lead in leads:
        keys = sorted(out[lead], key=float)
        for earlier, later in zip(keys, keys[1:]):
            out[lead][later] = {day: min(v, out[lead][earlier][day]) for day, v in out[lead][later].items()}
    return out


def leadgate_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="pooled_gate_595")
    splits = load_split_declaration(rds.SPLITS)
    rows = {row.date: row for row in load_daily_panel(args.scratch)}
    settle, _h41, _suffix = ann.ARMS[ARM]
    documents = {}
    for path in args.inputs:
        document = json.loads(path.read_text(encoding="utf-8"))
        documents[document["horizon"]] = document
    if sorted(documents) != list(LEADS):
        raise SystemExit(f"the row's forecasts are needed at every lead {list(LEADS)}, got {sorted(documents)}")
    digests = {d["panel_sha256"] for d in documents.values()}
    if digests != {panel_sha256(args.published)}:
        raise SystemExit("a forecast file was scored on another panel")
    forecasts = {h: documents[h]["forecasts"][ROW] for h in LEADS}
    not_risk_date = {
        h: {day: not ann.risk_flag(splits, rows[date.fromisoformat(day)].values, settle or h == 1) for day in forecasts[h][next(iter(forecasts[h]))]}
        for h in LEADS
    }
    out = lead_gate(forecasts, not_risk_date)
    for h in LEADS:
        document = {
            "arm": ARM,
            "horizon": h,
            "panel_sha256": documents[h]["panel_sha256"],
            "scratch_panel_sha256": documents[h]["scratch_panel_sha256"],
            "declaration": declared,
            "declarations": {VARIANTS["leadgate"]: {"rule": "lead_gate: the row's forecasts, a day not a risk date kept at lead h only if cleared at every farther lead"}},
            "forecasts": {VARIANTS["leadgate"]: out[h]},
        }
        target = args.output_dir / f"leadgate_h{h}.json"
        target.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"horizon": h, "output": str(target)}))
    return 0


# -- variants (b) and (c): the row's component refitted, the gate applied ------------------------------------


def run_command(args) -> int:
    """The row's every-day component at one lead, gated at the row's quantile and at the stricter one (variant b), or refitted on the tail signal (variant c)."""

    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="pooled_gate_595")
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
    component_inputs = tail_inputs(h) if args.variant == "tail" else row_inputs(h)
    predictor = ml.pressure_risk_date_variant_exceedance(
        spec["kind"], parent_features, splits, minimum, every_day=True, early_prior=False, component_inputs=component_inputs
    )
    features = tuple(dict.fromkeys(parent_features + component_inputs))
    with rds.switched_on(), (h41_release.release_dating() if h41 else contextlib.nullcontext()):
        report = rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=VARIANTS["tail"] if args.variant == "tail" else ROW,
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

    def gated(params):
        out = fa.apply_control("gate", params, raw, off, [None] * len(days))
        return {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}

    if args.variant == "tail":
        forecasts = {VARIANTS["tail"]: gated(GATE)}
    else:
        forecasts = {ROW: gated(GATE), VARIANTS["gate95"]: gated(STRICT_GATE)}
    document = {
        "arm": ARM,
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": {name: fa._settings(report) for name in forecasts},
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "variant": args.variant, "output": str(args.output)}))
    return 0


# -- the diagnosis -----------------------------------------------------------------------------------------


def diagnose(pj, declaration, name, by_name, grids, calendar, scratch, splits):
    """Every day flagged at some lead 1 to 5 that is not a pressure day, with its leads, year, source and weight."""

    tau = declaration.primary
    settle, _h41, _suffix = ann.ARMS["both"]
    leads = [h for h in LEADS if h in declaration.horizons]
    common = sorted(set.intersection(*(set(grids[h].dates) for h in leads)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in leads}
    first = leads[0]
    pressure = [bool(grids[first].outcomes[tau][position[first][day]]) for day in common]
    onset = [bool(grids[first].onset_at(tau, tau)[position[first][day]]) for day in common]
    place = {day: k for k, day in enumerate(calendar)}
    places = [place[day] for day in common]
    weights = list(
        pj.false_alarm_weights(declaration.weighted_miss, positions=places, pressure=[int(p) for p in pressure], known_through=places[-1])
    ) if declaration.weighted_miss is not None else [1.0] * len(common)
    flag = {
        h: [
            by_name[name][h].probabilities[tau][position[h][day]] >= by_name[name][h].cutoffs[tau][position[h][day]]
            for day in common
        ]
        for h in leads
    }
    onsets = sum(onset)
    days = []
    for k, day in enumerate(common):
        flagged = [h for h in leads if flag[h][k]]
        values = scratch[day].values
        risk_by_lead = {h: ann.risk_flag(splits, values, settle or h == 1) for h in leads}
        days.append(
            {
                "date": day.isoformat(),
                "year": day.year,
                "regime": grids[first].groups["regime"][position[first][day]],
                "day_type": grids[first].groups["day_type"][position[first][day]],
                "pressure_day": pressure[k],
                "onset": onset[k],
                "weight": weights[k],
                "flagged_at": flagged,
                "risk_date_at": [h for h in leads if risk_by_lead[h]],
                "iorb_announced_change_bps": values.get(ANNOUNCED) or 0.0,
                "probability": {str(h): by_name[name][h].probabilities[tau][position[h][day]] for h in leads},
            }
        )
    false_alarms = [d for d in days if d["flagged_at"] and not d["pressure_day"]]

    def source(d):
        flagged, risky = set(d["flagged_at"]), set(d["risk_date_at"])
        if flagged <= risky:
            return "risk date at every lead that flags it"
        if not flagged & risky:
            return "every-day part at every lead that flags it"
        return "risk date at some leads, every-day part at others"

    def tally(items):
        return {"days": len(items), "weighted": round(sum(d["weight"] for d in items), 3)}

    by_source = defaultdict(list)
    for d in false_alarms:
        by_source[source(d)].append(d)
    by_year = defaultdict(list)
    for d in false_alarms:
        by_year[d["year"]].append(d)
    by_count = defaultdict(list)
    for d in false_alarms:
        by_count[len(d["flagged_at"])].append(d)
    by_lead = {
        str(h): {"flags": sum(1 for k in range(len(common)) if flag[h][k] and not pressure[k]),
                 "weighted": round(sum(weights[k] for k in range(len(common)) if flag[h][k] and not pressure[k]), 3)}
        for h in leads
    }
    only_one = Counter(d["flagged_at"][0] for d in false_alarms if len(d["flagged_at"]) == 1)
    iorb_days = [d for d in false_alarms if d["iorb_announced_change_bps"]]
    caught = {}
    for d in days:
        if d["onset"] and d["flagged_at"]:
            caught[d["date"]] = {"flagged_at": d["flagged_at"], "risk_date_at": d["risk_date_at"], "iorb": d["iorb_announced_change_bps"]}
    return {
        "row": name,
        "rule": "weighted" if declaration.weighted_miss is not None else "flat",
        "tau_bp": tau,
        "leads": leads,
        "scored_days": len(common),
        "onsets": onsets,
        "onsets_flagged": len(caught),
        "pooled_false_alarms": tally(false_alarms),
        "pooled_false_alarms_per_onset": {
            "flat": len(false_alarms) / onsets,
            "weighted": sum(d["weight"] for d in false_alarms) / onsets,
        },
        "by_lead": by_lead,
        "by_source": {k: tally(v) for k, v in sorted(by_source.items())},
        "by_year": {str(k): tally(v) for k, v in sorted(by_year.items())},
        "by_number_of_leads_flagging": {str(k): tally(v) for k, v in sorted(by_count.items())},
        "flagged_at_one_lead_only": {str(k): v for k, v in sorted(only_one.items())},
        "on_an_iorb_announcement_day": tally(iorb_days),
        "onsets_caught": caught,
        "false_alarm_days": false_alarms,
    }


def markdown(document: dict) -> str:
    out = [f"Diagnosis of `{document['row']}` at +{document['tau_bp']:g} bp, {document['rule']} rule, leads {document['leads'][0]} to {document['leads'][-1]}.\n"]
    pooled = document["pooled_false_alarms"]
    per = document["pooled_false_alarms_per_onset"]
    out.append(
        f"{document['onsets_flagged']} of {document['onsets']} onsets flagged; {pooled['days']} pooled false-alarm days, weighted {pooled['weighted']}; "
        f"per onset {per['flat']:.2f} flat, {per['weighted']:.2f} weighted (limit 2).\n"
    )
    for title, key in (
        ("By source", "by_source"),
        ("By year", "by_year"),
        ("By number of leads that flag the day", "by_number_of_leads_flagging"),
    ):
        out.append(f"{title}.\n")
        out.append("| cell | false-alarm days | weighted |")
        out.append("|---|---|---|")
        for k, v in document[key].items():
            out.append(f"| {k} | {v['days']} | {v['weighted']} |")
        out.append("")
    out.append("By lead alone (a day counted at each lead that flags it).\n")
    out.append("| lead | flags that are false alarms | weighted |")
    out.append("|---|---|---|")
    for h, v in document["by_lead"].items():
        out.append(f"| {h} | {v['flags']} | {v['weighted']} |")
    out.append("")
    out.append(f"Days flagged at one lead only, by the lead: {document['flagged_at_one_lead_only']}.\n")
    out.append(f"On an IORB announcement day: {document['on_an_iorb_announcement_day']}.\n")
    return "\n".join(out)


def diagnose_command(args) -> int:
    from repo_model import pressure_judge as pj

    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    scratch = {row.date: row for row in load_daily_panel(args.scratch)}
    splits = load_split_declaration(rds.SPLITS)
    by_name, grids, calendar = judged_forecasts(pj, declaration, rows, splits, args.panel, args.inputs)
    document = diagnose(pj, declaration, args.row, by_name, grids, calendar, scratch, splits)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    diag = sub.add_parser("diagnose")
    diag.add_argument("--rule", choices=("unweighted", "weighted"), default="weighted")
    diag.add_argument("--row", default=ROW)
    diag.add_argument("--panel", type=Path, required=True)
    diag.add_argument("--scratch", type=Path, required=True)
    diag.add_argument("--output", type=Path, required=True)
    diag.add_argument("--markdown", type=Path)
    diag.add_argument("inputs", nargs="+", type=Path)
    diag.set_defaults(func=diagnose_command)
    sub.add_parser("declare").set_defaults(func=declare_command)
    run = sub.add_parser("run")
    run.add_argument("--variant", choices=("gate", "tail"), required=True, help="gate: the row refitted and gated at 0.9 and 0.95; tail: variant (c)")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    lead = sub.add_parser("leadgate")
    lead.add_argument("--published", type=Path, required=True)
    lead.add_argument("--scratch", type=Path, required=True)
    lead.add_argument("--output-dir", type=Path, required=True)
    lead.add_argument("inputs", nargs="+", type=Path)
    lead.set_defaults(func=leadgate_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
