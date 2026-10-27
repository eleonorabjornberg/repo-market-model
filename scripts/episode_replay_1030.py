"""The per-episode stress replay of the published model and the benchmarks (#1030; H5 step 6, the validation report).

Lens D of #958: on every onset replayed (16-18 September 2019, 11-17 March 2020, the 2018, 2024 and 2025 year-end turns)
the published model's q95 sat below the print and the band widened after the first miss. This script lays that out, day
by day, as a table per episode: the print and the q05, q50 and q95 of the published model, B1, B2 and B1'.

A read of tracked records, not a refit. The published model's quantiles are read from the committed record
`docs/runs/published_distribution_daily_h1.json` (target day, h = 1). No record holds the daily quantiles of B1, B2 or
B1'; they are the protocol's own zero-parameter functions of the panel (`repo_model.protocol_benchmarks`,
`repo_model.b1_calendar`), evaluated at the decision day before each target day. The panel must be the record's (its
digest is checked). No day after 2025-12-31 is read (`docs/decisions/lockbox.md`). Development data, not a verdict.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/episode_replay_1030.py run --panel /tmp/funding_panel.csv
    PYTHONPATH=src python3 scripts/episode_replay_1030.py check

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import b1_calendar as b1c, protocol_benchmarks as pb  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.scoring_protocol import GRID  # noqa: E402

ISSUE = 1030
OUT = REPO / "docs" / "research" / "episode-replay-1030"
RESULT = OUT / "result.json"
PAGE = REPO / "docs" / "research" / "episode-replay-1030-result.md"
RECORD = REPO / "docs" / "runs" / "published_distribution_daily_h1.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
DECISION_TIME = time(16, 0)
#: `docs/decisions/lockbox.md`: a comparison scores only days before 2026-01-01.
LAST_DAY = date(2025, 12, 31)
LEVELS = (0.05, 0.5, 0.95)
KEYS = ("q05", "q50", "q95")
MODELS = ("published", "B1", "B2", "B1_prime")
#: Target-day windows. The September 2019 and March 2020 windows are the directive's. A year-end turn runs from 26
#: December to 3 January; the 2025 turn stops at the lockbox (2025-12-31).
EPISODES: Tuple[Tuple[str, date, date], ...] = (
    ("2018 year-end turn", date(2018, 12, 26), date(2019, 1, 3)),
    ("September 2019", date(2019, 9, 16), date(2019, 9, 18)),
    ("March 2020", date(2020, 3, 11), date(2020, 3, 17)),
    ("2024 year-end turn", date(2024, 12, 26), date(2025, 1, 3)),
    ("2025 year-end turn", date(2025, 12, 26), date(2026, 1, 3)),
)
#: How each model stands against `docs/research/provisional-calendar-register.md` (#1028).
STATUS = {
    "published": "provisional: calendar not read at the target day (class a+b at lead 1, the register's first row)",
    "B1": "provisional: reads no calendar day (a zero-parameter reference; nothing to re-run)",
    "B2": "not provisional: reads the target day's reporting type (a zero-parameter reference)",
    "B1_prime": "not provisional: reads the target day's reporting type (a zero-parameter reference)",
}
LABELS = {"published": "Published model", "B1": "B1", "B2": "B2", "B1_prime": "B1′"}


def registry() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def episode_days(dates: Sequence[date]) -> Dict[str, List[date]]:
    """The panel days inside each window, none after `LAST_DAY` (the lockbox)."""

    return {name: [d for d in sorted(dates) if first <= d <= last and d <= LAST_DAY] for name, first, last in EPISODES}


def levels_at(levels: Sequence[float], quantiles: Sequence[float], wanted: Sequence[float] = LEVELS) -> List[float]:
    """The quantiles at exactly the `wanted` levels; a level that is not there is a ValueError."""

    if len(levels) != len(quantiles):
        raise ValueError(f"{len(levels)} levels but {len(quantiles)} quantiles")
    index = {round(level, 6): i for i, level in enumerate(levels)}
    out = []
    for level in wanted:
        if round(level, 6) not in index:
            raise ValueError(f"level {level} is not among the forecast's levels {list(levels)}")
        out.append(quantiles[index[round(level, 6)]])
    return out


def published_days(record: dict) -> Dict[date, dict]:
    """The committed record's days by target day: the print and the q05, q50 and q95."""

    out = {}
    for day in record["days"]:
        quantiles = day["quantiles_bps"]
        if any(b < a for a, b in zip(quantiles, quantiles[1:])):
            raise ValueError(f"the record's quantiles for {day['date']} are not sorted")
        q05, q50, q95 = levels_at(record["levels"], quantiles)
        out[date.fromisoformat(day["date"])] = {"print_bp": day["actual_bps"], "q05": q05, "q50": q50, "q95": q95}
    return out


def band_summary(rows: Sequence[dict]) -> dict:
    """Misses of the q05-q95 band over rows with `print_bp`, `q05`, `q95`, and the band width after the first miss.

    A print on an edge is inside. `widened_after_first_miss` compares the widest band after the first miss with the
    band on the day of the first miss; None when there was no miss or no later day.
    """

    width = [r["q95"] - r["q05"] for r in rows]
    above = [i for i, r in enumerate(rows) if r["print_bp"] > r["q95"]]
    below = [i for i, r in enumerate(rows) if r["print_bp"] < r["q05"]]
    first = min(above + below) if above or below else None
    after = width[first + 1:] if first is not None else []
    return {
        "days": len(rows),
        "above_q95": len(above),
        "below_q05": len(below),
        "first_miss": rows[first]["date"] if first is not None else None,
        "width_first_day": width[0] if rows else None,
        "width_after_first_miss": after,
        "widened_after_first_miss": (max(after) > width[first]) if after else None,
    }


def _cut(forecast: Sequence[float]) -> dict:
    return dict(zip(KEYS, levels_at(GRID, forecast)))


def replay(panel: Sequence[DailyObservation], record: dict, panel_path) -> dict:
    """The replay: every target day of every episode, for the published model and B1, B2 and B1'."""

    digest = panel_sha256(Path(panel_path))
    if digest != record["panel_sha256"]:
        raise ValueError(f"the panel ({digest}) is not the record's ({record['panel_sha256']})")
    published = published_days(record)
    splits = load_split_declaration(SPLITS)
    reg = registry()
    settings = dict(registry=reg, decision_time=DECISION_TIME)
    position = {row.date: i for i, row in enumerate(panel)}
    episodes = []
    for name, days in episode_days([row.date for row in panel]).items():
        rows = []
        for day in days:
            if day not in published:
                raise ValueError(f"{day} is not in the published record")
            index = position[day]
            if abs(panel[index].spread_bps - published[day]["print_bp"]) > 1e-9:
                raise ValueError(f"the record's print for {day} is not the panel's spread")
            decision = index - 1
            rows.append({
                "date": day.isoformat(),
                "print_bp": panel[index].spread_bps,
                "published": {k: published[day][k] for k in KEYS},
                "B1": _cut(pb.b1_forecast(panel, decision, **settings)[1]),
                "B2": _cut(pb.b2_forecast(panel, decision, splits=splits, **settings)[1]),
                "B1_prime": _cut(b1c.b1_calendar_forecast(panel, decision, splits=splits, **settings)[1]),
            })
        summary = {m: band_summary([{"date": r["date"], "print_bp": r["print_bp"], **r[m]} for r in rows]) for m in MODELS}
        first, last = next((f, l) for n, f, l in EPISODES if n == name)
        episodes.append({"name": name, "window": [first.isoformat(), min(last, LAST_DAY).isoformat()], "rows": rows,
                         "summary": summary})
    return {
        "issue": ISSUE,
        "label": "development data, not a verdict; no refit",
        "hypothesis": "H5, step 6 (the validation report)",
        "lead": 1,
        "last_day": LAST_DAY.isoformat(),
        "panel_sha256": digest,
        "published_record": RECORD.relative_to(REPO).as_posix(),
        "benchmarks": "zero-parameter functions of the panel (protocol_benchmarks.b1_forecast, b2_forecast; "
                      "b1_calendar.b1_calendar_forecast) at the decision day before each target day",
        "levels": list(LEVELS),
        "status": STATUS,
        "episodes": episodes,
    }


def _bp(x: float) -> str:
    return f"{x:+.1f}"


def _cell(r: dict, m: str) -> str:
    q = r[m]
    text = f"{_bp(q['q05'])} / {_bp(q['q50'])} / {_bp(q['q95'])}"
    return f"**{text}**" if r["print_bp"] > q["q95"] or r["print_bp"] < q["q05"] else text


def render(result: dict) -> str:
    L = [
        "# Per-episode stress replay (#1030)", "",
        "**Hypothesis and step:** H5 (primary goal), step 6 (the validation report). **Development data, not a verdict** "
        "(scoring protocol v1, #640). Nothing is refitted: the published model's quantiles are read from "
        f"`{result['published_record']}`; B1, B2 and B1′ are the protocol's zero-parameter functions of the panel "
        "(no record holds their daily quantiles). Lead h = 1, target days; the forecast for a target day is made at 16:00 "
        f"the business day before. No day after {result['last_day']} is read (`docs/decisions/lockbox.md`).", "",
        "Each cell is q05 / q50 / q95 in bp of SOFR − IORB. A **bold** cell is a miss: the print is outside the q05–q95 "
        "band. The 2025 year-end turn stops at 2025-12-31, the last unlocked day.", "",
        "## Calendar status of each row (#1028)", "",
    ]
    for m in MODELS:
        L.append(f"- **{LABELS[m]}:** {result['status'][m]}.")
    L.append("")
    for ep in result["episodes"]:
        L += [f"## {ep['name']} ({ep['window'][0]} to {ep['window'][1]})", "",
              "| Target day | Print, bp | " + " | ".join(LABELS[m] for m in MODELS) + " |",
              "|---|---|" + "---|" * len(MODELS)]
        for r in ep["rows"]:
            L.append(f"| {r['date']} | {_bp(r['print_bp'])} | " + " | ".join(_cell(r, m) for m in MODELS) + " |")
        L += ["", "| Model | Days | Print above q95 | Print below q05 | First miss | Band q95−q05 on that day and after |",
              "|---|---|---|---|---|---|"]
        for m in MODELS:
            s = ep["summary"][m]
            first = s["first_miss"]
            rows = ep["rows"]
            if first is None:
                tail = "no miss"
            else:
                i = next(k for k, r in enumerate(rows) if r["date"] == first)
                tail = ", ".join(f"{r[m]['q95'] - r[m]['q05']:.1f}" for r in rows[i:])
            L.append(f"| {LABELS[m]} | {s['days']} | {s['above_q95']} | {s['below_q05']} | {first or '-'} | {tail} |")
        L.append("")
    L += ["## Lens D's reading, against the tables (published model)", "",
          "| Episode | Days | Print above q95 | Band wider on a later day than on the first-miss day |", "|---|---|---|---|"]
    for ep in result["episodes"]:
        s = ep["summary"]["published"]
        wide = {True: "yes", False: "no", None: "no later day or no miss"}[s["widened_after_first_miss"]]
        L.append(f"| {ep['name']} | {s['days']} | {s['above_q95']} | {wide} |")
    L += ["", "The reading is that on every onset the q95 sat below the print and the band widened after the first miss. "
          "Where a row above shows otherwise, the reading does not hold for that episode.", ""]
    L += ["## What this shows, and does not", "",
          "- It replays the days the directive names, from records already on main. It scores nothing, ranks nothing and "
          "decides nothing: three or four days per episode, and episodes chosen because they were stress days.",
          "- The published row and B1 read no calendar day at the target day; B2 and B1\u2032 read the target day's "
          "reporting type. A miss by a row marked provisional is not evidence about a calendar-aware model.",
          "- The episode windows are the directive's dates for September 2019 and March 2020; the year-end windows "
          "(26 December to 3 January) are this study's choice, pinned in `tests/test_episode_replay_1030.py`.", ""]
    return "\n".join(L)


def run_command(args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    panel = load_daily_panel(Path(args.panel))
    result = replay(panel, record, args.panel)
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(result), encoding="utf-8")
    print("wrote", RESULT, PAGE)
    return 0


def check_command(_args) -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if PAGE.read_text(encoding="utf-8") != render(result):
        print("the page is not what result.json gives; run `run`", file=sys.stderr)
        return 1
    print("ok")
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", required=True)
    run.set_defaults(func=run_command)
    commands.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
