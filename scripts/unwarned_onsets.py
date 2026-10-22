"""The eight onsets no scored model warns: was anything public? (#560, a diagnostic of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the directory it is given and nothing into
`docs/runs/`. It changes no model, rule, cut-off, threshold, declaration or published figure, and no day after
2025-12-31 is read (`docs/decisions/lockbox.md`). The readings it makes (the z-score reference, the bar, the
verdicts) are declared in `metadata/unwarned_onsets.json`, committed before any score was read; this script refuses
to read an uncommitted or edited declaration.

For each onset and each lead L = 1 to 5 (the forecast made L scored days before the onset day):

* every as-of input the information set can read (`INPUTS`), as a z-score against the same input, read at the same
  lead, on the scored days of the same regime that are not pressure days; the ten largest |z| listed;
* every scored row's probability and cut-off at that lead, and whether it flags (the judge's own flags);
* the scheduled events known at the decision instant: the calendar, the settlement sizes as announced, the policy
  register as of the decision instant and the entries announced in the ten days before, and the FOMC meeting
  days and the Treasury quarterly-refunding statement days within ten days (`FOMC`, `REFUNDING`, each with its URL).

The verdict per onset is the first that holds of "signal public and unused", "signal public and too weak" and "no
public signal found" (`verdict`). The sources outside the panel that plausibly carried a signal are named in the
result page, with date and URL; none is fetched into the panel.

    PYTHONPATH=src python3 scripts/unwarned_onsets.py run --panel PUBLISHED.csv --scratch-panel AUG4.csv \\
        --output-dir OUT 'OUT/bench_h{h}.json' 'OUT/risk_h{h}.json' ...        # one template per forecast file family

The z-scores are in hindsight: the reference mean and sd use the whole regime, so they describe, they do not forecast.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import subprocess
import sys
from dataclasses import replace
from datetime import date, datetime, time, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import policy_events  # noqa: E402
from repo_model.asof import TARGET, InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "as_of_at_lead": (
        "not_entry",
        "reads each scored day's as-of inputs at a lead for the descriptive diagnostic of the "
        "unwarned onsets (#560); compares nothing, and walks _as_of_folds, which refuses a locked "
        "day (tests/test_unwarned_onsets.py)",
    ),
}

DECLARATION = REPO / "metadata" / "unwarned_onsets.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
MINIMUM_HISTORY = 61
DECISION = time(16, 0)
HORIZONS = (1, 2, 3, 4, 5)

UNUSED = "signal public and unused"
WEAK = "signal public and too weak"
NONE = "no public signal found"

# The panel inputs the information set can read as of a decision instant, each z-scored. The calendar fields are
# classification, listed with the events.
INPUTS = (
    TARGET, "sofr", "iorb", "sofr_volume", "sofr_p25", "sofr_p75", "sofr_p1", "sofr_p99", "tgcr", "bgcr", "effr",
    "reserve_balances", "tga", "tga_daily", "tga_daily_change", "tga_change_x_reserves", "bank_total_assets",
    "on_rrp", "treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons",
    "treasury_settlement_soma", "dealer_treasury_position", "tbill_4w", "tbill_13w", "reserve_scarcity_state",
    "iorb_announced_change_bps", "iorb_days_to_announced_change", "ofr_tri_rate", "ofr_gcf_rate",
    "sofr_p99_iorb_bps", "sofr_p75_iorb_bps", "sofr_p99_iorb_sd15_bps",
)
CALENDAR = ("days_to_month_end", "quarter_end", "tax_date")
NET_SETTLEMENT = tuple(f"net_settlement_ahead_{k}d" for k in range(1, 6))
SETTLEMENT = ("treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons", "treasury_settlement_soma")

FED_CALENDAR = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
FED_2018 = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2018.htm"
FED_2020 = "https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm"
# FOMC meetings whose statement day (the last day of the meeting) is within the years of the onsets. The
# unscheduled actions of March 2020 are in the policy register with their own URLs.
FOMC = (
    ("2018-01-31", FED_2018), ("2018-03-21", FED_2018), ("2018-05-02", FED_2018), ("2018-06-13", FED_2018),
    ("2018-08-01", FED_2018), ("2018-09-26", FED_2018), ("2018-11-08", FED_2018), ("2018-12-19", FED_2018),
    ("2020-01-29", FED_2020), ("2020-04-29", FED_2020),
    ("2024-01-31", FED_CALENDAR), ("2024-03-20", FED_CALENDAR), ("2024-05-01", FED_CALENDAR),
    ("2024-06-12", FED_CALENDAR), ("2024-07-31", FED_CALENDAR), ("2024-09-18", FED_CALENDAR),
    ("2024-11-07", FED_CALENDAR), ("2024-12-18", FED_CALENDAR),
)

# Treasury quarterly-refunding statement days (the day the refunding announcement is made), read from the
# statements themselves on home.treasury.gov (#560 review): one per quarter that bounds an onset or a contrast onset.
# The statements of the other quarters of these years were not fetched.
TREASURY_PR = "https://home.treasury.gov/news/press-releases/"
REFUNDING = (
    ("2018-10-31", TREASURY_PR + "sm538"), ("2020-02-05", TREASURY_PR + "sm896"), ("2020-05-06", TREASURY_PR + "sm1001"),
    ("2024-07-31", TREASURY_PR + "jy2512"), ("2024-10-30", TREASURY_PR + "jy2697"),
    ("2025-07-30", TREASURY_PR + "sb0212"), ("2025-11-05", TREASURY_PR + "sb0305"),
)


def scheduled_within(table, origin: date, target: date) -> list[dict]:
    """The scheduled days of `table` ((day, url) pairs) within ten days of the origin and not after the target."""

    return [{"day": d, "url": u} for d, u in table if origin - timedelta(days=10) <= date.fromisoformat(d) <= target]


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pm = _script("episode_post_mortem")
PASSERS = pm.PASSERS


# -- pure readings --------------------------------------------------------------------------


def mean_sd(values):
    """The mean and sample sd of the known values; (None, None) for fewer than two."""

    known = [v for v in values if v is not None]
    if len(known) < 2:
        return None, None
    mean = sum(known) / len(known)
    return mean, math.sqrt(sum((v - mean) ** 2 for v in known) / (len(known) - 1))


def zscore(value, mean, sd):
    """(value - mean) / sd; None for a missing value or reference, or an sd of 0."""

    if value is None or mean is None or sd is None or sd == 0.0:
        return None
    return (value - mean) / sd


def reference_values(values, regime, pressure, label):
    """The input's known values on the days of regime `label` that are not pressure days."""

    return [v for v, r, p in zip(values, regime, pressure) if r == label and not p and v is not None]


def largest_moves(zs, k):
    """The `k` inputs of largest |z| as (name, z), ties by name; inputs without a z-score are left out."""

    known = [(n, z) for n, z in zs.items() if z is not None]
    return sorted(known, key=lambda item: (-abs(item[1]), item[0]))[:k]


def family(name: str) -> str:
    """Which of the directive's model families a row belongs to ("other" for a row it does not name).

    The five tier-1 passers, ngboost_laplace, the hurdle (#539), the timing change (#541), the structural model
    (#542), the stress factor (#543), the 2008-2018 pre-training (#544) and projected reserves (#545); the two
    references are "reference".
    """

    if name in PASSERS:
        return "passer"
    if name == "ngboost_laplace":
        return "ngboost_laplace"
    if name in ("calendar_climatology", "persistence_logistic"):
        return "reference"
    if "+every_day" in name:
        return "other"
    if "+hurdle_" in name:
        return "hurdle"
    if name == "structural_liquidity" or name.endswith("+structural"):
        return "structural"
    if name.startswith("latent_factor") or "+latent_factor" in name:
        return "stress_factor"
    if name.startswith("effr_") or "+effr_" in name:
        return "pretraining"
    if name == "projected_reserves" or name.endswith("+projected"):
        return "projected_reserves"
    if name.split("+", 1)[0] in PASSERS and name.split("+", 1)[1] in ("settle", "h41", "settle+h41"):
        return "timing"
    return "other"


MODEL_FAMILIES = ("passer", "ngboost_laplace", "hurdle", "timing", "structural", "stress_factor", "pretraining", "projected_reserves")


def share_below(value, others):
    """The share of `others` strictly below `value` (None for no others)."""

    return None if not others else sum(1 for v in others if v < value) / len(others)


def unflaggable(cells, top=5):
    """Cells of (row, lead) whose cut-off is infinite, so no probability can flag; the highest `top` by probability.

    `cells` maps a row to {lead: (probability, cutoff)}. Returns (count of cells, total, top cells).
    """

    total = sum(len(v) for v in cells.values())
    inf = [(p, name, lead) for name, by_lead in cells.items() for lead, (p, c) in by_lead.items() if not math.isfinite(c)]
    inf.sort(key=lambda item: (-item[0], item[1], item[2]))
    return len(inf), total, [{"row": n, "lead": l, "probability": p} for p, n, l in inf[:top]]


def warned_by(flags, k):
    """The rows whose flag is set at some lead for the day at position `k`."""

    return sorted(name for name, by_lead in flags.items() if any(v[k] for v in by_lead.values()))


def verdict(zs_by_lead, rows, used, net_z, *, z_strong=3.0, under_ratio=0.5):
    """The verdict of one onset (see `metadata/unwarned_onsets.json`, `readings`).

    `zs_by_lead` maps a lead to {input: z}; `rows` maps a row to {lead: (probability, cutoff)} for rows that did
    not flag; `used` is the set of inputs some row reads; `net_z` maps a lead to the z of the announced net
    settlement of the next days.
    """

    unused, weak = [], []
    for lead, zs in sorted(zs_by_lead.items()):
        for name, z in largest_moves(zs, len(zs)):
            if abs(z) >= z_strong:
                (weak if name in used else unused).append((name, lead, z))
    for lead, z in sorted(net_z.items()):
        if z is not None and abs(z) >= z_strong:
            unused.append(("net_settlement_ahead", lead, z))
    near = sorted(
        name for name, by_lead in rows.items()
        if any(math.isfinite(c) and c > 0.0 and p / c >= under_ratio for p, c in by_lead.values())
    )
    if unused:
        return {"verdict": UNUSED, "named": unused, "rows_near_cutoff": near}
    if near or weak:
        return {"verdict": WEAK, "named": weak, "rows_near_cutoff": near}
    return {"verdict": NONE, "named": [], "rows_near_cutoff": near}


# -- the reads -------------------------------------------------------------------------------


def check_days(days) -> None:
    """Refuse a scored day the lockbox holds, or one after 2025-12-31 (the post-mortem's guard)."""

    pm.require_scored_days(days)


def as_of_at_lead(rows, registry, scored_dates, inputs, lead):
    """Each input as of the decision instant `lead` rows before each scored day, by input then day.

    One `InformationRule` read per scored day at horizon `lead`, through `baseline._as_of_folds`, which checks
    the lockbox on the whole grid first and every read for leakage and staleness. The value is the cell of the
    row the read came from (`FieldRead.row`), not the scored day's own row.
    """

    rule = InformationRule(registry, tuple(inputs) + CALENDAR, decision_time=DECISION, horizon=lead)
    wanted = set(scored_dates)
    out = {name: {} for name in inputs}
    for fold in _as_of_folds(
        rows, rule, minimum_history=MINIMUM_HISTORY, refit_every=len(rows),
        entry="unwarned_onsets.as_of_at_lead", end=pm.LAST_DAY,
    ):
        day = rows[fold.index].date
        if day not in wanted:
            continue
        reads = {read.feature: read for read in fold.info.reads}
        for name in inputs:
            source = rows[reads[name].row]
            out[name][day] = source.spread_bps if name == TARGET else source.values.get(name)
    return out


def as_of_available(rows, registry, scored_dates, inputs, lead):
    """`as_of_at_lead` for the inputs the information set lets a forecast `lead` rows ahead read.

    An input the as-of rule refuses at this lead (its value for the target day is first observable after the
    decision instant, as the settlements known on the day itself at leads 2 to 5) is not public then: the guard
    names it, it is left out and listed, and the read is repeated. Returns (series, unavailable inputs).
    """

    remaining, unavailable = list(inputs), []
    while True:
        try:
            return as_of_at_lead(rows, registry, scored_dates, remaining, lead), unavailable
        except LookAheadError as error:
            match = re.search(r"'(\w+)' for the forecast", str(error))
            if match is None or match.group(1) not in remaining:
                raise
            remaining.remove(match.group(1))
            unavailable.append(match.group(1))


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", relative],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def row_features(name: str):
    """The features a row reads, from its candidate file (a combined row `a+b` falls back to `a`'s file)."""

    for candidate in (name, name.split("+")[0]):
        path = CANDIDATES / f"{candidate}.json"
        if path.exists():
            return list(json.loads(path.read_text()).get("features", []))
    return []


# -- building --------------------------------------------------------------------------------


def _load_forecasts(templates, digest):
    forecasts, seen = [], set()
    for template in templates:
        for h in HORIZONS:
            document = json.loads(Path(template.format(h=h)).read_text())
            if "bench" in Path(template).name and document["panel_sha256"] != digest:
                raise SystemExit(f"{template.format(h=h)} was scored on another panel")
            for f in pj.forecasts_from_horizon_document(document):
                if (f.name, f.horizon) not in seen:
                    seen.add((f.name, f.horizon))
                    forecasts.append(f)
    return forecasts


def build(panel: Path, scratch: Path, templates) -> dict:
    document = committed_declaration()
    jr = _script("judge_readings")
    judge_script = _script("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    base = pj.load_declaration()
    if not pj.load_weighted_miss().in_force:
        raise SystemExit("the weighted miss rule is not in force; this reads the rule in force")
    declaration = replace(base, weighted_miss=pj.load_weighted_miss(applied=True))
    readings = document["readings"]

    rows = load_daily_panel(panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(panel)
    forecasts = _load_forecasts(templates, digest)
    names = sorted({f.name for f in forecasts})
    for need in (base.climatology, base.persistence, *pm.PASSERS):
        if need not in names:
            raise SystemExit(f"no forecasts for {need}")
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in HORIZONS}

    def grids_of(items):
        out = {}
        for h in HORIZONS:
            reference = next(f for f in items if f.horizon == h and f.name == base.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    place = {day: k for k, day in enumerate(calendar)}
    grids = grids_of(forecasts)
    chosen = pj.choose_cutoffs(declaration, grids, forecasts, calendar)
    grids = grids_of(chosen)
    by_name = {}
    for f in chosen:
        by_name.setdefault(f.name, {})[f.horizon] = f
    tau = declaration.primary
    # A row with no candidate file is not a judged row (the judge refuses to flag it): left out and listed.
    left_out = sorted(n for n in names if n not in declaration.candidates)
    series = {
        n: jr.RowSeries(declaration, grids, by_name, n, place, pj.false_alarm_weights)
        for n in names if n in by_name and n in declaration.candidates
    }
    first = series[pm.PASSERS[0]]
    days = list(first.days)
    check_days(days)
    index = {d: i for i, d in enumerate(days)}
    g1 = grids[1]
    position = {h: {d: k for k, d in enumerate(grids[h].dates)} for h in HORIZONS}
    regime = [g1.groups["regime"][position[1][d]] for d in days]
    day_type = [g1.groups["day_type"][position[1][d]] for d in days]
    pressure = list(first.pressure)

    flags = {n: {h: s.flags[h] for h in HORIZONS} for n, s in series.items()}
    onset_positions = [k for k, v in enumerate(first.onset) if v]
    model_flags = {n: f for n, f in flags.items() if family(n) in MODEL_FAMILIES}
    unwarned_now = [days[k].isoformat() for k in onset_positions if not warned_by(model_flags, k)]
    unwarned_all_rows = [days[k].isoformat() for k in onset_positions if not warned_by(flags, k)]
    declared = document["onsets"]["unwarned"]

    scratch_rows = load_daily_panel(scratch)
    registry = measurement_fields.load_registry()
    risk = _script("risk_date_severity")
    risk.committed_declaration(risk.DECLARATION)
    read, unavailable = {}, {}
    with risk.switched_on():
        for lead in HORIZONS:
            read[lead], unavailable[lead] = as_of_available(scratch_rows, registry, days, INPUTS, lead)
    vectors = {lead: {n: [read[lead].get(n, {}).get(d) for d in days] for n in INPUTS} for lead in HORIZONS}
    stats = {
        (lead, n, label): mean_sd(reference_values(vectors[lead][n], regime, pressure, label))
        for lead in HORIZONS for n in INPUTS for label in sorted(set(regime))
    }
    def base_rates():
        """Per regime and lead: the share of ordinary days on which the verdict's bars are crossed (descriptive)."""

        out = {}
        for label in sorted(set(regime)):
            for lead in HORIZONS:
                ordinary = [i for i in range(len(days)) if regime[i] == label and not pressure[i]]
                any_over = unused_over = 0
                for i in ordinary:
                    zs = {n: zscore(vectors[lead][n][i], *stats[(lead, n, label)]) for n in INPUTS}
                    over = [n for n, z in zs.items() if z is not None and abs(z) >= readings["z_strong"]]
                    any_over += bool(over)
                    unused_over += any(n not in used for n in over)
                out[f"{label}/lead {lead}"] = {
                    "ordinary_days": len(ordinary),
                    "share_with_any_input_over_the_bar": any_over / len(ordinary) if ordinary else None,
                    "share_with_an_unused_input_over_the_bar": unused_over / len(ordinary) if ordinary else None,
                }
        return out

    def no_cutoff_share():
        out = {}
        for label in sorted(set(regime)):
            members = [d for d, r in zip(days, regime) if r == label]
            cells = inf = 0
            for name in series:
                if family(name) not in MODEL_FAMILIES:
                    continue
                for h in HORIZONS:
                    for d in members:
                        cells += 1
                        inf += not math.isfinite(probability(name, h, d)[1])
            out[label] = {"cells": cells, "share_with_no_cutoff": inf / cells if cells else None}
        return out

    scratch_by_day = {r.date: r for r in scratch_rows}
    scratch_place = {r.date: i for i, r in enumerate(scratch_rows)}
    def origin_row(day, lead):
        return scratch_by_day[calendar[place[day] - lead]]

    # The announced net settlement of the `lead` days after the origin, as the origin row carries it
    # (scripts/net_settlement.py panel refuses a column that differs from the panel cut at its own row).
    net_vectors = {
        k: [origin_row(d, k).values.get(f"net_settlement_ahead_{k}d") for d in days] for k in range(1, 6)
    }
    net_stats = {
        (k, label): mean_sd(reference_values(net_vectors[k], regime, pressure, label))
        for k in range(1, 6) for label in sorted(set(regime))
    }
    used = set()
    for n in names:
        used.update(row_features(n))
    register = policy_events.load_register()

    def probability(name, h, day):
        f = by_name[name][h]
        k = position[h][day]
        return f.probabilities[tau][k], f.cutoffs[tau][k]

    def events(origin: date, target: date, lead: int) -> dict:
        row = scratch_by_day[origin]
        target_row = scratch_by_day[target]
        state = policy_events.policy_state(register, datetime.combine(origin, DECISION))
        recent = [
            e for e in policy_events.known_entries(register, datetime.combine(origin, DECISION))
            if e.announced_at.date() >= origin - timedelta(days=10)
        ]
        return {
            "origin_day": origin.isoformat(),
            "calendar": {
                "target": {k: target_row.values.get(k) for k in CALENDAR},
                "origin": {k: row.values.get(k) for k in CALENDAR},
            },
            "settlement_for_the_target_day_as_public_at_origin": {
                k: read[lead].get(k, {}).get(target) for k in SETTLEMENT[:4]
            },
            "net_settlement_ahead_at_origin": {k: row.values.get(k) for k in ("net_settlement_due_5d",) + NET_SETTLEMENT},
            "policy_register": {
                "in_force": [{"kind": e.kind, "action": e.action, "effective": e.effective.isoformat() if e.effective else None}
                             for e in state.in_force if e.kind in ("iorb_rate", "debt_ceiling", "balance_sheet", "slr", "standing_repo", "reserve_management")
                             and e is state.latest(e.kind)],
                "pending": [{"id": e.id, "title": e.title, "effective": e.effective.isoformat() if e.effective else None}
                            for e in state.pending],
                "announced_in_the_10_days_before": [
                    {"id": e.id, "announced": e.announced_at.isoformat(), "title": e.title, "url": e.source_url}
                    for e in recent
                ],
            },
            "fomc_within_10_days": [
                {"statement_day": x["day"], "url": x["url"]} for x in scheduled_within(FOMC, origin, target)
            ],
            "refunding_within_10_days": [
                {"statement_day": x["day"], "url": x["url"]} for x in scheduled_within(REFUNDING, origin, target)
            ],
        }

    def onset_record(k: int) -> dict:
        day = days[k]
        label = regime[k]
        record = {
            "start": day.isoformat(), "regime": label, "day_type": day_type[k],
            "warned_by": warned_by(model_flags, k), "warned_by_other_rows": sorted(set(warned_by(flags, k)) - set(warned_by(model_flags, k))),
            "leads": {}, "rows": {},
        }
        zs_by_lead, net_z, near_rows = {}, {}, {}
        for lead in HORIZONS:
            zs = {n: zscore(vectors[lead][n][k], *stats[(lead, n, label)]) for n in INPUTS}
            zs_by_lead[lead] = {n: z for n, z in zs.items() if z is not None}
            origin = calendar[place[day] - lead]
            net_z[lead] = zscore(net_vectors[lead][k], *net_stats[(lead, label)])
            record["leads"][str(lead)] = {
                "origin_day": origin.isoformat(),
                "not_public_at_this_lead": unavailable[lead],
                "inputs": {n: {"value": vectors[lead][n][k], "z": zs[n]} for n in INPUTS},
                "largest_moves": [{"input": n, "z": z, "value": vectors[lead][n][k]} for n, z in largest_moves(zs, 10)],
                "net_settlement_ahead_z": net_z[lead],
                "events": events(origin, day, lead),
            }
        listed_near, listed_cells = {}, {}
        for name in sorted(series):
            by_lead = {h: probability(name, h, day) for h in HORIZONS}
            record["rows"][name] = {"family": family(name), "leads": {
                str(h): {"probability": p, "cutoff": None if not math.isfinite(c) else c, "flag": bool(flags[name][h][k])}
                for h, (p, c) in by_lead.items()
            }}
            if name not in warned_by(flags, k):
                near_rows[name] = by_lead
                if family(name) in MODEL_FAMILIES:
                    listed_near[name] = by_lead
            if family(name) in MODEL_FAMILIES:
                listed_cells[name] = by_lead
        record["verdict"] = verdict(
            zs_by_lead, near_rows, used, net_z, z_strong=readings["z_strong"], under_ratio=readings["under_ratio"]
        )
        count, total, top = unflaggable(listed_cells)
        for cell in top:
            h = cell["lead"]
            same = [
                probability(cell["row"], h, d)[0] for i, d in enumerate(days)
                if regime[i] == label and not pressure[i]
            ]
            cell["share_of_the_regimes_ordinary_days_below"] = share_below(cell["probability"], same)
        record["cells_with_no_cutoff"] = {"count": count, "of": total, "highest_probabilities": top}
        record["verdict_listed_models_only"] = verdict(
            zs_by_lead, listed_near, used, net_z, z_strong=readings["z_strong"], under_ratio=readings["under_ratio"]
        )
        return record

    by_start = {days[k].isoformat(): k for k in onset_positions}
    missing = [d for d in declared if d not in by_start]
    if missing:
        raise SystemExit(f"declared onsets that are not onsets of the grid: {missing}")
    unwarned = [onset_record(by_start[d]) for d in declared]

    # The contrast: 2025 onsets structural_liquidity and projected_reserves both miss while risk_gbm warns.
    contrast_days = [
        days[k].isoformat() for k in onset_positions
        if days[k].year == 2025 and "risk_gbm" in warned_by(flags, k)
        and "structural_liquidity" not in warned_by(flags, k) and "projected_reserves" not in warned_by(flags, k)
    ]
    contrast = [onset_record(by_start[d]) for d in contrast_days]

    return {
        "panel_sha256": digest, "scratch_panel_sha256": panel_sha256(scratch),
        "scored_days": [days[0].isoformat(), days[-1].isoformat()],
        "rows": sorted(series), "rows_left_out_no_candidate_file": left_out, "rows_scored_flags": {n: sum(1 for k in onset_positions if n in warned_by(flags, k)) for n in series},
        "onsets_in_grid": len(onset_positions),
        "unwarned_by_every_model": unwarned_now, "unwarned_by_every_row_including_other_rows": unwarned_all_rows,
        "declared_unwarned": declared, "base_rates": base_rates(), "no_cutoff_by_regime": no_cutoff_share(),
        "declared_matches_computed": sorted(unwarned_now) == sorted(declared),
        "rows_by_family": {f: sorted(n for n in series if family(n) == f) for f in MODEL_FAMILIES + ("reference", "other")},
        "inputs": list(INPUTS), "not_public_by_lead": {str(l): u for l, u in unavailable.items()},
        "used_inputs": sorted(used), "unused_inputs": sorted(set(INPUTS) - used),
        "readings": readings, "onsets": unwarned, "contrast": contrast,
    }


# -- output ----------------------------------------------------------------------------------


def _f(v, places=2):
    return "-" if v is None else f"{v:+.{places}f}"


def markdown(result: dict) -> str:
    models = [n for f in MODEL_FAMILIES for n in result["rows_by_family"][f]]
    lines = [
        "# The eight onsets no scored model warns (#560)", "",
        f"Published panel `{result['panel_sha256'][:8]}…`; {result['onsets_in_grid']} onsets on the shared grid; "
        f"{len(models)} model rows of the directive's families scored, and {len(result['rows']) - len(models)} other rows "
        "(the references, the every-day rows and the unselected quantile form). "
        f"Onsets warned by no model row (computed): {', '.join(result['unwarned_by_every_model']) or 'none'}; "
        f"the directive's list {'matches' if result['declared_matches_computed'] else 'DIFFERS FROM'} it "
        f"(declared: {', '.join(result['declared_unwarned'])}). "
        f"Warned by no row at all, other rows included: {', '.join(result['unwarned_by_every_row_including_other_rows']) or 'none'}.", "",
        "## Table 1. Verdict per onset", "",
        "Verdict as declared (every row's near-cut-off probabilities count) and with the directive's model families only.", "",
        "| onset | regime | type | model rows warning it | verdict | verdict, model families only | named (input, lead, z) |",
        "|---|---|---|---|---|---|---|",
    ]
    for block, tag in ((result["onsets"], ""), (result["contrast"], " (contrast)")):
        for o in block:
            v = o["verdict"]
            named = "; ".join(f"{n} (lead {l}, z {z:+.1f})" for n, l, z in v["named"][:4]) or "-"
            lines.append(
                f"| {o['start']}{tag} | {o['regime']} | {o['day_type']} | {len(o['warned_by'])} of {len(models)}"
                f"{' (' + ', '.join(o['warned_by'][:3]) + (', ...' if len(o['warned_by']) > 3 else '') + ')' if o['warned_by'] else ''} | "
                f"{v['verdict']} | {o['verdict_listed_models_only']['verdict']} | {named} |"
            )
    lines += [
        "", "## Table 2. How often the bars are crossed on ordinary days (the base rate)", "",
        "Descriptive, for reading Table 1: on the scored days of the regime that are not pressure days, the share with at least one "
        "input at |z| >= the bar (and with one no row reads), by lead.", "",
        "| regime / lead | ordinary days | any input over the bar | an unused input over the bar |", "|---|---|---|---|",
    ]
    for key, v in result["base_rates"].items():
        lines.append(
            f"| {key} | {v['ordinary_days']} | {v['share_with_any_input_over_the_bar']:.0%} | "
            f"{v['share_with_an_unused_input_over_the_bar']:.0%} |"
        )
    lines += [
        "", "## Table 2b. Cells with no cut-off in force (the cut-off is infinite: no probability can flag)", "",
        "| regime | model-row cells (row x lead x day) | share with no cut-off |", "|---|---|---|",
    ]
    for key, v in result["no_cutoff_by_regime"].items():
        lines.append(f"| {key} | {v['cells']} | {v['share_with_no_cutoff']:.0%} |")
    lines += ["", "| onset | cells with no cut-off | highest probabilities among them |", "|---|---|---|"]
    for o in result["onsets"] + result["contrast"]:
        c = o["cells_with_no_cutoff"]
        top = ", ".join(f"{t['row']} lead {t['lead']} {t['probability']:.2f} (above {t['share_of_the_regimes_ordinary_days_below']:.0%} of the regime's ordinary days)" for t in c["highest_probabilities"][:3])
        lines.append(f"| {o['start']} | {c['count']} of {c['of']} | {top or '-'} |")
    lines += ["", "## Table 3. The ten largest moves per onset and lead (z against the regime's ordinary days)", ""]
    for o in result["onsets"] + result["contrast"]:
        lines += [f"### {o['start']} ({o['regime']}, {o['day_type']})", ""]
        for lead in HORIZONS:
            block = o["leads"][str(lead)]
            moves = ", ".join(f"{m['input']} {m['z']:+.1f}" for m in block["largest_moves"])
            gone = f" [not public at this lead: {', '.join(block['not_public_at_this_lead'])}]" if block["not_public_at_this_lead"] else ""
            lines.append(f"* lead {lead} (decision {block['origin_day']}): {moves}{gone}")
        lines.append("")
    lines += ["## Table 4. Each model row's probability / cut-off at each lead (a flag is marked *)", ""]
    for o in result["onsets"] + result["contrast"]:
        lines += [f"### {o['start']}", "", "| row | family | " + " | ".join(f"lead {h}" for h in HORIZONS) + " |",
                  "|---|---|" + "---|" * len(HORIZONS)]
        for name, cells in o["rows"].items():
            if cells["family"] not in MODEL_FAMILIES + ("reference",):
                continue
            parts = []
            for h in HORIZONS:
                c = cells["leads"][str(h)]
                cut = "inf" if c["cutoff"] is None else f"{c['cutoff']:.2f}"
                parts.append(f"{c['probability']:.2f}/{cut}{'*' if c['flag'] else ''}")
            lines.append(f"| {name} | {cells['family']} | " + " | ".join(parts) + " |")
        lines.append("")
    lines += ["## Table 5. Scheduled events known at the decision (lead 1 and lead 5)", ""]
    for o in result["onsets"] + result["contrast"]:
        lines += [f"### {o['start']}", ""]
        for lead in (1, 5):
            e = o["leads"][str(lead)]["events"]
            cal = e["calendar"]
            sett = e["settlement_for_the_target_day_as_public_at_origin"]
            net = e["net_settlement_ahead_at_origin"]
            lines.append(
                f"* lead {lead} (origin {e['origin_day']}): target-day calendar {cal['target']}; origin-day calendar {cal['origin']}; "
                f"settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {sett}; "
                f"announced net settlement of the next 1 to 5 days {[net.get(k) for k in NET_SETTLEMENT]}; FOMC statement days {[f['statement_day'] for f in e['fomc_within_10_days']]}; "
                f"Treasury refunding statement days {[f['statement_day'] for f in e['refunding_within_10_days']]}; "
                f"register entries announced in the 10 days before {[x['id'] for x in e['policy_register']['announced_in_the_10_days_before']]}; "
                f"pending {[x['id'] for x in e['policy_register']['pending']]}; "
                f"in force {[(x['kind'], x['action'], x['effective']) for x in e['policy_register']['in_force']]}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def run_command(args) -> int:
    result = build(Path(args.panel), Path(args.scratch_panel), args.forecasts)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "onsets.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    (out / "onsets.md").write_text(markdown(result))
    print(json.dumps({"declared_matches_computed": result["declared_matches_computed"],
                      "unwarned_by_every_model": result["unwarned_by_every_model"],
                      "verdicts": {o["start"]: o["verdict"]["verdict"] for o in result["onsets"] + result["contrast"]}}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="build the tables")
    run.add_argument("--panel", required=True)
    run.add_argument("--scratch-panel", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("forecasts", nargs="+", help="forecast file templates with {h}")
    run.set_defaults(func=run_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
