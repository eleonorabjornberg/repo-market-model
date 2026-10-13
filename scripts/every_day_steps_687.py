"""Why the fitted ordinary-day models rank the ordinary days worse than their own main input (#687, avenue #674): the steps, one at a time.

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing into `docs/runs/`. Nothing is published, no day after
2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`), and the live record and pin do not move. Exploration on development data
(scoring protocol v1, #640): nothing here is a verdict.

The every-day part of `risk_gbm+every_day+gate+settle+h41+iorb` (#579) is a ridge logistic of a pressure day at +5 bp on the spread, the SOFR
75th and 99th percentile less IORB and (at lead 1) the announced IORB change. Three construction steps sit on its forecast, each declared before
any score of this directive in `metadata/every_day_steps_687.json`:

* `persist` (#532): the smaller of today's forecast and the previous scored day's;
* `gate` (#532, #595): kept only if above the 0.9 quantile of the forecasts of the previous 250 scored days that were not risk dates;
* `cap` (#601): kept only if the tail spread is at or below the 0.75 quantile of its readings over the previous 250 scored days.

`run` refits the component once per lead and writes the eight forecast sets that follow from every subset of the three steps, applied in that order
(`persist`, then `gate`, then `cap`), and the three day-level rows of #624's step 2 with its construction taken apart (the inputs alone, with the
scarcity state, with the inputs times the state). `gate` alone is the published row; `gate` and `cap` is `+tailcap75`. `blocks` compares the pooled
AUROC with the AUROC inside refit blocks. The statistics, the pairing and the intervals are `scripts/off_risk_day_624.py measure`'s.

    # PUBLISHED.csv and AUG2.csv, AUG2D.csv, AUG2R.csv: the scratch panels of scripts/off_risk_day_624.py's docstring; OUT/bench_h?.json are
    # pressure_judge.py forecasts; OUT/iorb_h?.json and OUT/cap_h?.json the published control row and its cap (iorb_every_day_579.py, every_day_conditioning_601.py)
    PYTHONPATH=src python3 scripts/every_day_steps_687.py declare
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/every_day_steps_687.py run --panel AUG2.csv --day-panel AUG2R.csv \\
        --published PUBLISHED.csv --horizon $h --output OUT/steps_h$h.json
    PYTHONPATH=src python3 scripts/every_day_steps_687.py check --input 'OUT/steps_h{h}.json' --iorb 'OUT/iorb_h{h}.json' --cap 'OUT/cap_h{h}.json'
    PYTHONPATH=src python3 scripts/every_day_steps_687.py measure ...   (see the result page for the exact commands)
    PYTHONPATH=src python3 scripts/every_day_steps_687.py blocks --panel PUBLISHED.csv --scratch AUG2.csv --input 'OUT/steps_h{h}.json' --output OUT/blocks.json
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import random
import sys
from datetime import date, time
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, ml, pressure_judge as pj, probability_calibration as pc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script_687", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script_687"] = module
    spec.loader.exec_module(module)
    return module


odr = _load("off_risk_day_624")
iorb = _load("iorb_every_day_579")
cond = _load("every_day_conditioning_601")
fa = _load("risk_date_false_alarm_controls")
ann = odr.ann
rds = odr.rds

DECLARATION = REPO / "metadata" / "every_day_steps_687.json"
LEADS = odr.LEADS
TAU = odr.TAU
#: the steps, in the order they are applied
STEPS = ("persist", "gate", "cap")
COMPONENT = "comp"
#: the published control row and the capped row, which two of the eight forecast sets must reproduce cell for cell
PUBLISHED_ROW = iorb.NEW
CAPPED_ROW = cond.VARIANTS["cap75"]
DAY_ROWS = {
    "day:inputs": "inputs", "day:inputs+state": "monotone", "day:inputs+state+interactions": "interaction",
}
CUT = "comp:cut"


# -- the pure steps ----------------------------------------------------------------------------------------


def row_name(steps: Sequence[str]) -> str:
    """The name of the forecast set with `steps` applied: `comp` alone, `comp+gate`, `comp+persist+gate+cap`."""

    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        raise ValueError(f"steps {unknown} are not declared; the declared ones are {list(STEPS)}")
    return "+".join((COMPONENT,) + tuple(s for s in STEPS if s in steps))


def subsets() -> List[Tuple[str, ...]]:
    """Every subset of the steps, the smallest first, each in the order the steps are applied."""

    return [tuple(c) for size in range(len(STEPS) + 1) for c in combinations(STEPS, size)]


def leave_one_out(steps: Sequence[str] = STEPS) -> Dict[str, Tuple[str, ...]]:
    """For each step, the subset with that step removed."""

    return {s: tuple(t for t in steps if t != s) for s in steps}


def gate_cut(raw: Sequence[float], off: Sequence[bool], *, quantile: float, window: int, minimum_earlier: int) -> List[Optional[float]]:
    """The gate's cut-off of each scored day (`risk_date_false_alarm_controls._gate`): the nearest-rank quantile of the component's forecasts
    on the days that were not risk dates among the previous `window` scored days; None on a risk date and while those number fewer than
    `minimum_earlier`. It reads forecasts of earlier days only.
    """

    import math

    cuts: List[Optional[float]] = []
    for k, flag in enumerate(off):
        if not flag:
            cuts.append(None)
            continue
        earlier = sorted(raw[i] for i in range(max(0, k - window), k) if off[i])
        cuts.append(None if len(earlier) < minimum_earlier else earlier[max(0, math.ceil(quantile * len(earlier)) - 1)])
    return cuts


def apply_steps(
    raw: Sequence[Sequence[float]], off: Sequence[bool], steps: Sequence[str], controls: Mapping[str, Mapping], keep: Optional[Sequence[bool]] = None
) -> List[List[float]]:
    """The component's forecasts `raw[threshold][day]` with `steps` applied in the declared order; a risk date keeps the raw forecast, which is
    the parent's and is not scored here. The curve across thresholds is made non-increasing after each step, as the published rows are.

    `keep` is the cap's kept-day mask (`every_day_conditioning_601.tail_cap`), needed when `cap` is a step.

    Raises:
        ValueError: for a step that is not declared, or a cap with no mask, or a mask of another length.
    """

    row_name(steps)
    out = [list(r) for r in raw]
    for step in STEPS:
        if step not in steps:
            continue
        if step == "cap":
            if keep is None:
                raise ValueError("the cap needs the tail spread's kept-day mask")
            if len(keep) != len(off):
                raise ValueError("the kept-day mask must be one per scored day")
            out = [[p if k else 0.0 for p, k in zip(r, keep)] for r in out]
            for j in range(1, len(out)):
                out[j] = [min(a, b) for a, b in zip(out[j], out[j - 1])]
        else:
            out = fa.apply_control(step, dict(controls[step]), out, off, [None] * len(off))
    return out


def within_block_auroc(scores: Sequence[float], outcomes: Sequence[int], blocks: Sequence[int]) -> Optional[float]:
    """The AUROC (ties half) over the pairs of a pressure day and a non-pressure day that are in the same refit block; None if there is no such pair.

    Raises:
        ValueError: for columns of different lengths.
    """

    if not len(scores) == len(outcomes) == len(blocks):
        raise ValueError("scores, outcomes and blocks must be one per day")
    by_block: Dict[int, List[int]] = {}
    for i, b in enumerate(blocks):
        by_block.setdefault(b, []).append(i)
    won, pairs = 0.0, 0
    for members in by_block.values():
        positive = [scores[i] for i in members if outcomes[i]]
        negative = [scores[i] for i in members if not outcomes[i]]
        for p in positive:
            for q in negative:
                pairs += 1
                won += 1.0 if p > q else 0.5 if p == q else 0.0
    return None if pairs == 0 else won / pairs


def block_costs(
    scores: Sequence[float], outcomes: Sequence[int], blocks: Sequence[int], *, seed: int, replications: int, block_length: float, level: float
) -> dict:
    """The pooled AUROC, the AUROC inside refit blocks, and the second less the first with a stationary-bootstrap interval.

    A positive difference means the pairs that cross blocks rank worse than the pairs inside them: the forecast's level shifts between refits cost
    ranking. A resample on which either AUROC is undefined is left out and counted.
    """

    n = len(outcomes)
    pooled, within = pj.auroc(list(scores), list(outcomes)), within_block_auroc(scores, outcomes, blocks)
    draws: List[float] = []
    rng = random.Random(seed)
    for _ in range(replications):
        drawn = stationary_bootstrap_indices(n, block_length, rng)
        a = pj.auroc([scores[i] for i in drawn], [outcomes[i] for i in drawn])
        b = within_block_auroc([scores[i] for i in drawn], [outcomes[i] for i in drawn], [blocks[i] for i in drawn])
        if a is not None and b is not None:
            draws.append(b - a)
    out = {"pooled_auroc": pooled, "within_block_auroc": within, "difference": None if pooled is None or within is None else within - pooled,
           "draws": len(draws), "left_out": replications - len(draws), "lower": None, "upper": None}
    if draws and out["difference"] is not None:
        ordered = sorted(draws)
        tail = (1.0 - level) / 2.0
        out["lower"], out["upper"] = odr._quantile(ordered, tail), odr._quantile(ordered, 1.0 - tail)
    return out


def lost_pressure_days(
    outcomes: Sequence[int], before: Sequence[float], after: Sequence[float], cuts: Sequence[Optional[float]]
) -> dict:
    """The ordinary pressure days a step or a row loses, counted two ways on the days that have a cut-off.

    `zeroed`: the pressure days on which the row forecasts 0 (`<= RELIABILITY_FLOOR`) and `before` forecast above it. `below_cut`: the pressure days
    on which `before` is above the cut-off and `after` is at or below it. The cut-off is the component's own walk-forward gate cut, so a day
    counted there is one the component itself would have flagged.

    Raises:
        ValueError: for columns of different lengths.
    """

    if not len(outcomes) == len(before) == len(after) == len(cuts):
        raise ValueError("outcomes, forecasts and cut-offs must be one per day")
    floor = odr.RELIABILITY_FLOOR
    zeroed = sum(1 for y, b, a in zip(outcomes, before, after) if y and b > floor and a <= floor)
    below = sum(1 for y, b, a, c in zip(outcomes, before, after, cuts) if y and c is not None and b > c and a <= c)
    return {"zeroed": zeroed, "below_cut": below, "pressure_days": int(sum(outcomes)), "days_with_cut": sum(1 for c in cuts if c is not None)}


# -- the declaration ---------------------------------------------------------------------------------------


def declaration_document() -> dict:
    step_one = json.loads(odr.STEP_ONE_DECLARATION.read_text(encoding="utf-8"))
    persistence = json.loads(odr.STEP_THREE_DECLARATION.read_text(encoding="utf-8"))
    return {
        "status": "declared by the pull request that closes #687 before any score of a step row; a measurement, not a record. Nothing is published: no rule, threshold or declaration changes, no day after 2025-12-31 is scored, and the live record and pin do not move. The days read are 2018-2025, so a result describes that history and does not confirm anything (ruling of 11 October 2026 on #567). Exploration on development data, not a verdict (scoring protocol v1, #640); no new +5 bp classification variant is proposed (paused)",
        "issue": 687,
        "serves": "H2 (the data we hold carries signal for ordinary-day pressure) and H5, step: the diagnosis of #674",
        "scoring": step_one["scoring"],
        "thresholds_bp": [5, 10],
        "horizons": list(LEADS),
        "bootstrap": persistence["bootstrap"],
        "population": persistence["population"],
        "outcome": persistence["outcome"],
        "statistics": persistence["statistics"],
        "reference_rows": persistence["reference_rows"],
        "component": {
            "row": "the every-day part of risk_gbm+every_day+gate+settle+h41+iorb (#579): ml.pressure_risk_date_variant_exceedance with every_day=True and early_prior=False, the component inputs of ml.EVERY_DAY_COMPONENT_INPUTS and, at lead 1 only, iorb_announced_change_bps; settlements dated from the announcement and the H.4.1 read per release (the 'both' arm of #541)",
            "raw": "the component's probability before any step, on the days that are not risk dates; a risk date keeps the parent's forecast and is not scored here",
        },
        "steps": {
            "order": list(STEPS),
            "persist": dict(fa.CONTROLS["persist"], rule="on a day that is not a risk date, the smaller of the component's forecast today and its forecast on the previous scored day (the parent's, if that was a risk date; #532)"),
            "gate": dict(fa.CONTROLS["gate"], rule="the component's forecast is kept only if strictly above the quantile (nearest rank) of its forecasts on the days that were not risk dates among the previous window scored days, with at least minimum_earlier of them (#532, #595)"),
            "cap": dict(cond.CAPS["cap75"], tail=cond.TAIL, rule="the forecast is kept only if the tail spread, read at the day's decision instant, is at or below the quantile of the readings of the previous window scored days that were not risk dates (#601)"),
            "values": "every value is the published one of the step it names; none is tuned here",
        },
        "rows": {
            "component_subsets": [row_name(s) for s in subsets()],
            "reproduced": {row_name(("gate",)): PUBLISHED_ROW, row_name(("gate", "cap")): CAPPED_ROW},
            "reproduction": "the two rows named above must equal the published control row and its +tailcap75 cap cell for cell on every lead; `check` refuses a difference",
            "leave_one_out": "from the full construction (persist, gate and cap, applied in that order) each step removed in turn; and each step added alone to the raw component. Persist is not in the published row; it is a #532 control that was not chosen, and is included here because the avenue (#674) names it",
            "day_level": {name: form for name, form in DAY_ROWS.items()},
            "day_level_reading": "the day-level model of #624 step 2 (a), taken apart: a ridge logistic of a pressure day at +5 bp, fitted at each refit block on the earlier days that were not risk dates and whose outcome was observable at the block's fit, on (1) the four inputs, (2) the four inputs and the as-of scarcity state, (3) those and each input times the state (#624's `+offday`). Inputs as in metadata/off_risk_day_624.json. No step of the component is applied to them",
        },
        "pairing": "every row is paired against the full construction (comp+persist+gate+cap) and against persistence_logistic on the same days (scripts/off_risk_day_624.py measure --pair-with), pooled, by the judge's regimes and by as-of scarcity state, at leads 1 to 5, with a 90% stationary-bootstrap interval from resamples shared by the rows",
        "refit_blocks": "`blocks` compares, for every row and the reference rows, the pooled AUROC on the ordinary days with the AUROC over the pairs (a pressure day, a non-pressure day) that are in the same refit block of 21 scored days (probability_calibration.blocks), and the second less the first with a 90% stationary-bootstrap interval (the seed and block length of the bootstrap above). The raw as-of spread has no refit, so its two figures differ only by which pairs are counted: it is the control",
        "cut_off": "'pushed below the cut-off' is counted against the component's own walk-forward gate cut: an ordinary pressure day on which the raw component is above that cut and the row is at or below it. 'zeroed' is a forecast of 0 (at most 1e-4) on a day the raw component forecast above it",
        "near_empty_cells": "a cell of fewer than 10 pressure days is called near-empty on the page, and a difference that sits only in such cells is reported as such",
        "published": "nothing",
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"declaration": str(DECLARATION)}))
    return 0


# -- run ---------------------------------------------------------------------------------------------------


def _component_forecasts(rows, registry, parents, spec, splits, declared, h: int, last: date):
    """The component's raw forecasts at lead `h`: `iorb_every_day_579.run_command`'s fit without its gate, with the announced IORB change at lead 1."""

    settle, h41, _suffix = ann.ARMS[iorb.ARM]
    rows, registry = ann.arm_inputs(iorb.ARM, rows, registry, h)
    parent_features = ann.features_for(parents, spec, h, settle)
    component_inputs = ml.EVERY_DAY_COMPONENT_INPUTS + ((iorb.ANNOUNCED,) if h in iorb.READ_AT else ())
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    predictor = ml.pressure_risk_date_variant_exceedance(
        spec["kind"], parent_features, splits, declared["scoring"]["minimum_history"], every_day=True, early_prior=False,
        component_inputs=component_inputs,
    )
    features = tuple(dict.fromkeys(parent_features + component_inputs))
    with rds.switched_on(), (h41_release.release_dating() if h41 else contextlib.nullcontext()):
        report = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=PUBLISHED_ROW, features=features, registry=registry,
            decision_time=time.fromisoformat(declared["scoring"]["decision_time"]), taus=taus,
            minimum_history=declared["scoring"]["minimum_history"], refit_every=declared["scoring"]["refit_every"], end=last, horizon=h,
        )
    return rds.column(report), taus, settle


def run_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    h = args.horizon
    if h not in LEADS:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="every_day_steps_687")
    pj.require_scored_days(pj.load_declaration(), [last], where="every_day_steps_687")
    ann_declaration = ann.rds.committed_declaration(ann.DECLARATION)
    spec = ann_declaration["models"][iorb.MODEL]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    registry = measurement_fields.load_registry()
    splits = load_split_declaration(odr.SPLITS)
    by_date = {row.date: row for row in rows}
    column, taus, settle = _component_forecasts(rows, registry, parents, spec, splits, declared, h, last)
    keys = [f"{tau:g}" for tau in taus]
    days = sorted(column[keys[0]])
    raw = [[column[key][day] for day in days] for key in keys]
    # the component's risk dates are those of the arm's rows (settlements dated from the announcement), as the published row serves them
    timed_rows, _timed_registry = ann.arm_inputs(iorb.ARM, rows, registry, h)
    timed_by_date = {row.date: row for row in timed_rows}
    off_arm = [not ann.risk_flag(splits, timed_by_date[date.fromisoformat(day)].values, settle or h == 1) for day in days]
    levels_by_day = cond.read_levels(rows, registry, last, h)
    missing = [d for d in days if d not in levels_by_day]
    if missing:
        raise SystemExit(f"lead {h}: {len(missing)} scored days are not on the fold grid, the first {missing[0]}")
    # the cap is the one of `every_day_conditioning_601.cap_command`, whose risk dates are the plain panel's (one day at lead 5 differs from the arm's)
    off = [not ann.risk_flag(splits, by_date[date.fromisoformat(day)].values, True) for day in days]
    keep = cond.tail_cap([levels_by_day[d] for d in days], off, **{k: declared["steps"]["cap"][k] for k in ("quantile", "window", "minimum_earlier")})
    controls = {s: {k: v for k, v in declared["steps"][s].items() if k != "rule"} for s in ("persist", "gate")}
    forecasts: Dict[str, dict] = {}
    for steps in subsets():
        out = apply_steps(raw, off_arm, steps, controls, keep)
        forecasts[row_name(steps)] = {key: dict(zip(days, out[j])) for j, key in enumerate(keys)}
    cut = gate_cut(raw[0], off_arm, **{k: declared["steps"]["gate"][k] for k in ("quantile", "window", "minimum_earlier")})
    # the cut-off is stored with the forecasts at +5 bp, the threshold the page scores
    forecasts[CUT] = {keys[0]: dict(zip(days, [None if c is None else c for c in cut]))}
    # the day-level rows: #624's step 2 (a) with its construction taken apart
    scoring = declared["scoring"]
    taus_day = tuple(taus)
    scored, train_ends, outcomes = odr.grid(rows, splits, scoring, h, taus_day, last)
    if [d.isoformat() for d in scored] != days:
        raise SystemExit(f"lead {h}: the component's scored days are not the grid's")
    states = odr._load("pressure_judge")._scarcity_states(h, last)
    state_value = [None if states.get(d) is None else float(states[d]) for d in scored]
    day_rows = load_daily_panel(args.day_panel)
    audit_panel(day_rows)
    reads = odr.read_features(day_rows, registry, last, h)
    base = odr.design_rows([reads[d] for d in days], state_value)
    step_two = json.loads(odr.STEP_TWO_DECLARATION.read_text(encoding="utf-8"))
    for name, form in DAY_ROWS.items():
        designs = [None if row is None else _design(form, row, state_value[k]) for k, row in enumerate(base)]
        model = odr.walk_forward_day_model(
            designs, {tau: outcomes[tau] for tau in taus_day}, scored, train_ends, off, kind="logistic", monotone=None,
            minimum_pairs=step_two["constants"]["minimum_pairs"], minimum_events=step_two["constants"]["minimum_events"], fit=ml.fit_off_risk_day_model,
        )
        # a risk date is not scored here; its forecast is 0 so that the file is a row on the grid
        monotone = odr.monotone_across_thresholds(model, taus_day)
        forecasts[name] = {f"{tau:g}": {d: (monotone[tau][k] if off[k] else 0.0) for k, d in enumerate(days)} for tau in taus_day}
        print(json.dumps({"horizon": h, "row": name, "served_days": sum(1 for k, x in enumerate(designs) if off[k] and x is not None)}), flush=True)
    document = {
        "horizon": h, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel), "day_panel_sha256": panel_sha256(args.day_panel),
        "declaration": declared, "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _design(form: str, row: Sequence[float], state: float) -> List[float]:
    """The design row of a day-level form: `inputs` the four inputs alone, then `monotone` (with the state) and `interaction` (with the state and the products)."""

    if form == "inputs":
        return list(row)
    return odr.variant_vector(form, row, state)


# -- check: the reproduced rows ----------------------------------------------------------------------------


def check_command(args) -> int:
    """Refuse a difference between the component rows that are published rows and the published rows, cell for cell."""

    worst = 0.0
    cells = 0
    for h in LEADS:
        steps = json.loads(Path(args.input.format(h=h)).read_text(encoding="utf-8"))["forecasts"]
        for name, template, published in (
            (row_name(("gate",)), args.iorb, PUBLISHED_ROW), (row_name(("gate", "cap")), args.cap, CAPPED_ROW),
        ):
            expected = json.loads(Path(template.format(h=h)).read_text(encoding="utf-8"))["forecasts"][published]
            for tau, by_day in expected.items():
                if sorted(by_day) != sorted(steps[name][tau]):
                    raise SystemExit(f"h = {h}, {name}, +{tau} bp: the scored days differ from the published row's")
                for day, value in by_day.items():
                    cells += 1
                    worst = max(worst, abs(value - steps[name][tau][day]))
    print(json.dumps({"cells_compared": cells, "largest_absolute_difference": worst}))
    if worst > 1e-12:
        raise SystemExit("a reproduced row differs from the published row")
    return 0


# -- blocks: the pooled AUROC against the AUROC inside refit blocks ---------------------------------------


def blocks_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    scoring = declared["scoring"]
    boot = declared["bootstrap"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="every_day_steps_687")
    rows = load_daily_panel(args.scratch)
    audit_panel(rows)
    splits = load_split_declaration(odr.SPLITS)
    by_date = {row.date: row for row in rows}
    templates = dict(item.split("=", 1) for item in args.row)
    result: Dict[str, dict] = {}
    for h in LEADS:
        scored, train_ends, outcomes = odr.grid(rows, splits, scoring, h, [TAU], last)
        days = [d.isoformat() for d in scored]
        block_of = [0] * len(scored)
        for number, (start, stop, _end) in enumerate(pc.blocks(scored, train_ends)):
            for i in range(start, stop):
                block_of[i] = number
        off = [not ann.risk_flag(splits, by_date[d].values, True) for d in scored]
        keep = [i for i, flag in enumerate(off) if flag]
        y = [int(outcomes[TAU][i]) for i in keep]
        blocks = [block_of[i] for i in keep]
        for name, template in templates.items():
            if template.startswith("asof:"):
                reads = odr.read_features(rows, measurement_fields.load_registry(), last, h, fields=("spread_bps",))
                document = odr.asof_spread_document(reads, days, h)
                forecast = document["forecasts"][odr.SPREAD_REFERENCE][f"{TAU:g}"]
            else:
                document = json.loads(Path(template.format(h=h)).read_text(encoding="utf-8"))
                if document["horizon"] != h or document["panel_sha256"] != panel_sha256(args.panel):
                    raise SystemExit(f"{template.format(h=h)} is not the forecasts at h = {h} on this panel")
                forecast = document["forecasts"][name][f"{TAU:g}"]
                if sorted(forecast) != days:
                    raise SystemExit(f"{name}: the scored days at +{TAU:g} bp are not the grid's at h = {h}")
            scores = [float(forecast[days[i]]) for i in keep]
            result.setdefault(name, {})[str(h)] = dict(
                block_costs(scores, y, blocks, seed=boot["seed"], replications=boot["replications"], block_length=boot["block_length"], level=boot["level"]),
                days=len(y), pressure_days=int(sum(y)), blocks=len(set(blocks)),
            )
            print(json.dumps({"row": name, "horizon": h}), flush=True)
    document = {"declaration": declared, "panel_sha256": panel_sha256(args.panel), "scratch_panel_sha256": panel_sha256(args.scratch), "rows": result}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


# -- losses: how many ordinary pressure days each step loses -----------------------------------------------


def losses_command(args) -> int:
    declared = rds.committed_declaration(DECLARATION)
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="every_day_steps_687")
    rows = load_daily_panel(args.scratch)
    audit_panel(rows)
    splits = load_split_declaration(odr.SPLITS)
    by_date = {row.date: row for row in rows}
    result: Dict[str, dict] = {}
    for h in LEADS:
        scored, train_ends, outcomes = odr.grid(rows, splits, scoring, h, [TAU], last)
        days = [d.isoformat() for d in scored]
        off = [not ann.risk_flag(splits, by_date[d].values, True) for d in scored]
        keep = [i for i, flag in enumerate(off) if flag]
        document = json.loads(Path(args.input.format(h=h)).read_text(encoding="utf-8"))
        if document["horizon"] != h or document["panel_sha256"] != panel_sha256(args.panel):
            raise SystemExit(f"{args.input.format(h=h)} is not the forecasts at h = {h} on this panel")
        forecasts = document["forecasts"]
        y = [int(outcomes[TAU][i]) for i in keep]
        cuts = [forecasts[CUT][f"{TAU:g}"][days[i]] for i in keep]
        cuts = [None if c is None else float(c) for c in cuts]
        raw = [forecasts[row_name(())][f"{TAU:g}"][days[i]] for i in keep]
        for name in forecasts:
            if name == CUT:
                continue
            after = [forecasts[name][f"{TAU:g}"][days[i]] for i in keep]
            entry = lost_pressure_days(y, raw, after, cuts) if name.startswith(COMPONENT) else {
                "zeroed": None, "below_cut": None, "pressure_days": int(sum(y)), "days_with_cut": sum(1 for c in cuts if c is not None),
            }
            entry["pressure_days_on_zero"] = sum(1 for yy, a in zip(y, after) if yy and a <= odr.RELIABILITY_FLOOR)
            result.setdefault(name, {})[str(h)] = entry
    out = {"declaration": declared, "panel_sha256": panel_sha256(args.panel), "scratch_panel_sha256": panel_sha256(args.scratch), "rows": result}
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    r = sub.add_parser("run")
    r.add_argument("--panel", type=Path, required=True, help="the scratch panel (AUG2.csv)")
    r.add_argument("--day-panel", type=Path, required=True, help="the scratch panel with the satiation distance built per release (AUG2R.csv)")
    r.add_argument("--published", type=Path, required=True)
    r.add_argument("--horizon", type=int, required=True)
    r.add_argument("--output", type=Path, required=True)
    r.set_defaults(func=run_command)
    c = sub.add_parser("check")
    c.add_argument("--input", required=True, help="template with {h}")
    c.add_argument("--iorb", required=True)
    c.add_argument("--cap", required=True)
    c.set_defaults(func=check_command)
    b = sub.add_parser("blocks")
    b.add_argument("--panel", type=Path, required=True, help="the published panel")
    b.add_argument("--scratch", type=Path, required=True)
    b.add_argument("--row", action="append", required=True, help="NAME=TEMPLATE, or spread_bps_asof=asof:spread_bps")
    b.add_argument("--output", type=Path, required=True)
    b.set_defaults(func=blocks_command)
    l = sub.add_parser("losses")
    l.add_argument("--panel", type=Path, required=True)
    l.add_argument("--scratch", type=Path, required=True)
    l.add_argument("--input", required=True, help="template with {h}")
    l.add_argument("--output", type=Path, required=True)
    l.set_defaults(func=losses_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
