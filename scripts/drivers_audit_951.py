"""Why do known repo-market drivers add nothing? An audit of the "no gain" results and one declared re-run (#951, H5 step 4 and H2).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model and no published figure. Every choice, the reading rules included,
is in `metadata/drivers_audit_951.json`, which `walk`, `score`, `ceiling-fit` and `ceiling-score` refuse to read unless it is committed and unchanged;
`declare` writes it from the constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no
day of a locked tier is read (`docs/decisions/lockbox.md`).

The four suspects (Eleonora's ruling on #951, 19 October 2026):

1. the all-inputs ceiling of H2 scores below the reachable model (`ceiling-fit`, `ceiling-score`);
2. calendar and scheduled inputs trained one day off (`audit`);
3. `min_samples_leaf=20` and the rare days a tree can split on (`rare`);
4. dilution of the calendar-day gain in the pooled test (`score`, the calendar-day cells).

Then the declared re-run: `gbm_funding` with and without the calendar and net-settlement inputs, on aligned (direct) training pairs, at a leaf size
that can split on rare days (`walk`, `score`).

    # PUB.csv: the published panel (digest 4ddc3882...); AUG2D.csv: the scratch panel of scripts/spread_distribution_634.py's docstring;
    # AUG3.csv: AUG2D.csv with the net settlement columns; DERIV.csv: H2's scratch panel (scripts/deriv_chain_903.py run)
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/net_settlement.py panel --panel AUG2D.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/drivers_audit_951.py declare            # then commit metadata/drivers_audit_951.json before any score
    PYTHONPATH=src python3 scripts/drivers_audit_951.py audit --output OUT/audit.json
    PYTHONPATH=src python3 scripts/drivers_audit_951.py rare --published PUB.csv --panel AUG3.csv --output OUT/rare.json
    for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
        for a in <each arm of ARMS>: PYTHONPATH=src python3 scripts/drivers_audit_951.py walk --arm $a --horizon $h --published PUB.csv --panel AUG3.csv --output OUT/${a}_h$h.json
    PYTHONPATH=src python3 scripts/drivers_audit_951.py score --published PUB.csv --panel AUG3.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/drivers_audit_951.py report OUT/score.json --audit OUT/audit.json --rare OUT/rare.json --output OUT/report.md
    # the ceiling re-fit is long (needs-mac, #46): PYTHONPATH=src python3 scripts/drivers_audit_951.py ceiling-fit --panel DERIV.csv --output OUT/ceiling_fits.json
    PYTHONPATH=src python3 scripts/drivers_audit_951.py ceiling-score --published PUB.csv --fits OUT/ceiling_fits.json --output OUT/ceiling_score.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import multiprocessing
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date, time
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "drivers_audit_951.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 951
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 2_000
MINIMUM_DAYS = 30
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
HORIZONS = sp.HORIZONS
GRID = sp.GRID

#: how a fit pairs a target with its design row
ONE_STEP = "one_step"  # the target of row p + 1 is paired with the design of row p
DIRECT = "direct"  # `training_pairs="direct"`: the target is paired with its own as-of read
AS_OF_READ = "as_of_read"  # the design of each target is read as of its own decision instant (H2's study)
PAIRINGS = (ONE_STEP, DIRECT, AS_OF_READ)

CONTROL = "gbm_funding"
#: the calendar and net-settlement inputs added to the published funding inputs (the issue's "calendar and net-settlement inputs")
CALENDAR_INPUTS = ("quarter_end", "tax_date", "days_to_month_end", "net_settlement", "net_settlement_due_5d")
#: every arm is fitted on direct pairs; a name says its inputs and its leaf size
ARMS: Dict[str, dict] = {
    "direct_base_leaf20": {"inputs": "base", "min_samples_leaf": 20, "training_pairs": DIRECT},
    "direct_base_leaf5": {"inputs": "base", "min_samples_leaf": 5, "training_pairs": DIRECT},
    "direct_cal_leaf20": {"inputs": "calendar", "min_samples_leaf": 20, "training_pairs": DIRECT},
    "direct_cal_leaf5": {"inputs": "calendar", "min_samples_leaf": 5, "training_pairs": DIRECT},
}
#: (first, second): the second is read against the first; the first pair is the key comparison
KEY_COMPARISONS = (
    ("direct_base_leaf5", "direct_cal_leaf5"),
    ("direct_base_leaf20", "direct_cal_leaf20"),
    ("direct_base_leaf20", "direct_base_leaf5"),
    ("direct_cal_leaf20", "direct_cal_leaf5"),
    (CONTROL, "direct_base_leaf20"),
    (CONTROL, "direct_cal_leaf5"),
)
KEY_COMPARISON = KEY_COMPARISONS[0]
#: a rare-day group and how it is flagged on the scratch panel
RARE_GROUPS = ("quarter_end", "tax_date", "month_end")
LEAF_SIZES = (20, 10, 5)
#: day types a result is reported by (`EvaluationSplits.reporting_day_type`), the calendar ones among them
CALENDAR_KINDS = ("quarter_end", "month_end", "tax_date")
COUPON_SETTLEMENT = "coupon settlement"
CALENDAR_DAYS = "calendar days"

#: the families of the nested ceiling: column name prefixes, in the order a column is assigned to the first that matches
FAMILIES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("calendar", ("quarter_end", "tax_date", "days_to_month_end")),
    ("net settlement", ("net_settlement", "treasury_settlement")),
    ("reserves and TGA", ("reserve", "tga", "satiation", "bank_total_assets")),
    ("rates and volumes", ("sofr", "tgcr", "bgcr", "effr", "tbill", "ofr_", "dealer")),
    ("policy and facilities", ("policy_", "iorb", "fed_repo", "on_rrp", "srf_")),
)
OTHER_FAMILY = "other"


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
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def require_study_window(days: Sequence[date]) -> None:
    """Refuse a run that would read a day after 2025-12-31: raises `LookAheadError`."""

    late = [day for day in days if day > LAST_TARGET]
    if late:
        raise LookAheadError(f"drivers_audit_951 reads no day after {LAST_TARGET}; asked for {min(late)}")


# -- the pure parts: alignment --------------------------------------------------------------------------------------


def load_sources() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def contract_calendar() -> FrozenSet[str]:
    return frozenset(contract.CALENDAR_FEATURES)


def served_from_target(sources: Mapping[str, Mapping], calendar: FrozenSet[str], feature_fields: Optional[Mapping] = None) -> FrozenSet[str]:
    """The columns rule 2 of `asof.py` serves from the target row itself: the calendar columns and every field a source lists under
    `scheduled_availability`."""

    feature_fields = contract.FEATURE_FIELDS if feature_fields is None else feature_fields
    scheduled = set()
    for source_id, source in sources.items():
        block = source.get("scheduled_availability")
        if block:
            fields = set(block.get("fields", ()))
            scheduled.update(fields)
            # a panel column is served from the target row when its (source, field) is scheduled
            scheduled.update(column for column, pairs in feature_fields.items() if any(s == source_id and f in fields for s, f in pairs))
    return frozenset(calendar) | frozenset(scheduled)


def misaligned_columns(columns: Sequence[str], pairing: str, *, served_from_target: FrozenSet[str]) -> List[str]:
    """The columns a fit trains from a different row than the one it serves them from.

    A one-step fit pairs the target of row p + 1 with the design of row p, so a column served from the target row is learned one day off. A fit on
    direct pairs, or on a design read as of each target's own decision instant, trains and serves such a column from the same row.
    """

    if pairing not in PAIRINGS:
        raise ValueError(f"unknown pairing {pairing!r}; one of {', '.join(PAIRINGS)}")
    if pairing == ONE_STEP:
        return [c for c in columns if c in served_from_target]
    return []


# -- the pure parts: rare days --------------------------------------------------------------------------------------


def month_end_flags(days_to_month_end: Sequence[Optional[float]]) -> List[bool]:
    """A row is a month-end row when its `days_to_month_end` is 0."""

    return [value is not None and float(value) == 0.0 for value in days_to_month_end]


def count_in_window(flags: Sequence[bool], anchor: int, trainable: Optional[Sequence[bool]] = None) -> int:
    """The flagged rows among the training rows of a refit: the rows at or before `anchor` (the last row public at the block's first decision
    instant) that have a label."""

    return sum(1 for i, flag in enumerate(flags[: anchor + 1]) if flag and (trainable is None or trainable[i]))


def can_split_alone(count: int, min_samples_leaf: int) -> bool:
    """Whether a tree can put only these days on one side of a split: both children need `min_samples_leaf` rows, so a group
    smaller than a leaf is always mixed with other days."""

    return count >= min_samples_leaf


# -- the pure parts: subsets and intervals --------------------------------------------------------------------------


def calendar_subset(kinds: Mapping[date, str]) -> set:
    """The days whose reporting type is a calendar one (quarter-end, month-end, tax date)."""

    return {day for day, kind in kinds.items() if kind in CALENDAR_KINDS}


def interval_width(interval: Optional[Sequence[float]]) -> Optional[float]:
    return None if interval is None else interval[1] - interval[0]


def percentile_interval(draws: Sequence[float]) -> Optional[List[float]]:
    from repo_model.metrics import _quantile

    ordered = sorted(draws)
    return [_quantile(ordered, 0.05), _quantile(ordered, 0.95)] if ordered else None


def family_of(column: str) -> str:
    for name, prefixes in FAMILIES:
        if any(column.startswith(prefix) for prefix in prefixes):
            return name
    return OTHER_FAMILY


def family_columns(columns: Sequence[str]) -> Dict[str, List[str]]:
    """Each input column assigned to the first family whose prefix matches; every column is in exactly one."""

    out: Dict[str, List[str]] = {}
    for column in columns:
        out.setdefault(family_of(column), []).append(column)
    return out


def ceiling_lineup(columns: Sequence[str], candidate_columns: Sequence[str]) -> Dict[str, dict]:
    """The declared ceilings. `all inputs, generous` is H2's (rerun by `scripts/upper_bound_635.py fit`, not here). Each entry here is cross-fitted:
    `all inputs, reachable settings`; the candidate's own inputs at the reachable settings (the nested floor, which a ceiling must not score
    below by construction); and the candidate's inputs plus one family at a time, at the reachable settings. The ceiling read is the best of the
    entries by CRPS on the walk-forward ordinary days, the candidate's own inputs among them."""

    present = [c for c in columns if c not in candidate_columns]
    out = {
        "candidate inputs": {"columns": list(candidate_columns), "settings": "reachable"},
        "all inputs, reachable settings": {"columns": list(columns), "settings": "reachable"},
    }
    for family, members in family_columns(present).items():
        out[f"candidate + {family}"] = {"columns": list(candidate_columns) + members, "settings": "reachable"}
    return out


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #951 before any number was computed; a measurement, not a record. Nothing is published: no arm joins any published declaration, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 951,
        "hypothesis": "H5 step 4 (re-examining #775/#758) and H2 (the ceiling, #703/#635)",
        "ruling": "Eleonora, 19 October 2026, on the fixed-income reviews of main at 362df84 (relayed on #951)",
        "protocol": {
            "scorer": "repo_model.scoring_protocol (grid_crps, day_scores, fill_missing, paired_tests) and repo_model.protocol_benchmarks (b1_forecast, b2_forecast)",
            "primary_score": "grid CRPS averaged with equal weight over h = 1 to 5, one number per decision day",
            "difference": "d = S(first) - S(second); positive favours the second; skill = mean(d) / mean(S(first))",
            "interval": f"stationary bootstrap, {HEADLINE_DRAWS} draws for pooled cells and {SPLIT_DRAWS} for the others, seed {SEED}; the 90% interval is the 5th to 95th percentile of the skill draws",
            "first_day_rule": "a decision day is scored when every one of its five target days is on or before 2025-12-31 and has a published outcome",
        },
        "arms": {name: dict(arm) for name, arm in ARMS.items()},
        "control": CONTROL,
        "inputs": {
            "base": "the published funding declaration's features at the lead (scripts/live_record.py published_features), spread_bps among them as the as-of spread",
            "calendar": "base plus " + ", ".join(CALENDAR_INPUTS),
            "panel": "the scratch panel AUG3.csv of scripts/spread_distribution_634.py's docstring plus scripts/net_settlement.py panel; the base columns are the published panel's, read with the plain registry",
        },
        "training_pairs": "direct (ml.TRAINING_PAIRS): each target is paired with its own as-of read, so a calendar or scheduled column is trained from the row it is served from",
        "leaf_sizes": list(LEAF_SIZES),
        "leaf_rule": "20 is ml.fit_gradient_boosted_quantiles' default; 5 is the smaller leaf, declared as the setting that can put a rare-day group alone on one side of a split once the training window holds 5 of them",
        "key_comparison": list(KEY_COMPARISON),
        "comparisons": [list(pair) for pair in KEY_COMPARISONS],
        "benchmarks": ["B1", "B2", CONTROL],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ["2018-19", "2020", "2021-23", "2024", "2025-26"],
            "day_types": list(CALENDAR_KINDS) + ["ordinary"],
            "calendar_days": "target days whose reporting day type is quarter_end, month_end or tax_date, and the coupon-settlement days (treasury_settlement_coupons > 0 on the target day), reported with their number of days and the width of the skill interval",
        },
        "reading_rules": {
            "key": "the second arm of the key comparison is read as carrying signal in a cut when the lower end of the 90% skill interval of its CRPS against the first is above 0 on at least 30 decision days; it is read as not seen otherwise, which is not 'no signal'",
            "dilution": "the calendar-day cell is read beside the pooled cell with its number of days and interval width; a gain visible on calendar days and not in the pooled cell is dilution",
            "no_verdict": "development data gives no verdict; whether the ruling of 15 October 2026 is reopened is Eleonora's",
        },
        "rare_days": {"groups": list(RARE_GROUPS), "leaf_sizes": list(LEAF_SIZES), "refit_every": REFIT_EVERY, "minimum_history": MINIMUM_HISTORY},
        "ceiling": {
            "design": "H2's cross-fit (scripts/upper_bound_635.py, 10 contiguous blocks per lead, the walk-forward embargo), spread gbm only, with the lineup below; the ceiling read is the best of the lineup by CRPS on the walk-forward ordinary days, so it cannot score below the candidate's own inputs",
            "families": {name: list(prefixes) for name, prefixes in FAMILIES},
            "other_family": OTHER_FAMILY,
            "settings": {"reachable": "ml.UPPER_BOUND_SETTINGS['reachable']"},
            "candidate_inputs": "the published funding declaration's inputs as H2's scratch panel names them",
            "reading": "the best-of-lineup ceiling's skill against B1 minus the reachable model's, in points of skill, with the paired 90% interval; stop reading 'no headroom' when it is positive with the lower end above 0",
        },
        "limits": ["no day after 2025-12-31", "no lockbox day", "no published record is edited", "gbm_funding's declaration and scripts/final_test_preregistration.py are not changed"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the audit ------------------------------------------------------------------------------------------------------


def audit_command(args) -> int:
    served = served_from_target(load_sources(), contract_calendar())
    inventory = json.loads(args.inventory.read_text(encoding="utf-8")) if args.inventory else json.loads(AUDIT_INVENTORY.read_text(encoding="utf-8"))
    rows = []
    for fit in inventory["fits"]:
        columns = fit["calendar_and_scheduled_columns"]
        outside = sorted(set(columns) - served)
        if outside:
            raise ValueError(f"{fit['fit']}: {outside} are listed as calendar or scheduled but rule 2 does not serve them from the target row")
        rows.append({**fit, "trained_one_day_off": misaligned_columns(columns, fit["pairing"], served_from_target=served)})
    document = {"served_from_target": sorted(served), "fits": rows}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "fits": len(rows), "one_day_off": sum(1 for r in rows if r["trained_one_day_off"])}))
    return 0


AUDIT_INVENTORY = REPO / "metadata" / "drivers_audit_951_fits.json"


# -- the rare days --------------------------------------------------------------------------------------------------


def rare_command(args) -> int:
    from repo_model.asof import InformationRule, fold_grid, refit_blocks
    from repo_model.data import audit_panel, load_daily_panel

    committed_declaration()
    sd = _load("spread_distribution_634")
    require_study_window([LAST_TARGET])
    rows = [r for r in load_daily_panel(args.panel) if r.date <= LAST_TARGET]
    audit_panel(rows)
    dates = [r.date for r in rows]
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    flags = {
        "quarter_end": [bool(r.values.get("quarter_end")) and float(r.values["quarter_end"]) == 1.0 for r in rows],
        "tax_date": [bool(r.values.get("tax_date")) and float(r.values["tax_date"]) == 1.0 for r in rows],
        "month_end": month_end_flags([r.values.get("days_to_month_end") for r in rows]),
    }
    trainable = [r.spread_bps is not None for r in rows]
    out = {}
    for h in HORIZONS:
        grid = fold_grid(dates, registry, decision_time=time(16, 0), minimum_history=MINIMUM_HISTORY, horizon=h)
        rule = InformationRule(registry, ("sofr_p25",), decision_time=time(16, 0), horizon=h)
        windows = []
        for indices in refit_blocks(grid, REFIT_EVERY):
            anchor = rule.information_set(dates, indices[0]).anchor
            windows.append({"first_scored": dates[indices[0]].isoformat(), "training_rows": count_in_window([True] * len(rows), anchor, trainable),
                            **{g: count_in_window(flags[g], anchor, trainable) for g in RARE_GROUPS}})
        summary = {}
        for g in RARE_GROUPS:
            counts = [w[g] for w in windows]
            summary[g] = {
                "first_refit": counts[0], "median_refit": sorted(counts)[len(counts) // 2], "last_refit": counts[-1],
                **{f"refits_with_a_leaf_of_{leaf}": sum(1 for c in counts if can_split_alone(c, leaf)) for leaf in LEAF_SIZES},
            }
        out[str(h)] = {"refits": len(windows), "summary": summary, "windows": windows}
    document = {"panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(), "leaf_sizes": list(LEAF_SIZES), "leads": out}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


# -- the walks ------------------------------------------------------------------------------------------------------


def arm_features(arm: str, horizon: int) -> Tuple[str, ...]:
    live = _load("live_record")
    base = tuple(live.published_features(horizon))
    if ARMS[arm]["inputs"] == "base":
        return base
    return base + tuple(c for c in CALENDAR_INPUTS if c not in base)


def arm_fit(arm: str, features: Sequence[str]):
    from repo_model import ml

    spec = ARMS[arm]
    return functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID,
        training_pairs=spec["training_pairs"], min_samples_leaf=spec["min_samples_leaf"],
    )


def walk_command(args) -> int:
    from repo_model import measurement_fields
    from repo_model.baseline import panel_sha256
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.lockbox import require_unlocked

    declared = committed_declaration()
    if args.arm not in declared["arms"]:
        raise SystemExit(f"{args.arm!r} is not a declared arm")
    h = args.horizon
    sd = _load("spread_distribution_634")
    require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="drivers_audit_951")
    if sd.finished_walk(args.output, variant=args.arm, horizon=h, published=args.published, panel=args.panel):
        print(json.dumps({"variant": args.arm, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    published = load_daily_panel(args.published)
    audit_panel(published)
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    features = arm_features(args.arm, h)
    registry = measurement_fields.load_registry()
    with _load("net_settlement").switched_on():
        result, levels, settings = sd.walk(
            rows, fit=arm_fit(args.arm, features), features=features, online_calibration=None, registry=registry, horizon=h,
            minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY, expected_levels=GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": args.arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": args.arm, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- scoring --------------------------------------------------------------------------------------------------------


def _summarise(test) -> dict:
    interval = percentile_interval(test.skill_draws)
    return {
        "n": test.n, "benchmark_mean": test.benchmark_mean, "candidate_mean": test.benchmark_mean - test.mean_difference,
        "mean_difference": test.mean_difference, "skill": test.skill, "skill_interval_90": interval, "interval_width": interval_width(interval),
        "mean_difference_lower_95_one_sided": test.lower_mean_difference(), "bootstrap_p": test.p_value,
    }


def _paired_job(job):
    key, chosen, draws = job
    return key, [_summarise(test) for test in sp.paired_tests(chosen, seed=SEED, draws=draws)]


def settings_of(document: Mapping) -> Mapping:
    """A walk's recorded fit settings; `spread_distribution_634.py walk` stores a mapping proxy as the text of its dict."""

    import ast

    settings = document.get("settings", {})
    if isinstance(settings, str):
        settings = ast.literal_eval(settings)
    if not isinstance(settings, Mapping):
        raise ValueError(f"the walk's settings are not a mapping: {settings!r}")
    return settings


def comparison_pairs(arms: Sequence[str]) -> List[Tuple[str, str]]:
    """The control and every declared arm against B1 and B2, every arm against the control (the control against B1 and B2 was added after the first scoring pass), then the declared arm-against-arm comparisons."""

    pairs = [(b, a) for a in (CONTROL, *arms) for b in ("B1", "B2", CONTROL) if b != a]
    return pairs + [pair for pair in KEY_COMPARISONS if pair not in pairs]


def score_command(args) -> int:
    from repo_model import protocol_benchmarks as pb
    from repo_model.baseline import panel_sha256
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    declared = committed_declaration()
    sd = _load("spread_distribution_634")
    require_unlocked([LAST_TARGET], where="drivers_audit_951")
    published = load_daily_panel(args.published)
    audit_panel(published)
    scratch = {r.date: r for r in load_daily_panel(args.panel)}
    calendar = [r.date for r in published]
    position = {day: i for i, day in enumerate(calendar)}
    outcomes = {r.date: r.spread_bps for r in published}
    row_of = {r.date: r for r in published}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    digest = panel_sha256(args.published)
    arms = list(declared["arms"])
    names = [CONTROL, *arms]
    decisions, covered = {}, {}
    for name in names:
        for h in HORIZONS:
            document = json.loads((args.walks / f"{name}_h{h}.json").read_text(encoding="utf-8"))
            if document["panel_sha256"] != digest:
                raise ValueError(f"{name} lead {h} was walked on another published panel")
            pairing = settings_of(document).get("training_pairs")
            if name == CONTROL and pairing is not None:
                raise ValueError(f"the control {name} lead {h} names training_pairs {pairing!r}; it must be unset (one-step)")
            if name != CONTROL and pairing != "direct":
                raise ValueError(f"{name} lead {h} does not name training_pairs 'direct'")
        decisions[name], covered[name] = sd.lead_forecasts(sd.load_laws(args.walks, name), calendar)
    common = sorted(set.intersection(*(set(d) for d in covered.values())))
    common = [d for d in common if all(calendar[position[d] + h] <= LAST_TARGET for h in HORIZONS)]
    sd.refuse_locked(common + [calendar[position[d] + h] for d in common for h in HORIZONS])
    usable, unbuilt = [], []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, published, [day], registry=registry, decision_time=sd.DECISION)
            pb.forecasts(pb.b2_forecast, published, [day], registry=registry, decision_time=sd.DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError as error:
            unbuilt.append((day.isoformat(), str(error)))
    common = usable
    b1 = pb.forecasts(pb.b1_forecast, published, common, registry=registry, decision_time=sd.DECISION)
    b2 = pb.forecasts(pb.b2_forecast, published, common, registry=registry, decision_time=sd.DECISION, splits=splits)
    forecasts, missing = {"B1": b1, "B2": b2}, {}
    for name in names:
        filled = sp.fill_missing({d: decisions[name][d] for d in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    every = ["B1", "B2", *names]
    cells = {n: sd.cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in every}
    days = sorted(set.intersection(*(set(sp.day_scores(forecasts[n], outcomes, calendar)) for n in every)))

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    def coupon(day: date) -> bool:
        value = scratch[day].values.get("treasury_settlement_coupons") if day in scratch else None
        return value is not None and float(value) > 0.0

    target_kind = {calendar[position[d] + h]: kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS}
    cut_target = {
        **{kind: (lambda t, kind=kind: target_kind[t] == kind) for kind in (*CALENDAR_KINDS, "ordinary")},
        CALENDAR_DAYS: lambda t: target_kind[t] in CALENDAR_KINDS,
        COUPON_SETTLEMENT: coupon,
    }
    pairs = comparison_pairs(arms)
    jobs, shells = [], {}

    def add(key, include, group, headline):
        means = {n: sd.day_means(cells[n], include) for n in every}
        shared = sorted(set.intersection(*(set(m) for m in means.values())) & set(group))
        entry = {"n": len(shared), "mean": {n: sum(means[n][d] for d in shared) / len(shared) for n in every} if shared else {}}
        if len(shared) < MINIMUM_DAYS or len(shared) <= sp.HAC_LAG:
            entry["thin"] = True
        else:
            jobs.append((key, [({d: means[b][d] for d in shared}, {d: means[c][d] for d in shared}) for b, c in pairs], HEADLINE_DRAWS if headline else SPLIT_DRAWS))
        shells[key] = entry

    add(("pooled", "all"), lambda d, h: True, days, True)
    for label in splits.regime_labels:
        group = [d for d in days if splits.regime(d) == label]
        if group:
            add(("regime", label), lambda d, h, g=set(group): d in g, group, False)
    for kind, test in cut_target.items():
        add(("day type", kind), lambda d, h, t=test: t(calendar[position[d] + h]), days, kind == CALENDAR_DAYS)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, results in pool.map(_paired_job, jobs):
            shells[key]["tests"] = {f"{b} -> {c}": row for (b, c), row in zip(pairs, results)}
    tables: Dict[str, dict] = {}
    for (group, label), entry in shells.items():
        tables.setdefault(group, {})[label] = entry
    document = {
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(), "panel_sha256": digest, "scratch_panel_sha256": panel_sha256(args.panel),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()}, "seed": SEED,
        "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS}, "decision_days_without_a_benchmark": unbuilt, "missing": missing,
        "names": every, "pairs": [f"{b} -> {c}" for b, c in pairs], "key_comparison": " -> ".join(KEY_COMPARISON), "tables": tables,
        "features": {n: json.loads((args.walks / f"{n}_h1.json").read_text(encoding="utf-8"))["features"] for n in names},
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the nested ceiling (long: needs-mac) ---------------------------------------------------------------------------


_STATE: dict = {}


def _ceiling_task(task):
    from repo_model import ml

    entry, lead, start, stop = task
    ub = _STATE["ub"]
    state = _STATE
    x_lead = state["x"][entry][lead]
    y, valid, rows_of, anchor = state["y"], state["valid"], state["rows"], state["anchors"][lead]
    train = [p for p in ub.crossfit_positions(rows_of, anchor, start, stop) if valid[p]]
    serve = [p for p in range(start, stop) if valid[p]]
    if len(train) < ub.MINIMUM_TRAIN or not serve:
        return task, None
    settings = ml.UPPER_BOUND_SETTINGS["reachable"]
    block = ml.grid_quantiles_gbm([x_lead[p] for p in train], [y[p] for p in train], [x_lead[p] for p in serve], GRID, settings["gbm"])
    return task, {"serve": serve, "train_rows": len(train), "spread": block}


def ceiling_fit_command(args) -> int:
    from repo_model import dvp_segment, measurement_fields
    from repo_model.data import load_daily_panel

    declared = committed_declaration()
    ub = _load("upper_bound_635")
    d631 = ub.d631
    inputs = ub.committed()["inputs"]["columns"]
    rows = load_daily_panel(args.panel)
    if rows[-1].date > LAST_TARGET:
        raise SystemExit(f"the panel runs past {LAST_TARGET}")
    dvp_segment.require_ofr_public(rows)
    registry = measurement_fields.load_registry()
    read_columns = [n for n in inputs if n not in d631.INTERACTIONS and n != ub.SPREAD_ASOF]
    with d631.switched():
        scored, series, anchors = ub.read_inputs(rows, registry, read_columns)
    d631.add_interactions(series)
    base = json.loads((REPO / "metadata" / "spread_distribution_634.json").read_text(encoding="utf-8"))["inputs"]["base"]["columns"]
    candidate = [c for c in (ub.SPREAD_ASOF if c == "spread_bps" else c for c in base) if c in inputs]
    lineup = ceiling_lineup(inputs, candidate)
    x = {}
    for entry, spec in lineup.items():
        x[entry] = _subset(ub, series, inputs, spec["columns"])
    spreads = [rows[i].spread_bps for i in scored]
    _STATE.update(ub=ub, x=x, y=[float(s) if s is not None else None for s in spreads], valid=[s is not None for s in spreads], rows=scored, anchors=anchors)
    tasks = [(entry, lead, a, b) for entry in lineup for lead in ub.LEADS for a, b in ub.folds(len(scored))]
    if args.limit:
        tasks = tasks[: args.limit]  # a smoke run of the code path; its output is not read
    results = []
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        for done, (task, result) in enumerate(pool.imap_unordered(_ceiling_task, tasks, chunksize=1), 1):
            results.append((task, result))
            if done % 25 == 0 or done == len(tasks):
                print(json.dumps({"fitted": done, "of": len(tasks)}), flush=True)
    document = {
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(), "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "scored_days": [rows[i].date.isoformat() for i in scored], "scored_rows": scored, "spread": [s for s in spreads],
        "lineup": lineup, "tasks": [{"entry": t[0], "lead": t[1], "start": t[2], "stop": t[3], "result": r} for t, r in sorted(results, key=lambda tr: (tr[0][0], tr[0][1], tr[0][2]))],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "tasks": len(tasks)}))
    return 0


def _subset(ub, series, inputs, columns):
    """`upper_bound_635.design_matrices` restricted to `columns`, in the order given."""

    full = ub.design_matrices(series, inputs)
    index = [inputs.index(c) for c in columns]
    return {lead: [[row[i] for i in index] for row in matrix] for lead, matrix in full.items()}


def ceiling_score_command(args) -> int:
    from repo_model import protocol_benchmarks as pb
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    committed_declaration()
    ub = _load("upper_bound_635")
    fits = json.loads(args.fits.read_text(encoding="utf-8"))
    if fits["declaration_sha256"] != hashlib.sha256(DECLARATION.read_bytes()).hexdigest():
        raise SystemExit("the fits were made under a different declaration")
    published = [r for r in load_daily_panel(args.published) if r.date <= LAST_TARGET]
    audit_panel(published)
    dates = [r.date for r in published]
    scored_rows = fits["scored_rows"]
    if [dates[i].isoformat() for i in scored_rows] != fits["scored_days"]:
        raise SystemExit("the published panel's days are not the fit panel's")
    require_study_window(dates[i] for i in scored_rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    forecast = {entry: {lead: {} for lead in ub.LEADS} for entry in fits["lineup"]}
    for task in fits["tasks"]:
        if task["result"] is None:
            continue
        for position, quantiles in zip(task["result"]["serve"], task["result"]["spread"]):
            forecast[task["entry"]][task["lead"]][position] = quantiles
    per_entry = {entry: ub.decision_forecasts(per_lead, scored_rows, dates) for entry, per_lead in forecast.items()}
    walk_days = sorted(set.intersection(*(set(v) for v in per_entry.values())))
    b1 = pb.forecasts(pb.b1_forecast, published, walk_days, registry=registry, decision_time=time(16, 0))
    outcome = {dates[scored_rows[p]]: s for p, s in enumerate(fits["spread"]) if s is not None}
    ordinary = {dates[i] for i in scored_rows if not ub.ann.risk_flag(splits, published[i].values, True)}
    outcome = {d: (v if d in ordinary else None) for d, v in outcome.items()}
    forecasts = {"B1": b1, **{entry: {d: per_entry[entry][d] for d in walk_days} for entry in per_entry}}
    scores = {n: sp.day_scores(fc, outcome, dates) for n, fc in forecasts.items()}
    days = sorted(set.intersection(*(set(v) for v in scores.values())))
    names = [n for n in forecasts if n != "B1"]
    tests = sp.paired_tests([(scores["B1"], scores[n]) for n in names], seed=SEED, draws=SPLIT_DRAWS) if days else []
    cells = {n: _summarise(t) for n, t in zip(names, tests)}
    best = min(names, key=lambda n: cells[n]["candidate_mean"])
    floor = "candidate inputs"
    document = {"decision_days": len(days), "cells": cells, "best_of_lineup": best, "candidate_inputs_cell": floor,
                "ceiling_is_at_least_the_candidate": cells[best]["candidate_mean"] <= cells[floor]["candidate_mean"]}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best": best}))
    return 0


# -- the report -----------------------------------------------------------------------------------------------------


def _f(value: Optional[float], digits: int = 3, signed: bool = True) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _iv(interval) -> str:
    return "n/a" if interval is None else f"[{_f(interval[0])}, {_f(interval[1])}]"


def audit_section(audit: Mapping) -> List[str]:
    lines = ["## 1. Which fits train a calendar or scheduled column one day off (suspect 2)", "",
             "Rule 2 of `src/repo_model/asof.py` serves calendar columns and scheduled fields from the target row. A one-step fit pairs the target of row p + 1 with row p, so it learns such a column one day off. `net_settlement*` are observed columns (dated at their own day), not scheduled.", "",
             "| result | fit | pairing | calendar or scheduled columns in it | trained one day off |", "|---|---|---|---|---|"]
    for fit in audit["fits"]:
        lines.append(f"| {fit['result']} | {fit['fit']} | {fit['pairing']} | {', '.join(fit['calendar_and_scheduled_columns']) or 'none'} | {', '.join(fit['trained_one_day_off']) or 'no'} |")
    return lines + [""]


def rare_section(rare: Mapping) -> List[str]:
    lines = ["## 2. Rare days in each refit's training window (suspect 3)", "",
             "Refits of the walk-forward (every 21 scored days, minimum history 61). A tree can put only the days of a group on one side of a split when the training window holds at least `min_samples_leaf` of them; below that the group is always mixed with ordinary days. Cells: refits whose window holds at least that many.", "",
             "| lead | group | refits | days at first / median / last refit | with at least 20 | with at least 10 | with at least 5 |", "|---|---|---|---|---|---|---|"]
    for h, block in rare["leads"].items():
        if h not in ("1", "5"):
            continue
        for group, row in block["summary"].items():
            lines.append(f"| {h} | {group} | {block['refits']} | {row['first_refit']} / {row['median_refit']} / {row['last_refit']} | {row['refits_with_a_leaf_of_20']} | {row['refits_with_a_leaf_of_10']} | {row['refits_with_a_leaf_of_5']} |")
    return lines + [""]


def ceiling_section(ceiling: Mapping) -> List[str]:
    lines = ["## 3. The nested ceiling (suspect 1)", "",
             f"Cross-fitted as H2's ceiling is (10 contiguous blocks per lead, the walk-forward embargo), spread gbm at the reachable settings, scored on the ordinary-day targets of {ceiling['decision_days']} decision days against B1. The ceiling read is the best of the lineup, so it cannot score below the candidate's own inputs (best: {ceiling['best_of_lineup']}; at least the candidate's inputs: {ceiling['ceiling_is_at_least_the_candidate']}).", "",
             "| lineup entry | mean CRPS | skill against B1 [90%] |", "|---|---|---|"]
    for name, cell in ceiling["cells"].items():
        lines.append(f"| {name} | {_f(cell['candidate_mean'], 3, False)} | {_f(cell['skill'])} {_iv(cell['skill_interval_90'])} |")
    return lines + [""]


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    lines = []
    if args.audit:
        lines += audit_section(json.loads(args.audit.read_text(encoding="utf-8")))
    if args.rare:
        lines += rare_section(json.loads(args.rare.read_text(encoding="utf-8")))
    if args.ceiling:
        lines += ceiling_section(json.loads(args.ceiling.read_text(encoding="utf-8")))
    lines += [
        "## 4. The declared re-run: tables",
        "",
        "Development data, not a verdict. Skill = (mean S(first) - mean S(second)) / mean S(first) of the grid CRPS; positive favours the second arm; 90% interval of the stationary bootstrap (5th to 95th percentile).",
        f"Decision days: {document['decision_days']['n']} ({document['decision_days']['first']} to {document['decision_days']['last']}). `n` below is the number of decision days with at least one target in the cut.",
        "",
    ]
    key = {f"{b} -> {c}" for b, c in KEY_COMPARISONS} | {f"{b} -> {CONTROL}" for b in ("B1", "B2")}
    for group, cells in document["tables"].items():
        for label, entry in cells.items():
            lines += [f"### {group}: {label}", ""]
            if "tests" not in entry:
                lines += [f"n = {entry['n']}: fewer than {MINIMUM_DAYS} decision days.", ""]
                continue
            full = (group, label) in (("pooled", "all"), ("day type", CALENDAR_DAYS))
            lines += [f"n = {entry['n']} decision days.", "", "| first -> second | mean first | mean second | skill [90%] | interval width |", "|---|---|---|---|---|"]
            for pair, row in entry["tests"].items():
                if full or pair in key or pair.startswith("B1 -> direct_cal_leaf5"):
                    lines.append(f"| {pair} | {_f(row['benchmark_mean'], 3, False)} | {_f(row['candidate_mean'], 3, False)} | {_f(row['skill'])} {_iv(row['skill_interval_90'])} | {_f(row['interval_width'], 3, False)} |")
            lines.append("")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("declare")
    p.set_defaults(run=declare_command)
    p = sub.add_parser("audit")
    p.add_argument("--inventory", type=Path, default=None)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=audit_command)
    p = sub.add_parser("rare")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=rare_command)
    p = sub.add_parser("walk")
    p.add_argument("--arm", required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=walk_command)
    p = sub.add_parser("score")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--walks", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--workers", type=int, default=4)
    p.set_defaults(run=score_command)
    p = sub.add_parser("report")
    p.add_argument("score", type=Path)
    p.add_argument("--audit", type=Path, default=None)
    p.add_argument("--rare", type=Path, default=None)
    p.add_argument("--ceiling", type=Path, default=None)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=report_command)
    p = sub.add_parser("ceiling-fit")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--limit", type=int, default=0, help="fit only the first N tasks (a smoke run)")
    p.set_defaults(run=ceiling_fit_command)
    p = sub.add_parser("ceiling-score")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--fits", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=ceiling_score_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
