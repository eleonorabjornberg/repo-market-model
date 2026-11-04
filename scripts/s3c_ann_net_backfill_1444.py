"""(s3c-ann-net) trained on the admitted 2014-18 back-filled history: a scratch measurement (#1444; H4 step 3, on the H5 candidate; #1223).

A development study and a scratch measurement, never a verdict. Her ruling of 26 October 2026 (ledger item 56 on #1116, option 1): IOER/IORB on back-filled
rows is admitted as training history only (the amendment merged as #1230 / PR #1268), and the measurement was then queued. Nothing is adopted and the frozen
candidate does not change. Every choice is in `metadata/s3c_ann_net_backfill_1444.json`, which this script refuses to read unless it is committed and unchanged.

The control is (s3c-ann-net) as #1288 / #1319 / #1314 walk it, run unchanged by `scripts/s3c_announced_settlement_1288.py` on the published panel at the 18:00
decision instant. The arm, (s3c-ann-net+bf), is the same model on the same decision days, the same refit days and the same cap at the SRF line, with the
back-filled rows (2014-08-22 to 2018-03-29) before the published rows in every training frame. What this script adds:

* the extended term table (`ExtendedTermTable`): the published table's rows, with the back-filled rows before them; a back-filled row carries `quarter_end` and
  `tax_date` from its own calendar columns and `dom_19_23` from its date, and no flag for the settlement and market-holiday terms;
* the two-stage refit (`two_stage`): the settlement terms (net coupon and net bill settlement) and the two market-holiday terms (`month_end`,
  `post_month_end_window`: the pinned holiday table starts on 2018-01-01) are fitted on the pairs whose target row is a published row only (stage 1, the
  arm's own fit); the three terms the back-filled rows carry are then fitted on every pair, on the residual net of the stage-1 effects of the four others
  (stage 2). The forecast reads both sets of effects and the stage-2 pool;
* the pressure-day types of the back-filled days (`back_filled_turn_days`): the model's level is the median of the last ordinary spreads, and a day is ordinary
  unless it is a turn day or a tax date, which needs the month's last business day; the pinned market holiday table starts on 2018-01-01, so before it a month's
  business days are the panel's own days (the rule of `scripts/backfill_history.py` for `quarter_end`);
* the guards of the back-fill rule, on every refit and every scored decision (`require_backfill_guards`, `require_published_targets`,
  `require_backfilled_admitted` of `scripts/backfill_h5_726.py`);
* the walk (`walk_extended`: `spread_mr_state_calendar.walk` with that refit), the paired scores against the control and B1'*, the split by regime (2018-19,
  2018 H2), pressure-day type and target-day type, the two named quarter-ends (2018-09-28 and 2018-12-31), the terms that entered each refit, and the
  2018-19 coverage of the central 90% band.

Commands, from a clone of the branch (about twenty to forty minutes in a cloud session, the walks and the paired tests; no step is expected to run over two
hours):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
    PYTHONPATH=src python3 scripts/s3c_ann_net_backfill_1444.py panel --extended EXT.csv --published PUB.csv --output EST.csv
    PYTHONPATH=src python3 scripts/s3c_ann_net_backfill_1444.py score --panel PUB.csv --extended EST.csv \\
        --output docs/research/s3c-ann-net-backfill-1444/result.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_backfill_1444.py page \\
        --score docs/research/s3c-ann-net-backfill-1444/result.json --output docs/research/s3c-ann-net-backfill-1444-result.md

Stdlib only. The fit is `spread_mr_state_calendar.fit_state_terms`, on direct pairs (`training_pairs='direct'`): the one-step guard is met and no allow-list entry
is used or added. No gradient-boosted fitter is called.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import dataclasses
import importlib.util
import json
import multiprocessing
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, backfill, b1_calendar, metrics, policy_events, s3c_announced, s3c_net  # noqa: E402
from repo_model import data, protocol_benchmarks as pb, scoring_protocol as sp, spread_mean_reversion as smr, spread_mr_fhs as fhs  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc, turn_days  # noqa: E402
from repo_model.baseline import ScoredFold, panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

#: #1288's script (the walks, the frame, the cell table, the paired tests) and #726's (the back-fill panel checks), each under an alias of its own so that the
#: pickling of the worker pool's tasks does not meet another test module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1444")
b726 = _load("backfill_h5_726", "backfill_h5_726_in_1444")
m1273, m1255, k, c, s686, s761 = m1288.m1273, m1288.m1255, m1288.k, m1288.c, m1288.s686, m1288.s761

DECLARATION = REPO / "metadata" / "s3c_ann_net_backfill_1444.json"
POSTING = REPO / "metadata" / "backfill_posting.json"
SEED = m1288.SEED
LAST_DAY = m1288.LAST_DAY
WINDOWS = m1288.WINDOWS
WINDOW_LAST = m1288.WINDOW_LAST
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
CONTROL = m1288.ANNNET
ARM = "sc_s3c_ann_net_bf"
REFERENCE = "B1'*"
MODELS = (CONTROL, ARM, REFERENCE)
LABELS = {CONTROL: "(s3c-ann-net)", ARM: "(s3c-ann-net+bf)", REFERENCE: "B1'*"}
NET_ARM = s3c_announced.ANN_NET_ARM

#: The instant this study is made at: the repository's decision instant since #1312.
INSTANT_TIME = time(18, 0)
INSTANT_TEXT = INSTANT_TIME.isoformat(timespec="minutes")

#: The terms a back-filled row carries a flag for: its own `quarter_end` and `tax_date` columns, and the day of the month. The settlement terms have no column on a
#: back-filled row and the two market-holiday terms need the pinned holiday table, which starts on 2018-01-01: those four are fitted on published targets only.
A_TERMS: Tuple[str, ...] = ("quarter_end", "tax_date", "dom_19_23")
#: The fields the model reads, which the extended panel's published rows must carry as the published panel does.
READ_FIELDS = ("sofr", "iorb", "quarter_end", "tax_date", "days_to_month_end", "treasury_settlement_bills", "treasury_settlement_coupons")
#: Sub-windows of a regime that the study names (declared): the second half of 2018 inside 2018-19.
H2_2018 = (date(2018, 7, 1), date(2018, 12, 31))
NAMED_TARGETS = (date(2018, 9, 28), date(2018, 12, 31))
HEADLINE_REGIME = "2018-19"


# -- the guards ----------------------------------------------------------------------------------------------------------


def require_instant(decision_time: time) -> None:
    """Refuse to make an 18:00 study at another decision instant.

    Raises:
        ValueError: the repository's decision instant is not the declared one.
    """

    if decision_time != INSTANT_TIME:
        raise ValueError(f"this study is made at {INSTANT_TEXT}; the repository's decision instant is {decision_time.isoformat(timespec='minutes')}")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def require_published_targets(pairs: Sequence[sc.StatePair], prefix: int, *, where: str) -> None:
    """Refuse a pair whose target is a back-filled row in a fit of the settlement and market-holiday terms.

    A back-filled row has no settlement column (information-set.md, back-fill amendment, item 4) and no market-holiday flag, so such a pair read there as
    'no settlement' would teach the fit that settlement days are ordinary days.

    Raises:
        LookAheadError: a pair's target row is before `prefix`, the first published row.
    """

    for pair in pairs:
        if pair.target < prefix:
            raise LookAheadError(f"{where}: a pair with target row {pair.target} (a back-filled row, before row {prefix}) is in a fit of terms that are not fitted on back-filled rows")


def require_backfill_guards(
    dates: Sequence[date], anchor: int, day: date, posting: Optional[datetime], admitted: Mapping[str, datetime], reads: Sequence[str], *, where: str
) -> None:
    """The back-fill rule for one refit: the fit trains on rows from the first back-filled row to the anchor.

    Raises:
        LookAheadError: the workbook's posting instant is undeclared or later than the start of the day the training ends, or a series the fit reads is not
            admitted (`backfill.require_posting_established`, `backfill.require_series_admitted`).
    """

    fold = ScoredFold(train_start=dates[0], train_end=dates[anchor], train_rows=anchor + 1, feature_date=dates[anchor], scored_date=day)
    backfill.require_posting_established([fold], posting, where=where)
    backfill.require_series_admitted([fold], reads, admitted, where=where)


def require_same_refits(control: Sequence[date], arm: Sequence[date]) -> None:
    """The arm refits on the control's refit days: a different set is a different experiment.

    Raises:
        ValueError: the two lists of refit days differ.
    """

    if list(control) != list(arm):
        raise ValueError(f"the arm's refit days are not the control's: {sorted(set(control) ^ set(arm))[:5]} differ")


def require_same_published(published: Sequence[DailyObservation], extended: Sequence[DailyObservation], fields: Sequence[str] = READ_FIELDS) -> int:
    """The extended panel is back-filled rows followed by the published panel, cell for cell in `fields`. Returns the number of back-filled rows.

    Raises:
        ValueError: no back-filled row, a back-filled row after the first published day, or a published row that differs.
    """

    prefix = backfill.prefix_length([row.date for row in extended])
    if prefix == 0:
        raise ValueError("the extended panel has no back-filled row")
    rows = extended[prefix:]
    if [row.date for row in rows] != [row.date for row in published]:
        raise ValueError("the extended panel's published days are not the published panel's days")
    for mine, theirs in zip(published, rows):
        for name in fields:
            a, b = mine.values.get(name), theirs.values.get(name)
            if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9):
                raise ValueError(f"{mine.date} {name}: published {a!r} != extended {b!r}")
    return prefix


# -- the pressure-day types of the back-filled days ----------------------------------------------------------------------


@contextlib.contextmanager
def back_filled_turn_days(dates: Sequence[date]):
    """Serve `turn_days.turn_days_of_month` for the months the pinned market holiday table does not cover (it starts on 2018-01-01) from the panel's own days.

    The model's level is the median of the last ordinary spreads, and a row is ordinary unless it is a turn day or a tax date (`turn_days.reporting_day_type`),
    so the fit cannot read a back-filled row without knowing its month's last business day. The scratch panel of #430 has the same gap for `quarter_end` and
    closes it the same way (`scripts/backfill_history.py`): the business days of a back-filled month are the days the New York Fed's workbook has a rate for. A
    month the table covers is served by the table, unchanged. The table itself is not extended: that is a data decision of hers.

    Raises:
        ValueError: (inside the block) a month with no panel day before 2018, or no panel day after its last.
    """

    first = data.market_holidays().first
    by_month: Dict[Tuple[int, int], List[date]] = {}
    for day in dates:
        by_month.setdefault((day.year, day.month), []).append(day)
    ordered = sorted(dates)
    original = turn_days.turn_days_of_month

    def served(year: int, month: int) -> Tuple[date, date]:
        if date(year, month, 1) >= first:
            return original(year, month)
        days = by_month.get((year, month))
        if not days and date(year, month, 1) < ordered[0]:
            return date.min, date.min  # a month before the panel starts: its turn days fall on no panel day
        if not days:
            raise ValueError(f"no panel day in {year}-{month:02d}: its turn days cannot be read from the panel's own days")
        last = max(days)
        later = next((d for d in ordered if d > last), None)
        if later is None:
            raise ValueError(f"no panel day after {last}: the turn day after the month's last business day cannot be read")
        return last, later

    turn_days.turn_days_of_month = served
    try:
        yield
    finally:
        turn_days.turn_days_of_month = original


# -- the extended term table ---------------------------------------------------------------------------------------------


def prefix_flags(rows: Sequence[DailyObservation], names: Sequence[str]) -> Dict[str, List[int]]:
    """The flag of each term at each back-filled row: `quarter_end` and `tax_date` from the row's own columns, `dom_19_23` from its date, the others 0 (they are
    not fitted on back-filled rows)."""

    out: Dict[str, List[int]] = {}
    for name in names:
        if name in ("quarter_end", "tax_date"):
            out[name] = [1 if (row.values.get(name) or 0.0) > 0 else 0 for row in rows]
        elif name == "dom_19_23":
            out[name] = [1 if 19 <= row.date.day <= 23 else 0 for row in rows]
        else:
            out[name] = [0] * len(rows)
    return out


class ExtendedTermTable(s3c_announced.AnnouncedTermTable):
    """`AnnouncedTermTable` of the published panel with the back-filled rows before it.

    Every row of the published panel is served exactly as that table serves it (the announced settlement terms included); a back-filled row carries the flags of
    `prefix_flags`. The table is built on the published panel, because the market holiday table behind `month_end` and `post_month_end_window` starts on
    2018-01-01; the rows it adds are never read for those two terms by a fit (`two_stage`).
    """

    def __init__(self, published: Sequence[DailyObservation], extended: Sequence[DailyObservation], announcements, results, *, decision_time: time):
        super().__init__(published, announcements, results, decision_time=decision_time)
        self.prefix = require_same_published(published, extended)
        old = extended[: self.prefix]
        flags = prefix_flags(old, [term.name for term in cal.TERMS])
        for (term, lead), values in list(self._flags.items()):
            unreadable = all(v is None for v in values)
            self._flags[(term, lead)] = ([None] * self.prefix if unreadable else flags[term]) + list(values)
        self.dates = [row.date for row in old] + list(self.dates)


# -- the two-stage refit -------------------------------------------------------------------------------------------------


def known_terms(location: Sequence[str]) -> Tuple[str, ...]:
    """The arm's terms a back-filled row carries a flag for."""

    return tuple(name for name in location if name in A_TERMS)


def unknown_terms(location: Sequence[str]) -> Tuple[str, ...]:
    """The arm's terms fitted on published targets only: the settlement terms and the market-holiday terms."""

    return tuple(name for name in location if name not in A_TERMS)


def two_stage(pairs: Sequence[sc.StatePair], prefix: int, arm: sc.StateArm, lead: int) -> sc.StateEstimate:
    """One lead's estimate of `arm` with the back-filled pairs (target row before `prefix`) in the fit of `known_terms` only.

    Stage 1 is the arm's own fit (`sc.fit_state_terms`) on the published-target pairs; it keeps the effects of `unknown_terms`. Stage 2 fits `known_terms` on every
    pair, on the pair's residual net of the stage-1 effects of `unknown_terms` where the pair's row carries them. The estimate holds both sets of effects and the
    stage-2 pool, the standardised residual after all of them.

    Raises:
        LookAheadError: a stage-1 pair has a back-filled target (cannot arise from the split below; the guard stays for a changed split).
        InsufficientHistory: no published-target pair.
    """

    published = [pair for pair in pairs if pair.target >= prefix]
    require_published_targets(published, prefix, where="stage 1 of the two-stage refit")
    common = dict(interact=arm.interact, robust=arm.robust, training_pairs="direct", ridge=arm.ridge, calendar_k=arm.calendar_k)
    first = sc.fit_state_terms(published, regressors=cal.regressors_of(arm, lead), terms=arm.location, sized=arm.sized, extra=arm.extra, **common)
    unknown, known = unknown_terms(arm.location), known_terms(arm.location)
    adjusted = []
    for pair in pairs:
        if pair.target >= prefix:
            shift = sum(first.effect[n] * sc.regressor(n, pair.flags, pair.sizes, pair.state, arm.sized) for n in unknown if n in first.effect)
            adjusted.append(pair._replace(raw=pair.raw - pair.scale * shift))
        else:
            adjusted.append(pair)
    second_arm = dataclasses.replace(arm, name=arm.name + "_known", location=known, sized=False)
    second = sc.fit_state_terms(adjusted, regressors=cal.regressors_of(second_arm, lead), terms=known, sized=False, extra=(), **common)
    effect = {**{n: first.effect[n] for n in unknown if n in first.effect}, **second.effect}
    ordered = tuple(n for n in cal.ALL_TERMS if n in effect)
    flagged = {**{n: v for n, v in first.flagged.items() if n in unknown}, **{n: v for n, v in second.flagged.items() if n in known}}
    return dataclasses.replace(second, terms=ordered, effect={n: effect[n] for n in ordered}, flagged=flagged, pairs=len(pairs), sized=arm.sized)


def refit_extended(
    panel: Sequence[DailyObservation], decision_index: int, table: ExtendedTermTable, states, arm: sc.StateArm, *, registry, decision_time, levels, base: smr.Fit,
    sizes,
) -> Dict[int, sc.StateEstimate]:
    """`spread_mr_state_calendar.refit` for one sized arm with `two_stage` in place of the single fit: each lead's estimate as of the decision on `decision_index`.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale reads is after the anchor, or a state is read after the decision.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in LEADS for origin, _ in rows[h]} | {anchor})
    variant = sc.BASE_VARIANT
    read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, variant)
    out: Dict[int, sc.StateEstimate] = {}
    for h in LEADS:
        k_ = h + lag
        pairs = []
        for origin, target in rows[h]:
            scale = reader.at(origin)
            if scale is None:
                continue
            raw = (spreads[target] - levels[origin]) - base.phi**k_ * (spreads[origin] - levels[origin])
            state = sc.level(sc.pair_state(states, dates, origin, lag, decision_index))
            size = sizes.sizes_at(h, target) if target >= table.prefix else {}
            pairs.append(sc.StatePair(raw, scale, table.flags_at(h, target), state, size, origin, target))
        if not pairs:
            raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
        out[h] = two_stage(pairs, table.prefix, arm, h)
    return out


@dataclasses.dataclass(frozen=True)
class ExtendedWalk:
    forecasts: Dict[date, Dict[int, List[float]]]
    #: Refit day -> lead -> the estimate.
    estimates: Dict[date, Dict[int, sc.StateEstimate]]
    skipped: Tuple[date, ...]


def walk_extended(
    panel: Sequence[DailyObservation], decision_days: Sequence[date], table: ExtendedTermTable, states, arm: sc.StateArm, *, registry, decision_time,
    splits, sizes, posting: Optional[datetime], admitted: Mapping[str, datetime], reads: Sequence[str], refit_every: int = smr.REFIT_EVERY,
) -> ExtendedWalk:
    """`spread_mr_state_calendar.walk` for one arm on the extended panel: the same refit rule (a refit every `refit_every` forecast days), the two-stage refit,
    and the back-fill guards on every refit.

    Raises:
        LookAheadError: a guard.
        ProtocolError: a decision day that is not a panel day.
    """

    position = {row.date: index for index, row in enumerate(panel)}
    dates = [row.date for row in panel]
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    estimates: Dict[date, Dict[int, sc.StateEstimate]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_estimates: Dict[str, Dict[int, sc.StateEstimate]] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise sp.ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                anchor = pb._anchor(panel, index, registry, decision_time)
                require_backfill_guards(dates, anchor, day, posting, admitted, reads, where="s3c_ann_net_backfill_1444")
                found = refit_extended(panel, index, table, states, arm, registry=registry, decision_time=decision_time, levels=levels, base=base, sizes=sizes)
                current, current_estimates = base, {arm.name: found}
                estimates[day] = found
                since = 0
            mine, _detail = sc.forecast(
                panel, index, current_estimates, table, states, (arm,), registry=registry, decision_time=decision_time, levels=levels, base=current, sizes=sizes)
        except smr.InsufficientHistory:
            skipped.append(day)
            continue
        except LookAheadError:
            raise
        except SplitError:
            if current is not None:
                raise
            skipped.append(day)
            continue
        since += 1
        forecasts[day] = mine[arm.name]
    return ExtendedWalk(forecasts, estimates, tuple(skipped))


# -- the readings --------------------------------------------------------------------------------------------------------


def reading(row: Optional[Mapping[str, object]]) -> str:
    """`gain` when the studentized interval of the difference (reference less arm; positive favours the arm) is wholly above zero, `cost` when wholly below,
    `undecided` otherwise; `identical` for a group the two score alike on every day, `not read` where the interval is undefined."""

    if row is None:
        return "not read"
    if row.get("identical"):
        return "identical"
    interval = row.get("difference_interval")
    if not interval:
        return "not read"
    if interval[0] > 0.0:
        return "gain"
    if interval[1] < 0.0:
        return "cost"
    return "undecided"


# -- the scored tests, in parallel ---------------------------------------------------------------------------------------

_STATE: Dict = {}


def _task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    days = list(members)
    out: Dict[str, dict] = {}
    # d = reference less arm: positive favours the arm (as #1288's paired rows)
    for name, (reference, candidate) in {
        "arm_vs_control": (CONTROL, ARM), "arm_vs_B1star": (REFERENCE, ARM), "control_vs_B1star": (REFERENCE, CONTROL),
    }.items():
        if all(series[candidate][d] == series[reference][d] for d in days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        row = s761.run_pairs({reference: series[reference]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[reference]
        row["reading"] = reading(row)
        out[name] = row
    return (split, label, metric), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_task, jobs, chunksize=1)


def mean_move(series_arm: Mapping[date, float], series_control: Mapping[date, float], days: Sequence[date], reps: int) -> dict:
    """The mean of (arm less control) over `days` in date order and its 90% stationary-bootstrap percentile interval (the move in the hit rate of a band)."""

    ordered = sorted(days)
    d = [series_arm[x] - series_control[x] for x in ordered]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=sp.BLOCK_LENGTH, seed=SEED, replications=reps)
    return {"days": len(d), "arm": sum(series_arm[x] for x in ordered) / len(d), "control": sum(series_control[x] for x in ordered) / len(d),
            "move": sum(d) / len(d), "interval": [low, high]}


# -- one window ----------------------------------------------------------------------------------------------------------


def estimate_record(est: sc.StateEstimate) -> dict:
    return {"terms": list(est.terms), "flagged": dict(est.flagged), "effect": dict(est.effect), "pairs": est.pairs}


def refit_of(day: date, refit_days: Sequence[date]) -> date:
    """The refit a decision on `day` reads: the latest refit day on or before it."""

    return max(r for r in refit_days if r <= day)


def run_window(window: str, ctx: dict, args) -> dict:
    panel, extended = ctx["panel"], ctx["extended"]
    frame, notes, walks, (_term_table, _net_table), _cells, groups_fn = m1288.build(
        window, panel, ctx["splits"], ctx["registry"], ctx["table"], ctx["register"], ctx["results"], ctx["auctions"], None)
    last = WINDOW_LAST[window]
    control_walk = walks["ann"]
    control_raw = control_walk.forecasts[NET_ARM.name]
    first = min(control_raw)
    days = [d for d in m1288.candidate_days(frame, window, None) if d >= first]
    with back_filled_turn_days([row.date for row in extended]):
        walked = walk_extended(
            extended, days, ctx["terms"], ctx["states"], NET_ARM, registry=ctx["registry"], decision_time=k.DECISION_TIME, splits=ctx["splits"],
            sizes=ctx["sizes"], posting=ctx["posting"], admitted=ctx["admitted"], reads=ctx["reads"])
    refit_days = sorted(control_walk.fits)
    require_same_refits(refit_days, sorted(walked.estimates))
    for d in frame.days:
        if d not in walked.forecasts:
            raise ValueError(f"the extended walk has no forecast of the scored decision day {d}")
    # every scored decision: the scored day and its feature date are published days
    ext_dates = [row.date for row in extended]
    folds = []
    for d in frame.days:
        anchor = pb._anchor(extended, ext_dates.index(d), ctx["registry"], k.DECISION_TIME)
        folds.append(ScoredFold(train_start=ext_dates[0], train_end=ext_dates[anchor], train_rows=anchor + 1, feature_date=ext_dates[anchor], scored_date=d))
    backfill.require_training_only(folds, where="s3c_ann_net_backfill_1444")
    positions = {row.date: i for i, row in enumerate(panel)}
    settings = dict(registry=ctx["registry"], decision_time=k.DECISION_TIME, splits=ctx["splits"])
    star = {d: b1_calendar.b1_calendar_anchor_forecast(panel, positions[d], **settings) for d in frame.days}
    forecasts = {
        CONTROL: {d: frame.forecasts[CONTROL][d] for d in frame.days},
        ARM: m1255.s3c_forecasts(frame, ctx["register"], {d: walked.forecasts[d] for d in frame.days}),
        REFERENCE: star,
    }
    cells = {m: m1288.cell_table(frame, forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    labels = c.day_labels(frame, ctx["table"])
    pressure = k.pressure_labels(frame, sorted(labels))
    groups = list(groups_fn(frame, labels, pressure))
    targets = sorted(labels)
    h2 = [t for t in targets if H2_2018[0] <= t <= H2_2018[1]]
    if h2:
        groups.append(("regime", "2018 H2", "target", h2))
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            jobs.append((split, label, grain, metric, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result_groups: Dict[str, dict] = {}
    for split, label, grain, members in groups:
        entry = result_groups.setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}}
            if metric in TESTED:
                entry[metric]["vs"] = {}
    for (split, label, metric), payload in done:
        result_groups[split][label][metric]["vs"] = payload
    # the coverage of the central 90% band, as a move with an interval
    coverage = {}
    for split, label, grain, members in groups:
        if (split, label) in (("pooled", "all decision days"), ("regime", HEADLINE_REGIME), ("regime", "2018 H2")) and len(members) >= MIN_GROUP_DAYS:
            ser = series[(grain, "b90_closed")]
            coverage[f"{split}/{label}"] = mean_move(ser[ARM], ser[CONTROL], members, args.reps)
    # the named quarter-ends, cell by cell
    lo, hi = m1288.BAND90
    named = []
    for d in frame.days:
        for h in LEADS:
            t = frame.target(d, h)
            if t not in NAMED_TARGETS:
                continue
            r = refit_of(d, refit_days)
            row = {"target": t.isoformat(), "decision_day": d.isoformat(), "lead": h, "outcome_bp": frame.outcome[t], "refit_day": r.isoformat()}
            for m, est in ((CONTROL, control_walk.estimates[r][NET_ARM.name][h]), (ARM, walked.estimates[r][h])):
                q = forecasts[m][d][h]
                row[m] = {"q05": q[lo], "q50": q[sp.GRID.index(0.5)], "q95": q[hi], "grid_crps": cells[m]["grid_crps"][(d, h)],
                          "upper_tail_twcrps": cells[m]["upper_tail_twcrps"][(d, h)], "quarter_end_effect": est.effect.get("quarter_end"),
                          "quarter_end_flagged": est.flagged.get("quarter_end")}
            named.append(row)
    refits = {
        r.isoformat(): {str(h): {"control": estimate_record(control_walk.estimates[r][NET_ARM.name][h]), "arm": estimate_record(walked.estimates[r][h])}
                        for h in LEADS}
        for r in refit_days
    }
    first_entry = {
        str(h): {name: next((r.isoformat() for r in refit_days if "quarter_end" in (control_walk.estimates[r][NET_ARM.name][h] if name == "control"
                                                                                      else walked.estimates[r][h]).terms), None)
                 for name in ("control", "arm")} for h in LEADS
    }
    return {
        "notes": notes, "days": len(frame.days), "first_scored": frame.days[0].isoformat(), "last_scored": frame.days[-1].isoformat(),
        "first_forecast_day": first.isoformat(), "skipped_by_arm": [d.isoformat() for d in walked.skipped],
        "refits": {"control": len(control_walk.fits), "arm": len(walked.estimates), "days": [r.isoformat() for r in refit_days]},
        "refit_terms": refits, "first_quarter_end_refit": first_entry, "coverage_90": coverage, "named_quarter_ends": named,
        "groups": result_groups, "skipped_groups": skipped,
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
    }


# -- the commands --------------------------------------------------------------------------------------------------------


def build_extended(scratch_rows: Sequence[Mapping[str, str]], published_rows: Sequence[Mapping[str, str]], fields: Sequence[str]) -> List[Dict[str, str]]:
    """The extended panel as CSV rows: the scratch panel's back-filled rows (every cell but the admitted series and the calendar columns already blank), then every
    row of the published panel. The scratch panel's own published rows end at 2025-12-31 (#726); where it has them they must equal the published panel's in `fields`.

    Raises:
        ValueError: a published day of the scratch panel is missing from the published panel, or a field differs.
    """

    first = backfill.FIRST_PUBLISHED.isoformat()
    published = {row["date"]: row for row in published_rows}
    out: List[Dict[str, str]] = []
    for row in scratch_rows:
        if row["date"] < first:
            out.append({name: row.get(name, "") for name in published_rows[0]})
            continue
        there = published.get(row["date"])
        if there is None:
            raise ValueError(f"{row['date']} is in the scratch panel and not in the published panel")
        for name in fields:
            a, b = row.get(name, ""), there.get(name, "")
            if a != b and not (a and b and abs(float(a) - float(b)) <= 1e-9):
                raise ValueError(f"{row['date']} {name}: scratch {a!r} != published {b!r}")
    out.extend(dict(row) for row in published_rows)
    return out


def panel_command(args) -> int:
    """Blank every cell of a back-filled row but the admitted series and the calendar columns, as #726 does, then put the published panel after them."""

    require_unlocked([LAST_DAY], where="s3c_ann_net_backfill_1444")
    admitted = backfill.load_admitted_series(POSTING)
    blanked_path = Path(args.output).with_suffix(".blanked.csv")
    blanked = b726.established_panel(args.extended, blanked_path, admitted)
    with blanked_path.open(newline="", encoding="utf-8") as handle:
        scratch = list(csv.DictReader(handle))
    with Path(args.published).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        names = list(reader.fieldnames or [])
        published = list(reader)
    rows = build_extended(scratch, published, READ_FIELDS)
    with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    blanked_path.unlink()
    print(json.dumps({"back_filled_rows": blanked, "rows": len(rows), "output": str(args.output)}))
    return 0


def score_command(args) -> int:
    declaration = committed_declaration()
    require_instant(k.DECISION_TIME)
    require_unlocked([LAST_DAY], where="s3c_ann_net_backfill_1444")
    published_sha = panel_sha256(Path(args.panel))
    extended_sha = panel_sha256(Path(args.extended))
    panel = [row for row in load_daily_panel(Path(args.panel)) if row.date <= LAST_DAY]
    extended = [row for row in load_daily_panel(Path(args.extended)) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_ann_net_backfill_1444")
    prefix = require_same_published(panel, extended)
    admitted = backfill.load_admitted_series(POSTING)
    posting = backfill.load_posting_instant(POSTING)
    b726.require_backfilled_admitted(extended, admitted, where="s3c_ann_net_backfill_1444")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    results = m1288.load_results()
    auctions = m1273.load_auctions()
    ctx = {
        "panel": panel, "extended": extended, "splits": splits, "registry": registry, "register": policy_events.load_register(), "results": results,
        "auctions": auctions, "table": cal.TermTable(panel, announcements, decision_time=c.DECISION_TIME),
        "terms": ExtendedTermTable(panel, extended, announcements, results, decision_time=k.DECISION_TIME),
        "sizes": s3c_announced.AnnouncedNetSizeTable(extended, auctions, decision_time=k.DECISION_TIME),
        "states": s3c_net.constant_states(extended), "posting": posting, "admitted": admitted,
        "reads": backfill.series_read(["spread_bps", "quarter_end", "tax_date"]),
    }
    result: dict = {
        "issue": 1444, "declaration": str(DECLARATION.relative_to(REPO)), "label": "development, not a verdict", "instant": INSTANT_TEXT,
        "published_panel_sha256": published_sha, "extended_panel_sha256": extended_sha, "back_filled_rows": prefix,
        "first_back_filled": extended[0].date.isoformat(), "last_back_filled": extended[prefix - 1].date.isoformat(),
        "posting_instant": None if posting is None else posting.isoformat(), "admitted": {n: v.isoformat() for n, v in admitted.items()},
        "series_read_from_back_filled_rows": list(ctx["reads"]), "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "labels": LABELS, "reading_rules": declaration["reading_rules"], "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, ctx, args)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _iv(interval: Optional[Sequence[float]], digits: int = 3) -> str:
    return "not read" if not interval else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def cell(row: Optional[Mapping[str, object]]) -> str:
    if row is None:
        return "n/a"
    if row.get("identical"):
        return "identical"
    if "difference" not in row:
        return "not read"
    return f"{row['difference']:+.3f} {_iv(row.get('difference_interval'))} **{row.get('reading', reading(row))}**"


def group_table(groups: Mapping[str, dict], split: str, metric: str, key: str) -> List[str]:
    out = ["| group | days | " + f"{LABELS[CONTROL]} | {LABELS[ARM]} | {LABELS[REFERENCE]} | d, " + {"arm_vs_control": "control less arm", "arm_vs_B1star": "B1'* less arm",
           "control_vs_B1star": "B1'* less control"}[key] + " |", "|---|---|---|---|---|---|"]
    for label, entry in groups.get(split, {}).items():
        if metric not in entry:
            continue
        means = entry[metric]["means"]
        row = entry[metric].get("vs", {}).get(key)
        out.append(f"| {label} | {entry['days']} | {means[CONTROL]:.3f} | {means[ARM]:.3f} | {means[REFERENCE]:.3f} | {cell(row) if row else 'group too small'} |")
    return out


def render(r: dict) -> str:
    lines = [
        "# (s3c-ann-net) trained on the 2014-18 back-filled history: a scratch measurement (#1444)",
        "",
        "> **Development evidence, not a verdict** (scoring protocol v1: development data never gives one). H4 (longer history fixes part of 2018-19), step 3, "
        "measured on the H5 candidate (s3c-ann-net). A scratch measurement under her ruling of 26 October 2026 (ledger item 56, #1223; "
        "`docs/decisions/information-set.md`, back-fill amendment, item 3): nothing is adopted and the frozen candidate does not change. Made at "
        f"{r['instant']} New York time. Declaration: [`{r['declaration']}`](../../{r['declaration']}), committed before any score.",
        "",
        "## What was measured",
        "",
        f"The control is (s3c-ann-net) as #1288, #1319 and #1314 walk it, on the published panel (from 2018-04-03). The arm, (s3c-ann-net+bf), is the same model on the "
        f"same decision days and refit days with the {r['back_filled_rows']} back-filled rows ({r['first_back_filled']} to {r['last_back_filled']}) before the "
        f"published rows in every training frame. A back-filled row carries SOFR, IORB, TGCR, BGCR and the calendar columns only; every fit reads the series "
        f"{', '.join(r['series_read_from_back_filled_rows'])}, admitted from {r['posting_instant']}. The two settlement terms and the two market-holiday terms "
        "(`month_end`, `post_month_end_window`; the pinned holiday table starts on 2018-01-01) are **not fitted on back-filled rows**: they are fitted on published "
        "targets only, and the three terms a back-filled row carries (`quarter_end`, `tax_date`, `dom_19_23`) are then fitted on every pair, net of those effects. "
        "A back-filled settlement or month-end day is therefore not flagged and its residual stays in the pool and in the three fits: that is a cost the "
        "measurement includes, not one it removes.",
        "",
        "d is the reference's score less the arm's, so a positive d favours the arm. The interval is the studentized stationary-bootstrap interval of the protocol "
        "(`scoring_protocol.paired_tests`, 90%); *gain* is an interval wholly above zero, *cost* wholly below, *undecided* otherwise. Day-type groups are scored on their "
        "own days as #1288 scores them, so a group that is not contiguous joins days that were months apart into one block.",
        "",
    ]
    for window in WINDOWS:
        w = r["windows"][window]
        lines += [
            f"## {m1288.WINDOW_TITLES[window]}",
            "",
            f"{w['days']} decision days, first scored {w['first_scored']}, last {w['last_scored']}; {w['refits']['control']} refits of the control and "
            f"{w['refits']['arm']} of the arm (the same days). The arm had no forecast on {len(w['skipped_by_arm'])} days before the control's first.",
            "",
        ]
        for metric in TESTED:
            lines += [f"### {METRIC_TITLES[metric]}, {window}", "", "Pooled and by lead", ""]
            lines += group_table(w["groups"], "pooled", metric, "arm_vs_control")
            lines += [""] + group_table(w["groups"], "lead", metric, "arm_vs_control")
            lines += ["", "By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)", ""]
            lines += group_table(w["groups"], "regime", metric, "arm_vs_control")
            lines += ["", "By pressure-day type", ""] + group_table(w["groups"], "pressure_day_type", metric, "arm_vs_control")
            lines += ["", "By target-day type", ""] + group_table(w["groups"], "target_day_type", metric, "arm_vs_control")
            lines += ["", "Each arm against B1'* (the arm, then the control), pooled and by regime", ""]
            lines += group_table(w["groups"], "pooled", metric, "arm_vs_B1star")
            lines += group_table(w["groups"], "regime", metric, "arm_vs_B1star")[2:]
            lines += [""] + group_table(w["groups"], "pooled", metric, "control_vs_B1star")
            lines += group_table(w["groups"], "regime", metric, "control_vs_B1star")[2:]
            lines += [""]
        lines += ["### Coverage of the central 90% band", "", "| group | days | control | arm | move (arm less control) |", "|---|---|---|---|---|"]
        for name, row in w["coverage_90"].items():
            lines.append(f"| {name} | {row['days']} | {row['control']:.3f} | {row['arm']:.3f} | {row['move']:+.3f} {_iv(row['interval'])} |")
        lines += ["", "(The interval of a move in coverage is the unstudentized 90% stationary-bootstrap percentile interval; no reading is taken from it.)", ""]
        if w["named_quarter_ends"]:
            lines += ["### The named quarter-ends", "", "| target | decision day | lead | outcome (bp) | control q05 / q50 / q95 | arm q05 / q50 / q95 | control CRPS | arm CRPS | control quarter-end effect (flagged) | arm quarter-end effect (flagged) |",
                      "|---|---|---|---|---|---|---|---|---|---|"]
            for row in w["named_quarter_ends"]:
                a, b = row[CONTROL], row[ARM]

                def eff(x):
                    return "not in fit" if x["quarter_end_effect"] is None else f"{x['quarter_end_effect']:+.2f} ({x['quarter_end_flagged']})"
                lines.append(f"| {row['target']} | {row['decision_day']} | {row['lead']} | {row['outcome_bp']:.1f} | {a['q05']:.1f} / {a['q50']:.1f} / {a['q95']:.1f} | "
                             f"{b['q05']:.1f} / {b['q50']:.1f} / {b['q95']:.1f} | {a['grid_crps']:.3f} | {b['grid_crps']:.3f} | {eff(a)} | {eff(b)} |")
            lines.append("")
        lines += ["### The first refit at which `quarter_end` entered the fit", "", "| lead | control | arm |", "|---|---|---|"]
        for h, row in w["first_quarter_end_refit"].items():
            lines.append(f"| {h} | {row['control'] or 'never'} | {row['arm'] or 'never'} |")
        lines.append("")
    lines += [
        "## What this does and does not show",
        "",
        "It is a scratch measurement on development data. It does not adopt the back-fill, change the frozen candidate, or settle whether IORB on back-filled rows "
        "stays admitted beyond training history. The 2014-18 floor period was calm with a negative spread, so its residuals can make the 2018-19 bands too narrow; "
        "the coverage table is the check. The result goes to the validation report's known limits. Skipped groups, with their sizes, are in `result.json`.",
        "",
        "Every figure on this page is in [`result.json`](s3c-ann-net-backfill-1444/result.json).",
        "",
    ]
    return "\n".join(lines)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--extended", type=Path, required=True, help="the scratch panel of scripts/backfill_history.py panel")
    p.add_argument("--published", type=Path, required=True, help="the published panel (PUB.csv)")
    p.add_argument("--output", type=Path, required=True)
    s = sub.add_parser("score")
    s.add_argument("--panel", type=Path, required=True)
    s.add_argument("--extended", type=Path, required=True)
    s.add_argument("--output", type=Path, required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000)
    s.add_argument("--workers", type=int, default=4)
    g = sub.add_parser("page")
    g.add_argument("--score", type=Path, required=True)
    g.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {"panel": panel_command, "score": score_command, "page": page_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
