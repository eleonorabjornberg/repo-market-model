"""gbm_funding's raw-level inputs re-encoded as the quantities the mechanism acts on, on #1027's direct calendar design: one declared variant (#1029, H5 step 3).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no published figure. Every choice is in
`metadata/mechanism_encodings_1029.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from the constants
below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**The variant.** `gbm_funding_cal_direct_enc` is #1027's `gbm_funding_cal_direct` with each raw level of its inputs replaced, in place, by its encoding
(`repo_model.mechanism_encodings`, Lens D of #958): the 4-week and 13-week bill less IORB, SOFR less its 25th and its 75th percentile less SOFR (bp), SOFR
volume over its trailing-year median, reserve balances over their trailing-year median. `tga`, the lagged spread and the settlement columns stay as they
are; the target-row calendar and scheduled columns and the observed net-settlement columns are #1027's, read the same way, on direct pairs
(`training_pairs="direct"`), so every column is trained from the row it is served from and the #947 guard needs no allow-list entry. The only difference
from `gbm_funding_cal_direct` is the encoding of the six levels: the leaf (5), seed, fold grid, refit cadence (21 scored days, 61 minimum history) and
quantile grid are the same. Each encoding is a function of its own row and earlier rows, declared on the union of its constituents' source fields, so the
as-of rule reads it at the row of its slowest constituent and no later: no new publication instant (`tests/test_mechanism_encodings_1029.py`).

The walks are long (`needs-mac`, #46); `score` reads them. The scratch panel is #951's `AUG3` built from the tracked fixtures (the commands below build it; its
digest is recorded in the result). #1027's own variant is re-walked on the same panel so that the pair shares its inputs byte for byte; `gbm_funding`'s
reference walks are #634's on the published panel, unchanged.

    S=<a directory>; P=$S/panels; W=$S/walks; mkdir -p $P $W
    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output $P/PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00                       # digest 4ddc3882...
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output $P/AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel $P/AUG.csv --output $P/AUG2.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel $P/AUG2.csv --output $P/AUG2D.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/net_settlement.py panel --panel $P/AUG2D.csv --output $P/AUG3.csv
    PYTHONPATH=src python3 scripts/mechanism_encodings_1029.py declare            # then commit metadata/mechanism_encodings_1029.json before any score
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published $P/PUB.csv --panel $P/PUB.csv --output $W/gbm_funding_h$h.json
        for v in gbm_funding_cal_direct gbm_funding_cal_direct_enc:
            OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/mechanism_encodings_1029.py walk --variant $v --horizon $h \\
                --published $P/PUB.csv --panel $P/AUG3.csv --output $W/${v}_h$h.json
    PYTHONPATH=src python3 scripts/mechanism_encodings_1029.py score --published $P/PUB.csv --panel $P/AUG3.csv --walks $W \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
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


from repo_model import mechanism_encodings as me, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

ac = _load("aligned_calendar_1027")

DECLARATION = REPO / "metadata" / "mechanism_encodings_1029.json"
SPLITS = ac.SPLITS
SOURCES = ac.SOURCES
LAST_TARGET = ac.LAST_TARGET
SEED = 1029
MINIMUM_HISTORY, REFIT_EVERY = ac.MINIMUM_HISTORY, ac.REFIT_EVERY
HORIZONS, GRID, LEAF = ac.HORIZONS, ac.GRID, ac.LEAF
MIN_GROUP_DAYS = ac.MIN_GROUP_DAYS

CONTROL = ac.CONTROL                  # gbm_funding
BASE = ac.DIRECT                      # #1027's direct variant: the same design on the raw levels
ENC = "gbm_funding_cal_direct_enc"
VARIANTS = (BASE, ENC)                # walked on the scratch panel
BENCHMARKS = ("B1", ac.B1P, "B2", ac.CTX)
METRICS = ac.METRICS
CALENDAR_TYPES = ac.CALENDAR_TYPES
ORDER_REGIME = ac.ORDER_REGIME


# -- the variant -------------------------------------------------------------------------------------------------------


def variant_features(variant: str, horizon: int) -> Tuple[str, ...]:
    """#1027's direct inputs at a lead; for the encoded variant each raw level replaced, in place, by its encoding."""

    base = ac.variant_features(ac.DIRECT, horizon)
    if variant == BASE:
        return base
    if variant != ENC:
        raise ValueError(f"{variant!r} is not a declared variant")
    return me.encode_features(base)


def variant_fit(variant: str, features: Sequence[str]):
    """The variant's fitter: `gbm_funding`'s gbm at `LEAF` on direct pairs (both variants), over the variant's regressors."""

    if variant not in VARIANTS:
        raise ValueError(f"{variant!r} is not a declared variant")
    return ac.variant_fit(ac.DIRECT, features)


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1029 before any number was computed; a measurement, not a record. Nothing is published: the variant joins no published declaration, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1029,
        "hypothesis": "H5 step 3 (mechanism-consistent encodings of gbm_funding's raw-level inputs; Lens D of #958)",
        "ruling": "Eleonora, 19 and 20 October 2026 (the five-lens review is the queue's guide; calendar first)",
        "variant": {
            ENC: {
                "base": f"{BASE} of metadata/aligned_calendar_1027.json: direct pairs, the target-row calendar and scheduled columns, the observed net_settlement columns, leaf {LEAF}",
                "pairing": "direct pairs (training_pairs='direct'): each target is paired with its own as-of read; the #947 guard needs no allow-list entry",
                "encodings": {
                    raw: {
                        "column": column,
                        "constituents": {
                            "tbill_4w_less_iorb_bps": ["tbill_4w", "iorb"], "tbill_13w_less_iorb_bps": ["tbill_13w", "iorb"],
                            "sofr_less_p25_bps": ["sofr", "sofr_p25"], "p75_less_sofr_bps": ["sofr_p75", "sofr"],
                            "sofr_volume_to_median": ["sofr_volume"], "reserves_to_median": ["reserve_balances"],
                        }[column],
                    }
                    for raw, column in me.ENCODED.items()
                },
                "definitions": {
                    "bp": "(upper - lower) * 100, the panel's levels being in percent",
                    "ratio": f"the value over the median of the present values among the last {me.WINDOW_ROWS} panel rows ending at the row (the row included), at least {me.MINIMUM_ROWS} present, else missing",
                },
                "unchanged": ["spread_bps", "tga", "treasury_settlement", "the target-row columns", "net_settlement", "net_settlement_due_5d"],
                "as_of": "each column is declared on the union of its constituents' source fields (repo_model.mechanism_encodings.COLUMN_FIELDS), so asof.InformationRule reads it at the row of its slowest constituent; no new publication instant; InformationRule, contract.FEATURE_FIELDS and the registry are unchanged",
            }
        },
        "settings": "gbm_funding's and #1027's: seed, quantile grid, refit every 21 scored days, 61 minimum history, leaf 5",
        "panel": "#951's scratch panel AUG3, built from the tracked fixtures by the commands in scripts/mechanism_encodings_1029.py; the encoded columns are added in memory by repo_model.mechanism_encodings.build_columns; #1027's direct variant is re-walked on the same panel; gbm_funding's reference walks are #634's on the published panel",
        "benchmarks": [CONTROL, BASE, "B1", ac.B1P, "B2", ac.CTX],
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "settlement": "a target day whose reporting day type is ordinary and whose treasury_settlement_coupons or treasury_settlement_bills is above 0",
            "calendar_days": list(CALENDAR_TYPES),
        },
        "interval": "stationary bootstrap, seed 1029, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "against_each_comparator": "for gbm_funding and for gbm_funding_cal_direct: the variant beats it when the lower end of its pooled grid-CRPS skill interval is above 0, and loses to it when the upper end is below 0; otherwise it is not shown to differ",
            "calendar_and_ordinary": "as #1027: beats gbm_funding on calendar days when the lower end of its skill interval on the calendar_days cut is above 0, and loses on ordinary days when the upper end of its skill interval there is below 0",
            "regimes": "reported per regime, with no threshold: the encodings are meant to carry the mechanism across regimes, so the per-regime skill over gbm_funding_cal_direct is the table to read",
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

    ac.committed_declaration(DECLARATION)
    sd = _load("spread_distribution_634")
    variant, h = args.variant, args.horizon
    if variant not in VARIANTS or h not in HORIZONS:
        raise SystemExit(f"variant {variant!r} / lead {h} is not declared")
    ac.require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="mechanism_encodings_1029")
    if ac._finished(args.output, variant, h, args.published, args.panel):
        print(json.dumps({"variant": variant, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    if variant == ENC:
        rows = me.build_columns(rows)
    features = variant_features(variant, h)
    with _load("net_settlement").switched_on(), me.switched_on():
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


# -- the reading rules (tested) ---------------------------------------------------------------------------------------


def _verdict(row: Optional[dict]) -> Optional[str]:
    """`beats`, `loses` or `not shown to differ` from a paired row's studentized interval; `None` if the cut is not scored or undefined."""

    if row is None or "undefined" in row:
        return None
    low, high = row["skill_interval"]
    return "beats" if low > 0.0 else ("loses to" if high < 0.0 else "is not shown to differ from")


def reading_rules(rows: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    """The declared sentences per comparator, from the variant's paired grid-CRPS rows on `pooled`, `calendar` and `ordinary` cuts.

    `rows[comparator]` maps those three names to a paired row (`s761.paired_row`), an undefined one, or None. The lower end of a studentized two-sided
    90% interval is the one-sided 95% lower bound.
    """

    s761 = _load("spread_mr_variants_761")
    out = []
    for comparator, cells in rows.items():
        parts = []
        for cut, label in (("pooled", "on all decision days"), ("calendar", "on calendar days"), ("ordinary", "on ordinary days")):
            row = cells.get(cut)
            verdict = _verdict(row)
            if verdict is None:
                parts.append(f"{label}: not read (the cut is not scored or undefined)")
            else:
                parts.append(
                    f"{label} {verdict} it (skill {s761.pct(row['skill'])}, interval {s761.pct(row['skill_interval'][0])} to {s761.pct(row['skill_interval'][1])})"
                )
        out.append(f"{ENC}, against {comparator}: " + "; ".join(parts) + ".")
    return out


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


def score_command(args) -> int:
    b960 = _load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = ac.committed_declaration(DECLARATION)
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    pub = load_daily_panel(published)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), walks)
    models = list(BENCHMARKS) + [CONTROL]
    for variant in VARIANTS:
        frame.forecasts[variant] = load_walks(walks, variant, published, panel_path, frame)
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
    labels = {"regime": {t: frame.regime(t) for t in targets}, "target_type": {t: ac.target_type(frame, t) for t in targets}}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    groups[("target_type", "calendar_days")] = ("target", [d for d in targets if labels["target_type"][d] in CALENDAR_TYPES])

    pairs = [(ENC, b) for b in (CONTROL, BASE) + BENCHMARKS]
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
        "issue": 1029, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models, "pairs": [list(p) for p in pairs],
        "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in models} for label, _ in METRICS},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"],
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = _SERIES[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(split, label, comparator):
        return result["groups"].get(split, {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{ENC} vs {comparator}")

    result["reading_rules"] = reading_rules(
        {c: {"pooled": pick("pooled", "all decision days", c), "calendar": pick("target_type", "calendar_days", c), "ordinary": pick("target_type", "ordinary", c)}
         for c in (CONTROL, BASE)}
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


# -- Markdown --------------------------------------------------------------------------------------------------------

METRIC_TITLES = ac.METRIC_TITLES
SPLIT_TITLES = ac.SPLIT_TITLES


def render_report(r: dict, s761) -> str:
    """#1027's report with this study's title and reading; the tables are the same (`ac.render_report`), the mean scores and groups are this run's."""

    text = ac.render_report({**r, "not_run": {}}, s761)
    text = text.replace(
        "# gbm_funding with calendar and scheduled columns read from the target row (#1027): development data, not a verdict",
        "# gbm_funding with its raw levels re-encoded as the mechanism acts on them, on #1027's direct calendar design (#1029): development data, not a verdict",
    )
    return text


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
