#!/usr/bin/env python3
"""The H3 source screen with the OFR cleared-repo series read at the page's stated lag (#968, Lens E of #958).

A scratch measurement, not a record: nothing is selected, no model changes, no published declaration changes, and
no day in a locked tier is read (`docs/decisions/lockbox.md`; the screen refuses a panel past 2026-09-03). It
writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.

    PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv AUG2D.csv --output SCREEN.csv
    PYTHONPATH=src python3 scripts/source_screen.py run --panel SCREEN.csv --output OUT/screen.json
    PYTHONPATH=src python3 scripts/ofr_cleared_lag_968.py compare OUT/screen.json --output OUT/compare.json --markdown OUT/compare.md

`source_screen.py panel` adds a corrected-lag copy (suffix `_1d`) of each cleared-repo column: the same values, read by the
as-of rule at `ofr_stfm_repo_cleared` (one business day, 15:00) instead of `ofr_stfm_repo` (two business days, 16:00).
`compare` sets each column beside its copy in one screen, so the data, the days and the reading rules are the same and only
the lag differs. It also checks what must hold, and refuses to write if it does not:

* every other series' cells are what the screen gives without the copies (`--base`, a screen of the panel without them,
  optional);
* a copy read at lead L is the original read at lead L - 1 (the same row), for the leads both were computed at.

`gbm` is #187's paired test for `ofr_dvp_minus_bgcr_bp` alone, at both lags, on the OFR window. After
`dvp_segment_inputs.py run` (control@ofr, persistence_logistic@ofr, ofr_dvp_minus_bgcr_bp and ofr_dvp_minus_bgcr_bp@1d, at
h = 1 to 5), `pair` (the two groups, at h = 1 to 5) and `crps` (the two groups) have written RUNS:

    PYTHONPATH=src python3 scripts/ofr_cleared_lag_968.py gbm --runs RUNS --output OUT/gbm.json --markdown OUT/gbm.md

Each reading's p-values are #187's (one-sided paired stationary bootstrap, `P_VALUE_REPLICATIONS`, the same seeds), but the
Holm correction runs over that reading's own comparisons only (`FAMILY`), not #187's family of every group: the other groups are
not re-scored here. The two readings are corrected alike, so they are comparable with each other and not with #187's outcome.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import dvp_segment  # noqa: E402
from repo_model.dvp_segment import BENCHMARKS, HORIZONS, ONSET, POOLED, THRESHOLDS, comparison_key  # noqa: E402

#: (two-day original, one-day copy), in the order the tables use.
PAIRS: Tuple[Tuple[str, str], ...] = (
    ("ofr_dvp_minus_bgcr_bp", "ofr_dvp_minus_bgcr_bp_1d"),
    ("ofr_dvp_rate", "ofr_dvp_rate_1d"),
    ("ofr_gcf_rate", "ofr_gcf_rate_1d"),
)
LEADS = ("1", "2", "3", "5", "10")
#: Table 1 of the screen: the series with the largest absolute pooled correlation, over the leads.
TOP = 12


def _cell(series: Mapping, lead: str, split: str = "all", target: str = "pressure") -> Mapping:
    return series["leads"][lead][split][target]


def check_identity(original: Mapping, copy: Mapping) -> List[str]:
    """Problems with "a copy at lead L is the original at lead L - 1", for the leads both were computed at."""

    problems = []
    for lead in LEADS:
        earlier = str(int(lead) - 1)
        if earlier not in original["leads"] or lead not in copy["leads"]:
            continue
        for target in ("pressure", "level", "change"):
            if _cell(copy, lead, target=target) != _cell(original, earlier, target=target):
                problems.append(f"lead {lead} of the copy differs from lead {earlier} of the original ({target})")
    return problems


def check_others(base: Mapping, screen: Mapping) -> List[str]:
    """Series other than the copies that differ between a screen without them (`base`) and with them."""

    copies = {copy for _o, copy in PAIRS}
    problems = [f"{name} differs" for name in sorted(base["series"]) if base["series"][name] != screen["series"].get(name)]
    problems += [f"{name} is new" for name in sorted(set(screen["series"]) - set(base["series"]) - copies)]
    return problems


def _strength(series: Mapping) -> Optional[float]:
    values = [abs(_cell(series, lead)["rho"]) for lead in series["leads"] if _cell(series, lead)["rho"] is not None]
    return max(values) if values else None


def ranks(screen: Mapping, swap: bool) -> Dict[str, Tuple[int, int]]:
    """Each paired column's rank among the screened series by `_strength` (1 = strongest), and the series counted.

    With `swap` the copies stand in for their originals, so the count is the screen's own.
    """

    left_out = {o for o, _c in PAIRS} if swap else {c for _o, c in PAIRS}
    pool = {name: series for name, series in screen["series"].items() if name not in left_out}
    strengths = {name: _strength(series) for name, series in pool.items()}
    ordered = sorted((n for n in strengths if strengths[n] is not None), key=lambda n: (-strengths[n], n))
    return {name: (ordered.index(name) + 1, len(ordered)) for name in ordered if name in {p for pair in PAIRS for p in pair}}


def count_identity_breaks(original: Mapping, copy: Mapping) -> int:
    """How many cells of a copy are not the original's one lead earlier (the opposite of `check_identity`)."""

    return len(check_identity(original, copy))


def compare(screen: Mapping, base: Optional[Mapping] = None, government_open_days: bool = False) -> dict:
    """The paired tables and the checks; raises `ValueError` if a check fails.

    With `government_open_days` (#1016) the copies are dated by the days the government is open, so a copy at lead L
    is no longer the original at lead L - 1 on the days after a statutory holiday the market opened: that check is
    replaced by a count of the cells that differ.
    """

    problems: List[str] = []
    if base is not None:
        problems += check_others(base, screen)
    breaks = {}
    for original, copy in PAIRS:
        if government_open_days:
            breaks[copy] = count_identity_breaks(screen["series"][original], screen["series"][copy])
        else:
            problems += [f"{copy}: {p}" for p in check_identity(screen["series"][original], screen["series"][copy])]
    if problems:
        raise ValueError("; ".join(problems))
    own = ranks(screen, swap=False)
    swapped = ranks(screen, swap=True)
    pairs = {}
    for original, copy in PAIRS:
        o, c = screen["series"][original], screen["series"][copy]
        pairs[original] = {
            "copy": copy,
            "rank_two_day": own.get(original),
            "rank_one_day": swapped.get(copy),
            "pressure_by_lead": {
                lead: {"two_day": _cell(o, lead), "one_day": _cell(c, lead)} for lead in LEADS
            },
            "level_change_lead1": {
                target: {"two_day": _cell(o, "1", target=target), "one_day": _cell(c, "1", target=target)}
                for target in ("level", "change")
            },
            "regimes_lead1": {
                regime: {"two_day": _cell(o, "1", regime), "one_day": _cell(c, "1", regime)}
                for regime in ("regime:ample", "regime:scarce")
            },
            "pre_onset_lead1": {"two_day": o["pre_onset"]["all"], "one_day": c["pre_onset"]["all"]},
        }
    top_two = [n for n in _top(screen, set(c for _o, c in PAIRS))]
    top_one = [n for n in _top(screen, set(o for o, _c in PAIRS))]
    return {
        "scope": screen["scope"],
        "pairs": pairs,
        "top_two_day": top_two,
        "top_one_day": top_one,
        "checks": {
            "other_series_unchanged": base is not None,
            "copy_equals_original_one_lead_earlier": not government_open_days,
            **({"cells_differing_from_one_lead_earlier": breaks} if government_open_days else {}),
        },
    }


def _top(screen: Mapping, exclude: set) -> List[str]:
    strengths = {n: _strength(s) for n, s in screen["series"].items() if n not in exclude}
    ordered = sorted((n for n in strengths if strengths[n] is not None), key=lambda n: (-strengths[n], n))
    return ordered[:TOP]


def _f(value: Optional[float], digits: int = 3) -> str:
    return "-" if value is None else f"{value:+.{digits}f}"


def markdown(result: Mapping) -> str:
    scope = result["scope"]
    lines = [
        "# The cleared-repo series at the page's stated lag, beside the declared one (#968)",
        "",
        f"{scope['scored_days']:,} scored days ({scope['first_day']} to {scope['last_day']}), {scope['pressure_days']} above +5 bp; "
        f"panel `{scope['panel_sha256'][:12]}…`. Each column is read twice in one screen: at the declared lag "
        "(`ofr_stfm_repo`, two business days, 16:00) and at the lag the OFR's page states (`ofr_stfm_repo_cleared`, one business day, 15:00; the `_1d` columns).",
        "",
        "## Table 1. Spearman correlation with the +5 bp indicator, pooled, by lead",
        "",
        "| series | reading | " + " | ".join(f"lead {l}" for l in LEADS) + " | days at lead 1 | rank at the strongest lead |",
        "|---|---|" + "---|" * (len(LEADS) + 2),
    ]
    for original, data in result["pairs"].items():
        for key, name, label in (("two_day", original, "declared (2 days)"), ("one_day", data["copy"], "stated (1 day)")):
            rank = data["rank_two_day" if key == "two_day" else "rank_one_day"]
            lines.append(
                f"| `{name}` | {label} | "
                + " | ".join(_f(data["pressure_by_lead"][l][key]["rho"]) for l in LEADS)
                + f" | {data['pressure_by_lead']['1'][key]['n']} | {rank[0]} of {rank[1]} |"
            )
    lines += [
        "",
        "## Table 2. Lead 1 in detail",
        "",
        "| series | reading | level | change | ample days (pressure) | scarce days (pressure) | pre-onset AUC | pre-onset mean diff / sd |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for original, data in result["pairs"].items():
        for key, name, label in (("two_day", original, "declared"), ("one_day", data["copy"], "stated")):
            ample, scarce = (data["regimes_lead1"][r][key] for r in ("regime:ample", "regime:scarce"))
            pre = data["pre_onset_lead1"][key]
            lines.append(
                f"| `{name}` | {label} | {_f(data['level_change_lead1']['level'][key]['rho'])} | "
                f"{_f(data['level_change_lead1']['change'][key]['rho'])} | "
                f"{_f(ample['rho'])} ({ample['pressure_days']}) | {_f(scarce['rho'])} ({scarce['pressure_days']}) | "
                f"{pre['auc']:.3f} | {pre['std_diff']:+.2f} |"
            )
    lines += [
        "",
        "## Checks",
        "",
        "* Every cell of every other series is identical to the same screen without the `_1d` columns."
        if result["checks"]["other_series_unchanged"]
        else "* The comparison with a screen without the `_1d` columns was not requested.",
        "* A `_1d` column at lead L equals its original at lead L - 1 in every cell (the same row is read), for every lead both were computed at."
        if result["checks"]["copy_equals_original_one_lead_earlier"]
        else "* A `_1d` column is dated by the days the government is open (#1016), so it differs from its original one lead earlier "
        "on the days after a statutory holiday the market opened; cells that differ: "
        + ", ".join(f"`{c}` {n}" for c, n in sorted(result["checks"]["cells_differing_from_one_lead_earlier"].items())) + ".",
        "",
        (
            f"The twelve strongest series (largest absolute pooled correlation over the leads) are the same with the declared and with the stated lag, "
            f"and none of the three cleared-repo columns is among them: {', '.join(f'`{n}`' for n in result['top_two_day'])}."
            if result["top_two_day"] == result["top_one_day"]
            else f"The twelve strongest series differ: {', '.join(f'`{n}`' for n in result['top_two_day'])} with the declared lag, "
            f"{', '.join(f'`{n}`' for n in result['top_one_day'])} with the stated one."
        )
        + " Exploratory, unadjusted for multiplicity.",
        "",
    ]
    return "\n".join(lines)


# -- #187's paired test, at both lags ------------------------------------------------------------

GROUP = "ofr_dvp_minus_bgcr_bp"
#: The two readings: the declared lag (#187's group) and the page's stated lag.
READINGS: Tuple[Tuple[str, str], ...] = ((GROUP, "declared (2 days)"), (GROUP + "@1d", "stated (1 day)"))


def _group(name: str) -> dvp_segment.Group:
    base = next(g for g in dvp_segment.GROUPS if g.name == GROUP)
    return base._replace(name=name)


def narrow_family(entries: Dict[str, dict], name: str) -> dict:
    """Holm over one reading's own comparisons, then `dvp_segment.classify` of the reading as a group.

    `entries` maps `comparison_key`s to entries with `mean`, `p_improve`, `p_worse` (Brier entries on all days also
    `regimes`). Adds `holm_improve` and `holm_worse` to the reading's entries in place and returns the classification.
    """

    own = {key for key in entries if key.split("|", 1)[0] == name}
    improve = dvp_segment.holm({key: entries[key]["p_improve"] for key in own})
    worse = dvp_segment.holm({key: entries[key]["p_worse"] for key in own})
    for key in own:
        entries[key]["holm_improve"], entries[key]["holm_worse"] = improve[key], worse[key]
    return dvp_segment.classify(_group(name), {key: entries[key] for key in own})




def gbm(runs: Path, readings: Tuple[Tuple[str, str], ...] = READINGS) -> dict:
    """The readings' paired comparisons, p-values and classification from the files `pair` and `crps` wrote.

    `readings` is both of #968's by default. A grid's series are resampled with the same draws and each p-value is its
    own series', so one reading alone (#1016) gets the p-values it would have beside the other (the same seed and days).
    """

    from repo_model import ml

    entries: Dict[str, dict] = {}
    grids: Dict[tuple, list] = {}
    for name, _label in readings:
        for h in HORIZONS:
            paired = json.loads((runs / f"pair_{name}_h{h}.json").read_text())
            entries.update(paired["entries"])
            for window, h_, day_set, block, key, differences in paired["grid_members"]:
                grids.setdefault((window, h_, day_set, block), []).append((key, differences))
        crps = json.loads((runs / f"crps_{name}.json").read_text())["comparison"]
        key = comparison_key(name, "crps")
        per_origin = [origin["difference_bps"] for origin in crps["per_origin"]]
        if max(origin["scored_date"] for origin in crps["per_origin"]) > "2025-12-31":
            raise ValueError(f"{name}: CRPS scored a locked day")
        entries[key] = {
            "mean": crps["mean_difference_bps"],
            "interval": crps["mean_difference_interval"],
            "days": crps["origin_count"],
            "control_crps_bps": crps["model_a"]["crps_bps"],
            "candidate_crps_bps": crps["model_b"]["crps_bps"],
        }
        grids.setdefault(("ofr", 1, "crps", crps["mean_difference_interval"]["block_length"]), []).append((key, per_origin))
    for (window, h, day_set, block), members in sorted(grids.items(), key=lambda item: str(item[0])):
        if len({len(values) for _key, values in members}) != 1:
            raise ValueError(f"grid {window} h{h} {day_set}: the readings' day sets differ")
        p_values = ml.paired_bootstrap_p_values(
            [values for _key, values in members],
            block_length=block,
            seed=dvp_segment.p_value_seed(window, h, day_set),
            replications=dvp_segment.P_VALUE_REPLICATIONS,
        )
        for (key, _values), (p_improve, p_worse) in zip(members, p_values):
            entries[key]["p_improve"], entries[key]["p_worse"] = p_improve, p_worse
    outcomes = {name: narrow_family(entries, name) for name, _label in readings}
    return {
        "directive": "#968",
        "status": "scratch measurement; development data, not a verdict; nothing published moves",
        "holm_family": "each reading's own comparisons (40 Brier and 1 CRPS), not #187's family",
        "outcomes": outcomes,
        "comparisons": entries,
    }


def _iv(entry: Mapping, places: int = 4) -> str:
    interval = entry["interval"]
    return f"{entry['mean']:+.{places}f} [{interval['lower']:+.{places}f}, {interval['upper']:+.{places}f}]"


def _p(entry: Mapping) -> str:
    mark = " ✓" if entry.get("holm_improve") else (" ✗" if entry.get("holm_worse") else "")
    return f"{entry['p_improve']:.4f}{mark}"


def gbm_markdown(result: Mapping) -> str:
    entries = result["comparisons"]
    out = [
        "## Table 3. #187's paired test for `ofr_dvp_minus_bgcr_bp`, at both lags (OFR window)",
        "",
        "Paired Brier difference, benchmark minus candidate (positive favours the input), 90% stationary-bootstrap interval, and the one-sided "
        "p for improvement. ✓ = survives Holm over that reading's own 41 comparisons; ✗ = significantly worse after it.",
        "",
    ]
    for day_set, title in ((POOLED, "all scored days"), (ONSET, "onset days (#160)")):
        out += [
            f"### Brier, {title}",
            "",
            "| reading | h | +5 vs v1 | p | +5 vs persistence-logistic | p | +10 vs v1 | p | +10 vs persistence-logistic | p |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for name, label in READINGS:
            for h in HORIZONS:
                cells: List[str] = []
                for tau in THRESHOLDS:
                    for bench in BENCHMARKS:
                        entry = entries[comparison_key(name, "brier", day_set, tau, h, bench)]
                        cells += [_iv(entry), _p(entry)]
                out.append(f"| {label} | {h} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["### CRPS, horizon 1: control minus candidate, bp", "", "| reading | CRPS control | CRPS candidate | difference | p improve | p worse |", "|---|---|---|---|---|---|"]
    for name, label in READINGS:
        entry = entries[comparison_key(name, "crps")]
        out.append(
            f"| {label} | {entry['control_crps_bps']:.4f} | {entry['candidate_crps_bps']:.4f} | {_iv(entry)} | {_p(entry)} | {entry['p_worse']:.4f} |"
        )
    out += ["", "### The win rule (#187, items 3-5), as `dvp_segment.classify` reads it", "", "| reading | outcome | +5 bp | +10 bp |", "|---|---|---|---|"]
    for name, label in READINGS:
        verdict = result["outcomes"][name]
        cells = []
        for tau in ("5", "10"):
            t = verdict["by_threshold"][tau]
            missed = [k.split("_", 1)[0] for k, v in t["conditions"].items() if not v]
            cells.append(f"{t['outcome']}; survives at h={t['horizons_surviving_correction'] or '–'}; misses {', '.join(missed) or 'none'}")
        out.append(f"| {label} | **{verdict['outcome']}** | " + " | ".join(cells) + " |")
    out.append("")
    return "\n".join(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("compare", help="set each cleared-repo column beside its corrected-lag copy")
    one.add_argument("screen", type=Path, help="source_screen.py run's JSON on a panel carrying the _1d columns")
    one.add_argument("--base", type=Path, help="the same screen on the panel without them (checks the other series)")
    one.add_argument("--output", type=Path, required=True)
    one.add_argument("--markdown", type=Path, required=True)
    one.add_argument(
        "--government-open-days", action="store_true",
        help="the screen was run with source_screen.py --government-open-days (#1016): count, do not require, the identity",
    )
    two = sub.add_parser("gbm", help="#187's paired test for ofr_dvp_minus_bgcr_bp at both lags")
    two.add_argument("--runs", type=Path, required=True)
    two.add_argument("--output", type=Path, required=True)
    two.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "gbm":
        result = gbm(args.runs)
        args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        args.markdown.write_text(gbm_markdown(result), encoding="utf-8")
        print(json.dumps({"outcomes": {k: v["outcome"] for k, v in result["outcomes"].items()}}))
        return 0
    screen = json.loads(args.screen.read_text())
    base = json.loads(args.base.read_text()) if args.base else None
    result = compare(screen, base, args.government_open_days)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"pairs": list(result["pairs"]), "checks": result["checks"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
