"""Tier 1 of the pressure judge under the readings the forensic audit questioned (#523): a scratch measurement.

It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. The rows, the readings and what
is reported are in `metadata/judge_readings.json`, which this script refuses to read unless it is committed and
unchanged; the bar, the cut-off rule, the weighted miss rule and the bootstrap are the judge's, unchanged. Scored days
are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published --output OUT/bench_hH.json
    ... each row's own forecast script, h = 1 to 5, as `docs/pivot/judge-readings-result.md` lists ...
    PYTHONPATH=src python3 scripts/judge_readings.py score --panel PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --row two_part_gbm='OUT/tp_h{h}.json' ... \\
        --output OUT/readings.json --markdown OUT/readings.md

For each row and for each of the two rules (the cut-offs and the limit on the flat count, or on the weighted count) it
reads tier 1 (onset warning at lead of at least 1) as (a) declared, (b) at one horizon and pooled across horizons,
(c) with the training-window check beside the realised count, (d) with the weighted rule's discount applied only to
alarms before an episode, and (e) outside 2018-19. Reading (a) is the judge's own and is checked against `judge`.
"""

from __future__ import annotations

import argparse
import bisect
import importlib.util
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "judge_readings.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
EARLY_YEARS = (2018, 2019)
RULES = ("unweighted", "weighted")


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- helpers ------------------------------------------------------------------


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", relative],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def before_only_weights(
    rule: "pj.WeightedMiss", *, positions: Sequence[int], pressure: Sequence[int], known_through: int
) -> tuple:
    """The weight of a false alarm when the discount is for alarms before an episode only (#514).

    As `pressure_judge.false_alarm_weights`, except that the distance is read to the *next* pressure day among the days
    given: an alarm after an episode, with no later pressure day known, weighs `rule.beyond`, and an alarm between two
    episodes weighs by its distance to the one ahead.

    Raises:
        LookAheadError: if a day is after `known_through`.
        ValueError: if the series differ in length or positions are not ascending.
    """

    if len(positions) != len(pressure):
        raise ValueError("the weights need one pressure flag per day")
    if any(b <= a for a, b in zip(positions, positions[1:])):
        raise ValueError("positions must be ascending")
    late = [p for p in positions if p > known_through]
    if late:
        raise LookAheadError(
            f"{len(late)} day(s) from position {min(late)} on are after position {known_through}, the last whose "
            f"outcome was known; a false alarm's weight reads the pressure days known by then only"
        )
    ahead = [p for p, y in zip(positions, pressure) if y]
    out = []
    for position, y in zip(positions, pressure):
        if y:
            out.append(0.0)
            continue
        k = bisect.bisect_right(ahead, position)
        out.append(pj.miss_weight(rule, ahead[k] - position if k < len(ahead) else None))
    return tuple(out)


def pooled_false_alarm_days(flags_by_horizon: Dict[int, Sequence[int]], pressure: Sequence[int]) -> List[int]:
    """1 on a day that is not a pressure day and is flagged at some horizon: a day flagged twice is one false alarm (#509)."""

    out = [0] * len(pressure)
    for flags in flags_by_horizon.values():
        for k, (flag, y) in enumerate(zip(flags, pressure)):
            if flag and not y:
                out[k] = 1
    return out


def year_masks(days: Sequence[date], years: Sequence[int]):
    """(inside, outside): which days are in the given calendar years, and which are not (#510)."""

    inside = [day.year in years for day in days]
    return inside, [not x for x in inside]


def window_false_alarms_per_onset(
    *,
    probabilities: Sequence[float],
    pressure: Sequence[int],
    onset: Sequence[int],
    cutoff: float,
    weights: Optional[Sequence[float]],
) -> Optional[float]:
    """The false alarms per onset a cut-off raises on a window, as the cut-off rule counts them (#512).

    A flag on a day that is not a pressure day counts 1, or its weight when `weights` is given. `None` when the window
    has no onset.
    """

    onsets = sum(onset)
    if not onsets:
        return None
    total = 0.0
    for k, (p, y) in enumerate(zip(probabilities, pressure)):
        if p >= cutoff and not y:
            total += 1.0 if weights is None else weights[k]
    return total / onsets


# -- one row's series -----------------------------------------------------------


class RowSeries:
    """A row's flags at every horizon on the days all horizons share, with the day-level facts the readings read."""

    def __init__(self, declaration, grids, by_name, name, place, weight_fn):
        tau = declaration.primary
        self.declaration, self.name = declaration, name
        self.horizons = [h for h in declaration.horizons if h in grids]
        self.common = sorted(set.intersection(*(set(grids[h].dates) for h in self.horizons)))
        position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in self.horizons}
        first = self.horizons[0]
        self.days = self.common
        self.onset = [float(grids[first].onset[position[first][day]]) for day in self.common]
        self.pressure = [grids[first].outcomes[tau][position[first][day]] for day in self.common]
        self.flags, self.clim, self.state, self.positive = {}, {}, {}, {}
        for h in self.horizons:
            at = [position[h][day] for day in self.common]
            if [grids[h].outcomes[tau][k] for k in at] != self.pressure:
                raise ValueError(f"{name}: the outcome of a day differs between horizons")
            chosen = by_name[name][h]
            raw = [1 if chosen.probabilities[tau][k] >= chosen.cutoffs[tau][k] else 0 for k in at]
            self.flags[h] = pj._alarm_flags(declaration, name, raw, self.onset)
            self.clim[h] = [by_name[declaration.climatology][h].probabilities[tau][k] for k in at]
            self.state[h] = [grids[h].groups["scarcity_state"][k] for k in at]
            self.positive[h] = [chosen.probabilities[tau][k] > 0.0 for k in at]
        places = [place[day] for day in self.common]
        rule = declaration.weighted_miss
        self.miss = (
            list(weight_fn(rule, positions=places, pressure=self.pressure, known_through=places[-1]))
            if rule is not None else [1.0] * len(self.common)
        )
        self.risk_date = [grids[first].groups["risk_date"][position[first][day]] for day in self.common]

    def false_alarms(self, h: int, idx: Sequence[int]):
        flat = sum(1 for k in idx if self.flags[h][k] and not self.pressure[k])
        weighted = sum(self.miss[k] for k in idx if self.flags[h][k] and not self.pressure[k])
        return flat, weighted


def _cell(declaration, series: RowSeries, idx, horizons, *, pooled: bool, seed_parts, limited_weighted: bool):
    """Tier 1's figures on the days `idx`, flagging at `horizons`: onsets warned, recall, false alarms, the verdict."""

    n = len(idx)
    onset = [series.onset[k] for k in idx]
    onsets = int(sum(onset))
    caught = [0.0] * n
    reference_missed = [1.0] * n
    flat_by_h, weighted_by_h = {}, {}
    pressure = [series.pressure[k] for k in idx]
    for h in horizons:
        flags = [series.flags[h][k] for k in idx]
        raised = sum(1 for f, y in zip(flags, pressure) if f and not y)
        caught = [max(c, float(f)) for c, f in zip(caught, flags)]
        flat_by_h[h] = raised
        weighted_by_h[h] = sum(series.miss[k] for k, f, y in zip(idx, flags, pressure) if f and not y)
    if pooled:
        union = pooled_false_alarm_days({h: [series.flags[h][k] for k in idx] for h in horizons}, pressure)
        flat_pooled = sum(union)
        weighted_pooled = sum(series.miss[k] for k, u in zip(idx, union) if u)
        references = [(series.clim[horizons[0]], flat_pooled)]
    else:
        flat_pooled = weighted_pooled = None
        references = [(series.clim[h], flat_by_h[h]) for h in horizons]
    for probabilities, raised in references:
        weights = pj.matched_false_alarm_weights([probabilities[k] for k in idx], pressure, raised)
        reference_missed = [m * (1.0 - w) for m, w in zip(reference_missed, weights)]
    out = {"days": n, "onsets": onsets}
    if not onsets:
        out["unavailable"] = "no onset on these days"
        return out
    evidence = pj._bootstrap(
        declaration,
        {"onsets": [onset, [o * c for o, c in zip(onset, caught)], [o * (1.0 - m) for o, m in zip(onset, reference_missed)]]},
        pj._ONSET_STATS, n, seed=pj._seed(declaration.seed, series.name, *seed_parts),
    )["onsets"]
    flat = (flat_pooled if pooled else max(flat_by_h.values())) / onsets
    weighted = (weighted_pooled if pooled else max(weighted_by_h.values())) / onsets
    limited = weighted if limited_weighted else flat
    lower = pj._lower(evidence["recall"])
    recall = evidence["recall"]["mean"]
    criteria = {
        "recall": recall is not None and recall >= declaration.onset_recall_at_least,
        "recall_above_climatology": lower is not None and lower > evidence["climatology_recall"]["mean"],
        "false_alarms": limited <= declaration.onset_false_alarms_at_most,
    }
    out.update(
        onsets_flagged=pj._clean(sum(o * c for o, c in zip(onset, caught))),
        recall=recall,
        recall_interval=[evidence["recall"]["interval"]["lower"], evidence["recall"]["interval"]["upper"]]
        if "interval" in evidence["recall"] else None,
        climatology_recall=evidence["climatology_recall"]["mean"],
        false_alarms_per_onset_flat=flat,
        false_alarms_per_onset_weighted=weighted,
        false_alarms_per_onset_limited=limited,
        criteria=criteria,
        passes=all(criteria.values()),
    )
    return out


def readings_for(declaration, series: RowSeries, *, limited_weighted: bool) -> dict:
    """Readings (a), (b) and (e) of one row at the cut-offs `series` carries."""

    everything = list(range(len(series.common)))
    horizons = series.horizons
    out = {"a": _cell(declaration, series, everything, horizons, pooled=False, seed_parts=("onsets", 1), limited_weighted=limited_weighted)}
    out["b1"] = {
        str(h): _cell(declaration, series, everything, [h], pooled=False, seed_parts=("onsets-h", h), limited_weighted=limited_weighted)
        for h in horizons
    }
    best = [c for c in out["b1"].values() if c.get("passes")]
    out["b1_best"] = (
        {"passes": True, "horizon": next(h for h, c in out["b1"].items() if c.get("passes"))}
        if best else {"passes": False}
    )
    out["b2"] = _cell(declaration, series, everything, horizons, pooled=True, seed_parts=("onsets-pooled", 1), limited_weighted=limited_weighted)
    inside, outside = year_masks(series.common, EARLY_YEARS)
    out["e"] = {
        "outside_2018_19": _cell(
            declaration, series, [k for k, o in enumerate(outside) if o], horizons, pooled=False,
            seed_parts=("onsets-outside", 1), limited_weighted=limited_weighted,
        ),
        "in_2018_19": _cell(
            declaration, series, [k for k, o in enumerate(inside) if o], horizons, pooled=False,
            seed_parts=("onsets-inside", 1), limited_weighted=limited_weighted,
        ),
    }
    return out


def training_checks(declaration, grids, forecasts, calendar, name) -> dict:
    """(c): at each refit, the cut-off in force applied to the training window, counted as the cut-off rule counts it."""

    position = {day: k for k, day in enumerate(calendar)}
    tau, step = declaration.primary, declaration.cutoff_refit_every
    out = {}
    for h in declaration.horizons:
        f = next(x for x in forecasts if x.name == name and x.horizon == h)
        grid = grids[h]
        onset = grid.onset_at(tau, declaration.primary)
        checks = []
        for start in range(0, len(f.dates), step):
            last_known = position[f.dates[start]] - h - 1
            if last_known < 0:
                continue
            training_end = calendar[last_known]
            window = [k for k in range(start) if f.dates[k] <= training_end]
            weights = None
            if declaration.weighting_applied and window:
                weights = pj.false_alarm_weights(
                    declaration.weighted_miss, positions=[position[f.dates[k]] for k in window],
                    pressure=[grid.outcomes[tau][k] for k in window], known_through=position[training_end],
                )
            value = window_false_alarms_per_onset(
                probabilities=[f.probabilities[tau][k] for k in window], pressure=[grid.outcomes[tau][k] for k in window],
                onset=[onset[k] for k in window], cutoff=f.cutoffs[tau][start], weights=weights,
            )
            if value is not None:
                checks.append(value)
        out[str(h)] = {
            "refits_checked": len(checks),
            "last": checks[-1] if checks else None,
            "largest": max(checks) if checks else None,
            "median": statistics.median(checks) if checks else None,
        }
    return out


# -- the command --------------------------------------------------------------


def _load(template: str, h: int) -> dict:
    return json.loads(Path(template.format(h=h)).read_text())


def score_command(args) -> int:
    document = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    names = (
        document["rows"]["risk_date_passers"] + document["rows"]["best_recall_rows"] + document["rows"]["references"]
    )
    templates = dict(item.split("=", 1) for item in args.row)
    if sorted(templates) != sorted(document["rows"]["best_recall_rows"]):
        raise SystemExit(f"--row must name exactly the declared rows {document['rows']['best_recall_rows']}")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    horizons = base.horizons
    if list(horizons) != document["scoring"]["horizons"]:
        raise SystemExit("the judge's horizons are not the declared ones")
    forecasts, panels = [], {}
    for h in horizons:
        sources = [("bench", args.bench), ("risk", args.risk), *templates.items()]
        for label, template in sources:
            doc = _load(template, h)
            if doc["panel_sha256"] != digest and label in ("bench",):
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            panels[f"{label}_h{h}"] = doc["panel_sha256"]
            forecasts.extend(f for f in pj.forecasts_from_horizon_document(doc) if f.name in names)
    unique = {}
    for f in forecasts:
        unique.setdefault((f.name, f.horizon), f)
    forecasts = list(unique.values())
    missing = [(n, h) for n in names for h in horizons if (n, h) not in unique]
    if missing:
        raise SystemExit(f"no forecast for {missing[:3]}")
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == base.climatology)
            out[h] = pj.build_grid(base, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    grids = grids_of(forecasts)
    result: Dict[str, object] = {
        "readings": {}, "training_checks": {}, "judge": {}, "scarcity_2020": {}, "h_ge_2": {}, "cross_check": {},
    }
    original = pj.false_alarm_weights
    runs = []
    for rule in RULES:
        declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
        runs.append((rule, "drafted", declaration, original))
    runs.append((
        "weighted", "before_only",
        replace(base, weighted_miss=pj.load_weighted_miss(applied=True)), before_only_weights,
    ))
    for rule, variant, declaration, weight_fn in runs:
        key = f"{rule}/{variant}" if variant != "drafted" else rule
        pj.false_alarm_weights = weight_fn
        try:
            chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
            by_name: Dict[str, Dict[int, "pj.Forecast"]] = defaultdict(dict)
            for f in chosen:
                by_name[f.name][f.horizon] = f
            result["readings"][key] = {}
            for name in names:
                series = RowSeries(declaration, grids, by_name, name, place, weight_fn)
                limited_weighted = rule == "weighted"
                result["readings"][key][name] = readings_for(declaration, series, limited_weighted=limited_weighted)
                if variant == "drafted":
                    result["training_checks"].setdefault(key, {})[name] = training_checks(declaration, grids, chosen, calendar, name)
                    result["h_ge_2"].setdefault(key, {})[name] = _beyond_one_day(series)
                    if name in document["rows"]["risk_date_passers"]:
                        result["scarcity_2020"].setdefault(key, {})[name] = _scarcity_2020(series)
            if variant == "drafted":
                judged = pj.judge(
                    declaration, grids_of(chosen), chosen, calendar=calendar, holdouts=judge_script._holdouts()
                )
                result["judge"][key] = {
                    n: {"onset_warning": c["tiers"]["onset_warning"]}
                    for n, c in judged["candidates"].items() if n in names
                }
                # Reading (a) is the judge's own: its onsets warned and worst false alarms per onset must match.
                for n in names:
                    near = judged["candidates"][n]["tiers"]["onset_warning"]["lead_at_least_1"]
                    mine = result["readings"][key][n]["a"]
                    theirs = near["worst_weighted_false_alarms_per_onset" if rule == "weighted" else "worst_false_alarms_per_onset"]
                    agree = (
                        abs(near["onsets_flagged"] - mine["onsets_flagged"]) < 1e-9
                        and abs(theirs - mine["false_alarms_per_onset_limited"]) < 1e-9
                        and abs(near["recall"]["mean"] - mine["recall"]) < 1e-9
                    )
                    result["cross_check"].setdefault(key, {})[n] = agree
                    if not agree:
                        raise SystemExit(f"reading (a) of {n} under the {key} rule does not match the judge's own row")
        finally:
            pj.false_alarm_weights = original
    result["declaration"] = {"path": "metadata/judge_readings.json", "judge_commit": judge_commit}
    result["provenance"] = {"panel_sha256": digest, "forecast_panels": panels}
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, document), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _beyond_one_day(series: RowSeries) -> dict:
    """The ceiling at lead of at least 2 (#511): onsets, those on a scheduled risk date, and the ones flagged at h >= 2."""

    far = [h for h in series.horizons if h >= 2]
    onset_days = [k for k, o in enumerate(series.onset) if o]
    flagged_far = [k for k in onset_days if any(series.flags[h][k] for h in far)]
    on_risk = [k for k in onset_days if series.risk_date[k] == "1"]
    reachable = [k for k in onset_days if any(series.positive[h][k] for h in far)]
    return {
        "onsets": len(onset_days),
        "onsets_with_a_forecast_above_0_at_h_ge_2": len(reachable),
        "onsets_on_a_scheduled_risk_date": len(on_risk),
        "onsets_flagged_at_h_ge_2": len(flagged_far),
        "of_which_on_a_risk_date": sum(1 for k in flagged_far if series.risk_date[k] == "1"),
        "of_which_off_a_risk_date": sum(1 for k in flagged_far if series.risk_date[k] != "1"),
    }


def _scarcity_2020(series: RowSeries) -> dict:
    """The as-of scarcity state of each false-alarm day of 2020, at the worst horizon and over the days flagged at any."""

    idx = [k for k, day in enumerate(series.common) if day.year == 2020]
    worst = max(series.horizons, key=lambda h: series.false_alarms(h, idx)[0])
    by_state = lambda days: dict(sorted(  # noqa: E731
        defaultdict(int, {s: sum(1 for k in days if series.state[worst][k] == s) for s in {series.state[worst][k] for k in days}}).items()
    ))
    worst_days = [k for k in idx if series.flags[worst][k] and not series.pressure[k]]
    union = pooled_false_alarm_days({h: series.flags[h] for h in series.horizons}, series.pressure)
    union_days = [k for k in idx if union[k]]
    return {
        "worst_horizon": worst,
        "worst_horizon_false_alarms": len(worst_days),
        "worst_horizon_by_state": by_state(worst_days),
        "any_horizon_false_alarms": len(union_days),
        "any_horizon_by_state": by_state(union_days),
    }


# -- the summary --------------------------------------------------------------


def _f(value, places=2):
    return "–" if value is None else f"{value:.{places}f}"


def _v(passes):
    return "pass" if passes else "fail"


def _row(name, cell):
    if "unavailable" in cell:
        return f"| {name} | – | – | – | – | – | – |"
    low, high = cell["recall_interval"] or (None, None)
    return (
        f"| {name} | {cell['onsets_flagged']:g} of {cell['onsets']} | {_f(cell['recall'], 3)} [{_f(low, 3)}, {_f(high, 3)}] "
        f"| {_f(cell['false_alarms_per_onset_limited'])} | {_f(cell['false_alarms_per_onset_flat'])} "
        f"| {_f(cell['false_alarms_per_onset_weighted'])} | {_v(cell['passes'])} |"
    )


HEAD = (
    "| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |\n"
    "|---|---|---|---|---|---|---|"
)


def markdown(result: dict, document: dict) -> str:
    names = document["rows"]["risk_date_passers"] + document["rows"]["best_recall_rows"] + document["rows"]["references"]
    lines = ["# Tier 1 under the readings the audit questioned (#523)", ""]
    titles = {
        "unweighted": "Unweighted rule",
        "weighted": "Weighted rule in force",
        "weighted/before_only": "(d) weighted rule, discount for alarms before an episode only",
    }
    for key, rows in result["readings"].items():
        lines += [f"## {titles[key]}", ""]
        for title, pick in (
            ("(a) as declared", lambda r: r["a"]),
            ("(b2) warnings and false alarms pooled across horizons", lambda r: r["b2"]),
            ("(e) outside 2018-19", lambda r: r["e"]["outside_2018_19"]),
            ("(e) in 2018-19", lambda r: r["e"]["in_2018_19"]),
        ):
            lines += [f"### {title}", "", HEAD]
            lines += [_row(n, pick(rows[n])) for n in names]
            lines.append("")
        lines += [
            "### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon",
            "", "| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |", "|---|---|---|---|---|---|---|",
        ]
        for n in names:
            b = rows[n]["b1_best"]
            cells = [
                f"{c['onsets_flagged']:g} / {_f(c['false_alarms_per_onset_limited'])}" if "onsets_flagged" in c else "–"
                for c in (rows[n]["b1"][str(h)] for h in (1, 2, 3, 4, 5))
            ]
            lines.append(f"| {n} | " + " | ".join(cells) + f" | {_v(b['passes'])}" + (f" (h = {b['horizon']})" if b["passes"] else "") + " |")
        lines.append("")
    lines += ["## (c) the cut-off rule's training-window check beside the realised count", ""]
    for key, rows in result["training_checks"].items():
        lines += [f"### {key}", "", "| row | realised, worst horizon | check at the last refit | largest check | median check |", "|---|---|---|---|---|"]
        for n in names:
            cell = result["readings"][key][n]["a"]
            if "unavailable" in cell:
                continue
            checks = rows[n]
            worst_h = max(checks, key=lambda h: checks[h]["last"] or 0)
            lines.append(
                f"| {n} | {_f(cell['false_alarms_per_onset_limited'])} | {_f(checks[worst_h]['last'])} (h = {worst_h}) "
                f"| {_f(max(c['largest'] or 0 for c in checks.values()))} | {_f(max(c['median'] or 0 for c in checks.values()))} |"
            )
        lines.append("")
    lines += ["## The ceiling at lead of at least 2 (#511): the judge's own rows", ""]
    for key, rows in result["judge"].items():
        lines += [
            f"### {key}", "",
            "| row | judge: lead >= 1 warned | judge: lead >= 3 warned | onsets on a risk date (grid label) | onsets forecast above 0 at some h >= 2 | flagged at h >= 2 (on / off a risk date) |",
            "|---|---|---|---|---|---|",
        ]
        for n in names:
            ow = rows[n]["onset_warning"]
            ceiling = result["h_ge_2"][key][n]
            warned = [
                f"{ow[k]['onsets_flagged']:g} of {ow[k]['onsets']}" if "onsets_flagged" in ow.get(k, {}) else "–"
                for k in ("lead_at_least_1", "lead_at_least_3")
            ]
            lines.append(
                f"| {n} | {warned[0]} | {warned[1]} | {ceiling['onsets_on_a_scheduled_risk_date']} of {ceiling['onsets']} "
                f"| {ceiling['onsets_with_a_forecast_above_0_at_h_ge_2']} of {ceiling['onsets']} "
                f"| {ceiling['onsets_flagged_at_h_ge_2']} ({ceiling['of_which_on_a_risk_date']} / {ceiling['of_which_off_a_risk_date']}) |"
            )
        lines.append("")
    lines += ["## 2020 false-alarm days by as-of scarcity state", ""]
    for key, rows in result["scarcity_2020"].items():
        lines += [f"### {key}", "", "| row | worst horizon | false alarms there | by state | flagged at any horizon | by state |", "|---|---|---|---|---|---|"]
        for n, c in rows.items():
            lines.append(
                f"| {n} | {c['worst_horizon']} | {c['worst_horizon_false_alarms']} | {c['worst_horizon_by_state']} "
                f"| {c['any_horizon_false_alarms']} | {c['any_horizon_by_state']} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_command(args) -> int:
    document = committed_declaration(DECLARATION)
    args.markdown.write_text(markdown(json.loads(args.result.read_text()), document), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="read tier 1 under the declared readings")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--bench", required=True)
    score.add_argument("--risk", required=True)
    score.add_argument("--row", action="append", default=[])
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.set_defaults(func=score_command)
    render = sub.add_parser("render", help="write the Markdown tables from a score's JSON")
    render.add_argument("result", type=Path)
    render.add_argument("--markdown", type=Path, required=True)
    render.set_defaults(func=render_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
