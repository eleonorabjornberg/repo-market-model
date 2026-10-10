#!/usr/bin/env python3
"""Screen every data source against the spread and against pressure days (#478).

An exploratory measurement, not a record: nothing is selected, no model changes, no
published figure moves, and no day in a locked tier is read (`docs/decisions/lockbox.md`).
It writes JSON, Markdown and an SVG to the paths it is given and nothing into `docs/runs/`.
The numbers belong to the pull request that closes #478 and to the evidence folder
`docs/pivot/evidence/source-screen/`; they feed #473 and #477.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG4.csv --output AUG5.csv
    PYTHONPATH=src python3 scripts/nowcast.py panel --panel AUG5.csv --output AUG6.csv --summary OUT/nowcast_panel.json
    PYTHONPATH=src python3 scripts/dvp_segment_inputs.py panel --panel PUB.csv --output DVP.csv
    PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv
    PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv --output SCREEN.csv
    PYTHONPATH=src python3 scripts/source_screen.py run --panel SCREEN.csv --output OUT/screen.json
    PYTHONPATH=src python3 scripts/source_screen.py report OUT/screen.json --tables OUT/tables.md --heatmap OUT/heatmap.svg

* `panel` joins the columns of the scratch panels above onto one panel by date, up to 2025-12-31.
  A column two panels both carry must agree to the last digit, or the command refuses.
* `run` reads every series **as of each decision instant** with the as-of rule
  (`repo_model.asof.InformationRule`, `docs/decisions/information-set.md`), at leads of
  1, 2, 3, 5 and 10 panel days (the rule's `horizon`: the decision is made that many panel days
  before the scored day, so a lead of 1 is the rule every published record was scored under).
  Every column is declared with the availability its own module gives it
  (`measurement_fields`, `net_settlement`, `policy_features`, `fed_liquidity`, `nowcast`,
  `dvp_segment`, `early_warning`; the scarcity state is switched on as `scarcity.measurement_declaration`
  does). A column with no row-relative availability is refused by the rule and is listed under
  `unreadable` with the refusal, never read at the row it sits on. The spread's own as-of lag
  (`spread_bps`, the latest spread public at the decision) is screened beside them.
* The target days are the lead-1 fold grid from 2018-06-29 to 2025-12-31, the days every
  published comparison scores, the same days at every lead. The screen fits nothing, so a longer
  lead does not need a longer training history; it only needs the earlier row to exist.
* Three targets: the spread level `s_T`; the change `s_T - s_(T-1)` over the scored day (at a lead
  of 1 this is the next-day change after the decision); the pressure indicator, the spread strictly
  above +5 bp on whole basis points (`repo_model.data.exceeds_bp`).
* Spearman correlation (average ranks), reported with the days it rests on and, for the
  indicator, the pressure days among them. A cell with fewer than `MINIMUM_DAYS` days or fewer than
  `MINIMUM_PRESSURE` pressure days (or none that is not pressure) is left empty, not reported as 0.
* The pre-onset comparison: an onset is a pressure day with no pressure day on the
  `repo_model.pressure.ONSET_QUIET_DAYS` panel days before it (`pressure.onsets`). The series, read at a
  lead of 1, on the 1 to 5 panel days before each onset is compared with every other scored day:
  the two means, the difference in units of the other days' standard deviation, and the share of
  (pre-onset, other) pairs in which the pre-onset value is higher (the AUC; ties count a half).
* Splits: the as-of reserve-scarcity state at the same lead (0 and 1 `ample`, 2 and 3 `scarce`, no
  reading `unknown`, as `repo_model.group_calibration` groups it) and the calendar year.

Every number is exploratory: series x leads x 3 targets correlations are computed, and the
report states the count. Nothing here selects a model input.

Reads the scratch panels, which are gitignored, so this is not a test (the same posture as
`scripts/spread_change_autocorrelation.py`). Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, dvp_segment, early_warning, fed_liquidity, measurement_fields  # noqa: E402
from repo_model import net_settlement, nowcast, policy_features, pressure, scarcity  # noqa: E402
from repo_model.asof import KIND_OBSERVED, InformationRule, InformationSet, fold_grid  # noqa: E402
from repo_model.data import DailyObservation, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.registry import RegistryContractError  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

FIRST_DAY = date(2018, 6, 29)
LAST_DAY = date(2025, 12, 31)
LEADS = (1, 2, 3, 5, 10)
THRESHOLD_BP = 5.0
DECISION_TIME = time(16, 0)
MINIMUM_HISTORY = 61
#: A correlation cell needs this many days, and this many pressure days (and a day that is not one).
MINIMUM_DAYS = 30
MINIMUM_PRESSURE = 3
#: The pre-onset window, in panel days before the onset day (the onset day itself is not in it).
PRE_ONSET_DAYS = (1, 5)
CALLED_OUT_YEARS = (2018, 2020, 2024)
BANDS = ("ample", "scarce", "unknown")
TARGETS = ("level", "change", "pressure")
SCARCITY = scarcity.RESERVE_SCARCITY_STATE
#: How many rows the readable tables show; the JSON carries every series.
TOP_PRE_ONSET = 25
TOP_SPLITS = 15
TOP_WITHIN = 8

#: The five models that pass tier 1 of the pressure judge at lead >= 1 under the unweighted rule
#: (`docs/pivot/weighted-miss-result.md`, Table 1, column "tier 1, unweighted"), and the declaration
#: that lists the inputs of each (`metadata/risk_date_severity.json`).
TIER_1_PASSERS = (
    "risk_gbm",
    "risk_gbm_base",
    "risk_logistic",
    "risk_logistic_base",
    "risk_quantile_skewt_base",
)
RISK_DECLARATION = REPO / "metadata" / "risk_date_severity.json"

#: Panel columns that are not series to screen: the date, and the target's own legs, which the
#: spread series (`spread_bps`) carries.
NOT_SCREENED = ("date", "sofr", "iorb")

#: The spread's own as-of lag, screened beside the columns (the persistence value).
SPREAD_LAG = "spread_bps"

#: Every snapshot directory under `tests/fixtures/snapshots/`, with the series built from it or
#: why none can be read as-of. `tests/test_source_screen.py` refuses a directory this table lacks.
SNAPSHOT_INVENTORY: Mapping[str, Tuple[str, str]] = {
    "funding_inputs": ("read", "NY Fed SOFR/TGCR/BGCR rates and volumes, FRED H.4.1 weeklies (reserves, TGA), Treasury bills and settlement: the published panel's columns"),
    "treasury_bills": ("read", "Treasury bill rates (tbill_4w, tbill_13w), by year"),
    "treasury_auctions": ("read", "gross settlement columns of the published panel (treasury_settlement*)"),
    "net_settlement_inputs": ("read", "net settlement columns (net_settlement, net_settlement_bills, net_settlement_due_5d)"),
    "on_rrp_inputs": ("read", "on_rrp, the Desk's ON RRP operation results"),
    "nyfed-rrp-results": ("read", "the Desk's ON RRP operation results the on_rrp column is built from"),
    "h8_inputs": ("read", "bank_total_assets and reserve_scarcity_state (H.8 first prints)"),
    "nyfed_effr_inputs": ("read", "effr"),
    "ofr_inputs": ("read", "OFR repo segment rates (ofr_tri_rate, ofr_gcf_rate, ofr_dvp_rate) and the DVP-segment columns"),
    "dts_inputs": ("read", "tga_daily, the daily Treasury General Account balance, and its change"),
    "srf_inputs": ("read", "srf_take_up, the standing repo facility take-up"),
    "repo_ops_inputs": ("read", "the Desk's repo operations (fed_repo_* columns, both availability readings)"),
    "fed-iorb-announcements": ("read", "iorb_announced_change_bps, iorb_days_to_announced_change"),
    "fr2004": ("read", "dealer_treasury_position (FR 2004 weekly)"),
    "treasury_bill_rates_page": ("cannot", "the Treasury text-view page as served: evidence for #445 (its 3:30 pm quote time), not a data input; no series is built from it"),
    "nyfed-primary-dealer": ("cannot", "a hand-downloaded 'latest' CSV with no recorded retrieval time (its manifest says 'None'): the as-of rule cannot say when any row was public; its weekly positions are the FR 2004's, already read"),
    "frb_ddp": ("cannot", "the Board's H.15 and PRATES SDMX files, read only by repo_model.effr_history for the pre-SOFR study; EFFR and IOER are already read from the NY Fed and FRED, and the primary credit rate is a step series set by the policy register"),
    "alfred-dff": ("cannot", "ALFRED vintage pulls at three dates, kept to study revisions: not a daily series with a first print per day"),
    "alfred-dff-first-print": ("cannot", "ALFRED pulls at five dates, kept to study first prints: not a daily series"),
    "alfred-h41-first-print": ("cannot", "ALFRED first-print pulls around three dates: a revision study, not a daily series"),
    "alfred-ioer": ("cannot", "ALFRED vintage pulls at three dates: IORB/IOER is read from the NY Fed and the announcements table"),
    "alfred-rrpontsyd": ("cannot", "ALFRED vintage pulls at dated vintages: on_rrp is read from the Desk's results"),
    "alfred-wlrrafoial": ("cannot", "ALFRED vintage pulls (H.4.1 reverse repos, foreign official): a revision study, no daily first prints"),
    "alfred-wlrral": ("cannot", "ALFRED vintage pulls (H.4.1 reverse repos): a revision study, no daily first prints"),
    "alfred-wlrraol": ("cannot", "ALFRED vintage pulls (H.4.1 reverse repos, other): a revision study, no daily first prints"),
    "alfred-wresbal": ("cannot", "ALFRED vintage pulls: reserve_balances is read from the FRED latest-vintage snapshot under the registry's declared lag"),
    "alfred-wtregen": ("cannot", "ALFRED vintage pulls at four dates: tga is read from the FRED latest-vintage snapshot under the registry's declared lag"),
}


#: Raw columns of the scratch panels that no module declares as a feature on its own, with the source
#: fields its derived columns read them from (`dvp_segment`, `contract.SRF_OPERATION_RESULTS_FIELDS`).
RAW_INPUTS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "bgcr_volume": (dvp_segment._BGCR_VOLUME,),
    "ofr_dvp_rate": (dvp_segment._OFR_RATE,),
    "srf_take_up": tuple(contract.SRF_OPERATION_RESULTS_FIELDS),
}


def switched_on_fields() -> Dict[str, Tuple[Tuple[str, str], ...]]:
    """Every scratch column's declared source fields, from the module that builds it."""

    merged: Dict[str, Tuple[Tuple[str, str], ...]] = {}
    for module_fields in (
        measurement_fields.COLUMN_FIELDS,
        net_settlement.COLUMN_FIELDS,
        policy_features.COLUMN_FIELDS,
        fed_liquidity.ALL_COLUMN_FIELDS,
        nowcast.COLUMN_FIELDS,
        dvp_segment.COLUMN_FIELDS,
        early_warning.COLUMN_FIELDS,
    ):
        for column, fields in module_fields.items():
            if column in merged and tuple(merged[column]) != tuple(fields):
                raise ValueError(f"{column!r} is declared on different fields by two modules")
            merged[column] = tuple(fields)
    # Raw inputs that a module reads only through its derived columns, declared here on the fields the
    # module itself draws them from, so they can be screened on their own.
    for column, fields in RAW_INPUTS.items():
        merged.setdefault(column, tuple(fields))
    return merged


def declared_features() -> Dict[str, Tuple[Tuple[str, str], ...]]:
    """`contract.FEATURE_FIELDS` with the scarcity inputs and every scratch column switched on."""

    base = dict(scarcity.measurement_feature_fields())
    base.update(switched_on_fields())
    return base


class Switched:
    """`declared_features()` in `contract` for the run, and the published map back after it."""

    def __enter__(self):
        self._saved = (contract.FEATURE_FIELDS, contract.FEATURE_SOURCES)
        fields = declared_features()
        contract.FEATURE_FIELDS = MappingProxyType(fields)
        contract.FEATURE_SOURCES = MappingProxyType(
            {column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()}
        )
        return self

    def __exit__(self, *exc):
        contract.FEATURE_FIELDS, contract.FEATURE_SOURCES = self._saved
        return False


# -- statistics ---------------------------------------------------------------


def average_ranks(values: Sequence[float]) -> List[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start
        while stop + 1 < len(order) and values[order[stop + 1]] == values[order[start]]:
            stop += 1
        middle = (start + stop) / 2.0 + 1.0
        for position in range(start, stop + 1):
            ranks[order[position]] = middle
        start = stop + 1
    return ranks


def pearson(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(x)
    mean_x, mean_y = sum(x) / n, sum(y) / n
    sxx = sum((a - mean_x) ** 2 for a in x)
    syy = sum((b - mean_y) ** 2 for b in y)
    if sxx <= 0.0 or syy <= 0.0:
        return None
    sxy = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    return sxy / math.sqrt(sxx * syy)


def spearman(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    """Spearman's rank correlation, or `None` when either side is constant."""

    if len(x) != len(y):
        raise ValueError("the two samples differ in length")
    if len(x) < 2:
        return None
    return pearson(average_ranks(x), average_ranks(y))


def pre_onset_contrast(pre: Sequence[float], other: Sequence[float]) -> Optional[dict]:
    """Means, standardised difference and AUC of the pre-onset values against the other days'."""

    if not pre or len(other) < 2:
        return None
    mean_pre = sum(pre) / len(pre)
    mean_other = sum(other) / len(other)
    sd = math.sqrt(sum((v - mean_other) ** 2 for v in other) / (len(other) - 1))
    ranks = average_ranks(list(pre) + list(other))
    rank_sum = sum(ranks[: len(pre)])
    auc = (rank_sum - len(pre) * (len(pre) + 1) / 2.0) / (len(pre) * len(other))
    return {
        "n_pre": len(pre),
        "n_other": len(other),
        "mean_pre": mean_pre,
        "mean_other": mean_other,
        "std_diff": None if sd <= 0.0 else (mean_pre - mean_other) / sd,
        "auc": auc,
    }


# -- the panel ----------------------------------------------------------------


def _cell(value) -> str:
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    base = load_daily_panel(args.panel)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    extra_values: Dict[str, Dict[date, Optional[float]]] = {}
    for path in args.extra:
        for row in load_daily_panel(path):
            for column, value in row.values.items():
                extra_values.setdefault(column, {})[row.date] = value
    keep = [row for row in base if row.date <= LAST_DAY]
    columns = list(header[1:])
    for column in extra_values:
        if column in keep[0].values:
            for row in keep:
                if extra_values[column].get(row.date) != row.values[column]:
                    raise ValueError(f"{column!r} differs between the panels on {row.date}")
        elif column not in columns:
            columns.append(column)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date"] + columns)
        for row in keep:
            out = []
            for column in columns:
                value = row.values[column] if column in row.values else extra_values[column].get(row.date)
                out.append(_cell(value))
            writer.writerow([row.date.isoformat()] + out)
    print(json.dumps({"rows": len(keep), "columns": len(columns), "last": keep[-1].date.isoformat()}))
    return 0


# -- reading ------------------------------------------------------------------


def screened_columns(rows: Sequence[DailyObservation]) -> List[str]:
    return [column for column in rows[0].values if column not in NOT_SCREENED]


def probe(registry, columns, rows) -> Tuple[List[str], Dict[str, str]]:
    """The columns the as-of rule can read, and the refusal for each it cannot."""

    dates = [row.date for row in rows]
    readable: List[str] = []
    unreadable: Dict[str, str] = {}
    middle = len(rows) // 2
    for column in columns:
        try:
            rule = InformationRule(registry, (column,), decision_time=DECISION_TIME, horizon=1)
            rule.information_set(dates, middle)
        except (KeyError, RegistryContractError, SplitError, ValueError) as exc:
            unreadable[column] = f"{type(exc).__name__}: {exc}"
        else:
            readable.append(column)
    return readable, unreadable


def read_series(rows, registry, columns):
    """For the scored days, each lead's as-of value of each column.

    A calendar column is known in advance and is read on the scored day itself; every other
    column is read at the latest row public at the decision instant, `lead` panel days before.
    """

    dates = [row.date for row in rows]
    scored = [
        index
        for index in fold_grid(
            dates, registry, decision_time=DECISION_TIME, minimum_history=MINIMUM_HISTORY, horizon=1
        )
        if FIRST_DAY <= dates[index] <= LAST_DAY
    ]
    require_unlocked((dates[index] for index in scored), where="source_screen")
    series: Dict[int, Dict[str, List[Optional[float]]]] = {}
    not_public: Dict[str, Dict[int, int]] = {}
    for lead in LEADS:
        rule = InformationRule(registry, tuple(columns), decision_time=DECISION_TIME, horizon=lead)
        wanted = {group.feature: position for position, group in enumerate(rule.groups) if position}
        if lead == LEADS[0]:
            kinds = {group.feature: group.kind for group in rule.groups if group.feature in wanted}
            kinds[SPREAD_LAG] = KIND_OBSERVED
        values: Dict[str, List[Optional[float]]] = {column: [] for column in columns}
        values[SPREAD_LAG] = []
        for index in scored:
            info = rule.information_set(dates, index)
            for column in columns:
                read = info.reads[wanted[column]]
                # Each read is checked alone: a scheduled input announced after this lead's decision
                # instant is not public then (`LookAheadError`), and is a hole at this lead, not a leak.
                # A stale read (`StaleReadError`) is a bug and propagates.
                try:
                    rule.check(
                        dates, InformationSet(info.scored_index, info.decision_instant, info.anchor, (read,))
                    )
                except LookAheadError:
                    values[column].append(None)
                    not_public.setdefault(column, {}).setdefault(lead, 0)
                    not_public[column][lead] += 1
                    continue
                values[column].append(rows[read.row].values.get(column))
            values[SPREAD_LAG].append(rows[info.anchor].spread_bps)
        series[lead] = values
    return [dates[i] for i in scored], series, not_public, kinds


def band(state: Optional[float]) -> str:
    if state is None:
        return "unknown"
    return "ample" if state < 2 else "scarce"


def correlate(x, y_by_target, subset) -> dict:
    """Spearman of `x` with each target on `subset` (days where `x` is present)."""

    cell = {}
    for target, y in y_by_target.items():
        pairs = [(x[i], y[i]) for i in subset if x[i] is not None]
        n = len(pairs)
        entry = {"n": n}
        if target == "pressure":
            events = sum(1 for _a, b in pairs if b > 0)
            entry["pressure_days"] = events
            ok = n >= MINIMUM_DAYS and events >= MINIMUM_PRESSURE and n - events >= 1
        else:
            ok = n >= MINIMUM_DAYS
        entry["rho"] = spearman([a for a, _b in pairs], [b for _a, b in pairs]) if ok else None
        cell[target] = entry
    return cell


def tier_one_usage() -> Dict[str, List[str]]:
    """For each input name any tier-1 passer declares, the passers that use it."""

    declared = json.loads(RISK_DECLARATION.read_text(encoding="utf-8"))
    used: Dict[str, List[str]] = {}
    for name in TIER_1_PASSERS:
        spec = declared["candidates"][name]
        for group in spec["inputs"]:
            for feature in declared["features"][group]:
                used.setdefault(feature, []).append(name)
    return used


def run_command(args) -> int:
    rows = load_daily_panel(args.panel)
    registry = measurement_fields.load_registry()
    if rows[-1].date > LAST_DAY:
        raise SystemExit(f"the panel runs past {LAST_DAY}; a screen reads no day in a locked tier")
    with Switched():
        columns = screened_columns(rows)
        readable, unreadable = probe(registry, columns, rows)
        scored, series, not_public, kinds = read_series(rows, registry, readable)
    position = {row.date: i for i, row in enumerate(rows)}
    spreads = [row.spread_bps for row in rows]
    targets = {
        "level": [spreads[position[d]] for d in scored],
        "change": [spreads[position[d]] - spreads[position[d] - 1] for d in scored],
        "pressure": [1.0 if exceeds_bp(spreads[position[d]], THRESHOLD_BP) else 0.0 for d in scored],
    }
    onset_days = pressure.onsets(rows, THRESHOLD_BP, scored)
    scored_index = {d: i for i, d in enumerate(scored)}
    pre_days = set()
    for onset in onset_days:
        at = position[onset]
        for back in range(PRE_ONSET_DAYS[0], PRE_ONSET_DAYS[1] + 1):
            day = rows[at - back].date
            if day in scored_index:
                pre_days.add(day)
    pre_index = sorted(scored_index[d] for d in pre_days)
    pre_set = set(pre_index)
    other_index = [i for i in range(len(scored)) if i not in pre_set]
    years = sorted({d.year for d in scored})

    def regimes(lead: int) -> List[str]:
        states = series[lead].get(SCARCITY)
        return [band(s) for s in states] if states is not None else ["unknown"] * len(scored)

    out_series = {}
    for column in readable + [SPREAD_LAG]:
        per_lead = {}
        for lead in LEADS:
            regime = regimes(lead)
            splits = {"all": list(range(len(scored)))}
            for name in BANDS:
                splits[f"regime:{name}"] = [i for i in range(len(scored)) if regime[i] == name]
            for year in years:
                splits[f"year:{year}"] = [i for i, d in enumerate(scored) if d.year == year]
            per_lead[str(lead)] = {
                name: correlate(series[lead][column], targets, idx) for name, idx in splits.items()
            }
        x1 = series[1][column]
        regime1 = regimes(1)
        keeps = {"all": lambda i: True}
        keeps.update({f"regime:{name}": (lambda i, name=name: regime1[i] == name) for name in BANDS})
        keeps.update({f"year:{year}": (lambda i, year=year: scored[i].year == year) for year in years})
        pre = {
            name: pre_onset_contrast(
                [x1[i] for i in pre_index if keep(i) and x1[i] is not None],
                [x1[i] for i in other_index if keep(i) and x1[i] is not None],
            )
            for name, keep in keeps.items()
        }
        out_series[column] = {"kind": kinds[column], "leads": per_lead, "pre_onset": pre}
    result = {
        "scope": {
            "first_day": scored[0].isoformat(),
            "last_day": scored[-1].isoformat(),
            "scored_days": len(scored),
            "leads": list(LEADS),
            "threshold_bp": THRESHOLD_BP,
            "pressure_days": int(sum(targets["pressure"])),
            "onsets": [d.isoformat() for d in onset_days],
            "pre_onset_days": len(pre_index),
            "pre_onset_window_panel_days": list(PRE_ONSET_DAYS),
            "years": years,
            "called_out_years": list(CALLED_OUT_YEARS),
            "minimum_days": MINIMUM_DAYS,
            "minimum_pressure_days": MINIMUM_PRESSURE,
            "series_screened": len(out_series),
            "correlations_computed": len(out_series) * len(LEADS) * len(TARGETS),
            "regime_days": {name: regimes(1).count(name) for name in BANDS},
            "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        },
        "series": out_series,
        "unreadable": unreadable,
        "not_public_at_lead": {c: {str(l): n for l, n in v.items()} for c, v in sorted(not_public.items())},
        "tier_1_passers": tier_one_usage(),
        "snapshots": {name: {"status": s, "note": n} for name, (s, n) in SNAPSHOT_INVENTORY.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result["scope"].items() if k != "onsets"}, indent=1))
    print(f"unreadable: {len(unreadable)}")
    return 0


# -- the report ---------------------------------------------------------------


def _fmt(value, digits=3, signed=True) -> str:
    if value is None:
        return "-"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def best_pressure_lead(series: dict, split: str = "all") -> Tuple[Optional[float], Optional[int]]:
    best, best_lead = None, None
    for lead in LEADS:
        rho = series["leads"][str(lead)][split]["pressure"]["rho"]
        if rho is not None and (best is None or abs(rho) > abs(best)):
            best, best_lead = rho, lead
    return best, best_lead


def ranking(result: dict, split: str = "all") -> List[Tuple[str, float, int]]:
    ranked = []
    for name, series in result["series"].items():
        rho, lead = best_pressure_lead(series, split)
        if rho is not None:
            ranked.append((name, rho, lead))
    ranked.sort(key=lambda item: (-abs(item[1]), item[0]))
    return ranked


def tables_markdown(result: dict) -> str:
    scope = result["scope"]
    passers = result["tier_1_passers"]
    ranked = ranking(result)
    leads = scope["leads"]
    lines = [
        "## Ranking by correlation with the pressure indicator",
        "",
        f"Scored days {scope['first_day']} to {scope['last_day']} ({scope['scored_days']} days, {scope['pressure_days']} "
        f"above +{scope['threshold_bp']:g} bp, {len(scope['onsets'])} onsets). Spearman correlation of the series, read as of the "
        "decision instant, with the +5 bp pressure indicator of the scored day. The rank is by the largest absolute value over leads "
        f"{', '.join(str(lead) for lead in leads)}. `Read as` is how the as-of rule reads it: `observed` at the latest row public at the decision instant, `scheduled` (known in advance for the scored day itself, and public at a lead of 1 only) or `calendar` (known in advance). The last column lists the tier-1 passers that name the series as an input.",
        "",
        "| rank | series | " + " | ".join(f"lead {lead}" for lead in leads) + " | strongest | days at lead 1 | read as | used by tier-1 passers |",
        "|---|---|" + "---|" * len(leads) + "---|---|---|---|",
    ]
    for rank, (name, rho, lead) in enumerate(ranked, start=1):
        cells = [_fmt(result["series"][name]["leads"][str(l)]["all"]["pressure"]["rho"]) for l in leads]
        users = passers.get(name)
        lines.append(
            f"| {rank} | `{name}` | " + " | ".join(cells) + f" | {_fmt(rho)} at {lead} | {result['series'][name]['leads']['1']['all']['pressure']['n']} | "
            f"{result['series'][name]['kind']} | "
            + (", ".join(f"`{u}`" for u in users) if users else "no") + " |"
        )
    unranked = sorted(set(result["series"]) - {n for n, _r, _l in ranked})
    if unranked:
        lines += [
            "",
            "No correlation could be formed (a constant series, or too few days or pressure days): "
            + ", ".join(f"`{n}`" for n in unranked) + ".",
        ]
    lines += ["", "## Pre-onset window", ""]
    lines += [
        f"The series read at lead 1 on the {scope['pre_onset_window_panel_days'][0]} to {scope['pre_onset_window_panel_days'][1]} "
        f"panel days before each of the {len(scope['onsets'])} onsets ({scope['pre_onset_days']} scored days) against every other "
        "scored day. The difference is in units of the other days' standard deviation; the AUC is the share of "
        "(pre-onset, other) pairs with the pre-onset value higher.",
        "",
        "| series | mean before onsets | mean other days | difference (sd) | AUC |",
        "|---|---|---|---|---|",
    ]
    by_contrast = []
    for name, series in result["series"].items():
        c = series["pre_onset"]["all"]
        if c and c["std_diff"] is not None:
            by_contrast.append((abs(c["std_diff"]), name, c))
    by_contrast.sort(key=lambda item: (-item[0], item[1]))
    for _size, name, c in by_contrast[:TOP_PRE_ONSET]:
        lines.append(
            f"| `{name}` | {c['mean_pre']:.4g} | {c['mean_other']:.4g} | {_fmt(c['std_diff'], 2)} | {c['auc']:.2f} |"
        )
    lines += ["", f"The {TOP_PRE_ONSET} largest by absolute difference; every series is in `screen.json`.", ""]
    lines += regime_year_tables(result, ranked)
    return "\n".join(lines) + "\n"


def regime_year_tables(result: dict, ranked) -> List[str]:
    scope = result["scope"]
    years = scope["years"]
    leads = scope["leads"]
    lines = ["## By regime", ""]
    lines += [
        f"The as-of reserve-scarcity state at the same lead (lead 1 shown for the day counts): ample (0 and 1) on "
        f"{scope['regime_days']['ample']} days, scarce (2 and 3) on {scope['regime_days']['scarce']}, no reading on "
        f"{scope['regime_days']['unknown']}. Spearman correlation with the pressure indicator, the {TOP_SPLITS} top-ranked series, "
        "at the lead of their strongest pooled correlation. A `-` has too few days or pressure days.",
        "",
        "| series | lead | all | ample | scarce | unknown |",
        "|---|---|---|---|---|---|",
    ]
    for name, _rho, lead in ranked[:TOP_SPLITS]:
        cell = result["series"][name]["leads"][str(lead)]
        lines.append(
            f"| `{name}` | {lead} | "
            + " | ".join(_fmt(cell[s]["pressure"]["rho"]) for s in ("all", "regime:ample", "regime:scarce", "regime:unknown"))
            + " |"
        )
    pressure_by_year = {
        y: result["series"][SPREAD_LAG]["leads"]["1"][f"year:{y}"]["pressure"]["pressure_days"] for y in years
    }
    lines += ["", "### Strongest within each regime", ""]
    lines += [
        f"The {TOP_WITHIN} series with the largest absolute correlation inside the regime, over leads {', '.join(str(l) for l in leads)}. "
        "A series that is constant inside a regime, or has too few days there, is not ranked.",
        "",
        "| regime | rank | series | strongest | days | pressure days |",
        "|---|---|---|---|---|---|",
    ]
    for split in ("regime:ample", "regime:scarce"):
        for rank, (name, rho, lead) in enumerate(ranking(result, split)[:TOP_WITHIN], start=1):
            cell = result["series"][name]["leads"][str(lead)][split]["pressure"]
            lines.append(
                f"| {split.split(':')[1]} | {rank} | `{name}` | {_fmt(rho)} at {lead} | {cell['n']} | {cell['pressure_days']} |"
            )
    lines += [
        "",
        "## By year",
        "",
        "Spearman correlation with the pressure indicator, the same series and leads. Years 2018, 2020 and 2024 are in bold; "
        "the first row is the number of pressure days in the year.",
        "",
        "| series | lead | " + " | ".join(f"**{y}**" if y in scope["called_out_years"] else str(y) for y in years) + " |",
        "|---|---|" + "---|" * len(years),
        "| pressure days | | " + " | ".join(str(pressure_by_year[y]) for y in years) + " |",
    ]
    for name, _rho, lead in ranked[:TOP_SPLITS]:
        cell = result["series"][name]["leads"][str(lead)]
        lines.append(
            f"| `{name}` | {lead} | " + " | ".join(_fmt(cell[f"year:{y}"]["pressure"]["rho"]) for y in years) + " |"
        )
    lines += ["", "### Strongest within the called-out years", ""]
    lines += [
        "The same ranking inside 2018, 2020 and 2024, the years with the fewest pressure days to rest on. "
        "Read these as anecdotes: the days are in the first row of the table above.",
        "",
        "| year | rank | series | strongest | days | pressure days |",
        "|---|---|---|---|---|---|",
    ]
    for year in [y for y in scope["called_out_years"] if y in years]:
        split = f"year:{year}"
        for rank, (name, rho, lead) in enumerate(ranking(result, split)[:TOP_WITHIN], start=1):
            cell = result["series"][name]["leads"][str(lead)][split]["pressure"]
            lines.append(f"| {year} | {rank} | `{name}` | {_fmt(rho)} at {lead} | {cell['n']} | {cell['pressure_days']} |")
    lines += [
        "",
        "## Against the spread: the level and the next-day change",
        "",
        "The same series against the spread level and against the change in the spread over the scored day, pooled, by lead; "
        f"the {TOP_SPLITS} series with the largest absolute correlation with the level at lead 1.",
        "",
        "| series | target | " + " | ".join(f"lead {lead}" for lead in leads) + " |",
        "|---|---|" + "---|" * len(leads),
    ]
    by_level = []
    for name, series in result["series"].items():
        rho = series["leads"]["1"]["all"]["level"]["rho"]
        if rho is not None:
            by_level.append((abs(rho), name))
    by_level.sort(key=lambda item: (-item[0], item[1]))
    for _size, name in by_level[:TOP_SPLITS]:
        for target in ("level", "change"):
            cells = [_fmt(result["series"][name]["leads"][str(l)]["all"][target]["rho"]) for l in leads]
            lines.append(f"| `{name}` | {target} | " + " | ".join(cells) + " |")
    return lines


def heatmap_svg(result: dict) -> str:
    """Series x lead, coloured by Spearman correlation with the pressure indicator."""

    scope = result["scope"]
    names = [name for name, _r, _l in ranking(result)]
    cell_w, cell_h, left, top = 64, 15, 330, 62
    width = left + cell_w * len(LEADS) + 40
    height = top + cell_h * len(names) + 30
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Spearman correlation of each series with the +{scope["threshold_bp"]:g} bp pressure indicator, by lead">',
        "<style>text{font:11px sans-serif;fill:#222}.h{font-weight:bold}rect.c{stroke:#fff;stroke-width:.5}"
        "@media (prefers-color-scheme:dark){text{fill:#ddd}rect.c{stroke:#111}}</style>",
        f'<text class="h" x="4" y="14">Spearman correlation with the +{scope["threshold_bp"]:g} bp pressure indicator, '
        f'{scope["first_day"]} to {scope["last_day"]}</text>',
        '<text x="4" y="30">exploratory screen; ranked by the strongest absolute value over the leads; blank = not formed</text>',
    ]
    for j, lead in enumerate(LEADS):
        out.append(f'<text class="h" x="{left + j * cell_w + cell_w / 2}" y="{top - 6}" text-anchor="middle">lead {lead}</text>')
    for i, name in enumerate(names):
        y = top + i * cell_h
        out.append(f'<text x="{left - 6}" y="{y + cell_h - 4}" text-anchor="end">{name}</text>')
        for j, lead in enumerate(LEADS):
            rho = result["series"][name]["leads"][str(lead)]["all"]["pressure"]["rho"]
            if rho is None:
                continue
            colour = "#c0392b" if rho > 0 else "#1f6fb2"
            out.append(
                f'<rect class="c" x="{left + j * cell_w}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{colour}" '
                f'fill-opacity="{min(1.0, abs(rho) / 0.5):.2f}"><title>{name}, lead {lead}: {rho:+.3f}</title></rect>'
            )
            if abs(rho) >= 0.15:
                out.append(
                    f'<text x="{left + j * cell_w + cell_w / 2}" y="{y + cell_h - 4}" text-anchor="middle">{rho:+.2f}</text>'
                )
    legend_y = top + cell_h * len(names) + 18
    out.append(f'<text x="4" y="{legend_y}">red: a higher series goes with more pressure; blue: the reverse; full colour at |rho| = 0.5; '
               f'values shown from 0.15</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    result = json.loads(args.screen.read_text(encoding="utf-8"))
    if args.tables:
        args.tables.write_text(tables_markdown(result), encoding="utf-8")
    if args.heatmap:
        args.heatmap.write_text(heatmap_svg(result), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    panel = sub.add_parser("panel")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--extra", type=Path, nargs="*", default=[])
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(func=panel_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    report = sub.add_parser("report")
    report.add_argument("screen", type=Path)
    report.add_argument("--tables", type=Path)
    report.add_argument("--heatmap", type=Path)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
