"""The amendment 4 coverage report for (s3c-ann-net) at spacing h + 1 (#1527, H5, step M5: registration).

A development study, never a verdict. Her rulings of 8 November 2026 (#1525, "spacing") and 10 November 2026 (#1545, "both") move amendment 4's
Kupiec and independence tests from every h-th decision day to every (h + 1)-th (`scoring_protocol.coverage_cells(method="spaced")`, the method
the requirement reads, `COVERAGE_REQUIREMENT_METHOD`). This study reads the frozen candidate's development walk (the walk of
`candidate_calibration_1363.py`, unchanged, through `coverage_report_1512.py`) and reports the list of rejections at the new spacing next to the
design as set (`thinned`) and the reported-only HAC variant at the corrected lag (`spaced_hac`). The report's own reading of a cell is the one
`enforce_coverage_requirement` applies (the flag is patched on inside the call only, by `coverage_report_1512.report`).

No arms, no tuned setting, no declaration. Nothing after 2025-12-31 and no locked day is read (`coverage_report_1512.load_window_doc` refuses
another window and any later day, and `coverage_cells` refuses a locked day again). The study neither reads nor writes
`COVERAGE_REQUIREMENT_IN_FORCE`.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/coverage_spacing_1527.py walk --panel PUB.csv --output WALK/development.json
    OUT=docs/research/coverage-spacing-1527
    PYTHONPATH=src python3 scripts/coverage_spacing_1527.py score --walk WALK/development.json --output $OUT/result.json
    PYTHONPATH=src python3 scripts/coverage_spacing_1527.py page --score $OUT/result.json --output docs/research/coverage-spacing-1527-result.md

The walk takes about two minutes and `score` seconds, below the `long-run` line.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m12 = _load("coverage_report_1512", "coverage_report_1512_in_1527")
ISSUE = 1527
CANDIDATE = m12.CANDIDATE
#: the design of the requirement first, then the design as set (#1522) and the reported-only HAC variant at the corrected lag
METHODS: Dict[str, str] = {
    "spaced": "Kupiec and independence on every (h + 1)-th decision day (the requirement, #1527)",
    "thinned": "Kupiec and independence on every h-th decision day (as set by #1522)",
    "spaced_hac": "Kupiec on every day with a Newey-West variance at lag h, independence on every (h + 1)-th day (reported only)",
}
RULE = "strict"


def report_all(window) -> Dict[str, dict]:
    """`coverage_report_1512.report` once per method; the module's `METHOD` is set for the call and restored."""

    out: Dict[str, dict] = {}
    original = m12.METHOD
    try:
        for method in METHODS:
            m12.METHOD = method
            rep = m12.report(window)
            out[method] = {k: v for k, v in rep.items() if not k.startswith("_")}
    finally:
        m12.METHOD = original
    return out


def walk_command(args) -> int:
    return m12.walk_command(args)


def score_command(args) -> int:
    doc = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    window = m12.load_window_doc(doc)
    record = json.loads(m12.RECORD_1314.read_text(encoding="utf-8"))
    reproduction = m12.m63.reproduction_check(window, record)
    by_method = report_all(window)
    qs = window.q[CANDIDATE]
    result = {
        "issue": ISSUE, "label": "development, not a verdict", "candidate": CANDIDATE, "panel_sha256": doc.get("panel_sha256"),
        "window": window.name, "decision_days": len(window.days), "last_target": window.last_day().isoformat(),
        "family": m12.FAMILY, "alpha": m12.ALPHA, "rules": list(m12.RULES), "regimes": by_method["spaced"]["regimes"],
        "regime_days": by_method["spaced"]["regime_days"], "requirement_method": sp.COVERAGE_REQUIREMENT_METHOD,
        "methods": by_method,
        "ties": {f"{lv:g}": sum(1 for q, y in zip(qs, window.y) if q[sp.GRID.index(lv)] == y) for lv in m12.LEVELS},
        "reproduction": {"against": str(m12.RECORD_1314.relative_to(REPO)), "models": {CANDIDATE: reproduction[CANDIDATE]}},
        "coverage_requirement_in_force": sp.COVERAGE_REQUIREMENT_IN_FORCE,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _p(x: Optional[float]) -> str:
    return "n/a" if x is None else ("<0.001" if x < 0.001 else f"{x:.3f}")


def render(r: Mapping[str, object]) -> str:
    methods: Mapping[str, dict] = r["methods"]
    L: List[str] = []
    a = L.append
    a("# Amendment 4 coverage report for (s3c-ann-net) at spacing h + 1 (#1527)")
    a("")
    a("**Hypothesis and step:** H5, step M5 (registration). **Development data, not a verdict.** Generated by `scripts/coverage_spacing_1527.py page` "
      "from `docs/research/coverage-spacing-1527/result.json`, not edited by hand. No model is changed and nothing is registered.")
    a("")
    a("**What was measured.** The frozen candidate (s3c-ann-net) on its development walk-forward forecasts: "
      f"{r['decision_days']} decision days, targets to {r['last_target']}, the walk of `scripts/candidate_calibration_1363.py` unchanged. Kupiec and "
      "Christoffersen at q05/q95 and q01/q99 by lead h = 1 to 5 and regime, with Holm over every test of a hit rule at "
      f"{r['alpha']:.0%} (`enforce_coverage_requirement(..., family=\"{r['family']}\", alpha={r['alpha']}, rule=...)`; the script checks that its "
      "reading and the function's agree, with the flag patched on inside the call only). Three designs of `coverage_cells`:")
    a("")
    for m, text in METHODS.items():
        a(f"- `{m}`: {text}.")
    a("")
    a("The 2026 days and every locked day are not read. The design that the draft amendment would put in force is `spaced`.")
    a("")
    a("## Does the candidate pass, and which tests are rejected?")
    a("")
    a("| Design | Hit rule | passes | tests in the family | rejected by Holm |")
    a("|---|---|---|---|---|")
    for m in METHODS:
        for rule in r["rules"]:
            v = methods[m]["verdict"][rule]
            a(f"| `{m}` | {m12.RULE_NAMES[rule]} | **{m12._mark(v['passes'])}** | {v['tests']} | {v['rejected']} |")
    a("")
    for m in METHODS:
        v = methods[m]["verdict"][RULE]
        a(f"### Rejections under `{m}`, `{RULE}` rule ({v['rejected']})")
        a("")
        if v["failing_tests"]:
            for t in v["failing_tests"]:
                a(f"- `{t}`")
        else:
            a("None.")
        a("")
    same = all(methods["spaced"]["verdict"][x]["failing_tests"] == methods["spaced"]["verdict"][r["rules"][0]]["failing_tests"] for x in r["rules"])
    a("The three hit rules give the same rejections: " + ("yes" if same else "no") + f" (ties at the four read levels: "
      + ", ".join(f"q{k} {v}" for k, v in r["ties"].items()) + ").")
    a("")
    a("## Pass or fail per lead and regime, design `spaced`, `strict` rule")
    a("")
    a("| Lead | " + " | ".join(r["regimes"]) + " |")
    a("|---|" + "---|" * len(r["regimes"]))
    for h in methods["spaced"]["leads"]:
        a(f"| {h} | " + " | ".join(m12._mark(methods['spaced']['pass_fail'][RULE][str(h)][g]) for g in r["regimes"]) + " |")
    a("")
    a("## The cells, design `spaced`, `strict` rule")
    a("")
    a("Hit rate with its Wilson 95% interval, Kupiec p and independence p (raw, before Holm). `n` is the sample on every (h + 1)-th decision day.")
    a("")
    a("| Lead | Regime | Level | n | hits | rate [95%] | nominal | Kupiec p | independence p | rejected |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for c in methods["spaced"]["cells"]:
        if c["rule"] != RULE:
            continue
        iv = c["interval"]
        rate = "n/a" if c["rate"] is None else f"{c['rate']:.1%} [{iv[0]:.1%}, {iv[1]:.1%}]"
        a(f"| {c['lead']} | {c['regime']} | q{c['level']:g} | {c['n']} | {c['hits']} | {rate} | {c['nominal']:.0%} | {_p(c['kupiec_p'])} | "
          f"{_p(c['independence_p'])} | {', '.join(c['failed_tests']) or '-'} |")
    a("")
    a("## What this shows and does not show")
    a("")
    a("- It shows how the frozen candidate reads against amendment 4 at spacing h + 1, on seen development days. It is no verdict, and "
      "the candidate's registration (#1510) stays her attested action.")
    a("- The size of this design is #1528's (1.1% [0.6%, 2.0%] on a world fitted to the development spreads), not this candidate's. Small "
      "regimes hold few spaced days, most of all at leads 4 and 5; see `n`.")
    a("- A fault confined to quarter-end days is not detected at any spacing (#1528); quarter-end coverage is reported, not gated (§7). The cells "
      "are lead by regime only: no split by pressure-day type is made here.")
    a("- `spaced_hac` is reported only; it decides nothing. The 2026 days (the near-blind tier) are not read. B1, B1', B2 and B4 are not put through the check.")
    a("")
    a(f"Panel sha256 `{r['panel_sha256']}`. Its mean grid CRPS reproduces the 1314 record: {json.dumps(r['reproduction']['models'][CANDIDATE], sort_keys=True)}.")
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
