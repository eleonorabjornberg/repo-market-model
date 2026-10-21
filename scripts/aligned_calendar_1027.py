"""gbm_funding with every calendar and scheduled column read from the target row at every lead: two declared variants (#1027, H5 step 3/4 re-run).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no published figure. Every choice
is in `metadata/aligned_calendar_1027.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from the
constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**The design.** `asof.py` rule 2 serves a calendar column, and every field a source lists under `scheduled_availability`, from the *target* row of a
forecast (`served_columns`). A pair trains what it will be served: in the pair whose target is row t, those columns must be row t's. Two variants,
both fitted at `gbm_funding`'s settings except the leaf (`LEAF`, 5: `docs/research/drivers-audit-951-result.md` §2 shows 78 of 90 refits hold five
quarter-end days and only 33 hold twenty), on the same inputs at every lead (`variant_features`): `gbm_funding`'s published inputs at the lead, plus
`TARGET_ROW_COLUMNS` (read from the target row) and the observed `net_settlement`, `net_settlement_due_5d` (read as of the decision instant).

* `gbm_funding_cal_aligned` (i): the one-step pairs of `gbm_funding` (the pair of row p is `(p, p + 1)`, at every lead, as the current fit trains it),
  on the frame with each `TARGET_ROW_COLUMNS` column of row p replaced by row p + 1's (`align_columns`, #931's `align_field` for several columns). The
  observed columns of row p are untouched. Serving is the as-of rule's, unchanged.
* `gbm_funding_cal_direct` (ii): the same inputs, trained on #951's direct pairs (`training_pairs="direct"`): each target is paired with its own
  as-of read, so every column is trained from the row it is served from by construction.

The only difference between the variants is the pairing; the leaf, seed, fold grid, refit cadence (21 scored days, 61 minimum history) and quantile
grid are `gbm_funding`'s and #951's. The scratch panel is #951's `AUG3` (`gbm_funding`'s published columns plus the net-settlement columns).

**The #947 guard.** `repo_model.one_step_guard` refuses a calendar or scheduled regressor on any one-step fit, whether or not the frame was aligned, and its
allow-list is pinned and Eleonora's. Variant (ii) passes it (direct pairs are not checked). Variant (i) is admitted by two entries (lead 1; leads 2 to 5,
which share one set of inputs), allowed by Eleonora on 21 October 2026 and ending on 15 November 2026. An entry matches the fitter and the regressors, not
the frame, so before every fit `require_aligned` refuses a frame whose target-row columns are not the next row's: the exemption covers the aligned fit only.

The walks are long (`needs-mac`, #46); `score` reads them. The reference walks of `gbm_funding` are #634's (`spread_distribution_634.py walk`).

    # PUB.csv: the published panel (digest 4ddc3882...); AUG3.csv: #951's scratch panel (see scripts/drivers_audit_951.py's docstring)
    PYTHONPATH=src python3 scripts/aligned_calendar_1027.py declare            # then commit metadata/aligned_calendar_1027.json before any score
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published PUB.csv --panel PUB.csv --output WALKS/gbm_funding_h$h.json
        for v in gbm_funding_cal_aligned gbm_funding_cal_direct:
            OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_calendar_1027.py walk --variant $v --horizon $h \\
                --published PUB.csv --panel AUG3.csv --output WALKS/${v}_h$h.json
    PYTHONPATH=src python3 scripts/aligned_calendar_1027.py score --published PUB.csv --panel AUG3.csv --walks WALKS \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import multiprocessing
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


from repo_model import ml, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "aligned_calendar_1027.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 1027
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
HORIZONS = sp.HORIZONS
GRID = sp.GRID
#: the leaf size that lets a tree put five quarter-end days alone on one side of a split (#951 §2)
LEAF = 5

CONTROL = "gbm_funding"
ALIGNED = "gbm_funding_cal_aligned"
DIRECT = "gbm_funding_cal_direct"
VARIANTS = (ALIGNED, DIRECT)
#: read from the target row of each pair (served from it by rule 2 of `asof.py`); `treasury_settlement_*` are scheduled fields of the auction source
TARGET_ROW_COLUMNS = (
    "quarter_end", "days_to_month_end", "tax_date", "treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills",
)
#: the scheduled settlement columns among them: announced one business day ahead (15:00 the day before, `metadata/sources.json` `treasury_auctions`), so only a
#: lead-1 decision can read them; at a longer lead `asof.InformationRule.check` raises `LookAheadError` (`gbm_funding` already drops `treasury_settlement` at h > 1)
SETTLEMENT_COLUMNS = ("treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills")
#: observed columns (dated at their own day), read as of the decision instant; added to `gbm_funding`'s inputs by this directive
OBSERVED_COLUMNS = ("net_settlement", "net_settlement_due_5d")
CTX = "spread_mr_ctx"
B1P = "B1_prime"
BENCHMARKS = ("B1", B1P, "B2", CTX)
METRICS = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
#: the calendar day types of the reading rule (the target day's reporting day type, or a coupon or bill settlement on an otherwise ordinary day)
CALENDAR_TYPES = ("quarter_end", "month_end", "tax_date", "settlement")
ORDER_REGIME = ["2018-19", "2020", "2021-23", "2024", "2025-26"]
MIN_GROUP_DAYS = 20


def decision_time():
    return _load("spread_distribution_634").DECISION


def __getattr__(name):  # DECISION, read lazily: #634's script loads the whole scoring stack
    if name == "DECISION":
        return decision_time()
    raise AttributeError(name)


# -- the declaration and the guards ----------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"aligned_calendar_1027 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the variants ----------------------------------------------------------------------------------------------------


def served_columns() -> FrozenSet[str]:
    """The panel columns rule 2 of `asof.py` serves from the target row: the calendar columns and every column of a scheduled field."""

    from repo_model import contract

    return _load("drivers_audit_951").served_from_target(json.loads(SOURCES.read_text(encoding="utf-8")), frozenset(contract.CALENDAR_FEATURES))


def align_columns(frame: Sequence[DailyObservation], fields: Sequence[str] = TARGET_ROW_COLUMNS) -> List[DailyObservation]:
    """The frame with each of `fields` on row p replaced by row p + 1's, so the one-step pair (p, p + 1) trains them from the target's row.

    Every other column of every row, and every date, is the frame's own. The last row has no successor in the frame and is no origin of a pair; its
    `fields` are made holes rather than left as values of the wrong day.

    Raises:
        ValueError: a field the frame's rows do not carry (a misspelt column would be aligned to nothing and trained from row p silently).
    """

    rows = list(frame)
    for field in fields:
        if rows and field not in rows[0].values:
            raise ValueError(f"column {field!r} is not in the frame; there is nothing to align")
    aligned = []
    for position, row in enumerate(rows):
        values = dict(row.values)
        for field in fields:
            values[field] = rows[position + 1].values.get(field) if position + 1 < len(rows) else None
        aligned.append(DailyObservation(date=row.date, values=values))
    return aligned


def require_aligned(frame: Sequence[DailyObservation], aligned: Sequence[DailyObservation], fields: Sequence[str] = TARGET_ROW_COLUMNS) -> None:
    """Refuse to fit the one-step variant on a frame whose `fields` on row p are not `frame`'s row p + 1 (the guard's exemption assumes they are).

    Raises:
        ValueError: a row whose date or one of whose `fields` differs from what `align_columns` makes of `frame`, naming the first.
    """

    rows, shifted = list(frame), list(aligned)
    if [r.date for r in rows] != [r.date for r in shifted]:
        raise ValueError("the aligned frame's dates are not the frame's; every row must keep its own date")
    for position, row in enumerate(shifted):
        for field in fields:
            if field not in row.values:
                continue
            expected = rows[position + 1].values.get(field) if position + 1 < len(rows) else None
            if row.values[field] != expected:
                raise ValueError(
                    f"{field!r} on {row.date} is not the next row's value: the frame is not aligned, so the one-step fit "
                    "would train it one day off (#914) and #947's exemption does not cover it"
                )


def target_row_columns(horizon: int) -> Tuple[str, ...]:
    """The `TARGET_ROW_COLUMNS` a decision at `horizon` can read: the calendar columns at every lead, the scheduled settlement columns at lead 1."""

    return tuple(c for c in TARGET_ROW_COLUMNS if horizon == 1 or c not in SETTLEMENT_COLUMNS)


def regressors(features: Sequence[str]) -> Tuple[str, ...]:
    return tuple(name for name in features if name != "spread_bps")


def variant_features(variant: str, horizon: int) -> Tuple[str, ...]:
    """The inputs of both variants at a lead: `gbm_funding`'s published inputs, then the target-row columns, then the observed ones, none twice."""

    if variant not in VARIANTS:
        raise ValueError(f"{variant!r} is not a declared variant")
    base = tuple(_load("live_record").published_features(horizon))
    return base + tuple(c for c in target_row_columns(horizon) + OBSERVED_COLUMNS if c not in base)


def variant_fit(variant: str, features: Sequence[str]):
    """The variant's fitter: `gbm_funding`'s gbm at `LEAF`; one-step pairs on the aligned frame (i), or direct pairs (ii)."""

    names = regressors(features)
    if variant == DIRECT:
        return functools.partial(ml.fit_gradient_boosted_quantiles, regressors=names, levels=GRID, min_samples_leaf=LEAF, training_pairs="direct")
    if variant != ALIGNED:
        raise ValueError(f"{variant!r} is not a declared variant")

    def fit(train_frame, minimum_history):
        aligned = align_columns(train_frame)
        require_aligned(train_frame, aligned)
        return ml.fit_gradient_boosted_quantiles(
            aligned, regressors=names, levels=GRID, minimum_history=minimum_history, min_samples_leaf=LEAF
        )

    return fit


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1027 before any number was computed; a measurement, not a record. Nothing is published: neither variant joins any published declaration, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1027,
        "hypothesis": "H5 step 3/4, re-run on aligned pairs (#914 class; #951)",
        "ruling": "Eleonora, 20 October 2026, relayed by the orchestrating session: a model that does not read calendar days at the target day is wrong; the calendar fix comes first",
        "variants": {
            ALIGNED: {
                "947_guard": "refused by repo_model.one_step_guard until its pinned allow-list (Eleonora's) has an entry for each lead's regressors; variant (ii) passes",
                "pairing": "one-step pairs (p, p + 1) of gbm_funding's current fit, at every lead, on the frame whose target-row columns are row p + 1's (align_columns)",
                "training_pairs": None,
                "min_samples_leaf": LEAF,
            },
            DIRECT: {
                "pairing": "#951's direct pairs: each target is paired with its own as-of read",
                "training_pairs": "direct",
                "min_samples_leaf": LEAF,
            },
        },
        "inputs": {
            "base": "gbm_funding's published inputs at the lead (scripts/live_record.py published_features), each read as of the decision instant",
            "target_row": list(TARGET_ROW_COLUMNS),
            "target_row_by_lead": {"1": list(target_row_columns(1)), "2 to 5": list(target_row_columns(2)), "why": "the scheduled settlement columns are public at 15:00 the business day before the target (sources.json treasury_auctions), so a decision at lead 2 or more cannot read them: asof.InformationRule.check raises LookAheadError. The directive's wording, every column at every lead, is read as 'every column the information set allows' (a marked question on the pull request)"},
            "observed_added": list(OBSERVED_COLUMNS),
            "rule": "asof.py rule 2: the target_row columns are served from the target row (the calendar columns at every lead h = 1 to 5, the settlement columns at h = 1); the one-step pair (p, p + 1) trains them from row p + 1, a direct pair from its own target; the observed_added columns are dated at their own day and read as of the decision instant",
            "panel": "#951's scratch panel AUG3 (the published columns plus scripts/net_settlement.py panel); the reference walks of gbm_funding are #634's on the published panel",
        },
        "settings": {
            "as_gbm_funding": ["seed", "quantile grid", "refit every 21 scored days", "minimum history 61", "n_estimators and depth of ml.fit_gradient_boosted_quantiles"],
            "except": {"min_samples_leaf": f"{LEAF} instead of 20: #951 section 2 shows 78 of 90 refits hold five quarter-end days against 33 for twenty; #951 tested 5 and 20 only, so 10 is untested"},
        },
        "benchmarks": ["gbm_funding", "B1", "B1_prime", "B2", CTX],
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "settlement": "a target day whose reporting day type is ordinary and whose treasury_settlement_coupons or treasury_settlement_bills is above 0",
            "calendar_days": list(CALENDAR_TYPES),
        },
        "interval": "stationary bootstrap, seed 1027, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "reads_calendar_days_and_beats": "a variant beats gbm_funding on calendar days when the lower end of its grid-CRPS skill interval over gbm_funding on the calendar_days cut (the union of the calendar types) is above 0",
            "without_losing_on_ordinary_days": "and its skill over gbm_funding on ordinary target days has an upper interval end of 0 or more; 'loses' means an interval wholly below 0",
            "replacement": "naming the variant that reads calendar days and does not lose is a marked question for Eleonora; replacing the candidate is hers",
            "no_verdict": "development data gives no verdict",
        },
        "limits": ["no day after 2025-12-31", "no lockbox day", "no published record is edited", "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk --------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    from repo_model import measurement_fields

    committed_declaration()
    sd = _load("spread_distribution_634")
    variant, h = args.variant, args.horizon
    if variant not in VARIANTS or h not in HORIZONS:
        raise SystemExit(f"variant {variant!r} / lead {h} is not declared")
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="aligned_calendar_1027")
    if _finished(args.output, variant, h, args.published, args.panel):
        print(json.dumps({"variant": variant, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    features = variant_features(variant, h)
    with _load("net_settlement").switched_on():
        result, levels, settings = sd.walk(
            rows, fit=variant_fit(variant, features), features=features, online_calibration=None, registry=measurement_fields.load_registry(),
            horizon=h, minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY, expected_levels=GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": variant, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


def _finished(output: Path, variant: str, h: int, published: Path, panel: Path) -> bool:
    """Whether `output` already holds this walk, from the same panel bytes (a walk takes hours; a stopped run keeps what it wrote)."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(document, dict) and isinstance(document.get("laws"), dict) and document.get("variant") == variant and document.get("horizon") == h
        and document.get("panel_sha256") == panel_sha256(published) and document.get("scratch_panel_sha256") == panel_sha256(panel)
    )


# -- the reading rules (tested) ---------------------------------------------------------------------------------------


def reading_rules(rows: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    """The declared sentences per variant, from its paired grid-CRPS rows over gbm_funding on `calendar` and `ordinary` target days.

    `rows[variant]` maps "calendar" and "ordinary" to a paired row (`s761.paired_row`), an undefined one, or None (not scored). The lower end of a
    studentized two-sided 90% interval is the one-sided 95% lower bound.
    """

    s761 = _load("spread_mr_variants_761")
    out = []
    for variant, cells in rows.items():
        calendar, ordinary = cells.get("calendar"), cells.get("ordinary")
        if calendar is None or ordinary is None or "undefined" in calendar or "undefined" in ordinary:
            out.append(f"{variant}: not read (a cut is not scored or undefined).")
            continue
        beats = calendar["skill_interval"][0] > 0.0
        loses = ordinary["skill_interval"][1] < 0.0
        out.append(
            f"{variant} {'beats' if beats else 'is not shown to beat'} gbm_funding on calendar days (skill {s761.pct(calendar['skill'])}, one-sided 95% lower bound "
            f"{s761.pct(calendar['skill_interval'][0])}) and {'loses' if loses else 'does not lose'} on ordinary days (skill {s761.pct(ordinary['skill'])}, "
            f"interval {s761.pct(ordinary['skill_interval'][0])} to {s761.pct(ordinary['skill_interval'][1])})."
        )
    return out


def target_type(frame, day: date) -> str:
    """The target day's reporting day type, with a settlement on an otherwise ordinary day called `settlement`."""

    kind = frame.day_type(day)
    if kind != "ordinary":
        return kind
    values = frame.values[day]
    if any((values.get(c) or 0.0) > 0.0 for c in ("treasury_settlement_coupons", "treasury_settlement_bills")):
        return "settlement"
    return kind


# -- the frame and the scoring -----------------------------------------------------------------------------------------

_SERIES: Dict = {}


def load_walks(walks: Path, name: str, published: Path, panel: Path, frame) -> Dict[date, Dict[int, List[float]]]:
    """A model's forecast on each decision day its five walks cover, a missing lead standing in as B1, as #634 and #960 fill it."""

    sd = _load("spread_distribution_634")
    for h in HORIZONS:
        document = json.loads((walks / f"{name}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("panel_sha256") != panel_sha256(published):
            raise ValueError(f"{name}_h{h}.json was walked from published panel {document.get('panel_sha256')}, not {panel_sha256(published)}")
        if name in VARIANTS and document.get("scratch_panel_sha256") != panel_sha256(panel):
            raise ValueError(f"{name}_h{h}.json was walked from scratch panel {document.get('scratch_panel_sha256')}, not {panel_sha256(panel)}")
    decisions, walked = sd.lead_forecasts(sd.load_laws(walks, name), frame.dates)
    usable = [d for d in walked if frame.target(d, max(HORIZONS)) <= LAST_TARGET and d in frame.forecasts["B1"]]
    sd.refuse_locked(usable + [frame.target(d, h) for d in usable for h in HORIZONS])
    return sp.fill_missing({d: decisions[d] for d in usable}, {d: frame.forecasts["B1"][d] for d in usable}, usable).forecasts


def _task(job):
    key, metric, candidate, benchmark, days = job
    s761 = _SERIES["s761"]
    series = _SERIES[(key[0], metric)]
    return key, metric, candidate, benchmark, s761.run_pairs({benchmark: series[benchmark]}, series[candidate], days, seed=SEED, draws=_SERIES["draws"])[benchmark]


def scored_variants(walks: Path) -> Tuple[List[str], Dict[str, str]]:
    """The variants whose five walks exist, and why any other is not run.

    The aligned one-step variant may be absent: `repo_model.one_step_guard` (#947) refuses it until Eleonora admits it by an allow-list entry, so its walks
    write nothing. The direct variant may not be absent, and a variant with some leads walked and others not is an error, never a silent drop (Eleonora,
    21 October 2026: score the direct variant against the control, the aligned one reported as not run).
    """

    scored, not_run = [], {}
    for variant in VARIANTS:
        present = [h for h in HORIZONS if (walks / f"{variant}_h{h}.json").is_file()]
        if len(present) == len(HORIZONS):
            scored.append(variant)
        elif present:
            raise ValueError(f"{variant} has walks for leads {present} only; walk every lead or none")
        elif variant == ALIGNED:
            not_run[variant] = "not run: refused by repo_model.one_step_guard (#947) until Eleonora admits it by an allow-list entry per lead"
        else:
            raise ValueError(f"{variant} has no walks; the direct variant is the one calendar first asks for and must be scored")
    return scored, not_run


def score_command(args) -> int:
    b960 = _load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = committed_declaration()
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    pub = load_daily_panel(published)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), walks)
    models = list(BENCHMARKS) + [CONTROL]
    variants, not_run = scored_variants(walks)
    for variant in variants:
        forecasts = load_walks(walks, variant, published, panel_path, frame)
        frame.forecasts[variant] = forecasts
        models.append(variant)
    days = [d for d in frame.days if all(d in frame.forecasts[m] for m in models)]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    notes["scored_decision_days"] = len(days)

    cells = {(label, m): s686.cell_scores(frame, m, fn) for label, fn in METRICS for m in models}
    series: Dict = {}
    for label, _ in METRICS:
        series[("decision", label)] = {m: s686.by_decision(cells[(label, m)]) for m in models}
        series[("target", label)] = {m: s686.by_target(frame, cells[(label, m)]) for m in models}
    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    labels = {"regime": {t: frame.regime(t) for t in targets}, "target_type": {t: target_type(frame, t) for t in targets}}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    calendar_days = [d for d in targets if labels["target_type"][d] in CALENDAR_TYPES]
    groups[("target_type", "calendar_days")] = ("target", calendar_days)

    pairs = [(v, b) for v in variants for b in (CONTROL,) + BENCHMARKS] + ([(ALIGNED, DIRECT)] if ALIGNED in variants else [])
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
        "issue": 1027, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models, "pairs": [list(p) for p in pairs],
        "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in models} for label, _ in METRICS},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"], "not_run": not_run,
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = _SERIES[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(label, candidate):
        return result["groups"].get("target_type", {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{candidate} vs {CONTROL}")

    result["reading_rules"] = reading_rules({v: {"calendar": pick("calendar_days", v), "ordinary": pick("ordinary", v)} for v in variants})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


# -- Markdown --------------------------------------------------------------------------------------------------------

METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}
SPLIT_TITLES = {"pooled": "pooled (decision days)", "regime": "regime (target day)", "target_type": "target day type"}


def render_report(r: dict, s761) -> str:
    n = r["notes"]
    lines = [
        "# gbm_funding with calendar and scheduled columns read from the target row (#1027): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`. Declaration `{r['declaration']}`. Seed {r['seed']}, {r['draws']} draws, "
        f"the studentized stationary bootstrap. {n['scored_decision_days']} decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); "
        "positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 "
        "standard error behind the block length is noisy on this many days.", "",
        "## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {m} | " + " | ".join(f"{r['means'][label][m]:.4f}" for label in r["means"]) + " |")
    lines += ["", "## Reading (declared rules)", ""] + [f"- {s}" for s in r["reading_rules"]]
    lines += [f"- {v}: {why}." for v, why in sorted(r.get("not_run", {}).items())]
    lines += ["", "Replacing the candidate is a marked question for Eleonora; this page does not decide it.", ""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            lines += [f"### {SPLIT_TITLES[split]}", ""]
            names = [f"{c} vs {b}" for c, b in r["pairs"]]
            lines += ["| group | days | " + " | ".join(f"{p.replace(' vs ', ' over ')}" for p in names) + " |", "|---|---|" + "---|" * len(names)]
            for label in sorted(r["groups"][split], key=lambda l: ORDER_REGIME.index(l) if l in ORDER_REGIME else (-1 if l == "ordinary" else 99)):
                entry = r["groups"][split][label]
                cells = entry["metrics"].get(metric, {}).get("pairs", {})
                lines.append(f"| {label} | {entry['days']:,} | " + " | ".join(s761.skill_text(cells[p]) if p in cells else "n/a" for p in names) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += ["Groups of fewer than %d days, listed and not tested: " % MIN_GROUP_DAYS + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(run=declare_command)
    walk = sub.add_parser("walk")
    walk.add_argument("--variant", required=True, choices=VARIANTS)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(run=walk_command)
    score = sub.add_parser("score")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--workers", type=int, default=4)
    score.set_defaults(run=score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
