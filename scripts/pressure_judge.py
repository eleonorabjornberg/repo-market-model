"""The pressure-day judge (#375): score candidates under #374's declared bar.

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`. The bar, the thresholds,
the horizons and the rule that chooses every flagging cut-off are in `metadata/pressure_judge.json`, and each
candidate in a file of its own under `metadata/pressure_judge/candidates/`, all of which this script refuses to read unless it is committed and unchanged: a
declaration is made before scoring, not edited beside it.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PANEL --horizon H \
        --output OUT/forecasts_hH.json [--published]
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL \
        --output OUT/judge.json --markdown OUT/judge.md OUT/forecasts_h1.json ... OUT/forecasts_h5.json

`forecasts` scores the two benchmarks at one horizon (`pressure_judge.benchmark_forecasts`)
and, with `--published`, the current published probability (pressure model v1:
the published funding declaration's distribution, conformal PID with nested
selection, recalibrated out of fold; `scripts/pressure_model_v1.py publish`) as
the `published_v1` baseline row. Its output has the shape of
`pressure_model_v1.py horizon`'s `forecasts` block, so a candidate track writes
its own forecasts in that shape and passes the file to `judge`.

`judge` reads the forecast files, builds the shared grid at each horizon (the
declared groupings: year regimes, the reserve-scarcity state of #115 read as of
each forecast's decision instant, the pressure-day type, and the scheduled risk
dates), and writes the evidence of Eleonora's replacement bar (tiers 1 to 5 and
the pass rule) for every declared candidate. Scored days are before 2026-01-01
(`docs/decisions/lockbox.md`, #374); `--confirmation` is the single look at
2026-01-01 to 2026-09-03 and scores only the candidates the declaration names
for it. The flag cut-off of every row is chosen by the declaration's `cutoff_rule`, refit by refit, from
the days before the refit (`pressure_judge.choose_cutoffs`, #407); the look reads the development days as
training and scores its window only.

    PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json [--horizon H] [--output OUT/tables.md]

`table` prints the verdicts of a `judge` file in one row per model, then the models split by regime and
pressure-day type (the table a pull request carries).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.exploration import panel_end  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
EVENTS = REPO / "metadata" / "events.json"
THRESHOLDS = REPO / "metadata" / "stress_thresholds.json"
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_committed_declaration(path: Path, repo: Path = REPO) -> str:
    """The commit that last changed the declaration, refusing one that is not committed.

    The declaration is its own file and every candidate's file under `metadata/pressure_judge/candidates/`
    (`pressure_judge.declaration_files`); a candidate file that is untracked, modified or staged-only is
    refused, so no candidate is scored before it is committed.

    Raises:
        SystemExit: if any of them differs from `HEAD` or is untracked.
    """

    repo = Path(repo).resolve()
    relatives = [str(Path(path).resolve().relative_to(repo))]
    directory = pj.candidates_directory(path)
    relatives.append(str(directory.resolve().relative_to(repo)))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", *relatives],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(
            f"{' and '.join(relatives)} is not committed ({dirty}); the judge's declaration, and each "
            f"candidate's file, is committed before any score is computed"
        )
    return subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", *relatives], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def require_committed_file(path: Path, repo: Path = REPO) -> None:
    """Refuse a file that is untracked or differs from `HEAD`: a rule is committed before it scores anything."""

    relative = str(Path(path).resolve().relative_to(Path(repo).resolve()))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", relative],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a rule is committed before any score is computed")


def _document(horizon, digest, forecasts):
    return {
        "horizon": horizon,
        "panel_sha256": digest,
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
            for forecast in forecasts
        },
    }


def _published(rows, splits, registry, horizon, declaration, end):
    """The published probability: pressure model v1's recalibrated distributional gbm.

    The same run as `pressure_model_v1.py publish`, which writes a record and
    not the per-day probabilities this judge needs.
    """

    from repo_model import ml, pressure
    from repo_model.baseline import rolling_exceedance_backtest
    from repo_model.recalibration import NestedFoldPid

    model = _load_script("pressure_model_v1")
    features = model._at_horizon(model.GBM_FEATURES, horizon)
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY))
        return built[-1]

    raw = rolling_exceedance_backtest(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(name for name in features if name != "spread_bps"), minimum_history=MINIMUM_HISTORY
        ),
        model_name="distributional_gbm",
        features=features,
        registry=registry,
        decision_time=DECISION,
        taus=declaration.thresholds,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=end,
        horizon=horizon,
        online_calibration=online,
    )
    return pj.report_forecast("published_v1", pressure.recalibrated(raw))


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    end = declaration.confirmation_last if args.confirmation else declaration.last_day
    if args.end is not None:
        if args.confirmation:
            raise SystemExit("--end is a scratch scored span for development days; the confirmation look keeps the declared window")
        end = panel_end(args.end, end, where="pressure_judge.forecasts")
    forecasts = pj.benchmark_forecasts(
        declaration, rows, splits, registry, horizon=args.horizon,
        decision_time=DECISION, minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY, end=end,
    )
    if args.published:
        forecasts.append(_published(rows, splits, registry, args.horizon, declaration, end))
    document = _document(args.horizon, panel_sha256(args.panel), forecasts)
    document["declaration_commit"] = commit
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "models": sorted(document["forecasts"]), "output": str(args.output)}))
    return 0


#: Set to `same_row` (by `scripts/own_leg_rescore.py`) to read the state the way it was read before #586, for a
#: before-and-after comparison on the same forecasts. Unset, the state is the own-leg read.
STATE_READ_VARIABLE = "RMM_SCARCITY_READ"


def _scarcity_states(horizon, last_day):
    """{day: state} on the shared grid, each leg read at its own latest public row (#586).

    Eleonora's ruling on #571 (relayed 11 October 2026): the reserves, the H.8 total assets and the
    day's ON RRP are each read as of the forecast's decision instant at `horizon`, not all at the row
    the H.8 lag picks. `_same_row_scarcity_states` is the read this replaces, kept to count the days
    that change.
    """

    from repo_model.scarcity import measurement_declaration, own_leg_states

    if os.environ.get(STATE_READ_VARIABLE) == "same_row":
        return _same_row_scarcity_states(horizon, last_day)
    validation = _load_script("scarcity_validation")
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _, registry, decision = validation.build_measurement_panel(REGISTRY, Path(tmp))
        scored = own_leg_states(
            build.observations, registry=registry, decision_time=decision,
            minimum_history=MINIMUM_HISTORY, horizon=horizon, end=last_day,
        )
    return {entry.day: entry.state for entry in scored}


def _same_row_scarcity_states(horizon, last_day):
    """{day: state} as read before #586: the `reserve_scarcity_state` column, one row for all three legs."""

    from repo_model.asof import InformationRule
    from repo_model.baseline import _as_of_folds
    from repo_model.scarcity import (
        RESERVE_SCARCITY_STATE, measurement_declaration, with_reserve_scarcity_state,
    )

    validation = _load_script("scarcity_validation")
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _, registry, decision = validation.build_measurement_panel(REGISTRY, Path(tmp))
        rows = with_reserve_scarcity_state(build.observations)
        rule = InformationRule(
            registry, ("spread_bps", RESERVE_SCARCITY_STATE), decision_time=decision, horizon=horizon
        )
        states = {}
        for fold in _as_of_folds(
            rows, rule, minimum_history=MINIMUM_HISTORY, refit_every=len(rows),
            entry="pressure_judge.scarcity_state", end=last_day,
        ):
            states[rows[fold.index].date] = fold.feature_row.values.get(RESERVE_SCARCITY_STATE)
    return states


def _holdouts():
    document = json.loads(EVENTS.read_text())
    return {
        window["name"]: (date.fromisoformat(window["start"]), date.fromisoformat(window["end"]))
        for window in document["windows"]
    }


def judge_command(args) -> int:
    declaration = pj.load_declaration()
    commit = require_committed_declaration(pj.DEFAULT_DECLARATION)
    # The weighted miss rule (#454): `declared` follows the switch in metadata/weighted_miss.json (on: the weighted
    # count decides, and the flat count is reported beside it); `weighted` and `unweighted` force it
    # for one scratch run, which is how a candidate is scored under both rules.
    require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    applied = {"declared": None, "weighted": True, "unweighted": False}[args.rule]
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=applied))
    if args.confirmation and declaration.weighting_applied and applied is not None:
        raise SystemExit(
            "the weighted rule is forced on for a scratch run and is not scored on the 2026 confirmation tier: "
            "adopting it there changes a pre-registered test and needs Eleonora's own attested approval (#256)"
        )
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)

    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    # The flag cut-off of every forecast is chosen refit by refit from the development days before it
    # (`pressure_judge.choose_cutoffs`), on a grid of all the days the forecast file holds; the single
    # look then scores the declared window and nothing else.
    last = declaration.confirmation_last if args.confirmation else declaration.last_day
    states = {horizon: _scarcity_states(horizon, last) for horizon in declaration.horizons}

    def grids_of(forecasts):
        out = {}
        for horizon in declaration.horizons:
            reference = next(f for f in forecasts if f.horizon == horizon and f.name == declaration.climatology)
            out[horizon] = pj.build_grid(
                declaration, horizon, rows, reference.dates, splits, scarcity_state=states[horizon]
            )
        return out

    calendar = [row.date for row in rows]
    forecasts = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    if args.confirmation:
        forecasts = [
            pj.restrict_forecast(f, declaration.confirmation_first, declaration.confirmation_last)
            for f in forecasts
        ]
    grids = grids_of(forecasts)
    result = pj.judge(
        declaration, grids, forecasts,
        calendar=calendar, holdouts=_holdouts(), confirmation=args.confirmation,
    )
    result["provenance"] = {
        "panel_sha256": digest,
        "declaration_commit": commit,
        "forecast_files": [str(p) for p in args.inputs],
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "mode": result["mode"],
        "verdicts": {name: c["verdict"]["passes"] for name, c in result["candidates"].items()},
    }))
    return 0


# -- the summary --------------------------------------------------------------


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _cell(cell):
    if cell is None:
        return "–"
    if "interval" in cell:
        i = cell["interval"]
        return f"{cell['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"
    return f"{_f(cell['mean'], 4)} (no interval)"


def _yes(value):
    return "–" if value is None else ("yes" if value else "no")


def _scarce_line(scarce):
    """The pass within the scarce regime alone: reported, not part of the pass rule."""

    if "unavailable" in scarce:
        return f" Scarce regime alone (reported only): {scarce['unavailable']}."
    return (
        f" Scarce regime alone (state >= {scarce['scarcity_state_at_least']}, reported only): "
        f"{'pass' if scarce['passes'] else 'fail'} (tier 1 {_yes(scarce['tier_1_onset_warning'])}, "
        f"tier 3 {_yes(scarce['tier_3_no_crying_wolf'])}, tier 5 {_yes(scarce['tier_5_week_ahead'])}; "
        f"{scarce['onsets']} onsets)."
    )


def _cutoff(summary):
    """The cut-offs chosen over the scored days: their median, and the days that flag nothing."""

    median = "–" if "median" not in summary else f"{summary['median']:.3g}"
    return f"{median} ({summary['days_never_flag']} of {summary['days']} days never flag)"


def _pooled_alarms(cell) -> str:
    """Tier 1's false alarms per onset as the rule counts them (#509): a day flagged at any horizon is one."""

    if "pooled_false_alarms_per_onset" not in cell:
        return _f(cell.get("worst_false_alarms_per_onset"), 2)
    shown = _f(cell["pooled_false_alarms_per_onset"], 2)
    if "pooled_weighted_false_alarms_per_onset" in cell:
        shown += f" flat / {_f(cell['pooled_weighted_false_alarms_per_onset'], 2)} weighted"
    return shown


def _interval(stat) -> str:
    if not stat:
        return "–"
    interval = stat.get("interval")
    return f"{_f(stat['mean'], 3)}" + (f" [{interval['lower']:.3f}, {interval['upper']:.3f}]" if interval else " (no interval)")


def _span_line(label: str, cell) -> str:
    """One line of tier 1 on a span of days: onsets warned, recall with its interval, false alarms per onset (flat / weighted)."""

    if "onsets_flagged" not in cell:
        return f"| {label} | {cell.get('onsets', 0)} | – | – | – | – |"
    alarms = cell["false_alarms_per_onset"]
    weighted = alarms.get("weighted")
    return (
        f"| {label} | {cell['onsets']} | {cell['onsets_flagged']:g} | {_interval(cell['recall'])} | "
        f"{_interval(alarms['flat'])} | {_interval(weighted) if weighted else '–'} |"
    )


SPAN_HEAD = (
    "| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |\n"
    "|---|---|---|---|---|---|"
)


def tier1_lines(onset) -> List[str]:
    """The lines every judge table adds to tier 1 (rulings of 10 October 2026): each lead alone, inside and outside the
    early years (#510), and the recall with equal weight per regime. Empty for a result written before them."""

    cell = onset.get("lead_at_least_1") or next(iter(onset.values()), {})
    if "per_lead" not in cell:
        return []
    lines = [SPAN_HEAD]
    for h, lead in cell["per_lead"].items():
        passes = lead.get("passes")
        lines.append(_span_line(f"lead {h} alone" + ("" if passes is None else f" ({'pass' if passes else 'fail'})"), lead))
    years = cell["early_years"]
    span = "-".join(str(y) for y in (years["years"][0], years["years"][-1]))
    lines.append(_span_line(f"inside {span}", years["inside"]))
    lines.append(_span_line(f"outside {span}", years["outside"]))
    equal = cell.get("regime_equal_weight_recall")
    if equal:
        parts = ", ".join(
            f"{label} {c['onsets_flagged']:g}/{c['onsets']}" for label, c in equal["regimes"].items()
        )
        lines += ["", f"Recall with equal weight per regime: {_f(equal['recall'], 3)} ({parts})."]
    return lines


def markdown(result) -> str:
    declaration = result["declaration"]
    primary = f"{declaration['primary_threshold_bp']:g}"
    tiers = declaration["tiers"]
    lines = [
        "# Pressure-day judge (#375)",
        "",
        f"Mode: {result['mode']}. Declaration `{declaration['path']}` sha256 `{declaration['sha256'][:12]}…`. "
        f"Scored days {result['scored_window']['first']} to {result['scored_window']['last']}. "
        f"Pass rule: tier 1 (onset warning) at lead >= {tiers['onset_warning']['lead_at_least']}, tier 3 (no crying wolf) "
        f"at every lead, and tier 5 (week-ahead window), at +{primary} bp; {declaration['bootstrap']['level']:.0%} "
        "stationary bootstrap intervals.",
        "",
    ]
    for name, candidate in result["candidates"].items():
        verdict = candidate["verdict"]
        near_key = f"lead_at_least_{tiers['onset_warning']['lead_at_least']}"
        far_key = f"lead_at_least_{tiers['onset_warning']['far_lead_at_least']}"
        onset = candidate["tiers"]["onset_warning"]
        lines += [
            f"## {name} ({candidate['role']}): {'PASS' if verdict['passes'] else 'FAIL'} at +{primary} bp",
            "",
            f"Tier 1 {_yes(verdict['tier_1_onset_warning'])}, tier 3 {_yes(verdict['tier_3_no_crying_wolf'])}, "
            f"tier 5 {_yes(verdict['tier_5_week_ahead'])}."
            + (f" Not scored at horizons {verdict['not_scored']}." if verdict["not_scored"] else "")
            + _scarce_line(verdict["scarce_regime"]),
            "",
            "| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |",
            "|---|---|---|---|---|---|---|",
        ]
        for key in (near_key, far_key):
            cell = onset[key]
            if "recall" not in cell:
                lines.append(f"| {key} | {cell.get('onsets', '–')} | – | {cell.get('unavailable', '–')} | | | |")
                continue
            recall = cell["recall"]
            interval = recall.get("interval")
            shown = f"{_f(recall['mean'])}" + (f" [{interval['lower']:.3f}, {interval['upper']:.3f}]" if interval else " (no interval)")
            criteria = cell.get("criteria")
            note = (
                ", ".join(f"{k} {_yes(v)}" for k, v in criteria.items()) if criteria
                else f"reported only; meets far recall: {_yes(cell.get('meets_far_recall'))}"
            )
            lines.append(
                f"| {key} | {cell['onsets']} | {cell['onsets_flagged']} | {shown} | {_f(cell['climatology_recall'])} | "
                f"{_pooled_alarms(cell)} | {note}{'' if cell['complete'] else ' (partial horizons)'} |"
            )
        extra = tier1_lines(onset)
        if extra:
            lines += ["", "Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):", ""] + extra
        lines += [
            "",
            "| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for horizon, per_tau in candidate["horizons"].items():
            row = per_tau[primary]
            paired = row["paired"]
            lines.append(
                f"| {horizon} | {_cutoff(row['cutoff'])} | {row['flags']['alarms']} | {_f(row['flags']['recall'])} | "
                f"{_f(row['flags']['precision'])} | {_f(row['brier'], 4)} | "
                f"{_cell(paired['vs_calendar_climatology']['brier_difference'])} | "
                f"{_cell(paired['vs_persistence_logistic']['brier_difference'])} | "
                f"{_f(row['auroc'])} | {_f(row['usefulness'].get('relative'))} | {_yes(row['no_crying_wolf']['ok'])} |"
            )
        lines += ["", "Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):", ""]
        for horizon, per_tau in candidate["horizons"].items():
            wolf = per_tau[primary]["no_crying_wolf"]
            stretches = "; ".join(
                f"{label}: {_f(c['flags_per_year'], 1)} over {c['days']} days" for label, c in wolf["abundant_stretches"].items()
            )
            calibrated = ", ".join(f"{k} {_yes(v)}" for k, v in wolf["calibrated_by_regime"].items())
            reported = ", ".join(
                f"{k} {_yes(v['covers_zero'])} ({v['events']} pressure days)" for k, v in wolf["calibration_reported_regimes"].items()
            )
            lines.append(
                f"- h = {horizon}: {stretches}. Calibrated (regimes with enough pressure days): {calibrated or 'none'}."
                + (f" Reported, too few pressure days to test: {reported}." if reported else "")
            )
        risky = candidate["tiers"]["risky_dates"]
        lines += ["", "Tier 2 (reported only): " + (
            risky["unavailable"] if "unavailable" in risky
            else f"h = {risky['lead']}, {risky['days']} risky dates in scarcity state >= {tiers['risky_dates']['scarcity_state_at_least']}, "
            f"AUROC {_f(risky['auroc'])} (climatology {_f(risky['climatology_auroc'])}, difference {_cell(risky['auroc_difference'])}); "
            f"meets {tiers['risky_dates']['auroc_at_least']}: {_yes(risky['meets_auroc'])}, beats climatology: {_yes(risky['beats_climatology'])}."
        )]
        week = candidate["tiers"]["week_ahead"]
        lines += ["", "Tier 5 (week-ahead window): " + (
            week["unavailable"] if "unavailable" in week
            else f"{week['days']} decision days, base rate {_f(week['base_rate'])}, Brier {_f(week['brier'], 4)}, "
            f"ΔBrier vs climatology {_cell(week['brier_difference_vs_climatology'])}, "
            f"realised minus predicted {_cell(week['realised_minus_predicted'])}; "
            + ", ".join(f"{k} {_yes(v)}" for k, v in week["criteria"].items()) + "."
        ), ""]
        first = next(iter(candidate["horizons"]))
        row = candidate["horizons"][first][primary]
        lines += [
            f"By group at h = {first}:",
            "",
            "| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for dimension, cells in row.get("splits", {}).items():
            for label, cell in cells.items():
                flags = cell["flags"]
                lines.append(
                    f"| {dimension} | {label} | {cell['days']} | {cell['events']} | {_f(flags['recall'])} | "
                    f"{_f(flags['precision'])} | {_f(cell['mean_predicted'], 4)} | {_f(cell['realised_frequency'], 4)} | "
                    f"{_cell(cell['brier_difference_vs_climatology'])} |"
                )
        if row.get("holdouts"):
            lines += ["", f"Knowledge holdouts at h = {first} (descriptive):", "", "| window | days | events | recall | precision | Brier | climatology Brier |", "|---|---|---|---|---|---|---|"]
            for window, cell in row["holdouts"].items():
                if not cell.get("days"):
                    lines.append(f"| {window} | 0 | | | | | |")
                    continue
                lines.append(
                    f"| {window} | {cell['days']} | {cell['events']} | {_f(cell['flags']['recall'])} | "
                    f"{_f(cell['flags']['precision'])} | {_f(cell['brier'], 4)} | {_f(cell['climatology_brier'], 4)} |"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def _false_alarm_cell(onset) -> str:
    """The false alarms per onset, both counts labelled and the one tier 1 is decided on named (#577).

    Tier 1 counts a day flagged at any horizon once (#509), so the pooled count is shown when the result has it and the
    worst single horizon otherwise (a result written before the ruling). Under the weighted miss rule in force the limit
    applies to the weighted count; the flat count is printed beside it. A run with no weighted rule has the flat count alone.
    """

    pooled = "pooled_false_alarms_per_onset" in onset
    flat = f"{_f(onset.get('pooled_false_alarms_per_onset' if pooled else 'worst_false_alarms_per_onset'), 2)} flat"
    weighted = onset.get("pooled_weighted_false_alarms_per_onset" if pooled else "worst_weighted_false_alarms_per_onset")
    if weighted is None:
        return f"{flat} (tier 1 on the flat count)"
    basis = "weighted" if onset.get("weighted_miss_applied") else "flat"
    return f"{flat} / {_f(weighted, 2)} weighted (tier 1 on the {basis} count)"


def summary_tables(result, horizon="1") -> str:
    """The judge's verdicts in one row per model, then the same models split by regime and pressure-day type.

    Table 1: tier 1 (recall with its interval, climatology's recall at the same false alarms, the worst
    false alarms per onset, as the flat and the weighted count with the one tier 1 is decided on named), tier 3 (the worst alarm rate in the abundant stretches over the leads, and the
    regimes with a pressure day that are calibrated at the first lead), tier 5, the pass, and the pass
    within the scarce regime alone (reported, not part of the rule). Tables 2 and 3: at `horizon`, the
    share of pressure days flagged and the Brier difference against calendar climatology (positive: the model is better,
    90% interval) in every regime and every pressure-day type.
    """

    declaration = result["declaration"]
    primary = f"{declaration['primary_threshold_bp']:g}"
    near = f"lead_at_least_{declaration['tiers']['onset_warning']['lead_at_least']}"
    lines = [
        f"Table 1. Tiers at +{primary} bp, h = 1 to 5; 90% stationary-bootstrap intervals. "
        f"The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.",
        "",
        "| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), "
        "flat count / weighted count (tier 1 is decided on the one named) "
        "| tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. "
        "| pass | scarce regime alone (tiers 1 / 3 / 5) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, candidate in result["candidates"].items():
        onset = candidate["tiers"]["onset_warning"][near]
        recall = onset.get("recall") or {}
        interval = recall.get("interval")
        shown = _f(recall.get("mean")) + (f" [{interval['lower']:.3f}, {interval['upper']:.3f}]" if interval else "")
        wolf = candidate["tiers"]["no_crying_wolf"]
        worst = {}
        for tier in wolf.values():
            for label, stretch in tier["abundant_stretches"].items():
                rate = stretch["flags_per_year"]
                worst[label] = rate if worst.get(label) is None or (rate is not None and rate > worst[label]) else worst[label]
        state0 = worst.get(f"scarcity_state_{declaration['tiers']['no_crying_wolf']['abundant_scarcity_state']}")
        regime = worst.get(f"regime_{declaration['tiers']['no_crying_wolf']['abundant_regime']}")
        first = wolf[next(iter(wolf))]
        tested = first["calibrated_by_regime"]
        week = candidate["tiers"]["week_ahead"]
        week_cell = (
            "–" if "criteria" not in week
            else f"{_yes(week['criteria']['calibrated'])}, {_yes(week['criteria']['beats_climatology_brier'])}"
        )
        verdict = candidate["verdict"]
        scarce = verdict["scarce_regime"]
        scarce_cell = (
            "unavailable" if "unavailable" in scarce
            else f"{'pass' if scarce['passes'] else 'fail'} ({_yes(scarce['tier_1_onset_warning'])} / "
            f"{_yes(scarce['tier_3_no_crying_wolf'])} / {_yes(scarce['tier_5_week_ahead'])})"
        )
        lines.append(
            f"| {name} | {onset.get('onsets_flagged', '–')} of {onset.get('onsets', '–')} | {shown} | "
            f"{_f(onset.get('climatology_recall'))} | {_false_alarm_cell(onset)} | "
            f"{_f(state0, 1)} / {_f(regime, 1)} | {sum(tested.values())} of {len(tested)} | {week_cell} | "
            f"{'PASS' if verdict['passes'] else 'fail'} (tiers {_yes(verdict['tier_1_onset_warning'])} / "
            f"{_yes(verdict['tier_3_no_crying_wolf'])} / {_yes(verdict['tier_5_week_ahead'])}) | {scarce_cell} |"
        )
    detail = {name: tier1_lines(c["tiers"]["onset_warning"]) for name, c in result["candidates"].items()}
    if any(detail.values()):
        lines += [
            "",
            "Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight "
            "per regime: reported for every model, not part of the pass rule.",
        ]
        for name, rows in detail.items():
            if rows:
                lines += ["", f"{name}:", ""] + rows
    labels = {}
    for candidate in result["candidates"].values():
        splits = candidate["horizons"].get(horizon, {}).get(primary, {}).get("splits", {})
        for dimension in ("regime", "day_type"):
            for label in splits.get(dimension, {}):
                labels.setdefault(dimension, [])
                if label not in labels[dimension]:
                    labels[dimension].append(label)
    columns = [(d, label) for d in ("regime", "day_type") for label in labels.get(d, [])]
    for title, render in (
        (f"Table 2. Share of the pressure days flagged at h = {horizon} (+{primary} bp), by regime and pressure-day type; the number of pressure days in the group in brackets.",
         lambda cell: "–" if not cell["events"] else f"{_f(cell['flags']['recall'], 2)} ({cell['events']})"),
        (f"Table 3. Brier difference against calendar climatology at h = {horizon} (+{primary} bp), by regime and pressure-day type "
         "(positive: better than climatology; 90% interval).",
         lambda cell: _cell(cell["brier_difference_vs_climatology"])),
    ):
        lines += [
            "",
            title,
            "",
            "| model | " + " | ".join(f"{d}: {label}" for d, label in columns) + " |",
            "|---|" + "---|" * len(columns),
        ]
        for name, candidate in result["candidates"].items():
            splits = candidate["horizons"].get(horizon, {}).get(primary, {}).get("splits", {})
            cells = [
                render(splits[d][label]) if d in splits and label in splits[d] else "–" for d, label in columns
            ]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def table_command(args) -> int:
    result = json.loads(args.judge.read_text())
    text = summary_tables(result, args.horizon)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.add_argument("--published", action="store_true")
    forecasts.add_argument("--end", help="last scored day, ISO; default the committed declaration's own (at most 2026-09-03, #684: a scratch scored span, no published declaration moves)")
    forecasts.add_argument(
        "--confirmation", action="store_true",
        help="score walk-forward through the confirmation window's last day (for the single look)",
    )
    forecasts.set_defaults(run=forecasts_command)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True)
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument(
        "--confirmation", action="store_true",
        help="the single look at the declared confirmation window, for the declared candidates only",
    )
    judge.add_argument(
        "--rule", choices=("declared", "weighted", "unweighted"), default="declared",
        help="how false alarms count (#454): as the switch in metadata/weighted_miss.json says (default), or forced",
    )
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(run=judge_command)
    table = commands.add_parser("table", help="the judge's verdicts in one row per model, split by regime and day type")
    table.add_argument("judge", type=Path, help="a judge.json written by `judge`")
    table.add_argument("--horizon", default="1")
    table.add_argument("--output", type=Path)
    table.set_defaults(run=table_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
