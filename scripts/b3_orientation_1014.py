#!/usr/bin/env python3
"""The B3 five-level critical value, calibrated in the orientation `report` reads (H1, #1014, finding #1001).

`scoring_protocol.report` reads B3 as the benchmark: its `against_b3` test has d = S(B3) - S(candidate). The drafts of #873
and #886 calibrated the B3 value on S(B1) - S(B3) (`protocol_coverage.calibration_series`), the reverse, and the daily
difference is skewed, so its quantile depends on the sign (#830). This script calibrates on S(B3) - S(B1), on the decision
days from 2020-04-03, with the windows, block and seed of the record in force (20,000 windows at 125 and 250 days, circular
blocks of 10, seed 1), and reports, for the value in force and the drafts of #873 and #886, the share of null paths each
detects in that orientation (#699's rule, 2,000 paths). Development data only; it changes no constant and edits no decision
record: adopting any value is Eleonora's section 13 decision.

    PYTHONPATH=src python3 scripts/b3_orientation_1014.py calibrate --write
    python3 scripts/b3_orientation_1014.py report
    python3 scripts/b3_orientation_1014.py check

`calibrate` writes `docs/research/b3-orientation-1014/result.json`; `report` writes `docs/research/b3-orientation-1014-result.md`
from it alone, so no figure on the page is typed; `check` refuses a page that is not what `report` would write. Standard
library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "b3-orientation-1014" / "result.json"
PAGE = RESEARCH / "b3-orientation-1014-result.md"
CALIBRATION_873 = RESEARCH / "protocol-calibration-873" / "result.json"
CALIBRATION_886 = RESEARCH / "protocol-calibration-886" / "result.json"

#: Decision days from this day are "post-2020-04" (as #886 and the confirmation-design study read them).
FIRST_DAY = date(2020, 4, 3)
ORIENTATION = "d = S(B3) - S(B1), B3 the benchmark, as `scoring_protocol.report` reads its against-B3 test"
WINDOWS = 20_000
SEED = 1
PATHS = 2_000
LOOKS = (125, 250)


def _protocol_coverage():
    spec = importlib.util.spec_from_file_location("protocol_coverage_for_1014", REPO / "scripts" / "protocol_coverage.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["protocol_coverage_for_1014"] = module
    spec.loader.exec_module(module)
    return module


def report_orientation_series(days: Sequence[date], s1: Sequence[float], s3: Sequence[float],
                              first: date = FIRST_DAY) -> Tuple[List[date], List[float]]:
    """The days from `first` and `S(B3) - S(B1)` on them, in order: the series the against-B3 test applies.

    Raises:
        ValueError: `days`, `s1` and `s3` differ in length.
    """

    if not len(days) == len(s1) == len(s3):
        raise ValueError(f"{len(days)} days, {len(s1)} B1 scores and {len(s3)} B3 scores")
    kept = [(d, b - a) for d, a, b in zip(days, s1, s3) if d >= first]
    return [d for d, _ in kept], [v for _, v in kept]


def calibrate_value(series: Sequence[float], *, days: int, level: float, windows: int = WINDOWS, seed: int = SEED) -> float:
    """The protocol's calibration of the one-sided bound's critical value, with the record in force's block."""

    return sp.calibrate_critical_value(series, days=days, level=level, windows=windows, seed=seed)


def null_share(s1: Sequence[float], s3: Sequence[float], critical: Dict[int, float], paths: int = PATHS) -> Dict[str, float]:
    """The share of null paths detected by each look at `critical`, in the orientation `report` reads.

    #699's paths (`protocol_coverage.detections`) with B3 in the benchmark's place: no true difference, the first 250 days of
    a stationary-bootstrap resample of the series, ungated.
    """

    return _protocol_coverage().detections(list(s3), list(s1), delta=0.0, noise=1.0, critical=critical, paths=paths)["ungated"]


def _values() -> List[Dict[str, object]]:
    d873 = json.loads(CALIBRATION_873.read_text(encoding="utf-8"))["comparison_critical_values"][sp.FIVE_LEVEL_COMPARISON]
    d886 = json.loads(CALIBRATION_886.read_text(encoding="utf-8"))["comparison_critical_values"][sp.FIVE_LEVEL_COMPARISON]
    force = sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON]
    return [
        {"name": "in force", "source": "`scoring_protocol.CRITICAL_VALUES`", "critical": {str(n): force[n] for n in LOOKS}},
        {"name": "#873 draft", "source": "`protocol-calibration-873/result.json` (S(B1) - S(B3), full history)",
         "critical": {str(n): d873[str(n)] for n in LOOKS}},
        {"name": "#886 draft", "source": "`protocol-calibration-886/result.json` (S(B1) - S(B3), post-2020 stationary windows)",
         "critical": {str(n): d886[str(n)] for n in LOOKS}},
    ]


def calibration(windows: int = WINDOWS, seed: int = SEED, paths: int = PATHS) -> Dict[str, object]:
    pc = _protocol_coverage()
    s1, s3 = pc.five_level_scores()
    days, series = report_orientation_series(pc._SCORES["five_days"], s1, s3)
    kept = [(a, b) for d, a, b in zip(pc._SCORES["five_days"], s1, s3) if d >= FIRST_DAY]
    post1, post3 = [a for a, _ in kept], [b for _, b in kept]
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    calibrated = {str(n): calibrate_value(series, days=n, level=levels[n], windows=windows, seed=seed) for n in LOOKS}
    values = _values()
    values.append({"name": "calibrated here", "source": "`scripts/b3_orientation_1014.py` (S(B3) - S(B1), post-2020-04)",
                   "critical": calibrated})
    for entry in values:
        entry["null_share"] = null_share(post1, post3, {n: entry["critical"][str(n)] for n in LOOKS}, paths=paths)
    return {
        "directive": "https://github.com/eleonorabjornberg/repo-market-model/issues/1014",
        "orientation": ORIENTATION,
        "first_day": days[0].isoformat(), "last_day": days[-1].isoformat(), "series_days": len(series),
        "windows": windows, "seed": seed, "block": sp.WINDOW_BLOCK, "paths": paths,
        "nominal_levels": {str(n): levels[n] for n in LOOKS},
        "calibrated": calibrated, "values": values,
    }


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def render(record: Dict[str, object]) -> str:
    levels = record["nominal_levels"]
    L = [
        "# The B3 five-level critical value in the orientation `report` reads (H1, #1014)", "",
        "**Development data only; no verdict, no lockbox day scored.** Every figure is read from "
        "`docs/research/b3-orientation-1014/result.json` by `scripts/b3_orientation_1014.py report`. "
        "`scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read, and PR #953 is untouched.", "",
        "## What was calibrated", "",
        f"`report` reads B3 as the benchmark: {record['orientation']}. The drafts of #873 and #886 calibrated the B3 value on "
        "S(B1) - S(B3), the reverse; the daily difference is skewed, so the two quantiles differ (#830). This page calibrates on "
        f"S(B3) - S(B1) over {record['series_days']} decision days ({record['first_day']} to {record['last_day']}), "
        f"{record['windows']:,} windows at each look, circular blocks of {record['block']} days, seed {record['seed']}, as the "
        "record in force.", "",
        "## The value and each value's null share", "",
        f"The null share is the share of {record['paths']:,} null paths (no true difference, the first 250 days of a "
        "stationary-bootstrap resample of the same S(B3) - S(B1) series, #699's rule, ungated) detected by that look. A value "
        f"calibrated for this series has a null share near its nominal level: {_pct(levels['125'])} at 125 days and "
        f"{_pct(levels['250'])} by 250 days (the overall size is 5%).", "",
        "| value | source | critical 125 | critical 250 | null share by 125 | null share by 250 |", "|---|---|---|---|---|---|",
    ]
    for v in record["values"]:
        L.append(f"| {v['name']} | {v['source']} | {v['critical']['125']:.3f} | {v['critical']['250']:.3f} | "
                 f"{_pct(v['null_share']['125'])} | {_pct(v['null_share']['250'])} |")
    L += ["", "## For Eleonora (nothing settled in code)", "",
          "Adopting any of these values is a section 13 decision and is hers; this page changes no constant. For the draft in "
          "#953, a marked line it could carry: *\"B3 five-level critical values: calibrate on S(B3) - S(B1), the orientation "
          "`report` reads; value pending Eleonora's decision.\"*", ""]
    return "\n".join(L)


def calibrate_command(args) -> int:
    record = calibration(windows=args.windows, seed=args.seed, paths=args.paths)
    if args.write:
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, sort_keys=True))
    return 0


def report_command(_args) -> int:
    PAGE.write_text(render(json.loads(RECORD.read_text(encoding="utf-8"))), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    if not RECORD.exists() or not PAGE.exists():
        print("no record or page yet: `calibrate --write` and `report` have not been run", file=sys.stderr)
        return 1
    if PAGE.read_text(encoding="utf-8") != render(json.loads(RECORD.read_text(encoding="utf-8"))):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    cal = commands.add_parser("calibrate")
    cal.add_argument("--windows", type=int, default=WINDOWS)
    cal.add_argument("--seed", type=int, default=SEED)
    cal.add_argument("--paths", type=int, default=PATHS)
    cal.add_argument("--write", action="store_true")
    cal.set_defaults(func=calibrate_command)
    commands.add_parser("report").set_defaults(func=report_command)
    commands.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
