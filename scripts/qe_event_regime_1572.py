"""#1548's quarter-end arm by regime of the event (#1572; H5 step 3, development tier; her ruling of 11 November 2026, card f1560-split-1111, option (a)).

#1548's declaration (`metadata/qe_event_model_1548.json`, `reading_rules`, third item) promised the arm's gain by regime of the event; the page did not carry it.
This study re-reads #1548's walk: the same panel, the same refits, the same forecasts (`scripts/qe_event_model_1548.build`), nothing declared again and
nothing new fitted. It cuts the group's cells (the target days of type `quarter_end_turn` or `year_end`) into quarter-end turns and year-ends, and each of those
by the regime of the event (the declared regime of the calendar date of the quarter-end the event is named for: 2018-19, 2020, 2021-23, 2024, 2025-26), and
reports, for the arm against the candidate on the same cells, the 90% coverage, the miss rates above q95 and below q01 (and the other two the page carries),
grid CRPS and upper-tail twCRPS, each with its event-cluster 90% interval (2,000 resamples, seed 1548, the method of #1548) and the number of events and cells.
A cell of fewer than FEW events is flagged. The table's "all regimes" rows must equal #1548's group figures or the script refuses to write.

The kill of #1548 stays as declared. Nothing here is a verdict, a choice or an adoption. No score is of a locked day or of a day after 2026-09-03.

Commands, from a clone of the branch (the panel build is #1548's):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 scripts/qe_event_regime_1572.py score --panel PUB.csv --output docs/research/qe-event-regime-1572/result.json
    PYTHONPATH=src python3 scripts/qe_event_regime_1572.py page --score docs/research/qe-event-regime-1572/result.json \\
        --record docs/research/qe-event-model-1548/result.json --output docs/research/qe-event-model-1548-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(name)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # the worker pool of the walk pickles by module name
    spec.loader.exec_module(module)
    return module


m1548 = _load("qe_event_model_1548")
from repo_model import announced_iorb, policy_events  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402

c, m1321, m1288, m1273, m1402 = m1548.c, m1548.m1321, m1548.m1288, m1548.m1273, m1548.m1402
SPLITS = load_split_declaration(c.SPLITS)
REGIMES = ("2018-19", "2020", "2021-23", "2024", "2025-26")
SCOPES = ("group", "quarter_end_turn", "year_end")
#: A table cell of fewer events than this is flagged as resting on few events. A reading aid, not a rule: it moves no kill and no claim.
FEW = 5
TOLERANCE = 1e-9
SEED, EVENT_REPS = m1548.SEED, m1548.EVENT_REPS
MEASURES = m1548.MEASURES
DATED = "11 November 2026"


def regime_of_event(event: str, splits=SPLITS) -> str:
    """The declared regime of the calendar date of the quarter-end an event (`YYYY-MM`) is named for.

    Raises:
        ValueError: the date is in no declared regime.
    """

    year, month = (int(x) for x in event.split("-"))
    return splits.regime(date(year, month, 28))


def few_events(entry: Mapping[str, object]) -> bool:
    return entry["events"] < FEW


def regime_table(cells: Sequence[dict], splits=SPLITS, *, reps: int = EVENT_REPS) -> dict:
    """`table[scope][regime or "all"]`: `m1548.summarise` of the group's cells of a scope, in a regime (`None` when the regime holds none)."""

    inside = [x for x in cells if x["in_group"]]
    out: dict = {}
    for scope in SCOPES:
        chosen = inside if scope == "group" else [x for x in inside if x["type"] == scope]
        row = {"all": m1548.summarise(chosen, reps=reps)}
        for regime in REGIMES:
            row[regime] = m1548.summarise([x for x in chosen if regime_of_event(x["event"], splits) == regime], reps=reps)
        out[scope] = row
    return out


def reproduce(table: Mapping[str, Mapping[str, Optional[dict]]], group: Mapping[str, object]) -> None:
    """The "all regimes" rows against #1548's group figures (pooled and by type): every mean and interval equal.

    Raises:
        ValueError: a figure differs.
    """

    there = {"group": group["pooled"], "quarter_end_turn": group["by_type"]["quarter_end_turn"], "year_end": group["by_type"]["year_end"]}
    for scope, theirs in there.items():
        mine = table[scope]["all"]
        if (mine is None) != (theirs is None):
            raise ValueError(f"{scope}: one of the two is empty")
        if mine is None:
            continue
        if (mine["cells"], mine["events"]) != (theirs["cells"], theirs["events"]):
            raise ValueError(f"{scope}: cells and events differ from #1548's")
        for name in MEASURES:
            for key in ("candidate", "arm", "diff"):
                a, b = mine["measures"][name][key], theirs["measures"][name][key]
                if abs(a - b) > TOLERANCE:
                    raise ValueError(f"{scope} {name} {key}: {a!r} against #1548's {b!r}")
                for x, y in zip(mine["measures"][name][key + "_interval"], theirs["measures"][name][key + "_interval"]):
                    if abs(x - y) > TOLERANCE:
                        raise ValueError(f"{scope} {name} {key} interval: {x!r} against #1548's {y!r}")


# -- the walk, re-read -------------------------------------------------------------------------------------------------------


def score(args) -> int:
    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = m1548.committed_declaration()
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m1548.load_daily_panel(panel_path) if row.date <= m1548.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/qe_event_regime_1572")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    theirs = json.loads(Path(args.record).read_text(encoding="utf-8")) if args.first is None else None
    result: dict = {"issue": 1572, "source": "docs/research/qe-event-model-1548/result.json (the walk of #1548, re-read; no refit, no new forecast)",
                    "declaration": str(m1548.DECLARATION.relative_to(REPO)), "panel_sha256": sha, "label": "development, not a verdict", "seed": SEED,
                    "event_reps": args.event_reps, "k": m1548.K, "few_events_below": FEW, "regimes": list(REGIMES),
                    "subset_from": None if args.first is None else args.first.isoformat(), "windows": {}}
    for window in m1548.WINDOWS:
        frame, notes, labels, _record, counts, _groups = m1548.build(
            window, panel, splits, registry, table, register, results, auctions, args.first, m1548.K)
        cells = m1548.group_cells(frame, labels, table, frame.forecasts[m1548.ANNNET], frame.forecasts[m1548.ARM])
        tab = regime_table(cells, splits, reps=args.event_reps)
        if theirs is not None:
            reproduce(tab, theirs["windows"][window]["group"])
        result["windows"][window] = {"notes": notes, "outside_the_group": counts, "table": tab}
    result["reproduction"] = ("the all-regimes rows equal #1548's group figures (means and intervals) to 1e-9, both windows"
                              if theirs is not None else "not checked: a subset run")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page section ----------------------------------------------------------------------------------------------------------

_f, _iv, _signed, _siv = m1548._f, m1548._iv, m1548._signed, m1548._siv

SCOPE_TITLES = {"group": "group (turns and year-ends)", "quarter_end_turn": "quarter-end turns", "year_end": "year-ends"}


def _cell(m: Mapping[str, Mapping[str, object]], name: str) -> str:
    x = m[name]
    return f"{_f(x['candidate'])} / {_f(x['arm'])}; d {_signed(x['diff'])} {_siv(x['diff_interval'])}"


def _rows(table: Mapping[str, Mapping[str, Optional[dict]]], names: Sequence[str]) -> List[str]:
    head = ["| set | regime of the event | events | cells | flag | " + " | ".join(NAMES[n] for n in names) + " |", "|---|---|---|---|---|" + "---|" * len(names)]
    out = list(head)
    for scope in SCOPES:
        for regime in ("all",) + REGIMES:
            e = table[scope][regime]
            label = "all regimes" if regime == "all" else regime
            if e is None:
                out.append(f"| {SCOPE_TITLES[scope]} | {label} | 0 | 0 | none | " + " | ".join("n/a" for _ in names) + " |")
                continue
            flag = f"**few events ({e['events']})**" if few_events(e) else ""
            out.append(f"| {SCOPE_TITLES[scope]} | {label} | {e['events']} | {e['cells']} | {flag} | " + " | ".join(_cell(e["measures"], n) for n in names) + " |")
    return out


NAMES = {
    "cover90": "90% coverage: cand. / arm; d [interval]", "miss_above_q95": "above q95 (5%): cand. / arm; d [interval]",
    "miss_below_q01": "below q01 (1%): cand. / arm; d [interval]", "grid_crps": "grid CRPS: cand. / arm; d [interval] (negative favours the arm)",
    "upper_tail_twcrps": "upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm)",
}


def _few_list(table: Mapping[str, Mapping[str, Optional[dict]]]) -> str:
    items = [f"{SCOPE_TITLES[s]}, {'all' if r == 'all' else r} ({table[s][r]['events']})" for s in SCOPES for r in REGIMES if table[s][r] is not None and few_events(table[s][r])]
    return "; ".join(items) if items else "none"


def _excluding_zero(table: Mapping[str, Mapping[str, Optional[dict]]], name: str) -> str:
    items = []
    for s in SCOPES:
        for r in REGIMES:
            e = table[s][r]
            if e is None or e["events"] < 2:  # one event resamples to itself: the interval is a point, not evidence
                continue
            lo, hi = e["measures"][name]["diff_interval"]
            if lo > 0.0 or hi < 0.0:
                items.append(f"{SCOPE_TITLES[s]}, {r} ({_signed(e['measures'][name]['diff'])} {_siv([lo, hi])}, {e['events']} events)")
    return "; ".join(items) if items else "none"


def section(record: Mapping[str, object]) -> List[str]:
    """The dated section of #1548's page: the arm against the candidate by regime of the event, both windows."""

    out = [f"## Addendum of {DATED} (#1572): the arm's gain by regime of the event", "",
           "#1548's declaration promised, as its third reading rule, the arm's gain by regime of the event. This section is that table. It re-reads the walk above: "
           "the same panel, refits and forecasts, nothing fitted again, no new forecast and no figure above changed. **The kill stays as declared** (above): this "
           "section does not re-read it, move it or apply it to a cell. Nothing here is a verdict, a choice or an adoption, and (s3c-ann-net) stays frozen. "
           "Generated by `scripts/qe_event_regime_1572.py page` from `docs/research/qe-event-regime-1572/result.json`, not edited by hand; settled-questions "
           "register: #1548 is recorded as run and no entry splits it by event regime.", "",
           "**How to read it.** A cell is the group's cells (the target days of type `quarter_end_turn` or `year_end`, h = 1 to 5) of one set in one regime. The regime "
           "of an event is the declared regime (`metadata/evaluation_splits.json`) of the calendar date of the quarter-end the event is named for; a year-end's two "
           "days belong to the regime of the December that names it. Each cell gives the candidate's figure, the arm's, and d, the arm minus the candidate on the "
           "same cells, with its 90% event-cluster interval (whole events resampled, "
           f"{record['event_reps']:,} resamples, seed {record['seed']}, the method of #1548). The h = 1 to 5 forecasts aimed at one turn are one event, so the "
           f"events column is the number of independent turns behind a cell. A cell of fewer than {record['few_events_below']} events is flagged: its interval is "
           "narrower than its evidence, and a bootstrap over so few events can return a degenerate interval (a difference that is exactly zero in every event has "
           "an interval of [+0.000, +0.000], which is not a finding). The flag is a reading aid, not a rule. The all-regimes rows equal the figures of #1548 "
           "above (group CRPS, the 22 turns' coverage, the 8 year-ends' twCRPS), and the script refuses to write if they do not.", ""]
    for window, title in (("development", "The development window"), ("2026", "The 2026 development days (decide nothing)")):
        w = record["windows"][window]
        t = w["table"]
        out += [f"### {title}", "",
                f"Group cells {w['outside_the_group']['group_cells']:,}; the cells below are exactly these, cut by set and regime (the regime cells of each set add up to its "
                "all-regimes row).", "",
                "**Coverage and tail misses**", ""] + _rows(t, ("cover90", "miss_above_q95", "miss_below_q01")) + [
                "", "**Accuracy of the distribution**", ""] + _rows(t, ("grid_crps", "upper_tail_twcrps")) + [
                "", f"Cells resting on few events (under {record['few_events_below']}): {_few_list(t)}.", "",
                f"Regime cells whose grid CRPS interval of d excludes zero: {_excluding_zero(t, 'grid_crps')}. Whose coverage interval of d excludes zero: "
                f"{_excluding_zero(t, 'cover90')}. Whose upper-tail twCRPS interval of d excludes zero: {_excluding_zero(t, 'upper_tail_twcrps')}. "
                "A cell of a single event resamples to itself, so its interval is a point and it is left out of these lists. "
                "With this many cells, several intervals are expected to exclude zero by chance, and none was chosen in advance.", ""]
    out += ["### What this adds and does not add", "",
            "It adds where the group figures of #1548 come from: which regimes and which kind of turn carry the coverage gain and the CRPS and twCRPS differences, "
            "and how many events each rests on. It does not change the declared kill, which compares the group's point difference in grid CRPS and the coverage "
            "interval and stays as declared; it does not test one regime against another, correct for the number of cells read, or say that a regime's gain would "
            "recur. It is development data (scoring protocol v1), not a verdict. The ruling on the quarter-end family (#1561 waits on it) is hers.", ""]
    return out


def full_page(theirs: dict, record: dict) -> str:
    return m1548.render(theirs, section(record))


def page(args) -> int:
    theirs = json.loads(Path(args.record).read_text(encoding="utf-8"))
    record = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(full_page(theirs, record), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="re-read #1548's walk and cut the group by regime of the event")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--record", default=str(REPO / "docs" / "research" / "qe-event-model-1548" / "result.json"))
    s.add_argument("--event-reps", type=int, default=EVENT_REPS)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (a subset, for the script's test only)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write #1548's page with this section")
    g.add_argument("--score", required=True)
    g.add_argument("--record", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
