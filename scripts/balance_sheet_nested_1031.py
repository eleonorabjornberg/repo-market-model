"""The G-SIB and foreign-bank balance-sheet days, re-dated onto the turn days and nested into the calendar-aware candidate (#1031, H5 step 2 / H6 step 1).

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and
nothing into `docs/runs/`, registers nothing and changes no rule, no published model, no published declaration and no published figure. Every choice
is in `metadata/balance_sheet_nested_1031.json`, which `walk` and `score` refuse to read unless it is committed and unchanged; `declare` writes it from
the constants below and was run, and its output committed, before any number was computed. No day after 2025-12-31 and no day of a locked tier is
read (`docs/decisions/lockbox.md`).

**The design.** Five-lens review, Lens A (#958): the flags of `repo_model.balance_sheet_days` (#427) sit on run-up days the panel shows are cold (quarter-end
2nd- and 3rd-last), so nested as coded they fail for the wrong reason. Two arms, each the #1027 direct-pairs candidate (`gbm_funding_cal_direct`: the
published inputs, the calendar columns at the target day, `treasury_settlement` at lead 1, leaf 5, direct pairs) plus three flag columns and nothing else:

* `gbm_funding_cal_direct_bs_coded`: the three flags as coded (`balance_sheet_days.flags`: the last 3 business days of a quarter, the last business day of
  other months, the last 5 of December);
* `gbm_funding_cal_direct_bs_turn`: the same three rules on the turn days of #959 (`balance_sheet_days.relabelled_flags`: the last business day and the
  first business day after it; December its own type).

Each flag is a function of the row's own date and the market holiday table alone (scheduled, known in advance), written about the target day
(`target_day_columns`), so `asof` rule 2 serves it from the scored row at every lead and a direct pair trains it from its own target row. The page reads
with and without the relabel: the coded arm is the "without". Adopting the relabel is Eleonora's (a data meaning) and is off in every published
declaration.

The base walks (`gbm_funding_cal_direct`) and the control's (`gbm_funding`) are #1027's, on her Mac; copy them next to the new ones. The new walks are long
(`needs-mac`, #46); `score` reads all of them.

    # PUB.csv, AUG3.csv: as in scripts/aligned_calendar_1027.py's docstring (the same panels); WALKS holds #1027's gbm_funding and gbm_funding_cal_direct walks
    PYTHONPATH=src python3 scripts/balance_sheet_nested_1031.py declare           # then commit metadata/balance_sheet_nested_1031.json before any score
    for h in 1 2 3 4 5; do for a in gbm_funding_cal_direct_bs_coded gbm_funding_cal_direct_bs_turn; do
        OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/balance_sheet_nested_1031.py walk --arm $a --horizon $h \\
            --published PUB.csv --panel AUG3.csv --output WALKS/${a}_h$h.json; done; done
    PYTHONPATH=src python3 scripts/balance_sheet_nested_1031.py score --published PUB.csv --panel AUG3.csv --walks WALKS \\
        --output OUT/score.json --markdown OUT/report.md
"""

from __future__ import annotations

import argparse
import contextlib
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


from repo_model import asof, balance_sheet_days as bsd, contract, scoring_protocol as sp, turn_days as td  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

a1027 = _load("aligned_calendar_1027")

DECLARATION = REPO / "metadata" / "balance_sheet_nested_1031.json"
SPLITS = a1027.SPLITS
LAST_TARGET = a1027.LAST_TARGET
SEED = 1031
HORIZONS = sp.HORIZONS
MIN_GROUP_DAYS = a1027.MIN_GROUP_DAYS
ORDER_REGIME = a1027.ORDER_REGIME

#: the #1027 direct-pairs candidate the flags are nested into, and the H5 candidate still in force (Eleonora, 21 October 2026, on #1027)
BASE = a1027.DIRECT
CONTROL = a1027.CONTROL
CODED = "gbm_funding_cal_direct_bs_coded"
TURN = "gbm_funding_cal_direct_bs_turn"
ARMS = (CODED, TURN)
_KIND = {CODED: "coded", TURN: "turn"}
_COLUMNS = {CODED: bsd.CODED_COLUMNS, TURN: bsd.TURN_COLUMNS}
BENCHMARKS = ("B1", "B2")
METRICS = a1027.METRICS
#: the day groups the page reports, each a cut of target days (they overlap as declared)
CUTS = ("turn_days", "coded_days", "unflagged", "penultimate", "december_26")
CUT_TITLES = {
    "turn_days": "turn days (all three relabelled labels: the relabelled flags' days)",
    "coded_days": "as-coded flag days (the run-up windows)",
    "unflagged": "days neither set flags",
    "penultimate": "penultimate days (second-last business day of a month)",
    "december_26": "26 December",
}
#: each arm's own flagged days: where its three flags can move a forecast
OWN_CUT = {CODED: "coded_days", TURN: "turn_days"}


def __getattr__(name):  # DECISION, read lazily: #634's script loads the whole scoring stack
    if name == "DECISION":
        return a1027.decision_time()
    raise AttributeError(name)


# -- the arms --------------------------------------------------------------------------------------------------------


def arm_columns(arm: str) -> Tuple[str, ...]:
    """The three flag columns an arm adds to the base candidate's inputs.

    Raises:
        ValueError: `arm` is not a declared arm.
    """

    if arm not in _COLUMNS:
        raise ValueError(f"{arm!r} is not a declared arm; one of {', '.join(ARMS)}")
    return _COLUMNS[arm]


def arm_features(arm: str, horizon: int) -> Tuple[str, ...]:
    """The base candidate's inputs at the lead, then the arm's three flag columns."""

    return a1027.variant_features(BASE, horizon) + arm_columns(arm)


def with_flags(rows: Sequence[DailyObservation], arm: str) -> List[DailyObservation]:
    """`rows` with the arm's three flag columns, each from its own row's date."""

    arm_columns(arm)
    return bsd.add_columns(rows, _KIND[arm])


def arm_fit(arm: str, features: Sequence[str]):
    """The arm's fitter: the base candidate's, on direct pairs, with the flag columns among the regressors."""

    arm_columns(arm)
    return a1027.variant_fit(BASE, features)


def registry() -> dict:
    from repo_model import measurement_fields

    return measurement_fields.load_registry()


@contextlib.contextmanager
def switched(arm: str) -> Iterator[None]:
    """#1027's switched-on inputs (net settlement, the measurement fields) and the arm's flags as calendar columns, for this run only.

    The flags are known in advance and written about the target day: `asof` rule 2 reads them from the scored row whatever the lead.
    """

    calendar = contract.CALENDAR_FEATURES | frozenset(arm_columns(arm))
    with a1027._load("net_settlement").switched_on(), mock.patch.object(contract, "CALENDAR_FEATURES", calendar), mock.patch.object(
        asof, "CALENDAR_FEATURES", calendar
    ):
        yield


# -- the declaration -------------------------------------------------------------------------------------------------


def declaration_document() -> dict:
    return {
        "status": "declared by the pull request that closes #1031 before any number was computed; a measurement, not a record. Nothing is published: neither arm joins any published declaration, no day after 2025-12-31 is scored (docs/decisions/lockbox.md), no rule changes, the live record and pin do not move. Development data gives no verdict (scoring protocol v1, #46).",
        "issue": 1031,
        "hypothesis": "H5 step 2 and H6 step 1 (nest the balance-sheet days after the turn relabel; five-lens review, Lens A, #958, #950 row 5)",
        "ruling": "Eleonora, 19 and 20 October 2026 (the queue's guide, #958); calendar first, 20 October 2026: the model it changes reads calendar days at the target day, on direct pairs",
        "adoption": "the relabel is not adopted here: adopting the turn label is Eleonora's (a data meaning, #959 criterion 4). The page reads with it (arm bs_turn) and without it (arm bs_coded); the columns are off in every published declaration",
        "base": {
            "model": BASE,
            "what": "#1027's direct-pairs candidate: gbm_funding's published inputs at the lead, the calendar columns at the target day at every lead, treasury_settlement and its parts at lead 1, net_settlement and net_settlement_due_5d as observed; leaf 5; direct pairs (training_pairs='direct'); passes the #947 guard, which checks one-step fits only",
            "walks": "#1027's, on Eleonora's Mac (not committed): WALKS/gbm_funding_cal_direct_h1..5.json, from the same published panel and scratch panel; score refuses walks from other panels",
            "control": "gbm_funding, #634's walks, the H5 candidate in force (Eleonora, 21 October 2026, on #1027: keep it for now and adopt nothing yet)",
        },
        "arms": {
            CODED: {
                "flags": "repo_model.balance_sheet_days.flags: foreign_bank_quarter_end = the last 3 business days of March, June, September, December; foreign_bank_month_end = the last business day of a month that is not a quarter's last; gsib_year_end = the last 5 business days of December",
                "columns": list(bsd.CODED_COLUMNS),
            },
            TURN: {
                "flags": "repo_model.balance_sheet_days.relabelled_flags, on the turn days of #959 (repo_model.turn_days): foreign_bank_quarter_end = the quarter's last business day and the first business day after it, for March, June, September and December; foreign_bank_month_end = the last business day and the first business day after it, in a month that is not a quarter's last; gsib_year_end = the last business day of December and the first business day of January. No other change: the rules, their sources, their public_from gates and their names are the coded ones",
                "columns": list(bsd.TURN_COLUMNS),
            },
        },
        "december": "December is its own type: the year-end turn carries gsib_year_end and, as the rule names December among the quarter-ends, foreign_bank_quarter_end too. 26 December is flagged by no relabelled rule (the coded gsib window held it) and is reported as its own row. Whether the December turn should carry the quarter flag as well is a marked question for Eleonora",
        "same_in_both": "the only difference between the arms is the dates of three columns; inputs, leaf, seed, fold grid, refit cadence (21 scored days, 61 minimum history) and quantile grid are the base's",
        "calendar_first": "each flag is a function of the row's own date and metadata/market_holidays.json (scheduled, known in advance), written about the target day: declared in repo_model.target_day_columns, served from the scored row by asof rule 2 at every lead h = 1 to 5, and trained from the pair's own target row by direct pairs; a one-step fit on any of them is refused by the #947 guard",
        "benchmarks": [CONTROL, BASE, "B1", "B2"],
        "pairs": [[arm, other] for arm in ARMS for other in (BASE, "B2", "B1", CONTROL)] + [[TURN, CODED], [BASE, "B2"]],
        "metrics": ["grid_crps", "upper_tail_twcrps"],
        "cuts": {
            "pooled": "all scored decision days",
            "regimes": ORDER_REGIME,
            "target_day_types": "the turn labels of #959 on the target day: turn, quarter_end_turn, year_end, tax_date, ordinary",
            "day_groups": {
                "turn_days": "target days labelled turn, quarter_end_turn or year_end: exactly the days the relabelled flags fire on",
                "coded_days": "target days on which any as-coded flag fires",
                "unflagged": "target days on which neither set fires",
                "penultimate": "the month's second-last business day (turn_days.penultimate_day), reported alone",
                "december_26": "26 December, reported alone",
            },
            "minimum": f"a group of fewer than {MIN_GROUP_DAYS} target days is listed and not tested; every group lists its day count",
        },
        "interval": "stationary bootstrap, seed 1031, the studentized interval of ruling 1 (#739); the lower end of the two-sided 90% interval is the one-sided 95% lower bound",
        "caveat": "Lens C of #958: the lag-10 standard error behind the block length is itself noisy on this many days; every interval here is read with that in mind",
        "reading_rules": {
            "beats_its_base": "an arm beats gbm_funding_cal_direct on its flagged days when the lower end of its grid-CRPS skill interval over the base on its own cut (bs_coded: coded_days, bs_turn: turn_days) is above 0",
            "does_not_lose_elsewhere": "and does not lose on days neither set flags when the upper end of its skill interval over the base there is 0 or more; 'loses' means an interval wholly below 0",
            "against_b2": "the same sentence is written for each arm against B2 on the same days",
            "relabel": "the turn arm over the coded arm on the turn days is the relabel's own effect; it is read the same way and never decides adoption",
            "no_verdict": "development data gives no verdict",
        },
        "variants": {
            CODED: {"label": "the base plus the three flags as coded", "run": True},
            TURN: {"label": "the base plus the three flags on the turn days", "run": True},
        },
        "walk_time": "the base's own direct walks took several hours on Eleonora's Mac (#1027); this is two arms of five leads: needs-mac, overnight (#46)",
        "limits": [
            "no day after 2025-12-31",
            "no lockbox day",
            "no published record, declaration or decided value is edited; adopting the relabel is Eleonora's",
            "gbm_funding's declaration, scripts/final_test_preregistration.py and the aligned (one-step) variant of #1027 are not touched",
        ],
        "questions_for_eleonora": [
            "adopt the turn relabel for the balance-sheet flags (and so for any published declaration that carries them)? Default: no, leave it off",
            "should the December turn carry foreign_bank_quarter_end as well as gsib_year_end (as here), or gsib_year_end alone? Default: both, as the rule names December among the quarter-ends",
        ],
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION.relative_to(REPO))}))
    return 0


# -- the walk --------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    committed_declaration()
    sd = _load("spread_distribution_634")
    arm, h = args.arm, args.horizon
    if arm not in ARMS or h not in HORIZONS:
        raise SystemExit(f"arm {arm!r} / lead {h} is not declared")
    a1027.require_study_window([LAST_TARGET])
    require_unlocked([LAST_TARGET], where="balance_sheet_nested_1031")
    if a1027._finished(args.output, arm, h, args.published, args.panel):
        print(json.dumps({"arm": arm, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    audit_panel(load_daily_panel(args.published))
    scratch = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(scratch)
    rows = with_flags(scratch, arm)
    features = arm_features(arm, h)
    with switched(arm):
        result, levels, settings = sd.walk(
            rows, fit=arm_fit(arm, features), features=features, online_calibration=None, registry=registry(),
            horizon=h, minimum_history=a1027.MINIMUM_HISTORY, refit_every=a1027.REFIT_EVERY, expected_levels=a1027.GRID,
        )
    laws = {rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": arm, "horizon": h, "levels": levels, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "flag_columns": list(arm_columns(arm)), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"arm": arm, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


def committed_declaration() -> dict:
    return a1027.committed_declaration(DECLARATION)


# -- the groups (tested) -----------------------------------------------------------------------------------------------


def day_flags(days: Sequence[date]) -> Dict[date, Dict[str, bool]]:
    """Each day's membership of the declared cuts, from the date and the holiday table alone."""

    out = {}
    for day in days:
        turn = td.turn_label(day) is not None
        coded = any(value == 1.0 for value in bsd.flags(day, day).values())
        out[day] = {
            "turn_days": turn,
            "coded_days": coded,
            "unflagged": not turn and not coded,
            "penultimate": td.penultimate_day(day),
            "december_26": td.december_26(day),
        }
    return out


def reading_rules(cells: Mapping[str, Mapping[str, Optional[dict]]]) -> List[str]:
    """The declared sentence per arm, from its paired grid-CRPS rows over a reference on its own flagged days and on the unflagged days.

    `cells[arm]` maps "flagged" and "unflagged" to a paired row (`s761.paired_row`), an undefined one, or None (not scored). The lower end of a
    studentized two-sided 90% interval is the one-sided 95% lower bound.
    """

    s761 = a1027._load("spread_mr_variants_761")
    out = []
    for arm, group in cells.items():
        flagged, other = group.get("flagged"), group.get("unflagged")
        if flagged is None or other is None or "undefined" in flagged or "undefined" in other:
            out.append(f"{arm}: not read (a cut is not scored or undefined).")
            continue
        beats = flagged["skill_interval"][0] > 0.0
        loses = other["skill_interval"][1] < 0.0
        out.append(
            f"{arm} {'beats' if beats else 'is not shown to beat'} the reference on its flagged days (skill {s761.pct(flagged['skill'])}, one-sided 95% lower bound "
            f"{s761.pct(flagged['skill_interval'][0])}) and {'loses' if loses else 'does not lose'} on days neither set flags (skill {s761.pct(other['skill'])}, "
            f"interval {s761.pct(other['skill_interval'][0])} to {s761.pct(other['skill_interval'][1])})."
        )
    return out


def target_label(frame, day: date) -> str:
    """The target day's turn label (`turn_days.turn_day_type`), the tax-date column read at the day."""

    return td.turn_day_type(day, tax_date=float(frame.values[day]["tax_date"]) == 1.0)


# -- the score -------------------------------------------------------------------------------------------------------


def load_arm_walks(walks: Path, arm: str, published: Path, panel: Path, frame):
    """The arm's forecast on each decision day, after checking its five walks came from these panels with these inputs."""

    for h in HORIZONS:
        document = json.loads((walks / f"{arm}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("scratch_panel_sha256") != panel_sha256(panel):
            raise ValueError(f"{arm}_h{h}.json was walked from scratch panel {document.get('scratch_panel_sha256')}, not {panel_sha256(panel)}")
        if document.get("features") != list(arm_features(arm, h)):
            raise ValueError(f"{arm}_h{h}.json was walked on inputs other than the declared ones")
    return a1027.load_walks(walks, arm, published, panel, frame)


def score_command(args) -> int:
    b960 = _load("b1_calendar_960")
    s761, s686 = b960.s761, b960.s686
    declaration = committed_declaration()
    published, panel_path, walks = Path(args.published), Path(args.panel), Path(args.walks)
    for name in (BASE,) + ARMS:
        missing = [h for h in HORIZONS if not (walks / f"{name}_h{h}.json").is_file()]
        if missing:
            raise ValueError(f"{name} has no walk for leads {missing}; walk every lead of both arms and the base before scoring")
    pub = load_daily_panel(published)
    splits = load_split_declaration(SPLITS)
    reg = json.loads(a1027.SOURCES.read_text(encoding="utf-8"))
    frame, notes = b960.build_frame(pub, panel_sha256(published), splits, reg, s761.committed_declaration(b960.DECLARATION), walks)
    frame.forecasts[CONTROL] = frame.forecasts.pop(b960.GBM)
    models = list(BENCHMARKS) + [CONTROL, BASE] + list(ARMS)
    frame.forecasts[BASE] = a1027.load_walks(walks, BASE, published, panel_path, frame)
    for arm in ARMS:
        frame.forecasts[arm] = load_arm_walks(walks, arm, published, panel_path, frame)
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
    targets = sorted({frame.target(d, h) for d in days for h in HORIZONS})
    flags = day_flags(targets)
    groups: Dict[Tuple[str, str], Tuple[str, List[date]]] = {("pooled", "all decision days"): ("decision", list(days))}
    labelled = {"regime": {t: frame.regime(t) for t in targets}, "target_type": {t: target_label(frame, t) for t in targets}}
    for split, mapping in labelled.items():
        by_label: Dict[str, List[date]] = {}
        for day in sorted(mapping):
            by_label.setdefault(mapping[day], []).append(day)
        for label, members in by_label.items():
            groups[(split, label)] = ("target", members)
    for cut in CUTS:
        groups[("cut", cut)] = ("target", [t for t in targets if flags[t][cut]])

    pairs = [(arm, other) for arm in ARMS for other in (BASE, "B2", "B1", CONTROL)] + [(TURN, CODED), (BASE, "B2")]
    jobs, skipped = [], {}
    for (split, label), (grain, members) in groups.items():
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric, _ in METRICS:
            for candidate, benchmark in pairs:
                jobs.append(((grain, f"{split}/{label}"), metric, candidate, benchmark, tuple(members)))
    a1027._SERIES.update(series)
    a1027._SERIES.update({"draws": args.draws, "s761": s761})
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        out = pool.map(a1027._task, jobs, chunksize=1)

    result: dict = {
        "issue": 1031, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(published), "scratch_panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "notes": notes, "models": models, "pairs": [list(p) for p in pairs],
        "means": {label: {m: sum(series[("decision", label)][m].values()) / len(days) for m in models} for label, _ in METRICS},
        "groups": {}, "skipped_groups": skipped, "declared_reading_rules": declaration["reading_rules"],
    }
    for (grain, name), metric, candidate, benchmark, row in out:
        split, label = name.split("/", 1)
        members = groups[(split, label)][1]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members), "metrics": {}})
        ser = a1027._SERIES[(grain, metric)]
        entry["metrics"].setdefault(metric, {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in models}, "pairs": {}})
        entry["metrics"][metric]["pairs"][f"{candidate} vs {benchmark}"] = row

    def pick(split, label, candidate, reference):
        return result["groups"].get(split, {}).get(label, {}).get("metrics", {}).get("grid_crps", {}).get("pairs", {}).get(f"{candidate} vs {reference}")

    result["reading_rules"] = {}
    for reference in (BASE, "B2"):
        result["reading_rules"][reference] = reading_rules(
            {arm: {"flagged": pick("cut", OWN_CUT[arm], arm, reference), "unflagged": pick("cut", "unflagged", arm, reference)} for arm in ARMS}
        )
    result["reading_rules"]["relabel_alone"] = reading_rules(
        {TURN: {"flagged": pick("cut", "turn_days", TURN, CODED), "unflagged": pick("cut", "unflagged", TURN, CODED)}}
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_report(result, s761), encoding="utf-8")
    return 0


# -- Markdown --------------------------------------------------------------------------------------------------------

METRIC_TITLES = a1027.METRIC_TITLES
SPLIT_TITLES = {"pooled": "pooled (decision days)", "regime": "regime (target day)", "target_type": "target day type (turn labels)", "cut": "day groups (target day)"}


def render_report(r: dict, s761) -> str:
    n = r["notes"]
    lines = [
        "# The balance-sheet days on the turn days, nested into the calendar-aware candidate (#1031): development data, not a verdict", "",
        f"Published panel `{r['panel_sha256']}`, scratch panel `{r['scratch_panel_sha256']}`. Declaration `{r['declaration']}`. Seed {r['seed']}, {r['draws']} draws, "
        f"the studentized stationary bootstrap. {n['scored_decision_days']} decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); "
        "positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 "
        "standard error behind the block length is noisy on this many days. The relabel is not adopted here; the page reads with it (`bs_turn`) and without it (`bs_coded`).", "",
        "## Mean scores, pooled", "", "| model | " + " | ".join(METRIC_TITLES[m] for m in r["means"]) + " |", "|---|" + "---|" * len(r["means"])]
    for m in r["models"]:
        lines.append(f"| {m} | " + " | ".join(f"{r['means'][label][m]:.4f}" for label in r["means"]) + " |")
    lines += ["", "## Reading (declared rules)", ""]
    for reference, sentences in r["reading_rules"].items():
        title = {"relabel_alone": "the relabel alone (turn arm over coded arm)"}.get(reference, f"over {reference}")
        lines += [f"**{title}**", ""] + [f"- {s}" for s in sentences] + [""]
    lines += ["Adopting the relabel is a marked question for Eleonora; this page does not decide it.", ""]
    for metric in METRIC_TITLES:
        lines += [f"## {METRIC_TITLES[metric]}", ""]
        for split in SPLIT_TITLES:
            if split not in r["groups"]:
                continue
            lines += [f"### {SPLIT_TITLES[split]}", ""]
            names = [f"{c} vs {b}" for c, b in r["pairs"]]
            lines += ["| group | days | " + " | ".join(p.replace(" vs ", " over ") for p in names) + " |", "|---|---|" + "---|" * len(names)]

            def order(label):
                if label in ORDER_REGIME:
                    return ORDER_REGIME.index(label)
                return CUTS.index(label) if label in CUTS else 50

            for label in sorted(r["groups"][split], key=order):
                entry = r["groups"][split][label]
                cell = entry["metrics"].get(metric, {}).get("pairs", {})
                shown = CUT_TITLES.get(label, label) if split == "cut" else label
                lines.append(f"| {shown} | {entry['days']:,} | " + " | ".join(s761.skill_text(cell[p]) if p in cell else "n/a" for p in names) + " |")
            lines.append("")
    if r["skipped_groups"]:
        lines += [f"Groups of fewer than {MIN_GROUP_DAYS} days, listed and not tested: " + ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items())) + ".", ""]
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
