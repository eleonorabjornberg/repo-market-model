"""The hurdle variants of #539 re-scored with settlements dated from the announcement and the H.4.1 read per release (#556).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given, and nothing into `docs/runs/`.
Eleonora's ruling of 10 October 2026 (relayed on #541) is implemented as two measurement declarations, off in every published
declaration (`metadata/settlement_announcement_dating.json`, `metadata/h41_release_dating.json`; #541), and
`metadata/hurdle_dating.json` declares this scoring; the script refuses a declaration that is not committed, and
`pressure_judge.py` refuses a candidate file that is not. The scoring window ends 2025-12-31 (`docs/decisions/lockbox.md`;
`require_unlocked`).

The arms are those of `announcement_dating_rescore.py` (`published`, `settle`, `h41`, `both`); the rows are the twenty hurdle
variants of `metadata/risk_date_hurdle.json` (five parents x four variants), run by the machinery of `risk_date_hurdle.py`
with the arm's panel columns and registry. A risk date keeps the parent's forecast exactly and any other day is served the
every-day hazard, so an arm moves a variant in three ways and no more: the parent's own inputs (settlements, reserves) on a
risk date; which days are risk dates (the coupon clause applies at h >= 2 under `settle` and `both`); and the reserve scarcity
state, the hazard's input in the `state` variants (`h41`, `both`). `compare` shows where each arm differs from the published
row, day by day, so the claim is read off the scores and not assumed.

    PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py declare      # once, before any score
    PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py run --arm ARM --panel AUG2.csv --published PUBLISHED.csv --horizon H --output OUT/hd_ARM_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule RULE --output OUT/judge_RULE.json OUT/bench_h?.json OUT/hd_*_h?.json
    PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py compare --rule RULE --panel PUBLISHED.csv --output OUT/compare_RULE.json --markdown OUT/compare_RULE.md OUT/bench_h?.json OUT/hd_*_h?.json
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
from repo_model.lockbox import require_unlocked  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adr = _load("announcement_dating_rescore")
rdh = _load("risk_date_hurdle")
rds = rdh.rds

DECLARATION = REPO / "metadata" / "hurdle_dating.json"
HURDLE = REPO / "metadata" / "risk_date_hurdle.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
ARMS = adr.ARMS
COUPON_ONSETS = adr.COUPON_ONSETS
VARIANTS = rdh.VARIANTS
PARENT_NAMES = rdh.PARENT_NAMES
#: probabilities closer than this are the same forecast
SAME = 1e-9


def name_of(parent: str, variant: str, arm: str) -> str:
    """The forecast name of `parent` + `variant` under `arm`."""

    return parent + variant + ARMS[arm][2]


def rows_of_pairs() -> list:
    """Every (arm, arm row, its published row): the twenty variants under the three dating arms."""

    return [
        (arm, name_of(parent, variant, arm), name_of(parent, variant, "published"))
        for parent in PARENT_NAMES
        for variant in VARIANTS
        for arm in ("settle", "h41", "both")
    ]


# -- the declaration --------------------------------------------------------------------------------------


def declaration_document(hurdle: dict) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #556 before any score was computed; a measurement, not a record. Nothing here is "
            "published: the settlement and H.4.1 declarations it reads are off in every published declaration, no 2026 day is scored, and "
            "the live record and pin do not move. The rulings are Eleonora's of 10 October 2026, relayed by the orchestrating session on #541"
        ),
        "scoring": hurdle["scoring"],
        "thresholds_bp": hurdle["thresholds_bp"],
        "horizons": hurdle["horizons"],
        "parents": hurdle["parents"],
        "variants": hurdle["variants"],
        "declaration_of_the_variants": "metadata/risk_date_hurdle.json (unchanged: the hazard, its inputs and the walk-forward calibration), which reads metadata/risk_date_severity.json for the parents (unchanged)",
        "arms": {
            "published": "the published registry and panel columns: re-run here by the same code as the other arms, because #539's evidence keeps the pairing tables and not the forecasts; the control of every pairing",
            "settle": "metadata/settlement_announcement_dating.json (#541): the settlement columns are those known h panel days ahead from the auction announcements and the registry declares them public then; the settlement columns stay in the parent's features at every horizon, so the coupon clause of the risk-date rule applies at h >= 2",
            "h41": "metadata/h41_release_dating.json (#541): reserve_balances, tga and the reserve read of reserve_scarcity_state are dated by the print of their own Wednesday's release",
            "both": "both of the above",
        },
        "what_an_arm_changes": (
            "the parent's forecast on a risk date (its inputs: settlements under settle and both, reserves under h41 and both), the set of risk "
            "days (the coupon clause at h >= 2 under settle and both; a coupon-settlement day moves from the hazard to the parent), and the "
            "reserve scarcity state, the hazard's input in the two state variants (h41 and both). The hazard of the two plain variants reads "
            "the spread and SOFR's percentiles, which neither dating moves. compare reports the days on which each arm's forecast differs "
            "from the published row, split by whether the day is a risk day under either reading"
        ),
        "judge": "the judge as declared (metadata/pressure_judge.json), unchanged, under the flat and the weighted rule; the benchmarks and the evaluation days, tiers and onsets do not depend on an arm",
        "pairing": "each arm's variant against the same variant under the published arm, with 90% stationary-bootstrap intervals (the judge's bootstrap), split by regime and pressure-day type and by year; the Brier score and the log loss (probability floor 1e-6)",
        "published": "nothing; no rule, threshold, definition or availability time changes in a published declaration",
    }


def declare_command(args) -> int:
    hurdle = json.loads(HURDLE.read_text(encoding="utf-8"))
    DECLARATION.write_text(json.dumps(declaration_document(hurdle), indent=2) + "\n", encoding="utf-8")
    made = 0
    for parent in PARENT_NAMES:
        for variant in VARIANTS:
            published = parent + variant
            base = json.loads((CANDIDATES / f"{published}.json").read_text(encoding="utf-8"))
            for arm, (settle, h41, suffix) in ARMS.items():
                if arm == "published":
                    continue
                entry = dict(base)
                entry["track"] = "G (#556)"
                entry["parent"] = published
                dating = []
                if settle:
                    dating.append("settlements dated from the auction announcement (metadata/settlement_announcement_dating.json), the settlement columns kept in the parent's features at every horizon and the coupon clause of the risk-date rule applied at h >= 2")
                if h41:
                    dating.append("the H.4.1 weeklies read per release (metadata/h41_release_dating.json)")
                if settle:
                    entry["features_at_horizon_2_or_more"] = "with treasury_settlement and treasury_settlement_coupons"
                entry["calibration"] = base["calibration"].split("; metadata/")[0] + "; scored under " + " and ".join(dating) + "; metadata/hurdle_dating.json"
                (CANDIDATES / f"{published}{suffix}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
                made += 1
    print(json.dumps({"declaration": str(DECLARATION), "candidates": made}))
    return 0


# -- run ---------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(rdh.PARENTS.read_text(encoding="utf-8"))
    h, arm = args.horizon, args.arm
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    settle, h41, _suffix = ARMS[arm]
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="hurdle_dating_rescore")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    registry = measurement_fields.load_registry()
    rows, registry = adr.arm_inputs(arm, rows, registry, h)
    splits = load_split_declaration(rds.SPLITS)
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    coupon_clause = settle or h == 1
    chosen = [args.candidate] if args.candidate else list(declared["parents"])
    forecasts, settings = {}, {}
    for parent in chosen:
        spec = declared["parents"][parent]
        parent_features = adr.features_for(parents, spec, h, settle)
        parent_predictor = rdh.shared(ml.pressure_risk_date_exceedance(spec["kind"], parent_features, splits, minimum))
        for variant in VARIANTS:
            inputs = declared["variants"][variant]["inputs"]
            features = tuple(dict.fromkeys(parent_features + tuple(inputs)))
            predictor = ml.pressure_risk_date_hurdle_exceedance(
                spec["kind"], parent_features, splits, minimum, variant=variant, parent_predictor=parent_predictor
            )
            with rds.switched_on(), (h41_release.release_dating() if h41 else contextlib.nullcontext()):
                report = rolling_exceedance_backtest(
                    rows,
                    predictor=predictor,
                    model_name=name_of(parent, variant, arm),
                    features=features,
                    registry=registry,
                    decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                    taus=taus,
                    minimum_history=minimum,
                    refit_every=declared["scoring"]["refit_every"],
                    end=last,
                    horizon=h,
                )
            forecasts[name_of(parent, variant, arm)] = rds.column(report)
            settings[name_of(parent, variant, arm)] = rdh._settings(report)
            print(json.dumps({"arm": arm, "horizon": h, "parent": parent, "variant": variant, "done": True}), flush=True)
    risk_days = [
        row.date.isoformat() for row in rows if row.date <= last and adr.risk_flag(splits, row.values, coupon_clause)
    ]
    document = {
        "arm": arm,
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "risk_days": risk_days,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"arm": arm, "horizon": h, "output": str(args.output)}))
    return 0


# -- compare ----------------------------------------------------------------------------------------------

_f, _interval = adr._f, adr._interval


def risk_days_by_arm(inputs) -> dict:
    """{(arm, horizon): set of ISO dates the arm treats as risk days}, from the run documents among `inputs`."""

    out = {}
    for path in inputs:
        document = json.loads(Path(path).read_text())
        if "risk_days" in document:
            out[(document["arm"], int(document["horizon"]))] = set(document["risk_days"])
    return out


def compare_command(args) -> int:
    from repo_model import pressure_judge as pj
    from repo_model import probability_calibration

    pj_script = _load("pressure_judge")
    declared = rds.committed_declaration(DECLARATION)
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=(args.rule == "weighted")))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(rds.SPLITS)
    forecasts = rdh._load_forecasts(pj, panel_sha256(args.panel), args.inputs)
    risk_days = risk_days_by_arm(args.inputs)
    states = {h: pj_script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}
    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, rdh._grids(pj, declaration, rows, splits, states, forecasts), forecasts, calendar)
    grids = rdh._grids(pj, declaration, rows, splits, states, chosen)
    tau = declaration.primary
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    pairs = rows_of_pairs()
    published_rows = sorted({ref for _a, _n, ref in pairs})
    arm_rows = sorted({name for _a, name, _ref in pairs})
    wanted = set(published_rows) | set(arm_rows) | {declaration.climatology, declaration.persistence}
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

    caught_by = {
        name: [(1.0 if any(flagged_at(name, h, day) for h in horizons) else 0.0) * onset[i] for i, day in enumerate(common)]
        for name in wanted - {declaration.climatology, declaration.persistence}
    }
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
    for _arm, name, ref in pairs:
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
        for name in caught_by
    }
    onsets_in = {cell: int(sum(m * o for m, o in zip(inside, onset))) for cell, inside in cells_for.items()}

    flags = {}
    for name in sorted(caught_by):
        flags[name] = {}
        for h in horizons:
            f, g = by_name[name][h], grids[h]
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

    floor = probability_calibration.PROBABILITY_FLOOR
    brier, log_loss, differ = {}, {}, {}
    for _arm, name, ref in pairs:
        brier[name], log_loss[name], differ[name] = {}, {}, {}
        for h in horizons:
            g = grids[h]
            outcomes = g.outcomes[tau]
            n = len(outcomes)
            groups = {"all": list(range(n))}
            for dimension in ("regime", "day_type"):
                for label in sorted(set(g.groups[dimension])):
                    groups[f"{dimension} {label}"] = [k for k, x in enumerate(g.groups[dimension]) if x == label]
            years_of = [day.year for day in g.dates]
            for year in sorted(set(years_of)):
                groups[f"year {year}"] = [k for k, y in enumerate(years_of) if y == year]
            p = by_name[name][h].probabilities[tau]
            ref_p = by_name[ref][h].probabilities[tau]
            pers = by_name[declaration.persistence][h].probabilities[tau]
            result = pj._bootstrap(
                declaration,
                {grp: pj._paired_vectors(p, ref_p, pers, outcomes, members) for grp, members in groups.items()},
                pj._PAIRED_STATS, n, seed=pj._seed(seed, "brier", name, h, ref),
            )
            brier[name][str(h)] = {
                grp: {"days": result[grp]["days"], "vs_published": result[grp]["brier_difference_vs_climatology"]} for grp in groups
            }
            paired_loss = pj._bootstrap(
                declaration,
                {grp: rdh.log_loss_vectors(p, ref_p, outcomes, set(members), floor) for grp, members in groups.items()},
                {"log_loss_difference": pj._ratio(1, 0)}, n, seed=pj._seed(seed, "log_loss", name, h, ref),
            )
            log_loss[name][str(h)] = {grp: paired_loss[grp]["log_loss_difference"] for grp in groups}
            arm_days, pub_days = risk_days.get((_arm, h)), risk_days.get(("published", h))
            moved = [k for k in range(n) if abs(p[k] - ref_p[k]) > SAME]
            cell = {"scored_days": n, "forecast_differs": len(moved)}
            if arm_days is not None and pub_days is not None:
                dates = [day.isoformat() for day in g.dates]
                on_risk_both = [k for k in moved if dates[k] in arm_days and dates[k] in pub_days]
                newly_risk = [k for k in moved if dates[k] in arm_days and dates[k] not in pub_days]
                other = [k for k in moved if dates[k] not in arm_days]
                cell.update({
                    "risk_days_published": sum(1 for d in dates if d in pub_days),
                    "risk_days_arm": sum(1 for d in dates if d in arm_days),
                    "risk_day_in_both_readings": len(on_risk_both),
                    "newly_a_risk_day": len(newly_risk),
                    "not_a_risk_day_under_the_arm": len(other),
                })
            differ[name][str(h)] = cell

    onset_days = {day for i, day in enumerate(common) if onset[i]}
    coupon = {}
    for name in sorted(caught_by):
        coupon[name] = {}
        for day in COUPON_ONSETS:
            when = date.fromisoformat(day)
            coupon[name][day] = {
                "is_onset": when in onset_days,
                "leads_flagged": [h for h in horizons if when in place[h] and flagged_at(name, h, when)],
            }
    document = {
        "declaration": declared,
        "rule": args.rule,
        "onsets": int(sum(onset)),
        "onsets_in_cell": onsets_in,
        "caught_at_some_lead": caught_count,
        "recall_at_some_lead": recall,
        "flags": flags,
        "brier": brier,
        "log_loss": log_loss,
        "forecast_differences": differ,
        "coupon_onsets": coupon,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(document)
    if args.markdown:
        args.markdown.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def markdown(document: dict) -> str:
    out = []
    arms = ("settle", "h41", "both")
    heads = [parent + variant for parent in PARENT_NAMES for variant in VARIANTS]
    out.append("Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the published row and each arm.\n")
    for head in heads:
        group = [head] + [head + ARMS[a][2] for a in arms]
        out.append(f"\n{head}\n")
        out.append("| cell | onsets | published | " + " | ".join(arms) + " |")
        out.append("|---|---|---|" + "---|" * len(arms))
        for cell, n_onsets in document["onsets_in_cell"].items():
            out.append(f"| {cell} | {n_onsets} | " + " | ".join(str(document["caught_at_some_lead"][n][cell]) for n in group) + " |")
    out.append("\nTable 2. Recall difference against the published row, by cell (90% interval).\n")
    for head in heads:
        out.append(f"\n{head}\n")
        out.append("| cell | " + " | ".join(arms) + " |")
        out.append("|---|" + "---|" * len(arms))
        for cell in document["onsets_in_cell"]:
            out.append(f"| {cell} | " + " | ".join(_interval(document["recall_at_some_lead"][head + ARMS[a][2]][cell]["recall_difference"]) for a in arms) + " |")
    out.append("\nTable 3. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.\n")
    out.append("| row | " + " | ".join(f"h = {h}" for h in (1, 2, 3, 4, 5)) + " |")
    out.append("|---|" + "---|" * 5)
    for head in heads:
        for name in [head] + [head + ARMS[a][2] for a in arms]:
            cells = []
            for h in ("1", "2", "3", "4", "5"):
                c = document["flags"][name][h]
                cells.append(f"{c['flags']}({c['false_alarms']}); {c['onsets_flagged']}/{c['onsets']}; {_f(c['false_alarms_per_onset'], 2)}")
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nTable 4. The seven coupon-settlement onsets of docs/pivot/desk-standard-result.md section 2 that are not calendar risk dates: the leads at which each row flags (judge's cut-offs), `-` if none.\n")
    out.append("| row | " + " | ".join(COUPON_ONSETS) + " |")
    out.append("|---|" + "---|" * len(COUPON_ONSETS))
    for head in heads:
        for name in [head] + [head + ARMS[a][2] for a in arms]:
            cells = []
            for day in COUPON_ONSETS:
                c = document["coupon_onsets"][name][day]
                cells.append(("h " + ",".join(str(h) for h in c["leads_flagged"])) if c["leads_flagged"] else "-")
            out.append(f"| {name} | " + " | ".join(cells) + " |")
    out.append("\nTable 5. Where each arm differs from the published row: scored days, days on which the +5 bp forecast differs (by more than 1e-9), and of those the days that are a risk day under both readings, newly a risk day under the arm (a coupon-settlement day at h >= 2), and not a risk day under the arm.\n")
    for h in ("1", "2", "3", "4", "5"):
        out.append(f"\nh = {h}\n")
        out.append("| row | risk days published / arm | forecast differs | risk day in both | newly a risk day | other days |")
        out.append("|---|---|---|---|---|---|")
        for head in heads:
            for a in arms:
                name = head + ARMS[a][2]
                c = document["forecast_differences"][name][h]
                out.append(
                    f"| {name} | {c.get('risk_days_published', '-')} / {c.get('risk_days_arm', '-')} | {c['forecast_differs']} | "
                    f"{c.get('risk_day_in_both_readings', '-')} | {c.get('newly_a_risk_day', '-')} | {c.get('not_a_risk_day_under_the_arm', '-')} |"
                )
    out.append("\nTable 6. Paired Brier score and log loss the published row loses to the arm (positive favours the arm), +5 bp, 90% interval, by horizon: all days and by pressure-day type.\n")
    for h in ("1", "2", "3", "4", "5"):
        out.append(f"\nh = {h}\n")
        out.append("| row | cell | days | Brier vs published | log loss vs published |")
        out.append("|---|---|---|---|---|")
        for _arm, name, _ref in rows_of_pairs():
            for cell, c in document["brier"][name][h].items():
                if cell == "all" or cell.startswith("day type"):
                    out.append(f"| {name} | {cell} | {int(c['days'])} | {_interval(c['vs_published'])} | {_interval(document['log_loss'][name][h][cell])} |")
    return "\n".join(out)


def summary_command(args) -> int:
    """The judge's tier 1 row at +5 bp for every published and arm row, under each rule."""

    judged = {rule: json.loads(Path(path).read_text())["candidates"] for rule, path in (("flat", args.flat), ("weighted", args.weighted))}
    lines = [
        "| row | onsets flagged, flat / weighted | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    yes = lambda x: "yes" if x else "no"
    for parent in PARENT_NAMES:
        for variant in VARIANTS:
            for arm in ARMS:
                name = name_of(parent, variant, arm)
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
    run.add_argument("--candidate", default=None, help="one parent")
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
