"""gbm_funding fit on SOFR's distance from the ON RRP rate, mapped back to SOFR - IORB (#948, H5 step 3): arm, walk, scoring and report.

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths
it is given and nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no
published figure. Every choice is in `metadata/onrrp_distance_948.json`, which this script refuses to read unless it is committed and
unchanged. No day after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

`gbm_funding` is fit on SOFR - IORB in bp. The IORB - ON RRP width stepped over the sample (25, 20, 15, 10, then 15 bp), so that target
carries the steps as level shifts. The arm `gbm_funding_onrrp` is fit on z(t) = SOFR(t) - ON RRP(t) = spread_bps(t) + W(t) and its
quantiles are mapped back to SOFR - IORB: q_y = q_z - W(t, D), W(t, D) being the width of the register entries announced at or before the
decision instant D and effective on or before the target day t. Both rates are read from `metadata/policy_events.json`, announcement-dated
(`policy_events.require_announced`), never FRED's realised `RRPONTSYAWARD`. The ON RRP rate is here only a re-expression of the target,
never a regressor and never a series this repository models: the ON RRP rate as a liquidity input is repo-market-liquidity's (#643).

At lead 1 `treasury_settlement` is trained from the target's own row (`aligned_pairs_931.align_field`, #931 having merged); at the other
leads the field is not an input and the pairs are gbm_funding's one-step pairs.

Walk-forward refits are long (about an hour for the eleven walks on four cores).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/onrrp_distance_948.py walk --horizon $h --published PUB.csv \\
            --output OUT/gbm_funding_onrrp_h$h.json
    OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_pairs_931.py walk --published PUB.csv \\
        --output OUT/gbm_funding_aligned_h1.json
    PYTHONPATH=src python3 scripts/onrrp_distance_948.py score --published PUB.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/onrrp_distance_948.py report OUT/score.json --output OUT/report.md
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, policy_events, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "onrrp_distance_948.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
RECORDED_449 = REPO / "docs" / "research" / "direct-twin-449" / "score.json"
RECORDED_931 = REPO / "docs" / "research" / "aligned-pairs-931" / "score.json"
LAST_TARGET = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
SEED = 948
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 2_000
MINIMUM_DAYS = 30
HORIZONS = sp.HORIZONS
GRID = sp.GRID
CONTROL = "gbm_funding"
ARM = "gbm_funding_onrrp"
ALIGNED = "gbm_funding_aligned"
MODELS = (CONTROL, ARM)
PAIRS = [("B1", CONTROL), ("B2", CONTROL), ("B1", ARM), ("B2", ARM), (CONTROL, ARM)]
ALIGNED_PAIR = (ALIGNED, ARM)
SCENARIOS = ("all days", "without 2019-09-18")
#: a tolerance for the reproduction of the recorded means: the walks are deterministic, so this is rounding only
REPRODUCTION_TOLERANCE = 1e-6
#: the register's key for the rate of each kind, in percent
RATE_KEY = {"iorb_rate": "rate_percent", "on_rrp": "offering_rate_percent"}
#: the IORB - ON RRP width eras of the sample, as the declaration describes them
WIDTH_ERAS = (
    ("25 bp", date(2018, 4, 3), date(2018, 6, 13)),
    ("20 bp", date(2018, 6, 14), date(2018, 12, 19)),
    ("15 bp (2018-12 to 2019-04)", date(2018, 12, 20), date(2019, 5, 1)),
    ("10 bp", date(2019, 5, 2), date(2024, 12, 18)),
    ("15 bp (2024-12 on)", date(2024, 12, 19), LAST_TARGET),
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the declaration and the guards ---------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"onrrp_distance_948 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the rates and the target ---------------------------------------------------------------------------------------


def end_of_day(day: date) -> datetime:
    """The last second of `day`, America/New_York wall clock: when everything announced on it is public."""

    return datetime.combine(day, policy_events.END_OF_DAY)


def rate_in_force(
    register: Sequence[policy_events.PolicyEntry], kind: str, target_day: date, as_of: datetime
) -> policy_events.PolicyEntry:
    """The entry of `kind` in force on `target_day` among those announced at or before `as_of`.

    Entries announced after `as_of` are not candidates, and the entry chosen is checked by `policy_events.require_announced`, which
    raises `LookAheadError`. The latest by effective date, then announcement, wins. No entry in force is a `ValueError`.
    """

    known = policy_events.known_entries(register, as_of)
    pool = [e for e in known if e.kind == kind and e.effective is not None and e.effective <= target_day]
    if not pool:
        raise ValueError(f"no {kind} entry is in force on {target_day} among those announced by {as_of}")
    return policy_events.require_announced(max(pool, key=lambda e: (e.effective, e.announced_at)), as_of)


def rate_percent(register: Sequence[policy_events.PolicyEntry], kind: str, target_day: date, as_of: datetime) -> float:
    """The rate, in percent, of the entry of `kind` in force on `target_day` as announced by `as_of`. A malformed entry is a `ValueError`."""

    entry = rate_in_force(register, kind, target_day, as_of)
    value = entry.details.get(RATE_KEY[kind])
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"policy entry {entry.id} carries no numeric {RATE_KEY[kind]}")
    return float(value)


def width_bp(register: Sequence[policy_events.PolicyEntry], target_day: date, as_of: datetime) -> float:
    """IORB - ON RRP in force on `target_day`, in bp, from the entries announced at or before `as_of`."""

    iorb = rate_percent(register, "iorb_rate", target_day, as_of)
    on_rrp = rate_percent(register, "on_rrp", target_day, as_of)
    return round(100.0 * (iorb - on_rrp), 6)


@dataclass(frozen=True)
class DistanceObservation(DailyObservation):
    """A row whose `spread_bps` is SOFR's distance from the ON RRP rate: the spread plus the width in force on the day."""

    shift_bps: float = 0.0

    @property
    def spread_bps(self) -> float:
        return super().spread_bps + self.shift_bps


def distance_frame(frame: Sequence[DailyObservation], register: Sequence[policy_events.PolicyEntry]) -> List[DailyObservation]:
    """`frame` with every row's target re-expressed as SOFR - ON RRP; dates and every value are the frame's own.

    The width of a training row is the one in force on its own day as announced by the end of that day: a training target is a
    realised day, and no entry announced after it is read.
    """

    return [
        DistanceObservation(row.date, row.values, width_bp(register, row.date, end_of_day(row.date))) for row in frame
    ]


def check_panel_iorb(rows: Sequence[DailyObservation], register: Sequence[policy_events.PolicyEntry]) -> None:
    """The panel's `iorb` is the register's IORB on every row: otherwise SOFR - ON RRP - W is not SOFR - IORB. Raises `ValueError`."""

    for row in rows:
        stated = row.values.get("iorb")
        expected = rate_percent(register, "iorb_rate", row.date, end_of_day(row.date))
        if stated is None or abs(100.0 * (float(stated) - expected)) > 0.01:
            raise ValueError(f"{row.date}: the panel's iorb {stated} is not the register's {expected}")


def map_back(quantiles: Optional[Sequence[float]], width: float) -> Optional[List[float]]:
    """The fitted quantiles of the distance, shifted by the as-of width into SOFR - IORB; a missing law stays missing."""

    return None if quantiles is None else [float(value) - width for value in quantiles]


# -- the arm --------------------------------------------------------------------------------------------------------


class DistanceModel:
    """A fitted model that reads and forecasts the distance: the feature row it is served is re-expressed like its training rows.

    `ml.fit_gradient_boosted_quantiles` takes the last observed spread as an input beside the regressors, so a fit on the distance
    target must be served the last observed distance, SOFR - ON RRP on the anchor day, and not the spread. The rate is the one in force
    on the anchor day. Everything else is the wrapped fit's own.
    """

    def __init__(self, fitted, register: Sequence[policy_events.PolicyEntry]):
        self._fitted = fitted
        self._register = register

    def __getattr__(self, name: str):
        return getattr(self._fitted, name)

    def predict(self, feature_row: DailyObservation):
        return self._fitted.predict(distance_frame([feature_row], self._register)[0])

    def with_history(self, history: Sequence[DailyObservation]) -> "DistanceModel":
        return DistanceModel(self._fitted.with_history(distance_frame(history, self._register)), self._register)


def regressors(features: Sequence[str]) -> Tuple[str, ...]:
    return tuple(name for name in features if name != "spread_bps")


def aligns(features: Sequence[str]) -> bool:
    """Whether the lead's features read the settlement field, so that its training row is the target's own (#931)."""

    return _load("aligned_pairs_931").FIELD in regressors(features)


def training_frame(
    frame: Sequence[DailyObservation], register: Sequence[policy_events.PolicyEntry], align: bool
) -> List[DailyObservation]:
    rows = _load("aligned_pairs_931").align_field(frame) if align else list(frame)
    return distance_frame(rows, register)


def arm_fit(features: Sequence[str], register: Sequence[policy_events.PolicyEntry]):
    """`gbm_funding`'s fit on the distance target (and, where the field is an input, the aligned settlement); nothing else changed."""

    names = regressors(features)
    align = aligns(features)

    def fit(train_frame, minimum_history):
        return DistanceModel(
            ml.fit_gradient_boosted_quantiles(
                training_frame(train_frame, register, align), regressors=names, levels=GRID, minimum_history=minimum_history
            ),
            register,
        )

    return fit


# -- the walk -------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    h = args.horizon
    if h not in sd.HORIZONS:
        raise SystemExit(f"horizon {h} is not a protocol lead")
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="onrrp_distance_948")
    if sd.finished_walk(args.output, variant=ARM, horizon=h, published=args.published, panel=args.published):
        print(json.dumps({"variant": ARM, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in published if row.date <= LAST_TARGET]
    register = policy_events.load_register()
    check_panel_iorb(rows, register)
    features = tuple(sd._load("live_record").published_features(h))
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    result, levels, settings = sd.walk(
        rows, fit=arm_fit(features, register), features=features, online_calibration=None, registry=registry,
        horizon=h, minimum_history=61, refit_every=21, expected_levels=GRID,
    )
    dates = [row.date for row in rows]
    rule = InformationRule(registry, features, decision_time=sd.DECISION, horizon=h)
    laws, distance, widths = {}, {}, {}
    for index, quantiles in result:
        day = dates[index].isoformat()
        width = width_bp(register, dates[index], rule.decision_instant(dates, index))
        distance[day], widths[day], laws[day] = quantiles, width, map_back(quantiles, width)
    document = {
        "variant": ARM,
        "horizon": h,
        "levels": levels,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": None,
        "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)),
        "aligned_settlement": aligns(features),
        "widths_bp": widths,
        "laws_distance": distance,
        "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": ARM, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- scoring --------------------------------------------------------------------------------------------------------


def _summarise(test) -> dict:
    skill_lower = test.skill - sp._bound(test.skill_t_draws, 1.0 - test.alpha, test.draws) * test.skill_standard_error
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "mean_difference": test.mean_difference,
        "skill": test.skill,
        "mean_difference_lower_95_one_sided": test.lower_mean_difference(),
        "skill_lower_95_one_sided": skill_lower,
        "skill_upper_95_one_sided": test.upper_skill(),
        "bootstrap_p": test.p_value,
        "dm_statistic": test.dm_statistic,
        "dm_p": test.dm_p_value,
    }


def _paired_job(job):
    """One `paired_tests` call in a worker: `(key, [(benchmark series, candidate series)], draws)` to `(key, rows)`."""

    key, chosen, draws = job
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return key, [_summarise(test) for test in tests]


def settings_of(document: Mapping) -> Mapping:
    """A walk's recorded fit settings. `spread_distribution_634.py walk` writes them with `default=str`, so a mapping
    proxy is stored as the text of its dict; both forms are read."""

    settings = document.get("settings", {})
    if isinstance(settings, str):
        settings = ast.literal_eval(settings)
    if not isinstance(settings, Mapping):
        raise ValueError(f"the walk's settings are not a mapping: {settings!r}")
    return settings


def without_excluded(days: Sequence[date]) -> List[date]:
    return [day for day in days if day != EXCLUDED_DAY]


def check_walks(directory: Path, published: Path) -> Dict[str, Dict[str, str]]:
    """Each walk's recorded pairing and panel, read from its own file: both on the published panel, none on direct pairs."""

    digest = panel_sha256(published)
    out: Dict[str, Dict[str, str]] = {}
    for name in MODELS:
        out[name] = {}
        for h in HORIZONS:
            document = json.loads((directory / f"{name}_h{h}.json").read_text(encoding="utf-8"))
            if document["panel_sha256"] != digest or document["variant"] != name or document["horizon"] != h:
                raise ValueError(f"{name}_h{h}.json is not the walk of {name} at lead {h} on this panel")
            pairing = settings_of(document).get("training_pairs", "unset (one-step)")
            if pairing != "unset (one-step)":
                raise ValueError(f"{name} lead {h} names training_pairs {pairing!r}; the pairs must be one-step")
            out[name][str(h)] = pairing
    for h in HORIZONS:
        control = json.loads((directory / f"{CONTROL}_h{h}.json").read_text(encoding="utf-8"))
        arm = json.loads((directory / f"{ARM}_h{h}.json").read_text(encoding="utf-8"))
        if control["features"] != arm["features"]:
            raise ValueError(f"lead {h}: the control and the arm read different features")
        if arm.get("aligned_settlement") != (h == 1):
            raise ValueError(f"lead {h}: the arm's settlement alignment is {arm.get('aligned_settlement')}")
        mapped = {day: map_back(q, arm["widths_bp"][day]) for day, q in arm["laws_distance"].items()}
        if mapped != arm["laws"]:
            raise ValueError(f"lead {h}: the arm's laws are not its distance laws less the recorded width")
    return out


def width_of(decision_day: date) -> Optional[str]:
    for label, first, last in WIDTH_ERAS:
        if first <= decision_day <= last:
            return label
    return None


def score_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="onrrp_distance_948")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    register = policy_events.load_register()
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    recorded = json.loads(RECORDED_449.read_text(encoding="utf-8"))
    pairing = check_walks(args.walks, args.published)
    walks = {name: sd.load_laws(args.walks, name) for name in MODELS}
    # #449's decision days, so that the figures here are those of #449 for the same days
    first = date.fromisoformat(recorded["decision_days"]["first"])
    last = date.fromisoformat(recorded["decision_days"]["last"])
    unbuilt = {date.fromisoformat(day) for day, _ in recorded["decision_days_without_a_benchmark"]}
    decisions, days_by_name = {}, {}
    for name, laws in walks.items():
        decisions[name], days_by_name[name] = sd.lead_forecasts(laws, calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by_name.values())))
    common = [d for d in common if first <= d <= last and d not in unbuilt and all(calendar[position[d] + h] <= LAST_TARGET for h in HORIZONS)]
    if len(common) != recorded["decision_days"]["n"]:
        raise ValueError(f"the decision-day set has {len(common)} days, #449's score has {recorded['decision_days']['n']}")
    sd.refuse_locked(common + [calendar[position[d] + h] for d in common for h in HORIZONS])
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=sd.DECISION, splits=splits)
    forecasts = {"B1": b1, "B2": b2}
    missing = {}
    for name in MODELS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = ["B1", "B2", *MODELS]
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    cells = {n: sd.cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in names}
    # the aligned control, lead 1 only (#931's walk), to separate the transform from the alignment
    aligned_laws = _load("aligned_pairs_931").load_walk(args.walks, ALIGNED, args.published)
    aligned_absent, cells[ALIGNED] = 0, {}
    for d in common:
        target = calendar[position[d] + 1]
        law = aligned_laws.get(target)
        if law is None:
            aligned_absent += 1
            law = b1[d][1]
        cells[ALIGNED][(d, 1)] = sp.grid_crps(law, outcomes[target])
    missing[ALIGNED] = {"days": aligned_absent, "share": aligned_absent / len(common)}

    # the reproductions: the control's and the benchmarks' means at every lead against #449's score, the aligned control against #931's
    reproduced = {}
    for h in HORIZONS:
        recorded_means = recorded["tables"]["all days"]["all"]["all"][str(h)]["mean"]
        here = {
            n: sum(v for (d, hh), v in cells[n].items() if hh == h) / len(common) for n in ("B1", "B2", CONTROL)
        }
        reproduced[str(h)] = {n: {"recomputed": here[n], "recorded_449": recorded_means[n]} for n in here}
        for n in here:
            if abs(here[n] - recorded_means[n]) > REPRODUCTION_TOLERANCE:
                raise ValueError(f"lead {h}: {n}'s mean grid CRPS is {here[n]} here and {recorded_means[n]} in #449's score")
    recorded_931 = json.loads(RECORDED_931.read_text(encoding="utf-8"))
    aligned_here = sum(cells[ALIGNED].values()) / len(common)
    aligned_recorded = recorded_931["tables"]["all days"]["all"]["all"]["mean"][ALIGNED]
    reproduced["aligned_lead_1"] = {"recomputed": aligned_here, "recorded_931": aligned_recorded}
    if abs(aligned_here - aligned_recorded) > REPRODUCTION_TOLERANCE:
        raise ValueError(f"{ALIGNED}'s mean at lead 1 is {aligned_here} here and {aligned_recorded} in #931's score")

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    kinds = sorted({kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS})
    all_names = [*names, ALIGNED]

    def series(group: Sequence[date], lead: Optional[int], kind: Optional[str]) -> Dict[str, Dict[date, float]]:
        keep = set(group)
        include = lambda d, h: d in keep and (lead is None or h == lead) and (kind is None or kind_of(calendar[position[d] + h]) == kind)  # noqa: E731
        chosen = all_names if lead == 1 else names
        return {n: sd.day_means(cells[n], include) for n in chosen}

    jobs, shells = [], {}

    def add(key, group, lead, kind, headline):
        means = series(group, lead, kind)
        common_days = sorted(set.intersection(*(set(m) for m in means.values())) & set(group))
        pairs = PAIRS + ([ALIGNED_PAIR] if lead == 1 else [])
        entry = {"n": len(common_days), "mean": {n: sum(means[n][d] for d in common_days) / len(common_days) for n in means} if common_days else {}}
        if len(common_days) < MINIMUM_DAYS or len(common_days) <= sp.HAC_LAG:
            entry["thin"] = True
        else:
            jobs.append((key, [({d: means[b][d] for d in common_days}, {d: means[c][d] for d in common_days}) for b, c in pairs],
                         HEADLINE_DRAWS if headline else SPLIT_DRAWS))
            entry["pairs"] = [f"{b} -> {c}" for b, c in pairs]
        shells[key] = entry

    for scenario in SCENARIOS:
        scored = days if scenario == SCENARIOS[0] else without_excluded(days)
        groups = {"all": scored}
        for label in splits.regime_labels:
            groups[f"regime {label}"] = [d for d in scored if splits.regime(d) == label]
        for label, _first, _last in WIDTH_ERAS:
            groups[f"width {label}"] = [d for d in scored if width_of(d) == label]
        for group_name, group in groups.items():
            for kind in (None, *kinds):
                for lead in (None, *HORIZONS):
                    # the cross of a regime (or width era) and a day type is not a declared table; the width eras are described
                    # at the pooled figure and at lead 1 only
                    if group_name != "all" and kind is not None:
                        continue
                    if group_name.startswith("width ") and lead not in (None, 1):
                        continue
                    add((scenario, group_name, kind or "all", lead or "pooled"), group, lead, kind, group_name == "all" and kind is None)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, results in pool.map(_paired_job, jobs):
            shells[key]["tests"] = dict(zip(shells[key]["pairs"], results))
    tables: Dict[str, dict] = {}
    for (scenario, group, kind, lead), entry in shells.items():
        entry.pop("pairs", None)
        tables.setdefault(scenario, {}).setdefault(group, {}).setdefault(kind, {})[str(lead)] = entry
    document = {
        "declaration": "metadata/onrrp_distance_948.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "seed": SEED,
        "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS},
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "excluded_day_scores": {n: primary[n].get(EXCLUDED_DAY) for n in names},
        "missing": missing,
        "pairing": pairing,
        "pairs_used": {"1": "treasury_settlement aligned to the target's own row (#931), every other field one-step", "2 to 5": "one-step"},
        "reproduction": reproduced,
        "names": names,
        "kinds": kinds,
        "regimes": list(splits.regime_labels),
        "width_eras": [label for label, _first, _last in WIDTH_ERAS],
        "tables": tables,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report -----------------------------------------------------------------------------------------------------


def fmt(value: Optional[float], digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def pair_cell(entry: dict, pair: str) -> str:
    if entry.get("thin"):
        return "too thin"
    row = entry["tests"].get(pair)
    if row is None:
        return "n/a"
    return f"{100 * row['skill']:+.1f}% [{100 * row['skill_lower_95_one_sided']:+.1f}, {100 * row['skill_upper_95_one_sided']:+.1f}]"


def table(title: str, scenario_tables: Mapping[str, dict], group: str, kind: str, leads: Sequence[str]) -> List[str]:
    if group not in scenario_tables or not any(scenario_tables[group][kind].get(lead, {}).get("mean") for lead in leads):
        return []
    lines = [f"### {title}", "", "| lead | days | B1 | B2 | gbm | arm | gbm vs B1 | arm vs B1 | gbm vs B2 | arm vs B2 | arm vs gbm |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for lead in leads:
        entry = scenario_tables[group][kind].get(lead)
        if not entry or not entry["mean"]:
            continue
        mean = entry["mean"]
        lines.append(
            f"| {lead} | {entry['n']} | " + " | ".join(fmt(mean[n], 2) for n in ("B1", "B2", CONTROL, ARM)) + " | "
            + " | ".join(pair_cell(entry, f"{b} -> {c}") for b, c in (("B1", CONTROL), ("B1", ARM), ("B2", CONTROL), ("B2", ARM), (CONTROL, ARM)))
            + " |"
        )
    return lines + [""]


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    leads = ["pooled", *map(str, HORIZONS)]
    out = [
        "# gbm_funding fit on SOFR's distance from the ON RRP rate (#948, H5 step 3)",
        "",
        "**Development data, not a verdict.** A measurement under scoring protocol v1: nothing is published or registered; the declared candidate,",
        "the published model and every published figure are as they were. Whether the candidate changes is Eleonora's. Declaration:",
        "`metadata/onrrp_distance_948.json`.",
        "",
        f"Decision days {score['decision_days']['first']} to {score['decision_days']['last']} ({score['decision_days']['n']}). Panel `{score['panel_sha256'][:12]}…`.",
        "Grid CRPS in bp (lower is better). A skill cell is the skill of the second forecast over the first named (positive favours the second), with the one-sided",
        "95% lower and upper bounds of skill from the studentized stationary bootstrap, as `[lower, upper]` (block 10, seed 948; "
        f"{score['draws']['headline']:,} draws on pooled and per-lead figures, {score['draws']['splits']:,} on splits). No day after 2025-12-31 and no locked day is scored.",
        "",
        "## The arm",
        "",
        "`gbm` is the declared `gbm_funding`, fit on SOFR - IORB. `arm` (`gbm_funding_onrrp`) is the same fit on SOFR - ON RRP, with its quantiles mapped back to",
        "SOFR - IORB by the width IORB - ON RRP known at the decision instant. The width stepped over the sample: "
        + ", ".join(score["width_eras"]) + " (in that order). Both rates are read from the policy register, announcement-dated, never FRED's realised `RRPONTSYAWARD`.",
        "The ON RRP rate here only re-expresses the target; as a liquidity input it is repo-market-liquidity's (#643).",
        "",
        "**Training pairs used (the ruling asks to say which).** "
        + "; ".join(f"lead {lead}: {text}" for lead, text in score["pairs_used"].items())
        + ". `gbm` (the control) stays on one-step pairs, as declared. Lead 1 therefore also pairs the arm against `gbm_funding_aligned` (#931's arm, re-walked), which "
        "separates the transform from the alignment.",
        "",
        "**Amendment 1 (declared after a first scoring pass, named as such).** The first pass trained the fit on the distance but served it the plain last spread, an input the fit takes beside "
        "the regressors; that pass scored the arm at -92.7% against `gbm` and is discarded. The served row now carries the last observed distance, as the training rows do; a constant shift of "
        "the target leaves the mapped-back predictions unchanged. The figures on this page are from the walks after the amendment.",
        "",
        "The walks' own settings name no `training_pairs` for either model at any lead. The control reproduces #449's recorded mean grid CRPS of `gbm_funding`, B1 and B2 at "
        "every lead to the digit, and `gbm_funding_aligned` reproduces #931's at lead 1; the score refuses to run otherwise.",
        "",
        "| lead | gbm (recorded in #449) | gbm (here) |",
        "|---|---|---|",
    ]
    for lead in map(str, HORIZONS):
        row = score["reproduction"][lead][CONTROL]
        out.append(f"| {lead} | {fmt(row['recorded_449'], 6)} | {fmt(row['recomputed'], 6)} |")
    row = score["reproduction"]["aligned_lead_1"]
    out += [
        "",
        f"`gbm_funding_aligned` at lead 1: {fmt(row['recorded_931'], 6)} recorded in #931, {fmt(row['recomputed'], 6)} here.",
        "",
        f"Missing laws (the day takes B1's law): " + ", ".join(f"{n} {v['days']} ({100 * v['share']:.1f}%)" for n, v in score["missing"].items()) + ".",
        "",
        f"Decision day {score['excluded_day']} scores (grid CRPS, mean over its five leads): "
        + ", ".join(f"{n} {fmt(v, 1)}" for n, v in score["excluded_day_scores"].items() if v is not None)
        + ".",
        "",
        "## The arm against the control, in one place",
        "",
    ]
    for scenario in SCENARIOS:
        pooled = score["tables"][scenario]["all"]["all"]
        row = pooled["pooled"]["tests"][f"{CONTROL} -> {ARM}"]
        by_lead = {lead: pooled[lead]["tests"][f"{CONTROL} -> {ARM}"] for lead in map(str, HORIZONS)}
        worse = [lead for lead, r in by_lead.items() if r["skill_upper_95_one_sided"] < 0]
        ahead = [lead for lead, r in by_lead.items() if r["skill_lower_95_one_sided"] > 0]
        out.append(
            f"- {scenario}: pooled over leads the arm's skill over the control is {100 * row['skill']:+.1f}% "
            f"[{100 * row['skill_lower_95_one_sided']:+.1f}, {100 * row['skill_upper_95_one_sided']:+.1f}] "
            f"(mean grid CRPS {fmt(row['benchmark_mean'], 3)} bp for the control); leads where the whole interval is below zero (arm worse): "
            f"{', '.join(worse) or 'none'}; leads where it is above zero (arm ahead on these development days): {', '.join(ahead) or 'none'}."
        )
    lead_one = score["tables"][SCENARIOS[0]]["all"]["all"]["1"]
    out += [
        f"- Lead 1, the arm over `gbm_funding_aligned` (the transform alone): "
        + pair_cell(lead_one, f"{ALIGNED} -> {ARM}")
        + f"; mean grid CRPS {fmt(lead_one['mean'][ALIGNED], 3)} bp for the aligned control, {fmt(lead_one['mean'][ARM], 3)} bp for the arm.",
        "",
    ]
    for scenario in SCENARIOS:
        tables = score["tables"][scenario]
        out += [f"## {scenario}", ""]
        out += table("Pooled over leads and each lead alone", tables, "all", "all", leads)
        for kind in score["kinds"]:
            out += table(f"Target-day type: {kind}", tables, "all", kind, leads)
        for label in score["regimes"]:
            out += table(f"Regime of the decision day: {label}", tables, f"regime {label}", "all", leads)
        for label in score["width_eras"]:
            out += table(f"Width era of the decision day: {label} (described, not a declared split)", tables, f"width {label}", "all", ["pooled", "1"])
    out += [
        "## Marked question for Eleonora (this PR settles nothing)",
        "",
        "Does the declared candidate switch to the ON RRP distance fit? The measurement above is development evidence, not a verdict, and changes no published model,",
        "declaration or figure. Adopting it would also change what the published model's quantiles are relative to: that is a candidate change and hers to decide.",
        "",
    ]
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="walk the arm at one lead")
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    score = sub.add_parser("score", help="score the arm and the control against B1 and B2 and each other")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    report = sub.add_parser("report", help="render the Markdown page")
    report.add_argument("score", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
