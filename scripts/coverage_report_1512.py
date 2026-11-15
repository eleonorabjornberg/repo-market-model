"""The amendment 4 coverage report for the frozen candidate (s3c-ann-net) (#1512, H5, step M5: registration).

A development study, never a verdict. Amendment 4 of `docs/decisions/scoring-protocol.md` (#1130, in force since 23 October 2026) makes a
coverage report a requirement of registration: Kupiec (unconditional coverage) and Christoffersen (independence) at q05/q95 and q01/q99, for
each lead h = 1 to 5 and each regime, from `scoring_protocol.coverage_cells`, at the design the amendment's answers set (thinned days at
leads above 1, Holm over the family at 5%, regimes the protocol's development split), under both deterministic hit rules (`strict`,
`tie_counts`) and the randomised tie rule. The report reads the candidate on its development walk-forward forecasts only: the window of
`scripts/candidate_calibration_1363.py` ("development": decision days whose five targets fall on or before 2025-12-31). Nothing after that
day and no locked day is read (`load_window_doc` refuses both; `coverage_cells` refuses a locked day again).

The pass or fail of a cell is read as `enforce_coverage_requirement` reads it: Holm over every test of one hit rule (Kupiec and independence,
all four levels, all leads and regimes), and a cell fails when one of its tests is rejected. The candidate passes under a rule when no cell
of that rule fails. `scoring_protocol.COVERAGE_REQUIREMENT_IN_FORCE` is not touched: it is patched on inside `report` only, for the
duration of the call, to read the verdict the way the requirement would, and it is False in the tree.

Choices this script makes and the page states (none changes a threshold or a rule of the protocol):
- the walk is `candidate_calibration_1363.py walk`, unchanged (the code of `scripts/s3c_announced_settlement_1288.py`, refit every 21 decision
  days, direct pairs, the SRF cap, the 18:00 decision instant); its mean grid CRPS is checked against the 1314 record by `score`;
- the regime of a cell is the regime of its decision day, `frame.regime(d)`, as the walk file carries it (`regime_of_day`);
- the randomised rule needs the probability that a tie at a quantile is a hit, from the forecast's own distribution. The forecast is 23
  quantiles of a whole-basis-point target, so the tie probability is read as `randomised_pit_970` reads a tie: the forecast's mass at q is
  the level bracket between the largest level whose quantile is below q and the smallest whose quantile is above it, and
  `coverage_tests.tie_hit_probability` gives the share of that mass a hit in the tail needs. (`regime_spells_1182` reads the same 23
  quantiles as a continuous law, whose tie probability is 0 and whose randomised rule is `strict`; both readings are named on the page.)
- the draws are `random.Random(SEED)` in (decision day, lead, grid level) order, recorded by their seed.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/coverage_report_1512.py walk --panel PUB.csv --output WALK/development.json
    OUT=docs/research/coverage-report-1512
    PYTHONPATH=src python3 scripts/coverage_report_1512.py score --walk WALK/development.json --output $OUT/result.json
    PYTHONPATH=src python3 scripts/coverage_report_1512.py page --score $OUT/result.json --output docs/research/coverage-report-1512-result.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests as ct, scoring_protocol as sp  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m63 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1512")

ISSUE = 1512
SEED = 1512
CANDIDATE = m63.CANDIDATE
WINDOW = "development"
LAST_DAY: date = m63.WINDOW_LAST[WINDOW]
# the design of the amendment's answers 1, 2 and 5
METHOD = "thinned"
FAMILY = "holm"
ALPHA = 0.05
RULES: Tuple[str, ...] = tuple(sp.COVERAGE_RULES) + (sp.RANDOMISED_RULE,)
LEVELS = tuple(sp.COVERAGE_LEVELS)
LEADS = tuple(sp.HORIZONS)
RECORD_1314 = m63.RECORD_1314
RULE_NAMES = {"strict": "strict (y beyond q)", "tie_counts": "tie_counts (y at or beyond q)", "randomised": "randomised tie rule"}


# -- the walk file -------------------------------------------------------------------------------------------------------------


def load_window_doc(doc: Mapping[str, object]) -> "m63.Window":
    """A walk file as `candidate_calibration_1363.Window`, refused unless it is the development window and ends on or before its last day.

    Raises:
        ValueError: the file is another window.
        LookAheadError: a decision or target day is after 2025-12-31 or in a locked tier.
    """

    if doc.get("window") != WINDOW:
        raise ValueError(f"this report reads the {WINDOW!r} window only, got {doc.get('window')!r}")
    window = m63.Window(doc)
    m63.refuse_beyond(list(window.days) + [t for _d, _h, t in window.cells], LAST_DAY, where="coverage_report_1512.load_window")
    if CANDIDATE not in window.q:
        raise ValueError(f"the walk file carries no forecasts of {CANDIDATE}")
    return window


def tie_probabilities(law: Sequence[float]) -> List[float]:
    """Per grid level, the probability that an outcome equal to the law's quantile counts as a hit in that level's own tail.

    The forecast's mass at q is the bracket (`below`, `at`): `below` the largest level whose quantile is under q (0 if none), `at` the smallest
    level whose quantile is over it (1 if none), as `randomised_pit_970.pit_bracket` reads a tie. `coverage_tests.tie_hit_probability` then gives
    the share of that mass a hit needs, in the upper tail for a level above one half and in the lower tail otherwise.
    """

    out: List[float] = []
    for level, q in zip(sp.GRID, law):
        below = max((l for l, v in zip(sp.GRID, law) if v < q), default=0.0)
        at = min((l for l, v in zip(sp.GRID, law) if v > q), default=1.0)
        if level in LEVELS:
            upper = level > 0.5
            out.append(ct.tie_hit_probability(below, at, (1.0 - level) if upper else level, upper=upper))
        else:
            out.append(0.0)
    return out


def make_draws(window: "m63.Window", seed: int = SEED) -> Dict[date, Dict[int, List[float]]]:
    """One uniform draw in [0, 1) per (decision day, lead, grid level), in that order, from `random.Random(seed)`."""

    rng = random.Random(seed)
    return {d: {h: [rng.random() for _ in sp.GRID] for h in LEADS} for d in window.days}


def inputs(window: "m63.Window") -> dict:
    """The arguments of `scoring_protocol.coverage_cells` for the candidate: forecasts, outcomes, calendar, regimes, tie probabilities, draws.

    Raises:
        ValueError: a cell's target is not the h-th scoring-calendar day after its decision day (the walk and the protocol would disagree).
    """

    position = window.position
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    ties: Dict[date, Dict[int, List[float]]] = {}
    for (d, h, t), q in zip(window.cells, window.q[CANDIDATE]):
        if position[d] + h >= len(window.calendar) or window.calendar[position[d] + h] != t:
            raise ValueError(f"cell ({d}, {h}) targets {t}, not the {h}-th scoring-calendar day after {d}")
        forecasts.setdefault(d, {})[h] = list(q)
        ties.setdefault(d, {})[h] = tie_probabilities(q)
    return {
        "forecasts": forecasts, "outcomes": dict(window.outcome), "calendar": list(window.calendar),
        "regimes": dict(window.regime_of_day), "ties": ties, "draws": make_draws(window),
    }


# -- the report ----------------------------------------------------------------------------------------------------------------


def wilson(hits: int, n: int, z: float = 1.959964) -> Optional[List[float]]:
    """The Wilson score 95% interval of a hit rate (None for an empty cell)."""

    if n <= 0:
        return None
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, centre - half), min(1.0, centre + half)]


def test_names(cell: "sp.CoverageCell") -> List[Tuple[str, float]]:
    """The tests of one cell as `enforce_coverage_requirement` names them."""

    out = [(cell.label() + " / kupiec", cell.kupiec_p)]
    if cell.independence_p is not None:
        out.append((cell.label() + " / independence", cell.independence_p))
    return out


def report(window: "m63.Window") -> dict:
    """The coverage report of one walk: every cell, the pass or fail per lead, regime and rule, and the candidate's verdict per rule."""

    inp = inputs(window)
    cells = sp.coverage_cells(
        inp["forecasts"], inp["outcomes"], inp["calendar"], inp["regimes"], method=METHOD,
        tie_probabilities=inp["ties"], draws=inp["draws"],
    )
    regimes = sorted({c.regime for c in cells})
    rows: List[dict] = []
    pass_fail: Dict[str, Dict[str, Dict[str, bool]]] = {}
    verdict: Dict[str, dict] = {}
    for rule in RULES:
        mine = [c for c in cells if c.rule == rule]
        tests = {name: p for c in mine for name, p in test_names(c)}
        rejected = sp.holm(tests, ALPHA)
        failing = sorted(name for name, r in rejected.items() if r)
        # the verdict the requirement itself would read, with the flag patched on for this call only
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            try:
                sp.enforce_coverage_requirement(cells, alpha=ALPHA, family=FAMILY, rule=rule)
                enforced = True
            except sp.CoverageRequirementFailed:
                enforced = False
        if enforced != (not failing):
            raise ValueError(f"rule {rule}: the report and enforce_coverage_requirement disagree")
        verdict[rule] = {"passes": enforced, "tests": len(tests), "rejected": len(failing), "failing_tests": failing}
        pass_fail[rule] = {str(h): {} for h in LEADS}
        for c in mine:
            names = [name for name, _p in test_names(c)]
            failed = [name for name in names if rejected[name]]
            ok = pass_fail[rule][str(c.lead)].get(c.regime, True) and not failed
            pass_fail[rule][str(c.lead)][c.regime] = ok
            rows.append({
                "rule": rule, "lead": c.lead, "regime": c.regime, "level": c.level, "n": c.n, "hits": c.hits,
                "rate": (c.hits / c.n) if c.n else None, "nominal": min(c.level, 1.0 - c.level),
                "interval": wilson(c.hits, c.n), "kupiec_p": c.kupiec_p, "independence_p": c.independence_p,
                "failed_tests": [n.rsplit(" / ", 1)[1] for n in failed],
            })
    return {
        "method": METHOD, "family": FAMILY, "alpha": ALPHA, "rules": list(RULES), "levels": list(LEVELS), "leads": list(LEADS),
        "regimes": regimes, "window": window.name, "decision_days": len(window.days), "cells_n": len(window.cells),
        "last_target": window.last_day().isoformat(), "seed": SEED, "cells": rows, "pass_fail": pass_fail, "verdict": verdict,
        "regime_days": {r: sum(1 for d in window.days if window.regime_of_day[d] == r) for r in regimes},
        "_cells": cells,
    }


# -- commands ------------------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    """The development walk of `candidate_calibration_1363.py walk`, unchanged, for the development window only."""

    ns = argparse.Namespace(panel=args.panel, window=WINDOW, output=args.output, first=None)
    return m63.walk_command(ns)


def score_command(args) -> int:
    doc = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    window = load_window_doc(doc)
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    reproduction = m63.reproduction_check(window, record)
    rep = report(window)
    qs = window.q[CANDIDATE]
    rep["ties"] = {"cells": len(window.cells), "by_level": {f"{lv:g}": sum(1 for q, y in zip(qs, window.y) if q[sp.GRID.index(lv)] == y) for lv in LEVELS}}
    rep = {k: v for k, v in rep.items() if not k.startswith("_")}
    rep.update({
        "issue": ISSUE, "label": "development, not a verdict", "candidate": CANDIDATE, "panel_sha256": doc.get("panel_sha256"),
        "reproduction": {"against": str(RECORD_1314.relative_to(REPO)), "models": {CANDIDATE: reproduction[CANDIDATE]}},
        "coverage_requirement_in_force": sp.COVERAGE_REQUIREMENT_IN_FORCE,
        "randomised_reading": "tie probability from the level bracket of the forecast's quantiles (randomised_pit_970), draws random.Random(1512)",
    })
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _p(x: Optional[float]) -> str:
    return "n/a" if x is None else ("<0.001" if x < 0.001 else f"{x:.3f}")


def _mark(ok: bool) -> str:
    return "pass" if ok else "FAIL"


def render(r: Mapping[str, object]) -> str:
    verdict, rules, regimes = r["verdict"], r["rules"], r["regimes"]
    L: List[str] = []
    a = L.append
    a("# Amendment 4 coverage report for (s3c-ann-net) (#1512)")
    a("")
    a("**Hypothesis and step:** H5, step M5 (registration). **Development data, not a verdict.** Generated by `scripts/coverage_report_1512.py page` "
      "from `docs/research/coverage-report-1512/result.json`, not edited by hand. This is the report that amendment 4 of "
      "`docs/decisions/scoring-protocol.md` (#1130, in force since 23 October 2026) makes a registration requirement, and that her ruling on "
      "PR #1511 (Q8) says the registration of #1510 waits for.")
    a("")
    a("**What was measured.** The frozen candidate (s3c-ann-net) on its development walk-forward forecasts: "
      f"{r['decision_days']} decision days, targets to {r['last_target']}, the 18:00 decision instant, the walk of `scripts/candidate_calibration_1363.py` unchanged "
      "(its mean grid CRPS reproduces the 1314 record to 1e-9). Kupiec and Christoffersen at q05/q95 and q01/q99 by lead h = 1 to 5 and by regime "
      f"({', '.join(regimes)}), from `scoring_protocol.coverage_cells` with `method=\"{r['method']}\"` (every h-th decision day at lead h), under both "
      "deterministic hit rules and the randomised tie rule. A cell fails when one of its tests is rejected by Holm over all tests of the rule at "
      f"{r['alpha']:.0%}, which is how `enforce_coverage_requirement(cells, alpha={r['alpha']}, family=\"{r['family']}\", rule=...)` reads it "
      "(the script checks that its own reading and `enforce_coverage_requirement` agree, with the flag patched on inside the call only). "
      "No 2026 day and no locked day is read.")
    a("")
    a("## Does the candidate pass?")
    a("")
    a("| Hit rule | passes | tests in the family | rejected by Holm |")
    a("|---|---|---|---|")
    for rule in rules:
        v = verdict[rule]
        a(f"| {RULE_NAMES[rule]} | **{_mark(v['passes'])}** | {v['tests']} | {v['rejected']} |")
    a("")
    for rule in rules:
        v = verdict[rule]
        if v["failing_tests"]:
            shown = v["failing_tests"][:12]
            a(f"Rejected under `{rule}` ({len(shown)} of {v['rejected']} shown): " + "; ".join(f"`{t}`" for t in shown) + ".")
            a("")
    a("## Pass or fail per lead and regime, by hit rule")
    a("")
    a("A cell passes when none of its tests (Kupiec and independence at the four levels) is rejected.")
    a("")
    a("| Lead | Regime | " + " | ".join(RULE_NAMES[x] for x in rules) + " |")
    a("|---|---|" + "---|" * len(rules))
    for h in r["leads"]:
        for g in regimes:
            a(f"| {h} | {g} | " + " | ".join(_mark(r["pass_fail"][rule][str(h)][g]) for rule in rules) + " |")
    a("")
    a("## The cells")
    a("")
    a("Hit rate with its Wilson 95% interval, Kupiec p and independence p (raw, before Holm), by level, lead, regime and rule. "
      "`n` is the thinned sample: a decision day every h-th day.")
    a("")
    key = lambda c: (c["lead"], c["regime"], c["level"])
    by_rule = {rule: {key(c): (c["hits"], c["kupiec_p"], c["independence_p"]) for c in r["cells"] if c["rule"] == rule} for rule in rules}
    same = all(by_rule[rule] == by_rule[rules[0]] for rule in rules)
    if same:
        a(f"The three rules give the same hits and p-values in every cell: no outcome of the {r['ties']['cells']} cells equals the forecast's quantile at any of "
          f"the four read levels (ties counted: {', '.join(f'q{k} {v}' for k, v in r['ties']['by_level'].items())}), so the rules never differ. "
          "One table is printed, for all three.")
        a("")
    for rule in (rules[:1] if same else rules):
        a(f"### {'all three rules' if same else RULE_NAMES[rule]}")
        a("")
        a("| Lead | Regime | Level | n | hits | rate [95%] | nominal | Kupiec p | independence p | rejected |")
        a("|---|---|---|---|---|---|---|---|---|---|")
        for c in r["cells"]:
            if c["rule"] != rule:
                continue
            iv = c["interval"]
            rate = "n/a" if c["rate"] is None else f"{c['rate']:.1%} [{iv[0]:.1%}, {iv[1]:.1%}]"
            a(f"| {c['lead']} | {c['regime']} | q{c['level']:g} | {c['n']} | {c['hits']} | {rate} | {c['nominal']:.0%} | {_p(c['kupiec_p'])} | "
              f"{_p(c['independence_p'])} | {', '.join(c['failed_tests']) or '-'} |")
        a("")
    a("## What this shows and does not show")
    a("")
    a("- It shows how the frozen candidate reads against the requirement of amendment 4 on its development walk-forward forecasts, "
      "by the design the amendment's answers set. It is development evidence on seen days and no verdict.")
    a("- The requirement is **not in force in the tree**: `scoring_protocol.COVERAGE_REQUIREMENT_IN_FORCE` is False and this report does not "
      "change it. See the marked question in the pull request.")
    a("- The amendment leaves the rule the requirement reads to the size simulation (answer 4); #1156 found the randomised tie rule the only "
      "one whose size is within the family-wise level for a calibrated forecaster with whole-bp ties. The table reads all three; which one a "
      "registration is held to is hers.")
    a("- The randomised rule's tie probability comes from the level bracket of the 23 quantiles (as `randomised_pit_970` reads a tie), "
      "which is a reading of a 23-quantile forecast of a whole-bp target and not the forecast's own full distribution. Read as a continuous "
      "law between the quantiles (as `regime_spells_1182` does), a tie is never a hit and the randomised rule is the `strict` rule.")
    a("- Size is only known for a synthetic world (#1156), not for this candidate: Holm over this family at "
      f"{r['alpha']:.0%} may reject more or less often than nominal here. Small regimes have few thinned days, most of all at leads 4 and 5; "
      "see `n` in the cells.")
    a("- HAC (`method=\"hac\"`) is not run. The 2026 days (the near-blind tier) are not read. B1, B1', B2 and B4 are not put through the check.")
    a("")
    a(f"Seed {r['seed']} for the randomised draws. Panel sha256 `{r['panel_sha256']}`.")
    a("")
    return "\n".join(L)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk")
    w.add_argument("--panel", required=True)
    w.add_argument("--output", required=True)
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score")
    s.add_argument("--walk", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
