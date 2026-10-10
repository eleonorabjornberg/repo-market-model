"""Episode-by-episode post-mortem of the +5 bp pressure episodes (#474, track of #374).

A scratch measurement, not a record: it writes JSON, a Markdown summary and one SVG per
episode type into the directory it is given, and nothing into `docs/runs/`. It decides
nothing and changes no declaration, cut-off, tier or published figure. Scored days are
2018-06-29 to 2025-12-31; no day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

The episodes are the +5 bp onsets of tier 1 at lead >= 1: the onsets on the days scored at
every horizon h = 1 to 5 (`pressure.onsets` through `pressure_judge.build_grid`), the same 26
the judge counts. The five models are the tier-1 passers of #428 (`risk_gbm`, `risk_gbm_base`,
`risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`) under the judge's own
cut-offs (`pressure_judge.choose_cutoffs`, #407, chosen from each refit's training window alone).

Per episode and model: the h = 1 probability on each of the 10 scored days before the start
and on the start day itself, with the cut-off in force on each, and the probability, cut-off
and flag at every horizon h = 1 to 5 for the start day. "Warned at lead >= 1" is a flag at
some horizon h >= 1 for the start day, exactly tier 1's reading.

For a missed episode, the panel inputs are read as of the decision instant of each scored day
through the information set (`asof.InformationRule`, the reads of `FieldRead.row`; the
leakage and staleness guards of `baseline._as_of_folds` hold), never from the day's own row.
An input "moved" when its change over the 10 scored days before the start is at least
`MOVE_Z` trailing standard deviations of its 10-day changes over the `TRAILING` scored days
that end 10 days before the start (so nothing later than the window is used). Whether the
panel distinguished an episode from the false alarms of its regime: a false alarm is a
non-pressure day flagged at h = 1 by one of the five models; an input "separates" the
episode when its as-of level on the start day lies outside the range of that input over those
days, with at least `MIN_FALSE_ALARMS` of them. With `K` inputs and `n` false alarms about
`K * 2 / (n + 1)` inputs would do so by chance for an exchangeable episode; that expectation
is reported beside the count.

Cause of a miss, a reading of this script (declared here, listed in the pull request for
review): for a model that did not warn,

* "signal present, under the cut-off": at some horizon the start day's probability reached
  `UNDER_RATIO` of the cut-off in force (never for a cut-off of infinity);
* else "signal too late for the lead rule": the model flags the start day's successor, or the
  day after it, at h = 1 (the pressure itself is in the as-of spread by then);
* else "no signal in the panel": neither.

An episode missed by all five models takes the best of the five readings in that order.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts ...          # bench_h1..5.json
    PYTHONPATH=src python3 scripts/risk_date_severity.py run ...            # risk_h1..5.json
    PYTHONPATH=src python3 scripts/episode_post_mortem.py run --panel PUBLISHED.csv \\
        --scratch-panel AUG2.csv --output-dir OUT OUT/bench_h?.json OUT/risk_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, time
from html import escape
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.asof import TARGET, InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
LAST_DAY = date(2025, 12, 31)
MINIMUM_HISTORY = 61
DECISION = time(16, 0)

PASSERS = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")
HORIZONS = (1, 2, 3, 4, 5)
PATH_DAYS = 10
MOVE_Z = 2.0
TRAILING = 250
MIN_FALSE_ALARMS = 5
UNDER_RATIO = 0.5
LATE_DAYS = 2

CAUSE_UNDER = "signal present, under the cut-off"
CAUSE_LATE = "signal too late for the lead rule"
CAUSE_NONE = "no signal in the panel"
CAUSES = (CAUSE_UNDER, CAUSE_LATE, CAUSE_NONE)

# The panel inputs the post-mortem reads, each as of the decision instant: the latest public
# spread, the rates and volumes, reserves and the Treasury account, the ON RRP balance, the
# reserve-scarcity state (#115) and the settlements. The calendar is known ahead and is
# classification, not an input that moves.
INPUTS = (
    TARGET,
    "sofr_volume",
    "sofr_p75_iorb_bps",
    "sofr_p99_iorb_bps",
    "tgcr",
    "reserve_balances",
    "tga",
    "tga_daily",
    "tga_daily_change",
    "on_rrp",
    "reserve_scarcity_state",
    "dealer_treasury_position",
    "tbill_4w",
    "treasury_settlement",
    "treasury_settlement_coupons",
)
CALENDAR = ("days_to_month_end", "quarter_end", "tax_date")


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- pure readings (tested on small series) ------------------------------------------------


def flagged(probability: float, cutoff: float) -> bool:
    """A flag: the probability reaches the cut-off in force (a cut-off of infinity flags nothing)."""

    return probability >= cutoff


def under_ratio(probability: float, cutoff: float) -> float:
    """How close the probability came to the cut-off: 0 for a cut-off that flags nothing."""

    if not math.isfinite(cutoff) or cutoff <= 0.0:
        return 0.0
    return probability / cutoff


def classify_miss(per_horizon: dict, later_flags: list) -> str:
    """The cause of one model's miss of one episode (see the module docstring).

    `per_horizon` maps h to `{"probability", "cutoff"}` for the start day; `later_flags` is the
    model's h = 1 flags on the `LATE_DAYS` days after the start day.
    """

    best = max(under_ratio(v["probability"], v["cutoff"]) for v in per_horizon.values())
    if best >= UNDER_RATIO:
        return CAUSE_UNDER
    if any(later_flags):
        return CAUSE_LATE
    return CAUSE_NONE


def best_cause(causes: list) -> str:
    """The best reading across models, in the order of `CAUSES`."""

    return next(cause for cause in CAUSES if cause in causes)


def ten_day_changes(series: list, lag: int = PATH_DAYS) -> list:
    """`series[i] - series[i - lag]` wherever both are known."""

    return [
        series[i] - series[i - lag]
        for i in range(lag, len(series))
        if series[i] is not None and series[i - lag] is not None
    ]


def moved(series: list, index: int, *, lag: int = PATH_DAYS, trailing: int = TRAILING, z: float = MOVE_Z) -> dict:
    """Whether `series[index]` moved over `lag` days against its changes that ended `lag` days before.

    Only `series[:index - lag + 1]` enters the scale: the changes over windows that closed at or
    before the start of this one. Returns the change, the scale and the standardised change; the
    flag `moved` is `|standardised| >= z`. A series with no change, or too short a history, reads
    as not moved with `standardised` None.
    """

    now, then = series[index], series[index - lag] if index - lag >= 0 else None
    if now is None or then is None:
        return {"change": None, "scale": None, "standardised": None, "moved": False}
    history = ten_day_changes(series[max(0, index - lag - trailing) : index - lag + 1], lag)
    if len(history) < 20:
        return {"change": now - then, "scale": None, "standardised": None, "moved": False}
    mean = sum(history) / len(history)
    scale = math.sqrt(sum((x - mean) ** 2 for x in history) / (len(history) - 1))
    if scale == 0.0:
        return {"change": now - then, "scale": 0.0, "standardised": None, "moved": now != then}
    value = (now - then) / scale
    return {"change": now - then, "scale": scale, "standardised": value, "moved": abs(value) >= z}


def separates(level: float, others: list) -> bool:
    """The level lies strictly outside the range of the others (None for no level or no others)."""

    known = [x for x in others if x is not None]
    if level is None or len(known) < MIN_FALSE_ALARMS:
        return False
    return level < min(known) or level > max(known)


# -- the reads -----------------------------------------------------------------------------


def require_scored_days(days) -> None:
    """Refuse a scored day the lockbox holds, or one after the declared last scored day."""

    require_unlocked(days, where="episode_post_mortem.require_scored_days")
    late = [day for day in days if day > LAST_DAY]
    if late:
        raise LookAheadError(f"episode_post_mortem: scored day {late[0]} is after the last scored day {LAST_DAY}")


def as_of_series(rows, registry, scored_dates, inputs=INPUTS) -> dict:
    """Each input's value as of the decision instant of every scored day, by input then day.

    One `InformationRule` read per scored day (h = 1), through `baseline._as_of_folds`, which checks
    the lockbox on the whole grid first and every read for leakage and staleness. The value is the
    cell of the row the read came from (`FieldRead.row`), not the scored day's own row.
    """

    rule = InformationRule(registry, tuple(inputs) + tuple(CALENDAR), decision_time=DECISION, horizon=1)
    wanted = set(scored_dates)
    out = {name: {} for name in inputs}
    for fold in _as_of_folds(
        rows, rule, minimum_history=MINIMUM_HISTORY, refit_every=len(rows),
        entry="episode_post_mortem.as_of_series", end=LAST_DAY,
    ):
        day = rows[fold.index].date
        if day not in wanted:
            continue
        reads = {read.feature: read for read in fold.info.reads}
        for name in inputs:
            source = rows[reads[name].row]
            out[name][day] = source.spread_bps if name == TARGET else source.values.get(name)
    return out


# -- building the post-mortem --------------------------------------------------------------


def load_forecasts(panel: Path, inputs: list, rows, splits):
    """The judge's forecasts with their cut-offs, and the grids, for the five models."""

    declaration = pj.load_declaration()
    digest = panel_sha256(panel)
    forecasts = []
    for path in inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state={})
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    return declaration, grids, by_name


def build(panel: Path, scratch: Path, inputs: list) -> dict:
    risk = _script("risk_date_severity")
    risk.committed_declaration(risk.DECLARATION)
    rows = load_daily_panel(panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    declaration, grids, by_name = load_forecasts(panel, inputs, rows, splits)
    tau = declaration.primary
    missing = [name for name in PASSERS if name not in by_name]
    if missing:
        raise SystemExit(f"no forecasts for {missing}")
    require_scored_days(grids[1].dates)

    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in HORIZONS}
    common = sorted(set.intersection(*(set(grids[h].dates) for h in HORIZONS)))
    onset_days = [day for day in common if grids[1].onset[position[1][day]]]
    g1 = grids[1]

    def p_cut(name, h, day):
        k = position[h][day]
        f = by_name[name][h]
        return f.probabilities[tau][k], f.cutoffs[tau][k]

    reg = measurement_fields.load_registry()
    scratch_rows = load_daily_panel(scratch)
    with risk.switched_on():
        series = as_of_series(scratch_rows, reg, g1.dates)
    days = list(g1.dates)
    index = {day: i for i, day in enumerate(days)}
    vectors = {name: [series[name].get(day) for day in days] for name in INPUTS}

    # False alarms: a non-pressure day flagged at h = 1 by any of the five models.
    false_alarms = []
    for k, day in enumerate(days):
        if g1.outcomes[tau][k]:
            continue
        who = [n for n in PASSERS if flagged(*p_cut(n, 1, day))]
        if who:
            false_alarms.append({"date": day, "regime": g1.groups["regime"][k], "models": who})

    episodes = []
    for day in onset_days:
        k = index[day]
        record = {
            "start": day.isoformat(),
            "regime": g1.groups["regime"][k],
            "day_type": g1.groups["day_type"][k],
            "models": {},
        }
        before = days[max(0, k - PATH_DAYS) : k + 1]
        record["path_days"] = [d.isoformat() for d in before]
        record["path_complete"] = len(before) == PATH_DAYS + 1
        for name in PASSERS:
            path = []
            for d in before:
                p, c = p_cut(name, 1, d)
                path.append(
                    {"date": d.isoformat(), "probability": p, "cutoff": None if not math.isfinite(c) else c,
                     "flag": flagged(p, c), "pressure": bool(g1.outcomes[tau][index[d]])}
                )
            per_horizon = {}
            for h in HORIZONS:
                p, c = p_cut(name, h, day)
                per_horizon[h] = {"probability": p, "cutoff": c, "flag": flagged(p, c)}
            warned = any(v["flag"] for v in per_horizon.values())
            later = [flagged(*p_cut(name, 1, d)) for d in days[k + 1 : k + 1 + LATE_DAYS]]
            entry = {
                "path_h1": path,
                "start_day_by_horizon": {
                    str(h): {"probability": v["probability"],
                             "cutoff": None if not math.isfinite(v["cutoff"]) else v["cutoff"],
                             "flag": v["flag"]}
                    for h, v in per_horizon.items()
                },
                "warned_at_lead_at_least_1": warned,
                "warned_at_horizons": [h for h, v in per_horizon.items() if v["flag"]],
            }
            if not warned:
                entry["cause"] = classify_miss(per_horizon, later)
                entry["silent"] = all(v["probability"] == 0.0 for v in per_horizon.values())
            record["models"][name] = entry
        misses = [n for n in PASSERS if not record["models"][n]["warned_at_lead_at_least_1"]]
        record["missed_by"] = misses
        record["missed_by_all"] = len(misses) == len(PASSERS)
        if misses:
            record["cause_best_of_five"] = best_cause([record["models"][n]["cause"] for n in misses]) if record["missed_by_all"] else None
            record["inputs"] = _inputs_for(day, k, days, vectors, false_alarms, g1, tau)
        episodes.append(record)

    summary = _summary(episodes)
    return {
        "scored_days": [days[0].isoformat(), days[-1].isoformat()],
        "panel_sha256": panel_sha256(panel),
        "scratch_panel_sha256": panel_sha256(scratch),
        "models": list(PASSERS),
        "readings": {
            "move_z": MOVE_Z, "trailing": TRAILING, "path_days": PATH_DAYS, "min_false_alarms": MIN_FALSE_ALARMS,
            "under_ratio": UNDER_RATIO, "late_days": LATE_DAYS,
        },
        "false_alarm_days": [
            {"date": f["date"].isoformat(), "regime": f["regime"], "models": f["models"]} for f in false_alarms
        ],
        "episodes": episodes,
        "summary": summary,
    }


def _inputs_for(day, k, days, vectors, false_alarms, g1, tau) -> dict:
    """The inputs' 10-day movement before `day`, and whether they separate it from its regime's false alarms."""

    index = {d: i for i, d in enumerate(days)}
    regime = g1.groups["regime"][k]
    same = [f["date"] for f in false_alarms if f["regime"] == regime and f["date"] < day]
    same_all = [f["date"] for f in false_alarms if f["regime"] == regime and f["date"] != day]
    out = {"false_alarms_same_regime": len(same_all), "inputs": {}}
    count = 0
    for name in INPUTS:
        series = vectors[name]
        move = moved(series, k)
        level = series[k]
        others = [series[index[d]] for d in same_all]
        sep = separates(level, others)
        count += int(sep)
        out["inputs"][name] = {
            "level": level, "change_10d": move["change"], "standardised_change": move["standardised"],
            "moved": move["moved"], "separates_from_false_alarms": sep,
        }
    n = len(same_all)
    out["moved"] = [n_ for n_, v in out["inputs"].items() if v["moved"]]
    out["separating"] = [n_ for n_, v in out["inputs"].items() if v["separates_from_false_alarms"]]
    out["expected_separating_by_chance"] = (
        len(INPUTS) * 2.0 / (n + 1) if n >= MIN_FALSE_ALARMS else None
    )
    del same
    return out


def _summary(episodes: list) -> dict:
    per_model = {}
    for name in PASSERS:
        causes = {c: 0 for c in CAUSES}
        warned = 0
        silent = 0
        for e in episodes:
            m = e["models"][name]
            if m["warned_at_lead_at_least_1"]:
                warned += 1
            else:
                causes[m["cause"]] += 1
                silent += int(m["silent"])
        per_model[name] = {"episodes": len(episodes), "warned": warned, "missed": len(episodes) - warned,
                           "causes": causes, "missed_while_silent": silent}
    all_missed = [e for e in episodes if e["missed_by_all"]]
    by_all = {c: sum(1 for e in all_missed if e["cause_best_of_five"] == c) for c in CAUSES}
    caught_by_some = sum(1 for e in episodes if len(e["missed_by"]) < len(PASSERS))
    return {
        "episodes": len(episodes),
        "warned_by_at_least_one": caught_by_some,
        "missed_by_all_five": len(all_missed),
        "missed_by_all_five_cause_counts": by_all,
        "per_model": per_model,
        "by_regime": _split(episodes, "regime"),
        "by_day_type": _split(episodes, "day_type"),
    }


def _split(episodes: list, key: str) -> dict:
    out = {}
    for e in episodes:
        cell = out.setdefault(e[key], {"episodes": 0, "missed_by_all_five": 0, "warned_by_model": {n: 0 for n in PASSERS}})
        cell["episodes"] += 1
        cell["missed_by_all_five"] += int(e["missed_by_all"])
        for n in PASSERS:
            cell["warned_by_model"][n] += int(e["models"][n]["warned_at_lead_at_least_1"])
    return out


# -- rendering -----------------------------------------------------------------------------

COLORS = {
    "risk_gbm": "#1f77b4", "risk_gbm_base": "#17becf", "risk_logistic": "#d62728",
    "risk_logistic_base": "#ff7f0e", "risk_quantile_skewt_base": "#2ca02c",
}


def figure(day_type: str, episodes: list) -> str:
    """One SVG for an episode type: a panel per episode, each model's h = 1 path, cut-offs dashed."""

    columns = min(3, max(1, len(episodes)))
    rows_ = (len(episodes) + columns - 1) // columns
    w, h, pad_x, pad_y = 300, 170, 46, 40
    width, height = columns * w + 20, rows_ * h + 70
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="sans-serif" font-size="10" role="img" aria-label="Episodes of type {escape(day_type)}">',
        '<style>.t{fill:#222}.a{stroke:#888;stroke-width:1}.g{stroke:#ddd}@media (prefers-color-scheme: dark){.t{fill:#ddd}.a{stroke:#aaa}.g{stroke:#444}}</style>',
        f'<text class="t" x="10" y="16" font-size="13" font-weight="bold">Episode type: {escape(day_type)} '
        f'({len(episodes)} episodes): h = 1 probability of a +5 bp day, 10 days before the start; dashed: cut-off in force</text>',
    ]
    for i, name in enumerate(PASSERS):
        x = 10 + i * 175
        parts.append(f'<line x1="{x}" x2="{x + 16}" y1="30" y2="30" stroke="{COLORS[name]}" stroke-width="2"/>')
        parts.append(f'<text class="t" x="{x + 20}" y="33">{escape(name)}</text>')
    for n, e in enumerate(episodes):
        ox, oy = 10 + (n % columns) * w, 50 + (n // columns) * h
        top = max(
            [0.05]
            + [p["probability"] for m in e["models"].values() for p in m["path_h1"]]
            + [p["cutoff"] for m in e["models"].values() for p in m["path_h1"] if p["cutoff"] is not None]
        )
        top = min(1.0, top * 1.1)
        steps = len(e["path_days"])
        inner_w, inner_h = w - pad_x - 12, h - pad_y - 22

        def X(i):
            return ox + pad_x + (inner_w * i / max(1, PATH_DAYS))

        def Y(v):
            return oy + 14 + inner_h * (1 - min(v, top) / top)

        shift = PATH_DAYS + 1 - steps
        parts.append(f'<text class="t" x="{ox + pad_x}" y="{oy + 8}" font-weight="bold">{e["start"]} · {escape(e["regime"])}'
                     f'{"" if not e["missed_by"] else " · missed by " + str(len(e["missed_by"]))}</text>')
        parts.append(f'<line class="a" x1="{ox + pad_x}" x2="{ox + pad_x}" y1="{oy + 14}" y2="{oy + 14 + inner_h}"/>')
        parts.append(f'<line class="a" x1="{ox + pad_x}" x2="{ox + pad_x + inner_w}" y1="{oy + 14 + inner_h}" y2="{oy + 14 + inner_h}"/>')
        for v in (0.0, top):
            parts.append(f'<text class="t" x="{ox + pad_x - 4}" y="{Y(v) + 3}" text-anchor="end">{v:.2f}</text>')
        parts.append(f'<line x1="{X(PATH_DAYS)}" x2="{X(PATH_DAYS)}" y1="{oy + 14}" y2="{oy + 14 + inner_h}" stroke="#c00" stroke-dasharray="2 2"/>')
        parts.append(f'<text class="t" x="{X(PATH_DAYS)}" y="{oy + 14 + inner_h + 12}" text-anchor="middle">start</text>')
        parts.append(f'<text class="t" x="{X(0)}" y="{oy + 14 + inner_h + 12}" text-anchor="middle">-10</text>')
        for name in PASSERS:
            path = e["models"][name]["path_h1"]
            pts = " ".join(f"{X(shift + j):.1f},{Y(p['probability']):.1f}" for j, p in enumerate(path))
            parts.append(f'<polyline fill="none" stroke="{COLORS[name]}" stroke-width="1.6" points="{pts}"/>')
            cut = [(shift + j, p["cutoff"]) for j, p in enumerate(path) if p["cutoff"] is not None]
            if cut:
                pts = " ".join(f"{X(j):.1f},{Y(c):.1f}" for j, c in cut)
                parts.append(f'<polyline fill="none" stroke="{COLORS[name]}" stroke-width="1" stroke-dasharray="3 2" opacity="0.7" points="{pts}"/>')
            if e["models"][name]["warned_at_lead_at_least_1"]:
                parts.append(f'<circle cx="{X(PATH_DAYS)}" cy="{Y(path[-1]["probability"]):.1f}" r="2.5" fill="{COLORS[name]}"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def percent(k: int, n: int) -> str:
    return f"{k} of {n}"


def markdown(document: dict) -> str:
    s = document["summary"]
    lines = [
        "# Episode post-mortem (#474)",
        "",
        f"{s['episodes']} +5 bp episodes (onsets scored at every horizon h = 1 to 5), {document['scored_days'][0]} to "
        f"{document['scored_days'][1]}; published panel `{document['panel_sha256'][:8]}…`. Descriptive only.",
        "",
        "Table 1. Warned at lead >= 1 (a flag at some horizon h = 1 to 5 for the start day), by model, and the cause of each miss.",
        "",
        "| model | warned | missed | " + " | ".join(CAUSES) + " | missed while silent (probability 0) |",
        "|---|---|---|" + "---|" * (len(CAUSES) + 1),
    ]
    for name, m in s["per_model"].items():
        lines.append(
            f"| {name} | {percent(m['warned'], m['episodes'])} | {m['missed']} | "
            + " | ".join(str(m["causes"][c]) for c in CAUSES) + f" | {m['missed_while_silent']} |"
        )
    lines += [
        "",
        f"Warned by at least one of the five: {percent(s['warned_by_at_least_one'], s['episodes'])}. "
        f"Missed by all five: {s['missed_by_all_five']}, by cause (best of the five): "
        + "; ".join(f"{c}: {n}" for c, n in s["missed_by_all_five_cause_counts"].items()) + ".",
        "",
        "Table 2. Episodes by regime and pressure-day type: episodes, missed by all five, warned by each model.",
        "",
        "| group | episodes | missed by all five | " + " | ".join(PASSERS) + " |",
        "|---|---|---|" + "---|" * len(PASSERS),
    ]
    for key in ("by_regime", "by_day_type"):
        for label, c in sorted(s[key].items()):
            lines.append(
                f"| {key[3:]}: {label} | {c['episodes']} | {c['missed_by_all_five']} | "
                + " | ".join(str(c["warned_by_model"][n]) for n in PASSERS) + " |"
            )
    lines += [
        "",
        "Table 3. Every episode: regime, pressure-day type, the models that warned (horizons flagged), and for a miss its cause.",
        "",
        "| start | regime | type | " + " | ".join(PASSERS) + " |",
        "|---|---|---|" + "---|" * len(PASSERS),
    ]
    for e in document["episodes"]:
        cells = []
        for name in PASSERS:
            m = e["models"][name]
            if m["warned_at_lead_at_least_1"]:
                cells.append("warned h=" + ",".join(str(h) for h in m["warned_at_horizons"]))
            else:
                cells.append("missed: " + m["cause"] + (" (silent)" if m["silent"] else ""))
        lines.append(f"| {e['start']} | {e['regime']} | {e['day_type']} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Table 4. Missed episodes: panel inputs that moved in the 10 scored days before the start (as-of values; "
        f"|change| >= {MOVE_Z:g} trailing sd of 10-day changes), and inputs whose start-day level lies outside the range "
        "over the false alarms of the same regime (flagged non-pressure days at h = 1 by any of the five); "
        "the count expected by chance beside it.",
        "",
        "| start | regime | missed by | false alarms (regime) | inputs that moved | inputs outside the false alarms' range | expected by chance |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in document["episodes"]:
        if not e["missed_by"]:
            continue
        i = e["inputs"]
        expected = i["expected_separating_by_chance"]
        lines.append(
            f"| {e['start']} | {e['regime']} | {len(e['missed_by'])} of 5 | {i['false_alarms_same_regime']} | "
            f"{', '.join(i['moved']) or '–'} | {', '.join(i['separating']) or '–'} | "
            f"{'–' if expected is None else format(expected, '.1f')} |"
        )
    return "\n".join(lines) + "\n"


def run_command(args) -> int:
    document = build(args.panel, args.scratch_panel, args.inputs)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "episodes.json").write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    (out / "summary.md").write_text(markdown(document), encoding="utf-8")
    types = {}
    for e in document["episodes"]:
        types.setdefault(e["day_type"], []).append(e)
    for day_type, episodes in sorted(types.items()):
        (out / f"figure_{day_type}.svg").write_text(figure(day_type, episodes), encoding="utf-8")
    print(json.dumps({"output_dir": str(out), "episodes": len(document["episodes"]), "types": sorted(types)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--scratch-panel", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("inputs", nargs="+")
    run.set_defaults(func=run_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
