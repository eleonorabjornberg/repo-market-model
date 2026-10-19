#!/usr/bin/env python3
"""The corrected test's size on post-2020 resampled history (H1 step 5, #886).

#873 recalibrated the critical and futility values in the orientation the test applies, on circular blocks of the full
development history. Every confirmation day falls after 2020, so this script calibrates the same values on
stationary-bootstrap windows of the post-2020 days (decision days from 2020-04-03), in the same orientation
d = S(B1) - S(candidate), at the same looks, windows and seed. Development and simulated data only; nothing here is a
verdict, and `scoring_protocol`'s constants and the decision record are not touched.

    PYTHONPATH=src python3 scripts/postcovid_886.py calibrate --write
    PYTHONPATH=src python3 scripts/postcovid_886.py power --out docs/research/power-study-886
    PYTHONPATH=src python3 scripts/postcovid_886.py replay --out docs/research/power-replay-886
    PYTHONPATH=src python3 scripts/postcovid_886.py design --out docs/research/confirmation-design-886 [--workers K]
    PYTHONPATH=src python3 scripts/postcovid_886.py report
    PYTHONPATH=src python3 scripts/postcovid_886.py check

`calibrate` writes `docs/research/protocol-calibration-886/result.json`; `power` is `power_study_769.py run --values
draft-886`; `replay` is `power_replay_inforce_873.py` over three value sets; `design` re-runs #733's six designs at values
calibrated on the corrected test; `report` writes `docs/research/postcovid-886-result.md` from those records alone, so no
figure on the page is typed; `check` refuses a page that is not what `report` would write. Standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import math
import multiprocessing
import random
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

RESEARCH = REPO / "docs" / "research"
CALIBRATION = RESEARCH / "protocol-calibration" / "result.json"
CALIBRATION_873 = RESEARCH / "protocol-calibration-873" / "result.json"
CALIBRATION_886 = RESEARCH / "protocol-calibration-886" / "result.json"
POWER_873 = RESEARCH / "power-study-873"
POWER_886 = RESEARCH / "power-study-886"
REPLAY_886 = RESEARCH / "power-replay-886"
DESIGN_733 = RESEARCH / "confirmation-design-733"
DESIGN_886 = RESEARCH / "confirmation-design-886"
PAGE = RESEARCH / "postcovid-886-result.md"

#: Decision days from this day are "post-2020" (the confirmation-design study's `POST_2020_FIRST`).
POST_2020_FIRST = date(2020, 4, 3)
ORIENTATION = "d = S(benchmark) - S(candidate), benchmark B1"
GENERATOR = "stationary bootstrap, mean block length scoring_protocol.BLOCK_LENGTH, on the post-2020 days"
#: Windows per look, as the record in force. Look 1 (60 days) has no efficacy value (Q-B), so it is not calibrated.
CALIBRATION_WINDOWS = {125: 20_000, 250: 20_000}
FUTILITY_WINDOWS = 20_000
SEED = 1


def load_script(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -- the history and the generator -------------------------------------------------------------------------------


def post_2020(days, values):
    """The days from `POST_2020_FIRST` and their values, in order.

    Raises:
        ValueError: `days` and `values` differ in length.
    """

    if len(days) != len(values):
        raise ValueError(f"{len(days)} days but {len(values)} values")
    kept = [(d, v) for d, v in zip(days, values) if d >= POST_2020_FIRST]
    return [d for d, _ in kept], [v for _, v in kept]


def stationary_window_indices(size, days, rng, block):
    """A window of `days` positions drawn as the power study draws a path: a stationary bootstrap resample."""

    return list(stationary_bootstrap_indices(size, block, rng)[:days])


@contextlib.contextmanager
def stationary_windows():
    """Within the block, `scoring_protocol`'s calibration draws its windows by the stationary bootstrap."""

    original = sp._window_indices
    sp._window_indices = stationary_window_indices
    try:
        yield
    finally:
        sp._window_indices = original


def calibration_series(grid_days, grid, five_days, five):
    """The two comparisons' calibration series on the post-2020 days, each B1's day scores less the candidate's."""

    out = {}
    for name, days, (bench, candidate) in ((sp.GRID_COMPARISON, grid_days, grid), (sp.FIVE_LEVEL_COMPARISON, five_days, five)):
        out[name] = post_2020(days, [b - c for b, c in zip(bench, candidate)])[1]
    return out


def futility_inputs(days, pair):
    """B1's day scores and `S(B1) - S(candidate)` on the same post-2020 days."""

    bench, candidate = pair
    return post_2020(days, list(bench))[1], post_2020(days, [b - c for b, c in zip(bench, candidate)])[1]


# -- the calibration ---------------------------------------------------------------------------------------------


def calibration(seed=SEED, windows=None, futility_windows=FUTILITY_WINDOWS):
    windows = dict(CALIBRATION_WINDOWS if windows is None else windows)
    pc = load_script("protocol_coverage_for_886", "protocol_coverage.py")
    grid, five = pc.grid_scores(), pc.five_level_scores()
    grid_days, five_days = pc._SCORES["grid_days"], pc._SCORES["five_days"]
    pairs = calibration_series(grid_days, grid, five_days, five)
    levels = dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))
    values = {}
    with stationary_windows():
        for name, series in pairs.items():
            values[name] = {"60": None, **{
                str(n): sp.calibrate_critical_value(series, days=n, level=levels[n], windows=windows[n], seed=seed)
                for n in windows
            }}
        bench, differences = futility_inputs(grid_days, grid)
        futility = {sp.GRID_COMPARISON: {
            str(n): sp.calibrate_futility_value(bench, differences, days=n, level=sp.FUTILITY_LEVEL,
                                                windows=futility_windows, seed=seed)
            for n in sp.CHECKPOINTS
        }}
    return {
        "orientation": ORIENTATION, "generator": GENERATOR,
        "directive": "https://github.com/eleonorabjornberg/repo-market-model/issues/886",
        "history_first_decision_day": POST_2020_FIRST.isoformat(),
        "series_days": {name: len(series) for name, series in pairs.items()},
        "nominal_levels": {str(n): levels[n] for n in sp.CHECKPOINTS},
        "windows": {str(n): w for n, w in windows.items()}, "futility_windows": futility_windows,
        "window_block": sp.BLOCK_LENGTH, "seed": seed,
        "comparison_critical_values": values,
        "futility_level": sp.FUTILITY_LEVEL, "futility_critical_values": futility,
        "compared_with": {"protocol_calibration_873_sha256": sha256(CALIBRATION_873)},
        "note": (
            "same looks, windows, level and seed as the records of #695 and #873; only the history (post-2020 decision "
            "days) and the window generator (stationary bootstrap, as the power study's readings (c) and (d)) change. "
            "Look 1 has no efficacy value (Q-B). Nothing here is in force."
        ),
    }


def calibrate_command(args) -> int:
    result = calibration()
    if args.write:
        CALIBRATION_886.parent.mkdir(parents=True, exist_ok=True)
        CALIBRATION_886.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


# -- the power study, the replay -----------------------------------------------------------------------------------


def power_command(args) -> int:
    study = load_script("power_study_769_for_886", "power_study_769.py")
    return study.main(["run", "--out", args.out, "--values", "draft-886", "--paths", str(args.paths)])


def replay_value_sets():
    """The protocol's values at looks 2 and 3 on the replay's 250-day windows: those in force, #878's draft, and this one."""

    pri = load_script("power_replay_inforce_873_for_886", "power_replay_inforce_873.py")
    looks = pri.LOOKS[1:]
    records = {
        "draft of #873 (878)": json.loads(CALIBRATION_873.read_text(encoding="utf-8"))["comparison_critical_values"],
        "post-2020 stationary (886)": json.loads(CALIBRATION_886.read_text(encoding="utf-8"))["comparison_critical_values"],
    }
    sets = {"in force today": {n: sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in looks}}
    five = {"in force today": {n: sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON][n] for n in looks}}
    for name, record in records.items():
        sets[name] = {n: record[sp.GRID_COMPARISON][str(n)] for n in looks}
        five[name] = {n: record[sp.FIVE_LEVEL_COMPARISON][str(n)] for n in looks}
    return pri, sets, five


def replay_command(args) -> int:
    pri, sets, five = replay_value_sets()
    pr = pri.pr
    cells, _kinds, digest, _pool = pr.build_cells()
    result = {
        "panel_sha256": digest, "draft_873_sha256": sha256(CALIBRATION_873),
        "calibration_886_sha256": sha256(CALIBRATION_886), "days": pri.DAYS, "looks": list(pri.LOOKS),
        "study_end": pr.STUDY_END.isoformat(), "step": pr.STEP, "seed": pr.SEED,
        "values": {f"grid|{name}": {str(n): v for n, v in c.items()} for name, c in sets.items()}
        | {f"five|{name}": {str(n): v for n, v in c.items()} for name, c in five.items()},
        "replay": {},
    }
    for family, family_sets, pairs in (("grid", sets, pr.PAIRS), ("five", five, ("P3",))):
        for name, critical in family_sets.items():
            for pair in pairs:
                for kind in pr.KINDS:
                    result["replay"][f"{family}|{name}|{pair}|{kind}"] = pri.summarize(pri.replay(cells[pair], kind, critical))
                print("replayed", family, name, pair, flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


# -- the confirmation designs of #733 ------------------------------------------------------------------------------


def stationary_window_statistics(series, *, days, lengths, windows, seed, block=sp.BLOCK_LENGTH):
    """`confirmation_design.window_statistics` with stationary-bootstrap windows: sorted studentized means at each look."""

    values = [float(v) for v in series]
    truth = sum(values) / len(values)
    rng = random.Random(seed)
    out = {n: [] for n in lengths}
    for _ in range(windows):
        window = [values[i] for i in stationary_window_indices(len(values), days, rng, block)]
        for n in lengths:
            part = window[:n]
            out[n].append((sum(part) / n - truth) / sp._standard_error(part, sp.HAC_LAG, "a window"))
    return {n: sorted(v) for n, v in out.items()}


def design_values(job):
    """A design's values at looks 2 and 3 on the candidate-side series `e`: (a) full history, circular blocks (#873's
    reading) and (b) post-2020 days, stationary bootstrap (this one)."""

    cd = load_script("confirmation_design_for_886", "confirmation_design.py")
    design, series, windows = job
    looks = design.checkpoints
    levels = sp.nominal_levels(looks)
    full = cd.window_statistics(series.e, days=design.days, lengths=looks[1:], windows=windows, seed=cd.CALIBRATION_SEED)
    _days, post = post_2020(series.dates, series.e)
    after = stationary_window_statistics(post, days=design.days, lengths=looks[1:], windows=windows, seed=cd.CALIBRATION_SEED)
    return design.id, {
        "full_history_circular": {str(n): sp._bound(full[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])},
        "post_2020_stationary": {str(n): sp._bound(after[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])},
        "series_days": len(series.e), "post_2020_days": len(post),
    }


VALUE_SETS = ("full_history_circular", "post_2020_stationary")


def design_command(args) -> int:
    cd = load_script("confirmation_design_for_886", "confirmation_design.py")
    pool, digest = cd.load_pool()
    series = {d.id: cd.design_series(pool, d) for d in cd.DESIGNS}
    with multiprocessing.Pool(max(1, args.workers)) as workers:
        values = dict(workers.map(design_values, [(d, series[d.id], args.windows) for d in cd.DESIGNS]))
    histories = {(d.id, h): cd.history_slice(series[d.id], h) for d in cd.DESIGNS for h in ("full", "post-2020")}
    published = json.loads((DESIGN_733 / "result.json").read_text(encoding="utf-8"))
    result = {
        "panel_sha256": digest, "result_733_sha256": sha256(DESIGN_733 / "result.json"),
        "constants": {"windows": args.windows, "paths": args.paths, "seed": cd.SEED, "calibration_seed": cd.CALIBRATION_SEED,
                      "mme": sp.MME, "block_length": sp.BLOCK_LENGTH},
        "values": values, "published_733": {"values": {k: v["critical_values"] for k, v in published["designs"].items()},
                                            "reading": published["reading"]},
        "scenarios": {}, "reading": {},
    }
    for name in VALUE_SETS:
        critical = {k: v[name] for k, v in values.items()}
        scenarios = cd.simulate((histories, cd.DESIGNS), critical, paths=args.paths, workers=args.workers)
        result["scenarios"][name] = scenarios
        result["reading"][name] = cd.reading(scenarios)
        print("read", name, json.dumps(result["reading"][name]["admissible"]), result["reading"][name]["recommended"], flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


# -- the page ----------------------------------------------------------------------------------------------------------


def load(*parts):
    return json.loads(RESEARCH.joinpath(*parts).read_text(encoding="utf-8"))


def pct(p, se=None):
    return f"{100 * p:.1f}%" if se is None else f"{100 * p:.1f}% ± {196 * se:.1f}"


def share(p, paths):
    return pct(p, math.sqrt(p * (1 - p) / paths))


def num(value):
    return "none" if value is None else f"{value:.3f}"


def table(header, rows):
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]


def calibration_section(old, mid, new):
    rows = []
    for comparison, label in ((sp.GRID_COMPARISON, "efficacy, grid comparison (B2 against B1)"),
                              (sp.FIVE_LEVEL_COMPARISON, "efficacy, B3 against B1 (five levels)")):
        for n in ("125", "250"):
            rows.append([label, n, num(old["comparison_critical_values"][comparison][n]),
                         num(mid["comparison_critical_values"][comparison][n]),
                         num(new["comparison_critical_values"][comparison][n])])
    for n in ("60", "125", "250"):
        rows.append(["futility (upper bound of skill, grid comparison)", n,
                     num(old["futility_critical_values"][sp.GRID_COMPARISON][n]),
                     num(mid["futility_critical_values"][sp.GRID_COMPARISON][n]),
                     num(new["futility_critical_values"][sp.GRID_COMPARISON][n])])
    days = new["series_days"]
    return [
        "## 1. The calibrated values", "",
        f"Same looks, level, windows ({', '.join(f'{n}: {w:,}' for n, w in new['windows'].items())} for the efficacy value, "
        f"{new['futility_windows']:,} for futility) and seed {new['seed']} as the records of #695 and #873. Only the history and "
        f"the window generator change: the new column draws {new['generator']} (post-2020 series: "
        f"{days[sp.GRID_COMPARISON]:,} days for the grid comparison, {days[sp.FIVE_LEVEL_COMPARISON]:,} for B3's five levels; "
        f"decision days from {new['history_first_decision_day']}). Every column is in the orientation `{new['orientation']}` except "
        "the first. Look 1 has no efficacy value (Q-B).", "",
        *table(["value", "days", "in force (S(B2) - S(B1), circular, full history)", "#878's draft (S(B1) - S(candidate), circular, full history)", "new (S(B1) - S(candidate), stationary, post-2020)"], rows), "",
    ]


NAMES = {"a": "full history, circular blocks", "b": "post-2020-04, circular blocks",
         "c": "full history, stationary bootstrap", "d": "post-2020-04, stationary bootstrap"}


def power_section(mid, new):
    rows = []
    for reading, label in NAMES.items():
        for title, source in (("#878's values", mid), ("new values", new)):
            paths = source["constants"]["paths"]
            cells = source["readings"][reading]["cells"]
            row = [f"({reading}) {label}", title, share(cells["noise=1.0, delta=0.0"]["ungated"]["125"], paths),
                   share(cells["noise=1.0, delta=0.0"]["ungated"]["250"], paths)]
            for key in ("noise=1.0, delta=0.03", "noise=1.0, delta=0.1"):
                for n in ("125", "250"):
                    row.append(share(cells[key]["gated"][n], paths))
            rows.append(row)
    return [
        "## 2. Size and power at the MME and at 10%", "",
        f"`scripts/power_study_769.py` (the rule, the paths and the four readings of #769; {new['constants']['paths']:,} paths per "
        f"cell, seed {new['constants']['seed']}) at the critical values at looks 2 and 3 (#878's: "
        f"{', '.join(f'{k}: {v:.3f}' for k, v in mid['constants']['critical_values'].items())}; new: "
        f"{', '.join(f'{k}: {v:.3f}' for k, v in new['constants']['critical_values'].items())}). Size is the share of null paths "
        "detected by that look (the test without the MME gate); power is the MME-gated share at a true skill of 3% (the MME) and "
        "10% against B1 (`NOISE` = 1). Each figure carries ± 1.96 Monte Carlo standard errors. The B2 half of Supported is not "
        "simulated, so each power is an upper bound.", "",
        *table(["reading", "values", "size 125", "size 250", "3% 125", "3% 250", "10% 125", "10% 250"], rows), "",
    ]


def replay_section(replay):
    pairs = {"P2": "P2 B2 vs B1", "P2r": "P2r B1 vs B2 (a reversed pair, a diagnostic)", "P3": "P3 B3 vs B1"}
    kinds = {"real": "real pair", "E1": "E1 relabelled copy", "E2": "E2 demeaned", "E3": "E3 sign-flipped"}
    out = ["## 3. The replay of #754 and #792 at the corrected values", "",
           f"`scripts/power_replay_inforce_873.py`'s windows ({replay['days']} days, slid every {replay['step']} days, no day after "
           f"{replay['study_end']}), read at looks {', '.join(str(n) for n in replay['looks'])} at three sets of values for the grid "
           "comparison and, on P3 only, at the matching five-level values. Share of windows flagged (MME-gated in brackets), with a "
           "moving-block 95% interval for the test share. The windows overlap, so the effective number of independent windows is "
           "small (7 at 250 days): read the interval, not the share.", ""]
    for family, names in (("grid", [n.split("|", 1)[1] for n in replay["values"] if n.startswith("grid|")]),
                          ("five", [n.split("|", 1)[1] for n in replay["values"] if n.startswith("five|")])):
        for name in names:
            out += [f"### {'Grid' if family == 'grid' else 'B3 five-level'} values: {name} "
                    f"({', '.join(f'{k}: {v:.3f}' for k, v in replay['values'][f'{family}|{name}'].items())})", ""]
            rows = []
            for pair, plabel in pairs.items():
                if f"{family}|{name}|{pair}|real" not in replay["replay"]:
                    continue
                for kind, klabel in kinds.items():
                    cell = replay["replay"][f"{family}|{name}|{pair}|{kind}"]["all"]
                    s, lo, hi = cell["test"]
                    rows.append([plabel, klabel, str(cell["windows"]), str(cell["effective"]),
                                 f"{pct(s)} ({pct(cell['gated'][0])}) [{pct(lo)}, {pct(hi)}]"])
            out += table(["pair", "series", "windows", "effective", "test (gated) [interval]"], rows) + [""]
    return out


def design_section(design):
    published = design["published_733"]
    designs = sorted(design["values"])
    rows = []
    for d in designs:
        rows.append([d, "#733 as published (largest across four orientations, full history, circular)",
                     " / ".join(f"{v:.2f}" for v in published["values"][d].values())])
        for name, label in (("full_history_circular", "candidate orientation, full history, circular"),
                            ("post_2020_stationary", "candidate orientation, post-2020, stationary")):
            rows.append([d, label, " / ".join(f"{v:.2f}" for v in design["values"][d][name].values())])
    out = ["## 4. #733's confirmation designs on the corrected test", "",
           f"`scripts/postcovid_886.py design` ({design['constants']['windows']:,} windows per value, "
           f"{design['constants']['paths']:,} paths per scenario, seeds of `scripts/confirmation_design.py`, panel "
           f"`{design['panel_sha256'][:8]}…`): each of #733's six designs, with its values at looks 2 and 3 recalibrated on the "
           "candidate-side series (`S(B1) - S(candidate)`), either on the full history with circular blocks (the reading #873 "
           "adopted) or on the post-2020 days with stationary-bootstrap windows (this step), then simulated under #733's "
           "scenarios and read by #733's rule (§7: admissible when size is at most 5% on both histories; recommended: the "
           "shortest design within one standard error of the best power at 3%).", "",
           "### Values at looks 2 and 3", "", *table(["design", "values", "look 2 / look 3"], rows), ""]
    for name, label in (("full_history_circular", "candidate orientation, full history, circular"),
                        ("post_2020_stationary", "candidate orientation, post-2020, stationary")):
        reading = design["reading"][name]
        rows = []
        for d in designs:
            r = reading["rows"][d]
            rows.append([d, str(r["days"]), pct(r["size_full"]), pct(r["size_post_2020"]), pct(r["power_3"]),
                         pct(r["power_10"]), pct(r["power_3_post_2020"]), pct(r["power_10_post_2020"]),
                         "yes" if r["admissible"] else "no"])
        out += [f"### Size and power: {label}", "",
                *table(["design", "days", "size, full", "size, post-2020", "power at 3%, full", "power at 10%, full",
                        "power at 3%, post-2020", "power at 10%, post-2020", "admissible"], rows), "",
                f"Admissible: {', '.join(reading['admissible']) or 'none'}. Recommended by §7: {reading['recommended'] or 'none'}.", ""]
    before = design["published_733"]["reading"]
    out += [f"#733 as published: admissible {', '.join(before['admissible']) or 'none'}; recommended {before['recommended'] or 'none'}.", ""]
    return out


def sources():
    return {
        "old": load("protocol-calibration", "result.json"), "mid": load("protocol-calibration-873", "result.json"),
        "new": load("protocol-calibration-886", "result.json"),
        "power_mid": load("power-study-873", "result.json"), "power_new": load("power-study-886", "result.json"),
        "replay": load("power-replay-886", "result.json"), "design": load("confirmation-design-886", "result.json"),
    }


def render(s) -> str:
    lines = [
        "# The corrected test on post-2020 resampled history: result (H1 step 5, #886)", "",
        "**Development and simulated data only; no verdict, no lockbox day scored.** Every figure below is read from "
        "`docs/research/protocol-calibration-886/result.json`, `power-study-886/result.json`, `power-replay-886/result.json` and "
        "`confirmation-design-886/result.json` (with #878's records beside them) by `scripts/postcovid_886.py report`. "
        "`scoring_protocol.CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are unchanged "
        "by this step.", "",
        *calibration_section(s["old"], s["mid"], s["new"]), *power_section(s["power_mid"], s["power_new"]),
        *replay_section(s["replay"]), *design_section(s["design"]),
    ]
    return "\n".join(lines) + "\n"


def report_command(args) -> int:
    PAGE.write_text(render(sources()), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(args) -> int:
    s = sources()
    study = load_script("power_study_769_for_886", "power_study_769.py")
    if study.main(["check", "--out", str(POWER_886)]) != 0:
        return 1
    if s["replay"]["calibration_886_sha256"] != sha256(CALIBRATION_886) or s["replay"]["draft_873_sha256"] != sha256(CALIBRATION_873):
        raise ValueError("power-replay-886 was made from other calibration records")
    if s["design"]["result_733_sha256"] != sha256(DESIGN_733 / "result.json"):
        raise ValueError("confirmation-design-886 was made against another #733 result")
    if PAGE.read_text(encoding="utf-8") != render(s):
        raise ValueError(f"{PAGE.name} is not what `report` writes; run `python3 scripts/postcovid_886.py report`")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calibrate")
    cal.add_argument("--write", action="store_true")
    cal.set_defaults(func=calibrate_command)
    power = sub.add_parser("power")
    power.add_argument("--out", required=True)
    power.add_argument("--paths", type=int, default=2000)
    power.set_defaults(func=power_command)
    replay = sub.add_parser("replay")
    replay.add_argument("--out", required=True)
    replay.set_defaults(func=replay_command)
    design = sub.add_parser("design")
    design.add_argument("--out", required=True)
    design.add_argument("--windows", type=int, default=20_000)
    design.add_argument("--paths", type=int, default=2_000)
    design.add_argument("--workers", type=int, default=1)
    design.set_defaults(func=design_command)
    for name, func in (("report", report_command), ("check", check_command)):
        sub.add_parser(name).set_defaults(func=func)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
