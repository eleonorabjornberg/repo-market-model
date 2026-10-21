"""gbm_funding with `treasury_settlement` trained from the target's own row, at lead 1 (#931, H5): arm, walk, scoring and report.

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths
it is given and nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no
published figure. Every choice is in `metadata/aligned_pairs_931.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

`gbm_funding` at lead 1 takes `treasury_settlement` as an input (`live_record.published_features(1)`). Served, the as-of rule reads it
from the target's own row (announced a day ahead); trained on one-step pairs, row p's value is paired with spread(p + 1). The arm
`gbm_funding_aligned` is `gbm_funding` with exactly that field trained from row p + 1, the row it is served from: one-step pairs for
every other field, the same fit, seed, fold grid and quantile grid. The reference is the pair of walks of #449 at lead 1 (the control
`gbm_funding`, the direct-pairs twin `gbm_funding_direct`), re-walked here and reproduced to the digit.

Walk-forward refits are long: the walks are run on the Mac (`needs-mac`, #46's top block), then scored and reported here.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon 1 \\
        --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h1.json
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/direct_twin_449.py walk --horizon 1 --published PUB.csv \\
        --output OUT/gbm_funding_direct_h1.json
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_pairs_931.py walk --published PUB.csv \\
        --output OUT/gbm_funding_aligned_h1.json
    PYTHONPATH=src python3 scripts/aligned_pairs_931.py alignment --published PUB.csv --output OUT/alignment.json
    PYTHONPATH=src python3 scripts/aligned_pairs_931.py score --published PUB.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/aligned_pairs_931.py report OUT/score.json --alignment OUT/alignment.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "served_row": (
        "not_entry",
        "reads one target's information set for a named day and checks both guards (#931); scores "
        "nothing; the named days (`alignment_days` in the declaration) all end on or before "
        "2025-12-31",
    ),
}

DECLARATION = REPO / "metadata" / "aligned_pairs_931.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
RECORDED = REPO / "docs" / "research" / "direct-twin-449" / "score.json"
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
SEED = 931
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 2_000
MINIMUM_DAYS = 30
LEAD = 1
GRID = sp.GRID
FIELD = "treasury_settlement"
COUPON_FIELD = "treasury_settlement_coupons"
CONTROL = "gbm_funding"
ALIGNED = "gbm_funding_aligned"
TWIN = "gbm_funding_direct"
MODELS = (CONTROL, ALIGNED, TWIN)
PAIRS = [
    ("B1", CONTROL), ("B1", ALIGNED), ("B1", TWIN),
    ("B2", CONTROL), ("B2", ALIGNED), ("B2", TWIN),
    (CONTROL, ALIGNED), (CONTROL, TWIN), (ALIGNED, TWIN),
]
SCENARIOS = ("all days", "without 2019-09-18")
#: a tolerance for the reproduction of #449's recorded skill: the walks are deterministic, so this is rounding only
REPRODUCTION_TOLERANCE = 1e-6
MID_MONTH_COUPON = "mid_month_coupon"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the declaration and the guards ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"aligned_pairs_931 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the arm --------------------------------------------------------------------------------------------------------


def align_field(frame: Sequence[DailyObservation], field: str = FIELD) -> List[DailyObservation]:
    """The frame with `field` of row p replaced by row p + 1's, so that the one-step pair (p, p + 1) trains `field` from the target's row.

    Every other field of every row, and every date, is the frame's own. The last row has no successor in the frame and is no origin of a
    pair (an origin needs a target among the fit rows); its `field` is made a hole rather than left as a value of the wrong day. A
    regressor read from a row after the last row of the frame is never invented.
    """

    rows = list(frame)
    aligned = []
    for position, row in enumerate(rows):
        values = dict(row.values)
        values[field] = rows[position + 1].values.get(field) if position + 1 < len(rows) else None
        aligned.append(DailyObservation(date=row.date, values=values))
    return aligned


def regressors(features: Sequence[str]) -> Tuple[str, ...]:
    return tuple(name for name in features if name != "spread_bps")


def aligned_fit(features: Sequence[str]):
    """`gbm_funding`'s fit on the frame with the settlement field aligned to its target; nothing else changed."""

    names = regressors(features)
    if FIELD not in names:
        raise ValueError(f"{FIELD!r} is not among the regressors {names}; there is nothing to align")

    def fit(train_frame, minimum_history):
        return ml.fit_gradient_boosted_quantiles(
            align_field(train_frame), regressors=names, levels=GRID, minimum_history=minimum_history
        )

    return fit


# -- the walk -------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="aligned_pairs_931")
    if sd.finished_walk(args.output, variant=ALIGNED, horizon=LEAD, published=args.published, panel=args.published):
        print(json.dumps({"variant": ALIGNED, "horizon": LEAD, "skipped": "finished walk at " + str(args.output)}))
        return 0
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    features = tuple(sd._load("live_record").published_features(LEAD))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    result, levels, settings = sd.walk(
        rows, fit=aligned_fit(features), features=features, online_calibration=None, registry=registry,
        horizon=LEAD, minimum_history=61, refit_every=21, expected_levels=GRID,
    )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": ALIGNED,
        "horizon": LEAD,
        "levels": levels,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": None,
        "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)),
        "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": ALIGNED, "horizon": LEAD, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the alignment check --------------------------------------------------------------------------------------------


def served_row(rule: InformationRule, dates: Sequence[date], target: int, field: str = FIELD) -> date:
    """The day of the row the as-of rule reads `field` from when serving the forecast of target row `target` (both guards called)."""

    info = rule.information_set(dates, target)
    rule.check(dates, info)
    rows = {dates[read.row] for read in info.reads if any(name == field for _source, name in read.fields)}
    if len(rows) != 1:
        raise ValueError(f"{field!r} is read from {len(rows)} rows for the target {dates[target]}, not one")
    return rows.pop()


def trained_row(frame_dates: Sequence[date], origin: int, aligned: bool) -> date:
    """The day of the row the training pair (origin, origin + 1) takes the settlement field from: its own row, or the target's."""

    return frame_dates[origin + 1] if aligned else frame_dates[origin]


def alignment_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    declared = json.loads(DECLARATION.read_text(encoding="utf-8"))
    rows = [row for row in load_daily_panel(args.published) if row.date <= LAST_TARGET]
    dates = [row.date for row in rows]
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    features = tuple(sd._load("live_record").published_features(LEAD))
    rule = InformationRule(registry, features, decision_time=sd.DECISION, horizon=LEAD)
    table = []
    for day in declared["alignment_days"]:
        target = date.fromisoformat(day)
        index = dates.index(target)
        table.append({
            "target_day": day,
            "served_from": served_row(rule, dates, index).isoformat(),
            "one_step_trains_from": trained_row(dates, index - 1, aligned=False).isoformat(),
            "aligned_trains_from": trained_row(dates, index - 1, aligned=True).isoformat(),
            "settlement_billions": rows[index].values.get(FIELD),
            "settlement_billions_day_before": rows[index - 1].values.get(FIELD),
        })
    document = {"panel_sha256": panel_sha256(args.published), "rows": table}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    bad = [r for r in table if r["served_from"] != r["aligned_trains_from"]]
    print(json.dumps({"output": str(args.output), "rows": len(table), "aligned_rows_that_differ_from_serving": len(bad)}))
    return 0 if not bad else 1


# -- scoring --------------------------------------------------------------------------------------------------------


def without_excluded(days: Sequence[date]) -> List[date]:
    return [day for day in days if day != EXCLUDED_DAY]


def day_type(reporting: str, values: Mapping[str, Optional[float]]) -> str:
    """The reporting day type of a target day, with its ordinary days split: a mid-month coupon settlement day is its own type.

    A mid-month coupon date is a day the splits call ordinary on which `treasury_settlement_coupons` is positive.
    """

    coupon = values.get(COUPON_FIELD)
    if reporting == "ordinary" and coupon is not None and float(coupon) > 0.0:
        return MID_MONTH_COUPON
    return reporting


def _summarise(test) -> dict:
    skill_lower = test.skill - sp._bound(test.skill_t_draws, 1.0 - test.alpha, test.draws) * test.skill_standard_error
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "mean_difference": test.mean_difference,
        "skill": test.skill,
        "mean_difference_lower_95_one_sided": test.lower_mean_difference(),
        "skill_lower_95_one_sided": skill_lower,
        "skill_upper_95_one_sided": test.upper_skill(),
        "bootstrap_p": test.p_value,
        "dm_statistic": test.dm_statistic,
        "dm_p": test.dm_p_value,
    }


def _paired_job(job):
    key, chosen, draws = job
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return key, [_summarise(test) for test in tests]


def load_walk(directory: Path, name: str, published: Path) -> Dict[date, Optional[List[float]]]:
    path = directory / f"{name}_h{LEAD}.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    if document["panel_sha256"] != panel_sha256(published) or document["variant"] != name or document["horizon"] != LEAD:
        raise ValueError(f"{path.name} is not the walk of {name} at lead {LEAD} on this panel")
    return {date.fromisoformat(day): (None if q is None else [float(v) for v in q]) for day, q in document["laws"].items()}


def check_pairing(directory: Path) -> Dict[str, str]:
    """Each walk's recorded pairing, read from its own settings: the control and the arm one-step, the twin direct."""

    out = {}
    for name in MODELS:
        document = json.loads((directory / f"{name}_h{LEAD}.json").read_text(encoding="utf-8"))
        settings = document.get("settings", {})
        if isinstance(settings, str):
            settings = ast.literal_eval(settings)
        out[name] = settings.get("training_pairs", "unset (one-step)")
    one_step = lambda pairing: pairing.startswith("unset")  # noqa: E731
    if not (one_step(out[CONTROL]) and one_step(out[ALIGNED])) or out[TWIN] != "direct":
        raise ValueError(f"the walks are not fitted as declared: {out}")
    return out


def score_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="aligned_pairs_931")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    first = date.fromisoformat(recorded["decision_days"]["first"])
    last = date.fromisoformat(recorded["decision_days"]["last"])
    unbuilt = {date.fromisoformat(day) for day, _ in recorded["decision_days_without_a_benchmark"]}
    # #449's decision days, so that the figures here are those of #825 for the same days
    days = [
        d for d in calendar
        if first <= d <= last and d not in unbuilt and position[d] + 5 < len(calendar) and calendar[position[d] + 5] <= LAST_TARGET
    ]
    if len(days) != recorded["decision_days"]["n"]:
        raise ValueError(f"the decision-day set has {len(days)} days, #449's score has {recorded['decision_days']['n']}")
    sd.refuse_locked(days + [calendar[position[d] + LEAD] for d in days])
    pairing = check_pairing(args.walks)
    b1 = pb.forecasts(pb.b1_forecast, rows, days, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, days, registry=registry, decision_time=sd.DECISION, splits=splits)
    cells: Dict[str, Dict[date, float]] = {}
    missing: Dict[str, dict] = {}
    for name, forecasts in (("B1", b1), ("B2", b2)):
        cells[name] = {d: sp.grid_crps(forecasts[d][LEAD], outcomes[calendar[position[d] + LEAD]]) for d in days}
    for name in MODELS:
        laws = load_walk(args.walks, name, args.published)
        absent, cells[name] = 0, {}
        for d in days:
            target = calendar[position[d] + LEAD]
            law = laws.get(target)
            if law is None:
                absent += 1
                law = b1[d][LEAD]
            cells[name][d] = sp.grid_crps(law, outcomes[target])
        missing[name] = {"days": absent, "share": absent / len(days)}

    # the reproduction of #449's recorded skill of the twin over the control, at this lead
    control_sum, twin_sum = sum(cells[CONTROL].values()), sum(cells[TWIN].values())
    skill = (control_sum - twin_sum) / control_sum
    recorded_skill = recorded["tables"]["all days"]["all"]["all"][str(LEAD)]["tests"][f"{CONTROL} -> {TWIN}"]["skill"]
    reproduced = {"recomputed": skill, "recorded_449": recorded_skill, "difference": skill - recorded_skill}
    if abs(skill - recorded_skill) > REPRODUCTION_TOLERANCE:
        raise ValueError(f"the twin's skill over the control is {skill} here and {recorded_skill} in #449's score")

    names = ["B1", "B2", *MODELS]

    def kind_of(day: date) -> str:
        return day_type(splits.reporting_day_type(day, row_of[day].values), row_of[day].values)

    kinds = sorted({kind_of(calendar[position[d] + LEAD]) for d in days})
    jobs, shells = [], {}
    for scenario in SCENARIOS:
        scored = days if scenario == SCENARIOS[0] else without_excluded(days)
        groups = {"all": scored}
        for label in splits.regime_labels:
            groups[f"regime {label}"] = [d for d in scored if splits.regime(d) == label]
        for group_name, group in groups.items():
            for kind in (None, *kinds):
                if group_name != "all" and kind is not None:
                    continue  # the cross of a regime and a day type is not a declared table
                chosen = [d for d in group if kind is None or kind_of(calendar[position[d] + LEAD]) == kind]
                key = (scenario, group_name, kind or "all")
                entry = {"n": len(chosen), "mean": {n: sum(cells[n][d] for d in chosen) / len(chosen) for n in names} if chosen else {}}
                if len(chosen) < MINIMUM_DAYS or len(chosen) <= sp.HAC_LAG:
                    entry["thin"] = True
                else:
                    jobs.append((key, [({d: cells[b][d] for d in chosen}, {d: cells[c][d] for d in chosen}) for b, c in PAIRS],
                                 HEADLINE_DRAWS if group_name == "all" and kind is None else SPLIT_DRAWS))
                shells[key] = entry
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, results in pool.map(_paired_job, jobs):
            shells[key]["tests"] = {f"{b} -> {c}": row for (b, c), row in zip(PAIRS, results)}
    tables: Dict[str, dict] = {}
    for (scenario, group, kind), entry in shells.items():
        tables.setdefault(scenario, {}).setdefault(group, {})[kind] = entry
    document = {
        "declaration": "metadata/aligned_pairs_931.json",
        "panel_sha256": panel_sha256(args.published),
        "lead": LEAD,
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "seed": SEED,
        "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS},
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "excluded_day_scores": {n: cells[n].get(EXCLUDED_DAY) for n in names},
        "missing": missing,
        "pairing": pairing,
        "reproduction_of_449": reproduced,
        "names": names,
        "kinds": kinds,
        "regimes": list(splits.regime_labels),
        "tables": tables,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report -----------------------------------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def pair_cell(entry: dict, pair: str) -> str:
    if entry.get("thin"):
        return "too thin"
    row = entry["tests"][pair]
    return f"{100 * row['skill']:+.1f}% [{100 * row['skill_lower_95_one_sided']:+.1f}, {100 * row['skill_upper_95_one_sided']:+.1f}]"


def table(title: str, entries: Mapping[str, dict], group: str, kind: str) -> List[str]:
    entry = entries[group][kind]
    if not entry["mean"]:
        return []
    mean = entry["mean"]
    pairs = [("B1", CONTROL), ("B1", ALIGNED), ("B2", CONTROL), ("B2", ALIGNED), (CONTROL, ALIGNED), (CONTROL, TWIN), (ALIGNED, TWIN)]
    lines = [
        f"| {title} | {entry['n']} | " + " | ".join(fmt(mean[n], 2) for n in ("B1", "B2", *MODELS)) + " | "
        + " | ".join(pair_cell(entry, f"{b} -> {c}") for b, c in pairs) + " |"
    ]
    return lines


TABLE_HEAD = [
    "| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
]


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    alignment = json.loads(args.alignment.read_text(encoding="utf-8")) if args.alignment else None
    out = [
        "# Training `treasury_settlement` from the target's own row, at lead 1 (#931, H5)",
        "",
        "**Development data, not a verdict.** A measurement under scoring protocol v1: nothing is published or registered; the declared candidate,",
        "the published model and every published figure are as they were. Whether the candidate changes is Eleonora's. Declaration:",
        "`metadata/aligned_pairs_931.json`.",
        "",
        f"Decision days {score['decision_days']['first']} to {score['decision_days']['last']} ({score['decision_days']['n']}), lead {score['lead']} only; no day after",
        f"2025-12-31 and no locked day is scored. Panel `{score['panel_sha256'][:12]}…`. Grid CRPS in bp (lower is better). A skill cell is the skill of the second",
        "forecast over the first named (positive favours the second), with the one-sided 95% lower and upper bounds of skill from the studentized stationary",
        f"bootstrap, as `[lower, upper]` (block 10, seed {score['seed']}; {score['draws']['headline']:,} draws on the pooled row, {score['draws']['splits']:,} on splits).",
        "",
        "## The three arms",
        "",
    ]
    for name, pairs in score["pairing"].items():
        out.append(f"- `{name}`: training pairs {pairs}")
    out += [
        "",
        "`gbm` is the declared `gbm_funding` (one-step pairs). `aligned` is `gbm_funding` with `treasury_settlement` alone trained from the target's own row",
        "(row p + 1 for the pair (p, p + 1)), every other field one-step, same fit, seed and folds. `twin` is the direct-pairs twin of #449, which also reads every",
        "other field at the as-of read, staler than the one-step pair. The score reproduces #449's recorded twin-over-gbm skill at lead 1 "
        f"({100 * score['reproduction_of_449']['recomputed']:+.4f}% against {100 * score['reproduction_of_449']['recorded_449']:+.4f}% recorded).",
        "",
    ]
    if alignment:
        out += [
            "## The alignment, read from the as-of rule (acceptance 1)",
            "",
            "| target day | served from | one-step trains from | aligned trains from | settlement on the day (USD bn) | the day before (USD bn) |",
            "|---|---|---|---|---|---|",
        ]
        for r in alignment["rows"]:
            out.append(
                f"| {r['target_day']} | {r['served_from']} | {r['one_step_trains_from']} | {r['aligned_trains_from']} | "
                f"{fmt(r['settlement_billions'], 1)} | {fmt(r['settlement_billions_day_before'], 1)} |"
            )
        out += ["", "The one-step pair trains the field from the day before the target; serving reads it from the target's own row; the aligned arm trains it from that row.", ""]
    absent = ", ".join("{} {} ({:.1f}%)".format(n, v["days"], 100 * v["share"]) for n, v in score["missing"].items())
    out.append(f"Missing laws (the day takes B1's law): {absent}.")
    out.append("")
    pair = f"{CONTROL} -> {ALIGNED}"
    headline = score["tables"][SCENARIOS[0]]["all"]
    out += ["## The aligned arm against gbm_funding, in one place", ""]
    for label, kind in (("pooled", "all"), *((k, k) for k in score["kinds"])):
        entry = headline[kind]
        out.append(f"- {label} ({entry['n']} days): {pair_cell(entry, pair)}" + (" over gbm_funding's mean grid CRPS of " + fmt(entry["mean"][CONTROL], 2) + " bp" if not entry.get("thin") else ""))
    out += ["", "Skills above are all days; the same table without 2019-09-18 follows. Intervals are one-sided 95% bounds `[lower, upper]`.", ""]
    for scenario in SCENARIOS:
        entries = score["tables"][scenario]
        out += [f"## {scenario}", "", *TABLE_HEAD]
        out += table("pooled", entries, "all", "all")
        out += [""]
        out += ["### By target-day type", "", *TABLE_HEAD]
        for kind in score["kinds"]:
            out += table(kind, entries, "all", kind)
        out += ["", "### By regime of the decision day", "", *TABLE_HEAD]
        for label in score["regimes"]:
            out += table(label, entries, f"regime {label}", "all")
        out.append("")
    out += [
        "## Question for Eleonora (marked; this PR settles nothing)",
        "",
        "Does the declared candidate train `treasury_settlement` from the target's row at lead 1? The measurement above is development evidence, not a verdict,",
        "and changes no published model, declaration or figure.",
        "",
    ]
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="walk the aligned arm at lead 1")
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    alignment = sub.add_parser("alignment", help="the rows the settlement field is served and trained from, on named days")
    alignment.add_argument("--published", type=Path, required=True)
    alignment.add_argument("--output", type=Path, required=True)
    alignment.set_defaults(run=alignment_command)
    score = sub.add_parser("score", help="score the three arms against B1 and B2 and each other")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    report = sub.add_parser("report", help="render the Markdown page")
    report.add_argument("score", type=Path)
    report.add_argument("--alignment", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
