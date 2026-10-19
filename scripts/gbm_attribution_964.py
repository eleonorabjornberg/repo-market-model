"""Which inputs does `gbm_funding` read, and how does it read them? Input attribution (#964, H5 step 4 and the validation report).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model and no published figure. `gbm_funding` is refitted exactly as
`metadata/spread_distribution_634.json` declares it (`scripts/spread_distribution_634.py walk`: the published funding inputs of
`live_record.published_features(h)`, `ml.fit_gradient_boosted_quantiles` on the protocol grid, no new setting, the fold grid of the #634 walks).
Every choice, the reading rule included, is in `metadata/gbm_attribution_964.json`, which `walk`, `score` and `report` refuse to read unless it is
committed and unchanged; `declare` writes it from the constants below (and the panel's own decile grid) and was run, and its output committed,
before any number was computed. No day after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

What each refit block does, with the block's own fitted model and its scored days (no refit for an attribution):

1. permutation importance: one design column at a time, its values are shuffled among the block's scored days (`PERMUTATION_REPEATS` shuffles,
   each seeded from the study seed, the lead, the block and the input), each day is re-forecast and scored against its own outcome; the importance
   of an input on a day is the mean grid CRPS of the shuffled forecasts less the grid CRPS of the forecast;
2. partial dependence of q50 and q95 on the five inputs of the directive: the input is set, for every scored day, to each point of a declared
   grid (the 10th, 30th, 50th, 70th and 90th percentiles of that input over the scored days of the panel), the others as read;
3. a one-sigma shock of q50 and q95: the input is moved by plus and minus its standard deviation over the block's training frame.

`score` cuts these by regime (2018-19, 2020, 2021-23, 2024, 2025) and lead, with a stationary-bootstrap interval on each importance (the protocol's
studentized bootstrap, `scoring_protocol.paired_tests`, on the difference of the shuffled and the unshuffled day scores). `report` reads the
regime-coded dependence off the declared rule. The walks refit about ninety blocks per lead and are long: needs-mac (#46).

    # PUB.csv: the published panel (digest 4ddc3882...), built as scripts/spread_distribution_634.py's docstring says
    PYTHONPATH=src python3 scripts/gbm_attribution_964.py declare --published PUB.csv   # then commit metadata/gbm_attribution_964.json before any score
    for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/gbm_attribution_964.py walk --horizon $h --published PUB.csv --output OUT/attribution_h$h.json
    PYTHONPATH=src python3 scripts/gbm_attribution_964.py score --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/gbm_attribution_964.py report OUT/score.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import math
import random
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule, fold_grid, refit_blocks, require_refit_every  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    _AsOfFold,
    _at_decision,
    _check_decision_relative_availability,
    _check_fitter_stayed_inside,
    _fit_at_origin,
    _reads_information,
    _resolve_fields,
    panel_sha256,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "gbm_attribution_964.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 964
DECISION = time(16, 0)
HORIZONS = sp.HORIZONS
GRID = sp.GRID
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
#: shuffles per input per block; a block with fewer scored days than `MINIMUM_BLOCK` is not shuffled (one day cannot be permuted)
PERMUTATION_REPEATS = 5
MINIMUM_BLOCK = 5
HEADLINE_DRAWS = 2_000
MINIMUM_DAYS = 30
#: the inputs whose partial dependence and shocks are reported (the directive's five)
DEPENDENCE_INPUTS = ("reserve_balances", "tbill_4w", "tga", "sofr_volume", "spread_bps")
DEPENDENCE_POINTS = (0.1, 0.3, 0.5, 0.7, 0.9)
LEVELS_READ = (0.5, 0.95)
#: (name, first target day, last target day); a day belongs to the regime of its target day
REGIMES = (
    ("2018-19", date(2018, 1, 1), date(2019, 12, 31)),
    ("2020", date(2020, 1, 1), date(2020, 12, 31)),
    ("2021-23", date(2021, 1, 1), date(2023, 12, 31)),
    ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ("2025", date(2025, 1, 1), date(2025, 12, 31)),
)
#: the reading rule (marked in the pull request as a choice for Eleonora to rule on): a regime reads an input only when the partial
#: dependence of its median moves by at least this many bp across the declared points
READING_FLOOR_BP = 0.5
#: the level below which the directive's example split (reserves, in $ bn) would lie
RESERVE_SPLIT_BN = 1700.0


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the guards ------------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    document = json.loads(path.read_text(encoding="utf-8"))
    if tuple(document["protocol"]["grid"]) != GRID:
        raise SystemExit("the declared grid is not the protocol's")
    return document


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"gbm_attribution_964 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the pure parts --------------------------------------------------------------------------------------------------


def regime_of(day: date) -> Optional[str]:
    for name, first, last in REGIMES:
        if first <= day <= last:
            return name
    return None


def quantile_of(values: Sequence[float], level: float) -> float:
    """The linear-interpolation quantile of `values` (the 'type 7' rule), at `level` in [0, 1]."""

    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values to take a quantile of")
    if not 0.0 <= level <= 1.0:
        raise ValueError(f"level {level} is not in [0, 1]")
    position = level * (len(ordered) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def dependence_grid(columns: Mapping[str, Sequence[float]]) -> Dict[str, List[float]]:
    """The declared partial-dependence points of each input: its `DEPENDENCE_POINTS` percentiles over the scored days."""

    return {name: [round(quantile_of(columns[name], level), 6) for level in DEPENDENCE_POINTS] for name in DEPENDENCE_INPUTS}


def std(values: Sequence[float]) -> float:
    if len(values) < 2:
        raise ValueError("a standard deviation needs at least two values")
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def shuffled(column: Sequence[float], rng: random.Random) -> List[float]:
    """The column's values in a random order (the multiset is the same)."""

    out = list(column)
    rng.shuffle(out)
    return out


def with_value(design: Sequence[float], position: int, value: float) -> Tuple[float, ...]:
    out = list(design)
    out[position] = value
    return tuple(out)


def block_attribution(
    predict: Callable[[Sequence[float]], Sequence[float]],
    designs: Sequence[Sequence[float]],
    outcomes: Sequence[float],
    names: Sequence[str],
    *,
    seed_key: str,
    grid_points: Mapping[str, Sequence[float]],
    sigmas: Mapping[str, float],
    score: Callable[[Sequence[float], float], float] = sp.grid_crps,
    repeats: int = PERMUTATION_REPEATS,
) -> List[dict]:
    """One refit block's attribution, one entry per scored day (in the order of `designs`).

    `predict` maps a design row to the model's quantile vector at the protocol grid. Each entry holds the unshuffled forecast and its score,
    `perm[name]` (the mean score of the shuffled forecasts of that day, scored against that day's own outcome; `None` when the block is shorter
    than `MINIMUM_BLOCK`), `pd[name]` (q50 and q95 at each declared point) and `shock[name]` (q50 and q95 at minus and plus one sigma).
    """

    if len(designs) != len(outcomes):
        raise ValueError(f"{len(designs)} design rows for {len(outcomes)} outcomes")
    levels = [GRID.index(level) for level in LEVELS_READ]
    position = {name: index for index, name in enumerate(names)}
    base = [list(predict(design)) for design in designs]
    out = [
        {"base": base[i], "base_score": score(base[i], outcomes[i]), "perm": {}, "pd": {}, "shock": {}}
        for i in range(len(designs))
    ]
    long_enough = len(designs) >= MINIMUM_BLOCK
    for name in names:
        column = [design[position[name]] for design in designs]
        totals = [0.0] * len(designs)
        for repeat in range(repeats):
            order = shuffled(column, random.Random(f"{SEED}/{seed_key}/{name}/{repeat}")) if long_enough else column
            for i, design in enumerate(designs):
                totals[i] += score(predict(with_value(design, position[name], order[i])), outcomes[i])
        for i in range(len(designs)):
            out[i]["perm"][name] = totals[i] / repeats if long_enough else None
    for name in DEPENDENCE_INPUTS:
        if name not in position:
            continue
        at = position[name]
        for i, design in enumerate(designs):
            out[i]["pd"][name] = [
                [predict(with_value(design, at, point))[level] for level in levels] for point in grid_points[name]
            ]
            sigma = sigmas[name]
            out[i]["shock"][name] = {
                label: [predict(with_value(design, at, design[at] + sign * sigma))[level] for level in levels]
                for label, sign in (("minus", -1.0), ("plus", 1.0))
            }
    return out


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def dependence_range(curve: Sequence[float]) -> float:
    return max(curve) - min(curve)


def reads_input(curves_by_regime: Mapping[str, Sequence[float]], floor: float = READING_FLOOR_BP) -> dict:
    """The declared reading of one input's median dependence, regime by regime.

    A regime *reads* the input when its curve moves by at least `floor` bp across the points; its sign is that of the move from the first to the
    last point. The dependence is *regime-coded* when the regimes that read the input do not all share one sign.
    """

    reading = {name: ("flat" if dependence_range(curve) < floor else ("up" if curve[-1] > curve[0] else "down")) for name, curve in curves_by_regime.items()}
    signs = {sign for sign in reading.values() if sign != "flat"}
    return {"by_regime": reading, "regime_coded": len(signs) > 1}


def reserve_split(points: Sequence[float], curve: Sequence[float], floor: float = READING_FLOOR_BP, split: float = RESERVE_SPLIT_BN) -> bool:
    """Whether the dependence on reserves lives only below `split`: it moves by at least `floor` across the segments that start at or below it, and
    by less than `floor` (in total, both directions) across the segments that start above it."""

    if len(points) != len(curve) or len(points) < 2:
        raise ValueError("one curve value per point, at least two points")
    below = sum(abs(curve[k + 1] - curve[k]) for k in range(len(points) - 1) if points[k] <= split)
    above = sum(abs(curve[k + 1] - curve[k]) for k in range(len(points) - 1) if points[k] > split)
    return below >= floor and above < floor


# -- the declaration -------------------------------------------------------------------------------------------------


def declaration_document(published_rows) -> dict:
    scored = [row for row in published_rows if row.date <= LAST_TARGET]
    columns = {"spread_bps": [float(row.spread_bps) for row in scored]}
    for name in DEPENDENCE_INPUTS:
        if name not in columns:
            columns[name] = [float(row.values[name]) for row in scored if row.values.get(name) is not None]
    return {
        "status": "declared by the pull request that closes #964 before any score was computed; a measurement, not a record. Nothing is published: no published declaration, model, record, pin or figure moves, no day after 2025-12-31 is read (docs/decisions/lockbox.md). Development data gives no verdict (scoring protocol v1, #640): every figure here is exploration",
        "issue": 964,
        "hypothesis": "H5 (primary goal), step 4 (why the known drivers add nothing; scopes #951's follow-up) and the validation report (docs/model/validation.md, sensitivity analysis)",
        "rulings": ["Eleonora, 19 October 2026 (relayed on #958): the five-lens review, Lens D; directive #964"],
        "protocol": {"record": "docs/decisions/scoring-protocol.md (version 1)", "grid": list(GRID), "score": "grid CRPS, scoring_protocol.grid_crps"},
        "arms": {"gbm_funding": "the attributed model, refitted as metadata/spread_distribution_634.json declares it; a measurement of an existing model, not a new variant"},
        "estimators": {
            "model": "gbm_funding of metadata/spread_distribution_634.json, refitted exactly as declared there (spread_distribution_634.py walk): ml.fit_gradient_boosted_quantiles on the protocol grid, default settings, regressors live_record.published_features(h) without spread_bps (which the design adds), the shared fold grid",
            "minimum_history": MINIMUM_HISTORY,
            "refit_every": REFIT_EVERY,
            "decision_time": "16:00",
            "horizons": list(HORIZONS),
            "inputs": "the design columns of the fitted model at each lead (spread_bps and the published regressors; treasury_settlement is not read at h >= 2)",
            "last_target_day": LAST_TARGET.isoformat(),
        },
        "statistics": {
            "permutation_importance": f"per refit block, per design column: the column's values are shuffled among the block's scored days ({PERMUTATION_REPEATS} shuffles, random.Random of '{SEED}/<lead>/<block's first target day>/<input>/<repeat>'); importance = mean grid CRPS of the shuffled forecasts less the grid CRPS of the forecast, each against its own day's outcome; blocks shorter than {MINIMUM_BLOCK} days are not shuffled",
            "partial_dependence": {
                "inputs": list(DEPENDENCE_INPUTS),
                "levels": list(LEVELS_READ),
                "points": f"the {', '.join(str(int(p * 100)) for p in DEPENDENCE_POINTS)}th percentiles of the input over the panel's rows up to {LAST_TARGET} (computed by `declare`, in the panel's units: $ bn for reserve_balances, tga; percent for tbill_4w; the volume's own unit; bp for spread_bps)",
                "grid": dependence_grid(columns),
                "panel_sha256": None,
            },
            "shock": "q50 and q95 with each of the five inputs moved by plus and minus one standard deviation of the input over the block's training frame (as-of), the others as read",
        },
        "cuts": {
            "regimes": [{"name": name, "first": first.isoformat(), "last": last.isoformat()} for name, first, last in REGIMES],
            "regime_of_a_day": "the regime of its target day",
            "leads": list(HORIZONS),
            "minimum_days_per_cell": MINIMUM_DAYS,
            "interval": f"scoring_protocol.paired_tests, seed {SEED}, {HEADLINE_DRAWS} draws, stationary bootstrap, mean block 10, studentized; the one-sided lower 95% bound of mean(shuffled score - score)",
        },
        "reading": {
            "regime_coded_dependence": f"for each of the five inputs, in each regime: the median's partial dependence 'reads' the input when it moves by at least {READING_FLOOR_BP} bp across the five points; its sign is that of the move from the first to the last point; the dependence is regime-coded when the regimes that read it do not all share one sign",
            "reading_floor_bp": READING_FLOOR_BP,
            "reserves_split": f"for reserve_balances, whether the median's dependence moves only across the segments between points that start at or below {RESERVE_SPLIT_BN:g} ($ bn) and is flat (under the floor) across the later segments, in each regime (the directive's example)",
            "consequence_if_regime_coded": "the pull request names the relative encodings (tbill - iorb, sofr_p75 - sofr and sofr - sofr_p25 in bp, volume over its trailing 60-row median, reserves as the as-of ratio) as the next declared variant",
            "consequence_if_stable": "the pull request says the dependence is stable across regimes and the encoding avenue is dead",
            "choice_marked_for_eleonora": "the floor of 0.5 bp and the sign rule are the author's choice, marked in the pull request",
        },
        "limits": "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed; no published record changes; nothing after 2025-12-31 and no lockbox day is scored",
    }


def declare_command(args) -> int:
    published = load_daily_panel(args.published)
    audit_panel(published)
    document = declaration_document(published)
    document["statistics"]["partial_dependence"]["panel_sha256"] = panel_sha256(args.published)
    DECLARATION.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk --------------------------------------------------------------------------------------------------------


def attribution_walk(rows, *, features, registry, horizon, grid_points, minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY):
    """`spread_distribution_634.walk` for `gbm_funding`, with `block_attribution` run on each refit block's fitted model.

    Returns `[(row index, entry)]` in fold order and the design names. An entry carries the day, its outcome, its design row, the sigma of the
    block's training frame and `block_attribution`'s fields.
    """

    declared = tuple(features)
    fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID)
    _field_sources, sources = _resolve_fields(declared)
    rule = InformationRule(registry, declared, decision_time=DECISION, horizon=horizon)
    refit = require_refit_every(refit_every)
    dates = [row.date for row in rows]
    grid = fold_grid(dates, registry, decision_time=DECISION, minimum_history=minimum_history, horizon=horizon)
    require_study_window([dates[index] for index in grid])
    require_unlocked([dates[index] for index in grid], where="gbm_attribution_964")
    reads_information = _reads_information(fit)
    results = []
    names: Optional[Tuple[str, ...]] = None
    checked = False
    for indices in refit_blocks(grid, refit):
        folds = []
        for index in indices:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for read in info.reads:
                _check_decision_relative_availability(registry, read.fields, dates, read.row, index, decision_time=DECISION, horizon=horizon)
            block_frame = rule.frame(rows, info) if index == indices[0] else None
            folds.append(_AsOfFold(index, info, block_frame, rule.observation(rows, info)))
        fitted = _fit_at_origin(fit, folds[0].frame, minimum_history=minimum_history, information=rule, reads_information=reads_information)
        if not checked:
            _check_fitter_stayed_inside(fitted.features_read, declared, sources)
            checked = True
        if fitted.calibration != "none":
            raise ValueError("an attribution reads the uncalibrated fit; the model reports a calibrated band")
        names = tuple(fitted.design_names)
        views = [_at_decision(fitted, rows, rule, fold) for fold in folds]
        designs = [list(fitted.design_row(fold.feature_row)) for fold in folds]
        for view, fold, design in zip(views, folds, designs):
            if tuple(view.predict(fold.feature_row)) != tuple(fitted._quantile_vector(design)):
                raise ValueError("the shuffled forecast would not be the model's own at the unshuffled design row")
        training = [fitted.design_row(row) for row in folds[0].frame]
        sigmas = {name: std([design[names.index(name)] for design in training]) for name in DEPENDENCE_INPUTS if name in names}
        entries = block_attribution(
            fitted._quantile_vector,
            designs,
            [rows[fold.index].spread_bps for fold in folds],
            names,
            seed_key=f"{horizon}/{dates[indices[0]].isoformat()}",
            grid_points={name: points for name, points in grid_points.items() if name in names},
            sigmas=sigmas,
        )
        for fold, design, entry in zip(folds, designs, entries):
            entry.update(
                {
                    "date": dates[fold.index].isoformat(),
                    "outcome": float(rows[fold.index].spread_bps),
                    "design": dict(zip(names, design)),
                    "sigma": sigmas,
                }
            )
            results.append((fold.index, entry))
    return results, list(names or ())


def walk_command(args) -> int:
    declared = committed_declaration()
    h = args.horizon
    if h not in declared["estimators"]["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    require_unlocked([LAST_TARGET], where="gbm_attribution_964")
    published = load_daily_panel(args.published)
    audit_panel(published)
    if declared["statistics"]["partial_dependence"]["panel_sha256"] != panel_sha256(args.published):
        raise SystemExit("the panel is not the one the declaration's grid was computed from")
    rows = [row for row in published if row.date <= LAST_TARGET]
    live = _load("live_record")
    features = tuple(live.published_features(h))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    results, names = attribution_walk(
        rows, features=features, registry=registry, horizon=h, grid_points=declared["statistics"]["partial_dependence"]["grid"]
    )
    document = {
        "horizon": h,
        "design_names": names,
        "panel_sha256": panel_sha256(args.published),
        "declaration_dependence_grid": declared["statistics"]["partial_dependence"]["grid"],
        "days": [entry for _index, entry in results],
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"horizon": h, "days": len(results), "inputs": names}))
    return 0


# -- the score and the report ----------------------------------------------------------------------------------------


def _cut(days: Sequence[dict], regime: Optional[str]) -> List[dict]:
    return [d for d in days if regime is None or regime_of(date.fromisoformat(d["date"])) == regime]


def score_command(args) -> int:
    declared = committed_declaration()
    out: Dict[str, dict] = {"importance": {}, "dependence": {}, "shock": {}, "reading": {}, "reserves_split": {}}
    regimes = [None] + [name for name, _first, _last in REGIMES]
    walks: Dict[int, dict] = {}
    for h in declared["estimators"]["horizons"]:
        path = args.walks / f"attribution_h{h}.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != declared["statistics"]["partial_dependence"]["panel_sha256"]:
            raise SystemExit(f"{path} was walked from another panel than the declaration's")
        walks[h] = document
        require_study_window([date.fromisoformat(d["date"]) for d in document["days"]])
    for h, document in walks.items():
        for regime in regimes:
            days = _cut(document["days"], regime)
            label = regime or "pooled"
            for name in document["design_names"]:
                pairs = [(date.fromisoformat(d["date"]), d["perm"][name], d["base_score"]) for d in days if d["perm"][name] is not None]
                if len(pairs) < MINIMUM_DAYS:
                    out["importance"][f"{h}|{label}|{name}"] = None
                    continue
                test = sp.paired_test({day: perm for day, perm, _ in pairs}, {day: base for day, _, base in pairs}, seed=SEED, draws=HEADLINE_DRAWS, with_skill=False)
                out["importance"][f"{h}|{label}|{name}"] = {
                    "n": test.n, "mean": test.mean_difference, "lower_95_one_sided": test.lower_mean_difference(), "bootstrap_p": test.p_value,
                }
            for name in DEPENDENCE_INPUTS:
                if name not in document["design_names"] or len(days) < MINIMUM_DAYS:
                    continue
                points = len(days[0]["pd"][name])
                out["dependence"][f"{h}|{label}|{name}"] = {
                    "n": len(days),
                    "points": document["declaration_dependence_grid"][name],
                    "q50": [mean([d["pd"][name][k][0] for d in days]) for k in range(points)],
                    "q95": [mean([d["pd"][name][k][1] for d in days]) for k in range(points)],
                }
                base_q50 = mean([d["base"][GRID.index(0.5)] for d in days])
                base_q95 = mean([d["base"][GRID.index(0.95)] for d in days])
                out["shock"][f"{h}|{label}|{name}"] = {
                    "n": len(days), "base_q50": base_q50, "base_q95": base_q95,
                    **{
                        f"{side}_{level}": mean([d["shock"][name][side][i] for d in days])
                        for side in ("minus", "plus") for i, level in enumerate(("q50", "q95"))
                    },
                }
    for h in walks:
        for name in DEPENDENCE_INPUTS:
            curves = {r: out["dependence"][f"{h}|{r}|{name}"]["q50"] for r, _f, _l in REGIMES if f"{h}|{r}|{name}" in out["dependence"]}
            if len(curves) >= 2:
                out["reading"][f"{h}|{name}"] = reads_input(curves, declared["reading"]["reading_floor_bp"])
        for r, _f, _l in REGIMES:
            cell = out["dependence"].get(f"{h}|{r}|reserve_balances")
            if cell is not None:
                out["reserves_split"][f"{h}|{r}"] = reserve_split(cell["points"], cell["q50"])
    args.output.write_text(json.dumps(out, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"cells": {k: len(v) for k, v in out.items()}}))
    return 0


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    regimes = ["pooled"] + [name for name, _f, _l in REGIMES]
    lines = ["# Input attribution for `gbm_funding` (#964)", "", "Development data, not a verdict (scoring protocol v1). Importance is the rise in grid CRPS when the input is shuffled within its refit block.", ""]
    for h in HORIZONS:
        names = sorted({key.split("|")[2] for key in score["importance"] if key.startswith(f"{h}|")})
        if not names:
            continue
        lines += [f"## Lead {h}: permutation importance (mean rise in grid CRPS, bp; one-sided lower 95% bound in brackets)", "", "| input | " + " | ".join(regimes) + " |", "|---|" + "---|" * len(regimes)]
        for name in names:
            cells = []
            for regime in regimes:
                cell = score["importance"].get(f"{h}|{regime}|{name}")
                cells.append("n/a" if cell is None else f"{cell['mean']:+.3f} ({cell['lower_95_one_sided']:+.3f})")
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## Partial dependence of q50 and q95 (bp), by regime", ""]
    for key, cell in sorted(score["dependence"].items()):
        h, regime, name = key.split("|")
        lines.append(f"- lead {h}, {regime}, {name}: q50 " + ", ".join(f"{v:.2f}" for v in cell["q50"]) + "; q95 " + ", ".join(f"{v:.2f}" for v in cell["q95"]) + f" at points " + ", ".join(f"{p:g}" for p in cell["points"]))
    lines += ["", "## One-sigma shocks (change in q50 and q95, bp)", ""]
    for key, cell in sorted(score["shock"].items()):
        h, regime, name = key.split("|")
        lines.append(
            f"- lead {h}, {regime}, {name}: q50 {cell['minus_q50'] - cell['base_q50']:+.2f} / {cell['plus_q50'] - cell['base_q50']:+.2f}; "
            f"q95 {cell['minus_q95'] - cell['base_q95']:+.2f} / {cell['plus_q95'] - cell['base_q95']:+.2f}"
        )
    lines += ["", "## Declared reading: regime-coded dependence", ""]
    for key, reading in sorted(score["reading"].items()):
        lines.append(f"- {key.replace('|', ', ')}: {'REGIME-CODED' if reading['regime_coded'] else 'stable'} ({', '.join(f'{r}: {s}' for r, s in reading['by_regime'].items())})")
    lines += ["", "## Reserves: does the median's dependence live only below $1.7 tn? (declared check)", ""]
    for key, split in sorted(score["reserves_split"].items()):
        lines.append(f"- {key.replace('|', ', ')}: {'only below' if split else 'not only below'}")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    declare = sub.add_parser("declare")
    declare.add_argument("--published", type=Path, required=True)
    declare.set_defaults(func=declare_command)
    walk = sub.add_parser("walk")
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(func=walk_command)
    score = sub.add_parser("score")
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report")
    report.add_argument("score", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
