"""A two-of-three alarm for the pressure-day judge (#458, a track of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. The candidate `vote_2_of_3` is declared in `metadata/pressure_judge/candidates/vote_2_of_3.json`, which
this script refuses to read unless it is committed and unchanged (`pressure_judge.py`'s own check). It flags a day
when at least two of its three voters flag it, each at the cut-off the judge chooses for that voter refit by refit
from the voter's training window (`pressure_judge.choose_cutoffs`). It uses the voters' existing walk-forward
forecasts and refits nothing.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/bench_hH.json
    ... the voters' own forecast scripts, h = 1 to 5 (see `docs/pivot/vote-2-of-3-result.md`) ...
    PYTHONPATH=src python3 scripts/vote_2_of_3.py judge --panel PUB.csv --output OUT/vote.json \\
        --markdown OUT/vote.md --overlap OUT/overlap.json OUT/bench_h?.json OUT/tp_h?.json OUT/q_h?.json OUT/hl_h?.json

The voters are not in the judge's declaration on main (each track declared them in its own file); they are added to
the declaration in memory, with the entries of `docs/pivot/evidence/judge-amendment/pressure_judge_rejudge.json`, for
this run only. No published declaration moves. The vote's probability is the share of the voters whose flag is up and
its cut-off is 2/3, so its flag is the vote; the tiers that need a calibrated probability (tier 3's calibration, tier 5)
read that share and say so in the result.

`judge` also writes how the voters' flags overlap at +5 bp, h = 1 to 5: the false alarms (flags on days that are not
pressure days) and the hits (the onsets each voter flags at lead of at least 1, as tier 1 counts them).
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402

VOTE = "vote_2_of_3"
REJUDGE = REPO / "docs" / "pivot" / "evidence" / "judge-amendment" / "pressure_judge_rejudge.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
NEEDED = 2


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def voters_of(declaration_dir: Path = pj.DEFAULT_DECLARATION) -> list:
    """The vote's voters, as its committed candidate file names them."""

    entry = json.loads((pj.candidates_directory(declaration_dir) / f"{VOTE}.json").read_text(encoding="utf-8"))
    voters = list(entry["voters"])
    if len(voters) != 3 or len(set(voters)) != 3:
        raise ValueError(f"{VOTE} needs three distinct voters, not {voters}")
    return voters


def composed_declaration(voters) -> pj.Declaration:
    """The judge's declaration (with `vote_2_of_3`) plus the voters' entries, for this run only."""

    known = json.loads(REJUDGE.read_text(encoding="utf-8"))["candidates"]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copy(pj.DEFAULT_DECLARATION, root / "pressure_judge.json")
        shutil.copytree(pj.candidates_directory(pj.DEFAULT_DECLARATION), root / "pressure_judge" / "candidates")
        for name in voters:
            (root / "pressure_judge" / "candidates" / f"{name}.json").write_text(
                json.dumps(known[name]), encoding="utf-8"
            )
        return pj.load_declaration(root / "pressure_judge.json")


def vote_forecast(declaration: pj.Declaration, voters, horizon: int, chosen) -> pj.Forecast:
    """The vote at one horizon from the voters' forecasts with their cut-offs chosen.

    Raises:
        ValueError: if the voters are not on the same days.
    """

    parts = [chosen[(name, horizon)] for name in voters]
    dates = parts[0].dates
    if any(tuple(p.dates) != tuple(dates) for p in parts):
        raise ValueError(f"the voters are not on the same days at h = {horizon}")
    probabilities, cutoffs = {}, {}
    for tau in declaration.thresholds:
        votes = [
            sum(1 for p in parts if p.probabilities[tau][k] >= p.cutoffs[tau][k]) for k in range(len(dates))
        ]
        probabilities[tau] = tuple(v / len(voters) for v in votes)
        cutoffs[tau] = tuple(NEEDED / len(voters) - 1e-9 for _ in dates)
    return pj.Forecast(
        name=VOTE, horizon=horizon, dates=dates, probabilities=probabilities,
        cutoffs=cutoffs, cutoff_rule=declaration.sha256,
    )


def _flags(forecast: pj.Forecast, tau: float):
    return [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]


def overlap(declaration, grids, chosen, voters, vote_by_horizon) -> dict:
    """How the voters' flags overlap at the primary threshold, h = 1 to 5: false alarms and onsets flagged."""

    tau = declaration.primary
    horizons = list(declaration.horizons)
    false_alarms = {name: set() for name in [*voters, VOTE]}
    flag_days = {name: set() for name in [*voters, VOTE]}
    caught = {name: set() for name in [*voters, VOTE]}
    onsets = set()
    for h in horizons:
        grid = grids[h]
        for name in [*voters, VOTE]:
            forecast = vote_by_horizon[h] if name == VOTE else chosen[(name, h)]
            for k, flag in enumerate(_flags(forecast, tau)):
                if not flag:
                    continue
                flag_days[name].add((h, grid.dates[k]))
                if not grid.outcomes[tau][k]:
                    false_alarms[name].add((h, grid.dates[k]))
    # Onsets as tier 1 counts them at lead >= 1: the days every horizon scores, flagged at some horizon.
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    first = horizons[0]
    for day in common:
        if grids[first].onset[position[first][day]]:
            onsets.add(day)
    for h in horizons:
        for name in [*voters, VOTE]:
            forecast = vote_by_horizon[h] if name == VOTE else chosen[(name, h)]
            flags = _flags(forecast, tau)
            for day in onsets:
                if flags[position[h][day]]:
                    caught[name].add(day)

    def pairs(sets):
        out = {}
        for a, b in itertools.combinations(voters, 2):
            both, either = sets[a] & sets[b], sets[a] | sets[b]
            out[f"{a} & {b}"] = {
                "both": len(both), "either": len(either), "jaccard": len(both) / len(either) if either else None,
            }
        every = set.intersection(*(sets[n] for n in voters))
        anyone = set.union(*(sets[n] for n in voters))
        exactly = {k: sum(1 for x in anyone if sum(x in sets[n] for n in voters) == k) for k in (1, 2, 3)}
        out["all three"] = len(every)
        out["at least one"] = len(anyone)
        out["flagged by exactly k voters"] = {str(k): v for k, v in exactly.items()}
        return out

    return {
        "onsets": len(onsets),
        "per_voter": {
            name: {
                "flag_days": len(flag_days[name]),
                "false_alarms": len(false_alarms[name]),
                "onsets_flagged": len(caught[name]),
            }
            for name in [*voters, VOTE]
        },
        "false_alarm_overlap": pairs(false_alarms),
        "hit_overlap": pairs(caught),
    }


def overlap_markdown(doc, voters) -> str:
    lines = [
        "Table O1. Flags at +5 bp, h = 1 to 5 together. A false alarm is a flag on a day that is not a pressure day (a "
        "day and horizon counted once); a hit is an onset flagged at some horizon h >= 1.",
        "",
        "| row | flag-days | false alarms | onsets flagged (of %d) |" % doc["onsets"],
        "|---|---|---|---|",
    ]
    for name, row in doc["per_voter"].items():
        lines.append(f"| {name} | {row['flag_days']} | {row['false_alarms']} | {row['onsets_flagged']} |")
    for title, key in (("false alarms", "false_alarm_overlap"), ("hits (onsets flagged)", "hit_overlap")):
        part = doc[key]
        lines += ["", f"Table O2 ({title}): overlap of the three voters.", "", "| pair | in both | in either | share in both |", "|---|---|---|---|"]
        for pair, cell in part.items():
            if isinstance(cell, dict) and "both" in cell:
                share = "–" if cell["jaccard"] is None else f"{cell['jaccard']:.2f}"
                lines.append(f"| {pair} | {cell['both']} | {cell['either']} | {share} |")
        exactly = part["flagged by exactly k voters"]
        lines += [
            "",
            f"Flagged by all three: {part['all three']}; by at least one: {part['at least one']}; by exactly one / two / "
            f"three voters: {exactly['1']} / {exactly['2']} / {exactly['3']}.",
        ]
    return "\n".join(lines) + "\n"


def judge_command(args) -> int:
    script = _judge_script()
    script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    voters = voters_of()
    declaration = composed_declaration(voters)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = script.load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    wanted = {declaration.climatology, declaration.persistence, *voters}

    forecasts, scratch = [], {}
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            scratch[str(path)] = document["panel_sha256"]
        forecasts.extend(f for f in pj.forecasts_from_horizon_document(document) if f.name in wanted)
    # A forecast file scored on a scratch panel (the hierarchical logistic's `pressure_v1_1.py panel`) is accepted
    # only when its days are the published panel's benchmark days; its digest is recorded.
    for path in scratch:
        document = json.loads(Path(path).read_text())
        for f in pj.forecasts_from_horizon_document(document):
            if f.name not in wanted:
                continue
            reference = next(
                (g for g in forecasts if g.horizon == f.horizon and g.name == declaration.climatology), None)
            if reference is None or tuple(reference.dates) != tuple(f.dates):
                raise SystemExit(f"{path} was scored on another panel ({scratch[path][:8]}) and its days are not the grid's")
    states = {h: script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(forecasts):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in forecasts if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    grids = grids_of(forecasts)
    forecasts = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
    chosen = {(f.name, f.horizon): f for f in forecasts}
    votes = {h: vote_forecast(declaration, voters, h, chosen) for h in declaration.horizons}
    forecasts = [*forecasts, *votes.values()]
    result = pj.judge(
        declaration, grids, forecasts, calendar=calendar, holdouts=script._holdouts()
    )
    result["provenance"] = {
        "panel_sha256": digest,
        "declaration_commit": script.require_committed_declaration(pj.DEFAULT_DECLARATION),
        "forecast_files": [str(p) for p in args.inputs],
        "voters": voters,
        "scratch_panel_files": scratch,
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(script.markdown(result), encoding="utf-8")
    shares = overlap(declaration, grids, chosen, voters, votes)
    if args.overlap:
        args.overlap.write_text(json.dumps(shares, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        args.overlap.with_suffix(".md").write_text(overlap_markdown(shares, voters), encoding="utf-8")
    print(json.dumps({"output": str(args.output),
                      "verdicts": {n: c["verdict"]["passes"] for n, c in result["candidates"].items()}}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True)
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument("--overlap", type=Path)
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(run=judge_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
