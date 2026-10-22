"""The #1027 direct variant with the Treasury settlement columns dated from the auction announcement at leads 2 to 5: two declared arms (#1124, H5 step 3).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no published figure. The dating it
reads (`metadata/settlement_announcement_dating.json`, #541) is measured and **not in force**: rule 2 of `docs/decisions/information-set.md` is not amended,
`metadata/sources.json` is unchanged, and the published paths still refuse a settlement column beyond lead 1 (`tests/test_aligned_announcement_1124.py`).
Every choice is in `metadata/aligned_announcement_1124.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes
it from the constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is
read (`docs/decisions/lockbox.md`).

**The arms.** Each is `gbm_funding_cal_direct` of #1027 (`scripts/aligned_calendar_1027.py`: `gbm_funding`'s published inputs, the calendar columns read from the
target row, the observed net-settlement columns, leaf 5, direct pairs) with settlement columns added at leads 2 to 5, where the published declaration and the
published features carry none:

* `gbm_funding_cal_direct_ann`: `treasury_settlement` (the gross aggregate), `treasury_settlement_coupons` and `treasury_settlement_bills`;
* `gbm_funding_cal_direct_ann_coupons`: `treasury_settlement_coupons` only (the coupon leg, read apart from the gross aggregate: through it alone a day on which
  only bills settle looks like a day with no settlement, Lens A of #958).

**The dating.** For a settlement day d and lead h, a column is the sum of the offerings of the auctions settling on d that had been announced by 12:00 on the
panel day h rows before d (`settlement_dating.known_columns`, checked by `check_known_columns`, which raises `LookAheadError` for a column that counts an
auction not yet announced). `result_dated_registry` declares those columns to `InformationRule` as a scheduled field available h panel days ahead, in a copy of
the registry: the file on disk is not touched, and nothing outside this script reads the copy. At lead 1 the dated columns are the published panel's, so the arms
are `gbm_funding_cal_direct` there by construction; `score` reports whether the lead-1 walks agree.

**The #947 guard.** The arms train on direct pairs (`training_pairs="direct"`), which the guard does not check, so no allow-list entry is needed. The aligned one-step
design (`gbm_funding_cal_aligned`) with these columns at leads 2 to 5 would need allow-list entries, which are Eleonora's decision and which the ruling on #1124 did not
make; it is not run, and `gbm_funding_cal_aligned` is scored here as a comparator only, from #1027's walks.

The walks are long (`needs-mac`, #46); `score` reads them. The reference walks (`gbm_funding`, `gbm_funding_cal_aligned`, `gbm_funding_cal_direct`) are #1027's.

    # PUB.csv: the published panel (digest 4ddc3882...); AUG3.csv: #951's scratch panel; REF: #1027's walks (~/rmm-1027/WALKS on the Mac)
    PYTHONPATH=src python3 scripts/aligned_announcement_1124.py declare            # then commit metadata/aligned_announcement_1124.json before any score
    for h in 1 2 3 4 5:
        for a in gbm_funding_cal_direct_ann gbm_funding_cal_direct_ann_coupons:
            OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_announcement_1124.py walk --arm $a --horizon $h \\
                --published PUB.csv --panel AUG3.csv --output WALKS/${a}_h$h.json
    PYTHONPATH=src python3 scripts/aligned_announcement_1124.py score --published PUB.csv --panel AUG3.csv --walks WALKS --reference-walks REF \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import ml, scoring_protocol as sp, settlement_dating  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

ac = _load("aligned_calendar_1027")

DECLARATION = REPO / "metadata" / "aligned_announcement_1124.json"
DATING = REPO / "metadata" / "settlement_announcement_dating.json"
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions" / "20260914T051023Z_722359ea9bc7.json"
LAST_TARGET = ac.LAST_TARGET
SEED = 1124
HORIZONS = ac.HORIZONS
GRID = ac.GRID
METRICS = ac.METRICS
ORDER_REGIME = ac.ORDER_REGIME
MIN_GROUP_DAYS = ac.MIN_GROUP_DAYS

CONTROL = ac.CONTROL
ALIGNED = ac.ALIGNED
DIRECT = ac.DIRECT
ANN = "gbm_funding_cal_direct_ann"
ANN_COUPONS = "gbm_funding_cal_direct_ann_coupons"
ARMS = (ANN, ANN_COUPONS)
#: the columns each arm adds at leads 2 to 5 to the direct variant's inputs
ADDED = {
    ANN: ("treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills"),
    ANN_COUPONS: ("treasury_settlement_coupons",),
}
BENCHMARKS = ("B1", ac.B1P, "B2")
#: the two windows of a score: the protocol's (the mean over leads 1 to 5) and the arms' own leads (2 to 5, where they differ from the direct variant)
WINDOWS = {"h1_5": (1, 2, 3, 4, 5), "h2_5": (2, 3, 4, 5)}
#: the target day types of this study: #1027's, with a settlement on an otherwise ordinary day split into coupon and bill-only
CALENDAR_TYPES = ("quarter_end", "month_end", "tax_date", "settlement_coupon", "settlement_bill")
SETTLEMENT_TYPES = ("settlement_coupon", "settlement_bill")


# -- the arms --------------------------------------------------------------------------------------------------------


def arm_features(arm: str, horizon: int) -> Tuple[str, ...]:
    """The arm's inputs at a lead: the direct variant's, then its settlement columns (none twice)."""

    if arm not in ARMS:
        raise ValueError(f"{arm!r} is not a declared arm")
    base = ac.variant_features(DIRECT, horizon)
    return base + tuple(c for c in ADDED[arm] if c not in base)


def arm_fit(arm: str, features: Sequence[str]):
    """The arm's fitter: the direct variant's (the gbm at the declared leaf, on direct pairs) with the settlement columns among the regressors."""

    if arm not in ARMS:
        raise ValueError(f"{arm!r} is not a declared arm")
    return functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=ac.regressors(features), levels=GRID, min_samples_leaf=ac.LEAF, training_pairs="direct"
    )


def arm_inputs(
    rows: Sequence[DailyObservation],
    registry: Mapping[str, Mapping[str, object]],
    horizon: int,
    *,
    results: Optional[Sequence[settlement_dating.AuctionResult]] = None,
    declaration: Optional[Mapping[str, object]] = None,
) -> Tuple[List[DailyObservation], dict]:
    """`rows` with the settlement columns as public `horizon` panel days ahead, checked, and a copy of `registry` declaring them so.

    The announcement dating is measured and off: the published registry is not changed (`result_dated_registry` copies it) and no published path reads
    the copy. Raises `LookAheadError` (`StaleReadError`) when a column counts an auction not yet announced (leaves one out).
    """

    declaration = settlement_dating.load_result_dating(DATING) if declaration is None else declaration
    results = settlement_dating.load_snapshot_results(SNAPSHOT, declaration) if results is None else results
    dated = settlement_dating.known_columns(rows, results, horizon, declaration)
    settlement_dating.check_known_columns(dated, results, horizon, declaration)
    registry = settlement_dating.result_dated_registry(registry, declaration, horizon)
    return dated, registry


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# -- the day types ---------------------------------------------------------------------------------------------------


def target_type(frame, day: date) -> str:
    """The target day's reporting day type; an otherwise ordinary day is `settlement_coupon` when a coupon settles on it, else `settlement_bill` when only bills do."""

    kind = frame.day_type(day)
    if kind != "ordinary":
        return kind
    values = frame.values[day]
    if (values.get("treasury_settlement_coupons") or 0.0) > 0.0:
        return "settlement_coupon"
    if (values.get("treasury_settlement_bills") or 0.0) > 0.0:
        return "settlement_bill"
    return kind


# -- the declaration ---------------------------------------------------------------------------------------------------------


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1124 before any number was computed; a measurement, not a record. Nothing is published: neither arm joins any published declaration, the announcement dating stays measured and not in force (rule 2 of docs/decisions/information-set.md is not amended), no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1124,
        "hypothesis": "H5 step 3 (avenue #1114): the #1027 aligned design with the Treasury settlement columns dated from the auction announcement at leads 2 to 5",
        "ruling": "Eleonora, 22 October 2026, relayed by the orchestrating session on #1124: 'queue them now' (avenue #1114)",
        "dating": {
            "file": "metadata/settlement_announcement_dating.json",
            "status": "measured and not in force; read here through this study's own scratch-only path (scripts/aligned_announcement_1124.py arm_inputs), which dates the columns with settlement_dating.known_columns, checks them with check_known_columns and declares them in a copy of the registry with result_dated_registry",
            "unchanged": ["metadata/sources.json", "docs/decisions/information-set.md", "the published declaration", "metadata/settlement_announcement_dating.json"],
            "at_lead_1": "the dated column is the published panel's column on every panel day (the file's own rule), so an arm is gbm_funding_cal_direct at lead 1; score reports whether the lead-1 walks agree",
        },
        "arms": {
            ANN: {
                "base": DIRECT,
                "adds_at_leads_2_to_5": list(ADDED[ANN]),
                "training_pairs": "direct",
                "min_samples_leaf": ac.LEAF,
                "947_guard": "passes: a direct fit is not checked, and no allow-list entry is added",
            },
            ANN_COUPONS: {
                "base": DIRECT,
                "adds_at_leads_2_to_5": list(ADDED[ANN_COUPONS]),
                "training_pairs": "direct",
                "min_samples_leaf": ac.LEAF,
                "947_guard": "passes: a direct fit is not checked, and no allow-list entry is added",
                "why": "the coupon leg read apart from the gross aggregate (Lens A of #958: through the coupon leg alone a bill-only settlement day looks like a day with no settlement)",
            },
        },
        "one_step_guard": "Direct pairs were used, as the ruling prefers. The aligned one-step design (gbm_funding_cal_aligned) with these columns at leads 2 to 5 would need allow-list entries in repo_model.one_step_guard, which are Eleonora's decision and which today's ruling did not admit (#1093, #1098, #1109); it is not run. gbm_funding_cal_aligned is a comparator only, from #1027's walks, which its existing allow-list entries admit until their end date.",
        "inputs": {
            "base": "gbm_funding_cal_direct's inputs at the lead (scripts/aligned_calendar_1027.py variant_features): gbm_funding's published inputs, the calendar columns read from the target row, the observed net_settlement columns",
            "added": "ANN: treasury_settlement, treasury_settlement_coupons, treasury_settlement_bills; ANN_COUPONS: treasury_settlement_coupons; leads 2 to 5 only",
            "read": "the target row, as announced by 12:00 on the panel day h rows before it; a direct pair trains each column from its own target's as-of read",
            "panel": "#951's scratch panel AUG3, as #1027; the walks of gbm_funding and of the two #1027 variants are #1027's, reused",
        },
        "settings": {"as_variant": ["seed", "quantile grid", "refit every 21 scored days", "minimum history 61", "min_samples_leaf 5", "n_estimators and depth of ml.fit_gradient_boosted_quantiles"]},
        "comparisons": {
            "against": [ALIGNED, CONTROL, "B1", ac.B1P, "B2", DIRECT],
            "why_direct": "the matched control: the same pairing and inputs without the settlement columns at leads 2 to 5, so the difference is the dating alone",
            "between_arms": [ANN_COUPONS, ANN],
        },
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "windows": {"h1_5": "the protocol's primary figure: the mean over leads 1 to 5 per decision day (and per target day)", "h2_5": "the mean over leads 2 to 5, the leads the arms differ at"},
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement_coupon", "settlement_bill", "ordinary"],
            "settlement_coupon": "a target day whose reporting day type is ordinary and whose treasury_settlement_coupons is above 0 (a bill may settle too)",
            "settlement_bill": "a target day whose reporting day type is ordinary, whose treasury_settlement_coupons is not above 0 and whose treasury_settlement_bills is above 0 (bill-only)",
            "settlement_any": "the union of the two, #1027's settlement type",
            "calendar_days": "quarter_end, month_end, tax_date, settlement_coupon and settlement_bill",
            "labels": "read from the published panel's target-day columns, after the fact, for scoring; never an input",
        },
        "interval": "stationary bootstrap, seed 1124, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "helps_on_settlement_days": "an arm helps over gbm_funding_cal_direct on coupon (bill-only) settlement days when the lower end of its grid-CRPS skill interval over gbm_funding_cal_direct on the settlement_coupon (settlement_bill) cut, at leads 2 to 5, is above 0",
            "does_not_lose_on_ordinary_days": "and its skill over gbm_funding_cal_direct on ordinary target days, at leads 2 to 5, has an upper interval end of 0 or more; 'loses' means an interval wholly below 0",
            "coupon_leg_against_the_aggregate": "the coupon leg alone is compared with the aggregate arm on the same cuts, by the same lower and upper ends",
            "publish": "whether the announcement dating is put in force is Eleonora's decision (an amendment to rule 2 of docs/decisions/information-set.md); this page does not decide it",
            "no_verdict": "development data gives no verdict",
        },
        "limits": [
            "no day after 2025-12-31",
            "no lockbox day",
            "no published record is edited",
            "no published declaration changes: metadata/sources.json and docs/decisions/information-set.md are unchanged",
            "no allow-list entry is added to repo_model.one_step_guard",
            "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed",
        ],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk ----------------------------------------------------------------------------------------------------------------


def _finished(output: Path, arm: str, h: int, published: Path, panel: Path) -> bool:
    """Whether `output` already holds this walk, from the same panel, dating and snapshot bytes (a stopped run keeps what it wrote)."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(document, dict) and isinstance(document.get("laws"), dict) and document.get("variant") == arm and document.get("horizon") == h
        and document.get("panel_sha256") == panel_sha256(published) and document.get("scratch_panel_sha256") == panel_sha256(panel)
        and document.get("dating_sha256") == sha256(DATING) and document.get("auctions_sha256") == sha256(SNAPSHOT)
    )


def walk_command(args) -> int:
    from repo_model import measurement_fields

    ac.committed_declaration(DECLARATION)
    sd = ac._load("spread_distribution_634")
    arm, h = args.arm, args.horizon
    if arm not in ARMS or h not in HORIZONS:
        raise SystemExit(f"arm {arm!r} / lead {h} is not declared")
    ac.require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="aligned_announcement_1124")
    if _finished(args.output, arm, h, args.published, args.panel):
        print(json.dumps({"arm": arm, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    plain = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(plain)
    rows, registry = arm_inputs(plain, measurement_fields.load_registry(), h)
    features = arm_features(arm, h)
    with ac._load("net_settlement").switched_on():
        result, levels, settings = sd.walk(
            rows, fit=arm_fit(arm, features), features=features, online_calibration=None, registry=registry,
            horizon=h, minimum_history=ac.MINIMUM_HISTORY, refit_every=ac.REFIT_EVERY, expected_levels=GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "dating_sha256": sha256(DATING), "auctions_sha256": sha256(SNAPSHOT), "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"arm": arm, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the reading rules (tested) ------------------------------------------------------------------------------------------------


def scored_arms(walks: Path) -> List[str]:
    """The arms, each with all five walks present; an arm with some leads only, or none, is an error and never a silent drop."""

    scored = []
    for arm in ARMS:
        present = [h for h in HORIZONS if (walks / f"{arm}_h{h}.json").is_file()]
        if len(present) == len(HORIZONS):
            scored.append(arm)
        elif present:
            raise ValueError(f"{arm} has walks for leads {present} only; walk every lead or none")
        else:
            raise ValueError(f"{arm} has no walks; both arms are declared and must be scored")
    return scored


def lead_1_identical(walks: Path, reference: Path, arm: str) -> bool:
    """Whether the arm's lead-1 walk equals `gbm_funding_cal_direct`'s (it must, the dated column being the published one at lead 1)."""

    ours = json.loads((Path(walks) / f"{arm}_h1.json").read_text(encoding="utf-8"))["laws"]
    theirs = json.loads((Path(reference) / f"{DIRECT}_h1.json").read_text(encoding="utf-8"))["laws"]
    return ours == theirs


def reading_rules(rows: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    """The declared sentences per arm from its paired grid-CRPS rows over `gbm_funding_cal_direct`, leads 2 to 5, on coupon-settlement, bill-only-settlement and ordinary days.

    `rows[arm]` maps "settlement_coupon", "settlement_bill" and "ordinary" to a paired row (`s761.paired_row`), an undefined one, or None (not scored).
    The lower end of a studentized two-sided 90% interval is the one-sided 95% lower bound.
    """

    s761 = ac._load("spread_mr_variants_761")
    out = []
    for arm, cells in rows.items():
        coupon, bill, ordinary = cells.get("settlement_coupon"), cells.get("settlement_bill"), cells.get("ordinary")
        if any(cell is None or "undefined" in cell for cell in (coupon, bill, ordinary)):
            out.append(f"{arm}: not read (a cut is not scored or undefined).")
            continue

        def help_text(cell, label):
            helps = cell["skill_interval"][0] > 0.0
            return (
                f"{'helps' if helps else 'is not shown to help'} on {label} settlement days (skill {s761.pct(cell['skill'])}, one-sided 95% lower bound "
                f"{s761.pct(cell['skill_interval'][0])})"
            )

        loses = ordinary["skill_interval"][1] < 0.0
        out.append(
            f"{arm} {help_text(coupon, 'coupon')}, {help_text(bill, 'bill-only')} and {'loses' if loses else 'does not lose'} on ordinary days "
            f"(skill {s761.pct(ordinary['skill'])}, interval {s761.pct(ordinary['skill_interval'][0])} to {s761.pct(ordinary['skill_interval'][1])}), "
            f"over {DIRECT}, leads 2 to 5."
        )
    return out


# -- the score --------------------------------------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _task(job):
    key, metric, candidate, benchmark, days = job
    series = _SERIES[(key[0], metric)]
    return key, metric, candidate, benchmark, _SERIES["s761"].run_pairs({benchmark: series[benchmark]}, series[candidate], days, seed=SEED, draws=_SERIES["draws"])[benchmark]


def _check_arm_walks(walks: Path, arm: str, panel: Path, published: Path) -> None:
    for h in HORIZONS:
        document = json.loads((walks / f"{arm}_h{h}.json").read_text(encoding="utf-8"))
        for key, path in (("panel_sha256", published), ("scratch_panel_sha256", panel), ("dating_sha256", DATING), ("auctions_sha256", SNAPSHOT)):
            current = panel_sha256(path) if key.endswith("panel_sha256") else sha256(path)
            if document.get(key) != current:
                raise ValueError(f"{arm}_h{h}.json was walked with {key} {document.get(key)}, not the current {current}")


def score_command(args) -> int:
    b960 = ac._load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = ac.committed_declaration(DECLARATION)
    published, panel_path, walks, reference = Path(args.published), Path(args.panel), Path(args.walks), Path(args.reference_walks)
    pub = load_daily_panel(published)
    splits = load_split_declaration(ac.SPLITS)
    registry = json.loads(ac.SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), reference)
    arms = scored_arms(walks)
    models = list(BENCHMARKS) + [CONTROL, ALIGNED, DIRECT] + arms
    for name in (ALIGNED, DIRECT):
        frame.forecasts[name] = ac.load_walks(reference, name, published, panel_path, frame)
    for arm in arms:
        _check_arm_walks(walks, arm, panel_path, published)
        frame.forecasts[arm] = ac.load_walks(walks, arm, published, panel_path, frame)
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in models)]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes["scored_decision_days"] = len(days)
    notes["lead_1_identical_to_gbm_funding_cal_direct"] = {arm: lead_1_identical(walks, reference, arm) for arm in arms}

    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in models}
    series: Dict = {}
    for window, leads in WINDOWS.items():
        for label, _ in METRICS:
            kept = {m: {k: v for k, v in cells[(label, m)].items() if k[1] in leads} for m in models}
            series[(f"decision:{window}", label)] = {m: s686.by_decision(kept[m]) for m in models}
            series[(f"target:{window}", label)] = {m: s686.by_target(frame, kept[m]) for m in models}
    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    types = {t: target_type(frame, t) for t in targets}
    labels = {"regime": {t: frame.regime(t) for t in targets}, "target_type": types}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    groups[("target_type", "calendar_days")] = ("target", [d for d in targets if types[d] in CALENDAR_TYPES])
    groups[("target_type", "settlement_any")] = ("target", [d for d in targets if types[d] in SETTLEMENT_TYPES])

    pairs = [(arm, benchmark) for arm in arms for benchmark in (ALIGNED, DIRECT, CONTROL) + BENCHMARKS] + [(ANN_COUPONS, ANN)]
    jobs, skipped, window_days = [], {}, {}
    for (split, label), (grain, members) in groups.items():
        for window in WINDOWS:
            # a target day reached only by a lead outside the window has no score in it: the window's group is the days it scores
            scored = series[(f"{grain}:{window}", METRICS[0][0])][CONTROL]
            kept = tuple(d for d in members if d in scored)
            if len(kept) < MIN_GROUP_DAYS:
                skipped[f"{split}/{label}/{window}"] = len(kept)
                continue
            window_days[(split, label, window)] = kept
            for metric, _ in METRICS:
                for candidate, benchmark in pairs:
                    jobs.append(((f"{grain}:{window}", f"{split}/{label}/{window}"), metric, candidate, benchmark, kept))
    _SERIES.update(series)
    _SERIES.update({"draws": args.draws, "s761": s761})
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        out = pool.map(_task, jobs, chunksize=1)

    result: dict = {
        "issue": 1124, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "dating_sha256": sha256(DATING), "auctions_sha256": sha256(SNAPSHOT), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "notes": notes, "models": models, "pairs": [list(p) for p in pairs], "windows": {k: list(v) for k, v in WINDOWS.items()},
        "means": {
            window: {label: {m: sum(series[(f"decision:{window}", label)][m].values()) / len(days) for m in models} for label, _ in METRICS} for window in WINDOWS
        },
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"],
    }
    for (grain_window, name), metric, candidate, benchmark, row in out:
        split, label, window = name.split("/", 2)
        members = window_days[(split, label, window)]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"windows": {}})
        ser = _SERIES[(grain_window, metric)]
        scored = entry["windows"].setdefault(window, {"days": len(members)})
        cell = scored.setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        cell["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(label, candidate, benchmark, window="h2_5"):
        entry = result["groups"].get("target_type", {}).get(label)
        return None if entry is None else entry["windows"].get(window, {}).get("grid_crps", {}).get("pairs", {}).get(f"{candidate} vs {benchmark}")

    result["reading_rules"] = reading_rules(
        {a: {cut: pick(cut, a, DIRECT) for cut in ("settlement_coupon", "settlement_bill", "ordinary")} for a in arms}
    )
    if ANN in arms and ANN_COUPONS in arms:
        result["reading_rules_coupon_leg_against_the_aggregate"] = reading_rules(
            {f"{ANN_COUPONS} (over {ANN})": {cut: pick(cut, ANN_COUPONS, ANN) for cut in ("settlement_coupon", "settlement_bill", "ordinary")}}
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
WINDOW_TITLES = {"h1_5": "mean over leads 1 to 5 (the protocol's figure)", "h2_5": "mean over leads 2 to 5 (the leads the arms differ at)"}
TYPE_ORDER = ("ordinary", "quarter_end", "month_end", "tax_date", "settlement_coupon", "settlement_bill", "settlement_any", "calendar_days")


def _group_order(label: str):
    if label in ORDER_REGIME:
        return (1, ORDER_REGIME.index(label))
    if label in TYPE_ORDER:
        return (0, TYPE_ORDER.index(label))
    return (2, 0)


def render_report(r: dict, s761) -> str:
    n = r["notes"]
    lines = [
        "# The #1027 direct variant with settlements dated from the auction announcement at leads 2 to 5 (#1124): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`, dating `{r['dating_sha256'][:12]}`, auctions `{r['auctions_sha256'][:12]}`. "
        f"Declaration `{r['declaration']}`. Seed {r['seed']}, {r['draws']} draws, the studentized stationary bootstrap. {n['scored_decision_days']} decision days, "
        "every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided "
        "95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. The announcement dating is measured "
        "and not in force; the arms read it through a scratch-only path. The cuts `settlement_any` and `calendar_days` overlap the exclusive day types. A settlement "
        "on a quarter-end, month-end or tax date is in that type, not in a settlement type.", "",
        f"Lead 1 of each arm equals `{DIRECT}`'s lead 1 (the dated column is the published one there): "
        + ", ".join(f"{a} {'yes' if ok else 'NO'}" for a, ok in n["lead_1_identical_to_gbm_funding_cal_direct"].items()) + ".", ""]
    for window, title in WINDOW_TITLES.items():
        lines += [f"## Mean scores, pooled: {title}", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"][window]) + " |", "|---|" + "---|" * len(r["means"][window])]
        for m in r["models"]:
            lines.append(f"| {m} | " + " | ".join(f"{r['means'][window][label][m]:.4f}" for label in r["means"][window]) + " |")
        lines.append("")
    lines += ["## Reading (declared rules)", "", "Over the matched control:", ""] + [f"- {s}" for s in r["reading_rules"]]
    lines += ["", "Coupon leg against the aggregate:", ""] + [f"- {s}" for s in r.get("reading_rules_coupon_leg_against_the_aggregate", [])]
    lines += ["", "Whether the announcement dating is put in force is Eleonora's decision; this page does not decide it.", ""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for window, title in WINDOW_TITLES.items():
            lines += [f"### {title}", ""]
            for split in SPLIT_TITLES:
                if split not in r["groups"]:
                    continue
                lines += [f"#### {SPLIT_TITLES[split]}", ""]
                names = [f"{c} vs {b}" for c, b in r["pairs"]]
                lines += ["| group | days | " + " | ".join(p.replace(" vs ", " over ") for p in names) + " |", "|---|---|" + "---|" * len(names)]
                for label in sorted(r["groups"][split], key=_group_order):
                    entry = r["groups"][split][label]
                    scored = entry["windows"].get(window, {})
                    row_cells = scored.get(metric, {}).get("pairs", {})
                    lines.append(f"| {label} | {scored.get('days', 0):,} | " + " | ".join(s761.skill_text(row_cells[p]) if p in row_cells else "n/a" for p in names) + " |")
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
    score.add_argument("--reference-walks", type=Path, required=True, help="the directory of #1027's walks: gbm_funding and the two variants")
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
