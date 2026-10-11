"""The five risk-date passers re-scored with settlements dated from the announcement and the H.4.1 read per release (#541).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given, and nothing into `docs/runs/`.
Eleonora's ruling of 10 October 2026 (relayed on #541) is implemented as two measurement declarations, off in every published
declaration (`metadata/settlement_announcement_dating.json`, `metadata/h41_release_dating.json`), and `metadata/announcement_dating.json`
declares this scoring; the script refuses a declaration that is not committed, and `pressure_judge.py` refuses a candidate file that
is not. The scoring window ends 2025-12-31 (`docs/decisions/lockbox.md`; `require_unlocked`).

Arms, each a registry and a set of panel columns, scored at every horizon with the machinery of `risk_date_severity.py` (the parents)
and `risk_date_false_alarm_controls.py` (the `+every_day` variant and its `+gate` control):

* `published`: the published declaration, as #534 scored it (the control of every pairing);
* `settle`: settlements dated from the announcement (`settlement_dating.known_columns`, checked by `check_known_columns`, and
  `result_dated_registry`). The settlement columns stay in the features at every horizon, so the coupon clause of the risk-date rule
  applies at h >= 2;
* `h41`: the H.4.1 weeklies dated by their release (`h41_release.release_dated_registry`);
* `both`.

    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py declare
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm ARM --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/ARM_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule RULE --output OUT/judge_RULE.json OUT/bench_h?.json OUT/*_h?.json
    PYTHONPATH=src python3 scripts/announcement_dating_rescore.py compare --rule RULE --panel PUBLISHED.csv --output OUT/compare_RULE.json --markdown OUT/compare_RULE.md OUT/bench_h?.json OUT/*_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import replace
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, ml, settlement_dating  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "announcement_dating.json"
SETTLE = REPO / "metadata" / "settlement_announcement_dating.json"
H41 = REPO / "metadata" / "h41_release_dating.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
SNAPSHOT = (
    REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions"
    / "20260914T051023Z_722359ea9bc7.json"
)
EPISODES = REPO / "docs" / "pivot" / "evidence" / "episode-post-mortem" / "episodes.json"
GATE = "+every_day+gate"
#: arm -> (settlements dated from the announcement, H.4.1 read per release, suffix of the forecast name)
ARMS = {
    "published": (False, False, ""),
    "settle": (True, False, "+settle"),
    "h41": (False, True, "+h41"),
    "both": (True, True, "+settle+h41"),
}
MODELS = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")
#: The seven coupon-settlement onsets that are not calendar risk dates (docs/pivot/desk-standard-result.md, section 2).
COUPON_ONSETS = ("2018-11-15", "2018-12-28", "2019-01-15", "2019-03-15", "2019-10-15", "2025-10-15", "2025-12-26")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rds = _load("risk_date_severity")
fa = _load("risk_date_false_alarm_controls")


def names(model: str, arm: str) -> tuple:
    """The forecast names of `model` under `arm`: the passer and its `+every_day+gate` row."""

    suffix = ARMS[arm][2]
    return model + suffix, model + GATE + suffix


# -- the declaration ---------------------------------------------------------------------------------------


def declaration_document(parents: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #541 before any score was computed; a measurement, not a record. Nothing here is "
            "published: the settlement and H.4.1 declarations it reads are off in every published declaration, no 2026 day is scored, and "
            "the live record and pin do not move. The rulings are Eleonora's of 10 October 2026, relayed by the orchestrating session on #541"
        ),
        "scoring": parents["scoring"],
        "thresholds_bp": parents["thresholds_bp"],
        "horizons": parents["horizons"],
        "models": {name: parents["candidates"][name] for name in MODELS},
        "models_declaration": "metadata/risk_date_severity.json (unchanged: the risk dates, the features, the estimators); the gate row of each is the 'gate' control of metadata/risk_date_false_alarm_controls.json on the +every_day variant of metadata/risk_date_every_day.json (unchanged)",
        "arms": {
            "published": "the published registry and panel columns: the control of every pairing, re-run here by the same code as the other arms",
            "settle": "metadata/settlement_announcement_dating.json: the settlement columns are those known h panel days ahead from the auction announcements (settlement_dating.known_columns, checked by check_known_columns) and the registry declares them public then (result_dated_registry)",
            "h41": "metadata/h41_release_dating.json: reserve_balances, tga and reserve_scarcity_state's reserve read are dated by the print of their own Wednesday's release (h41_release.release_dated_registry)",
            "both": "both of the above",
        },
        "features": "each model's features as declared, except that under settle and both the settlement columns stay in the features at every horizon (risk_date_severity.SETTLEMENT_COLUMNS are dropped at h >= 2 only under the published arm)",
        "risk_dates": "a scored day whose pressure-day type is not ordinary, or whose treasury_settlement_coupons, as known at the horizon, is positive: at h = 1 under every arm, and at h >= 2 under settle and both (the coupon clause the announcement makes known); the published arm's rule is unchanged",
        "judge": "the judge as declared (metadata/pressure_judge.json), unchanged, under the flat and the weighted rule; the benchmarks and the evaluation days, tiers and onsets do not depend on an arm",
        "pairing": "each arm's model against the same model under the published arm, with 90% stationary-bootstrap intervals (the judge's bootstrap), split by regime and pressure-day type and by year",
        "published": "nothing; no rule, threshold, definition or availability time changes in a published declaration",
    }


def declare_command(args) -> int:
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    document = declaration_document(parents)
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    made = 0
    for model in MODELS:
        for arm, (settle, h41, suffix) in ARMS.items():
            if arm == "published":
                continue
            for published, label in ((model, "the risk-date model"), (model + GATE, "the every-day variant with the gate control")):
                base = json.loads((CANDIDATES / f"{published}.json").read_text(encoding="utf-8"))
                entry = dict(base)
                entry["track"] = "G (#541)"
                entry["parent"] = published
                dating = []
                if settle:
                    dating.append("settlements dated from the auction announcement (metadata/settlement_announcement_dating.json), the settlement columns kept at every horizon and the coupon clause of the risk-date rule applied at h >= 2")
                if h41:
                    dating.append("the H.4.1 weeklies read per release (metadata/h41_release_dating.json)")
                entry["features_at_horizon_2_or_more"] = (
                    "with treasury_settlement and treasury_settlement_coupons" if settle else base.get("features_at_horizon_2_or_more", "")
                )
                entry["calibration"] = base["calibration"].split("; metadata/")[0] + "; scored under " + " and ".join(dating) + "; metadata/announcement_dating.json"
                (CANDIDATES / f"{published}{suffix}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
                made += 1
    print(json.dumps({"declaration": str(DECLARATION), "candidates": made}))
    return 0


# -- run ---------------------------------------------------------------------------------------------------


def arm_inputs(arm: str, rows, registry, horizon: int):
    """`rows` and `registry` as `arm` reads them at `horizon`, checked."""

    settle, h41, _suffix = ARMS[arm]
    registry = dict(registry)
    if settle:
        declaration = settlement_dating.load_result_dating(SETTLE)
        results = settlement_dating.load_snapshot_results(SNAPSHOT, declaration)
        rows = settlement_dating.known_columns(rows, results, horizon, declaration)
        settlement_dating.check_known_columns(rows, results, horizon, declaration)
        registry = settlement_dating.result_dated_registry(registry, declaration, horizon)
    if h41:
        registry = h41_release.release_dated_registry(registry, h41_release.load_release_dating(H41))
    return rows, registry


def features_for(declared: dict, spec: dict, horizon: int, settle: bool) -> tuple:
    names_ = [name for group in spec["inputs"] for name in declared["features"][group]]
    return tuple(name for name in names_ if settle or horizon == 1 or name not in rds.SETTLEMENT_COLUMNS)


def risk_flag(splits, values, coupon_clause: bool) -> bool:
    """The risk-date rule as the model serves it (`ml._RiskDateDesign.member`)."""

    if splits.day_type(values) != "ordinary":
        return True
    return coupon_clause and float(values.get(rds.COUPONS) or 0.0) > 0.0


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    h, arm = args.horizon, args.arm
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    settle, _h41, suffix = ARMS[arm]
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="announcement_dating_rescore")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    registry = measurement_fields.load_registry()
    rows, registry = arm_inputs(arm, rows, registry, h)
    by_date = {row.date: row for row in rows}
    splits = load_split_declaration(rds.SPLITS)
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    coupon_clause = settle or h == 1
    chosen = [args.model] if args.model else list(declared["models"])
    forecasts, settings = {}, {}
    for model in chosen:
        spec = declared["models"][model]
        parent_features = features_for(parents, spec, h, settle)
        for variant, (every_day, features) in {
            "parent": (False, parent_features),
            "every_day": (True, tuple(dict.fromkeys(parent_features + ml.EVERY_DAY_COMPONENT_INPUTS))),
        }.items():
            if every_day:
                predictor = ml.pressure_risk_date_variant_exceedance(
                    spec["kind"], parent_features, splits, minimum, every_day=True, early_prior=False
                )
            else:
                predictor = ml.pressure_risk_date_exceedance(spec["kind"], features, splits, minimum_history=minimum)
            with rds.switched_on():
                report = rolling_exceedance_backtest(
                    rows,
                    predictor=predictor,
                    model_name=model + suffix + ("+every_day" if every_day else ""),
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
            if not every_day:
                forecasts[model + suffix] = column
                settings[model + suffix] = fa._settings(report)
                continue
            keys = [f"{tau:g}" for tau in taus]
            days = sorted(column[keys[0]])
            raw = [[column[key][day] for day in days] for key in keys]
            off = [not risk_flag(splits, by_date[date.fromisoformat(day)].values, coupon_clause) for day in days]
            out = fa.apply_control("gate", fa.CONTROLS["gate"], raw, off, [None] * len(days))
            forecasts[model + GATE + suffix] = {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}
            settings[model + GATE + suffix] = fa._settings(report)
        print(json.dumps({"arm": arm, "horizon": h, "model": model, "done": True}), flush=True)
    document = {
        "arm": arm,
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"arm": arm, "horizon": h, "output": str(args.output)}))
    return 0


# -- compare ----------------------------------------------------------------------------------------------


def _f(value, places=3):
    return "-" if value is None else f"{value:.{places}f}"


def _interval(cell):
    if cell is None or cell.get("mean") is None:
        return "-"
    if "interval" not in cell:
        return f"{cell['mean']:+.4f} (no interval)"
    return f"{cell['mean']:+.4f} [{cell['interval']['lower']:+.4f}, {cell['interval']['upper']:+.4f}]"


def rows_of_pairs() -> list:
    """Every (arm, model row, its published counterpart): the passers and their gate rows."""

    out = []
    for model in MODELS:
        for published in (model, model + GATE):
            for arm in ("settle", "h41", "both"):
                suffix = ARMS[arm][2]
                out.append((arm, published + suffix, published))
    return out


def compare_command(args) -> int:
    from repo_model import pressure_judge as pj

    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    by_date = {row.date: row for row in rows}
    forecasts = fa._load_forecasts(pj, panel_sha256(args.panel), args.inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, fa._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = fa._grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    pairs = rows_of_pairs()
    wanted = {name for _a, name, _ref in pairs} | {ref for _a, _n, ref in pairs} | {declaration.climatology, declaration.persistence}
    for name in sorted(wanted):
        if name not in by_name:
            raise SystemExit(f"no forecasts for {name!r} in the inputs")
    horizons = list(declaration.horizons)
    seed = declaration.document()["bootstrap"]["seed"]
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    place = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    onset = [float(grids[1].onset[place[1][day]]) for day in common]
    count = len(common)

    def flagged_at(name, h, day):
        f = by_name[name][h]
        k = place[h][day]
        return f.probabilities[tau][k] >= f.cutoffs[tau][k]

    def caught(name):
        return [
            (1.0 if any(flagged_at(name, h, day) for h in horizons) else 0.0) * onset[i]
            for i, day in enumerate(common)
        ]

    caught_by = {name: caught(name) for name in wanted}
    years = sorted({day.year for day in common})
    regimes = [grids[1].groups["regime"][place[1][day]] for day in common]
    kinds = [grids[1].groups["day_type"][place[1][day]] for day in common]
    cells_for = {
        "all": [1.0] * count,
        **{f"year {y}": [1.0 if day.year == y else 0.0 for day in common] for y in years},
        **{f"regime {r}": [1.0 if x == r else 0.0 for x in regimes] for r in sorted(set(regimes))},
        **{f"day type {t}": [1.0 if x == t else 0.0 for x in kinds] for t in sorted(set(kinds))},
    }
    recall_stats = {
        "recall": pj._ratio(1, 0),
        "reference_recall": pj._ratio(2, 0),
        "recall_difference": lambda t: (t[1] - t[2]) / t[0] if t[0] else None,
    }
    recall = {}
    for arm, name, ref in pairs:
        cells = {
            cell: [
                [m * o for m, o in zip(inside, onset)],
                [m * c for m, c in zip(inside, caught_by[name])],
                [m * c for m, c in zip(inside, caught_by[ref])],
            ]
            for cell, inside in cells_for.items()
        }
        recall[name] = pj._bootstrap(declaration, cells, recall_stats, count, seed=pj._seed(seed, "recall", name, ref))
    caught_count = {
        name: {cell: int(sum(m * c for m, c in zip(inside, caught_by[name]))) for cell, inside in cells_for.items()}
        for name in wanted
    }
    onsets_in = {cell: int(sum(m * o for m, o in zip(inside, onset))) for cell, inside in cells_for.items()}

    flags = {}
    for name in sorted(wanted):
        flags[name] = {}
        for h in horizons:
            grid = by_name[name][h], grids[h]
            f, g = grid
            raised = [1 if q >= c else 0 for q, c in zip(f.probabilities[tau], f.cutoffs[tau])]
            outcomes, onsets = g.outcomes[tau], g.onset_at(tau, tau)
            n_onsets = sum(onsets)
            flagged = [k for k, r in enumerate(raised) if r]
            flags[name][str(h)] = {
                "onsets": n_onsets,
                "flags": len(flagged),
                "false_alarms": sum(1 for k in flagged if not outcomes[k]),
                "onsets_flagged": sum(1 for k in flagged if onsets[k]),
                "false_alarms_per_onset": sum(1 for k in flagged if not outcomes[k]) / n_onsets if n_onsets else None,
            }

    brier = {}
    for arm, name, ref in pairs:
        brier[name] = {}
        for h in horizons:
            g = grids[h]
            outcomes = g.outcomes[tau]
            n = len(outcomes)
            groups = {"all": list(range(n))}
            for dimension in ("regime", "day_type"):
                for label in sorted(set(g.groups[dimension])):
                    groups[f"{dimension} {label}"] = [k for k, x in enumerate(g.groups[dimension]) if x == label]
            p = by_name[name][h].probabilities[tau]
            ref_p = by_name[ref][h].probabilities[tau]
            pers = by_name[declaration.persistence][h].probabilities[tau]
            cells = {grp: pj._paired_vectors(p, ref_p, pers, outcomes, members) for grp, members in groups.items()}
            result = pj._bootstrap(declaration, cells, pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h, ref))
            brier[name][str(h)] = {
                grp: {"days": result[grp]["days"], "vs_published": result[grp]["brier_difference_vs_climatology"]}
                for grp in groups
            }

    onset_days = {day for i, day in enumerate(common) if onset[i]}
    coupon = {}
    for name in sorted(wanted - {declaration.climatology, declaration.persistence}):
        coupon[name] = {}
        for day in COUPON_ONSETS:
            when = date.fromisoformat(day)
            coupon[name][day] = {
                "is_onset": when in onset_days,
                "leads_flagged": [h for h in horizons if when in place[h] and flagged_at(name, h, when)],
            }
    post_mortem = json.loads(EPISODES.read_text(encoding="utf-8"))["episodes"]
    index = {day.isoformat(): i for i, day in enumerate(common)}
    episodes = [
        {
            "start": episode["start"],
            "regime": episode["regime"],
            "day_type": episode["day_type"],
            **{name: bool(caught_by[name][index[episode["start"]]]) for name in sorted(wanted - {declaration.climatology, declaration.persistence})},
        }
        for episode in post_mortem
        if episode["start"] in index
    ]
    document = {
        "declaration": declared,
        "rule": args.rule,
        "onsets": int(sum(onset)),
        "onsets_in_cell": onsets_in,
        "caught_at_some_lead": caught_count,
        "recall_at_some_lead": recall,
        "flags": flags,
        "brier": brier,
        "coupon_onsets": coupon,
        "episodes": episodes,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document, pairs)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict, pairs) -> str:
    out = []
    arms = ("settle", "h41", "both")
    rows = []
    for model in MODELS:
        rows += [model, model + GATE]
    out.append("Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the published row and each arm.\n")
    for published in rows:
        group = [published] + [published + ARMS[a][2] for a in arms]
        out.append(f"\n{published}\n")
        out.append("| cell | onsets | published | " + " | ".join(a for a in arms) + " |")
        out.append("|---|---|---|" + "---|" * len(arms))
        for cell, n_onsets in document["onsets_in_cell"].items():
            out.append(f"| {cell} | {n_onsets} | " + " | ".join(str(document["caught_at_some_lead"][n][cell]) for n in group) + " |")
    out.append("\nTable 2. Recall difference against the published row, by cell (90% interval).\n")
    for published in rows:
        group = [published + ARMS[a][2] for a in arms]
        out.append(f"\n{published}\n")
        out.append("| cell | " + " | ".join(arms) + " |")
        out.append("|---|" + "---|" * len(arms))
        for cell in document["onsets_in_cell"]:
            out.append(f"| {cell} | " + " | ".join(_interval(document["recall_at_some_lead"][n][cell]["recall_difference"]) for n in group) + " |")
    out.append("\nTable 3. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.\n")
    out.append("| row | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for published in rows:
        for name in [published] + [published + ARMS[a][2] for a in arms]:
            cells = []
            for h in ("1", "2", "3", "4", "5"):
                c = document["flags"][name][h]
                cells.append(f"{c['flags']}({c['false_alarms']}); {c['onsets_flagged']}/{c['onsets']}; {_f(c['false_alarms_per_onset'], 2)}")
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nTable 4. The seven coupon-settlement onsets of docs/pivot/desk-standard-result.md section 2 that are not calendar risk dates: the leads at which each row flags (judge's cut-offs), `-` if none.\n")
    out.append("| row | " + " | ".join(COUPON_ONSETS) + " |")
    out.append("|---|" + "---|" * len(COUPON_ONSETS))
    for published in rows:
        for name in [published] + [published + ARMS[a][2] for a in arms]:
            cells = []
            for day in COUPON_ONSETS:
                c = document["coupon_onsets"][name][day]
                cells.append(("h " + ",".join(str(h) for h in c["leads_flagged"])) if c["leads_flagged"] else "-")
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nTable 5. Paired Brier difference against the published row, +5 bp (negative favours the arm), 90% interval, by horizon: all days and by pressure-day type.\n")
    for h in ("1", "2", "3", "4", "5"):
        out.append(f"\nh = {h}\n")
        out.append("| row | cell | days | difference |")
        out.append("|---|---|---|---|")
        for _arm, name, _ref in pairs:
            for cell, c in document["brier"][name][h].items():
                if cell == "all" or cell.startswith("day type"):
                    out.append(f"| {name} | {cell} | {int(c['days'])} | {_interval(c['vs_published'])} |")
    return "\n".join(out)


def summary_command(args) -> int:
    """The judge's tier 1 row at +5 bp for every published and arm row, under each rule."""

    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    lines = [
        "| row | onsets flagged, flat / weighted | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    yes = lambda x: "yes" if x else "no"
    for model in MODELS:
        for published in (model, model + GATE):
            for arm in ARMS:
                name = published + ARMS[arm][2]
                cells = {}
                for rule, candidates in judged.items():
                    entry = candidates[name]
                    tier = entry["tiers"]["onset_warning"]["lead_at_least_1"]
                    verdict = entry["verdict"]
                    cells[rule] = {
                        "flagged": tier["onsets_flagged"], "onsets": tier["onsets"], "recall": tier["recall"],
                        "flat": tier["worst_false_alarms_per_onset"], "weighted": tier.get("worst_weighted_false_alarms_per_onset"),
                        "tiers": " / ".join(yes(verdict[k]) for k in ("tier_1_onset_warning", "tier_3_no_crying_wolf", "tier_5_week_ahead")),
                        "passes": verdict["passes"],
                    }
                f, w = cells["flat"], cells["weighted"]
                ci = lambda c: f"{c['recall']['mean']:.3f} [{c['recall']['interval']['lower']:.3f}, {c['recall']['interval']['upper']:.3f}]"
                lines.append(
                    f"| {name} | {f['flagged']:g}/{f['onsets']} / {w['flagged']:g}/{w['onsets']} | {ci(f)} | {ci(w)} | {f['flat']:.2f} | "
                    f"{_f(w['weighted'], 2)} | {f['tiers']} | {w['tiers']} | {yes(f['passes'])} / {yes(w['passes'])} |"
                )
    text = "\n".join(lines) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    run = sub.add_parser("run")
    run.add_argument("--arm", choices=list(ARMS), required=True)
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--model", default=None)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    compare = sub.add_parser("compare")
    compare.add_argument("--rule", choices=("unweighted", "weighted"), default="unweighted")
    compare.add_argument("--panel", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--markdown", type=Path)
    compare.add_argument("inputs", nargs="+", type=Path)
    compare.set_defaults(func=compare_command)
    summary = sub.add_parser("summary")
    summary.add_argument("--flat", type=Path, required=True)
    summary.add_argument("--weighted", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    summary.set_defaults(func=summary_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
