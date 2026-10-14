#!/usr/bin/env python3
"""H3 step 3 (#708): each new source family added to H5's candidate, one at a time. Walks, scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/h3_nested_708.json`, which this script refuses to read unless it is committed and unchanged.
Scored decision days end where their fifth target day is on or before 2025-12-31 (`docs/decisions/lockbox.md`). Development
days give a score and an interval, never a verdict (scoring protocol v1, #640). The walk, the benchmarks and the scorer are
#634's (`scripts/spread_distribution_634.py`); this script adds the family columns and the nested pairs.

    # panels: #634's chain (see its docstring), then the four families' columns on top
    PYTHONPATH=src python3 scripts/new_sources.py panel --panel AUG2D.csv --output NEW.csv
    for h in 1 2 3 4 5: for v in base plus_nyfed_pd_financing plus_treasury_auction_results \\
            plus_nyfed_on_rrp_counterparties plus_treasury_dts_debt_cash:
        PYTHONPATH=src python3 scripts/h3_nested_708.py walk --variant $v --horizon $h --published PUBLISHED.csv \\
            --panel NEW.csv --output OUT/${v}_h$h.json
    PYTHONPATH=src python3 scripts/h3_nested_708.py score --published PUBLISHED.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/h3_nested_708.py report --score OUT/score.json --output OUT/report.md

`walk` is #634's variant (b) walk with the family's columns added to the features, under a declaration that switches the
columns on for this run only (they stay off in every published declaration), so the as-of rule governs each column at its
registered availability. A walk whose output already holds the same variant and lead, from the same panel bytes, is skipped.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s634 = _load("spread_distribution_634")

from repo_model import contract, ml, new_sources, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "h3_nested_708.json"
SEED = 708
HORIZONS = sp.HORIZONS
GRID = sp.GRID
LAST_TARGET = date(2025, 12, 31)
DECISION = s634.DECISION
SPLITS = s634.SPLITS
SOURCES = s634.SOURCES
VARIANTS = ("base",) + tuple(f"plus_{family}" for family in new_sources.SOURCES)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    import subprocess

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


DECLARATION_DATA = json.loads(DECLARATION.read_text(encoding="utf-8"))


def family_columns(declaration: Mapping) -> Dict[str, Tuple[str, ...]]:
    """The declared families and their columns."""

    return {name: tuple(entry["columns"]) for name, entry in declaration["families"].items() if isinstance(entry, dict)}


def family_of(variant: str) -> Optional[str]:
    """The family a variant adds to the candidate; `None` for the candidate itself."""

    if variant == "base":
        return None
    family = variant[len("plus_"):] if variant.startswith("plus_") else None
    if family not in new_sources.SOURCES:
        raise ValueError(f"{variant!r} is not a declared variant")
    return family


def family_features(horizon: int, family: Optional[str]) -> Tuple[str, ...]:
    """The candidate's features at `horizon` and, if `family` is given, its declared columns."""

    columns = family_columns(DECLARATION_DATA)[family] if family else ()
    return tuple(sorted(set(s634.new_features(horizon)) | set(columns)))


@contextlib.contextmanager
def switched_on():
    """#634's new inputs and the families' columns in the feature map, for this run only."""

    sdist = s634._load("satiation_distance_598")
    with sdist.switched_on():
        fields = dict(new_sources.COLUMN_FIELDS)
        with mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType(
                {**contract.FEATURE_SOURCES, **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()}}
            ),
        ):
            yield


def holm(p_values: Sequence[float]) -> List[float]:
    """Holm's step-down adjustment, in the input order."""

    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


def finished_walk(output: Path, *, variant: str, horizon: int, published: Path, panel: Path) -> bool:
    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(document, dict) or not isinstance(document.get("laws"), dict):
        return False
    return (
        document.get("variant") == variant
        and document.get("horizon") == horizon
        and document.get("panel_sha256") == panel_sha256(published)
        and document.get("scratch_panel_sha256") == panel_sha256(panel)
    )


# -- the walks -------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    declared = committed_declaration()
    h, variant = args.horizon, args.variant
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    if variant not in VARIANTS:
        raise SystemExit(f"{variant!r} is not a declared variant")
    require_unlocked([LAST_TARGET], where="h3_nested_708")
    if finished_walk(args.output, variant=variant, horizon=h, published=args.published, panel=args.panel):
        print(json.dumps({"variant": variant, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    minimum, refit = declared["scoring"]["minimum_history"], declared["scoring"]["refit_every"]
    audit_panel(load_daily_panel(args.published))
    sdist = s634._load("satiation_distance_598")
    from repo_model import scarcity

    panel = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(panel)
    registry = sdist.measurement_fields.load_registry()
    timed_rows, timed_registry = sdist.ann.arm_inputs("both", panel, registry, h)
    features = family_features(h, family_of(variant))
    with switched_on(), sdist.h41_release.release_dating(), scarcity.own_leg_composition():
        fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID)
        result, levels, settings = s634.walk(
            timed_rows, fit=fit, features=features, online_calibration=None, registry=timed_registry, horizon=h,
            minimum_history=minimum, refit_every=refit, expected_levels=GRID,
        )
    laws = {timed_rows[i].date.isoformat(): q for i, q in result}
    document = {
        "variant": variant, "horizon": h, "levels": levels,
        "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features), "settings": json.loads(json.dumps(settings, default=str)), "laws": laws,
    }
    partial = args.output.with_name(args.output.name + ".partial")
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the score -------------------------------------------------------------------------------------------------------


def score_command(args) -> int:
    declared = committed_declaration()
    require_unlocked([LAST_TARGET], where="h3_nested_708")
    draws = args.draws
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    walks = {name: s634.load_laws(args.walks, name) for name in VARIANTS}
    decisions, days_by = {}, {}
    for name, laws in walks.items():
        decisions[name], days_by[name] = s634.lead_forecasts(laws, calendar)
    common = sorted(set.intersection(*(set(d) for d in days_by.values())))
    common = [day for day in common if all(calendar[position[day] + h] <= LAST_TARGET for h in HORIZONS)]
    s634.refuse_locked(common + [calendar[position[day] + h] for day in common for h in HORIZONS])
    usable, unbuilt = [], []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=DECISION)
            pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError as error:
            unbuilt.append((day.isoformat(), str(error)))
    common = usable
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=DECISION, splits=splits)
    forecasts: Dict[str, dict] = {"B1": b1, "B2": b2}
    missing = {}
    for name in VARIANTS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = ["B1", "B2", *VARIANTS]
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    secondary = {n: sp.day_scores(forecasts[n], outcomes, calendar, score=sp.upper_tail_twcrps) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days or sorted(secondary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    families = [v for v in VARIANTS if v != "base"]
    nested = [("base", v) for v in families]
    versus = [(b, c) for c in VARIANTS for b in ("B1", "B2")]
    pairs = nested + versus
    document: dict = {
        "declaration": "metadata/h3_nested_708.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws, "seed": SEED, "decision_days_without_a_benchmark": unbuilt, "missing": missing, "names": names,
        "families": families,
        "mean_primary": {n: sum(primary[n].values()) / len(days) for n in names},
        "mean_key_secondary": {n: sum(secondary[n].values()) / len(days) for n in names},
    }
    document["pooled_primary"] = pair_table(primary, pairs, days, draws)
    document["pooled_key_secondary"] = pair_table(secondary, pairs, days, draws)
    nested_p = [document["pooled_primary"][f"{b} -> {c}"]["bootstrap_p"] for b, c in nested]
    for (b, c), adjusted in zip(nested, holm(nested_p)):
        document["pooled_primary"][f"{b} -> {c}"]["holm_p"] = adjusted
    cells = {n: s634.cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in names}
    document["by_lead"] = {
        n: {str(h): sum(v for (d, hh), v in cells[n].items() if hh == h) / max(1, sum(1 for (d, hh) in cells[n] if hh == h)) for h in HORIZONS}
        for n in names
    }
    document["by_lead_nested"] = {
        f"{b} -> {c}": {
            str(h): {
                "mean_difference": sum(cells[b][k] - cells[c][k] for k in cells[b] if k[1] == h and k in cells[c])
                / max(1, sum(1 for k in cells[b] if k[1] == h and k in cells[c]))
            }
            for h in HORIZONS
        }
        for b, c in nested
    }
    # splits: the as-of scarcity state of the decision day (lead 1), the pressure-day type of the target, the provisional regimes
    states = _scarcity_states()
    from repo_model import risk_date_spread as rds

    def group_of(day: date) -> str:
        return rds.state_group(states.get(calendar[position[day] + 1]))

    document["by_scarcity_state"] = {}
    for label in sorted({group_of(d) for d in days}):
        group = [d for d in days if group_of(d) == label]
        if len(group) > sp.HAC_LAG:
            document["by_scarcity_state"][label] = {
                "n": len(group),
                "mean_primary": {n: sum(primary[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(primary, pairs, group, draws),
            }
    document["by_regime"] = {}
    for label in splits.regime_labels:
        group = [d for d in days if splits.regime(d) == label]
        if len(group) > sp.HAC_LAG:
            document["by_regime"][label] = {
                "n": len(group),
                "mean_primary": {n: sum(primary[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(primary, pairs, group, draws),
            }

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    kinds = sorted({kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS})
    document["by_type"] = {}
    for kind in kinds:
        include = lambda d, h, kind=kind: kind_of(calendar[position[d] + h]) == kind
        means = {n: s634.day_means(cells[n], include) for n in names}
        group = sorted(set.intersection(*(set(m) for m in means.values())))
        if len(group) > sp.HAC_LAG:
            document["by_type"][kind] = {
                "decision_days": len(group),
                "mean_primary": {n: sum(means[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(means, pairs, group, draws),
            }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


def pair_table(scores, pairs, days, draws) -> Dict[str, dict]:
    """`paired_tests` of each (benchmark, candidate) pair on `days` at this directive's seed; empty when the days cannot carry the lag."""

    if len(days) <= sp.HAC_LAG:
        return {}
    chosen = [({d: scores[b][d] for d in days}, {d: scores[c][d] for d in days}) for b, c in pairs]
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return {f"{b} -> {c}": s634.summarise(test) for (b, c), test in zip(pairs, tests)}


def _scarcity_states() -> Dict[date, Optional[float]]:
    """Lead-1 target day -> the own-leg scarcity state as read at that lead's decision instant."""

    judge = s634._load("pressure_judge")
    return judge._scarcity_states(1, LAST_TARGET)


# -- the report ------------------------------------------------------------------------------------------------------

LABELS = {
    "B1": "B1 as-of persistence",
    "B2": "B2 calendar climatology",
    "base": "candidate (#634 variant b)",
    "plus_nyfed_pd_financing": "+ nyfed_pd_financing",
    "plus_treasury_auction_results": "+ treasury_auction_results",
    "plus_nyfed_on_rrp_counterparties": "+ nyfed_on_rrp_counterparties",
    "plus_treasury_dts_debt_cash": "+ treasury_dts_debt_cash",
}


def _pct(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:+.1f}%"


def _cell(entry: Optional[dict]) -> str:
    if not entry:
        return "n/a"
    return f"{_pct(entry['skill'])} [{_pct(entry.get('skill_lower_95_one_sided'))}, {_pct(entry.get('skill_upper_95_one_sided'))}] / {entry['mean_difference_lower_95_one_sided']:+.4f}"


def verdict_lines(score: dict) -> List[str]:
    """One line per family, then one for H3 overall, by the declared reading rule (development, not a verdict)."""

    lines, improving = [], []
    for family in score["families"]:
        entry = score["pooled_primary"].get(f"base -> {family}")
        lower = entry["mean_difference_lower_95_one_sided"]
        if lower > 0:
            improving.append(family)
        lines.append(
            f"- `{family[len('plus_'):]}`: {'improves' if lower > 0 else 'no improvement beyond its interval'} "
            f"(skill {_pct(entry['skill'])}, lower bound of mean(d) {lower:+.4f}, Holm p {entry['holm_p']:.3f})."
        )
    lines.append(
        "- **H3 overall (development, not a verdict):** "
        + (f"{', '.join(improving)} improve(s) the candidate beyond the interval." if improving else "no family improves the candidate beyond its interval: the kill reading is met on development data.")
    )
    return lines


def report_command(args) -> int:
    score = json.loads(args.score.read_text(encoding="utf-8"))
    out = ["# H3 step 3: the nested test (#708), report", "",
           f"Decision days {score['decision_days']['n']} ({score['decision_days']['first']} to {score['decision_days']['last']}); "
           f"draws {score['draws']}, seed {score['seed']}. Cells: skill [one-sided 95% bounds] / lower bound of mean daily difference.", ""]
    out += ["## Grid CRPS (bp), mean", "", "| model | mean | vs B1 | vs B2 |", "|---|---|---|---|"]
    for n in ["base"] + score["families"]:
        out.append(f"| {LABELS[n]} | {score['mean_primary'][n]:.3f} | {_cell(score['pooled_primary'].get('B1 -> ' + n))} | {_cell(score['pooled_primary'].get('B2 -> ' + n))} |")
    out += ["", "B1: %.3f; B2: %.3f." % (score["mean_primary"]["B1"], score["mean_primary"]["B2"]), ""]
    out += ["## Nested difference (candidate minus candidate + family), grid CRPS", "", "| family | primary | upper-tail twCRPS | Holm p |", "|---|---|---|---|"]
    for family in score["families"]:
        key = f"base -> {family}"
        out.append(f"| {LABELS[family]} | {_cell(score['pooled_primary'][key])} | {_cell(score['pooled_key_secondary'][key])} | {score['pooled_primary'][key]['holm_p']:.3f} |")
    out += ["", "## Reading (declared rule)", ""] + verdict_lines(score) + [""]
    for title, key in (("As-of scarcity state of the decision day", "by_scarcity_state"), ("Pressure-day type of the target day", "by_type"), ("Provisional regimes (hindsight; reported only)", "by_regime")):
        out += [f"## {title}", ""]
        for label, block in score[key].items():
            n = block.get("n", block.get("decision_days"))
            out += [f"### {label} (n = {n})", "", "| family | nested difference |", "|---|---|"]
            for family in score["families"]:
                out.append(f"| {LABELS[family]} | {_cell(block['tests'].get('base -> ' + family))} |")
            out.append("")
    out += ["## By lead (mean grid CRPS, bp)", "", "| model | " + " | ".join(f"h={h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
    for n in ["B1", "B2", "base"] + score["families"]:
        out.append(f"| {LABELS[n]} | " + " | ".join(f"{score['by_lead'][n][str(h)]:.3f}" for h in HORIZONS) + " |")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk")
    walk.add_argument("--variant", required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(func=walk_command)
    score = sub.add_parser("score")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
