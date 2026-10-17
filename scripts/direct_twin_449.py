"""gbm_funding against its direct-pairs twin under scoring protocol v1 (#449, H5): walks, scoring and report.

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths
it is given and nothing into `docs/runs/`, registers nothing and changes no rule, no published model and no published figure.
Every choice is in `metadata/direct_twin_449.json`, which this script refuses to read unless it is committed and unchanged. No day
after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

The control is `gbm_funding` of #634 (`ml.fit_gradient_boosted_quantiles` on one-step pairs, `training_pairs` unset); the twin is
the same call with `training_pairs="direct"` and nothing else changed. The control's walks are those of
`scripts/spread_distribution_634.py walk --variant gbm_funding`; the twin's are walked here on the same fold grid.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/direct_twin_449.py walk --horizon $h --published PUB.csv \\
            --output OUT/gbm_funding_direct_h$h.json
    PYTHONPATH=src python3 scripts/direct_twin_449.py score --published PUB.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/direct_twin_449.py report OUT/score.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import ast
import functools
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
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "direct_twin_449.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
SEED = 449
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 2_000
MINIMUM_DAYS = 30
HORIZONS = sp.HORIZONS
GRID = sp.GRID
CONTROL = "gbm_funding"
TWIN = "gbm_funding_direct"
MODELS = (CONTROL, TWIN)
PAIRS = [("B1", CONTROL), ("B2", CONTROL), ("B1", TWIN), ("B2", TWIN), (CONTROL, TWIN)]
SCENARIOS = ("all days", "without 2019-09-18")


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
        raise LookAheadError(f"direct_twin_449 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the pure parts -------------------------------------------------------------------------------------------------


def fitter(features: Sequence[str], **extra):
    """The fit of `gbm_funding` as `spread_distribution_634.py` builds it, with `extra` (the twin's `training_pairs`)."""

    return functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID, **extra
    )


def settings_of(document: Mapping) -> Mapping:
    """A walk's recorded fit settings. `spread_distribution_634.py walk` writes them with `default=str`, so a mapping
    proxy is stored as the text of its dict; both forms are read."""

    settings = document.get("settings", {})
    if isinstance(settings, str):
        settings = ast.literal_eval(settings)
    if not isinstance(settings, Mapping):
        raise ValueError(f"the walk's settings are not a mapping: {settings!r}")
    return settings


def check_pairing(control: Mapping, twin: Mapping) -> None:
    """The control is fitted on one-step pairs and the twin on direct pairs, as the walks' own settings say."""

    if "training_pairs" in settings_of(control):
        raise ValueError(f"the control walk names training_pairs {settings_of(control)['training_pairs']!r}; it must be unset")
    if settings_of(twin).get("training_pairs") != "direct":
        raise ValueError("the twin walk does not name training_pairs 'direct'")


def without_excluded(days: Sequence[date]) -> List[date]:
    return [day for day in days if day != EXCLUDED_DAY]


def lead_series(cells: Mapping[Tuple[date, int], float], lead: int) -> Dict[date, float]:
    """The decision-day series of one lead's cells."""

    return {day: value for (day, h), value in cells.items() if h == lead}


# -- the twin's walks -----------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    h = args.horizon
    if h not in sd.HORIZONS:
        raise SystemExit(f"horizon {h} is not a protocol lead")
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="direct_twin_449")
    if sd.finished_walk(args.output, variant=TWIN, horizon=h, published=args.published, panel=args.published):
        print(json.dumps({"variant": TWIN, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    live = sd._load("live_record")
    features = tuple(live.published_features(h))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    result, levels, settings = sd.walk(
        rows, fit=fitter(features, training_pairs="direct"), features=features, online_calibration=None, registry=registry,
        horizon=h, minimum_history=61, refit_every=21, expected_levels=GRID,
    )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": TWIN,
        "horizon": h,
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
    print(json.dumps({"variant": TWIN, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- scoring --------------------------------------------------------------------------------------------------------


def _paired_job(job):
    """One `paired_tests` call in a worker: `(key, [(benchmark series, candidate series)], draws)` to `(key, rows)`."""

    key, chosen, draws = job
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return key, [_summarise(test) for test in tests]


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


def load_walks(directory: Path, published: Path) -> Dict[str, Dict[int, Dict[date, Optional[List[float]]]]]:
    """Both models' walks at the five leads, checked: same panel, the control on one-step and the twin on direct pairs."""

    sd = _load("spread_distribution_634")
    digest = panel_sha256(published)
    for h in HORIZONS:
        documents = {n: json.loads((directory / f"{n}_h{h}.json").read_text(encoding="utf-8")) for n in MODELS}
        for name, document in documents.items():
            if document["panel_sha256"] != digest:
                raise ValueError(f"{name} lead {h} was walked on another published panel")
        check_pairing(documents[CONTROL], documents[TWIN])
        if documents[CONTROL]["features"] != documents[TWIN]["features"]:
            raise ValueError(f"lead {h}: the control and the twin read different features")
    return {name: sd.load_laws(directory, name) for name in MODELS}


def score_command(args) -> int:
    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="direct_twin_449")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    walks = load_walks(args.walks, args.published)
    pairing = {
        name: {
            str(h): settings_of(json.loads((args.walks / f"{name}_h{h}.json").read_text(encoding="utf-8"))).get("training_pairs", "unset (one-step)")
            for h in HORIZONS
        }
        for name in MODELS
    }
    decisions, days_by_name = {}, {}
    for name, laws in walks.items():
        decisions[name], days_by_name[name] = sd.lead_forecasts(laws, calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by_name.values())))
    common = [day for day in common if all(calendar[position[day] + h] <= LAST_TARGET for h in HORIZONS)]
    sd.refuse_locked(common + [calendar[position[day] + h] for day in common for h in HORIZONS])
    usable, unbuilt = [], []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=sd.DECISION)
            pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=sd.DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError as error:
            unbuilt.append((day.isoformat(), str(error)))
    common = usable
    if not common:
        raise SystemExit("no decision day has both walks and both benchmarks")
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=sd.DECISION, splits=splits)
    forecasts = {"B1": b1, "B2": b2}
    missing = {}
    for name in MODELS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = ["B1", "B2", *MODELS]
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    cells = {n: sd.cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in names}
    kinds = sorted({splits.reporting_day_type(calendar[position[d] + h], row_of[calendar[position[d] + h]].values) for d in days for h in HORIZONS})

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    def series(group: Sequence[date], lead: Optional[int], kind: Optional[str]) -> Dict[str, Dict[date, float]]:
        keep = set(group)
        include = lambda d, h: d in keep and (lead is None or h == lead) and (kind is None or kind_of(calendar[position[d] + h]) == kind)
        return {n: sd.day_means(cells[n], include) for n in names}

    jobs, shells = [], {}
    for scenario in SCENARIOS:
        scored = days if scenario == SCENARIOS[0] else without_excluded(days)
        groups = {"all": scored}
        for label in splits.regime_labels:
            groups[f"regime {label}"] = [d for d in scored if splits.regime(d) == label]
        for group_name, group in groups.items():
            for kind in (None, *kinds):
                for lead in (None, *HORIZONS):
                    means = series(group, lead, kind)
                    common_days = sorted(set.intersection(*(set(m) for m in means.values())) & set(group))
                    key = (scenario, group_name, kind or "all", lead or "pooled")
                    # the cross of a regime and a day type is not a declared table
                    if group_name != "all" and kind is not None:
                        continue
                    entry = {"n": len(common_days), "mean": {n: sum(means[n][d] for d in common_days) / len(common_days) for n in names} if common_days else {}}
                    if len(common_days) < MINIMUM_DAYS or len(common_days) <= sp.HAC_LAG:
                        entry["thin"] = True
                    else:
                        headline = group_name == "all" and kind is None
                        jobs.append((key, [({d: means[b][d] for d in common_days}, {d: means[c][d] for d in common_days}) for b, c in PAIRS],
                                     HEADLINE_DRAWS if headline else SPLIT_DRAWS))
                    shells[key] = entry
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, results in pool.map(_paired_job, jobs):
            shells[key]["tests"] = {f"{b} -> {c}": row for (b, c), row in zip(PAIRS, results)}
    tables: Dict[str, dict] = {}
    for (scenario, group, kind, lead), entry in shells.items():
        tables.setdefault(scenario, {}).setdefault(group, {}).setdefault(kind, {})[str(lead)] = entry
    document = {
        "declaration": "metadata/direct_twin_449.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "seed": SEED,
        "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS},
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "excluded_day_scores": {n: primary[n].get(EXCLUDED_DAY) for n in names},
        "decision_days_without_a_benchmark": unbuilt,
        "missing": missing,
        "pairing": pairing,
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


def table(title: str, scenario_tables: Mapping[str, dict], group: str, kind: str, leads: Sequence[str]) -> List[str]:
    if not any(scenario_tables[group][kind][lead]["mean"] for lead in leads):
        return []
    lines = [f"### {title}", "", "| lead | days | B1 | B2 | gbm | twin | gbm vs B1 | twin vs B1 | gbm vs B2 | twin vs B2 | twin vs gbm |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for lead in leads:
        entry = scenario_tables[group][kind][lead]
        mean = entry["mean"]
        if not mean:
            continue
        lines.append(
            f"| {lead} | {entry['n']} | " + " | ".join(fmt(mean[n], 2) for n in ("B1", "B2", CONTROL, TWIN)) + " | "
            + " | ".join(pair_cell(entry, f"{b} -> {c}") for b, c in (("B1", CONTROL), ("B1", TWIN), ("B2", CONTROL), ("B2", TWIN), (CONTROL, TWIN)))
            + " |"
        )
    return lines + [""]


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    leads = ["pooled", *map(str, HORIZONS)]
    out = [
        "# gbm_funding against its direct-pairs twin (#449, H5)",
        "",
        "Development data, a measurement and never a verdict (scoring protocol v1). Nothing is published or registered; the declared candidate,",
        "the published model and every published figure are as they were. Declaration: `metadata/direct_twin_449.json`.",
        "",
        f"Decision days {score['decision_days']['first']} to {score['decision_days']['last']} ({score['decision_days']['n']}). Panel `{score['panel_sha256'][:12]}…`.",
        "Grid CRPS in bp (lower is better). A cell is the skill of the second forecast over the first named benchmark (positive favours the second), with the one-sided",
        "95% lower and upper bounds of skill from the studentized stationary bootstrap, as `[lower, upper]` (block 10, seed 449; "
        f"{score['draws']['headline']:,} draws on pooled and per-lead figures, {score['draws']['splits']:,} on splits).",
        "",
        "## How each model is fitted (read from the walks' own settings)",
        "",
    ]
    for name, by_lead in score["pairing"].items():
        out.append(f"- `{name}`: training_pairs = {', '.join(sorted(set(by_lead.values())))} at every lead")
    out += [
        "",
        "Confirmed in code (acceptance 1): `ml.fit_gradient_boosted_quantiles` with `training_pairs` unset trains each target on the row before it, so every",
        "regressor of a training row sits one row before its target; the walk (`spread_distribution_634.walk`) reads the model at the as-of read of the",
        "decision instant at the lead (`asof.InformationRule(horizon=h)`), where the spread sits h + 1 rows before the target. The twin trains each target on its",
        "own as-of read at the same lead (`_direct_pairs`). The walks' recorded settings above are read, not assumed; the score refuses to run if the control",
        "names `training_pairs` or the twin does not name `direct`.",
    ]
    out.append("")
    out.append(
        f"Decision day {score['excluded_day']} scores (grid CRPS, mean over its five leads): "
        + ", ".join(f"{n} {fmt(v, 1)}" for n, v in score["excluded_day_scores"].items() if v is not None)
        + "."
    )
    out.append("")
    out += ["## The twin against the control, in one place", ""]
    for scenario in SCENARIOS:
        pooled = score["tables"][scenario]["all"]["all"]
        row = pooled["pooled"]["tests"][f"{CONTROL} -> {TWIN}"]
        by_lead = {lead: pooled[lead]["tests"][f"{CONTROL} -> {TWIN}"] for lead in map(str, HORIZONS)}
        worse = [lead for lead, r in by_lead.items() if r["skill_upper_95_one_sided"] < 0]
        ahead = [lead for lead, r in by_lead.items() if r["skill_lower_95_one_sided"] > 0]
        out.append(
            f"- {scenario}: pooled over leads the twin's skill over the control is {100 * row['skill']:+.1f}% "
            f"[{100 * row['skill_lower_95_one_sided']:+.1f}, {100 * row['skill_upper_95_one_sided']:+.1f}] "
            f"(mean grid CRPS {fmt(row['benchmark_mean'], 3)} bp for the control); leads where the whole interval is below zero (twin worse): "
            f"{', '.join(worse) or 'none'}; leads where it is above zero (twin ahead): {', '.join(ahead) or 'none'}."
        )
    out.append("")
    for scenario in SCENARIOS:
        tables = score["tables"][scenario]
        out += [f"## {scenario}", ""]
        out += table("Pooled over leads and each lead alone", tables, "all", "all", leads)
        for kind in score["kinds"]:
            out += table(f"Target-day type: {kind}", tables, "all", kind, leads)
        for label in score["regimes"]:
            out += table(f"Regime of the decision day: {label}", tables, f"regime {label}", "all", leads)
    out += [
        "## Question for Eleonora (marked; this PR settles nothing)",
        "",
        "Does the declared candidate switch to the direct-pairs twin? The measurement above is development evidence, not a verdict, and changes no published model.",
        "",
    ]
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="walk the twin at one lead")
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    score = sub.add_parser("score", help="score both models against B1 and B2 and each other")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    report = sub.add_parser("report", help="render the Markdown page")
    report.add_argument("score", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
