"""The 15 October tax-date column on the two calendar-aware #1027 variants: two declared arms (#1095, finding #1004; H5 step 3, calendar first).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers no result and changes no rule, no published model, no published declaration and no published figure: `tax_date`, B2 and
every existing declaration stay as they are, and adopting the label is Eleonora's (a data meaning, #1004). Every choice is in
`metadata/october_tax_1004.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from the constants below
and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**Why.** #979 tested the 15 October label only in B2 and the H8 ranker, on the days that prompted it (2019-10-15, 16 and 17; 2025-10-15 and 16), and no learned
model ever read it. Eleonora's ruling on #1004 (20 October 2026, corrected): deferred, not rejected; tested again with a candidate that reads calendar days at
the target day, and only on a reading that leaves out the 2019 and 2025 October days, or on 2026 development days.

**The arms.** Each arm is a #1027 variant (`scripts/aligned_calendar_1027.py`) with the column `tax_date_october` (`repo_model.tax_date_october.add_columns`: the 15th
of October rolled off weekends and DC holidays, as `data.corporate_tax_deadline` rolls, and the two market days after it) added as a regressor at every lead
h = 1..5. The variant's other inputs, leaf, seed, quantile grid, refit cadence and pairing are the variant's, so an arm differs from its variant by one column.

* `gbm_funding_cal_direct_october`: `gbm_funding_cal_direct` plus the column, on direct pairs (`training_pairs="direct"`).
* `gbm_funding_cal_aligned_october`: `gbm_funding_cal_aligned` plus the column, on one-step pairs of the aligned frame. The #947 guard refuses it: the allow-list
  entries of #1027 cover that variant's regressors only, and a new entry is hers (CLAUDE.md). `walk` refuses it (a non-zero exit) and writes nothing until she
  admits it; `score` then reports it as not run.

**Read at the target day.** The column is a function of the row's own date and the market holiday table. It is served to the model as a calendar column for
this run only (`switched`: `contract.CALENDAR_FEATURES` and `asof.CALENDAR_FEATURES` gain it), so `asof` rule 2 reads it from the scored row at every lead, and a
direct pair trains it from the pair's own target row; the aligned arm moves it up one row with the other target-row columns (`align_columns`, then `require_aligned`
before every fit). It is declared in `repo_model.target_day_columns`, so `repo_model.one_step_guard` refuses it on any one-step fit that is not admitted.

**What is scored** (all paired, studentized stationary bootstrap, seed 1095, development days to 2025-12-31 only): grid CRPS and upper-tail twCRPS of each arm over its
variant without the column, over B1, over B2 and over `gbm_funding`; and, on the days the published distribution (B3) has all five leads, the five-level CRPS of each arm
and variant over B3 (the secondary comparison of the protocol). Pooled, by regime, by the target day's reporting day type, and on the October cuts: the window in all
years, the window with 2019 and 2025 left out, and ordinary days outside the window. The 2026 development days (2026-01-01 to 2026-09-03) hold no October window;
`reading_2026` reports that, and no day after 2025-12-31 is scored.

    # PUB.csv, AUG3.csv and the walks of gbm_funding and gbm_funding_cal_direct: ~/rmm-1027 on the Mac (#1027's paste builds them)
    PYTHONPATH=src python3 scripts/october_tax_1004.py declare            # then commit metadata/october_tax_1004.json before any score
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/october_tax_1004.py walk --arm gbm_funding_cal_direct_october --horizon $h \\
            --published PUB.csv --panel AUG3.csv --output WALKS/gbm_funding_cal_direct_october_h$h.json
    PYTHONPATH=src python3 scripts/october_tax_1004.py score --published PUB.csv --panel AUG3.csv --walks WALKS --reference-walks REF \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import asof, contract, ml, one_step_guard, protocol_benchmarks as pb, scoring_protocol as sp, tax_date_october as tdo  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

ac = _load("aligned_calendar_1027")

DECLARATION = REPO / "metadata" / "october_tax_1004.json"
LAST_TARGET = ac.LAST_TARGET
SEED = 1095
HORIZONS = ac.HORIZONS
GRID = ac.GRID
COLUMN = tdo.COLUMN

CONTROL = ac.CONTROL
DIRECT_OCTOBER = "gbm_funding_cal_direct_october"
ALIGNED_OCTOBER = "gbm_funding_cal_aligned_october"
ARMS = (DIRECT_OCTOBER, ALIGNED_OCTOBER)
#: each arm's #1027 variant, the one it is scored against besides the benchmarks and the control
BASE = {DIRECT_OCTOBER: ac.DIRECT, ALIGNED_OCTOBER: ac.ALIGNED}
BENCHMARKS = ("B1", "B2")
METRICS = ac.METRICS
#: the secondary comparison against B3 (the published distribution): the grid CRPS on its own five levels, which has no tail-weighted form
B3_METRIC = "grid_crps_b3_levels"
B3_TITLE = "Grid CRPS on B3's five levels (the published distribution, protocol secondary comparison)"
ORDER_REGIME = ac.ORDER_REGIME
MIN_GROUP_DAYS = ac.MIN_GROUP_DAYS
#: the named October cuts are the point of the study and are scored from this many target days (listed with their day counts; the intervals on so few days are weak)
NAMED_CUT_MIN_DAYS = 10
#: the years whose October days prompted the label (#979, finding #1004): the reading that leaves them out is the one the ruling asks for
LEFT_OUT_YEARS = (2019, 2025)
#: the overlapping October cuts of target days, beside the five exclusive target day types of #1027
CUTS = ("october_window", "october_without_2019_2025", "ordinary_outside_october")
CUT_TITLES = {
    "october_window": "the October window, every year (the 15th rolled, and the two market days after it)",
    "october_without_2019_2025": "the October window with 2019 and 2025 left out",
    "ordinary_outside_october": "ordinary days outside the October window",
}
#: the 2026 development days the lockbox leaves open: the near-blind tier, opened on 2026-10-05 (docs/decisions/lockbox.md, #151)
OPEN_2026 = (date(2026, 1, 1), date(2026, 9, 3))


# -- the arms --------------------------------------------------------------------------------------------------------


def arm_features(arm: str, horizon: int) -> Tuple[str, ...]:
    """The arm's inputs at a lead: its #1027 variant's, then the October column (none twice)."""

    if arm not in ARMS:
        raise ValueError(f"{arm!r} is not a declared arm")
    base = ac.variant_features(BASE[arm], horizon)
    return base + tuple(c for c in (COLUMN,) if c not in base)


def arm_fit(arm: str, features: Sequence[str]):
    """The arm's fitter: its variant's (the gbm at the declared leaf), on direct pairs or on the aligned frame, with the October column among the regressors."""

    names = ac.regressors(features)
    if arm == DIRECT_OCTOBER:
        return functools.partial(ml.fit_gradient_boosted_quantiles, regressors=names, levels=GRID, min_samples_leaf=ac.LEAF, training_pairs="direct")
    if arm != ALIGNED_OCTOBER:
        raise ValueError(f"{arm!r} is not a declared arm")
    fields = ac.TARGET_ROW_COLUMNS + (COLUMN,)

    def fit(train_frame, minimum_history):
        aligned = ac.align_columns(train_frame, fields)
        ac.require_aligned(train_frame, aligned, fields)
        return ml.fit_gradient_boosted_quantiles(
            aligned, regressors=names, levels=GRID, minimum_history=minimum_history, min_samples_leaf=ac.LEAF
        )

    return fit


def require_admitted(arm: str, horizon: int) -> None:
    """Refuse, with a non-zero exit, before any work when the #947 guard would refuse the arm's fit (adding an allow-list entry is Eleonora's decision)."""

    if arm != ALIGNED_OCTOBER:
        return
    try:
        one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", ac.regressors(arm_features(arm, horizon)))
    except ValueError as error:
        raise SystemExit(
            f"{arm} lead {horizon}: not run. repo_model.one_step_guard (#947) refuses it, and a new allow-list entry is Eleonora's decision "
            f"(CLAUDE.md); nothing is written. {error}"
        ) from None


@contextlib.contextmanager
def switched() -> Iterator[None]:
    """The October column as a calendar column, for this run only: a function of the date, known in advance, so `asof` rule 2 reads it from the scored row at every lead."""

    calendar = contract.CALENDAR_FEATURES | frozenset((COLUMN,))
    with mock.patch.object(contract, "CALENDAR_FEATURES", calendar), mock.patch.object(asof, "CALENDAR_FEATURES", calendar):
        yield


# -- the October cuts and the 2026 reading ----------------------------------------------------------------------------------


def october_cuts(targets: Sequence[date], types: Optional[Mapping[date, str]] = None) -> Dict[str, List[date]]:
    """The overlapping October cuts of `targets`: the window in every year, the window without 2019 and 2025, and (given each day's #1027 type) ordinary days outside it.

    Labels for scoring only, from the date and the market holiday table: never an input.
    """

    out: Dict[str, List[date]] = {name: [] for name in CUTS}
    for day in sorted(targets):
        window = tdo.october_window(day)
        if window:
            out["october_window"].append(day)
            if day.year not in LEFT_OUT_YEARS:
                out["october_without_2019_2025"].append(day)
        elif types is not None and types[day] == "ordinary":
            out["ordinary_outside_october"].append(day)
    return out


def reading_2026(targets: Sequence[date]) -> dict:
    """What the 2026 development days (the opened near-blind tier) can say about an October label: nothing on this panel, and why.

    The panel ends on 2026-09-03 and the October 2026 window (15, 16 and 19 October) is after it, in the blind tier, which no comparison may score. The study window
    is #1027's, 2025-12-31, so no 2026 day is scored either; extending it would need new walks of the control and of the variant and is Eleonora's question.
    """

    open_days = [d for d in targets if OPEN_2026[0] <= d <= OPEN_2026[1]]
    return {
        "open_2026_days": [OPEN_2026[0].isoformat(), OPEN_2026[1].isoformat()],
        "scored_open_2026_days": len(open_days),
        "october_window_days": sum(1 for d in open_days if tdo.october_window(d)),
        "october_2026_window": [d.isoformat() for d in tdo._window_after(tdo.october_deadline(2026))],
        "why": (
            "the October 2026 window falls after the panel's end (2026-09-03), in the blind tier, which no comparison may score (docs/decisions/lockbox.md); "
            "the open 2026 days hold no October window, and the study window ends on 2025-12-31 as #1027's walks do"
        ),
    }


# -- B3 -------------------------------------------------------------------------------------------------------------------


def b3_levels() -> Tuple[float, ...]:
    """The levels B3 (the published distribution) forecasts, from the protocol's incumbent."""

    return tuple(float(level) for level in pb.incumbent()["levels"])


def at_b3_levels(quantiles: Sequence[float]) -> List[float]:
    """A 23-level forecast read at B3's five levels (`scoring_protocol.on_levels`)."""

    return sp.on_levels(quantiles, b3_levels())


# -- the declaration ----------------------------------------------------------------------------------------------------------


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1095 before any number was computed; a measurement, not a record. Nothing is published: neither arm joins any published declaration, tax_date and B2 are unchanged, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Adopting the label is Eleonora's (a data meaning, #1004). Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1095,
        "finding": 1004,
        "hypothesis": "H5 step 3, calendar first: the 15 October tax-date column on the calendar-aware variants of #1027",
        "ruling": "Eleonora, 20 October 2026, on #1004 (corrected by the orchestrating session): the 15 October label is deferred, not rejected; tested again with a candidate that reads calendar days at the target day, and only on a reading that leaves out the 2019 and 2025 October days that prompted it, or on 2026 development days",
        "column": {
            "name": COLUMN,
            "definition": "repo_model.tax_date_october.add_columns: 1.0 on the 15th of October rolled forward off weekends and DC holidays (the rule of data.corporate_tax_deadline) and the two market days after it; 0.0 otherwise. A function of the row's own date and metadata/market_holidays.json",
            "declared_in": "repo_model.target_day_columns (OCTOBER_TAX_TARGET_DAY_COLUMNS): written about the target day, so asof rule 2 serves it from the scored row and a one-step fit on it is refused by the #947 guard",
            "served_as": "a calendar column for the run only (october_tax_1004.switched): contract.CALENDAR_FEATURES and asof.CALENDAR_FEATURES gain it inside the walk; no published declaration reads it",
        },
        "arms": {
            DIRECT_OCTOBER: {
                "base": ac.DIRECT,
                "adds": [COLUMN],
                "training_pairs": "direct",
                "min_samples_leaf": ac.LEAF,
                "947_guard": "passes: a direct fit is not checked",
            },
            ALIGNED_OCTOBER: {
                "base": ac.ALIGNED,
                "adds": [COLUMN],
                "training_pairs": None,
                "min_samples_leaf": ac.LEAF,
                "947_guard": "refused by repo_model.one_step_guard: the #1027 allow-list entries cover that variant's regressors only, and a new entry is Eleonora's decision. The arm is run only if she admits it; otherwise it is reported as not run (walk refuses and writes nothing)",
            },
        },
        "inputs": {
            "base": "the #1027 variant's inputs at the lead (scripts/aligned_calendar_1027.py variant_features), unchanged",
            "added": [COLUMN],
            "read": "the target row, at every lead h = 1 to 5: asof rule 2 serves a calendar column from the scored row; a direct pair trains it from its own target row, the aligned arm from the frame whose row p carries row p + 1's",
            "panel": "#951's scratch panel AUG3, as #1027 (the walks of gbm_funding and of the two #1027 variants are #1027's, reused); the column is added to the rows inside the walk",
        },
        "settings": {"as_variant": ["seed", "quantile grid", "refit every 21 scored days", "minimum history 61", "min_samples_leaf 5", "n_estimators and depth of ml.fit_gradient_boosted_quantiles"]},
        "comparisons": [
            "each arm over its #1027 variant without the column",
            "each arm over B1 and over B2 (the protocol's primary benchmarks, on the 23-level grid)",
            "each arm over B3, the published distribution, on its five levels (the protocol's secondary comparison; the variants over B3 beside it)",
            "each arm over gbm_funding",
            "each variant over B1 and B2 beside them, for scale",
        ],
        "metrics": ["grid_crps", "upper_tail_twcrps", "grid_crps_b3_levels (B3 only)"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "calendar_days": list(ac.CALENDAR_TYPES),
            "october_window": CUT_TITLES["october_window"],
            "october_without_2019_2025": "the October window of every year but 2019 and 2025, the years of the motivating prints (2019-10-15, 16 and 17; 2025-10-15 and 16): the reading the ruling asks for",
            "ordinary_outside_october": CUT_TITLES["ordinary_outside_october"] + ": where the column is 0, so a loss there is the cost of carrying the column",
            "october_2026": "the 2026 development days the lockbox leaves open (2026-01-01 to 2026-09-03): reported by reading_2026, not scored. The panel ends on 2026-09-03 and the October 2026 window (15, 16 and 19 October) is in the blind tier; the open 2026 days hold no October window. Extending the study window to them would need new walks of the control and of the variant and is a marked question for Eleonora",
            "minimum": f"a regime or target-type group of fewer than {MIN_GROUP_DAYS} target days is listed and not tested; the three October cuts are scored from {NAMED_CUT_MIN_DAYS} target days, with their day counts and the weak intervals said on the page",
            "labels": "the October cuts label target days after the fact for scoring; they are never an input. Beside them the page lists the October window by year with the realised spread (bp) and each model's mean scores",
        },
        "interval": "stationary bootstrap, seed 1095, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound; each pair carries the interval of the mean difference and of the skill",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind, and the October cuts are 18 to 24 target days",
        "reading_rules": {
            "helps_without_the_motivating_years": "an arm helps over its variant when the lower end of the studentized interval of its mean grid-CRPS difference over the variant on october_without_2019_2025 is above 0 (finding #1004 read the mean difference, whose interval covered zero)",
            "does_not_lose_elsewhere": "and its mean difference over the variant on ordinary_outside_october has an upper interval end of 0 or more; 'loses' means an interval wholly below 0",
            "context": "the same sentence is written for the October window in every year, to show what the two motivating years add; it is context, never the reading",
            "twcrps": "the upper-tail twCRPS of the same cuts is reported beside grid CRPS and is not a second gate",
            "no_verdict": "development data gives no verdict, and adopting the label (tax_date, B2, H8's calendar) is Eleonora's",
        },
        "limits": [
            "no day after 2025-12-31",
            "no lockbox day",
            "no published record is edited",
            "no published declaration changes: every existing declaration stays as it is",
            "tax_date and B2 are unchanged",
            "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed",
        ],
        "questions_for_eleonora": [
            "admit the aligned October arm to the #947 guard (allow-list entries per lead, with an end date)? Default: no, report it as not run",
            "extend the study window to the open 2026 days (2026-01-01 to 2026-09-03), which needs new walks of the control and of the variant? They hold no October window, so it would only show the column costs nothing there. Default: no",
        ],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk ----------------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    from repo_model import measurement_fields

    ac.committed_declaration(DECLARATION)
    sd = ac._load("spread_distribution_634")
    arm, h = args.arm, args.horizon
    if arm not in ARMS or h not in HORIZONS:
        raise SystemExit(f"arm {arm!r} / lead {h} is not declared")
    ac.require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="october_tax_1004")
    require_admitted(arm, h)
    if ac._finished(args.output, arm, h, args.published, args.panel):
        print(json.dumps({"arm": arm, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    plain = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(plain)
    rows = tdo.add_columns(plain)
    features = arm_features(arm, h)
    with ac._load("net_settlement").switched_on(), switched():
        result, levels, settings = sd.walk(
            rows, fit=arm_fit(arm, features), features=features, online_calibration=None, registry=measurement_fields.load_registry(),
            horizon=h, minimum_history=ac.MINIMUM_HISTORY, refit_every=ac.REFIT_EVERY, expected_levels=GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"arm": arm, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the reading rules (tested) ------------------------------------------------------------------------------------------------


def scored_arms(walks: Path) -> Tuple[List[str], Dict[str, str]]:
    """The arms whose five walks exist, and why any other is not run.

    The aligned arm may be absent: the #947 guard refuses it until Eleonora admits it by an allow-list entry, so its walks write nothing. The direct arm may
    not be absent, and an arm with some leads walked and others not is an error, never a silent drop.
    """

    scored, not_run = [], {}
    for arm in ARMS:
        present = [h for h in HORIZONS if (walks / f"{arm}_h{h}.json").is_file()]
        if len(present) == len(HORIZONS):
            scored.append(arm)
        elif present:
            raise ValueError(f"{arm} has walks for leads {present} only; walk every lead or none")
        elif arm == ALIGNED_OCTOBER:
            not_run[arm] = "not run: repo_model.one_step_guard (#947) refuses it until Eleonora admits it by an allow-list entry per lead; walk refuses and writes nothing"
        else:
            raise ValueError(f"{arm} has no walks; the direct arm is the one calendar first asks for and must be scored")
    return scored, not_run


def reading_rules(rows: Mapping[str, Mapping[str, Optional[dict]]], window: str = "october_without_2019_2025") -> List[str]:
    """The declared sentences per arm from its paired grid-CRPS rows over its #1027 variant on the October `window` cut and on `ordinary_outside_october`.

    `rows[arm]` maps those two cut names to a paired row (`s761.paired_row`), an undefined one, or None (not scored). The reading is the mean difference's
    interval (finding #1004 read it); the lower end of a studentized two-sided 90% interval is the one-sided 95% lower bound.
    """

    words = {
        "october_without_2019_2025": "in the October window without 2019 and 2025",
        "october_window": "in the October window of every year",
    }[window]
    out = []
    for arm, cells in rows.items():
        inside, outside = cells.get(window), cells.get("ordinary_outside_october")
        if inside is None or outside is None or "undefined" in inside or "undefined" in outside:
            out.append(f"{arm}: not read (a cut is not scored or undefined).")
            continue
        helps = inside["difference_interval"][0] > 0.0
        loses = outside["difference_interval"][1] < 0.0
        out.append(
            f"{arm} {'helps' if helps else 'is not shown to help'} over {BASE[arm]} {words} (mean difference {inside['difference']:+.3f}, one-sided 95% lower bound "
            f"{inside['difference_interval'][0]:+.3f}, {inside['days']} days) and {'loses' if loses else 'does not lose'} outside October (mean difference "
            f"{outside['difference']:+.3f}, interval {outside['difference_interval'][0]:+.3f} to {outside['difference_interval'][1]:+.3f}, {outside['days']} days)."
        )
    return out


# -- the score --------------------------------------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _task(job):
    key, metric, candidate, benchmark, days = job
    series = _SERIES[(key[0], metric)]
    return key, metric, candidate, benchmark, _SERIES["s761"].run_pairs({benchmark: series[benchmark]}, series[candidate], days, seed=SEED, draws=_SERIES["draws"])[benchmark]


def _check_arm_walks(walks: Path, arm: str, panel: Path) -> None:
    for h in HORIZONS:
        document = json.loads((walks / f"{arm}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("scratch_panel_sha256") != panel_sha256(panel):
            raise ValueError(f"{arm}_h{h}.json was walked from scratch panel {document.get('scratch_panel_sha256')}, not {panel_sha256(panel)}")
        if document.get("features") != list(arm_features(arm, h)):
            raise ValueError(f"{arm}_h{h}.json was walked on inputs other than the declared ones")


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def score_command(args) -> int:
    b960 = ac._load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = ac.committed_declaration(DECLARATION)
    published, panel_path, walks, reference = Path(args.published), Path(args.panel), Path(args.walks), Path(args.reference_walks)
    pub = load_daily_panel(published)
    splits = load_split_declaration(ac.SPLITS)
    registry = json.loads(ac.SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), reference)
    arms, not_run = scored_arms(walks)
    bases = [BASE[arm] for arm in arms]
    models = list(BENCHMARKS) + [CONTROL] + bases + arms
    for base in bases:
        frame.forecasts[base] = ac.load_walks(reference, base, published, panel_path, frame)
    for arm in arms:
        _check_arm_walks(walks, arm, panel_path)
        frame.forecasts[arm] = ac.load_walks(walks, arm, published, panel_path, frame)
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in models)]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days if d in frame.forecasts[name]}
    notes["scored_decision_days"] = len(days)

    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in models}
    series: Dict = {}
    for label, _ in METRICS:
        series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in models}
        series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in models}

    # B3, the published distribution, on its five levels: the days with all five published leads, every model read at those levels
    levels = b3_levels()
    if levels != tuple(s686.FIVE):
        raise ValueError(f"B3's levels {levels} are not the five levels scripts/spread_mean_reversion_686.py reads")
    published_b3 = s686.read_published()
    b3_cells = s686.published_cells(frame, published_b3, days)
    complete = [d for d in days if all((d, h) in b3_cells for h in HORIZONS)]
    kept = set(complete)
    five = {m: s686.five_level_cells(frame, frame.forecasts[m], complete) for m in models}
    five["B3"] = {k: v for k, v in b3_cells.items() if k[0] in kept}
    series[("decision", B3_METRIC)] = {m: s686.by_decision(five[m]) for m in five}
    series[("target", B3_METRIC)] = {m: s686.by_target(frame, five[m]) for m in five}
    notes["b3_decision_days"] = len(complete)
    notes["decision_days_without_five_published_leads"] = len(days) - len(complete)

    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    types = {t: ac.target_type(frame, t) for t in targets}
    labels = {"regime": {t: frame.regime(t) for t in targets}, "target_type": types}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    groups[("target_type", "calendar_days")] = ("target", [d for d in targets if types[d] in ac.CALENDAR_TYPES])
    cuts = october_cuts(targets, types)
    for name, members in cuts.items():
        groups[("october", name)] = ("target", members)

    pairs = [(arm, other) for arm in arms for other in (BASE[arm],) + BENCHMARKS + (CONTROL,)] + [(base, other) for base in bases for other in BENCHMARKS]
    b3_pairs = [(m, "B3") for m in bases + arms]
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        floor = NAMED_CUT_MIN_DAYS if split == "october" else MIN_GROUP_DAYS
        if len(members) < floor:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate, benchmark in pairs:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
        b3_members = tuple(d for d in members if d in series[(grain, B3_METRIC)]["B3"])
        if len(b3_members) >= floor:
            for candidate, benchmark in b3_pairs:
                jobs.append(((grain, f"{split}/{label}"), B3_METRIC, candidate, benchmark, b3_members))
        else:
            skipped[f"{split}/{label} (B3)"] = len(b3_members)
    _SERIES.update(series)
    _SERIES.update({"draws": args.draws, "s761": s761})
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        out = pool.map(_task, jobs, chunksize=1)

    result: dict = {
        "issue": 1095, "finding": 1004, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models, "b3_levels": list(levels),
        "pairs": {**{m: [list(p) for p in pairs] for m, _ in METRICS}, B3_METRIC: [list(p) for p in b3_pairs]},
        "means": {label: {m: _mean(list(series[("decision", label)][m].values())) for m in models} for label, _ in METRICS},
        "b3_means": {m: _mean(list(series[("decision", B3_METRIC)][m].values())) for m in series[("decision", B3_METRIC)]},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"], "not_run": not_run,
        "reading_2026": reading_2026(targets), "october_by_year": october_by_year(frame, cuts["october_window"], series, models),
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = [d for d in groups[(split, label)][1] if d in series[(grain, metric)][candidate] and d in series[(grain, metric)][benchmark]]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(groups[(split, label)][1]), "metrics": {}})
        ser = series[(grain, metric)]
        entry["metrics"].setdefault(metric, {"days": len(members), "means": {m: _mean([ser[m][d] for d in members]) for m in ser if members and all(d in ser[m] for d in members)}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(label, candidate, benchmark, metric="grid_crps"):
        return result["groups"].get("october", {}).get(label, {}).get("metrics", {}).get(metric, {}).get("pairs", {}).get(f"{candidate} vs {benchmark}")

    result["reading_rules"] = reading_rules(
        {a: {"october_without_2019_2025": pick("october_without_2019_2025", a, BASE[a]), "ordinary_outside_october": pick("ordinary_outside_october", a, BASE[a])} for a in arms}
    )
    result["reading_rules_context_every_year"] = reading_rules(
        {a: {"october_window": pick("october_window", a, BASE[a]), "ordinary_outside_october": pick("ordinary_outside_october", a, BASE[a])} for a in arms},
        window="october_window",
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


def october_by_year(frame, window_days: Sequence[date], series: Mapping, models: Sequence[str]) -> Dict[str, dict]:
    """Each year's October window: its target days, the realised spread, and each model's mean scores on them (the 2019 and 2025 rows are the motivating ones)."""

    out: Dict[str, dict] = {}
    for year in sorted({d.year for d in window_days}):
        members = [d for d in window_days if d.year == year]
        out[str(year)] = {
            "days": [d.isoformat() for d in members],
            "spread_bp": [frame.outcome[d] for d in members],
            "motivating": year in LEFT_OUT_YEARS,
            "means": {label: {m: _mean([series[("target", label)][m][d] for d in members]) for m in models} for label, _ in METRICS},
        }
    return out


# -- Markdown ---------------------------------------------------------------------------------------------------------------------

METRIC_TITLES = {**ac.METRIC_TITLES, B3_METRIC: B3_TITLE}
SPLIT_TITLES = {**ac.SPLIT_TITLES, "october": "October cuts (target day; they overlap the types above)"}


def _group_order(label: str):
    if label in ORDER_REGIME:
        return (1, ORDER_REGIME.index(label))
    if label in CUTS:
        return (3, CUTS.index(label))
    return (0, 0) if label == "ordinary" else (2, 0)


def render_report(r: dict, s761) -> str:
    n = r["notes"]
    lines = [
        "# The 15 October tax-date column on the #1027 calendar-aware variants (#1095, finding #1004): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`. Declaration `{r['declaration']}`. "
        f"Seed {r['seed']}, {r['draws']} draws, the studentized stationary bootstrap. {n['scored_decision_days']} decision days, every pair on the same days. "
        "Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). "
        "Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days, and the October cuts hold 18 to 24 target days. "
        "The October cuts overlap the five exclusive target day types. Adopting the label is Eleonora's; this page does not decide it.", "",
        "## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {m} | " + " | ".join(f"{r['means'][label][m]:.4f}" for label in r["means"]) + " |")
    lines += ["", f"B3's five levels ({', '.join(str(level) for level in r['b3_levels'])}); {n['b3_decision_days']} decision days have all five published leads "
              f"({n['decision_days_without_five_published_leads']} do not):", "", "| model | " + METRIC_TITLES[B3_METRIC] + " |", "|---|---|"]
    lines += [f"| {m} | {v:.4f} |" for m, v in r["b3_means"].items()]
    lines += ["", "## Reading (declared rules)", "", "Over the arm's #1027 variant, in the October window without 2019 and 2025:", ""] + [f"- {s}" for s in r["reading_rules"]]
    lines += ["", "Context only, the October window in every year:", ""] + [f"- {s}" for s in r["reading_rules_context_every_year"]]
    lines += [f"- {a}: {why}." for a, why in sorted(r.get("not_run", {}).items())]
    w = r["reading_2026"]
    lines += ["", "## The 2026 development days", "",
              f"{w['why'].capitalize()}. Scored 2026 target days: {w['scored_open_2026_days']}; October-window days among them: {w['october_window_days']}. "
              f"The October 2026 window is {', '.join(w['october_2026_window'])}. Extending the study window to the open 2026 days is a marked question for Eleonora.", "",
              "## The October window by year", "",
              "Realised SOFR - IORB (bp) on the window's target days, and each model's mean grid CRPS on them. Marked years are the ones whose prints prompted the label.", "",
              "| year | target days | spread (bp) | " + " | ".join(f"{m}" for m in r["models"]) + " |", "|---|---|---|" + "---|" * len(r["models"])]
    for year, entry in r["october_by_year"].items():
        spread = ", ".join(f"{day[5:]} {value:+.1f}" for day, value in zip(entry["days"], entry["spread_bp"]))
        mark = " (motivating)" if entry["motivating"] else ""
        lines.append(f"| {year}{mark} | {len(entry['days'])} | {spread} | " + " | ".join(f"{entry['means']['grid_crps'][m]:.3f}" for m in r["models"]) + " |")
    lines.append("")
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        names = [f"{c} vs {b}" for c, b in r["pairs"][metric]]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            lines += [f"### {SPLIT_TITLES[split]}", ""]
            lines += ["| group | days | " + " | ".join(p.replace(" vs ", " over ") for p in names) + " |", "|---|---|" + "---|" * len(names)]
            for label in sorted(r["groups"][split], key=_group_order):
                entry = r["groups"][split][label]
                if metric not in entry["metrics"]:
                    continue
                row_cells = entry["metrics"][metric]["pairs"]
                shown = CUT_TITLES.get(label, label) if split == "october" else label
                days = entry["metrics"][metric]["days"] if metric == B3_METRIC else entry["days"]
                lines.append(f"| {shown} | {days:,} | " + " | ".join(s761.skill_text(row_cells[p]) if p in row_cells else "n/a" for p in names) + " |")
            lines.append("")
        if metric != B3_METRIC and "october" in r["groups"]:
            lines += [f"### Mean difference, {METRIC_TITLES[metric]} (positive favours the first model; October cuts)", "",
                      "| group | days | " + " | ".join(p.replace(" vs ", " over ") for p in names) + " |", "|---|---|" + "---|" * len(names)]
            for label in sorted(r["groups"]["october"], key=_group_order):
                entry = r["groups"]["october"][label]
                row_cells = entry["metrics"].get(metric, {}).get("pairs", {})
                lines.append(f"| {CUT_TITLES.get(label, label)} | {entry['days']:,} | " + " | ".join(s761.diff_text(row_cells[p]) if p in row_cells else "n/a" for p in names) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += ["Groups below their minimum, listed and not tested: " + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(run=declare_command)
    walk = sub.add_parser("walk")
    walk.add_argument("--arm", required=True, choices=ARMS)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    score = sub.add_parser("score")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True, help="the directory of this study's arm walks")
    score.add_argument("--reference-walks", type=Path, required=True, help="the directory of #1027's walks: gbm_funding and the variants")
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
