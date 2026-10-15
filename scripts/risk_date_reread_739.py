"""H6 step 1 re-read on the studentized bootstrap (#739; H6 step 1, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
It changes nothing in #693's declaration or published evidence. It rebuilds #693's scores with #693's own code (the same
panel, day set, candidates, benchmarks and seed 693) and reads the kill rule of `metadata/risk_date_spread_693.json` on
the interval of protocol ruling 1 (`scoring_protocol`: the studentized stationary bootstrap) in place of the percentile
interval of the draws (Eleonora, ruling on #739, 14 October 2026: development kill rules are read on the studentized
bootstrap; the calibrated critical value belongs to checkpoints; ruling 6 stands, so B1 is unchanged). Scored days are
#693's: decision days whose five targets are on or before 2025-12-31 (`docs/decisions/lockbox.md`). Nothing here is a
verdict (scoring protocol v1, #640).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/risk_date_reread_739.py score --panel /tmp/funding_panel.csv \\
        --output docs/research/evidence/risk-date-reread-739.json --markdown docs/research/risk-date-reread-739.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s693 = _load("risk_date_spread_693")
BENCHMARKS = s693.BENCHMARKS
CANDIDATES = s693.CANDIDATES
LEVEL = sp.ALPHA


def studentized_skill_interval(test: sp.PairedTest) -> Tuple[float, float]:
    """The 90% interval of skill read on the studentized draws: `skill - q * se` at the 95th and 5th percentile of `t`."""

    t, se = test.skill_t_draws, test.skill_standard_error
    return (
        test.skill - sp._bound(t, 1.0 - LEVEL, test.draws) * se,
        test.skill - sp._bound(t, LEVEL, test.draws) * se,
    )


def studentized_row(test: sp.PairedTest) -> dict:
    """The row #693 records (`paired_row`), with the studentized interval beside the percentile one."""

    row = s693.s686.paired_row(test)
    low, high = studentized_skill_interval(test)
    row["percentile_skill_interval"] = row["skill_interval"]
    row["skill_interval"] = [low, high]
    return row


def has_skill(row: dict) -> bool:
    """The studentized 90% interval of the pooled skill lies above zero."""

    return "undefined" not in row and row["skill_interval"][0] > 0.0


def kill_rule(primary: Mapping[str, dict]) -> dict:
    """#693's declared kill rule (`risk_date_spread_693.kill_rule`), read with the studentized `has_skill`."""

    out = {"skill": {}, "against_both": [], "against_at_least_one": []}
    for c in CANDIDATES:
        flags = {
            metric: {b: has_skill(primary[metric]["vs"][c][b]) for b in BENCHMARKS} for metric in ("grid_crps", "mae")
        }
        out["skill"][c] = flags
        if any(all(f.values()) for f in flags.values()):
            out["against_both"].append(c)
        if any(any(f.values()) for f in flags.values()):
            out["against_at_least_one"].append(c)
    out["killed"] = not out["against_both"]
    out["killed_on_the_weaker_reading"] = not out["against_at_least_one"]
    return out


def vs_all(series: Mapping[str, Mapping[date, float]], days: Sequence[date], draws: int) -> Dict[str, dict]:
    """Each candidate against each benchmark on `days`, on #693's resample stream (seed 693), studentized."""

    out: Dict[str, dict] = {}
    for c in CANDIDATES:
        pairs = [({d: series[b][d] for d in days}, {d: series[c][d] for d in days}) for b in BENCHMARKS]
        tests = sp.paired_tests(pairs, seed=s693.SEED, draws=draws)
        out[c] = {b: studentized_row(t) for b, t in zip(BENCHMARKS, tests)}
    return out


def score(args) -> int:
    s693.committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s693.SPLITS)
    registry = json.loads(s693.SOURCES.read_text(encoding="utf-8"))
    states = s693.scarcity_states()
    frame, notes, _ = s693.build_frame(panel, splits, registry, states)
    draws = args.draws

    metrics = ("grid_crps", "mae")
    cells = {m: {metric: s693.cell_scores(frame, m, metric) for metric in metrics} for m in s693.MODELS}
    target = {metric: {m: s693.by_target(frame, cells[m][metric]) for m in s693.MODELS} for metric in metrics}
    target_days = sorted(target["grid_crps"]["B1"])
    s693.require_scored_days(target_days)
    result: dict = {
        "issue": 739, "reads": "scripts/risk_date_spread_693.py", "panel_sha256": panel_sha256(panel_path),
        "label": "development, not a verdict", "seed": s693.SEED, "draws": draws, "notes": notes,
        "interval": "the studentized stationary bootstrap of protocol ruling 1: skill - q * se at the 95th and 5th percentile of t",
        "days": len(target_days),
    }
    primary = {}
    for metric in metrics:
        series = target[metric]
        primary[metric] = {"means": {m: s693.mean(series[m].values()) for m in s693.MODELS}, "vs": vs_all(series, target_days, draws)}
    result["primary"] = primary
    result["kill_rule"] = kill_rule(primary)

    regime_of = {t: splits.regime(t) for t in target_days}
    three = {t: s693.THREE_REGIMES[regime_of[t]] for t in target_days}
    result["regime_three"] = {}
    for label, members in s693.s686.group_days(target_days, three).items():
        if len(members) < s693.MIN_GROUP_DAYS:
            result["regime_three"][label] = {"days": len(members), "note": "fewer than 20 days; not tested"}
            continue
        result["regime_three"][label] = {
            "days": len(members), "grid_crps": {"vs": vs_all(target["grid_crps"], members, draws)}}

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render(result), encoding="utf-8")
    return 0


def pct(value: float) -> str:
    return f"{100.0 * value:+.2f}%"


def skill_text(row: dict) -> str:
    if "undefined" in row:
        return "undefined"
    low, high = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(low)}, {pct(high)}]"


def render(r: dict) -> str:
    a = s693.A
    rule = r["kill_rule"]
    crps, mae = r["primary"]["grid_crps"]["vs"][a], r["primary"]["mae"]["vs"][a]
    lines = [
        "# H6 step 1 re-read on the studentized bootstrap (#739)", "",
        "**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), step 1. **Development data only: not a verdict** "
        "(scoring protocol v1, #640). Generated by `scripts/risk_date_reread_739.py`; it reads #693's scores "
        "(`docs/pivot/risk-date-spread-result.md`, left as published) on the interval of protocol ruling 1, the studentized stationary bootstrap, "
        "as Eleonora ruled on #739. The percentile interval is the one #693 published.", "",
        f"Target: the SOFR - IORB spread in bp on {r['days']:,} risk target days to 2025-12-31, the same days, candidates, benchmarks and seed 693 as #693. "
        "B1 is unchanged (ruling 6).", "",
        "| pooled, first candidate (the H5 mean-reverting row) | skill [90%], studentized | skill lower bound, percentile (as #693 published) |",
        "|---|---|---|",
    ]
    for metric, vs in (("grid CRPS", r["primary"]["grid_crps"]["vs"][a]), ("MAE of the median", r["primary"]["mae"]["vs"][a])):
        for b in BENCHMARKS:
            lines.append(f"| {metric} against {b} | {skill_text(vs[b])} | {pct(vs[b]['percentile_skill_interval'][0])} |")
    lines += [
        "", "| regime (CRPS against B1) | days | skill [90%], studentized |", "|---|---|---|",
    ]
    for label, cell in r["regime_three"].items():
        if "grid_crps" in cell:
            lines.append(f"| {label} | {cell['days']} | {skill_text(cell['grid_crps']['vs'][a]['B1'])} |")
    verdict = ("**No development skill.** On the declared rule, skill against both benchmarks on CRPS or MAE, no candidate has it: "
               "the studentized lower bound of CRPS skill against B1 is "
               f"{pct(crps['B1']['skill_interval'][0])} and MAE against B1 has none either."
               if rule["killed"] else
               "**The declared rule still passes.** At least one candidate has skill against both benchmarks on the studentized interval.")
    lines += ["", verdict, "",
              "H6 stays open: its kill is by futility on prospective days, not by this re-read (ruling on #739). The reading of the "
              "development kill rule changes; #693's published page is not edited.", ""]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="re-read #693's kill rule on the studentized interval")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--markdown")
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.set_defaults(func=score)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
