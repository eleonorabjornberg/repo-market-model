"""Why does gbm_funding fitted on direct pairs score below the same model on one-step pairs? (#865, H5): arms, walks and scoring.

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths
it is given and nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no
published figure. Every choice is in `metadata/twin_diagnosis_865.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

The reference is #449's pair of walks (`scripts/spread_distribution_634.py walk --variant gbm_funding` and
`scripts/direct_twin_449.py walk`), re-run here. Two kinds of arm change one thing in the twin or the control:

* `train_k`: the twin with the training pairs read k + 1 business days before their target (k <= the lead) instead of h + 1.
* `control_trim`: the control fitted without the first h + 3 rows, so that its training targets are exactly the twin's.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 3 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/direct_twin_449.py walk --horizon $h --published PUB.csv \\
            --output OUT/gbm_funding_direct_h$h.json
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/twin_diagnosis_865.py walk --arm train_k --k 1 --horizon 5 --published PUB.csv \\
        --output OUT/gbm_funding_direct_k1_h5.json
    PYTHONPATH=src python3 scripts/twin_diagnosis_865.py alignment --published PUB.csv --output OUT/alignment.json
    PYTHONPATH=src python3 scripts/twin_diagnosis_865.py score --published PUB.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/twin_diagnosis_865.py report OUT/score.json --alignment OUT/alignment.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
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
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "alignment_row": (
        "not_entry",
        "reads one training pair's information set for a named decision day and checks both guards "
        "(#865); scores nothing; the named days (`ALIGNMENT_DAYS`) all end on or before 2025-12-31",
    ),
}

DECLARATION = REPO / "metadata" / "twin_diagnosis_865.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
RECORDED = REPO / "docs" / "research" / "direct-twin-449" / "score.json"
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
SEED = 865
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 2_000
MINIMUM_DAYS = 30
HORIZONS = sp.HORIZONS
GRID = sp.GRID
CONTROL = "gbm_funding"
TWIN = "gbm_funding_direct"
SCENARIOS = ("all days", "without 2019-09-18")
ALIGNMENT_DAYS = (date(2019, 9, 17), date(2020, 3, 16), date(2021, 12, 31), date(2023, 3, 13), date(2025, 12, 12))
#: fields announced ahead of their day (metadata/sources.json), the only ones a read may take from a row after the decision day
FORWARD_KNOWN = ("treasury_settlement",)
#: the arms walked (declared in metadata/twin_diagnosis_865.json): (kind, lead, k)
ARMS = (("train_k", 3, 1), ("train_k", 3, 2), ("train_k", 5, 1), ("train_k", 5, 3), ("control_trim", 5, None))
#: a tolerance for the reproduction of #449's recorded skill: the walks are deterministic, so this is rounding only
REPRODUCTION_TOLERANCE = 1e-6


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the declaration and the guards ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD` (the check of #449's script)."""

    return _load("direct_twin_449").committed_declaration(path)


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"twin_diagnosis_865 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the arms -------------------------------------------------------------------------------------------------------


def arm_name(kind: str, k: Optional[int] = None) -> str:
    if kind == "train_k":
        return f"{TWIN}_k{k}"
    if kind == "control_trim":
        return "gbm_funding_trim"
    raise ValueError(f"{kind!r} is not a declared arm")


def check_arm(*, lead: int, k: Optional[int]) -> None:
    """A `train_k` arm trains on pairs read k + 1 business days before their target, 1 <= k <= the lead.

    Fresher than the lead it is served at, never staler: a staler pairing is a different question (the twin is k = lead).
    """

    if k is None or not 1 <= k <= lead:
        raise ValueError(f"training lag k = {k!r} must satisfy 1 <= k <= the lead ({lead})")


def regressors(features: Sequence[str]) -> Tuple[str, ...]:
    return tuple(name for name in features if name != "spread_bps")


def train_k_fit(features: Sequence[str], k: int, registry: Mapping, *, decision_time=None):
    """The twin's fit with the training pairs read by an as-of rule of horizon `k`; everything else is the twin's.

    The fit names `information` so the walk hands it its own rule (lead h), which it ignores for the training pairs: they are read
    by `InformationRule(horizon=k)`. Every training target is in the frame the walk hands over, which ends at the walk's anchor, so
    no pair reads a row the walk's decision instant could not see.
    """

    sd = _load("spread_distribution_634")
    rule = InformationRule(registry, tuple(features), decision_time=decision_time or sd.DECISION, horizon=k)
    names = regressors(features)

    def fit(train_frame, minimum_history, information=None):
        return ml.fit_gradient_boosted_quantiles(
            train_frame, regressors=names, levels=GRID, minimum_history=minimum_history, information=rule, training_pairs="direct"
        )

    return fit


def trimmed(frame: Sequence, lead: int) -> list:
    """The frame without its first `lead + 3` rows: the targets the twin trains no pair on (they have no as-of read)."""

    return list(frame)[lead + 3 :]


def trim_fit(features: Sequence[str], lead: int):
    """The control on the trimmed frame. Its minimum history counts the trimmed frame, so the walk's first fit (61 rows) fits."""

    names = regressors(features)

    def fit(train_frame, minimum_history):
        return ml.fit_gradient_boosted_quantiles(trimmed(train_frame, lead), regressors=names, levels=GRID, minimum_history=minimum_history - (lead + 3))

    return fit


# -- the walks ------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    h, kind, k = args.horizon, args.arm, args.k
    if h not in HORIZONS:
        raise SystemExit(f"horizon {h} is not a protocol lead")
    if kind not in declared["arms"] and kind != "trim":
        raise SystemExit(f"{kind!r} is not a declared arm")
    kind = "control_trim" if kind in ("trim", "control_trim") else kind
    if kind == "train_k":
        check_arm(lead=h, k=k)
    elif k is not None:
        raise SystemExit("control_trim takes no --k")
    name = arm_name(kind, k)
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="twin_diagnosis_865")
    if sd.finished_walk(args.output, variant=name, horizon=h, published=args.published, panel=args.published):
        print(json.dumps({"variant": name, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    features = tuple(sd._load("live_record").published_features(h))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    fit = train_k_fit(features, k, registry) if kind == "train_k" else trim_fit(features, h)
    result, levels, settings = sd.walk(
        rows, fit=fit, features=features, online_calibration=None, registry=registry,
        horizon=h, minimum_history=61, refit_every=21, expected_levels=GRID,
    )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": name,
        "horizon": h,
        "arm": {"kind": kind, "k": k},
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
    print(json.dumps({"variant": name, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the alignment check --------------------------------------------------------------------------------------------


def alignment_row(rule: InformationRule, dates: Sequence[date], decision: date, lead: int) -> dict:
    """The twin's training pair for target `decision + lead` business days, read at the lead: what it reads and when.

    The anchor is the last row whose spread the decision instant could see, before the decision day. A field may be read from a row
    after the decision day only if it is announced ahead (`FORWARD_KNOWN`). `rule.check` (both guards) is called, as the walk and
    `_direct_pairs` call it.
    """

    position = {day: index for index, day in enumerate(dates)}
    target = position[decision] + lead
    info = rule.information_set(dates, target)
    rule.check(dates, info)
    reads = sorted({dates[field.row] for field in info.reads})
    return {
        "decision_day": decision.isoformat(),
        "lead": lead,
        "target_day": dates[target].isoformat(),
        "anchor": dates[info.anchor].isoformat(),
        "anchor_rows_before_target": target - info.anchor,
        "latest_read": reads[-1].isoformat(),
        "earliest_read": reads[0].isoformat(),
        "fields_read_after_the_anchor": sorted(
            {name for field in info.reads if dates[field.row] > dates[info.anchor] for _source, name in field.fields}
        ),
        "fields_read_after_the_decision_day": sorted(
            {name for field in info.reads if dates[field.row] > decision for _source, name in field.fields}
        ),
    }


def alignment_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    live = sd._load("live_record")
    rows = [row for row in load_daily_panel(args.published) if row.date <= LAST_TARGET]
    dates = [row.date for row in rows]
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    table = []
    for h in HORIZONS:
        features = tuple(live.published_features(h))
        rule = InformationRule(registry, features, decision_time=sd.DECISION, horizon=h)
        for day in ALIGNMENT_DAYS:
            if day not in dates:
                raise SystemExit(f"{day} is not a panel day")
            table.append(alignment_row(rule, dates, day, h))
    document = {"panel_sha256": panel_sha256(args.published), "rows": table}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    bad = [row for row in table if set(row["fields_read_after_the_decision_day"]) - set(FORWARD_KNOWN)]
    print(json.dumps({"output": str(args.output), "rows": len(table), "reads_that_are_not_announced_ahead": len(bad)}))
    return 0 if not bad else 1


# -- scoring --------------------------------------------------------------------------------------------------------


def half_year(day: date) -> str:
    return f"{day.year}H{1 if day.month <= 6 else 2}"


def gap_closed(*, twin_to_arm: float, twin_to_control: float) -> Optional[float]:
    """Mean difference twin -> arm over twin -> control: 1 when the arm is the control; `None` where the twin is not worse."""

    if twin_to_control <= 0:
        return None
    return twin_to_arm / twin_to_control


def without_excluded(days: Sequence[date]) -> List[date]:
    return [day for day in days if day != EXCLUDED_DAY]


def _summarise(test) -> dict:
    return _load("direct_twin_449")._summarise(test)


def _paired_job(job):
    key, chosen, draws = job
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return key, [_summarise(test) for test in tests]


def load_walk(directory: Path, name: str, lead: int, published: Path) -> Optional[Dict[date, Optional[List[float]]]]:
    path = directory / f"{name}_h{lead}.json"
    if not path.exists():
        return None
    document = json.loads(path.read_text(encoding="utf-8"))
    if document["panel_sha256"] != panel_sha256(published) or document["variant"] != name or document["horizon"] != lead:
        raise ValueError(f"{path.name} is not the walk of {name} at lead {lead} on this panel")
    return {date.fromisoformat(day): (None if q is None else [float(v) for v in q]) for day, q in document["laws"].items()}


def score_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="twin_diagnosis_865")
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
    days = [
        d for d in calendar
        if first <= d <= last and d not in unbuilt and position[d] + max(HORIZONS) < len(calendar)
        and calendar[position[d] + max(HORIZONS)] <= LAST_TARGET
    ]
    if len(days) != recorded["decision_days"]["n"]:
        raise ValueError(f"the decision-day set has {len(days)} days, #449's score has {recorded['decision_days']['n']}")
    sd.refuse_locked(days + [calendar[position[d] + h] for d in days for h in HORIZONS])
    b1 = pb.forecasts(pb.b1_forecast, rows, days, registry=registry, decision_time=sd.DECISION)

    walks: Dict[str, Dict[int, Dict[date, Optional[List[float]]]]] = {}
    names_at: Dict[int, List[str]] = {}
    for lead in HORIZONS:
        for name in (CONTROL, TWIN, *(arm_name(kind, k) for kind, h, k in ARMS if h == lead)):
            laws = load_walk(args.walks, name, lead, args.published)
            if laws is not None:
                walks.setdefault(name, {})[lead] = laws
                names_at.setdefault(lead, []).append(name)
    leads = [lead for lead in HORIZONS if CONTROL in names_at.get(lead, []) and TWIN in names_at.get(lead, [])]
    if not leads:
        raise SystemExit("no lead has both the control's and the twin's walk")
    cells: Dict[str, Dict[Tuple[date, int], float]] = {}
    missing: Dict[str, Dict[str, dict]] = {}
    for name, by_lead in walks.items():
        cells[name], missing[name] = {}, {}
        for lead, laws in by_lead.items():
            absent = 0
            for d in days:
                target = calendar[position[d] + lead]
                if outcomes.get(target) is None:
                    continue
                law = laws.get(target)
                if law is None:
                    absent += 1
                    law = b1[d][lead]
                cells[name][(d, lead)] = sp.grid_crps(law, outcomes[target])
            missing[name][str(lead)] = {"days": absent, "share": absent / len(days)}

    # the reproduction of #449's recorded skill of the twin over the control, at each walked lead
    reproduced = {}
    for lead in leads:
        control = {d: cells[CONTROL][(d, lead)] for d in days if (d, lead) in cells[CONTROL]}
        twin = {d: cells[TWIN][(d, lead)] for d in days if (d, lead) in cells[TWIN]}
        skill = (sum(control.values()) - sum(twin.values())) / sum(control.values())
        recorded_skill = recorded["tables"]["all days"]["all"]["all"][str(lead)]["tests"][f"{CONTROL} -> {TWIN}"]["skill"]
        reproduced[str(lead)] = {"recomputed": skill, "recorded_449": recorded_skill, "difference": skill - recorded_skill}
        if abs(skill - recorded_skill) > REPRODUCTION_TOLERANCE:
            raise ValueError(f"lead {lead}: the twin's skill over the control is {skill} here and {recorded_skill} in #449's score")

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    kinds = sorted({kind_of(calendar[position[d] + h]) for d in days for h in leads})
    half_years = sorted({half_year(d) for d in days})

    def means(names: Sequence[str], group: Sequence[date], lead: Optional[int], kind: Optional[str]) -> Dict[str, Dict[date, float]]:
        keep = set(group)

        def include(d, h):
            return d in keep and (lead is None or h == lead) and h in leads and (kind is None or kind_of(calendar[position[d] + h]) == kind)

        return {n: sd.day_means(cells[n], include) for n in names}

    jobs, shells = [], {}
    for scenario in SCENARIOS:
        scored = days if scenario == SCENARIOS[0] else without_excluded(days)
        groups = {"all": scored}
        for label in splits.regime_labels:
            groups[f"regime {label}"] = [d for d in scored if splits.regime(d) == label]
        for label in half_years:
            groups[f"half-year {label}"] = [d for d in scored if half_year(d) == label]
        for group_name, group in groups.items():
            for kind in (None, *kinds):
                if group_name != "all" and kind is not None:
                    continue
                for lead in (None, *leads):
                    names = [CONTROL, TWIN] if lead is None else names_at[lead]
                    series = means(names, group, lead, kind)
                    common = sorted(set.intersection(*(set(series[n]) for n in names)) & set(group))
                    key = (scenario, group_name, kind or "all", lead or "pooled")
                    entry = {"n": len(common), "names": names, "mean": {n: sum(series[n][d] for d in common) / len(common) for n in names} if common else {}}
                    pairs = [(CONTROL, TWIN)] + [(CONTROL, n) for n in names if n not in (CONTROL, TWIN)] + [(TWIN, n) for n in names if n not in (CONTROL, TWIN)]
                    if len(common) < MINIMUM_DAYS or len(common) <= sp.HAC_LAG:
                        entry["thin"] = True
                    else:
                        headline = group_name == "all" and kind is None
                        jobs.append((key, [({d: series[b][d] for d in common}, {d: series[c][d] for d in common}) for b, c in pairs], HEADLINE_DRAWS if headline else SPLIT_DRAWS))
                        entry["pairs"] = [f"{b} -> {c}" for b, c in pairs]
                    shells[key] = entry
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, results in pool.map(_paired_job, jobs):
            shells[key]["tests"] = dict(zip(shells[key]["pairs"], results))
            for row_key, row in shells[key]["tests"].items():
                before, _, after = row_key.partition(" -> ")
                if before == TWIN and after != CONTROL:
                    twin_worse = shells[key]["tests"][f"{CONTROL} -> {TWIN}"]["mean_difference"]
                    row["gap_closed"] = gap_closed(twin_to_arm=row["mean_difference"], twin_to_control=-twin_worse)
    tables: Dict[str, dict] = {}
    for (scenario, group, kind, lead), entry in shells.items():
        tables.setdefault(scenario, {}).setdefault(group, {}).setdefault(kind, {})[str(lead)] = entry
    document = {
        "declaration": "metadata/twin_diagnosis_865.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "seed": SEED,
        "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS},
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "leads": leads,
        "arms": {name: {"leads": sorted(by_lead)} for name, by_lead in walks.items()},
        "missing": missing,
        "reproduction_of_449": reproduced,
        "kinds": kinds,
        "regimes": list(splits.regime_labels),
        "half_years": half_years,
        "tables": tables,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days), "leads": leads}))
    return 0


# -- the report -----------------------------------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def cell(entry: dict, pair: str) -> str:
    if entry.get("thin"):
        return "too thin"
    row = entry["tests"].get(pair)
    if row is None:
        return "n/a"
    return f"{100 * row['skill']:+.1f}% [{100 * row['skill_lower_95_one_sided']:+.1f}, {100 * row['skill_upper_95_one_sided']:+.1f}]"


def report_table(title: str, tables: Mapping[str, dict], group: str, kind: str, leads: Sequence[str]) -> List[str]:
    lines = [f"### {title}", ""]
    rows = []
    for lead in leads:
        entry = tables[group][kind].get(lead)
        if entry is None or not entry["mean"]:
            continue
        others = [n for n in entry["names"] if n not in (CONTROL, TWIN)]
        rows.append((lead, entry, others))
    if not rows:
        return []
    lines += ["| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |", "|---|---|---|---|---|---|---|---|---|"]
    for lead, entry, others in rows:
        if not others:
            lines.append(f"| {lead} | {entry['n']} | {fmt(entry['mean'][CONTROL])} | {fmt(entry['mean'][TWIN])} | | {cell(entry, f'{CONTROL} -> {TWIN}')} | | | |")
        for other in others:
            tests = entry.get("tests", {})
            closed = tests.get(f"{TWIN} -> {other}", {}).get("gap_closed")
            lines.append(
                f"| {lead} | {entry['n']} | {fmt(entry['mean'][CONTROL])} | {fmt(entry['mean'][TWIN])} | `{other}` {fmt(entry['mean'][other])} | "
                f"{cell(entry, f'{CONTROL} -> {TWIN}')} | {cell(entry, f'{CONTROL} -> {other}')} | {cell(entry, f'{TWIN} -> {other}')} | "
                f"{'n/a' if closed is None else f'{100 * closed:.0f}%'} |"
            )
    return lines + [""]


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    leads = ["pooled", *map(str, score["leads"])]
    out = [
        "# Why the direct-pairs twin scores below gbm_funding (#865, H5)",
        "",
        "Development data, a measurement and never a verdict (scoring protocol v1). Nothing is published or registered; the declared candidate,",
        "the published model and every published figure are as they were. Declaration: `metadata/twin_diagnosis_865.json`.",
        "",
        f"Decision days {score['decision_days']['first']} to {score['decision_days']['last']} ({score['decision_days']['n']}). Panel `{score['panel_sha256'][:12]}…`.",
        f"Leads walked here: {', '.join(map(str, score['leads']))}. Grid CRPS in bp (lower is better). A skill is the first named forecast's loss less the second's, over the first's,",
        "positive favouring the second, with the one-sided 95% lower and upper bounds from the studentized stationary bootstrap, as `[lower, upper]` "
        f"(block 10, seed {score['seed']}; {score['draws']['headline']:,} draws on pooled and per-lead figures, {score['draws']['splits']:,} on splits). Pooled rows average the walked leads.",
        "",
        "## Reproduction of #449",
        "",
        "| lead | twin vs control here | recorded in #449 | difference |",
        "|---|---|---|---|",
    ]
    for lead, row in score["reproduction_of_449"].items():
        out.append(f"| {lead} | {100 * row['recomputed']:+.4f}% | {100 * row['recorded_449']:+.4f}% | {row['difference']:.2e} |")
    out.append("")
    for scenario in SCENARIOS:
        tables = score["tables"][scenario]
        out += [f"## {scenario}", ""]
        out += report_table("Pooled over the walked leads and each lead alone", tables, "all", "all", leads)
        for kind in score["kinds"]:
            out += report_table(f"Target-day type: {kind}", tables, "all", kind, leads)
        for label in score["regimes"]:
            out += report_table(f"Regime of the decision day: {label}", tables, f"regime {label}", "all", leads)
        for label in score["half_years"]:
            out += report_table(f"Half-year of the decision day: {label}", tables, f"half-year {label}", "all", leads)
    if args.alignment:
        alignment = json.loads(args.alignment.read_text(encoding="utf-8"))
        out += [
            "## The alignment check on named days",
            "",
            "The twin's lead-h training pair for target d + h, read by `asof.InformationRule(horizon=h)` and checked by both guards.",
            "",
            "| decision day d | lead | target | anchor | rows from anchor to target | latest read | fields read after the decision day |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in alignment["rows"]:
            out.append(
                f"| {row['decision_day']} | {row['lead']} | {row['target_day']} | {row['anchor']} | {row['anchor_rows_before_target']} | "
                f"{row['latest_read']} | {', '.join(row['fields_read_after_the_decision_day']) or 'none'} |"
            )
        out.append("")
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="walk one arm at one lead")
    walk.add_argument("--arm", required=True, choices=["train_k", "control_trim", "trim"])
    walk.add_argument("--k", type=int)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    align = sub.add_parser("alignment", help="the named-day alignment check")
    align.add_argument("--published", type=Path, required=True)
    align.add_argument("--output", type=Path, required=True)
    align.set_defaults(run=alignment_command)
    score = sub.add_parser("score", help="score the walks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    report = sub.add_parser("report", help="the Markdown report")
    report.add_argument("score", type=Path)
    report.add_argument("--alignment", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
