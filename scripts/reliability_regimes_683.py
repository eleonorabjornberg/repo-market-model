"""Reliability slopes within regimes (#683, finding #670): the page tables the pooled slopes hid.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given. Development data only (no day after
2025-12-31 is read, `docs/decisions/lockbox.md`); nothing here is a verdict. Serves H5 (calibration in 2018-19 and 2025-26) and H2.

    PYTHONPATH=src python3 scripts/reliability_regimes_683.py tracked --output OUT/tracked.json --markdown OUT/tracked.md
    PYTHONPATH=src python3 scripts/reliability_regimes_683.py kinked --published PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/kinked_h{h}.json' \\
        --output OUT/kinked.json --markdown OUT/kinked.md
    PYTHONPATH=src python3 scripts/reliability_regimes_683.py derived631 --published PUBLISHED.csv --rows 'OUT/v631_h{h}.json' \\
        --output OUT/derived631.json --markdown OUT/derived631.md
    PYTHONPATH=src python3 scripts/reliability_regimes_683.py spread632 --published PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/refs_h{h}.json' --rows 'OUT/sd_h{h}.json' \\
        --output OUT/spread632.json --markdown OUT/spread632.md

`kinked` needs only `bench_h?`, `both_h?` and `kinked_h?` (the benchmarks, the parent and #626's rows), not the risk-date, `pressure_track_q` or `satiation_587` files that
`scripts/kinked_626.py compare` also reads. Its cost is the bootstrap, a pure-Python logistic fit per resample (about 8 ms on 1,900 days), so `--workers` spreads the
rows over processes: about 26 minutes with 4 workers at the declared 2,000 replications. A cell's resample stream is seeded by its row and horizon, so the figures do not
depend on the number of workers (#753).

`tracked` reads the per-regime slopes already in a tracked evidence file (#624's `step2-off-risk-days.json`) and tabulates them: no
forecast is rebuilt, and the file carries points without intervals. `kinked` re-reads the forecast files of #626 (built by the commands in
`scripts/kinked_626.py`'s docstring), takes the same days as its `extras` (the days that are not risk dates) and fits the reliability line
with `repo_model.reliability_regimes`, pooled, per regime (2018-19, 2020-24, 2025-26) and per as-of scarcity state, each with a 90%
stationary-bootstrap interval of the judge's declaration. The pooled cell is there to be compared with the regimes, never read alone. `derived631` does the same for the two every-day rows of #631's page (`docs/pivot/derived-features-result.md`, Table M2) on the days
that page's slopes are read on, the days that are not risk dates as the model serves them (#785). Its forecasts are the files of `derived_features_631.py model`, whose
inputs are listed in that script's page. `spread632` does the same for the rows of #632's page
(`docs/pivot/spread-distribution-result.md`) on the days whose pressure-day type is ordinary, the days that page's slopes are read on (#786). Its
forecasts are rebuilt by the commands in the docstrings of `scripts/spread_distribution_632.py` and of the scripts that one points to.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model import reliability_regimes as rr  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

LAST_DAY = date(2025, 12, 31)
SPREAD632_TITLE = "Reliability slope within regimes, #632's rows on the ordinary days (#786)"
DERIVED631_TITLE = "Reliability slope within regimes, #631's rows on the ordinary days (#785)"
#: A fitted slope this large in size is a near-separated fit, not a reading.
UNSTABLE = 25.0
#: A cell with fewer pressure days than this is marked: its slope is a handful of events' worth.
FEW = 5
SPLITS = REPO / "metadata" / "evaluation_splits.json"
STEP2 = REPO / "docs" / "pivot" / "evidence" / "off-risk-day" / "step2-off-risk-days.json"

READING = (
    "Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the "
    "bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. "
    "Figures here are development, not a verdict."
)


def _script(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def _kinked():
    return _script("kinked_626")


# -- tracked: the points already in #624's evidence ----------------------------------------------------------------


def tracked_command(args) -> int:
    require_unlocked([LAST_DAY], where="reliability_regimes_683")
    data = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    out: Dict[str, dict] = {}
    for row, leads in data["rows"].items():
        out[row] = {
            h: {
                cell: {
                    "days": v["days"], "pressure_days": v["pressure_days"], "slope": v.get("slope"),
                    "positive_days": v.get("positive_days"), "pressure_days_on_zero": v.get("pressure_days_on_zero"),
                }
                for cell, v in body["cells"].items()
            }
            for h, body in leads.items()
        }
    result = {"source": str(Path(args.evidence).relative_to(REPO)) if Path(args.evidence).is_absolute() else str(args.evidence), "rows": out, "reading": READING}
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(tracked_text(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _slope_text(cell) -> str:
    if cell is None:
        return "–"
    if cell["pressure_days"] == 0:
        return "undefined"
    on_zero = cell.get("pressure_days_on_zero") or 0
    if cell["slope"] is None:
        # #801: a row that forecasts zero on every pressure day is uncalibrated, not a fit that "is not formed".
        if on_zero >= cell["pressure_days"]:
            return f"uncalibrated: zero on all {cell['pressure_days']}"
        return "–"
    if abs(cell["slope"]) > UNSTABLE:
        return "unstable"
    # #801: the fit keeps only days whose forecast is above RELIABILITY_FLOOR, so the mark counts the pressure days in the fit.
    mark = "†" if cell["pressure_days"] - on_zero < FEW else ""
    return f"{cell['slope']:.2f}{mark}"


def tracked_text(result: dict) -> str:
    columns = ["all", "regime 2018-19", "regime 2020", "regime 2021-23", "regime 2024", "regime 2025-26"]
    out = [
        "# Reliability slope by regime, from the tracked evidence of #624 (#683)", "",
        READING, "",
        f"Source: `{result['source']}`. Points only: that file carries no interval for a regime's slope. The slope is that of the logistic fit of "
        "the outcome on logit(forecast) on the days that are not risk dates where the forecast is above 1e-4 (1 is reliable); `undefined` is a regime with no pressure day; `–` a "
        "regime whose forecast is constant or whose fit is not formed; `uncalibrated: zero on all N` a regime whose forecast is zero (1e-4 or "
        "below) on all N pressure days, so no fit is formed and the row misses every event; `unstable` a near-separated fit (a slope beyond 25 in size); "
        "`†` a cell with fewer than 5 pressure days in the fit (the pressure days on forecasts above 1e-4, not all the cell's), whose slope is a handful "
        "of events' worth.", "",
    ]
    for row, leads in result["rows"].items():
        out += [
            f"## `{row}`", "",
            "| lead | " + " | ".join(c if c != "all" else "all days (pooled)" for c in columns) + " |",
            "|---|" + "---|" * len(columns),
        ]
        for h, cells in sorted(leads.items(), key=lambda kv: int(kv[0])):
            out.append(f"| {h} | " + " | ".join(_slope_text(cells.get(c)) for c in columns) + " |")
        out.append("")
    return "\n".join(out)


# -- kinked: #626's rows, refitted within regimes ------------------------------------------------------------------


def _run_rows(jobs, workers: int = 1, mp_context=None) -> Dict[object, dict]:
    """The cells of every job, in the order of `jobs`. Each cell's resample stream is seeded by its job, so the number of
    workers changes the time and nothing else (#753: the bootstrap is pure Python, about 8 ms a fit on 1,900 days, and it ran
    in one process)."""

    if workers < 1:
        raise ValueError(f"workers must be at least 1, got {workers}")
    if workers == 1 or len(jobs) < 2:
        return dict(rr.row_cells(job) for job in jobs)
    with ProcessPoolExecutor(max_workers=min(workers, len(jobs)), mp_context=mp_context) as pool:
        return dict(pool.map(rr.row_cells, jobs))


def kinked_command(args) -> int:
    k = _kinked()
    declared = k.declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="reliability_regimes_683")
    judge_script = k._load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    base = pj.load_declaration()
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in base.horizons}
    names = [
        "structural_liquidity", "structural_liquidity+h41", "structural_kinked_fitted", "structural_kinked_rolling",
        k.OFF, k.COMPARATOR, base.persistence, base.climatology,
    ]
    result: Dict[str, dict] = {}
    jobs = []
    for h in base.horizons:
        columns: Dict[str, Dict[str, float]] = {}
        for template in (args.bench, args.parents, args.rows):
            doc = json.loads(Path(template.format(h=h)).read_text())
            for name, column in doc["forecasts"].items():
                if name in names:
                    columns.setdefault(name, column[f"{base.primary:g}"])
        days = sorted(date.fromisoformat(d) for d in columns[base.climatology])
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=states[h])
        keep = [i for i, label in enumerate(grid.groups["risk_date"]) if label == "0"]
        outcome = [grid.outcomes[base.primary][i] for i in keep]
        regime = [rr.regime_of(days[i]) for i in keep]
        state = [f"scarcity state {grid.groups['scarcity_state'][i]}" for i in keep]
        for n in names:
            p = [columns[n][days[i].isoformat()] for i in keep]
            settings = dict(
                block_length=base.block_length, seed=base.seed + h, replications=args.replications or base.replications, level=base.level
            )
            jobs.append(((h, n), p, outcome, regime, state, settings))
        result[str(h)] = {"days": len(keep), "events": sum(outcome), "rows": {}}
        print(json.dumps({"horizon": h, "off_risk_days": len(keep)}), flush=True)
    for (h, n), cells in _run_rows(jobs, workers=args.workers).items():
        result[str(h)]["rows"][n] = cells
    out = {"level": base.level, "replications": args.replications or base.replications, "block_length": base.block_length, "reading": READING, "horizons": result}
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(kinked_text(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- spread632: #632's rows on the ordinary days -------------------------------------------------------------------


def merged_columns(documents, names, primary: float) -> Dict[str, Dict[str, float]]:
    """The probability column of each of `names` at `primary`, the first document that carries a name supplying it.

    A name no document carries is refused by name: a page's slope must not silently lose a row."""

    columns: Dict[str, Dict[str, float]] = {}
    for doc in documents:
        for name, column in doc["forecasts"].items():
            if name in names and f"{primary:g}" in column:
                columns.setdefault(name, column[f"{primary:g}"])
    missing = [n for n in names if n not in columns]
    if missing:
        raise ValueError(f"no forecast at {primary:g} for {missing}")
    return columns


def spread632_command(args) -> int:
    sd = _script("spread_distribution_632")
    declared = sd.declared_document()
    base = pj.load_declaration()
    require_unlocked([base.last_day], where="reliability_regimes_683")
    judge_script = sd._load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    names = sd.all_rows() + list(declared["references"]["pair_against"])
    replications = args.replications or base.replications
    result: Dict[str, dict] = {}
    jobs = []
    for h in declared["horizons"]:
        states = judge_script._scarcity_states(h, base.last_day)
        documents = [json.loads(Path(t.format(h=h)).read_text()) for t in (args.bench, args.risk, args.reference, args.parents, args.rows)]
        columns = merged_columns(documents, names, base.primary)
        days = sorted(date.fromisoformat(d) for d in columns[base.climatology])
        for n in names:
            if sorted(date.fromisoformat(d) for d in columns[n]) != days:
                raise ValueError(f"{n} at h = {h} is not on the shared grid")
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=states)
        keep = [i for i, label in enumerate(grid.groups["day_type"]) if label == "ordinary"]
        outcome = [grid.outcomes[base.primary][i] for i in keep]
        regime = [rr.regime_of(days[i]) for i in keep]
        state = [f"scarcity state {grid.groups['scarcity_state'][i]}" for i in keep]
        settings = dict(block_length=base.block_length, seed=base.seed + h, replications=replications, level=base.level)
        for n in names:
            jobs.append(((h, n), [columns[n][days[i].isoformat()] for i in keep], outcome, regime, state, settings))
        result[str(h)] = {"days": len(keep), "events": sum(outcome), "rows": {}}
        print(json.dumps({"horizon": h, "ordinary_days": len(keep)}), flush=True)
    for (h, n), cells in _run_rows(jobs, workers=args.workers).items():
        result[str(h)]["rows"][n] = cells
    out = {
        "level": base.level, "replications": replications, "block_length": base.block_length, "reading": READING,
        "title": SPREAD632_TITLE, "panel_sha256": panel_sha256(args.published), "horizons": result,
    }
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(kinked_text(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- derived631: #631's rows on the ordinary days -------------------------------------------------------------------


def shared_columns(documents, names, key: str, last: date) -> tuple:
    """The days every one of `names` forecasts, up to `last`, and each row's forecasts on them.

    `key` is the threshold column of the forecast files ("5" for +5 bp, as #631's files name it). A name no document carries is
    refused by name: a page's slope must not silently lose a row. The first document that carries a name supplies it."""

    columns: Dict[str, Dict[str, float]] = {}
    for doc in documents:
        for name, column in doc["forecasts"].items():
            if name in names and key in column:
                columns.setdefault(name, column[key])
    missing = [n for n in names if n not in columns]
    if missing:
        raise ValueError(f"no forecast at {key} for {missing}")
    days = sorted(d for d in map(date.fromisoformat, set.intersection(*(set(columns[n]) for n in names))) if d <= last)
    if not days:
        raise ValueError(f"{names} share no day up to {last}")
    return days, {n: [float(columns[n][d.isoformat()]) for d in days] for n in names}


def derived631_command(args) -> int:
    d631 = _script("derived_features_631")
    declared = d631._committed()
    base = pj.load_declaration()
    last = date.fromisoformat(d631.MODEL_TEST_LAST_DAY)
    require_unlocked([last], where="reliability_regimes_683")
    judge_script = d631._load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    _ss, ann = d631._modules()
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    by_date = {r.date: r for r in published}
    names = [d631.PARENT, d631.TEST]
    replications = args.replications or base.replications
    result: Dict[str, dict] = {}
    jobs = []
    for h in declared["model_test"]["scoring"]["horizons"]:
        days, columns = shared_columns([json.loads(Path(args.rows.format(h=h)).read_text())], names, "5", last)
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=judge_script._scarcity_states(h, base.last_day))
        # the days of Table M2: not a risk date as the model serves it (`ml._RiskDateDesign.member`), as `derived_features_631.py ordinary` keeps them
        keep = [i for i, day in enumerate(days) if not ann.risk_flag(splits, by_date[day].values, True)]
        days = [days[i] for i in keep]
        columns = {n: [columns[n][i] for i in keep] for n in names}
        outcome = [1 if exceeds_bp(by_date[day].spread_bps, d631.THRESHOLD_BP) else 0 for day in days]
        regime = [rr.regime_of(day) for day in days]
        state = [f"scarcity state {grid.groups['scarcity_state'][i]}" for i in keep]
        settings = dict(block_length=base.block_length, seed=base.seed + h, replications=replications, level=base.level)
        for n in names:
            jobs.append(((h, n), columns[n], outcome, regime, state, settings))
        result[str(h)] = {"days": len(days), "events": sum(outcome), "rows": {}}
        print(json.dumps({"horizon": h, "ordinary_days": len(days)}), flush=True)
    for (h, n), cells in _run_rows(jobs, workers=args.workers).items():
        result[str(h)]["rows"][n] = cells
    out = {
        "level": base.level, "replications": replications, "block_length": base.block_length, "reading": READING,
        "title": DERIVED631_TITLE, "panel_sha256": panel_sha256(args.published), "horizons": result,
    }
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(kinked_text(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _cells(d: Dict[str, dict]) -> Dict[str, rr.Cell]:
    return {
        key: rr.Cell(
            v["days"], v["events"], v["slope"], v["intercept"],
            None if v["slope_interval"] is None else tuple(v["slope_interval"]),
            None if v["intercept_interval"] is None else tuple(v["intercept_interval"]),
        )
        for key, v in d.items()
    }


def kinked_text(result: dict) -> str:
    out = [
        "# " + result.get("title", "Reliability slope within regimes, #626's rows on the days that are not risk dates (#683)"), "",
        READING, "",
        f"Intercept and slope of `logit P(y = 1) = intercept + slope * logit(p)` (1 and 0 for a reliable forecast), "
        f"{round(result['level'] * 100)}% stationary-bootstrap intervals (block length {result['block_length']}, {result['replications']} "
        "replications); `undefined` where the cell has no pressure day, the forecast is constant there or the fit has no maximum; no interval where the cell has too "
        "few events to give one. Regimes: 2018-19, 2020-24 (which holds 2021-23, with no pressure day) and 2025-26.", "",
    ]
    for h, body in sorted(result["horizons"].items(), key=lambda kv: int(kv[0])):
        out += [f"## h = {h}: {body['days']} days, {body['events']} above +5 bp", ""]
        for row, split in body["rows"].items():
            out += [f"### `{row}`", "", "By regime.", "", rr.markdown_table(_cells(split["regime"]), level=result["level"]),
                    "By as-of scarcity state.", "", rr.markdown_table(_cells(split["scarcity_state"]), level=result["level"])]
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("tracked")
    p.add_argument("--evidence", type=Path, default=STEP2)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("kinked")
    p.add_argument("--published", type=Path, required=True)
    for name in ("bench", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1), help="processes for the bootstrap (the cells do not depend on it)")
    p.add_argument("--replications", type=int, help="override the declaration's bootstrap replications (a smoke run; a record uses the declared number)")
    p = sub.add_parser("spread632")
    p.add_argument("--published", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1), help="processes for the bootstrap (the cells do not depend on it)")
    p.add_argument("--replications", type=int, help="override the declaration's bootstrap replications (a smoke run; a record uses the declared number)")
    p = sub.add_parser("derived631")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--rows", required=True, help="the forecast files of `derived_features_631.py model`, with {h}")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1), help="processes for the bootstrap (the cells do not depend on it)")
    p.add_argument("--replications", type=int, help="override the declaration's bootstrap replications (a smoke run; a record uses the declared number)")
    args = parser.parse_args(argv)
    return {"tracked": tracked_command, "kinked": kinked_command, "spread632": spread632_command, "derived631": derived631_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
