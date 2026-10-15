#!/usr/bin/env python3
"""Inter-source correlations, and every source against the spread on ordinary days (#629).

An exploratory screen, not a record: nothing is selected, no model changes, no published figure moves, and no day in a
locked tier is read (`docs/decisions/lockbox.md`). It writes JSON, CSV, SVG and Markdown to the paths it is given and nothing
into `docs/runs/`. It follows `scripts/source_screen.py` (#478, with the OFR real-time guard of #522) and asks two things that
screen did not: how the sources relate to each other, and which of them say anything on ordinary days, the days that are not
known risk dates, where the risk-date part of a forecast is 0 (PR #608, PR #612). Every choice is in
`metadata/source_matrix_629.json`, which this script refuses to read unless it is committed and unchanged. The series list in it is
formed from the panel's columns and the as-of rule's refusals, before any statistic is computed.

    # PUBLISHED.csv is the published panel; the scratch panels are those of docs/pivot/source-screen-result.md (Reproduce),
    # and AUG2D.csv is satiation_distance_598.py's
    PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv AUG2D.csv --output SCREEN.csv
    PYTHONPATH=src python3 scripts/source_matrix_629.py declare --panel SCREEN.csv
    git add metadata/source_matrix_629.json && git commit        # a declaration is made before any score
    PYTHONPATH=src python3 scripts/source_matrix_629.py run --panel SCREEN.csv --output OUT/source_matrix.json --matrices OUT
    PYTHONPATH=src python3 scripts/source_matrix_629.py report OUT/source_matrix.json --output OUT

* **Days.** The scored days of the lead-1 fold grid, 2018-06-29 to 2025-12-31 (`source_screen`), the same days at every lead. An
  ordinary day is one the risk-date part does not serve: its day type is `ordinary` and no coupon settlement is known for it
  (`treasury_settlement_coupons`, dated from the auction announcement, read at lead 1).
* **Reading.** Each series is read as of the decision instant through `repo_model.asof.InformationRule`, at leads of 1, 2, 3, 5 and
  10 panel days. A series announced for the scored day itself and not public at a longer lead is a hole at that lead.
  Columns the settlement dating (#541) or the per-release H.4.1 dating changes are read twice, as published and `@per_release`.
  The inputs of the every-day part (#601) are formed from the same masked frames.
* **Matrix.** Spearman, by pairs of days on which both series are present, at lead 1: all scored days and ordinary days, pooled,
  and ordinary days by period regime and by as-of scarcity state. Groups are complete-linkage clusters with every pair at
  |rho| >= the declared threshold; a group's representative is the member with the largest mean |rho| to the others.
* **Against the target on ordinary days.** Spearman with the +5 bp indicator, the spread level and the spread change; the AUROC for
  pressure days against other ordinary days; the pre-onset contrast. 90% intervals by the stationary bootstrap over the days in date order.
* **Incremental.** The partial rank correlation of the top series after the as-of scarcity state and the tail spread are taken out.

Every number is exploratory and none is corrected for multiplicity. Reads the scratch panels, which are gitignored, so this is not
a test. Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import multiprocessing
import random
import statistics
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import backfill, contract, h41_release, pressure, risk_dates, scarcity, settlement_dating  # noqa: E402
from repo_model import satiation as sat  # noqa: E402
from repo_model.asof import InformationRule, InformationSet, fold_grid  # noqa: E402
from repo_model.baseline import _as_of_folds  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import _quantile, stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


ss = _load("source_screen")
eds = _load("every_day_separation_601")
sd = eds.sd
ann = eds.ann

DECLARATION = REPO / "metadata" / "source_matrix_629.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
FIRST_DAY = ss.FIRST_DAY
LAST_DAY = ss.LAST_DAY
LEADS = (1, 2, 3, 5, 10)
TARGETS = ("pressure", "level", "change")
THRESHOLD_BP = 5.0
CLUSTER_THRESHOLD = 0.8
DECISION_TIME = ss.DECISION_TIME
SCARCITY = ss.SCARCITY
TAIL = eds.TAIL
BOOTSTRAP = {"level": 0.9, "replications": 1000, "block_length": 10, "seed": 629}
#: A matrix cell, a correlation or a split needs this much to be reported.
MINIMUM_DAYS = ss.MINIMUM_DAYS
MINIMUM_PRESSURE = ss.MINIMUM_PRESSURE
MINIMUM_ONSETS = 3
MINIMUM_PRE_DAYS = 10
PRE_ONSET_DAYS = (1, 5)
TOP_SERIES = 15
PER_RELEASE = "@per_release"
FOURTEEN = tuple(eds.INPUTS)
#: Series whose reading the controls of the incremental check already carry.
CONTROLS = (SCARCITY, TAIL)
BANDS = ("ample", "scarce", "unknown")

# -- guards -------------------------------------------------------------------


def require_panel_window(rows) -> None:
    """Refuse a panel that runs past the last day a comparison may score.

    Raises:
        LookAheadError: when the last row is after 2025-12-31 (the 2026 tiers are locked, `docs/decisions/lockbox.md`).
    """

    if rows[-1].date > LAST_DAY:
        raise LookAheadError(f"the panel runs to {rows[-1].date}, past {LAST_DAY}; a screen reads no day in a locked tier")


def require_no_backfill(rows) -> None:
    """Refuse a panel that carries the back-filled 2014-18 history: its posting instant is not established (#572).

    Raises:
        LookAheadError: when the first row is before `backfill.FIRST_PUBLISHED`.
    """

    if rows[0].date < backfill.FIRST_PUBLISHED:
        raise LookAheadError(
            f"the panel starts {rows[0].date}, before {backfill.FIRST_PUBLISHED}: the back-filled history has no posting instant (#572)"
        )


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def is_ordinary(day_type: str, coupons: Optional[float]) -> bool:
    """A day the risk-date part does not serve: an `ordinary` day type and no coupon settlement known for it."""

    return not risk_dates.non_ordinary_day(day_type, coupons)


# -- statistics -----------------------------------------------------------------


def spearman_pairwise(x: Sequence[Optional[float]], y: Sequence[Optional[float]]) -> Tuple[Optional[float], int]:
    """Spearman's rho on the days both are present, and how many there are."""

    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 2:
        return None, len(pairs)
    return ss.spearman([a for a, _b in pairs], [b for _a, b in pairs]), len(pairs)


def auc(values: Sequence[Optional[float]], labels: Sequence[int]) -> Optional[float]:
    """P(a labelled day's value is above an unlabelled day's), a tie counting half; holes dropped; `None` without both classes."""

    kept = [(v, l) for v, l in zip(values, labels) if v is not None]
    events = sum(1 for _v, l in kept if l)
    others = len(kept) - events
    if events == 0 or others == 0:
        return None
    ranks = ss.average_ranks([v for v, _l in kept])
    rank_sum = sum(r for r, (_v, l) in zip(ranks, kept) if l)
    return (rank_sum - events * (events + 1) / 2.0) / (events * others)


def _dense(values: Sequence[Optional[float]]) -> Tuple[List[Optional[int]], int]:
    """Each value's position among the distinct values (ties share one); holes stay `None`."""

    distinct = sorted({v for v in values if v is not None})
    index = {v: i for i, v in enumerate(distinct)}
    return [None if v is None else index[v] for v in values], len(distinct)


def _auc_dense(dense: Sequence[Optional[int]], labels: Sequence[int], size: int, resample: Sequence[int]) -> Optional[float]:
    """The AUROC of the resampled days, from dense value positions: counts per value, a running total, no sort."""

    negatives = [0] * (size + 1)
    positives: List[int] = []
    for i in resample:
        d = dense[i]
        if d is None:
            continue
        if labels[i]:
            positives.append(d)
        else:
            negatives[d] += 1
    others = sum(negatives)
    if not positives or others == 0:
        return None
    below = [0] + list(itertools.accumulate(negatives))
    total = 0.0
    for d in positives:
        total += below[d] + 0.5 * negatives[d]
    return total / (len(positives) * others)


def resampled_auc(values: Sequence[Optional[float]], labels: Sequence[int], resample: Sequence[int]) -> Optional[float]:
    """The AUROC of the days `resample` picks (indices, repeats allowed)."""

    dense, size = _dense(values)
    return _auc_dense(dense, labels, size, resample)


def _interval(draws: List[float], level: float) -> Optional[Tuple[float, float]]:
    if not draws:
        return None
    draws = sorted(draws)
    tail = (1.0 - level) / 2.0
    return _quantile(draws, tail), _quantile(draws, 1.0 - tail)


def bootstrap_interval(
    values: Sequence[Optional[float]], labels: Sequence[int], resamples: Sequence[Sequence[int]], *, level: float
) -> Optional[Tuple[float, float]]:
    """The percentile interval of the AUROC over `resamples` (draws with only one class are skipped)."""

    dense, size = _dense(values)
    draws = [d for d in (_auc_dense(dense, labels, size, r) for r in resamples) if d is not None]
    return _interval(draws, level)


def _std_diff(values: Sequence[Optional[float]], labels: Sequence[int], resample: Sequence[int]) -> Optional[float]:
    """Mean of the labelled days less the mean of the others, in units of the others' standard deviation."""

    pre: List[float] = []
    other: List[float] = []
    for i in resample:
        v = values[i]
        if v is None:
            continue
        (pre if labels[i] else other).append(v)
    if not pre or len(other) < 2:
        return None
    mean_other = sum(other) / len(other)
    sd_other = math.sqrt(sum((v - mean_other) ** 2 for v in other) / (len(other) - 1))
    if sd_other <= 0.0:
        return None
    return (sum(pre) / len(pre) - mean_other) / sd_other


def complete_linkage(names: Sequence[str], rho: Callable[[str, str], Optional[float]], threshold: float) -> List[List[str]]:
    """Groups in which every pair has |rho| >= threshold (complete linkage); a missing correlation never joins.

    Merges the two groups with the largest smallest-|rho| between them while that is at least `threshold`.
    Groups and members are in the order of `names`.
    """

    order = {name: i for i, name in enumerate(names)}
    groups = [[name] for name in names]

    def link(a: Sequence[str], b: Sequence[str]) -> float:
        smallest = math.inf
        for x in a:
            for y in b:
                r = rho(x, y)
                if r is None:
                    return -1.0
                smallest = min(smallest, abs(r))
        return smallest

    while len(groups) > 1:
        best, pair = -1.0, None
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                value = link(groups[i], groups[j])
                if value > best:
                    best, pair = value, (i, j)
        if pair is None or best < threshold:
            break
        i, j = pair
        merged = sorted(groups[i] + groups[j], key=order.__getitem__)
        groups = [g for k, g in enumerate(groups) if k not in pair] + [merged]
        groups.sort(key=lambda g: order[g[0]])
    return groups


def medoid(cluster: Sequence[str], rho: Callable[[str, str], Optional[float]]) -> str:
    """The member with the largest mean |rho| to the others (ties: the first in the list)."""

    if len(cluster) == 1:
        return cluster[0]
    best, chosen = -1.0, cluster[0]
    for x in cluster:
        scores = [abs(rho(x, y)) for y in cluster if y != x and rho(x, y) is not None]
        mean = sum(scores) / len(scores) if scores else 0.0
        if mean > best + 1e-12:
            best, chosen = mean, x
    return chosen


def _solve(matrix: List[List[float]], rhs: List[float]) -> Optional[List[float]]:
    """Gaussian elimination with partial pivoting; `None` when the system is singular."""

    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-9:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(col + 1, n):
            factor = a[r][col] / a[col][col]
            for k in range(col, n + 1):
                a[r][k] -= factor * a[col][k]
    solution = [0.0] * n
    for r in range(n - 1, -1, -1):
        solution[r] = (a[r][n] - sum(a[r][k] * solution[k] for k in range(r + 1, n))) / a[r][r]
    return solution


def _residual(target: Sequence[float], controls: Sequence[Sequence[float]]) -> Optional[List[float]]:
    columns = [[1.0] * len(target)] + [list(c) for c in controls]
    k = len(columns)
    gram = [[sum(a * b for a, b in zip(columns[i], columns[j])) for j in range(k)] for i in range(k)]
    rhs = [sum(a * b for a, b in zip(columns[i], target)) for i in range(k)]
    beta = _solve(gram, rhs)
    if beta is None:
        return None
    return [t - sum(beta[i] * columns[i][row] for i in range(k)) for row, t in enumerate(target)]


def partial_spearman(
    x: Sequence[Optional[float]], y: Sequence[Optional[float]], controls: Sequence[Sequence[Optional[float]]]
) -> Optional[float]:
    """The rank correlation of `x` and `y` after the ranks of `controls` are regressed out of both.

    Days on which any of the series is a hole are dropped. `None` when a residual is constant (a series that is its control) or the
    controls are collinear.
    """

    keep = [i for i in range(len(x)) if x[i] is not None and y[i] is not None and all(c[i] is not None for c in controls)]
    if len(keep) < 3:
        return None
    rx = ss.average_ranks([x[i] for i in keep])
    ry = ss.average_ranks([y[i] for i in keep])
    rc = [ss.average_ranks([c[i] for i in keep]) for c in controls]
    ex, ey = _residual(rx, rc), _residual(ry, rc)
    if ex is None or ey is None:
        return None
    if max(map(abs, ex)) < 1e-9 or max(map(abs, ey)) < 1e-9:
        return None
    return ss.pearson(ex, ey)


# -- the series ---------------------------------------------------------------


class Switched:
    """`ss.declared_features()` and the two satiation-distance columns in `contract` for a run, and the published map back after it."""

    def __enter__(self):
        self._saved = (contract.FEATURE_FIELDS, contract.FEATURE_SOURCES)
        fields = dict(ss.declared_features())
        fields.update(sat.DISTANCE_COLUMN_FIELDS)
        contract.FEATURE_FIELDS = MappingProxyType(fields)
        contract.FEATURE_SOURCES = MappingProxyType(
            {column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()}
        )
        return self

    def __exit__(self, *exc):
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = self._saved
        return False


def per_release_columns(columns: Sequence[str]) -> List[str]:
    """The columns that the settlement dating (#541) or the per-release H.4.1 dating changes how they are read.

    A column is listed when it is one of `settlement_dating.COLUMNS`, or draws on a field of the source the H.4.1 declaration names.
    """

    h41 = ann.json.loads(ann.H41.read_text(encoding="utf-8"))
    h41_source, h41_fields = h41["source"], set(h41["fields"])
    fields = dict(ss.declared_features())
    fields.update(sat.DISTANCE_COLUMN_FIELDS)
    out = []
    for column in columns:
        draws = fields.get(column, ())
        if column in settlement_dating.COLUMNS or any(src == h41_source and f in h41_fields for src, f in draws):
            out.append(column)
    return out


def scored_grid(rows, registry) -> List[int]:
    dates = [row.date for row in rows]
    scored = [
        index
        for index in fold_grid(dates, registry, decision_time=DECISION_TIME, minimum_history=ss.MINIMUM_HISTORY, horizon=1)
        if FIRST_DAY <= dates[index] <= LAST_DAY
    ]
    require_unlocked((dates[index] for index in scored), where="source_matrix_629")
    return scored


def read_lead(rows, registry, columns, lead: int, scored: Sequence[int], *, per_release: bool):
    """For the scored days, each column's as-of value at one lead; a scheduled input not yet public at this lead is a hole."""

    if per_release:
        rows, registry = ann.arm_inputs("both", rows, registry, lead)
    dates = [row.date for row in rows]
    context = h41_release.release_dating() if per_release else contextlib.nullcontext()
    values: Dict[str, List[Optional[float]]] = {column: [] for column in columns}
    spread_lag: List[Optional[float]] = []
    holes: Dict[str, int] = {}
    with context:
        rule = InformationRule(registry, tuple(columns), decision_time=DECISION_TIME, horizon=lead)
        wanted = {group.feature: position for position, group in enumerate(rule.groups) if position}
        kinds = {group.feature: group.kind for group in rule.groups if group.feature in wanted}
        for index in scored:
            info = rule.information_set(dates, index)
            for column in columns:
                read = info.reads[wanted[column]]
                try:
                    rule.check(dates, InformationSet(info.scored_index, info.decision_instant, info.anchor, (read,)))
                except LookAheadError:
                    values[column].append(None)
                    holes[column] = holes.get(column, 0) + 1
                    continue
                values[column].append(rows[read.row].values.get(column))
            spread_lag.append(rows[info.anchor].spread_bps)
    return values, spread_lag, holes, kinds


def read_derived(rows, registry, lead: int, scored_dates: Sequence[date]) -> Dict[str, List[Optional[float]]]:
    """The inputs of the every-day part (#601), formed from the masked frame of each decision, per-release reading, for the scored days."""

    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, lead)
    dates = [row.date for row in timed_rows]
    splits = load_split_declaration(SPLITS)
    in_window = [row for row in timed_rows if row.date <= LAST_DAY]
    day_types = [splits.day_type(row.values) for row in in_window]
    wanted = set(scored_dates)
    found: Dict[date, Dict[str, Optional[float]]] = {}
    with sd.switched_on(), h41_release.release_dating():
        rule = InformationRule(timed_registry, eds.READ, decision_time=time(16, 0), horizon=lead)
        for fold in _as_of_folds(
            timed_rows, rule, minimum_history=ss.MINIMUM_HISTORY, refit_every=len(timed_rows), entry="source_matrix_629", end=LAST_DAY
        ):
            day = dates[fold.index]
            if day not in wanted:
                continue
            frame = rule.frame(timed_rows, fold.info)
            anchor = len(frame) - 1
            series = {c: [row.values.get(c) for row in frame] for c in (TAIL, eds.P99, eds.P1, eds.P75, eds.RESERVES, eds.TGA, eds.DISTANCE)}
            found[day] = eds.read_inputs(
                series, anchor=anchor,
                rows_to_risk=eds.rows_to_next_risk_date(day_types, fold.index - lead, columns=eds.CALENDAR_COLUMNS),
            )
    return {name: [found.get(day, {}).get(name) for day in scored_dates] for name in FOURTEEN}


def series_names(readable: Sequence[str], affected: Sequence[str]) -> List[str]:
    return list(readable) + [ss.SPREAD_LAG] + [c + PER_RELEASE for c in affected] + list(FOURTEEN)


# -- the declaration ---------------------------------------------------------------------


def declaration_document(names: Sequence[str], readable, unreadable, affected, panel_sha: str, columns: int) -> dict:
    return {
        "status": (
            "declared by the pull request that closes #629 before any statistic; an exploratory screen, not a record. Nothing is selected "
            "into a model and nothing is published: no rule, threshold, onset definition or availability time changes, no day after "
            "2025-12-31 is read, the back-filled 2014-18 history is not read while its posting instant is null (#572), and no hindsight "
            "regime label is used (ruling on #515). None of the tests below is corrected for multiplicity"
        ),
        "issue": 629,
        "panel": {
            "sha256": panel_sha,
            "columns": columns,
            "built_by": "docs/pivot/source-matrix-ordinary-days-result.md (Reproduce): source_screen.py panel over the published panel's scratch panels and satiation_distance_598.py's",
        },
        "days": "the scored days of the lead-1 fold grid, 2018-06-29 to 2025-12-31 (source_screen), the same days at every lead",
        "ordinary_days": (
            "a scored day whose day type (metadata/evaluation_splits.json) is ordinary and whose treasury_settlement_coupons, dated from the auction "
            "announcement (#541) and read at lead 1, is not positive: the risk-date rule of the every-day part (announcement_dating_rescore.risk_flag)"
        ),
        "leads": list(LEADS),
        "targets": list(TARGETS),
        "target_definitions": {
            "pressure": "the spread strictly above +5 bp on whole basis points (repo_model.data.exceeds_bp)",
            "level": "the spread of the scored day",
            "change": "the spread of the scored day less that of the day before",
        },
        "series": {
            "count": len(names),
            "names": list(names),
            "rule": (
                "every column of the joined scratch panel (except date, sofr and iorb) that the as-of rule reads, as published; the spread's own as-of lag; "
                "the columns the settlement dating (#541) or the per-release H.4.1 dating changes, read a second time as NAME@per_release; "
                "and the 14 inputs of the every-day part (#601), formed from the per-release masked frames"
            ),
            "unreadable": dict(sorted(unreadable.items())),
            "per_release": list(affected),
            "derived": list(FOURTEEN),
        },
        "matrix": {
            "lead": 1,
            "subsets": [
                "all scored days, pooled",
                "ordinary days, pooled",
                "ordinary days by period regime (metadata/evaluation_splits.json, 2018-19 | 2020 | 2021-23 | 2024 | 2025-26)",
                "ordinary days by as-of scarcity state (ample | scarce | unknown)",
            ],
            "statistic": "Spearman on the days both series are present; a pair with fewer than %d days is left empty" % MINIMUM_DAYS,
        },
        "cluster": {
            "threshold": CLUSTER_THRESHOLD,
            "linkage": "complete: every pair in a group has |rho| >= the threshold; a missing correlation never joins",
            "matrix": "ordinary days, pooled, lead 1 (the all-days matrix is clustered too, as a check)",
            "representative": "the member with the largest mean |rho| to the other members (the medoid), chosen without the target",
        },
        "target_screen": {
            "days": "ordinary days",
            "spearman": "each series with each target at each lead, pooled, by period regime and by as-of scarcity state (at the same lead); empty under %d days or %d pressure days" % (MINIMUM_DAYS, MINIMUM_PRESSURE),
            "auroc": "pressure days against the other ordinary days, per lead and split, with a 90% bootstrap interval",
            "pre_onset": "onsets (repo_model.pressure.onsets) that fall on ordinary days; the pre-onset days are the 1 to 5 panel days before each, scored and ordinary; the contrast is their series, read at lead 1, against the other ordinary days: standardised difference and AUROC, each with a 90%% bootstrap interval; empty under %d onsets or %d pre-onset days in a split" % (MINIMUM_ONSETS, MINIMUM_PRE_DAYS),
        },
        "bootstrap": {
            **BOOTSTRAP,
            "resampling": "the stationary bootstrap over the days of the split in date order (repo_model.metrics.stationary_bootstrap_indices), one draw per replication shared by every series; the interval is the 5th and 95th percentile",
        },
        "incremental": {
            "series": "the %d series with the largest absolute pooled ordinary-day Spearman with the pressure indicator over leads 1 to 10, the two controls and the spread's own lag left out" % TOP_SERIES,
            "controls": "the as-of scarcity state and the tail spread (sofr_p99_iorb_bps), each read at the lead of the cell",
            "statistic": "the rank correlation of the series and the target after the ranks of the controls are regressed out of both, on ordinary days",
        },
        "regimes": "period slices of metadata/evaluation_splits.json (fixed in advance) and the as-of reserve-scarcity state; no regime is drawn from the outcome",
        "due_diligence": "one table per source from metadata/sources.json and metadata/sources_measurement.json: publisher, start of history and gaps measured on the panel, frequency, the publication instant the as-of rule uses, vintages, caveats citing findings",
        "tests_counted": "the report states the number of correlations, AUROCs and contrasts computed and that none is corrected for multiplicity",
        "published": "nothing; no variant, input or setting joins any published declaration",
    }


def panel_series(rows):
    """The readable columns of the panel, with the as-of rule's refusals; no statistic is formed."""

    registry = ss.measurement_fields.load_registry()
    with Switched():
        columns = ss.screened_columns(rows)
        readable, unreadable = ss.probe(registry, columns, rows)
        affected = per_release_columns(readable)
    return registry, readable, unreadable, affected


def declare_command(args) -> int:
    rows = load_daily_panel(args.panel)
    require_panel_window(rows)
    require_no_backfill(rows)
    ss.dvp_segment.require_ofr_public(rows)
    _registry, readable, unreadable, affected = panel_series(rows)
    names = series_names(readable, affected)
    document = declaration_document(names, readable, unreadable, affected, hashlib.sha256(args.panel.read_bytes()).hexdigest(), len(rows[0].values))
    DECLARATION.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION), "series": len(names), "readable": len(readable), "per_release": len(affected), "unreadable": len(unreadable)}))
    return 0


# -- the run ------------------------------------------------------------------------------


def _popcount(mask: int) -> int:
    return bin(mask).count("1")


def _mask(values: Sequence[Optional[float]], subset: Sequence[int]) -> int:
    mask = 0
    for position, i in enumerate(subset):
        if values[i] is not None:
            mask |= 1 << position
    return mask


def correlation_matrix(series: Mapping[str, Sequence[Optional[float]]], names: Sequence[str], subset: Sequence[int]) -> Dict[str, Dict[str, Optional[float]]]:
    """Spearman for every pair of `names` on the days of `subset` where both are present (ranks cached per pair of presence masks)."""

    masks = {name: _mask(series[name], subset) for name in names}
    cache: Dict[Tuple[str, int], List[float]] = {}

    def ranks(name: str, common: int) -> List[float]:
        key = (name, common)
        if key not in cache:
            cache[key] = ss.average_ranks([series[name][i] for position, i in enumerate(subset) if common >> position & 1])
        return cache[key]

    out: Dict[str, Dict[str, Optional[float]]] = {name: {} for name in names}
    for a, name in enumerate(names):
        out[name][name] = 1.0 if _popcount(masks[name]) >= 2 else None
        for other in names[a + 1:]:
            common = masks[name] & masks[other]
            value = None
            if _popcount(common) >= MINIMUM_DAYS:
                value = ss.pearson(ranks(name, common), ranks(other, common))
            out[name][other] = out[other][name] = value
    return out


def day_count(series: Mapping[str, Sequence[Optional[float]]], name: str, subset: Sequence[int]) -> int:
    return sum(1 for i in subset if series[name][i] is not None)


def _chunks(items: Sequence, n: int) -> List[List]:
    return [list(items[i::n]) for i in range(n)]


_WORK: Dict[str, object] = {}


def _bootstrap_job(job):
    """One series, one lead: the AUROC and its interval in every split, and (lead 1) the pre-onset contrast."""

    name, lead = job
    values = _WORK["series"][lead][name]
    out = {"auc": {}, "pre": {}}
    for split, positions in _WORK["splits"][lead].items():
        x = [values[i] for i in positions]
        labels = [_WORK["pressure"][i] for i in positions]
        resamples = _WORK["resamples"][(lead, split)]
        point = auc(x, labels)
        events = sum(1 for v, l in zip(x, labels) if l and v is not None)
        present = sum(1 for v in x if v is not None)
        cell = {"n": present, "pressure_days": events, "auc": None, "interval": None}
        if point is not None and present >= MINIMUM_DAYS and events >= MINIMUM_PRESSURE:
            cell["auc"] = point
            cell["interval"] = bootstrap_interval(x, labels, resamples, level=BOOTSTRAP["level"])
        out["auc"][split] = cell
        if lead != 1:
            continue
        pre_labels = [_WORK["pre"][i] for i in positions]
        in_pre = [i for i, l in zip(positions, pre_labels) if l]
        pre_present = sum(1 for v, l in zip(x, pre_labels) if l and v is not None)
        onsets = len({_WORK["onset_of"][i] for i in in_pre if _WORK["onset_of"].get(i) is not None})
        entry = {"n_pre": pre_present, "n_other": sum(1 for v, l in zip(x, pre_labels) if not l and v is not None), "onsets": onsets,
                 "auc": None, "auc_interval": None, "std_diff": None, "std_diff_interval": None}
        if onsets >= MINIMUM_ONSETS and pre_present >= MINIMUM_PRE_DAYS:
            entry["auc"] = auc(x, pre_labels)
            entry["auc_interval"] = bootstrap_interval(x, pre_labels, resamples_for(lead, split, "pre"), level=BOOTSTRAP["level"])
            entry["std_diff"] = _std_diff(x, pre_labels, range(len(x)))
            draws = [d for d in (_std_diff(x, pre_labels, r) for r in resamples_for(lead, split, "pre")) if d is not None]
            entry["std_diff_interval"] = _interval(draws, BOOTSTRAP["level"])
        out["pre"][split] = entry
    return name, lead, out


def resamples_for(lead: int, split: str, kind: str):
    return _WORK["resamples"][(lead, split)]


def make_resamples(splits: Mapping[int, Mapping[str, Sequence[int]]]) -> Dict[Tuple[int, str], List[Tuple[int, ...]]]:
    """One set of stationary-bootstrap draws per split, shared by every series (seeded from the declared seed and the split)."""

    out: Dict[Tuple[int, str], List[Tuple[int, ...]]] = {}
    for lead, by_split in splits.items():
        for split, positions in by_split.items():
            key = (lead, split)
            seed = int(hashlib.sha256(f"{BOOTSTRAP['seed']}:{lead}:{split}".encode()).hexdigest()[:12], 16)
            rng = random.Random(seed)
            n = len(positions)
            out[key] = [stationary_bootstrap_indices(n, BOOTSTRAP["block_length"], rng) for _ in range(BOOTSTRAP["replications"])] if n else []
    return out


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    rows = load_daily_panel(args.panel)
    require_panel_window(rows)
    require_no_backfill(rows)
    ss.dvp_segment.require_ofr_public(rows)
    panel_sha = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if panel_sha != declared["panel"]["sha256"]:
        raise SystemExit(f"the panel's sha256 {panel_sha[:8]}… is not the declared {declared['panel']['sha256'][:8]}…; rebuild it as the declaration says")
    registry, readable, unreadable, affected = panel_series(rows)
    names = series_names(readable, affected)
    if names != declared["series"]["names"]:
        raise SystemExit("the series the panel gives are not the declared series list")
    scored = scored_grid(rows, registry)
    dates = [rows[i].date for i in scored]
    position = {row.date: i for i, row in enumerate(rows)}
    spreads = [row.spread_bps for row in rows]
    pressure_flag = [1 if exceeds_bp(spreads[position[d]], THRESHOLD_BP) else 0 for d in dates]
    targets = {
        "pressure": [float(v) for v in pressure_flag],
        "level": [spreads[position[d]] for d in dates],
        "change": [spreads[position[d]] - spreads[position[d] - 1] for d in dates],
    }
    # -- ordinary days
    splits_decl = load_split_declaration(SPLITS)
    coupon_rows, _r = ann.arm_inputs("both", rows, registry, 1)
    ordinary = [
        is_ordinary(splits_decl.day_type(rows[position[d]].values), coupon_rows[position[d]].values.get(eds.rds.COUPONS)) for d in dates
    ]
    ordinary_idx = [i for i, ok in enumerate(ordinary) if ok]
    print(json.dumps({"scored_days": len(dates), "ordinary_days": len(ordinary_idx), "pressure_days": sum(pressure_flag),
                      "pressure_days_ordinary": sum(pressure_flag[i] for i in ordinary_idx)}), flush=True)
    regime_of = [splits_decl.regime(d) for d in dates]
    # -- readings
    values: Dict[int, Dict[str, List[Optional[float]]]] = {}
    kinds: Dict[str, str] = {}
    not_public: Dict[str, Dict[str, int]] = {}
    with Switched():
        for lead in LEADS:
            published, spread_lag, holes, lead_kinds = read_lead(rows, registry, readable, lead, scored, per_release=False)
            published[ss.SPREAD_LAG] = spread_lag
            kinds.update(lead_kinds)
            released, _s, release_holes, _k = read_lead(rows, registry, affected, lead, scored, per_release=True)
            for column in affected:
                published[column + PER_RELEASE] = released[column]
                if release_holes.get(column):
                    not_public.setdefault(column + PER_RELEASE, {})[str(lead)] = release_holes[column]
            for column, n in holes.items():
                not_public.setdefault(column, {})[str(lead)] = n
            published.update(read_derived(rows, registry, lead, dates))
            values[lead] = published
            print(json.dumps({"read_lead": lead, "series": len(published)}), flush=True)
    for lead in LEADS:
        missing = [n for n in names if n not in values[lead]]
        if missing:
            raise SystemExit(f"series not read at lead {lead}: {missing}")
    states = {lead: values[lead].get(SCARCITY) for lead in LEADS}
    bands = {lead: [ss.band(s) for s in states[lead]] for lead in LEADS}
    # -- splits (positions in `dates`), per lead
    period_labels = [label for label in splits_decl.regime_labels if any(regime_of[i] == label for i in ordinary_idx)]
    split_positions: Dict[int, Dict[str, List[int]]] = {}
    for lead in LEADS:
        by = {"pooled": list(ordinary_idx)}
        for label in period_labels:
            by["regime:" + label] = [i for i in ordinary_idx if regime_of[i] == label]
        for b in BANDS:
            by["scarcity:" + b] = [i for i in ordinary_idx if bands[lead][i] == b]
        split_positions[lead] = by
    # -- matrices at lead 1
    lead1 = values[1]
    matrix_subsets = {"all_pooled": list(range(len(dates))), "ordinary_pooled": list(ordinary_idx)}
    for label in period_labels:
        matrix_subsets["ordinary_regime_" + label] = split_positions[1]["regime:" + label]
    for b in BANDS:
        matrix_subsets["ordinary_scarcity_" + b] = split_positions[1]["scarcity:" + b]
    matrices = {}
    matrix_subsets = {key: subset for key, subset in matrix_subsets.items() if subset}  # a state with no ordinary day has no matrix
    for key, subset in matrix_subsets.items():
        matrices[key] = correlation_matrix(lead1, names, subset)
        print(json.dumps({"matrix": key, "days": len(subset)}), flush=True)
    primary = matrices["ordinary_pooled"]
    clusters = {}
    for key in ("ordinary_pooled", "all_pooled"):
        rho = lambda a, b, m=matrices[key]: m[a][b]
        groups = complete_linkage(names, rho, CLUSTER_THRESHOLD)
        clusters[key] = [{"members": g, "representative": medoid(g, rho)} for g in groups]
    # -- target correlations, ordinary days
    correlations: Dict[str, dict] = {}
    for name in names:
        per_lead = {}
        for lead in LEADS:
            per_lead[str(lead)] = {split: ss.correlate(values[lead][name], targets, idx) for split, idx in split_positions[lead].items()}
        correlations[name] = per_lead
    # -- bootstrap: AUROC and the pre-onset contrast
    onset_days = pressure.onsets(rows, THRESHOLD_BP, dates)
    date_index = {d: i for i, d in enumerate(dates)}
    ordinary_set = set(ordinary_idx)
    ordinary_onsets = [d for d in onset_days if date_index.get(d) in ordinary_set]
    pre_flag = [0] * len(dates)
    onset_of: Dict[int, date] = {}
    for onset in ordinary_onsets:
        at = position[onset]
        for back in range(PRE_ONSET_DAYS[0], PRE_ONSET_DAYS[1] + 1):
            day = rows[at - back].date
            i = date_index.get(day)
            if i is not None and i in ordinary_set:
                pre_flag[i] = 1
                onset_of.setdefault(i, onset)
    _WORK.update(series=values, splits=split_positions, pressure=pressure_flag, pre=pre_flag, onset_of=onset_of)
    _WORK["resamples"] = make_resamples(split_positions)
    jobs = [(name, lead) for name in names for lead in LEADS]
    boots: Dict[str, dict] = {name: {"auroc": {}, "pre_onset": None} for name in names}
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        for count, (name, lead, out) in enumerate(pool.imap_unordered(_bootstrap_job, jobs, chunksize=4), 1):
            boots[name]["auroc"][str(lead)] = out["auc"]
            if lead == 1:
                boots[name]["pre_onset"] = out["pre"]
            if count % 50 == 0:
                print(json.dumps({"bootstrap_done": count, "of": len(jobs)}), flush=True)
    # -- incremental
    def best_abs(name):
        best = 0.0
        for lead in LEADS:
            r = correlations[name][str(lead)]["pooled"]["pressure"]["rho"]
            if r is not None:
                best = max(best, abs(r))
        return best

    candidates = [n for n in names if n not in CONTROLS and n != ss.SPREAD_LAG]
    top = sorted(candidates, key=lambda n: (-best_abs(n), n))[:TOP_SERIES]
    incremental = {}
    for name in top:
        per_lead = {}
        for lead in LEADS:
            idx = ordinary_idx
            controls = [[values[lead][c][i] for i in idx] for c in CONTROLS]
            x = [values[lead][name][i] for i in idx]
            cell = {}
            for target in TARGETS:
                y = [targets[target][i] for i in idx]
                raw, n = spearman_pairwise(x, y)
                cell[target] = {"n": n, "raw": raw, "partial": partial_spearman(x, y, controls)}
            per_lead[str(lead)] = cell
        incremental[name] = per_lead
    # -- due diligence measures from the panel
    columns_present = {}
    for column in rows[0].values:
        present = [row.date for row in rows if row.values.get(column) is not None]
        first_row = next((i for i, row in enumerate(rows) if row.values.get(column) is not None), None)
        columns_present[column] = {"first": present[0].isoformat() if present else None, "last": present[-1].isoformat() if present else None,
                                   "present": len(present), "rows": len(rows), "first_row": first_row}
    n_series = len(names)
    n_matrix_cells = sum(1 for _ in itertools.combinations(names, 2)) * len(matrices)
    result = {
        "scope": {
            "first_day": dates[0].isoformat(), "last_day": dates[-1].isoformat(), "scored_days": len(dates),
            "ordinary_days": len(ordinary_idx), "pressure_days": sum(pressure_flag),
            "pressure_days_ordinary": sum(pressure_flag[i] for i in ordinary_idx),
            "onsets": len(onset_days), "onsets_on_ordinary_days": len(ordinary_onsets), "onset_dates": [d.isoformat() for d in ordinary_onsets],
            "pre_onset_days": sum(pre_flag), "leads": list(LEADS), "series": n_series, "period_regimes": period_labels,
            "regime_days_ordinary": {split: len(idx) for split, idx in split_positions[1].items()},
            "panel_sha256": panel_sha, "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
            "tests": {
                "matrix_pairs": n_matrix_cells,
                "spearman_cells": n_series * len(LEADS) * len(TARGETS) * len(split_positions[1]),
                "auroc_cells": n_series * len(LEADS) * len(split_positions[1]),
                "pre_onset_cells": n_series * len(split_positions[1]),
                "incremental_cells": len(top) * len(LEADS) * len(TARGETS),
            },
        },
        "matrix_days": {k: len(v) for k, v in matrix_subsets.items()}, "names": names, "kinds": {n: kinds.get(n, "derived" if n in FOURTEEN else "n/a") for n in names},
        "clusters": clusters, "correlations": correlations, "bootstrap": boots,
        "incremental": {"controls": list(CONTROLS), "top": top, "cells": incremental},
        "not_public_at_lead": {c: v for c, v in sorted(not_public.items())},
        "columns": columns_present, "unreadable": unreadable, "per_release": affected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    matrices_dir = args.matrices
    matrices_dir.mkdir(parents=True, exist_ok=True)
    for key, matrix in matrices.items():
        with (matrices_dir / f"matrix_{key}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([""] + names)
            for name in names:
                writer.writerow([name] + ["" if matrix[name][o] is None else f"{matrix[name][o]:.4f}" for o in names])
    (matrices_dir / "matrices.json").write_text(
        json.dumps({"names": names, "matrices": {k: {a: {b: (None if v is None else round(v, 4)) for b, v in row.items()} for a, row in m.items()} for k, m in matrices.items()},
                    "days": {k: len(s) for k, s in matrix_subsets.items()}}, sort_keys=True) + "\n", encoding="utf-8")
    heat = {key: heatmap_svg(matrices[key], names, clusters["ordinary_pooled"], key) for key in ("ordinary_pooled", "all_pooled")}
    for key, svg in heat.items():
        (matrices_dir / f"heatmap_{key}.svg").write_text(svg, encoding="utf-8")
    print(json.dumps({"written": str(args.output), "series": n_series, "clusters": len(clusters["ordinary_pooled"])}))
    return 0


#: Due diligence, one row per source group: the registry entries it draws on, the panel columns it supplies, how its vintages and revisions
#: are handled, and the known construction caveats with the findings that record them. The publisher, frequency and publication instant
#: are read from `metadata/sources.json` and `metadata/sources_measurement.json`; the start of history and the gaps are measured on the panel.
DILIGENCE: Tuple[dict, ...] = (
    {
        "name": "NY Fed SOFR, with percentiles and volume",
        "registry": ("nyfed_sofr",),
        "columns": ("sofr_volume", "sofr_p1", "sofr_p25", "sofr_p75", "sofr_p99", "sofr_p75_iorb_bps", "sofr_p99_iorb_bps", "sofr_p99_iorb_sd15_bps", "sofr_p99_p75_bps"),
        "vintages": "first published about 08:00 ET on the next business day and may be revised about 14:30 ET that day; the registry dates a value at the finalized 15:00 ET. The snapshot is one retrieval, so a later revision is not tracked",
        "caveats": "panel history starts at the first publication, 2018-04-03; the back-filled 2014-18 history is not read while its posting instant is null (#572, guarded by PR #590; the posting dates are now #633)",
    },
    {
        "name": "NY Fed TGCR and BGCR, with percentiles and volume",
        "registry": ("nyfed_tgcr", "nyfed_bgcr"),
        "columns": ("tgcr", "bgcr", "bgcr_volume", "sofr_tgcr_bps", "bgcr_tgcr_bps"),
        "vintages": "first published on the next business day; 15:00 ET is the conservative finalized instant the adapter uses for all the secured rates",
        "caveats": "same start and the same back-fill posting question as SOFR (#572)",
    },
    {
        "name": "NY Fed EFFR",
        "registry": ("nyfed_effr",),
        "columns": ("effr", "sofr_above_effr_share_20", "effr_iorb_change_20_bps"),
        "vintages": "first published about 09:00 ET on the next business day; 15:00 ET is declared. Taken from the New York Fed as published, not from FRED's DFF copy",
        "caveats": "EFFR less IORB is a different market and target from SOFR less IORB (registry note on frb_ddp, #129)",
    },
    {
        "name": "FRED: reserve balances (WRESBAL) and Treasury General Account (WTREGEN), weekly",
        "registry": ("fred_macro_latest_vintage",),
        "columns": ("reserve_balances", "tga", "tga_change_x_reserves", "tga_change_5d"),
        "vintages": "FRED serves the latest revised vintage only; observations inherit the snapshot's retrieval instant, so a re-fetch does not reproduce an old snapshot's bytes. The published reading applies a declared weekly lag; the `@per_release` reading dates each Wednesday level at its H.4.1 release (#541)",
        "caveats": "the per-release calendar assumed a Thursday print for any week not in its exception list and ignored its declared coverage (#576, guarded by PR #590; coverage now runs through 2026-09-03, #625); ALFRED pulls exist at a few dates as revision studies, not as a daily series",
    },
    {
        "name": "H.8 total assets and the reserve-scarcity state",
        "registry": ("frb_h8",),
        "columns": ("bank_total_assets", "reserve_scarcity_state"),
        "vintages": "the H.8 is revised after its first print; the first print of a week is used, released the second Friday after the week ends at 16:15 ET",
        "caveats": "the scarcity state is reserves over total assets against a published 0.12 band, so it carries the weekly steps of both legs",
    },
    {
        "name": "NY Fed overnight reverse repo (ON RRP)",
        "registry": ("nyfed_on_rrp", "nyfed_on_rrp_sameday"),
        "columns": ("on_rrp", "on_rrp_sameday", "on_rrp_below_100bn"),
        "vintages": "the sum of amounts accepted over the day's operations; dated at 16:00 ET on the next business day because the Desk states no publication time. The same-day reading (#445) carries a value only on dates whose records were last written on the day itself before 15:00",
        "caveats": "an amount accepted that day, not the balance outstanding (registry note on nyfed_on_rrp); the same-day column has holes on dates without evidence",
    },
    {
        "name": "NY Fed standing repo facility and repo operations",
        "registry": ("nyfed_srf", "nyfed_repo_ops", "nyfed_repo_ops_sameday"),
        "columns": ("srf_take_up", "srf_take_up_positive", "fed_repo_accepted", "fed_repo_submitted", "fed_repo_rate_iorb_bps", "fed_repo_ops",
                    "fed_repo_log_accepted", "fed_repo_log_accepted_change", "fed_repo_days_since_positive", "fed_repo_accepted_sameday", "fed_repo_submitted_sameday",
                    "fed_repo_rate_iorb_bps_sameday", "fed_repo_ops_sameday", "fed_repo_log_accepted_sameday", "fed_repo_log_accepted_change_sameday",
                    "fed_repo_days_since_positive_sameday"),
        "vintages": "results are dated at 16:00 ET on the next business day: the Desk states no publication time and `lastUpdated` is a write time that was rewritten days later. The same-day sensitivity (#442) withholds the dates written after their own 16:00",
        "caveats": "`srf_take_up` starts with the facility's first operation on 2021-07-29, the `fed_repo_*` columns are present from the start of the panel; a day on which nothing was taken is 0.0",
    },
    {
        "name": "Treasury auctions: gross settlements",
        "registry": ("treasury_auctions",),
        "columns": ("treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons", "treasury_settlement_soma"),
        "vintages": "dated from the settlement by the published registry; the `@per_release` reading dates each settlement from the auction announcement at 12:00 ET (#541). Records carry no revision history",
        "caveats": "one aggregate across security types; SOMA add-ons are not in it; an auction with 'null' total_accepted at retrieval has no result instant; `treasury_settlement_soma` is a hole under announcement dating",
    },
    {
        "name": "Treasury auctions: net settlement",
        "registry": ("treasury_auction_net_settlement",),
        "columns": ("net_settlement", "net_settlement_bills", "net_settlement_due_5d"),
        "vintages": "counts the auctions announced on or before the day, at 12:00 ET; the announcement clock time is declared conservatively, not verified",
        "caveats": "the maturing amount is an estimate of the publicly held share (registry limitation)",
    },
    {
        "name": "Treasury daily bill rates",
        "registry": ("treasury_bill_rates",),
        "columns": ("tbill_4w", "tbill_13w"),
        "vintages": "one export per year; the quote date is the record date and availability is declared at 16:30 ET on it",
        "caveats": "the export header is not stable across years (17-week from 2022, 6-week from 2025); the page's quote time is the subject of #445, and a same-day reading is excluded",
    },
    {
        "name": "Treasury Daily Treasury Statement: TGA close",
        "registry": ("treasury_dts_tga",),
        "columns": ("tga_daily", "tga_daily_change"),
        "vintages": "the statement for a business day is published at 4:00 PM ET on the next business day; 16:30 ET that day is declared. The API keeps no vintages",
        "caveats": "a daily series beside FRED's weekly WTREGEN; the two are near-duplicates in the matrix",
    },
    {
        "name": "OFR short-term funding monitor: DVP, tri-party and GCF repo rates",
        "registry": ("ofr_stfm_repo", "ofr_stfm_repo_segments"),
        "columns": ("ofr_tri_rate", "ofr_gcf_rate", "ofr_dvp_rate", "ofr_dvp_minus_bgcr_bp", "ofr_dvp_minus_bgcr_bp_backfill", "dvp_volume_share", "dvp_volume_share_chg20"),
        "vintages": "the API states no publication time and keeps no vintages; its one timestamp is a last-write time. A day's value is dated at 16:00 ET two business days after it",
        "caveats": "history before 2020-09-09 was filled in after the OFR began publishing in real time and is blanked by a guard (#508, #522), so these series start in September 2020; the `_backfill` column therefore equals the real-time one here",
    },
    {
        "name": "NY Fed primary dealer statistics (FR 2004)",
        "registry": ("nyfed_fr2004",),
        "columns": ("dealer_treasury_position",),
        "vintages": "weekly, dated six days after the as-of date at 16:30 ET. The lag rests on the published release schedule and not on the snapshot",
        "caveats": "a '*' marks a figure withheld for confidentiality and yields no observation; the tracked export mixes as-of dates, so no date is taken from the file as a whole",
    },
    {
        "name": "Fed IORB implementation notes",
        "registry": ("fed_iorb_announcements",),
        "columns": ("iorb_announced_change_bps", "iorb_days_to_announced_change"),
        "vintages": "an event table of every note that changed the rate since 2018-04; each note is read only at or after its announcement instant. No revisions",
        "caveats": "scheduled: public at lead 1 only, a hole at longer leads; `iorb_days_to_announced_change` is a hole on days with no change scheduled, so its gaps are by design; a 0.0 change is a computed value, not a missing one",
    },
    {
        "name": "Policy register (hand-kept)",
        "registry": ("policy_register",),
        "columns": ("policy_days_since_known", "policy_days_until_effective", "policy_pending_count", "policy_iorb_offset_bp", "policy_qt_in_force",
                    "policy_standing_repo_in_force", "policy_slr_exclusion_in_force", "policy_reserve_management_in_force", "policy_debt_limit_reinstated"),
        "vintages": "computed from `metadata/policy_events.json` entries announced at or before 16:00 ET on the row's own date; no vintages",
        "caveats": "a register built by hand, not fetched; the in-force flags are step functions of the calendar, so a correlation with them is also a correlation with the period (this screen's reading, Tables 6 and 7)",
    },
    {
        "name": "Constructed from the sources above (no source of their own)",
        "registry": ("spread_nowcast", "satiation_columns", "satiation_distance_columns", "projected_reserves_columns"),
        "columns": ("spread_nowcast_bps", "satiation_dist_roll", "satiation_hinge_roll", "quarter_end", "tax_date", "days_to_month_end"),
        "vintages": "zero lag by construction: each row uses only reads the as-of rule allows at 16:00 ET on that day. The calendar columns are known in advance",
        "caveats": "the rolling satiation level works as a two-year reserves low and its hinge is on in 2022-23 (#621); the distance columns read reserves on the old weekly lag, one release behind the `+h41` rows they join (#622); the nowcast is the naive previous spread wherever its model is not fitted",
    },
)
#: Entries that supply no series in this screen, with the reason.
NOT_READ = {
    "sec_nmfp": "monthly as-filed bulk extracts with the extract's retrieval instant as availability; no panel column is built from it (`metadata/sec_nmfp_archives.json`)",
    "frb_ddp": "not a panel source: read only by the pre-SOFR history study (#129)",
    "treasury_bill_rates_sameday": "excluded: no publication time before 16:00 ET is evidenced (#445)",
    "back-filled 2014-18 history": "stamped as public in real time from 2014 although its posting instant is null; not read (#572, guarded by PR #590; the posting dates are now #633)",
}


def diligence_rows(result: Mapping) -> List[str]:
    registry: Dict[str, dict] = {}
    for name in ("sources", "sources_measurement"):
        registry.update(json.loads((REPO / "metadata" / f"{name}.json").read_text(encoding="utf-8")))
    columns = result["columns"]
    out = [
        "| source | publisher | start of history | frequency | publication instant used | vintages and revisions | gaps after the start | caveats |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for group in DILIGENCE:
        entries = [(r, registry[r]) for r in group["registry"] if r in registry]
        publishers = sorted({e["provider"] for _r, e in entries})
        freqs = sorted({e["frequency"] for _r, e in entries})
        instants = []
        for r, e in entries:
            lag = e.get("release_lag", {})
            if lag.get("days") is not None and lag.get("available_time"):
                instants.append(f"`{r}`: {lag['available_time']} ET, reference date + {lag['days']} day{'s' if lag['days'] != 1 else ''}")
            elif lag.get("basis"):
                instants.append(f"`{r}`: {lag['basis'].replace('_', ' ')}")
        present = [c for c in group["columns"] if c in columns and columns[c]["first"]]
        firsts = sorted(columns[c]["first"] for c in present)
        first = None if not firsts else firsts[0] if firsts[0] == firsts[-1] else f"{firsts[0]} to {firsts[-1]}, by column"
        gap_text = "-"
        if present:
            worst = []
            for c in present:
                info = columns[c]
                span = info["rows"] - info["first_row"]
                worst.append((span - info["present"], c, span))
            worst.sort(reverse=True)
            top = worst[0]
            gap_text = f"{top[0]} of {top[2]} rows (`{top[1]}`)" if top[0] else "none"
        out.append(
            f"| {group['name']} | {'; '.join(publishers)} | {first or '-'} | {'; '.join(freqs)} | {'; '.join(instants) or '-'} "
            f"| {group['vintages']} | {gap_text} | {group['caveats']} |"
        )
    for name, why in NOT_READ.items():
        out.append(f"| {name} | - | not read | - | - | - | - | {why} |")
    return out


# -- the heatmap and the report ---------------------------------------------------------------


def _colour(rho: Optional[float]) -> str:
    """A diverging scale: blue for negative, white at 0, orange for positive; grey for no value."""

    if rho is None:
        return "#d9d9d9"
    t = max(-1.0, min(1.0, rho))
    if t >= 0:
        low, high = (255, 255, 255), (217, 95, 2)
    else:
        low, high = (255, 255, 255), (27, 98, 168)
    k = abs(t)
    return "#%02x%02x%02x" % tuple(round(a + (b - a) * k) for a, b in zip(low, high))


def heatmap_svg(matrix, names: Sequence[str], clusters: Sequence[dict], title: str) -> str:
    """The Spearman matrix with series ordered by cluster, so redundant groups sit on the diagonal."""

    order = [m for group in clusters for m in group["members"]]
    n, cell, left, top = len(order), 6, 190, 190
    width, height = left + n * cell + 20, top + n * cell + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="sans-serif" font-size="5">',
           f'<title>Spearman correlation between series, lead 1, {title}; series ordered by complete-linkage group</title>',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<text x="10" y="14" font-size="10">Spearman correlation between series, lead 1, {title} (rows and columns in the same order)</text>']
    for i, a in enumerate(order):
        out.append(f'<text x="{left - 3}" y="{top + i * cell + 5}" text-anchor="end">{_esc(a)}</text>')
        out.append(f'<text transform="translate({left + i * cell + 5},{top - 3}) rotate(-90)">{_esc(a)}</text>')
        for j, b in enumerate(order):
            r = matrix[a][b]
            out.append(f'<rect x="{left + j * cell}" y="{top + i * cell}" width="{cell}" height="{cell}" fill="{_colour(r)}"/>')
    # group boundaries
    at = 0
    for group in clusters:
        size = len(group["members"])
        if size > 1:
            out.append(f'<rect x="{left + at * cell}" y="{top + at * cell}" width="{size * cell}" height="{size * cell}" fill="none" stroke="#222" stroke-width="0.6"/>')
        at += size
    out.append("</svg>\n")
    return "\n".join(out)


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _f(value, digits=3, signed=True) -> str:
    return "-" if value is None else f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _iv(interval, digits=2) -> str:
    return "-" if not interval else f"[{interval[0]:.{digits}f}, {interval[1]:.{digits}f}]"


def report_command(args) -> int:
    result = json.loads(args.result.read_text(encoding="utf-8"))
    out: List[str] = []
    scope = result["scope"]
    names = result["names"]
    # Table 1: clusters
    out.append("Table 1. Groups of redundant series (every pair |rho| >= %.1f, complete linkage), ordinary days pooled, lead 1. A series with no partner is not listed.\n" % CLUSTER_THRESHOLD)
    out.append("| representative | members | series |")
    out.append("|---|---|---|")
    groups = [g for g in result["clusters"]["ordinary_pooled"] if len(g["members"]) > 1]
    for g in sorted(groups, key=lambda g: (-len(g["members"]), g["representative"])):
        rest = [m for m in g["members"] if m != g["representative"]]
        out.append(f"| `{g['representative']}` | {len(g['members'])} | " + ", ".join(f"`{m}`" for m in rest) + " |")
    singles = [g["members"][0] for g in result["clusters"]["ordinary_pooled"] if len(g["members"]) == 1]
    out.append(f"\n{len(singles)} series have no partner at this threshold; with the representatives, {len(singles) + len(groups)} series carry what the {len(names)} do.\n")
    # Table 2: top series on ordinary days
    def best(name, target, split="pooled"):
        top_r, top_lead = None, None
        for lead in LEADS:
            r = result["correlations"][name][str(lead)][split][target]["rho"]
            if r is not None and (top_r is None or abs(r) > abs(top_r)):
                top_r, top_lead = r, lead
        return top_r, top_lead

    ranking = sorted(names, key=lambda n: (-(abs(best(n, "pressure")[0]) if best(n, "pressure")[0] is not None else 0.0), n))
    out.append("Table 2. Ordinary days, pooled: the 25 series with the largest absolute Spearman correlation with the +5 bp indicator over leads 1 to 10. Group representative in the last column.\n")
    out.append("| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | AUROC at lead 1 [90%] | days at lead 1 | group |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    rep_of = {}
    for g in result["clusters"]["ordinary_pooled"]:
        for m in g["members"]:
            rep_of[m] = g["representative"]
    for name in ranking[:25]:
        cells = [_f(result["correlations"][name][str(l)]["pooled"]["pressure"]["rho"]) for l in LEADS]
        a = result["bootstrap"][name]["auroc"]["1"]["pooled"]
        out.append(f"| `{name}` | " + " | ".join(cells) + f" | {_f(a['auc'], 2, False)} {_iv(a['interval'])} | {result['correlations'][name]['1']['pooled']['pressure']['n']} | `{rep_of[name]}` |")
    # Table 3: level and change
    out.append("\nTable 3. Ordinary days, pooled: the 12 series with the largest absolute Spearman correlation with the spread level and with the spread change, best lead of 1, 2, 3, 5, 10.\n")
    out.append("| target | series | best lead | rho | days |")
    out.append("|---|---|---|---|---|")
    for target in ("level", "change"):
        order = sorted(names, key=lambda n: (-(abs(best(n, target)[0]) if best(n, target)[0] is not None else 0.0), n))
        for name in order[:12]:
            r, lead = best(name, target)
            out.append(f"| {target} | `{name}` | {lead} | {_f(r)} | {result['correlations'][name][str(lead)]['pooled'][target]['n']} |")
    # Table 4: AUROC by regime for the top 12 by AUROC distance
    def auc_of(name, lead="1", split="pooled"):
        return result["bootstrap"][name]["auroc"][lead][split]

    by_auc = sorted([n for n in names if auc_of(n)["auc"] is not None], key=lambda n: (-abs(auc_of(n)["auc"] - 0.5), n))
    splits = list(result["bootstrap"][names[0]]["auroc"]["1"].keys())
    out.append("\nTable 4. Ordinary days, lead 1: the 15 series whose AUROC for pressure days is furthest from 0.5, with the 90% interval, pooled and by split. A split with too few pressure days is empty.\n")
    out.append("| series | " + " | ".join(splits) + " |")
    out.append("|---|" + "---|" * len(splits))
    for name in by_auc[:15]:
        cells = []
        for split in splits:
            c = auc_of(name, "1", split)
            cells.append("-" if c["auc"] is None else f"{c['auc']:.2f} {_iv(c['interval'])}")
        out.append(f"| `{name}` | " + " | ".join(cells) + " |")
    out.append("\nPressure days and ordinary days per split, lead 1: " + "; ".join(f"{s} {result['bootstrap'][names[0]]['auroc']['1'][s]['pressure_days']} of {scope['regime_days_ordinary'][s]}" for s in splits) + ".\n")
    # Table 5: pre-onset
    def pre_of(name, split="pooled"):
        return result["bootstrap"][name]["pre_onset"][split]

    by_pre = sorted([n for n in names if pre_of(n)["auc"] is not None], key=lambda n: (-abs(pre_of(n)["auc"] - 0.5), n))
    out.append(f"Table 5. Pre-onset contrast on ordinary days, lead 1: the 15 series whose pre-onset AUROC is furthest from 0.5. {scope['onsets_on_ordinary_days']} of the {scope['onsets']} onsets fall on ordinary days; {scope['pre_onset_days']} pre-onset days (1 to 5 panel days before them).\n")
    out.append("| series | pre-onset days | AUROC [90%] | std. diff. [90%] |")
    out.append("|---|---|---|---|")
    for name in by_pre[:15]:
        p = pre_of(name)
        out.append(f"| `{name}` | {p['n_pre']} | {p['auc']:.2f} {_iv(p['auc_interval'])} | {_f(p['std_diff'], 2)} {_iv(p['std_diff_interval'])} |")
    # Table 6: incremental
    out.append("\nTable 6. Incremental: Spearman with the +5 bp indicator on ordinary days, raw and after the as-of scarcity state and the tail spread are taken out, for the top series, by lead.\n")
    out.append("| series | " + " | ".join(f"lead {l} raw / partial" for l in LEADS) + " |")
    out.append("|---|" + "---|" * len(LEADS))
    for name in result["incremental"]["top"]:
        cells = []
        for lead in LEADS:
            c = result["incremental"]["cells"][name][str(lead)]["pressure"]
            cells.append(f"{_f(c['raw'], 2)} / {_f(c['partial'], 2)}")
        out.append(f"| `{name}` | " + " | ".join(cells) + " |")
    # Table 7: the same top series, by split
    splits_all = list(result["correlations"][names[0]]["1"].keys())
    out.append(
        "\nTable 7. Ordinary days, lead 1: Spearman with the +5 bp indicator in each split, for the top series of Table 6. "
        "A split with under %d days or %d pressure days is empty. The first row gives the pressure days in the split.\n" % (MINIMUM_DAYS, MINIMUM_PRESSURE)
    )
    out.append("| series | " + " | ".join(splits_all) + " |")
    out.append("|---|" + "---|" * len(splits_all))
    head = [str(result["correlations"][names[0]]["1"][sp]["pressure"]["pressure_days"]) for sp in splits_all]
    out.append("| pressure days | " + " | ".join(head) + " |")
    for name in result["incremental"]["top"]:
        cells = [_f(result["correlations"][name]["1"][sp]["pressure"]["rho"], 2) for sp in splits_all]
        out.append(f"| `{name}` | " + " | ".join(cells) + " |")
    # Table 8: due diligence
    out.append("\nTable 8. Due diligence, one row per source group.\n")
    out.extend(diligence_rows(result))
    # Table 9: counts
    t = scope["tests"]
    out.append("\nTable 9. Tests run. None is corrected for the number of tests.\n")
    out.append("| quantity | computed |")
    out.append("|---|---|")
    out.append(f"| series | {scope['series']} |")
    out.append(f"| pairwise Spearman cells (series pairs, in each of {len(result['matrix_days'])} matrices) | {t['matrix_pairs']} |")
    out.append(f"| Spearman cells against a target (series x leads x targets x splits) | {t['spearman_cells']} |")
    out.append(f"| AUROC cells with a bootstrap interval (series x leads x splits) | {t['auroc_cells']} |")
    out.append(f"| pre-onset cells with a bootstrap interval (series x splits, lead 1) | {t['pre_onset_cells']} |")
    out.append(f"| partial-correlation cells (top series x leads x targets) | {t['incremental_cells']} |")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "tables.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(args.output / "tables.md")}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    declare = sub.add_parser("declare", help="write the declaration (the series list) from the panel, before any statistic")
    declare.add_argument("--panel", type=Path, required=True)
    declare.set_defaults(func=declare_command)
    run = sub.add_parser("run", help="read every series as of each decision and compute the matrices and the screen")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--matrices", type=Path, required=True, help="directory for the matrices (CSV, JSON) and heatmaps (SVG)")
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(func=run_command)
    report = sub.add_parser("report", help="write the tables")
    report.add_argument("result", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
