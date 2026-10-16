"""H5's calibration after reserve-management purchases began (#845, avenue #835; H5 step 3, development tier).

A scratch measurement, not a record: it fits and changes no model, writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`. Every choice is in `metadata/exploration_845.json`, which this script refuses to read unless it is
committed and unchanged. It reads H5's predictive laws, unchanged, on ordinary target days: mean reversion (#686), #761's
variant (i), and #634's variant (c) and `gbm_funding`, with `persistence_logistic` as the reference. For two stretches (2025-12-12
to the last development day, and 2019-10-15 to 2020-02-28) it reports by lead the mean P(spread > +5 bp) against the realised
share, with a 90% stationary-bootstrap interval (block 10), and splits the error into a level part and a residual-pool part.

The last day is `repo_model.exploration.EXPLORATORY_END` (2026-09-03): the near-blind tier the lockbox opened on 2026-10-05,
read as development days (`repo_model.exploration.panel_end`; a later or locked day raises `LookAheadError` and the run stops,
`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640). Eleonora's ruling on #710 keeps a minimum of
3 pressure days per (stretch, lead) cell: a cell under it has only its counts in the tracked score and on the page; its figures
go to the `--withheld` file, which is not tracked.

    # PUBLISHED.csv and AUG2D.csv are built exactly as in the docstring of scripts/spread_distribution_634.py
    for h in 1 2 3 4 5: for v in gbm_funding c_two_part_new:
        PYTHONPATH=src python3 scripts/calibration_reserve_mgmt_845.py walk --variant $v --horizon $h \\
            --published PUBLISHED.csv --panel AUG2D.csv --output OUT/${v}_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/calibration_reserve_mgmt_845.py exceedance --horizon $h \\
        --published PUBLISHED.csv --output OUT/exceed_h$h.json
    PYTHONPATH=src python3 scripts/calibration_reserve_mgmt_845.py score --published PUBLISHED.csv --walks OUT \\
        --output docs/pivot/evidence/calibration-reserve-mgmt-845/score.json --withheld OUT/withheld.json
    PYTHONPATH=src python3 scripts/calibration_reserve_mgmt_845.py page \\
        --score docs/pivot/evidence/calibration-reserve-mgmt-845/score.json --output docs/pivot/calibration-reserve-mgmt-845-result.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr  # noqa: E402
from repo_model import spread_mr_variants as var  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, panel_end, require_exploratory_window  # noqa: E402
from repo_model.metrics import _quantile  # noqa: E402

DECLARATION = REPO / "metadata" / "exploration_845.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
WHERE = "scripts/calibration_reserve_mgmt_845"
DECISION_TIME = time(16, 0)
HORIZONS = sp.HORIZONS
TAU = 5.0
SEED = 845
BLOCK = 10
INTERVAL = (0.05, 0.95)
MINIMUM_PRESSURE_DAYS = 3
MEDIAN_AT = sp.GRID.index(0.5)
#: the two #634 laws walked here; each has a walk file per lead.
WALKED = ("gbm_funding", "c_two_part_new")
MR, CTX, PERSISTENCE = var.REFERENCE, "spread_mr_ctx", "persistence_logistic"
#: every law in table order, and the label each carries on the page.
LAWS = (MR, CTX, "c_two_part_new", "gbm_funding", PERSISTENCE)
LABELS = {MR: "mean reversion (#686)", CTX: "variant (i) (#761)", "c_two_part_new": "(c) two-part (#634)",
          "gbm_funding": "gbm_funding (#634)", PERSISTENCE: "persistence-logistic"}
#: the laws with a 23-quantile distribution, which can be decomposed.
DISTRIBUTIONS = (MR, CTX, "c_two_part_new", "gbm_funding")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


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


def last_day(value: Optional[str]) -> date:
    """The last day this script reads: `EXPLORATORY_END`, or an earlier `--end`.

    Raises:
        LookAheadError: a day after `EXPLORATORY_END`, or in a tier the lockbox still locks.
    """

    return panel_end(value, EXPLORATORY_END, where=WHERE)


def stretches(path: Path = DECLARATION) -> Dict[str, Tuple[date, date]]:
    """The two declared stretches by target day: name -> (first, last)."""

    document = json.loads(path.read_text(encoding="utf-8"))["stretches"]
    return {
        name: (date.fromisoformat(entry["first_target_day"]), date.fromisoformat(entry["last_target_day"]))
        for name, entry in document.items()
    }


def stretch_parts(path: Path = DECLARATION) -> List[Tuple[str, date, date]]:
    """Every row of the report in order: each stretch, then the declared parts of the earlier case."""

    document = json.loads(path.read_text(encoding="utf-8"))["stretches"]
    out = []
    for name, (first, last) in stretches(path).items():
        out.append((name, first, last))
        for label, (low, high) in document[name].get("parts", {}).items():
            out.append((f"{name}: {label}", date.fromisoformat(low), date.fromisoformat(high)))
    return out


def in_stretch(day: date, first: date, last: date) -> bool:
    """Whether the target day `day` belongs to the stretch (inclusive at both ends)."""

    return first <= day <= last


def under_minimum(pressure_days: int, minimum: int = MINIMUM_PRESSURE_DAYS) -> bool:
    """Whether a (stretch, lead) cell has fewer pressure days than Eleonora's minimum (#710)."""

    return pressure_days < minimum


def tracked_cell(cell: Mapping, *, withheld: bool) -> dict:
    """The cell as the tracked score keeps it: whole, or only its counts when it is under the minimum."""

    if not withheld:
        return dict(cell)
    return {"cells": cell["cells"], "pressure_days": cell["pressure_days"], "withheld": True}


# -- the statistics ------------------------------------------------------------------------------------------------


def stationary_interval(series: Sequence[Sequence[float]], *, draws: int, seed: int, block: int = BLOCK) -> List[Tuple[float, float]]:
    """The 5th and 95th percentile of the mean of each series over `draws` stationary-bootstrap resamples.

    The series are resampled jointly (one set of indices per draw), in the order given, as a Politis-Romano stationary
    bootstrap with mean block length `block`: after each index the next is its successor (wrapping) with probability
    1 - 1/block and a fresh uniform index otherwise.

    Raises:
        ValueError: no series, an empty one, or series of unequal length.
    """

    if not series or not series[0]:
        raise ValueError("a bootstrap needs at least one non-empty series")
    n = len(series[0])
    if any(len(s) != n for s in series):
        raise ValueError("the series of a joint bootstrap must have one length")
    rng = random.Random(seed)
    restart = 1.0 / block
    means: List[List[float]] = [[] for _ in series]
    for _ in range(draws):
        i = rng.randrange(n)
        indices = []
        while len(indices) < n:
            indices.append(i)
            i = rng.randrange(n) if rng.random() < restart else (i + 1) % n
        for k, values in enumerate(series):
            means[k].append(sum(values[j] for j in indices) / n)
    return [(_quantile(sorted(m), INTERVAL[0]), _quantile(sorted(m), INTERVAL[1])) for m in means]


def decompose(laws: Sequence[Sequence[float]], outcomes: Sequence[float], tau: float = TAU) -> dict:
    """The error mean P - realised share split into a level part and a residual-pool part (declared in `metadata/exploration_845.json`).

    `delta` is the mean over the cells of (outcome - the law's median); `centred_mean_p` is the mean P of the same laws moved by
    `delta`, their shape unchanged. Level part = mean P - centred mean P; residual-pool part = centred mean P - realised share.

    Raises:
        ValueError: no cells, or a different number of laws and outcomes.
    """

    if not laws or len(laws) != len(outcomes):
        raise ValueError("a decomposition needs one law and one outcome per cell, and at least one cell")
    n = len(laws)
    mean_p = sum(smr.exceedance(q, tau) for q in laws) / n
    realised = sum(1.0 if exceeds_bp(y, tau) else 0.0 for y in outcomes) / n
    mean_median = sum(q[MEDIAN_AT] for q in laws) / n
    mean_outcome = sum(outcomes) / n
    delta = sum(y - q[MEDIAN_AT] for q, y in zip(laws, outcomes)) / n
    centred = sum(smr.exceedance([x + delta for x in q], tau) for q in laws) / n
    return {
        "mean_p": mean_p, "realised": realised, "error": mean_p - realised,
        "mean_median_bp": mean_median, "mean_outcome_bp": mean_outcome, "delta_bp": delta, "delta": delta,
        "centred_mean_p": centred, "level": mean_p - centred, "pool": centred - realised,
    }


# -- walks of #634, to the last day --------------------------------------------------------------------------------


def _stamp(output: Path, end: date) -> None:
    document = json.loads(output.read_text(encoding="utf-8"))
    document["last_target"] = end.isoformat()
    partial = output.with_name(output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(output)


def _refuse_other_end(output: Path, end: date) -> None:
    """A file already at `output` that was walked to another last day is not reused."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if isinstance(document, dict) and document.get("last_target") != end.isoformat():
        raise SystemExit(f"{output} was walked to {document.get('last_target')}, not {end}; use another directory")


def walk_command(args) -> int:
    """One of #634's walks (`spread_distribution_634.py walk`), unchanged, to the last day instead of 2025-12-31."""

    committed_declaration()
    if args.variant not in WALKED:
        raise SystemExit(f"{args.variant!r} is not walked here; the declared walks are {WALKED}")
    end = last_day(args.end)
    _refuse_other_end(args.output, end)
    s634 = _load("spread_distribution_634")
    s634.LAST_TARGET = end
    s634.walk_command(args)
    _stamp(args.output, end)
    return 0


def exceedance_command(args) -> int:
    """`persistence_logistic` and the calendar climatology (`spread_distribution_634.py exceedance`), to the last day."""

    committed_declaration()
    end = last_day(args.end)
    _refuse_other_end(args.output, end)
    s634 = _load("spread_distribution_634")
    s634.LAST_TARGET = end
    s634.exceedance_command(args)
    _stamp(args.output, end)
    return 0


# -- the cells -----------------------------------------------------------------------------------------------------


def mean_reversion_laws(panel, splits, registry) -> Dict[str, Dict[int, Dict[date, List[float]]]]:
    """Mean reversion's and variant (i)'s law of each target day at each lead: name -> lead -> target day -> 23 quantiles."""

    days = [row.date for row in panel]
    position = {day: i for i, day in enumerate(days)}
    decision_days = [day for i, day in enumerate(days) if i + max(HORIZONS) < len(days)]
    walk = var.walk(panel, decision_days, registry=registry, decision_time=DECISION_TIME, splits=splits, b2={})
    out: Dict[str, Dict[int, Dict[date, List[float]]]] = {MR: {h: {} for h in HORIZONS}, CTX: {h: {} for h in HORIZONS}}
    for name in (MR, CTX):
        for day, by_lead in walk.forecasts[name].items():
            for h in HORIZONS:
                if position[day] + h < len(days):
                    out[name][h][days[position[day] + h]] = [float(v) for v in by_lead[h]]
    return out


def read_walk_laws(directory: Path, panel_path: Path, end: date) -> Dict[str, Dict[int, Dict[date, Optional[List[float]]]]]:
    """#634's laws as `{name: {lead: {target day: quantiles or None}}}`, refused unless walked to `end`."""

    s634 = _load("spread_distribution_634")
    sha = panel_sha256(panel_path)
    for name in WALKED:
        for h in HORIZONS:
            document = json.loads((directory / f"{name}_h{h}.json").read_text(encoding="utf-8"))
            if document.get("last_target") != end.isoformat():
                raise ValueError(f"{name}_h{h}.json was walked to {document.get('last_target')}, not {end}")
            if document.get("panel_sha256") != sha:
                raise ValueError(f"{name}_h{h}.json was walked from another published panel")
    return {name: s634.load_laws(directory, name) for name in WALKED}


def read_persistence(directory: Path, panel_path: Path, end: date) -> Dict[int, Dict[date, float]]:
    """`persistence_logistic`'s P(spread > +5 bp) by lead and target day."""

    sha = panel_sha256(panel_path)
    out: Dict[int, Dict[date, float]] = {}
    for h in HORIZONS:
        document = json.loads((directory / f"exceed_h{h}.json").read_text(encoding="utf-8"))
        if document.get("last_target") != end.isoformat() or document.get("panel_sha256") != sha:
            raise ValueError(f"exceed_h{h}.json was not walked to {end} from this published panel")
        out[h] = {date.fromisoformat(day): p for day, p in document["forecasts"][PERSISTENCE][f"{TAU:g}"].items()}
    return out


def build_cell(rows: Sequence[dict], *, draws: int) -> dict:
    """One (stretch part, lead) cell from its rows (target-day order): `{day, outcome, event, p: {law: P}, q: {law: law}}`."""

    n = len(rows)
    events = [1.0 if row["event"] else 0.0 for row in rows]
    cell: dict = {"cells": n, "pressure_days": int(sum(events))}
    if not n:
        return cell
    series = [events]
    for name in LAWS:
        series.append([row["p"][name] for row in rows])
    for name in LAWS:
        series.append([row["p"][name] - e for row, e in zip(rows, events)])
    bounds = stationary_interval(series, draws=draws, seed=SEED)
    cell["realised"], cell["realised_interval"] = sum(events) / n, list(bounds[0])
    cell["laws"] = {}
    for k, name in enumerate(LAWS):
        mean_p = sum(row["p"][name] for row in rows) / n
        entry = {"mean_p": mean_p, "mean_p_interval": list(bounds[1 + k]), "error": mean_p - cell["realised"],
                 "error_interval": list(bounds[1 + len(LAWS) + k])}
        if name in DISTRIBUTIONS:
            parts = decompose([row["q"][name] for row in rows], [row["outcome"] for row in rows])
            entry.update({key: parts[key] for key in ("level", "pool", "delta_bp", "centred_mean_p", "mean_median_bp", "mean_outcome_bp")})
        cell["laws"][name] = entry
    return cell


def score_command(args) -> int:
    declared = committed_declaration()
    end = last_day(args.end)
    published = load_daily_panel(args.published)
    panel = [row for row in published if row.date <= end]
    require_exploratory_window([row.date for row in panel], where=WHERE)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    outcome = {row.date: row.spread_bps for row in panel}
    ordinary = {row.date: splits.reporting_day_type(row.date, row.values) == "ordinary" for row in panel}

    laws = mean_reversion_laws(panel, splits, registry)
    laws.update(read_walk_laws(args.walks, args.published, end))
    persistence = read_persistence(args.walks, args.published, end)

    missing: Dict[str, int] = {name: 0 for name in LAWS}
    tracked: dict = {}
    full: dict = {}
    for part, first, last in stretch_parts():
        tracked[part] = {"first_target_day": first.isoformat(), "last_target_day": last.isoformat(), "leads": {}}
        full[part] = {"leads": {}}
        for h in HORIZONS:
            rows = []
            for day in sorted(d for d in outcome if in_stretch(d, first, last) and ordinary[d]):
                have = {name: laws[name][h].get(day) for name in DISTRIBUTIONS}
                have_p = persistence[h].get(day)
                if any(q is None for q in have.values()) or have_p is None:
                    for name in DISTRIBUTIONS:
                        missing[name] += have[name] is None
                    missing[PERSISTENCE] += have_p is None
                    continue
                p = {name: smr.exceedance(q, TAU) for name, q in have.items()}
                p[PERSISTENCE] = have_p
                rows.append({"day": day, "outcome": outcome[day], "event": exceeds_bp(outcome[day], TAU), "p": p, "q": have})
            cell = build_cell(rows, draws=args.draws)
            withheld = under_minimum(cell["pressure_days"])
            tracked[part]["leads"][str(h)] = tracked_cell(cell, withheld=withheld)
            if withheld:
                full[part]["leads"][str(h)] = cell
    result = {
        "issue": 845, "declaration": str(DECLARATION.relative_to(REPO)),
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        "label": "development, not a verdict", "panel_sha256": panel_sha256(args.published),
        "last_day": end.isoformat(), "tau_bp": TAU, "seed": SEED, "draws": args.draws, "block": BLOCK,
        "minimum_pressure_days": MINIMUM_PRESSURE_DAYS, "laws": list(LAWS), "labels": LABELS,
        "cells_missing_a_law": missing, "stretches": tracked,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    if args.withheld is not None:
        args.withheld.write_text(json.dumps({"issue": 845, "withheld_cells": full, "note": "not tracked; for the pull request body (#710)"},
                                            indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"stretches": {p: {h: (c["cells"], c["pressure_days"]) for h, c in v["leads"].items()} for p, v in tracked.items()},
                      "missing": missing}))
    return 0


# -- the page ------------------------------------------------------------------------------------------------------


def fmt(x: float) -> str:
    return format(x, ".3f")


def with_interval(value: float, interval: Sequence[float]) -> str:
    return f"{fmt(value)} [{fmt(interval[0])}, {fmt(interval[1])}]"


def signed(value: float, interval: Sequence[float]) -> str:
    return f"{value:+.3f} [{interval[0]:+.3f}, {interval[1]:+.3f}]"


def page_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    names, labels = score["laws"], score["labels"]
    lines = [
        "# H5's calibration after reserve-management purchases began (#845)",
        "",
        "H5 step 3, development data: **not a verdict** (scoring protocol v1, #640). Evaluation only: no model is fitted or changed, "
        "no remedy is added, nothing is published (`metadata/exploration_845.json`).",
        "",
        f"On ordinary target days, by lead, the mean P(spread > +{score['tau_bp']:g} bp) each law gives against the share of those days that "
        f"realised it, for the stretches after the Fed began reserve-management purchases: 2025-12-12 to {score['last_day']} "
        "(the development days; `repo_model.exploration.EXPLORATORY_END`) and the earlier case, 2019-10-15 to 2020-02-28, which stops "
        "before the March 2020 QE. Intervals are the 5th and 95th percentile of a stationary bootstrap "
        f"(mean block {score['block']}, {score['draws']:,} draws). The laws are mean reversion (#686), #761's variant (i), "
        "#634's variant (c) and `gbm_funding`, and `persistence_logistic`, which has no distribution and so no decomposition.",
        "",
        "A (stretch, lead) cell with fewer than "
        f"{score['minimum_pressure_days']} pressure days follows Eleonora's minimum (#710): only its counts are shown. Whether "
        "calibration in the large may be reported for such a cell is hers.",
        "",
        "**Reading the split.** The level part is the over-warning that moving each law's centre onto the realised ordinary spread "
        "(by the stretch's mean location error, a hindsight diagnostic) would remove; the residual-pool part is what is left with the "
        "centre right. The two add to the error exactly.",
        "",
    ]
    for part, body in score["stretches"].items():
        lines += [f"## {part}", "", f"Target days {body['first_target_day']} to {body['last_target_day']}.", ""]
        lines += ["**Mean P against the realised share** (mean P [interval])", "",
                  "| lead | cells | pressure days | realised share | " + " | ".join(labels[n] for n in names) + " |",
                  "|---|---|---|---|" + "|".join("---" for _ in names) + "|"]
        for h, cell in body["leads"].items():
            if cell.get("withheld"):
                lines.append(f"| {h} | {cell['cells']} | {cell['pressure_days']} | under the minimum: counts only |" + " |" * len(names))
            elif not cell["cells"]:
                lines.append(f"| {h} | 0 | 0 | no cells |" + " |" * len(names))
            else:
                lines.append(f"| {h} | {cell['cells']} | {cell['pressure_days']} | {with_interval(cell['realised'], cell['realised_interval'])} | "
                             + " | ".join(with_interval(cell["laws"][n]["mean_p"], cell["laws"][n]["mean_p_interval"]) for n in names) + " |")
        shown = {h: c for h, c in body["leads"].items() if not c.get("withheld") and c["cells"]}
        if shown:
            lines += ["", "**Error (mean P - realised share), and its level and residual-pool parts**", "",
                      "| lead | law | error [interval] | level part | residual-pool part | centre shift (bp) |", "|---|---|---|---|---|---|"]
            for h, cell in shown.items():
                for n in names:
                    entry = cell["laws"][n]
                    if "level" in entry:
                        lines.append(f"| {h} | {labels[n]} | {signed(entry['error'], entry['error_interval'])} | {entry['level']:+.3f} | "
                                     f"{entry['pool']:+.3f} | {entry['delta_bp']:+.2f} |")
                    else:
                        lines.append(f"| {h} | {labels[n]} | {signed(entry['error'], entry['error_interval'])} | n/a | n/a | n/a |")
        lines.append("")
    lines += ["Cells missing a law (not filled): " + ", ".join(f"{labels[n]} {c}" for n, c in score["cells_missing_a_law"].items()) + ".",
              "", "Development, not a verdict.", ""]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


# -- the command line ----------------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="one of #634's walks, to the last development day")
    walk.add_argument("--variant", required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.add_argument("--end")
    walk.set_defaults(func=walk_command)
    exceed = sub.add_parser("exceedance", help="persistence-logistic at one lead, to the last development day")
    exceed.add_argument("--horizon", type=int, required=True)
    exceed.add_argument("--published", type=Path, required=True)
    exceed.add_argument("--output", type=Path, required=True)
    exceed.add_argument("--end")
    exceed.set_defaults(func=exceedance_command)
    score = sub.add_parser("score", help="mean P against the realised share, by stretch and lead")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--withheld", type=Path, help="where the figures of cells under the minimum go (not tracked)")
    score.add_argument("--end")
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.set_defaults(func=score_command)
    page = sub.add_parser("page", help="write the results page from the score")
    page.add_argument("--score", type=Path, required=True)
    page.add_argument("--output", type=Path, required=True)
    page.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
