"""Three ex-ante variants of the published model that try to keep the direct-pairs twin's turning-point gain (#453).

Declared before any score in `metadata/turning_point_variant.json`. Scored days are 2018-06-29 to 2025-12-31 only: the panel is cut
at 2025-12-31 before any fit (`docs/decisions/lockbox.md`). Writes nothing into `docs/runs/` and changes no published figure.
The persistence, published and twin walks are `scripts/direct_pairs_twin.py`'s (#450); `blend` and `calendar` are this script's.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for W in persistence published twin; do
        OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/direct_pairs_twin.py walk --panel PUB.csv --which $W --output OUT/walk_$W.json
    done
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/turning_point_variant.py walk --panel PUB.csv --output OUT/walk_blend.json
    PYTHONPATH=src python3 scripts/turning_point_variant.py calendar --panel PUB.csv --output OUT/calendar.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/turning_point_variant.py score --panel PUB.csv --calendar OUT/calendar.json \\
        OUT/walk_persistence.json OUT/walk_published.json OUT/walk_twin.json OUT/walk_blend.json --output OUT/score.json

The pressure candidates (the judge as declared in `metadata/pressure_judge.json`, days to 2025-12-31 only):

    for H in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $H --published --output OUT/bench_h$H.json
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/turning_point_variant.py pressure --panel PUB.csv --horizon 1 --output OUT/direct_h1.json
    for H in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/turning_point_variant.py pressure-variants --panel PUB.csv --horizon $H \\
        --bench OUT/bench_h$H.json --direct OUT/direct_h1.json --walk OUT/walk_blend.json --calendar OUT/calendar.json --output OUT/variants_h$H.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/variants_h?.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402
from repo_model.metrics import _quantile, crps_from_quantiles, stationary_bootstrap_indices  # noqa: E402
from repo_model.recalibration import SCORECASTER_INDICATORS, scorecaster_calendar  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


twin_script = _script("direct_pairs_twin")

DECLARATION = REPO / "metadata" / "turning_point_variant.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DAILY_RECORD = twin_script.DAILY_RECORD
END = date(2025, 12, 31)
CANDIDATES = ("blend_equal", "calendar_switch", "predicted_turn_switch")
MODELS = ("persistence", "published", "twin") + CANDIDATES
BLOCK, REPLICATIONS, LEVEL, SEED, ALPHA = 2, 2000, 0.90, 453, 0.05
MINIMUM_MOVE_BP = 2.0
THRESHOLD = 0.5
REFIT_EVERY = 21
LAGS = twin_script.LAGS
FIRST_TURN_DAY = 6


def declaration_commit() -> str:
    """The commit that last changed the declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(DECLARATION.relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True,
                           text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", relative], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


# -- the blend walk -------------------------------------------------------------


class _BlendFitted:
    """The equal-weight average of two uncalibrated quantile fits, read as one fit."""

    tail_fit = None

    def __init__(self, first, second):
        if tuple(first.levels) != tuple(second.levels):
            raise ValueError("the two fits report different quantile levels")
        self.levels = first.levels
        self._first, self._second = first, second
        self.features_read = tuple(dict.fromkeys(tuple(first.features_read) + tuple(second.features_read)))
        settings = dict(getattr(first, "model_settings", None) or {})
        self.model_settings = {**settings, "blend": "equal weight of the published fit and its direct-pairs twin"}

    def predict(self, feature_row):
        a, b = self._first.predict(feature_row), self._second.predict(feature_row)
        return tuple(0.5 * (x + y) for x, y in zip(a, b))


class _Recording:
    """An online calibration that remembers each scored day's as-of row date and passes everything else on."""

    def __init__(self, inner):
        self._inner = inner
        self.anchors = {}

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def view(self, model, index, feature_row):
        self.anchors[index] = feature_row.date
        return self._inner.view(model, index, feature_row)


def walk_command(args) -> int:
    declaration_commit()
    fto = twin_script._script("final_test_opening")
    live_record = fto._script("live_record")
    fto.live_record = live_record
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    rows = [row for row in rows if row.date <= END]
    require_unlocked([row.date for row in rows], where="turning-point variant")
    registry = json.loads(live_record.REGISTRY.read_text(encoding="utf-8"))
    sides, parsed = live_record._compare_sides(1)
    _name, fit_published, features, factory = sides["published"]
    _tname, fit_twin, twin_features, _tonline, _targs = twin_script.twin_side(live_record)
    if tuple(twin_features) != tuple(features):
        raise SystemExit("the twin reads other features than the published model")
    reads = {id(f): live_record._reads_information(f) for f in (fit_published, fit_twin)}

    def fit(train_frame, *, minimum_history, information=None):
        fits = []
        for part in (fit_published, fit_twin):
            if reads[id(part)]:
                fits.append(part(train_frame, minimum_history=minimum_history, information=information))
            else:
                fits.append(part(train_frame, minimum_history=minimum_history))
        return _BlendFitted(*fits)

    built = []

    def online(rows_, rule):
        built.append(_Recording(factory(rows_, rule)))
        return built[-1]

    walk, levels, settings = fto.distribution_walk(
        rows, fit=fit, features=features, online_calibration=online, registry=registry, horizon=1,
        minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
    )
    anchors = built[0].anchors
    days = [{"date": rows[i].date.isoformat(), "quantiles_bps": list(q), "actual_bps": rows[i].spread_bps,
             "anchor": anchors[i].isoformat()} for i, q in walk]
    document = {
        "which": "blend", "model": "blend_equal", "features": list(features), "levels": list(levels),
        "settings": settings, "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "first": days[0]["date"], "last": days[-1]["date"], "days": days,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=dict) + "\n", encoding="utf-8")
    print(json.dumps({"which": "blend", "days": len(days), "first": document["first"], "last": document["last"]}))
    return 0


# -- the calendar ---------------------------------------------------------------


def calendar_command(args) -> int:
    """The scorecaster's four indicators for every panel day to 2025-12-31, each read at its own decision instant."""

    declaration_commit()
    fto = twin_script._script("final_test_opening")
    live_record = fto._script("live_record")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    rows = [row for row in rows if row.date <= END]
    require_unlocked([row.date for row in rows], where="turning-point variant")
    registry = json.loads(live_record.REGISTRY.read_text(encoding="utf-8"))
    sides, _parsed = live_record._compare_sides(1)
    features = tuple(sides["published"][2])
    rule = live_record.InformationRule(registry, features, decision_time=live_record.DECISION, horizon=1)
    splits = load_split_declaration(SPLITS)
    dates = [row.date for row in rows]
    flags = {}
    for index, row in enumerate(rows):
        if index == 0:
            continue  # no earlier panel day, so no decision instant
        flags[row.date.isoformat()] = list(scorecaster_calendar(rows, rule, index, splits, dates))
    document = {"indicators": list(SCORECASTER_INDICATORS), "flags": flags,
                "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"days": len(flags), "indicators": document["indicators"]}))
    return 0


# -- the turning-point probability ----------------------------------------------


def turn_features(series, calendar_flags, anchor, day):
    """The features of the scored day at row `day`, read from the as-of row `anchor` and the day's calendar."""

    last = series[anchor]
    change = last - series[anchor - 1]
    spread_window = series[anchor - 4:anchor + 1]
    return [last, change, abs(change), statistics.pstdev(spread_window)] + [float(x) for x in calendar_flags[day]]


def turn_probabilities(series, calendar_flags, scored, anchors, *, refit_every=REFIT_EVERY, fit_model=None):
    """The probability that each scored row is a turning point, refitted walk-forward at each refit block.

    `scored` and `anchors` are the scored rows' indices and their as-of rows' indices. A block's model is trained at
    its first scored row `t0` on the rows `d` from `FIRST_TURN_DAY` to the as-of row of `t0` less one, whose
    label (the next day's spread) is public by then: `d + 1 <= anchor(t0)`.
    """

    from repo_model import ml

    labels = twin_script.turning_points(series, MINIMUM_MOVE_BP)
    probabilities = {}
    for start in range(0, len(scored), refit_every):
        block = list(range(start, min(start + refit_every, len(scored))))
        first_anchor = anchors[block[0]]
        train = [d for d in range(FIRST_TURN_DAY, first_anchor) if labels[d] is not None]
        if train and max(train) + 1 > first_anchor:
            raise LookAheadError(
                f"the turning-point label of row {max(train)} reads the spread of row {max(train) + 1}, which is "
                f"after the block's first as-of row {first_anchor}: it was not public at the refit"
            )
        x = [turn_features(series, calendar_flags, d - 2, d) for d in train]
        y = [1 if labels[d] else 0 for d in train]
        positives = sum(y)
        if positives < 10 or positives == len(y):
            predicted = [positives / len(y) if y else 0.0] * len(block)
        else:
            rows = [turn_features(series, calendar_flags, anchors[i], scored[i]) for i in block]
            predicted = ml.standardised_logistic_probabilities(x, y, rows, c=1.0, max_iter=1000)
        for i, p in zip(block, predicted):
            probabilities[i] = p
    return [probabilities[i] for i in range(len(scored))]


# -- scoring --------------------------------------------------------------------


def holm(gains, *, alpha=ALPHA, seed=SEED, replications=REPLICATIONS, block=BLOCK):
    """Holm across `gains` (name -> per-day paired gains), all read off the same stationary resamples."""

    names = list(gains)
    n = len(gains[names[0]])
    rng = random.Random(seed)
    draws = {name: [] for name in names}
    for _ in range(replications):
        indices = stationary_bootstrap_indices(n, block, rng)
        for name in names:
            values = gains[name]
            draws[name].append(sum(values[i] for i in indices) / len(indices))
    p = {name: (1 + sum(1 for d in draws[name] if d <= 0)) / (1 + replications) for name in names}
    ranked = sorted(names, key=lambda name: (p[name], names.index(name)))
    out, standing = {}, True
    for rank, name in enumerate(ranked, start=1):
        level = alpha / (len(names) - rank + 1)
        ordered = sorted(draws[name])
        lower = _quantile(ordered, level)
        interval = [_quantile(ordered, alpha), _quantile(ordered, 1 - alpha)]
        standing = standing and lower > 0
        out[name] = {"mean": sum(gains[name]) / n, "interval_90": interval, "p_one_sided": p[name], "holm_rank": rank,
                     "holm_level": level, "holm_adjusted_lower_bound": lower,
                     "verdict": "better" if standing else "worse" if interval[1] < 0 else "no difference"}
    return out


def switch_inputs(series, calendar, walk, dates_to_position):
    """Per scored day (an ISO date): whether the calendar flags it, and its predicted turning-point probability."""

    days = [d["date"] for d in walk["days"]]
    flags_by_row = {dates_to_position[date.fromisoformat(d)]: f for d, f in calendar["flags"].items()}
    scored = [dates_to_position[date.fromisoformat(d)] for d in days]
    anchors = [dates_to_position[date.fromisoformat(d["anchor"])] for d in walk["days"]]
    if any(a != s_ - 2 for a, s_ in zip(anchors, scored)):
        raise SystemExit("an as-of row is not two rows before its scored day; the turn model's lag assumes it is")
    probability = turn_probabilities(series, flags_by_row, scored, anchors)
    return {
        d: {"flagged": any(flags_by_row[r]), "turn_probability": p}
        for d, r, p in zip(days, scored, probability)
    }


def _cell_gain(values, members):
    return twin_script._mean_ci([values[i] for i in members], SEED)


def score_command(args) -> int:
    commit = declaration_commit()
    require_unlocked([END], where="turning-point variant")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {r.date: r for r in rows}
    position = {r.date: i for i, r in enumerate(rows)}
    splits = load_split_declaration(SPLITS)
    walks, digest = {}, None
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        walks[document["which"]] = document
        digest = digest or document["panel_sha256"]
        if document["panel_sha256"] != digest:
            raise SystemExit("the walks were run on different panels")
    if set(walks) != {"persistence", "published", "twin", "blend"}:
        raise SystemExit("score needs the walks persistence, published, twin and blend")
    calendar = json.loads(Path(args.calendar).read_text(encoding="utf-8"))
    if calendar["panel_sha256"] != digest:
        raise SystemExit("the calendar was read on another panel")
    published = {d["date"]: d for d in json.loads(DAILY_RECORD.read_text(encoding="utf-8"))["days"]
                 if d["date"] <= END.isoformat()}
    days = sorted(published)
    by_walk = {}
    for which, document in walks.items():
        have = {d["date"]: d for d in document["days"]}
        if sorted(have) != days:
            raise SystemExit(f"the {which} walk is not on the published record's scored days")
        by_walk[which] = have
    if any(by_walk["published"][d]["quantiles_bps"] != published[d]["quantiles_bps"] for d in days):
        raise SystemExit("the published walk differs from the published record")
    levels = tuple(walks["published"]["levels"])
    series = [r.spread_bps for r in rows if r.date <= END]
    flags_by_row = {position[date.fromisoformat(d)]: f for d, f in calendar["flags"].items()}
    scored = [position[date.fromisoformat(d)] for d in days]
    anchors = [position[date.fromisoformat(by_walk["blend"][d]["anchor"])] for d in days]
    if any(a != s - 2 for a, s in zip(anchors, scored)):
        raise SystemExit("an as-of row is not two rows before its scored day; the turn model's lag assumes it is")
    actual = [by_date[date.fromisoformat(d)].spread_bps for d in days]
    probability = turn_probabilities(series, flags_by_row, scored, anchors)
    flagged = [any(flags_by_row[s]) for s in scored]
    fired = [p >= THRESHOLD for p in probability]
    pick = {"calendar_switch": flagged, "predicted_turn_switch": fired}
    vectors = {"persistence": [by_walk["persistence"][d]["quantiles_bps"] for d in days],
               "published": [by_walk["published"][d]["quantiles_bps"] for d in days],
               "twin": [by_walk["twin"][d]["quantiles_bps"] for d in days],
               "blend_equal": [by_walk["blend"][d]["quantiles_bps"] for d in days]}
    for name, use_twin in pick.items():
        vectors[name] = [vectors["twin"][i] if use_twin[i] else vectors["published"][i] for i in range(len(days))]
    losses = {m: [crps_from_quantiles(levels, vectors[m][i], actual[i]) for i in range(len(days))] for m in MODELS}
    gains = {c: [losses["published"][i] - losses[c][i] for i in range(len(days))] for c in CANDIDATES}
    primary = holm(gains)
    # Cells.
    turning = twin_script.turning_points(series, MINIMUM_MOVE_BP)
    is_turn = [turning[s] is True for s in scored]
    month_end = [bool(flags_by_row[s][SCORECASTER_INDICATORS.index("month_end")]) for s in scored]
    groups = {"regime": [], "day_type": [], "outcome": []}
    for d in days:
        when = date.fromisoformat(d)
        row = by_date[when]
        groups["regime"].append(splits.regime(when))
        groups["day_type"].append(splits.reporting_day_type(when, row.values))
        groups["outcome"].append("pressure day (> +5 bp)" if exceeds_bp(row.spread_bps, 5) else "other days")
    cells = {"all": list(range(len(days)))}
    for dimension, labels in groups.items():
        for label in sorted(set(labels)):
            cells[f"{dimension}: {label}"] = [i for i, g in enumerate(labels) if g == label]
    cells["turning-point days"] = [i for i, t in enumerate(is_turn) if t]
    cells["not turning-point days"] = [i for i, t in enumerate(is_turn) if not t]
    cells["month-end days"] = [i for i, m in enumerate(month_end) if m]
    cells["not month-end days"] = [i for i, m in enumerate(month_end) if not m]
    crps = {}
    for label, members in cells.items():
        entry = {"days": len(members),
                 "mean_crps": {m: (sum(losses[m][i] for i in members) / len(members) if members else None) for m in MODELS}}
        if members:
            persistence_gain = {m: [losses["persistence"][i] - losses[m][i] for i in range(len(days))]
                                for m in MODELS if m != "persistence"}
            entry["gain_over_published"] = {c: _cell_gain(gains[c], members) for c in CANDIDATES}
            entry["gain_over_persistence"] = {m: _cell_gain(v, members) for m, v in persistence_gain.items()}
        crps[label] = entry
    # Lag.
    median_at = levels.index(0.5)
    lag = {}
    for label, members in cells.items():
        if len(members) < 30 or not (label == "all" or label.startswith("regime")):
            continue
        # The panel is cut at END, so the lag at -3 has no spread for the last three days: they are left out of the lag.
        members = [i for i in members if scored[i] + max(-min(LAGS), 0) < len(series)]
        member_pos = [scored[i] for i in members]
        tables = {m: twin_script._lag_table([vectors[m][i][median_at] for i in members], series, member_pos)
                  for m in MODELS}
        lag[label] = {"days": len(members), "best_lag": {m: twin_script._best(t) for m, t in tables.items()},
                      "correlation_at_lag_0_and_2": {m: [t[0], t[2]] for m, t in tables.items()}}
    # Coverage.
    lo50, hi50, lo90, hi90 = (levels.index(x) for x in (0.25, 0.75, 0.05, 0.95))
    coverage = {}
    for label, members in cells.items():
        if label != "all" and not label.startswith("regime"):
            continue
        entry = {"days": len(members)}
        for m in MODELS:
            q = [vectors[m][i] for i in members]
            a = [actual[i] for i in members]
            entry[m] = {"50%": sum(x[lo50] <= v <= x[hi50] for x, v in zip(q, a)) / len(a),
                        "90%": sum(x[lo90] <= v <= x[hi90] for x, v in zip(q, a)) / len(a)}
        coverage[label] = entry
    # The switches.
    n_turn = sum(is_turn)
    switches = {}
    for name, use in pick.items():
        hits = sum(1 for u, t in zip(use, is_turn) if u and t)
        switches[name] = {"fires": sum(use), "days": len(days), "turning_point_days": n_turn,
                          "hit_rate_on_turning_points": hits / n_turn if n_turn else None,
                          "precision": hits / sum(use) if sum(use) else None}
    out = {
        "directive": "#453", "declaration": str(DECLARATION.relative_to(REPO)), "declaration_commit": commit,
        "panel_sha256": digest, "first": days[0], "last": days[-1], "days": len(days),
        "published_walk_reproduces_the_record": {"days": len(days), "differing": 0},
        "interval": {"method": "stationary_bootstrap", "block_length": BLOCK, "replications": REPLICATIONS,
                     "level": LEVEL, "seed": SEED},
        "sign": "gain = CRPS(published) - CRPS(candidate) per day; positive favours the candidate",
        "primary": primary, "crps": crps, "lag": lag, "coverage": coverage, "switches": switches,
        "blend_settings": walks["blend"]["settings"],
    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(primary, indent=1))
    print(json.dumps(switches, indent=1))
    return 0


# -- the pressure candidates ----------------------------------------------------


def _pressure_script():
    return _script("pressure_judge")


def pressure_command(args) -> int:
    """`published_v1_direct`: the published pressure classifier with direct-pairs training, at one horizon."""

    from repo_model import ml, pressure
    from repo_model.baseline import rolling_exceedance_backtest
    from repo_model.recalibration import NestedFoldPid
    from repo_model import pressure_judge as pj

    declaration_commit()
    require_unlocked([END], where="turning-point variant")
    pjs = _pressure_script()
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    rows = [row for row in rows if row.date <= END]
    splits = load_split_declaration(SPLITS)
    registry = json.loads(pjs.REGISTRY.read_text())
    model = pjs._load_script("pressure_model_v1")
    h = args.horizon
    features = model._at_horizon(model.GBM_FEATURES, h)

    def online(rows_, rule):
        return NestedFoldPid(rows_, rule, splits=splits, refit_every=pjs.REFIT_EVERY)

    raw = rolling_exceedance_backtest(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(n for n in features if n != "spread_bps"), minimum_history=pjs.MINIMUM_HISTORY,
            training_pairs="direct",
        ),
        model_name="distributional_gbm",
        features=features,
        registry=registry,
        decision_time=pjs.DECISION,
        taus=declaration.thresholds,
        minimum_history=pjs.MINIMUM_HISTORY,
        refit_every=pjs.REFIT_EVERY,
        end=declaration.last_day,
        horizon=h,
        online_calibration=online,
    )
    forecast = pj.report_forecast("published_v1_direct", pressure.recalibrated(raw))
    document = pjs._document(h, hashlib.sha256(args.panel.read_bytes()).hexdigest(), [forecast])
    document["declaration_commit"] = declaration_commit()
    document["features"] = list(features)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "model": forecast.name, "output": str(args.output)}))
    return 0


def variants_command(args) -> int:
    """The three candidates' probabilities at one horizon: the switches and the blend at h = 1, published_v1's after."""

    declaration_commit()
    require_unlocked([END], where="turning-point variant")
    h = args.horizon
    control_doc = json.loads(args.bench.read_text(encoding="utf-8"))
    control = control_doc["forecasts"]["published_v1"]
    names = {c: f"published_v1_{c}" for c in CANDIDATES}
    if h > 1:
        forecasts = {name: control for name in names.values()}
    else:
        direct_doc = json.loads(args.direct.read_text(encoding="utf-8"))
        if direct_doc["panel_sha256"] != control_doc["panel_sha256"]:
            raise SystemExit("the direct-pairs forecasts were scored on another panel")
        direct = direct_doc["forecasts"]["published_v1_direct"]
        rows = load_daily_panel(args.panel)
        audit_panel(rows)
        series = [r.spread_bps for r in rows if r.date <= END]
        position = {r.date: i for i, r in enumerate(rows)}
        walk = json.loads(args.walk.read_text(encoding="utf-8"))
        calendar = json.loads(args.calendar.read_text(encoding="utf-8"))
        if calendar["panel_sha256"] != control_doc["panel_sha256"] or walk["panel_sha256"] != control_doc["panel_sha256"]:
            raise SystemExit("the calendar or the blend walk is from another panel")
        inputs = switch_inputs(series, calendar, walk, position)
        forecasts = {name: {} for name in names.values()}
        for tau, column in control.items():
            if set(column) != set(direct[tau]):
                raise SystemExit(f"the control and the twin are not on the same days at tau {tau}")
            missing = [d for d in column if d not in inputs]
            if missing:
                raise SystemExit(f"{len(missing)} pressure days are not CRPS-scored days, first {missing[0]}")
            out = {name: {} for name in names.values()}
            for day, p in column.items():
                q = direct[tau][day]
                out[names["blend_equal"]][day] = 0.5 * (p + q)
                out[names["calendar_switch"]][day] = q if inputs[day]["flagged"] else p
                out[names["predicted_turn_switch"]][day] = q if inputs[day]["turn_probability"] >= THRESHOLD else p
            for name in names.values():
                forecasts[name][tau] = out[name]
    document = {"horizon": h, "panel_sha256": control_doc["panel_sha256"], "forecasts": forecasts,
                "declaration_commit": declaration_commit()}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "models": sorted(forecasts), "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    walk = commands.add_parser("walk")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(handler=walk_command)
    calendar = commands.add_parser("calendar")
    calendar.add_argument("--panel", type=Path, required=True)
    calendar.add_argument("--output", type=Path, required=True)
    calendar.set_defaults(handler=calendar_command)
    score = commands.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--calendar", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("inputs", nargs=4, type=Path)
    score.set_defaults(handler=score_command)
    pressure = commands.add_parser("pressure")
    pressure.add_argument("--panel", type=Path, required=True)
    pressure.add_argument("--horizon", type=int, required=True)
    pressure.add_argument("--output", type=Path, required=True)
    pressure.set_defaults(handler=pressure_command)
    variants = commands.add_parser("pressure-variants")
    variants.add_argument("--panel", type=Path, required=True)
    variants.add_argument("--horizon", type=int, required=True)
    variants.add_argument("--bench", type=Path, required=True)
    variants.add_argument("--direct", type=Path)
    variants.add_argument("--walk", type=Path)
    variants.add_argument("--calendar", type=Path)
    variants.add_argument("--output", type=Path, required=True)
    variants.set_defaults(handler=variants_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
