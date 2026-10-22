"""A day-of-month level term added to #1027's direct-pairs variant: one declared variant (#1032, H5 step 2, Lens A of #958).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model and no published figure. Every choice is in
`metadata/dom_level_term_1032.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from the
constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is read
(`docs/decisions/lockbox.md`).

**The design.** The 19th to 23rd of the month is a trough in the spread's level (-5.4 to -6.6 bp; Lens A of #958, `calendar_check.py`), invisible to
#631's screen of onsets. The one added input is `dom_bucket` (`repo_model.dom_calendar`): the bucket, over 1-5, 6-14, 15-18, 19-23 and 24-31, of the
*target* day's day of the month. Rule 2 of `asof.py` serves a calendar column from the target row, at every lead, so the variant trains it on direct
pairs (`training_pairs="direct"`), where each target is paired with its own as-of read; a one-step fit would train it a row off (#914) and
`repo_model.one_step_guard` refuses it. The variant is `gbm_funding_cal_direct` of #1027 (`scripts/aligned_calendar_1027.py`) plus that column and
nothing else: same inputs at each lead, same leaf, seed, fold grid, refit cadence and quantile grid, same scratch panel. The column is written by
`dom_calendar.add_columns` and served for the run by `dom_calendar.switched_on`. The aligned one-step variant of #1027 with the term would need an
allow-list entry for its new regressors, which is Eleonora's; it is not declared (a marked question on the pull request).

The walks are long (`needs-mac`, #46); `score` reads them. The reference walks are #1027's and #634's, from the same panels; a walk already finished
(same panel bytes) is skipped, so one folder serves both studies.

    # PUB.csv: the published panel (digest 4ddc3882...); AUG3.csv: #951's scratch panel (see scripts/drivers_audit_951.py's docstring)
    PYTHONPATH=src python3 scripts/dom_level_term_1032.py declare              # then commit metadata/dom_level_term_1032.json before any score
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/dom_level_term_1032.py walk --horizon $h --published PUB.csv --panel AUG3.csv \\
            --output WALKS/gbm_funding_cal_direct_dom_h$h.json
    # the controls, from #1027's script (each skipped if WALKS already holds it):
    for h in 1 2 3 4 5:
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant gbm_funding --horizon $h \\
            --published PUB.csv --panel PUB.csv --output WALKS/gbm_funding_h$h.json
        for v in gbm_funding_cal_aligned gbm_funding_cal_direct:
            OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/aligned_calendar_1027.py walk --variant $v --horizon $h \\
                --published PUB.csv --panel AUG3.csv --output WALKS/${v}_h$h.json
    PYTHONPATH=src python3 scripts/dom_level_term_1032.py score --published PUB.csv --panel AUG3.csv --walks WALKS \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import dom_calendar, ml, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "dom_level_term_1032.json"
SEED = 1032
HORIZONS = sp.HORIZONS
DOM = "gbm_funding_cal_direct_dom"
_M = []


def m():
    """#1027's script, loaded once: its variants, fitters, walk helpers and scoring helpers are this study's."""

    if not _M:
        spec = importlib.util.spec_from_file_location("aligned_calendar_1027_script", REPO / "scripts" / "aligned_calendar_1027.py")
        module = sys.modules.get(spec.name)
        if module is None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
        _M.append(module)
    return _M[0]


def __getattr__(name):
    if name == "CONTROLS":  # (gbm_funding, gbm_funding_cal_direct, gbm_funding_cal_aligned): the references the term is read against
        return (m().CONTROL, m().DIRECT, m().ALIGNED)
    raise AttributeError(name)


# -- the variant -----------------------------------------------------------------------------------------------------


def variant_features(horizon: int) -> Tuple[str, ...]:
    """#1027's direct variant's inputs at the lead, then the term, none twice."""

    base = m().variant_features(m().DIRECT, horizon)
    return base + tuple(c for c in (dom_calendar.COLUMN,) if c not in base)


def variant_fit(features: Sequence[str]):
    """The direct variant's fitter (`gbm_funding`'s gbm at #1027's leaf, direct pairs) on `features`."""

    return functools.partial(
        ml.fit_gradient_boosted_quantiles, regressors=m().regressors(features), levels=m().GRID, min_samples_leaf=m().LEAF, training_pairs="direct"
    )


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1032 before any number was computed; a measurement, not a record. Nothing is published: the variant joins no published declaration, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1032,
        "hypothesis": "H5 step 2: a day-of-month level term for the 19th to 23rd trough (five-lens, Lens A of #958; #950 row 4)",
        "calendar_first": "the term is read from the target row at every lead h = 1 to 5, on direct pairs (training_pairs=direct); a one-step fit is refused by repo_model.one_step_guard (#947)",
        "term": {
            "column": dom_calendar.COLUMN,
            "buckets": [list(b) for b in dom_calendar.BUCKETS],
            "definition": "the bucket number (0 to 4) of the calendar day of the month of the row's own date; the target row's value is served at every lead (rule 2 of asof.py, a calendar column)",
            "why_these_buckets": "the trough is the 19th to 23rd (-5.4 to -6.6 bp), the 6th to 14th sits at -4.8 to -5.6 bp and the 31st at +1.3 bp (Lens A of #958); the first week, the 15th to 18th and the 24th to month end are the remaining stretches. The edges are declared here, before any score, and a tree may split finer on days_to_month_end, which it already reads",
            "module": "src/repo_model/dom_calendar.py (add_columns writes it onto the scratch panel; switched_on serves it as a calendar column for one run; it is not in contract.CALENDAR_FEATURES, whose bytes the final test freezes)",
        },
        "variants": {
            DOM: {
                "base": "gbm_funding_cal_direct of #1027 (metadata/aligned_calendar_1027.json): gbm_funding's published inputs at the lead, the calendar columns at every lead and the settlement columns at lead 1 from the target row, net_settlement and net_settlement_due_5d",
                "added": [dom_calendar.COLUMN],
                "training_pairs": "direct",
                "min_samples_leaf": 5,
                "aligned_one_step_with_the_term": "not declared: it would need an allow-list entry in repo_model.one_step_guard for its new regressors, which is Eleonora's decision (marked question on the pull request)",
            }
        },
        "settings": "as gbm_funding_cal_direct: seed, quantile grid, refit every 21 scored days, minimum history 61, n_estimators and depth of ml.fit_gradient_boosted_quantiles, leaf 5",
        "panel": "#951's scratch panel AUG3 (as #1027); the term is written onto it at load by dom_calendar.add_columns, so the panel's bytes and digest do not move",
        "references": ["gbm_funding_cal_direct", "gbm_funding_cal_aligned", "gbm_funding", "B1", "B1_prime", "B2", "spread_mr_ctx"],
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": m().ORDER_REGIME,
            "target_day_types": ["quarter_end", "month_end", "tax_date", "settlement", "ordinary"],
            "dom_bucket": [f"{lo}-{hi}" for lo, hi in dom_calendar.BUCKETS],
            "calendar_days": list(m().CALENDAR_TYPES),
        },
        "interval": "stationary bootstrap, seed 1032, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "pairing": "the term is read against gbm_funding_cal_direct, which differs from it by the term alone; the other references are reported on the same cuts",
            "helps": "the term helps when the lower end of its grid-CRPS skill interval over gbm_funding_cal_direct on the pooled cut is above 0",
            "trough": "it helps on the trough when the same lower end on target days of the 19-23 bucket is above 0",
            "loses": "'loses' means a skill interval wholly below 0, read on ordinary target days",
            "replacement": "adopting the term, or naming it with a variant of #1027 as the candidate, is a marked question for Eleonora",
            "no_verdict": "development data gives no verdict",
        },
        "limits": ["no day after 2025-12-31", "no lockbox day", "no published record is edited", "gbm_funding's declaration, contract.py and scripts/final_test_preregistration.py are not changed"],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk --------------------------------------------------------------------------------------------------------


def walk_rows(rows, horizon: int, *, minimum_history: int, refit_every: int):
    """Walk the variant at `horizon` over `rows` (a scratch panel without the term): `(result, levels, settings, features)`.

    Raises:
        LookAheadError: a row after the study's last day (`aligned_calendar_1027.require_study_window`).
    """

    from repo_model import measurement_fields

    m().require_study_window([row.date for row in rows])
    sd = m()._load("spread_distribution_634")
    features = variant_features(horizon)
    rows = dom_calendar.add_columns(rows)
    with m()._load("net_settlement").switched_on(), dom_calendar.switched_on():
        result, levels, settings = sd.walk(
            rows, fit=variant_fit(features), features=features, online_calibration=None, registry=measurement_fields.load_registry(),
            horizon=horizon, minimum_history=minimum_history, refit_every=refit_every, expected_levels=m().GRID,
        )
    return rows, result, levels, settings, features


def walk_command(args) -> int:
    m().committed_declaration(DECLARATION)
    h = args.horizon
    if h not in HORIZONS:
        raise SystemExit(f"lead {h} is not declared")
    m().require_study_window([m().LAST_TARGET])
    require_unlocked([m().LAST_TARGET], where="dom_level_term_1032")
    if m()._finished(args.output, DOM, h, args.published, args.panel):
        print(json.dumps({"variant": DOM, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    scratch = [row for row in load_daily_panel(args.panel) if row.date <= m().LAST_TARGET]
    audit_panel(scratch)
    rows, result, levels, settings, features = walk_rows(scratch, h, minimum_history=m().MINIMUM_HISTORY, refit_every=m().REFIT_EVERY)
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": DOM, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": DOM, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the reading rules (tested) ---------------------------------------------------------------------------------------


def bucket_label(day: date) -> str:
    return dom_calendar.label(day)


def reading(rows: Mapping[str, Optional[dict]]) -> List[str]:
    """The declared sentences, from the paired grid-CRPS rows of the variant over `gbm_funding_cal_direct` on the `pooled` cut, the `trough` cut
    (target days of the 19-23 bucket) and the `ordinary` cut (ordinary target days). A row is a paired row (`s761.paired_row`), an undefined one,
    or None (not scored). The lower end of a studentized two-sided 90% interval is the one-sided 95% lower bound."""

    s761 = m()._load("spread_mr_variants_761")

    def usable(name):
        row = rows.get(name)
        return row is not None and "undefined" not in row

    def text(name):
        row = rows[name]
        return f"skill {s761.pct(row['skill'])}, interval {s761.pct(row['skill_interval'][0])} to {s761.pct(row['skill_interval'][1])}"

    out = []
    for name, subject in (("pooled", "on all decision days"), ("trough", "on target days of the 19th to 23rd")):
        if not usable(name):
            out.append(f"{DOM} {subject}: not read (a cut is not scored or undefined).")
            continue
        helps = rows[name]["skill_interval"][0] > 0.0
        out.append(f"The day-of-month term {'helps' if helps else 'is not shown to help'} over gbm_funding_cal_direct {subject} ({text(name)}).")
    if usable("ordinary"):
        loses = rows["ordinary"]["skill_interval"][1] < 0.0
        out.append(f"It {'loses' if loses else 'does not lose'} on ordinary target days ({text('ordinary')}).")
    else:
        out.append("Ordinary target days: not read (a cut is not scored or undefined).")
    return out


# -- scoring -----------------------------------------------------------------------------------------------------------


def load_dom_walks(walks: Path, published: Path, panel: Path, frame):
    for h in HORIZONS:
        document = json.loads((walks / f"{DOM}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("variant") != DOM or document.get("scratch_panel_sha256") != panel_sha256(panel):
            raise ValueError(f"{DOM}_h{h}.json was not walked from scratch panel {panel_sha256(panel)} as {DOM}")
    return m().load_walks(walks, DOM, published, panel, frame)


def score_command(args) -> int:
    mod = m()
    b960 = mod._load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = mod.committed_declaration(DECLARATION)
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    pub = load_daily_panel(published)
    splits = load_split_declaration(mod.SPLITS)
    registry = json.loads(mod.SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, registry, s761.committed_declaration(b960.DECLARATION), walks)
    models = list(mod.BENCHMARKS) + [mod.CONTROL]
    present = [v for v in (mod.DIRECT, mod.ALIGNED) if all((walks / f"{v}_h{h}.json").is_file() for h in HORIZONS)]
    if mod.DIRECT not in present:
        raise ValueError(f"{mod.DIRECT} has no walks; the term is read against it")
    for variant in present:
        frame.forecasts[variant] = mod.load_walks(walks, variant, published, panel_path, frame)
        models.append(variant)
    frame.forecasts[DOM] = load_dom_walks(walks, published, panel_path, frame)
    models.append(DOM)
    days = [d for d in frame.days if all(d in frame.forecasts[name] for name in models)]
    frame.days = days
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    frame.forecasts[mod.CONTROL] = frame.forecasts.pop(b960.GBM)
    notes["scored_decision_days"] = len(days)

    cells = {(label, name): s686.cell_scores(frame, name, fn) for label, fn in mod.METRICS for name in models}
    series: Dict = {}
    for label, _ in mod.METRICS:
        series[("decision", label)] = {name: s686.by_decision(cells[(label, name)]) for name in models}
        series[("target", label)] = {name: s686.by_target(frame, cells[(label, name)]) for name in models}
    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    labels = {
        "regime": {t: frame.regime(t) for t in targets},
        "target_type": {t: mod.target_type(frame, t) for t in targets},
        "dom_bucket": {t: bucket_label(t) for t in targets},
    }
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, mapping in labels.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    groups[("target_type", "calendar_days")] = ("target", [d for d in targets if labels["target_type"][d] in mod.CALENDAR_TYPES])

    references = [mod.DIRECT] + [v for v in (mod.ALIGNED,) if v in present] + [mod.CONTROL] + list(mod.BENCHMARKS)
    pairs = [(DOM, b) for b in references]
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < mod.MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in mod.METRICS:
            for candidate, benchmark in pairs:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
    mod._SERIES.update(series)
    mod._SERIES.update({"draws": args.draws, "s761": s761})
    with mock.patch.object(mod, "SEED", SEED), multiprocessing.get_context("fork").Pool(args.workers) as pool:
        out = pool.map(mod._task, jobs, chunksize=1)

    result: dict = {
        "issue": 1032, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models, "pairs": [list(p) for p in pairs],
        "means": {label: {name: sum(series[("decision", label)][name].values()) / len(days) for name in models} for label, _ in mod.METRICS},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"],
        "not_run": {} if mod.ALIGNED in present else {mod.ALIGNED: "no walks in the folder; not a reference here"},
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = mod._SERIES[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {n: sum(ser[n][d] for d in members) / len(members) for n in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(split, label, reference):
        return result["groups"].get(split, {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{DOM} vs {reference}")

    cuts = {"pooled": pick("pooled", "all decision days", mod.DIRECT), "trough": pick("dom_bucket", "19-23", mod.DIRECT), "ordinary": pick("target_type", "ordinary", mod.DIRECT)}
    result["reading_rules"] = reading(cuts)
    result["reading_over_gbm_funding"] = mod.reading_rules(
        {DOM: {"calendar": pick("target_type", "calendar_days", mod.CONTROL), "ordinary": pick("target_type", "ordinary", mod.CONTROL)}}
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


def render_report(r: dict, s761) -> str:
    mod = m()
    with mock.patch.dict(mod.SPLIT_TITLES, {"dom_bucket": "day of month of the target day (bucket)"}):
        text = mod.render_report(r, s761)
    lines = text.splitlines()
    lines[0] = "# gbm_funding_cal_direct with a day-of-month level term (#1032): development data, not a verdict"
    at = next(i for i, line in enumerate(lines) if line.startswith("Replacing the candidate"))
    lines[at:at + 1] = ["Against gbm_funding (calendar days and ordinary days, #1027's reading): " + " ".join(r["reading_over_gbm_funding"]), "",
                        "Adopting the term, or naming it with a variant of #1027 as the candidate, is a marked question for Eleonora; this page does not decide it."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(run=declare_command)
    walk = sub.add_parser("walk")
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
