"""The ordinary-day P(spread > +5 bp) of H5's spread models against persistence-logistic (#844; H5 step 3, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/exploration_844.json`, which this script refuses to read unless it is committed and
unchanged. It adds no variant: each row is the walk-forward law of a model that already exists, with P(spread > 5 bp)
read off its 23 quantiles. Scored target days end on 2025-12-31 and no later day is read (`docs/decisions/lockbox.md`).
Nothing here is a verdict (scoring protocol v1, #640): it is exploration on development data.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    # the scratch panel AUG2D.csv and the #634 walks (c_two_part_new and gbm_funding at each lead, and the persistence-logistic
    # exceedance at each lead) are built by the commands in the docstring of scripts/spread_distribution_634.py, into WALKS/
    PYTHONPATH=src python3 scripts/ordinary_day_p5_844.py cells --panel PUBLISHED.csv --walks WALKS --output CELLS.json
    PYTHONPATH=src python3 scripts/ordinary_day_p5_844.py score --cells CELLS.json --output score.json --markdown report.md
    PYTHONPATH=src python3 scripts/ordinary_day_p5_844.py page --score score.json --output docs/pivot/ordinary-day-p5-result.md

The bootstrap is pure Python (a logistic fit per resample), so `score --workers` spreads the cells over processes; a cell's
resample stream is seeded by its lead, regime and definition, so the figures do not depend on the number of workers.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script_844", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script_844"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import protocol_benchmarks as pb, risk_dates  # noqa: E402
from repo_model import reliability_regimes as rr  # noqa: E402
from repo_model import spread_mean_reversion as smr  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402
from repo_model import lockbox  # noqa: E402

DECLARATION = REPO / "metadata" / "exploration_844.json"
LAST_DAY = date(2025, 12, 31)
TAU = 5.0
HORIZONS = (1, 2, 3, 4, 5)
MODEL_ROWS = ("spread_mr_level10", "spread_mr_ctx", "c_two_part_new", "gbm_funding")
REFERENCE = "persistence_logistic"
RAW = "as_of_spread"
LABELS = {
    "spread_mr_level10": "mean reversion (#686)",
    "spread_mr_ctx": "(i) context-pooled residuals (#761)",
    "c_two_part_new": "(c) two-part (#634)",
    "gbm_funding": "gbm_funding (#634)",
    REFERENCE: "persistence-logistic",
    RAW: "raw as-of spread",
}
DEFINITIONS = {"non_ordinary": risk_dates.NON_ORDINARY, "scheduled": risk_dates.SCHEDULED}
CELLS = ("pooled",) + tuple(label for label, _, _ in rr.REGIMES)
MINIMUM_PRESSURE_DAYS = 3
LEVEL, BLOCK, REPLICATIONS = 0.90, 10, 2000
MAX_UNDEFINED_SHARE = rr.MAX_UNDEFINED_SHARE


# -- the declaration and the scope ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_scored_days(days, last: date = LAST_DAY) -> None:
    """Refuse a day after `last`, the declared end of the scored days, and a locked day.

    Mutation record: replacing `if day > last:` with `if day > last + timedelta(days=400):` makes
    `test_ordinary_day_p5_844_script.ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError`
    ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > last:
            raise LookAheadError(f"{day} is after {last}, the last day #844 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/ordinary_day_p5_844")


# -- the metrics ---------------------------------------------------------------------------------------------------


def auroc(scores: Sequence[float], outcomes: Sequence[int]) -> Optional[float]:
    """The probability that a pressure day scores above a day that is not one, ties half; `None` with no day of either kind."""

    if len(scores) != len(outcomes):
        raise ValueError("scores and outcomes differ in length")
    events = sum(outcomes)
    others = len(outcomes) - events
    if events == 0 or others == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rank_sum = 0.0
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        average = (i + j) / 2.0 + 1.0
        rank_sum += average * sum(outcomes[order[k]] for k in range(i, j + 1))
        i = j + 1
    return (rank_sum - events * (events + 1) / 2.0) / (events * others)


def brier(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    if len(probabilities) != len(outcomes) or not outcomes:
        raise ValueError("probabilities and outcomes must be non-empty and of one length")
    return sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


def metrics(name: str, scores: Sequence[float], outcomes: Sequence[int], *, fit: bool = True) -> Dict[str, Optional[float]]:
    """One row's metrics on one set of days: the AUROC always; for a probability, the Brier score and the reliability line."""

    out: Dict[str, Optional[float]] = {"auroc": auroc(scores, outcomes)}
    if name == RAW:
        return out
    out["brier"] = brier(scores, outcomes)
    line = rr.fit(scores, outcomes) if fit else None
    out["slope"] = None if line is None else line.slope
    out["intercept"] = None if line is None else line.intercept
    return out


def _percentile(draws: List[float], probability: float) -> float:
    return rr._percentile(sorted(draws), probability)


def interval(draws: Sequence[Optional[float]], replications: int, level: float = LEVEL) -> Optional[List[float]]:
    """The percentile interval of the defined draws; `None` where more than `MAX_UNDEFINED_SHARE` of the resamples are undefined."""

    kept = [d for d in draws if d is not None]
    if len(draws) - len(kept) > MAX_UNDEFINED_SHARE * replications or not kept:
        return None
    tail = (1.0 - level) / 2.0
    return [_percentile(kept, tail), _percentile(kept, 1.0 - tail)]


def cell_result(
    columns: Mapping[str, Sequence[float]], outcomes: Sequence[int], *, seed: int, replications: int = REPLICATIONS,
    block_length: float = BLOCK, level: float = LEVEL,
) -> dict:
    """Every row's metrics on the cell's days, with paired stationary-bootstrap intervals against persistence-logistic.

    `columns` maps a row to its forecast on the cell's days, in date order; it holds `REFERENCE` and may hold `RAW`.
    A cell with fewer than `MINIMUM_PRESSURE_DAYS` pressure days reports no AUROC, slope or intercept (Eleonora's #710 minimum):
    its Brier score and counts remain. A slope has an interval only with at least 5 pressure days and 5 other days.
    """

    n, events = len(outcomes), int(sum(outcomes))
    if REFERENCE not in columns:
        raise ValueError("the reference row is missing")
    for name, column in columns.items():
        if len(column) != n:
            raise ValueError(f"{name} has {len(column)} days, the cell {n}")
    event_based = events >= MINIMUM_PRESSURE_DAYS
    fit_ok = event_based and events >= rr.DEFAULT_MINIMUM_EVENTS and n - events >= rr.DEFAULT_MINIMUM_EVENTS
    result = {"days": n, "pressure_days": events, "rows": {}}
    point = {}
    for name, column in columns.items():
        m = metrics(name, column, outcomes)
        if not event_based:
            for key in ("auroc", "slope", "intercept"):
                if key in m:
                    m[key] = None
        point[name] = m
    draws: Dict[str, Dict[str, List[Optional[float]]]] = {
        name: {key: [] for key in point[name]} for name in columns
    }
    if n and event_based:
        rng = random.Random(seed)
        for _ in range(replications):
            idx = stationary_bootstrap_indices(n, block_length, rng)
            y = [outcomes[i] for i in idx]
            for name, column in columns.items():
                resample = [column[i] for i in idx]
                m = metrics(name, resample, y, fit=fit_ok)
                for key in draws[name]:
                    draws[name][key].append(m.get(key))
    for name in columns:
        row: Dict[str, object] = {}
        for key, value in point[name].items():
            entry: Dict[str, object] = {"value": value, "interval": None}
            if n and event_based and (key in ("auroc", "brier") or fit_ok):
                entry["interval"] = interval(draws[name][key], replications, level)
            row[key] = entry
            if name != REFERENCE and key in point[REFERENCE]:
                a, b = value, point[REFERENCE][key]
                paired = [
                    None if x is None or r is None else x - r
                    for x, r in zip(draws[name][key], draws[REFERENCE][key])
                ] if draws[name][key] else []
                row[f"{key}_minus_reference"] = {
                    "value": None if a is None or b is None else a - b,
                    "interval": interval(paired, replications, level) if paired and (key in ("auroc", "brier") or fit_ok) else None,
                }
        result["rows"][name] = row
    return result


# -- the cells -----------------------------------------------------------------------------------------------------


def assemble(panel_path: Path, walks: Path, declaration: dict) -> dict:
    """The rows' P(> 5 bp) on every (lead, target day) they all cover, with the outcome, the regime and the ordinary-day flags."""

    s686 = _load("spread_mean_reversion_686")
    s761 = _load("spread_mr_variants_761")
    s634 = _load("spread_distribution_634")
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    frame, notes, _ = s761.build_frame(panel, splits, registry, s761.committed_declaration())
    require_scored_days(frame.days)
    values = {row.date: row.values for row in panel}
    spreads = {row.date: row.spread_bps for row in panel}
    calendar = [row.date for row in panel]
    per_lead: Dict[int, Dict[date, dict]] = {h: {} for h in HORIZONS}
    for d in frame.days:
        anchor = pb._anchor(panel, frame.position[d], registry, s761.DECISION_TIME)
        for h in HORIZONS:
            target = frame.target(d, h)
            per_lead[h][target] = {
                "spread_mr_level10": smr.exceedance(frame.forecasts["spread_mr_level10"][d][h], TAU),
                "spread_mr_ctx": smr.exceedance(frame.forecasts["spread_mr_ctx"][d][h], TAU),
                RAW: float(panel[anchor].spread_bps),
            }
    laws = {name: s634.load_laws(walks, name) for name in ("c_two_part_new", "gbm_funding")}
    result = {"horizons": {}, "panel_sha256": panel_sha256(panel_path), "decision_days": len(frame.days), "notes": notes, "walks": {}}
    for h in HORIZONS:
        bench = json.loads((walks / f"exceed_h{h}.json").read_text(encoding="utf-8"))
        pl = bench["forecasts"][REFERENCE][f"{TAU:g}"]
        for name, law in laws.items():
            for target, quantiles in law[h].items():
                cell = per_lead[h].get(target)
                if cell is not None and quantiles is not None:
                    cell[name] = s634.exceedance(quantiles, TAU)
        for target, cell in per_lead[h].items():
            value = pl.get(target.isoformat())
            if value is not None:
                cell[REFERENCE] = float(value)
        needed = set(MODEL_ROWS) | {REFERENCE, RAW}
        days = sorted(t for t, cell in per_lead[h].items() if needed <= set(cell) and t in spreads)
        require_scored_days(days)
        rows = []
        for t in days:
            flags = {
                key: not risk_dates.is_risk_date(values[t], definition, splits=splits, reporting_on=t)
                if definition == risk_dates.NON_ORDINARY else not risk_dates.is_risk_date(values[t], definition)
                for key, definition in DEFINITIONS.items()
            }
            rows.append({
                "day": t.isoformat(), "y": int(exceeds_bp(spreads[t], TAU)), "regime": rr.regime_of(t),
                "ordinary": flags, "p": {name: per_lead[h][t][name] for name in sorted(needed)},
            })
        result["horizons"][str(h)] = rows
        result["walks"][str(h)] = {name: len(law[h]) for name, law in laws.items()}
    return result


def cells_command(args) -> int:
    declaration = committed_declaration()
    out = assemble(Path(args.panel), Path(args.walks), declaration)
    Path(args.output).write_text(json.dumps(out, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cells": {h: len(r) for h, r in out["horizons"].items()}}))
    return 0


# -- the scores ----------------------------------------------------------------------------------------------------


def _job(job):
    key, columns, outcomes, seed, replications = job
    return key, cell_result(columns, outcomes, seed=seed, replications=replications)


def score_command(args) -> int:
    declaration = committed_declaration()
    document = json.loads(Path(args.cells).read_text(encoding="utf-8"))
    replications = args.replications or declaration["interval"]["replications"]
    jobs = []
    counts = {}
    for definition_index, definition in enumerate(DEFINITIONS):
        for h in HORIZONS:
            rows = document["horizons"][str(h)]
            require_scored_days(date.fromisoformat(r["day"]) for r in rows)
            for cell_index, cell in enumerate(CELLS):
                kept = [r for r in rows if r["ordinary"][definition] and (cell == "pooled" or r["regime"] == cell)]
                if not kept:
                    continue
                names = sorted(kept[0]["p"])
                columns = {name: [r["p"][name] for r in kept] for name in names}
                seed = 844 * 1000 + 100 * h + 10 * cell_index + 5 * definition_index
                jobs.append(((definition, h, cell), columns, [r["y"] for r in kept], seed, replications))
                counts[(definition, h, cell)] = len(kept)
    if args.workers == 1:
        done = dict(_job(job) for job in jobs)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            done = dict(pool.map(_job, jobs))
    result: Dict[str, dict] = {}
    for (definition, h, cell), body in done.items():
        result.setdefault(definition, {}).setdefault(str(h), {})[cell] = body
    out = {
        "issue": 844, "level": LEVEL, "block_length": BLOCK, "replications": replications, "panel_sha256": document["panel_sha256"],
        "decision_days": document["decision_days"], "walks": document["walks"], "definitions": result,
    }
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(render_report(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cells": len(done)}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------


def fmt(entry: Optional[dict], places: int = 3, signed: bool = False) -> str:
    if entry is None or entry["value"] is None:
        return "n/a"
    text = f"{entry['value']:+.{places}f}" if signed else f"{entry['value']:.{places}f}"
    if entry["interval"] is None:
        return text + "†"
    lo, hi = entry["interval"]
    return f"{text} [{lo:+.{places}f}, {hi:+.{places}f}]" if signed else f"{text} [{lo:.{places}f}, {hi:.{places}f}]"


def sign_of(entry: Optional[dict]) -> Optional[str]:
    """`above`, `covers` or `below` zero for a paired difference's interval; `None` where it has none."""

    if entry is None or entry["interval"] is None:
        return None
    lo, hi = entry["interval"]
    return "above" if lo > 0 else "below" if hi < 0 else "covers"


def kill_lines(result: dict, definition: str = "non_ordinary") -> List[str]:
    """One line per row: the regime-by-lead cells (with enough pressure days) whose paired AUROC difference is above, covering or below zero."""

    lines = []
    for name in MODEL_ROWS:
        tally = {"above": 0, "covers": 0, "below": 0}
        counted = 0
        for h in map(str, HORIZONS):
            for cell in CELLS[1:]:
                body = result["definitions"][definition].get(h, {}).get(cell)
                if body is None or body["pressure_days"] < MINIMUM_PRESSURE_DAYS:
                    continue
                verdict = sign_of(body["rows"][name]["auroc_minus_reference"])
                if verdict is None:
                    continue
                tally[verdict] += 1
                counted += 1
        lines.append(
            f"- **{LABELS[name]}**: of {counted} regime-by-lead cells with at least {MINIMUM_PRESSURE_DAYS} pressure days and an interval, "
            f"the paired AUROC difference from persistence-logistic is above zero in {tally['above']}, covers zero in {tally['covers']} "
            f"and is below zero in {tally['below']}. Development, not a verdict."
        )
    return lines


def render_report(result: dict) -> str:
    level = round(result["level"] * 100)
    out = [
        "# Ordinary-day P(spread > +5 bp) against persistence-logistic (#844)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (evaluation): the \"no ordinary-day ranking gain\" half of H5's kill rule. "
        "**Development data only: this is not a verdict** (scoring protocol v1, #640). No day after 2025-12-31 is read, so the regime "
        "labelled 2025-26 holds the days of 2025. Declaration: `metadata/exploration_844.json`.", "",
        f"A cell is a target day at one lead. Each row's P(spread > +5 bp) is read off its own walk-forward law; persistence-logistic is the "
        f"project's own. Intervals are {level}% stationary-bootstrap percentile intervals (block {result['block_length']}, "
        f"{result['replications']} replications), paired: a difference is the row minus persistence-logistic on the same resamples. "
        "A higher AUROC and a lower Brier score are better; a reliability slope of 1 and an intercept of 0 are reliable. "
        "`n/a`: fewer than 3 pressure days (Eleonora's #710 minimum) or an undefined fit. `†`: no interval, because the cell has too few "
        "pressure days or too many resamples were undefined.", "",
    ]
    for definition, title in (
        ("non_ordinary", "Ordinary days: not a risk date under `risk_dates.NON_ORDINARY` (read at the target day)"),
        ("scheduled", "Sensitivity: not a risk date under `risk_dates.SCHEDULED` (the judge's grouping; #800 is open)"),
    ):
        out += [f"## {title}", ""]
        for h in map(str, HORIZONS):
            by_cell = result["definitions"][definition].get(h, {})
            out += [f"### Lead h = {h}", ""]
            for cell in CELLS:
                body = by_cell.get(cell)
                if body is None:
                    continue
                reference = body["rows"][REFERENCE]
                out += [
                    f"**{cell}**: {body['days']} days, {body['pressure_days']} pressure days.", "",
                    f"| row | AUROC | AUROC minus PL | Brier | Brier minus PL | slope | intercept |",
                    "|---|---|---|---|---|---|---|",
                ]
                for name in (REFERENCE,) + MODEL_ROWS + (RAW,):
                    r = body["rows"][name]
                    if name == RAW:
                        out.append(f"| {LABELS[name]} | {fmt(r['auroc'])} | {fmt(r.get('auroc_minus_reference'), signed=True)} | – | – | – | – |")
                    elif name == REFERENCE:
                        out.append(f"| {LABELS[name]} | {fmt(r['auroc'])} | – | {fmt(r['brier'], 4)} | – | {fmt(r['slope'], 2)} | {fmt(r['intercept'], 2, True)} |")
                    else:
                        out.append(
                            f"| {LABELS[name]} | {fmt(r['auroc'])} | {fmt(r['auroc_minus_reference'], signed=True)} | {fmt(r['brier'], 4)} | "
                            f"{fmt(r['brier_minus_reference'], 4, True)} | {fmt(r['slope'], 2)} | {fmt(r['intercept'], 2, True)} |"
                        )
                out.append("")
    out += ["## Against H5's ordinary-day kill clause (development)", "", *kill_lines(result), "",
            "These lines count cells; they set no threshold. What counts as a ranking gain is Eleonora's.", ""]
    return "\n".join(out)


def page_command(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    level = round(result["level"] * 100)
    lines = [
        "# Ordinary-day P(> +5 bp) against persistence-logistic: result (#844)", "",
        "**Hypothesis and step:** H5 (primary goal), research step 3 (evaluation). **Development data only: this is not a verdict** "
        "(scoring protocol v1, #640). Generated by `scripts/ordinary_day_p5_844.py page`; the evidence is in "
        "`docs/pivot/evidence/ordinary-day-p5-844/`. No day after 2025-12-31 is read.", "",
        f"P(spread > +5 bp) read off each model's walk-forward law, scored on ordinary target days against the project's "
        f"persistence-logistic, by regime and lead; {level}% stationary-bootstrap intervals, paired. The headline cells are the pooled "
        "ordinary days at leads 1 and 3 and the two target regimes at lead 1; every cell is in the report.", "",
    ]
    for h, cell in (("1", "pooled"), ("1", "2018-19"), ("1", "2025-26"), ("3", "pooled")):
        body = result["definitions"]["non_ordinary"].get(h, {}).get(cell)
        if body is None:
            continue
        lines += [f"**Lead {h}, {cell}**: {body['days']} days, {body['pressure_days']} pressure days.", "",
                  "| row | AUROC | AUROC minus PL | Brier minus PL | slope |", "|---|---|---|---|---|"]
        for name in MODEL_ROWS:
            r = body["rows"][name]
            lines.append(f"| {LABELS[name]} | {fmt(r['auroc'])} | {fmt(r['auroc_minus_reference'], signed=True)} | "
                         f"{fmt(r['brier_minus_reference'], 4, True)} | {fmt(r['slope'], 2)} |")
        lines.append("")
    lines += ["## Against H5's ordinary-day kill clause (development)", "", *kill_lines(result), ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("cells", help="assemble the rows' P(> 5 bp) on the shared target days")
    c.add_argument("--panel", required=True)
    c.add_argument("--walks", required=True)
    c.add_argument("--output", required=True)
    c.set_defaults(func=cells_command)
    s = sub.add_parser("score", help="score the cells with paired bootstrap intervals")
    s.add_argument("--cells", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--markdown")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--replications", type=int, help="override the declared replications (a smoke run; a record uses the declared number)")
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the short result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
