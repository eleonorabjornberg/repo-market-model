"""The two #1027 calendar-aware variants with the FOMC meeting columns added: two declared arms (#1087, H5 step 3, calendar first).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no published figure (Eleonora,
21 October 2026, on #1046: the columns stay off every published declaration until this result is in). Every choice is in
`metadata/fomc_variants_1087.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from the constants
below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**The arms.** Each arm is a #1027 variant (`scripts/aligned_calendar_1027.py`) with `fomc_meeting_day` and `fomc_days_to_next_meeting`
(`repo_model.fomc_calendar`, #1038) added as regressors at every lead h = 1..5. The variant's other inputs, leaf, seed, quantile grid, refit cadence and
pairing are the variant's, so an arm differs from its variant by the two columns only.

* `gbm_funding_cal_direct_fomc`: `gbm_funding_cal_direct` plus the columns, on direct pairs (`training_pairs="direct"`).
* `gbm_funding_cal_aligned_fomc`: `gbm_funding_cal_aligned` plus the columns, on one-step pairs of the aligned frame. The #947 guard refuses it: the
  allow-list entries of #1027 cover that variant's regressors only, and a new entry is hers (CLAUDE.md). `walk` refuses it (a non-zero exit) and writes nothing
  until she admits it; `score` then reports it as not run.

**Read at the target day.** The columns are written about the target day and read at the decision instant of the lead (`asof` rule 2). Three parts:
`with_fomc` gives row T the values read at the decision instant of the panel day h rows before T (`fomc_calendar.add_columns(horizon=h)`: a meeting is
counted from its schedule's release instant and a cancelled one is dropped from its cancellation's, each meeting passing `require_public`);
`fomc_registry(h)` declares the source to `InformationRule` as a scheduled field available h panel days ahead at 16:00, so the rule serves the columns from
the target row and `check` raises `LookAheadError` for a read that is not public; and the fit trains each column from the target row of its pair (direct
pairs by construction; one-step pairs on the frame with row p carrying row p + 1's).

    # PUB.csv, AUG3.csv and the walks of gbm_funding and of the two #1027 variants: ~/rmm-1027 on the Mac (#1027's paste builds them)
    PYTHONPATH=src python3 scripts/fomc_variants_1087.py declare            # then commit metadata/fomc_variants_1087.json before any score
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/fomc_variants_1087.py walk --arm gbm_funding_cal_direct_fomc --horizon $h \\
            --published PUB.csv --panel AUG3.csv --output WALKS/gbm_funding_cal_direct_fomc_h$h.json
    PYTHONPATH=src python3 scripts/fomc_variants_1087.py score --published PUB.csv --panel AUG3.csv --walks WALKS --reference-walks REF \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import functools
import hashlib
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import contract, fomc_calendar as fc, ml, one_step_guard, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

ac = _load("aligned_calendar_1027")

DECLARATION = REPO / "metadata" / "fomc_variants_1087.json"
LAST_TARGET = ac.LAST_TARGET
SEED = 1087
HORIZONS = ac.HORIZONS
GRID = ac.GRID
FOMC_COLUMNS = fc.COLUMNS

CONTROL = ac.CONTROL
DIRECT_FOMC = "gbm_funding_cal_direct_fomc"
ALIGNED_FOMC = "gbm_funding_cal_aligned_fomc"
ARMS = (DIRECT_FOMC, ALIGNED_FOMC)
#: each arm's #1027 variant, the one it is scored against besides the control
BASE = {DIRECT_FOMC: ac.DIRECT, ALIGNED_FOMC: ac.ALIGNED}
METRICS = ac.METRICS
ORDER_REGIME = ac.ORDER_REGIME
MIN_GROUP_DAYS = ac.MIN_GROUP_DAYS
#: the overlapping cuts of FOMC days, beside the five exclusive target day types of #1027
FOMC_CUTS = ("fomc_day", "fomc_ordinary", "ordinary_non_fomc")


# -- the arms --------------------------------------------------------------------------------------------------------


def arm_features(arm: str, horizon: int) -> Tuple[str, ...]:
    """The arm's inputs at a lead: its #1027 variant's, then the two FOMC columns (none twice)."""

    if arm not in ARMS:
        raise ValueError(f"{arm!r} is not a declared arm")
    base = ac.variant_features(BASE[arm], horizon)
    return base + tuple(c for c in FOMC_COLUMNS if c not in base)


def arm_fit(arm: str, features: Sequence[str]):
    """The arm's fitter: its variant's (the gbm at the declared leaf), on direct pairs or on the aligned frame, with the FOMC columns among the regressors."""

    names = ac.regressors(features)
    if arm == DIRECT_FOMC:
        return functools.partial(ml.fit_gradient_boosted_quantiles, regressors=names, levels=GRID, min_samples_leaf=ac.LEAF, training_pairs="direct")
    if arm != ALIGNED_FOMC:
        raise ValueError(f"{arm!r} is not a declared arm")
    fields = ac.TARGET_ROW_COLUMNS + FOMC_COLUMNS

    def fit(train_frame, minimum_history):
        aligned = ac.align_columns(train_frame, fields)
        ac.require_aligned(train_frame, aligned, fields)
        return ml.fit_gradient_boosted_quantiles(
            aligned, regressors=names, levels=GRID, minimum_history=minimum_history, min_samples_leaf=ac.LEAF
        )

    return fit


def require_admitted(arm: str, horizon: int) -> None:
    """Refuse, with a non-zero exit, before any work when the #947 guard would refuse the arm's fit (adding an allow-list entry is Eleonora's decision)."""

    if arm != ALIGNED_FOMC:
        return
    try:
        one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", ac.regressors(arm_features(arm, horizon)))
    except ValueError as error:
        raise SystemExit(
            f"{arm} lead {horizon}: not run. repo_model.one_step_guard (#947) refuses it, and a new allow-list entry is Eleonora's decision "
            f"(CLAUDE.md); nothing is written. {error}"
        ) from None


# -- the columns, read at the target day --------------------------------------------------------------------------------


def with_fomc(rows: Sequence[DailyObservation], horizon: int, calendar: Optional[Sequence[fc.Meeting]] = None) -> List[DailyObservation]:
    """`rows` with row T's FOMC columns as read at the decision instant of the panel day `horizon` rows before T (the lead's own)."""

    return fc.add_columns(rows, calendar, horizon=horizon)


def fomc_registry(horizon: int, registry: Optional[Mapping[str, Mapping[str, object]]] = None) -> Dict[str, Mapping[str, object]]:
    """A copy of the registry whose `fomc_calendar` source is a scheduled field available `horizon` panel days ahead, at the 16:00 decision time.

    The value for the target row is computed from the meetings public at the decision instant of `horizon` rows before it (`with_fomc`), so it is
    public at that instant by construction; `asof` rule 2 then serves it from the target row, and `InformationRule.check` raises `LookAheadError` for a
    declaration of availability later than the decision. The registries on disk are not changed.
    """

    if registry is None:
        from repo_model import measurement_fields

        registry = measurement_fields.load_registry()
    out = dict(registry)
    source = copy.deepcopy(dict(out[fc.SOURCE_ID]))
    source["scheduled_availability"] = {
        "basis": "announced_before_ref_date",
        "unit": "business_days",
        "days": horizon,
        "available_time": "16:00",
        "timezone": "America/New_York",
        "fields": list(FOMC_COLUMNS),
        "evidence": (
            "Declared for the #1087 study at lead h = days. The value for target row T is computed by repo_model.fomc_calendar.add_columns(horizon=days) "
            "from the meetings public at the 16:00 decision instant of the panel day `days` rows before T (each passing require_public, which raises "
            "LookAheadError), so it is public at that instant by construction; tests/test_fomc_calendar.py pins the dating and tests/test_fomc_variants_1087.py "
            "the read at each lead."
        ),
        "note": "A study-time declaration, not a registry change: metadata/sources_measurement.json is unchanged and the columns stay off every published declaration.",
    }
    out[fc.SOURCE_ID] = source
    return out


@contextlib.contextmanager
def fomc_fields_on():
    """The FOMC columns in the feature map, for this run only (`contract.FEATURE_FIELDS`, as `net_settlement.switched_on` does for its columns)."""

    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fc.COLUMN_FIELDS}),
        FEATURE_SOURCES=MappingProxyType(
            {**contract.FEATURE_SOURCES, **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fc.COLUMN_FIELDS.items()}}
        ),
    ):
        yield


def calendar_sha256() -> str:
    return hashlib.sha256(fc.CALENDAR_PATH.read_bytes()).hexdigest()


# -- the day types ---------------------------------------------------------------------------------------------------------


def is_fomc_day(day: date, calendar: Sequence[fc.Meeting]) -> bool:
    """Whether `day` held a Committee meeting, labelled after the fact (a label for a score, never an input): both days of a two-day meeting, an
    unscheduled meeting on its day, a cancelled meeting not at all."""

    return any(m.cancelled_at is None and m.start <= day <= m.end for m in calendar)


def fomc_cuts(types: Mapping[date, str], calendar: Sequence[fc.Meeting]) -> Dict[str, List[date]]:
    """The overlapping FOMC cuts of the target days `types` maps to their #1027 type: every meeting day; a meeting day whose #1027 type is ordinary;
    and an ordinary day with no meeting."""

    out: Dict[str, List[date]] = {name: [] for name in FOMC_CUTS}
    for day in sorted(types):
        meeting = is_fomc_day(day, calendar)
        if meeting:
            out["fomc_day"].append(day)
        if meeting and types[day] == "ordinary":
            out["fomc_ordinary"].append(day)
        if not meeting and types[day] == "ordinary":
            out["ordinary_non_fomc"].append(day)
    return out


# -- the declaration ----------------------------------------------------------------------------------------------------------


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1087 before any number was computed; a measurement, not a record. Nothing is published: neither arm joins any published declaration, the FOMC columns stay off every published declaration (Eleonora, 21 October 2026, on #1046), no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1087,
        "hypothesis": "H5 step 3, calendar first: the FOMC meeting columns (#1038, #1046) on the calendar-aware variants of #1027",
        "ruling": "Eleonora, 21 October 2026, relayed by the orchestrating session, on #1046: calendar first; FOMC meeting days are calendar days, so the columns are tested on the calendar-aware variants (option 2)",
        "arms": {
            DIRECT_FOMC: {
                "base": ac.DIRECT,
                "adds": list(FOMC_COLUMNS),
                "training_pairs": "direct",
                "min_samples_leaf": ac.LEAF,
                "947_guard": "passes: a direct fit is not checked",
            },
            ALIGNED_FOMC: {
                "base": ac.ALIGNED,
                "adds": list(FOMC_COLUMNS),
                "training_pairs": None,
                "min_samples_leaf": ac.LEAF,
                "947_guard": "refused by repo_model.one_step_guard: the #1027 allow-list entries cover that variant's regressors only, and a new entry is Eleonora's decision. The arm is run only if she admits it; otherwise it is reported as not run (walk refuses and writes nothing)",
            },
        },
        "inputs": {
            "base": "the #1027 variant's inputs at the lead (scripts/aligned_calendar_1027.py variant_features), unchanged",
            "added": list(FOMC_COLUMNS),
            "read": "the target row, at every lead h = 1 to 5: row T carries the values read at the decision instant of the panel day h rows before T (fomc_calendar.add_columns(horizon=h)), a meeting counted from its schedule's release instant and a cancelled one dropped from its cancellation's; served by asof rule 2 under a study-time scheduled declaration of h panel days ahead at 16:00 (fomc_registry)",
            "calendar": "metadata/fomc_calendar.json (#1038), its sha256 recorded in every walk and checked at score time",
            "panel": "#951's scratch panel AUG3, as #1027 (the walks of gbm_funding and of the two #1027 variants are #1027's, reused)",
        },
        "settings": {"as_variant": ["seed", "quantile grid", "refit every 21 scored days", "minimum history 61", "min_samples_leaf 5", "n_estimators and depth of ml.fit_gradient_boosted_quantiles"]},
        "comparisons": ["each arm over its #1027 variant without the columns", "each arm over gbm_funding"],
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "calendar_days": list(ac.CALENDAR_TYPES),
            "fomc_day": "every target day that held a meeting (both days of a two-day meeting; an unscheduled meeting on its day; a cancelled meeting not), whatever its other type; overlaps the types above",
            "fomc_ordinary": "a meeting day whose #1027 type is ordinary",
            "ordinary_non_fomc": "an ordinary target day that held no meeting",
            "labels": "the FOMC cuts label target days after the fact for scoring; they are never an input",
        },
        "interval": "stationary bootstrap, seed 1087, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "helps_on_fomc_days": "an arm helps over its variant on FOMC days when the lower end of its grid-CRPS skill interval over the variant on the fomc_day cut is above 0",
            "does_not_lose_elsewhere": "and its skill over the variant on ordinary non-FOMC days has an upper interval end of 0 or more; 'loses' means an interval wholly below 0",
            "against_the_control": "read as #1027's rule: an arm beats gbm_funding on calendar days when the lower end of its grid-CRPS skill interval over gbm_funding on the calendar_days cut is above 0, and does not lose on ordinary days when that interval's upper end on the ordinary cut is 0 or more",
            "publish": "whether the columns join a published declaration is Eleonora's question (#1046) and comes back to her with this result; this page does not decide it",
            "no_verdict": "development data gives no verdict",
        },
        "limits": ["no day after 2025-12-31", "no lockbox day", "no published record is edited", "no published declaration changes", "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk ----------------------------------------------------------------------------------------------------------------


def _finished(output: Path, arm: str, h: int, published: Path, panel: Path) -> bool:
    """Whether `output` already holds this walk, from the same panel and calendar bytes (a stopped run keeps what it wrote)."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(document, dict) and isinstance(document.get("laws"), dict) and document.get("variant") == arm and document.get("horizon") == h
        and document.get("panel_sha256") == panel_sha256(published) and document.get("scratch_panel_sha256") == panel_sha256(panel)
        and document.get("fomc_calendar_sha256") == calendar_sha256()
    )


def walk_command(args) -> int:
    from repo_model import measurement_fields

    ac.committed_declaration(DECLARATION)
    sd = ac._load("spread_distribution_634")
    arm, h = args.arm, args.horizon
    if arm not in ARMS or h not in HORIZONS:
        raise SystemExit(f"arm {arm!r} / lead {h} is not declared")
    ac.require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="fomc_variants_1087")
    require_admitted(arm, h)
    if _finished(args.output, arm, h, args.published, args.panel):
        print(json.dumps({"arm": arm, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    plain = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(plain)
    rows = with_fomc(plain, h)
    features = arm_features(arm, h)
    registry = fomc_registry(h, measurement_fields.load_registry())
    with ac._load("net_settlement").switched_on(), fomc_fields_on():
        result, levels, settings = sd.walk(
            rows, fit=arm_fit(arm, features), features=features, online_calibration=None, registry=registry,
            horizon=h, minimum_history=ac.MINIMUM_HISTORY, refit_every=ac.REFIT_EVERY, expected_levels=GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "fomc_calendar_sha256": calendar_sha256(), "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
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
        elif arm == ALIGNED_FOMC:
            not_run[arm] = "not run: repo_model.one_step_guard (#947) refuses it until Eleonora admits it by an allow-list entry per lead; walk refuses and writes nothing"
        else:
            raise ValueError(f"{arm} has no walks; the direct arm is the one calendar first asks for and must be scored")
    return scored, not_run


def reading_rules(rows: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    """The declared sentences per arm from its paired grid-CRPS rows over its #1027 variant on `fomc_day` and `ordinary_non_fomc` target days.

    `rows[arm]` maps those two cut names to a paired row (`s761.paired_row`), an undefined one, or None (not scored). The lower end of a studentized
    two-sided 90% interval is the one-sided 95% lower bound.
    """

    s761 = ac._load("spread_mr_variants_761")
    out = []
    for arm, cells in rows.items():
        fomc, ordinary = cells.get("fomc_day"), cells.get("ordinary_non_fomc")
        if fomc is None or ordinary is None or "undefined" in fomc or "undefined" in ordinary:
            out.append(f"{arm}: not read (a cut is not scored or undefined).")
            continue
        helps = fomc["skill_interval"][0] > 0.0
        loses = ordinary["skill_interval"][1] < 0.0
        out.append(
            f"{arm} {'helps' if helps else 'is not shown to help'} over {BASE[arm]} on FOMC days (skill {s761.pct(fomc['skill'])}, one-sided 95% lower bound "
            f"{s761.pct(fomc['skill_interval'][0])}) and {'loses' if loses else 'does not lose'} on ordinary non-FOMC days (skill {s761.pct(ordinary['skill'])}, "
            f"interval {s761.pct(ordinary['skill_interval'][0])} to {s761.pct(ordinary['skill_interval'][1])})."
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
        if document.get("fomc_calendar_sha256") != calendar_sha256():
            raise ValueError(f"{arm}_h{h}.json was walked from another FOMC calendar than metadata/fomc_calendar.json")


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
    models = [CONTROL] + bases + arms
    for base in bases:
        frame.forecasts[base] = ac.load_walks(reference, base, published, panel_path, frame)
    for arm in arms:
        _check_arm_walks(walks, arm, panel_path)
        frame.forecasts[arm] = ac.load_walks(walks, arm, published, panel_path, frame)
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in models)]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes["scored_decision_days"] = len(days)

    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in models}
    series: Dict = {}
    for label, _ in METRICS:
        series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in models}
        series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in models}
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
    for name, members in fomc_cuts(types, fc.load_calendar()).items():
        groups[("target_type", name)] = ("target", members)

    pairs = [(arm, benchmark) for arm in arms for benchmark in (BASE[arm], CONTROL)]
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate, benchmark in pairs:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
    _SERIES.update(series)
    _SERIES.update({"draws": args.draws, "s761": s761})
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        out = pool.map(_task, jobs, chunksize=1)

    result: dict = {
        "issue": 1087, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "fomc_calendar_sha256": calendar_sha256(), "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models,
        "pairs": [list(p) for p in pairs], "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in models} for label, _ in METRICS},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"], "not_run": not_run,
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = _SERIES[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(label, candidate, benchmark):
        return result["groups"].get("target_type", {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{candidate} vs {benchmark}")

    result["reading_rules"] = reading_rules({a: {"fomc_day": pick("fomc_day", a, BASE[a]), "ordinary_non_fomc": pick("ordinary_non_fomc", a, BASE[a])} for a in arms})
    result["reading_rules_against_the_control"] = ac.reading_rules(
        {a: {"calendar": pick("calendar_days", a, CONTROL), "ordinary": pick("ordinary", a, CONTROL)} for a in arms}
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


# -- Markdown ---------------------------------------------------------------------------------------------------------------------

METRIC_TITLES = ac.METRIC_TITLES
SPLIT_TITLES = ac.SPLIT_TITLES


def _group_order(label: str):
    if label in ORDER_REGIME:
        return (1, ORDER_REGIME.index(label))
    if label in FOMC_CUTS:
        return (3, FOMC_CUTS.index(label))
    return (0, 0) if label == "ordinary" else (2, 0)


def render_report(r: dict, s761) -> str:
    n = r["notes"]
    lines = [
        "# The #1027 calendar-aware variants with the FOMC meeting columns (#1087): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`, FOMC calendar `{r['fomc_calendar_sha256']}`. Declaration `{r['declaration']}`. "
        f"Seed {r['seed']}, {r['draws']} draws, the studentized stationary bootstrap. {n['scored_decision_days']} decision days, every pair on the same days. "
        "Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). "
        "Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. The cuts `fomc_day`, `fomc_ordinary` and "
        "`ordinary_non_fomc` overlap the five exclusive target day types.", "",
        "## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {m} | " + " | ".join(f"{r['means'][label][m]:.4f}" for label in r["means"]) + " |")
    lines += ["", "## Reading (declared rules)", "", "Over the arm's #1027 variant:", ""] + [f"- {s}" for s in r["reading_rules"]]
    lines += ["", "Over gbm_funding:", ""] + [f"- {s}" for s in r["reading_rules_against_the_control"]]
    lines += [f"- {a}: {why}." for a, why in sorted(r.get("not_run", {}).items())]
    lines += ["", "Whether the columns join a published declaration is Eleonora's question (#1046); this page does not decide it.", ""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            lines += [f"### {SPLIT_TITLES[split]}", ""]
            names = [f"{c} vs {b}" for c, b in r["pairs"]]
            lines += ["| group | days | " + " | ".join(p.replace(" vs ", " over ") for p in names) + " |", "|---|---|" + "---|" * len(names)]
            for label in sorted(r["groups"][split], key=_group_order):
                entry = r["groups"][split][label]
                row_cells = entry["metrics"].get(metric, {}).get("pairs", {})
                lines.append(f"| {label} | {entry['days']:,} | " + " | ".join(s761.skill_text(row_cells[p]) if p in row_cells else "n/a" for p in names) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += ["Groups of fewer than %d days, listed and not tested: " % MIN_GROUP_DAYS + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
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
