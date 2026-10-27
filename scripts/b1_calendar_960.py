"""B1', the calendar-aware persistence, on real data, and the paired test of gbm_funding against it (#960; H5 step 5, H1 step 3).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/b1_calendar_960.json`, which this script refuses to read unless it is committed and unchanged.
B1' is `repo_model.b1_calendar`; the transparent model is #761's `spread_mr_ctx`; `gbm_funding` is #634's walk, read through
`scripts/h5_splits_805.py` from a walks directory (a needs-mac input: the walks take hours). Scored with the scorer of
scoring protocol v1 (`repo_model.scoring_protocol`, #655) at the development tier, with the studentized stationary
bootstrap of ruling 1 (#739). Scored days are decision days whose five targets are on or before 2025-12-31
(`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    # the arms that need no walks (B1, B2, B1', spread_mr_ctx):
    PYTHONPATH=src python3 scripts/b1_calendar_960.py score --panel /tmp/funding_panel.csv --output OUT/score.json --markdown OUT/report.md
    # all arms: --panel is the PUBLISHED.csv that #634's gbm_funding walks were made from (the same build), --walks their directory,
    # made as in the docstring of scripts/spread_distribution_634.py (only the five gbm_funding files are read):
    PYTHONPATH=src python3 scripts/b1_calendar_960.py score --panel /tmp/funding_panel.csv --walks WALKS \\
        --output OUT/score.json --markdown OUT/report.md

Stdlib only.
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


from repo_model import turn_days  # noqa: E402
from repo_model import b1_calendar as b1c, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

s761 = _load("spread_mr_variants_761")
s686 = s761.s686

DECLARATION = REPO / "metadata" / "b1_calendar_960.json"
SEED = 960
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
CTX = "spread_mr_ctx"
B1P = "B1_prime"
GBM = "gbm_funding"
MME = 0.03
METRICS = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
#: [candidate, benchmark]; the gbm pairs are skipped when no walks are given.
PAIRS = (
    (GBM, CTX), (GBM, B1P), (CTX, B1P), (GBM, "B1"), (GBM, "B2"), (CTX, "B1"), (CTX, "B2"), (B1P, "B1"), (B1P, "B2"),
)
ORDER_REGIME = ["2018-19", "2020", "2021-23", "2024", "2025-26"]


# -- the reading rules (tested) ------------------------------------------------------------------------------------


def reading_rules(rows: Mapping[str, dict]) -> List[str]:
    """The two sentences the declaration fixes, from the paired rows `ordinary` and `pooled` of gbm_funding.

    `rows` maps "gbm_vs_ctx_ordinary" and "gbm_vs_b1p_pooled" to a paired row (`s761.paired_row`) or an undefined one.
    The one-sided 95% lower bound of a skill is the lower end of its studentized two-sided 90% interval.
    """

    out = []
    gbm_ctx = rows.get("gbm_vs_ctx_ordinary")
    if gbm_ctx is None:
        out.append("gbm_funding against spread_mr_ctx on ordinary targets: not scored (the gbm walks are absent).")
    elif "undefined" in gbm_ctx:
        out.append("gbm_funding against spread_mr_ctx on ordinary targets: undefined (%s)." % gbm_ctx["undefined"])
    elif gbm_ctx["skill_interval"][0] < 0.0:
        out.append("The gbm is not shown to carry anything beyond the transparent model: its skill over spread_mr_ctx on "
                   "ordinary targets is %s with a one-sided 95%% lower bound of %s, below 0."
                   % (s761.pct(gbm_ctx["skill"]), s761.pct(gbm_ctx["skill_interval"][0])))
    else:
        out.append("gbm_funding's skill over spread_mr_ctx on ordinary targets is %s with a one-sided 95%% lower bound of %s, "
                   "not below 0." % (s761.pct(gbm_ctx["skill"]), s761.pct(gbm_ctx["skill_interval"][0])))
    gbm_b1p = rows.get("gbm_vs_b1p_pooled")
    if gbm_b1p is None:
        out.append("gbm_funding against B1': not scored (the gbm walks are absent).")
    elif "undefined" in gbm_b1p:
        out.append("gbm_funding against B1', pooled: undefined (%s)." % gbm_b1p["undefined"])
    elif gbm_b1p["skill"] < MME:
        out.append("The MME as set (3%% against B1) is not reachable by this candidate against B1': its pooled skill over B1' "
                   "is %s, below 3%%." % s761.pct(gbm_b1p["skill"]))
    else:
        out.append("gbm_funding's pooled skill over B1' is %s, not below the 3%% of the MME as set." % s761.pct(gbm_b1p["skill"]))
    return out


# -- the frame -----------------------------------------------------------------------------------------------------


def load_gbm(walks: Path, panel_sha: str, frame) -> Dict[date, Dict[int, List[float]]]:
    """gbm_funding's forecast on each decision day #634's walks cover, a missing lead standing in as B1, as #634 and #805 fill it.

    The five lead files `gbm_funding_h<h>.json` are #634's (`spread_distribution_634.py walk`), and must have been walked
    on the panel being scored: each carries the digest of the published panel it was walked from.

    Raises:
        ValueError: a walk was made from another panel.
        LookAheadError: a scored day is in a locked tier.
    """

    sd = _load("spread_distribution_634")
    for h in sp.HORIZONS:
        document = json.loads((walks / f"{GBM}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("panel_sha256") != panel_sha:
            raise ValueError(f"{GBM}_h{h}.json was walked from panel {document.get('panel_sha256')}, not {panel_sha}")
    decisions, walked = sd.lead_forecasts(sd.load_laws(walks, GBM), frame.dates)
    usable = [d for d in walked if frame.target(d, max(sp.HORIZONS)) <= LAST_DAY and d in frame.forecasts["B1"]]
    sd.refuse_locked(usable + [frame.target(d, h) for d in usable for h in sp.HORIZONS])
    b1 = {d: frame.forecasts["B1"][d] for d in usable}
    return sp.fill_missing({d: decisions[d] for d in usable}, b1, usable).forecasts


def build_frame(panel, panel_sha, splits, registry, declaration, walks: Optional[Path] = None):
    """#761's frame (B1, B2, the reference and the variants), with B1' added, and gbm_funding when the walks are given."""

    frame, notes, walk = s761.build_frame(panel, splits, registry, declaration)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    b1p, missing = {}, []
    for day in frame.days:
        try:
            b1p[day] = b1c.b1_calendar_forecast(panel, frame.position[day], **settings)
        except sp.ProtocolError:
            missing.append(day)
    days = [d for d in frame.days if d in b1p]
    gbm_notes = None
    if walks is not None:
        gbm = load_gbm(walks, panel_sha, frame)
        common = [d for d in days if d in gbm]
        gbm_notes = {"gbm_days": len(gbm), "transparent_days": len(days), "common_days": len(common)}
        frame.forecasts[GBM] = {d: gbm[d] for d in common}
        days = common
    frame.days = days
    frame.forecasts[B1P] = {d: b1p[d] for d in days}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes.update({"scored_decision_days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat(),
                  "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
                  "b1_prime_missing": [d.isoformat() for d in missing], "gbm": gbm_notes})
    return frame, notes


def groupings(frame) -> Dict[str, Tuple[str, Dict]]:
    """Each split: its grain ('target' or 'decision') and its day -> label map."""

    days = frame.days
    targets = sorted({frame.target(d, h) for d in days for h in sp.HORIZONS})
    anchors = {}
    for d in days:
        a = pb._anchor(frame.panel, frame.position[d], frame.registry, DECISION_TIME)
        anchors[d] = turn_days.reporting_day_type(frame.splits, frame.panel[a].date, frame.panel[a].values)
    return {
        "regime": ("target", {t: frame.regime(t) for t in targets}),
        "target_type": ("target", {t: frame.day_type(t) for t in targets}),
        "anchor_type": ("decision", anchors),
    }


# -- the tests, in parallel ----------------------------------------------------------------------------------------

_SERIES: Dict = {}


def _task(job):
    key, metric, candidate, benchmark, days = job
    series = _SERIES[(key[0], metric)]
    row = s761.run_pairs({benchmark: series[benchmark]}, series[candidate], days, seed=SEED, draws=_SERIES["draws"])[benchmark]
    return key, metric, candidate, benchmark, row


def run_jobs(jobs, workers: int):
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        return pool.map(_task, jobs, chunksize=1)


def score(args) -> int:
    declaration = s761.committed_declaration(DECLARATION)
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s761.SPLITS)
    registry = json.loads(s761.SOURCES.read_text(encoding="utf-8"))
    walks = Path(args.walks) if args.walks else None
    frame, notes = build_frame(panel, panel_sha256(panel_path), splits, registry, declaration, walks)
    days = frame.days
    models = ["B1", "B2", B1P, CTX] + ([GBM] if walks else [])
    pairs = [(c, b) for c, b in PAIRS if c in models]

    cells = {(m_label, m): s686.cell_scores(frame, m, fn) for m_label, fn in METRICS for m in models}
    for m_label, fn in METRICS:
        for m in models:
            official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=fn)
            mine = s686.by_decision(cells[(m_label, m)])
            if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
                raise SystemExit(f"{m_label} of {m}: the cell means differ from scoring_protocol.day_scores")

    # reproduction: with the transparent days, B1, B2 and spread_mr_ctx reproduce #761's pooled means
    reproduced = None
    if not walks:
        prior = json.loads((REPO / "docs/pivot/evidence/spread-mr-variants/score.json").read_text(encoding="utf-8"))
        reproduced = {}
        for m in ("B1", "B2", CTX):
            mine = sum(s686.by_decision(cells[("grid_crps", m)]).values()) / len(days)
            reproduced[m] = {"here": mine, "761": prior["means"]["grid_crps"][m]}
            if abs(mine - prior["means"]["grid_crps"][m]) > 1e-9:
                raise SystemExit(f"grid CRPS of {m} does not reproduce #761's page: {mine} against {prior['means']['grid_crps'][m]}")

    series: Dict = {}
    for m_label, _ in METRICS:
        series[("decision", m_label)] = {m: s686.by_decision(cells[(m_label, m)]) for m in models}
        series[("target", m_label)] = {m: s686.by_target(frame, cells[(m_label, m)]) for m in models}
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    for split, (grain, labels) in groupings(frame).items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(labels):
            by_label.setdefault(labels[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = (grain, members)

    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for m_label, _ in METRICS:
            for candidate, benchmark in pairs:
                jobs.append(((grain, f"{split}/{label}"), m_label, candidate, benchmark, tuple(members)))
    _SERIES.update(series)
    _SERIES["draws"] = args.draws
    out = run_jobs(jobs, args.workers)

    result: dict = {
        "issue": 960, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models,
        "pairs": [list(p) for p in pairs], "reproduced_761": reproduced,
        "means": {ml: {m: sum(series[("decision", ml)][m].values()) / len(days) for m in models} for ml, _ in METRICS},
        "groups": {}, "skipped_groups": skipped,
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(groups[(split, label)][1]), "metrics": {}})
        ser = _SERIES[(grain, metric)]
        members = groups[(split, label)][1]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row
    pick = lambda split, label, c, b: result["groups"].get(split, {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{c} vs {b}")
    result["reading_rules"] = reading_rules({
        k: v for k, v in (("gbm_vs_ctx_ordinary", pick("target_type", "ordinary", GBM, CTX)),
                          ("gbm_vs_b1p_pooled", pick("pooled", "all decision days", GBM, B1P))) if v is not None})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result), encoding="utf-8")
    return 0


# -- Markdown ------------------------------------------------------------------------------------------------------

LABELS = {GBM: "gbm_funding (#634)", CTX: "spread_mr_ctx (#761)", B1P: "B1' (#960)", "B1": "B1", "B2": "B2"}
SPLIT_TITLES = {"pooled": "pooled (decision days)", "regime": "regime (target day)",
                "target_type": "reporting day type (target day)", "anchor_type": "anchor day type (decision)"}
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}


def _labels(split: str, labels) -> List[str]:
    if split == "regime":
        return [l for l in ORDER_REGIME if l in labels] + [l for l in labels if l not in ORDER_REGIME]
    return sorted(labels, key=lambda l: (l != "ordinary", l))


def render_report(r: dict) -> str:
    n = r["notes"]
    lines = [
        "# B1' (a calendar-aware persistence) and gbm_funding, paired (#960): development data, not a verdict", "",
        f"Panel `{r['panel_sha256']}`. Declaration `{r['declaration']}`. Seed {r['seed']}, {r['draws']} draws, the studentized "
        f"stationary bootstrap (block 10). Decision days {n['first']} to {n['last']} (last target {n['last_target']}): "
        f"{n['scored_decision_days']} days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours "
        "the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound).", ""]
    if n.get("gbm"):
        g = n["gbm"]
        lines += [f"gbm_funding days {g['gbm_days']:,}; transparent arms {g['transparent_days']:,}; common {g['common_days']:,}.", ""]
    else:
        lines += ["**The gbm_funding arms are not scored here:** its per-day forecasts are #634's walks, which are run on the Mac "
                  "(#46's rule on long runs; #905 has not committed them). Only the arms that need no walks are scored.", ""]
    lines += ["## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {LABELS[m]} | " + " | ".join(f"{r['means'][ml][m]:.4f}" for ml in r["means"]) + " |")
    lines.append("")
    if r.get("reproduced_761"):
        lines += ["Reproduction: mean grid CRPS of B1, B2 and spread_mr_ctx equals #761's page "
                  "(" + ", ".join(f"{m} {v['here']:.4f}" for m, v in r["reproduced_761"].items()) + ").", ""]
    lines += ["## Reading rules (declared)", ""] + [f"- {s}" for s in r["reading_rules"]] + [""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            lines += [f"### {SPLIT_TITLES[split]}", ""]
            pairs = [f"{c} vs {b}" for c, b in r["pairs"]]
            lines += ["| group | days | " + " | ".join(f"{LABELS[p.split(' vs ')[0]]} over {LABELS[p.split(' vs ')[1]]}" for p in pairs) + " |",
                      "|---|---|" + "---|" * len(pairs)]
            for label in _labels(split, r["groups"][split]):
                entry = r["groups"][split][label]
                cells = entry["metrics"].get(metric, {}).get("pairs", {})
                lines.append(f"| {label} | {entry['days']:,} | " + " | ".join(s761.skill_text(cells[p]) if p in cells else "n/a" for p in pairs) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("score")
    one.add_argument("--panel", required=True)
    one.add_argument("--walks")
    one.add_argument("--output", required=True)
    one.add_argument("--markdown")
    one.add_argument("--draws", type=int, default=sp.DRAWS)
    one.add_argument("--workers", type=int, default=multiprocessing.cpu_count())
    args = parser.parse_args(argv)
    return score(args)


if __name__ == "__main__":
    sys.exit(main())
